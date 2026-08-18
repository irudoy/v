# JK08A custom CAN telemetry design

## Status and objective

This document specifies the implemented software endpoint. The tracked source,
layout, generated tables, SHA-locked payloads, host decoder, unified builder,
and independent GNU SH-2E executable gate are complete. Target-vehicle testing
passes for `wide54`, divisor 1, and standard ID `0x6F0` in the recorded moving
load and stationary contexts. The endpoint remains disabled by default, and a
hardware result does not authorize flashing another image. Concrete image and
capture identities are represented only by hashes in `hardware-results.toml`.

The objective is a coherent, loss-detectable tuning stream over stock HCAN1
without diagnostic polling. The receiver is passive. The ECU firmware owns
sampling, event latching, framing, and transmission.

The maximum useful periodic rate is the natural `FUN_00020DFE` cadence:
`204800 / Pphi` seconds. Passive vehicle timestamps establish
`Pphi = 20 MHz`, so the measured cadence is `10.24 ms` or `97.65625 Hz`.
Faster transport of the same scheduler-owned values would duplicate samples.
Event producers that run faster than this cadence require counters, bitmaps,
or peak latches instead of a faster general snapshot.

## Architecture

```text
main-loop gate
  -> stock FUN_00020DFE and its 124 periodic tasks
  -> coherent telemetry capture
  -> inactive 64-byte frame bank
  -> atomic active/pending publication
  -> HCAN1 physical mailbox 26
  -> SLE1 completion wrapper
  -> next page or newest pending snapshot
```

The design preserves the stock CAN transmit scan, the stock serializers, all
stock receive mailboxes, and the stock mailbox-28 SLE1 behavior.

## Exact integration points

| Integration point | Stock value | Designed behavior |
| --- | ---: | --- |
| mailbox-26 record at `0x000097BE` | `05 00 00 00` | type 4, DLC 8, build-selected unused standard ID |
| main-loop call literal at `0x00028090` | `0x00020DFE` | wrapper calls stock `0x00020DFE`, captures, then returns |
| periodic table entry at `0x00021A70` | `0x000493E8` | wrapper latches knock count/mask before stock coordinator clears the count |
| HCAN1 SLE1 vector word at `0x000203A0` | `0x000C7914` | combined ISR handles mailbox 26, reproduces mailbox-28 behavior, and executes `RTE` |
| composed startup wrapper | existing wrapper chain | explicitly clears telemetry RAM state |

The mailbox ID is a build parameter. `0x6F0` is the disabled default and the
hardware-tested ID for the current `wide54`, divisor-1 result. It is numerically
above the highest normal stock ECM broadcast ID `0x6E2` and therefore has lower
arbitration priority than every normal stock ECM broadcast. It is absent from
363,923 endpoint-disabled frames spanning startup, idle, stationary controls,
and stationary Rolling Launch trials. A subsequent moving-load capture with
the endpoint enabled contains 286,493 valid `0x6F0` frames without a schema,
queue, warning, or error result. This evidence accepts `0x6F0` for the current
tuning-telemetry use. For this ID, the mailbox record is `04 08 DE 00` because
the table stores `STDID << 5`.

Physical mailbox 26 uses control base `0xFFFFDC40`, data bytes
`0xFFFFDC48..0xFFFFDC4F`, and bit `0x0400` in HCAN1 TXPR1, TXACK1, ABACK1,
and MBIMR1.

## Coherent capture boundary

The main loop enables interrupts at `0x00027EEC`, waits for
`0xFFFF84B9.bit2`, and calls the pointer stored at `0x00028090`.
`FUN_00020DFE` masks interrupts, performs its snapshot copies, calls all 124
periodic tasks, and returns before the main loop re-enables interrupts through
`FUN_00027AA2`.

The telemetry wrapper therefore calls stock `FUN_00020DFE` first and copies
all selected sources immediately afterward. No additional interrupt-mask
transition is required. The copy extends an existing interrupt-disabled
region, so its instruction count and measured duration are hardware gates.

All multi-byte sources are copied in ECU big-endian representation. The
firmware performs no engineering-unit conversion. Scaling and physical names
belong to the generated host schema, where evidence levels can be retained.

