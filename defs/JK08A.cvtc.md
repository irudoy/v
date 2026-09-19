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
`raw*0.5-64 degCA`. Identity and bank are exact, and the code path under
"Cam edge phase bytes" proves the latter: one count of the actual bytes is
0.5 crank degrees of cam edge phase relative to the learned rest edge. The
monitor forms its gap `0xFFFF1476 + b` as target minus actual in the same raw
units at `0x8F496`, so target `0xFFFF2327` and the surfaces behind it share
the conversion. The definition rows of `0xB33A`, `0xB2FA`, `0xAB4A`, and the
standstill override scalar `0x8E36` in `defs/JK08A.findings.csv` carry this
conversion at code confidence; the crank-wheel origin of the absolute angle
remains open.

The intake pair `0xFFFF2442`/`0xFFFF2443` (`0xFFFF2442` is DID `0x1135`)
shares the unit. The channel-1A handlers form the intake edge phases
`0xFFFF22CC`/`0xFFFF22CD` with the same divider and the same 20-count selector
step in 0.5 crank degrees, `FUN 000BD9F0` centers each actual byte on its rest
edge, and `FUN 0004D2A6` subtracts the actual bytes from common target
`0xFFFF2326` in raw units. The definition rows of `0xB43A`, `0xB53A`, and
`0xAB5A` carry `(x-128)*0.5` crank degrees at code confidence; the intake sign
is advance positive.

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

Byte `0xFFFF4247` bit 0 selects the fixed intake test fractions and byte
`0xFFFF4251` bit 0 the fixed exhaust test fractions; both bits are clear in
normal operation and the computed words are driven. With the intake bit set
(`tst #1; bt` at `0xBEAE0`), `FUN 000BEACE` drives fixed fractions while
saturated engine-speed byte `0xFFFF11EA` is positive, and zero otherwise:

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
Timing Map` with `(raw-128)*0.5 deg`, and the same conversion is code-proven
for JK08A: the surfaces feed target `0xFFFF2327`, monitor `FUN 0008F168`
compares that target in raw units with the actual bytes `0xFFFF2324` and
`0xFFFF2325`, and `FUN 000BFC2E` writes those bytes in counts of 0.5 crank
degrees relative to the learned rest edge (see "Cam edge phase bytes"). Stock
0xB2FA is neutral 128 throughout. Its cold/fallback name describes the exact
coolant-selector role without asserting a catalog title.

The dashboard recordings of 2026-09-17 (`tools/logs/mlg_relation_audit.py`)
show the closed loop on the running engine. With a Map 3 image whose surfaces
are neutral, both actual bytes stay within two counts of a target that has
been unchanged for 100 records in 98 percent of 83,229 and 34,026 samples per
bank. With the stock Map 1 image the same share is 77 to 78 percent: at 700 to
1300 RPM the actual bytes exceed the target of 140 by 9 to 45 counts while
the duty words hold 400 to 700 of 1024, so the stock retard request overshoots
at low speed rather than lagging.

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
immediate map lookup or be replaced with neutral `0x80`. The exhaust stages
are listed under "Standstill override and slew" below.

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

### Standstill override and slew

`FUN 000BFE88` conditions the coolant-selected exhaust byte before the demand
comparison. Three hysteresis flags precede a map-independent override:

```text
ffff24ab bit 0 = uint8[ffff11ae] + (bit 0 ? ROM8[0x86E1] = 4 : 0) >= ROM8[0x8E3B] = 36
                 engine speed at or above 1800 RPM, released below 1600 RPM    stored at 0xBFEE4
ffff24ab bit 1 = uint8[ffff11ae] - (bit 1 ? ROM8[0x86E1] = 4 : 0) <= ROM8[0x8E3A] = 80
                 engine speed at or below 4000 RPM, released above 4200 RPM    stored at 0xBFF14
ffff24ac bit 7 = uint8[ffff110e] - (bit 7 ? ROM8[0x86E8] = 1 : 0) <= ROM8[0x8E3C] = 2
                 coarse vehicle speed at or below 2 counts, released above 3   stored at 0xBFF4E
ffff246c bit 1 = ffff248b bit 2 && ffff24ab bit 0 && ffff24ab bit 1
                 && ffff24ac bit 7 && ffff244f bit 2                          stored at 0xC017E
```

Bit 1 of `0xFFFF24AB` and bit 7 of `0xFFFF24AC` come from comparator
`FUN 000259D0`, which subtracts the hysteresis offset only while the flag is
already set. The override stage at `0xC018E..0xC01F4` then selects the byte
stored to `0xFFFF137E`:

```text
ffff248b bit 2 clear              latch ffff2478 bit 4 cleared at 0xC018C, byte = map
ffff246c bit 1 set, latch clear   byte = clamp_u8(ROM8[0x8E36] + 128) = 168 (+20 degCA);
                                  with ffff24d3 bit 4 set the latch is set at 0xC01C8
                                  instead and byte = 128
