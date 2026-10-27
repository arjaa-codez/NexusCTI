# NexusCTI Phase 8.2 — Prospective Power Analysis & Scenario Assumptions

**Audit Date:** 2026-10-11  
**Experiment Root:** `experiments/phase8_2_power_and_verification_20261011_014200/`  
**Statistical Framework:** Exact Two-Sided McNemar Test ($\alpha = 0.05$) via Exact Binomial Integration and Monte Carlo Simulation ($M = 10,000$ trials, seed=42)  

---

## 1. Mathematical Framework and Planning Parameters

In an independent paired evaluation of $N$ unseen campaign cases, each case yields a binary outcome for Full Hybrid ($Y_{H,i} \in \{0, 1\}$) and Retrieval-only ($Y_{R,i} \in \{0, 1\}$).

The paired outcomes depend on two independent population parameters:
1. **Discordance Rate ($q$):** The probability that the two systems disagree on a given campaign:
   $$q = P(Y_{H,i} \ne Y_{R,i}) = P(\text{discordance})$$
   In Phase 8, the sample estimate was $\hat{q} = \frac{7}{24} = 29.17\%$, with 95% Clopper-Pearson CI $[12.62\%, 51.09\%]$.
2. **Conditional Hybrid-Win Probability ($\theta$):** The probability that Full Hybrid is correct given that the two systems disagree:
   $$\theta = P(Y_{H,i} = 1 \mid Y_{H,i} \ne Y_{R,i}) = \frac{b}{b + c}$$
   - Under $H_0$, $\theta = 0.50$ (no advantage).
   - In Phase 8, the observed sample estimate was $\hat{\theta} = \frac{6}{7} = 85.71\%$, with 95% Clopper-Pearson CI $[42.13\%, 99.64\%]$.

The expected marginal Top-3 accuracy gain is directly governed by $q$ and $\theta$:
$$\Delta = E[p_{\text{hybrid}} - p_{\text{retrieval}}] = q \times (2\theta - 1)$$

---

## 2. Prospective Scenario Definitions

| Scenario Name | Discordance ($q$) | Conditional Win ($\theta$) | Implied $\Delta$ | Interpretation |
|:---|:---:|:---:|:---:|:---|
| **Scenario 0: Null** | Any $q$ (0.15–0.29) | **0.50** | **0.0%** | Full Hybrid provides zero true benefit over Retrieval-only ($H_0$). Tests Type I error control. |
| **Scenario 1: Modest** | 0.20–0.25 | **0.60** | **+4.0% to +5.0%** | Hybrid provides a minor edge, correcting 3 errors for every 2 it introduces. |
| **Scenario 2: Moderate** | 0.25 | **0.70** | **+10.0%** | Hybrid provides a solid advantage, correcting 7 errors for every 3 retrieval errors. |
| **Scenario 3: Large / Target**| 0.25 | **0.80** | **+15.0%** | Hybrid reliably catches complex TTPs, meeting the pre-registered practical bar. |
| **Scenario 4: Observed Phase 8**| 0.2917 | **0.8571** | **+20.83%** | Direct continuation of the exact 6:1 discordance pattern observed on $N=24$. |

*Note: All scenarios are explicitly designated as planning assumptions, not established population facts.*

---

## 3. Power Matrix Summary Table (Exact Two-Sided McNemar at $\alpha = 0.05$)

The table below summarizes the exact prospective power across sample sizes $N \in \{24, 40, 60, 80, 100, 150, 200\}$ computed via exact binomial integration $\sum_{d=1}^N P(D=d) \sum_{b \in \mathcal{R}_d} P(B=b \mid D=d)$ and verified by $M = 10,000$ Monte Carlo simulations:

