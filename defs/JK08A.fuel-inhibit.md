# JK08A Fuel-Output Inhibit Arbitration

## Status and scope

This document records the complete static software model of the aggregate
six-channel fuel-output inhibit coordinator in the exact JK08A/JK03A
executable. It covers all global Boolean contributors, the two calls whose
return values are discarded, DFCO/count-mask composition, Nissan service 0x30
Power Balance replacement, the ETC-actuator-fault auxiliary mask, and final
publication to `0xFFFF22E0`.

The operational conditions and ordering are established by executable code.
External diagnostic names are used only where an exact ROM descriptor or a
structured Nissan-family diagnostic definition connects the code to that
name. The two shared prerequisite bits and the direct composite-status seed
are cleared by normal startup and recovery initialization. A whole-program
p-code census and the recovered DMAC configuration find no path that can set
any of them, making the two contributors and the direct seed stock-inert in the
proven application lifecycle.

## Exact evaluation and mask order

Periodic-table index 27 invokes `fuel_output_inhibit_coordinator` at
`0x0004ED88`. Its global accumulator receives exactly 15 Boolean results.
`0x0004F758` and `0x0004F7E0` execute in the same sequence but their return
values are discarded; they only update state consumed by later calls.

| Order | Function | Operational role | Stock classification |
|---:|---|---|---|
| 1 | `0x0004F14E` | zero-speed, high-BFS, high-RPM delayed inhibit | live |
| 2 | `0x0004F19C` | vehicle-speed fuel-cut state machine | live |
| 3 | `0x0004F282` | main engine-speed fuel cut | live |
| 4 | `0x0004F324` | stationary engine-speed fuel cut | live |
| 5 | `0x0004F494` | P1217 engine-overtemperature fuel inhibit | live |
| 6 | `0x0004F662` | BFS-threshold hysteresis state | stock-inert |
| 7 | `0x0004F736` | dual-bank MAF diagnostic summary plus RPM inhibit | conditional |
| side effect | `0x0004F758` | low-speed BFS/RPM latch update | return discarded |
| 8 | `0x0004F9C4` | transition-window, low-speed RPM inhibit | conditional |
| side effect | `0x0004F7E0` | low-speed RPM exposure accumulator update | return discarded |
| 9 | `0x0004F958` | sustained low-speed RPM inhibit | live |
| 10 | `0x000507CE` | composite status/RPM inhibit | conditional; bit-7 seed stock-inert |
| 11 | `0x00050920` | critical ECM/ETC diagnostic RPM inhibit | conditional |
| 12 | `0x0004FAA0` | shared status byte bit 1 | stock-inert lifecycle-zero input |
| 13 | `0x0004FAAC` | status-gated engine-running inhibit | stock-inert lifecycle-zero prerequisite |
| 14 | `0x00050A60` | CAN-derived requested RPM ceiling | conditional |
| 15 | `0x00050B3C` | P0011/P0021 intake-valve-timing fault RPM inhibit | conditional |

Any nonzero result makes the global mask `0x3F`. The remainder of the
coordinator is exactly:

```text
B = OR of the 15 Boolean contributors
G = 0x3F if B != 0 else 0x00
D = mask returned by dfco_state_machine
C = mask returned by count_to_inhibit_mask
P = G | D | C
R = cached Power Balance mask if Power Balance is active else P
A = ETC-actuator-fault auxiliary mask
0xFFFF22E0 = (R | A) & 0x3F
```

A global condition therefore inhibits all six channels before diagnostic
replacement. Power Balance can replace or clear the combined global, DFCO,
and count result. The auxiliary ETC mask is added after replacement and cannot
be cleared by Power Balance.

## Global contributors

### Zero-speed, high-BFS, high-RPM delay

`0x0004F14E` returns true only while all of these conditions hold:

```text
uint8[0xFFFF110E] == 0
uint8[0xFFFF11AE] >= ROM8[0x88E3] = 0x60       # 4800 RPM
high_byte(uint16[0xFFFF1024]) >= ROM8[0x8B5D] = 0x48
uint8[0xFFFF253B] == 0
```

Any failed condition reloads `0xFFFF253B` with 110. The byte lies outside the
code-proven `0xFFFF256A..0xFFFF25F3` tenth-phase decrement range. Its decrement
owner and wall-clock period remain unresolved, so the value 110 is not assigned
a `10.24 ms` conversion.

### Vehicle-speed fuel cut

`0x0004F050` maintains `0xFFFF24A7.bit5` with an RPM/25 hysteresis helper.
The bit is set below 4500 RPM and, once set, does not clear until at least
5000 RPM. `0x0004F19C` requires this gate to be clear.

With `0xFFFF24A6.bit0` clear, the state machine arms at coarse vehicle-speed
count `>=93`. Stock delay `ROM8[0x8CAF]` is zero, so it can set the active bit
in the same invocation. Once active, it remains active at speed count `>=91`
while the RPM gate remains clear. It clears below 91 or when the RPM gate sets.
The homologous speed conversion is approximately 2 km/h per count, placing the
two candidate physical boundaries near 186 and 182 km/h. The raw count
thresholds and full `0x3F` fuel-cut result are exact.

### Main and stationary engine-speed cuts

`0x0004F282` and `0x0004F324` are the main and stationary engine-speed
fuel-cut state machines. Each returns one Boolean contributor and therefore
produces the same full `0x3F` global mask. Their thresholds, delays, and
interaction with the separate request limiter are specified in
[`JK08A.limiters.md`](JK08A.limiters.md).

### P1217 engine-overtemperature protection

`0x0004F494` is enabled by `ROM8[0x186C9].bit0`, which is set in stock JK08A.
It maintains a coolant hysteresis state from raw coolant snapshot
`0xFFFF1071`:

```text
set at raw >= ROM8[0x8D15] = 190
retain at raw >= 180
clear below raw 180
```

The `deg C + 50` coding that the ECU declares for the coolant byte through
J1979 PID `0x05` puts the boundaries at 140 and 130 deg C. The function reports
exact descriptor index 2,
whose JK08A record at `0x19378` contains P1217 `ENG OVER TEMP`.

The final fuel-inhibit state additionally requires the internal P1217 phase
bit, current `0xFFFF2458.bit5` clear, and an RPM/25 hysteresis state that sets
at 1900 RPM and retains through 1700 RPM. The diagnostic identity and software
cut path are exact; the temperature conversion remains homologous until
hardware validation.

### Stock-inert BFS hysteresis branch

`0x0004F662` compares the high byte of current Base Fuel Schedule
`0xFFFF1024` with RPM-indexed maps `0x12116` and `0x12984`. Both complete maps
contain zero in stock JK08A. An unsigned BFS byte can never be below the
clear-state threshold zero, so bit `0xFFFF249F.bit0` cannot set through this
function. If the bit is externally nonzero, the set-state comparison with zero
clears it on the next evaluation. The branch is structurally present but
stock-inert.

### Dual-bank MAF diagnostic summary RPM branch

Runtime record `0x129` is an extension summary rather than a ROM-backed DTC
descriptor. `0x00097EB4` starts both status-byte accumulators at zero, ORs
byte 1 and byte 2 from these six exact JK08A runtime records, and writes those
status bytes to `0xFFFF5A94..0xFFFF5A95` through a three-byte block copy. The
fuel path does not consume byte 0 at `0xFFFF5A93`:

| Runtime index | Descriptor | DTC | Factory-manual title |
|---:|---:|---|---|
| `0xBA` | `0x00019C18` | P0101 | MAF SEN/CIRCUIT-B1 |
| `0xBB` | `0x00019C24` | P0102 | MAF SEN/CIRCUIT-B1 |
| `0xBC` | `0x00019C30` | P0103 | MAF SEN/CIRCUIT-B1 |
| `0x07` | `0x000193B4` | P010B | MAF SEN/CIRCUIT-B2 |
| `0x08` | `0x000193C0` | P010C | MAF SEN/CIRCUIT-B2 |
| `0x09` | `0x000193CC` | P010D | MAF SEN/CIRCUIT-B2 |

The exact descriptors establish the six DTC identities. The homologous VQ35HR
factory manual supplies the bank-specific titles. Initializer `0x0007EBEC`
clears record `0x129` within its `0x157`-record pass; periodic diagnostic
dispatcher `0x0007BFC4` later invokes the group-summary builder. A complete
2,315-function p-code pass found the exact consumer and block-copy boundary and
found no unresolved address candidate. The initialization loop and summary
builder are the only recovered write paths for this extension record.

`0x0003C3AC` calls `diagnostic_record_byte1_bit7_predicate(0x129)` and writes
the ORed MAF-fault result to current state `0xFFFF2449.bit7`; the periodic
snapshot copier moves it to `0xFFFF2448.bit7`. `0x0004F736` returns true when
that snapshot bit is set and `0xFFFF11B2 >= 0xC0`, or 2400 RPM in the
code-proven RPM/12.5 domain. Any of the six MAF records can therefore request
the full global fuel-inhibit mask at or above 2400 RPM.

### Transition-window, low-speed RPM branch

`0x0004F9C4` maintains counter `0xFFFF1690` from the current/previous
`0xFFFF244F.bit2` and `0xFFFF2453.bit2` snapshots. A current set bit loads 255,
a previous-only set bit loads zero, and the otherwise-active path increments
the counter with saturation.

The active state is `0xFFFF2497.bit7`. Entry requires all of the following:

```text
0xFFFF245D.bit6 == 0
0xFFFF41D4.bit0 == 0
RPM/25 >= 108                         # 2700 RPM
raw coolant >= 0x55
coarse vehicle speed <= 4
transition count < 60
```

The state clears below 2200 RPM or at transition count `>=150`. The
`ROM8[0x8B3F].bit7` master gate is clear in stock and therefore enables this
path. Its transition and thermal conditions are exact; the physical identity
of the snapshot bit remains unresolved.

### Sustained low-speed RPM exposure branch

`0x0004F7E0` updates word accumulator `0xFFFF1932`; its return value is not
used by the global OR. The stock cap is:

```text
ROM8[0x84DE] * ROM16[0x90E0] = 12 * 2000 = 24000
```

Under its status gates, each eligible invocation at coarse speed `<=4` and
RPM between 2300 and 2900 adds 12 up to the cap. The principal decay path
subtracts one outside that window; several inhibit paths clear the word.
Reaching the cap therefore requires 2000 qualifying periodic invocations.

`0x0004F958` sets `0xFFFF247C.bit7` after the accumulator reaches 24000 and
RPM is at least 1800. Once set, it remains active while the accumulator stays
at the cap and RPM remains at least 1500. The function returns that state as a
global contributor.

### Composite status/RPM branch

`0x000507CE` ORs three independently proven subpaths:

1. Direct seed `0xFFFF41EA.bit7`, which is lifecycle-zero in the stock
   application.
2. `0xFFFF245D.bit6`, `0xFFFF2458.bit5`, and RPM state
   `0xFFFF2489.bit0`, which sets at 1800 RPM and retains through 1600 RPM.
3. Either `0xFFFF24CE.bit2` or `0xFFFF24D2.bit0`, plus high-RPM state
   `0xFFFF249F.bit2`. Stock map `0x12A32` contains `0xFF` in every cell, so
   the activation boundary is 510 RPM/12.5 counts, or 6375 RPM; stock
   hysteresis `ROM16[0x9462]=16` gives a 200 RPM retention band.

