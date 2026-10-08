# JK08A injection start-delay

## Bounded injection start-delay publication

The natural publisher at `7mfk:000521a8` and its quotient and remainder
callees at `00021bbc` and `00021e14` bind 404 instructions, 871 bound bytes,
and 6855 literal cases. The envelope contains 808 instruction bytes and
63 data bytes. Nine high-RAM pointer aliases relocate data addresses for the
simulator; instruction bytes, numeric constants, ROM pointers, helper targets,
delay slots, and natural calls and returns remain byte-identical. The fixture
uses `boundary=False` and executes both helpers without stock-function stubs.

The selected speed R is `uint16(ffff10ca)` when
`uint8(ffff4184).bit6` is set, otherwise `uint16(ffff11bc)`. The coefficient is
`K = floor(uint32(16*R*50331)/65536)`; the first multiplication retains its
low32 wrap. P is the maximum of the six unsigned16 words at
`ffff23d4..ffff23de` and the unsigned16 floor at `ffff241c`.
The pulse fraction is `p = min(255,floor(K*P/65536))`.
With `E = uint16(ffff192e)`, the nonnegative delay is
`D0 = max(0,2*E-4*p)`. If `uint8(ffff24c9).bit5` is set,
`D = max(0,D0-ROM8[0x000083ea])`; otherwise `D = D0`.
The scalar at ROM83EA is an unsigned byte with factory value 30.

Both helpers receive D in `0..131070` and divisor 120. The byte at
`ffff23f0` receives `uint8(floor(D/120))` unless
`uint8(ffff4251).bit0` forces 3. The byte at `ffff23bf` receives
`floor(min(116,max(4,D%120))/4)`. The full quotient register and remainder
accumulator have distinct identities from the stored bytes. Negative
numerators, zero/negative/wide divisors, helper sign correction, and the main
negative-angle adjustment are identity-only within this caller domain.

The 4 arithmetic records in `injection_phase`, steps 9, 10, 11, and 12,
use only this publisher as their proof path. Their sign is `none` under the
admitted full-word and byte-store domains. Executed stock contexts give lead
`0 -> 6` for R `5333 -> 5334`, `255 -> 0` for E `15359 -> 15360`, and
`0 -> 255` for P `0 -> 6`. The first-product and quotient-byte wraps prevent
a universal direction for the lead byte. The angle byte has a separate
periodic remainder: with factory calibration 30, an executed context
stores `29 -> 1` for E `15359 -> 15360`, as D changes `30718 -> 30720`
and D%120 changes `118 -> 0`. The angle is independent of the lead
override. Upper remainder clamps 116 through 120 give the same stored
byte after floor division by 4; this equivalence states no intermediate
register or instruction identity. Address-base relations identify indexed
storage; the base owners are not extra numerical inputs. The unsigned scalar owner
`injection_start_delay_decrement/tbl` belongs to `injection_timing/block`
and states only this conditional reader. The independent reader at `4e03e`
has a separate evidence scope.

The matrix contains 5446 primary-speed and 1409 alternate-speed contexts,
4446 short-helper and 2409 long-helper paths, all 120 remainders,
5610 stock-delay contexts, and 1245 artificial delay-byte contexts.
The control cross-product has 32 cases covering all eight relevant bit
combinations, both incoming T values, and both register contexts.
All three full control-byte domains are represented. Factory calibration 30
permits only even D; odd D uses artificial odd calibration contexts.
The zero-numerator path executes in 1304 cases.

Every literal checks all fifteen GPRs, T and full SR relative to the actual
prepared SR, GBR, MACH, MACL, natural PR/SP, the immutable input context,
both result bytes, every other byte of the 64k RAM image, all 63 data bytes,
the complete frame `SP-64..SP+31`, and an independent external C ABI snapshot.
The prefix preserves MD/RB and other current nonT bits except the explicitly
cleared M/Q state. It records the actual prepared SR before guest GPR loads.
Both frame snapshots share the same origin; the exit capture starts at SP+32.
Short-path low accumulator bits and long-path save locations have independent
literal expectations.