```
+------------------------------------+--------+--------+--------+--------+--------+---------+---------+
| Scenario                           | N = 24 | N = 40 | N = 60 | N = 80 | N = 100| N = 150 | N = 200 |
+------------------------------------+--------+--------+--------+--------+--------+---------+---------+
| Null (θ = 0.50, q = 0.25) [Type I] |  1.3%  |  2.2%  |  2.7%  |  3.0%  |  3.0%  |   3.4%  |   3.7%  |
| Modest (θ = 0.60, q = 0.25, Δ = 5%)|  2.4%  |  4.9%  |  7.6%  |  9.9%  | 11.9%  |  18.4%  |  25.0%  |
| Moderate (θ=0.70, q=0.25, Δ = 10%) |  6.3%  | 15.0%  | 25.7%  | 35.4%  | 44.0%  |  64.3%  |  78.7%  |
| Large / Bar (θ=0.80, q=0.25, Δ=15%)| 15.1%  | 36.4%  | 58.1%  | 73.7%  | 83.7%  |  96.0%  |  99.2%  |
| Phase 8 Baseline (θ=0.857, q=0.29) | 32.0%  | 63.2%  | 85.2%  | 94.4%  | 98.0%  |  99.9%  | 100.0%  |
+------------------------------------+--------+--------+--------+--------+--------+---------+---------+
```

### Key Statistical Takeaways:
1. **The Inadequacy of $N = 24$ Explained:** At $N = 24$, even under the optimistic Phase 8 observed effect ($\theta = 0.8571, q = 0.2917$), statistical power was only **32.0%**, meaning there was a **68.0% probability of failing to reject $H_0$** strictly due to small sample size and discreteness.
2. **Evaluation of the Proposed $N = 60$ Target:**
   - Under the observed Phase 8 rate ($\theta = 0.8571$), $N = 60$ achieves **85.2% power**.
   - However, under the more realistic Large Advantage benchmark ($\theta = 0.80, q = 0.25, \Delta = 15\%$), $N = 60$ achieves **58.1% power**, which falls well below the standard 80% threshold.
   - If the true advantage is Moderate ($\theta = 0.70, \Delta = 10\%$), $N = 60$ achieves only **25.7% power**.
3. **Requirement for Adequate Power:** To reliably achieve $\ge 80\%$ power under a $+15\%$ gain ($\theta = 0.80, q = 0.25$), the benchmark requires **$N \ge 90$ to $100$ independent cases**. To achieve $\ge 80\%$ power under a $+10\%$ gain ($\theta = 0.70, q = 0.25$), the benchmark requires **$N \ge 200$ cases**.

---

## 4. Statistical Significance vs. Practical Effect Probability

A fundamental principle of decision science is distinguishing between two distinct questions:
1. **Statistical Power ($P(\text{reject } H_0 \mid \theta, q)$):** The probability that the exact hypothesis test achieves $p \le 0.05$.
2. **Practical Effect Exceedance ($P(\hat{\Delta} \ge 15\% \mid \theta, q)$):** The probability that the observed sample risk difference meets or exceeds the practical threshold of $+15$ percentage points.

```
+--------------------------------------------------------------------------------------------------------+
| PROBABILITY OF MEETING PRACTICAL BAR (Δ_hat ≥ 15%) vs. REJECTING NULL (p ≤ 0.05) [q = 0.25, θ = 0.80] |
+--------------------------------------------------------------------------------------------------------+
| Sample Size (N)       P(Δ_hat ≥ 15%) [Practical Bar]       Exact Power (p ≤ 0.05) [Significance]       |
+--------------------------------------------------------------------------------------------------------+
| N = 24                            51.1%                                   15.1%                        |
| N = 40                            56.2%                                   36.4%                        |
| N = 60                            55.1%                                   58.1%                        |
| N = 80                            54.4%                                   73.7%                        |
| N = 100                           53.9%                                   83.7%                        |
| N = 150                           49.8%                                   96.0%                        |
| N = 200                           52.8%                                   99.2%                        |
+--------------------------------------------------------------------------------------------------------+
```

### Why These Concepts Diverge:
- In small samples ($N = 24$), sampling variance is huge. Even when an experiment observes $\hat{\Delta} = +20.83\%$, the standard error is so wide that the 95% confidence interval spans $[-3.27\%, +36.60\%]$ and the exact test yields $p = 0.1250$. Thus, a study can easily meet a practical bar while remaining statistically inconclusive.
- Conversely, in very large samples ($N \ge 500$), an uninterestingly small effect ($\Delta = +3\%$) will easily reject $H_0$ ($p < 0.001$), but will almost never meet the practical $+15\%$ threshold.
- For a rigorous benchmark, both criteria must be prespecified and evaluated jointly: an architecture is only superior if it rejects the null hypothesis **AND** demonstrates a clinically meaningful effect size whose lower confidence bound or point estimate meets the practical threshold.
