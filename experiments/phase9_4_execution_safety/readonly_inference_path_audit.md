# NexusCTI Phase 9.4 — Read-Only Inference Path Audit

**Document Version:** 1.0 (Operational Safeguard Audit)  
**Date:** 2026-10-11  
**Project Root:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI`  
**Experiment Root:** `experiments/phase9_4_execution_safety/`  
**Telemetry Artifact:** `execution_safety_telemetry.json`  
**Executable Audit Script:** `run_safety_check_audit.py`

---

## 1. Executive Summary & Core Finding

In Phase 9.3, read-only database integrity was evaluated using an isolated, direct SQLite connection with URI mode `?mode=ro`. While this proved that the raw underlying SQLite data can be queried in read-only mode by Python's native `sqlite3` library, **it did not test the actual ChromaDB client used in the active inference path**.

In this Phase 9.4 execution-safety audit, we traced and empirically instrumented the **actual active retrieval path** (`ThreatRAGEngine` -> `chromadb.PersistentClient` -> `SqliteDB` -> `collection.query()`). 

### Critical Audit Finding:
> **The active ChromaDB client implementation (`chromadb.PersistentClient`) CANNOT reliably operate in a read-only configuration where database writes are prevented.**
>
> 1. When `chromadb.PersistentClient` initializes, its underlying connection manager (`PerThreadPool`) opens `chroma.sqlite3` in read-write mode and executes migration checks and lock acquisition.
> 2. This connection handshake automatically increments SQLite file header bytes 24–27 (the `file_change_counter`), mutating the raw file SHA-256 hash even during a pure retrieval query.
> 3. When write access is strictly prevented at the OS filesystem level (read-only attribute / `chmod 0o444`), `chromadb.PersistentClient` crashes on startup with:
>    $$\texttt{chromadb.errors.InternalError: (code: 8) attempt to write a readonly database}$$
> 4. In accordance with the protocol instructions (*"If the active ChromaDB implementation cannot reliably operate read-only, STOP and report the limitation. Do not silently substitute a different retrieval backend or alter the locked system"*), this limitation is formally recorded, requiring remediation before Phase 10.

---

## 2. Active Retrieval Path Trace

The execution call stack from the evaluation runner down to the SQLite storage layer was traced through the codebase:

```
[Phase 10 Evaluation Runner / NexusCTI Pipeline]
    │
    ▼
cyber_attribution_engine.src.rag_engine.ThreatRAGEngine
    │
    ├── __init__(persist_directory="cyber_attribution_engine/data/chroma_db")
    │     │
    │     ├── Resolves Path: C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\cyber_attribution_engine\data\chroma_db
    │     │
    │     └── chromadb.PersistentClient(path=str(self.persist_directory), settings=Settings(...))
    │           │
    │           ▼
    │         chromadb.db.impl.sqlite.SqliteDB.__init__()
    │           │
    │           ├── self._db_file = self._settings.require("persist_directory") + "/chroma.sqlite3"
    │           └── self._conn_pool = PerThreadPool(self._db_file)
    │                 │
    │                 └── sqlite3.connect(self._db_file)  <-- [OPENS IN READ-WRITE MODE, NO ?mode=ro]
    │
    ├── self.collection = self.client.get_or_create_collection("cti_threat_reports")
    │     │
    │     └── Executes write-capable schema check / migration verification in SQLite
    │
    └── hybrid_search(query, gnn_top_group, top_k)
          │
          └── self.collection.query(query_embeddings=[query_emb], n_results=top_k)
```

### Configured Database Path Resolution:
- Configured Relative Path: `cyber_attribution_engine/data/chroma_db/chroma.sqlite3`
- Absolute Target File: `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\cyber_attribution_engine\data\chroma_db\chroma.sqlite3`
- Target File Status: **EXISTS AND VERIFIED** (Size: $294{,}912$ bytes).

---

## 3. Empirical Test on Development Fixture

To audit the runtime behavior without altering the production database, the active database was duplicated to an isolated scratch fixture (`experiments/phase9_4_execution_safety/scratch/chroma_test_active/chroma.sqlite3`).

### 3.1 Test A: Active Client Query Under Default File Permissions
The active `ThreatRAGEngine` was instantiated pointing to the test fixture, and a known development fixture query was executed:
- Query: `"cisa advisory apt29 solarwinds orion backdoor 185.225.17.42"` with `gnn_top_group="APT29"`.
- Results Retrieved: $2$ authentic CTI document chunks (`cisa_aa20_352a_apt29_solarwinds_0`, `cisa_aa20_352a_apt29_solarwinds_1`).

**Telemetry Observed:**
```
Pre-Test SQLite Change Counter (Bytes 24-27):  20
Post-Test SQLite Change Counter (Bytes 24-27): 21  (Incremented by +1)
Raw File Binary SHA-256 Match:                 FALSE (Mutated due to change counter)
Canonical Content SHA-256 Match:              TRUE  (100% Invariant, 668d0776...)
```
While the canonical logical content remained completely unaltered, the active ChromaDB client performed a file-level modification to SQLite metadata.

### 3.2 Test B: Write-Prevented Execution (Read-Only Filesystem Enforcement)
To determine if ChromaDB can execute when physical writes are prohibited, the isolated database file was set to read-only (`os.chmod(test_ro_sqlite, stat.S_IREAD)` / `attrib +r`):

**Outcome Observed:**
```
Execution Attempt: ThreatRAGEngine(persist_directory=test_ro_dir)
Result:            CRASH ON STARTUP
Exception:         chromadb.errors.InternalError
Error Message:     error returned from database: (code: 8) attempt to write a readonly database
```

### 3.3 Root Cause Analysis
1. ChromaDB's `SqliteDB` implementation initializes connection pools via `PerThreadPool(self._db_file)`.
2. Unlike the in-memory mode (which uses `file::memory:?cache=shared` with `is_uri=True`), persistent mode passes a raw file path string.
3. ChromaDB's startup sequence unconditionally verifies schema migrations and attempts lock transactions in SQLite. When SQLite opens a database whose file permissions are read-only, any attempt to acquire a transaction lock or check migrations fails with SQLite error code 8 (`SQLITE_READONLY`).
4. Standalone URI connection (`file:chroma.sqlite3?mode=ro`) works in raw Python `sqlite3`, but ChromaDB's high-level `PersistentClient` does not support URI connection parameters or an explicit read-only flag.

---

## 4. Audit Conclusion & Compliance Action

The prompt establishes a strict decision protocol:
> *"If the active ChromaDB implementation cannot reliably operate read-only, STOP and report the limitation. Do not silently substitute a different retrieval backend or alter the locked system."*

Because the active ChromaDB client cannot operate in a write-prevented configuration and automatically increments the SQLite file change counter, the system **cannot satisfy the strict operational read-only guarantee under its current client implementation without engineering remediation**.

Therefore, the evaluation must **STOP** at Phase 9.4 and issue the verdict:
**`NOT READY — REMEDIATION REQUIRED`**.
