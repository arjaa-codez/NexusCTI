"""
Dual-Layer Verifiable Attribution Brief Generator.
Formats structural Graph Trails and text-grounded Narrative Proofs
into actionable reports for SOC analysts and incident responders.
"""

from typing import Dict, Any, List
import json
from datetime import datetime

from .engine import FusionAnalysisResult


class AttributionReportGenerator:
    """
    Generates verifiable CTI briefs featuring Dual-Layer Validation:
    Layer 1: The Graph Trail
    Layer 2: The Narrative Proof
    """

    @staticmethod
    def generate_markdown_report(result: FusionAnalysisResult) -> str:
        top = result.top_actor
        if not top:
            return "# Threat Attribution Report: Inconclusive\n\nNo viable attribution candidate found."

        trail = result.graph_trail
        proofs = result.narrative_proofs

        md = []
        md.append(f"# 🛡️ NEXUS-CTI VERIFIABLE THREAT ATTRIBUTION BRIEF")
        md.append(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')} | **System:** NexusCTI Multi-Modal Engine")
        md.append(f"**Investigated Indicator:** `{result.query_ioc}`")
        md.append(f"**Attributed Threat Actor:** **{top.actor_name}**")
        md.append(f"**Confidence Verdict:** `{top.verdict}` ({top.fused_confidence * 100:.1f}%)")
        md.append(f"**Hallucination Risk Level:** `{result.hallucination_risk}`\n")
        md.append("---\n")

        # Executive Summary
        md.append("## 1. Executive Attribution Summary")
        md.append(result.synergistic_rationale)
        md.append("\n| Metric | Score | Rationale |")
        md.append("|---|---|---|")
        md.append(f"| **Fused Confidence** | **{top.fused_confidence * 100:.1f}%** | Synergistic combination of graph & text signals |")
        md.append(f"| **GNN Structural Score** | {top.structural_confidence * 100:.1f}% | Latent neighborhood similarity over multi-hop infrastructure |")
        md.append(f"| **RAG Textual Score** | {top.textual_confidence * 100:.1f}% | BM25 + Dense semantic retrieval over vendor advisories |")
        md.append(f"| **Cross-Validation Score** | {top.cross_validation_score * 100:.1f}% | Graph-text indicator overlap verification |")
        md.append(f"| **Multi-Hop Reasoning Depth** | {result.multi_hop_depth} hops | Intermediary hops traversed to link IOC to threat group |\n")

        # Layer 1: The Graph Trail
        md.append("## 2. 🔗 Layer 1: The Graph Trail (Structural Chain)")
        md.append("Defenders can verify the exact multi-hop structural pivots connecting the input indicator to the adversary's toolset and historical infrastructure:\n")

        if trail and trail.hops:
            md.append("```mermaid")
            md.append("graph LR")
            for hop in trail.hops:
                src_clean = hop.source_name.replace("[", "").replace("]", "").replace(".", "_")
                tgt_clean = hop.target_name.replace("[", "").replace("]", "").replace(".", "_")
                md.append(f'    {src_clean}["{hop.source_name} ({hop.source_type})"] -->|"{hop.relation}"| {tgt_clean}["{hop.target_name} ({hop.target_type})"]')
            md.append("```\n")

            md.append("| Step | Source Entity | Pivot Relation | Target Entity | Technical Rationale | Authoritative Topology Citation |")
            md.append("|---|---|---|---|---|---|")
            for hop in trail.hops:
                md.append(f"| {hop.step} | `{hop.source_name}` ({hop.source_type}) | **{hop.relation}** | `{hop.target_name}` ({hop.target_type}) | {hop.rationale} | *{hop.citation}* |")
            md.append("")
        else:
            md.append("> *No multi-hop graph chain resolved for this indicator. Structural confidence derived from direct cluster proximity.*")

        # Layer 2: The Narrative Proof
        md.append("\n## 3. 📜 Layer 2: The Narrative Proof (Authoritative Text Evidence)")
        md.append("Textual passages retrieved from authoritative CISA advisories, threat intelligence briefings, and vendor incident reports:\n")

        if proofs:
            for idx, proof in enumerate(proofs, 1):
                md.append(f"### Evidence Passage #{idx} — *{proof.source}* ({proof.date})")
                md.append(f"> \"{proof.relevant_text.strip()}\"\n")
                if proof.matched_iocs:
                    md.append(f"- **Corroborated Indicators:** {', '.join([f'`{ioc}`' for ioc in proof.matched_iocs])}")
                md.append(f"- **Retrieved Document ID:** `{proof.doc_id}` | **Relevance Rank Score:** {proof.retrieval_score:.2f}\n")
        else:
            md.append("> *No direct textual mentions retrieved in the current corpus.*")

        # Recommended Defensive Actions
        md.append("\n## 4. 🛡️ Prioritized Defensive Actions & Containment")
        md.append(f"Based on the attribution to **{top.actor_name}**, SOC defenders should immediately execute the following countermeasures:")
        md.append("1. **Perimeter Blacklisting:** Block all identified IPs, C2 staging domains, and reverse infrastructure hashes in EDR and firewall ACLs.")
        md.append("2. **Active Directory Audit:** Review privileged account usage, Kerberos tickets, and Golden SAML token signing certs for anomalous issuance.")
        md.append("3. **Vulnerability Patch Verification:** Immediately confirm patch status for CVEs associated with this threat group's operational chain.")
        md.append("4. **Hunting Queries:** Execute hunting queries across endpoint telemetry for known associated MITRE ATT&CK techniques.")

        return "\n".join(md)

    @staticmethod
    def generate_json_report(result: FusionAnalysisResult) -> Dict[str, Any]:
        return {
            "metadata": {
                "generated_at": datetime.utcnow().isoformat(),
                "engine": "NexusCTI v1.0",
                "framework": "Hybrid GNN + Text-Grounded RAG"
            },
            "investigation": {
                "query_ioc": result.query_ioc,
                "multi_hop_depth": result.multi_hop_depth,
                "hallucination_risk": result.hallucination_risk,
                "synergistic_rationale": result.synergistic_rationale
            },
            "top_attribution": result.top_actor.dict() if result.top_actor else None,
            "all_candidates": [c.dict() for c in result.all_candidates],
            "graph_trail": result.graph_trail.dict() if result.graph_trail else None,
            "narrative_proofs": [p.dict() for p in result.narrative_proofs]
        }