Two calls to the diagnostic record-state helper use sentinel index `-1` and
always return zero. The enclosed `0xFFFF1038` comparison branch is therefore
unreachable in this executable.

Primary startup initializer `0x00027AC0` clears `0xFFFF41EA` inside effective
span `[0xFFFF261C,0xFFFF4514)`. Conditional clear service `0x0002FC24` and
recovery loop `0x00034B70` clear it again inside
`[0xFFFF1000,0xFFFF5CF4)`. A whole-program p-code pass covers all 2,315
functions without a decompilation failure or unresolved address candidate for
the byte. Its only runtime writers are `0x0007C166`, `0x00050920`, and
`0x0007F870`; their masks and whole-byte writes preserve bit 7. Recovered DMAC
destinations are limited to `0xFFFF86CC..0xFFFF87CB`. The direct seed therefore
remains zero and cannot activate this contributor in the proven stock
application lifecycle. The other two subpaths remain conditional and live.

### Critical ECM/ETC diagnostic RPM branch

`0x0007C166` recomputes `0xFFFF41EA.bit5` as the OR of ten exact diagnostic
record predicates:

| Runtime index | Descriptor | DTC | Attribute |
|---:|---:|---|---:|
| `0x4E` | `0x00019708` | P0605 | `0x2241` |
| `0x51` | `0x0001972C` | P0605 | `0x2241` |
| `0x6F` | `0x00019894` | P2119 | `0x2242` |
| `0x121` | `0x0001A0EC` | P1238 | `0x2242` |
| `0x70` | `0x000198A0` | P2119 | `0x2242` |
| `0x122` | `0x0001A0F8` | P1238 | `0x2242` |
| `0x72` | `0x000198B8` | P0603 | `0x00A0` |
| `0x73` | `0x000198C4` | P0605 | `0x2260` |
| `0x77` | `0x000198F4` | P0605 | `0x2261` |
| `0x79` | `0x0001990C` | P0605 | `0x0081` |

Predicate `0x0007C3B4` requires record byte 1 bit 7 and additionally requires
either byte 1 bit 5 or descriptor-attribute bit `0x2000`. The exact JK08A
descriptors identify P0603/P0605 ECM faults and P2119/P1238 ETC actuator faults;
the homologous factory manual names them ECM BACK UP/CIRCUIT, ECM, ETC ACTR-B1,
and ETC ACTR-B2 respectively.

`0x000804CE` produces the three qualification latches consumed by
`0x0007D856`:

```text
0xFFFF422E.bit7 sets once RPM/12.5 >= 0x20             # 400 RPM
0xFFFF422F.bit4 sets once raw coolant - selected raw temperature >= 20
0xFFFF422F.bit5 sets once raw coolant >= 0x78          # 70 deg C under raw-50
```

The first latch proves that engine-running speed has been reached. The third is
a coolant warm-up latch. The second compares exact raw coolant snapshot
`0xFFFF1071` with selected-temperature snapshot `0xFFFF106E`; the selected
value equals coolant while computed START SIGNAL is set and battery-voltage raw
is below 100. When that condition ends, selector `0x0003967A` returns coolant
once, sets its transition latch, and then publishes the stock-lifecycle zero
sentinel. At 0.08 V per count of DID `0x1103`, raw 100 is 8.00 V.
Consequently bit 4 is a post-start or low-voltage-transition qualifier rather
than a comparison with a second physical temperature. The zero sentinel has no
coolant scale and must not be rendered as `-50 deg C`. These bits latch until
diagnostic reset service `0x00080B54` clears them. The complete source and DID
chain is specified in `JK08A.start-signal-temperature-selector.md`.

`0x0007D856` resets `0xFFFF4B0E` only when the critical diagnostic aggregate
bit is clear. While that bit is set, it increments the counter with saturation
only when all three qualification latches are set; if any latch is clear, the
counter holds its previous value. `0x00050920` requires the counter to exceed
stock threshold four and the aggregate bit to remain set. Its RPM/25 state in
`0xFFFF41EA.bit6` activates at 2525 RPM, clears at or below 2000 RPM, and
retains its previous value from 2025 through 2500 RPM.

