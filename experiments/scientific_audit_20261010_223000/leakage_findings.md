# Comprehensive Data Leakage Audit Findings

**Experiment ID:** `scientific_audit_20261010_223000`  
**Date:** October 10, 2026  
**Scope:** All 12 Benchmark Scenarios, Knowledge Graph (`knowledge_base.py`), Unstructured Corpus (`corpus.py`), and R-GCN Training Routine (`trainer.py`).

---

## 1. Executive Leakage Summary

| Leakage Class | Severity | Finding Status | Affected Cases | Key Finding & Remediation |
| :--- | :---: | :---: | :---: | :--- |
| **A. Split Contamination** | **MEDIUM** | **REVIEW** | 9 of 12 cases | The knowledge graph is constructed transductively; nodes within 3 hops of threat actors were included in the reachability-based training supervision labels. |
| **B. Graph Shortcut Leakage** | **LOW** | **PASS** | 0 cases (1 direct 1-hop) | No synthetic or unprincipled direct shortcuts exist from telemetry indicators (IPs, hashes) directly to threat actors. Case 2 tests direct malware identification (1-hop by definition). Multi-hop chains are preserved. |
| **C. Retrieval Text Leakage** | **MEDIUM** | **REVIEW** | 8 of 12 cases | Official CTI reports in the corpus explicitly cite technical indicators (e.g. `185.225.17.42`) and name the attributed actor. Expected in retrospective CTI, but means exact BM25 keyword matching can identify the actor directly. |
| **D. Duplicate / Overlap** | **MEDIUM** | **REVIEW** | 12 of 12 cases | All 12 benchmark cases correspond to the exact 6 threat campaigns documented in the 6 corpus reports. No entirely unseen out-of-distribution campaigns exist. |
| **E. Temporal / Provenance** | **LOW** | **PASS (Documented)** | All cases | Reports are retrospective post-incident forensic advisories (e.g., CISA AA20-352A published post-SolarWinds). The system performs retrospective forensic verification rather than predictive zero-day attribution. |
| **F. Evaluation & Tuning** | **MEDIUM** | **REVIEW** | All cases | Hyperparameters ($\alpha=0.5$ in capstone; fusion weights $0.45, 0.35, 0.20$ in core service) and thresholds were calibrated on these 12 cases. They must be treated as development/validation benchmark cases rather than fully held-out blind test sets. |

---

## 2. Detailed Findings by Leakage Dimension

### 2.1 Split Contamination (Transductive vs. Inductive Graph Learning)
- **Mechanism:** In `nexuscti/gnn/trainer.py`, `GNNAttributionTrainer._prepare_training_labels()` iterates over threat actors and computes `nx.single_source_shortest_path_length(nx_graph, actor_id, cutoff=3)`.
- **Evidence:** 
  - For Tier 1 and Tier 2 cases (`test_case_01` to `test_case_06`), the indicator nodes (e.g. `avsvmcloud.com`, `a3d9e84b...`, `f441c21d...`, `027cc450...`) are within 1 to 2 hops of their respective malware node and within 2 to 3 hops of the threat actor. Consequently, their tensor representations were trained with explicit actor cross-entropy supervision.
  - For Tier 3 and Tier 4 cases (`test_case_07`, `test_case_09`, `test_case_10`), the indicators (`185.225.17.42`, `203.0.113.88`, `91.242.217.5`) are 4 hops away from the actor node (or dynamically added temporary nodes), which falls outside the 3-hop supervision cutoff. These cases represent true relational topological inference.
- **Remediation Recommendation:**
  In future academic reporting, explicitly classify the benchmark as **Transductive Multi-Hop Verification** for Tiers 1–2 and **Inductive Deep-Chain Reasoning** for Tiers 3–4. Do not claim the entire benchmark is out-of-sample inductive.

---

