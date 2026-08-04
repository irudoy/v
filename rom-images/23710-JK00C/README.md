# 23710-JK00C - stock ROM

Owned pre-write dump from a physical `23710-JK00C` ECU, read on 2026-08-03
with PCMFlash 1.2.0, module 18
`Nissan: EFI SH705822N, SH705828N (Hitachi SH7058/1MB)`, through a
Scanmatik-SM2 USB adapter.

The original PCMFlash filename was
`1JK00C_8MFKPCN14-20260803-221649_MEC100-120-C1-6Z03.bin`. Its identity fields
and read time are retained here as provenance; the stored binary uses the
project's canonical name.

## Contents

- `1JK00C-20260803-stock.bin` - flash ROM, 1,048,576 bytes (`0x100000`);
- `1JK00C-20260803-stock.bin.md5` - MD5 sidecar.

ROM hashes:

- SHA-256: `b287ef26373cd6d06a0b9f206648e9b8890a2a5b6cde982bb9d918d77eb69289`;
- MD5: `db15ba6b449163b4025c4a9ae9acd254`.

## Identification

The PCMFlash identity agrees with strings inside the image:

| Field | Value | Evidence |
|-------|-------|----------|
| ECM part # | `23710-JK00C` | physical ECU identification |
| Calibration | `1JK00C00000` | ROM `0x8204` |
| Main number / software ID | `8MFKPCN14` | ROM `0x7009`, `0x22628` |
| EFI / MCU class | `SH705822N` | ROM `0x50c6`, `0x22646` |
| Hitachi hardware | `MEC100-120 C1`, lot `6Z03` | original read filename / ECU identification |
| Protocol | Hitachi CAN | PCMFlash module profile |

The source ECU was subsequently used for the controlled map-switching
`FAIL-BOOT` reproduction. This file is its stock baseline before any project
write, not a readback of the later JK08A or map-switching images.
It has no Ghidra export or Memgraph layer, so its `roms.csv` graph label is
empty.

## Application and comparison

Public listings identify the `MEC100-120 C1` hardware family as the automatic
JDM PV36 Skyline 350GT with a VQ35HR engine. No public catalog entry for the
exact `23710-JK00C` suffix was found, so the vehicle application is
hardware-family evidence rather than exact-part catalog evidence.

The image is not an exact-code relative of the owned JK00D VQ35HR dump. The two
one-MiB SH7058 images use different software IDs and differ at 466,806 byte
positions. The complete stock line `[0x8080, 0x8100)` contains `0x00`.

Application source:

- https://www.ebay.com/itm/284029944805
