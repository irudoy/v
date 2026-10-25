# Natural uptight-duck entry

`JK08A.uptight-duck.toml` declares the complete stock function `000B784E`
and its natural 32-knot lookup and signed-division helpers. The GNU fixture
preserves instruction words, delay slots and returns. Only listed RAM
pointer literals relocate to simulator storage.

Incoming R5 is the coordinate. `00026524` reads three 32-word curves on the
axis at `00013CA8` and also reads the following physical word. `00015C80`
is `blond-panther`. The stock axis is 32 zero knots, so every coordinate
selects the last knot. A strict axis is an explicit calibration input.

The signed call to `00021BBC` at `000B7892` does not receive any of those lookups.
`000B7894` places incoming R4 in R1. R0 is the constant `000F4240`. The
lookup is stored and becomes the published word at `FFFF35B6` when the
sign-extended low half of the quotient is at least the byte at `00008C8C`
minus 50. Otherwise that word is 1.

Independent equations cover the lookup, the post-delay operands and both
publications. The divisor is never zero, so the callee fault store at
`FFFF9818` stays unchanged. The proof does not publish a native relation,
admit scale, establish scheduling, or qualify hardware.


## Independent coordinate inputs

The input stream retains all 11 original cases and their complete contexts.
Additional rising-curve/strict-axis coordinate contrasts hold the dividend,
threshold, other registers, SR, complete RAM and calibration fixed. They use
a fixed fifth word independent of R5, including word sign and upper boundaries.
The same input header, C driver and observer transport this explicit raw word.
These definitions supply no executed coordinate comparison, caller-origin
binding, datum identity or native publication by themselves.


The coordinate response consumer binds all three real 26524 calls and their
post-delay R6 arguments to incoming R5. It requires the actual word stores at
FFFF35A0 and FFFF35B6, positive output contrasts in every controlled interior
interval and invariant endpoint publications. Complete other CPU, SR, frame,
RAM, calibration and caller inputs remain fixed. This callee value response
supplies no independent binding to an upstream RAM source or native relation.

The same complete callee capture varies four prior bytes at FFFF3348 while
holding the other inputs fixed. Every bit, its complement and integer edges
participate in each combination of the two publication branches. A separate
consumer rejects native, relocated and overlapping accesses to those bytes,
requires their preservation and compares the complete returned CPU, frame,
other RAM, ABI, calibration, calls and physical path. This selected physical
reader boundary preserves the incoming R4 signed dividend, its constant divisor
and the caller's distinct value publication. Four controlled storage bytes
supply no semantic width or signedness declaration for the native owner.
