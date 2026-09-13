# -*- coding: utf-8 -*-
"""Run a built run (study design v8, sections 10.3 and 10.9): every block is drawn to k valid replies, the
three providers in parallel, blocks started in the recorded random order. Within a block one call is sent
first, so the provider can cache the prompt, and the rest are then sent together.

Appends one JSON line per call to raw/<run>/raw.jsonl and never edits it. Resumable: running it again
continues where it stopped. Stops launching new blocks at the spending cap, and stops everything at once if
a provider rejects a request as malformed or unauthorised. The console shows progress, statuses and cost,
never a disposal or a ground.

    python scripts/run.py --run pilot-1
    python scripts/run.py --run test-1 --dry-run      no API call; fabricated replies, for testing
"""
import argparse
import asyncio
import hashlib
import json
import os
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone

import prompts
import providers
from config import (ARMS, CEILING_EUR, CONCURRENCY, PILOT_CAP_EUR, RAW, ROOT, TRANSPORT_ATTEMPTS,
                    max_replacements)
from integrity import verify_frozen
from parse import parse_reply

KEY_ENV = {"openai": "OPENAI_API_KEY", "anthropic": "ANTHROPIC_API_KEY", "google": "GEMINI_API_KEY"}
PROVIDER_CLASS = {"openai": providers.OpenAIProvider, "anthropic": providers.AnthropicProvider,
                  "google": providers.GoogleProvider}
BLOCK_LANES = {"openai": 3, "anthropic": 3, "google": 3}  # blocks in progress at once, per provider
FATAL_ERRORS = {"BadRequestError", "AuthenticationError", "PermissionDeniedError", "NotFoundError",
                "UnprocessableEntityError"}


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


OUT_OF_CREDIT = ("insufficient_quota", "credit balance", "billing", "exceeded your current quota",
                 "purchase credits", "payment", "resource_exhausted", "quota exceeded")


def _is_fatal(exc):
    """A request the provider rejects outright: malformed, unauthorised, or unpaid. Never retried."""
    if type(exc).__name__ in FATAL_ERRORS:
        return True
    text = str(exc).lower()
    if any(marker in text for marker in OUT_OF_CREDIT):
        return True
    code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
    return type(exc).__name__ == "ClientError" and code in (400, 401, 403, 404)


class AppendLog:
    def __init__(self, path):
        self.path = path
        self.lock = asyncio.Lock()

    async def write(self, record):
        async with self.lock:
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                f.flush()
                os.fsync(f.fileno())


def _read_log(path):
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


