# JK08A state-ratio and byte-transition caller withdrawals

Natural callers 64CB2 and BDC66 and their exact real helper closure contain
927 stock instructions, 1854 code bytes and 11 code spans. The actual caller
closure requires 828 feasible instructions. The descriptor binds 91 literal spans,
30 pointer aliases, 45 complete RAM fields, 30 configuration fields,
107 complete calibration spans, 85 raw input fields and 19 reused helper sources.
The joint descriptor contains 123 exact access originals: 113 readers and ten
individually pinned writers, 94 complete owners, 66 complete functions and
115 matching ledger selectors. All 123 exact normal unlink operations are mandatory.
The selected unsupported originals are:

| Datum | Natural function | Exact unsupported original |
|---|---|---|
| `7mfk:0000ab5a` | `7mfk:000bdc66` | `732688d3434fc5a9a865a6cebd20539bcfc8910a4081e9b969e2acd61d7bd78d` |
| `7mfk:0000b43a` | `7mfk:000bdc66` | `f73ed3184f14337902a9cf59ecad78ad4758f406cf517eb3051d29b6c51ad816` |
| `7mfk:0000b53a` | `7mfk:000bdc66` | `2e5256f30e8ea2c75bbf968f4a83d03fde44859214cb1f1891cf7a8148674f31` |
| `7mfk:0000b5fa` | `7mfk:00064cb2` | `0eb7a55d3774f6a93694313064815dcfa169939e114231fe1b262f249e4e7e81` |
| `7mfk:00011fe6` | `7mfk:00064cb2` | `b302d7d9f9f92e555d671576982f93b50d101da12e7bd9d8c3756a1939d516ae` |
| `7mfk:000122f2` | `7mfk:000bdc66` | `156e43c13f7bac66de494bd9181c94497ad05da8619c9987c1ccb816a8577ca7` |
| `7mfk:00012b32` | `7mfk:00064cb2` | `4ebd4423d2ab59540c501b6622cb53a52163bda63ba24c092463de7f4d67fef9` |
| `7mfk:00012b52` | `7mfk:00064cb2` | `c836c14a4677ec716ae2b0a170eed751e0d6ee2f05b0edf5e78d5b156f56cd9c` |

## Complete callers and physical input closure

Caller 64CB2 retains 64CB2..64DC4, 64E00..64ED4 and 64EE2..64FE2.
Caller BDC66 retains BDC66..BDCFA and BDD80..BDED8. The three intervening
literal holes remain data. All natural prologues, local frame values, branches,
delay slots, helper arguments, returns and epilogues remain explicit. Exactly
30 MOV.L native RAM pointers relocate to the existing 64 KiB alias domain.
No MOV.W pointer alias or alternate observer profile is introduced. The existing
80-byte context, 572-byte observer and 192-byte frame with 160-byte prefix remain
mandatory. Initial and final complete RAM, CPU, SR, frame and calibration images
remain bound to the actual observation.

## Signed and unsigned state ratios

Configuration byte 870C and the independent RAM flag combinations choose the
primary or alternate ratio paths. The primary path updates flag 40 of 24A3 and
flag 01 of 246A. The divisor at 240E is a real sign-extended word. Zero bypasses
the division and publishes zero without a fault-helper entry. A nonzero divisor
and the sign-extended ROM word 8EA6 form a signed difference. The difference is
clamped to the signed 16 interval before the actual 32-bit left shift by 16.
The raw shifted word enters real 21BBC with the signed-word divisor.

Both divisor signs and both short/long quotient paths remain explicit. The real
DIV0S sign carrier is numerator-MSB XOR divisor-MSB, including zero numerator
with a negative divisor. Negative-divisor normalization and the exact sign
restoration instructions remain reachable. The signed quotient is interpreted
after its real 32-bit wrap, then independently floored at zero and capped at FFFF.
INT_MIN divided by minus one therefore retains its raw 80000000 result before
the caller's signed floor. A widened positive integer cannot replace that word.

The remaining primary path subtracts unsigned ROM word 906C with a zero floor.
The complete alternate body retains the 1082/108A threshold, the independent
246D/246A/2454/2450/2453/244F gates, and both configuration-selected byte inputs.
The 3373-based target is scaled by 256;the ramp retains its independent 13DE
addition, FFFF cap and target minimum. Exact 1770/176A/1774/1868 transfers and
every conditional publication remain distinct.

The variable unsigned-ratio path retains the minimum of 1774 and 1770 and the
complete sum of 1772 with unsigned ROM word 9456. Both actual comparisons must
establish a positive difference before real 21CE0 receives its divisor. The
divisor is bounded to 1..65535. The numerator is the real 32-bit product of the
positive difference and 1868. Exact short/long division, FFFF cap, 13DC decay,
the saved local flag byte and saved native pointer remain explicit. All known
returned registers and special registers are independent of the final stores.

## Byte transition, counter and saved candidate

The 8B34/8B42 special path retains its status gate and the unchanged RAM path
when 10E4 mask 08 is clear. EXTU.W bounds the 1000 word before its two arithmetic
right shifts and 255 cap. Both CMP/PZ branches are therefore fixed taken.
The alternate special path reads either signed ROM byte 851D or native byte 558A.

The main body retains every 246B/248B/41FA gate. ROM bytes 8D2D and 8D2E are
independent raw high and low thresholds. The sorted interior branch requires
low<coordinate<=high. The unsigned 1C5C/1C5E endpoint difference is a signed 32
carrier, its product enters real 21BBC, and the saved unsigned low endpoint is
added after truncation toward zero. This convex byte result is in 0..255, so the
upper-overflow branch at BDDDA is fixed fallthrough. Reversed or equal thresholds
retain their actual endpoint-selection path instead of a sorted-axis premise.

