#!/usr/bin/env python3
"""Regression for bounded two-run SF3 route evidence classification."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


root = Path(__file__).resolve().parents[2]
script = root / "lab" / "sf3" / "compare_route_evidence.py"
spec = spec_from_file_location("compare_route_evidence", script)
assert spec and spec.loader
module = module_from_spec(spec)
spec.loader.exec_module(module)


def evidence() -> dict:
    subsystem = {name: {"ok": True} for name in (
        "gpu", "spu", "audio", "cdrom", "pad", "dispatch"
    )}
    return {
        "result": {"exit_code": 0, "bounded_completion": True},
        "application_transitions": [
            {"depth": 0, "state": 0},
            {"depth": 2, "state": 4},
            {"depth": 2, "state": 8},
            {"depth": 1, "state": 0},
            {"depth": 2, "state": 5},
        ],
        "state0_page_samples": [
            {"ok": True, "display_x": 0, "display_y": 0},
            {"ok": True, "display_x": 0, "display_y": 240},
        ],
        "corruption_matches": [],
        "periodic": [{"depth": 1, "state": 0, **subsystem}],
    }


a, b = evidence(), evidence()
assert module.compare_evidence(a, b)["ok"]

b["corruption_matches"] = [{"scan": {"first_match_frame": 123}}]
report = module.compare_evidence(a, b)
assert not report["ok"]
assert any("red/checkered" in error for error in report["errors"])

b = evidence()
b["state0_page_samples"] = b["state0_page_samples"][:1]
report = module.compare_evidence(a, b)
assert not report["ok"]
assert any("two distinct" in error for error in report["errors"])

b = evidence()
b["application_transitions"].pop()
report = module.compare_evidence(a, b)
assert not report["ok"]
assert any("following" in error for error in report["errors"])
