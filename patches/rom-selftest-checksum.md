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

Each checksum calculation prepares complete big-endian words from the current
image in a separate native array. Excluded words become zero, the neutral
operand of both SUM and XOR. The image remains unchanged, and every calculation
reads its current bytes. Partial ranges, general buffers, and unsupported
native word widths use the scalar reader. Independent scalar tests cover the
registered image domains, exclusions, wraparound, and live input changes.

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

## SH7059 1ME3B layout

1ME3B keeps the four SUM16 domains and the single Runtime A domain of the 1ND
layout at the same regions and SUM16 fields. Its Runtime A references are
`0x0096f4` (XOR) and `0x0096fc` (SUM), and the Runtime A exclusions are
`0x008200`, `0x0096f4`, `0x0096fc`, and `0x020000`.

Function `0x00002c60`, byte-identical to the 1ND verifier, incrementally checks
the calibration and application SUM16 fields. Functions `0x00021a78` and
`0x00021b8e` accumulate the application XOR and SUM over
`[0x008200, 0x180000)`, and `0x00021c74` compares the accumulators with both
references. Function `0x0013339c` independently checks the runtime pair and
both lower-code SUM16 fields. The recalculation order equals the 1ND order.

| ROM | Calibration SUM16 | Application SUM16 | Boot SUM16 | Vector SUM16 | A XOR | A SUM |
|---|---:|---:|---:|---:|---:|---:|
| 1ME3B | `bed1` | `80ea` | `0b3c` | `27f4` | `53b4709e` | `c5f53006` |

## SH7059 1EK7A layout

The application verifier at `0x00021be2` compares Runtime A against XOR field
`0x00986c` and SUM field `0x009870`. The domain covers `[0x008200, 0x180000)`
and skips both runtime fields and the SUM16 words at `0x008200` and `0x020000`.
The calibration, application, and boot SUM16 domains and both runtime fields
reproduce on the cataloged read.

The self-test at `0x00154458` calculates the vector SUM16 over
`[0x006000, 0x008200)` while skipping `0x006efe`. The stored value is `0x7c56`
and the calculated value is `0x73da`. The repository's full-image verifier
flags this field on the cataloged image. The PCMFlash read verification
reported success. The vector domain is outside calibration storage.

### Diagnostic RAM status and reply

The diagnostic selector at `0x00039162` routes service `0xa0` to handler
`0x00039fac`. For mode `0x02`, the handler stores the mode at `0xfffebb6e`
and sets `0xfffebd5a.bit1` at `0x0003a2d2`. The application task table entry
at `0x000222b4` points to `0x00037a2e`. That task tests the pending bit before
passing the mode byte to the self-test in the tail-jump delay slot at
`0x00037a56`. The mode-2 branch at `0x001548c6` also tests
`0xfffebd90.bit7` before starting the scan.

Mode 2 checks the application XOR and SUM, boot SUM16, and vector SUM16.
The vector comparison at `0x0015495a` feeds the common mismatch branch at
`0x0015495e`. The epilogue at `0x00155504` publishes completion in
`0xfffebd05.bit5` and mismatch in bit 6. At `0x0003a2e8` the response handler
tests completion and schedules negative response code `0x78` while pending.
The completed reply contains `0xe0 0x02` followed by `0x55` for a match or
`0xaa` for a mismatch, selected at `0x0003a4ee`. The handler clears the two
status bits at `0x0003a562`. The reply carries one combined verdict over the
four fields. The mismatch branch and reply encoding are derived from ROM code.

The reset vector points to `0x00002470`. Its application-entry decision uses
the mask from `0x008000` and `0x008080` and the image marker fields at
`0x17ff80` and `0x17ff84`. In the cataloged image this path selects the
application vector table at `0x020004` and dispatches through `0x0200fc` to
`0x0002ef42`. The background checker at `0x00021be2` compares the application
XOR and SUM. It sets or clears `0xfffebd90.bit7` based on that comparison.
Mode 2 sets the shared bit after either comparison outcome at `0x0015497c`.

