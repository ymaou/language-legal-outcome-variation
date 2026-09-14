# -*- coding: utf-8 -*-
"""The complete results package for a run: every comparison the design allows, as one Excel workbook (one tab
per table), the same tables as CSV, and figures as PDF and PNG. Reads results/<run>/csv/ (written by
analyse.py) and raw/<run>/manifest.json. Writes results/<run>/package/.

Tables: run summary; outcome distribution per model and arm; modal outcome per case for every model and arm
against the court; grant share per case; inter-model agreement per arm; agreement with the court per arm;
ground distribution per model and arm; modal ground per case; reply language and reliability per arm;
tokens, latency and cost per model and arm; flips (any arm against the Greek modal); rates under each
definition (from analyse.py); direction; stated ground.

    python scripts/results_package.py --run main-1
    python scripts/results_package.py --run predict-1
"""
import argparse
import csv
import json
from collections import Counter, defaultdict
from itertools import combinations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

import measures as M
from config import CONFIGS, GROUND_LABELS, OPTION_LABELS, RAW, RESULTS
from tables import write_csv, write_workbook

INK, INK2, MUTED, GRID, AXIS, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
RAMP = {1: "#104281", 2: "#2a78d6", 3: "#86b6ef", 4: "#cde2fb"}   # ordinal blue ramp, most relief darkest
GROUND_RAMP = {1: "#104281", 2: "#1c5cab", 3: "#2a78d6", 4: "#6da7ec", 5: "#b7d3f6"}
ARM_ORDER = ["gr", "bt-en", "en", "bt-de", "de-lit", "de-eng"]
ARM_LABEL = {"gr": "Greek", "bt-en": "BT via English", "en": "English", "bt-de": "BT via German",
             "de-lit": "German (plain terms)", "de-eng": "German (English terms)"}
CFG_LABEL = {"terra": "GPT-5.6 Terra", "terra-off": "GPT-5.6 Terra, reasoning off", "sonnet": "Claude Sonnet 5",
             "gemini": "Gemini 3.6 Flash"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": AXIS, "axes.linewidth": 0.6,
                     "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK, "axes.labelcolor": INK2,
                     "figure.facecolor": "white", "axes.facecolor": SURFACE, "savefig.facecolor": "white"})