The mandatory owner and registered-stock contracts bind these counts to the
canonical Region, header, harness loop, typed symbols, conditional relations,
and exact instruction/data bytes. The independent arithmetic evaluation uses
the existing Grammar and exact rational values. The software proof covers
this consumer and these helper domains; acquisition, full scheduler
reachability, operating cadence, physical units and calibration purpose,
and hardware behavior require their own evidence.

## Bounded injection result snapshot

The caller slice `00021314..0002131a` and its real byte-copy helper
`00022558..0002258e` bind 32 instructions, 72 bound bytes and
1700 literal cases. Entry registers are explicit: R11=00022558 and
R12=140. The two original pool words identify source `ffff23bc` and
destination `ffff2330`. The natural JSR delay slot supplies length 140.
The helper copies in ascending byte order, checks the limit after each
byte, and returns through its stock RTS and R2-restoring delay slot.
Only the two high-RAM data pointers are aliased for the simulator.

The copy places `ffff23f0 -> ffff2364` at offset 52 and
`ffff23bf -> ffff2333` at offset 3. Native `injection_phase`
steps 13 and 14 state `to = uint8(from)` through the ordered caller and
real helper. The sign is `positive` for the unsigned-byte source domain.
The 6 arithmetic records bound by the publisher and copy fixtures
comprise four publisher records and these two copies. They establish no physical scale
or upstream production claim.

The matrix contains 1024 affine caller contexts, 280 isolated-byte caller contexts,
384 direct helper contexts, and 12 successive caller contexts.
Every source position in the affine contexts takes all 256 byte values.
The isolated contexts exercise each of the 140 source positions independently.
Direct calls cover lengths 0, 1, 2, 3, 4, 5, 6, 7, 139, 140, 141 and 255,
all sixteen source/destination alignments, and both incoming T values.
Two register contexts cover both caller T values. Successive contexts
retain the preceding RAM state. A twelve-case preliminary matrix includes
the caller and every early helper exit before full execution.

Every case checks all fifteen GPRs, complete SR relative to the recorded
prepared SR, MACH, MACL, GBR, PR/SP, the immutable 76-byte input context,
the complete 96-byte frame, all 64k RAM bytes, both pool words, and an
independent external C ABI snapshot. Source and neighboring RAM bytes
remain unchanged; only the declared destination bytes receive source bytes.
The helper saves R2/R3/R4 even on its zero-length path.

The simulator boundary at `0002131c` restores PR from SP+24 using R7,
then returns outside all tested instructions. The caller's observed R7
therefore holds the boundary continuation; this is not a stock R7-preservation
claim. Direct helper calls retain incoming R7 and use the natural return.
The existing shared invocation prefix clears M/Q, sets entry T, and preserves
the other observed SR bits. Separate static bytes identify the upstream
R11 helper pool and the R12 length preparation; the executable slice begins
with explicit input registers. Complete scheduler execution, live cadence,
other copy calls, overlapping-source domains, hardware atomicity, and
hardware readiness retain separate evidence.

## Bounded injection slot construction

The bounded `00054a64..00054ac6` slice binds 50 instructions,
152 bound bytes and 8508 literal cases. Entry contexts are R2=255,
R5=ffff8510, R14=ffff4555 and GBR=ffff1ff4. Four RAM literal aliases
and the corresponding incoming base-register aliases place high RAM in
simulator memory after exact instruction identity. The original 52 pool
and order-table bytes are bound. The entry-preparation bytes at
`00054a56..00054a62` retain static identity; the prologue is not executed.
An appended RTS/NOP at `00054ac8` returns outside the stock slice.

The cylinder input c is an unsigned byte in 1..6. Two fixed stock ROM
lookups at `0002268e` and `0002269b` yield c in this domain. Counter
`ffff4555` saturates at 255. History `ffff1526` ORs `1<<(c-1)`.
Control byte `ffff8513`.bit5 selects unsigned lead `ffff2364` or constant 3.
The negative difference receives one addition of 6 before byte storage.
Cylinder 1, lead 7 and bit5 set stores 255; mathematical modulo-6 yields 5.
For a given c, lead <= c+5 makes the stored byte equal modulo-6 in 0..5.
The uniform bound lead <= 6 covers all six legal cylinder inputs.

