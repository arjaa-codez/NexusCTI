# NexusCTI Phase 9.5 — Remediation Options Comparison

**Document Version:** 1.0 (Design & Feasibility Evaluation)  
**Date:** 2026-10-11  
**Project Root:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI`  
**Target Phase:** Phase 9.5 Remediation Design  

---

## 1. Executive Summary

Phase 9.4 correctly halted Phase 10 evaluation because the active `chromadb.PersistentClient` requires SQLite write access during initialization and crashes when write access is denied. 

This document evaluates four distinct remediation designs against the hard constraints of Phase 9.5:
- **Zero modification** to model weights, graph semantics, fusion weights, or decision thresholds.
- **Zero access** to prospective test labels (100 Task A + 30 Task B test cases).
- **Zero modification** to the original frozen database (`cyber_attribution_engine/data/chroma_db/chroma.sqlite3`).
- **Full audit trail** and complete cryptographic hash tracking.

---

## 2. Detailed Technical Comparison Matrix

The four remediation candidates were evaluated across six operational criteria:

| Evaluation Dimension | Option A: Native ChromaDB Read-Only | Option B: Custom Read-Only Query Adapter | Option C: Immutable Snapshot + Ephemeral Runner | Option D: Formal Protocol Logical Immutability Amendment |
| :--- | :--- | :--- | :--- | :--- |
| **1. Physical Write Prevention** | **IMPOSSIBLE** (Fails with SQLite error code 8) | **STRICTLY IMPOSSIBLE** (Runs on OS `chmod 0o444` write-protected file) | **PERMITTED ON EPHEMERAL COPY ONLY** (Master copy remains untouched) | **PERMITTED FOR METADATA** (Bookkeeping writes tolerated on SQLite header) |
| **2. Compatibility with Frozen Runtime** | Fully native, but non-functional under write denial | High compatibility (replaces `PersistentClient` retrieval call in RAG engine) | 100% native compatibility (no code changes to `ThreatRAGEngine`) | 100% native compatibility (no code changes to any component) |
| **3. Retrieval Output Equivalence** | Baseline standard | **100% EQUIVALENT** on distinct scores; slight tie-breaking variance on ties | **100% BIT-IDENTICAL** across all queries and edge cases | **100% BIT-IDENTICAL** across all queries and edge cases |
| **4. Ranking / Semantic Risk** | None (Baseline) | Low (mathematically identical cosine similarity dot-product) | None (identical binary code executed) | None (identical binary code executed) |
| **5. Changed Files & Re-Freezing** | None | Requires adding `ReadOnlyChromaAdapter` to `rag_engine.py` or evaluation runner | Requires ephemeral scratch copy logic in evaluation harness | Protocol document update only; zero code changes |
| **6. Protocol Governance Status** | Violates existing strict write-denial rule | Requires code reconciliation and re-freeze manifest | Satisfies physical isolation of master; requires snapshot clarification | Requires formal prospective protocol amendment |

---

## 3. Deep-Dive Evaluation of Each Option

### 3.1 Option A: Supported Read-Only ChromaDB Query Path
- **Description:** Attempt to pass configuration flags, environment variables, or SQLite connection parameters (`?mode=ro`) to `chromadb.PersistentClient` to achieve native read-only operation.
- **Physical Writes:** Cannot be prevented. ChromaDB `1.5.9` does not support read-only mode. When filesystem write access is revoked via `chmod 0o444`, `PersistentClient` crashes on startup with `chromadb.errors.InternalError: (code: 8) attempt to write a readonly database`.
- **Runtime Compatibility:** Incompatible with a write-denied environment.
- **Output Equivalence:** N/A (cannot execute).
- **Verdict:** **TECHNICALLY UNVIABLE**. Discarded.

---

### 3.2 Option B: Custom Read-Only Query Adapter (`ReadOnlyChromaAdapter`)
- **Description:** Implement an independent, minimal read-only query adapter that connects directly to `chroma.sqlite3` using Python's standard `sqlite3` library with explicit URI read-only syntax (`file:{path}?mode=ro`, `uri=True`). The adapter reads the frozen 384-dimensional dense vectors and metadata from the `embeddings_queue` table, generates query embeddings using the identical `MiniLMEmbeddingFunction`, and computes cosine similarity via NumPy dot products.
- **Physical Writes:** **STRICTLY IMPOSSIBLE**. Because the connection is opened in `?mode=ro`, the operating system and SQLite engine reject all writes. Verified empirically on write-protected files (`chmod 0o444`) with **0-byte file mutation** and **change counter delta = 0**.
- **Runtime Compatibility:** Directly replicates `ThreatRAGEngine.hybrid_search(query, gnn_top_group, top_k)`.
- **Retrieval Equivalence:**
  - On development queries with distinct similarity scores (T1, T2, T3, T4, T5, T6, T7, T9), output documents, threat actor labels, and similarity scores are **100% bit-identical** to ChromaDB.
  - On queries with exact similarity ties (e.g. T8 where 5 documents have similarity 0.0, or T10 where two documents have raw similarity 0.0527), minor rank ordering differences occur because ChromaDB uses HNSW graph beam traversal order for ties whereas the adapter uses unrounded dot-product sorting.
- **Risks:** Requires introducing new adapter code, which alters source file SHA-256 hashes and requires protocol reconciliation before Phase 10.
- **Verdict:** **HIGHLY VIABLE TECHNICAL REMEDIATION**.

---

### 3.3 Option C: Immutable Master Database Snapshot + Ephemeral Inference Runner
- **Description:** Preserve the original frozen database (`cyber_attribution_engine/data/chroma_db/chroma.sqlite3`) as an immutable golden master locked with read-only permissions on disk. At evaluation runtime, the harness copies the database to an ephemeral temporary directory (`tempfile.TemporaryDirectory()`), executes standard `ThreatRAGEngine` inference against the temporary replica, and deletes the replica immediately after evaluation.
- **Physical Writes:** The golden master database experiences **ZERO physical writes** and remains cryptographically invariant before and after the evaluation. The ephemeral scratch replica experiences standard SQLite change counter increments (bytes 24–27).
- **Runtime Compatibility:** **100% COMPATIBLE**. Requires zero changes to `ThreatRAGEngine`, `SentenceTransformer`, or ChromaDB internals.
- **Retrieval Equivalence:** **100% BIT-IDENTICAL**. Guaranteed byte-for-byte fidelity with the original frozen system.
- **Risks:** The ephemeral copy undergoes metadata header mutations during inference.
- **Verdict:** **HIGHLY VIABLE OPERATIONAL REMEDIATION**.

---

### 3.4 Option D: Formal Protocol Amendment Defining Logical-Content Immutability
- **Description:** Formally amend the protocol preregistration to replace the raw binary file hash requirement with a **canonical logical content hash requirement**. Under this definition, database immutability is defined as:
  $$\text{Content Invariance} \iff \Delta\Big(\text{SHA-256}\big(\text{canonical}(\text{collections}, \text{embeddings}, \text{metadata})\big)\Big) = 0$$
  Internal SQLite housekeeping writes (e.g. `file_change_counter` in bytes 24–27, transaction flags, cache flush timestamps) are explicitly categorized as benign storage-layer artifacts that do not affect scientific validity.
- **Scientific and Operational Assessment:**
  - *Scientific Integrity:* The scientific endpoint of NexusCTI evaluates threat actor attribution accuracy. As long as the document texts, vector embeddings, chunk indices, and threat actor labels remain 100% invariant, the retrieval space is completely identical.
  - *Distinction from Excusing Substantive Writes:* This amendment does **NOT** permit substantive writes (`INSERT`, `UPDATE`, `DELETE`). Any change to table contents or collection records triggers an immediate audit failure.
- **Verdict:** **ESSENTIAL GOVERNANCE BRIDGE**.

---

## 4. Synthesis and Recommended Remediation Strategy

The optimal, most robust scientific strategy combines **Option B / Option C** with **Option D**:

1. **Operational Level (Option C):** Protect the master database on disk at all times. Phase 10 inference should operate against an ephemeral verified scratch replica to prevent any accidental corruption or mutation of the golden master.
2. **Technical Alternative (Option B):** If strict OS-level write denial must be enforced on the active file itself during inference, `ReadOnlyChromaAdapter` is fully validated to execute under `chmod 0o444` with 0 byte mutations.
3. **Governance Level (Option D):** Formally record a prospective protocol amendment defining canonical logical content hash invariance (`668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7`) as the official verification criterion for database integrity.
