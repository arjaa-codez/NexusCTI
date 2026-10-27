"""
NexusCTI — Authoritative Disposable Runtime Snapshot Manager
============================================================
Enforces master store immutability via Option C (Disposable Native ChromaDB Runtime Snapshot Lifecycle).
Reuses the verified fail-closed snapshot lifecycle from Protocol Amendment 3 (v2.2-amended).
Guarantees:
1. Zero writes to the authoritative master directory (cyber_attribution_engine/data/chroma_db/).
2. Master quiescence and cryptographic manifest verification before any copy.
3. Fail-closed snapshot validation (SHA-256 parity, SQLite integrity check, canonical hash, doc count).
4. Safe teardown with ChromaDB singleton cache clearance (SharedSystemClient.clear_system_cache).
"""

from __future__ import annotations

import os
import gc
import time
import uuid
import shutil
import sqlite3
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List

# Authoritative frozen master baseline constants (Protocol Amendment 3 / Phase 9.9)
LOCKED_CANONICAL_CONTENT_HASH = "668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7"
LOCKED_SQLITE_CHANGE_COUNTER = 30
LOCKED_DOCUMENT_COUNT = 7

LOCKED_FIVE_FILE_MANIFEST = {
    "3962f896-273d-4039-b97e-d0aa4e6d29ed/data_level0.bin": {
        "size_bytes": 167600,
        "sha256": "dd3bc35aff31318f10dab2111ad835e55926233f1e0e8922cdc30bc92ce171f8"
    },
    "3962f896-273d-4039-b97e-d0aa4e6d29ed/header.bin": {
        "size_bytes": 100,
        "sha256": "a0e81c3b22454233bc12d0762f06dcca48261a75231cf87c79b75e69a6c00150"
    },
    "3962f896-273d-4039-b97e-d0aa4e6d29ed/length.bin": {
        "size_bytes": 400,
        "sha256": "a2cab3b7fffef0b5e24cb03aaf91e69be401e590bbff1c192c3d12be61d46f06"
    },
    "3962f896-273d-4039-b97e-d0aa4e6d29ed/link_lists.bin": {
        "size_bytes": 0,
        "sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    },
    "chroma.sqlite3": {
        "size_bytes": 294912,
        "sha256": "f4a0960e60ef06d5669df55e648ad463ebbdcdff62381ec6d26e17dfaefc56dc"
    }
}


def compute_sha256(filepath: Path) -> str:
    """Computes SHA-256 digest of a file in 64KB blocks."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def compute_canonical_db_content_hash(db_path: Path) -> str:
    """Computes invariant content hash across SQLite relational tables in read-only mode."""
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
    """Reads 4-byte SQLite header change counter from byte offset 24..28."""
    with open(db_path, "rb") as f:
        hdr = f.read(32)
    return int.from_bytes(hdr[24:28], "big")


def build_directory_manifest(directory: Path) -> Dict[str, Dict[str, Any]]:
    """Builds dictionary mapping relative POSIX paths to size_bytes and sha256."""
    files = {}
    for p in sorted(directory.rglob("*")):
        if p.is_file():
            rel = p.relative_to(directory).as_posix()
            files[rel] = {
                "size_bytes": p.stat().st_size,
                "sha256": compute_sha256(p)
            }
    return files


class ConsistentSnapshotManager:
    """
    Manages creation, validation, and safe destruction of disposable runtime snapshots.
    Reuses the verified lifecycle from Protocol Amendment 3.
    """

    def __init__(
        self,
        master_dir: Path,
        expected_manifest: Optional[Dict[str, Any]] = None,
        expected_content_hash: str = LOCKED_CANONICAL_CONTENT_HASH,
        scratch_base_dir: Optional[Path] = None,
    ):
        self.master_dir = Path(master_dir).resolve()
        self.expected_manifest = expected_manifest or LOCKED_FIVE_FILE_MANIFEST
        self.expected_content_hash = expected_content_hash
        self.scratch_base_dir = (
            Path(scratch_base_dir).resolve()
            if scratch_base_dir
            else self.master_dir.parent / "snapshots"
        )
        self.scratch_base_dir.mkdir(parents=True, exist_ok=True)

    def assert_master_quiescence(self) -> None:
        """Asserts zero active SQLite journal, WAL, or SHM sidecar files in master directory."""
        sidecars = (
            list(self.master_dir.glob("*-wal"))
            + list(self.master_dir.glob("*-shm"))
            + list(self.master_dir.glob("*-journal"))
        )
        if sidecars:
            raise RuntimeError(
                f"FAIL-CLOSED: Master store is not quiescent! Active sidecars detected: {sidecars}"
            )

    def verify_master_manifest(self) -> None:
        """Verifies that the master directory exactly matches the locked manifest."""
        current_manifest = build_directory_manifest(self.master_dir)
        mismatches: List[str] = []

        for rel, expected_info in self.expected_manifest.items():
            if rel not in current_manifest:
                mismatches.append(f"Missing expected file: {rel}")
            else:
                curr_info = current_manifest[rel]
                if curr_info["sha256"] != expected_info["sha256"]:
                    mismatches.append(
                        f"Hash mismatch on {rel}: expected {expected_info['sha256']}, got {curr_info['sha256']}"
                    )
                if curr_info["size_bytes"] != expected_info["size_bytes"]:
                    mismatches.append(
                        f"Size mismatch on {rel}: expected {expected_info['size_bytes']}, got {curr_info['size_bytes']}"
                    )

        for rel in current_manifest:
            if rel not in self.expected_manifest:
                mismatches.append(f"Unexpected extra file in master: {rel}")

        if mismatches:
            raise ValueError(f"FAIL-CLOSED: Master manifest mismatch detected: {mismatches}")

        # Check canonical content hash
        db_path = self.master_dir / "chroma.sqlite3"
        content_hash = compute_canonical_db_content_hash(db_path)
        if content_hash != self.expected_content_hash:
            raise ValueError(
                f"FAIL-CLOSED: Master canonical content hash mismatch: expected {self.expected_content_hash}, got {content_hash}"
            )

    def create_snapshot(self, target_dir: Optional[Path] = None) -> Path:
        """
        Creates, validates, and returns an isolated disposable snapshot directory.
        If validation fails, the target directory is deleted before raising.
        """
        if target_dir is None:
            unique_id = f"snap_{os.getpid()}_{int(time.time())}_{uuid.uuid4().hex[:6]}"
            target_dir = self.scratch_base_dir / unique_id
        else:
            target_dir = Path(target_dir).resolve()

        if target_dir.exists():
            shutil.rmtree(target_dir, ignore_errors=True)

        try:
            # 1. Quiescence and pre-copy manifest checks
            self.assert_master_quiescence()
            self.verify_master_manifest()

            # 2. Atomic recursive copy
            shutil.copytree(self.master_dir, target_dir)

            # 3. Snapshot manifest parity check
            snap_manifest = build_directory_manifest(target_dir)
            for rel, expected_info in self.expected_manifest.items():
                if rel not in snap_manifest:
                    raise ValueError(f"Snapshot copy missing file: {rel}")
                if snap_manifest[rel]["sha256"] != expected_info["sha256"]:
                    raise ValueError(f"Snapshot copy hash mismatch on {rel}")
                if snap_manifest[rel]["size_bytes"] != expected_info["size_bytes"]:
                    raise ValueError(f"Snapshot copy size mismatch on {rel}")

            # 4. SQLite PRAGMA integrity check on snapshot
            db_snap = target_dir / "chroma.sqlite3"
            conn = sqlite3.connect(f"file:{db_snap.resolve()}?mode=ro", uri=True)
            cur = conn.cursor()
            cur.execute("PRAGMA integrity_check;")
            res = cur.fetchall()
            if res != [("ok",)]:
                conn.close()
                raise RuntimeError(f"Snapshot SQLite integrity check failed: {res}")

            # 5. Canonical content hash check on snapshot
            content_hash = compute_canonical_db_content_hash(db_snap)
            if content_hash != self.expected_content_hash:
                conn.close()
                raise ValueError(
                    f"Snapshot content hash mismatch: {content_hash} != {self.expected_content_hash}"
                )

            # 6. Embedding document count check
            cur.execute("SELECT COUNT(*) FROM embeddings;")
            emb_cnt = cur.fetchone()[0]
            conn.close()
            if emb_cnt != LOCKED_DOCUMENT_COUNT:
                raise ValueError(
                    f"Snapshot embedding count {emb_cnt} != {LOCKED_DOCUMENT_COUNT}"
                )

            return target_dir

        except Exception as e:
            # Clean up on failure
            self.destroy_snapshot(target_dir)
            raise e

    def destroy_snapshot(self, target_dir: Path) -> None:
        """
        Safely clears ChromaDB system client cache, forces garbage collection,
        and deletes the disposable snapshot directory with Windows handle release retries.
        """
        target_dir = Path(target_dir).resolve()

        # Release ChromaDB internal singleton caches
        try:
            from chromadb.api.client import SharedSystemClient
            SharedSystemClient.clear_system_cache()
        except Exception:
            pass

        gc.collect()

        if not target_dir.exists():
            return

        for attempt in range(5):
            try:
                shutil.rmtree(target_dir)
                break
            except Exception:
                gc.collect()
                time.sleep(0.05 * (attempt + 1))

        if target_dir.exists():
            shutil.rmtree(target_dir, ignore_errors=True)

        if target_dir.exists():
            raise RuntimeError(
                f"FAIL-CLOSED: Disposable snapshot directory could not be removed: {target_dir}"
            )
