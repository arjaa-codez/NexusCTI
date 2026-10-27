# NexusCTI Phase 7 — Independent Scientific Audit of Phase 6

**Audit Date:** 2026-10-11  
**Audit Directory:** `experiments/phase7_independent_audit_20261011_011500/`  
**Audited Target:** `experiments/phase6_external_benchmark_20261010_231000/`  
**Python Environment:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\.venv\Scripts\python.exe`  
**Execution Command:** `& "c:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\.venv\Scripts\python.exe" -u "c:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\experiments\phase7_independent_audit_20261011_011500\run_phase7_audit.py"`  

---

## Concise Executive Verdict

### 1. Are the Phase 6 data and source claims verified?
**VERIFIED WITH ONE MINOR TEXTUAL CORRECTION.**
All 16 external technical reports and 16 distinct campaigns were independently validated against authentic, public CTI advisories (CISA, Microsoft MSRC, Mandiant, UK NCSC). Zero reports or indicators were fabricated. The exact string overlap between external benchmark IOCs and training infrastructure was independently confirmed to be **0.0% (0 out of 33 indicators)**. 

*Correction Noted:* In `phase6_report.md` Section 5 Question 1, the textual breakdown stated "CISA (8 advisories), Microsoft MSRC (4 advisories), Mandiant (1 advisory), UK NCSC (1 advisory)", which totals 14. In reality, the manifest and table contain 16 reports (10 CISA/FBI, 4 Microsoft MSRC, 1 Mandiant, 1 UK NCSC). The narrative omitted 2 co-authored CISA/FBI advisories.

### 2. Are the reported metrics independently reproducible?
**100% INDEPENDENTLY REPRODUCIBLE.**
Recalculation directly from `frozen_predictions.csv` reproduced all reported metrics with zero numerical discrepancies:
- **Task A Top-1 Accuracy:** Full Hybrid: **4/8 (50.0%)**, Retrieval-only: **4/8 (50.0%)**, Graph+RAG: **4/8 (50.0%)**, Graph-only: **1/8 (12.5%)**, GNN-only: **1/8 (12.5%)**.
- **Task A Top-3 Accuracy:** Full Hybrid: **7/8 (87.5%)**, Retrieval-only: **5/8 (62.5%)**, Graph-only: **3/8 (37.5%)**.
- **Task B Open-Set Proper Abstention Rate:** **4/4 (100.0%)**, False Attribution Rate: **0/4 (0.0%)**.
All source code SHA-256 hashes matched `reproducibility_manifest.json` exactly.

### 3. Is the claimed hybrid improvement supported?
**UNSUPPORTED STATISTICALLY AT N=8 (DIRECTIONALLY PROMISING ONLY).**
While Full Hybrid achieved 7/8 Top-3 accuracy compared to 5/8 for Retrieval-only, this numerical difference involves only 2 discordant pairs (`bench_ext_01`, `bench_ext_09`). A two-sided paired exact McNemar test yields $p = 0.5000 \gg 0.05$. Furthermore, on Top-1 accuracy, Full Hybrid and Retrieval-only are identical (4/8 vs 4/8). The claim of proven hybrid superiority over retrieval alone is **statistically unsupported** at current sample sizes.

### 4. Which conclusions are safe to report academically?
- **Safe to Report:**
  1. *Under campaign-disjoint conditions with novel indicators, purely topological Graph-only and GNN-only attribution degrades to near-chance levels (12.5% Top-1).*
  2. *Semantic behavioral retrieval provides the primary cross-campaign anchor, achieving 50.0% Top-1 accuracy.*
  3. *Uncertainty-calibrated hybrid fusion safely abstains on out-of-vocabulary threat actors and commodity vulnerabilities without forced false attribution (100% abstention on tested cases).*
  4. *The 100% accuracy reported in early phases was an artifact of indicator overlap and lexical leakage.*
- **Unsafe to Report:**
  1. *Do NOT claim Full Hybrid is statistically superior to Retrieval-only (McNemar $p = 0.50$).*
  2. *Do NOT claim confidence intervals span $\pm 15\%$ (Wilson score interval for $N=8, p=0.50$ is $[21.5\%, 78.5\%]$, which is $\pm 28.5\%$).*
  3. *Do NOT claim general open-set robustness based on $N=4$ test cases.*

### 5. What is the single highest-priority next experiment?
**Scale the campaign-disjoint external benchmark from $N=8$ to $N \ge 40$ independent paired campaign cases across at least 10 threat actors.** This is the minimal sample size required to power a paired statistical test ($\alpha = 0.05, \beta = 0.80$) capable of determining whether hybrid fusion genuinely outperforms dense retrieval under distribution shift.

---

## Audit A — Dataset Provenance and Counts

### Findings:
- Total unique reports in `external_report_manifest.csv`: **16**.
- Total unique campaigns: **16**.
- Total candidate indicators: **33**.
- Total scored cases: **16** (8 Task A Frozen Test, 4 Task A Validation, 4 Task B Frozen Test).
- All 16 URLs point to legitimate, active public disclosures from CISA, Microsoft MSRC, Mandiant, or UK NCSC.
- Verbatim excerpts in `external_report_manifest.csv` match source disclosures.
- Hashes recorded in the manifest match computed content digests.

### Reconciled Source Organization Count:
| Source Organization | Reports in Manifest | Stated in Phase 6 Text | Audit Finding |
|:---|:---:|:---:|:---|
| **CISA / FBI / NSA (US Gov)** | 10 | 8 | Discrepancy: Report omitted 2 joint CISA/FBI advisories in text summary |
| **Microsoft MSRC** | 4 | 4 | Verified match |
| **Mandiant / Google Cloud** | 1 | 1 | Verified match |
| **UK NCSC / CISA** | 1 | 1 | Verified match |
| **Total** | **16** | **14** (stated in text) | **Reconciled to 16 actual reports** |

*Artifact Generated:* [`source_provenance_audit.csv`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase7_independent_audit_20261011_011500/source_provenance_audit.csv)

---

## Audit B — Ground-Truth Validity

All 16 benchmark cases were audited for attribution defensibility:
- **Task A (Known Actors, Unseen Campaigns, 12 cases):**
  - All 12 cases have explicit, traceable government or tier-1 vendor attribution linking the campaign indicators to `actor_apt28`, `actor_apt29`, `actor_sandworm`, `actor_lazarus`, `actor_fin7`, or `actor_volt_typhoon`.
  - In all 12 cases, the specific campaign and indicators were completely unobserved during training.
  - 8 cases correctly designated as `FROZEN_TEST`; 4 cases correctly designated as `VALIDATION_SET`.
- **Task B (Open-Set & Ambiguous Campaigns, 4 cases):**
  - 3 cases (`bench_ext_13` Kimsuky, `bench_ext_14` LockBit, `bench_ext_15` APT41) represent authentic threat actors absent from the 6-actor closed candidate set. Ground-truth label `UNSEEN_ACTOR` is defensible.
  - 1 case (`bench_ext_16` ManageEngine CVE-2022-47966) represents commodity multi-actor exploitation where attribution to a single actor is formally disputed/unknown. Ground-truth label `AMBIGUOUS` is defensible.

*Artifact Generated:* [`ground_truth_validity_audit.csv`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase7_independent_audit_20261011_011500/ground_truth_validity_audit.csv)

---

## Audit C — Split Integrity and Leakage

### Independent Verification Results:
1. **Indicator Overlap:** Re-evaluating all 33 external indicators against the 23 baseline indicators yielded **0 exact matches (0.0% overlap)**.
2. **Graph Contamination:** The training graph contains 0 nodes or edges derived from external campaign reports.
   - *Audit check on prefix match:* In validation case `bench_ext_04`, indicator `185.141.63.120` matched training node `ioc_ip_185_141_63_12` due to prefix containment. Audit confirms this case was properly quarantined in `VALIDATION_SET` and excluded from test metrics.
3. **Retrieval Index Contamination:** Exactly 0 external reports were indexed in the training retrieval corpus.
4. **Semantic Feature Leakage Analysis:**
   - Test queries contain behavioral descriptions (e.g., Print Spooler LPE, WatchGuard ELF implant, SAML SSO exploitation).
   - The dense retriever matches these against historical profiles using general semantic embeddings.
   - This represents **legitimate cross-campaign behavioral similarity**, which is the explicit objective of cross-campaign attribution, rather than dataset contamination.

*Artifact Generated:* [`split_and_leakage_audit.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase7_independent_audit_20261011_011500/split_and_leakage_audit.json)

