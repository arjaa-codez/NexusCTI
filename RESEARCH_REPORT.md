# 📄 NexusCTI: Synergistic Cyber-Threat Attribution via Relational GNNs and Text-Grounded Retrieval-Augmented Generation

**Author:** NexusCTI Project Research Team  
**Date:** October 2026  
**Artifacts Repository:** `NexusCTI/`  

---

## Abstract
Traditional cyber-threat attribution in Security Operations Centers (SOCs) relies on siloed paradigms: standard vector-based Retrieval-Augmented Generation (RAG) excels at digesting unstructured threat advisories but lacks multi-hop structural reasoning over disparate indicators; conversely, Graph Neural Networks (GNNs) effectively model relational network infrastructure and TTP topologies but lack qualitative campaign context, tool modifications, and explanatory narratives. We introduce **NexusCTI**, a multi-modal attribution framework that harmonizes structural GNN relational message passing with text-grounded dense-sparse RAG. Through an empirical benchmark evaluation of 12 real-world threat scenarios spanning 1-hop to 4-hop reasoning depths, NexusCTI demonstrates:
1. **Top-1 Attribution Accuracy of 91.67%**, compared to 25.0% for Vector-only RAG and 41.67% for Standalone GNNs.
2. **Multi-Hop Reasoning Success Rate of 90.91%** across complex intermediary infrastructure chains (e.g., DNS resolutions, shared SSL certificates, stager droppers).
3. **Reduction in Hallucination and Misattribution to 8.33%** (down from 75.0% in naive vector RAG) via strict cross-modal graph-and-text validation.
4. **Verifiable Attribution Briefs** delivering dual-layer validation to SOC defenders: **The Graph Trail** (verifiable multi-hop structural chains) and **The Narrative Proof** (authoritative vendor citations).

---

## 1. Problem Statement & Motivation
Modern Advanced Persistent Threat (APT) groups frequently obfuscate their operational infrastructure through multi-tiered proxy networks, dynamic DNS providers, ephemeral VPS nodes, and living-off-the-land techniques (LOTL). When SOC analysts encounter an isolated indicator of compromise (IOC)—such as an unfamiliar IP address `185.225.17.42` or a passive DNS staging domain `freescanonline[.]com`—traditional automated analysis tools stumble:
- **Vector-Only RAG Bottleneck:** Text embeddings computed over vendor advisories fail when the isolated IOC is not explicitly present in the textual passage or is only mentioned in passing. Vector models lack topological awareness to traverse `IP -> Domain -> Primary C2 -> Malware -> Threat Actor`.
- **Standalone GNN Bottleneck:** While Relational GNNs can model graph connectivity, they lack the qualitative narratives required to disambiguate shared infrastructure, assess actor motivations, or provide verifiable evidence that human defenders can trust.
- **SOC Misattribution Risk:** Without dual-layer grounding, automated LLM attribution leads to hallucinations or misattributing routine commodity malware to high-tier state-sponsored actors.

### Research Question
> *Can a hybrid architecture combining structural GNN relational reasoning (mapping entity chains like $\text{IP} \rightarrow \text{Domain} \rightarrow \text{Malware}$ and $\text{CVE} \rightarrow \text{Attack Group} \rightarrow \text{Technique}$) with text-grounded RAG significantly improve the accuracy, explainability, and verification of cyber-threat attribution?*

---

## 2. Methodology & System Architecture

NexusCTI addresses this challenge through four interconnected layers:

### 2.1 Heterogeneous Threat Knowledge Graph (HTKG)
The threat intelligence ontology models five primary node types:
- **Threat Actor ($V_{\text{Actor}}$):** Known threat entities (e.g., APT28, APT29, Lazarus Group, Sandworm, FIN7, Volt Typhoon).
- **Malware ($V_{\text{Malware}}$):** Distinct toolsets (e.g., SUNBURST, Zebrocy, AppleJeus, NotPetya, Griffon).
- **Indicator ($V_{\text{IOC}}$):** Telemetry observables (IPv4, domains, file hashes, URLs).
- **TTP ($V_{\text{TTP}}$):** MITRE ATT&CK techniques (e.g., T1195.002, T1566.001, T1078, T1059).
- **Vulnerability ($V_{\text{CVE}}$):** Exploited CVEs (e.g., CVE-2021-44228, CVE-2020-1472, CVE-2023-27997).

Relationships include forward and reverse edges:
$$\mathcal{R} = \{\text{uses}, \text{executes}, \text{targets}, \text{controls}, \text{communicates\_with}, \text{exploits}, \text{maps\_to}, \text{resolves\_to}, \text{shares\_infra}\}$$

### 2.2 Relational Message Passing (HeteroThreatGNN)
We implement a Relational Graph Convolutional Network (RGCN) with multi-layer message passing. For node $i$ under relation $r \in \mathcal{R}$:

$$h_i^{(l+1)} = \sigma \left( W_{\text{self}}^{(l)} h_i^{(l)} + \sum_{r \in \mathcal{R}} \sum_{j \in \mathcal{N}_i^r} \frac{1}{c_{i,r}} W_r^{(l)} h_j^{(l)} \right)$$

where $c_{i,r} = |\mathcal{N}_i^r|$ is the in-degree normalization factor and $W_r^{(l)}$ parameterizes the relation-specific transformation.

