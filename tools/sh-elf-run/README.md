# GNU SH-ELF firmware instruction verification

The firmware gate independently assembles and executes the instruction-changing
Map Switching, Rolling Launch and CAN telemetry patches. It also runs the
delayed-branch incident control and the consumers of redirected ignition lookup
literals. The GNU assembler, linker, compiler and simulator run in the pinned
container defined by `Dockerfile`.

## Run the patch gate

```sh
make verify-firmware
```

`make verify` includes this gate along with the repository checks and tests.
The first invocation builds the toolchain image; subsequent invocations reuse
Docker layers. `run.sh` and `generate-targets.sh` select the local `default`
Docker context and discard `DOCKER_HOST` for their child processes without
changing the caller's configured context. This keeps image builds, input-label
checks and execution on the same local daemon and image store.
`docker_lifecycle.py` also passes `--context default` for its Docker operations.
The daemon behind that context must provide the image validated below;
`DOCKER_HOST` does not select a rootless or remote daemon for this gate.
`run.sh` mounts the checkout read-only.

The gate uses the patch layouts, payload manifests, runtime bindings and stock
ROM registry. It has no knowledge-package, graph, TEST witness or stock-proof
qualification dependency. Its successful terminal reports the patch stages and
executed cases. It does not publish evidence receipts or change canonical facts.

`run.sh --rom <ROM>` executes only the stages that cover one supported ROM: the
native stages for a member of the exact family, whose members carry the same
payloads at the same addresses, or the runtime target of one relocated ROM. The
toolchain check and the delay-slot probe run in both scopes. The terminal line
names the scope as `scope=full` or `scope=rom:<ROM>`. `make preflash` runs this
scope for the ROM of the image it qualifies.

`run.sh --rolling-ignition` executes the dwell-veto kernel against the stock
unsigned divider. Its matrix checks eligibility, cylinder masks, accumulator
boundaries, counter wrapping, quiet events, the misfire latch and the complete
divider ABI. A PC trace requires every kernel instruction, both outcomes of
each conditional branch and every delay slot. The alias window is excluded
from the harness ELF and ROM fixture, with a compiled collision case that
must fail before simulator entry. The same scope executes both stock command
builders, the adapter and publisher, both stock schedulers, the command splitter
and phase normalizer. Its independent state model supplies complete publication
records and the effective argument for each consumer. A separate adapter trace
requires every instruction, both conditional outcomes and every delay slot.
The simulated upstream auxiliary gate selects the final-coordinate source at
`0x0008C3FA`; that function is outside the reconstructed ignition instructions.
The native pipeline requires this scope as its `rolling_ignition` stage.

The coupled fixture executes the original tooth countdown and set-arming
recovery, both complete `GR11A`/`GR11B` handlers, and the primary scheduler's
immediate recovery. Its phase-zero event model advances reference teeth over
the two omitted nominal positions, applies the selected `POPCR` actions to
ordinary pin-state memory, and services each compare through its original
handler. It checks both equal-time service orders, zero/partial/full cut
fractions, dwell boundaries and CANCEL release before arming, after selection
and after the dwell compare. A selected cut survives both recovery entries
and produces no successor dwell or spark edge. The builders also execute
phases 4 and 9 against the independently supplied consumer argument.
H9/H32 regression windows use representative stock commands from the hold
medians and every integer dwell in the reported 86..94 degree interval; these
rows bound the scheduling defect and do not replay measured coil edges.
A negative fixture defers the veto until `GR11A` and must fail on the extra
dwell edge at command 120 and dwell 90.

The tooth fixture preserves its original prologue and epilogue. Declared
simulator-only jumps at `0x00028ECC` and `0x000295B8` enter the context at
`0x00108400` and the observation tail at `0x00108500`; the stock instructions
under test are `0x000292EC..0x000295B8`. Crank decoding and unrelated tooth
dispatch are excluded. The observation code reads the publication tuple
before the bounded body and the actuator counters before returning, so an
engine recovery after return cannot erase the observed event. The fixture
checks that every ROM difference belongs to these declared exclusions or
the auxiliary stub.

Instruction-boundary IRQ rows inject the real tooth entry at each executed
publication store and interrupt-mask change of a steady RPM pass and a
CANCEL-release pass. Each row requires a coherent consumed q, the correct
event count and decision, the engine's final q and preserved ABI, the stock
RTE and its slot, and one completed entry/return report. The declared
downward stack excludes ELF storage; a compiled collision must refuse before
execution. These rows enter from the main loop and use one maskable IRQ.
The event model supplies no cycle timing, peripheral arbitration, electrical
coil behavior or vehicle acceptance.

