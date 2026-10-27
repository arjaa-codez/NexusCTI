# Deep GNN Supervision & Leakage Trace

**Experiment ID:** `phase4_leakage_and_generalization_20261010_224500`  
**Date:** October 10, 2026  
**Auditor:** Principal AI Systems & Scientific Integrity Auditor  
**Module Audited:** `nexuscti/gnn/trainer.py` (`GNNAttributionTrainer._prepare_training_labels`) and `knowledge_base.py`.

---

## 1. Mathematical & Algorithmic Formulation of Training Label Derivation

In `nexuscti/gnn/trainer.py`, the training routine does not rely on externally partitioned train/test splits. Instead, supervision targets are derived directly from the complete knowledge graph via **graph reachability**:

```python
for a_local_idx, a_node_idx in enumerate(self.tkg.actor_indices):
    a_node_id = self.tkg.idx_to_node_id[a_node_idx]

    # Find all nodes reachable from this actor in directed / undirected graph within 3 hops
    lengths = nx.single_source_shortest_path_length(self.tkg.nx_graph, a_node_id, cutoff=3)
    for target_id, dist in lengths.items():
        if dist > 0:  # Exclude self
            target_idx = self.tkg.node_id_to_idx[target_id]
            labeled_indices.append(target_idx)
            labels.append(a_local_idx)
```

### The Mechanism of Supervision Leakage:
1. **Node Classification Target Injection:**
   Every entity node $u$ that is within 3 hops of threat actor $A_i$ in `nx_graph` is assigned the ground-truth label $y_u = A_i$.
2. **Loss Function:**
   The training loop optimizes Cross-Entropy loss over all labeled indices:
   $$\mathcal{L}_{\text{CE}} = - \sum_{u \in \text{labeled\_indices}} \log \text{Softmax}(\text{Logits}_u)[y_u]$$
3. **Implication:**
   When the GNN trains, the neural classification head is **directly optimized to predict the ground-truth actor for those specific node indices**.

---

## 2. Case-by-Case Supervision Trace Across the 12 Benchmark Indicators

We mapped each of the 12 benchmark test cases to its underlying knowledge graph node, calculated its hop distance to the ground truth actor in `self.tkg.nx_graph`, and verified whether its index was included in `labeled_indices`:

| Case ID | Anchor Indicator | Graph Node ID | Hop Distance to Ground-Truth Actor | Included in GNN Training Supervision? | Supervision Label Assigned | Leakage Classification |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| `test_case_01` | `avsvmcloud[.]com` | `ioc_domain_avsvmcloud` | 2 hops (`APT29 -> SUNBURST -> avsvmcloud`) | **YES** | `actor_apt29` | **CONFIRMED SUPERVISION LEAKAGE** |
| `test_case_02` | `Industroyer (CrashOverride)` | `mal_industroyer` | 1 hop (`Sandworm -> Industroyer`) | **YES** | `actor_sandworm` | **CONFIRMED SUPERVISION LEAKAGE** |
| `test_case_03` | `secure-crypto-wallet[.]org`| `ioc_domain_crypto_wallet` | 2 hops (`Lazarus -> AppleJeus -> wallet`) | **YES** | `actor_lazarus` | **CONFIRMED SUPERVISION LEAKAGE** |
| `test_case_04` | `a3d9e84b...` (Delphi Hash) | `ioc_hash_zebrocy_bin` | 2 hops (`APT28 -> Zebrocy -> hash`) | **YES** | `actor_apt28` | **CONFIRMED SUPERVISION LEAKAGE** |
| `test_case_05` | `f441c21d...` (Griffon JS) | `ioc_hash_griffon_js` | 2 hops (`FIN7 -> Griffon -> hash`) | **YES** | `actor_fin7` | **CONFIRMED SUPERVISION LEAKAGE** |
| `test_case_06` | `027cc450...` (NotPetya) | `ioc_hash_notpetya_bin` | 2 hops (`Sandworm -> NotPetya -> hash`) | **YES** | `actor_sandworm` | **CONFIRMED SUPERVISION LEAKAGE** |
| `test_case_07` | `185.225.17.42` (SolarWinds IP) | `ioc_ip_185_225_17_42` | 4 hops (`APT29 -> SUNBURST -> avsvmcloud -> freescan -> IP`) | **NO** | *Unsupervised* | **CLEAN (Relational Message Passing)** |
| `test_case_08` | `mail-update-service[.]net` | `ioc_domain_mail_update`| 3 hops (`APT28 -> Zebrocy -> auth-m365 -> mail-update`) | **YES** | `actor_apt28` | **CONFIRMED SUPERVISION LEAKAGE** |
| `test_case_09` | `203.0.113.88` (SOHO Proxy) | `ioc_ip_203_0_113_88` | 4 hops (`Volt Typhoon -> KV -> cisco-mesh -> IP198 -> IP203`)| **NO** | *Unsupervised* | **CLEAN (Relational Message Passing)** |
| `test_case_10` | `91.242.217.5` (Dark Subnet)| `ioc_ip_91_242_217_5` | 4 hops (`Sandworm -> BlackEnergy -> ukr-cert -> IP194 -> IP91`)| **NO** | *Unsupervised* | **CLEAN (Relational Message Passing)** |
| `test_case_11` | `175.45.176.8` (NK Border IP) | `ioc_ip_175_45_176_8` | 3 hops (`Lazarus -> AppleJeus -> wallet -> IP175`) | **YES** | `actor_lazarus` | **CONFIRMED SUPERVISION LEAKAGE** |
| `test_case_12` | `193.106.191.4` (POS Host IP)| `ioc_ip_193_106_191_4` | 3 hops (`FIN7 -> Griffon -> doc-share -> IP193`) | **YES** | `actor_fin7` | **CONFIRMED SUPERVISION LEAKAGE** |

---

## 3. Findings & Architectural Implications

1. **Quantification of Transductive Label Leakage:**
   - **9 out of 12 benchmark indicators (75.0%)** had their node indices directly supervised with the true threat actor during model training.
   - For these 9 cases, the GNN did not need to perform complex unguided inference; the classification head had explicitly memorized the node index mapping during the 120 training epochs.
2. **The 3 Genuinely Relational Multi-Hop Cases:**
   - Only **3 cases (`test_case_07`, `test_case_09`, `test_case_10`)** were outside the 3-hop cutoff (each exactly 4 hops away).
   - For these 3 cases, the model had **zero direct supervision targets on the anchor indicator**. Their correct attribution proves that RGCN message passing successfully propagates relational embeddings across intermediate infrastructure.
3. **Why Graph-Only Achieved 12/12:**
   - As proven in `verify_existing_results.py`, each threat actor's infrastructure in `knowledge_base.py` forms an isolated cluster.
   - Any path between an indicator and a non-matching threat actor must detour through shared MITRE ATT&CK TTPs (`T1566.001`, `T1078`) or CVEs, which always adds 2 to 4 additional hops.
   - Therefore, shortest-path distance $d(u, A)$ to the true actor is strictly minimal, guaranteeing a 100% Top-1 ranking under closed-world conditions.
