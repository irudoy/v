# JK08A Deceleration Fuel Cut

## Status and scope

This document records the static code model of deceleration fuel cut (DFCO) in
the exact JK08A/JK03A executable. The request logic, four RPM threshold tables,
entry and exit delays, five-state machine, rotating release tail, final
six-channel arbitration, and ATU-II output path are established by executable
code. Physical signal names that are not connected to an exact diagnostic or
terminal source remain unnamed.

No road log or bench observation is used here. Timing in scheduler counts is
code-proven. Timing in milliseconds and the physical injector result remain
hardware-validation items.

## Execution cadence

Normal startup calls `FUN_0002718A` and `FUN_000274AC`. The former configures
ATU-II timer channel 3 with `TCR3 = 5`, and the latter writes `PSCR1 = 1`.
`FUN_0002040C` advances `GR3A` by `0x140`, or 320 timer counts, on each base
interrupt. The SH7059 hardware manual gives these divisors:

```text
PSCR1 = 1  -> first prescaler output = Pphi / 2
TCR3 = 5   -> timer input = prescaler output / 32
channel 3  -> Pphi / 64
```

The exact base-interrupt period is therefore:

```text
320 * 64 / Pphi = 20480 / Pphi seconds
```

`FUN_0002040C` raises scheduler bit 2 every tenth base interrupt. On the same
cadence it decrements each nonzero byte in `0xFFFF256A..0xFFFF25F3`, including
DFCO timers `0xFFFF2571..0xFFFF2573`. `FUN_00020DFE` is dispatched on that bit
and reaches the periodic table containing `FUN_0004ED88`. One DFCO timer count
therefore equals exactly:

```text
204800 / Pphi seconds
```

The local NissanECU hardware note identifies a 10 MHz crystal, while the
SH7059 manual defines `Pphi = EXTAL * 2`. If that board-level assumption applies
to the target ECU, one DFCO count is 10.24 ms. This physical conversion is a
candidate until the target peripheral clock is measured or independently
confirmed.

## Upstream mode snapshots

`FUN_0006EFBC` is the sole writer found for `0xFFFF2459.bit5`. Periodic
scheduler `FUN_00020DFE` shifts the snapshots in this order:

```text
producer 0xFFFF2459 -> current 0xFFFF2458 -> previous 0xFFFF245A
```

The bit is a code-proven upstream DFCO mode or eligibility input, but its
physical identity is unresolved. It is not named as pedal, throttle, or a
driver request.

The producer sets the bit when either of two Boolean groups is true. One group
requires `(0xFFFF2451.bit7 || 0xFFFF24CD.bit7)` and `FUN_0008C3FA()`. The other
selects between `0xFFFF417F.bit3` and `0xFFFF4230.bit7` according to
`0xFFFF4245.bit0`, `0xFFFF4249.bit4`, and timer `0xFFFF259C`.
`FUN_0008C3FA` itself requires `0xFFFF4184.bit6` clear and
`0xFFFF244F.bit5` set, with one additional low-count exception. These Boolean
relations are exact; their physical signal names are not.

## Cut request and threshold selection

`FUN_0004FBE2` always interpolates both coolant-indexed cut tables and compares
the selected threshold with `0xFFFF11B3`, the code-proven RPM/25 snapshot. The
comparison is strict: a request is returned only when current RPM is greater
than the selected threshold.

The stock selection is edge-sensitive:

| Current `2458.bit5` | Previous `245A.bit5` | Primary threshold | Meaning |
|---:|---:|---|---|
| 0 | any | none | request blocked |
| 1 | 0 | `0x12718` | rising-edge entry threshold; vehicle-speed snapshot must be at least 4 |
| 1 | 1 | `0x126E4` | held-request threshold, subject to additional runtime branches |

Both maps are live in stock JK08A. The A2L labels them as different ECU-family
sets, but those source labels do not describe this executable's dynamic
selection. `ROM8[0x8B3F].bit7` and `ROM8[0x870C].bit7` are both clear in the
stock image, which establishes the stock branch used above.

`0xFFFF4250.bit7` can add `ROM8[0x84E8] = 24` RPM/25 counts to both thresholds
with saturation. `0xFFFF4246.bit3` can lower-bound both with
`ROM8[0x85F3] = 0`. Held-request branches also inspect current
`0xFFFF2458.bit7`, `0xFFFF1083`, `0xFFFF24CF.bit4`, `0xFFFF2978`, and vehicle
speed. Their Boolean effects are retained in the code annotations without
assigning unproven physical names.

## Restore classifier

`FUN_00050018` always interpolates both restore tables:

| Address | Stored result | Role |
|---|---|---|
| `0x1298C` | `0xFFFF1778` | upper threshold for the intermediate restore class |
| `0x12818` | `0xFFFF16AA` | lower threshold for the full restore class |

