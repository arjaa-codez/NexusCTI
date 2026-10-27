# Repository Inventory & System Architecture Map

**Experiment:** `scientific_audit_20261010_223000`  
**Date:** October 10, 2026  
**Auditor:** Automated Scientific Integrity & Benchmark Audit Agent  
**Repository Root:** `c:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI`

---

## 1. Dual-Architecture Overview

The repository hosts two parallel, complementary implementations of the Cyber-Threat Attribution Engine:

1. **`nexuscti/` (Core Research Engine)**:
   - Python library implementing the multi-hop Heterogeneous Threat Knowledge Graph (`HeteroThreatGNN`), Hybrid RAG (BM25Okapi + continuous semantic projections with subword hash n-grams), Reciprocal Rank Fusion, Synergistic Fusion Engine with Cross-Validation, and the 12-case standardized benchmark harness.
   - Entry points: `run_benchmark.py`, `run_demo.py`, `start_server.py`, `test_pipeline.py`.

2. **`cyber_attribution_engine/` (Capstone Implementation Package)**:
   - Self-contained implementation using PyTorch Geometric (`HeteroData`), Relational Graph Convolutional Networks with basis-decomposition (`ThreatRGCN`), persistent ChromaDB vector storage with `sentence-transformers/all-MiniLM-L6-v2`, FastAPI endpoints, and Streamlit dashboard.
   - Entry points: `cyber_attribution_engine/verify_system.py`, `cyber_attribution_engine/src/api.py`, `cyber_attribution_engine/ui/app.py`.

---

## 2. Inventory of Relevant Files & Components

### 2.1 Benchmark Cases & Evaluation
| File Path | Component | Description & Role |
| :--- | :--- | :--- |
| [`nexuscti/eval/benchmark_cases.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/nexuscti/eval/benchmark_cases.py) | Benchmark Dataset | Defines 12 standardized CTI test scenarios spanning 1-hop to 4-hop multi-hop reasoning with ground-truth actor IDs. |
| [`nexuscti/eval/baselines.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/nexuscti/eval/baselines.py) | Baselines | Implements `NaiveVectorRAGBaseline` (pure dense text retrieval) and `StandaloneGNNBaseline` (pure structural topological prediction). |
| [`nexuscti/eval/evaluator.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/nexuscti/eval/evaluator.py) | Evaluation Engine | Implements `AttributionEvaluator`, calculating Top-1, Top-3, Top-5 accuracy, multi-hop success rate, hallucination rate, and Mean Reciprocal Rank (MRR). |
| [`run_benchmark.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/run_benchmark.py) | Benchmark Runner | CLI script that initializes the service, runs `AttributionEvaluator`, prints Markdown summary, and saves JSON output to `artifacts/benchmark_results.json`. |
| [`artifacts/benchmark_results.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/artifacts/benchmark_results.json) | Baseline Artifact | Pre-existing recorded benchmark results across all 12 cases. |

### 2.2 Knowledge Graph & GNN Relational Reasoning
| File Path | Component | Description & Role |
| :--- | :--- | :--- |
| [`nexuscti/data/ontology.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/nexuscti/data/ontology.py) | Ontology Schema | Defines STIX 2.1 & MITRE ATT&CK node types (`ThreatActor`, `Malware`, `Indicator`, `TTP`, `Vulnerability`) and edge types. |
| [`nexuscti/data/knowledge_base.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/nexuscti/data/knowledge_base.py) | Knowledge Base | Curated entities and multi-hop edges connecting threat actors, malware, C2 IPs, staging domains, hashes, CVEs, and TTPs. |
| [`nexuscti/gnn/graph_builder.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/nexuscti/gnn/graph_builder.py) | Graph Constructor | Builds `NetworkX` directed graph, node index maps, relation index maps, and initial PyTorch node feature tensors. |
| [`nexuscti/gnn/model.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/nexuscti/gnn/model.py) | GNN Architecture | `HeteroThreatGNN`: 2-layer Relational Graph Convolutional Network with actor classification head and LeakyReLU activations. |
| [`nexuscti/gnn/trainer.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/nexuscti/gnn/trainer.py) | GNN Training & Inference | Derives supervision labels from 3-hop shortest-path reachability; trains using Cross-Entropy loss over 120 epochs; computes cached node embeddings. |
| [`nexuscti/gnn/trail_extractor.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/nexuscti/gnn/trail_extractor.py) | Graph Trail Extractor | Multi-hop shortest path search using Dijkstra algorithm; generates verifiable provenance chains. |
| [`cyber_attribution_engine/src/graph_builder.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/cyber_attribution_engine/src/graph_builder.py) | PyG Graph Builder | Ingests raw STIX JSON, official MITRE ATT&CK STIX 2.1, and CISA KEV JSON into PyTorch Geometric `HeteroData`. |
| [`cyber_attribution_engine/src/gnn_model.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/cyber_attribution_engine/src/gnn_model.py) | RGCN & Contrastive Loss | Implements RGCN with basis decomposition ($W_r = \sum a_{r,b} V_b$), incoming degree normalization ($c_{v,r}$), contrastive link prediction loss, and `AttributionReasoner`. |

### 2.3 Retrieval & Vector Database
| File Path | Component | Description & Role |
| :--- | :--- | :--- |
| [`nexuscti/data/corpus.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/nexuscti/data/corpus.py) | Textual Corpus | Collection of 6 authoritative vendor threat reports (CISA AA20-352A, Mandiant, Microsoft) with metadata, IOCs, CVEs, and TTPs. |
| [`nexuscti/rag/chunker.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/nexuscti/rag/chunker.py) | Text Chunker | Technical narrative sliding window chunker preserving IOC tokens. |
| [`nexuscti/rag/bm25_retriever.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/nexuscti/rag/bm25_retriever.py) | Sparse Retrieval | BM25Okapi retriever preserving cyber indicators (`[.]`, dots, hyphens, hashes, CVEs). |
| [`nexuscti/rag/dense_retriever.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/nexuscti/rag/dense_retriever.py) | Dense Retrieval | Continuous semantic representations with subword character tri-gram hash embeddings and LayerNorm cosine similarity. |
| [`nexuscti/rag/hybrid_retriever.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/nexuscti/rag/hybrid_retriever.py) | Reciprocal Rank Fusion | Merges BM25 and Dense rankings via Reciprocal Rank Fusion (RRF with weights 0.6 / 0.4, $k=60$). |
| [`cyber_attribution_engine/src/rag_engine.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/cyber_attribution_engine/src/rag_engine.py) | ChromaDB Vector Store | Persistent ChromaDB collection indexed with `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional dense vectors). |

