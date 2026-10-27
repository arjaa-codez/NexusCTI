# Controlled Ablation Experiment Protocol

**Experiment ID:** `scientific_audit_20261010_223000`  
**Date:** October 10, 2026  
**Evaluation Dataset:** 12 Standardized Multi-Hop Benchmark Cases (`nexuscti/eval/benchmark_cases.py`)  
**Evaluation Scope:** Closed-world APT attribution across 6 primary threat actors (`APT28`, `APT29`, `Lazarus Group`, `Sandworm Team`, `FIN7`, `Volt Typhoon`).

---

## 1. Experimental Objectives

To isolate and quantify the specific performance contributions of each architectural module in **NexusCTI**:
1. Does multi-hop graph structure compensate for the known failure mode of vector retrieval on isolated indicators?
2. Does a learned Relational Graph Convolutional Network (R-GCN) outperform a non-neural shortest-path graph baseline?
3. Does synergistic cross-validation fusion (GNN + RAG + consistency validation) outperform simple heuristic combinations?

---

## 2. The Five Evaluated Configurations

| Configuration | Designation | Active Modules | Inactive / Bypassed Modules | Mathematical Scoring Formulation |
| :--- | :--- | :--- | :--- | :--- |
| **Config A** | **Vector-only RAG** | Dense text retriever (`SemanticTextEncoder` / `all-MiniLM-L6-v2`) | Graph topology, GNN forward pass, cross-validation | $S_A(a) = \sum_{c \in \text{chunks}(a)} \max(0, \text{Sim}_{\cos}(E_q, E_c))$ |
| **Config B** | **Graph-only (Topological)** | Symbolic NetworkX graph traversal (Dijkstra shortest path) | Vector store, text embeddings, R-GCN neural weights | $S_B(a) = \frac{1.0}{1.0 + d(u, a)}$ where $d$ is shortest hop distance |
| **Config C** | **GNN-only (Neural)** | Trained `HeteroThreatGNN` / `ThreatRGCN` relational representations | Text corpus, vector retriever, BM25 keyword index | $S_C(a) = \text{Softmax}(z_u^T z_a)$ via structural message passing |
| **Config D** | **Graph + RAG (Non-Neural)** | Symbolic graph distance $S_B(a)$ + Text retrieval score $S_A(a)$ | Learned R-GCN neural embeddings, consistency matrix | $S_D(a) = 0.5 \cdot S_B(a) + 0.5 \cdot S_A(a)$ |
| **Config E** | **Full Hybrid (NexusCTI)** | GNN neural structural score $S_C(a)$ + RAG hybrid text score $S_A(a)$ + Cross-Validation $C(a)$ | None (Complete unified framework) | $S_E(a) = 0.45 \cdot S_C(a) + 0.35 \cdot S_A(a) + 0.20 \cdot C_{\text{score}}(a)$ |

---

## 3. Strict Verification of Component Isolation

To prevent bleed-through between configurations:
- **Config A Execution Trace:** Zero NetworkX calls; zero PyTorch tensor operations on graph adjacency matrices.
- **Config B Execution Trace:** Zero text chunks accessed; zero embedding lookups; deterministic distance calculation.
- **Config C Execution Trace:** Operates solely on tensor node features and adjacency lists; zero text queries executed.
- **Config D Execution Trace:** Uses only scalar topological graph distance and scalar text similarity; no neural GNN forward pass is invoked.
- **Config E Execution Trace:** Complete pipeline executing message passing, text retrieval, Dijkstra trail extraction, and topological-textual cross-validation.

---

## 4. Evaluation Metrics & Standards

- **Top-1 Accuracy:** $\frac{\sum_{i=1}^N \mathbb{I}(\text{rank}_i = 1)}{N} \times 100\%$
- **Top-3 Accuracy:** $\frac{\sum_{i=1}^N \mathbb{I}(\text{rank}_i \le 3)}{N} \times 100\%$
- **Mean Reciprocal Rank (MRR):** $\frac{1}{N} \sum_{i=1}^N \frac{1}{\text{rank}_i}$ (where $\text{rank}_i > 10 \implies 0$)
- **Multi-Hop Success Rate:** Accuracy on cases requiring $\ge 2$ intermediate hops (11 cases total).
- **Hallucination / Misattribution Rate:** Percentage of test cases where the top candidate is incorrect.
- **Sample Size Context:** $N = 12$ cases. Each case represents $\approx 8.33\%$ accuracy.
