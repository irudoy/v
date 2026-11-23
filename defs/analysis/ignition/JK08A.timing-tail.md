# Explicit timing accumulator tail

`JK08A.timing-tail.toml` declares the stock tail entered at `0004B3F2`
inside `0004AFDC`. It retains the stock instructions through the byte store
before `0004B4A4`, their literal pools, delay slots and natural lookup and
unsigned division helpers. Entry explicitly supplies R9=`01001068`,
R10/GBR=`0100128C` and R13=`010041A9`. Execution from the parent function
entry and natural scheduling are not inferred from this bounded input.

The tail selects the minimum of words `FFFF28B8` and `FFFF28BA`, subtracts
7350, bounds the coefficient below at zero and stores its word at
`FFFF1900`. It admits the lookups only when `FFFF41AB.bit6` is set and
the selected minimum reaches the stock word at `00009010`.

The byte curve `00011EFA` uses coordinate `FFFF106F` and axis `00011EEA`
through natural wrapper `00026474`. Its endpoint neighbor at `00011F02`
is physically read with zero weight. The word curve `000147CA` uses
coordinate `FFFF10CA` and axis `0001460A` through `000264CC`. Its physical
endpoint neighbor is the word at `000147DA`. Both neighboring inputs retain
their stock bytes in every synthetic calibration variant.

The word result is bounded to 255. Its product with the byte result and
the stored coefficient supplies R1 through `0004B472`, the delay slot of
the call at `0004B470`. R0 supplies divisor 500000. The unsigned quotient
is bounded to 255. The bounded tail publishes `FFFF1347`, `FFFF1349`,
`FFFF134B` and `FFFF12D5` on the admitted path; disabled lookup paths
preserve the cached curve outputs and publish zero at `FFFF12D5`.

A separately assembled observing return occupies `0004B4A4..0004B4AC`,
outside the stock spans under test. It restores PR from the observing
frame at `SP+24` and returns through that explicit continuation. It admits
no subsequent parent instructions and replaces no natural stock helper.

The original capture includes the full context, GPR/special/SR/ABI state,
frame, RAM, calibration and observing boundary. Independent consumers
bind actual private inputs, exact reconstruction, fixture, executable,
commands and terminal to separate curve, coefficient, product, quotient,
clamp, physical operand and complete-state equations. Independent table
variations retain other inputs and must change the divider argument and
bounded output.

The timing argument descriptor registers the exact `00011EFA` and
`000147CA` reader dispositions with the existing compositor dispositions.
The normal writer requires every registered original claim, qualified
same-primary components and exact ledger selector retirement. Every other
fact, TEST context and existing physical proof namespace remains fixed.
The dependency grants identity only, without scale, units, parent-entry
reachability or hardware qualification.
