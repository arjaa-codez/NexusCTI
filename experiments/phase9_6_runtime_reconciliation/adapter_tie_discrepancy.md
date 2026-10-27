# NexusCTI Phase 9.6 — Adapter Tie Discrepancy & Sorting Investigation

**Document Version:** 1.0 (Retriever Tie-Breaking Forensic Analysis)  
**Date:** 2026-10-11  
**Project Root:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI`  
**Experiment Root:** `experiments/phase9_6_runtime_reconciliation/`  

---

## 1. Executive Summary

In Phase 9.5, the initial prototype of `ReadOnlyChromaAdapter` exhibited subtle rank discrepancies at Rank 3 for test cases T8 (5-way zero-similarity tie) and T10 (punctuation-noise query), despite identical Top-1 attributions and identical numerical similarity scores.

This document presents a comprehensive forensic investigation into:
1. The mathematical and algorithmic mechanisms producing the Rank 3 discrepancies.
2. The contrast between ChromaDB's native C++ HNSW graph beam traversal and Python linear-scan sorting.
3. How Phase 9.6 resolved the discrepancy by sorting on raw unrounded float32 dot-products.
4. Why Option C (Disposable Native Snapshot) remains superior to Option B by eliminating all custom tie-breaking assumptions from the evaluation protocol.

---

## 2. Forensic Analysis of Discrepancies

### 2.1 Test Case T8: The Five-Way Zero-Similarity Tie
- **Query:** `"threat actor not in registry"`, `gnn_top_group="NovelUnseenActor"`, `top_k=3`.
- **Search Context:** Because `"NovelUnseenActor"` is absent from metadata, the filter returns empty and the retriever falls back to an unrestricted search across all 7 corpus documents.
- **Top 2 Ranks (Identical across both engines):**
  - Rank 1: `Volt Typhoon` (`bundle--volt-typhoon-critical-infra-2024_0`), $\text{Sim} = 0.0820$
  - Rank 2: `Lazarus Group` (`bundle--lazarus-applejeus-crypto-2022_0`), $\text{Sim} = 0.0722$
- **Rank 3 Divergence in Phase 9.5 Prototype:**
  - *Native ChromaDB returned:* `Sandworm Team` with $\text{Sim} = 0.0$.
  - *Phase 9.5 Adapter returned:* `APT29` with $\text{Sim} = 0.0$.
- **Mathematical Cause:**
  All remaining 5 candidate documents in the corpus have cosine distances $\ge 1.000$ (negative dot products):
  ```
  1. Sandworm Team: dist = 1.004418 -> Sim = max(0.0, round(1 - 1.004418, 4)) = 0.0
  2. APT29 Chunk 1: dist = 1.020425 -> Sim = max(0.0, round(1 - 1.020425, 4)) = 0.0
  3. APT29 Chunk 0: dist = 1.030651 -> Sim = max(0.0, round(1 - 1.030651, 4)) = 0.0
  4. APT28:         dist = 1.033468 -> Sim = max(0.0, round(1 - 1.033468, 4)) = 0.0
  5. FIN7:          dist = 1.082507 -> Sim = max(0.0, round(1 - 1.082507, 4)) = 0.0
  ```
  Because the Phase 9.5 prototype mapped scores to `0.0` *before* sorting, all 5 documents had an identical sort key (`0.0`). Python's stable Timsort maintained the initial SQLite candidate sequence (which had APT29 first). In contrast, ChromaDB's HNSW index returned `Sandworm Team` based on raw distance ordering ($1.004418 < 1.020425$).

---

### 2.2 Test Case T10: Float Precision Truncation on Punctuation Noise
- **Query:** `"!@#$%^&*()_+~`{}[]:;'<>?,./"`, `gnn_top_group=None`, `top_k=3`.
- **Top 2 Ranks (Identical across both engines):**
  - Rank 1: `APT29` (`bundle--apt29-solarwinds-sunburst-2020_0`), $\text{Sim} = 0.0689$
  - Rank 2: `APT28` (`bundle--apt28-fancybear-zebrocy-2023_0`), $\text{Sim} = 0.0540$
- **Rank 3 Divergence in Phase 9.5 Prototype:**
  - *Native ChromaDB returned:* `Volt Typhoon` with $\text{Sim} = 0.0527$.
  - *Phase 9.5 Adapter returned:* `APT29` chunk 1 with $\text{Sim} = 0.0527$.
- **Mathematical Cause:**
  Inspection of raw unrounded distances reveals:
  ```
  Volt Typhoon:   dist = 0.947257 -> raw dot-product = 0.052743 -> round(..., 4) = 0.0527
  APT29 Chunk 1:  dist = 0.947288 -> raw dot-product = 0.052712 -> round(..., 4) = 0.0527
  ```
  The delta between the two documents was $\Delta = 0.000031$ ($3.1 \times 10^{-5}$). When rounded to 4 decimal places, **both candidates evaluated to exactly $0.0527$**. 
  Because ChromaDB sorts documents on raw unrounded float32 distances *prior* to rounding, `Volt Typhoon` ($0.052743$) strictly precedes `APT29` ($0.052712$). The Phase 9.5 prototype rounded *before* sorting, treating them as tied and breaking the tie in reverse order.

---

## 3. Resolution in Phase 9.6 Refined Adapter

In Phase 9.6, `ReadOnlyChromaAdapter` was refined to mirror ChromaDB's exact sorting pipeline:
```python
# Score by raw unrounded float32 dot product
scored = []
for r in filtered:
    raw_sim = float(np.dot(query_emb, r["vector"]))
    scored.append((raw_sim, r))

