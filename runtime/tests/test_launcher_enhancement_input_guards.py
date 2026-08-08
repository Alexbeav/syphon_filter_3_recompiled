#!/usr/bin/env python3
"""Pin launcher/runtime ownership of live dual input bindings."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MAIN = (ROOT / "runtime/src/main.cpp").read_text(encoding="utf-8")
HEADER = (ROOT / "runtime/include/psx_keybinds.h").read_text(encoding="utf-8")
KEYBINDS = (ROOT / "runtime/src/psx_keybinds.c").read_text(encoding="utf-8")

required_main = (
    "if (p.kind != 0 && p.kind != 1)",
    "btn &= pad_from_keyboard(player);",
    "gi.keybinds_path        = rui_keybinds_path.c_str();",
    "psx_keybinds_load_file(rui_keybinds_path.c_str());",
)
for token in required_main:
    if token not in MAIN:
        raise AssertionError(f"missing launcher/input lifecycle token: {token}")

for token in (
        "psx_keybinds_load_file", "psx_keybinds_get_button_alt",
        "psx_keybinds_set_button_alt"):
    if token not in HEADER:
        raise AssertionError(f"missing public keybind API: {token}")

for token in ("PSXKB_MOUSE_SC_BASE", "s_alt_binds", "held_scancode"):
    if token not in KEYBINDS:
        raise AssertionError(f"missing dual/mouse implementation: {token}")

print("PASS: launcher and runtime share live dual input bindings")
