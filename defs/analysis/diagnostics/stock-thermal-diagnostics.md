# Stock engine-temperature diagnostics

## Service 0x22 temperature readouts

In the service 0x22 response publisher, family `0x11` dispatches on
the low request byte and loads a longword pointer from its table.
DID `0x1101` reads the conditioned engine coolant byte. DID `0x1106`
reads the published intake-air temperature byte. The response copies
one byte from the selected pointer in either case. The temperature
transfer is in the signal producers, so the response byte retains the
producer's encoded value.

| ROM | Response publisher | `0x1101` record and coolant source | `0x1106` record and intake-air source |
| --- | --- | --- | --- |
| JK08A | `0003235c` | `000226b0` -> `ffff1079` | `000226c4` -> `ffff2837` |
| JK00C | `00032f9c` | `0002273c` -> `ffff107f` | `00022750` -> `ffff28d6` |
| JK00D | `00032f9c` | `0002273c` -> `ffff107f` | `00022750` -> `ffff28ea` |
| JK78C | `00035b80` | `0002271c` -> `ffff106f` | `00022730` -> `ffff278a` |
| 1ND0A and 1ND3B | `00037ff8` | `00022a74` -> `fffe8079` | `00022a88` -> `fffe98aa` |
| 1ME3B | `0003b008` | `00022ae8` -> `fffe8079` | `00022afc` -> `fffe9928` |
| 1EK7A | `0003bf98` | `00022b7c` -> `fffe809d` | `00022b90` -> `fffe9972` |

The stock publishers also use these same temperature signals for
diagnostics and control through their own copies and admission conditions.
The [service inventory](../../../tools/diagnostics/README.md) pins the
records to the exact images.

## Stock thermal diagnostics on JK78C, JK00C, and JK00D

### Descriptor catalogue

Each descriptor is 12 bytes. The packed DTC occupies bytes 6 and 7. The
parallel pointer table selects its two-byte attribute. The descriptor and
pointer bases are `0001b7ac / 0001c5ec` on JK78C, `0001c4e0 / 0001d2b4`
on JK00C, and `0001c500 / 0001d2d4` on JK00D.

| DTC | JK78C index / descriptor | JK00C index / descriptor | JK00D index / descriptor |
| --- | --- | --- | --- |
| P0116 | `297 / 0001c598` | `294 / 0001d2a8` | `294 / 0001d2c8` |
| P0117 | `176 / 0001bfec` | `187 / 0001cda4` | `187 / 0001cdc4` |
| P0118 | `177 / 0001bff8` | `188 / 0001cdb0` | `188 / 0001cdd0` |
| P0125 | `22 / 0001b8b4` | `22 / 0001c5e8` | `22 / 0001c608` |
| P0128 | `189 / 0001c088` | `200 / 0001ce40` | `200 / 0001ce60` |
| P1421 | `265 / 0001c418` | `291 / 0001d284` | `291 / 0001d2a4` |
| P1422 | Absent | `290 / 0001d278` | `290 / 0001d298` |

P0115, P0119, P050A, P050B, and P050E are absent from all three descriptor
tables. The related records below are present. The idle-speed codes retain
their own report paths and the code numbers alone establish their presence.

| Additional DTC | JK78C index | JK00C / JK00D index |
| --- | --- | --- |
| P0112 / P0113 / P0127 | `178 / 179 / 180` | `189 / 190 / 191` |
| P0500 | `0` | `0` |
| P0505 / P0506 / P0507 | `204 / 154 / 155` | `217 / 162 / 163` |

The P0128 descriptor is `360005000000012810000000` on all three. The
attribute pointers select `0001750c`, `000186ae`, and `000186ce`; each
attribute is `00a0`. P0117/P0118 attributes are `02f0` on JK78C and `00b0`
on JK00C/D. P0116, P0125, P1421, and the present P1422 attributes are `00a0`.

### P0128 schedule and record handling

The periodic diagnostic task requires both `ROM8[calibration] & 0x20` and
`ROM8[group] & 0x01` before calling the thermostat wrapper. Both stock
bits are set on JK78C. Both are clear on JK00C and JK00D, whose diagnostic
task branches over the wrapper while retaining its model and report path.

