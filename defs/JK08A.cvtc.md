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

## Solenoid output stage

Both cam-phaser solenoids are driven by ATU-II channel 7 in PWM mode. The
hardware manual assigns the channel-7 block as cycle registers `CYLR7A..CYLR7D`
at `0xFFFFF588..0xFFFFF58E` and buffer registers `BFR7A..BFR7D` at
`0xFFFFF590..0xFFFFF596`. Application code programs the buffer register; the
timer transfers it into the duty register at the cycle boundary.

| Channel | Cycle register | Buffer register | Path | Source cell |
|---|---:|---:|---|---:|
| 7A | `0xFFFFF588` | `0xFFFFF590` | intake, second cell | `0xFFFF23B5` |
| 7B | `0xFFFFF58A` | `0xFFFFF592` | intake, first cell | `0xFFFF23B4` |
| 7C | `0xFFFFF58C` | `0xFFFFF594` | exhaust bank 2 | `0xFFFF1AAE` |
| 7D | `0xFFFFF58E` | `0xFFFFF596` | exhaust bank 1 | `0xFFFF1AAC` |

Exhaust bank identity is exact through the service-0x22 pointer table. The
intake pair carries no diagnostic identity, so its bank order follows the
adjacent-pair convention of `0xFFFF2442`/`0xFFFF2443` and
`0xFFFF2440`/`0xFFFF2441` rather than a code proof.

`FUN 000CD75C` programs both cycle pairs from adjacent period bytes
`ROM8[0x8DFC] = 33` for the intake pair and `ROM8[0x8DFD] = 20` for the exhaust
pair, each multiplied by 125:

```text
CYLR7A = CYLR7B = 125 * ROM8[0x8DFC] = 4125 counts
CYLR7C = CYLR7D = 125 * ROM8[0x8DFD] = 2500 counts
```

`FUN 000BEACE` converts the two intake duty bytes with the same period byte
through signed division helper `0x00021BBC`:

```text
BFR7B = uint8[ffff23b4] * ROM8[0x8DFC] * 39 / 80
BFR7A = uint8[ffff23b5] * ROM8[0x8DFC] * 39 / 80
```

`FUN 000C2152` converts the two exhaust duty words with the exhaust period byte
through helper `0x00022508`:

```text
BFR7D = uint16[ffff1aac] * ROM8[0x8DFD] * 125 / 1024
BFR7C = uint16[ffff1aae] * ROM8[0x8DFD] * 125 / 1024
```

Dividing each result by its own cycle register gives the exact duty fractions
`uint8/256.41` for the intake bytes and `uint16/1024` for the exhaust words.
The engineering conversions are therefore code-proven:

```text
intake_percent  = uint8[ffff23b4|ffff23b5] * 39 / 100
exhaust_percent = uint16[ffff1aac|ffff1aae] * 100 / 1024
```

Byte `0xFFFF4247` bit 0 selects the computed intake path and byte `0xFFFF4251`
bit 0 selects the computed exhaust path. With the intake bit clear,
`FUN 000BEACE` drives fixed fractions while saturated engine-speed byte
`0xFFFF11EA` is positive, and zero otherwise:

```text
BFR7B = 825  = 20 percent of 4125
BFR7A = 1238 = 30 percent of 4125
```

## Exhaust duty word array

`FUN 000C2040` takes the bank index in `r4` and reaches its per-bank words
through window base `0xFFFF128C`:

| Offset | Address | Role |
|---:|---:|---|
| `0x818` | `0xFFFF1AA4 + 4*b` | longword controller state |
| `0x820` | `0xFFFF1AAC + 2*b` | published exhaust duty word |
| `0x828` | `0xFFFF1AB4 + 2*b` | previous exhaust duty word |
| `0x890` | `0xFFFF1B1C + b` | control-mode byte |
| `0x9E4` | `0xFFFF1C70 + 2*b` | duty request clamped to 1024 |

