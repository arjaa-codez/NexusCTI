"""
Hybrid Dense-Sparse CTI Retrieval Engine with Reciprocal Rank Fusion (RRF).
Extracts qualitative evidence and text-grounded actor attribution signals.
"""

from typing import List, Dict, Tuple, Any, Optional
from collections import defaultdict
from pydantic import BaseModel, Field

from .chunker import TextChunk, CTIChunker
from .bm25_retriever import BM25Retriever
from .dense_retriever import DenseRetriever
from ..data.corpus import ThreatReport, get_default_threat_corpus
from ..config import RAG_TOP_K, RAG_RRF_K


class NarrativeProof(BaseModel):
    chunk_id: str
    doc_id: str
    source: str
    date: str
    target_actor: str
    relevant_text: str
    matched_iocs: List[str] = Field(default_factory=list)
    retrieval_score: float = 0.0
    direct_quote: str = ""


class HybridRetriever:
    """
    Combines BM25 exact indicator lookup and Dense semantic context
    via Reciprocal Rank Fusion (RRF).
    """

    def __init__(self, corpus: Optional[List[ThreatReport]] = None):
        if corpus is None:
            corpus = get_default_threat_corpus()
        self.corpus = corpus

        # Chunk corpus
        chunker = CTIChunker(chunk_size=450, overlap=80)
        self.chunks: List[TextChunk] = chunker.chunk_corpus(corpus)

        # Initialize sub-retrievers
        self.bm25 = BM25Retriever(self.chunks)
        self.dense = DenseRetriever(self.chunks)

    def retrieve(
        self,
        query: str,
        top_k: int = RAG_TOP_K,
        rrf_k: int = RAG_RRF_K
    ) -> List[NarrativeProof]:
        """
        Executes hybrid dense-sparse search and merges using Reciprocal Rank Fusion.
        """
        sparse_results = self.bm25.search(query, top_k=top_k * 2)
        dense_results = self.dense.search(query, top_k=top_k * 2)

        # Map chunk_id to RRF score
        rrf_scores: Dict[str, float] = defaultdict(float)
        chunk_map: Dict[str, TextChunk] = {}

        # Sparse contribution
        for rank, (chunk, _) in enumerate(sparse_results):
            chunk_map[chunk.chunk_id] = chunk
            rrf_scores[chunk.chunk_id] += 0.6 / (rrf_k + rank + 1)

        # Dense contribution
        for rank, (chunk, _) in enumerate(dense_results):
            chunk_map[chunk.chunk_id] = chunk
            rrf_scores[chunk.chunk_id] += 0.4 / (rrf_k + rank + 1)

        # Sort by final fused RRF score
        ranked_items = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        proofs: List[NarrativeProof] = []
        for chunk_id, score in ranked_items[:top_k]:
            chunk = chunk_map[chunk_id]

            # Find matching indicators
            query_lower = query.lower()
            matched = [
                ioc for ioc in chunk.iocs_mentioned
                if ioc.lower() in query_lower or ioc.lower().replace("[.]", ".") in query_lower
            ]

            # Extract most prominent direct quote sentence
            sentences = [s.strip() for s in chunk.content.split(".") if len(s.strip()) > 15]
            quote = sentences[0] + "." if sentences else chunk.content[:200]

            proofs.append(NarrativeProof(
                chunk_id=chunk.chunk_id,
                doc_id=chunk.doc_id,
                source=chunk.source,
                date=chunk.date,
                target_actor=chunk.target_actor,
                relevant_text=chunk.content,
                matched_iocs=matched,
                retrieval_score=round(score * 100.0, 4),  # Scale for display
                direct_quote=quote
            ))

        return proofs

    def predict_attribution(self, query: str) -> List[Dict[str, Any]]:
        """
        Aggregates retrieved narrative context into actor attribution probabilities.
        """
        proofs = self.retrieve(query, top_k=6)
        if not proofs:
            return []

        actor_scores: Dict[str, float] = defaultdict(float)
        total_score = 0.0

        for proof in proofs:
            # Score weight decays with rank
            weight = proof.retrieval_score
            # Boost if exact IOC was matched in this passage
            if proof.matched_iocs:
                weight *= 1.5
            actor_scores[proof.target_actor] += weight
            total_score += weight

        results = []
        if total_score > 0:
            for actor_id, score in actor_scores.items():
                prob = score / total_score
                results.append({
                    "actor_id": actor_id,
                    "textual_confidence": round(prob, 4),
                    "evidence_chunks": [p.chunk_id for p in proofs if p.target_actor == actor_id]
                })

        results.sort(key=lambda x: x["textual_confidence"], reverse=True)
        return results
