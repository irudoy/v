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
Q = int32[0xFFFF1E38]
F = ROM8 [0x8A27] = 109
K = ROM16[0x9284] = 26806
E = ROM8 [0x88FB] = 3
N = selected engine-speed count, lower-bounded at 64
```

For positive Q and a nonzero denominator, the exact integer sequence is:

```text
p = floor(F*K*uint32(Q)/256)
t = p modulo 2^40
fixed = min(floor(t/(E*N)), 0x726F9)
0xFFFF1E40 = floor(fixed*9163/65536)
```

Nonpositive signed Q publishes zero. A zero denominator with positive Q selects
the fixed cap without calling the division helpers. The normal word-speed mode
selects unsigned `0xFFFF11E8` or `0xFFFF11DC` by `0xFFFF2461.bit5`; the other
mode uses eight times its cached unsigned `0xFFFF2804` byte. Every selected
count is lower-bounded at 64. The pre-entry selector is statically bound;
independent execution begins at `0x3B7C6` with its selected context.

The complete bank-contribution and aggregate proofs bound coherent stock Q at
`2*0xFFFFFF+0x7FFF+0xFFFF=0x02017FFC`. With stock F and K, p stays below
`2^40` over that domain, so the simpler unbounded product gives the same result.
Wide positive Q and changed fixture coefficients execute the 40-bit wrap as
software boundaries without establishing live reachability or calibration
validity.

The following Q7 consumer uses cached quarter BFS, rather than rereading its
longword, and publishes:

```text
product = uint32(cached_quarter * uint8[0xFFFF1160])
0xFFFF1062 = min(65535, floor(product/128))
```

For coherent quarter BFS, the cached value equals `0xFFFF1E40` and is at most
65535. Direct consumer cases also execute mismatched and wide cached values;
they establish the operand and product width without asserting a live RAM race.

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

`FUN_0003BD74` contains the live accessor for Fuel Compensation Main `0xA29A`.
At `0x3C284..0x3C29C`, the active lookup path uses wrapper `0x261F0` with row
axis `0x11CF0` over RPM/12.5 word `0xFFFF11F4` and column axis `0x11D4C` over
byte `0xFFFF1170`, then writes the uint8 result to `0xFFFF1160`. Runtime
gates select the surface when `ROM8[0x8B42].bit5` is set,
`ROM8[0x8B34].bit4` is clear, or `ROM8[0x8B42].bit0` is clear and
`ROM8[0x8B34].bit1` is set. Otherwise the selected unsigned bypass byte is:

| Condition | Source |
|---|---|
| `0x8B42.bit0` set, `0x86F9.bit1` set | `ROM8[0x851A]` |
| `0x8B42.bit0` set, `0x86F9.bit1` clear | `RAM8[0xFFFF5625]` |
| `0x8B42.bit0` clear | `RAM8[0xFFFF2836]` |

The bypass clamps its byte to `64..192` and publishes the same destination,
without invoking the surface. The fixed control bytes are calibration inputs;
their physical mode identities and the preceding bypass-state writers are
separate verification items.

Each axis clamps below its first point and from its last point upward. Within
a cell, the kernel returns the unsigned truncated Q0.16 fraction
`floor((coordinate-a)*65536/(b-a))`. Row points are multiplied by four before
this calculation; column points are direct bytes. The byte finisher applies
the following directional interpolation to columns of each active row, then
to those row results:

```text
L(a,b,f) = a + floor(max(0,b-a)*f/65536) - floor(max(0,a-b)*f/65536)
```

A zero fraction uses the exact cell without reading its next neighbor. When
both fractions are zero, the natural wrapper can sign-extend the byte; the
coordinator's byte store publishes its unsigned low eight bits. Descending
increments and the column-first order distinguish this contract from flooring
a weighted average. The row input is the coherent cached unsigned word loaded
from `0xFFFF11F4`, rather than a fresh read at the lookup. The executable gate
binds this cache association statically, executes both selector arms, the axes,
divider, finisher, and store, and checks input, calibration, MACL, and GBR
preservation. It does not execute preceding state writers.

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

The cached unsigned byte `RAM8[0xFFFF24B1]` selects the rate arm. With bit 4 set:

```text
0xFFFF1DEE = min(65535, max(P - T, 0) >> 15)
```

With bit 4 clear, the candidate is `min(65535, (P + T) >> 15)`. The stock
overflow test selects `0xFFFFFFFF` before the word cap when `T >= ~P`;
that path bypasses the shifts and also publishes 65535. A candidate below
`min(65535, 4*f)` advances by one only when it equals the previous working
word. The difference arm has no such increment. The two 15-bit sequences
include the sum's final shift in a delay slot. `ROM8[0x8D92].bit4` controls
the subsequent blended publication rather than this rate selection.
`FUN_0003BD74` also publishes `0xFFFF115C`; its selected source can be a
calculated word, a parallel working word, or stock constant
`ROM16[0x90EE] = 0x020C` according to runtime state. `0xFFFF115C` is therefore
not the `0xA29A` result and must not be merged with `0xFFFF1160` in a definition
or patch.

The alpha-N byte `0xFFFF1170` sets `0xFFFF24B1.bit7` when it is at least the
upper calibration byte and `uint16[0xFFFF1E06] >= 4*f`. Otherwise a byte below
the lower calibration clears bit 7; intermediate contexts retain it. Other
bits are preserved. JK08A holds 202 and 200 at `0x8319` and `0x831A`.

Timers `0xFFFF1E20` and `0xFFFF1E47` select four under `0xFFFF2449.bit7`
and `0xFFFF4250.bit6`, respectively, or decrement toward zero. Mode bit 3
of `0x8D92` enables the query/timer arm. The call at `0x0003BA66` passes
signed word -1, for which the natural diagnostic predicate at `0x000259E4`
returns zero. The third timer `0xFFFF1E4C` therefore decrements; its
refresh-to-four arm requires an artificial nonzero query result in the
bounded executable fixture. Any active updated timer sets `0xFFFF244E.bit7`;
all zero timers clear it. Mode bit 3 clear preserves the third timer and
the entire monitor byte.

Signed correction requires `0xFFFF2462.bit0`, `0xFFFF24BD.bit2`, clear
`0xFFFF24B1.bit7`, and zero first/second timers:

```text
R7 = clamp(floor((uint16[0xFFFF1DEE] - uint16[0xFFFF1E06]) *
                 ROM8[0x865A] / 64), -32768, 32767)
