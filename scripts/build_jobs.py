# -*- coding: utf-8 -*-
"""Build a run: the blocks to be drawn, in a random order under a recorded seed, and the run manifest
(study design v8, sections 10.9 and 10.10). Writes raw/<run>/manifest.json. Never overwrites a run.

A block is one case, in one arm, on one model configuration. Its draws are sent together when it runs.

    python scripts/build_jobs.py --run pilot-1 --mode pilot
    python scripts/build_jobs.py --run main-1 --mode main        (or --mode reduced: 20 draws per arm)
"""
import argparse
import hashlib
import json
import platform
import random
import secrets
import subprocess
import sys
from datetime import datetime, timezone
from importlib import metadata

import prompts
from config import (ARMS, BUDGET_EUR, CASES, CEILING_EUR, CONFIGS, DRAWS, FROZEN, GREEK_ARM, GREEK_FACTOR,
                    MAX_OUTPUT_TOKENS, PILOT_CAP_EUR, PRICES, PROMPT_SETS, RAW, REPLACEMENT_SHARE, ROOT)
from integrity import verify_frozen


def _git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True, help="name of the run folder under raw/")
    ap.add_argument("--mode", required=True, choices=sorted(DRAWS))
    ap.add_argument("--configs", default=",".join(CONFIGS), help="comma-separated; default all")
    ap.add_argument("--seed", type=int, help="order seed; drawn at random and recorded if omitted")
    ap.add_argument("--prompts", default="decide", choices=sorted(PROMPT_SETS), help="prompt set; default the frozen main-run prompts")
    ap.add_argument("--arms", default=",".join(ARMS), help="comma-separated arms; default all six")
    ap.add_argument("--draws", type=int, help="draws per arm, overriding the mode's default (Greek gets twice this)")
    a = ap.parse_args()

    n_frozen = verify_frozen()
    run_dir = RAW / a.run
    if run_dir.exists():
        sys.exit(f"{run_dir} already exists; a run is never overwritten")
    configs = a.configs.split(",")
    unknown = [c for c in configs if c not in CONFIGS]
    if unknown:
        sys.exit(f"unknown configuration(s): {unknown}")

    if a.mode == "pilot":
        lengths = {c: len(prompts.file_a(GREEK_ARM, c)) for c in CASES}
        cases = [min(lengths, key=lengths.get), max(lengths, key=lengths.get)]
    else:
        cases = list(CASES)
    k = a.draws or DRAWS[a.mode]
    arms = a.arms.split(",")
    unknown_arms = [x for x in arms if x not in ARMS]
    if unknown_arms:
        sys.exit(f"unknown arm(s): {unknown_arms}")
    seed = a.seed if a.seed is not None else secrets.randbits(32)

    blocks = []
    for cfg in configs:
        for case in cases:
            for arm in arms:
                system, user = prompts.build(arm, case, a.prompts)
                blocks.append({
                    "block": f"{cfg}|{case}|{arm}", "config": cfg, "case": case, "arm": arm,
                    "k": k * (GREEK_FACTOR[a.mode] if arm == GREEK_ARM else 1),
                    "prompt_chars": len(system) + len(user),
                    "prompt_sha256": hashlib.sha256(f"{system}\n\x00\n{user}".encode("utf-8")).hexdigest(),
                })
    random.Random(seed).shuffle(blocks)
    for i, b in enumerate(blocks):
        b["order"] = i

    versions = {}
    for package in ("openai", "anthropic", "google-genai"):
        try:
            versions[package] = metadata.version(package)
        except metadata.PackageNotFoundError:
            versions[package] = None
    manifest = {
        "run": a.run,
        "mode": a.mode,
        "prompt_set": a.prompts,
        "arms": arms,
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "order_seed": seed,
        "cases": cases,
        "configs": {c: CONFIGS[c] for c in configs},
        "draws_per_arm": k,
        "greek_draws": k * GREEK_FACTOR[a.mode],
        "replacement_share_of_k": REPLACEMENT_SHARE[a.mode],
        "max_output_tokens": MAX_OUTPUT_TOKENS,
        "not_sent": ["temperature", "top_p", "seed"],
        "prices_usd_per_million_tokens": PRICES,
        "budget_eur": BUDGET_EUR, "ceiling_eur": CEILING_EUR, "pilot_cap_eur": PILOT_CAP_EUR,
        "frozen_files_verified": n_frozen,
        "frozen_list_sha256": hashlib.sha256(FROZEN.read_bytes()).hexdigest(),
        "git_commit": _git("rev-parse", "HEAD"),
        "git_uncommitted_changes": bool(_git("status", "--porcelain")),
        "python": platform.python_version(),
        "sdk_versions": versions,
        "blocks": blocks,
    }
    run_dir.mkdir(parents=True)
    (run_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    planned = sum(b["k"] for b in blocks)
    print(f"run {a.run}: mode {a.mode}, {len(cases)} cases, {len(configs)} configurations, "
          f"{len(blocks)} blocks, {planned} draws planned (before replacements); order seed {seed}")
    print(f"frozen files verified: {n_frozen}; manifest at {run_dir / 'manifest.json'}")


if __name__ == "__main__":
    main()
