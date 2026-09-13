# -*- coding: utf-8 -*-
"""Paper figures and tables for a main run, from results/<run>/csv/. Writes results/<run>/paper/.
Colours: the validated ordinal blue ramp for amount of relief; blue / orange / aqua for the Greek, English and
back-translated arms; everything else in de-emphasis gray. One hue per single-series panel.

    python scripts/paper_figures.py --run main-1
"""
import argparse
import csv
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Patch

from config import RESULTS
from tables import write_workbook

INK, INK2, MUTED, GRID, AXIS, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
RELIEF = {3: ("#86b6ef", "dismissed"), 2: ("#2a78d6", "granted in part"), 1: ("#104281", "granted in full"),
          4: ("#f0efec", "conditional order"), "none": ("#ffffff", "no clear answer")}
ARM_COLOR = {"gr": "#2a78d6", "en": "#eb6834", "bt-en": "#1baf7a"}
ARM_LABEL = {"gr": "Greek", "bt-en": "BT via English", "en": "English", "bt-de": "BT via German",
             "de-lit": "German (plain terms)", "de-eng": "German (English terms)"}
ARMS = ["gr", "bt-en", "en", "bt-de", "de-lit", "de-eng"]
CFG_LABEL = {"terra": "GPT-5.6 Terra", "terra-off": "GPT-5.6 Terra, reasoning off", "sonnet": "Claude Sonnet 5",
             "gemini": "Gemini 3.6 Flash"}
LANG_LABEL = {"el": "Greek", "en": "English", "de-lit": "German (plain)", "de-eng": "German (Eng. terms)"}
OFFSET = {"gr": -0.24, "bt-en": -0.10, "en": 0.04, "bt-de": 0.16, "de-lit": 0.24, "de-eng": 0.32}

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.edgecolor": AXIS, "axes.linewidth": 0.6,
                     "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK, "axes.labelcolor": INK2,
                     "figure.facecolor": "white", "axes.facecolor": SURFACE, "savefig.facecolor": "white"})


def read(run, name):
    with open(RESULTS / run / "csv" / f"{name}.csv", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def block(blocks, cfg, case, arm):
    return next(b for b in blocks if b["configuration"] == cfg and b["case"] == case and b["arm"] == arm)


def save(fig, out, stem):
    for ext in ("png", "pdf"):
        fig.savefig(out / f"{stem}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)


def fig_grid(blocks, court, configs, cases, out):
    fig, axes = plt.subplots(1, len(configs), figsize=(6.6, 3.1), sharey=True)
    cols = ARMS + ["court"]
    for ax, cfg in zip(axes, configs):
        ax.set_title(CFG_LABEL[cfg], fontsize=7.5, color=INK, pad=6)
        for i, case in enumerate(cases):
            for j, col in enumerate(cols):
                if col == "court":
                    v = int(court[case])
                else:
                    m = block(blocks, cfg, case, col)["modal"]
                    v = int(m) if m.isdigit() else "none"
                x = j + (0.45 if col == "court" else 0)
                ax.add_patch(FancyBboxPatch((x + 0.08, i + 0.08), 0.84, 0.84,
                                            boxstyle="round,pad=0,rounding_size=0.12",
                                            linewidth=0.6 if v == "none" else 0, edgecolor=AXIS,
                                            facecolor=RELIEF[v][0], hatch="//" if v == "none" else None))
        ax.set_xlim(0, len(cols) + 0.45)
        ax.set_ylim(len(cases), 0)
        ax.set_xticks([j + (0.45 if c == "court" else 0) + 0.5 for j, c in enumerate(cols)])
        ax.set_xticklabels([ARM_LABEL.get(c, "Court") for c in cols], rotation=60, ha="right", fontsize=6.3)
        ax.set_yticks([i + 0.5 for i in range(len(cases))])
        ax.set_yticklabels(cases, fontsize=6.3)
        ax.tick_params(length=0)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.axvline(len(ARMS) + 0.22, color=AXIS, lw=0.6)
    handles = [Patch(facecolor=RELIEF[k][0], label=RELIEF[k][1]) for k in (1, 2, 3)]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=7, bbox_to_anchor=(0.5, -0.03))
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    save(fig, out, "F1_modal_disposal_grid")


def fig_grid_paper(blocks, court, configs, cases, out):
    """Figure 1 at the proceedings' text width (about 12.5 cm): the four panels in a 2 x 2 layout."""
    fig, axes = plt.subplots(2, 2, figsize=(4.9, 5.4), sharey=True)
    cols = ARMS + ["court"]
    short = {"gr": "GR", "bt-en": "BT-en", "en": "EN", "bt-de": "BT-de", "de-lit": "DE-lit", "de-eng": "DE-eng",
             "court": "court"}
    for ax, cfg in zip(axes.flat, configs):
        ax.set_title(CFG_LABEL[cfg], fontsize=7, color=INK, pad=4)
        for i, case in enumerate(cases):
            for j, col in enumerate(cols):
                if col == "court":
                    v = int(court[case])
                else:
                    m = block(blocks, cfg, case, col)["modal"]
                    v = int(m) if m.isdigit() else "none"
                x = j + (0.45 if col == "court" else 0)
                ax.add_patch(FancyBboxPatch((x + 0.08, i + 0.08), 0.84, 0.84,
                                            boxstyle="round,pad=0,rounding_size=0.12",
                                            linewidth=0.6 if v == "none" else 0, edgecolor=AXIS,
                                            facecolor=RELIEF[v][0], hatch="//" if v == "none" else None))
        ax.set_xlim(0, len(cols) + 0.45)
        ax.set_ylim(len(cases), 0)
        ax.set_xticks([j + (0.45 if c == "court" else 0) + 0.5 for j, c in enumerate(cols)])
        ax.set_xticklabels([short[c] for c in cols], rotation=90, fontsize=6)
        ax.set_yticks([i + 0.5 for i in range(len(cases))])
        ax.set_yticklabels(cases, fontsize=6)
        ax.tick_params(length=0)
        for s in ax.spines.values():
            s.set_visible(False)
        ax.axvline(len(ARMS) + 0.22, color=AXIS, lw=0.6)
    handles = [Patch(facecolor=RELIEF[k][0], label=RELIEF[k][1]) for k in (1, 2, 3)]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=6.5, bbox_to_anchor=(0.5, -0.01))
    fig.tight_layout(rect=(0, 0.04, 1, 1), h_pad=1.2)
    save(fig, out, "F1_modal_disposal_grid_paper")


