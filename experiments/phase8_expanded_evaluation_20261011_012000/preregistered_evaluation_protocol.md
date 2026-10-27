# NexusCTI Phase 8 — Pre-Registered Evaluation Protocol

**Document Version:** 1.0 (Pre-Registered Frozen Protocol)  
**Date of Registration:** 2026-10-11T01:20:00+05:30  
**Repository Root:** `c:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI`  
**Experiment Root:** `experiments/phase8_expanded_evaluation_20261011_012000/`  
**Status:** FROZEN PRIOR TO TEST EVALUATION  

---

## 1. Scientific Objective and Context

The primary objective of Phase 8 is to perform an expanded, prospective, pre-registered evaluation to definitively resolve the core scientific question of the NexusCTI project:

> **Primary Research Question:** Does the Unified Full Hybrid architecture (combining Relational Graph Convolutional Networks, Topological Knowledge Graph distance, and Dense Vector Retrieval) provide a statistically reproducible and practically meaningful improvement over the Retrieval-only baseline on genuinely unseen cyber threat campaigns?

In Phase 6, preliminary evaluation across $N=8$ closed-set cases reported Full Hybrid Top-3 accuracy of 87.5% (7/8) vs. Retrieval-only 62.5% (5/8). However, the Phase 7 independent audit proved that this observed difference was statistically non-significant (exact McNemar $p = 0.5000$) due to small sample size.

Phase 8 expands the empirical evaluation to an adequately powered benchmark ($N \ge 40$ campaign cases spanning $\ge 10$ threat actors) under strict pre-registration constraints.

---

## 2. Pre-Registered Hypotheses and Endpoints

### 2.1 Primary Hypothesis ($H_1$)
- **Formal Hypothesis:** On a campaign-disjoint benchmark of unseen cyber threat campaigns, the Full Hybrid architecture achieves a higher Top-3 attribution accuracy than the Retrieval-only baseline:
  $$H_0: P(\text{Hybrid correct}, \text{Retrieval incorrect}) = P(\text{Retrieval correct}, \text{Hybrid incorrect}) \quad (b = c)$$
  $$H_1: P(\text{Hybrid correct}, \text{Retrieval incorrect}) > P(\text{Retrieval correct}, \text{Hybrid incorrect}) \quad (b > c)$$
- **Primary Endpoint:** The paired per-case difference in Top-3 attribution correctness on the Task A closed-set frozen test split.

### 2.2 Secondary Endpoints
1. **Top-1 Attribution Accuracy:** Exact match of the highest-ranked actor against the ground truth.
2. **Mean Reciprocal Rank (MRR):** $\frac{1}{N} \sum_{i=1}^N \frac{1}{\text{rank}_i}$, where $\text{rank}_i \in [1, 6]$ (or $0.0$ if rank $> 6$).
3. **Open-Set Abstention Performance (Task B):** Proper abstention rate on out-of-vocabulary threat actors and ambiguous multi-actor vulnerabilities (verdict = `INCONCLUSIVE`).
4. **False Attribution Rate (Task B):** Proportion of Task B cases assigned confident attribution (`CONFIRMED` or `PROBABLE`) to any closed-set actor.
5. **Per-Actor Macro-Averaged Performance:** Balanced accuracy across the 6 represented candidate actors.
6. **Inference Latency:** Mean and 95th percentile wall-clock latency per case.

### 2.3 Minimally Meaningful Effect Size
- The smallest effect considered practically meaningful for cyber threat intelligence analysts is **$\Delta \text{Top-3} \ge +15.0\%$** (or an odds ratio of discordant pairs $\psi = b/c \ge 2.5$). A smaller gain does not justify the computational overhead of maintaining a relational graph convolutional network alongside dense vector search.

---

## 3. Statistical Testing and Multiplicity Control

1. **Primary Test:** Two-sided Exact McNemar Test on the paired contingency table of Top-3 correctness for Task A test cases:
   - Discordant pairs:
     - $b$: Full Hybrid correct, Retrieval-only incorrect.
     - $c$: Retrieval-only correct, Full Hybrid incorrect.
   - Exact binomial test under $H_0: p = 0.5$ on $n = b + c$:
     $$p\text{-value} = 2 \times \sum_{k=b}^{n} \binom{n}{k} 0.5^n \quad (\text{if } b > c)$$
