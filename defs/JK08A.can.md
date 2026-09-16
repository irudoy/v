# Exact JK08A HCAN1 model

## Scope

This specification records the stock HCAN1 mailbox configuration and the
transmit path used by exact ROM
`ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23`.
It separates code-proven controller behavior from payload names that still
depend on vehicle capture or homologous diagnostic evidence.

The Renesas SH7058S hardware manual is authoritative for register behavior.
The exact ROM is authoritative for the application configuration.

## Mailbox table

`FUN_000C2FBE` reads 30 four-byte records from ROM `0x0000975A`. Record `i`
configures physical HCAN1 mailbox `i + 1`; mailbox 0 and mailbox 31 are
initialized separately. A record contains:

```text
byte 0: firmware type
byte 1: DLC
byte 2: high byte of STDID << 5
byte 3: low byte of STDID << 5
```

The firmware types have the following exact effects:

| Type | MBC | Direction | Mailbox activity interrupt |
| ---: | ---: | --- | --- |
| 1 | `010` | receive | masked |
| 2 | `010` | receive | enabled |
| 3 | `000` | transmit | masked |
| 4 | `000` | transmit | enabled |
| 5 | `111` | inactive | masked |

The stock records are:

| Physical mailbox | Record | Type | Direction | DLC | Standard ID |
| ---: | ---: | ---: | --- | ---: | ---: |
| 1 | `0x975A` | 3 | TX | 5 | `0x239` |
| 2 | `0x975E` | 1 | RX | 8 | `0x2B0` |
| 3 | `0x9762` | 3 | TX | 3 | `0x6E2` |
| 4 | `0x9766` | 3 | TX | 8 | `0x551` |
| 5 | `0x976A` | 3 | TX | 8 | `0x1F9` |
| 6 | `0x976E` | 3 | TX | 3 | `0x580` |
| 7 | `0x9772` | 3 | TX | 7 | `0x182` |
| 8 | `0x9776` | 3 | TX | 8 | `0x180` |
| 9 | `0x977A` | 3 | TX | 7 | `0x160` |
| 10 | `0x977E` | 1 | RX | 3 | `0x560` |
| 11 | `0x9782` | 1 | RX | 6 | `0x177` |
| 12 | `0x9786` | 1 | RX | 8 | `0x174` |
| 13 | `0x978A` | 1 | RX | 7 | `0x176` |
| 14 | `0x978E` | 1 | RX | 8 | `0x284` |
| 15 | `0x9792` | 1 | RX | 8 | `0x354` |
| 16 | `0x9796` | 1 | RX | 8 | `0x245` |
| 17 | `0x979A` | 1 | RX | 5 | `0x1A5` |
| 18 | `0x979E` | 1 | RX | 8 | `0x5C5` |
| 19 | `0x97A2` | 3 | TX | 4 | `0x512` |
| 20 | `0x97A6` | 1 | RX | 4 | `0x342` |
| 21 | `0x97AA` | 1 | RX | 8 | `0x54C` |
| 22 | `0x97AE` | 1 | RX | 8 | `0x35D` |
| 23 | `0x97B2` | 1 | RX | 8 | `0x358` |
| 24 | `0x97B6` | 1 | RX | 6 | `0x215` |
| 25 | `0x97BA` | 1 | RX | 6 | `0x625` |
| 26 | `0x97BE` | 5 | inactive | 0 | none |
| 27 | `0x97C2` | 1 | RX | 8 | `0x280` |
| 28 | `0x97C6` | 4 | TX | 0 | configured at runtime |
| 29 | `0x97CA` | 2 | RX | 0 | configured at runtime |
| 30 | `0x97CE` | 2 | RX | 0 | configured at runtime |

The table proves configured capability, not traffic observed on a particular
vehicle. A passive capture is required to establish actual presence, period,
jitter, and payload behavior.

## Stock broadcast transmit path

The stock periodic path has two separate stages in the 124-entry table called
by `FUN_00020DFE`:

1. `FUN_000C38DE`, referenced at `0x00021928`, scans only type-3 records and
   calls `FUN_000C3746` for eligible transmissions.
2. `FUN_000C3DE4`, referenced at `0x00021930`, scans only type-3 records and
   serializes the payload for a subsequent scan.

The scan therefore precedes payload preparation in the same scheduler cycle.
Each table record has a ten-byte software state record at
`0xFFFF3AB5 + 10*i`; the last eight bytes are its payload. The submitter copies
that payload into physical mailbox `i + 1` and requests transmission through
TXPR.

Type-4 mailbox 28 does not enter either type-3 scan. Its mailbox-empty event is
handled by the HCAN1 SLE1 interrupt at `FUN_000C7914` in stock firmware.

The stock type-3 frames are:

| Standard ID | DLC | Physical mailbox | Serializer | Relative cadence |
| ---: | ---: | ---: | ---: | ---: |
| `0x160` | 7 | 9 | `0x000C590E` | `Tcan` |
| `0x180` | 8 | 8 | `0x000C577A` | `Tcan` |
| `0x182` | 7 | 7 | `0x000C5558` | `Tcan` |
| `0x1F9` | 8 | 5 | `0x000C5236` | `Tcan` |
| `0x239` | 5 | 1 | `0x000C5ABE` | `2*Tcan` |
| `0x512` | 4 | 19 | `0x000C509E` | `Tcan`, conditional |
| `0x551` | 8 | 4 | `0x000C5372` | `10*Tcan` |
| `0x580` | 3 | 6 | `0x000C5508` | `10*Tcan` |
| `0x6E2` | 3 | 3 | `0x000C5100` | `10*Tcan` |

The code-proven period is `Tcan = 204800 / Pphi` seconds. Passive vehicle
timestamps establish `Pphi = 20 MHz` and `Tcan = 10.24 ms`. Frame `0x512`
additionally requires `0xFFFF4231.bit2`.

## Proven payload boundaries

The following payload claims are sufficiently narrow for use as cross-checks:

- `0x180` bytes 0 and 1 and `0x1F9` bytes 2 and 3 contain big-endian engine
  speed with `RPM = raw / 8`.
- `0x180` byte 5 and the top two bits of byte 6 contain a ten-bit source from
  `0xFFFF279C`, limited to 1000. Accelerator-pedal semantics remain a
  homologous and live-correlation claim.
- `0x239` byte 3 receives one-hot steering-switch code `0xFFFF36D8`.
- `0x551` byte 0 receives coolant snapshot `0xFFFF3FA4`; code 0 is the lower
  saturation and positive codes use the exact `code - 40` transform.
- `0x551` byte 5 bits 4 through 6 contain `0xFFFF40D0 & 7`, the complete
  three-bit ASCD display state.
- `0x551` byte 4 is forced to zero in exact JK08A.
- `0x174` byte 3 high nibble is target gear and its low nibble is current gear.
  Values 1 through 7 become zero-based indices 0 through 6; every other value
  becomes zero. `FUN_000C47EA` publishes the live pair and `FUN_00020DFE`
  snapshots it for request-limiter use.
- `0x174` byte 4 bits 5 through 7 are a TCM status field published to
  `0xFFFF3A2E` by `FUN_000C47EA`; `FUN_0007724C` maps value 3 to
  `0xFFFF419B.bit4`, the source of transition-neutralizer latch
  `0xFFFF418F.bit4`. Byte 4 bits 0 through 3 and byte 5 bits 6 and 7 feed two
  further status bytes. The field meaning is not established.
- `0x177` byte 2 bits 0 through 2 are a zero-based TCM gear-phase index decoded
  by `FUN_000C4ACE`. Higher bits are independent status flags.

Other field names require a code trace or a synchronized vehicle capture.
Geometry copied from a Z34 frame list is not exact JK08A evidence.

## Passive vehicle capture evidence

