# JK08A ignition output and late-retard contract

## Scope and result

This document describes the exact stock JK08A software path from the final
signed timing coordinate to the SH7058 Advanced Pulse Controller (APC). It also
defines the static acceptance boundary for a late retard-only override at the
final consumer, which the historical Rolling Launch RPM-hold endpoints applied.
The current Rolling Launch adapter passes the stock command through unchanged.

The normal-mode software contract supports a target command range of
`110..117`. In the normal diagnostic coordinate this range represents
`0..-7 deg BTDC`. A late override is retard-only when it selects
`max(stock_command, target_command)`. Support is conditional on preserving the
stock command while `0xFFFF24C9.bit6` is set, because that bit selects a
P0335-driven APC fallback scheduler whose physical angle behavior is not part
of the normal contract.

Static analysis proves command construction, ordering, byte ranges, both APC
compare paths, diagnostic publication, the crank reference tooth of the command,
the output edge that carries the spark, and the dwell sequencing, recovery and
timeout that protect the coil outputs. It does not prove the external
driver stage or the mechanical offset between the crank sensor and the signal
plate. Those properties require a timing light and a controlled bench or engine
test.

## Timing-state selector

`FUN_0004AFDC` produces a signed timing-state addend in `0xFFFF1511`. Three
eight-point maps use the exact `x-128` transform, but the stock selector gives
them different roles and also contains a constant bypass:

| Priority | Selected source | Exact predicate |
|---:|---|---|
| 1 | feature map `0x121A6` | `ROM8[0x870B].bit0 = 1` and `uint16[0xFFFF2318] < 0x4000` |
| 2 | warm DFCO-transition map `0x1219E` | `0xFFFF244F.bit2 = 0`, `0xFFFF41DE.bit5 = 1`, `0xFFFF2458.bit5 = 1`, and `0xFFFF2590 != 0` |
| 3 | constant `ROM8[0x86A2]` | `0xFFFF22FF = 3` and `0xFFFF2458.bit7 = 1` |
| 4 | default/post-transition map `0x12196` | every other case |

The warm latch in `0xFFFF41DE.bit5` sets when raw coolant snapshot
`0xFFFF1071` reaches `ROM8[0x86A4] = 110` and remains set down to raw 106.
Under the exact diagnostic `raw-50` conversion, those boundaries are 60 and
56 deg C. While `0xFFFF2458.bit5` is clear, the function reloads
`0xFFFF2590` from `ROM8[0x86A3] = 85`. Once the bit becomes set, the periodic
scheduler decrements the timer and `0x1219E` remains eligible only while it is
nonzero. One timer count is `204800/Pphi` seconds. Passive target-CAN timing
establishes `Pphi = 20 MHz`, giving a maximum selection window of `870.4 ms`.

The constant path selects stock byte `0x9E`, which becomes `+30` after the
same `x-128` transform. It bypasses all three maps.

The `0x121A6` path is stock-inert for two independent reasons. Stock
`ROM8[0x870B] = 0x46` has bit 0 clear. In addition, initialization writes
exactly `0x4000` to `0xFFFF2318`, while the selector requires a strict value
below `0x4000`; a whole-application p-code census found no other writer. The
stock bytes of `0x121A6` are identical to default map `0x12196`, but this
identity is not needed for the reachability result.

The enabled 1.11 target capture isolates the default/post-transition map during
matched warm deceleration. At `4000..4400 RPM`, a 16-count slot difference
produces the same 16-count shift in the median final software timing coordinate
while the calculated injection words and Base Fuel Schedule remain effectively
unchanged. This establishes one-for-one software-coordinate propagation in the
observed state and disproves an exclusive cold-idle qualifier. The A2L names
`Cold Idle Ignition Timing`, `Idle Ignition Timing`, and `Idle Timing (Lean)`
remain catalog provenance. The coefficient-1 chain from `0xFFFF23EE` through
`0xFFFF1830`, `0xFFFF2404`, `0xFFFF2378`, `0xFFFF12D6`, and `0xFFFF11DA` to
`0xFFFF11D4`, together with the J1979 PID `0x0E` declaration of that
coordinate, makes one count of these maps one crank degree.

