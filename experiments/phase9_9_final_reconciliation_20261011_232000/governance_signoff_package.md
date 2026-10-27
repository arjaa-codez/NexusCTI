# NexusCTI Evaluation Governance Sign-Off Package
## Protocol Amendment 3 & Final Pre-Phase 10 Authorization Gate

**Document Version:** Final Signable Release  
**Date of Submission:** 2026-10-11  
**Project Root:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\cyber_attribution_engine`  
**Governing Authority:** NexusCTI Independent Evaluation Governance Committee  
**Reconciliation Reference:** [`experiments/phase9_9_final_reconciliation_20261011_232000/`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_9_final_reconciliation_20261011_232000/)  

---

> [!IMPORTANT]
> **GOVERNANCE NOTICE: SEPARATION OF TECHNICAL READINESS FROM FORMAL APPROVAL**  
> Technical verification (Phases 9.1–9.9) is 100% complete and verified. However, **technical readiness does NOT constitute protocol approval**.  
> **Phase 10 prospective evaluation remains strictly UNAUTHORIZED until the designated human governance authority signs this document.**

---

## 1. Summary of Protocol Changes (Base v2.1 to Proposed v2.2)

This amendment updates **only** the persistence access and storage governance clauses (Sections 3.1 and 3.2). All scientific endpoints, statistical tests, hypothesis criteria, model weights, and benchmark data remain **100% frozen and unaltered**.

| Protocol Section | Previously Registered Protocol (v2.1-amended) | Proposed Protocol Amendment 3 (v2.2-amended) | Rationale & Justification |
| :--- | :--- | :--- | :--- |
| **Inference Connection Mode** (Section 3.1) | Mandated SQLite `?mode=ro` URI flag on the active ChromaDB client connection. | Replaced by the **7-Step Disposable Native ChromaDB Runtime Snapshot Lifecycle (Option C)**. | ChromaDB v1.5.9 does not pass SQLite URI flags to its C++/Rust engine, crashing with `readonly_db` under filesystem write denial. Ephemeral snapshot cloning enforces complete master immutability without modifying retrieval code. |
| **Master Store Manifest** (Section 3.2) | Single file: `chroma.sqlite3` (`f1619bf2...`, initial freeze). | Complete 5-file store: `chroma.sqlite3` and segment folder `3962f896-273d-4039-b97e-d0aa4e6d29ed/` with reconciled 64-hex SHA-256 hashes. | ChromaDB v1.5.9 stores vector graph indices outside SQLite. Single-file cloning breaks HNSW retrieval. Reconciled manifest reflects change counter state 30 following diagnostic inspection. |
| **Hypothesis & Endpoints** (Section 2.1) | Paired Top-3 Accuracy on 100 closed-set Task A campaigns. | Paired Top-3 Accuracy on 100 closed-set Task A campaigns. | **UNCHANGED** |
| **Primary Statistical Test** (Section 2.2) | Exact two-sided McNemar test on discordant pairs ($\alpha = 0.05$). | Exact two-sided McNemar test on discordant pairs ($\alpha = 0.05$). | **UNCHANGED** |
| **Directional Rule** (Section 2.3) | Confirmatory superiority requires $p \le 0.05$ **AND** $\hat{\Delta} > 0$. | Confirmatory superiority requires $p \le 0.05$ **AND** $\hat{\Delta} > 0$. | **UNCHANGED** |
| **Confidence Interval** (Section 3.3) | 95% Agresti–Min (2005) pseudo-observation paired interval. | 95% Agresti–Min (2005) pseudo-observation paired interval. | **UNCHANGED** |
| **Planning MDE Target** (Section 2.4) | $+15.0\%$ percentage points (sample size planning MDE only). | $+15.0\%$ percentage points (sample size planning MDE only). | **UNCHANGED** |

---

## 2. Locked Statistical Decision Rule and Scientific Parameters

### 2.1 Primary Endpoint & Statistical Test
- **Primary Endpoint:** Paired Top-3 Accuracy difference between Full Hybrid ($A$) and Retrieval-only ($B$) models across $N = 100$ independent closed-set Task A campaigns.
- **Primary Test:** Exact two-sided McNemar test on discordant campaign pairs ($b$: Hybrid success / Retrieval failure; $c$: Retrieval success / Hybrid failure):
  $$p = 2 \sum_{k=b}^{n_d} \binom{n_d}{k} (0.5)^{n_d} \quad \text{if } b > c, \quad \text{where } n_d = b + c$$
- **Significance Level:** $\alpha = 0.05$ (two-sided).

### 2.2 Decision Rule for Confirmatory Superiority
Confirmatory superiority is achieved if and only if **both** criteria are satisfied:
1. Exact two-sided McNemar test $p \le 0.05$.
2. Observed paired risk difference $\hat{\Delta} = \frac{b - c}{N} > 0$.

### 2.3 Prespecified Confidence Interval Method
To prevent interval-test discordance while maintaining exact coverage, practical effect magnitude will be reported using the prespecified **95% Agresti–Min (2005) Paired Risk-Difference Interval**:
$$\tilde{\Delta} \pm 1.95996 \cdot \widetilde{\text{SE}}$$
where $+1.0$ pseudo-observation is added to each discordant cell ($+2.0$ to total sample size):
$$\tilde{\Delta} = \frac{(b + 1) - (c + 1)}{N + 2}, \qquad \widetilde{\text{SE}} = \frac{1}{N + 2}\sqrt{(b + 1) + (c + 1) - \frac{[(b + 1) - (c + 1)]^2}{N + 2}}$$
*(Reference: Agresti, A., & Min, Y. (2005). Statistics in Medicine, 24(5), 729–740).*

### 2.4 Power Assumptions and Role of MDE Target
- **Power Assumptions:** Evaluated at $N = 100$, discordant pair proportion $q = 0.25$, odds ratio $\theta = 4.0$ ($0.80 / 0.20$), yielding **$83.674\%$ statistical power**.
- **Role of $+15.0\%$ Target:** The $+15.0$ percentage point target is prespecified as the **planning Minimal Detectable Effect (MDE)** for sample size calibration, **not** an additional observed sample point-estimate gating constraint.

---

## 3. Authoritative Master Store Cryptographic Manifest

The authoritative frozen vector store is located at:
`cyber_attribution_engine/data/chroma_db/`

Every file was directly re-hashed from byte streams in Phase 9.9. All SHA-256 digests are strictly 64 hexadecimal characters:

| Relative File Path | Exact Byte Size | Authoritative SHA-256 Digest (64 Hex Characters) | Role & Description |
| :--- | :---: | :--- | :--- |
| `chroma.sqlite3` | 294,912 | `f4a0960e60ef06d5669df55e648ad463ebbdcdff62381ec6d26e17dfaefc56dc` | Relational metadata, documents, and segment mappings. |
| `3962f896-.../data_level0.bin` | 167,600 | `dd3bc35aff31318f10dab2111ad835e55926233f1e0e8922cdc30bc92ce171f8` | HNSW Level-0 graph and 384d vector embeddings. |
| `3962f896-.../header.bin` | 100 | `a0e81c3b22454233bc12d0762f06dcca48261a75231cf87c79b75e69a6c00150` | HNSW index configuration header (cosine metric). |
| `3962f896-.../length.bin` | 400 | `a2cab3b7fffef0b5e24cb03aaf91e69be401e590bbff1c192c3d12be61d46f06` | Vector array length offsets. |
| `3962f896-.../link_lists.bin` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | Skip-list layers $\ge 1$ (0 bytes: normal for $N=7, l_{\max}=0$). |

- **Canonical Content SHA-256:** `668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7` (**100% Invariant**)
- **SQLite Change Counter:** `30`
- **SQLite Integrity:** `PRAGMA integrity_check == 'ok'`

---

## 4. Disclosed Historical Deviations, Limitations, and Residual Risks

### 4.1 Disclosed Deviations
1. **DEV-01 (Change Counter Increment 29 -> 30):** An interactive diagnostic command (`task-2785`) executed on `2026-10-11 22:33:27` opened `PersistentClient` directly on the master path, incrementing SQLite's header change counter from 29 to 30. Zero data rows or embeddings were altered (`668d0776...` invariant). The resulting binary hash (`f4a0960e...`) is locked as the authoritative master baseline.
2. **DEV-02 (Replacement of `?mode=ro` with Option C):** The unexecutable URI flag clause was replaced by the 7-step ephemeral snapshot lifecycle.
3. **DEV-03 (Agresti–Min Reaffirmation):** Corrected casual references to "Wilson score" in Phase 9.7 review text back to the prespecified Agresti–Min (2005) formulation.

### 4.2 Residual Limitations & Operational Safeguards
1. **Windows NTFS File Handle Locks:** On Windows, ChromaDB's cached singleton holds open file handles to SQLite and `data_level0.bin`. The Phase 10 execution harness must execute:
   ```python
   del rag.collection; del rag.client; del rag
   SharedSystemClient.clear_system_cache()
   gc.collect()
   shutil.rmtree(snapshot_dir, ignore_errors=True)
   ```
2. **Path Misconfiguration Protection:** The Phase 10 evaluation harness must reject any configuration pointing directly to `cyber_attribution_engine/data/chroma_db/`. Execution is permitted only via `persist_directory=str(snapshot_dir)`.
3. **Quarantine of Prospective Labels:** Ground-truth test labels for the 100 closed-set and 30 open-set campaigns remain strictly quarantined. Unblinding is prohibited until all model predictions are written and sealed on disk.

---

## 5. Text of Protocol Amendment 3 (Final Signable Form)

```
========================================================================================
                      NEXUSCTI PREREGISTERED EVALUATION PROTOCOL
                          AMENDMENT 3 (PROTOCOL v2.2-AMENDED)
