# Phase 9.9 — Active Production Runtime Code Trace

**Audit Phase:** NexusCTI Phase 9.9 — Final Integrity Reconciliation and Protocol Approval Preparation  
**Timestamp:** 2026-10-11T23:24:00+05:30  
**Project Root:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\cyber_attribution_engine`  
**Scope:** Verification of End-to-End Production Retrieval Pipeline and Phase 10 Harness Binding  

---

## 1. Executive Summary

Task 3 of Phase 9.9 requires tracing the active production inference path from the public API entrypoint down to the ChromaDB storage layer. The objective is to verify that the prospective evaluation will invoke the **authentic production retrieval logic**, rather than an obsolete test stub, an unverified mock, or an alternate database path.

This code audit confirms:
1. **Unbroken Production Chain:** The inference path is continuous from [`cyber_attribution_engine/src/api.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/cyber_attribution_engine/src/api.py) -> [`cyber_attribution_engine/src/fusion_layer.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/cyber_attribution_engine/src/fusion_layer.py) -> [`cyber_attribution_engine/src/rag_engine.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/cyber_attribution_engine/src/rag_engine.py) -> `chromadb.PersistentClient`.
2. **Identical Retrieval Execution:** The prospective evaluation harness will invoke the identical `ThreatRAGEngine.hybrid_search` and `HybridFusionEngine.compute_hybrid_attribution` methods used in production.
3. **No Alternate Retrieval Modules:** The codebase contains no shadow vector engines or competing RAG implementations. The evaluated model is the active production model.

---

## 2. Step-by-Step Production Code Trace

```
[HTTP Request: POST /attribute or POST /api/analyze]
                        │
                        ▼
    ┌─────────────────────────────────────────────────────────┐
    │ 1. Application Entrypoint:                              │
    │    cyber_attribution_engine/src/api.py                  │
    │    Function: attribute_ioc(req: AttributionRequest)     │
    │    Line: 154-167                                        │
    └─────────────────────────────────────────────────────────┘
                        │
                        ▼ Calls engine.compute_hybrid_attribution()
    ┌─────────────────────────────────────────────────────────┐
    │ 2. Hybrid Score Fusion Layer:                           │
    │    cyber_attribution_engine/src/fusion_layer.py         │
    │    Class: HybridFusionEngine                            │
    │    Method: compute_hybrid_attribution(ioc, alpha, ...)  │
    │    Line: 40-60                                          │
    └─────────────────────────────────────────────────────────┘
                        │
                        ▼ Calls self.rag.hybrid_search()
    ┌─────────────────────────────────────────────────────────┐
    │ 3. Semantic Vector Retrieval Layer:                     │
    │    cyber_attribution_engine/src/rag_engine.py           │
    │    Class: ThreatRAGEngine                               │
    │    Method: hybrid_search(query, gnn_top_group, top_k)  │
    │    Line: 147-202                                        │
    └─────────────────────────────────────────────────────────┘
                        │
                        ▼ Executes Dense Embedding & Filtered Query
    ┌─────────────────────────────────────────────────────────┐
    │ 4. Embedding Model:                                     │
    │    cyber_attribution_engine/src/rag_engine.py           │
    │    Class: MiniLMEmbeddingFunction                       │
    │    Model: sentence-transformers/all-MiniLM-L6-v2 (384d) │
    │    Line: 19-60                                          │
    └─────────────────────────────────────────────────────────┘
                        │
                        ▼ Queries collection via self.collection.query()
    ┌─────────────────────────────────────────────────────────┐
    │ 5. ChromaDB Native Vector Store:                        │
    │    chromadb.PersistentClient                            │
    │    Collection: "cti_threat_reports" (UUID cd6345d4...)  │
    │    Underlying Directory: persist_directory              │
    └─────────────────────────────────────────────────────────┘
```

---

## 3. Function-Level Source Code Evidence

