#!/usr/bin/env python3
"""Observe a captured SCUS-94640 route without supplying or forcing input."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any

from probe_story import ProbeError, app_pair, tcp_call, wait_for


def route_sample_count(path: Path) -> int:
    with path.open("rt", encoding="utf-8") as stream:
        header = stream.readline().split()
    if len(header) != 3 or header[0] != "PSXPAD2" or header[2] == "-":
        raise ProbeError("route must have a PSXPAD2 count and compatibility ID")
    try:
        count = int(header[1], 10)
    except ValueError as exc:
        raise ProbeError("route sample count is not decimal") from exc
    if not 1 <= count <= 10_000_000:
        raise ProbeError("route sample count is outside the supported range")
    return count


def safe_call(port: int, command: str, **fields: Any) -> dict[str, Any]:
    try:
        return tcp_call(port, command, **fields)
    except (ConnectionError, OSError, ProbeError) as exc:
        return {"ok": False, "error": str(exc)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cue", type=Path, help="user-owned USA SCUS-94640 cue")
    parser.add_argument("route", type=Path, help="captured PSXPAD2 input route")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--port", type=int, default=4388)
    parser.add_argument("--timeout", type=float, default=7200.0)
    parser.add_argument("--renderer", choices=("software", "opengl"), default="opengl")
    parser.add_argument("--display-ring-aux", action="store_true")
    parser.add_argument("--observed-red-limit-bp", type=int, default=1500)
    parser.add_argument("--observed-hot-red-limit-bp", type=int, default=500)
    args = parser.parse_args()
    for value, label in (
        (args.observed_red_limit_bp, "--observed-red-limit-bp"),
        (args.observed_hot_red_limit_bp, "--observed-hot-red-limit-bp"),
    ):
        if not 0 <= value <= 10000:
            parser.error(f"{label} must be between 0 and 10000")

    cue = args.cue.absolute()
    route = args.route.resolve()
    project = args.project.resolve()
    out = args.out.resolve()
    exe = project / "build-r1" / "Syphon_Filter_3_Recompiled.exe"
    game_toml = project / "game.toml"
    for path, label in (
        (cue, "cue"),
        (route, "input route"),
        (exe, "diagnostic executable"),
        (game_toml, "game.toml"),
    ):
        if not path.is_file():
            raise ProbeError(f"missing {label}: {path}")
    if out.exists():
        raise ProbeError(f"output directory must not exist: {out}")
    (out / "memcard").mkdir(parents=True)
    sample_count = route_sample_count(route)

    env = os.environ.copy()
    env["SDL_AUDIODRIVER"] = "dummy"
    env["PSX_DEBUG_FMV_QUIET"] = "1"
    env["PSX_INPUT_REPLAY"] = str(route)
    env.pop("PSX_INPUT_RECORD", None)
    env["PSX_INPUT_STOP_AFTER"] = str(sample_count)
    env["PSX_DISPLAY_RING_AUX"] = "1" if args.display_ring_aux else "0"
    command = [
        str(exe),
        "--hidden-window",
        "--no-launcher",
        "--renderer",
        args.renderer,
        "--game",
        str(game_toml),
        "--disc",
        str(cue),
        "--memcard-dir",
        str(out / "memcard"),
        "--debug-port",
        str(args.port),
    ]

    evidence: dict[str, Any] = {
        "renderer": args.renderer,
        "sample_count": sample_count,
        "display_ring_aux": args.display_ring_aux,
        "observed_corruption_limits_bp": {
            "red_dominant": args.observed_red_limit_bp,
            "hot_red": args.observed_hot_red_limit_bp,
        },
        "application_transitions": [],
        "state0_page_samples": [],
        "corruption_matches": [],
        "periodic": [],
    }
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    stdout_path = out / "stdout.log"
    stderr_path = out / "stderr.log"
    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        process = subprocess.Popen(
            command,
            cwd=exe.parent,
            env=env,
            stdout=stdout,
            stderr=stderr,
            creationflags=creationflags,
        )
        evidence["pid"] = process.pid
        last_pair: tuple[int, int] | None = None
        last_frame = -1
        last_page_sample = -60
        last_periodic = -600
        last_scanned = 0
        deadline = time.monotonic() + args.timeout
        try:
            def server_ready() -> dict[str, Any]:
                code = process.poll()
                if code is not None:
                    raise ProbeError(f"runtime exited before debug server (code {code})")
                return tcp_call(args.port, "frame")

            wait_for("debug server", 20.0, server_ready)
            while process.poll() is None:
                if time.monotonic() >= deadline:
                    raise ProbeError(f"route observation exceeded {args.timeout:.0f}s")
                try:
                    frame = int(tcp_call(args.port, "frame")["frame"])
                    pair = app_pair(args.port)
                except (ConnectionError, OSError, ProbeError):
                    time.sleep(0.02)
                    continue
                last_frame = frame
                if pair != last_pair:
                    event: dict[str, Any] = {
                        "frame": frame,
                        "depth": pair[0],
                        "state": pair[1],
                    }
                    if pair in ((2, 4), (2, 8), (1, 0)):
                        event["gpu"] = safe_call(args.port, "gpu_state")
                        event["cdrom"] = safe_call(args.port, "cdrom_state")
                    evidence["application_transitions"].append(event)
                    last_pair = pair

                if pair == (1, 0) and frame - last_page_sample >= 60:
                    ring = tcp_call(args.port, "display_ring_stats")
                    oldest = int(ring["oldest_frame"])
                    newest = int(ring["newest_frame"])
                    # Consecutive frames are required here: SF3 alternates its
                    # display pages, so a fixed even polling interval can
                    # repeatedly observe only one page and create false
                    # two-page confidence.
                    for page_frame in range(max(oldest, newest - 1), newest + 1):
                        color = safe_call(
                            args.port, "display_ring_color_stats", frame=page_frame
                        )
                        evidence["state0_page_samples"].append(color)
                    last_page_sample = frame

                    scan = tcp_call(
                        args.port,
                        "display_ring_color_scan",
                        min_frame=last_scanned + 1,
                        red_dominant_bp=args.observed_red_limit_bp,
                        hot_red_bp=args.observed_hot_red_limit_bp,
                    )
                    last_scanned = max(last_scanned, int(scan["newest_frame"]))
                    if int(scan["matches"]) > 0 and not evidence["corruption_matches"]:
                        match_frame = int(scan["first_match_frame"])
                        match: dict[str, Any] = {"scan": scan}
                        match["display"] = safe_call(
                            args.port,
                            "display_ring_get",
                            frame=match_frame,
                            path=(out / f"corrupt-frame-{match_frame}.png").as_posix(),
                        )
                        if args.display_ring_aux:
                            match["vram"] = safe_call(
                                args.port,
                                "display_ring_aux",
                                frame=match_frame,
                                path=(out / f"corrupt-frame-{match_frame}-vram.bin").as_posix(),
                            )
                        evidence["corruption_matches"].append(match)

                if frame - last_periodic >= 600:
                    evidence["periodic"].append(
                        {
                            "frame": frame,
                            "depth": pair[0],
                            "state": pair[1],
                            "gpu": safe_call(args.port, "gpu_state"),
                            "spu": safe_call(args.port, "spu_status"),
                            "audio": safe_call(args.port, "audio_stats"),
                            "cdrom": safe_call(args.port, "cdrom_state"),
                            "pad": safe_call(args.port, "pad_status"),
                            "dispatch": safe_call(args.port, "dispatch_stats"),
                        }
                    )
                    last_periodic = frame
                time.sleep(0.02)

            exit_code = process.wait(timeout=5.0)
            stdout.flush()
            stderr.flush()
            stdout_text = stdout_path.read_text(encoding="utf-8", errors="replace")
            completion = f"bounded input sample limit reached ({sample_count})"
            evidence["result"] = {
                "exit_code": exit_code,
                "last_observed_frame": last_frame,
                "bounded_completion": completion in stdout_text,
            }
            if exit_code != 0 or completion not in stdout_text:
                raise ProbeError(
                    f"route did not complete cleanly (exit={exit_code}, marker={completion in stdout_text})"
                )
            (out / "evidence.json").write_text(
                json.dumps(evidence, indent=2) + "\n", encoding="utf-8"
            )
            print(json.dumps({"ok": True, "out": str(out), "frames": last_frame}))
            return 0
        except Exception as exc:
            evidence["failure"] = str(exc)
            (out / "evidence.json").write_text(
                json.dumps(evidence, indent=2) + "\n", encoding="utf-8"
            )
            raise
        finally:
            if process.poll() is None:
                try:
                    tcp_call(args.port, "quit")
                except Exception:
                    pass
                try:
                    process.wait(timeout=5.0)
                except subprocess.TimeoutExpired:
                    process.terminate()
                    process.wait(timeout=5.0)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProbeError as exc:
        print(f"observe_input_route: {exc}", file=sys.stderr)
        raise SystemExit(1)
