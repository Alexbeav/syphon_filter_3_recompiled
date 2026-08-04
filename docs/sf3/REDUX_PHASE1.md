# SF3 Redux Phase 1

## Baseline and boundary

Redux begins at SF3 Recomp compatibility commit `6aa349e`. The accepted
42,480-sample Mission 1/Mission 2 route remains the compatibility oracle; its
SHA-256 is `4b534e2b0e1b7e675fb55f8967f539333ba3b5b37902eb0caa503faa419d1277`.
No enhancement may force application state, patch generated retail code,
fabricate callbacks, replace gameplay or hide interpreter ownership.

The isolated project contains framework source and clean configuration only.
User-owned SCUS-94640, discs, BIOS, cards, traces, generated sources, caches and
captures remain ignored local inputs.

## Evidence and current delta

The generic runtime already provides OpenGL 1x-4x internal supersampling,
nearest/bilinear texture selection, configurable keyboard-to-PAD input and a
reversible GTE/presentation widescreen facility. Phase 1 therefore does not
need a new high-resolution renderer. It needs an SF3 profile, regressions and
retail-route validation.

The fallback layer converts relative mouse motion into bounded ordinary
retail D-pad pulses, with right-button aim gating for vertical motion. Mouse
buttons map to existing retail PAD buttons. It is disabled by default, loses
all state when focus is lost, cannot operate headlessly or in a hidden window,
and commits exactly once per vblank. This is a usable compatibility layer, not
yet true freelook.

SCUS-94640 was checked independently rather than accepting SF2 addresses. The
SF2 semantic camera instruction `0x8EA30034` occurs uniquely in each user-owned
executable: SF2 at `0x80053464`, SF3 at `0x800549C4`. The surrounding sequence
is instruction-for-instruction identical after a `+0x1560` shift. Structural
mapping places the containing SF3 routine at `0x80053954`. At the candidate
site SF3 retains controller in `$s2` and player in `$s3`; SF3's state layout
uses controller/wrapper pointers at `+0xF4/+0xF8`, not SF2's `+0xDC/+0xE0`.
Application state `0x80121B88` is independently established by the SF3 runtime
profile. These facts narrow a direct camera hook but do not validate SF2's
owner/pitch offsets for SF3.

## Bounded SF3 proof — 2026-08-03

A read-only hidden/dummy-audio probe armed only routine `0x80053954` and block
`0x800549C4`. At retail state 0 it observed player `0x801B0608`, state
`0x8012D79C`, controller `0x801A1CF4`, wrapper `0x801FD2BC` and base
`0x8012B7D0`. Wrapper `+0xDC` equalled the player during player ownership;
base `+0x8E8` and `+0x918` agreed. The exact block executed in the bounded
window. A separate 4x Redux replay also observed the wrapper owner switch to
`0x801AEE48` during the opening scripted camera, proving that state 0 alone is
insufficient and that the owner check is necessary.

The direct bridge therefore takes player from live `$s3` and controller from
live `$s2`, avoiding SF2's global-player lookup. Generation fails if the exact
resident word changes. Runtime application additionally requires application
state 0, valid RAM pointers and `owner == player`. Motion expires after four
vblank callbacks and resets on focus loss. The title-neutral unit covers chase,
aim and owner rejection; source-contract tests cover the generation/runtime
guards. The framework suite passes 53/53.

The accepted route was retagged only after exact source SHA-256 validation;
all 42,480 PAD payload samples remain byte-identical (payload SHA-256
`6d26b87efb8b9cf935d73a156581edb899d2891896bd761d7d0ab7ec1499840f`).
The 4x diagnostic run reached the state-0 window, recorded exact site hits and
ended cleanly at the 3,000-sample bound. This proves structural integration,
not human camera feel.

## Ordered gates

1. Build and unit-test the reversible PAD adapter and focus isolation.
2. Run the accepted retail route at 4x/4:3 and compare transitions, terminal
   report, cards and bounded captures against the compatibility baseline.
3. Observe the candidate camera routine live in state 0. Validate player,
   controller, wrapper, owner and pitch fields with bounded RAM/register
   checks; reject every contradicted SF2-derived offset.
4. Add direct mouse camera only behind a title-configured exact-word hook and
   an off switch. Prove no motion outside live state 0 and two matching clean
   route runs.
5. Validate 16:9 separately. Generic widescreen stretches HUD/FMV, so it is
   experimental until SF3-specific projection and 2D/FMVs pass captures.
6. Treat PGXP, interpolation, texture replacement/filtering and other Redux
   features as later independent gates. PsyCross PGXP is not a drop-in patch.

First unresolved invariant: visible chase/aim feel and seamless ownership
handoff across scripted cameras. This requires a human windowed run; hidden
evidence cannot close it.

## Runtime profile boundary

The exact-word-guarded SCUS-94640 hook is present in both modes; enhancement
selection does not regenerate or edit retail code. Per-install
`settings.toml [controller]` now owns `mouse_camera`, four independent chase/
aim sensitivities, and `mouse_invert_y`. `PSX_MOUSE_CAMERA=0|1` is a bounded
per-run override for automated A/B checks. Launcher writes preserve all six
fields even though dedicated camera widgets are not yet exposed.

The 2026-08-03 Release A/B used one executable and the same retagged,
payload-identical accepted route. Camera-on and camera-off hidden/silent runs
both stopped cleanly at sample 3,000 and produced matching card hashes. The
framework suite passes 54/54 under `PYTHONUTF8=1`, including a parse/save/
reload regression for the new settings. Full 42,480-sample Redux closure
remains pending; this short check proves switch ownership, not mission flow.
