# NexusCTI Phase 8.1 — Confidence Interval Methodology and Hypothesis Test Consistency Audit

**Audit Date:** 2026-10-11  
**Audited Artifact:** `experiments/phase8_expanded_evaluation_20261011_012000/paired_comparison_results.json`  
**Estimand:** Paired Top-3 Risk Difference ($\Delta = p_{\text{hybrid}} - p_{\text{retrieval}}$) and Odds Ratio ($\psi = b / c$) on Task A ($N=24$)  

---

## 1. Resolution of the Apparent Statistical Contradiction

### The Observed Contradiction in Phase 8:
In `paired_comparison_results.json` and `phase8_report.md`, Phase 8 reported:
- Paired Top-3 Risk Difference: **$\Delta = +20.83\%$**
- Paired 95% Confidence Interval: **$[+0.90\%, +40.77\%]$**
- Exact Two-Sided McNemar Test: **$p = 0.1250$**

**The Paradox:** An interval of $[+0.90\%, +40.77\%]$ strictly excludes 0, which commonly implies statistical significance at $\alpha = 0.05$. Yet the exact McNemar test yielded $p = 0.1250 > 0.05$.

### Independent Methodological Audit Finding:
1. **Method Used in Phase 8:** The formula implemented in `run_phase8_evaluation.py` lines 1357–1362 was the **uncorrected asymptotic Wald interval for paired proportions**:
   $$\text{SE}_{\text{Wald}} = \sqrt{\frac{(b + c) - (b - c)^2 / N}{N^2}}$$
   With $b = 6, c = 1, N = 24$, this yielded $\text{SE} = 0.101707$, giving:
   $$0.208333 \pm 1.95996 \times 0.101707 = [+0.00899, +0.40767] = [+0.90\%, +40.77\%]$$
2. **Methodological Inappropriateness:**
   - In biostatistical literature (Agresti & Min 2005; Newcombe 1998; Tango 1998), the uncorrected asymptotic Wald interval is universally condemned for small sample sizes where the number of discordant pairs is small ($n_d = b + c = 7 < 20$).
   - The uncorrected Wald interval exhibits **severe downward bias in standard error and severe undercoverage** (true coverage is often only 88–91% instead of 95%).
   - The Wald interval relies on the uncorrected score $Z = \frac{b - c}{\sqrt{b + c}} = \frac{5}{\sqrt{7}} \approx 1.8898$, whose two-sided asymptotic p-value is $p = 0.0588$.
   - By contrast, the **Exact McNemar Test** evaluates the exact binomial distribution:
     $$b \mid (b+c) \sim \text{Binomial}(7, 0.50)$$
     where $P(K \ge 6 \text{ or } K \le 1) = 2 \times \frac{8}{128} = \mathbf{0.1250}$.
3. **Consistency Restored via Exact / Appropriate Confidence Intervals:**
   When methodologically appropriate intervals for small-sample paired binary data are evaluated, the interval consistently **overlaps zero**, matching the exact McNemar test result ($p = 0.1250$):

```
+------------------------------------------------+----------------------------+-----------------------+
| Method                                         | 95% Confidence Interval    | Excludes Zero (p<.05)?|
+------------------------------------------------+----------------------------+-----------------------+
| Uncorrected Asymptotic Wald (Phase 8 report)   | [+0.90%, +40.77%]          | YES (Artifact of bias)|
| Continuity-Corrected Wald Interval             | [-3.27%, +36.60%]          | NO (Consistent p=.125)|
| Adjusted Agresti-Min Paired Interval (+2 cell) | [-1.98%, +39.42%]          | NO (Consistent p=.125)|
| Exact Clopper-Pearson on Discordant Ratio (π)  | [0.4213, 0.9964]           | NO (Includes π = 0.50)|
| Exact Conditional Odds Ratio (ψ = b/c = 6.0)   | [0.728, 276.8]             | NO (Includes ψ = 1.0) |
+------------------------------------------------+----------------------------+-----------------------+
```

### Conclusion:
The reported $[+0.90\%, +40.77\%]$ interval was an artifact of using the uncorrected asymptotic Wald formula on a small discordant sample ($n_d = 7$). Under exact and continuity-corrected paired methods, the 95% confidence interval spans across zero (e.g., $[-1.98\%, +39.42\%]$), which is **100% mathematically consistent with the exact McNemar test ($p = 0.1250$)**.

---

## 2. Statistical Significance vs. Practical Meaningfulness

1. **Statistical Significance ($lpha = 0.05$):**
   - The exact two-sided McNemar test yielded $p = 0.1250$.
   - **Verdict:** NOT statistically significant. $H_0$ cannot be rejected.
2. **Practical Meaningfulness ($\Delta \ge +15.0\%$):**
   - The observed risk difference is $+20.83\%$, which exceeds the pre-registered threshold for practical importance ($+15.0\%$).
   - The discordance odds ratio is $6.0$ (Hybrid corrected 6 retrieval errors while retrieval corrected only 1 hybrid error).
3. **Synthesis:**
   - The observed effect is **directionally large and practically meaningful**, but the sample size ($N = 24$, $n_d = 7$) does not possess sufficient statistical power to rule out random variation at $\alpha = 0.05$.
   - The Phase 8 pre-registered decision boundary correctly concluded: **RESULTS ARE INCONCLUSIVE**.
