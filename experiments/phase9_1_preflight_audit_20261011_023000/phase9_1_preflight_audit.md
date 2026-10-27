# NexusCTI Phase 9.1 — Independent Preflight Audit Master Report

**Document Version:** 1.0 (Independent Scientific Audit)  
**Date:** 2026-10-11  
**Experiment Root:** `experiments/phase9_1_preflight_audit_20261011_023000/`  
**Prior Baselines Audited (Read-Only):**
- Phase 8: `experiments/phase8_expanded_evaluation_20261011_012000/`
- Phase 8.1: `experiments/phase8_1_independent_audit_20261011_013000/`
- Phase 8.2: `experiments/phase8_2_power_and_verification_20261011_014200/`
- Phase 8.3: `experiments/phase8_3_statistical_consistency_20261011_015200/`
- Phase 9: `experiments/phase9_benchmark_preparation_20261011_020400/`

---

## Executive Summary & Final Determination

Phase 9.1 executes a strict, independent preflight audit of the prospective benchmark preparation, system freeze, leakage quarantine, and pre-registered protocol established in Phase 9.

### Master Audit Verdict:
# **READY ONLY AFTER PROTOCOL CLARIFICATION**

### Core Findings Summary:
1. **Audit A (Decision-Rule Power):** The pre-registered decision rule requires BOTH: (1) exact two-sided McNemar $p \le 0.05$ AND (2) observed risk difference $\hat{\Delta} \ge +0.15$. The reported power figure of $83.67\%$ applies **only** to the McNemar test alone. Because the sample estimator $\hat{\Delta}$ is centered at $+0.15$ under the planning model, $P(\hat{\Delta} \ge 0.15) \to 50\%$ by the Central Limit Theorem. Consequently, the actual probability of satisfying BOTH pre-registered success criteria is only **$53.91\%$** at $N=100$. Under the planning parameters ($q=0.25, \theta=0.80$), joint power **never reaches $80\%$ at any sample size**. Reaching $\ge 80\%$ joint power requires either a larger true effect ($\theta \ge 0.87, \Delta \ge +18.5\%$) or clarifying whether $+15.0\%$ is an MDE planning target rather than an empirical sample hurdle.
2. **Audit B (Confidence Interval Specification):** The pre-registered "Agresti-Min Paired Pseudocount Interval" is verified as a published technique (**Agresti & Min 2005, *Stat Med***). In 25,000-iteration Monte Carlo simulations across 5 regimes, it demonstrates nominal $\approx 95\%$ coverage ($95.16\%$ at $N=100$, $94.20\%$ at $N=24$), avoiding the severe undercoverage of uncorrected Wald ($90.08\%$). It is an adjusted Wald interval, not an exact test inversion, meaning marginal interval inclusion of zero can differ slightly from the exact conditional odds-ratio interval at the critical boundary.
3. **Audit C (Leakage-Audit Reproducibility):** The reported metric of "0 / 1,428 unique IOCs" was an unverified asserted literal in Phase 9 documentation caused by a script bug that queried non-existent keys (`"nodes"` and `"content"`). Correcting the parser reveals the true training evidence comprises **53 canonical graph nodes** and **61 technical indicator tokens**. Matching these against the 130 eligible candidate benchmark campaigns confirmed **0 matching indicators (0.0% contamination)**. "Full DB Quarantine" was clarified to mean test reports are excluded from ChromaDB (which holds solely the 7 baseline training chunks).
4. **Audit D (Freeze & Runtime Provenance):** 15 of 16 frozen files match their SHA-256 digests perfectly. The sole mismatch was `chroma.sqlite3`, caused by SQLite's internal page change counter updating upon database connection. The active engine in `cyber_attribution_engine/src/api.py` loads `rag_engine.py` (which successfully uses `sentence-transformers/all-MiniLM-L6-v2`), while the legacy `SemanticTextEncoder` in `nexuscti/rag/dense_retriever.py` is confirmed dead code.

---

## Audit A — Decision-Rule Power

### A.1 Mathematical Problem Formulation
The Phase 9 protocol declares that Full Hybrid will be declared superior to Retrieval-only **if and only if BOTH conditions are met**:
$$\text{Condition 1: } p_{\text{McNemar}} \le 0.05 \quad (\text{two-sided exact binomial test on discordant pairs } n_d)$$
$$\text{Condition 2: } \hat{\Delta} = \frac{b - c}{N} \ge +0.15 \quad (\text{observed sample risk difference hurdle})$$

Under the planning assumption:
- Discordance rate: $q = P(Y_H \ne Y_R) = 0.25$
- Conditional win rate: $\theta = P(Y_H = 1 \mid Y_H \ne Y_R) = 0.80$
- Implied true population risk difference: $\Delta = q(2\theta - 1) = 0.25(2(0.80) - 1) = +0.150$

