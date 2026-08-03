#!/usr/bin/env python3
"""Select only capture identities represented by a proven cache.

This is a migration aid for rebuilding an overlay cache under a new emitter
hash. It does not infer safety: the supplied cache directory is the explicit
operator-approved identity set, and every selected capture must match one of
its immutable ``<address>_<crc>.dll`` names exactly.
"""

import argparse
import base64
import binascii
import json
from pathlib import Path


def capture_identity(capture: dict) -> str:
    data = base64.b64decode(capture["bytes_b64"], validate=True)
    address = int(capture["load_addr"], 0) & 0x1FFFFFFF
    return f"{address:08X}_{binascii.crc32(data) & 0xFFFFFFFF:08X}"


def capture_sources(path: Path) -> list[Path]:
    result = [path]
    history = Path(str(path) + ".d")
    if history.is_dir():
        result.extend(sorted(history.glob("*.json")))
    return result


def load_captures(path: Path) -> list[dict]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if isinstance(value, dict):
        value = value.get("captures", [])
    if not isinstance(value, list):
        raise ValueError(f"capture document is not a list: {path}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--captures", action="append", type=Path, required=True)
    parser.add_argument("--approved-cache", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    approved = {item.stem.upper() for item in args.approved_cache.glob("*.dll")}
    if not approved:
        parser.error("approved cache contains no immutable DLL identities")

    unique: dict[str, dict] = {}
    for root in args.captures:
        for source in capture_sources(root):
            for capture in load_captures(source):
                identity = capture_identity(capture)
                if identity in approved:
                    unique[identity] = capture

    selected = [unique[key] for key in sorted(unique)]
    if not selected:
        parser.error("no capture identity matched the approved cache")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(selected, indent=2) + "\n", encoding="utf-8")
    print(f"selected {len(selected)} exact captures from {len(approved)} approved DLL identities")
    for identity in sorted(unique):
        print(identity)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
