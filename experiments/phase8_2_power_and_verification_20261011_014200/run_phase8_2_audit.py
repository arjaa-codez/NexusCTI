"""
NexusCTI Phase 8.2: Statistical Method Verification & Prospective Power Analysis
================================================================================
Independently verifies:
1. Exact Clopper-Pearson intervals and paired risk-difference intervals (Newcombe, CC-Wald, Agresti-Min).
2. Exact two-sided McNemar test and odds ratio intervals.
3. Prospective power analysis across multiple (q, theta, N) scenarios combining exact binomial integration and Monte Carlo simulation.
4. Generates all Phase 8.2 deliverables.
"""

import os
import sys
import json
import csv
import math
import hashlib
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Any

import numpy as np
import scipy
import scipy.stats as stats

# Repositories and paths
REPO_ROOT = Path("c:/Users/Arjaa Chatterjee/OneDrive/Desktop/NexusCTI")
PHASE8_DIR = REPO_ROOT / "experiments" / "phase8_expanded_evaluation_20261011_012000"
PHASE8_1_DIR = REPO_ROOT / "experiments" / "phase8_1_independent_audit_20261011_013000"
PHASE8_2_DIR = REPO_ROOT / "experiments" / "phase8_2_power_and_verification_20261011_014200"
PHASE8_2_DIR.mkdir(parents=True, exist_ok=True)

def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

# =============================================================================
# STEP 0: HASH PRESERVATION OF PRIOR EXPERIMENT ARTIFACTS
# =============================================================================
print("[*] STEP 0: Hashing and preserving Phase 8 and Phase 8.1 artifacts...")
artifact_hashes = {}

for p_dir, p_label in [(PHASE8_DIR, "phase8"), (PHASE8_1_DIR, "phase8_1")]:
    if p_dir.exists():
        for f in sorted(p_dir.glob("*")):
            if f.is_file():
                h = compute_sha256(f)
                artifact_hashes[f"{p_label}/{f.name}"] = {
                    "sha256": h,
                    "size_bytes": f.stat().st_size,
                    "path": str(f)
                }

with open(PHASE8_2_DIR / "artifact_hash_manifest.json", "w", encoding="utf-8") as f:
    json.dump({
        "audit_phase": "Phase 8.2 Statistical Audit and Prospective Power Analysis",
        "timestamp": "2026-10-11T01:42:00+05:30",
        "preserved_artifacts_count": len(artifact_hashes),
        "artifacts": artifact_hashes
    }, f, indent=2)
print(f"[+] Preserved {len(artifact_hashes)} artifacts into artifact_hash_manifest.json")

