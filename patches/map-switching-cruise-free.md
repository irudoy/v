# Cruise-free Map Switching and EEPROM persistence

This document records the static cross-ROM engineering basis for selecting Map
Switching slots without cruise-control steering switches and retaining the
active slot in external serial EEPROM. It covers the registered SH7058 images
(`JK08A`, `JK00C`, `JK00D`, `JK78C`, plus the byte-identical 7MFK siblings
`JK00A`, `JK03A`, `JK03B`) and SH7059 images (`1ND0A`, `1ND3B`, `1ME3B`,
`1EK7A`).

The exact 7MFK family (`JK08A` and byte-identical siblings `JK00A`, `JK03A`,
`JK03B`) implements the cruise-free cyclic selector, stationary `0x284` latch,
configurable multi-channel cluster indication (`CRUISE`/`SET`, MIL
`0x551[3].5`, and stationary-only tachometer `0x180`/`0x1F9`), and two-copy
ping-pong EEPROM persistence (`0x0680..0x069F` and `0x0700..0x071F`, `MSPE` v1
configuration at `0x000D7200..0x000D720F`, cold/warm startup separation via
stock return address `0x00027C4C`, and stepped non-blocking SCI2 writer with
quarantine recovery on the 10.24 ms EEPROM task hook) with an optional
`[map_switching]` build profile section and full GNU SH-2E simulator coverage. Relocation of the cruise-free and EEPROM persistence extensions to
the remaining seven ROM profiles is tracked as follow-on work. This
specification defines the verified stock interfaces, qualified EEPROM storage
design, stationary vehicle-speed contract, and cluster indicator boundaries
required for implementation and hardware qualification.

## Stock serial EEPROM driver

All eight target ROMs access an external SPI EEPROM through synchronous SCI2 at
`0xFFFFF010` (`SMR2 = 0x80`, `BRR2 = 0x01`, `SDCR2 = 0xFA`, `TDR2 = 0xFFFFF013`,
`SSR2 = 0xFFFFF014`, `RDR2 = 0xFFFFF015`) with chip select on Port C `PCDR.4`
(`0xFFFFF73E`). Transactions mask and restore interrupts around chip-select
updates and save/restore `BRR2`, `SDCR2`, and `PLIR` (`0xFFFFF75C`).

Each entry below pairs the stock routine entry point with the store instruction
that writes the SPI command byte to `TDR2`:

| Image | `READ 0x03` | `WRITE 0x02` | `WREN 0x06` | `WRDI 0x04` | 32-byte `0xFF` fill |
| --- | --- | --- | --- | --- | --- |
| `JK08A` | `00066BD0 / 00066C38` | `000666B0 / 00066714` | `00068952 / 00068996` | `000688AC / 000688F0` | `00066510` |
| `JK00C` / `JK00D` | `00068E90 / 00068EF8` | `00068970 / 000689D4` | `0006AC22 / 0006AC66` | `0006AB7C / 0006ABC0` | `000687D0` |
| `JK78C` | `000851A4 / 0008520C` | `00084C84 / 00084CE8` | `00086F1A / 00086F5E` | `00086E74 / 00086EB8` | `00084AE4` |
| `1ND0A` / `1ND3B` | `00093EF8 / 00093FF0` | `00093424 / 00093494` | `00095B12 / 00095B62` | `00095A60 / 00095AB0` | `00093280` |
| `1ME3B` | `00099CFC / 00099DF4` | `000991FC / 00099272` | `0009BAC2 / 0009BB12` | `0009BA10 / 0009BA60` | `00099058` |
| `1EK7A` | `0009D9B8 / 0009DAB0` | `0009CEB8 / 0009CF2E` | `0009F792 / 0009F7E2` | `0009F6E0 / 0009F730` | `0009CB6C`, `0009CD10` |

SPI command bytes are followed by a 16-bit big-endian address. Under the 4 KiB
ST M95320 geometry (128 pages of 32 bytes, `A11..A0`, matching the
`rom-images/23710-JK03A/` ST95320 dump and the stock 32-byte fill stride and
`0x0FFF` upper checks):

