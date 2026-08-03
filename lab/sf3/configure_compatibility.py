#!/usr/bin/env python3
"""Apply source-owned SF3 compatibility defaults to a generated project."""

from __future__ import annotations

import argparse
from pathlib import Path


def configure(game_toml: Path) -> bool:
    text = game_toml.read_text(encoding="utf-8")
    setting = "overlay_native = false"
    if setting in text:
        return False
    marker = "[runtime]\n"
    if marker not in text:
        raise ValueError(f"missing [runtime] table in {game_toml}")
    text = text.replace(marker, marker + setting + "\n", 1)
    game_toml.write_text(text, encoding="utf-8", newline="\n")
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project", type=Path,
                        help="generated SF3 project directory")
    args = parser.parse_args()
    game_toml = args.project.resolve() / "game.toml"
    changed = configure(game_toml)
    print(f"SF3 compatibility defaults {'applied' if changed else 'already present'}: "
          f"{game_toml}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
