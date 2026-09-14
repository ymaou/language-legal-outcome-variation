# -*- coding: utf-8 -*-
"""The paper's single figure: the modal outcome of every case, in every arm, for every model, under the decide
framing (main-1, six arms) and the predict framing (predict-1, Greek and English), with the court's order.
One panel per model, 2 x 2, at a text width of 12.2 cm. Writes results/main-1/paper/Figure1.pdf/.png.

    python scripts/paper_figure_single.py
"""
import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Patch

from config import RESULTS

INK, INK2, MUTED, AXIS = "#0b0b0b", "#52514e", "#898781", "#c3c2b7"
FILL = {1: "#104281", 2: "#2a78d6", 3: "#86b6ef", 4: "#e1e0d9", "none": "#ffffff"}   # validated ordinal ramp
NAME = {1: "granted in full", 2: "granted in part", 3: "dismissed", 4: "conditional order", "none": "no clear answer"}
MODELS = [("terra", "GPT-5.6 Terra"), ("terra-off", "GPT-5.6 Terra, reasoning off"),
          ("sonnet", "Claude Sonnet 5"), ("gemini", "Gemini 3.6 Flash")]
DECIDE = [("gr", "GR"), ("bt-en", "BT-en"), ("en", "EN"), ("bt-de", "BT-de"), ("de-lit", "DE-lit"), ("de-eng", "DE-eng")]
PREDICT = [("gr", "GR"), ("en", "EN")]
GAP = 0.55
CM = 1 / 2.54

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 6.5, "text.color": INK,
                     "figure.facecolor": "white", "savefig.facecolor": "white"})


def blocks(run):
    with open(RESULTS / run / "csv" / "blocks.csv", encoding="utf-8-sig") as f:
        return {(b["configuration"], b["case"], b["arm"]): b["modal"] for b in csv.DictReader(f)}


def value(v):
    return int(v) if str(v).isdigit() else "none"


def main():
    decide, predict = blocks("main-1"), blocks("predict-1")
    with open(RESULTS / "main-1" / "csv" / "sensitivity_by_case.csv", encoding="utf-8-sig") as f:
        court = {r["case"]: int(r["court option"]) for r in csv.DictReader(f)}
    cases = sorted(court)
    columns = [(x, "decide", arm) for x, (arm, _) in enumerate(DECIDE)]
    columns += [(len(DECIDE) + GAP + i, "predict", arm) for i, (arm, _) in enumerate(PREDICT)]
    court_x = len(DECIDE) + GAP + len(PREDICT) + GAP
    labels = [lab for _, lab in DECIDE] + [lab for _, lab in PREDICT] + ["court"]
    xs = [x for x, _, _ in columns] + [court_x]

    fig, axes = plt.subplots(2, 2, figsize=(12.2 * CM, 10.6 * CM))
    for n, (ax, (cfg, title)) in enumerate(zip(axes.flat, MODELS)):
        for i, case in enumerate(cases):
            cells = [(x, value((decide if run == "decide" else predict)[(cfg, case, arm)])) for x, run, arm in columns]
            cells.append((court_x, court[case]))
            for x, v in cells:
                ax.add_patch(FancyBboxPatch((x + 0.07, i + 0.07), 0.86, 0.86, boxstyle="round,pad=0,rounding_size=0.1",
                                            facecolor=FILL[v], edgecolor=AXIS if v == "none" else "none",
                                            linewidth=0.5, hatch="////" if v == "none" else None))
        ax.set_xlim(-0.05, court_x + 1.05)
        ax.set_ylim(len(cases) + 0.05, -1.05)
        ax.set_title(title, fontsize=7, color=INK, pad=2)
        ax.text(len(DECIDE) / 2, -0.45, "decide", ha="center", va="center", fontsize=6, color=INK2)
        ax.text(len(DECIDE) + GAP + len(PREDICT) / 2, -0.45, "predict", ha="center", va="center", fontsize=6, color=INK2)
        for x0 in (len(DECIDE) + GAP / 2, len(DECIDE) + GAP + len(PREDICT) + GAP / 2):
            ax.plot([x0, x0], [0, len(cases)], color=AXIS, lw=0.5)
        ax.set_xticks([x + 0.5 for x in xs])
        ax.set_xticklabels(labels, rotation=90, fontsize=6, color=MUTED)
        ax.set_yticks([i + 0.5 for i in range(len(cases))])
        ax.set_yticklabels(cases if n % 2 == 0 else [], fontsize=6, color=MUTED)
        ax.tick_params(length=0, pad=1.5)
        for spine in ax.spines.values():
            spine.set_visible(False)
    handles = [Patch(facecolor=FILL[k], label=NAME[k]) for k in (1, 2, 3)]
    fig.legend(handles=handles, loc="lower center", ncol=3, frameon=False, fontsize=6.5, bbox_to_anchor=(0.5, 0.0),
               handlelength=1.4, columnspacing=1.6)
    fig.tight_layout(rect=(0, 0.045, 1, 1), h_pad=0.5, w_pad=1.6)
    out = RESULTS / "main-1" / "paper"
    for ext in ("pdf", "png"):
        fig.savefig(out / f"Figure1.{ext}", dpi=600 if ext == "png" else None)
    print("written:", out / "Figure1.pdf", "and .png, 12.2 x 10.6 cm")


if __name__ == "__main__":
    main()
