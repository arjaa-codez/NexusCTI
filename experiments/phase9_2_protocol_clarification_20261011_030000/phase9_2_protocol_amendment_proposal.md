# NexusCTI Phase 9.2 — Protocol Amendment Proposal: Statistical Decision Rule

**Document Version:** 1.0 (Formal Protocol Amendment Proposal)  
**Date:** 2026-10-11  
**Experiment Root:** `experiments/phase9_2_protocol_clarification_20261011_030000/`  
**Target Baseline (Read-Only):** `experiments/phase9_benchmark_preparation_20261011_020400/phase9_protocol_freeze.md`  
**Power Recheck Manifest:** [`joint_decision_rule_power_recheck.csv`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_2_protocol_clarification_20261011_030000/joint_decision_rule_power_recheck.csv)

---

## Executive Summary

Phase 9.1 uncovered a fundamental structural power deficit in the frozen Phase 9 evaluation protocol:
- The frozen protocol asserted that $N = 100$ campaigns provided **$83.67\%$ power** to satisfy the declared success rule.
- However, the declared success rule required **BOTH**:
  1. Exact two-sided McNemar test $p \le 0.05$.
  2. Observed sample paired risk difference $\hat{\Delta} = \frac{b - c}{N} \ge +0.15$.
- Because the planning assumptions ($q = 0.25$ discordance, $\theta = 0.80$ conditional win rate) specify a true population risk difference of exactly $\Delta = +0.15$, the sample estimator $\hat{\Delta}$ is centered at $0.15$.
- By the Central Limit Theorem, $P(\hat{\Delta} \ge 0.15) \to 50\%$ as $N \to \infty$. Consequently, the joint probability of satisfying **BOTH** criteria is only **$53.91\%$** at $N = 100$.

This amendment proposal outlines two mutually exclusive, methodologically rigorous protocol paths for resolving this issue prior to observing test predictions.

---

## 1. Mathematical Problem Formulation & Independent Power Recheck

Let $Y_{H,i}, Y_{R,i} \in \{0, 1\}$ denote paired binary Top-3 correctness across $N$ independently sampled cyber threat campaigns.
The population discordance rate is $q = P(Y_{H,i} \ne Y_{R,i})$, and the conditional win rate when systems disagree is $\theta = P(Y_{H,i} = 1 \mid Y_{H,i} \ne Y_{R,i}) = \frac{b}{b + c}$.
The marginal population risk difference is:
$$\Delta = E[Y_{H,i} - Y_{R,i}] = q(2\theta - 1)$$

Under the Phase 9 primary planning baseline:
$$q = 0.25, \quad \theta = 0.80 \implies \Delta = 0.25(2(0.80) - 1) = \mathbf{+15.0\%}$$

### Independent Verification of Probabilities at $N = 100$:
1. **Hypothesis Test Power Alone ($p_{\text{McNemar}} \le 0.05, \hat{\Delta} > 0$):** **$83.674\%$** (Monte Carlo $M=100,000$: $83.797\% \pm 0.117\%$) — **VERIFIED**.
2. **Observed Hurdle Probability Alone ($\hat{\Delta} \ge +0.15$):** **$53.911\%$** (Monte Carlo $M=100,000$: $54.141\% \pm 0.158\%$) — **VERIFIED**.
3. **Joint Success Probability (BOTH Conditions Met):** **$53.911\%$** (Monte Carlo $M=100,000$: $54.141\% \pm 0.158\%$) — **VERIFIED**.

> [!CRITICAL]
> **Definitive Epistemological Fact:**  
> The Phase 9 reported power of $83.67\%$ is the **test-only rejection power**, **NOT** the joint decision-rule power. Sizing at $N = 100$ leaves the evaluation with an unacknowledged **$46.1\%$ risk of Type II failure**, even if Full Hybrid achieves its exact target advantage of $+15.0\%$!

---

## 2. Protocol Alternative A: Retain Both Decision Conditions