## Final command and diagnostic coordinate

Engine-event dispatcher `0x0004E162` executes this fixed order:

```text
0x0004E112 -> 0x0004E0C2 -> 0x0004D99C -> 0x0004DBE8
             -> 0x0004DF82 -> 0x0004E080
```

`0x0004DBE8` performs the final stock timing arbitration and writes signed byte
`0xFFFF11D4`. Its input sum is

```text
ffff11da = clamp(ffff12d6 + ffff564c, ROM8[0x8221], ROM8[0x821E])
```

with stock bounds `ROM8[0x821E] = 50` and `ROM8[0x8221] = 0xF9`, where `0xF9`
is `-7` as `int8`. `0xFFFF12D6` is the engine-event correction of
`0x0004D99C`, which carries the previous-pass timing state `0xFFFF2378`, the
negated retard request `0xFFFF11D6`, the bounded correction `0xFFFF2356`, and
the scaled `0x147DA` subtraction. `0xFFFF564C` is the `-5..0` work-support
timing adjustment `TARGET IGN TIM ADJ` of `0x0004AAD0`, published as DID
`0x112D` and specified in `JK08A.work-support.md`. It is added only while bits
1..5 of mode byte `0xFFFF5B31` are clear: coolant raw at or above 110, RPM/25
within `ROM8[0x8897]..ROM8[0x8896] = 48..128`, and load within
`ROM8[0x8768]..ROM8[0x8767] = 64..96`, each with hysteresis. The sum then
moves from the previous `0xFFFF11D4` by at most `ROM8[0x828A..0x828E] = 4`
counts upward per pass (`15` in the flagged modes)
and `ROM8[0x8291] = 15` downward, is re-clamped to `-7..50`, is bounded below
by `-(129 - coolant raw)` while coolant raw is below 130 and above by
`ROM8[0x83D5] - 40 = 70`, and is written to `0xFFFF11D4`. Stock
`ROM8[0x8B34] = 0x81` has bit 4 clear, which skips the override branch. Every
term enters with coefficient 1, so the coordinate is crank degrees as declared
by J1979 PID `0x0E`. Additional diagnostic and fallback modes can use other
boundaries, so `-7..50` is the normal-mode envelope rather than a universal
final range.

On the normal path `0x0004DF82` computes:

```text
command = uint8(110 - uint8(final_signed_coordinate))
```

Stock `ROM8[0x83D5]` supplies `110`. The function writes the command to
`0xFFFF2022` and calls primary scheduler `0x0002A892`. Exact JK08A UDS table
entries for DIDs `0x1107`, `0x1108`, `0x1109`, and `0x110A` all return this same
byte.

The homologous P32M Nissan diagnostic profile defines DID `0x110A` as
`IGN TIMING4` with `deg = 110 - raw`. This exactly inverts the normal firmware
transform over the admitted range:

| Command | Normal diagnostic coordinate |
| ---: | ---: |
| `110` | `0 deg BTDC` |
| `115` | `-5 deg BTDC` |
| `117` | `-7 deg BTDC` |

The VQ35HR factory ESM identifies `IGN TIMING` as a value computed by the ECM.
Its active test directs CONSULT-III to retard ignition while a timing light is
connected. The diagnostic byte is therefore a commanded/computed value, not a
measurement of physical spark angle.

## Late override point

The call target literal at `0x0004E198` belongs to the final call in
`0x0004DF82`. Replacing only that consumer places an adapter after all stock
final-angle arbitration and before the primary APC scheduler. The required
adapter sequence is:

```text
stock command from r4
  -> validate runtime mode and configuration
  -> require 0xFFFF24C9.bit6 == 0
  -> validate target in 110..117
  -> effective = max(stock, target)
  -> write effective to 0xFFFF2022
  -> tail-call 0x0002A892 with effective in r4
```

