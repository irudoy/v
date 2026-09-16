# ROM checksums - supported SH7058 and SH7059 families

The registered SH7058 images are 1 MiB and the registered SH7059 images are
1.5 MiB. All images are big-endian and based at `0x0`. Addressed coverage and
the number of checksum domains belong to the exact ROM profile in
`checksum-layouts.toml`; neither is inferred from file size or MCU family.

The Developer Immobilizer control in the JK08A definitions changes only
`ROM[0x8725].bit0`. The historical one-bit validation image retained stock
checksum fields, and the flasher corrected them while writing. The layout below
supports code analysis and independent verification of ROM content.
`rom_checksums.py` implements the profile registry and generic calculation.
`jk08a_checksums.py` preserves the 7MFKAVN86 compatibility API used by the
current builder. Component-stage tools use the same dependency order.

## 7MFKAVN86 shared layout

## SUM16

| Check | Stored value | Summed region |
|-------|-------------:|---------------|
| SUM16 A | BE `u16` at `0x008200` | BE `u16` values in `[0x008202, 0x020000)` |
| SUM16 B | BE `u16` at `0x020000` | BE `u16` values in `[0x020002, 0x100000)` |

The sum is computed modulo `2^16`. Bounds are half-open: SUM16 A ends before
`0x020000` and does not include the stored SUM16 B word. Both checks exclude
their own stored words through their range placement.

This layout matches the 1 MiB SH7058 scheme in the NissanECU wiki mirror at
`refs/nissanecu-wiki/Checksums.md` and reproduces stock
JK00A/JK03A/JK03B/JK08A.

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

## 8MFK member-specific layouts

JK00C and JK00D retain the same SUM16 fields and half-open SUM16 regions. Their
runtime B references remain at `0x020404` and `0x020408`, while the covered
range is `[0x02040c, 0x022628)`. Runtime A still covers
`[0x008204, 0x100000)` and excludes its own fields plus `0x020000`, but the A
reference fields differ between the two images.

| ROM | A XOR reference | A SUM reference | B end |
|-----|----------------:|----------------:|------:|
| JK00C | `0x009798` | `0x0097a0` | `0x022628` |
| JK00D | `0x0097a8` | `0x0097b0` | `0x022628` |

The JK00C and JK00D checksum functions at `0x02168e`, `0x0216d0`,
`0x0216f6`, `0x021790`, and `0x0217f0` have exact same-address instruction
bytes. Their literal pools bind the member-specific Runtime A fields and the
common Runtime B final byte at `0x022626`.

`rom_checksums.py` verifies stored values against independently calculated
values, reports every mismatched field, and recalculates in the order above.
Its output is verified again before return. The unified builder permits final
byte changes only inside the union of its runtime composition ranges and the
six checksum fields selected for the exact input ROM.

## SH7059 1ND exact-code layout

1ND0A and 1ND3B share one exact checksum implementation and six stored
references. Four domains sum big-endian `u16` values modulo `2^16`. The
application domain computes XOR and SUM over big-endian `u32` values, with the
sum reduced modulo `2^32`.

| SUM16 domain | Stored field | Region | Exclusions |
|---|---:|---|---|
| Calibration | `0x008200` | `[0x008202, 0x020000)` | none |
| Application | `0x020000` | `[0x020002, 0x180000)` | none |
| Boot code | `0x005ffe` | `[0x000000, 0x005ffe)` | none |
| Vector code | `0x006efe` | `[0x006000, 0x008200)` | `0x006efe` |

| Runtime domain | Region | XOR reference | SUM reference | Exclusions |
|---|---|---:|---:|---|
| A | `[0x008200, 0x180000)` | `0x009610` | `0x009618` | `0x008200`, `0x009610`, `0x009618`, `0x020000` |

Function `0x00002c60` incrementally checks the calibration and application
SUM16 fields. Function `0x0012604c` independently checks both lower-code SUM16
fields and the runtime XOR+SUM pair. Its instruction stream starts the runtime
cursor at `0x008200`, terminates it at `0x180000`, and compares the calculated
values with `0x009610` and `0x009618`. The stock self-test checksum contract
does not use RIPEMD-160.

Runtime A is recalculated before the calibration SUM16 because both runtime
references lie inside the calibration domain. The two primary SUM16 fields are
excluded from Runtime A. The lower-code sums are independent and can be closed
after the application domains.