`VQ_SH_ELF_IMAGE` selects the local image tag. `VQ_SH_ELF_SKIP_BUILD=1` reuses
that tag without building it; the image input check below still applies.
`VQ_SH_ELF_STOCK_TIMEOUT_SECONDS` retains the supported timeout
settings for the bounded ignition-consumer invocation; the script validates the
value before starting Docker. Compiler and assembler limits remain separate.

## Image inputs

`Dockerfile` binds the base image to a multi-platform index digest. Every stage
resolves packages from fixed `snapshot.debian.org` snapshots of the Debian and
Debian security archives. The toolchain stage installs exact versions of
binutils, GCC, newlib and Python, and the observer stage builds the simulator
from a checksummed GDB release. A rebuild without the layer cache resolves the
same packages. A package version changes together with the snapshot timestamps
that provide it.

`image_inputs.py` names the Dockerfile and every local file that it copies. Their
SHA-256 fingerprint is the `vhrev.sh-elf-run.inputs` image label, and every gate
build applies it. Before creating a container, the runner reads the image ID and
this label from one inspection. An absent or different label refuses the run
with `VQ_SH_ELF_LIFECYCLE status=REFUSE kind=stale`, also when the build is
skipped; otherwise the container starts from that image ID.

`generate-targets.sh` builds the same labeled image, honours
`VQ_SH_ELF_SKIP_BUILD=1` in the same way, and applies the same input check
through `docker_lifecycle.py --identify`, which prints the verified image ID
or refuses a stale image before execution. The target generator runs from that
image ID with the invoking user's UID and GID, so the files that it writes in
the checkout belong to that user.

`generate-targets.sh --telemetry` writes the canonical JK08A telemetry payload
manifest and refuses when a lock of the telemetry layout differs from the
assembled bytes. `--telemetry --update` derives those locks, rewrites them in
the layout, and writes both files only after the strict generation passes
against the rewritten layout. `make telemetry-update` runs it after the profile
projection checks and then regenerates the relocated target payloads.

## Executable boundary

The canonical and relocated runtime verifiers:

- Assemble the patch sources independently with GNU SH-2E tools and compare
  their complete output with the declared machine-code payloads.
- Compose each supported target against its exact stock image and check write
  sets, hooks, entries, pointer tables and mailbox configuration.
- Execute selector, adapter, limiter, startup, feedback, Rolling Launch,
  telemetry capture, control and interrupt paths with distinct fixture values.
- Exercise relevant branch outcomes, delay slots, call/return paths and boundary
  inputs. Capability-specific target harnesses retain their own assertions.
- Execute the original unsafe delayed-branch pair and a safe control fixture.

The canonical JK08A map-switching harness measures executed PCs and opcodes
for `startup_wrapper`, `limiter_commit`, `selector_host`,
`cruise_feedback_wrapper`, `cruise_feedback_engine`, the canonical lookup adapters
and their shared helper, and the bounded throttle-cluster prefix. Its observer records the
actual delay-slot execution order. The verifier requires every instruction, both
conditional outcomes, and matched calls and returns in this scope. It binds
the trace to the independently assembled payload, the composed ROM, and the
final ELF; simulator RAM-literal translations preserve instruction words.
Before execution, the common map binding also compares JSR/JMP ROM pools and
adapter entry R3 stock-target pools with the composed image. Control targets
come from those composed bytes. Declared RAM data operands retain their fixture
aliases.
The ordinary GNU toolchain includes the optional host observer. Trace requests
cover the declared canonical, JK00C, JK00D, JK78C, 1ND0A and 1ND3B scopes, with no target-state instrumentation.
The displaced stock host, serializer and initializer retain their existing
RTS/NOP fixture stubs; this coverage does not qualify their original bodies.

Independent negative builds suppress the actual `run_limiter_cases()`,
`run_adapter_cases()`, `run_selector_cases()` or `run_feedback_cases()` call while
retaining the same ROM bytes and semantic PASS prefix. Each build must fail
coverage at its exact omitted startup, helper, selector or feedback-wrapper entry.
Case totals are reporting metadata. Coverage of the remaining
payloads, targets, and other SH7058 limiter-pointer consumers remains outside this
bounded check. Case and entry totals printed by the other harnesses do not
establish instruction coverage.

