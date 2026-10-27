# Phase 9.7 — Protocol Amendment Review Report

**Audit Phase:** NexusCTI Phase 9.7 — Independent Runtime and Protocol Approval Gate  
**Timestamp:** 2026-10-11T22:38:00+05:30  
**Document Reviewed:** Phase 9.6 Protocol Amendment Proposal 3 (`experiments/phase9_6_runtime_reconciliation/protocol_amendment_proposal.md`)  
**Base Protocol:** Phase 9.3 Final Protocol (`experiments/phase9_3_final_authorization_20261011/phase9_3_final_protocol.md`)  
**Review Status:** **READY FOR FORMAL PROTOCOL APPROVAL (Pending Official Ratification)**  

---

## 1. Executive Summary

Task 4 of Phase 9.7 requires a formal line-by-line review comparing **Protocol Amendment Proposal 3** against the frozen **Phase 9.3 Evaluation Protocol**.

The review establishes that:
1. **Scientific Integrity Preserved:** The amendment makes zero changes to the hypothesis, the 100-case closed-set prospective test cohort, the 30-case open-set cohort, the primary endpoint (paired Top-3 accuracy), the primary statistical test (exact two-sided McNemar test at $\alpha = 0.05$), the directional success rule ($\Delta > 0$), or the confidence interval methodology (Wilson-score paired risk difference).
2. **Technical Conflict Reconciled:** The amendment correctly replaces an unexecutable runtime clause (`?mode=ro` SQLite URI parameter, which ChromaDB v0.5.5 / 1.5.9 does not pass or support) with an executable, mathematically isolated **Disposable Snapshot Lifecycle Architecture (Option C)**.
3. **Explicit Specification of Store & Segments:** The review notes that while Proposal 3 specifies the master directory, the amendment language must formally enumerate the HNSW segment directory (`3962f896-273d-4039-b97e-d0aa4e6d29ed/`) alongside `chroma.sqlite3` as an indivisible component of a valid persistent snapshot.
4. **Governance Boundary Maintained:** The amendment is classified as **Proposed and Verified**. It is NOT marked as approved; formal ratification by the designated protocol authority is required before Phase 10 execution can be authorized.

---

## 2. Point-by-Point Protocol Requirement Comparison

| Protocol Dimension | Phase 9.3 Locked Protocol | Amendment Proposal 3 | Audit Assessment & Finding |
| :--- | :--- | :--- | :--- |
| **Primary Evaluation Endpoint** | Paired Top-3 Accuracy (Full Hybrid vs Retrieval-Only) on 100 closed-set cases | Paired Top-3 Accuracy (Full Hybrid vs Retrieval-Only) on 100 closed-set cases | **UNCHANGED** |
| **Statistical Test** | Exact two-sided McNemar test on discordant pairs ($b$ vs $c$) | Exact two-sided McNemar test on discordant pairs ($b$ vs $c$) | **UNCHANGED** |
| **Significance Level ($\alpha$)** | $\alpha = 0.05$ | $\alpha = 0.05$ | **UNCHANGED** |
| **Directional Condition** | Observed paired risk difference $\Delta = (b - c)/N > 0$ | Observed paired risk difference $\Delta = (b - c)/N > 0$ | **UNCHANGED** |
| **Confidence Interval Method** | Wilson-score paired difference interval for marginal risk | Wilson-score paired difference interval for marginal risk | **UNCHANGED** |
| **Planning MDE** | $+15\%$ planning target; not a hard exclusion gate | $+15\%$ planning target; not a hard exclusion gate | **UNCHANGED** |
| **Model Weights & Graph** | Frozen GNN weights, schema, and dense encoder | Frozen GNN weights, schema, and dense encoder | **UNCHANGED** |
| **Retriever Fusion & Top-$k$** | Fusion weights $\alpha=0.6, \beta=0.4$; top-$k=3$ | Fusion weights $\alpha=0.6, \beta=0.4$; top-$k=3$ | **UNCHANGED** |
| **Database Connection Mode** | Mandated `?mode=ro` URI flag on active connection | **REPLACED:** 6-Step Disposable Snapshot Lifecycle (Option C) | **MODIFIED (Remediated unexecutable clause)** |
| **Master Store Invariance** | Master must remain unchanged | Master binary SHA-256 and content hash verified pre/post | **STRENGTHENED (Cryptographically enforced)** |

---

## 3. Deep-Dive: Changes Introduced by Amendment Proposal 3

The only operational requirements modified are those governing the runtime persistence layer:

### 3.1 Replacement of Unexecutable `?mode=ro` Mandate
- **Original Phase 9.3 Clause:** Section 3.1 stated: *"The prospective evaluation runner must connect to ChromaDB exclusively using the ?mode=ro URI flag."*
- **Technical Barrier Discovered in Phase 9.4/9.5:** ChromaDB v0.5.5 initializes its SQLite connection via `sqlite3.connect(database_path)` where `database_path` is a plain filesystem path string, ignoring SQLite URI flags. When write access is stripped via OS permissions (`chmod 0o444`), ChromaDB crashes on startup with SQLite error code 8 (`readonly_db`).
- **Remediation in Amendment 3:** The runner connects to an ephemeral snapshot directory instantiated in a scratch space (`experiments/.../scratch/`), preserving native ChromaDB compatibility while guaranteeing 100% read-only isolation of the authoritative master store.

