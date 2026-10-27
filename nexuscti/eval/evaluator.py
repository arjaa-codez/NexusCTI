"""
Empirical Benchmark Evaluation Harness for NexusCTI.
Compares Hybrid GNN+RAG against Naive Vector RAG and Standalone GNN baselines.
"""

from typing import List, Dict, Any, Tuple
from collections import defaultdict

from .benchmark_cases import BenchmarkTestCase, get_benchmark_dataset
from .baselines import NaiveVectorRAGBaseline, StandaloneGNNBaseline
from ..fusion.engine import SynergisticFusionEngine


class BenchmarkResults(dict):
    """Container for benchmark metrics."""
    pass


class AttributionEvaluator:
    """
    Executes standardized empirical benchmarking across all evaluation dimensions.
    """

    def __init__(
        self,
        fusion_engine: SynergisticFusionEngine,
        vector_baseline: NaiveVectorRAGBaseline,
        gnn_baseline: StandaloneGNNBaseline,
        test_cases: List[BenchmarkTestCase] = None
    ):
        self.fusion_engine = fusion_engine
        self.vector_baseline = vector_baseline
        self.gnn_baseline = gnn_baseline
        self.test_cases = test_cases or get_benchmark_dataset()

    def run_benchmark(self) -> Dict[str, Any]:
        """
        Runs complete benchmark evaluation comparing the 3 architectures.
        """
        models = {
            "Naive Vector-only RAG": self._evaluate_vector_rag,
            "Standalone GNN Classifier": self._evaluate_standalone_gnn,
            "NexusCTI Hybrid (GNN + RAG)": self._evaluate_hybrid
        }

        benchmark_summary: Dict[str, Any] = {}
        detailed_records: List[Dict[str, Any]] = []

        for model_name, eval_fn in models.items():
            metrics, records = eval_fn()
            benchmark_summary[model_name] = metrics
            for rec in records:
                rec["model"] = model_name
                detailed_records.append(rec)

        return {
            "summary": benchmark_summary,
            "detailed_case_evaluations": detailed_records,
            "total_test_cases": len(self.test_cases)
        }

    def _evaluate_vector_rag(self) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        top1_hits = 0
        top3_hits = 0
        top5_hits = 0
        multihop_hits = 0
        multihop_total = 0
        hallucinations = 0
        reciprocal_ranks = []
        records = []

        for case in self.test_cases:
            preds = self.vector_baseline.predict(case.query)
            pred_actors = [p[0] for p in preds]

            is_top1 = len(pred_actors) > 0 and pred_actors[0] == case.ground_truth_actor
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

            # Hallucination metric: if top prediction is confident but totally incorrect
            if preds and preds[0][0] != case.ground_truth_actor:
                hallucinations += 1

            records.append({
                "case_id": case.id,
                "case_name": case.name,
                "category": case.category,
                "ground_truth": case.ground_truth_actor,
                "predicted_top1": pred_actors[0] if pred_actors else "None",
                "is_correct": is_top1,
                "rank": rank,
                "confidence": preds[0][1] if preds else 0.0
            })

        n = len(self.test_cases)
        metrics = {
            "top1_accuracy": round((top1_hits / n) * 100, 2),
            "top3_accuracy": round((top3_hits / n) * 100, 2),
            "top5_accuracy": round((top5_hits / n) * 100, 2),
            "multihop_reasoning_success": round((multihop_hits / multihop_total) * 100, 2) if multihop_total else 0.0,
            "hallucination_rate": round((hallucinations / n) * 100, 2),
            "mrr": round(sum(reciprocal_ranks) / n, 4)
        }
        return metrics, records

    def _evaluate_standalone_gnn(self) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        top1_hits = 0
        top3_hits = 0
        top5_hits = 0
        multihop_hits = 0
        multihop_total = 0
        hallucinations = 0
        reciprocal_ranks = []
        records = []

        for case in self.test_cases:
            preds = self.gnn_baseline.predict(case.anchor_ioc)
            pred_actors = [p[0] for p in preds]

            is_top1 = len(pred_actors) > 0 and pred_actors[0] == case.ground_truth_actor
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

            if preds and preds[0][0] != case.ground_truth_actor:
                hallucinations += 1

            records.append({
                "case_id": case.id,
                "case_name": case.name,
                "category": case.category,
                "ground_truth": case.ground_truth_actor,
                "predicted_top1": pred_actors[0] if pred_actors else "None",
                "is_correct": is_top1,
                "rank": rank,
                "confidence": preds[0][1] if preds else 0.0
            })

        n = len(self.test_cases)
        metrics = {
            "top1_accuracy": round((top1_hits / n) * 100, 2),
            "top3_accuracy": round((top3_hits / n) * 100, 2),
            "top5_accuracy": round((top5_hits / n) * 100, 2),
            "multihop_reasoning_success": round((multihop_hits / multihop_total) * 100, 2) if multihop_total else 0.0,
            "hallucination_rate": round((hallucinations / n) * 100, 2),
            "mrr": round(sum(reciprocal_ranks) / n, 4)
        }
        return metrics, records

    def _evaluate_hybrid(self) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        top1_hits = 0
        top3_hits = 0
        top5_hits = 0
        multihop_hits = 0
        multihop_total = 0
        hallucinations = 0
        reciprocal_ranks = []
        records = []

        for case in self.test_cases:
            result = self.fusion_engine.analyze_incident(
                query=case.query,
                ioc_override=case.anchor_ioc
            )

            pred_actors = [c.actor_id for c in result.all_candidates]

            is_top1 = len(pred_actors) > 0 and pred_actors[0] == case.ground_truth_actor
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

            # Hallucination is strictly controlled: if cross-validation was below threshold or top is wrong
            if result.top_actor and (result.top_actor.actor_id != case.ground_truth_actor or result.top_actor.cross_validation_score < 0.35):
                hallucinations += 1

            records.append({
                "case_id": case.id,
                "case_name": case.name,
                "category": case.category,
                "ground_truth": case.ground_truth_actor,
                "predicted_top1": pred_actors[0] if pred_actors else "None",
                "is_correct": is_top1,
                "rank": rank,
                "confidence": result.top_actor.fused_confidence if result.top_actor else 0.0,
                "hops": result.multi_hop_depth,
                "hallucination_risk": result.hallucination_risk
            })

        n = len(self.test_cases)
        metrics = {
            "top1_accuracy": round((top1_hits / n) * 100, 2),
            "top3_accuracy": round((top3_hits / n) * 100, 2),
            "top5_accuracy": round((top5_hits / n) * 100, 2),
            "multihop_reasoning_success": round((multihop_hits / multihop_total) * 100, 2) if multihop_total else 0.0,
            "hallucination_rate": round((hallucinations / n) * 100, 2),
            "mrr": round(sum(reciprocal_ranks) / n, 4)
        }
        return metrics, records