Three PEAK PCAN-View TRC 1.1 captures recorded on 2026-08-16 provide the
current vehicle baseline. The nominal bitrate was configured as `500 kbit/s`.
The raw traces remain local and untracked; their hashes and exact firmware
identities are registered in `../patches/hardware-results.toml`.

| Firmware label | Recorded context | Frames | Observed span | Standard IDs |
| --- | --- | ---: | ---: | ---: |
| `1.8` | startup | 30,481 | 15.660 s | 49 |
| `1.8` | idle, ASCD input, and stationary PRND selection | 100,000 | 51.398 s | 44 |
| `1.10` | idle, ASCD input, and stationary Rolling Launch trials | 233,442 | 120.053 s | 44 |

All 363,923 records are received standard data frames. The traces contain no
extended, RTR, warning, or error records. Absence of error records is
conclusive only when PCAN-View error-frame logging was enabled during capture.

The 44 IDs common to the idle and Rolling Launch captures are:

```text
002 160 174 176 177 180 182 1A5 1B4 1F9 215 216 239 245 280 284 285
2A0 2B0 2B3 2B4 2DE 351 354 355 358 35D 421 515 51F 540 541 542 54A
54B 54C 551 560 580 5C5 60D 625 6C2 6E2
```

The startup capture additionally contains `0x71D`, `0x71E`, `0x71F`, `0x72D`,
and `0x72E`. Neither conditional ECM frame `0x512` nor telemetry candidate
`0x6F0` occurs in any endpoint-disabled capture. A separate enabled capture
establishes successful `0x6F0` coexistence under moving load and accepts the ID
for the current tuning-telemetry use. The ID has lower arbitration priority
than all observed stock ECM broadcasts through `0x6E2`, but higher priority
than the five startup-only IDs.

Measured ECM periods agree with the code-derived schedule:

| ID | Median period | P99 range across captures |
| ---: | ---: | ---: |
| `0x160` | 10.2 ms | 10.6 to 10.7 ms |
| `0x180` | 10.2 ms | 11.0 to 11.3 ms |
| `0x182` | 10.2 ms | 11.0 to 11.4 ms |
| `0x1F9` | 10.2 ms | 11.0 to 11.3 ms |
| `0x239` | 20.5 ms | 21.4 to 21.7 ms |
| `0x551` | 102.4 ms | 104.9 to 105.8 ms |
| `0x580` | 102.3 to 102.4 ms | 105.2 to 105.8 ms |
| `0x6E2` | 102.3 to 102.4 ms | 105.5 to 106.0 ms |

The `10*Tcan` median of 102.4 ms yields `Tcan = 10.24 ms`; substitution into
`Tcan = 204800 / Pphi` establishes `Pphi = 20 MHz`. The `1.8` and `1.10`
captures have identical normal-operation ID and DLC sets and no material ECM
period or jitter regression.

Across 18,267 paired scheduler cycles, `0x180` bytes 0 and 1 exactly equal the
following `0x1F9` bytes 2 and 3. The second copy arrives 0.4 to 1.8 ms later.
This independently confirms the shared big-endian engine-speed source and the
`RPM = raw / 8` transform.

Live control correlations establish `0x239` byte 3 values `0x20` for release,
`0x10` for RESUME/ACCEL, `0x08` for SET, and `0x02` for CANCEL. The saved
2026-08-17 trace contains release, SET, and CANCEL; the `0x10` RESUME/ACCEL
code is an operator-confirmed live observation outside that saved trace. Frame
`0x551` byte 5 preserves low nibble `0x02` while custom state 6 appears as
`0x62` during map feedback and custom state 7 appears as `0x72` during Rolling
Launch ACTIVE. Exact-target observation establishes that state 6 illuminates
SET together with CRUISE. A CRUISE-only value is not yet bound; state 5 is the
leading candidate from the stock ASCD diagnostic state machine. The map
feedback mask correction first included in firmware `1.9` is present in
firmware `1.11`: its `0x8F` immediate clears all three state bits before
inserting `0x60`. The observed SET lamp is therefore a property of state 6 on
the exact target, not a retained state-7 bit.

