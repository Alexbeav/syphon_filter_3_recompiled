#!/usr/bin/env python3
"""Observe the SCUS-94640 cold-boot movie path with an explicit neutral pad.

The runtime uses a hidden SDL/OpenGL window and SDL's dummy audio backend, so
the hardware renderer is exercised without opening a visible window or a
physical sound device. All captures are retail-derived and must stay beneath
an ignored output directory.
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
TITLE_SUBSTATE = 0x8015741C
TITLE_HEAP = 0x8015E5F0


class ProbeError(RuntimeError):
    pass


def call(port: int, command: str, **fields: Any) -> dict[str, Any]:
    request = {"id": 1, "cmd": command, **fields}
    with socket.create_connection(("127.0.0.1", port), timeout=5.0) as sock:
        sock.sendall((json.dumps(request, separators=(",", ":")) + "\n").encode())
        response = bytearray()
        while b"\n" not in response:
            part = sock.recv(65536)
            if not part:
                break
            response.extend(part)
    if not response:
        raise ProbeError(f"empty response to {command}")
    result = json.loads(bytes(response).split(b"\n", 1)[0])
    if not result.get("ok"):
        raise ProbeError(f"{command}: {result}")
    return result


def read_u32(port: int, address: int) -> int:
    result = call(port, "read_ram", addr=f"0x{address:08X}", len=4)
    return int.from_bytes(bytes.fromhex(result["hex"]), "little")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("cue", type=Path)
    parser.add_argument("--project", type=Path, default=Path("lab/sf3/generated/fmv-a"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--port", type=int, default=4391)
    parser.add_argument("--timeout", type=float, default=240.0)
    parser.add_argument("--post-movie-frames", type=int, default=120,
                        help="guest frames to observe after the last decode")
    parser.add_argument("--max-frame", type=int, default=0,
                        help="finish with an observation summary at this guest frame")
    parser.add_argument("--trace-fmv", action="store_true",
                        help="retain bounded MDEC tracing for diagnosis")
    args = parser.parse_args()

    project = args.project.resolve()
    out = args.out.resolve()
    cue = args.cue.absolute()
    exe = project / "build-r1" / "Syphon_Filter_3_Recompiled.exe"
    game = project / "game.toml"
    for path, label in ((cue, "cue"), (exe, "diagnostic executable"), (game, "game.toml")):
        if not path.is_file():
            raise ProbeError(f"missing {label}: {path}")
    if out.exists():
        raise ProbeError(f"output directory must not exist: {out}")
    (out / "memcard").mkdir(parents=True)

    env = os.environ.copy()
    env["SDL_AUDIODRIVER"] = "dummy"
    env["PSX_DEBUG_FMV_QUIET"] = "0" if args.trace_fmv else "1"
    command = [
        str(exe), "--hidden-window", "--no-launcher",
        "--game", str(game), "--disc", str(cue),
        "--memcard-dir", str(out / "memcard"),
        "--debug-port", str(args.port),
    ]
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    samples: list[dict[str, Any]] = []
    captures: list[dict[str, Any]] = []
    last_decode = 0
    last_capture_decode = 0
    last_decode_frame = 0
    first_title_frame: int | None = None
    neutral_armed = False
    deadline = time.monotonic() + args.timeout

    with (out / "stdout.log").open("wb") as stdout, (out / "stderr.log").open("wb") as stderr:
        process = subprocess.Popen(
            command, cwd=exe.parent, env=env, stdout=stdout, stderr=stderr,
            creationflags=creationflags,
        )
        try:
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise ProbeError(f"runtime exited with code {process.returncode}")
                try:
                    frame = call(args.port, "frame")["frame"]
                    if not neutral_armed:
                        # A hidden SDL window must not inherit a key currently
                        # held in another application or a noisy controller.
                        # This is a persistent all-released PAD word, not a
                        # gameplay/state write.
                        call(args.port, "set_input", buttons=0xFFFF)
                        neutral_armed = True
                    fmv = call(args.port, "fmv_state")
                    gpu = call(args.port, "gpu_state")
                    depth = read_u32(args.port, APP_DEPTH)
                    state = read_u32(args.port, APP_STATE)
                except (ConnectionError, OSError, ProbeError):
                    time.sleep(0.05)
                    continue

                decode = int(fmv["mdec_decode_count"])
                if decode != last_decode or not samples:
                    samples.append({
                        "frame": frame, "depth": depth, "state": state,
                        "title_substate": read_u32(args.port, TITLE_SUBSTATE),
                        "title_heap": read_u32(args.port, TITLE_HEAP),
                        "depth24": int(gpu["depth24"]),
                        "mdec_decode_count": decode,
                        "xa_stream_active": int(fmv["xa_stream_active"]),
                        "auto_skip_fmv": int(fmv["auto_skip_fmv"]),
                        "pad1": fmv["pad1"],
                    })
                    last_decode = decode
                    last_decode_frame = frame

                if (depth, state) == (2, 4) and first_title_frame is None:
                    first_title_frame = frame

                capture_stride = 5 if len(captures) < 4 else 100
                if decode >= last_capture_decode + capture_stride and len(captures) < 10:
                    path = out / f"fmv-{len(captures):02d}-f{frame}.png"
                    captures.append(call(args.port, "screenshot_file", path=path.as_posix()))
                    last_capture_decode = decode

                # TITLE is installed behind the opening movie, so reaching
                # state 4 is not movie completion. Wait until MDEC has been
                # idle for two seconds of guest VBlank time and XA has ended.
                movie_complete = (
                    decode > 0
                    and frame >= last_decode_frame + args.post_movie_frames
                    and int(fmv["xa_stream_active"]) == 0
                )
                if args.max_frame and frame >= args.max_frame:
                    summary = {
                        "ok": True,
                        "observation_only": True,
                        "final_frame": frame,
                        "first_title_frame": first_title_frame,
                        "mdec_decode_count": decode,
                        "captures": captures,
                        "samples": samples,
                        "neutral_input": all(row["pad1"] == "0xFFFF" for row in samples),
                        "auto_skip_disabled": all(row["auto_skip_fmv"] == 0 for row in samples),
                        "final_fmv": call(args.port, "fmv_state"),
                        "final_mdec": call(args.port, "mdec_state"),
                        "final_gpu": call(args.port, "gpu_state"),
                        "final_cdrom": call(args.port, "cdrom_state"),
                    }
                    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
                    print(json.dumps({"ok": True, "out": str(out), "captures": len(captures)}))
                    return 0
                if not args.max_frame and (depth, state) == (2, 4) and movie_complete:
                    summary = {
                        "ok": True,
                        "final_frame": frame,
                        "first_title_frame": first_title_frame,
                        "mdec_decode_count": decode,
                        "captures": captures,
                        "samples": samples,
                        "neutral_input": all(row["pad1"] == "0xFFFF" for row in samples),
                        "auto_skip_disabled": all(row["auto_skip_fmv"] == 0 for row in samples),
                        "final_fmv": call(args.port, "fmv_state"),
                        "final_mdec": call(args.port, "mdec_state"),
                        "final_gpu": call(args.port, "gpu_state"),
                        "final_cdrom": call(args.port, "cdrom_state"),
                    }
                    if args.trace_fmv:
                        summary["mdec_trace"] = call(args.port, "mdec_trace", count=256)
                    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
                    print(json.dumps({"ok": True, "out": str(out), "captures": len(captures)}))
                    return 0
                time.sleep(0.04)
            raise ProbeError("timeout before a decoded movie completed into retail TITLE")
        finally:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
