# NexusCTI Phase 9.5 — ChromaDB Version and Source Code Audit

**Document Version:** 1.0 (Technical Deep-Dive Audit)  
**Date:** 2026-10-11  
**Project Root:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI`  
**Target Environment:** Python 3.10 (.venv)  
**Evaluated Package:** `chromadb` (Installed Version: `1.5.9`)  
**Source Path:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI\.venv\Lib\site-packages\chromadb`  

---

## 1. Executive Summary

Phase 9.4 halted Phase 10 authorization because `chromadb.PersistentClient` attempts SQLite write operations during initialization, crashing when filesystem write permissions are denied (`chmod 0o444` / `attrib +r`). 

This technical audit investigates the exact installed ChromaDB package (`version 1.5.9`) to establish:
1. Whether ChromaDB officially or unofficially supports a persistent read-only query mode.
2. The exact call stack and mechanism responsible for write attempts during client initialization.
3. The distinction between SQLite storage-layer activity (header change counter, WAL/journal) and substantive canonical data mutations.
4. The feasibility and risks of connection-pool monkey patching versus adapter-based remediation.

**Core Audit Finding:**  
ChromaDB `1.5.9` **does NOT officially support read-only persistent querying**. There is no supported configuration, environment variable, or client parameter that allows `PersistentClient` to operate against a read-only SQLite database. Any attempt to enforce read-only status at the operating system level results in an unhandled SQLite fatal exception (`code: 8, attempt to write a readonly database`).

---

## 2. Package Version and Environment Verification

The runtime environment was inspected via Python interpreter interrogation and virtual environment inspection:

```python
import chromadb
print(chromadb.__version__)  # Output: 1.5.9
```

- **Exact Version:** `1.5.9`
- **Underlying Engine:** SQLite 3 (`sqlite3` standard library interface) + `hnswlib` native C++ bindings for vector indexing (`urn:chroma:segment/vector/hnsw-local-persisted`).
- **Storage Architecture:** Dual-engine hybrid persistence:
  1. Metadata and coordination stored in `chroma.sqlite3` (SQLite database).
  2. Dense vector graph index stored in segment directory `3962f896-273d-4039-b97e-d0aa4e6d29ed/` containing binary index files (`data_level0.bin`, `header.bin`, `length.bin`, `link_lists.bin`).

---

## 3. ChromaDB Source Code Audit

A comprehensive search across all 185 Python files in `.venv/Lib/site-packages/chromadb` was conducted for read-only tokens (`readonly`, `read_only`, `mode=ro`, `PRAGMA query_only`).

**Search Result:** **0 matches** across the entire client, database, and segment implementation layers.

### 3.1 Trace of `chromadb.PersistentClient` Initialization

When `ThreatRAGEngine` instantiates `chromadb.PersistentClient`:

```python
self.client = chromadb.PersistentClient(
    path=str(self.persist_directory),
    settings=Settings(anonymized_telemetry=False, is_persistent=True),
)
```

The call chain executes as follows:

1. **`chromadb.__init__.PersistentClient(path, settings)`**:
   - Validates that `path` is a filesystem path string.
   - Instantiates `chromadb.api.segment.SegmentAPI`.
   - Passes system settings to `chromadb.db.impl.sqlite.SqliteDB`.

2. **`chromadb.db.impl.sqlite.SqliteDB.__init__()`**:
   - Resolves `self._db_file = os.path.join(persist_directory, "chroma.sqlite3")`.
   - Constructs a connection pool: `self._conn_pool = PerThreadPool(self._db_file)`.
   - In `chromadb.db.impl.sqlite.PerThreadPool._get_conn()`:
     ```python
     # Inside chroma/db/impl/sqlite.py
     conn = sqlite3.connect(self._db_file)
     ```
     Notice that `sqlite3.connect` is invoked **without** `uri=True` and **without** `?mode=ro`. SQLite defaults to `SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE`.

