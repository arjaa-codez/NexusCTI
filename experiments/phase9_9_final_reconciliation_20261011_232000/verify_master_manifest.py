"""
Read-Only Cryptographic Verification of Master Store
Does NOT use ChromaDB PersistentClient.
Uses only standard library hashlib and sqlite3 in uri=True, mode=ro.
"""
import hashlib
import json
import sqlite3
from pathlib import Path
from datetime import datetime

CHROMA_MASTER_DIR = Path("c:/Users/Arjaa Chatterjee/OneDrive/Desktop/NexusCTI/cyber_attribution_engine/data/chroma_db")
BASELINE_MANIFEST_PATH = Path("c:/Users/Arjaa Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_9_final_reconciliation_20261011_232000/actual_file_sha256_manifest.json")
OUTPUT_COMPARISON_PATH = Path("c:/Users/Arjaa Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_9_final_reconciliation_20261011_232000/master_manifest_comparison.json")

def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def compute_canonical_db_content_hash(db_path: Path) -> str:
    conn = sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True)
    cur = conn.cursor()
    hasher = hashlib.sha256()
    for tbl in ["collections", "embeddings", "embedding_metadata"]:
        cur.execute(f"PRAGMA table_info({tbl})")
        cols = [c[1] for c in cur.fetchall()]
        cur.execute(f"SELECT {', '.join(cols)} FROM {tbl} ORDER BY id")
        for r in cur.fetchall():
            hasher.update(f"{tbl}:{r}\n".encode("utf-8"))
    conn.close()
    return hasher.hexdigest()

def get_sqlite_change_counter(db_path: Path) -> int:
    with open(db_path, "rb") as f:
        hdr = f.read(32)
    return int.from_bytes(hdr[24:28], "big")

# 1. Load baseline
with open(BASELINE_MANIFEST_PATH, "r", encoding="utf-8") as f:
    baseline = json.load(f)

# 2. Compute current state
current_files = {}
for p in sorted(CHROMA_MASTER_DIR.rglob("*")):
    if p.is_file():
        rel = str(p.relative_to(CHROMA_MASTER_DIR)).replace("\\", "/")
        current_files[rel] = {
            "size_bytes": p.stat().st_size,
            "sha256": compute_sha256(p)
        }

db_path = CHROMA_MASTER_DIR / "chroma.sqlite3"
current_canonical_hash = compute_canonical_db_content_hash(db_path)
current_change_counter = get_sqlite_change_counter(db_path)

# 3. Compare
comparison = {
    "verification_timestamp": datetime.now().isoformat(),
    "master_store_path": str(CHROMA_MASTER_DIR).replace("\\", "/"),
    "baseline_manifest_ref": str(BASELINE_MANIFEST_PATH).replace("\\", "/"),
    "canonical_content_hash": {
        "baseline": baseline["canonical_content_hash"],
        "current": current_canonical_hash,
        "match": baseline["canonical_content_hash"] == current_canonical_hash
    },
    "sqlite_change_counter": {
        "baseline": baseline["sqlite_change_counter"],
        "current": current_change_counter,
        "match": baseline["sqlite_change_counter"] == current_change_counter
    },
    "file_comparisons": {},
    "all_files_match": True
}

for rel, base_info in baseline["files"].items():
    cur_info = current_files.get(rel)
    if not cur_info:
        comparison["file_comparisons"][rel] = {
            "status": "MISSING_IN_CURRENT",
            "baseline_sha256": base_info["sha256"],
            "current_sha256": None,
            "match": False
        }
        comparison["all_files_match"] = False
    else:
        match = (base_info["sha256"] == cur_info["sha256"]) and (base_info["size_bytes"] == cur_info["size_bytes"])
        comparison["file_comparisons"][rel] = {
            "status": "MATCH" if match else "MISMATCH",
            "baseline_size": base_info["size_bytes"],
            "current_size": cur_info["size_bytes"],
            "baseline_sha256": base_info["sha256"],
            "current_sha256": cur_info["sha256"],
            "match": match
        }
        if not match:
            comparison["all_files_match"] = False

# Check for unexpected extra files
for rel in current_files:
    if rel not in baseline["files"]:
        comparison["file_comparisons"][rel] = {
            "status": "UNEXPECTED_EXTRA_FILE",
            "match": False
        }
        comparison["all_files_match"] = False

with open(OUTPUT_COMPARISON_PATH, "w", encoding="utf-8") as f:
    json.dump(comparison, f, indent=2)

print("Comparison result:")
print(f"  All files match: {comparison['all_files_match']}")
print(f"  Canonical content hash match: {comparison['canonical_content_hash']['match']} ({current_canonical_hash[:16]}...)")
print(f"  Change counter match: {comparison['sqlite_change_counter']['match']} ({current_change_counter})")
for rel, comp in comparison["file_comparisons"].items():
    print(f"  [{comp['status']}] {rel}: {comp['current_sha256'][:16] if comp.get('current_sha256') else 'N/A'}...")
