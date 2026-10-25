# JK08A bounded whole feedback calculation

## Bounded feedback

The natural entry 0005cbec executes both bank state paths and fifteen real
helpers. One mandatory Region binds 3067 instructions, 63998 bound bytes and
1829 literal cases. There are no stock-function stubs. The wide calibration
span binds byte identity; it does not assign meaning to every covered byte.
The independent equations describe raw software inputs and the exact stock
calibration. Hardware readiness is NO.

The closure contains 00021bbc, 00026474, 000264a0, 00026740, 00026944,
00026c78, 0005ca8c, 0005d66c, 0005d6ae, 0005d86e, 0005da24, 0005dc24,
0005dcfa, 0005ddc4 and 0005df48. All natural calls, returns and executed delay
slots retain stock instruction bytes. Full RAM, both bank outputs, fifteen
GPRs, actual prepared full SR, GBR, MACH, MACL, natural PR/SP, external ABI
and the 352-byte nested frame have independent expectations. The deepest
stock frame is 308 bytes; twelve lower guard bytes and thirty-two upper bytes
are also compared. Partial stores retain the untouched bytes: the word
ffff11bc stored at caller SP+2 precedes the byte ffff110e at SP+3.

## Simulation addresses

Forty-three declared long RAM pointers use the existing positive RAM mapping.
Seventeen word pointers bind the coherent overlapping workspace
ffff88b0..ffff89dd to 00005ffc..00006129. Every word alias has the same
translation, including nested and partly overlapping windows. The driver
compares all 302 shared bytes, thirty-two neighbors at either end, all 65536
ordinary RAM bytes and all 63998 bound bytes. Original instruction bytes are
unchanged; address pools alone carry documented simulator relocations.

## Transition-sensitive numerical view

closed_loop_fuel step 8 binds bank 1, x=0, from=uint16(ffff29e2), and
to=uint16(ffff40ac). The same arithmetic is checked independently with x=1,
from=uint16(ffff29e4), and output ffff40ae for the parallel bank. This second
software view does not add an ordered architecture step. The sign remains
none: mode and initialization choose independent alternatives, and the
transition detector can replace a selected value with 25600.

RAM operands refer to their exact reader phases. Prior transition flag
ffff88c0+B, count ffff88b8+2*B, previous control ffff88cd and history words
ffff88b4/ffff88b6 refer to the state before 0005ca8c. The control ffff14c1,
packet inputs ffff15da/ffff22e8, nominal ffff28b8+2*B and observed `from`
refer to the independent incoming packet values. The curve coordinate is
uint8(floor(uint16(ffff11bc)/2)); lookup(00023752,coordinate) uses the eight
byte points at axis 0002374a and exact stock directional integer rounding.
The transition threshold is ROM8[00008822] times that result. The unsigned
band endpoints wrap separately after subtracting ROM16[000092ee] and adding
ROM16[000092f0]. The inclusive interval and strict old-count threshold retain
their stock ordering, even when unsigned endpoint wrap reverses the interval.

Latch ffff88be+B, override flags ffff89da+B/ffff89dc+B, backup ffff8964,
disabled ffff8967+B, neutral ffff8965+B and elapsed ffff8969+B refer to their
current values after the real helper calls. The transition mask is derived
from the earlier packet and history equations, and is checked against the
published ffff8958+B. Selection uses, in order: an exact latch value of one,
first override ffff2a1e+2*B, second override ffff1628+2*B, transition neutral,
shared backup ffff8920, disabled neutral, neutral ramp ffff8922+2*B, elapsed
ramp ffff8926+2*B, and baseline ffff2898+2*B. An unset incoming bit 4 of
ffff88ec preserves the prior selected word ffff88b0+2*B. The final value is
max(ROM16[00008fc4],min(ROM16[00008fc6],selected)); the upper operation
precedes the lower operation. Values and flags at these reader phases are
defined by the complete independent memory equations.

## Literal domain and boundaries

The 1829 contexts comprise one zero baseline, all 256 initialization bytes,
eight patterned preservation contexts, 24 six-mask bank contexts, 312 elapsed
counter/divider boundaries, 240 transition-band/counter boundaries, all 256
coordinates of each of the two curves, 220 source-selection boundaries and
256 seven-source priority combinations. Ten final-source alternatives occur
across 3658 bank observations. The 220 boundaries use both banks and values
0, 19199, 19200, 19201, 25599, 25600, 25601, 31999, 32000, 32001 and 65535.
This domain is not the full Cartesian product of independent inputs.

Stock ROM8[000086f8]=255 fixes the neutral and elapsed ramp branch domain.
Other step calibrations, zero or negative divider denominators outside the
bounded real caller, arbitrary status bits outside the prepared contract,
interrupts, exceptions, peripherals and ISR/RTE paths retain identity-only
coverage. Physical units, upstream producers, event cadence, complete ECU
scheduling and engine reachability require separate evidence. The full
function proof establishes this explicit software invocation, with independent
incoming state, and does not establish those external paths.

The exact active-state argument and writer boundary is specified in
[`JK08A.closed-loop-feedback-accesses.md`](JK08A.closed-loop-feedback-accesses.md).
It uses the same whole-feedback code, overlapping workspace and observer,
with input-only raw observations, separate argument/store attribution and
complete native/TEST preservation.