### Knock event phase

`FUN_0004A238` sets `0xFFFF24C2.bit6` for the current threshold exceedance,
updates per-cylinder bitmap `0xFFFF2150`, and saturating-increments event count
`0xFFFF2142`. Periodic-table entry 65 calls `FUN_000493E8`, which consumes and
clears the count before the final snapshot boundary.

A direct post-`FUN_00020DFE` read of `0xFFFF2142` would therefore normally
observe zero. The wrapper at `0x00021A70` copies the count and bitmap into
telemetry-owned latches before calling stock `FUN_000493E8`. The final capture
uses those latches together with the updated timing state. This hook preserves
the stock call and clear order.

## ROM and RAM layout

The telemetry runtime owns `0x000D4280..0x000D6000` inside the audited free ROM
region. Active schema-1 bytes are contiguous through `0x000D4E10`; the
remaining 4,592 bytes are an erased, exclusive future reserve.

| ROM range | Size | Purpose |
| ---: | ---: | --- |
| `0x000D4280..0x000D4340` | 192 | main, knock, and startup wrappers |
| `0x000D4340..0x000D4800` | 1,216 | capture, bank build, and page request |
| `0x000D4800..0x000D4C00` | 1,024 | combined SLE1 ISR and queue completion |
| `0x000D4C00..0x000D4E00` | 512 | generated source-pointer tables |
| `0x000D4E00..0x000D4E10` | 16 | fail-closed build configuration |
| `0x000D4E10..0x000D6000` | 4,592 | exclusive future ROM reserve |

The active half-open allocation is `0xFFFF5E00..0xFFFF5F00`. It lies within
the audited `0xFFFF5D00..0xFFFF7000` free range and has no direct exact-ROM
xref in the current census. The cross-runtime ledger reserves the adjacent
`0xFFFF5F00..0xFFFF6000` exclusively for future telemetry revisions and checks
it against every active and future owner.

| Range | Size | Purpose |
| ---: | ---: | --- |
| `0xFFFF5E00..0xFFFF5E20` | 32 | state, counters, profile, and event latches |
| `0xFFFF5E20..0xFFFF5E60` | 64 | complete frame bank A |
| `0xFFFF5E60..0xFFFF5EA0` | 64 | complete frame bank B |
| `0xFFFF5EA0..0xFFFF5EE0` | 64 | event accumulators or a future bounded event ring |
| `0xFFFF5EE0..0xFFFF5F00` | 32 | reserved, cleared at startup |

| Future range | Size | Purpose |
| ---: | ---: | --- |
| `0xFFFF5F00..0xFFFF6000` | 256 | exclusive future RAM reserve; unused by schema 1 |

Each frame bank contains eight ready-to-copy eight-byte CAN payloads. The
snapshot wrapper builds a complete inactive bank before publishing it. The
interrupt handler never reads a bank that the main path may overwrite.

## Queue policy

The queue has one active bank and one replaceable pending bank:

1. If TX is idle, a new capture becomes active and page 0 is requested.
2. If TX is active, the inactive bank receives the newest capture and becomes
   pending.
3. A later capture overwrites an already pending bank and increments
   `snapshot_overrun`. This is a latest-wins queue, not a backlog.
4. After every successful page transmission, a newer pending snapshot
   preempts the untransmitted tail of the active snapshot. The receiver
   discards the resulting incomplete older group.
5. Without a pending snapshot, the ISR requests the next page. Completion of
   the last configured page makes TX idle.
6. An ABACK abandons the active group, increments `tx_abort`, and starts the
   newest pending group if present.

The firmware never waits for TX completion in the main loop and never creates
an unbounded queue. HCAN automatic retransmission remains enabled. A lost
arbitration or bus error leaves TXPR set; no new page is requested until the
controller reports completion. The design does not use TX cancellation.

## SLE1 combined ISR

The stock SLE1 ISR at `0x000C7914` handles only physical mailbox 28, bit
`0x1000`, and owns the exception return. Calling it with `JSR` is invalid.
An indirect tail jump would consume a general register whose interrupted entry
value the stock prologue must preserve. The implemented vector target therefore
uses one combined ISR that:

1. save every register and special register it modifies;
2. check mailbox-26 bit `0x0400` in TXACK1 and ABACK1;
3. clear a handled flag by writing one to the corresponding register;
4. clear HCAN1 IRR bit 8 by writing `0x0100` to `0xFFFFD808`;
5. advance or abandon the bounded telemetry queue;
6. reproduce the complete stock mailbox-28 TXACK and ABACK body, including the
   success-only call to `0x000C6B68`;
7. restore `r0..r7`, PR, and the original exception stack; and
8. execute `RTE` with its delay-slot `NOP`.

If mailbox 26 and mailbox 28 are both pending, the combined handler services
both during the same exception path. TXACK has the same priority over ABACK as
the stock mailbox-28 handler. TXACK1 and ABACK1 remain write-one-to-clear
registers; each path writes only its mailbox mask.

## Wire protocol

All frames use one build-selected standard 11-bit CAN ID and DLC 8. Byte 0 is
the page header:

```text
byte0 = ((tick16 & 0x1f) << 3) | page_id
```

`page_id` occupies bits 2 through 0. The low five bits of `tick16` occupy bits
7 through 3. Page 0 carries the complete big-endian `tick16` in bytes 1 and 2.
At the candidate cadence, the five-bit sequence wraps every `327.68 ms` and
`tick16` wraps every `671.08864 s`.

The receiver must require page 0, verify that `tick16 & 0x1f` equals the page
header sequence, require strictly increasing page IDs, and discard every
incomplete group. It unwraps `tick16` modulo 65536. It must not interpolate a
missing page or combine pages from different groups.

### Core pages

Pages 0 through 4 form the stable `core32` profile. They carry 32 source bytes
plus one telemetry status byte.

| Page | Bytes | Field | Exact source or origin |
| ---: | ---: | --- | --- |
| 0 | 1..2 | `tick16` | telemetry state |
| 0 | 3..4 | `rpm_raw` | `0xFFFF11F4`, `RPM = raw * 12.5` |
| 0 | 5 | `final_timing_raw` | signed byte `0xFFFF11D4` |
| 0 | 6 | `apc_command_raw` | `0xFFFF2022` |
| 0 | 7 | `fuel_inhibit_mask` | `0xFFFF22E0` |
| 1 | 1..2 | `maf_b1_raw` | `0xFFFF101C` |
| 1 | 3..4 | `maf_b2_raw` | `0xFFFF101E` |
| 1 | 5..6 | `maf_total_raw` | `0xFFFF3852` |
| 1 | 7 | `af_b1_raw` | `0xFFFF22C4` |
| 2 | 1..2 | `bfs_raw` | `0xFFFF1026` |
| 2 | 3 | `af_b2_raw` | `0xFFFF22C5` |
| 2 | 4..5 | `injection_0_raw` | `0xFFFF23C8` |
| 2 | 6..7 | `injection_1_raw` | `0xFFFF23CA` |
| 3 | 1..2 | `injection_2_raw` | `0xFFFF23CC` |
| 3 | 3..4 | `injection_3_raw` | `0xFFFF23CE` |
| 3 | 5..6 | `injection_4_raw` | `0xFFFF23D0` |
| 3 | 7 | `telemetry_status` | telemetry latches |
| 4 | 1..2 | `injection_5_raw` | `0xFFFF23D2` |
| 4 | 3..4 | `knock_timing_state_raw` | `0xFFFF121A` |
| 4 | 5 | `knock_surface_state` | `0xFFFF2466` |
| 4 | 6 | `knock_count_latched` | pre-`0x000493E8` latch of `0xFFFF2142` |
| 4 | 7 | `knock_channel_mask_latched` | pre-`0x000493E8` latch of `0xFFFF2150` |

Injection channels remain numbered 0 through 5. Static code does not prove
their physical cylinder order or that `0xFFFF23C8..0xFFFF23D3` is the final
electrical injector-open duration. `0xFFFF2022` is a software command, not a
measured spark angle.

On the stock normal path, `final_timing_raw = 110 - apc_command_raw`.
Rolling Launch inserts its late override after the final stock coordinate is
written and before the APC scheduler consumes the command. During that
override, `final_timing_raw` therefore remains the upstream stock coordinate,
while `apc_command_raw` is the effective software command. Neither field is a
measurement of physical crankshaft timing.

