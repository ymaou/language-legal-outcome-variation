# -*- coding: utf-8 -*-
"""One call to one model, normalised to the same record whatever the provider (study design v8, 10.2 and
10.9). No temperature, top_p or seed is sent. Reasoning is set explicitly. Nothing here prints.

Each call() returns: response_id, model_returned, finish ('completed' | 'truncated' | 'refused' | other),
text (the visible reply), usage (token counts), detail (provider-specific extras worth keeping).
"""
import asyncio
import json
import os
import random

from config import FIELD_NAMES, MAX_OUTPUT_TOKENS, PRICES, REPLY_LANGUAGE


def _result(**fields):
    base = {"response_id": None, "model_returned": None, "finish": None, "text": "", "usage": {}, "detail": None}
    base.update(fields)
    return base


def cost_usd(model, usage):
    price = PRICES.get(model)
    if not price or not usage:
        return 0.0
    return (usage.get("uncached_input", 0) * price["input"]
            + usage.get("cached_input", 0) * price["cached"]
            + usage.get("cache_write", 0) * price["cache_write"]
            + usage.get("output", 0) * price["output"]) / 1e6


class OpenAIProvider:
    name = "openai"

    def __init__(self):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(max_retries=5, timeout=900)

    async def call(self, cfg, system, user, lang):
        r = await self.client.responses.create(
            model=cfg["model"],
            instructions=system,
            input=user,
            reasoning={"effort": cfg["reasoning"]},
            max_output_tokens=MAX_OUTPUT_TOKENS,
            store=False,
        )
        u = r.usage
        total_in = (u.input_tokens or 0) if u else 0
        details_in = getattr(u, "input_tokens_details", None)
        cached = (getattr(details_in, "cached_tokens", 0) or 0) if details_in else 0
        details_out = getattr(u, "output_tokens_details", None)
        refused = any(getattr(part, "type", None) == "refusal"
                      for item in (r.output or []) if getattr(item, "type", None) == "message"
                      for part in (getattr(item, "content", None) or []))
        if r.status == "incomplete":
            reason = getattr(r.incomplete_details, "reason", None)
            finish = {"max_output_tokens": "truncated", "content_filter": "refused"}.get(reason, f"incomplete:{reason}")
        elif refused:
            finish = "refused"
        else:
            finish = r.status
        usage = {
            "input_total": total_in,
            "uncached_input": max(total_in - cached, 0),
            "cached_input": cached,
            "cache_write": 0,
            "output": (u.output_tokens or 0) if u else 0,
            "reasoning": (getattr(details_out, "reasoning_tokens", 0) or 0) if details_out else 0,
        }
        detail = {"cache_write_tokens_reported": getattr(details_in, "cache_write_tokens", None) if details_in else None,
                  "service_tier": getattr(r, "service_tier", None)}
        return _result(response_id=r.id, model_returned=r.model, finish=finish, text=r.output_text or "",
                       usage=usage, detail=detail)


class AnthropicProvider:
    name = "anthropic"

    def __init__(self):
        from anthropic import AsyncAnthropic
        self.client = AsyncAnthropic(max_retries=5, timeout=900)

    async def call(self, cfg, system, user, lang):
        async with self.client.messages.stream(
            model=cfg["model"],
            max_tokens=MAX_OUTPUT_TOKENS,
            system=system,
            messages=[{"role": "user", "content": user}],
            thinking={"type": "adaptive"},
            output_config={"effort": cfg["reasoning"]},
            cache_control={"type": "ephemeral"},
        ) as stream:
            m = await stream.get_final_message()
        text = "".join(block.text for block in m.content if block.type == "text")
        finish = {"end_turn": "completed", "max_tokens": "truncated", "refusal": "refused"}.get(
            m.stop_reason, str(m.stop_reason))
        u = m.usage
        uncached = u.input_tokens or 0
        read = u.cache_read_input_tokens or 0
        write = u.cache_creation_input_tokens or 0
        details_out = getattr(u, "output_tokens_details", None)
        usage = {
            "input_total": uncached + read + write,
            "uncached_input": uncached,
            "cached_input": read,
            "cache_write": write,
            "output": u.output_tokens or 0,
            "reasoning": None,
        }
        detail = {"output_tokens_details": details_out.model_dump() if details_out is not None else None,
                  "stop_details": m.stop_details.model_dump() if getattr(m, "stop_details", None) else None}
        return _result(response_id=m.id, model_returned=m.model, finish=finish, text=text, usage=usage, detail=detail)


