# NexusCTI Evaluation Runner Synthetic Dry-Run Validation Report

**Document Version:** 1.0 (Pipeline & Blinding Verification)  
**Date:** 2026-10-11  
**Project Root:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI`  
**Experiment Root:** `experiments/phase9_3_final_authorization_20261011/`  
**Executable Script:** `run_synthetic_runner_validation.py`  
**Saved Predictions:** `synthetic_predictions_dev.csv`  
**Saved Metrics:** `synthetic_runner_metrics.json`

---

## 1. Executive Summary & Verification Matrix

The evaluation runner was validated using the 15 quarantined development partition fixtures (`cand_dev_case_01` through `cand_dev_case_15`) with synthetic ground-truth labels. The actual prospective test cases (100 Task A and 30 Task B) were **NOT** touched or evaluated:

| Capability / Requirement | Test Condition | Observed Result | Classification |
| :--- | :--- | :--- | :--- |
| **Ground-Truth Blinding** | Input dictionary contains 0 labels | Zero label leakage into inference | **REPRODUCED** |
| **Frozen Record Emission** | 15 development cases processed | Exactly 15 serialized records | **REPRODUCED** |
| **Field Completeness** | Rankings, confidence, verdicts, status| All 16 protocol fields captured | **REPRODUCED** |
| **Missing Data Policy** | Case 14 simulated timeout | Rank = 99 assigned (Penalized) | **REPRODUCED** |
| **Empty Output Policy** | Case 15 simulated empty string | Rank = 99 assigned (Penalized) | **REPRODUCED** |
| **Paired Contingency Table**| Discordance aggregation | $a=9, b=3, c=0, d=3, N=15$ | **REPRODUCED** |
| **Exact McNemar p-value** | Binomial tail probability ($n_d = 3$) | $p = 0.250000$ exact | **REPRODUCED** |
| **Agresti–Min 95% CI** | Pseudocount paired interval formula | $[-0.0673, +0.4202]$ | **REPRODUCED** |
| **Saved File Reproducibility**| Re-scoring from saved CSV file | 100% bit-identical metrics | **REPRODUCED** |

---

## 2. Dry-Run Contingency Table and Statistical Telemetry

The synthetic runner produced the following paired evaluation outcomes:

```
+---------------------------------------------------------------------------------------------------------+
| SYNTHETIC EVALUATION RUNNER OUTCOME SUMMARY (N = 15 Development Cases)                                  |
+-------------------------------------------------------------+-------------------------------------------+
| Metric / Parameter                                          | Observed Synthetic Telemetry              |
+-------------------------------------------------------------+-------------------------------------------+
| Sample Size (Development Partition)                         | N = 15                                    |
| Both Correct in Top-3 (a)                                   | 9 cases                                   |
| Full Hybrid Hit, Retrieval Miss (b)                         | 3 cases                                   |
| Retrieval Hit, Full Hybrid Miss (c)                         | 0 cases                                   |
| Both Missed Top-3 (d)                                       | 3 cases (including 2 injected failures)   |
| Total Discordant Pairs (n_d = b + c)                        | 3 pairs                                   |
| Full Hybrid Top-1 Accuracy                                  | 9 / 15 (60.00%)                           |
| Full Hybrid Top-3 Accuracy                                  | 12 / 15 (80.00%)                          |
| Retrieval-only Top-1 Accuracy                               | 7 / 15 (46.67%)                           |
| Retrieval-only Top-3 Accuracy                               | 9 / 15 (60.00%)                           |
| Observed Paired Risk Difference (Δ_hat = (b - c)/N)         | +0.2000 (+20.0 percentage points)         |
| Directional Condition Met (Δ_hat > 0)                       | TRUE                                      |
| Exact Two-Sided McNemar p-value                             | 0.250000                                  |
| Prespecified 95% Agresti-Min Confidence Interval            | [-6.73%, +42.02%]                         |
+-------------------------------------------------------------+-------------------------------------------+
```

---

## 3. Failure Injection and Intention-to-Evaluate Policy

To confirm that the runner enforces the protocol's missing-data policy:
1. **Injected Execution Timeout (`cand_dev_case_14`):**
   - Simulated network timeout / thread crash during GNN feature extraction.
   - **Runner Behavior:** Caught exception cleanly, emitted `execution_status = "FAILED_EXCEPTION_TIMEOUT"`, assigned `hybrid_rank = 99` and `retrieval_rank = 99`, recorded `hybrid_abstention = True`.
2. **Injected Empty Payload (`cand_dev_case_15`):**
   - Simulated unparseable JSON output from the inference pipeline.
   - **Runner Behavior:** Emitted `execution_status = "MISSING_PREDICTION_EMPTY"`, assigned `hybrid_rank = 99` and `retrieval_rank = 99`.
3. **Scoring Consequence:** Both cases were scored as incorrect ($d$ cell incremented). The pipeline did not crash, drop rows, or substitute fallback cases.

---

## 4. Frozen Prediction Serialization & Re-Scoring Invariance

1. The runner wrote all 15 records to `synthetic_predictions_dev.csv`.
2. An independent scoring routine re-opened `synthetic_predictions_dev.csv` from disk and re-calculated the contingency table, risk difference, McNemar $p$-value, and Agresti–Min interval.
3. Every single metric matched the in-memory calculation to 10 decimal places with zero discrepancies.

**Validation Conclusion:** The evaluation runner is certified for prospective execution. It contains all necessary safeguards, adheres to technical blinding, and executes deterministically.
