# Phase 9.8 — Retrieval Equivalence Reproduction Report

**Audit Phase:** NexusCTI Phase 9.8 — Master Hash Chain of Custody and Snapshot Consistency  
**Timestamp:** 2026-10-11T23:07:00+05:30  
**Project Root:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI`  
**Execution Target:** Reproduction of Development Fixtures T1–T10 through Active `ThreatRAGEngine` Retrieval Path  
**Supporting Telemetry:** [`phase9_8_artifact_manifest.json`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_8_evidence_reconciliation/phase9_8_artifact_manifest.json)  

---

## 1. Executive Summary

Task 3 of Phase 9.8 mandates the complete reproduction of the 10 development query evaluations (T1–T10) comparing the **Option C Disposable Native Snapshot Runtime** against the frozen retrieval baseline.

This audit independently verified:
1. **Invocation of the Actual Active Retrieval Path:** The evaluation was executed directly via `ThreatRAGEngine.hybrid_search(query, gnn_top_group, top_k)` in `cyber_attribution_engine/src/rag_engine.py`, rather than through lower-level isolated ChromaDB client calls.
2. **Exact Retrieval Equivalence:** Across all 10 queries, Top-1 threat actors, ordered candidate document IDs, raw unrounded cosine distances, and displayed similarity scores matched the frozen baseline **100% identically**.
3. **Equivalence Classification Rigor:** In accordance with audit standards, we explicitly separate binary pre-query identity, canonical-content equivalence, and empirical retrieval equivalence on the tested queries.

---

## 2. Technical Environment & Retrieval Pipeline Provenance

- **Retrieval Engine Module:** [`cyber_attribution_engine/src/rag_engine.py`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/cyber_attribution_engine/src/rag_engine.py)
- **Active Method Invoked:** `ThreatRAGEngine.hybrid_search(query: str, gnn_top_group: Optional[str], top_k: int)`
- **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional dense semantic embeddings)
- **Collection Name:** `cti_threat_reports`
- **Collection UUID:** `cd6345d4-cc6a-4d4d-b527-5a34fd4de2ee`
- **Collection Document Count:** 7 canonical CTI threat report chunks
- **Index Configuration:** HNSW segment `3962f896-273d-4039-b97e-d0aa4e6d29ed`, Space: `cosine`, Dimension: 384
- **Distance Metric:** Cosine Distance $d \in [0, 2]$
- **Score Formulation:** $\text{Sim}_{\cos} = \max(0.0, \text{round}(1.0 - d, 4))$

---

## 3. Query-by-Query Forensic Reproduction Table (T1–T10)

All 10 development queries were executed against a freshly validated disposable snapshot managed by `ConsistentSnapshotManager`:

| Query ID | Query String | GNN Filter | Top-1 Threat Actor | Ordered Candidate IDs | Raw Unrounded Distances | Displayed Similarity | Equivalence Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :---: |
| **T1** | `SolarWinds backdoor SUNBURST 185.225.17.42` | `APT29` | **APT29** | `['apt29_apt29_cisa_1', 'apt29_apt29_cisa_0']` | `[1.000958, 1.016318]` | `[0.0, 0.0]` | **EXACT MATCH** |
| **T2** | `Sandworm wiper high voltage substation Industroyer2` | `Sandworm Team` | **Sandworm Team** | `['sandworm_team_sandworm_cisa_0']` | `[0.967824]` | `[0.0322]` | **EXACT MATCH** |
| **T3** | `AppleJeus cryptocurrency exchange trojanized application` | `Lazarus Group` | **Lazarus Group** | `['lazarus_group_lazarus_cisa_0']` | `[1.012413]` | `[0.0]` | **EXACT MATCH** |
| **T4** | `Volt Typhoon living off the land wmic powershell cve` | `Volt Typhoon` | **Volt Typhoon** | `['volt_typhoon_volt_typhoon_cisa_0']` | `[0.925740]` | `[0.0743]` | **EXACT MATCH** |
| **T5** | `FIN7 financial POS malware Carbanak cash out` | `FIN7` | **FIN7** | `['fin7_mandiant_fin7_0']` | `[1.033816]` | `[0.0]` | **EXACT MATCH** |
| **T6** | `APT28 Fancy Bear Zebrocy spearphishing credential harvesting` | `APT28` | **APT28** | `['apt28_apt28_cisa_0']` | `[1.049346]` | `[0.0]` | **EXACT MATCH** |
| **T7** | `generic ransomware c2 beaconing payload` | `Unknown` (None) | **Volt Typhoon** | `['volt_typhoon_volt_typhoon_cisa_0', 'lazarus_group_lazarus_cisa_0', 'apt29_apt29_cisa_0']` | `[0.891478, 0.910602, 0.931700]` | `[0.1085, 0.0894, 0.0683]` | **EXACT MATCH** |
| **T8** | `threat actor not in registry` | `NovelUnseenActor` | **Volt Typhoon** | `['volt_typhoon_volt_typhoon_cisa_0', 'lazarus_group_lazarus_cisa_0', 'sandworm_team_sandworm_cisa_0']` | `[0.918017, 0.927799, 1.004418]` | `[0.0820, 0.0722, 0.0]` | **EXACT MATCH** |
| **T9** | `""` (Empty Query) | `APT28` | **APT28** | `['apt28_apt28_cisa_0']` | `[0.971588]` | `[0.0284]` | **EXACT MATCH** |
| **T10** | `!@#$%^&*()_+~` | `None` | **APT29** | `['apt29_apt29_cisa_0', 'apt28_apt28_cisa_0', 'volt_typhoon_volt_typhoon_cisa_0']` | `[0.931082, 0.945958, 0.947257]` | `[0.0689, 0.0540, 0.0527]` | **EXACT MATCH** |

