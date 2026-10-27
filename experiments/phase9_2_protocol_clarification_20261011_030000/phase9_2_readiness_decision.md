# NexusCTI Phase 9.2 — Master Readiness Decision & Protocol Remediation Report

**Document Version:** 1.0 (Master Pre-Evaluation Decision)  
**Date:** 2026-10-11  
**Experiment Root:** `experiments/phase9_2_protocol_clarification_20261011_030000/`  
**Prior Audits Synthesized:**
- Phase 9 Protocol Freeze: `experiments/phase9_benchmark_preparation_20261011_020400/`
- Phase 9.1 Preflight Audit: `experiments/phase9_1_preflight_audit_20261011_023000/`
- Phase 9.2 Remediation: `experiments/phase9_2_protocol_clarification_20261011_030000/`

---

## Final Official Recommendation:
# **READY ONLY AFTER PROTOCOL AMENDMENT**

> [!IMPORTANT]
> **Administrative Constraint:**  
> A readiness recommendation is **not** permission to run the benchmark. In strict compliance with preregistration governance, **zero test cases were evaluated, zero test labels were unblinded, and zero model parameters were altered during Phase 9.2**.

---

## 1. Executive Synthesis of Phase 9.2 Remediations

Phase 9.2 resolved the three outstanding methodological and runtime concerns identified in Phase 9.1:

```
+---------------------------------------------------------------------------------------------------------------+
| PHASE 9.2 REMEDIATION AUDIT MATRIX & FINAL STATUS                                                             |
+--------------------------+-----------------------+------------------------------------------------------------+
| Remediation Concern      | Final Determination   | Verified Findings & Supporting Artifact Reference          |
+--------------------------+-----------------------+------------------------------------------------------------+
| Statistical Power Deficit| VERIFIED / REMEDIATED | - Phase 9.1 finding independently confirmed: Joint power   |
|                          |                       |   for dual rule is 53.911% at N=100 (never reaches 80%).   |
|                          |                       | - Prepared Alternative B proposal: Treats +15% as Minimal  |
|                          |                       |   Detectable Effect (MDE) with Agresti-Min 95% CI.         |
|                          |                       |   Restores inferential power to 83.674% at N=100.          |
|                          |                       |   Ref: phase9_2_protocol_amendment_proposal.md             |
|                          |                       |   Ref: joint_decision_rule_power_recheck.csv               |
+--------------------------+-----------------------+------------------------------------------------------------+
| Leakage Audit Script Bug | VERIFIED / REMEDIATED | - Traced schema mismatch: "nodes" vs "node_mappings" and   |
|                          |                       |   "content" vs "narrative".                                |
|                          |                       | - Implemented run_leakage_audit_v2.py with loud schema     |
|                          |                       |   validation and deterministic extraction.                 |
|                          |                       | - True count verified: 0 matching IOCs between 60 training |
|                          |                       |   indicators and 130 test observables (0.0% leakage).      |
|                          |                       |   Ref: leakage_audit_reproducibility_v2.md                 |
|                          |                       |   Ref: run_leakage_audit_v2.py                             |
+--------------------------+-----------------------+------------------------------------------------------------+
| ChromaDB Hash Mismatch   | VERIFIED / REMEDIATED | - Safe snapshot forensic inspection of SQLite page header. |
|                          |                       | - Proven: Mismatch caused solely by volatile bytes 24-27   |
|                          |                       |   (file change counter = 20) updating on active open.      |
|                          |                       | - Schema cookie (bytes 40-43) = 52 is invariant.           |
|                          |                       | - Deterministic content SHA-256 hash 9a88316a... verified  |
|                          |                       |   100% invariant across all 7 chunks and 49 metadata items.|
|                          |                       |   Ref: database_integrity_verification.md                 |
|                          |                       |   Ref: run_database_integrity_check.py                     |
+--------------------------+-----------------------+------------------------------------------------------------+
| Runtime Determinism      | VERIFIED              | - Active API strictly uses src/rag_engine.py (MiniLM-L6).  |
|                          |                       | - 10-iteration repeatability test achieved bit-identical   |
|                          |                       |   embeddings (max abs diff = 0.0000000000).                |
|                          |                       | - Pre/post database content hash 668d0776... unchanged.    |
|                          |                       | - Clarified PYTHONHASHSEED interpreter lifecycle mechanics.|
|                          |                       |   Ref: runtime_determinism_report.md                       |
|                          |                       |   Ref: run_runtime_determinism_check.py                    |
+--------------------------+-----------------------+------------------------------------------------------------+
```

---

## 2. Rationale for the Readiness Recommendation

Why **`READY ONLY AFTER PROTOCOL AMENDMENT`** instead of `READY FOR BLIND EVALUATION` or `NOT READY FOR EVALUATION`?

1. **Why NOT "READY FOR BLIND EVALUATION"?**
   - The prospective benchmark evaluation cannot be executed under the unmodified Phase 9 protocol because the unmodified decision rule requires observed $\hat{\Delta} \ge +0.150$.
   - As proven mathematically and numerically, that rule has only a **$53.91\%$ chance of succeeding** under the planning assumptions, even if Full Hybrid is genuinely $+15.0\%$ superior.
   - Proceeding to blind evaluation without formally enacting **Alternative B** would knowingly subject the study to an unacceptably high $46.1\%$ Type II error rate.
2. **Why NOT "NOT READY FOR EVALUATION"?**
   - The system, models, graph, vector retrieval corpus, candidate benchmark cases, and evaluation code are **technically healthy, leak-free, deterministic, and complete**.
   - No models need retraining; no weights need tuning; no benchmark cases were compromised or exposed.
   - The blocker is purely governance: formal adoption of the proposed protocol amendment.
3. **The Path Forward:**
   - Adopting **Alternative B** from [`phase9_2_protocol_amendment_proposal.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_2_protocol_clarification_20261011_030000/phase9_2_protocol_amendment_proposal.md) establishes a fully powered ($83.67\%$), confirmatory statistical evaluation with rigorous Agresti-Min 95% confidence interval reporting.

---

## 3. Preregistration Amendment Protocol Checklist

Before any test predictions are unblinded or scored, the following three administrative actions must be enacted:

- [ ] **Action 1 (Protocol Amendment Enactment):** Formally adopt Alternative B as Master Protocol Amendment 1.0, establishing primary statistical superiority as exact two-sided McNemar $p \le 0.05$ ($\hat{\Delta} > 0$), with $+15.0\%$ designated as the planning Minimal Detectable Effect (MDE) evaluated via the 95% Agresti-Min confidence interval.
- [ ] **Action 2 (Shell Hash-Seed Enforcement):** Configure evaluation runner launch scripts to set `$env:PYTHONHASHSEED = "0"` prior to interpreter execution.
- [ ] **Action 3 (Read-Only Database VFS):** Enforce URI read-only connection mode (`file:chroma.sqlite3?mode=ro`) during benchmark execution, with automated pre-run and post-run content hash verification (`9a88316a...`).

---

## 4. Final Determination & Sign-Off

The NexusCTI cyber-threat attribution engine, frozen knowledge graph, authentic retrieval corpus, and candidate campaign benchmark are **methodologically clarified, forensic integrity verified, and officially classified as**:

# **READY ONLY AFTER PROTOCOL AMENDMENT**
