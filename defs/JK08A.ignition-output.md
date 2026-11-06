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

The tooth entry `0x00028EA2` reads `ICR0A` at `0xFFFFF434`. Initializer
`0x00028D3C` writes `IPRC = 0xF7F8`, so `ICI0A` uses priority 8
(`IPRC[3:0]`, vector 84). The cam entry `0x0002A2BE` reads `TSR1A` at
`0xFFFFF45E` and clears its bit 4 with `0x01EF` at `0x0002A2EE`.
That flag is `IMF1E`, whose interrupt `IMI1E` uses vector 100 and
`IPRD[3:0]`. The other cam entry, `0x0002A5CC`, clears `IMF1F` with
`0x01DF` at `0x0002A5FC`; `IMI1F` uses vector 101 in the same priority
group. The initializer writes `IPRD = 0xFF8A`, so both cam sources use
priority 10 and can preempt a tooth section at mask 8. They cannot preempt
each other. The register
and vector assignments are defined by the SH7058S/SH7059 hardware manual,
table 7.4 and section 11.2.5.

The cam path reaches the engine-event feeder through the fallback branch
`0x0002A316..0x0002A31E`, `0x0002A4B2`, `0x0002A51E`, and the call to
`0x0002B768` at `0x0002A592`. That routine calls `0x000208F8` at
`0x0002BC80`. The second cam entry tests bit 6 at
`0x0002A626..0x0002A62E`, enters `0x0002A782` and calls `0x0002B768` at
`0x0002A86C`. Both feeder paths require `0xFFFF24C9.bit6` to be set; with
the bit clear, neither cam path runs the ignition dispatcher. The mode
snapshot is copied by main-loop function `0x00020DFE` from
`0xFFFF24CE..0xFFFF24D3` to
`0xFFFF24C8..0xFFFF24CD` by `0x00022558` at `0x00021348`, after the
periodic loop raises its mask to 15 at `0x00021300`. The main loop cannot
run inside an interrupt handler, so the snapshot stays fixed for the entire
handler. With bit 6 set, the tooth entry tests it at
`0x00028EEA..0x00028EF2` and jumps through literal `0x0002902C` to epilogue
`0x0002A294`, which returns at `0x0002A2BA`, before the only feeder call at
`0x0002983A`. The tooth path therefore publishes no ignition command in
fallback mode. Thus a
normal-mode adapter publication cannot be interrupted by a cam fallback
publication. When fallback is selected, the adapter and publisher must
apply the stock command and publish zero cut fraction on every entry.

## Dwell sequence guard and recovery

The divider call and the following masked enable check use stable eligibility
inputs. The normal tooth path and `0x0002B768` write `0xFFFF13D1`,
`0xFFFF13D2` and `0xFFFF84EA`; `0x0002B768` runs only in the mutually
exclusive cam fallback path described above. The tooth path updates its
cylinder mask after both dwell-arming sections. `IMI11B` runs at level 8 and
cannot preempt either section. The writer of `0xFFFF4185`, task
`0x00021834`, runs from `IMI3A` at level 6. The timeout handlers `IMI5A`
and `IMI5B` run at level 10 and can update compare and output registers,
but do not write these eligibility inputs or `0xFFFF8511`. The reviewed
higher-priority handlers provide no other normal-mode writer. This
exclusion requires the stock interrupt priorities and no additional
higher-priority writer of the eligibility inputs.

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

## GR11B programming-time budget

The dwell veto adds execution before the stock stores to `GR11B` at
`0x000294DC` and `0x00029572`. Its software-state exclusion does not establish
that either store precedes its compare deadline. The bounded GNU fixture
executes the countdown and output paths, but its scaffold transfers from
`0x00028ECC` to `0x000292EC`. It excludes the earlier capture processing and
does not model CPU cycles, peripheral bus arbitration or interrupt arrival
rates. Its result is **executed functional coverage**, not a measured
capture-to-compare latency.

### Clock and nominal compare window

The SH7058S/SH7059 hardware manual, sections 5.1 and 5.2, specifies
`phi = 8 * EXTAL` and `Pphi = 2 * EXTAL`. With the target's established
`Pphi = 20 MHz`, the CPU clock is `80 MHz`. Initializer `0x000274AC` writes
`PSCR1 = 1` at `0x000274B4`; initializer `0x0002718A` writes `TCR11 = 5`
at `0x0002745A`. Under sections 11.2.2 and 11.2.3, these select
`TCNT11 = Pphi / (2 * 32) = 312500 Hz`, or `3.2 us` per count.

