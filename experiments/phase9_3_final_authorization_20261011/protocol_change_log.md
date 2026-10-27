# NexusCTI Protocol Change Log (Phases 9.0 to 9.3)

**Document Version:** 2.0 (Audit Trail & Version Control)  
**Date:** 2026-10-11  
**Project Root:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI`  
**Experiment Root:** `experiments/phase9_3_final_authorization_20261011/`

---

## 1. Protocol Version Summary

| Protocol Version | Date & Timestamp | Originating Phase | Status | Key Characteristics |
| :--- | :--- | :--- | :--- | :--- |
| **v1.0** | 2026-10-11T02:04:00+05:30 | Phase 9 | Superseded | Initial pre-registration protocol; dual rule ($p \le 0.05$ AND $\hat{\Delta} \ge +0.150$). |
| **v1.1 (Proposed)** | 2026-10-11T03:00:00+05:30 | Phase 9.2 | Adopted | Formulated Alternative B amendment decoupling planning MDE from sample point estimate. |
| **v2.0 (Locked)** | 2026-10-11T03:06:00+05:30 | Phase 9.3 | **ACTIVE / LOCKED** | Formally locks Alternative B, Agresti–Min CI formula, missing data policy, and read-only URI mode. |

---

## 2. Chronological Record of Amendments

### Amendment 1: Reformulation of Confirmatory Superiority Decision Rule
- **Amendment Identifier:** AMEND-20261011-01
- **Effective Version:** Version 2.0 (supersedes Version 1.0 Section 2.2)
- **Timestamp:** 2026-10-11T03:00:00+05:30
- **Changes Confirmatory Decision Rule?** **YES**
- **Original Text (v1.0):**
  > "A positive confirmatory conclusion requires BOTH of the following conditions:
  > 1. Exact two-sided McNemar test p-value $\le 0.05$.
  > 2. Observed sample paired risk difference $\hat{\Delta} \ge +0.150$ (+15.0 percentage points)."
- **Amended Text (v2.0):**
  > "A formal claim of confirmatory superiority requires satisfying BOTH:
  > 1. Exact two-sided McNemar test p-value $\le 0.05$.
  > 2. Observed paired risk difference $\hat{\Delta} > 0$ (directional condition, $b > c$).
  > The $+15.0$ percentage point target is explicitly designated as the planning Minimal Detectable Effect (MDE) used for sample size determination ($N=100$), rather than a hard observed sample point estimate gate. Practical effect magnitude is reported via the prespecified Agresti–Min 95% confidence interval."
- **Scientific & Statistical Rationale:**  
  Phase 9.1's independent preflight audit uncovered that enforcing a sample-level constraint $\hat{\Delta} \ge +0.150$ in addition to $p \le 0.05$ degraded the prospective statistical power from $83.67\%$ down to $53.91\%$. Under the central limit theorem, when the true population difference is $+0.150$, the sample estimator $\hat{\Delta}$ is symmetrically distributed around $+0.150$, meaning $P(\hat{\Delta} \ge +0.150) \approx 0.50$. Capping confirmatory power at $54\%$ created an unacceptable $46\%$ Type II error rate. Alternative B restores the statistical test to its intended operating characteristics ($83.67\%$ power) while reporting the magnitude of effect via confidence estimation.

---

### Amendment 2: Prespecification of Agresti–Min Confidence Interval Method
- **Amendment Identifier:** AMEND-20261011-02
- **Effective Version:** Version 2.0 (replaces informal dual interval references in v1.0 Section 3)
- **Timestamp:** 2026-10-11T03:00:00+05:30
- **Changes Confirmatory Decision Rule?** **NO** (Secondary estimation standard)
- **Original Text (v1.0):**
  > "Report 95% confidence intervals using Agresti–Min and continuity-corrected Wald methods."
- **Amended Text (v2.0):**
  > "The primary confidence interval for the paired risk difference is the Agresti–Min (2005) pseudo-observation interval, defined as:
  > $\tilde{b} = b + 1, \; \tilde{c} = c + 1, \; \tilde{N} = N + 2, \; \tilde{\Delta} = (b - c)/(N + 2)$,
  > with standard error $\text{SE}(\tilde{\Delta}) = \sqrt{\frac{\tilde{p}_{12} + \tilde{p}_{21} - \tilde{\Delta}^2}{N + 2}}$.
  > Methodological Reference: Agresti, A., & Min, Y. (2005). Statistics in Medicine, 24(5), 729–740."
- **Scientific & Statistical Rationale:**  
  In Phase 8.3, the uncorrected Newcombe score interval produced an interval $[+0.72\%, +38.31\%]$ that excluded zero despite an exact McNemar test $p$-value of $0.125$ (which failed to reject zero). To guarantee statistical consistency and conservative coverage without erratic zero-exclusion, the Agresti–Min pseudocount method was mathematically validated as the optimal estimator for matched-pair designs.

---

### Amendment 3: Explicit Missing Data and Failure Handling Policy
- **Amendment Identifier:** AMEND-20261011-03
- **Effective Version:** Version 2.0 (formally locks Section 5)
- **Timestamp:** 2026-10-11T03:06:00+05:30
- **Changes Confirmatory Decision Rule?** **NO** (Operational integrity constraint)
- **Original Text (v1.0):**
  > "Missing predictions are penalized."
- **Amended Text (v2.0):**
  > "In accordance with the intention-to-evaluate principle, any test case that produces an execution timeout, unhandled exception, corrupted JSON payload, or empty prediction is automatically assigned Rank = 99 (Incorrect). Failed cases are not excluded or re-sampled. Ties in fused confidence score are resolved deterministically by lexicographical order of canonical actor IDs."
- **Scientific & Statistical Rationale:**  
  Guarantees complete protection against post-hoc data filtering or selective attrition bias during benchmark unblinding.

---

### Amendment 4: Mandatory Epistemic Disclaimers on Generalization and Operational Utility
- **Amendment Identifier:** AMEND-20261011-04
- **Effective Version:** Version 2.0 (added to Section 4.1)
- **Timestamp:** 2026-10-11T03:06:00+05:30
- **Changes Confirmatory Decision Rule?** **NO** (Epistemic qualification)
- **Amended Text (v2.0):**
  > "The prospective evaluation report must explicitly declare that statistical significance on this benchmark does NOT establish operational SOC utility, causal attribution validity, or real-world generalization to novel evasive adversaries."
- **Scientific & Statistical Rationale:**  
  Precludes unwarranted academic or commercial claims regarding causal validity based solely on paired accuracy metrics on synthetic or curated benchmark suites.

---

### Amendment 5: Read-Only SQLite URI Connection Enforcement
- **Amendment Identifier:** AMEND-20261011-05
- **Effective Version:** Version 2.0 (infrastructure prerequisite)
- **Timestamp:** 2026-10-11T03:06:00+05:30
- **Changes Confirmatory Decision Rule?** **NO** (Cryptographic integrity enforcement)
- **Amended Text (v2.0):**
  > "All evaluation runs must connect to the ChromaDB database using the read-only URI mode: `file:chroma.sqlite3?mode=ro`. Opening the database in read-write mode causes SQLite header bytes 24–27 (file change counter) to mutate, causing raw binary SHA-256 hash checks to fail despite 100% content invariance."
- **Scientific & Statistical Rationale:**  
  Phase 9.2 demonstrated that using read-only URI mode achieves 0-byte header mutation, ensuring raw binary SHA-256 invariance throughout prospective inference.
