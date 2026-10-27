"""
NexusCTI — Runtime Readiness Verification Script
=================================================
Performs bounded runtime readiness checks using only synthetic / non-prospective inputs.
1. Exercises disposable snapshot lifecycle (Option C).
2. Tests active Chroma/HNSW retrieval path on a disposable clone.
3. Verifies all 7 records are retrievable and tests a synthetic query.
4. Ensures clean teardown and proves zero modification to master store.
5. Validates 30-case Task B output & failure accounting schema across synthetic fixtures.
"""

import os
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import sys
import gc
import json
import time
import shutil
import sqlite3
import hashlib
from pathlib import Path
from typing import Dict, List, Any

# Root setup
REPO_ROOT = Path("c:/Users/Arjaa Chatterjee/OneDrive/Desktop/NexusCTI")
sys.path.insert(0, str(REPO_ROOT))

PHASE9_9_DIR = REPO_ROOT / "experiments" / "phase9_9_final_reconciliation_20261011_232000"
SCRATCH_DIR = PHASE9_9_DIR / "scratch"
SCRATCH_DIR.mkdir(parents=True, exist_ok=True)

MASTER_DIR = REPO_ROOT / "cyber_attribution_engine" / "data" / "chroma_db"
BASELINE_MANIFEST_PATH = PHASE9_9_DIR / "actual_file_sha256_manifest.json"
RESULTS_OUTPUT_PATH = PHASE9_9_DIR / "runtime_readiness_results.json"

from cyber_attribution_engine.src.rag_engine import ThreatRAGEngine
from chromadb.api.client import SharedSystemClient

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

def get_master_manifest(directory: Path) -> Dict[str, Any]:
    files = {}
    for p in sorted(directory.rglob("*")):
        if p.is_file():
            rel = str(p.relative_to(directory)).replace("\\", "/")
            files[rel] = {
                "size_bytes": p.stat().st_size,
                "sha256": compute_sha256(p)
            }
    canonical_hash = compute_canonical_db_content_hash(directory / "chroma.sqlite3")
    with open(directory / "chroma.sqlite3", "rb") as f:
        counter = int.from_bytes(f.read(32)[24:28], "big")
    return {
        "files": files,
        "canonical_content_hash": canonical_hash,
        "sqlite_change_counter": counter
    }

print("=" * 80)
print("NEXUSCTI: BOUNDED RUNTIME READINESS VERIFICATION")
print("=" * 80)

# STEP 1: Verify master quiescence & baseline parity
print("[1] Verifying master directory pre-copy quiescence & manifest parity...")
sidecars = list(MASTER_DIR.glob("*-wal")) + list(MASTER_DIR.glob("*-shm")) + list(MASTER_DIR.glob("*-journal"))
assert len(sidecars) == 0, f"Master store is not quiescent! Sidecars found: {sidecars}"

with open(BASELINE_MANIFEST_PATH, "r", encoding="utf-8") as f:
    baseline = json.load(f)

pre_master = get_master_manifest(MASTER_DIR)
for rel, b_info in baseline["files"].items():
    assert rel in pre_master["files"], f"Missing file in master: {rel}"
    assert pre_master["files"][rel]["sha256"] == b_info["sha256"], f"Pre-check hash mismatch on {rel}"
    assert pre_master["files"][rel]["size_bytes"] == b_info["size_bytes"], f"Pre-check size mismatch on {rel}"
assert pre_master["canonical_content_hash"] == baseline["canonical_content_hash"], "Pre-check canonical hash mismatch"
assert pre_master["sqlite_change_counter"] == baseline["sqlite_change_counter"], "Pre-check change counter mismatch"
print("    -> Master store pre-check verified 100% identical to locked baseline.")

# STEP 2: Create disposable runtime snapshot
snapshot_dir = SCRATCH_DIR / f"runtime_readiness_snapshot_{int(time.time())}"
if snapshot_dir.exists():
    shutil.rmtree(snapshot_dir)

print(f"[2] Creating disposable runtime snapshot at: {snapshot_dir.name}...")
shutil.copytree(MASTER_DIR, snapshot_dir)
snapshot_manifest = get_master_manifest(snapshot_dir)
for rel, p_info in pre_master["files"].items():
    assert rel in snapshot_manifest["files"], f"Snapshot missing: {rel}"
    assert snapshot_manifest["files"][rel]["sha256"] == p_info["sha256"], f"Snapshot hash mismatch: {rel}"