Every invalid, inactive, or fallback-mode path must tail-call `0x0002A892`
with the unchanged stock command. Writing the effective command to
`0xFFFF2022` is necessary because the following `0x0004E080` call reads that
byte to construct the secondary command. It also makes DIDs `0x1107..0x110A`
report the effective command.

For normal-mode commands, selecting the larger byte cannot advance the
software timing coordinate because the diagnostic transform has slope `-1`.
Targets `110..117` stay inside the stock normal lower bound. Commands above
`117`, which would represent values below `-7 deg BTDC` under the same formula,
are outside this static acceptance boundary.

## Active target-vehicle command evidence

The exact 1.11 image and 2026-08-17 moving capture are registered in
`../patches/hardware-results.toml`. Across 35,811 complete telemetry snapshots,
the normal identity `final_timing_raw = 110 - apc_command_raw` holds in 35,444.
All 367 differences occur during Map 2 or Map 3 Rolling Launch intervals: 342
while CANCEL is held and 25 around release.

This establishes the intended late-hook ordering on the target. The telemetry
field sourced from `0xFFFF11D4` remains the upstream stock coordinate, while
the field sourced from `0xFFFF2022` carries the effective command consumed by
the APC scheduler. Every recorded activation reaches the configured bounded
retard-command region and retains the stock value whenever it is already at
least as retarded. The evidence validates software command direction and
adapter placement, not physical crankshaft timing.

## Primary APC scheduler

Helper `0x00028E7C` splits an unsigned byte exactly into:

```text
quotient = floor(command / 10)
remainder = command - 10 * quotient
```

Normal-mode scheduler `0x0002A892` stores the decade and remainder at
`0xFFFF1558` and `0xFFFF155A`, carries complete decades through
`0x00028DC8` and continuation handler `0x0002AB24`, and calculates the current
fractional compare offset as:

```text
0xFFFF16C2 = min(65535, floor(0xFFFF22BC * remainder / 10))
```

It programs `GR11A` at `0xFFFFF5C2`, clears the applicable `TSR11` flag, and
enables the current-cylinder low-byte `POPCR` action. Target commands
`110..117` share one command decade and remain below the fallback-only clamp at
`199`.

`0xFFFF24C9.bit6` selects a different primary and secondary scheduling mode.
The bit is the periodic snapshot of `0xFFFF24CF.bit6`. Function `0x00099A48`
sets it from the active runtime status of the P0335 record pair when the P0340
and P0345 record pairs do not select their companion modes. Because the
alternate APC path is a position-sensor diagnostic fallback, the late override
must pass the stock command through whenever the snapshot bit is set.

## Secondary compare and overflow proof

The secondary command is produced after the primary call:

```text
secondary_command = effective_primary_command + reset_offset
```

The complete stock range proof is:

1. `0x0004C1E4` bounds byte `0xFFFF1874` by
   `ROM8[0x8B88] = 6` and `ROM8[0x8B87] = 114`.
2. It writes `0xFFFF2406 = min(0xFFFF1874, 0xFFFF1875)`, or forces `24` under
   the associated diagnostic state. Therefore `0xFFFF2406` is in `0..114`.
3. Periodic dispatcher `0x00020DFE` copies `0x8C` bytes from
   `0xFFFF23BC..0xFFFF2447` to `0xFFFF2330..0xFFFF23BB`. The matching offset
   proves `0xFFFF2406 -> 0xFFFF237A`.
4. `0x0004E080` starts from `120 - uint8(0xFFFF237A)`. Its optional subtraction
   uses stock `ROM8[0x8649] = 0`, so stock `reset_offset` is in `6..120` in
   either branch.
5. For an applied target of at most `117`, the largest newly constructed
   secondary command is `117 + 120 = 237`, below the byte boundary `256`.
   When the stock primary command is already above the target, the override
   leaves it unchanged and introduces no new arithmetic case.

