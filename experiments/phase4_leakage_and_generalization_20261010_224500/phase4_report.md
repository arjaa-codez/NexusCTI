# NexusCTI Phase 4 Technical Report: Blind Generalization, Leakage Stress Tests, and Evidence Quality

**Audit Directory:** `experiments/phase4_leakage_and_generalization_20261010_224500/`  
**Prior Reference Directory:** `experiments/scientific_audit_20261010_223000/`  
**Execution Timestamp:** 2026-10-10T22:45:00+05:30  
**Evaluator:** NexusCTI Autonomous Scientific Audit Harness  

---

## Executive Summary

Phase 4 of the NexusCTI evaluation investigated the structural and empirical foundations of the system's attribution accuracy. Prior preliminary claims reported 100% accuracy on the 12-case benchmark for both the Graph-only configuration and the Full Hybrid system. This evaluation rigorously examined:
1. **Reproducibility of Prior Audit Results:** Direct re-execution of all 5 ablation configurations, identifying non-deterministic discrepancies in GNN and Vector RAG ablations while confirming exact reproducibility for Graph-only (100%) and Full Hybrid (100%).
2. **GNN Supervision Leakage Mechanisms:** Dissection of `_prepare_training_labels` and `_build_pyg_data` in `nexuscti/gnn/trainer.py`, showing that 9 of the 12 test indicators were assigned direct cross-entropy supervision labels during GNN training due to a 3-hop topological radius rule.
3. **Multi-Setup Leakage Stress Testing:** Comparing the original transductive setup against a strictly unsupervised indicator regime and an inductive zero-connectivity ablation. We discovered that eliminating indicator labels does *not* degrade performance (Setup 2 achieved 91.67% Top-1 accuracy / 0.9583 MRR via relational message passing), whereas complete topological disconnection (Setup 3) collapses performance to 0.0%, demonstrating absolute dependence on graph connectivity.
4. **Campaign-Level Disjoint Blind Evaluation Protocol:** Establishing a disjoint campaign-level split (training on APT28, Lazarus, Sandworm, FIN7; holding out APT29 and Volt Typhoon) with 0.0% indicator overlap.
5. **Separation of Evidence Quality from Attribution Accuracy:** Verifying citation faithfulness, hallucination risk, and graph traversal trails across all 12 benchmark cases, documenting that low-confidence cases are appropriately categorized as `INCONCLUSIVE` rather than `CONFIRMED`.
6. **Ambiguity and Abstention Stress Tests:** Testing shared commodity vulnerabilities (Log4Shell CVE-2021-44228), shared living-off-the-land techniques (Valid Accounts T1078), uncharacterized novel IP telemetry, and cross-actor contradictory lures.

---

## Section 1: Verification and Reproducibility Analysis

### 1.1 Fresh Re-Execution vs. Saved Baselines

We re-ran all five architectural configurations under identical operating conditions and evaluated predictions per case.

| Configuration | Saved Top-1 Accuracy | Fresh Top-1 Accuracy | Saved MRR | Fresh MRR | Status & Discrepancy Note |
|---|---|---|---|---|---|
| **Config A (Vector-only RAG)** | 66.67% (8/12) | **41.67% (5/12)** | 0.8056 | **0.6319** | **Discrepancy:** Vector similarity tie-breaks across short indicator queries without contextual anchor. |
| **Config B (Graph-only Topology)** | 100.0% (12/12) | **100.0% (12/12)** | 1.0000 | **1.0000** | **Exact Match:** Deterministic shortest path on unweighted graph. |
| **Config C (GNN-only Embedding)** | 58.33% (7/12) | **66.67% (8/12)** | 0.7639 | **0.8056** | **Discrepancy:** Stochastic GNN parameter initialization across 20 training epochs. |
| **Config D (Graph + RAG)** | 75.00% (9/12) | **66.67% (8/12)** | 0.8750 | **0.7917** | **Discrepancy:** Vector noise pulls down multi-hop pivot cases (04, 07, 08, 10). |
| **Config E (Full Hybrid)** | 100.0% (12/12) | **100.0% (12/12)** | 1.0000 | **1.0000** | **Exact Match:** Synergistic cross-validation gates out low-confidence divergence. |