ffff246f bit 1 set                byte = 128 on the pass after the predicate falls
latch set                         byte = previous ffff137e
otherwise                         byte = coolant-selected map value
```

`0xFFFF246F` is the scheduler's prior-cycle copy of `0xFFFF246C`. The
override commands 20 degrees of exhaust retard whenever the engine passes
1800 RPM with the vehicle at rest while the operational enable is set,
independently of surfaces `0xB33A`, `0xB2FA`, and `0xAB4A`; it ends when the
engine speed leaves the window, the vehicle moves, or `0xFFFF244F` bit 2
clears. `0xFFFF24D3` bit 4 is written at `0xC0A0A` from `0xFFFF247E` bit 0
together with the published target above 128 or counter `0xFFFF1C74` at most
2; `0xFFFF247E` bit 0 is set at `0xC098A` when countdown `0xFFFF25E7` reads
zero, and the countdown is reloaded with `ROM8[0x8CBF] = 50` at `0xBFFBC`
while byte `0xFFFF1240` or `0xFFFF1241` lies outside `+/- ROM8[0x8E16] = 6`.

After the limiter for bytes at or above `ROM8[0x8DE4] = 190` (counter
`0xFFFF1954`, bound `ROM8[0x8E1E] = 120`), the slew stage at
`0xC045A..0xC04B4` bounds the increase of the byte over the previous
`0xFFFF1C90`. The step, stored to `0xFFFF1995`, is `ROM8[0x830A] = 4` times
`0xFFFF11C0` while `0xFFFF2482` bit 1 marks a byte at or above the
previous-pass value `0xFFFF125A`, and `ROM8[0x84F3] = 20` times `0xFFFF11C0`
otherwise. The 2026-09-17 captures show the override rising by 4 counts per
scheduler tick, which corresponds to `0xFFFF11C0 = 1`.

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

While bit 3 is clear and either enable bit is still set, the published
target is held at `clamp_u8(ROM8[0x8DCB] - ROM8[0x86F4] + 128) = 140` at
`0xC07EA..0xC081E`; once both enable bits are clear it becomes
`clamp_u8(ROM8[0x8E38] + 128) = 128` at `0xC0820`. This hold is the +6 degCA
plateau that follows each override release in the 2026-09-17 captures.

`0xFFFF1284` is the previous-pass snapshot of `0xFFFF1246`. Scheduler
`FUN 00020DFE` copies the `0x3E`-byte block `0xFFFF120E..0xFFFF124B` to
`0xFFFF124C..0xFFFF1289` through `FUN 00022558` at `0x20F7C`, so bits 0 and 1
hold the bank-enable state of the previous scheduler pass. They are consumed
here, in `FUN 000C1152` at `0xC1320`, and in `FUN 000C2040` at `0xC20B2`,
where a set snapshot bit beside a clear current bit marks the pass on which
the enable falls.

### Enable bits of `0xFFFF248B`

Enable coordinator `FUN 000BF630` writes bits 0 and 2 of `0xFFFF248B`, the
two inputs the state machine reads on every transition. It first refreshes
hysteresis flags from the scheduler snapshots, adding the offset while the
flag is already set:

```text
ffff24a9 bit 3 = (ffff1071 + 3)  >  ROM8[0x8E03] = 106      raw coolant
ffff24a9 bit 6 = (ffff1071 - 3)  <= ROM8[0x8E00] = 170      raw coolant
ffff24a8 bit 4 = (ffff11b2 + 16) >= ROM8[0x8DE9] = 72       900 RPM, 700 release
ffff24a8 bit 2 = (ffff11b2 + 16) >= ROM8[0x8DEC] = 72       900 RPM, 700 release
ffff24aa bit 5 = (ffff110e + ROM8[0x86DE] = 1) >= ROM8[0x8E0F] = 5   vehicle speed
ffff24aa bit 7 = (ffff110e - 1)  <= ROM8[0x8E0D] = 48       low vehicle speed
ffff246c bit 3 = (ffff2772 + 3)  >= ROM8[0x8DFF] = 110      oil temperature
ffff246c bit 2 = (ffff24a9 & 0x48) == 0x48                  coolant window, 0xBF864
```

Bit 0 of `0xFFFF248B`, stored at `0xBF852`, is the electrical enable. It
requires battery snapshot `0xFFFF1108` above `ROM8[0x8E0A] = 125` and at most
`ROM8[0x8E07] = 200`, driver status `0xFFFF850C` bits 5 and 6 clear (the
edge-count anomaly flags of `FUN 000C22DC`, see "Driver status and edge-count
monitor"), a zero result from crank and cam sensor fault predicate
`FUN 00025E4E` (stored P0335, P0340, or P0345), `0xFFFF244F` bit 5 set, and
the stored-fault bit of `FUN 00025E20` clear for the P0014/P0024 extension
slots `0x14F..0x152` and the P0078/P0084 records `0x43` and `0x44`.
`ROM8[0x8616]` bit 0 is the oil-temperature sensor configuration bit: the test
at `0xBF80E` is `tst #1; bt 0xBF842`, which skips the block while the bit is
clear, and stock JK08A holds `0x01`, so the enable also requires the P0197,
P0198, and P0196 records `0xDD`, `0xDE`, and `0xE4` clear.

Two latches in `0xFFFF248C` follow the window flags against their prior-cycle
copies in `0xFFFF246F`, which the scheduler refreshes at `0x2105A`. Bit 6 sets
at `0xBF880` on the rising edge of coolant-window bit `0xFFFF246C` bit 2 while
`0xFFFF2458` bit 5 is clear and clears at `0xBF884` while that bit is set.
Bit 7 sets at `0xBF8C6` on the rising edge of oil-temperature bit
`0xFFFF246C` bit 3 and clears at `0xBF894` while `0xFFFF2458` bit 5 and
`0xFFFF24AA` bit 7 are both set.

Bit 2 of `0xFFFF248B`, stored at `0xBF99A`, is the operating enable:

```text
bit 2 = bit 0
    and ffff2458 bit 5 clear
    and ((ffff246c bit 2 and ffff248c bit 6 clear) or ffff249c bit 6)
    and ((ffff24aa bit 5 or ffff2468 bit 3) ? ffff24a8 bit 4 : ffff24a8 bit 2)
    and ffff41be bit 6, ffff41d1 bit 7, ffff41d0 bit 0 clear
    and ffff2f64 bits 0 and 1 clear
    and ffff14b8 bits 0 and 1 clear
    and (ffff246c bit 3 and ffff248c bit 7 clear)      with ROM8[0x8616] bit 0 set (stock 0x01)
```

