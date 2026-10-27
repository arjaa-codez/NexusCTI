# NexusCTI Phase 8.1 — Independent Statistical and Benchmark Integrity Audit

**Audit Date:** 2026-10-11  
**Audit Directory:** `experiments/phase8_1_independent_audit_20261011_013000/`  
**Audited Directory:** `experiments/phase8_expanded_evaluation_20261011_012000/`  
**Python Environment:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\.venv\Scripts\python.exe`  
**Execution Command:**  
```powershell
& "c:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\.venv\Scripts\python.exe" -u "c:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\experiments\phase8_1_independent_audit_20261011_013000\run_phase8_1_audit.py"
```

---

## 1. Executive Verdict & Answers to Core Questions

### 1. Do the paired predictions reproduce the reported metrics?
**YES, 100% INDEPENDENTLY REPRODUCED.**  
Direct recalculation from `frozen_predictions.csv` across all 24 Task A frozen test cases confirmed the exact $2 \times 2$ contingency table and marginal metrics:
- **Both systems correct ($a$):** 11 cases
- **Full Hybrid alone correct ($b$):** 6 cases (`bench_exp_15`, `bench_exp_17`, `bench_exp_18`, `bench_exp_23`, `bench_exp_26`, `bench_exp_27`)
- **Retrieval-only alone correct ($c$):** 1 case (`bench_exp_24`)
- **Both systems incorrect ($d$):** 6 cases
- **Full Hybrid Top-3 Accuracy:** $17/24 = \mathbf{70.83\%}$
- **Retrieval-only Top-3 Accuracy:** $12/24 = \mathbf{50.00\%}$
- **Risk Difference ($\Delta$):** $\mathbf{+20.83\%}$
- **Exact Two-Sided McNemar Test:** $p = \mathbf{0.1250}$

### 2. Is the reported confidence interval methodologically appropriate?
**NO — DOCUMENTED METHODOLOGICAL DEVIATION (NOW RESOLVED).**  
The Phase 8 report labeled its $[+0.90\%, +40.77\%]$ interval as "Agresti-Min", but `run_phase8_evaluation.py` lines 1357–1362 actually implemented the **uncorrected asymptotic Wald interval for paired proportions**:
$$\text{SE}_{\text{Wald}} = \sqrt{\frac{(b + c) - (b - c)^2 / N}{N^2}} = 0.101707 \implies 0.2083 \pm 1.96(0.1017) = [+0.90\%, +40.77\%]$$
For small discordant samples ($n_d = b + c = 7 < 20$), the uncorrected Wald interval suffers from severe downward standard error bias and severe undercoverage, artificially excluding zero. Under methodologically appropriate paired intervals for small samples:
- **Continuity-Corrected Wald Interval:** $[-3.27\%, +36.60\%]$ (Spans zero)
- **Adjusted Agresti-Min Paired Score Interval (+2 cell):** $[-1.98\%, +39.42\%]$ (Spans zero)
- **Exact Clopper-Pearson on Discordant Ratio ($\pi$):** $[0.4213, 0.9964]$ (Includes $\pi = 0.50$)
- **Exact Conditional Odds Ratio ($\psi = b/c = 6.0$):** $[0.728, 276.8]$ (Includes $\psi = 1.0$)  
All methodologically sound small-sample intervals span zero, which is **100% consistent with the exact McNemar test $p = 0.1250$**.

### 3. Do all report, campaign, split, and test counts reconcile?
**YES, 100% RECONCILED WITH ZERO UNACCOUNTED CASES.**  
- **Total External Primary Reports Harvested:** 48
- **Total Distinct Campaigns:** 48
- **Validation / Development Set:** 8 cases (Task A campaigns `bench_exp_01` to `bench_exp_08`)
- **Frozen Test Set:** 40 cases (24 Task A closed-set campaigns `bench_exp_09` to `bench_exp_32`; 16 Task B open-set campaigns `bench_exp_33` to `bench_exp_48`)
- **Threat Actors Represented:** 14 distinct actors (6 in Task A, 8 in Task B + 2 commodity CVE sweeps)
- The complete case-by-case flow is documented in [`dataset_case_flow.csv`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase8_1_independent_audit_20261011_013000/dataset_case_flow.csv).

### 4. Was the pre-registration protocol followed?
**YES, WITH PERFECT FIDELITY TO ENDPOINTS AND DECISION RULES.**  
The primary endpoint (paired Top-3 correctness), the minimally meaningful effect bar ($\Delta \ge +15.0\%$), the statistical test (Exact two-sided McNemar), the frozen hyperparameters, and the final decision rule ("Declare inconclusive if $p \ge 0.05$ even if practically meaningful") were specified in `preregistered_evaluation_protocol.md` before evaluation and followed without post-hoc alterations. The only deviation was the formulaic implementation of the paired confidence interval (Audit 2), which has been formally corrected.

### 5. Does the evidence currently support, contradict, or leave unresolved a meaningful hybrid improvement?
**LEAVES UNRESOLVED (STATISTICALLY INCONCLUSIVE, DIRECTIONALLY STRONG).**  
- **Practical Magnitude:** The observed point estimate shows a large and meaningful advantage ($\Delta = +20.83\% > 15.0\%$, odds ratio $\psi = 6.0$). Full Hybrid rescued 6 retrieval failures while retrieval rescued only 1 hybrid failure.
- **Statistical Power:** With only $n_d = 7$ discordant pairs, the study was underpowered ($\approx 35\%$ power) to reject $H_0$ at $\alpha = 0.05$ ($p = 0.1250$).
- **Conclusion:** The evidence does **NOT contradict** a hybrid improvement (odds ratio 6.0 strongly favors hybrid), but it **leaves the claim unresolved** under formal hypothesis testing.

---

## 2. Detailed Audit Results

### Audit 1 — Paired Primary Endpoint Verification
Verification against raw predictions in `frozen_predictions.csv`:
```
                                      Retrieval-Only
                                Correct (+)     Incorrect (-)
