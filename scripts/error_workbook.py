# -*- coding: utf-8 -*-
"""Error-coding workbook (study design v8, section 12). One row per robust flip: a case and model whose modal
disposal in a non-Greek arm differs from the modal disposal of all the Greek draws. Each row carries the Greek
and the arm's File A side by side, three typical reasons from each side, and empty coding columns with
drop-down lists: the flip code (T, G, S, D, N, O), the threshold codes T1-T4 for each side, and the ground check.

It never overwrites a workbook that already exists, so coding in progress cannot be lost.

    python scripts/error_workbook.py --run main-1
"""
import argparse
import sys

import measures as M
import prompts
from config import CONFIGS, GREEK_ARM, GROUND_LABELS, NOISE_SHARE, OPTION_LABELS, REASONS_PER_SIDE, RESULTS
from load_results import load_run
from tables import write_workbook

ARM_KIND = {"en": "language: English", "de-lit": "language: German, plain terms",
            "de-eng": "language: German, English Part 24 terms", "bt-en": "back-translation via English",
            "bt-de": "back-translation via German"}
CODES = "T,G,S,D,N,O"
YES_NO = "yes,no,n/a"
GROUND_CHECK = "matches,does not match,unclear"


def label(value):
    return "no clear answer" if value == M.NONE else f"{value} {OPTION_LABELS[value]}"


def typical_reasons(block, modal_value, n):
    chosen = [r for r in block["valid"] if modal_value == M.NONE or r["parse"]["outcome"] == modal_value]
    return chosen[:n]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    a = ap.parse_args()
    manifest, blocks, records = load_run(a.run)
    if manifest["mode"] == "pilot":
        sys.exit("a pilot run is not analysed (v8 section 10.10)")
    out_dir = RESULTS / a.run
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "error_coding.xlsx"
    if path.exists():
        sys.exit(f"{path} already exists and may hold your coding; it is not overwritten")
    dry = any(r.get("dry_run") for r in records if r.get("kind") == "draw")

    headers = ["flip", "configuration", "model", "reasoning setting", "case", "arm", "kind of arm",
               "Greek modal (all Greek draws)", "Greek modal share", "arm modal", "arm modal share", "noise flag"]
    headers += ["Greek File A", "arm File A"]
    for side in ("Greek", "arm"):
        for i in range(1, REASONS_PER_SIDE + 1):
            headers += [f"{side} reason {i}", f"{side} reason {i}: model's ground"]
    coding = ["PRIMARY CODE", "SECONDARY CODE"] + [f"Greek T{i}" for i in range(1, 5)] + \
        [f"arm T{i}" for i in range(1, 5)] + ["Greek ground check", "arm ground check", "note"]
    headers += coding

    rows, n = [], 0
    for cfg in manifest["configs"]:
        for case in manifest["cases"]:
            greek_block = blocks[(cfg, case, GREEK_ARM)]
            greek = [r["parse"]["outcome"] for r in greek_block["valid"]]
            greek_modal, greek_share = M.modal(greek), M.modal_share(greek)
            for arm, kind in ARM_KIND.items():
                arm_block = blocks[(cfg, case, arm)]
                values = [r["parse"]["outcome"] for r in arm_block["valid"]]
                arm_modal, arm_share = M.modal(values), M.modal_share(values)
                if arm_modal == greek_modal:
                    continue
                n += 1
                noise = f"modal share below {NOISE_SHARE:.2f} on at least one side: consider N" \
                    if min(greek_share, arm_share) < NOISE_SHARE else ""
                row = [n, cfg, CONFIGS[cfg]["model"], CONFIGS[cfg]["reasoning"], case, arm, kind,
                       label(greek_modal), greek_share, label(arm_modal), arm_share, noise,
                       prompts.file_a(GREEK_ARM, case), prompts.file_a(arm, case)]
                for block, modal_value in ((greek_block, greek_modal), (arm_block, arm_modal)):
                    chosen = typical_reasons(block, modal_value, REASONS_PER_SIDE)
                    for i in range(REASONS_PER_SIDE):
                        if i < len(chosen):
                            g = chosen[i]["parse"]["ground"]
                            row += [chosen[i]["reasoning_text"], f"{g} {GROUND_LABELS[g]}"]
                        else:
                            row += ["", ""]
                rows.append(row + [""] * len(coding))

    wide = {"Greek File A": 70, "arm File A": 70, "note": 40}
    for side in ("Greek", "arm"):
        for i in range(1, REASONS_PER_SIDE + 1):
            wide[f"{side} reason {i}"] = 55
    validations = {"PRIMARY CODE": CODES, "SECONDARY CODE": CODES,
                   "Greek ground check": GROUND_CHECK, "arm ground check": GROUND_CHECK}
    for side in ("Greek", "arm"):
        for i in range(1, 5):
            validations[f"{side} T{i}"] = YES_NO
    codebook = [
        ("T", "flip code", "Translation: the arm's File A changes or drops a legally material fact."),
        ("G", "flip code", "Ground shift: the same facts relied on, a different ground chosen."),
        ("S", "flip code", "Standard: the same ground, but the real-prospect threshold applied differently."),
        ("D", "flip code", "Doctrinal import: the arm's reasons invoke English authorities or concepts absent from the Greek reasons."),
        ("N", "flip code", f"Noise: modal share below {NOISE_SHARE:.2f} in either arm."),
        ("O", "flip code", "Other: describe it in the note."),
        ("T1", "threshold code", "Standard applied: the reasons apply a real-prospect standard rather than deciding who is more likely right on the merits (yes = threshold standard applied)."),
        ("T2", "threshold code", "Limb (b) addressed: any 'other compelling reason for a trial' reasoning is present (yes = addressed). The headline code."),
        ("T3", "threshold code", "Right party assessed: the reasons evaluate the respondent's prospects specifically (yes = respondent's prospects assessed)."),
        ("T4", "threshold code", "Evidential conflict: a conflict of affidavit evidence is treated as a reason not to resolve the matter (yes). Only where a conflict exists; otherwise n/a."),
        ("ground check", "per side", "Does the model's chosen ground match what its reasons actually turn on?"),
        ("one primary code", "rule", "One primary flip code per row, at most one secondary (v8 section 12)."),
    ]
    options = [(str(k), v) for k, v in OPTION_LABELS.items()] + [(f"ground {k}", v) for k, v in GROUND_LABELS.items()]
    notes = [f"Error coding for run {a.run}{' - FABRICATED DRY-RUN DATA, NOT RESULTS' if dry else ''}. "
             f"{len(rows)} flips. Code in the capitalised columns at the right; the drop-down lists hold the allowed values.",
             "The Greek side is always the modal disposal of all the Greek draws; reasons shown are the first "
             f"{REASONS_PER_SIDE} valid replies that chose that side's modal disposal."]
    write_workbook(path, [
        {"name": "Flips", "headers": headers, "rows": rows, "notes": notes, "widths": wide,
         "wrap": ["Greek File A", "arm File A"] + [h for h in headers if " reason " in h and "ground" not in h],
         "validations": validations},
        {"name": "Codebook", "headers": ["code", "type", "meaning"], "rows": codebook, "widths": {"meaning": 120}},
        {"name": "Options and grounds", "headers": ["value", "meaning"], "rows": options, "widths": {"meaning": 50}},
    ])
    print(f"{len(rows)} flips written to {path}")


if __name__ == "__main__":
    main()