Every term is a code fact. The test of `ROM8[0x8616]` bit 0 at `0xBF974`
passes the oil-temperature term while the bit is clear; with the stock value
the term requires oil-temperature flag `0xFFFF246C` bit 3 set and latch
`0xFFFF248C` bit 7 clear, so the operating enable waits, after the oil
temperature has reached raw 110 (60 degC), for the first pass on which
`0xFFFF2458` bit 5 and low-speed flag `0xFFFF24AA` bit 7 are both set.
`FUN 000BF630` is the only writer of `0xFFFF248C` bits 6 and 7: the other
writers of the byte in the export, `FUN 0004C4CC` and `FUN 0004C9D2` (bits 4
and 5), `FUN 0004C536` (bits 0 to 2), and `FUN 0004C6BA` (bit 3), leave both
latches alone, so bit 6 stays set from the rising edge of the coolant window
until `0xFFFF2458` bit 5 clears it.

`0xFFFF2458` bit 5 is the scheduled copy of `0xFFFF2459` bit 5, which status
packer `FUN 0002E0D4` publishes as DID `0x1302` bit 0, `CLSD THL POS`: the
idle position that the ECM computes from the accelerator pedal position sensor
signal. The operating enable therefore holds only while the pedal is off its
idle position. A coolant window that opens with the pedal applied sets latch
bit 6 and blocks the coolant term until the first pass with the pedal at idle,
and oil-temperature latch bit 7 releases on the first pass with the pedal at
idle while low-speed flag `0xFFFF24AA` bit 7 is set.

### Inhibit terms of the operating enable

The five inhibit terms of bit 2 resolve to two attribute-class fault polls and
three terms that stock JK08A never sets.

- `0xFFFF41BE` bit 6 is written only by `FUN 0008C24E` (`0x8C266` set,
  `0x8C268` clear) from `FUN 0008C396(0x0100)`. The poll walks all `0x129`
  descriptor records and returns 1 when any record has a mask bit set in its
  attribute word (pointer table `0x1A14C`) and bit 7 set in byte 1 of its
  runtime record `0xFFFF5718 + 3*index`, the stored-fault bit of
  `FUN 0008C2D2`. Attribute bit 8 is carried by 36 stock records: twenty
  `P0605` records and `P0120`, `P0643`, `P1123`, `P1127`, `P1129`, `P1233`
  (two), `P1236`, `P1238`, `P1290`, `P2100`, `P2101` (two), `P2103`, `P2118`,
  and `P2119`.
- `0xFFFF41D1` bit 7 is written only by `FUN 0008C272` (`0x8C28C`), which sets
  bits 7, 2, and 0 together while event byte `0xFFFF48E0` is nonzero.
  `FUN 0008C2D2` sets that byte at `0x8C326` when the record it stores has
  attribute bit 10, and stage 3 of summary pass `FUN 0008C65C` clears it once
  `FUN 0008C396(0x0400)` finds no stored record of the class. Attribute bit 10
  is carried by the six mass-airflow records `P0101`, `P0102`, `P0103`
  (indices `0xBA..0xBC`) and `P010B`, `P010C`, `P010D` (indices `0x07..0x09`).
- `0xFFFF41D0` bit 0 has no setter in the image. The writers of the byte
  handle bits 1 to 7 (`FUN 00056BD0` bit 1, `FUN 000473AC` bits 2 and 3,
  `FUN 000A40F4` and `FUN 000A454E` bits 4 and 5, `FUN 000A2094`,
  `FUN 000A2254`, and `FUN 000A3BA8` bit 6, `FUN 000A3F96` and
  `FUN 000A407A` bit 7), so the term is inert.
- `0xFFFF2F64` bits 0 and 1 are the per-bank judged flags of `FUN 00090D54`,
  the `P1080`/`P1086` path (records `0x88` and `0x89`). With `0xFFFF4184`
  bit 7 and `0xFFFF24AB` bit 3 set it flags a cam edge phase snapshot
  `0xFFFF11C8 + b` at or below `ROM8[0x8E32] = 254` once timer
  `0xFFFF25F0 + b` has expired and reports through `FUN 0007D8B8`. Family
  entry `FUN 00090E5E` calls it only under `ROM8[0x186F2]` bits 5 and 4
  (`0x90EC6`, `0x90ED6`); the stock byte is `0x07`, so the function never runs
  and the bits stay clear.
- `0xFFFF14B8` bits 0 and 1 are the per-bank flags of `FUN 00090BD2`, a third
  `P0014`/`P0024` path. With `0xFFFF24A7` bit 4 set, a neutral conditioned
  target `0xFFFF2327`, the bank bit of `0xFFFF48DF`, and a zero duty word it
  flags a cam edge phase that exceeds the high byte of reference word
  `0xFFFF5578 + 2b` by at least `ROM8[0x895E] = 254`, and once timer
  `0xFFFF2539 + b` (`ROM8[0x88D2] = 5`) has expired it stores record `0xD2` or
  `0xD3` through `FUN 0008C2D2` and `FUN 0007D8B8`. `FUN 00090E5E` calls it
  only under `ROM8[0x186F1]` bits 3 and 2 (`0x90E80`, `0x90E90`); the stock
  byte is `0xF0`, so the function never runs and the bits stay clear.

`FUN 00090E02`, which `FUN 00090E5E` calls while `0xFFFF424F` bit 2 is set,
clears both flag pairs and reloads their timers. `FUN 00090E5E` also forms
`0xFFFF24AB` bit 3 as engine-speed byte `0xFFFF11B2` at least
`ROM8[0x8E33] = 0`, which holds on every pass. On stock JK08A the inhibit
terms therefore reduce to a stored fault of the attribute-bit-8 group or of
the mass-airflow group.

