# Exact JK78C HCAN model

## Scope

This specification records the stock HCAN configuration, the receive dispatch,
and the transmit composition of exact ROM
`86387d1de1daa8bf5f98e071eb899be462b7a466cb43f88a96e4dc8b87892b8d`.
It separates code-proven controller behavior from payload names that still
depend on vehicle capture or homologous diagnostic evidence.

The Renesas SH7058S hardware manual is authoritative for register behavior.
The exact ROM is authoritative for the application configuration.

JK78C drives two controllers. HCAN1 carries the vehicle bus. HCAN0 carries a
private bus whose participants are the VVEL control modules.

## Controllers

| Controller | Register block | Mailbox area | Record table | Configurator | Software shadow |
| --- | --- | --- | --- | --- | --- |
| HCAN1 | `0xFFFFD800` | `0xFFFFD900` | `0x0000944A` | `FUN_000EA19E` | `0xFFFF3D33` |
| HCAN0 | `0xFFFFD000` | `0xFFFFD100` | `0x000094C2` | `FUN_000EA6DE` | `0xFFFF3E5F` |

Each configurator reads 30 four-byte records. Record `i` configures physical
mailbox `i + 1` at `mailbox area + 0x20 * (i + 1)`. A record contains:

```text
byte 0: firmware type
byte 1: DLC
byte 2: high byte of STDID << 5
byte 3: low byte of STDID << 5
```

The firmware types have the following exact effects:

| Type | Direction | Mailbox activity interrupt |
| ---: | --- | --- |
| 1 | receive | masked |
| 2 | receive | enabled |
| 3 | transmit | masked |
| 4 | transmit | enabled |
| 5 | inactive | masked |

Each mailbox owns a ten-byte software state record in its controller shadow.
Record `i` starts at `shadow + 10 * i`; its last eight bytes are the payload.
The record tables are contiguous: `0x000094C2` is `0x0000944A + 120`.

## HCAN1 mailbox records

| Physical mailbox | Record | Type | Direction | DLC | Standard ID |
| ---: | ---: | ---: | --- | ---: | ---: |
| 1 | `0x944A` | 5 | inactive | - | - |
| 2 | `0x944E` | 5 | inactive | - | - |
| 3 | `0x9452` | 3 | TX | 8 | `0x1F9` |
| 4 | `0x9456` | 1 | RX | 8 | `0x245` |
| 5 | `0x945A` | 3 | TX | 8 | `0x551` |
| 6 | `0x945E` | 5 | inactive | - | - |
| 7 | `0x9462` | 3 | TX | 8 | `0x182` |
| 8 | `0x9466` | 3 | TX | 8 | `0x180` |
| 9 | `0x946A` | 3 | TX | 7 | `0x160` |
| 10 | `0x946E` | 5 | inactive | - | - |
| 11 | `0x9472` | 5 | inactive | - | - |
| 12 | `0x9476` | 5 | inactive | - | - |
| 13 | `0x947A` | 3 | TX | 3 | `0x580` |
| 14 | `0x947E` | 1 | RX | 8 | `0x284` |
| 15 | `0x9482` | 3 | TX | 3 | `0x6E2` |
| 16 | `0x9486` | 3 | TX | 4 | `0x512` |
| 17 | `0x948A` | 1 | RX | 4 | `0x342` |
| 18 | `0x948E` | 1 | RX | 8 | `0x54C` |
| 19 | `0x9492` | 1 | RX | 8 | `0x5C5` |
| 20 | `0x9496` | 1 | RX | 8 | `0x280` |
| 21 | `0x949A` | 1 | RX | 6 | `0x625` |
| 22 | `0x949E` | 1 | RX | 8 | `0x358` |
| 23 | `0x94A2` | 1 | RX | 8 | `0x35D` |
| 24 | `0x94A6` | 1 | RX | 6 | `0x215` |
| 25 | `0x94AA` | 1 | RX | 8 | `0x354` |
| 26 | `0x94AE` | 5 | inactive | - | - |
| 27 | `0x94B2` | 2 | RX | 8 | `0x000` |
| 28 | `0x94B6` | 4 | TX | 0 | `0x000` |
| 29 | `0x94BA` | 2 | RX | 0 | `0x000` |
| 30 | `0x94BE` | 2 | RX | 0 | `0x000` |

## HCAN0 mailbox records

Mailboxes 8 through 30 are inactive.

| Physical mailbox | Record | Type | Direction | DLC | Standard ID |
| ---: | ---: | ---: | --- | ---: | ---: |
| 1 | `0x94C2` | 3 | TX | 8 | `0x22B` |
| 2 | `0x94C6` | 1 | RX | 8 | `0x22A` |
| 3 | `0x94CA` | 1 | RX | 8 | `0x22C` |
| 4 | `0x94CE` | 1 | RX | 3 | `0x22D` |
| 5 | `0x94D2` | 1 | RX | 8 | `0x230` |
| 6 | `0x94D6` | 1 | RX | 3 | `0x231` |
| 7 | `0x94DA` | 1 | RX | 3 | `0x232` |

