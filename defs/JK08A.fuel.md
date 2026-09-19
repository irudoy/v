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
words to the ATU-II one-shot outputs fixes their millisecond scale. Road-log
statistics appear only where they bound a scale that code leaves open. The
physical connection between the scheduled durations and the injector terminals
remains a hardware-validation item.

## Periodic ordering

`FUN_00020DFE` dispatches the 124-entry table at `0x21970`. Relevant entries are
ordered as follows:

| Index | Function | Established role |
|---:|---|---|
| 11 | `FUN_000769C0` | request-limit source coordinator, including the `0x0942C` branch |
| 18 | `FUN_00071508` | signed-minimum request-limit arbiter |
| 20 | `FUN_000702A0` | ordered request-controller stages and final selector |
| 21 | `FUN_00079DD8` | signed request-boundary dispatch |
| 22 | `FUN_000730FC` | downstream inverse-coordinate and limit calculations |
| 27 | `FUN_0004ED88` | final six-channel inhibit/override mask `0xFFFF22E0` |
| 35 | `FUN_00057608` | fuel-multiplier calculation coordinator |
| 38 | `FUN_00056FC0` | common additive and masked-channel override word `0xFFFF2436` |
| 39 | `FUN_00053698` | common Q14 gain `0xFFFF165E` |
| 41 | `FUN_000522C4` | transient and per-channel preparation, including `0xFFFF2300` |
| 42 | `FUN_0004E974` | common and two-bank injection precursors |
| 54 | `FUN_0005C910` | runtime STFT publication |
| 60 | `FUN_0004ECAC` | two parity bases and six-channel compensated pulse calculation |
| 80 | `FUN_00057020` | downstream mode-dependent fuel calculation |

The ordering proves current-pass dependencies from the inhibit mask and fuel
multiplier through the transient term and pulse calculation. Scheduler index 83
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

Exact DID `0x1208` identifies `0xFFFF1026` as Base Fuel Schedule. The
homologous structured-profile conversion `raw/2048 ms` and the `ms/kg` K-Value
unit are dimensionally consistent with the code, but remain candidate
engineering scales until hardware validation. The airflow entering the
producer is declared by the ECU itself: J1979 Mode 01 PID `0x10` publishes
`105 * 0xFFFF105C / 256` as g/s*100, so one count of the total is
`105 / 25600` g/s. The `kg/hr` MAF Factor unit with scale `x * 0.0001` gives
0.0109 kg/hr per count against 0.01477 kg/hr from that declaration; the
discrepancy is recorded at the finding.

## Fuel Compensation Main to BFS

`FUN_0003BE3C` contains the live accessor for Fuel Compensation Main `0xA29A`.
At `0x3C284..0x3C29C`, the active lookup path uses wrapper `0x261F0`, axes
`0x11CF0` and `0x11D4C`, RPM-related coordinate `0xFFFF11F4`, and byte
coordinate `0xFFFF1170`, then writes the uint8 result to `0xFFFF1160`. Runtime
gates can select a bounded bypass value instead of the map result; the common
destination is unchanged.

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
wot   = 0xFFFF2468.bit3            # 0xFFFF3528 >= 200 (+8 hysteresis), ~70 deg TVO
load  = wot ? 0xFF : uint8[0xFFFF102C]
m     = map8x8(0xA9AA; rpm axis 0x11CC0 vs uint16[0xFFFF11BC], load axis 0x11AC7)
if 0xFFFF2466.bit6:                # high-detonation surface selected
    t = map1D(0x12552 on uint8[0xFFFF11AE], axis 0x11CD8)
    m = sat_u8(128 + ((m - 128) * t >> 7))
rich  = 0xFFFF24A2.bit7            # m + (rich ? 1 : 0) >= ROM8[0x8B9B] = 130
0xFFFF15EB = rich ? m : 128
```

`0xFFFF3528` is `min(255, uint16[0xFFFF40C6] * 0x505B >> 16)` from
`FUN_00054EB8`, the first stage of the coordinator. The 70-degree figure
inherits the candidate `0.0275` degree scale of axis `0x155A0`.

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

`FUN_00053698`, table index 39, recalculates on alternating invocations. It
uses current BFS and maps `0x129E2` and `0x129F2`, saturates their byte sum at
255, and applies complement multiplier `256 - sum`. Its terminal calculation
writes:

```text
0xFFFF165E = floor(uint8[0xFFFF160D] *
                   ROM16[0x9332] / 256)
ROM16[0x9332] = 13972
```

`0xFFFF165E` is the common Q14 gain consumed by the next current-pass pulse
stage. Its physical compensation identity remains unresolved.

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
The code establishes two bank-indexed precursors but does not establish the
physical cylinder ordering of the later parity channels.

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
`uint16[0xFFFF15FC] <= uint16[0xFFFF15FE]`. Otherwise the word is clamped
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
uint8[0xFFFF41FA].bit0 clear and uint8[0xFFFF248B].bit1 set
uint8[0xFFFF249C].bit6 set and uint8[0xFFFF248B].bit0 set
```

The published word is therefore either a clamped learned value inside
`90..110` percent or exactly `100.000` percent. A capture that reads exactly
`0x6400` does not by itself distinguish a neutralized publication from a
learned grid that still holds its initialization value; `0xFFFF2306` and
`0xFFFF5648` separate the two cases.

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
within one count in 95 to 97 percent. Each closed-loop pulse word is linear
in `BFS * STFT / 0x6400 / 20.48` with slope 0.87 to 0.89 and an additive 42 to
53 raw at correlation 0.99 on both banks; the slope below unity and the
additive term are the `0xFFFF165E` gain and the battery-dependent
`0xFFFF2436` base, which the profile does not stream. The factor 20.48 is the
ratio of the candidate `raw/2048 ms` BFS scale to the established
`raw/100 ms` pulse scale, so the measured slope is the chain gain between the
schedule and the injector command in physical units.

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

Base Fuel Schedule keeps its candidate `raw / 2048 ms` scale. No ROM constant
fixes a reference value for the product of the gains between the schedule and
the pulse words: common gain `0xFFFF165E` reaches at most
`floor(255 * 13972 / 256) = 13918` against the `16384` that would make its
stage unity, so code alone cannot close the schedule. The recorded relation
bounds it instead. With the pulse scale absolute, the measured chain gain is
`0.88` under `raw / 2048 ms`, `0.44` under `raw / 1024 ms`, and `1.76` under
`raw / 4096 ms`. Only the near-unity value matches a chain whose recovered
stages are unity-normalized.

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
   opening time `0xFFFF2436`, and record the terminal order of the six
   channel-8 outputs.
5. Retain Map 1 storage for the DFCO held-request and intermediate-restore
   thresholds until FAIL-BOOT is fixed and base map switching is confirmed on
   hardware; only then add Map 1-5 Hold and Intermediate support.