- `WREN`, `WRITE`, and `WRDI` are issued as separate chip-select frames. The
  device internal write cycle begins when `WRITE` deselects chip select, so a
  persistence writer must poll the device write-in-progress (`WIP`) state with a
  bounded wait rather than relying on SCI2 transfer completion alone.
- Checked word readers (`JK08A:0006727C`, `1ND:000943D6`, `1ME3B:0009A234`,
  `1EK7A:0009DEF4`) compare two consecutive reads to catch transient bus errors
  but cannot detect an interrupted multi-byte write that settled into a
  corrupted value.

## 4 KiB EEPROM address census and page selection

Full call-site, operand, raw-pointer, and table censuses across all eight
registered ROMs separate fixed application records, finite ROM address tables,
queued requests, factory restore tables, and explicit whole-array service
sweeps:

| Image | Max fixed / startup page | Factory byte-restore table (tail) | Broad B16 write staging slot | Whole-array service sweep dispatcher |
| --- | --- | --- | --- | --- |
| `JK08A` | `0x16` (`0x200` / startup `0x24448`, 29 rows) | `0x24954` (159 rows, `0x05AA = 0x55`) | `FFFF3DC4` (service-only) | `000CD85C` |
| `JK00C` | `0x200` (startup `0x24540`, 29 rows, max `0x100`) | `0x24A6C` (161 rows, `0x05AA = 0x55`) | `FFFF3EFA` (service-only) | `000D94BA` |
| `JK00D` | `0x200` (startup `0x24540`, 29 rows, max `0x100`) | `0x24A6C` (161 rows, `0x05AA = 0x55`) | `FFFF3F0E` (service-only) | `000D9BF6` |
| `JK78C` | `0x200` (startup `0x254B0`, 29 rows, max `0x100`) | `0x258B4` (169 rows, `0x05AA = 0x55`) | `FFFF406C` (service-only) | `000FA1A4` |
| `1ND0A` / `1ND3B` | `0x320` (startup `0x25AD0`, 29 rows, max `0x100`) | `0x25EF4` (175 rows, `0x05AA = 0x55`) | `FFFEB32C` (service-only) | `0012604C` |
| `1ME3B` | `0x340` (startup `0x25CD0`, 41 rows) | `0x26200` (214 rows) | `FFFEB476` (service-only) | `0013339C` |
| `1EK7A` | `0x3E0` (startup `0x260EC`, 46 rows) | `0x26740` (278 rows, `0x05AA = 0x55`) | `FFFEB7C0` (service-only) | `00154458` |

Key allocation results across all eight ROMs:

- **No page is outside the explicit factory service sweep.** Every ROM contains
  a service dispatcher that fills and pattern-tests all 128 pages
  (`0x000..0xFE0`, stride 32). A persistent Map Switching format must therefore
  tolerate erasure of both copies and fall back cleanly to Map 1.
- **Selected static storage pages on all eight ROMs:** physical byte ranges
  **`0x0680..0x069F` (page `0x34`)** and **`0x0700..0x071F` (page `0x38`)**.
  - Both pages lie above the factory-restore tail (`0x05AA`) and below
    `0x0800`, so ST M95320 top-quarter and top-half block-protection settings
    leave them writable (whole-array protection still covers them and remains a
    board-level check).
  - Neither page intersects any fixed application record, short-word queue
    (`<= 0x01FF`), bounded ordinary byte-write producer (`0x0218..0x021B` in
    `JK78C:00084872`, `1ND:00092F8C`, `1ME3B:00098D64`, `1EK7A:0009C862`),
    retained DTC queue (`0x0330..0x0337`, `0x0340..0x0345` on `1ME3B` and
    `1EK7A`), startup restore table, factory byte-restore table, or conservative
    full-`u8` scan of the reviewed DTC/queued ROM word tables (`JK08A:0x23DE4..`,
    `JK00C`/`JK00D:0x23EDC..`, `JK78C:0x24CCC..`, `1ND0A`/`1ND3B:0x25298..`,
    `1ME3B:0x25498..`, `1EK7A:0x25858..`).
  - Page `0x30` (`0x0600..0x061F`) was rejected because out-of-range `u8` scans
    of the `JK08A` and `1ME3B` ROM word windows hit `0x0608`
    (`7mfk:000241F6 = 0x0304`) and `0x0618` (`1me3b:00025A2A = 0x0B0C`).
  - On every ROM, the broad byte-write staging slot has literal-derived stores
    only inside the explicit service dispatcher. General diagnostic byte reads
    may inspect either page without altering it.
  - Both pages are `0xFF` in the `23710-JK03A` ST95320 dump.
