from pathlib import Path
import re


root = Path(__file__).resolve().parents[2]
main_source = (root / "runtime/src/main.cpp").read_text(encoding="utf-8")
beetle_source = (root / "runtime/src/beetle_main.cpp").read_text(
    encoding="utf-8")
sf3_keybinds = (root / "lab/sf3/keybinds.ini").read_text(encoding="utf-8")

# Turbo belongs to an otherwise unused frontend key. Tab remains available to
# the guest controller mapping (SF3 uses it for R1) and must not be intercepted.
assert "keys[SDL_SCANCODE_KP_PLUS]" in main_source
assert "keys[SDL_SCANCODE_TAB]" not in main_source
assert "keys[SDL_SCANCODE_KP_PLUS]" in beetle_source
assert "keys[SDL_SCANCODE_TAB]" not in beetle_source
assert re.search(r"^r1\s*=\s*Tab$", sf3_keybinds, re.MULTILINE)
