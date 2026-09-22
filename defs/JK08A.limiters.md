# JK08A Rev-Limiter Arbitration

## Status and scope

This document records the static code model for the three adjacent rotational-speed
limiters in the exact JK08A/JK03A executable:

- main engine-speed fuel cut at `0x0934E`;
- the stationary fuel-cut state machine in `FUN_0004F324`;
- the request-limiter branch rooted at scalar `0x0942C`.

The model establishes periodic execution order, state transitions, mask precedence,
and downstream software effects. A controlled vehicle comparison of three
`0x0942C` values on 2026-09-21, recorded in
[`../patches/hardware-results.toml`](../patches/hardware-results.toml), fixes the
`x*0.78125 RPM` conversion of `0x0942C` and the throttle-plate action behind the
`Throttle Rev Limiter` name. The same session ran the main fuel cut from a map
slot copy and fixes the `x*12.5 RPM` conversion of `0x0934E`.

## Periodic execution order

`FUN_00020DFE` dispatches the 124-entry table at `0x2196C` in ascending index order.
The limiter-related entries are:

| Index | Function | Established role |
|---:|---|---|
| 12 | `FUN_000769C0` | request-limit source coordinator; reaches `FUN_0007584E` through `FUN_00075E9E` |
| 19 | `FUN_00071508` | signed minimum arbiter, including `0x0942C` result `0xFFFF19D8` |
| 21 | `FUN_000702A0` | ordered request-controller stages ending in `FUN_00070D82` |
| 22 | `FUN_00079DD8` | request-boundary dispatch ending in `FUN_00079030` |
| 23 | `FUN_000730FC` | downstream inverse-coordinate and limit calculations through `FUN_00073432` |
| 28 | `FUN_0004ED88` | final six-channel fuel inhibit/override mask `0xFFFF22E0` |
| 36 | `FUN_00057608` | fuel-multiplier coordinator, ending in `FUN_000556EC` |
| 43 | `FUN_0004E974` | common and bank-specific injection precursors |
| 61 | `FUN_0004ECAC` | parity bases and six compensated pulse channels |

The request limiter is therefore calculated before the main/stationary fuel-cut
states in the same periodic pass. The two mechanisms do not feed the same arbiter:
the request limiter enters a signed-min controller path, while the fuel limiters enter
the six-channel inhibit mask.

## Main engine-speed fuel cut

`FUN_0004F282` reads the first four words of `0x0934E` as two activation/release
pairs. Stock `ROM8[0x8B38]=0x63` has bit 7 clear, so the alternate pair at
`0x09356/0x09358` is outside the active path. `0xFFFF2468.bit4` selects the active
column.

| State transition | Column 0 | Column 1 |
|---|---:|---:|
| activate when RPM/12.5 is `>=` | 612 = 7650 RPM | 596 = 7450 RPM |
| release when RPM/12.5 is `<` | 596 = 7450 RPM | 368 = 4600 RPM |

With `0xFFFF2497.bit2` clear, reaching the activation threshold sets arming bit 1
and loads `0xFFFF24F1` from `ROM8[0x8C69]`. The stock delay is zero, so active bit 2
is set in the same invocation. While active, speed equal to the release threshold
retains the cut; only a value below it clears bits 1 and 2.

The returned Boolean is one of the global inputs of `FUN_0004ED88`. An active state
therefore becomes `0x3F`, not a rotating or partial mask.

The 2026-09-21 vehicle session ran column 0 from the Map 3 slot copy at
`0xD3508`, whose words are 612/596/604/368; only the column-0 release word
differs from stock. `FUN_00020DFE` copies `0xFFFF11F4` into the compared word
`0xFFFF11BC` between two telemetry captures of `0xFFFF11F4`, so each mask
transition bounds the threshold by the two captured RPM words around it. Eight
activations and eight releases of the full `0x3F` mask bound the activation word
to 612 = 7650 RPM and the release word to 604..606 = 7550..7575 RPM. Stock release
word 596 cannot produce any of the eight releases, whose lower captured word is
599..603. Column 1 remained unexercised.