- **Open scope:** Board-level EEPROM part identity, protection-bit state, and
  power-loss behavior remain hardware qualification items on each board.

## Two-copy ping-pong persistence protocol

Each of the two selected 32-byte pages stores one 16-byte record in bytes
`0..15` while preserving bytes `16..31`:

| Page offset | Size | Field |
| --- | ---: | --- |
| `0..1` | 2 bytes | Record identifier |
| `2` | 1 byte | Format version |
| `3` | 1 byte | Selected slot (`1..5`) |
| `4..7` | 4 bytes | Monotonic 32-bit generation counter |
| `8..11` | 4 bytes | CRC32 over bytes `0..7` |
| `12..15` | 4 bytes | Aligned 4-byte commit marker (separate M95320 programming group) |

Boot and selection rules:

- Both pages are read and validated at boot. When both records are valid, the
  newer generation wins across 32-bit unsigned rollover.
- When both records are erased or invalid, or when two valid records carry equal
  or half-range-separated (`0x80000000`) generations, boot selects Map 1. Equal
  or half-range-separated ambiguity also inhibits new writes until resolved.
- Repeating the currently committed active slot schedules no EEPROM write.

Write transaction on the inactive page (leaving the active committed page
disjoint at every step):

1. **Invalidate destination marker:** write an invalid value to bytes `12..15`,
   wait for `WIP` completion, and read back the invalid marker.
2. **Program destination body:** write bytes `0..11`, wait for `WIP` completion,
   and read back both the exact 12-byte body and the invalid marker.
3. **Commit destination marker:** write the valid commit marker to bytes
   `12..15`, wait for `WIP` completion, and read back the complete 16-byte
   record.

Any failed or timed-out step aborts the update without touching the previously
committed page. Firmware implementations must serialize these transactions with
stock SCI2 activity, bound `WIP` waits, block writes on transport read failure,
and inhibit new writes during low-voltage or key-off states.

Under the reference M95320 command-group-local fault model (4-byte programming
groups, page-local wrap), exhaustive model verification passes across 125,345
prefix/interruption cases, 125 slot updates, 30 redundant selections, 133
invalid/ambiguous records, and 20,436 arbitrary-byte fault injections across all
three programming phases. Under a weaker whole-page corruption fault, the
previous page remains byte-invariant, while arbitrary corruption of the
destination page could forge a syntactically valid record; electrical power-down
behavior outside operating `VCC` remains a board-level qualification item.

## Cruise-free selector inputs and stationary contract

### Brake, dual APP, and engine speed

The brake input is `PH1` (`PHDR` at `0xFFFFF72C`, bit 1; high sets the RAM bit
on all eight ROMs). Physical stop-lamp vs ASCD brake-switch polarity on each
harness remains a bench check. APP1 and APP2 are unsigned 16-bit snapshots read
by Service `0x22` DIDs `0x120D` and `0x120E`, and the coarse RPM snapshot uses
nominal `12.5 RPM/count`:

| Image | `PH1` load -> RAM bit | DID `0x1305` byte / mask | APP1 / APP2 snapshots | RPM snapshot | Coarse speed snapshot |
| --- | --- | --- | --- | --- | --- |
| `JK08A` | `0003870E -> FFFF2451.7` | `FFFF3345 / 44` | `FFFF269E / FFFF26A2` | `FFFF11BC` | `FFFF110E` |
| `JK00C` | `0003922A -> FFFF24D5.7` | `FFFF341B / 44` | `FFFF272E / FFFF2732` | `FFFF11CA` | `FFFF111A` |
| `JK00D` | `0003922A -> FFFF24DD.7` | `FFFF342F / 44` | `FFFF2742 / FFFF2746` | `FFFF11CA` | `FFFF111A` |
| `JK78C` | `0003BE74 -> FFFF23B1.6` | `FFFF34EF / 54` | `FFFF25F8 / FFFF25FC` | `FFFF11AC` | `FFFF10FC` |
| `1ND0A` / `1ND3B` | `0003F706 -> FFFE9473.6` | `FFFEA6FB / 44` | `FFFE96F6 / FFFE96FA` | `FFFE81B6` | `FFFE8104` |
| `1ME3B` | `00042886 -> FFFE9443.6` | `FFFEA7E7 / 44` | `FFFE96CE / FFFE96D2` | `FFFE819E` | `FFFE80F8` |
| `1EK7A` | `00043872 -> FFFE944F.6` | `FFFEAA9F / 44` | `FFFE96F8 / FFFE96FC` | `FFFE81C4` | `FFFE811E` |

### Stationary vehicle-speed path (`0x284` / `0x280`)

The ROM-selected HCAN1 speed receiver is `0x284` (`01 08 50 80`) on SH7058 and
`0x280` (`01 08 50 00`) on SH7059. Each 10-byte software record stores state and
8-bit receive age followed by eight payload bytes; the fine speed source is
unsigned `BE16(payload[4:6])`:

| Image | RX descriptor | ROM selectors | RX dispatcher / call / decoder | Payload bytes 4–5 | Fine word / store | State / 8-bit age | Required RX gate bits | Age task ptr / entry |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `JK08A` | `0000978E: 01 08 50 80` | `8349=3B, 834F=02, 89C0=00` | `000C3B14 / 000C3CB8 / 000C4506` | `FFFF3B3D..3B3E` | `FFFF113C / 000C4558` | `FFFF3B37 / FFFF3B38` | `FFFF4185.7, FFFF4195.0` | `00021840 / 000C3994` |
| `JK00C` | `00009852: 01 08 50 80` | `834C=3B, 8352=02, 89E2=00` | `000C981C / 000C9A0E / 000CAFD8` | `FFFF3C6F..3C70` | `FFFF1148 / 000CB02A` | `FFFF3C69 / FFFF3C6A` | `FFFF4320.7, FFFF4331.0` | `000218C8 / 000C96A4` |
| `JK00D` | `00009862: 01 08 50 80` | `834C=3B, 8352=02, 89E3=00` | `000C9F58 / 000CA14A / 000CB714` | `FFFF3C83..3C84` | `FFFF1148 / 000CB766` | `FFFF3C7D / FFFF3C7E` | `FFFF4334.7, FFFF4345.0` | `000218C8 / 000C9DE0` |
| `JK78C` | `0000947E: 01 08 50 80` | `831D=3B, 8323=02, 883B=00` | `000EB58C / 000EB71C / 000EBF88` | `FFFF3DBB..3DBC` | `FFFF1128 / 000EBFDA` | `FFFF3DB5 / FFFF3DB6` | `FFFF44E0.7, FFFF44F0.1` | `00021928 / 000EB2DC` |
| `1ND0A` / `1ND3B` | `00009734: 01 08 50 00` | `832E=3B, 8334=01, 88CD=00` | `00114AE0 / 00114DD2 / 00115CCE` | `FFFEB06F..B070` | `FFFE812E / 00115D16` | `FFFEB069 / FFFEB06A` | `FFFEB7F4.6, FFFEB807.6` | `00021F2C / 00114900` |
| `1ME3B` | `00009818: 01 08 50 00` | `8331=3B, 8337=01, 88F6=00` | `00120830 / 00120B56 / 00121FA2` | `FFFEB1B3..B1B4` | `FFFE8120 / 00121FEA` | `FFFEB1AD / FFFEB1AE` | `FFFEB954.6, FFFEB967.6` | `00021F98 / 00120618` |
| `1EK7A` | `00009990: 01 08 50 00` | `8341=3B, 8347=01, 8960=00` | `00140E94 / 0014116E / 00142606` | `FFFEB4E9..B4EA` | `FFFE8144 / 00142654` | `FFFEB4E3 / FFFEB4E4` | `FFFEBCE0.6, FFFEBCF4.4` | `00022024 / 00140C7C` |

