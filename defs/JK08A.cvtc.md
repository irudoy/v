# JK08A intake-CVTC target and reference model

## Scope

This specification owns the exact software path from the intake-CVTC target
surfaces through coolant selection and the two centered reference bytes exposed
by the custom CAN telemetry. It separates code-proven raw behavior from
candidate engineering units and physical camshaft response.

The canonical address, dependency, confidence, and scaling claims remain in
`JK08A.findings.csv`, `JK08A.axes.csv`, `JK08A.funcs.csv`, and
`JK08A.vars.csv`. The reproducible capture analysis is implemented by
`tools/logs/cvtc_target_audit.py`; immutable image and capture results are in
`patches/hardware-results.toml`.

## Data flow

```text
RPM/50 ffff11ae -------------------------+
normalized-BFS snapshot ffff102c --------+--> FUN 000bda64
                                              |  cold 0xB53A -> ffff1c5e
ffff2466.bit6 -> correction 0xAB5A -----------+  main 0xB43A -> ffff1c5c
                                                               |
coolant snapshot ffff1071 -------------------------------------+--> FUN 000bdc66
                                                                    |
                                                                    +-> ffff1bee
                                                                    +-> mode/rate/offset
                                                                    +-> ffff2326

independent centered-reference state machine FUN 000bfe88 ----------> ffff2327

ffff2326, ffff2327, actual B1 ffff2442, actual B2 ffff2443
    -> FUN 0004d2a6 intake-cam-deviation correction
    -> ignition-coordinate consumers
```

`0xFFFF2326` is common to both actual cam channels. `0xFFFF2327` is produced by
a different state machine and is not a second-bank version of `0xFFFF2326`.

## Exact target surfaces

| Role | Map | Geometry | RPM axis | Load axis | Raw result |
|---|---:|---:|---:|---:|---|
| Warm/main target | `0xB43A` | 16x16 uint8 | `0x12F3E` | `0x12F1E` | centered byte |
| Cold target | `0xB53A` | 8x8 uint8 | `0x12ECA` | `0x12EAA` | centered byte |
| Conditional correction | `0xAB5A` | 4x4 uint8 | `0x12F9A` | `0x12F92` | centered byte |

The row key is the RPM/50 scheduler snapshot `0xFFFF11AE`. Its common producer
establishes the exact relation
`min(255, uint16[0xFFFF11F4] >> 2)` to the captured RPM/12.5 word. The column
key is the Q7 normalized-BFS scheduler snapshot `0xFFFF102C`:

```text
load_raw = min(255, floor(uint16[ffff1026] * 128 / ROM16[00009534]))
ROM16[00009534] = 0x6A5A
normalized_percent = load_raw * 100 / 128
```

The explicit byte-axis search at `0x26944` clamps outside the axis, selects the
lower cell inside the axis, and computes a Q0.16 fraction with integer
truncation. Finisher `0x26770` first interpolates adjacent columns for each row
and then interpolates those row results. Unsigned linear interpolation at
`0x26740` truncates after each stage, so a floating-point bilinear expression is
not generally byte-equivalent.

`FUN 000BDA64` calculates:

```text
cold = interpolate_u8(0xB53A, rpm50, load_raw)
base_main = interpolate_u8(0xB43A, rpm50, load_raw)
correction = interpolate_u8(0xAB5A, rpm50, load_raw)

if (uint8[ffff2466] & 0x40) == 0:
    main = base_main
else:
    main = clamp_u8(base_main - correction + 128)
```

The arithmetic and centered raw representation are code-proven. The catalog
conversion `(raw-128)*0.5 degCA`, the Cylinder Filling name for the normalized
BFS ratio, and the high-detonation name for `0xAB5A` remain candidate physical
semantics.

## Coolant selection and conditioning

`FUN 000BDC66` uses raw coolant scheduler snapshot `0xFFFF1071`, which is copied
from exact DID source byte `0xFFFF1079`:

```text
coolant <= ROM8[00008D2E] = 106: selected = cold
coolant >  ROM8[00008D2D] = 131: selected = main
otherwise:
    selected = cold + trunc0((coolant-106) * (main-cold) / 25)
```

The signed division truncates toward zero. Under the exact DID conversion
`degC = raw-50`, the raw thresholds correspond to 56 and 81 degC. The selected
byte is written to scratch `0xFFFF1BEE`, then continues through mode, rate, and
offset logic before the function writes `0xFFFF2326`. Consequently
`0xFFFF2326` can be constrained or replaced with neutral `0x80`; it is not an
unconditional direct copy of a map result.

`FUN 000BFE88` independently maintains the auxiliary centered reference and
writes `0xFFFF2327` at `0xC0CEE`. Its inputs include separately produced
centered map values and mode/state gates. `FUN 0004D2A6` consumes
`0xFFFF2324..0xFFFF2327` together with both actual intake-cam bytes, but this
shared consumer does not make `0xFFFF2327` a bank-2 target.

## Target-vehicle replay

The replay reads its constants, axes, and surfaces directly from tested image
`aa18c919bf885b572aba15bb5068609ccb0ecc99f739e364938fc170bdf0d72a`.
The consumed calibration spans are also byte-identical to registered stock.
Capture `new-log-full.trc` has SHA-256
`a1f8b8c50d45e2f281917bea998d638e2d81e3a2be51b105f885f9f43c181298`.
The strict decoder produced 35,811 complete groups and 35,808 samples with all
required rotating context.

The preceding contiguous telemetry snapshot is the best dynamic input
alignment for the scheduler-produced reference:

| Check | Result |
|---|---|
| Captured coolant | raw 139..143; 35,807 warm samples; cold and blend not exercised |
| Conditional correction | `ffff2466.bit6` active in 0 samples |
| Direct selected value vs `ffff2326` | 32,256 / 35,807 exact; MAE 1.563661 raw |
| Downstream-neutralized intervals | 1,968 samples in 51 runs |
| Excluding those intervals | 32,256 / 33,839 exact; 33,122 within 1 raw; MAE 0.102131 raw; p95 0 raw |
| Active result unchanged for 8 cycles | 5,989 / 6,113 exact; 6,070 within 1 raw; p95 0 raw |
| Active result unchanged for 16 cycles | 4,781 / 4,827 exact; 4,814 within 1 raw; p95 0 raw |
| Selected value vs `ffff2327` | 17,090 / 35,807 exact; MAE 17.403524 raw; p95 56 raw |

The same-snapshot stable-active 16-cycle subset has 4,828 / 4,839 exact
comparisons and every comparison within 2 raw. This convergence, the dynamic
one-cycle alignment, and the explicit neutralized runs are consistent with a
map-derived reference followed by rate and mode conditioning. The poor
`0xFFFF2327` comparison independently rejects a symmetric bank-target model.

## Evidence boundary

The target-vehicle capture validates the warm/main raw lookup path, its exact
RPM and normalized-BFS coordinates, byte interpolation, scheduler alignment,
and the distinct operational roles of `0xFFFF2326` and `0xFFFF2327`. It does not
exercise the cold surface, coolant blend, or conditional correction. It also
does not establish the candidate degree-per-byte conversion, electrical valve
command, or physical camshaft angle at the crankshaft.

The verified CAN profile retains legacy field identifiers
`intake_cvtc_target_b1_raw` and `intake_cvtc_target_b2_raw` because they are part
of the profile CRC. User-facing dashboard and MLG labels identify them as the
common CVTC reference and auxiliary centered reference without changing the
wire contract.
