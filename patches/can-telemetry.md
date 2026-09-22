# Custom CAN telemetry schema 2 and JK08A producer

## Status and objective

This document specifies the ROM-neutral schema 2 wire contract and its exact
JK08A firmware producer. The firmware, generated source-pointer table, strict
host decoder, dashboard, MLVLG recorder, ROM builder, and GNU SH-2E executable
gate use the same profile identity.

The generated host schema contains only transport layout, field semantics, and
profile identity. It contains no ROM name, producer RAM address, physical
mailbox, or patch location. Host tools load that file directly and do not import
the JK08A producer manifest. The schema also carries the frozen host contract
of every retired profile ID, so recordings of a retired profile stay
decodable. The producer binding retains the exact ROM, RAM,
hook, source-address, and mailbox constraints required to build safe firmware.
The profile CRC covers the wire layout alone: protocol version, profile ID,
page count, the page, offset, width, and signedness of every fixed field, and
the page, tag, and ordered widths and signedness of every context. ROM
identity, source addresses, producer storage kinds, field names, context
names, and scale strings are outside it, so a renamed field or a restated
scale keeps the CRC and the firmware bytes. The profile ID states which
quantity each slot carries: a slot that carries a different quantity takes a
new profile ID, and the producer test suite pins one digest of the
slot-to-field assignment per profile ID. Two producers implementing the same
placement, widths, signedness, contexts, profile ID, and protocol version
therefore publish the same wire identity.

The endpoint is disabled by default. The complete software gate passes, and
three road drives on 2026-08-26 accepted schema 2 transport and channel
coverage. Those drives carried profile 1, the recording of 2026-09-17 carried
profile 3, and the road session of 2026-09-21 in registry entry
`can_telemetry.schema2_profile5_drive_2026_09_21` carried profile 5. The road
session of 2026-09-22 in registry entry
`can_telemetry.schema2_profile5_drive_2026_09_22` carried the same profile,
and its TRC captures measure the whole-bus load of the stream. The current
profile 6 sends the same eleven DLC-8 frames per snapshot and has no vehicle
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
  -> poll physical mailbox 31 for an exact START or STOP command
  -> coherent capture into inactive 88-byte bank
  -> atomic active/pending publication
  -> eleven DLC-8 frames on one standard CAN ID
  -> HCAN1 physical mailbox 26
  -> combined SLE1 completion handler
  -> next page or newest pending snapshot
