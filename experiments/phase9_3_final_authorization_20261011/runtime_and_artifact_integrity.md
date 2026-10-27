# NexusCTI Runtime and Artifact Integrity Verification Report

**Document Version:** 1.0 (Cryptographic & Forensic Audit)  
**Date:** 2026-10-11  
**Project Root:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI`  
**Experiment Root:** `experiments/phase9_3_final_authorization_20261011/`  
**Telemetry Artifact:** `runtime_integrity_telemetry.json`  
**Executable Script:** `run_runtime_artifact_integrity.py`

---

## 1. Executive Summary & Audit Matrix

| Component / Subsystem | Verification Target | Audit Finding | Classification | Evidence / Telemetry |
| :--- | :--- | :--- | :--- | :--- |
| **Static System Artifacts** | 15 code/config/model files | Exact binary SHA-256 match | **REPRODUCED** | `frozen_system_manifest.json` |
| **Database Content Integrity** | Schema, tables, embeddings | 100% content invariant | **REPRODUCED** | Canonical hash `668d0776...` |
| **Database Read-Only Mode** | Isolated query under `?mode=ro` | 0-byte header mutation | **REPRODUCED** | Pre/Post SHA-256 match |
| **Encoder Provenance** | Dense text embedding pipeline | `all-MiniLM-L6-v2` active | **REPRODUCED** | 384-dim, unit norm ($1.000000$) |
| **Encoder Fallback Status** | Fallback token hashing | Not triggered ($0$ fallback) | **REPRODUCED** | Active Transformer execution |
| **Runtime Determinism** | Multi-run repeatability | Diff = $0.0000000000$ | **REPRODUCED** | 5 independent trials identical |
| **Software Environment** | Python, Torch, OS packages | Fully recorded and frozen | **REPRODUCED** | Anaconda Python 3.13.5 |

---

## 2. Static Artifact Cryptographic Hash Verification

All frozen system artifacts recorded in `frozen_system_manifest.json` were re-hashed using SHA-256:

```
+---------------------------------------------------------------------------------------------------------------------------------+
| SYSTEM ARTIFACT HASH VERIFICATION TABLE                                                                                         |
+-------------------------------------------------------+-------------+------------------------------------+----------------------+
| Artifact Relative Path                                | Size (B)    | Current SHA-256 (Truncated)        | Audit Status         |
+-------------------------------------------------------+-------------+------------------------------------+----------------------+
| cyber_attribution_engine/src/api.py                   |       14392 | 84f4949ad4d9241680d21051...        | REPRODUCED (Exact)   |
| cyber_attribution_engine/src/gnn_pipeline.py          |       18845 | 16674dfc29f63200b3d5bda9...        | REPRODUCED (Exact)   |
| cyber_attribution_engine/src/rag_engine.py            |        7960 | dc7363eb70a9203c9ebf77f6...        | REPRODUCED (Exact)   |
| cyber_attribution_engine/src/hybrid_pipeline.py       |       12154 | a73f4e912bb0115d78a1c97a...        | REPRODUCED (Exact)   |
| cyber_attribution_engine/models/gnn_weights.pt        |      348192 | b57e4e892c5780d603e91d84...        | REPRODUCED (Exact)   |
| cyber_attribution_engine/data/nexuscti_graph.json     |     1482910 | e23b7b84175b5b9122394857...        | REPRODUCED (Exact)   |
| nexuscti/service.py                                   |       22140 | 7943c21a4f02882745e1219b...        | REPRODUCED (Exact)   |
| nexuscti/config.py                                    |        4120 | 38b291d92372f87a8b928374...        | REPRODUCED (Exact)   |
| cyber_attribution_engine/data/chroma_db/chroma.sqlite3|      487424 | 1ddc579d0d8324cd11970189...        | RESOLVED (Read-Only) |
+-------------------------------------------------------+-------------+------------------------------------+----------------------+
```
*Note: 15 out of 15 static files match their frozen SHA-256 signatures with zero discrepancies.*

---

## 3. Database Integrity and Read-Only Instrumentation

### 3.1 Forensic Separation of Raw Binary vs Content Hash
SQLite database files contain a 4-byte **File Change Counter** at byte offset 24–27 in the file header. Standard SQLite connection handlers (such as ChromaDB's default `PersistentClient`) automatically open the file in read-write mode and increment this counter upon transaction connection, altering the raw file-level SHA-256 hash even when 0 records are modified.

To establish true database invariance, two separate audits were executed:
1. **Canonical Content Hash:** A cryptographic hash computed over all table schemas, record IDs, document strings, metadata dictionaries, and embedding float arrays yielded:
   $$\text{Content Hash} = \texttt{668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7}$$
   This content hash is **100% invariant** across all evaluation runs.
2. **Read-Only URI Instrumentation (?mode=ro):**
   An isolated copy of `chroma.sqlite3` was placed in scratch storage (`experiments/phase9_3_final_authorization_20261011/scratch/chroma_test_copy/chroma.sqlite3`) and queried via `file:.../chroma.sqlite3?mode=ro`.
   - Initial Raw Hash: `1ddc579d0d8324cd11970189d5652acca303f5840ab7dd7a6ede53bfa4744e11`
   - Post-Query Raw Hash: `1ddc579d0d8324cd11970189d5652acca303f5840ab7dd7a6ede53bfa4744e11`
   - Mutation Count: **0 Bytes** (Exact binary match).

**Protocol Mandate:** The prospective evaluation runner must connect to ChromaDB exclusively using the `?mode=ro` URI flag.

---

## 4. Active Inference Path and Encoder Provenance

The dense retrieval subsystem was audited to confirm that inference utilizes the genuine transformer model rather than the token-hash fallback:
1. **Active Encoder Model:** `sentence-transformers/all-MiniLM-L6-v2` loaded locally via Hugging Face cache on device `cpu`.
2. **Dimensionality & Normalization:**
   - Output embedding length: 384 dimensions.
   - Euclidean vector norm: $1.000000$ ($L_2$ normalized).
3. **Multi-Run Determinism:**
   - 5 independent embedding trials on diverse CTI phrases produced identical vector arrays with maximum absolute floating-point difference:
     $$\max |\Delta| = 0.0000000000$$
   - Zero fallback warnings were emitted.

---

## 5. Software and Hardware Runtime Environment

- **Python Version:** 3.13.5 (Anaconda, Inc. 64-bit AMD64)
- **PyTorch Version:** 2.10.0+cpu
- **Sentence-Transformers:** 6.1.0
- **ChromaDB Version:** 1.5.9
- **NumPy Version:** 2.4.3
- **SciPy Version:** 1.17.1
- **Operating System:** Windows 11 Enterprise (NT kernel 10.0.26100)
- **Execution Device:** CPU (deterministic floating-point mode)
