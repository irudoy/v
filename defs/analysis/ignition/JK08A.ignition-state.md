# JK08A ignition timing-state surfaces

## Scope and result

This specification defines the exact JK08A software semantics of the 16x16
surface triplet at `0x991A`, `0x9A1A`, and `0x9B1A`. These surfaces participate
in selected timing state, knock feedback, and the final ignition-command path.
They are not direct commanded spark-angle tables.

The low seven bits form the interpolated timing-state value. Bit 7 is an
independent pass-through flag that enables a knock-state path. Exact JK08A code
proves the `x - 64` crank-degree scale of the low field: compositor
`0x0004BDC2` centers it at 64 beside the computed base angle `0xFFFF23F1`,
every later term enters the final coordinate `0xFFFF11D4` with coefficient 1,
and J1979 Mode 01 PID `0x0E` publishes that coordinate as degrees before TDC.
The homologous HR A2L and UpRev vocabulary names the field a timing trim
relative to calculated MBT. Physical spark timing on the crankshaft remains a
hardware measurement.

## Coordinates and interpolation

All three surfaces use the same explicit axes:

| Axis | Address | Exact representation |
| --- | --- | --- |
| Row | `0x11ECE` | RPM / 50, spanning 400..7400 RPM |
| Column | `0x11EBE` | Q7 normalized BFS, `raw * 100 / 128 percent` |

The column coordinate is scheduler snapshot `0xFFFF102C`. It is formed from
Base Fuel Schedule and `ROM16[0x9534]` as documented in `JK08A.load.md`. The row
coordinate is compared with RPM/12.5 word `0xFFFF11BC` after each stored axis
point is multiplied by four.

Wrapper `0x00026230` uses byte-axis core `0x00026944` and the unique finisher at
`0x000267CC`. The finisher performs two-dimensional interpolation on only bits
`0..6`. It then copies bit 7 from the lower-left cell selected by the two axis
searches. Bit 7 is not numerically interpolated.

## Cold, active, and reference samples

Function `0x0004E1C0` produces two samples on every pass:

- `0xFFFF160F` is the active cold/hot sample;
- `0xFFFF1610` is the cold/high-octane reference sample.

The exact selection is:

| Coolant snapshot `0xFFFF1071` | Active sample `0xFFFF160F` | Reference sample `0xFFFF1610` |
| --- | --- | --- |
| `<= ROM8[0x8D2E] = 106` | `0x991A` cold | `0x991A` cold |
| `107..131` | blend cold with selected hot | blend cold with `0x9A1A` |
| `> ROM8[0x8D2D] = 131` | selected hot | `0x9A1A` high octane |

The exact diagnostic coolant conversion is `deg C = raw - 50`, so the cold
boundary is 56 deg C and the warm boundary is 81 deg C. The interpolation band
therefore covers raw 107..131, or 57..81 deg C.

Bit 6 of `0xFFFF2466` selects the active hot surface:

| `0xFFFF2466.bit6` | Active hot surface |
| ---: | --- |
| 0 | `0x9A1A`, high octane |
| 1 | `0x9B1A`, high detonation |

Consequently `0x9A1A` remains the reference even when `0x9B1A` is active. The
two output samples are equal in the cold region and on the high-octane hot
path. They can differ only when the high-detonation path is active during the
blend or warm region.

When `0xFFFF2468.bit3` and stock `ROM8[0x8B3D].bit1` are both set, the relevant
surface lookups use column key `0xFF` instead of `0xFFFF102C`. Stock
`ROM8[0x8B3D]` is `0x82`, so the calibration gate is enabled.

## Selected-state extraction

Function `0x0004AF38` separates the fields and publishes:

```text
ffff12de = ffff160f & 0x7f
ffff12e0 = ffff1610 & 0x7f

if ROM8[0x8b3f].bit1:
    ffff12df = max(ffff12e0 - ffff12de, 0)
else:
    ffff12df = 0

ffff23bd = max(ffff12de - ffff11af, 0)
```

The normal branch of compositor `0x0004BDC2` includes `0xFFFF23BD` linearly in
the signed state written to `0xFFFF1830`. The chain from that state to the
final software coordinate is exact:

```text
ffff1830 = clamp_s8(ffff23f1 + ffff23bd - ffff23c5 - ffff12dc - ffff15ea
                    - 128 + ffff1a7d + ffff134a)
         = ffff23f1 + (max(low7 - ffff11af, 0) - 64) + (ffff1a7d - 64)
           - ffff23c5 - ffff12dc - ffff15ea + ffff134a
ffff2404 = ffff1830                          # latch 0x0004C136, normal gates
ffff2378 = ffff2404 of the previous pass     # scheduler 0x00020DFE block copy
ffff12d6 = clamp_s8(ffff2378 + ffff11d6 + ffff2356 - ffff1ff6)   # 0x0004D99C
ffff11da = clamp(ffff12d6 + ffff564c, -7, 50)   # 0x0004DBE8, ffff564c gated
ffff11d4 = rate-limited and bounded ffff11da    # 0x0004DBE8
```