def fig_grant_share(blocks, court, configs, cases, out):
    fig, axes = plt.subplots(len(configs), 1, figsize=(6.6, 5.8), sharex=True)
    for ax, cfg in zip(axes, configs):
        for i, case in enumerate(cases):
            if court[case] in ("1", "2"):
                ax.axvspan(i - 0.5, i + 0.5, color="#f0efec", lw=0)
        for arm in ARMS:
            ys = [float(block(blocks, cfg, case, arm)["grant share"]) for case in cases]
            xs = [i + OFFSET[arm] for i in range(len(cases))]
            if arm in ARM_COLOR:
                ax.scatter(xs, ys, s=34, color=ARM_COLOR[arm], edgecolor=SURFACE, linewidth=1.2, zorder=3,
                           label=ARM_LABEL[arm])
            else:
                ax.scatter(xs, ys, s=16, color=AXIS, edgecolor=SURFACE, linewidth=1, zorder=2,
                           label="German arms and BT via German" if arm == "bt-de" else None)
        ax.set_ylim(-0.04, 1.04)
        ax.set_yticks([0, 0.5, 1])
        ax.set_yticklabels(["0", ".5", "1"], fontsize=6.5)
        ax.grid(axis="y", color=GRID, lw=0.6)
        ax.set_axisbelow(True)
        ax.text(0.005, 0.93, CFG_LABEL[cfg], transform=ax.transAxes, fontsize=7.5, color=INK, va="top")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.tick_params(length=0)
    axes[-1].set_xticks(range(len(cases)))
    axes[-1].set_xticklabels(cases, fontsize=6.5)
    fig.text(0.005, 0.5, "share of draws granting relief (options 1 or 2)", rotation=90, va="center",
             fontsize=7, color=INK2)
    handles, labels = axes[0].get_legend_handles_labels()
    handles.append(Patch(facecolor="#f0efec", label="court granted (in full or in part)"))
    labels.append("court granted (in full or in part)")
    fig.legend(handles, labels, loc="lower center", ncol=3, frameon=False, fontsize=6.5, bbox_to_anchor=(0.5, -0.005))
    fig.tight_layout(rect=(0.02, 0.05, 1, 1))
    save(fig, out, "F2_grant_share_by_case")