Both results use RPM/25. A coolant-indexed floor is selected from raw/selected
coolant boundaries `[4, 8, 12, 32]` and floor values `[36, 48, 54, 62]`, or
`[900, 1200, 1350, 1550] RPM`. When `0xFFFF24CF.bit4` is clear, both thresholds
are also clamped to at least `ROM8[0x8A3F] = 48`, or 1200 RPM.

The return contract is:

| Return | State-machine meaning |
|---:|---|
| 0 | remain in or allow DFCO |
| 1 | master inhibit or upstream DFCO mode absent |
| 2 | intermediate restore class |
| 3 | full restore class |

At vehicle-speed snapshot below 4 counts, the stock classifier is explicit:

```text
RPM <= lower threshold                       -> 3
lower threshold < RPM <= upper threshold    -> 2
RPM > upper threshold                        -> 0
```

At speed 4 or above, the common stock branches return 3 at or below the
selected lower threshold and 0 above it. Additional branches use
`0xFFFF2458.bit7`, `0xFFFF24CF.bit4`, `0xFFFF1083`, `0xFFFF2978`, speed 10,
and fallback constants. The two restore tables are therefore operational, even
though the upper table is not used by every branch.

`0xFFFF2468.bit6` forces return 1. A clear current `0xFFFF2458.bit5` also
returns 1 and updates the associated status bit.

## Entry and exit delays

`FUN_0004FE9C` returns `stage1 << 8 | stage2`. The state machine loads the high
byte into `0xFFFF2571` and the low byte into `0xFFFF2572`.

With stock `ROM8[0x870C].bit7 = 0`, normal branches select:

| Condition | Stage 1 | Stage 2 | Candidate time at 10.24 ms/count |
|---|---:|---:|---:|
| `0xFFFF2468.bit7 = 0` | 60 | 0 | 614.4 ms |
| bit 7 set and raw coolant below `0x6E` | 40 | 0 | 409.6 ms |
| bit 7 set and raw coolant at least `0x6E` | 75 | 0 | 768.0 ms |

Raw coolant `0x6E` corresponds to a candidate 60 deg C under the diagnostic
`raw - 50` conversion. The nominal 3000 RPM split does not alter the stock
warm result because both selected constants are 75.

Map `0x120F6` is a code-proven conditional stage-1 DFCO entry-delay table. It
is reached only through the non-stock `ROM8[0x870C].bit7 = 1` branch with
`0xFFFF2468.bit7` set, warm coolant, and RPM below 3000. Its coordinate is
`clamp(max(vehicle_speed - 6, 0) * 8, 0, 255)`. All 16 stock cells are 60, so
the coordinate cannot change the result in the stock calibration.

`FUN_0005038A` selects the state-4 exit delay placed in `0xFFFF2573`. All
relevant stock bytes are zero, so the normal stock exit delay is zero.

## Five-state machine

`FUN_000503E0` stores its state in `0xFFFF14C1`. The state-to-mask table at
`0x2371C` is `[0x00, 0x00, 0x15, 0x3F, 0x15]`:

| State | Meaning | Base mask |
|---:|---|---:|
| 0 | idle | `0x00` |
| 1 | first entry delay | `0x00` |
| 2 | second entry delay | `0x15` |
| 3 | full six-channel cut | `0x3F` |
| 4 | exit delay | `0x15` |

The normal transition sequence is:

```text
idle 0 --cut request and restore=0--> 1 --timer 2571=0--> 2
2 --timer 2572=0--> 3
3 --restore request--> rotating release or 4
4 --timer 2573=0--> 0
```

The implementation tests successive states in one invocation. Stock stage-2
and exit delays are zero, so states 2 and 4 normally collapse immediately. The
observable stock base mask is therefore usually 0 while state 1 waits, then
`0x3F` in state 3, then 0 on normal release. Mask `0x15` becomes persistent
only with a nonzero corresponding delay or another branch condition.

`0xFFFF2468.bit6` resets the machine. A separate state-4 reset branch uses
current `0xFFFF2458.bit5` and the `ROM8[0x8A40] = 4` coolant boundary.

## Injector-event rotating release

One release branch leaves state 3 through a rotating per-channel tail instead
of state 4. It requires loss of current upstream mode and the calibrated/runtime
branch controlled by `ROM8[0x8711].bit1`, `ROM8[0x8B3F].bit7`, and
`0xFFFF24CF.bit4`. At RPM/25 above `ROM8[0x8C1E] = 30`, or 750 RPM, it exits
without a rotating tail.

For the stock `0x8B3F.bit7 = 0` branch, `0xFFFF1517` selects class 0 below 4,
class 1 at 4, and class 2 at or above 5. Tables at `0x1269D` and `0x1269A`
provide delays `[0, 5, 2]` and counts `[0, 2, 2]`. Candidate physical delays
are 0, 51.2, and 20.48 ms under the 10.24 ms/count assumption.

