"""
Graph Trail Extractor: Discovers and scores multi-hop structural reasoning chains
connecting unknown or novel IOCs to candidate threat actors.
"""

from typing import List, Dict, Any, Optional
import networkx as nx
from pydantic import BaseModel, Field

from .graph_builder import ThreatKnowledgeGraph


class TrailHop(BaseModel):
    step: int
    source_id: str
    source_name: str
    source_type: str
    relation: str
    target_id: str
    target_name: str
    target_type: str
    citation: str = ""
    rationale: str = ""


class GraphTrail(BaseModel):
    source_ioc_id: str
    source_ioc_name: str
    target_actor_id: str
    target_actor_name: str
    hops: List[TrailHop] = Field(default_factory=list)
    hop_count: int = 0
    path_confidence: float = 0.0
    chain_summary: str = ""

    def to_readable_chain(self) -> str:
        if not self.hops:
            return "No verifiable structural path discovered."
        parts = [f"[{self.hops[0].source_type}] {self.hops[0].source_name}"]
        for hop in self.hops:
            parts.append(f"--({hop.relation})--> [{hop.target_type}] {hop.target_name}")
        return " ".join(parts)


class GraphTrailExtractor:
    """
    Finds and ranks multi-hop explanatory paths through the Heterogeneous Threat Graph.
    """

    RELATION_DESCRIPTIONS = {
        "resolves_to": "DNS domain name resolution binding",
        "rev_resolves_to": "Reverse DNS IP-to-domain mapping",
        "communicates_with": "Malware C2 network communication beacon",
        "rev_communicates_with": "C2 server receiving command telemetry from malware",
        "uses": "Threat actor operational utilization of tool/malware",
        "rev_uses": "Malware family operated by threat actor",
        "executes": "Adversary execution of MITRE ATT&CK technique",
        "rev_executes": "ATT&CK technique associated with threat actor",
        "targets": "Adversary active targeting of vulnerability CVE",
        "rev_targets": "Vulnerability exploited in campaigns by threat actor",
        "shares_infra": "Co-located hosting, ASN subnet, or shared SSL certificate",
        "rev_shares_infra": "Infrastructure cluster pivot",
        "maps_to": "Malware capability mapped to MITRE TTP",
        "exploits": "Malware automated weaponization of CVE",
    }

    def __init__(self, tkg: ThreatKnowledgeGraph):
        self.tkg = tkg

    def extract_best_trail(
        self,
        source_id: str,
        actor_id: str,
        max_hops: int = 5
    ) -> Optional[GraphTrail]:
        """
        Extracts the most structurally sound multi-hop path from source IOC to the candidate Threat Actor.
        """
        if source_id not in self.tkg.nx_graph or actor_id not in self.tkg.nx_graph:
            return None

        # Search for paths in directed graph first, fallback to undirected if reverse relations needed
        try:
            all_paths = list(nx.all_simple_paths(
                self.tkg.nx_graph,
                source=source_id,
                target=actor_id,
                cutoff=max_hops
            ))
        except Exception:
            all_paths = []

        if not all_paths:
            # Try path from actor to source (and reverse it)
            try:
                rev_paths = list(nx.all_simple_paths(
                    self.tkg.nx_graph,
                    source=actor_id,
                    target=source_id,
                    cutoff=max_hops
                ))
                all_paths = [list(reversed(p)) for p in rev_paths]
            except Exception:
                all_paths = []

        if not all_paths:
            return None

        # Score paths based on hop length (parsimony) and edge confidence
        best_path = None
        best_score = -1.0
        best_hops: List[TrailHop] = []

        for path in all_paths:
            hops: List[TrailHop] = []
            path_conf = 1.0

            for i in range(len(path) - 1):
                u = path[i]
                v = path[i + 1]

                # Get edge data
                edge_data = self.tkg.nx_graph.get_edge_data(u, v)
                if not edge_data:
                    # check reverse
                    edge_data = self.tkg.nx_graph.get_edge_data(v, u)

                rel_key = list(edge_data.keys())[0] if edge_data else "associated_with"
                edge_info = edge_data[rel_key] if edge_data else {}
                rel_name = edge_info.get("rel_type", rel_key)
                citation = edge_info.get("citation", "Knowledge Graph Topology")

                u_node = self.tkg.node_dict.get(u)
                v_node = self.tkg.node_dict.get(v)

                rationale = self.RELATION_DESCRIPTIONS.get(
                    rel_name, f"Structural link '{rel_name}' between entities"
                )

                hops.append(TrailHop(
                    step=i + 1,
                    source_id=u,
                    source_name=u_node.name if u_node else u,
                    source_type=u_node.type.value if u_node else "Unknown",
                    relation=rel_name,
                    target_id=v,
                    target_name=v_node.name if v_node else v,
                    target_type=v_node.type.value if v_node else "Unknown",
                    citation=citation,
                    rationale=rationale
                ))
                path_conf *= 0.92  # Slight decay per hop

            # Scoring: decay with length, higher for shorter verifiable chains
            score = path_conf / (len(path) ** 0.5)
            if score > best_score:
                best_score = score
                best_path = path
                best_hops = hops

        if not best_hops:
            return None

        source_node = self.tkg.node_dict.get(source_id)
        actor_node = self.tkg.node_dict.get(actor_id)

        trail = GraphTrail(
            source_ioc_id=source_id,
            source_ioc_name=source_node.name if source_node else source_id,
            target_actor_id=actor_id,
            target_actor_name=actor_node.name if actor_node else actor_id,
            hops=best_hops,
            hop_count=len(best_hops),
            path_confidence=round(best_score, 4),
            chain_summary=f"Discovered {len(best_hops)}-hop structural trail linking '{source_node.name if source_node else source_id}' to '{actor_node.name if actor_node else actor_id}'."
        )
        return trail
