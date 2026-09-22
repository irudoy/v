# JK08A Main Fuel Calculation

## Status and scope

This document records the static code model of the main fuel calculation in the
exact JK08A/JK03A executable. The established path covers dual-bank MAF input,
Base Fuel Schedule (BFS), Fuel Compensation Main, the periodic fuel multiplier,
bank-specific base terms, closed-loop trims, six per-channel compensated pulse
words, and the shared fuel-output inhibit mask. The complete source and
precedence model for that mask is maintained in
[`JK08A.fuel-inhibit.md`](JK08A.fuel-inhibit.md).

Arithmetic, RAM data flow, scheduler ordering, diagnostic bindings, and ATU-II
register use are code-proven, and the code path from the compensated pulse
words to the ATU-II one-shot outputs fixes their millisecond scale. The same
path places each pulse by crank angle from the injection-end delay tables.
The same arithmetic fixes one Base Fuel Schedule count at `1/2048 ms`.
Road-log statistics reproduce the code chain on the running engine. The
physical connection between the scheduled durations and the injector
terminals remains a hardware-validation item.

## Periodic ordering

`FUN_00020DFE` dispatches the 124-entry table at `0x2196C`. Relevant entries are
ordered as follows:

| Index | Function | Established role |
|---:|---|---|
| 12 | `FUN_000769C0` | request-limit source coordinator, including the `0x0942C` branch |
| 19 | `FUN_00071508` | signed-minimum request-limit arbiter |
| 21 | `FUN_000702A0` | ordered request-controller stages and final selector |
| 22 | `FUN_00079DD8` | signed request-boundary dispatch |
| 23 | `FUN_000730FC` | downstream inverse-coordinate and limit calculations |
| 28 | `FUN_0004ED88` | final six-channel inhibit/override mask `0xFFFF22E0` |
| 36 | `FUN_00057608` | fuel-multiplier calculation coordinator |
| 39 | `FUN_00056FC0` | common additive and masked-channel override word `0xFFFF2436` |
| 40 | `FUN_00053698` | common Q14 gain `0xFFFF165E` |
| 42 | `FUN_000522C4` | transient and per-channel preparation, including `0xFFFF2300` |
| 43 | `FUN_0004E974` | common and two-bank injection precursors |
| 55 | `FUN_0005C910` | runtime STFT publication |
| 61 | `FUN_0004ECAC` | two parity bases and six-channel compensated pulse calculation |
| 81 | `FUN_00057020` | downstream mode-dependent fuel calculation |

The ordering proves current-pass dependencies from the inhibit mask and fuel
multiplier through the transient term and pulse calculation. Scheduler index 84
is the separate two-bank exhaust-VTC coordinator `FUN_000C21E6`; it is outside
the fuel calculation.

The request limiter is calculated before the fuel-output inhibit mask, but it
does not feed that mask. Its signed-minimum controller path and the exact
main/stationary/DFCO mask precedence are documented in
[`JK08A.limiters.md`](JK08A.limiters.md).

The MAF/BFS producer uses a separate every-fourth-base-interrupt table at
`0x21818`. `FUN_0003A904` is index 2 and `FUN_0003B75C` is index 3. The periodic
snapshot dispatcher moves `0xFFFF1026` into current BFS `0xFFFF1024` and retains
the previous current value in `0xFFFF1028`. The same producer forms live Q7
normalized-BFS byte `0xFFFF1048`, which the dispatcher snapshots to internal
map coordinate `0xFFFF102C`. Its fixed-reference formula and distinction from
J1979 Calculated Load are specified in
[`JK08A.load.md`](JK08A.load.md).

## MAF to Base Fuel Schedule

Exact diagnostic and ADC paths identify the two airflow channels:

```text
AN4 / AN15
  -> DID 0x1204 / DID 0x1205
  -> MAF curves 0x14274 / 0x141F4
  -> FUN_0003A904
  -> FUN_0003B252
  -> combined nonnegative MAF aggregate 0xFFFF1E38
  -> FUN_0003B75C
  -> newest BFS 0xFFFF1026
  -> current BFS 0xFFFF1024
```

`FUN_0003B252` writes:

```text
Q = max(0,
        int32[0xFFFF1DF8] +
        int32[0xFFFF1DFC] +
        int16[0xFFFF1E2A] +
        uint16[0xFFFF2368])
```

Stock JK08A configuration makes `0xFFFF1E2A` zero on each producer call. A
whole-program p-code census found no application-code writer for
`0xFFFF2368`; startup clears its containing RAM range. The normal analyzed
application therefore reduces the aggregate to the nonnegative sum of the two
32-bit bank terms. Unresolved indirect hardware activity remains outside this
static boundary.

For the primary BFS branch, let:

```text
Q = uint32[0xFFFF1E38]
F = ROM8 [0x8A27] = 109
K = ROM16[0x9284] = 26806
E = ROM8 [0x88FB] = 3
N = selected engine-speed count, lower-bounded at 64
```

The exact integer sequence is equivalent to:

```text
fixed = min(floor(floor(F*K*Q/256)/(E*N)), 0x726F9)
0xFFFF1E40 = floor(fixed*9163/65536)
```

The fallback branch looks up uint16 table `0x15630` by normalized coolant,
writes the result to `0xFFFF1E44`, and writes one quarter of it to
`0xFFFF1E40`.