The word arrays at `0x820` and `0x828` are eight bytes apart and hold four
slots each, of which the application uses two. Dispatcher `0x000C2220` is the
only caller and invokes `FUN 000C2040` exactly twice, with `r4 = 0` and
`r4 = 1`, so the store at `0x000C213E` can only reach `0xFFFF1AAC` and
`0xFFFF1AAE`. Slots `0xFFFF1AB0` and `0xFFFF1AB2` are never written.

The service-0x22 pointer table nevertheless publishes those two slots as DIDs
`0x122D` and `0x122E`, named `VTC DTY IN B1` and `VTC DTY IN B2` by structured
Nissan diagnostics. Both DIDs therefore return the RAM initialization value for
the whole life of the image, and intake duty is not reachable through them. The
live intake command is the byte pair `0xFFFF23B4` and `0xFFFF23B5`, and its
diagnostic companion pair is `0xFFFF2440` and `0xFFFF2441`.

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

## Exhaust duty controller and disable path

Two-bank coordinator `FUN 000C21E6` runs the exhaust chain once per scheduler
pass. It calls target accessor `FUN 000BFDC0`, target conditioner
`FUN 000BFE88`, and then for each bank `b` in `0, 1` the feed-forward stage
`FUN 000C0D32`, the selected error stage, the state machine `FUN 000C1DEC`,
and the duty stage `FUN 000C2040`. After both banks it calls output converter
`FUN 000C2152` at `0xC2276`. Calibration byte `ROM8[0x8615]` bit 3 selects the
error stage: stock `0xAB` has the bit set, so `FUN 000C1152` runs and
`FUN 000C0D90` does not.

### Demand flag and bank enable

`FUN 000BFE88` writes the coolant-selected exhaust target to `0xFFFF1C90` at
`0xC055C` before conditioning it into `0xFFFF2327`. Demand flag
`0xFFFF24A7` bit 3 compares that selected target with an entry threshold and
adds hysteresis while the flag is already set:

```text
entry     = clamp_u8(ROM8[0x8DCB] + 128) = 142
hold      = ROM8[0x86F4] = 2, added to the target while bit 3 is set
bit 3     = (uint8[ffff1c90] + hold) >= entry           at 0xC05C8
release   = clamp_u8(ROM8[0x8DE6] + 128) = 144           actual-position bound
```

With bit 3 set the function ORs bits 0 and 1 into bank-enable byte
`0xFFFF1246` at `0xC0604`, clears bits 0 and 1 of `0xFFFF1C7E`, and counts
saturating cycle counters `0xFFFF1951` and `0xFFFF1952` per bank while the
corresponding `0xFFFF1AD9` bit is set, plus common counter `0xFFFF1953`.
An actual position `0xFFFF2324` or `0xFFFF2325` at or above the release bound
zeroes that bank's counter and its `0xFFFF1AD9` bit. The demand path never
clears a bank-enable bit.

With bit 3 clear the function arms `0xFFFF1AD9` bit 0 or bit 1 for every bank
whose actual position is below the release bound, increments `0xFFFF1953`
while any enable bit is set, and increments the armed per-bank counters. Once
`0xFFFF1951` and `0xFFFF1952` reach `ROM8[0x8CBC] = 1` and `0xFFFF1953` exceeds
`ROM8[0x8CC1] = 30`, it clears bit 0 at `0xC08A6`, clears bit 1 at `0xC0906`
when `0xFFFF1952` is at least the bound, and zeroes `0xFFFF1953` at `0xC0920`.
On each clear, when the matching bit of `0xFFFF1284` is set and engine-speed
byte `0xFFFF11AE` lies inside `ROM8[0x8E15] = 44 .. ROM8[0x8E14] = 80`
(2200 to 4000 RPM), the function also sets the bank bit of `0xFFFF1C7E`.

`0xFFFF1284` has no writer in the whole-program export; its bits 0 and 1 are
consumed here, in `FUN 000C1152` at `0xC1320`, and in `FUN 000C2040` at
`0xC20B2`. Their physical meaning is unresolved.

### State machine