async def run(a):
    run_dir = RAW / a.run
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        sys.exit(f"no manifest at {manifest_path}; build the run first")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    n_frozen = verify_frozen()

    log_path = run_dir / "raw.jsonl"
    existing = _read_log(log_path)
    if any(r.get("dry_run") != a.dry_run for r in existing):
        sys.exit("this run already holds calls made with a different --dry-run setting; use a new run")

    needed = sorted({manifest["configs"][b["config"]]["provider"] for b in manifest["blocks"]})
    if a.dry_run:
        clients = {p: providers.DryRunProvider(seed=manifest["order_seed"] + i) for i, p in enumerate(needed)}
    else:
        try:
            from dotenv import load_dotenv
            load_dotenv(ROOT / ".env")
        except ImportError:
            pass
        missing = [KEY_ENV[p] for p in needed if not os.environ.get(KEY_ENV[p])]
        if missing:
            sys.exit(f"missing API key(s) in .env: {', '.join(missing)}")
        clients = {p: PROVIDER_CLASS[p]() for p in needed}

    mode = manifest["mode"]
    cap = a.cap if a.cap is not None else (PILOT_CAP_EUR if mode == "pilot" else CEILING_EUR)
    concurrency = {p: (a.concurrency or CONCURRENCY[p]) for p in needed}
    lanes = {p: (a.lanes or BLOCK_LANES[p]) for p in needed}

    state = {"spent": sum(r.get("cost_usd", 0.0) for r in existing), "stopped_at_cap": False, "fatal": None,
             "reserved": 0.0, "unit_cost": {}}
    for r in existing:  # most expensive call seen per configuration, for reserving the cost of a batch
        if r.get("kind") == "draw":
            state["unit_cost"][r["config"]] = max(state["unit_cost"].get(r["config"], 0.0), r.get("cost_usd", 0.0))
    statuses = Counter(r["parse"]["status"] for r in existing if r.get("kind") == "draw")
    progress = defaultdict(lambda: {"valid": 0, "next_index": 0, "unit_cost": 0.0})
    for r in existing:
        if "draw_index" not in r:
            continue
        p = progress[r["block"]]
        p["next_index"] = max(p["next_index"], r["draw_index"] + 1)
        if r.get("kind") == "draw" and r["parse"]["status"] == "ok":
            p["valid"] += 1

    semaphores = {p: asyncio.Semaphore(concurrency[p]) for p in needed}
    log = AppendLog(log_path)
    total_blocks = len(manifest["blocks"])
    await log.write({"kind": "session", "run": a.run, "dry_run": a.dry_run, "started_utc": _now(), "cap": cap,
                     "concurrency": concurrency, "block_lanes": lanes, "frozen_files_verified": n_frozen,
                     "already_spent_usd": round(state["spent"], 6)})

    async def one_call(block, draw_index):
        cfg = manifest["configs"][block["config"]]
        provider = cfg["provider"]
        lang = ARMS[block["arm"]]
        system, user = prompts.build(block["arm"], block["case"], manifest.get("prompt_set", "decide"))
        if hashlib.sha256(f"{system}\n\x00\n{user}".encode("utf-8")).hexdigest() != block["prompt_sha256"]:
            state["fatal"] = f"prompt for {block['block']} differs from the manifest"
            return "fatal", 0.0
        base = {"run": a.run, "dry_run": a.dry_run, "block": block["block"], "order": block["order"],
                "config": block["config"], "provider": provider, "model_requested": cfg["model"],
                "reasoning": cfg["reasoning"], "case": block["case"], "arm": block["arm"], "prompt_lang": lang,
                "prompt_sha256": block["prompt_sha256"], "draw_index": draw_index,
                "is_replacement": draw_index >= block["k"]}
        for attempt in range(1, TRANSPORT_ATTEMPTS + 1):
            if state["fatal"]:
                return "fatal", 0.0
            async with semaphores[provider]:
                started, t0 = _now(), time.monotonic()
                try:
                    result, error, fatal = await clients[provider].call(cfg, system, user, lang), None, False
                except Exception as exc:
                    result, error, fatal = None, f"{type(exc).__name__}: {str(exc)[:800]}", _is_fatal(exc)
                latency = round(time.monotonic() - t0, 3)
            record = dict(base, attempt=attempt, started_utc=started, ended_utc=_now(), latency_s=latency)
            if result is None:
                record.update(kind="error", error=error, fatal=fatal, cost_usd=0.0)
                await log.write(record)
                if fatal:
                    state["fatal"] = f"{provider} rejected the request: {error}"
                    return "fatal", 0.0
                if attempt < TRANSPORT_ATTEMPTS:
                    await asyncio.sleep(min(90, 5 * 2 ** attempt))
                    continue
                return "error", 0.0
            cost = providers.cost_usd(cfg["model"], result["usage"])
            parsed = parse_reply(result["text"], lang, result["finish"])
            record.update(kind="draw", response_id=result["response_id"], model_returned=result["model_returned"],
                          finish=result["finish"], usage=result["usage"], detail=result["detail"],
                          cost_usd=round(cost, 6), text=result["text"], parse=parsed)
            state["spent"] += cost
            statuses[parsed["status"]] += 1
            await log.write(record)
            return parsed["status"], cost

    async def run_block(provider, block):
        p = progress[block["block"]]
        k = block["k"]
        while p["valid"] < k and not state["fatal"] and not state["stopped_at_cap"]:
            if p["next_index"] == 0:
                indices = [0]  # one call first, so the prompt is cached for the rest
            else:
                need = min(k - p["valid"], (k + max_replacements(mode, k)) - p["next_index"])
                if need <= 0:
                    print(f"  [{provider}] {block['block']}: replacement limit reached with {p['valid']}/{k} valid")
                    return
                indices = list(range(p["next_index"], p["next_index"] + need))
            # Reserve the batch's likely cost before sending it, so blocks running in parallel cannot
            # together carry the spend past the cap. The estimate is the dearest call seen so far.
            unit = p["unit_cost"] or state["unit_cost"].get(block["config"], 0.0) or 0.50
            estimate = unit * len(indices)
            if state["spent"] + state["reserved"] + estimate > cap:
                state["stopped_at_cap"] = True
                return
            state["reserved"] += estimate
            try:
                results = await asyncio.gather(*(one_call(block, i) for i in indices))
            finally:
                state["reserved"] -= estimate
            costs = [c for _, c in results if c]
            if costs:
                p["unit_cost"] = max([p["unit_cost"], *costs])
                state["unit_cost"][block["config"]] = max(state["unit_cost"].get(block["config"], 0.0), *costs)
            p["next_index"] += len(indices)
            p["valid"] += sum(1 for s, _ in results if s == "ok")
        if not state["fatal"]:
            print(f"  [{provider}] block {block['order'] + 1}/{total_blocks} {block['config']} {block['case']} "
                  f"{block['arm']}: {p['valid']}/{k} valid | spent ${state['spent']:.2f}", flush=True)

    async def worker(provider):
        queue = asyncio.Queue()
        for b in manifest["blocks"]:
            if manifest["configs"][b["config"]]["provider"] == provider and progress[b["block"]]["valid"] < b["k"]:
                queue.put_nowait(b)

        async def lane():
            while not queue.empty() and not state["fatal"] and not state["stopped_at_cap"]:
                await run_block(provider, queue.get_nowait())

        await asyncio.gather(*(lane() for _ in range(lanes[provider])))

    print(f"run {a.run} ({mode}{', DRY RUN' if a.dry_run else ''}): {total_blocks} blocks, providers "
          f"{', '.join(needed)}, cap {cap}; already spent ${state['spent']:.2f}", flush=True)
    t_start = time.monotonic()
    await asyncio.gather(*(worker(p) for p in needed))
    minutes = (time.monotonic() - t_start) / 60
    print(f"\nsession ended after {minutes:.1f} min; spent ${state['spent']:.2f}; reply statuses: {dict(statuses)}")
    incomplete = [b["block"] for b in manifest["blocks"] if progress[b["block"]]["valid"] < b["k"]]
    if state["fatal"]:
        print(f"STOPPED: {state['fatal']}")
        if any(m in state["fatal"].lower() for m in OUT_OF_CREDIT):
            print("This looks like an EMPTY BALANCE or a spending limit at the provider. Top up or raise the limit, "
                  "then run the same command again; the run resumes where it stopped.")
    if state["stopped_at_cap"]:
        print(f"STOPPED AT THE SPENDING CAP ({cap})")
    print(f"blocks complete: {total_blocks - len(incomplete)}/{total_blocks}")
    import costs
    costs.record(a.run, mode, a.dry_run)
    if state["fatal"]:
        sys.exit(2)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--dry-run", action="store_true", help="no API call; fabricated replies")
    ap.add_argument("--cap", type=float, help="spending cap for this session; default from config")
    ap.add_argument("--concurrency", type=int, help="calls at once per provider; default from config")
    ap.add_argument("--lanes", type=int, help="blocks in progress at once per provider; default 3")
    asyncio.run(run(ap.parse_args()))


if __name__ == "__main__":
    main()
