# NexusCTI Phase 9 — Campaign Deduplication & Canonical Unit Report

**Document Version:** 1.0 (Pre-Registration Protocol Freeze)  
**Date:** 2026-10-11  
**Experiment Root:** `experiments/phase9_benchmark_preparation_20261011_020400/`  

---

## 1. Deduplication Principles & Rationale

In cyber threat intelligence (CTI), multiple security vendors (e.g., CISA, Microsoft MSRC, Mandiant/Google, CrowdStrike, ESET) frequently publish overlapping advisories regarding the exact same operational intrusion campaign.

Counting multiple vendor reports of a single intrusion as independent test cases violates the core statistical assumption of independent and identically distributed (i.i.d.) observations, artificially inflates sample size, and induces pseudo-replication bias.

### Core Rule: Canonical Campaign Units
A **campaign unit** is defined as a bounded operational cluster of intrusions conducted by a common threat actor sharing:
1. Substantially overlapping command-and-control (C2) infrastructure or payload delivery domains.
2. Identical victimology (industry sector, target nation, or specific organization).
3. Overlapping operational objectives executed within a contiguous temporal window ($\le 90$ days).

When multiple vendor advisories or government alerts report on the same intrusion campaign, they are **collapsed into a single canonical benchmark entity**. The highest-quality, most forensically detailed report is designated as the primary reference document, and secondary reports are linked as corroborating evidence.

---

## 2. Case Flow & Deduplication Accounting

