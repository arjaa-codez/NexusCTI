"""ThreatRGCN Model Module for Cyber-Threat Attribution Engine.
Implements Relational Graph Convolutional Network (RGCN) message passing with basis decomposition
and contrastive link prediction loss as mathematically defined in Section 2.A & 2.B:

Formula 2.A:
h_v^{(l+1)} = \sigma( W_0^{(l)} h_v^{(l)} + \sum_{r \in R} \sum_{u \in N_r(v)} (1 / c_{v,r}) W_r^{(l)} h_u^{(l)} )
where W_r^{(l)} = \sum_{b=1}^B a_{r,b} V_b^{(l)}

Formula 2.B (Contrastive Link Prediction Loss):
L_{GNN} = - \sum_{(u,v) \in E_{pos}} \log \sigma(z_u^T z_v) - \sum_{(u, v') \in E_{neg}} \log(1 - \sigma(z_u^T z_{v'}))
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import networkx as nx
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import HeteroData


class RGCNBasisLayer(nn.Module):
    """RGCN Layer with Basis-Decomposition and Normalization Constant c_{v,r}."""

    def __init__(self, in_features: int, out_features: int, num_relations: int, num_bases: int = 4):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.num_relations = num_relations
        self.num_bases = min(num_bases, num_relations)

        # Basis matrices V_b^{(l)} \in R^{in x out}
        self.basis = nn.Parameter(torch.empty(self.num_bases, in_features, out_features))
        # Coefficient coefficients a_{r, b}
        self.coeffs = nn.Parameter(torch.empty(num_relations, self.num_bases))
        # Self-loop transformation W_0^{(l)}
        self.w_self = nn.Linear(in_features, out_features, bias=True)

        self.reset_parameters()

    def reset_parameters(self):
        nn.init.xavier_uniform_(self.basis)
        nn.init.xavier_uniform_(self.coeffs)

    def forward(
        self,
        x_total: torch.Tensor,
        edge_index: torch.Tensor,
        edge_type: torch.Tensor,
        c_vr: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """Forward message passing step.
        x_total: (N, in_features)
        edge_index: (2, E) where edge_index[0]=src, edge_index[1]=dst
        edge_type: (E,) relation IDs
        c_vr: (N,) incoming normalization constant
        """
        N = x_total.size(0)
        # Compute self-loop transformation: W_0^{(l)} h_v^{(l)}
        out = self.w_self(x_total)

        if edge_index.numel() == 0:
            return out

        # Reconstruct relation matrices: W_r = \sum_b a_{r,b} V_b
        # (num_relations, in_features, out_features)
        W_relations = torch.einsum("rb,bio->rio", self.coeffs, self.basis)

        src, dst = edge_index[0], edge_index[1]
        x_src = x_total[src]  # (E, in_features)

        # Gather relation matrices for each edge: (E, in_features, out_features)
        W_edges = W_relations[edge_type]
        # Transformed messages: h_u * W_r
        msg = torch.einsum("ei,eio->eo", x_src, W_edges)

        # Aggregate incoming messages per target node: \sum_{u \in N_r(v)}
        aggregated = torch.zeros(N, self.out_features, device=x_total.device)
        aggregated.index_add_(0, dst, msg)

        # Normalize by incoming count c_{v, r}
        if c_vr is not None and c_vr.numel() == N:
            c_norm = c_vr.unsqueeze(-1).clamp(min=1.0)
            aggregated = aggregated / c_norm

        out = out + aggregated
        return out


class ThreatRGCN(nn.Module):
    """Complete ThreatRGCN Model implementing:
    - Sparse node embedding lookup table
    - 2-layer RGCN forward pass with LeakyReLU
    - Contrastive link prediction loss
    - Multi-hop attribution inference
    """

    def __init__(
        self,
        total_nodes: int,
        in_dim: int = 64,
        hidden_dim: int = 64,
        out_dim: int = 64,
        num_relations: int = 5,
        num_bases: int = 4,
    ):
        super().__init__()
        self.total_nodes = total_nodes
        self.in_dim = in_dim
        self.hidden_dim = hidden_dim
        self.out_dim = out_dim
        self.num_relations = num_relations

        # Embedding lookup table for initializing sparse node features
        self.node_embeddings = nn.Embedding(total_nodes, in_dim)
        nn.init.xavier_uniform_(self.node_embeddings.weight)

        # Layer 1 & Layer 2 RGCN
        self.layer1 = RGCNBasisLayer(in_dim, hidden_dim, num_relations, num_bases)
        self.layer2 = RGCNBasisLayer(hidden_dim, out_dim, num_relations, num_bases)
        self.dropout = nn.Dropout(p=0.1)

    def forward(
        self,
        edge_index: torch.Tensor,
        edge_type: torch.Tensor,
        c_vr: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        """Returns final latent node representations Z \in R^{N x out_dim}."""
        # Initial node features from embedding table
        x = self.node_embeddings.weight
        h1 = self.layer1(x, edge_index, edge_type, c_vr)
        h1 = F.leaky_relu(h1, negative_slope=0.2)
        h1 = self.dropout(h1)

        z = self.layer2(h1, edge_index, edge_type, c_vr)
        # Normalize representations to unit sphere for stable dot product similarities
        z = F.normalize(z, p=2, dim=-1)
        return z

    def compute_contrastive_loss(
        self,
        z: torch.Tensor,
        pos_edges: torch.Tensor,
        num_neg_samples: int = 2,
    ) -> torch.Tensor:
        """Computes Equation 2.B:
        L_{GNN} = - \sum_{(u,v) \in E_{pos}} \log \sigma(z_u^T z_v)
                  - \sum_{(u, v') \in E_{neg}} \log(1 - \sigma(z_u^T z_{v'}))
        """
        if pos_edges.numel() == 0:
            return torch.tensor(0.0, requires_grad=True)

        u = pos_edges[0]
        v = pos_edges[1]

        # Positive pairs: \sigma(z_u^T z_v)
        pos_scores = (z[u] * z[v]).sum(dim=-1)
        pos_loss = -torch.log(torch.sigmoid(pos_scores) + 1e-8).mean()

        # Negative sampling: replace v with random corruptions v'
        num_pos = u.size(0)
        neg_v = torch.randint(0, self.total_nodes, (num_pos * num_neg_samples,), device=z.device)
        rep_u = u.repeat_interleave(num_neg_samples)

        neg_scores = (z[rep_u] * z[neg_v]).sum(dim=-1)
        neg_loss = -torch.log(1.0 - torch.sigmoid(neg_scores) + 1e-8).mean()

        total_loss = pos_loss + neg_loss
        return total_loss


class AttributionReasoner:
    """Combines ThreatRGCN with NetworkX topological path finding to provide
    structural multi-hop traversal and structural confidence scores.
    """

    def __init__(
        self,
        hetero_data_path: str | Path,
        metadata_path: str | Path,
        model_weights_path: Optional[str | Path] = None,
    ):
        self.hetero_data_path = Path(hetero_data_path)
        self.metadata_path = Path(metadata_path)

        with open(self.metadata_path, "r", encoding="utf-8") as f:
            self.metadata = json.load(f)

        self.node_mappings = self.metadata["node_mappings"]
        self.reverse_mappings = {
            nt: {int(k): v for k, v in m.items()}
            for nt, m in self.metadata["reverse_mappings"].items()
        }
        self.actor_metadata = self.metadata.get("actor_metadata", {})

        # Compute global continuous node offsets
        self.node_type_offsets: Dict[str, int] = {}
        curr_offset = 0
        for nt in ["ip", "domain", "malware", "cve", "attack_group", "technique"]:
            self.node_type_offsets[nt] = curr_offset
            curr_offset += len(self.node_mappings[nt])
        self.total_nodes = curr_offset

        # Build homogeneous unified graph tensors and NetworkX graph for path exploration
        self.build_unified_graph()

        # Initialize ThreatRGCN
        self.model = ThreatRGCN(
            total_nodes=self.total_nodes,
            in_dim=64,
            hidden_dim=64,
            out_dim=64,
            num_relations=len(self.metadata["edge_relations"]),
            num_bases=4,
        )

        if model_weights_path and os.path.exists(model_weights_path):
            self.model.load_state_dict(torch.load(model_weights_path, map_location="cpu"))
            self.model.eval()
        else:
            self.train_and_save_weights(epochs=120)

    def to_global_id(self, node_type: str, local_id: int) -> int:
        return self.node_type_offsets[node_type] + local_id

    def build_unified_graph(self):
        """Build unified tensors and NetworkX directed graph for path tracing."""
        self.nx_graph = nx.DiGraph()
        edge_list: List[Tuple[int, int]] = []
        edge_types: List[int] = []

        relations = self.metadata["edge_relations"]

        # Load HeteroData
        data: HeteroData = torch.load(self.hetero_data_path, map_location="cpu", weights_only=False)

        for rel_idx, rel in enumerate(relations):
            s_type, rel_name, t_type = rel[0], rel[1], rel[2]
            edge_index = data[s_type, rel_name, t_type].edge_index
            if edge_index.shape[1] > 0:
                for i in range(edge_index.shape[1]):
                    s_local = edge_index[0, i].item()
                    t_local = edge_index[1, i].item()
                    s_global = self.to_global_id(s_type, s_local)
                    t_global = self.to_global_id(t_type, t_local)

                    edge_list.append((s_global, t_global))
                    edge_types.append(rel_idx)

                    # NetworkX attributes
                    s_label = self.reverse_mappings[s_type][s_local]
                    t_label = self.reverse_mappings[t_type][t_local]
                    self.nx_graph.add_node(s_label, node_type=s_type, global_id=s_global)
                    self.nx_graph.add_node(t_label, node_type=t_type, global_id=t_global)
                    self.nx_graph.add_edge(s_label, t_label, relation=rel_name)

        if edge_list:
            src, dst = zip(*edge_list)
            self.unified_edge_index = torch.tensor([src, dst], dtype=torch.long)
            self.unified_edge_type = torch.tensor(edge_types, dtype=torch.long)
        else:
            self.unified_edge_index = torch.empty((2, 0), dtype=torch.long)
            self.unified_edge_type = torch.empty((0,), dtype=torch.long)

        # Incoming node degree normalization c_vr
        c_vr = torch.zeros(self.total_nodes, dtype=torch.float)
        if self.unified_edge_index.numel() > 0:
            for dst_n in self.unified_edge_index[1]:
                c_vr[dst_n.item()] += 1.0
        self.unified_c_vr = c_vr.clamp(min=1.0)

    def train_and_save_weights(self, epochs: int = 120, lr: float = 0.01):
        """Train ThreatRGCN using Contrastive Link Prediction Loss."""
        optimizer = torch.optim.Adam(self.model.parameters(), lr=lr, weight_decay=1e-4)
        self.model.train()

        for epoch in range(1, epochs + 1):
            optimizer.zero_grad()
            z = self.model(self.unified_edge_index, self.unified_edge_type, self.unified_c_vr)
            loss = self.model.compute_contrastive_loss(z, self.unified_edge_index, num_neg_samples=3)
            loss.backward()
            optimizer.step()

        self.model.eval()
        weights_path = self.hetero_data_path.parent / "rgcn_weights.pt"
        torch.save(self.model.state_dict(), weights_path)
        print(f"[ThreatRGCN] Trained {epochs} epochs, final contrastive loss: {loss.item():.4f}")

    def get_embeddings(self) -> torch.Tensor:
        """Returns normalized latent node representations Z."""
        self.model.eval()
        with torch.no_grad():
            return self.model(self.unified_edge_index, self.unified_edge_type, self.unified_c_vr)

    def find_multi_hop_path(self, ioc: str, target_group: str) -> Optional[List[Dict[str, str]]]:
        """Finds directed multi-hop provenance path from IOC to Attack Group."""
        try:
            if not self.nx_graph.has_node(ioc) or not self.nx_graph.has_node(target_group):
                # Try finding bidirectional path or shortest undirected path
                undir = self.nx_graph.to_undirected()
                if nx.has_path(undir, ioc, target_group):
                    node_path = nx.shortest_path(undir, ioc, target_group)
                    path_steps = []
                    for i in range(len(node_path) - 1):
                        u, v = node_path[i], node_path[i + 1]
                        rel = (
                            self.nx_graph[u][v].get("relation", "connected_to")
                            if self.nx_graph.has_edge(u, v)
                            else self.nx_graph[v][u].get("relation", "connected_to")
                        )
                        u_type = self.nx_graph.nodes[u].get("node_type", "entity")
                        v_type = self.nx_graph.nodes[v].get("node_type", "entity")
                        path_steps.append({
                            "from": u,
                            "from_type": u_type,
                            "relation": rel,
                            "to": v,
                            "to_type": v_type,
                        })
                    return path_steps
                return None

            if nx.has_path(self.nx_graph, ioc, target_group):
                node_path = nx.shortest_path(self.nx_graph, ioc, target_group)
                path_steps = []
                for i in range(len(node_path) - 1):
                    u, v = node_path[i], node_path[i + 1]
                    rel = self.nx_graph[u][v].get("relation", "relates_to")
                    u_type = self.nx_graph.nodes[u].get("node_type", "entity")
                    v_type = self.nx_graph.nodes[v].get("node_type", "entity")
                    path_steps.append({
                        "from": u,
                        "from_type": u_type,
                        "relation": rel,
                        "to": v,
                        "to_type": v_type,
                    })
                return path_steps
        except Exception:
            return None
        return None

    def attribute_ioc(self, ioc: str) -> Dict[str, Any]:
        """Perform GNN structural similarity ranking over candidate Attack Groups.
        Computes dot-product cosine similarity and softmax confidence over attack groups.
        """
        clean_ioc = ioc.strip()
        matched_type = None
        matched_local_id = None

        for nt in ["ip", "domain", "malware", "cve"]:
            if clean_ioc in self.node_mappings[nt]:
                matched_type = nt
                matched_local_id = self.node_mappings[nt][clean_ioc]
                break

        groups = list(self.node_mappings["attack_group"].keys())
        z = self.get_embeddings()

        if matched_type is None:
            # Cold-start / Unknown IOC
            return {
                "matched": False,
                "ioc": clean_ioc,
                "top_group": "Unknown",
                "confidence": 0.0,
                "group_scores": {g: 1.0 / len(groups) for g in groups},
                "traversal_path": [],
            }

        ioc_global_id = self.to_global_id(matched_type, matched_local_id)
        z_ioc = z[ioc_global_id]  # (D,)

        group_logits = []
        for g in groups:
            g_local = self.node_mappings["attack_group"][g]
            g_global = self.to_global_id("attack_group", g_local)
            z_g = z[g_global]
            # Dot-product similarity z_IOC^T z_{A_i}
            sim = torch.dot(z_ioc, z_g).item()
            group_logits.append(sim)

        # Softmax over candidate groups
        logits_tensor = torch.tensor(group_logits, dtype=torch.float)
        probs = F.softmax(logits_tensor * 4.0, dim=0).tolist()
        group_scores = {g: round(p, 4) for g, p in zip(groups, probs)}

        # Find best group
        best_idx = int(torch.argmax(logits_tensor).item())
        best_group = groups[best_idx]
        best_conf = group_scores[best_group]

        # Multi-hop traversal path
        traversal_path = self.find_multi_hop_path(clean_ioc, best_group) or []

        return {
            "matched": True,
            "ioc": clean_ioc,
            "ioc_type": matched_type,
            "top_group": best_group,
            "confidence": best_conf,
            "group_scores": group_scores,
            "traversal_path": traversal_path,
            "group_metadata": self.actor_metadata.get(best_group, {}),
        }


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    reasoner = AttributionReasoner(
        "cyber_attribution_engine/data/processed_graph/hetero_graph.pt",
        "cyber_attribution_engine/data/processed_graph/graph_metadata.json",
    )
    test_res = reasoner.attribute_ioc("185.225.17.42")
    print("[ThreatRGCN Attribution Result]:")
    print(json.dumps(test_res, indent=2))
