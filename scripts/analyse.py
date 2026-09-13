# -*- coding: utf-8 -*-
"""Analysis of a main run, as specified in study design v8, sections 10.4 to 10.7, written and frozen before
the run. Writes results/<run>/results.xlsx (one tab per table, and an 'About' tab explaining each),
the same tables as CSV files in results/<run>/csv/, and a readable summary, results/<run>/report.md.

Refuses to analyse a pilot run (v8 section 10.10). The court's order is read here and nowhere else, from the
private coding sheet given with --court, and only its columns case_id, disposal, partial and disposal_ground.

    python scripts/analyse.py --run main-1 --court "<path to the coding sheet>"
    python scripts/analyse.py --run main-1 --court "<path>" --strata strata.csv   (optional: case_id,stratum)
"""
import argparse
import csv
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

import measures as M
from config import (ARMS, BOOT_SEED, CONFIGS, COURT_DISPOSAL, COURT_GROUND, GREEK_ARM, GROUND_LABELS, N_BOOT,
                    N_SPLITS, OPTION_LABELS, RESULTS, SPLIT_SEED)
from load_results import load_run
from tables import write_csv, write_workbook

COMPARED = ("bt-en", "bt-de", "en", "de-lit")
DEFINITIONS = {
    "modal": ("primary: modal disposal (v8 10.4)", M.modal, None),
    "strict": ("secondary: strict majority (v8 10.4)", M.strict_majority, None),
    "binary": ("secondary: relief (options 1-2) against none (3-4) (v8 10.4)", M.modal, M.relief),
    "failcat": ("check: failed draws counted as a category of their own (v8 14)", M.modal, None),
}
RATES = [("F", "noise floor: Greek half against Greek half"),
         ("W_en", "rewording via English: Greek half against BT-en"),
         ("L_EN", "language: Greek half against EN"),
         ("W_de", "rewording via German: Greek half against BT-de"),
         ("L_DE", "German language: Greek half against DE-lit")]
DIFFERENCES = [("delta_EN", "estimand RQ1: L_EN - W_en"),
               ("delta_DE", "German analogue: L_DE - W_de"),
               ("L_EN_minus_F", "L_EN - F")]
_halvings = {}


def fmt(x, digits=2):
    return "n/a" if x is None or (isinstance(x, float) and math.isnan(x)) else f"{x:.{digits}f}"


def halvings(n):
    n -= n % 2
    if n not in _halvings:
        _halvings[n] = M.splits(n, N_SPLITS, SPLIT_SEED)
    return _halvings[n]


def outcomes(block, field="outcome"):
    return [r["parse"][field] for r in block["valid"]]


def originals_with_failures(block):
    return [r["parse"]["outcome"] if r["parse"]["status"] == "ok" else "failed"
            for r in block["draws"] if not r["is_replacement"]]