| ROM | Calibration SUM16 | Application SUM16 | Boot SUM16 | Vector SUM16 | A XOR | A SUM |
|---|---:|---:|---:|---:|---:|---:|
| 1ND0A | `2f52` | `b7dd` | `e629` | `41d8` | `e0f04d48` | `7131b24a` |
| 1ND3B | `5dd1` | `b7dd` | `e629` | `41d8` | `5a01b3c1` | `ab671f91` |

## JK78C exact-code layout

JK78C retains the four-domain SH7058 algorithm while using target-specific
Runtime A fields and a shorter Runtime B region. Its exact checksum functions
at `0x0216fc`, `0x02173c`, `0x021762`, `0x0217fc`, and `0x02185c` preserve the
normalized control-flow shapes of the JK00D implementation. Target literals
bind the start and final-byte boundaries and all four Runtime reference fields.

| Domain | Stored field or fields | Region | Exclusions |
|---|---|---|---|
| SUM16 A | `0x008200` | `[0x008202, 0x020000)` | none |
| SUM16 B | `0x020000` | `[0x020002, 0x100000)` | none |
| Runtime A | XOR `0x0093d4`, SUM `0x0093dc` | `[0x008204, 0x100000)` | `0x0093d4`, `0x0093dc`, `0x020000` |
| Runtime B | XOR `0x020408`, SUM `0x020404` | `[0x02040c, 0x022604)` | none |

The Runtime B literal identifies `0x022602` as the final covered byte, so the
last aligned word starts at `0x022600`. All six stock references reproduce by
independent calculation.

### Runtime A background scanner

JK78C verifies Runtime A incrementally from the periodic list at `0x00021A4C`
walked by `FUN_00020F1A`. Entry 141 is `FUN_000214D4`, 228 bytes, which is
reached only through that list. The exact-code function group is:

| Function | Role |
|---|---|
| `0x0216FC` | Initializer: writes the scan cursor `0xFFFF2B10` |
| `0x0214D4` | Periodic entry: gate, chunk scan, end-of-pass sequence |
| `0x0215B8` | Single-longword step, same skips and end handling, no `0x0216D8` call |
| `0x02164E` | Comparison: accumulators against `[0x0093D4]` and `[0x0093DC]`, mismatch to bit 3 of `0xFFFF4568` |
| `0x021680` | Fault latch: bit 7 of `0xFFFF4565` = mismatch and bit 0 of `0xFFFF4564` |
| `0x0216A8` | Bit 0 of `0xFFFF4564` = mismatch of the completed pass |
| `0x0216C4` | With bit 7 of `0xFFFF4565` set, jumps to the fault-state dispatcher `0x09DFA8` with descriptor index `0x6F` in `r4` |
| `0x02162C` | Latch: `0xFFFF2A2C` <- `0xFFFF3350`, `0xFFFF2A30` <- `0xFFFF34E8`, then clears both accumulators |
| `0x0216D8` | Sets bit 2 of `0xFFFF4564` unless the pass mismatched with bit 7 of `0xFFFF4564` clear |

The gate is the conjunction of two conditions. The first reads the byte table
at `0x0001A88C` indexed by descriptor status group: bit 7 of `[0x0001A8B1]`
(group `0x25`, stock `0xEF`), or bit 7 of `[0x0001A8B2]` (group `0x26`, stock
`0x10`), or `[0x0001729F]` (stock `0x00`) not equal to `0x55`. The second is
bit 7 of `0xFFFF44DF`, the walker's copy of `0xFFFF44E0` taken before the
walk; the bit is port L pin PL4 read high, or low for less than a 50-tick
debounce, and its writers are listed in `../defs/JK78C.can.md` under
recovered periodic entries. Group `0x25` holds the eight `P0605` descriptors at indices 111 to 117;
index `0x6F` is the record at `0x0001BCE0` with group `0x25`, bit 7, code
`P0605`, byte-identical to the JK08A record at index `0x75` that the JK08A
verifier `0x021714` raises.

