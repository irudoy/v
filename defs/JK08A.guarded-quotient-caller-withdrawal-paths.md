# JK08A guarded quotient caller withdrawals

Natural callers 532AE, 74B68 and 75306 and the complete real signed divider contain
511 stock instructions, 1022 code bytes and 6 code spans. The bounded caller
closure requires 505 feasible instructions. The descriptor binds 46 literal spans,
14 pointer aliases, 26 complete RAM fields, 4 scalar configuration words,
46 complete calibration spans, 40 raw input fields and 7 reused helper sources.
The joint descriptor contains 132 exact access originals: 121 readers and eleven
individually pinned writers, 100 complete owners, 73 complete functions and
124 matching ledger selectors. All 132 exact normal unlink operations are mandatory.
The selected unsupported originals are:

| Datum | Natural function | Exact unsupported original |
|---|---|---|
| `7mfk:0001198e` | `7mfk:000532ae` | `6058df3ab81fa13bb54d91f7e75c7a296e9dcd50b80d45dd2762b6d24b56837a` |
| `7mfk:000126b0` | `7mfk:000532ae` | `6c9f4250619347ff8194043c8243c7d30e4d4bb389b002b66a88bf87efd8f235` |
| `7mfk:000126b8` | `7mfk:000532ae` | `c1d274e32563d7c74891c872fa46392064637818cd6e89dee35c5598cd0d09a8` |
| `7mfk:00012a82` | `7mfk:000532ae` | `868537232a2d40bec435a486835bab723ad56022b92b2e0be29c65169deec358` |
| `7mfk:000153b0` | `7mfk:00074b68` | `d961725e5c49bea33ba3188206854a27395362e43f18d5f11d7ed583bb63eb41` |
| `7mfk:000153b8` | `7mfk:00074b68` | `6c58ca67411a67c211c802575a710fae9d7e145d195d34f9f08d4e9a9caaf8b5` |
| `7mfk:00015770` | `7mfk:00075306` | `d5899807d9addb2b878cf5d643b4dfa2a132c11e24a42ebd8bfe47950dea631d` |
| `7mfk:ffff15f8` | `7mfk:000532ae` | `1b3937e671acbb4fcf17f1915a3e236caf33f087a088b1e084202159125123b6` |

The full 532AE body consists of 532AE..533BA and 533FC..534AE. The full
75306 body consists of 75306..75344 and 7534E..75396. Both literal holes
remain data. The 74B68 body is contiguous through 74C08. All natural return
instructions, original delay slots, saved registers, special registers and SP
remain exact. No body is replaced by an interior admission window.

Caller 532AE reads actual flag bytes 230E/2485/161A and word 22E8. Their
individual branches admit a main arithmetic path or a conditional fallback.
The main path optionally subtracts unsigned ROM word 9092 from word 1426
with a zero floor. It saves the sum of unsigned word 15CE and signed word
15FE in its local frame while calling real 21BBC with dividend 7FFFFFFF
and the current unsigned word 1426 as divisor. A zero divisor executes the
actual fault store 044E at RAM 9818. The complete saved sum is read after
that call; a quotient or final frame cannot replace its input carrier.

The main comparison selects multiplication before or after the actual
signed extraction path. Raw 32-bit products retain their wrap. Negative
carriers add 3FFF before two SHLL operations, self-SUBC, ROTCL and XTRCT.
Every carry, borrow and intermediate register value remains explicit. The
multiply-first branch implies a positive saved sum, so its negative adjustment
is unreachable within this exact caller scope. The raw R0 return is a full
word and is not inferred from a desired table identity.

The fallback reads unsigned bytes 1601/15DF/1680/193D, the actual signed
byte 1660 and unsigned word 2FF0. It composes wrapped products, shifts and
the saved carrier at local SP+4. A nonpositive carrier selects zero. A positive
carrier is a real signed divisor for dividend 3FC00000; its complete incoming
word 1426 is separately saved at local SP+8. The divisor can exceed 65535.
The complete 21BBC large-divisor instruction path is retained. The comparison,
wrapped product, optional 003FFFFF adjustment, SWAP.W/EXTS.W/SHLL2/SHLR8
and final signed comparison retain their actual carriers and byte truncation.
The fallback publishes byte 1600 and updates bit 10 of byte 2485. Its zero
return does not replace these independent physical publications.