The adapter scope uses entries from the layout's existing code regions,
including each entry inside the shared lookup-adapter assembly unit. Instruction
requirements use typed instruction statements alone; pools, pointer tables and
fill bytes do not contribute to instruction coverage. The checker validates
actual BRA and JMP successors against the independently bound operands.

Each adapter binds R3 through its entry's original PC-relative stock-wrapper
load. The shared helper inherits that exact origin; other R3 uses or unsupported
transfer forms fail verification. A tail transfer preserves the originating
invoke frame. Entries visited on that frame qualify their return only when the
bound stock RTS/NOP stub reaches the original invoke continuation. These stubs
do not qualify the stock lookup bodies.

The selector matrix used by canonical, JK00C, JK00D, JK78C, 1ND0A and 1ND3B builds declares the expected published state, observed R4
and whether a limiter write is permitted. Blocked and aborted gestures require
untouched shadows and throttle runtime; normalization commits are explicit.
Feedback rows declare state, payload and observed R4 independently. Zero-pulse
feedback clears its own transient state while preserving the selector and stock
payload. These R4 observations use the fixture's invoke helper. Case totals for
canonical, JK00C, JK00D, JK78C, 1ND0A and 1ND3B builds do not gate acceptance; other relocated targets retain
their existing matrices and checks.

The relocated map verifier measures JK00C, JK00D, JK78C, 1ND0A and 1ND3B through the existing
target compile and run path. Typed instructions and entries come from every declared map unit
and code region. The secondary CVTC adapter uses its local selection and R3 tail
paths; it does not require a visit to the shared adapter helper. The target's
word-copy limiter and state-writing serializer fixture retain their exact
declared transformations. Guard cases use the rendered target addresses and
independent state, return and write-effect oracles.

Relocated targets carry no Rolling Launch stage; their telemetry composes on
the map stage.

JK00C, JK00D, JK78C, 1ND0A, 1ND3B and 1ME3B telemetry measure the projected wrappers, control handler, capture
regions, completion body and the mailbox-26 SLE1 tail. The tail jumps to the
stock ISR stub and does not qualify that body. Omitting the main wrapper,
invalid configuration, zero-channel margin, direct page send, saturated bank
context, invalid capture configuration, idle acknowledgement or the SLE1
entry fails at that entry or outcome.

JK78C uses its declared second idle-ignition entry and alternate fuel-compensation
selection. Its leaf limiter copies the native fuel caps, both curves and the
throttle scalar. The existing C oracle checks the complete shadows against
distinct selected ROM sources and requires the throttle runtime to remain
untouched. Selector and feedback guards use the target's ASCD mask and addresses.
Native fuel-cut calls retain their existing state and threshold assertions;
the stock fuel-cut and interpolation bodies receive no instruction qualification.

The SH7059 1ND0A and 1ND3B layouts additionally declare an ignition state-code
adapter. Its entry binds R3 to the composed stock-lookup pool; local selection
and both JMP tails retain that exact owner and the originating invoke frame.
The stock RTS/NOP boundary must return to the original continuation. Existing
C rows independently check each selected state-code family, invalid indices,
unknown-table pass-through and memory guards. Each ROM runs against its own
composition and requires its own measured terminal.

JK00C, JK00D, JK78C, 1ND0A and 1ND3B require typed, composed and fixture context, final ELF/invoke binding,
complete observer records and the measured coverage terminal. Four actual
omission builds must fail at their exact target entries despite semantic PASS.
No canonical stock-consumer window runs on JK00C, JK00D, JK78C, 1ND0A or 1ND3B. Other ROMs and feature gates
retain their existing execution checks and receive no measured qualification
from these JK00C, JK00D, JK78C, 1ND0A and 1ND3B map scopes.

The canonical JK08A Rolling Launch gate measures the regions
`periodic_wrapper`, `selector_arbiter`, `startup_wrapper`, `engine`,
`speed_controller`, `feedback_arbiter`, `rpm_controller`, `rpm_fraction`,
`control_publisher`, `ignition_publisher`, `actuation`, `slot_validator` and
`state_check` with the same host PC observer. Typed instruction statements of
their units define this scope; pools and fill bytes do not count as
instructions and must not execute. The gate does not execute the ignition
adapter or the spark-cut actuator, so an image that contains them stays
ineligible for hardware testing until their executable coverage exists.