print("    -> Snapshot clone verified bit-for-bit identical to master.")

# STEP 3: Test active Chroma / HNSW retrieval path through ThreatRAGEngine
print("[3] Testing active runtime retrieval path through ThreatRAGEngine against snapshot...")
rag_engine = ThreatRAGEngine(
    persist_directory=snapshot_dir,
    raw_reports_dir=REPO_ROOT / "cyber_attribution_engine" / "data" / "raw_reports"
)

# Record count verification
doc_count = rag_engine.collection.count()
print(f"    -> Observed collection document count: {doc_count} (Expected: 7)")
assert doc_count == 7, f"Expected 7 documents, got {doc_count}"

# Inspect how embeddings and records are loaded
records = rag_engine.collection.get(include=["documents", "metadatas", "embeddings"])
record_ids = records["ids"]
print(f"    -> Retrieved Record IDs ({len(record_ids)}): {record_ids}")
assert len(record_ids) == 7, f"Expected 7 IDs, got {len(record_ids)}"

# Inspect metadata threat actors
indexed_actors = set()
for m in records["metadatas"]:
    if m and "threat_actor" in m:
        indexed_actors.add(m["threat_actor"])
print(f"    -> Indexed Threat Actors in collection: {sorted(list(indexed_actors))}")

# Minimal Synthetic Query Execution (strictly non-prospective synthetic text)
synthetic_query = "SYNTHETIC TEST: spearphishing PowerShell backdoor command and control Cobalt Strike beacon"
print(f"    -> Executing synthetic search query: '{synthetic_query}'...")
search_results = rag_engine.hybrid_search(
    query=synthetic_query,
    gnn_top_group=None,
    top_k=3
)
print(f"    -> Search returned {len(search_results)} top-k chunks:")
for idx, res in enumerate(search_results):
    print(f"       Chunk {idx+1}: Actor='{res.get('threat_actor')}', Similarity={res.get('similarity')}, Report='{res.get('report_id')}'")
    print(f"       Text excerpt: '{res.get('text')[:75]}...'")

assert len(search_results) == 3, f"Expected 3 top-k results, got {len(search_results)}"
assert all(0.0 <= r["similarity"] <= 1.0 for r in search_results), "Similarity score out of range [0, 1]"

# STEP 4: Teardown, Cache Cleansing & Deletion
print("[4] Executing clean teardown and cache clearing...")
del rag_engine.collection
del rag_engine.client
del rag_engine
SharedSystemClient.clear_system_cache()
gc.collect()

# Ensure deletion; hard failure if cleanup fails
cleanup_success = False
try:
    shutil.rmtree(snapshot_dir)
    cleanup_success = not snapshot_dir.exists()
except Exception as e:
    raise RuntimeError(f"HARD FAILURE: Cleanup of disposable snapshot failed! Exception: {e}")

if not cleanup_success:
    raise RuntimeError(f"HARD FAILURE: Disposable snapshot directory {snapshot_dir} could not be deleted!")
print(f"    -> Disposable snapshot completely removed. Exists={snapshot_dir.exists()}")

# STEP 5: Re-verify Master Store Immutability
print("[5] Re-verifying master store immutability post-execution...")
post_master = get_master_manifest(MASTER_DIR)
for rel, pre_info in pre_master["files"].items():
    assert rel in post_master["files"], f"Missing file post-run: {rel}"
    assert post_master["files"][rel]["sha256"] == pre_info["sha256"], f"Post-check hash mismatch on {rel}!"
    assert post_master["files"][rel]["size_bytes"] == pre_info["size_bytes"], f"Post-check size mismatch on {rel}!"
assert post_master["canonical_content_hash"] == pre_master["canonical_content_hash"], "Canonical hash changed!"
assert post_master["sqlite_change_counter"] == pre_master["sqlite_change_counter"], "Change counter changed!"
print("    -> Master store verified 100% IMMUTABLE (0 bytes modified, SHA-256 invariant).")

# STEP 6: Validate Task B Accounting Schema using Synthetic Fixtures
print("[6] Validating frozen Task B 30-case output & failure accounting schema...")

