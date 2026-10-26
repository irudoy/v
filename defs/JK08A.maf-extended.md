# JK08A MAF processing, publication and bounded caller accesses

Source bindings: `JK08A.maf-extended.toml`.


The independent consumer compares reconstructed stock bytes, private
sources, pointer aliases, fixture/ELF/object identities, the actual GNU
command and terminal streams. Separate instruction-state and integer
equations bind exact memory sites and natural call arguments after their
delay slots. Every reader requires positive datum/output alternatives
with all other input bytes, registers and calibrations fixed. A producer
marker or association with an existing function grants no semantic fact.

## Compensation

Entry `0003AE8A` uses the low byte of R4 as bank 0 or 1. Bank 1 reads
FFFF101E at 0003AEAC and writes FFFF1E4A at 0003AEC0 on initialization
or at 0003AF30 on an initialized path. The initialized nonzero-denominator
path reads the unsigned 32-bit correction FFFF399C at 0003AF04.
The bank initialization bit, previous output, stock multiplier 335 and
bias 80 determine the natural branch and real numerator/denominator.
Call 0003AF20 enters the existing unsigned divider `00021CE0` with its
actual post-delay R0 and R1. A controlled zero bias covers the natural
zero-denominator alternative without changing an instruction or pointer.
The output equation retains unsigned multiplication, quotient truncation
and modulo-65536 subtraction. Sibling-bank and fault-record bytes remain
part of the full state comparison.

## Contribution

Entry `0003AF42` reads bank-1 input FFFF1DF2 at 0003AF68. The enable,
diagnostic, inhibit and latch bytes distinguish active and fallback
paths. Forced fallback writes the constant byte 3 to FFFF43CB at
0003AF82; its reader is at 0003AFAA. The active path reads the base,
delta, correction and residual references and publishes the base word,
correction word, contribution longword and residual magnitude. Actual
BT/S and BRA delay-slot stores remain part of those transfers.

The active call at 0003B154 enters `000224FA`, the six-SHAR body of the
normalized `000224F8` function. The fixture reconstructs that exact
interior helper entry and natural RTS delay slot. It supplies no stub
and makes no claim that the normalized entry executes. Separate equations
retain truncation toward zero at /8, /512 and /256, arithmetic shift at
/64, signed clamps and signed residual retention. Fallback equations
retain low-32-bit products and the two staged logical shifts.

Native semantic types are preserved: imposing-auk is signed 32-bit,
maf_correction_state_b2 is signed 16-bit, and maf_fallback_latch_b2 is
8-bit. The existing reverse-only properties of unselfish-okapi also stay
unchanged. An owning access proof grants no reverse function evidence.

## Scaling

Entry `0003C408` calls guard `00067188` and scaler `000671D8` in their
natural order. The guard conditionally reads FFFF4970 at 0006719A and
resets it to ROM default 8000 only outside its inclusive 7900..8700
bounds. Mode bit 8 bypasses that read. The scaler reads the current
coefficient at 000671E0; its actual R4 sample and R5 caller-local output
pointer follow the call delay slot. The parent reads FFFF1D64 at
0003C420 and 0003C42C and writes FFFF101E at 0003C450. The numeric
equation retains the word cap, the 03FF full-scale increment and the
final word publication. Boundaries and unsigned word edges have explicit
input cases without an assertion of live calibration reachability.

## Battery coefficient consumer

The complete natural publisher00039A9E..00039AEE uses the same unchanged
scaling assembly and real guard00067188 and scaler000671D8. Its two
additional pool spans are00039BDC,2 bytes, and00039CAC,20 bytes. Three
additional long pointer aliases relocate FFFF1E60,FFFF1D34 andFFFF1114.
All original instructions remain exact. This entry uses its natural return;
it has no added observing return or replacement helper.