### 3.1 Application Entrypoint (`api.py`)
In [`cyber_attribution_engine/src/api.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/cyber_attribution_engine/src/api.py), lines 154–167:
```python
@app.post("/attribute", response_model=AttributionResponse)
def attribute_ioc(req: AttributionRequest):
    """PDF Specification endpoint executing GNN traversal and RAG retrieval pipeline."""
    if not req.ioc.strip():
        raise HTTPException(status_code=400, detail="IOC string must not be empty.")

    engine = get_engines()
    try:
        result = engine.compute_hybrid_attribution(
            ioc=req.ioc.strip(),
            alpha=req.alpha,
            top_k_rag=req.top_k_rag,
            ollama_model=req.ollama_model,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Attribution processing error: {str(e)}")
```

### 3.2 Fusion Layer (`fusion_layer.py`)
In [`cyber_attribution_engine/src/fusion_layer.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/cyber_attribution_engine/src/fusion_layer.py), lines 48–60:
```python
        # Step 1: Structural GNN Inference
        gnn_result = self.gnn.attribute_ioc(ioc)
        gnn_top_group = gnn_result.get("top_group", "Unknown")
        gnn_scores = gnn_result.get("group_scores", {})
        traversal_path = gnn_result.get("traversal_path", [])

        # Step 2: Semantic Vector RAG Retrieval
        rag_query = f"{ioc} malware exploit command control infrastructure campaign threat actor"
        retrieved_chunks = self.rag.hybrid_search(
            query=rag_query,
            gnn_top_group=gnn_top_group if gnn_result.get("matched") else None,
            top_k=top_k_rag,
        )
```

### 3.3 RAG Retrieval Layer (`rag_engine.py`)
In [`cyber_attribution_engine/src/rag_engine.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/cyber_attribution_engine/src/rag_engine.py), lines 157–181:
```python
        query_emb = self.embedding_fn.embed_query(query)

        where_filter = None
        if gnn_top_group and gnn_top_group != "Unknown":
            where_filter = {"threat_actor": gnn_top_group}

        results = None
        if where_filter:
            try:
                results = self.collection.query(
                    query_embeddings=[query_emb],
                    n_results=top_k,
                    where=where_filter,
                )
            except Exception as e:
                print(f"[RAG Engine] Filtered query error: {e}, falling back to unrestricted search")
                results = None

        if not results or not results["ids"] or len(results["ids"][0]) == 0:
            results = self.collection.query(
                query_embeddings=[query_emb],
                n_results=top_k,
            )
```

---

## 4. Evaluation Harness Parameter Injection Protocol

In production, `ThreatRAGEngine` defaults to:
```python
persist_directory = "cyber_attribution_engine/data/chroma_db"
```

Under **Option C (Disposable Runtime Snapshot)**, the Phase 10 evaluation harness injects the path of the validated disposable snapshot:
```python
# Phase 10 Evaluation Harness Binding
snapshot_dir = snapshot_manager.create_snapshot(scratch_path)
eval_rag = ThreatRAGEngine(persist_directory=str(snapshot_dir))
eval_engine = HybridFusionEngine(reasoner=prod_reasoner, rag_engine=eval_rag)
```

### Verifications:
1. **Zero Logic Divergence:** The evaluation harness does not reimplement cosine distance, tie-breaking, or metadata filtering. It calls the exact same `ThreatRAGEngine.hybrid_search` production implementation.
2. **Zero Storage Contamination:** Because `persist_directory` points to `scratch/...`, all SQLite connection metadata writes and HNSW buffer updates take place in the disposable directory.
3. **Master Immunity:** The authoritative master directory (`cyber_attribution_engine/data/chroma_db/`) is never opened by the evaluation process.

---

## 5. Audit Verdict

| Verification Item | Requirement | Code Finding | Status |
| :--- | :--- | :--- | :---: |
| Entrypoint Linkage | `api.py` links to `fusion_layer.py` | Line 161 verified | **PASSED** |
| Fusion Linkage | `fusion_layer.py` links to `rag_engine.py` | Line 56 verified | **PASSED** |
| Retrieval Implementation | Uses `ThreatRAGEngine.hybrid_search` | Lines 147–202 verified | **PASSED** |
| ChromaDB Binding | Uses native `PersistentClient` | Line 73 verified | **PASSED** |
| Path Injection Support | Accepts dynamic `persist_directory` | Line 66 verified | **PASSED** |
| Obsolete Paths Check | No shadow vector engines found | 0 alternate paths | **PASSED** |

**Conclusion:** The active runtime inference path is verified, continuous, and identical to the evaluated pipeline.
