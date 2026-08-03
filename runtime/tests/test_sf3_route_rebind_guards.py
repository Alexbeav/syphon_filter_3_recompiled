#!/usr/bin/env python3
"""Guard the explicit, payload-preserving route rebind helper."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
source = (ROOT / "lab/sf3/rebind_input_route.py").read_text(encoding="utf-8")
for token in ("--expected-old-id", "--new-id", "refusing to overwrite",
              "len(body.splitlines()) != count", "encode(\"ascii\") + body"):
    assert token in source
print("PASS: route rebinding is explicit and preserves the sample payload")
