# JK78C VVEL load coordinate

## Scope

`vvel_load_coordinate/ram` is the unsigned word at `0xFFFF238A` on layout
`jk78c`. Its native owner records the storage, reviewed producer/consumer
locations, and the unit boundary. `JK78C.vvel.md` describes the surrounding
mode selector and target pairs.

The word supplies the load coordinate of the mode-4 intake-phase surface. It
is separate from `normalized_load/ram` at `0xFFFF1032`, the Q7 normalized Base
Fuel Schedule snapshot. The coordinate does not inherit that byte's percentage
conversion.

## Stored-count producer

Function `0x0004726C` reads unsigned words `0xFFFF310C` and `0xFFFF197A` at
`0x000472A8` and `0x000472B4`. Both convert exactly to single precision.
The instructions multiply them, multiply by the single-precision literal
`0x307FFFFF` at `0x00047450`, and then by `0x42C80000` at `0x00047454`.

The result is compared with `0x42C7FEF9` at `0x00047458`. A larger result
selects `0xFFFF`. Otherwise the result is multiplied by `0x4423D70A` at
`0x0004745C` and converted to an integer with `FTRC`. Instruction
`0x00047326` stores the selected low word in `0xFFFF238A`.

The constants decode to approximately `9.313225191043273e-10`, `100.0`,
`99.99799346923828`, and `655.3599853515625`. The instruction sequence retains
its single-precision rounding and comparison. Replacing it with an exact
integer-product shift or a decimal scale is not an established equivalence.
The upstream physical roles of the two input words are outside this binding.

## Mode-4 consumer

Task `0x00054FD0` reads the coordinate at `0x00055466` and stores the word at
its `SP+0x3A` at `0x0005546A`. The resolver call is `0x000554AC`.

Resolver `0x000564A4` saves 48 bytes and allocates 64 bytes before its body.
Its `SP+0xAA` therefore denotes the caller's word at `SP+0x3A`. Instructions
`0x000566D8..0x000566DA` retrieve the word; the delay slot at `0x000566E0`
places it at stack coordinate `+2` of the lookup called at `0x000566DE`.
The lookup uses values `0x000108CE` and axes `0x00016DE4/0x00016E04`.
The other coordinate is the engine-speed word supplied in `R7`.

The native RAM reader relation names the direct task reader. The resolver's
forwarded stack argument is recorded here as a static caller/callee path;
it is not represented as a direct RAM access by the resolver.

## Unit boundary

The established representation is a stored unsigned count with the producer
sequence above. Neither a constant named `100.0`, the axis endpoint, nor a
similar coordinate on another layout independently establishes physical
engine load, cylinder filling, or `100*x/65535` percent. The physical role of
the input product and an independent scale anchor remain unresolved.

The mode-4 table's centered numeric phase arithmetic also retains its
separate physical-degree boundary. This coordinate binding establishes
neither valve motion nor camshaft/crankshaft degree units.
