# ROM family and support matrix

This matrix separates binary homology, editor-definition coverage, production
runtime coverage, executable verification, and hardware evidence. A shared
engine name or similar graph structure does not permit address inheritance.

## Family baseline

| Family | ROMs | MCU and flash | Binary relationship | Address policy |
| --- | --- | --- | --- | --- |
| `7MFKAVN86` | JK00A, JK03A, JK03B, JK08A | SH7058, 1 MiB | Exact executable ranges; differences are calibration, identity, diagnostic, and checksum storage below `0x020000` | Same-address executable and semantic inheritance after exact-range validation |
| `8MFK` | JK00C, JK00D | SH7058, 1 MiB | Near-code lineage with insertions, deletions, and relocated storage | Independent address profiles and hook validation for each image |
| JK78C | JK78C | SH7058, 1 MiB | Distinct VQ37 code base | Independent layout, checksum model, allocation, and payload lock |
| `1ND` | 1ND0A, 1ND3B | SH7059, 1.5 MiB | Exact executable ranges within the pair; cross-generation homolog of JK78C | One shared executable layout with independent stock identities and stage hashes |
| `1ME3B` | 1ME3B | SH7059, 1.5 MiB | Distinct VQ37 code base; shares the blocks below `0x008200` and a relocated diagnostic descriptor region with `1ND` | Independent recovery for every address; nothing is inherited from `1ND` or JK78C |

## Functional coverage

| Family | Definition source | Map Switching | Rolling Launch | CAN telemetry | Checksum closure | Hardware status |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `7MFKAVN86` | Canonical JK08A model plus exact-image inheritance | 12 families | Canonical fuel-shadow actuator | Schema 2 | Six fields | JK08A has scoped vehicle evidence; other members inherit no hardware result |
| `8MFK` | SHA-bound JK00C and JK00D projections | 13 families, including independent intake-cam and exhaust-cam target switching | Relocated fuel-shadow actuator | Schema 2, mailbox 24 | Six fields | Read `../patches/hardware-results.toml`; no result is inherited from JK08A |
| JK78C | Independent SHA-bound VQ37 projection plus native fuel-cut registry | 14 families | Final-mask coordinator actuator | Schema 2, mailbox 26 | Six fields | `UNTESTED` on bench and vehicle hardware |
| `1ND` | Shared reviewed address layout plus image-local values and native fuel-cut registry | 14 families | Final-mask coordinator actuator | Schema 2, mailbox 26 | Six fields | `UNTESTED` on bench and vehicle hardware |
| `1ME3B` | None | None | None | None | None | Stock read only; no derived image exists |

## Diagnostic layer

| Family | DTC codes | Developer Immobilizer | Native RomRaider checksum |
| --- | ---: | --- | --- |
| `7MFKAVN86` | 36 | `0x8725` | `alt` and `alt2` |
| JK00C | 36 | `0x873F` | `alt` and `alt2` |
| JK00D | 36 | `0x8740` | `alt` and `alt2` |
| JK78C | 35 | `0x861C` | `alt` and `alt2` |
| `1ND` | 35 | `0x8668` | `alt2` |

Each image stores its diagnostic descriptors as twelve-byte records followed
immediately by one 32-bit attribute pointer per record. The pointer table is the
ECU's own attribute reference and reproduces every canonical JK08A attribute
address exactly, so a relocated binding is read out of the target image. A code
is carried only when exactly one target record is byte-identical to the
canonical record. VQ37 declares no P1422 record, which is why its registries
hold 35 codes rather than 36.

The `1ND` layout declares one runtime domain, so it projects to a single `alt2`
handler. Its boot and vector SUM16 domains end at `0x8200`, below the lowest
published entity at `0x8524`, so no editor session can leave them stale.

`1ME3B` has no diagnostic projection. Its descriptor region is byte-identical
to `1ND0A` across 1,936 bytes at a constant `+0x164` relocation and carries the
same VQ37 group `0x37` boundary, but no code, attribute-pointer, or Developer
Immobilizer binding is recovered from the image. Its four SUM16 checksum
domains reproduce at the `1ND` field addresses while the application XOR and
SUM fields sit at `0x0096F4` and `0x0096FC`; no checksum layout is registered
because the verifier functions are not located.

The VQ37 Map Switching model replaces the canonical 2x2 fuel-cut table with
two scalar caps and two independent eight-point curves. Exact stock function,
coordinator, scheduler pointer, calibration bytes, ROM pointers, and RAM bases
are bound in `../defs/vq37-native-fuel-cut.toml`. Rolling Launch executes the
stock final-mask coordinator first and adds all six cylinder bits only for the
exact request value `0x003F`.

## Source-map parity