---

## 4. Analysis of Tie-Breaking and Near-Tie Behavior

In Phase 9.5, the custom SQL adapter exhibited a rank discrepancy on queries with tied cosine distances (e.g., $d \ge 1.0$, resulting in similarity $0.0$). The custom adapter enforced `ORDER BY id ASC`, placing `apt29_apt29_cisa_0` ahead of `apt29_apt29_cisa_1`.

In this reproduction:
- In Query T1 (`SolarWinds backdoor SUNBURST`), both candidates yield similarity `0.0`.
- The native ChromaDB HNSW runtime ordered `apt29_apt29_cisa_1` ahead of `apt29_apt29_cisa_0` based on HNSW graph traversal.
- The **Option C Native Snapshot reproduced this ordering identically** with zero divergence from the frozen baseline.

---

## 5. Strict Categorization of Equivalence Claims

To avoid overstating guarantees beyond what was empirically audited, the evaluation boundaries are categorized as follows:

| Equivalence Level | Definition | Scope Evaluated | Audit Finding |
| :--- | :--- | :--- | :---: |
| **1. Binary Identity Before Run** | Bit-for-bit SHA-256 match between master and freshly cloned snapshot files prior to opening connection. | All 5 files (`chroma.sqlite3`, `header.bin`, `length.bin`, `data_level0.bin`, `link_lists.bin`) | **CONFIRMED (100% Bitwise Identical)** |
| **2. Canonical-Content Equivalence** | Cryptographic hash over all logical SQLite tables (`collections`, `embeddings`, `embedding_metadata`). | All rows and metadata attributes across 7 CTI reports | **CONFIRMED (Hash: `668d0776...` Invariant)** |
| **3. Retrieval Equivalence on Tested Suite** | Exact agreement on ordered document IDs, ranks, raw distances, displayed scores, and tie-breaking. | Development suite T1 through T10 | **CONFIRMED (10/10 Queries 100% Identical)** |
| **4. General Equivalence** | Universal mathematical guarantee for arbitrary unseen future queries across all possible parameter combinations. | Out of scope for empirical testing | **NOT CLAIMED (Properly restricted to audited cases)** |

---

## 6. Audit Verdict

| Criterion | Standard | Observed Result | Status |
| :--- | :--- | :--- | :---: |
| Invocation of Active RAG Path | Invokes `ThreatRAGEngine.hybrid_search` directly | Active method verified | **PASSED** |
| Top-1 Threat Actor Match | 100% agreement across T1–T10 | 10/10 (100.0%) | **PASSED** |
| Candidate ID Rank Order | Exact match on all returned document IDs | 10/10 (100.0%) | **PASSED** |
| Raw Distance Match | Distance delta $< 10^{-7}$ | $\Delta = 0.0$ | **PASSED** |
| Displayed Score Match | Exact match on 4-decimal rounded similarities | 100% match | **PASSED** |
| Tie-Breaking Fidelity | Preserves native HNSW node traversal order | 100% match | **PASSED** |

**Conclusion:** The Option C Native Snapshot Runtime executed through the authentic `ThreatRAGEngine` retrieval path reproduces the frozen baseline with 100% fidelity on the approved development fixtures.
