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

## Functional coverage

| Family | Definition source | Map Switching | Rolling Launch | CAN telemetry | Checksum closure | Hardware status |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `7MFKAVN86` | Canonical JK08A model plus exact-image inheritance | 12 families | Canonical fuel-shadow actuator | Schema 2 | Six fields | JK08A has scoped vehicle evidence; other members inherit no hardware result |
| `8MFK` | SHA-bound JK00C and JK00D projections | 13 families, including independent intake-cam and exhaust-cam target switching | Relocated fuel-shadow actuator | Schema 2, mailbox 24 | Six fields | Read `../patches/hardware-results.toml`; no result is inherited from JK08A |
| JK78C | Independent SHA-bound VQ37 projection plus native fuel-cut registry | 14 families | Final-mask coordinator actuator | Schema 2, mailbox 26 | Six fields | `UNTESTED` on bench and vehicle hardware |
| `1ND` | Shared reviewed address layout plus image-local values and native fuel-cut registry | 14 families | Final-mask coordinator actuator | Schema 2, mailbox 26 | Six fields | `UNTESTED` on bench and vehicle hardware |

The VQ37 Map Switching model replaces the canonical 2x2 fuel-cut table with
two scalar caps and two independent eight-point curves. Exact stock function,
coordinator, scheduler pointer, calibration bytes, ROM pointers, and RAM bases
are bound in `../defs/vq37-native-fuel-cut.toml`. Rolling Launch executes the
stock final-mask coordinator first and adds all six cylinder bits only for the
exact request value `0x003F`.

## Remaining editor-parity work

Runtime capability does not imply complete source-map parity. The following
visible canonical roles still have no promoted target-native editor binding:

| Target family | Canonical roles without a target binding | Classification |
| --- | --- | --- |
| JK78C and `1ND` | exhaust-CVTC target surface `0x0B33A` | The published target byte has no statically resolvable store; the writer, its calibration storage, and the editor geometry remain unbound |

The `8MFK` projections carry no unsupported source row. Every visible canonical
map and required axis reaches a reviewed JK00C and JK00D address. The
stationary rev-limiter and accelerator-pedal thresholds are bound through the
shared literal pool of the relocated calculators: JK08A `FUN_0004F324`
corresponds to JK00C `0x050C9A` and JK00D `0x050C96`, and JK08A `FUN_00047A56`
corresponds to JK00C `0x048ADC` and JK00D `0x048AE0`.

The exhaust-CVTC boundary is characterised by four independent results. The
canonical 16x16 interpolation contract `0x261B8` has no homolog in either
complete VQ37 interpolation library census. The service-0x22 `0x11xx` pointer
table is index-aligned with the canonical table, which places DID `0x1166` at
JK78C `0xFFFF23A4` and 1ND `0xFFFE9466`; three unrelated slots of the same
table carry independent direct-reference evidence. Neither published byte
appears in the complete Ghidra reference export of its image, while the
canonical `0xFFFF2327` carries 21 references. Enumerating every indexed store
through the JK78C state base `0xFFFF2314` yields written displacements
`0x20..0x8E` and never `0x90`. The exhaust target is therefore published
through a path that static address resolution does not reach, and no
target-native calibration storage is established.

The three canonical intake-CVTC source slots `0x0AB5A`, `0x0B43A`, and
`0x0B53A` are explicit no-op dispatcher slots in the reviewed VQ37 topology.
They are architectural removals rather than missing address relocations. The
canonical fuel-cut table `0x0934E` also remains an unsupported source row on
VQ37, but its tuning role is covered by the target-native cap and curve maps.

No unsupported row may be replaced with a similar address or graph neighbor.
Promotion requires exact target storage, geometry, consumer path, and stock
image binding.