def read(run, name):
    with open(RESULTS / run / "csv" / f"{name}.csv", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def label(v):
    return "no clear answer" if v in ("none", M.NONE) else f"{v} {OPTION_LABELS[int(v)]}"


def save(fig, out, stem):
    for ext in ("png", "pdf"):
        fig.savefig(out / f"{stem}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    a = ap.parse_args()
    run = a.run
    out = RESULTS / run / "package"
    out.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((RAW / run / "manifest.json").read_text(encoding="utf-8"))
    blocks = read(run, "blocks")
    draws = read(run, "draws")
    court = {r["case"]: r["court option"] for r in read(run, "sensitivity_by_case")}
    configs = [c for c in CFG_LABEL if any(b["configuration"] == c for b in blocks)]
    arms = [x for x in ARM_ORDER if any(b["arm"] == x for b in blocks)]
    cases = sorted({b["case"] for b in blocks})
    B = {(b["configuration"], b["case"], b["arm"]): b for b in blocks}
    sheets = []

    # 1. Run summary
    models_returned = Counter((r["configuration"], r["model returned"]) for r in draws)
    first = min(r["started (UTC)"] for r in draws)
    last = max(r["started (UTC)"] for r in draws)
    summary = [
        ["run", run], ["prompt set", manifest.get("prompt_set", "decide")], ["mode", manifest["mode"]],
        ["arms", ", ".join(arms)], ["cases", ", ".join(cases)],
        ["draws per arm (Greek)", f"{manifest['draws_per_arm']} ({manifest['greek_draws']})"],
        ["replies", len(draws)], ["valid replies", sum(r["status"] == "ok" for r in draws)],
        ["first call (UTC)", first], ["last call (UTC)", last],
        ["order seed", manifest["order_seed"]], ["protocol commit", manifest.get("git_commit", "")],
        ["max output tokens", manifest["max_output_tokens"]], ["not sent", ", ".join(manifest["not_sent"])],
        ["cost, computed at list prices (USD)", round(sum(float(r["cost (USD)"] or 0) for r in draws), 2)],
    ]
    for cfg in configs:
        c = CONFIGS[cfg]
        got = ", ".join(sorted(m for (k, m) in models_returned if k == cfg))
        summary.append([f"configuration {cfg}", f"{c['provider']} {c['model']}, reasoning {c['reasoning']}; identifier returned: {got}"])
    sheets.append({"name": "Run summary", "headers": ["item", "value"], "rows": summary, "widths": {"item": 36, "value": 110}})

    # 2. Outcome distribution per model and arm
    rows = []
    for cfg in configs:
        for arm in arms:
            bs = [B[(cfg, c, arm)] for c in cases]
            n = sum(int(b["valid draws used"]) for b in bs)
            counts = [sum(int(b[f"option {o}"]) for b in bs) for o in (1, 2, 3, 4)]
            rows.append([CFG_LABEL[cfg], ARM_LABEL[arm], n] + counts + [f"{x / n:.3f}" for x in counts]
                        + [f"{(counts[0] + counts[1]) / n:.3f}"])
    sheets.append({"name": "Outcomes by model and arm", "rows": rows, "headers":
                   ["model", "arm", "valid draws", "granted in full", "granted in part", "dismissed", "conditional order",
                    "share full", "share part", "share dismissed", "share conditional", "share granting relief"]})

    # 3. Modal outcome per case, every model and arm, against the court
    hdr = ["case", "court order"] + [f"{CFG_LABEL[cfg]} | {ARM_LABEL[arm]}" for cfg in configs for arm in arms]
    rows = [[c, label(court[c])] + [label(B[(cfg, c, arm)]["modal"]) for cfg in configs for arm in arms] for c in cases]
    sheets.append({"name": "Modal outcome per case", "headers": hdr, "rows": rows, "widths": {h: 22 for h in hdr}})

    # 4. Grant share per case
    rows = [[c, "yes" if court[c] in ("1", "2") else "no"] + [float(B[(cfg, c, arm)]["grant share"]) for cfg in configs for arm in arms] for c in cases]
    sheets.append({"name": "Grant share per case", "headers": ["case", "court granted"] + hdr[2:], "rows": rows, "widths": {h: 22 for h in hdr}})

    # 5. Inter-model agreement per arm (share of cases on which two configurations give the same modal outcome)
    rows = []
    for arm in arms:
        for a1, a2 in combinations(configs, 2):
            agree = sum(B[(a1, c, arm)]["modal"] == B[(a2, c, arm)]["modal"] for c in cases)
            rows.append([ARM_LABEL[arm], CFG_LABEL[a1], CFG_LABEL[a2], agree, len(cases), f"{agree / len(cases):.2f}"])
    sheets.append({"name": "Inter-model agreement", "rows": rows, "headers":
                   ["arm", "model A", "model B", "cases where modal outcomes agree", "cases", "share"]})

    # 6. Agreement with the court per arm (four options, and relief-versus-none), with MCC
    rows = []
    for cfg in configs:
        for arm in arms:
            truth = [int(court[c]) for c in cases]
            pred = [B[(cfg, c, arm)]["modal"] for c in cases]
            pred_i = [int(p) if p.isdigit() else M.NONE for p in pred]
            acc = sum(t == p for t, p in zip(truth, pred_i)) / len(cases)
            bt = M.relief(truth)
            bp = [M.NONE if p == M.NONE else M.relief([p])[0] for p in pred_i]
            rows.append([CFG_LABEL[cfg], ARM_LABEL[arm], f"{acc:.2f}", f"{M.mcc(truth, pred_i):.2f}",
                         f"{sum(t == p for t, p in zip(bt, bp)) / len(cases):.2f}", f"{M.mcc(bt, bp):.2f}",
                         f"{max(Counter(truth).values()) / len(cases):.2f}"])
    sheets.append({"name": "Agreement with court by arm", "rows": rows, "headers":
                   ["model", "arm", "accuracy (four options)", "MCC", "accuracy (relief or none)", "MCC (relief or none)",
                    "majority-class baseline"]})

    # 7. Ground distribution per model and arm
    rows = []
    for cfg in configs:
        for arm in arms:
            bs = [B[(cfg, c, arm)] for c in cases]
            n = sum(int(b["valid draws used"]) for b in bs)
            counts = [sum(int(b[f"ground {g}"]) for b in bs) for g in (1, 2, 3, 4, 5)]
            rows.append([CFG_LABEL[cfg], ARM_LABEL[arm], n] + counts + [f"{x / n:.3f}" for x in counts])
    sheets.append({"name": "Grounds by model and arm", "rows": rows, "headers":
                   ["model", "arm", "valid draws"] + [f"ground {g}: {GROUND_LABELS[g]}" for g in (1, 2, 3, 4, 5)]
                   + [f"share ground {g}" for g in (1, 2, 3, 4, 5)]})

    # 8. Modal ground per case
    rows = [[c] + [B[(cfg, c, arm)]["modal ground"] for cfg in configs for arm in arms] for c in cases]
    sheets.append({"name": "Modal ground per case", "headers": ["case"] + hdr[2:], "rows": rows, "widths": {h: 22 for h in hdr}})

    # 9. Reply language and reliability per model and arm
    rows = []
    for cfg in configs:
        for arm in arms:
            rs = [r for r in draws if r["configuration"] == cfg and r["arm"] == arm]
            st = Counter(r["status"] for r in rs)
            langs = Counter(r["reply language"] for r in rs if r["status"] in ("ok", "wrong_language"))
            keys = Counter(r["field names"] for r in rs)
            rows.append([CFG_LABEL[cfg], ARM_LABEL[arm], rs[0]["prompt language"], len(rs), st.get("ok", 0),
                         ", ".join(f"{k} {v}" for k, v in sorted(st.items()) if k != "ok") or "none",
                         ", ".join(f"{k} {v}" for k, v in sorted(langs.items())),
                         ", ".join(f"{k} {v}" for k, v in sorted(keys.items())),
                         sum(1 for r in rs if r["fields in order"] == "True")])
    sheets.append({"name": "Reliability by arm", "rows": rows, "headers":
                   ["model", "arm", "prompt language", "replies", "valid", "failures", "reply language", "field names",
                    "fields in asked order"]})

    # 10. Tokens, latency and cost per model and arm
    rows = []
    for cfg in configs:
        for arm in arms:
            rs = [r for r in draws if r["configuration"] == cfg and r["arm"] == arm]
            f = lambda k: [float(r[k]) for r in rs if r[k] not in ("", None)]
            mean = lambda xs: sum(xs) / len(xs) if xs else float("nan")
            rows.append([CFG_LABEL[cfg], ARM_LABEL[arm], len(rs), round(mean(f("input tokens"))),
                         f"{mean([float(r['cached tokens']) / float(r['input tokens']) for r in rs if float(r['input tokens'] or 0)]):.2f}",
                         round(mean(f("output tokens"))), round(mean(f("reasoning tokens"))) if f("reasoning tokens") else "n/a",
                         f"{mean(f('seconds')):.1f}", round(sum(f("cost (USD)")), 3)])
    sheets.append({"name": "Tokens and cost", "rows": rows, "headers":
                   ["model", "arm", "calls", "mean input tokens", "mean cached share", "mean output tokens",
                    "mean reasoning tokens (Sonnet: not separated)", "mean seconds", "cost (USD)"]})

    # 11. Flips: any arm whose modal outcome differs from the Greek modal
    rows = []
    for cfg in configs:
        for c in cases:
            g = B[(cfg, c, "gr")]
            for arm in arms:
                if arm == "gr":
                    continue
                b = B[(cfg, c, arm)]
                if b["modal"] != g["modal"]:
                    rows.append([CFG_LABEL[cfg], c, ARM_LABEL[arm], label(g["modal"]), f"{float(g['modal share']):.2f}",
                                 label(b["modal"]), f"{float(b['modal share']):.2f}", label(court[c])])
    sheets.append({"name": "Flips against Greek", "rows": rows, "headers":
                   ["model", "case", "arm", "Greek modal", "Greek modal share", "arm modal", "arm modal share", "court order"]})

    # 12-14. From analyse.py
    for name, tab in (("rates", "Rates (all definitions)"), ("direction", "Direction RQ2"), ("ground", "Stated ground RQ3")):
        rs = read(run, name)
        sheets.append({"name": tab, "headers": list(rs[0].keys()) if rs else [], "rows": [list(r.values()) for r in rs]})

    write_workbook(out / "results_package.xlsx", sheets)
    for s in sheets:
        write_csv(out / (s["name"].lower().replace(" ", "_").replace("(", "").replace(")", "") + ".csv"), s["headers"], s["rows"])

    # Figures
    # A. Outcome distribution: stacked bars per arm, one panel per model
    fig, axes = plt.subplots(1, len(configs), figsize=(1.7 * len(configs) + 1, 2.6), sharey=True)
    axes = list(axes) if len(configs) > 1 else [axes]
    for ax, cfg in zip(axes, configs):
        for j, arm in enumerate(arms):
            bs = [B[(cfg, c, arm)] for c in cases]
            n = sum(int(b["valid draws used"]) for b in bs)
            bottom = 0.0
            for o in (1, 2, 3, 4):
                share = sum(int(b[f"option {o}"]) for b in bs) / n
                if share > 0:
                    ax.bar(j, share, bottom=bottom, width=0.62, color=RAMP[o], linewidth=0, zorder=3)
                    ax.bar(j, min(0.006, share), bottom=bottom + share - min(0.006, share), width=0.62, color=SURFACE, linewidth=0, zorder=4)
                    bottom += share
        ax.set_title(CFG_LABEL[cfg], fontsize=7, color=INK, pad=4)
        ax.set_xticks(range(len(arms)))
        ax.set_xticklabels([ARM_LABEL[x] for x in arms], rotation=60, ha="right", fontsize=5.5)
        ax.set_ylim(0, 1)
        ax.set_yticks([0, 0.5, 1])
        ax.set_yticklabels(["0", ".5", "1"], fontsize=6)
        ax.tick_params(length=0)
        ax.grid(axis="y", color=GRID, lw=0.6)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    handles = [Patch(facecolor=RAMP[o], label=OPTION_LABELS[o]) for o in (1, 2, 3, 4)]
    fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=6.5, bbox_to_anchor=(0.5, -0.02))
    fig.text(0.005, 0.55, "share of valid draws", rotation=90, va="center", fontsize=6.5, color=INK2)
    fig.tight_layout(rect=(0.02, 0.06, 1, 1))
    save(fig, out, "outcome_distribution_by_model_and_arm")

    # B. Ground distribution: stacked bars per arm, one panel per model
    fig, axes = plt.subplots(1, len(configs), figsize=(1.7 * len(configs) + 1, 2.6), sharey=True)
    axes = list(axes) if len(configs) > 1 else [axes]
    for ax, cfg in zip(axes, configs):
        for j, arm in enumerate(arms):
            bs = [B[(cfg, c, arm)] for c in cases]
            n = sum(int(b["valid draws used"]) for b in bs)
            bottom = 0.0
            for g in (1, 2, 3, 4, 5):
                share = sum(int(b[f"ground {g}"]) for b in bs) / n
                if share > 0:
                    ax.bar(j, share, bottom=bottom, width=0.62, color=GROUND_RAMP[g], linewidth=0, zorder=3)
                    ax.bar(j, min(0.006, share), bottom=bottom + share - min(0.006, share), width=0.62, color=SURFACE, linewidth=0, zorder=4)
                    bottom += share
        ax.set_title(CFG_LABEL[cfg], fontsize=7, color=INK, pad=4)
        ax.set_xticks(range(len(arms)))
        ax.set_xticklabels([ARM_LABEL[x] for x in arms], rotation=60, ha="right", fontsize=5.5)
        ax.set_ylim(0, 1)
        ax.set_yticks([0, 0.5, 1])
        ax.set_yticklabels(["0", ".5", "1"], fontsize=6)
        ax.tick_params(length=0)
        ax.grid(axis="y", color=GRID, lw=0.6)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    handles = [Patch(facecolor=GROUND_RAMP[g], label=f"{g} {GROUND_LABELS[g]}") for g in (1, 2, 3, 4, 5)]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=6, bbox_to_anchor=(0.5, -0.05))
    fig.text(0.005, 0.55, "share of valid draws", rotation=90, va="center", fontsize=6.5, color=INK2)
    fig.tight_layout(rect=(0.02, 0.1, 1, 1))
    save(fig, out, "ground_distribution_by_model_and_arm")

    # C. Inter-model agreement heatmap per arm (sequential blue), models as rows and columns
    fig, axes = plt.subplots(1, len(arms), figsize=(1.6 * len(arms) + 0.6, 1.9), sharey=True)
    axes = list(axes) if len(arms) > 1 else [axes]
    short = {"terra": "Terra", "terra-off": "Terra off", "sonnet": "Sonnet", "gemini": "Gemini"}
    steps = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
    for ax, arm in zip(axes, arms):
        for i, a1 in enumerate(configs):
            for j, a2 in enumerate(configs):
                agree = sum(B[(a1, c, arm)]["modal"] == B[(a2, c, arm)]["modal"] for c in cases) / len(cases)
                ax.add_patch(plt.Rectangle((j + 0.04, i + 0.04), 0.92, 0.92, color=steps[min(6, int(agree * 6.999))], lw=0))
                ax.text(j + 0.5, i + 0.5, f"{agree:.1f}", ha="center", va="center", fontsize=5.5,
                        color="white" if agree >= 0.6 else INK)
        ax.set_xlim(0, len(configs))
        ax.set_ylim(len(configs), 0)
        ax.set_xticks([i + 0.5 for i in range(len(configs))])
        ax.set_xticklabels([short[c] for c in configs], rotation=60, ha="right", fontsize=5.5)
        ax.set_yticks([i + 0.5 for i in range(len(configs))])
        ax.set_yticklabels([short[c] for c in configs], fontsize=5.5)
        ax.set_title(ARM_LABEL[arm], fontsize=6.5, color=INK, pad=3)
        ax.tick_params(length=0)
        for s in ax.spines.values():
            s.set_visible(False)
    fig.suptitle("share of cases on which two models give the same modal outcome", fontsize=6.5, color=INK2, y=1.02)
    fig.tight_layout()
    save(fig, out, "inter_model_agreement_by_arm")

    # D. Per-case grant share across arms and models: one panel per case (small multiples)
    ncol = 5
    nrow = -(-len(cases) // ncol)
    fig, axes = plt.subplots(nrow, ncol, figsize=(1.35 * ncol + 0.6, 1.5 * nrow + 0.6), sharey=True)
    for ax, c in zip(axes.flat, cases):
        for i, cfg in enumerate(configs):
            ys = [float(B[(cfg, c, arm)]["grant share"]) for arm in arms]
            ax.plot(range(len(arms)), ys, color=AXIS, lw=0.8, zorder=2)
            ax.scatter(range(len(arms)), ys, s=14, color=["#2a78d6", "#eb6834", "#1baf7a", "#eda100"][i],
                       edgecolor=SURFACE, linewidth=0.8, zorder=3, label=CFG_LABEL[cfg])
        ax.set_title(f"{c}  (court: {OPTION_LABELS[int(court[c])]})", fontsize=5.5, color=INK, pad=2)
        ax.set_ylim(-0.05, 1.05)
        ax.set_yticks([0, 0.5, 1])
        ax.set_yticklabels(["0", ".5", "1"], fontsize=5)
        ax.set_xticks(range(len(arms)))
        ax.set_xticklabels([{"gr": "GR", "bt-en": "BTen", "en": "EN", "bt-de": "BTde", "de-lit": "DElit", "de-eng": "DEeng"}[x] for x in arms],
                           fontsize=4.5, rotation=90)
        ax.tick_params(length=0)
        ax.grid(axis="y", color=GRID, lw=0.5)
        ax.set_axisbelow(True)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    for ax in list(axes.flat)[len(cases):]:
        ax.set_visible(False)
    handles, labels = axes.flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, frameon=False, fontsize=6, bbox_to_anchor=(0.5, -0.02))
    fig.text(0.005, 0.55, "share of draws granting relief", rotation=90, va="center", fontsize=6, color=INK2)
    fig.tight_layout(rect=(0.02, 0.06, 1, 1))
    save(fig, out, "grant_share_per_case_small_multiples")

    md = [f"# Results package: {run}", "", "Tables (one tab each in `results_package.xlsx`, also as CSV):", ""]
    md += [f"- {s['name']}: {len(s['rows'])} rows" for s in sheets]
    md += ["", "Figures (PDF and PNG): outcome_distribution_by_model_and_arm, ground_distribution_by_model_and_arm, "
           "inter_model_agreement_by_arm, grant_share_per_case_small_multiples.", "",
           f"Regenerate with `python scripts/results_package.py --run {run}` after `python scripts/analyse.py --run {run} --court <coding sheet>`."]
    (out / "README.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"{run}: {len(sheets)} tables, 4 figures -> {out}")


if __name__ == "__main__":
    main()
