# JK08A scalar RAM product withdrawals

Source bindings: `JK08A.scalar-ram-products.toml`.


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




Original and controlled refusal sources cover complete raw streams, source
bytes, toolchain, input widths, exact reconstruction/aliases, CPU/RAM/frame/
ABI state, ordered physical accesses, branch/return/delay effects, arithmetic
and fixed-width premises, actual output alternatives, both independent
components, prior full-record and source-file retention, exact native writer,
review retirement, TEST/type/ledger/scope preservation and forbidden donation.
Source preparation supplies no passing executable acceptance.


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
