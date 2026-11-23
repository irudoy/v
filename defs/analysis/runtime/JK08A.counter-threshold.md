# JK08A bounded counter threshold

The explicit `00079538` window starts at `00079686` with R6 equal to
`min(uint16(FFFF40C6) >> 2, 255)`, R11 pointing to `FFFF28F8`, and R12 equal
to zero. The preparation of those entry values and the complete parent state
machine are outside the admitted window.

The natural `000260BC` helper uses `00026944` twice to find lower-knot indices
on the four-byte axes at `00012FEE` and `00012FF2`. It ignores both returned
fractions. It reads one signed byte at `table + row_index * 4 + column_index`;
the caller converts that byte to uint8. The first table is `0000AAFA`, whose
selected byte is stored at `FFFF351C`; the adjacent table `0000AAEA` supplies
the lower threshold at `FFFF3449`. The row comes from `FFFF11AE`. The column
comes from the low byte of the caller word at SP, physically SP+3, which the
caller writes independently of the R7 row argument.

The byte counter at `FFFF3448` multiplies the selected AAFA byte. Call
`00079728` receives constant 10 in R0 and the complete product in R1 after
delay slot `0007972A`. Both inputs are uint8, so signed division equals
`floor(elapsed * raw / 10)` throughout the admitted domain. The threshold is
the maximum of that quotient and `uint8(FFFF3449)`. The word counter at
`FFFF3446` increments with saturation at 65535. The comparison sets R12 when
the incremented counter reaches the threshold.

`JK08A.counter-threshold-factor.toml` binds only the existing AAFA fields
`unit="ratio"`, `scale="x/10"`, `to_raw="x*10"`, and `scale_level="code"`.
The owning arithmetic-factor dependency retains the original scale support.
Its joint consumer requires the complete original raw execution, exact native
claim, ledger, and existing scale fields. The raw capture grants no scale by
itself. This proof supplies no physical time units or scale to another owner.

The fixture aliases only the RAM pointers at `000797F8` and `000797FC` into
the simulator RAM window. The observing return at `0007974A` restores the
observer continuation from SP+24 and is assembled separately from the stock
instructions. The zero-divisor fault pointer stays stock because the divisor
is constant 10. Simulator boundaries do not establish complete parent
reachability, scheduling, subsystem semantics, or hardware behavior.
