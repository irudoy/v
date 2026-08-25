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
| JK78C | Independent SHA-bound VQ37 projection plus native fuel-cut and native table registries | 14 families | Final-mask coordinator actuator | Schema 2, mailbox 26 | Six fields | `UNTESTED` on bench and vehicle hardware |
| `1ND` | Shared reviewed address layout plus image-local values and native fuel-cut and native table registries | 14 families | Final-mask coordinator actuator | Schema 2, mailbox 26 | Six fields | `UNTESTED` on bench and vehicle hardware |
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

VQ37 duplicates two canonical roles into a default and an alternate table.
Neither pair carries an engine-bank identity: both members of each pair are read
with the same index byte and the same interpolator, and a state selector picks
one of them. Canonical `0x0A29A` reaches JK78C `0x09EBA` and 1ND `0x0A1C0`;
canonical `0x1219E` reaches JK78C `0x137E8` and 1ND `0x13C1A`. The alternates
`0x09FBA`, `0x137F0`, `0x0A2C0`, and `0x13C22` have no canonical source and are
registered in `../defs/vq37-native-tables.toml` with exact stock values and
accessor literal-pool bindings.

The compensation accessors publish four parallel channels. The two 16x16
surfaces share index byte `0xFFFF22F8` and axes `0x13AF8` and `0x13B18` and
write adjacent bytes `0xFFFF1E91` and `0xFFFF1E92`; the consumer at `0x40E86`
selects one channel per state code and crossfades it against the previous
state's channel by a normalized progress weight where `0x8000` is 1.0. The
eight-point timing accessor `FUN_000644D0` reads index byte `0xFFFF11A2` on both
branches and selects the alternate through bit 0 of `0xFFFF4525`, a latch on the
u16 transition progress at `0xFFFF447E` that sets at `0x8000` and releases at
`0x7300`.

The state code is a status-block byte at `0xFFFFA22F`. `FUN_00054FD0` publishes
it to `0xFFFF2808`, and `FUN_0004692A` reduces it to eight buckets: raw `5` maps
to `2`, `3` to `3`, `10` to `4`, `12` to `5`, `13` to `6`, `14` to `7`, `15` to
`8`, and every other raw value to `1`. `FUN_0004678C` derives the origin and
destination buckets, the progress at `0xFFFF447E`, and the blend weight at
`0xFFFF43F0`. Scheduler `FUN_00020F1A` copies the `0x6C`-byte block at
`0xFFFF4468` to `0xFFFF43FC` and shuffles the current and previous copies, which
places the origin bucket at `0xFFFF4414`, the destination bucket at
`0xFFFF43EE`, and the applied weight at `0xFFFF43EC`. The compensation consumer
maps bucket `2` to the alternate surface, bucket `8` to the separate table
`0x13AE8`, and every other bucket to the default surface.

`FUN_00054E16` snapshots the machine inputs into `0xFFFFA204` onward, taking
`0xFFFFA219` from `0xFFFF1066` and `0xFFFFA21A` from `0xFFFF1069`. Periodic
runner `FUN_00020F1A` copies six bytes from `0xFFFF106A` to `0xFFFF1064` at the
head of every pass, so `0xFFFF1069` is the previous-cycle copy of the coolant
byte that service-0x22 DID `0x1101` binds. `FUN_00054B2C` takes the cold path
while `0xFFFFA21A` is below `ROM8[0x84A6]` or `0xFFFFA219` is below
`ROM8[0x84A4]`, the previous raw state is not `5`, `10`, `12`, or `13`, and, if
the previous raw state is `4`, `0xFFFFA21A` is also below `ROM8[0x84A5]`. That
path enters raw state `4` through `FUN_00054AC4` or raw state `3` through
`FUN_00054AE8`. All three stock JK78C thresholds are `120`, the `70 C` grid
point of coolant axis `0x14208`, which carries `90, 100, 110, 120, 130, 140,
150, 160` for `40 C` through `110 C`.

Above the threshold the machine resolves three booleans that `FUN_00054FD0`
flattens next to the state block. `0xFFFFA311` mirrors bit 7 of `0xFFFF455B`
and routes to raw state `13` when `0xFFFFA30F`, bit 6 of `0xFFFF23C6`, is set
and to raw state `12` when it is clear. With `0xFFFFA311` clear, `0xFFFFA310`,
bit 7 of `0xFFFF456F`, routes to raw state `15`. With both clear,
`FUN_00054A62` enters raw state `10` while `0xFFFFA30E` is set and raw state
`5`, the only bucket-`2` state, while it is clear. Raw states `3`, `4`, `10`,
`12`, and `13` all reach the default surface, so the alternate surface is the
fully qualified terminal state and the default surface covers every other
condition.

