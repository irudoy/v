# ROM checksums - JK03A / JK03B / JK08A

JK03A, JK03B, and JK08A images are 1 MiB, big-endian, and based at `0x0`. They
share a checksum layout consisting of two SUM16 checks and two runtime self-test
XOR+SUM domains.

`apply_immo_off.py` changes only `ROM[0x8725].bit0` and leaves stored checksum
fields equal to stock. The flasher corrects checksums when writing. The layout
below supports code analysis and independent verification of ROM content.
`jk08a_checksums.py` implements the complete layout, and
`apply_map_switching.py` requires a valid input and writes a recalculated,
self-consistent output.

## SUM16

| Check | Stored value | Summed region |
|-------|-------------:|---------------|
| SUM16 A | BE `u16` at `0x008200` | BE `u16` values in `[0x008202, 0x020000)` |
| SUM16 B | BE `u16` at `0x020000` | BE `u16` values in `[0x020002, 0x100000)` |

The sum is computed modulo `2^16`. Bounds are half-open: SUM16 A ends before
`0x020000` and does not include the stored SUM16 B word. Both checks exclude
their own stored words through their range placement.

This layout matches the 1 MiB SH7058 scheme in the NissanECU wiki mirror at
`refs/nissanecu-wiki/Checksums.md` and reproduces stock JK03A/JK03B/JK08A.

## Runtime self-test XOR+SUM

Each domain computes XOR and a sum over big-endian `u32` values; the sum is
modulo `2^32`.

| Domain | Region | XOR reference | SUM reference | Exclusions |
|--------|--------|--------------:|--------------:|------------|
| A | `[0x008204, 0x100000)` | `0x0096d4` | `0x0096dc` | `0x0096d4`, `0x0096dc`, `0x020000` |
| B | `[0x02040c, 0x02259c)` | `0x020408` | `0x020404` | none |

The bounds are stored as ROM constants and read by code:
`[0x022650] = 0x8204`, `[0x022654] = 0xfffff` for A;
`[0x022648] = 0x2040c`, `[0x02264c] = 0x2259a` for B. The final B word starts
at `0x22598` and covers bytes through `0x2259b`.

Field order is reversed between the domains: A stores XOR first, while B stores
SUM first. The A exclusions are mandatory: two addresses hold the domain's own
references, and `0x020000` holds SUM16 B and the beginning of the vector table.

## Dependencies and recalculation order

1. Compute self-test B and write SUM at `0x020404`, then XOR at `0x020408`.
2. Compute self-test A with the updated B references and write XOR at `0x0096d4`,
   then SUM at `0x0096dc`.
3. Compute SUM16 A and write `0x008200`.
4. Compute SUM16 B and write `0x020000`.

The B references are included in self-test A and SUM16 B. The A references are
included in SUM16 A. SUM16 B is excluded from self-test A and lies beyond the
end of SUM16 A, so steps 3 and 4 are independent.

`jk08a_checksums.py` verifies stored values against independently calculated
values, reports every mismatched field, and recalculates in the order above.
Its output is verified again before return. The map-switching patcher permits
final byte changes only inside its declared composition ranges and these six
checksum fields.

## RomRaider

The native RomRaider handlers reproduce the layout in this order:

1. `alt` with `start=0x2040C`, `end=0x2259C`, `sumloc=0x20404`, and
   `xorloc=0x20408` writes self-test B.
2. `alt2` with `start=0x8200`, `end=0x100000`, `skiploc=0x20000`,
   `sumloc=0x96DC`, and `xorloc=0x96D4` writes self-test A and both SUM16
   values.

The B fields are part of domain A, so the reverse order is incorrect.
`defs/JK08A.xml` contains the handlers in `alt` -> `alt2` order.

## TunerPro

`defs/JK08A.xdf` intentionally contains no `XDFCHECKSUM`. The TunerPro artifact
defines calibration tables and reversible patches only. Checksum correction is
performed by the flashing workflow, so editor-side recalculation is not part of
the XDF contract.

## Verified stock values

| ROM | SUM16 A | SUM16 B | A XOR | A SUM | B SUM | B XOR |
|-----|---------|---------|-------|-------|-------|-------|
| JK03A | `d58a` | `eee1` | `e93fb358` | `d61bc71c` | `ac399870` | `07131670` |
| JK03B | `9a0a` | `eee1` | `ff15d54a` | `2ec1b4d2` | `ac399870` | `07131670` |
| JK08A | `2cae` | `eee1` | `47a28253` | `094aa8cf` | `ac399870` | `07131670` |

Domain B and its values match because JK03A, JK03B, and JK08A have an identical
`0x020000..0x0fffff` region. The A and SUM16 A values reflect
configuration/calibration differences.

## Runtime self-test machinery

| Address | Operation |
|---------|-----------|
| `00021610` | sets cursor A: `[0xffff2c04] = 0x8204` |
| `00021440` | scans an A slice and accumulates XOR and SUM |
| `000214d0` | completes A when the cursor reaches `0x00100000` |
| `00021562` | compares A with `[0x0096d4]` and `[0x0096dc]` |
| `00021654` | sets cursor B to `0x2040c` and sets the scan step |
| `0002167a` | scans B and accumulates XOR and SUM |
| `00021714` | compares B with `[0x020408]` and `[0x020404]` |

On a mismatch, `00021714` invokes the shared fault manager `0007d8b8` with code
`0x75`. This semantic claim has `code` confidence; the response has not been
observed on a physical ECU.

## Scope

The exact-layout profile is confirmed for JK03A, JK03B, and JK08A. This
specification makes no claim about checksum-field locations or coverage for
1ND0A, 1ND3B, JK78C, JK00C, or JK00D.
