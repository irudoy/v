# JK08A byte ratio producer withdrawal

Source bindings: `JK08A.byte-ratio-producer-withdrawal-paths.toml`.


## Complete products and distinct real division paths

The caller occupies 4AE6C..4AEAC and 4AEC4..4AF38 around its literal hole.
All three complete helpers remain bound: 21BBC..21CD6, 21CE0..21DC6 and
22508..2251A.

The unsigned byte at 17B8 multiplies the complete unsigned word at 14DC.
A zero product selects sentinel 65535 without calling the first divider.
A nonzero product is the actual unsigned divisor. The complete unsigned word
at 1630 multiplies 120 times the raw byte at ROM884D to form the numerator.
The real 21CE0 helper retains word/large-divisor and short/long paths. The
first result or sentinel then adds floor(5*raw_ROM8B6C/2).

Below 65536, the complete unsigned 11BC word multiplies that ratio. The caller
keeps the low32 product, shifts it logically by10, multiplies by3 and executes
real unsigned division by5. At or above 65536, the caller instead forms the
low32 product word11BC*65535 and executes the full 22508 helper. That helper
performs a signed shift by10, including its sign extension and both SHAR steps.
The full result multiplies by3 and enters the real 21BBC signed divider with
positive divisor5. Both signs and short/long signed paths remain required.
An ideal widened product or a common unsigned shift does not replace either path.

The final comparison treats the quotient as an unsigned32 word. Values above
141 select127. Other values subtract14 before the byte store, including the
actual wrap below zero. A zero quotient therefore publishes raw242. The real
publication at4AF36 is in the RTS delay slot and writes RAM23F1. R0 returns the
fixed displacement53. MACL, PR, the complete frame and every actual CPU/SR value
remain bound through the natural return.

The exact domain requires 9 two-sided conditions and 4 fixed conditions.
The 59 excluded instructions are the signed helper's two negative-divisor
instructions, its51 zero/large-divisor instructions and the unsigned helper's
six zero-divisor instructions. Their bytes remain in the complete image, and
the complete broader direct-divider original is mandatory from the identical primary.

## Actual saved R1 continuity

The scalar quotient does not determine post-DIV1 R1 or Q. A nonzero first
division followed by the upper ratio branch passes that actual R1 to22508,
which saves it at caller_SP-12 and restores it in its real return delay slot.
The independent arithmetic leaves the value unknown. Exactly the two physical
operands22508/22518 bind their full four bytes to the complete reconstructed
instruction trace, with the real predecrement/postincrement stack positions and
the same complete restored R1. No unknown value is admitted as a numeric input.

The following real21BBC push replaces all four bytes with independently known
R2 at the same stack address. The independent final frame therefore contains
no unknown bytes and compares in full with actual returned frame memory.
An omitted/duplicated operand, changed site/address/width/register, detached R1,
changed stack position, broadened unknown scope or absent known overwrite fails.
The complete actual instruction engine and observer remain unchanged.

## Causality and exact native boundaries

Fixed-other alternatives require changed actual final bytes at a common real
computed publication outside the controlled RAM input. Complete CPU, SR, RAM,
frame, calibration and bound preimages remain fixed. Input echoes, unchanged
common values and a changed write-set alone fail. The selected ROM12006 root
requires exact physical interval absence independently of operand direction or
domain labels. No native geometry or natural-caller interpretation is inferred.


Full actual-original, independent arithmetic, variable product/division,
65536 split, signed shift, actual saved R1, frame overwrite, byte publication,
CPU/SR/RAM/physical/call/delay/return/causal/native/prior/full-function/type/
role/TEST/ledger/scope/review and published-count refusals remain mandatory.
Source preparation grants no executable acceptance, owning replacement,
reverse donation, native geometry, scale, units or hardware admission.


The complete byte-factor caller boundary is specified in
`defs/JK08A.byte-factor-caller-withdrawal-paths.md`. All121 preceding full
records,current images and64 complete functions remain exact. An additional
complete function transition removes one individually pinned reverse writer
selector;the preceding two transitions,row79,row99,eight writer identities
and eighteen indexed_by originals remain exact. Both real byte curves,signed
word promotion,partial products and the percentage delay-slot store are required.