`rolling_launch_rows.py` derives every row from the schema 6 model in
`patches/rolling_launch.py` and renders it as the C header that
`rolling_launch_harness.c` includes; the verifier compiles the harness once
for each row set. Engine rows reject each check of the configuration head,
the five map slots and the efficiency table alone, cross the gates at their
boundaries, activate both regulator kinds, and run the ACTIVE transitions, both
controllers and their saturations, the ready holds, the cooldown and its
re-arm, and the recovery from every failing check of the record. Publisher
rows run the ignition and control publishers, and fraction rows the RPM
fraction at its soft-width boundaries. Five fixed cases run the startup
wrapper and the selector arbiter in each phase, and eight cases run the
feedback arbiter.

Each row writes its configuration record and its efficiency table into the
simulator ROM image at the addresses of the Rolling Launch layout,
`0x000D6320` and `0x000D6390`, which changes no instruction byte, and its
base record, extension and inputs into test RAM. The feedback cases also
write the two phase counts of the Map Switching feedback engine, one pulse
each, at its layout address `0x000D3848`. The verifier passes these three
layout addresses to the compiler, and the harnesses define no copy of them.
The harness fills the rest of the 64 KiB test RAM with a pattern and, after
the call, compares all of it with the expected image: the output records of
the row, the map 1 limiter commit of a corrupt-state recovery, the
diagnostic status mirror `0xFFFF2A84` of the map selector host, and no other
byte. Every selector case seeds the mirror with `0xA5`; the IDLE case starts
the SET gesture, and the host mirrors map 1 as a clear bit 7, `0x25`. The
configuration, the table and the phase counts must stay unchanged.

`invoke_rolling.s` is a simulator-only call helper. `invoke_regs` loads
`r1..r14` and the T, S, I, Q and M bits of SR from a register array, calls
the entry through `r0`, and stores `r0..r14` and SR back; the simulator keeps
its other SR bits, which later SR transfers need. The harness seeds every
register that an entry does not take, and every call checks `r8..r14`, SP,
GBR and the SR bits of its contract. The publishers run alternately at
SR = 0 and with every loadable SR bit set and must restore the SR of their
caller.

The fixture stubs the displaced periodic task `0x000A9554`, the stock ASCD
host `0x000D09D8`, the startup initializer `0x0002C648` and the primary
ignition consumer `0x0002A892` with RTS/NOP. The stock feedback serializer
`0x000C5372` is a stub that stores `0xB5` in the ASCD status byte
`0xFFFF3ADA` and returns. The stock unsigned divider `0x00021CE0` runs
unstubbed. The idle selector path runs the Map Switching selector host. None
of these executions qualifies a stock or Map Switching body.

The trace must match the fixture opcodes and execute every instruction of
the scope, counting executions in a delay slot, both outcomes of every
conditional branch, every delay slot, and every call with its return to the
call continuation. The targets of a register transfer come from a backward
walk of the control-flow graph of its unit: every path must end at a
PC-relative long load of the transfer register, and a path that reaches
another write of that register, a call or the unit entry leaves the transfer
unbound. Execution must reach every such target and no other. The invoke
helper may call only the harness entries, and an RTE fails the trace.

Three negative row sets keep the semantic PASS marker and remove one covered
path each: the periodic row calls the engine directly, the lower-limit
integrator row of the speed controller stays above the limit, and the
cooldown rows with an invalid configuration or table are omitted. The
verifier collects every unmet obligation of each variant. The periodic
variant must leave exactly the obligations of the periodic wrapper unmet,
its entry first; the controller and engine variants must leave exactly the
omitted outcome of the integrator lower-limit branch and of the cooldown
validity branch unmet, together with the obligations of the block that only
this outcome reaches: from the fall-through to the next label, or through
the delay slot of the next unconditional transfer.

