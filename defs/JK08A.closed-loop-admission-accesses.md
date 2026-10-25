# Bounded JK08A closed-loop admission byte writers

`JK08A.closed-loop-admission.toml` binds two bounded input-decoding windows
of normalized parent `000A0EE8`. The existing complete
`stock_jk08a_closed_loop_adjustment.s` and its legacy full-entry harness
remain unchanged. This component uses the existing 80-byte context and
572-byte complete observer inside the same original COPY primary.

## Exact windows and premises

Window `000A0F04`..`000A0F7E` decodes three independent unsigned raw
bytes at FFFF48C0, FFFF48BE and FFFF48B7. It reads the existing base
pointer, initializes its bank-loop registers and assigns two output
bytes per input. The outputs are workspace offsets2C/2D,2E/2F and30/31.

The second entry `000A0FFE` executes code spans
`000A0FFE`..`000A101C` and `000A102C`..`000A1036`. The literal gap
between those spans is data. This entry decodes independent raw byte
FFFF48B4 to workspace offsets39/3A. Its explicit incoming premises are
R8=1, R9=0 and R10=2. Both entries require GBR=0100977C, the relocated
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

## Independent observation boundary

Only pointer pool000A114C changes from FFFF4558 to01004558. The four
displacement words remain stock, and the observed byte00008E78 preserves
the existing assembly origin. The declared pools contain13 bytes.
Independent SP+24/R7 observing returns at000A0F7E and000A1036 lie outside
every tested code span and pool. Each return is separately assembled
from `publication_inhibit_snapshot_return.s` and must equal
57F6472A000B0009. Tested stock instructions retain their exact bytes.

Required component `closed_loop_admission_paths` records independent raw
mask bytes and complete entry contexts without expected output values.
Full-byte input sweeps, separate low-bit combinations, SR alternatives
and a second complete context feed independent instruction-state and
scalar/physical consumers. Every original invocation retains all RAM,
sibling bytes, canaries, GPR/SR, MACH/MACL/GBR, complete frame, outer ABI,
calibration bytes, terminal SP/PR and observing continuation. Every mask
and loop branch needs both outcomes. Each bank-2 writer requires positive
raw-input/output alternatives with every other input fixed.

## Exact owning publication

`JK08A.closed-loop-admission-access-claims.toml` contains four exact
original writer relations in four complete owner documents. The existing
writer requires four exact ordinary `link` appends together. One reserved
`closed-loop-admission-access` item attaches to each existing writer.
The existing reader relation, symbol evidence and TEST positions, native
types, properties and absent ledger remain exact. A unique append is
neutral to existing physical scopes only with its complete pinned
canonical relation digest. Changed, duplicate or misplaced items retain
their scope effect. Full publication comparison, TEST-origin equality
and exact COPY/injection/coherent/SID22 scope equality remain required.

The owning proof supports access identity only. It supplies no complete
adjustment entry, integrator update, physical permission, source producer,
engineering units, scale, scheduling or hardware qualification. The
full-entry contract in `JK08A.closed-loop-adjustment.md` retains its
separate evidence obligations. Source preparation does not qualify an
original pending review.