`FUN 000C1DEC` keeps one control-mode byte per bank at window offset `0x890`,
`0xFFFF1B1C + b`. Mode 0 is off, mode 1 is active, and mode 2 is ramp-down.
Every transition reads `0xFFFF248B` bits 0 and 2 together with the bank bit of
`0xFFFF1246`:

| From | To | Condition | Store |
|---:|---:|---|---:|
| 0 | 1 | `(ffff248b & 5) == 5` and enable bit `b` set | `0xC1E32` |
| 1 | 0 | `ffff248b` bit 0 clear | `0xC1E66` |
| 1 | 2 | bit 0 set and enable bit `b` clear | `0xC1E66` |
| 2 | 0 | `uint16[ffff1aac + 2b] == 0` or bit 0 clear | `0xC1E92` |
| 2 | 1 | `(ffff248b & 5) == 5` and enable bit `b` set | `0xC1EB4` |

Mode 0 forces the controller state `P` to zero. Any other mode reads gain
curve `0x1205A` over axis `0x12850` with byte `0xFFFF2772` as the coordinate
through the byte wrapper `0x00026474` and stores the result in `0xFFFF143A`
at `0xC1EE2`. Stock curve values are `0x66, 0x66, 0x66, 0x6A, 0x71, 0x7B,
0x80, 0x80` over axis `0x32, 0x5A, 0x64, 0x6E, 0x78, 0x82, 0x87, 0xAA`, so the
gain rises from 102 to 128 counts across the coordinate. `0xFFFF2772` has no
writer in the export.

With `ROM8[0x8615]` bit 3 set, the stock branch scales the bank error word
that `FUN 000C1152` wrote to `0xFFFF1B18 + 2b`:

```text
K  = ROM16[0x9212] for bank 1, ROM16[0x9214] for bank 2, both 0x22A2 = 8866
P  = floor(floor(uint16[ffff1b18 + 2b] * K) * gain * 2 / 625)
P  = min(P, 0x04000000)
```

The quotient and remainder pass through `0x00021CE0` and `0x00021F40`. With
bit 3 clear the alternate branch forms
`(uint16[ffff1a86 + 2b] + uint16[ffff1a98 + 2b] - 65536) << 16 +
int32[ffff1a90 + 4b] - 0x08000000`, keeps only a positive result, and scales it
by `gain / 128` with the same cap. Both branches store `P` as a longword at
`0xFFFF1AA4 + 4b` at `0xC1FF4`, after clamping to `0 .. 0x04000000`.

`FUN 000C1152` reads `0xFFFF1246` at `0xC12F2` and writes the error word at
`0xC1DAC` only while the bank bit is set, as the `0 .. 65535` clamp of the
saturating sum `0x000265C4`. A disabled bank therefore keeps its previous
error word.

### Duty request and ramp-down

`FUN 000C2040` converts `P` into a duty request against battery-voltage
snapshot `0xFFFF1108`:

```text
batt = uint8[ffff1108]
req  = floor((P >> 16) * 150 / batt)
     + ((floor(((P >> 8) & 0xFF) * 150 / batt) + 128) >> 8)
req  = min(req, 1024)
uint16[ffff1c70 + 2b] = req                              at 0xC20AE
```

When the bank bit of `0xFFFF1284` is set and the bank bit of `0xFFFF1246` is
clear, it copies the published word `0xFFFF1AAC + 2b` to the previous-word
slot `0xFFFF1AB4 + 2b` at `0xC20DA`. The published word then follows the
control mode:

```text
mode 0: out = 0
mode 1: out = req
mode 2: out = req                       while enable bit b is set
        out = max(0, cur - ((prev * ROM8[0x8DE1]) >> 8))   otherwise
uint16[ffff1aac + 2b] = min(out, 1024)                     at 0xC213E
```

Stock `ROM8[0x8DE1] = 10` removes 10/256 of the previous word per pass, so a
ramp-down from 1024 reaches zero in about 130 passes while `prev` keeps
tracking the published word, and the decrement becomes zero once the previous
word is below 26 counts.

### Output and hardware fallback

