"""
Sparse BM25 Keyword Retriever tailored for Cyber Threat Intelligence text.
Preserves technical indicators (CVEs, IPs, domains, hashes, and ATT&CK IDs).
"""

from typing import List, Dict, Tuple, Any
import math
import re
from collections import Counter

from .chunker import TextChunk
from ..config import RAG_BM25_K1, RAG_BM25_B


def cti_tokenize(text: str) -> List[str]:
    """
    Tokenizes text while preserving CTI-specific tokens:
    - IPs: e.g. 194.28.172.10
    - Domains: e.g. auth-microsoft365.com, avsvmcloud.com
    - CVEs: e.g. CVE-2021-44228
    - MITRE ATT&CK: e.g. T1566.001
    - Hashes: hex strings
    """
    # Defang normalize
    normalized = text.lower().replace("[.]", ".").replace("[:]", ":")
    # Tokenize on whitespace, commas, quotes, parenthesis
    raw_tokens = re.split(r"[^\w\.\-\_]+", normalized)
    tokens = [t.strip(".-_") for t in raw_tokens if len(t.strip(".-_")) > 1]
    return tokens


class BM25Retriever:
    """
    Pure Python / NumPy BM25Okapi retriever for high-precision IOC lookup.
    """

    def __init__(self, chunks: List[TextChunk], k1: float = RAG_BM25_K1, b: float = RAG_BM25_B):
        self.chunks = chunks
        self.k1 = k1
        self.b = b

        self.corpus_size = len(chunks)
        self.doc_lens = []
        self.doc_term_freqs: List[Counter] = []
        self.df: Counter = Counter()

        self._build_index()

    def _build_index(self):
        total_len = 0
        for chunk in self.chunks:
            tokens = cti_tokenize(chunk.content)
            tf = Counter(tokens)
            self.doc_term_freqs.append(tf)
            self.doc_lens.append(len(tokens))
            total_len += len(tokens)

            for term in tf.keys():
                self.df[term] += 1

        self.avg_doc_len = (total_len / self.corpus_size) if self.corpus_size > 0 else 1.0

        # Compute IDF dictionary
        self.idf: Dict[str, float] = {}
        for term, freq in self.df.items():
            self.idf[term] = math.log(1.0 + (self.corpus_size - freq + 0.5) / (freq + 0.5))

    def search(self, query: str, top_k: int = 5) -> List[Tuple[TextChunk, float]]:
        query_tokens = cti_tokenize(query)
        if not query_tokens:
            return []

        scores: List[float] = [0.0] * self.corpus_size

        for term in query_tokens:
            if term not in self.idf:
                continue
            idf_val = self.idf[term]

            for doc_idx in range(self.corpus_size):
                tf = self.doc_term_freqs[doc_idx].get(term, 0)
                if tf == 0:
                    continue
                doc_len = self.doc_lens[doc_idx]
                denom = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avg_doc_len))
                term_score = idf_val * (tf * (self.k1 + 1.0)) / denom
                scores[doc_idx] += term_score

        # Pair with chunk and sort
        scored_chunks = [(self.chunks[i], scores[i]) for i in range(self.corpus_size)]
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        return scored_chunks[:top_k]
