# Natural signed-curve entry

`JK08A.signed-curve.toml` declares the complete stock function `0007B0A0`
and its natural 16-word lookup and signed-division helpers. The GNU fixture
preserves instruction words, delay slots and returns. Only listed RAM
pointer literals relocate to simulator storage.

The entry reads two curves through `000266E8`. `00018E06` supplies the bias.
`00018DE6` is `vagabond-seagull`. Both use the 16-knot axis at `00018E26`
and the unsigned coordinate at `FFFF10BC`. Each curve has 16 semantic words.
The wrapper also reads the following physical word, which is the first word
of the next object.

Each lookup is biased by -32768. Their floored difference is the signed
divisor. Three nonnegative RAM differences are multiplied by 800 and passed
in R1. `0007B152` completes that dividend from MACL. `0007B16A` and
`0007B182` place the divisor in R0. A zero difference skips all three calls
to `00021BBC` and stores 800. The bypass does not inherit the callee
zero-divisor fault store at `FFFF9818`.

`FFFF4214` bit `0x40` selects the comparison word. `000083C1` bit 1 selects
whether the bounded result or the word at `FFFF2712` is published at
`FFFF35CE`. Independent equations cover the lookups, the post-delay signed
arguments, the zero bypass and the clamps. The proof does not publish a
native relation, admit scale, establish scheduling, or qualify hardware.