class GoogleProvider:
    name = "google"

    def __init__(self):
        from google import genai
        from google.genai import types
        self.types = types
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

    async def call(self, cfg, system, user, lang):
        t = self.types
        level = {"low": t.ThinkingLevel.LOW, "medium": t.ThinkingLevel.MEDIUM, "high": t.ThinkingLevel.HIGH}[cfg["reasoning"]]
        r = await self.client.aio.models.generate_content(
            model=cfg["model"],
            contents=user,
            config=t.GenerateContentConfig(
                system_instruction=system,
                max_output_tokens=MAX_OUTPUT_TOKENS,
                thinking_config=t.ThinkingConfig(thinking_level=level),
                automatic_function_calling=t.AutomaticFunctionCallingConfig(disable=True),  # no tools; quiets a warning
            ),
        )
        candidate = r.candidates[0] if r.candidates else None
        reason = getattr(candidate, "finish_reason", None) if candidate else None
        reason = getattr(reason, "name", None) or (str(reason) if reason is not None else "")
        blocked = getattr(getattr(r, "prompt_feedback", None), "block_reason", None)
        text = ""
        if candidate is not None and candidate.content is not None and candidate.content.parts:
            text = "".join(p.text for p in candidate.content.parts
                           if getattr(p, "text", None) and not getattr(p, "thought", False))
        if blocked:
            finish = "refused"
        elif reason == "STOP":
            finish = "completed"
        elif reason == "MAX_TOKENS":
            finish = "truncated"
        elif reason in {"SAFETY", "RECITATION", "PROHIBITED_CONTENT", "BLOCKLIST", "SPII"}:
            finish = "refused"
        else:
            finish = reason.lower() or "unknown"
        um = r.usage_metadata
        prompt_tokens = (um.prompt_token_count or 0) if um else 0
        cached = (um.cached_content_token_count or 0) if um else 0
        thoughts = (um.thoughts_token_count or 0) if um else 0
        usage = {
            "input_total": prompt_tokens,
            "uncached_input": max(prompt_tokens - cached, 0),
            "cached_input": cached,
            "cache_write": 0,
            "output": ((um.candidates_token_count or 0) if um else 0) + thoughts,
            "reasoning": thoughts,
        }
        detail = {"finish_reason": reason, "block_reason": str(blocked) if blocked else None}
        return _result(response_id=r.response_id, model_returned=r.model_version, finish=finish, text=text,
                       usage=usage, detail=detail)


class DryRunProvider:
    """No API call. Fabricated replies in the arm's language, with occasional failures, to test the plumbing."""
    name = "dryrun"
    SAMPLE = {
        "el": "Ο καθ’ ου η αίτηση δεν έχει πραγματική προοπτική επιτυχίας. Η υπεράσπιση είναι γενική άρνηση.",
        "en": "The respondent has no real prospect of success. The defence is a bare denial of the claim.",
        "de": "Der Antragsgegner hat keine realistische Erfolgsaussicht. Die Verteidigung ist nicht substantiiert.",
    }

    def __init__(self, seed=0):
        self.rng = random.Random(seed)

    async def call(self, cfg, system, user, lang):
        await asyncio.sleep(self.rng.uniform(0.005, 0.03))
        roll = self.rng.random()
        n_in = len(system + user) // 3
        usage = {"input_total": n_in, "uncached_input": n_in, "cached_input": 0, "cache_write": 0,
                 "output": 180, "reasoning": 0}
        if roll < 0.04:
            return _result(response_id="dry", model_returned="dryrun", finish="truncated", text="", usage=usage)
        if roll < 0.08:
            text = "I cannot produce JSON for this."
        else:
            keys = FIELD_NAMES[lang]
            text = json.dumps({keys[0]: self.SAMPLE[REPLY_LANGUAGE[lang]], keys[1]: self.rng.randint(1, 4),
                               keys[2]: self.rng.randint(1, 5)}, ensure_ascii=False)
        return _result(response_id=f"dry-{self.rng.getrandbits(32):08x}", model_returned="dryrun",
                       finish="completed", text=text, usage=usage)
