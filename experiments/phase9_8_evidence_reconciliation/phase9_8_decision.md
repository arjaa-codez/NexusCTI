# NexusCTI Phase 9.8 — Independent Gate Decision Report

**Phase:** Phase 9.8 — Master Hash Chain of Custody and Snapshot Consistency Gate  
**Timestamp:** 2026-10-11T23:08:00+05:30  
**Project Root:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI`  
**Governing Authority:** NexusCTI Independent Audit and Protocol Approval Board  

---

## 1. Official Gate Decision

### **DECISION: READY FOR FORMAL PROTOCOL APPROVAL**

> **CRITICAL GOVERNANCE DECLARATION:**  
> **"READY FOR FORMAL PROTOCOL APPROVAL"** certifies that the master hash discrepancy between Phase 9.6 and Phase 9.7 has been forensically traced, explained, and reconciled; snapshot consistency and fail-closed guards have been verified; and retrieval equivalence through the active `ThreatRAGEngine` retrieval path has been reproduced on all approved development fixtures.  
>  
> **THIS DECISION DOES NOT CONSTITUTE FORMAL PROTOCOL APPROVAL ITSELF, NOR DOES IT AUTHORIZE PHASE 10 EXECUTION.**  
> **Phase 10 evaluation remains strictly UNAUTHORIZED until Protocol Amendment 3 is officially ratified by the designated authority and all pre-execution authorization gates are satisfied.**

---

## 2. Gate Verification Summary

| Audit Item | Governing Standard | Forensic / Empirical Finding | Status | Supporting Artifact |
| :--- | :--- | :--- | :---: | :--- |
| **1. Master Hash Reconciliation** | Identify exact transition cause between `a93e9561...` and `f4a0960e...`. Verify canonical content and SQLite integrity. | The transition was traced to an un-isolated diagnostic command (task-2785, `2026-10-11 22:33:27`) which opened `PersistentClient(master_dir)`, bumping change counter from 29 to 30. Zero data rows modified. Content hash invariant at `668d0776...`. | **PASSED** | [`master_hash_chain_of_custody.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_8_evidence_reconciliation/master_hash_chain_of_custody.md) |
| **2. Snapshot Consistency & Quiescence** | Prove master quiescence; verify atomic directory clone; enforce fail-closed guards; eliminate fallback. | Pre-copy quiescence assertion verified (0 WAL/SHM sidecars). Recursive copy (`copytree`) verified. 6-point fail-closed validation verified. | **PASSED** | [`snapshot_consistency_review.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_8_evidence_reconciliation/snapshot_consistency_review.md) |
| **3. Deterministic Teardown Protocol** | Ensure ephemeral snapshot is completely destroyed on Windows without handle locking errors (`WinError 32`). | Incorporating `SharedSystemClient.clear_system_cache()` along with `gc.collect()` clears all cached ChromaDB handles, achieving clean directory deletion. | **PASSED** | [`snapshot_consistency_review.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_8_evidence_reconciliation/snapshot_consistency_review.md) |
| **4. Retrieval Equivalence on Active Path** | Reproduce T1–T10 comparisons on the authentic `ThreatRAGEngine.hybrid_search` path with unrounded distances and tie fidelity. | 10/10 rank matches, Top-1 actor matches, identical raw distances ($\Delta = 0.0$), identical tie resolution. Categorized without overstating general equivalence. | **PASSED** | [`retrieval_equivalence_reproduction.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_8_evidence_reconciliation/retrieval_equivalence_reproduction.md) |
| **5. Complete Directory Manifest** | Document complete manifest for ratification in Protocol Amendment 3. | Cataloged all 5 files in `cyber_attribution_engine/data/chroma_db/` with exact byte sizes and SHA-256 hashes. | **PASSED** | [`phase9_8_artifact_manifest.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_8_evidence_reconciliation/phase9_8_artifact_manifest.json) |

---

## 3. Specifications for Formal Ratification of Protocol Amendment 3

For the protocol amendment to be formally ratified, the approving authority must reference the exact reconciled parameters established in this audit:

### 3.1 Authoritative Master Store Directory Manifest
- **Master Directory:** `cyber_attribution_engine/data/chroma_db/`
- **File Manifest:**
  1. `chroma.sqlite3`: 294,912 bytes | SHA-256: `f4a0960e60ef06d5669df55e648ad463ebbdcdff62381ec6d26e17dfaefc56dc`
  2. `3962f896-273d-4039-b97e-d0aa4e6d29ed/header.bin`: 100 bytes | SHA-256: `a0e81c3b22454233bc12d0762f06dcca48261a75231cf87c79b75e69a6c00150`
  3. `3962f896-273d-4039-b97e-d0aa4e6d29ed/link_lists.bin`: 0 bytes | SHA-256: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
  4. `3962f896-273d-4039-b97e-d0aa4e6d29ed/length.bin`: 400 bytes | SHA-256: `a2cab3b7fffef0b5e24cb03aaf91e69be401e590bbff1c192c3d12be61d46f06`
  5. `3962f896-273d-4039-b97e-d0aa4e6d29ed/data_level0.bin`: 167,600 bytes | SHA-256: `dd3bc35aff31318f10dab2111ad835e55926233f1e0e8922cdc30bc92ce171f8`
- **Canonical Content Hash:** `668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7`
- **SQLite Change Counter:** `30`

### 3.2 Approved Snapshot Lifecycle Protocol
1. **Pre-Snapshot Quiescence Assert:** Assert zero `*-wal`, `*-shm`, or `*-journal` files in master directory.
2. **Pre-Copy Master Check:** Compute master directory manifest and assert exact match with Section 3.1.
3. **Atomic Clone:** Execute `shutil.copytree(master_dir, snapshot_dir)`.
4. **Snapshot Pre-Flight Verification:** Run 6-point check (completeness, hash parity, SQLite integrity, content hash, collection count = 7).
5. **Isolated Blind Inference:** Execute Phase 10 prospective evaluation passing exclusively `persist_directory=snapshot_dir`.
6. **Teardown & Handle Clearance:** Invoke `SharedSystemClient.clear_system_cache(); gc.collect(); shutil.rmtree(snapshot_dir)`.
7. **Post-Evaluation Master Invariance Re-Check:** Recompute master directory manifest; assert delta = 0.

---

## 4. Unresolved Risks and Safeguards

1. **Risk of Ad-Hoc Direct Connections:** As demonstrated by the Phase 9.7 diagnostic command (task-2785), invoking `chromadb.PersistentClient` directly on `master_dir` modifies header bytes.
   - *Mandatory Safeguard:* The Phase 10 execution runner must reject any path pointing directly to the master directory and mandate execution against a verified snapshot.
2. **Risk of Prospective Label Leakage:** Pre-evaluation runners must not load, parse, or display files in `cyber_attribution_engine/data/raw_reports/prospective_test/` or any ground-truth label map until all predictions have been written and sealed on disk.

---

## 5. Governance Authority and Next Actions

- **Responsible Authority:** Principal Investigator / NexusCTI Evaluation Governance Committee.
- **Action Required:**
  1. Review the Phase 9.8 evidence package in [`experiments/phase9_8_evidence_reconciliation/`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_8_evidence_reconciliation/).
  2. Formally ratify **Protocol Amendment 3** incorporating the authoritative manifest and 7-step snapshot lifecycle.
  3. Release **NexusCTI Evaluation Protocol v2.2-amended**.
- **Phase 10 Execution Status:** **UNAUTHORIZED.** Phase 10 cannot proceed until formal ratification is completed.
