import chromadb
from pathlib import Path

client = chromadb.PersistentClient(path="cyber_attribution_engine/data/chroma_db")
coll = client.get_collection("cti_threat_reports")

res8 = coll.query(query_texts=["threat actor not in registry"], n_results=7)
print("=== T8 Chroma all 7 items ===")
for i in range(7):
    print(f"Rank {i+1}: {res8['ids'][0][i]} | dist={res8['distances'][0][i]:.6f}")

res10 = coll.query(query_texts=["!@#$%^&*()_+~`{}[]:;'<>?,./"], n_results=7)
print("\n=== T10 Chroma all 7 items ===")
for i in range(7):
    print(f"Rank {i+1}: {res10['ids'][0][i]} | dist={res10['distances'][0][i]:.6f}")