| Stage | JK78C | JK00C | JK00D |
| --- | --- | --- | --- |
| Dispatch slot and task | `00021c38` -> `0009c284` | `00021b8c` -> `0007ee9c` | `00021b8c` -> `0007ee9c` |
| Calibration byte | `000087d3 = a1` | `0000895e = 01` | `0000895f = 01` |
| Group byte | `0001a8c2 = ff` | `0001b66e = 00` | `0001b68e = 00` |
| Wrapper call and target | `0009c3ae` -> `000df0cc` | `0007efd2` -> `000bc1fa` | `0007efd2` -> `000bc1da` |
| Divider and tenth-pass model | `ffff35ce`, `000df0f4` -> `000df756` | `ffff34cc`, `000bc222` -> `000bc8a2` | `ffff34e0`, `000bc202` -> `000bc882` |
| Complementary path with the local index | `000df112` -> `000dce14`, index `189` | `000bc240` -> `000baa04`, index `200` | `000bc220` -> `000ba9e4`, index `200` |
| Report path with the local index | `000df134` -> `0009dfa8`, index `189` | `000bc262` -> `000808e0`, index `200` | `000bc242` -> `000808e0`, index `200` |

The wrapper runs three fast helpers before the divider. Counts below 9
increment the divider. At 9 it calls the inhibit collector and the model,
reads their output flags, and then clears the divider. `000df756` publishes
JK78C result bits `ffff451b.7`, `ffff4557.6`, and `ffff4553.5` from
`ffffaa1c`, `ffffaa20`, and `ffffaa21` at `000df9ac`, `000df9ec`, and
`000df9fe`. JK00C publishes corresponding bits `ffff435a.7`, `ffff4393.3`,
and `ffff438f.0` from `ffff9ca8`, `ffff9cac`, and `ffff9cad` at
`000bcafe`, `000bcb3e`, and `000bcb4e`. JK00D has the same publication
logic with its relocated state. The first bit admits both local branches.
The second selects the complementary call and the third selects reporting.
The no-repeat check tests `ffff456b.7` on JK78C, `ffff43a7.1` on JK00C,
and `ffff43bb.1` on JK00D before either branch. Both registrations use
`EXTU.B` in the call delay slot to pass the positive descriptor index.

#### Inputs and timer state

The model passes the previous-cycle speed byte to its speed-dependent
helper and passes the coolant diagnostic temperature byte to its final
temperature stage. The raw values stay in ECU units.

| Signal or state | JK78C | JK00C | JK00D |
| --- | --- | --- | --- |
| Previous-cycle speed input | `ffff10fc` at `000df8a8` | `ffff111a` at `000bc9f8` | `ffff111a` at `000bc9d8` |
| Coolant temperature used by P0125 and thermal model | `ffff1069` at `000ca6c8` and `000df95a` | `ffff1078` at `000ab868` and `000bcaa8` | `ffff1078` at `000ab854` and `000bca88` |
| Temperature byte supplied to the model's intake-side term | `ffff2690` at `000df896` | `ffff27ce` at `000bc9e8` | `ffff27e2` at `000bc9c8` |
| Elapsed accumulator and reload timer | `ffff329e / ffff4771` | `ffff3212 / ffff45ba` | `ffff3226 / ffff45ce` |
| Elapsed producer | `000df3d4` | `000bc514` | `000bc4f4` |

The elapsed producer increments its unsigned word with saturation at
`0xffff` when its countdown is zero and reloads the countdown to 100
after a successful increment. The same routine retains the start-side
temperature byte, modeled state byte, and elapsed word on the admitted
report path. This divider contract states raw scheduler and timer counts.

#### Temperature decision

The model calls `000df478`, `000bc5c4`, and `000bc5a4` from `000df980`,
`000bcace`, and `000bcaae`, respectively. The decision state starts at
`ffffaa0c` on JK78C and `ffff9c98` on JK00C/D. State byte `+0x17` admits
the predicted-temperature timer. The saturating 32-bit counter at `+0` resets below
the ROM temperature floor and increments at or above it. Reaching the
first timer limit sets `+0x13`.

| Input or limit | JK78C | JK00C | JK00D |
| --- | --- | --- | --- |
| Predicted temperature, state `+0x22` | `ffffaa2e` | `ffff9cba` | `ffff9cba` |
| ROM temperature floor | `00008a42 = 7b` | `00008cbc = 00` | `00008cbe = 00` |
| Three consecutive 16-bit timer limits | `00008dd8 = 0370, 0000, 0000` | `00009100 = 0000, 0000, 0000` | `0000910e = 0000, 0000, 0000` |
| Measured coolant load in decision | `000df4da` | `000bc626` | `000bc606` |

The measured coolant byte is compared with the same floor. The two
unsigned 32-bit outcome counters at `+4` and `+8` reset the opposite
counter on their admitted paths. At or above the floor with no retained
terminal latch, the warm path can set the complementary flag `+0x14`
and common result flag `+0x10`. Below the floor or with a retained
terminal latch, byte `+0x1e` admits the failure-side timer. At its limit,
while the complementary flag is clear, byte `+0x18` selects retention
in `+0x16` or assertion of the failure flag `+0x15` and `+0x10`.
Suppression from `+0x23` through `+0x1d` clears the outcome flags and
common result flag. The timer limits count model invocations.

