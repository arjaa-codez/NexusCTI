# Phase 9.9 — Protocol Amendment Diff and Final Proposed Amendment

**Audit Phase:** NexusCTI Phase 9.9 — Final Integrity Reconciliation and Protocol Approval Preparation  
**Timestamp:** 2026-10-11T23:25:00+05:30  
**Project Root:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\cyber_attribution_engine`  
**Base Preregistration Protocol:** Phase 9.3 Final Evaluation Protocol (`experiments/phase9_3_final_authorization_20261011/phase9_3_final_protocol.md`)  
**Proposed Version:** NexusCTI Preregistered Evaluation Protocol v2.2-amended  

---

## 1. Executive Summary

This document performs the formal reconciliation between the base preregistered protocol (Phase 9.3, v2.1-amended) and the final **Protocol Amendment 3 (v2.2-amended)**.

### Governing Rules Strictly Maintained:
1. **Primary Endpoint Unaltered:** Paired Top-3 accuracy on 100 closed-set Task A campaigns comparing Full Hybrid vs. Retrieval-only.
2. **Statistical Decision Rule Unaltered:** Confirmatory superiority requires **both**:
   - Exact two-sided McNemar test $p \le 0.05$.
   - Observed paired risk difference $\hat{\Delta} = (b - c) / N > 0$.
3. **Prespecified Confidence Interval:** 95% Agresti–Min (2005) pseudo-observation interval for paired risk differences (+1 pseudo-observation per discordant cell / +2 overall effective sample size).
4. **Planning MDE Clarified:** The $+15.0$ percentage point target is explicitly reaffirmed as a sample size planning target (MDE at $83.67\%$ power for $N=100$), **not** a hard observed exclusion threshold.
5. **Sole Protocol Modification:** Replaces the unexecutable `?mode=ro` URI flag clause with the mathematically and cryptographically verified **Disposable Native ChromaDB Runtime Snapshot Lifecycle (Option C)**.

---

## 2. Protocol Clause Diff (Base v2.1 vs. Proposed v2.2)

```diff
================================================================================
SECTION 3.1: INFERENCE DATABASE PERSISTENCE AND ACCESS GOVERNANCE
================================================================================
- [Phase 9.3 v2.1 Clause]:
- The prospective evaluation runner must connect to ChromaDB exclusively using
- the ?mode=ro URI flag. The master database file must be marked read-only at
- the filesystem level, and any write attempt must fail.
+ [Proposed Amendment 3 v2.2 Clause]:
+ The authoritative master ChromaDB persistence store located at
+ cyber_attribution_engine/data/chroma_db/ is designated as an immutable golden
+ master. Prior to prospective evaluation, the evaluation harness must clone the
+ complete persistence directory (chroma.sqlite3 and segment folder
+ 3962f896-273d-4039-b97e-d0aa4e6d29ed/) into an isolated disposable runtime
+ directory via shutil.copytree(). Inference must execute strictly against this
+ disposable snapshot using the native ThreatRAGEngine. The disposable snapshot
+ must be verified pre-inference, completely destroyed post-inference, and the
+ authoritative master directory re-verified to ensure zero bytes modified.

================================================================================
SECTION 3.2: PERSISTENCE STORE MASTER MANIFEST
================================================================================
- [Phase 9.3 v2.1 Clause]:
- Master File: cyber_attribution_engine/data/chroma_db/chroma.sqlite3
- Pre-Evaluation Binary SHA-256: f1619bf2182fe2cdeef65be2e6785262b5e2e5e0f83a7bbdfa3f9cb67a0232a5
+ [Proposed Amendment 3 v2.2 Clause]:
+ Master Directory: cyber_attribution_engine/data/chroma_db/
+ Reconciled Master Manifest (Five Files):
+ 1. chroma.sqlite3:
+    Size: 294,912 bytes | SHA-256: f4a0960e60ef06d5669df55e648ad463ebbdcdff62381ec6d26e17dfaefc56dc
+ 2. 3962f896-273d-4039-b97e-d0aa4e6d29ed/data_level0.bin:
+    Size: 167,600 bytes | SHA-256: dd3bc35aff31318f10dab2111ad835e55926233f1e0e8922cdc30bc92ce171f8
+ 3. 3962f896-273d-4039-b97e-d0aa4e6d29ed/header.bin:
+    Size: 100 bytes     | SHA-256: a0e81c3b22454233bc12d0762f06dcca48261a75231cf87c79b75e69a6c00150
+ 4. 3962f896-273d-4039-b97e-d0aa4e6d29ed/length.bin:
+    Size: 400 bytes     | SHA-256: a2cab3b7fffef0b5e24cb03aaf91e69be401e590bbff1c192c3d12be61d46f06
+ 5. 3962f896-273d-4039-b97e-d0aa4e6d29ed/link_lists.bin:
+    Size: 0 bytes       | SHA-256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
+ Canonical Content SHA-256: 668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7
+ SQLite Change Counter: 30

