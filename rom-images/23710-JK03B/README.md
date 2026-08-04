# 23710-JK03B - stock ROM

Owned pre-write dump from a physical `23710-JK03B` ECU, read on 2026-08-04
with PCMFlash 1.2.0, module 18
`Nissan: EFI SH705822N, SH705828N (Hitachi SH7058/1MB)`, through a
Scanmatik-SM2 USB adapter.

The original PCMFlash filename was
`1JK03B_7MFKAVN86-20260804-013935_MEC100-191-A1-7911.bin`. Its identity fields
and read time are retained here as provenance; the stored binary uses the
project's canonical name.

## Contents

- `1JK03B-20260804-stock.bin` - flash ROM, 1,048,576 bytes (`0x100000`);
- `1JK03B-20260804-stock.bin.md5` - MD5 sidecar.

ROM hashes:

- SHA-256: `a9aa7a337375b7c9419b0970c32674e98f12ea4215c079898190c5c771a96f1a`;
- MD5: `d22d789a71075b35d06c1a3696e03a64`.

## Identification

The PCMFlash identity agrees with strings inside the image:

| Field | Value | Evidence |
|-------|-------|----------|
| ECM part # | `23710-JK03B` | physical ECU identification |
| Calibration | `1JK03B00000` | ROM `0x8204` |
| Main number / software ID | `7MFKAVN86` | ROM `0x6f09`, `0x2259c` |
| EFI / MCU class | `SH705822N` | ROM `0x50c6`, `0x225ba` |
| Hitachi hardware | `MEC100-191 A1`, lot `7911` | original read filename / ECU identification |
| Protocol | Hitachi CAN | PCMFlash module profile |

The image independently satisfies all six checksum references documented for
the JK00A / JK03A / JK03B / JK08A exact-code family.

## Application and exact-code relationship

Exact-part and hardware-family sources identify this ECU as a JDM V36 Skyline
250GT with a VQ25HR engine and automatic transmission. The ROM provides an
independent structural cross-check: its known executable ranges
`0x000000..0x0081ff` and `0x020000..0x0fffff` are byte-identical to JK00A,
JK03A, and JK08A, and all four images use software ID `7MFKAVN86`.

JK03B differs from JK00A at 9,118 byte positions in 1,439 contiguous ranges,
all within `0x008200..0x0191ad`. It differs from JK03A at 118 positions in 44
ranges, all within `0x008200..0x014ff1`, and from JK08A at 229 positions in 94
ranges, all within `0x008200..0x0190c9`. These are separate stock calibration
and configuration images in one exact-code family; JK03B does not inherit the
live JK08A annotation set until it has its own export and graph layer. Its
`roms.csv` graph label is therefore empty.

The complete pre-write line `[0x8080, 0x8100)` contains `0xEE`. The later
marker-only readback from the same programming workflow contains `0x00` there,
so the zero line is not an unconditional PCMFlash read transformation. The
remaining evidence does not distinguish checksum-correction behavior from a
core module-18 programming rule.

Application sources:

- https://otomotiv-forum.com/threads/chip-ttyuning-nissan-skyline-v36-at-2-5i-proshivka-yevro-2-tyun.63512/
- https://yahoo.aleado.com/lot?auctionID=m403371593