### 3.2 Definition of Authoritative Frozen Master Artifacts
Amendment Proposal 3 explicitly records:
- **Authoritative Database:** `cyber_attribution_engine/data/chroma_db/chroma.sqlite3`
- **Segment Subdirectory:** `cyber_attribution_engine/data/chroma_db/3962f896-273d-4039-b97e-d0aa4e6d29ed/`
- **Pre-Evaluation Binary Hash:** `f4a0960e60ef06d5669df55e648ad463ebbdcdff62381ec6d26e17dfaefc56dc`
- **Canonical Content Hash:** `668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7`
- **Master Files Invariance Rule:** Post-evaluation master manifest must be 100% bitwise identical to pre-evaluation manifest. Any modification of the master invalidates the study.

### 3.3 Definition of Permitted vs. Prohibited Mutations
To eliminate ambiguity regarding internal SQLite metadata changes:
- **Permitted (Disposable Snapshot Only):**
  - Increments to the 4-byte SQLite header change counter (bytes 24–27).
  - Memory-mapped index buffer synchronization in `length.bin` and `data_level0.bin`.
  - Ephemeral creation and automatic deletion of SQLite rollback journal or WAL files.
- **Strictly Prohibited (All Environments):**
  - Any insertion, modification, or deletion of rows in `collections`, `embeddings`, `embedding_metadata`, or `embeddings_queue`.
  - Any alteration of canonical report content or embedding vectors.
  - Any copy, sync, or write-back from the ephemeral snapshot to the master database.

### 3.4 Six-Step Mandatory Execution Lifecycle
The amendment mandates the following sequence in the Phase 10 execution harness:
1. **Pre-Evaluation Master Integrity Audit:** Verify all 5 master files against locked SHA-256 hashes and verify zero active `-wal`/`-shm` sidecars.
2. **Atomic Snapshot Instantiation:** Perform recursive clone using `shutil.copytree()` into an isolated scratch directory.
3. **Pre-Inference Snapshot Parity Check:** Verify all cloned snapshot files match master hashes bit-for-bit.
4. **Blind Prospective Inference:** Execute evaluation runner exclusively passing `persist_directory=snapshot_dir`.
5. **Deterministic Teardown:** Invoke `del rag_engine; gc.collect(); shutil.rmtree(snapshot_dir)`.
6. **Post-Evaluation Master Integrity Audit:** Re-compute master hashes; assert delta $= 0$.

---

## 4. Evaluation of Failure Modes and Audit Logging

Amendment Proposal 3 specifies strict fail-closed requirements:
- **Snapshot Creation Failure:** Aborts evaluation before loading prospective test data.
- **Master Mutation Detection:** If any file in `cyber_attribution_engine/data/chroma_db/` exhibits a modified hash, evaluation is immediately flagged as **COMPROMISED AND INVALID**.
- **Audit Logging:** Every stage of the 6-step lifecycle must record structured JSON telemetry into the Phase 10 experiment directory.

---

## 5. Audit Recommendations for Formal Protocol Adoption

Before formal sign-off, the following clarifications should be incorporated into the final protocol ratification text:
1. **Explicit Segment Listing:** Explicitly enumerate the 4 HNSW binary files (`header.bin`, `length.bin`, `data_level0.bin`, `link_lists.bin`) alongside `chroma.sqlite3` in Section 3.1.
2. **Explicit Garbage Collection Mandate:** Mandate `import gc; gc.collect()` prior to `shutil.rmtree()` in the Phase 10 harness to prevent Windows `WinError 32` file lock collisions.
3. **Canonical Content Verification Script:** Mandate automated execution of `verify_canonical_content_hash.py` during Step 1 and Step 6.

---

## 6. Audit Verdict

| Review Criterion | Standard | Evaluation | Status |
| :--- | :--- | :--- | :---: |
| Primary Endpoint Invariance | Paired Top-3 Accuracy on 100 cases unchanged | Fully preserved | **VERIFIED** |
| Statistical Rigor | Exact McNemar test ($\alpha=0.05$) and Wilson CI preserved | Fully preserved | **VERIFIED** |
| Scope of Change | Limited strictly to runtime persistence lifecycle | Fully confined | **VERIFIED** |
| Master Protection | Cryptographic pre/post invariance gates enforced | Fully specified | **VERIFIED** |
| Fail-Closed Design | Immediate abort on failure before test unblinding | Fully enforced | **VERIFIED** |

**Conclusion:** Protocol Amendment Proposal 3 is mathematically sound, technically necessary, fully specified, and preserves the scientific integrity of the NexusCTI benchmark. It is **READY FOR FORMAL PROTOCOL APPROVAL**.
