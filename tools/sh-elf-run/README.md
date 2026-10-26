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