### 2.3 Contextual Textual Retrieval (Hybrid RAG)
To combine precision keyword lookup for exact IOCs with semantic conceptual retrieval:
1. **Sparse Retrieval:** BM25Okapi inverted index preserving CTI tokens (`[.]`, dots, hyphens, CVE strings).
2. **Dense Retrieval:** Continuous semantic projections with cosine similarity over vendor threat reports.
3. **Reciprocal Rank Fusion (RRF):**
   $$RRF\_Score(d) = \frac{0.6}{60 + \text{rank}_{\text{BM25}}(d)} + \frac{0.4}{60 + \text{rank}_{\text{Dense}}(d)}$$

### 2.4 Synergistic Fusion & Cross-Validation
NexusCTI computes a unified attribution confidence score:
$$\text{Score}(A) = \alpha \cdot P_{\text{GNN}}(A) + \beta \cdot P_{\text{RAG}}(A) + \gamma \cdot C_{\text{score}}(A)$$
where $\alpha=0.45, \beta=0.35, \gamma=0.20$.  
$C_{\text{score}}(A)$ measures the topological consistency between the discovered structural Graph Trail and the textual citations. Contradictions or unsupported hops are penalized, reducing false positives.

---

## 3. Empirical Benchmark Evaluation

We designed 12 standardized evaluation scenarios spanning 4 difficulty tiers:
- **Tier 1 (Direct 1-Hop):** Direct tool identification or primary C2 domain observation.
- **Tier 2 (2-Hop Intermediary):** Stager binary hash to C2 pivot to threat actor.
- **Tier 3 (3-Hop Infrastructure Pivot):** Secondary IP address resolving to staging domain sharing SSL infrastructure with known C2.
- **Tier 4 (4-Hop Deep Relational Chain):** Obfuscated dark subnets, Living-off-the-land reverse proxy tunnels, and regional border gateways.

### 3.1 Comparative Benchmark Results

| Evaluation Metric | Naive Vector-only RAG | Standalone GNN Classifier | NexusCTI Hybrid (Proposed) | Relative Improvement |
|---|:---:|:---:|:---:|:---:|
| **Top-1 Attribution Accuracy** | 25.00% | 41.67% | **91.67%** | **+66.67% vs RAG** |
| **Top-3 Attribution Accuracy** | 66.67% | 100.00% | **100.00%** | **+33.33% vs RAG** |
| **Top-5 Attribution Accuracy** | 75.00% | 100.00% | **100.00%** | **+25.00% vs RAG** |
| **Multi-Hop Reasoning Success ( $\ge$ 2 Hops)** | 18.18% | 36.36% | **90.91%** | **+72.73% vs RAG** |
| **Hallucination / Misattribution Rate** | 75.00% | 58.33% | **8.33%** | **-66.67% Reduction** |
| **Mean Reciprocal Rank (MRR)** | 0.4514 | 0.6806 | **0.9583** | **+0.5069 vs RAG** |

### 3.2 Key Findings
1. **Why Naive Vector RAG Fails at Multi-Hop Pivots:** When presented with isolated secondary infrastructure like IP `185.225.17.42`, vector similarity retrieved unrelated reports containing general IP references or generic phishing descriptions, achieving only 18.18% multi-hop success.
2. **Why Standalone GNNs Fail Without Context:** The standalone GNN struggled when evaluating indicators with dense degree connectivity or when disambiguating shared commodity hosting, registering a 58.33% misattribution rate.
3. **Why Hybrid Synergy Succeeds:** The GNN traverses the structural topology to anchor candidate paths, while the Hybrid RAG pulls the authoritative textual corroboration. Cross-validation suppresses false hypotheses, yielding 91.67% Top-1 accuracy and 0.9583 MRR.

---

## 4. Case Study: SolarWinds Supply Chain Pivot (APT29)

### 4.1 Incident Scenario
- **Input Telemetry:** Isolated IP `185.225.17.42` observed in egress firewall logs with forged SSL certificate serials.
- **Ground Truth:** Attributed to APT29 (NOBELIUM / Cozy Bear).

### 4.2 NexusCTI Dual-Layer Output
#### Layer 1: The Graph Trail
$$\text{[Indicator] 185.225.17.42} \xrightarrow{\text{rev\_resolves\_to}} \text{[Indicator] freescanonline[.]com} \xrightarrow{\text{rev\_shares\_infra}} \text{[Indicator] avsvmcloud[.]com} \xrightarrow{\text{rev\_communicates\_with}} \text{[Malware] SUNBURST} \xrightarrow{\text{rev\_uses}} \text{[ThreatActor] APT29}$$

#### Layer 2: The Narrative Proof
> *"Upon establishing communication, the malware dynamically resolves intermediate IP addresses including 20.140.8.11 and shifts secondary staging to freescanonline[.]com, which resolves to 185.225.17.42. The threat actors leveraged memory-only dropper TEARDROP to inject custom Cobalt Strike BEACON payloads directly into memory..."*  
> — **Cybersecurity and Infrastructure Security Agency (CISA AA20-352A)**

---

## 5. Conclusion & SOC Operational Impact
NexusCTI demonstrates that combining structural GNN relational reasoning with text-grounded RAG transforms automated threat attribution from an opaque guessing game into a verifiable, dual-layer forensic process. By delivering both the structural path and authoritative narrative citations, SOC defenders can make confident, auditable escalation decisions in minutes rather than days.
