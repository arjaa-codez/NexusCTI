# NexusCTI Blind Evaluation Protocol: Campaign-Level Disjoint Evaluation Standard

**Document Version:** 1.0 (Phase 5 Hardened Benchmark Specification)  
**Experiment Root:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\experiments\phase5_scientific_validation_20261010_225000\`  
**Date:** 2026-10-10  
**Evaluator:** Independent Audit Suite  

---

## 1. Motivation & Scope

Prior preliminary evaluations of NexusCTI evaluated all 12 benchmark test cases against a monolithic Threat Knowledge Graph and an unpartitioned Threat Corpus. This introduced two critical forms of evaluation leakage:
1. **Transductive Graph Leakage:** All 12 test indicators were embedded directly into the knowledge graph structure prior to inference, with 9 of the 12 indicators directly receiving ground-truth actor supervision during GNN training.
2. **Retrieval Contamination:** The source reports containing the answers to the benchmark scenarios were fully indexed in the vector database, enabling the vector retriever to retrieve verbatim text chunks rather than performing generalized cross-source inference.

This protocol establishes a formal **Campaign-Level Disjoint Split Standard** designed to prevent data leakage and provide a sound methodology for future prospective evaluations.

---

## 2. Dataset Partitioning Specification

The NexusCTI dataset consists of 6 CTI incident reports documenting 6 threat campaigns across 5 adversary groups. The benchmark dataset contains 12 structured scenarios.

### 2.1 Split Assignment

| Split Role | Campaign ID | Target Threat Actor | Source Report ID | Benchmark Test Cases |
|---|---|---|---|---|
| **Training / Dev** | `cmp_apt28_ntlm` | APT28 (Fancy Bear) | `rpt_mandiant_apt28_fancybear` | `test_case_04`, `test_case_08` |
| **Training / Dev** | `cmp_lazarus_applejeus` | Lazarus Group | `rpt_cisa_lazarus_applejeus` | `test_case_03`, `test_case_11` |
| **Training / Dev** | `cmp_sandworm_powergrid` | Sandworm Team | `rpt_cisa_sandworm_powergrid`, `rpt_dragos_sandworm_industroyer_wiper` | `test_case_02`, `test_case_06`, `test_case_10` |
| **Training / Dev** | `cmp_fin7_retail` | FIN7 | `rpt_mandiant_fin7_carbanak` | `test_case_05`, `test_case_12` |
| **Held-Out Test** | `cmp_apt29_solarwinds` | APT29 (Cozy Bear / NOBELIUM) | `rpt_cisa_apt29_solarwinds` | `test_case_01`, `test_case_07` |
| **Held-Out Test** | `cmp_volt_typhoon_mesh` | Volt Typhoon | `rpt_cisa_volt_typhoon_critical_infra` | `test_case_09` |

### 2.2 Split Statistics
- **Total Training Scenarios:** 9 cases (75.0%)
- **Total Held-Out Test Scenarios:** 3 cases (25.0%)
- **Indicator Overlap Between Splits:** **0.0%** (Zero shared IP addresses, domain names, hashes, or staging URLs).
- **Report Text Overlap:** **0.0%** (Disjoint source reports).
- **Legitimate Background Knowledge Overlap:** Shared universal MITRE ATT&CK techniques (`T1078` Valid Accounts, `T1059.001` PowerShell, `T1566.001` Spearphishing) and common CVE references (`CVE-2021-44228`).

---

## 3. Leakage Prevention Rules

To guarantee evaluation validity, an experiment conforming to this protocol must strictly enforce the following rules:

### Rule A: Graph Construction Isolation
1. All indicator nodes, malware nodes, and relationship edges originating exclusively from the held-out reports (`rpt_cisa_apt29_solarwinds` and `rpt_cisa_volt_typhoon_critical_infra`) must be completely excluded from the training knowledge graph.
2. In Phase 5 controlled ablation audits, this corresponded to removing 28 directional edges (documented in `graph_edge_removal_manifest.csv`).
3. Under no circumstances may held-out indicators appear in `train_indices` or `train_labels` of the GNN trainer.

### Rule B: Retrieval Corpus Isolation
1. Held-out campaign reports must be purged from the text corpus before chunking and embedding.
2. The vector index (`DenseRetriever`) must be constructed strictly from training set report chunks.
3. If an incoming test query contains an indicator not present in the indexed corpus, the retriever must return general TTP/contextual matches or empty scores without hallucinating.

### Rule C: Parameter and Threshold Freezing
1. All hyperparameter tuning (GNN learning rate, epochs, hidden dimensions, fusion weights $w_{gnn}, w_{rag}, w_{topo}$, and decision thresholds for `CONFIRMED`, `PROBABLE`, `INCONCLUSIVE`) must be finalized exclusively on the 9 training/dev cases.
2. The held-out test split must be evaluated exactly once under frozen parameters.

---

## 4. Evaluation Limitations of Existing Data

### 4.1 The Evidence-Absence Dilemma
An audit of the existing repository reveals an important structural reality:
- When a campaign is completely removed from both the graph and the retrieval corpus (Variant 5 in Phase 5), the system has **zero underlying evidence** linking the novel indicator (e.g. `avsvmcloud[.]com`) to the threat actor (APT29).
- In this regime, accuracy on held-out cases drops to **0.0% for Graph-only and Vector-only**, and **33.33% for Full Hybrid** (due solely to diffuse technique overlap).
- **Scientific Conclusion:** Evaluating completely unseen campaigns where no background intelligence exists is not a test of generalized reasoning; it is an **Evidence-Absence Test**. Attribution is fundamentally an evidence-synthesis problem; an algorithm cannot deduce that a previously unknown IP address belongs to an actor without either telemetry linkages or contextual reports.

### 4.2 Feasibility of a Prospective Blind Evaluation Today
- **Finding:** A true, statistically robust blind evaluation cannot be constructed exclusively from the existing 6 reports and 12 benchmark cases without either:
  1. Ingesting at least 15–20 additional real-world CTI reports from independent sources (e.g., CISA, Mandiant, CrowdStrike, SentinelOne) documenting separate campaigns conducted by the same 5 actors, OR
  2. Evaluating cross-campaign technique attribution where novel indicators are linked to known actors via infrastructure telemetry (e.g., Passive DNS, WHOIS, ASN ownership).
- **Prohibition:** We explicitly refuse to fabricate synthetic reports or fake campaigns to artificially inflate sample size.

---

## 5. Provenance and Integrity Verification

| File / Component | Relative Path | SHA-256 Checksum |
|---|---|---|
| Benchmark Dataset | `nexuscti/eval/benchmark_cases.py` | `d59cbbaeaeb8d1d8ef3cb83e89547b7468132f831fbb9c81a5477b789178129d` |
| Threat Corpus | `nexuscti/data/corpus.py` | `0523ecddfef4375b0ecb39d1b01777d130ce5ef8f8a3794770146b281f69666f` |
| Knowledge Base | `nexuscti/data/knowledge_base.py` | `c05d76d435eebe2d5da124e4d7e1742416f0e4b7c8df0cc9622d14cb837cfcb3` |
| GNN Trainer | `nexuscti/gnn/trainer.py` | `d601b088e847aeae9e7eaec88ba4ef98e54619ee67bb939c368d37fc1c55db90` |
| Fusion Engine | `nexuscti/fusion/engine.py` | `43593b45e998797f7bbff2f26019b8ecf30b9d99723554e20b333ba3d7a8e8e7` |
