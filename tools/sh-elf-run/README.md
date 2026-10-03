# GNU SH-ELF firmware instruction verification

This directory is the mandatory independent executable gate for every firmware
patch that changes instruction bytes. It uses the GNU SH-2E assembler, linker,
and instruction-set simulator in a pinned Debian container rather than Ghidra
p-code.

The default gate is fully repository-contained. Verification of the separate
npkern project is optional, external, and revision-locked.

## Repository-contained gate

Run the complete current runtime gate from the repository root:

```bash
make verify-firmware
```

The first run builds the image defined by `Dockerfile`; later runs reuse Docker
layers. The runner selects the `default` Docker context without changing
the caller's configured context.

`VQ_SH_ELF_IMAGE` selects another compatible local image name.
`VQ_SH_ELF_SKIP_BUILD=1` skips the image build only when that image was already
built from the current Dockerfile.

The gate performs these checks:

1. Assemble every current Map Switching, Rolling Launch, and CAN telemetry
   source unit with GNU `sh-elf-as --isa=sh2e`. This covers the canonical JK08A
   units and every rendered JK00C, JK00D, JK78C, 1ND0A, 1ND3B, and 1ME3B
   target unit. A unit that includes a generated header of `patches/`, as the
   telemetry capture and control units include the profile identity
   `can-telemetry-identity.h`, reaches the assembler with the integer symbols
   of the header written as numbers; the telemetry harness compiles with
   `patches/` on its include path and installs the configuration record
   `TELEMETRY_CONFIGURATION` of the same header.
   Targets without a declared capability have no synthetic stage or payload.
2. Reconstruct each fill-aware ROM envelope and require byte identity with the
   corresponding SHA-locked payload in the tracked manifest.
3. Independently compose the current non-flashable capability-specific
   fixtures for JK08A, JK00C, JK00D, JK78C, 1ND0A, 1ND3B, and 1ME3B and
   enforce their declared write sets, entries, hooks, pointers, mailbox record,
   stock-image identity, and stage hashes. The SH7058 images are one MiB; the
   SH7059 1ND and 1ME3B images are 1.5 MiB.