`FUN 000C2152` reads `0xFFFF4251` bit 0. With the bit set it programs
`BFR7D` and `BFR7C` from the two published words as described under
"Solenoid output stage". With the bit clear it reprograms the cycle registers
`CYLR7C = CYLR7D = 2500` and drives fixed fractions while `0xFFFF11BC` is
non-zero, and zero otherwise:

```text
BFR7C = 1500 = 60 percent of 2500
BFR7D = 1250 = 50 percent of 2500
```

`FUN 000CD75C`, reached from `0x0002E81A` and `0x000306F8`, clears bit 0 at
`0xCD76E` while it programs both cycle pairs from `ROM8[0x8DFC]` and
`ROM8[0x8DFD]`.

### Diagnostic monitor

`FUN 000BFE88` and the controller do not raise codes. `FUN 0008F168`, called
from `FUN 0007C166`, is the exhaust-VTC monitor. Its front stage maintains two
timers at `0xFFFF43C3` and `0xFFFF43C2`, reloaded with `ROM8[0x8E40] = 60`
at `0x8F39E` and `0x8F428`:

```text
ffff43c3 reloads while non-zero and (ffff4184 bit 7 clear or ffff2327 == 0x80)
ffff43c2 reloads while non-zero and (ffff24aa bit 4 clear or ffff2327 != 0x80)
```

`0xFFFF424F` bit 2 diverts the monitor into reset helper `FUN 0008FC6A`, which
clears every latch, counter, and result byte listed below. The sampling stage
then writes:

| Cell | Value | Store |
|---:|---|---:|
| `0xFFFF1476` | `clamp_u8(ffff2327 - ffff2324 + 128)`, bank-1 target minus actual | `0x8F496` |
| `0xFFFF1477` | same for bank-2 actual `0xFFFF2325` | `0x8F4BC` |
| `0xFFFF16BA` | `clamp_u8(ffff11c8 - ROM8[0x831D] + 128)`, `ROM8[0x831D] = 88` | `0x8F4EC` |
| `0xFFFF16BB` | same for `0xFFFF11C9` and `ROM8[0x831E] = 88` | `0x8F524` |
| `0xFFFF1413` | staircase lookup of table `0x988A` | `0x8F57A` |
| `0xFFFF1994` | `abs(ffff2327 - ffff232d)`, target change since the retained copy | `0x8F58E` |
| `0xFFFF13A8` | `max(ffff13a8, ffff1413)` while `ffff1994 > ROM8[0x8E43] = 2`, else `ffff1413` | `0x8F5AA` |

The `0x988A` lookup is a step function rather than an interpolation. Each
index is the number of axis points at positions 1 to 7 that are at or below
the coordinate, so it runs from 0 to 7, and the value is
`ROM8[0x988A + 8*row + col]`. The row coordinate is engine-speed byte
`0xFFFF11AE` against axis `0x119F8` (`0x22, 0x24, 0x26, 0x28, 0x2A, 0x2C,
0x38, 0x40`, 1700 to 3200 RPM) and the column coordinate is coolant byte
`0xFFFF1071` against axis `0x11A08` (`0x78, 0x7D, 0x82, 0x87, 0x8C, 0x91,
0x96, 0xAA`, 70 to 120 degC). All 64 stock cells of the 8x8 block
`0x988A..0x98C9` hold `0x3C = 60`, so the evaluation window is 60 samples at
every operating point.

Each sub-monitor takes the bank index in `r4` and an enable flag in `r5`. A
zero flag runs the helper's reset path. `FUN 0008F168` computes the ten flags
before calling the five helpers for bank 0 and then for bank 1:

