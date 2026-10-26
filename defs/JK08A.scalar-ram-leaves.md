# JK08A scalar RAM leaf withdrawals

Source bindings: `JK08A.scalar-ram-leaves.toml`.


Entry259BE selects modular R4-R6 only when the low byte of R7 is zero and
returns the signed comparison with R5. Entries39588/39874 preserve a value
above its target and advance at most two toward a higher target. Entry468B0
combines unsigned words/bytes, two signed words and an optional byte before
clamping to0..65535. Entry4AB94 computes the nonnegative word difference,
multiplies by an unsigned word, shifts14 bits and caps the result. Entry554AE
adds0x4000 and two unsigned words to a complete low32 accumulator, retaining
the signed comparison and both saturation boundaries.

Entry4AF38 masks two incoming bytes to seven bits and publishes the separate
gated difference and nonnegative offset term. Entry4BB6A combines two bytes
and the upper trim nibble with0..255 clamps; its physical store at4BBA0 is
the natural RTS delay slot. Entry4C136 preserves both mode shortcuts, the
input flag update and status-dependent state selection. Entry70D82 selects
the signed request word and publishes both word copies; its final R0 carries
the literal offset0x736. EntryA5530 preserves each flag/gate/unsigned-word
comparison return carrier, both RTS sites and the actual delayed byte store.

Entry4E112 retains its early nonzero-latch return and its separate signed-byte
decay/configuration return. The byte input lies in-128..127, so a one-count
step toward zero lies in-127..126. The upper clamp branch at4E140 and lower
clamp branch at4E14E therefore have fixed taken outcomes. Their three
unreachable instructions4E142/4E144/4E150 remain bound stock bytes, with no
claim of executed coverage. The other 32 two-sided conditional sites require
both feasible outcomes. Both RTS4E15A/4E15E and every feasible conditional,
jump and return delay slot are mandatory.

The two-word MACL/GBR frame and single-word GBR/R14 frames preserve the exact
saved values and original return paths.

RAM arithmetic and ROM configuration reads are real accesses. Configuration
bytes8440/870C/8B3F are explicit controlled inputs. PC pools retain their exact
stock bytes except for the declared native RAM pointer aliases. The selected
ROM datum roots are distinct from all admitted physical data operands.
`no_selected_datum_access` independently rejects a read overlapping any
selected root or an unlisted ROM physical source; the complete ordered
physical guard also rejects substituted RAM and stack operands. Syntax or
function membership supplies no absence proof and no owning table identity.

Every used input has actual returned/stored output alternatives with complete
other RAM, context, SR, frame, ABI, SP, continuation and code/literal preimages
held fixed. Configuration alternatives omit only their exact byte in both
calibration and bound observations. R7 omits its register and declared frame
carrier, which are two copies of the same incoming argument. No expected
output is placed in an input case or generated driver.


Original and controlled refusal sources cover raw schema/streams/toolchain/
source bytes, exact reconstruction and aliases, complete CPU/RAM/frame/ABI,
physical operands and order, conditional and signed-byte premises, both
multi-return entries, actual output alternatives, full native documents,
TEST/type/ledger/scope preservation and exact writer/review retirement.
No executable acceptance or hardware behavior follows from source preparation.


The joint batch also binds the exact265C4 register-overflow helper through
`register_overflow_paths`, including NEG80000000 and all four natural
returns. The complete prior34 references retain reconstructed prefix postimage
digests and prior24 functions retain direct digests, with nine exact RPM RAM source pins. The shared byte instruction
engine includes the required ADDV/SUBV forms in the complete current source
snapshot. `defs/JK08A.register-overflow-paths.md` defines this boundary.


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