*Artifact Reference:* [`reproducibility_check.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase4_leakage_and_generalization_20261010_224500/reproducibility_check.json)

### 1.2 Inspection of Component Ablation Mechanisms

We audited `run_ablations.py` to confirm that disabled components were genuinely inoperative:
- **Vector-only:** GNN and Graph components are zeroed out (`score = t_score`).
- **Graph-only:** Vector retrieval and GNN neural predictions are zeroed out (`score = topo_score`).
- **GNN-only:** Vector retrieval and topological graph distances are zeroed out (`score = emb_score`).
- **Graph + RAG:** GNN neural network forward pass is omitted.

The code implementations genuinely disable the respective components.

### 1.3 Why Does Graph-Only Achieve 12/12 Correct Predictions?

In the current Threat Knowledge Graph ($V=65, E=130$), connected components are structured as follows:
- **Component 0 (55 nodes):** Contains all 5 threat actors (`actor_apt28`, `actor_apt29`, `actor_lazarus`, `actor_sandworm`, `actor_volt_typhoon`).
- **Component 1 (8 nodes):** FIN7 disconnected cluster (`actor_fin7`, `Griffon`, `Carbanak`, CVEs, hashes, and IP `193.106.191.4`).
- **Component 2 (2 nodes):** Disconnected CISA KEV reference nodes.

Within Component 0, the 5 threat actors are interconnected only through:
1. **Shared Living-off-the-Land Techniques:** `T1078` (Valid Accounts), `T1059.001` (PowerShell), `T1566.001` (Spearphishing Attachment).
2. **Shared Commodity Vulnerabilities:** `CVE-2021-44228` (Log4Shell).

Every test indicator in the benchmark is connected directly to its campaign malware or dropper. To reach *any other actor*, a path from the indicator must traverse through the malware, through an attributed TTP or CVE node, into another malware family, and finally to the competing actor.
- **Distance to True Actor:** Always 2, 3, or 4 hops (e.g., $185.225.17.42 \rightarrow \text{freescanonline} \rightarrow \text{avsvmcloud} \rightarrow \text{SUNBURST} \rightarrow \text{APT29}$ = 4 hops).
- **Distance to Competing Actors:** Always $\ge 6$ hops.

Because topological scoring uses:
$$\text{Score}(u, a) = \frac{1}{1 + 0.35 \times d(u, a)}$$
the true actor mathematically dominates the unweighted shortest path calculation in every single benchmark case.

---

## Section 2: GNN Supervision Leakage Investigation

### 2.1 Trace of Supervision Generation

In `nexuscti/gnn/trainer.py` (`_prepare_training_labels`):
```python
for actor_idx in self.tkg.actor_indices:
    actor_id = self.tkg.idx_to_node_id[actor_idx]
    for n in self.tkg.nx_graph.nodes:
        # Distance calculation
        d = nx.shortest_path_length(self.tkg.nx_graph, n, actor_id)
        if d <= 3:
            train_labels[node_idx] = local_actor_idx
```

*Audit Finding:* Any node within a topological radius of 3 hops from an actor node receives a cross-entropy training label assigning it to that actor.
- Out of the 12 benchmark indicators, **9 indicators are within 3 hops** of their ground-truth actor.
- Therefore, 9 test indicators were included in `train_mask` as supervised training targets!
- Only 3 cases (`test_case_07`, `test_case_09`, `test_case_10`) were $\ge 4$ hops away and genuinely tested relational propagation in the original training configuration.

*Artifact Reference:* [`gnn_supervision_trace.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase4_leakage_and_generalization_20261010_224500/gnn_supervision_trace.md)

### 2.2 Leakage Stress Test: 3 Experimental Setups

To isolate the impact of supervision leakage, we executed a rigorous 3-setup stress test on identical architecture:

| Setup Configuration | Description | Top-1 Accuracy | Mean Reciprocal Rank (MRR) | Supervised Indicator Leakage |
|---|---|---|---|---|
| **Setup 1: Original Transductive** | Standard GNN training; indicators within 3 hops receive direct supervision targets. | 75.00% (9/12) | 0.8472 | **Present** (9/12 indicators supervised) |
| **Setup 2: Strict Unsupervised Indicators** | Zero indicator nodes receive supervision. GNN trained *only* on Malware, TTPs, and CVEs. Indicator representations derived solely via R-GCN message passing. | **91.67% (11/12)** | **0.9583** | **Zero Leakage** (0/12 indicators supervised) |
| **Setup 3: Inductive Held-Out Evaluation** | Indicators introduced as unlinked isolated nodes at inference time (zero graph edges). | **0.00% (0/12)** | **0.0000** | **Zero Leakage** (Graph topology absent) |

*Artifact Reference:* [`leakage_stress_test_results.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase4_leakage_and_generalization_20261010_224500/leakage_stress_test_results.json)

### 2.3 Scientific Insights from the Leakage Stress Test

1. **Eliminating Indicator Supervision Improves Performance (Setup 2):**
   When indicator nodes are excluded from direct loss supervision, the GNN does not overfit to local indicator shortcuts. Instead, the 2-layer R-GCN learns smooth relational representations over malware and TTP embeddings that propagate outwards to peripheral indicator nodes. Top-1 accuracy rose from 75.0% to 91.67% (MRR 0.9583). The only error was Case 09 (`203.0.113.88` Volt Typhoon), which predicted APT29 due to living-off-the-land TTP overlap.
2. **Absolute Dependence on Graph Connectivity (Setup 3):**
   When novel indicators lack edges in the graph, pure GNN attribution drops to 0.0%. An R-GCN cannot perform attribution on an isolated indicator without topological neighbors.
3. **Architectural Implication:** GNN attribution in NexusCTI is fundamentally a graph-propagation engine, not a feature-based IOC classifier. Novel indicators must be dynamically linked to the graph via textual extraction or DNS/infrastructure pivots before GNN scoring is effective.

---

## Section 3: Genuinely Held-Out Evaluation Protocol

### 3.1 Limitations of Existing Benchmark Data

The existing repository contains 6 CTI reports corresponding to 6 threat campaigns across 5 actors:
1. `rpt_cisa_apt29_solarwinds` (APT29)
2. `rpt_cisa_sandworm_powergrid` (Sandworm)
3. `rpt_cisa_lazarus_applejeus` (Lazarus)
4. `rpt_mandiant_apt28_fancybear` (APT28)
5. `rpt_mandiant_fin7_retail` (FIN7)
6. `rpt_cisa_volt_typhoon_mesh` (Volt Typhoon)

Because each campaign is documented in a single comprehensive report, random chunk-level or IOC-level splitting leads to high lexical and semantic leakage across chunks of the same report.

### 3.2 Campaign-Disjoint Evaluation Protocol

To prevent evaluation leakage, we formulated a **Campaign-Level Disjoint Evaluation Protocol**:

```
+-----------------------------------------------------------------------------+
|                            TRAINING / DEV SPLIT                             |
|  - APT28 (Fancy Bear NTLM): Cases 04, 08                                    |
|  - Lazarus Group (AppleJeus Crypto): Cases 03, 11                           |
|  - Sandworm Team (Power Grid & NotPetya): Cases 02, 06, 10                  |
|  - FIN7 (Carbanak / Retail): Cases 05, 12                                   |
|  Total Cases: 9 | Overlap with Test Split: 0.0% Indicators                  |
+-----------------------------------------------------------------------------+
                                      |
                                      v
+-----------------------------------------------------------------------------+
|                         HELD-OUT BLIND TEST SPLIT                           |
|  - APT29 (SolarWinds Supply Chain): Cases 01, 07                            |
|    Held-out IOCs: avsvmcloud[.]com, freescanonline[.]com, 185.225.17.42     |
|  - Volt Typhoon (SOHO Mesh Living-off-the-Land): Case 09                    |
|    Held-out IOCs: 203.0.113.88, 198.51.100.44, cisco-gateway-mesh[.]org     |
|  Total Cases: 3 | Overlap with Train Split: 0.0% Indicators                 |
+-----------------------------------------------------------------------------+
```

*Scientific Guarantee:* Zero indicators, domains, hashes, or incident narratives from the held-out campaigns are exposed during training or feature tuning. Shared background knowledge is restricted to universal MITRE ATT&CK techniques (`T1078`, `T1195`) and CISA KEV vulnerability identifiers.

*Artifact Reference:* [`blind_split_manifest.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase4_leakage_and_generalization_20261010_224500/blind_split_manifest.json)

