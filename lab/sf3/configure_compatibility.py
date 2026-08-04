#!/usr/bin/env python3
"""Apply source-owned SF3 compatibility defaults to a generated project."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil


def set_setting(text: str, table: str, setting: str) -> tuple[str, bool]:
    if setting in text:
        return text, False
    marker = f"[{table}]\n"
    if marker not in text:
        text += f"\n{marker}"
    return text.replace(marker, marker + setting + "\n", 1), True


def set_setting_value(text: str, table: str, key: str,
                      value: str) -> tuple[str, bool]:
    setting = f"{key} = {value}"
    marker = f"[{table}]\n"
    if marker not in text:
        return set_setting(text, table, setting)
    start = text.index(marker) + len(marker)
    end = text.find("\n[", start)
    if end < 0:
        end = len(text)
    section = text[start:end]
    for line in section.splitlines():
        if line.strip().startswith(f"{key} ="):
            if line.strip() == setting:
                return text, False
            updated = section.replace(line, setting, 1)
            return text[:start] + updated + text[end:], True
    return set_setting(text, table, setting)


def configure(project: Path, widescreen: bool = False, pgxp: bool = False,
              geometry_precision: bool = False,
              perspective_textures: bool = False,
              output_config: str | None = None) -> bool:
    game_toml = project / (output_config or "game.toml")
    output_created = False
    if output_config and not game_toml.exists():
        shutil.copyfile(project / "game.toml", game_toml)
        output_created = True
    text = game_toml.read_text(encoding="utf-8")
    text, compat_changed = set_setting(
        text, "runtime", "overlay_native = false")
    text, scale_changed = set_setting(
        text, "video", "supersampling = 4")
    text, mouse_pad_changed = set_setting(
        text, "controller", "mouse_pad = false")
    camera_changed = "[controller.mouse_camera]" not in text
    if camera_changed:
        camera_profile = (Path(__file__).with_name("redux") /
                          "game-controller.toml").read_text(encoding="utf-8")
        camera_table = camera_profile.split("[controller.mouse_camera]", 1)[1]
        text = (text.rstrip() +
                "\n\n[controller.mouse_camera]" + camera_table)

    widescreen_changed = False
    if widescreen:
        for key, value in (
            ("nw_hud_corners", "false"),
            ("nw_full_mirror", "false"),
        ):
            text, changed = set_setting_value(
                text, "widescreen", key, value)
            widescreen_changed = widescreen_changed or changed
        for table, setting in (
            ("video", 'aspect_ratio = "16:9"'),
            ("widescreen", "native_wide = true"),
            ("widescreen", "gte_game_mode = true"),
            ("widescreen", "nw_guest_projection = true"),
            # SCUS-94640 Mission 1 census: world list 483..925 polygons;
            # auxiliary lists 1..21. Sixty-four is a measured separation,
            # not an address/value copied from SF2.
            ("widescreen", "nw_world_min_polygons = 64"),
            ("widescreen.cull", "auto_screen_x = true"),
            ("widescreen.cull",
             'screen_h_imms = ["0xE0", "0xF0", "0xF1"]'),
        ):
            text, changed = set_setting(text, table, setting)
            widescreen_changed = widescreen_changed or changed
    precision_changed = False
    if pgxp:
        geometry_precision = True
        perspective_textures = True
    for enabled, setting in (
        (geometry_precision, "geometry_precision = true"),
        (perspective_textures, "perspective_textures = true"),
    ):
        if enabled:
            text, changed = set_setting(text, "video", setting)
            precision_changed = precision_changed or changed
    game_toml.write_text(text, encoding="utf-8", newline="\n")

    source_bindings = Path(__file__).with_name("keybinds.ini")
    project_bindings = project / "keybinds.ini"
    bindings_changed = (not project_bindings.exists() or
                        project_bindings.read_bytes() != source_bindings.read_bytes())
    if bindings_changed:
        shutil.copyfile(source_bindings, project_bindings)

    cmake = project / "CMakeLists.txt"
    cmake_text = cmake.read_text(encoding="utf-8")
    config_select_changed = "SF3_GAME_CONFIG" not in cmake_text
    if config_select_changed:
        cmake_text = cmake_text.replace(
            'set(PSXRECOMP_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/psxrecomp")',
            'set(SF3_GAME_CONFIG "game.toml" CACHE STRING '
            '"Generated game config selected for this build")\n'
            'set(PSXRECOMP_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/psxrecomp")')
        cmake_text = cmake_text.replace(
            'DEFAULT_GAME_CONFIG_PATH "game.toml"',
            'DEFAULT_GAME_CONFIG_PATH "${SF3_GAME_CONFIG}"')
    copy_block = """
if(EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/keybinds.ini")
  add_custom_command(TARGET psx-runtime POST_BUILD
    COMMAND ${CMAKE_COMMAND} -E copy_if_different
      "${CMAKE_CURRENT_SOURCE_DIR}/keybinds.ini"
      "$<TARGET_FILE_DIR:psx-runtime>/keybinds.ini")
endif()
"""
    cmake_changed = "TARGET_FILE_DIR:psx-runtime>/keybinds.ini" not in cmake_text
    if cmake_changed:
        cmake_text = cmake_text.rstrip() + "\n" + copy_block
    if config_select_changed or cmake_changed:
        cmake.write_text(cmake_text, encoding="utf-8", newline="\n")

    for build in project.glob("build*"):
        if build.is_dir():
            shutil.copyfile(source_bindings, build / "keybinds.ini")

    return (output_created or compat_changed or scale_changed or mouse_pad_changed or
            camera_changed or widescreen_changed or precision_changed or bindings_changed or
            config_select_changed or cmake_changed)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path,
                        help="generated SF3 project directory")
    parser.add_argument(
        "--widescreen", action="store_true",
        help="emit the isolated native-wide/culling-capable SF3 candidate")
    parser.add_argument(
        "--pgxp", action="store_true",
        help="emit the isolated address-provenance PGXP candidate")
    parser.add_argument(
        "--geometry-precision", action="store_true",
        help="emit only the fractional-geometry PGXP axis")
    parser.add_argument(
        "--perspective-textures", action="store_true",
        help="emit only the perspective-texture PGXP axis")
    parser.add_argument(
        "--output-config",
        help="write/read a sibling config instead of changing game.toml")
    args = parser.parse_args()
    project = args.project.resolve()
    changed = configure(project, widescreen=args.widescreen, pgxp=args.pgxp,
                        geometry_precision=args.geometry_precision,
                        perspective_textures=args.perspective_textures,
                        output_config=args.output_config)
    print(f"SF3 compatibility/presentation defaults "
          f"{'applied' if changed else 'already present'}: {project}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
