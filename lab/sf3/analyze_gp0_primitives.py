#!/usr/bin/env python3
"""Bounded classifier for malformed PS1 polygon packets in route evidence."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


POLYGONS = {
    0x20: (4, (1, 2, 3)),
    0x24: (7, (1, 3, 5)),
    0x28: (5, (1, 2, 3, 4)),
    0x2C: (9, (1, 3, 5, 7)),
    0x30: (6, (1, 3, 5)),
    0x34: (9, (1, 4, 7)),
    0x38: (8, (1, 3, 5, 7)),
    0x3C: (12, (1, 4, 7, 10)),
}


def signed16(value: int) -> int:
    value &= 0xFFFF
    return value - 0x10000 if value & 0x8000 else value


def parse_word(value: str | int) -> int:
    return int(value, 0) if isinstance(value, str) else int(value)


def edge_oversize(a: tuple[int, int], b: tuple[int, int]) -> bool:
    return abs(a[0] - b[0]) > 1023 or abs(a[1] - b[1]) > 511


def polygon_oversize(vertices: list[tuple[int, int]]) -> bool:
    edges = ((0, 1), (1, 2), (2, 0))
    if len(vertices) == 4:
        edges = ((0, 1), (1, 3), (3, 2), (2, 0))
    return any(edge_oversize(vertices[a], vertices[b]) for a, b in edges)


def classify_entry(entry: dict[str, Any]) -> dict[str, Any] | None:
    opcode = int(str(entry["op"]), 0)
    family = opcode & 0xFC
    spec = POLYGONS.get(family)
    if spec is None:
        return None
    expected, xy_indices = spec
    words = [parse_word(word) for word in entry.get("w", [])]
    declared = int(entry.get("n", len(words)))
    result: dict[str, Any] = {
        "seq": int(entry.get("seq", 0)),
        "op": f"0x{opcode:02X}",
        "declared_words": declared,
        "expected_words": expected,
        "src": entry.get("src"),
        "ot": entry.get("ot"),
        "pc": entry.get("pc"),
        "func": entry.get("func"),
        "ra": entry.get("ra"),
        "reasons": [],
    }
    if declared != expected or len(words) < expected:
        result["reasons"].append("packet_length")
        return result
    vertices = [
        (signed16(words[index]), signed16(words[index] >> 16))
        for index in xy_indices
    ]
    result["vertices"] = vertices
    span_x = max(x for x, _ in vertices) - min(x for x, _ in vertices)
    span_y = max(y for _, y in vertices) - min(y for _, y in vertices)
    result["span_x"] = span_x
    result["span_y"] = span_y
    if span_x > 512:
        result["reasons"].append("wide_span")
    if span_y > 384:
        result["reasons"].append("tall_span")
    if polygon_oversize(vertices):
        result["reasons"].append("hardware_oversize")
        if len(vertices) == 4:
            tri_a = polygon_oversize(vertices[:3])
            tri_b = polygon_oversize([vertices[2], vertices[1], vertices[3]])
            if tri_a != tri_b:
                result["reasons"].append("partial_quad_risk")
    if any(abs(x) > 1024 or abs(y) > 1024 for x, y in vertices):
        result["reasons"].append("coordinate_range")
    return result if result["reasons"] else None


def analyze(evidence: dict[str, Any]) -> dict[str, Any]:
    frames = []
    for capture in evidence.get("capture_frames", []):
        gp0 = capture.get("gp0", {})
        flagged = [
            finding
            for entry in gp0.get("entries", [])
            if (finding := classify_entry(entry)) is not None
        ]
        frames.append({
            "frame": int(gp0.get("frame", capture.get("frame", -1))),
            "packets": int(gp0.get("count", 0)),
            "flagged": flagged,
        })
    return {
        "frames": frames,
        "flagged_total": sum(len(frame["flagged"]) for frame in frames),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = analyze(json.loads(args.evidence.read_text(encoding="utf-8")))
    encoded = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8", newline="\n")
    else:
        print(encoded, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
