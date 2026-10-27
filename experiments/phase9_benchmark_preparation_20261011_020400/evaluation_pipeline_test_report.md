# NexusCTI Phase 9 — Evaluation Pipeline Validation Report

**Document Version:** 1.0 (Pre-Registration Protocol Freeze)  
**Date:** 2026-10-11  
**Experiment Root:** `experiments/phase9_benchmark_preparation_20261011_020400/`  

---

## Executive Summary

Before freezing the benchmark and executing test predictions, the automated evaluation pipeline and statistical scoring engine were subjected to rigorous stress testing across seven synthetic edge-case prediction tables and missing-data scenarios.

The pipeline successfully processed all edge cases without numerical instability, division-by-zero crashes, or NaN generation, confirming that the scoring code is robust and ready for untouched prospective evaluation.

---

## 1. Synthetic Edge-Case Test Suite

The scoring pipeline was tested using the following synthetic contingency tables (results preserved in `pipeline_validation_data.json`):

```
+--------------------------------------------------------------------------------------------------------+
| SYNTHETIC PIPELINE STRESS TEST RESULTS MATRIX                                                          |
+--------------------------+----+----+----+----+----+--------+---------+--------+--------+---------------+
| Test ID / Condition      | a  | b  | c  | d  | N  | n_d    | p-value | Δ (%)  | ψ (OR) | Status        |
+--------------------------+----+----+----+----+----+--------+---------+--------+--------+---------------+
| TC-1: All Concordant Cor.| 50 |  0 |  0 |  0 | 50 |   0    | 1.0000  |  0.0%  | 1.000  | PASSED        |
| TC-2: All Concordant Inc.|  0 |  0 |  0 | 50 | 50 |   0    | 1.0000  |  0.0%  | 1.000  | PASSED        |
| TC-3: Zero Cell (c = 0)  | 20 | 25 |  0 | 20 | 65 |  25    | 0.0000  | +38.5% | inf    | PASSED (Handl)|
| TC-4: Zero Cell (b = 0)  | 20 |  0 | 25 | 20 | 65 |  25    | 0.0000  | -38.5% | 0.000  | PASSED (Handl)|
| TC-5: Balanced Discord.  | 30 | 10 | 10 | 30 | 80 |  20    | 1.0000  |  0.0%  | 1.000  | PASSED        |
| TC-6: Strong Asymmetry   | 30 | 20 |  5 | 30 | 85 |  25    | 0.0041  | +17.6% | 4.000  | PASSED        |
| TC-7: Small Sample Tie   |  5 |  1 |  1 |  5 | 12 |   2    | 1.0000  |  0.0%  | 1.000  | PASSED        |
+--------------------------+----+----+----+----+----+--------+---------+--------+--------+---------------+
```

---

## 2. Detailed Edge-Case Behavioral Analysis

### Test Case 1 & 2: Zero Discordant Pairs ($n_d = 0$)
- **Condition:** When both systems agree on all test cases ($b = 0, c = 0$), McNemar's test has 0 degrees of freedom.
- **Pipeline Behavior:** The engine detects $n_d = 0$, avoids division by zero, outputs exact $p = 1.0000$, sets odds ratio $\psi = 1.0$, and centers risk difference at $\Delta = 0.0\%$.
- **Interval Check:** Agresti-Min interval cleanly evaluates to $[-5.75\%, +5.75\%]$ for $N = 50$, properly reflecting random symmetry.

### Test Case 3: Zero Discordant Cell for Retrieval ($c = 0$, $b = 25$)
- **Condition:** Full Hybrid wins all 25 discordant cases; Retrieval-only wins 0.
- **Pipeline Behavior:** The engine avoids runtime `ZeroDivisionError` when computing $\psi = b/c$. The point estimate is correctly reported as `"inf"`, the exact one-sided Clopper-Pearson lower bound is evaluated ($[0.863, 1.000]$ on $\pi$, yielding $\psi_{\text{low}} = 6.299$), and the exact McNemar test evaluates $p = 2 \times (0.5)^{25} \approx 5.96 \times 10^{-8} \le 0.05$.
- **Interval Check:** The Agresti-Min risk difference interval evaluates to $[+24.72\%, +49.62\%]$, properly excluding zero and confirming statistical significance.

### Test Case 4: Zero Discordant Cell for Hybrid ($b = 0$, $c = 25$)
- **Condition:** Retrieval-only wins all 25 discordant cases; Full Hybrid wins 0.
- **Pipeline Behavior:** Correctly evaluates odds ratio $\psi = 0.0$, sets $\psi_{\text{high}} = 0.159$, evaluates exact two-sided $p = 5.96 \times 10^{-8}$, and computes $\Delta = -38.46\%$.

### Test Case 5: Balanced Discordance ($b = 10, c = 10$)
- **Condition:** Equal disagreements ($n_d = 20$).
- **Pipeline Behavior:** Evaluates exact binomial $p = 1.0000$, $\Delta = 0.0\%$, and Agresti-Min 95% interval $[-9.95\%, +9.95\%]$, spanning zero symmetrically.

### Test Case 6: Strong Practical Advantage ($b = 20, c = 5, N = 85$)
- **Condition:** Hybrid wins 20 cases, Retrieval wins 5. $\hat{\Delta} = +17.65\%$, which crosses the $+15.0\%$ threshold.
- **Pipeline Behavior:** Evaluates exact McNemar $p = 0.004077 \le 0.05$. The Agresti-Min interval is $[+4.82\%, +29.14\%]$, which excludes zero. The pipeline correctly flags this synthetic scenario as meeting **both** statistical significance ($p \le 0.05$) and practical significance ($\hat{\Delta} \ge +15.0\%$).

---

## 3. Resilience to Missing or Invalid Prediction Data

To prevent test-phase failures due to unexpected model errors or malformed outputs, the pipeline was tested against missing-data scenarios:

1. **Missing Candidate Prediction:** If Full Hybrid or Retrieval-only returns an empty ranking or throws a timeout, the case is deterministically assigned:
   - Rank: $99$
   - Reciprocal Rank: $0.0$
   - Correctness Indicator: $Y_i = 0$ (Incorrect)
2. **Invalid Candidate Name:** If a system outputs an unrecognized string outside the 6 candidate actor names, it is flagged as invalid and scored as incorrect ($Y_i = 0$).
3. **No Imputation Rule:** The pipeline enforces a strict zero-imputation policy. Missing cases are never replaced with mean predictions or discarded from the denominator.

**Conclusion:** The evaluation and scoring pipeline is validated, deterministic, and fully ready for frozen prospective benchmark execution.