========================================================================================

1. SCOPE AND GOVERNANCE
   This Amendment ratifies the Disposable Native ChromaDB Runtime Snapshot Lifecycle
   (Option C) and updates the persistence store manifest in the NexusCTI Preregistered
   Evaluation Protocol. All hypotheses, test cohorts, endpoints, statistical decision
   rules, and model weights remain strictly frozen.

2. AUTHORITATIVE MASTER STORE IMMUTABILITY
   The master ChromaDB directory located at:
     cyber_attribution_engine/data/chroma_db/
   is designated as an immutable reference artifact. The master directory must exhibit
   zero file modifications throughout the evaluation (pre/post manifest delta = 0).

3. MANDATORY 7-STEP SNAPSHOT LIFECYCLE FOR PHASE 10 EXECUTION
   The Phase 10 evaluation runner must execute inference strictly through this sequence:
   Step 1: Verify master quiescence (assert zero *-wal, *-shm, or *-journal files).
   Step 2: Verify master directory manifest matches the locked 64-hex SHA-256 hashes.
   Step 3: Atomically clone the full directory via shutil.copytree() to scratch space.
   Step 4: Verify snapshot integrity (hash parity, PRAGMA integrity, count == 7).
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

## 6. Formal Governance Sign-Off & Phase 10 Authorization Block