def case_measures(cfg, case, blocks):
    B = {arm: blocks[(cfg, case, arm)] for arm in ARMS}
    row = {"config": cfg, "model": CONFIGS[cfg]["model"], "reasoning": CONFIGS[cfg]["reasoning"], "case": case}
    for arm in ARMS:
        row[f"valid {arm}"] = f"{len(B[arm]['valid'])}/{B[arm]['k']}"
    row["complete"] = all(len(B[a]["valid"]) == B[a]["k"] for a in ARMS)
    greek = outcomes(B[GREEK_ARM])
    row["usable"] = bool(greek)
    if not greek:
        return row
    for name, (_, summarise, transform) in DEFINITIONS.items():
        if name == "failcat":
            g = originals_with_failures(B[GREEK_ARM])
            arms = {a: originals_with_failures(B[a]) for a in COMPARED}
        else:
            t = transform or (lambda v: v)
            g = t(greek)
            arms = {a: t(outcomes(B[a])) for a in COMPARED}
        r = M.per_case_rates(g, arms, halvings(len(g)), summarise)
        row.update({f"{name}:F": r["F"], f"{name}:W_en": r["bt-en"], f"{name}:L_EN": r["en"],
                    f"{name}:W_de": r["bt-de"], f"{name}:L_DE": r["de-lit"],
                    f"{name}:delta_EN": r["en"] - r["bt-en"], f"{name}:delta_DE": r["de-lit"] - r["bt-de"],
                    f"{name}:L_EN_minus_F": r["en"] - r["F"]})
    modal_all = {arm: M.modal(outcomes(B[arm])) for arm in ARMS}
    for arm in ARMS:
        row[f"modal {arm}"] = modal_all[arm]
        row[f"share {arm}"] = M.modal_share(outcomes(B[arm]))
    row["EN vs BT-en"] = float(modal_all["en"] != modal_all["bt-en"])
    row["DE-lit vs BT-de"] = float(modal_all["de-lit"] != modal_all["bt-de"])
    row["DE-lit vs DE-eng"] = float(modal_all["de-lit"] != modal_all["de-eng"])
    english = outcomes(B["en"])
    row["D"] = M.grant_share(english) - M.grant_share(greek) if english else float("nan")
    if modal_all["en"] == modal_all[GREEK_ARM]:
        row["flip direction"] = "no flip"
    elif row["D"] > 0:
        row["flip direction"] = "towards granting"
    elif row["D"] < 0:
        row["flip direction"] = "towards refusing"
    else:
        row["flip direction"] = "flip, grant share unchanged"
    greek_grounds = outcomes(B[GREEK_ARM], "ground")
    for arm in ("en", "bt-en"):
        holding, mismatched = M.ground_mismatch(greek, greek_grounds, outcomes(B[arm]), outcomes(B[arm], "ground"),
                                                halvings(len(greek)))
        row[f"ground holding {arm}"] = holding
        row[f"ground mismatched {arm}"] = mismatched
    return row