### 2.4 Score Fusion & Evidence Synthesis
| File Path | Component | Description & Role |
| :--- | :--- | :--- |
| [`nexuscti/fusion/engine.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/nexuscti/fusion/engine.py) | Synergistic Fusion | `SynergisticFusionEngine`: $\text{Score} = 0.45 \cdot P_{\text{GNN}} + 0.35 \cdot P_{\text{RAG}} + 0.20 \cdot C_{\text{score}}$, with cross-modal consistency matrix. |
| [`cyber_attribution_engine/src/fusion_layer.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/cyber_attribution_engine/src/fusion_layer.py) | Hybrid Score Merger | Implements Formula 2.C: $S(A_i \mid \text{IOC}) = \alpha \cdot \text{Softmax}(z_{\text{IOC}}^T z_{A_i}) + (1-\alpha) \cdot \max \text{Sim}_{\cos}(E_q, E_d)$. |

---

## 3. The 12 Standardized Benchmark Cases

| Case ID | Name | Category | Anchor IOC | Ground Truth Actor | Expected Hops |
| :--- | :--- | :--- | :--- | :--- | :---: |
| `test_case_01` | APT29 SUNBURST Direct Backdoor Detection | 1-hop direct | `avsvmcloud[.]com` | `actor_apt29` (APT29) | 2 |
| `test_case_02` | Sandworm Industroyer Power Grid Payload | 1-hop direct | `Industroyer (CrashOverride)` | `actor_sandworm` (Sandworm Team) | 1 |
| `test_case_03` | Lazarus AppleJeus Trojanized Installer | 1-hop direct | `secure-crypto-wallet[.]org` | `actor_lazarus` (Lazarus Group) | 2 |
| `test_case_04` | APT28 Zebrocy Binary Hash to C2 Pivot | 2-hop stager | `a3d9e84b72110cfa...` | `actor_apt28` (APT28) | 2 |
| `test_case_05` | FIN7 Griffon Stager & Zerologon Exploitation | 2-hop stager | `f441c21d84812a10...` | `actor_fin7` (FIN7) | 2 |
| `test_case_06` | Sandworm NotPetya Wiper Binary Artifact | 2-hop stager | `027cc45097f8c234...` | `actor_sandworm` (Sandworm Team) | 2 |
| `test_case_07` | APT29 Multi-Hop Secondary Infrastructure Pivot | 3-hop infra pivot | `185.225.17.42` | `actor_apt29` (APT29) | 3 |
| `test_case_08` | APT28 Shared DNS Resolution Pivot | 3-hop infra pivot | `mail-update-service[.]net` | `actor_apt28` (APT28) | 3 |
| `test_case_09` | Volt Typhoon SOHO Mesh Egress Pivot | 3-hop infra pivot | `203.0.113.88` | `actor_volt_typhoon` (Volt Typhoon) | 3 |
| `test_case_10` | Sandworm Obfuscated Subnet Pivot to BlackEnergy | 4-hop deep chain | `91.242.217.5` | `actor_sandworm` (Sandworm Team) | 4 |
| `test_case_11` | Lazarus North Korean AS131279 Gateway Correlation | 4-hop deep chain | `175.45.176.8` | `actor_lazarus` (Lazarus Group) | 3 |
| `test_case_12` | FIN7 Hosting Staging Infrastructure Pivot | 4-hop deep chain | `193.106.191.4` | `actor_fin7` (FIN7) | 3 |
