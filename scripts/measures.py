# -*- coding: utf-8 -*-
"""The measures of study design v8, sections 10.4 to 10.7, as plain functions. Standard library only.

Clarifications fixed here, where v8 leaves a choice open (recorded for the analysis plan):
- A block's draws in analysis are its first k valid replies, in draw order.
- The same 200 random halvings are used for every case and every model configuration.
- RQ3 counts a disposal as holding only where both sides have a clear modal option.
- The direction of a flip is the sign of the grant-share difference D for that case.
- Rates are averaged over splits within each case, then over cases; intervals treat the ten cases as n.
"""
import math
import random
from collections import Counter
from itertools import product

NONE = "none"  # no clear answer: two or more options tie for the most draws
RELIEF = {1, 2}


def mean(values):
    values = [v for v in values if v is not None and not (isinstance(v, float) and math.isnan(v))]
    return sum(values) / len(values) if values else float("nan")


def modal(values):
    """The option chosen by the most draws; NONE if two or more tie for most, or if there are no draws."""
    if not values:
        return NONE
    ranked = Counter(values).most_common()
    if len(ranked) > 1 and ranked[0][1] == ranked[1][1]:
        return NONE
    return ranked[0][0]


def modal_share(values):
    return Counter(values).most_common(1)[0][1] / len(values) if values else float("nan")


def strict_majority(values):
    """An option held by more than half the draws; otherwise NONE."""
    if not values:
        return NONE
    value, count = Counter(values).most_common(1)[0]
    return value if count > len(values) / 2 else NONE


def relief(values):
    return ["relief" if v in RELIEF else "no relief" for v in values]


def grant_share(values):
    return sum(v in RELIEF for v in values) / len(values) if values else float("nan")


def splits(n, n_splits, seed):
    """n_splits random halvings of positions 0..n-1 (n even), reproducible from the seed."""
    rng = random.Random(seed)
    out = []
    for _ in range(n_splits):
        idx = list(range(n))
        rng.shuffle(idx)
        out.append((sorted(idx[: n // 2]), sorted(idx[n // 2:])))
    return out


def per_case_rates(greek, arms, halves, summarise=modal):
    """For one case and one model configuration.
    F: share of halvings in which the two Greek halves differ.
    For each arm: share of (halving, half) comparisons in which a Greek half differs from the arm."""
    arm_values = {a: summarise(v) for a, v in arms.items()}
    floor, acc = 0.0, {a: 0.0 for a in arms}
    for first, second in halves:
        m1 = summarise([greek[i] for i in first])
        m2 = summarise([greek[i] for i in second])
        floor += m1 != m2
        for a, value in arm_values.items():
            acc[a] += ((m1 != value) + (m2 != value)) / 2
    n = len(halves) or 1
    return {"F": floor / n, **{a: acc[a] / n for a in arms}}


def ground_mismatch(greek_disposals, greek_grounds, arm_disposals, arm_grounds, halves):
    """RQ3 for one case: over every (halving, half) comparison in which the modal disposal holds (the same
    clear option in the Greek half and the arm), count those whose modal ground differs. A tied ground on
    either side counts as a mismatch. Returns (comparisons holding, of which mismatched)."""
    arm_disposal, arm_ground = modal(arm_disposals), modal(arm_grounds)
    holding = mismatched = 0
    for first, second in halves:
        for positions in (first, second):
            disposal = modal([greek_disposals[i] for i in positions])
            if disposal != NONE and disposal == arm_disposal:
                holding += 1
                ground = modal([greek_grounds[i] for i in positions])
                if ground == NONE or arm_ground == NONE or ground != arm_ground:
                    mismatched += 1
    return holding, mismatched


def wilson(p, n, z=1.959963984540054):
    if not n or p is None or (isinstance(p, float) and math.isnan(p)):
        return float("nan"), float("nan")
    denominator = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / denominator
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denominator
    return max(0.0, centre - half), min(1.0, centre + half)


def bootstrap_mean_ci(values, n_boot, seed, level=0.95):
    """Percentile interval for the mean, resampling the values (cases) with replacement."""
    values = [v for v in values if not (isinstance(v, float) and math.isnan(v))]
    if not values:
        return float("nan"), float("nan")
    rng = random.Random(seed)
    n = len(values)
    means = sorted(sum(values[rng.randrange(n)] for _ in range(n)) / n for _ in range(n_boot))
    lo = means[int(round((1 - level) / 2 * (n_boot - 1)))]
    hi = means[int(round((1 + level) / 2 * (n_boot - 1)))]
    return lo, hi


def sign_test(n_positive, n_negative):
    """Exact two-sided binomial sign test."""
    n = n_positive + n_negative
    if n == 0:
        return float("nan")
    k = min(n_positive, n_negative)
    return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n)


def wilcoxon_exact(differences):
    """Exact two-sided Wilcoxon signed-rank test; zeros dropped, tied absolute values given average ranks.
    Returns (p, W+, number of non-zero differences)."""
    d = [round(x, 10) for x in differences if not (isinstance(x, float) and math.isnan(x))]
    d = [x for x in d if x != 0]
    n = len(d)
    if n == 0:
        return float("nan"), 0.0, 0
    order = sorted(range(n), key=lambda i: abs(d[i]))
    ranks = [0.0] * n
    i = 0
    while i < n:
        j = i
        while j + 1 < n and abs(d[order[j + 1]]) == abs(d[order[i]]):
            j += 1
        for t in range(i, j + 1):
            ranks[order[t]] = (i + j) / 2 + 1
        i = j + 1
    w_plus = sum(r for r, x in zip(ranks, d) if x > 0)
    expected = sum(ranks) / 2
    observed = abs(w_plus - expected)
    extreme = sum(1 for signs in product((0, 1), repeat=n)
                  if abs(sum(r for r, s in zip(ranks, signs) if s) - expected) >= observed - 1e-9)
    return min(1.0, extreme / 2 ** n), w_plus, n


def mcc(truth, predicted):
    """Matthews correlation coefficient for any number of classes (Gorodkin's generalisation)."""
    n = len(truth)
    if n == 0:
        return float("nan")
    labels = set(truth) | set(predicted)
    t, p = Counter(truth), Counter(predicted)
    correct = sum(1 for a, b in zip(truth, predicted) if a == b)
    numerator = correct * n - sum(t[k] * p[k] for k in labels)
    denominator = math.sqrt((n * n - sum(p[k] ** 2 for k in labels)) * (n * n - sum(t[k] ** 2 for k in labels)))
    return numerator / denominator if denominator else 0.0