Exact DID `0x1208` identifies `0xFFFF1026` as Base Fuel Schedule. One count of
the word is `1/2048 ms` in the time base of the injection-pulse words, as
derived under [Injection-pulse time scale](#injection-pulse-time-scale); the
homologous structured-profile conversion `raw/2048 ms` agrees with it. The
`ms/kg` K-Value unit is dimensionally consistent with the code and remains a
candidate engineering scale. The airflow entering the
producer is declared by the ECU itself: J1979 Mode 01 PID `0x10` publishes
`105 * 0xFFFF105C / 256` as g/s*100, so one count of the total is
`105 / 25600` g/s. The `kg/hr` MAF Factor unit with scale `x * 0.0001` gives
0.0109 kg/hr per count against 0.01477 kg/hr from that declaration; the
discrepancy is recorded at the finding.

## Fuel Compensation Main to BFS

`FUN_0003BE3C` contains the live accessor for Fuel Compensation Main `0xA29A`.
At `0x3C284..0x3C29C`, the active lookup path uses wrapper `0x261F0` with row
axis `0x11CF0` over RPM/12.5 word `0xFFFF11F4` and column axis `0x11D4C` over
byte `0xFFFF1170`, then writes the uint8 result to `0xFFFF1160`. Runtime
gates can select a bounded bypass value instead of the map result; the common
destination is unchanged.

Byte core `0x269C4` compares each row point after multiplication by four with
the RPM/12.5 word, so one row-axis count is 50 RPM. Byte core `0x26944`
compares each column point with `0xFFFF1170` directly. `FUN_0003B498` writes
that byte as the high byte of curve `0x15042`, at coordinate `4 * u` below
`u = 0x3C00`, or of curve `0x15022`, at coordinate `u - 0x3C00` from there:

```text
u = min(65535, (0xFFFF1E60 * 0xFFFF114E >> 9)
             + (0xFFFF120E * 0xFFFF114E >> 11))
0xFFFF114E = min(65535, 0xDC1D00 / 0xFFFF1F46), or 0 while 0xFFFF1F46 = 0
0xFFFF1F46 = min(65535, ROM8[0x8D8F] * 0xFFFF11F4)
```

`FUN_0003B40A` writes `0xFFFF1F46`, and `FUN_0003B436` writes `0xFFFF114E`,
which is inversely proportional to engine speed. `FUN_0003B468`
selects `0xFFFF1E60` from ETC-path value `0xFFFF3A76`, which `FUN_0003B520`
derives through the Throttle Angle-to-Area pair `0x13202`/`0x155A0`, or from
ROM word `0x916C`.

Both addends of `u` are opening areas in the value domain of `0x13202`, divided
by engine speed. `0xFFFF3A76` sums two areas:

```text
0xFFFF3A76 = min(0xFFFF, clamp(area(min(0xFFFF, 4 * 0xFFFF284A)) - 0xFFFF56A2, 0, 0xFFFF)
                       + clamp(area(min(0xFFFF, 4 * 0xFFFF284C)) - 0xFFFF56A4, 0, 0xFFFF))
area(x) = lookup of 0x13202 over axis 0x155A0 at x
```

`0xFFFF120E` is an inflow area in four times those counts: `FUN_0003B498` adds
`0xFFFF120E / 4` to the throttle area, and `FUN_00072C3C` subtracts
`0xFFFF120E >> 2` from shared throttle target area `0xFFFF19B2`. With
`ROM8[0x8D8F] = 100`, `0xFFFF1F46` is `8 * RPM` and `0xFFFF114E` is about
`1803168 / RPM`, so:

```text
u ~= 3522 * (0xFFFF1E60 + 0xFFFF120E / 4) / RPM
```

The column coordinate is therefore an alpha-N flow estimate: opening area over
engine speed through a saturating curve. The high bytes of curve `0x15042` run
from 4 to 204 and those of curve `0x15022` from 204 to 224. MAF range
monitors `FUN_0008152A` (P0101) and `FUN_00081D74` (P010B) evaluate the same
curve pair and read `0xFFFF120E`. The A2L names the coordinate QH0 Flow
Quantity with a candidate `x * 0.390625` percent scale, which is the curve
high byte over 256. It is not the normalized Base Fuel Schedule that indexes
the ignition and CVTC target maps.

The map's code-level representation is Q7:

```text
raw 128 = 1.0 = 100 percent
```

`FUN_0003B75C` consumes the current byte directly:

```text
f = min(65535, floor(uint16[0xFFFF1E40] *
                     uint8 [0xFFFF1160] / 128))
0xFFFF1062 = f
```

A separate selected word `0xFFFF115C` enters the next stage:

```text
T = sat_u32(4 * f * uint16[0xFFFF115C])
P = uint16[0xFFFF1F30] * uint16[0xFFFF1E06]
```

Stock `ROM8[0x8D92] = 0x7A` has bit 4 set, selecting:

```text
0xFFFF1DEE = min(65535, max(P - T, 0) >> 13)
```

The opposite configuration branch uses the saturated `(P + T) >> 13` result.
`FUN_0003BE3C` also publishes `0xFFFF115C`; its selected source can be a
calculated word, a parallel working word, or stock constant
`ROM16[0x90EE] = 0x020C` according to runtime state. `0xFFFF115C` is therefore
not the `0xA29A` result and must not be merged with `0xFFFF1160` in a definition
or patch.

The corrected schedule is rate-adjusted and optionally blended with the prior
sample. RPM curve `0x12C9E` normally caps the result before it is written to
`0xFFFF1026`; an alternate mode uses direct grid `0x974E`.

## Commanded mixture

`FUN_0005594A`, the second stage of `FUN_00057608`, is the only stock writer of
the commanded-mixture word `0xFFFF22E8`. The alternate writer `FUN_00055596`
is reached only when `ROM8[0x8B42]` bit 0 or `ROM8[0x8B34]` bit 4 is set;
stock holds both clear.

The target byte is a Q7 fuel-multiplier command against the stoichiometric base
schedule, `128` = closed-loop stoichiometric target:

```text
wot   = 0xFFFF2468.bit3            # 0xFFFF3528 >= 200 (+8 hysteresis), 78.4 % opening
load  = wot ? 0xFF : uint8[0xFFFF102C]
m     = map8x8(0xA9AA; rpm axis 0x11CC0 vs uint16[0xFFFF11BC], load axis 0x11AC7)
if 0xFFFF2466.bit6:                # high-detonation surface selected
    t = map1D(0x12552 on uint8[0xFFFF11AE], axis 0x11CD8)
    m = sat_u8(128 + ((m - 128) * t >> 7))
rich  = 0xFFFF24A2.bit7            # m + (rich ? 1 : 0) >= ROM8[0x8B9B] = 130
0xFFFF15EB = rich ? m : 128
```

`0xFFFF3528` is `min(255, uint16[0xFFFF40C6] * 0x505B >> 16)` from
`FUN_00054EB8`, the first stage of the coordinator. `FUN_0006F236` applies the
same gradient, after subtracting idle base `0xFFFF28F8`, to the byte it
publishes as J1979 PID 0x11 absolute throttle, so `0xFFFF3528` is throttle
opening from coordinate zero at 100/255 percent per count, and the latch
threshold 200 is 78.4 percent.

Request byte `0xFFFF1411` and state byte `0xFFFF1410` select how the word
moves toward the target: `8` while coolant `0xFFFF1071` is below
`ROM8[0x8CF8] = 115` (`0xFFFF24A4` bit 5), `1` when `m == 128`, otherwise
`2..7` from the engine-speed band flags of `0xFFFF2493` (`0xFFFF11AE` against
`ROM8[0x87D4] = 44` and `ROM8[0x87D3] = 72`, i.e. 2200 and 3600 rpm), the
wide-open latch, and `0xFFFF2485` bit 6. The ramp uses the previous-pass
snapshot `0xFFFF1278`, which `FUN_00020DFE` copies from `0xFFFF123A` in the
`0x3E`-byte block `0xFFFF120E -> 0xFFFF124C`:

```text
prev   = uint16[0xFFFF1278]
target = uint8[0xFFFF15EB] << 7
down   = max(0x4000, prev - ROM8[0x849B] * 8)      # 304 per pass
up     = min(target, prev + ROM8[0x849C] * 8)      # 384 per pass
state 1        -> 0x4000
state 4, 5     -> target
state 2, 3, 6  -> ramp (kick-off ROM8[0x8B9C] << 7 = 0x4100,
                        floor ROM16[0x929C] = 0x4000, direct target
                        once 0xFFFF2485.bit5 reports arrival)
0xFFFF123A = min(value, target)
0xFFFF2485.bit5 = (0xFFFF123A == target)
```

`FUN_0005651C` forms the second word `0xFFFF123C` under gates that stock
constants neutralize (`0x11EDE` flat 254, `ROM8[0x87D9] = 0`, ramp toward
`ROM16[0x8F86] = 0x4000`), so it stays at `0x4000`. The final publication:

```text
v = max(uint16[0xFFFF123A], uint16[0xFFFF123C])
if uint8[0xFFFF2700] < 32:            # interval-derived rpm/12.5 byte, 400 rpm
    0xFFFF2531 = ROM8[0x87D6] = 2
if uint8[0xFFFF2700] < 32 or 0xFFFF2531 != 0:
    v = 0x4000
if 0xFFFF4252.bit1:
    v = min(v, ROM16[0x94EC] = 0xFFFF)
0xFFFF22E8 = v
```

`0xFFFF2700` is the scheduler snapshot of `0xFFFF2804`, the median-of-three
quotient `41666 / uint16[0xFFFF22BC]` from `FUN_0003DF2C`, whose diagnostic
substitute `0xFFFF11EA` fixes the representation as rpm/12.5.

Three 2026-08-26 vehicle recordings agree with this chain: the streamed word is
always a multiple of 128 within `16384..19072`, settled values match the
`0xA9AA` lookup in 98.3..100 percent of records, and both STFT words stay at
neutral `0x6400` whenever the command exceeds `0x4000`. Commanded lambda is
`16384 / raw`; the public HR A2L names `0xA9AA` `Target AFR Map (8x8)` with
gasoline scale `1881.6 / x`, which remains a candidate.

## Fuel multiplier and full-inhibit behavior

`FUN_00057608` calls the current fuel-multiplier stages in this fixed order:

```text
0x54EB8 -> 0x5594A -> conditional 0x55596 -> 0x5525A -> 0x55098
        -> 0x52F00 -> 0x54EE0 -> 0x554AE -> 0x55648 -> 0x554F8
        -> 0x556EC
```

`FUN_000554AE` forms a saturated unsigned base term:

```text
0xFFFF231A = clamp_u16(int32 [0xFFFF15F8] +
                       0x4000 +
                       uint16[0xFFFF230C] +
                       uint16[0xFFFF15DA])
```

`FUN_000554F8` conditionally looks up `0x154B0` on axis `0x13B28`, caps the
result at 3768, and writes `0xFFFF240A`; disabled paths write zero. Its
`Cranking Base Fuel Schedule` name and engineering scale remain candidate.

`FUN_000556EC` begins with the code-exact provisional target:

```text
sum    = min(65535, uint16[0xFFFF231A] + uint16[0xFFFF240A])
target = floor(sum * uint16[0xFFFF22E8] / 16384)
```

Additional gates, bounds, and rate limits form working word `0xFFFF18E4`.
Publication to `0xFFFF22E6` has an exact full-inhibit rule:

```text
if uint8[0xFFFF22E0] == 0x3F:
    0xFFFF22E6 = 0
else:
    0xFFFF22E6 = 0xFFFF18E4
```

The working word is retained even when the published value is forced to zero.
This creates a direct current-pass link from the aggregate six-channel cutoff
mask to the main pulse precursor.

## Common gain and transient additive term

`FUN_00053698`, table index 39, recalculates on alternating invocations gated
by `0xFFFF2485.bit3`:

```text
P = ROM16[0x93C6] + arithmetic_shift7(ROM8[0x89FE] * uint16[0xFFFF4524])
P = 51865 when FUN_00025E20(-1) is nonzero
0xFFFF517C = sat_u16(P)
R = clamp(floor(256 * P / 51865), ROM8[0x83C4], 256)

b = uint8[0xFFFF2733], or ROM8[0x8B51] when FUN_00025E20(0x125) is nonzero
T = clamp(floor(76288 / (b + 223)), ROM8[0x83C5] + 128, ROM8[0x83C6] + 128)

0xFFFF13B1 = min(255, ((uint16[0xFFFF1024] * R >> 8) * T) >> 15)
0xFFFF17BA = curve 0x129E2 at 0xFFFF13B1
0xFFFF17BB = curve 0x129F2 at engine-speed byte 0xFFFF11B3
0xFFFF17B9 = min(255, 0xFFFF17BA + 0xFFFF17BB)
0xFFFF31D8 = sat_u16(P * (256 - 0xFFFF17B9) >> 8)

K = ROM8[0x8AE7]
0xFFFF17EE = min(255, floor((K << 18) / ((K << 10) + 0xFFFF31D8)))
0xFFFF160D = min(255, floor((0xFFFF17EE * 5259 + 0x128500) / 10000))
0xFFFF165E = floor(uint8[0xFFFF160D] * ROM16[0x9332] / 256)
```

Stock constants are `ROM16[0x93C6] = 51865`, `ROM8[0x89FE] = 0`,
`ROM8[0x83C4] = 128`, `ROM8[0x83C5] = 51`, `ROM8[0x83C6] = 215`,
`ROM8[0x8B51] = 75`, `K = 175`, and `ROM16[0x9332] = 13972`. The zero slope
byte makes `P` the constant 51865 and `R = 256`, so the gain depends only on
Base Fuel Schedule, intake-temperature byte `0xFFFF2733`, and engine-speed
byte `0xFFFF11B3`. Both curves are 16-point implicit-axis `uint8` tables of
primitive `FUN_00026388`.

`0xFFFF165E` is the common Q14 gain consumed by the next current-pass pulse
stage. Ratio byte `0xFFFF17EE` spans `198..255`, factor byte `0xFFFF160D`
spans `225..255`, and the gain spans `12280..13917`, which is
`0.7495..0.8494` of unity `16384`. `ROM16[0x9332] / 16384 = 0.8528` is a fixed
calibration scalar.

The stage has the form of an injector differential-pressure correction.
`0xFFFF17EE` is `256 * C / (C + V)` with `C = K << 10 = 179200`, and the affine
map to `0xFFFF160D` sends 256 to 256 and stays within 0.4 count of
`256 * sqrt(x / 256)` before the integer floor, so `0xFFFF160D / 256`
approximates `sqrt(C / (C + V))`. With one count of `C`, `P`, and `V` read as
`1/512 kPa`, `C` is `350.0 kPa`, the fuel-pressure specification of the
homologous VQ35HR service manual, `P = 51865` is `101.30 kPa`, and
`V = P * (1 - 0xFFFF17B9 / 256)` is the modelled manifold depression that adds
to the differential pressure of a rail regulated against atmosphere. With the
ECU-declared `degC = raw - 50` temperature scale, `b + 223` is kelvin and
`T = 256 * 298 / kelvin`. This physical reading is a candidate; the arithmetic
is exact.

Within table-index-41 coordinator `FUN_000522C4`, `FUN_000528BE` selects byte
`0xFFFF150A` from map `0x12176` or constant 64 and calls `FUN_00052902`.
The latter writes:

```text
0xFFFF2300 = clamp_s16(trunc_toward_zero(
                         uint8[0xFFFF150A] *
                         int16[0xFFFF1A66] / 256))
```

A runtime gate can force the result to zero. This signed word is a current-pass
additive pulse term; its physical transient qualifier remains unresolved.

## Common and bank-specific pulse precursors

`FUN_0004E974` normally selects current BFS `0xFFFF1024`. When
`0xFFFF245D.bit5` is set it selects alternate word `0xFFFF123E`. Optional
`0xFFFF24D2.bit0` logic bounds that source using RPM word `0xFFFF11BC`,
`ROM32[0x96E0] = 0x0012C000`, and `0xFFFF34F6`, and records the bounded result
in `0xFFFF196A`.

Let the selected and bounded source be `S`:

```text
H = floor(S * uint16[0xFFFF22E6] / 131072)
A = int16[0xFFFF2300]
G = uint16[0xFFFF165E]
```

For bank index `b` in `{0,1}`:

```text
B_b = uint16[0xFFFF40B6 + 2*b]
X_b = floor(H * B_b / 0x6400) + A
Y_b = trunc_toward_zero(X_b * G / 16384)
I_b = max(ROM16[0x94E8], clamp_u16(Y_b))

ROM16[0x94E8] = 170
0xFFFF18C0 + 2*b = I_b
```

The signed scaling is implemented by `FUN_0002657C(v, G, -2)`. A parallel
common result omits the bank multiplier:

```text
Y_common = trunc_toward_zero((H + A) * G / 16384)
0xFFFF1876 = max(170, clamp_u16(Y_common))
```

`0xFFFF24A1.bit0` records whether the common result was raised to the minimum.
The code establishes two bank-indexed precursors. Channel index `i` of the later
parity channels carries cylinder `i + 1`, as derived under
[Injection timing](#injection-timing).

## Closed-loop trims and two parity bases

`FUN_000593AC` initializes both STFT and LTFT diagnostic words to neutral
Q8.8-percent value `0x6400`. It also initializes per-bank correction words
`0xFFFF2310` and `0xFFFF2312` to offset-neutral `0x8000`. A whole-program p-code
census found no later application-code writer for the latter pair.

For bank index `b` in `{0,1}`, `FUN_0004EAD4` reads:

```text
STFT_b  = uint16[0xFFFF22DC + 2*b]
LTFT_b  = uint16[0xFFFF2302 + 2*b]
extra_b = uint16[0xFFFF2A24 + 2*b]
I_b     = uint16[0xFFFF18C0 + 2*b]
offset_b = uint16[0xFFFF2310 + 2*b]
```

Stock `ROM8[0x893D] = 0x51` has bit 1 clear and
`ROM8[0x8940] = 0x01` has bit 4 clear, so the selected control word is
`0xFFFF22E6`. The stock branch computes trim delta:

```text
if uint16[0xFFFF22E6] > 0x4000:
    trim_b = STFT_b + extra_b - 0x6400
else:
    trim_b = STFT_b + LTFT_b + extra_b - 0xC800

trim_b = max(trim_b, 0)
```

The base result is:

```text
v = uint16[0xFFFF2436] + floor(I_b * trim_b / 65536)

if I_b != 0:
    v = floor((256*v + offset_b - 0x8000) / 256)

0xFFFF191C + 2*b = min(v, 65535)
```

All three trim words are Q8.8 percent with neutral `0x6400`, so the neutral
delta is `0x6400` and the neutral stage factor is `0x6400 / 65536 = 100 / 256`.
Third trim array `0xFFFF2A24` is initialized to `0x6400` by `FUN_0002C648` and
reset to it by `FUN_0005B708`. `FUN_0005B534` steps each bank word by
ROM-defined increments inside `ROM8[0x82E4] << 8 .. ROM8[0x82E5] << 8`, stock
90 to 110 percent, and otherwise ramps it toward `0x6400`; the physical source
of this correction is unresolved.

The startup-only `offset_b = 0x8000` makes the last correction neutral in the
analyzed application. `0xFFFF2436` is both a common additive term in normal
base calculation and the direct value selected for masked channels.

### Long-term trim publication and neutralization

`FUN 00057B26` takes the bank index in `r4` and publishes the LTFT diagnostic
word from the selected learned cell and the adjustment term:

```text
raw_b = uint16[0xFFFF2306 + 2*b] + uint16[0xFFFF5648 + 2*b] - 0x6400
```

Limiting is skipped when bit `b` of `0xFFFF230E` is set, or when
`uint16[0xFFFF15FC] <= int16[0xFFFF15FE]`: `extu.w` at `0x57B60` zero-extends
the first word, the load at `0x57B62` sign-extends the second, and `cmp/gt` at
`0x57B64` compares them as signed 32-bit values. Otherwise the word is clamped
between two adjacent ROM bytes scaled to Q8.8 percent:

```text
raw_b = min(max(raw_b, ROM8[0x8E5B] << 8), ROM8[0x8E5A] << 8)
ROM8[0x8E5B] = 90, ROM8[0x8E5A] = 110
```

Four independent conditions replace the result with exactly neutral `0x6400`
before the store to `0xFFFF2302 + 2*b`:

```text
FUN 00025E20(0x0129) != 0
uint8[0xFFFF41B5].bit0 set
uint8[0xFFFF41FA].bit0 set and uint8[0xFFFF248B].bit1 set
uint8[0xFFFF249C].bit6 set and uint8[0xFFFF248B].bit0 set
```

`tst #1` at `0x57C02` and `bt 0x57C10` skip the third condition while
`0xFFFF41FA.bit0` is clear. Runtime record `0x129` is the dual-bank MAF
diagnostic summary of [`JK08A.fuel-inhibit.md`](JK08A.fuel-inhibit.md).

`FUN 00057D1E` keeps each learned cell inside `ROM8[0x8A9E] << 8` to
`ROM8[0x8A9F] << 8`, 90 to 110 percent. With a neutral adjustment term the
published word is therefore the selected learned cell or exactly `100.000`
percent, whether or not limiting runs. `0xFFFF2306` and `0xFFFF5648`
distinguish a neutralized publication from the clamped summand sum whenever
that sum differs from `0x6400`; neutral summands under a neutral word do not.
`FUN 0005796C` refills the bank grid with `0x6400` and selects `0x6400` while
runtime record `0x129` or `0xFFFF41B5.bit0` is set, so neutral summands also
fit a grid that one of these conditions holds at `0x6400`.

The 2026-09-22 road session is recorded under
`can_telemetry.ltft_learning_2026_09_22` in `patches/hardware-results.toml`,
and `tools/logs/ltft_publication_audit.py` reproduces its figures from the
dashboard MLG recordings. The published bank 1 word equals the clamped summand
sum in all 45,586 tag-2 refreshes whose bracketing tag-0 refreshes agree,
23,079 of them with a non-neutral prediction, and no refresh publishes a forced
neutral word. The adjustment term stays `0x6400` in all 46,931 samples, so the
adjustment path and the neutralizing conditions stay unexercised. The learned
word changes 1,332 times. Of the 525 changes inside one replayed selector cell,
520 stay within the single-update bound, and 492 of the 518 with non-neutral
STFT follow its sign. No learned change occurs in the 7,996 tag-0 pairs in P or
in the 293.181 s of the cold-start capture after coolant reaches
`ROM8[0x8CFD]`. The fuel-inhibit mask is zero in 8,745 snapshots of that warm
part whose RPM/12.5 word reaches the `0xC0` gate of `FUN 0004F736`, which
requests the full mask while MAF summary snapshot bit `0xFFFF2448.bit7` is set;
the stream carries neither `0xFFFF41B5` nor the remaining permit terms of
`FUN 00057D1E`.

## Six-channel compensated pulse words

`FUN_0004ECAC` calls `FUN_0004EAD4` for the two parity bases and then invokes
`FUN_0004EBA2` for channel indices 0 through 5. For channel `i`:

```text
if 0xFFFF22E0 has bit i set:
    base_i = uint16[0xFFFF2436]
else:
    base_i = uint16[0xFFFF191C + 2*(i & 1)]

v = base_i + int16[0xFFFF1396 + 2*i]
```

Stock `ROM8[0x8D92].bit3` is set, so the executing path then subtracts
`int16[0xFFFF1466 + 2*i]`. Negative results become zero. Each positive result
is multiplied by `ROM8[0x129C0 + i]` and shifted right by seven before uint16
saturation. All six stock multipliers are `0x80`, or unity in Q1.7.

The raw result is written to `0xFFFF23C8 + 2*i`. Exact DID `0x1206` returns the
first word, and the VQ35HR factory manual identifies the corresponding monitor
as actual compensated injection pulse width for bank 1. One count is 10 us, so
the conversion is `ms = raw / 100`; the derivation is in
[Injection-pulse time scale](#injection-pulse-time-scale).

Each raw word also passes through `FUN_0005B7EC`. With stock coefficients:

```text
C0 = ROM16[0x91DA] = 13656
C1 = ROM16[0x91DC] = 16384
D0 = ROM16[0x91DE] = 4250
D1 = ROM16[0x91E0] = 0

y0 = sat_u16(floor((x*C0 + 100*D0) / 16384))
y1 = sat_u16(floor((x*C1 + 100*D1) / 16384))
return max(x, y0, y1)
```

For the stock coefficients `y1 = x`, so the transform simplifies to:

```text
max(x, sat_u16(floor((13656*x + 425000) / 16384)))
```

The transformed six-word array begins at `0xFFFF23D4`. It is the duration the
scheduler programs into the ATU-II one-shot outputs, so `FUN_0005B7EC` is the
final minimum-pulse enforcement before the hardware. `FUN_000521A8` takes the
maximum of all six transformed words and `0xFFFF241C`, then derives scalar
bytes `0xFFFF23BF` and `0xFFFF23F0`.

## Active-vehicle reproduction

The dashboard recordings of 2026-09-17 (`tools/logs/mlg_relation_audit.py`,
statistics in `patches/hardware-results.toml`) reproduce the chain on the
running engine in raw units. At steady MAF inputs the published total word
equals `floor(105 * (A + B) / 256)` exactly in 57 to 85 percent of records and
within one count in 62 to 93 percent, with the median ratio of the total to
`A + B` at `105/256`. Base Fuel Schedule matches the primary-branch producer
with `Q = A + B` and `N = 2 * rpm_raw` at a median ratio of 0.98 to 0.99
(p5 0.87 to 0.94, p95 1.01 to 1.04). The J1979 Calculated Load byte matches
its formula from the prior record exactly in 77 to 80 percent of records and
within one count in 95 to 97 percent.

The same audit replays the code chain from the schedule to both bank pulse
words. For each closed-loop record whose schedule stays within 2 percent over
the previous 50 records it rebuilds common gain `0xFFFF165E` from the recorded
schedule, intake-temperature byte, and engine speed, applies the unity
multiplier `0x4000`, the recorded short-term and long-term trims with the
third trim at neutral, and the opening time from the recorded battery byte:

| Recording | Records | Median pulse / replay | p5 | p95 | Within 2 percent | Median gain |
|---|---|---|---|---|---|---|
| 17-10-15 | 6270 | 1.000 | 0.991 | 1.011 | 97 to 98 percent | 0.7928 |
| 17-44-20 | 19654 | 1.000 | 0.984 | 1.018 | 92 to 93 percent | 0.7928 |
| 18-02-32 | 7560 | 1.000 | 0.975 | 1.022 | 87 to 91 percent | 0.7728 |

The replayed gain spans `0.766..0.849`, inside the code range. A free linear
fit of each closed-loop pulse word against `BFS * STFT / 0x6400 / 20.48` gives
slope 0.87 to 0.89 and an additive 42 to 53 raw at correlation 0.99 on both
banks. The gain rises with load, so that fit reports a slope above the local
gain and an intercept below the 66 to 87 count opening time; the replay with
the code-defined gain and intercept removes both offsets. The factor 20.48 is
the ratio of the `raw/2048 ms` BFS scale to the `raw/100 ms` pulse scale.

## Override word

`FUN_00056FC0` uses `FUN_000224F8`, whose exact leaf contract is arithmetic
right shift by seven. Stock constants are `ROM8[0x84F6] = 92` and
`ROM8[0x8C9E] = 70`. The resulting word is:

```text
0xFFFF2436 = clamp_u16(max(0,
    arithmetic_shift7((175 - uint8[0xFFFF1108]) * 92) + 70))
```

The word is added to both normal parity-base calculations and directly replaces
the parity base for a channel selected by `0xFFFF22E0`. Its physical unit and
sensor interpretation require hardware validation.

## Duration path to the ATU-II outputs

Both pulse producers reach the same six ATU-II channel-8 one-shot outputs
through `FUN_0002C13C`, which takes an aggregate channel mask and a pointer to
six consecutive duration words.

The main path carries the transformed array through the scheduler snapshot:

```text
0xFFFF23C8 + 2*i    raw compensated pulse words, DID 0x1206
  -> FUN_0005B7EC   affine minimum-pulse floor
0xFFFF23D4 + 2*i    transformed pulse words
  -> FUN_00020DFE   periodic 140-byte copy of 0xFFFF23BC to 0xFFFF2330
0xFFFF2348 + 2*i    snapshot of the transformed words
  -> FUN_00054D3E   source selection and per-channel lower bound
0xFFFF224E + 2*i    scheduled durations
  -> FUN_0002C13C   ATU-II DCNT8A..DCNT8F and DSTR
```

At `0x21314` `FUN_00020DFE` calls byte copier `FUN_00022558` with source
`0xFFFF23BC`, destination `0xFFFF2330`, and length `0x8C`, so every word of
producer block `0xFFFF23BC..0xFFFF2447` has a snapshot 140 bytes below it.
`0xFFFF2348` is the snapshot of `0xFFFF23D4`, `0xFFFF2390` of `0xFFFF241C`, and
`0xFFFF23AA` of override word `0xFFFF2436`.

`FUN_00054D3E` selects what fills the duration array:

| Condition | Six words filled from |
| --- | --- |
| `0xFFFF418C.bit1` set or `0xFFFF24A0.bit6` clear | `0xFFFF23AA` |
| `param_1 == 0` | `0xFFFF238A` |
| `param_1` in 1, 2, 4 | start word selected by `param_1` |
| otherwise | `0xFFFF2348 + 2*i`, floored at `0xFFFF2390` |

The start branch compares `uint16[0xFFFF23AA] + (ROM16[0x94E8] * 100 >> 8)`
against `0xFFFF2388`, conditionally subtracts `0xFFFF238A` from `0xFFFF2386`,
and floors the result at `0xFFFF238C`, `0xFFFF238E`, or `0xFFFF2392` for
`param_1` 1, 2, and 4.

The three functions that pass `0xFFFF224E` to `FUN_0002C13C` (`FUN_00029588`,
`FUN_0002BE40`, `FUN_00054A44`) each refill it through `FUN_00054D3E` first.
The fourth caller, `FUN_00051F1E`, passes `0xFFFF1568` with mask `0xFFFF1220`.
That array is the mask-gated per-channel path: `FUN_00051A98` writes
`0xFFFF155C + 2*i` and stores `FUN_0005B7EC` of that word to
`0xFFFF1568 + 2*i`. For channel `i` its stock branch is:

```text
base = arithmetic_shift6(uint8[0xFFFF152C] * uint8[0xFFFF1527])
base = max(0, base +/- uint8[0xFFFF15D8])   sign from 0xFFFF2484.bit0
add  = 0x32 if bit i of uint8[0xFFFF1574] else 0
q    = sat_u16((int16[0xFFFF142E + 2*i] * (base + add)) >> 10)
q    = sat_u16((uint16[0xFFFF165E] * q) >> 13)
0xFFFF155C + 2*i = sat_u16(q + uint16[0xFFFF2436])
```

`FUN_0002C13C` gates on `0xFFFF4184.bit7` and, per channel `i`:

```text
d = duration[i]
if bit i of 0xFFFF22E0 or of history 0xFFFF1935:
    d = uint16[0xFFFF23AA]; set bit i of 0xFFFF1935
if bit i of DSTR is already set:
    d = max(0, d - uint16[0xFFFF23AA])
c = sat_u16((800 * d) >> 8)
if 0xFFFF4251.bit0: c = 1000
DCNT8x += c with interrupts masked; set bit i of DSTR
```

Substituting the injector opening time for an inhibited channel and removing it
again when a pulse is already in flight are consistent only if the duration
words and `0xFFFF23AA` share one unit.

## Injection-pulse time scale

The ATU-II programming fixes that unit absolutely.

`FUN_000274AC` writes `PSCR1 = 1` at `0xFFFFF404`, so the prescaler output is
`phi' = Pphi / 2`. `FUN_0002718A` writes `TCR8 = 0x55` at `0xFFFFF668`, so
`CKSELA = 5` selects `phi' / 32` for down-counters `DCNT8A..DCNT8H`. The six
injector channels count at `Pphi / 64`. With `Pphi = 20 MHz` established from
the target CAN base interval in [`JK08A.dfco.md`](JK08A.dfco.md), one counter
step is `3.2 us`.

`FUN_0002C13C` programs `DCNT8x += sat_u16(800 * d / 256)`, so one duration
count is `3.125` counter steps:

```text
t = d * (800 / 256) * (64 / Pphi) = d * 200 / Pphi = d * 10 us
```

Every word on both duration paths is therefore in `10 us` units, full scale
`655.35 ms`:

| Word | Content |
| --- | --- |
| `0xFFFF23C8 + 2*i` | compensated pulse, DID `0x1206`, `ms = raw / 100` |
| `0xFFFF23D4 + 2*i` | the same words after the minimum-pulse floor |
| `0xFFFF224E + 2*i` | scheduled duration |
| `0xFFFF155C + 2*i`, `0xFFFF1568 + 2*i` | mask-gated per-channel path |
| `0xFFFF2436`, `0xFFFF23AA` | injector opening time |
| `0xFFFF241C`, `0xFFFF2390` | minimum pulse |
| `0xFFFF2412..0xFFFF241E` | start durations |
| `0xFFFF191C`, `0xFFFF191E` | parity pulse bases |
| `0xFFFF1876`, `0xFFFF18C0`, `0xFFFF18C2` | common and bank precursors |

The forced value `1000` behind `0xFFFF4251.bit0` is `3.2 ms` expressed in
counter steps, not a duration word.

Independent magnitudes agree with the scale:

- Override word `0xFFFF2436` holds `70` counts, `0.70 ms`, at battery snapshot
  `0xFFFF1108 = 175` and moves `92/128` counts per byte. At `0.08 V` per count
  that byte is `14.0 V` and the slope is `0.09 ms/V`;
  over the recorded byte range `157..180` the word spans `0.66..0.82 ms`. That
  is the opening time of a port injector.
- The stock `FUN_0005B7EC` floor `max(x, 0.8335*x + 25.94)` enforces a minimum
  pulse of `0.26 ms` and stops acting at `1.56 ms`.
- Precursor minimum `ROM16[0x94E8] = 170` is `1.70 ms`. The recordings of
  2026-09-17 give warm-idle medians of `3.53`, `3.60`, and `3.62 ms` and a
  maximum of `14.08 ms` at `3587.5 rpm`, which is 42 percent of the `33.4 ms`
  engine cycle at that speed.

The same arithmetic fixes the Base Fuel Schedule scale at `raw / 2048 ms`.
Every stage between the schedule and the pulse words carries its own
normalizer:

```text
FUN_0004E974   S * M / 131072        M = 0x4000 at unity          1/8
FUN_0004E974   H * B / 0x6400        B = 0x6400 at unity          1
FUN_0004E974   X * G / 16384         G = common gain 0xFFFF165E   G/16384
FUN_0004EAD4   I * trim / 65536      trim = 0x6400 at neutral     100/256
```

The product of the fixed normalizers is `(1/8) * (100/256) = 100/2048`, so at
unity multipliers, unity gain, and neutral trims the pulse before opening time
is `floor(BFS * 100 / 2048)` counts of 10 us: one schedule count is
`1/2048 ms` of pulse. Common gain `G / 16384` is the only factor that never
reaches unity; its code range `0.7495..0.8494` is the ratio of the delivered
pulse to the schedule. The adjacent scales `raw / 1024 ms` and `raw / 4096 ms`
would need a gain of `0.39` or `1.57`, outside that range. The chain replay
under [Active-vehicle reproduction](#active-vehicle-reproduction) reproduces
the recorded pulse words at a median ratio of `1.000`.

## Injection timing

Each pulse is placed by crank angle. The delay runs from the reference engine
event of the scheduled cylinder to the end of the pulse:

```text
0x12302, 0x1230A             injection-end delay tables, 4 crank degrees per count
  -> FUN_00056BD0            0xFFFF192E = 2 * min(y, 209), 2 crank degrees per count
  -> FUN_000521A8            start delay = end delay - pulse angle
0xFFFF23F0, 0xFFFF23BF       lead in 120-degree events, start angle / 4
  -> FUN_00020DFE            snapshots 0xFFFF2364 and 0xFFFF2333
  -> FUN_00054A44            slot selection on every engine event
  -> FUN_0002B64A            ATU-II GR1A compare for the start angle
  -> FUN_0002BE40            compare-match handler fires the pending channel mask
```

`FUN_000521A8` takes the longest of the six transformed pulse words and floor
`0xFFFF241C`, in `10 us` counts, and the engine-speed word in RPM/12.5
(`0xFFFF11BC`, or `0xFFFF10CA` while `0xFFFF4184.bit6` is set):

```text
k = ((speed << 4) * ROM32[0x522A8]) >> 16      ROM32[0x522A8] = 0xC49B
p = min((k * pulse) >> 16, 255)                pulse angle, 4 crank degrees per count
E = uint16[0xFFFF192E]
d = 2 * E - 4 * p  if E >= 2 * p  else 0       start delay, crank degrees
d = max(d - ROM8[0x83EA], 0)                   only while 0xFFFF24C9.bit5 is set; stock 30
0xFFFF23F0 = d / 120                           forced to 3 while 0xFFFF4251.bit0 is set
0xFFFF23BF = clamp(d % 120, 4, 116) / 4
```

Three constants fix the angle domain. `p = rpm * t * 1.49998` while the crank
turns `rpm * t * 6` degrees, so one count of `p` is 4 crank degrees. Divisor 120
is the engine-event spacing of a six-cylinder four-stroke engine. `FUN_0002B64A`
splits the same angle by the 10-degree crank tooth. One count of `0xFFFF192E`
is therefore 2 crank degrees and one cell count of tables `0x12302` and
`0x1230A` is 4 crank degrees. The stock base table holds 133 in all eight
cells, 532 crank degrees; the conditional table holds 160..200, 640..800 crank
degrees. A whole-ROM scan finds `FUN_000521A8` as the only reader of
`0xFFFF192E`. The pulse angle comes from the longest of the six pulses, so the
end delay is exact for that channel.

Diagnostic word `0xFFFF162E` is outside this path. Both service-`0x22` pointer
tables return its high byte as DIDs `0x1131`, `0x1132`, `0x1133`, and
`0x113D`, which public definitions name fuel-injection timing. The word has no
runtime producer: startup initializer `FUN_00027C50` clears it, and a
whole-program p-code scan with computed-address candidates, a
constant-propagation sweep of register-relative accesses, and the block-copy
groups of scheduler walkers `FUN_00020DFE` and `FUN_000209D8` find no other
access. The four DIDs publish a constant zero, and all 143961 records of the
2026-09-17 recordings, made with telemetry profile 3, stream 0. The live
end-of-injection angle is `0xFFFF192E`, which the tuning telemetry profile
streams in place of the diagnostic word.

`FUN_00054A44` is entry 1 of the ten-entry engine-event task table at `0x21B5C`
and runs from feeder `FUN_000208F8` on every engine event. With `n` the
engine-event cylinder index `0xFFFF11DE` in 1..6:

```text
lead = 0xFFFF2364 if 0xFFFF8513.bit5 else 3
slot = (n - 1 - lead) mod 6                                    0xFFFF20B4
if 0xFFFF84EC.bit7:                        delayed start of the previous event still pending
    refill 0xFFFF224E; fire mask 0xFFFF2228; clear TIER1A bit 0
delta = 0xFFFF221D - lead
delta == 0: accept slot only if slot == (0xFFFF221E + 1) mod 6
delta >  0: advance 0xFFFF221E through delta skipped slots, fire their masks at once, accept slot
delta <  0: accept no slot
0xFFFF2228 = ROM8[0x22695 + slot] if a slot is accepted else 0     cells 02 04 08 10 20 01
0xFFFF221D = lead
FUN_0002B64A(0x34 if 0xFFFF4251.bit0 else 4 * 0xFFFF2333)
```

The body after the slot calculation runs only while bits 7..5 of `0xFFFF8513`
are all set. Engine-event driver `FUN_00029588` sets bit 6 after the first
grouped pulse, whose masks come from `ROM8[0x226A2 + n]` (`00 18 30 21 03 06
0C`), and bit 5 once start-event count `0xFFFF2298` reaches 4. While P0335
fallback snapshot `0xFFFF24C9.bit5` is set and `0xFFFF8513.bit4` is clear, the
sequencer sets bits 7..4 itself and seeds `0xFFFF221E` with the slot before
the current one and `0xFFFF221D` with the lead. Every fired mask is ORed into `0xFFFF20B5`,
`0xFFFF157E`, and `0xFFFF16FE`, removed from DFCO fallback history
`0xFFFF1935`, and, with stock `ROM8[0x8D92]` bit 3 set, ORed into `0xFFFF14C3`
and `0xFFFF14C2`.

`FUN_0002B64A` sets pending flag `0xFFFF84EC.bit7`, splits its angle by ten
through `FUN_00028E7C` into tooth count `0xFFFF13B8` and remainder
`0xFFFF193B`, and, when the count is zero, writes
`GR1A = 0xFFFF158A + 0xFFFF22BC * remainder / 10`, or `TCNT1A + 2` when that
instant has passed. `0xFFFF22BC` is the time of one 10-degree crank tooth in
`3.2 us` channel-1 counts and `0xFFFF158A` is the crank reference capture of
the current event. It then clears `TSR1A` bit 0 and sets `TIER1A` bit 0. In
P0335 fallback (`0xFFFF24C9.bit6`) an angle of 120 or more becomes count 1
with remainder `angle - 120`. Handler `FUN_0002BE40` clears the pending flag
and fires mask `0xFFFF2228` on the compare match.

### Reference tooth and cylinder order

The reference engine event is tooth 7 of the crank signal plate. The plate
carries ten teeth at 10-degree pitch per 120 crank degrees with two missing
teeth between tooth 7 and tooth 8. The ICI0A input-capture handler (vector 84,
prologue `0x28EA2`, body `FUN_00029588`) runs on every tooth:

```text
0xFFFF158A = OSBR1                                 tooth capture, 3.2 us counts
0xFFFF22BA = capture - previous capture            tooth interval
0xFFFF196C = min(255, 64 * previous / current)     gap ratio, 192 on tooth 9
ratio > ROM8[0x8C89] = 118 and count >= 8          sets gap flag 0xFFFF84E9.bit7
next tooth: 0xFFFF13B4 = count; 0xFFFF13B2 = 0     sets sync flag 0xFFFF8501.bit7
tooth 8 with sync: 0xFFFF22BC = interval / 3       multiplier 0x5555 >> 16
other teeth:       0xFFFF22BC = interval           time of 10 crank degrees
```

Relative to tooth 7, teeth 8, 9, 0, 1, 2, 3, 4, 5, 6, and 7 follow at 30, 40,
50, 60, 70, 80, 90, 100, 110, and 120 degrees. Normalizer `FUN_00028DC8`
converts a count of 10-degree steps into a count of tooth events and is exact
for this layout only: from tooth 7 it maps 1 and 2 to zero events with 10 and
20 degrees added to the remainder, 3..12 to `count - 2`, 13 and 14 to ten
events with the same remainders, and 15..24 to `count - 4`.

Tooth 4 identifies the cylinder from the cam edge counts and tooth 7 copies it
to event index `0xFFFF11DE` before feeder `FUN_000208F8` runs the engine-event
tasks. Ignition command `ROM8[0x83D5] - advance = 110 - advance` is the delay in
crank degrees after that tooth, so tooth 7 is 110 degrees before compression
TDC of the event cylinder and TDC falls on tooth 6. The event index is the
cylinder number. The misfire interval captured on tooth 9 of event index `c`
spans 50..170 degrees after compression TDC of index `c - 2`; detection core
`FUN_00085A70` tests interval `T[n-7]`, which is congruent to `T[n-1]` and lies
on the expansion stroke of index `c - 3`, and charges it to cylinder number
`ROM8[0x2265C + c] = c + 3` modulo six. `FUN_00084AA4` and reporter
`FUN_00084CD0` report counter element 1 as P0301 and element 6 as P0306. The
index advances 1-2-3-4-5-6, the firing order.

The sequencer accepts channel bit `(n - lead) mod 6`, whose reference event is
tooth 7 of event index `c0 = n - lead`. Channel bit `k` drives the injector of
cylinder `k + 1`: service 0x30 IOLID `0x0C` Power Balance replaces the same
six-channel mask bit for bit, and the Nissan-family diagnostic profile assigns
its bits 1, 2, 4, 8, 16, and 32 to cylinders 1 through 6. The injected cylinder
`c0 + 1` fires 120 degrees after cylinder `c0`, so the reference tooth is 230
degrees before its compression TDC and 130 degrees after its intake TDC:

```text
end of injection = 130 + D degrees after intake TDC
                 = D - 590 degrees after the following intake TDC
0x12302   133 counts, 532 degrees       58 degrees before intake TDC
0x1230A   160..200 counts, 640..800     50..210 degrees after intake TDC
saturation 209 counts, 836 degrees      246 degrees after intake TDC
```

The start delay is never negative, so a pulse starts no earlier than 130
degrees after the preceding intake TDC of its cylinder. `FUN_00056BD0` selects
table `0x1230A` while `0xFFFF2484` bits 4 and 5 and warm latch
`0xFFFF41D0.bit1` are all set; the latch sets at raw coolant
`ROM8[0x8770] = 120`, 70 deg C, and releases below 115. The base path adds
`uint8[0xFFFF340C]` to the table value.

While bits 7..6 of `0xFFFF8513` are set and bit 5 is clear, the lead is 3 and
the tooth-9 path of `FUN_00029588` programs the delayed start with angle
`ROM8[0x8D5F] = 0`, or `ROM8[0x8D60] = 92` while `0xFFFF24CA.bit1` is set. The
pulse then starts 190 or 98 degrees before intake TDC of the injected cylinder.
The first grouped pulse on tooth 4 opens channel bits `j + 2` and `j + 3` of
current cylinder `j` from `ROM8[0x226A2 + j]`. These are cylinders `j + 3` and
`j + 4`, 20 and 140 degrees before their intake TDC: the two cylinders whose
start-phase injection instant has passed and whose intake stroke has not begun.

The angles are firmware coordinates. The mechanical offset between the crank
sensor and the signal plate is a hardware boundary, and the injector channel
order rests on the family Power Balance bit assignment and is not measured
electrically.

### Homologous targets

JK00C, JK00D, JK78C, the 1ND pair, and 1ME3B carry the same chain, so their
end-of-injection word has the JK08A coordinate: `raw * 2 - 590` degrees after
intake TDC of the injected cylinder. The 1ND addresses are those of `1ND0A`;
`1ND3B` is byte-identical over every listed range.

| Stage | JK08A | JK00C | JK00D | JK78C | 1ND | 1ME3B |
| --- | --- | --- | --- | --- | --- | --- |
| writer with the 209-count clamp and doubled store | `0x56BD0` | `0x58AE4` | `0x58AE0` | `0x730CC` | `0x7F4E0` | `0x841B4` |
| end-of-injection word | `0xFFFF192E` | `0xFFFF1992` | `0xFFFF1996` | `0xFFFF192A` | `0xFFFE89A2` | `0xFFFE8946` |
| reader | `0x521A8` | `0x53BF8` | `0x53BF4` | `0x6E12C` | `0x79D2E` | `0x7E736` |
| fallback subtraction | `ROM8[0x83EA] = 30` | `ROM8[0x83EC] = 30` | `ROM8[0x83EC] = 30` | `ROM8[0x839D] = 50` | `ROM8[0x83B9] = 50` | `ROM8[0x83C0] = 50` |
| engine-event task table | `0x21B5C` | `0x21BE8` | `0x21BE8` | `0x21C8C` | `0x222A8` | `0x22324` |
| sequencer, entry 1 | `0x54A44` | `0x56978` | `0x56974` | `0x70EDC` | `0x7D3E8` | `0x81EEC` |
| slot masks `02 04 08 10 20 01` | `0x22695` | `0x22721` | `0x22721` | `0x226FD` | `0x22A55` | `0x22AC9` |
| delayed-start programmer | `0x2B64A` | `0x2C2D2` | `0x2C2D2` | `0x2E52E` | `0x2F48E` | `0x321D6` |
| tooth-count normalizer | `0x28DC8` | `0x29A50` | `0x29A50` | `0x2B820` | inlined | inlined |
| tooth dispatch on 4, 6, 7, 8, 9 | `0x2965A` | `0x2A2E2` | `0x2A2E2` | `0x2C0DE` | `0x2D082` | `0x2FEC2` |
| event index | `0xFFFF11DE` | `0xFFFF11EE` | `0xFFFF11EE` | `0xFFFF11C8` | `0xFFFE81D6` | `0xFFFE81BC` |
| feeder | `0x208F8` | `0x20926` | `0x20926` | `0x2095C` | `0x20CF4` | `0x20D04` |
| ignition task, entry 4 | `0x4E162` | `0x4FAB2` | `0x4FAAE` | `0x69A80` | `0x74AFA` | `0x78F14` |
| ignition reference constant `110` | `ROM8[0x83D5]` | `ROM8[0x83D8]` | `ROM8[0x83D8]` | `ROM8[0x838F]` | `ROM8[0x83AB]` | `ROM8[0x83B2]` |
| set-edge scheduler | `0x2A892` | `0x2B51A` | `0x2B51A` | `0x2D6F6` | `0x2E464` | `0x311B2` |
| misfire attribution map | `0x2265C` | `0x226E8` | `0x226E8` | `0x226C4` | `0x22A1C` | RAM `0xFFFEEA58` |

The JK08A sequencing constant block `0x22658..0x226A9`, which holds the misfire
attribution map, the successor and reset-mask cells, the slot masks, and the
grouped-pulse masks, is byte-identical in the four images at offsets `+0x8C`,
`+0x8C`, `+0x68`, and `+0x3C0`. 1ME3B holds the same cells without the ROM
attribution map and its pad byte: JK08A `0x22658..0x2265B` lies at `+0x43C` and
`0x22664..0x226A9` at `+0x434`, and the byte string `00 04 05 06 01 02 03`
occurs nowhere in the image.

Every reader computes `k` with constant `0xC49B`, forms `d = 2 * E - 4 * p`,
divides by 120, and clamps the remainder to 4..116; 1ND and 1ME3B divide inline
through reciprocal `0x88888889`. Every sequencer computes `slot = (n - 1 - lead) mod 6`
with default lead 3, reads the slot mask cell, and passes `0x34` or four times
the start snapshot to the delayed-start programmer. Every programmer splits the
angle by ten and applies the normalizer mapping of JK08A, including ten events
for counts 13 and 14 and `count - 4` for 15..24, so the plate layout of ten
teeth per 120 degrees with the gap after tooth 7 holds in every target. 1ND
and 1ME3B inline the division by ten and the mapping in the programmer.

On tooth 7 every tooth handler copies the identified cylinder to the event
index, forms ignition set mask `1 << (index - 1)`, and calls the feeder. The
ignition task computes the command as the reference constant minus the final
timing byte and hands it to the set-edge scheduler, which splits it by ten, so
tooth 7 is 110 degrees before compression TDC of the event cylinder in every
target. 1ND and 1ME3B inline the command builder into the ignition task, and
the 1ME3B handler forms the set mask through runtime shift helper `0x22674`.
The 1ME3B reader, sequencer, programmer, ignition task, scheduler, and feeder
decompile to the 1ND bodies with other displacements and flag bits.

The tooth-9 path of every handler indexes the misfire attribution map with the
event index. The misfire metric helper keeps the JK08A interval-history
displacements in JK00C and JK00D (`FUN_0008B308`) and in JK78C
(`FUN_000A8B72`). 1ND forms its misfire metric through a different algorithm
whose interval lag is not decompiled, so its identity of event index and
cylinder number rests on the attribution map and the identical attribution
read.

1ME3B keeps the attribution map in RAM. The first pass of tooth handler
`FUN_0002F730` after reset writes `0xFFFEEA58..0xFFFEEA5E` from immediates:
`00 04 05 06 01 02 03`, the JK08A map, while `0xFFFEBA4D.bit0` is set, and
`00 05 06 01 02 03 04` while it is clear. The block `0x2F784..0x2F7C6` runs
only while the byte `0xFFFEB7B6` is zero, and its last store at `0x2F7C4` sets
that byte to 1. `FUN_00034340`, which reset entry
`FUN_0002E23A` reaches through `FUN_0002DF4E` before its main loop first lowers
the interrupt mask at `0x2E444`, derives the bit from the misfire interval
teeth, start tooth `a = ROM8[0x8AF0]` and end tooth `b = ROM8[0x8AEE]`:

```text
a >= b   bit = not (a >= 7 and b < 7)
a <  b   bit = a < 7 and b >= 7
```

The bit is set exactly when tooth 7, which advances the event index, lies
inside the interval, so both maps charge cylinder `c + 4` of the event index
`c` at the start tooth. Stock teeth `9` and `9` set the bit and select the
JK08A map. The handler builds the map once per reset, on its first pass, from
the bit as it stands then. The tooth-9 path stores the interval to
`0xFFFE8D50` and the attributed cylinder to `0xFFFEB778` with the 1ND
instruction sequence, and the 1ME3B misfire metric is not decompiled, so the
identity of event index and cylinder number rests on this map as it does for
1ND.

The JK08A hardware boundaries apply to every target: the mechanical
offset between the crank sensor and the signal plate, and the injector channel
order from the family Power Balance bit assignment.

## Hardware validation priorities

The minimum controlled validation set is:

1. Record exact DID `0x1208` BFS, DID `0x1206` compensated injection pulse,
   STFT/LTFT, RPM, MAF, lambda, and the six output waveforms on a bench or engine.
2. Apply a bounded single-region change to Fuel Compensation Main `0xA29A` and
   verify the expected multiplicative movement in BFS and pulse duration.
3. Trigger DFCO and RPM cut conditions separately and compare
   `0xFFFF22E0`-equivalent behavior with all six electrical outputs.
4. Measure injector-terminal pulse width against exact DID `0x1206` at several
   battery voltages to confirm the `10 us` duration count and the modeled
   opening time `0xFFFF2436`, and confirm that channel-8 output `i` drives
   the injector of cylinder `i + 1`.
5. Retain Map 1 storage for the DFCO held-request and intermediate-restore
   thresholds until FAIL-BOOT is fixed and base map switching is confirmed on
   hardware; only then add Map 1-5 Hold and Intermediate support.
