# NexusCTI Phase 9.6 — Final Runtime Selection & Reconciliation Decision

**Document Version:** 1.0 (Formal Engineering & Governance Decision Gate)  
**Date:** 2026-10-11  
**Project Root:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI`  
**Experiment Root:** `experiments/phase9_6_runtime_reconciliation/`  
**Target Evaluation:** Phase 10 Independent Blind Evaluation  
**Mandated Output Decision Token:** Exactly one of:
- `READY FOR FORMAL PROTOCOL APPROVAL`
- `NOT READY — REMEDIATION REQUIRED`

---

## 1. Executive Summary & Gate Status

Phase 9.5 demonstrated that the native ChromaDB persistent client cannot query under filesystem write denial (`chmod 0o444`), while the custom read-only adapter prototype exhibited a tied-rank discrepancy at Rank 3 for boundary cases. Phase 10 remained unauthorized.

Phase 9.6 was charged with making a prospective, documented decision regarding the inference runtime without executing the blind evaluation, accessing ground-truth labels, or altering frozen models.

---

## 2. Technical Findings & Architectural Determination

### 2.1 Runtime Architecture Selection
**Option C (Disposable Runtime Snapshot Architecture)** is formally selected as the primary runtime architecture for NexusCTI Phase 10:
1. **Zero Code Changes:** Preserves the unmodified frozen `ThreatRAGEngine` and native ChromaDB client implementation.
2. **Native Index Traversal:** Preserves the native compiled C++ HNSW vector index (`urn:chroma:segment/vector/hnsw-local-persisted`), avoiding linear-scan approximations.
3. **Master Database Protection:** The authoritative frozen master database (`cyber_attribution_engine/data/chroma_db/chroma.sqlite3`) remains write-protected on disk, experiencing **0 bytes modified** and **change counter delta = 0** across all trials.
4. **Disposable Lifecycle:** Ephemeral runtime replicas are instantiated in isolated temporary directories, audited, and destroyed immediately following inference.

### 2.2 Native Snapshot Reproducibility & Determinism
Empirical auditing on development fixtures proved:
- **Intra-Session Determinism (Trial 1 vs Trial 2):** **100% BIT-IDENTICAL**.
- **Cross-Creation Reproducibility (Fresh Snapshot vs Trial 1):** **100% BIT-IDENTICAL**.
- **Sidecar Cleanliness:** Zero lingering `-journal` or `-wal` sidecar files remaining post-run.
- **Canonical Content Invariance:** Content hash `668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7` strictly preserved.

### 2.3 Fair Adapter Comparison & Tie Discrepancy Resolution
- Forensic analysis revealed that Phase 9.5's adapter discrepancy was caused by sorting documents *after* rounding similarity scores to 4 decimal places.
- When refined to sort by raw unrounded float32 dot-products (matching ChromaDB's internal sorting pipeline), the adapter achieved **100% full rank and score equivalence** across all 10 development queries, resolving both the 5-way zero-similarity tie (T8) and the punctuation-noise query (T10).
- Option C is nonetheless preferred over Option B because Option C avoids modifying frozen source code and preserves authentic compiled HNSW graph traversal semantics.

---

## 3. Protocol Reconciliation Status

Technical auditing revealed that Phase 9.3 Section 3.1 contained an unworkable clause requiring ChromaDB to connect with `?mode=ro`. 

In response, **Protocol Amendment Proposal 3** has been formally prepared in [protocol_amendment_proposal.md](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_6_runtime_reconciliation/protocol_amendment_proposal.md):
- It replaces the unviable active write-denial clause with the auditable **Disposable Snapshot Lifecycle Architecture**.
- It establishes the master database as the authoritative frozen artifact and permits SQLite bookkeeping increments on ephemeral snapshots only.
- It preserves all primary and secondary statistical endpoints, test hypotheses, $\alpha = 0.05$, decision thresholds, and locked scoring rules without modification.

---

## 4. Hard Constraints Verification

| Protocol Constraint | Verification Status | Audit Evidence |
| :--- | :---: | :--- |
| **Phase 10 Not Executed** | **CONFIRMED** | Blind evaluation was neither authorized nor run. |
| **Prospective Labels Untouched** | **CONFIRMED** | 100 Task A + 30 Task B test cases and labels remain strictly unaccessed. |
| **Master Database Untouched** | **CONFIRMED** | Binary SHA-256 (`a93e9561...`) and content hash (`668d0776...`) 100% invariant. |
| **Frozen Models Unaltered** | **CONFIRMED** | GNN weights (`rgcn_weights.pt`), graph schema, and fusion weights preserved. |
| **Cryptographic Audit Trail** | **CONFIRMED** | Complete manifest in [frozen_master_and_snapshot_manifest.json](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_6_runtime_reconciliation/frozen_master_and_snapshot_manifest.json). |

---

## 5. Final Formal Decision

All technical investigations, empirical snapshot validations, adapter forensic analyses, and protocol reconciliation documents are complete and verified. 

The formal decision for Phase 9.6 is:

### **READY FOR FORMAL PROTOCOL APPROVAL**

*(Note: In accordance with the Phase 9.6 specification, readiness denotes that the proposal and technical evidence are prepared for review—not that the amendment has already been approved. Phase 10 blind evaluation remains strictly unauthorized).*