Let A=uint16(RAM16[FFFF1D6E]). The publisher retains A atFFFF1FC4 and
stores B=uint8(A>>2) atFFFF1FC6. Mode bit3 atFFFF4252 bypasses the guard.
Otherwise the guard retains coefficient K=RAM16[FFFF4970] only in the
inclusive7900..8700 range and resets it to ROM16[000092BE]=8000 outside
that range. The real scaler receives unsigned B in R4 and the actual
caller-local output pointer in delay slot00039ACC. Its result is
S=min(65535,floor(K*B/32768)); the publisher stores min(255,S) atFFFF1188.
The byte input keeps S below510, so the scaler word-cap taken path has no
execution claim from this caller. There is no raw-full-scale increment.

Exact physical order binds the source word, raw and byte staging stores,
mode read, conditional guard read/reset at0006719A/000671BC, staged byte
reload, current coefficient read at000671E0 and final byte store00039AE2.
The reset is visible to the scaler. Calls00039ABC/00039ACA, post-delay
R4/R5, real SP/PR/GBR, helper returns and natural publisher return retain
their complete state. Terminal R0=74, restored GBR and preserved MACH/MACL
are independently compared. Both outcomes of the caller's byte-cap branch
and its three actual guard branches are required within this entry.

Explicit word-wrap, byte-cap255/256, guard-bound, mode, coefficient,
SR/M/Q/T and context inputs join the same complete raw component.
Positive coefficient alternatives vary only FFFF4970 and must change
the actual output byte with all other RAM, registers, frame, SP,
continuation, ABI, SR and calibrations fixed. The original unsigned16
coefficient type remains unchanged. This access proof supplies no voltage
conversion, physical acquisition, live bypass state, units, scale,
scheduling or hardware admission.

## Bounded dual-bank callers

The window `0003A91A`..`0003A922` belongs to normalized parent
`0003A904`. Its two BSR instructions call `0003AE8A` in bank order 0, 1.
The incoming premises are R12=0, R13=1 and relocated R14=01001E1C.
The actual post-delay R4 at each call must equal its bank. Both unsigned
words FFFF101C and FFFF101E are read at callee site 0003AEAC.
The separate equations compose both compensation calls over their actual
intermediate RAM, preserving initialization bits, previous outputs and
any nested unsigned division arguments. Each input has positive output
alternatives with the other bank, complete context and calibrations fixed.

The window `0003C3B6`..`0003C3BE` belongs to normalized parent
`0003C3AC`. It calls `0003C408` with bank arguments 0 and 1 in its
delay slots. Each bank executes the real guard and scaler in order.
The first bank's coefficient reset remains visible to the second bank;
the consumer compares both physical word stores at 0003C450 to
FFFF101C and FFFF101E. Nested sample arguments and caller-local output
pointers are part of the complete instruction-state comparison.

At the two exclusive window ends, the fixture installs an explicit
observing return from `publication_inhibit_snapshot_return.s`. Each
return is separately assembled at its actual address and must equal
57F6472A000B0009: load PR through scratch R7 from SP+24, RTS, NOP.
These bytes are outside every tested stock span. Reconstruction, private
source, fixture identity, full frame and terminal PR/R7 remain mandatory.
The windows admit no full coordinator body, scheduler entry, interrupt
context, ROM lookup lineage, engineering units, array geometry or hardware
behavior. The related lookup and diagnostic-record reviews remain open.

## Banked publications

Entry `0003B224` reads the bank contribution at `0003B234`, adds the
sign-extended word FFFF1E2A and unsigned word FFFF2368 with 32-bit wrap,
then clamps the signed total at zero. Its natural RTS delay slot at
`0003B250` publishes the longword. At bank 1, imposing-auk/FFFF1DFC is
the signed 32-bit input. The separate source equations retain overflow
before the sign test and preserve the sibling bank and every input byte.

Entry `0003C45C` reads the sample at `0003C466` and stores the same word
in its RTS delay slot at `0003C46E`. Stock offset 07B2 and base FFFF128C
select FFFF1A40 for bank 1, while the source is FFFF1D64. The source's
unsigned 16-bit declaration stays fixed. The destination camouflaged-cockle
has unset width and signedness; a physical word store infers neither.
Its ledger, offset mapping and TEST evidence at index 1 remain unchanged.

