# Conditional signed curve-difference arguments

The explicit `00044A58` window in `00044910` reads `00012738` as A,
`00012748` as B and `00012930` as C through natural `00026388`, `00026A84`
and `00026740`. Each curve has sixteen bytes and a common coordinate from
`FFFF106F`. R10 explicitly supplies the relocated `FFFF128C` base, R11 the
relocated `FFFF106A` base and R14 the natural wrapper address.

If A>B, signed divider `00021BBC` receives divisor A-B in R0 at `00044A9C`.
Delay slot `00044A9E` places the low32 product C*(A-uint8[`FFFF16AB`]) in R1.
The quotient is floored at zero, capped at 255 and written to `FFFF171D`
by `00044ABA`. A nonpositive difference bypasses division and writes zero.
Independent changes of A and B must change the corresponding arguments
and bounded result under equal RAM and other calibrations.

The raw driver retains complete CPU/SR/ABI/frame/RAM and actual calibration
state. Independent physical, instruction-state and integer consumers require
all three lookup calls, exact byte reads, natural helper execution, both
required conditional outcomes, arguments after delay slots and the actual
output store. The unconsumed native pointer loaded into R9 before the store
retains its original value; no native memory access through it is admitted.

A separately assembled observing return at `00044ABC..00044AC4` uses the
saved continuation at SP+24. Its bytes `57F6472A000B0009` lie outside the
tested stock spans. The frame equations retain the partial byte writes at
SP and SP+4. No stock helper is stubbed. The complete parent path, preceding
register preparation, following parent instructions and scheduler remain
unadmitted.