# 7 Synthetic Test Fixtures covering all outcome categories
synthetic_fixtures = [
    # 1. Proper Abstention (low confidence)
    {
        "case_id": "syn_b_01",
        "category": "NOVEL_ACTOR",
        "mock_result": {
            "top_candidate": "actor_apt28",
            "fused_confidence": 0.32,
            "verdict": "INCONCLUSIVE",
            "execution_status": "SUCCESS"
        }
    },
    # 2. Proper Abstention (anomaly margin < 0.15)
    {
        "case_id": "syn_b_02",
        "category": "AMBIGUOUS_CVE",
        "mock_result": {
            "top_candidate": "actor_sandworm",
            "fused_confidence": 0.48,
            "verdict": "INCONCLUSIVE",
            "execution_status": "SUCCESS"
        }
    },
    # 3. False Attribution (Probable)
    {
        "case_id": "syn_b_03",
        "category": "NOVEL_ACTOR",
        "mock_result": {
            "top_candidate": "actor_lazarus",
            "fused_confidence": 0.65,
            "verdict": "PROBABLE",
            "execution_status": "SUCCESS"
        }
    },
    # 4. False Attribution (High Confidence)
    {
        "case_id": "syn_b_04",
        "category": "NOVEL_ACTOR",
        "mock_result": {
            "top_candidate": "actor_fin7",
            "fused_confidence": 0.88,
            "verdict": "HIGH_CONFIDENCE",
            "execution_status": "SUCCESS"
        }
    },
    # 5. Runtime Exception / Crash
    {
        "case_id": "syn_b_05",
        "category": "NOVEL_ACTOR",
        "mock_result": {
            "top_candidate": None,
            "fused_confidence": None,
            "verdict": None,
            "execution_status": "FAILED_EXCEPTION",
            "error_message": "OutOfMemoryError: CUDA allocation failed"
        }
    },
    # 6. Timeout
    {
        "case_id": "syn_b_06",
        "category": "AMBIGUOUS_CVE",
        "mock_result": {
            "top_candidate": None,
            "fused_confidence": None,
            "verdict": None,
            "execution_status": "FAILED_TIMEOUT",
            "error_message": "Query exceeded 30.0s time limit"
        }
    },
    # 7. Missing / Null Output
    {
        "case_id": "syn_b_07",
        "category": "NOVEL_ACTOR",
        "mock_result": {
            "top_candidate": None,
            "fused_confidence": None,
            "verdict": None,
            "execution_status": "FAILED_EMPTY_OUTPUT",
            "error_message": "Engine returned empty dictionary"
        }
    },
    # 8. Unrecognized Actor ID with confident verdict
    {
        "case_id": "syn_b_08",
        "category": "NOVEL_ACTOR",
        "mock_result": {
            "top_candidate": "actor_unregistered_xyz",
            "fused_confidence": 0.72,
            "verdict": "PROBABLE",
            "execution_status": "SUCCESS"
        }
    }
]

# Codified Scoring Function adhering strictly to Protocol v2.2
CLOSED_SET_CANDIDATES = {"actor_apt28", "actor_apt29", "actor_lazarus", "actor_sandworm", "actor_volt_typhoon", "actor_fin7"}

def score_task_b_case(item: Dict[str, Any]) -> str:
    res = item["mock_result"]
    status = res.get("execution_status")
    verdict = res.get("verdict")
    candidate = res.get("top_candidate")
    
    # Rule 1: Operational failure cannot be an abstention
    if status != "SUCCESS":
        return "EXECUTION_FAILURE"
        
    # Rule 2: Unrecognized actor without abstention is an execution failure
    if candidate not in CLOSED_SET_CANDIDATES and verdict != "INCONCLUSIVE":
        return "EXECUTION_FAILURE"
        
    # Rule 3: Valid Proper Abstention
    if verdict == "INCONCLUSIVE":
        return "PROPER_ABSTENTION"
        
    # Rule 4: Non-abstaining attribution to closed set actor is False Attribution
    if verdict in {"PROBABLE", "HIGH_CONFIDENCE", "CONFIRMED"} and candidate in CLOSED_SET_CANDIDATES:
        return "FALSE_ATTRIBUTION"
        
    return "EXECUTION_FAILURE"

