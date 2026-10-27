# NexusCTI Phase 10 — Confirmatory Prospective Benchmark Evaluation Report

**Evaluation Phase:** Phase 10 — Confirmatory Evaluation  
**Protocol Version:** NexusCTI Preregistered Evaluation Protocol v2.2-amended  
**Date of Execution:** 2026-10-28T02:12:00+05:30  
**Project Root:** `c:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI`  
**Frozen Predictions Digest:** `79e304118cc31f8d25edd44045eed162b45c952586224a272fa3039aeeb14cdb`  

---

## 1. Executive Summary & Confirmatory Verdict

### **CONFIRMATORY SUPERIORITY: FORMALLY CONFIRMED AND PASSED**

Under the preregistered decision rules specified in Section 2.3 of Protocol v2.2-amended, **NexusCTI Full Hybrid** demonstrates statistically significant and directionally superior attribution performance over the **Retrieval-only** baseline:
1. **Exact Two-Sided McNemar Test:** $p = 4.6566 \times 10^{-10}$ (significance threshold $\alpha = 0.05$ satisfied; $p \ll 0.001$).
2. **Directional Requirement:** Observed paired risk difference $\hat{\Delta} = +32.00$ percentage points ($\hat{\Delta} > 0$ satisfied).
3. **95% Agresti–Min (2005) Confidence Interval:** $[+21.97\%, \; +40.78\%]$ (excludes zero by over $21.9$ percentage points).
4. **Planning MDE Comparison:** The observed point difference ($+32.00\%$) substantially exceeds the $+15.0\%$ planning Minimal Detectable Effect.
5. **Open-Set Abstention Fidelity (Task B):** $100.0\%$ proper abstention rate ($30/30$), suppressing $100\%$ of out-of-registry false attributions.

---

## 2. Primary Endpoint: Paired Top-3 Attribution Accuracy ($N = 100$)

### 2.1 $2 \times 2$ Paired Contingency Table

$$\begin{array}{c|cc|c}
& \text{Retrieval Correct } (Y_2=1) & \text{Retrieval Incorrect } (Y_2=0) & \text{Total} \\
\hline
\text{Hybrid Correct } (Y_1=1) & a = 64 & b = 32 & 96 \\
\text{Hybrid Incorrect } (Y_1=0) & c = 0 & d = 4 & 4 \\
\hline
\text{Total} & 64 & 36 & N = 100
\end{array}$$

- **Marginal Full Hybrid Top-3 Accuracy:** $p_1 = \frac{64 + 32}{100} = \mathbf{96.00\%}$
- **Marginal Retrieval-only Top-3 Accuracy:** $p_2 = \frac{64 + 0}{100} = \mathbf{64.00\%}$
- **Marginal Standalone GNN Top-3 Accuracy:** $\mathbf{44.00\%}$
- **Total Discordant Pairs ($n_d = b + c$):** $32$
- **Discordance Ratio ($b / c$):** $32 / 0 = +\infty$

### 2.2 Statistical Inference & Interval Estimation

| Metric | Formally Prespecified Formula | Observed Value | Confirmatory Criteria |
| :--- | :--- | :---: | :---: |
| **Paired Risk Difference ($\hat{\Delta}$)** | $(b - c) / N$ | **$+32.00\%$** | $\hat{\Delta} > 0$ (**PASSED**) |
| **Exact McNemar $p$-value** | $2 \sum_{k=b}^{n_d} \binom{n_d}{k} (0.5)^{n_d}$ | **$4.66 \times 10^{-10}$** | $p \le 0.05$ (**PASSED**) |
| **95% Agresti–Min CI** | $\tilde{\Delta} \pm 1.95996 \cdot \widetilde{\text{SE}}$ | **$[+21.97\%, \; +40.78\%]$** | Strictly positive (**PASSED**) |

---

## 3. Secondary Performance Dimensions (Task A)

| Evaluation Metric | Full Hybrid (NexusCTI) | Retrieval-only Baseline | Standalone GNN Baseline | Relative Gain |
| :--- | :---: | :---: | :---: | :---: |
| **Top-1 Attribution Accuracy** | **88.00%** | 38.00% | 40.00% | **+50.00% vs RAG** |
| **Top-3 Attribution Accuracy** | **96.00%** | 64.00% | 44.00% | **+32.00% vs RAG** |
| **Top-5 Attribution Accuracy** | **98.00%** | 76.00% | 52.00% | **+22.00% vs RAG** |
| **Mean Reciprocal Rank (MRR)** | **0.9233** | 0.5186 | 0.4431 | **+0.4047 vs RAG** |
| **Misattribution / Failure Rate** | **4.00%** | 36.00% | 56.00% | **-32.00% Reduction** |

---

## 4. Secondary Endpoint: Task B Open-Set Abstention ($N = 30$)

Task B evaluates $N = 30$ independent, out-of-registry novel intrusion sets (e.g. LockBit 3.0, BlackCat/ALPHV, Cl0p, Scattered Spider, Log4j commodity waves) where candidate groups are outside the closed set:

| Model Architecture | Proper Abstention Count | False Attribution Count | Proper Abstention Rate |
| :--- | :---: | :---: | :---: |
| **NexusCTI Full Hybrid** | **30 / 30** | **0 / 30** | **100.00%** |
| **Retrieval-only Baseline** | 0 / 30 | 30 / 30 | 0.00% |

**Key Finding:** Standard dense vector search suffers from forced attribution—because it lacks a calibrated cross-modal consistency matrix, it blindly assigns the highest cosine-similarity text chunk as ground truth (100% false attribution). In contrast, NexusCTI's dual-layer confidence matrix detects topological dissonance when retrieved text cannot be corroborated by graph traversal, triggering proper abstention (`INCONCLUSIVE`).

---

## 5. Artifact Chain of Custody & Hash Manifest

All Phase 10 artifacts are sealed and verifiable:

- [`frozen_test_predictions.csv`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase10_confirmatory_evaluation/frozen_test_predictions.csv): `79e304118cc31f8d25edd44045eed162b45c952586224a272fa3039aeeb14cdb`
- [`phase10_metrics.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase10_confirmatory_evaluation/phase10_metrics.json)
- [`phase10_contingency_table.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase10_confirmatory_evaluation/phase10_contingency_table.json)
- [`run_phase10_confirmatory_evaluation.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase10_confirmatory_evaluation/run_phase10_confirmatory_evaluation.py)
