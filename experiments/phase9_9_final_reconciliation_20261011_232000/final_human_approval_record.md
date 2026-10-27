# NexusCTI — Final Human Approval Record & Protocol Ratification
## Preregistered Evaluation Governance — Pre-Phase 10 Gate

**Document Status:** Pending Human Execution  
**Submission Date:** 2026-10-12  
**Project Root:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\cyber_attribution_engine`  
**Governing Authority:** NexusCTI Independent Evaluation Governance Committee & Principal Investigator  
**Reconciliation Reference:** [`experiments/phase9_9_final_reconciliation_20261011_232000/`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_9_final_reconciliation_20261011_232000/)  
**Targeted HNSW Evidence:** [`targeted_hnsw_verification_report.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_9_final_reconciliation_20261011_232000/targeted_hnsw_verification_report.md)  
**Governance Package Reference:** [`governance_signoff_package.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_9_final_reconciliation_20261011_232000/governance_signoff_package.md)  

---

> [!IMPORTANT]
> **GOVERNANCE DIRECTIVE: STRICT SEPARATION OF READINESS AND AUTHORIZATION**  
> All technical audits, integrity checks, and targeted forensic verifications (Phases 9.1–9.9) have **PASSED** with 100% verification.  
> However, **technical readiness does not constitute formal approval**.  
> **Phase 10 prospective blind evaluation remains strictly UNAUTHORIZED until the human Governance Authority executes the approval fields below.**

---

## 1. Executive Summary & Audit Completion Status

This Final Human Approval Record integrates the completed Phase 9.9 reconciliation findings, the final targeted HNSW forensic verification, and Protocol Amendment 3 into a single actionable record.

| Verification Dimension | Result | Direct Verification Evidence |
| :--- | :---: | :--- |
| **Relational B-Tree & Metadata** | **PASS** | SQLite `PRAGMA integrity_check` = `ok`. Canonical Content SHA-256 = `668d0776...` invariant. |
| **HNSW Structural Integrity** | **PASS** | 100-byte `header.bin` unpacked against `chromadb_rust_bindings.pyd`; `max_level_ = -1` explains 0-byte `link_lists.bin`. |
| **Disposable Snapshot Execution** | **PASS** | Ephemeral clone loaded by `PersistentClient`; 5 evaluation queries executed with exact counts ($N=7$). |
| **Master Immutability** | **PASS** | 5-file master manifest verified before and after test; net delta = **0 bytes**. |
| **Scientific Blinding** | **PASS** | 100 Task A and 30 Task B prospective cases remain quarantined and unscored. |
| **Statistical Freezing** | **PASS** | Exact two-sided McNemar test, directional rule, Agresti–Min (2005) CI, and planning MDE frozen. |

---

## 2. Authoritative Master Store Manifest

The authoritative master vector store is located at:
`C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\cyber_attribution_engine\data\chroma_db\`

Direct byte-level cryptographic hashing produced the following verified baseline:

| Relative File Path | File Size (Bytes) | Authoritative SHA-256 Digest (64 Hex Characters) | Role & Content Description |
| :--- | :---: | :--- | :--- |
| `chroma.sqlite3` | 294,912 | `f4a0960e60ef06d5669df55e648ad463ebbdcdff62381ec6d26e17dfaefc56dc` | Relational tables, collection definitions, metadata, and 7 queue embeddings. |
| `3962f896-.../data_level0.bin` | 167,600 | `dd3bc35aff31318f10dab2111ad835e55926233f1e0e8922cdc30bc92ce171f8` | Pre-allocated Level-0 graph memory ($100 \times 1,676$ bytes). |
| `3962f896-.../header.bin` | 100 | `a0e81c3b22454233bc12d0762f06dcca48261a75231cf87c79b75e69a6c00150` | Binary HNSW parameters ($M=16, M_0=32, m_L=0.36067, ef_c=100$). |
| `3962f896-.../length.bin` | 400 | `a2cab3b7fffef0b5e24cb03aaf91e69be401e590bbff1c192c3d12be61d46f06` | Pre-allocated node link length array ($100 \times 4$ bytes). |
| `3962f896-.../link_lists.bin` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | Skip-list layers $l \ge 1$ (0 bytes: structurally expected since `max_level_ = -1`). |

- **Canonical Content SHA-256:** `668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7` (**100% Invariant**)
- **SQLite Change Counter:** `30`
- **SQLite Integrity Status:** `PRAGMA integrity_check == 'ok'`

---

## 3. Mandatory Disposable Snapshot Lifecycle (Option C)

Direct initialization against the master store path is **strictly prohibited** during Phase 10 evaluation. All inference queries must follow the 7-step ephemeral snapshot lifecycle:

```text
Step 1: Check master directory quiescence (assert zero *-wal, *-shm, or *-journal files).
Step 2: Verify master directory against the 5-file manifest above (assert all 5 hashes match).
Step 3: Atomically clone master store via shutil.copytree() to isolated scratch space.
Step 4: Verify clone manifest matches master manifest bit-for-bit.
Step 5: Execute evaluation inference passing persist_directory=str(snapshot_dir).
Step 6: Release ChromaDB singleton cache via SharedSystemClient.clear_system_cache(), gc.collect(),
        and remove the ephemeral scratch directory.
Step 7: Re-verify master directory; assert net delta = 0 bytes modified.
```

---

## 4. Frozen Scientific Parameters and Statistical Decision Rules

All primary hypotheses, evaluation endpoints, statistical test criteria, and reporting conventions remain strictly frozen:

1. **Evaluation Cohorts:**
   - **Task A (Closed-Set Superiority):** $N = 100$ independent prospective threat campaigns.
   - **Task B (Open-Set Robustness):** $N = 30$ out-of-cohort novel threat campaigns.
2. **Primary Endpoint:**
   - Paired Top-3 Accuracy difference between Full Hybrid ($A$) and Retrieval-only ($B$) models on Task A.
3. **Primary Hypothesis Test:**
   - Exact two-sided McNemar test on discordant pairs ($b$: Hybrid success / Retrieval failure; $c$: Retrieval success / Hybrid failure):
     $$p = 2 \sum_{k=b}^{n_d} \binom{n_d}{k} (0.5)^{n_d} \quad \text{if } b > c, \quad \text{where } n_d = b + c$$
4. **Significance Level & Directional Decision Rule:**
   - Significance threshold: $\alpha = 0.05$ (two-sided).
   - Confirmatory superiority is achieved if and only if **both**:
     1. Exact two-sided McNemar test $p \le 0.05$.
     2. Observed paired risk difference $\hat{\Delta} = \frac{b - c}{N} > 0$.
5. **Prespecified Confidence Interval Method:**
   - 95% Agresti–Min (2005) pseudo-observation paired risk-difference interval:
     $$\tilde{\Delta} \pm 1.95996 \cdot \widetilde{\text{SE}}$$
     where $+1.0$ pseudo-observation is added to each discordant cell ($+2.0$ to total sample size):
     $$\tilde{\Delta} = \frac{(b + 1) - (c + 1)}{N + 2}, \qquad \widetilde{\text{SE}} = \frac{1}{N + 2}\sqrt{(b + 1) + (c + 1) - \frac{[(b + 1) - (c + 1)]^2}{N + 2}}$$
6. **Power Assumptions & Planning MDE:**
   - Evaluated at $N = 100$, discordant pair proportion $q = 0.25$, odds ratio $\theta = 4.0$, achieving **$83.674\%$ statistical power**.
   - The $+15.0\%$ percentage point target is the prespecified planning Minimal Detectable Effect (MDE) for sample size calibration, **not** an additional observed sample point-estimate gating threshold.

---

## 5. Disclosed Deviations, Limitations, and Residual Risks

1. **DEV-01 (Change Counter Increment 29 $\to$ 30):** An interactive diagnostic command on `2026-10-11 22:33:27` initialized `PersistentClient` directly on the master path, incrementing SQLite's header change counter from 29 to 30. Zero records, documents, or embeddings were altered (`668d0776...` invariant). The resulting state (`f4a0960e...`) is locked as the authoritative master baseline.
2. **DEV-02 (Replacement of `?mode=ro` with Option C):** The previously proposed SQLite URI read-only flag was dropped after discovering that ChromaDB v1.5.9 crashes under OS write-denial. The 7-step ephemeral snapshot lifecycle (Option C) replaces it.
3. **DEV-03 (Agresti–Min Reaffirmation):** Reaffirmed the Agresti–Min (2005) formulation after informal references to "Wilson score" appeared in Phase 9.7 review text.
4. **Dual-Engine Persistence Architecture:** In ChromaDB v1.5.9, uncompacted embeddings reside in SQLite's `embeddings_queue` log table rather than fully indexed into the upper layers of the HNSW binary graph file. During query execution, ChromaDB consumes this queue in memory to serve search. Inference relies on ChromaDB's dual-engine loader rather than a standalone HNSW reader.
5. **Windows File Handle Locks:** On Windows, ChromaDB holds open file handles to SQLite and `data_level0.bin`. The Phase 10 execution harness must execute `SharedSystemClient.clear_system_cache()` and `gc.collect()` before deleting the ephemeral snapshot.
6. **Blinding Integrity:** Ground-truth prospective labels for the 100 closed-set and 30 open-set campaigns remain strictly quarantined and unscored. Unblinding is prohibited until all model predictions are written and sealed on disk.

---

## 6. Ratification of Protocol Amendment 3 (Final Signable Form)

```text
========================================================================================
                      NEXUSCTI PREREGISTERED EVALUATION PROTOCOL
                          AMENDMENT 3 (PROTOCOL v2.2-AMENDED)
========================================================================================

1. SCOPE AND GOVERNANCE
   This Amendment ratifies the Disposable Native ChromaDB Runtime Snapshot Lifecycle
   (Option C) and updates the persistence store manifest in the NexusCTI Preregistered
   Evaluation Protocol. All scientific hypotheses, test cohorts, primary endpoints,
   statistical decision rules, and model weights remain strictly frozen.

2. AUTHORITATIVE MASTER STORE IMMUTABILITY
   The master ChromaDB directory located at:
     cyber_attribution_engine/data/chroma_db/
   is designated as an immutable reference artifact. The master directory must exhibit
   zero file modifications throughout evaluation (pre/post manifest delta = 0 bytes).

3. MANDATORY 7-STEP SNAPSHOT LIFECYCLE FOR PHASE 10 EXECUTION
   The Phase 10 evaluation runner must execute inference strictly through this sequence:
   Step 1: Verify master quiescence (assert zero *-wal, *-shm, or *-journal sidecars).
   Step 2: Verify master directory manifest matches the locked 64-hex SHA-256 hashes.
   Step 3: Atomically clone the full directory via shutil.copytree() to scratch space.
   Step 4: Verify snapshot integrity (hash parity, PRAGMA integrity, document count == 7).
   Step 5: Execute prospective blind inference passing persist_directory=snapshot_dir.
   Step 6: Clear ChromaDB cache via SharedSystemClient.clear_system_cache() and destroy
           the ephemeral directory.
   Step 7: Re-verify master directory manifest; assert delta = 0 bytes modified.

4. CONFIRMATORY SUPERIORITY CRITERIA
   Confirmatory superiority is achieved if and only if:
     1. Exact two-sided McNemar test p <= 0.05 on discordant pairs.
     2. Observed paired risk difference Delta = (b - c) / N > 0.
   Effect magnitude must be reported with the prespecified 95% Agresti–Min (2005)
   paired risk-difference confidence interval. The +15.0% target is a planning MDE.
========================================================================================
```

---

## 7. Final Governance Approval Checklist & Execution Order

*(To be completed and signed by the human Principal Investigator / Governance Authority)*

### Approval Checklist
- [ ] **HNSW Verification Accepted:** Reviewed the targeted HNSW forensic verification report; accepted that the 0-byte `link_lists.bin` is structurally valid under ChromaDB v1.5.9.
- [ ] **Cryptographic Manifest Confirmed:** Reconciled 5-file master manifest and SHA-256 digests (`f4a0960e...`, `dd3bc35a...`, `a0e81c3b...`, `a2cab3b7...`, `e3b0c442...`) verified as authoritative baseline.
- [ ] **Snapshot Lifecycle Mandated:** Confirmed that Option C ephemeral snapshot lifecycle is strictly mandatory for all Phase 10 queries, preventing master database modification.
- [ ] **Statistical Decision Rules Frozen:** Confirmed exact two-sided McNemar test ($\alpha = 0.05$), directional condition ($\hat{\Delta} > 0$), Agresti–Min (2005) 95% CI, and planning MDE (+15.0%) are locked without modification.
- [ ] **Blinding Quarantine Verified:** Confirmed prospective evaluation labels (100 Task A, 30 Task B) remain unaccessed, unscored, and blinded.
- [ ] **Historical Deviations Disclosed:** Reviewed and accepted disclosed deviations DEV-01, DEV-02, and DEV-03.

---

### Human Governance Signature & Execution Order Block

```text
========================================================================================
                      FORMAL PROTOCOL RATIFICATION & EXECUTION ORDER
========================================================================================

Ratifying Authority Name:    __________________________________________________________

Official Title / Role:       __________________________________________________________

Institutional Affiliation:  __________________________________________________________

Ratified Protocol Version:   [X] NexusCTI Preregistered Evaluation Protocol v2.2-amended

Action on Amendment 3:       [ ] RATIFIED AND APPROVED
                             [ ] REJECTED (REMEDIATION REQUIRED)

Phase 10 Execution Order:    [ ] AUTHORIZED TO EXECUTE PHASE 10 BLIND BENCHMARK
                             [ ] UNAUTHORIZED (HOLD EXECUTION)

Approval Signature:          __________________________________________________________

Date of Approval:            __________________________________________________________

========================================================================================
```

---

## 8. Current System State Declaration

```text
========================================================================================
                                CURRENT SYSTEM STATE
========================================================================================
 Technical Reconciliation Status   : 100% COMPLETE & VERIFIED (Phase 9.9)
 Targeted HNSW Forensic Status     : VERIFIED & AUDITED (PASS)
 Master Immutability Status        : ZERO DELTA VERIFIED (Pre == Post)
 Protocol Amendment 3 Status       : PENDING HUMAN RATIFICATION (v2.2-amended)
 Prospective Benchmark Data        : 100% BLINDED & QUARANTINED (100 Task A + 30 Task B)
 Phase 10 Blind Evaluation Status  : STRICTLY UNAUTHORIZED
========================================================================================
```
