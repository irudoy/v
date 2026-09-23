# JK08A Base Fuel Schedule load coordinates

## Scope

This specification separates the internal load coordinate used by tuning maps
from the J1979 Mode 01 PID `0x04` Calculated Load byte. Both values are derived
from Base Fuel Schedule, but they use different denominators, encodings, RAM
locations, and consumers.

The arithmetic and scheduling relationships below have code confidence. The
catalog name `Cylinder Filling Up Efficiency` remains a physical-name
candidate. The exact engineering interpretation used in this project is the
dimensionless percentage of a Base Fuel Schedule reference.

## Base Fuel Schedule source

The primary airflow path is:

```text
MAF ADC channels
  -> ffff101c/ffff101e
  -> bank MAF preprocessing and scaling
  -> ffff1e38
  -> FUN 0003b75c
  -> newest Base Fuel Schedule ffff1026
```

Exact DID `0x1208` identifies `ffff1026` as Base Fuel Schedule. One count is
`1/2048 ms` in the time base of the injection-pulse words, as derived in
[`JK08A.fuel.md`](JK08A.fuel.md); the load-coordinate ratios do not depend on
that physical conversion.

## Internal map coordinate

`FUN 0003b75c` reads the newest unsigned Base Fuel Schedule word and
`ROM16[0x9534]`. Stock `ROM16[0x9534]` is `0x6A5A`, or 27226. Sites
`0x3BD3A..0x3BD5A` implement:

```text
live_load_raw = min(255, floor(uint16(ffff1026) * 128 / 27226))
ffff1048 = live_load_raw
```

The first equivalent quotient at `0x3BD1E..0x3BD34` performs the saturation
test; the second quotient reads `ffff1026` explicitly and supplies the stored
byte. A whole-program p-code census finds `0x3BD5A` as the only direct writer
of `ffff1048`.

The exact normalized representation is therefore:

```text
normalized_BFS_percent = raw * 100 / 128
                       = raw * 0.78125
```

Raw 128 means that Base Fuel Schedule equals the `0x9534` reference. Raw 255
is the saturated representation and corresponds to 199.21875% of that
reference. This is a normalized Base Fuel Schedule ratio, independent of the
physical BFS unit. Reference `0x6A5A` is `27226 / 2048 = 13.29 ms`.

## Scheduler snapshot

At `0x20F0A..0x20F1A`, `FUN 00020dfe` calls block copier `FUN 00022104` with
source `ffff1048`, destination `ffff102c`, and length `0x1C`:

```text
ffff1048..ffff1063 -> ffff102c..ffff1047
```

Consequently `ffff102c` is the scheduler snapshot of `ffff1048`. The copy runs
before periodic tasks produce the next `ffff1026` and `ffff1048` values. Maps
executed in that scheduler pass consume `ffff102c`; the end-of-pass custom CAN
snapshot contains the newly produced `ffff1026`. The telemetry profile also
carries `ffff102c` itself, the coordinate those maps consumed. A recording
without that byte reconstructs the map coordinate aligned with pass N from the
contiguous BFS sample at pass N-1, and a missing telemetry tick breaks that
reconstruction for the following sample.

## Code-proven consumers

The internal coordinate has a broad tuning role:

| Consumer | Coordinate use |
| --- | --- |
| `FUN 0004e1c0` | Column input for timing-state maps `0x991A`, `0x9A1A`, and `0x9B1A` |
| `FUN 000bda64` | Column input for intake-cam target maps `0xB43A`, `0xB53A`, and conditional correction `0xAB5A` |
| `FUN 000bfdc0` | Normal load input for exhaust-CVTC target maps `0xB33A`, `0xB2FA`, and correction `0xAB4A`; runtime flags can force `0xFF` |
| `FUN 0004d2a6` | Threshold comparison and `raw >> 3` coordinate for intake-cam-deviation coefficient maps `0xA4AA` and `0x9F1A` |
| `FUN 0004ac60`, `000528be`, `0005651c` | Inputs to additional limits, transient coefficients, and state thresholds with unresolved physical outputs |

