# Conditional value argument of the cranking calibration

The natural `000B7A3C` entry uses the eight-word `00014E42` curve through
`000264CC`, with axis `00013BB8` and the low byte of the independent fifth
argument shifted left by eight. The physical lookup reads the selected word
and its following word; the retained ninth word is a stock neighbor, not an
additional semantic knot.

The lookup result is negated, multiplied by the byte at `00008832`, and
multiplied by 20 with low32 arithmetic. Call `000B7AE8` passes that product in
R1 to signed divider `00021BBC`. Its delay slot `000B7AEA` places the low
16 bits of incoming R4 in R0. A zero R4 halfword bypasses this call and does
not inherit the divider's zero-divisor fault write at `FFFF9818`.

The preceding signed call uses divisor 20000. The following `000264F8`
lookup uses `000151F2` and axis `00013BF8`; two unsigned calls use divisors
255 and 2500. The natural return preserves the stock frame operations.
The final 32-bit store is at `FFFF3228`. These operations remain part of
the independent complete-RAM and CPU-state equations.

The raw driver records explicit R4/R5/R6/R7/fifth arguments, calibration
bytes, complete RAM, registers, special registers, SR, ABI and frame state.
Controlled curve and axis inputs include a positive lookup change under
equal arithmetic arguments and other calibrations. The independent consumer
requires distinct lookup values and R1 products, exact post-delay call
arguments, the zero-divisor bypass, physical reads, and branch outcomes.
The curve, axis and configuration inputs are explicit simulator inputs;
their use does not establish natural caller reachability.


The proposed native disposition replaces the exact `00014E42` reader claim
on `00021BBC` with a conditional `arithmetic-argument` dependency. Its
descriptor retains the complete original claim and ledger and retires only
the corresponding legacy consumer selector. The operation is not registered
for native publication. Source preparation supplies no qualified claim,
scale, physical ROM reader on the arithmetic callee, scheduler behavior or
hardware qualification.