# =============================================================================
# TASK 1: INDEPENDENT VERIFICATION OF PHASE 8.1 STATISTICS
# =============================================================================
print("\n[*] TASK 1: Verifying contingency table and exact intervals...")
preds_csv = PHASE8_DIR / "frozen_predictions.csv"
rows = []
with open(preds_csv, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

task_a_test = [r for r in rows if r["split_role"] == "FROZEN_TEST" and "Task A" in r["task"]]
n_total = len(task_a_test)
print(f"    Loaded {n_total} Task A Frozen Test Cases")

a = sum(1 for r in task_a_test if int(r["hybrid_rank"]) <= 3 and int(r["retrieval_rank"]) <= 3)
b = sum(1 for r in task_a_test if int(r["hybrid_rank"]) <= 3 and int(r["retrieval_rank"]) > 3)
c = sum(1 for r in task_a_test if int(r["hybrid_rank"]) > 3 and int(r["retrieval_rank"]) <= 3)
d = sum(1 for r in task_a_test if int(r["hybrid_rank"]) > 3 and int(r["retrieval_rank"]) > 3)

assert n_total == 24
assert a == 11 and b == 6 and c == 1 and d == 6, f"Mismatch: a={a}, b={b}, c={c}, d={d}"

full_hybrid_top3 = a + b  # 17
retrieval_top3 = a + c    # 12
diff_prop = (b - c) / n_total  # 5/24 = 0.208333...

# 1. Exact two-sided McNemar p-value via SciPy binomtest
b_res = stats.binomtest(b, b + c, p=0.5, alternative='two-sided')
mcnemar_p = float(b_res.pvalue)
print(f"    Exact McNemar p-value (SciPy): {mcnemar_p:.6f}")

# 2. Clopper-Pearson 95% interval for conditional probability pi = b / (b + c)
pi_hat = b / (b + c)
ci_pi = stats.beta.ppf(0.025, b, c + 1), stats.beta.ppf(0.975, b + 1, c)
print(f"    Exact Clopper-Pearson for pi = b/(b+c): [{ci_pi[0]:.4f}, {ci_pi[1]:.4f}] (hat = {pi_hat:.4f})")

# 3. Discordance probability q = (b + c) / N
q_hat = (b + c) / n_total
ci_q = stats.beta.ppf(0.025, b + c, n_total - (b + c) + 1), stats.beta.ppf(0.975, b + c + 1, n_total - (b + c))
print(f"    Exact Clopper-Pearson for q = (b+c)/N: [{ci_q[0]:.4f}, {ci_q[1]:.4f}] (hat = {q_hat:.4f})")

# 4. Exact conditional odds ratio interval: psi = pi / (1 - pi)
psi_hat = b / c if c > 0 else float("inf")
psi_low = ci_pi[0] / (1.0 - ci_pi[0])
psi_high = ci_pi[1] / (1.0 - ci_pi[1])
print(f"    Exact Conditional Odds Ratio psi: [{psi_low:.3f}, {psi_high:.3f}] (hat = {psi_hat:.1f})")

# 5. Paired Risk Difference Intervals (Small-Sample Methods)
# Method A: Continuity-Corrected Wald
se_wald = math.sqrt(((b + c) - ((b - c)**2) / n_total) / (n_total**2))
diff_cc = (abs(b - c) - 1.0) / n_total
ci_cc_low = diff_cc - 1.95996 * se_wald
ci_cc_high = diff_cc + 1.95996 * se_wald

# Method B: Newcombe Paired Score Method (Method 10, Newcombe 1998)
def wilson_limits(k, n, z=1.95996):
    p = k / n
    denom = 1.0 + z**2 / n
    ctr = (p + z**2 / (2 * n)) / denom
    hw = (z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2))) / denom
    return max(0.0, ctr - hw), min(1.0, ctr + hw)

l1, u1 = wilson_limits(full_hybrid_top3, n_total)
l2, u2 = wilson_limits(retrieval_top3, n_total)
p1 = full_hybrid_top3 / n_total
p2 = retrieval_top3 / n_total

# Phi correlation between marginals
phi_num = (a * d - b * c)
phi_den = math.sqrt((a + b) * (c + d) * (a + c) * (b + d))
phi = phi_num / phi_den if phi_den > 0 else 0.0

newcombe_low = diff_prop - math.sqrt((p1 - l1)**2 + (u2 - p2)**2 - 2 * phi * (p1 - l1) * (u2 - p2))
newcombe_high = diff_prop + math.sqrt((u1 - p1)**2 + (p2 - l2)**2 - 2 * phi * (u1 - p1) * (p2 - l2))

# Method C: Agresti-Min Paired Pseudo-count (+0.5 per cell)
a_star, b_star, c_star, d_star = a + 0.5, b + 0.5, c + 0.5, d + 0.5
n_star = a_star + b_star + c_star + d_star
diff_agresti = (b_star - c_star) / n_star
se_agresti = math.sqrt(((b_star + c_star) - ((b_star - c_star)**2) / n_star) / (n_star**2))
agresti_low = diff_agresti - 1.95996 * se_agresti
agresti_high = diff_agresti + 1.95996 * se_agresti

# Save mcnemar_verification.json
mcnemar_verification_data = {
    "audit_timestamp": "2026-10-11T01:42:00+05:30",
    "software_environment": {
        "python_version": sys.version,
        "scipy_version": scipy.__version__,
        "numpy_version": np.__version__
    },
    "reconstructed_contingency_table": {
        "both_correct_a": a,
        "hybrid_only_correct_b": b,
        "retrieval_only_correct_c": c,
        "both_incorrect_d": d,
        "total_task_a_n": n_total
    },
    "marginal_proportions": {
        "full_hybrid_top3_accuracy": round(p1 * 100, 2),
        "retrieval_only_top3_accuracy": round(p2 * 100, 2),
        "paired_risk_difference_percent": round(diff_prop * 100, 2)
    },
    "exact_hypothesis_test": {
        "test_name": "Exact Two-Sided McNemar Test (SciPy binomtest)",
        "formula": "binomtest(b, b+c, p=0.5, alternative='two-sided')",
        "discordant_pairs_n_d": b + c,
        "hybrid_wins_b": b,
        "retrieval_wins_c": c,
        "p_value": round(mcnemar_p, 6),
        "is_statistically_significant_alpha_0_05": (mcnemar_p < 0.05)
    },
    "odds_ratio_estimation": {
        "point_estimate_psi": round(psi_hat, 2),
        "exact_conditional_95_ci": [round(psi_low, 3), round(psi_high, 3)],
        "ci_includes_null_psi_1_0": (psi_low <= 1.0 <= psi_high)
    }
}

