# GNU SH branch display limitation

Diagnostic `sh-elf-objdump -d` output from Debian `binutils-sh-elf 2.44+3+b1`
on the project's `linux/arm64` toolchain image prints incorrect targets for
negative BT, BF, BT/S and BF/S displacements. The instruction words assembled
by GNU match the expected encodings. Zero and positive displacement boundaries
display the correct target. This is a disassembly display limitation, not
evidence of a simulator or firmware execution defect.

The encoded target is `PC + 4 + 2 * signed8(opcode & 0xff)`. At `PC=0x128`,
`0x8bfa` therefore targets `0x120`; the affected disassembler prints `0x320`.
The display error for a negative displacement is `+0x200`.

The upstream `BRANCH_8` decoder sign-extends the displacement and then computes
`imm = ((char) imm) * 2 + 4`. With unsigned plain `char`, that narrowing
discards the sign extension. With signed plain `char`, it preserves the negative
value. This makes the display depend on the host configuration, even when the
SH target and binutils release are identical. The observed arm64 result matches
that unsigned-char arithmetic. See the
[binutils 2.44 decoder](https://sources.debian.org/src/binutils-gold/2.44-2/opcodes/sh-dis.c/#L524).

## Evidence boundary

Printed branch targets from the affected diagnostic disassembly are excluded
from control-flow evidence. Use the exact opcode's signed displacement, the
independently assembled source, and the executable gate's observed PCs and delay
slots to establish a transition.

The firmware gates do not consume instruction disassembly:

- `verify_map_switching.py` uses `objdump -h` for the linked text-section address.
- `verify_npkern_can.py` uses `-h`, `-t` and `-r` for section headers, function
  symbols and relocation records.

Those metadata queries do not use the affected branch-target formatter. Their
existing qualification remains unchanged. The host regression tests cover the
signed displacement boundaries and constrain gate consumers to metadata modes.
The toolchain image, assembler, simulator and runner retain their existing
contracts.
