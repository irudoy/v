# 23710-JK08A - stock ROM

Owned dump from the physical `23710-JK08A` target ECU in a V36 Skyline 250GT,
read on 2026-07-26 with PCMFlash 1.2.0, module 18
`Nissan: EFI SH705822N, SH705828N (Hitachi SH7058/1MB)`, through a
Scanmatik-SM2 USB adapter.

## Contents

- `1JK08A-20260726-stock.bin` - flash ROM, 1,048,576 bytes (`0x100000`);
- `1JK08A-20260726-stock.bin.md5` - MD5 sidecar;
- `mods/immo-off/` - one-bit immo-off modification.
- `mods/map-switching/` - software-verified ten-family production map-switching image.

ROM hashes:

- SHA-256: `ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23`;
- MD5: `db4eeb16e6385afcb69e70955147c483`.

The MD5 matches the value produced by PCMFlash during the read. The package does
not include a PCMFlash identification screenshot.

## Identification

PCMFlash data agrees with strings inside the image:

| Field | Value | ROM offset |
|-------|-------|-----------:|
| ECM part # | `23710-JK08A` | PCMFlash identification |
| Calibration | `1JK08A00000` | `0x8204` |
| Main number / software ID | `7MFKAVN86` | `0x6f09`, `0x2259c` |
| EFI / MCU class | `SH705822N` | `0x50c6` |
| Protocol | Hitachi CAN | PCMFlash module profile |

The package contains only the main flash ROM. The absence of an EEPROM file does
not establish that the board has no external EEPROM; its presence and contents
remain a separate task.

## Comparison with JK03A

Donor `JK03A` has the same size, MCU, and `7MFKAVN86` software ID. The images
differ at 121 byte positions in 58 contiguous ranges, all within
`0x008200..0x0190c9`. These regions are byte-identical:

- `0x000000..0x0081ff`, SHA-256
  `d3b00d4ea983f0eaaa2085af4c79f087c8a6256379b11e5f962eefd121a4c902`;
- `0x020000..0x0fffff`, SHA-256
  `34726ad5cf8a81b632502102887273dad7c45e4e0a4f380163d251b386bb4c9e`.

The delta includes the ROM ID, checksum, four known 1D-16 `uint16` curves at
`0x15360`, `0x15380`, `0x19090`, and `0x190b0`, diagnostic descriptors, and
other configuration/calibration data. The separate JK08A Memgraph layer reuses
the common structure of the exact-code pair but measures values from this image.
The working `defs/JK08A.xml` and `defs/JK08A.xdf` do not expose the four
differing unnamed candidate curves; every other exposed table and axis is
byte-identical to the donor.
