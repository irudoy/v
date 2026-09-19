# ECM immo-off through the Developer Immobilizer flag

## Purpose

ECM immo-off is implemented by clearing bit 0 of the factory Developer
Immobilizer configuration flag. The patch does not replace an ID-check result or
change synchronization data in the external EEPROM.

For the JK03A / JK08A exact-code pair:

```text
ROM[0x00008725]: 0x01 -> 0x00
```

One bit changes. The flasher corrects checksums while writing.

## Verified ROM sites

| ROM | Offset | Stock | Immo-off | Basis |
|-----|-------:|------:|---------:|-------|
| JK03A | `0x8725` | `0x01` | `0x00` | four code consumers |
| JK08A | `0x8725` | `0x01` | `0x00` | JK03A exact-code pair |
| JK00C | `0x873F` | `0x01` | `0x00` | four homologous consumers |
| JK00D | `0x8740` | `0x01` | `0x00` | four homologous consumers |
| JK78C | `0x861C` | `0x01` | `0x00` | homologous configuration block |
| 1ND0A / 1ND3B | `0x8668` | `0x01` | `0x00` | homologous configuration block and state machine |
| 1ME3B | `0x8671` | `0x01` | `0x00` | 1ND0A configuration block and eleven paired consumers |

Each site is bound to its independently analyzed ROM. An offset is not
transferred directly between independent builds. Every site above is published
as a Developer Immobilizer control in its own definition, and the projection
re-reads the stock byte from the target image before emitting the control.

Hardware evidence covers a JK08A-derived image on a 23710-JK00D ECU. No other
image carries a hardware result, and the published control states this.

## JK03A / JK08A execution path

Four functions read bit 0 at `0x8725`:

| Function | Read site | Role |
|----------|----------:|------|
| `FUN_000A3F96` | `0x000A3FA6` | state monitor |
| `FUN_000BBC88` | `0x000BBD42` | main state machine |
| `FUN_000BC82E` | `0x000BC83C` | transition and inhibit-state normalization |
| `FUN_000BC9E4` | `0x000BC9F0` | engine inhibit formation |

Wrapper `FUN_000BCB60` invokes the path in a fixed order:

```text
BBC88 -> BC00E -> BC220 -> BC388 -> BC82E -> BC9E4
```

When `ROM[0x8725].bit0 = 0`, `FUN_000BC82E` bypasses the Developer
Immobilizer transitions and clears `0xFFFF55E4.bit2`. The following
`FUN_000BC9E4` clears `0xFFFF4198.bit1`.

`0xFFFF4198.bit1` is the engine inhibit:

- when the bit is set, `FUN_00029588` clears the per-cylinder mask at
  `0xFFFF13D1`;
- when the bit is set, `FUN_0002AF38` skips configuration of ATU-II engine
  events and also clears `0xFFFF13D1`;
- when the bit is clear, the one-bit mask for the current cylinder is written to
  the high byte of `POPCR` at `0xFFFFF700`.

`POPCR[15:8]` contains `PULS7ROE..PULS0ROE`, which permit clearing the
corresponding APC pulse outputs on a `GR11B/TCNT11` compare match. The flag
therefore controls the actuator-level inhibit for engine pulses, not merely a
diagnostic status.

## 8MFK execution path

`8MFK` keeps the four-consumer shape with its own addresses. The read sites are
bound to each image:

| Role | JK00C read site | JK00D read site |
|------|----------------:|----------------:|
| state monitor | `0x000A9304` | `0x000A92F0` |
| main state machine | `0x000C1838` | `0x000C1810` |
| transition and inhibit-state normalization | `0x000C2370` | `0x000C2348` |
| engine inhibit formation | `0x000C2522` | `0x000C24FA` |

The main state machine widens the byte through `extu.b` before the bit test
instead of loading it into `R0` directly. The remaining three sites match the
JK03A / JK08A instruction sequence. Each flag carries eleven literal-pool
references across the image, the same count as JK03A / JK08A.

## 1ME3B site

`1ME3B` relocates no code from any modelled ROM, so its site is bound through
the `1ND0A` flag in three independent ways.

The 24 configuration bytes at `1ND0A` `0x8660..0x8677`
(`00 FF 00 0A 0A 05 18 05 01 05 64 50 46 28 2D 28 C8 7D AA 82 00 64 00 C8`)
occur exactly once in `1ME3B`, at `0x8669`. The flag byte `0x8668` of that
window lands on `0x8671`, which holds `0x01`.

