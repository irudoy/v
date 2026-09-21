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
flash, and the boot and vector blocks with `1ND0A`: below `0x008200` the two
images differ at only 14 byte positions, namely a four-byte value at
`0x005FE0`, the stored SUM16 fields at `0x005FFE` and `0x006EFE`, and the
software identifier at `0x006F09`. The application layout above that boundary
is independent: programmed content reaches
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

The descriptor region holds 334 twelve-byte records at `0x01BF58` followed by
their 334 attribute pointers at `0x01CF00`, against 331 records at `0x01BE00`
in `1ND0A`. `../../defs/1ME3B.dtc.csv` carries 38 canonical codes out of it;
`P0443`, `P1422`, and the eight exhaust valve timing records have no
byte-identical record in this image. The relocation
is uniform only inside the 1,936-byte window: across the 38 codes shared with
`1ND0A` the records sit at `+0x14C`, `+0x158`, and `+0x164`, at index offsets of
`-1`, `0`, and `+1`. Each binding is therefore read from this image through the
record and its own attribute pointer rather than derived from an offset.

## Checksum verification

`../../patches/checksum-layouts.toml` registers the image as layout
`sh7059_1me3b` with the `1ND` domain geometry and the runtime fields at
`0x0096F4` and `0x0096FC`. The verifiers are located in the image. `0x002C60`
is byte-identical to the `1ND` function and incrementally verifies the
`0x008200` and `0x020000` SUM16 fields. `0x021A78` and `0x021B8E` accumulate
the application XOR and SUM over `0x008200:0x180000` in the runtime, skipping
the `0x008200` word, both fields, and the `0x020000` word; `0x021C74` compares
the accumulators with the two fields. `0x013339C` compares the same two fields
and the `0x005FFE` and `0x006EFE` SUM16 fields with values it computes itself,
as `0x12604C` does in `1ND0A`. The stock image reproduces all six fields under
the registered layout.

## Structure export and cross-ROM correspondence

Headless recovery folds 82,820 instructions in 578 regions into functions with
no failure, leaving 2,320 functions, 3,695 resolved call edges, 97,939
peripheral and RAM references, and 445,342 instructions. The Memgraph structure
layer holds 2,320 `Func` nodes, 13,464 `Reg` nodes, and 55,608 `USES` edges.

Whole-function hashes pair this image with `1ND0A` far more strongly than with
JK78C. Counting only hashes that are unique on both sides, `1ND0A` gives 1,021
instruction-shape pairs and 636 exact-byte pairs, while JK78C gives 146 and
136. Shape equality folds literal values and symbol addresses and keeps the
instruction and register shape, so it survives relocation and recalibration
that exact bytes do not.

The pairing is a relocation map rather than one shift. Across the 636
exact-byte pairs, 97 functions keep their `1ND0A` address and the largest
remaining groups sit at `+0x3010` with 46, `+0x5F94` with 44, `+0x3E58` with
43, `+0x3E60` with 33, and `+0x3E70` with 31 functions. These pairs are
correspondence candidates for review and carry no semantic claim.

## Calibration access library

The `1ND` calibration access library does not carry across; this image fuses
wrapper, kernel, and axis search into one leaf per access. The absence analysis,
the recovered contracts of `../../defs/1ME3B.interp.csv`, the fused census, and
the tool boundary are in `../../defs/1ME3B.interp.md`.

## Definition correspondence

`../../defs/JK08A-1ME3B.definition-addresses.csv` binds the reviewed `1ND`
semantic set to this image, and `../../defs/definition-projections.toml`
publishes `../../defs/1ME3B.xml` and `../../defs/1ME3B.xdf` from it. The
evidence rules, the row counts, the unsupported ignition surfaces, and the
target-native publication are in `../../defs/README.md`.

Identity and stock hashes are authoritative in `../roms.csv` and
`../README.md`; family classification and pairwise measurements are in
`../homology.toml` and `../homology.csv`.
