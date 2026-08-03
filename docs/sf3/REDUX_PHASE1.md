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

The first new layer converts relative mouse motion into bounded ordinary
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

First unresolved invariant: SF3 camera owner and pitch-field semantics at the
confirmed candidate site. No offsets will be copied by analogy.
