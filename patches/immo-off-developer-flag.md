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

| Role | JK00C function | JK00C read site | JK00D function | JK00D read site |
|------|----------------|----------------:|----------------|----------------:|
| state monitor | `FUN_000A92F4` | `0x000A9304` | `FUN_000A92E0` | `0x000A92F0` |
| main state machine | `FUN_000C177C` | `0x000C1838` | `FUN_000C1754` | `0x000C1810` |
| transition and inhibit-state normalization | `FUN_000C2362` | `0x000C2370` | `FUN_000C233A` | `0x000C2348` |
| engine inhibit formation | `FUN_000C2516` | `0x000C2522` | `FUN_000C24EE` | `0x000C24FA` |

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
eleven bit-0 read sites of the flag, nine through literal-pool words and two
GBR-relative, against the eleven literal-pool loaders of JK03A / JK08A, and no
`1ME3B` literal pool holds `0x8668`. The site is a code fact of the target image; the
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

## 1ND0A NATS state analysis

`../tools/ghidra/symbols.csv` names the 1ND0A NATS functions. They latch the
result of the BCM exchange into registered, Lock, and present bits and into
DTCs P1610-P1615 through calibrated thresholds. No function compares a stored
ID with a received one bytewise, and the Developer Immobilizer flag at `0x8668`
drives the engine inhibit without passing through this state.

| Element | Static evidence |
|---------|-----------------|
| ECM DTC descriptors | 12-byte records from `0x1BE00`; P1610-P1615 at indices 42-47, `0x1BFF8..0x1C040`, group `0x0D`, bits 5..0, code words `0x1BFFE..0x1C03A`; B2193 (`0xA193`) lies outside the table at `0x2742C` |
| `immo_dtc_status_engine` `FUN_000B741E` | 5,642-byte leaf; compares its condition with `0xFFFED298`; its tail touches CAN RAM `0xFFFEB844` and `0xFFFEBEFC`; the dispatcher `FUN_000B6988` handles monitor IDs `0x171` and `0x174` |
| `immo_channel_evaluator` `FUN_000CD374` | compares count `0xFFFE9782`, level `0xFFFE80FC`, and conditioned signal `0xFFFE880C` with ROM thresholds reached through `PTR_000CD514`, `PTR_000CD51C`, `PTR_000CD538`, `PTR_000CD53C`, and `PTR_000CD834`, among them `0x8941` and `0x8AE5` |
| `immo_registration` `FUN_000CCF08` | attempt counter `0xFFFEC7F7`/`0xFFFEC7F8` against `0x0B`; below it the registered bit tracks `0xFFFEA232.bit0`, set at `0x0CD012` and cleared at `0x0CCFFA`; at or above it the body is skipped; the eleven-entry event ring from `0xFFFEC7FA` is read by `FUN_000C4454`, `FUN_000C96E0`, `FUN_000CAF20`, `FUN_000CCCA0`, and `FUN_000F5CC8` |
| `immo_lock_setter` `FUN_000BF0AC` | writes the condition and DTC bits `0xFFFEB852..0xFFFEB859` |
| Injection enable | `0xFFFEB7F3.bit6` is an unconditional copy of `0xFFFEB7F4`, which `FUN_0003FB4E` fills from `0xFFFFF75E` |
| CAN transmit builders | `FUN_0000423C`, `FUN_000043C6`, `FUN_0011B218`, and `FUN_00000830` with packer `FUN_00003258` read payload sources `0xFFFF8248` and `0xFFFF0850` and frame counter `0xFFFF800C`, and no address in `0xFFFExxxx` |

The eleven Lock readers write no hardware register. Their RAM writes meet the
reads of the 80 hardware writers at four addresses: `0xFFFEB825` and
`0xFFFED704` are read only by `consult_actuator_test` `FUN_0012604C`, while
`0xFFFEB8C8` and the shared status byte `0xFFFEB818` feed status and lamp
paths. The 26 functions of the NATS domain write 569 RAM addresses, of which
the sixteen ATU-II injection and ignition timer writers read four:
`0xFFFEB825`, `0xFFFEB82A`, `0xFFFEB831`, and `0xFFFED704`. All four reach the
timers only through `consult_actuator_test` and the reset routine
`FUN_00125EE0`.

The analysis excludes a fuel or spark cut driven by Lock, registration,
immo-present, or immo-DTC within zero and one hop. Deeper data flow, another
security state, the main relay, the fuel pump, and a separate handshake or
transmit path remain outside that boundary.

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
