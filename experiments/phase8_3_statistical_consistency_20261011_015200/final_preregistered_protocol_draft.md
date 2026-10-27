# NexusCTI — Final Pre-Registered Benchmark Protocol (Draft v1.0)

**Document Type:** Formal Pre-Registration Study Protocol  
**Audit Date:** 2026-10-11  
**Target Study:** Independent Cross-Campaign Attribution Benchmark (Phase 9)  
**Governance:** NexusCTI Independent Scientific Review Board  
**Status:** FROZEN PRE-REGISTRATION SPECIFICATION  

---

## 1. Study Objectives & Primary Endpoint

### 1.1 Primary Objective
To determine whether NexusCTI's **Full Hybrid architecture** (combining Knowledge Graph R-GCN reasoning with dense semantic retrieval) achieves a statistically significant and practically meaningful improvement over the **Retrieval-only baseline** in attributing previously unseen, real-world cyber threat campaigns to known threat actors under closed-set conditions.

### 1.2 Primary Endpoint
- **Endpoint Definition:** Paired Top-3 attribution correctness on eligible Task A closed-set campaign cases.
- **Binary Indicator:** For campaign $i \in \{1, \dots, N\}$, $Y_{H,i} = 1$ if the true ground-truth threat actor is present in Full Hybrid's Top-3 candidate ranking, else $0$. Similarly, $Y_{R,i} = 1$ if the true actor is present in Retrieval-only's Top-3 ranking, else $0$.

### 1.3 Secondary Endpoints
- **Top-1 Attribution Accuracy:** Exact match of the rank-1 predicted threat actor.
- **Mean Reciprocal Rank (MRR):** Reciprocal rank of the ground-truth threat actor in the candidate list.
- **Task B Open-Set Rejection AUROC:** Ability to abstain or flag unrepresented novel threat actors based on attribution confidence.

---

## 2. Statistical Analysis Plan & Decision Boundaries

### 2.1 Primary Hypothesis Test
- **Test:** Exact Two-Sided McNemar Test on discordant pairs ($n_d = b + c$).
- **Null Hypothesis ($H_0$):** $\theta = P(Y_{H,i} = 1 \mid Y_{H,i} \ne Y_{R,i}) = 0.50$ (neither system has an advantage on discordant cases).
- **Alternative Hypothesis ($H_1$):** $\theta \ne 0.50$.
- **Significance Level:** $\alpha = 0.05$ (two-sided).
- **Implementation:** Exact binomial test on Hybrid wins $B \sim \text{Binomial}(n_d, 0.50)$ via SciPy `stats.binomtest(b, b + c, p=0.5, alternative='two-sided')`.

### 2.2 Pre-Registered Confidence Intervals & Estimands
To prevent post-hoc interval shopping, the following estimators are frozen:
1. **Primary Test Estimand (Conditional Odds Ratio):**
   - Estimand: $\psi = \frac{b}{c} = \frac{\theta}{1 - \theta}$.
   - Method: Exact Conditional Fisher/Clopper-Pearson 95% Confidence Interval.
   - Purpose: Direct inversion of the primary McNemar test.
2. **Primary Marginal Risk Difference Estimand:**
   - Estimand: $\Delta = p_{\text{hybrid}} - p_{\text{retrieval}} = \frac{b - c}{N}$.
   - Method: **Agresti-Min Paired Pseudocount Interval** (+0.5 per cell / +2 overall).
   - Rationale: Fully maintains nominal 95% coverage across finite samples, avoids the severe undercoverage of uncorrected Wald ($n_d < 20$), and avoids false-positive claims.
   - Secondary Sensitivity Interval: Continuity-Corrected Wald Interval.

### 2.3 Practical Significance Bar
- **Practical Effect Threshold:** $\Delta \ge +15.0$ percentage points in marginal Top-3 accuracy.
- **Formal Decision Rule:** Full Hybrid is declared scientifically superior **if and only if**:
  1. The exact two-sided McNemar test achieves $p \le 0.05$, **AND**
  2. The observed marginal risk difference meets or exceeds the practical threshold ($\hat{\Delta} \ge +15.0\%$).
- **Rule on Non-Significance:** If $p > 0.05$, the evaluation outcome **must remain strictly classified as inconclusive**. Post-hoc pooling, sub-group re-stratification, metric switching, or threshold tuning are strictly prohibited.

---

## 3. Sample Size & Prospective Power Specification

### 3.1 Sample Size Allocation
```
+--------------------------------------------------------------------------------------------------------+
| PRE-REGISTERED BENCHMARK SAMPLE SIZE ALLOCATION                                                        |
+--------------------------+-------------------+---------------------------------------------------------+
| Benchmark Component      | Sample Size       | Selection Rationale                                     |
+--------------------------+-------------------+---------------------------------------------------------+
| Task A (Closed-Set)      | N = 100 cases     | Powered at 83.7% for Δ = +15% effect (θ=0.80, q=0.25)    |
| Task B (Open-Set)        | N = 30 cases      | Evaluates anomaly abstention on novel threat actors     |
| Development Set (Held)   | N = 15 cases      | Sanity checking without touching the frozen test set    |
| TOTAL CAMPAIGN POOL      | N = 145 cases     | Rigorous, independent cross-campaign corpus             |
+--------------------------+-------------------+---------------------------------------------------------+
```