Nine literal-pool words hold the flag address in each image, and each word has
one `mov.l @(disp,pc)` loader. The loaders pair in address order, and the
instruction words that follow each pair are equal apart from PC-relative
displacements: a byte read and a bit-0 test.

| `1ND0A` loader | `1ME3B` loader | Test after the load |
|---------------:|---------------:|---------------------|
| `0x10D176` | `0x118F1C` | `mov.b @r2,r0; and #1,r0` |
| `0x10D2E6` | `0x11908A` | `tst.b #1,@(r0,gbr)` with GBR loaded with 0 |
| `0x10D592` | `0x119340` | `mov.b @r2,r0; and #1,r0` |
| `0x11B632` | `0x127C3E` | `mov.b @r6,r0; tst #1,r0` |
| `0x11BEFC` | `0x1285A0` | `mov.b @r6,r0; tst #1,r0` |
| `0x11CD7A` | `0x1295E6` | `mov.b @r6,r0; and #1,r0` |
| `0x11D7E6` | `0x12A216` | `mov.b @r1,r0; and #1,r0` |
| `0x11DEA6` | `0x12A8D6` | `mov #1,r4; mov.b @r1,r0; and #1,r0` |
| `0x11E1F4` | `0x12AC2C` | `mov #1,r5; mov.b @r1,r0; and #1,r0` |

Two further consumers reach the byte through `tst.b #1,@(r0,gbr)` with a
GBR-relative literal, which a search for the absolute address does not see:

| Image | Function | GBR | Literal | Effective address |
|-------|----------|----:|--------:|------------------:|
| `1ND0A` | `FUN_000EA0A0`, load `0xEA0DC` | `0xFFFEB7ED` | `0x0001CE7B` | `0x8668` |
| `1ME3B` | `FUN_000F68B8`, load `0xF68F4` | `0xFFFEB94D` | `0x0001CD24` | `0x8671` |
| `1ND0A` | `FUN_0010C764`, load `0x10C9A6` | `0xFFFEB7EE` | `0x0001CE7A` | `0x8668` |
| `1ME3B` | `FUN_001184C8`, load `0x1186F6` | `0xFFFEB954` | `0x0001CD1D` | `0x8671` |

`FUN_000EA0A0` and `FUN_000F68B8` have equal instruction-shape hashes and read
the flag at instruction ordinal 31 of 130 bytes. Each image therefore carries
eleven consumers of the flag, the same count as JK03A / JK08A, and no `1ME3B`
literal pool holds `0x8668`. The site is a code fact of the target image; the
engine-inhibit path behind it is inherited from the `1ND` state machine by
pairing and carries no hardware result.

## Adjacent NATS states

The following states belong to registration, Lock, and diagnostics, but are not
part of the immo-off execution path:

| JK03A / JK08A state | Address | Function |
|---------------------|---------|----------|
| registered channel 0 | `0xFFFF41C1.bit0` | `FUN_000937DC` |
| registered channel 1 | `0xFFFF41C2.bit6` | `FUN_000937DC` |
| Lock | `0xFFFF4201.bit2` | `FUN_0008D724` |
| NATS DTC | `P1610-P1615` | shared diagnostic path |

Disabling Developer Immobilizer and suppressing DTCs are independent tasks.
Immo-off may leave NATS DTCs and the security indicator active.

## JK08A hardware test

The one-bit image with SHA-256
`de7f99cfb592d1cd1d83706f08cbea99ad0aef8602090d009cb37e9d37080d8c`
was tested on 2026-07-27 in a replacement JK00D ECU installed in a V36 Skyline
250GT with a VQ25HR engine. The engine starts and runs normally. The derived
artifact is reproducible and is not retained under `rom-images/`.

DTC P1610 remains in the ECM and returns after clearing. It does not block engine
starting or operation. This hardware result confirms the separation between the
Developer Immobilizer actuator flag and the adjacent diagnostic path. The full
P0 `read -> patch -> write` cycle is complete.

## Definition control

`defs/JK08A.xml` exposes Developer Immobilizer as a reversible RomRaider
switch. `defs/JK08A.xdf` exposes the same byte as a one-entry TunerPro patch
with exact stock `basedata`. Both controls use `01` for the stock state and
`00` for immo-off. Checksum correction remains part of the editor and flashing
workflow.
