import sqlite3
from pathlib import Path

db_path = Path(r"C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\cyber_attribution_engine\data\chroma_db\chroma.sqlite3")
conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
cur = conn.cursor()

tables = cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
print("Tables in chroma.sqlite3:", [t[0] for t in tables])

for t in ["embeddings", "embedding_metadata", "segments", "collections", "embeddings_queue"]:
    count = cur.execute(f"SELECT COUNT(*) FROM {t};").fetchone()[0]
    print(f"Table {t}: {count} rows")

cur.execute("SELECT id, string_id, length(vector), vector IS NULL FROM embeddings LIMIT 10;")
rows = cur.fetchall()
print("Embeddings sample (id, string_id, vector_len, is_null):")
for r in rows:
    print(r)

cur.execute("SELECT * FROM segments;")
print("Segments:")
for s in cur.fetchall():
    print(s)
conn.close()
