# JK08A exact register-overflow helper withdrawal

Source bindings: `JK08A.register-overflow-paths.toml`.



The helper tests the signed incoming R5. For R5>=0, ADDV changes R5 to the
low32 sum; positive overflow returns7FFFFFFF, otherwise the natural delayed
move returns R5. For negative R5 other than80000000, the NEG/SUBV path
changes R5 to its positive magnitude and R4 to the low32 sum; negative
overflow returns80000000, otherwise the delayed move returns R4.

For R5=80000000, NEG retains80000000. SUBV therefore computes the signed
first operand plus2147483648. With incoming signed R4<0, it returns that
nonnegative shifted result; with R4>=0, the overflow path returns80000000.
Examples include(-1,80000000) returning7FFFFFFF, (1,80000000) returning
80000000 and(80000000,80000000) returning0. These cases are distinct from
an ideal saturating-add substitution. Raw32 inputs establish no natural
caller operand range or hardware reachability. The native function summary
describes this piecewise raw32 behavior without claiming executable
qualification; the minimum-word boundary is explicit in this narrow contract.

Independent scalar equations use signed integer bounds and an explicit
minimum-word case, while the instruction engine uses low32 arithmetic and
sign-bit overflow logic. Both predict complete GPR/SR/GBR/MACH/MACL/SP/PR,
unchanged RAM, unchanged frame and the natural branch/return path. The
3 two-sided conditional sites require both outcomes. The 4 natural RTS sites
265CE/265D6/265DC/265E2 and each MOV/NOP delay slot remain exact.
The only physical data reads are the independently reconstructed long
constants80000000/7FFFFFFF at265E8/265EC. No RAM read, write, stack operand
or outside call is admitted. The observer/profile and instruction bytes
under test are unchanged.


Complete original and controlled raw/source/opcode/T/overflow/minimum-word/
constant/state/physical/four-return/RAM-alias/actual-output and full native/
prior/other-family/TEST/type/ledger/scope/writer/review refusal sources are
mandatory. Source preparation supplies no passing executable acceptance.


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
remain mandatory. The joint total includes 120 datum-end selectors and
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
identical primary. The joint selector total contains 120 datum-end and
8 function-end removals.
