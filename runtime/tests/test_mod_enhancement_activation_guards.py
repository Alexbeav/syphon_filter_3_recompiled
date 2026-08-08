#!/usr/bin/env python3
"""Pin complete launcher-owned enhancement activation and reset ordering."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAIN = (ROOT / "runtime/src/main.cpp").read_text(encoding="utf-8")
STATE_H = (ROOT / "runtime/include/mod_enhancement_state.h").read_text(
    encoding="utf-8")
STATE_C = (ROOT / "runtime/src/mod_enhancement_state.c").read_text(
    encoding="utf-8")
MOUSE = (ROOT / "runtime/src/mouse_camera.c").read_text(encoding="utf-8")
RECOMPILER = (ROOT / "recompiler/src/main_psx.cpp").read_text(encoding="utf-8")

for token in (
        "int geometry_precision;", "int perspective_textures;",
        "PsxModEnhancementConfig baseline;",
        "PsxModEnhancementConfig current;"):
    if token not in STATE_H:
        raise AssertionError(f"incomplete enhancement state: {token}")

for token in (
        "mode >= PSX_MOD_PGXP_GEOMETRY",
        "mode >= PSX_MOD_PGXP_FULL",
        "state->current = state->baseline"):
    if token not in STATE_C:
        raise AssertionError(f"incomplete enhancement transition: {token}")

for token in (
        "g_geometry_precision ? 1 : 0",
        "g_perspective_textures ? 1 : 0",
        "psx_mod_enhancement_initialize(&g_mod_enhancements",
        "psx_mod_enhancement_reset(&g_mod_enhancements)",
        "psx_mouse_camera_set_enabled(g_mouse_camera_enabled)",
        "mouse_pad_reset()"):
    if token not in MAIN:
        raise AssertionError(f"missing runtime enhancement lifecycle: {token}")

activation = MAIN.index("mod_runtime_activate_plugins();")
reset = MAIN.rindex("psx_mod_enhancement_reset(&g_mod_enhancements)", 0,
                    activation)
apply = MAIN.rindex("apply_mod_enhancement_state();", 0, activation)
if not reset < apply < activation:
    raise AssertionError("enhancement baseline is not restored before activation")

if "s_config.enabled = enabled ? 1 : 0;\n    psx_mouse_camera_reset();" not in MOUSE:
    raise AssertionError("mouse-camera disable does not clear pending motion")

if "if (cfg.runtime.controller_mouse_camera_facing_site)" not in RECOMPILER:
    raise AssertionError("mouse-camera hook still depends on default enablement")

print("PASS: launcher enhancement modes reset completely before activation")