`telemetry_status` is latched until a complete group carrying it succeeds:

| Bit | Meaning |
| ---: | --- |
| 0 | at least one pending snapshot was replaced |
| 1 | at least one telemetry TX abort occurred |
| 2 | at least one event accumulator overflowed |
| 3 | an active group was preempted after a page ACK |
| 4..7 | reserved, transmitted as zero |

### Wide pages

The `wide54` profile adds pages 5 through 7. Pages 5 and 6 are sampled at every
snapshot boundary.

| Page | Bytes | Field | Exact source |
| ---: | ---: | --- | --- |
| 5 | 1..2 | `app1_raw` | `0xFFFF269E` |
| 5 | 3..4 | `app2_raw` | `0xFFFF26A2` |
| 5 | 5..6 | `tps_b1_raw` | `0xFFFF2756` |
| 5 | 7 | `absolute_throttle_raw` | `0xFFFF1075` |
| 6 | 1..2 | `tps_b2_raw` | `0xFFFF285C` |
| 6 | 3 | `intake_cvtc_actual_b1_raw` | `0xFFFF2442` |
| 6 | 4 | `intake_cvtc_actual_b2_raw` | `0xFFFF2443` |
| 6 | 5 | `intake_cvtc_target_b1_raw` | `0xFFFF2326` |
| 6 | 6 | `intake_cvtc_target_b2_raw` | `0xFFFF2327` |
| 6 | 7 | `calculated_load_raw` | `0xFFFF413E` |

Page 7 uses byte 1 as a context tag and rotates four regular contexts. One
context is therefore sampled at one quarter of the snapshot rate. A build may
pin one context instead when its fields need the full snapshot rate.

| Tag | Bytes 2..7 |
| ---: | --- |
| `0x00` | coolant `0xFFFF1079`, IAT `0xFFFF2837`, raw DID sources `0xFFFF1074` and `0xFFFF2876`, full A/F factor `0xFFFF22E8` |
| `0x01` | full STFT B1 `0xFFFF22DC`, full STFT B2 `0xFFFF22DE`, intake CVTC duty B1/B2 `0xFFFF2440/41` |
| `0x02` | full LTFT B1 `0xFFFF2302`, full LTFT B2 `0xFFFF2304`, timing-state bytes `0xFFFF2023` and `0xFFFF564C` |
| `0x03` | protocol version, profile ID, profile CRC16, saturated overrun count, saturated abort count |

The exact DID pointer table binds `0xFFFF1074` and `0xFFFF2876`; their fuel-
temperature and oil-temperature names and physical transforms remain
diagnostic-evidence claims. The host schema must preserve that distinction.

Tags `0x80..0xFF` are reserved for an event aggregate and preempt one regular
context when present:

| Byte | Event field |
| ---: | --- |
| 1 | `0x80 | event_type` |
| 2..3 | event `tick16` |
| 4 | channel or cylinder bitmap |
| 5..6 | event raw or peak word |
| 7 | saturating event count |

Tags `0x80..0xFF` and the generic event aggregate are reserved for a later
schema. Schema 1 implements only the regular contexts and the dedicated knock
count/mask latches in core page 4. The current decoder rejects unknown context
tags. A future high-rate producer must aggregate within one snapshot interval
rather than enqueue one CAN record per combustion event.

## Generated profile contract

`can-telemetry-profile.toml` is the tracked declarative profile source.
`can_telemetry_profile.py` generates both fixed SH-2E source pointers and the
host decoder schema. Runtime arbitrary-address interpretation is not part of
the firmware.

The generator must validate:

- source address and width against an explicit side-effect-free RAM allowlist;
- byte order and signedness;
- no field split across pages;
- page count from 1 through 8;
- tick divisor and expected load;
- profile ID and CRC16 over the ordered wire schema;
- mailbox ID range and exact `STDID << 5` encoding; and
- overlap with every composed RAM, ROM, hook, and vector claim.

