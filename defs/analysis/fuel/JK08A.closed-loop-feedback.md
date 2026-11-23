# JK08A bounded whole feedback calculation

## Bounded feedback

The natural entry 0005cbec executes both bank state paths and fifteen real
helpers.

The closure contains 00021bbc, 00026474, 000264a0, 00026740, 00026944,
00026c78, 0005ca8c, 0005d66c, 0005d6ae, 0005d86e, 0005da24, 0005dc24,
0005dcfa, 0005ddc4 and 0005df48.

## Transition-sensitive numerical view

closed_loop_fuel step 8 binds bank 1, x=0, from=uint16(ffff29e2), and
to=uint16(ffff40ac). The parallel bank uses x=1,
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
from the earlier packet and history equations and published at ffff8958+B. Selection uses, in order: an exact latch value of one,
first override ffff2a1e+2*B, second override ffff1628+2*B, transition neutral,
shared backup ffff8920, disabled neutral, neutral ramp ffff8922+2*B, elapsed
ramp ffff8926+2*B, and baseline ffff2898+2*B. An unset incoming bit 4 of
ffff88ec preserves the prior selected word ffff88b0+2*B. The final value is
max(ROM16[00008fc4],min(ROM16[00008fc6],selected)); the upper operation
precedes the lower operation.
## Literal domain and boundaries

Stock ROM8[000086f8]=255 fixes the neutral and elapsed ramp branch domain.
Other step calibrations, zero or negative divider denominators outside the
bounded real caller, arbitrary status bits outside the prepared contract,
interrupts, exceptions, peripherals and ISR/RTE paths retain identity-only
coverage. Physical units, upstream producers, event cadence, complete ECU
scheduling and engine reachability require separate evidence.
