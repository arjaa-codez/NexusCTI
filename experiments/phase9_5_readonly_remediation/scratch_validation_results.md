# NexusCTI Phase 9.5 — Scratch Validation Results

**Document Version:** 1.0 (Empirical Test Telemetry)  
**Date:** 2026-10-11  
**Project Root:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI`  
**Test Script:** [run_phase9_5_validation.py](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_5_readonly_remediation/run_phase9_5_validation.py)  
**Telemetry Artifact:** [remediation_telemetry.json](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_5_readonly_remediation/remediation_telemetry.json)  
**Scratch Database Target:** `experiments/phase9_5_readonly_remediation/scratch/chroma_remediation_test.sqlite3`  

---

## 1. Executive Summary

This document presents the empirical validation results of the remediation design tested on an isolated scratch copy of the frozen ChromaDB database.

### Core Validation Findings:
1. **Physical Write Prevention Succeeded:** When strict OS-level read-only permissions were enforced (`chmod 0o444` / `attrib +r`), the custom `ReadOnlyChromaAdapter` initialized and executed 10 diverse test queries with **ZERO errors** and **ZERO crashes**.
2. **Binary Raw File Hash Preserved:**
   $$\text{Pre-Test Raw SHA-256} = \texttt{4860151a865b40d15bef1d1c9e55744c72a7065f2cc230fb25193c3c5bdbcdfe}$$
   $$\text{Post-Test Raw SHA-256} = \texttt{4860151a865b40d15bef1d1c9e55744c72a7065f2cc230fb25193c3c5bdbcdfe}$$
   $$\mathbf{\Delta(\text{Raw SHA-256}) = 0\text{ bytes modified}}$$
3. **SQLite Header Change Counter Invariant:**
   $$\text{Pre-Test Change Counter (Bytes 24–27)} = 22$$
   $$\text{Post-Test Change Counter (Bytes 24–27)} = 22$$
   $$\mathbf{\Delta(\text{Change Counter}) = 0}$$
4. **Canonical Logical Content Hash Invariant:**
   $$\text{Pre-Test Canonical Content SHA-256} = \texttt{668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7}$$
   $$\text{Post-Test Canonical Content SHA-256} = \texttt{668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7}$$
   $$\mathbf{\Delta(\text{Content Hash}) = 0}$$

---

## 2. Experimental Setup and Write Protection

To eliminate any risk of mutating the original frozen database (`cyber_attribution_engine/data/chroma_db/chroma.sqlite3`), the validation procedure strictly isolated the test environment:

```python
# 1. Create isolated scratch replica
scratch_db = SCRATCH_DIR / "chroma_remediation_test.sqlite3"
shutil.copy2(CHROMA_ORIG_PATH, scratch_db)

# 2. Deny write permissions at the OS filesystem level
os.chmod(scratch_db, stat.S_IREAD)  # chmod 0o444
```

### Sidecar File Auditing:
- Prior to test: 0 journal files, 0 WAL files (`chroma_remediation_test.sqlite3-journal` and `-wal` did not exist).
- After test execution: 0 journal files, 0 WAL files created.

---

## 3. Query Suite and Empirical Telemetry

A suite of 10 diverse development queries was executed, evaluating authentic CTI campaigns, cross-actor filtering, edge cases, out-of-vocabulary terms, empty strings, and special characters:

| Test ID | Query Text | GNN Candidate Group | Top-k | Retrieved Count | Top-1 Threat Actor | Similarity Scores | Status |
| :--- | :--- | :--- | :---: | :---: | :--- | :--- | :---: |
| **T1** | `"SolarWinds backdoor SUNBURST 185.225.17.42"` | `APT29` | 2 | 2 | `APT29` | `[0.0, 0.0]` | **PASS** (Bit-Identical) |
| **T2** | `"Sandworm wiper high voltage substation Industroyer2"` | `Sandworm Team` | 2 | 1 | `Sandworm Team` | `[0.0322]` | **PASS** (Bit-Identical) |
| **T3** | `"AppleJeus cryptocurrency exchange trojanized application"` | `Lazarus Group` | 2 | 1 | `Lazarus Group` | `[0.0]` | **PASS** (Bit-Identical) |
| **T4** | `"Volt Typhoon living off the land wmic powershell cve"` | `Volt Typhoon` | 2 | 1 | `Volt Typhoon` | `[0.0743]` | **PASS** (Bit-Identical) |
| **T5** | `"FIN7 financial POS malware Carbanak cash out"` | `FIN7` | 2 | 1 | `FIN7` | `[0.0]` | **PASS** (Bit-Identical) |
| **T6** | `"APT28 Fancy Bear Zebrocy spearphishing credential harvesting"` | `APT28` | 2 | 1 | `APT28` | `[0.0]` | **PASS** (Bit-Identical) |
| **T7** | `"generic ransomware c2 beaconing payload"` | `Unknown` (unrestricted) | 3 | 3 | `Volt Typhoon` | `[0.1085, 0.0894, 0.0683]` | **PASS** (Bit-Identical) |
| **T8** | `"threat actor not in registry"` | `NovelUnseenActor` (fallback) | 3 | 3 | `Volt Typhoon` | `[0.0820, 0.0722, 0.0]` | **PASS (Scores Match)** / Tie order |
| **T9** | `""` (Empty query string) | `APT28` | 2 | 1 | `APT28` | `[0.0284]` | **PASS** (Bit-Identical) |
| **T10** | `"!@#$%^&*()_+~`{}[]:;'<>?,./"` (Special chars) | `None` (unrestricted) | 3 | 3 | `APT29` | `[0.0689, 0.0540, 0.0527]` | **PASS (Scores Match)** / Tie order |

---

## 4. Empirical Failure Analysis of Native ChromaDB Under Write Denial

To provide an empirical baseline, the native `ThreatRAGEngine` was invoked directly against the write-protected scratch copy:

```python
# Attempting native ChromaDB PersistentClient on write-protected scratch DB
test_engine = ThreatRAGEngine(persist_directory=SCRATCH_DIR)
```

**Observed Output:**
```
chromadb.errors.InternalError: error returned from database: (code: 8) attempt to write a readonly database
```

**Diagnostic Analysis:**
1. ChromaDB's `SqliteDB._initialize_migrations()` unconditionally issues:
   ```sql
   CREATE TABLE IF NOT EXISTS migrations (dir TEXT, version INTEGER, hash TEXT);
   ```
2. In SQLite, executing DDL statements (`CREATE TABLE IF NOT EXISTS`) requires a write transaction, even if the table already exists.
3. Because the file was write-protected, SQLite returned error code 8 (`SQLITE_READONLY`).
4. In contrast, `ReadOnlyChromaAdapter` only issues pure read queries (`SELECT id, vector, metadata FROM embeddings_queue`), which succeed unconditionally.

---

## 5. Summary of Validation Artifacts

All validation telemetry has been recorded in `experiments/phase9_5_readonly_remediation/remediation_telemetry.json` with full audit timestamps, environment details, pre/post hashes, and query results.
