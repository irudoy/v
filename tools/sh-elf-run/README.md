# GNU SH-ELF firmware instruction verification

This directory is the mandatory independent executable gate for every firmware
patch that changes instruction bytes. It uses the GNU SH-2E assembler, linker,
and instruction-set simulator in a pinned Debian container rather than Ghidra
p-code.

The default gate is fully repository-contained. Verification of the separate
npkern project is optional, external, and revision-locked.

## Repository-contained gate

Run the complete current JK08A gate from the repository root:

```bash
tools/sh-elf-run/run.sh --verbose
```

The first run builds the image defined by `Dockerfile`; later runs reuse Docker
layers. The runner selects the `default` Docker context without changing
the caller's configured context.

`VQ_SH_ELF_IMAGE` selects another compatible local image name.
`VQ_SH_ELF_SKIP_BUILD=1` skips the image build only when that image was already
built from the current Dockerfile.

The gate performs these checks:

1. Assemble every current Map Switching, Rolling Launch, and CAN telemetry
   source unit with GNU `sh-elf-as --isa=sh2e`.
2. Reconstruct each fill-aware ROM envelope and require byte identity with the
   corresponding SHA-locked payload in the tracked manifest.
3. Independently compose the current non-flashable one-MiB Map Switching,
   Rolling Launch, and CAN telemetry fixtures and enforce their declared write
   sets, entries, hooks, pointers, mailbox record, and instruction audits.
4. Execute every declared Map Switching selector, adapter, limiter, startup,
   feedback, Rolling Launch behavior, telemetry HCAN1 initialization, control
   polling, runtime enable overrides, capture, bank publication, page request,
   ACK, abort, preemption, corruption, and ISR path with distinct fixture
   values that expose wrong slots or addresses.
5. Apply only the documented simulator transformations after exact byte
   identity succeeds: high-RAM data-literal relocation and explicit stubs for
   unchanged stock callees outside the implementation under test. The Rolling
   Launch fixture uses a deterministic stock-serializer stub to seed the CAN
   payload before executing both feedback layers. The telemetry fixture also
   installs a simulator-only TRAPA vector after byte identity is proven. TRAPA
   creates the architectural exception stack, then the exact combined SLE1 ISR
   returns through its unchanged `RTE` instruction.
6. Execute the exact unsafe delayed-branch incident words at their ROM addresses
   and require an illegal-instruction stop, while a control fixture that changes
   only the delay-slot word returns normally.

A successful run prints `VQ_SH_ELF_MAP_SWITCHING`,
`VQ_SH_ELF_ROLLING_LAUNCH`, `VQ_SH_ELF_ROLLING_VERIFY`,
`VQ_SH_ELF_CAN_TELEMETRY`, `VQ_SH_ELF_CAN_TELEMETRY_VERIFY`, and
`VQ_SH_ELF_VERIFY` markers with `status=PASS`. The markers calculate current
instruction, case, branch, relocation, and composition values at runtime; this
document does not duplicate them.

## External npkern gate

Run the external gate separately:

```bash
tools/sh-elf-run/run-npkern.sh --verbose
```

Or request it after the repository-contained gate:

```bash
tools/sh-elf-run/run.sh --with-npkern --verbose
```

The default checkout is `../../oss/npkern` relative to this repository.
`VQ_NPKERN_SOURCE` may point to another checkout, but `run-npkern.sh` requires
that path to be the Git root, at the exact revision embedded in the script, and
completely clean. It does not fetch, clone, select a mirror, or modify the
external project.

If the checkout is absent, the external command reports `status=SKIP` and
`hardware_ready=NO`. A wrong revision, nested Git root, or dirty tree is a hard
failure. The repository-contained gate remains independent of npkern
availability.

The npkern verifier builds exact-address SH7058 and SH7059 CAN targets in
read-only and explicitly write-enabled configurations, executes parser,
ISO-TP, and flash-boundary fixtures, checks production-to-simulator byte
identity outside declared relocation literals, and verifies the unchanged
legacy SH7058 K-line target.

## Simulator boundaries

GNU `sh-elf-run` cannot map the SH7058S `0xFFFFxxxx` RAM window. The gate first
proves the original literal bytes, then relocates only those validated data
literals to test RAM. Instruction bytes and control-flow addresses remain
unchanged.

HCAN status registers are write-one-to-clear in silicon but ordinary memory in
the simulator. Simultaneous mailbox-26/mailbox-28 ISR cases place the two flags
in independent TXACK1 and ABACK1 words, so both mailbox paths execute in one
TRAPA exception without modifying instructions under test. Individual ACK and
abort cases execute each write-one-to-clear instruction and boundary path.
Mailbox-31 cases likewise execute RXPR1, RFPR1, and UMSR1 writes, including
data, remote-only, retained-remote, malformed, and invalid-configuration paths;
the fixture observes the write values rather than emulating their hardware
clearing effect.

The simulator does not model HCAN-II, the SH7058/SH7059 flash controller, or the
external watchdog. The npkern marker therefore remains
`hardware_ready=NO`. Repository firmware fixtures also do not emulate the full
ECU, power sequencing, analog inputs, or engine.

Passing this gate proves a bounded software execution contract. It does not
make an image eligible for flashing without static review and the project's
bench, readback, and engine validation gates.

## Adding an instruction-changing patch

The same change that introduces a patch must extend this gate. Its verifier
must:

1. Independently assemble the source or reconstruct declared raw words and
   prove identity with the exact instructions emitted into the ROM.
2. Execute every changed entry and reachable branch outcome, including delay
   slots, call/return paths, failure paths, and relevant boundary inputs.
3. Use distinct fixture values where equal production defaults could conceal a
   wrong address, slot, width, or branch.
4. Declare simulator-only relocations and stock-function stubs, apply them only
   after byte identity, and leave instructions and control-flow addresses under
   test unchanged.
5. Add deterministic host-side tests and make `run.sh` execute the new
   repository-contained check.

A simulator limitation is not a waiver. Until an equivalent executable check
exists, the image remains ineligible for hardware testing.
