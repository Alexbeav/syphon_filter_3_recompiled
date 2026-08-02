#!/usr/bin/env python3
"""Drive the verified SCUS-94640 Story/Mission 1 path through physical PAD.

This probe never writes guest RAM or invokes a retail callback.  It waits on
retail-owned state and call checkpoints, supplies active-low PAD words through
the runtime's SIO input override, and stores all derived evidence below an
ignored output directory.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
from typing import Any, Callable


APP_DEPTH = 0x80121B84
APP_STATE = 0x80121B88
TITLE_SUBSTATE = 0x8015741C
TITLE_HEAP = 0x8015E5F0

TITLE_PAD_RETURN = 0x801565B4
STATE8_PAD_RETURN = 0x8002A4AC
STATE8_POP_RETURN = 0x8002A67C
MISSION1_PAD_RETURN = 0x80050DA8

PAD_CROSS = 0xBFFF
PAD_UP = 0xFFEF


class ProbeError(RuntimeError):
    pass


def tcp_call(port: int, command: str, **fields: Any) -> dict[str, Any]:
    request = {"id": 1, "cmd": command, **fields}
    with socket.create_connection(("127.0.0.1", port), timeout=5.0) as sock:
        sock.sendall((json.dumps(request, separators=(",", ":")) + "\n").encode())
        chunks = bytearray()
        while b"\n" not in chunks:
            part = sock.recv(65536)
            if not part:
                break
            chunks.extend(part)
    if not chunks:
        raise ProbeError(f"empty response to {command}")
    response = json.loads(bytes(chunks).split(b"\n", 1)[0])
    if not response.get("ok"):
        raise ProbeError(f"{command}: {response}")
    return response


def read_u32(port: int, address: int) -> int:
    reply = tcp_call(port, "read_ram", addr=f"0x{address:08X}", len=4)
    return int.from_bytes(bytes.fromhex(reply["hex"]), "little")


def app_pair(port: int) -> tuple[int, int]:
    return read_u32(port, APP_DEPTH), read_u32(port, APP_STATE)


def latest_trace(port: int, target: int, count: int = 8) -> list[dict[str, Any]]:
    return tcp_call(
        port,
        "fntrace_dump",
        target_lo=f"0x{target:08X}",
        target_hi=f"0x{target + 1:08X}",
        count=count,
    )["entries"]


def wait_for(label: str, timeout: float, predicate: Callable[[], Any]) -> Any:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            value = predicate()
            if value:
                return value
        except (ConnectionError, OSError, ProbeError) as exc:
            last_error = exc
        time.sleep(0.05)
    suffix = f"; last error: {last_error}" if last_error else ""
    raise ProbeError(f"timeout waiting for {label}{suffix}")


def press(port: int, buttons: int, frames: int) -> None:
    tcp_call(port, "press", buttons=buttons, frames=frames)


def bounded_press_until(
    port: int,
    label: str,
    buttons: int,
    predicate: Callable[[], Any],
    attempts: int = 3,
) -> tuple[Any, int]:
    """Retry a physical press only while the retail gate remains unchanged.

    A clean headless pad can begin in analog mode.  The first injected D-pad
    word may therefore be consumed by the coherent analog-to-digital request
    before the next retail poll.  A neutral interval followed by another edge
    is how a physical controller supplies the input; no guest state is edited.
    """
    for attempt in range(1, attempts + 1):
        press(port, buttons, 8)
        try:
            return wait_for(label, 5.0, predicate), attempt
        except ProbeError:
            tcp_call(port, "clear_input")
            time.sleep(0.10)
    raise ProbeError(f"{label} unchanged after {attempts} bounded PAD attempts")


def screenshot(port: int, path: Path) -> dict[str, Any]:
    return tcp_call(port, "screenshot_file", path=path.as_posix())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cue", type=Path, help="user-owned USA SCUS-94640 cue")
    parser.add_argument(
        "--project",
        type=Path,
        default=Path("lab/sf3/generated/run-a"),
        help="generated SF3 project containing game.toml and build-r1",
    )
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--port", type=int, default=4388)
    parser.add_argument("--timeout", type=float, default=120.0)
    args = parser.parse_args()

    # Preserve mapped-drive spelling.  Path.resolve() expands a mapped drive to
    # UNC on Windows, while the current runtime CLI deliberately accepts the
    # user-selected Z: path and its own UNC normalization is a separate concern.
    cue = args.cue.absolute()
    project = args.project.resolve()
    out = args.out.resolve()
    exe = project / "build-r1" / "Syphon_Filter_3_Recompiled.exe"
    game_toml = project / "game.toml"
    for path, label in ((cue, "cue"), (exe, "diagnostic executable"), (game_toml, "game.toml")):
        if not path.is_file():
            raise ProbeError(f"missing {label}: {path}")
    if out.exists():
        raise ProbeError(f"output directory must not exist: {out}")
    (out / "memcard").mkdir(parents=True)

    env = os.environ.copy()
    env["PSX_DEBUG_FMV_QUIET"] = "1"
    env["PSX_FNTRACE_ARM"] = ",".join(
        f"0x{x:08X}"
        for x in (
            0x800FB368,
            0x80029ED8,
            0x80029FB8,
            TITLE_PAD_RETURN,
            STATE8_PAD_RETURN,
            STATE8_POP_RETURN,
            MISSION1_PAD_RETURN,
        )
    )
    command = [
        str(exe),
        "--headless",
        "--no-launcher",
        "--game",
        str(game_toml),
        "--disc",
        str(cue),
        "--memcard-dir",
        str(out / "memcard"),
        "--debug-port",
        str(args.port),
    ]
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    with (out / "stdout.log").open("wb") as stdout, (out / "stderr.log").open("wb") as stderr:
        process = subprocess.Popen(
            command,
            cwd=exe.parent,
            env=env,
            stdout=stdout,
            stderr=stderr,
            creationflags=creationflags,
        )
        evidence: dict[str, Any] = {"pid": process.pid, "port": args.port}
        try:
            def server_ready() -> dict[str, Any]:
                exit_code = process.poll()
                if exit_code is not None:
                    raise RuntimeError(f"runtime exited before debug server (code {exit_code})")
                return tcp_call(args.port, "frame")

            wait_for("debug server", 20.0, server_ready)

            def title_ready() -> dict[str, Any] | None:
                frame = tcp_call(args.port, "frame")["frame"]
                traces = latest_trace(args.port, TITLE_PAD_RETURN, 16)
                ready_calls = [
                    row for row in traces
                    if row["a1"] == "0x00000000" and row["s3"] == "0x00000000"
                ]
                if (
                    frame >= 1000
                    and app_pair(args.port) == (2, 4)
                    and read_u32(args.port, TITLE_SUBSTATE) == 0
                    and read_u32(args.port, TITLE_HEAP) != 0
                    and len(ready_calls) >= 4
                ):
                    return {"frame": frame, "pad_calls": ready_calls[:4]}
                return None

            evidence["title"] = wait_for("stable retail TITLE", args.timeout, title_ready)
            evidence["title"]["screenshot"] = screenshot(args.port, out / "title.png")

            def story_choice_or_later() -> tuple[int, int, int] | None:
                depth, state = app_pair(args.port)
                substate = read_u32(args.port, TITLE_SUBSTATE)
                if state != 4 or substate == 10:
                    return depth, state, substate
                return None

            choice, attempts = bounded_press_until(
                args.port, "retail Story choice", PAD_CROSS, story_choice_or_later
            )
            evidence["story_choice"] = {
                "depth": choice[0], "state": choice[1], "substate": choice[2],
                "pad_attempts": attempts,
            }
            if choice[1] == 4 and choice[2] == 10:
                evidence["story_choice"]["screenshot"] = screenshot(args.port, out / "story-choice.png")

                def story_accepted() -> tuple[int, int, int] | None:
                    depth, state = app_pair(args.port)
                    substate = read_u32(args.port, TITLE_SUBSTATE)
                    if state != 4 or substate != 10:
                        return depth, state, substate
                    return None

                accepted, accept_attempts = bounded_press_until(
                    args.port, "retail New Game acceptance", PAD_CROSS, story_accepted
                )
                evidence["story_choice"]["accepted"] = {
                    "depth": accepted[0], "state": accepted[1], "substate": accepted[2],
                    "pad_attempts": accept_attempts,
                }

            def state8_ready() -> dict[str, Any] | None:
                depth, state = app_pair(args.port)
                traces = latest_trace(args.port, STATE8_PAD_RETURN, 8)
                if (depth, state) == (2, 8) and traces:
                    return {"depth": depth, "state": state, "pad_calls": traces[:4]}
                return None

            evidence["state8"] = wait_for("Mission 1 state 8", args.timeout, state8_ready)
            evidence["state8"]["screenshot"] = screenshot(args.port, out / "state8.png")

            def state8_accepted() -> tuple[int, int] | None:
                pair = app_pair(args.port)
                return pair if pair != (2, 8) else None

            accepted, attempts = bounded_press_until(
                args.port, "state-8 confirmation", PAD_CROSS, state8_accepted
            )
            evidence["state8"]["accepted"] = {
                "depth": accepted[0], "state": accepted[1], "pad_attempts": attempts,
            }

            def state0_ready() -> dict[str, Any] | None:
                if app_pair(args.port) != (1, 0):
                    return None
                pops = latest_trace(args.port, STATE8_POP_RETURN, 4)
                pads = latest_trace(args.port, MISSION1_PAD_RETURN, 8)
                if not pops or not pads:
                    return None
                pop_frame = pops[0]["frame"]
                live = [row for row in pads if row["frame"] >= pop_frame]
                if live:
                    return {"depth": 1, "state": 0, "pop": pops[0], "pad_calls": live[:4]}
                return None

            evidence["state0"] = wait_for("state-0 Mission 1 PAD polling", args.timeout, state0_ready)
            pop_frame = evidence["state0"]["pop"]["frame"]
            wait_for(
                "post-intro control frame",
                args.timeout,
                lambda: tcp_call(args.port, "frame")["frame"] >= pop_frame + 2000,
            )
            evidence["state0"]["before_move"] = screenshot(args.port, out / "state0-before-move.png")
            before_frame = tcp_call(args.port, "frame")["frame"]
            press(args.port, PAD_UP, 16)
            wait_for(
                "movement sample",
                10.0,
                lambda: tcp_call(args.port, "frame")["frame"] >= before_frame + 24,
            )
            evidence["state0"]["after_move"] = screenshot(args.port, out / "state0-after-move.png")

            evidence["final"] = {
                "frame": tcp_call(args.port, "frame"),
                "application": {"depth": app_pair(args.port)[0], "state": app_pair(args.port)[1]},
                "gpu": tcp_call(args.port, "gpu_state"),
                "spu": tcp_call(args.port, "spu_status"),
                "audio": tcp_call(args.port, "audio_stats"),
                "cdrom": tcp_call(args.port, "cdrom_state"),
                "pad": tcp_call(args.port, "pad_status"),
                "overlays": tcp_call(args.port, "overlay_loader_status"),
                "dispatch": tcp_call(args.port, "dispatch_stats"),
            }
            (out / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
            print(json.dumps({"ok": True, "out": str(out), "state": "0/1"}))
            return 0
        except Exception as exc:
            evidence["failure"] = str(exc)
            (out / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
            raise
        finally:
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
        print(f"probe_story: {exc}", file=sys.stderr)
        raise SystemExit(1)
