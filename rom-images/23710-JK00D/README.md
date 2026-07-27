# 23710-JK00D - stock ROM

Owned dump from the physical `23710-JK00D` bench ECU, read on 2026-07-26 with
PCMFlash 1.2.0, module 18
`Nissan: EFI SH705822N, SH705828N (Hitachi SH7058/1MB)`, through a
Scanmatik-SM2 USB adapter.

## Contents

- `1JK00D-20260726-stock.bin` - flash ROM, 1,048,576 bytes (`0x100000`);
- `1JK00D-20260726-stock.bin.md5` - MD5 sidecar;
- `1JK00D-20260726-pcmflash-identification.png` - screenshot of successful
  PCMFlash identification.

ROM hashes:

- SHA-256: `e2d7a374b4f7cb42d1963e7aeea424f2147ef01afd231f31b599d83f87f315d3`;
- MD5: `e22136ffcb90319c4e1ab678d0ee5fbe`.

## Identification

PCMFlash identification agrees with strings inside the image:

| Field | Value | ROM offset |
|-------|-------|-----------:|
| ECM part # | `23710-JK00D` | PCMFlash identification |
| Calibration | `1JK00D00000` | `0x8204` |
| Main number / software ID | `8MFK36N15` | `0x7009` |
| EFI / MCU class | `SH705822N` | `0x50C6` |
| Protocol | Hitachi CAN | PCMFlash identification |

The package contains only the main flash ROM. The absence of an EEPROM file does
not establish that the board has no external EEPROM; its presence and contents
remain a separate task.