Target-vehicle selector observations establish the following `0x421` byte-0
mapping:

| Code | Selector state | Evidence |
| ---: | --- | --- |
| `0x08` | P | saved trace and operator confirmation |
| `0x10` | R | saved trace and operator confirmation |
| `0x18` | N | saved trace and operator confirmation |
| `0x20` | D | saved trace and operator confirmation |
| `0x28` | DS | saved trace and operator confirmation |
| `0x80` | M1 | saved trace and operator confirmation |
| `0x88` | M2 | saved trace and operator confirmation |
| `0x90` | M3 | saved trace and operator confirmation |
| `0x98` | M4 | operator confirmation outside saved trace |
| `0xA0` | M5 | operator confirmation outside saved trace |

Transient zero appears between some detents and is not a stable selector
position. No M6 or M7 code is inferred from the numeric pattern.

The same moving capture establishes transmission payload sequencing independent
of selector frame `0x421`:

| Shift observation | `0x174` byte 3 sequence | `0x177` low-three-bit sequence |
| --- | --- | --- |
| downshift 4 to 3 | `0x44 -> 0x34 -> 0x33` | `3 -> 2` between target and current updates |
| downshift 3 to 2 | `0x33 -> 0x23 -> 0x22` | `2 -> 1` between target and current updates |
| upshift 2 to 3 | `0x22 -> 0x32 -> 0x33` | `1 -> 2` between target and current updates |

The high nibble therefore represents target gear and changes before the
low-nibble current gear for both shift directions. In stable first through
fourth gear, the `0x177` value equals current gear minus one. Its intermediate
timing establishes an operational TCM phase index but does not prove the exact
mechanical engagement boundary. These payloads are received by the ECM:
stock mailbox records `0x9786=01 08 2E 80` and `0x9782=01 06 2E E0` encode
standard IDs `0x174` and `0x177` as `STDID << 5`.

### Enabled telemetry moving-load evidence

The 2026-08-17 `1.11` schema-1 capture records 1,000,000 standard received data frames
over 366.920 seconds with PCAN-View error-frame recording enabled. It contains
286,493 `0x6F0` frames and 35,811 complete `wide54` divisor-1 groups after the
initial partial group. Every accepted tick advances by one. Schema mismatch,
incomplete group, malformed group after synchronization, telemetry status,
snapshot-overrun, transmit-abort, PCAN warning, and PCAN error counts are all
zero. Measured whole-bus load is 57.185% to 69.437% on average, with a
59.006% to 71.650% peak over a rolling 100 ms window.

Frame `0x280` bytes 4 and 5 form a big-endian moving quantity. The homologous
Z34 formula `raw / 100 km/h` yields 0.00 to 68.54 km/h in this target capture
and returns to zero at the operator-confirmed stationary end. This establishes
the target field location and zero state. The physical scale remains a
candidate until a synchronized independent speed reference is recorded.

### Navigation-coordinate boundary

The captured primary CAN network has no verified latitude or longitude
signal. The factory AV/navigation topology connects the GPS antenna directly
to the AV control unit, which calculates vehicle position from GPS, gyro,
vehicle speed, and map data. Its primary-CAN signal chart carries vehicle
context into that unit but does not identify a geographic-coordinate broadcast.
The separate AV communication network was not present in the OBD PCAN capture.

Accordingly, no primary-CAN ID or byte layout is assigned to latitude or
longitude. The dashboard and MLG schema reserve `gps_lat` and `gps_lon` for
UltraLog compatibility, expose their source as unavailable on primary CAN,
and store `NaN` until a separate AV-network or external-GPS capture establishes
an exact binding. Vehicle speed is not integrated into a synthetic route.

## Mailbox-empty interrupt

Vector-table word `0x000203A0` points to `FUN_000C7914`. The ISR checks only
physical mailbox 28, represented by bit `0x1000` in HCAN1 TXACK1 and ABACK1.
It clears HCAN1 IRR bit 8 with word `0x0100`. A successful mailbox-28
transmission calls `FUN_000C6B68`; the abort path does not.

