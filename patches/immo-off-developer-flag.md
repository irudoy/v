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

## Supported ROMs

| ROM | Offset | Stock | Immo-off | Basis |
|-----|-------:|------:|---------:|-------|
| JK03A | `0x8725` | `0x01` | `0x00` | four code consumers |
| JK08A | `0x8725` | `0x01` | `0x00` | JK03A exact-code pair |
| JK00D | `0x8740` | `0x01` | `0x00` | four homologous consumers |
| JK78C | `0x861C` | `0x01` | `0x00` | homologous configuration block |
| 1ND0A / 1ND3B | `0x8668` | `0x01` | `0x00` | homologous configuration block and state machine |

The patcher verifies the SHA-256 of the exact stock ROM from
`rom-images/roms.csv` and the original byte value. An offset is not transferred
directly between independent builds.

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

## Usage

```bash
python3 patches/apply_immo_off.py --rom JK08A
```

Output:
`1JK08A-20260727-immo-off.bin` at a caller-selected output path.
The adjacent MD5 sidecar is
`1JK08A-20260727-immo-off.bin.md5`. The patcher never overwrites a differing BIN
or sidecar. The output directory is not a build input.

Verify without creating a file:

```bash
python3 patches/apply_immo_off.py --rom JK08A --verify-only
```
