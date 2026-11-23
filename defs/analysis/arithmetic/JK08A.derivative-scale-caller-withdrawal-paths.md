# JK08A paired derivative-scale caller withdrawals

Source bindings: `JK08A.derivative-scale-caller-withdrawal-paths.toml`.


The natural B78DA body consists of B78DA..B794C and B79AC..B7A3C.
The natural B7A3C body consists of B7A3C..B7AFA and B7B06..B7B98.
Both literal holes remain data. Instruction count is the sum of actual spans;
entry plus a Ghidra instruction-byte count does not define a contiguous body.
Each natural RTS and its original register-restore delay slot remain exact.

Both callers divide the full raw signed incoming R6 by 20000 through real
21BBC instructions. The low byte of R5 for B78DA or R7 for B7A3C is saved
separately in the local frame, multiplied by 50 and subtracted from that
quotient. Candidates above 30267 select 32767; candidates below -35268 select
-32768; the middle path adds 2500. EXTS.W and an explicit nonnegative floor
produce a bounded factor. A real physical gain byte scales that factor.
Products above 131070 select FFFFFFFF; other products use a logical right shift
by one. Later EXTU.W preserves the exact capped ratio carrier.

B78DA selects its gain byte at 86D2 or 86D3 from the low byte of raw R4.
Its negative numerator starts with unsigned word 9292 and gain byte 8819.
B7A3C first reads the full incoming fifth stack word, writes its unchanged
low byte at incoming SP+3 and reads that byte again. The byte shifted by eight
is the coordinate for the actual 264CC wrapper, table 14E42 and axis 13BB8.
The wrapper supplies R4=14 to 26984, binding exactly eight semantic knots
and a ninth physical table read neighbor. Gain byte 8A30 scales the factor;
the lookup word and byte 8832 supply the negative numerator.

The fifth argument is an independent full 32-bit input. Its operand follows
three actual ordered full-word read, low-byte write and low-byte read events.

The low word of raw R7 for B78DA or R4 for B7A3C is the next divisor.
A zero divisor bypasses the signed helper and explicitly selects -1 or zero
from the sign of the negative product. A nonzero divisor uses the product
times 20 modulo 32 bits as a real signed 21BBC dividend. Quotients at least
-65535 are decremented; smaller quotients select zero. The resulting low word
feeds a real 264F8 wrapper with R4=30, sixteen unsigned axis knots, seventeen
physical table words and the real 26984/26C78/26740 helpers. B78DA uses
14CCA/13B38; B7A3C uses 151F2/13BF8. A generic helper name grants no different
table extent or native geometry.

Negated second lookup values at least -255 are decremented; other values
select zero. The low byte multiplies the low-word ratio. Both callers execute
real unsigned 21CE0 instructions for division by 255. B78DA then divides the
word divisor times the low word of that quotient by 250 and stores DWORD 2F98.
B7A3C divides by 2500 and multiplies the quotient by a separately selected
gain byte before storing DWORD 3228. Its selector is min(low8(raw R5)+1,4):
mode 1 uses constant 10, mode 2 byte 8A35, mode 3 byte 8A36 and mode 4 byte
8A34. Temporary GBR points to the existing ROM domain and is fully restored.
All incoming saved registers, MACL, PR and SP retain their natural return paths.

Literal FFFF763C at B79A0 and B7C20 is -35268. Literal FFFF0001 at B7C04 is
-65535. These three exact scalar constants remain immutable and unrelocated.
Only fault pointers at 21CD8/21DC8 and the publication base at B7C18 use the
three declared native RAM aliases. No high-address heuristic expands them.

Separate equations bind unsigned backward selection without a monotonicity
premise, positive fractional division, both interpolation directions, all
caller numerical stages, known returned CPU fields, complete RAM and every
intermediate saved frame word. The scalar quotient explicitly leaves DIV1
remainder R1 and Q to the complete independent instruction oracle. Full actual
helper-entry state remains bound to the exact post-delay instruction trace,
including those fields. Complete CPU continuity, instruction bytes, physical
events, call and return paths remain mandatory independently of the separate
known-field summaries. Numerical helpers do not replace executable helper bytes.

The 31 two-sided conditions require both feasible outcomes. The 7 fixed branch premises
retain nonzero positive word divisors, positive fractional divisors and the
reached capped mode-4 dispatch. Unused zero/negative/large-divisor helper paths
remain exact source bytes and retain full independent direct-helper originals.
Full timing_denominator_paths, normalization_paths, division_callees_paths
and viridian_armadillo_paths originals are mandatory from the identical COPY
primary. Their complete previous native, TEST, helper and argument obligations
remain exact. The two-entry raw capture preserves the full B7A3C function.

Actual fixed-other alternatives bind every semantic curve cell, each complete
axis blob, selected gain/threshold byte or word, raw caller parameter and the
fifth argument. Physical last neighbors have exact byte/read obligations but
no claimed output causality. Cell masks preserve all neighboring calibration
bytes and all other CPU/frame/RAM/instruction preimages. Input matrices and
generated drivers contain no expected outputs.


Selected ROM 15BF0/15C80 and native RAM 110E/178E/2733/3348/35A0/35B6 and
their exact aliases require physical interval absence independently of domain
labels. Literal values, value arguments and neighboring ownership grant no
selected reader identity, replacement relation, reverse evidence donation,
native geometry, scale, units, caller interpretation or hardware acceptance.


Full actual-original, controlled numerical, raw-carrier, literal-hole,
negative-constant, physical, CPU/SR/frame/RAM, post-delay helper, natural-return,
native/prior/type/role/TEST/ledger/scope and count refusal sources are mandatory.
Source preparation grants no executable acceptance or publication.


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