`0xFFFF249C` bit 6 is written by `FUN 0002E466`, reached from `FUN 0002E66C`
and `FUN 000CA79E`. It sets at `0x2E5EC` while service-0x30 Output Control
IOLID `0x1D` is active (`0xFFFF99C7` bit 4), `0xFFFF248B` bit 0 and
`0xFFFF244F` bit 1 are set, vehicle-speed byte `0xFFFF110E` is at most
`ROM8[0x89F1] = 2`, and raw coolant `0xFFFF1071` lies in `ROM8[0x89F3] = 110
.. ROM8[0x89F2] = 170`; the same path stores the requested offset
`0xFFFF1706 = clamp(int8(0xFFFF9940), ROM8[0x873E] = -20 .. ROM8[0x873F] =
20)` at `0x2E612`, and the bit clears at `0x2E61C` otherwise. `0xFFFF9940` is
the IOLID `0x1D` value byte of handler `FUN 00030C4C` (`0xFFFF9923 + n`) and
`0xFFFF99C7` bit 4 its active flag; `FUN 000BFE88` reads the offset at
`0xC04DA` while the bit is set and adds it to the exhaust target. The bit is
therefore the CONSULT active-test request for the exhaust cam at standstill,
and it bypasses the coolant-window term for the duration of the test. The
VTC channel enabled by `0xFFFF248B` bit 1 runs through the same function
with IOLIDs `0x19` and `0x1A` (`0xFFFF41FA` bit 0, `0xFFFF41FB` bit 7,
offsets `0xFFFF1704` and `0xFFFF1705`).

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
gain rises from 102 to 128 counts across the coordinate. `0xFFFF2772` is the
previous-pass snapshot of engine-oil-temperature byte `0xFFFF2876`, the source
of DID `0x111F`: scheduler `FUN 00020DFE` copies the `0x104`-byte block
`0xFFFF277E..0xFFFF2881` to `0xFFFF267A..0xFFFF277D` at `0x20FCC`.
`ROM8[0x8616]` bit 0 selects the sensor path of producer `FUN 0003EB84`
(`tst #1; bf` at `0x3EB96`): with the bit set, as in stock JK08A, the function
filters ADC sample `0xFFFF1D5C` into word `0xFFFF1F92` and raw byte
`0xFFFF117B`, converts it through curve `0x12C6E` into `0xFFFF1F94`, and
publishes it in `0xFFFF2876`, directly while `0xFFFF4183` bit 7 is set and
otherwise rising at once and falling only after a drop of two or more counts;
a raw byte outside `3..241` or a stored P0197, P0198, or P0196 record sets
`0xFFFF4182` bit 7 and publishes `0xFF`. With the bit clear the function
writes zero at `0x3ECAE`. The stock coordinate therefore follows the engine
oil temperature, and the gain is 102 up to raw 100 (50 degC) and 128 from raw
135 (85 degC).

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

`FUN 000C2152` reads `0xFFFF4251` bit 0 (`tst #1; bf 0xC21B4` at `0xC215C`).
With the bit clear, the state after every reset, it programs `BFR7D` and
`BFR7C` from the two published words as described under "Solenoid output
stage". With the bit set it reprograms the cycle registers `CYLR7C = CYLR7D
= 2500` and drives fixed fractions while `0xFFFF11BC` is non-zero, and zero
otherwise:

```text
BFR7C = 1500 = 60 percent of 2500
BFR7D = 1250 = 50 percent of 2500
```

`FUN 000CD75C`, reached from `0x0002E81A` and `0x000306F8`, clears bit 0 at
`0xCD76E` while it programs both cycle pairs from `ROM8[0x8DFC]` and
`ROM8[0x8DFD]`, and zeroes the checksum state `0xFFFF30F8`, `0xFFFF3084`, and
`0xFFFF30B0` with `0xFFFF41DE` bit 2. The only setter is memory task
`FUN 000CD85C`, which scheduler task `FUN 0002E8D2` (periodic list entry
`0x21AA0`) calls with request byte `0xFFFF40BE` while pending flag
`0xFFFF41DE` bit 0 is set (`tst #1; bt exit` at `0x2E8F2`): request 3
executes `or #1` into `0xFFFF4251` at `0xCDD4E` (`cmp/eq #3` at `0xCDD40`),
and the task clears the pending flag when a pass completes. Requests 1 and 2
are the ROM sum and compare passes (`0xFFFF3324`, `0xFFFF31F8` against
`ROM32[0x96D4]`, `ROM32[0x96DC]`, `ROM16[0x5FFE]`, `ROM16[0x6EFE]`). The
request byte is the sub-function byte `0xFFFF8005` of manufacturer
diagnostic service `0xA0`: dispatcher `FUN 0002F928` routes the service to
handler `FUN 000306F8` at `0x2FA78`, and the handler copies an accepted code
into `0xFFFF40BE` (`0x309CA` for codes 1, 2, and 3) and sets the pending
flag at `0x309D6`; initialization path `FUN 0002E81A` resets the byte to
zero at `0x2E890`. The fixed 60/50 percent fractions are therefore an actuator-test state
requested over the diagnostic link, and the computed duty path is the
default after every reset.

### Cam edge phase bytes

Rest-position sources `0xFFFF11C8` and `0xFFFF11C9` are previous-pass
snapshots of the exhaust-cam edge phase bytes `0xFFFF1200` and `0xFFFF1201`,
copied by scheduler `FUN 00020DFE` in the `0x38`-byte block
`0xFFFF11D4..0xFFFF120B -> 0xFFFF119C..0xFFFF11D3` at `0x20F6C`. The phase
bytes are written by the ATU-II channel-4 input-capture handlers.
`FUN 000C2D76`, with its continuation body `FUN 000C2DE0`, serves IMI4D through
interrupt pointer entry `0x20210` and writes the bank-1 byte `0xFFFF1200` at
`0xC2E60`; `FUN 000C2C58` serves IMI4C through entry `0x2020C` and writes the
bank-2 byte `0xFFFF1201` at `0xC2D2C`. Each handler clears its IMF flag in
TSR3 at `0xFFFFF480` (masks `0x7EFF` and `0x7F7F`), reads capture register
GR4D at `0xFFFFF4C8` or GR4C at `0xFFFFF4C6`, and forms the phase as