0xFFFF1060 = int16(R7)
```

Other contexts publish zero. The natural helper at `0x000224FA` performs
six arithmetic right shifts, including its return delay slot, so negative
division rounds down. JK08A holds gain 160. The limiter consumes cached R7
after the word publication, without rereading that RAM cell in this slice.

Mode bit 4 enables `0xFFFF1DEC` publication. Enable bit 0, clear diagnostic
bit 2, and set latch bit 7 select:

```text
A = uint8[0xFFFF1EE1]
0xFFFF1DEC = (A * uint16[0xFFFF1DEE] +
              (256 - A) * uint16[0xFFFF1E04]) >> 8
```

Other enabled contexts copy `0xFFFF1DEE`; mode bit 4 clear preserves the
previous blended word. This publication does not add the signed correction.
RPM curve `0x12C9E` normally caps the selected, signed-corrected result before
it is written to `0xFFFF1026`; an alternate mode uses direct grid `0x974E`.

With `0xFFFF2449.bit7` clear, the limiting slice uses unsigned blended word
`0xFFFF1DEC` when `ROM8[0x8D92].bit4` is set, or unsigned unblended word
`0xFFFF1DEE` otherwise. It adds the cached signed correction word also stored
at `0xFFFF1060` and clamps the candidate at zero. The coordinate byte
`0xFFFF11EB` selects the implicit 16-point byte curve with 16-count spacing.
Below coordinate 240, each directional increment truncates down separately:

```text
i, fraction = divmod(coordinate, 16)
a = ROM8[0x12C9E+i]
b = ROM8[0x12C9E+i+1]
cell = a + floor(max(0,b-a)*fraction/16) - floor(max(0,a-b)*fraction/16)
0xFFFF1E46 = cell
0xFFFF1026 = min(max(0, selected_word + signed_correction), cell*256)
```

Coordinates from 240 upward use cell 15 directly; the caller makes its signed
byte return unsigned before the shift and comparison. Stock cells 0 and 1
are 101, and cells 2 through 15 are 255. The corresponding bounds are 25856
at coordinates up to 16 and 65280 from 32 upward. Descending interpolation
differs from flooring an unbounded weighted average.

With bit 7 set, the branch bypasses the correction and curve. RPM/12.5 byte
`0xFFFF11EA` selects rows below 64, 128, and 192; at or above 192 it publishes
zero. Absolute-throttle byte `0xFFFF1075` selects columns below 7, 15, and 22,
or the last column otherwise. A selected grid cell is shifted left eight;
this branch preserves `0xFFFF1E46`. Independent execution covers both paths
through the exact word store. Preceding state writers remain outside that
slice. The exact mode-byte record applies to JK08A, which holds `0x7A`;
JK00A shares layout `7mfk` and holds `0x7E` at that address.

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
P = uint32(I_b * trim_b)
v = uint16[0xFFFF2436] + floor(P / 65536)

if I_b != 0:
    v = floor(uint32(256*v + offset_b - 0x8000) / 256)

0xFFFF191C + 2*b = min(v, 65535)
```

