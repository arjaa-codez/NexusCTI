# NexusCTI Phase 10 Execution Contract Verification Report

**Document Version:** 1.0 (Execution Contract & Operational Readiness)  
**Date:** 2026-10-11  
**Project Root:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI`  
**Experiment Root:** `experiments/phase9_4_execution_safety/`  
**Protocol Basis:** `experiments/phase9_3_final_authorization_20261011/phase9_3_final_protocol.md` (Version 2.0 Locked)  
**Audit Telemetry:** `execution_safety_telemetry.json`

---

## 1. Executive Summary & Verification Matrix

This audit evaluated the exact execution contract governing the prospective Phase 10 blind evaluation run to confirm full compliance with Protocol Version 2.0:

| Contract Provision | Target Specification | Observed Audit Value | Verification Status |
| :--- | :--- | :--- | :--- |
| **Task A Case Count** | 100 closed-set campaigns | Exactly 100 cases registered | **VERIFIED** |
| **Task B Case Count** | 30 open-set novel campaigns | Exactly 30 cases registered | **VERIFIED** |
| **Total Test Universe** | 130 independent campaigns | Exactly 130 cases registered | **VERIFIED** |
| **Case Identifier Stability** | Unique opaque IDs (`cand_task_...`) | 130 / 130 unique IDs | **VERIFIED** |
| **Failure Handling Policy** | Rank = 99 for timeouts/exceptions | Verified on dev cases 14 & 15 | **VERIFIED** |
| **Prediction Serialization** | Freeze & hash prior to scoring | Validated serialization flow | **VERIFIED** |
| **Primary Endpoint** | Paired Top-3 accuracy (Hybrid vs Ret) | Formally locked in runner | **VERIFIED** |
| **Primary Statistical Test**| Exact two-sided McNemar ($\alpha=0.05$)| Binomial tail summation locked | **VERIFIED** |
| **Directional Superiority** | $\hat{\Delta} > 0$ ($b > c$) | Strictly enforced | **VERIFIED** |
| **Planning MDE** | $+15.0$ percentage points | Decoupled from sample gate | **VERIFIED** |
| **Confidence Interval** | Agresti–Min (2005) 95% paired CI | Exact pseudocount formula locked | **VERIFIED** |

---

## 2. Test Case Partitioning and Identifier Stability

Inspection of the candidate manifest confirmed that the prospective evaluation corpus is fully formed and locked:
1. **Task A (Closed-Set Confirmatory Evaluation):**
   - $N = 100$ independent campaigns attributed to 14 candidate threat actors (`actor_apt28`, `actor_apt29`, `actor_lazarus`, `actor_sandworm`, `actor_volt_typhoon`, `actor_fin7`, etc.).
   - Each campaign possesses a unique opaque identifier (`cand_task_a_actor_apt28_01` through `cand_task_a_actor_wizard_spider_07`).
2. **Task B (Open-Set Novel Campaign Abstention):**
   - $N = 30$ independent intrusion operations representing out-of-registry actors and commodity multi-actor campaigns.
   - Each campaign possesses a unique opaque identifier (`cand_task_b_AMBIGUOUS_MULTI_ACTOR_01` through `cand_task_b_NOVEL_UNSEEN_ACTOR_15`).
3. **Total Unique Identifiers:** Exactly $130$ distinct, stable IDs with zero duplicates or collisions.

---

## 3. Failure Handling & Intention-to-Evaluate Enforcement

Under Protocol Version 2.0 Section 5, every test case must be scored without post-hoc exclusions:
- **Runtime Timeouts:** If GNN inference or vector retrieval times out (simulated on `cand_dev_case_14`), the runner records `execution_status = "FAILED_EXCEPTION_TIMEOUT"` and assigns `hybrid_rank = 99` and `retrieval_rank = 99`.
- **Unparseable Outputs:** If the model outputs empty or non-parseable JSON (simulated on `cand_dev_case_15`), the runner records `execution_status = "MISSING_PREDICTION_EMPTY"` and assigns `hybrid_rank = 99` and `retrieval_rank = 99`.
- **Scoring Consequence:** In both failure modes, the outcome increments the discordant/miss cell ($d$), directly penalizing the failing system. Cases are never dropped or re-sampled.

---

## 4. Prediction Freezing Sequence Before Unblinding

The Phase 10 execution runner is contractually constrained to execute in strict phases:
```
[Phase 10 Execution Sequence]
    │
    ├── Step 1: Run inference on all 130 cases (Task A + Task B) using inputs only.
    │           (Ground-truth labels are completely inaccessible to the runner).
    │
    ├── Step 2: Write all 130 prediction records to "frozen_test_predictions.csv".
    │
    ├── Step 3: Compute and record the cryptographic SHA-256 hash of "frozen_test_predictions.csv".
    │
    ├── Step 4: ONLY AFTER prediction freeze, load quarantined ground-truth labels.
    │
    └── Step 5: Execute scoring script to compute paired tables, McNemar p-value, and Agresti-Min CI.
```

---

## 5. Statistical Estimands and Decision Rule Verification

The scoring engine enforces the exact mathematical specifications of Protocol Version 2.0:
1. **Paired Sample Risk Difference:**
   $$\hat{\Delta} = \frac{b - c}{N} = \frac{b - c}{100}$$
2. **Exact Two-Sided McNemar Test:**
   $$p_{\text{McNemar}} = \min\left(1.0, \, 2 \times \sum_{i = \max(b, c)}^{b + c} \binom{b + c}{i} 0.5^{b + c}\right)$$
3. **Directional Superiority Requirement:**
   $$\hat{\Delta} > 0 \iff b > c$$
4. **Agresti–Min (2005) 95% Confidence Interval:**
   $$\tilde{b} = b + 1, \quad \tilde{c} = c + 1, \quad \tilde{N} = 102$$
   $$\tilde{\Delta} = \frac{b - c}{102}, \quad \text{SE}(\tilde{\Delta}) = \sqrt{\frac{\frac{b + c + 2}{102} - \tilde{\Delta}^2}{102}}$$
   $$\text{CI}_{95\%} = \left[ \tilde{\Delta} - 1.95996 \times \text{SE}(\tilde{\Delta}), \; \tilde{\Delta} + 1.95996 \times \text{SE}(\tilde{\Delta}) \right]$$

---

## 6. Execution Contract Conclusion

The Phase 10 execution contract mechanics are **VERIFIED AND CERTIFIED**. The test case accounting, identifier stability, failure handling policy, prediction serialization sequence, and statistical decision rules match Protocol Version 2.0 exactly.
