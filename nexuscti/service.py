"""
NexusCTI Core Service Coordinator.
Initializes the Knowledge Graph, GNN, RAG Retriever, and Fusion Engine.
"""

from typing import Optional, Dict, Any
import logging

from .data.knowledge_base import build_default_knowledge_graph_data
from .data.corpus import get_default_threat_corpus
from .gnn.graph_builder import ThreatKnowledgeGraph
from .gnn.trainer import GNNAttributionTrainer
from .gnn.trail_extractor import GraphTrailExtractor
from .rag.hybrid_retriever import HybridRetriever
from .rag.dense_retriever import DenseRetriever
from .fusion.engine import SynergisticFusionEngine, FusionAnalysisResult
from .eval.evaluator import AttributionEvaluator
from .eval.baselines import NaiveVectorRAGBaseline, StandaloneGNNBaseline

logger = logging.getLogger("NexusCTI")


class NexusCTIService:
    """
    Unified high-level interface for all NexusCTI operations.
    """

    def __init__(self):
        logger.info("Initializing NexusCTI Service...")

        # 1. Structural Knowledge Graph
        nodes, edges = build_default_knowledge_graph_data()
        self.tkg = ThreatKnowledgeGraph(nodes, edges)

        # 2. Relational GNN Trainer & Message Passing
        self.gnn_trainer = GNNAttributionTrainer(self.tkg)
        self.gnn_trainer.train(epochs=120, verbose=False)

        # 3. Multi-Hop Graph Trail Extractor
        self.trail_extractor = GraphTrailExtractor(self.tkg)

        # 4. Contextual Hybrid RAG Retriever
        self.corpus = get_default_threat_corpus()
        self.hybrid_retriever = HybridRetriever(self.corpus)

        # 5. Synergistic Fusion Engine
        self.fusion_engine = SynergisticFusionEngine(
            gnn_trainer=self.gnn_trainer,
            trail_extractor=self.trail_extractor,
            hybrid_retriever=self.hybrid_retriever
        )

        # 6. Evaluation Baselines & Benchmark Harness
        self.vector_baseline = NaiveVectorRAGBaseline(self.hybrid_retriever.dense)
        self.gnn_baseline = StandaloneGNNBaseline(self.gnn_trainer)
        self.evaluator = AttributionEvaluator(
            fusion_engine=self.fusion_engine,
            vector_baseline=self.vector_baseline,
            gnn_baseline=self.gnn_baseline
        )

        logger.info("NexusCTI Engine successfully initialized and ready.")

    def analyze(self, query: str, ioc_override: Optional[str] = None) -> FusionAnalysisResult:
        """
        Executes end-to-end attribution on given telemetry or indicator.
        """
        return self.fusion_engine.analyze_incident(query, ioc_override=ioc_override)

    def run_benchmark(self) -> Dict[str, Any]:
        """
        Executes comparative benchmark against baselines.
        """
        return self.evaluator.run_benchmark()

    def get_graph_data(self) -> Dict[str, Any]:
        """
        Exports full graph topology for web visualizer.
        """
        nodes_data = []
        for n in self.tkg.raw_nodes:
            nodes_data.append({
                "id": n.id,
                "label": n.name,
                "type": n.type.value,
                "description": n.description,
                "degree": self.tkg.nx_graph.degree(n.id)
            })

        edges_data = []
        seen = set()
        for u, v, data in self.tkg.nx_graph.edges(data=True):
            rel = data.get("rel_type", "associated_with")
            if rel.startswith("rev_"):
                continue  # Skip inverse edges in visual representation for clarity
            edge_key = (u, v, rel)
            if edge_key not in seen:
                seen.add(edge_key)
                edges_data.append({
                    "source": u,
                    "target": v,
                    "relation": rel,
                    "citation": data.get("citation", "")
                })

        return {"nodes": nodes_data, "edges": edges_data}


# Global singleton instance
_service_instance: Optional[NexusCTIService] = None


def get_service() -> NexusCTIService:
    global _service_instance
    if _service_instance is None:
        _service_instance = NexusCTIService()
    return _service_instance