def read_court(path):
    import openpyxl
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    rows = wb["coding"].iter_rows(values_only=True)
    header = [str(h).strip() if h else "" for h in next(rows)]
    missing = [c for c in ("case_id", "disposal", "partial", "disposal_ground") if c not in header]
    if missing:
        sys.exit(f"court sheet: missing column(s) {missing}")
    col = {c: header.index(c) for c in ("case_id", "disposal", "partial", "disposal_ground")}
    court = {}
    for r in rows:
        case = r[col["case_id"]]
        if not case:
            continue
        option = COURT_DISPOSAL.get(str(r[col["disposal"]]).strip())
        if option is None:
            sys.exit(f"court sheet: disposal for {case} is not one of {sorted(COURT_DISPOSAL)}")
        if option == 1 and str(r[col["partial"]] or "").strip().lower() == "yes":
            option = 2
        court[str(case).strip()] = {"option": option, "ground": COURT_GROUND.get(str(r[col["disposal_ground"]]).strip())}
    return court


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--court", help="path to the private coding sheet; without it the sensitivity check is skipped")
    ap.add_argument("--strata", help="optional CSV with columns case_id,stratum, for descriptive tables by stratum")
    a = ap.parse_args()

    manifest, blocks, records = load_run(a.run)
    if manifest["mode"] == "pilot":
        sys.exit("a pilot run is not analysed (v8 section 10.10)")
    configs, cases = list(manifest["configs"]), manifest["cases"]
    dry = any(r.get("dry_run") for r in records if r.get("kind") == "draw")
    out_dir = RESULTS / a.run
    (out_dir / "csv").mkdir(parents=True, exist_ok=True)

    per_case = [case_measures(cfg, case, blocks) for cfg in configs for case in cases]
    by_cfg = defaultdict(list)
    for r in per_case:
        if r["usable"]:
            by_cfg[r["config"]].append(r)
    incomplete = [f"{r['config']} {r['case']}" for r in per_case if not r["complete"]]

    # Rates, under each definition
    rate_rows = []
    for name, (label, _, _) in DEFINITIONS.items():
        for cfg in configs:
            rows = by_cfg[cfg]
            n = len(rows)
            for key, what in RATES:
                value = M.mean([r[f"{name}:{key}"] for r in rows])
                lo, hi = M.wilson(value, n)
                rate_rows.append([label, cfg, CONFIGS[cfg]["model"], CONFIGS[cfg]["reasoning"], key, what, n, value, lo, hi,
                                  "Wilson, n = cases"])
            for key, what in DIFFERENCES:
                values = [r[f"{name}:{key}"] for r in rows]
                lo, hi = M.bootstrap_mean_ci(values, N_BOOT, BOOT_SEED)
                rate_rows.append([label, cfg, CONFIGS[cfg]["model"], CONFIGS[cfg]["reasoning"], key, what, n, M.mean(values),
                                  lo, hi, f"paired bootstrap over cases, {N_BOOT:,} resamples"])
    rate_headers = ["definition", "configuration", "model", "reasoning", "measure", "what it compares", "cases",
                    "value", "95% CI low", "95% CI high", "interval"]

    # Secondary contrasts
    contrast_rows = []
    for cfg in configs:
        rows = by_cfg[cfg]
        for key, what in (("EN vs BT-en", "language contrast with one translation step between the texts"),
                          ("DE-lit vs BT-de", "the German analogue"),
                          ("DE-lit vs DE-eng", "the vocabulary contrast")):
            value = M.mean([r[key] for r in rows])
            lo, hi = M.wilson(value, len(rows))
            contrast_rows.append([cfg, CONFIGS[cfg]["model"], CONFIGS[cfg]["reasoning"], key, what, len(rows), value, lo, hi])
    contrast_headers = ["configuration", "model", "reasoning", "contrast", "what it is", "cases",
                        "share of cases whose modal disposal differs", "95% CI low", "95% CI high"]

    # Direction, RQ2
    direction_rows = []
    for cfg in configs:
        rows = by_cfg[cfg]
        ds = [r["D"] for r in rows]
        lo, hi = M.bootstrap_mean_ci(ds, N_BOOT, BOOT_SEED)
        counts = Counter(r["flip direction"] for r in rows)
        p_sign = M.sign_test(counts["towards granting"], counts["towards refusing"])
        p_wilcoxon, w_plus, n_nonzero = M.wilcoxon_exact(ds)
        direction_rows.append([cfg, CONFIGS[cfg]["model"], CONFIGS[cfg]["reasoning"], len(rows), M.mean(ds), lo, hi,
                               counts["towards granting"], counts["towards refusing"],
                               counts["flip, grant share unchanged"], counts["no flip"], p_sign, p_wilcoxon, n_nonzero])
    direction_headers = ["configuration", "model", "reasoning", "cases", "mean D (EN grant share minus Greek)",
                         "95% CI low", "95% CI high", "flips towards granting", "flips towards refusing",
                         "flips, grant share unchanged", "no flip", "exact sign test p (two-sided)",
                         "Wilcoxon signed-rank p on D (exact)", "non-zero D"]

    # Stated ground, RQ3
    ground_rows = []
    for cfg in configs:
        rows = by_cfg[cfg]
        h_en, m_en = sum(r["ground holding en"] for r in rows), sum(r["ground mismatched en"] for r in rows)
        h_bt, m_bt = sum(r["ground holding bt-en"] for r in rows), sum(r["ground mismatched bt-en"] for r in rows)
        share_en = m_en / h_en if h_en else float("nan")
        share_bt = m_bt / h_bt if h_bt else float("nan")
        ground_rows.append([cfg, CONFIGS[cfg]["model"], CONFIGS[cfg]["reasoning"], h_en, m_en, share_en, h_bt, m_bt,
                            share_bt, share_en - share_bt if h_en and h_bt else float("nan")])
    ground_headers = ["configuration", "model", "reasoning", "comparisons holding: Greek half vs EN",
                      "of which ground differs", "share (EN)", "comparisons holding: Greek half vs BT-en",
                      "of which ground differs", "share (BT-en)", "difference (EN minus BT-en)"]

    # Sensitivity check, v8 10.6
    sensitivity_rows, sensitivity_case_rows = [], []
    court = read_court(a.court) if a.court else None
    if court:
        for cfg in configs:
            rows = [r for r in by_cfg[cfg] if r["case"] in court]
            truth = [court[r["case"]]["option"] for r in rows]
            predicted = [r[f"modal {GREEK_ARM}"] for r in rows]
            n = len(rows)
            accuracy = M.mean([float(t == p) for t, p in zip(truth, predicted)])
            baseline = max(Counter(truth).values()) / n if n else float("nan")
            bin_truth = M.relief(truth)
            bin_pred = [M.NONE if p == M.NONE else M.relief([p])[0] for p in predicted]
            bin_accuracy = M.mean([float(t == p) for t, p in zip(bin_truth, bin_pred)])
            bin_baseline = max(Counter(bin_truth).values()) / n if n else float("nan")
            sensitivity_rows.append([cfg, CONFIGS[cfg]["model"], CONFIGS[cfg]["reasoning"], n, accuracy, baseline,
                                     M.mcc(truth, predicted), bin_accuracy, bin_baseline, M.mcc(bin_truth, bin_pred)])
            for r, t, p in zip(rows, truth, predicted):
                sensitivity_case_rows.append([cfg, r["case"], t, OPTION_LABELS[t], p, OPTION_LABELS.get(p, "no clear answer"),
                                              r[f"share {GREEK_ARM}"], t == p, court[r["case"]]["ground"]])
    sensitivity_headers = ["configuration", "model", "reasoning", "cases", "accuracy (four options)",
                           "majority-class baseline", "MCC", "accuracy (relief / none)", "baseline (relief / none)",
                           "MCC (relief / none)"]
    sensitivity_case_headers = ["configuration", "case", "court option", "court order", "Greek modal (all Greek draws)",
                                "Greek modal, in words", "Greek modal share", "agree", "court ground (model's scale)"]

    # Per case
    case_headers = ["config", "model", "reasoning", "case", "complete"] + [f"valid {a}" for a in ARMS] + \
        [f"modal:{k}" for k, _ in RATES] + [f"modal:{k}" for k, _ in DIFFERENCES] + \
        ["EN vs BT-en", "DE-lit vs BT-de", "DE-lit vs DE-eng", "D", "flip direction"] + \
        [f"modal {a}" for a in ARMS] + [f"share {a}" for a in ARMS]
    case_rows = [[r.get(h) for h in case_headers] for r in per_case]

    # Strata, descriptive
    strata_rows = []
    if a.strata:
        with open(a.strata, encoding="utf-8-sig", newline="") as f:
            stratum = {row["case_id"].strip(): row["stratum"].strip() for row in csv.DictReader(f)}
        for cfg in configs:
            groups = defaultdict(list)
            for r in by_cfg[cfg]:
                groups[stratum.get(r["case"], "unassigned")].append(r)
            for s, rows in sorted(groups.items()):
                strata_rows.append([cfg, s, len(rows), M.mean([r["modal:W_en"] for r in rows]),
                                    M.mean([r["modal:L_EN"] for r in rows]), M.mean([r["modal:delta_EN"] for r in rows])])
    strata_headers = ["configuration", "stratum", "cases", "W_en", "L_EN", "delta_EN"]

    # Blocks, failures, tokens, draws
    block_rows, failure_rows, token_rows, draw_rows = [], [], [], []
    for cfg in configs:
        for arm in ARMS:
            arm_draws = [r for case in cases for r in blocks[(cfg, case, arm)]["draws"]]
            statuses = Counter(r["parse"]["status"] for r in arm_draws)
            calls = len(arm_draws)
            failure_rows.append([cfg, CONFIGS[cfg]["model"], arm, calls, statuses.get("ok", 0),
                                 (calls - statuses.get("ok", 0)) / calls if calls else float("nan"),
                                 ", ".join(f"{s} {n}" for s, n in sorted(statuses.items()) if s != "ok") or "none"])
            token_rows.append([cfg, CONFIGS[cfg]["model"], arm, calls,
                               M.mean([r["usage"].get("input_total") for r in arm_draws]),
                               M.mean([r["usage"]["cached_input"] / r["usage"]["input_total"]
                                       for r in arm_draws if r["usage"].get("input_total")]),
                               M.mean([r["usage"].get("output") for r in arm_draws]),
                               M.mean([r["usage"].get("reasoning") for r in arm_draws]),
                               sum(r.get("cost_usd", 0.0) for r in arm_draws)])
            for case in cases:
                b = blocks[(cfg, case, arm)]
                v, g = outcomes(b), outcomes(b, "ground")
                oc, gc = Counter(v), Counter(g)
                fails = Counter(r["parse"]["status"] for r in b["draws"] if r["parse"]["status"] != "ok")
                block_rows.append([cfg, CONFIGS[cfg]["model"], CONFIGS[cfg]["reasoning"], case, arm, b["k"], len(v)]
                                  + [oc.get(o, 0) for o in (1, 2, 3, 4)]
                                  + [M.modal(v), M.modal_share(v), M.strict_majority(v), M.grant_share(v)]
                                  + [gc.get(o, 0) for o in (1, 2, 3, 4, 5)]
                                  + [M.modal(g), ", ".join(f"{s} {n}" for s, n in sorted(fails.items())) or "none"])
            for r in arm_draws:
                p, u = r["parse"], r["usage"]
                draw_rows.append([r["config"], r["model_requested"], r.get("model_returned"), r["case"], r["arm"],
                                  r["prompt_lang"], r["draw_index"], r["is_replacement"], p["status"], p["outcome"],
                                  OPTION_LABELS.get(p["outcome"]), p["ground"], GROUND_LABELS.get(p["ground"]),
                                  p["reply_language"], p["keys"], p["field_order_as_asked"], r["reasoning_text"],
                                  r.get("finish"), u.get("input_total"), u.get("cached_input"), u.get("output"),
                                  u.get("reasoning"), r.get("cost_usd"), r.get("latency_s"), r.get("started_utc"),
                                  r.get("response_id")])
    block_headers = ["configuration", "model", "reasoning", "case", "arm", "k", "valid draws used", "option 1",
                     "option 2", "option 3", "option 4", "modal", "modal share", "strict majority", "grant share",
                     "ground 1", "ground 2", "ground 3", "ground 4", "ground 5", "modal ground", "failed draws"]
    failure_headers = ["configuration", "model", "arm", "calls with a reply", "valid", "failure rate", "failures by kind"]
    token_headers = ["configuration", "model", "arm", "calls", "mean input tokens", "mean cached share",
                     "mean output tokens", "mean reasoning tokens", "cost (USD)"]
    draw_headers = ["configuration", "model requested", "model returned", "case", "arm", "prompt language", "draw",
                    "replacement", "status", "outcome", "outcome in words", "ground", "ground in words",
                    "reply language", "field names", "fields in order", "reasoning", "finish", "input tokens",
                    "cached tokens", "output tokens", "reasoning tokens", "cost (USD)", "seconds", "started (UTC)",
                    "response id"]

    about_notes = [
        f"Results for run {a.run}{' - FABRICATED DRY-RUN DATA, NOT RESULTS' if dry else ''}.",
        f"Generated {datetime.now(timezone.utc).isoformat(timespec='seconds')} by scripts/analyse.py, as specified in "
        "study design v8, sections 10.4-10.7.",
        f"Draws per arm {manifest['draws_per_arm']}, Greek {manifest['greek_draws']}. Cases {len(cases)}. "
        f"Halvings {N_SPLITS} (seed {SPLIT_SEED}); bootstrap {N_BOOT:,} resamples (seed {BOOT_SEED}); "
        f"run order seed {manifest['order_seed']}.",
        "Incomplete blocks (fewer valid draws than k): " + (", ".join(incomplete) if incomplete else "none") + ".",
        "Read the numbers with the interpretation fixed in advance at v8 section 10.11. Ten cases: estimates and "
        "intervals, no equivalence claims.",
    ]
    tabs = [
        ("Rates", "F, W, L and the language effect, per model, under each definition (primary first)."),
        ("Contrasts", "Secondary contrasts between non-Greek arms."),
        ("Direction", "RQ2: whether English moves the disposal towards granting or refusing."),
        ("Ground", "RQ3: whether the stated ground changes where the disposal holds."),
        ("Sensitivity", "The precondition: Greek modal disposal against the court's order (only with --court)."),
        ("Sensitivity by case", "The same, case by case."),
        ("Per case", "Every measure for every case and model."),
        ("Strata", "Descriptive, by stratum (only with --strata)."),
        ("Blocks", "Counts of each option and ground in every case, arm and model."),
        ("Failures", "Failure rate per model and arm (v8 10.3)."),
        ("Tokens", "Tokens, reasoning tokens and cost per model and arm."),
        ("Draws", "Every reply, one row each, with its reasoning."),
    ]
    sheets = [
        {"name": "About", "headers": ["tab", "what it holds"], "rows": tabs, "notes": about_notes,
         "widths": {"tab": 22, "what it holds": 110}},
        {"name": "Rates", "headers": rate_headers, "rows": rate_rows, "widths": {"definition": 45, "what it compares": 42}},
        {"name": "Contrasts", "headers": contrast_headers, "rows": contrast_rows},
        {"name": "Direction", "headers": direction_headers, "rows": direction_rows},
        {"name": "Ground", "headers": ground_headers, "rows": ground_rows},
        {"name": "Sensitivity", "headers": sensitivity_headers, "rows": sensitivity_rows},
        {"name": "Sensitivity by case", "headers": sensitivity_case_headers, "rows": sensitivity_case_rows},
        {"name": "Per case", "headers": case_headers, "rows": case_rows},
        {"name": "Strata", "headers": strata_headers, "rows": strata_rows},
        {"name": "Blocks", "headers": block_headers, "rows": block_rows},
        {"name": "Failures", "headers": failure_headers, "rows": failure_rows, "widths": {"failures by kind": 50}},
        {"name": "Tokens", "headers": token_headers, "rows": token_rows},
        {"name": "Draws", "headers": draw_headers, "rows": draw_rows, "widths": {"reasoning": 90}, "wrap": ["reasoning"]},
    ]
    write_workbook(out_dir / "results.xlsx", sheets)
    for sheet in sheets[1:]:
        write_csv(out_dir / "csv" / (sheet["name"].lower().replace(" ", "_") + ".csv"), sheet["headers"], sheet["rows"])

    # Readable summary
    def rate(cfg, key, name="modal"):
        return next(r for r in rate_rows if r[1] == cfg and r[4] == key and r[0] == DEFINITIONS[name][0])

    lines = [f"# Results: {a.run}", ""]
    if dry:
        lines += ["**FABRICATED DRY-RUN DATA. THESE ARE NOT RESULTS.**", ""]
    lines += about_notes[1:4] + ["", "## Headline, primary definition (modal disposal)", "",
                                 "| configuration | F | W_en | L_EN | Δ_EN [95% CI] | Δ_DE [95% CI] | mean D [95% CI] | "
                                 "flips to granting / refusing | ground differs: EN / BT-en | sensitivity accuracy (baseline) |",
                                 "|---|---|---|---|---|---|---|---|---|---|"]
    for cfg in configs:
        d_en, d_de = rate(cfg, "delta_EN"), rate(cfg, "delta_DE")
        dr = next(r for r in direction_rows if r[0] == cfg)
        gr = next(r for r in ground_rows if r[0] == cfg)
        sr = next((r for r in sensitivity_rows if r[0] == cfg), None)
        lines.append(f"| {cfg} | {fmt(rate(cfg, 'F')[7])} | {fmt(rate(cfg, 'W_en')[7])} | {fmt(rate(cfg, 'L_EN')[7])} | "
                     f"{fmt(d_en[7])} [{fmt(d_en[8])}, {fmt(d_en[9])}] | {fmt(d_de[7])} [{fmt(d_de[8])}, {fmt(d_de[9])}] | "
                     f"{fmt(dr[4])} [{fmt(dr[5])}, {fmt(dr[6])}] | {dr[7]} / {dr[8]} | {fmt(gr[5])} / {fmt(gr[8])} | "
                     + (f"{fmt(sr[4])} ({fmt(sr[5])})" if sr else "not run") + " |")
    lines += ["", "Every other table is in `results.xlsx`; the tab 'About' lists them. The same tables are in `csv/`.",
              "The error-coding workbook is made separately with `scripts/error_workbook.py`."]
    (out_dir / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nwritten: {out_dir / 'results.xlsx'}, {out_dir / 'report.md'}, {out_dir / 'csv'}")


if __name__ == "__main__":
    main()
