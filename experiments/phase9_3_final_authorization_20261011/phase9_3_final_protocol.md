# NexusCTI Phase 9.3 — Final Evaluation Protocol (Version 2.0 Locked)

**Document Version:** 2.0 (Confirmatory Protocol Freeze & Blind-Evaluation Authorization Gate)  
**Date:** 2026-10-11  
**Project Root:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI`  
**Experiment Root:** `experiments/phase9_3_final_authorization_20261011/`  
**Prior Protocol Base:** `experiments/phase9_benchmark_preparation_20261011_020400/phase9_protocol_freeze.md` (v1.0)  
**Protocol Amendment Basis:** `experiments/phase9_2_protocol_clarification_20261011_030000/phase9_2_protocol_amendment_proposal.md` (Alternative B)

---

## 1. Confirmatory Evaluation Overview & Scope

This document specifies the frozen confirmatory evaluation protocol for **NexusCTI**, comparing the **Full Hybrid** attribution architecture (combining graph topological clustering, relational inductive bias via Graph Neural Networks, and dense semantic vector retrieval via ChromaDB) against the baseline **Retrieval-only** architecture.

The evaluation will be performed across a prospective benchmark consisting of:
- **Task A (Closed-Set Confirmatory Evaluation):** $N = 100$ independent, verified, external cyber threat campaigns attributed to 14 candidate threat actors.
- **Task B (Open-Set Abstention Evaluation):** $N = 30$ independent, out-of-registry novel threat campaigns and ambiguous multi-actor intrusion sets to measure abstention fidelity and false-attribution suppression.

All models, embedding weights, graph topology, retrieval index, decision thresholds, and evaluation code are cryptographically frozen.

---

## 2. Primary Endpoint and Confirmatory Decision Rules

### 2.1 Primary Endpoint Specification
The primary confirmatory endpoint is the **paired Top-3 attribution accuracy** of **Full Hybrid** versus **Retrieval-only** on the $N = 100$ closed-set test campaigns of Task A.

Each campaign is evaluated independently under identical inputs:
- $Y_{1,i} \in \{0, 1\}$: Full Hybrid Top-3 correctness indicator on campaign $i \in \{1, \dots, 100\}$.
- $Y_{2,i} \in \{0, 1\}$: Retrieval-only Top-3 correctness indicator on campaign $i \in \{1, \dots, 100\}$.

The paired outcomes form a standard $2 \times 2$ contingency table:
$$\begin{array}{c|cc|c}
& \text{Retrieval Correct } (Y_2=1) & \text{Retrieval Incorrect } (Y_2=0) & \text{Total} \\
\hline
\text{Hybrid Correct } (Y_1=1) & a & b & a + b \\
\text{Hybrid Incorrect } (Y_1=0) & c & d & c + d \\
\hline
\text{Total} & a + c & b + d & N = 100
\end{array}$$

The marginal Top-3 accuracy for Full Hybrid is $p_1 = (a + b)/N$, and for Retrieval-only is $p_2 = (a + c)/N$.  
The paired risk difference is:
$$\hat{\Delta} = p_1 - p_2 = \frac{b - c}{N}$$
where $b$ is the number of campaigns correctly attributed in Top-3 by Full Hybrid but missed by Retrieval-only, and $c$ is the number of campaigns correctly attributed in Top-3 by Retrieval-only but missed by Full Hybrid. The total number of discordant pairs is $n_d = b + c$.

### 2.2 Primary Hypothesis & Significance Test
The formal statistical test is the **exact two-sided McNemar test** evaluated at significance level $\alpha = 0.05$. Under the null hypothesis $H_0: p_1 = p_2 \iff b \sim \text{Binomial}(n_d, 0.5)$:
$$p_{\text{McNemar}} = \begin{cases} 
1.0 & \text{if } n_d = 0 \\
\min\left(1.0, \, 2 \times \sum_{i = \max(b, c)}^{n_d} \binom{n_d}{i} 0.5^{n_d}\right) & \text{if } n_d > 0
\end{cases}$$

### 2.3 Confirmatory Superiority Decision Rule
A formal claim of confirmatory superiority of Full Hybrid over Retrieval-only requires satisfying BOTH of the following prespecified conditions:
1. **Statistical Significance:** $p_{\text{McNemar}} \le 0.05$.
2. **Directional Superiority:** The observed paired risk difference is strictly positive:
   $$\hat{\Delta} = \frac{b - c}{N} > 0 \quad (\text{i.e., } b > c)$$

### 2.4 Role of Planning MDE (+15 Percentage Points)
The $+15.0$ percentage point difference ($\Delta_{\text{target}} = +0.15$) is explicitly recorded as the **planning Minimal Detectable Effect (MDE)** that justified the sample size of $N = 100$ under prospective power modeling ($q = 0.25, \theta = 0.80$, yielding $83.67\%$ power).

**Crucial Protocol Amendment:**  
The $+15.0$ percentage point target is **NOT** a hard gating constraint required of the sample point estimate $\hat{\Delta}$. Demanding that the sample mean simultaneously achieve $\hat{\Delta} \ge +0.150$ artificially capped statistical power at $\approx 54\%$ due to the central limit property of sample estimators. Instead, confirmatory superiority is governed by Section 2.3, while practical effect magnitude is transparently reported via the prespecified Agresti–Min confidence interval.

---

## 3. Prespecified Confidence Interval: Agresti–Min (2005)

### 3.1 Justification and Methodological Reference
To prevent interval-test discordance (such as the uncorrected Newcombe interval excluding zero when the exact McNemar test does not reject $H_0$), this protocol prespecifies the **Agresti–Min paired risk-difference confidence interval**.

- **Citation:** Agresti, A., & Min, Y. (2005). *Frequently asked questions about intervals for difference of proportions in matched-pair designs.* **Statistics in Medicine**, 24(5), 729–740. DOI: 10.1002/sim.1973.

### 3.2 Mathematical Formula
The Agresti–Min method adds $+1.0$ pseudo-observation to each discordant cell, adding $2.0$ to the effective total sample size:
$$\tilde{b} = b + 1, \quad \tilde{c} = c + 1, \quad \tilde{N} = N + 2$$
The pseudo-proportions are:
$$\tilde{p}_{12} = \frac{\tilde{b}}{\tilde{N}} = \frac{b + 1}{N + 2}, \quad \tilde{p}_{21} = \frac{\tilde{c}}{\tilde{N}} = \frac{c + 1}{N + 2}$$
The pseudocount point difference is:
$$\tilde{\Delta} = \tilde{p}_{12} - \tilde{p}_{21} = \frac{b - c}{N + 2}$$
The estimated variance under the paired multinomial distribution is:
$$\widehat{\text{Var}}(\tilde{\Delta}) = \frac{\tilde{p}_{12} + \tilde{p}_{21} - (\tilde{p}_{12} - \tilde{p}_{21})^2}{\tilde{N}} = \frac{\frac{b + c + 2}{N + 2} - \left(\frac{b - c}{N + 2}\right)^2}{N + 2}$$
The standard error is:
$$\text{SE}(\tilde{\Delta}) = \sqrt{\widehat{\text{Var}}(\tilde{\Delta})}$$
For a nominal $95\%$ two-sided interval, $z_{0.975} = 1.95996$. The confidence limits are:
$$\text{CI}_{95\%}(\Delta) = \left[ \max\left(-1.0, \, \tilde{\Delta} - z_{1 - \alpha/2} \text{SE}(\tilde{\Delta})\right), \; \min\left(1.0, \, \tilde{\Delta} + z_{1 - \alpha/2} \text{SE}(\tilde{\Delta})\right) \right]$$

---

## 4. Mandatory Reporting Standards

The prospective evaluation report must record all of the following quantities without redaction:
1. Exact two-sided McNemar $p$-value ($p_{\text{McNemar}}$).
2. Paired sample risk difference $\hat{\Delta} = (b - c)/N$ (in percentage points).
3. 95% Agresti–Min confidence interval $[\text{CI}_{\text{low}}, \text{CI}_{\text{high}}]$.
4. Complete $2 \times 2$ paired contingency table counts: $a, b, c, d$, and $n_d = b + c$.
5. Per-model marginal metrics on Task A:
   - Full Hybrid Top-1 accuracy, Top-3 accuracy, and Mean Reciprocal Rank (MRR).
   - Retrieval-only Top-1 accuracy, Top-3 accuracy, and MRR.
   - Graph-only Top-1 and Top-3 accuracy.
   - GNN-only Top-1 and Top-3 accuracy.
6. Open-set Task B performance ($N = 30$):
   - Full Hybrid proper abstention rate and false attribution count.
   - Baseline proper abstention rate and false attribution count.

### 4.1 Epistemic and Operational Disclaimers
The final evaluation report must explicitly state:
> **"Statistical significance on this benchmark demonstrates that the Full Hybrid architecture outperforms the Retrieval-only baseline under the specific distribution of the evaluated test cases. It does NOT establish operational utility in production SOC workflows, causal attribution validity of external actors, or guaranteed generalization to previously unobserved campaign types or adversarial evasion."**

---

## 5. Data Handling and Missing Data Policy (Intention-to-Evaluate)

To prevent selection bias, post-hoc exclusions, or optimistic attrition handling:
1. **Intention-to-Evaluate Principle:** Every one of the $N = 100$ Task A cases and $N = 30$ Task B cases must be evaluated and accounted for.
2. **Missing Predictions & Execution Failures:** Any campaign prediction that fails due to runtime exception, memory exhaustion, timeout, parse failure, or empty output is **automatically assigned Rank = 99 (Incorrect)**. It cannot be dropped or replaced.
3. **Score Ties:** In the event that two candidate actors receive identical fused confidence scores, ties are resolved deterministically by lexicographical order of their canonical actor IDs (`actor_apt28` < `actor_apt29` < ...).
4. **Pre-Evaluation Exclusions:** The 10 syndicated duplicate reports and 10 ambiguous/contaminated reports identified in Phase 9 are permanently excluded prior to unblinding and cannot be reintroduced.

---

## 6. Technical Blinding & Quarantine Enforcement

1. **Storage Segregation:** Ground-truth labels for Task A and Task B reside exclusively in quarantined storage (`quarantined_test_labels.json` / `candidate_campaign_manifest.csv`) and are strictly inaccessible to the inference runner.
2. **Input Isolation:** The inference execution loop receives only raw text passages, campaign identifiers, and extracted observable indicators.
3. **Unblinding Sequence:**
   - Step 1: Execute inference runner across all test cases.
   - Step 2: Freeze and hash `frozen_test_predictions.csv`.
   - Step 3: Verify cryptographic SHA-256 of the prediction file.
   - Step 4: Programmatically merge predictions with ground-truth labels to compute contingency tables and metrics.

---
*Protocol Version 2.0 locked and certified for Phase 9.3.*