---

## Audit D — Independent Metric Recalculation

All metrics were recomputed from raw rows in `frozen_predictions.csv`:

```
+-------------------+--------------------+--------------------+--------+--------------------+
| Architecture      | Recalculated Top-1 | Recalculated Top-3 | Rec MRR| Discrepancy Status |
+-------------------+--------------------+--------------------+--------+--------------------+
| Graph-only        | 1 / 8 (12.5%)      | 3 / 8 (37.5%)      | 0.3583 | Zero Discrepancy   |
| GNN-only          | 1 / 8 (12.5%)      | 3 / 8 (37.5%)      | 0.3583 | Zero Discrepancy   |
| Retrieval-only    | 4 / 8 (50.0%)      | 5 / 8 (62.5%)      | 0.6333 | Zero Discrepancy   |
| Graph + RAG       | 4 / 8 (50.0%)      | 5 / 8 (62.5%)      | 0.6333 | Zero Discrepancy   |
| Full Hybrid       | 4 / 8 (50.0%)      | 7 / 8 (87.5%)      | 0.6708 | Zero Discrepancy   |
+-------------------+--------------------+--------------------+--------+--------------------+
```

- **Task B Proper Abstention:** 4 / 4 (100.0%) assigned `INCONCLUSIVE` (Verdicts: all `INCONCLUSIVE`, confidence 0.33–0.39 < 0.70 threshold).
- **Task B False Attribution:** 0 / 4 (0.0%). Zero false attributions to closed-set actors.

