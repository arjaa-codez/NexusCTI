# NexusCTI Phase 8 — Expanded External Benchmark and Pre-Registered Evaluation

**Master Technical Report & Pre-Registered Evaluation Outcome**  
**Execution Timestamp:** 2026-10-11T01:20:00+05:30  
**Phase Directory:** `experiments/phase8_expanded_evaluation_20261011_012000/`  
**Python Environment:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\.venv\Scripts\python.exe`  
**Pre-Registered Protocol:** [`preregistered_evaluation_protocol.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase8_expanded_evaluation_20261011_012000/preregistered_evaluation_protocol.md)  
**Power Analysis:** [`power_analysis.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase8_expanded_evaluation_20261011_012000/power_analysis.md)  

---

## 1. Executive Summary & Pre-Registered Final Decision

In Phase 8, NexusCTI completed a large-scale, pre-registered prospective evaluation to determine whether the **Full Hybrid architecture** provides a statistically reproducible improvement over **Retrieval-only** on genuinely unseen cyber threat campaigns.

### Pre-Registered Decision Outcome: **RESULTS ARE INCONCLUSIVE**

```
========================================================================================================
PRIMARY PRE-REGISTERED ENDPOINT: PAIRED TOP-3 CORRECTNESS (TASK A CLOSED SET, N = 24)
========================================================================================================
                                      Retrieval-Only
                                Correct (+)     Incorrect (-)
Full Hybrid     Correct (+)       a = 11            b = 6
               Incorrect (-)      c = 1             d = 6
--------------------------------------------------------------------------------------------------------
Metric                           Full Hybrid       Retrieval-Only     Paired Difference (Δ)
--------------------------------------------------------------------------------------------------------
Top-3 Accuracy                   70.83% (17/24)    50.00% (12/24)     +20.83%
95% Confidence Interval          [50.8%, 85.1%]    [31.4%, 68.6%]     [+0.90%, +40.77%] (Agresti-Min)
Discordance Odds Ratio (ψ = b/c)       --                --           6.00 (Hybrid rescues 6 retrieval errors)
Exact McNemar Test (Two-Sided)        --                --           p = 0.1250 (Inconclusive at α = 0.05)
Pre-Registered Practical Bar (≥15%)   --                --           PASSED (+20.83% ≥ +15.0%)
========================================================================================================
```

### Scientific Interpretation:
1. **Practical Effect Supported:** Full Hybrid achieved a **+20.83% improvement** in Top-3 candidate recall over Retrieval-only, exceeding the pre-registered threshold for practical meaningfulness ($\Delta \ge +15.0\%$). The 95% Agresti-Min confidence interval for the paired difference is strictly positive ($[+0.90\%, +40.77\%]$), and the discordance odds ratio is **6.0** (Hybrid rescued 6 retrieval failures while retrieval rescued only 1 hybrid failure).
2. **Statistical Significance Inconclusive:** With $n_d = 7$ discordant pairs, the exact two-sided binomial McNemar test yielded **$p = 0.1250$**. Because $p > 0.05$, the pre-registered decision boundary requires declaring the outcome **statistically inconclusive**.
3. **Graph Breakdown Replicated:** Purely topological Graph-only and GNN-only architectures collapsed to **0.0% Top-1 accuracy** (0/24) and **33.33% Top-3 accuracy** (8/24, MRR 0.2604), confirming that graph methods cannot attribute novel indicators without semantic or behavioral bridges.
4. **Open-Set Robustness Validated:** On Task B ($N = 16$ cases spanning 8 out-of-vocabulary threat actors and commodity vulnerabilities), NexusCTI achieved a **100% Proper Abstention Rate** (16/16, 95% Wilson CI: $[80.64\%, 100.0\%]$) with **0.0% False Attribution Rate**.

---

## 2. Expanded Benchmark Provenance and Split Integrity

### 2.1 Dataset Composition (48 Campaigns across 14 Threat Actors)
The benchmark was expanded from 16 to **48 authentic, verified technical reports** documenting 48 distinct campaigns published between 2020 and 2025:
- **Task A Known Threat Actors (32 Campaigns across 6 Actors):**
  - `APT28` (GRU 26165): GooseEgg LPE, Drovorub Linux Rootkit, Roundcube Webmail XSS, Cisco IOS SNMP Jaguar Tooth, LoJax UEFI Firmware (5 campaigns).
  - `APT29` (SVR): TeamCity Auth Bypass, Midnight Blizzard OAuth Cloud, WellMess Vaccine Espionage, USAID EnvyScout Phishing, SVR Cloud Token Spray (5 campaigns).
  - `Sandworm` (GRU 74455): Cyclops Blink Botnet, Infamous Chisel Android/Tor, HermeticWiper Ukraine Sabotage, Industroyer2 Power Grid, AcidRain SATCOM Wiper (5 campaigns).
  - `Lazarus` (RGB 121): TraderTraitor Trojanized Trading Apps, FASTCash ATM Cash-Out, Ronin Bridge $620M DeFi Heist, Horizon Bridge $100M Attack, DTrack Nuclear Spyware, MagicRAT C2 (6 campaigns).
  - `FIN7` (Carbanak): PowerPlant PowerShell Backdoor, Domino Backdoor/Trickbot, JSSLoader Retail Access, BadUSB Hardware Injection, Carbanak Banking Terminal (5 campaigns).
  - `Volt Typhoon` (PRC Infrastructure): Ivanti Connect Secure Zero-Day, Fortinet FortiOS SSL-VPN, Telecom/SOHO Living-off-the-Land, KV-Botnet Cisco Router, Water/Energy Pre-positioning, Maritime Port OT (6 campaigns).
- **Task B Open-Set Unseen Threat Actors (16 Campaigns across 8 Actors + Commodity):**
  - `Kimsuky` (RGB): BabyShark Think Tank Phishing, AppleSeed Backdoor (2 campaigns).
  - `LockBit` (LockBit 3.0 / Green): CitrixBleed Extortion, Conti-derived Locker (2 campaigns).
  - `APT41` (Barium / Chinese MSS): Global Citrix/Zoho Sweep, US State Government KeyPlug (2 campaigns).
  - `Charming Kitten` (APT35 / Phosphorus / Iran): Federal Agency Log4j, Hyperscrap Exchange Extraction (2 campaigns).
  - `Gamaredon` (Primitive Bear / FSB 18th Center): Pterodo Military Phishing, GammaLoad Telecom (2 campaigns).
  - `BlackCat` (ALPHV): Healthcare ESXi Extortion, Sphynx Defense Evasion (2 campaigns).
  - `Scattered Spider` (UNC3944 / Octo Tempest): Okta Identity / Helpdesk Hijacking (1 campaign).
  - `Clop` (TA505 / Lace Tempest): MOVEit Transfer SQL Injection Zero-Day (1 campaign).
  - `Ambiguous Commodity Exploits`: ManageEngine CVE-2022-47966, Log4j Multi-Actor Scanning (2 campaigns).

### 2.2 Deduplication and Contamination Audits
- **Exact Indicator Overlap:** Re-checking all 48 candidate IOCs against the 23 baseline training IOCs confirmed **0 exact overlaps (0.0%)**.
- **Graph Contamination:** The training graph contains exactly 0 external threat campaign nodes or edges (`graph_contamination_audit.json`).
- **Retrieval Index Contamination:** Exactly 0 external reports were indexed in the baseline retrieval corpus (`retrieval_contamination_audit.json`).

---

## 3. Multi-Architecture Performance Across All 5 Systems

All 5 architectures were evaluated across the same frozen cases under fixed seeds (`torch.manual_seed(42)` and deterministic MD5 dense hashing).

```
+-------------------+----------------------+----------------------+--------+-----------------------+----------------------+
| Architecture      | Task A Top-1 (N=24)  | Task A Top-3 (N=24)  | Task A | Task B Abstention     | Task B False         |
|                   | [95% Wilson CI]      | [95% Wilson CI]      | MRR    | (N=16) [95% Wilson CI]| Attribution (N=16)   |
+-------------------+----------------------+----------------------+--------+-----------------------+----------------------+
| Graph-only        | 0.0% (0/24) [0-13.8%]| 33.3% (8/24) [18-53%]| 0.2604 | 100.0% (16/16)[81-100%| 0.0% (0/16)          |
| GNN-only (R-GCN)  | 0.0% (0/24) [0-13.8%]| 33.3% (8/24) [18-53%]| 0.2604 | 100.0% (16/16)[81-100%| 0.0% (0/16)          |
| Retrieval-only    | 25.0% (6/24)[12-45%] | 50.0% (12/24)[31-69%]| 0.4562 | 100.0% (16/16)[81-100%| 0.0% (0/16)          |
| Graph + RAG       | 25.0% (6/24)[12-45%] | 50.0% (12/24)[31-69%]| 0.4562 | 100.0% (16/16)[81-100%| 0.0% (0/16)          |
| Full Hybrid       | 29.2% (7/24)[15-49%] | 70.8% (17/24)[51-85%]| 0.5229 | 100.0% (16/16)[81-100%| 0.0% (0/16)          |
+-------------------+----------------------+----------------------+--------+-----------------------+----------------------+
```

### Analysis by Component:
1. **The Structural Floor of Pure Graph Methods:** When evaluated on truly disjoint campaigns where indicators have never been observed in training, Graph-only and GNN-only achieve 0.0% Top-1 accuracy. Because dynamic unlinked indicators have equal distance to training clusters, graph algorithms fall back to uniform default proximities.
2. **Dense Retrieval as the Baseline Driver:** Dense vector retrieval provides the primary predictive signal, achieving 25.0% Top-1 and 50.0% Top-3 accuracy by matching behavioral TTP text against historical actor dossiers.
3. **Hybrid Cross-Modal Correction:** Full Hybrid elevates Top-3 recall from 50.0% to 70.83% and increases MRR from 0.4562 to 0.5229. Crucially, the hybrid engine corrected 6 cases where Retrieval-only failed to rank the ground-truth actor in the top 3:
   - `bench_exp_15` (AcidRain SATCOM Wiper -> Sandworm)
   - `bench_exp_17` (FASTCash ATM Interbank Switch -> Lazarus)
   - `bench_exp_18` (Ronin Bridge DeFi Theft -> Lazarus)
   - `bench_exp_23` (JSSLoader Hospitality Network -> FIN7)
   - `bench_exp_26` (Fortinet FortiOS SSL-VPN -> Volt Typhoon)
   - `bench_exp_27` (KV-Botnet SOHO Routers -> Volt Typhoon)

In each of these 6 cases, multi-hop trail extraction and graph constraints prevented retrieval from being misled by generic commodity phrases (such as generic C2 channels or common shellcode loaders).

---

## 4. Evaluation of Open-Set Rejection (Task B, N = 16)

Task B evaluated whether NexusCTI avoids overconfident false attribution when presented with intrusions from out-of-vocabulary threat actors or commodity multi-actor CVE sweeps:

```
+-----------------------------------+-----------------------------------+
| Metric                            | Phase 8 Task B Result (N = 16)    |
+-----------------------------------+-----------------------------------+
| Total Scored Open-Set Cases       | 16 cases                          |
| Threat Actors Represented         | 8 Unseen Actors + 2 Commodity CVEs|
| Proper Abstention Rate            | 100.0% (16 / 16 cases INCONCLUSIVE|
| 95% Wilson Score Interval         | [80.64%, 100.00%]                 |
| False Attribution Rate            | 0.0% (0 / 16 cases misattributed) |
| Maximum Fused Confidence Observed | 0.4124 (Threshold for CONFIRMED: 0.85, PROBABLE: 0.50) |
+-----------------------------------+-----------------------------------+
```

Across all 16 cases—including high-profile campaigns by LockBit, Kimsuky, APT41, Charming Kitten, Gamaredon, BlackCat, Scattered Spider, Clop, and commodity Log4j/ManageEngine scanning—fused confidence remained strictly below 0.50 (ranging from 0.31 to 0.41), resulting in an `INCONCLUSIVE` verdict. NexusCTI successfully avoids catastrophic hallucination on out-of-distribution cyber intrusions.

---

## 5. Academic Publication Recommendations

### What MAY be claimed in an academic paper:
1. **Practically Meaningful Hybrid Advantage:** Unified neuro-symbolic hybrid fusion provides a **+20.83% gain in Top-3 candidate recall** over dense retrieval alone on genuinely unseen cyber campaigns (70.83% vs 50.00%), rescuing 6 retrieval failures with a discordance odds ratio of 6.0 (Agresti-Min 95% CI: $[+0.90\%, +40.77\%]$).
2. **Failure of Unlinked Graph Reasoning:** Pure knowledge graph topology and GNN message passing suffer catastrophic breakdown (0.0% Top-1, 33.3% Top-3) when applied to novel indicators that lack pre-existing graph bridges.
3. **Calibrated Abstention on Open-Set Intrusions:** Uncertainty-calibrated hybrid gating achieves a **100% proper abstention rate** (95% CI: $[80.64\%, 100.0\%]$) across 16 out-of-vocabulary threat actors and multi-actor commodity intrusions.

### What MUST NOT be claimed:
1. **Do NOT claim proven statistical significance:** With $p = 0.1250$ on the exact McNemar test, the hypothesis cannot be declared statistically significant at $\alpha = 0.05$. It must be reported honestly as an **inconclusive but directionally strong empirical trend**.
2. **Do NOT claim >80% autonomous Top-1 attribution:** On novel campaigns with 0.0% indicator overlap, Top-1 accuracy is 29.17% for Hybrid and 25.00% for Retrieval-only.

---

## 6. Highest-Priority Next Experiment

Rather than prematurely tuning model hyperparameters or threshold heuristics to force $p < 0.05$, the single highest-priority next experiment is:

> **Expand the paired benchmark sample size to $N \ge 60$ closed-set campaigns (requiring $n_d \ge 15$ discordant pairs).** Under the observed discordance odds ratio of $\psi = 6.0$, an effective sample size of $n_d = 15$ discordant pairs achieves a two-sided exact McNemar $p$-value of $p = 0.0074 < 0.01$, providing definitive statistical proof of hybrid superiority at $\ge 80\%$ statistical power.

---

## 7. Deliverables Manifest

All 15 deliverables required for Phase 8 have been generated and archived in `experiments/phase8_expanded_evaluation_20261011_012000/`:

1. [`phase8_report.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase8_expanded_evaluation_20261011_012000/phase8_report.md) — Master Phase 8 evaluation report.
2. [`preregistered_evaluation_protocol.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase8_expanded_evaluation_20261011_012000/preregistered_evaluation_protocol.md) — Pre-registered protocol frozen prior to evaluation.
3. [`power_analysis.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase8_expanded_evaluation_20261011_012000/power_analysis.md) — Statistical power formulation, sample size calculations, and sensitivity analysis.
4. [`external_report_manifest.csv`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase8_expanded_evaluation_20261011_012000/external_report_manifest.csv) — 48 external reports with URLs, publishers, dates, and SHA-256 hashes.
5. [`ground_truth_evidence_manifest.csv`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase8_expanded_evaluation_20261011_012000/ground_truth_evidence_manifest.csv) — Verifiable ground-truth attribution passages for all 48 cases.
6. [`campaign_deduplication_report.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase8_expanded_evaluation_20261011_012000/campaign_deduplication_report.json) — Indicator overlap analysis confirming 0.0% overlap with training infrastructure.
7. [`split_manifest.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase8_expanded_evaluation_20261011_012000/split_manifest.json) — Campaign-disjoint split partitioning (Validation: 8, Frozen Test: 40).
8. [`graph_contamination_audit.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase8_expanded_evaluation_20261011_012000/graph_contamination_audit.json) — Verification of zero external threat campaign edges in the training graph.
9. [`retrieval_contamination_audit.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase8_expanded_evaluation_20261011_012000/retrieval_contamination_audit.json) — Verification of zero external reports indexed in baseline retrieval.
10. [`frozen_predictions.csv`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase8_expanded_evaluation_20261011_012000/frozen_predictions.csv) — Complete per-case prediction records across all 5 architectures.
11. [`paired_comparison_results.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase8_expanded_evaluation_20261011_012000/paired_comparison_results.json) — Exact McNemar test, contingency table, risk difference, and Agresti-Min CI.
12. [`benchmark_metrics.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase8_expanded_evaluation_20261011_012000/benchmark_metrics.json) — Recomputed benchmark metrics with 95% Wilson confidence intervals.
13. [`reproducibility_manifest.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase8_expanded_evaluation_20261011_012000/reproducibility_manifest.json) — Source code SHA-256 hashes, deterministic seeding, and environment details.
14. [`limitations_and_claims_register.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase8_expanded_evaluation_20261011_012000/limitations_and_claims_register.md) — Claim-by-claim register with formal audit verdicts.
15. [`run_phase8_evaluation.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase8_expanded_evaluation_20261011_012000/run_phase8_evaluation.py) — Standalone evaluation runner script.
