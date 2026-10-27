# NexusCTI Phase 8 — Limitations and Claims Register

**Audit Date:** 2026-10-11  
**Experiment Root:** `experiments/phase8_expanded_evaluation_20261011_012000/`  
**Evaluation Scope:** Pre-Registered Expanded External Benchmark ($N = 48$ Campaigns across 14 Threat Actors)  

---

## 1. Summary of Claims & Formal Verdicts

| ID | Claim Statement | Phase 8 Pre-Registered Benchmark Finding | Final Verdict |
|:---|:---|:---|:---:|
| **CLM-P8-01** | **Dataset Authenticity & Scale**<br>"Benchmark comprises 48 verified, non-fabricated primary reports across 14 distinct threat actors." | 48 primary CTI reports (CISA, FBI, NSA, Microsoft, Mandiant, ESET, UK NCSC, CERT-UA, SentinelOne) verified with canonical URLs, dates, and verbatim excerpts. 0 synthetic reports. | **VERIFIED** |
| **CLM-P8-02** | **Infrastructure Disjointness**<br>"Zero indicator overlap with training data across all 48 campaigns." | String deduplication across 48 external indicators and 23 baseline training IOCs confirmed exactly 0 overlaps (**0.0% overlap**). | **VERIFIED** |
| **CLM-P8-03** | **Zero Contamination in Training Views**<br>"Zero external reports indexed in retrieval corpus, zero external edges in training graph." | Audits confirmed 0 external reports indexed in baseline retrieval, and 0 external indicators present in the training graph. | **VERIFIED** |
| **CLM-P8-04** | **Primary Hypothesis: Hybrid Superiority over Retrieval-Only**<br>"Full Hybrid provides a statistically significant improvement over Retrieval-only on Top-3 accuracy on unseen campaigns." | On Task A frozen test cases ($N=24$), Full Hybrid achieved 70.83% Top-3 (17/24) vs Retrieval-only 50.00% (12/24). While the risk difference is +20.83% (95% CI: [0.9%, 40.8%], odds ratio 6.0), the exact McNemar $p$-value is $p = 0.1250 > 0.05$. Under the pre-registered protocol, the result is inconclusive. | **INCONCLUSIVE** |
| **CLM-P8-05** | **Practical Meaningfulness of Hybrid Effect**<br>"The observed Top-3 difference between Hybrid and Retrieval meets the pre-registered threshold for practical importance ($\Delta \ge +15.0\%$). | Observed risk difference is $\Delta = +20.83\%$ with lower bound of 95% CI strictly positive at $+0.90\%$. Hybrid fixed 6 retrieval errors while retrieval fixed only 1 hybrid error ($b=6, c=1$). | **VERIFIED (Directionally)** |
| **CLM-P8-06** | **Topological Graph Degradation on Novel Indicators**<br>"Graph-only and GNN-only architectures collapse on unlinked novel campaign indicators." | Both Graph-only and GNN-only achieved 0.0% Top-1 accuracy (0/24) and 33.33% Top-3 accuracy (8/24, MRR 0.2604), demonstrating topological breakdown when indicators lack pre-existing graph bridges. | **VERIFIED** |
| **CLM-P8-07** | **Open-Set Rejection & Abstention Robustness**<br>"NexusCTI rejects out-of-vocabulary threat actors and commodity intrusions without false attribution." | Across 16 Task B frozen cases (Kimsuky, LockBit, APT41, Charming Kitten, Gamaredon, BlackCat, Scattered Spider, Clop, and commodity multi-actor CVEs), proper abstention was 16/16 (100.0%, 95% Wilson CI: [80.6%, 100.0%]) with 0.0% false attribution. | **VERIFIED** |
| **CLM-P8-08** | **High-Confidence Attribution Accuracy**<br>"NexusCTI attributes unseen campaigns with >80% Top-1 accuracy." | Top-1 accuracy across novel campaigns without direct graph linkage is 29.17% (7/24) for Full Hybrid and 25.00% (6/24) for Retrieval-only. Overconfident attribution claims are refuted. | **REFUTED** |

---

## 2. Pre-Registered Decision Conclusion

According to Section 9 of the pre-registered protocol:
- **Decision:** **RESULTS ARE INCONCLUSIVE.**
- **Rationale:** While the point estimate shows a large and practically meaningful advantage ($\Delta = +20.83\%$, odds ratio $\psi = 6.0$), the paired test on $n_d = 7$ discordant pairs yields an exact two-sided binomial $p$-value of $0.1250$, failing the pre-registered $\alpha = 0.05$ significance threshold.
- **Academic Recommendation:** It is scientifically valid to report that neuro-symbolic fusion shows strong positive directional trends ($\Delta = +20.83\%$, Agresti-Min 95% CI $[+0.9\%, +40.8\%]$) and rescues 6 retrieval failures, but claims of definitive statistical superiority must await further benchmark scaling to $N \ge 60$ paired cases.
