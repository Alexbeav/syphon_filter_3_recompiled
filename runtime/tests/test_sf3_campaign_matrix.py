#!/usr/bin/env python3
"""Guard the bounded, source-owned SF3 campaign qualification ledger."""

from pathlib import Path
import re


root = Path(__file__).resolve().parents[2]
matrix_path = root / "docs" / "sf3" / "CAMPAIGN_QUALIFICATION.md"
text = matrix_path.read_text(encoding="utf-8")

start = "<!-- campaign-matrix:start -->"
end = "<!-- campaign-matrix:end -->"
if text.count(start) != 1 or text.count(end) != 1:
    raise SystemExit("campaign matrix must have one bounded machine-readable section")
table = text.split(start, 1)[1].split(end, 1)[0]

row_pattern = re.compile(
    r"^\|\s*(\d+)\s*\|\s*([^|]+?)\s*\|\s*`([A-Z0-9]+)`\s*\|"
    r"\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|"
    r"\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|"
    r"\s*([^|]+?)\s*\|$",
    re.MULTILINE,
)
rows = [match.groups() for match in row_pattern.finditer(table)]

missions = [
    (1, "Hotel Fukushima", "TOKYO"),
    (2, "Costa Rican Plantation", "JUNGLE"),
    (3, "C-5 Galaxy Transport", "JUNGLE3"),
    (4, "Pugari Gold Mine", "AFRICA1"),
    (5, "Pugari Complex", "AFRICA2"),
    (6, "Kabul, Afghanistan", "AFGHAN2"),
    (7, "S.S. Lorelei", "LONDON1"),
    (8, "Aztec Ruins", "JUNGLE2"),
    (9, "Waterfront", "LONDON2"),
    (10, "Docks Final Assault", "LONDON3"),
    (11, "Convoy", "AFGHAN1"),
    (12, "The Beast", "AFGHAN3"),
    (13, "Australian Outback", "TRIAGE1"),
    (14, "St. George Australia", "TRIAGE2"),
    (15, "Paradise Ridge", "RIDGE"),
    (16, "Militia Compound", "SNOWCAMP"),
    (17, "Underground Bunker", "MCAVES"),
    (18, "Senate Building", "SENATE"),
    (19, "DC Subway", "SENATE2"),
]
actual = [(int(row[0]), row[1].strip(), row[2]) for row in rows]
if actual != missions:
    raise SystemExit(f"campaign rows do not match the 19-mission retail map: {actual!r}")

allowed = {"pass-2x+human", "pass-human", "entry-human", "open", "n/a"}
for row in rows:
    number = int(row[0])
    for value in row[3:9]:
        status = value.strip().split(maxsplit=1)[0]
        if status not in allowed:
            raise SystemExit(f"mission {number} uses unknown evidence status: {status}")

# Preserve the exact current claim boundary. Later evidence may intentionally
# update this guard in the same reviewed checkpoint as the matrix.
by_number = {int(row[0]): row for row in rows}
if not all(value.strip().startswith("pass-2x+human") for value in by_number[1][3:9]):
    raise SystemExit("Mission 1 must retain complete deterministic and human coverage")
if by_number[2][3].strip() != "pass-2x+human":
    raise SystemExit("Mission 2 entry must retain the qualified Mission 1 handoff")
if not by_number[4][3].strip().startswith("entry-human"):
    raise SystemExit("Mission 4 is currently entry-only human evidence")
if any(not value.strip().startswith("open") for value in by_number[4][4:9]):
    raise SystemExit("Mission 4 gameplay/completion seams must remain open")
for number in range(5, 20):
    if any(not value.strip().startswith("open") for value in by_number[number][3:9]):
        raise SystemExit(f"Mission {number} must remain explicitly unqualified")

required_contract = (
    "Direct mission boot", "two clean processes", "Mission 4 continuation",
    "PSXPAD2", "relative-mouse motion", "SF2 Recomp",
)
missing = [token for token in required_contract if token not in text]
if missing:
    raise SystemExit(f"campaign qualification contract is missing: {missing}")

print("SF3 campaign qualification matrix: OK")
