"""
Baseline model implementations for empirical evaluation:
1. Naive Vector-only RAG (pure dense vector text retrieval)
2. Standalone GNN Classifier (pure relational graph structural reasoning)
"""

from typing import List, Dict, Any, Tuple
from collections import defaultdict
import torch
import torch.nn.functional as F

from ..rag.dense_retriever import DenseRetriever
from ..rag.chunker import TextChunk
from ..gnn.trainer import GNNAttributionTrainer


class NaiveVectorRAGBaseline:
    """
    Baseline 1: Standard Vector-only RAG.
    Operates strictly on unstructured text embeddings without graph relational topology.
    """

    def __init__(self, dense_retriever: DenseRetriever):
        self.retriever = dense_retriever

    def predict(self, query: str) -> List[Tuple[str, float]]:
        """
        Retrieves top text chunks using dense semantic similarity and aggregates scores per actor.
        """
        results = self.retriever.search(query, top_k=5)
        if not results:
            return []

        actor_scores: Dict[str, float] = defaultdict(float)
        for chunk, score in results:
            # Positive score contribution
            norm_score = max(score, 0.0)
            actor_scores[chunk.target_actor] += norm_score

        total = sum(actor_scores.values()) or 1.0
        ranked = [(actor, round(score / total, 4)) for actor, score in actor_scores.items()]
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked


class StandaloneGNNBaseline:
    """
    Baseline 2: Standalone Relational GNN.
    Operates strictly on knowledge graph topology without textual intelligence reports.
    """

    def __init__(self, gnn_trainer: GNNAttributionTrainer):
        self.gnn = gnn_trainer

    def predict(self, ioc_val: str) -> List[Tuple[str, float]]:
        """
        Performs structural inference on the knowledge graph without text guidance.
        """
        node = self.gnn.tkg.find_node_by_indicator(ioc_val)
        if not node:
            # Unseen node with no text context
            node_id = self.gnn.tkg.add_temporary_ioc_node(ioc_val)
        else:
            node_id = node.id

        predictions = self.gnn.predict_attribution(node_id)
        ranked = [(p["actor_id"], p["structural_confidence"]) for p in predictions]
        return ranked
