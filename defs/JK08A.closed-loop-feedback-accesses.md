# JK08A feedback argument, active-state store and transition-counter boundary

`JK08A.closed-loop-feedback-accesses.toml` binds the complete natural
`0005CBEC` feedback invocation, the real active-state call to `0005D6AE`
and the transition packet/callee sequence `0005D66C`/`0005CA8C`.
The existing whole-feedback assembly, helpers, observer and independent
memory, frame and terminal equations retain their source identities.
No helper is replaced by its arithmetic result.

## Exact native transitions

`JK08A.closed-loop-feedback-arguments.toml` contains three exact original
helper-reader dispositions. Each becomes an owning `depends` relation with
role `arithmetic-argument`, through caller `0005CBEC` to `funky-toucanet/fn`.
It establishes a value argument under that real invocation, without inferring
a physical RAM reader inside the callee or an unrestricted absence of reads.

| Owner | Datum | Caller read | Argument |
|---|---|---|---|
| `fuzzy-mouse/ram` | `FFFF106E` byte | `0005CEDA` | Fifth argument, low byte of the word at caller SP |
| `raspberry-dragon/ram` | `FFFF1071` byte | `0005CEF2` | Full sign-extended R5 after the call delay slot |
| `rpm/ram` | `FFFF11BC` word | `0005CEE6` | Full sign-extended R7; the callee uses its unsigned low word |

The shared `JK08A.closed-loop-coordinate-access-claims.toml` contains twelve exact owning appends:
six retained coordinate relations, two feedback writers, two transition-counter relations
and two coolant constant readers described in `JK08A.closed-loop-coolant-accesses.md`.
The feedback stores at `0005D846` and `0005D84E` publish four bytes
to `FFFF895C` (`crazy-lynx/ram`) and `FFFF8960` (`arrogant-walrus/ram`).
The actual sixth-argument pointer binds both addresses. Physical four-byte
stores do not fill either owner's unset semantic width or signedness.


## Real argument carriers and output phase

The BSR at `0005CEF8` returns to `0005CEFC`. Its `MOV R0,R5` delay slot at
`0005CEFA` passes the sign-extended byte from `FFFF1071`. The word load at
`0005CEE6` supplies sign-extended R7. R4 contains the actual Boolean derived
from `FFFF4184.bit6`; R6 names the two current decoded bank bytes. R9 contains
the independently relocated `FFFF40B0` pointer at call entry.

The byte store at `0005CEE0` updates SP+3 with `FFFF106E`. Upper fifth-word
bytes retain the preceding partial stores. The delay-slot load at `0005D6D2`
reads that complete fifth word; the active path explicitly uses its low byte.
The full pointer store at `0005CEF4` and load at `0005D844` carry the sixth
argument through SP+4. Its observed alias is `000060A8`, corresponding to
`FFFF895C`. The two natural stores retain their exact order, datum, width and
value. RTS at `0005D868` and its restoring delay slot return to `0005CEFC`.
Nested SP, PR, GBR and full register arguments are independently checked.

Separate state equations retain the active latch, elapsed counter, old bank
criteria, current input bank bytes, byte-curve criterion, conditional
thresholds and delayed output phase. The two store values are checked at the
active-state phase, as well as within the final complete memory result.
The argument evidence does not substitute an argument value for an observed
load, and the writer evidence does not assign an input role to an output.

## Actual transition-counter phase

The two counter relations belong to
`closed_loop_feedback_transition_counter_b2/ram` at `FFFF88BA`, an unsigned
16-bit datum. Their exact reader and writer target is
`closed_loop_feedback_transition/fn` at `0005CA8C`. Both original TEST positions and the following spec position
remain in order. The two appends share one complete owner postimage; symbol,
layout, ledger, other links and existing physical scopes remain exact.

BSR `0005CC4C` enters the real packet `0005D66C` and returns to `0005CC50`.
The packet calls `0005CA8C` at `0005D696`, with return `0005D69A`. The actual
delay-slot word store at `0005D698` supplies the final observed bank word.
Exact nominal, observed and output pointers, full scalar arguments, nested
SP/PR/GBR, the output flag and natural returns at `0005CBE4` and `0005D6AA`
remain required. The existing word aliases bind the counter to `00006006`
and its bank flag to `0000600D` in the coherent shared workspace.

Counter values come from the independent `transition.before` phase after
the preceding helpers and packet stores. For software bank 2, the physical
consumer binds conditional reads at `0005CB30`, `0005CB7A` and `0005CB9C`,
the increment delay-slot store at `0005CBAA`, and the clearing store at
`0005CBBC`. Associated flag reads and writes retain their exact sequence,
byte/word widths, addresses and values. Separate equations bind all three
activation predicates, the byte-product threshold, inclusive lower/upper
band, counter increment or clear, and the resulting flag.

The guard at `5CB84` requires only its taken outcome under this exact natural
call. `EXTU.B` at `5CB20`/`5CB24` and `MUL.L` at `5CB26` bound the product
by 65025. `EXTU.W` and the comparison at `5CB36`/`5CB38` reject counts above
that product before the later counter read. No intervening count store
permits 65535 at the saturation guard. The original must observe the guard
and must not enter `5CB86..5CB92` (end exclusive). This premise grants no
general hardware, interrupt, scheduling or event-cadence claim.

## Existing observation and input-only domain


The input parser preserves 1829 legacy input contexts. It reads only the first
three input columns and the `inputs` byte-change array. Expected output
ranges, expected workspace bytes and CPU-result rows are not consumed or
compiled into the raw driver. Separate controlled contexts hold context,
seed, memory, frame and other inputs fixed while changing one source.
Unsigned word boundaries, full byte domains, old latch/count boundaries,
bank masks and current/previous control alternatives retain their explicit
software premises.
Additional stock-profile inputs retain unsigned counter threshold neighbors,
65534/65535, activation alternatives, and exact inclusive band endpoints
with their adjacent outside values. Counter positive alternatives compare
the actual transition-phase value and output. Only that input's bytes are
excluded from both complete ordinary and shared preimages; every other
input, context, calibration, frame and ABI remains fixed.

There are 18 controlled calibration bytes: the 16-point criterion table at
`00012312`, the threshold byte at `00008392` and the threshold byte at
`00008CD4`. Stock, ascending and descending profiles are explicit inputs;
controlled contrast grants no stock calibration or engine reachability claim.
All other bound bytes remain stock or exactly declared pointer aliases.