On JK78C `000dfb5e` seeds the signed estimate with `10000 * ECT - 500000`
or uses the retained estimate at `ffffaa34`, applies the computed delta,
and clamps to `[-500000, 2050000]`. It publishes the signed accumulator
at `ffff2ed4` and the divided result plus `0x32` at `ffff2ed1`. The
coordinator copies the result byte to `ffffaa2e` before the decision call.

### Related ECT and IAT conditions

P0125 reads the start-side and current coolant values. It waits for a
32-bit accumulator to reach `0xa00 * window_byte`. The start-side coolant
value selects between two calibration floors, both `0x3c` in each stock
ROM. The worker passes index 22 when the current coolant byte is strictly
below the selected floor. The start-side selection threshold is `0x28`.

P0116 requires its local admission flag and an unsigned accumulator at
least `ROM16[limit] << 8`. The report requires an unsigned metric at or
below its ROM ceiling. At window completion the routine clears the
accumulator and advances a saturating 16-bit completion count.

| Path | JK78C | JK00C | JK00D |
| --- | --- | --- | --- |
| P0125 function / call | `000ca606 / 000ca6d4` | `000ab7fc / 000ab874` | `000ab7e8 / 000ab860` |
| P0125 elapsed input / window byte | `ffff2a88 / ffff3734` | `ffff2c28 / ffff361c` | `ffff2c3c / ffff3630` |
| P0116 function / call | `000caaee / 000cab22` | `000abbfa / 000abc2e` | `000abbe6 / 000abc1a` |
| P0116 elapsed calibration | `0000922a = 0438` | `0000962e = ffff` | `0000963c = ffff` |
| P0116 metric / ROM ceiling | `ffff2af9 / 00008abc = 34` | `ffff2c97 / 00008d59 = 00` | `ffff2cab / 00008d5b = 00` |
| P0117 / P0118 report calls | `000cacba / 000cad00` | `000abdaa / 000abdf0` | `000abd96 / 000abddc` |
| P0112 / P0113 / P0127 report calls | `000c8950 / 000c89a0 / 000c8a3c` | `000a9c9a / 000a9ce4 / 000a9d66` | `000a9c86 / 000a9cd0 / 000a9d52` |

The P0117 and P0118 worker uses independent byte countdowns. Each timer
reloads to 50 when its comparison or admission fails. With admission valid,
sample `<= 2` and a zero low countdown permit P0117. Sample `>= 0xf2`
and a zero high countdown permit P0118. The sampled byte is `ffff10f2`
on JK78C and `ffff1111` on both JK00C and JK00D. The stored calibrated
coolant byte and the circuit comparator sample are distinct inputs.

### Cold-start routing

The diagnostic task calls `000bd3bc` at `0009c47a` on JK78C. That routine
tests `ROM8[0001a8d2].0`, whose stock byte is `0xf1`, for P1421. It
tests `ffff44fb` masks `0x04` and `0x08` for the complementary and report
calls, respectively. The report at `000bd74a` passes index `0x0109` to
`0009dfa8`. The P1421 report path is admitted by stock configuration and
still requires the current failure flag.

On JK00C and JK00D the diagnostic task calls `000a109c` and `000a1088`
at `0007f0b6`. The stock group byte `0xf0` at `0001b67e` or `0001b69e`
has both routing bits clear. The P1421 report calls at `000a13fe` and
`000a13ea` pass `0x0123`. The P1422 report calls at `000a142e` and
`000a141a` pass `0x0122`. Both report branches and their complementary
counterparts are bypassed in the stock routing stage.

## Stock 1ND thermal diagnostics

This specification covers the checked stock 1ND0A and 1ND3B images. The
descriptor table and reviewed executable paths are byte-identical across
the two images. Calibration operands below are checked in each image
because some earlier ROM regions differ. Addresses and mask values are
hexadecimal. Counts and temperatures are raw firmware quantities.

### Descriptor inventory and activation

The 331 zero-based 12-byte descriptors occupy `0001be00..0001cd83`;
the big-endian SAE code is at record offset 6. The corresponding 331
four-byte attribute pointers start at `0001cd84`. Both images contain
the following records.

| DTC | Index | Descriptor | Exact descriptor bytes | Attribute target / contents | Transfer |
| --- | ---: | --- | --- | --- | --- |
| P0128 | 193 | `0001c70c` | `360005000000012810000000` | `00017b56 / 00a0` | `0010551a` |
| P0125 | 22 | `0001bf08` | `080005000000012500000000` | `00017b90 / 00a0` | `000ed0f2` |
| P0116 | 308 | `0001cc70` | `530300000000011600000000` | `00017b98 / 00a0` | `000ed776` |
| P0117 | 180 | `0001c670` | `350700000000011700000000` | `00017b96 / 00b0` | `000ed8f8`; alternate fragment `000ed834` |
| P0118 | 181 | `0001c67c` | `350600000000011800000000` | `00017b94 / 00b0` | `000ed956`; alternate fragment `000ed878` |
| P1421 | 276 | `0001caf0` | `460000000000142110000000` | `0001799e / 00a0` | `000de756` |
| P1217 | 2 | `0001be18` | `010000000000121700000000` | `00017ac0 / 22e0` | `00076e2a` |