3. **Automatic Schema Migrations and Lock Checks**:
   - `SqliteDB.start()` invokes `SqliteDB._initialize_migrations()`.
   - It checks table `migrate_operations` and `migrations`.
   - It executes:
     ```sql
     CREATE TABLE IF NOT EXISTS migrations (
         dir TEXT,
         version INTEGER,
         hash TEXT
     );
     ```
   - It then acquires a migration lock on table `acquire_write`.

4. **Failure under Filesystem Read-Only Protection**:
   - If the database file has the OS read-only attribute set (`stat.S_IREAD`), SQLite fails on the very first migration check or transaction begin:
     ```
     chromadb.errors.InternalError: (code: 8) attempt to write a readonly database
     ```
   - The exception is raised inside CPython's `sqlite3` module and cannot be suppressed via settings.

---

## 4. Technical Distinctions in SQLite Activity

To design an objective, scientifically valid remediation, we must strictly distinguish four categories of file and data mutations:

| Activity Category | Mechanism | Physical File Impact | Canonical Data Impact | Retrieval Impact |
| :--- | :--- | :--- | :--- | :--- |
| **A. Write-Denied Open** | OS denies write access (`chmod 0o444`) | None (File access blocked) | Crashes process | Query impossible |
| **B. SQLite Header / Change Counter Activity** | SQLite transaction / connection bookkeeping | Bytes 24–27 (`file_change_counter`) incremented; raw SHA-256 changes | None (Zero rows altered) | None (Identical) |
| **C. Journal / WAL Activity** | SQLite temporary journal or WAL file creation | `-journal` or `-wal` sidecar files created temporarily | None | None |
| **D. Canonical Data Mutations** | `INSERT`, `UPDATE`, `DELETE` on records | Payload pages modified; content hashes mutate | Threat actors, embeddings, or metadata modified | Changes retrieval results |

### Audit Evidence:
- Under default permissions, executing `ThreatRAGEngine.hybrid_search()` causes Category B activity: the SQLite `file_change_counter` increments from 20 to 21 (or 22 to 23).
- Canonical table inspection (`collections`, `embeddings`, `embedding_metadata`) demonstrates that **0 rows** were altered. The canonical content SHA-256 hash remained strictly invariant:
  $$\text{Content SHA-256} = \texttt{668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7}$$
- However, because Phase 9.4 established a strict zero-mutation execution-safety boundary, the active ChromaDB client's inability to run under Category A constitutes an operational failure that requires architectural remediation.

---

## 5. Feasibility of Monkey-Patching Internal Connection Pools

We evaluated whether monkey-patching `chromadb.db.impl.sqlite.PerThreadPool._get_conn` to inject `uri=True` and `file:{path}?mode=ro` could resolve the issue.

### Technical Assessment:
1. **Migration Engine Conflict**: Even if the connection is opened with `?mode=ro`, ChromaDB's startup lifecycle unconditionally executes `CREATE TABLE IF NOT EXISTS migrations` and `INSERT INTO acquire_write`. A read-only SQLite connection will immediately raise `sqlite3.OperationalError: attempt to write a readonly database` when ChromaDB executes these statements.
2. **Version Fragility**: Monkey-patching internal private methods (`_get_conn`, `_initialize_migrations`) violates software engineering integrity, creates a fragile dependency on undocumented internals of ChromaDB 1.5.9, and cannot be audited cleanly under the preregistered evaluation protocol.
3. **Verdict**: **REJECTED AS AN UNSTABLE / VERSION-FRAGILE HACK**.

---

## 6. Conclusion and Remediation Mandate

ChromaDB 1.5.9 cannot natively operate in a read-only mode where filesystem writes are prohibited. 

To satisfy the protocol freeze and preserve scientific rigor, NexusCTI must either:
1. Implement a clean, decoupled read-only query adapter (`ReadOnlyChromaAdapter`) that reads frozen embeddings directly via native SQLite `?mode=ro`, or
2. Employ an isolated, ephemeral snapshot architecture (Option C) combined with a formal protocol amendment defining logical content invariance (Option D).