The interrupt rows inject the crank-tooth publication into engine passes
through the optional interrupt hook. `rolling_launch_rows.interrupt_scenarios`
defines six passes, which `rolling_launch_irq.c` runs at SR.I = 0 through
`invoke_regs`: steady ACTIVE ready holds of both kinds, an activation of each
kind from an IDLE record that keeps a map index, a law output 0 and a control
error of an earlier hold, an abort and corrupt-state recovery. A run without
a request records the PC trace. A publication and a pass observe each other
only through memory, so the interleavings of one publication with a pass are
the points after its first instruction and after each of its loads and
stores. One run requests vector 80 at level 8 after every store that a pass
executes, inside and between its masked groups, and one more after the first
of the other instructions that share each further acceptance point. The
simulator-only handler `irq_rolling.s` records its entry SP, the address of
the interrupt frame, saves `r0..r7`, PR, MACH, MACL and GBR, runs the
ignition publisher at SR.I = 8 with the wide S and P of the scenario,
restores them, stores a return marker and returns with RTE. The verifier
derives the acceptance point from the trace: the first later boundary at
SR.I below 8 that follows no delay slot and no LDC, STC, LDS or STS. An
executed `ldc r0,sr` after `or #0xf0,r0` masks, and every other LDC to SR
restores the level of the pass. The report must hold one entry row that
names that point and the handler, so a request inside a masked group is
accepted only after the instruction that follows the LDC that lowers the
mask, and one return row that resumes at that point with SP eight bytes
above the recorded frame. A PENDING or UNRETURNED report fails the run.

Each injected run must return through the handler with `r8..r14`, SP, GBR
and SR preserved, leave the output of every other pass unchanged, store the
model publication of the record pair that the handler observes, and leave
the records of a publication before or after the pass. Corrupt-state
recovery clears both records after its check, so it may also leave the
records of the pass without a publication. In a steady pass every
publication passes the check and publishes P with the ready mark. The RPM
activation has at least one publication between its error pair and the
publisher mask, and each publishes the stock command: the status view keeps
kind NONE of the IDLE record until the masked wire views at the end of the
pass. Across the observed records, an activation changes only the sample,
the gate flags and the abort reason before the phase, stores the mode after
the map, the law output before the kind and the trim of the run last; an
abort changes only the sample before the phase, and recovery changes no
record field before it. Neither publishes P after its phase store.

The canonical JK08A harness also executes the fuel-cut state-machine consumer
of the redirected limiter pointer. Its independent assembly binds the original
instruction window and operand pools before execution. The fixture translates
only the bound state-base, threshold-pointer and RPM-base RAM words; all tested
instructions and their original addresses remain intact. Cases populate the
selected shadow through the real limiter entry and check thresholds, state,
timer, return value, stack, GBR and memory guards.

The canonical harness executes the redirected throttle-scalar clamp at its
original instruction addresses. Independent reconstruction binds its unchanged
instructions, the composed pointer and the original observation-boundary bytes.
The fixture translates only the bound RAM pointer and replaces instructions
after the clamp with RTS/NOP to observe R4 and SR. Cases use the selected shadow
and check unsigned comparisons, results, preserved SR bits, stack, GBR and memory
guards. The scalar invoke helper is bound to its independently assembled bytes
in the final ELF. These functional checks do not establish consumer PC coverage.

The redirected `rev_throttle_cluster_base` consumer executes its original
prologue and prefix at `[0x7584e,0x7587a)` and epilogue at
`[0x75c32,0x75c48)`. Independent assembly binds both instruction windows and
four original operand pools to the stock and composed images. Only the bound
request-base and cluster-pointer data words receive simulator RAM aliases.
A GNU-assembled BRA/NOP boundary at `[0x7587a,0x7587e)` replaces the first two
enabled-body instructions and reaches the original epilogue without changing R0.
All tested instruction bytes and the boundary are checked after other stubs.
The coverage result counts payload and original consumer words as `instructions`.
It reports executed simulator-only boundary words separately as
`fixture_boundary_instructions`; both sets retain their execution requirements.

Cases commit each selected bank through the real limiter entry, preseed the
shadow with the opposite sentinel and make the old ROM source contradict the
committed word. They check the prefix's R0 probe, request and memory guards,
read-only shadow and restored stack. The PC checker requires both actual BF
successors and the non-NOP store and register-pop delay slots. R0 observes the
stopped prefix's caller-saved register; it is not a return value of the stock
void function. An unchanged request on the enabled path establishes only the
absence of a write before the boundary. The remaining enabled body, its calls
and its final request remain outside this executable scope.