`0x0004E080` stores the offset at `0xFFFF2230` and calls `0x0002ACBA` with the
sum. The secondary scheduler uses the same divide-by-ten representation and
programs `GR11B` at `0xFFFFF5C4`. The accepted override range therefore reaches
both stock compare schedulers without a newly introduced `uint8` wrap.

The SH7058 hardware manual proves that the selected low `POPCR` bit drives the
PULS output high on a `GR11A` compare and the selected high `POPCR` bit drives
it low on a `GR11B` compare.

## Crank reference and output edges

The command is the delay in crank degrees after tooth 7 of the crank signal
plate, the last tooth before the two-missing-teeth gap. The ICI0A handler
(vector 84, entry `FUN_00028EA2`) counts ten teeth per 120
crank degrees in `0xFFFF13B2`; on tooth 7 it copies the identified cylinder to
event index `0xFFFF11DE`, forms set mask `0xFFFF13BD = 1 << (index - 1)`, and
runs the engine-event tasks that build the command. `0x0002A892` splits the
command by ten, `FUN_00028DC8` converts the 10-degree steps into tooth events
across the gap, and the handler prologue decrements tooth count `0xFFFF1558` on
every later tooth. At zero it writes
`GR11A = 0xFFFF158A + 0xFFFF22BC * remainder / 10` from the tooth capture and
the 10-degree interval and enables the set action of the mask. Command 95
becomes six tooth events to tooth 3 plus 15 degrees.

With `ROM8[0x83D5] = 110` the command is `110 - advance`, so tooth 7 is 110
degrees before compression TDC of the event cylinder and TDC falls on tooth 6.
The event index is the cylinder number of the P0301..P0306 descriptors; the
derivation through the misfire interval attribution is in
[`JK08A.fuel.md`](JK08A.fuel.md).

The ignition advance moves only the `GR11A` set edge, so that edge is the spark.
`0x0004E080` places the `GR11B` reset edge `120 - 0xFFFF237A` degrees after the
primary command, which is `0xFFFF237A` degrees before the set edge of the next
cylinder, and reset mask `0xFFFF13D1 = ROM8[0x22687 + 0xFFFF13D3]` addresses
that next cylinder (`0xFFFF13D3 = ROM8[0x22680 + 0xFFFF13C9]`, the successor of
the current cylinder). The low state of a PULS pin is therefore the dwell of
its cylinder and `0xFFFF237A` is the dwell angle in crank degrees. The pin scans
at `0x0002A05E` and `0x0002BCEA` read PULS0..4 from `PDDR` bits 8..12 and PULS5
from `PBDR` bit 15, skip the all-high idle state, and record the number of the
first low pin in `0xFFFF13D2`. Bit `c - 1` of both masks addresses cylinder
`c`. The external driver stage and the
cylinder-to-pin continuity are hardware boundaries.

## Output enables and dwell sequencing

Both `POPCR` actions are one-shot. Handler `0x0002AB24`, at interrupt-table
entry `0x000202E4`, services the `GR11A` match. While the set compare is armed
(`0xFFFF8517.bit7`) it clears the low byte of `POPCR`, clears the armed bit
and, with crank sync `0xFFFF8501.bit7`, advances dwell channel
`0xFFFF13D3 = ROM8[0x22680 + 0xFFFF13C9]`, the successor of the event
cylinder. It also sets `0xFFFF850E.bit7` while `0xFFFF84EA.bit7` is set,
`0xFFFF13D2` is zero and `0xFFFF24C9.bit6` is clear.

Handler `0x0002AF38`, at entry `0x000202EC`, services the `GR11B` match while
`0xFFFF8518.bit7` is set. With interrupts masked it saves the high byte of
`POPCR`, the pins that have just entered dwell, in `0xFFFF13CE` and clears
that byte. It then recomputes the dwell mask
`0xFFFF13D1 = ROM8[0x22687 + 0xFFFF13D3]`, the one-hot bit of the successor
of `0xFFFF13D3`; `0xFFFF4198.bit1` forces the mask to zero instead. With the
stock tables every `GR11A` match advances `0xFFFF13D3` by one cylinder and
every `GR11B` match advances `0xFFFF13D1` by one cylinder.

