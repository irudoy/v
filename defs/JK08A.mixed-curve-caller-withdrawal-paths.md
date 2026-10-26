# JK08A mixed curve caller withdrawals

Natural callers 3B498, 41DB6, 4BDC2 and 659AE and their complete real helper
closures contain 964 stock instructions, 1928 code bytes and 17 code spans.
The bounded caller closure requires 876 feasible instructions. The descriptor
binds 70 literal spans, 22 pointer aliases, 43 complete RAM fields,
114 scalar configuration fields, 79 complete calibration spans,
175 raw input fields and 33 reused helper sources. The joint descriptor
contains 129 exact access originals: 119 readers and ten individually pinned
writers, 98 complete owners, 70 complete functions and 121 matching ledger selectors.
All 129 exact normal unlink operations are mandatory. The selected unsupported
originals are:

| Datum | Natural function | Exact unsupported original |
|---|---|---|
| `7mfk:00010b8e` | `7mfk:000659ae` | `ea68a6b80640ced3d347421e1ee38375a22e6c9cf0533775b444cda015a877b7` |
| `7mfk:00012196` | `7mfk:0004bdc2` | `c638206ca7fd33d917a82061925c79683301c5962be263783d279abd091196c6` |
| `7mfk:0001219e` | `7mfk:0004bdc2` | `aa811f9566043dbf2c67f43e399ca35b654a4e71c2e867c02a1770567444e549` |
| `7mfk:000127a8` | `7mfk:00041db6` | `da9b2c172b7614e33d3f913c1790f81e57080f8fa8a6a04819431a70df59ff26` |
| `7mfk:000127e8` | `7mfk:00041db6` | `798c9e94fd08d7709381dd7e051c1adbfdddf5b66dbf86bf5fda357d950b9098` |
| `7mfk:00013202` | `7mfk:0003b498` | `7a47a5cc01d09c1a49e7799cdcc523dbc8025b812b7c275d2e0d2056f0e62aaa` |
| `7mfk:000154a0` | `7mfk:000659ae` | `8493572c035dac033b196ebb017eda328de39e92d345597c2bf41d343b257a2b` |
| `7mfk:000155a0` | `7mfk:0003b498` | `4246f372f407cd8d806292efe7d3c6e57559411abc87c010b448167fb21a3ad7` |

All four natural bodies are complete and contiguous. The exact spans are
3B498..3B520, 41DB6..41E40, 4BDC2..4BEF2 and 659AE..65A92. All original
instructions, branch outcomes, delay slots, register saves, special registers,
stack allocations, real calls and natural returns remain explicit. The fixture
uses the existing 80-byte context, 572-byte observer, 192-byte frame with a
160-byte prefix and 64 KiB RAM observation. It introduces no storage profile.

## Implicit word lookup and byte history

Caller 3B498 combines unsigned word products with separate shifts by9 and11
and two unsigned FFFF caps. It publishes the resulting word at1E62. For a
result below3C00, instruction3B4EE loads literal3B684=00015042 and uses the
result multiplied by4 as its coordinate. The coordinate is0..EFFC and reads
16 words at15042..15062. For a result at or above3C00, instruction3B4FA loads
literal3B688=00015022 and subtracts3C00. The coordinate is0..C3FF and reads
14 words at15022..1503E. These two physical ranges are disjoint. The four
bytes at1503E..15042 are immutable, unread and outside controlled calibration.
No continuous union, reversed literal assignment or artificial overlap is used.

The real263F4 path tail-jumps to26A64. Twelve shift/rotate steps retain the
integer index and the exact fraction. It always reads the two actual unsigned
word operands before the real26740 interpolation. Both caller coordinate
ranges are belowF000. The generic endpoint instructions are outside this
specific caller path; the complete rugged_gerbil_paths original retains its
independent generic endpoint obligations. The caller publishes the high byte
of the lookup at1170, subtracts the saved unsigned old byte and stores the low
word of that wrapped delta at1138. The full R0 return is retained separately.

## Signed word composition

Caller41DB6 has independent admission flags at bytes2465 and2468. Its disabled
path returns FFFFFF80 and stores byte80 at2315. Its admitted path adds unsigned
word1752, four times byte1765, byte1763 and byte1F62. The divisor is0..67065.
The numerator is the actual signed word2266 scaled by128 in its raw32-bit
carrier. A zero divisor selects a caller-local sentinel from the numerator
sign without entering the divider or changing its fault word. Nonzero values
execute real21BBC, add128 and retain separate signed zero and255 caps.
The full positive-word and large-positive-divisor instruction paths remain
mandatory. An independently composed quotient does not invent DIV1 remainder
R1 or Q; complete actual helper input and return state remains bound to the
independent instruction trace.

## Complete timing compositor

Caller4BDC2 retains both complete modes and all signed and unsigned byte
operands. The main mode uses the smaller of unsigned words28B8/28BA, a
separate41AB admission bit and raw ROM threshold9012. The admitted path calls
real26474 over byte curve11F02 and eight raw byte knots at11EEA, publishing
134C. The nine physical curve bytes include the endpoint neighbor read.