## Stationary fuel-cut state machine

`FUN_0004F324` is enabled only while all three entry gates hold:

```text
uint8[0xFFFF110E] == 0
0xFFFF244F.bit2 == 1
0xFFFF2458.bit5 == 0
```

The first condition is the previous-periodic-pass coarse vehicle-speed snapshot. The
exact CAN/filter chain makes zero an unambiguous stationary value. If any gate fails,
the function clears accumulator `0xFFFF16A6`, timer/readiness/cut bits 3..5 of
`0xFFFF247F`, and its stationary-cut result.

The enabled state has a delayed readiness stage:

1. On first entry, bit 3 is set and timer `0xFFFF258A` is loaded with 100.
2. `FUN_0002040C` decrements this byte as part of `0xFFFF256A..0xFFFF25F3` on every
   tenth base interrupt.
3. At zero, the function calculates
   `q=clamp((signed16(0xFFFF11BC)-160)/2,0,255)`, looks up `0x124D2`, adds
   `lookup-128` to `0xFFFF16A6` with unsigned saturation, and reloads 100.
4. Readiness bit 4 is set at accumulator `>= ROM16[0x911C]`, whose stock value is
   381. The secondary stock temperature threshold `ROM8[0x8D0E]=0` cannot block
   an unsigned coolant byte.

At or below 2000 RPM the first table cell produces step zero, so readiness cannot
build from a cleared state. At the stock high-RPM limiter region the interpolated
cell is 255 and the step is 127. Exactly three timer expirations reach
`3*127=381`, or 300 countdown counts after initial entry. The countdown period is
the same exact `204800/Pphi` used by the surrounding byte-timer range. Passive
target-CAN timing establishes `Pphi=20 MHz`, so high-RPM readiness takes about
3.072 seconds.

After readiness, `0xFFFF11AE` uses exact `x*50 RPM` thresholds:

```text
ROM8[0x85D9] = 36: set cut bit 5 at RPM >= 1800
ROM8[0x85DA] = 30: retain cut at RPM >= 1500, clear below 1500
```

The returned bit 5 enters the same global Boolean group as the main RPM fuel cut and
therefore also becomes a full `0x3F` mask.

## Rotational-speed request limiter

`FUN_0007584E` reads calibrated words from `0x09424..0x0943E`; the base
threshold is `ROM16[0x0942C]=0x2580`. A value of `0xFFFF` writes neutral signed
limit `0x7FFF` to `0xFFFF19D8` and returns without advancing any limiter state.

On the enabled path, speed coordinate `N=uint16[0xFFFF11B6]` is filtered as:

```text
first pass: S_new = min(65535, 4*N), S_blend = S_new
later pass: S_blend = S_entry
            S_new = min(65535, N + floor(3*S_entry/4))
```

For stable speed the state converges to `4*N`. The blend uses the entry value,
while both request-rate terms use the newly stored value. This one-sample split
increases reduction during a rising-speed transient.

Dynamic threshold `0xFFFF1796` is initialized from `0x0942C`. The coolant latch
sets only at raw 255, remains set at raw 239, and clears at raw 238. Its stock
alternate threshold at `0x9434` is `0xFFFF`. Stock decrement and increment rates
at `0x9430` and `0x9436` are zero, so the normal threshold remains `0x2580`.

At steady speed, the effective delta is:

```text
L = clamp_u16(S + floor(76 * (D - S) / 1024))
delta = L - S
```

The signed `delta` changes state `0xFFFF19DA` with rate 1500 while the fast-mode
byte is nonzero and its nonpositive-ramp latch remains clear, or with rate 200
otherwise. An independent rate-2000 term is applied to the final request on
every active or inactive pass. `0xFFFF19DC` provides a second recovery envelope;
when this envelope wins, the ramp is rolled back to its entry value. Equality
between previous limiter output and APP request takes the inactive/reset branch.
The fast-mode byte `0xFFFF25B0` is initialized and reloaded with 100 and has no
other writer; it is not a countdown. Its paired latch alone selects the normal
rate after a nonpositive-ramp transition.

