# -*- coding: utf-8 -*-
"""Keyword screen of the models' reasoning (not hand coding). For every valid reply in a run, whether the
reasoning text matches each consideration's pattern, in Greek, English and German; reported as the share of
replies per model, overall, among dismissals and among grants. Writes results/<run>/paper/T3_considerations.csv
and prints the share of grants and dismissals that mention limb (b).

    python scripts/keyword_screen.py --run main-1
"""
import argparse
import csv
import re

from config import RESULTS

CONFIGS = ("terra", "terra-off", "sonnet", "gemini")
PATTERNS = {
    "disputed facts / conflicting evidence": r"αμφισβητ|αντικρου|διαφων|disput|conflict|contest|streitig|widersprüch|bestritten|umstritten",
    "credibility / cross-examination": r"αξιοπιστ|αντεξέτασ|credib|cross-exam|glaubwürdig|kreuzverhör",
    "trial or full hearing needed": r"\bδίκη|πλήρη ακρόαση|\btrial\b|full hearing|hauptverhandlung|\bverhandlung\b|mündliche",
    "fanciful / realistic distinction": r"φανταστ|εξωπραγματ|ρεαλιστ|fancif|realistic|merely arguable|phantast|realistisch|bloß",
    "documents / expert evidence needed": r"πραγματογνωμ|expert|sachverständ|gutacht",
    "real prospect (the limb (a) phrase)": r"πραγματικ\w* προοπτικ|real prospect|realistische erfolgsaussicht",
    "compelling reason (the limb (b) phrase)": r"επιτακτικ\w* λόγ|compelling reason|zwingend\w* grund",
    "mini-trial": r"mini[- ]?trial|μίνι[- ]?δίκη|mini-verhandlung|summarische verhandlung",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    a = ap.parse_args()
    with open(RESULTS / a.run / "csv" / "draws.csv", encoding="utf-8-sig") as f:
        draws = [r for r in csv.DictReader(f) if r["status"] == "ok"]
    rows = []
    for cfg in CONFIGS:
        rs = [r for r in draws if r["configuration"] == cfg]
        if not rs:
            continue
        dismissed = [r for r in rs if r["outcome"] == "3"]
        granted = [r for r in rs if r["outcome"] in ("1", "2")]
        for name, pattern in PATTERNS.items():
            rx = re.compile(pattern, re.I)
            share = lambda xs: sum(1 for r in xs if rx.search(r["reasoning"])) / len(xs) if xs else float("nan")
            rows.append([cfg, name, round(share(rs), 3), round(share(dismissed), 3),
                         round(share(granted), 3) if granted else "n/a", len(granted)])
    out = RESULTS / a.run / "paper"
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "T3_considerations.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["configuration", "consideration", "share of all replies", "share of dismissals", "share of grants", "n grants"])
        w.writerows(rows)
    limb_b = re.compile(PATTERNS["compelling reason (the limb (b) phrase)"], re.I)
    granted = [r for r in draws if r["outcome"] in ("1", "2")]
    dismissed = [r for r in draws if r["outcome"] == "3"]
    g = sum(1 for r in granted if limb_b.search(r["reasoning"]))
    d = sum(1 for r in dismissed if limb_b.search(r["reasoning"]))
    print(f"limb (b) mentioned: grants {g}/{len(granted)} ({g / len(granted):.0%}); "
          f"dismissals {d}/{len(dismissed)} ({d / len(dismissed):.0%})")
    print("written:", out / "T3_considerations.csv")


if __name__ == "__main__":
    main()