The 2 arithmetic records at native injection_phase steps 15 and 16
bind lead and cylinder inputs to slot `ffff20b4` through the sequencer.
They use sign `none` and the exact bounded expression:

```text
F = (uint8(ffff8513)>>5)&1; L = F*uint8(ffff2364)+(1-F)*3; d = uint8(ffff11de)-1-L; to = uint8(d+6*min(1,max(0,-d)))
```

The matrix has 12 early contexts, 6144 enabled-lead contexts,
48 disabled-lead contexts, 2048 full-control-byte contexts and
256 counter-byte contexts. Enabled lead covers 0..255 for each legal c,
both incoming T values and two complete GPR variants. Control contexts
cover all 256 raw byte values, including other bits and sign extension.
Counter contexts cover every byte and both saturation branch outcomes.
EARLY_ONLY=1 executes the first twelve literals; the mandatory Region
uses EARLY_ONLY=0 and requires the complete declared count.

Each case observes all fifteen GPRs, actual prepared complete SR/T,
MACH, MACL, GBR, PR/SP, the immutable 76-byte context, all 96 frame bytes,
an independent outer C ABI, all 64k RAM bytes and every bound ROM byte.
Only counter, history and slot stores may change RAM. This slice has no
stock call, MMIO access or internal frame write. The shared invocation
prefix preserves its accepted instruction bytes and its SR preparation.

Full-byte lead values are explicit consumer contexts. Complete prologue
and tail behavior, upstream producer bounds, live scheduling, physical
cylinder identity and hardware reachability require separate evidence.
This proof does not establish that lead values above six occur in service.

## Bounded injection pending-mask selection

The accepted lookup and two selection entries bind 32 instructions,
80 bound bytes and 9216 literal cases. The direct lookup at
`00054d06..00054d0a` requires slot 0..5 and reads the six stock masks
`02 04 08 10 20 01` at `00022695`. Entry `00054bdc` supplies the
zero-lead-delta context: it clears pending byte `ffff2228`, computes the
next cursor as old cursor+1 below 5 and zero otherwise, and accepts only
a matching target slot. Acceptance stores the cursor and the looked-up
mask. Entry `00054c0e` supplies the negative-lead-delta context and clears
only the pending byte. The boundary at `00054d0c` is outside all three
stock spans; its RTS/NOP adds no sequencer semantics. One RAM literal
and incoming GBR/R14 alone use simulator RAM aliases.

The matrix contains 12 early contexts, 6144 valid-slot zero-delta contexts,
1500 invalid-slot contexts, 1024 negative-delta contexts, 24 accepted
direct lookups and 512 full-cursor extreme-invalid-slot contexts. The
zero-delta and negative-delta inputs cover complete unsigned byte domains;
direct lookup contexts keep the necessary valid table-index bound.
Earlier mode gates and earlier mode exits, positive-delta catch-up, stock
calls and MMIO are outside these spans. Native step 17 retains a separate
complete-selection question; this fixture does not assert that every
sequencer path without an accepted slot clears pending.

EARLY_ONLY=1 executes the first twelve literals; the mandatory Region uses
EARLY_ONLY=0 and requires its complete declared count. Each case observes
all fifteen GPRs, actual complete SR including T, MACH, MACL, GBR, PR/SP,
the immutable 76-byte incoming context, all 96 frame bytes, an independent
outer C ABI, all 64k RAM bytes and every bound pool byte. The unchanged
shared invocation prepares the entry and observes the return. Software
execution establishes no live reachability, physical scale or hardware
behavior outside the declared instruction entries.

## Bounded injection reciprocal splitter