Runtime capability does not imply complete source-map parity. Every visible
canonical map and required axis either reaches a reviewed target address or is
an established architectural removal. No canonical role is left unlocalised.

RomRaider XML and TunerPro XDF publish the same entities on every ROM. The two
formats use different constructs for one control: RomRaider models a reversible
two-state range as a `Switch` table and TunerPro as an `XDFPATCH` entry, so
parity is asserted over exact ROM ranges and their stock and patched bytes.
TunerPro additionally publishes one group patch per DTC group; RomRaider has no
construct for a switch spanning discontiguous ranges. Every group entry repeats
an individual entry.

VQ37 splits two canonical roles into parallel per-bank tables. One input index
reaches two tables through shared axes and one interpolator with no branch, and
the two results land in adjacent RAM bytes. Canonical `0x0A29A` becomes JK78C
`0x09EBA` and `0x09FBA` writing `0xFFFF1E91` and `0xFFFF1E92`; canonical
`0x1219E` becomes `0x137E8` and `0x137F0` writing `0xFFFF14E6` and `0xFFFF14E7`.
The channel-to-bank assignment follows record order and is not established from
a consumer trace.

The `8MFK` projections carry no unsupported source row. Every visible canonical
map and required axis reaches a reviewed JK00C and JK00D address. The
stationary rev-limiter and accelerator-pedal thresholds are bound through the
shared literal pool of the relocated calculators: JK08A `FUN_0004F324`
corresponds to JK00C `0x050C9A` and JK00D `0x050C96`, and JK08A `FUN_00047A56`
corresponds to JK00C `0x048ADC` and JK00D `0x048AE0`.

### VQ37 removes exhaust camshaft timing control

The DTC descriptor table states the removal directly. JK08A group `0x37` holds
sub-indices `04`, `03`, `02`, `01`, and `00` for P0174, P0011, P0021, P0014,
and P0024 at `0x019D14`. JK78C at `0x01C0B8` and 1ND0A at `0x01C73C` hold
byte-identical `04`, `03`, and `02` records and continue directly with group
`0x38`. The P1078 and P1084 exhaust-timing-sensor records are absent from both
VQ37 images as well. No exhaust camshaft monitor exists on VQ37.

The service-0x22 `0x11xx` pointer tables reach the same boundary from the
diagnostic side. JK08A base `0x226AC` and JK78C base `0x22718` populate 84 of
124 slots with an identical sparsity pattern. Intake DIDs stay live in both:
`0x113A` reaches JK08A `0xFFFF2326` and JK78C `0xFFFF227A`. The exhaust triple
`0x1164`, `0x1165`, and `0x1166` carries 12, 6, and 21 references on JK08A and
none on JK78C or `1ND`.

Five independent static channels agree that the inherited exhaust target byte
is never produced. JK78C `0xFFFF23A4` and 1ND `0xFFFE9466` have no direct
reference, no GBR-relative access, and no decompiler-resolved store through
pointer arithmetic. Every indexed store whose constant base can reach them has
a proven index bound that stops short: the two-bank arrays at JK78C
`0xFFFF239A` and `0xFFFF23A0`, the six-cylinder array at `0xFFFF237A`, and
their 1ND homologs. Each 32-bit address occurs exactly once in its image, in
its own pointer-table slot, so no ROM table can deliver it. The same channels
recover the canonical writers `FUN_000BCED0` and the conditioner store at
`0x000C0CEE`, so the null result is a property of the target images rather
than of the method.

The same channels separate inert bytes from live ones inside the block. The
inherited intake actual-angle DIDs at JK78C `0xFFFF239C` and `0xFFFF239D` and
1ND `0xFFFE945D` and `0xFFFE945E` carry decompiler-resolved reads, and the
two-bank arrays beside them carry resolved writes. The exhaust triple carries
neither a read nor a write in either image.

Canonical exhaust-CVTC target surface `0x0B33A` is therefore an architectural
removal on VQ37 rather than a relocated address. Interpolation contract
`0x261B8` is the only canonical contract with no VQ37 library homolog, and it
serves only the cam-target calculators.

The three canonical intake-CVTC source slots `0x0AB5A`, `0x0B43A`, and
`0x0B53A` are explicit no-op dispatcher slots in the reviewed VQ37 topology.
VQ37 retains intake camshaft timing control together with its P0011 and P0021
monitors and its live intake target byte, and computes that target without the
canonical surface pair. The canonical fuel-cut table `0x0934E` also remains an
unsupported source row on VQ37, but its tuning role is covered by the
target-native cap and curve maps.

No unsupported row may be replaced with a similar address or graph neighbor.
Promotion requires exact target storage, geometry, consumer path, and stock
image binding.