CAN `0x174` payload byte 3 supplies zero-based target gear in its high nibble
and current gear in its low nibble. CAN `0x177` payload byte 2 bits 0 through 2
supply the zero-based TCM gear-phase index. The limiter admits immediate
recovery tracking and its auxiliary output only for `target > current`, and
selects the 30-count recovery rate for `target > phase`, otherwise 50. Passive
target transitions prove target-first field ordering for both shift directions.

The optional forced-neutral override is not a stock upshift gate. Selected
producer `FUN_00077892` sets it for any target/current mismatch only when
`0xFFFF418F.bit4` is set and its independent inhibit aggregate is clear.
Bit 4 is the scheduler latch of `0xFFFF419B.bit4`, which `FUN_0007724C` sets
when TCM field `0xFFFF3A2E` (CAN `0x174` byte 4 bits 5 through 7) equals 3;
the 2026-09-22 road captures carry that value in 4-3 and 3-2 downshifts
([`JK08A.can.md`](JK08A.can.md#transmission-request-interface)).

The full state machine, calibration inventory, exact integer boundaries, and
auxiliary outputs are specified in
[`JK08A.throttle-control.md`](JK08A.throttle-control.md).

`FUN_00077892` also uses `0x0942C` as the upper cap in a gear-indexed
transmission-request calculation. The resulting signed word `0xFFFF4162` can
reach `FUN_00079030` only while `0xFFFF41A6.bit3` is set. The selected function
sets that bit from the forced-neutral state or from retained byte
`0xFFFF4413`, which it loads only on the same branch and `FUN_0002040C`
decrements, so the bit covers a gear change with TCM status 3 and the 307.2 ms
hold after it. The 2026-09-22 road captures show such episodes in 4-3 and 3-2
downshifts, where the secondary result bounds the shared request. A
calibration-only A/B change to `0x0942C` is isolated from this secondary path
only outside those episodes and only while external diagnostics or another
patch do not mutate those state bytes.

The exact downstream chain is:

```text
0x0942C
  -> FUN_0007584E -> 0xFFFF19D8
  -> FUN_00071508 -> 0xFFFF243A
  -> FUN_000702A0 / FUN_00070D82 -> 0xFFFF2438 and 0xFFFF19C2
  -> FUN_00079030 -> 0xFFFF19C6
  -> FUN_00073432 -> 0xFFFF198A
  -> FUN_000730FC -> 0xFFFF183E
  -> FUN_00072C3C -> 0xFFFF19B2
  -> FUN_0006F48C -> 0xFFFF28BC / 0xFFFF28BE
  -> FUN_000CC720 regulator
  -> FUN_000407C0 -> ATU-II BFR6A-D
```

`FUN_00071508` is a signed-min arbiter, so the most restrictive signed candidate
wins. `FUN_00070D82` either selects `0xFFFF243A` directly or selects controller
result `0xFFFF19C0`; in its enabled mixed mode it again takes the signed minimum.
`FUN_00079030` applies additional signed bounds before publishing the shared request
coordinate.

The `x*0.78125 RPM` conversion maps `0x2580` to 7500 RPM, placing the request
intervention 150 RPM below the column-0 fuel-cut activation and 50 RPM above its
release point. Exact stock-ROM execution across 7200..7800 RPM and four APP
requests confirms neutral arbitration through 7500 and progressive request
reduction above it. After 20 measured 10.24 ms passes, APP request 10000 produces
limiter requests 10000, 7601, 5466, and 3086 at 7500, 7600, 7700, and 7800.

The 2026-09-21 vehicle comparison selected three map slots whose copies of the
scalar hold `0x1900`, `0x2580`, and `0xFFFF` and read both primary throttle
sensor words `0xFFFF2756/285C`:

| Scalar | Conversion | Onset | Throttle sensor counts | Held speed |
|---|---:|---|---|---|
| `0x1900` | 5000 RPM | 5000 RPM, APP rising 2.17..3.06 V | 369/371 -> 166/171 | 4915..5137 RPM |
| `0x2580` | 7500 RPM | 7466..7488 RPM, APP held at 4.70 V | 838 -> 209/214 | 7412..7565 RPM for 1.44 s |
| `0xFFFF` | disabled | none | 835..837 at full pedal | main fuel cut at 7650 RPM, mask `0x3F` |

No limiter interval sets `0xFFFF22E0`. The measurement carries the request to
the throttle plates of both banks. Plate response time and channel-to-bank
identity remain outside it.

## Exact fuel-mask precedence

Let `B` be the OR of the 15 global Boolean results evaluated by
`fuel_output_inhibit_coordinator`. It includes the main and stationary
engine-speed cuts plus 13 other conditions. Two additional calls update state
but have their return values discarded. The complete contributor inventory is
maintained in [`JK08A.fuel-inhibit.md`](JK08A.fuel-inhibit.md). The exact mask
calculation is:

```text
G = 0x3F if B != 0 else 0x00
D = mask returned by DFCO state machine FUN_000503E0
C = count-derived mask returned by FUN_0005079C
P = G | D | C
R = uint8[0xFFFF2B2C] if Power Balance is active else P
A = ETC-actuator-fault mask returned by FUN_0005096C
0xFFFF22E0 = (R | A) & 0x3F
```

This gives the following precedence rules:

1. Main RPM fuel cut and stationary fuel cut have no priority over each other. Either
   active Boolean makes `G=0x3F`; simultaneous activation produces the same result.
2. A global `0x3F` absorbs every partial DFCO or count-derived bit through OR.
3. `power_balance_mask_apply` applies the diagnostic replacement after that OR.
   When service 0x30 IOLID `0x0C` is active, the replacement can substitute or
   clear any main/stationary/DFCO/count bits in `P`.
4. `etc_actuator_fault_inhibit_mask` is ORed after the replacement, so P2119/P1238
   auxiliary bits cannot be cleared by Power Balance.
5. `FUN_00050A4C` removes bits 6 and 7 from the final result.

The stationary entry gate requires `0xFFFF2458.bit5=0`, while a new or held DFCO cut
request in `FUN_0004FBE2` requires that bit to be 1. New requests are therefore
mutually exclusive on one snapshot. A persisted DFCO exit state or rotating release
tail can overlap after the bit changes; an active stationary `0x3F` then absorbs its
partial mask.

The `0x0942C` request limiter never enters this formula. It cannot clear, replace, or
delay the main fuel cut. If request reduction does not hold speed below the selected
`0x0934E` activation threshold, `FUN_0004F282` independently asserts the full fuel
mask later in the same periodic pass.

## Downstream effects and validation boundary

Index 27 publishes `0xFFFF22E0` before the current-pass fuel multiplier, injection
precursor, and six-channel compensated-word stages. A full `0x3F` mask causes
`FUN_000556EC` to publish zero in `0xFFFF22E6`; per-channel consumers also select
override/fallback paths through `FUN_0004EBA2`, `FUN_00052034`, and
`FUN_0002C13C`.

Static code therefore establishes a hard six-channel fuel-output path for main and
stationary RPM cut, and a separate softer signed-request path for `0x0942C` that
reaches ATU-II BFR6A-D through the stock throttle regulator. The 2026-09-21
vehicle session confirms the `0x0942C` scale and throttle-plate closure and the
`0x0934E` scale in column 0. Hardware validation remains required for plate
response time, bank and polarity assignment, external injector-driver behavior,
and channel-to-cylinder order.
The two shared-status prerequisites are lifecycle-zero and stock-inert under the
recovered startup, runtime, recovery, and DMAC paths.