## HCAN0 scheduling and dispatch

Two scheduler pointer arrays hold the HCAN0 entry points. ROM `0x00021940`
holds `FUN_000EDC70`, the receive dispatcher; ROM `0x00021A14` holds
`FUN_000EDE12`, which builds and queues the transmit frame. The homologous
HCAN1 entries `FUN_000EB58C` and `FUN_000EB84E` occupy the adjacent slots
`0x0002193C` and `0x00021A10`.

`FUN_000EDC70` walks the 30 records of `0x000094C2`, selects the receive
records with pending data, and branches on the standard ID:

| Standard ID | Handler | Shadow payload byte 0 |
| ---: | --- | --- |
| `0x22A` | `FUN_000EE138` | `0xFFFF3E6B` |
| `0x22C` | `FUN_000EE29A` | `0xFFFF3E75` |
| `0x22D` | `FUN_000EE472` | `0xFFFF3E7F` |
| `0x230` | `FUN_000EE4BA` | `0xFFFF3E89` |
| `0x231` | `FUN_000EE558` | `0xFFFF3E93` |
| `0x232` | `FUN_000EE58C` | `0xFFFF3E9D` |

Every handler sets an arrival bit in `0xFFFF45AE`: bit 7 for `0x22D`, bit 6 for
`0x230`, bit 5 for `0x231`, bit 4 for `0x232`. `FUN_000EE138` and
`FUN_000EE29A` set arrival bits in `0xFFFF45AD` instead.

## Received signal placement

Byte indices are payload indices within the received frame.

`0x22A`, `FUN_000EE138`:

| Source | Destination |
| --- | --- |
| bytes 0-1 as a word | `0xFFFF41AC` |
| bytes 2-3 as a word | `0xFFFF41AE` |
| byte 4 bits 7-4 | `0xFFFF3C04` |
| byte 5 bit 7 | `0xFFFF4596` bit 5 |
| byte 5 bit 6 | `0xFFFF45AE` bit 2 |
| byte 5 bit 5 | `0xFFFF45AE` bit 3 |
| byte 5 bit 4 | `0xFFFF44EF` bit 7 |
| byte 5 bit 3 | `0xFFFF44F8` bit 5 |
| byte 6 | `0xFFFF42B0` |
| byte 7 bits 7-3 | `0xFFFF44F9` bits 4-0 |
| byte 7 bits 2-0 | `0xFFFF44FA` bits 7-5 |

`0x22C`, `FUN_000EE29A`, distributes single bits of payload bytes 0, 1, and 2
into the fault-status bytes `0xFFFF44F4`, `0xFFFF44F6`, `0xFFFF44F7`,
`0xFFFF44F8`, `0xFFFF44F9`, and `0xFFFF44FA`, and writes `0xFFFF5BB6` through
`0xFFFF5BBA` and `0xFFFF62B0`. The frame carries no scaled quantity.

`0x22D`, `FUN_000EE472`:

| Source | Destination |
| --- | --- |
| byte 0 bit 0 | `0xFFFF44F4` bit 1 |
| byte 1 bit 0 | `0xFFFF44F4` bit 3 |
| byte 2 bit 0 | `0xFFFF44F7` bit 6 |

`0x230`, `FUN_000EE4BA`:

| Source | Destination |
| --- | --- |
| byte 0 | `0xFFFF27CB` |
| byte 1 | `0xFFFF27CC` |
| byte 2 | `0xFFFF42BD` |
| byte 3 | `0xFFFF42BE` |
| byte 4 bits 7-4 | `0xFFFF42C4` |
| byte 4 bits 3-0 | `0xFFFF42C5` |
| byte 5 bits 7-4 | `0xFFFF42BB` |
| byte 5 bits 3-0 | `0xFFFF42BC` |
| bytes 6-7 as a word | `0xFFFF42C0` |

`0x231`, `FUN_000EE558`:

| Source | Destination |
| --- | --- |
| byte 0 | `0xFFFF42C6` |
| bytes 1-2 as a word | `0xFFFF42C2` |

`0x232`, `FUN_000EE58C`, uses payload byte 0 bits 2-0 as a channel selector and
stores it in `0xFFFF4151`. Selector `0` routes the word in bytes 1-2 to
`0xFFFF42FA` and its value shifted right by five and clamped to `0xFF` to
`0xFFFF42FC`. Selector `1` routes the same fields to `0xFFFF42FE` and
`0xFFFF4300`. Other selector values store nothing.

## Transmitted frame 0x22B

`FUN_000EE630` is the only producer of the eight payload bytes
`0xFFFF3E61` through `0xFFFF3E68` of HCAN0 mailbox 1.