4. Execute every declared Map Switching selector, adapter, limiter, startup,
   feedback, Rolling Launch behavior, telemetry HCAN1 initialization, control
   polling, runtime enable overrides, capture, bank publication, page request,
   ACK, abort, preemption, corruption, and ISR path with distinct fixture
   values that expose wrong slots or addresses. The 8MFK cases include both
   CVTC target families, the two-byte-aligned throttle limiter container,
   mailbox 26, and the stock-ISR tail chain. The 1ND cases include both fuel
   banks, both warm-idle banks, the shared cold-idle family, native fuel-cut
   caps and curves, the exact stock fuel-cut state machine, the throttle
   scalar, Rolling Launch final-mask coordination, mailbox 26, and the stock-ISR
   tail chain. JK78C executes the same VQ37 capability cases through its
   independent SH7058 addresses, stock hooks, RAM sources, and checksums.
   1ME3B executes them through its own SH7059 addresses with the target bit
   layout: the native fuel-cut state byte keeps the active and armed flags in
   bits 3 and 2. The ASCD cases of every target set the MAIN switch bit of the
   ASCD flag byte at the position of its layout: bit 7 on JK08A, JK00C, and
   JK00D, bit 4 on JK78C, bit 5 on 1ND, and bit 1 on 1ME3B. One selector case
   and one Rolling Launch gate case set every other bit of the byte, which
   neither aborts the selector nor fails the gate. The Rolling Launch
   fuel-cut flag cases set the active cut bit of the stock RPM fuel-cut state
   of each target: bit 2 on JK08A, bit 6 on JK00C and JK00D, and the active
   bit of the native rev-limit state byte on the VQ37 targets, bit 4 on
   JK78C, bit 5 on 1ND, and bit 3 on 1ME3B. One case sets every other bit of
   the byte, and on the VQ37 targets a final mask that inhibits all six
   cylinders, and requires the flag clear; the VQ37 fuel coordinator cases
   require the state byte unchanged. The VQ37 Rolling Launch hold cases run
   the engine and then the coordinator wrapper at engine speeds below, at, and
   above cut and at and below restore in both hold modes and in observe mode,
   and require the request, its latch, and the final mask of each pass: the
   request latches at cut, holds down to restore, releases below it, stays
   released between the thresholds, and latches again at cut; a latch other
   than 1 publishes no request; an abort clears the latch; and activation
   clears a latch left in IDLE at a saturated capture, whose captured speed
   lies between restore and cut. The telemetry knock surface cases set
   the high-detonation bit of the knock surface byte of each target, bit 6 on
   every target except 1ME3B and bit 7 on 1ME3B, whose capture moves it into
   wire bit 6 and clears the other bits of the wire byte; one case sets every
   other bit of the byte and requires wire bit 6 clear. The
   VQ37 ignition cases select all five slots of the two executed 16x16
   surfaces. The 1ND and JK78C cases pass the three equal-byte surfaces of the
   gated coordinator half, which the 1ME3B coordinator does not carry, through
   the adapter while a non-default slot is active. The harness
   names those three bases by the placeholders `0x0000991a`, `0x0000e91a`, and
   `0x0000ea1a`, which the target renderer rewrites to the profile symbols
   `ignition_gated_surface_1` to `ignition_gated_surface_3`. The 1ND and 1ME3B
   targets add the adapter of the four 8x8 state-code ignition surfaces: every slot and
   both invalid selector values of each family, plus one unknown base that must
   reach the stock 8x8 lookup unchanged. The harness names the four bases by
   the placeholders `0x0000f610`, `0x0000f710`, `0x0000f690`, and `0x0000f6d0`,
   and the stock 8x8 lookup is a return stub of the dynamic fixture. The three
   targets differ in adapter count and entry count; each
   marker carries its own values, and the verifier sums the case counts the
   markers report.
5. Apply only the documented simulator transformations after exact byte
   identity succeeds: high-RAM data-literal relocation and explicit stubs for
   unchanged stock callees outside the implementation under test. The Rolling
   Launch fixture uses a deterministic, PC-relative-alignment-aware stock
   serializer stub to seed the CAN payload before executing both feedback
   layers. The VQ37 fixture stubs the stock final-mask fuel coordinator with a
   deterministic routine that publishes a distinct base mask to the aliased
   final-mask byte and returns that byte zero-extended, so the wrapper return
   path is executed against an exact expected value. The telemetry fixture
   replaces the stock knock slice evaluator of every target with a stub that
   stores a staged 32-bit value at a staged address, counts the call, and
   overwrites `r0..r7`. The harness stages the offset-binary metric of the
   evaluated channel through the block at `0x0100ff00` of the test window, so
   a knock margin wrapper that reads its operands before the stock call, or
   that relies on a register across it, fails the case. The telemetry fixture
   also installs a simulator-only TRAPA vector after byte identity is proven.
   TRAPA creates the architectural exception stack. The canonical combined
   SLE1 ISR returns through its unchanged `RTE` instruction. Each 8MFK wrapper
   restores all interrupted registers, including `r0` in the `JMP` delay slot,
   and tail-chains to an explicit simulator-only `RTE` stub for the unchanged
   stock ISR. The same tail-chain boundary is executed for the VQ37 mailbox-26
   wrappers.
6. Execute the exact unsafe delayed-branch incident words at their ROM addresses
   and require an illegal-instruction stop, while a control fixture that changes
   only the delay-slot word returns normally.