Why the stock fine/coarse speed words and stock age byte alone are insufficient:

- On SH7058, the decoder maps wire sentinel `0xFFFF` to `0` (`000C454A`,
  `000CB01C`, `000CB758`, `000EBFCC`); on SH7059, unsigned division by 10 maps
  `0xFFFF` to `6553`. Raw values `1..9` also quantize to fine word `0`.
- None of the decoders refresh their output when no new frame arrives, and the
  stock age byte starts at `0` at startup and during receiver recovery before
  any valid frame has been received.
- Sixteen registered PCAN-View vehicle captures (`hardware-results.toml`,
  `23710-JK00D` hardware running `JK08A`) measure 134,884 `0x284` frames (median
  `20.0 ms`, per-trace P99 `20.6..21.4 ms`, max ordinary gap `22.5 ms`) and
  138,438 `0x280` frames (median `20.0 ms`, P99 `20.8..21.2 ms`, max ordinary
  gap `22.7 ms`). In `9-turn-off.trc`, `0x284` stops for `71,841.0 ms` during
  ignition-off while `0x280` transmits 3,593 zero-speed frames across the same
  gap.

**Stationary predicate contract:**

```text
receiver_ready && observed_valid_frame_since_reset && sample_age_ms <= 30.72 && raw_speed == 0
```

- Start with `observed_valid_frame_since_reset = false`.
- While the selected ROM configuration and both receive gates hold, latch raw
  `BE16(payload[4:6])` and observation time on each new-frame processing event
  (standard data frame, DLC 8).
- Any accepted nonzero raw word (including `0xFFFF`) clears stationary
  immediately; expiry past **`30.72 ms`** (three `10.24 ms` CAN task periods),
  disabled gates, or receiver reset invalidates the sample until a new frame
  arrives.

## Cluster indication and alternate controls

### Stock MIL request (`0x551` byte 3 bit 5)

Across all eight ROMs, **`0x551` byte 3 bit 5 (`0x20`, active-high)** carries
the ECM diagnostic MIL request. Each serializer clears bits 5 and 6 (`0xC99F`)
and conditionally sets bit 5 (`0xCB20`) from the CAN snapshot copy of the live
diagnostic lamp bit (on `JK08A`, the diagnostic branch also tests `0xFFFF493E.7`,
the source reported in J1979 Mode 01 PID `0x01` at `00035B9A`):

| Image | Lamp publisher | Live bit -> CAN snapshot bit | Snapshot copy | `0x551` serializer / byte 3 store |
| --- | --- | --- | --- | --- |
| `JK08A` | `00080334` | `FFFF4251.3 -> FFFF4247.3` | `00021350` | `000C5372 / 000C53C6` |
| `JK00C` | `0008473C` | `FFFF43F9.1 -> FFFF43EE.1` | `000213CC` | `000CCB32 / 000CCBCA` |
| `JK00D` | `0008473C` | `FFFF440D.1 -> FFFF4402.1` | `000213CC` | `000CD26E / 000CD306` |
| `JK78C` | `000A1FA6` | `FFFF45C9.7 -> FFFF45BF.7` | `00021394` | `000ED03C / 000ED08E` |
| `1ND0A` / `1ND3B` | `000BEE64` | `FFFEB8FB.7 -> FFFEB8EE.7` | `00021826 / 00021828` | `00116E4C / 00116EFC` |
| `1ME3B` | `000C8730` | `FFFEBA69.1 -> FFFEBA5A.1` | `0002188A / 0002188C` | `00123264 / 001232CC` |
| `1EK7A` | `000CD8F4` | `FFFEBE0E.6 -> FFFEBDFF.6` | `000218CE / 000218D0` | `001438E0 / 00143948` |

