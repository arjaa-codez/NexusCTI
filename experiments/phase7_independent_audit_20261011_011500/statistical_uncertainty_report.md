# NexusCTI Phase 7 — Statistical Uncertainty and Confidence Interval Audit

**Audit Date:** 2026-10-11  
**Experiment Root:** `experiments/phase7_independent_audit_20261011_011500/`  
**Sample Sizes:** Task A Closed Set ($N=8$), Task B Open Set ($N=4$)  

---

## 1. Executive Statistical Finding: Correction of Phase 6 Claim

In `phase6_report.md` Section 5 Question 7 and `benchmark_metrics.json`, the report claimed:
> *"With N=8 frozen Task A cases and N=4 frozen Task B cases, confidence intervals span approximately ±15%."*

### Independent Verification Result: **CONTRADICTED & CORRECTED**
This claim is mathematically incorrect. At sample size $N=8$, confidence intervals are drastically wider than $\pm 15\%$.

Using the standard **Wilson Score Interval** with 95% confidence ($\alpha = 0.05$):

$$w = \\frac{p + \\frac{z^2}{2n} \\pm z \\sqrt{\\frac{p(1-p)}{n} + \\frac{z^2}{4n^2}}}{1 + \\frac{z^2}{n}}$$

| Metric | Sample Success ($k/n$) | Point Estimate ($p$) | 95% Wilson Score Interval | True Error Margin | Phase 6 Claimed Margin | Audit Finding |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Top-1 Accuracy (Full Hybrid)** | 4 / 8 | **50.0%** | **[21.52%, 78.48%]** | **± 28.48%** | ± 15.0% | **Severely Understated Margin** |
| **Top-3 Accuracy (Full Hybrid)** | 7 / 8 | **87.5%** | **[52.91%, 97.76%]** | **[-34.59%, +10.26%]**| ± 15.0% | **Asymmetric Uncertainty** |
| **Top-1 Accuracy (Graph-only)** | 1 / 8 | **12.5%** | **[2.24%, 47.09%]** | **[-10.26%, +34.59%]**| ± 15.0% | **Asymmetric Uncertainty** |
| **Top-3 Accuracy (Retrieval-only)**| 5 / 8 | **62.5%** | **[30.57%, 86.32%]** | **± 27.88%** | ± 15.0% | **Severely Understated Margin** |
| **Task B Abstention Rate** | 4 / 4 | **100.0%** | **[51.01%, 100.00%]**| **[-48.99%, +0.00%]** | ± 15.0% | **Extreme Uncertainty** |

The actual uncertainty margin at $N=8$ for $p=0.50$ is **$\pm 28.5\%$**, nearly **double** the $\pm 15\%$ reported in Phase 6.

---

## 2. Hypothesis Testing: Full Hybrid vs. Retrieval-Only

In Phase 6, the report highlighted Full Hybrid's Top-3 accuracy of 87.5% (7/8) over Retrieval-only's 62.5% (5/8).

### Paired McNemar Exact Binomial Test:
- **Null Hypothesis ($H_0$):** Full Hybrid and Retrieval-only have equal marginal error rates on unseen campaign attribution.
- **Discordant Pairs ($N=8$):**
  - Cases where Full Hybrid succeeded in Top-3 but Retrieval-only failed: **$b = 2$** (`bench_ext_01`, `bench_ext_09`).
  - Cases where Retrieval-only succeeded in Top-3 but Full Hybrid failed: **$c = 0$**.
- **Two-Sided Exact Binomial Test ($n = b+c = 2$):**
  $$p\\text{-value} = 2 \\times \\left(\\frac{1}{2}\\right)^2 = 0.5000$$

### Finding:
Because $p = 0.5000 \\gg 0.05$, the observed improvement of Full Hybrid over Retrieval-only is **NOT statistically significant**. It is plausible under random chance at $N=8$. While the trend is directionally promising (7/8 vs 5/8), claims of proven architectural superiority over retrieval alone cannot be supported without expanding the test set to at least $N \\ge 40$ independent campaigns.

---

## 3. Task B Open-Set Evaluation Validity ($N=4$)

For Task B, four cases were evaluated:
1. `bench_ext_13` (Kimsuky): Correctly rejected (Verdit: `INCONCLUSIVE`).
2. `bench_ext_14` (LockBit): Correctly rejected (Verdit: `INCONCLUSIVE`).
3. `bench_ext_15` (APT41): Correctly rejected (Verdit: `INCONCLUSIVE`).
4. `bench_ext_16` (CVE-2022-47966 Commodity): Correctly rejected (Verdit: `INCONCLUSIVE`).

### Finding:
While the empirical abstention was 4/4 (100.0%), the 95% Wilson confidence interval for $k=4, N=4$ is **$[51.01\\%, 100.00\\%]$**. 
A sample size of $N=4$ is **statistically insufficient** to prove open-set out-of-distribution robustness. It serves only as a qualitative sanity check.