The canonical JK08A CAN telemetry gate measures the existing `wrappers` and
`control` units, the `capture`, `build_bank`, `knock_margin_wrapper` and
`request_page` regions, and the `sle1_isr` and `completion` regions. Entries come
from the telemetry layout and the named internal configuration-validator label.
Typed instruction statements define coverage;
source tables, pools and fill remain data. Independent GNU assembly, composed
ROM, simulator fixture, final ELF and invoke code bind the measured PCs.
ROM call pools are checked against the composition before tool execution;
declared RAM operand aliases remain permitted.

The local checker requires every instruction, both BT/BF outcomes, exact
BRA/BSR/JSR targets, real delay slots and matched invoke continuations. The
internal configuration validator must return from each of its typed RTS sites
to each parsed BSR caller. The margin evaluator call must reach its bound ROM
target and return from the declared simulator stand-in's RTS to the wrapper.
Canonical probes check exact allowed state and mailbox deltas, preserved
neighboring bytes, mixed flag sentinels, init result and stack.
Alias-memory flag checks observe the written values, without modeling hardware
write-one-to-clear behavior. The existing C case counter reports all canonical
probes; measured execution provides instruction qualification.

Margin probes stage the evaluator metric independently and compare literal
expected latch values for selector choices, channel bounds, threshold equality,
signed minima and clamp boundaries. They check the complete allocated telemetry
state and restored stack. The evaluator stand-in writes the staged metric,
clobbers caller-saved registers and counts its actual invocation; its bytes and
return site bind the call without qualifying the stock evaluator body.

Private negative harnesses preserve the same linked ROM, semantic output and
assertions. One bypasses `MAIN_WRAPPER` with real `CONTROL_POLL` and `CAPTURE`
calls. Another skips only the invalid-magic poll invocation while retaining its
case count and no-side-effect assertions. A margin build invokes the evaluator
stand-in directly for the ignored zero-channel case, retaining its actual call,
case count and unchanged-state assertions. A request build copies the eight
mailbox bytes in the harness instead of either direct `request_page` invoke.
A bank build keeps the direct call but supplies context 0 instead of the
saturated context, so the clamp that clears a context of 5 or more does not
execute. A capture build skips the call whose configuration magic is wrong,
so the first validation branch to the shared return does not execute.
An ISR build clears both mailbox-28 abort sources, so the abort
fall-through does not execute. A completion build keeps the idle-ack
assertions but omits that call, so the busy check does not fall through.
The ISR enters from the TRAPA vector and leaves with
RTE; the following harness instruction is outside the ROM trace. Its BSR
into completion is a measured call and return. Coverage must reject
the missing main entry, configuration-magic outcome, zero-channel margin
outcome, request invoke return, the context clamp outcome, the capture
validation outcome, the ISR abort outcome or the idle-ack outcome.

`request_page` accepts that direct invoke, the capture idle-publish BSR, and
the completion JSRs that load its entry. `build_bank` accepts its direct
invoke and the two capture BSRs. Those call instructions, their delay nops
and the completion entry literal stay bound to the composed image. `build_bank`
must execute both page and byte loops, both context seeks, the margin rearm
and both context-clamp outcomes. `request_page` must execute both bank
selections, the eight-byte copy loop and the return delay slot.
The completion body must execute both ack and abort outcomes, including an
ack while idle, an abort while not busy, and an abort of a corrupt queue.
Its queue check and bank toggle are in the same measured span. Direct
completion invokes must return to an invoke word.

Lower startup
and stock callee bodies remain outside CAN instruction qualification. Existing
TRAPA/RTE cases execute as separate harness calls; exception behavior receives
no additional qualification from this scope.
Unsupported transfers during an active monitored frame fail verification.

The ignition-consumer verifier reconstructs each declared stock call window
and its operands independently. It then executes the real composed lookup
literal through the injected adapter. Its C harness checks complete callee and
return register state, SR, stack arguments, caller ABI, frame contents, RAM and
observation guards for valid and invalid selector inputs. The patch-only mode
retains these assertions and emits the completion marker without raw evidence
snapshots.

The unchanged lookup body is an explicit observation stub. A separate return
boundary restores the continuation outside the instruction windows under test.
Both modifications are checked for overlap, and every tested instruction keeps
its stock bytes. `patches/ignition_literal_consumers.py` declares the required
consumer windows and rejects omitted or changed literal operands.
The reconstruction and lookup stubs embed only their linked `.text` section;
the default GNU linker script's loadable `.stack` section is outside the
fixture content. The stubs retain their declared stock entry addresses.

## Container lifecycle and results

