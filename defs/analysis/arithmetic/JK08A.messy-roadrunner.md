# JK08A bounded byte correction

The explicit `00069374` window `0006AE78..0006AEBC` supplies R2 as a uint16
coordinate source, R8 as the simulator view of `FFFF8E08`, R11 as `00021BBC`,
and GBR as the simulator view of `FFFF8E34`. Complete parent reachability and
the preparation of these inputs are outside the scope.

The window passes the high byte of R2 to natural `00026474` with table
`00011F3A` and axis `00011AEF`. Its eight semantic bytes retain the physical
neighbor at `00011F42`. The helper reads the next byte before the current
byte, including at the endpoint where the neighbor has zero weight.

The zero-extended lookup M is shifted left six bits. Call `0006AE92` receives
R1=`M * 64` and R0=125 after delay slot `0006AE94`. The quotient is in
0..130, so the following byte extension preserves it. The caller adds it to
`uint16(FFFF8E08)` and stores the full sum at `FFFF8EC0` in delay slot
`0006AEA6`. The word store `0006AEBA` publishes
`min(base + floor(M * 64 / 125) + 0x7FBE, 65535)` at `FFFF8FDE`.

The original physical-reader claim on the arithmetic callee has an exact
conditional arithmetic-argument proposal with its complete original ledger.
The proposal does not admit physical units, scale, scheduling or hardware
behavior. The raw execution and independent physical/full-state/numeric
consumers require actual lookup operands, post-delay arguments, both stores,
independent calibration variation and both saturation outcomes.

No stock pointer literal is relocated. The separately assembled observing
return starts at `0006AEBC` and restores the observer continuation from SP+24.
The following absolute control-memory stores remain outside the window.