def fig_framing(out, decide_run="main-1", predict_run="predict-1"):
    """Figure 2: grant share per case under the decide and predict framings, Greek and English arms. Colour is
    the language (blue Greek, orange English); a filled marker is the decide framing, a hollow one predict."""
    D, P = read(decide_run, "blocks"), read(predict_run, "blocks")
    court = {r["case"]: r["court option"] for r in read(decide_run, "sensitivity_by_case")}
    configs = [c for c in CFG_LABEL if any(b["configuration"] == c for b in P)]
    cases = sorted({b["case"] for b in P})
    fig, axes = plt.subplots(2, 2, figsize=(4.9, 4.2), sharex=True, sharey=True)
    for ax, cfg in zip(axes.flat, configs):
        for i, case in enumerate(cases):
            if court[case] in ("1", "2"):
                ax.axvspan(i - 0.5, i + 0.5, color="#f0efec", lw=0)
        for arm, colour, dx in (("gr", "#2a78d6", -0.18), ("en", "#eb6834", 0.18)):
            for blocks, hollow, dd in ((D, False, -0.07), (P, True, 0.07)):
                ys = [float(block(blocks, cfg, case, arm)["grant share"]) for case in cases]
                xs = [i + dx + dd for i in range(len(cases))]
                ax.scatter(xs, ys, s=22, facecolor=SURFACE if hollow else colour, edgecolor=colour,
                           linewidth=1.1, zorder=3)
        ax.set_ylim(-0.05, 1.05)
        ax.set_yticks([0, 0.5, 1])
        ax.set_yticklabels(["0", ".5", "1"], fontsize=6)
        ax.grid(axis="y", color=GRID, lw=0.6)
        ax.set_axisbelow(True)
        ax.set_title(CFG_LABEL[cfg], fontsize=7, color=INK, pad=3)
        ax.set_xticks(range(len(cases)))
        ax.set_xticklabels(cases, fontsize=5.5, rotation=90)
        ax.tick_params(length=0)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    from matplotlib.lines import Line2D
    handles = [Line2D([], [], marker="o", ls="", ms=5, mfc="#2a78d6", mec="#2a78d6", label="Greek, decide"),
               Line2D([], [], marker="o", ls="", ms=5, mfc=SURFACE, mec="#2a78d6", label="Greek, predict"),
               Line2D([], [], marker="o", ls="", ms=5, mfc="#eb6834", mec="#eb6834", label="English, decide"),
               Line2D([], [], marker="o", ls="", ms=5, mfc=SURFACE, mec="#eb6834", label="English, predict"),
               Patch(facecolor="#f0efec", label="court granted")]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=6, bbox_to_anchor=(0.5, -0.02))
    fig.text(0.005, 0.55, "share of draws granting relief", rotation=90, va="center", fontsize=6.5, color=INK2)
    fig.tight_layout(rect=(0.02, 0.07, 1, 1))
    save(fig, out, "F2_framing_grant_share_paper")


def fig_tokens(tokens, out):
    panels = [("terra", "reasoning tokens"), ("sonnet", "output tokens, thinking included"),
              ("gemini", "reasoning tokens")]
    fig, axes = plt.subplots(1, 3, figsize=(6.6, 2.3))
    langs = ["el", "en", "de-lit", "de-eng"]
    for ax, (cfg, what) in zip(axes, panels):
        vals = [tokens[(cfg, lang)] for lang in langs]
        ax.bar(range(4), vals, width=0.55, color="#2a78d6", linewidth=0, zorder=3)
        for i, v in enumerate(vals):
            ax.text(i, v, f"{v:,.0f}", ha="center", va="bottom", fontsize=6.5, color=INK2)
        ax.set_xticks(range(4))
        ax.set_xticklabels([LANG_LABEL[lang] for lang in langs], fontsize=6, rotation=25, ha="right")
        ax.set_title(f"{CFG_LABEL[cfg]}\n{what}", fontsize=7, color=INK, pad=4)
        ax.set_ylim(0, max(vals) * 1.25)
        ax.grid(axis="y", color=GRID, lw=0.6)
        ax.set_axisbelow(True)
        ax.tick_params(length=0, labelsize=6)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
    fig.tight_layout()
    save(fig, out, "F3_reasoning_tokens_by_language")