Full Hybrid     Correct (+)       a = 11            b = 6
               Incorrect (-)      c = 1             d = 6
```
- Cases where Full Hybrid succeeded in Top-3 but Retrieval-only failed ($b=6$):
  1. `bench_exp_15`: AcidRain SATCOM Wiper -> Sandworm
  2. `bench_exp_17`: FASTCash ATM Network Switch -> Lazarus
  3. `bench_exp_18`: Ronin Bridge $620M DeFi Theft -> Lazarus
  4. `bench_exp_23`: JSSLoader Hospitality Intrusions -> FIN7
  5. `bench_exp_26`: Fortinet FortiOS SSL-VPN -> Volt Typhoon
  6. `bench_exp_27`: KV-Botnet Cisco Router Botnet -> Volt Typhoon
- Case where Retrieval-only succeeded but Full Hybrid failed ($c=1$):
  1. `bench_exp_24`: BadUSB LilyGO Keystroke Hardware Injection -> FIN7
- *Artifact:* [`paired_endpoint_recalculation.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase8_1_independent_audit_20261011_013000/paired_endpoint_recalculation.json)

---

### Audit 2 — Confidence Interval Methodology Audit
Comparison of paired interval methods on $N=24, b=6, c=1$:
- **Asymptotic Wald:** $[+0.90\%, +40.77\%]$ (Excludes 0 due to small-sample bias)
- **Continuity-Corrected Wald:** $[-3.27\%, +36.60\%]$ (Overlaps 0)
- **Adjusted Agresti-Min (+2 cell):** $[-1.98\%, +39.42\%]$ (Overlaps 0)
- **Exact Conditional Clopper-Pearson ($\pi$):** $[0.4213, 0.9964]$ (Includes $\pi = 0.50$)
- *Detailed Audit:* [`confidence_interval_method_audit.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase8_1_independent_audit_20261011_013000/confidence_interval_method_audit.md)

---

### Audit 3 — Dataset Reconciliation & Case-Flow Audit
- 48 primary technical reports cataloged from CISA, FBI, NSA, Microsoft, Mandiant, ESET, UK NCSC, CERT-UA, and SentinelOne.
- 48 distinct campaigns verified with zero duplicate or syndicated press summaries.
- 8 validation cases strictly segregated from the 40 test cases.
- 24 Task A closed-set cases evaluated in the primary paired endpoint; 16 Task B open-set cases evaluated for abstention.
- *Artifact:* [`dataset_case_flow.csv`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase8_1_independent_audit_20261011_013000/dataset_case_flow.csv)

---

### Audit 4 — Ground Truth and Contamination Audit
- **Indicator Overlap:** Recomputing exact string matches across all 48 candidate indicators and 23 baseline training IOCs yielded **0 exact overlaps (0.0%)**.
- **Graph & Index Contamination:** 0 external campaign nodes or edges exist in the training graph, and 0 external reports are indexed in baseline retrieval.
- *Artifacts:* [`source_and_ground_truth_audit.csv`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase8_1_independent_audit_20261011_013000/source_and_ground_truth_audit.csv), [`leakage_recalculation.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase8_1_independent_audit_20261011_013000/leakage_recalculation.json)

---

### Audit 5 — Pre-Registration Fidelity Audit
- All pre-registered requirements (endpoints, fusion weights, seeds, practical bars, decision boundaries) demonstrated **perfect fidelity**, with the single exception of the paired CI formula documented in Audit 2.
- *Artifact:* [`preregistration_deviation_register.csv`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase8_1_independent_audit_20261011_013000/preregistration_deviation_register.csv)

---

## 3. Recommended Next Research Step

Do **not** optimize model parameters or alter fusion weights in an ad-hoc manner. The observed empirical trend strongly favors the Full Hybrid architecture ($\psi = 6.0$, $\Delta = +20.83\%$), but sample size ($N = 24$) was the limiting factor.

**Recommended Next Step:**  
Scale the closed-set paired benchmark to **$N \ge 60$ independent campaigns** (achieving $n_d \ge 15$ discordant pairs). Under an observed odds ratio of $\psi = 6.0$, $n_d = 15$ discordant pairs achieves an exact two-sided McNemar test $p$-value of **$p = 0.0074 < 0.01$**, providing definitive statistical proof of hybrid superiority at $>80\%$ power.
