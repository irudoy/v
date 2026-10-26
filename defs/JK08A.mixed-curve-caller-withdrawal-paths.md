# JK08A mixed curve caller withdrawals

Source bindings: `JK08A.mixed-curve-caller-withdrawal-paths.toml`.


All four natural bodies are complete and contiguous. The exact spans are
3B498..3B520, 41DB6..41E40, 4BDC2..4BEF2 and 659AE..65A92.

## Implicit word lookup and byte history

Caller 3B498 combines unsigned word products with separate shifts by9 and11
and two unsigned FFFF caps. It publishes the resulting word at1E62. For a
result below3C00, instruction3B4EE loads literal3B684=00015042 and uses the
result multiplied by4 as its coordinate. The coordinate is0..EFFC and reads
16 words at15042..15062. For a result at or above3C00, instruction3B4FA loads
literal3B688=00015022 and subtracts3C00. The coordinate is0..C3FF and reads
14 words at15022..1503E. These two physical ranges are disjoint. The four
bytes at1503E..15042 are immutable, unread and outside controlled calibration.
No continuous union, reversed literal assignment or artificial overlap is used.

The real263F4 path tail-jumps to26A64. Twelve shift/rotate steps retain the
integer index and the exact fraction. It always reads the two actual unsigned
word operands before the real26740 interpolation. Both caller coordinate
ranges are belowF000. The generic endpoint instructions are outside this
specific caller path; the complete rugged_gerbil_paths original retains its
independent generic endpoint obligations. The caller publishes the high byte
of the lookup at1170, subtracts the saved unsigned old byte and stores the low
word of that wrapped delta at1138. The full R0 return is retained separately.

## Signed word composition

Caller41DB6 has independent admission flags at bytes2465 and2468. Its disabled
path returns FFFFFF80 and stores byte80 at2315. Its admitted path adds unsigned
word1752, four times byte1765, byte1763 and byte1F62. The divisor is0..67065.
The numerator is the actual signed word2266 scaled by128 in its raw32-bit
carrier. A zero divisor selects a caller-local sentinel from the numerator
sign without entering the divider or changing its fault word. Nonzero values
execute real21BBC, add128 and retain separate signed zero and255 caps.
The full positive-word and large-positive-divisor instruction paths remain
mandatory. An independently composed quotient does not invent DIV1 remainder
R1 or Q; complete actual helper input and return state remains bound to the
independent instruction trace.

## Complete timing compositor

Caller4BDC2 retains both complete modes and all signed and unsigned byte
operands. The main mode uses the smaller of unsigned words28B8/28BA, a
separate41AB admission bit and raw ROM threshold9012. The admitted path calls
real26474 over byte curve11F02 and eight raw byte knots at11EEA, publishing
134C. The nine physical curve bytes include the endpoint neighbor read.

Instruction4BE48 saves word1024 at localSP+2. The real26270 surface wrapper
reads that carrier as a complete local32-bit word at26286 and then retains its
low halfword for the inner coordinate. The untouched upper halfword is part
of the exact observed frame. Outer coordinate10CA, eight-word axes1461A/1464A
and the full64-word surfaceC50E feed the actual26984/26C78 and26848/26740
instruction paths. Every saved axis offset, fraction, table pointer and PR
remains explicit. Raw axes permit duplicates and nonmonotonic values; the
backward scan selects the actual rightmost qualifying knot. Only an actual
interior bracket supplies a positive divisor. The zero-fraction path retains
the signed MOV.W carrier until the caller's real EXTU.W instruction.

The caller caps the surface value at255 and publishes1348. It multiplies
unsigned word1900 by the actual byte results in32-bit carriers, calls the
complete real unsigned21CE0 large-divisor path with500000, caps at255 and
actually writes byte134A at4BE92. The original reader claim for RAM134A is
not selected for withdrawal and remains open; this full execution includes
its real write. The rest of the main and alternate modes retain byte12D4,
the24D1 bit update and signed8 saturation at1830. Unwritten lookup preimages
are preserved on bypass paths, and their unchanged bytes supply no computed
alternative.

## Biased product and conditional byte curve

Caller659AE subtracts16384 from unsigned word18E4, multiplies the raw32-bit
carrier by byte87EE and adds127 only to a negative product. Real224F8 executes
all seven arithmetic shifts. The caller adds16384 and applies its upper cap.
Unsigned word2408 plus signed word18CA, a wrapped product, the conditional
3FFF adjustment, two SHLL operations, self-SUBC, ROTCL and XTRCT retain the
exact signed carrier and carry/borrow state. The intermediate result is saved
and later read from the complete local frame.

Byte15EB and bit20 of2485 independently select the curve path or weight256.
The admitted path derives its raw byte coordinate from word22E8 and calls
real26474 over curve1245A and eight byte knots at11A55. Its ninth physical
neighbor byte is retained. The weight is256 minus the actual unsigned lookup
byte. The final raw product, optional255 adjustment and SHLR8/SWAP.W/EXTS.B/
XTRCT sequence retain the real arithmetic shift. Separate signed16 lower and
upper caps publish word18CC. Independent raw product, weight-bypass and clamp
input cross-cases preserve both actual saturation paths.
