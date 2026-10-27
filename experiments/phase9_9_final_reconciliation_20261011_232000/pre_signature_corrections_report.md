# NexusCTI — Final Pre-Signature Corrections Report
## Technical Audit & Protocol Clarification Prior to Human Ratification

**Document Status:** Final Audit Complete — Awaiting Human Governance Review  
**Date:** 2026-10-12  
**Project Root:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\cyber_attribution_engine`  
**Reference Directory:** [`experiments/phase9_9_final_reconciliation_20261011_232000/`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_9_final_reconciliation_20261011_232000/)  
**Original Artifact Preserved:** [`final_human_approval_record.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_9_final_reconciliation_20261011_232000/final_human_approval_record.md)  
**Corrected Versioned Artifact:** [`final_human_approval_record_v2.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_9_final_reconciliation_20261011_232000/final_human_approval_record_v2.md)  

---

> [!IMPORTANT]
> **GOVERNANCE STATUS: PHASE 10 BLIND EVALUATION REMAINS STRICTLY UNAUTHORIZED**  
> This document executes technical corrections and verifies analytical claims prior to formal human governance sign-off.  
> It does **not** authorize Phase 10 execution, access prospective test labels, or sign on behalf of the Principal Investigator.

---

## 1. Statistical Power Correction & Exact Reproduction

### 1.1 Inconsistency Identified
In the Phase 9.9 [`final_human_approval_record.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_9_final_reconciliation_20261011_232000/final_human_approval_record.md) (Section 4, Item 6, line 98), the power planning statement read:
> *"Evaluated at $N = 100$, discordant pair proportion $q = 0.25$, odds ratio $\theta = 4.0$, achieving $83.674\%$ statistical power."*

This notation was inconsistent: in standard paired binomial and McNemar power modeling (Connor 1987; Agresti 2002), $\theta$ denotes the **conditional binomial probability** that a discordant pair favors the novel model ($b$ vs. $c$), where $\theta \in [0, 1]$. An odds ratio is denoted by $\psi \in [0, \infty)$, defined as $\psi = \frac{\theta}{1 - \theta}$. Stating $\theta = 4.0$ conflated the probability parameter with the odds ratio.

### 1.2 Source Code Location & Mathematical Formulation
The authoritative power-analysis implementation was located in:
[`experiments/phase9_3_final_authorization_20261011/run_power_audit.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_3_final_authorization_20261011/run_power_audit.py) (lines 14–115).

In this script, the statistical model is defined as:
1. Total sample size: $N = 100$.
2. Total number of discordant pairs: $n_d = b + c \sim \text{Binomial}(N, q)$, where $q = P(\text{discordant pair}) = 0.25$.
3. Favorable discordant pairs: $b \mid n_d \sim \text{Binomial}(n_d, \theta)$, where $\theta = P(\text{Hybrid correct, Retrieval incorrect} \mid \text{discordant pair}) = \mathbf{0.80}$.
4. Discordant odds ratio: $\psi = \frac{p_{10}}{p_{01}} = \frac{\theta}{1 - \theta} = \frac{0.80}{0.20} = \mathbf{4.0}$.
5. Implied population risk difference: $\Delta = q(2\theta - 1) = 0.25(2 \times 0.80 - 1) = +0.150$ (+15.0 percentage points).
6. Decision rule: Two-sided exact McNemar test $p \le 0.05$ AND directional condition $b > c$:
   $$p_{\text{McNemar}} = \begin{cases} 1.0 & \text{if } n_d = 0 \\ \min\left(1.0, \, 2 \sum_{k = \min(b, n_d - b)}^{n_d} \binom{n_d}{k} 0.5^{n_d}\right) & \text{if } n_d > 0 \end{cases}$$

### 1.3 Exact Power Computation & Verification
The joint probability mass function across all possible $(n_d, b)$ realizations is:
$$P(n_d, b) = \binom{N}{n_d} q^{n_d} (1 - q)^{N - n_d} \times \binom{n_d}{b} \theta^b (1 - \theta)^{n_d - b}$$

The exact prospective power is the sum of $P(n_d, b)$ over all pairs $(n_d, b)$ where $p_{\text{McNemar}}(b, n_d) \le 0.05$ and $b > n_d - b$:
$$\text{Power} = \sum_{n_d = 1}^{N} \sum_{b = \lfloor n_d/2 \rfloor + 1}^{n_d} P(n_d, b) \cdot \mathbb{I}\left(p_{\text{McNemar}}(b, n_d) \le 0.05\right)$$

Execution of the reproduction script:
- **Executable Script:** [`experiments/phase9_9_final_reconciliation_20261011_232000/verify_corrections.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_9_final_reconciliation_20261011_232000/verify_corrections.py)
- **Command:** `python verify_corrections.py`
- **Computed Output:**
  ```text
  Computed Power (N=100, q=0.25, theta=0.8): 83.67351%
  Power exactly matches 83.674%!
  ```

