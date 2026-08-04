# GNU SH-ELF firmware instruction verification

This directory is the mandatory independent executable gate for every current
or future firmware patch that changes instruction bytes. It uses the GNU SH-2E
assembler, linker, and instruction-set simulator from Debian trixie instead of
Ghidra p-code. The registered verifiers cover the complete JK08A map-switching
implementation and its default-disabled Rolling Launch extension.

Run the complete gate from the repository root:

```bash
tools/sh-elf-run/run.sh --verbose
```

The first run builds `vq-sh-elf-run:16.3`. Later runs reuse Docker layers. Set
`VQ_SH_ELF_IMAGE` to select a compatible local image. Set
`VQ_SH_ELF_SKIP_BUILD=1` only when that image was already built from this
Dockerfile. Docker's standard `DOCKER_CONTEXT` variable selects a non-default
local context when required.

The gate performs five independent checks:

1. GNU `sh-elf-as --isa=sh2e` assembles eight map-switching and three Rolling
   Launch source units. Explicit instruction and data bytes are reconstructed
   over each declared `0xFF` envelope and must be byte-identical to the
   SHA-locked Ghidra payloads.
2. Those independent bytes build two exact non-flashable one-MiB compositions.
   Map switching locks 414 instruction placements and eleven entries. Rolling
   Launch extends only that exact endpoint and locks another 751 instruction
   placements, five entries, nine diagnostic pointers, and a 1876-byte write
   set before any simulator-only transformation.
3. The GNU-assembled bytes build the final five cumulative hardware-overlay
   compositions independently of the tracked payload bundle. Stages 15 through
   17 each contain 156 instruction placements while the full-DFCO payload and
   hooks are introduced. Stage 18 contains 324 instruction placements with the
   selector host active but CAN feedback absent. Stage 19 contains all 414
   instruction placements and must equal the independently composed complete
   ten-family runtime endpoint. The exact hardware-output hashes are locked by
   the overlay builder.
4. `sh-elf-run` executes 210 behavior cases. Map switching retains its 116
   adapter, limiter/startup, selector, and feedback cases. Rolling Launch adds
   94 structural, gate, configuration, activation, active-state, cooldown,
   ignition, and wrapper cases. Every declared implementation entry executes.
   Map copies receive distinct simulator-only values so a wrong slot cannot
   pass merely because all initial copies equal Map 1. Only documented stock
   callees outside the implementations are replaced with `RTS/NOP` stubs.
5. A separate ELF places the exact failed Overlay 07 words `AFAC D304` at
   `0xD2314`. GNU simulator 16.3 must stop with signal 4. A control ELF at the
   same addresses replaces only `D304` with `NOP` and must return normally.

GNU simulator cannot map the SH7058S `0xFFFFxxxx` RAM window because its SH
memory implementation accepts at most a 31-bit address space. The gate first
proves the original high-address literal bytes against the tracked payloads,
then relocates only those validated `.long` data literals to a dedicated
`0x01000000` test region. Instruction bytes and control-flow addresses remain
unchanged. This is an implementation-level ECU fixture, not peripheral or
whole-firmware emulation.

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

A successful run includes all five markers:

```text
VQ_SH_ELF_OVERLAYS status=PASS stages=5 stage15_instructions=156 stage16_instructions=156 stage17_instructions=156 stage18_instructions=324 stage19_instructions=414 ...
VQ_SH_ELF_MAP_SWITCHING status=PASS cases=116 selector=17 adapters=76 limiter=14 feedback=9 feedback_invocations=17 entries=11
VQ_SH_ELF_ROLLING_LAUNCH status=PASS cases=94 structural=11 gates=24 config=22 activation=5 active=9 cooldown=4 ignition=13 wrappers=6 entries=5
VQ_SH_ELF_ROLLING_VERIFY status=PASS units=3 instructions=751 ... diagnostics=9 ...
VQ_SH_ELF_VERIFY status=PASS ... hardware_overlay_stages=5 rolling_launch_instructions=751 rolling_launch_cases=94 ... unsafe_signal=4
```
