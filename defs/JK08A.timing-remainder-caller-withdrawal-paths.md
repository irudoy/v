# JK08A timing and remainder caller withdrawals

Source bindings: `JK08A.timing-remainder-caller-withdrawal-paths.toml`.


The complete 4D99C body consists of 4D99C..4DAA4 and 4DAA8..4DB9C. Its
four-byte literal hole remains data. The complete 521A8 body is contiguous
through 52292.

## Complete timing history and correction

Caller 4D99C independently reads the configuration flag at 8710 and the RAM
flags at 24C5/24CB. Actual signed-byte negation, signed word differences and
separate comparisons publish words 11D6 and 11D8. A signed MOV.B carrier is
not replaced by an unsigned byte or an ideal widened arithmetic expression.

Configuration byte 8290 and the separate mask01/mask02 controls at 24C2
govern counter reset, flag40 of 24C0 and byte 25FC. The history comparison
uses the complete signed32 carrier at 1FF8 and the actual sign-extended byte
229D. A step first takes EXTS.W of the saved history and then adds or subtracts
one before the full32-bit store. For history 7FFFFFFF, the decreasing path
stores FFFFFFFE. For history 80000000, the increasing path stores 00000001.
The counter reload, original equality branch and all intermediate publications
remain distinct from the final correction byte.

The admitted curve path calls real 264CC. Its JSR at 264D6 executes
`mov #0xe,r4` at delay slot 264D8. This selects eight word knots at
13C48..13C58 and nine physical words at 147DA..147EC. Eight words carry
interpolated values; the ninth retains the actual neighbor read at the final
knot. The real 26984 backward scan permits raw duplicate and nonmonotonic
knots and uses only its actual positive bracket for 26C78. Exact 26740
interpolation preserves MACL and the complete saved frame.

The caller actually writes the lookup word to RAM 2000 at 4DA90. Its original
reader claim remains unselected and open. Mask20 of 2459 selects raw ROM byte
8A3C or 8A3D. The real unsigned 21CE0 call divides the unsigned word/byte
product by100. Its separate FFFF cap publishes word 1FF6. Actual history,
limited and fallback paths retain the signed byte at 2356, signed word 11D6,
byte 2378 and the exact lower/upper signed8 caps before publishing 12D6.
The bypass path retains the sign-extended MOV.B value directly; its comparison
against127 cannot take the upper-overflow path. The full R0 return is4A.

## Complete transformed-pulse quotient and remainder

Mask40 of 4184 selects unsigned word 10CA or 11BC. The multiply-by16 and
multiply-byC49B operations retain their real32-bit product wrap before SHLR16.
Six complete words at 23D4..23E0 and the separate word 241C supply the actual
maximum. Its product with the transformed carrier and the unsigned byte cap
retain their exact integer boundaries.

The raw word at 192E, twice the capped value and the real shifts form a
nonnegative numerator. The caller saves its complete32-bit value at localSP.
Mask20 of 24C9 optionally subtracts unsigned ROM byte 83EA with a zero floor
and writes the same saved location. Real 21BBC receives divisor120 and that
complete numerator. The quotient is separately saved at localSP+4. The caller
then reads the complete original numerator from localSP and calls real 21E14
with the same divisor120. A quotient or identical terminal frame cannot replace
that reread. A zero numerator enters both real nonzero-divisor helpers and
preserves the original fault word.

The full real signed remainder body 21E14..21F38 is independently reconstructed.
Its actual short and long positive-word paths retain their restoring additions,
natural returns and complete actual CPU state. The final nonrestoring quotient
bit selects restoration through quotient parity. Independent scalar summaries
do not invent returned R1 or Q. Those fields remain bound to the complete
independent DIV1 instruction state and continuous actual helper trace.

The remainder is separately clamped to4..116 and shifted right by two before
the byte23BF store. Mask01 of 4251 selects the saved quotient or the exact
override3 before the byte23F0 store. The full R0 return retains the complete
quotient or override before byte truncation. Both saved frame locations,
post-delay inputs, real helper returns and all original ABI state remain exact.
