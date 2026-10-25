# JK08A exact scaling and division caller withdrawals

The natural callers 4E59C, 74478 and 74B04 and real 224FA/21BBC helpers contain
340 stock instructions, 680 code bytes and 5 code spans. The caller-scoped
closure contains 191 feasible caller instructions. The descriptor binds
33 literal spans, 9 pointer aliases, 2 controlled word divisors and
33 complete calibration spans. The joint descriptor contains 123 exact access
originals: 115 readers and ten individually pinned writers, 95 complete owners,
67 complete functions and 117 matching ledger selectors. All 125 exact normal
unlink operations are mandatory. The selected unsupported originals are:

| Datum | Natural function | Exact unsupported original |
|---|---|---|
| `7mfk:00012432` | `7mfk:0004e59c` | `37a7d0813e696d1ae72ff71cc98a0e9c83c5bb1ebaae0c2d6ef020df01fe2bc7` |
| `7mfk:00015770` | `7mfk:00074b04` | `8aa69bd24e2f365fc2ba12af43e13ec5ed1436dcb34c5c32179bd485ca529ce0` |
| `7mfk:00019190` | `7mfk:00074478` | `0e56068a2df4d1cc74996097fda4018457460adda77683a8ffa87bd7b0587f0b` |

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

The 8 two-sided caller conditions require both feasible outcomes. The 1 fixed
reciprocal cap retains its bounded inactive result. The seven real shift-helper
instructions and every feasible caller instruction are required. The complete
21BBC bytes remain in the fixture; the separate unchanged complete division
and register-only originals from the identical COPY primary retain all prior
generic helper entries, branch outcomes and native/TEST obligations.

Actual fixed-other output alternatives bind each raw source/gain/divisor,
independent flag byte, blend weight and signed history. Complete configuration
and context widths, ordered physical ROM/RAM/frame operands, all call delays,
natural returns, zero fault effects and immutable instruction/pool bytes are
mandatory. The generated driver and matrix contain no expected outputs.

The three selected originals are readers without roles. Existing three writer
exceptions and eighteen individually pinned indexed_by originals remain exact.
The only shared owner is kind-kittiwake/tbl. It permits one additional exact
reader/link-selector deletion. Full preceding prefix postimages are rebuilt
from complete original documents and only their exact prefix removals; full
current postimages retain separate exact identity pins. All prior54 records,
38 functions, every other field/order/type/evidence/TEST/ledger fact and the
earlier prior19/26/31/34/35/38/40/41/44/49 boundaries remain mandatory. No native
type widening, generic helper ownership change or reverse fact donation exists.

The selected ROM12432/15770/19190 roots require physical interval absence
independently of the event domain label. Real ROM944E/16316 reads, semantic
dependencies, pointer values or data written by another function do not grant
the selected physical reader identities. No owning replacement is published.

The 99 prior domain sources retain 98 byte-identical sources and the existing
explicit two-site gated spelling exception with exact current/legacy hashes.
All original RPM/helper, counter/MAF, prior source/TEST/type/ledger and physical
proof scopes remain exact. Twenty-seven independent components require one complete
original COPY primary. The ordinary registry contains
thirteen families and forty-seven capture bindings. The seventeenth standard
source-only adapter retains the preceding sixteen adapters and all thirty-two
generated output identities. Its terminal marker is
VQ_SH_ELF_SCALED_DIVISION_CALLER_WITHDRAWAL.

Complete actual-original/controlled source/input/product-wrap/signed-shift/
zero-fault/reciprocal/saturation/blend/physical/CPU/frame/SR/full-call/return/
native-root/shared-owner/prior/type/role/TEST/ledger/scope/review refusal sources,
published-count gates and common anchors are mandatory. Source preparation
grants no executable acceptance, geometry, scale, units, caller interpretation,
hardware qualification or publication.

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