The product and offset expression retain their low32 machine values before
logical shifts. I_b=0 bypasses the offset read and correction. The bounded
bank-base contract states the full unsigned-word consumer domain.

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

`FUN 00057B26` publishes the LTFT diagnostic word from the selected learned
cell and the adjustment term. The legal bank is b=uint8(full incoming R4) in 0..1; its upper 24 bits are independent of b.

```text
raw_b = uint32(uint16[0xFFFF2306 + 2*b] + uint16[0xFFFF5648 + 2*b] - 0x6400)
```

Limiting is skipped when bit `b` of `0xFFFF230E` is set, or when
`uint16[0xFFFF15FC] <= int16[0xFFFF15FE]`: `extu.w` at `0x57B60` zero-extends
the first word, the load at `0x57B62` sign-extends the second, and `cmp/gt` at
`0x57B64` compares them as signed 32-bit values. Otherwise the raw uint32 value
is limited by unsigned comparisons between two adjacent ROM bytes scaled to
Q8.8 percent:

```text
raw_b = min(max(raw_b, ROM8[0x8E5B] << 8), ROM8[0x8E5A] << 8)
ROM8[0x8E5B] = 90, ROM8[0x8E5A] = 110
```

Four independent conditions replace the result with exactly neutral `0x6400`
before the store to `0xFFFF2302 + 2*b`. The final word store publishes uint16(raw_b) unless a neutral condition selects 0x6400.
The independent neutral conditions are:

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

## Bounded bank base-pulse builder

The complete natural-return `bank_base_pulse_builder/fn` at
7mfk:0004ead4 has an independently reconstructed GNU SH-2E contract of
103 instructions, 232 bound bytes and 6184 literal cases. Its stock RTS
at 0004eb9e executes the MACL-restoring delay slot at 0004eba0. The three
high-RAM pointer pools at 0004ec00/0004ec04/0004ec08 are the declared
simulator aliases; the ROM pointer and arithmetic constant FFFF3800
retain their stock values. No call, MMIO access or exception return occurs
within this envelope.

Full incoming R4 is an independent context; its low byte b is admitted
only in 0..1. Each numerical operand is interpreted by this bounded
consumer as an unsigned16 RAM word. The first and second banks have
S at ffff22dc+2*b, L at ffff2302+2*b, E at ffff2a24+2*b,
I at ffff18c0+2*b and O at ffff2310+2*b. Common A is at ffff2436.
ROM8[00008940].bit4 selects control C at ffff22e8 when set or
ffff22e6 when clear. Include L if ROM8[0000893d].bit1 is set or
the selected C<=16384. When bit1 is set, the code reads neither control
candidate nor the bit4 scalar.

```
trim = max(0,S+L+E-51200) if include_L else max(0,S+E-25600)
P = uint32(I*trim)
v = A+floor(P/65536)
corrected = floor(uint32(256*v+O-32768)/256) if I!=0 else v
output = min(65535,corrected)
```

I=0 bypasses the O read and the complete offset calculation. MUL.L
supplies the low32 product; logical shifts and the unsigned cap retain
the stated machine domain. Full-word inputs admit product overflow and
unsigned offset underflow. They can produce decreasing output when S,
L, E, I or A increases, including with factory flag bytes 51/01. The six
complete-domain views in closed_loop_fuel steps 16..19 and fuel_pulse
steps 17/19 therefore use sign=none. Their other fields and all other
39 notes remain intact. These are views of one output publication.

The fixture checks both legal banks, upper R4 bits, incoming T0/1,
all flag-byte values, trim and cap equality neighbors, zero-I bypass,
word boundaries, product overflow and offset wrap. Stock calibration
contexts and artificial contexts retain separate classifications.
Expectations are independent integer literals, including all fifteen
exit GPRs and final cap T. Original GNU nonT status bits are retained;
STC records the actual full SR after bank-preserving LDC. Exit full SR
equals (sr_before&~1)|expected_T. Arbitrary nonT-bit variation and
full incoming SR=0/1 are not claimed.

Every case checks the selected two output bytes and every other byte of
the 64 KiB aliased RAM, all 26 bound pool/calibration bytes, natural
PR/SP/GBR/MACH/MACL and the independent C caller ABI. The complete
80-byte frame spans SP-48..SP+31, with saved GBR at SP-8 and MACL
at SP-4; all other observed bytes retain their seeded values. Exit capture
starts at SP+32 and is disjoint from that frame.

`tools/kb/tests/test_bank_base_pulse_chain.py` owns the native view through
`test_bank_base_pulse_chain_owner_contract` and the registered executable
identity through `test_bank_base_pulse_registered_stock_contract`. The
gate binds every stock byte, scalar shape, typed bank and input conditions,
literal matrix, publication counts and preserved ledger selectors.

