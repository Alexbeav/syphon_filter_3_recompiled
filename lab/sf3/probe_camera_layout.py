#!/usr/bin/env python3
"""Read-only, bounded SCUS-94640 camera-layout probe.

Consumes a previously accepted PAD route in a hidden/dummy-audio diagnostic
runtime. It never writes guest RAM, invokes a retail callback or supplies new
input. Pointer candidates are derived from the live argument of the independently
mapped retail routine and retained as evidence rather than assumed from SF2.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import socket
import subprocess
import time
from typing import Any


APP_DEPTH = 0x80121B84
APP_STATE = 0x80121B88
CAMERA_ROUTINE = 0x80053954


class ProbeError(RuntimeError):
    pass


def call(port: int, command: str, **fields: Any) -> dict[str, Any]:
    request = {"id": 1, "cmd": command, **fields}
    with socket.create_connection(("127.0.0.1", port), timeout=5.0) as sock:
        sock.sendall((json.dumps(request, separators=(",", ":")) + "\n").encode())
        data = bytearray()
        while b"\n" not in data:
            block = sock.recv(65536)
            if not block:
                break
            data.extend(block)
    if not data:
        raise ProbeError(f"empty response to {command}")
    reply = json.loads(bytes(data).split(b"\n", 1)[0])
    if not reply.get("ok"):
        raise ProbeError(f"{command}: {reply}")
    return reply


def call_streamed_json(port: int, command: str, **fields: Any) -> dict[str, Any]:
    """Read debug commands whose one JSON reply is streamed over many lines."""
    request = {"id": 1, "cmd": command, **fields}
    with socket.create_connection(("127.0.0.1", port), timeout=5.0) as sock:
        sock.sendall((json.dumps(request, separators=(",", ":")) + "\n").encode())
        sock.settimeout(5.0)
        data = bytearray()
        while b"]}\n" not in data:
            block = sock.recv(65536)
            if not block:
                break
            data.extend(block)
    reply = json.loads(b"".join(bytes(data).splitlines()))
    if not reply.get("ok"):
        raise ProbeError(f"{command}: {reply}")
    return reply


def read(port: int, address: int, length: int) -> bytes:
    reply = call(port, "read_ram", addr=f"0x{address:08X}", len=length)
    return bytes.fromhex(reply["hex"])


def u32(port: int, address: int) -> int:
    return int.from_bytes(read(port, address, 4), "little")


def pointer(value: int) -> bool:
    return value != 0 and (value & 0x1FFFFFFF) < 0x00200000


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cue", type=Path)
    parser.add_argument("route", type=Path)
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument(
        "--exe-relative", type=Path,
        default=Path("build-r1/Syphon_Filter_3_Recompiled.exe"),
    )
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--port", type=int, default=4391)
    parser.add_argument("--stop-after", type=int, default=3000)
    parser.add_argument("--timeout", type=float, default=300.0)
    args = parser.parse_args()

    project = args.project.resolve()
    exe = project / args.exe_relative
    game = project / "game.toml"
    # Preserve mapped-drive spelling. Path.resolve() can turn Z: into a UNC
    # path that a separately launched retail runtime cannot open.
    cue = args.cue.absolute()
    route = args.route.resolve()
    out = args.out.resolve()
    for path in (exe, game, cue, route):
        if not path.is_file():
            raise ProbeError(f"missing required input: {path}")
    if out.exists():
        raise ProbeError(f"output must not already exist: {out}")
    (out / "memcard").mkdir(parents=True)

    env = os.environ.copy()
    env["SDL_AUDIODRIVER"] = "dummy"
    env["PSX_DEBUG_FMV_QUIET"] = "1"
    env["PSX_INPUT_REPLAY"] = str(route)
    env["PSX_INPUT_STOP_AFTER"] = str(args.stop_after)
    env.pop("PSX_INPUT_RECORD", None)
    command = [
        str(exe), "--hidden-window", "--no-launcher", "--renderer", "opengl",
        "--game", str(game), "--disc", str(cue),
        "--memcard-dir", str(out / "memcard"), "--debug-port", str(args.port),
    ]
    evidence: dict[str, Any] = {
        "camera_routine": f"0x{CAMERA_ROUTINE:08X}",
        "stop_after": args.stop_after,
        "reads_only": True,
    }
    deadline = time.monotonic() + args.timeout
    with (out / "stdout.log").open("wb") as stdout, (out / "stderr.log").open("wb") as stderr:
        process = subprocess.Popen(
            command, cwd=exe.parent, env=env, stdout=stdout, stderr=stderr,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
        try:
            state0_frame = None
            entries: list[dict[str, Any]] = []
            tracing_armed = False
            last_frame = -1
            last_pair = None
            transitions = []
            ownership_samples = []
            last_ownership = None
            while time.monotonic() < deadline and process.poll() is None:
                try:
                    frame = int(call(args.port, "frame")["frame"])
                    last_frame = frame
                    if not tracing_armed:
                        call(
                            args.port, "fn_filter",
                            lo=f"0x{CAMERA_ROUTINE:08X}",
                            hi=f"0x{CAMERA_ROUTINE + 1:08X}",
                        )
                        call(args.port, "fn_clear")
                        call(args.port, "cyc_watch", pc="0x800549C4", n=32)
                        tracing_armed = True
                    depth, state = u32(args.port, APP_DEPTH), u32(args.port, APP_STATE)
                    pair = (depth, state)
                    if pair != last_pair:
                        transitions.append({"frame": frame, "depth": depth, "state": state})
                        last_pair = pair
                    if frame >= 2000 and depth == 1 and state == 0:
                        dump = call(
                            args.port, "fn_entry_dump",
                            addr_lo=f"0x{CAMERA_ROUTINE:08X}",
                            addr_hi=f"0x{CAMERA_ROUTINE + 1:08X}", count=32,
                        )
                        entries = dump["entries"]
                        if entries:
                            player_now = int(entries[-1]["a0"], 16)
                            state_now = u32(args.port, player_now + 0x20)
                            wrapper_now = u32(args.port, state_now + 0xF8) if pointer(state_now) else 0
                            owner_now = u32(args.port, wrapper_now + 0xDC) if pointer(wrapper_now) else 0
                            ownership = (player_now, owner_now)
                            if ownership != last_ownership:
                                ownership_samples.append({
                                    "frame": frame,
                                    "player": f"0x{player_now:08X}",
                                    "owner": f"0x{owner_now:08X}",
                                    "matches": player_now == owner_now,
                                })
                                last_ownership = ownership
                            if owner_now == player_now:
                                state0_frame = frame
                                break
                except (OSError, ProbeError, KeyError, ValueError):
                    pass
                time.sleep(0.02)
            if state0_frame is None:
                evidence.update({
                    "last_frame": last_frame,
                    "application_transitions": transitions,
                })
                (out / "evidence.json").write_text(
                    json.dumps(evidence, indent=2) + "\n", encoding="utf-8"
                )
                if process.poll() is not None:
                    stdout.flush()
                    tail = (out / "stdout.log").read_text(
                        encoding="utf-8", errors="replace"
                    )[-800:]
                    raise ProbeError(
                        f"runtime exited before evidence (code {process.returncode}): {tail}"
                    )
                raise ProbeError("no live camera-routine entry observed in state 0")

            players = sorted({int(entry["a0"], 16) for entry in entries})
            layouts = []
            for player in players:
                state_ptr = u32(args.port, player + 0x20) if pointer(player) else 0
                controller = u32(args.port, state_ptr + 0xF4) if pointer(state_ptr) else 0
                wrapper = u32(args.port, state_ptr + 0xF8) if pointer(state_ptr) else 0
                base = u32(args.port, wrapper + 0xA4) if pointer(wrapper) else 0
                owner_dc = u32(args.port, wrapper + 0xDC) if pointer(wrapper) else 0
                layouts.append({
                    "player": f"0x{player:08X}",
                    "player_state": f"0x{state_ptr:08X}",
                    "controller_f4": f"0x{controller:08X}",
                    "wrapper_f8": f"0x{wrapper:08X}",
                    "base_a4": f"0x{base:08X}",
                    "owner_dc": f"0x{owner_dc:08X}",
                    "owner_dc_matches_player": owner_dc == player,
                    "wrapper_words_c0_f0": read(args.port, wrapper + 0xC0, 0x34).hex() if pointer(wrapper) else None,
                    "base_words_8d0_930": read(args.port, base + 0x8D0, 0x64).hex() if pointer(base) else None,
                    "pitch_8e8": u32(args.port, base + 0x8E8) if pointer(base) else None,
                    "pitch_918": u32(args.port, base + 0x918) if pointer(base) else None,
                })
            evidence.update({
                "state0_frame": state0_frame,
                "application_transitions": transitions,
                "ownership_samples": ownership_samples,
                "function_entries": entries,
                "facing_site_hits": call_streamed_json(args.port, "cyc_watch_dump"),
                "layouts": layouts,
            })

            while time.monotonic() < deadline and process.poll() is None:
                time.sleep(0.05)
            if process.poll() is None:
                raise ProbeError("bounded route did not terminate")
            stdout.flush()
            marker = f"bounded input sample limit reached ({args.stop_after})"
            stdout_text = (out / "stdout.log").read_text(encoding="utf-8", errors="replace")
            evidence["result"] = {
                "exit_code": process.returncode,
                "bounded_completion": marker in stdout_text,
            }
            if process.returncode != 0 or marker not in stdout_text:
                raise ProbeError(f"unclean bounded completion: {evidence['result']}")
            (out / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
            print(json.dumps({"ok": True, "out": str(out), "state0_frame": state0_frame}))
            return 0
        finally:
            if process.poll() is None:
                try:
                    call(args.port, "quit")
                except Exception:
                    process.terminate()
                process.wait(timeout=10)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ProbeError as exc:
        print(f"probe_camera_layout: {exc}", file=os.sys.stderr)
        raise SystemExit(1)
