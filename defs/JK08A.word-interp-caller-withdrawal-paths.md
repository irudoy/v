# JK08A exact constant-root word interpolation caller withdrawals

The natural callers 72F1E and B7B98 and nine real interpolation helpers contain
419 stock instructions, 838 code bytes and 11 code spans. The caller-scoped
closure contains 414 feasible instructions. The descriptor binds 21 literal spans,
2 pointer aliases, 65 physical curve words and 27 complete calibration spans.
The joint descriptor contains 124 exact access originals: 114 readers and ten
individually pinned writers, 95 complete owners, 66 complete functions and
116 matching ledger selectors. All 123 exact normal unlink operations are mandatory.
The selected unsupported originals are:

| Datum | Natural function | Exact unsupported original |
|---|---|---|
| `7mfk:000175c8` | `7mfk:00072f1e` | `4b97eb1e73817d75504aa38835796a7d10bb9268be350a5b62dda81c5f001cc6` |
| `7mfk:ffff1024` | `7mfk:000b7b98` | `ae1c5d03bbbaed09e5d8c4437305e27d646d11b5ce31b4186ccb46bc80db691c` |
| `7mfk:ffff11bc` | `7mfk:000b7b98` | `600906141f73792784d0da8ded0b5c30d632c7a90d94e1df0c6935fd7c872775` |
| `7mfk:ffff1d10` | `7mfk:00072f1e` | `61ff5c17a1c2a129ea4a3395359986ede8da0aef857bb6d6fc706cf8c2f0a8a9` |
| `7mfk:ffff35fe` | `7mfk:00072f1e` | `7cc39463a836a76598dd58578359fb7812eeeb0f673f03852f25d3e7639cd15d` |

Caller 72F1E reads the unsigned DWORD at 1D08 and the final low-axis word at
18EC4. A source above that unsigned threshold selects the high curve, shifts
the source logically by four bits and caps it at 65535. The low branch caps
the source at 65535; its cap is fixed inactive because the selected threshold
is already a U16 word. The natural helper 26714 searches 32 unsigned axis words,
reads the selected curve word and its physical neighbor, then tail-calls 26AF8.
The result is stored as a word at 1D12. The complete natural return restores PR.
Neither the DWORD read at 1D08 nor the word store at 1D12 accesses base 1D10.
No storage extent or geometry is inferred for that native symbol.

The high view starts at 18F96 and the low view at 18FD6. Their 32 semantic
words and one read neighbor share one physical word: high neighbor 32 is low
cell 0. One authoritative 65-word physical union covers both views. Each word
is supplied once; no independent view can overwrite the shared preimage.
The low-axis threshold is word 31 of its controlled 32-word axis, not an
immutable instruction literal or a second independently overwritten copy.
Both axes and the complete 16 by 16 word surface have explicit physical input
blobs. Input styles construct raw bytes only and contain no expected output.

Caller B7B98 supplies constant surface D40E, row axis 13D74 and column axis
13DB4 to the real 262A8 wrapper. R6 supplies the unsigned row coordinate and
R4 supplies the unsigned column coordinate. The JSR delay slot writes the
column word at SP+2; the wrapper reads its actual caller-local DWORD carrier
and extracts the low word. The low byte of R5 selects zero output or the
unsigned lookup word times the low byte of R7. The output is a DWORD at 2D04.
The complete incoming MACL, PR, R13, R14 and SP are restored through the natural
RTS delay slot. A zero-fraction surface return can be a sign-extended word;
the caller's explicit EXTU.W precedes multiplication and remains distinct.

The independent axis equation scans backwards and selects the rightmost
qualifying unsigned knot. Equality and values above the final knot have zero
fraction; values below all knots select index zero with zero fraction. An
interior bracket uses floor((coordinate-first)*65536/(next-first)). The chosen
next knot is strictly above the coordinate, so its actual divisor is positive
without a monotonicity premise. Duplicate, descending, flat and nonmonotonic
physical axis preimages retain the actual backward search behavior.