Some paths read the live producer byte `ffff1048` instead of its scheduler
snapshot. `FUN 0004bbee` uses the terminal byte at `0x11ECD` of ignition load
axis `0x11EBE` as its upper coordinate. That byte is raw 128, so the ramp's
upper coordinate is exactly the 100% fixed-reference point. A separate gate
inside final timing-coordinate builder `FUN 0004dbe8` also reads `ffff1048`.
The representation is the same; only the scheduling age differs.

## J1979 Calculated Load

`FUN 0008083c` independently produces `ffff413e`, returned by
`FUN 00035856` for Mode 01 PID `0x04`. It uses the scheduler Base Fuel Schedule
word `ffff1024` and RPM-dependent map `0x1491A`:

```text
rpm25 = min(255, uint16(ffff11f4) >> 1)
M = implicit_u16_interpolate(ROM[0x1491A], rpm25 << 8, step=0x1000)
q = floor(uint16(ffff1024) * 256 / M)
ffff413e = min(255, q)
```

The 16 implicit RPM points are exactly 0, 400, 800, ..., 6000 RPM. The final
cell is selected above the last point. Entry gates can force zero or 255.

An optional second normalization uses `ffff329f` when
`ROM8[0x870E].bit4` is set. Stock `ROM8[0x870E]` is `0x28`, so bit 4 is clear
and the second normalization is inactive in stock JK08A. Standard J1979
presentation converts the byte as `100 * A / 255 percent`.

## Representation comparison

| Property | Internal tuning coordinate | J1979 PID `0x04` |
| --- | --- | --- |
| Live/result RAM | `ffff1048`, snapshot `ffff102c` | `ffff413e` |
| BFS input | newest `ffff1026` | scheduler snapshot `ffff1024` |
| Denominator | fixed `ROM16[0x9534]` | RPM-dependent map `0x1491A` |
| Encoding | Q7 ratio, `100 * raw / 128` | J1979 byte, `100 * raw / 255` |
| Main purpose | ignition, CVTC, AFR candidate, internal coefficients | diagnostic publication |

PID `0x04` is not a direct observation of the internal map axis. No constant
linear conversion between the two bytes exists because the diagnostic
denominator varies with RPM.

## Moving-load capture validation

`tools/logs/load_axis_audit.py` reproduces both formulas from the exact ROM and
strict historical schema-1 `wide54` telemetry. For capture SHA-256
`a1f8b8c50d45e2f281917bea998d638e2d81e3a2be51b105f885f9f43c181298`:

- 35,811 complete snapshots are present and 35,809 follow schema verification;
- reconstructed internal load spans raw 9..116, or 7.03125..90.62500%;
- diagnostic load spans raw 16..230;
- same-snapshot diagnostic reconstruction is exact for 26,914 of 35,809
  samples and within one code for 33,682 samples;
- previous-contiguous-snapshot reconstruction is exact for 28,093 of 35,808
  comparisons and within one code for 34,367 samples, with maximum absolute
  error 8 codes.

The improved previous-snapshot alignment is consistent with the code-proven
scheduler copy and producer order. Residual differences can include
within-pass input timing and diagnostic entry gates; they do not collapse the
two denominator models into one quantity.

## Calibration boundary

`0x9534` controls the normalization of all internal-map consumers and also
appears in the engine-torque filling coordinate and torque base-term
calculation. Editing it is therefore a cross-subsystem change, not a display
calibration. `0x1491A` controls diagnostic Calculated Load and is not an axis
reference for the ignition or intake-cam maps.

The historical `wide54` capture is sufficient for offline reconstruction of the
internal coordinate. Adding `ffff102c` to a future wire schema is useful only
when exact per-pass alignment must survive dropped groups or when the live
snapshot byte itself is required.