7. Execute the stock instruction regions whose behavior the entity files state
   (`verify_stock_code.py`). The JK08A primary RPM producer
   `0x00038272..0x0003829d` and its unsigned divider
   `0x00021ce0..0x00021dc5` share an independent reconstruction at their
   stock addresses. The harness takes the mode flags, event interval,
   output word, and divider entry from the meaning files. It executes
   inhibit selection, zero-divisor recording, quotient truncation,
   saturation, and the unsigned word/longword divisor boundary. Direct
   divider entries also exercise the short-quotient branch, its boundary,
   and the maximum unsigned return value. Only the declared high-RAM
   pool words change in the simulator; both functions return through their
   stock instructions. The output window and mode flags retain all other
   bytes, and zero division writes the stock diagnostic record.
   The JK08A region `0x0003e1fe..0x0003e26b`
   contains the enabled non-fault arithmetic of the RPM-drop producer.
   Its GNU reconstruction links on `0x0003e1fc`, with two padding bytes
   outside the region, to preserve PC-relative longword alignment.
   `stock_invoke_gbr` supplies the aliased `satisfied-macaque/ram` address
   as GBR. The harness takes current speed, four-sample-old speed, and the
   preceding filter snapshot from the meaning addresses. Reviewed expected
   literals distinguish rising speed with nonzero history, equal speed,
   falling speed, truncation, and saturation; every neighboring byte stays
   unchanged. The only simulator changes are the high-RAM pool word and the
   RTS/NOP boundary at `0x0003e26c`; the arithmetic instructions stay stock.
   Mode selection, history shifting, and publication are outside this slice.
   The JK78C region `0x000fcbb0..0x000fcbed` of the
   ASCD task `0x000fb9c0` holds the coolant flag and the MAIN switch block.
   The verifier links its GNU reconstruction `stock_jk78c_ascd_main.s` at the
   region start and requires byte identity with the stock image for the region
   and the four pool words that it loads. The fixture aliases the two high-RAM
   pool words, places an RTS/NOP pair at `0x000fcbee` directly after the
   region, and keeps the region bytes stock. `stock_invoke.s` calls the region
   with R12 set to the stock pool literal that `0x000fc9ca` loads and with GBR
   0, as the stock firmware runs. The harness takes the address of
   `ascd_state/ram`, the mask of its named bit `main`, and the address of
   `button_state/ram` on the layout from the entity files and executes every
   branch outcome: the button source, the alternative source that bit 7 of the
   calibration byte `0x0000894f` selects, which the harness sets in the fixture
   for two cases and then restores, and both outcomes of the coolant threshold.
   Each case requires the MAIN bit to follow its source, the other bits of the
   flag byte to keep their values, and every other byte of the flag window to
   stay unchanged. The JK00C function `0x00050bf8..0x00050c99` and the JK00D
   function `0x00050bf4..0x00050c95` are the main RPM fuel-cut state machines
   of the two relocated 8MFK layouts. The reconstructions
   `stock_jk00c_rpm_fuel_cut.s` and `stock_jk00d_rpm_fuel_cut.s` hold each
   function and the five pool words that it loads; the fixture aliases the two
   high-RAM pool words, and the function returns through its own RTS, whose
   delay slot restores the GBR that it saves. The shared harness
   `stock_rpm_fuel_cut_harness.c` takes the address of `fuel_inhibit/ram`,
   the masks of its named bits `armed` and `active`, the engine speed word
   `rpm/ram`, and the threshold table `rev_limit_fuel_cut/tbl` from the entity
   files, and the delay counter, the pair selector, and the configuration and
   delay bytes, which no entity file names, from the region. It requires the
   stock configuration to select the pair by bit 4 of the selector, reads the
   thresholds from the fixture, and executes both pairs: speed below, at, and
   above the cut-on word with the arm clear and set, a zero and a nonzero cut
   delay counter, a nonzero delay byte that the harness sets in the fixture for
   one case and then restores, and speed at, above, and below the release word
   with the cut active. Each case requires both named bits, the delay counter,
   and the return value, the other bits of the state byte to keep their
   values, the engine speed word, and every other byte of the window around
   GBR to stay unchanged.

