# JK08A exact scaling and division caller withdrawals

Source bindings: `JK08A.scaled-division-caller-withdrawal-paths.toml`.


Caller 4E59C reads unsigned word 1652 and byte 15DE, computes their product
times six and shifts logically by fifteen bits. Its actual complete input
widths bound the denominator below 65535, so the first cap is fixed inactive.
The denominator is published at 12C2. The real signed divider receives that
nonnegative denominator and numerator 65536 after the actual SHLL16 delay
slot. Zero executes the actual fault store 044E at 9818 and returns zero.
The caller adds 256, caps the unsigned result at 65535 and stores word 16C0.
The temporary GBR, complete MACL, PR and SP are restored at the natural return.

Callers 74B04 and 74478 multiply two unsigned words modulo 2^32 and pass the
complete product through the real 224FA helper. Its six SHAR instructions,
including the RTS delay slot, interpret the product as signed32 and leave T
equal to original product bit5. A logical shift or unbounded positive product
is not an equivalent premise. Each shifted value is multiplied by a signed
word modulo 2^32, then divided by an explicit unsigned word from ROM944E or
ROM16316 through the real 21BBC entry. The independent quotient equation
truncates toward zero. Actual zero/short/long helper paths remain distinct.

Caller 74B04 saves the complete dividend in its reserved caller frame word
from the first JSR delay slot. A quotient at most 32767 causes another real
division using the same saved dividend and a second actual divisor read.
The result is saturated to signed16 and stored at 18E8. Two zero-divisor
invocations produce two physical fault writes even when final RAM is identical.
Two long invocations can save different R4 values at the same frame depth;
each intermediate save/read remains exact. A final frame image or one quotient
cannot replace these actual events or the second invocation.

Caller 74478 saturates its first quotient to signed16 and stores 1CF8. Active
flags 245F.bit7, 417E.bit3 or 249B.bit0 select direct publication at 1D00.
Otherwise unsigned weight 2422 selects current at zero, signed history 1CF6
at 65535, or the modulo32 sum current*(65536-weight)+signed(history)*weight.
The real SWAP.W keeps both result halves; only the low word is published.
The full returned R4 is distinct from a sign-extended published word. Complete
MACL, PR, R14 and SP are restored through the natural RTS delay slot.

Separate equations retain complete RAM and intermediate frame words, all
known returned registers and SR, complete post-delay helper input GPR/SP/PR/
GBR/MACH/MACL/SR state, signed shift T, fault writes and natural helper returns.
Positive-divider remainder and Q are not assigned by the quotient equation;
complete actual CPU/SR/frame/RAM must match the independent instruction oracle
that executes every helper byte. Helper entry and intermediate CPU snapshots
remain bound to the exact post-delay instruction path. No helper executes
through an arithmetic stub or a substituted output.

The reciprocal cap is inactive within the described caller domain.

Actual fixed-other output alternatives bind each raw source/gain/divisor,
independent flag byte, blend weight and signed history. Complete configuration
and context widths, ordered physical ROM/RAM/frame operands, all call delays,
natural returns, zero fault effects and immutable instruction/pool bytes are
mandatory. The generated driver and matrix contain no expected outputs.


The selected ROM12432/15770/19190 roots require physical interval absence
independently of the event domain label. Real ROM944E/16316 reads, semantic
dependencies, pointer values or data written by another function do not grant
the selected physical reader identities. No owning replacement is published.


Complete actual-original/controlled source/input/product-wrap/signed-shift/
zero-fault/reciprocal/saturation/blend/physical/CPU/frame/SR/full-call/return/
native-root/shared-owner/prior/type/role/TEST/ledger/scope/review refusal sources,
published-count gates and common anchors are mandatory. Source preparation
grants no executable acceptance, geometry, scale, units, caller interpretation,
hardware qualification or publication.

The constant-root curve/scale caller component is defined by
`defs/analysis/interpolation/JK08A.curve-scale-caller-withdrawal-paths.md`. Full prior57 records and41 functions retain complete prefix postimage digests;
current complete postimages have separate exact identity pins. All nine preceding
scaling/division inputs retain byte identities. The real32-word axis and
33-word curve, two pointer aliases and unrelocated negative comparison literal
remain explicit. Unchanged complete uptight-duck and division originals from
the identical primary retain proper neighboring ownership and every full helper obligation.

The paired derivative-scale caller component is defined by
`defs/analysis/arithmetic/JK08A.derivative-scale-caller-withdrawal-paths.md`. Complete prior60
postimages are reconstructed from full originals and exact prefix removals;
current complete images are separately pinned. The two shared owners admit
only four additional exact reader/selector removals. Full timing, normalization,
division and viridian originals remain mandatory from the identical primary.


The mixed curve caller component is defined by
`defs/analysis/interpolation/JK08A.mixed-curve-caller-withdrawal-paths.md`. Complete prior79 records
and47 functions retain full prefix reconstruction with separate current-image
pins. Three shared owners admit only exact additional reader/selector removals.
Disjoint implicit ranges, the unread immutable gap, complete local frame
carriers and the actual unselected134A write remain explicit. Full original
timing,implicit,register and division obligations remain mandatory from the
identical primary.

The timing and remainder caller component is defined by
`defs/analysis/ignition/JK08A.timing-remainder-caller-withdrawal-paths.md`. Complete prior87
records, current postimages and51 functions remain directly exact. The exact
eight-knot curve, raw signed-history/low-word steps and saved numerator/quotient
carriers retain full physical and actual CPU obligations. Actual word2000
publication remains explicit and its original reader is unselected. Actual
common computed publication alternatives exclude controlled RAM input echoes
and write-set-only differences. All full preceding helper/native/TEST and
original remainder-source obligations remain mandatory from the identical primary.


The complete DFCO state component is defined by
`defs/analysis/fuel/JK08A.dfco-state-caller-withdrawal-paths.md`. Full prior 100 records, current
postimages and 55 functions retain direct exact boundaries. All 256 state bytes,
six delay bytes, raw local R6 word/dword/byte operations, real rotation loop and
actual 1939 writes retain complete physical and CPU obligations. All preceding
family/helper/native/TEST originals remain mandatory from the identical primary.

The complete paired flag writer component is defined by
`defs/analysis/runtime/JK08A.paired-inhibit-writer-withdrawal-paths.md`. Full prior 107 records and
56 functions retain exact boundaries. Entry-scoped absence preserves the real
first-entry 4A45/4A70/4AC6 stores. All ordered RMW read/write pairs, the real nibble
helper and five exact reverse selectors in two complete function postimages
remain mandatory. The joint total includes 118 datum-end selectors and
8 function-end selectors. Every previous family/helper/native/TEST original
remains mandatory from the identical primary.

The complete threshold-window reader component is defined by
`defs/analysis/runtime/JK08A.threshold-window-reader-withdrawal-paths.md`. Three exact additional
reader removals compose with the preceding paired writer postimages of the
same three datum owners. Full prior 112 records reconstruct exactly; all
58 complete prior function records, including both exact function postimages,
remain unchanged. The full raw coordinate window, two real signed divisions,
ordered local byte/dword carriers and actual boolean return remain bound.
All previous family/helper/native/TEST originals remain mandatory from the
identical primary. The joint selector total contains 118 datum-end and
8 function-end removals.