P0115, P0119, P050A, P050B and P050E have no descriptor in either image.
The P1217 row identifies the neighboring overtemperature code and its
index load. Its monitor is outside the reviewed window.

`ROM32[00022250] = 000b6384` selects the periodic diagnostic task. It
calls the P0117/P0118 routine at `000b6476`, the P0125 coordinator at
`000b647c`, and the P0116 coordinator at `000b6482`. The first branch
uses stock enable bits `0x80` and `0x40` in `ROM8[0001af11] = 0xcc`.
P0125 reaches its coordinator, which returns on the clear bit 0 of
`ROM8[0001aee4] = 0x00`. P0116 reaches its coordinator, which returns
on the clear bit 3 of `ROM8[0001af2f] = 0x00`. The P0128 task branch
requires both `ROM8[00008864] & 0x20` and
`ROM8[0001af12] & 0x01` before the JSR at `000b64a4`.
The first byte is `0x21` and the second is `0x64` in both stock images,
so the periodic task skips the P0128 monitor body.

The failure transfers use `000ba0b8`. Its normal report path calls
`000ce048` at `000ba126`. The marker sets bit 7 of byte 1 of the
three-byte runtime record at `fffed298 + 3 * index`. Shared report
activity is maintained at `fffebf4a`. The monitor-local decisions below
describe the executable branches. Their stock scheduling gates above
determine which branch families can run.

### P0128 thermostat decision

`00105394` is the monitor entry. The start-temperature path and the first
thermal decision use separate inputs.

| Input or state | Exact binding |
| --- | --- |
| Conditioned coolant publication | `fffe8079`, written at `00040218`; snapshot `fffe8073` from `000212e2..000212e6` |
| Selected start coolant | `fffe8076`, written at `00040238` after selector `0004039e`; snapshot `fffe8070` at `000212ca..000212ce` |
| Additional starting temperature input | `fffe8075` is a transfer-curve output, with a seed at `00030c48`; snapshot `fffe806f` at `000212d2..000212e4` |
| Monitor-local snapshots | One-shot `fffea76e <- fffe806f` at `00105438`, and `fffea70c <- fffe9796` at `001054c2`. Each requires `(fffeb7f3 & 0x10) == 0` or the battery snapshot `fffe80fc >= 100`; the second additionally requires `fffeb7ff & 0x04` |
| Thermal model inputs | Live ECT is `fffe8073`. The model forms `10 * (fffe8073 - fffefe3b)` and writes the difference from its retained reference to `fffe9c3a`. It also uses vehicle speed `fffe8104`, the operating word `fffe81b6`, and the two thermal prediction bytes at `fffefe4e` |
| Model cadence | `fffea7e7` advances from 0 through 9, then `001054d0` calls the exclusion stage `00105188` and `001054d4` calls model `001059c4`. The byte resets at `00105532`. This is every tenth monitor invocation when enabled |
| Elapsed and event counters | A 100-count reload at `fffebadc` gates the saturating `fffea452` elapsed counter. The secondary stage `00105614` runs each invocation and maintains `fffebb9c`, `fffebb9e` and the event counter `fffecb34`. Timer setup uses the two words at `00008f28`, both `0xffff` in stock |

The scheduler snapshot at `fffe8070` is separate from live coolant
`fffe8073`. The monitor also retains a word at `fffebf46` from
`fffe9754` and can latch the comparison
`u16(fffebf46) > u16(fffe9754) + 0x3200` after countdown
`fffeba9f` expires. Its refill value is 100. The two ROMs use the same
instructions for this branch.

`00105188` reduces a set of prerequisite diagnostic status bytes into
an exclusion bit. It clears `fffeb894 & 0x80` only if none of its
checked status bytes has mask `0x60` and `fffeb842 & 0x20` is set.
`001059c4` combines operating qualification, accumulated counters and
temperature history. It counts run/coast qualifications, including a
50-model-pass threshold at `000090e2`, vehicle-speed limit 10 at
`0000876b`, and an operating-word bound `0xffff` at `0000916c`.
It evaluates a two-axis surface at `0000e848` and two instances of
the same byte curve at `00013f5a`, with speed/load and temperature
history feeding fixed-point terms. The surface and byte curve differ
between the two stock images. The selected ECT admission window reads
lower/upper bytes `0xff/0x00` at `00008b67/00008b66`, so that
particular admission clause rejects every raw byte in both stock images.