# Sort descending by RAW float32 similarity BEFORE rounding
scored.sort(key=lambda x: x[0], reverse=True)

# Truncate to top_k and THEN round to 4 decimals
results = []
for raw_sim, r in scored[:top_k]:
    sim_cos = max(0.0, round(raw_sim, 4))
    results.append({...})
```

### Empirical Result of Refined Sorting:
As recorded in `snapshot_reconciliation_telemetry.json`:
- **Top-1 Actor Matches:** **10 / 10 (100%)**
- **Full Rank & Score Matches:** **10 / 10 (100%)**
- Test T8 and Test T10 now match ChromaDB's ordered outputs **bit-identically**.

---

## 4. Assessment of HNSW vs Linear Tie Policies

While the refined adapter achieved 100% equivalence on the 10 development queries, adopting a custom adapter into the preregistered evaluation protocol carries scientific and operational risks:

1. **HNSW Graph Beam Non-Linearity:** In larger vector stores, HNSW approximate nearest neighbor search does not evaluate all candidate dot-products; it traverses a hierarchical graph via greedy beam search. In boundary conditions where two nodes have identical graph distances, traversal path depends on internal node insertion order and graph entry points.
2. **Deterministic Tie Policy Adoption:** A custom tie-breaking policy (such as secondary sorting by document ID or insertion index) can be formally defined, but adopting it represents a **modification of the frozen retrieval runtime**.
3. **Protocol Freezing Principle:** In a preregistered evaluation, altering the retrieval backend to resolve an infrastructure write-permission bug risks conflating infrastructure remediation with algorithmic tweaking.

---

## 5. Architectural Recommendation

To ensure the prospective evaluation remains 100% faithful to the locked scientific design:
- **Do not deploy a modified adapter for Phase 10.**
- **Select Option C (Native Disposable Snapshot).** Option C preserves the authentic compiled HNSW retrieval engine, executes the unmodified `ThreatRAGEngine` code, and guarantees 100% determinism without requiring custom tie-breaking rules.
- Retain the refined `ReadOnlyChromaAdapter` in project documentation as a validated technical fallback in the event that ephemeral snapshot creation is prevented by OS policy.
