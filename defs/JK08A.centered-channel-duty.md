# Centered channel quantities and indexed duty

The source binds 816 stock instructions in 2 actual entry paths and 12 spans,
53 literal pools, 14 four-byte RAM pointer aliases and 65 calibration spans.
The complete 000BE5BC producer has 254 instructions; the complete 000BE814
consumer has 107 instructions. The source includes 10 stock entry paths and
9 raw ROM controls. Both phases use the existing 80-byte context,
572-byte observer and 192-byte frame. Each phase has 20 independent context fields.
All published counts read the executed descriptor.

The producer retains its complete low/high override paths controlled by
ROM8[00008615], FFFF2326 and the real ROM thresholds, latch FFFF248E.bit6,
counter FFFF2608 and override value FFFF1A59. Override sets FFFF24A7.bit0
and preserves both incoming composite channel words. The ordinary path
clears those bits and preconditions independent raw words FFFF1AFC and
FFFF1B00. Each subtracts 0x800000 and shifts left 7 with exact 32-bit wrap
before the real signed 00021BBC division by ROM8[00008DD8]. The signed
wrapped quotient plus 0x800000 saturates to 0..00FFFFFF and publishes
FFFF16E8 or FFFF16EC. Zero divisors retain the actual FFFF9818 fault stores.

ROM8[00008616].bit0 selects both curve families. The stock mode byte is 1,
selecting explicit curves 00012E82 and 00012E8A with the shared 8-byte axis
00011BDB through complete 00026474/00026944/00026C78 helpers. The rightmost
qualifying knot rule retains unsorted, equal and boundary axis inputs.
Each curve has 8 active cells and 9 physical bytes because the byte
accessor reads both neighboring map bytes even when the endpoint fraction
is zero. Their shared 00012E8A byte is bound once in a 17-byte combined
span. The zero fraction does not remove that actual physical neighbor read.

Controlled bit-clear mode uses the two 8-byte implicit curves 00012E72 and
00012E7A at the byte coordinate FFFF106F through complete 00026370,
00026A80 and 00026740 paths. Both complete families, natural delayed
calls and directed interpolation remain mandatory. The first lookup byte
publishes FFFF1A7B and the second FFFF1A7C. Each byte x forms the actual
composite clamp(prior preconditioned word + (x-128)*65536,0,00FFFFFF),
published at FFFF1A9C or FFFF1AA0. The implicit table association is
conditional; it does not state that this family is stock-active.

The consumer takes the low byte of its independent entry R4 as channel.
It reads the actual word at FFFF1A9C + 4*channel and publishes one byte at
FFFF2440 + channel. The raw FFFF28C2 mask can force 255; the full enable
path through FFFF246B.bit6, FFFF248B.bit1 and FFFF41FA.bit0 can force zero.
FFFF24A7.bit0 selects FFFF1A59 override. The calculated path executes both
00021CE0 divisions using the actual FFFF1108 byte, the word high half and
middle byte, exact rounding and the final 255 cap. Both zero-divisor fault
writes remain visible. The actual store is 000BE8DC, including the full
32-bit -1 register in its forced-maximum path. Channel 1 writes FFFF2441.

Each pair carries the complete 65536-byte RAM after the producer into the
consumer without reseeding. All calibration and bound code/pool bytes
remain equal between phases. Both independent complete contexts, full
CPU/register/SR state, real division M/Q/T updates, frame bytes, SP/PR and
the producer R10-R14 and consumer R13/MACL/GBR saved words remain bound.
Both natural RTS-delay full register restores remain mandatory. No
instruction under test, helper or return is replaced by a semantic stub.

Separate wide equations compute every RAM publication and ordered physical
operand. All 16 implicit cells require held-other alternatives that change
the actual composite word and actual duty in their corresponding channel
with all other complete inputs fixed. A supplied intermediate word, input
echo, detached context or matching output bytes cannot replace that path.
The complete existing byte-factor and division originals remain mandatory
from the same primary.

Two exact proof appends retain the table quantity reader for channel 0
and the FFFF2441 writer for channel 1. The full native owners and both
functions preserve all summaries, units, scales, editor properties, links,
symbols and ledger/evidence/TEST positions. The table semantic width and
signedness stay unset; the native writer keeps width 8 and unset signedness.
No native geometry, scale, units, scheduling or hardware admission follows.

Original reader: a69bc8909b529103b95aee0b5311f2066d0b1e3f6e42130b5cfc7444781a10e2.
Original writer: 426553c268981befe38983973d516cf5698b607b5465df9fe36804564c4a3e92.
