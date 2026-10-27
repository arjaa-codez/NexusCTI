# Phase 9.8 — Master Hash Chain of Custody Report

**Audit Phase:** NexusCTI Phase 9.8 — Master Hash Chain of Custody and Snapshot Consistency  
**Timestamp:** 2026-10-11T23:05:00+05:30  
**Project Root:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI`  
**Governing Objective:** Forensic investigation and reconciliation of the master SQLite database SHA-256 hash transition between Phase 9.6 and Phase 9.7.  

---

## 1. Executive Summary and Problem Statement

In the Phase 9.7 audit request, the oversight committee noted a discrepancy in the reported binary SHA-256 hash of the authoritative master vector store database (`cyber_attribution_engine/data/chroma_db/chroma.sqlite3`):
- **Phase 9.6 Reported Hash:** `a93e9561add3b86c064642d0fc6b9dc21222e6322ea91e03d233e76060bfb8d3`
- **Phase 9.7 Reported Hash:** `f4a0960e60ef06d5669df55e648ad463ebbdcdff62381ec6d26e17dfaefc56dc`

This forensic audit traced the exact chronological lifecycle, byte-level mutations, filesystem timestamps, and process execution logs across all phases.

### Key Forensic Findings:
1. **The Discrepancy is Completely Explained:** The binary hash difference is localized strictly to SQLite's 4-byte internal header change counter (bytes 24–27: `file_change_counter`) and memory-mapped HNSW buffer synchronization.
2. **Identification of the Exact Mutating Event:** The mutation occurred on **2026-10-11 at 22:33:27** during Phase 9.7 (Task `task-2785`), when an interactive diagnostic command invoked `chromadb.PersistentClient(path="cyber_attribution_engine/data/chroma_db")` directly against the master directory to check collection count, rather than against an isolated snapshot.
3. **Canonical Data Invariance:** Zero rows were inserted, deleted, or modified. SQLite `PRAGMA integrity_check` returns `ok`. The canonical content hash remains **100% invariant** at `668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7`.
4. **Historical Continuity:** Hash `f4a0960e...` is not an alien or random hash; it is the exact binary hash generated when native ChromaDB connects to SQLite at change counter state 30 (previously documented as the post-query snapshot hash in Phase 9.6).

---

## 2. Chronological Chain of Custody Across Phases

| Phase & Timestamp | Event / Operation | Recorded Binary SHA-256 | SQLite Change Counter | Canonical Content Hash |
| :--- | :--- | :--- | :---: | :--- |
| **Phase 9 Baseline Freeze**<br>`2026-10-11T02:04:00` | Baseline preregistration freeze recorded in [`frozen_system_manifest.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_benchmark_preparation_20261011_020400/frozen_system_manifest.json). | `f1619bf2182fe2cdeef65be2e6785262b5e2e5e0f83a7bbdfa3f9cb67a0232a5` | Initial state | `668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7` |
| **Phase 9.4 Safety Check**<br>`2026-10-11T03:30:00` | First connection safety test documented in [`frozen_manifest_reconciliation.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_4_execution_safety/frozen_manifest_reconciliation.md). Identified that SQLite connection handshake updates change counter. | `1ddc579d0d8324cd11970189d5652acca303f5840ab7dd7a6ede53bfa4744e11` | Counter bumped | `668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7` |
| **Phase 9.6 Reconciliation**<br>`2026-10-11T22:18:00` | Option C design and baseline lock in [`snapshot_reconciliation_telemetry.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_6_runtime_reconciliation/snapshot_reconciliation_telemetry.json). Master locked at counter 29; snapshot after query became counter 30 (`f4a0960e...`). | `a93e9561add3b86c064642d0fc6b9dc21222e6322ea91e03d233e76060bfb8d3` | 29 | `668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7` |
| **Phase 9.7 Start**<br>`2026-10-11T22:30:00` | Independent audit suite [`run_phase9_7_audit.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_7_independent_approval/run_phase9_7_audit.py) (task-2716). Log confirms master read at `a93e9561...`. | `a93e9561add3b86c064642d0fc6b9dc21222e6322ea91e03d233e76060bfb8d3` | 29 | `668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7` |
| **Phase 9.7 Diagnostic Event**<br>`2026-10-11T22:33:27` | Direct diagnostic invocation (task-2785): `PersistentClient(master_dir)`. Opened SQLite connection on master, incrementing change counter 29 -> 30. | `f4a0960e60ef06d5669df55e648ad463ebbdcdff62381ec6d26e17dfaefc56dc` | 30 | `668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7` |
| **Phase 9.7 Inventory**<br>`2026-10-11T22:35:00` | Task-2805 generated [`full_persistence_inventory.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_7_independent_approval/full_persistence_inventory.json), reading the active master file (mtime `22:33:27`), recording `f4a0960e...`. | `f4a0960e60ef06d5669df55e648ad463ebbdcdff62381ec6d26e17dfaefc56dc` | 30 | `668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7` |
| **Phase 9.8 Re-Verification**<br>`2026-10-11T22:56:00` | Formal audit suite [`run_phase9_8_audit.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_8_evidence_reconciliation/run_phase9_8_audit.py) (task-2982). Verified master invariant, quiescent, and intact. | `f4a0960e60ef06d5669df55e648ad463ebbdcdff62381ec6d26e17dfaefc56dc` | 30 | `668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7` |

---

## 3. Byte-Level Forensic Analysis of the Transition

We conducted a byte-by-byte forensic analysis of `chroma.sqlite3`:
1. **File Size Invariance:** Exactly $294{,}912$ bytes across all states.
2. **SQLite Header Byte Offset 24–27:**
   - At state `a93e9561...`: Bytes 24–27 = `0x00 0x00 0x00 0x1D` (Integer value 29).
   - At state `f4a0960e...`: Bytes 24–27 = `0x00 0x00 0x00 0x1E` (Integer value 30).
3. **Database Table Verification:**
   - Table `collections`: 1 row (Collection ID: `cd6345d4-cc6a-4d4d-b527-5a34fd4de2ee`, Name: `cti_threat_reports`, Dimension: 384, Space: `cosine`).
   - Table `embeddings`: 7 rows (7 canonical CTI reports).
   - Table `embedding_metadata`: 49 rows (7 metadata fields $\times$ 7 reports).
   - Table `embeddings_queue`: 7 rows.
   - Table `segments`: 2 rows (HNSW segment `3962f896-273d-4039-b97e-d0aa4e6d29ed` + SQLite metadata segment).
4. **HNSW Segment Directory Synchronization:**
   - Along with the SQLite change counter, opening `PersistentClient` on master triggered hnswlib to synchronize its internal header and length buffers:
     - `header.bin`: `a0e81c3b22454233bc12d0762f06dcca48261a75231cf87c79b75e69a6c00150` (100 bytes - invariant)
     - `link_lists.bin`: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (0 bytes - invariant)
     - `length.bin`: `a2cab3b7fffef0b5e24cb03aaf91e69be401e590bbff1c192c3d12be61d46f06` (400 bytes)
     - `data_level0.bin`: `dd3bc35aff31318f10dab2111ad835e55926233f1e0e8922cdc30bc92ce171f8` (167,600 bytes)

---

## 4. Governance Conclusion: Authoritative Master Baseline for Protocol Amendment 3

The transition from `a93e9561...` to `f4a0960e...` is conclusively explained by an un-isolated diagnostic command (task-2785) executed during Phase 9.7 auditing. No content, graph edges, neural weights, or documents were altered.

To ensure unambiguous, auditable compliance:
- **Authoritative Approved Master Hash:** The official master SQLite hash for ratification in Protocol Amendment 3 is formally locked as:
  $$\mathbf{H}_{\text{master}} = \texttt{f4a0960e60ef06d5669df55e648ad463ebbdcdff62381ec6d26e17dfaefc56dc}$$
- **Canonical Content Hash:** Formally locked as:
  $$\mathbf{H}_{\text{content}} = \texttt{668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7}$$
- **Lesson for Phase 10 Harness:** This incident empirically confirms why Option C is indispensable: **any direct invocation of `chromadb.PersistentClient` on a persistent directory mutates SQLite and HNSW headers.** Phase 10 MUST instantiate `ThreatRAGEngine` exclusively within an ephemeral snapshot directory, protecting the authoritative master from direct connections.
