# Natural denominator entries

`JK08A.timing-denominator.toml` declares the complete stock functions
`0007B2C8` and `0007B3F4` together with their natural lookup and division
helpers. The GNU fixture preserves instruction words, delay slots, stack
operations and returns. Only listed RAM pointer literals relocate to
simulator storage. No stock function is replaced by an arithmetic stub.

Both parents read `000083C1` bit 1 before any lookup. When the bit is
clear, `0007B2C8` copies the word at `FFFF243C` to `FFFF2C6C`, and
`0007B3F4` copies the word at `FFFF1D26` to `FFFF35D2`.

When the bit is set, each parent interpolates a 16 by 16 word surface and
an eight-word denominator curve. `0007B2C8` reads `0000C98E` through
`000262A8` and `00014AFA` through `000264CC`. `0007B3F4` reads `00016948`
through `00026628` and `00018DD6` through `000266BC`. The row coordinate
is the unsigned word at `FFFF412A` or `FFFF35CE`. The column coordinate is
the word at `FFFF11B6`, passed through the caller's local word at `SP+2`.
The curve coordinate is the unsigned word at `FFFF10BC`.

Each curve has eight semantic words and one physical neighboring word.
The wrapper reads that neighbor even when the selected interval weight is
zero. Synthetic curve inputs retain the stock neighbor. Each surface axis
has 16 knots and starts at zero, so an unsigned coordinate cannot take
the negative-index exit of the axis scan.

The curve result is the unsigned divisor. The dividend is the same
unsigned row word multiplied by 255. `0007B330`, in the delay slot of
`0007B32E`, places the divisor in R0 after R1 already holds the dividend.
`0007B484`, in the delay slot of `0007B482`, finishes the dividend in R1
after R0 already holds the divisor. Argument admission uses the callee
entry after the delay slot. A zero curve result branches around
`00021CE0` and saturates the ratio at 255 in the caller. That bypass does
not execute the callee and does not inherit its zero-divisor store of
`0000044E` at `FFFF9818`.

The later signed calls `0007B356` and `0007B4AA` copy MACL to R1 in their
delay slots and divide by the constant 255. `FFFF41FB` bits `0x20` and
`0x10` are final overrides of `0007B2C8`. `FFFF4214` bits `0x10` and
`0x20` select a stored word in `0007B3F4` before either lookup.

Independent equations cover both surfaces, both curves, the post-delay
unsigned arguments, the zero bypass, the signed correction and the clamps.
Separate instruction equations compare the complete machine state with
the original GNU observations. The original process, terminal, image,
reconstruction and private inputs remain required. The bounded proof does
not publish native relations or geometry, resolve other divider callers,
admit scale, establish natural scheduling, or qualify hardware behavior.
