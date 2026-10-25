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

All ten preceding complete coordinate/publication reference records have
independent retention pins, including the six original coordinate records.
All 37 calculation identities retain their exact pins, including the prior
34-identity boundary; the calculation registry contains 38 dispositions. Every full native
preimage and proposed postimage retains other links, reverse structural
properties, symbol/layout/type data, ledger positions and TEST origins.
The existing unsigned 16-bit RPM and transition-counter types remain exact;
the other four semantic types remain unset. Ordinary appends and calculation dispositions use their
existing complete batch and publication operations. Exact existing physical
scope equality remains mandatory. Owning evidence supplies identity only.

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

The unit contains 3067 instructions and 63998 bound code/pool bytes. Its
43 long pointer aliases and 17 word pointer aliases retain the existing
coherent translation. The shared workspace has 302 bytes at
`FFFF88B0..FFFF89DE`, observed at `00005FFC..0000612A` (end exclusive), with 32 canary bytes
at each end. Ordinary 64 KiB RAM is observed separately. Its unaliased copy
of the workspace remains unchanged; only the independently observed shared
bytes overlay the logical memory used by the consumers.

The existing observer has a 76-byte incoming context, an 892-byte result and
a 352-byte frame at SP-320..SP+31. Full incoming registers, actual prepared
SR, exit registers, natural PR/SP, external ABI, MACH, MACL, GBR, frame,
ordinary RAM, shared memory, canaries, controlled calibrations and all bound
code/pool bytes are recorded before and after execution. Extended frame and
shared-workspace interpretation in the independent instruction engine
requires the exact feedback descriptor, unit, aliases and storage premise.
Other descriptor paths retain their existing frame and memory boundaries.

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

## Independent admission and refusals

The `closed_loop_feedback_paths` capture joins the same complete COPY primary
through its binding in the existing ordinary registration. The
registration contains thirteen ordinary families and forty-seven capture bindings.
No new mode, common dispatch route, observer, ISA or storage allocator is
defined. Existing complete-primary capture presence remains structural;
the independent domain consumer must establish
`exact_feedback_arguments`, `exact_feedback_stores` and
`exact_transition_counter_accesses`.

Complete natural instruction state, the existing independent memory equations,
separate nested-frame equations and terminal-register equations must agree
with the actual original. The physical consumer requires the exact ordered
caller reads, partial fifth-byte store, full fifth-word load, sixth pointer
carriers, post-delay arguments, two phase-correct stores and natural return.
All 27 required active-state and transition conditional sites require both feasible outcomes.
The separate saturation guard retains its exact bounded taken premise.
Each argument needs fixed-other alternatives that change a separate active
state result after its own input bytes are excluded from the comparison.
Each writer needs a changed actual store value with the bank input changed
and every other complete input fixed.
The counter reader needs a changed counter/flag result under fixed-other
counter alternatives; the writer needs a changed actual store under
fixed-other flag alternatives. Both ordinary and native mirrors retain
the same exclusion, and the physical counter datum remains phase-specific.

Regression sources retain complete native/type/TEST/scope and old-reference
boundaries. They reject missing or stale originals, altered code/pools/aliases,
changed toolchain or invocation streams, changed complete memory/CPU/frame/ABI,
workspace or canary changes, reordered carriers/stores, altered full signed
arguments, pointer substitutions, natural-return changes, transition phase or
counter/flag substitutions, saturation escapes, changed original TEST/spec
positions and missing independent
domain flags. Controlled metadata tests grant no executable admission.

This boundary establishes no upstream producer, physical units, calibration
suitability, event cadence, complete ECU scheduling, interrupts, peripheral
effects, hardware eligibility or engine behavior. Source preparation does not
close an original review or constitute executable acceptance.
