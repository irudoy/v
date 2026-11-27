# Published event timing map result and live register consumption

The described natural entry is `0004D99C`.

Complete 0004D99C retains both ordinary and knock-related construction of
FFFF11D6 and FFFF11D8. Signed byte and word loads, ROM8[00008710].bit5,
FFFF24C5.bit5, FFFF24CB.bit2 and the actual upper byte of FFFF23C2 remain
independent raw inputs. ROM8[00008290] controls the real target/counter
logic at FFFF229D, FFFF25FC and FFFF24C0.bit6. FFFF24CC.bit1 selects the
actual bypass from signed FFFF2378 to FFFF12D6 (set bypasses recalculation,
clear admits it). Latch `0004C136` mirrors `FFFF4184.bit6` (computed START
SIGNAL, copied from `FFFF4185` at `00021090..00021092`; see
[`JK08A.start-signal-temperature-selector.md`](../runtime/JK08A.start-signal-temperature-selector.md))
into `FFFF24D2.bit1` at `0004C140..0004C152` under periodic-table task
`ROM32[00021A88] = 0004D888` (`0004D91A` via literal `0004D994`). Periodic
snapshot `00020DFE` then copies six bytes from `FFFF24CE` to `FFFF24C8` through
`00022558` at `00021348`, delivering `FFFF24D2.bit1` into `FFFF24CC.bit1`. The
startup RMW at `0002C99C..0002C9A0` ORs `0x08` and preserves bit 1.

The active path executes the complete 000264CC wrapper with the unsigned
FFFF237E coordinate. Complete 00026984 searches all eight unsigned axis
words at 00013C48 from right to left without a monotonicity assumption.
The actual bracket gives a strictly positive denominator to complete
00026C78 and a fraction below 65536. Exact knots, below-axis inputs,
above-axis inputs, duplicate knots and nonmonotonic raw knots retain
their actual natural paths.

The wrapper physically reads nine uint16 words at 000147DA. Eight words
have possible nonzero influence. At the final knot it still reads the
ninth word at 000147EA with zero fraction. Complete directed interpolation
00026740 remains bound through the real 000264EA tail. Every physical word,
including that extra endpoint read, remains in the immutable input and
physical operand stream.

The raw result is copied from R0 to R6 at 0004DA8E and published as uint16
FFFF2000 from R0 at 0004DA90. The same complete live R6 continues through
the unsigned extension at 0004DAB4 and multiplication at 0004DAB8.
FFFF2459.bit5 selects raw coefficient `ROM8[00008A3C]` when set or
`ROM8[00008A3D]` when clear (`0004DA92..0004DAB2`; both stock bytes are 100),
also published at FFFF226C. Complete 00021CE0 divides the nonnegative
product by exactly 100, and the uint16 cap publishes at FFFF1FF6 (`0004DAD4`),
while the live value in R6 feeds the subtractions at `0004DB46` and `0004DB5C`.

The final path preserves the full FFFF1FF8 counter, signed target
FFFF229D, timer FFFF25FC, sign16 one-count step, actual FFFF40E7 limit,
FFFF24C2.bit1, signed FFFF2356 and final signed-byte clamp. FFFF12D6 is
written from the complete live R6 at 0004DB8C. Equality of the full counter
and signed target clears the active slew flag before the update; an equal
counter update outcome is caller-infeasible. The bypass comparison cannot
exceed 127 because its input is already sign8. The constant-100 divider
has no zero or wide divisor path in this caller. Complete existing word
interpolation and division originals remain mandatory from the same primary.


Each of eight active table words requires held-other alternatives changing
actual FFFF2000, FFFF1FF6 and final FFFF12D6. The ninth physical word requires
zero-weight value invariance. Independent overwritten prior FFFF2000
inputs on the active path must preserve the complete exit CPU, frame and
final RAM. The prior FFFF2000 word is not physically read. Matching output
bytes or a supplied live R6 do not replace complete state and actual flow.