Vehicle captures corroborate the ignition-on request: in `startup.trc`, bit 5
clears `60.4 ms` before the first positive RPM transmission; in `9-turn-off.trc`,
bit 5 asserts `11.1 ms` after the first zero-RPM frame and clears `40.0 ms`
before positive RPM resumes. Because `0x551` byte 3 bit 5 carries an active
diagnostic MIL meaning and passes through the meter lamp controller, pulsing it
for map confirmation requires preserving real fault status and validating meter
latency/bulb-check behavior on hardware.

### Stock RPM broadcasts (`0x180` and `0x1F9`)

Both `0x180` (bytes 0–1, `03 08 30 00`) and `0x1F9` (bytes 2–3, `03 08 3F 20`)
encode the same live unsigned 16-bit fine RPM word multiplied by 25 (nominal
`wire / 8` RPM, saturating at `0xFFFF` on SH7058 and `0xFFFE` on SH7059):

| Image | TX dispatcher | Live RPM word | `0x180` packer / load | `0x1F9` packer / load |
| --- | --- | --- | --- | --- |
| `JK08A` | `000C3DE4` | `FFFF11EE` | `000C577A / 000C5784` | `000C5236 / 000C530C` |
| `JK00C` | `000C9C5E` | `FFFF1200` | `000CD00C / 000CD016` | `000CC9F4 / 000CCACC` |
| `JK00D` | `000CA39A` | `FFFF1200` | `000CD748 / 000CD752` | `000CD130 / 000CD208` |
| `JK78C` | `000EB84E` | `FFFF11DA` | `000ED456 / 000ED460` | `000ECEC6 / 000ECFD6` |
| `1ND0A` / `1ND3B` | `001151D8` | `FFFE81E8` | `00117468 / 0011746E` | `00116CF8 / 00116DE6` |
| `1ME3B` | `00120F98` | `FFFE81D0` | `00123978 / 0012397E` | `001230D4 / 001231FE` |
| `1EK7A` | `001415D8` | `FFFE81F6` | `00144024 / 0014402A` | `00143750 / 0014387A` |

Because `0x180` and `0x1F9` are shared bus broadcasts consumed outside the
instrument cluster, using either field for tachometer slot feedback requires
bench and vehicle verification of every recipient (especially TCM and VDC/ABS).

### SLIP, VDC OFF, and other candidates

- **SLIP and VDC OFF:** Both the 2007 G35 (`MWI-37..38`) and 2013 G37
  (`MWI-38..39`) service manuals identify the ABS actuator and control unit as
  the factory sender of SLIP and VDC OFF indicator requests, not the ECM. All
  eight ECMs configure `0x354` as RX (`01 08 6A 80`); in 67,443 captured `0x354`
  frames, the Z34 TCS-OFF candidate bit (byte 4 bit 6) never asserted.
- **Other `0x551` fields:** Byte 0 carries the same coolant-temperature code as
  PID `0x05`; byte 5 bits 4–6 carry the stock ASCD display state (`map-switching-selector.md`).
- **Alternate switches (`0x5C5`, `0x60D`, Drive Mode, rear defogger, spare ADC):**
  `0x5C5` is RX-only on `JK08A`, `JK00C`, `JK00D`, `JK78C`, `1ND0A` and inactive
  on `1ND3B`, `1ME3B`, `1EK7A`; `0x60D` has no stock ECM TX descriptor. No
  dedicated Drive Mode, defogger, VDC switch, or free ADC channel is qualified
  across all targets.

## Open work before hardware testing

1. Relocate the cruise-free selector and two-copy EEPROM persistence runtime to
   the remaining seven registered ROM profiles (`JK00C`, `JK00D`, `JK78C`,
   `1ND0A`, `1ND3B`, `1ME3B`, `1EK7A`) with full `tools/sh-elf-run/` executable
   coverage.
2. Validate on bench and vehicle: installed EEPROM part/write-protection and
   power-loss recovery, stop-switch polarity, and cluster indication behavior
   (`0x551` MIL vs tachometer) on cruise-less vehicles.
