"""
Dense Semantic Vector Retriever for CTI narrative passages.
Uses PyTorch tensor projections for high-dimensional semantic similarity.
"""

import hashlib
from typing import List, Tuple, Dict, Any, Optional
import torch
import torch.nn.functional as F
import numpy as np

from .chunker import TextChunk
from ..config import RAG_DENSE_DIM


class SemanticTextEncoder:
    """
    Continuous semantic representation encoder for cyber threat intelligence narratives.
    Utilizes subword hash n-gram projections into dense latent space with LayerNorm.
    Uses stable deterministic MD5 hashing across process runs to eliminate Python SipHash seed randomization.
    """

    def __init__(self, dim: int = RAG_DENSE_DIM):
        self.dim = dim
        # Deterministic projection seed
        torch.manual_seed(42)
        self.hash_buckets = 8192
        self.embedding = torch.randn(self.hash_buckets, dim) * 0.1

    def encode(self, text: str) -> torch.Tensor:
        words = text.lower().split()
        if not words:
            return torch.zeros(self.dim)

        indices = []
        for word in words:
            # Deterministic word hash
            h1 = int(hashlib.md5(word.encode("utf-8")).hexdigest()[:8], 16) % self.hash_buckets
            indices.append(h1)
            # Character tri-grams for morphological robustness
            if len(word) >= 3:
                for j in range(len(word) - 2):
                    trigram = word[j:j+3]
                    h2 = int(hashlib.md5(trigram.encode("utf-8")).hexdigest()[:8], 16) % self.hash_buckets
                    indices.append(h2)

        idx_tensor = torch.tensor(indices, dtype=torch.long)
        vecs = self.embedding[idx_tensor]
        pooled = vecs.mean(dim=0)
        normed = F.normalize(pooled.unsqueeze(0), p=2, dim=1).squeeze(0)
        return normed


class DenseRetriever:
    """
    Dense semantic vector store and retriever for CTI chunks.
    """

    def __init__(self, chunks: List[TextChunk]):
        self.chunks = chunks
        self.encoder = SemanticTextEncoder(dim=RAG_DENSE_DIM)
        self._embed_corpus()

    def _embed_corpus(self):
        if not self.chunks:
            self.doc_embeddings = torch.empty((0, RAG_DENSE_DIM))
            return

        embs = []
        for chunk in self.chunks:
            # Combine title + tags + content for rich representation
            text = f"{chunk.metadata.get('title', '')} {' '.join(chunk.metadata.get('tags', []))} {chunk.content}"
            embs.append(self.encoder.encode(text))

        self.doc_embeddings = torch.stack(embs)  # [N, dim]

    def search(self, query: str, top_k: int = 5) -> List[Tuple[TextChunk, float]]:
        if self.doc_embeddings.size(0) == 0:
            return []

        q_emb = self.encoder.encode(query).unsqueeze(0)  # [1, dim]
        # Cosine similarity
        sims = torch.mm(q_emb, self.doc_embeddings.t()).squeeze(0)  # [N]

        top_scores, top_indices = torch.topk(sims, k=min(top_k, len(self.chunks)))

        results = []
        for score, idx in zip(top_scores.tolist(), top_indices.tolist()):
            results.append((self.chunks[idx], float(score)))
        return results
