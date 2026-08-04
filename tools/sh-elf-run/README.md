# GNU SH-ELF map-switching verification

This directory provides an independent executable gate for the complete JK08A
map-switching implementation. It uses the GNU SH-2E assembler, linker, and
instruction-set simulator from Debian trixie instead of Ghidra p-code.

Run the complete gate from the repository root:

```bash
tools/sh-elf-run/run.sh --verbose
```

The first run builds `vq-sh-elf-run:16.3`. Later runs reuse Docker layers. Set
`VQ_SH_ELF_IMAGE` to select a compatible local image. Set
`VQ_SH_ELF_SKIP_BUILD=1` only when that image was already built from this
Dockerfile. Docker's standard `DOCKER_CONTEXT` variable selects a non-default
local context when required.

The gate performs four independent checks:

1. GNU `sh-elf-as --isa=sh2e` assembles all seven source units. Explicit
   instruction and data bytes are reconstructed over each declared `0xFF`
   envelope and must be byte-identical to the SHA-locked Ghidra payloads.
2. Those independent bytes build the exact non-flashable one-MiB composition.
   Its SHA-256, write boundary, 387 instruction placements, and ten entries are
   locked before any simulator-only transformation.
3. `sh-elf-run` executes 87 behavior cases: 47 adapter cases, 14 limiter and
   startup cases, 17 selector cases, and nine feedback sequences containing 17
   wrapper invocations. Every declared implementation entry executes. Map
   copies receive distinct simulator-only values so a wrong slot cannot pass
   merely because all initial copies equal Map 1. Only documented stock callees
   outside the implementation are replaced with `RTS/NOP` stubs.
4. A separate ELF places the exact failed Overlay 07 words `AFAC D304` at
   `0xD2314`. GNU simulator 16.3 must stop with signal 4. A control ELF at the
   same addresses replaces only `D304` with `NOP` and must return normally.

GNU simulator cannot map the SH7058S `0xFFFFxxxx` RAM window because its SH
memory implementation accepts at most a 31-bit address space. The gate first
proves the original high-address literal bytes against the tracked payloads,
then relocates only those validated `.long` data literals to a dedicated
`0x01000000` test region. Instruction bytes and control-flow addresses remain
unchanged. This is an implementation-level ECU fixture, not peripheral or
whole-firmware emulation.

A successful run ends with both markers:

```text
VQ_SH_ELF_MAP_SWITCHING status=PASS cases=87 selector=17 adapters=47 limiter=14 feedback=9 feedback_invocations=17 entries=10
VQ_SH_ELF_VERIFY status=PASS ... unsafe_signal=4
```