def json_serial(obj):
    if isinstance(obj, (np.bool_, bool)):
        return bool(obj)
    if isinstance(obj, (np.floating, float)):
        return float(obj)
    if isinstance(obj, (np.integer, int)):
        return int(obj)
    return str(obj)

with open(PHASE8_2_DIR / "mcnemar_verification.json", "w", encoding="utf-8") as f:
    json.dump(mcnemar_verification_data, f, indent=2, default=json_serial)
print(f"[+] Saved mcnemar_verification.json")

# Save exact_interval_recalculation.json
exact_intervals_data = {
    "audit_timestamp": "2026-10-11T01:42:00+05:30",
    "estimands": {
        "conditional_hybrid_win_prob_pi": {
            "definition": "P(Hybrid Correct | Disagreement)",
            "point_estimate": round(pi_hat, 4),
            "exact_clopper_pearson_95_ci": [round(ci_pi[0], 4), round(ci_pi[1], 4)],
            "includes_null_0_50": (ci_pi[0] <= 0.50 <= ci_pi[1]),
            "consistency_with_mcnemar_test": "CONSISTENT (Includes 0.50 <-> p = 0.1250 > 0.05)"
        },
        "paired_discordance_prob_q": {
            "definition": "P(Systems Disagree) = (b+c)/N",
            "point_estimate": round(q_hat, 4),
            "exact_clopper_pearson_95_ci": [round(ci_q[0], 4), round(ci_q[1], 4)],
            "note": "Critical nuisance parameter for prospective sample-size and power planning."
        },
        "conditional_odds_ratio_psi": {
            "definition": "Odds Ratio of Discordance = b / c",
            "point_estimate": round(psi_hat, 2),
            "exact_95_ci": [round(psi_low, 3), round(psi_high, 3)],
            "includes_null_1_0": (psi_low <= 1.0 <= psi_high),
            "consistency_with_mcnemar_test": "CONSISTENT (Includes 1.0 <-> p = 0.1250 > 0.05)"
        },
        "paired_risk_difference_delta": {
            "definition": "Marginal Top-3 Accuracy Difference = p_hybrid - p_retrieval",
            "point_estimate_percent": round(diff_prop * 100, 2),
            "methods": {
                "uncorrected_asymptotic_wald": {
                    "interval_percent": [0.90, 40.77],
                    "validity": "INVALID_SMALL_SAMPLE (Severe undercoverage when n_d = 7 < 20)"
                },
                "continuity_corrected_wald": {
                    "interval_percent": [round(ci_cc_low * 100, 2), round(ci_cc_high * 100, 2)],
                    "includes_zero": (ci_cc_low <= 0.0 <= ci_cc_high),
                    "validity": "DEFENSIBLE_CONSERVATIVE (Consistent with p = 0.1250)"
                },
                "newcombe_paired_score_method_10": {
                    "interval_percent": [round(newcombe_low * 100, 2), round(newcombe_high * 100, 2)],
                    "includes_zero": (newcombe_low <= 0.0 <= newcombe_high),
                    "validity": "RECOMMENDED_STANDARD (Maintains nominal 95% coverage for paired data)"
                },
                "agresti_min_pseudocount_adjusted": {
                    "interval_percent": [round(agresti_low * 100, 2), round(agresti_high * 100, 2)],
                    "includes_zero": (agresti_low <= 0.0 <= agresti_high),
                    "validity": "DEFENSIBLE_SMOOTHED (Consistent with p = 0.1250)"
                }
            }
        }
    }
}

with open(PHASE8_2_DIR / "exact_interval_recalculation.json", "w", encoding="utf-8") as f:
    json.dump(exact_intervals_data, f, indent=2, default=json_serial)
print(f"[+] Saved exact_interval_recalculation.json")

# =============================================================================
# TASK 2: PROSPECTIVE POWER ANALYSIS ACROSS (q, theta, N) SCENARIOS
# =============================================================================
print("\n[*] TASK 2: Simulating and computing prospective power across scenarios...")

# Grid parameters
q_scenarios = [
    ("Low Discordance", 0.15),
    ("Moderate-Low Discordance", 0.20),
    ("Moderate Discordance", 0.25),
    ("High Discordance (Phase 8 Baseline)", 0.2917)
]

