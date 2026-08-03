from pathlib import Path


root = Path(__file__).resolve().parents[2]
header = (root / "recompiler/src/config_loader.h").read_text(encoding="utf-8")
loader = (root / "recompiler/src/config_loader.cpp").read_text(encoding="utf-8")
main = (root / "runtime/src/main.cpp").read_text(encoding="utf-8")
configurator = (root / "lab/sf3/configure_compatibility.py").read_text(
    encoding="utf-8")

assert "bool                  overlay_native = true;" in header
assert 'runtime.contains("overlay_native")' in loader
assert 'toml::find<bool>(runtime, "overlay_native")' in loader
assert "if (!gc.runtime.overlay_native)" in main
assert "overlay_loader_set_native_exec(0);" in main
assert 'setting = "overlay_native = false"' in configurator

print("overlay native config guards: OK")