### 1.4 Verification Conclusion & Corrected Notation
The parameter $\theta = 0.80$ was unambiguously intended and reproduces **$83.674\%$** statistical power to the fifth decimal place ($83.67351\%$).
The corrected notation is:
$$\text{Discordant proportion } q = 0.25, \quad \text{conditional probability } \theta = 0.80, \quad \text{discordant odds ratio } \psi = \frac{\theta}{1 - \theta} = 4.0$$
This correction is incorporated into [`final_human_approval_record_v2.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_9_final_reconciliation_20261011_232000/final_human_approval_record_v2.md) while the original `final_human_approval_record.md` remains unaltered.

---

## 2. Open-Set Protocol Completeness (Task B, $N=30$)

A comprehensive audit of the preregistration protocol and historical amendments was conducted:
- Phase 8 Preregistration: [`experiments/phase8_expanded_evaluation_20261011_012000/preregistered_evaluation_protocol.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase8_expanded_evaluation_20261011_012000/preregistered_evaluation_protocol.md)
- Phase 9 Protocol Freeze: [`experiments/phase9_benchmark_preparation_20261011_020400/phase9_protocol_freeze.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_benchmark_preparation_20261011_020400/phase9_protocol_freeze.md)
- Phase 9.3 Final Protocol: [`experiments/phase9_3_final_authorization_20261011/phase9_3_final_protocol.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_3_final_authorization_20261011/phase9_3_final_protocol.md)
- Production Configuration: [`nexuscti/config.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/nexuscti/config.py)
- Attribution Engine Logic: [`nexuscti/fusion/engine.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/nexuscti/fusion/engine.py)

To ensure zero ambiguity during Phase 10 execution, all five required specifications for Task B are codified below:

### 2.1 Abstention Threshold & Selection Methodology
1. **Operating Rule:**
   A case receives the abstention verdict `INCONCLUSIVE` if and only if:
   - The top candidate's fused confidence score $S_{\text{fused}} < 0.50$, OR
   - The top candidate's cross-validation hallucination risk is `CRITICAL`, OR
   - The top-1 anomaly margin is $< 0.15$ (i.e., top candidate score does not clear the runner-up by at least $0.15$).
2. **Prespecified Origin:**
   This threshold is derived directly from frozen system constants in `nexuscti/config.py` (`ATTRIBUTION_THRESHOLD_MEDIUM = 0.50`), `nexuscti/fusion/engine.py` (lines 118–124), and `phase9_protocol_freeze.md` (line 59).
3. **Absence of Post-Hoc Tuning:**
   The threshold $\tau = 0.50$ was selected on operational grounds prior to assembling the benchmark test suite. It has **not** been tuned, adjusted, or calibrated against the prospective test set.

### 2.2 Definition and Denominator of False Attribution
1. **Definition:**
   A **False Attribution** occurs when an open-set campaign in Task B (which represents an unrepresented novel actor or an ambiguous multi-actor commodity intrusion) is assigned a confident non-abstaining attribution (`HIGH_CONFIDENCE`, `CONFIRMED`, or `PROBABLE`) to any candidate closed-set actor.
2. **Denominator:**
   The denominator is strictly the total number of eligible Task B campaigns: **$N = 30$**.
3. **Formula:**
   $$\text{False Attribution Rate (FAR)} = \frac{\sum_{i=1}^{30} \mathbb{I}(\text{verdict}_i \in \{\text{HIGH\_CONFIDENCE}, \text{CONFIRMED}, \text{PROBABLE}\})}{30}$$

### 2.3 Abstention-Rate Calculation & Uncertainty Reporting
1. **Formula:**
   $$\text{Proper Abstention Rate (PAR)} = \frac{\sum_{i=1}^{30} \mathbb{I}(\text{verdict}_i == \text{"INCONCLUSIVE"} \land \text{execution\_status} == \text{"SUCCESS"})}{30}$$
2. **Confidence Interval Method:**
   In accordance with Section 3.3 of the Phase 8 preregistration protocol, uncertainty for single proportions on Task B must be reported using the **95% Wilson Score Interval** without continuity correction:
   $$\text{CI}_{95\%} = \frac{\hat{p} + \frac{z^2}{2N} \pm z \sqrt{\frac{\hat{p}(1 - \hat{p})}{N} + \frac{z^2}{4N^2}}}{1 + \frac{z^2}{N}}$$
   where $N = 30$ and $z = 1.95996$.

