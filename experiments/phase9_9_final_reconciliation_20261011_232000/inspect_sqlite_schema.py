import sqlite3
from pathlib import Path

db_path = Path(r"C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\cyber_attribution_engine\data\chroma_db\chroma.sqlite3")
conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
cur = conn.cursor()

for t in ["embeddings", "segments", "embeddings_queue"]:
    cols = [col[1] for col in cur.execute(f"PRAGMA table_info({t});").fetchall()]
    print(f"Table {t} columns: {cols}")
    rows = cur.execute(f"SELECT * FROM {t} LIMIT 3;").fetchall()
    print(f"Sample rows from {t}:")
    for r in rows:
        # truncate large fields
        trunc = [str(x)[:60] if x is not None else "None" for x in r]
        print("  ", trunc)

conn.close()
