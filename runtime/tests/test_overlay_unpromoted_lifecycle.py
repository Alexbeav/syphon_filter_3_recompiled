#!/usr/bin/env python3
"""Pin generic publication and loader ownership of unpromoted shards."""

import importlib.util
import json
from pathlib import Path
import tempfile


ROOT = Path(__file__).resolve().parents[2]
SPEC = importlib.util.spec_from_file_location(
    "compile_overlays", ROOT / "tools" / "compile_overlays.py")
if not SPEC or not SPEC.loader:
    raise RuntimeError("compile_overlays module is unavailable")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

with tempfile.TemporaryDirectory(prefix="psx-unpromoted-") as temporary:
    dll = str(Path(temporary) / "00010000_DEADBEEF.dll")
    MODULE.update_unpromoted_marker(dll, "source-owned-test-policy")
    marker = Path(dll).with_suffix(".unpromoted")
    payload = json.loads(marker.read_text(encoding="utf-8"))
    if payload != {
            "schema": MODULE.UNPROMOTED_MARKER,
            "reason": "source-owned-test-policy"}:
        raise AssertionError(f"unexpected marker payload: {payload!r}")
    MODULE.update_unpromoted_marker(dll, None)
    if marker.exists():
        raise AssertionError("promotion did not remove the quarantine marker")

loader = (ROOT / "runtime" / "src" / "overlay_loader.c").read_text(
    encoding="utf-8")
for required in (
        "cache_path_is_unpromoted(file->path)",
        "cache_path_is_unpromoted(full)",
        "if (cache_path_is_unpromoted(dll_path))"):
    if required not in loader:
        raise AssertionError(f"missing loader boundary: {required}")

if "source-owned-test-policy" in loader:
    raise AssertionError("evidence policy leaked into the generic loader")

print("PASS: unpromoted shard publication is atomic and loader-owned")