### Vector block evidence

The base identity at `0x006f00` holds `1UX0A` and `2FZ35YN21`.
Nissan lists `23703-1UX0A` as a non-programmed ECM for the 370Z. The later
identity slot at `0x007000` starts with `1EK7A` and carries `TOCHIEOLPG`
at `0x00701d`. [Nissan 370Z parts catalog](https://parts.nissanusa.com/v-2013-nissan-370z--base--3-7l-v6-gas/engine--control-modules)

The boot path at `0x00001824` selects an identity slot from the records
scanned by `0x000011b0`, including `0x007000` when `0x006f00` is the last
occupied slot. It stages the received 48-byte record followed by `0xff`
padding to a 128-byte programming page. The write task at `0x00000884`
uses the staged destination at `0xffff8260`, then checks the page in
`0x00000a90`. The same task can stage the page at `0x008080` through
`0x000019dc`. Both pages lie above the checksum word at `0x006efe`.
The application transfer at `0x000015cc` separately bounds the application
data at `0x008200` and above. Consequently, these programming operations can
change bytes included in the vector scan while retaining the stored word.

Against both cataloged peers `1ME3B` and `1ND0A`, the vector bytes differ,
apart from the stored SUM16 word, within `[0x006400, 0x006480)`,
`[0x006f00, 0x006f80)`, `[0x007000, 0x007080)`, and `[0x008080, 0x008100)`.
The boot initializer at `0x00002816` copies the first word at `0x006400` to
`0xffff8298`. The records at `0x006f00` and `0x007000` carry software
identifiers. The reset code reads the first byte at `0x008080` as part of
the mask calculation. The first and last spans each contain one repeated
word in the 1EK7A read, `0x1509` and `0xf0f0` respectively. Their peers contain
`0xffff` and `0xeeee` respectively. Replacing a 128-byte repeated-word span by
another repeated word changes SUM16 by a multiple of `0x40`. The observed
delta `0x087c` has remainder `0x3c` modulo `0x40`. Substituting the
corresponding pages from the stock catalog and constant-fill variants
`00`, `ee`, `f0`, and `ff` across all four spans yields no `0x7c56` result.

### Retained reference comparison

The sum below applies the same vector-domain arithmetic to compare byte
states. For the last column, replace `[0x007000, 0x007080)` with `0xff`
and `[0x008080, 0x008100)` with `0xee`, as found in the cataloged images
with an erased second identity slot.

| Image | Stored word | Current sum | Sum with base page pattern |
|---|---:|---:|---:|
| JK00C | `0x5bd8` | `0x36c8` | `0x5bd8` |
| JK00D | `0x5bd8` | `0xdd4f` | `0x5bd8` |
| JK78C | `0x58da` | `0x0be9` | `0x58da` |
| 1EK7A | `0x7c56` | `0x73da` | `0xad75` |

The marker write to JK00D also has a paired outbound image and readback
identified in [`hardware-results.toml`](hardware-results.toml) under
`map_switching.marker`. The vector domain differs by one page. The page
at `0x008080` changes from `0xee` to zero, the sum moves from `0x5bd8` to
`0xa058`, and the stored word stays `0x5bd8`.

PCMFlash documents verification after saving a read. Its public Module 18
protocol listing advertises checksum support for SH705927N and leaves
the covered address ranges unspecified. The slot contents, write path, and
retained references support an earlier-state checksum as the explanation
for `1EK7A`. The exact byte state that produced `0x7c56` remains unknown.
[PCMFlash manual, section 3.2.4](https://eu.pcmflash.ru/legal/manual.pdf#page=26)
[PCMFlash module and protocol list](https://forum.pcmflash.ru/forum/viewtopic.php?t=15670)

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
JK78C, 1ND0A, 1ND3B, and 1ME3B.