The standard-library container runner serializes one gate per checkout and
checks Docker state before building or creating a child. A live matching child,
an ambiguous state or a surviving child after client loss refuses another run.
It never removes unrelated containers or changes system sleep settings.

Owner, attempt and container records live under `tmp/local-results/sh-elf-run`.
A configured results-directory link may point to another disk; nested links
cannot escape that destination. The container exposes that destination read-only
at its actual path so checkout-relative links remain valid. The original runtime
terminal binds the image identity, checkout, attempt, exact container and observed
stopped or absent state.

Stage records include elapsed time and successful or failed terminals. A partial
stream or an unfinished stage does not establish a completed verification.

## Simulator boundaries

The verifiers compare original instruction and operand bytes before applying
declared simulator-only RAM translations and stock-function stubs. The
translations leave instructions and control-flow addresses under test unchanged.
Harness storage is separate from ROM, target RAM and observation windows.

`gnu16.3-sh-high-ram-alias.patch` supplies an optional host-side data-memory
alias for exact stock instruction paths whose operands lie in
`0xFFFF0000..0xFFFFFFFF`. With `VQ_SH_HIGH_RAM_BASE=0x01000000`, an aligned
access uses flat storage at `0x01000000 + (address & 0xFFFF)`. The base must
be nonzero, aligned to 64 KiB, and leave the complete window inside the
simulator's allocated flat memory. An invalid setting refuses execution.
An unset variable retains the original special-address behavior. Unaligned
accesses retain their bus error, and instruction addresses and instruction
bytes are unchanged. Mapped peripheral registers are ordinary fixture memory;
the alias does not supply peripheral behavior or interrupt scheduling.

The `simulator_memory` stage executes the alias probes before any patch gate.
It checks the disabled default for each access width and direction, enabled
byte/word/long access and target byte order, sign extension, both window
boundaries, invalid bases, unaligned accesses and an address outside the window.
The enabled setting is confined to the probe subprocesses; other gates retain
the unset default unless their own fixture explicitly declares the alias.
Before any probe executes, its ELF load segments and allocated sections must
exclude the complete alias window and the adjacent probe canary. A fixture
that enables the alias declares and checks its own ELF and harness storage;
the simulator patch itself has no ELF ownership model.

## Optional SH-2E interrupt injection

`gnu16.3-sh-irq-injection.patch` adds a one-shot maskable CPU interrupt request to the
standalone GNU runner. A publication-race fixture can run an interrupt
handler after a selected store of an unmasked engine pass. With all
`VQ_SH_IRQ_*` variables unset, instruction
execution, exception handling and the PC observer retain their ordinary
behavior. A request supplies all of these variables:

| Variable | Value |
| --- | --- |
| `VQ_SH_IRQ_PC` | An even 32-bit instruction address in hexadecimal, with an optional `0x` prefix |
| `VQ_SH_IRQ_COUNT` | A decimal execution number, at least 1, within an unsigned 64-bit value |
| `VQ_SH_IRQ_LEVEL` | A decimal priority level from 1 to 15 |
| `VQ_SH_IRQ_VECTOR` | A decimal vector number from 0 to 255 |
| `VQ_SH_IRQ_REPORT` | The path of the request report |

The request becomes pending after completion of the selected execution of
the instruction. A delayed branch completes with its executed delay slot;
a trigger on the slot also becomes pending after that slot. Both outcomes
of `BT/S` and `BF/S` retain the protected slot. Pending delivery waits until
the first instruction boundary where `SR.I < LEVEL` and interrupt acceptance
is allowed. It occurs before execution of the instruction at that boundary.

The [SH7059/SH7058S Hardware Manual](../../refs/renesas-sh7059-sh7058s-hardware-manual.md),
section 6.6, table 6.10, prohibits acceptance between a delayed branch and its
slot, and immediately after `LDC`, `LDC.L`, `STC`, `STC.L`, `LDS`, `LDS.L`,
`STS` and `STS.L`. The FPU instructions in its tables 2.18 and 2.19 also
inhibit acceptance. Section 6.6 accepts an interrupt when an instruction
that permits acceptance is decoded. The instruction following an inhibiting
instruction therefore executes before deferred acceptance. Consecutive
inhibiting instructions extend this deferral. For `ldc ...,sr; nop; resume:`,
a pending request is accepted at `resume`, even when the LDC lowers the mask.

