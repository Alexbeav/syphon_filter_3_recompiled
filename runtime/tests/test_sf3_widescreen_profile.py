import importlib.util
from pathlib import Path
import tempfile


root = Path(__file__).resolve().parents[2]
configurator_path = root / "lab/sf3/configure_compatibility.py"
spec = importlib.util.spec_from_file_location(
    "sf3_configure_compatibility", configurator_path)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

with tempfile.TemporaryDirectory() as temp:
    project = Path(temp)
    (project / "game.toml").write_text(
        "[runtime]\nwindow_title = \"SF3 test\"\n\n"
        "[video]\nrenderer = \"opengl\"\n\n"
        "[controller]\ndefault_mode = \"digital\"\n",
        encoding="utf-8")
    (project / "CMakeLists.txt").write_text(
        'set(PSXRECOMP_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/psxrecomp")\n'
        "add_executable(psx-runtime main.cpp)\n"
        'DEFAULT_GAME_CONFIG_PATH "game.toml"\n', encoding="utf-8")

    assert module.configure(
        project, widescreen=True, output_config="game-wide.toml")
    first = (project / "game-wide.toml").read_text(encoding="utf-8")
    assert "[widescreen]" in first
    assert "native_wide = true" in first
    assert "gte_game_mode = true" in first
    assert "nw_full_mirror = true" in first
    assert "nw_hud_corners = true" in first
    assert "nw_guest_projection = true" in first
    assert "nw_world_min_polygons = 64" in first
    assert "[widescreen.cull]" in first
    assert "auto_screen_x = true" in first
    assert 'screen_h_imms = ["0xE0", "0xF0", "0xF1"]' in first
    assert "overlay_native = false" in first
    assert "supersampling = 4" in first

    assert not module.configure(
        project, widescreen=True, output_config="game-wide.toml")
    second = (project / "game-wide.toml").read_text(encoding="utf-8")
    assert second == first
    assert second.count("[widescreen]") == 1
    assert second.count("[widescreen.cull]") == 1
    assert "[widescreen]" not in (project / "game.toml").read_text(
        encoding="utf-8")
    cmake = (project / "CMakeLists.txt").read_text(encoding="utf-8")
    assert 'set(SF3_GAME_CONFIG "game.toml" CACHE STRING' in cmake
    assert 'DEFAULT_GAME_CONFIG_PATH "${SF3_GAME_CONFIG}"' in cmake

profile = (root / "lab/sf3/redux/settings-wide.toml").read_text(
    encoding="utf-8")
assert 'aspect_ratio = "16:9"' in profile
assert "supersampling = 4" in profile
assert "frame_interpolation = false" in profile
assert "mouse_camera = true" in profile

print("SF3 widescreen profile: OK")
