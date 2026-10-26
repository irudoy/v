# Bounded JK08A closed-loop admission byte writers

`JK08A.closed-loop-admission.toml` binds two bounded input-decoding windows
of normalized parent `000A0EE8`.

## Exact windows and premises

Window `000A0F04`..`000A0F7E` decodes three independent unsigned raw
bytes at FFFF48C0, FFFF48BE and FFFF48B7. It reads the existing base
pointer, initializes its bank-loop registers and assigns two output
bytes per input. The outputs are workspace offsets2C/2D,2E/2F and30/31.

The second entry `000A0FFE` executes code spans
`000A0FFE`..`000A101C` and `000A102C`..`000A1036`. The literal gap
between those spans is data. This entry decodes independent raw byte
FFFF48B4 to workspace offsets39/3A. Its explicit incoming premises are
R8=1, R9=0 and R10=2. Both entries use GBR to address the
existing FFFF977C workspace. No low-memory domain or full prologue is
inferred from these premises.

For raw byte M and bank B=0 or1, the separate output equation is
`(M >> B) & 1`. The real loops retain their TST, BT/S delay-slot address
calculation, conditional BRA delay-slot one-store or zero-store, bank
increment and conditional repeat. The exact bank-2 destinations are
FFFF97A9, FFFF97AB, FFFF97AD and FFFF97B6. Their native symbols retain
unsigned8-bit semantic types. Bit0 changes the sibling-bank result;
bit1 changes the selected bank-2 result. Higher input bits do not supply
an additional output meaning.
