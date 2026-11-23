# Conditional timing compositor and divider arguments

`JK08A.timing-division.toml` declares the complete stock `0004BDC2` function
and its natural lookup, interpolation and unsigned division helpers. The
GNU fixture preserves instruction words, delay slots, stack operations and
returns. Only the listed RAM pointer literals relocate to simulator storage.
No stock function is replaced by an arithmetic stub.

The normal lookup path requires `FFFF2458.bit5` clear, `FFFF41AB.bit6` set
and the minimum of words `FFFF28B8` and `FFFF28BA` at least the stock word
at `00009012`. Other modes retain their conditional cache and publication
effects and omit both table lookups and the divider call.

The byte wrapper `00026474` reads the `00011F02` curve through the byte
axis at `00011EEA`, with coordinate `FFFF106F`. It has eight semantic
values. It physically reads the following neighbor before the selected
value even at an endpoint with zero interpolation weight. The synthetic
calibration inputs retain the ninth byte from the stock image.

The word wrapper `00026270` reads an eight by eight word surface at
`0000C50E`. The row and column axes are `0001461A` and `0001464A`.
Coordinates come from words `FFFF10CA` and `FFFF1024`. The latter reaches
the wrapper through the caller's actual local word at `SP+2`; it is
independent of the observing context's fifth value. The kernel `00026848`
reads adjacent columns and rows only when their respective interpolation
fractions are nonzero. Both stock word axes start at zero, so unsigned
coordinates cannot reach the negative-index exit of the axis scan.

The caller bounds the word lookup to 255, multiplies it by the byte lookup
and word `FFFF1900`, and passes the low 32 bits as the dividend in R1.
The divisor in R0 is 500000. The instruction at `0004BE82`, in the delay
slot of the `0004BE80` call, copies MACL into R1. Argument admission uses
the callee-entry state after that slot. The unsigned quotient is bounded
to 255 and published at `FFFF134A` and `FFFF12D4`; the final signed
composition is bounded to -128 through 127 at `FFFF1830`.

Independent numeric equations cover the two lookups, actual operand
offsets, multiply/divide inputs, clamps and complete RAM publication.
Separate instruction equations compare all GPRs, special registers, SR,
the observing frame, call/return state and the complete RAM image with
the original GNU observations. The original process, terminal, exact
image, reconstruction, private input header, observer, executable identity
and current source closure remain required.

The bounded caller proof distinguishes the physical lookup readers from
the later divider's value arguments. It does not publish native relations
or geometry, resolve other divider callers, admit units or scale, establish
natural scheduling, or qualify hardware behavior.
