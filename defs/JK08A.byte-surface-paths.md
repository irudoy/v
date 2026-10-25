# JK08A byte-surface caller and natural interpolation closure

`defs/JK08A.byte-surface-paths.toml` declares the complete natural entry at
`000BFDC0`, its byte-surface wrappers, byte-axis search, interpolation kernel,
linear blend and divider. The independent mnemonic source retains their stock
entries, calls, returns and delay slots. The image identity binds the owned
JK08A stock bytes.

The caller reads the first coordinate from `FFFF11AE`. Its second coordinate
uses the byte at `FFFF102C` or the forced value 255, selected by `FFFF2468.bit3`
and `ROM8[00008615].bit0`. The optional correction uses `FFFF2466.bit6`.
The caller stores the first surface byte at `FFFF1C5F`. It stores the main
surface byte, or `clamp(mainByte - correctionByte + 128, 0, 255)`, at
`FFFF1C5D`.

## Conditional geometry and arithmetic

The wrappers supply their axis maxima and row strides to natural helper paths:

| Table | Axis maximum | Row stride |
|---|---|---|
| `0000AB4A` | 3 | 4 |
| `0000B2FA` | 7 | 8 |
| `0000B33A` | 15 | 16 |

These bounds describe conditional row-major extents;
canonical geometry publication requires independent complete admission.

The byte-axis search clamps outside its endpoint interval. Between distinct
knots it produces a 16-bit fraction by unsigned division. The surface applies
column interpolation before row interpolation. A decreasing blend subtracts
the truncated positive difference product. The direct-cell return retains the
MOV.B sign extension; the caller explicitly consumes its low byte.
`byte_surface_semantics.py` expresses these numeric equations separately from
the bounded instruction-state oracle in `byte_surface_equations.py`.

## Fixture and state boundary

Pool `000C0008` holds `FFFF5773`, a wrapping offset relative to ROM GBR
`00012EA2`. Their 32-bit sum is `00008615`. This pool is excluded from RAM
pointer relocation. Declared native RAM pointer pools use simulator aliases;
the test instructions remain unchanged. No stock helper is a simulator stub.

The state oracle admits only the declared instruction closure and bounded
ROM, RAM and observer-frame domains. It retains each exact-width access,
full general/special register and SR result, stack writes, calls, returns and
delay slots. This oracle is an expected-state calculation and supplies no
execution receipt.

The DIV0U, DIV1 and ROTCL flag equations follow the
[SH-2E Software Manual, REJ09B0316-0200](https://www.renesas.com/en/document/mah/sh-2e-software-manual),
sections 7.2.17, 7.2.18 and 7.2.44. The DIV1 Boolean equation retains M/Q/T
instead of substituting a quotient for the natural instruction sequence.

## Dependency boundary

The outputs at `FFFF1C5F` and `FFFF1C5D` enter later conditioning. A positive
path through that conditioning and the complete SID22 byte publication must
separately support a ROM-to-DID dependency. This caller/helper scope supplies
no later BFE88 path, physical ROM-reader relation for the SID publisher,
universal ROM-read exclusion, upstream coordinate reachability or hardware
qualification.

## Original observation contract

The raw producer runs in the complete stock runner and retains
`byte_surface_paths` in the existing COPY packet. Caller and direct-helper
inputs have explicit typed roles. Stock and synthetic calibration inputs are
distinct cases: synthetic table patterns exercise cell addressing, decreasing
blends, both correction clamps and their exact boundaries. Configuration-bit
variants preserve the surrounding ROM byte. Test instructions and natural
helper entries remain fixed.

The existing independent-fifth observer supplies the 80-byte input context and
572-byte full observation. It stages the lookup fifth argument at SP+0 and
incoming R7 at SP+4. The driver emits actual const context, full register/SR,
caller ABI, frame, complete RAM, and calibration bytes before and after each
invocation. Lossless canonical RLE represents the entire RAM span.

The independent consumer binds current native table/function anchors, complete
code/pool reconstruction, exact aliases, actual private sources, fixture/ELF
identities, compile/simulator commands, finite simulator bound, original streams
and typed invocation order. Separate state and numeric equations must agree
with every actual observation. Required conditional branches have both outcomes;
all natural entry roles and correction boundaries participate. Raw packets
supply no self-admission, native geometry or ROM-to-DID dependency.
