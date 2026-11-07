# Custom CAN telemetry schema 2 and JK08A producer

## Status and objective

This document specifies the ROM-neutral schema 2 wire contract and its exact
JK08A firmware producer. The firmware, generated source-pointer table, strict
host decoder, dashboard, MLVLG recorder, ROM builder, and GNU SH-2E executable
gate use the same profile identity.

The generated host schema contains only transport layout, field semantics, the
host presentation of each field, and profile identity. It contains no ROM name,
producer RAM address, physical mailbox, or patch location. Host tools load that
file directly and do not import the JK08A producer manifest. The producer
binding retains the exact ROM, RAM, hook, source-address, and mailbox
constraints required to build safe firmware. The profile CRC covers the wire
layout alone: protocol version, profile ID, page count, the page, offset,
width, and signedness of every fixed field, the page, tag, and ordered
widths and signedness of every context, and the dynamic page. ROM identity, source addresses,
producer storage kinds, field names, context names, scale strings, and the host
presentation are outside it, so a renamed field, a restated scale, or another
presentation keeps the CRC and the firmware bytes. The profile ID states which
quantity each slot carries: a slot that carries a different quantity takes a
new profile ID, and the producer test suite pins one digest of the
slot-to-field assignment per profile ID. Two producers implementing the same
placement, widths, signedness, contexts, profile ID, and protocol version
therefore publish the same wire identity.

Explicit reserved payload bytes carry zero and have no observation channel.
Their page, offset, width, and optional context tag enter the profile CRC.
Fixed-page padding can occupy any declared free span; context padding follows
the last field. The complete payload remains assigned without overlaps or
implicit gaps. The source-pointer table repeats configuration byte 7, whose
reserved-zero value both configuration guards require. The host rejects a
snapshot with nonzero reserved payload bytes.

The endpoint is disabled by default. The complete software gate passes, and
three road drives on 2026-08-26 accepted schema 2 transport and channel
coverage. Those drives carried profile 1, the recording of 2026-09-17 carried
profile 3, and the road session of 2026-09-21 in registry entry
`can_telemetry.schema2_profile5_drive_2026_09_21` carried profile 5. The road
session of 2026-09-22 in registry entry
`can_telemetry.schema2_profile5_drive_2026_09_22` carried the same profile,
and its TRC captures measure the whole-bus load of the stream. The current
profile, whose ID and CRC16 the generated `can-telemetry-identity.h` states,
sends the same eleven DLC-8 frames per snapshot and has no vehicle
recording. The recorded
schema 1 `wide54` result remains useful bus-capacity and mailbox evidence; it
does not validate schema 2 and is intentionally not accepted by the current
decoder.

The objective is a coherent, loss-detectable tuning stream over stock HCAN1
without diagnostic polling. Sampling occurs immediately after the stock
periodic scheduler while interrupts are already masked. The natural cadence is
`204800 / Pphi`. With the measured `Pphi = 20 MHz`, this is `10.24 ms` or
`97.65625 Hz`. Sending the same scheduler-owned values faster would duplicate
samples.

## Architecture

```text
main-loop wrapper
  -> stock FUN_00020DFE and its periodic tasks
  -> poll control mailbox 31 (22 on 1ME3B) for an exact START or STOP command
  -> coherent capture into inactive 88-byte bank
  -> atomic active/pending publication
  -> eleven DLC-8 frames on one standard CAN ID
  -> HCAN1 physical mailbox 26
  -> combined SLE1 completion handler
  -> next page or newest pending snapshot
```

The JK08A implementation preserves the stock CAN transmit scan, stock
serializers, all stock receive mailboxes, and the complete mailbox-28 SLE1
behavior. It converts stock-inactive mailbox 31 into a polled receive mailbox
after every primary or recovery HCAN1 initialization.

The 1ME3B stock initializer configures physical mailbox 31 as receive ID
`0x292` from ROM record `0x00009844`. Its telemetry control endpoint uses
physical mailbox 22 at `0xFFFFDBC0`, data bytes `0xFFFFDBC8..0xFFFFDBCF`,
and group mask `0x0040`. The allocation preserves stock mailbox 31 and its
receive ID. Other targets use physical mailbox 31 for control.

The 1ME3B record for mailbox 22 at `0x00009820` is inactive type 5.
The primary and recovery callers use initializer `0x0011F2EC`, whose table
programmer `0x0011EEDA` leaves that mailbox inactive. The runtime transmit
scanner `0x00120280` skips type 5; its dynamic transmitter `0x0011FE2C`
reconfigures only physical mailbox 1. Runtime diagnostic writers use mailbox
28. The programming handoff at `0x0012B53C` deactivates mailboxes 0..26 and
enters a non-returning RAM programming loop; the application and telemetry
polling do not continue through that path. This allocation requires bench
validation of control and stock reception before vehicle testing.

## Exact integration points

| Integration point | Stock value | Implemented behavior |
| --- | ---: | --- |
| mailbox-26 record at `0x000097BE` | `05 00 00 00` | type 4, DLC 8, build-selected data ID; remains idle while streaming is disabled |
| main-loop call literal at `0x00028090` | `0x00020DFE` | call stock scheduler, poll control, capture, return |
| periodic table entry at `0x00021A70` | `0x000493E8` | latch knock count and mask before the stock consumer clears them |
| knock slice evaluator literal at `0x0004A9C0` | `0x0004A238` | call the stock evaluator, then fold `threshold - metric` of the evaluated channel into its minimum latch |
| HCAN1 SLE1 vector at `0x000203A0` | `0x000C7914` | service mailbox 26 and reproduce mailbox-28 success and abort behavior |
| composed startup wrapper | existing wrapper chain | clear the complete active telemetry RAM allocation and arm the six knock margin latches |
| primary HCAN1 initializer pointer at `0x0002D7FC` | `0x000C338A` | call the stock initializer, preserve its result, then configure mailbox 31 |
| recovery HCAN1 initializer pointer at `0x000C3B10` | `0x000C338A` | restore mailbox 31 after the stock recovery path reinitializes HCAN1 |

The candidate standard ID is `0x6F0`. The ID remains a build parameter in the
range `0x001..0x6FE`, but every page in one build uses the same ID. Eleven
pages fit the four-bit page number, and additional IDs would not reduce bus
occupancy while only one verified physical mailbox is used.

For `0x6F0`, the enabled mailbox record is `04 08 DE 00` because the table
stores `STDID << 5`. Physical mailbox 26 uses control base `0xFFFFDC40`, data
bytes `0xFFFFDC48..0xFFFFDC4F`, and bit `0x0400` in HCAN1 TXPR1, TXACK1,
ABACK1, and MBIMR1.

The control ID is always the data ID plus one. For the default pair, telemetry
uses `0x6F0` and control uses `0x6F1`. Physical mailbox 31 uses control base
`0xFFFFDCE0`, data bytes `0xFFFFDCE8..0xFFFFDCEF`, and bit `0x8000` in HCAN1
RXPR1, RFPR1, MBIMR1, and UMSR1. Its mailbox activity interrupt remains masked;
the main wrapper polls it at the base scheduler boundary.

The table record and the physical mailbox register use different encodings.
The table stores `STDID << 5` for the stock initializer, while mailbox 31
register bytes 0 and 1 store `STDID << 4` directly because byte 1 bits 3 and 2
are RTR and IDE. The default control register word is therefore `0x6F10`.

## Build-time CAN ID checks