The complete `00028e7c..00028e9c` helper binds 17 instructions,
36 bound bytes and 12826 literal cases. It takes a full unsigned 32-bit
input M in R4 and independent word and byte output pointers in R5/R6.
The ROM word `00028ea0` is 6554. The actual operator is
`Q=floor(uint32(6554*M)/65536)` with word Q and byte `uint8(M-10*Q)`.
There is no saturating quotient cap. Both quotient-zero branch outcomes,
the word store in its BT/S delay slot, and the natural return with MACL
restoration in its delay slot execute. No literal or instruction alias
is needed. Prepared output pointers are explicit helper contexts; this
generic fixture does not identify all callers' destinations.

For M in 0..255, Q equals floor(M/10). Larger operands can differ through
reciprocal precision and low-32-bit wrap. The early M=200000 context
executes Q=20001 and residue byte 246. The matrix contains 12 early
contexts, 2816 coarse word-period products, 9450 product-wrap seam
contexts, 512 complete unsigned-byte/T contexts and 36 raw-32-bit corners.
All byte-valued remainders contribute wrap-seam boundaries where present.

EARLY_ONLY=1 executes the first twelve literals; the mandatory Region uses
EARLY_ONLY=0 and requires its complete declared count. Each case observes
all fifteen GPRs, actual complete SR including T, MACH, MACL, GBR, PR/SP,
the immutable 76-byte incoming context, all 96 frame bytes, an independent
outer C ABI, all 64k RAM bytes and every bound pool byte. The unchanged
shared invocation prepares the entry and observes the return. Software
execution establishes no live reachability, physical scale or hardware
behavior outside the declared instruction entries.

## Bounded injection argument splitting and phase normalization

The caller at `0002b660..0002b6cc`, its complete phase normalizer at
`00028dc8..00028e7a` and its real reciprocal splitter bind 162 instructions,
350 bound bytes and 12668 literal cases. A=uint8(R4) executes in the
BT/S delay slot on both mode-bit6 outcomes. With bit6 clear, byte-domain
division by ten is exact: initial count is max(0,floor(A/10)-1), and
remainder is A%10 plus ten when the quotient is nonzero. The normalizer
reads raw position byte `ffff13b2` and writes count word `ffff13b8` and
remainder byte `ffff193b`. With bit6 set, A<120 stores count zero and
remainder A; other byte values store count one and remainder A-120.

At position 4 the normalizer maps count 4 to 3 with remainder+10, 5 to 3
with remainder+20, and 6..15 to count-2. At position 9 it maps 9 to 8
with remainder+10 and counts >=10 to count-2 with remainder+20. Other
raw position bytes map 1 to zero with remainder+10, 2 to zero with
remainder+20, 3..12 to count-2, 13 to ten with remainder+10, 14 to ten
with remainder+20, and 15..24 to count-4. Other counts are unchanged.
Byte additions keep uint8 storage while scratch GPRs retain signed
byte extension. This full raw consumer domain does not expand the
physical tooth domain.

The matrix contains 12 early contexts, 2560 normal byte/valid-position
contexts, 1536 fallback contexts, 3328 complete raw-position contexts,
1536 complete control-byte contexts, 288 upper-argument-bit contexts,
32 direct clamp contexts and 3376 direct normalizer contexts. The direct
clamp supplies entry `0002b676` to cover the signed clamp unreachable
after byte truncation. The normalizer uses its natural return. Caller
entries return through a PR restore at stack offset 24 in a boundary
at `0002b6ce`, with R11 as scratch outside the stock bytes. Three RAM
pool words alone are aliased. The prologue, source-argument dispatch,
preceding pending flag and following count decision and MMIO retain
separate evidence. Native step 18 requires composition with those
caller conditions before it gains a complete arithmetic record.

EARLY_ONLY=1 executes the first twelve literals; the mandatory Region uses
EARLY_ONLY=0 and requires its complete declared count. Each case observes
all fifteen GPRs, actual complete SR including T, MACH, MACL, GBR, PR/SP,
the immutable 76-byte incoming context, all 96 frame bytes, an independent
outer C ABI, all 64k RAM bytes and every bound pool byte. The unchanged
shared invocation prepares the entry and observes the return. Software
execution establishes no live reachability, physical scale or hardware
behavior outside the declared instruction entries.

## Bounded injection offset multiplication

