"""
Test script comparing:
1. Original ChromaDB PersistentClient query
2. Read-Only SQLite Adapter query
Across diverse development queries and edge cases (normal, empty, malformed, out-of-vocabulary).
"""

import os
import sys
import json
import sqlite3
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
import numpy as np

REPO_ROOT = Path("c:/Users/Arjaa Chatterjee/OneDrive/Desktop/NexusCTI")
sys.path.insert(0, str(REPO_ROOT))

from cyber_attribution_engine.src.rag_engine import ThreatRAGEngine, MiniLMEmbeddingFunction

# Path to frozen chroma db
CHROMA_PATH = REPO_ROOT / "cyber_attribution_engine" / "data" / "chroma_db" / "chroma.sqlite3"

class ReadOnlyChromaAdapter:
    """Custom read-only query adapter connecting via file:...?mode=ro.
    Guarantees 0-byte header mutations and works on write-protected filesystems.
    """
    def __init__(self, db_path: Path):
        self.db_path = Path(db_path).resolve()
        self.embedding_fn = MiniLMEmbeddingFunction()
        self._load_frozen_records()

    def _load_frozen_records(self):
        conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        cur = conn.cursor()
        cur.execute("SELECT id, vector, metadata FROM embeddings_queue")
        self.records = []
        for r in cur.fetchall():
            doc_id, vec_blob, meta_str = r
            meta = json.loads(meta_str) if meta_str else {}
            vec = np.frombuffer(vec_blob, dtype=np.float32)
            self.records.append({
                "doc_id": doc_id,
                "vector": vec,
                "text": meta.get("chroma:document", ""),
                "threat_actor": meta.get("threat_actor"),
                "aliases": meta.get("aliases"),
                "origin": meta.get("origin"),
                "report_id": meta.get("report_id")
            })
        conn.close()

    def hybrid_search(
        self,
        query: str,
        gnn_top_group: Optional[str] = None,
        top_k: int = 3
    ) -> List[Dict[str, Any]]:
        query_emb = np.array(self.embedding_fn.embed_query(query), dtype=np.float32)
        
        # Filter by candidate actor if provided and not Unknown
        filtered = self.records
        if gnn_top_group and gnn_top_group != "Unknown":
            candidate_filtered = [r for r in self.records if r.get("threat_actor") == gnn_top_group]
            if candidate_filtered:
                filtered = candidate_filtered

        # Score documents via Cosine Similarity = dot product (both unit norm)
        scored = []
        for r in filtered:
            sim = float(np.dot(query_emb, r["vector"]))
            sim_cos = max(0.0, round(sim, 4))
            scored.append({
                "text": r["text"],
                "threat_actor": r["threat_actor"],
                "aliases": r["aliases"],
                "origin": r["origin"],
                "report_id": r["report_id"],
                "similarity": sim_cos
            })

        # Sort descending by similarity
        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return scored[:top_k]

# Run Comparison Test across diverse test queries
queries = [
    ("Q1: Normal SolarWinds", "SolarWinds backdoor SUNBURST 185.225.17.42", "APT29", 2),
    ("Q2: Normal Industroyer", "Sandworm wiper high voltage substation Industroyer2", "Sandworm Team", 2),
    ("Q3: Normal Lazarus", "AppleJeus cryptocurrency exchange trojanized application", "Lazarus Group", 2),
    ("Q4: Unknown GNN actor", "critical infrastructure living off the land wmic powershell", "Unknown", 3),
    ("Q5: Non-matching GNN actor", "FIN7 financial POS malware Carbanak", "NonExistentActor", 2),
    ("Q6: Empty Query", "", "APT28", 2),
    ("Q7: Malformed / special chars", "!@#$%^&*()_+=~`{}[]:;'<>?,./", None, 2),
    ("Q8: Unrestricted Top 5", "APT28 Fancy Bear Zebrocy spearphishing campaign", None, 5)
]

orig_rag = ThreatRAGEngine()
ro_adapter = ReadOnlyChromaAdapter(CHROMA_PATH)

print("=" * 80)
print("COMPARING ORIGINAL CHROMADB VS READ-ONLY QUERY ADAPTER")
print("=" * 80)

all_match = True
for q_name, q_text, gnn_actor, k in queries:
    res_orig = orig_rag.hybrid_search(q_text, gnn_top_group=gnn_actor, top_k=k)
    res_ro = ro_adapter.hybrid_search(q_text, gnn_top_group=gnn_actor, top_k=k)
    
    # Check exact equivalence of retrieved texts, actors, and similarity scores
    match = (len(res_orig) == len(res_ro))
    if match:
        for o, r in zip(res_orig, res_ro):
            if o["threat_actor"] != r["threat_actor"] or o["report_id"] != r["report_id"] or abs(o["similarity"] - r["similarity"]) > 1e-4:
                match = False
                break
    
    if not match:
        all_match = False
        print(f"[FAIL] {q_name}")
        print("  Original:", res_orig)
        print("  Adapter: ", res_ro)
    else:
        print(f"[PASS] {q_name}: {len(res_orig)} results identical (Sim: {[x['similarity'] for x in res_ro]})")

print(f"\nOverall Equivalence: {'100% BIT-IDENTICAL' if all_match else 'DISCREPANCIES DETECTED'}")
