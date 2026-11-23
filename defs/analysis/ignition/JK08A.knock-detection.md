# JK08A knock-threshold detection

## Scope and result

This specification separates the active per-channel knock-threshold table at
`0x1108E` from the structurally similar but unreferenced calibration bank at
`0x10F8E`. Exact JK08A code reads only `0x1108E`. The neighboring bank does not
participate in the unmodified firmware and is hidden from tuning definitions.

The active table has six rows of sixteen big-endian `uint16` thresholds. Code
proves a one-based evaluator channel taken from the engine-event index, one
evaluation of every channel per engine cycle in a fixed crank-angle window,
and engine-speed interpolation. It selects no knock sensor per channel and
does not prove the catalog-derived knock strength scale.

## Active lookup

Function `0x00049FFC` selects a one-based channel and interpolates one row:

```text
if ROM8[0x8B3D].bit3 == 0:
    channel = uint8[0xFFFF11DE]
else:
    channel = uint8[0xFFFF2143]

row = 0x1108E + 0x20 * (channel - 1)
threshold = interp_u16_1d(
    row,
    axis=0x15340,
    input=uint16[0xFFFF11F4]
)
uint16[0xFFFF2144 + 2 * (channel - 1)] = threshold
```

Stock `ROM8[0x8B3D]` is `0x82`, so bit 3 is clear and the exact image selects
`0xFFFF11DE`. A zero channel causes the evaluator to return before the lookup.
The speed input is the code-proven RPM/12.5 word. Static editor labels render
the sixteen positions as 400..6400 RPM, matching the exact axis contents.

