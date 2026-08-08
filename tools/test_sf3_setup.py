from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest
import zipfile


ROOT = pathlib.Path(__file__).parents[1]
SETUP = ROOT / "public" / "SETUP.ps1"


class Sf3SetupContractTests(unittest.TestCase):
    def run_setup(self, root: pathlib.Path, *args: str, env=None) -> subprocess.CompletedProcess[str]:
        shell = shutil.which("pwsh") or shutil.which("powershell")
        if not shell:
            self.skipTest("PowerShell is unavailable")
        return subprocess.run(
            [shell, "-NoProfile", "-ExecutionPolicy", "Bypass",
             "-File", str(root / "SETUP.ps1"), *args],
            check=False, text=True, encoding="utf-8", errors="replace",
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env,
        )

    def test_player_entry_point_is_ascii_crlf(self) -> None:
        data = (ROOT / "public" / "SETUP.cmd").read_bytes()
        data.decode("ascii")
        self.assertNotIn(b"\n", data.replace(b"\r\n", b""))
        text = (ROOT / "public" / "START_HERE.md").read_text(encoding="utf-8")
        self.assertIn("WinGet, Git, pip, and Visual Studio are not required", text)
        self.assertNotIn("Python 3, CMake, Ninja, and a C/C++ compiler available", text)

    def test_builder_declares_tool_resolver_before_use(self) -> None:
        text = (ROOT / "tools" / "New-SF3LocalBuild.ps1").read_text(encoding="utf-8")
        declaration = text.index("function Resolve-CommandPath")
        first_use = text.index("$python = Resolve-CommandPath")
        self.assertLess(declaration, first_use)

    def test_resolve_one_owned_cue(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp) / "SF3Kit"
            root.mkdir()
            shutil.copy2(SETUP, root / "SETUP.ps1")
            cue = root / "Syphon Filter 3 (USA).cue"
            cue.write_text('FILE "track.bin" BINARY\n', encoding="ascii")
            result = self.run_setup(root, "-ResolveCueOnly")
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn(str(cue), result.stdout)

    def test_ambiguous_cue_selection_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp) / "SF3Kit"
            root.mkdir()
            shutil.copy2(SETUP, root / "SETUP.ps1")
            (root / "one.cue").write_text("FILE one.bin BINARY\n", encoding="ascii")
            (root / "two.cue").write_text("FILE two.bin BINARY\n", encoding="ascii")
            result = self.run_setup(root, "-ResolveCueOnly")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Could not uniquely find", result.stdout)

    @unittest.skipUnless(os.name == "nt", "Windows setup contract")
    def test_unverified_tool_archive_is_removed(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp) / "SF3Kit"
            root.mkdir()
            shutil.copy2(SETUP, root / "SETUP.ps1")
            archive = root / "untrusted.zip"
            with zipfile.ZipFile(archive, "w") as zf:
                zf.writestr("mingw64/bin/gcc.exe", b"untrusted")
            env = os.environ.copy()
            env["PATH"] = os.environ["SystemRoot"] + r"\System32"
            env["SF3_SETUP_DISABLE_STANDARD_DISCOVERY"] = "1"
            env["SF3_SETUP_TEST_MODE"] = "1"
            env["SF3_SETUP_TEST_WINLIBS_ARCHIVE"] = str(archive)
            env["SF3_SETUP_TEST_WINLIBS_SHA256"] = "0" * 64
            result = self.run_setup(root, "-PreflightOnly", "-InstallDependencies", env=env)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("archive hash mismatch", result.stdout)
            self.assertIn("untrusted download was removed", result.stdout)
            self.assertFalse((root / "dependencies" / "winlibs-16.1.0-14.0.0-r4").exists())

    def test_non_ascii_kit_path_fails_before_tool_work(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = pathlib.Path(temp) / "Γιώργος"
            root.mkdir()
            shutil.copy2(SETUP, root / "SETUP.ps1")
            result = self.run_setup(root, "-PreflightOnly", "-NoInstallDependencies")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("non-ASCII", result.stdout)
            self.assertNotIn("Downloading pinned", result.stdout)


if __name__ == "__main__":
    unittest.main()
