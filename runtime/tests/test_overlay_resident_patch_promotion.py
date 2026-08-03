#!/usr/bin/env python3
"""Regression for fail-closed resident control-flow patch promotion."""

import importlib.util
import json
from pathlib import Path
import struct
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "compile_overlays", ROOT / "tools" / "compile_overlays.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def words(*values: int) -> bytes:
    return b"".join(struct.pack("<I", value) for value in values)


resident_bytes = words(0x27BDFFF0, 0x01204009, 0x24020001, 0x03E00008)
resident = (0x10000, resident_bytes)

assert not MODULE.resident_control_flow_patch(resident_bytes, 0x10000, resident)
assert MODULE.resident_control_flow_patch(
    words(0x27BDFFF0, 0x00000000, 0x24020001, 0x03E00008),
    0x10000, resident)
assert not MODULE.resident_control_flow_patch(
    words(0x27BDFFE0, 0x00000000, 0x24020001, 0x03E00008),
    0x10000, resident)
assert not MODULE.resident_control_flow_patch(
    words(0x27BDFFF0, 0x08004008, 0x24020001, 0x03E00008),
    0x10000, resident)

with tempfile.TemporaryDirectory() as temporary:
    dll = str(Path(temporary) / "00010000_DEADBEEF.dll")
    MODULE.update_unpromoted_marker(dll, "resident-control-flow-patch")
    marker = Path(dll).with_suffix(".unpromoted")
    payload = json.loads(marker.read_text(encoding="utf-8"))
    assert payload["schema"] == MODULE.UNPROMOTED_MARKER
    MODULE.update_unpromoted_marker(dll, None)
    assert not marker.exists()

loader = (ROOT / "runtime" / "src" / "overlay_loader.c").read_text(
    encoding="utf-8")
assert "cache_path_is_unpromoted(file->path)" in loader
assert "cache_path_is_unpromoted(full)" in loader
assert "if (cache_path_is_unpromoted(dll_path))" in loader

print("PASS: resident CFG-only variants remain captured evidence, not native authority")