*Artifact Generated:* [`independent_metric_recalculation.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase7_independent_audit_20261011_011500/independent_metric_recalculation.json)

---

## Audit E — Statistical Validity and Confidence Intervals

### 1. Mathematical Correction of Confidence Interval Claims
Phase 6 stated that confidence intervals span "approximately $\pm 15\%$".
Using the **Wilson score interval** with 95% confidence ($\alpha = 0.05$):
- **Full Hybrid Top-1 Accuracy ($4/8 = 50.0\%$):** 
  - 95% CI: **$[21.52\%, 78.48\%]$**
  - True Error Margin: **$\pm 28.48\%$** (nearly double the claimed $\pm 15\%$).
- **Full Hybrid Top-3 Accuracy ($7/8 = 87.5\%$):** 
  - 95% CI: **$[52.91\%, 97.76\%]$**
- **Retrieval-only Top-3 Accuracy ($5/8 = 62.5\%$):** 
  - 95% CI: **$[30.57\%, 86.32\%]$**
- **Task B Abstention Rate ($4/4 = 100.0\%$):** 
  - 95% CI: **$[51.01\%, 100.00\%]$**

### 2. Paired Hypothesis Test: Full Hybrid vs. Retrieval-Only
- Successes in Top-3: Full Hybrid (7/8) vs. Retrieval-only (5/8).
- Discordant pairs: $b = 2$ (`bench_ext_01`, `bench_ext_09` where Hybrid succeeded and Retrieval missed), $c = 0$.
- Two-sided exact binomial test: $p = 2 \times (0.5)^2 = \mathbf{0.5000}$.
- **Conclusion:** $p = 0.50 \gg 0.05$. The observed difference is **NOT statistically significant**.

*Artifact Generated:* [`statistical_uncertainty_report.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase7_independent_audit_20261011_011500/statistical_uncertainty_report.md)

---

## Audit F — Reproducibility

### Code and Artifact Hash Verification
Recomputing SHA-256 digests across all repository code files confirmed **100% hash identity**:
- `nexuscti/service.py`: `f9fcf4b6...` (MATCH)
- `nexuscti/gnn/trainer.py`: `51fd0eed...` (MATCH)
- `nexuscti/gnn/graph_builder.py`: `6e53faee...` (MATCH)
- `nexuscti/rag/dense_retriever.py`: `87b23795...` (MATCH)
- `nexuscti/fusion/engine.py`: `ce3102da...` (MATCH)
- `experiments/phase6_external_benchmark_20261010_231000/run_phase6_benchmark.py`: `15b601ee...` (MATCH)

Deterministic MD5 hashing in `SemanticTextEncoder` and fixed PyTorch seed (`42`) ensure process-level repeatability.

*Artifacts Generated:* [`reproducibility_audit.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase7_independent_audit_20261011_011500/reproducibility_audit.json), [`phase7_hash_manifest.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase7_independent_audit_20261011_011500/phase7_hash_manifest.json)

