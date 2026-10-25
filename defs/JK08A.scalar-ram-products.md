# JK08A scalar RAM product withdrawals

The source boundary contains four natural entries, 199 stock instructions,
398 code bytes, 24 literal/configuration spans and 8 pointer aliases. The
exact descriptor is `defs/JK08A.scalar-ram-products.toml`. Seven exact
unsupported ROM-reader originals share the existing
`scalar-ram-leaf-withdrawal` family with nineteen scalar RAM leaf originals.
The joint descriptor pins 123 relations, 95 complete native owner transitions
and 67 complete retained functions. Its normal writer requires all 125 exact
`unlink` operations and removes 117 matching ledger selectors.

| Datum | Natural function | Exact unsupported original |
|---|---|---|
| `7mfk:0000abba` | `7mfk:000a5284` | `49079a5f27a6eaf6cbd98b4c01e6df5e3c90299c2733958e08ecefd1dad77abd` |
| `7mfk:0000abfa` | `7mfk:000a5284` | `aae3934fa0bdc4c566945b51bc78c9608206e103218c947e8419f4915c5ca0e1` |
| `7mfk:00012176` | `7mfk:00052902` | `1203c702373ffa952f31f2b3ce62af854749e24f92b06761bec1e692803562a5` |
| `7mfk:0001233a` | `7mfk:0005444c` | `5aadff23e65061162eb21e81a53fa223a2df9e82c8999244a2f9cb0d58535f1e` |
| `7mfk:00012352` | `7mfk:0005444c` | `6f87244dfbf5f668f11d4b1e6e023d2689254ce52f7a4a185d5bdfabe27f49bb` |
| `7mfk:000123e2` | `7mfk:000a5284` | `211523f962786d4111a6029f4d54f1689f3359705575f13f235b52a242acf873` |
| `7mfk:00012432` | `7mfk:0005279c` | `16dd91b882b70fa7ee892396a8cd9b27ac8ce3d282d6715401562f2857d870d8` |

Entry5279C subtracts the full previous long from the zero-extended target
word shifted eight bits, retaining low32 signed interpretation. It truncates
the signed difference toward zero by256, multiplies by an unsigned gain byte,
truncates toward zero by32 and saturates the signed word output atFFFF1A66.
The real error flag byte atFFFF4184 disables the arithmetic and publishes
zero through the natural conditional delay slot. The active path leaves
R2=FFFF8000; the disabled path retains incoming R2. R0 carries offset07DA.

Entry52902 multiplies an unsigned gain byte by a signed input word, truncates
toward zero by256 and publishes the signed additive word atFFFF2300. The
RAM flag bit20 atFFFF245D and ROM configuration bit04 at8B40 jointly select
zero. The quotient lies in-32640..32639. Therefore52930 is fixed taken,
5293E is fixed fallthrough, and52932 is unreachable under the exact byte/word
input domain. The bound clamp bytes retain their stock identity.

Entry5444C multiplies two unsigned RAM bytes and the controlled ROM factor
at8BBE. It shifts14 bits and caps the first result at255 before publishing
FFFF33BE. Multiplication by the unsigned word atFFFF1024, shift5 and a
separate65535 cap produce FFFF415A. This second product lies in0..16711425,
so5448E is fixed taken and54490 is unreachable. The independent consumer
requires 13 two-sided conditional sites, 3 fixed conditional outcomes and
binds the 2 unreachable instructions without claiming executed coverage.

EntryA5284 uses only the low16 halves of incoming R4/R5. With x=R4.low16,
w=R5.low16, a=byte[FFFF338A] and b=byte[FFFF2FF2], P=w*a*b. The forward
term is F=FFFFFFFF when P>=80000000, otherwise F=2*P. The retained term
is G=(65536-w)*x. The result is min((F+G)>>16,65535), retaining the full
high-half sum and low-half carry. Complete post-delay registers bind the
uncapped high sum in R4, carry in R6, retained high half in R5, final
cap carrier in R2 and returned word in R0.