A successful run prints `VQ_SH_ELF_MAP_SWITCHING`,
`VQ_SH_ELF_ROLLING_LAUNCH`, `VQ_SH_ELF_ROLLING_VERIFY`,
`VQ_SH_ELF_CAN_TELEMETRY`, `VQ_SH_ELF_CAN_TELEMETRY_VERIFY`,
`VQ_SH_ELF_RUNTIME_TARGET`, `VQ_SH_ELF_RUNTIME_TARGETS`,
`VQ_SH_ELF_STOCK_CODE`, and `VQ_SH_ELF_VERIFY` markers with `status=PASS`. The markers calculate current
instruction, case, branch, relocation, and composition values at runtime; this
document does not duplicate them.

The target payload registry is a tracked product of the same pinned GNU
toolchain. Rebuild it after an intentional target-source or address-profile
change with:

```bash
make runtime-targets-generate
```

## External npkern gate

Run the external gate separately:

```bash
make verify-npkern
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

### Factory loader ABI

The CAN targets load through the factory reprogramming services `0x27`,
`0x34`, `0x36`, `0x37`, and `0xBF` of the stock diagnostic dispatcher, in that
order. The dispatcher selects each service handler with a PC-relative `mov.l`
from its literal pool:

| ROM | Dispatcher | SID | Literal-pool entry | Handler |
| --- | --- | --- | --- | --- |
| JK08A | `0x0002F928` | `0x27` | `0x0002FB44` | `0x00033578` |
| JK08A | `0x0002F928` | `0x34` | `0x0002FB5C` | `0x00034410` |
| JK08A | `0x0002F928` | `0x36` | `0x0002FB3C` | `0x000345F4` |
| JK08A | `0x0002F928` | `0x37` | `0x0002FB40` | `0x0003469C` |
| JK08A | `0x0002F928` | `0xBF` | `0x0002FB38` | `0x0003475C` |
| 1ND0A | `0x00035098` | `0x27` | `0x00035290` | `0x00039278` |
| 1ND0A | `0x00035098` | `0x34` | `0x00035294` | `0x0003A200` |
| 1ND0A | `0x00035098` | `0x36` | `0x000352C8` | `0x0003A494` |
| 1ND0A | `0x00035098` | `0x37` | `0x000352CC` | `0x0003A55C` |
| 1ND0A | `0x00035098` | `0xBF` | `0x000352C4` | `0x0003A624` |

`tools/tests/test_npkern_can_verifier.py` reads every row from the registered
stock image, requires the entry to hold the handler, and requires a `mov.l`
between the dispatcher entry point and the literal-pool entry to load it. Each
target in `verify_npkern_can.py` spans the loader-owned window from `origin`
to `boundary`, and its `aligned_limit` is that window rounded down to 32
bytes; the same test holds the relation.

## Simulator boundaries

GNU `sh-elf-run` cannot map the ECU high-RAM windows. The gate first proves the
original literal bytes, then aliases validated `0xFFFE8000..0xFFFFFFFF` data
literals into a 64-KiB test window by their low 16 bits. Instruction bytes and
control-flow addresses remain unchanged. This covers both the SH7058
`0xFFFFxxxx` application RAM and the SH7059 1ND and 1ME3B `0xFFFExxxx`
application RAM.

HCAN status registers are write-one-to-clear in silicon but ordinary memory in
the simulator. Canonical simultaneous mailbox-26/mailbox-28 ISR cases place the
two flags in independent TXACK1 and ABACK1 words, so both mailbox paths execute
in one TRAPA exception without modifying instructions under test. The 8MFK
and VQ37 tail-chain cases exercise mailbox 26 alone and together with unrelated
stock mailbox-28 flags, then verify the target wrapper's register-preserving
stock-ISR boundary.
Individual ACK and abort cases execute each custom write-one-to-clear
instruction and boundary path. Mailbox-31 cases likewise execute RXPR1, RFPR1,
and UMSR1 writes, including data, remote-only, retained-remote, malformed, and
invalid-configuration paths; the fixture observes the write values rather than
emulating their hardware clearing effect.

The simulator does not model HCAN-II, the SH7058/SH7059 flash controller, or the
external watchdog. The 1.5-MiB target harness places its test driver beyond the
complete ROM image; this relocation affects only harness code, not target
instructions. The npkern marker therefore remains
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
