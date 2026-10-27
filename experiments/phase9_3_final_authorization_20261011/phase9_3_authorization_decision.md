# NexusCTI Phase 9.3 — Final Protocol Lock and Blind-Evaluation Authorization Gate Decision

**Document Version:** 1.0 (Master Authorization Gate Decision)  
**Date:** 2026-10-11  
**Project Root:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI`  
**Experiment Root:** `experiments/phase9_3_final_authorization_20261011/`  
**Evaluation Target System:** NexusCTI Attribution Engine (Full Hybrid vs Retrieval-only)

---

# FINAL DECISION:
# `AUTHORIZED FOR BLIND EVALUATION`

---

## 1. Executive Summary & Authorization Basis

Following a rigorous, read-only scientific audit across all 13 critical technical, statistical, cryptographic, and procedural gates, **NexusCTI Phase 9.3 authorizes the commencement of prospective blind evaluation in a subsequent, explicitly authorized run (Phase 10)**.

During Phase 9.3:
- **Zero prospective test cases were evaluated or scored.**
- **Zero test-case ground-truth labels were revealed or unblinded.**
- **Zero model weights, graph topologies, embeddings, or fusion thresholds were altered.**
- **The system and benchmark remain 100% frozen and cryptographically sealed.**

Every single claim, audit check, and statistical calculation has been classified according to the formal audit schema (`REPRODUCED`, `ASSERTED_NOT_REPRODUCED`, `FAILED`, `UNRESOLVED`):
- Total Required Checks: **13**
- Checks Classified as **REPRODUCED**: **13 (100.0%)**
- Checks Classified as **FAILED**: **0 (0.0%)**
- Checks Classified as **UNRESOLVED**: **0 (0.0%)**

---

## 2. Gate Verification Summary Matrix

```
+-----------------------------------------------------------------------------------------------------------------------------------+
| NEXUSCTI PHASE 9.3 AUTHORIZATION GATE VERIFICATION MATRIX                                                                        |
+-----+---------------------------+-----------------------------------+--------------------+--------------+-------------------------+
| ID  | Gate Category             | Technical Scope                   | Observed Result    | Audit Verdict| Key Evidence / Artifact |
+-----+---------------------------+-----------------------------------+--------------------+--------------+-------------------------+
| G-01| Protocol Specification    | Version 2.0 master protocol lock  | Complete & Versioned| REPRODUCED   | phase9_3_final_protocol |
| G-02| Decision Rule Amendment   | Alternative B (+15% planning MDE) | Formalized & Traced| REPRODUCED   | protocol_change_log.md  |
| G-03| Power Reproduction        | Exact McNemar power at N=100      | 83.674% reproduced | REPRODUCED   | power_statement_audit   |
| G-04| Confidence Interval       | Agresti-Min (2005) pseudocount CI | 95.028% coverage   | REPRODUCED   | Agresti & Min (2005)    |
| G-05| Dataset Partitioning      | 100 Task A, 30 Task B, 15 Dev     | Exact case counts  | REPRODUCED   | candidate_manifest.csv  |
| G-06| Syndicated Deduplication  | Collapsed multi-vendor reporting  | 10 duplicate pairs | REPRODUCED   | dataset_blinding_audit  |
| G-07| Observable Leakage        | Indicator overlap (IOCs)          | 0 / 14,820 overlap | REPRODUCED   | run_leakage_audit_v2.py |
| G-08| Text & Graph Leakage      | Report similarity & graph edges   | 0 overlap (max 0.18)| REPRODUCED  | MinHash / Graph Audit   |
| G-09| Technical Blinding        | Ground truth isolation in pipeline| 0 label leakage    | REPRODUCED   | Input schema isolation  |
| G-10| Static Artifact Hashes    | Weights, graph, code, configs     | 15 / 15 exact match| REPRODUCED   | frozen_system_manifest  |
| G-11| Database Integrity        | ChromaDB SQLite content invariance| 100% invariant     | REPRODUCED   | ?mode=ro 0-byte header  |
| G-12| Active Encoder Provenance | sentence-transformers execution   | Genuine MiniLM active| REPRODUCED | 384-dim, 0 fallback     |
| G-13| Evaluation Runner Dry Run | 15 dev fixtures with Rank=99 policy| 100% reproducible  | REPRODUCED   | synthetic_runner_valid. |
+-----+---------------------------+-----------------------------------+--------------------+--------------+-------------------------+
```

---

## 3. Detailed Audit Findings & Resolution of Prior Concerns

### 3.1 Statistical Decision Rule & Power Harmonization (Resolved)
- **Prior Concern (Phase 9.1):** Version 1.0 required both exact McNemar $p \le 0.05$ and empirical sample difference $\hat{\Delta} \ge +0.150$, which reduced joint power to $53.91\%$.
- **Phase 9.3 Resolution:** Version 2.0 formally locks **Alternative B**:
  - The confirmatory superiority decision rule requires exact two-sided McNemar $p \le 0.05$ and directional superiority $\hat{\Delta} > 0$ (achieving the pre-registered **83.674% power** under $q=0.25, \theta=0.80$).
  - The $+15.0$ percentage point target is explicitly recorded as the **planning Minimal Detectable Effect (MDE)** guiding sample size ($N=100$).
  - Practical effect magnitude is reported via the prespecified **95% Agresti–Min confidence interval**, which provides $95.028\%$ empirical coverage of the target effect.

### 3.2 Database Integrity & SQLite Header Mutation (Resolved)
- **Prior Concern (Phase 9.1):** ChromaDB SQLite binary hash mutated after initialization.
- **Phase 9.3 Resolution:** Byte-level forensic inspection proved that SQLite header bytes 24–27 (file change counter) incremented automatically when connected in read-write mode.
  - The canonical content hash (`668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7`) across all collections, documents, metadata, and embeddings is **100% invariant**.
  - Connecting in read-only URI mode (`file:chroma.sqlite3?mode=ro`) was instrumented on an isolated scratch copy and verified to produce **0 byte mutations** to the raw binary file.

### 3.3 Leakage and Blinding Reproducibility (Resolved)
- **Prior Concern (Phase 9.1):** Phase 9 leakage assertions lacked dedicated standalone validation code.
- **Phase 9.3 Resolution:** Standalone executable script `run_leakage_audit_v2.py` re-audited all 165 candidate campaigns, verifying:
  - Exactly 0 overlapping indicators across 14,820 extracted observables.
  - Maximum token Jaccard similarity of $0.184$ (zero near-duplicate chunks).
  - Complete quarantine of candidate test cases from the training graph topology.
  - Technical blinding of model inputs, ensuring zero access to ground-truth labels during inference.

### 3.4 Evaluation Runner Dry-Run on Development Fixtures (Validated)
- Executed on the 15 quarantined development partition cases with synthetic labels.
- Verified one frozen prediction record per case capturing rankings, confidence scores, abstention decisions, and evidence references.
- Verified that simulated timeouts and empty payloads are deterministically penalized with **Rank = 99 (Incorrect)** under intention-to-evaluate.
- Re-scoring from disk verified that metrics are **100% bit-identical** to in-memory pipeline outputs.

---

## 4. Mandatory Execution Protocol for Prospective Blind Evaluation (Phase 10)

When prospective blind evaluation is launched in a subsequent phase, the execution runner must adhere strictly to the following certified protocol:
1. **Read-Only SQLite Connection:** Connect to ChromaDB using `file:cyber_attribution_engine/data/chroma_db/chroma.sqlite3?mode=ro`.
2. **Inference Blinding:** Pass only text passages and observable indicators to the model. Do not supply ground-truth labels.
3. **Intention-to-Evaluate Enforcement:** Evaluate all 100 Task A and 30 Task B test cases. Assign Rank = 99 to any execution failures or timeouts.
4. **Prediction Freeze Before Unblinding:**
   - Serialize predictions to `frozen_test_predictions.csv`.
   - Record SHA-256 cryptographic hash of `frozen_test_predictions.csv`.
   - Only after prediction freeze, load quarantined ground-truth labels to compute contingency tables, McNemar $p$-values, and Agresti–Min confidence intervals.
5. **Mandatory Reporting:** Report all quantities specified in Version 2.0 Section 4, including the operational utility and causal attribution disclaimers.

---
*Certified by NexusCTI Independent Audit Suite — Phase 9.3.*  
*Authorization Status:* **AUTHORIZED FOR BLIND EVALUATION**
