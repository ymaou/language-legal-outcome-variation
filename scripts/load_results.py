# -*- coding: utf-8 -*-
"""Read a run into blocks. For each (configuration, case, arm): every draw in order, and the draws used in
analysis, which are the first k valid replies in draw order. Reads raw/<run>/manifest.json and raw.jsonl."""
import json

from config import RAW
from parse import reasoning_text


def load_run(run):
    run_dir = RAW / run
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    with open(run_dir / "raw.jsonl", encoding="utf-8") as f:
        records = [json.loads(line) for line in f if line.strip()]
    blocks = {(b["config"], b["case"], b["arm"]): {"k": b["k"], "order": b["order"], "draws": [], "valid": []}
              for b in manifest["blocks"]}
    for r in records:
        if r.get("kind") != "draw":
            continue
        r["reasoning_text"] = reasoning_text(r.get("text", ""), r["prompt_lang"])
        blocks[(r["config"], r["case"], r["arm"])]["draws"].append(r)
    for b in blocks.values():
        b["draws"].sort(key=lambda r: (r["draw_index"], r.get("attempt", 1)))
        b["valid"] = [r for r in b["draws"] if r["parse"]["status"] == "ok"][: b["k"]]
    return manifest, blocks, records
