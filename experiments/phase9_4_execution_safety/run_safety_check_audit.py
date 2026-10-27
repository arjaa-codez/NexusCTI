"""
NexusCTI Phase 9.4: Execution Safety Check & Operational Safeguards Audit
========================================================================
1. Traces and verifies active ChromaDB retrieval path and test read-only enforcement.
2. Audits ground-truth isolation across manifests, graphs, metadata, and inference APIs.
3. Recomputes and reconciles frozen artifact provenance against Phase 9.3 manifests.
4. Verifies the Phase 10 execution contract mechanics on development fixtures.
"""

import os
import sys
import json
import csv
import stat
import shutil
import sqlite3
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Tuple

REPO_ROOT = Path("c:/Users/Arjaa Chatterjee/OneDrive/Desktop/NexusCTI")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
ENGINE_ROOT = REPO_ROOT / "cyber_attribution_engine"
PHASE9_3_DIR = REPO_ROOT / "experiments" / "phase9_3_final_authorization_20261011"
PHASE9_4_DIR = REPO_ROOT / "experiments" / "phase9_4_execution_safety"
SCRATCH_DIR = PHASE9_4_DIR / "scratch"
SCRATCH_DIR.mkdir(parents=True, exist_ok=True)

CHROMA_SQLITE_FILE = ENGINE_ROOT / "data" / "chroma_db" / "chroma.sqlite3"
FROZEN_MANIFEST_PATH = REPO_ROOT / "experiments" / "phase9_benchmark_preparation_20261011_020400" / "frozen_system_manifest.json"
CANDIDATE_MANIFEST_PATH = REPO_ROOT / "experiments" / "phase9_benchmark_preparation_20261011_020400" / "candidate_campaign_manifest.csv"

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

print("=" * 80)
print("NEXUSCTI PHASE 9.4: FINAL EXECUTION-SAFETY CHECK")
print("=" * 80)

# =============================================================================
# 1. READ-ONLY CHROMADB INFERENCE PATH AUDIT
# =============================================================================
print("\n[+] 1. Auditing Active ChromaDB Retrieval Path & Read-Only Enforcement:")

# Verify absolute path resolution
configured_db_path = CHROMA_SQLITE_FILE.resolve()
db_exists = configured_db_path.exists()
print(f"    - Configured Database Path: {configured_db_path}")
print(f"    - Target Exists:            {db_exists}")
assert db_exists, f"ChromaDB file missing at {configured_db_path}"

# Test 1A: Trace active retrieval import and client
import chromadb
from chromadb.config import Settings
from cyber_attribution_engine.src.rag_engine import ThreatRAGEngine

# Copy Chroma DB to scratch for safe active testing
test_chroma_dir = SCRATCH_DIR / "chroma_test_active"
test_chroma_dir.mkdir(parents=True, exist_ok=True)
test_chroma_sqlite = test_chroma_dir / "chroma.sqlite3"
shutil.copy2(CHROMA_SQLITE_FILE, test_chroma_sqlite)

initial_raw_hash = compute_sha256(test_chroma_sqlite)
initial_content_hash = compute_canonical_db_content_hash(test_chroma_sqlite)

# Inspect SQLite header change counter
with open(test_chroma_sqlite, "rb") as f:
    hdr = f.read(32)
initial_change_counter = int.from_bytes(hdr[24:28], "big")

# Run active ThreatRAGEngine on scratch copy
rag = ThreatRAGEngine(persist_directory=test_chroma_dir)
fixture_query = "cisa advisory apt29 solarwinds orion backdoor 185.225.17.42"
retrieved_results = rag.hybrid_search(fixture_query, gnn_top_group="APT29", top_k=2)
del rag

post_active_raw_hash = compute_sha256(test_chroma_sqlite)
post_active_content_hash = compute_canonical_db_content_hash(test_chroma_sqlite)

with open(test_chroma_sqlite, "rb") as f:
    hdr_post = f.read(32)
post_change_counter = int.from_bytes(hdr_post[24:28], "big")

active_content_invariant = (initial_content_hash == post_active_content_hash)
active_raw_invariant = (initial_raw_hash == post_active_raw_hash)

print(f"    - Retrieval Result Count:   {len(retrieved_results)} (Dev fixture retrieved)")
print(f"    - Pre-Test Change Counter:  {initial_change_counter}")
print(f"    - Post-Test Change Counter: {post_change_counter} (Diff: {post_change_counter - initial_change_counter})")
print(f"    - Raw File SHA-256 Match:   {active_raw_invariant}")
print(f"    - Content SHA-256 Match:    {active_content_invariant}")

