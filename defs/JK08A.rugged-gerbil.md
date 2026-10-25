# Conditional high-range denominator

The explicit `00081674` window in `0008152A` selects word curve `00015022`
through natural `000263F4`, the `00026A64` entry of `00026A60`, and `00026740`.
Incoming R0 is restricted to `00003C00..0000FFFF`; the lookup coordinate is
R0 minus `00003C00`. R14 names the natural wrapper; R12 and GBR explicitly
name the relocated `FFFF128C` base. These are bounded entry premises, not
proof of the complete parent path or its scheduling.

The kernel uses sixteen unsigned words with uniform `00001000` spacing.
Its complete word interpolation retains the selected word and next word.
The bounded coordinate reaches at most `0000C3FF`, below the wrapper's
terminal-knot branch at `0000F000`.

The interpolated result is narrowed to its high byte and stored at
`FFFF1738`. A nonzero high byte enters unsigned divider `00021CE0` as R0
at call `0008169A`; delay slot `0008169C` shifts the independently supplied
byte at `FFFF1737` left by eight in R1. A zero high byte bypasses the call
and selects 255. The quotient is capped at 255 and stored at `FFFF1733`.
The zero bypass preserves the divider fault word at `FFFF9818`.

The fixture independently reconstructs all tested stock instructions and
literal pools. An observing return at `0008171E..00081726` loads the saved
continuation from SP+24 through R7; its separately assembled bytes are
`57F6472A000B0009`. It lies outside the tested stock spans and admits no
following parent instructions. No stock helper is replaced by a stub.

The raw component retains the complete actual CPU, SR, ABI, frame, RAM,
calibration and original terminal inside the existing common COPY packet.
Independent instruction-state and numeric consumers require the explicit
entry premises, physical word reads, arguments after delay slots, zero
bypass and positive independent calibration changes with distinct divisors
and outputs. Native relation admission requires the complete original and
current exact inputs.

The proposed native disposition changes only the exact legacy reader of
`00015022` on `00021CE0` into an `arithmetic-argument` dependency. The complete
original claim and ledger constrain the proposed replacement. Its native
write operation is not registered. Source preparation supplies no
qualification, physical ROM read by the arithmetic callee, units, scale,
complete parent reachability, scheduler behavior or hardware result.
