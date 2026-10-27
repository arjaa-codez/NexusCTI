# NexusCTI Phase 8.2 — Benchmark Design & Sample Size Recommendation

**Document Version:** 1.0  
**Date:** 2026-10-11  
**Experiment Root:** `experiments/phase8_2_power_and_verification_20261011_014200/`  

---

## 1. Executive Sample Size Recommendation

Based on the prospective exact power analysis across multiple planning scenarios:

```
========================================================================================================
RECOMMENDED BENCHMARK SAMPLE SIZE TARGETS (TASK A CLOSED SET)
========================================================================================================
Target Level           Sample Size (N)     Expected Power          Planning Rationale
--------------------------------------------------------------------------------------------------------
Minimal Feasible Target     N = 60             85.2% (at Phase 8)  Adequate power ONLY if the extreme 
                                               58.1% (at θ=0.80)   observed 6:1 ratio persists; underpowered
                                                                   under a standard +15% effect (58%).
Recommended Target          N = 80             94.4% (at Phase 8)  Reaches 73.7% power for large effects;
                                               73.7% (at θ=0.80)   strong compromise between collection
                                               35.4% (at θ=0.70)   feasibility and statistical rigor.
Ideal Asymptotic Target     N = 100            98.0% (at Phase 8)  Achieves ≥83.7% power for +15% gain
                                               83.7% (at θ=0.80)   and >44% for moderate (+10%) gain.
========================================================================================================
```

### Recommendation Statement:
We recommend targeting **$N = 80$ to $N = 100$ eligible, campaign-disjoint closed-set cases** (accompanied by $N = 25$ to $N = 30$ Task B open-set cases for a total benchmark size of $N \approx 105$–$130$ cases).

If real-world CTI report availability restricts collection to $N = 60$, the evaluation must explicitly state that it is powered solely to detect strong effects ($\theta \ge 0.85$, $\psi \ge 6.0$), and that an inconclusive result ($p > 0.05$) cannot rule out moderate or even large improvements ($\Delta \approx 10\%$–$15\%$).

---

## 2. Methodological Standards for the Next Benchmark Expansion

To ensure scientific validity and reproducibility, the expanded benchmark must enforce the following 10 standards:

1. **Strict Campaign Independence:** Multiple advisories, syndicated news reports, or foreign translations documenting the same underlying intrusion must be deduplicated into a single campaign entity.
2. **Threat Actor Diversity:** Cases must span at least 10–12 threat actors, with no single threat actor contributing more than 15% of the total test set to prevent clustering bias.
3. **Traceable Ground Truth:** Attribution labels must be backed by explicit government or vendor text citations; inferred or suspected attributions must be partitioned into Task B.
4. **Separate Task Architectures:** Closed-set classification (Task A) and open-set anomaly rejection (Task B) must be scored using mutually exclusive metrics.
5. **Zero Infrastructure Contamination:** Exact string deduplication must confirm 0.0% overlap between external test indicators and training knowledge graph telemetry.
6. **Zero Retrieval Index Contamination:** Held-out external reports must be strictly quarantined from the training retrieval database.
7. **Frozen Hyperparameters:** GNN weights, dense projections, fusion weights, and decision thresholds must be locked prior to test evaluation.
8. **Pre-Registration:** The primary endpoint, hypothesis test, and practical significance threshold must be timestamped before examining test predictions.
9. **Independent Development Set:** A dedicated development set ($N \approx 15$) must be reserved for any sanity checks, keeping the frozen test set ($N \ge 80$) untouched.
10. **Honest Reporting of Uncertainty:** If the expanded test fails to achieve $p \le 0.05$, the authors must report the result as inconclusive rather than modifying thresholds or metrics post-hoc.
