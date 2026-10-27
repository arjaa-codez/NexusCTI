# NexusCTI Phase 9 — Sample Size & Statistical Power Justification

**Document Version:** 1.0 (Pre-Registration Protocol Freeze)  
**Date:** 2026-10-11  
**Experiment Root:** `experiments/phase9_benchmark_preparation_20261011_020400/`  

---

## Executive Summary

Phase 9 establishes and pre-registers the sample size targets for the upcoming prospective NexusCTI benchmark evaluation:
- **Task A (Closed-Set Primary Evaluation):** **$N = 100$ eligible canonical campaign cases**
- **Task B (Open-Set Abstention Evaluation):** **$N = 30$ eligible canonical campaign cases**
- **Development Partition (Quarantined Pre-Test):** **$N = 15$ canonical campaign cases**
- **Total Benchmark Pool:** **$N = 145$ independent campaign units**

This sample size is justified through exact analytical power calculations, sensitivity modeling, and risk management against small-sample discreteness penalties.

---

## 1. Primary Planning Parameters & Mathematical Framework

The primary comparison evaluates paired binary correctness ($Y_{H,i}, Y_{R,i} \in \{0, 1\}$) across $N$ independently sampled cyber threat campaigns.

The statistical power of the exact two-sided McNemar test at $\alpha = 0.05$ is governed by two independent population parameters:
1. **Discordance Rate ($q$):** $P(Y_{H,i} \ne Y_{R,i}) = \frac{n_d}{N}$.
   - *Planning Assumption:* $q = 0.25$ (the systems are assumed to disagree on 1 out of every 4 campaigns).
   - In Phase 8, the sample estimate was $\hat{q} = 7/24 = 29.17\%$ (95% CI $[12.6\%, 51.1\%]$). Planning at $q = 0.25$ provides a conservative buffer against regression to lower discordance.
2. **Conditional Win Rate ($\theta$):** $P(Y_{H,i} = 1 \mid Y_{H,i} \ne Y_{R,i}) = \frac{b}{b + c}$.
   - *Planning Assumption:* $\theta = 0.80$ (when the systems disagree, Full Hybrid wins 4 out of 5 cases, corresponding to an odds ratio $\psi = 4.0$).
   - In Phase 8, the sample estimate was $\hat{\theta} = 6/7 = 85.71\%$. Planning at $\theta = 0.80$ avoids assuming that the extreme 6:1 ratio will persist indefinitely.
3. **Implied Marginal Effect Size ($\Delta$):**
   $$\Delta = E[p_{\text{hybrid}} - p_{\text{retrieval}}] = q \times (2\theta - 1) = 0.25 \times (2(0.80) - 1) = 0.25 \times 0.60 = \mathbf{+15.0\%}$$
   This aligns precisely with the pre-registered practical significance threshold of $+15$ percentage points.

---

## 2. Power Curve & Final Sample Size Selection

The exact analytical power of the exact two-sided McNemar test integrates over all possible realizations of $D \sim \text{Binomial}(N, q)$ and $B \mid D \sim \text{Binomial}(D, \theta)$:

```
+--------------------------------------------------------------------------------------------------------+
| PROSPECTIVE EXACT POWER CURVE UNDER PRIMARY PLANNING OBJECTIVE (q = 0.25, θ = 0.80, Δ = +15%)          |
+--------------------------+--------------------+--------------------------------------------------------+
| Candidate Sample Size    | Exact Power (α=.05)| Methodological Evaluation                              |
+--------------------------+--------------------+--------------------------------------------------------+
| N = 24 (Phase 8 Size)    | 15.08%             | Severely underpowered; 84.9% risk of Type II error     |
| N = 40                   | 36.37%             | Inadequate; less than coin-flip detection probability  |
| N = 60                   | 58.09%             | Underpowered; 41.9% risk of false-negative outcome     |
| N = 80                   | 73.68%             | Intermediate floor; close to 80% standard              |
| N = 100 (Selected Target)| 83.67%             | Robustly powered; exceeds 80% scientific standard      |
| N = 120                  | 90.35%             | Highly powered; 90% detection threshold                |
| N = 150                  | 96.01%             | Asymptotically optimal; dimishing returns vs cost      |
+--------------------------+--------------------+--------------------------------------------------------+
```

