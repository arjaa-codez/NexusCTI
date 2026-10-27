# NexusCTI Phase 9.7 — Independent Gate Decision Report

**Phase:** Phase 9.7 — Independent Runtime and Protocol Approval Gate  
**Timestamp:** 2026-10-11T22:40:00+05:30  
**Project Root:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI`  
**Governing Authority:** NexusCTI Independent Audit and Protocol Approval Board  

---

## 1. Official Gate Decision

### **DECISION: READY FOR FORMAL PROTOCOL APPROVAL**

> **IMPORTANT GOVERNANCE NOTICE:**  
> **"READY FOR FORMAL PROTOCOL APPROVAL"** certifies that Option C (the Disposable Native ChromaDB Runtime Snapshot architecture) and Protocol Amendment Proposal 3 are completely specified, technically verified, and supported by conclusive cryptographic and empirical evidence.  
>  
> **THIS DECISION DOES NOT CONSTITUTE PROTOCOL APPROVAL ITSELF, NOR DOES IT AUTHORIZE PHASE 10 EXECUTION.**  
> **Phase 10 evaluation remains strictly UNAUTHORIZED until the formal protocol amendment is officially signed and all pre-execution authorization gates are satisfied.**

---

## 2. Gate Verification Summary

Each of the mandatory audit gates has been evaluated with rigorous independent inspection, recomputed cryptographic hashes, and empirical telemetry.

| Audit Gate | Scope & Criteria | Empirical Finding | Status | Supporting Artifact |
| :--- | :--- | :--- | :---: | :--- |
| **Gate 1: Complete Persistence Store Inventory** | Verify all files in `cyber_attribution_engine/data/chroma_db/`, including SQLite DB and HNSW index segments. Verify atomic directory clone. | Master contains 5 files (SQLite + 4 HNSW segment binary files). Full recursive clone via `shutil.copytree` verified. | **PASSED** | [`full_persistence_inventory.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_7_independent_approval/full_persistence_inventory.json) |
| **Gate 2: Master Directory Isolation** | Master store remains 100% bitwise invariant before, during, and after query workloads. Process binding isolated to snapshot. | Master SHA-256 hashes 100% identical across all 5 files. Zero bytes modified. Change counter delta = 0. Zero active sidecars. | **PASSED** | [`master_isolation_audit.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_7_independent_approval/master_isolation_audit.md) |
| **Gate 3: Snapshot Creation & Teardown Protocol** | Safe creation without dirty reads, clear mutation boundaries, deterministic Windows file handle release (`gc.collect`). | Quiescent master verified (no WAL/SHM). Snapshot mutations isolated to temp directory. Windows `WinError 32` lock avoided via GC. | **PASSED** | [`snapshot_creation_and_cleanup_audit.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_7_independent_approval/snapshot_creation_and_cleanup_audit.md) |
| **Gate 4: Retrieval Equivalence Reproduction** | Native snapshot matches frozen baseline across development queries T1–T10 on candidate IDs, raw distances, scores, ties, edge cases. | 100% rank match, Top-1 actor match, identical raw distances ($\Delta = 0.0$), identical tie resolution, multi-trial determinism. | **PASSED** | [`retrieval_equivalence_reproduction.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_7_independent_approval/retrieval_equivalence_reproduction.md) |
| **Gate 5: Protocol Amendment 3 Completeness** | Amendment explicitly specifies master immutability, snapshot lifecycle, fail-closed guards, unchanged primary endpoints. | Amendment Proposal 3 reviewed line-by-line; replaces unexecutable `?mode=ro` clause while preserving all statistical endpoints. | **PASSED** | [`protocol_amendment_review.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_7_independent_approval/protocol_amendment_review.md) |
| **Gate 6: Evidence Hash Reconciliation** | Recompute hashes of all Phase 9.6 telemetry, reports, and manifests. Resolve any discrepancies. | All 8 Phase 9.6 artifacts independently hashed and cataloged with zero unrecorded drift. | **PASSED** | [`artifact_hash_reconciliation.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_7_independent_approval/artifact_hash_reconciliation.json) |

---

## 3. Cryptographic and Technical Evidence Base

### 3.1 Master Store Cryptographic Hashes (Invariance Verified)
- `chroma.sqlite3`: `f4a0960e60ef06d5669df55e648ad463ebbdcdff62381ec6d26e17dfaefc56dc` (294,912 bytes)
- `3962f896-.../data_level0.bin`: `dd3bc35aff31318f10dab2111ad835e55926233f1e0e8922cdc30bc92ce171f8` (167,600 bytes)
- `3962f896-.../header.bin`: `a0e81c3b22454233bc12d0762f06dcca48261a75231cf87c79b75e69a6c00150` (100 bytes)
- `3962f896-.../length.bin`: `a2cab3b7fffef0b5e24cb03aaf91e69be401e590bbff1c192c3d12be61d46f06` (400 bytes)
- `3962f896-.../link_lists.bin`: `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (0 bytes)
- **Canonical Content Hash:** `668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7` (7 CTI reports)

### 3.2 Key Empirical Findings
1. **Dual-Engine Store:** ChromaDB v0.5.5 relies fundamentally on both `chroma.sqlite3` and the external HNSW segment directory `3962f896-273d-4039-b97e-d0aa4e6d29ed/`. Single-file snapshots are defective. Option C's `shutil.copytree` captures the complete store.
2. **Native Index Buffering:** When native ChromaDB queries an index, its C++ binding updates internal memory-mapped buffers (`data_level0.bin`, `length.bin`) and SQLite increments its header change counter. Because these mutations are intrinsic to native query execution, running against a physically write-denied directory is impossible. Confining these operations to a disposable ephemeral snapshot eliminates write contamination while preserving exact retrieval behavior.
3. **Retrieval Parity:** Option C eliminates the tied-rank discrepancy observed in the custom SQL adapter (Option B), delivering 100% full-rank agreement with the baseline across all test fixtures.

---

## 4. Residual Risks and Recommended Mitigations

1. **Risk: Windows OS Handle Contention (`WinError 32`)**  
   - *Description:* On Windows, compiled C++ extensions (`hnswlib.pyd`) can hold open file handles after queries finish, causing `shutil.rmtree()` to fail during cleanup.
   - *Mitigation:* The Phase 10 evaluation harness must explicitly execute:
     ```python
     del rag_engine.collection
     del rag_engine.client
     del rag_engine
     import gc
     gc.collect()
     ```
     before calling `shutil.rmtree(snapshot_dir)`.

2. **Risk: Partial or Interrupted Snapshots**  
   - *Description:* A crash or out-of-disk condition during snapshot creation could yield an incomplete index.
   - *Mitigation:* The harness must verify post-copy file counts, segment existence, and hash parity before initializing inference.

3. **Risk: Accidental Unblinding**  
   - *Description:* Prematurely loading test labels during preflight setup.
   - *Mitigation:* Prospective test label files remain strictly isolated and must only be unblinded after prospective predictions are written to disk and hashed.

---

## 5. Responsibility for Formal Protocol Approval and Next Steps

- **Responsible Entity:** Project Principal Investigator / NexusCTI Evaluation Governance Committee.
- **Action Required for Phase 10 Authorization:**
  1. Review the Phase 9.7 audit package (`experiments/phase9_7_independent_approval/`).
  2. Formally countersign and ratify **Protocol Amendment 3**, releasing **NexusCTI Protocol v2.2-amended**.
  3. Authorize the Phase 10 execution runner to proceed under the ratified 6-step snapshot lifecycle.

---

## 6. Phase 10 Status Declaration

```
========================================================================================
                          NEXUSCTI GOVERNANCE GATE STATUS
========================================================================================
 Phase 9.7 Audit Status       : PASSED (All 6 gates verified)
 Option C Specification       : SUFFICIENT & CONCLUSIVELY EVIDENCED
 Gate Decision                : READY FOR FORMAL PROTOCOL APPROVAL
 Protocol Amendment Status    : PENDING FORMAL RATIFICATION (v2.2-amended)
 Prospective Test Data        : UNTOUCHED & BLINDED (100 Task A + 30 Task B)
 Phase 10 Execution Status    : UNAUTHORIZED
========================================================================================
```
