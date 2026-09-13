# -*- coding: utf-8 -*-
"""Checks on the measures against hand-worked values.  python scripts/test_measures.py"""
import math

import measures as M


def close(a, b, tol=1e-4):
    return abs(a - b) < tol


def main():
    checks = []
    add = lambda name, ok: checks.append((name, bool(ok)))

    add("modal: clear winner", M.modal([1, 1, 2]) == 1)
    add("modal: two-way tie is no clear answer", M.modal([1, 2]) == M.NONE)
    add("modal: tie for most among three", M.modal([1, 1, 2, 2, 3]) == M.NONE)
    add("modal: 11/10/4 has a clear mode though no majority", M.modal([1] * 11 + [2] * 10 + [3] * 4) == 1)
    add("strict majority: 11/10/4 has none", M.strict_majority([1] * 11 + [2] * 10 + [3] * 4) == M.NONE)
    add("strict majority: 13 of 25", M.strict_majority([1] * 13 + [3] * 12) == 1)
    add("no clear answer against no clear answer is not a flip", (M.NONE != M.NONE) is False)
    add("grant share counts options 1 and 2", close(M.grant_share([1, 2, 3, 4]), 0.5))

    s = M.splits(50, 200, 7)
    add("splits: 200 halvings", len(s) == 200)
    add("splits: halves disjoint and complete", all(sorted(a + b) == list(range(50)) and len(a) == 25 for a, b in s))
    add("splits: reproducible from the seed", s == M.splits(50, 200, 7))

    halves = M.splits(50, 200, 1)
    r = M.per_case_rates([1] * 50, {"en": [1] * 25, "bt": [3] * 25}, halves)
    add("rates: identical Greek halves give F = 0", r["F"] == 0)
    add("rates: arm agreeing with Greek gives 0", r["en"] == 0)
    add("rates: arm disagreeing with Greek gives 1", r["bt"] == 1)

    held, mismatched = M.ground_mismatch([1] * 50, [1] * 50, [1] * 25, [3] * 25, halves)
    add("RQ3: disposal holds in every comparison", held == 400)
    add("RQ3: ground differs in every comparison", mismatched == 400)
    held, _ = M.ground_mismatch([1] * 50, [1] * 50, [3] * 25, [1] * 25, halves)
    add("RQ3: no holding comparisons when disposal differs", held == 0)

    lo, hi = M.wilson(0.5, 10)
    add("Wilson 5/10 = [0.2366, 0.7634]", close(lo, 0.2366) and close(hi, 0.7634))
    add("sign test 9 against 1: p = 0.0215", close(M.sign_test(9, 1), 0.021484375))
    add("sign test 5 against 5: p = 1", M.sign_test(5, 5) == 1.0)
    p, w, n = M.wilcoxon_exact([1, 2, 3, 4, 5])
    add("Wilcoxon all positive, n = 5: p = 0.0625", close(p, 0.0625) and w == 15 and n == 5)
    p, _, _ = M.wilcoxon_exact([0.04, -0.04, 0.08, -0.08])
    add("Wilcoxon symmetric: p = 1", close(p, 1.0))
    add("MCC perfect = 1", close(M.mcc([1, 2, 3, 1], [1, 2, 3, 1]), 1.0))
    add("MCC inverted binary = -1", close(M.mcc([1, 1, 3, 3], [3, 3, 1, 1]), -1.0))
    add("MCC constant prediction = 0", close(M.mcc([1, 2, 3, 1], [1, 1, 1, 1]), 0.0))
    lo, hi = M.bootstrap_mean_ci([0.1] * 10, 1000, 3)
    add("bootstrap of a constant is that constant", close(lo, 0.1) and close(hi, 0.1))
    add("mean ignores NaN", close(M.mean([1.0, float("nan"), 3.0]), 2.0))

    for name, ok in checks:
        print(f"{'PASS' if ok else 'FAIL'}  {name}")
    failed = sum(not ok for _, ok in checks)
    print(f"\n{len(checks) - failed}/{len(checks)} passed")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
