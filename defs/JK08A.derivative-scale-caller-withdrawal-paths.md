# JK08A paired derivative-scale caller withdrawals

Natural callers B78DA and B7A3C and seven real helpers contain 715 stock instructions,
1430 code bytes and 11 code spans. The caller-scoped closure requires
614 feasible instructions. The descriptor binds 53 literal spans,
3 pointer aliases, 43 physical curve words, 40 axis words,
56 complete calibration spans, 72 raw input fields and 31 reused helper sources.
The joint descriptor contains 125 exact access originals: 115 readers and ten
individually pinned writers, 95 complete owners, 67 complete functions and
117 matching ledger selectors. All 125 exact normal unlink operations are mandatory.
The selected unsupported originals are:

| Datum | Natural function | Exact unsupported original |
|---|---|---|
| `7mfk:00015bf0` | `7mfk:000b78da` | `e50bf2ae3fbd6e46ee8421e61c6d3019fcab782748a1de7f49b36fb90fdc2821` |
| `7mfk:00015c80` | `7mfk:000b7a3c` | `135b4bf6288e3b975c8a616f93fc760776bb5751356b8805576b24ec0c97ee1a` |
| `7mfk:ffff110e` | `7mfk:000b78da` | `036bd425947d6ea6b3d8f732a6427ad3e7bd555898e56beb96b30b026c1c9332` |
| `7mfk:ffff110e` | `7mfk:000b7a3c` | `32b20036c5e60a367da500146f25121094a9f11af3952e9063153cab4301788f` |
| `7mfk:ffff178e` | `7mfk:000b7a3c` | `76aa231e36017454b261a39ee19edf364ad4abb611477e3c0ca260f1e52c46b9` |
| `7mfk:ffff2733` | `7mfk:000b78da` | `92dfcb0943b8b651253776a006fba60c01487ea7b768b2dab387d69302848c14` |
| `7mfk:ffff2733` | `7mfk:000b7a3c` | `7defb8aedceeaaa17c4a43a870460907d61b5e9933bea8b136732115ab3615a3` |
| `7mfk:ffff3348` | `7mfk:000b78da` | `ec181ca2f794853e947329334c40017f426533116fd07a94ffe46dc1174b70e9` |
| `7mfk:ffff3348` | `7mfk:000b7a3c` | `9f418c7091d6acf535a07437acd5068090a8b59e50d8426db950136c98b527e3` |
| `7mfk:ffff35a0` | `7mfk:000b78da` | `9d3662e96629145aec9374547056749303b0b6295506e49ba4693a4722ef566e` |
| `7mfk:ffff35b6` | `7mfk:000b7a3c` | `453f6650c03c4604fd20fcb4c273cf86f51d642ee1161d9a552dc0c7d39cc01f` |

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

The fifth argument is an independent full 32-bit input in context word 19.
The existing 80-byte context and 572-byte observation are unchanged.
Its causal mask covers both context word 19 and frame_before[160:164].
The original raw R7 frame copy at frame_before[164:168] retains its separate
mask. An unchanged final fifth word cannot replace the three actual ordered
full-word read, low-byte write and low-byte read events.

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

All eleven selected originals are readers. Eight retain their exact indexed_by
role. The shared perky-agama and ruddy-anaconda owner postimages remove only
two additional exact readers and two matching selectors each. Complete prior
60 records and 42 functions retain full digests through exact prefix postimage
reconstruction. Current complete postimages are separately pinned; no field
is ignored and no owner-level exception is admitted. Every previous full
prefix, native type or unknown type, source, evidence index, TEST position,
ledger presence/absence and proof scope remains exact. The joint three writer
exceptions and eighteen exact indexed_by originals remain individually pinned.

Selected ROM 15BF0/15C80 and native RAM 110E/178E/2733/3348/35A0/35B6 and
their exact aliases require physical interval absence independently of domain
labels. Literal values, value arguments and neighboring ownership grant no
selected reader identity, replacement relation, reverse evidence donation,
native geometry, scale, units, caller interpretation or hardware acceptance.

The 117 prior domain sources retain 116 byte-identical sources and the existing
explicit two-site gated spelling exception with complete current/legacy hashes.
Twenty-seven independent components require one complete original COPY primary.
The ordinary registry contains thirteen families and forty-seven capture bindings.
The nineteenth standard source-only adapter retains the preceding eighteen adapters
and all thirty-six generated output identities. Its terminal marker is
VQ_SH_ELF_DERIVATIVE_SCALE_CALLER_WITHDRAWAL.

Full actual-original, controlled numerical, raw-carrier, literal-hole,
negative-constant, physical, CPU/SR/frame/RAM, post-delay helper, natural-return,
native/prior/type/role/TEST/ledger/scope and count refusal sources are mandatory.
Source preparation grants no executable acceptance or publication.

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