The `0002b6d4..0002b6f6` multiply and its complete real reciprocal helper
bind 35 instructions, 90 bound bytes and 14118 literal cases. The caller
reads unsigned period word `ffff22bc` and remainder byte `ffff193b`.
It computes M=P*R and passes the actual word output `ffff16c2` and byte
output `ffff166c` to `00028e7c`. The word is Q and the byte is
uint8(M-10*Q). MACL contains M after the helper restores its saved input;
it does not preserve the MACL value before the caller's multiplication.

Native injection_phase step 19 has sign `none`, includes the ordered
caller and real helper, and binds the exact bounded arithmetic:

```text
M = uint16(ffff22bc)*uint8(ffff193b); to = floor(uint32(6554*M)/65536)
```

P=8192,R=4 executes Q=3277 while ordinary division gives 3276.
P=25000,R=8 executes Q=20001 and byte 246. Across full word/byte
consumer contexts the reciprocal product wraps and Q can decrease
when an operand increases. The raw residue is not limited to 0..9.
The matrix contains 12 early contexts, 3328 coarse word/byte products,
9450 wrap-seam contexts, 1280 complete-byte contexts at five word values,
and 48 word-corner contexts. Two declared RAM literals alone are aliased.
The boundary at `0002b6f8` restores PR from stack offset 24 using R11
outside all tested bytes. The preceding zero-count decision, compare
programming, physical timer units and hardware retain separate evidence.

EARLY_ONLY=1 executes the first twelve literals; the mandatory Region uses
EARLY_ONLY=0 and requires its complete declared count. Each case observes
all fifteen GPRs, actual complete SR including T, MACH, MACL, GBR, PR/SP,
the immutable 76-byte incoming context, all 96 frame bytes, an independent
outer C ABI, all 64k RAM bytes and every bound pool byte. The unchanged
shared invocation prepares the entry and observes the return. Software
execution establishes no live reachability, physical scale or hardware
behavior outside the declared instruction entries.

## Bounded injection positive-delta mask accumulation

The loop at `00054c54..00054cc6` binds 58 instructions,
138 bound bytes and 11340 literal cases. Its input N=uint8(R6) is a
prepared register context. For N=0 it leaves all RAM unchanged and writes
zero at SP+12 and SP+16. For N>0 each iteration increments the raw cursor
byte `ffff221e`, wraps a resulting byte >=6 to zero, and reads the mask
`02 04 08 10 20 01` at `00022695+cursor`. The final cursor is
`(min(old_cursor,5)+N)%6`. The accumulator ORs the next min(N,6) masks;
N>=6 produces 0x3f. It ORs that accumulator into `ffff20b5`, `ffff157e`
and `ffff16fe`, and clears its bits in `ffff1935`. Upper byte bits in the
four history values are preserved. Signed MOV.B scratch registers retain
their actual full GPR values before unsigned byte storage.

For N>0 the loop saves incoming R9 at SP and restores it, stores N at
SP+12 and stores the accumulated mask at SP+16. Other frame bytes are
held. The boundary at `00054cc8` uses an RTS/NOP outside the stock span.
The two RAM literal bases alone use simulator aliases; incoming R8 is
the stock table base `0002268e`, and incoming GBR is the declared RAM
alias of `ffff1ff4`. ROM instructions, masks and offsets are unchanged.

The matrix contains 12 early contexts, 7168 full-cursor and selected-delta
contexts with both GPR patterns and entry T values, 3072 full-delta
contexts over all six valid cursor values and two GPR patterns, 1024
independent full-byte history contexts and 64 upper-delta-bit contexts.
Every cursor byte and low delta byte occurs. N=0, loop completion,
cursor wrap, repeated complete cycles and both incoming T values execute.
The native owners describe unsigned byte storage and the exact bounded
writer. All 22 complete steps of injection_phase retain their current
bindings. The preceding mode/lead decision, later flag and duration-helper
paths, pending-mask publication, one-shot call, physical channel mapping
and hardware retain separate evidence. These raw direct contexts do not
establish service reachability or the full step-17 selection conditions.

