# JK08A custom CAN telemetry schema 2

## Status and objective

This document specifies the single implemented JK08A custom telemetry patch.
The firmware, generated source-pointer table, strict host decoder, dashboard,
MLVLG recorder, ROM builder, and GNU SH-2E executable gate use the same schema
2 contract.

The endpoint is disabled by default. The complete software gate passes, but
schema 2 has not been tested in the target vehicle. The recorded schema 1
`wide54` result remains useful bus-capacity and mailbox evidence; it does not
validate schema 2 and is intentionally not accepted by the current decoder.

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
  -> coherent capture into inactive 88-byte bank
  -> atomic active/pending publication
  -> eleven DLC-8 frames on one standard CAN ID
  -> HCAN1 physical mailbox 26
  -> combined SLE1 completion handler
  -> next page or newest pending snapshot
```

The implementation preserves the stock CAN transmit scan, stock serializers,
all stock receive mailboxes, and the complete mailbox-28 SLE1 behavior.

## Exact integration points

| Integration point | Stock value | Implemented behavior |
| --- | ---: | --- |
| mailbox-26 record at `0x000097BE` | `05 00 00 00` | type 4, DLC 8, build-selected standard ID when enabled |
| main-loop call literal at `0x00028090` | `0x00020DFE` | call stock scheduler, capture, return |
| periodic table entry at `0x00021A70` | `0x000493E8` | latch knock count and mask before the stock consumer clears them |
| HCAN1 SLE1 vector at `0x000203A0` | `0x000C7914` | service mailbox 26 and reproduce mailbox-28 success and abort behavior |
| composed startup wrapper | existing wrapper chain | clear the complete active telemetry RAM allocation |

The candidate standard ID is `0x6F0`. The ID remains a build parameter in the
range `0x001..0x7FF`, but every page in one build uses the same ID. Eleven
pages fit the four-bit page number, and additional IDs would not reduce bus
occupancy while only one verified physical mailbox is used.

For `0x6F0`, the enabled mailbox record is `04 08 DE 00` because the table
stores `STDID << 5`. Physical mailbox 26 uses control base `0xFFFFDC40`, data
bytes `0xFFFFDC48..0xFFFFDC4F`, and bit `0x0400` in HCAN1 TXPR1, TXACK1,
ABACK1, and MBIMR1.

## Coherent capture boundary

The main loop calls the pointer at `0x00028090` while interrupts are masked.
`FUN_00020DFE` performs its snapshot copies and periodic tasks before returning.
The wrapper calls the stock function first and copies all selected sources
immediately afterward without another interrupt-state transition.

All multi-byte values retain ECU big-endian representation. Firmware performs
no engineering conversion. The generated host schema owns signedness, scale,
and candidate semantic labels.

`FUN_000493E8` consumes and clears the knock interval count before the final
capture boundary. The wrapper at periodic entry 65 therefore latches
`0xFFFF2142` and `0xFFFF2150` before calling the stock function. The main
capture includes those latches with the updated timing state.

## ROM and RAM layout

The runtime owns `0x000D4280..0x000D6000` inside the audited free ROM region.

| ROM range | Size | Purpose |
| ---: | ---: | --- |
| `0x000D4280..0x000D4340` | 192 | main, knock, and startup wrappers |
| `0x000D4340..0x000D4800` | 1,216 | configuration guard, capture, bank builder, and page request |
| `0x000D4800..0x000D4C00` | 1,024 | combined SLE1 ISR and bounded queue |
| `0x000D4C00..0x000D4E00` | 512 | 444-byte generated source-pointer table plus erased tail |
| `0x000D4E00..0x000D4E10` | 16 | fail-closed build configuration |
| `0x000D4E10..0x000D6000` | 4,592 | exclusive erased future ROM reserve |

The active RAM allocation is `0xFFFF5E00..0xFFFF5F00`.

| RAM range | Size | Purpose |
| ---: | ---: | --- |
| `0xFFFF5E00..0xFFFF5E20` | 32 | state, profile, status, counters, and knock latches |
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
| 4 | 1 | profile ID `1` |
| 5 | 1 | page count `11` |
| 6 | 1 | tick divisor `1..255` |
| 7 | 1 | reserved zero |
| 8 | 2 | standard CAN ID |
| 10 | 2 | profile CRC16 `0xE881` |
| 12 | 4 | integrity word `0x54454C32` (`TEL2`) |

The only profile name is `tuning`. The default disabled bytes are
`43 54 02 00 01 0B 01 00 06 F0 E8 81 54 45 4C 32`.

Firmware validates every field before incrementing the telemetry tick or
touching the queue. The builder independently requires the mailbox record to
match the same enable state and CAN ID. Any mismatch leaves custom TX inactive.

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

### Fixed pages

Pages 0 through 8 are captured at every published snapshot.

| Page | Fields and exact sources |
| ---: | --- |
| 0 | `tick16`; `rpm_raw` `FFFF11F4`; `final_timing_raw` `FFFF11D4`; `apc_command_raw` `FFFF2022`; `fuel_inhibit_mask` `FFFF22E0` |
| 1 | `maf_b1_raw` `FFFF101C`; `maf_b2_raw` `FFFF101E`; `maf_total_raw` `FFFF3852`; `front_oxygen_sensor_b1_raw` `FFFF22C4` |
| 2 | `bfs_raw` `FFFF1026`; `front_oxygen_sensor_b2_raw` `FFFF22C5`; `injection_0_raw` `FFFF23C8`; `injection_1_raw` `FFFF23CA` |
| 3 | `injection_2_raw` `FFFF23CC`; `injection_3_raw` `FFFF23CE`; `injection_4_raw` `FFFF23D0`; `telemetry_status` |
| 4 | `injection_5_raw` `FFFF23D2`; `knock_timing_state_raw` `FFFF121A`; `knock_surface_state` `FFFF2466`; latched knock count and channel mask |
| 5 | `app1_raw` `FFFF269E`; `app2_raw` `FFFF26A2`; `tps_b1_raw` `FFFF2756`; `absolute_throttle_raw` `FFFF1075` |
| 6 | `tps_b2_raw` `FFFF285C`; intake actual B1/B2 `FFFF2442/2443`; intake target `FFFF2326`; exhaust target `FFFF2327`; calculated load `FFFF413E` |
| 7 | bounded throttle request `FFFF19C6`; engine torque state `FFFF18CC`; injection timing state `FFFF162E`; exhaust actual B1 `FFFF2324` |
| 8 | shared throttle target `FFFF19B2`; channel targets `FFFF28BC/28BE`; exhaust actual B2 `FFFF2325` |

The six injection words are calculated software values. Their physical
cylinder order and equality to electrical injector-open duration remain
unverified. The timing fields are software coordinates rather than an
independent crank-referenced spark measurement.

### Rotating context pages

Pages 9 and 10 carry the same context tag in byte 1. Tags rotate from 0 through
3. Both pages are transmitted every snapshot, while each tagged field set is
refreshed once per four published snapshots. At divisor 1, the context-field
rate is `24.4140625 Hz`.

| Tag | Page 9 bytes 2..7 | Page 10 bytes 2..7 |
| ---: | --- | --- |
| 0 | coolant `FFFF1079`, IAT `FFFF2837`, fuel/oil diagnostic sources `FFFF1074/2876`, Q14 A/F factor `FFFF22E8` | high-resolution intake duty B1/B2 `FFFF1AB0/1AB2`, manifold pressure bytes `FFFF118A/16D2` |
| 1 | STFT B1/B2 `FFFF22DC/22DE`, low-resolution intake duty B1/B2 `FFFF2440/2441` | high-resolution exhaust duty B1/B2 `FFFF1AAC/1AAE`, atmosphere `FFFF4544`, battery `FFFF1188` |
| 2 | LTFT B1/B2 `FFFF2302/2304`, timing states `FFFF2023/564C` | front A/F words `FFFF2780/2782`, adjustment state B1 `FFFF45A0` |
| 3 | protocol version, profile ID, profile CRC, saturated overrun and abort counters | secondary throttle B1/B2 `FFFF275E/2864`, adjustment state B2 `FFFF45A2` |

Schema-dependent conversions stay disabled until page 9 tag 3 reports version
2, profile ID 1, and CRC `0xE881`. A later mismatch disables conversions again.
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
- version 2, profile ID 1, and CRC `0xE881` health identity;
- no sustained incomplete groups, overrun, abort, CAN warning, or CAN error;
- acceptable stock-frame cadence and whole-bus utilization.

The acceptance run does not need a shutdown cycle, active diagnostic session,
DTC comparison, or direct scheduler-slack measurement for this logging use.

## Verification gates

The repository-contained gate independently assembles all injected SH-2E
instructions and proves identity with the tracked payloads before installing
simulator-only high-RAM relocations and stock-function stubs. It executes all
changed entries, relevant branch outcomes, delay slots, call and return paths,
both banks, all pages, all eight context records, queue boundaries, latest-wins
replacement, preemption, TXACK, ABACK, simultaneous mailbox-26/mailbox-28
flags, corrupt-state fail-closed behavior, a real `TRAPA` exception entry, and
the exact ISR `RTE`.

The locked software result is:

- 482 injected instructions and 596 data bytes;
- eight executable entries and 50 dynamic telemetry cases;
- composition SHA-256
  `65f4f9f0095c77ae4580bbbaa0777b68e6ac596c7c56fadde2256084f881aaa1`;
- 1,320 changed bytes inside a 2,980-byte declared write set.

This gate proves the bounded software contract. It does not replace physical
CAN, ECU, sensor, or actuator validation.

## Artifact inventory

| Artifact | Responsibility |
| --- | --- |
| `can-telemetry-profile.toml` | authoritative field and context schema |
| `can_telemetry_profile.py` | pointer-table and host-schema generator |
| `can-telemetry-schema.json` | generated strict host contract |
| `can-telemetry-layout.toml` | ROM, RAM, hook, configuration, and reserve contract |
| `can-telemetry-*.s` | wrappers, capture, queue, ISR, and generated tables |
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
