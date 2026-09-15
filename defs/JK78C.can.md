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

## Producers of the transmit words

Both command words are latched copies made by `FUN_00020F1A`, the walker of the
periodic pointer list at `0x00021A4C` (144 entries). The main loop
`FUN_0002A7F4` calls it once per tick flag (bit 2 of `0xFFFF84B9`). With the
interrupt mask raised it copies input blocks before the walk and output blocks
after it through the block-copy helpers `FUN_00022164` and `FUN_000225C0`
(`r1` destination, `r2` source, `r0` length in bytes).

| Copy site | Destination | Source | Length | Position |
| --- | --- | --- | ---: | --- |
| `0x00021004` | `0xFFFF2588..0xFFFF25A7` | `0xFFFF25A8..0xFFFF25C7` | `0x20` | before the walk |
| `0x00021026` | `0xFFFF25D8..0xFFFF26D5` | `0xFFFF26D6..0xFFFF27D3` | `0xFE` | before the walk |
| `0x00021362` | `0xFFFF43FC..0xFFFF4467` | `0xFFFF4468..0xFFFF44D3` | `0x6C` | after the walk |
| `0x0002136C` | `0xFFFF5BE4..0xFFFF5D3B` | `0xFFFF5D3C..0xFFFF5E93` | `0x158` | after the walk |

The length of the last copy is built as `mov #0x56,r0; shll2 r0`. The copies
fix three bindings:

- `0xFFFF443E` is the copy of `0xFFFF44AA`;
- `0xFFFF5D36` is the copy of `0xFFFF5E8E`;
- `0xFFFF2670` and `0xFFFF2672`, the inputs of `FUN_0004C2B2`, are the copies of
  the VVEL TIM pair `0xFFFF276E` and `0xFFFF2770` written by `FUN_000EDF62`.

`0xFFFF44AA` is the VVEL command word. `FUN_00054FD0`, entry 98 of the periodic
list, writes it at `0x0005576C` and clears `0xFFFF44AC`. The value is the target
control-shaft angle in 1/512 degree units passed through the angle-to-command
curve (axis `0x000156DC`, values `0x000156FC`, lookup `FUN_00028320`) and
limited by four bound words computed earlier in the task; the reverse lookup of
the stored command lands in `0xFFFF35BA`. The target angle comes from
`FUN_000564A4`, which reads the maps `0x0000E1CE` and `0x0000E24E` (8x8 uint16,
axes `0x000160CA` and `0x000160DA`), `0x000108CE` (16x16 uint16, axes
`0x00016DE4` and `0x00016E04`) and the curves `0x0001600A`, `0x0001601A`,
`0x00016BB4`, `0x00016D14`, `0x00016DC4`. The task itself reads the curves
`0x0001609A`, `0x000160AA`, `0x000160BA`, `0x00016A74`, and its inputs include
the latched VVEL TIM pair at `0xFFFF25D8 + 0x98` and `+ 0x9A`. The same curve
pair serves both directions: `FUN_0004D3CE` converts the received angle into
model units for `FUN_0004C2B2`, and `FUN_00054FD0` converts the target angle
into the command.

`0xFFFF5E8E` is a signed 16-bit integrator of the bank difference.
`FUN_00080ED6(bank)` forms `0xFFFF194C` and `0xFFFF194E` from
`0xFFFF1A48[bank]`, which tracks `0xFFFF2238[bank]`, plus `0xFFFF225A[bank]`,
minus `0x6400`, saturated to `0..0xFFFF`. `FUN_00080FEC` stores the difference
of the two words in `0xFFFF1464` and its product with ROM `0x00008EC2`
(`0x0106`) in `0xFFFF1A5C`. `FUN_00081040` adds `0xFFFF1A5C` to `0xFFFF5E8E`
and saturates at +-ROM `0x00008FFE` (811) while bit 0 of `0xFFFF23E5` is set.
`FUN_00081126`, reached from entry 67 of the periodic list (`FUN_000756DC`),
runs this chain while bit 7 of ROM `0x00008957` (`0x3A`) is clear and otherwise
writes ROM `0x00008C6C` (0) into `0xFFFF5E8E`.

The transmit builder reads the two latched words at `0x000EE63A` and
`0x000EE664`. Confirming the transmitted content on a vehicle requires a bus
capture of frame `0x22B` or the CONSULT-III Plus value published from
`0xFFFF423C`.

The decompiler SSA trace, the GBR inventory, the pointer-argument join, and the
`FUN_000225C0` destination ranges do not reach either word: the block copies
pass their addresses and lengths in registers built by arithmetic, and the
helper body is an unrolled jump table. A cell without a direct static writer is
checked against the copy groups of `FUN_00020F1A` before any other conclusion.

## Calibration boundary

The six HCAN0 receive handlers write 36 RAM cells. Twenty-four of them are read
by functions outside the handler set, and one, `0xFFFF44EF`, is read by five of
the 378 functions that call the interpolation library. `0xFFFF44EF` is a
status-group byte written from many unrelated functions across the image, and
the handler sets a bit in it rather than publishing a measurement. The
remaining HCAN0 destinations reach diagnostic status bytes, the identifier
publication tables, and the telemetry staging block written by `FUN_000CC1FE`.

Payload bytes 0 through 3 of frame `0x22B` carry the calibrated command word
and the bank integrator described above; bytes 4 through 7 carry status bits.
The VVEL TIM pair written by `FUN_000EDF62` reaches the interpolation consumers
`FUN_0004C2B2` and `FUN_00054FD0` through the latch at `0xFFFF2670` and
`0xFFFF2672`, outside the direct-read census above.

The census behind these counts covers interpolation-addressed tables. The
`direct-row-major` and `direct-scalar` families of the map inventory are
addressed without the library and lie outside it, so the count constrains
library-addressed calibration and leaves direct addressing open.

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