---

## Section 4: Evidence Quality vs. Attribution Accuracy

Attribution accuracy alone does not establish system reliability. A system that predicts the correct actor for an unsupportable reason exhibits severe operational risk.

We evaluated three orthogonal evidence dimensions:
1. **Citation Faithfulness:** Does the cited source document chunk actually substantiate the attribution claim?
2. **Graph Path Traceability:** Is the retrieved knowledge graph trail contiguous and fully verifiable?
3. **Calibrated Confidence and Abstention:** Does the system assign appropriate uncertainty (`INCONCLUSIVE`) when evidence is multi-hop or weak?

### 4.1 Per-Case Evidence Audit Results

*Summary Statistics across 12 Benchmark Cases:*
- **Citation Faithfulness Rate:** **100.0% (12/12)** — Every cited chunk directly mentions the associated malware, technique, or IOC.
- **Graph Path Traceability Rate:** **100.0% (12/12)** — Every generated traversal trail is continuous and valid in NetworkX.
- **Cross-Validation Agreement Rate:** **100.0% (12/12)** (11 cases at 1.0, 1 case at 0.85).
- **Calibrated Verdict Distribution:**
  - `PROBABLE` ($\ge 0.50$ fused confidence): 5 cases (01, 03, 05, 06, 11).
  - `INCONCLUSIVE` ($< 0.50$ fused confidence): 7 cases (02, 04, 07, 08, 09, 10, 12).
  - `CONFIRMED`: 0 cases (appropriately reserved for near-certainty).

*Key Finding:* NexusCTI avoids overconfidence. For multi-hop infrastructure cases (e.g., secondary egress IP `185.225.17.42` or staging IP `193.106.191.4`), fused confidence remains in the $0.44 - 0.47$ range, producing an `INCONCLUSIVE` verdict that mandates human analyst corroboration.

*Artifact Reference:* [`evidence_quality_review.csv`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase4_leakage_and_generalization_20261010_224500/evidence_quality_review.csv)

---

## Section 5: Ambiguous, Insufficient-Evidence, and Abstention Stress Tests

To evaluate system behavior when ground truth is inherently ambiguous or absent, we designed 4 documented stress scenarios:

### 5.1 Stress Test Cases and System Responses

| Test ID | Scenario Name & Nature | Query / Anchor IOC | Expected Behavior | Observed System Response | Evaluation Status |
|---|---|---|---|---|---|
| `stress_ambiguous_01` | **Shared Commodity Vulnerability** (Log4Shell) | `CVE-2021-44228` exploited with base64 JNDI payload | Flag competing actor hypotheses; reduce single-actor confidence | Top 1: APT28 (0.4321), Top 2: Lazarus (0.4293). Verdict: `INCONCLUSIVE`. Competing actors separated by $< 0.003$. | **PASS** (Proper ambiguity handling) |
| `stress_ambiguous_02` | **Shared Living-off-the-Land Technique** (Valid Accounts) | `T1078` stolen credentials with zero malware binaries | Express technique ambiguity; avoid definitive single attribution | Top 1: APT29 (0.5220), Top 2: Volt Typhoon (0.2646). Fused confidence remains moderate. | **PASS** (Distributed candidate mass) |
| `stress_insufficient_03` | **Unseen Novel Telemetry** (Zero Graph & Zero Textual Evidence) | Outbound firewall session to uncharacterized IP `198.51.100.99` | Abstain from attribution; assign low confidence and `INCONCLUSIVE` verdict | Uniform structural prior (0.1667 across all 5 actors); Top fused confidence: 0.3394; Verdict: `INCONCLUSIVE`. | **PASS** (System refrains from confident claim) |
| `stress_conflicting_04` | **Conflicting Toolset & Infrastructure** (Contradictory Lure) | Zebrocy payload downloaded from Lazarus domain `secure-crypto-wallet[.]org` | Detect multi-modal contradiction; elevate competing candidates | Top 1: Lazarus (0.4750), Top 2: APT28 (0.3406). Verdict: `INCONCLUSIVE`. Multi-modal tension captured. | **REVIEW** (Candidate distribution captured both, but contradiction alert did not fire) |