The complete candidate is saved at local SP and published separately to 1BEE.
The 24A7/previous 2326/1553/247B/1A1E gates and 25EE counter select a saved threshold,
the previous byte, or the previous byte plus one. With a zero counter, the
incremented candidate remains in the frame while the real curve call updates
1A1E and 25EE. Its return cannot replace the separate saved 2326 candidate.
The optional sign-extended 1704 byte is added to that candidate with independent
upper 255 and zero floors before the final byte 2326 publication.

## Exact fixed byte lookup and complete helper originals

The first physical byte curve is 12EFE..12F06 and the second is 12F06..12F0E.
Each has exactly eight independently controlled bytes. They are distinct,
contiguous and nonoverlapping. Configuration 8616 selects the first curve with
the actual unsigned 2772-byte times 32 divided by 20 and capped at 255, or the
second curve with unsigned 106F as coordinate.

The complete 26370 entry loads threshold 00E0 from 26382. Coordinates below 224
take the exact jump at 2637A and its real delay slot clearingR3, entering 26A80.
Only the actual byte-mode spans 26A80..26A9C and 26AAA..26ABA belong to this
closure. The fixed branch at 26A9A takes the byte path. The generic 26A60 entry
and its word mode are not admitted by this caller. The real 26740 interpolation
retains direction-dependent truncation, MACL preservation and its saved first
byte. Coordinates 224..255 return the sign-extended endpoint byte from the
real RTS delay slot 26380. Byte stores truncate that word;the helper return
and scratch state retain its complete sign extension.

The 76 two-sided conditions require both feasible outcomes. The 8 fixed branch premises
retain the actual nonzero/signed-word or positive unsigned divisors, the fixed
byte mode, the two EXTU.W signs and the convex transition cap. Exactly 99
instructions outside the actual caller premises are excluded from the 828-site
closure. Full division_callees_paths and byte_curve_caller_withdrawal_paths
remain mandatory from the identical COPY primary. The complete original standard
implicit-byte marker and its exact fixture/harness sources remain mandatory.
Their full generic division and lookup obligations are not narrowed to these
callers. No quotient, lookup or return stub is used.

## Physical, causal and native boundaries

Every actual initial/intermediate/helper-post-delay/return CPU state remains
continuous. Ordered physical operands retain exact site, direction, address,
width, register, domain and bytes. Complete frame reads and writes bind the
endpoint copies, flag byte, pointer and separate saved candidate. Unknown DIV1
R1/Q values are not invented by scalar summaries;their complete actual state
remains independently reconstructed from instruction bytes.

Fixed-other alternatives require changed actual R0 or changed final bytes at
a common actual computed RAM publication. Only real reconstructed RAM writes
supply publication locations and actual final RAM supplies their values. Any
publication overlapping the controlled RAM input is excluded. Input echoes,
unchanged common values or a changed write-set alone cannot establish an
alternative. Every other complete input, frame, CPU and bound image remains fixed.

All eight selected originals are readers with empty roles. The first three
retain their exact identity-plus-scale supports arrays and reverse clauses.
The other five retain identity support. Eleven exact matching ledger selectors
are removed from eight additional complete owners. No owner is shared with the
preceding 92-reference set. Complete prior 92 records, current postimages and 53
functions retain their direct digests and every preceding prefix reconstruction.
Types, unknown types, evidence positions, original TEST, ledger presence/absence
and proof scopes remain exact. The three writer exceptions and eighteen
indexed_by originals retain their individual identities. No reverse fact,
owning replacement, native geometry, scale, units, caller or hardware admission is
created. The generic 26370 RAM11B2 claim remains unselected.

The 153 prior domain sources retain 152 byte-identical sources and the exact
existing two-site gated spelling exception with complete current/legacy hashes.
Twenty-seven independent components require one complete original COPY primary.
The registry contains thirteen families and forty-seven capture bindings.
The twenty-third standard source-only adapter retains the preceding twenty-two adapters
and all forty-four generated output identities. Its marker is
VQ_SH_ELF_STATE_RATIO_CALLER_WITHDRAWAL.

Full actual-original, controlled arithmetic, negative and zero divisor, raw word
wrap, signed endpoint, candidate/counter/frame, physical CPU/SR/call/return,
computed-publication/input-echo/write-set, native/prior/type/role/TEST/ledger/
scope/review and published-count refusal sources are mandatory. Source
preparation grants no executable acceptance or publication.

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
remain mandatory. The joint total includes 108 datum-end selectors and
7 function-end selectors. Every previous family/helper/native/TEST original
remains mandatory from the identical primary.

The complete threshold-window reader component is defined by
`defs/JK08A.threshold-window-reader-withdrawal-paths.md`. Three exact additional
reader removals compose with the preceding paired writer postimages of the
same three datum owners. Full prior 112 records reconstruct exactly; all
58 complete prior function records, including both exact function postimages,
remain unchanged. The full raw coordinate window, two real signed divisions,
ordered local byte/dword carriers and actual boolean return remain bound.
All previous family/helper/native/TEST originals remain mandatory from the
identical primary. The joint selector total contains 108 datum-end and
5 function-end removals.

## Joint paired normalization boundary

The joint descriptor contains123 exact access originals:113 readers and ten
individually pinned writers,94 complete datum owners,66 complete functions and
115 matching ledger selectors. These contain108 datum-end selectors and
7 function-end selectors. Twenty-seven independent components require one
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