> **INSTRUCTIONS FOR GOVERNANCE AUTHORITY:**  
> Review the Phase 9.9 reconciliation findings and the terms of Amendment 3 above.  
> If satisfied, execute the fields below to ratify Protocol Amendment 3 and authorize Phase 10 blind evaluation.

```
========================================================================================
                     FORMAL PROTOCOL RATIFICATION & EXECUTION ORDER
========================================================================================

Ratifying Authority Name:   __________________________________________________________

Official Title / Role:      __________________________________________________________

Institutional Affiliation: __________________________________________________________

Ratified Protocol Version:  [X] NexusCTI Preregistered Evaluation Protocol v2.2-amended

Action on Amendment 3:      [ ] RATIFIED AND APPROVED
                            [ ] REJECTED (REMEDIATION REQUIRED)

Phase 10 Execution Order:   [ ] AUTHORIZED TO EXECUTE PHASE 10 BLIND BENCHMARK
                            [ ] UNAUTHORIZED (HOLD EXECUTION)

Approval Signature:         __________________________________________________________

Date of Approval:           __________________________________________________________

========================================================================================
```

---

## 7. Current Governance Status Declaration

```
========================================================================================
                             CURRENT REPOSITORY STATUS
========================================================================================
 Technical Reconciliation Status  : 100% COMPLETE & VERIFIED (Phase 9.9)
 Gate Decision Evaluation         : READY FOR HUMAN/FORMAL PROTOCOL APPROVAL
 Protocol Amendment 3 Status      : PENDING HUMAN SIGNATURE (v2.2-amended)
 Prospective Benchmark Data       : BLINDED & QUARANTINED (100 Task A + 30 Task B)
 Phase 10 Execution Status        : UNAUTHORIZED
========================================================================================
```