### 2.1 Specification
Alternative A retains the original dual-condition decision rule without alteration:
$$\text{Full Hybrid Superiority Declared } \iff (p_{\text{McNemar}} \le 0.05) \land (\hat{\Delta} \ge +0.150)$$

### 2.2 Probabilistic Performance Across Scenarios
From [`joint_decision_rule_power_recheck.csv`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_2_protocol_clarification_20261011_030000/joint_decision_rule_power_recheck.csv):

```
+---------------------------------------------------------------------------------------------------------------+
| ALTERNATIVE A: JOINT DECISION-RULE POWER ACROSS PLAUSIBLE POPULATION REGIMES                                  |
+-------+------+-------+-----------+---------------+--------------------+------------------+--------------------+
| N     | q    | θ     | True Δ    | McNemar Power | Δ_hat >= 0.15 Prob | Joint Power (A)  | Meets 80% Standard |
+-------+------+-------+-----------+---------------+--------------------+------------------+--------------------+
| 100   | 0.25 | 0.80  | +15.0%    | 83.67%        | 53.91%             | 53.91%           | NO (Sub-coin flip) |
| 150   | 0.25 | 0.80  | +15.0%    | 96.01%        | 49.78%             | 49.78%           | NO                 |
| 200   | 0.25 | 0.80  | +15.0%    | 99.20%        | 52.77%             | 52.77%           | NO                 |
| 300   | 0.25 | 0.80  | +15.0%    | 99.97%        | 52.26%             | 52.26%           | NO                 |
| 100   | 0.25 | 0.85  | +17.5%    | 94.75%        | 73.78%             | 73.78%           | NO                 |
| 100   | 0.25 | 0.87  | +18.5%    | 96.94%        | 80.52%             | 80.52%           | YES (Requires 87%) |
| 100   | 0.25 | 0.90  | +20.0%    | 99.08%        | 88.65%             | 88.65%           | YES                |
| 58    | 0.25 | 0.90  | +20.0%    | 89.02%        | 83.86%             | 81.11%           | YES (Achieved N=58)|
+-------+------+-------+-----------+---------------+--------------------+------------------+--------------------+
```

### 2.3 Methodological Analysis of Alternative A:
- **The Ceiling Mechanism:** When the true population mean equals the hurdle ($\Delta = 0.15$), sample estimates fluctuate symmetrically around $0.15$. Exactly $\approx 50\%$ of trials will realize $\hat{\Delta} < 0.15$ (e.g., $14/100 = 14.0\%$), causing an automatic failure of Condition 2 despite statistically significant superiority ($p = 0.021$).
- **Requirements for 80% Power:** To reach $\ge 80\%$ joint power under Alternative A, one must assume that the true effect size is substantially larger than $+15.0\%$:
  * At $N = 100$: Requires true win rate $\theta \ge 0.87$ (true effect $\Delta \ge +18.5\%$, odds ratio $\psi \ge 6.69$).
  * Or if true effect is $\Delta = +20.0\%$ (the Phase 8 baseline of $17/24$ vs $12/24$, $\theta = 0.90$), then $N = 58$ is sufficient.
- **Scientific Limitation:** Inflating the assumed effect size post-hoc simply to claim $80\%$ joint power violates ethical planning standards. If the genuine planning assumption remains $\Delta = +15.0\%$, selecting Alternative A means accepting that the study has only a **$53.9\%$ detection probability**.

---

## 3. Protocol Alternative B: Treat +15% as a Planning Target (MDE)

### 3.1 Specification
Alternative B separates the **confirmatory hypothesis decision** from the **practical effect size estimation**, adhering to standard biostatistical and clinical trial governance (e.g., ICH E9 guideline on statistical principles for clinical trials, Section 3.5):

1. **Confirmatory Statistical Superiority Rule (Primary Hypothesis Test):**
   Full Hybrid is declared statistically superior to Retrieval-only if and only if:
   $$p_{\text{McNemar}} \le 0.05 \quad (\text{two-sided exact binomial test on discordant pairs}) \quad \land \quad \hat{\Delta} > 0$$
   *Power under Primary Planning Baseline ($q=0.25, \theta=0.80, N=100$):* **$83.674\%$** (**VERIFIED**).

