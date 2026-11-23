# Exact 1ME3B fused calibration access library

## Scope

This specification records the calibration access library of the exact 1ME3B
stock image registered in `../../../rom-images/roms.csv` and the census taken from
it. `1ME3B.interp.csv` is the registry the census populates,
and `../../../rom-images/23710-1ME3B/README.md` owns the read record and the image
identity.

The library is read from leaf code. The census establishes address, geometry,
and consumer path; it assigns no semantics.

## Absence of the 1ND library

The `1ND` calibration access library does not carry across. Of the 64 `1ND0A`
functions in `0x028390:0x02928C`, 58 have no structural homolog in this image,
and they include all 13 registry kernels and all 36 registry wrappers. Code
immediately around that block does carry across at constant relocations:
`0x0283D4` at `+0x5D4`, `0x0289C0` and `0x028A08` at `+0x297C`, and `0x0291EC`
onward at `+0x2D50`. The absence is therefore a property of the library, not of
the region.

The replacement occupies `0x028980:0x02BF60` and holds 42 functions and 13,710
bytes with no `1ND0A` structural homolog; 41 of them are call-graph leaves.
`1ND0A` reaches the same behaviour through a wrapper that calls a kernel which
may call a shared tail, in 58 functions and 3,572 bytes. This image fuses each
access into one self-contained function and unrolls the axis search, which
accounts for the size. Callers load a leaf address from a literal-pool word and
`jsr` it, so no wrapper level and no shared kernel exist.

## Recovered geometry and contracts

`1ME3B.interp.csv` registers 34 leaves with `kernel` equal to `wrapper`. Their
geometry is read from the leaf code: the unrolled axis search gives point count
and axis element (a byte axis clamps at `points - 1`, a word axis at
`2 * (points - 1)`), the cell loads give the storage type, the row stride before
`mulu.w` gives the second dimension, and an implicit leaf gives its step from
the index shift and its point count from the input clamp. The argument
convention is `r4` table, `r5` first axis, `r6` second axis, `r7` first input,
and the second input on the stack; a one-dimensional explicit leaf takes its
input in `r6`, and an implicit leaf takes its raw input in `r5`.

The 34 contracts reproduce the `1ND0A` registry vocabulary exactly: the eight
implicit geometries (4 points at step 64, 8 at 32, 16 at 16, 32 at 8, 4 at
16384, 8 at 8192, 16 at 4096, and 64 at 256), the six explicit one-dimensional
contracts, and the ten explicit two-dimensional contracts, including the mixed
`uint8` and `uint16` axis pairs. Seven registered leaves are byte-identical
copies of another leaf (`0x02B3B0`, `0x02B5A4`, `0x02B878`, `0x02BBA4`,
`0x02BBF8`, `0x02BCD4`, and `0x02BE20`), each with its own callers.

Variants inside one contract are properties of the leaf rather than of the
registry row. `0x028C8C`, `0x0291DC`, `0x0293D8`, `0x0298B4`, and `0x029BA8`
compare a `uint16` input with `uint8` first-axis values scaled by four, and
`0x02A388` with its copy scales them by sixteen. `0x0293D8` and `0x029BA8` mask
every cell with `0x7F`. `0x02A6B4` treats cells at or above `0x80` as
sentinels. `0x02B0D4` and its copy search 32 points through a partitioned rather
than linear comparison chain.

## Functions outside the registry vocabulary

Eight functions in the range are outside the registry vocabulary. `0x0289A8`
reads an 8x8 `uint8` table at the raw inputs shifted right by five without
interpolation, `0x028C30` reads a 4x4 `uint8` table at the floor indices of two
`uint8` axes without interpolation, and `0x0289CC` interpolates an 8x8 `uint16`
table over two implicit axes at step 8192, a two-dimensional implicit form the
registry does not express. `0x02AC3C` is the 16-point step-16 implicit leaf over
`int8` cells, biased by `0x80` around the interpolation. `0x02B33C` is a signed
fixed-point multiply with a shift count, `0x02B384` a saturating add, and
`0x02BF3C` with `0x02BF58` a byte sum over RAM `0xFFFEBD88:0xFFFEDB11` against
fields at `0xFFFEDB14` and `0xFFFEDB16`.

## Census

The fused census (`ResolveAccessors.java` with the `fused` token, one run per
registry row) resolves 1,053 call sites in 1,098 rows, the excess being selector
branches. Data flow recovers a ROM base at all but three sites; the linear
backtrack agrees at 625 rows, is superseded at 371, and conflicts at 23.

The layer holds 768 tables and 457 axes, 561 tables through explicit axes and
207 through implicit ones, all between `0x009924` and `0x025490` with seven
above `0x020000`. One table is read by two leaves of equal geometry. The largest
contracts by table count are the 8-point `uint8` implicit leaf `0x02A9F4` with
95 tables, the 16-point `uint16` explicit leaf `0x02AF88` with 92, the 8-point
`uint16` explicit leaf `0x02AEAC` with 90, and the 8-point `uint8` explicit leaf
`0x02AC9C` with 82.

`1ND0A-1ME3B.census-correspondence.csv` classifies these operands against the
`1ND0A` census, and `README.md` records the methods and the ledger counts.

## Tool boundary

`FindInterpCore.java` does not locate this library. Its signature is a
literal-pool slot plus two levels of indirection, which a fused leaf does not
use. Its highest-ranked candidates in this image, `0x037378` and `0x03CF10`,
are a byte-queue emitter that appends to `0xFFFEDC26` under the counter at
`0xFFFEDD2A`.