---

## Audit G — Claim-by-Claim Verdict Register

Summary of formal audit verdicts across all major claims in Phase 6:

| Claim ID | Claim Statement | Phase 7 Verdict | Audit Rationale |
|:---|:---|:---:|:---|
| **CLM-P6-01** | 16 verified real-world CTI reports and campaigns collected without fabrication | **VERIFIED** | All 16 URLs, publishers, dates, and verbatim passages verified. |
| **CLM-P6-02** | Report publisher breakdown matches stated text (8 CISA, 4 Microsoft, 1 Mandiant, 1 NCSC) | **PARTIALLY VERIFIED** | Total rows = 16. Narrative omitted 2 joint CISA/FBI reports in text breakdown. |
| **CLM-P6-03** | Zero indicator overlap between external benchmark and training corpus (0.0%) | **VERIFIED** | String comparison across 33 IOCs confirmed 0 exact overlaps (0.0%). |
| **CLM-P6-04** | Zero contamination in training knowledge graph and retrieval corpus | **VERIFIED** | 0 external reports indexed. Prefix match quarantined to validation set. |
| **CLM-P6-05** | Full Hybrid achieves 50.0% Top-1 and 87.5% Top-3 on unseen campaigns | **VERIFIED** | Recalculated directly from predictions CSV (4/8 Top-1, 7/8 Top-3). |
| **CLM-P6-06** | Full Hybrid statistically outperforms Retrieval-only under campaign shift | **UNSUPPORTED** | Top-1 is identical (4/8 vs 4/8); Top-3 difference has McNemar $p = 0.50$. |
| **CLM-P6-07** | Confidence intervals at N=8 span approximately ±15% | **CONTRADICTED** | Wilson score interval is $[21.5\%, 78.5\%]$ ($\pm 28.5\%$, nearly double). |
| **CLM-P6-08** | Task B open-set robustness proven by 100% abstention on 4 cases | **PARTIALLY VERIFIED** | Empirically 4/4 abstained, but Wilson CI $[51.0\%, 100\%]$ is insufficient. |
| **CLM-P6-09** | Pure graph and GNN methods collapse to 12.5% Top-1 on novel unlinked IOCs | **VERIFIED** | Confirmed empirically across both Graph-only and GNN-only. |

*Artifact Generated:* [`claim_verdict_register.csv`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase7_independent_audit_20261011_011500/claim_verdict_register.csv)

---

## Summary of Audit Deliverables

All required Phase 7 deliverables have been created and preserved in `experiments/phase7_independent_audit_20261011_011500/`:

1. [`phase7_audit_report.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase7_independent_audit_20261011_011500/phase7_audit_report.md) — This master independent audit report.
2. [`source_provenance_audit.csv`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase7_independent_audit_20261011_011500/source_provenance_audit.csv) — 16-row report provenance and URL validation audit.
3. [`ground_truth_validity_audit.csv`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase7_independent_audit_20261011_011500/ground_truth_validity_audit.csv) — 16-row case defensibility and split assignment audit.
4. [`independent_metric_recalculation.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase7_independent_audit_20261011_011500/independent_metric_recalculation.json) — Independent recomputation of all multi-architecture metrics.
5. [`split_and_leakage_audit.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase7_independent_audit_20261011_011500/split_and_leakage_audit.json) — Audit of graph, index, and semantic feature leakage.
6. [`statistical_uncertainty_report.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase7_independent_audit_20261011_011500/statistical_uncertainty_report.md) — Wilson score intervals, hypothesis test, and error margin corrections.
7. [`claim_verdict_register.csv`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase7_independent_audit_20261011_011500/claim_verdict_register.csv) — Claim-by-claim audit register with formal verdicts.
8. [`reproducibility_audit.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase7_independent_audit_20261011_011500/reproducibility_audit.json) — Code hash verification and deterministic reproduction analysis.
9. [`phase7_hash_manifest.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase7_independent_audit_20261011_011500/phase7_hash_manifest.json) — Pre-audit SHA-256 digests preserving Phase 6 artifacts.
10. [`run_phase7_audit.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase7_independent_audit_20261011_011500/run_phase7_audit.py) — Standalone reproduction script for all Phase 7 computations.
