"""
Training and inference pipeline for HeteroThreatGNN.
Trains relational representations using link prediction and actor supervision.
"""

from typing import Dict, List, Tuple, Any
import torch
import torch.nn as nn
import torch.optim as optim
import networkx as nx

from .graph_builder import ThreatKnowledgeGraph
from .model import HeteroThreatGNN
from ..config import GNN_LEARNING_RATE, GNN_EPOCHS, GNN_WEIGHT_DECAY


class GNNAttributionTrainer:
    """
    Handles model training, representation learning, and inference.
    """

    def __init__(self, tkg: ThreatKnowledgeGraph):
        self.tkg = tkg
        self.num_relations = len(tkg.relation_to_idx)
        self.num_actors = len(tkg.actor_indices)

        self.model = HeteroThreatGNN(
            in_dim=tkg.x.size(1),
            hidden_dim=64,
            num_relations=self.num_relations,
            num_actors=self.num_actors,
            num_layers=2
        )

        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=GNN_LEARNING_RATE,
            weight_decay=GNN_WEIGHT_DECAY
        )

        self.cached_embeddings: torch.Tensor = None
        self._is_trained = False

    def _prepare_training_labels(self) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Derives training labels by finding which actor each entity is reachable from
        via multi-hop paths in the knowledge graph.
        """
        labeled_indices = []
        labels = []

        for a_local_idx, a_node_idx in enumerate(self.tkg.actor_indices):
            a_node_id = self.tkg.idx_to_node_id[a_node_idx]

            # Find all nodes reachable from this actor in directed / undirected graph within 3 hops
            lengths = nx.single_source_shortest_path_length(self.tkg.nx_graph, a_node_id, cutoff=3)
            for target_id, dist in lengths.items():
                if dist > 0:  # Exclude self
                    target_idx = self.tkg.node_id_to_idx[target_id]
                    labeled_indices.append(target_idx)
                    labels.append(a_local_idx)

        idx_tensor = torch.tensor(labeled_indices, dtype=torch.long)
        labels_tensor = torch.tensor(labels, dtype=torch.long)
        return idx_tensor, labels_tensor

    def train(self, epochs: int = GNN_EPOCHS, verbose: bool = False) -> Dict[str, float]:
        """
        Executes relational representation learning.
        """
        self.model.train()
        train_indices, train_labels = self._prepare_training_labels()
        criterion = nn.CrossEntropyLoss()

        best_loss = float("inf")

        for epoch in range(epochs):
            self.optimizer.zero_grad()
            embeddings, actor_logits = self.model(self.tkg.x, self.tkg.rel_edge_indices)

            # Supervision loss on reachable entities
            target_logits = actor_logits[train_indices]
            loss = criterion(target_logits, train_labels)

            loss.backward()
            self.optimizer.step()

            if loss.item() < best_loss:
                best_loss = loss.item()

            if verbose and (epoch + 1) % 20 == 0:
                print(f"Epoch [{epoch+1}/{epochs}] - GNN Relational Loss: {loss.item():.4f}")

        self.model.eval()
        with torch.no_grad():
            self.cached_embeddings, _ = self.model(self.tkg.x, self.tkg.rel_edge_indices)
        self._is_trained = True

        return {"final_loss": float(best_loss), "epochs": epochs}

    def predict_attribution(self, query_node_id: str) -> List[Dict[str, Any]]:
        """
        Performs structural relational inference for a query IOC / entity.
        Returns ranked list of candidate Threat Actors with structural confidence scores.
        """
        if not self._is_trained:
            self.train(epochs=GNN_EPOCHS, verbose=False)

        if query_node_id not in self.tkg.node_id_to_idx:
            # Query node not found
            return []

        query_idx = self.tkg.node_id_to_idx[query_node_id]

        if self.cached_embeddings is not None and query_idx < self.cached_embeddings.size(0):
            with torch.no_grad():
                probs = self.model.predict_actor_affinity(
                    self.cached_embeddings,
                    query_idx,
                    self.tkg.actor_indices
                )
        else:
            # Query node not present during last embedding computation (e.g. temporary novel node)
            num_actors = len(self.tkg.actor_indices)
            probs = torch.ones(num_actors) / max(num_actors, 1)

        query_id = self.tkg.idx_to_node_id[query_idx]
        raw_scores = []
        for local_idx, actor_node_idx in enumerate(self.tkg.actor_indices):
            actor_id = self.tkg.idx_to_node_id[actor_node_idx]
            actor_name = self.tkg.actor_idx_to_name[actor_node_idx]
            emb_conf = float(probs[local_idx].item())

            # Compute topological reachability
            try:
                path_len = nx.shortest_path_length(self.tkg.nx_graph, query_id, actor_id)
                topo_score = 1.0 / (1.0 + 0.35 * path_len)
            except Exception:
                try:
                    path_len = nx.shortest_path_length(self.tkg.nx_graph, actor_id, query_id)
                    topo_score = 1.0 / (1.0 + 0.35 * path_len)
                except Exception:
                    topo_score = 0.05

            combined_score = 0.45 * emb_conf + 0.55 * topo_score
            raw_scores.append((actor_id, actor_name, combined_score, actor_node_idx))

        # Softmax normalize over candidate actors
        score_sum = sum(s[2] for s in raw_scores) or 1.0
        results = []
        for actor_id, actor_name, score, actor_node_idx in raw_scores:
            norm_conf = round(score / score_sum, 4)
            results.append({
                "actor_id": actor_id,
                "actor_name": actor_name,
                "structural_confidence": norm_conf,
                "actor_node_idx": actor_node_idx
            })

        # Sort descending by structural confidence
        results.sort(key=lambda x: x["structural_confidence"], reverse=True)
        return results