EARLY_ONLY=1 executes the first twelve literals; the mandatory Region uses
EARLY_ONLY=0 and requires every literal. Each case observes all fifteen GPRs,
actual complete SR including T, MACH, MACL, GBR, PR/SP, the immutable
76-byte entry context, all 96 frame bytes, a separate twelve-word outer
C ABI, all 64k RAM bytes and every bound ROM pool byte. The original
shared invocation and pinned GNU tools execute the fixture.

## Bounded injection pre-call argument preparation

The mandatory `jk08a-injection-dispatch` Region reconstructs 12 instructions,
38 bound bytes and 9292 literal cases with `EARLY_ONLY=0`. It enters at
00054d0c and observes at 00054d24 before JSR to 0002b64a. The byte at
ffff221d receives uint8(R9). Bit 0 of ffff4251 selects argument 52 when set
and the complete 32-bit word at SP+8 when clear. Other flag bits are retained;
the MOV of 52 executes in the BRA delay slot. R2 holds the stock callee
address at the boundary. Further callee execution has separate evidence.

The stored-word domain includes 4*A for every byte A in 0..255, independent
upper-word contexts and both prepared T values. These are explicit entry
inputs; earlier producer and mode conditions retain their own proof. The
matrix contains 12 early cases, 4096 full-flag cases, 4096 byte-snapshot-word
cases, 1024 previous-lead cases and 64 upper-word cases. Every flag byte and
every previous lead byte is covered. The direct contexts do not establish
caller reachability or all combinations of 32-bit arguments and lead values.

The harness checks all fifteen GPRs and the actual complete SR, MACH, MACL,
GBR, PR/SP, the immutable 76-byte context, 96 frame bytes, an independent
12-word C caller ABI record, 64k RAM and every bound ROM-pool byte. R11 is
the explicit boundary scratch and equals the independently recorded driver
continuation. Fourteen other GPR results bind to the literal matrix. The
frame and RAM checks permit only the stock lead-byte write. The input flag,
saved argument, neighboring frame bytes and other RAM retain their values.

`stock_injection_dispatch_invoke.s` preserves the complete start-delay
observer after a symbol rename and two setup instructions. Those instructions
copy the explicit incoming R4 word into SP+8 before the before-frame capture.
The contract normalizes that insertion and compares the complete remaining
source with `stock_injection_start_delay_invoke.s`. Mutation checks reject
each register result, each bound byte, changed setup offset/source, missing
frame capture, changed Region boundaries and conflicting published counts.

Simulator RAM aliases affect only the declared words at 00054e8c and
00054e9c. The existing boundary stub at 00054d24 loads its continuation
from SP+24 through R11; the interval under test retains its exact ROM bytes.
The pinned GNU tools, image, runner and timeouts remain the standard gate.
The boundary precedes hardware compare and timer accesses; software proof
of argument preparation leaves hardware validation as a separate condition.

## Bounded injection count decision and saved-frame return

The mandatory `jk08a-injection-count` Region reconstructs 44 instructions,
108 bound bytes and 10252 literal cases with `EARLY_ONLY=0`. It enters at
0002b6ce, reads the stored unsigned word ffff13b8 through GBR and tests zero.
MOV.W sign-extends the scratch R0; that sign does not affect the zero test.
Count zero executes M=uint16(ffff22bc)*uint8(ffff193b), followed by the real
00028e7c reciprocal splitter: Q=floor(uint32(6554*M)/65536), word ffff16c2=Q
and byte ffff166c=uint8(M-10*Q). Observation at 0002b6f8 is before MMIO.
The reciprocal formula preserves 32-bit multiplication wrap and byte residue
truncation; exact division by ten does not describe every input context.

Nonzero count branches to the real saved-frame epilogue 0002b74a..0002b754.
It restores the explicitly staged GBR, MACL, PR, R14 and R13, including R13
in the RTS delay slot, and returns with SP+20. All RAM bytes are preserved.
The staged frame is an explicit direct-entry input. The original prologue,
validity of that frame as its product, earlier producers, actual dispatcher
invocation and complete caller composition retain separate evidence.