```

The implementation preserves the stock CAN transmit scan, stock serializers,
all stock receive mailboxes, and the complete mailbox-28 SLE1 behavior. It
converts stock-inactive mailbox 31 into a polled receive mailbox after every
primary or recovery HCAN1 initialization.

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
range `0x001..0x7FE`, but every page in one build uses the same ID. Eleven
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

## Coherent capture boundary

The main loop calls the pointer at `0x00028090` while interrupts are masked.
`FUN_00020DFE` performs its snapshot copies and periodic tasks before returning.
The wrapper calls the stock function first and copies all selected sources
immediately afterward without another interrupt-state transition.

All multi-byte values retain ECU big-endian representation. Firmware performs
no engineering conversion. The generated host schema owns placement,
signedness, scale, and candidate semantic labels. Exact producer source
addresses remain only in the firmware manifest and generated pointer table.

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
| `0x000D4800..0x000D4C00` | 1,024 | combined SLE1 ISR and bounded queue |
| `0x000D4C00..0x000D4E00` | 512 | 492-byte generated source-pointer table plus erased tail |
| `0x000D4E00..0x000D4E10` | 16 | fail-closed build configuration |
| `0x000D4E10..0x000D5000` | 496 | HCAN1 initialization wrapper, control poller, exact command validator, and shared configuration guard |
| `0x000D5000..0x000D6000` | 4,096 | exclusive erased future ROM reserve |

The active RAM allocation is `0xFFFF5E00..0xFFFF5F00`.

| RAM range | Size | Purpose |
| ---: | ---: | --- |
| `0xFFFF5E00..0xFFFF5E20` | 32 | queue state, runtime enable override, profile, status, counters, knock latches, and the six knock margin words at `0xFFFF5E10..0xFFFF5E1C` |
| `0xFFFF5E20..0xFFFF5E78` | 88 | complete frame bank A |
| `0xFFFF5E78..0xFFFF5ED0` | 88 | complete frame bank B |
| `0xFFFF5ED0..0xFFFF5EE0` | 16 | reserved event state |
| `0xFFFF5EE0..0xFFFF5F00` | 32 | active reserve, cleared at startup |
| `0xFFFF5F00..0xFFFF6000` | 256 | exclusive future telemetry RAM reserve |

The main path constructs a complete inactive bank before publication. The ISR
never reads a bank that the main path may overwrite.

## Configuration contract

The 16-byte configuration contains:

| Offset | Width | Field |
| ---: | ---: | --- |
| 0 | 2 | magic `0x4354` |
| 2 | 1 | protocol version `2` |
| 3 | 1 | enable byte `0` or `1` |
| 4 | 1 | profile ID `6` |
| 5 | 1 | page count `11` |
| 6 | 1 | tick divisor `1..255` |
| 7 | 1 | reserved zero |
| 8 | 2 | standard CAN ID |
| 10 | 2 | profile CRC16 `0xF14E` |
| 12 | 4 | integrity word `0x54454C32` (`TEL2`) |

The only profile name is `tuning`. The default disabled bytes are
`43 54 02 00 06 0B 01 00 06 F0 F1 4E 54 45 4C 32`.

Firmware validates every field before incrementing the telemetry tick,
touching the queue, or accepting a control command. The protocol version,
profile ID, page count, and profile CRC the capture and control guards compare
against are checked instruction by instruction and literal by literal against
`can-telemetry-profile.toml`, and the executable gate requires the harness
configuration fixture to equal the configuration record the same manifest
produces. A wire layout change that moves the CRC therefore fails the gate
until both the firmware guards and the fixture carry the new identity. The
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
accepts only an exact command payload with DLC 8. An invalid producer
configuration does not consume the mailbox and cannot change runtime state.

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

`tick16` lives in producer RAM and restarts with the controller, so a tick that
drops back into the opening window `0x0000..0x00FF` from a larger value marks a
new producer run rather than a stale group. The receiver opens a new run there,
restarts the unwrapped tick, counts the restart, and waits for the next health
context before it treats the wire contract as verified again. A backwards step
that lands outside that window remains a rejected stale group, and a 16-bit
wrap keeps the run because its forward distance stays small. Snapshots of
different runs are never adjacent: the distance across a restart is a gap of
unknown length, not a snapshot count.

### Fixed pages

Pages 0 through 8 are captured at every published snapshot.

| Page | Fields and exact sources |
| ---: | --- |
| 0 | `tick16`; `rpm_raw` `FFFF11F4`; `final_timing_raw` `FFFF11D4`; `apc_command_raw` `FFFF2022`; `fuel_inhibit_mask` `FFFF22E0` |
| 1 | `maf_b1_raw` `FFFF101C`; `maf_b2_raw` `FFFF101E`; `maf_total_raw` `FFFF3852`; `normalized_load_raw` `FFFF102C` |
| 2 | `bfs_raw` `FFFF1026`; `rolling_launch_phase` `FFFF5D40`; `injection_0_raw` `FFFF23C8`; `injection_1_raw` `FFFF23CA` |
| 3 | `injection_2_raw` `FFFF23CC`; `injection_3_raw` `FFFF23CE`; `injection_4_raw` `FFFF23D0`; `telemetry_status` |
| 4 | `injection_5_raw` `FFFF23D2`; `knock_timing_state_raw` `FFFF121A`; `knock_surface_state` `FFFF2466`; latched knock count and channel mask |
| 5 | `app1_raw` `FFFF269E`; `app2_raw` `FFFF26A2`; `tps_b1_raw` `FFFF2756`; `absolute_throttle_raw` `FFFF1075` |
| 6 | `tps_b2_raw` `FFFF285C`; intake actual B1/B2 `FFFF2442/2443`; intake target `FFFF2326`; exhaust target `FFFF2327`; calculated load `FFFF413E` |
| 7 | bounded throttle request `FFFF19C6`; engine torque state `FFFF18CC`; end-of-injection angle word `FFFF192E`; exhaust actual B1 `FFFF2324` |
| 8 | shared throttle target `FFFF19B2`; channel targets `FFFF28BC/28BE`; exhaust actual B2 `FFFF2325` |

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

A scale string without the word `candidate` is fixed by code, by ROM constants
against factory limits, or by the ECU's own J1979 declaration: MAF voltage and
airflow, Base Fuel Schedule at `raw / 2048 ms`, the injection words, the
end-of-injection angle, CVTC targets and positions, the intake duty command
and the live duty pair it latches, the exhaust duty words, the four
temperatures, battery voltage, absolute throttle, the pedal and throttle
sensor voltages, the APC command at `110 - raw` degrees BTDC, the
ignition-timing adjustment `FFFF564C` in degrees, both final channel throttle
targets at `raw * 34285 / 1114112` percent of throttle opening above the
learned closed position, and the front A/F sensor voltage at `raw / 200 V`. Engine torque state, the bounded throttle
request, the shared throttle target area, and both A/F adjustment states keep
candidate conversions. The A/F adjustment words and the ignition-timing
adjustment `FFFF564C` occupy signed slots, because their producers are
signed.

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

Pages 9 and 10 carry the same context tag in byte 1. Tags rotate from 0 through
4. Both pages are transmitted every snapshot, while each tagged field set is
refreshed once per five published snapshots. At divisor 1, the context-field
rate is `19.53125 Hz`.

| Tag | Page 9 bytes 2..7 | Page 10 bytes 2..7 |
| ---: | --- | --- |
| 0 | coolant `FFFF1079`, IAT `FFFF2837`, fuel/oil diagnostic sources `FFFF1074/2876`, Q14 A/F factor `FFFF22E8` | Rolling Launch abort reason `FFFF5D41`, battery `FFFF1188`, LTFT learned B1 `FFFF2306`, LTFT adjustment B1 `FFFF5648` |
| 1 | STFT B1/B2 `FFFF22DC/22DE`, low-resolution intake duty B1/B2 `FFFF2440/2441` | high-resolution exhaust duty B1/B2 `FFFF1AAC/1AAE`, intake duty commands B1/B2 `FFFF23B4/23B5` |
| 2 | LTFT B1/B2 `FFFF2302/2304`, active map index `FFFF5D00`, ignition-timing adjustment `FFFF564C` | front A/F words `FFFF2780/2782`, A/F adjustment B1 `FFFF45A0` |
| 3 | protocol version, profile ID, profile CRC, saturated overrun and abort counters | secondary throttle B1/B2 `FFFF275E/2864`, A/F adjustment B2 `FFFF45A2` |
| 4 | minimum knock margin of channels 1 to 3, latches `FFFF5E10/5E12/5E14` | minimum knock margin of channels 4 to 6, latches `FFFF5E16/5E18/5E1A` |

Tag 1 carries the live intake duty pair on page 9 and the intake duty command
pair, its scheduler latch, on page 10, so one capture pass samples both pairs
and a recording compares them byte for byte.

Tag 4 carries six signed words in evaluator units. Each word is the minimum of
`threshold - metric` over the evaluations of its channel since the previous
capture of the tag, and `32767` stands for no evaluation or a margin of 32767
or more. At one evaluation of a channel per engine cycle, every tag-4 interval
at divisor 1 holds an evaluation only above about 2350 rpm.

Schema-dependent conversions stay disabled until page 9 tag 3 reports version
2 and a profile ID with the CRC that the host schema declares for it: current
profile 6 with CRC `0xF14E`, or retired profile 5 with CRC `0xE144`, whose
frozen contract decodes the fields of its recordings. A later mismatch disables
conversions again.
Raw values from an otherwise structurally complete group remain available for
diagnosis.

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
- version 2, profile ID 6, and CRC `0xF14E` health identity;
- no sustained incomplete groups, overrun, abort, CAN warning, or CAN error;
- acceptable stock-frame cadence and whole-bus utilization.

The TRC captures of registry entry `can_telemetry.schema2_transport_2026_09_22`
measure the last criterion for profile 5 on the target vehicle; profile 6 has
no target-vehicle capture.

The acceptance run does not need a shutdown cycle, active diagnostic session,
DTC comparison, or direct scheduler-slack measurement for this logging use.

## Verification gates

The repository-contained gate independently assembles all injected SH-2E
instructions and proves identity with the tracked payloads before installing
simulator-only high-RAM relocations and stock-function stubs. It executes all
changed entries, relevant branch outcomes, delay slots, call and return paths,
both banks, all pages, all ten context records, queue boundaries, latest-wins
replacement, preemption, TXACK, ABACK, simultaneous mailbox-26/mailbox-28
flags, both HCAN1 initialization hooks, startup-disabled START, startup-enabled
STOP, divisor restart, invalid payloads, invalid DLC, remote frames, corrupt
configuration, rejection of profile IDs 0, 5, and 7 by the capture entry and of
profile ID 5 by the control receiver, active-group stop, corrupt-state
fail-closed behavior, a real `TRAPA` exception entry, and the exact ISR `RTE`.
The knock margin wrapper runs against a simulator-only evaluator stub that
stores a staged metric and overwrites `r0..r7`, which binds the order of the
stock call and the operand reads. Its cases cover channel 0, a channel above
6, both selector outcomes and the stock selector byte, a positive margin, the
comparison boundary, an exceedance, the saturated exceedance and its edge,
keeping and replacing a lower minimum across the sign boundary, a margin
beyond the signed word, the startup arming, and the rearm behind tag 4 alone.

The locked software result is:

- 720 injected instructions and 770 data bytes;
- eleven executable entries and 78 dynamic telemetry cases;
- composition SHA-256
  `567f7e67166cd87ddbc99e33aafde292598a08887960bb27b3c50e78459a8adb`;
- 1,922 changed bytes inside a 3,488-byte declared write set.

This gate proves the bounded software contract. It does not replace physical
CAN, ECU, sensor, or actuator validation.

## Artifact inventory

| Artifact | Responsibility |
| --- | --- |
| `can-telemetry-profile.toml` | authoritative wire fields and exact JK08A producer bindings |
| `can_telemetry_profile.py` | producer validator, pointer-table generator, and neutral host-schema generator |
| `can-telemetry-schema.json` | generated ROM-neutral strict host contract |
| `can-telemetry-layout.toml` | ROM, RAM, hook, configuration, and reserve contract |
| `can-telemetry-*.s` | wrappers, capture, control receiver, queue, ISR, and generated tables |
| `can-telemetry-payloads.toml` | SHA-locked independently assembled bytes |
| `can_telemetry.py` | fail-closed configuration and mailbox encoding |
| `can_telemetry_compose.py` | deterministic non-flashable composition |
| `apply_can_telemetry.py` | checksum-closing application stage |
| `build_rom.py` | complete three-runtime image composition |
| `../tools/logs/can_telemetry.py` | strict schema 2 decoder |
| `../tools/logs/trc_to_mlg.py` | PEAK TRC to MLVLG converter |
| `../tools/can_dashboard/` | versioned live display and MLVLG recorder |
| `../tools/sh-elf-run/verify_can_telemetry.py` | executable instruction gate |
| `jk08a-runtime-reservations.toml` | cross-runtime ownership and future budgets |