## Bounded two-curve lookup

`JK08A.maf-transfer.toml` binds 0003A922..0003A94C and the real
26410/26A74/26740 wrapper and interpolation bodies. The normalized
parent is0003A904, dual_bank_maf_coordinator. Incoming R14 explicitly
selects the relocated FFFF1E1C input base. Independent unsigned ADC
words FFFF1E48 and FFFF1E4A become uint16(ADC*16) in the actual call
delay slots. The first wrapper call selects wealthy-woodlouse/00014274;
the second selects ivory-gecko/000141F4. Each curve covers128 bytes.

The wrapper clamps coordinates >=3F00 to the last word. Other inputs
select cell coordinate/256 and fraction(coordinate%256)*256. Ascending
and descending interpolation retain separate integer rounding. Interior
interpolation zero-extends the result; the upper-clamp MOV.W delay slot
sign-extends its result in R0. Stored word width and returned register
bits remain separate observations. The first result is stored at
FFFF1054; the second remains in R0 at the exclusive window boundary.
The window ends before the second word publication and correction call.

Only pool0003AB68 changes from FFFF1048 to01001048. The bound DC byte
at000086F9 preserves the existing assembly origin000086F8 and remains
observed; its correction consumer has no execution admission here. An
independently assembled SP+24/R7 observing return at0003A94C lies outside
the tested spans. Every stock instruction retains its exact bytes.

The lower-cell word load at00026AA0 binds each exact curve
root. Neighbor reads and high-end loads retain their own sites and
addresses. The word wrapper selects the word arm of the shared interpolation
body; the byte arm is outside this entry's described domain.

The exact native disposition removes the two unsupported reader relations
to wondrous-camel/0003B27E. Positive owning evidence attaches to the
already-existing reader relations to dual_bank_maf_coordinator/0003A904.
Other readers remain present. Both complete table documents retain all
six layouts, unset semantic types and existing symbol evidence. The
correction grants no universal absence-of-read claim, full coordinator,
calibration geometry, physical scale, scheduling or hardware behavior.

## Existing record-member readers

`JK08A.maf-record-readers.toml` binds the natural predicate
`00025E20`..`00025E44` and bounded coordinator window
`0003C3C6`..`0003C3DA`. The existing owner tourmaline-jackal is a
three-byte record at FFFF5A93, index0129 in the existing stride-three
record structure. Its member at offset1 is FFFF5A94. The established
record geometry remains bound to `test_ram_structure.py`; neither the
member access nor its one-byte instruction width creates a separate
symbol or assigns semantic width or signedness to the record owner.

The predicate sign-extends the low word of its explicit R4 argument.
Index0129 reads byte1 at00025E32 and returns its bit7 as R0. Full R4
upper-word alternatives retain that low-word index. SentinelFFFFFFFF
returns0 without reading record RAM. The bounded coordinator supplies
index0129 through its actual call at0003C3CA and requires incoming
GBR=01002449. Its natural predicate return reaches0003C3CE. The selected
branch executes OR.B80 in the BRA delay slot at0003C3D6 or AND.B7F at
0003C3D8, preserving status bits0..6 while assigning bit7 from the
predicate. Separate byte read and write observations bind that exact RMW.



Two owning appends share one complete record-owner postimage. Its eleven
symbol evidence items, ledger and other three access relations remain
exact. The other reader and two writer relations retain their separate
review obligations. This component admits no record producer, RPM
contributor, full coordinator, new geometry, units, scale, scheduling or
hardware behavior.

## Joint owning publication


Full publication comparison and exact COPY/injection/coherent/SID22
scope equality are required. Only a unique owning append with its full
pinned canonical relation digest is neutral to existing physical scopes.
Changed, duplicated or misplaced items retain their scope effect.
This transition adds no physical scope
normalization, separate receipt, writer command or observer ABI. Owning
proofs support access identity only. They admit no units, scale, natural
caller scheduling, hardware behavior or reachability of every controlled
input. Source preparation does not qualify a pending review.
