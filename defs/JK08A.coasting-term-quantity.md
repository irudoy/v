# Byte-table coasting quantity and rate-limited publication

The source binds 467 stock instructions in 2 actual entry paths and 9 spans,
33 literal pools, 12 four-byte RAM pointer aliases and 47 calibration spans.
The complete 0002C626 producer has 15 instructions; the complete 00047120
consumer has 287 instructions. The source includes 8 stock entry paths.
Both phases use the existing 80-byte context, 572-byte observer and
192-byte frame. Each phase has 20 independent context fields. All counts
read the executed descriptor.

The producer reads the byte coordinate FFFF1077 and evaluates the physical
8-byte curve at 000122E2 with the complete 00026370 entry. Coordinates
0..223 use directed interpolation between adjacent unsigned byte cells
with a fraction of (coordinate % 32) * 2048. Coordinates 224..255 return
cell 7. The real 00026A80 tail, full shared 00026A60 body and complete
00026740 interpolation remain bound. The producer writes the resulting
0..255 as words at FFFF1230 and FFFF126E. The second write is the natural
RTS delay slot at 0002C642.

The consumer begins at 00047120 with independent complete CPU context and
the complete 65536-byte RAM after the producer, without reseeding. It
reads the actual carried FFFF1230 word at 0004726E and 00047282 when the
coasting latch is active. The unsigned FFFF1748 word is additive. The
producer range makes the sum nonnegative, so branch 00047276 is taken
and its negative-sum arm is infeasible in this exact pair. Physical table
reads belong to the producer and its helper; the native consumer reader
states the quantity association through FFFF1230.

The entry retains the complete admission path through FFFF2458.bit5,
FFFF244F.bit2, the raw signed-byte register comparison of FFFF110E with
ROM8[000086FD], FFFF4197.bit6, the real 00025E4E fault wrapper and
00025E20 predicate, FFFF106A and ROM8[00008763]. The wrapper evaluates
the two minus-one sentinels and the actual diagnostic record indices
20,71,72,73,74,75,76,138,139,140 in order, stopping at the first active
byte-1 bit 7. The separate minus-one call in the consumer returns zero.
The wrapper sentinel branches and consumer sentinel branch keep their
exact fixed outcomes. Real diagnostic records retain both outcomes.

ROM8[0000870C].bit7 requires FFFF2466.bit7 and, with FFFF2458.bit7, selects
the corrected speed coordinate. Correction subtracts the sign-extended
ROM8[00008252] from the unsigned FFFF110E byte and clamps to 0..255.
FFFF1A7A receives that coordinate or the unchanged speed byte. The
FFFF2473.bit2 latch sets only when the complete speed, FFFF11B2,
FFFF22E4, FFFF1071 and ROM8[00008762..00008766] comparisons permit it
and FFFF24A0.bit0 is clear. Existing latch and decay states stay distinct.

An active latch caps the nonnegative carried quantity with the complete
16-byte curve at 00011FF6, evaluated at min(255,4 * FFFF1A7A) by the
real 00026388 and 00026A84 entries. Both directed interpolation outcomes,
endpoint paths and the repeated lookup remain exact. The target is
128 * min(carried quantity, curve byte). Maintenance uses the exact
FFFF11B2/FFFF22E4, FFFF2465.bit6 and raw signed-byte register speed
comparisons with ROM8[00008760] and ROM8[00008761]. Growth publishes
min(unsigned prior FFFF13EA + ROM8[000084D9], target). Maintenance
failure clears FFFF2473.bit2 and sets FFFF24A0.bit0. Decay uses the
original unsigned FFFF13EA and ROM8[000084D8], saturates at zero and
clears the decay bit at zero. Admission failure clears both bits and
publishes zero. Every path writes FFFF13EA at 00047356.

Separate wide equations bind every RAM publication and ordered physical
ROM/RAM operand. The complete independently decoded CPU trace binds
registers, special registers, SR, helper arguments, natural calls/returns,
all frame bytes, both outer saved PR words, the consumer GBR/R12/R13
words and its natural RTS-delay R12 restore. The full RAM, calibration
and bound code/pool bytes stay equal across the handoff. All 8 source
cells require held-other alternatives that change actual FFFF1230 and
actual final FFFF13EA with every other complete input fixed. Input echo,
a supplied intermediate word or matching output bytes alone is refused.
The complete existing byte-factor caller original remains mandatory
from the same primary.

Original d5e2adc6b2fb8ed85f5a63dd8dd6ba51d6093025cfdb5364142328ed1922c183
retains its reader type, structural identity claim, roles and evidence.
One exact owning proof append preserves every other native fact, editor
property, lookup/input dependency, symbol and ledger/evidence/TEST
position. The intermediate FFFF1230 owner and both complete native
functions stay fixed. Semantic width and signedness remain unset.
The separate counter-average original on the same table owner and its
pending source prerequisite remain independent. This source grants no
native table geometry, scale, units, scheduling, whole-ECU or hardware
admission.
