# NexusCTI Scientific Limitations and Claims Register

**Directory:** `experiments/phase5_scientific_validation_20261010_225000/`  
**Audit Date:** 2026-10-10  
**Evaluator:** Independent Audit Suite  

Every performance claim, architectural assertion, and experimental finding from preliminary project documentation and Phases 1–4 has been audited against independent empirical execution and source code inspection.

---

## Claims Register Table

| Claim ID | Original Claim Description | Source Context | Phase 5 Audit Status | Audit Evidence & Scientific Determination |
|---|---|---|---|---|
| **CLM-01** | *“Full Hybrid NexusCTI achieves 100% Top-1 accuracy and 1.0 MRR on the 12-case benchmark.”* | Preliminary Benchmark Report | **VERIFIED (TRANSDUCTIVE ONLY)** | Reproduced deterministically on the full transductive graph (12/12, Top-1 = 100.0%, MRR = 1.0). However, this score is valid **only under transductive graph presence and indexed retrieval**. It drops to 75.0% (33.3% on held-out) under blind evaluation. |
| **CLM-02** | *“Graph-only topological attribution achieves 100% Top-1 accuracy (12/12) without text retrieval.”* | Phase 2 & 3 Ablation Reports | **CONFIRMED LEAKAGE (GRAPH SHORTCUT)** | While 12/12 is computationally reproducible, it is driven entirely by graph construction topology: all 12 test indicators are wired exclusively to their true campaign's malware. Distance to true actor is 2–4 hops; distance to competing actors is $\ge 6$ hops. When held-out edges are removed, held-out accuracy collapses to **0.0% (0/3)**. |
| **CLM-03** | *“GNN Relational Message Passing achieves 58.33% Top-1 accuracy.”* | Phase 3 Ablation Report | **NOT REPRODUCED (STOCHASTIC VARIANCE)** | Evaluated across 5 independent training runs: GNN-only accuracy ranges from **50.0% to 75.0%** (Mean: 63.33% ± 8.5%, MRR: 0.7917 ± 0.0465). The saved 58.33% was a single arbitrary checkpoint artifact resulting from unseeded Adam weight initialization on a tiny 65-node graph. |
| **CLM-04** | *“Naive Vector-only RAG achieves 66.67% Top-1 accuracy.”* | Phase 3 Ablation Report | **NOT REPRODUCED (HASH RANDOMIZATION)** | Fresh runs without fixing `PYTHONHASHSEED` yield **41.67% to 58.33%** (Mean: 50.0% ± 0.0% within session, MRR: 0.625). Root cause: `SemanticTextEncoder` relies on Python's built-in `hash(word)` which uses randomized SipHash salt per process session, shifting vector projection buckets across restarts. |
| **CLM-05** | *“9 of 12 benchmark indicators received direct ground-truth supervision during GNN training.”* | Phase 4 Audit Report | **VERIFIED & CONFIRMED LEAKAGE** | Directly inspected `_prepare_training_labels` in `nexuscti/gnn/trainer.py`. Any node within 3 hops of an actor receives a cross-entropy target label. Exactly 9 of the 12 test indicators are within 3 hops and were included in the training loss. Only Cases 07, 09, and 10 were $\ge 4$ hops away. |
| **CLM-06** | *“Eliminating indicator supervision from GNN training maintains high relational accuracy.”* | Phase 4 Stress Test Report | **VERIFIED** | Training strictly on malware and TTP nodes without any indicator labels (Setup 2 in Phase 4) achieves **91.67% Top-1 accuracy (11/12)** and 0.9583 MRR via R-GCN message passing. Message passing from malware/TTP nodes effectively propagates actor affinity to unlabelled peripheral indicator nodes. |
| **CLM-07** | *“GNN can attribute novel unlinked indicators in an inductive setting.”* | Architectural Claim | **CONFIRMED LEAKAGE / DISPROVEN** | When an indicator is introduced as an isolated node with zero graph edges (Setup 3 in Phase 4, Variant 5 in Phase 5), GNN accuracy is **0.0% (0/12)**. An R-GCN has no neighboring edges to aggregate features from; it cannot perform inductive attribution without graph linkage. |
| **CLM-08** | *“Vector RAG generalizability across threat intelligence sources is proven by the benchmark.”* | Phase 1 & 2 Narrative | **CONFIRMED LEAKAGE (RETRIEVAL CONTAMINATION)** | Audit of `retrieval_contamination_audit.json` proves that in 100% of benchmark cases where retrieval succeeded, the top-k retrieved chunks were from the exact CTI source report documenting the campaign. The benchmark queries are lexical paraphrases of the indexed reports, testing report lookup rather than cross-source deduction. |
| **CLM-09** | *“The fused confidence score represents a calibrated attribution probability.”* | System Documentation | **DISPROVEN / CONFIRMED MISCHARACTERIZATION** | The fused confidence score is an ad-hoc linear blend ($0.45 S_{gnn} + 0.55 S_{topo}$ combined with $S_{rag}$). It does not satisfy probability axioms, produces a Brier score of 0.2677 and log loss of 0.7288, and cannot be treated as a posterior probability $P(Y=a \mid X)$. |
| **CLM-10** | *“NexusCTI achieves zero hallucination rate across all evaluations.”* | Capstone Report Narrative | **CONFIRMED MISCHARACTERIZATION** | Zero incorrect predictions on a 12-case transductive benchmark where 9 cases received training labels cannot be equated to a zero real-world hallucination rate. When tested on conflicting cross-actor lures (`stress_conflicting_04`), the system failed to trigger a contradiction alert. |
| **CLM-11** | *“The system properly abstains on insufficient evidence.”* | Phase 4 Stress Test Report | **VERIFIED** | When tested with completely novel uncharacterized telemetry (`198.51.100.99`), the system assigned a low fused confidence (0.3452) and correctly categorized the incident as `INCONCLUSIVE`, preventing a false positive attribution. |
| **CLM-12** | *“A true prospective blind evaluation can be completed on the existing dataset.”* | Preliminary Phase 4 Recommendation | **INCONCLUSIVE / STRUCTURAL LIMITATION** | Removing held-out campaigns from both graph and text leaves the system with zero underlying intelligence for those actors, turning the evaluation into an evidence-absence test (0.0% accuracy). A true prospective blind evaluation requires ingesting additional real-world CTI reports from independent sources. |

---

## Summary of Audit Verdicts

- **VERIFIED:** 3 claims (CLM-01 transductive, CLM-05 supervision leakage, CLM-11 abstention)
- **NOT REPRODUCED:** 2 claims (CLM-03 GNN variance, CLM-04 Python hash variance)
- **CONFIRMED LEAKAGE:** 4 claims (CLM-02 graph shortcut, CLM-07 inductive claim, CLM-08 retrieval contamination, CLM-05 supervision)
- **CONFIRMED MISCHARACTERIZATION:** 2 claims (CLM-09 probability claim, CLM-10 zero hallucination claim)
- **INCONCLUSIVE / LIMITATION:** 1 claim (CLM-12 prospective blind evaluation feasibility)
