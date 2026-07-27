# 23710-JK03A

Stock package for a V36 Skyline 250GT 2WD 5AT with a VQ25HR engine. The main ROM
and external SPI EEPROM were imported into the project on 2026-07-15.

## Contents

- `1JK03A-20260715-stock.bin` - flash ROM, 1,048,576 bytes (`0x100000`);
- `1JK03A-20260715-stock.bin.md5` - MD5 sidecar for the main ROM;
- `ST95320-20260715-nats-sync.bin` - external SPI EEPROM, 4,096 bytes;
- `ST95320-20260715-nats-sync.bin.md5` - EEPROM MD5 sidecar.

Main ROM hashes:

- SHA-256: `f78929547c08dc5ecde256fb3a6f6f3ef6daa9010e1531b3eac99fd9509225b4`;
- MD5: `52b9f9dcb2b0336d842eb29b66f9037e`.

EEPROM hashes:

- SHA-256: `68bb95f6ed70ec247f752a2d6817c83f14cdb7dc9db55c316852c0be0d362aaf`;
- MD5: `e836c9331545113460eac37c5c3b6f82`.

## Identification

| Field | Value | ROM offset |
|-------|-------|-----------:|
| ECM part # | `23710-JK03A` | package identification |
| Calibration | `1JK03A00000` | `0x8204` |
| Software ID | `7MFKAVN86` | `0x6F09` |
| EFI / MCU class | `SH705822N` | `0x50C6` |

`ST95320-20260715-nats-sync.bin` contains NATS synchronization/adaptation data
and is not MCU flash ROM. It has no graph label in `roms.csv`.
