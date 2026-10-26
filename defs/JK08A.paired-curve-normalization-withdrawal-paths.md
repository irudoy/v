# JK08A paired curve normalization withdrawal

Source bindings: `JK08A.paired-curve-normalization-withdrawal-paths.toml`.


## Complete natural entries and byte curve inputs

The full code spans bind 655B4..65702, 65B08..65C26, 21BBC..21CD6,
264A0..264C2, 26740..2676E, 26944..26980 and 26C78..26D0E.

The real 264A0 wrapper receives data root 11D24, axis root 1199E and a full byte
coordinate. Its 26944 scanner receives maximum byte offset 15. It scans the
16 raw axis bytes backward and selects the rightmost qualifying knot. A global
monotonicity assumption is absent. On an actual bracket path the later scanned
neighbor is greater than the coordinate, so its positive adjacent difference
is the real divisor of 26C78. All raw axis bytes remain independent inputs.

The wrapper physically reads data[index+1] before data[index]. The complete
data preimage therefore contains 17 bytes. At index15 the fraction is zero:
data16 remains an exact varied physical input without numerical causality
admission. Both interpolation directions, actual positive fractional division,
zero-fraction paths, descending scan reads and helper frame restoration remain
explicit. No fixed data value, synthetic helper result or native geometry is
substituted for the complete raw preimage.

## Separate caller arithmetic and local frame lineage

With configuration bit20 clear, both callers subtract signed 2404 and unsigned
12DF/15EA from signed 23F1, then clip negative coordinates to zero. The first
coordinate is saved as one local byte. The first real curve result is saved
as another local byte four bytes later. Both bytes have separate real reloads.
The second coordinate adds signed 11C2 for 655B4 or signed 11C1 for 65B08 and
the unsigned 12DF/15EA inputs, then clips to 0..255. The callers retain their
distinct EXTS.W and EXTU.W instructions and actual complete register states.

The first coefficient produces divisor 256-first, in 1..256. The complete
MOV.W sign-extended 18CC word multiplies 256-second before the real 21BBC signed
division. Both signs and short/long helper paths remain required. The physical
signed word is not an inferred native type. Zero, negative and large divisors
are outside this exact caller domain. The complete broader direct-divider
original remains mandatory from the identical primary. Unknown post-DIV1
register/SR fields are not fabricated; the actual trace retains them.

With configuration bit20 set, 655B4 compares the signed 11A0/119E words. Equality
copies the actual 18CE word to 18D4 without a helper. The unequal path retains
the signed 23E2 sum, negative unsigned 413F threshold and signed 2404/23F1
coordinate computation. The 65B08 alternate path subtracts signed 11A2 from
signed 23F1 before clipping and EXTU.B. Each alternate computation executes one
real curve, multiplies signed 18CC by 256-coefficient and divides by256 toward
zero through its actual negative adjustment and shift sequence.

Both functions retain final signed saturation to -32768..32767. The real word
publication sites are 656F2 at RAM18D4 and 65C16 at RAM18CE. Their returned R0
values are the fixed GBR displacements 648 and 642. Numerical alternatives
therefore require changed final bytes at a common actual computed word outside
the controlled RAM input. Complete other CPU/frame/RAM/calibration/bound
preimages stay fixed. Input echoes, unchanged common bytes and a changed
write-set alone fail. The publication, GBR/MACL/PR/R14 restoration and R12 pop
in the RTS delay slot remain separate physical effects.

The domain requires 28 two-sided conditions and 7 fixed conditions. Exactly
three impossible byte-cap instructions, two negative-divisor instructions,
51 signed zero/large-divisor instructions and two fractional zero-return
instructions form the 58 excluded instructions. All remain in the complete
bound image. Their caller premises and each remaining instruction are explicit.
