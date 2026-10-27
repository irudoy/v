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
Docker layers. `run.sh` selects the local `default` Docker context without
changing the caller's configured context. It mounts the checkout read-only.

The gate uses the patch layouts, payload manifests, runtime bindings and stock
ROM registry. It has no knowledge-package, graph, TEST witness or stock-proof
qualification dependency. Its successful terminal reports the patch stages and
executed cases. It does not publish evidence receipts or change canonical facts.

`VQ_SH_ELF_IMAGE` selects a compatible local image. Set
`VQ_SH_ELF_SKIP_BUILD=1` only when that image is already built from the current
Dockerfile. `VQ_SH_ELF_STOCK_TIMEOUT_SECONDS` retains the supported timeout
settings for the bounded ignition-consumer invocation; the script validates the
value before starting Docker. Compiler and assembler limits remain separate.

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

The canonical JK08A Rolling Launch harness measures `periodic_wrapper`,
`selector_arbiter`, `startup_wrapper`, `threshold_helper`, `feedback_arbiter`,
and `ignition_controller`
with the same host PC observer. Typed instruction statements define this scope; pools and fill
bytes do not count as instructions. Exact composed instructions and control
literals survive the declared fixture translations and match the final ELF
and invoke code. Each wrapper invocation retains its originating invoke frame
through calls and selector tail transfers, and qualifies its return only after
its declared stock RTS/NOP boundary. These boundaries do not qualify the stock
bodies.

The threshold helper accepts an originating invoke call or the exact bound
engine call window on an active engine frame. Its R3 divider load binds the
composed control pool before execution. Each helper invocation requires the
actual divider call and return followed by its native RTS to the original
continuation. Both outcomes of every helper branch and its delay slots must
execute; the engine and stock divider bodies receive no instruction-coverage
qualification.

The canonical-only `VERIFY_CANONICAL_ROLLING` build adds boundary
inputs for the exact floor, rounding transition, wide ramp and saturated upper
limit. Independent literal results specify the two output words. The complete
state, configuration, selector, shadows, runtime words, named input/output
buffers, stack pointer and GBR must otherwise remain intact. The observed R4
retains the configuration-pointer role exposed by `invoke_r4`; it is not a C
return-value contract. Relocated harness matrices and assertions are unchanged.

The feedback arbiter accepts only a bound invoke origin. Its literal R0 call
runs the existing Map Switching feedback wrapper before applying Rolling Launch
status. That call must return to its original continuation after an actual
nested call and return through the declared stock serializer fixture stub.
The arbiter must then execute its own native RTS and delay slot. These call
boundaries do not qualify the Map Switching or original stock function bodies.

Canonical feedback rows retain independent literal status and map-feedback
results, including an IDLE case with no failure reason and a held button.
They check every payload byte, the complete Rolling Launch and selector state,
configuration, pulse-count constants, concrete shadows and input/output
buffers, SP and GBR. Unconsumed Rolling Launch state bytes carry a distinctive
pattern. The existing case counter reports both canonical boundary matrices;
relocated feedback rows and assertions retain their original behavior.

The ignition controller inherits only the original invoke frame of the bound
ignition-adapter entry and its exact literal tail window. The controller's R3
divider call must return before its final stock tail, whose declared RTS/NOP
stub returns to that original invoke continuation. The adapter's alternate
stock tail has its own bound window; neither its other instructions nor the
stock divider body receive additional instruction qualification. Every typed
controller instruction and conditional outcome must execute. Inside the blend
path, BandStart < RPM < Cut implies Cut - BandStart >= 2.

Canonical ignition cases use independent literal output commands and check the
complete state, concrete buffers, configuration, SP and GBR. A negative build
sets the existing APC fallback input only for the zero-band case, bypassing
that real controller path while preserving its semantic assertions and case
count. Coverage must reject the omitted zero-band outcome.

A Rolling Launch negative build calls the engine directly instead of the
periodic wrapper, preserving ROM bytes, case counts and the semantic PASS
marker. Measured coverage must reject the omitted periodic entry. Coverage of
the engine and ignition-adapter bodies remains outside this bounded scope.

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
`control` units and the `capture`, `build_bank`, `knock_margin_wrapper` and
`request_page` regions of `capture`. Entries come
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
Coverage must reject the missing main entry, configuration-magic
outcome, zero-channel margin outcome, request invoke return, the context
clamp outcome or that capture validation outcome.

`request_page` accepts that direct invoke, the capture idle-publish BSR, and
the completion JSRs that load its entry. `build_bank` accepts its direct
invoke and the two capture BSRs. Those call instructions, their delay nops
and the completion entry literal stay bound to the composed image. The
surrounding capture and completion bodies are not qualified. `build_bank`
must execute both page and byte loops, both context seeks, the margin rearm
and both context-clamp outcomes. `request_page` must execute both bank
selections, the eight-byte copy loop and the return delay slot.

Completion, lower startup
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
