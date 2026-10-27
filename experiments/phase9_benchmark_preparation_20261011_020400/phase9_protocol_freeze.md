# NexusCTI Phase 9 — Prospective Benchmark Preparation and Protocol Freeze

**Document Version:** 1.0 (Master Pre-Registration Protocol Freeze)  
**Date:** 2026-10-11  
**Auditor / Protocol Officer:** NexusCTI Independent Audit Agent (Phase 9)  
**Experiment Root:** `experiments/phase9_benchmark_preparation_20261011_020400/`  
**Prior Baselines Audited (Read-Only):**
- Phase 8: `experiments/phase8_expanded_evaluation_20261011_012000/`
- Phase 8.1: `experiments/phase8_1_independent_audit_20261011_013000/`
- Phase 8.2: `experiments/phase8_2_power_and_verification_20261011_014200/`
- Phase 8.3: `experiments/phase8_3_statistical_consistency_20261011_015200/`

---

## Executive Summary

Phase 9 completes the formal preparation, system freezing, benchmark construction, anti-leakage auditing, pipeline stress testing, and protocol pre-registration for the prospective independent evaluation of **NexusCTI Full Hybrid versus Retrieval-only**.

In strict accordance with scientific integrity standards:
1. **Zero System Modifications:** No models were trained, retrained, or fine-tuned. Graph topology, R-GCN weights, ChromaDB embeddings, fusion weights, and confidence thresholds remain cryptographically locked.
2. **Zero Test Prediction Inspection:** No evaluation was conducted on the newly curated test set. This phase is dedicated exclusively to benchmark preparation and pre-registration.
3. **Comprehensive Protocol Freeze:** The study design, primary endpoints, exact statistical tests, primary confidence interval estimators, practical significance bars, and case-flow rules are permanently registered before examining test predictions.

---

## 1. System Freezing & Cryptographic Manifest

All system components, models, databases, and source files have been recorded in [`frozen_system_manifest.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_benchmark_preparation_20261011_020400/frozen_system_manifest.json):

```
+--------------------------------------------------------------------------------------------------------+
| FROZEN SYSTEM ARTIFACT REGISTRY                                                                        |
+--------------------------+---------------------------------------------------+-------------------------+
| Component Category       | Artifact Path                                     | SHA-256 Digest (Trunc)  |
+--------------------------+---------------------------------------------------+-------------------------+
| R-GCN Checkpoint Weights | cyber_attribution_engine/data/processed_graph/...  | cb20c29f6916e788...     |
| Heterogeneous Graph      | cyber_attribution_engine/data/processed_graph/...  | 7f9ad2e240212e3e...     |
| Graph Metadata           | cyber_attribution_engine/data/processed_graph/...  | 17b8f2cfaefab754...     |
| ChromaDB Vector Database | cyber_attribution_engine/data/chroma_db/chroma... | a0a0e28f3216834b...     |
| Training Report 1        | data/raw_reports/cisa_aa20_352a_apt29_solarwinds  | 9851e4bb2ec844b2...     |
| Training Report 2        | data/raw_reports/cisa_aa22_054a_sandworm_industr. | fa11566378e9f2d1...     |
| Training Report 3        | data/raw_reports/cisa_aa22_110a_lazarus_applejeus | e7dfbd4563a35bfa...     |
| Training Report 4        | data/raw_reports/cisa_aa23_074a_apt28_fancybear   | f8e390cbfbb5e468...     |
| Training Report 5        | data/raw_reports/cisa_aa24_038a_volt_typhoon      | 46f9037c729c15ff...     |
| Training Report 6        | data/raw_reports/mandiant_m_trends_fin7           | bfb93a02bb8efc83...     |
| GNN Reasoning Code       | cyber_attribution_engine/src/gnn_model.py         | 1c5e62bc123f009e...     |
| Graph Construction Code  | cyber_attribution_engine/src/graph_builder.py     | 7a21394be5c422aa...     |
| Vector Retrieval Code    | cyber_attribution_engine/src/rag_engine.py        | 894cf7ef6fae1011...     |
| Score Fusion Code        | cyber_attribution_engine/src/fusion_layer.py      | 61cf941a8e2cb6f6...     |
| Engine API Code          | cyber_attribution_engine/src/api.py               | a201ef4cf66ef610...     |
+--------------------------+---------------------------------------------------+-------------------------+
```

### Frozen Architectural Hyperparameters:
- **Fusion Formula:** $S(A_i \mid \text{IOC}) = \alpha \cdot \text{Softmax}(z_{\text{IOC}}^T z_{A_i}) + (1 - \alpha) \cdot \max_{d \in D_k} \text{Sim}_{\cos}(E_q, E_d)$ with **$\alpha = 0.50$**.
- **GNN Structure:** 2-layer Relational Graph Convolutional Network (R-GCN), 64 hidden channels, 4 relation bases, dropout 0.10.
- **Dense Retriever:** `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional embeddings, cosine similarity, top-3 chunk retrieval).
- **Candidate Closed Set (6 Threat Actors):** `actor_apt28`, `actor_apt29`, `actor_lazarus`, `actor_sandworm`, `actor_volt_typhoon`, `actor_fin7`.
- **Decision & Abstention Thresholds:** Confirmed ($\ge 0.70$), Probable ($\ge 0.50$), Inconclusive ($< 0.50$). Open-set anomaly abstention margin: top-1 margin $< 0.15$.

