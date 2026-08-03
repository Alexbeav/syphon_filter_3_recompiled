#!/usr/bin/env python3
"""Source guards for the human-capture and bounded hidden replay handoff."""

from pathlib import Path
import subprocess
import sys


root = Path(__file__).resolve().parents[2]
record = root / "lab" / "sf3" / "record_input_route.ps1"
replay = root / "lab" / "sf3" / "replay_input_route.ps1"

record_text = record.read_text(encoding="utf-8")
replay_text = replay.read_text(encoding="utf-8")

record_required = (
    "PSX_INPUT_RECORD",
    "PSX_INPUT_REPLAY",
    "--renderer $Renderer",
    "Release all controls before closing",
    ".partial",
)
replay_required = (
    "PSX_INPUT_REPLAY",
    "PSX_INPUT_STOP_AFTER",
    "SDL_AUDIODRIVER",
    "--hidden-window",
    "--renderer $Renderer",
    "bounded input sample limit reached",
    "PSXPAD2",
)
for path, source, tokens in (
    (record, record_text, record_required),
    (replay, replay_text, replay_required),
):
    missing = [token for token in tokens if token not in source]
    if missing:
        raise SystemExit(f"{path.name} contract tokens missing: {missing}")

runtime = (root / "runtime" / "src" / "main.cpp").read_text(encoding="utf-8")
if "!g_headless && !g_hidden_window" not in runtime:
    raise SystemExit("bounded replay must accept the hidden renderer without accepting visible mode")
if "bounded input sample limit reached" not in runtime:
    raise SystemExit("bounded replay completion marker missing")

if sys.platform == "win32":
    for script in (record, replay):
        command = (
            "$e=$null; $t=$null; "
            f"[System.Management.Automation.Language.Parser]::ParseFile('{script}',[ref]$t,[ref]$e)"
            " | Out-Null; if ($e.Count) { $e | ForEach-Object { Write-Error $_ }; exit 1 }"
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
            check=True,
        )