At the model output, the end-of-evaluation qualifier is
`fffeb834 & 0x20`. The positive result flag is `fffeb878 & 0x80`;
the failure candidate is `fffeb873 & 0x01`. These are the direct
control dependencies for the two index-193 transfers:

- When the one-shot completion bit `fffeb893 & 0x40` is clear, a
  qualified positive result calls the generic DTC state update
  `00103344(193)` at `001054f4`. That helper clears byte 2 bit 0
  of the indexed runtime record, and conditionally updates its other
  state bits. The monitor sets `fffeb82e & 0x01` and the completion bit.
- In the same evaluation window, the code retests the qualifier and the
  failure flag. `00105516..0010551c` zero-extends `0xc1` into R4 and
  calls the report dispatcher. The monitor sets `fffeb82e & 0x02`,
  the completion bit, and `fffeb894 & 0x10`.
- The first report snapshot stores the selected start-coolant coordinate,
  `fffe9ae2`, the elapsed counter, and the operating flag at
  `fffecbaf`, `fffebe66`, `fffec6ca`, and `fffebe8d`, respectively,
  then sets `fffeb894 & 0x20`. A task reset at
  `001053a0..00105412` clears the reviewed result and snapshot state.

The ROM establishes counts per scheduled invocation and the encoded
admission windows. No conversion of the monitor countdowns to seconds
or of all modeled inputs to measured temperatures is established here.

### P0125 and ECT circuit monitoring

P0125 coordinator `000ed558` calls `000ecefc`, `000ecfdc` and
`000ed080` in order. The coordinator admits the calculation only for
the shared ECT monitor permit `fffeb842 & 0x20`, eligible diagnostic
status and an unset completion bit. The initial selected coolant
`fffe8070` chooses a curve around the raw breakpoint 40 at
`0000868e`. `000ecefc` updates the calibrated threshold byte
`fffea958`. `000ecfdc` integrates in `fffe9bcc`: the selected
normalized temperature `fffe8071` indexes the curve at `00016a38`,
and the result is compared against `fffe9776` to choose a step of
256 or `ROM8[00008b9a] = 169`. Battery snapshot must be at least
`0x89` for accumulation. The alternate state subtracts
`ROM8[00008b56] = 123` with a floor of zero. The accumulator clamps to
`0x00ffffff`.

`000ed080` requires `fffe9bcc >= 2560 * fffea958`. It then compares
live ECT snapshot `fffe8073` with the threshold selected by
`fffe8070 < 40`. The two stock thresholds at `00008377` and
`00008b53` are both 45. A strict lower live code calls the common
report with index 22 loaded in the delay slot at `000ed0f4`.
The decision sets `fffeb859 & 0x40` and maintains the one-shot
evaluation counter at `fffecbac`.

P0116 coordinator `000ed6b0` uses eligibility function `000ed1b4`
and integrator `000ed3d4`. The latter uses the selected pair's
normalized lane `fffe8071` and the same ROM curve, decrement and clamp
as the P0125 integrator. The coordinator tracks minimum and maximum
live ECT at `fffea954/fffea955` while the operating state allows
sampling and publishes `sat_u8(max - min + 50)` to `fffe9c3d`.
With eligibility set, `u32(fffea950) >= ROM16[00009444] << 8`
triggers evaluation. Passing a less-than-or-equal comparison against
`ROM8[00008b97]` calls the dispatcher. The stock operands are
`0xffff` and zero respectively. The transfer at `000ed776`
constructs index 308 by shifting immediate `0x4d` left by two in
the delay slot. Evaluation resets the integrator, sets the
completion latch and increments `fffecbb2` with saturation.

The scheduled P0117/P0118 entry `000ed886` reads electrical input
snapshot `fffe80fa`. It selects
the stock branch through clear bit 5 of `ROM8[0001aedc] = 0x12`.
With the common permit set and `fffeb7f3 & 0x10` clear, P0117 tests
`raw <= 2` against zero countdown `fffeba58`, then dispatches
index 180 at `000ed8f8`. P0118 tests `raw >= 242` against zero
countdown `fffeba59` and tail-transfers index 181 at `000ed956`.
Ineligible paths reload the respective countdown with 50. The raw
cloned logic at `000ed7e4` contains equivalent index transfers at
`000ed834` and `000ed878`; no scheduled caller was established for
that fragment.

### Cold-start temperature selection

