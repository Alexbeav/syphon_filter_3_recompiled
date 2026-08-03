#!/usr/bin/env python3
"""Protect the bounded-cost and CPU-VRAM-nonmutating display-ring contract."""

from pathlib import Path


root = Path(__file__).resolve().parents[2]
source = (root / "runtime" / "src" / "debug_server.c").read_text(encoding="utf-8")

required = (
    'getenv("PSX_DISPLAY_RING_AUX")',
    "size_t vram = disp_ring_aux_enabled() ? (size_t)1024 * 512 : 0;",
    "if (e->vram) {",
    "display ring aux capture disabled",
    "handle_display_ring_color_stats",
    "handle_display_ring_color_scan",
    '\\"display_x\\"',
    '\\"display_y\\"',
)
missing = [token for token in required if token not in source]
if missing:
    raise SystemExit(f"display-ring bounded-cost guard missing: {missing}")

capture_start = source.index("static void disp_ring_capture(void)")
capture_end = source.index("static void handle_display_ring_aux", capture_start)
capture = source[capture_start:capture_end]
full_peek = "gl_renderer_fbo_peek(0, 0, 1024, 512, e->vram)"
if full_peek not in capture:
    raise SystemExit("display-ring full-VRAM forensic capture disappeared")
if capture.index("if (e->vram) {") > capture.index(full_peek):
    raise SystemExit("full-VRAM display-ring readback is no longer aux-gated")
if "gl_renderer_sync_cpu" in capture:
    raise SystemExit("display ring must not write FBO truth into CPU VRAM")