### 2.4 Handling of Errors, Missing Outputs, and Unrecognized Actors
1. **Intention-to-Evaluate (ITE):**
   In accordance with Section 5 of the Phase 9.3 protocol, all 30 Task B cases must be submitted to evaluation and fully accounted for. No cases may be discarded post hoc.
2. **Operational Failures:**
   If the attribution engine encounters a runtime crash, unhandled exception, out-of-memory condition, timeout, parse failure, or empty output, the case must be assigned:
   $$\text{execution\_status} = \text{"FAILED\_EXCEPTION"}$$
3. **Strict Prohibition on Crediting Failures as Abstentions:**
   An engine failure, crash, or missing output **MUST NOT** be credited as a calibrated abstention (`INCONCLUSIVE`). Crediting system crashes as valid open-set abstentions would introduce severe survivorship bias. An execution failure is scored as an unhandled error ($0$ proper abstention credit).
4. **Unrecognized Actor Outputs:**
   If an engine outputs an actor ID outside the closed-set candidate registry without marking the verdict `INCONCLUSIVE`, it is scored as an invalid prediction and assigned `FAILED_EXCEPTION`.

### 2.5 Reporting & Decision Rules for all 30 Cases
1. **Secondary Characterization Role:**
   Task B is prespecified as a secondary characterization endpoint to assess novelty rejection and overconfidence risks. It is exploratory and does not alter the primary confirmatory hypothesis test (paired McNemar on Task A, $N=100$).
2. **Case-by-Case Transparency:**
   The Phase 10 evaluation report must publish a complete, unblinded 30-case table detailing:
   - Case ID & Canonical Campaign Name
   - Ground-Truth Category (Novel Actor vs. Ambiguous Commodity CVE)
   - Top-1 Predicted Candidate Actor ID
   - Fused Confidence Score & Hallucination Risk
   - Output Verdict (`INCONCLUSIVE`, `PROBABLE`, `HIGH_CONFIDENCE`)
   - Outcome Classification (`PROPER_ABSTENTION`, `FALSE_ATTRIBUTION`, or `EXECUTION_FAILURE`)
3. **Comparative Evaluation:**
   Both Full Hybrid and Retrieval-only baseline models must be evaluated on identical Task B inputs using identical scoring criteria.

---

## 3. Provenance & Verification Matrix

To maintain rigorous scientific accounting, all claims are classified by evidentiary source:

| Assertion / Specification | Provenance Status | Verification Method |
| :--- | :---: | :--- |
| **Statistical Power = 83.674%** | **VERIFIED COMPUTATION** | Recomputed from exact McNemar binomial summation via `verify_corrections.py`. |
| **Parameter $\theta = 0.80$** | **VERIFIED COMPUTATION** | Located in `run_power_audit.py` (line 104); verified that $\theta = 0.80 \implies \psi = 4.0$. |
| **Master Store SHA-256 Hashes** | **VERIFIED COMPUTATION** | Recomputed directly from actual 5 files on disk (`actual_file_sha256_manifest.json`). |
| **HNSW 0-byte `link_lists.bin`** | **VERIFIED COMPUTATION** | Inspected binary `header.bin` (`max_level_ = -1`) and verified against ChromaDB runtime. |
| **Abstention Threshold $\tau = 0.50$** | **INHERITED SPECIFICATION** | Grounded in `nexuscti/config.py`, `fusion/engine.py`, and `phase9_protocol_freeze.md`. |
| **Task B Denominator $N = 30$** | **INHERITED SPECIFICATION** | Grounded in Phase 8 protocol Section 2.2 and Phase 9 benchmark candidate manifest. |
| **Wilson Score Interval for Task B** | **INHERITED SPECIFICATION** | Grounded in Phase 8 protocol Section 3.3; verified mathematically in `verify_corrections.py`. |
| **Intention-to-Evaluate Rule** | **INHERITED SPECIFICATION** | Grounded in Phase 9.3 protocol Section 5. |

---

## 4. Governance Sign-Off Recommendation

1. Original approval record [`final_human_approval_record.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_9_final_reconciliation_20261011_232000/final_human_approval_record.md) is preserved without alteration.
2. Corrected version [`final_human_approval_record_v2.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_9_final_reconciliation_20261011_232000/final_human_approval_record_v2.md) has been created incorporating the statistical power notation fix and Section 4.7 codifying Task B open-set rules.
3. The human Governance Authority may now execute `final_human_approval_record_v2.md`.
4. **Phase 10 blind evaluation remains strictly UNAUTHORIZED until human execution is complete.**