### A.2 Independent Power Calculations
Both analytical integration across all $(n_d, b)$ pairs and Monte Carlo simulation ($M = 100,000$ draws) were independently computed:

```
+---------------------------------------------------------------------------------------------------------------+
| AUDIT A: INDEPENDENT DECISION-RULE POWER VERIFICATION (N = 100, q = 0.25, θ = 0.80, Δ = +15.0%)               |
+---------------------------------------+-------------------+---------------------------+-----------------------+
| Decision Criterion                   | Analytical Value  | Monte Carlo (M = 100,000) | Audit Determination   |
+---------------------------------------+-------------------+---------------------------+-----------------------+
| Condition 1 Alone (McNemar p <= 0.05) | 83.674%           | 83.797% +/- 0.117%        | VERIFIED (Matches P9) |
| Condition 2 Alone (Δ_hat >= +0.15)    | 53.911%           | 54.141% +/- 0.158%        | VERIFIED (Discovered) |
| JOINT DECISION RULE (Condition 1 & 2) | 53.911%           | 54.141% +/- 0.158%        | FAILED (P9 Overclaim) |
+---------------------------------------+-------------------+---------------------------+-----------------------+
```

### A.3 The Asymptotic Power Ceiling Discovery
Why does joint power collapse from $83.67\%$ to $53.91\%$?
- In any finite sample, $\hat{\Delta} = \frac{b - c}{N}$ is an empirical estimator with standard error $SE = \frac{1}{N}\sqrt{n_d - \frac{(b-c)^2}{N}} \approx 0.047$.
- When the true mean is exactly $\Delta = 0.15$, the distribution of $\hat{\Delta}$ is centered at $0.15$.
- By the Central Limit Theorem, $P(\hat{\Delta} \ge 0.15) \to 0.50$ (50%) as $N \to \infty$.
- **Critical Finding:** Under $q=0.25, \theta=0.80$, **no sample size $N$ can ever achieve 80% joint power**. Even at $N = 300$, McNemar power is $99.97\%$, but joint power is only **$52.26\%$**!

### A.4 Sensitivity Grid & Sample Size Requirements
From the 280-cell sensitivity grid exported to [`joint_decision_rule_power.csv`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_1_preflight_audit_20261011_023000/joint_decision_rule_power.csv):

```
+---------------------------------------------------------------------------------------------------------------+
| SENSITIVITY OF JOINT DECISION-RULE POWER ACROSS PLAUSIBLE POPULATION REGIMES                                 |
+-------+------+-------+-----------+---------------+--------------------+-------------+-------------------------+
| N     | q    | θ     | True Δ    | McNemar Power | Δ_hat >= 0.15 Hurdle| Joint Power | Meets 80% Joint Standard|
+-------+------+-------+-----------+---------------+--------------------+-------------+-------------------------+
| 100   | 0.25 | 0.80  | +15.0%    | 83.67%        | 53.91%             | 53.91%      | NO (Severe Deficit)     |
| 100   | 0.25 | 0.85  | +17.5%    | 94.75%        | 73.78%             | 73.78%      | NO (Sub-80% Floor)      |
| 100   | 0.25 | 0.87  | +18.5%    | 96.94%        | 80.52%             | 80.52%      | YES (80% Power Target)  |
| 100   | 0.25 | 0.90  | +20.0%    | 99.08%        | 88.65%             | 88.65%      | YES (Robust Target)     |
| 60    | 0.25 | 0.90  | +20.0%    | 89.02%        | 83.86%             | 83.66%      | YES (Achieved at N=60)  |
| 100   | 0.20 | 0.80  | +12.0%    | 71.69%        | 32.14%             | 32.14%      | NO                      |
| 100   | 0.30 | 0.80  | +18.0%    | 91.14%        | 71.05%             | 71.05%      | NO                      |
+-------+------+-------+-----------+---------------+--------------------+-------------+-------------------------+
```

### A.5 Audit A Determination:
- Exact McNemar Power Calculation ($83.67\%$): **VERIFIED**.
- Phase 9 Claim that $N=100$ Provides $83.67\%$ Power for the Dual Decision Rule: **FAILED**.
- Recommendation: Before unblinding test data, the protocol must clarify whether $+15.0\%$ is a Minimal Detectable Effect (planning target) or an empirical sample gate, or adjust the true effect planning baseline to $\theta \ge 0.87$.

---

## Audit B — Confidence Interval Specification

