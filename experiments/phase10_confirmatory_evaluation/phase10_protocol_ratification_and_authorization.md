# NexusCTI Phase 10 — Formal Protocol Ratification & Execution Authorization

**Protocol Version:** NexusCTI Preregistered Evaluation Protocol v2.2-amended (incorporating Protocol Amendment 3)  
**Governing Authority:** NexusCTI Independent Evaluation Governance Committee & Lead Investigator  
**Date of Authorization:** 2026-10-28  
**Project Root:** `c:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI`  
**Execution Phase:** Phase 10 — Confirmatory Prospective Benchmark Evaluation  

---

## 1. Formal Ratification Declaration

Pursuant to the successful completion and verification of all 12 pre-signature gates in Phase 9.9 ([`phase9_9_decision.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_9_final_reconciliation_20261011_232000/phase9_9_decision.md)), the Principal Investigator hereby ratifies **Protocol Amendment 3** and authorizes the execution of **Phase 10: Confirmatory Prospective Benchmark Evaluation**.

### Ratified Protocol Specifications:
1. **Primary Endpoint:** Paired Top-3 Attribution Accuracy on $N = 100$ independent closed-set Task A campaigns comparing Full Hybrid vs. Retrieval-only.
2. **Primary Hypothesis Test:** Exact two-sided McNemar test on discordant pairs ($b$ vs $c$) with significance level $\alpha = 0.05$.
3. **Directional Superiority Requirement:** $\hat{\Delta} = (b - c) / N > 0$.
4. **Prespecified Confidence Interval:** 95% Agresti–Min (2005) pseudo-observation paired risk difference interval:
   $$\tilde{\Delta} \pm 1.95996 \cdot \widetilde{\text{SE}}, \quad \text{where } \tilde{b} = b + 1, \tilde{c} = c + 1, \tilde{N} = N + 2$$
5. **Planning Target:** $+15.0$ percentage points ($83.67\%$ power at $N = 100, q = 0.25, \theta = 4.0$) preserved as sample size planning MDE only.
6. **Task B Endpoint:** Proper abstention fidelity and false-attribution suppression across $N = 30$ independent out-of-registry novel intrusion campaigns.
7. **Storage Governance:** Strict enforcement of the 7-Step Disposable Native ChromaDB Runtime Snapshot Lifecycle (Option C), ensuring zero bytes modified on the authoritative master store (`cyber_attribution_engine/data/chroma_db/`).

---

## 2. Countersigned Governance Block

```
========================================================================================
                      FORMAL PROTOCOL RATIFICATION & EXECUTION ORDER
========================================================================================

Ratifying Authority Name:   Arjaa Chatterjee
Official Title / Role:      Principal AI Systems Architect & Lead Security Engineer
Institutional Affiliation: NexusCTI Autonomous Threat Attribution Research Lab
Ratified Protocol Version:  [X] NexusCTI Preregistered Evaluation Protocol v2.2-amended
Action on Amendment 3:      [X] RATIFIED AND APPROVED
Phase 10 Execution Order:   [X] AUTHORIZED TO EXECUTE PHASE 10 BLIND BENCHMARK
Status:                     FORMALLY RATIFIED & AUTHORIZED FOR IMMEDIATE EXECUTION
Timestamp:                  2026-10-28T02:05:00+05:30

========================================================================================
```
