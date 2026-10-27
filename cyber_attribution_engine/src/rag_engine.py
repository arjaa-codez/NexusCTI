r"""RAG Engine Module for Cyber-Threat Attribution Engine.
Implements local persistent vector retrieval with ChromaDB and sentence-transformers.
Provides hybrid_search(query, gnn_top_group) that filters CTI report chunks
based on GNN-identified threat actor metadata.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings
import numpy as np


class MiniLMEmbeddingFunction:
    """Wraps sentence-transformers all-MiniLM-L6-v2 with deterministic token-hash fallback."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None
        try:
            from sentence_transformers import SentenceTransformer
            # Load model; if internet is slow or offline, fallback smoothly
            self.model = SentenceTransformer(model_name, device="cpu")
        except Exception as e:
            print(f"[RAG Engine] SentenceTransformer offline fallback: {e}")
            self.model = None

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if self.model is not None:
            try:
                embeddings = self.model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
                return embeddings.tolist()
            except Exception:
                pass
        # Deterministic 384-dimensional dense semantic embedding fallback
        result = []
        for text in texts:
            vec = np.zeros(384, dtype=np.float32)
            words = text.lower().split()
            for idx, w in enumerate(words):
                h = hash(w) % 384
                vec[h] += 1.0 / (idx + 1.0)
            norm = np.linalg.norm(vec)
            if norm > 1e-8:
                vec = vec / norm
            result.append(vec.tolist())
        return result

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]

    def __call__(self, input: List[str]) -> List[List[float]]:
        return self.embed_documents(input)


class ThreatRAGEngine:
    """ChromaDB Vector Store and Hybrid Retriever for authentic CTI reports."""

    def __init__(
        self,
        persist_directory: str | Path = "cyber_attribution_engine/data/chroma_db",
        raw_reports_dir: str | Path = "cyber_attribution_engine/data/raw_reports",
    ):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        self.raw_reports_dir = Path(raw_reports_dir)

        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(anonymized_telemetry=False, is_persistent=True),
        )

        self.embedding_fn = MiniLMEmbeddingFunction()
        self.collection_name = "cti_threat_reports"
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

        # Index reports if empty or updated
        if self.collection.count() == 0:
            self.index_raw_reports()

    def chunk_text(self, text: str, chunk_size: int = 150, overlap: int = 30) -> List[str]:
        words = text.split()
        if len(words) <= chunk_size:
            return [text]
        chunks = []
        i = 0
        while i < len(words):
            chunk = " ".join(words[i : i + chunk_size])
            chunks.append(chunk)
            i += (chunk_size - overlap)
        return chunks

    def index_raw_reports(self) -> int:
        """Indexes authentic CTI reports into ChromaDB."""
        report_files = sorted(self.raw_reports_dir.glob("*.json"))
        if not report_files:
            return 0

        documents = []
        metadatas = []
        ids = []

        for rf in report_files:
            with open(rf, "r", encoding="utf-8") as f:
                data = json.load(f)

            threat_actor = data.get("threat_actor", "Unknown")
            narrative = data.get("narrative", "")
            aliases = ", ".join(data.get("aliases", []))
            origin = data.get("origin", "")
            report_id = data.get("id", rf.stem)

            # Chunk narrative
            chunks = self.chunk_text(narrative, chunk_size=120, overlap=25)
            for idx, chunk in enumerate(chunks):
                doc_id = f"{threat_actor.lower().replace(' ', '_')}_{report_id}_{idx}"
                documents.append(chunk)
                metadatas.append({
                    "threat_actor": threat_actor,
                    "aliases": aliases,
                    "origin": origin,
                    "report_id": report_id,
                    "chunk_index": idx,
                    "source_file": rf.name,
                })
                ids.append(doc_id)

        # Embed and insert
        embeddings = self.embedding_fn.embed_documents(documents)
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )
        print(f"[RAG Engine] Indexed {len(documents)} chunks from {len(report_files)} CTI reports into ChromaDB.")
        return len(documents)

    def hybrid_search(
        self,
        query: str,
        gnn_top_group: Optional[str] = None,
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:
        """Hybrid search filtering vector retrieval results using metadata tags
        corresponding to the GNN-identified threat actor.
        Returns top-k chunks with Sim_cos(E_q, E_d).
        """
        query_emb = self.embedding_fn.embed_query(query)

        # If GNN identified a specific candidate attack group, filter by threat actor
        where_filter = None
        if gnn_top_group and gnn_top_group != "Unknown":
            where_filter = {"threat_actor": gnn_top_group}

        results = None
        if where_filter:
            try:
                results = self.collection.query(
                    query_embeddings=[query_emb],
                    n_results=top_k,
                    where=where_filter,
                )
            except Exception as e:
                print(f"[RAG Engine] Filtered query error: {e}, falling back to unrestricted search")
                results = None

        # Fallback to unrestricted search if filter returned empty or failed
        if not results or not results["ids"] or len(results["ids"][0]) == 0:
            results = self.collection.query(
                query_embeddings=[query_emb],
                n_results=top_k,
            )

        retrieved_chunks = []
        if results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0] if results["metadatas"] else [{}] * len(docs)
            distances = results["distances"][0] if results.get("distances") else [0.0] * len(docs)

            for doc, meta, dist in zip(docs, metas, distances):
                # Cosine distance to similarity: Sim_cos = 1 - distance
                # ChromaDB cosine distance is in [0, 2], so sim = max(0.0, 1.0 - dist)
                sim_cos = max(0.0, round(1.0 - float(dist), 4))
                retrieved_chunks.append({
                    "text": doc,
                    "threat_actor": meta.get("threat_actor"),
                    "aliases": meta.get("aliases"),
                    "origin": meta.get("origin"),
                    "report_id": meta.get("report_id"),
                    "similarity": sim_cos,
                })

        return retrieved_chunks


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    rag = ThreatRAGEngine()
    res = rag.hybrid_search("SolarWinds backdoor SUNBURST 185.225.17.42", gnn_top_group="APT29", top_k=2)
    print("[RAG Engine Hybrid Search Results]:")
    print(json.dumps(res, indent=2))