`FUN_00050766` rotates the current injector-event one-hot mask held in
`0xFFFF1936`. Injector-event handler `FUN_0002BE40` supplies that mask, clears
the current channel from history `0xFFFF1935`, and, while rotating count
`0xFFFF1937` is nonzero and aggregate mask `0xFFFF22E0` is nonzero, decrements
the count and adds the current channel to history. The release tail is therefore
synchronized to injector events rather than only to the periodic DFCO task.

`0xFFFF4250.bit7` or nonzero timer/state `0xFFFF259C` clears the rotating state.

## Final arbitration

`FUN_0004ED88` is the aggregate six-channel fuel-output inhibit/override
coordinator:

```text
global Boolean conditions -> FUN_0004FB5E -> 0x00 or 0x3F
DFCO request/class/delays  -> FUN_000503E0 -> DFCO mask
per-channel count          -> FUN_0005079C -> count mask
auxiliary RPM branch       -> FUN_0005096C -> auxiliary mask
runtime override           -> FUN_00050A06/FUN_00050A34
all selected masks         -> FUN_00050A4C -> value & 0x3F
                                              -> 0xFFFF22E0
```

The global Boolean group includes the main RPM limiter `FUN_0004F282`, the
stationary RPM limiter `FUN_0004F324`, and additional unresolved conditions.
`FUN_0005079C` maps a clamped count through masks
`[0x01, 0x05, 0x15, 0x17, 0x1F, 0x3F]`. `FUN_0005096C` creates an independent
RPM-shaped mask under its own status gates. `FUN_00050A06` can activate a
runtime replacement byte from `0xFFFF992F`. These contributors share the final
mask but are not evidence that their physical causes are DFCO.

## Output path

`0xFFFF22E0` is not a direct pulse-width value and does not by itself prove that
a displayed duration becomes zero. It changes the six-channel path in three
code-proven places:

1. `FUN_0004EBA2` selects override word `0xFFFF2436` for each masked channel
   instead of the normal calculated pulse path.
2. `FUN_00052034` clears or withholds the corresponding eligibility bit in
   `0xFFFF1220`; `FUN_00051A98` skips its normal duration path for such a bit.
3. Injector-event scheduler `FUN_0002C13C` substitutes fallback word
   `0xFFFF23AA` when the current channel is present in `0xFFFF22E0` or rotating
   history `0xFFFF1935`, scales the selected word by 800/256, adds it to
   ATU-II channel 8 counters `DCNT8A..DCNT8F`, and writes the start mask to
   `DSTR`.

The SH7059 manual identifies those registers as six ATU-II one-shot outputs.
This closes the static path from DFCO state to the injector-output scheduling
peripheral. Physical cylinder order, the exact electrical output behavior, and
the relationship between fallback/override words and a diagnostic injector-time
display require bench or engine validation.

## Calibration inventory

| Address | Shape | Code role | Scale | Stock characteristics |
|---|---|---|---|---|
| `0x120F6` | 1x16 u8 | conditional stage-1 entry delay | scheduler counts | all cells 60; stock selector branch disabled |
| `0x126E4` | 1x16 u8 | held-request RPM threshold | `x * 25 RPM` | live in stock |
| `0x12718` | 1x16 u8 | rising-edge entry RPM threshold | `x * 25 RPM` | live in stock |
| `0x12818` | 1x16 u8 | lower/full-restore RPM threshold | `x * 25 RPM` | live in stock |
| `0x1298C` | 1x16 u8 | upper/intermediate-restore RPM threshold | `x * 25 RPM` | live in stock |
| `0x1269A` | byte vector | rotating-release event counts | injector events | first classes `[0, 2, 2]` |
| `0x1269D` | byte vector | rotating-release delay | scheduler counts | first classes `[0, 5, 2]` |
| `0x2371C` | byte vector | state-to-six-channel mask | bit mask | `[0x00, 0x00, 0x15, 0x3F, 0x15]` |

The four RPM tables share the implicit coolant axis
`[-40, -30, ..., 110] deg C`. At 80 deg C their stock thresholds are 1800 RPM
hold, 1050 RPM entry, 900 RPM full restore, and 900 RPM intermediate restore.
At 110 deg C they are 1800, 1400, 1200, and 1200 RPM respectively. Runtime
floors, offsets, edge selection, speed gates, and timers remain part of the
effective behavior.

## Map-switching consequence

The current map-switching layout redirects only `0x12718` and `0x12818`.
Consequently it switches the rising-edge entry threshold and the lower/full
restore threshold, while held-request table `0x126E4` and upper/intermediate
restore table `0x1298C` remain in Map 1 storage. This is a partial DFCO
calibration switch, not a complete switch of DFCO behavior.

## Hardware validation boundary

The next validation phase should establish, without changing this static model:

- physical meaning and transition conditions of `0xFFFF2459.bit5`;
- target `Pphi` and the timer-count conversion;
- state, timer, threshold, and `0xFFFF22E0` transitions during real deceleration;
- physical injector closure and diagnostic injector-duration behavior;
- injector channel-to-cylinder order;
- behavior of the rotating release branch near 750 RPM.