The runtime transmits raw values only. A manifest binds ROM identity, CAN ID,
tick divisor, page count, profile ID, and schema CRC. `wide54` conversion
requires a matching in-band health context. `core32` has no context page, so
its decoder binding is the explicitly selected generated schema and build
manifest.

Before incrementing the telemetry tick or touching the queue, the runtime
validates magic, schema version, enable byte, profile ID, page count, nonzero
divisor, reserved byte, CAN ID range `1..0x7FF`, exact profile CRC16, and the
integrity word. The builder independently requires the mailbox record to encode
the same CAN ID and enable state.

## Profile and divisor semantics

`core32` transmits pages 0 through 4, five CAN frames per snapshot. It contains
the high-rate tuning core: RPM, final timing command, APC command, fuel-inhibit
mask, both MAF channels and their total, both A/F channels, BFS, six injection
words, knock state, and the latched knock interval count and channel mask.

`wide54` transmits pages 0 through 7, eight CAN frames per snapshot. It includes
the complete `core32` set and adds APP, both throttle positions, absolute
throttle, actual and target intake CVTC for both banks, calculated load, and one
rotating page-7 context. Coolant/IAT/temperature sources, STFT/CVTC duty,
LTFT/timing state, and protocol/queue health are therefore each available at
one quarter of the snapshot rate. Pinning one context is a separate build-time
choice that omits the other three contexts.

`wide54` at divisor 1 is the schema-1 ceiling, not a full-rate stream of every
context field. The three-bit page ID is exhausted by pages 0 through 7. Sending
all four current contexts at every base tick requires a new wire schema and at
least three additional DLC-8 frames per group, or a second CAN ID.

The base wrapper runs every `10.24 ms`. `tick_divisor` selects every Nth base
tick for publication:

| Divisor | Snapshot rate | Snapshot interval | `tick16` step on the wire |
| ---: | ---: | ---: | ---: |
| 1 | 97.65625 Hz | 10.24 ms | 1 |
| 2 | 48.828125 Hz | 20.48 ms | 2 |
| 4 | 24.4140625 Hz | 40.96 ms | 4 |

The transmitted `tick16` step distinguishes configured downsampling from a
lost snapshot. The schema-1 builder copies all eight pages into the inactive
bank whenever a snapshot is due, including under `core32`; `page_count` limits
transmission, not capture construction. At the same divisor, `core32` and
`wide54` therefore have the same main-loop capture/copy work. `wide54` adds
three CAN transmissions and their three completion-ISR executions.

The knock wrapper refreshes the count and mask latches at every base interval
before the stock consumer clears them. With a divisor greater than 1, an older
nonzero interval can be overwritten before the next published snapshot.
Divisor 1 is therefore the only schema-1 setting that preserves each base-rate
knock interval in the outgoing snapshot sequence.

## Bandwidth

A standard 11-bit classical-CAN data frame with DLC 8 occupies 111 bits
including intermission before bit stuffing. A conservative maximum-stuffing
bound is 135 bits. At `500 kbit/s` and the measured `97.65625 Hz` snapshot
rate:

| Profile | Frames per snapshot | Frames per second | Added bus load | No-arbitration group time |
| --- | ---: | ---: | ---: | ---: |
| `core32` | 5 | 488.28125 | 10.84% to 13.18% | 1.11 to 1.35 ms |
| `wide54` | 8 | 781.25 | 17.34% to 21.09% | 1.78 to 2.16 ms |

The exact stock ECM broadcast estimate is 9.70% to 11.78% without conditional
`0x512` and 11.25% to 13.64% with it. Stock ECM plus telemetry is therefore:

| Profile | Without `0x512` | With `0x512` |
| --- | ---: | ---: |
| `core32` | 20.54% to 24.96% | 22.09% to 26.82% |
| `wide54` | 27.04% to 32.87% | 28.59% to 34.73% |

These totals exclude every other vehicle controller, retransmission, error
frame, and diagnostic session. Aggregate utilization alone is not an approval
criterion. Passive whole-bus capture and a bounded hardware trial determine
the usable profile and divisor.

### Measured whole-vehicle baseline