theta_scenarios = [
    ("Null (No Advantage)", 0.50),
    ("Modest Advantage", 0.60),
    ("Moderate Advantage", 0.70),
    ("Large Advantage", 0.80),
    ("Observed Phase 8 Advantage", 0.8571)
]

sample_sizes = [24, 40, 60, 80, 100, 150, 200]
monte_carlo_trials = 10000
rng = np.random.default_rng(seed=42)

power_records = []

# Precompute exact binomial rejection lookup for d in 0..200
# rejection_table[d] = set of b values that reject H0 at alpha <= 0.05
rejection_table = {}
for d_val in range(1, 201):
    rej_b = set()
    for b_val in range(d_val + 1):
        pval = stats.binomtest(b_val, d_val, 0.5, alternative='two-sided').pvalue
        if pval <= 0.05:
            rej_b.add(b_val)
    rejection_table[d_val] = rej_b

print("    Computing exact binomial integration and Monte Carlo verification...")
for q_label, q_val in q_scenarios:
    for th_label, th_val in theta_scenarios:
        for n_val in sample_sizes:
            # 1. Exact Binomial Analytical Power
            # Sum over d = 1..N of P(D = d) * Sum over b in rej_table[d] of P(B = b | D = d)
            exact_pwr = 0.0
            prob_practical_exact = 0.0
            for d_val in range(1, n_val + 1):
                prob_d = stats.binom.pmf(d_val, n_val, q_val)
                if prob_d < 1e-12:
                    continue
                # For this d_val, get b's that reject
                rej_b = rejection_table[d_val]
                for b_val in rej_b:
                    prob_b = stats.binom.pmf(b_val, d_val, th_val)
                    exact_pwr += prob_d * prob_b

                # Practical effect probability: Delta_hat = (2b - d)/n_val >= 0.15
                for b_val in range(d_val + 1):
                    if (2 * b_val - d_val) / n_val >= 0.15:
                        prob_practical_exact += prob_d * stats.binom.pmf(b_val, d_val, th_val)

            # If d = 0, Delta = 0, never rejects or meets practical threshold

            # 2. Monte Carlo Simulation Check
            d_samples = rng.binomial(n_val, q_val, size=monte_carlo_trials)
            b_samples = rng.binomial(d_samples, th_val)

            # Check rejections
            # Using vectorization via lookup table
            mc_rejections = 0
            mc_practical = 0
            for i in range(monte_carlo_trials):
                d_i = d_samples[i]
                b_i = b_samples[i]
                if d_i > 0 and b_i in rejection_table[d_i]:
                    mc_rejections += 1
                if (2 * b_i - d_i) / n_val >= 0.15:
                    mc_practical += 1

            mc_pwr = mc_rejections / monte_carlo_trials
            mc_se = math.sqrt(mc_pwr * (1.0 - mc_pwr) / monte_carlo_trials)
            mc_prac_pwr = mc_practical / monte_carlo_trials

            expected_delta = q_val * (2 * th_val - 1) * 100

            power_records.append({
                "discordance_scenario": q_label,
                "discordance_rate_q": q_val,
                "advantage_scenario": th_label,
                "conditional_win_prob_theta": th_val,
                "expected_delta_percent": round(expected_delta, 2),
                "sample_size_N": n_val,
                "exact_mcnemar_power_percent": round(exact_pwr * 100, 2),
                "mc_estimated_power_percent": round(mc_pwr * 100, 2),
                "mc_standard_error_percent": round(mc_se * 100, 3),
                "prob_practical_effect_ge_15_percent": round(prob_practical_exact * 100, 2)
            })

# Save prospective_power_analysis.csv
power_csv_path = PHASE8_2_DIR / "prospective_power_analysis.csv"
with open(power_csv_path, "w", newline="", encoding="utf-8") as f:
    fields = [
        "discordance_scenario", "discordance_rate_q", "advantage_scenario",
        "conditional_win_prob_theta", "expected_delta_percent", "sample_size_N",
        "exact_mcnemar_power_percent", "mc_estimated_power_percent",
        "mc_standard_error_percent", "prob_practical_effect_ge_15_percent"
    ]
    writer = csv.DictWriter(f, fieldnames=fields)
    writer.writeheader()
    writer.writerows(power_records)
print(f"[+] Saved prospective power analysis table ({len(power_records)} scenarios) to prospective_power_analysis.csv")

print("\n[+] Phase 8.2 statistical verification and prospective power calculations completed successfully!")
