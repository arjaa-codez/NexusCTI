"""
Synthetic Smoke Test for Secondary API Runtime Snapshot Isolation
==================================================================
Executes:
1. Pre-test master baseline verification.
2. Disposable snapshot creation via secondary API engine initialization.
3. Execution of one minimal synthetic non-prospective IOC query against the secondary API.
4. Clean teardown and snapshot deletion.
5. Post-test master baseline verification (5 files + canonical content hash).
"""

from __future__ import annotations

import os
import sys
import json
from pathlib import Path

# Enforce offline HuggingFace execution
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from cyber_attribution_engine.src.snapshot_manager import (
    build_directory_manifest,
    compute_canonical_db_content_hash,
    get_sqlite_change_counter,
    LOCKED_FIVE_FILE_MANIFEST,
    LOCKED_CANONICAL_CONTENT_HASH,
    LOCKED_SQLITE_CHANGE_COUNTER,
)
from cyber_attribution_engine.src import api


def main():
    print("=" * 70)
    print("NexusCTI — Secondary API Runtime-Isolation Synthetic Smoke Test")
    print("=" * 70)

    master_dir = api.CHROMA_DIR
    print(f"Master store path: {master_dir}")

    # STEP 1: Pre-test master baseline check
    print("\n[1] Verifying Pre-Test Master Baseline...")
    pre_manifest = build_directory_manifest(master_dir)
    assert set(pre_manifest.keys()) == set(LOCKED_FIVE_FILE_MANIFEST.keys()), "Pre-test manifest keys mismatch!"
    for rel, exp in LOCKED_FIVE_FILE_MANIFEST.items():
        assert pre_manifest[rel]["sha256"] == exp["sha256"], f"Pre-test SHA-256 mismatch: {rel}"
        assert pre_manifest[rel]["size_bytes"] == exp["size_bytes"], f"Pre-test size mismatch: {rel}"

    pre_content_hash = compute_canonical_db_content_hash(master_dir / "chroma.sqlite3")
    assert pre_content_hash == LOCKED_CANONICAL_CONTENT_HASH, "Pre-test canonical content hash mismatch!"
    pre_change_counter = get_sqlite_change_counter(master_dir / "chroma.sqlite3")
    assert pre_change_counter == LOCKED_SQLITE_CHANGE_COUNTER, "Pre-test change counter mismatch!"
    print("    -> Pre-test master baseline verified 100% invariant.")

    # STEP 2: Secondary API engine initialization
    print("\n[2] Initializing Secondary API Engine (triggering disposable snapshot creation)...")
    engine = api.get_engines()
    active_snap = api.active_snapshot_dir
    print(f"    -> Active snapshot directory: {active_snap}")
    assert active_snap is not None, "active_snapshot_dir must not be None!"
    assert active_snap.resolve() != master_dir.resolve(), "Active snapshot MUST NOT be master store!"
    assert active_snap.exists(), "Active snapshot directory must exist on disk!"
    assert api.rag_engine.persist_directory.resolve() == active_snap.resolve(), "RAG engine not bound to snapshot!"
    print("    -> Confirmed: ThreatRAGEngine strictly bound to disposable snapshot.")

    # STEP 3: Synthetic IOC query execution
    print("\n[3] Executing Synthetic IOC Query against Secondary API (/attribute pipeline)...")
    # Using RFC 5737 TEST-NET synthetic IP
    synthetic_req = api.AttributionRequest(
        ioc="192.0.2.42",
        alpha=0.5,
        top_k_rag=3,
        ollama_model="llama3",
    )
    result = api.attribute_ioc(synthetic_req)
    print("    -> Synthetic Query Output:")
    print(f"       IOC: {result.get('ioc')} (Type: {result.get('ioc_type')})")
    print(f"       Attributed Group: {result.get('attributed_group')}")
    print(f"       Final Attribution Score: {result.get('final_attribution_score'):.4f}")
    print(f"       GNN Structural Score: {result.get('gnn_structural_score'):.4f}")
    print(f"       RAG Semantic Score: {result.get('rag_semantic_score'):.4f}")
    print(f"       Retrieved Chunks Count: {len(result.get('retrieved_cti_chunks', []))}")
    for idx, c in enumerate(result.get("retrieved_cti_chunks", [])):
        print(f"         Chunk {idx+1}: Actor='{c.get('threat_actor')}', Similarity={c.get('similarity'):.4f}, Report='{c.get('report_id')}'")

    assert result.get("ioc") == "192.0.2.42"
    assert "attributed_group" in result
    assert "final_attribution_score" in result
    assert len(result.get("retrieved_cti_chunks", [])) <= 3
    print("    -> Synthetic query executed successfully.")

    # STEP 4: Safe teardown & snapshot destruction
    print("\n[4] Shutting down Secondary API engines & destroying disposable snapshot...")
    snap_to_clean = active_snap
    api.cleanup_engines()
    assert api.active_snapshot_dir is None, "active_snapshot_dir must be None after cleanup!"
    assert api.fusion_engine is None, "fusion_engine must be None after cleanup!"
    assert not snap_to_clean.exists(), f"Snapshot directory {snap_to_clean} was not deleted!"
    print(f"    -> Snapshot directory {snap_to_clean.name} verified deleted with zero residual handles.")

    # STEP 5: Post-test master baseline check
    print("\n[5] Verifying Post-Test Master Baseline (Zero-Mutation Verification)...")
    post_manifest = build_directory_manifest(master_dir)
    assert set(post_manifest.keys()) == set(LOCKED_FIVE_FILE_MANIFEST.keys()), "Post-test manifest keys mismatch!"
    for rel, exp in LOCKED_FIVE_FILE_MANIFEST.items():
        assert post_manifest[rel]["sha256"] == exp["sha256"], f"Post-test SHA-256 mismatch: {rel}"
        assert post_manifest[rel]["size_bytes"] == exp["size_bytes"], f"Post-test size mismatch: {rel}"

    post_content_hash = compute_canonical_db_content_hash(master_dir / "chroma.sqlite3")
    assert post_content_hash == LOCKED_CANONICAL_CONTENT_HASH, "Post-test canonical content hash mismatch!"
    post_change_counter = get_sqlite_change_counter(master_dir / "chroma.sqlite3")
    assert post_change_counter == LOCKED_SQLITE_CHANGE_COUNTER, "Post-test change counter mismatch!"
    print("    -> Post-test master baseline verified 100% invariant.")
    print("    -> All 5 file SHA-256 digests identical.")
    print("    -> Canonical content hash identical: 668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7")
    print("    -> SQLite change counter identical: 30")

    print("\n" + "=" * 70)
    print("SYNTHETIC SMOKE TEST RESULT: PASS (100% Isolated & Immutable)")
    print("=" * 70)


if __name__ == "__main__":
    main()
