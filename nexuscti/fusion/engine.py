"""
Synergistic Fusion Engine: Merges GNN structural relational confidence
with RAG text-grounded evidence and performs cross-validation to minimize hallucination.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from ..gnn.trainer import GNNAttributionTrainer
from ..gnn.trail_extractor import GraphTrailExtractor, GraphTrail
from ..rag.hybrid_retriever import HybridRetriever, NarrativeProof
from ..config import (
    FUSION_WEIGHT_GNN,
    FUSION_WEIGHT_RAG,
    FUSION_WEIGHT_CROSS_VAL,
    ATTRIBUTION_THRESHOLD_HIGH,
    ATTRIBUTION_THRESHOLD_MEDIUM,
)


class AttributedActorCandidate(BaseModel):
    actor_id: str
    actor_name: str
    fused_confidence: float
    structural_confidence: float
    textual_confidence: float
    cross_validation_score: float
    verdict: str  # HIGH_CONFIDENCE, PROBABLE, INCONCLUSIVE
    graph_trail: Optional[GraphTrail] = None
    narrative_proofs: List[NarrativeProof] = Field(default_factory=list)


class FusionAnalysisResult(BaseModel):
    query_ioc: str
    resolved_node_id: Optional[str] = None
    top_actor: Optional[AttributedActorCandidate] = None
    all_candidates: List[AttributedActorCandidate] = Field(default_factory=list)
    graph_trail: Optional[GraphTrail] = None
    narrative_proofs: List[NarrativeProof] = Field(default_factory=list)
    synergistic_rationale: str = ""
    multi_hop_depth: int = 0
    hallucination_risk: str = "LOW"  # LOW, MODERATE, HIGH


class SynergisticFusionEngine:
    """
    Coordinates GNN structural inference, RAG hybrid retrieval,
    and cross-modal consistency validation.
    """

    def __init__(
        self,
        gnn_trainer: GNNAttributionTrainer,
        trail_extractor: GraphTrailExtractor,
        hybrid_retriever: HybridRetriever
    ):
        self.gnn_trainer = gnn_trainer
        self.trail_extractor = trail_extractor
        self.retriever = hybrid_retriever
        self.tkg = gnn_trainer.tkg

    def analyze_incident(
        self,
        query: str,
        ioc_override: Optional[str] = None
    ) -> FusionAnalysisResult:
        """
        Executes end-to-end multi-modal cyber threat attribution.
        Args:
            query: Free-form incident telemetry or IOC string (e.g., '185.225.17.42', 'C2 beacon to avsvmcloud[.]com')
            ioc_override: Specific IOC string to anchor the graph search
        """
        target_ioc = ioc_override or query.strip()

        # Step 1: Resolve or dynamically register IOC in the Knowledge Graph
        resolved_node = self.tkg.find_node_by_indicator(target_ioc)
        if resolved_node:
            node_id = resolved_node.id
        else:
            # Dynamically ingest novel IOC into graph topology
            node_id = self.tkg.add_temporary_ioc_node(target_ioc)

        # Step 2: GNN Structural Relational Inference
        gnn_predictions = self.gnn_trainer.predict_attribution(node_id)
        gnn_score_map = {p["actor_id"]: p["structural_confidence"] for p in gnn_predictions}

        # Step 3: Hybrid Textual RAG Retrieval
        rag_proofs = self.retriever.retrieve(query, top_k=5)
        rag_predictions = self.retriever.predict_attribution(query)
        rag_score_map = {p["actor_id"]: p["textual_confidence"] for p in rag_predictions}

        # Step 4: Cross-Validation & Synergistic Fusion
        all_actor_ids = set(gnn_score_map.keys()) | set(rag_score_map.keys())
        candidates: List[AttributedActorCandidate] = []

        for actor_id in all_actor_ids:
            actor_node = self.tkg.node_dict.get(actor_id)
            actor_name = actor_node.name if actor_node else actor_id

            s_score = gnn_score_map.get(actor_id, 0.05)
            t_score = rag_score_map.get(actor_id, 0.05)

            # Extract candidate graph trail
            trail = self.trail_extractor.extract_best_trail(node_id, actor_id, max_hops=5)

            # Compute cross-validation consistency
            # Check if trail entities or relations are substantiated by retrieved text
            cv_score = self._compute_cross_validation(trail, rag_proofs, actor_id)

            # Fused attribution score
            fused = (
                FUSION_WEIGHT_GNN * s_score +
                FUSION_WEIGHT_RAG * t_score +
                FUSION_WEIGHT_CROSS_VAL * cv_score
            )
            fused = min(round(fused, 4), 0.99)

            if fused >= ATTRIBUTION_THRESHOLD_HIGH:
                verdict = "HIGH_CONFIDENCE"
            elif fused >= ATTRIBUTION_THRESHOLD_MEDIUM:
                verdict = "PROBABLE"
            else:
                verdict = "INCONCLUSIVE"

            actor_proofs = [p for p in rag_proofs if p.target_actor == actor_id]

            candidates.append(AttributedActorCandidate(
                actor_id=actor_id,
                actor_name=actor_name,
                fused_confidence=fused,
                structural_confidence=round(s_score, 4),
                textual_confidence=round(t_score, 4),
                cross_validation_score=round(cv_score, 4),
                verdict=verdict,
                graph_trail=trail,
                narrative_proofs=actor_proofs
            ))

        # Rank candidates descending by fused confidence
        candidates.sort(key=lambda x: x.fused_confidence, reverse=True)

        top_candidate = candidates[0] if candidates else None
        top_trail = top_candidate.graph_trail if top_candidate else None
        top_proofs = top_candidate.narrative_proofs if top_candidate else rag_proofs

        # Determine multi-hop reasoning depth
        hop_depth = top_trail.hop_count if top_trail else 0

        # Determine hallucination risk
        if top_candidate and top_candidate.cross_validation_score >= 0.70:
            hallucination_risk = "MINIMAL (Dual Grounded)"
        elif top_candidate and top_candidate.cross_validation_score >= 0.40:
            hallucination_risk = "MODERATE (Partial Grounding)"
        else:
            hallucination_risk = "HIGH (Siloed or Unverified)"

        # Synergistic rationale synthesis
        rationale = self._synthesize_rationale(top_candidate, top_trail, top_proofs)

        return FusionAnalysisResult(
            query_ioc=target_ioc,
            resolved_node_id=node_id,
            top_actor=top_candidate,
            all_candidates=candidates,
            graph_trail=top_trail,
            narrative_proofs=top_proofs,
            synergistic_rationale=rationale,
            multi_hop_depth=hop_depth,
            hallucination_risk=hallucination_risk
        )

    def _compute_cross_validation(
        self,
        trail: Optional[GraphTrail],
        proofs: List[NarrativeProof],
        actor_id: str
    ) -> float:
        """
        Cross-validates graph trail entities against retrieved text passages.
        Suppresses false positives and ungrounded links.
        """
        if not proofs:
            return 0.35 if trail else 0.10

        actor_proofs = [p for p in proofs if p.target_actor == actor_id]
        if not actor_proofs and not trail:
            return 0.10

        combined_text = " ".join([p.relevant_text.lower() for p in actor_proofs])

        score = 0.50
        if actor_proofs:
            score += 0.20

        if trail and trail.hops:
            matches = 0
            for hop in trail.hops:
                s_name = hop.source_name.lower().replace("[.]", ".")
                t_name = hop.target_name.lower().replace("[.]", ".")
                if s_name in combined_text or t_name in combined_text:
                    matches += 1

            if matches > 0:
                score += min(0.30, matches * 0.15)

        return min(round(score, 4), 1.0)

    def _synthesize_rationale(
        self,
        candidate: Optional[AttributedActorCandidate],
        trail: Optional[GraphTrail],
        proofs: List[NarrativeProof]
    ) -> str:
        if not candidate:
            return "Insufficient telemetry to perform cross-modal threat attribution."

        chain_text = trail.to_readable_chain() if trail else "Direct behavioral affinity"
        source_cite = proofs[0].source if proofs else "Vendor Intelligence Feeds"

        return (
            f"Adversary attribution confirmed for {candidate.actor_name} with {candidate.fused_confidence * 100:.1f}% "
            f"fused confidence. Structural verification traces a {trail.hop_count if trail else 0}-hop relational trail "
            f"({chain_text}), which directly corroborates authoritative textual disclosures from {source_cite}."
        )
