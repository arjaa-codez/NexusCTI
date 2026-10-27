# NexusCTI Phase 8.2 — Reproduction Instructions

**Execution Command:**
```powershell
& "C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\.venv\Scripts\python.exe" -u "C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\experiments\phase8_2_power_and_verification_20261011_014200\run_phase8_2_audit.py"
```

**Requirements:**
- Python 3.13.5 (AMD64)
- NumPy 2.4.3
- SciPy 1.17.1

**Inputs:**
- `experiments/phase8_expanded_evaluation_20261011_012000/frozen_predictions.csv`
- `experiments/phase8_1_independent_audit_20261011_013000/paired_endpoint_recalculation.json`

**Output Artifacts Generated:**
- `artifact_hash_manifest.json` — Cryptographic SHA-256 hashes of all Phase 8 and Phase 8.1 artifacts.
- `mcnemar_verification.json` — Exact paired contingency table, marginal rates, and exact McNemar test.
- `exact_interval_recalculation.json` — Clopper-Pearson intervals, exact odds ratio, and 4 paired risk-difference intervals.
- `prospective_power_analysis.csv` — Power grid across 140 parameter combinations (exact integration + Monte Carlo).
- `power_analysis_assumptions.md` — Formal documentation of scenarios, equations, and simulation outcomes.
- `sample_size_recommendation.md` — Target sample size recommendations and 10 benchmark design rules.
- `phase8_2_statistical_audit_report.md` — Master audit report resolving all statistical nuances.
