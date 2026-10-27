# NexusCTI Power Statement Audit & Reproduction Report

**Document Version:** 1.0 (Independent Mathematical Verification)  
**Date:** 2026-10-11  
**Project Root:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI`  
**Experiment Root:** `experiments/phase9_3_final_authorization_20261011/`  
**Data Artifact:** `power_statement_audit_grid.csv`  
**Executable Script:** `run_power_audit.py`

---

## 1. Executive Summary & Verification Classification

| Metric / Parameter | Value / Finding | Audit Classification | Supporting Evidence |
| :--- | :--- | :--- | :--- |
| **Exact McNemar Power ($p \le 0.05$)** | **83.674%** | **REPRODUCED** | `run_power_audit.py`, $100{,}000$ iterations |
| **Directional Superiority ($b > c$)** | **99.988%** | **REPRODUCED** | Monte Carlo simulation grid |
| **Alternative B Decision Rule Power** | **83.674%** | **REPRODUCED** | Combined $p \le 0.05 \land \hat{\Delta} > 0$ |
| **Version 1.0 Dual Decision Rule Power** | **53.911%** | **REPRODUCED** | Combined $p \le 0.05 \land \hat{\Delta} \ge 0.150$ |
| **Agresti–Min 95% CI Coverage** | **95.028%** | **REPRODUCED** | Covers target $\Delta = +0.150$ |
| **Agresti–Min CI Lower Bound $> 0$** | **88.420%** | **REPRODUCED** | Confirms strictly positive lower bound |

---

## 2. Statistical Model and Assumption Verification

### 2.1 Parameter Specification
The prospective power analysis models paired binary classification outcomes across $N = 100$ independent closed-set campaigns. Out of $N$ pairs, the joint distribution of $(Y_{1,i}, Y_{2,i})$ is governed by a paired multinomial distribution characterized by:
- Discordance rate: $q = p_{12} + p_{21} = P(Y_1 \ne Y_2) = 0.25$.
- Expected discordant pairs: $\mathbb{E}[n_d] = N \times q = 100 \times 0.25 = 25$.
- Conditional superiority parameter: $\theta = \frac{p_{12}}{p_{12} + p_{21}} = P(Y_1 = 1 \mid Y_1 \ne Y_2) = 0.80$.

### 2.2 Implied Marginal Parameters
Under these foundational assumptions:
- Probability Full Hybrid wins: $p_{12} = q \times \theta = 0.25 \times 0.80 = 0.200$ (expected count $b = 20$).
- Probability Retrieval-only wins: $p_{21} = q \times (1 - \theta) = 0.25 \times 0.20 = 0.050$ (expected count $c = 5$).
- **Implied marginal risk difference:**
  $$\Delta = p_{12} - p_{21} = 0.200 - 0.050 = +0.150 \quad (+15.0 \text{ percentage points})$$
- **Implied conditional odds ratio:**
  $$\psi = \frac{p_{12}}{p_{21}} = \frac{\theta}{1 - \theta} = \frac{0.80}{0.20} = 4.000$$

These mathematical derivations confirm that the Phase 9 planning parameters $(q = 0.25, \theta = 0.80)$ uniquely and unambiguously imply a true marginal effect of $+15.0$ percentage points.

---

## 3. Disaggregated Power and Operating Characteristics

To provide complete statistical clarity, power is evaluated under each separate decision criterion without conflating composite rules:

```
+---------------------------------------------------------------------------------------------------------+
| OPERATING CHARACTERISTICS OF EVALUATION DECISION RULES (N = 100, q = 0.25, theta = 0.80)                |
+-------------------------------------------------------------+-------------+-------------+---------------+
| Decision Criterion                                          | Sample Size | Power (%)   | Status        |
+-------------------------------------------------------------+-------------+-------------+---------------+
| 1. Exact McNemar Test Alone (p <= 0.05)                     | N = 100     | 83.674%     | REPRODUCED    |
| 2. Directional Superiority Condition Alone (b > c)          | N = 100     | 99.988%     | REPRODUCED    |
| 3. Version 2.0 Confirmatory Rule (p <= 0.05 AND b > c)      | N = 100     | 83.674%     | REPRODUCED    |
| 4. Sample Magnitude Threshold Alone (Δ_hat >= +0.150)       | N = 100     | 58.740%     | REPRODUCED    |
| 5. Version 1.0 Old Dual Rule (p <= 0.05 AND Δ_hat >= +0.150)| N = 100     | 53.911%     | REPRODUCED    |
| 6. Agresti-Min 95% Confidence Interval Coverage of Δ = 0.15 | N = 100     | 95.028%     | REPRODUCED    |
| 7. Agresti-Min 95% CI Lower Bound Strictly Positive (> 0)   | N = 100     | 88.420%     | REPRODUCED    |
+-------------------------------------------------------------+-------------+-------------+---------------+
```

### 3.1 Explanation of Discrepancy in Version 1.0 Dual Rule
Why did Version 1.0 report $83.67\%$ power when its stated rule required $\hat{\Delta} \ge +0.150$?
- The analytical formula for McNemar's test power calculates the probability that $p_{\text{McNemar}} \le 0.05$. At $N=100, q=0.25, \theta=0.80$, this exact value is **$83.674\%$**.
- However, when the empirical point estimator $\hat{\Delta} = (b - c)/N$ is also required to be $\ge +0.150$, the central limit theorem dictates that for an estimator with mean $\mu = +0.150$, approximately $50\%$ of realizations fall below $+0.150$ due to random sampling variance ($\text{SE} \approx 0.048$).
- Conditioning on both $p \le 0.05$ and $\hat{\Delta} \ge +0.150$ dropped joint power to **$53.911\%$**.
- Adopting Alternative B formally designates $+15.0\%$ as the **planning MDE** that motivated the $N=100$ design, while the confirmatory statistical gate is governed by $p \le 0.05$ and $\hat{\Delta} > 0$, correctly restoring statistical power to **$83.674\%$**.

---

## 4. Confidence Interval Operating Characteristics

Under the prespecified Agresti–Min pseudo-observation interval formula:
1. **Nominal Coverage:** Over $100{,}000$ simulated experiments, the 95% Agresti–Min interval successfully contained the true parameter $\Delta = +0.150$ in **$95{,}028$ trials ($95.028\%$)**, validating exact calibration.
2. **Exclusion of Null Effect:** The interval lower bound was strictly greater than zero in **$88{,}420$ trials ($88.420\%$)**, demonstrating that the estimation approach provides even slightly greater sensitivity for ruling out no-effect than the exact two-sided test.
3. **No Inflated Effect Assumptions:** All calculations were performed strictly under $q = 0.25, \theta = 0.80$. No artificially elevated effect size or reduced variance was introduced.

---

## 5. Epistemic Guardrail Statement

- **Power is NOT Operational Utility:** Achieving $83.67\%$ power indicates that if the true effect size is $+15.0$ percentage points with $25\%$ discordance, there is an $83.67\%$ probability that the study will reject the null hypothesis at $\alpha = 0.05$. It is **NOT** a probability that the model will be useful in a production Security Operations Center.
- **Sample Size Does Not Guarantee Significance:** A sample size of $N=100$ does not guarantee that the result will be statistically significant; if the true architecture difference is smaller than $+15\%$ or if discordance is lower than $25\%$, the study may fail to reject $H_0$.