The operator-confirmed nominal bitrate is `500 kbit/s`. Three endpoint-disabled
PEAK TRC 1.1 captures contain 363,923 standard data frames over 187.112 seconds.
The load bounds count intermission; the lower bound excludes bit stuffing and
the upper bound applies a conservative maximum-stuffing count.

| Firmware label and context | Average load | Peak 100 ms | Peak 1 s |
| --- | ---: | ---: | ---: |
| `1.8`, startup | 39.889% to 48.402% | 43.260% to 52.500% | 40.428% to 49.057% |
| `1.8`, idle, ASCD, PRND | 39.870% to 48.379% | 41.262% to 50.070% | 40.098% to 48.654% |
| `1.10`, idle, ASCD, Rolling Launch | 39.849% to 48.353% | 41.198% to 49.990% | 40.052% to 48.600% |

The traces contain no RTR, warning, or error records. PCAN-View can omit error
frames according to its recording configuration, so these endpoint-disabled
captures alone do not close the physical error-rate gate. The enabled capture
below supplies the acceptance evidence with error-frame recording enabled.

Adding the theoretical telemetry cost to the highest observed average gives a
planning bound, not a counterfactual measurement:

| Profile and divisor | Snapshot rate | Projected average load |
| --- | ---: | ---: |
| `core32`, 4 | 24.414 Hz | 42.599% to 51.698% |
| `core32`, 2 | 48.828 Hz | 45.309% to 54.994% |
| `core32`, 1 | 97.656 Hz | 50.729% to 61.586% |
| `wide54`, 4 | 24.414 Hz | 44.225% to 53.675% |
| `wide54`, 2 | 48.828 Hz | 48.561% to 58.949% |
| `wide54`, 1 | 97.656 Hz | 57.233% to 69.496% |

### Target-vehicle `wide54` result

The 2026-08-17 target-vehicle run uses firmware label `1.11`, standard ID
`0x6F0`, `wide54`, divisor 1, and a listen-only PCAN-USB receiver at
`500 kbit/s`. PCAN-View error-frame recording was enabled. The saved TRC spans
366.920 seconds and contains 1,000,000 standard received data frames across 45
IDs, including 286,493 custom frames. Five initial custom frames are the tail
of a group already in progress when recording begins. Every subsequent custom
frame forms one of 35,811 complete snapshots.

| Measurement | Result |
| --- | ---: |
| Complete snapshot rate | 97.599 Hz |
| Tick steps | 35,810 steps of exactly 1 |
| Schema mismatches | 0 |
| Incomplete or malformed groups after initial synchronization | 0 |
| Nonzero telemetry status samples | 0 |
| Snapshot overrun / TX abort | 0 / 0 |
| PCAN warning / error records | 0 / 0 |
| Group latency median / P99 / maximum | 2.3 / 6.3 / 8.1 ms |
| Whole-bus average load | 57.185% to 69.437% |
| Whole-bus peak 100 ms load | 59.006% to 71.650% |
| Whole-bus peak 1 s load | 57.473% to 69.787% |

The final dashboard view retains 105,153 complete groups with verified schema
and zero visible loss, source drop, schema mismatch, error, overrun, or abort
counters. The stream RPM and nearest stock `0x180` RPM samples differ by a
mean absolute 6.382 RPM across all 35,811 groups. The recorded result closes
hardware acceptance for the current tuning-telemetry configuration. No
additional shutdown, concurrent-diagnostic, DTC-comparison, or direct
scheduler-slack observation is required for this use.

The versioned dashboard records the strict stream directly as MLVLG v2, and a
separate converter produces the same schema from PEAK TRC 1.1 captures. The
schema contains all custom fields, retained stock RPM/speed/control context,
and reserved `gps_lat`/`gps_lon` channels. Geographic coordinates are not
verified on the captured primary CAN network and remain `NaN`; no route is
derived from speed or other vehicle signals.

The retained fallback order is `wide54` divisor 2, then `wide54` divisor 4.
The passing divisor-1 result remains selected unless a later observation shows
recurring incomplete or preempted groups, a nonzero overrun/abort trend, CAN
warning/error or bus-state records, stock-frame period regression, or ECU
reset. Changing to `core32` is appropriate only when the additional fields are
intentionally discarded; at a common divisor it does not reduce snapshot
construction work. Absence of PCAN error records alone is not sufficient
because arbitration retries do not necessarily increment the telemetry abort
counter.