2. **Practical Significance & Estimation Criteria (Dual-Tier Reporting):**
   The study was sized at $N = 100$ specifically to guarantee $>80\%$ power to detect a **Minimal Detectable Effect (MDE) of $+15.0$ percentage points**.
   The observed effect size $\hat{\Delta}$ and its **95% Agresti-Min Paired Pseudocount Confidence Interval** $[\hat{\Delta}_L, \hat{\Delta}_U]$ are reported to establish practical significance under three pre-specified tiers:
   - **Strong Practical Superiority:** $p_{\text{McNemar}} \le 0.05$ AND the lower bound of the 95% CI exceeds meaningful nonzero progress ($\hat{\Delta}_L \ge +0.050$), with the point estimate consistent with the planning target ($\hat{\Delta} \ge +0.150$).
   - **Moderate Practical Superiority:** $p_{\text{McNemar}} \le 0.05$ AND the 95% CI covers the planning target ($+0.150 \in [\hat{\Delta}_L, \hat{\Delta}_U]$), even if the point estimate realized is marginally below $0.150$ (e.g. $\hat{\Delta} = +0.130$, 95% CI $[+0.038, +0.222]$).
   - **Statistically Significant but Minor:** $p_{\text{McNemar}} \le 0.05$, but the entire 95% CI falls below the planning target ($\hat{\Delta}_U < +0.150$).
   - **Inconclusive / Failed:** $p_{\text{McNemar}} > 0.05$.

### 3.2 Power Recalculation for Alternative B:
- Under Alternative B, the binary hypothesis test power under $q = 0.25, \theta = 0.80$ is **$83.67\%$**.
- The pre-evaluation sample size justification of $N = 100$ remains **mathematically sound, valid, and fully powered**.
- The protocol avoids the self-inflicted $46.1\%$ false-negative trap of a double gate on noisy sample realizations.

---

## 4. Comparative Evaluation & Formal Recommendation

```
+---------------------------------------------------------------------------------------------------------------+
| COMPARATIVE EVALUATION MATRIX: ALTERNATIVE A VERSUS ALTERNATIVE B                                             |
+--------------------------+-----------------------------------+------------------------------------------------+
| Evaluation Dimension     | Alternative A (Retain Dual Gate)  | Alternative B (MDE Target + CI Estimation)     |
+--------------------------+-----------------------------------+------------------------------------------------+
| Primary Decision Rule    | p <= 0.05 AND Δ_hat >= +0.150     | p <= 0.05 AND Δ_hat > 0                        |
| True Power at N = 100    | 53.91% (Severe Deficit)           | 83.67% (Adequately Powered >= 80%)             |
| Risk of False Negative   | 46.09% (Near coin flip)           | 16.33% (Controlled Type II error)              |
| Planning MDE Role        | Hard empirical sample filter      | Minimal Detectable Effect guiding sample size  |
| Alignment with Standards | Project-specific ad-hoc hurdle    | Standard empirical / biostatistical convention |
| Handling of Borderlines  | Rejects trial if Δ_hat = +0.140   | Interprets Δ_hat = +0.140 via 95% CI           |
| Ethical Integrity        | Requires inflating θ post-hoc     | Retains honest planning assumption θ = 0.80    |
+--------------------------+-----------------------------------+------------------------------------------------+
```

### Official Auditor Recommendation:
**AMEND PROTOCOL TO ADOPT ALTERNATIVE B.**

**Rationale:**  
Alternative B restores scientific coherence to the Phase 9 evaluation. It honors the original $+15.0\%$ practical threshold by treating it as what it mathematically is: the **Minimal Detectable Effect** that governed the calculation of $N = 100$. Forcing $+15.0\%$ to serve simultaneously as an empirical sample gate cuts the statistical power to $53.9\%$, invalidating the sample size justification. Alternative B protects the confirmatory trial against false negatives while rigorously reporting the Agresti-Min 95% confidence interval to determine whether the observed effect achieves practical relevance.
