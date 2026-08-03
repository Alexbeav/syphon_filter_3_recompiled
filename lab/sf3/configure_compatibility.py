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


def configure(project: Path) -> bool:
    game_toml = project / "game.toml"
    text = game_toml.read_text(encoding="utf-8")
    text, compat_changed = set_setting(
        text, "runtime", "overlay_native = false")
    text, scale_changed = set_setting(
        text, "video", "supersampling = 4")
    game_toml.write_text(text, encoding="utf-8", newline="\n")

    source_bindings = Path(__file__).with_name("keybinds.ini")
    project_bindings = project / "keybinds.ini"
    bindings_changed = (not project_bindings.exists() or
                        project_bindings.read_bytes() != source_bindings.read_bytes())
    if bindings_changed:
        shutil.copyfile(source_bindings, project_bindings)

    cmake = project / "CMakeLists.txt"
    cmake_text = cmake.read_text(encoding="utf-8")
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
        cmake.write_text(cmake_text.rstrip() + "\n" + copy_block,
                         encoding="utf-8", newline="\n")

    for build in project.glob("build*"):
        if build.is_dir():
            shutil.copyfile(source_bindings, build / "keybinds.ini")

    return compat_changed or scale_changed or bindings_changed or cmake_changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path,
                        help="generated SF3 project directory")
    args = parser.parse_args()
    project = args.project.resolve()
    changed = configure(project)
    print(f"SF3 compatibility/presentation defaults "
          f"{'applied' if changed else 'already present'}: {project}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
