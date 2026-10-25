# Natural quiet-cat

`JK08A.quiet-cat.toml` declares the complete stock function `000BE32A`
and its natural byte-lookup and division helpers. The GNU fixture preserves
instruction words, delay slots and returns. Only listed RAM pointer literals
relocate to simulator storage.

R4 is an index. The byte at `FFFF1224` plus that index, reduced by 128, is one
factor of the later product. `000BE3BC` divides a separate lookup by 100.
`000BE41E` enters `00021BBC` and uses `000123EA` or `00012412`.

Index zero selects `000123EA`, `belligerent-potoo`. Any other index selects
`00012412`, `red-bullmastiff`. `00026474` reads the selected eight-byte curve
on the axis at `00011BE3`, including the following byte. `000BE420` completes
the product of that lookup and the biased difference in R1. R0 is the constant
100.

Independent equations cover both indexes, the post-delay operands and the byte
reads. Changing only the selected curve changes the dividend. The other curve
is not read. The divisor is never zero, so the callee fault store at
`FFFF9818` stays unchanged. The proof does not publish a native relation,
admit scale, establish scheduling, or qualify hardware.