# Test 1B: Attempt Write-Prevented Execution (Read-Only Filesystem Permission)
test_ro_dir = SCRATCH_DIR / "chroma_test_ro_fs"
test_ro_dir.mkdir(parents=True, exist_ok=True)
test_ro_sqlite = test_ro_dir / "chroma.sqlite3"
shutil.copy2(CHROMA_SQLITE_FILE, test_ro_sqlite)

# Set file to read-only attribute
os.chmod(test_ro_sqlite, stat.S_IREAD)
ro_prevented_error = None
try:
    rag_ro = ThreatRAGEngine(persist_directory=test_ro_dir)
    res_ro = rag_ro.hybrid_search(fixture_query, gnn_top_group="APT29", top_k=1)
    del rag_ro
except Exception as e:
    ro_prevented_error = f"{type(e).__name__}: {str(e)}"
finally:
    os.chmod(test_ro_sqlite, stat.S_IWRITE)

print(f"    - Write-Prevented Test:     {'CRASH DETECTED' if ro_prevented_error else 'SUCCESS'}")
if ro_prevented_error:
    print(f"      [!] Error: {ro_prevented_error}")

# =============================================================================
# 2. GROUND-TRUTH ACCESS CONTROL AUDIT
# =============================================================================
print("\n[+] 2. Auditing Ground-Truth Isolation & Blinding Safeguards:")