Rows 3 and 5 contain only `0xFFFF`; rows 1, 2, 4, and 6 contain finite
thresholds after their first `0xFFFF` cell at 400 RPM. A `0xFFFF` threshold
admits an exceedance only for a metric above 65535 (see
[Evaluator outputs](#evaluator-outputs)), and
[Channel schedule](#channel-schedule) gives the crank-angle window that each
row serves.

## Executable lookup contract

The accessor contract requires `1 <= channel <= 6`; it contains no channel
guard. The zero-channel check belongs to the evaluator. Stock selector `0x82`
chooses the primary channel; the other selector-byte contexts test bit 3
without establishing their use in an unmodified ECU. The wrapper narrows the
coordinate to `uint16` and returns zero fraction below the first or at and
above the last axis point. It loads both cells even when the fraction is zero,
including the word at `0x1114E` following the last row.

For unsigned cells `a`, `b` and Q0.16 fraction `f`, the finisher returns
`a + floor(max(0, b-a)*f/65536) - floor(max(0, a-b)*f/65536)`.
Descending intervals truncate the positive decrement before subtraction.
The accessor stores the threshold and naturally returns `R0 = 2*channel`
with the threshold in `R2`.

This execution contract covers lookup and threshold publication from explicit
RAM contexts. Metric production, evaluator comparison and event-count updates,
reference learning, acquisition, scheduling, physical channel or sensor mapping
and the engineering threshold scale have separate evidence boundaries.

## Bounded comparison contract

The comparison entry
at `0x4A2EE` executes the natural threshold accessor and real interpolation
helpers, then reads the selected unsigned longword metric and threshold word.
The caller supplies legal channels `1..6`; the channel-zero guard is outside
this entry. Metric production is separate from the input contract.

For selected channel `c`, raw metric `m = RAM32[0xFFFF21D8 + 4*(c-1)]` and
threshold `t = RAM16[0xFFFF2144 + 2*(c-1)]`, exceedance is the strict unsigned
predicate `m > 0x80000000 + t`. Equality clears the condition. Status bit 6 at
`0xFFFF24C2` reflects exceedance while other bits are retained. The local byte
at `SP+12` holds `0x40` or zero. The selected bit `c-1` at `0xFFFF2150` is set
or cleared without changing sibling bits. Exceedance increments the unsigned
byte at `0xFFFF2142`, saturated at 255; the clear path preserves it.

The real left-shift helper executes every legal channel shift `0..5`. Isolated
contexts also cover `6..7`, negative counts and counts `>=32`. Negative counts
retain the input; counts `>=32` return zero. Positive counts `8..31` are outside
the bound execution envelope. Artificial selector-byte contexts establish the
raw bit-3 alternative without a stock mode-reachability claim.

Only eight declared RAM pool words are relocated after byte identity. Every
case checks all other aliased RAM, sibling thresholds and metrics, inputs,
calibration, preserved fragment registers and a separate C caller ABI. The
52-byte observed frame contains exact nested saved words, the wrapper/linear
tail slot, local neighbors and the continuation at `SP+16`. A descending tail
stores its unsigned left cell in the reused tail slot; other paths retain the
wrapper return. The boundary at `0x4A386` restores driver PR and R1 outside
tested instructions. It does not establish a stock function-return contract
or execute reference learning, full evaluator dispatch, acquisition, physical
timing or hardware behavior.

## Channel schedule

Crank tooth handler `FUN_00029588` opens one knock window per 120 crank
degrees on tooth 7 and closes it on tooth 0, 50 degrees later:

```text
tooth 7: call 0x0004A5AC at 0x000297B0               open the window
         if 0xFFFF8501.bit7:                         crank synchronized
             uint8[0xFFFF11DE] = uint8[0xFFFF13C8]   store at 0x000297DE
tooth 0: call 0x0004A8D4 at 0x0002A1DE               close the window
             call 0x0004A238 through literal 0x0004A9C0
```

The window start runs before tooth 7 copies identified cylinder `0xFFFF13C8`
into event index `0xFFFF11DE`, so the evaluator on tooth 0 selects the index
of the tooth-7 event that opened the window. `FUN_0004A8D4` calls the
evaluator on every tooth 0 while `ROM8[0x8B3D]` bit 7 enables the window, and
the evaluator returns early only for index 0. Under crank synchronization the
index, which is the cylinder number, advances 1-2-3-4-5-6 in firing order
([`JK08A.fuel.md`](../fuel/JK08A.fuel.md#reference-tooth-and-cylinder-order)), so
every channel is evaluated once per engine cycle. Channels 3 and 5 run the
same window, acquisition, metric, and comparison as the other channels; the
channels differ only in their threshold row, reference row, and result slots.

Tooth 7 is 110 degrees before compression TDC of its event cylinder in the
firmware coordinate of ignition command
`ROM8[0x83D5] - advance = 110 - advance`. The window of channel `c` therefore
spans 110..60 degrees before compression TDC of cylinder `c`, which is 10..60
degrees after compression TDC of cylinder `c - 1` (cylinder 6 for channel 1).
The windows of channels 3 and 5 span 10..60 degrees after compression TDC of
cylinders 2 and 4.

With stock `ROM8[0x8B3D] = 0x82`, the window start programs one acquisition
for every channel: DMAC channel 2 reads `ADDR24` (`SAR2 = 0xFFFFF840`), and
`ADCSR2 = 0x59` selects 4-channel scan mode over AN24 and AN25 with the A/D2
interrupt enabled. With bit 3 set, which the stock image does not select, the
window start stores the index before the tooth-7 copy, `c - 1`, as channel
`0xFFFF2143` and alternates the input by its parity: odd channels keep
`0xFFFFF840` and `0x59`, and even channels take `ADDR28` (`0xFFFFF848`) and
`ADCSR2 = 0x5D`, AN28 and AN29. On the stock path the channel number
therefore selects no A/D input. The code does not identify the sensors wired
to AN24, AN25, AN28, and AN29.

## Evaluator outputs

Function `0x0004A238` builds the metric of the selected channel `c`, calls
`0x00049FFC`, compares the metric with the threshold, and updates the
reference of the channel:

```text
c = uint8[0xFFFF11DE]                               return when c == 0
if uint8[0xFFFF2154] == 0:                          no DMAC block completed in the window
    v[i] = 0xFFFF                                   i = 0..7
else:
    v[i] = window value i through 0x00021CE0
d[i] = v[i] - reference[c][i]                       reference at 0xFFFF2178 + 16 * (c - 1)
s = sum of the ROM8[0x8870] = 3 largest d[i] outside mask ROM8[0x8618] = 0x00
metric = sign(s) * min(g * |s| >> 14, 0x7FFFFFFF)   g = ROM8[0x86AC] * ROM8[0x8694] * ROM8[0x86A7] >> 7
exceedance = metric > threshold                      threshold + 0x80000000 < metric + 0x80000000
reference[c][i] = (224 * v[i] + 31 * reference[c][i]) >> 8, plus 1 when below the old value
```

The stock bytes `ROM8[0x86AC] = ROM8[0x8694] = ROM8[0x86A7] = 0x80` give
`g = 16384`, a gain of exactly 1. The metric is therefore the sum of the three
largest rises of the window values over the reference of the channel and lies
in -196605..196605. The reference weight is `ROM8[0x884B] = 0xE0`. While
runtime diagnostic record `0x12D` or `0x13F` has byte-1 bit 7 set (predicate
`0x00025E20`), the update sets every reference to `ROM16[0x9282] = 0xFFFF`
instead. Threshold `0xFFFF` admits an exceedance only for a metric above
65535. A window without a completed DMAC block substitutes `0xFFFF` for every
value, and its metric is 196605 minus the sum of the three smallest references
of the channel.

The evaluator updates three outputs:

- `0xFFFF24C2.bit6` is the current selected-channel comparison result;
- bit `c - 1` of `0xFFFF2150` is the current comparison result of channel `c`;
- `0xFFFF2142` is the saturating interval event count consumed and cleared by
  knock timing-state coordinator `0x000493E8`.

An exceedance sets the selected bitmap bit and increments the event count up
to `0xFF`. A non-exceedance clears the selected bitmap bit. The coordinator
consumes the count, not the bitmap.

The event count influences the timing-state coordinator described in
`JK08A.ignition-state.md`. It is not itself a commanded retard value.

## Margin telemetry

The evaluator leaves both comparison operands in RAM: the offset-binary metric
of the evaluated channel at `int32[0xFFFF21D8 + 4 * (channel - 1)]` and its
threshold at `uint16[0xFFFF2144 + 2 * (channel - 1)]`. The stock comparison is
`threshold + 0x80000000 < metric` on unsigned 32-bit values. Every evaluation
overwrites the pair of its channel, so a pointer sampled at the snapshot rate
misses the evaluations between two snapshots.

The custom CAN telemetry wraps the evaluator behind its only reference, literal
`0x0004A9C0` in `FUN_0004A8D4`. The caller reads no register that the evaluator
leaves, so the wrapper calls the stock evaluator first and then repeats the
channel selection and the comparison on the stored operands. It keeps the
per-channel minimum of `threshold - metric` as a signed word at
`0xFFFF5E10 + 2 * (channel - 1)`. An exceedance yields a negative margin
limited at `-32768`. Context tag 4 of the `tuning` profile publishes the six
minimums and rearms them with `32767`, which stands for an interval without an
evaluation of the channel or a margin of 32767 or more. With one evaluation of
each channel per engine cycle, every 51.2 ms tag-4 interval holds an
evaluation of every channel from 2343.75 RPM, `0xFFFF11F4` 188, upward; below
that speed an interval can end without one. A row of `0xFFFF` thresholds
publishes a value below `32767` only for a metric above 32768, so on channels
3 and 5 the value `32767` does not distinguish an interval without an
evaluation from evaluated metrics of at most 32768. The profile carries no
evaluation count or metric per channel. `patches/can-telemetry.md` defines the
wire contract.

## Vehicle result of 2026-09-21

Registry entry `knock_margin.vehicle_2026_09_21` in
[`../../../patches/hardware-results.toml`](../../../patches/hardware-results.toml) holds
the knock margins of the eleven profile-5 captures of the 2026-09-21 road
session. The image carries the stock `0x1108E` rows and evaluator constants.
Channels 3 and 5 publish `32767` in all 18,893 tag-4 groups of the seven TRC
captures and carry no value in any of the 279,143 MLG records. Of those
groups, 1,158 have `0xFFFF11F4` 188 or more; there channels 1, 2, 4, and 6
carry an evaluated margin in every group and channels 3 and 5 in none. Every
evaluation of channels 3 and 5 in those intervals therefore has a metric of
at most 32768.

From `0xFFFF11F4` 64, the first axis point at which rows 1, 2, 4, and 6 hold
finite thresholds, one evaluation per engine cycle predicts 2,968 of 11,340
groups without an evaluation of a given channel; channels 1, 2, 4, and 6
publish `32767` in 2,936..2,944 of them. The idle values of the valued
channels follow the evaluation cadence.

| Channel | Idle TRC groups | Lowest margin | Largest metric |
| ---: | ---: | ---: | ---: |
| 1 | 8,731 | -1,957 | 15,190 |
| 2 | 8,739 | -1,680 | 14,240 |
| 3 | 18,893 | `32767` | at most 32768 |
| 4 | 8,730 | -3,018 | 20,627 |
| 5 | 18,893 | `32767` | at most 32768 |
| 6 | 8,732 | -3,939 | 13,226 |

The lowest margins cover all eleven captures, and none reaches `-32768`. The
metric of a group is the image threshold at the captured `0xFFFF11F4` minus the
published margin. From `0xFFFF11F4` 512 upward the threshold is the last row
cell, so the largest metrics, all at `0xFFFF11F4` 603..617 in the Map 3
full-pedal run of `6-map-1-3-4-limiter.mlg`, are exact. The largest, 20,627 on
channel 4 at 7537.5 RPM with margin -697 against threshold 19,930, falls
inside the main fuel-cut cycling of `main_fuel_cut.vehicle_2026_09_21`. The
latched bitmap is nonzero in 90 records, its union `0x2B` holds only the bits
of channels 1, 2, 4, and 6, and the latched count never exceeds 1.

The recordings bound the metric of channels 3 and 5 at 32768 without
observing it. The largest metric of the valued channels lies below that
bound, so evaluations with metrics like theirs publish `32767` on channels 3
and 5 as well.

## Unreferenced bank at 0x10F8E

`0x10F8E..0x1104D` is another 192-byte, 6x16 `uint16` array. It resembles the
active table and has the same all-`0xFFFF` rows 3 and 5, but resemblance is not
execution evidence.

The exact-image reference audit establishes all of the following:

- the Ghidra direct and literal-pool reference census has zero hits anywhere
  in `0x10F8E..0x1104D`;
- the complete ROM contains no exact 32-bit value `0x00010F8E`;
- the recovered interpolation inventory assigns zero accessors to `0x10F8E`;
- active base `0x0001108E` occurs exactly once, at literal `0x0004A204`;
- instruction `0x0004A014` loads that literal and `0x0004A02C` calls the
  interpolation wrapper with the derived row address.

The unreferenced bank therefore has catalog role `dead` for exact JK08A code.
Changing it cannot alter the active threshold calculation unless executable
code is also changed to reference it.

## Target-layout raw threshold role

The exact 1ND0A and 1ND3B accessors at `0006e854` load table `000122c8`;
the exact 1ME3B accessor at `0007275c` loads table `00011dfc`. Each selects a
channel row, interpolates an unsigned word coordinate and publishes a raw
threshold word. Their callers compare the selected uint32 metric with
`0x80000000 + uint16(threshold)` using strict CMP/HI. These operands and the
consumer establish raw threshold-role homology with JK08A table `0001108e`.

The target axes end at raw knots 464, 504 and 544; JK08A ends at 448, 480
and 512. The target calibration data agree across the three exact images.
1ME3B uses a fused FLOAT/FMUL/FDIV/FTRC leaf with a sign-extended
zero-fraction return; its accessor stores the low word. The integer wrapper
and the fused leaf require separate arithmetic and ABI proofs.

The sole interpolation call has ordinal 0 of 1 inside
each accessor. This static gate establishes neither target execution nor
full arithmetic/ABI equivalence, engineering scale or physical channel
identity.

## Calibration boundary

- Only `0x1108E` is an active threshold calibration in the exact image.
- Increasing an active raw threshold makes an exceedance less likely; lowering
  it makes an exceedance more likely.
- Rows 3 and 5 hold `0xFFFF` in stock and admit an exceedance only for a
  metric above 65535; the 2026-09-21 recordings bound their metric at 32768
  without observing it.
- The `x * 0.0015259` knock-strength conversion is catalog-derived and remains
  candidate evidence. Raw comparison behavior is code-proven.
- The combustion event that each channel window observes, the sensors behind
  AN24 and AN25, and the physical scale require controlled signal or vehicle
  validation before per-cylinder tuning decisions.

## Bounded knock reference learning

The complete RAM-only learner at `0004a118..0004a1fc` and its real
diagnostic predicate at `00025e20..00025e44` form the registered
`jk08a-knock-reference-learning` Region. The exact contract binds
132 instructions, 304 bound bytes and 7336 cases. The envelope contains
264 instruction bytes and 40 data bytes: 36 pool bytes and 4 calibration bytes. Both functions
return through their natural stock RTS/delay slots; no predicate stub or
boundary return replaces an instruction.

`ROM8[0x00008b3d].bit3` selects primary channel byte `ffff11de` when clear
and alternate byte `ffff2143` when set. Normal learning uses a declared
one-based channel `c` in 1..6, eight unsigned samples at
`ffff20c2+2*i`, and eight unsigned old words at
`ffff2178+16*(c-1)+2*i`, with `i` in 0..7. Both loaded words are
zero-extended before multiplication. With both queried diagnostic results
clear, byte weight `W = ROM8[0x0000884b]` supplies:

```text
q = floor((W*uint16(v)+(255-W)*uint16(old))/256)
new = min(65535,q+min(1,max(0,uint16(old)-q)))
```

The coefficients sum to 255. Stock `W=224` supplies coefficients 224
and 31. Equal positive sample and old values do not imply an unchanged
word: `v=old=65535` yields `q=65279` and `new=65280`. Across the complete
uint16/byte-weight domain, the numerator fits uint32, `q<=65279`, and
`new<=65280`. The upper-clamp taken arm is unreachable in this domain;
out-of-domain inputs do not force it. Only the selected 16-byte reference row may
change on the normal path.

The genuine calls query ids `012d` and `013f` through byte1.bit7 at
`ffff5718+3*sign16(id)+1`, giving `ffff5aa0` and `ffff5ad6`. Either set
result resets all 48 reference words across the six-row, 96-byte reference bank
to the low word of `ROM16[0x00009282]`; stock reset is `ffff`. A set first
result skips the second query. The normal path consumes the sample and
weight inputs; forced reset does not. Diagnostic low bits, samples,
unselected inputs, calibration and other RAM remain unchanged. These are
executed branch and return facts; no direct invocation-count observation
is inferred.

The literal matrix contains 5256 normal learning cases, 540 forced reset cases and
1540 direct predicate cases. There are 5796 natural learner calls.
Stock selector/weight/reset bytes supply 2015 stock normal cases and
18 stock forced cases, totaling 2033 stock natural cases.
Artificial selector, weight and reset contexts retain separate labels.
All 42048 normal output words and each of the 7336 full fifteen-GPR and
SR.T exit vectors have independent arithmetic expectations. Direct
predicate contexts cover all 256 record bytes for both ids and three
independent R4 upper words, plus four low-word-ffff sentinel contexts.
The sentinel returns zero without reading a record. Other signed indices
and diagnostic array extent are outside this contract.

Chain step 2 has sign=none. Separate static caller
anchors do not execute acquisition or full evaluator dispatch. ADC/DMAC,
digital-bin production, metric scaling, threshold/count updates,
diagnostic producers, physical units, sensor mapping, scheduling and
hardware behavior require their own evidence.

## Bounded post-acquisition knock metric

The metric calculation starts at 0004a2b6 and stops before threshold
lookup at 0004a2ee. Its alternate subtraction span is 0004a496..0004a4c8;
complete selection 00049d88..00049e96, complete scaler 00049e96..00049fc0,
bitmap dispatcher 000221bc..000221d6 and ladder 000221e0..000221f8 retain
their stock addresses and instruction bytes.

The caller supplies eight unsigned software sample words at ffff20c2 and
the selected eight-word reference row at ffff2178+16*(c-1). Selector
ROM8[00008b3d].bit3 chooses unsigned channel ffff11de or ffff2143; c is 1..6.
Each signed difference is sample-reference in -65535..65535 and is published
at ffff2158+4*i. The raw source path begins with these explicit post-acquisition
words. ADC/DMAC, the channel-zero guard, filter/transform or bin production,
full evaluator dispatch, ISR/RTE, physical channel order, physical units,
asynchronous cadence and engine reachability remain separate evidence.

ROM8[00008618] masks slots with INT32_MIN sentinels. The complete helper
orders eight values descending and sums the first N ranks excluding
sentinels, with N=ROM8[00008870] in 0..8. N=0 yields zero; N=9..255 is outside
the contract. The selected signed sum is stored at ffff2274+4*(c-1), in
-524280..524280 for legal word differences. A finite network of 28 min/max
compare-exchanges expresses mathematical ordering with the existing
arithmetic Grammar. It is independent of the instruction sequence.

The complete scaler separately admits a full signed32 sum A. Its gain is
G=min(65535,floor(ROM8[000086ac]*ROM8[00008694]*ROM8[000086a7]/128)). The
gain factors are raw bytes; generic owners assign no stock value or scale.
q=floor(abs(A)*G/16384); positive output is min(q,2147483647), and negative
output is -min(q,2147483648). The signed cell at ffff21f8+4*(c-1) is stored
at 00049f32 and read back at 00049f3c. Addition at 00049f42 and store at
00049f4c publish uint32(metric+0x80000000) at ffff21d8+4*(c-1). The signed
cell reader is genuine RAM readback, independently of the normalization
sample/cache parallel stores.

The literal matrix contains 6488 composite, 972 direct selection and 1944
direct scaler contexts. Of the composite contexts, 386 retain the six stock
calibration bytes: selector 0x82, mask 0, count 3 and gain bytes 128. Other
calibrations are labelled artificial inputs. Mask 0..255, count 0..8, all
six channels, unsigned word boundaries, ties, mixed and negative order,
every maximum position, exact gain neighbors 65534/65535/65536 and both
signed saturation neighbors are independently literal. No runtime output
or instruction interpreter supplies an expectation.

Every context checks fifteen GPRs, observed full SR, MACL/MACH/GBR, PR/SP,
the outer C ABI, 112 frame bytes at incoming SP-80..SP+31, all declared
outputs and the remaining 64 KiB RAM and bound data. Entry mode bits are
retained; M/Q/T are cleared and independent T0/1 is seeded before STC
records the prepared SR. Exit is (sr_before&~1)|expected_t. Composite T=0;
direct selection T=((selector&8)==0); direct scaler
T=(A>=0 && q>=2147483648). No arbitrary entry M/Q or runtime-mode change
is claimed. Output capture and the SR observation lie outside the observed
stock frame.

Both subtraction loops, real BSR calls, eight real shift calls, helper
return delay slots and selected stores execute through stock bytes. Shift
indices are 0..7; the zero-result arm 000221e0..000221e4 has byte identity
only. Other shift domains are outside this Region. The early product/carry
branches 00049f12/00049f74 and late positive comparison branch 00049faa are
unreachable under the declared signed32/gain bounds. The full scalar
saturation contexts do not establish those inputs from acquisition.

The sample and reference chain signs vary one word with channel, mask,
count, gain and every other input fixed. The stated stock sign context
uses mask 0, count 3 and gain bytes 128, with sum -196605..196605. Changing
calibrations or channel has no joint monotonicity claim. Normalization and
metric have separate execution boundaries and no joint-invocation claim.
Hardware readiness is NO.

## Bounded software knock normalization

Normalization begins at 0004a26a or alternate 0004a3b0,
stops at 0004a2b6 before subtraction, and includes positive-word divider
00021ce0..00021d6a with its natural returns. Additional stock spans are
0004a3b0..0004a3fe, 0004a438..0004a496 and 0004a4fc..0004a58e. The
last span includes the real delay-slot store at 0004a58c; alignment at
0004a58e is outside the contract.

Explicit inputs are legal selected channel c=1..6, unsigned byte
B=ffff2154, unsigned word P=ffff2152, eight unsigned words
X[i]=RAM16[ffff2132+2*i] and raw byte F=ffff87e1. Selector
ROM8[00008b3d].bit3 chooses ffff11de or ffff2143. Primary R5=c/R11=0
and alternate R14=c/R11=8 agree with the selected byte and ROM bit.
The unused channel byte remains independently supplied and preserved.
The producers of these post-acquisition software inputs and registers are outside the fixture.

B=0 publishes 65535. B>0 gives q[i]=floor(X[i]*P/(32*B)); F=0 publishes
uint16(q[i]), while F!=0 publishes min(65535,8*q[i]). Both sample words at
ffff20c2 and cache words at ffff20d2+16*(c-1) use the same live register,
without a sample RAM readback. Each context checks all sixteen outputs.
Ordinary publication wraps the low word; it has no full-domain positive
sign. Weighted publication saturates separately. B=0 reads neither bins,
multiplier nor mode and calls no divider.

For positive B the exact divisor 32*B is 32..8160. X*P is at most 4294836225,
q at most 134213632, and 8*q at most 1073709056; no uint32 numerator or
weighted shift overflow occurs. Each positive context executes eight real
divider calls with MACL transferred in the delay slot. Fast and long
returns, threshold q 255/256/257, low-word neighbors 65535/65536/65537,
weighted neighbors 8191/8192/8193, both cache branches, both mode branches
and the zero-block fallback are covered. Raw weighted equality 65535 is
unreachable because 8*q is a multiple of eight. The zero and full 32-bit
denominator alternatives are outside the tested divider span.

The independent matrix contains 3281 primary and 3282 alternate contexts:
522 zero-block, 2512 ordinary and 3529 weighted. Its 1325 stock software
arithmetic contexts use selector 0x82, B<=8, P<=256 and F 0/1. These are
software classifications, without a live acquisition claim. Other byte/
word contexts and selector values are explicitly artificial inputs.

Every context checks fifteen GPRs, actual prepared full SR, MACL/MACH/GBR,
PR/SP, the outer ABI, 64 frame bytes at incoming SP-32..SP+31, bound data,
input context and all remaining 64 KiB RAM. Entry retains runtime mode bits,
clears M/Q/T, seeds independent T0/1 and observes SR after LDC. B=0 exits
with (sr_before&~1)|1; B>0 exits with
(sr_before&~0x301)|1|((1-(q[7]&1))<<8). Final Q uses the full quotient before
word wrapping or weighted cap; equal FFFF outputs at q 8192/8193 retain
different Q. Arbitrary incoming M/Q and new runtime modes are outside
this contract. The saved R2 and conditional last-long R3 words, sample/
cache pointer slots and all frame neighbors have literal expectations.

ADC/DMAC/MMIO completion,
filter/transform and bin production, ISR/RTE, full dispatch, channel-zero
guards, physical channel mapping, cadence, physical units and engine
reachability have no proof from this CPU contract. Hardware readiness is NO.

## Bounded owning access identity

The table readers bind lower-cell load 00026510 to root datum 0001108E.
The cache writer belongs to normalization within parent 0004A238.