P1421 has one stock descriptor. P1422 has none. The periodic task
calls cold-start coordinator `000de4f4` at `000b656a`. Its index-276
state-update and report paths at `000de746` and `000de756` require
`ROM8[0001af22] & 1`. Both stock images hold `0xf0`, so those
transfers are skipped. With that gate set, bit 2 of `fffeb813`
qualifies the state-update transfer to `00103344`, and bit 3 qualifies
the report to `000ba0b8`. Both calls form the index from raw immediate
`0x45` shifted left by two in the delay slot. The companion behavior
outside these two transfers is outside the reviewed P1421 path.

The selected coolant input used by the warm-up paths is also the
independently verified temperature coordinate for the stock 1ND VVEL
startup duration. Selector `0004039e` refreshes from the conditioned
coolant publication or retains the previous selection. The snapshot
feeds lookup `0002893c` with axis `00017812` and values `00016440`.
The executable axis and refresh conditions are specified in
`defs/analysis/valve-timing/VQ37.temperature-axis-scale.md`. The
startup lookup establishes temperature-dependent operating behavior
without an associated P050A, P050B or P050E descriptor.

## SH7059 thermostat and cold-start diagnostics

The periodic diagnostic task is at `0x000c0040` on 1ME3B and `0x000c4884` on 1EK7A. The stock scheduler pointers are at `0x000222c8` and `0x0002235c`, respectively. Record indices select a 12-byte descriptor and an independent attribute halfword. The packed code occupies descriptor bytes 6 and 7.

| Layout | Code and index | Descriptor | Attribute halfword | Diagnostic group byte in stock |
|---|---|---|---|---|
| 1ME3B | P0125 22 | `0x0001c060` | `0x00017c5a = 0x00a0` | `0x0001afbc = 0x00` |
| 1ME3B | P0128 194 | `0x0001c870` | `0x00017c20 = 0x00a0` | `0x0001afea = 0x64` |
| 1EK7A | P0125 22 | `0x0001caa0` | `0x00018680 = 0x00a0` | `0x0001b9e8 = 0x00` |
| 1EK7A | P0128 194 | `0x0001d2b0` | `0x00018646 = 0x00a0` | `0x0001ba16 = 0x64` |
| 1EK7A | P0128 348 | `0x0001d9e8` | `0x00018488 = 0x00a0` | `0x0001ba46 = 0x00` |
| 1EK7A | P050B 335 | `0x0001d94c` | `0x00018470 = 0x00a0` | `0x0001ba3b = 0x00` |
| 1EK7A | P050A 336 | `0x0001d958` | `0x00018474 = 0x00a0` | `0x0001ba3b = 0x00` |
| 1EK7A | P050E 337 | `0x0001d964` | `0x00018476 = 0x00a0` | `0x0001ba3b = 0x00` |

The 1ME3B stock descriptor extent contains P0125 and one P0128 record. Its extent contains no P050A, P050B or P050E descriptor. At their own stock group gates, the two P0125 coordinators return, the two index-194 P0128 calls are skipped, the 1EK7A index-348 coordinator returns, and the 1EK7A cold-start evaluator and its three reports are skipped. The group and runtime predicates below describe the retained code paths.

### P0125 coolant warm-up

The periodic task calls the P0125 coordinator at `0x000c0132` on 1ME3B and `0x000c497c` on 1EK7A. Its first gate requires group 8 bit `0x01`. The coordinator owns the episode state and tail-calls the index-22 decision routine. The two later runtime gates require the layout's diagnostic operating-enable bit and clear `0x60` in two runtime-only status bytes. An already completed episode also clears admission. The reset flag clears episode bits 0 and 1, the delay byte, the accumulator and a lookup snapshot word. A distinct option bit conditionally resets the persistent event-count lane.

| Layout | Coordinator and group test | Reset predicate | Episode byte, diagnostic operating enable | Runtime-only byte-2 statuses | Accumulator update and report |
|---|---|---|---|---|---|
| 1ME3B | `0x000f9362`, `0x000f936e` | `0xfffeba65 & 0x02` | `0xfffeb9bc`, `0xfffeb9a7 & 0x40` | `0xfffed80c`, `0xfffed81b` | `0x000f8de4`, `0x000f8e8a` |
| 1EK7A | `0x0010d088`, `0x0010d094` | `0xfffebe09 & 0x01` | `0xfffebd55`, `0xfffebd3d & 0x01` | `0xfffede3b`, `0xfffede4a` | `0x0010cb04`, `0x0010cba8` |

When admitted and operating status bit `0x10` is set, the coordinator captures a lower value of the neighboring temperature-coordinate byte on a `0xffff8023 & 0x40` tick and clears the accumulator on that transition. If that operating bit is clear, it sets the minimum byte to `0xff`. The accumulator stage zeros its state when admission or operating status is clear. It updates on the same tick while its additional inhibit is clear. With its selector set, it subtracts stock `0x7b` to a floor of zero. The other arm requires the battery snapshot at least `0x89`, refreshes a lookup threshold using the neighboring temperature-coordinate byte, and adds either 256 or a calibrated byte. The positive branch saturates at `0xffffff`.

