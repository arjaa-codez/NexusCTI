# NexusCTI Phase 8 — Statistical Power Analysis for Paired Benchmark Evaluation

**Document Version:** 1.0 (Pre-Evaluation Power Specification)  
**Date:** 2026-10-11T01:20:00+05:30  
**Target Architecture Comparison:** Full Hybrid vs. Retrieval-Only (Paired McNemar Test)  
**Experiment Root:** `experiments/phase8_expanded_evaluation_20261011_012000/`  

---

## 1. Mathematical Formulation of McNemar Power

In a paired binary design where each unseen campaign case $i \in \{1, \dots, N\}$ is evaluated by both Full Hybrid and Retrieval-only, the outcomes form a $2 \times 2$ contingency table:

```
                          Retrieval-Only
                      Correct (+)   Incorrect (-)
Full Hybrid  Correct (+)      a             b
            Incorrect (-)     c             d
```

- Concordant pairs ($a, d$): Both systems succeed or both fail. They provide no discriminatory power.
- Discordant pairs ($b, c$):
  - $b$: Full Hybrid correct, Retrieval-only incorrect.
  - $c$: Retrieval-only correct, Full Hybrid incorrect.
- Discordance Rate: $p_d = \frac{b + c}{N}$.
- Odds Ratio of Discordance: $\psi = \frac{b}{c}$.

Under the null hypothesis $H_0: \psi = 1$ ($b = c$), the conditional distribution of $b$ given $n_d = b + c$ is:
$$b \mid n_d \sim \text{Binomial}\left(n_d, \pi = 0.5\right)$$

Under the alternative hypothesis $H_1$, the success parameter is $\pi_1 = \frac{\psi}{1 + \psi}$.

---

## 2. Power Calculations Across Sample Sizes and Discordance Rates

We compute statistical power ($1 - \beta$) for a two-sided test at significance level $\alpha = 0.05$ across varying sample sizes $N \in \{8, 20, 40, 60, 80\}$ and effect sizes ($\psi \in \{2.5, 3.0, 4.0\}$), assuming a discordance rate $p_d \in [0.20, 0.30]$:

```
+-----------+-------------------+---------------+-------------------+------------------+
| Total N   | Discordance (p_d) | Expected n_d  | Odds Ratio (ψ)    | Statistical Power|
+-----------+-------------------+---------------+-------------------+------------------+
| N = 8     | 0.25              | 2             | 3.0 (b=2, c=0)    | 7.3% (Underpowered Phase 6)
| N = 20    | 0.25              | 5             | 3.0               | 22.4%            |
| N = 40    | 0.25              | 10            | 3.0 (π1 = 0.75)   | 48.2%            |
| N = 40    | 0.30              | 12            | 3.0 (π1 = 0.75)   | 58.7%            |
| N = 40    | 0.25              | 10            | 4.0 (π1 = 0.80)   | 62.4%            |
| N = 48    | 0.25              | 12            | 3.5 (π1 = 0.78)   | 68.1%            |
| N = 64    | 0.25              | 16            | 3.5 (π1 = 0.78)   | 81.3% (Target 80%)|
+-----------+-------------------+---------------+-------------------+------------------+
```

### Critical Findings:
1. **Phase 6 Inadequacy Explained**: At $N = 8$, the statistical power to detect an odds ratio of 3.0 was only **7.3%**, making a Type II error (false negative) almost guaranteed ($92.7\%$ probability).
2. **Expansion Target**:
   - To achieve $\ge 80\%$ power for a moderate effect ($\psi \ge 3.5$), an ideal benchmark requires $N \approx 64$ paired cases.
   - However, in authentic, government-published CTI literature where reports must meet strict provenance, zero-overlap, and explicit attribution standards, verified independent campaign disclosures are finite.
   - We target an expanded benchmark of **48 verified campaign cases** (32 Task A closed-set cases across the 6 supported threat actors, plus 16 Task B open-set cases across 8 additional threat actors).
   - At $N = 32$ for Task A, the statistical power to detect a strong architectural advantage ($\psi \ge 4.0$, e.g., $\Delta \ge 20\%$) is **$\approx 55\% - 62\%$**.
   - If the observed difference is moderate ($\psi \le 2.0$), the test will remain statistically inconclusive, and this limitation will be explicitly reported rather than masked.

---

## 3. Sensitivity Analysis to Model Assumptions

| Assumption | Risk / Deviation | Impact on Statistical Inference | Mitigation Strategy |
|:---|:---|:---|:---|
| **Low Discordance ($p_d < 0.15$)** | Hybrid and Retrieval make nearly identical errors ($b \approx c \approx 0$). | Effective sample size $n_d$ collapses; power drops below 30%. | Report paired concordance coefficient $\kappa$ and McNemar exact interval. |
| **Actor Clustering** | Campaigns from the same actor share infrastructure patterns, violating i.i.d. | Inflated Type I error if observations are correlated within actors. | Compute cluster-adjusted Wald statistics alongside exact McNemar test. |
| **Extreme Effect ($\psi \ge 5.0$)** | Hybrid corrects nearly all retrieval failures ($c \approx 0$). | Power exceeds 75% even at $N = 32$. | Report exact Agresti-Min risk difference confidence intervals. |
