# 🛡️ NexusCTI: Hybrid Multi-Modal Cyber-Threat Attribution Engine

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-orange.svg)](https://pytorch.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green.svg)](https://fastapi.tiangolo.com/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

> **Research Question:** *Can a hybrid architecture combining structural GNN relational reasoning with text-grounded RAG significantly improve the accuracy, explainability, and verification of cyber-threat attribution?*

---

## 🌟 Overview
**NexusCTI** bridges structured cyber telemetry and unstructured threat intelligence reports into a unified multi-modal attribution engine:
- **Structural Relational Modeling (GNN):** Heterogeneous Threat Knowledge Graph (HTKG) with Relational Graph Convolutional message passing (`HeteroThreatGNN`) to compute structural proximity and multi-hop infrastructure overlap.
- **Contextual Textual Retrieval (Hybrid RAG):** Dense-sparse hybrid search combining BM25 exact indicator lookup and continuous semantic embeddings merged via Reciprocal Rank Fusion (RRF).
- **Synergistic Fusion & Cross-Validation:** Fuses structural graph confidence with textual narrative evidence, performing cross-modal consistency validation to suppress hallucinations.
- **Verifiable Dual-Layer Attribution Briefs:** Delivers auditable threat intelligence reports featuring:
  - **The Graph Trail:** The precise structural chain (e.g. `Target IP -> Staging Domain -> Primary C2 -> Malware -> Threat Actor`).
  - **The Narrative Proof:** Direct, citable textual evidence pulled from authoritative research reports (CISA, Mandiant, Microsoft).

---

## 📊 Empirical Benchmark Results

Comparing **NexusCTI Hybrid** against **Naive Vector-only RAG** and **Standalone GNN Classifiers** across 12 standardized test scenarios (1-hop to 4-hop challenges):

| Evaluation Dimension | Naive Vector RAG | Standalone GNN | NexusCTI Hybrid | Relative Gain |
|---|:---:|:---:|:---:|:---:|
| **Top-1 Attribution Accuracy** | 25.0% | 41.7% | **91.7%** | **+66.7% vs RAG** |
| **Top-3 Attribution Accuracy** | 66.7% | 100.0% | **100.0%** | **+33.3% vs RAG** |
| **Top-5 Attribution Accuracy** | 75.0% | 100.0% | **100.0%** | **+25.0% vs RAG** |
| **Multi-Hop Reasoning ( $\ge$ 2 Hops)** | 18.2% | 36.4% | **90.9%** | **+72.7% vs RAG** |
| **Hallucination / Misattribution** | 75.0% | 58.3% | **8.3%** | **-66.7% Reduction** |
| **Mean Reciprocal Rank (MRR)** | 0.4514 | 0.6806 | **0.9583** | **+0.5069 vs RAG** |

---

## 🚀 Quick Start Guide

### 1. Prerequisites
- Python 3.10+ (PyTorch, NetworkX, FastAPI, Uvicorn, NumPy)
- Virtual environment is already pre-configured in `.venv/`

### 2. Launch the SOC Analyst Web Dashboard
Start the FastAPI server and interactive web UI:
```bash
.\.venv\Scripts\python.exe start_server.py
```
Open your browser at:
👉 **`http://localhost:8000`**

- **Interactive Incident Workbench:** Enter novel IOCs or select from 12 pre-loaded incident scenarios.
- **Knowledge Graph Explorer:** Pan, zoom, and explore 40+ threat entities with glowing active path highlighting.
- **Live Empirical Benchmarks:** Run and visualize live comparative metric charts.
- **Verifiable Attribution Brief:** Preview and export Markdown/JSON threat briefs.

---

### 3. Run the Empirical Benchmark Suite
Run the standardized 12-case comparative evaluation:
```bash
.\.venv\Scripts\python.exe run_benchmark.py
```
Outputs complete metric summaries and saves detailed records to `artifacts/benchmark_results.json`.

---

### 4. Run CLI Attribution Demo
Execute end-to-end attribution on any indicator (e.g. secondary SolarWinds IP pivot):
```bash
.\.venv\Scripts\python.exe run_demo.py "185.225.17.42"
```
Or investigate another scenario:
```bash
.\.venv\Scripts\python.exe run_demo.py "avsvmcloud.com"
.\.venv\Scripts\python.exe run_demo.py "027cc45097f8c2342332e5964cb68104d41fbe70e6b4ae0a30e60f34647d7826"
```
Saves reports to:
- `artifacts/attribution_brief.md`
- `artifacts/attribution_brief.json`

---

## 📁 Repository Structure

```
NexusCTI/
├── requirements.txt            # System dependencies
├── start_server.py             # Launches FastAPI Web Dashboard (port 8000)
├── run_benchmark.py            # Executes live 12-case empirical evaluation
├── run_demo.py                 # CLI demonstration for arbitrary IOC attribution
├── ARCHITECTURE.md             # Detailed engineering & mathematical blueprint
├── RESEARCH_REPORT.md          # Comprehensive academic research report
├── nexuscti/
│   ├── config.py               # Hyperparameters, paths, thresholds
│   ├── service.py              # Central coordinator & singleton service
│   ├── data/
│   │   ├── ontology.py         # STIX 2.1 & MITRE ATT&CK schema definitions
│   │   ├── knowledge_base.py   # Curated HTKG entities and multi-hop edges
│   │   └── corpus.py           # Authoritative vendor reports (CISA, Mandiant)
│   ├── gnn/
│   │   ├── graph_builder.py    # NetworkX & PyTorch tensor constructor
│   │   ├── model.py            # HeteroThreatGNN relational message passing
│   │   ├── trainer.py          # Representation learning & topological inference
│   │   └── trail_extractor.py  # Multi-hop Dijkstra path tracer
│   ├── rag/
│   │   ├── chunker.py          # Technical narrative sliding window chunker
│   │   ├── bm25_retriever.py   # CTI-tailored sparse BM25 retriever
│   │   ├── dense_retriever.py  # Continuous semantic vector retriever
│   │   └── hybrid_retriever.py # Reciprocal Rank Fusion (RRF)
│   ├── fusion/
│   │   ├── engine.py           # Synergistic fusion & consistency matrix
│   │   └── report_generator.py # Dual-layer Markdown & JSON report synthesis
│   └── eval/
│       ├── benchmark_cases.py  # 12 standardized 1-hop to 4-hop challenge cases
│       ├── baselines.py        # Naive Vector RAG & Standalone GNN baselines
│       └── evaluator.py        # Top-1/Top-5 accuracy, multi-hop depth, MRR
└── web/
    ├── index.html              # Cyber-defense SOC dashboard UI
    ├── style.css               # Futuristic glassmorphic dark theme
    └── app.js                  # Workbench, interactive canvas, live benchmarks
```

---

## 📡 REST API Reference

The FastAPI backend exposes the following REST endpoints:

- `POST /api/analyze`  
  **Payload:** `{"query": "185.225.17.42", "ioc_override": null}`  
  **Returns:** Full multi-modal analysis, candidate confidence matrix, graph trail hops, and narrative proofs.

- `GET /api/graph`  
  **Returns:** Full knowledge graph topology (nodes, edges, node degrees, entity types).

- `GET /api/cases`  
  **Returns:** The 12 benchmark test cases with ground truth labels and expected hop counts.

- `GET /api/benchmark`  
  **Returns:** Comparative benchmark results across Vector RAG, Standalone GNN, and NexusCTI Hybrid.

- `GET /docs`  
  Interactive Swagger UI documentation.

---

## 🛡️ License
Licensed under the Apache License 2.0.
