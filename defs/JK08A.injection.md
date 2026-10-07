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
