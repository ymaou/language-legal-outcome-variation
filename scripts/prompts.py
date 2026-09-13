# -*- coding: utf-8 -*-
"""Assemble what each call sends (prompting.md D-P5): the system prompt, and the user prompt with the rule
text and File A inserted. Reads only the published, frozen files in prompts/ and data/stimuli/.

The section headings '# SYSTEM PROMPT' and '# USER PROMPT' are not sent. File A is sent without its
case_id line. Line endings are normalised to LF; the frozen files themselves are not touched.
"""
import re

from config import ARMS, PROMPTS, PROMPT_SETS, STIMULI

_FRONT = re.compile(r"\A---\ncase_id: (C\d{4})\n---\n")


def _read(path):
    return path.read_text(encoding="utf-8").replace("\r\n", "\n")


def prompt_parts(lang, prompt_set="decide"):
    text = _read(PROMPT_SETS[prompt_set] / f"prompt_{lang}.md").lstrip()
    head, sep, user = text.partition("# USER PROMPT")
    if not sep or not head.startswith("# SYSTEM PROMPT"):
        raise ValueError(f"prompt_{lang}.md: section headings not found")
    system = head[len("# SYSTEM PROMPT"):].strip()
    user = user.strip()
    for placeholder in ("{rule text}", "{File A}"):
        if user.count(placeholder) != 1:
            raise ValueError(f"prompt_{lang}.md: {placeholder} must occur exactly once")
    return system, user


def rule_text(lang):
    return _read(PROMPTS / f"part24_{lang}.md").strip("\n")


def file_a(arm, case):
    text = _read(STIMULI / arm / f"{case}.md")
    match = _FRONT.match(text)
    if not match or match.group(1) != case:
        raise ValueError(f"{arm}/{case}.md: does not open with its case_id line")
    body = text[match.end():].strip("\n")
    if "case_id" in body:
        raise ValueError(f"{arm}/{case}.md: case_id appears in the body")
    return body


def build(arm, case, prompt_set="decide"):
    lang = ARMS[arm]
    system, user = prompt_parts(lang, prompt_set)
    user = user.replace("{rule text}", rule_text(lang), 1)
    user = user.replace("{File A}", file_a(arm, case), 1)
    return system, user