At acceptance, the hook writes SR at `SP-4`, the return PC at `SP-8`, sets
SP to `SP-8`, and sets `SR.I` to the requested level. It reads the handler
from `mem32[VBR + 4*VECTOR]` at acceptance, including any intervening change
to VBR or the vector entry. Entry validates stack alignment and address
arithmetic. Memory accesses use the ordinary data paths; their bus faults
stop the run. The handler runs
from its original instruction address; no target opcode is replaced.

GNU's RTE decoder uses the SH-4 SSR/SPC return registers. For the RTE ending
this hook's injected exception, with GNU's BL bit clear, the hook reads PC
and SR from the current SH-2E stack frame, advances SP by eight bytes, and
supplies those return registers to the unchanged decoder. RTE and its delay slot execute normally;
a probe verifies that the slot observes the restored stack pointer.
At entry the hook saves the surrounding GNU SSR/SPC pair and restores it
after the injected RTE and its slot complete. An ordinary GNU TRAPA inside
the handler sets BL, so its RTE uses GNU's decoder without consuming the
injected frame. IRQ entry clears GNU's BL tag only in the handler SR; the
frame retains it, so the injected RTE restores BL in the outer ISR. Probes
cover an IRQ inside a GNU TRAPA ISR that opens its mask by read-modify-write
while retaining BL, the outer ISR tail and caller SR, and a GNU TRAPA inside
the injected handler. A frame inside GNU TRAPA retains the GNU MD/RB/BL
bits, which do not exist on SH-2E.
This compatibility does not qualify SH-2E TRAPA semantics or other simulator
exception paths. The hook supplies no peripheral behavior,
INTC arbitration, nested maskable IRQ requests or cycle timing. Each fixture
declares its stack, vector and harness storage separately from executable storage.

An accepted and returned request writes two report lines with hexadecimal values:

```text
triggered=00001200 accepted=00001202 handler=00001400 sr=00000000
returned=00001202 sp=00017ff0
```

`triggered` is the configured instruction address; `accepted` is the return
PC placed in the frame, which can differ from the instruction immediately
following the trigger. The `returned` row records the frame consumed and
the restored SP before GNU executes RTE. Successful completion of RTE and
its slot is required separately: a delivered request without that completion
adds `status=UNRETURNED`. An undelivered request, including an execution count
that is never reached, writes `status=PENDING`. Either status changes an
otherwise successful runner exit to 125 and retains an existing target
failure or signal. Partial or invalid requests refuse execution with exit code 125;
report I/O errors fail the run with that code. The ordinary PC trace remains
an ordered record of the instructions that execute, including the handler,
RTE and its delay slot.

The mandatory `simulator_irq` stage runs the compiled C and assembly probes
before patch execution. It checks the unset default, repeated executions,
priority masking, inhibit chains, delayed branches, the saved frame, RTE,
both GNU TRAPA nesting orders, exit without return, a fault in the RTE slot,
vector lookup at acceptance, undelivered requests and invalid settings.
Disabled and enabled runs consume the same ELF bytes. Requests are confined
to child processes; the probe uses ordinary flat memory without enabling a
high-RAM alias.

The simulator does not reproduce the complete ECU, peripherals, power sequence
or engine. HCAN write-one-to-clear registers behave as ordinary memory in the
fixture. The exception model does not establish the silicon exception stack.
These limitations remain relevant to the hardware gates; a software pass alone
does not establish readiness to flash.

## Optional external npkern gate

```sh
make verify-npkern
```

`run-npkern.sh` accepts only the declared external checkout and exact revision.
It does not fetch, clone, choose a mirror or modify that project. A missing
checkout reports a skip; a dirty tree or a different revision is a failure.
`VQ_NPKERN_SOURCE` selects the checkout location. The external gate independently
builds and executes its CAN parser, transport and flash-boundary harnesses.

The repository patch gate remains independent of that checkout. To request both
through the shell entry point, use `run.sh --with-npkern --verbose`.

## Instruction-changing patches

A patch extends this gate in the same change as its executable instructions.
It binds exact emitted bytes to an independently assembled or reconstructed
fixture and executes every changed entry, relevant branch outcome, delay slot,
call/return path and boundary. Redirected literal words require their actual
consumers to execute. Simulator relocations and stubs are explicit and leave the
instruction bytes under test unchanged. A simulator limitation requires equivalent
executable coverage before hardware testing.