### 2.2 Graph Shortcut Leakage
- **Mechanism:** Checking whether the knowledge graph contains artificial or circular edges connecting an indicator directly to an actor node (e.g., `185.225.17.42 -> actor_apt29`).
- **Evidence:**
  - Audited all 42 relational edges in `nexuscti/data/knowledge_base.py` and 53 triples in `cyber_attribution_engine/data/processed_graph/graph_metadata.json`.
  - Zero direct edges exist from IPv4 addresses, domains, or file hashes to `ThreatActor` nodes.
  - All paths follow strict STIX 2.1 schemas:
    $$\text{IPv4} \xrightarrow{\text{resolves\_to}} \text{Domain} \xrightarrow{\text{shares\_infra}} \text{Domain} \xrightarrow{\text{communicates\_with}} \text{Malware} \xrightarrow{\text{uses}} \text{ThreatActor}$$
  - `test_case_02` evaluates `Industroyer (CrashOverride)`. Because Industroyer is a malware entity, its edge `actor_sandworm --(uses)--> mal_industroyer` is 1 hop. This is legitimate direct tool attribution, not an indicator shortcut.
- **Verdict:** **PASS**. Graph topology represents legitimate cybersecurity domain knowledge.

---

### 2.3 Retrieval Leakage & Text-Grounding Analysis
- **Mechanism:** Checking whether query terms, indicator strings, or test answers appear verbatim in the retrieval corpus.
- **Evidence:**
  - In 8 of the 12 cases, the exact indicator string (e.g., `185.225.17.42`, `freescanonline.com`, `027cc45097f8...`) appears directly inside the narrative of the corresponding threat advisory in `nexuscti/data/corpus.py`.
  - For example, `rpt_cisa_apt29_solarwinds` explicitly states:
    > *"Upon establishing communication, the malware dynamically resolves intermediate IP addresses including 20.140.8.11 and shifts secondary staging to freescanonline[.]com, which resolves to 185.225.17.42."*
  - This indicator co-occurrence allows BM25 to score high term-frequency matches, effectively bypassing deep semantic reasoning for those specific text passages.
- **Verdict:** **REVIEW**. While indicator presence in advisories is realistic (analysts read real advisories containing known IOCs), it means Naive Vector RAG's performance is driven by exact keyword matches rather than semantic generalizability. When isolated indicators are absent from the text (e.g., dark subnets or fast-flux nodes), vector retrieval collapses.

---

### 2.4 Duplicate & Near-Duplicate Contamination
- **Evidence:**
  - The corpus consists of 6 authoritative threat reports.
  - The 12 benchmark cases represent multiple pivots into the same 6 campaign clusters (SolarWinds Orion, Fancy Bear NTLM relay, Lazarus AppleJeus crypto theft, Sandworm Industroyer/NotPetya, FIN7 POS theft, Volt Typhoon SOHO router mesh).
  - There are zero benchmark test cases from unseen actors (e.g. Charming Kitten, APT41, Kimsuky).
- **Verdict:** **REVIEW**. The benchmark tests multi-tiered infrastructural depth across known actor playbooks rather than open-world actor discovery.

---

### 2.5 Temporal Provenance
- **Evidence:**
  - `rpt_cisa_apt29_solarwinds`: Published December 17, 2020.
  - `rpt_mandiant_apt28_fancybear`: Published April 12, 2023.
  - `rpt_cisa_lazarus_applejeus`: Published April 14, 2022.
  - `rpt_cisa_sandworm_powergrid`: Published February 24, 2022.
  - `rpt_cisa_volt_typhoon_mesh`: Published February 7, 2024.
  - `rpt_mandiant_fin7_retail`: Published August 10, 2021.
- **Verdict:** **PASS (Properly Documented)**. The system is designed for retrospective, auditable triage of technical indicators against existing historical intelligence, not prospective predictive attribution of uncharacterized novel actors.

---

### 2.6 Evaluation & Tuning Leakage
- **Evidence:**
  - The fusion parameters ($\alpha = 0.45, \beta = 0.35, \gamma = 0.20$ and $\alpha = 0.5$) and cross-validation consistency thresholds were determined by observing outcomes across these 12 scenarios.
  - No separate held-out validation split exists.
- **Verdict:** **REVIEW**. To adhere to strict scientific rigor, these 12 cases must be described as a **Standardized Development Benchmark**, and an independent test set of newly documented campaigns must be used for future blind validation.