### 3.2 Explicit Power Planning Assumptions
- **Planning Discordance Rate ($q$):** $q = 0.25$ (assumes systems disagree on 25% of cases).
- **Planning Win Rate ($\theta$):** $\theta = 0.80$ (Hybrid wins 4 out of every 5 disagreements).
- **Target Effect Size ($\Delta$):** $\Delta = q \times (2\theta - 1) = 0.25 \times 0.60 = +15.0\%$.
- **Exact Analytical Power at $N = 100$:** **$83.67\%$** (verified by $M = 20,000$ Monte Carlo trials: $83.06\% \pm 0.27\%$).
- **Contingency Sizing ($N = 80$):** If CTI report curation constraints cap Task A at $N = 80$, the protocol acknowledges that power drops to **$73.68\%$** for a $+15\%$ effect, and the study will be transparently documented as having an elevated 26.3% risk of Type II error.

---

## 4. Benchmark Integrity & Anti-Leakage Protocol

### 4.1 Campaign-Level Independence & Deduplication
- **Intrusion Deduplication:** Multiple advisories, syndicated vendor blog posts, or localized CISA/CERT alerts documenting the same underlying operational activity must be deduplicated into a single canonical campaign entity.
- **Temporal Disjointness:** Test campaigns must originate from distinct time horizons or distinct intrusion sets relative to the training corpora.

### 4.2 Threat Actor Diversity
- **Actor Coverage:** Task A must include at least 10–14 distinct threat actors representing diverse geopolitical regions (e.g., APT28, APT29, Lazarus Group, Sandworm, Volt Typhoon, BlackCat, LockBit).
- **Clustering Ceiling:** No single threat actor may account for more than 12% of the Task A cases ($N_{\text{max}} = 12$ cases per actor).

### 4.3 Ground-Truth Verification Standards
- **Explicit Provenance:** Ground truth must be supported by explicit, high-confidence attribution statements from authoritative vendors or government agencies (e.g., CISA, Mandiant, Microsoft, CrowdStrike).
- **Quarantine of Low-Confidence Cases:** Any campaign where attribution is described as "suspected", "affiliated", or "probable" without definitive IOC clustering must be relegated to Task B.

### 4.4 Cryptographic System Freezing
Prior to scoring any test campaign:
1. **Model Weights:** R-GCN checkpoint weights, dense encoder embeddings, and linear projection heads must be cryptographically hashed.
2. **Knowledge Graph:** The training knowledge graph (entities, relations, telemetry) must be frozen.
3. **Retrieval Corpus:** The vector database must be frozen and quarantined; no text from test campaigns may be present in the indexed corpus.
4. **Decision Thresholds & Weights:** Fusion weights ($w_{\text{GNN}}, w_{\text{dense}}, w_{\text{sparse}}$) and confidence cutoffs must remain fixed.
5. **Pre-Scoring Hash Manifest:** An `artifact_hash_manifest.json` must be committed before predictions are generated.

### 4.5 Auditing for Data Contamination
- **Telemetry Leakage:** 0.0% overlap between test campaign observables (IPs, domains, hashes) and training knowledge graph edges.
- **Textual Leakage:** MinHash / n-gram near-duplicate checks between test report text and retrieval corpus chunks (Jaccard similarity threshold $< 0.15$).

---

## 5. Case-Flow Accounting & Missing Data Rules

```
+--------------------------------------------------------------------------------------------------------+
| CASE FLOW ACCOUNTING SCHEMA                                                                            |
+--------------------------------------------------------------------------------------------------------+
| 1. Candidate Campaigns Screened                                                 [N_screened]           |
| 2. Excluded: Duplicate campaign / syndicated report                             [-N_dup]               |
| 3. Excluded: Inadequate ground-truth provenance                                 [-N_prov]              |
| 4. Excluded: Contamination with training telemetry                             [-N_leak]              |
| 5. Eligible Closed-Set Campaigns (Task A)                                       [N_task_a = 100]       |
| 6. Eligible Open-Set Campaigns (Task B)                                         [N_task_b = 30]        |
| 7. Reserved Development Campaigns                                               [N_dev = 15]           |
+--------------------------------------------------------------------------------------------------------+
```

- **Logging Exclusions:** Every excluded campaign must be logged with timestamp, source URL, and exact exclusion reason prior to scoring.
- **No Mid-Trial Dropouts:** Once a case enters the frozen test set, it cannot be dropped, modified, or re-labeled. Missing system outputs will be scored as incorrect ($Y_i = 0$).

---

## 6. Reproduction Protocol

- **Executable Automation:** The entire benchmark evaluation, scoring pipeline, and statistical test suite must run via a single Python script (`run_benchmark_evaluation.py`).
- **Independent Verification:** An independent reviewer must be able to clone the repository, run the evaluation script against the frozen test artifacts, and reproduce the contingency table, exact intervals, and $p$-values with bitwise equivalence.