Caller 74B68 has separate gates at bytes 417E/249B/245F. Admitted paths use
byte 24D2 to select addition or subtraction of unsigned word 17F8 from word
2422. The subtraction path floors negative values at zero. The addition path
saves its complete sum and compares unsigned input word 1210 against separate
raw ROM thresholds 914E/9150. Below or at the low threshold the candidate is
zero; at or above the high threshold it is FFFF. The actual interior numerator
is (input-low)*65535 modulo 32 bits. Real 21BBC interprets that raw word as
signed. An overflowed numerator therefore produces a negative quotient; no
ideal unsigned fraction replaces it. CMP/HS against the saved sum, the later
signed cap and final word store preserve the exact mixed signedness. For
low=0, high=65535 and input=65534, the real quotient is -3 and the stored word
is FFFD. Temporary GBR and its original frame are fully restored.

Caller 75306 independently rejects zero words 19A2 and 23FC. The first
real 21BBC call divides signed word 18F2 times unsigned ROM word 944E by
the unsigned word 19A2. It clamps the signed quotient to -33554432..33554431,
scales by 64 within the actual 32-bit carrier, and performs a second real
signed call using the unsigned word 23FC. Separate signed16 saturation
publishes word 19D4 in the natural RTS delay slot. Either early zero gate
bypasses both calls and preserves the original fault word.

All zero, positive-word and actual large-positive-divisor helper paths remain
complete. Independent scalar quotients leave nonzero DIV1 remainder R1 and Q
to the full independent instruction oracle. Full actual post-delay helper-entry
state, including those fields, is bound to the exact instruction trace and its
complete CPU continuity. Known separate returned registers, special registers,
RAM, every intermediate frame word, physical operand site/mode/address/width/
register/domain/bytes and all natural controls remain mandatory. An identical
terminal frame or output cannot replace saved input or divisor lineage.

The 40 two-sided conditions require both feasible outcomes. The 3 fixed branch premises
retain positive denominators, the positive large-divisor dividend and the
positive multiply-first sum. Only two negative-denominator, two unreachable
large-negative-numerator and two impossible multiply-first negative-adjustment
instructions are excluded from this caller-feasible closure. All original
helper bytes and the complete division_callees_paths original remain mandatory
from the identical COPY primary, including its full signed/unsigned, zero,
negative and large-divisor obligations. No helper uses a stock-function stub.

All eight selected originals are readers with empty roles. Shared opal-camel
and vigilant-rat owner postimages remove only one additional exact reader and
one corresponding selector each. Complete prior71 records and 44 functions
retain full digests through exact prefix postimage reconstruction; complete
current images are separately pinned. Prior57 also uses full reconstruction
where the shared owners change its current image. Every preceding full SHA,
native type or unknown type, source, evidence position, original TEST, ledger
presence/absence and proof scope remains exact. Three writer exceptions and
eighteen indexed_by originals retain their exact individual identities.

The eight exact link removals have nine matching ledger selectors. The complete
native reconstruction preserves the additional selector rather than deriving
its count from link count. Physical interval absence binds the selected ROM
roots and RAM 15F8 with alias 010015F8 independently of domain labels. Actual
neighbor word 15FE, literal values, value arguments and neighboring ownership
grant no selected reader identity, replacement relation or reverse donation.
No native geometry, physical scale, units or caller interpretation is admitted.

Actual fixed-other output alternatives retain complete other CPU/frame/RAM,
calibration and instruction preimages. Full raw input matrices and generated
drivers contain no expected outputs. The 126 prior domain sources retain
125 byte-identical sources and the existing explicit two-site gated spelling
exception with complete current/legacy hashes. Thirty-two independent components
require one complete original COPY primary. The ordinary registry contains
thirteen families and forty-seven capture bindings. The twentieth standard
source-only adapter retains the preceding nineteen adapters and all thirty-eight
generated output identities. Its marker is VQ_SH_ELF_GUARDED_QUOTIENT_CALLER_WITHDRAWAL.

Full actual-original, controlled numerical, zero/large-helper, saved-carrier,
physical, CPU/SR/frame/RAM, post-delay call, natural-return, native/prior/type/
role/TEST/ledger/scope/review and published-count refusal sources are mandatory.
Source preparation grants no executable acceptance or publication.

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
remain mandatory. The joint total includes 116 datum-end selectors and
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
identical primary. The joint selector total contains 116 datum-end and
8 function-end removals.

## Joint paired normalization boundary

The joint descriptor contains132 exact access originals:121 readers and eleven
individually pinned writers,100 complete datum owners,73 complete functions and
124 matching ledger selectors. These contain116 datum-end selectors and
8 function-end selectors. Thirty-two independent components require one
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
