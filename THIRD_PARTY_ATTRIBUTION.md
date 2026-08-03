# Third-Party Attribution

## PSX Ports shared input timeline

The title-neutral pad timeline implementation in `runtime/include/input_timeline.hpp`
and `runtime/src/input_timeline.cpp`, plus its contract test, were adapted from
the private PSX Ports shared runtime by PSX Ports contributors, licensed
**MIT**. The SF3 integration, compatibility fingerprint and retail SIO
placement are independently validated in this project.

MIT License

Copyright (c) 2026 PSX Ports contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## OpenBIOS — PCSX-Redux's free PS1 BIOS

[OpenBIOS](https://github.com/grumpycoders/pcsx-redux) (src/mips/openbios) by
the PCSX-Redux authors, licensed **MIT** (notice: `bios/OpenBIOS.LICENSE`;
the binary also links permissively-licensed code from
[uC-sdk](https://github.com/grumpycoders/uC-sdk), noted there too). Vendored
as the prebuilt image `bios/openbios.bin` (pin and build recipe recorded in
`bios/OpenBIOS.toml`) and statically recompiled by
`psxrecomp-bios --config bios/OpenBIOS.toml` exactly like the retail BIOS.
Normal runtime builds stage it automatically so players supply only a disc;
`bios/OpenBIOS.LICENSE` always rides alongside the shipped image.


## sljit — stack-less JIT compiler (Tier-2 in-process overlay backend)

[sljit](https://github.com/zherczeg/sljit) by Zoltan Herczeg, licensed
**BSD-2-Clause**. Vendored at `lib/sljit/` (source `lib/sljit/sljit_src/`,
license `lib/sljit/LICENSE`) and compiled into the runtime as the self-contained
Tier-2 overlay JIT backend (`runtime/src/overlay_sljit.c`). No external toolchain
dependency; sljit auto-detects the host architecture. See `SLJIT.md` (repo root /
workspace) for the backend design.

## JRickey / gba-recomp — verified-enhancement shadow + screen color science

The verified-enhancement QoL layer (`feat/shadow-enhancements`) reuses two
engine-agnostic pieces originally authored by Jrickey in
[JRickey/gba-recomp](https://github.com/JRickey/gba-recomp), licensed
**MIT OR Apache-2.0**, used with permission:

- **`ShadowVerifier`** — the envelope-correlation differential self-check,
  probation auto-gain calibration, and prove/strike/pause state machine.
  Original: `crates/gba-core/src/shadow.rs`.
  This repo: `runtime/src/audio_shadow.c`, `runtime/include/audio_shadow.h`
  (C re-implementation, via the gbarecomp C++ port `src/gba/audio_shadow.*`
  and the snesrecomp C port `runner/src/snes/audio_shadow.*`; the algorithm is
  unchanged).

- **Color-science core** (xyY→XYZ, primaries→matrix, Bradford chromatic
  adaptation, sRGB OETF) used to bake the present-time screen-color LUT.
  Original: `crates/screen/src/{color,profile,lut}.rs`.
  This repo: `runtime/src/color_lut.c`, `runtime/include/color_lut.h`
  (C re-implementation, via the gbarecomp C++ port `src/runtime/color_lut.*`).

### PSX-specific work (ours)

- The **CRT / composite / Trinitron** display panel models in `color_lut.c`
  (the GBA port modelled a handheld LCD; a console scanned out to a TV needs a
  CRT/composite model instead) — SMPTE-C / Trinitron-class phosphor gamuts,
  CRT gamma, black-lift.
- The **SPU float shadow render** (`runtime/src/spu_shadow.c`,
  `runtime/include/spu_shadow.h`): 4-point cubic resampling + float headroom
  re-render of the PS1 SPU ADPCM voice mix, driven from a read-only tap on the
  canon `spu.c` voice state. This is console-specific (the SNES analog re-renders
  the S-DSP; the GBA analog re-renders the MP2K software mixer).
- The tap plumbing in `runtime/src/spu.c` and `runtime/include/spu.h`.

All reuse keeps the original copyright and dual MIT/Apache-2.0 license.