Independent scalar equations predict every GPR, SR, GBR, MACH, MACL, complete
RAM, frame and natural control path. A separate instruction engine predicts
the exact byte execution. Ordered physical guards bind every pool,
configuration, RAM and stack operand by site, address, width, register and
byte value. Every feasible branch, jump, RTS and delay slot is mandatory.
The selected ROM datum roots cannot be replaced by real RAM or pool operands.
Actual return/store variation holds complete other RAM/register/SR/frame/
ABI/SP/continuation/code/configuration preimages fixed. Cases and the generated
driver carry inputs only.

The existing COPY primary carries both `scalar_ram_leaf_paths` and
`scalar_ram_product_paths`. Both independent consumers are mandatory in the
same original record. Each filters exactly its own originals and requires
its exact-domain and no-selected-datum flags with native identity disabled.
The joint native transition preserves every other field, surviving link and
selector position, type, original TEST context and physical proof scope.

The first nineteen reference records retain a full-record digest. Their
previous postimages are reconstructed by removing only those nineteen
original links/selectors from their complete original documents. The joint
postimages are independently reconstructed by the exact twenty-six removals.
Only tuscan-porcupine/tbl and soft-pronghorn/tbl share both components; each
receives precisely the additional A5284 reader/selector deletion. The first
twelve complete function records retain their full digest. Nine source-file
pins retain the previous leaf fixture, matrix, numerical/physical equations,
producer, generated driver and generated refusal source byte identities.

The ordinary registry contains thirteen families and forty-seven capture bindings.
The standard seventh source-only adapter retains the existing 80/572 observer,
64KiB RAM domain and complete observation transport; the preceding six adapters
retain their byte identities. No replacement owning claim or evidence item,
identity, geometry, scale, units, caller reachability, hardware qualification
or publication follows from this withdrawal source.

Original and controlled refusal sources cover complete raw streams, source
bytes, toolchain, input widths, exact reconstruction/aliases, CPU/RAM/frame/
ABI state, ordered physical accesses, branch/return/delay effects, arithmetic
and fixed-width premises, actual output alternatives, both independent
components, prior full-record and source-file retention, exact native writer,
review retirement, TEST/type/ledger/scope preservation and forbidden donation.
Source preparation supplies no passing executable acceptance.

The joint batch also binds five gated/indexed scalar originals through
`scalar_ram_gated_paths`. The first26 full reference records and first16
full functions retain separate reconstructed-boundary digests; nine exact
product source pins retain the input, fixture, scalar/physical, producer and
generated identities. The additional shared owners are cautious-iguana/tbl
and rev_limit_throttle_cut/tbl, each with its exact selected deletion.
`defs/JK08A.scalar-ram-gated.md` defines the five-original boundary.

The joint batch also binds three selected native RAM readers through
`rpm_ram_withdrawal_paths`. Its separate mandatory native RAM/alias absence
guard cannot use ROM-only absence as evidence. The full first31 reference prefix retains reconstructed complete postimage
digests; first21 functions retain direct digests, with nine gated source pins. Complete existing counter/MAF owner and reference inputs are retained.
`defs/JK08A.rpm-ram-withdrawal-paths.md` defines this component's exact
physical and original-role boundary.

The joint batch also binds the exact265C4 register-overflow helper through
`register_overflow_paths`, including NEG80000000 and all four natural
returns. The complete prior34 references retain reconstructed prefix postimage
digests and prior24 functions retain direct digests, with nine exact RPM RAM source pins. The shared byte instruction
engine includes the required ADDV/SUBV forms in the complete current source
snapshot. `defs/JK08A.register-overflow-paths.md` defines this boundary.

The complete word-rate/channel component is defined by
`defs/JK08A.scalar-ram-word-paths.md`. Its exact shared rev-limit delta
retains full prior35 reference/prefix postimages and25 function bindings;
current postimages are separately pinned. Six independent components
share one original COPY primary and preserve every other native fact.

The complete RPM-state component is defined by
`defs/JK08A.rpm-state-withdrawal-paths.md`. Its two exact indexed_by readers
share tough-earwig/ram and have no matching selectors. Full prior38/28
reference/function boundaries and nine exact word-domain source pins remain
mandatory. Twenty-seven independent components share one original COPY primary.

The exact indexed-word component is defined by
`defs/JK08A.indexed-word-update-paths.md`. Its single writer type is pinned
by original identity; all40 prior reader records and30 complete functions
retain direct digests. The physical state-word overlap, temporary/restored
interrupt mask and intermediate frame-pointer effects remain independent
obligations under the shared original COPY primary.

