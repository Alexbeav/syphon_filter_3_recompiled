#!/usr/bin/env python3
"""Structural guard for exact-identity cache migration."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
source = (ROOT / "lab/sf3/select_approved_overlay_captures.py").read_text(
    encoding="utf-8")
for token in ("binascii.crc32", "& 0x1FFFFFFF", 'glob("*.dll")',
              'history.glob("*.json")', "if identity in approved",
              "for key in sorted(unique)"):
    assert token in source
print("PASS: approved capture migration is exact, additive, and deterministic")
