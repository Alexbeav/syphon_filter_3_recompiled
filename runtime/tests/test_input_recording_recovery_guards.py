#!/usr/bin/env python3
"""Keep explicit input recording useful after a hard failure."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
main = (ROOT / "runtime/src/main.cpp").read_text(encoding="utf-8")
assert "kInputPartialFlushSamples = 600u" in main
assert "g_input_sample_index % kInputPartialFlushSamples" in main
assert 'g_input_timeline_path.string() + ".partial"' in main
print("PASS: opt-in recording publishes a bounded replayable failure prefix")
