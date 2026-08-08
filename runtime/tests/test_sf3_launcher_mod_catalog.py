#!/usr/bin/env python3
"""Qualify the source-owned, default-off SF3 enhancement catalog."""

import importlib.util
from pathlib import Path
import tempfile
import tomllib


ROOT = Path(__file__).resolve().parents[2]
CONFIGURATOR = ROOT / "lab/sf3/configure_compatibility.py"
spec = importlib.util.spec_from_file_location("sf3_configure", CONFIGURATOR)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

with tempfile.TemporaryDirectory() as tmp:
    project = Path(tmp)
    (project / "game.toml").write_text(
        '[game]\nid = "SCUS-94640"\n[runtime]\n[video]\n[widescreen]\n',
        encoding="utf-8")
    (project / "CMakeLists.txt").write_text(
        'set(PSX_RECOMP_UI OFF CACHE BOOL "" FORCE)\n'
        'set(PSXRECOMP_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/psxrecomp")\n'
        'psxrecomp_add_runtime_target(psx-runtime\n'
        '  DEFAULT_GAME_CONFIG_PATH "game.toml"\n)\n',
        encoding="utf-8")

    if not module.configure(project, launcher_mods=True):
        raise AssertionError("first launcher-Mod configuration reported no change")
    if module.configure(project, launcher_mods=True):
        raise AssertionError("launcher-Mod configuration is not idempotent")

    game = tomllib.loads((project / "game.toml").read_text(encoding="utf-8"))
    if game["video"].get("aspect_ratio") != "4:3":
        raise AssertionError("all-off launcher baseline is not 4:3")
    if game["video"].get("geometry_precision", True):
        raise AssertionError("all-off launcher baseline enables geometry PGXP")
    if game["video"].get("perspective_textures", True):
        raise AssertionError("all-off launcher baseline enables perspective PGXP")
    if game["controller"]["mouse_camera"].get("enabled", True):
        raise AssertionError("all-off launcher baseline enables mouse camera")
    if game["widescreen"].get("offer", True):
        raise AssertionError("legacy Settings widescreen still competes with Mods")

    manifest_path = (project / "mods/preloaded/packages/sf3.enhancements/"
                     "1.0.0/manifest.toml")
    manifest = tomllib.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest["target"] != [{"game_id": "SCUS-94640"}]:
        raise AssertionError("catalog target is not exact SCUS-94640")
    features = {feature["id"]: feature for feature in manifest["feature"]}
    if set(features) != {"mouse-look", "widescreen", "pgxp"}:
        raise AssertionError("catalog enhancement feature set drifted")
    if any(feature.get("default_enabled", True) for feature in features.values()):
        raise AssertionError("an enhancement is not default off")
    choices = manifest["option"][0]["choice"]
    if [choice["value"] for choice in choices] != ["geometry", "full"]:
        raise AssertionError("PGXP does not expose complete geometry/full modes")

    cmake = (project / "CMakeLists.txt").read_text(encoding="utf-8")
    for token in ('set(PSX_RECOMP_UI ON CACHE BOOL "" FORCE)',
                  "EXTRAS_SOURCES", "src/sf3_mods.c",
                  "Installing Syphon Filter 3 built-in mod catalog"):
        if token not in cmake:
            raise AssertionError(f"generated build omits catalog wiring: {token}")

plugin = (ROOT / "lab/sf3/src/sf3_mods.c").read_text(encoding="utf-8")
for token in ("PSX_MOD_PGXP_GEOMETRY", "PSX_MOD_PGXP_FULL",
              'strcmp(mode, "full")', '"sf3.widescreen"',
              '"sf3.mouse-look"', '"sf3.pgxp"'):
    if token not in plugin:
        raise AssertionError(f"trusted plugin mode missing: {token}")

print("PASS: SF3 launcher catalog is default-off, complete, and idempotent")