The normal secondary scheduler `0x0002ACBA` adds ten to the byte remainder
at `0x0002AE34..0x0002AE3E`. Normalizer `0x00028DC8` retains that remainder
or adds another ten or twenty. The nominal minimum countdown-expiry offset
is therefore ten crank degrees. At steady speed its ideal duration is
`60 / (RPM * 36)` seconds:

| Speed | Ideal ten-degree interval | Interval rounded down to TCNT11 counts |
| ---: | ---: | ---: |
| 7650 RPM | 217.865 us | 68 counts, 217.6 us |
| 5000 RPM | 333.333 us | 104 counts, 332.8 us |

The stock active fuel-cut values at `0x0000934E` include 7650 RPM under the
established `raw * 12.5 RPM` conversion. This is a stock calibration reference,
not a universal engine-speed limit. The interval calculation assumes the
stored tooth period represents the upcoming interval. Capture delivery,
period-filter error and acceleration can reduce the available window.

The tooth stores use the captured reference `0xFFFF158A`, saved at
`0x00028F22`; they do not read the current `TCNT11` or clamp a late compare.
The immediate secondary scheduler has a different contract: its
`0x0002AE90..0x0002AEB6` path checks elapsed time and substitutes
`TCNT11 + 2` when needed. Section 11.3.1 defines equality compare matching.
A tooth-path store behind the current counter does not cause immediate
catch-up. Without another compare write or counter reset, the next equality
requires a counter wrap, whose full period is `209.7152 ms`. This does not
establish that a vehicle output remains unchanged for that period; later
stock writes and recovery can replace the compare.

### Instruction accounting and executed paths

The accounting model assigns five CPU states to every executed instruction,
including delay slots, at 80 MHz: one instruction costs `0.0625 us`.
The private-path figures are **maximum instruction counts observed in the
GNU matrix**, not hardware WCET. The observer binds each executed word,
branch, delay slot and call/return to the payload and fixture. Counts start
at the actuator entry, include helper calls, their returns and the tail
jump, and stop before stock divider `0x00021CE0`.

| Private path | Maximum observed instructions | Model time per call |
| --- | ---: | ---: |
| Cached off-HOLD phase, quiet counter saturated, no marker to release | 27 | 1.6875 us |
| Cached off-HOLD phase, quiet counter still increasing | 29 | 1.8125 us |
| Cached ACTIVE outside HOLD | 22 | 1.375 us |
| First off-HOLD arming of a phase, including reset and event service | 105 | 6.5625 us |
| Cached IDLE with marker 1 requiring the masked recheck | 84 | 5.25 us |
| Admitted HOLD arming, including a cut and a zero-to-one latch update | 153 | 9.5625 us |
| Other HOLD paths, including invalid q or accumulator reset | 144 | 9 us |

The matrix includes all six valid one-hot cylinder masks, first and repeated
armings, quiet counts across 13/14 and 254/255, a marker supplied after
saturation, and an IDLE/ACTIVE/COOLDOWN/IDLE cycle. The trace requires a
single reset on the first off-HOLD path and no reset on either cached path.
The reset cache at base `+0x1F` is published after all six accumulator
stores with interrupts masked, and every HOLD entry invalidates it before
an accumulator can change. Quiet and latch service continue on cache hits.
The fast tail enters the original divider at `0x00021CE0`; its ABI and
final stack are compared with the independently executed stock call.

Before the second `GR11B` store, both countdown slots can call the veto.
Charging the observed admitted maximum twice gives 306 instructions, or
`19.125 us` in this model. The counts cover the declared functional matrix;
they do not establish a capture-to-store time or interrupt arrival bound.

The stock capture prefix is not executed by this fixture. A deliberately
loose static allocation counts every listed instruction once, expands each
six-iteration loop to six copies, and retains mutually exclusive forward
branches. From entry `0x00028EA2` through the first or second store, it has
these components:

| Component | First store | Second store |
| --- | ---: | ---: |
| Tooth-handler instructions through the store | 681 | 756 |
| Divider `0x00021BBC`, called at `0x000290B4` | 141 | 141 |
| `0x00054D3E` with the caller's r4 = 0, excluding its callee | 176 | 176 |
| Six-channel scheduler `0x0002C13C`, called at `0x000291C6` | 564 | 564 |
| Optional `0x000571C0`, excluding its six helper calls | 388 | 388 |
| Stock divider `0x00021CE0`, up to two or three calls | 230 | 345 |
| Known subtotal, excluding six calls to `0x000221BC` | 2180 | 2370 |