Image construction requires both the data ID and the control ID to be below
`0x700`, and rejects either ID when it matches an active stock HCAN1 ROM-table
record of the selected image. The error identifies the data or control ID,
physical mailbox, direction, and ROM record. This applies to disabled-startup
and auto-start configurations. Inactive type-5 records reserve no ID, so
exact-code sibling images retain their own mailbox availability.

The reviewed setup functions use four-byte records containing type, DLC, and
`STDID << 5`. Types 1 and 2 receive; types 3 and 4 transmit. The SH7059 scan
also accepts transmit types `0x23`, `0x53`, `0xA3`, `0xB3`, and `0xC3`.
High-nibble types and zero-based indices above 30 in that scan alias physical
mailbox 1; the additional records participate in collision checks. The existing physical
mailbox-26 anchor locates the table without a separate address registry.

| Layout | Mailbox setup entry | ROM records | Direct initialization IDs |
| --- | --- | ---: | --- |
| `7mfk` | `0x000C2FBE` | 30 | `0x7E8`, `0x7E0`, `0x7D0` |
| `jk00c` | `0x000C8CAE` | 30 | `0x7DF`, `0x7E8`, `0x7E0`, `0x7D0` |
| `jk00d` | `0x000C93EA` | 30 | `0x7DF`, `0x7E8`, `0x7E0`, `0x7D0` |
| `jk78c` | `0x000EA19E` | 30 | `0x7DF`, `0x7E8`, `0x7E0`, `0x7D0` |
| `1nd` | `0x0011322A` | 36 | `0x7DF`, `0x7E8`, `0x7E0`, `0x7D0` |
| `1me3b` | `0x0011EEDA` | 36 | `0x7DF`, `0x7E8`, `0x7E0`, `0x7D0` |

The direct initialization writes use diagnostic IDs, covered by reserving
`0x700..0x7FF`. The wire configuration field has its own numeric range;
the stricter image-construction policy does not change its encoding.
An unreviewed layout or record type refuses telemetry construction. These
checks cover the ECU's ROM mailbox tables and direct initialization writes.
IDs of other vehicle modules require a passive whole-bus capture before
transmission is enabled.

## Coherent capture boundary

The main loop calls the pointer at `0x00028090` while interrupts are masked.
`FUN_00020DFE` performs its snapshot copies and periodic tasks before returning.
The wrapper calls the stock function first and copies all selected sources
immediately afterward without another interrupt-state transition.

All multi-byte values retain ECU big-endian representation. Firmware performs
no engineering conversion. The generated host schema owns placement,
signedness, the scale with the conversion, unit, candidate flag, values,
named bits, or a value packed into a bit range beside named bits that it
states, and the host presentation of each field: the
label, digits, recording group, dashboard panel, description, and live feed
channel. Exact producer source addresses remain only in the firmware manifest
and generated pointer table.

`FUN_000493E8` consumes and clears the knock interval count before the final
capture boundary. The wrapper at periodic entry 65 therefore latches
`0xFFFF2142` and `0xFFFF2150` before calling the stock function. The main
capture includes those latches with the updated timing state.

## Knock margin latches

Slice evaluator `0x0004A238` has one reference in the image, literal
`0x0004A9C0` of `FUN_0004A8D4`, and no `BSR` caller. After the call the caller
reads only registers that it sets again, so the wrapper at `0x000D4600` owns
`r0..r7` and preserves PR alone. It calls the stock evaluator first and then
repeats the stock channel selection: `ROM8[0x8B3D]` bit 3 clear selects
`uint8[0xFFFF11DE]`, otherwise `uint8[0xFFFF2143]`. A channel outside `1..6`
leaves every latch unchanged.

For the evaluated channel the wrapper reads the operands that the evaluator
leaves in RAM, the offset-binary metric at
`int32[0xFFFF21D8 + 4 * (channel - 1)]` and the threshold at
`uint16[0xFFFF2144 + 2 * (channel - 1)]`, and applies the stock comparison
`threshold + 0x80000000 < metric` on unsigned 32-bit values. The margin is
`threshold - metric` in evaluator units. An exceedance yields a negative
margin limited at `-32768`. The signed word at
`0xFFFF5E10 + 2 * (channel - 1)` keeps the minimum margin of its channel, so
a margin of 32767 or more never replaces the idle value `32767`.

The bank builder copies the six latches as context tag 4 and rearms them with
`32767` directly after that copy, inside the same interrupt-masked capture.
The startup wrapper arms them after clearing the telemetry RAM. A published
`32767` therefore reports an interval without an evaluation of the channel or
a margin of 32767 or more. A tag-4 group that the queue replaces, preempts, or
discards before transmission takes its minimums with it; the overrun and abort
counters and the host group accounting expose those intervals.