| Payload byte | Source |
| ---: | --- |
| 0 | high byte of the word at `0xFFFF443E` |
| 1 | low byte of the word at `0xFFFF443E` |
| 2 | high byte of the word at `0xFFFF5D36` |
| 3 | low byte of the word at `0xFFFF5D36` |
| 4 bits 7-4 | `0xFFFF401D` bits 3-0 |
| 4 bits 3-0 | retained from the previous frame |
| 5 | status bits from `0xFFFF45B9`, `0xFFFF45C1`, `0xFFFF23B1`, `0xFFFF44E0`, `0xFFFF45AD` |
| 6 | `0xFFFF42EB` |
| 7 | status bits from `0xFFFF45C2`, `0xFFFF61C2`, `0xFFFF61C6`, `0xFFFF61C9` |

The same function mirrors the word at `0xFFFF443E` into `0xFFFF423C` after
moving the previous contents of `0xFFFF423C` to `0xFFFF423E`. `FUN_000EDF62`
reads that pair together with `0xFFFF41AC` and `0xFFFF41AE` and publishes them
through the diagnostic identifier tables.

## Unwritten transmit fields

No ROM instruction writes `0xFFFF443E` or `0xFFFF5D36`. Both cells lie inside
the zero-filled RAM ranges declared at ROM `0x0002266C`
(`0xFFFF2564..0xFFFF4876`) and ROM `0x0002268C` (`0xFFFF4878..0xFFFF6524`).
Payload bytes 0 through 3 of frame `0x22B` therefore leave the ECM as the
zero-initialized value.

Three independent passes establish the absence of a producer:

- the Ghidra decompiler SSA trace over all 3015 defined functions reports the
  two cells only as reads, at `0x000EE63A` and `0x000EE664`;
- the same trace's unresolved pointer-expression set contains no write whose
  anchor can reach either cell;
- a whole-ROM linear constant-tracking scan covering direct, displacement,
  indexed, and GBR-relative forms, including every region no function covers,
  finds no write.

The homologous 1ND0A cell `0xFFFEB73A` shows the same pattern: two reads in the
transmit builders at `0x00118282` and `0x00118BF0`, and no write.

Confirming the transmitted content on a vehicle requires a bus capture of frame
`0x22B` or the CONSULT-III Plus value published from `0xFFFF423C`. Static
analysis establishes the instruction set that reaches the payload, not the
electrical content of the private bus.

## Calibration boundary

No map-consuming function reads any RAM cell written by the six HCAN0 receive
handlers. The 691 interpolation-addressed tables of the exact ROM and the
handlers' 36 destination cells have an empty intersection. HCAN0 traffic
reaches diagnostic status bytes, the identifier publication tables, and the
telemetry staging block written by `FUN_000CC1FE`, and nothing else.

The exact ROM therefore contains no calibration surface bound to the private
bus, and no calibrated target is transmitted on it.

## Diagnostic descriptors

The DTC descriptor table occupies ROM `0x0001B7AC..0x0001C5EB` as 304 records of
12 bytes. A record contains:

```text
byte 0:   status-group byte offset
byte 1:   bit index within the status group
bytes 6-7: packed DTC code, one hexadecimal digit pair per byte
```

Twenty records carry the codes associated with the private-bus modules:

| Record | Index | Group | Bit | Code |
| ---: | ---: | ---: | ---: | --- |
| `0x1C46C` | 272 | `0x48` | 1 | `P1088` |
| `0x1C478` | 273 | `0x48` | 0 | `P1087` |
| `0x1C484` | 274 | `0x49` | 7 | `P1092` |
| `0x1C490` | 275 | `0x49` | 6 | `P1089` |
| `0x1C49C` | 276 | `0x49` | 5 | `P1092` |
| `0x1C4A8` | 277 | `0x49` | 4 | `P1089` |
| `0x1C4B4` | 278 | `0x49` | 3 | `P1092` |
| `0x1C4C0` | 279 | `0x49` | 2 | `P1089` |
| `0x1C4CC` | 280 | `0x49` | 1 | `P1092` |
| `0x1C4D8` | 281 | `0x49` | 0 | `P1089` |
| `0x1C4E4` | 282 | `0x4A` | 6 | `P1093` |
| `0x1C4F0` | 283 | `0x4A` | 5 | `P1090` |
| `0x1C4FC` | 284 | `0x4A` | 4 | `P1093` |
| `0x1C508` | 285 | `0x4A` | 3 | `P1090` |
| `0x1C520` | 287 | `0x4A` | 1 | `P1092` |
| `0x1C52C` | 288 | `0x4A` | 0 | `P1089` |
| `0x1C580` | 295 | `0x4B` | 1 | `P1091` |
| `0x1C58C` | 296 | `0x4B` | 0 | `P1091` |
| `0x1C5BC` | 300 | `0x55` | 3 | `P100B` |
| `0x1C5C8` | 301 | `0x55` | 2 | `P100A` |

Records 286, 289, 290, and 292 in the same groups carry `P1608`, `P1607`,
`P1607`, and `P1606`. Descriptor presence declares the code, not its stock
enable state; the enable state lives in the separate attribute array reached
through `JK78C.dtc.csv`.

## Hardware boundary

Static analysis does not establish bus wiring, module participation, physical
scaling of a received word, or the behavior of any module other than the ECM.
Promotion of a received field to a named physical quantity requires a bus
capture with a controlled operating condition and an independent observation.