The complete bounded-divisor caller component is defined by
`defs/JK08A.division-caller-withdrawal-paths.md`. Its real signed/unsigned
helpers retain a separate complete direct-helper original from the identical
primary. The only additional shared-owner delta removes the selected
scrupulous-yak reader/selector. Full prior41/31 and earlier prefix boundaries
retain complete previous records while current postimages remain separately pinned.

The constant-root byte-curve caller component is defined by
`defs/JK08A.byte-curve-caller-withdrawal-paths.md`. Its two additional writer
ids remain individually pinned. Full prior44 records/34 functions and all nine
division-caller source inputs retain exact direct boundaries. The real interior
byte path and its intermediate frame save/read remain separate from later
division state and from unchanged generic helper ownership.

The constant-root word interpolation caller component is defined by
`defs/JK08A.word-interp-caller-withdrawal-paths.md`. Full prior49 records and
36 functions retain complete reconstructed boundaries. One authoritative 65-word union binds
the shared curve neighbor. All earlier full helper originals remain mandatory,
and this component also requires the unchanged timing-denominator original
from the identical primary. The three exact writer exceptions remain unchanged.

The scaling/division caller component is defined by
`defs/JK08A.scaled-division-caller-withdrawal-paths.md`. Its shared owner permits
only the additional exact kind-kittiwake reader/link-selector delta. Full
prior54 records and 38 functions retain complete reconstructed prefix digests,
with current full postimages separately pinned. All nine word-caller input
sources remain exact. Complete division and register-only originals from the
identical primary are mandatory in addition to every preceding helper obligation.

The constant-root curve/scale caller component is defined by
`defs/JK08A.curve-scale-caller-withdrawal-paths.md`. Full prior57 records and41 functions retain complete prefix postimage digests;
current complete postimages have separate exact identity pins. All nine preceding
scaling/division inputs retain byte identities. The real32-word axis and
33-word curve, two pointer aliases and unrelocated negative comparison literal
remain explicit. Unchanged complete uptight-duck and division originals from
the identical primary retain proper neighboring ownership and every full helper obligation.

The paired derivative-scale caller component is defined by
`defs/JK08A.derivative-scale-caller-withdrawal-paths.md`. Complete prior60
postimages are reconstructed from full originals and exact prefix removals;
current complete images are separately pinned. The two shared owners admit
only four additional exact reader/selector removals. Full timing, normalization,
division and viridian originals remain mandatory from the identical primary.

The guarded quotient caller component is defined by
`defs/JK08A.guarded-quotient-caller-withdrawal-paths.md`. Complete prior71
records and44 functions retain exact prefix reconstruction with separately
pinned current images. Shared opal/vigilant owners admit only two additional
exact reader/selector removals. Real zero/word/large-divisor instructions,
signed fraction wrap, ordered frame carriers and full direct helper originals
remain mandatory from the identical primary.

The mixed curve caller component is defined by
`defs/JK08A.mixed-curve-caller-withdrawal-paths.md`. Complete prior79 records
and47 functions retain full prefix reconstruction with separate current-image
pins. Three shared owners admit only exact additional reader/selector removals.
Disjoint implicit ranges, the unread immutable gap, complete local frame
carriers and the actual unselected134A write remain explicit. Full original
timing,implicit,register and division obligations remain mandatory from the
identical primary.

The timing and remainder caller component is defined by
`defs/JK08A.timing-remainder-caller-withdrawal-paths.md`. Complete prior87
records, current postimages and51 functions remain directly exact. The exact
eight-knot curve, raw signed-history/low-word steps and saved numerator/quotient
carriers retain full physical and actual CPU obligations. Actual word2000
publication remains explicit and its original reader is unselected. Actual
common computed publication alternatives exclude controlled RAM input echoes
and write-set-only differences. All full preceding helper/native/TEST and
original remainder-source obligations remain mandatory from the identical primary.

The complete state-ratio and byte-transition component is defined by
`defs/JK08A.state-ratio-caller-withdrawal-paths.md`. Full prior92 records,current
postimages and53 functions retain direct exact boundaries. Signed-word divisor
normalization,raw32 ratio operations,two distinct byte curves and separate
candidate/counter publications retain their complete physical and actual CPU
obligations. All full preceding division,byte-caller,standard implicit-byte,
native and TEST originals remain mandatory from the identical primary.

