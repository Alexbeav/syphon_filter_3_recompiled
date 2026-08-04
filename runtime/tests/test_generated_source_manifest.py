#!/usr/bin/env python3
"""Regression for bounded split-TU generated-source verification."""

from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "runtime" / "check_generated_sources.cmake"
RUNTIME_CMAKE = ROOT / "runtime" / "runtime.cmake"


class GeneratedSourceManifestTest(unittest.TestCase):
    def run_checker(self, manifest: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "cmake",
                f"-DSOURCES_FILE={manifest}",
                "-DTARGET=manifest-contract",
                "-P",
                str(CHECKER),
            ],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_manifest_avoids_unbounded_dash_d_sources(self) -> None:
        text = RUNTIME_CMAKE.read_text(encoding="utf-8")
        self.assertIn('"-DSOURCES_FILE=${_psxrt_generated_sources_file}"', text)
        self.assertNotIn('"-DSOURCES=${_game_generated_check}"', text)

    def test_existing_manifest_entries_pass(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sources = [root / f"split_{index:03}.c" for index in range(300)]
            for source in sources:
                source.write_text("/* fixture */\n", encoding="utf-8")
            manifest = root / "sources.txt"
            manifest.write_text(
                "\n".join(str(source) for source in sources) + "\n",
                encoding="utf-8",
            )
            result = self.run_checker(manifest)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_missing_entry_fails_with_actionable_message(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            missing = root / "missing_split.c"
            manifest = root / "sources.txt"
            manifest.write_text(str(missing) + "\n", encoding="utf-8")
            result = self.run_checker(manifest)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Recompiled game code is MISSING", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
