# JK08A bounded RPM-inhibit reader dependencies

`JK08A.rpm-inhibit-access-claims.toml` contains fourteen exact original reader claims
owned by `fuel_output_inhibit_coordinator/fn` at `0004ED88`:

| Existing owner | Address | Physical read sites | Retained semantic type |
|---|---|---|---|
| `rev_limit_fuel_cut/tbl` | `0000934E` | `0004F2CC` | width and signedness unset |
| `stirring-mayfly/ram` | `FFFF2494` | `0004F2A4` | width and signedness unset |
| `fuel_inhibit/ram` | `FFFF2497` | `0004F288`, `0004F30E`, `0004F316` | unsigned 8-bit |
| `xanthic-yak/ram` | `FFFF24A6` | `0004F1A2`, `0004F1D6`, `0004F27A` | unsigned 8-bit |
| `resourceful-scorpion/ram` | `FFFF2448` | `0004F738` | width and signedness unset |
| `obedient-stoat/ram` | `FFFF418C` | `0004FAA2` | width and signedness unset |
| `accomplished-chicken/ram` | `FFFF2489` | `00050844`, `00050858`, `0005085A`, `00050868` | width and signedness unset |
| `resolute-bullfinch/ram` | `FFFF249F` | `0005089C`, `000508BC`, `000508BE`, `000508CC` | width and signedness unset |
| `agate-kingfisher/ram` | `FFFF41EA` | `000507E2` | width and signedness unset |
| `gifted-jackrabbit/tbl` | `000085D9` | `0004F422` | width and signedness unset |
| `ochre-jacamar/ram` | `FFFF247C` | `0004F9AE`, `0004F9B2`, `0004F9B4` | width and signedness unset |
| `blue-oyster/ram` | `FFFF247F` | `0004F330`, `0004F3A6`, `0004F43C` | width and signedness unset |
| `jovial-buzzard/ram` | `FFFF249C` | `00050A66`, `00050AEC`, `00050AF0`, `00050AF8` | width 8, signedness unset |
| `heavenly-whippet/ram` | `FFFF41F2` | `0004F4C0`, `0004F52C`, `0004F554`, `0004F600`, `0004F646` | width and signedness unset |

The exact full original native documents and proposed documents are pinned in
the claims descriptor. Each proposal appends one reserved indirect evidence
item to its existing reader relation. All fourteen appends form one ordinary
`link` batch; no alternative writer or canonical mutation path is defined.
Every other relation, layout, symbol type, ledger, evidence position and TEST
origin remains exact. The physical word read at `0000934E` and byte read at
`FFFF2494`, `FFFF2448` and `FFFF418C` do not establish semantic width, signedness, table geometry,
units or scale. Other questions attached to the coordinator remain separate.


## Executed boundary

`JK08A.rpm-inhibit.toml` declares the bounded entry at `0004EDBE` and outside
observing return at `0004EDC6`. The tested caller consists of eight stock bytes:
the BSR to `0004F19C`, its `MOV R0,R14` delay slot at `0004EDC0`, the BSR to
`0004F282`, and its `OR R0,R14` delay slot at `0004EDC4`. The independent caller
assembly binds those bytes to the unchanged existing vehicle-speed and main
RPM state-machine assembly. Executed leaf spans are
`0004F19C..0004F1D8`, `0004F240..0004F282` and `0004F282..0004F324`.

The incoming GBR is explicitly `01009F34`. R0 contains an explicit full
32-bit prior accumulator; other registers, SR, MACH, MACL, frame and caller
ABI are independently seeded and checked. The observed output pair is final
R0 from the main state machine and final R14 equal to the prior accumulator
OR the vehicle-speed Boolean. The actual post-delay state at both calls is
required. Natural leaf returns at `0004F27E` and `0004F320` target `0004EDC2`
and `0004EDC6`, respectively.

Two further bounded entries use the same component. Entry `0004EDD2` calls
the complete MAF-summary function `0004F736..0004F758`, with `OR R0,R14` at
`0004EDD4`. Entry `0004EDF8` calls the complete shared-status function
`0004FAA0..0004FAAC`, with `OR R2,R14` at `0004EDFA`. Their natural RTS sites
are `0004F754` and `0004FAA8`, returning to `0004EDD6` and `0004EDFC`.
Entry `0004EDEA` loads the real function pointer from `0004EF8C`, calls the
composite-status function at `0004EDEC`, and executes `OR R2,R14` at
`0004EDEE`. Its root spans are `000507CE..0005082A` and
`00050836..000508E6`; the natural RTS at `000508E2` returns to `0004EDF0`.
The exact real helper closure contains `000259E4..00025A12`,
`00026370..00026382`, `00026740..0002676E` and `00026A80..00026ABA`.
R0, R2 and R14 have explicit independent
full-word inputs. Final R0 is the leaf Boolean; final R14 is incoming R14 OR
incoming R0 for MAF summary, or incoming R14 OR incoming R2 for shared and composite status.
The leaf result is not retroactively merged into that delay-slot accumulator.