Both 26740 and 26AF8 compare unsigned operands with CMP/HS and use positive
distance interpolation: first plus or minus floor(abs(second-first)*fraction/
65536). A package name does not grant signed arithmetic to either helper.
Surface interpolation retains column-first then row interpolation, each
intermediate floor, actual zero-fraction bypass and raw sign promotion.

Separate compositional equations retain all returned GPRs, complete RAM,
every intermediate saved frame word, each physical operand, every feasible
instruction/control path, all helper post-delay CPU/SP/PR arguments and all
natural returned state. Fraction-divider Q/T values remain checked by the
complete independent instruction equations; the separate quotient equation
does not claim those bit states. Complete actual CPU/SR/frame/RAM observations
must match the instruction equations, and helper entry snapshots remain bound
to their exact post-delay trace states. No helper executes through a formula
or stock-function stub.

The 16 two-sided conditional sites require both feasible outcomes. The 3 fixed
premises are the inactive unsigned low cap and the positive-divisor branches
of both fraction helpers. The low-cap assignment and both zero-divisor RTS
pairs are outside this caller-scoped feasible closure. The separate unchanged
complete timing-denominator original from the identical COPY primary remains
mandatory; every existing full helper, native binding and path obligation is
retained. Generic helper ownership and arbitrary-entry reachability are unchanged.

Actual fixed-other output alternatives bind raw arguments, complete physical
surface/axis blobs and all 64 semantic curve cells. The final physical neighbor
is read at zero fraction and has no claimed output causality. Its two bytes
remain exact inputs and physical read obligations. Each alternative mask
changes only the selected physical bytes and their bound copies while retaining
every other CPU, frame, RAM, calibration and instruction preimage.

All five additional originals are readers. Three exact indexed_by roles retain
their original level/reverse support properties. All five owners are distinct
from the prior batch. Full prior49 records and 36 functions retain complete reconstructed
digests; current full postimages remain separately pinned. The earlier prior19/26/31/34/35/38/40/41/44
boundaries remain mandatory. The three writer exceptions remain individually
pinned. Unknown native widths remain unknown; the two declared U16 RAM types,
surviving links/selectors, order, evidence, other-family facts, complete function
documents and every original TEST position remain exact.

Selected ROM root 175C8 and native RAM roots FFFF1024, FFFF11BC, FFFF1D10 and
FFFF35FE require physical interval absence, including the exact RAM aliases,
independently of domain labels. An axis argument, semantic dependency, literal
value, neighboring word or output of another function grants no selected
physical reader identity. No owning replacement or reverse fact donation exists.

The 90 prior domain sources retain 89 byte-identical sources and the existing
explicit two-site gated assembly spelling exception with exact current and
legacy hashes. Original RPM, counter/MAF, prior source/TEST/type/ledger and
physical helper scopes remain unchanged. Twenty-seven independent components require
one complete original COPY primary. The ordinary registry contains
thirteen families and forty-seven capture bindings. The sixteenth standard
source-only adapter retains the preceding fifteen adapters and all thirty
generated output identities. Its terminal marker is
VQ_SH_ELF_WORD_INTERP_CALLER_WITHDRAWAL.

Actual-original and controlled source/byte/input/axis/unsigned-rounding/shared-
neighbor/fifth-argument/physical/CPU/SR/frame/full-call/return/native-root/type/
prior/TEST/ledger/scope/review refusal sources and source-bound count gates are
mandatory. Source preparation grants no executable acceptance, native geometry,
caller interpretation, hardware qualification or publication.

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
7 function-end selectors. Every previous family/helper/native/TEST original
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
7 function-end removals.

## Joint paired normalization boundary

The joint descriptor contains124 exact access originals:114 readers and ten
individually pinned writers,95 complete datum owners,66 complete functions and
116 matching ledger selectors. These contain109 datum-end selectors and
7 function-end selectors. Twenty-seven independent components require one
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