The `0x00054D3E` loop body has four instructions. The bodies at
`0x0002C16E..0x0002C21C` and `0x000571EE..0x00057262` have 88 and 59
instructions respectively. Each receives five additional copies above its
single listed copy. The optional call at `0x00054E78` is selected by
`ROM8[0x8D92].bit3`, set in stock byte `0x7A`. Its six calls at `0x000571F4`
enter computed-jump helper `0x000221BC`. Let H be an upper instruction count
for one complete helper call, including its selected shift tail. That
computed-target bound remains unreviewed here. The stock allocations are
therefore `S1 = 2180 + 6 * H` and `S2 = 2370 + 6 * H`, not complete numeric
prefix bounds. The 64 listed entry instructions before `0x00028F22` are
included; latency from the hardware capture to handler entry is additional.

### Higher-priority interference

Initializer `0x00028D3C` sets the relevant priorities to
`IPRD = 0xFF8A`, `IPRF = 0x6F9F` and `IPRG = 0xAFFF`. The following are
confirmed application sources above the tooth mask of 8:

| Source | Priority | Enable evidence | Handler and static instruction allocation |
| --- | ---: | --- | --- |
| IMI1E | 10 | `TIER1A = 0x0030` at `0x00027206`, bit 4 | `0x0002A2BE`, continuation `0x0002A36A`, exit `0x0002A59A`: 220 own instructions plus 141 for `0x00021BBC` |
| IMI1F | 10 | Same write, bit 5 | `0x0002A5CC`: 325 own instructions plus 141 for `0x00021BBC` |
| IMI4C | 9 | `TIER3 = 0x018B` at `0x0002727A`, bit 7 | `0x000C2C58`: 143 own instructions plus 141 for `0x00021BBC` |
| IMI4D | 9 | Same write, bit 8 | `0x000C2D76`, continuation `0x000C2DE0`: 143 own instructions plus 141 for `0x00021BBC` |
| IMI5A | 10 | `0x0002AF38` enables `TIER3.bit10` while arming timeout A | `0x0002B396`, continuation `0x0002B498`: 155 instructions |
| IMI5B | 10 | `0x0002AF38` enables `TIER3.bit11` while arming timeout B | `0x0002B4EC`, continuation `0x0002B5F4`: 158 instructions |

The cam allocations apply with the normal-mode snapshot bit 6 clear. They
exclude the mutually exclusive `0x0002B768` fallback call. These handlers
have no repeated local loop on the included paths; the allocations include
all listed forward alternatives and the completed `RTE` delay slot. They
bound instruction counts per invocation, not total interference. The six
allocations sum to `106.75 us` in the five-state model if one invocation of
each is charged. No bound of one invocation per source is established.

This is a confirmed subset, not an exhaustive enabled-source census.
SCI1, HCAN1, external IRQ/NMI, interval, ADC and DMA enabling and arrival
conditions are not fully bounded. A nonzero IPR field alone does not prove
that its peripheral source is enabled. Conversely, semantic exclusion of
eligibility writers does not limit the CPU time of their handlers. The
total preemption term remains **unbounded by this analysis**.

### Remaining margin

For store i, let A include capture-to-entry latency and period-estimation
allowance, P the total preemption time, and W the cumulative private-wrapper
time. The requested margin is `M = window - A - S / 16 - W - P` in us,
and its ratio to the wrapper addition is `M / W`.

At 7650 RPM, the admitted-path allocations give
`M1 = 71.7875 - 0.375 * H - A - P` and
`M2 = 50.35 - 0.375 * H - A - P` us. At 5000 RPM, replace the constants
by `186.9875` and `165.55`. These are conditional allocation equations,
not observed margins. H, A and P remain unresolved, and the deliberately
loose stock allocation is not an executed maximum. A positive complete
margin or a tenfold `M / W` factor is not established.

The model also needs a hardware bus-time qualification. Manual table 9.5
allows 8..11 CPU states for an ATU/APC/PORT byte or word access and 16..19
for a long access. A uniform five states per instruction cannot serve as
a hardware upper bound for these peripheral-heavy stock handlers. Capture
latency, complete prefix execution, enabled-source arrival bounds and
peripheral access costs remain timing obligations before treating this
calculation as a deadline proof.

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
