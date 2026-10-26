# JK08A exact indexed word native writer withdrawal

Source bindings: `JK08A.indexed-word-update-paths.toml`.


The actual entry converts incoming R4 and R5 to a byte index and byte mask.
The disabled path retains the full incoming index in R7 while its conditional
delay slot converts the mask. Enabled paths retain the actual fuel/inhibit/hold
priority, signed threshold word, unsigned configuration byte times128,
status1220 read/modify/write and complete preserved raw register context.

The delta view begins atFFFF1396 and the threshold view atFFFF142E, both
with256 word elements selected by the byte index. Their 76-word offset
creates one overlapping physical union of 332 authoritative state words.
The shared words have one input field and one physical preimage. Independent
logical copies cannot overwrite each other. The separate array atFFFF2348
contains 256 independent counter words. Every index, both logical views,
overlap boundaries and signed-word boundaries retain their actual addresses.

The update subtracts a signed16 delta from an unsigned16 counter, floors
negative differences to zero and stores the low16 word. Positive differences
can exceed65535:65535-(-1) produces65536 in R6 and0000 in RAM. There is no
upper saturation. The complete R4 difference and R6 result, final T,
status byte and all other RAM/register/frame effects remain independent.

All 128 complete SR contexts retain Q/M, every interrupt mask and both T
values. The counter path temporarily sets interrupt bitsF0 while preserving
the other SR bits, then restores the exact incoming mask with the arithmetic
T. Disabled, blocked and held paths retain their distinct final CPU state.
The frame at depth12 first stores pointer01002330, reads that exact pointer
and later replaces it with01002348. An identical terminal frame cannot
replace these intermediate ordered events. The complete saved old status,
temporary GBR and natural GBR restore remain bound to the original path.

The 6 two-sided conditional sites require both feasible outcomes. Every
instruction is feasible. The 1 natural RTS site520E8 retains its real
520EA GBR-restore delay slot. Independent complete scalar/CPU/SR/frame/RAM
equations, ordered physical ROM/RAM/stack operands, exact temporary/restored
SR states and fixed-other actual return/store alternatives are mandatory.
The generated driver and input matrix contain no numerical expectations.

The indexed-word writer type override names00052034-ffff120e-withdraw and its exact
original SHA256. All40 earlier originals retain their reader type. Their full records
reconstruct exact prefix postimages and compare the complete prior digest;
all30 prior complete functions retain their direct digest. The new owner is distinct. Only its selected writer and one
matching selector are removed. Surviving links/selectors, their order,
all other native fields, types, function facts, original TEST contexts,
reverse support properties and physical proof scopes remain exact.
Earlier prior19/26/31/34/35/38 boundaries remain mandatory. The three exact
indexed_by reader roles are unchanged. No arbitrary writer is admitted.

The selected rootFFFF120E and simulator alias0100120E identify the original
physical claim. Any overlapping memory interval at either form refuses
independently of its domain label. The actual word/status arrays, semantic
dependencies or the pointer value itself do not establish a physical access
to that root. A separate native-RAM absence admission is mandatory. No
owning replacement, reverse donation, geometry, scale, units or caller
interpretation is created.


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
remain mandatory. The joint total includes 118 datum-end selectors and
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
identical primary. The joint selector total contains 118 datum-end and
8 function-end removals.