The complete DFCO state component is defined by
`defs/JK08A.dfco-state-caller-withdrawal-paths.md`. Full prior 100 records, current
postimages and 55 functions retain direct exact boundaries. All 256 state bytes,
six delay bytes, raw local R6 word/dword/byte operations, real rotation loop and
actual 1939 writes retain complete physical and CPU obligations. All preceding
family/helper/native/TEST originals remain mandatory from the identical primary.

The complete paired flag writer component is defined by
`defs/JK08A.paired-inhibit-writer-withdrawal-paths.md`. Full prior 107 records and
56 functions retain exact boundaries. Entry-scoped absence preserves the real
first-entry 4A45/4A70/4AC6 stores. All ordered RMW read/write pairs, the real nibble
helper and five exact reverse selectors in two complete function postimages
remain mandatory. The joint total includes 109 datum-end selectors and
8 function-end selectors. Every previous family/helper/native/TEST original
remains mandatory from the identical primary.

The complete threshold-window reader component is defined by
`defs/JK08A.threshold-window-reader-withdrawal-paths.md`. Three exact additional
reader removals compose with the preceding paired writer postimages of the
same three datum owners. Full prior 112 records reconstruct exactly; all
58 complete prior function records, including both exact function postimages,
remain unchanged. The full raw coordinate window, two real signed divisions,
ordered local byte/dword carriers and actual boolean return remain bound.
All previous family/helper/native/TEST originals remain mandatory from the
identical primary. The joint selector total contains 109 datum-end and
8 function-end removals.

## Joint paired normalization boundary

The joint descriptor contains125 exact access originals:115 readers and ten
individually pinned writers,95 complete datum owners,67 complete functions and
117 matching ledger selectors. These contain109 datum-end selectors and
8 function-end selectors. Twenty-seven independent components require one
complete original COPY primary. The registry contains thirteen families and
forty-seven capture bindings. The paired normalization boundary is specified
in `defs/JK08A.paired-curve-normalization-withdrawal-paths.md`.

The complete prior reference and function boundaries retain exact full-record
digests. The sole additional current image delta is at lyrical-dragon/tbl
reference79:two exact reader links and two matching owner-end selectors.
No other preceding reference field or complete function record changes.
Both complete prior function transitions,five function-end selectors,eight
writer identities,eighteen indexed_by originals and every previous full
family/helper/native/TEST original remain mandatory from the identical primary.

The complete byte-ratio producer boundary is specified in
`defs/JK08A.byte-ratio-producer-withdrawal-paths.md`. The complete118-record and62-function prefix retains exact reconstructed
digests and explicitly bounded current shared-owner transitions,including
the paired-reader shared image and both full function transitions. Full variable
unsigned division,signed shift10,actual saved post-DIV1 R1 frame continuity,
byte publication and complete prior same-primary originals remain mandatory.

The complete state-surface caller boundary is specified in
`defs/JK08A.state-surface-caller-withdrawal-paths.md`. All119 preceding core
records and63 full functions remain exact. Only the additional row99 reader
and owner-end selector delta changes its full current postimage; the other118
full records,paired row79 and both complete function transitions remain exact.
The complete local word carrier,three state modes,raw four-row surface and
implicit-byte curve retain both broader same-primary originals.

The complete byte-factor caller boundary is specified in
`defs/JK08A.byte-factor-caller-withdrawal-paths.md`. All121 preceding full
records,current images and64 complete functions remain exact. An additional
complete function transition removes one individually pinned reverse writer
selector;the preceding two transitions,row79,row99,eight writer identities
and eighteen indexed_by originals remain exact. Both real byte curves,signed
word promotion,partial products and the percentage delay-slot store are required.

The complete byte-sum caller boundary is specified in
`defs/JK08A.byte-sum-caller-withdrawal-paths.md`. All122 preceding full
records,current images and65 complete functions remain exact. An additional
complete function transition removes one exact reverse writer selector;the new
datum owner retains its absent ledger. The preceding three full transitions,
row79,row99,nine writer identities and eighteen indexed_by originals remain exact.
