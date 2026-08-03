#!/usr/bin/env python3
"""Source guards for the human-capture and bounded hidden replay handoff."""

from pathlib import Path
import subprocess
import sys


root = Path(__file__).resolve().parents[2]
record = root / "lab" / "sf3" / "record_input_route.ps1"
replay = root / "lab" / "sf3" / "replay_input_route.ps1"
observer = root / "lab" / "sf3" / "observe_input_route.py"
transition = root / "lab" / "sf3" / "capture_transition_failure.ps1"

record_text = record.read_text(encoding="utf-8")
replay_text = replay.read_text(encoding="utf-8")
observer_text = observer.read_text(encoding="utf-8")
transition_text = transition.read_text(encoding="utf-8")

record_required = (
    "PSX_INPUT_RECORD",
    "PSX_INPUT_REPLAY",
    "'--renderer', $Renderer",
    "Release all controls before closing",
    ".partial",
    "[switch]$Unique",
    "yyyyMMdd-HHmmss",
    "Start-Process",
    "-Wait -PassThru",
    "$process.ExitCode",
)
replay_required = (
    "PSX_INPUT_REPLAY",
    "PSX_INPUT_STOP_AFTER",
    "SDL_AUDIODRIVER",
    "--hidden-window",
    "'--renderer', $Renderer",
    "bounded input sample limit reached",
    "PSXPAD2",
    "Start-Process",
    "-Wait -PassThru",
    "$process.ExitCode",
)
for path, source, tokens in (
    (record, record_text, record_required),
    (replay, replay_text, replay_required),
):
    missing = [token for token in tokens if token not in source]
    if missing:
        raise SystemExit(f"{path.name} contract tokens missing: {missing}")

transition_required = (
    "ConvertTo-NativeArgument", "$start.Arguments =", "PSX_INPUT_RECORD",
    "manual-input.psxpad", "psx_freeze_dump_*.json", ".partial",
)
missing = [token for token in transition_required if token not in transition_text]
if missing:
    raise SystemExit(f"{transition.name} contract tokens missing: {missing}")
if "$start.ArgumentList" in transition_text:
    raise SystemExit("transition capture regressed to PowerShell-7-only ArgumentList")

runtime = (root / "runtime" / "src" / "main.cpp").read_text(encoding="utf-8")
if "!g_headless && !g_hidden_window" not in runtime:
    raise SystemExit("bounded replay must accept the hidden renderer without accepting visible mode")
if "bounded input sample limit reached" not in runtime:
    raise SystemExit("bounded replay completion marker missing")

observer_required = (
    'env["PSX_INPUT_REPLAY"]',
    'env["PSX_INPUT_STOP_AFTER"]',
    'env["PSX_INPUT_STOP_AFTER"] = str(stop_after)',
    '"--memcard-source"',
    '"--stop-after"',
    '"--capture-frame"',
    '"--capture-frame-range"',
    '"--capture-frame-step"',
    "shutil.copy2",
    '"--hidden-window"',
    '"display_ring_color_scan"',
    '"display_ring_color_stats"',
    '"display_ring_get"',
    '"fmv_state"',
    '"mdec_state"',
    '"irq_state"',
    '"overlay_loader_status"',
    '"dirty_ram_stats"',
    '"application_transitions"',
    '"state0_page_samples"',
    "newest - 1",
    '"missing_capture_frames": sorted(pending_capture_frames)',
)
missing = [token for token in observer_required if token not in observer_text]
if missing:
    raise SystemExit(f"observe_input_route.py contract tokens missing: {missing}")
for forbidden in ('"set_input"', '"press"', '"write_ram"'):
    if forbidden in observer_text:
        raise SystemExit(f"route observer must not use active guest control: {forbidden}")

if sys.platform == "win32":
    for script in (record, replay, transition):
        command = (
            "$e=$null; $t=$null; "
            f"[System.Management.Automation.Language.Parser]::ParseFile('{script}',[ref]$t,[ref]$e)"
            " | Out-Null; if ($e.Count) { $e | ForEach-Object { Write-Error $_ }; exit 1 }"
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-NonInteractive", "-Command", command],
            check=True,
        )