### Justification for $N = 100$ Selection:
1. **$N = 60$ Was Rejected for Confirmatory Science:** Although earlier phases explored $N = 60$, exact power calculations demonstrate that $N = 60$ achieves only **$58.1\%$ power** under the primary $+15\%$ planning objective. A trial with $58\%$ power has a $41.9\%$ probability of returning an inconclusive result ($p > 0.05$) even if the true system advantage is $+15.0\%$.
2. **$N = 100$ Satisfies the 80% Power Benchmark:** At $N = 100$, exact power reaches **$83.67\%$** (verified by $M = 20,000$ Monte Carlo simulations: $83.06\% \pm 0.27\%$). This provides robust assurance that genuine improvements of $+15.0\%$ or greater will be reliably detected.
3. **Contingency Floor ($N = 80$):** If real-world CTI report curation constraints restrict the final eligible pool, $N = 80$ ($73.7\%$ power) represents the absolute minimum permissible floor. Any evaluation with $N < 80$ is formally classified as an exploratory pilot.

---

## 3. Sensitivity Modeling Across Less Favorable Scenarios

Power is strictly conditional on planning assumptions. We evaluated sensitivity across less favorable conditions:

```
+--------------------------------------------------------------------------------------------------------+
| SENSITIVITY OF POWER AT N = 100 ACROSS VARYING POPULATION PARAMETERS                                   |
+---------------------------------------+-----------+---------------+------------------------------------+
| Population Scenario                   | Implied Δ | Exact Power   | Risk & Interpretation              |
+---------------------------------------+-----------+---------------+------------------------------------+
| Null Hypothesis (θ = 0.50, q = 0.25)  |   0.0%    | 2.97% (Type I)| Proper conservative error control  |
| Modest Effect (θ = 0.60, q = 0.25)    |  +5.0%    | 11.92%        | Underpowered for small effects     |
| Moderate Effect (θ = 0.70, q = 0.25)  | +10.0%    | 43.99%        | 56.0% risk of Type II error        |
| Primary Objective (θ = 0.80, q = 0.25)| +15.0%    | 83.67%        | Adequately powered (≥80%)          |
| Phase 8 Baseline (θ=0.857, q=0.29)    | +20.8%    | 98.00%        | Overwhelmingly powered             |
| Lower Discordance (θ=0.80, q = 0.20)  | +12.0%    | 71.69%        | Moderately powered                 |
| Low Discordance (θ=0.80, q = 0.15)    |  +9.0%    | 57.89%        | Underpowered due to low discordance|
+---------------------------------------+-----------+---------------+------------------------------------+
```

### Critical Takeaways:
- **Sensitivity to Discordance:** If the two systems agree more frequently than anticipated ($q = 0.20$ instead of $0.25$), power drops to $71.7\%$. In that scenario, achieving $80\%$ power would require scaling to $N = 120$.
- **Sensitivity to Effect Size:** If the true advantage is moderate ($\Delta = +10.0\%$, $\theta = 0.70$), power at $N = 100$ drops to $44.0\%$. Detecting a $+10\%$ effect with $80\%$ power requires $N \ge 220$ campaigns.
- **The Planning Fallacy:** These calculations represent **planning models**, not physical guarantees. A sample size of $N = 100$ does not guarantee statistical significance.

---

## 4. Why Power Cannot Be Inferred from Discordant Pairs Alone

A common mistake in paired trial planning is assuming that one only needs to collect data until observing a fixed number of discordant pairs (e.g., $n_d = 20$).

This practice is invalid because:
1. **Optional Stopping Bias:** Terminating data collection dynamically when $n_d$ reaches a threshold inflates the Type I error rate well above $\alpha = 0.05$.
2. **Marginal Rate Confounding:** The marginal accuracy and risk difference depend directly on total $N$. The standard error of the risk difference $SE = \frac{1}{N} \sqrt{n_d - \frac{(b-c)^2}{N}}$ shrinks with $N$, not just $n_d$.
3. **Discreteness Barrier:** When $N$ is small, the probability that $D \le 5$ (where rejection is mathematically impossible) is high ($42.1\%$ at $N=24$). Fixing $N = 100$ guarantees that $P(D \le 5) = 1.3 \times 10^{-6}$, virtually eliminating the discreteness power penalty.
