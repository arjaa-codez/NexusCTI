import math
import scipy.stats as stats

# 1. Verify Power calculation with exact McNemar test
N = 100
q = 0.25
theta = 0.80
alpha = 0.05

def exact_mcnemar_two_sided_p(b, nd):
    if nd == 0:
        return 1.0
    return min(1.0, 2.0 * float(stats.binom.cdf(min(b, nd - b), nd, 0.5)))

power = 0.0
for nd in range(N + 1):
    p_nd = stats.binom.pmf(nd, N, q)
    for b in range(nd + 1):
        p_b = stats.binom.pmf(b, nd, theta)
        joint = p_nd * p_b
        p_val = exact_mcnemar_two_sided_p(b, nd)
        if p_val <= alpha and b > (nd - b):
            power += joint

print(f"Computed Power (N={N}, q={q}, theta={theta}): {power * 100:.5f}%")
assert abs(power - 0.83674) < 0.0001, f"Power mismatch: {power}"
print("Power exactly matches 83.674%!")

# 2. Check Wilson score interval formula for Task B (N=30)
def wilson_score_interval(k, n, z=1.95996):
    if n == 0:
        return 0.0, 0.0
    p = k / n
    denom = 1.0 + (z**2) / n
    center = (p + (z**2) / (2 * n)) / denom
    margin = (z / denom) * math.sqrt(p * (1 - p) / n + (z**2) / (4 * n**2))
    return max(0.0, center - margin), min(1.0, center + margin)

print("Wilson score CI for 30/30 abstentions:", [round(x, 4) for x in wilson_score_interval(30, 30)])
print("Wilson score CI for 28/30 abstentions:", [round(x, 4) for x in wilson_score_interval(28, 30)])
