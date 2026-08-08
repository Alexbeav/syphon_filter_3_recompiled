import importlib.util
from pathlib import Path
import tempfile
import tomllib


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
        'aspect_ratio = "4:3"\n'
        "geometry_precision = false\n"
        "perspective_textures = false\n\n"
        "[controller]\ndefault_mode = \"digital\"\n",
        encoding="utf-8")
    (project / "CMakeLists.txt").write_text(
        'set(PSXRECOMP_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/psxrecomp")\n'
        "add_executable(psx-runtime main.cpp)\n"
        'DEFAULT_GAME_CONFIG_PATH "game.toml"\n', encoding="utf-8")

    assert module.configure(
        project, widescreen=True, output_config="game-wide.toml")
    first = (project / "game-wide.toml").read_text(encoding="utf-8")
    assert 'aspect_ratio = "16:9"' in first
    assert "[widescreen]" in first
    assert "native_wide = true" in first
    assert "offer = true" in first
    assert "gte_game_mode = true" in first
    assert "nw_full_mirror = false" in first
    assert "nw_hud_corners = false" in first
    assert "nw_full_mirror = true" not in first
    assert "nw_hud_corners = true" not in first
    assert "nw_guest_projection = true" in first
    assert "nw_world_min_polygons = 64" in first
    assert "[widescreen.cull]" in first
    assert "auto_screen_x = true" in first
    assert 'screen_h_imms = ["0xE0", "0xF0", "0xF1"]' in first
    assert "overlay_native = false" in first
    assert "supersampling = 4" in first
    assert "enabled = true" in first.split(
        "[controller.mouse_camera]", 1)[1]

    assert not module.configure(
        project, widescreen=True, output_config="game-wide.toml")
    second = (project / "game-wide.toml").read_text(encoding="utf-8")
    assert second == first
    assert second.count("[widescreen]") == 1
    assert second.count("[widescreen.cull]") == 1
    assert "[widescreen]" not in (project / "game.toml").read_text(
        encoding="utf-8")

    assert module.configure(
        project, pgxp=True, output_config="game-pgxp.toml")
    pgxp = (project / "game-pgxp.toml").read_text(encoding="utf-8")
    assert "geometry_precision = true" in pgxp
    assert "perspective_textures = true" in pgxp
    assert "native_wide = true" not in pgxp
    assert not module.configure(
        project, pgxp=True, output_config="game-pgxp.toml")

    assert module.configure(
        project, widescreen=True, pgxp=True,
        output_config="game-pgxp-wide.toml")
    combined = (project / "game-pgxp-wide.toml").read_text(encoding="utf-8")
    parsed = tomllib.loads(combined)
    assert parsed["video"]["aspect_ratio"] == "16:9"
    assert parsed["video"]["geometry_precision"] is True
    assert parsed["video"]["perspective_textures"] is True
    assert parsed["controller"]["mouse_camera"]["enabled"] is True
    assert parsed["widescreen"]["offer"] is True
    for key in ("aspect_ratio", "geometry_precision", "perspective_textures"):
        assert combined.count(f"{key} =") == 1

    assert module.configure(
        project, geometry_precision=True,
        output_config="game-pgxp-geometry.toml")
    geometry = (project / "game-pgxp-geometry.toml").read_text(
        encoding="utf-8")
    assert "geometry_precision = true" in geometry
    assert "perspective_textures = true" not in geometry
    assert "native_wide = true" not in geometry
    assert not module.configure(
        project, geometry_precision=True,
        output_config="game-pgxp-geometry.toml")

    assert module.configure(
        project, widescreen=True, geometry_precision=True,
        precise_culling=True,
        output_config="game-pgxp-culling-wide.toml")
    culling = tomllib.loads(
        (project / "game-pgxp-culling-wide.toml").read_text(
            encoding="utf-8"))
    assert culling["video"]["precise_culling"] is True
    assert culling["video"]["aspect_ratio"] == "16:9"
    assert culling["widescreen"]["offer"] is True
    assert culling["controller"]["mouse_camera"]["enabled"] is True

    assert module.configure(
        project, perspective_textures=True,
        output_config="game-pgxp-perspective.toml")
    perspective = (project / "game-pgxp-perspective.toml").read_text(
        encoding="utf-8")
    assert "geometry_precision = true" not in perspective
    assert "perspective_textures = true" in perspective
    assert "native_wide = true" not in perspective
    cmake = (project / "CMakeLists.txt").read_text(encoding="utf-8")
    assert 'set(SF3_GAME_CONFIG "game.toml" CACHE STRING' in cmake
    assert 'DEFAULT_GAME_CONFIG_PATH "${SF3_GAME_CONFIG}"' in cmake

profile = (root / "lab/sf3/redux/settings-wide.toml").read_text(
    encoding="utf-8")
assert 'aspect_ratio = "16:9"' in profile
assert "supersampling = 4" in profile
assert "frame_interpolation = false" in profile
assert "mouse_camera = true" in profile

pgxp_profile = (root / "lab/sf3/redux/settings-pgxp.toml").read_text(
    encoding="utf-8")
assert 'aspect_ratio = "4:3"' in pgxp_profile
assert "supersampling = 4" in pgxp_profile
assert "frame_interpolation = false" in pgxp_profile

print("SF3 widescreen profile: OK")
