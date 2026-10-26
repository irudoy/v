# JK08A pedal snapshot and high-state quantity

Component `pedal_snapshot_high_state_paths` binds 613 stock instructions in
7 stock entry paths and 9 code spans, 58 literal pools, 21 four-byte RAM aliases
and 89 calibration spans. The comparator root uses 28 stack bytes. Its 30 raw
ROM controls and 16-byte uniform curve retain their complete physical bytes.

The first stage reuses the exact registered `jk08a-coherent-00020fcc` prefix
`00020FA4..00020FD0` and full `00022558` helper. The existing history moves
`FFFF2672..FFFF2675` to `FFFF266E..FFFF2671` before the 260-byte block transfer.
The existing R11 entry condition, 76-byte context, 380-byte observer, 96-byte
frame and 4 observing-boundary instructions remain intact.

The second stage uses the complete `00047A56` comparator and its real
curve and fixed diagnostic helpers.

Independent equations cover the complete history and block transfer, both
pedal comparison modes, timer and diagnostic precedence, raw ordered
hysteresis, status flags and all RAM publications. Independent physical/state
checks bind actual source2672, history destination266E, full CPU/SR/GBR/
MACH/MACL/PR/SP, both frames and external caller ABIs, exact instructions and
delay slots, physical operands, and real helper arguments and returns.
Held-other source-word alternatives must change the actual `FFFF246A.bit7`.

The owning proof retains the original `pedal/ram` reader of `00047A56` as a
quantity relation through the registered history. It does not attribute a
physical2672 read instruction to the comparator. Original semantic width and
signedness remain unset; units, scale, all other native claims, function
facts, ledger and TEST positions remain exact. The full existing coherent
COPY original is mandatory in the same complete primary. This controlled
scope supplies no scheduler, geometry, units, scale or hardware claim.
Shared acceptance supplies the executed result.
