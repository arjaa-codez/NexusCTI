# NexusCTI Ground-Truth Isolation & Access-Control Audit

**Document Version:** 1.0 (Blinding & Leakage Prevention Audit)  
**Date:** 2026-10-11  
**Project Root:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI`  
**Experiment Root:** `experiments/phase9_4_execution_safety/`  
**Manifest Path:** `experiments/phase9_benchmark_preparation_20261011_020400/candidate_campaign_manifest.csv`  
**Audit Telemetry:** `execution_safety_telemetry.json`

---

## 1. Executive Summary & Verification Matrix

This audit evaluated all possible pathways by which prospective test ground-truth labels could potentially leak into the inference process. Prospective ground-truth labels were **NEVER opened, loaded, or displayed** during this phase.

| Access Vector / Pathway | Audit Scope | Observed Result | Status |
| :--- | :--- | :--- | :--- |
| **Ground-Truth Storage Files** | Identify files containing labels | Confined to `candidate_campaign_manifest.csv` | **VERIFIED_ISOLATED** |
| **Direct Inference API Parameters** | Function signatures of active models | Zero label parameters accepted | **VERIFIED_ISOLATED** |
| **Metadata & Subgraph Leakage** | Node attributes in `hetero_graph.pt` | Zero candidate test nodes in graph | **VERIFIED_ISOLATED** |
| **Vector DB Document Metadata** | Metadata attributes in ChromaDB | Contains only 6 training CTI reports | **VERIFIED_ISOLATED** |
| **Cached Predictions & Run Logs** | Temp files / previous evaluation logs | Exactly 0 cached test predictions | **VERIFIED_ISOLATED** |
| **Filename & ID Leakage** | Opaque IDs (`cand_task_a_...`) | Synthetic opaque identifiers | **VERIFIED_ISOLATED** |

---

## 2. Identification of Ground-Truth Storage

The prospective evaluation dataset consists of $130$ total test campaigns ($100$ Task A closed-set and $30$ Task B open-set).
- **Physical Storage Location:**
  `experiments/phase9_benchmark_preparation_20261011_020400/candidate_campaign_manifest.csv`
- **Specific Label Columns:**
  `attributed_actor` (Ground-truth threat actor identifier, e.g., `actor_apt28`)  
  `actor_aliases` (Vendor naming synonyms, e.g., `Forest Blizzard / Fancy Bear / GRU 26165`)
- **Quarantine Safeguard:**
  The evaluation runner receives an input view containing only `candidate_id`, `campaign_id`, `campaign_name`, and `exact_supporting_passage`. Columns containing attribution answers are strictly omitted from the runner's input feed.

---

## 3. Active Inference Pipeline Parameter Inspection

The signatures of all active reasoning and retrieval classes in `cyber_attribution_engine/src/` were programmatically inspected using Python's `inspect` module:

```python
# 1. Relational Graph Convolutional Network Reasoner
AttributionReasoner.attribute_ioc(self, ioc: str)
# Arguments accepted: ['self', 'ioc']

# 2. Semantic Text Retrieval Engine
ThreatRAGEngine.hybrid_search(self, query: str, gnn_top_group: Optional[str] = None, top_k: int = 3)
# Arguments accepted: ['self', 'query', 'gnn_top_group', 'top_k']

# 3. Hybrid Synergistic Score Fusion Layer
HybridFusionEngine.compute_hybrid_attribution(self, ioc: str, alpha: float = 0.5, top_k_rag: int = 3, ollama_model: str = "llama3")
# Arguments accepted: ['self', 'ioc', 'alpha', 'top_k_rag', 'ollama_model']
```

### Parameter Isolation Proof:
- **Zero Label Parameters:** No model or retrieval class accepts a ground-truth label, target actor, or attribution hint as an argument.
- **Model Inputs:** The models operate exclusively on observable indicators (`ioc`) and sanitized text queries (`query`).

---

## 4. Subgraph, Metadata, and Corpus Leakage Verification

### 4.1 Knowledge Graph Topology Isolation
- The relational graph artifact (`cyber_attribution_engine/data/processed_graph/hetero_graph.pt`) contains nodes and edges compiled strictly from the 6 training reports.
- No test campaign nodes, target labels, or attribution edges exist within the frozen graph topology.

### 4.2 Retrieval Vector Store Isolation
- ChromaDB's vector store (`cyber_attribution_engine/data/chroma_db/chroma.sqlite3`) contains exactly $7$ document chunks derived from the $6$ training CTI reports.
- No prospective test reports or candidate attribution passages are indexed in ChromaDB.

### 4.3 Cache and Ephemeral Storage Check
- A recursive search of the workspace confirmed that **zero** prospective test prediction records (`frozen_test_predictions.csv`) exist in temporary, cached, or experiment directories.
- The inference process cannot draw from prior execution runs.

---

## 5. Access-Control Audit Conclusion

Technical blinding and access-control isolation are **VERIFIED AND SECURE**. The inference pipeline is completely isolated from prospective test labels, and the test labels remain securely quarantined prior to Phase 10 execution.