The matrix contains 12 early cases, 4096 count-word contexts, 4096 period-word
contexts, 1024 remainder-byte contexts and 1024 independent upper-count-byte
contexts. Both count-byte positions cover 0..255 independently; every period
low byte, remainder byte and both prepared T values are covered. These domains
do not claim all 65536 count words, a full Cartesian product or caller reachability.

The harness checks all fifteen GPRs and the actual complete SR, MACH, MACL,
GBR, actual PR/SP, the immutable 92-byte context, 96 frame bytes, an independent
12-word C caller ABI record, 64k RAM and every bound ROM-pool byte. R11 is
the declared scratch of the zero-path boundary and equals its recorded
continuation; the nonzero path preserves its incoming value. Saved GBR and
MACL differ from their incoming values, and saved R13/R14 are independently
seeded. The zero path permits only the offset word, residue byte and the real
splitter's saved-MACL frame word to change. The nonzero path permits no RAM
or frame change. The observer records actual returned SP before compensation.

`stock_injection_count_invoke.s` retains the complete start-delay observer
after normalization of symbol names, the declared frame allocation, saved-frame
setup, two return-capture sequences, actual-SP capture and continuation pointer.
Its entire normalized source equals `stock_injection_start_delay_invoke.s`.
Contracts bind every execution input by SHA-256 and reject changed registers,
saved state, every bound byte, missing reader evidence, altered chain description,
changed Region boundaries and conflicting published counts. The dispatch input
contract binds the shared invocation source including the count observer.

Simulator RAM aliases affect only the declared words at 0002b864 and 0002b874.
The standard boundary stub at 0002b6f8 reads SP+24 through R11. All instructions
under test retain their exact ROM bytes. The pinned GNU tools, image, runner
and timeouts are the standard gate. MMIO and hardware behavior have separate
validation conditions.

## Bounded injection programmer entry frame and byte flag

The mandatory `jk08a-injection-prologue` Region reconstructs 11 instructions,
28 bound bytes and 1036 literal cases with `EARLY_ONLY=0`. It enters at
0002b64a and observes at 0002b660 before the argument and mode calculations.
The five saved words are R13, R14, PR, MACL and GBR, pushed in that order;
actual SP-20 and every saved byte are observed before stack compensation.
The natural JSR continuation is saved PR. The long pool at 0002b864 loads
GBR from ffff128c. The exact word 0002b75c=84ec sign-extends to ffff84ec;
MOV.B loads that byte with sign extension, OR 0x80 sets bit 7 and MOV.B
stores the low byte. R0 retains the sign-extended byte OR 128; T is held.

The matrix covers every byte 0..255, two independent complete register
contexts and both prepared T values, plus 12 early cases. The harness checks
all fifteen GPRs, actual complete SR, MACH/MACL, loaded GBR, actual PR/SP,
the immutable 76-byte input context, 96 frame bytes, an independent 12-word
C caller ABI record, 64k RAM, all six pool bytes and sixteen low-alias bytes.
Only the alias byte's bit 7 and the five saved words may change. The complete
high-RAM test window and every neighboring low-alias byte are retained.

The declared simulator binding (0002b75c, ffff84ec, 0x7f00, 1) relocates only
the pointer's two pool bytes. Its original sign-extended target lies in the
configured MCU RAM domain. The positive signed-word alias and its extent
must fit the image, avoid all tested code, pool data and return boundaries,
and avoid repeated pool words or overlapping aliases and original RAM
extents. A simultaneous long-literal binding to the same original address
is refused. The long pointer alone maps to 0x0100128c. Every instruction
under test retains its stock bytes. Two padding bytes before the two-byte
aligned entry are outside the reconstructed code and preserve PC-relative
longword alignment. The boundary is the ordinary RTS/NOP pair.

The complete normalized observer equals the start-delay observer after the
declared allocation and actual-SP capture insertions. Every old Region's
complete declaration and simulator fixture remain exact with the empty
RAM-word binding default. The GNU image, tools, runner and timeouts are the
standard gate. Storage width is eight bits; the physical flag meaning,
following mode/delta selection, count/remainder composition, real dispatcher
invocation, whole-function return, MMIO and hardware retain separate evidence.