| Helper | Judged latch | Result byte | Indices | Codes |
|---|---|---|---|---|
| `FUN 00090086` | `0xFFFF3580` bits 0, 1 | driver status `0xFFFF850C` bits 3, 4 | `0x84`, `0x85` | P1078, P1084 position sensor path A |
| `FUN 0009018C` | `0xFFFF3581` bits 0, 1 | driver status `0xFFFF850C` bits 1, 2 | `0x86`, `0x87` | P1078, P1084 position sensor path B |
| `FUN 00090256` | `0xFFFF3582` bits 0, 1 | `0xFFFF358B` bits 0, 1 | `0xD2`, `0xD3` | P0014, P0024 rest position |
| `FUN 000904C2` | `0xFFFF3583` bits 0, 1 | `0xFFFF358C` bits 0, 1 | `0xD2`, `0xD3` | P0014, P0024 target tracking |
| `FUN 00090642` | `0xFFFF3584` bits 0, 1 | `0xFFFF358D` bits 0, 1 | `0x43`, `0x44` | P0078, P0084 magnet retarder circuit |

An enable flag is set only while the helper's judged-latch bit for that bank
is clear, so each helper judges once per reset cycle. The additional
conditions are:

- Common front gate: `0xFFFF4184` bits 7 and 6 clear, predicate `0x00025E4E`
  returns zero, and `0xFFFF2B9A == 0`.
- Position sensor paths: `0xFFFF420F` bit 1 clear, then enable mask
  `ROM8[0x186F1] = 0xF0` bits 7 and 6 for path A banks 1 and 2 and bits 5 and
  4 for path B banks 1 and 2.
- Performance codes: battery snapshot `0xFFFF1108` above `ROM8[0x8E0B] = 125`
  and at most `ROM8[0x8E08] = 203`, `0xFFFF420F` bit 0 clear, `0xFFFF4210`
  bit 7 clear, and readiness predicate `0x00025E20` clear for runtime indices
  `0x12A`, `0x60`, and `0x151`. The rest-position pair additionally needs the
  predicate clear for `0x152` and `0xFFFF24AB` bits 7 and 5 set. The
  target-tracking pair needs `0xFFFF24A8` bits 5 and 3, `0xFFFF24A9` bits 1
  and 4, the predicate clear for `0x14F` and `0x150`, `0xFFFF1413 != 0`,
  `0xFFFF2327 != 0x80`, `0xFFFF1994 <= ROM8[0x8E43]`, `0xFFFF43C3 == 0`, and
  stabilization timer `0xFFFF42E7` expired; the timer reloads with
  `ROM8[0x8396] = 10` whenever one of those conditions fails. Mask
  `ROM8[0x186FF]` bit 1 enables bank 1 and bit 0 enables bank 2 for both
  pairs.
- Magnet retarder circuit: `0xFFFF4184` bit 7 set and bit 6 clear,
  `0xFFFF41C8` bit 7 clear, `0xFFFF1108` above `0x89` and at most `0xC8`, and
  `ROM8[0x186DE]` bit 1 for bank 1 and bit 0 for bank 2. `FUN 00090642`
  returns without judging while the published duty word
  `0xFFFF1AAC + 2b` is zero.

After the helpers return, the routing stage calls `FUN 0008C2D2` to set or
`FUN 0008C348` to clear the stored-fault bit of each index from the result
bit, and calls dispatcher `FUN 0007D8B8` with the same index while the judged
latch is set. `FUN 0008C2D2` sets bit 7 of byte 1 in descriptor record
`0xFFFF5718 + 3*index` and marks bit 4 on a fresh fault; `FUN 0008C348`
clears bit 7. For P0014 and P0024 the routing also copies the three-byte
record of index `0xD2` or `0xD3` into extension slots `0x3ED`, `0x3F0`,
`0x3F3`, and `0x3F6` through block copier `0x00022558`.

`FUN 00090256` evaluates only while `0xFFFF2327 == 0x80`, timer `0xFFFF43C3`
is zero, per-bank timers `0xFFFF42F6 + b` and `0xFFFF430A + b` have expired
(reloads `ROM8[0x855D] = 10` and `ROM8[0x871F] = 10`), and bits of
`0xFFFF24AA`, `0xFFFF24AB`, and `0xFFFF2458` permit it. It compares the
rest-position byte `0xFFFF16BA + b` with the window
`128 - ROM8[0x8952] .. 128 + ROM8[0x8951]`, both 34, and sets the bank bit of
`0xFFFF358B` or `0xFFFF3582` when the byte is outside it and the matching
`0xFFFF43C0 + b` or `0xFFFF43B6 + b` timer has expired. The source bytes
`0xFFFF11C8` and `0xFFFF11C9` have no direct writer in the export and are read
only by `FUN 0008F168`, `FUN 00090884`, and `FUN 000BFAD4`.

