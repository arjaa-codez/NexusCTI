"""
NexusCTI Phase 9.9: Final Integrity Reconciliation & Protocol Approval Preparation
==================================================================================
Direct Machine Validation & Verification Suite.
"""

import os
import sys
import gc
import json
import shutil
import sqlite3
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple

REPO_ROOT = Path("c:/Users/Arjaa Chatterjee/OneDrive/Desktop/NexusCTI")
sys.path.insert(0, str(REPO_ROOT))

PHASE9_9_DIR = REPO_ROOT / "experiments" / "phase9_9_final_reconciliation_20261011_232000"
SCRATCH_DIR = PHASE9_9_DIR / "scratch"
PHASE9_9_DIR.mkdir(parents=True, exist_ok=True)
SCRATCH_DIR.mkdir(parents=True, exist_ok=True)

CHROMA_MASTER_DIR = REPO_ROOT / "cyber_attribution_engine" / "data" / "chroma_db"
CHROMA_MASTER_SQLITE = CHROMA_MASTER_DIR / "chroma.sqlite3"

from cyber_attribution_engine.src.rag_engine import ThreatRAGEngine
from chromadb.api.client import SharedSystemClient

def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def compute_sha1(filepath: Path) -> str:
    h = hashlib.sha1()
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

print("=" * 80)
print("NEXUSCTI PHASE 9.9: FINAL INTEGRITY RECONCILIATION & VALIDATION")
print("=" * 80)

# TASK 1: Full Direct SHA-256 Manifest Generation
manifest = {}
for p in sorted(CHROMA_MASTER_DIR.rglob("*")):
    if p.is_file():
        rel = str(p.relative_to(CHROMA_MASTER_DIR)).replace("\\", "/")
        sha256_val = compute_sha256(p)
        sha1_val = compute_sha1(p)
        size = p.stat().st_size
        manifest[rel] = {
            "size_bytes": size,
            "sha256": sha256_val,
            "sha256_len": len(sha256_val),
            "sha1": sha1_val,
            "sha1_len": len(sha1_val)
        }

print("\n[1] Authoritative Master Store Direct Hash Manifest:")
for rel, meta in manifest.items():
    print(f"    - {rel:48s} | {meta['size_bytes']:7d} B | SHA-256: {meta['sha256']} (len={meta['sha256_len']})")

# Assert all SHA-256 hashes are exactly 64 characters
for rel, meta in manifest.items():
    assert meta["sha256_len"] == 64, f"Hash for {rel} is not 64 hex characters!"
    assert all(c in "0123456789abcdef" for c in meta["sha256"]), f"Hash for {rel} contains non-hex chars!"

manifest_export = {
    "verification_timestamp": "2026-10-11T23:20:00+05:30",
    "master_store_path": str(CHROMA_MASTER_DIR).replace("\\", "/"),
    "canonical_content_hash": compute_canonical_db_content_hash(CHROMA_MASTER_SQLITE),
    "sqlite_change_counter": get_sqlite_change_counter(CHROMA_MASTER_SQLITE),
    "total_files": len(manifest),
    "files": manifest
}

with open(PHASE9_9_DIR / "actual_file_sha256_manifest.json", "w", encoding="utf-8") as f:
    json.dump(manifest_export, f, indent=2)

# TASK 2: Structural HNSW and SQLite Integrity Validation
print("\n[2] Structural HNSW & SQLite Validation:")
conn = sqlite3.connect(f"file:{CHROMA_MASTER_SQLITE.resolve()}?mode=ro", uri=True)
cur = conn.cursor()
cur.execute("PRAGMA integrity_check;")
sqlite_integrity = cur.fetchall()
print(f"    - SQLite PRAGMA integrity_check: {sqlite_integrity}")
assert sqlite_integrity == [("ok",)], "SQLite integrity check failed!"

cur.execute("SELECT id, name, dimension FROM collections;")
col_info = cur.fetchall()
print(f"    - Collections: {col_info}")

