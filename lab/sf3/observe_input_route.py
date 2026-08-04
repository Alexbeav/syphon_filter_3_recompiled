#!/usr/bin/env python3
"""Observe a captured SCUS-94640 route without supplying or forcing input."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
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
    except (ConnectionError, OSError, ProbeError, ValueError) as exc:
        return {"ok": False, "error": str(exc)}


def parse_frame_range(value: str) -> tuple[int, int]:
    try:
        lo_text, hi_text = value.split(":", 1)
        lo, hi = int(lo_text, 10), int(hi_text, 10)
    except (ValueError, TypeError) as exc:
        raise argparse.ArgumentTypeError("frame range must be START:END") from exc
    if lo < 0 or hi < lo:
        raise argparse.ArgumentTypeError("frame range must satisfy 0 <= START <= END")
    return lo, hi


def parse_address_range(value: str) -> tuple[int, int]:
    try:
        lo_text, hi_text = value.split(":", 1)
        lo, hi = int(lo_text, 0), int(hi_text, 0)
    except (ValueError, TypeError) as exc:
        raise argparse.ArgumentTypeError("address range must be LO:HI") from exc
    if not 0 <= lo < hi <= 0x1_0000_0000:
        raise argparse.ArgumentTypeError("address range must satisfy 0 <= LO < HI <= 2^32")
    return lo, hi


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cue", type=Path, help="user-owned USA SCUS-94640 cue")
    parser.add_argument("route", type=Path, help="captured PSXPAD2 input route")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument(
        "--game-config", default="game.toml",
        help="project-relative game configuration (default: game.toml)",
    )
    parser.add_argument(
        "--executable",
        type=Path,
        help="explicit diagnostic Release executable (required when build names are ambiguous)",
    )
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--port", type=int, default=4388)
    parser.add_argument("--timeout", type=float, default=7200.0)
    parser.add_argument("--renderer", choices=("software", "opengl"), default="opengl")
    parser.add_argument(
        "--memcard-source",
        type=Path,
        help="copy an existing card directory into the isolated replay directory",
    )
    parser.add_argument("--display-ring-aux", action="store_true")
    parser.add_argument(
        "--fn-entry-tail-count",
        type=int,
        default=0,
        help="sample this many entries from an env-filtered function-entry ring",
    )
    parser.add_argument(
        "--wtrace-range",
        type=parse_address_range,
        action="append",
        default=[],
        metavar="LO:HI",
        help="arm a focused guest-write trace range after the debug server starts",
    )
    parser.add_argument(
        "--cyc-watch-pc",
        type=lambda value: int(value, 0),
        help="arm the diagnostic block-entry register/cycle watch at this guest PC",
    )
    parser.add_argument(
        "--cyc-watch-count",
        type=int,
        default=1024,
        help="maximum diagnostic block-entry watch hits (default: 1024)",
    )
    parser.add_argument(
        "--widescreen-census", action="store_true",
        help="periodically dump the passive GPU census during state-0 gameplay",
    )
    parser.add_argument(
        "--stop-after",
        type=int,
        help="stop after this many route samples instead of consuming the full route",
    )
    parser.add_argument(
        "--capture-frame",
        type=int,
        action="append",
        default=[],
        help="dump an exact authoritative display-ring frame (repeatable)",
    )
    parser.add_argument(
        "--capture-frame-range",
        type=parse_frame_range,
        action="append",
        default=[],
        metavar="START:END",
        help="attempt every authoritative display-ring frame in an inclusive range",
    )
    parser.add_argument(
        "--capture-frame-step",
        type=int,
        default=1,
        help="sample inclusive capture ranges at this positive frame interval",
    )
    parser.add_argument("--observed-red-limit-bp", type=int, default=1500)
    parser.add_argument("--observed-hot-red-limit-bp", type=int, default=500)
    parser.add_argument(
        "--require-state",
        type=int,
        action="append",
        default=[],
        help="require an observed retail application state (repeatable)",
    )
    parser.add_argument(
        "--require-state0-samples",
        type=int,
        default=0,
        help="require at least this many state-0 display-page samples",
    )
    args = parser.parse_args()
    for value, label in (
        (args.observed_red_limit_bp, "--observed-red-limit-bp"),
        (args.observed_hot_red_limit_bp, "--observed-hot-red-limit-bp"),
    ):
        if not 0 <= value <= 10000:
            parser.error(f"{label} must be between 0 and 10000")
    if args.require_state0_samples < 0:
        parser.error("--require-state0-samples must be non-negative")
    if not 0 <= args.fn_entry_tail_count <= 256:
        parser.error("--fn-entry-tail-count must be between 0 and 256")
    if not 1 <= args.cyc_watch_count <= 1024:
        parser.error("--cyc-watch-count must be between 1 and 1024")

    cue = args.cue.absolute()
    route = args.route.resolve()
    project = args.project.resolve()
    out = args.out.resolve()
    memcard_source = args.memcard_source.resolve() if args.memcard_source else None
    if args.executable:
        exe = args.executable.resolve()
    else:
        candidates = [
            path
            for build_name in ("build-diagnostic", "build-r1")
            for path in (project / build_name).glob("*_Recompiled.exe")
        ]
        if len(candidates) != 1:
            raise ProbeError(
                "expected exactly one diagnostic Release executable; "
                "use --executable to select it explicitly"
            )
        exe = candidates[0]
    game_relative = Path(args.game_config)
    if game_relative.is_absolute() or ".." in game_relative.parts:
        parser.error("--game-config must stay within the generated project")
    game_toml = project / game_relative
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
    if memcard_source is not None and not memcard_source.is_dir():
        raise ProbeError(f"missing memory-card source directory: {memcard_source}")
    (out / "memcard").mkdir(parents=True)
    if memcard_source is not None:
        for card in memcard_source.iterdir():
            if card.is_file():
                shutil.copy2(card, out / "memcard" / card.name)
    sample_count = route_sample_count(route)
    stop_after = args.stop_after if args.stop_after is not None else sample_count
    if not 1 <= stop_after <= sample_count:
        parser.error("--stop-after must be between 1 and the route sample count")
    capture_frame_set = set(args.capture_frame)
    if args.capture_frame_step < 1:
        parser.error("--capture-frame-step must be positive")
    for lo, hi in args.capture_frame_range:
        capture_frame_set.update(range(lo, hi + 1, args.capture_frame_step))
    capture_frames = sorted(capture_frame_set)
    if any(frame < 0 or frame > stop_after for frame in capture_frames):
        parser.error("--capture-frame must be between 0 and --stop-after")

    env = os.environ.copy()
    env["SDL_AUDIODRIVER"] = "dummy"
    env["PSX_DEBUG_FMV_QUIET"] = "1"
    env["PSX_INPUT_REPLAY"] = str(route)
    env.pop("PSX_INPUT_RECORD", None)
    env["PSX_INPUT_STOP_AFTER"] = str(stop_after)
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
        "stop_after": stop_after,
        "capture_frames_requested": capture_frames,
        "capture_frames": [],
        "memcard_source": str(memcard_source) if memcard_source else None,
        "display_ring_aux": args.display_ring_aux,
        "observed_corruption_limits_bp": {
            "red_dominant": args.observed_red_limit_bp,
            "hot_red": args.observed_hot_red_limit_bp,
        },
        "application_transitions": [],
        "state0_page_samples": [],
        "corruption_matches": [],
        "periodic": [],
        "widescreen_census": [],
        "fn_entry_samples": [],
        "cyc_watch_samples": [],
        "cd_dma_samples": [],
        "cdrom_command_samples": [],
        "dma_cdrom_history_samples": [],
        "wtrace_ranges": [
            {"lo": f"0x{lo:08X}", "hi": f"0x{hi:08X}"}
            for lo, hi in args.wtrace_range
        ],
        "requirements": {
            "states": args.require_state,
            "state0_samples": args.require_state0_samples,
            "reject_freeze_dump": True,
        },
    }
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    stdout_path = out / "stdout.log"
    stderr_path = out / "stderr.log"
    with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
        process = subprocess.Popen(
            command,
            cwd=out,
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
        last_cyc_watch_sample = -60
        last_cd_dma_sample = -60
        last_cdrom_lifecycle_sample = -60
        last_scanned = 0
        last_census_frame = -60
        pending_capture_frames = set(capture_frames)
        deadline = time.monotonic() + args.timeout
        try:
            def server_ready() -> dict[str, Any]:
                code = process.poll()
                if code is not None:
                    raise ProbeError(f"runtime exited before debug server (code {code})")
                return tcp_call(args.port, "frame")

            wait_for("debug server", 20.0, server_ready)
            if args.wtrace_range:
                safe_call(args.port, "wtrace_disarm_all")
                for lo, hi in args.wtrace_range:
                    response = safe_call(
                        args.port,
                        "wtrace_arm",
                        lo=f"0x{lo:08X}",
                        hi=f"0x{hi:08X}",
                    )
                    if not response.get("ok"):
                        raise ProbeError(
                            f"cannot arm write trace 0x{lo:08X}:0x{hi:08X}: {response}"
                        )
            if args.cyc_watch_pc is not None:
                response = safe_call(
                    args.port,
                    "cyc_watch",
                    pc=f"0x{args.cyc_watch_pc:08X}",
                    n=args.cyc_watch_count,
                )
                if not response.get("ok"):
                    raise ProbeError(f"cannot arm cycle/register watch: {response}")
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
                if pending_capture_frames:
                    ring = safe_call(args.port, "display_ring_stats")
                    if ring.get("ok"):
                        oldest = int(ring["oldest_frame"])
                        newest = int(ring["newest_frame"])
                        ready = sorted(
                            target
                            for target in pending_capture_frames
                            if oldest <= target <= newest
                        )
                        for target in ready:
                            capture = safe_call(
                                args.port,
                                "display_ring_get",
                                frame=target,
                                path=(out / f"display-frame-{target}.png").as_posix(),
                            )
                            capture["gp0"] = safe_call(
                                args.port,
                                "gpu_frame_dump",
                                frame=target,
                                count=8192,
                            )
                            if args.display_ring_aux:
                                capture["vram"] = safe_call(
                                    args.port,
                                    "display_ring_aux",
                                    frame=target,
                                    path=(out / f"display-frame-{target}-vram.bin").as_posix(),
                                )
                            evidence["capture_frames"].append(capture)
                            pending_capture_frames.remove(target)
                if pair != last_pair:
                    event: dict[str, Any] = {
                        "frame": frame,
                        "depth": pair[0],
                        "state": pair[1],
                    }
                    if pair in ((2, 4), (2, 8), (1, 0)):
                        event["gpu"] = safe_call(args.port, "gpu_state")
                        event["cdrom"] = safe_call(args.port, "cdrom_state")
                        event["fmv"] = safe_call(args.port, "fmv_state")
                        event["mdec"] = safe_call(args.port, "mdec_state")
                        event["irq"] = safe_call(args.port, "irq_state")
                        event["imask_trace"] = safe_call(
                            args.port, "imask_trace", count=16
                        )
                        event["dispatch"] = safe_call(args.port, "dispatch_stats")
                        event["overlay"] = safe_call(
                            args.port, "overlay_loader_status"
                        )
                        event["dirty_ram"] = safe_call(args.port, "dirty_ram_stats")
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

                    if args.fn_entry_tail_count:
                        evidence["fn_entry_samples"].append(
                            {
                                "frame": frame,
                                "trace": safe_call(
                                    args.port,
                                    "fn_entry_tail",
                                    count=args.fn_entry_tail_count,
                                ),
                            }
                        )

                if (args.widescreen_census and pair == (1, 0) and
                        frame - last_census_frame >= 60):
                    census_path = (out / "widescreen-census.csv").resolve()
                    evidence["widescreen_census"].append(
                        safe_call(args.port, "ws_census", start=0, end=frame,
                                  out=str(census_path))
                    )
                    last_census_frame = frame

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
                            "cd_dma": safe_call(args.port, "cd_read_log", tail=128),
                            "fmv": safe_call(args.port, "fmv_state"),
                            "mdec": safe_call(args.port, "mdec_state"),
                            "irq": safe_call(args.port, "irq_state"),
                            "imask_trace": safe_call(
                                args.port, "imask_trace", count=16
                            ),
                            "pad": safe_call(args.port, "pad_status"),
                            "dispatch": safe_call(args.port, "dispatch_stats"),
                            "overlay": safe_call(
                                args.port, "overlay_loader_status"
                            ),
                            "dirty_ram": safe_call(args.port, "dirty_ram_stats"),
                            "wtrace": (
                                safe_call(args.port, "wtrace_dump", count=2048, newest=1)
                                if args.wtrace_range else None
                            ),
                        }
                    )
                    last_periodic = frame
                if (args.cyc_watch_pc is not None and
                        frame - last_cyc_watch_sample >= 60):
                    evidence["cyc_watch_samples"].append(
                        {"frame": frame, "trace": safe_call(args.port, "cyc_watch_dump")}
                    )
                    last_cyc_watch_sample = frame
                if frame - last_cd_dma_sample >= 60:
                    evidence["cd_dma_samples"].append(
                        {"frame": frame, "trace": safe_call(args.port, "cd_read_log", tail=128)}
                    )
                    last_cd_dma_sample = frame
                if frame - last_cdrom_lifecycle_sample >= 60:
                    evidence["cdrom_command_samples"].append(
                        {
                            "frame": frame,
                            "trace": safe_call(
                                args.port, "cdrom_command_history", count=256
                            ),
                        }
                    )
                    evidence["dma_cdrom_history_samples"].append(
                        {
                            "frame": frame,
                            "trace": safe_call(
                                args.port,
                                "dma_cdrom_history",
                                count=512,
                                newest=1,
                            ),
                        }
                    )
                    last_cdrom_lifecycle_sample = frame
                time.sleep(0.02)

            exit_code = process.wait(timeout=5.0)
            stdout.flush()
            stderr.flush()
            stdout_text = stdout_path.read_text(encoding="utf-8", errors="replace")
            completion = f"bounded input sample limit reached ({stop_after})"
            evidence["result"] = {
                "exit_code": exit_code,
                "last_observed_frame": last_frame,
                "bounded_completion": completion in stdout_text,
                "missing_capture_frames": sorted(pending_capture_frames),
            }
            observed_states = {
                int(event["state"])
                for event in evidence["application_transitions"]
            }
            missing_states = sorted(set(args.require_state) - observed_states)
            freeze_dumps: list[Path] = []
            ignored_startup_dumps: list[Path] = []
            for path in sorted(out.glob("psx_freeze_dump_*.json")):
                try:
                    dump = json.loads(path.read_text(encoding="utf-8"))
                    dump_frame = int(dump.get("frame_count", 0))
                except (OSError, ValueError, TypeError, json.JSONDecodeError):
                    freeze_dumps.append(path)
                    continue
                if dump_frame >= 60:
                    freeze_dumps.append(path)
                else:
                    ignored_startup_dumps.append(path)

            semantic_stall = False
            if args.require_state and len(evidence["periodic"]) >= 3:
                tail = evidence["periodic"][-3:]
                dirty = [
                    item.get("dirty_ram", {}).get("insns_run") for item in tail
                ]
                static = [
                    item.get("dispatch", {}).get("static_hits") for item in tail
                ]
                frame_span = int(tail[-1]["frame"]) - int(tail[0]["frame"])
                semantic_stall = (
                    int(tail[-1].get("depth", -1)) == 0 and
                    frame_span >= 1200 and
                    None not in dirty and len(set(dirty)) == 1 and
                    None not in static and len(set(static)) == 1
                )
            evidence["result"]["missing_required_states"] = missing_states
            evidence["result"]["state0_page_sample_count"] = len(
                evidence["state0_page_samples"]
            )
            evidence["result"]["freeze_dumps"] = [
                path.name for path in freeze_dumps
            ]
            evidence["result"]["ignored_startup_freeze_dumps"] = [
                path.name for path in ignored_startup_dumps
            ]
            evidence["result"]["semantic_stall"] = semantic_stall
            if (exit_code != 0 or completion not in stdout_text or
                    pending_capture_frames or missing_states or freeze_dumps or
                    semantic_stall or
                    len(evidence["state0_page_samples"]) <
                    args.require_state0_samples):
                raise ProbeError(
                    "route did not complete cleanly "
                    f"(exit={exit_code}, marker={completion in stdout_text}, "
                    f"missing_frames={sorted(pending_capture_frames)}, "
                    f"missing_states={missing_states}, "
                    f"state0_samples={len(evidence['state0_page_samples'])}, "
                    f"freeze_dumps={[path.name for path in freeze_dumps]}, "
                    f"semantic_stall={semantic_stall})"
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
