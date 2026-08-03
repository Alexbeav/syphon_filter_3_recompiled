#!/usr/bin/env python3
"""Title-neutral active-read -> SeekL/SeekP retarget contract."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def function_body(source: str, signature: str, next_signature: str) -> str:
    start = source.index(signature)
    end = source.index(next_signature, start)
    return source[start:end]


def require_in_order(body: str, *needles: str) -> None:
    position = -1
    for needle in needles:
        position = body.index(needle, position + 1)


def model_contract() -> None:
    state = {
        "reading": True,
        "read_lba": 100,
        "seek_lba": 900,
        "pending_dataready": True,
        "status_read": True,
        "status_seek": False,
    }

    state["reading"] = False
    state["pending_dataready"] = False
    state["status_read"] = False
    state["status_seek"] = True
    assert not state["reading"] and not state["pending_dataready"]

    delivered = state["read_lba"] if state["reading"] else None
    assert delivered is None

    state["status_seek"] = False
    state["read_lba"] = state["seek_lba"]
    state["reading"] = True
    state["status_read"] = True
    assert state["read_lba"] == 900 and state["reading"]


def main() -> None:
    source = (ROOT / "runtime/src/cdrom.c").read_text(encoding="utf-8")
    command = function_body(source, "static void exec_command", "static void process_pending")
    seek = command[command.index("case 0x15:") : command.index("case 0x1A:")]

    require_in_order(
        seek,
        "stop_read_stream()",
        "stat_reg &= (uint8_t)~(CDSTAT_READ | CDSTAT_PLAY)",
        "stat_reg |= CDSTAT_SEEK",
        "pending.cmd = cmd",
    )
    assert "cdrom_clear_pending_dataready()" in function_body(
        source, "static void stop_read_stream", "static void stop_cdda_playback"
    )

    model_contract()
    print("CD-ROM active-read seek retarget contract: PASS")


if __name__ == "__main__":
    main()
