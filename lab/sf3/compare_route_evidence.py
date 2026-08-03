#!/usr/bin/env python3
"""Compare two passive SF3 route observations at bounded semantic gates."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


TITLE = (2, 4)
STATE8 = (2, 8)
STATE0 = (1, 0)


def transition_pairs(evidence: dict[str, Any]) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    for row in evidence.get("application_transitions", []):
        pair = (int(row["depth"]), int(row["state"]))
        if not result or result[-1] != pair:
            result.append(pair)
    return result


def contains_in_order(values: list[tuple[int, int]], required: tuple[tuple[int, int], ...]) -> bool:
    cursor = 0
    for value in values:
        if cursor < len(required) and value == required[cursor]:
            cursor += 1
    return cursor == len(required)


def following_transition(values: list[tuple[int, int]]) -> tuple[int, int] | None:
    try:
        state0 = values.index(STATE0)
    except ValueError:
        return None
    for value in values[state0 + 1 :]:
        if value != STATE0:
            return value
    return None


def page_origins(evidence: dict[str, Any]) -> set[tuple[int, int]]:
    return {
        (int(row["display_x"]), int(row["display_y"]))
        for row in evidence.get("state0_page_samples", [])
        if row.get("ok") and "display_x" in row and "display_y" in row
    }


def live_state0_snapshots(evidence: dict[str, Any]) -> int:
    required = ("gpu", "spu", "audio", "cdrom", "pad", "dispatch")
    count = 0
    for row in evidence.get("periodic", []):
        if (int(row.get("depth", -1)), int(row.get("state", -1))) != STATE0:
            continue
        if all(isinstance(row.get(name), dict) and row[name].get("ok") for name in required):
            count += 1
    return count


def compare_evidence(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    pairs_a, pairs_b = transition_pairs(a), transition_pairs(b)
    origins_a, origins_b = page_origins(a), page_origins(b)
    following_a, following_b = following_transition(pairs_a), following_transition(pairs_b)

    for label, evidence in (("a", a), ("b", b)):
        result = evidence.get("result", {})
        if int(result.get("exit_code", -1)) != 0 or not result.get("bounded_completion"):
            errors.append(f"run {label} did not consume the complete bounded route")
        pairs = pairs_a if label == "a" else pairs_b
        if not contains_in_order(pairs, (TITLE, STATE8, STATE0)):
            errors.append(f"run {label} did not observe TITLE -> state 8 -> state 0")
        origins = origins_a if label == "a" else origins_b
        if len(origins) < 2:
            errors.append(f"run {label} did not observe two distinct state-0 display origins")
        if evidence.get("corruption_matches"):
            errors.append(f"run {label} matched the known red/checkered corruption signature")
        if live_state0_snapshots(evidence) < 1:
            errors.append(f"run {label} has no complete live state-0 subsystem snapshot")

    if pairs_a != pairs_b:
        errors.append("retail application transition sequences differ")
    if origins_a != origins_b:
        errors.append("state-0 display-origin sets differ")
    if following_a is None or following_b is None:
        errors.append("a retail transition following the first state-0 interval was not observed")
    elif following_a != following_b:
        errors.append("the retail transitions following state 0 differ")

    return {
        "ok": not errors,
        "errors": errors,
        "transition_pairs_a": [list(pair) for pair in pairs_a],
        "transition_pairs_b": [list(pair) for pair in pairs_b],
        "following_transition_a": list(following_a) if following_a else None,
        "following_transition_b": list(following_b) if following_b else None,
        "page_origins_a": [list(origin) for origin in sorted(origins_a)],
        "page_origins_b": [list(origin) for origin in sorted(origins_b)],
        "live_state0_snapshots_a": live_state0_snapshots(a),
        "live_state0_snapshots_b": live_state0_snapshots(b),
        "known_corruption_matches_a": len(a.get("corruption_matches", [])),
        "known_corruption_matches_b": len(b.get("corruption_matches", [])),
        "scope": (
            "bounded semantic/page-origin comparison only; does not prove arbitrary "
            "texture correctness, audio quality, pause/death/checkpoint behavior, or mission completion"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("evidence_a", type=Path)
    parser.add_argument("evidence_b", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    a = json.loads(args.evidence_a.read_text(encoding="utf-8"))
    b = json.loads(args.evidence_b.read_text(encoding="utf-8"))
    report = compare_evidence(a, b)
    rendered = json.dumps(report, indent=2) + "\n"
    if args.out:
        if args.out.exists():
            parser.error(f"refusing to overwrite output: {args.out}")
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
