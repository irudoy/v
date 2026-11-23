# JK08A paired flag writer withdrawals

Source bindings: `JK08A.paired-inhibit-writer-withdrawal-paths.toml`.


## Complete natural entries and actual helper

The two caller bodies retain 7C8FA..7C9A8 and 7C9A8..7CA58. The complete
7D84C..7D856 helper reads 5B33, masks its low nibble and publishes the byte
in its real RTS delay slot. Each caller retains its complete prologue, PR/GBR
saves, flag gates, natural BSR, post-delay helper arguments, helper return,
epilogue and natural return. No instruction, conditional outcome or delay slot
is excluded. The 11 two-sided conditions require both feasible outcomes.



## Ordered physical read/modify/write operands

All 28 physical RMW sites retain two ordered operands at the same actual
instruction address: a byte read followed by a byte write. Every OR.B uses
mask 04 and every AND.B uses mask BF. The seven OR offsets from native GBR
5718 are 1F/22/25/28/2B/2E/31; the seven AND offsets are
20/23/26/29/2C/2F/32. The unmodified input byte, modified byte, address,
width, direction, register absence and RAM domain remain exact. One terminal
byte, one combined event or a reversed pair cannot replace the physical pair.
Independent scalar equations compose both ordered operands without decoding
the instruction bytes. Every preserved unmasked bit remains part of the input.

The 7C8FA caller retains its 41C5/41CF gates, 5B2C blocker, 41D4 mask DF,
5B2B mask BF, 5B2A mask FB and 41C1 mask FD. Its actual stores clear byte
4AC6 at 7C96C, byte 4A45 at 7C970, word 4A70 at 7C974 and byte 48C2.
These stores remain required. They cannot establish a writer relation for
the separate 7C9A8 function.

The 7C9A8 caller retains its 41D8/41BB gates, 5B2C blocker, 41D4 mask F7
and separate 5B2B masks EF/7F. Its actual stores clear bytes 4AC8/4A47,
word 4A74 and byte 48C4. Both 3118 and configuration 885D are MOV.B
sign-extended to complete 32-bit register words before unsigned CMP/HS.
A negative promoted threshold is not an unsigned byte threshold. Equality,
positive/negative cross-boundaries and both branch outcomes remain explicit.

Both callers retain the 5B33 high-bit blocker and bit-20 helper gate. The
blocker branch delay slot preserves the actual raw byte in R2. The real
7D84C helper preserves its exact low-nibble return, byte publication and
natural post-delay continuation. No helper or return stub is used.
