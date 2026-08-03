from pathlib import Path

root = Path(__file__).parents[2]
codegen = (root / "recompiler/src/code_generator.cpp").read_text(encoding="utf-8")
runtime = (root / "runtime/src/mouse_camera.c").read_text(encoding="utf-8")

for token in (
    "config_.mouse_camera_facing_site == block.start_addr",
    "*word != config_.mouse_camera_facing_expected",
    "psx_mouse_camera_hook(cpu, 0x{:08X}u)",
):
    assert token in codegen, f"missing exact codegen guard: {token}"

for token in (
    "site != s_config.facing_site",
    "cpu->read_word(site) != s_config.facing_expected",
    "cpu->read_word(s_config.application_state_addr) != 0u",
    "player = cpu->gpr[s_config.player_reg]",
    "owner != player",
):
    assert token in runtime, f"missing fail-closed runtime guard: {token}"
