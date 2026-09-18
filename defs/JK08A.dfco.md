# JK08A Deceleration Fuel Cut

## Status and scope

This document records the code model and bounded target-vehicle evidence for
deceleration fuel cut (DFCO) in the exact JK08A/JK03A executable. The request
logic, four RPM threshold tables, entry and exit delays, five-state machine,
rotating release tail, final six-channel arbitration, and ATU-II output path
are established by executable code. Physical signal names that are not
connected to an exact diagnostic or terminal source remain unnamed.

The upstream filtered engine-speed-drop path and calibration `0x1202E` are
specified separately in [JK08A.rpm-drop-state.md](JK08A.rpm-drop-state.md).

The enabled 1.11 vehicle capture validates the lower/full-restore table as the
operational entry veto under warm moving lift-off. Exact stock branch analysis
separates that moving role from the upper/intermediate table's low-speed role.
Timing in scheduler counts is code-proven, and passive target-CAN timestamps
establish the physical `10.24 ms` conversion. The physical injector result
remains a hardware-validation item.

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

Passive target-CAN timestamps show a `102.4 ms` median over ten scheduler
periods. Together with the exact timer formula, this establishes
`Pphi = 20 MHz` and one DFCO count of `10.24 ms` on the target ECU. The local
NissanECU hardware note and the SH7059 relation `Pphi = EXTAL * 2` independently
agree with that result.

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
| `0x1298C` | `0xFFFF1778` | low-speed upper threshold for the intermediate restore class |
| `0x12818` | `0xFFFF16AA` | lower threshold for the full restore class |

Both results use RPM/25. Scheduled positive RPM-drop byte `0xFFFF106A` is
classified by the first three breakpoints in ROM sequence
`0x11CB5 = [4, 8, 12, 32]`. Values `0..3`, `4..7`, `8..11`, and `12..255`
select floor values `0x1299C = [36, 48, 54, 62]`, or
`[900, 1200, 1350, 1550] RPM`. The fourth adjacent byte, 32, is not compared
by this four-class loop. When `0xFFFF24CF.bit4` is clear, both thresholds are
also clamped to at least `ROM8[0x8A3F] = 48`, or 1200 RPM.

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

At speed 4 or above, every reachable branch under the stock compile-time flags
`ROM8[0x8B3F].bit7 = 0` and `ROM8[0x870C].bit7 = 0` ignores the adjusted upper
threshold. These branches return class 3 when RPM is at or below the effective
lower threshold and class 0 only when RPM is strictly above it. Additional
runtime branches use `0xFFFF2458.bit7`, `0xFFFF24CF.bit4`, `0xFFFF1083`,
`0xFFFF2978`, speed 10, and fallback constants, but none compares RPM with
`0xFFFF1778` under the stock flags.

When `0xFFFF24CF.bit4` is clear, the effective lower threshold is at least
`ROM8[0x8A3F] = 48`, or 1200 RPM. The moving fallback constant
`ROM8[0x8A3A] = 42` is then dominated by that floor. Other runtime branches can
select additional constants, including 72 RPM/25 counts, without making the
upper map part of the moving comparison.

Consequently, `0x1298C` is live in the stock low-speed branch below 4 counts,
where it defines the class-2 band, but it has no effect on the stock moving
classifier at speed 4 or above. Interpolating and storing the map on every call
does not make it decision-relevant in those moving branches.

`0xFFFF2468.bit6` forces return 1. A clear current `0xFFFF2458.bit5` also
returns 1 and updates the associated status bit.

## Target-vehicle restore-family evidence

The exact image and 2026-08-17 moving capture are registered in
`../patches/hardware-results.toml`. The selected test calibration retained the
stock Hold and Entry request families while changing the Full Restore and
Intermediate Restore pair above the observed sub-5000-RPM region. The capture
filter required vehicle speed above 10 km/h, placing every selected sample in
the stock `0xFFFF110E >= 4` moving branch. Under warm moving lift-off, the
stock-family interval contained 957 full `0x3F` inhibit samples among 1,534
selected samples. The restore-only contrast contained zero full-inhibit samples
among 2,132 selected samples, and all six calculated injection words remained
nonzero.

This result matches the code-level entry condition:

```text
cut_request == 1 and restore_class == 0 -> entry may proceed
cut_request == 1 and restore_class != 0 -> entry is vetoed
```

Exact branch analysis makes `0x12818` the only changed restore table capable of
causing this moving result; `0x1298C` is not compared on the selected branch.
Hold and Entry therefore do not need to be moved above the operating range to
suppress DFCO there, and changing only `0x12818` is sufficient. Equality
belongs to full-restore class 3: a raw threshold of 200 vetoes DFCO through
exactly 5000 RPM in the RPM/25 coordinate, while class 0 begins only when the
quantized coordinate is strictly greater. The capture does not exercise that
above-boundary transition or prove physical injector closure.

## Per-slot map-switching projection

The complete five-slot JK08A runtime switches all four live DFCO threshold
families together with the selected map:

| Family | Map 1 | Maps 2 through 5 | Pointer table |
|---|---:|---:|---:|
| Hold | `0x126E4` | `0xD3F80..0xD3FBF` | `0xD24E0` |
| Entry | `0x12718` | `0xD2400..0xD243F` | `0xD3540` |
| Full Restore | `0x12818` | `0xD2440..0xD247F` | `0xD3554` |
| Intermediate Restore | `0x1298C` | `0xD3FC0..0xD3FFF` | `0xD3528` |

The two stock call sites are shared. Hook `0x4FDD0` can receive the Hold or
Entry base, while hook `0x50258` can receive the Full Restore or Intermediate
Restore base. The adapter at `0xD2480` recognizes all four exact bases, chooses
the matching five-entry pointer table, and delegates slot normalization to the
shared helper at `0xD2270`. Selector indices outside `0..4` fall back to Map 1.
An unrecognized base tail-jumps to stock wrapper `0x26388` unchanged.

Map 2 through Map 5 are initialized byte-identically from the input Map 1.
RomRaider and TunerPro expose five independent tables for each family. Hardware
overlays 15 through 17 install the inactive payload and then activate the two
shared hook literals independently before selector execution is introduced.

## Entry and exit delays

`FUN_0004FE9C` returns `stage1 << 8 | stage2`. The state machine loads the high
byte into `0xFFFF2571` and the low byte into `0xFFFF2572`.

With stock `ROM8[0x870C].bit7 = 0`, normal branches select:

| Condition | Stage 1 | Stage 2 | Time at 10.24 ms/count |
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
provide delays `[0, 5, 2]` and counts `[0, 2, 2]`. The corresponding target
delays are 0, 51.2, and 20.48 ms.

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
G = 0x3F when any global Boolean condition is active, otherwise 0x00
D = mask returned by FUN_000503E0
C = mask returned by FUN_0005079C
P = G | D | C
R = Power Balance mask when FUN_00050A34 selects it, otherwise P
A = ETC-actuator-fault mask returned by FUN_0005096C
0xFFFF22E0 = (R | A) & 0x3F
```

The global Boolean group contains exactly 15 contributors. It includes the main
RPM limiter `FUN_0004F282`, the stationary RPM limiter `FUN_0004F324`, and 13
other statically classified conditions. Two intervening calls update state but
do not contribute their return values. The complete inventory is maintained in
[`JK08A.fuel-inhibit.md`](JK08A.fuel-inhibit.md).
`FUN_0005079C` maps a clamped count through masks
`[0x01, 0x05, 0x15, 0x17, 0x1F, 0x3F]`. `FUN_0005096C` creates an independent
RPM-shaped mask for exact P2119/P1238 ETC actuator fault records. Nissan
service 0x30 IOLID `0x0C` can activate a Power Balance replacement byte from
`0xFFFF992F`. The replacement is applied after
the global/DFCO/count OR and can substitute or clear those bits. The auxiliary
mask is ORed after the replacement and cannot be cleared by it. Main and
stationary fuel cuts each contribute a full `0x3F`, which absorbs any partial
DFCO or count mask before the replacement stage. These contributors share the
final mask but are not evidence that their physical causes are DFCO. The unified
ordering and limiter boundaries are maintained in
[`JK08A.limiters.md`](JK08A.limiters.md).

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
peripheral. Fallback word `0xFFFF23AA` is the scheduler snapshot of injector
opening time `0xFFFF2436`, so an inhibited channel is commanded a pulse that
delivers no fuel, and the 800/256 factor places every duration word on the same
`10 us` scale as the diagnostic injection-pulse words; the derivation is in
[`JK08A.fuel.md`](JK08A.fuel.md). Physical cylinder order and the exact
electrical output behavior require bench or engine validation.

## Calibration inventory

| Address | Shape | Code role | Scale | Stock characteristics |
|---|---|---|---|---|
| `0x120F6` | 1x16 u8 | conditional stage-1 entry delay | scheduler counts | all cells 60; stock selector branch disabled |
| `0x126E4` | 1x16 u8 | held-request RPM threshold | `x * 25 RPM` | live in stock |
| `0x12718` | 1x16 u8 | rising-edge entry RPM threshold | `x * 25 RPM` | live in stock |
| `0x12818` | 1x16 u8 | lower/full-restore RPM threshold | `x * 25 RPM` | live in stock |
| `0x1298C` | 1x16 u8 | low-speed upper/intermediate-restore RPM threshold | `x * 25 RPM` | live below speed count 4; ignored by stock moving branches |
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

The map-switching layout redirects all four live DFCO thresholds through the
base-discriminating adapter. Hold, Entry, Full Restore, and Intermediate Restore
therefore resolve from one atomic slot index. Shared axes, delays, state-machine
logic, offsets, floors, and arbitration remain global and byte-identical to the
input firmware.

## Remaining hardware validation boundary

Further validation can establish, without changing the code model:

- physical meaning and transition conditions of `0xFFFF2459.bit5`;
- direct state and timer values during real deceleration;
- exercise the `0x12818` equality and above-range boundary on the vehicle;
- physical injector closure and diagnostic injector-duration behavior;
- injector channel-to-cylinder order;
- behavior of the rotating release branch near 750 RPM.
