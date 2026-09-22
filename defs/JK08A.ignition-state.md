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

## Target-vehicle trace boundary

`tools/logs/ignition_surface_audit.py` replays the exact ignition finisher,
normalized-BFS coordinate, active map slots, and the two hot surfaces against a
strict verified historical schema-1 `wide54` capture. It recovers complete one-based map commits
from the exact released/SET/CANCEL/SET/released gesture.

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