| Layout | Accumulator, minimum, delay threshold | Operating bit | Lookup snapshot | Event-count and latch |
|---|---|---|---|---|
| 1ME3B | `0xfffe9c74`, `0xfffeaa62`, `0xfffeaa6c` | `0xfffe9441 & 0x10` | `0xfffea60a` | `0xfffecca8`, `0xfffeba02 & 0x02` |
| 1EK7A | `0xfffe9d28`, `0xfffead6a`, `0xfffead74` | `0xfffe944d & 0x10` | `0xfffea82e` | `0xfffed1b4`, `0xfffebda5 & 0x08` |

The report routine requires episode admission, the operating bit and `accumulator >= u8[delay] * 0x0a00`. The first qualified decision increments the unsigned 16-bit event count with saturation and sets its latch. It chooses a coolant threshold by comparing the selected temperature snapshot against stock `0x28`. Both stock threshold arms are `0x2d` on both layouts. A strict unsigned `current_coolant_snapshot < threshold` calls the full reporter with index 22. The routine sets episode bit 1 after either temperature outcome. The retained reports are at `0x000f8f00` and `0x0010cc1e`.

| Layout | Selected / current coolant snapshot | ROM cutoff, lower-selected threshold, other threshold | Coordinator tail call |
|---|---|---|---|
| 1ME3B | `0xfffe8070` / `0xfffe8073` | `0x00008697`, `0x0000837f`, `0x00008ba4` | `0x000f94b2` |
| 1EK7A | `0xfffe8094` / `0xfffe8097` | `0x000086f4`, `0x00008391`, `0x00008c21` | `0x0010d216` |

The lookup for the positive increment compares a current unsigned threshold word with its lookup result and uses 256 when the result is at or below that word. Otherwise it uses ROM `0x00008bac = 0x00` on 1ME3B or `0x00008c65 = 0xa9` on 1EK7A. The 1ME3B delay lookup receives twice the captured minimum, capped at `0xff`, in `0x000f8d04`. The 1EK7A coordinator selects an axis and byte table using the same selected-temperature cutoff and invokes the lookup at `0x0010d208` with the captured minimum. The counter comparisons use the raw encoded inputs.

### P0128 index 194 thermostat model

The task requires global ROM mask `0x20` and group `0x36` mask `0x01` at the model call. The global ROM byte is `0x21` on both layouts. Group byte `0x64` leaves the group mask clear. These gates govern the call itself, including the local timer and result-state updates.

| Layout | Global option | Task gate and model call | Coordinator | Tick counter | Record guard and model update |
|---|---|---|---|---|---|
| 1ME3B | `0x00008888` | `0x000c014a` / `0x000c0154` / `0x000c015a` | `0x00110fc4` | `0xfffea8d5` | `0x00110db8` / `0x0011160e` |
| 1EK7A | `0x000088f4` | `0x000c4994` / `0x000c499e` / `0x000c49a4` | `0x001262cc` | `0xfffeabb3` | `0x001260b8` / `0x00126a56` |

The coordinator increments its byte while below nine. At nine or above it runs the record guard and model update and resets the counter after the decision. The record guard requires clear `0x60` in selected three-byte diagnostic runtime records and the operating-enable bit. It publishes a separate inhibit bit consumed by the model. The main decision uses a local inhibit and an enable followed by two separate result tests. The complementary update can precede the full reporter in one invocation. The second enable sample is taken after the complementary update.

The guard tests byte 2 of P0500, P0170, P0173, P0300 through P0306, P0607, U1000, U0164 and U0140 on both layouts. The remaining reads are runtime-only slots. Their indices are `335,339,334,350,351,353,354` on 1ME3B and `356,360,355,371,372,374,375` on 1EK7A. The ordered status map accompanies this specification. The guard clears `0xfffeb9fd & 0x20` or `0xfffebd9f & 0x40` on admission and sets that bit on failure.

| Layout | Local inhibit clear | Enable set | Complementary flag and call | Full report flag and call |
|---|---|---|---|---|
| 1ME3B | `0xfffeb9fc & 0x10` | `0xfffeb998 & 0x04` | `0xfffeb9de & 0x40`, `0x0011111e` | `0xfffeb9da & 0x80`, `0x00111144` |
| 1EK7A | `0xfffebd9e & 0x20` | `0xfffebd2e & 0x80` | `0xfffebd7c & 0x04`, `0x00126422` | `0xfffebd78 & 0x40`, `0x00126448` |