================================================================================
SECTION 3.3: PRIMARY STATISTICAL DECISION RULE & ESTIMANDS
================================================================================
  [Unaltered in v2.2]:
  Primary Endpoint: Paired Top-3 Accuracy (Hybrid vs Retrieval-only, N=100).
  Primary Hypothesis Test: Exact two-sided McNemar test, alpha = 0.05.
  Directional Requirement: Observed paired risk difference Delta > 0.
  Confidence Interval: Prespecified 95% Agresti–Min (2005) paired interval.
  Planning Target: +15.0 percentage points (sample size planning MDE only).
```

---

## 3. Disclosure of Protocol Deviations

To maintain absolute scientific transparency, every protocol adaptation that occurred since Phase 9 is explicitly documented and disclosed:

| Deviation ID | Nature of Deviation | Root Cause | Disclosure & Remediation Mechanism |
| :--- | :--- | :--- | :--- |
| **DEV-01** | Master SQLite change counter bumped 29 -> 30 | Diagnostic connection `PersistentClient(master_dir)` executed in Phase 9.7 (task-2785). | Fully disclosed in [`master_hash_chain_of_custody.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_8_evidence_reconciliation/master_hash_chain_of_custody.md). Canonical content verified invariant (`668d0776...`). Reconciled manifest locked in Amendment 3. |
| **DEV-02** | Replaced `?mode=ro` SQLite flag with Disposable Snapshot (Option C) | ChromaDB v1.5.9 does not pass URI flags and crashes with `readonly_db` under OS write denial. | Formally amended via Amendment 3. Ephemeral snapshot lifecycle enforces complete read-only isolation of master with zero leakage. |
| **DEV-03** | Clarification of Confidence Interval Formulation | Phase 9.7 review text casually referred to "Wilson score" instead of prespecified "Agresti–Min". | Corrected and reconciled in Phase 9.9. Protocol v2.2 explicitly reaffirms Agresti–Min (2005) pseudo-observation interval formula. |

---

## 4. Text of Final Proposed Protocol Amendment 3

### **Title: Protocol Amendment 3 — Master Immutability and Disposable Snapshot Lifecycle (NexusCTI Evaluation Protocol v2.2-amended)**

#### Clause 1: Scope of Amendment
This amendment amends Section 3 of the NexusCTI Preregistered Evaluation Protocol. It does not alter the hypothesis, sample cohorts, primary endpoints, statistical tests, significance levels, or model architectures.

#### Clause 2: The Authoritative Frozen Master Store
The master knowledge base is located at `cyber_attribution_engine/data/chroma_db/`. Its authoritative composition consists of the five files detailed in Section 2 above. The master directory must remain quiescent and immutable throughout all prospective evaluation runs.

#### Clause 3: Mandatory Disposable Snapshot Lifecycle Procedure
All Phase 10 prospective evaluation inference must be executed using the following 7-step sequence:
1. **Pre-Evaluation Quiescence Check:** Assert 0 active `*-wal`, `*-shm`, or `*-journal` files in the master directory.
2. **Master Directory Manifest Parity:** Assert all 5 files match the locked 64-hex SHA-256 hashes.
3. **Atomic Recursive Clone:** Execute `shutil.copytree(master_dir, snapshot_dir)`.
4. **Snapshot Pre-Flight Integrity Check:** Verify snapshot files match master hashes, SQLite integrity is `ok`, canonical content hash is `668d0776...`, and collection count is 7.
5. **Blind Prospective Inference:** Pass `persist_directory=str(snapshot_dir)` to `ThreatRAGEngine` and execute prospective test queries.
6. **Clean Resource Teardown:** Execute:
   ```python
   del eval_rag.collection; del eval_rag.client; del eval_rag
   SharedSystemClient.clear_system_cache()
   gc.collect()
   shutil.rmtree(snapshot_dir, ignore_errors=True)
   ```
7. **Post-Evaluation Master Invariance Verification:** Re-compute master hashes; assert delta $= 0$.

#### Clause 4: Confirmatory Decision Rule Reaffirmation
Confirmatory superiority is achieved if and only if:
1. Exact two-sided McNemar test $p \le 0.05$.
2. Observed paired risk difference $\hat{\Delta} = (b - c) / N > 0$.
The effect size must be reported with the prespecified 95% Agresti–Min (2005) paired risk-difference confidence interval:
$$\tilde{\Delta} \pm 1.95996 \cdot \widetilde{\text{SE}}$$
where $\tilde{\Delta} = \frac{(b + 1) - (c + 1)}{N + 2}$ and $\widetilde{\text{SE}} = \frac{1}{N+2}\sqrt{(b + 1) + (c + 1) - \frac{[(b + 1) - (c + 1)]^2}{N + 2}}$.