```text
interval = (GRx - uint16[ffff158a]) & 0xFFFF                 crank reference count
segment  = ffff13b2 > 7 ? ffff13b2 - 5 : ffff13b2 == 7 ? 0 : ffff13b2 + 5
phase    = 20 * segment + floor(20 * interval / uint16[ffff22bc])
```

through signed divider `0x00021BBC`. The bank-1 handler updates only while
cylinder index `0xFFFF11DE` is 1, 3, or 5 and driver status `0xFFFF850C`
bit 5 is clear; the bank-2 handler only while the index is 2, 4, or 6 and
bit 6 is clear. Each update first shifts the two previous values into
`0xFFFF1202` and `0xFFFF1204` for bank 1 or `0xFFFF1203` and `0xFFFF1205` for
bank 2, so the six bytes hold the last three edges per bank. The interval
words are also stored at `0xFFFF1A80` and `0xFFFF1A82` and the segment at
`0xFFFF16F2` through window base `0xFFFF128C`.

One phase unit is 0.5 degrees of crankshaft rotation. `FUN 0002718A` writes
`TCR1A = 5` at `0x271EC` and `TCR4 = 5` at `0x272C0`, so channels 1A and 4
count `phi'/32`, and zeroes `TCNT1A` at `0x271BE` and `TCNT4` at `0x272A4`
while `TSTR1` is zero; `FUN 000274AC` writes `PSCR1 = 1` (`phi' = Pphi/2 =
10 MHz`) and starts both counters together with `TSTR1 = 0x73` at `0x274C0`.
The channel-4 captures and crank reference `0xFFFF158A` (the GR1E or GR1F
capture stored by `FUN 0002B768` at `0x2B7CC`) therefore count the same
3.2 us clock and their difference is a time. `FUN 0002B768` forms the
engine-event timestamp from `TCNT0` (`phi'`) and the capture, divides the
wrap-corrected difference to the previous event by 32 into `0xFFFF11FC`
(3.2 us units) and by 12 into `0xFFFF22BC`. `FUN 00038272` publishes
`0xFFFF1196 = 32000000 / 0xFFFF11FC` at `0x38282`, and `0xFFFF1196` is the
`RPM * 5.12` engine-speed word (`0xFFFF11E6 = 0xFFFF1196 >> 8` in RPM/50),
so the interval is `6250000 / RPM` counts, one third of a revolution or 120
crank degrees, and `0xFFFF22BC` is 10 crank degrees, one tooth of the crank
wheel. `20 * interval / 0xFFFF22BC` is the crank angle of the cam edge after
the last crank reference in 0.5-degree units, and `20 * segment` places that
reference `10 * segment` degrees after the event origin. The stock rest
values `ROM8[0x831D] = ROM8[0x831E] = 88` are 44 crank degrees after the
event origin, and the phase reaches at most 240 units.

The intake cams use the same arithmetic on ATU-II channel 1A. `FUN 0002A5CC`
serves the bank-1 capture GR1F at `0xFFFFF44E` and `FUN 0002A36A` the bank-2
capture GR1E at `0xFFFFF44C`. Each handler stores the interval to crank
reference `0xFFFF158A` (`0xFFFF22C8` at `0x2A6D0`, `0xFFFF22CA` at `0x2A41E`),
divides `20 * interval` by `0xFFFF22BC` through the same signed divider
`0x00021BBC` (`0x2A6F4`, `0x2A442`), and forms the running phase

```text
phase = 20 * ffff13b2 + floor(20 * interval / uint16[ffff22bc]) - 60    ffff13b2 < 8
phase = 20 * ffff13b2 + floor(20 * interval / uint16[ffff22bc]) - 20    ffff13b2 >= 8
```

clamped at zero, into `0xFFFF22D2` (`0x2A746`) or `0xFFFF22D3` (`0x2A47E`).
The running byte becomes the edge phase `0xFFFF22CC` at `0x2A75E` while event
state `0xFFFF13C8` is 2, 4, or 6, and `0xFFFF22CD` at `0x2A496` while it is
1, 3, or 5. Both passes require `0xFFFF84FF` bit 7 set and their edge count
(`0xFFFF1391`, `0xFFFF1390`) equal to 1, are gated by bit 7 of status bytes
`0xFFFF8509` and `0xFFFF8504`, and shift the previous accepted values into
`0xFFFF22CE`/`0xFFFF22D0` and `0xFFFF22CF`/`0xFFFF22D1` on every processed
capture. One count is therefore 0.5 crank degrees on the intake phase axis as
well; the selector offsets differ from the exhaust segment mapping, so the two
axes have different origins. The stock rest values
`ROM8[0x831C] = ROM8[0x8321] = 140` are the phase of selector 8 at zero
interval.

`FUN 000BD9F0` publishes the actual intake bytes at `0xBDA34` as

```text
uint8[ffff2442] = clamp_u8(0x80 + ffff4799 - ffff22cc)
uint8[ffff2443] = clamp_u8(0x80 + ffff479a - ffff22cd)
```

or neutral `0x80` under the hardware-control mask. An edge earlier than the
rest edge reads above `0x80`, so the intake sign is advance positive, the
opposite of the exhaust pair. `FUN 0004D2A6` subtracts these bytes from
common target `0xFFFF2326` in raw units at `0x4D31E`, `0x4D32A`, and
`0x4D356`, so the target and the surfaces `0xB43A`, `0xB53A`, and `0xAB5A`
carry the same 0.5 crank degrees per count.

`FUN 000BFC2E`, called from coordinator `FUN 000C21E6` at `0xC220C` and
`0xC2212` with the channel in `r4`, turns the phase into the published
actual-position bytes `0xFFFF2324` and `0xFFFF2325` (DID `0x1164` and
`0x1165`). It returns at `0xBFC50` while `0xFFFF850C` bit `5 + ch` is set.
Otherwise it forms the deviations of the last three edges from the learned
rest edge `0xFFFF479B + ch`:

```text
d0   = clamp_u8(ffff11c8[ch] - ffff479b[ch] + 128)          -> ffff1c88 + ch
d1   = clamp_u8(ffff11ca[ch] - ffff479b[ch] + 128)          -> ffff1c8a + ch
d2   = clamp_u8(ffff11cc[ch] - ffff479b[ch] + 128)          -> ffff1c8c + ch
calc = (d0 + d1 + d2) / 3           ROM8[0x8615] bit 1 set (stock 0xAB)
calc = d0                           otherwise
x    = interp(0x12F7E over axis 0x12F6E by ffff11ae)         -> ffff160e
out  = 128 + round((x * (calc - 128) + (256 - x) * (ffff232a[ch] - 128)) / 256)
uint8[ffff2324 + ch] = clamp_u8(out)                         at 0xBFDAE
```

`0xFFFF11CA..0xFFFF11CD` are the scheduler snapshots of the older edges
`0xFFFF1202..0xFFFF1205`, and `0xFFFF232A` and `0xFFFF232B` are the
previous-pass copies of the two output bytes made at `0x21310`. Curve
`0x12F7E` holds `0xCD` at 800 RPM and `0xFF` from 1600 RPM over axis
`0x12F6E` (`0x10..0x80` RPM/50), so the output is a first-order filter that
passes 255/256 of each new sample above 1600 RPM. One count of DID `0x1164`
is therefore 0.5 crank degrees of the exhaust-cam edge relative to the
learned rest edge, which is the community definition `raw * 0.5 - 64`
degrees of crankshaft.

`FUN 000BFAD4`, called from the same coordinator at `0xC21FE`, learns the rest
edge. While `0xFFFF246B` bit 4 is set it forms `0xFFFF1376 = 128 +
clamp(ROM8[0x831D] - 0xFFFF11C8, -40..40)` at `0xBFB4A` and `0xFFFF1377` from
`ROM8[0x831E]` and `0xFFFF11C9` at `0xBFB98`, with `ROM8[0x8834] = 40`, and
sets `0xFFFF2495` bit 3 when a deviation reaches the bound; while bit 4 is
clear it clears that flag instead. It then stores the learned edges
`0xFFFF479B = clamp_u8(ROM8[0x831D] - 0xFFFF1376 + 128)` at `0xBFBF8` and
`0xFFFF479C` at `0xBFC1C` and sets `0xFFFF2475` bit 1 at `0xBFC20` when
`0xFFFF2495` bit 3 is clear, `0xFFFF24A8` bits 7 and 4 are set, and either
`0xFFFF246B` bit 4 has just fallen (prior-cycle `0xFFFF246E` bit 4 set) or it
is set with `0xFFFF2535 == 0`. Within the +/-40 band the learned edge equals
the measured phase, so the actual-position bytes read 128 at the learned rest
while the P0014/P0024 rest window `88 +/- 34` of `FUN 00090256` applies to
the raw phase snapshot. `FUN 000BCED0` initializes `0xFFFF1376`,
`0xFFFF1377`, `0xFFFF2324`, and `0xFFFF2325` to `0x80`.

`FUN 000BF9B0`, called from the same coordinator, writes both learning gates.
`0xFFFF24A8` bit 7 (`0xBFA3C` set, `0xBFA8A` clear) requires electrical enable
`0xFFFF248B` bit 0, coolant flags `0xFFFF24A9` bits 3 and 6, driver status
`0xFFFF850C` bits 5 and 6 clear, a zero result of `FUN 00025E4E`, inhibit
`0xFFFF41BE` bit 6 clear, and `0xFFFF24AA` bit 0, which comparator
`0x000259D0` holds while engine-speed byte `0xFFFF11B2` is at most
`ROM8[0x8E1B] = 80` (1000 RPM, release above 1200 RPM). With that gate set,
`0xFFFF246B` bit 4 sets while the conditioned target `0xFFFF2327` is `0x80`,
both duty words `0xFFFF1AAC` and `0xFFFF1AAE` are zero, and timer `0xFFFF2536`
has expired; while that timer runs the bit is clear and only `0xFFFF2535`
reloads from `ROM8[0x883D] = 10`. With the gate clear, the target off neutral,
or a duty word nonzero, the bit clears and both timers reload, `0xFFFF2536`
from `ROM8[0x883F] = 10`. A set bit leaves `0xFFFF2535` running, which is the
settle delay of the learner.

### Driver status and edge-count monitor

`FUN 000C22DC`, called from engine-event driver `FUN 00029588`, maintains
driver status `0xFFFF850C` and indicator byte `0xFFFF850D` from the per-bank
edge counters of the capture handlers: `FUN 000C2DE0` increments `0xFFFF4072`
with saturation at `0xC2E8E` on every bank-1 edge while `0xFFFF4120` bit 0 or
`0xFFFF4121` bit 0 is set, and `FUN 000C2C58` increments `0xFFFF4073` at
`0xC2D5A` for bank 2 with bit 1 of the same bytes. `0xFFFF4120` and
`0xFFFF4121` are the scheduler copies of arm bytes `0xFFFF4178` and
`0xFFFF4179` (block `0xFFFF4124..0xFFFF417B -> 0xFFFF40CC..0xFFFF4123` at
`0x2132C`). The bank-1 count is judged while cylinder index `0xFFFF11DE` is
2, 4, or 6, after the bank-1 window has closed, and zeroed otherwise at
`0xC24AA`; bank 2 is judged while the index is 1, 3, or 5.

```text
count == 1                     -> clear ffff850c bit 5, clear ffff850d bits 6 and 4
count == 0 and ffff4120 bit 0  -> set ffff850c bit 5, set ffff850d bit 6,
                                  ffff408c += 1 (saturating);
                                  at >= ROM8[0x8E21] = 10 set ffff850c bit 3
count >= 2 and ffff4121 bit 0  -> set ffff850c bit 5, set ffff850d bit 4,
                                  ffff408e += 1; at >= 10 set ffff850c bit 1
both arm bits clear            -> clear ffff850c bit 5 and the indicators
```