`0xFFFFA30E` mirrors bit 1 of `0xFFFF23E5`, which `FUN_00080CEC` holds set only
while bit 7 of `0xFFFF23EB` is set, tick counter `0xFFFF3754` is at most
`ROM8[0x8B06]`, and bit 6 of `0xFFFF45C8` is clear. Stock JK78C `ROM8[0x8B06]`
is `19`. `FUN_0008110A` dispatches `FUN_00080CEC` from `FUN_000756DC`, entry
`43` of the 144-entry periodic list at `0x21A4C` that `FUN_00020F1A` walks, so
one tick is one pass of that list. `FUN_000805E8` sets bit 7 of `0xFFFF23EB`
only while no pending `0x20` and no confirmed `0x40` status is present in DTC
records `10` through `16`, which `../defs/JK78C.dtc.csv` binds to P0306, P0305,
P0304, P0303, P0302, P0301, and P0300, and only after the countdown at
`0xFFFF255E`, reloaded from `ROM16[0x9286]`, reaches zero.

Both bit-7 producers are calibrated comparators with hysteresis.
`FUN_00059C2C` interpolates coolant-indexed curve `0x13F88`, or `0x13F90` when
bit 6 of `0xFFFF23C6` is set, over axis `0x14208`, compares `0xFFFF268C`
against the result with retention offset `ROM8[0x85D6]`, and requires a second
comparator on `0xFFFF11A2` against `0xFFFF226C` plus `ROM8[0x879D]` with band
`ROM8[0x85D4]`. Stock `0x13F88` is `255, 255, 255, 255, 255, 130, 110, 90` and
stock `0x13F90` is `90, 70, 50, 50, 50, 50, 50, 50`. `FUN_0005A0DA` compares
`0xFFFF11A3` against `ROM8[0x8784]` plus three conditional adders that are all
zero in stock, with band `ROM8[0x85D3]`, and additionally requires bit 6 of
`0xFFFF23B8` set and bit 1 of `0xFFFF4573` clear.

Bank identity is available from the ROM itself where it exists. The service-0x22
DID tables bind per-bank RAM directly, and their ordering agrees with the factory
manual rule that assigns bank 1 to the lower code of every per-bank DTC pair.
The DTC descriptor table does not repeat that order: JK78C group `0x49` stores
P1089 on even sub-indices and P1092 on odd, group `0x37` stores P0021 below
P0011, and group `0x3D` stores P0051 below P0031. Descriptor position carries no
bank convention, so a per-bank claim requires a DID binding or a consumer trace.

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

### VQ37 declares VVEL through its own DID tables

The same publication tables carry the VVEL addition positively. JK78C family
`0x11` holds 128 records against 124 on JK08A, and family `0x12` holds 95
records reaching DID `0x125E` against 81 reaching `0x1250`. Every added
populated slot belongs to VVEL, and JK08A declares none of them.

| DID | Factory name | JK78C RAM | Width |
| --- | --- | --- | ---: |
| `0x117D` | VVEL SEN LEARN-B1 | `0xFFFF42FC` | 1 |
| `0x117E` | VVEL SEN LEARN-B2 | `0xFFFF4300` | 1 |
| `0x125A` | VVEL POSITION SEN-B1 | `0xFFFF42C0` | 2 |
| `0x125B` | VVEL POSITION SEN-B2 | `0xFFFF42C2` | 2 |
| `0x125D` | VVEL TIM-B1 | `0xFFFF276E` | 2 |
| `0x125E` | VVEL TIM-B2 | `0xFFFF2770` | 2 |

Slot `0x125C` at `0xFFFF443E` is populated and unnamed in the factory manual.
`FUN_000EDF62` serves the VVEL TIM pair.

These bindings also fix the ROM's own bank ordering convention. Across the 18
populated bank-labelled DID pairs in JK78C and the 16 in JK08A, bank 1 is the
lower RAM address without exception, which is the same order the factory manual
uses for per-bank DTC pairs. The DID table therefore carries bank identity where
the DTC descriptor table does not.

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