A complete p-code pass over all 2,315 functions found no unresolved address
candidate for `0xFFFF41EA`, `0xFFFF422E`, or `0xFFFF422F`. Only
`0x0007C166` changes `0xFFFF41EA.bit5`, and every runtime writer of that byte
preserves bit 7. The other runtime writers of the qualification bytes preserve
bits 7, 4, and 5 respectively.

### Shared status bit branch

`0x0004FAA0` directly returns `0xFFFF418C.bit1`. Primary startup initializer
`0x00027AC0` clears the byte inside effective span
`[0xFFFF261C,0xFFFF4514)`. Conditional clear service `0x0002FC24` and recovery
loop `0x00034B70` clear it again inside `[0xFFFF1000,0xFFFF5CF4)`.

The whole-program p-code census covers all 2,315 functions without a
decompilation failure. It finds no exact or computed-address store to
`0xFFFF418C`. The sole unresolved indexed store anchored at `0xFFFF4184` has
only offsets `0x54` and `0x65`, resolving to `0xFFFF41D8` and `0xFFFF41E9`.
The recovered DMAC destinations are limited to
`0xFFFF86CC..0xFFFF87CB`. Consequently bit 1 remains zero and this contributor
returns false throughout the proven stock application lifecycle. No physical
name is assigned to the inactive bit.

### Status-gated engine-running branch

`0x0004FAAC` enables its local state only while all three conditions hold:

```text
0xFFFF2499.bit1 == 1
0xFFFF2494.bit4 == 1
0xFFFF244F.bit2 == 0
```

It captures `min(7, uint8[0xFFFF273C])` as a selector, but both eight-byte
threshold halves at `0x126F4` contain only zero in stock JK08A. The returned
state `0xFFFF2494.bit3` therefore sets and remains set whenever the enable
conditions hold and engine speed is nonzero; it clears at zero RPM or when an
enable condition fails.

`0x0003ECE8` is the exact producer of `0xFFFF2499.bit1`. Direct writers of
`0xFFFF2494` modify bits 0, 1, 2, 3, 6, and 7 while preserving bit 4. The
whole-program computed-address census finds no additional writer capable of
reaching the byte. Startup initializer `0x00027C50` clears it inside
`[0xFFFF1000,0xFFFF261C)`, and `0x0002FC24` plus `0x00034B70` clear it again
inside `[0xFFFF1000,0xFFFF5CF4)`. The recovered DMAC destinations do not
overlap either span. Bit 4 therefore remains zero in the proven stock
application lifecycle, the enable conjunction fails, bits 2 and 3 clear, and
the contributor returns false.

### CAN-derived requested RPM ceiling

The internal CAN dispatch key `0x2EE0` calls `0x000C4ACE`, which copies one
payload field to `0xFFFF2818`. The periodic snapshot block copies that byte to
`0xFFFF2714`. The corresponding invalid-frame handler `0x000C5D2E` writes
`0xFE`, producing an effectively neutral 12700 RPM ceiling rather than the
`0xFF` invalid sentinel used by the consumer. The internal key is not asserted
to be an untransformed physical CAN identifier.

`0x00050A60` disables the dynamic ceiling when the snapshot is zero or `0xFF`,
or when either associated status-fault bit is set. Otherwise it uses:

```text
threshold = max(ROM8[0x89FD], uint8[0xFFFF2714])
ROM8[0x89FD] = 36                    # 1800 RPM floor
activate when RPM/50 > threshold
release when RPM/50 <= threshold - ROM8[0x89FC]
ROM8[0x89FC] = 6                     # 300 RPM hysteresis
```

The code proves a requested RPM ceiling carried by the decoded field. The
originating module and physical request semantics remain unverified.