---

## 2. Independent Benchmark Construction & Deduplication

### 2.1 Benchmark Composition
The candidate campaign pool was structured and verified in [`candidate_campaign_manifest.csv`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_benchmark_preparation_20261011_020400/candidate_campaign_manifest.csv) and [`campaign_deduplication_report.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_benchmark_preparation_20261011_020400/campaign_deduplication_report.md):

```
+--------------------------------------------------------------------------------------------------------+
| FINAL BENCHMARK STRUCTURE & PARTITIONS                                                                 |
+--------------------------+-------------------+---------------------------------------------------------+
| Benchmark Partition      | Case Count        | Partition Role & Design Constraints                     |
+--------------------------+-------------------+---------------------------------------------------------+
| Task A (Closed-Set Test) | N = 100 cases     | Primary hypothesis test: Full Hybrid vs Retrieval-only  |
| Task B (Open-Set Test)   | N = 30 cases      | Evaluates novelty detection and anomaly abstention      |
| Development Partition    | N = 15 cases      | Reserved for pre-test calibration & sanity checking     |
| Collapsed Duplicate Rpts | N = 10 reports    | Multi-vendor syndications collapsed into primary units  |
| Excluded Candidates      | N = 10 reports    | Ineligible due to contamination, weak evidence, etc.    |
| TOTAL SCREENED RECORDS   | N = 165 records   | Comprehensively accounted candidate pool                |
+--------------------------+-------------------+---------------------------------------------------------+
```

### 2.2 Deduplication & Independence Enforcement
- **Collapsed Reports:** 10 syndicated reports describing previously covered intrusions (e.g. CISA, Microsoft, and Mandiant advisories on Drovorub, TeamCity, GooseEgg, and AppleJeus) were collapsed into their primary canonical campaign entities to eliminate pseudo-replication.
- **Threat Actor Balance (Task A):** Cases span all 6 candidate threat actors with strict balance: APT28 ($N=17$), APT29 ($N=17$), Lazarus Group ($N=17$), Sandworm ($N=17$), Volt Typhoon ($N=16$), FIN7 ($N=16$). No actor exceeds $17\%$ of the test set, preventing representation skew.
- **Open-Set Task Separation (Task B):** 30 campaigns represent unrepresented novel threat actors (Charming Kitten, Gamaredon, ALPHV/BlackCat, Scattered Spider, CL0P, LockBit, Kimsuky, Mustang Panda) and ambiguous commodity multi-actor CVEs (Log4j, ManageEngine).

---

## 3. Multi-Tier Leakage Audit Results

The multi-tier leakage audit documented in [`leakage_audit_report.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_benchmark_preparation_20261011_020400/leakage_audit_report.md) verified the following before evaluation:

1. **Exact & Normalized Indicator Overlap:** 0 matching IOCs between the 130 test campaigns and the 1,428 training graph/report tokens (**PASSED: 0.0% overlap**).
2. **Textual Retrieval Corpus Leakage:** 0 direct text chunks present in ChromaDB; 3-gram Jaccard similarity peaked at 0.042, below the 0.15 threshold (**PASSED: 0.0% text leakage**).
3. **Graph Topological Encoding:** 0 test campaign nodes or pre-encoded indicator-to-actor edges present in `hetero_graph.pt` (**PASSED: Topological independence confirmed**).
4. **Behavioral Profile / Label Leakage:** Inference query inputs contain strictly technical observables; actor metadata, vendor tags, and ground-truth labels are completely stripped (**PASSED: Input queries are blind**).
5. **Cross-Partition Disjointness:** 0 campaign overlap between the 15 development cases and 130 test cases (**PASSED: Partitions are strictly disjoint**).

---

## 4. Pre-Registered Analysis Plan & Decision Rules

To eliminate researcher degrees of freedom, the statistical analysis plan is frozen prior to generating test predictions:

### 4.1 Primary Endpoint & Comparison
- **Endpoint:** Paired Top-3 attribution correctness on eligible Task A closed-set campaigns ($N = 100$).
- **Primary Comparison:** NexusCTI Full Hybrid versus Retrieval-only.

### 4.2 Primary Hypothesis Test
- **Test:** Exact Two-Sided McNemar Test on discordant pairs ($n_d = b + c$).
- **Significance Threshold:** $\alpha = 0.05$ (two-sided).
- **Implementation:** SciPy `stats.binomtest(b, b + c, p=0.5, alternative='two-sided')`.

### 4.3 Pre-Registered Confidence Interval Estimators
- **Primary Test Estimand:** Conditional Odds Ratio $\psi = b/c$ with **Exact Conditional Fisher / Clopper-Pearson 95% Confidence Interval**.
- **Primary Risk Difference Estimand:** Marginal paired risk difference $\Delta = p_1 - p_2 = (b - c) / N$ with **Agresti-Min Paired Pseudocount Interval** (+0.5 per cell / +2 overall).
  - *Secondary Sensitivity Check:* Continuity-Corrected Wald Interval.

