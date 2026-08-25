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