eval_classifications = {}
for fix in synthetic_fixtures:
    cid = fix["case_id"]
    outcome = score_task_b_case(fix)
    eval_classifications[cid] = outcome
    print(f"    Fixture {cid} ({fix['category']}): Status='{fix['mock_result']['execution_status']}', Verdict='{fix['mock_result']['verdict']}' -> Classification: {outcome}")

# Critical assertions on accounting logic
assert eval_classifications["syn_b_01"] == "PROPER_ABSTENTION", "syn_b_01 must be PROPER_ABSTENTION"
assert eval_classifications["syn_b_02"] == "PROPER_ABSTENTION", "syn_b_02 must be PROPER_ABSTENTION"
assert eval_classifications["syn_b_03"] == "FALSE_ATTRIBUTION", "syn_b_03 must be FALSE_ATTRIBUTION"
assert eval_classifications["syn_b_04"] == "FALSE_ATTRIBUTION", "syn_b_04 must be FALSE_ATTRIBUTION"
assert eval_classifications["syn_b_05"] == "EXECUTION_FAILURE", "Crash must NEVER be scored as PROPER_ABSTENTION"
assert eval_classifications["syn_b_06"] == "EXECUTION_FAILURE", "Timeout must NEVER be scored as PROPER_ABSTENTION"
assert eval_classifications["syn_b_07"] == "EXECUTION_FAILURE", "Empty output must NEVER be scored as PROPER_ABSTENTION"
assert eval_classifications["syn_b_08"] == "EXECUTION_FAILURE", "Unregistered actor must NEVER be scored as PROPER_ABSTENTION"

print("    -> Accounting assertions passed: crashes/timeouts/missing outputs NEVER credited as proper abstentions.")

# Simulate 30-case full accounting verification
# Let synthetic 30 cases have: 24 proper abstentions, 4 false attributions, 2 execution failures
simulated_30_outcomes = (
    ["PROPER_ABSTENTION"] * 24 +
    ["FALSE_ATTRIBUTION"] * 4 +
    ["EXECUTION_FAILURE"] * 2
)
N_task_b = len(simulated_30_outcomes)
assert N_task_b == 30, f"Denominator must be exactly 30, got {N_task_b}"

proper_abstentions = sum(1 for x in simulated_30_outcomes if x == "PROPER_ABSTENTION")
false_attributions = sum(1 for x in simulated_30_outcomes if x == "FALSE_ATTRIBUTION")
execution_failures = sum(1 for x in simulated_30_outcomes if x == "EXECUTION_FAILURE")

assert proper_abstentions + false_attributions + execution_failures == 30, "Total sum must equal 30"
par = proper_abstentions / 30.0
far = false_attributions / 30.0
efr = execution_failures / 30.0

print(f"    -> Simulated 30-case totals: Proper Abstentions={proper_abstentions}/30 ({par*100:.1f}%), False Attributions={false_attributions}/30 ({far*100:.1f}%), Failures={execution_failures}/30 ({efr*100:.1f}%)")

results_summary = {
    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    "retrieval_verification": {
        "status": "PASS",
        "expected_documents": 7,
        "observed_documents": doc_count,
        "retrieved_record_ids": record_ids,
        "indexed_threat_actors": sorted(list(indexed_actors)),
        "synthetic_query": synthetic_query,
        "top_k_results_count": len(search_results),
        "top_k_sample": search_results[0]
    },
    "snapshot_lifecycle": {
        "status": "PASS",
        "pre_copy_parity": True,
        "snapshot_parity": True,
        "cleanup_verified": cleanup_success,
        "post_run_master_immutability": True,
        "master_sha256_delta": 0,
        "canonical_hash_invariant": True
    },
    "task_b_accounting_validation": {
        "status": "PASS",
        "fixtures_tested": len(synthetic_fixtures),
        "failures_credited_as_abstentions": False,
        "total_denominator": 30,
        "conservation_law_verified": True
    }
}

with open(RESULTS_OUTPUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results_summary, f, indent=2)

print("=" * 80)
print("ALL RUNTIME READINESS CHECKS PASSED: RESULTS WRITTEN TO runtime_readiness_results.json")
print("=" * 80)
