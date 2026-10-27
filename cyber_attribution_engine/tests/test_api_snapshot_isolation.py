"""
Focused Test Suite: Secondary API Runtime Snapshot Isolation & Master Immutability
==================================================================================
Tests:
1. Snapshot creation and bit-for-bit cryptographic parity
2. Manifest mismatch and quiescence fail-closed detection
3. Startup failure cleanup (no leaked snapshots or state)
4. Secondary API initialization against disposable snapshot, not frozen master
5. API shutdown and teardown handle clearance
6. Master store immutability verification (5 files + canonical content hash)
"""

from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from pathlib import Path

# Enforce offline HuggingFace execution to prevent network socket hangs
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from cyber_attribution_engine.src.snapshot_manager import (
    ConsistentSnapshotManager,
    LOCKED_FIVE_FILE_MANIFEST,
    LOCKED_CANONICAL_CONTENT_HASH,
    LOCKED_SQLITE_CHANGE_COUNTER,
    LOCKED_DOCUMENT_COUNT,
    build_directory_manifest,
    compute_canonical_db_content_hash,
    get_sqlite_change_counter,
)
from cyber_attribution_engine.src import api


class TestApiSnapshotIsolation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.master_dir = api.CHROMA_DIR
        self_test_manifest = build_directory_manifest(cls.master_dir)
        cls.initial_manifest = self_test_manifest

    def setUp(self):
        # Ensure clean initial state for api module
        api.cleanup_engines()

    def tearDown(self):
        # Ensure clean teardown after each test
        api.cleanup_engines()

    def test_01_master_baseline_integrity(self):
        """Verifies that the frozen master store exactly matches the locked manifest."""
        current_manifest = build_directory_manifest(self.master_dir)
        self.assertEqual(
            set(current_manifest.keys()),
            set(LOCKED_FIVE_FILE_MANIFEST.keys()),
            "Master directory file set must match locked five-file specification.",
        )
        for rel_path, expected_meta in LOCKED_FIVE_FILE_MANIFEST.items():
            self.assertEqual(
                current_manifest[rel_path]["sha256"],
                expected_meta["sha256"],
                f"Master file {rel_path} SHA-256 mismatch.",
            )
            self.assertEqual(
                current_manifest[rel_path]["size_bytes"],
                expected_meta["size_bytes"],
                f"Master file {rel_path} size mismatch.",
            )

        # Invariant canonical SQLite content hash and change counter
        master_db = self.master_dir / "chroma.sqlite3"
        content_hash = compute_canonical_db_content_hash(master_db)
        self.assertEqual(
            content_hash,
            LOCKED_CANONICAL_CONTENT_HASH,
            "Master canonical DB content hash must match locked baseline.",
        )
        change_counter = get_sqlite_change_counter(master_db)
        self.assertEqual(
            change_counter,
            LOCKED_SQLITE_CHANGE_COUNTER,
            "Master SQLite change counter must be exactly 30.",
        )

    def test_02_snapshot_creation_and_parity(self):
        """Verifies disposable snapshot creation, integrity checks, and teardown."""
        with tempfile.TemporaryDirectory() as scratch_dir:
            mgr = ConsistentSnapshotManager(
                master_dir=self.master_dir,
                scratch_base_dir=Path(scratch_dir),
            )
            snap_dir = mgr.create_snapshot()
            try:
                self.assertTrue(snap_dir.exists(), "Snapshot directory must exist.")
                snap_manifest = build_directory_manifest(snap_dir)
                self.assertEqual(
                    set(snap_manifest.keys()),
                    set(LOCKED_FIVE_FILE_MANIFEST.keys()),
                    "Snapshot directory file set must match master.",
                )
                for rel_path, expected_meta in LOCKED_FIVE_FILE_MANIFEST.items():
                    self.assertEqual(
                        snap_manifest[rel_path]["sha256"],
                        expected_meta["sha256"],
                        f"Snapshot {rel_path} hash parity mismatch.",
                    )
            finally:
                mgr.destroy_snapshot(snap_dir)
                self.assertFalse(snap_dir.exists(), "Snapshot directory must be removed after destruction.")

    def test_03_manifest_mismatch_fail_closed(self):
        """Verifies that an invalid or tampered master directory fails closed."""
        with tempfile.TemporaryDirectory() as fake_master_dir:
            fake_path = Path(fake_master_dir)
            # Create a corrupted mock directory missing files and wrong hashes
            (fake_path / "chroma.sqlite3").write_bytes(b"corrupted SQLite data")
            mgr = ConsistentSnapshotManager(master_dir=fake_path)

            with self.assertRaises((ValueError, RuntimeError)):
                mgr.verify_master_manifest()

            with self.assertRaises((ValueError, RuntimeError)):
                mgr.create_snapshot()

    def test_04_quiescence_violation_fail_closed(self):
        """Verifies that active SQLite sidecars (WAL/SHM/journal) trigger fail-closed abort."""
        with tempfile.TemporaryDirectory() as fake_master_dir:
            fake_path = Path(fake_master_dir)
            shutil.copytree(self.master_dir, fake_path, dirs_exist_ok=True)
            # Inject an active WAL sidecar
            wal_file = fake_path / "chroma.sqlite3-wal"
            wal_file.write_bytes(b"active uncommitted transaction")

            mgr = ConsistentSnapshotManager(master_dir=fake_path)
            with self.assertRaises(RuntimeError) as ctx:
                mgr.assert_master_quiescence()
            self.assertIn("FAIL-CLOSED", str(ctx.exception))

            with self.assertRaises(RuntimeError):
                mgr.create_snapshot()

    def test_05_api_engine_isolation_against_disposable_snapshot(self):
        """Verifies that get_engines() binds ThreatRAGEngine to a disposable snapshot, never CHROMA_DIR."""
        engine = api.get_engines()
        self.assertIsNotNone(engine, "HybridFusionEngine must be instantiated.")
        self.assertIsNotNone(api.active_snapshot_dir, "Active snapshot directory must be set.")
        self.assertNotEqual(
            api.active_snapshot_dir.resolve(),
            self.master_dir.resolve(),
            "ThreatRAGEngine must NOT be bound to the frozen master directory!",
        )
        # Check ThreatRAGEngine persist_directory
        self.assertEqual(
            api.rag_engine.persist_directory.resolve(),
            api.active_snapshot_dir.resolve(),
            "ThreatRAGEngine persist directory must be the isolated disposable snapshot.",
        )
        # Verify collection loads expected 7 chunks
        self.assertEqual(
            api.rag_engine.collection.count(),
            LOCKED_DOCUMENT_COUNT,
            f"Collection must load exactly {LOCKED_DOCUMENT_COUNT} documents.",
        )

        # Cleanup and verify snapshot is deleted
        snap_path = api.active_snapshot_dir
        api.cleanup_engines()
        self.assertIsNone(api.active_snapshot_dir, "active_snapshot_dir must be reset to None.")
        self.assertIsNone(api.fusion_engine, "fusion_engine must be reset to None.")
        self.assertFalse(snap_path.exists(), "Disposable snapshot must be removed from disk on cleanup.")

    def test_06_startup_failure_cleanup(self):
        """Verifies that a failure during engine initialization cleans up and does not leak state."""
        # Force snapshot_manager to point to an invalid directory
        with tempfile.TemporaryDirectory() as bad_dir:
            bad_mgr = ConsistentSnapshotManager(master_dir=Path(bad_dir))
            api.snapshot_manager = bad_mgr

            with self.assertRaises(Exception):
                api.get_engines()

            # Verify no active snapshot or engine leaked
            self.assertIsNone(api.active_snapshot_dir, "No active snapshot directory should remain on failure.")
            self.assertIsNone(api.fusion_engine, "fusion_engine must be None after failure.")
            self.assertIsNone(api.rag_engine, "rag_engine must be None after failure.")

    def test_07_master_immutability_after_all_tests(self):
        """Verifies zero bytes or bits changed in the master store after tests."""
        current_manifest = build_directory_manifest(self.master_dir)
        for rel_path, expected_meta in LOCKED_FIVE_FILE_MANIFEST.items():
            self.assertEqual(
                current_manifest[rel_path]["sha256"],
                expected_meta["sha256"],
                f"Master file {rel_path} SHA-256 must remain identical.",
            )
            self.assertEqual(
                current_manifest[rel_path]["size_bytes"],
                expected_meta["size_bytes"],
                f"Master file {rel_path} size must remain identical.",
            )

        master_db = self.master_dir / "chroma.sqlite3"
        content_hash = compute_canonical_db_content_hash(master_db)
        self.assertEqual(
            content_hash,
            LOCKED_CANONICAL_CONTENT_HASH,
            "Master canonical DB content hash must remain unchanged.",
        )
        change_counter = get_sqlite_change_counter(master_db)
        self.assertEqual(
            change_counter,
            LOCKED_SQLITE_CHANGE_COUNTER,
            "Master SQLite change counter must remain exactly 30.",
        )


if __name__ == "__main__":
    unittest.main()
