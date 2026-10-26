# Conditional signed arguments of the byte control curve

The natural `0004BBEE` entry selects two byte curves with `FFFF2466.bit6`.
The set branch reads `0001244A` and paired `00012472` through `00026388`;
the clear branch reads `0001243A` and `00012462`. The natural uniform
interpolation enters `00026A84`, then `00026740`, or reads the terminal
byte directly. Selected and unselected physical reads remain distinct.

The first lookup is stored at `FFFF15ED`, the second at `FFFF15EE`. When
the first result is below ROM byte `00011ECD`, the positive difference
becomes divisor R0 at signed call `0004BCEC` to `00021BBC`. Delay slot
`0004BCEE` transfers the low32 product of the second lookup and
`uint8[FFFF1048] - first_lookup` into R1. The signed quotient is capped at
the second byte and floored at zero, then stored at `FFFF15EC`. The other
branch stores zero there without invoking the divider.

The remaining natural instructions read the prior byte at `FFFF15EB`,
history word at `FFFF22E8` and mode-selected coefficients at `000087CA`.
They form the piecewise low32 product, apply the signed shift by fourteen,
cap it at the preceding phase value, floor it at zero and store `FFFF15EA`.
The complete frame, natural helper calls and return, registers, SR, ABI,
RAM, physical curve bytes and calibration snapshots remain observed.

The proposed `arithmetic-argument` dependency preserves the original exact
claim and retires only its corresponding legacy consumer selector. Its
native write operation is not registered. Source preparation supplies no
qualification, physical ROM reader on the arithmetic callee, units, scale,
natural scheduling or hardware result.
