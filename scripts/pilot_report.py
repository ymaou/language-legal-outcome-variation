# -*- coding: utf-8 -*-
"""Pilot report (study design v8, section 10.10): whether replies parse, arrive in the arm's language and
are complete; tokens, cost and time per call; and the projection of the full run under the budget rule of
section 10.3. It never reads or shows a disposal or a ground.

    python scripts/pilot_report.py --run pilot-1
"""
import argparse
import json
import statistics as st
from collections import Counter, defaultdict

import prompts
from config import ARMS, BUDGET_EUR, CASES, CEILING_EUR, CONCURRENCY, CONFIGS, GREEK_ARM, PRICES, RAW

MARGIN = 1.05  # allowance for replacement draws


def mean(values):
    values = [v for v in values if v is not None]
    return st.mean(values) if values else 0.0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    a = ap.parse_args()
    run_dir = RAW / a.run
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    records = [json.loads(line) for line in open(run_dir / "raw.jsonl", encoding="utf-8") if line.strip()]
    draws = [r for r in records if r["kind"] == "draw"]
    errors = [r for r in records if r["kind"] == "error"]
    lines = [f"# Pilot report: {a.run}", "",
             f"Dry run: {draws[0]['dry_run'] if draws else 'n/a'}. Calls with a reply: {len(draws)}. "
             f"Transport errors (retried, not draws): {len(errors)}. "
             f"Spent: ${sum(r.get('cost_usd', 0.0) for r in records):.2f}.", ""]

    lines += ["## Replies, by configuration and arm", "",
              "| configuration | arm | calls | ok | other statuses | keys as asked / fallback / other | "
              "fields in order | mean input tokens | cached share after 1st call | mean output tokens | "
              "mean reasoning tokens | mean seconds |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    groups = defaultdict(list)
    for r in draws:
        groups[(r["config"], r["arm"])].append(r)
    for (cfg, arm), rs in sorted(groups.items()):
        st_counts = Counter(r["parse"]["status"] for r in rs)
        keys = Counter(r["parse"]["keys"] for r in rs)
        order = sum(1 for r in rs if r["parse"]["field_order_as_asked"])
        later = [r for r in rs if r["draw_index"] > 0 and r["usage"].get("input_total")]
        cached_share = mean([r["usage"]["cached_input"] / r["usage"]["input_total"] for r in later])
        other = ", ".join(f"{s} {n}" for s, n in st_counts.items() if s != "ok") or "none"
        lines.append(f"| {cfg} | {arm} | {len(rs)} | {st_counts.get('ok', 0)} | {other} | "
                     f"{keys.get('as_asked', 0)} / {keys.get('fallback', 0)} / {keys.get('other', 0)} | "
                     f"{order} | {mean([r['usage'].get('input_total') for r in rs]):,.0f} | {cached_share:.0%} | "
                     f"{mean([r['usage'].get('output') for r in rs]):,.0f} | "
                     f"{mean([r['usage'].get('reasoning') for r in rs]):,.0f} | "
                     f"{mean([r['latency_s'] for r in rs]):.1f} |")

    # Projection of the full run from the pilot's measured tokens.
    chars = {(case, arm): sum(len(x) for x in prompts.build(arm, case)) for case in CASES for arm in ARMS}
    lines += ["", "## Projection of the full run", "",
              "Input tokens are scaled from the pilot's tokens per character for each configuration and arm to "
              "every case; output and reasoning tokens are the pilot means for that configuration and arm; draws "
              "after the first in each block are charged at the cached share observed in the pilot; "
              f"{MARGIN - 1:.0%} is added for replacement draws. Dollars are compared with euros as they stand.", "",
              "| configuration | cost at 31 draws (Greek 62) | cost at 25 draws (Greek 50) | calls at 31 | "
              "hours at 31, at current concurrency |", "|---|---|---|---|---|"]
    totals = {31: 0.0, 25: 0.0}
    for cfg in manifest["configs"]:
        model = CONFIGS[cfg]["model"]
        price = PRICES[model]
        cost = {31: 0.0, 25: 0.0}
        calls31, secs = 0, []
        for arm in ARMS:
            rs = groups.get((cfg, arm), [])
            if not rs:
                continue
            tpc = mean([r["usage"]["input_total"] / next(b["prompt_chars"] for b in manifest["blocks"]
                                                           if b["block"] == r["block"]) for r in rs])
            out = mean([r["usage"].get("output") for r in rs])
            later = [r for r in rs if r["draw_index"] > 0 and r["usage"].get("input_total")]
            share = mean([r["usage"]["cached_input"] / r["usage"]["input_total"] for r in later])
            secs.append(mean([r["latency_s"] for r in rs]))
            first_price = price["cache_write"] if CONFIGS[cfg]["provider"] == "anthropic" else price["input"]
            for k in (31, 25):
                kk = 2 * k if arm == GREEK_ARM else k
                for case in CASES:
                    tokens = chars[(case, arm)] * tpc
                    cost[k] += (tokens * first_price
                                + (kk - 1) * tokens * ((1 - share) * price["input"] + share * price["cached"])
                                + kk * out * price["output"]) / 1e6
                if k == 31:
                    calls31 += kk * len(CASES)
        for k in (31, 25):
            cost[k] *= MARGIN
            totals[k] += cost[k]
        provider = CONFIGS[cfg]["provider"]
        hours = calls31 * mean(secs) / CONCURRENCY.get(provider, 1) / 3600
        lines.append(f"| {cfg} | ${cost[31]:.2f} | ${cost[25]:.2f} | {calls31:,} | {hours:.1f} |")
    lines.append(f"| **all** | **${totals[31]:.2f}** | **${totals[25]:.2f}** | | |")

    if totals[31] <= BUDGET_EUR:
        verdict = f"Run at 31 draws: projection within the €{BUDGET_EUR} budget."
    elif totals[25] <= BUDGET_EUR:
        verdict = f"Run at 25 draws: 31 exceeds €{BUDGET_EUR}, 25 is within it."
    elif totals[25] <= CEILING_EUR:
        verdict = f"Run at 25 draws, above the €{BUDGET_EUR} budget but within the €{CEILING_EUR} ceiling."
    else:
        verdict = f"Do not start: 25 draws exceed the €{CEILING_EUR} ceiling. The author decides."
    lines += ["", f"**Under the budget rule (v8 section 10.3): {verdict}**",
              "", "Hours assume no rate limit binds; providers running in parallel, so the run takes about the "
              "longest of the three."]

    spent = sum(r.get("cost_usd", 0.0) for r in records)
    lines += ["", f"**Pilot cost, computed from list prices: ${spent:.2f}** for {len(draws)} replies. "
              "Compare with the providers' dashboards; the ledger is raw/COSTS.md."]
    report = "\n".join(lines) + "\n"
    (run_dir / "pilot_report.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
