#!/usr/bin/env python3
"""Structural guards for bounded scheduler/device freeze evidence."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]

def body(source: str, name: str) -> str:
    match = re.search(rf"\b(?:static\s+)?(?:void|int)\s+{name}\s*\([^;]*?\)\s*\{{", source, re.S)
    if not match:
        raise AssertionError(f"missing function {name}")
    start, depth = match.end(), 1
    for pos in range(start, len(source)):
        depth += source[pos] == "{"
        depth -= source[pos] == "}"
        if depth == 0:
            return source[start:pos]
    raise AssertionError(f"unterminated function {name}")

heartbeat = (ROOT / "runtime/src/freeze_heartbeat.c").read_text(encoding="utf-8")
traps = (ROOT / "runtime/src/traps.c").read_text(encoding="utf-8")
freeze_write = body(heartbeat, "freeze_dump_write")
scheduler_dump = body(traps, "psx_scheduler_freeze_dump_json")

for token in ("psx_scheduler_freeze_dump_json(f, debug_cpu_ptr);",
              "cdrom_debug_snapshot(&cd);", "mdec_debug_get_state(&mdec);",
              "spu_debug_info(&spu);"):
    assert token in freeze_write
for token in ("g_sched_escape_ring", "g_thread_ctx_ring",
              r'\"escape_tail\"', r'\"thread_ctx_tail\"',
              "e->seq != (uint32_t)seq"):
    assert token in scheduler_dump
heartbeat_tick = body(heartbeat, "heartbeat_write")
for forbidden in ("psx_scheduler_freeze_dump_json", "cdrom_debug_snapshot",
                  "mdec_debug_get_state", "spu_debug_info"):
    assert forbidden not in heartbeat_tick

print("PASS: freeze evidence is bounded, freeze-only, and scheduler/device complete")
