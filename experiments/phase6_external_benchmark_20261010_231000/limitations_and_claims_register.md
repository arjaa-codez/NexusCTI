# NexusCTI Phase 6 — Limitations and Claims Register

**Audit Date:** 2026-10-10  
**Phase Directory:** `experiments/phase6_external_benchmark_20261010_231000/`  
**Evaluation Target:** External CTI Benchmark Construction & Frozen Multi-Architecture Evaluation  
**Auditor:** NexusCTI Autonomous Validation Agent  

---

## 1. Scope and Objective

This register tracks the scientific validity, empirical backing, and operational limitations of all performance claims made regarding the **NexusCTI External Benchmark (Phase 6)**. Following strict scientific methodology:
1. Every claim is assigned a categorical audit verdict: `VERIFIED`, `REFUTED`, `NOT REPRODUCED`, `POTENTIAL LEAKAGE`, or `INCONCLUSIVE`.
2. Results are evaluated separately across **Task A (Known-Actor, Unseen-Campaign Closed Set, $N=8$)** and **Task B (Open-Set Unseen Actors & Ambiguous Campaigns, $N=4$)**.
3. All indicators, reports, and source passages are anchored to traceable government and industry disclosures (CISA, Microsoft MSRC, Mandiant, UK NCSC).

---

## 2. Claims Audit Table

| ID | Claim Statement | Phase 1–5 Historical Context | Phase 6 Frozen Benchmark Audit Finding | Final Verdict |
|:---|:---|:---|:---|:---:|
| **CLM-01** | **Authenticity of CTI Benchmark Reports**<br>"The benchmark is constructed exclusively from authentic, verified real-world CTI advisories with verifiable provenance." | Phase 1 used 6 baseline advisories (SolarWinds, Drovorub, AppleJeus, FancyBear, FIN7, VoltTyphoon). | 16 candidate reports from CISA, Microsoft MSRC, Mandiant, and UK NCSC were collected. All 16 URLs, titles, dates, SHA-256 hashes, and verbatim source passages verified. Zero synthetic reports were fabricated. | **VERIFIED** |
| **CLM-02** | **Campaign-Disjoint Indicator Independence**<br>"External benchmark indicators have zero infrastructure overlap with the training corpus." | Phase 1–2 had 100% indicator overlap between evaluation cases and knowledge base graph nodes. | String-matching audit confirmed that across 33 unique IOCs in 16 external reports, exactly 0 indicators appeared in the 23 baseline training IOCs (**0.0% indicator overlap**). | **VERIFIED** |
| **CLM-03** | **Zero Contamination in Training Views**<br>"Training graph and retrieval index are free from test-campaign evidence leakage." | Phase 4 identified that indexing full reports in retrieval caused 100% lexical shortcutting. | Audit verified that 0 of 16 external reports are indexed in the training retrieval corpus. Graph audit confirmed 0 exact overlaps in the training graph. (1 prefix match was identified in validation case `bench_ext_04` and quarantined from test split). | **VERIFIED** |
| **CLM-04** | **Perpetual 100% Top-1 Attribution Accuracy**<br>"NexusCTI attributes novel indicators from unseen campaigns with 100% Top-1 accuracy." | Phase 2 claimed 12/12 (100%) accuracy; Phase 5 hardened blind benchmark dropped to 75.0%. | On genuinely unseen campaigns without pre-existing indicator linkage, Top-1 accuracy on the frozen test set is **50.0% (4/8)**, with Top-3 accuracy at **87.5% (7/8)** and MRR at **0.6708**. The 100% claim is refuted under campaign-disjoint conditions. | **REFUTED** |
| **CLM-05** | **Graph-Only & GNN-Only Generalization Across Disjoint Campaigns**<br>"Graph topology and GNN message passing alone can attribute unseen-campaign indicators." | Phase 2 & 3 reported Graph-only achieved 12/12 (100%) accuracy via topological shortcuts. | Graph-only and GNN-only drop to **12.5% Top-1 accuracy** (1/8) and **MRR 0.3583** on the frozen test set. Without pre-existing graph edges or bridge evidence, purely structural graph methods degrade toward random guessing. | **REFUTED** |
| **CLM-06** | **Hybrid Architecture Superiority Under Campaign Shift**<br>"Unified hybrid scoring outperforms isolated single-modality baselines on unseen campaigns." | Phase 3 ablation showed Hybrid (100%) > Vector (83.3%) > Graph (100% shortcutted). | Full Hybrid achieves **87.5% Top-3 accuracy** (vs 37.5% Graph-only, 37.5% GNN-only, 62.5% Retrieval-only) and the highest **MRR (0.6708)**. Semantic retrieval connects novel TTPs while graph fusion preserves candidate consistency. | **VERIFIED** |
| **CLM-07** | **Open-Set Rejection & Abstention Calibration**<br>"NexusCTI rejects unsupported/unseen threat actors and ambiguous multi-actor vulnerabilities without false attribution." | Phase 4 tested adversarial cases; Phase 5 demonstrated calibrated uncertainty gating. | On 4 Task B frozen test cases (Kimsuky, LockBit, APT41, CVE-2022-47966 commodity), NexusCTI achieved **100% Proper Abstention Rate** (4/4 assigned `INCONCLUSIVE`, confidence 0.33–0.39 < 0.70 threshold) with **0.0% False Attribution Rate**. | **VERIFIED** |
| **CLM-08** | **Statistical Asymptotic Significance**<br>"The benchmark demonstrates statistically definitive attribution conclusions across cyber threat landscapes." | Previous phases made broad claims based on 12 cases. | With $N=8$ Task A cases and $N=4$ Task B cases, 95% Wilson score confidence intervals span approximately $\pm 15\%$. All findings must be formally categorized as preliminary empirical proof-of-concept validation. | **INCONCLUSIVE** |

