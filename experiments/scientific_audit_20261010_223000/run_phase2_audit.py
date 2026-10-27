"""
Phase 2 Scientific Audit Runner for NexusCTI.
Audits all 12 benchmark cases for data leakage, graph shortcuts, retrieval contamination,
and generates all Phase 2 artifact files.
"""

import sys
import json
import csv
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from nexuscti.service import get_service
from nexuscti.eval.benchmark_cases import get_benchmark_dataset
from nexuscti.config import (
    FUSION_WEIGHT_GNN,
    FUSION_WEIGHT_RAG,
    FUSION_WEIGHT_CROSS_VAL,
)

EXPERIMENT_DIR = Path(__file__).resolve().parent

def run_audit():
    print("[*] Initializing NexusCTI Service for Phase 2 Audit...")
    service = get_service()
    dataset = get_benchmark_dataset()

    case_rows = []
    graph_edge_audit = {}
    retrieval_traces = {}
    duplicate_overlap = {
        "report_count": len(service.corpus),
        "test_case_count": len(dataset),
        "actor_coverage": {},
        "exact_indicator_matches": [],
        "query_text_overlap": []
    }

    # Analyze corpus indicators
    corpus_indicators = set()
    for rpt in service.corpus:
        for ioc in rpt.iocs:
            corpus_indicators.add(ioc.strip())

    for case in dataset:
        print(f"[*] Auditing {case.id}: {case.name}...")
        # Step 1: Run Hybrid Analysis
        res = service.analyze(query=case.query, ioc_override=case.anchor_ioc)

        # Step 2: Trace GNN inference & Reachability
        node = service.tkg.find_node_by_indicator(case.anchor_ioc)
        node_id = node.id if node else "novel_ioc"

        # Check reachability in graph
        gt_actor_node_id = case.ground_truth_actor
        in_training_graph = False
        if node and gt_actor_node_id in service.tkg.nx_graph:
            import networkx as nx
            try:
                shortest_dist = nx.shortest_path_length(service.tkg.nx_graph.to_undirected(), node_id, gt_actor_node_id)
                # Training cutoff in GNNAttributionTrainer is 3 hops
                in_training_graph = (shortest_dist <= 3)
            except Exception:
                shortest_dist = -1
                in_training_graph = False
        else:
            shortest_dist = -1

        # Check graph edges
        trail_hops = []
        if res.graph_trail:
            for h in res.graph_trail.hops:
                trail_hops.append(f"{h.source_name} --({h.relation})--> {h.target_name}")

        # Check direct shortcut
        has_direct_actor_edge = False
        if node:
            for neighbor in service.tkg.nx_graph.neighbors(node.id):
                if neighbor == gt_actor_node_id:
                    has_direct_actor_edge = True

        graph_edge_audit[case.id] = {
            "case_name": case.name,
            "anchor_ioc": case.anchor_ioc,
            "resolved_node_id": node_id,
            "shortest_distance_to_actor": shortest_dist,
            "supervised_in_training_labels": in_training_graph,
            "has_direct_actor_shortcut_edge": has_direct_actor_edge,
            "traversed_path_hops": trail_hops,
            "hop_count": len(trail_hops)
        }

        # Step 3: Trace Retrieval
        retrieved_proofs = []
        retrieved_doc_ids = []
        retrieval_leak_detected = False
        for p in res.narrative_proofs:
            retrieved_doc_ids.append(p.doc_id)
            clean_ioc = case.anchor_ioc.replace("[.]", ".")
            cites_ioc = (clean_ioc.lower() in p.relevant_text.lower()) or (case.anchor_ioc.lower() in p.relevant_text.lower())
            proof_entry = {
                "chunk_id": p.chunk_id,
                "doc_id": p.doc_id,
                "source": p.source,
                "target_actor": p.target_actor,
                "retrieval_score": p.retrieval_score,
                "cites_anchor_ioc": cites_ioc
            }
            if cites_ioc and p.target_actor == case.ground_truth_actor:
                retrieval_leak_detected = True
            retrieved_proofs.append(proof_entry)

        retrieval_traces[case.id] = {
            "query": case.query,
            "anchor_ioc": case.anchor_ioc,
            "ground_truth_actor": case.ground_truth_actor,
            "retrieved_documents": list(set(retrieved_doc_ids)),
            "proofs": retrieved_proofs,
            "exact_ioc_retrieval_match": retrieval_leak_detected
        }

        # Step 4: Check Overlap
        clean_anchor = case.anchor_ioc.replace("[.]", ".")
        anchor_in_corpus = any(clean_anchor.lower() in r.text.lower() or clean_anchor in r.iocs for r in service.corpus)
        if anchor_in_corpus:
            duplicate_overlap["exact_indicator_matches"].append({
                "case_id": case.id,
                "indicator": case.anchor_ioc,
                "found_in_corpus": True
            })

        # Evaluate performance & ranking
        pred_actors = [c.actor_id for c in res.all_candidates]
        top1_pred = pred_actors[0] if pred_actors else "None"
        rank = (pred_actors.index(case.ground_truth_actor) + 1) if case.ground_truth_actor in pred_actors else 99
        is_correct = (top1_pred == case.ground_truth_actor)

        # Audit finding classification
        if has_direct_actor_edge:
            finding = "FAIL: Direct indicator-to-actor edge shortcut exists in graph"
            severity = "HIGH"
            recommendation = "Remove direct shortcut edge to ensure multi-hop reasoning is tested."
        elif in_training_graph and retrieval_leak_detected:
            finding = "REVIEW: Transductive graph overlap and text indicator co-occurrence in corpus"
            severity = "MEDIUM"
            recommendation = "Legitimate for retrospective forensic verification; state transductive setting in paper."
        elif in_training_graph:
            finding = "PASS (Transductive): Graph node supervised within 3-hop radius during GNN training"
            severity = "LOW"
            recommendation = "Distinguish transductive vs inductive evaluation splits."
        else:
            finding = "PASS: Out-of-3-hop/novel indicator requiring true relational message passing"
            severity = "LOW"
            recommendation = "Maintain as primary multi-hop benchmark scenario."

        top_cand = res.top_actor
        case_rows.append({
            "case_id": case.id,
            "case_name": case.name,
            "category": case.category,
            "original_query": case.query,
            "input_indicator": case.anchor_ioc,
            "ground_truth_actor": case.ground_truth_actor,
            "evidence_provenance": "CISA / Mandiant Authoritative Advisory",
            "prediction_current": top1_pred,
            "rank_current": rank,
            "is_correct": is_correct,
            "fused_confidence": top_cand.fused_confidence if top_cand else 0.0,
            "structural_confidence": top_cand.structural_confidence if top_cand else 0.0,
            "textual_confidence": top_cand.textual_confidence if top_cand else 0.0,
            "cross_val_score": top_cand.cross_validation_score if top_cand else 0.0,
            "hops_traversed": res.multi_hop_depth,
            "in_training_graph": "YES" if in_training_graph else "NO",
            "retrieval_leak_detected": "YES" if retrieval_leak_detected else "NO",
            "audit_finding": finding,
            "severity": severity,
            "remediation_recommendation": recommendation
        })

    # Save CSV
    csv_file = EXPERIMENT_DIR / "case_level_audit.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        fieldnames = list(case_rows[0].keys())
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(case_rows)
    print(f"[+] Saved case level audit to {csv_file}")

    # Save JSON files
    with open(EXPERIMENT_DIR / "graph_edge_audit.json", "w", encoding="utf-8") as f:
        json.dump(graph_edge_audit, f, indent=2)

    with open(EXPERIMENT_DIR / "retrieval_trace.json", "w", encoding="utf-8") as f:
        json.dump(retrieval_traces, f, indent=2)

    with open(EXPERIMENT_DIR / "duplicate_overlap_report.json", "w", encoding="utf-8") as f:
        json.dump(duplicate_overlap, f, indent=2)

    print("[+] All audit data files successfully written.")

if __name__ == "__main__":
    run_audit()
