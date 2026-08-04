# 23710-JK00A - stock ROM

Owned dump from a physical `23710-JK00A` ECU, read on 2026-08-04 with
PCMFlash 1.2.0, module 18
`Nissan: EFI SH705822N, SH705828N (Hitachi SH7058/1MB)`, through a
Scanmatik-SM2 USB adapter.

The original PCMFlash filename was
`1JK00A_7MFKAVN86-20260804-160509_MEC100-120-C1-7515.bin`. Its identity fields
and read time are retained here as provenance; the stored binary uses the
project's canonical name.

## Contents

- `1JK00A-20260804-stock.bin` - flash ROM, 1,048,576 bytes (`0x100000`);
- `1JK00A-20260804-stock.bin.md5` - MD5 sidecar.

ROM hashes:

- SHA-256: `ed0941de8435d9c61ac093a293757b93ad81bd413270a348c44a8fb6b78b6118`;
- MD5: `ab44e29b39f8aeca99b5c358548fd229`.

## Identification

The PCMFlash identity agrees with strings inside the image:

| Field | Value | Evidence |
|-------|-------|----------|
| ECM part # | `23710-JK00A` | physical ECU identification |
| Calibration | `1JK00A00000` | ROM `0x8204` |
| Main number / software ID | `7MFKAVN86` | ROM `0x6f09`, `0x2259c` |
| EFI / MCU class | `SH705822N` | ROM `0x50c6`, `0x225ba` |
| Hitachi hardware | `MEC100-120 C1`, lot `7515` | original read filename / ECU identification |
| Protocol | Hitachi CAN | PCMFlash module profile |

The image independently satisfies all six checksum references documented for
the JK00A / JK03A / JK03B / JK08A exact-code family. The complete stock line
`[0x8080, 0x8100)` contains `0xEE`.

## Application and exact-code relationship

Public exact-part listings identify `23710-JK00A` as an automatic JDM PV36
Skyline 350GT ECU with a VQ35HR engine. This application evidence is
marketplace-grade. The ROM provides an independent structural result: its known
executable ranges `0x000000..0x0081ff` and `0x020000..0x0fffff` are
byte-identical to JK03A, JK03B, and JK08A, and all four images use software ID
`7MFKAVN86`. The exact-code family therefore spans VQ35HR and VQ25HR
applications.

JK00A differs from JK03A at 9,125 byte positions in 1,430 contiguous ranges,
from JK03B at 9,118 positions in 1,439 ranges, and from JK08A at 9,163 positions
in 1,425 ranges. Every difference is within `0x008200..0x0191ad`. These are
separate stock calibration and configuration images. JK00A has no Ghidra export
or Memgraph layer and does not inherit the live JK08A annotation set; its
`roms.csv` graph label is empty.

JK00A and JK00C carry the same `MEC100-120 C1` hardware identifier but use
different software IDs and differ at 828,829 byte positions. The hardware label
does not establish an exact-code relationship.

Application sources:

- https://www.carsjp.ru/parts/nissan/skyline/blok_upravleniya_dvs
- https://www.wiweb.ru/vladivostok/parts/auto?mark=nissan&model=skyline&page=2&sort=date_asc