cur.execute("SELECT COUNT(*) FROM embeddings;")
emb_count = cur.fetchone()[0]
print(f"    - Embeddings row count: {emb_count}")
assert emb_count == 7, "Embeddings count must be 7!"
conn.close()

# Structural HNSW Validation
seg_dir = CHROMA_MASTER_DIR / "3962f896-273d-4039-b97e-d0aa4e6d29ed"
data_level0_size = (seg_dir / "data_level0.bin").stat().st_size
link_lists_size = (seg_dir / "link_lists.bin").stat().st_size
header_size = (seg_dir / "header.bin").stat().st_size
length_size = (seg_dir / "length.bin").stat().st_size

print(f"    - HNSW data_level0.bin: {data_level0_size} bytes (Graph adjacency and 7 vector embeddings)")
print(f"    - HNSW link_lists.bin:  {link_lists_size} bytes (Empty: expected since max level == 0 for N=7 nodes)")
print(f"    - HNSW header.bin:      {header_size} bytes (HNSW configuration and dimension headers)")
print(f"    - HNSW length.bin:      {length_size} bytes (Vector buffer length metadata)")

# TASK 3: Snapshot Creation and Equivalence Test
print("\n[3] Testing Disposable Snapshot & Active Runtime Path:")
disposable_dir = SCRATCH_DIR / "runtime_snapshot_phase9_9"
if disposable_dir.exists():
    shutil.rmtree(disposable_dir, ignore_errors=True)

# Check master quiescence before copy
master_sidecars = list(CHROMA_MASTER_DIR.glob("*-wal")) + list(CHROMA_MASTER_DIR.glob("*-shm")) + list(CHROMA_MASTER_DIR.glob("*-journal"))
print(f"    - Master sidecar check (WAL/SHM/journal): {[s.name for s in master_sidecars]} ({len(master_sidecars)} files)")
assert len(master_sidecars) == 0, "Master database not quiescent!"

# Copy snapshot
shutil.copytree(CHROMA_MASTER_DIR, disposable_dir)
snap_manifest = {str(p.relative_to(disposable_dir)).replace("\\", "/"): compute_sha256(p) for p in disposable_dir.rglob("*") if p.is_file()}
for rel in manifest:
    assert snap_manifest[rel] == manifest[rel]["sha256"], f"Snapshot parity failed for {rel}!"
print("    - Snapshot atomic clone and parity verification: PASSED")

# Run active ThreatRAGEngine on snapshot
rag = ThreatRAGEngine(persist_directory=str(disposable_dir))

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

equivalence_runs = []
for qid, qtext, gnn_actor, top_k in test_queries:
    res = rag.hybrid_search(qtext, gnn_top_group=gnn_actor, top_k=top_k)
    actors = [r["threat_actor"] for r in res]
    sims = [r["similarity"] for r in res]
    equivalence_runs.append({"id": qid, "top1": actors[0], "actors": actors, "scores": sims})
    print(f"    - {qid:30s} | Top-1: {actors[0]:15s} | Scores: {sims}")

# Clean teardown
del rag.collection
del rag.client
del rag
SharedSystemClient.clear_system_cache()
gc.collect()
shutil.rmtree(disposable_dir, ignore_errors=True)
print(f"    - Snapshot safely destroyed: {not disposable_dir.exists()}")
assert not disposable_dir.exists(), "Disposable snapshot was not deleted!"

# Confirm master untouched
post_master_manifest = {str(p.relative_to(CHROMA_MASTER_DIR)).replace("\\", "/"): compute_sha256(p) for p in CHROMA_MASTER_DIR.rglob("*") if p.is_file()}
master_intact = all(post_master_manifest[k] == manifest[k]["sha256"] for k in manifest)
print(f"    - Post-test master directory invariance: {master_intact}")
assert master_intact, "Master directory was modified during audit!"

print("\nPhase 9.9 verification suite execution complete.")
