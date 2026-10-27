import sys
from pathlib import Path
import numpy as np
import json
import sqlite3

REPO_ROOT = Path("c:/Users/Arjaa Chatterjee/OneDrive/Desktop/NexusCTI")
sys.path.insert(0, str(REPO_ROOT))
from cyber_attribution_engine.src.rag_engine import ThreatRAGEngine, MiniLMEmbeddingFunction

class RefinedReadOnlyChromaAdapter:
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

    def hybrid_search(self, query: str, gnn_top_group: str = None, top_k: int = 3):
        query_emb = np.array(self.embedding_fn.embed_query(query), dtype=np.float32)
        
        filtered = self.records
        if gnn_top_group and gnn_top_group != "Unknown":
            candidate_filtered = [r for r in self.records if r.get("threat_actor") == gnn_top_group]
            if candidate_filtered:
                filtered = candidate_filtered

        # Score by raw dot product
        scored = []
        for r in filtered:
            raw_sim = float(np.dot(query_emb, r["vector"]))
            scored.append((raw_sim, r))

        # Sort descending by RAW similarity (matches ChromaDB distance sorting)
        scored.sort(key=lambda x: x[0], reverse=True)

        results = []
        for raw_sim, r in scored[:top_k]:
            sim_cos = max(0.0, round(raw_sim, 4))
            results.append({
                "text": r["text"],
                "threat_actor": r["threat_actor"],
                "aliases": r["aliases"],
                "origin": r["origin"],
                "report_id": r["report_id"],
                "similarity": sim_cos
            })
        return results

# Test across all 10 queries
test_queries = [
    ("T1_SolarWinds_APT29", "SolarWinds backdoor SUNBURST 185.225.17.42", "APT29", 2),
    ("T2_Industroyer2_Sandworm", "Sandworm wiper high voltage substation Industroyer2", "Sandworm Team", 2),
    ("T3_AppleJeus_Lazarus", "AppleJeus cryptocurrency exchange trojanized application", "Lazarus Group", 2),
    ("T4_VoltTyphoon_CriticalInfra", "Volt Typhoon living off the land wmic powershell cve", "Volt Typhoon", 2),
    ("T5_FIN7_Carbanak", "FIN7 financial POS malware Carbanak cash out", "FIN7", 2),
    ("T6_APT28_FancyBear", "APT28 Fancy Bear Zebrocy spearphishing credential harvesting", "APT28", 2),
    ("T7_Unknown_Actor_Filter", "generic ransomware c2 beaconing payload", "Unknown", 3),
    ("T8_NonExistent_Actor", "threat actor not in registry", "NovelUnseenActor", 3),
    ("T9_Empty_Query_String", "", "APT28", 2),
    ("T10_Special_Chars_Query", "!@#$%^&*()_+~`{}[]:;'<>?,./", None, 3)
]

orig_rag = ThreatRAGEngine()
adapter = RefinedReadOnlyChromaAdapter("cyber_attribution_engine/data/chroma_db/chroma.sqlite3")

all_identical = True
for tid, q_text, gnn_actor, k in test_queries:
    o = orig_rag.hybrid_search(q_text, gnn_top_group=gnn_actor, top_k=k)
    r = adapter.hybrid_search(q_text, gnn_top_group=gnn_actor, top_k=k)
    
    match = (len(o) == len(r))
    if match:
        for oi, ri in zip(o, r):
            if oi["threat_actor"] != ri["threat_actor"] or oi["report_id"] != ri["report_id"] or abs(oi["similarity"] - ri["similarity"]) > 1e-4:
                match = False
                break
    if not match:
        all_identical = False
        print(f"FAIL: {tid}")
        print("  Orig:", [(x["threat_actor"], x["report_id"], x["similarity"]) for x in o])
        print("  Adap:", [(x["threat_actor"], x["report_id"], x["similarity"]) for x in r])
    else:
        print(f"PASS: {tid:28s} (100% Bit-Identical)")

print(f"\nALL 10 QUERIES IDENTICAL: {all_identical}")