Every coefficient of the map field along this chain is 1, and J1979 Mode 01
PID `0x0E` publishes `0xFFFF11D4` as `A/2 - 64` degrees before TDC. One raw
count of the low-seven field is therefore one crank degree while the field
stays above threshold `0xFFFF11AF`, and raw `64` is the zero adjustment
relative to the base angle and the other terms. The cam
term `0xFFFF1A7D` is centered at 64. The retard terms `0xFFFF23C5`,
`0xFFFF12DC`, `0xFFFF15EA`, and `0xFFFF11F9` are neutral at zero. The
work-support timing adjustment `0xFFFF564C` (`JK08A.work-support.md`) lies
within `-5..0` and is added only while the warm, mid-RPM, mid-load window
flags in `0xFFFF5B31` are clear. Threshold
`0xFFFF11AF` is the scheduler snapshot of `0xFFFF11E7`, a rate-limited follower
of `0xFFFF2363` written by `0x0004E0C2`. The surrounding terms, limits, and
mode selection prevent treating one surface cell as the final command.

Map bit 7 is consumed independently. Coordinator `0x000493E8` copies active
sample bit 7 into `0xFFFF2494.bit6`, which participates in the eligibility
logic for knock and high-detonation state. The editor therefore exposes the
low-seven timing trim and bit-7 enable field as preserving masked views of the
same byte.

## Knock coordinator and hot-surface difference

Periodic-table word `0x21A70` calls `0x000493E8` after the cold/hot selector.
The coordinator consumes and clears saturating knock-event count
`0xFFFF2142`, maintains several signed Q8 states, looks up both hot surfaces
independently, and updates `0xFFFF2466.bit6` for a later selector pass.

One coordinator branch updates signed state `0xFFFF1258` by:

```text
quiet interval: state += ROM16[0x8eaa] = 13
knock interval: state -= ROM16[0x8eae] * event_count
                                      = 307 * event_count
```

The arithmetic saturates to signed 16-bit range. Other mode branches can copy,
force, filter, or zero the state, so a nonzero latched event count does not by
itself guarantee a `-307` transition.

Both hot lookups discard bit 7. When `0xFFFF2469.bit7` is clear and
`0xFFFF2467.bit6` is set, the direct branch forms:

```text
ffff121a = int16(
    base_q8
    + ((high_octane_low7 - high_detonation_low7) << 8)
)
```

The alternate branch slew-limits a branch-selected Q8 state, applies a dynamic
negative bound, and clamps positive output to zero. Therefore the map-difference
formula is conditional, not a universal interpretation of `0xFFFF121A`.

The scheduler copies `0xFFFF2466` to `0xFFFF2467` at `0x21068` before the
periodic tasks. The coordinator reads `0xFFFF2469.bit7` before it updates that
byte through the shared store at `0x49704`. A capture after the scheduler
therefore reports the current pass's snapshot byte and the coordinator state
for the next evaluation. The previous consecutive full-rate capture supplies
the latter branch input for the current pass.

One guarded hysteresis path at `0x49A16` sets `0xFFFF2466.bit6` when signed
`RAM16[0xFFFF1382] <= ROM16[0x8F02]`, and clears it when that word exceeds
`ROM16[0x8F00]`. Other paths can force or retain the bit. The raw state
producer and the physical switching conditions remain unreviewed.

The published byte is truncation toward zero, not an unconditional high-byte
copy:

```text
ffff22fa = trunc_toward_zero(int16(ffff121a) / 256)
```

Function `0x0004D99C` consumes `0xFFFF22FA` while building signed engine-event
correction `0xFFFF12D6`. `0x0004DBE8` later combines that correction into final
software coordinate `0xFFFF11D4`; `0x0004DF82` converts the final coordinate to
the APC command. The complete output boundary is in
`JK08A.ignition-output.md`.

One selector hysteresis branch uses signed Q8 state `0xFFFF1382`. With stock
calibrations it sets `0xFFFF2466.bit6` when the state is at or below
`ROM16[0x8F02] = -1792` and clears it only above
`ROM16[0x8F00] = 8192`. These are raw Q8 thresholds of -7 and +32 state counts.
Other gates can force either selector state, so these thresholds are not the
complete high-level high-detonation policy.

## Bounded knock state selection

H is the explicit first masked byte at SP+0x0c, in 0..127. Incoming R0
supplies the independent second raw value; its AND #127 and byte store
execute. With `ffff2469.bit7` clear and `ffff2467.bit6` set, widened R2 is
`int16(ffff1380)+256*(H-(uint32(R0)&127))`. The register can exceed either
signed16 boundary and is neither saturated nor prematurely truncated.

