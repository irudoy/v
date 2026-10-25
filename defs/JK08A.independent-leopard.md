# Natural independent-leopard loop

`JK08A.independent-leopard.toml` declares the complete stock function `0005AC54`
and its natural byte-lookup and unsigned-division helpers. The GNU fixture
preserves instruction words, delay slots and returns. Only listed RAM
pointer literals relocate to simulator storage.

The loop runs two steps. Each step subtracts the word at `FFFF4020` from the
word at `FFFF288C`. The byte at `FFFF3529` becomes a coordinate: values below
`0x68` select the first curve byte, and larger values shift the excess left
by one and saturate at 255. `00026358` reads a four-byte curve. Coordinates
at or above 192 return the last byte. Smaller coordinates interpolate the
pair selected by the top two coordinate bits.

When the low 16 bits of the difference are nonnegative, the curve is
`00012522`, `fuzzy-giraffe`. Otherwise the curve is `00012526`, `rough-moose`. The lookup
byte is multiplied by the 32-bit difference, or by its negation on the
negative path. `0005AD64` completes that product in R1 from MACL. R0 is the
constant 100. The quotient is then combined with 500 and stored at
`FFFF40A4`.

Independent equations cover both steps, the post-delay unsigned arguments
and the byte reads. The divisor passed to `00021CE0` is never zero, so the callee fault store at
`FFFF9818` stays unchanged. The proof does not publish a native relation,
admit scale, establish scheduling, or qualify hardware.
