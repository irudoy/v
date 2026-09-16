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

The `1ND` calibration access library does not carry across. Of the 64 `1ND0A`
functions in `0x028390:0x02928C`, 58 have no structural homolog in this image,
and they include all 13 registry kernels and all 36 registry wrappers. Code
immediately around that block does carry across at constant relocations:
`0x0283D4` at `+0x5D4`, `0x0289C0` and `0x028A08` at `+0x297C`, and `0x0291EC`
onward at `+0x2D50`. The absence is therefore a property of the library, not of
the region.

The replacement occupies `0x028980:0x02BF60` and holds 42 functions and 13,710
bytes with no `1ND0A` structural homolog; 41 of them are call-graph leaves.
`1ND0A` reaches the same behaviour through a wrapper that calls a kernel
which may call a shared tail, in 58 functions and 3,572 bytes. This image fuses
each access into one self-contained function and unrolls the axis search, which
accounts for the size. Callers load a leaf address from a literal-pool word and
`jsr` it, so no wrapper level and no shared kernel exist.

`../../defs/1ME3B.interp.csv` registers 34 leaves with `kernel` equal to
`wrapper`. Their geometry is read from the leaf code: the unrolled axis search
gives point count and axis element (a byte axis clamps at `points - 1`, a word
axis at `2 * (points - 1)`), the cell loads give the storage type, the row
stride before `mulu.w` gives the second dimension, and an implicit leaf gives
its step from the index shift and its point count from the input clamp. The
argument convention is `r4` table, `r5` first axis, `r6` second axis, `r7`
first input, and the second input on the stack; a one-dimensional explicit leaf
takes its input in `r6`, and an implicit leaf takes its raw input in `r5`. The
34 contracts reproduce the `1ND0A` registry vocabulary exactly: the eight
implicit geometries (4 points at step 64, 8 at 32, 16 at 16, 32 at 8, 4 at
16384, 8 at 8192, 16 at 4096, and 64 at 256), the six explicit one-dimensional
contracts, and the ten explicit two-dimensional contracts, including the mixed
`uint8` and `uint16` axis pairs. Seven registered leaves are byte-identical
copies of another leaf (`0x02B3B0`, `0x02B5A4`, `0x02B878`, `0x02BBA4`,
`0x02BBF8`, `0x02BCD4`, and `0x02BE20`), each with its own callers.

Variants inside one contract are properties of the leaf rather than of the
registry row. `0x028C8C`, `0x0291DC`, `0x0293D8`, `0x0298B4`, and `0x029BA8`
compare a `uint16` input with `uint8` first-axis values scaled by four, and
`0x02A388` with its copy scales them by sixteen. `0x0293D8` and `0x029BA8`
mask every cell with `0x7F`. `0x02A6B4` treats cells at or above `0x80` as
sentinels. `0x02B0D4` and its copy search 32 points through a partitioned
rather than linear comparison chain.

Eight functions in the range are outside the registry vocabulary. `0x0289A8`
reads an 8x8 `uint8` table at the raw inputs shifted right by five without
interpolation, `0x028C30` reads a 4x4 `uint8` table at the floor indices of two
`uint8` axes without interpolation, and `0x0289CC` interpolates an 8x8
`uint16` table over two implicit axes at step 8192, a two-dimensional implicit
form the registry does not express. `0x02AC3C` is the 16-point step-16
implicit leaf over `int8` cells, biased by `0x80` around the interpolation.
`0x02B33C` is a signed fixed-point multiply with a shift count, `0x02B384` a
saturating add, and `0x02BF3C` with `0x02BF58` a byte sum over RAM
`0xFFFEBD88:0xFFFEDB11` against fields at `0xFFFEDB14` and `0xFFFEDB16`.

The fused census (`ResolveAccessors.java` with the `fused` token, one run per
registry row) resolves 1,053 call sites in 1,098 rows, the excess being
selector branches. Data flow recovers a ROM base at all but three sites; the
linear backtrack agrees at 625 rows, is superseded at 371, and conflicts at 23.
The layer holds 768 tables and 457 axes, 561 tables through explicit axes and
207 through implicit ones, all between `0x009924` and `0x025490` with seven
above `0x020000`. One table is read by two leaves of equal geometry. The
largest contracts by table count are the 8-point `uint8` implicit leaf
`0x02A9F4` with 95 tables, the 16-point `uint16` explicit leaf `0x02AF88` with
92, the 8-point `uint16` explicit leaf `0x02AEAC` with 90, and the 8-point
`uint8` explicit leaf `0x02AC9C` with 82. The census is a candidate layer: it
establishes address, geometry, and consumer path, not semantics.

`FindInterpCore.java` does not locate this library. Its signature is a
literal-pool slot plus two levels of indirection, which a fused leaf does not
use. Its highest-ranked candidates in this image, `0x037378` and `0x03CF10`,
are a byte-queue emitter that appends to `0xFFFEDC26` under the counter at
`0xFFFEDD2A`.

## Definition correspondence

`../../defs/JK08A-1ME3B.definition-addresses.csv` binds the reviewed `1ND`
semantic set to this image, and `../../defs/definition-projections.toml`
publishes `../../defs/1ME3B.xml` and `../../defs/1ME3B.xdf` from it. Every
row is established through the `1ND0A` structural export, because no code
relocates from any modelled ROM: an exact-bytes or normalized-shape function
pair that reads the target address at the same call ordinal, or a target
function that reproduces the `1ND0A` reader's operand set, selector arms, and
call order; the fused leaf whose contract equals the `1ND0A` wrapper; exact
target storage; and target literals. The registry holds 40 mapped rows, 27
maps and thirteen axes, and twelve unsupported source maps.

The three canonical ignition surfaces are unsupported. The ignition
coordinator `0x0797CC` reproduces only the mode-selected half of `1ND0A`
`0x074D98`, with its own surfaces `0x00A344`, `0x00A444`, and the 8x8 group;
the trio path that `1ND0A` gates by `0x008A2B` bit 5 and `0xFFFE9488` bit 6
has no counterpart, no function selects three 16x16 surfaces through one gate,
and the trio bytes do not recur in the image. The ignition axes `0x013716` and
`0x013726` remain bound because the coordinator reads them. `0x071D64` reads a
fourth 16x16 surface `0x00A774` with axis copies at `0x013599` and `0x0135A9`;
it has no `1ND0A` counterpart and no canonical role.

The MAF factor `0x008965` holds the value 133 and is read by `0x045634`,
`0x04570A`, and `0x048298`; the last combines it with the K-value `0x009170`,
the `0x9F38` reference `0x0094D4`, and the value-3 scalar `0x00885C` exactly as
the `1ND0A` consumer `0x0C188C` combines its four scalars. The projection
declares checksum support over the `sh7059_1me3b` layout and no runtime
allocation. The image has no address profile, and its declared family boundary
forbids address inheritance from any other image in the collection.

Identity and stock hashes are authoritative in `../roms.csv` and
`../README.md`; family classification and pairwise measurements are in
`../homology.toml` and `../homology.csv`.
