# NexusCTI Phase 9.6 — Runtime Architecture Decision

**Document Version:** 1.0 (Architecture Selection & Engineering Rationale)  
**Date:** 2026-10-11  
**Project Root:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI`  
**Experiment Root:** `experiments/phase9_6_runtime_reconciliation/`  
**Target Evaluation:** Phase 10 Independent Blind Evaluation  

---

## 1. Executive Summary

Phase 9.5 evaluated four remediation designs to resolve ChromaDB's inability to query under filesystem write denial. Phase 9.6 was chartered to make a prospective, documented architectural selection between:
- **Option C:** Disposable Runtime Snapshot executing native `chromadb.PersistentClient` / `ThreatRAGEngine`.
- **Option B:** Custom Read-Only Query Adapter (`ReadOnlyChromaAdapter`) bypassing ChromaDB migrations via direct SQLite `?mode=ro`.

### Architectural Decision:
> **Option C (Disposable Runtime Snapshot Architecture) is formally SELECTED as the primary runtime architecture for NexusCTI Phase 10 evaluation.**
>
> **Option B (Custom Read-Only Query Adapter) is retained as a fully validated, audited secondary fallback.**

This decision preserves 100% binary fidelity with the frozen model and native retrieval engine, avoids subtle tie-breaking discrepancies, protects the golden master database against mutation, and maintains reproducible inference ranking across independent executions.

---

## 2. Comparative Evaluation: Native Snapshot vs Custom Adapter

| Dimension | Option C: Disposable Native Snapshot | Option B: Custom Read-Only Adapter | Selected Option Advantage |
| :--- | :--- | :--- | :--- |
| **System Code Invariance** | **100% Unchanged** (`rag_engine.py` frozen) | Requires code modification or adapter injection | **Option C:** Zero changes to frozen code base |
| **Retrieval Engine Fidelity** | Native C++ HNSWlib index (`urn:chroma:...`) | Custom Python NumPy dot-product brute force | **Option C:** Exact native index traversal preserved |
| **Master Database Protection** | Master file locked; never written to (0 bytes modified) | Master file queried directly under `?mode=ro` | **Tie:** Both guarantee master database invariance |
| **Physical Write Denial on Active DB** | **No:** Ephemeral snapshot permits SQLite header writes | **Yes:** Active file operates under OS `chmod 0o444` | **Option B:** Option B strictly denies physical writes |
| **Tie-Breaking Determinism** | 100% bit-identical across fresh snapshot creations | Sensitive to unrounded vs rounded sort ordering | **Option C:** Identical to baseline development behavior |
| **Operational Overhead** | Ephemeral file copy ($294\text{ KB}$) created and destroyed | Direct file connection, zero copy overhead | **Option B:** Minimal overhead, but Option C copy is $<5\text{ ms}$ |
| **Protocol Governance Impact** | Requires formal amendment defining snapshot lifecycle | Requires formal amendment re-freezing adapter code | **Option C:** Governance cleanly isolates infrastructure from science |

---

## 3. Detailed Rationale for Selecting Option C

### 3.1 Preservation of Native HNSW Index Semantics
The frozen NexusCTI retrieval system uses ChromaDB's local persistent HNSW implementation (`urn:chroma:segment/vector/hnsw-local-persisted`). The segment directory (`3962f896-273d-4039-b97e-d0aa4e6d29ed/`) contains pre-constructed binary graph structures (`data_level0.bin`, `link_lists.bin`, `header.bin`, `length.bin`).
- Running Option C executes the authentic HNSW graph traversal routines compiled into `chromadb.segment.impl.vector.local_hnsw`.
- Substituting a custom linear-scan adapter (Option B) replaces graph-based approximate nearest neighbor traversal with brute-force linear search. While mathematically identical for small collections ($N=7$), it changes the runtime execution model and introduces tie-breaking ordering differences in boundary cases.
- Option C maintains complete algorithmic continuity with prior evaluation phases (Phase 6, Phase 8).

### 3.2 Master Database Immutability Guaranteed
Option C establishes a strict physical separation between the authoritative frozen repository and the execution environment:
1. The **Frozen Master Database** (`cyber_attribution_engine/data/chroma_db/chroma.sqlite3`) remains write-protected on disk and is never opened directly by a write-capable client.
2. Before inference begins, an ephemeral replica is instantiated in a secure temporary directory (`tempfile.TemporaryDirectory()`).
3. Native ChromaDB performs its necessary connection and transaction handshakes on the ephemeral copy.
4. After inference completes, the ephemeral directory is completely purged.
5. Post-run cryptographic verification proves that the master database experienced **0 bytes modified** and **change counter delta = 0**.

### 3.3 Elimination of Code Freeze Violations
Deploying Option B requires modifying `cyber_attribution_engine/src/rag_engine.py` or intercepting `ThreatRAGEngine` calls within the evaluation harness. Modifying frozen core source code invalidates previous hash manifests (`frozen_system_manifest.json`) and introduces new surface area for bugs.
In contrast, Option C executes the unmodified frozen `ThreatRAGEngine` code:
$$\text{SHA-256}(\texttt{cyber\_attribution\_engine/src/rag_engine.py}) = \texttt{dc7363eb70a9203c9ebf77f68c34f3c7e0c93c4e3635749f7ba384dbbf9be253}$$

---

## 4. Operational Requirements for Option C Execution

To ensure Option C satisfies scientific auditability during Phase 10:
1. **Pre-Run Verification:** The evaluation harness must compute the SHA-256 hash and canonical content hash of the master database and verify them against the frozen manifest before creating the snapshot.
2. **One-Way Copy Direction:** The runtime copy operation is strictly one-directional: $\text{Master} \to \text{Snapshot}$. Copying from $\text{Snapshot} \to \text{Master}$ is physically prohibited by code structure and filesystem permissions.
3. **Mandatory Ephemeral Disposal:** The snapshot must be destroyed upon evaluation completion, with failure to clean up treated as an execution anomaly.
4. **Post-Run Verification:** The harness must re-hash the master database immediately after evaluation completion to confirm zero bytes were modified.
5. **No False Claims of Physical Read-Only Active DB:** Documentation must explicitly disclose that the runtime snapshot experiences SQLite header change counter increments (bytes 24–27), while the master remains immutable.

---

## 5. Architectural Conclusion

Option C is the superior, scientifically sound remediation. It preserves native code and graph index behavior, guarantees master database invariance, and provides complete determinism across executions. Option C is hereby selected for prospective protocol reconciliation.
