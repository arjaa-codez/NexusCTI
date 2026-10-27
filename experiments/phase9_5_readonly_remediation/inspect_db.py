import sqlite3
import json
import numpy as np
from pathlib import Path

p = Path("cyber_attribution_engine/data/chroma_db/chroma.sqlite3")
conn = sqlite3.connect(f"file:{p.resolve()}?mode=ro", uri=True)
cur = conn.cursor()

print("=== COLLECTIONS ===")
cur.execute("SELECT id, name, dimension, config_json_str FROM collections")
for r in cur.fetchall():
    print(r)

print("\n=== EMBEDDINGS QUEUE (7 CHUNKS) ===")
cur.execute("SELECT id, vector, encoding, metadata FROM embeddings_queue")
rows = cur.fetchall()
print(f"Total rows in embeddings_queue: {len(rows)}")
for r in rows:
    doc_id, vec_blob, enc, meta_str = r
    meta = json.loads(meta_str) if meta_str else {}
    vec = np.frombuffer(vec_blob, dtype=np.float32) if vec_blob else None
    print(f"Doc ID: {doc_id}")
    print(f"  Threat Actor: {meta.get('threat_actor')}")
    print(f"  Report ID:    {meta.get('report_id')}")
    print(f"  Chunk index:  {meta.get('chunk_index')}")
    print(f"  Vector shape: {vec.shape if vec is not None else None}, norm: {float(np.linalg.norm(vec)) if vec is not None else None:.6f}")
    print(f"  Keys in meta: {list(meta.keys())}")

print("\n=== EMBEDDING FULLTEXT SEARCH ===")
cur.execute("SELECT rowid, string_value FROM embedding_fulltext_search")
for r in cur.fetchall():
    print(f"Row {r[0]}: {r[1][:80]}...")

conn.close()