Detailed in [`confidence_interval_validation.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_1_preflight_audit_20261011_023000/confidence_interval_validation.md) and [`confidence_interval_simulation_results.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_1_preflight_audit_20261011_023000/confidence_interval_simulation_results.json):

### B.1 Theoretical Specification
- **Adjusted Counts:** $a^* = a+0.5, b^* = b+0.5, c^* = c+0.5, d^* = d+0.5$ ($N^* = N+2$).
- **Estimator:** $\hat{\Delta}^* = \frac{b - c}{N + 2}$.
- **Variance:** $\widehat{\text{Var}}(\hat{\Delta}^*) = \frac{(b+c+1) - (b-c)^2/(N+2)}{(N+2)^2}$.
- **Literature Recognition:** Published named technique: **Agresti-Min (2005, *Stat Med*)** adjusted-Wald interval.

### B.2 Empirical Coverage
- In 25,000 Monte Carlo draws under the primary planning distribution ($N=100, q=0.25, \theta=0.80$), Agresti-Min achieved **$95.16\%$ coverage** (near-nominal), with mean interval width $0.1859$.
- Under sparse discordance ($q=0.05$), where uncorrected Wald failed with **$90.08\%$ coverage**, Agresti-Min maintained **$96.08\%$ coverage**.
- Under small-sample baseline ($N=24$), Agresti-Min achieved **$94.20\%$ coverage** vs $92.55\%$ for Wald and $90.15\%$ for CC-Wald.

### B.3 Relationship to McNemar & Odds Ratio
- Unlike the exact Clopper-Pearson odds ratio interval (which is strictly conditional on $b+c$), Agresti-Min divides by $N+2$. It is an adjusted Wald interval for the marginal risk difference, not an exact inversion.
- Boundary agreement with McNemar is very high, but minor discordance at $p \approx 0.05$ is mathematically possible.

### B.4 Audit B Determination:
- Method Provenance & Formulation: **VERIFIED**.
- Empirical Coverage Properties: **VERIFIED**.
- Status: **Approved as primary risk-difference interval, with exact odds-ratio interval co-primary for hypothesis coherence.**

---

## Audit C — Leakage-Audit Reproducibility