## Failure behavior

- Invalid configuration, invalid page count, or corrupted queue state disables
  custom TX and leaves every stock mailbox path intact.
- No telemetry path writes a stock payload record or stock mailbox.
- A busy mailbox never blocks the control loop.
- A delayed chain loses old snapshots rather than transmitting an unbounded
  history.
- Sequence, tick, incomplete groups, overrun count, and abort count make every
  loss visible to the logger.
- Bus-off and recovery remain under the stock HCAN controller and application
  behavior; telemetry does not reset the controller or alter stock error state.

## Verification gates

### Static and executable gates

The tracked software endpoint passes all of the following gates:

1. exact stock hash and exact original bytes at every table, hook, and vector
   site;
2. unified ROM and RAM overlap validation;
3. independently assembled SH-2E fixtures for every injected instruction;
4. `tools/sh-elf-run/` execution of startup clear, capture publication, idle
   start, every page transition, latest-wins replacement, preemption, final
   completion, TXACK, ABACK, simultaneous mailbox-26/mailbox-28 flags, corrupt
   state fail-closed behavior, relevant branches, delay slots, calls, returns,
   a real `TRAPA` exception entry, and the exact ISR `RTE`;
5. proof that simulator stubs and relocations do not alter bytes under test;
6. generated firmware and host schemas with the same profile CRC; and
7. a decoder test corpus containing wrap, loss, duplicate, reordered,
   incomplete, preempted, regular-context, health-match, and health-mismatch
   frames.

The GNU gate independently assembles 470 injected instructions, verifies eight
entries and the locked one-MiB composition, and executes 49 telemetry cases.
Simulator-only high-RAM relocations, stock-function stubs, and the TRAPA vector
are installed only after exact instruction identity. No instruction or
control-flow address under test is changed.

### Target-vehicle acceptance

The endpoint-disabled captures establish `Pphi = 20 MHz`, stock ID/DLC and
cadence, stationary utilization, and absence of `0x6F0` in the recorded stock
states. The enabled target-vehicle capture establishes coherent page order,
sequence and tick continuity, context rotation, queue health, CAN error status,
stock-frame coexistence, moving-load utilization, and dashboard reception at
the maximum schema-1 rate.

Together with the executable gate, this is the complete acceptance basis for
the current `0x6F0`, `wide54`, divisor-1 tuning logger. Additional stress or
physical-output measurements are relevant only to a changed configuration or
to claims about measured spark angle, injector waveform, or air-fuel ratio.

## Implementation inventory and acceptance status

| Artifact | Responsibility |
| --- | --- |
| `can-telemetry-profile.toml` | authoritative field and context schema |
| `can_telemetry_profile.py` | table and host-schema generator |
| `can-telemetry-layout.toml` | ROM, RAM, hook, configuration, and reserve contract |
| `can-telemetry-*.s` | wrappers, capture, queue, combined ISR, and generated tables |
| `can-telemetry-payloads.toml` | SHA-locked independently assembled bytes |
| `can_telemetry.py` | fail-closed build configuration and mailbox encoding |
| `can_telemetry_compose.py` | deterministic non-flashable composition |
| `apply_can_telemetry.py` | isolated checksum-closing application stage |
| `build_rom.py` | production three-runtime composition |
| `../tools/logs/can_telemetry.py` | strict candump group decoder |
| `../tools/logs/mlvlg.py` | common MLVLG v2 encoder and validator |
| `../tools/logs/trc_to_mlg.py` | strict PEAK TRC to MLVLG converter |
| `../tools/can_dashboard/` | versioned live display and MLVLG recorder |
| `../tools/sh-elf-run/verify_can_telemetry.py` | independent executable gate |
| `jk08a-runtime-reservations.toml` | shared active ownership and future budgets |

Schema 1 has no remaining hardware acceptance gate for the current standard ID,
profile, divisor, and tuning-logger use. A later observed transport failure uses
divisors 2 and 4 in that order. Any event extension or wire-schema change
requires an exact producer hook gate and a separate physical validation plan.
