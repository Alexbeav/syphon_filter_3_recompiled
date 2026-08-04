from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


path = Path(__file__).parents[2] / "lab/sf3/analyze_gp0_primitives.py"
spec = spec_from_file_location("sf3_gp0", path)
module = module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(module)


def word(x, y):
    return f"0x{((y & 0xFFFF) << 16) | (x & 0xFFFF):08X}"


normal = {
    "op": "0x24", "n": 7, "seq": 1,
    "w": ["0x24000000", word(10, 20), "0", word(40, 25), "0", word(20, 60), "0"],
}
assert module.classify_entry(normal) is None

exploded = dict(normal)
exploded["seq"] = 2
exploded["w"] = list(normal["w"])
exploded["w"][3] = word(900, 25)
finding = module.classify_entry(exploded)
assert finding and "wide_span" in finding["reasons"]

malformed = dict(normal)
malformed["n"] = 9
finding = module.classify_entry(malformed)
assert finding and finding["reasons"] == ["packet_length"]

signed = dict(normal)
signed["w"] = list(normal["w"])
signed["w"][1] = word(-40, -20)
assert module.classify_entry(signed) is None

partial_quad = {
    "op": "0x3C", "n": 12, "seq": 3,
    "w": [
        "0x3C000000", word(568, 549), "0", "0",
        word(-561, 630), "0", "0", word(110, 181),
        "0", "0", word(-112, 185), "0",
    ],
}
finding = module.classify_entry(partial_quad)
assert finding and "hardware_oversize" in finding["reasons"]
assert "partial_quad_risk" in finding["reasons"]

split_only = dict(partial_quad)
split_only["w"] = list(partial_quad["w"])
split_only["w"][1] = word(0, 0)
split_only["w"][4] = word(-512, 0)
split_only["w"][7] = word(512, 20)
split_only["w"][10] = word(0, 20)
finding = module.classify_entry(split_only)
assert finding and "hardware_oversize" not in finding["reasons"]
assert "partial_quad_risk" not in finding["reasons"]

print("SF3 GP0 primitive analyzer: OK")