In normal mode `0x0002ACBA` only stores the decade and remainder of the
secondary command. Two alternating countdown slots hold them:
`0xFFFF1448` with remainder `0xFFFF144E` and `0xFFFF144A` with remainder
`0xFFFF144F`. The crank-tooth handler `0x00028EA2` decrements each slot on
every tooth. At zero it computes the compare offset through divider
`0x00021CE0`, whose call target both slots load from literal `0x000296C0`
(`0x000294A2`, `0x0002953A`), and writes `GR11B = 0xFFFF158A + offset`. It
enables the high-byte action of `0xFFFF13D1` only when `0xFFFF84EA.bit7` and
`0xFFFF4185.bit7` are set, `0xFFFF13D2` is zero and `0xFFFF8511.bit7` is
clear (`0x000294DE..0x0002950C`, `0x00029574..0x000295A2`). It sets
`0xFFFF8518.bit7` in either case, so the `GR11B` match is serviced even when
no pin is enabled.

## Interrupt context of dwell arming

The engine-event task table runs inside the crank-tooth interrupt:
`0x00028EA2` calls task feeder `0x000208F8` at `0x0002983A`, and table index 4
is timing dispatcher `0x0004E162`, which calls `0x0004DF82` and then
`0x0004E080`. With stock `ROM8[0x8649] = 0` the secondary command of an
event is the primary command plus `120 - 0xFFFF237A`, so the dwell scheduled
at an event belongs to the successor cylinder.

Each countdown slot runs its divider call at interrupt mask 8, set at
`0x00029480`, and raises the mask to 15 from its `GR11B` write through the
enable check (`0x000294C8..0x00029520`). The set-arming section runs at mask
15, so `0x00029480` lowers the mask from 15 to 8; the paths that skip that
section already run at the mask 8 that `0x000291E0..0x000291E8` set. The recovery at set arming runs its compare write
and enable under mask 15 from `0x0002932E`. Handler `0x0002AB24` has no caller
besides its table entry; it saves its registers on entry and returns with
`RTE`. Handler `0x0002AF38` is the only stock writer of `0xFFFF8511`; the
crank-tooth handler, `0x0002A892`, `0x0002ACBA` and `0x0002B768` read it.
The interrupt-priority initializer `0x00028D3C` writes `0x8FFF` to `IPRJ`
(`0xFFFFED12`), so ATU channel 11 runs at level 8: `IMI11A` (vector 184,
`GR11A`, entry `0x000202E4`) and `IMI11B` (vector 186, `GR11B`, entry
`0x000202EC`) with `VBR = 0x00020004`. Neither match preempts the other or
the crank-tooth sections at mask 8, and an interrupt above level 8 can delay
both.

## Dwell sequence guard and recovery

After recomputing `0xFFFF13D1`, handler `0x0002AF38` compares it with the
successor of its previous value (`0x20` becomes `0x01`, other values shift
left by one). While `0xFFFF84EA.bit7` is set and `0xFFFF13D2` is zero, a
mismatch or a zero mask sets bits 7 and 6 of `0xFFFF8511`. A consistent
advance copies bit 7 into bit 6 and clears bit 7. Bit 7 withholds the next
dwell-start enable; bit 7 or bit 6 blocks the recovery below.

When the crank-tooth handler arms the set compare (`0x00029308..0x0002947E`)
and the `PULS` pin of firing mask `0xFFFF13BD` still reads high, it restarts
the dwell if `0xFFFF850E.bit7` is set, reset offset `0xFFFF2230` exceeds 20
(a dwell angle below 100 degrees) and bits 7 and 6 of `0xFFFF8511` are clear.
It clears the countdown slot selected by `0xFFFF84FB.bit7`, writes
`GR11B = TCNT11 + 2` and clears the `GR11B` match flag. With `0xFFFF84EA.bit7`
and `0xFFFF4185.bit7` set and `0xFFFF13D2` zero, it enables the high-byte
action when `0xFFFF13D1` equals `0xFFFF13BD`, and otherwise clears both
countdown slots. The cylinder then fires with only the angle that remains
between the arming tooth and its set compare. Primary scheduler `0x0002A892`
contains the same recovery for a set compare that its own call arms.