This bounded CPU result does not establish upstream producer states,
physical units, live bank mapping, caller dispatch, scheduling, injector
waveforms or engine reachability. Independent physical and hardware
evidence retains its existing scope.

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
with `Q = A + B` and `N` twice the RPM/12.5 coordinate `0xFFFF11F4` at a
median ratio of 0.98 to 0.99 (p5 0.87 to 0.94, p95 1.01 to 1.04). The J1979
Calculated Load byte matches its formula from the prior record exactly in 77
to 80 percent of records and within one count in 95 to 97 percent.

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

The three functions that pass `0xFFFF224E` to `FUN_0002C13C` (`FUN_00028EA2`,
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
if mask & (uint8[0xFFFF22E0] | uint8[0xFFFF1935]):
    d = uint16[0xFFFF23AA]; set every bit of mask in uint8[0xFFFF1935]
if bit i of DSTR is already set:
    d = max(0, d - uint16[0xFFFF23AA])
c = sat_u16((800 * d) >> 8)
if 0xFFFF4251.bit0: c = 1000
DCNT8x += c with interrupts masked; set bit i of DSTR
```

The selection predicate uses the entire incoming mask for every selected
channel. When any bit of that mask intersects inhibition or history, all
selected channels receive the opening word. The raw counter addition wraps
modulo65536. Substituting the same opening word and subtracting it from an
already started channel requires a common raw representation; physical
opening, pulse delivery and peripheral timing retain independent evidence.

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
are all set. Engine-event driver `FUN_00028EA2` sets bit 6 after the first
grouped pulse, whose masks come from `ROM8[0x226A2 + n]` (`00 18 30 21 03 06
0C`), and bit 5 once start-event count `0xFFFF2298` reaches 4. While P0335
fallback snapshot `0xFFFF24C9.bit5` is set and `0xFFFF8513.bit4` is clear, the
sequencer sets bits 7..4 itself and seeds `0xFFFF221E` with the slot before
the current one and `0xFFFF221D` with the lead. Every fired mask is ORed into `0xFFFF20B5`,
`0xFFFF157E`, and `0xFFFF16FE`, removed from DFCO fallback history
`0xFFFF1935`, and, with stock `ROM8[0x8D92]` bit 3 set, ORed into `0xFFFF14C3`
and `0xFFFF14C2`.

`FUN_0002B64A` sets pending flag `0xFFFF84EC.bit7` and uses the unsigned
low byte of its argument. The normal path splits that byte by ten through
`FUN_00028E7C`, moves one ten-count group into the remainder when nonzero,
and executes `FUN_00028DC8` to normalize tooth count `0xFFFF13B8` and
remainder byte `0xFFFF193B`. For the zero-count offset path,
`M = uint16(0xFFFF22BC) * uint8(0xFFFF193B)` and
`Q = floor(uint32(6554*M)/65536)`. It stores Q at `0xFFFF16C2` and
`uint8(M-10*Q)` at `0xFFFF166C`. The following compare programmer uses
`GR1A = 0xFFFF158A + Q`, or `TCNT1A + 2` when that instant has passed.
The bounded software proof of argument splitting, normalization and
offset arithmetic is in [JK08A.injection.md](JK08A.injection.md). `0xFFFF22BC` is the time of one 10-degree crank tooth in
`3.2 us` channel-1 counts and `0xFFFF158A` is the crank reference capture of
the current event. It then clears `TSR1A` bit 0 and sets `TIER1A` bit 0. In
P0335 fallback (`0xFFFF24C9.bit6`) an angle of 120 or more becomes count 1
with remainder `angle - 120`. Handler `FUN_0002BE40` clears the pending flag
and fires mask `0xFFFF2228` on the compare match.

### Reference tooth and cylinder order

The reference engine event is tooth 7 of the crank signal plate. The plate
carries ten teeth at 10-degree pitch per 120 crank degrees with two missing
teeth between tooth 7 and tooth 8. The ICI0A input-capture handler (vector 84,
entry `FUN_00028EA2`) runs on every tooth:

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
the tooth-9 path of `FUN_00028EA2` programs the delayed start with angle
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

## Bounded LTFT publication

The complete natural liberal-dormouse/fn at 7mfk:00057b26 and its real
diagnostic_record_byte1_bit7_predicate/fn have an independently
reconstructed original GNU SH-2E contract of 108 instructions,
268 bound bytes and 12028 literal cases. The instruction spans are
57B26..57B7A, 57BD4..57C34 and 25E20..25E44: 216 instruction bytes
and 52 bound data bytes. Exactly eight high-RAM longword pools are
simulator aliases. Three word operands, both ROM pointers and the real
predicate pointer retain their stock bytes. Natural RTS 57C30 executes
the R13-restoring delay slot at 57C32; the real predicate also returns
naturally, without a stack store or replacement stub.

Full incoming R4 is an independent context. Its low byte b=uint8(R4) is
admitted only in 0..1, and its upper 24 bits vary independently. The
bounded numerical inputs are unsigned words L at ffff2306+2*b and A at
ffff5648+2*b. U at ffff15fc is zero-extended; V at ffff15fe is sign-extended.
The complete byte mask M at ffff230e tests b+1, which is 1 or 2 for
these legal banks. Bounds lo=ROM8[00008e5b]*256 and hi=ROM8[00008e5a]*256
have stock operands 90 and 110. Every value 0..255 and reversed bound
pairs also have explicit artificial contexts.

    raw = uint32(L+A-25600)
    active = ((M&(b+1))==0) and (U>V)
    limited = min(hi,max(lo,raw)) if active else raw
    neutral = diagnostic_byte1.bit7 or F.bit0
              or (G.bit0 and H.bit1) or (K.bit6 and H.bit0)
    output = 25600 if neutral else uint16(limited)

F, G, H and K are the independent bytes at ffff41b5, ffff41fa,
ffff248b and ffff249c. Each genuine short-circuit neutral condition is
separate from the numerical limit gate. Diagnostic id 0129 addresses
byte1 at ffff5718+3*0129+1=ffff5a94. Record production and physical
diagnostic causes are outside this CPU result. The fixed caller cannot
take the predicate sentinel branch at 25E26 to 25E3E. That branch and
MOV #0,R2 at 25E3E are identity-only; direct sentinel, negative-id and
independent helper upper-word semantics are not claimed.

Equality U=V skips limiting. Negative mathematical sums wrap to uint32
before the genuine unsigned comparisons. With active factory bounds,
raw=-1 therefore selects 28160; raw=0 selects 23040. A limit bypass
publishes the low word, including overflow transitions. Reversed bounds
still implement lower-then-upper min(hi,max(lo,raw)). Full-domain output
can decrease when either input increases, so the two complete publication
views use sign=none. They describe one write, not sequential updates.
Their other fields and the other 17 closed_loop_fuel step records are
preserved, together with every held relation note/property/evidence and
ledger selector at both claiming ends.

Each legal bank has 6014 cases. Each incoming T value has 6014 cases.
There are 8564 factory-bound and 3464 artificial-bound contexts. Independent
integer expectations cover all 12028 output/T and fifteen-GPR vectors,
full R4 upper patterns, every mask/diagnostic/control/bound byte value,
all neutral combinations, all three numerical gate outcomes, unsigned
underflow, low-word wrap, signed comparison boundaries and bound equality.
Neither a stock instruction interpreter nor runtime output supplies
expected values.

Every literal checks full 64 KiB RAM except the selected output word,
both allowed output bytes, every bound data byte, all fifteen GPRs,
MACH/MACL/GBR, natural PR/SP, immutable context and an independent C ABI.
The actual current SR nonT bits are retained while requested T=0/1 is
injected. STC records prepared full SR, and exit SR equals
(preparedSR&~1)|expectedT. Arbitrary nonT variation or incoming full
SR=0/1 is not claimed. The 80-byte observer covers SP-48..SP+31 with
saved R13/R14/PR at SP-4/-8/-12. Those slots have literal expectations;
all other observed bytes, including a separate continuation at SP+24,
are preserved. Exit capture starts at SP+32. Snapshots are per literal.

The mandatory contracts test_ltft_publication_chain_owner_contract and
test_ltft_publication_registered_stock_contract in
tools/kb/tests/test_ltft_publication_chain.py bind every stock byte,
the independent literal output/T/GPR vectors, exact typed conditions,
scoped owner widths and the registered Region/header-array/C-loop counts.
Missing required owners, registration, header or publication sections
fail the contract. The shared predicate retains its separate bounded
knock-reference proof, both ledger claiming ends and existing evidence.
The fixed-id LTFT fixture adds no general-id helper case counts.

Upstream learned-grid selection/learning, adjustment production, bank
dispatch, percentages, physical fuel quantities, timing, live operating
reachability, full coordinator behavior and hardware validation retain
separate evidence boundaries. Existing units, scales, producer signedness,
other layouts and the shared predicate owner remain intact.

## Bounded channel pulse calculation and word snapshot

The mandatory `jk08a-channel-pulse` Region reconstructs 184 instructions,
423 bound bytes and 14132 literal cases with `EARLY_ONLY=0`. The complete
natural builder enters at 0004eba2, executes its second span at 0004ec24,
calls the real arithmetic-shift path 000224f8 and affine helper 0005b7ec,
and returns through its own RTS and delay slot at 0004eca8. The admitted
argument is uint8(R4)=i in 0..5; independent higher argument bits are retained.

A set aggregate inhibit bit i selects the unsigned opening word ffff2436
for both channel vectors and bypasses both helpers. Otherwise parity selects
ffff191c or ffff191e, adds signed16 ffff1396+2*i and conditionally subtracts
signed16 ffff1466+2*i under ROM8[8d92].bit3. A positive intermediate multiplies
unsigned ROM8[129c0+i] and shifts seven bits; nonpositive values become zero.
The compensated result is capped at 65535 and stored at ffff23c8+2*i.
The affine result at ffff23d4+2*i is the maximum of that input and two
independently saturated branches, each floor(uint32(a*x+100*b)/16384).
The four unsigned coefficients a,c,b,d occupy 91da,91dc,91de,91e0; exact
stock words are 3558,4000,109a,0000. All six exact stock multipliers are 0x80.
The second stock branch equals the input; artificial unsigned calibration
contexts execute separate branch saturation and low32 sum-wrap outcomes.
The generalized transformed relation uses `sign = "none"` because a wrap
does not establish global monotonicity.

The existing mandatory `jk08a-injection-snapshot` caller at 00021314 copies
the unsigned words ffff23d4+2*i to ffff2348+2*i through the real 140-byte
helper 00022558. Both vectors start at byte offset 24 of source ffff23bc and
destination ffff2330. Explicit R11=00022558 and R12=140 entry contexts and
the complete per-byte RAM checks bind this word relation. The copy does
not establish full scheduler execution, live cadence or hardware atomicity.
The formulas occupy fuel_pulse steps 20, 21, 22 and 23; all other fuel and
injection steps retain their independent contracts.

The numeric harness checks all fifteen GPRs, actual complete SR, natural
PR/SP, restored MACH/MACL/GBR, the immutable 76-byte entry context, 96 frame bytes,
the independent C caller ABI, 64k RAM and all 55 bound pool/calibration bytes.
The aggregate bypass and both real calls include exact saved and local words.
Only the selected compensated and transformed word writes may change RAM.
The simulator relocates exactly the three declared long RAM pools to matching
low16 offsets in 0x01000000 RAM; all instruction bytes remain original.
The original GNU image, assembler, compiler, simulator and 120-second stock
timeouts execute the contract. The physical decomposition of the corrections,
producer acquisition, operating cadence, actuation and hardware validation
remain separate from this bounded numeric publication.

## Connected injection calculation and raw scheduling

Ten mandatory Regions bind 3021 instructions, 7319 bound bytes
and 194860 literal cases with EARLY_ONLY=0. Each function or bounded view
has independently reconstructed instruction bytes. The registered contracts
execute the complete opening-word publisher, pulse selector, delayed-start
programmer, one-shot, end-angle publisher, injector-event ISR and dispatcher.
Three RPM views cover word scaling, capped byte scaling and the real copy;
they do not establish whole RPM-producer execution or sample simultaneity.

The opening word uses unsigned battery B and ROM bytes Q/A:
min(65535,max(0,floor((175-B)*Q/128)+A)). The real seven-SHAR helper floors
negative products. The full byte domains have a maximum of 603, making the
upper clamp unreachable. Raw duration and voltage units remain unverified.

The selector distinguishes override, stopped, start modes 1/2/4 and running.
Start modes compare the threshold with capped opening plus ROM margin,
conditionally subtract the stopped word, then apply the selected floor.
Running takes the maximum of each snapshot word and the running floor.
Its real secondary tail clears pending corrections and scales or copies
secondary words under the independent aggregate mask and ROM control bit.

The one-shot requires explicit invocation and an enabled output byte. Any
intersection of the whole mask with inhibition or history selects opening
for every selected channel. A set start bit subtracts opening with floor0.
The capped increment is floor(800*d/256), or 1000 in diagnostic mode; addition
to the raw counter wraps modulo65536. Its chain sign is none. DSTR ORs only
bits0..5 under I15 and restores the incoming interrupt mask. Synthetic raw
register storage does not verify peripheral timing or physical actuation.

Normal end-angle equations read the state after the prefix, latch, countdown
and bias updates. They select the conditional curve, fixed override, or base
curve plus bias, then cap at209 and double. The unsigned eight-cell implicit
lookup uses step32 and last-cell clamp224. It adds or subtracts the floor of
the positive interpolation distance. Alternate and inhibited entries retain
separately executed outcomes. Synthetic curves and scalars expose branches
that stock calibration suppresses; their physical reachability is unverified.

The base path of publisher 00056bd0 executes wrapper 00026370 and linear
finisher 00026740, adds the updated unsigned byte ffff340c to the base curve
result, applies the 209-count cap, and stores the doubled word at ffff192e.

Pending-mask equations read staged state after optional trigger setup and
before lead/cursor updates. Equal lead accepts only a matching next cursor,
negative lead clears pending, and positive lead executes the actual catch-up
loop and both consumers before publishing the final slot mask. The programmer
receives 4*unsigned8[ffff2333] or52 and wraps it to uint8. Nonzero normalized
count retains offset. Zero count uses the exact wrapped remainder and the
low32 reciprocal product. Compare selection uses delta+2>q, including timer
wrap; raw status/control updates have independently checked word boundaries.
The ISR equations require an explicit invocation; hardware compare delivery
is not inferred from separate compare and raw-publication observations.

Every admitted path observes all15 GPRs, complete SR/PR/SP/MACH/MACL/GBR,
the immutable76-byte input, the C caller ABI, declared saved/local bytes,
64k RAM, all bound ROM inputs and declared alias neighbors. The combined
dispatcher and ISR compare all192 frame bytes. The pinned GNU simulator's TRAPA/RTE uses SPC/SSR
and leaves SP unchanged. It does not establish the SH-2E exception stack;
equivalent exception-stack coverage is required before hardware eligibility.
Only declared RAM and register pointer pools are relocated. Exact instruction
bytes, the original GNU image and standard timeouts remain under the gate.

The arithmetic covers fuel_pulse18/24/25/26 and
injection_phase1..8/17/18/20..22. Indexed one-shot context x[0] is the incoming
aggregate mask and x[1] is channel0..5. The raw counter's previous value is
prev. This specification fixes the meaning of lookup and staged-state
boundaries; physical units, acquisition cadence and hardware validation
require their separate evidence.

## Upstream fuel pulse calculations

Eleven mandatory Regions bind 2726 instructions, 6494 bound bytes
and 696084 literal cases through the primary stock verifier. The sixteen
formula-bearing fuel_pulse steps1..16 use raw operand widths and exact
rounding, wrapping, latch and call boundaries.

| Calculation | Region | Literal cases |
|---|---|---|
| base-accumulator | `jk08a-base-accumulator` | 132684 |
| transient-coefficient | `jk08a-transient-coefficient` | 7440 |
| transient-additive | `jk08a-transient-additive` | 87052 |
| coolant-conditional | `jk08a-coolant-conditional` | 14261 |
| transient-pair-1 | `jk08a-transient-pair-1` | 44640 |
| transient-pair-2 | `jk08a-transient-pair-2` | 44640 |
| fuel-multiplier | `jk08a-fuel-multiplier` | 77328 |
| pulse-precursor | `jk08a-pulse-precursor` | 78272 |
| common-gain | `jk08a-common-gain` | 68855 |
| enrichment-prefix | `jk08a-enrichment-prefix` | 70800 |
| enrichment-terminal | `jk08a-enrichment-terminal` | 70112 |

Natural function 000554ae performs modulo-2^32 addition of RAM32[ffff15f8], 16384, unsigned RAM16[ffff230c] and unsigned RAM16[ffff15da], interprets the low32 result as signed, then clamps it to0..65535 atffff231a. The signed wrap seam prevents a universal positive input sign. Producer domains and physical units require independent evidence.

Natural function000528be reads doubled normalized load, capped255, through the actual eight-cell lookup00026370 atROM00012176. It publishes half the cell atffff150a while signed RAM16[ffff1a66]<0, otherwise64. Its natural RTS at000528f2 returns without calling00052902 or writingffff2300.

Natural function00052902 publishes signed16 atffff2300: trunc0(uint8(ffff150a)*int16(ffff1a66)/256), or0 whenffff245d.bit5 andROM8[00008b40].bit2 are both set. The admitted product bounds-32640..32639 make the explicit signed saturation unreachable. No physical transient qualifier or cadence is inferred.

The two bounded caller windows0005243c..00052444 and0005249e..000524a6 in000522c4 execute their original BSR pairs to000528be and00052902 with both delay slots and natural returns. Each caller observes current coefficient then signed additive publication. The surrounding dispatcher is outside these bounded windows.

Natural function0005525a updates threshold/hysteresis bits inffff2492/ffff2493, admits the actual gate, and uses uint8(4*max(0,uint8(ffff106f)+int16(ROM16[0005533c]))) for eight-cell curve00012422. It publishes lookup byteffff15dd and selected coefficient byteffff15dc fromROM0000990a, with load/RPM bins at00011b1b/00011b17. Optional signed difference rate limiting against oldffff15da precedes cap max(0,ROM16[0000929a]-RAM16[ffff22e8]+16384); disabled entries publish0 and retain lookup/coefficient bytes. Wrapped coordinates have sign none.

Natural function000556ec scales min(65535,RAM16[ffff231a]+RAM16[ffff240a]) by unsigned mixtureffff22e8 over16384. It executes special multiplier0000838e, floorffff15cc, cap byte00008b9d, eligibility gates, floor/phase latches and normal/transition rates000084e6/0000840d. Transition progress usesffff84c3.bit7. It writes workingffff18e4 and publishesffff22e6 as0 only when aggregateffff22e0 equals0x3f. Full admitted contexts contain downward discontinuities, so both input views have sign none.

Natural function0004e974 selects unsigned BFSffff1024 orffff123e; optionalRPM cap uses max(ffff34f6,ROM32[000096e0]/RPMwordffff11bc), with all-ones quotient at zeroRPM. It publishes selected BFS atffff196a. H=floor(B*RAM16[ffff22e6]/131072). For bank0/1 it adds signedffff2300 to floor(H*RAM16[ffff40b6+2*b]/25600), then executes actual signed Q14 multiplication by unsigned gainffff165e, signed truncation toward zero, clamp0..65535 and floorROM16[000094e8]. Commonffff1876 uses H directly and updatesffff24a1.bit0 on its pre-floor clamp. Bank outputs areffff18c0/ffff18c2.

Natural function00053698 alternatesffff2485.bit3: inactive entries set the bit and retain all gain intermediates; active entries clear it. Diagnostic argument-1 has a fixed false predicate. Raw P=floor(RAM16[ffff4524]*ROM8[000089fe]/128)+ROM16[000093c6] is retained for arithmetic after min(65535,P) publication atffff517c. Selected correction, ordered low/high clamps, BFS scaling and two16-cell curves000129e2/000129f2 precede saturated sum, complement load, ratio and floor((ratio*5259+1213696)/10000). Final gainffff165e=floor(byteffff160d*ROM16[00009332]/256). No temperature, pressure scale or acquisition cadence follows from these consumer contexts.

Bounded original prefix0005594a..00055a52 executes wide-open hysteresis onffff3528 and16-cell curve0001214e, explicitRPM/load axis search00011cc0/00011ac7, and8x8 surface0000a9aa with horizontal then vertical positive-distance-floor interpolation. Optional00012552 correction uses true signed seven-SHAR flooring of the deviation from128. The rich latch uses unsigned32 hysteresis arithmetic with bytes00008b9b/00008b9f and publishes surface value or128 atffff15eb. Synthetic calibrations expose direction reversals and unsigned wrap; surface sign is none. The boundary preserves the live outer frame and does not execute the subsequent state machine.

Bounded entry000562e2 resumes after the upstream state machine with an independently staged word atSP+12. Exact mode/phase/enable/tick branches update primaryffff123a, clamp it to mixture*128 and updateffff2485.bit5. The real0005651c auxiliary call updates curve/latches/countdown andffff123c. The terminal max(primary,auxiliary) is forced to16384 below rawRPM32 or duringffff2531 delay, then capped byROM16[000094ec] underffff4252.bit1 beforeffff22e8 publication. Untouched state-machine domains, physical mixture interpretation and tick cadence retain separate evidence.


The transient coefficient function returns naturally without invoking the
additive function. The bounded two-call windows of the real parent establish
their composition. The enrichment prefix stops before the upstream state
machine. The terminal resumes with a staged candidate at SP+12; it executes
the actual auxiliary function and terminal publication without inferring
the omitted state machine. These boundaries retain their original stock
instruction bytes and expose the complete live frame state.

All contexts compare complete GPRs, SR including M/Q/T and interrupt mask,
PR/SP/GBR/MACH/MACL, immutable input records, 192 frame bytes and the complete
64k RAM window. Natural calls and returns, original branch delay slots,
declared lookup pools and the shared 16-bit RAM pointer's neighboring bytes
are checked. Relocations affect declared data pointers only. The boundary
observer restores the admitted outer stack through an explicit scratch
register; it does not replace arithmetic under test.

Before simulator entry, the linked big-endian ELF32 SH image is checked for
every allocated section and every LOAD segment's virtual and physical memory
extent, including uninitialized BSS. Storage that intersects the declared
RAM window is rejected. Exact adjacency is admitted. Truncated, wrapping or
missing storage declarations are rejected. Literal context compaction retains
full register observations while placing executable fixture data outside RAM.

The numerical contracts permit synthetic calibration contexts to expose
otherwise inactive branches. They establish neither physical units nor
acquisition cadence or live producer reachability. Hardware eligibility
requires the corresponding bench and engine evidence; the existing GNU
SPC/SSR exception contract does not establish the SH-2E exception stack.

The named specification covers these exact chain members:

`0000a9aa`, `00012176`, `00012422`, `000129e2`, `000129f2`, `0004e974`, `000528be`, `00052902`, `00053698`, `0005525a`, `000554ae`, `000556ec`, `0005594a`, `ffff1024`, `ffff102c`, `ffff106f`, `ffff11bc`, `ffff15da`, `ffff15eb`, `ffff165e`, `ffff18c0`, `ffff22e6`, `ffff22e8`, `ffff2300`, `ffff231a`.
