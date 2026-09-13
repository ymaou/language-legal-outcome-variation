# -*- coding: utf-8 -*-
"""Cost ledger. After every session, run.py calls record(), which rewrites raw/COSTS.md and raw/costs.csv
from the logs of every run under raw/: per run and provider, calls, tokens and the cost computed from the
list prices in config.py. Dry runs are listed but marked and excluded from the totals.

The figures are computed, not billed. The providers' own dashboards are the authority; compare after each
session.  python scripts/costs.py   rebuilds the ledger by hand.
"""
import csv
import json
from collections import defaultdict
from datetime import datetime, timezone

from config import RAW


def record(run=None, mode=None, dry=None):
    rows = []
    for run_dir in sorted(p for p in RAW.iterdir() if p.is_dir() and (p / "raw.jsonl").exists()):
        manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8")) if (run_dir / "manifest.json").exists() else {}
        agg = defaultdict(lambda: {"calls": 0, "input": 0, "cached": 0, "output": 0, "reasoning": 0, "usd": 0.0,
                                   "first": None, "last": None, "dry": False})
        with open(run_dir / "raw.jsonl", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                if r.get("kind") != "draw":
                    continue
                a = agg[r["provider"]]
                u = r.get("usage") or {}
                a["calls"] += 1
                a["input"] += u.get("input_total") or 0
                a["cached"] += u.get("cached_input") or 0
                a["output"] += u.get("output") or 0
                a["reasoning"] += u.get("reasoning") or 0
                a["usd"] += r.get("cost_usd") or 0.0
                a["dry"] = a["dry"] or bool(r.get("dry_run"))
                a["first"] = min(a["first"] or r["started_utc"], r["started_utc"])
                a["last"] = max(a["last"] or r["ended_utc"], r["ended_utc"])
        for provider, a in sorted(agg.items()):
            rows.append([run_dir.name, manifest.get("mode", ""), provider, "yes" if a["dry"] else "no", a["calls"],
                         a["input"], a["cached"], a["output"], a["reasoning"], round(a["usd"], 4), a["first"], a["last"]])
    headers = ["run", "mode", "provider", "dry run", "calls", "input tokens", "of which cached", "output tokens",
               "of which reasoning", "cost USD (list prices)", "first call (UTC)", "last call (UTC)"]
    with open(RAW / "costs.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(headers)
        w.writerows(rows)
    real = [r for r in rows if r[3] == "no"]
    by_provider = defaultdict(float)
    for r in real:
        by_provider[r[2]] += r[9]
    lines = [f"# Cost ledger (computed from list prices; the providers' dashboards are the authority)", "",
             f"Rebuilt {datetime.now(timezone.utc).isoformat(timespec='seconds')}.", "",
             "## Real spend, all runs", "", "| provider | USD |", "|---|---|"]
    lines += [f"| {p} | {v:.2f} |" for p, v in sorted(by_provider.items())]
    lines += [f"| **total** | **{sum(by_provider.values()):.2f}** |", "", "## By run and provider", "",
              "| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    lines += ["| " + " | ".join(str(v) for v in r) + " |" for r in rows]
    (RAW / "COSTS.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if run is not None:
        this = [r for r in rows if r[0] == run]
        print("cost this run so far" + (" (dry run, no money)" if dry else "") + ": " +
              ", ".join(f"{r[2]} ${r[9]:.2f}" for r in this) + f" | ledger: {RAW / 'COSTS.md'}")


if __name__ == "__main__":
    record()
    print("ledger rebuilt:", RAW / "COSTS.md")