Relevant HCAN1 addresses are:

| Address | Register or field |
| ---: | --- |
| `0xFFFFD808` | IRR1; bit 8 is mailbox empty |
| `0xFFFFD820` | TXPR1 for physical mailboxes 16 through 31 |
| `0xFFFFD830` | TXACK1 |
| `0xFFFFD838` | ABACK1 |
| `0xFFFFD840` | RXPR1; bit 15 is mailbox-31 data-frame pending |
| `0xFFFFD848` | RFPR1; bit 15 is mailbox-31 remote-frame pending |
| `0xFFFFD850` | MBIMR1; zero enables a mailbox activity interrupt |
| `0xFFFFD858` | UMSR1; bit 15 reports mailbox-31 unread-message overflow |
| `0xFFFFDC40` | physical mailbox 26 control base |
| `0xFFFFDC48` | physical mailbox 26 eight-byte data field |
| `0xFFFFDCE0` | physical mailbox 31 control base |
| `0xFFFFDCE8` | physical mailbox 31 eight-byte data field |

For physical mailbox 26, the corresponding TXPR1, TXACK1, ABACK1, and MBIMR1
bit is bit 10, or `0x0400`.

## Safe extension boundary

Physical mailbox 26 is the only table-owned inactive mailbox that can be
promoted without replacing a stock receive or transmit role. The telemetry
runtime uses a type-4 record to configure it as a transmit mailbox and enable
its mailbox-empty interrupt while keeping it outside the stock type-3 scans.

Mailbox 31 is initialized separately as inactive by the complete HCAN1
initializer at `0x000C338A`. The initializer is called through pointers at
`0x0002D7FC` during primary startup and `0x000C3B10` during recovery. The
SH7058S transmit-cancellation limitation applies only when mailbox 31 is a
transmit buffer. The telemetry runtime calls the complete stock initializer,
preserves its return value, and then configures mailbox 31 as MBC `010`, DLC 8,
standard receive for the control ID. Its activity interrupt stays masked.
The direct physical mailbox ID word uses `STDID << 4`, not the table-record
encoding `STDID << 5`; the lower nibble contains RTR, IDE, and extended-ID
bits. Control ID `0x6F1` is therefore written as `0x6F10`.

The stock receive scans cover only the 30 table-backed mailboxes 1 through 30.
Telemetry therefore polls mailbox-31 RXPR1 at its interrupt-disabled scheduler
boundary. It also checks RTR and clears the corresponding RXPR1, RFPR1, and
UMSR1 bits, so a remote request or overflow cannot leave the mailbox blocked.

SH7058S hardware-manual section 17.7.6 permits changing the identifier of a
transmit mailbox whenever its corresponding TXPR bit is clear. After mailbox 26
reports TXACK or ABACK and the handler clears the flag, firmware could write a
different standard ID to `0xFFFFDC40`, update the payload, and request another
transmission without reconfiguring MBC or entering halt mode. Current telemetry
schema 2 does not use this capability: all eleven pages use one build-selected
standard ID and the identifier record remains constant while the endpoint is
active.

The implemented custom telemetry layer always promotes mailbox 26 to type 4 so
a runtime START command can activate a build whose startup flag is disabled.
The transmitter remains idle until streaming is enabled. The layer replaces
the SLE1 vector with one
combined handler that services mailbox 26 and reproduces the complete stock
mailbox-28 success and abort behavior before executing `RTE`. The stock handler
cannot be called with `JSR` because it owns the exception return, and an
indirect tail jump would consume a general register whose entry value the stock
prologue must preserve. The combined handler therefore saves `r0..r7` and PR,
services the bounded queue, executes the exact mailbox-28 side effects, restores
the interrupted state, and returns through one `RTE`.

The custom telemetry implementation that uses this boundary is specified in
`../patches/can-telemetry.md`.