def tables(run, blocks, out):
    sens = read(run, "sensitivity")
    rates = read(run, "rates")
    fails = read(run, "failures")
    t1 = []
    for r in sens:
        cfg = r["configuration"]
        greek = [b for b in blocks if b["configuration"] == cfg and b["arm"] == "gr"]
        n = sum(int(b["valid draws used"]) for b in greek)
        full = sum(int(b["option 1"]) for b in greek)
        part = sum(int(b["option 2"]) for b in greek)
        cond = sum(int(b["option 4"]) for b in greek)
        t1.append([CFG_LABEL[cfg], n, f"{full / n:.1%}", f"{part / n:.1%}", f"{(n - full - part - cond) / n:.1%}",
                   f"{float(r['accuracy (four options)']):.2f}", f"{float(r['majority-class baseline']):.2f}",
                   f"{float(r['MCC']):.2f}"])
    t1h = ["model", "Greek draws", "granted in full", "granted in part", "dismissed", "agreement with court",
           "baseline", "MCC"]
    prim = [r for r in rates if r["definition"].startswith("primary")]
    t2 = []
    for cfg in CFG_LABEL:
        row = {r["measure"]: r for r in prim if r["configuration"] == cfg}
        if not row:
            continue
        v = lambda m: f"{float(row[m]['value']):.2f}"
        ci = lambda m: f"{float(row[m]['value']):.2f} [{float(row[m]['95% CI low']):.2f}, {float(row[m]['95% CI high']):.2f}]"
        t2.append([CFG_LABEL[cfg], v("F"), v("W_en"), v("L_EN"), ci("delta_EN"), v("W_de"), v("L_DE"), ci("delta_DE")])
    t2h = ["model", "F (noise floor)", "W_en (rewording)", "L_EN (language)", "Δ_EN = L_EN − W_en [95% CI]",
           "W_de", "L_DE", "Δ_DE [95% CI]"]
    with open(out / "T3_considerations.csv", encoding="utf-8-sig") as f:
        t3 = list(csv.DictReader(f))
    cons = list(dict.fromkeys(r["consideration"] for r in t3))
    t3rows = []
    for c in cons:
        cells = []
        for cfg in CFG_LABEL:
            r = next(r for r in t3 if r["configuration"] == cfg and r["consideration"] == c)
            cells.append(f"{float(r['share of all replies']):.0%}")
        t3rows.append([c] + cells)
    t3h = ["consideration invoked in the reasoning (share of all valid replies)"] + [CFG_LABEL[c] for c in CFG_LABEL]
    t4 = [[CFG_LABEL[r["configuration"]], ARM_LABEL[r["arm"]], r["calls with a reply"], r["valid"],
           f"{float(r['failure rate']):.1%}"] for r in fails]
    t4h = ["model", "arm", "replies", "valid", "failure rate"]
    tabs = [("T1 sensitivity", t1h, t1), ("T2 rates", t2h, t2), ("T3 considerations", t3h, t3rows),
            ("T4 reliability", t4h, t4)]
    write_workbook(out / "paper_tables.xlsx", [{"name": n, "headers": h, "rows": r} for n, h, r in tabs])
    md = [f"# Paper tables: {run}", ""]
    for n, h, r in tabs:
        md += [f"## {n}", "", "| " + " | ".join(h) + " |", "|" + "---|" * len(h)]
        md += ["| " + " | ".join(str(x) for x in row) + " |" for row in r]
        md.append("")
    (out / "tables.md").write_text("\n".join(md), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    a = ap.parse_args()
    out = RESULTS / a.run / "paper"
    out.mkdir(parents=True, exist_ok=True)
    blocks = read(a.run, "blocks")
    court = {r["case"]: r["court option"] for r in read(a.run, "sensitivity_by_case")}
    configs = [c for c in CFG_LABEL if any(b["configuration"] == c for b in blocks)]
    cases = sorted({b["case"] for b in blocks})
    tok = defaultdict(list)
    for r in read(a.run, "draws"):
        if r["status"] != "ok":
            continue
        v = r["output tokens"] if r["configuration"] == "sonnet" else r["reasoning tokens"]
        tok[(r["configuration"], r["prompt language"])].append(float(v or 0))
    tokens = {k: sum(v) / len(v) for k, v in tok.items()}
    fig_grid(blocks, court, configs, cases, out)
    fig_grid_paper(blocks, court, configs, cases, out)
    fig_grant_share(blocks, court, configs, cases, out)
    fig_tokens(tokens, out)
    if (RESULTS / 'predict-1' / 'csv' / 'blocks.csv').exists():
        fig_framing(out)
    tables(a.run, blocks, out)
    print("written to", out)


if __name__ == "__main__":
    main()
