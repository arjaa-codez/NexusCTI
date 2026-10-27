"""
Heterogeneous Threat Graph Neural Network (HeteroThreatGNN).
Implements relational message passing, structural link prediction,
and multi-hop threat actor attribution.
"""

from typing import Dict, List, Tuple, Optional
import torch
import torch.nn as nn
import torch.nn.functional as F

from ..config import GNN_EMBEDDING_DIM, GNN_HIDDEN_DIM, GNN_DROPOUT


class RelationalMessagePassingLayer(nn.Module):
    """
    Relational Graph Convolutional message passing layer (RGCN).
    Aggregates neighborhood features per edge relation type.
    """

    def __init__(self, in_dim: int, out_dim: int, num_relations: int):
        super().__init__()
        self.in_dim = in_dim
        self.out_dim = out_dim
        self.num_relations = num_relations

        # Relation-specific weight matrices
        self.rel_weights = nn.Parameter(torch.Tensor(num_relations, in_dim, out_dim))
        # Self-connection weight matrix
        self.self_weight = nn.Linear(in_dim, out_dim, bias=True)
        # Layer normalization for training stability
        self.layer_norm = nn.LayerNorm(out_dim)

        self._reset_parameters()

    def _reset_parameters(self):
        nn.init.xavier_uniform_(self.rel_weights)
        nn.init.xavier_uniform_(self.self_weight.weight)
        if self.self_weight.bias is not None:
            nn.init.zeros_(self.self_weight.bias)

    def forward(
        self,
        x: torch.Tensor,
        rel_edge_indices: Dict[int, torch.Tensor]
    ) -> torch.Tensor:
        """
        Args:
            x: Node features [N, in_dim]
            rel_edge_indices: Dict mapping rel_idx -> [2, E_r] edge indices
        Returns:
            Updated node representations [N, out_dim]
        """
        num_nodes = x.size(0)
        # Self-loop contribution
        out = self.self_weight(x)

        # Message passing per relation
        for rel_idx, edge_index in rel_edge_indices.items():
            if edge_index.numel() == 0 or edge_index.size(1) == 0:
                continue

            src = edge_index[0]
            dst = edge_index[1]

            # Transform source node features using relation weight
            w_r = self.rel_weights[rel_idx]  # [in_dim, out_dim]
            src_feat = x[src]                # [E_r, in_dim]
            msg = torch.matmul(src_feat, w_r) # [E_r, out_dim]

            # Degree normalization for target nodes
            deg = torch.zeros(num_nodes, device=x.device).index_add_(
                0, dst, torch.ones(dst.size(0), device=x.device)
            )
            deg_inv = deg.pow(-1.0)
            deg_inv[deg_inv == float("inf")] = 0.0
            norm = deg_inv[dst].unsqueeze(-1)
            msg = msg * norm

            # Add messages to destination nodes
            out = out.index_add(0, dst, msg)

        out = self.layer_norm(out)
        return out


class HeteroThreatGNN(nn.Module):
    """
    End-to-end multi-layer Relational GNN for Cyber Threat Attribution.
    Computes structural proximity, latent neighborhood representations,
    and threat actor affinity probabilities.
    """

    def __init__(
        self,
        in_dim: int = GNN_EMBEDDING_DIM,
        hidden_dim: int = GNN_HIDDEN_DIM,
        num_relations: int = 20,
        num_actors: int = 6,
        num_layers: int = 2,
        dropout: float = GNN_DROPOUT
    ):
        super().__init__()
        self.in_dim = in_dim
        self.hidden_dim = hidden_dim
        self.num_actors = num_actors
        self.dropout = dropout

        # Input projection
        self.input_proj = nn.Linear(in_dim, hidden_dim)

        # Stacked RGCN layers
        self.rgcn_layers = nn.ModuleList([
            RelationalMessagePassingLayer(hidden_dim, hidden_dim, num_relations)
            for _ in range(num_layers)
        ])

        # DistMult Relational Link Prediction relation diagonal embeddings
        self.rel_diag = nn.Parameter(torch.Tensor(num_relations, hidden_dim))
        nn.init.normal_(self.rel_diag, mean=1.0, std=0.1)

        # Actor Classification Head (maps node embedding to actor probability logits)
        self.actor_classifier = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, num_actors)
        )

    def encode(
        self,
        x: torch.Tensor,
        rel_edge_indices: Dict[int, torch.Tensor]
    ) -> torch.Tensor:
        """
        Computes final node structural embeddings via multi-hop message passing.
        """
        h = F.relu(self.input_proj(x))
        for layer in self.rgcn_layers:
            h_new = layer(h, rel_edge_indices)
            h = F.relu(h_new)
            h = F.dropout(h, p=self.dropout, training=self.training)
        return h

    def predict_actor_affinity(
        self,
        node_embeddings: torch.Tensor,
        query_node_idx: int,
        actor_node_indices: List[int]
    ) -> torch.Tensor:
        """
        Computes structural affinity scores between a query node (IOC/Malware)
        and all candidate threat actor nodes.
        Uses cosine similarity + bilinear projection.
        """
        q_emb = node_embeddings[query_node_idx].unsqueeze(0)  # [1, hidden_dim]
        actor_embs = node_embeddings[actor_node_indices]      # [num_actors, hidden_dim]

        # Normalized cosine similarity in latent neighborhood space
        q_norm = F.normalize(q_emb, p=2, dim=1)
        a_norm = F.normalize(actor_embs, p=2, dim=1)
        scores = torch.mm(q_norm, a_norm.t()).squeeze(0)      # [num_actors]

        # Softmax over candidate actors
        probs = F.softmax(scores * 2.5, dim=0)
        return probs

    def forward(
        self,
        x: torch.Tensor,
        rel_edge_indices: Dict[int, torch.Tensor]
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass returning node embeddings and global actor classification logits.
        """
        embeddings = self.encode(x, rel_edge_indices)
        actor_logits = self.actor_classifier(embeddings)
        return embeddings, actor_logits
