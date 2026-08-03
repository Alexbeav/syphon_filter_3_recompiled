#!/usr/bin/env python3
"""Explicitly rebind an unchanged PSXPAD2 route to a proven-compatible build.

This does not infer compatibility. The caller must provide both the expected
old ID and the new ID after reviewing the runtime delta. Sample payload bytes
are copied verbatim and the declared count is checked against the body.
"""

import argparse
from pathlib import Path


def valid_id(value: str) -> bool:
    return value.startswith("psxrecomp-") and value[10:].isalnum()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--expected-old-id", required=True)
    parser.add_argument("--new-id", required=True)
    args = parser.parse_args()
    if not valid_id(args.expected_old_id) or not valid_id(args.new_id):
        parser.error("compatibility IDs must be psxrecomp-* tokens")
    if args.output.exists():
        parser.error("refusing to overwrite output route")

    data = args.source.read_bytes()
    header, separator, body = data.partition(b"\n")
    if not separator:
        parser.error("source route has no body")
    fields = header.decode("ascii").split()
    if len(fields) != 3 or fields[0] != "PSXPAD2":
        parser.error("source route is not PSXPAD2")
    if fields[2] != args.expected_old_id:
        parser.error(f"source ID is {fields[2]}, not the asserted old ID")
    count = int(fields[1])
    if count < 1 or count > 10_000_000:
        parser.error("source sample count is outside the format bound")
    if len(body.splitlines()) != count:
        parser.error("source body does not match its declared sample count")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(
        f"PSXPAD2 {count} {args.new_id}\n".encode("ascii") + body)
    print(f"rebound {count} unchanged samples: {args.expected_old_id} -> {args.new_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
