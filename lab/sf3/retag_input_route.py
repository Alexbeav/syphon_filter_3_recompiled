#!/usr/bin/env python3
"""Retag an accepted PSXPAD2 payload for an intentionally changed runtime.

The source file must match an explicit whole-file SHA-256. Only the third
header token changes; the complete sample payload is asserted byte-identical.
"""

from __future__ import annotations
import argparse
import hashlib
from pathlib import Path
import re


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("source", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--expected-sha256", required=True)
    p.add_argument("--runtime-id", required=True)
    a = p.parse_args()
    raw = a.source.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual.lower() != a.expected_sha256.lower():
        raise SystemExit(f"source SHA-256 mismatch: {actual}")
    if not re.fullmatch(r"psxrecomp-[0-9a-f]{16}", a.runtime_id):
        raise SystemExit("runtime ID must match psxrecomp-<16 lowercase hex>")
    line, sep, payload = raw.partition(b"\n")
    fields = line.decode("ascii").split()
    if len(fields) != 3 or fields[0] != "PSXPAD2":
        raise SystemExit("source is not a counted PSXPAD2 route")
    if a.output.exists():
        raise SystemExit(f"output already exists: {a.output}")
    rewritten = f"PSXPAD2 {fields[1]} {a.runtime_id}\n".encode("ascii") + payload
    if rewritten.partition(b"\n")[2] != payload:
        raise SystemExit("internal payload-identity failure")
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_bytes(rewritten)
    print(f"samples={fields[1]} payload_sha256={hashlib.sha256(payload).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
