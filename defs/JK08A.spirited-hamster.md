# Conditional byte denominator

The explicit `0007A20A` window in `0007A090` reads byte curve `00011FD6`
through natural `00026474`, axis search `00026944`, `00026C78` and linear
interpolation `00026740`. R2 explicitly contains a byte coordinate and R11
names the relocated `FFFF28F8` base. The eight semantic bytes retain the
physical neighbor at `00011FDE`; the wrapper reads next byte before current
byte. The source contract preserves this access order.

The lookup result is stored at `FFFF2BE4`. Nonzero results enter unsigned
divider `00021CE0` in R0 at `0007A230`; delay slot `0007A232` places the
product of unsigned word `FFFF2C78` and 200 in R1. The quotient is capped
at 65535 and stored at `FFFF2C74`. A zero lookup bypasses division, selects
65535 and preserves the fault word at `FFFF9818`.

The bounded fixture contains each natural helper instruction and literal.
The separately assembled observing return at `0007A248..0007A250` reads the
saved continuation at SP+24 through R7. Its bytes `57F6472A000B0009` replace
only instructions outside the tested stock spans. The complete parent path,
following instructions and scheduler are not admitted.

The raw component retains explicit register and RAM inputs, stock or
controlled curves and axes, the unchanged physical neighbor, complete CPU,
SR, ABI, frame and RAM, and actual calibration bytes. It remains inside the
same complete COPY original. Independent physical, instruction-state and
integer consumers require actual arguments after delay slots, required
conditional outcomes, the no-fault zero bypass and independent curve changes
with distinct divisors and outputs.

The exact proposed `arithmetic-argument` dependency preserves the complete
original claim and retires only its corresponding legacy consumer selector.
Its native write operation is not registered. Source preparation supplies no
qualification, physical ROM reader on the arithmetic callee, units, scale,
complete parent reachability, natural scheduling or hardware result.
