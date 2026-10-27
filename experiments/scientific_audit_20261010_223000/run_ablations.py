"""
Phase 3 Controlled Ablation Experiment Runner.
Executes and compares:
- Configuration A: Vector-only RAG
- Configuration B: Graph-only (Non-Neural Topological)
- Configuration C: GNN-only (Neural Relational Message Passing)
- Configuration D: Graph + RAG (Non-Neural Graph + Text Retrieval)
- Configuration E: Full Hybrid (NexusCTI Unified Engine)
Generates all Phase 3 result files, CSV tables, and reproducibility manifests.
"""

import sys
import time
import json
import csv
from pathlib import Path
from collections import defaultdict
import networkx as nx

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from nexuscti.service import get_service
from nexuscti.eval.benchmark_cases import get_benchmark_dataset

EXPERIMENT_DIR = Path(__file__).resolve().parent


class AblationExperimentSuite:
    def __init__(self):
        print("[*] Initializing ablation runner environment...")
        self.service = get_service()
        self.dataset = get_benchmark_dataset()
        self.actors = list(self.service.tkg.actor_indices)
        self.actor_ids = [self.service.tkg.idx_to_node_id[idx] for idx in self.actors]

    # --- CONFIGURATION A: VECTOR-ONLY ---
    def predict_config_a(self, query: str):
        """Pure text retrieval using dense semantic similarity without graph lookups."""
        results = self.service.hybrid_retriever.dense.search(query, top_k=5)
        actor_scores = defaultdict(float)
        for chunk, score in results:
            actor_scores[chunk.target_actor] += max(score, 0.0)

        total = sum(actor_scores.values()) or 1.0
        ranked = [(actor, round(score / total, 4)) for actor, score in actor_scores.items()]
        # Add remaining actors with zero score if missing
        existing = {a for a, _ in ranked}
        for a in self.actor_ids:
            if a not in existing:
                ranked.append((a, 0.0))
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked

    # --- CONFIGURATION B: GRAPH-ONLY (NON-NEURAL TOPOLOGICAL) ---
    def predict_config_b(self, ioc: str):
        """Symbolic shortest path topological distance on NetworkX graph without neural weights."""
        node = self.service.tkg.find_node_by_indicator(ioc)
        if not node:
            # Unseen node has equal prior distance
            return [(a, round(1.0 / len(self.actor_ids), 4)) for a in self.actor_ids]

        undirected_graph = self.service.tkg.nx_graph.to_undirected()
        scores = {}
        for a_id in self.actor_ids:
            try:
                dist = nx.shortest_path_length(undirected_graph, node.id, a_id)
                scores[a_id] = 1.0 / (1.0 + float(dist))
            except nx.NetworkXNoPath:
                scores[a_id] = 0.001

        total = sum(scores.values()) or 1.0
        ranked = [(a, round(s / total, 4)) for a, s in scores.items()]
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked

    # --- CONFIGURATION C: GNN-ONLY (NEURAL STRUCTURAL) ---
    def predict_config_c(self, ioc: str):
        """Trained HeteroThreatGNN relational inference without text retrieval."""
        node = self.service.tkg.find_node_by_indicator(ioc)
        node_id = node.id if node else self.service.tkg.add_temporary_ioc_node(ioc)

        raw_preds = self.service.gnn_trainer.predict_attribution(node_id)
        ranked = [(p["actor_id"], round(p["structural_confidence"], 4)) for p in raw_preds]
        existing = {a for a, _ in ranked}
        for a in self.actor_ids:
            if a not in existing:
                ranked.append((a, 0.0))
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked

    # --- CONFIGURATION D: GRAPH + RAG (NON-NEURAL GRAPH + TEXT) ---
    def predict_config_d(self, query: str, ioc: str):
        """Combines non-neural graph distance with text retrieval score without GNN embeddings."""
        preds_a = dict(self.predict_config_a(query))
        preds_b = dict(self.predict_config_b(ioc))

        combined = {}
        for a in self.actor_ids:
            s_a = preds_a.get(a, 0.0)
            s_b = preds_b.get(a, 0.0)
            combined[a] = round(0.5 * s_a + 0.5 * s_b, 4)

        ranked = sorted(combined.items(), key=lambda x: x[1], reverse=True)
        return ranked

    # --- CONFIGURATION E: FULL HYBRID (NEXUSCTI UNIFIED) ---
    def predict_config_e(self, query: str, ioc: str):
        """Full hybrid system combining GNN, RAG, and cross-validation consistency."""
        res = self.service.analyze(query, ioc_override=ioc)
        ranked = [(c.actor_id, round(c.fused_confidence, 4)) for c in res.all_candidates]
        existing = {a for a, _ in ranked}
        for a in self.actor_ids:
            if a not in existing:
                ranked.append((a, 0.0))
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked, res.multi_hop_depth

    def run_all(self):
        configs = [
            ("Config A (Vector-only)", "vector_only"),
            ("Config B (Graph-only)", "graph_only"),
            ("Config C (GNN-only)", "gnn_only"),
            ("Config D (Graph + RAG)", "graph_plus_rag"),
            ("Config E (Full Hybrid)", "full_hybrid")
        ]

        metrics_summary = {}
        runtime_summary = {}
        per_case_rows = []
        all_results_raw = {}

        total_suite_start = time.time()

        for config_name, config_key in configs:
            print(f"[*] Running evaluation for {config_name}...")
            start_time = time.time()
            top1_hits = 0
            top3_hits = 0
            top5_hits = 0
            multihop_hits = 0
            multihop_total = 0
            hallucinations = 0
            reciprocal_ranks = []
            case_evaluations = []

            for case in self.dataset:
                case_t0 = time.time()
                hops = 0

                if config_key == "vector_only":
                    preds = self.predict_config_a(case.query)
                elif config_key == "graph_only":
                    preds = self.predict_config_b(case.anchor_ioc)
                elif config_key == "gnn_only":
                    preds = self.predict_config_c(case.anchor_ioc)
                elif config_key == "graph_plus_rag":
                    preds = self.predict_config_d(case.query, case.anchor_ioc)
                elif config_key == "full_hybrid":
                    preds, hops = self.predict_config_e(case.query, case.anchor_ioc)

                case_elapsed = time.time() - case_t0
                pred_actors = [p[0] for p in preds]
                top1 = pred_actors[0] if pred_actors else "None"
                top1_conf = preds[0][1] if preds else 0.0

                is_top1 = (top1 == case.ground_truth_actor)
                is_top3 = case.ground_truth_actor in pred_actors[:3]
                is_top5 = case.ground_truth_actor in pred_actors[:5]

                rank = (pred_actors.index(case.ground_truth_actor) + 1) if case.ground_truth_actor in pred_actors else 99
                rr = 1.0 / rank if rank <= 10 else 0.0
                reciprocal_ranks.append(rr)

                if is_top1:
                    top1_hits += 1
                if is_top3:
                    top3_hits += 1
                if is_top5:
                    top5_hits += 1

                if case.expected_hops >= 2:
                    multihop_total += 1
                    if is_top1:
                        multihop_hits += 1

                if not is_top1:
                    hallucinations += 1

                record = {
                    "config": config_name,
                    "case_id": case.id,
                    "case_name": case.name,
                    "category": case.category,
                    "ground_truth": case.ground_truth_actor,
                    "predicted_top1": top1,
                    "is_correct": is_top1,
                    "rank": rank,
                    "confidence": top1_conf,
                    "runtime_sec": round(case_elapsed, 4),
                    "hops": hops
                }
                case_evaluations.append(record)
                per_case_rows.append(record)

            elapsed_total = time.time() - start_time
            n = len(self.dataset)

            met = {
                "top1_accuracy": round((top1_hits / n) * 100.0, 2),
                "top1_count": f"{top1_hits}/{n}",
                "top3_accuracy": round((top3_hits / n) * 100.0, 2),
                "top3_count": f"{top3_hits}/{n}",
                "top5_accuracy": round((top5_hits / n) * 100.0, 2),
                "top5_count": f"{top5_hits}/{n}",
                "multihop_accuracy": round((multihop_hits / multihop_total) * 100.0, 2) if multihop_total else 0.0,
                "multihop_count": f"{multihop_hits}/{multihop_total}",
                "hallucination_rate": round((hallucinations / n) * 100.0, 2),
                "hallucination_count": f"{hallucinations}/{n}",
                "mrr": round(sum(reciprocal_ranks) / n, 4),
                "total_runtime_sec": round(elapsed_total, 3),
                "avg_runtime_per_case_sec": round(elapsed_total / n, 4)
            }
            metrics_summary[config_name] = met
            runtime_summary[config_name] = {
                "total_sec": round(elapsed_total, 3),
                "avg_per_case_sec": round(elapsed_total / n, 4)
            }
            all_results_raw[config_name] = {
                "metrics": met,
                "cases": case_evaluations
            }
            print(f"    -> {config_name}: Top-1: {met['top1_accuracy']}% ({met['top1_count']}) | MRR: {met['mrr']} | Runtime: {met['total_runtime_sec']}s")

        total_suite_elapsed = time.time() - total_suite_start
        runtime_summary["overall_suite_runtime_sec"] = round(total_suite_elapsed, 3)

        # --- SAVE OUTPUT FILES ---
        # 1. Ablation Configurations
        with open(EXPERIMENT_DIR / "ablation_configurations.json", "w", encoding="utf-8") as f:
            json.dump({
                "experiment_id": "scientific_audit_20261010_223000",
                "total_configurations": 5,
                "configurations": {
                    "Config A": {"name": "Vector-only RAG", "modules": ["DenseRetriever"], "scoring": "CosSim Sum"},
                    "Config B": {"name": "Graph-only (Topological)", "modules": ["NetworkX ShortestPath"], "scoring": "1/(1+d)"},
                    "Config C": {"name": "GNN-only (Neural)", "modules": ["HeteroThreatGNN"], "scoring": "Softmax dot-product"},
                    "Config D": {"name": "Graph + RAG (Non-Neural)", "modules": ["NetworkX", "DenseRetriever"], "scoring": "0.5*Graph + 0.5*RAG"},
                    "Config E": {"name": "Full Hybrid (NexusCTI)", "modules": ["HeteroThreatGNN", "DenseRetriever", "CrossValidation"], "scoring": "0.45*GNN + 0.35*RAG + 0.20*CV"}
                }
            }, f, indent=2)

        # 2. Raw Ablation Results
        with open(EXPERIMENT_DIR / "ablation_results.json", "w", encoding="utf-8") as f:
            json.dump(all_results_raw, f, indent=2)

        # 3. Per Case Predictions CSV
        with open(EXPERIMENT_DIR / "per_case_predictions.csv", "w", newline="", encoding="utf-8") as f:
            fieldnames = ["config", "case_id", "case_name", "category", "ground_truth", "predicted_top1", "is_correct", "rank", "confidence", "hops", "runtime_sec"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(per_case_rows)

        # 4. Metrics Summary CSV
        with open(EXPERIMENT_DIR / "metrics_summary.csv", "w", newline="", encoding="utf-8") as f:
            fieldnames = ["configuration", "top1_accuracy_pct", "top1_count", "top3_accuracy_pct", "top3_count", "multihop_accuracy_pct", "multihop_count", "hallucination_rate_pct", "mrr", "runtime_total_sec", "avg_runtime_sec"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for cfg_name, met in metrics_summary.items():
                writer.writerow({
                    "configuration": cfg_name,
                    "top1_accuracy_pct": met["top1_accuracy"],
                    "top1_count": met["top1_count"],
                    "top3_accuracy_pct": met["top3_accuracy"],
                    "top3_count": met["top3_count"],
                    "multihop_accuracy_pct": met["multihop_accuracy"],
                    "multihop_count": met["multihop_count"],
                    "hallucination_rate_pct": met["hallucination_rate"],
                    "mrr": met["mrr"],
                    "runtime_total_sec": met["total_runtime_sec"],
                    "avg_runtime_sec": met["avg_runtime_per_case_sec"]
                })

        # 5. Runtime Summary JSON
        with open(EXPERIMENT_DIR / "runtime_summary.json", "w", encoding="utf-8") as f:
            json.dump(runtime_summary, f, indent=2)

        # 6. Reproducibility Manifest
        with open(EXPERIMENT_DIR / "reproducibility_manifest.json", "w", encoding="utf-8") as f:
            json.dump({
                "manifest_version": "1.0",
                "experiment_id": "scientific_audit_20261010_223000",
                "date": "2026-10-10",
                "environment": {
                    "os": "Windows 11",
                    "shell": "PowerShell 5.1",
                    "python_executable": sys.executable,
                    "python_version": sys.version
                },
                "execution_command": ".\\.venv\\Scripts\\python.exe -u experiments/scientific_audit_20261010_223000/run_ablations.py",
                "total_cases_evaluated": len(self.dataset),
                "evaluation_metrics_produced": ["Top-1", "Top-3", "Top-5", "Multi-Hop Success", "Hallucination Rate", "MRR", "Runtime"],
                "status": "COMPLETED_REPRODUCIBLE"
            }, f, indent=2)

        print("[+] All Phase 3 ablation files generated successfully!")


if __name__ == "__main__":
    suite = AblationExperimentSuite()
    suite.run_all()
