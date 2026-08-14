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

The code-proven period is `Tcan = 204800 / Pphi` seconds. The board-level
candidate `Pphi = 20 MHz` gives `Tcan = 10.24 ms`; physical timestamps remain
the hardware gate. Frame `0x512` additionally requires `0xFFFF4231.bit2`.

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

Other field names require a code trace or a synchronized vehicle capture.
Geometry copied from a Z34 frame list is not exact JK08A evidence.

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
| `0xFFFFD850` | MBIMR1; zero enables a mailbox activity interrupt |
| `0xFFFFDC40` | physical mailbox 26 control base |
| `0xFFFFDC48` | physical mailbox 26 eight-byte data field |

For physical mailbox 26, the corresponding TXPR1, TXACK1, ABACK1, and MBIMR1
bit is bit 10, or `0x0400`.

## Safe extension boundary

Physical mailbox 26 is the only table-owned inactive mailbox that can be
promoted without replacing a stock receive or transmit role. A type-4 record
would configure it as a transmit mailbox and automatically enable its
mailbox-empty interrupt while keeping it outside the stock type-3 scans.

Mailbox 31 is also initialized inactive, but the SH7058S manual has a specific
transmit-cancellation limitation for mailbox 31. It is not part of the baseline
extension design.

The implemented custom telemetry layer promotes mailbox 26 to type 4 only when
its build configuration is enabled. It replaces the SLE1 vector with one
combined handler that services mailbox 26 and reproduces the complete stock
mailbox-28 success and abort behavior before executing `RTE`. The stock handler
cannot be called with `JSR` because it owns the exception return, and an
indirect tail jump would consume a general register whose entry value the stock
prologue must preserve. The combined handler therefore saves `r0..r7` and PR,
services the bounded queue, executes the exact mailbox-28 side effects, restores
the interrupted state, and returns through one `RTE`.

The custom telemetry implementation that uses this boundary is specified in
`../patches/can-telemetry.md`.