Bank 2 mirrors the table with `0xFFFF850C` bit 6, arm bits 1, indicators
`0xFFFF850D` bits 7 and 5, counters `0xFFFF408D` and `0xFFFF408F`, and result
bits 4 and 2. A reset request in `0xFFFF850C` bit 7 clears the indicators,
zeroes the counters whose result bit is clear, zeroes both edge counts, and
clears bit 7 at `0xC23F6`. Bits 5 and 6 are therefore the per-bank edge-count
anomaly flags: no edge or more than one edge in the last window while the
corresponding path is armed. They inhibit the phase-byte update in the
capture handlers, the actual-position update in `FUN 000BFC2E`, and the
electrical enable; the ten-window results in bits 3, 4, 1, and 2 are the
position-sensor fault results that the table under "Diagnostic monitor"
lists.

`FUN 00090086` (path A) and `FUN 0009018C` (path B), called from
`FUN 0008F168` with the bank in `r4` and the enable flag in `r5`, arm the
counters and judge the indicators. With the enable set they set the bank bit
of `0xFFFF4178` or `0xFFFF4179` (`0x900D2` and `0x900F4` for path A) and,
when both arm bytes were clear for the bank, raise reset request
`0xFFFF850C` bit 7 (`0x900D8`, `0x901DE`) under interrupt mask. While the
indicator bit (`0xFFFF850D` bit `6 + b` for path A, bit `4 + b` for path B) is
clear they reload timer `0xFFFF43BE + b` with `ROM8[0x8E23] = 100`; when the
indicator is set and the timer has expired they set the judged latch
(`0xFFFF3580` at `0x9011C`, `0xFFFF3581` at `0x90222`), which routes to
P1078/P1084. A clear enable clears the arm bit (`0x90168`) and reloads the
timer, and a set judged latch clears the arm bit at `0x90182`. Reset helper
`FUN 0008FC6A` clears both arm bytes.

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
| `FUN 00090086` | `0xFFFF3580` bits 0, 1 | no-edge indicator `0xFFFF850D` bits 6, 7 with timer `0xFFFF43BE + b` | `0x84`, `0x85` | P1078, P1084 position sensor path A |
| `FUN 0009018C` | `0xFFFF3581` bits 0, 1 | extra-edge indicator `0xFFFF850D` bits 4, 5 with timer `0xFFFF43BE + b` | `0x86`, `0x87` | P1078, P1084 position sensor path B |
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
`0xFFFF11C8` and `0xFFFF11C9` are the cam edge phase snapshots described
above; the monitor forms `0xFFFF16BA + b` as `clamp_u8(source - ROM8[0x831D +
b] + 128)` at `0x8F4EC` and `0x8F524`, and `FUN 000BFC2E`, `FUN 00090BD2`,
`FUN 00090884`, and `FUN 000BFAD4` read the same bytes.

`FUN 000904C2` counts `0xFFFF1998 + b` while `0xFFFF84C3` bit 7 is set,
zeroes it while `0xFFFF1994` exceeds `ROM8[0x8E43] = 2`, and marks the
evaluation as running in `0xFFFF359A`. `0xFFFF84C3` is the scheduler's
snapshot of tick-flag byte `0xFFFF84C4` (`0x20EE6`), which base-tick handler
`FUN 0002040C` marks with bit 7 on every 1.024 ms interrupt at `0x20734` and
which the scheduler then reloads from `0xFFFF84BB` at `0x20EF0`; the bit is
set on every scheduler pass, so the counter advances once per 10.24 ms pass
and the 60-sample window is about 0.61 s. While the counter is at most
`0xFFFF13A8`, a gap `0xFFFF1476 + b` inside `128 - ROM8[0x894F] .. 128 +
ROM8[0x894D]`, both 34, latches the bank bit of `0xFFFF3598`; a gap outside it
sets the pending bit in `0xFFFF1478` unless the pass bit is already latched.
When the counter exceeds `0xFFFF13A8`, a latched pass bit sets `0xFFFF2D19`
and clears the stored code through `FUN 0008C348` with index `0xD2` for bank 1
and `0xD3` for bank 2, while a pending bit without a pass sets the bank bit of
`0xFFFF358C` and `0xFFFF3583`.

### Disable path

The calibration-only path keeps every map-derived exhaust target below the
entry threshold. With surfaces `0xB33A` and `0xB2FA` at `0x80` and correction
`0xAB4A` at `0x80`, `0xFFFF1C90` stays at 128 outside the standstill
override, bit 3 of `0xFFFF24A7` stays clear, `0xFFFF1246` keeps bits 0 and 1
clear, both control-mode bytes stay in mode 0, `P` and the published duty
words stay at zero, and `BFR7C` and `BFR7D` hold zero. The conditioned
target `0xFFFF2327` sits at `0x80`.

The standstill override is outside that path. With `0xFFFF246C` bit 1 set it
writes `ROM8[0x8E36] + 128 = 168` to `0xFFFF137E` regardless of the
surfaces, the demand flag sets, both banks energize, and the target returns
through the 140 hold to 128 once the predicate falls. The 2026-09-17
captures of a Map 3 image with all three surfaces neutral show eight such
excursions, each starting as the engine passed 1800 RPM at rest or while
creeping and ending on pedal release, on vehicle motion, or above 4200 RPM.
Calibration byte `ROM8[0x8E36]` is single-copy and not a Map Switching
family; a value of 0 makes the override command 128 on every map slot and
leaves the rest of the path unchanged.

On that path the monitor behaves as follows:

- The target-tracking pair is enabled only during the standstill override,
  because it requires `0xFFFF2327 != 0x80`; otherwise `FUN 000904C2` runs
  its reset path.
- The magnet retarder circuit pair is never judged, because `FUN 00090642`
  returns while the published duty word is zero.
