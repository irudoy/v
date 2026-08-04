# JK08A Rev-Limiter Arbitration

## Status and scope

This document records the static code model for the three adjacent rotational-speed
limiters in the exact JK08A/JK03A executable:

- main engine-speed fuel cut at `0x0934E`;
- the stationary fuel-cut state machine in `FUN_0004F324`;
- the request-limiter branch rooted at scalar `0x0942C`.

The model establishes periodic execution order, state transitions, mask precedence,
and downstream software effects. No road log or new hardware result is used. The
physical `Throttle Rev Limiter` name and `x*0.78125 RPM` conversion of `0x0942C`
remain catalog-supported candidates because the static trace stops at a shared signed
request coordinate rather than a throttle motor output.

## Periodic execution order

`FUN_00020DFE` dispatches the 124-entry table at `0x21970` in ascending index order.
The limiter-related entries are:

| Index | Function | Established role |
|---:|---|---|
| 11 | `FUN_000769C0` | request-limit source coordinator; reaches `FUN_0007584E` through `FUN_00075E9E` |
| 18 | `FUN_00071508` | signed minimum arbiter, including `0x0942C` result `0xFFFF19D8` |
| 20 | `FUN_000702A0` | ordered request-controller stages ending in `FUN_00070D82` |
| 21 | `FUN_00079DD8` | request-boundary dispatch ending in `FUN_00079030` |
| 22 | `FUN_000730FC` | downstream inverse-coordinate and limit calculations through `FUN_00073432` |
| 27 | `FUN_0004ED88` | final six-channel fuel inhibit/override mask `0xFFFF22E0` |
| 35 | `FUN_00057608` | fuel-multiplier coordinator, ending in `FUN_000556EC` |
| 42 | `FUN_0004E974` | common and bank-specific injection precursors |
| 60 | `FUN_0004ECAC` | parity bases and six compensated pulse channels |

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
the same exact `204800/Pphi` used by the surrounding byte-timer range. With the
board-level candidate `Pphi=20 MHz`, high-RPM readiness takes about 3.072 seconds.

After readiness, `0xFFFF11AE` uses exact `x*50 RPM` thresholds:

```text
ROM8[0x85D9] = 36: set cut bit 5 at RPM >= 1800
ROM8[0x85DA] = 30: retain cut at RPM >= 1500, clear below 1500
```

The returned bit 5 enters the same global Boolean group as the main RPM fuel cut and
therefore also becomes a full `0x3F` mask.

## Rotational-speed request limiter

`FUN_0007584E` reads the 28-byte calibration cluster at `0x09424`; the upper-speed
scalar is `ROM16[0x0942C]=0x2580`. A value of `0xFFFF` bypasses the branch and writes
neutral signed limit `0x7FFF` to `0xFFFF19D8`.

On the enabled path, speed coordinate `N=uint16[0xFFFF11B6]` is filtered as:

```text
first pass: S = min(65535, 4*N)
later pass: S = min(65535, N + floor(3*S_previous/4))
```

For stable speed the state converges to `4*N`. Dynamic threshold `0xFFFF1796` is
initialized from `0x0942C`. In stock calibration, decrement and increment steps at
`0x09430` and `0x09436` are zero and the alternative cap at `0x09434` is `0xFFFF`,
so the threshold remains `0x2580` in the normal path.

The exact downstream chain is:

```text
0x0942C
  -> FUN_0007584E -> 0xFFFF19D8
  -> FUN_00071508 -> 0xFFFF243A
  -> FUN_000702A0 / FUN_00070D82 -> 0xFFFF2438 and 0xFFFF19C2
  -> FUN_00079030 -> 0xFFFF19C6
  -> FUN_00073432 and FUN_00073628
```

`FUN_00071508` is a signed-min arbiter, so the most restrictive signed candidate
wins. `FUN_00070D82` either selects `0xFFFF243A` directly or selects controller
result `0xFFFF19C0`; in its enabled mixed mode it again takes the signed minimum.
`FUN_00079030` applies additional signed bounds before publishing the shared request
coordinate.

The HR catalog conversion maps `0x2580` to 7500 RPM, placing the candidate request
intervention 150 RPM below the column-0 fuel-cut activation and 50 RPM above its
release point. This numeric ordering supports staged request reduction before hard
fuel cut, but static code does not prove actual throttle-plate motion or response
time.

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
stationary RPM cut, and a separate softer signed-request path for `0x0942C`. Hardware
validation remains required for the physical throttle action, exact `0x0942C` scale,
external injector-driver behavior, and channel-to-cylinder order. The two shared-status
prerequisites are lifecycle-zero and stock-inert under the
recovered startup, runtime, recovery, and DMAC paths.