### 4.4 Practical Effect Threshold & Formal Decision Rule
- **Practical Threshold:** Marginal Top-3 accuracy advantage **$\Delta \ge +15.0$ percentage points**.
- **Superiority Declaration:** Full Hybrid is declared scientifically superior **if and only if**:
  1. The exact two-sided McNemar test achieves **$p \le 0.05$**, **AND**
  2. The observed paired risk difference meets or exceeds **$\hat{\Delta} \ge +15.0\%$**.
- **Rule on Non-Significance:** If $p > 0.05$, the evaluation outcome **must remain strictly classified as inconclusive**. Post-hoc pooling, subgroup slicing, metric changes, or threshold relaxation are strictly prohibited.

---

## 5. Sample Size & Prospective Power Justification

Detailed in [`sample_size_and_power_justification.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_benchmark_preparation_20261011_020400/sample_size_and_power_justification.md):
- **Planning Parameters:** Discordance rate $q = 0.25$, conditional win rate $\theta = 0.80$, implied $\Delta = +15.0\%$.
- **Exact Analytical Power at $N = 100$:** **$83.67\%$** (verified by $M = 20,000$ Monte Carlo trials: $83.06\% \pm 0.27\%$).
- **Rejection of $N = 60$:** Sizing at $N = 60$ yields only $58.1\%$ power under the $+15\%$ objective (a $41.9\%$ risk of a false negative), making it inadequate for confirmatory science.
- **Contingency Minimum:** $N = 80$ ($73.7\%$ power) represents the absolute minimum permissible floor. Any evaluation with $N < 80$ is classified as an exploratory pilot.

---

## 6. Evaluation Pipeline Stress Testing

Detailed in [`evaluation_pipeline_test_report.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_benchmark_preparation_20261011_020400/evaluation_pipeline_test_report.md) and `pipeline_validation_data.json`:
- **Synthetic Edge Cases Validated:**
  - TC-1 (All concordant correct, $n_d=0$): Output $p=1.000$, $\Delta=0.0\%$, intervals symmetric around 0.
  - TC-2 (All concordant incorrect, $n_d=0$): Output $p=1.000$, $\Delta=0.0\%$.
  - TC-3 (Zero cell $c=0$, $b=25$): Evaluated $\psi = \text{inf}$ gracefully; exact lower bound $\psi_{\text{low}} = 6.299$; $p < 0.001$; Agresti-Min $[+24.7\%, +49.6\%]$.
  - TC-4 (Zero cell $b=0$, $c=25$): Evaluated $\psi = 0.0$ gracefully; upper bound $\psi_{\text{high}} = 0.159$.
  - TC-5 (Balanced discordance $b=10, c=10$): Output $p=1.000$, $\Delta=0.0\%$.
  - TC-6 (Strong advantage $b=20, c=5, N=85$): Output $p=0.004077$, $\Delta=+17.65\%$, correctly flagged as statistically and practically significant.
  - TC-7 (Small sample tie $b=1, c=1, N=12$): Output $p=1.000$, $\Delta=0.0\%$.
- **Missing / Invalid Prediction Policy:** Any missing or invalid prediction is deterministically assigned Rank = 99 ($Y_i = 0$, incorrect) without imputation or crash.

---

## 7. Readiness Determination & Epistemological Separation

### 7.1 Readiness Declaration
The NexusCTI systems, models, databases, candidate campaign benchmark, and statistical evaluation pipeline are **officially verified, frozen, and ready for prospective, untouched benchmark evaluation**.

### 7.2 Epistemological Separation of Status

```
========================================================================================================
FINAL EPISTEMOLOGICAL SEPARATION (PHASE 9)
========================================================================================================
Verified Findings:         - Systems and source files are cryptographically hashed and locked.
                           - Benchmark contains 100 eligible Task A and 30 eligible Task B canonical units.
                           - Multi-tier leakage audit passed with 0.0% indicator, text, or graph overlap.
                           - Evaluation scoring pipeline passed all 7 synthetic edge-case tests.
--------------------------------------------------------------------------------------------------------
Method-Dependent Results:  - Confidence intervals for paired risk difference depend on finite-sample
                             correction; Agresti-Min (+2 pseudocount) is pre-registered to prevent
                             the known undercoverage of uncorrected Wald and Newcombe 10.
--------------------------------------------------------------------------------------------------------
Planning Assumptions:      - The prospective parameters q = 0.25 (discordance) and θ = 0.80 (win rate)
                             are planning models, NOT established physical facts.
                           - The power figure of 83.67% at N = 100 is conditional on these assumptions.
                             A larger sample size does not guarantee statistical significance.
--------------------------------------------------------------------------------------------------------
Unresolved Risks:          - Real-world CTI reporting exhibits latent vendor reporting bias.
                           - If real-world discordance between the systems is lower than q = 0.25,
                             actual statistical power will be lower than 83.7%.
                           - Open-set anomaly detection (Task B) requires independent operational
                             calibration and cannot be inferred from closed-set accuracy alone.
========================================================================================================
```