Stock threshold rows 3 and 5 of table `0x1108E` hold `0xFFFF`. Their channels
are evaluated once per engine cycle like the others, but they publish a value
below `32767` only for a metric above 32768 units, so on these channels
`32767` does not distinguish an interval without an evaluation from an
evaluated margin of 32767 or more. The profile carries no evaluation count or
metric per channel. The 2026-09-21 profile-5 recordings publish `32767` on
both channels in every tag-4 group, including 1,158 groups at 2350 RPM or
more, where every interval holds an evaluation of each channel; registry entry
`knock_margin.vehicle_2026_09_21` holds the result, and
[`../defs/JK08A.knock-detection.md`](../defs/JK08A.knock-detection.md#vehicle-result-of-2026-09-21)
states the metric bounds. The metric has no physical conversion. The window
of channel `c` spans 10..60 degrees after compression TDC of cylinder `c - 1`,
and on the stock path every channel samples the same A/D inputs.

## ROM and RAM layout

The runtime owns `0x000D4280..0x000D6000` inside the audited free ROM region.

| ROM range | Size | Purpose |
| ---: | ---: | --- |
| `0x000D4280..0x000D4340` | 192 | main, knock, and startup wrappers |
| `0x000D4340..0x000D4800` | 1,216 | configuration guard, capture, bank builder, knock margin wrapper at `0x000D4600`, and page request |
| `0x000D4800..0x000D4A70` | 624 | combined SLE1 ISR and bounded queue |
| `0x000D4A70..0x000D4C00` | 400 | dynamic page command handler |
| `0x000D4C00..0x000D4E00` | 512 | 492-byte generated source-pointer table plus erased tail |
| `0x000D4E00..0x000D4E10` | 16 | fail-closed build configuration |
| `0x000D4E10..0x000D5000` | 496 | HCAN1 initialization wrapper, control poller, exact command validator, and shared configuration guard |
| `0x000D5000..0x000D6000` | 4,096 | exclusive erased future ROM reserve |

The active RAM allocation is `0xFFFF5E00..0xFFFF5F90`.

| RAM range | Size | Purpose |
| ---: | ---: | --- |
| `0xFFFF5E00..0xFFFF5E20` | 32 | queue state, runtime enable override, profile, status, counters, knock latches, and the six knock margin words at `0xFFFF5E10..0xFFFF5E1C` |
| `0xFFFF5E20..0xFFFF5E78` | 88 | complete frame bank A |
| `0xFFFF5E78..0xFFFF5ED0` | 88 | complete frame bank B |
| `0xFFFF5ED0..0xFFFF5EE0` | 16 | reserved event state |
| `0xFFFF5EE0..0xFFFF5F00` | 32 | active reserve, cleared at startup |
| `0xFFFF5F00..0xFFFF5F90` | 144 | dynamic page state: active and staged configurations |
| `0xFFFF5F90..0xFFFF6000` | 112 | exclusive future telemetry RAM reserve |

The main path constructs a complete inactive bank before publication. The ISR
never reads a bank that the main path may overwrite.

## Configuration contract

The 16-byte configuration contains:

| Offset | Width | Field |
| ---: | ---: | --- |
| 0 | 2 | magic `0x4354` |
| 2 | 1 | protocol version `2` |
| 3 | 1 | enable byte `0` or `1` |
| 4 | 1 | profile ID `TELEMETRY_PROFILE_ID` |
| 5 | 1 | page count `11` |
| 6 | 1 | tick divisor `1..255` |
| 7 | 1 | reserved zero |
| 8 | 2 | standard CAN ID |
| 10 | 2 | profile CRC16 `TELEMETRY_PROFILE_CRC` |
| 12 | 4 | integrity word `0x54454C32` (`TEL2`) |

The only profile name is `tuning`. `TELEMETRY_PROFILE_ID` and
`TELEMETRY_PROFILE_CRC` are symbols of the generated header
`can-telemetry-identity.h`. Its `TELEMETRY_CONFIGURATION` is the enabled
record of the candidate CAN ID and tick divisor; the default disabled record
differs from it in enable byte 3 alone, which holds `00`.

Firmware validates every field before incrementing the telemetry tick,
touching the queue, or accepting a control command. `can_telemetry_profile.py`
writes the profile ID, page count, and profile CRC into the generated header
`can-telemetry-identity.h`, together with `TELEMETRY_CONFIGURATION`, the
enabled record of the candidate CAN ID and tick divisor. The capture and
control guards include the header and compare against its symbols, which the
source dialect writes as numbers before the static audit and GNU assembly;
the audit requires the symbols and checks the protocol version, profile ID,
page count, and profile CRC of the guards instruction by instruction and
literal by literal against `can-telemetry-profile.toml`. The executable
harness includes the same header and installs `TELEMETRY_CONFIGURATION`. A
wire layout change that moves the CRC therefore reaches the guards and the
fixture through the generator, and the SHA-256 locks of the assembled units
and of the composition hold the gate until they state the new bytes;
`make telemetry-update` derives them, as described under Lock update. The
builder independently
requires mailbox 26 to be a type-4 DLC-8 transmitter for the configured CAN ID.
This mailbox configuration is present even when startup streaming is disabled,
because a later START command must be able to transmit without reinitializing
HCAN1. No frame is requested while the runtime state remains disabled.

The generated JK08A XML and XDF expose byte `0x000D4E03` as `CAN Telemetry at
Startup`. `00` is the default disabled state and `01` starts streaming after
reset. Other values fail closed.

## Runtime control

The control frame is standard 11-bit classical CAN with DLC 8. Its ID is
`data_can_id + 1`. Commands include a four-byte `TEL2` magic, protocol version,
operation, and CRC-16/CCITT-FALSE over the first six bytes:

| Command | Exact payload |
| --- | --- |
| STOP | `54 45 4C 32 02 00 A6 13` |
| START | `54 45 4C 32 02 01 B6 32` |

Runtime state byte `0xFFFF5E0B` uses `0` to follow the ROM startup flag, `1` to
force streaming on, and `2` to force it off. START therefore activates
telemetry even when byte `0x000D4E03` is `00`. It preloads the divider state so
the capture immediately following the poll is due. STOP prevents new captures,
discards a replaceable pending snapshot, and lets an already active 11-frame
group finish coherently. A reset clears the override and restores the ROM flag.

Mailbox 31 uses non-overwrite receive mode. The poller rejects a retained RTR
frame, clears RXPR, RFPR, and UMSR for every consumed or rejected frame, and
accepts only an exact command payload with DLC 8. A DLC-8 frame without the
`TEL2` magic goes to the command handler of the [dynamic page](#dynamic-page).
An invalid producer configuration does not consume the mailbox and cannot
change runtime state.

The executable gate covers STOP, START, and the rejection of invalid control
frames. On the vehicle they remain untested: registry entry
`can_telemetry.schema2_transport_2026_09_22` records that no capture carries a
control frame.

## Wire protocol

All frames use one standard 11-bit CAN ID and DLC 8. Byte 0 is:

```text
byte0 = ((tick16 & 0x0f) << 4) | page_id
```

`page_id` occupies bits 3 through 0. The low four bits of `tick16` occupy bits
7 through 4. Page 0 also carries the complete big-endian `tick16` in bytes 1
and 2. At divisor 1, the header sequence wraps every `163.84 ms`; `tick16`
wraps every `671.08864 s`.

The receiver requires page 0 followed by pages 1 through 10 in order, verifies
the header sequence against `tick16`, and discards incomplete, duplicate,
reordered, or preempted groups. It never combines pages from different groups
or fabricates a missing value.

`tick16` lives in producer RAM and restarts with the controller. The receiver
compares each group with the previous accepted group by tick and by receive
time, and opens a new producer run on a group whose tick the current run cannot
explain:

- a tick that drops back into the opening window `0x0000..0x00FF` from a larger
  value;
- a tick that drops back after a receive pause longer than 0.5 s;
- a tick that steps forward by more than `(elapsed + 1.0 s) / 10.24 ms + 1`
  ticks, where `elapsed` is the receive time since the previous accepted
  group and 1.0 s is the assumed largest host queue delay of a group.
  Interface timestamps leave the queue delay out of `elapsed`. With host
  receive times, a longer queue delay of a group followed by lost groups
  opens a false new run.

A new run restarts the unwrapped tick, counts the restart, and waits for the
next health context before the receiver treats the wire contract as verified
again. A repeated tick, and a backwards step outside the opening window within
0.5 s of the previous group, remain rejected stale groups. A 16-bit wrap keeps
the run because its forward distance stays small, and STOP holds the tick, so
the next tick after a STOP pause of any length stays in the run. A receive
loss while the stream runs lets the tick advance: after a loss of more than
half the tick period, about 335.5 s, the next step reads as a step back and
opens a false new run, and after a loss of more than the full period, about
671 s, it reads as a forward step that drops whole periods from the unwrapped
tick. Without receive
times only the opening window marks a new run. A restart whose first received
tick lies ahead of the last tick of the old run by no more ticks than the
receive pause allows cannot be told from a continuation, and the receiver keeps
that group in the old run. Snapshots of different runs are never adjacent: the
distance across a restart is a gap of unknown length, not a snapshot count.

### Page layout

Pages 0 through 8 are captured at every published snapshot.
Pages 9 and 10 carry the same context tag in byte 1. Tags rotate from 0 through
4. Both pages are transmitted every snapshot, while each tagged field set is
refreshed once per five published snapshots. At divisor 1, the context-field
rate is `19.53125 Hz`.

`can_telemetry_profile.py` renders the tables below from
`can-telemetry-profile.toml`: the bytes, type, exact JK08A source, and scale
of every field. The type states signedness and width, `u` for unsigned and
`s` for signed. A source in active runtime RAM names its owner in
`jk08a-runtime-reservations.toml`.

<!-- telemetry-slots:begin -->
Fixed pages 0 through 8, bytes 1..7:

| Page | Bytes | Field | Type | Source | Scale |
| ---: | ---: | --- | --- | --- | --- |
| 0 | 1..2 | `tick16` | u16 | `can_telemetry` RAM `0xFFFF5E08` | base scheduler ticks |
| 0 | 3..4 | `request_flow_raw` | u16 | ECU RAM `0xFFFF1980` | raw count |
| 0 | 5 | `final_timing_raw` | s8 | ECU RAM `0xFFFF11D4` | raw degBTDC |
| 0 | 6 | `apc_command_raw` | u8 | ECU RAM `0xFFFF2022` | 110 - raw degBTDC |
| 0 | 7 | `fuel_inhibit_mask` | u8 | ECU RAM `0xFFFF22E0` | bits: 0 CYLINDER_1, 1 CYLINDER_2, 2 CYLINDER_3, 3 CYLINDER_4, 4 CYLINDER_5, 5 CYLINDER_6 |
| 1 | 1..2 | `maf_b1_raw` | u16 | ECU RAM `0xFFFF101C` | raw / 200 V |
| 1 | 3..4 | `maf_b2_raw` | u16 | ECU RAM `0xFFFF101E` | raw / 200 V |
| 1 | 5..6 | `maf_total_raw` | u16 | ECU RAM `0xFFFF3852` | raw / 100 g/s |
| 1 | 7 | `normalized_load_raw` | u8 | ECU RAM `0xFFFF102C` | raw * 100 / 128 percent |
| 2 | 1..2 | `bfs_raw` | u16 | ECU RAM `0xFFFF1026` | raw / 2048 ms |
| 2 | 3 | `rolling_launch_phase` | u8 | `rolling_launch` RAM `0xFFFF5D40` | enumeration: 0 IDLE, 1 ACTIVE, 2 COOLDOWN |
| 2 | 4..5 | `injection_0_raw` | u16 | ECU RAM `0xFFFF23C8` | raw / 100 ms |
| 2 | 6..7 | `injection_1_raw` | u16 | ECU RAM `0xFFFF23CA` | raw / 100 ms |
| 3 | 1 | `fuel_learning_permit_b_raw` | u8 | ECU RAM `0xFFFF1457` | bits: 0 BANK_1_COMPOSITE_PERMIT, 1 BANK_2_COMPOSITE_PERMIT |
| 3 | 2 | `fuel_learning_permit_a_raw` | u8 | ECU RAM `0xFFFF1458` | bits: 0 BANK_1_STABILITY_PERMIT, 1 BANK_2_STABILITY_PERMIT |
| 3 | 3 | `ltft_publication_neutral_control_raw` | u8 | ECU RAM `0xFFFF41B5` | bits: 0 NEUTRALIZE_PUBLICATION_AND_RESET_GRID |
| 3 | 4..5 | `torque_transition_state_raw` | u16 | ECU RAM `0xFFFF23C2` | raw count |
| 3 | 6 | `exhaust_cvtc_actual_b1_raw` | u8 | ECU RAM `0xFFFF2324` | raw * 0.5 - 64 degCA |
| 3 | 7 | `telemetry_page_configuration` | u8 | `can_telemetry` RAM `0xFFFF5F00` | ID in bits 0 through 6, group in bit 7 |
| 4 | 1 | `knock_state_snapshot_raw` | u8 | ECU RAM `0xFFFF2467` | bits: 6 DIRECT_DIFFERENCE_ENABLE |
| 4 | 2 | `knock_branch_state_raw` | u8 | ECU RAM `0xFFFF2469` | bits: 7 DIRECT_DIFFERENCE_INHIBIT |
| 4 | 3..4 | `knock_timing_state_raw` | s16 | ECU RAM `0xFFFF121A` | raw / 256 deg |
| 4 | 5 | `knock_surface_state` | u8 | ECU RAM `0xFFFF2466` | bits: 6 HIGH_DETONATION |
| 4 | 6 | `knock_count_latched` | u8 | `can_telemetry` RAM `0xFFFF5E0C` | saturating event count |
| 4 | 7 | `knock_channel_mask_latched` | u8 | `can_telemetry` RAM `0xFFFF5E0D` | six-position bit mask; bit c - 1 is knock channel c |
| 5 | 1..2 | `app1_raw` | u16 | ECU RAM `0xFFFF269E` | raw / 200 V |
| 5 | 3..4 | `app2_raw` | u16 | ECU RAM `0xFFFF26A2` | raw / 200 V |
| 5 | 5..6 | `tps_b1_raw` | u16 | ECU RAM `0xFFFF2756` | raw / 200 V |
| 5 | 7 | `absolute_throttle_raw` | u8 | ECU RAM `0xFFFF1075` | raw * 100 / 255 percent |
| 6 | 1..2 | `tps_b2_raw` | u16 | ECU RAM `0xFFFF285C` | raw / 200 V |
| 6 | 3 | `intake_cvtc_actual_b1_raw` | u8 | ECU RAM `0xFFFF2442` | raw * 0.5 - 64 degCA |
| 6 | 4 | `intake_cvtc_actual_b2_raw` | u8 | ECU RAM `0xFFFF2443` | raw * 0.5 - 64 degCA |
| 6 | 5 | `intake_cvtc_target_raw` | u8 | ECU RAM `0xFFFF2326` | raw * 0.5 - 64 degCA |
| 6 | 6 | `exhaust_cvtc_target_raw` | u8 | ECU RAM `0xFFFF2327` | raw * 0.5 - 64 degCA |
| 6 | 7 | `calculated_load_raw` | u8 | ECU RAM `0xFFFF413E` | raw * 100 / 255 percent |
| 7 | 1..2 | `throttle_request_bounded_raw` | s16 | ECU RAM `0xFFFF19C6` | raw count |
| 7 | 3..4 | `engine_torque_state_raw` | s16 | ECU RAM `0xFFFF18CC` | raw count |
| 7 | 5..6 | `transmission_reduction_state_raw` | u16 | ECU RAM `0xFFFF1866` | raw count |
| 7 | 7 | `telemetry_status` | u8 | `can_telemetry` RAM `0xFFFF5E07` | bit mask |
| 8 | 1..2 | `throttle_target_shared_raw` | u16 | ECU RAM `0xFFFF19B2` | raw count |
| 8 | 3..4 | `throttle_target_channel_0_raw` | u16 | ECU RAM `0xFFFF28BC` | raw * 34285 / 1114112 percent |
| 8 | 5..6 | `throttle_target_channel_1_raw` | u16 | ECU RAM `0xFFFF28BE` | raw * 34285 / 1114112 percent |
| 8 | 7 | `exhaust_cvtc_actual_b2_raw` | u8 | ECU RAM `0xFFFF2325` | raw * 0.5 - 64 degCA |

Context pages 9 and 10, bytes 2..7 after the tag in byte 1:

| Tag | Page | Context | Bytes | Field | Type | Source | Scale |
| ---: | ---: | --- | ---: | --- | --- | --- | --- |
| 0 | 9 | `temperatures_and_b2_trim_terms` | 2 | `coolant_raw` | u8 | ECU RAM `0xFFFF1079` | raw - 50 degC |
| 0 | 9 | `temperatures_and_b2_trim_terms` | 3 | `fuel_temperature_did_source_raw` | u8 | ECU RAM `0xFFFF1074` | raw - 50 degC |
| 0 | 9 | `temperatures_and_b2_trim_terms` | 4..5 | `ltft_learned_b2_raw` | u16 | ECU RAM `0xFFFF2308` | raw / 256 - 100 percent |
| 0 | 9 | `temperatures_and_b2_trim_terms` | 6..7 | `ltft_adjustment_b2_raw` | u16 | ECU RAM `0xFFFF564A` | raw / 256 - 100 percent |
| 0 | 10 | `launch_abort_voltage_and_trim_terms` | 2 | `rolling_launch_abort_reason` | u8 | `rolling_launch` RAM `0xFFFF5D41` | enumeration: 0 NONE, 1 CONFIG_INVALID, 2 MAP_INDEX_INVALID, 3 MAP_DISABLED, 4 SELECTOR_BUSY, 5 FEEDBACK_BUSY, 6 MAIN_PRESSED, 7 BUTTON_RELEASED, 8 BUTTON_INVALID, 9 SPEED_LOW, 10 RPM_LOW, 11 PEDAL_LOW, 12 COOLANT_OUTSIDE, 13 SPEED_FRAME_STALE, 14 TIMEOUT, 15 MAP_REQUEST, 16 STATE_CORRUPT, 17 MAP_CHANGED, 18 MODE_CHANGED, 19 SPEED_HIGH, 20 SPEED_ABOVE_WINDOW, 21 SPEED_BELOW_WINDOW, 22 SPEED_VALUE_INVALID, 23 SPEED_SOURCE_NOT_READY, 24 RPM_INPUT_INVALID, 25 CANCEL_CAPTURE_INVALID |
| 0 | 10 | `launch_abort_voltage_and_trim_terms` | 3 | `battery_voltage_raw` | u8 | ECU RAM `0xFFFF1188` | raw * 0.08 V |
| 0 | 10 | `launch_abort_voltage_and_trim_terms` | 4..5 | `ltft_learned_b1_raw` | u16 | ECU RAM `0xFFFF2306` | raw / 256 - 100 percent |
| 0 | 10 | `launch_abort_voltage_and_trim_terms` | 6..7 | `ltft_adjustment_b1_raw` | u16 | ECU RAM `0xFFFF5648` | raw / 256 - 100 percent |
| 1 | 9 | `short_fuel_trim_cvtc_duty` | 2..3 | `stft_b1_raw` | s16 | ECU RAM `0xFFFF22DC` | raw / 256 - 100 percent |
| 1 | 9 | `short_fuel_trim_cvtc_duty` | 4..5 | `stft_b2_raw` | s16 | ECU RAM `0xFFFF22DE` | raw / 256 - 100 percent |
| 1 | 9 | `short_fuel_trim_cvtc_duty` | 6 | `intake_cvtc_duty_b1_raw` | u8 | ECU RAM `0xFFFF2440` | raw * 39 / 100 percent |
| 1 | 9 | `short_fuel_trim_cvtc_duty` | 7 | `intake_cvtc_duty_b2_raw` | u8 | ECU RAM `0xFFFF2441` | raw * 39 / 100 percent |
| 1 | 10 | `air_oil_temperature_and_af_state` | 2 | `iat_raw` | u8 | ECU RAM `0xFFFF2837` | raw - 50 degC |
| 1 | 10 | `air_oil_temperature_and_af_state` | 3 | `oil_temperature_did_source_raw` | u8 | ECU RAM `0xFFFF2876` | raw - 50 degC |
| 1 | 10 | `air_oil_temperature_and_af_state` | 4..5 | `af_state_factor_raw` | u16 | ECU RAM `0xFFFF22E8` | raw / 16384 ratio |
| 1 | 10 | `air_oil_temperature_and_af_state` | 6..7 | `injection_end_angle_raw` | u16 | ECU RAM `0xFFFF192E` | raw * 2 - 590 degCA |
| 2 | 9 | `long_fuel_trim_map_index_flow` | 2..3 | `ltft_b1_raw` | s16 | ECU RAM `0xFFFF2302` | raw / 256 - 100 percent |
| 2 | 9 | `long_fuel_trim_map_index_flow` | 4..5 | `ltft_b2_raw` | s16 | ECU RAM `0xFFFF2304` | raw / 256 - 100 percent |
| 2 | 9 | `long_fuel_trim_map_index_flow` | 6 | `active_map_index` | u8 | `map_switching` RAM `0xFFFF5D00` | raw + 1; 0 through 4 select Maps 1 through 5, and any other value selects Map 1 |
| 2 | 9 | `long_fuel_trim_map_index_flow` | 7 | `alpha_n_flow_raw` | u8 | ECU RAM `0xFFFF1170` | raw count |
| 2 | 10 | `front_af_and_adjustment_b1` | 2..3 | `front_af_sensor_b1_word_raw` | u16 | ECU RAM `0xFFFF2780` | raw / 200 V |
| 2 | 10 | `front_af_and_adjustment_b1` | 4..5 | `front_af_sensor_b2_word_raw` | u16 | ECU RAM `0xFFFF2782` | raw / 200 V |
| 2 | 10 | `front_af_and_adjustment_b1` | 6..7 | `af_adjustment_b1_raw` | s16 | ECU RAM `0xFFFF45A0` | candidate raw * 0.002 ratio |
| 3 | 9 | `health` | 2 | `protocol_version` | u8 | ROM configuration `0x000D4E02` | identity |
| 3 | 9 | `health` | 3 | `profile_id` | u8 | ROM configuration `0x000D4E04` | identity |
| 3 | 9 | `health` | 4..5 | `profile_crc16` | u16 | ROM configuration `0x000D4E0A` | CRC-16/CCITT-FALSE |
| 3 | 9 | `health` | 6 | `snapshot_overrun_count` | u8 | `can_telemetry` RAM `0xFFFF5E0E` | saturating count |
| 3 | 9 | `health` | 7 | `tx_abort_count` | u8 | `can_telemetry` RAM `0xFFFF5E0F` | saturating count |
| 3 | 10 | `secondary_throttle_and_adjustment_b2` | 2..3 | `secondary_tps_b1_raw` | u16 | ECU RAM `0xFFFF275E` | raw / 200 V |
| 3 | 10 | `secondary_throttle_and_adjustment_b2` | 4..5 | `secondary_tps_b2_raw` | u16 | ECU RAM `0xFFFF2864` | raw / 200 V |
| 3 | 10 | `secondary_throttle_and_adjustment_b2` | 6..7 | `af_adjustment_b2_raw` | s16 | ECU RAM `0xFFFF45A2` | candidate raw * 0.002 ratio |
| 4 | 9 | `knock_margin_channels_1_to_3` | 2..3 | `knock_margin_min_ch1_raw` | s16 | `can_telemetry` RAM `0xFFFF5E10` | threshold minus metric in evaluator units, minimum since the previous capture of this context; 32767 without an evaluation or for a margin of 32767 or more |
| 4 | 9 | `knock_margin_channels_1_to_3` | 4..5 | `knock_margin_min_ch2_raw` | s16 | `can_telemetry` RAM `0xFFFF5E12` | threshold minus metric in evaluator units, minimum since the previous capture of this context; 32767 without an evaluation or for a margin of 32767 or more |
| 4 | 9 | `knock_margin_channels_1_to_3` | 6..7 | `knock_margin_min_ch3_raw` | s16 | `can_telemetry` RAM `0xFFFF5E14` | threshold minus metric in evaluator units, minimum since the previous capture of this context; 32767 without an evaluation or for a margin of 32767 or more |
| 4 | 10 | `knock_margin_channels_4_to_6` | 2..3 | `knock_margin_min_ch4_raw` | s16 | `can_telemetry` RAM `0xFFFF5E16` | threshold minus metric in evaluator units, minimum since the previous capture of this context; 32767 without an evaluation or for a margin of 32767 or more |
| 4 | 10 | `knock_margin_channels_4_to_6` | 4..5 | `knock_margin_min_ch5_raw` | s16 | `can_telemetry` RAM `0xFFFF5E18` | threshold minus metric in evaluator units, minimum since the previous capture of this context; 32767 without an evaluation or for a margin of 32767 or more |
| 4 | 10 | `knock_margin_channels_4_to_6` | 6..7 | `knock_margin_min_ch6_raw` | s16 | `can_telemetry` RAM `0xFFFF5E1A` | threshold minus metric in evaluator units, minimum since the previous capture of this context; 32767 without an evaluation or for a margin of 32767 or more |
<!-- telemetry-slots:end -->

### Fixed pages

The six injection words are calculated software values at `raw / 100 ms`, and
word `i` belongs to cylinder `i + 1` by code. Equality to electrical
injector-open duration is not measured at the injector terminals. The
end-of-injection angle word holds `2 * min(y, 209)` from `FUN_00056BD0`;
`raw * 2` is the delay in crank degrees after the reference tooth of the
scheduled cylinder, and the end of injection lies `raw * 2 - 590` degrees after
intake TDC of the injected cylinder. JK00C, JK00D, JK78C, 1ND, and 1ME3B bind
the word that their homologous stage writes with the same 209-count clamp:
`FFFF1992`, `FFFF1996`, `FFFF192A`, `FFFE89A2`, and `FFFE8946`. They carry the
JK08A chain from the tooth-7 reference with ignition constant `110` to the slot
masks, so the same anchor holds; [`JK08A.fuel.md`](../defs/JK08A.fuel.md) lists
the homologous stages and the 1ND and 1ME3B boundary. The timing fields are software coordinates rather
than an independent crank-referenced spark measurement.

A non-count engineering scale string without the word `candidate` is fixed by code, by ROM constants
against factory limits, or by the ECU's own J1979 declaration: MAF voltage and
airflow, Base Fuel Schedule at `raw / 2048 ms`, the injection words, the
end-of-injection angle, CVTC targets and positions, the intake duty command
and the live duty pair it latches, the exhaust duty words, the four
temperatures, battery voltage, absolute throttle, the pedal and throttle
sensor voltages, the APC command at `110 - raw` degrees BTDC, both final
channel throttle targets at `raw * 34285 / 1114112` percent of throttle opening
above the learned closed position, and the front A/F sensor voltage at
`raw / 200 V`. Engine torque state, the bounded throttle request, the shared
throttle target area, and both column coordinates use `raw count`: a host
storage view separate from a semantic engineering-scale claim. Their
Nm, cm2, and catalog-percent hypotheses remain in the source meanings with
their origins and limits. The gross and net torque states are distinct;
the retained road evidence does not separate 0.08 from 0.1 Nm/count. The
A/F adjustment states retain candidate conversions and occupy signed slots,
because their producers are signed.

The stock VQ37 images program the intake solenoids from 16-bit duty words,
and their intake duty command cells and live duty bytes hold the high byte `x`
of those words, `x * 25 / 64` percent. The wire keeps `raw * 39 / 100 percent`
on every layout; over the byte range the two scales differ by at most 0.16
percentage points, less than half a wire step.
[`JK78C.cvtc.md`](../defs/JK78C.cvtc.md) states the output stage.

The one-bit fields `knock_surface_state`, `knock_branch_state_raw`, and
`ltft_publication_neutral_control_raw` carry the named bit of their 7mfk
source in the wire bit that the hosts decode. A target that keeps that bit
in another bit of its source byte moves it into the wire bit after the
capture builds the fixed pages, and clears the other bits of the byte;
`patches/runtime-bindings.toml` states the source bit of each layout, and a
target that keeps the 7mfk bit sends its source byte unchanged. The LTFT
neutral control field lies on the dynamic page, so its bit moves only while
the page carries its default row with configuration byte 0; the slot bytes of
an installed configuration stay as the capture reads them.

The stream carries the two column coordinates of the tuning surfaces instead
of engine speed, which the stock bus publishes directly: `0x180` bytes 0 and 1
hold `RPM * 8` at `10.24 ms` from serializer `FUN_000C577A`, so a host that
reads the bus reads engine speed without a telemetry slot.
[`JK08A.can.md`](../defs/JK08A.can.md) states that frame.

`FFFF1980` on page 0 is the column coordinate of the requested-torque
conversion surfaces: `FUN_00073948` looks it up from `FFFF1824 = 8192 *
FFFF12A0 / RPM`, an opening area over engine speed, through curve pair
`0x15690` over `0x15500` and `0x156D0` over `0x15540`. `FFFF1170` in context
tag 2 is the column coordinate of Fuel Compensation Main `0xA29A`, the same
opening area over engine speed formed by `FUN_0003B498` through curve pair
`0x15042` and `0x15022`. Byte core `0x26944` compares each column point with
`FFFF1170` directly, so one context byte states the map column the fuel path
is reading. [`JK08A.throttle-control.md`](../defs/JK08A.throttle-control.md)
and [`JK08A.fuel.md`](../defs/JK08A.fuel.md) state both chains.

Normalized load `FFFF102C` is the scheduler snapshot of the Base Fuel Schedule
as a Q7 ratio to reference word `ROM16[0x9534]`: `raw * 100 / 128` percent,
saturated at raw 255, and the column coordinate of the ignition and intake-cam
target maps. The Rolling Launch phase `FFFF5D40` and abort reason `FFFF5D41`
carry the codes of the `Phase` and `AbortReason` enumerations of
`rolling_launch.py`, and active map index `FFFF5D00` selects Maps 1 through 5
with values 0 through 4 and Map 1 with any other value. The front
heated-oxygen-sensor bytes `FFFF22C4/22C5` and timing state `FFFF2023` have no
producer, and the atmospheric byte `FFFF4544` holds a fixed calibration
default because the barometric input is disabled, so none of them is
streamed.

### Rotating context pages

Tag 1 carries the live intake duty pair on page 9 and the intake duty command
pair, its scheduler latch, on page 10, so one capture pass samples both pairs
and a recording compares them byte for byte.

Tag 4 carries six signed words in evaluator units. Each word is the minimum of
`threshold - metric` over the evaluations of its channel since the previous
capture of the tag, and `32767` stands for no evaluation or a margin of 32767
or more. At one evaluation of a channel per engine cycle, every tag-4 interval
at divisor 1 holds an evaluation only above about 2350 rpm.

Schema-dependent conversions stay disabled until page 9 tag 3 reports version
2 and the profile ID and CRC of the generated identity header, or the identity
of the same profile in a frozen host schema that `can-telemetry-history.toml`
binds to a historical endpoint. The reported identity selects the placement of
the dynamic page; the host presents a frozen profile through the fields of the
current one, which carry its fields with the same widths and conversions. A
later mismatch disables conversions again.
Raw values from an otherwise structurally complete group remain available for
diagnosis.

## Dynamic page

Page 3 is the dynamic page of the profile. Bytes 1..6 carry the data of the
active configuration, and byte 7, `telemetry_page_configuration`, carries its
ID in bits 0 through 6 and the group of the snapshot in bit 7. The profile
states the page as `[profile.dynamic]`: the page, the six data bytes, and the
configuration byte offset 7.

Configuration ID 0 is the default: the fixed fields of page 3 in the slot
table above. Startup clears the active telemetry RAM allocation, which
installs it, and the DEFAULT command reinstalls it. Any other configuration
has one or two groups of one to six RAM slots of 1, 2, or 4 bytes. The slots
of a group fill the data bytes in order from byte 1, and the bytes after the
last slot are zero. A two-group configuration alternates its groups per
snapshot, so each group arrives every second snapshot, `48.828125 Hz` at
divisor 1.

### Commands

The control frame of [Runtime control](#runtime-control) carries three page
commands. Bytes 6..7 hold CRC-16/CCITT-FALSE over bytes 0..5. The opcodes
`0xC0..0xC2` differ from `0x54`, the first byte of the `TEL2` magic, so START
and STOP parse unchanged.

| Command | Bytes 0..5 |
| --- | --- |
| DEFAULT | `C0 00 00 00 00 00` |
| SET | `C1 id d a2 a1 a0` |
| COMMIT | `C2 id g n0 n1 00` |

- SET stages slot `(d >> 4) & 7`, below 6, of group `d >> 7`, with width
  `d & 0x0F` at address `0xFF000000 + a2a1a0`, for configuration ID 1 through
  127. A SET with an ID other than the staging ID restarts the staging.
- COMMIT installs the staging ID with `g` groups, 1 or 2, of `n0` and `n1`
  slots, when the staging holds exactly slots `0..n-1` of each group and each
  group fits six bytes. The capture of the same tick uses it.
- The handler rejects a wrong CRC, an unknown opcode, ID 0 or an ID above 127,
  a group, slot, or width out of range, a word or long at an unaligned
  address, an address outside the RAM window, a COMMIT with an ID other than
  the staging ID, and a COMMIT that does not match the staging. A
  rejection consumes the frame, clears the staging, and advances a saturating
  reject counter; the active configuration stays unchanged.

The RAM window is the on-chip RAM of the MCU: `0xFFFF0000..0xFFFFC000` on the
SH7058 targets JK08A, JK00C, JK00D, and JK78C, and `0xFFFE8000..0xFFFFC000` on
the SH7059 targets 1ND0A, 1ND3B, and 1ME3B. HCAN1 and every other peripheral
lie outside it. The commands write telemetry RAM alone. The capture checks
every slot of the active group again before it reads it; a failing slot or a
group wider than six bytes clears the configuration ID, and the page carries
the default.

The dynamic page state occupies `0xFFFF5F00..0xFFFF5F90`: the active ID, the
group count, the next group, the reject counter, the slot counts, the
staged-slot mask, the staging ID, and the active and staged slots of both
groups. A relocated target moves it by its RAM delta.

### Echo and decoding

The ECU consumes at most one control frame per 10.24 ms tick from a mailbox
that does not overwrite, so a host sends the frames of a configuration at
least 20 ms apart. No command has a response frame, and a rejected frame
leaves the active configuration in place. Every configuration change is
echoed in the configuration byte before data under the new ID is decoded:
the decoder places bytes 1..6 of a snapshot by the ID and group that byte 7 of
the same page carries, never by the configuration that a host requested.
A host confirms a request when the page carries its ID.

A snapshot whose configuration byte names an ID that the schema does not
define, a group beyond the groups of its configuration, or nonzero bytes after
the last slot leaves the data bytes of the page undecoded and counts as an
unknown configuration; the other pages decode. A field that the configuration
of a snapshot does not carry is absent from it.

### Host configurations

`can-telemetry-configurations.toml` defines the configurations: the ID,
name, label, status, and groups of slot names of each, and every slot with
its width, signedness, scale, presentation, and JK08A source. A source is a
`[[diagnostic]]` view of `rolling-launch-layout.toml` with an optional byte
offset, a field of the Rolling Launch state record or its extension by its
name in `STATE_FIELDS` of `rolling_launch.py`, whose format fixes the width
and signedness of the slot, or an ECU RAM address with the specification
that describes it. `can_telemetry_profile.py` validates the catalog against
the command rules and the JK08A RAM window and renders the ROM-neutral slot
fields and every configuration into the profile of the schema, and the JK08A
slot addresses and command frames of the current configurations into
`can-telemetry-configurations.json`. A configuration ID names one slot layout
for good: a changed layout takes a new ID, so a recorded trace decodes with a
later catalog. A historical configuration keeps its schema entry for
decoding and has no command frames. The relocated targets have no generated
slot addresses.

The dashboard offers the configurations that have command frames, sends the
frames of a configuration, checks them against the groups of the schema, and
confirms the echo; the MLVLG recorder and the TRC converter hold the slot
fields of every configuration.

## Queue and interrupt behavior

The queue contains one active bank and one replaceable pending bank:

1. An idle transmitter publishes the new bank and requests page 0.
2. A busy transmitter writes the inactive bank and marks it pending.
3. Another capture replaces only the pending bank and increments the saturated
   overrun counter.
4. After an ACK, pending data preempts the remainder of an older active group.
5. After an abort, the active group is discarded and the newest pending group
   starts immediately.
6. Corrupt bank, pending, page-count, or page-index state disables only custom
   transmission.

The host sees preemption as an incomplete group and resynchronizes at the next
page 0. `telemetry_status` latches pending replacement, TX abort, reserved event
overflow, and post-ACK preemption. Status bits clear only after a complete
group carrying the corresponding page succeeds.

The combined SLE1 handler saves `r0..r7` and PR, services mailbox 26, reproduces
the exact stock mailbox-28 TXACK/ABACK and activity behavior, restores the
interrupted state, and executes `RTE`. TXACK has priority over ABACK for each
mailbox, matching the stock handler.

## Rate and bandwidth

`tick_divisor` selects every Nth base capture:

| Divisor | Snapshot rate | Snapshot interval | Wire `tick16` step |
| ---: | ---: | ---: | ---: |
| 1 | 97.65625 Hz | 10.24 ms | 1 |
| 2 | 48.828125 Hz | 20.48 ms | 2 |
| 4 | 24.4140625 Hz | 40.96 ms | 4 |

All eleven pages are constructed and transmitted for every selected snapshot.
Divisor 1 is the intended tuning configuration and preserves every base-rate
knock latch update.

A standard DLC-8 classical-CAN frame occupies 111 bits including intermission
before stuffing. A conservative maximum-stuffing bound is 135 bits. At
`500 kbit/s`, eleven frames at divisor 1 produce `1,074.21875 frames/s`, add
`23.848%..29.004%` theoretical load, and require `2.442..2.970 ms` without
arbitration delay.

The highest recorded endpoint-disabled whole-vehicle average was
`39.889%..48.402%`. Adding the theoretical schema 2 stream gives a planning
average of `63.737%..77.406%`. The corresponding recorded 100 ms peak plus the
full theoretical stream is `67.108%..81.504%`. These sums are planning bounds,
not measurements of schema 2 traffic, and exclude retransmission and error
frames.

Registry entry `can_telemetry.schema2_transport_2026_09_22` measures the
profile 5 stream at divisor 1 in three moving TRC captures of the 2026-09-22
road session, 519.5 s in total. Per capture, the whole-bus average lies within
`63.671%..77.402%` and the highest 100 ms window within `65.600%..79.760%`, so
neither exceeds its planning bound. With PCAN-View error-frame recording
enabled, the captures contain no error, warning, or remote frame. Each of the
44 stock identifiers of the stationary baselines keeps its median period within
0.3 ms, `0x551` at `102.4 ms`, and its longest interval within 1.5 ms of the
baseline maximum. Every group that the capture end does not truncate arrives
complete with a `tick16` step of 1, and page 10 follows page 0 after
3.5..3.6 ms in the median and at most 8.8 ms.

## Evidence and acceptance boundary

The historical schema 1 target-vehicle capture used `0x6F0`, eight frames per
snapshot, and divisor 1. It recorded 35,811 complete groups at 97.599 Hz with
zero tick gaps, schema mismatches, queue status, overrun, abort, warning, or
error records. Whole-bus average load was `57.185%..69.437%`. This establishes
that mailbox 26, the combined ISR design, the selected ID, and the earlier load
level operated successfully in that drive.

Schema 2 changes the configuration identity, header layout, page count, RAM
banks, source table, payload, decoder, and total load. A schema 2 image remains
ineligible for normal vehicle use until a bounded target-vehicle capture shows:

- eleven ordered pages and exact tick continuity;
- version 2 and the generated profile ID and CRC as health identity;
- no sustained incomplete groups, overrun, abort, CAN warning, or CAN error;
- acceptable stock-frame cadence and whole-bus utilization.

The TRC captures of registry entry `can_telemetry.schema2_transport_2026_09_22`
measure the last criterion for profile 5 on the target vehicle; the current
profile has no target-vehicle capture.

The acceptance run does not need a shutdown cycle, active diagnostic session,
DTC comparison, or direct scheduler-slack measurement for this logging use.

## Verification gates

The repository-contained gate independently assembles all injected SH-2E
instructions and proves identity with the tracked payloads before installing
simulator-only high-RAM relocations and stock-function stubs. It executes all
changed entries, relevant branch outcomes, delay slots, call and return paths,
both banks, all pages, every context record, queue boundaries, latest-wins
replacement, preemption, TXACK, ABACK, simultaneous mailbox-26/mailbox-28
flags, both HCAN1 initialization hooks, startup-disabled START, startup-enabled
STOP, divisor restart, invalid payloads, invalid DLC, remote frames, corrupt
configuration, rejection of profile ID 0 and of both IDs adjacent to the
generated one by the capture entry and of the ID below it by the control
receiver, active-group stop, corrupt-state
fail-closed behavior, the byte of each one-bit field with only its source bit
set and with every other bit set, an installed configuration over the LTFT
neutral control byte, a real `TRAPA` exception entry, and the exact ISR
`RTE`.
The dynamic page cases cover the power-up and DEFAULT configuration, SET and
COMMIT of one and two groups, six one-byte slots, the group alternation, the
capture of 1-, 2-, and 4-byte slots, every rejection cause and the saturating
reject counter, both edges of the RAM window and the alignment of words and
longs, START and STOP beside the page commands, and the fallback of a corrupt
slot or slot budget.
The knock margin wrapper runs against a simulator-only evaluator stub that
stores a staged metric and overwrites `r0..r7`, which binds the order of the
stock call and the operand reads. Its cases cover channel 0, a channel above
6, both selector outcomes and the stock selector byte, a positive margin, the
comparison boundary, an exceedance, the saturated exceedance and its edge,
keeping and replacing a lower minimum across the sign boundary, a margin
beyond the signed word, the startup arming, and the rearm behind tag 4 alone.

`can-telemetry-layout.toml` owns the locked software result: the SHA-256,
instruction count, and data-byte count of every assembly unit, the executable
entries of its code regions, and the SHA-256 of the default composition.
`can-telemetry-profile.toml` owns the profile and context counts that the
harness marker states. The verifier takes these values from their owners. It
reports the dynamic case count, the changed bytes, and the declared write set
of the composition, which follow from the sources and are not locked.

This gate proves the bounded software contract. It does not replace physical
CAN, ECU, sensor, or actuator validation.

### Lock update

`can-telemetry-layout.toml` locks every assembly unit by the SHA-256 of its
assembled bytes, its instruction count, and its data-byte count, and locks the
default composition by its SHA-256. After an intentional change of the profile
or of a telemetry source, derive these locks and the payload manifest with:

```sh
make telemetry-update
```

The target first requires `can-telemetry-profile.toml` to match its rendering
from the knowledge base, and the generated tables, schema, identity header,
and slot tables of this specification to match the profile. A stale projection refuses and names its generator:
`uv run kb project patches/can-telemetry-profile.toml` for the profile and
`uv run python patches/can_telemetry_profile.py` for the generated files. The
target then runs
`tools/sh-elf-run/generate-targets.sh --telemetry --update` in the pinned GNU
SH-2E image. The update counts the instructions and data bytes of each unit
source, assembles the units independently, derives the unit and composition
locks from the assembled bytes, and rewrites only those values in the layout.
It then repeats the strict generation against the rewritten layout: the locks,
the static instruction audit, and the composition must hold before the layout
and `can-telemetry-payloads.toml` are replaced. Unchanged inputs leave both
files byte-identical. The update prints every changed lock with its declared
and derived value. The relocated runtime targets assemble the same telemetry
sources, so the target finally regenerates `runtime-target-payloads.toml` with
`tools/sh-elf-run/generate-targets.sh`.

The strict `--telemetry` generator and its `--check` mode never rewrite a lock.
A lock that differs from the assembled bytes refuses and names the update
command. The update does not replace `make verify-firmware`, which executes the
changed entries.

## Artifact inventory

| Artifact | Responsibility |
| --- | --- |
| `can-telemetry-profile.toml` | authoritative wire fields and exact JK08A producer bindings |
| `can_telemetry_profile.py` | producer validator and generator of the pointer table, the neutral host schema, the identity header, and the slot tables of this specification |
| `can-telemetry-schema.json` | generated ROM-neutral strict host contract |
| `can-telemetry-schema-profile9.json` | frozen host contract of profile 9, bound to endpoint `schema2-profile9` of `can-telemetry-history.toml` |
| `can-telemetry-configurations.toml` | host-defined dynamic page configurations and their JK08A slot sources |
| `can_telemetry_configurations.py` | catalog validator and generator of the dynamic page schema entries and JK08A command frames |
| `can-telemetry-configurations.json` | generated JK08A slot addresses and command frames of the configurations |
| `can-telemetry-identity.h` | generated profile ID, page count, CRC, and harness configuration record |
| `can-telemetry-layout.toml` | ROM, RAM, hook, configuration, and reserve contract |
| `can-telemetry-*.s` | wrappers, capture, control receiver, queue, ISR, and generated tables |
| `can-telemetry-payloads.toml` | SHA-locked independently assembled bytes |
| `can_telemetry_locks.py` | unit and composition locks of the layout, derived from the assembled bytes |
| `can_telemetry.py` | fail-closed configuration and mailbox encoding |
| `can_telemetry_compose.py` | deterministic non-flashable composition |
| `apply_can_telemetry.py` | checksum-closing application stage |
| `build_rom.py` | complete three-runtime image composition |
| `../tools/logs/can_telemetry.py` | strict schema 2 decoder |
| `../tools/logs/trc_to_mlg.py` | PEAK TRC to MLVLG converter |
| `../tools/can_dashboard/` | versioned live display and MLVLG recorder |
| `../tools/sh-elf-run/verify_can_telemetry.py` | executable instruction gate |
| `jk08a-runtime-reservations.toml` | cross-runtime ownership and future budgets |