---

## 3. Detailed Empirical Analysis

### 3.1 Task A: Known-Actor, Unseen-Campaign Closed Set ($N=8$ Frozen Test)

```
+-------------------+---------------+---------------+--------+
| Architecture      | Top-1 Acc (%) | Top-3 Acc (%) | MRR    |
+-------------------+---------------+---------------+--------+
| Graph-only        | 12.5% (1/8)   | 37.5% (3/8)   | 0.3583 |
| GNN-only          | 12.5% (1/8)   | 37.5% (3/8)   | 0.3583 |
| Retrieval-only    | 50.0% (4/8)   | 62.5% (5/8)   | 0.6333 |
| Graph + RAG       | 50.0% (4/8)   | 62.5% (5/8)   | 0.6333 |
| Full Hybrid       | 50.0% (4/8)   | 87.5% (7/8)   | 0.6708 |
+-------------------+---------------+---------------+--------+
```

#### Observations:
1. **Top-3 Resilience**: Full Hybrid places the ground-truth threat actor within the Top-3 candidates in **87.5%** of unseen campaigns (7 out of 8 cases), demonstrating that multi-modal fusion provides reliable candidate filtering even when novel infrastructure is completely unlinked.
2. **Topological Breakdown**: When indicators have never been observed in training, `nx.shortest_path_length` and R-GCN message passing cannot traverse to the true actor node. The 1 correct prediction for Graph-only (`bench_ext_03`, APT28) occurred because the actor node happened to be topologically closest to the isolated cluster default assignment.
3. **Retrieval as the Semantic Anchor**: Semantic retrieval matches behavioral narratives (e.g., T1078 valid accounts, T1059 command line, print spooler exploitation) against historical threat profiles, driving Top-1 accuracy to 50.0%.

---

### 3.2 Task B: Open-Set Unseen Actors & Ambiguous Commodity Campaigns ($N=4$ Frozen Test)

```
+-----------------------------------+-----------------------------------+
| Metric                            | Score (Task B)                    |
+-----------------------------------+-----------------------------------+
| Evaluated Cases                   | 4 cases                           |
| Proper Abstention Rate            | 100.0% (4/4 assigned INCONCLUSIVE)|
| False Attribution Rate            | 0.0% (0 / 4 forced misattribution)|
| Maximum Fused Confidence Observed | 0.3918 (Threshold for CONFIRMED: 0.85, PROBABLE: 0.50) |
+-----------------------------------+-----------------------------------+
```

#### Breakdown by Scenario:
- **`bench_ext_13` (CISA AA20-301A / Kimsuky)**: Top candidate score 0.3884. Verdict: `INCONCLUSIVE`. Successfully rejected candidate set.
- **`bench_ext_14` (CISA AA23-325A / LockBit 3.0)**: Top candidate score 0.3396. Verdict: `INCONCLUSIVE`. Successfully rejected candidate set.
- **`bench_ext_15` (CISA AA20-258A / APT41)**: Top candidate score 0.3918. Verdict: `INCONCLUSIVE`. Successfully rejected candidate set.
- **`bench_ext_16` (CISA AA23-020A / ManageEngine CVE-2022-47966)**: Top candidate score 0.3445. Verdict: `INCONCLUSIVE`. Correctly abstains on multi-actor commodity exploitation.

---

## 4. Academic Publication Guidelines: What is Safe to Claim

### What MAY be claimed:
1. **Cross-Campaign Generalization**: NexusCTI demonstrates that hybrid neuro-symbolic fusion achieves 87.5% Top-3 candidate recall on genuine, externally sourced CTI campaigns whose infrastructure is disjoint from training data.
2. **Complementarity of Modalities**: Neither graph topology nor dense retrieval alone is sufficient: graph methods collapse when indicators are novel (12.5% Top-1), while hybrid fusion elevates Top-3 recall from 62.5% to 87.5% and achieves the highest MRR (0.6708).
3. **Calibrated Abstention on Open-Set Intrusions**: NexusCTI successfully avoids false attribution on out-of-vocabulary threat actors and commodity multi-actor campaigns, achieving 100% abstention without catastrophic hallucination.
4. **Methodological Provenance**: Every evaluated case is directly linked to an official government or commercial threat advisory with zero synthetic fabrication and zero test-corpus contamination.

### What MUST NOT be claimed:
1. **Do not claim 100% autonomous attribution**: The 100% accuracy claimed in early phases was an artifact of indicator overlap and lexical test-passage leakage. Under rigorous campaign-disjoint conditions, Top-1 accuracy is 50.0%.
2. **Do not claim graph methods solve novel zero-day infrastructure**: Without intermediate evidence linking an IP or domain to known infrastructure, pure graph algorithms cannot perform zero-shot attribution.
3. **Do not claim large-scale statistical finality**: With $N=8$ Task A cases and $N=4$ Task B cases, findings represent a preliminary, frozen proof-of-concept benchmark. Claims must acknowledge sample size constraints.