Instruction4BE48 saves word1024 at localSP+2. The real26270 surface wrapper
reads that carrier as a complete local32-bit word at26286 and then retains its
low halfword for the inner coordinate. The untouched upper halfword is part
of the exact observed frame. Outer coordinate10CA, eight-word axes1461A/1464A
and the full64-word surfaceC50E feed the actual26984/26C78 and26848/26740
instruction paths. Every saved axis offset, fraction, table pointer and PR
remains explicit. Raw axes permit duplicates and nonmonotonic values; the
backward scan selects the actual rightmost qualifying knot. Only an actual
interior bracket supplies a positive divisor. The zero-fraction path retains
the signed MOV.W carrier until the caller's real EXTU.W instruction.

The caller caps the surface value at255 and publishes1348. It multiplies
unsigned word1900 by the actual byte results in32-bit carriers, calls the
complete real unsigned21CE0 large-divisor path with500000, caps at255 and
actually writes byte134A at4BE92. The original reader claim for RAM134A is
not selected for withdrawal and remains open; this full execution includes
its real write. The rest of the main and alternate modes retain byte12D4,
the24D1 bit update and signed8 saturation at1830. Unwritten lookup preimages
are preserved on bypass paths, and their unchanged bytes supply no computed
alternative.

## Biased product and conditional byte curve

Caller659AE subtracts16384 from unsigned word18E4, multiplies the raw32-bit
carrier by byte87EE and adds127 only to a negative product. Real224F8 executes
all seven arithmetic shifts. The caller adds16384 and applies its upper cap.
Unsigned word2408 plus signed word18CA, a wrapped product, the conditional
3FFF adjustment, two SHLL operations, self-SUBC, ROTCL and XTRCT retain the
exact signed carrier and carry/borrow state. The intermediate result is saved
and later read from the complete local frame.

Byte15EB and bit20 of2485 independently select the curve path or weight256.
The admitted path derives its raw byte coordinate from word22E8 and calls
real26474 over curve1245A and eight byte knots at11A55. Its ninth physical
neighbor byte is retained. The weight is256 minus the actual unsigned lookup
byte. The final raw product, optional255 adjustment and SHLR8/SWAP.W/EXTS.B/
XTRCT sequence retain the real arithmetic shift. Separate signed16 lower and
upper caps publish word18CC. Independent raw product, weight-bypass and clamp
input cross-cases preserve both actual saturation paths.

## Complete physical and native boundaries

The 44 two-sided conditions require both feasible outcomes. The 7 fixed branch premises
retain the caller's nonzero signed divisor, its nonnegative sign, fixed500000
unsigned divisor, implicit coordinate belowF000, word lookup mode and positive
axis bracket divisor. Only the corresponding88 instructions outside these
actual caller premises are excluded from the876-instruction closure. Full
timing_division_paths, rugged_gerbil_paths, register_only_helper_paths and
division_callees_paths originals remain mandatory from the identical COPY
primary, with every existing complete helper/native/TEST obligation intact.
No real call is replaced by a quotient, lookup value or stock-function stub.

Complete actual initial CPU, every intermediate CPU/SR transition, actual
post-delay helper input, natural return, RAM and ordered frame state are
mandatory. Independent equations retain known returned registers and special
registers. Every physical operand retains its site, direction, exact address,
width, register, domain and bytes. Terminal equality cannot replace any saved
argument, intermediate frame read, real instruction or post-delay lineage.
Selected datum absence uses the exact physical interval, independently of its
domain label. Actual literals, curve cells, value arguments and neighboring
ownership grant no selected reader identity or reverse fact donation.

All eight selected originals are readers with empty roles. Their exact props,
including reverse clauses, remain in their full original records. Their
withdrawal removes six exact matching selectors. Shared complex-condor,
garrulous-civet and idle_ignition_timing postimages remove one additional exact
reader and one matching selector each. Complete prior79 records and47 functions
retain full prefix reconstruction. Every preceding complete SHA and native
type, unknown type, evidence position, original TEST, ledger presence/absence
and proof scope remains exact. Complete current postimages have separate
identity pins. The three writer exceptions and eighteen indexed_by originals
retain their exact individual identities. No replacement relation is created.

Actual fixed-other alternatives require changed actual R0 or publication bytes
with every other complete CPU/frame/RAM/calibration/instruction preimage fixed.
Input matrices, generated drivers and private headers contain no expected
outputs. The135 prior domain sources retain134 byte-identical sources and the
existing two-site gated spelling exception with complete current/legacy hashes.
Twenty-nine independent components require one complete original COPY primary.
The ordinary registry contains thirteen families and forty-seven capture bindings.
The twenty-first standard source-only adapter retains the preceding twenty adapters
and all forty generated output identities. Its marker is
VQ_SH_ELF_MIXED_CURVE_CALLER_WITHDRAWAL.

Full actual-original, controlled arithmetic, signed/unsigned helper, saved-frame,
physical, CPU/SR/RAM, post-delay call, natural-return, native/prior/type/role/TEST/
ledger/scope/review and published-count refusal sources are mandatory. Source
preparation grants no executable acceptance, native geometry, scale, units,
natural caller interpretation, hardware qualification or publication.

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
remain mandatory. The joint total includes 113 datum-end selectors and
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
identical primary. The joint selector total contains 113 datum-end and
8 function-end removals.

## Joint paired normalization boundary

The joint descriptor contains129 exact access originals:119 readers and ten
individually pinned writers,98 complete datum owners,70 complete functions and
121 matching ledger selectors. These contain113 datum-end selectors and
8 function-end selectors. Twenty-nine independent components require one
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