The primary model has its own group `0x36` test and selected-temperature interval in the qualification calculation. The model compares the unsigned selected byte against an inclusive lower byte and an exclusive upper byte. The lower byte is `0xff` and the upper byte is `0x00` in both stock images, yielding an empty interval. This provides a second stock barrier at the model decision if the scheduler gate is considered separately.

| Layout | Model work block | Selected temperature | Stock upper / lower bytes | Qualification store |
|---|---|---|---|---|
| 1ME3B | `0xfffefea0` | `0xfffe8070` | `0x00008bb7 = 0x00` / `0x00008bb8 = 0xff` | `0x0011178c` |
| 1EK7A | `0xffff0d30` | `0xfffe8094` | `0x00008c34 = 0x00` / `0x00008c35 = 0xff` | `0x00126bd0` |

The same calculation also requires the model's status predicate and the raw byte at `0xfffe97c3` or `0xfffe97fb` to be at least stock `0xff`. The floor literals are `0x00008a95` and `0x00008b0e`. The coordinator clears local episode bits and selected working variables on its layout's reset predicate. The primary balance lookup also reads the previous Base Fuel Schedule word and a separate raw word. The source pairs are `0xfffe802c` / `0xfffe819e` at `0x001117de` / `0x001117e8` on 1ME3B and `0xfffe8030` / `0xfffe81c4` at `0x00126c20` / `0x00126c2a` on 1EK7A. The mapping of the other model-balance terms to physical inputs remains open.

### 1EK7A P0128 index 348

The task calls a separate coordinator `0x001268bc` at `0x000c49ac`. Group `0x66` bit `0x01` controls entry to its counter. The coordinator returns immediately while stock group byte `0x00` holds. Its own counter `0xfffe9dfc` increments below nine. At nine it calls `0x00127d98`, `0x0012810c`, `0x001290cc`, `0x0012a598`, `0x0012c060` and `0x0012cb7c` in order. It then reads `0xfffebda3`. Bit `0x80` selects the full report at `0x00126906`. If that bit is clear, bit `0x02` selects the complementary update at `0x00126916`. The coordinator resets only its own tick counter after the evaluation.

### 1EK7A P050A, P050B and P050E

At `0x000c4a68..0x000c4a72` the task tests the three group `0x5b` masks `0x01`, `0x04` and `0x02`. Any set bit allows the evaluator `0x000f424a` at `0x000c4a76`. The task calls report wrapper `0x000f6528` at `0x000c4a7c` regardless of that producer gate. The wrapper individually repeats the group bits. Stock zero prevents the P050x evaluator call and each of the identified report and complementary paths. It still calls the shared wrapper for its other records.

| Index and code | Required group mask | Complementary phase bit and call | Full report bit and call |
|---|---|---|---|
| 337 P050E | `0x01` | `0xfffebd22 & 0x20`, `0x000f6838` | `0xfffebd22 & 0x40`, `0x000f6856` |
| 335 P050B | `0x04` | `0xfffebd21 & 0x02`, `0x000f688a` | `0xfffebd21 & 0x80`, `0x000f68a8` |
| 336 P050A | `0x02` | `0xfffebd21 & 0x02`, `0x000f68dc` | `0xfffebd22 & 0x10`, `0x000f6914` |

The per-code complementary and full tests are separate. The 1EK7A full paths call `0x000c7990` and complementary paths call `0x00124154`. On 1ME3B the full reporter is `0x000c38f8` and the index-194 complementary update is `0x0010f2f0`. Their DTC-bit meanings are operational branch outcomes.

The evaluator maintains a separate cold-start state at `0xffff0234`. Its state bytes at offsets `0x07`, `0x06`, `0x05`, `0x04` and `0x03` feed the shared phase bit, the P050A result, the P050B result, the P050E phase bit and the P050E result, respectively. It derives the published flags after servicing the local phase helpers.

| Timer | Limit storage and stock literal | Counter and call | Behavior |
|---|---|---|---|
| First qualification | `0xffff0264`, ROM16 `0x00008ffa = 0x0000` times ten | `0xffff0254`, helper `0x00029142` at `0x000f4ae4` | Clear on false input. Count on consecutive qualified calls and clamp at the limit. A zero limit can qualify on the first true call. |
| Second qualification | `0xffff0260`, ROM8 `0x000083d5 = 0x00` times ten | `0xffff0250`, helper `0x0002917c` at `0x000f4b60` | Clear the counter and latch on reset. Latch the first true input, count subsequent calls and compare with the limit. |

One earlier evaluator predicate tests `u8[0xfffe92b1] - ROM8[0x0000887f] > ROM8[0x00008880]`. Both stock calibration bytes are `0x30`. The evaluator publishes this predicate separately in `0xfffebd77 & 0x80`, and later maps its phase state to the report bits listed above. This raw comparison does not assign a physical unit to the input.