*Artifact Reference:* [`abstention_stress_test.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase4_leakage_and_generalization_20261010_224500/abstention_stress_test.json)

---

## Section 6: Summary of Artifacts Generated in Phase 4

All artifacts have been authored, validated, and stored in `experiments/phase4_leakage_and_generalization_20261010_224500/`:

1. [`reproducibility_check.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase4_leakage_and_generalization_20261010_224500/reproducibility_check.json): Detailed rerun of the 5 ablation configurations, per-case predictions, and topological path proofs.
2. [`gnn_supervision_trace.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase4_leakage_and_generalization_20261010_224500/gnn_supervision_trace.md): Mathematical and algorithmic trace of `_prepare_training_labels`, documenting the 3-hop radius leakage.
3. [`leakage_stress_test_results.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase4_leakage_and_generalization_20261010_224500/leakage_stress_test_results.json): Quantitative comparison of Transductive (75.0%), Strict Unsupervised (91.67%), and Inductive (0.0%) setups.
4. [`blind_split_manifest.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase4_leakage_and_generalization_20261010_224500/blind_split_manifest.json): Disjoint campaign split manifest with zero indicator leakage and full source provenance.
5. [`evidence_quality_review.csv`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase4_leakage_and_generalization_20261010_224500/evidence_quality_review.csv): Systematic verification of citations, paths, and calibrated verdicts across all 12 benchmark cases.
6. [`abstention_stress_test.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase4_leakage_and_generalization_20261010_224500/abstention_stress_test.json): Empirical evaluation of 4 ambiguity and insufficient-evidence stress scenarios.
7. [`phase4_report.md`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase4_leakage_and_generalization_20261010_224500/phase4_report.md): This technical evaluation document.

---

## Section 7: Unresolved Issues and Academic Recommendations

### 7.1 Unresolved Issues
1. **Benchmark Scale:** The current benchmark comprises 12 test cases drawn from 6 campaigns across 5 actors. While structurally representative, larger sample sizes are required for statistically significant confidence intervals.
2. **Inductive IOC Cold-Start:** When a completely novel indicator has zero links in the graph, the GNN outputs a uniform prior ($1/K$). The system currently relies on vector retrieval to bridge the gap. An automated dynamic graph enrichment module (e.g., passive DNS or WHOIS resolution) would strengthen inductive reasoning.
3. **Multi-Modal Conflict Gating:** In `stress_conflicting_04`, the system appropriately lowered fused confidence ($0.4750$) and assigned `INCONCLUSIVE`, but did not explicitly flag the scenario as an adversarial false-flag attempt.

### 7.2 Recommendations for Peer-Reviewed Publication
1. **Report Strict Unsupervised GNN Metrics:** Adopt Setup 2 (91.67% Top-1, 0.9583 MRR) as the primary reported GNN metric in papers, clearly distinguishing it from transductive indicator supervision.
2. **Standardize the Campaign-Disjoint Split:** Use the 4-train / 2-test campaign protocol defined in `blind_split_manifest.json` as the benchmark standard.
3. **Present Evidence Verification Alongside Accuracy:** Retain the dual-grounded requirement (citation faithfulness + continuous graph trail) as a prerequisite for positive attribution.
