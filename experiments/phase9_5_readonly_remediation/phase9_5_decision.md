# NexusCTI Phase 9.5 — Final Remediation Decision

**Document Version:** 1.0 (Formal Engineering & Governance Gate)  
**Date:** 2026-10-11  
**Project Root:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI`  
**Experiment Root:** `experiments/phase9_5_readonly_remediation/`  
**Mandated Output Decision:** Exactly one of:
- `REMEDIATION VALIDATED — READY FOR PROTOCOL RECONCILIATION`
- `NOT READY — REMEDIATION REQUIRED`

---

## 1. Executive Summary & Audit Background

Phase 9.4 halted Phase 10 evaluation because `chromadb.PersistentClient` unconditionally attempts SQLite writes during startup (migration table inspection and transaction locking), crashing with `InternalError: (code: 8) attempt to write a readonly database` when filesystem write access is denied.

Phase 9.5 was chartered to design and validate the safest remediation without running prospective test cases, accessing ground-truth labels, or modifying the frozen model.

---

## 2. Remediation Design & Technical Findings

Four technical options were comprehensively evaluated and empirically tested on scratch copies:

1. **Option A (Native ChromaDB Read-Only):** **UNVIABLE**. Auditing of ChromaDB version `1.5.9` confirmed that native read-only persistent querying does not exist. `PerThreadPool` unconditionally opens SQLite in read-write mode and fails when the filesystem enforces read-only permissions.
2. **Option B (Custom Read-Only Query Adapter - `ReadOnlyChromaAdapter`):** **VALIDATED**. Bypasses ChromaDB's migration engine, connects via native SQLite URI `?mode=ro`, loads frozen embeddings/documents from `embeddings_queue`, computes cosine similarity via NumPy dot-products, guarantees 0 header mutations, and functions successfully under strict OS write protection (`chmod 0o444`).
3. **Option C (Immutable Snapshot + Ephemeral Runner):** **VALIDATED**. Keeps the golden master database write-protected on disk, while instantiating an ephemeral verified scratch replica for inference. Preserves 100% bit-for-bit equivalence with the original frozen runtime while isolating the golden database from accidental corruption.
4. **Option D (Formal Protocol Definition Amendment):** **VALIDATED AS ESSENTIAL GOVERNANCE BRIDGE**. Formally defines immutability as invariance of the canonical SQLite content hash (`668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7`) rather than raw binary SQLite file hash, distinguishing benign internal SQLite bookkeeping from substantive data corruption.

---

## 3. Strict Verification of Hard Constraints

| Protocol Constraint | Verification Status | Evidence / Audit Trail |
| :--- | :---: | :--- |
| **Phase 10 Not Executed** | **CONFIRMED** | Phase 10 evaluation runner was neither authorized nor executed. |
| **Prospective Labels Untouched** | **CONFIRMED** | Zero prospective benchmark files, test narratives, or ground-truth labels (100 Task A + 30 Task B) were accessed or read. |
| **Original Database Untouched** | **CONFIRMED** | `cyber_attribution_engine/data/chroma_db/chroma.sqlite3` canonical content hash remained strictly invariant: `668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7`. All empirical tests were restricted to `experiments/phase9_5_readonly_remediation/scratch/`. |
| **Frozen Models Unaltered** | **CONFIRMED** | Model weights, graph semantics, retrieval ranking formulas, fusion layer weights, and decision thresholds were preserved without modification. |
| **Audit Trail Preserved** | **CONFIRMED** | Cryptographic hash manifest recorded in [artifact_change_manifest.json](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_5_readonly_remediation/artifact_change_manifest.json). |

---

## 4. Protocol Reconciliation Requirement

In accordance with protocol governance (*"Do not describe a modified runtime as identical to the original frozen runtime"*):
- If the project selects **Option B** (`ReadOnlyChromaAdapter`), the runtime code differs from the original frozen runtime. While mathematically equivalent on distinct similarity scores, minor tie-breaking variance exists in rare edge cases (as documented in [runtime_equivalence_report.md](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_5_readonly_remediation/runtime_equivalence_report.md)). A formal protocol amendment must be registered before testing.
- If the project selects **Option C** (Ephemeral Scratch Inference) + **Option D** (Logical Content Immutability), the original frozen runtime executes without code changes, but the protocol must formally recognize the logical content hash criterion.

Neither remediation may be retroactively applied without a formal protocol reconciliation gate.

---

## 5. Final Formal Decision

In accordance with the criteria of Phase 9.5:
1. Technical options for read-only remediation have been thoroughly audited and documented.
2. The custom read-only adapter has been empirically validated on write-protected scratch data with 0 byte mutations.
3. The runtime equivalence and edge-case discrepancies have been fully investigated and documented.
4. Prospective test labels and frozen model weights remain 100% untouched.

Therefore, the formal status of Phase 9.5 is:

### **REMEDIATION VALIDATED — READY FOR PROTOCOL RECONCILIATION**

*(Note: Phase 10 blind evaluation remains strictly unauthorized pending formal protocol reconciliation).*