The alternative path uses S=`int16(ffff1258)`, V=`int16(ffff1380)` and
N=`uint8(ffff230a)`. With stock ROM16[00009078]=1280, it computes
`Y=min(S+1280,max(S-1280,V))` and `R2=min(0,max(Y,-256*N))`.
Standalone entries execute this path regardless of the normal gate bits.
All byte gates, all N values and every low7 difference are covered.
For N=128 the forcing-below-bound outcome is unreachable; equality is
covered. For N>=129 the bound lies below the signed input hull.

The first lookup/mask/store and second lookup are not executed. Exact static
anchors bind both table pointers, call/delay pairs and bases; they establish
no lookup numerics, producer identity or dispatch reachability. Six declared
high-RAM pool aliases preserve all checked instruction bytes.

The conversion gives
`ffff121a=uint16(R2)` and `ffff22fa=trunc0(int16(ffff121a)/256)`.
Signed monotonic behavior across word
wrap, complete coordinator execution, cadence, physical timing and hardware
behavior require separate evidence.

## Bounded knock event publication

Let S be the signed byte at `ffff2378`, W the signed word at `ffff11d6`,
and C the signed byte at `ffff2356`. P is the full independent incoming
R6 register, constrained to 0..65535. The fragment publishes the widened
signed32 sum S+W to longword `ffff1ff8` and signed byte
`max(-128,min(127,S+W+C-P))` to `ffff12d6`. The sum remains in R2 before
the remaining arithmetic; there is no RAM readback of `ffff1ff8`.

The RAM word at `ffff1ff6` is independently seeded and preserved. The
fragment neither reads that word as P nor executes its earlier producer.
It contains no EXTU.B or EXTU.W conversion of incoming R6. Literal cases
cover signed extrema, sums outside the signed-word range, independent
P boundaries and all valid neighbors of both signed-byte clamp edges.

The exact natural-path base anchors include the R13 load at `0004da7c`,
which addresses the `ffff2330` context.

Full builder execution, timer/latch behavior, scaled-term production,
bypass branches, natural full-function return, cadence, physical input
identities and hardware behavior remain outside this bounded proof.

## Bounded knock event retard

Let K, A and B be signed bytes at `ffff22fa`, `ffff11f9` and `ffff11fa`.
Let H be the unsigned high byte of word `ffff23c2`. Q is true when
`ffff24c5.bit5` or `ffff24cb.bit2` is set. G is bit 5 of ROM byte `00008710`;
the retained stock byte is `0x7c`. The two output words obey:

| Q | G | `ffff11d6` | `ffff11d8` |
|---|---|---|---|
| 0 | 0 | -A | Preserve the complete prior word |
| 0 | 1 | -A | -B |
| 1 | 0 | min(K, -A) | Preserve the complete prior word |
| 1 | 1 | min(K-H, -B) | min(K, -B) |

The enabled Q branch uses B for both minima. The high byte enters only its
first minimum, while the companion uses the unadjusted K. Signed byte loads,
negation, EXTS.W, comparisons, branch outcomes and store delay slots bind to
the exact instruction words. The unsigned high-byte interpretation does not
establish the source word producer's signedness or engineering scale.

Full event-builder mode reachability, timer/latch policy, producer lifecycle, later
summation, physical input identities, cadence and hardware behavior remain
outside this execution envelope.

## Shared ignition-advance event arithmetic

Steps 22 and 23 of `ignition_advance/chain` share the bounded event
publication contract, while steps 24 and 25 share the bounded event-retard
contract. All four views name `event_timing_correction_builder/fn` at
`7mfk:0004d99c`. The ordered paths, effects, signs and all other chain
steps retain their existing declarations.

Publication uses full independent incoming R6, P in 0..65535. Signed-byte
S at ffff2378 and signed-word W at ffff11d6 form the signed32 sum at
ffff1ff8; ffff12d6 receives signed-byte saturation of S+W+C-P, with signed
byte C at ffff2356. The live R2 supplies both publications with no RAM
readback. The bounded fragment does not consume the separately seeded
ffff1ff6 word numerically and establishes no equality between that RAM
word and incoming R6.

Retard uses Q from ffff24c5.bit5 OR ffff24cb.bit2 and G from the ROM
bit5 configuration scalar at 00008710. Signed K/A/B and unsigned high
byte H supply the declared FIRST alternatives. SECOND has whole-word
retention when G=0; when G=1 it publishes the separate B-based result.
The accepted contracts define these widths, conditions and alternatives.

Full builder dispatch, upstream request and P production, snapshot copying,
timer/latch behavior, scheduling, physical units and hardware validation
remain outside these bounded arithmetic proofs. Their independent owned
evidence retains its existing scope.