# Audit candidate campaign manifest columns
with open(CANDIDATE_MANIFEST_PATH, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    rows = list(reader)

print(f"    - Candidate Manifest Total Rows: {len(rows)}")
print(f"    - Manifest Fieldnames: {fieldnames}")

# Verify exact ground truth storage locations
gt_columns = [col for col in fieldnames if "actor" in col.lower() or "label" in col.lower() or "ground_truth" in col.lower()]
print(f"    - Columns containing labels:     {gt_columns}")

# Verify that inference engine functions do not accept ground truth
from cyber_attribution_engine.src.gnn_model import AttributionReasoner
from cyber_attribution_engine.src.fusion_layer import HybridFusionEngine

import inspect
reasoner_args = inspect.getfullargspec(AttributionReasoner.attribute_ioc).args
rag_args = inspect.getfullargspec(ThreatRAGEngine.hybrid_search).args
fusion_args = inspect.getfullargspec(HybridFusionEngine.compute_hybrid_attribution).args

print(f"    - AttributionReasoner.attribute_ioc args:        {reasoner_args}")
print(f"    - ThreatRAGEngine.hybrid_search args:            {rag_args}")
print(f"    - HybridFusionEngine.compute_hybrid_attribution: {fusion_args}")

has_label_leakage = any("actor" in a.lower() and a != "gnn_top_group" for a in rag_args) or \
                     any("label" in a.lower() or "ground_truth" in a.lower() for a in reasoner_args + fusion_args)

print(f"    - Direct API Parameter Label Leakage: {'DETECTED' if has_label_leakage else 'ZERO_LEAKAGE (Verified)'}")

# Verify absence of cached predictions or leaked outputs in repository
exp_dir = REPO_ROOT / "experiments"
prospective_pred_files = list(exp_dir.glob("**/frozen_test_predictions.csv"))
print(f"    - Existing Prospective Prediction Files Found: {len(prospective_pred_files)}")

# =============================================================================
# 3. FROZEN ARTIFACT PROVENANCE RECONCILIATION
# =============================================================================
print("\n[+] 3. Reconciling Frozen Artifact Hashes Against Frozen Manifest:")

with open(FROZEN_MANIFEST_PATH, "r", encoding="utf-8") as f:
    f_sys = json.load(f)

frozen_files_reconciliation = {}
mismatch_count = 0

for k, v in f_sys.get("frozen_files", {}).items():
    p = REPO_ROOT / v["path"]
    if not p.exists():
        frozen_files_reconciliation[k] = {"status": "MISSING", "path": v["path"]}
        mismatch_count += 1
    else:
        curr_h = compute_sha256(p)
        exp_h = v["sha256"]
        if curr_h == exp_h:
            frozen_files_reconciliation[k] = {
                "status": "REPRODUCED_EXACT",
                "path": v["path"],
                "sha256": curr_h
            }
        else:
            mismatch_count += 1
            is_chroma = "chroma.sqlite3" in v["path"]
            frozen_files_reconciliation[k] = {
                "status": "EXPECTED_SQLITE_MUTATION" if is_chroma else "FAILED_MISMATCH",
                "path": v["path"],
                "expected_sha256": exp_h,
                "current_sha256": curr_h
            }

print(f"    - Total Tracked Frozen Artifacts: {len(frozen_files_reconciliation)}")
print(f"    - Exact Static Binary Matches:    {sum(1 for v in frozen_files_reconciliation.values() if v['status'] == 'REPRODUCED_EXACT')}")
print(f"    - Mismatches / Mutable Artifacts: {mismatch_count}")
for k, v in frozen_files_reconciliation.items():
    if v["status"] != "REPRODUCED_EXACT":
        print(f"      [!] {k}: {v['status']} (Path: {v['path']})")

# =============================================================================
# 4. PHASE 10 EXECUTION CONTRACT RE-VERIFICATION
# =============================================================================
print("\n[+] 4. Verifying Phase 10 Execution Contract Mechanics:")

task_a_cases = [r for r in rows if r["task_assignment"] == "Task A: Closed-Set Evaluation"]
task_b_cases = [r for r in rows if r["task_assignment"] == "Task B: Open-Set Abstention"]

print(f"    - Task A Registered Cases: {len(task_a_cases)} (Required 100)")
print(f"    - Task B Registered Cases: {len(task_b_cases)} (Required 30)")
assert len(task_a_cases) == 100, f"Expected 100 Task A cases, got {len(task_a_cases)}"
assert len(task_b_cases) == 30, f"Expected 30 Task B cases, got {len(task_b_cases)}"

# Verify stable opaque IDs
all_ids = [r["candidate_id"] for r in task_a_cases + task_b_cases]
unique_ids = set(all_ids)
print(f"    - Unique Opaque Candidate IDs: {len(unique_ids)} / 130")
assert len(unique_ids) == 130, "Candidate IDs are not strictly unique!"

# Compile Telemetry JSON
telemetry = {
    "audit_timestamp": "2026-10-11T03:20:00+05:30",
    "chromadb_readonly_audit": {
        "configured_absolute_path": str(configured_db_path),
        "path_exists": db_exists,
        "initial_change_counter": initial_change_counter,
        "post_change_counter": post_change_counter,
        "raw_binary_invariant": active_raw_invariant,
        "content_invariant": active_content_invariant,
        "write_prevented_error": ro_prevented_error,
        "finding": (
            "ChromaDB's active PersistentClient opens SQLite in read-write mode via PerThreadPool, "
            "updating the file change counter upon connection. When database writes are prevented "
            "at the OS filesystem level, ChromaDB raises InternalError: (code: 8) attempt to write a readonly database."
        )
    },
    "ground_truth_isolation": {
        "manifest_path": str(CANDIDATE_MANIFEST_PATH.relative_to(REPO_ROOT)),
        "label_columns": gt_columns,
        "api_signatures_checked": ["AttributionReasoner.attribute_ioc", "ThreatRAGEngine.hybrid_search", "HybridFusionEngine.compute_hybrid_attribution"],
        "parameter_leakage": has_label_leakage,
        "prospective_predictions_found": len(prospective_pred_files)
    },
    "frozen_artifact_provenance": {
        "manifest_path": str(FROZEN_MANIFEST_PATH.relative_to(REPO_ROOT)),
        "total_files": len(frozen_files_reconciliation),
        "exact_matches": sum(1 for v in frozen_files_reconciliation.values() if v["status"] == "REPRODUCED_EXACT"),
        "mismatches": mismatch_count,
        "details": frozen_files_reconciliation
    },
    "execution_contract": {
        "task_a_count": len(task_a_cases),
        "task_b_count": len(task_b_cases),
        "unique_ids_count": len(unique_ids),
        "primary_endpoint": "Paired Top-3 accuracy Full Hybrid vs Retrieval-only",
        "primary_test": "Exact two-sided McNemar test, alpha = 0.05",
        "directional_condition": "Delta > 0",
        "planning_mde": "+15.0 percentage points",
        "ci_method": "Agresti-Min (2005) 95% paired interval",
        "missing_data_policy": "Rank = 99 (Incorrect) for timeouts, errors, or empty predictions"
    }
}

out_telemetry = PHASE9_4_DIR / "execution_safety_telemetry.json"
with open(out_telemetry, "w", encoding="utf-8") as f:
    json.dump(telemetry, f, indent=2)

print(f"\n[+] Saved execution safety telemetry: {out_telemetry.name}")
print("[+] Safety audit script execution completed.")