- The rest-position pair is enabled by the neutral target and compares
  `0xFFFF16BA` and `0xFFFF16BB` with the `128 +/- 34` window, which holds
  while the cam edge phase snapshots `0xFFFF11C8` and `0xFFFF11C9` stay
  within `88 +/- 34` counts. The pair follows the measured sensor edge, so
  this is the one P0014/P0024 path the calibration change leaves active; it
  passes as long as both exhaust cams rest within 34 units of the calibrated
  edge, which the de-energized magnets are expected to hold but which no
  capture has confirmed on the car.
- The position sensor paths judge driver status `0xFFFF850C` independently of
  the target and are not affected by the calibration change.

Executable alternatives, such as forcing mode 0 in `FUN 000C1DEC` or zeroing
the published duty words, replace instruction bytes and therefore require the
`tools/sh-elf-run` gate before any image built from them is eligible for
hardware.

### Registry suppression

The DTC registry switch of `JK08A.dtc.csv` zeroes the twelve descriptor bytes
and the attribute word of a record. For the exhaust records that removes the
published code and the attribute classes: `0x0020` for P0014/P0024 and
P1080/P1086, `0x00A0` for P0078/P0084, and `0x02A0` for P1078/P1084. None of
them carries attribute bit 8 or bit 10, so no exhaust record feeds the inhibit
polls of the operating enable. The monitor and the runtime record stay active:

- `FUN 0008C2D2` sets the stored-fault bit without reading the descriptor. It
  reads the attribute word only for class event bytes `0xFFFF48E0` (bit 10)
  and `0xFFFF48E2` (bit 13).
- `FUN 0007D8B8` routes a record whose descriptor byte 8 bit 6 and attribute
  bit 6 are clear to default handler `FUN 0007E334`, which updates bits 0, 1,
  5, and 6 of record byte 2 from the record alone. The descriptor enters only
  through the code comparison that selects the argument of `FUN 0007E560`,
  and attribute bit 7 gates only the call of `0x0008C900` on confirmation.

Consumers that address the records by index therefore keep their behaviour.
`0x25E20` tests the stored-fault bit and `0x259E4` tests bits 5 and 6 of
record byte 2.

| Consumer | Predicate and indices | Effect of a set record |
|---|---|---|
| `FUN 000BF630` | `0x25E20`: `0x14F..0x152`, `0x43`, `0x44` | electrical enable `0xFFFF248B` bit 0 clears |
| `FUN 0004D2A6` | `0x25E20`: `0x14B..0x152` | ignition cam-deviation correction `0xFFFF1A7D` takes fallback `ROM8[0x8DCC]`, `ROM8[0x8DCD]`, or `0x40`, all 64 on stock |
| `FUN 000995C4` | `0x25E20`: `0x151`, `0x152` | the P0011/P0021 monitor (records `0xD0`, `0xD1`) does not evaluate |
| `FUN 0008F168` | `0x25E20`: `0x14F`, `0x151`, `0x152` | the exhaust performance pairs do not evaluate |
| `FUN 00090A84` | `0x25E20` and `0x259E4`: `0x84..0x87` | the enable argument of `FUN 000907E8` is 0 |
| `FUN 000420B8` | `0x259E4`: `0x43`, `0x44`, `0x151`, `0x152`, `0x84..0x89`, `0xD0..0xD3` | arm bit `0xFFFF2497` bit 5 is withheld |
| `FUN 0009BDD0` | `0x259E4`: `0x43`, `0x44`, `0x84..0x88`, `0x14F`, `0x151`, `0x152` | the per-bank entry gate fails |

Registry suppression is a reporting control. On the calibration-only path the
target-tracking pair, the circuit pair, and the two masked paths are not
judged, so the rest-position pair of `FUN 00090256` is the single path that
can set records `0xD2` and `0xD3` and their extension slots; while it passes,
none of the consumers above changes state.

### Evidence boundary of the controller

The state machine, the arithmetic, the stores, the scheduler snapshots, the
enable coordinator, the capture handlers, the timer configuration, the
actual-position producer, the rest-edge learning, the edge-count monitor, and
the descriptor routing are exact code facts read from the whole-program
export and the headless listings. `FUN 000BF630` has one caller,
`FUN 000C21E6` at `0xC21F2`. The 0.5-degree phase unit rests on the
`phi'/32` configuration of both counters, on `Pphi = 20 MHz` established from
CAN timestamps, and on the `RPM * 5.12` identity of `0xFFFF1196`. The
following remain unresolved:

- the on-car phase value with both cams at their stops, which is a RAM read of
  `0xFFFF1200`/`0xFFFF1201` or of the learned edges `0xFFFF479B`/`0xFFFF479C`;
- the writers of mask byte `0xFFFF48DF` (`FUN 00090884`) and of reference
  word `0xFFFF5578`, which matter only to the masked third P0014/P0024 path,
  the function armed by `0xFFFF2497` bit 5, and the monitor behind
  `FUN 0009BDD0`;
- the crank-wheel origin of the engine-event segment, which fixes the
  absolute angle of the 44-degree stock rest value;
- the decrement cadence of timer `0xFFFF43BE + b`, the internals of
  `FUN 00090642` beyond its entry gate, and the tester-side meaning of
  service `0xA0` request 3;
- the physical meaning of `0xFFFF244F` bit 2 in the standstill predicate,
  the decrement site of countdown `0xFFFF25E7`, the identity of bytes
  `0xFFFF1240` and `0xFFFF1241`, and the purpose of the 20-degree standstill
  override.

## Evidence boundary

Static DID and DTC paths establish the intake/exhaust target distinction even
where downstream conditioning makes a map replay differ from the published
byte. The capture does not establish the electrical valve command or the physical
camshaft angle at the crankshaft; the degree-per-byte conversion rests on the
code path under "Cam edge phase bytes", not on the capture.

CAN telemetry schema 2 names the two sources `intake_cvtc_target_raw` and
`exhaust_cvtc_target_raw`, matching their recovered common-target roles. The
generated profile CRC binds those names and sources to the host decoder.
