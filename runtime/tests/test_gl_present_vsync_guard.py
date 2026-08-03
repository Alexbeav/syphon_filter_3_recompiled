#!/usr/bin/env python3
"""Source contract for direct-OpenGL present backpressure recovery."""

from pathlib import Path


root = Path(__file__).resolve().parents[2]
source = (root / "runtime" / "src" / "gpu_gl_renderer.c").read_text(
    encoding="utf-8"
)

required = (
    "static void swap_window_guarded(void)",
    "SDL_GL_SwapWindow(s_win)",
    "present_ms > 250",
    "g_present_slow_count >= 3",
    "SDL_GL_SetSwapInterval(0)",
    "g_present_vsync_disabled = 1",
    "if (g_present_vsync_disabled && interval != 0) interval = 0",
)
missing = [token for token in required if token not in source]
if missing:
    raise SystemExit(f"OpenGL vsync self-heal tokens missing: {missing}")

# The interpolation worker owns an interval-0 context and intentionally keeps
# its one raw host-cadence swap. Every guest-vblank GL path must use the guard.
if source.count("swap_window_guarded();") != 4:
    raise SystemExit("not every guest-vblank OpenGL present uses the guarded swap")
if source.count("SDL_GL_SwapWindow(s_win)") != 2:
    raise SystemExit("unexpected raw OpenGL swap bypasses or duplicates the guard")
