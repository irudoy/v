# JK08A intake- and exhaust-CVTC target model

## Scope

This specification owns the exact software paths from the intake- and
exhaust-CVTC target surfaces through coolant selection and the two centered
target bytes exposed by the custom CAN telemetry. It also binds actual exhaust
timing and exhaust duty through the exact JK08A service-0x22 pointer tables.
Code-proven raw behavior is kept separate from candidate engineering units and
physical camshaft response.

The canonical address, dependency, confidence, and scaling claims remain in
`JK08A.findings.csv`, `JK08A.axes.csv`, `JK08A.funcs.csv`, `JK08A.vars.csv`,
and `JK08A.diagnostic-bindings.csv`. Reproducible capture analysis is
implemented by `tools/logs/cvtc_target_audit.py`; immutable image and capture
results are in `patches/hardware-results.toml`.

## Data flow

```text
RPM/50 ffff11ae -------------------------+
normalized-BFS snapshot ffff102c --------+--> FUN 000bda64
                                              |  intake cold 0xB53A -> ffff1c5e
ffff2466.bit6 -> correction 0xAB5A -----------+  intake main 0xB43A -> ffff1c5c
                                                               |
coolant snapshot ffff1071 -------------------------------------+--> FUN 000bdc66
                                                                    +-> mode/rate/offset
                                                                    +-> intake target ffff2326

RPM/50 ffff11ae -------------------------+
normalized-BFS snapshot ffff102c --------+--> FUN 000bfdc0
                                              |  exhaust cold/fallback 0xB2FA -> ffff1c5f
ffff2466.bit6 -> correction 0xAB4A -----------+  exhaust main 0xB33A -> ffff1c5d
                                                               |
coolant snapshot ffff1071 -------------------------------------+--> FUN 000bfe88
                                                                    +-> mode/rate/offset
                                                                    +-> exhaust target ffff2327

intake target ffff2326, exhaust target ffff2327,
actual intake B1/B2 ffff2442/ffff2443,
actual exhaust B1/B2 ffff2324/ffff2325
    -> FUN 0004d2a6 cam-coordinate correction
    -> ignition-coordinate consumers
```

`0xFFFF2326` is the common intake target for both intake banks.
`0xFFFF2327` is the common exhaust target for both exhaust banks; it is not a
second-bank version of `0xFFFF2326`.

## Exact diagnostic bindings

The service-0x22 response tables provide direct runtime identities:

| DID | Exact source | Identity |
|---:|---:|---|
| `0x1164` | `0xFFFF2324` | actual exhaust timing B1 |
| `0x1165` | `0xFFFF2325` | actual exhaust timing B2 |
| `0x1166` | `0xFFFF2327` | common exhaust target angle |
| `0x122F` | `0xFFFF1AAC` | exhaust VTC duty B1 |
| `0x1230` | `0xFFFF1AAE` | exhaust VTC duty B2 |

Exhaust-VTC diagnostic coordinator `0x8F168` consumes target and actual bytes
and reaches exact descriptor records for P1078/P1084 exhaust timing sensors and
P0014/P0024 exhaust VTC control. The subsystem binding therefore does not
depend on map geometry or address-free catalog naming.

The structured diagnostic profile defines `raw*2-256 degCA` for DIDs
`0x1164..0x1166`, while the HR A2L and measured community definitions use
`raw*0.5-64 degCA`. Identity and bank are exact, but neither physical angle
conversion is target-code-proven. The definition and dashboard use the latter
as a visibly marked candidate because it agrees with the matching HR cam-map
encoding.

## Exact target surfaces

| Family | Role | Map | Geometry | RPM axis | Load axis | Raw result |
|---|---|---:|---:|---:|---:|---|
| intake | warm/main target | `0xB43A` | 16x16 uint8 | `0x12F3E` | `0x12F1E` | centered byte |
| intake | cold target | `0xB53A` | 8x8 uint8 | `0x12ECA` | `0x12EAA` | centered byte |
| intake | conditional correction | `0xAB5A` | 4x4 uint8 | `0x12F9A` | `0x12F92` | centered byte |
| exhaust | warm/main target | `0xB33A` | 16x16 uint8 | `0x12F2E` | `0x12F0E` | centered byte |
| exhaust | cold/fallback target | `0xB2FA` | 8x8 uint8 | `0x12EC2` | `0x12EA2` | centered byte |
| exhaust | conditional correction | `0xAB4A` | 4x4 uint8 | `0x12F96` | `0x12F8E` | centered byte |

Each calculator reaches its three surfaces through one literal block that pairs
every map base with its own interpolation entry:

| Path | Literal block | Cold | Warm/main | Correction |
|---|---:|---:|---:|---:|
| intake | `0xBDD04` | `0xB53A` | `0xB43A` | `0xAB5A` |
| exhaust | `0xC0014` | `0xB2FA` | `0xB33A` | `0xAB4A` |

