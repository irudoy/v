# GNU SH-ELF firmware instruction verification

This directory is the mandatory independent executable gate for every current
or future firmware patch that changes instruction bytes. It uses the GNU SH-2E
assembler, linker, and instruction-set simulator from Debian trixie instead of
Ghidra p-code. The registered verifiers cover the complete JK08A map-switching
implementation, its default-disabled Rolling Launch extension, and the external
npkern SH7058/SH7059 CAN targets.

Run the complete gate from the repository root:

```bash
tools/sh-elf-run/run.sh --verbose
```

The first run builds `vq-sh-elf-run:16.3`. Later runs reuse Docker layers. Set
`VQ_SH_ELF_IMAGE` to select a compatible local image. Set
`VQ_SH_ELF_SKIP_BUILD=1` only when that image was already built from this
Dockerfile. The runner exports `DOCKER_CONTEXT=desktop-linux` and removes
`DOCKER_HOST`, so it does not depend on or change the caller's active Docker
context. The npkern tree defaults to `../../oss/npkern` relative to this
repository; `VQ_NPKERN_SOURCE` selects another checkout.

The gate performs six independent checks:

1. GNU `sh-elf-as --isa=sh2e` assembles nine map-switching and three Rolling
   Launch source units. Explicit instruction and data bytes are reconstructed
   over each declared `0xFF` envelope and must be byte-identical to the
   SHA-locked Ghidra payloads.
2. Those independent bytes build two exact non-flashable one-MiB compositions.
   Map switching locks 435 instruction placements and twelve entries. Rolling
   Launch extends only that exact endpoint and locks another 755 instruction
   placements, five entries, nine diagnostic pointers, and a 1876-byte write
   set before any simulator-only transformation.
3. The GNU-assembled bytes build the final six cumulative hardware-overlay
   compositions independently of the tracked payload bundle. Stages 15 through
   17 each contain 156 instruction placements while the full-DFCO payload and
   hooks are introduced. Stage 18 contains 324 instruction placements with the
   selector host active but CAN feedback absent. Stage 19 contains 418
   instruction placements and retains the hardware-tested 10/10-frame CAN
   feedback timing. Stage 20 contains all 435 instruction placements, adds the
   two idle-ignition families, changes the timing to 15/15 frames, and must equal
   the independently composed complete twelve-family runtime endpoint. The exact
   hardware-output hashes are locked by the overlay builder.
4. `sh-elf-run` executes 229 behavior cases. Map switching retains its 131
   adapter, limiter/startup, selector, and feedback cases. Rolling Launch adds
   98 structural, gate, configuration, activation, active-state, cooldown,
   ignition, and wrapper cases. Every declared implementation entry executes.
   Map copies receive distinct simulator-only values so a wrong slot cannot
   pass merely because all initial copies equal Map 1. Only documented stock
   callees outside the implementations are replaced with `RTS/NOP` stubs.
5. A separate ELF places the exact failed Overlay 07 words `AFAC D304` at
   `0xD2314`. GNU simulator 16.3 must stop with signal 4. A control ELF at the
   same addresses replaces only `D304` with `NOP` and must return normally.
6. `verify_npkern_can.py` builds the exact-address SH7058 and SH7059 CAN kernels
   in both flash-read-only and explicitly write-enabled configurations. It
   executes 15 read-only parser cases, 23 write-enabled parser cases, and 16
   ISO-TP cases from the same relocatable objects used by the production ELFs.
   Ten additional guards execute the exact SH7058/SH7059 flash-write boundary
   paths without touching unmodeled flash-controller registers.
   Every non-relocated byte is required to match between the production and
   simulator links. Linker-address literals are the only declared relocation.
   The same verifier builds a deterministic legacy SH7058 K-line image and
   locks both its binary hash and the unchanged legacy parser source, so the
   CAN split cannot introduce an unverified K-line firmware change.

GNU simulator cannot map the SH7058S `0xFFFFxxxx` RAM window because its SH
memory implementation accepts at most a 31-bit address space. The gate first
proves the original high-address literal bytes against the tracked payloads,
then relocates only those validated `.long` data literals to a dedicated
`0x01000000` test region. Instruction bytes and control-flow addresses remain
unchanged. This is an implementation-level ECU fixture, not peripheral or
whole-firmware emulation.

The npkern verifier has an additional explicit limitation. GNU `sh-elf-run`
does not model HCAN-II, the SH7058/SH7059 flash controller, or the external
watchdog circuit. The verifier builds and audits those drivers but does not
execute their register interactions. Its PASS marker therefore includes
`hardware_ready=NO`; the generated kernels remain ineligible for hardware use
until passive capture and bench validation close that gap.

## Adding an instruction-changing patch

The change that introduces a patch must also extend this gate. The verifier for
that patch must:

1. Independently assemble the source or reconstruct the declared raw machine
   words, then prove byte identity with the instructions emitted into the ROM.
2. Execute every changed entry and reachable branch outcome, including all
   delay slots, call/return paths, failure paths, and relevant boundary inputs.
3. Use distinct fixture values wherever equal production defaults could conceal
   an incorrect address, slot, width, or branch selection.
4. Declare every simulator-only relocation and stock-function stub, apply them
   only after byte identity is established, and leave the tested instruction
   bytes and control-flow addresses unchanged.
5. Add deterministic host-side tests for the verifier and make the top-level
   `tools/sh-elf-run/run.sh` command execute the new check.

A simulator limitation is not a waiver. Until an equivalent executable check
exists, the resulting image must not be described as ready for hardware or
supplied for flashing. Passing this gate does not model ECU peripherals, prove a
complete reset sequence, or replace bench and engine validation.

A successful run includes all six primary markers:

```text
VQ_SH_ELF_OVERLAYS status=PASS stages=6 stage15_instructions=156 stage16_instructions=156 stage17_instructions=156 stage18_instructions=324 stage19_instructions=418 stage20_instructions=435 ...
VQ_SH_ELF_MAP_SWITCHING status=PASS cases=131 selector=17 adapters=91 limiter=14 feedback=9 feedback_invocations=17 entries=12
VQ_SH_ELF_ROLLING_LAUNCH status=PASS cases=98 structural=11 gates=25 config=22 activation=5 active=9 cooldown=5 ignition=15 wrappers=6 entries=5
VQ_SH_ELF_ROLLING_VERIFY status=PASS units=3 instructions=755 ... diagnostics=9 ...
VQ_SH_ELF_VERIFY status=PASS ... hardware_overlay_stages=6 rolling_launch_instructions=755 rolling_launch_cases=98 ... unsafe_signal=4
NPKERN_LEGACY_BUILD status=PASS target=SH7058_KLINE ...
NPKERN_CAN_VERIFY status=PASS targets=4 legacy_targets=1 ... flash_guard_cases=10 hardware_ready=NO limitation=HCAN_and_flash_peripherals_not_executed
```
