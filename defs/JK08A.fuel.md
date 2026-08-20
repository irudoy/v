# JK08A Main Fuel Calculation

## Status and scope

This document records the static code model of the main fuel calculation in the
exact JK08A/JK03A executable. The established path covers dual-bank MAF input,
Base Fuel Schedule (BFS), Fuel Compensation Main, the periodic fuel multiplier,
bank-specific base terms, closed-loop trims, six per-channel compensated pulse
words, and the shared fuel-output inhibit mask. The complete source and
precedence model for that mask is maintained in
[`JK08A.fuel-inhibit.md`](JK08A.fuel-inhibit.md).

No road log or bench observation is used here. Arithmetic, RAM data flow,
scheduler ordering, diagnostic bindings, and ATU-II register use are
code-proven. Engineering conversions derived from homologous definitions and
the physical connection between calculated pulse arrays and injector terminals
remain hardware-validation items.

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
| 83 | `FUN_000C21E6` | fuel-target calculation through `0xB33A` |

The ordering proves current-pass dependencies from the inhibit mask and fuel
multiplier through the transient term and pulse calculation. It does not imply
that the later fuel-target result at index 83 controls the pulse already
calculated at index 60 in the same pass.

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
homologous structured-profile conversion `raw/2048 ms`, the `ms/kg` K-Value
unit, and the `kg/hr` MAF Factor unit are dimensionally consistent with the
code, but remain candidate engineering scales until hardware validation.

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
as actual compensated injection pulse width for bank 1. The homologous
`raw/100 ms` conversion remains candidate for JK08A.

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

The transformed six-word array begins at `0xFFFF23D4`. Its exact numeric
contract is established, but its physical purpose remains unresolved.
`FUN_000521A8` takes the maximum of all six transformed words and
`0xFFFF241C`, then derives scalar bytes `0xFFFF23BF` and `0xFFFF23F0`.

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

## Hardware-output boundary

The aggregate mask has a separate code-proven path to the six ATU-II one-shot
outputs:

```text
0xFFFF22E0
  -> per-channel eligibility and fallback selection
  -> FUN_0002C13C
  -> ATU-II DCNT8A..DCNT8F and DSTR
```

`FUN_0002C13C` substitutes fallback word `0xFFFF23AA` for a masked channel or a
channel retained in rotating history `0xFFFF1935`, scales its selected duration
by `800/256`, adds it to the corresponding channel-8 down-counter, and starts
the selected one-shot output.

A complete application-code p-code census found no software consumer that
connects raw pulse array `0xFFFF23C8..0xFFFF23D3` to this ATU-II source path.
The only resolved read of `0xFFFF23C8` outside its producer is the diagnostic
response path. The only runtime consumer of transformed array
`0xFFFF23D4..0xFFFF23DF` is the maximum/scalar calculation in
`FUN_000521A8`. Fixed event words used by the ATU-II path also have no resolved
application-code writer beyond startup-range handling.

The following claims are therefore distinct:

- Code proves the complete main fuel arithmetic through six raw and six
  transformed pulse words.
- Code proves a shared inhibit/fallback path from `0xFFFF22E0` to six ATU-II
  one-shot outputs.
- Static analysis does not yet prove that either pulse array is the duration
  source consumed by `FUN_0002C13C`.
- Physical injector closure, pulse-width units, terminal ordering, and any
  hidden peripheral or transfer mechanism require bench or engine validation.

## Hardware validation priorities

The minimum controlled validation set is:

1. Record exact DID `0x1208` BFS, DID `0x1206` compensated injection pulse,
   STFT/LTFT, RPM, MAF, lambda, and the six output waveforms on a bench or engine.
2. Apply a bounded single-region change to Fuel Compensation Main `0xA29A` and
   verify the expected multiplicative movement in BFS and pulse duration.
3. Trigger DFCO and RPM cut conditions separately and compare
   `0xFFFF22E0`-equivalent behavior with all six electrical outputs.
4. Determine whether the ATU-II duration source is populated by an unresolved
   interrupt, transfer engine, peripheral side effect, or code outside the
   recovered application data flow.
5. Retain Map 1 storage for the DFCO held-request and intermediate-restore
   thresholds until FAIL-BOOT is fixed and base map switching is confirmed on
   hardware; only then add Map 1-5 Hold and Intermediate support.
