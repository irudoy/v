# JK08A diagnostic reset helper byte writer

The original `8dec00dbb4e93fb0907e58c1a1a0dd41e845c8856a229170e4ac1a3ad399b3c2`
associates `chocolate-civet/ram` at `FFFF99C7` with `cheerful-beluga/fn`
at `0002E76E`. The exact native append supports that writer identity.
The native storage width and signedness remain unset, and the unit remains
`bitfield`. Complete owner facts, other reader and writer relations, symbol
evidence, ledgers, TEST origins and all retained functions remain exact.


At `0002E77A`, stock `mov.b r7,@r5` (`2570`) stores zero to `FFFF99C7`.
The first helper loop has 4 stores starting at `FFFF99C4`; the selected
zero-based iteration is 3. Full `R7=0`, `R5=FFFF99C7`, `R6=4` and `R4=4`
belong to the actual instruction state. The caller at `0002E824` enters the
helper through its real `0002E826` delay slot and returns to `0002E828`.
The helper establishes its loop bound from stock instructions; no caller
`R4` premise is admitted. Its `0002E816` RTS and `0002E818` ordinary-byte
store delay slot retain their actual effects and the parent frame.


The executable fixture, independent complete-state equations, native banks,
exact PC/address/range/width/mode permissions, observer ABI, runner and real
call closure are the existing diagnostic reset boundary. This identity proof
admits no native geometry, scale, unit conversion, natural scheduling,
caller reachability, peripheral side effects or hardware qualification.
