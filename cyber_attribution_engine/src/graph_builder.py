r"""Graph Builder Module for Cyber-Threat Attribution Engine.
Ingests:
1. Authentic CTI STIX 2.1 bundles (infrastructural pivots: IP, domain, malware, CVE).
2. Official MITRE ATT&CK Enterprise STIX 2.1 dataset (191 APT intrusion-sets, 828 malware/tools, 858 techniques, and relationships).
3. Official CISA Known Exploited Vulnerabilities (KEV) catalog (1,739 exploited CVEs).

Constructs PyG HeteroData with exact node types:
- ip, domain, malware, cve, attack_group, technique
And directed edge types:
- ('ip', 'resolves_to', 'domain')
- ('domain', 'drops', 'malware')
- ('cve', 'exploited_by', 'malware')
- ('malware', 'attributed_to', 'attack_group')
- ('attack_group', 'uses', 'technique')
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import torch
from torch_geometric.data import HeteroData

NODE_TYPES = ["ip", "domain", "malware", "cve", "attack_group", "technique"]

EDGE_RELATIONS = [
    ("ip", "resolves_to", "domain"),
    ("domain", "drops", "malware"),
    ("cve", "exploited_by", "malware"),
    ("malware", "attributed_to", "attack_group"),
    ("attack_group", "uses", "technique"),
]


class ThreatGraphBuilder:
    """Builds and serializes PyTorch Geometric HeteroData from authentic CTI datasets."""

    def __init__(
        self,
        raw_reports_dir: str | Path,
        processed_dir: str | Path,
        external_dir: Optional[str | Path] = None,
    ):
        self.raw_reports_dir = Path(raw_reports_dir)
        self.processed_dir = Path(processed_dir)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.external_dir = Path(external_dir) if external_dir else self.raw_reports_dir.parent / "external_datasets"

        self.node_mappings: Dict[str, Dict[str, int]] = {nt: {} for nt in NODE_TYPES}
        self.reverse_mappings: Dict[str, Dict[int, str]] = {nt: {} for nt in NODE_TYPES}
        self.edge_records: Dict[Tuple[str, str, str], List[Tuple[int, int]]] = {
            rel: [] for rel in EDGE_RELATIONS
        }
        self.edge_sets: Dict[Tuple[str, str, str], set] = {
            rel: set() for rel in EDGE_RELATIONS
        }
        self.triples_raw: List[Dict[str, Any]] = []
        self.actor_metadata: Dict[str, Dict[str, Any]] = {}

        # STIX ID mapping table
        self.stix_id_to_name: Dict[str, Tuple[str, str]] = {}  # stix_id -> (node_type, name)

    def get_or_create_node_id(self, node_type: str, name: str) -> int:
        clean_name = str(name).strip()
        if not clean_name:
            clean_name = f"unknown_{node_type}"

        if clean_name not in self.node_mappings[node_type]:
            new_id = len(self.node_mappings[node_type])
            self.node_mappings[node_type][clean_name] = new_id
            self.reverse_mappings[node_type][new_id] = clean_name
        return self.node_mappings[node_type][clean_name]

    def add_edge(self, s_type: str, rel: str, t_type: str, s_val: str, t_val: str) -> None:
        rel_key = (s_type, rel, t_type)
        if rel_key in self.edge_records:
            s_id = self.get_or_create_node_id(s_type, s_val)
            t_id = self.get_or_create_node_id(t_type, t_val)
            edge_tuple = (s_id, t_id)
            if edge_tuple not in self.edge_sets[rel_key]:
                self.edge_sets[rel_key].add(edge_tuple)
                self.edge_records[rel_key].append(edge_tuple)
                self.triples_raw.append({
                    "source_type": s_type,
                    "source": s_val,
                    "relation": rel,
                    "target_type": t_type,
                    "target": t_val,
                })

    def ingest_raw_advisories(self) -> None:
        """Parse all authentic STIX JSON advisories in raw_reports_dir."""
        report_files = sorted(self.raw_reports_dir.glob("*.json"))
        for rf in report_files:
            with open(rf, "r", encoding="utf-8") as f:
                data = json.load(f)

            threat_actor = data.get("threat_actor")
            if threat_actor:
                self.actor_metadata[threat_actor] = {
                    "aliases": data.get("aliases", []),
                    "origin": data.get("origin", "Unknown"),
                    "confidence_base": data.get("confidence_base", 0.90),
                    "report_id": data.get("id"),
                    "narrative": data.get("narrative", ""),
                }

            triples = data.get("triples", [])
            for t in triples:
                self.add_edge(
                    t["source_type"],
                    t["relation"],
                    t["target_type"],
                    t["source"],
                    t["target"],
                )

    def ingest_mitre_attack(self) -> None:
        """Parse official MITRE ATT&CK Enterprise STIX 2.1 dataset."""
        mitre_file = self.external_dir / "enterprise_attack.json"
        if not mitre_file.exists():
            print(f"[GraphBuilder] MITRE ATT&CK dataset not found at {mitre_file}, skipping.")
            return

        print(f"[GraphBuilder] Parsing official MITRE ATT&CK dataset ({mitre_file.stat().st_size / (1024*1024):.1f} MB)...")
        with open(mitre_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        objects = data.get("objects", [])

        # Step 1: Index Intrusion Sets (Attack Groups)
        for obj in objects:
            obj_type = obj.get("type")
            stix_id = obj.get("id")
            if not stix_id or obj.get("revoked", False):
                continue

            name = obj.get("name", "").strip()
            if not name:
                continue

            if obj_type == "intrusion-set":
                aliases = obj.get("aliases", [])
                description = obj.get("description", "")
                self.stix_id_to_name[stix_id] = ("attack_group", name)
                self.get_or_create_node_id("attack_group", name)

                # Store metadata
                if name not in self.actor_metadata:
                    self.actor_metadata[name] = {
                        "aliases": aliases,
                        "origin": "State-Sponsored / Nation-State APT",
                        "confidence_base": 0.95,
                        "report_id": stix_id,
                        "narrative": description[:1000] if description else "",
                    }

            elif obj_type in ("malware", "tool"):
                self.stix_id_to_name[stix_id] = ("malware", name)
                self.get_or_create_node_id("malware", name)

            elif obj_type == "attack-pattern":
                ext_refs = obj.get("external_references", [])
                tech_id = name
                for ref in ext_refs:
                    if ref.get("source_name") == "mitre-attack":
                        tech_id = ref.get("external_id", name)
                        break
                self.stix_id_to_name[stix_id] = ("technique", tech_id)
                self.get_or_create_node_id("technique", tech_id)

        # Step 2: Index Relationships
        rel_count = 0
        for obj in objects:
            if obj.get("type") != "relationship" or obj.get("revoked", False):
                continue

            s_ref = obj.get("source_ref")
            t_ref = obj.get("target_ref")
            rel_type = obj.get("relationship_type")

            if s_ref in self.stix_id_to_name and t_ref in self.stix_id_to_name:
                s_type, s_name = self.stix_id_to_name[s_ref]
                t_type, t_name = self.stix_id_to_name[t_ref]

                # malware -> attributed_to -> attack_group
                # In MITRE STIX, it can be intrusion-set uses malware OR malware attributed-to intrusion-set
                if s_type == "attack_group" and t_type == "malware" and rel_type == "uses":
                    # Directional schema: malware is attributed_to attack_group
                    self.add_edge("malware", "attributed_to", "attack_group", t_name, s_name)
                    rel_count += 1
                elif s_type == "attack_group" and t_type == "technique" and rel_type == "uses":
                    self.add_edge("attack_group", "uses", "technique", s_name, t_name)
                    rel_count += 1
                elif s_type == "malware" and t_type == "technique" and rel_type == "uses":
                    # malware uses technique; we can link to technique
                    pass

        print(f"[GraphBuilder] Integrated MITRE ATT&CK: {rel_count} authentic relational edges added.")

    def ingest_cisa_kev(self) -> None:
        """Parse official CISA Known Exploited Vulnerabilities (KEV) catalog."""
        kev_file = self.external_dir / "cisa_kev.json"
        if not kev_file.exists():
            return

        print(f"[GraphBuilder] Ingesting CISA Known Exploited Vulnerabilities catalog...")
        with open(kev_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        vulnerabilities = data.get("vulnerabilities", [])
        cve_count = 0
        for v in vulnerabilities:
            cve_id = v.get("cveID", "").strip()
            if not cve_id:
                continue

            self.get_or_create_node_id("cve", cve_id)
            cve_count += 1

            # Check if notes or description associate this CVE with known malware/threat actors
            desc = (v.get("shortDescription", "") + " " + v.get("notes", "")).lower()
            known_malware = list(self.node_mappings["malware"].keys())
            for mw in known_malware[:100]:
                if len(mw) > 4 and mw.lower() in desc:
                    self.add_edge("cve", "exploited_by", "malware", cve_id, mw)

        print(f"[GraphBuilder] Integrated CISA KEV: {cve_count} verified exploited CVEs indexed.")

    def build_heterodata(self, feature_dim: int = 64) -> HeteroData:
        """Constructs and returns the PyG HeteroData object."""
        data = HeteroData()

        # Build node indices
        for nt in NODE_TYPES:
            count = len(self.node_mappings[nt])
            if count == 0:
                count = 1
                self.get_or_create_node_id(nt, f"empty_{nt}")

            data[nt].num_nodes = count
            data[nt].node_id = torch.arange(count, dtype=torch.long)
            # Embedding initialization
            data[nt].x = torch.randn(count, feature_dim)

        # Build edge indexes and incoming degree normalization constants c_{v, r}
        for rel_key, edges in self.edge_records.items():
            s_type, rel_name, t_type = rel_key
            if edges:
                src_list, dst_list = zip(*edges)
                edge_index = torch.tensor([src_list, dst_list], dtype=torch.long)
            else:
                edge_index = torch.empty((2, 0), dtype=torch.long)

            data[s_type, rel_name, t_type].edge_index = edge_index

            # Calculate incoming degree normalization: c_{v,r} = |N_r(v)|
            target_node_count = data[t_type].num_nodes
            in_degrees = torch.zeros(target_node_count, dtype=torch.float)
            if edge_index.shape[1] > 0:
                for dst_node in edge_index[1]:
                    in_degrees[dst_node.item()] += 1.0
            data[s_type, rel_name, t_type].c_vr = torch.clamp(in_degrees, min=1.0)

        return data

    def save(self, data: HeteroData, filename: str = "hetero_graph.pt") -> Path:
        """Persists the HeteroData and node registry metadata."""
        out_path = self.processed_dir / filename
        meta_path = self.processed_dir / "graph_metadata.json"

        torch.save(data, out_path)

        metadata = {
            "node_mappings": self.node_mappings,
            "reverse_mappings": self.reverse_mappings,
            "actor_metadata": self.actor_metadata,
            "edge_relations": [list(k) for k in EDGE_RELATIONS],
            "num_triples": len(self.triples_raw),
        }
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        return out_path


def build_and_save_graph(
    raw_dir: str = "cyber_attribution_engine/data/raw_reports",
    processed_dir: str = "cyber_attribution_engine/data/processed_graph",
    external_dir: str = "cyber_attribution_engine/data/external_datasets",
) -> Tuple[HeteroData, Dict[str, Any]]:
    """Builds and serializes the complete real-world threat knowledge graph."""
    builder = ThreatGraphBuilder(raw_dir, processed_dir, external_dir)
    builder.ingest_raw_advisories()
    builder.ingest_mitre_attack()
    builder.ingest_cisa_kev()

    data = builder.build_heterodata()
    saved_path = builder.save(data)

    print("=" * 65)
    print(f"[GraphBuilder] Serialized HeteroData saved to: {saved_path}")
    print("[GraphBuilder] Node Counts:")
    for nt in NODE_TYPES:
        print(f"  • {nt:<15}: {len(builder.node_mappings[nt]):>5} nodes")
    print(f"[GraphBuilder] Total Triples: {len(builder.triples_raw)}")
    print("=" * 65)
    return data, builder.actor_metadata


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    build_and_save_graph()
