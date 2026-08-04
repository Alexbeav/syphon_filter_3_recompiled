from pathlib import Path


source = (Path(__file__).parents[1] / "src" / "main.cpp").read_text(
    encoding="utf-8"
)

required = (
    "static bool keyboard_input_focused(void)",
    "if (!keyboard_input_focused()) return 0xFFFF;",
    "if (!keyboard_input_focused()) return;",
    "&& keyboard_input_focused())",
    "if (keyboard_input_focused()) {",
    "mouse_pad_set_focus(mouse_focus);",
    "ev.type == SDL_MOUSEWHEEL",
    "mouse_pad_add_wheel((int)ev.wheel.y);",
    "mouse_pad_merge_buttons(btn, host)",
)
for guard in required:
    assert guard in source, f"missing background-input guard: {guard}"