With bit 2 of `0xFFFF4564` clear the entry scans one chunk per call: from the
cursor for `[0x000215EC]` = `0x5E6C` bytes, clamped at
`[0x000226BC] + 1` = `0x100000`, skipping the longwords at `0x0093D4`,
`0x0093DC`, `0x008200`, and `0x020000`, XOR into `0xFFFF3350` and sum into
`0xFFFF34E8`. Reaching `0x100000` runs the sequence `0x02164E`, `0x021680`,
`0x0216A8`, `0x0216C4`, `0x02162C`, `0x0216D8` and reloads the cursor from
`[0x000226B8]` = `0x008204`. With bit 2 set the entry calls `0x0215B8` four
times, one longword per call, so a completed first pass continues at a
reduced rate. `0x0216FC` initializes the cursor from the same literal,
`0x008204`. A full pass covers `[0x008204, 0x100000)` in 43 chunks.

The chunk region and exclusions are the `sh7058_jk78c` Runtime A domain. The
skip at `0x008200` lies below the region start and never matches from a
cursor initialized at `0x008204`. Independent recalculation over
`[0x008204, 0x100000)` with the exclusions reproduces `E1E877CF` and
`0AF99D87`.

The JK08A homologs are `0x02167A` (scanner, cursor `0xFFFF2FF4`, accumulators
`0xFFFF3000` and `0xFFFF3008`, gate bit 7 of `0xFFFF4184`), `0x021714`
(verifier, fault index `0x75`) and `0x021774` (epilogue latching
`0xFFFF2B1C` and `0xFFFF2B20`). JK08A scans Runtime B in the background;
JK78C scans Runtime A.

## RomRaider 7MFKAVN86 projection

The native RomRaider handlers reproduce the layout in this order:

1. `alt` with `start=0x2040C`, `end=0x2259C`, `sumloc=0x20404`, and
   `xorloc=0x20408` writes self-test B.
2. `alt2` with `start=0x8200`, `end=0x100000`, `skiploc=0x20000`,
   `sumloc=0x96DC`, and `xorloc=0x96D4` writes self-test A and both SUM16
   values.

The B fields are part of domain A, so the reverse order is incorrect.
`defs/JK08A.xml` contains the handlers in `alt` -> `alt2` order.

## RomRaider 1ND projection

The SH7059 layout declares one runtime domain, so it projects to a single
handler: `alt2` with `start=0x8200`, `end=0x180000`, `skiploc=0x20000`,
`sumloc=0x9618`, and `xorloc=0x9610`. It writes Runtime A together with the
calibration and application SUM16 values.

The boot and vector SUM16 domains have no native handler. Both end at `0x8200`,
and the lowest published 1ND entity is `0x8524`, so no editor session can reach
their regions and leave a field stale. `tools/mapkit/emit_def.py` enforces the
precondition: it fails when any published entity falls outside the declared
checksum regions.

## TunerPro

`defs/JK08A.xdf` intentionally contains no `XDFCHECKSUM`. The TunerPro artifact
defines calibration tables and reversible patches only. Checksum correction is
performed by the flashing workflow, so editor-side recalculation is not part of
the XDF contract.

## Verified stock values

| ROM | SUM16 A | SUM16 B | A XOR | A SUM | B SUM | B XOR |
|-----|---------|---------|-------|-------|-------|-------|
| JK00A | `ecbd` | `eee1` | `ba979b43` | `1e132e15` | `ac399870` | `07131670` |
| JK03A | `d58a` | `eee1` | `e93fb358` | `d61bc71c` | `ac399870` | `07131670` |
| JK03B | `9a0a` | `eee1` | `ff15d54a` | `2ec1b4d2` | `ac399870` | `07131670` |
| JK08A | `2cae` | `eee1` | `47a28253` | `094aa8cf` | `ac399870` | `07131670` |
| JK00C | `a02a` | `b095` | `ebaee2dd` | `3ba6fca3` | `d38ba003` | `da585443` |
| JK00D | `d2c8` | `d962` | `d1850caa` | `0b2cd270` | `d396725d` | `da5e998d` |
| JK78C | `1f44` | `ccfa` | `e1e877cf` | `0af99d87` | `2bac8c8c` | `c83320ec` |

Domain B and its values match because JK00A, JK03A, JK03B, and JK08A have an
identical `0x020000..0x0fffff` region. The A and SUM16 A values reflect
configuration/calibration differences. JK00C and JK00D use the longer Runtime
B range and have distinct code and calibration content.

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

Exact layouts are registered for JK00A, JK03A, JK03B, JK08A, JK00C, JK00D,
JK78C, 1ND0A, and 1ND3B.