From the initial pool of 165 screened candidate records cataloged in [`candidate_campaign_manifest.csv`](file:///c:/Users/Arjaa%20Chatterjee/OneDrive/Desktop/NexusCTI/experiments/phase9_benchmark_preparation_20261011_020400/candidate_campaign_manifest.csv):

```
+--------------------------------------------------------------------------------------------------------+
| BENCHMARK CANDIDATE CASE FLOW & DEDUPLICATION ACCOUNTING                                               |
+--------------------------------------------------------------------------------+-----------------------+
| Processing Stage                                                               | Count                 |
+--------------------------------------------------------------------------------+-----------------------+
| Total Candidate Records Screened                                               | 165 candidate reports |
| - Deduplicated Syndicated Reports Collapsed into Primary Canonical Units       | -10 duplicate reports |
| - Excluded Ineligible Candidates (Contamination, Low Proof, Multi-Actor)       | -10 excluded cases    |
| - Quarantined Development Partition (Reserved for Pre-Test Checks)             | -15 dev cases         |
| ------------------------------------------------------------------------------ | --------------------- |
| Total Eligible Frozen Test Benchmark Cases                                     | 130 canonical units   |
|   * Task A: Eligible Closed-Set Attribution Cases                              | 100 canonical units   |
|   * Task B: Eligible Open-Set Novelty & Abstention Cases                       |  30 canonical units   |
+--------------------------------------------------------------------------------+-----------------------+
```

---

## 3. Explicit Collapsing Register

The following 10 syndicated/duplicate candidate reports were identified during screening and collapsed into their primary canonical campaign entities:

| Secondary Report ID | Title / Publisher | Canonical Target ID | Target Campaign Entity | Collapsing Evidence |
|:---|:---|:---|:---|:---|
| `cisa_alert_apt28_dup` | CISA Advisory on GooseEgg (CISA) | `cand_task_a_actor_apt28_01` | `cmp_actor_apt28_ext_01` | Identical CVE-2022-38028 spooler exploit and SHA-256 payload as Microsoft MSRC primary. |
| `mandiant_drovorub_dup` | Mandiant Report on Drovorub (Mandiant) | `cand_task_a_actor_apt28_02` | `cmp_actor_apt28_ext_02` | Redundant coverage of FBI/NSA Drovorub Linux kernel module; identical C2 nodes. |
| `msrc_teamcity_dup` | Microsoft Blog on SVR TeamCity (MSRC) | `cand_task_a_actor_apt29_01` | `cmp_actor_apt29_ext_01` | Identical CVE-2023-42793 exploitation timeline and victim footprint as CISA AA23-347A. |
| `ncsc_wellmess_dup` | UK NCSC Advisory on WellMess (NCSC) | `cand_task_a_actor_apt29_02` | `cmp_actor_apt29_ext_02` | Joint advisory coverage of 2020 vaccine espionage; identical payload hashes. |
| `fbi_flash_applejeus_dup` | FBI Flash on AppleJeus (FBI) | `cand_task_a_actor_lazarus_01` | `cmp_actor_lazarus_ext_01` | Syndicated coverage of cryptocurrency trading application malware; identical C2 IPs. |
| `cisa_trader_traitor_dup` | CISA Advisory on TraderTraitor (CISA) | `cand_task_a_actor_lazarus_02` | `cmp_actor_lazarus_ext_02` | Overlapping blockchain targeting attributed to Lazarus Group. |
| `cert_ua_industroyer2_dup` | CERT-UA Alert on Industroyer2 (CERT-UA) | `cand_task_a_actor_sandworm_01` | `cmp_actor_sandworm_ext_01` | Ukrainian energy grid attack telemetry identical to ESET/CISA research reports. |
| `cisa_hermetic_wiper_dup` | CISA Advisory on HermeticWiper (CISA) | `cand_task_a_actor_sandworm_02` | `cmp_actor_sandworm_ext_02` | Joint reporting describing HermeticWiper destructive drive wiper deployments. |
| `microsoft_volt_typhoon_dup`| Microsoft Alert on Volt Typhoon (MSRC) | `cand_task_a_actor_volt_typhoon_01`| `cmp_actor_volt_typhoon_ext_01`| Living-off-the-land SOHO router proxy network telemetry identical to CISA AA24-038A. |
| `mandiant_carbanak_dup` | Mandiant Analysis of FIN7 Bastion (Mandiant)| `cand_task_a_actor_fin7_01` | `cmp_actor_fin7_ext_01` | Syndicated reporting on FIN7 POS malware infrastructure. |

---

## 4. Exclusion of Ineligible Candidates

Ten candidate campaigns were formally excluded during pre-registration screening to preserve benchmark integrity:

1. `cand_excl_01` (SolarWinds Orion): **Excluded.** Contamination: Part of the base 6 training reports.
2. `cand_excl_02` (NotPetya Wiper): **Excluded.** Contamination: Hardcoded in training graph topology.
3. `cand_excl_03` (BioPass RAT): **Excluded.** Insufficient attribution evidence: Speculative vendor attribution without corroborating technical proof.
4. `cand_excl_04` (2016 DNC Exfiltration): **Excluded.** Historical baseline overlap: Overlaps training knowledge base entities.
5. `cand_excl_05` (WannaCry 2.0): **Excluded.** Contamination: Anchor IOCs present in training graph nodes.
6. `cand_excl_06` (Ivanti Zero-Day): **Excluded.** Multi-actor confounding: Overlapping activity clusters (UNC5221 / multiple state actors).
7. `cand_excl_07` (CozyDuke Phishing): **Excluded.** Incomplete telemetry: Lacks network indicators for objective evaluation.
8. `cand_excl_08` (BlackEnergy 3): **Excluded.** Historical overlap: Embedded in Capstone baseline reports.
9. `cand_excl_09` (DiceLoader SaaS): **Excluded.** Non-disjoint infrastructure: Reused C2 domain present in training graph telemetry.
10. `cand_excl_10` (VPNFilter Botnet): **Excluded.** Disputed attribution: Contested attribution between APT28 and Sandworm.

---

## 5. Summary & Verification

All 100 eligible Task A campaigns and 30 eligible Task B campaigns are confirmed to represent **strictly distinct, independent real-world operational units**. No two eligible test cases share C2 infrastructure, target campaigns, or overlapping reporting windows.