## Separate state and causal consumers

The raw input domain supplies 27 calibration bytes: configuration at `00008B38`,
main and vehicle delay reloads at `00008C69` and `00008CAF`, speed thresholds at
`00008DB7` and `00008DC3`, six words at `0000934E..0000935A`, the hysteresis word
at `00009462`, and eight curve bytes at `00012A32..00012A3A`.

The instruction-state engine and separate scalar equations must agree on all
RAM bytes and the output pair. The vehicle equations distinguish entry state,
control bit5, speed activation/release comparisons, control bit7, delay reload,
delay value and final state bit0. The main equations distinguish entry bit2,
arm bit1, on/off threshold pair selection, RPM comparison, delay reload and
delay value. The selected pairs use words 0/2, 1/3 and 4/5, respectively.
No external counter ticking or invocation cadence is assumed.

The third threshold pair requires an explicit controlled configuration bit7,
`FFFF2499.bit1`, `FFFF2494.bit5` and `FFFF244F.bit2`. The ordinary configuration
does not execute the `FFFF2494` read. The controlled path establishes that
reader dependency under its stated inputs; it grants no stock conditioned
branch reachability.

The separate MAF-summary equation returns one only when `FFFF2448.bit7` is
set and the unsigned byte at `FFFF11B2` is at least 192. Its exact physical
consumer distinguishes the conditional RPM read from the unconditional status
read. The shared-status equation returns `FFFF418C.bit1`, including its real
`MOVT` and RTS-delay `XOR` inversion. Both leaves preserve complete RAM. The
shared path uses an explicit controlled shared status; it establishes no
stock producer or lifecycle reachability for that bit.

The composite equation starts with the controlled `FFFF41EA.bit7` seed.
Its low latch sets `FFFF2489.bit0` when unsigned byte `FFFF11B3`, plus eight
when the incoming latch bit is set, reaches 72. The addition does not wrap
to eight bits. Its output requires `FFFF245D.bit6` and `FFFF2458.bit5`.
The curve coordinate is four times the unsigned `FFFF110E` byte capped at
63. The existing independent eight-byte curve equation supplies a byte;
twice that byte is stored as the word at `FFFF17CA`. The high latch sets
`FFFF249F.bit2` when unsigned word `FFFF11BC`, plus the unsigned hysteresis
word at `00009462` when the incoming latch bit is set, reaches that threshold.
The sum does not wrap to 16 bits. Its output requires `FFFF24CE.bit2` or
`FFFF24D2.bit0`. Final R0 is the OR of seed, low output and high output.
Only the two latch bytes and threshold word can change; all other RAM and
all unrelated latch bits remain exact. The seed is a controlled input;
this contract grants no stock seed lifecycle reachability.

Both actual calls to `000259E4` pass signed-short `-1`. The first argument
is set at `000507EE`; the second is set in the `000507FC` delay slot. The
real helper executes its sentinel branch and returns zero twice. Consequently
`000507F6` falls through and `00050800` is taken under these exact premises.
The diagnostic branch at `00050802..0005083E` does not execute; its conditional
sites and the helper's non-sentinel sites are excluded from feasible coverage.
No read of `FFFF1038` or `FFFF4200` is allowed. The byte-curve entry also
fixes the body branch at `00026A9A` to its byte route when that body executes.
These are four exact one-sided branch sites, bound to real instructions and
post-delay inputs. They establish no general absence or reachability claim.

An independent physical consumer requires every ordered non-frame access,
including PC-relative pools, ROM calibrations, RAM bytes and words, stores,
and both read/modify/write byte operations. It also requires exact natural
call entries, SP, PR, GBR, post-delay R0/R2/R14, leaf returns and terminal restored
state. The complete input domain binds 33 actual conditional branch sites;
both outcomes at each site are mandatory. Every listed owning read site must occur, including
the read halves of the state read/modify/write instructions.

Each of the nine owning inputs requires at least two original observations
with a changed caller output pair while every other complete RAM byte,
calibration, context, frame, SP, continuation, ABI and incoming SR is fixed.
The independent positive alternatives include threshold word 600/601 at RPM
600, main state 0/4, conditioned status 0/32, and vehicle state 0/1. A prior
accumulator of `80000000` with vehicle result 1 must retain R14=`80000001`.
MAF status 0/128 at RPM byte 192 and shared status 0/2 independently change
the leaf result with every other complete input fixed. Distinct incoming
R0=`80000000`, R2=1 and R14=`40000000` distinguish the two OR delay slots.
Low latch 0/1 at byte RPM 68, high latch 0/4 at word RPM 500 with hysteresis
16 and threshold 510, and seed 0/128 independently change the composite
result with every other complete input fixed. Explicit ascending, descending
and constant curves cover interpolation and last-cell returns. Full byte
state domains, unsigned boundaries, gate combinations, SR/MQT and incoming
word variants bind the actual root and helper paths.
Positive grouping holds the exact kind and entry as well as all other inputs.
