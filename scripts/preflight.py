# -*- coding: utf-8 -*-
"""One tiny call per model configuration, before the pilot: confirms the key, the model identifier and the
reasoning setting are accepted, and shows what the provider returns. Costs a few cents. Logs nothing.

    python scripts/preflight.py
"""
import asyncio
import os

import providers
from config import CONFIGS, ROOT
from run import KEY_ENV, PROVIDER_CLASS

SYSTEM = "Reply with the single word OK and nothing else."
USER = "Ready?"


async def main():
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
    missing = [KEY_ENV[c["provider"]] for c in CONFIGS.values() if not os.environ.get(KEY_ENV[c["provider"]])]
    if missing:
        raise SystemExit(f"missing key(s): {sorted(set(missing))}")
    clients = {p: PROVIDER_CLASS[p]() for p in {c["provider"] for c in CONFIGS.values()}}
    total = 0.0
    for name, cfg in CONFIGS.items():
        try:
            r = await clients[cfg["provider"]].call(cfg, SYSTEM, USER, "en")
        except Exception as exc:
            print(f"{name:10} FAILED  {type(exc).__name__}: {str(exc)[:300]}")
            continue
        cost = providers.cost_usd(cfg["model"], r["usage"])
        total += cost
        print(f"{name:10} ok  model returned: {r['model_returned']} | finish: {r['finish']} | reply: {r['text'].strip()[:40]!r} | "
              f"tokens in/out/reasoning: {r['usage']['input_total']}/{r['usage']['output']}/{r['usage'].get('reasoning')} | ${cost:.4f}")
    print(f"preflight cost: ${total:.4f}")


if __name__ == "__main__":
    asyncio.run(main())