### P0011/P0021 intake-valve-timing fault branch

`0x00050B3C` first requires at least 400 RPM, `0xFFFF4184.bit6` clear, and no
active record-state predicate for exact descriptor indices `0x52`, `0x55`,
and `0x11E`. Those indices contain U1001, U1000, and U1010 respectively. Three
additional sentinel `-1` predicates are inert.

The qualified path sets `0xFFFF2486.bit5`. With this bit and
`0xFFFF245C.bit1` set, `0xFFFF84C3.bit6` increments confirmation counter
`0xFFFF1946`; a clear hardware bit freezes the counter, while loss of the
software qualification resets it. At count `>=10`, byte-1 bit 5 in either
runtime record 208 or 209 sets `0xFFFF2486.bit6`. Exact JK08A descriptors at
`0x19D20` and `0x19D2C` identify those records as P0011 and P0021.

The final RPM state sets at 3000 RPM and retains through 2800 RPM. The function
returns true only while the P0011/P0021 fault state is active, current
`0xFFFF2458.bit5` is clear, and the RPM state is set.

## Power Balance replacement

`0x00030C4C` handles Nissan service 0x30 Output Control. Its IOLID `0x0C`
entry maps to active flag `0xFFFF99C5.bit3` and value byte `0xFFFF992F`.
Startup `0x0002E76E` clears both the active-bit array and the value array.

`0x00050A06` copies `0xFFFF992F` to per-pass cache `0xFFFF2B2C` and sets
`0xFFFF41FB.bit6` while the IOLID is active. `0x00050A34` returns that cached
byte instead of the aggregate input. When the IOLID is inactive, it returns
the aggregate input unchanged.

The VQ35HR factory ESM defines CONSULT-III `POWER BALANCE` as cutting each
injector signal one at a time. A structured Nissan-family diagnostic profile
defines IOLID `0x0C` bits 1, 2, 4, 8, 16, and 32 as cylinders 1 through 6.
This establishes the diagnostic function of the replacement. The electrical
JK08A channel-to-cylinder order remains a hardware-validation boundary.

## ETC-actuator-fault auxiliary mask

`diagnostic_record_byte1_bit7_predicate` at `0x00025E20` tests byte-1 bit 7 of
`0xFFFF5718 + 3*index`. `0x0005096C` invokes it for two exact indices:

| Index | JK08A descriptor | DTC |
|---:|---:|---|
| `0x71` (113) | `0x198AC` | P2119 `ETC ACTR-B1` |
| `0x123` (291) | `0x1A104` | P1238 `ETC ACTR-B2` |

If neither record bit is set, the auxiliary result is zero. If either is set,
`0x000509A0` returns this RPM/25-shaped mask:

| RPM/25 | RPM | Mask |
|---:|---:|---:|
| `<43` | `<1075` | `0x00` |
| `43` | 1075 | `0x01` |
| `44` | 1100 | `0x05` |
| `45` | 1125 | `0x07` |
| `46` | 1150 | `0x0F` |
| `47` | 1175 | `0x1F` |
| `>=48` | `>=1200` | `0x3F` |

`0x000509EA` additionally returns `0x3F` when coarse vehicle-speed count is
`<=2` and `0xFFFF10E4.bit2` is set. The two masks are ORed. Because this result
is merged after Power Balance replacement, the diagnostic test cannot clear an
active ETC-actuator-fault mask.

## Static and hardware boundaries

The exact executable establishes all 15 contributors, both side-effect-only
calls, their stock constants and state transitions, replacement precedence,
and the final six-bit mask. Remaining boundaries are:

- originating module and bus-level identity of internal CAN key `0x2EE0`;
- target channel-to-cylinder order and electrical injector behavior.

Execution outside the analyzed application or an external debug bus master
could alter internal RAM, but no such configuration path is present in the
recovered stock lifecycle. The remaining boundaries do not change the
code-proven arbitration or stock liveness classification above.
