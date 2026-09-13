# -*- coding: utf-8 -*-
"""Refuse to run on changed materials: every file listed in FROZEN.sha256 must match its fingerprint."""
import hashlib

from config import FROZEN, ROOT


def verify_frozen():
    changed, n = [], 0
    for line in FROZEN.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        digest, path = line.split(None, 1)
        path = path.strip().lstrip("*")
        n += 1
        target = ROOT / path
        if not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != digest:
            changed.append(path)
    if changed:
        raise SystemExit("FROZEN FILES CHANGED - no model is called:\n  " + "\n  ".join(changed))
    return n