Both blocks use interpolation entries `0x26140`, `0x261B8`, and `0x26084` in
that order. The grouping identifies the intake or exhaust role of a target
surface from stock bytes alone, without map values, axis geometry, or
dispatcher topology.

The row key is RPM/50 scheduler snapshot `0xFFFF11AE`. Its common producer
establishes the exact relation
`min(255, uint16[0xFFFF11F4] >> 2)` to the captured RPM/12.5 word. The column
key is Q7 normalized-BFS scheduler snapshot `0xFFFF102C`:

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

`FUN 000BDA64` calculates the intake surfaces:

```text
cold = interpolate_u8(0xB53A, rpm50, load_raw)
base_main = interpolate_u8(0xB43A, rpm50, load_raw)
correction = interpolate_u8(0xAB5A, rpm50, load_raw)

if (uint8[ffff2466] & 0x40) == 0:
    main = base_main
else:
    main = clamp_u8(base_main - correction + 128)
```

`FUN 000BFDC0` performs the same lookup and centered-subtraction pattern for
the exhaust surfaces:

```text
cold = interpolate_u8(0xB2FA, rpm50, load_raw)
base_main = interpolate_u8(0xB33A, rpm50, load_raw)
correction = interpolate_u8(0xAB4A, rpm50, load_raw)

if (uint8[ffff2466] & 0x40) == 0:
    main = base_main
else:
    main = clamp_u8(base_main - correction + 128)
```

The 0xB33A identity is code-proven by its path into DID 0x1166 and the exhaust
control and DTC consumers. The HR A2L defines a matching 16x16 `Exhaust Cam
Timing Map` with `(raw-128)*0.5 deg`; this conversion remains homologous for
JK08A. Stock 0xB2FA is neutral 128 throughout. Its cold/fallback name describes
the exact coolant-selector role without asserting a catalog title.

## Coolant selection and conditioning

`FUN 000BDC66` and `FUN 000BFE88` use raw coolant scheduler snapshot
`0xFFFF1071`, which is copied from exact DID source byte `0xFFFF1079`:

```text
coolant <= ROM8[00008D2E] = 106: selected = cold
coolant >  ROM8[00008D2D] = 131: selected = main
otherwise:
    selected = cold + trunc0((coolant-106) * (main-cold) / 25)
```

The signed division truncates toward zero. Under the exact DID conversion
`degC = raw-50`, the thresholds correspond to 56 and 81 degC. The
intake-selected byte is copied to scratch `0xFFFF1BEE` and continues through
mode, rate, and offset logic before `0xFFFF2326`. The exhaust-selected byte
continues through an independent set of mode, rate, and offset constraints
before `0xFFFF2327` at `0xC0CEE`. Either conditioned target can differ from the
immediate map lookup or be replaced with neutral `0x80`.

## Target-vehicle replay

The replay reads constants, axes, and surfaces directly from tested image
`aa18c919bf885b572aba15bb5068609ccb0ecc99f739e364938fc170bdf0d72a`.
The consumed calibration spans are byte-identical to registered stock. Capture
`new-log-full.trc` has SHA-256
`a1f8b8c50d45e2f281917bea998d638e2d81e3a2be51b105f885f9f43c181298`.
The strict decoder produced 35,811 complete groups and 35,808 samples with all
required rotating context.

The preceding contiguous telemetry snapshot is the best dynamic input
alignment for both scheduler-produced targets:

| Check | Intake `ffff2326` | Exhaust `ffff2327` |
|---|---:|---:|
| direct exact | 32,256 / 35,807 | 26,344 / 35,807 |
| direct MAE | 1.563661 raw | 5.619404 raw |
| downstream-neutralized intervals | 1,968 samples / 51 runs | 1,986 samples / 59 runs |
| unchanged 16-cycle exact | 4,781 / 4,827 | 4,838 / 5,366 |
| unchanged 16-cycle within 2 | 4,819 / 4,827 | 5,121 / 5,366 |
| unchanged 16-cycle MAE | 0.019888 raw | 1.015095 raw |

The capture coolant range is raw 139..143, all samples use the warm band, and
`ffff2466.bit6` is inactive throughout. The replay therefore validates both
warm/main lookup paths, exact RPM and normalized-BFS coordinates, interpolation
order, scheduler alignment, and convergence of the independently conditioned
targets. It does not exercise cold surfaces, coolant blends, or conditional
corrections.

## Evidence boundary

Static DID and DTC paths establish the intake/exhaust target distinction even
where downstream conditioning makes a map replay differ from the published
byte. The capture does not establish the candidate degree-per-byte conversion,
electrical valve command, or physical camshaft angle at the crankshaft.

CAN telemetry schema 2 names the two sources `intake_cvtc_target_raw` and
`exhaust_cvtc_target_raw`, matching their recovered common-target roles. The
generated profile CRC binds those names and sources to the host decoder.
