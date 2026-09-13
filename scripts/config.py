# -*- coding: utf-8 -*-
"""Run configuration: study design v8, sections 6.1 and 10. Every value here is part of the protocol."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STIMULI = ROOT / "data" / "stimuli"
PROMPTS = ROOT / "prompts"
RAW = ROOT / "raw"
FROZEN = ROOT / "FROZEN.sha256"

CASES = ("C0990", "C1026", "C1099", "C1195", "C1292", "C1316", "C1387", "C1423", "C1460", "C1621")

# Arm -> language of its prompt and rule text (v8 section 6.1).
ARMS = {"gr": "el", "bt-en": "el", "bt-de": "el", "en": "en", "de-lit": "de-lit", "de-eng": "de-eng"}
GREEK_ARM = "gr"  # drawn twice as often in the main run, for the split-half noise floor

# JSON field names in each prompt language (prompting.md D-P4) and the recorded fallback keys.
FIELD_NAMES = {
    "el": ("αιτιολογία", "κατάληξη", "λόγος"),
    "en": ("reasoning", "outcome", "ground"),
    "de-lit": ("Begründung", "Ergebnis", "Grund"),
    "de-eng": ("Begründung", "Ergebnis", "Grund"),
}
FALLBACK_KEYS = ("r", "d", "g")
REPLY_LANGUAGE = {"el": "el", "en": "en", "de-lit": "de", "de-eng": "de"}

# Model configurations (v8 sections 10.1, 10.2). No temperature, top_p or seed is sent to any model.
CONFIGS = {
    "terra": {"provider": "openai", "model": "gpt-5.6-terra", "reasoning": "medium"},
    "terra-off": {"provider": "openai", "model": "gpt-5.6-terra", "reasoning": "none"},
    "sonnet": {"provider": "anthropic", "model": "claude-sonnet-5", "reasoning": "medium"},
    "gemini": {"provider": "google", "model": "gemini-3.6-flash", "reasoning": "medium"},
}

MAX_OUTPUT_TOKENS = 32000  # v8 section 10.3; reasoning tokens count against it

# Draws per arm, per case, per configuration. The Greek arm gets twice this in the main run.
# Main run 31 (Greek 62), decided by the author on 13 September 2026 after the pilot projected $52 at 25;
# "reduced" (25) is the fallback if a projection ever exceeds the budget. Pilot 2 (reduced from 3 the same day).
DRAWS = {"main": 31, "reduced": 25, "pilot": 2}
GREEK_FACTOR = {"main": 2, "reduced": 2, "pilot": 1}

# Failed draws in a block are replaced until it has k valid replies, up to this share of k in extra calls
# (12 extra for a 31-draw block, 25 for the 62-draw Greek block; 2 in the pilot). A block that still falls
# short is reported as incomplete.
REPLACEMENT_SHARE = {"main": 0.4, "reduced": 0.4, "pilot": 1.0}


def max_replacements(mode, k):
    return int(round(k * REPLACEMENT_SHARE[mode]))

# List prices in US dollars per million tokens, consulted 13 September 2026. Confirm on the run date.
# OpenAI and Google report cached tokens inside total input; Anthropic reports them separately.
PRICES = {
    "gpt-5.6-terra": {"input": 2.00, "cached": 0.20, "cache_write": 2.00, "output": 12.00},
    "claude-sonnet-5": {"input": 2.00, "cached": 0.20, "cache_write": 2.50, "output": 10.00},
    "gemini-3.6-flash": {"input": 0.75, "cached": 0.075, "cache_write": 0.75, "output": 3.75},
}

# Budget (v8 section 10.3). Costs are computed in dollars and compared with these euro figures as they
# stand, which overstates the cost while a euro buys more than a dollar.
BUDGET_EUR = 100
CEILING_EUR = 150
PILOT_CAP_EUR = 30  # hard stop for the pilot

# Calls sent at the same time to each provider. Lower these if a provider reports rate limits.
CONCURRENCY = {"openai": 8, "anthropic": 8, "google": 8}

# A call that fails before a reply arrives (network error, rate limit after the SDK's own retries) is
# retried. Such failures are logged but are not draws.
TRANSPORT_ATTEMPTS = 4

# Analysis (v8 sections 10.4-10.7 and 12). Every seed is fixed here, before the main run.
RESULTS = ROOT / "results"
N_SPLITS = 200            # random halvings of the Greek draws
SPLIT_SEED = 20260913
N_BOOT = 10000            # paired bootstrap resamples over cases
BOOT_SEED = 20260914
NOISE_SHARE = 0.60        # flip code N: modal share below this in either arm
REASONS_PER_SIDE = 3      # reasons shown for each arm in the error-coding workbook

# The court's order on the model's four options (v8 section 10.4). Judgment on the claim, or the claim
# dismissed on a defendant's application, is 1, or 2 where the order was partial.
COURT_DISPOSAL = {"SUMMARY_JUDGMENT": 1, "CLAIM_STRUCK_OUT": 1, "APPLICATION_DISMISSED": 3, "CONDITIONAL_ORDER": 4}
# The court's dominant ground on the model's five grounds (v8 section 11). complex_case and
# conditional_24_6_2 have no fixed mapping; no case in the ten is coded with either.
COURT_GROUND = {"no_real_prospect": 1, "disputed_facts": 1, "evidence_not_investigated": 1, "law_point": 2,
                "limb_b": 3, "procedural": 4}

OPTION_LABELS = {1: "granted in full", 2: "granted in part", 3: "dismissed", 4: "conditional order"}
GROUND_LABELS = {1: "real prospect of success", 2: "point of law or construction of a document",
                 3: "other compelling reason for a trial", 4: "procedural point", 5: "another ground"}
