import sqlite3
import json

conn = sqlite3.connect("cyber_attribution_engine/data/chroma_db/chroma.sqlite3")
cur = conn.cursor()

print("=== EMBEDDINGS QUEUE ===")
cur.execute("SELECT rowid, id, metadata FROM embeddings_queue")
for r in cur.fetchall():
    m = json.loads(r[2]) if r[2] else {}
    print(f"rowid={r[0]} | id={r[1]} | actor={m.get('threat_actor')} | report={m.get('report_id')}")

print("\n=== SEGMENTS ===")
cur.execute("SELECT id, type, scope, collection FROM segments")
for r in cur.fetchall():
    print(r)

print("\n=== SEGMENT METADATA ===")
cur.execute("SELECT segment_id, key, str_value, int_value, float_value, bool_value FROM segment_metadata")
for r in cur.fetchall():
    print(r)

conn.close()
