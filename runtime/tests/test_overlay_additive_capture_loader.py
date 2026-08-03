#!/usr/bin/env python3
"""Regression for release overlay compilation consuming immutable history."""

import base64
import importlib.util
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "compile_overlays", ROOT / "tools" / "compile_overlays.py"
)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def region(payload: bytes, *pcs: int) -> dict:
    return {
        "schema": "psxrecomp overlay capture v2",
        "load_addr": "0x80150000",
        "size": len(payload),
        "bytes_b64": base64.b64encode(payload).decode("ascii"),
        "executed_pcs": [f"0x{pc:08X}" for pc in pcs],
        "dispatch_entry_pcs": [],
        "function_entry_pcs": [],
        "seeds": [],
    }


with tempfile.TemporaryDirectory() as temporary:
    latest = Path(temporary) / "overlay_captures.json"
    history = Path(str(latest) + ".d")
    history.mkdir()
    payload_a = b"\x01\x02\x03\x04"
    payload_b = b"\x05\x06\x07\x08"
    latest.write_text(json.dumps([region(payload_a, 0x80150004)]), encoding="utf-8")
    (history / "001.json").write_text(
        json.dumps([region(payload_a, 0x80150000), region(payload_b, 0x80150000)]),
        encoding="utf-8",
    )
    (history / "torn.json").write_text("[{", encoding="utf-8")

    captures, sources = MODULE.load_additive_captures(str(latest))
    assert len(sources) == 2, sources
    assert len(captures) == 2, captures
    by_payload = {
        base64.b64decode(capture["bytes_b64"]): capture for capture in captures
    }
    assert by_payload[payload_a]["executed_pcs"] == [0x80150000, 0x80150004]
    assert by_payload[payload_b]["executed_pcs"] == [0x80150000]

print("overlay additive capture loader: PASS")
