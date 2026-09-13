# -*- coding: utf-8 -*-
"""Parse one reply (study design v8, sections 9.3 and 10.3). Returns a status and, where the reply is
usable, the disposal (1-4) and the ground (1-5). Nothing here prints.

Statuses: ok; truncated; refused; empty; unparseable; missing_fields; invalid_value; wrong_language.
Only 'ok' counts towards a block's k. A wrong-language reply keeps its disposal and ground in the record,
for the check that counts failures as a category of their own (v8 section 14), but is not valid.
"""
import json
import re

from config import FALLBACK_KEYS, FIELD_NAMES, REPLY_LANGUAGE

GREEK = re.compile(r"[Ͱ-Ͽἀ-῿]")
LATIN = re.compile(r"[A-Za-zÀ-ÿ]")
EN_WORDS = {"the", "and", "of", "to", "is", "that", "has", "not", "in", "which", "for", "on", "with",
            "a", "an", "be", "this", "there", "as", "by", "no", "are", "it", "its"}
DE_WORDS = {"der", "die", "das", "und", "ist", "nicht", "zu", "den", "dem", "des", "hat", "eine", "ein",
            "mit", "auf", "für", "sich", "von", "es", "kein", "keine", "dass", "im", "wird", "sind"}


def detect_language(text):
    greek, latin = len(GREEK.findall(text)), len(LATIN.findall(text))
    if greek + latin == 0:
        return "none"
    if greek >= latin:
        return "el"
    words = re.findall(r"[a-zäöüß]+", text.lower())
    en = sum(w in EN_WORDS for w in words)
    de = sum(w in DE_WORDS for w in words)
    if en == de:
        return "latin-unclear"
    return "en" if en > de else "de"


def _json_object(text):
    body = re.sub(r"^\s*```[A-Za-z]*\s*|\s*```\s*$", "", text.strip())
    start, end = body.find("{"), body.rfind("}")
    if start == -1 or end <= start:
        return None
    try:
        obj = json.loads(body[start:end + 1])
    except json.JSONDecodeError:
        return None
    return obj if isinstance(obj, dict) else None


def _as_int(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and value.strip().isdigit():
        return int(value.strip())
    return None


def parse_reply(text, prompt_lang, finish):
    out = {"status": None, "keys": None, "field_order_as_asked": None, "outcome": None, "ground": None,
           "reasoning_chars": None, "reply_language": None}
    if finish == "truncated":
        out["status"] = "truncated"
        return out
    if finish == "refused":
        out["status"] = "refused"
        return out
    if not text or not text.strip():
        out["status"] = "empty"
        return out
    obj = _json_object(text)
    if obj is None:
        out["status"] = "unparseable"
        return out
    expected = FIELD_NAMES[prompt_lang]
    if all(k in obj for k in expected):
        keys, out["keys"] = expected, "as_asked"
    elif all(k in obj for k in FALLBACK_KEYS):
        keys, out["keys"] = FALLBACK_KEYS, "fallback"
    else:
        out["keys"] = "other"
        out["status"] = "missing_fields"
        return out
    out["field_order_as_asked"] = [k for k in obj if k in keys] == list(keys)
    reasoning, outcome, ground = obj[keys[0]], _as_int(obj[keys[1]]), _as_int(obj[keys[2]])
    if not isinstance(reasoning, str) or not reasoning.strip() or outcome not in (1, 2, 3, 4) \
            or ground not in (1, 2, 3, 4, 5):
        out["status"] = "invalid_value"
        return out
    out["reasoning_chars"] = len(reasoning)
    out["reply_language"] = detect_language(reasoning)
    out["outcome"], out["ground"] = outcome, ground
    out["status"] = "ok" if out["reply_language"] == REPLY_LANGUAGE[prompt_lang] else "wrong_language"
    return out


def reasoning_text(text, prompt_lang):
    """The reasoning string of a reply that parses; an empty string otherwise."""
    obj = _json_object(text or "")
    if obj is None:
        return ""
    for keys in (FIELD_NAMES[prompt_lang], FALLBACK_KEYS):
        if all(k in obj for k in keys):
            value = obj[keys[0]]
            return value if isinstance(value, str) else ""
    return ""
