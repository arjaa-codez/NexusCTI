# NexusCTI Phase 9.6 — Protocol Amendment Proposal 3

**Document Title:** Prospective Protocol Amendment 3: Master Database Immutability & Disposable Runtime Snapshot Lifecycle  
**Date:** 2026-10-11  
**Project Root:** `C:\Users\Arjaa Chatterjee\OneDrive\Desktop\NexusCTI`  
**Current Protocol Version:** NexusCTI Preregistered Evaluation Protocol v2.1-amended (Phase 9.3)  
**Proposed Protocol Version:** NexusCTI Preregistered Evaluation Protocol v2.2-amended  
**Governing Gate:** Pre-Phase 10 Protocol Reconciliation Gate  

---

## 1. Context and Need for Formal Amendment

In the Phase 9.3 Preregistration Protocol ([phase9_3_final_protocol.md](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_3_final_authorization_20261011/phase9_3_final_protocol.md)) and its supporting runtime audit ([runtime_and_artifact_integrity.md](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_3_final_authorization_20261011/runtime_and_artifact_integrity.md), Section 3.1), the operational mandate for database access was recorded as:
> *"Protocol Mandate: The prospective evaluation runner must connect to ChromaDB exclusively using the ?mode=ro URI flag."*

In Phase 9.4 and Phase 9.5, technical auditing established that:
1. `chromadb.PersistentClient` (version 1.5.9) does not accept or pass the `?mode=ro` URI flag.
2. ChromaDB unconditionally executes migration table checks and lock acquisitions on startup.
3. Denying write permissions at the filesystem level (`chmod 0o444`) causes ChromaDB to crash on startup with SQLite error code 8.

Therefore, the active inference database **cannot operate natively in a physically write-denied configuration**. To resolve this conflict transparently without compromising scientific integrity or concealing writes, a formal prospective amendment is required before Phase 10 blind evaluation can be authorized.

---

## 2. Interpretation Reconciled: Physical Active Read-Only vs Master Artifact Immutability

The existing protocol wording conflated two distinct requirements:
- **Requirement A:** The active database file opened by the running process must be physically read-only at the OS level throughout execution.
- **Requirement B:** The authoritative frozen knowledge base artifact must remain strictly immutable and untampered, guaranteeing zero data leakage or retrospective tuning.

**Resolution:**
Requirement A is an implementation-specific mechanism that is technically impossible in ChromaDB 1.5.9 without rewriting the retrieval engine. Requirement B is the true scientific desideratum. 

This amendment replaces the impossible Requirement A with a rigorous, auditable **Disposable Snapshot Lifecycle Architecture (Option C)** that strictly enforces Requirement B.

---

## 3. Formal Terms of Amendment 3

### 3.1 Authoritative Frozen Master Artifact
- **Authoritative Master File:** `cyber_attribution_engine/data/chroma_db/chroma.sqlite3`
- **Master Directory:** `cyber_attribution_engine/data/chroma_db/`
- **Pre-Evaluation Binary SHA-256:** `a93e9561add3b86c064642d0fc6b9dc21222e6322ea91e03d233e76060bfb8d3`
- **Canonical Content SHA-256:** `668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7`
- **Immutability Contract:** The authoritative master file must remain on disk with OS read-only protections enabled. It must **never** be opened directly by a write-capable process during inference.

### 3.2 Permitted vs Prohibited Mutations
1. **Permitted Mutations (Disposable Snapshot Only):**
   - SQLite internal connection metadata writes: incrementing the 4-byte `file_change_counter` (bytes 24–27).
   - Temporary creation and automatic deletion of SQLite rollback journal files (`chroma.sqlite3-journal`) or write-ahead log files (`chroma.sqlite3-wal`) within the temporary snapshot directory.
2. **Strictly Prohibited Mutations (All Environments):**
   - Any modification, insertion, deletion, or truncation of rows in tables `collections`, `embeddings`, `embedding_metadata`, or `embeddings_queue`.
   - Any change to the canonical content hash (`668d0776c609e3253143dd4764652ec4e121e082247458e18699a5e63a2faee7`).
   - Any copy or write-back from the runtime snapshot to the frozen master database.

### 3.3 Mandatory Disposable Snapshot Lifecycle Procedure
The Phase 10 evaluation harness must execute inference strictly according to the following 6-step lifecycle:

```
[Master DB: Read-Only]
       │
       ▼ (Step 1: Pre-Run Verification)
Verify Master Hash == a93e9561... & Content == 668d0776...
       │
       ▼ (Step 2: Ephemeral Copy)
Copy Master -> Ephemeral Scratch TempDir
       │
       ▼ (Step 3: Native Inference)
ThreatRAGEngine(persist_directory=TempDir) runs blind test cases
       │
       ▼ (Step 4: Snapshot Audit)
Verify Snapshot Content Hash == 668d0776...
       │
       ▼ (Step 5: Ephemeral Destruction)
Destroy TempDir (Purge all snapshot and sidecar files)
       │
       ▼ (Step 6: Post-Run Verification)
Re-Verify Master Hash == a93e9561... & Content == 668d0776... (Delta = 0)
```

### 3.4 Snapshot Failure and Exception Auditing
- If snapshot creation fails, evaluation must abort immediately before unblinding any test cases.
- If post-run verification reveals that the master database binary hash or content hash mutated by even 1 byte, the evaluation is automatically declared **COMPROMISED AND INVALID**.
- Incomplete destruction of the temporary directory triggers an audit flag, requiring manual inspection before scoring.

---

## 4. Preservation of Locked Statistical Endpoint and Scoring Rules

This amendment is strictly restricted to runtime storage lifecycle governance. All scientific, statistical, and evaluation parameters registered in Phase 9.3 remain **100% FROZEN AND UNALTERED**:

- **Primary Endpoint:** Paired Top-3 accuracy on 100 closed-set Task A campaigns (Full Hybrid minus Retrieval-only).
- **Primary Statistical Test:** Exact two-sided McNemar test on discordant pairs ($b$ vs $c$) with $\alpha = 0.05$.
- **Directional Success Condition:** Observed paired risk difference $\Delta > 0$ ($\text{Acc}_{\text{Hybrid}} > \text{Acc}_{\text{Retrieval}}$).
- **Secondary Endpoints:** Top-1 paired accuracy, MRR difference, open-set abstention AUROC (Task B, 30 cases).
- **Frozen Models:** GNN model weights (`gnn_weights.pt`), graph schema (`nexuscti_graph.json`), dense encoder (`all-MiniLM-L6-v2`), and fusion weights remain completely unchanged.

---

## 5. Proposed Governance Status

Upon formal approval by the evaluation review authority, this proposal will be ratified as **Amendment 3** to the preregistered evaluation protocol, advancing the protocol version to **NexusCTI Protocol v2.2-amended**, enabling blind-evaluation authorization.