`FUN 000904C2` counts `0xFFFF1998 + b` while `0xFFFF84C3` bit 7 is set,
zeroes it while `0xFFFF1994` exceeds `ROM8[0x8E43] = 2`, and marks the
evaluation as running in `0xFFFF359A`. While the counter is at most
`0xFFFF13A8`, a gap `0xFFFF1476 + b` inside `128 - ROM8[0x894F] .. 128 +
ROM8[0x894D]`, both 34, latches the bank bit of `0xFFFF3598`; a gap outside it
sets the pending bit in `0xFFFF1478` unless the pass bit is already latched.
When the counter exceeds `0xFFFF13A8`, a latched pass bit sets `0xFFFF2D19`
and clears the stored code through `FUN 0008C348` with index `0xD2` for bank 1
and `0xD3` for bank 2, while a pending bit without a pass sets the bank bit of
`0xFFFF358C` and `0xFFFF3583`.

### Disable path

The calibration-only path keeps every exhaust target below the entry
threshold. With surfaces `0xB33A` and `0xB2FA` at `0x80` and correction
`0xAB4A` at `0x80`, `0xFFFF1C90` stays at 128, bit 3 of `0xFFFF24A7` is never
set, `0xFFFF1246` keeps bits 0 and 1 clear, both control-mode bytes stay in
mode 0, `P` and the published duty words stay at zero, and `BFR7C` and
`BFR7D` hold zero. The conditioned target `0xFFFF2327` sits at `0x80`.

On that path the monitor behaves as follows:

- The target-tracking pair is never enabled, because it requires
  `0xFFFF2327 != 0x80`, so `FUN 000904C2` runs its reset path.
- The magnet retarder circuit pair is never judged, because `FUN 00090642`
  returns while the published duty word is zero.
- The rest-position pair is enabled by the neutral target and compares
  `0xFFFF16BA` and `0xFFFF16BB` with the `128 +/- 34` window, which holds
  while `0xFFFF11C8` and `0xFFFF11C9` stay within `88 +/- 34` counts. The
  physical source of that pair is not established, so this is the one
  P0014/P0024 path the calibration change leaves active.
- The position sensor paths judge driver status `0xFFFF850C` independently of
  the target and are not affected by the calibration change.

Executable alternatives, such as forcing mode 0 in `FUN 000C1DEC` or clearing
`0xFFFF4251` bit 0, replace instruction bytes and therefore require the
`tools/sh-elf-run` gate before any image built from them is eligible for
hardware.

### Evidence boundary of the controller

The state machine, the arithmetic, the stores, and the descriptor routing are
exact code facts read from the whole-program export and the headless
listings. The following remain unresolved:

- the writers and physical meaning of `0xFFFF1284` and `0xFFFF248B` bits 0
  and 2, which are consumed as enable inputs;
- the producer of gain coordinate `0xFFFF2772`;
- the producer and physical meaning of rest-position sources `0xFFFF11C8` and
  `0xFFFF11C9`;
- the meaning of `0xFFFF84C3` bit 7 as the sample-count condition of
  `FUN 000904C2`.

## Evidence boundary

Static DID and DTC paths establish the intake/exhaust target distinction even
where downstream conditioning makes a map replay differ from the published
byte. The capture does not establish the candidate degree-per-byte conversion,
electrical valve command, or physical camshaft angle at the crankshaft.

CAN telemetry schema 2 names the two sources `intake_cvtc_target_raw` and
`exhaust_cvtc_target_raw`, matching their recovered common-target roles. The
generated profile CRC binds those names and sources to the host decoder.