Detailed in [`leakage_audit_reproducibility.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_1_preflight_audit_20261011_023000/leakage_audit_reproducibility.md):

### C.1 The 0 / 1,428 Metric Trace
- The Phase 9 prep script (`run_phase9_prep.py`) contained two dictionary key errors:
  1. `g_meta.get("nodes", [])` returned an empty list because the key in `graph_metadata.json` is `"node_mappings"`.
  2. `c.get("content", "")` returned empty strings because the key in raw reports is `"narrative"`.
- Consequently, the script extracted 0 indicators, and the figure "1,428 unique IOCs" was asserted manually in markdown.
- **Audit Determination:** **NOT VERIFIED (Script Extraction Logic Discrepancy).**

### C.2 True Physical Leakage Verification
When corrected to parse the genuine schema:
- Training evidence contains **53 graph nodes** and **61 technical indicators** across 6 training advisories.
- Candidate test set contains 100 Task A and 30 Task B campaigns with 130 extracted technical observables.
- Matching training indicators against test observables: **0 matches found (0.0% overlap)**.
- Substring matching against 7 ChromaDB text chunks: **0 matches found (Max 3-gram Jaccard = 0.042)**.
- Graph node encoding: **0 test campaign IDs or test observables pre-encoded in `hetero_graph.pt`**.
- Inference queries: **Stripped of threat actor names, aliases, and vendor labels**.

### C.3 "Full DB Quarantine" Clarification
- ChromaDB is **not** empty; it contains exactly 7 chunks from the 6 training reports.
- "Full DB Quarantine" strictly means the 130 test campaigns were **completely quarantined from ingestion**.

### C.4 Audit C Determination:
- 0 / 1,428 Specific Script Output: **NOT VERIFIED**.
- Physical Data, Graph, and Semantic Isolation: **VERIFIED (Zero Contamination Confirmed)**.

---

## Audit D — Freeze and Runtime Provenance

Detailed in [`runtime_freeze_verification.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_1_preflight_audit_20261011_023000/runtime_freeze_verification.json) and [`artifact_hash_manifest.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_1_preflight_audit_20261011_023000/artifact_hash_manifest.json):

### D.1 Cryptographic Hash Verification
- 15 out of 16 system artifacts in `frozen_system_manifest.json` match their SHA-256 digests perfectly.
- **The Mutable Artifact Discovery:** `cyber_attribution_engine/data/chroma_db/chroma.sqlite3` exhibited a hash mismatch (`f1619bf...` vs `1ddc579...`).
  * Investigation confirmed that ChromaDB's PersistentClient touches SQLite's internal header change counter (bytes 24-27) upon read connection.
  * The actual table rows (`embeddings` count: 7, `embedding_metadata` count: 49) are completely identical.
  * Hashing mutable SQLite binary files directly is fragile; read-only mode (`?mode=ro`) or table content hashing must be utilized.

### D.2 Encoder Architecture & Dependency Audit
- Active Runtime: `cyber_attribution_engine/src/api.py` imports `cyber_attribution_engine/src/rag_engine.py`.
- Sentence Transformers: Verified installed (`sentence-transformers 6.1.0`), loads `all-MiniLM-L6-v2`, and generates shape `(1, 384)` embeddings.
- Offline Fallback Nuance: `MiniLMEmbeddingFunction` contains an offline fallback using `hash(w) % 384`. Because Python's built-in `hash()` randomizes its SipHash seed across processes, offline execution without `PYTHONHASHSEED=0` is non-deterministic.
- Legacy `SemanticTextEncoder`: Present in `nexuscti/rag/dense_retriever.py`, but verified **not imported by any active engine file** (**VERIFIED DEAD CODE**).

### D.3 Audit D Determination:
- Static System Files & Model Weights: **VERIFIED**.
- Chroma SQLite Binary Hash: **UNRESOLVED / MUTABLE RUNTIME ARTIFACT**.
- Sentence Transformers Runtime: **VERIFIED**.
- Legacy Encoder Dead Code: **VERIFIED**.

---

## Final Epistemological Separation & Audit Matrix

```
+---------------------------------------------------------------------------------------------------------------+
| PHASE 9.1 MASTER AUDIT MATRIX & EPISTEMOLOGICAL DETERMINATIONS                                                |
+--------------------------+-----------------------+------------------------------------------------------------+
| Item Description         | Determination         | Supporting Evidence & Analysis                             |
+--------------------------+-----------------------+------------------------------------------------------------+
| Exact McNemar Power      | VERIFIED              | Analytical: 83.674%, Monte Carlo: 83.797% +/- 0.117%       |
| Dual Decision-Rule Power | FAILED                | Joint Power: 53.911% (Bounded by 50% CLT on sample mean)   |
| Agresti-Min Interval     | VERIFIED              | Published named method (Agresti & Min 2005); 95.16% coverage|
| Zero Indicator Leakage   | VERIFIED              | 0 matches between 61 training IOCs and 130 test observables|
| 0 / 1,428 Script Trace   | NOT VERIFIED          | Buggy script parsed wrong keys; 1,428 was asserted literal |
| System Weight Freeze     | VERIFIED              | RGCN weights and hetero_graph match SHA-256 exactly        |
| Chroma DB File Hash      | UNRESOLVED            | SQLite header change counter mutated on active connection  |
| Sentence Transformers    | VERIFIED              | Functional; all-MiniLM-L6-v2 verified in PyTorch           |
| Legacy Dense Retriever   | VERIFIED DEAD CODE    | Unused legacy module; not imported by active API           |
+--------------------------+-----------------------+------------------------------------------------------------+
```

---

## Pre-Evaluation Recommendations

To transition from **`READY ONLY AFTER PROTOCOL CLARIFICATION`** to **`READY FOR BLIND EVALUATION`**, the protocol must formally register the following three clarifications before observing any test outcomes:

1. **Protocol Decision Rule Clarification (Mandatory):**
   - The protocol must explicitly resolve the joint power deficit:
     * *Option A (Recommended):* Clarify that $+15.0\%$ is the **Minimal Detectable Effect (MDE)** that guided planning, and that the confirmatory superiority hurdle requires **exact two-sided McNemar $p \le 0.05$ with $\hat{\Delta} > 0$**, while reporting $\hat{\Delta}$ and its Agresti-Min 95% CI.
     * *Option B:* If $\hat{\Delta} \ge +0.150$ is retained as an absolute empirical sample gate, the protocol must acknowledge that the study has only **$53.9\%$ power** under true $\Delta = +15.0\%$, and that $\ge 80\%$ joint power requires the true advantage to be $\Delta \ge +18.5\%$ ($\theta \ge 0.87$).
2. **Deterministic Runtime Enforcement (Mandatory):**
   - Mandate that the evaluation run with verified online HuggingFace model cache or set the environment variable `PYTHONHASHSEED=0` to guarantee determinism in the event of embedding fallback.
   - Access `chroma.sqlite3` in read-only mode to prevent header mutation.
3. **Correct Leakage Parser Registration:**
   - Replace the flawed Phase 9 extraction script with the verified Phase 9.1 parser using genuine `node_mappings` and `narrative` keys.
