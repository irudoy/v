# 23710-1ME3B additional evidence

This is an owned bench read from the physical ECU made on 2026-08-25 with
PCMFlash module 18 (DLL 1.0.0.124) through Scanmatik-SM2 USB under the
`EFI SH705927N (Hitachi SH7059/1.5MB)` protocol. The original PCMFlash
filename was `11ME3B_9FZ3V5DD1-20260825-205525`, and
`11ME3B-20260825-pcmflash-identification.txt` retains the read and
identification record. The ECU label carries the Hitachi hardware identifier
`MEC108-280 D1` and lot `0705`.

The donor vehicle is a JDM KY51 Fuga with VQ37VHR, known directly from the
ECU it was removed from. PCMFlash reports part number `23710-1ME3B`,
SW version `11ME3B00000`, base `9FZ3V5DD1`, and the Hitachi CAN protocol.
The image confirms every identifier through its own strings: `SH705927N` at
`0x0050D2`, `9FZ3V5DD1` at `0x006F09`, and `11ME3B0000011ME3B00000` at
`0x008204`. The package contains no external EEPROM read; this does not
establish that the hardware lacks one.

`1ME3B` is a distinct code base. It shares the SH7059 class, the 1.5 MiB
flash, and the boot and vector blocks below `0x008200` with `1ND0A` and
`1ND3B`, but its application layout is independent: programmed content reaches
`0x139DC3` against `0x12C98F` in the `1ND` pair, symmetric exact 64-byte code
windows cover 18.96 percent, and `radiff2 6.1.6` reports Myers similarity
`0.815` with edit distance `581,292`.

Two independent structures carry across from `1ND` at relocated addresses. The
four `1ND` SUM16 checksum domains reproduce exactly at their `1ND` field
addresses `0x005FFE`, `0x006EFE`, `0x008200`, and `0x020000`, while the
application XOR and SUM fields move from `0x009610` and `0x009618` to
`0x0096F4` and `0x0096FC`. The diagnostic descriptor region is byte-identical
across 1,936 bytes at a constant `+0x164` relocation, placing `1ND0A`
`0x01C558:0x01CCE8` at `0x01C6BC:0x01CE4C`. It carries the VQ37 group `0x37`
sequence that ends at sub-index `02` and continues with group `0x38`, so this
image has the VQ37 architecture without exhaust camshaft timing control.

The image has no registered checksum layout, address profile, Ghidra export,
Memgraph layer, or definition target. Its declared family boundary forbids
address inheritance from any other image in the collection.

Identity and stock hashes are authoritative in `../roms.csv` and
`../README.md`; family classification and pairwise measurements are in
`../homology.toml` and `../homology.csv`.
