# NexusCTI Phase 9.1 — Leakage-Audit Reproducibility Report

**Document Version:** 1.0 (Preflight Independent Audit)  
**Date:** 2026-10-11  
**Experiment Root:** `experiments/phase9_1_preflight_audit_20261011_023000/`  
**Prior Protocol Audited:** `experiments/phase9_benchmark_preparation_20261011_020400/leakage_audit_report.md`

---

## Executive Summary

Audit C conducts a comprehensive, line-by-line code trace and empirical reproducibility analysis of the multi-tier leakage audit performed in Phase 9.

### Key Audit Findings:
1. **The 0 / 1,428 Metric Discrepancy:**
   - The Phase 9 report claimed: *"Total unique training tokens: 1,428 unique IOCs. Audit Result: 0 / 1,428 matching indicators (Passed)"*.
   - **Investigation Result:** This specific count of 1,428 was **NOT REPRODUCIBLE** from `run_phase9_prep.py`. The Phase 9 script attempted to extract graph nodes using `g_meta.get("nodes", [])`, but `graph_metadata.json` actually stores nodes under `"node_mappings"`. Additionally, it attempted to extract report narratives using `c.get("content", "")`, but raw report JSON files store narratives under `"narrative"`. As a result, the Phase 9 script extracted 0 items and hardcoded/asserted the literal `1,428` in the markdown documentation.
2. **True Independent Leakage Verification:**
   - Correcting the extraction logic to parse `node_mappings` in `graph_metadata.json` and `triples` + `narrative` in `data/raw_reports/` yields:
     * **53 unique graph nodes** across 6 entity types (9 IPs, 10 domains, 12 malware, 6 CVEs, 6 attack groups, 10 techniques).
     * **61 unique technical indicator tokens** across graph nodes and report triples.
     * **390 unique words** across all training narratives.
   - When matching against the 130 eligible benchmark campaigns (Task A: 100, Task B: 30), the true exact indicator overlap is **strictly 0**.
   - **Verdict:** While the Phase 9 *reporting* of the 1,428 denominator was unverified and flawed, the substantive conclusion of **zero indicator contamination is VERIFIED**.
3. **Clarification of "Full DB Quarantine":**
   - The term "Full DB Quarantine" in Phase 9 markdown is misleading. It does **not** mean the ChromaDB vector database is taken offline or emptied.
   - It means that **test campaign reports were quarantined from ingestion**: only the 6 baseline training reports (7 text chunks) are present in ChromaDB, while zero test reports were indexed.

---

## 1. Exact Input Datasets and Indicator Counts

```
+---------------------------------------------------------------------------------------------------------------+
| AUDIT C: TRAINING EVIDENCE VERSUS TEST CANDIDATE BENCHMARK REGISTRY                                           |
+--------------------------+---------------------------------------------------+--------------------------------+
| Component                | Source File / Path                                | Verified Entity Count          |
+--------------------------+---------------------------------------------------+--------------------------------+
| Graph Node Mappings      | cyber_attribution_engine/data/processed_graph/    | 53 canonical nodes             |
|                          | graph_metadata.json                               | (9 IP, 10 Dom, 12 Mal, 6 CVE,  |
|                          |                                                   |  6 Groups, 10 Techniques)      |
| Heterogeneous Graph      | cyber_attribution_engine/data/processed_graph/    | 6 relations, 53 total nodes    |
|                          | hetero_graph.pt                                   |                                |
| Training CTI Reports     | cyber_attribution_engine/data/raw_reports/        | 6 JSON advisories,             |
|                          | *.json                                            | 61 technical indicators        |
| ChromaDB Vector Store    | cyber_attribution_engine/data/chroma_db/          | 1 collection (cti_threat_rpts),|
|                          | chroma.sqlite3                                    | 7 text chunks, 49 metadata k/v |
| Task A Eligible Cases    | candidate_campaign_manifest.csv                   | 100 canonical campaigns        |
| Task B Eligible Cases    | candidate_campaign_manifest.csv                   | 30 canonical campaigns         |
| Development Partition    | candidate_campaign_manifest.csv                   | 15 calibration campaigns       |
| Collapsed Duplicate Rpts | candidate_campaign_manifest.csv                   | 10 syndicated vendor reports   |
| Excluded Candidates      | candidate_campaign_manifest.csv                   | 10 contaminated / weak reports |
+--------------------------+---------------------------------------------------+--------------------------------+
```

---

## 2. Normalization Rules & Pipeline Specifications

To verify indicator matching, all strings undergo deterministic canonicalization:
1. **Network IPv4 Addresses:**
   - Stripped of CIDR subnet masks, whitespace, and bracket obfuscation (e.g., `185.225.17[.]42` $\to$ `185.225.17.42`).
   - Validated against octet ranges $0 \le \text{octet} \le 255$.
2. **Domain Names & Hostnames:**
   - Lowercased, stripped of trailing dots and protocol prefixes (`hxxps://` $\to$ `https://`, stripped to FQDN).
3. **Cryptographic Hashes:**
   - Lowercased, stripped of whitespace. Hexadecimal length checks (MD5: 32 chars, SHA-1: 40 chars, SHA-256: 64 chars).
4. **MITRE ATT&CK Techniques:**
   - Normalized to canonical `TXXXX` or `TXXXX.XXX` format (e.g., `T1195.002`).

---

## 3. Deconstruction of the 0 / 1,428 Claim

In Phase 9 `run_phase9_prep.py` (lines 378–432), the leakage audit was implemented as follows:

```python
# Lines 378-386 in run_phase9_prep.py:
training_graph_path = ENGINE_ROOT / "data" / "processed_graph" / "graph_metadata.json"
training_iocs = set()
if training_graph_path.exists():
    with open(training_graph_path, "r", encoding="utf-8") as f:
        g_meta = json.load(f)
        for node in g_meta.get("nodes", []):  # BUG: key "nodes" does not exist!
            if node.get("type") in ["IOC", "IP", "Domain", "Hash", "Malware"]:
                training_iocs.add(str(node.get("id")).lower().strip())
                training_iocs.add(str(node.get("value", "")).lower().strip())
```

### Forensic Deficiencies Identified:
1. **Key Mismatch in Graph Metadata:** `graph_metadata.json` does not have a top-level `"nodes"` key. Its top-level keys are: `['node_mappings', 'reverse_mappings', 'actor_metadata', 'edge_relations', 'num_triples']`. As a result, `g_meta.get("nodes", [])` returned an empty list (`[]`).
2. **Key Mismatch in Raw Reports:** In lines 408–410, `run_phase9_prep.py` queried `c.get("content", "") + " " + c.get("title", "")`. In the actual JSON schemas, narratives are keyed as `"narrative"`, not `"content"`. As a result, `training_texts` was populated with blank strings.
3. **Asserted Literal:** The figure `1,428` appeared nowhere in the script's calculations. It was manually authored in `leakage_audit_report.md` as an unverified assertion.

### Independent Rectification:
When parsed using the actual dictionary schema, our independent audit extracted:
- **53 nodes** from `node_mappings`
- **61 technical tokens** across graph mappings and report triples
- **130 observable tokens** from Task A and Task B candidate passages
- **Intersection:** $\text{Training IOCs} \cap \text{Test IOCs} = \emptyset$ (**0 matches**).

**Verdict on Indicator Contamination:** **VERIFIED (Zero Overlap).**  
**Verdict on Phase 9 Audit Reproducibility:** **NOT VERIFIED (Asserted Literal & Broken Extraction Logic).**

---

## 4. Multi-Vendor Deduplication, Aliases, & Syndication

A critical vulnerability in threat intelligence benchmarking is **pseudo-replication** caused by syndicated reporting across multiple security vendors (e.g., CISA, Microsoft, Mandiant, and ESET publishing separate advisories on the exact same intrusion campaign).

### 4.1 Collapsed Duplicate Reports
Phase 9 identified and collapsed 10 syndicated reports into their canonical primary campaigns:
- `mandiant_drovorub_dup` collapsed into `cmp_actor_apt28_ext_02`
- `msrc_teamcity_dup` collapsed into `cmp_actor_apt29_ext_01`
- `fbi_flash_applejeus_dup` collapsed into `cmp_actor_lazarus_ext_01`
- `cert_ua_industroyer2_dup` collapsed into `cmp_actor_sandworm_ext_01`
- `microsoft_volt_typhoon_dup` collapsed into `cmp_actor_volt_typhoon_ext_01`
- (and 5 others across CISA, NCSC, and Mandiant).

### 4.2 Threat Actor Alias Handling
- All candidate campaigns record full vendor alias clusters (e.g., *APT28 / Forest Blizzard / Fancy Bear / GRU 26165*).
- Candidate passages were audited to ensure that inference query prompts do **not** include these alias strings.
- **Verdict:** **VERIFIED (Syndications collapsed; prompt inputs blind).**

---

## 5. Textual Overlap & ChromaDB Retrieval Quarantine

We audited the exact contents of ChromaDB (`cyber_attribution_engine/data/chroma_db/chroma.sqlite3`):
- Total chunks in collection `cti_threat_reports`: **7 chunks**.
- Sources:
  * Chunk 0-1: `cisa_aa20_352a_apt29_solarwinds.json` (APT29)
  * Chunk 2: `cisa_aa22_054a_sandworm_industroyer.json` (Sandworm)
  * Chunk 3: `cisa_aa22_110a_lazarus_applejeus.json` (Lazarus)
  * Chunk 4: `cisa_aa23_074a_apt28_fancybear.json` (APT28)
  * Chunk 5: `cisa_aa24_038a_volt_typhoon.json` (Volt Typhoon)
  * Chunk 6: `mandiant_m_trends_fin7.json` (FIN7)
- **Overlap with Test Set:** All 130 test campaign narratives were compared against the 7 ChromaDB chunks using exact substring matching and 3-gram Jaccard similarity. Maximum observed Jaccard similarity was $0.042$ (representing shared security domain terms like *"command and control"*).
- **Quarantine Scope Clarification:** "Full DB Quarantine" signifies that the retrieval index was **strictly quarantined from test set contamination**, containing solely the 6 historical training documents.

---

## 6. Summary Audit Determination

| Leakage Dimension | Claimed Metric | Verified Metric | Audit Status |
|:---|:---:|:---:|:---:|
| **IOC Overlap Count** | 0 / 1,428 | 0 / 61 (True Tokens) | **VERIFIED (Zero Overlap)** |
| **Audit Script Logic** | Reported Automated | Buggy (Queried wrong keys) | **FAILED (Script Logic Discrepancy)** |
| **ChromaDB Text Leakage** | 0.0% Overlap | 0.0% Overlap (7 chunks) | **VERIFIED** |
| **Graph Node Encoding** | 0 test nodes in graph | 0 test nodes (53 total nodes) | **VERIFIED** |
| **Prompt Label Stripping** | Technical observables only | Stripped of actor/alias tags | **VERIFIED** |
| **Deduplication / Syndication** | 10 collapsed reports | 10 canonical collapsed units | **VERIFIED** |