## Dwell timeout

For the pins saved in `0xFFFF13CE`, handler `0x0002AF38` arms a dwell timeout
in one of two alternating slots selected by `0xFFFF851A.bit7`:

| Slot | Pins | Compare | Handler | Table entry |
| --- | --- | --- | --- | --- |
| A | `0xFFFF13CF` | `0xFFFFF4E2` | `0x0002B396` | `0x00020224` |
| B | `0xFFFF13D0` | `0xFFFFF4E4` | `0x0002B4EC` | `0x00020228` |

The timeout angle is `0xFFFF237A + ROM8[0x8A4F] + ROM8[0x8986]`, the dwell
angle plus `20 + 30` crank degrees, saturated at 255 and stored in
`0xFFFF1326`. It is converted with event period `0xFFFF11FC` as
`angle * 0xFFFF11FC / 1200`, capped at `ROM16[0x9222] = 3125`, stored in
`0xFFFF1834` and multiplied by ten. Longer timeouts run through extension
counts `0xFFFF1322` and `0xFFFF1324`. When the timeout expires and a pin of
its slot still reads low, the handler forces the spark: with a pending set
countdown in `0xFFFF1558` it clears the countdown, writes
`GR11A = TCNT11 + 2`, enables the low-byte action of the slot pins and sets
`0xFFFF8517.bit7`. Without a pending countdown it moves `GR11A` to
`TCNT11 + 2` when the compare lies more than five counts ahead or
`0xFFFF13D2` is nonzero, and enables the low-byte action of the slot pins.
At constant speed the forced spark follows the scheduled spark by about 50
crank degrees.
The absolute time unit of the timeout is not established here.

## Consequences of an omitted compare

- A set compare that is never scheduled after its dwell started leaves the
  pin low until the dwell timeout forces a late spark. The `GR11A` match of
  that forced spark arrives without `0xFFFF8517.bit7`, so `0x0002AB24` does not
  advance `0xFFFF13D3`, and the next `GR11B` match trips the sequence guard.
- A reset compare that is never scheduled leaves the pin high. The recovery at
  the set arming restarts the dwell, and the cylinder fires with a short
  dwell.
- Clearing `0xFFFF13D1` before an arming withholds that dwell, and the next
  `GR11B` match then sees a zero previous mask. The guard sets bits 7 and 6,
  which also withholds the dwell of the following cylinder and blocks its
  recovery.
- A dwell-start enable that is withheld through `0xFFFF8511.bit7` while its
  `GR11B` match is still serviced keeps both sequences intact. The match leaves
  `0xFFFF13CE` zero, so no timeout is armed; the guard sees a consistent
  advance and moves bit 7 into bit 6, which blocks the recovery at the set
  arming of that cylinder. Its `GR11A` match finds the pin high and produces
  no edge, and the next arming enables normally.

## Acceptance boundary

Static support for a late retard-only override requires all of these conditions:

- the adapter is placed at the final `0x0004E198` consumer;
- inactive and invalid paths preserve the stock command;
- `0xFFFF24C9.bit6 != 0` forces stock pass-through;
- each target is in `110..117`;
- the effective command is `max(stock, target)`;
- the effective command is written to `0xFFFF2022` before `0x0002A892`;
- commands above `117` remain rejected until separate hardware validation.

Target-vehicle telemetry establishes software command direction and late-hook
placement inside the accepted `110..117` range. The firmware coordinate places
the spark `command - 110` degrees after compression TDC. A timing-light
measurement is still required to bind that coordinate to the mechanical crank
angle before extending the accepted range beyond `117`.