## Connected injection calculation and raw scheduling

Ten mandatory Regions bind 3021 instructions, 7319 bound bytes
and 194860 literal cases with EARLY_ONLY=0. Each function or bounded view
has independently reconstructed instruction bytes. The registered contracts
execute the complete opening-word publisher, pulse selector, delayed-start
programmer, one-shot, end-angle publisher, injector-event ISR and dispatcher.
Three RPM views cover word scaling, capped byte scaling and the real copy;
they do not establish whole RPM-producer execution or sample simultaneity.

The opening word uses unsigned battery B and ROM bytes Q/A:
min(65535,max(0,floor((175-B)*Q/128)+A)). The real seven-SHAR helper floors
negative products. The full byte domains have a maximum of 603, making the
upper clamp unreachable. Raw duration and voltage units remain unverified.

The selector distinguishes override, stopped, start modes 1/2/4 and running.
Start modes compare the threshold with capped opening plus ROM margin,
conditionally subtract the stopped word, then apply the selected floor.
Running takes the maximum of each snapshot word and the running floor.
Its real secondary tail clears pending corrections and scales or copies
secondary words under the independent aggregate mask and ROM control bit.

The one-shot requires explicit invocation and an enabled output byte. Any
intersection of the whole mask with inhibition or history selects opening
for every selected channel. A set start bit subtracts opening with floor0.
The capped increment is floor(800*d/256), or 1000 in diagnostic mode; addition
to the raw counter wraps modulo65536. Its chain sign is none. DSTR ORs only
bits0..5 under I15 and restores the incoming interrupt mask. Synthetic raw
register storage does not verify peripheral timing or physical actuation.

Normal end-angle equations read the state after the prefix, latch, countdown
and bias updates. They select the conditional curve, fixed override, or base
curve plus bias, then cap at209 and double. The unsigned eight-cell implicit
lookup uses step32 and last-cell clamp224. It adds or subtracts the floor of
the positive interpolation distance. Alternate and inhibited entries retain
separately executed outcomes. Synthetic curves and scalars expose branches
that stock calibration suppresses; their physical reachability is unverified.

The base path of publisher 00056bd0 executes wrapper 00026370 and linear
finisher 00026740, adds the updated unsigned byte ffff340c to the base curve
result, applies the 209-count cap, and stores the doubled word at ffff192e.

Pending-mask equations read staged state after optional trigger setup and
before lead/cursor updates. Equal lead accepts only a matching next cursor,
negative lead clears pending, and positive lead executes the actual catch-up
loop and both consumers before publishing the final slot mask. The programmer
receives 4*unsigned8[ffff2333] or52 and wraps it to uint8. Nonzero normalized
count retains offset. Zero count uses the exact wrapped remainder and the
low32 reciprocal product. Compare selection uses delta+2>q, including timer
wrap; raw status/control updates have independently checked word boundaries.
The ISR equations require an explicit invocation; hardware compare delivery
is not inferred from separate compare and raw-publication observations.

Every admitted path observes all15 GPRs, complete SR/PR/SP/MACH/MACL/GBR,
the immutable76-byte input, the C caller ABI, declared saved/local bytes,
64k RAM, all bound ROM inputs and declared alias neighbors. The combined
dispatcher and ISR compare all192 frame bytes. The pinned GNU simulator's TRAPA/RTE uses SPC/SSR
and leaves SP unchanged. It does not establish the SH-2E exception stack;
equivalent exception-stack coverage is required before hardware eligibility.
Only declared RAM and register pointer pools are relocated. Exact instruction
bytes, the original GNU image and standard timeouts remain under the gate.

The arithmetic covers fuel_pulse18/24/25/26 and
injection_phase1..8/17/18/20..22. Indexed one-shot context x[0] is the incoming
aggregate mask and x[1] is channel0..5. The raw counter's previous value is
prev. This specification fixes the meaning of lookup and staged-state
boundaries; physical units, acquisition cadence and hardware validation
require their separate evidence.