2. **Significance Level:** $\alpha = 0.05$ (two-tailed).
3. **Confidence Interval Methods:**
   - Single proportions (Top-1, Top-3, Abstention): **95% Wilson Score Interval**.
   - Paired risk difference ($\Delta = p_{\text{hybrid}} - p_{\text{retrieval}}$): **Agresti-Min Paired Score Interval**.
4. **Multiple Comparison Policy:**
   - Strict hierarchical testing order: Primary endpoint evaluated at $\alpha = 0.05$.
   - Secondary endpoints (Top-1, MRR) are exploratory; adjusted $p$-values computed via Benjamini-Hochberg False Discovery Rate (FDR) control at $q = 0.05$.
5. **Missing Data Policy:**
   - No data imputation. Cases where an engine fails to output a prediction are coded as incorrect (Rank = 99, Reciprocal Rank = 0.0).

---

## 4. Frozen System Configurations and Hyperparameters

No model weights, graph structures, or threshold parameters may be altered during or after evaluating the frozen test set.

### 4.1 Architectures Evaluated (5-Way Comparison)
1. **Graph-only:** Topological shortest-path distance over unlinked dynamic knowledge graph ($s_g = 1 / (1 + d)$).
2. **GNN-only:** 2-layer Relational Graph Convolutional Network (R-GCN) structural scoring with no test-indicator supervision.
3. **Retrieval-only:** Dense semantic vector retrieval over historical training corpus chunks using frozen embeddings.
4. **Graph + RAG (No GNN):** Linear blend of graph topology and dense retrieval ($0.50 \cdot s_{\text{rag}} + 0.50 \cdot s_g$).
5. **Full Hybrid:** Unified NexusCTI engine fusing R-GCN structural confidence, topological graph proximity, dense text retrieval, and cross-validation gating.

### 4.2 Frozen Engine Parameters
- **R-GCN Hidden Dimension:** 64
- **Training Epochs:** 120 (Adam optimizer, lr = 0.01)
- **Random Seed:** PyTorch Seed = 42, Hashing = MD5 bucketed projection (8192 buckets)
- **Fusion Weights:**
  - Structural GNN Weight: $w_{\text{gnn}} = 0.45$
  - Topological Graph Weight: $w_{\text{topo}} = 0.55$
  - Cross-Validation Gate Multiplier: $\tau_{\text{cv}} = 0.20$
- **Decision Verdict Thresholds:**
  - `CONFIRMED`: Fused Confidence $\ge 0.85$ AND Hallucination Risk = `MINIMAL`
  - `PROBABLE`: Fused Confidence $\ge 0.50$ AND Hallucination Risk $\ne$ `CRITICAL`
  - `INCONCLUSIVE`: Fused Confidence $< 0.50$ OR Hallucination Risk = `CRITICAL`

---

## 5. Dataset Eligibility and Adjudication Criteria

### 5.1 Inclusion Criteria
1. Report originates from primary government intelligence or accredited cybersecurity threat intelligence research (CISA, FBI, NSA, Microsoft MSRC, Google Cloud/Mandiant, UK NCSC, CERT-EU, etc.).
2. Report documents an authentic, technically detailed intrusion campaign published between 2020 and 2025.
3. Report provides verifiable technical telemetry (CVEs, MITRE ATT&CK techniques, malware families, and network/host indicators).
4. Attribution is explicitly documented with traceable evidentiary excerpts in the report text.

### 5.2 Exclusion Criteria
1. Secondary aggregation blogs, syndicated news summaries, or repackaged duplicates of existing advisories.
2. Reports with conflicting, ambiguous, or disputed attribution (these are routed to Task B).
3. Any indicator or infrastructure that overlaps with the NexusCTI Phase 1–5 training corpus.

### 5.3 Task Partitioning
- **Task A (Known-Actor, Unseen-Campaign Closed Set):** Threat actor is one of the 6 supported training actors (`APT28`, `APT29`, `Sandworm`, `Lazarus`, `FIN7`, `Volt Typhoon`), but the campaign, indicators, and source report are completely held out.
- **Task B (Open-Set & Ambiguous Evaluation):** Attributed actor is outside the closed candidate set (`Kimsuky`, `LockBit`, `APT41`, `Charming Kitten`, `Gamaredon`, `BlackCat`, `Scattered Spider`, `DarkSide`) OR the incident involves commodity multi-actor CVE exploitation. Scored solely on proper rejection/abstention.