## Bounded knock integration

Let S be signed word `ffff1258`. The quiet entry publishes
`ffff1380 = clamp(S + ROM16[00008eaa], -32768, 32767)` with stock increment 13.
The event entry receives independent R4=x in the explicit domain 0..255 and
publishes `ffff1380 = clamp(S - ROM16[00008eae]*x, -32768, 32767)` with stock
multiplier 307. Both entries clear byte `ffff2142`. They are alternative entry
views of one publication, not sequential state updates. Event R4=0 remains an
event-entry context and does not identify a quiet dispatch.

The event MUL.L consumes the full 32-bit R4; this fragment performs no EXTU.B
on it and establishes no truncation of arbitrary upper bits. Every event case
seeds the RAM count independently and differently from R4. The preceding
dispatcher MOV.B at `0004952c` and EXTU.B at `0004952e` have separate static
byte checks; the dispatcher, quiet eligibility predicate and natural entry
selection are outside this execution envelope.

R4=213 includes the final transition at S=32623; R4>=214 publishes -32768
throughout the signed-word domain. MACL equals 307*x on the event path and
retains its incoming value on the quiet path.

This contract does not execute the complete coordinator or establish physical
mode reachability, event cadence, learning lifecycle or hardware behavior.

## Bounded timing-byte conversion

Incoming R2 is an explicit raw register context. EXTS.W R2,R12 gives the signed
low word. The delay-slot store at `00049656` publishes its raw low 16 bits to
`ffff121a` on both sign branches. Negative input receives an added 255 before
logical shift and signed reconstruction; nonnegative input bypasses that
adjustment. The byte store at `000496d8` publishes
`ffff22fa = trunc0(int16(ffff121a)/256)`. This formula describes the shared
low-word input; the conversion uses its register copy without reading the
stored word back.

Unexecuted stock load anchors at `000495da` and `000499ae` bind incoming R9 to
`ffff22f8`. Their producing paths are outside this execution. Only pool
`000496c8` receives the declared simulator alias for `ffff120e`. The ordinary
RTS/NOP boundary at `000496da` is outside checked stock instructions.

Positive inputs establish arithmetic without asserting full-coordinator mode
reachability. Earlier calculations, mode selection, event consumption, cadence,
complete coordinator behavior and hardware behavior remain separate contracts.

## Target-vehicle trace boundary

The historical verified schema-1 `wide54` analysis compares the exact ignition
finisher, normalized-BFS coordinate, active map slots, and the two hot surfaces
with the capture. It recovers complete one-based map commits from the exact
released/SET/CANCEL/SET/released gesture. The current
`tools/logs/ignition_surface_audit.py` uses the schema contract accepted by
`tools/logs/can_telemetry.py`; it does not replay that historical schema-1
capture with the current decoder.

For `new-log-full.trc` and its registered 1.11 image:

- 35,809 verified snapshots are analyzed;
- commits are recovered at 112.3953 seconds for Map 2 and 178.1622 seconds for
  Map 3;
- the sample distribution is 5,790 on Map 1, 6,418 on Map 2, and 23,601 on
  Map 3;
- `0xFFFF2466.bit6` remains clear in every sample, so the active hot surface is
  always high octane;
- five snapshots carry one latched threshold-exceedance event each;
- `0xFFFF121A` spans -307..0, and only one of those five event samples has the
  immediate `-307` state transition;
- both map commits have a zero `0xFFFF121A` step;
- at the code-proven prior-snapshot input alignment, the selected main-slot
  lookup differs from the stock-slot lookup in 8,253 of 35,808 comparisons;
  the selected high-detonation copies do not differ from stock in this image.

The capture proves the selector remained on the high-octane path and confirms
that event counts are subject to coordinator gates. It does not directly
observe `0xFFFF160F`, `0xFFFF1610`, `0xFFFF2467`, `0xFFFF2469`, or
`0xFFFF22FA`. It therefore does not dynamically validate cold blending,
high-detonation selection, bit-7 behavior, or the conditional direct
map-difference branch.

## Calibration boundary

- Edit the low-seven timing field and bit-7 enable field through their masked
  views so one edit preserves the other field.
- Raising a low-seven value by one count advances the final software
  coordinate by one crank degree, subject to the retard terms, the `-7..50`
  clamp, the rate limiter, and the mode bounds; it is not a request for an
  absolute spark angle.
- `0x9A1A` affects both the active high-octane sample and the reference used
  against `0x9B1A`; `0x9B1A` affects the active sample only when the selector is
  set.
- `0x991A` is common to all map-switching slots and controls the cold endpoint
  of both samples.
- A warm capture with `0xFFFF2466.bit6 = 0` cannot validate the cold or
  high-detonation surfaces.
- Physical spark interpretation still requires a timing-light reference and
  controlled knock-safe engine validation.
