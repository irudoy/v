# JK08A natural register-only helper withdrawals

Source bindings: `JK08A.register-only-helpers.toml`.


The full224F8 entry executes its first SHAR and falls through the distinct224FA
entry to RTS22504 and its SHAR delay slot22506. Their signed R0 shifts are7
and6 bits. Entry2251C produces signed R0 shifted11 bits, saves R1 on the
local stack and restores it in the natural RTS delay slot. Entry259D0 uses
the low byte of R7 to select modular R4-R6 or R4 before a signed R5 comparison.
Entry26740 chooses unsigned ascending/descending interpolation, retains the
low32 product, takes its high word, restores MACL and uses the original return
delay slot. Its descending path saves R0 and restores the saved value into R2.
Entry50A4C ORs R4/R5/R6 and returns the low six bits in R0.

These arithmetic behaviors bind no datum identity. Independent complete GPR,
GBR, MACH, MACL, SR, SP, PR, frame and scalar expectations accompany the
separate instruction engine. Ordered physical events admit only the exact
local push/pop pairs; ROM data access, RAM data access and calls are absent.
All natural instructions, both feasible outcomes of259D4/26742, each real
RTS and every delay slot are required. Complete RAM, code, read-only code
observation and external ABI remain exact.

Input-only alternatives cover complete register boundaries, signed and
unsigned comparisons, low-byte flag alternatives, modular subtraction,
low32 multiply wrap, shift/sign/T boundaries, both interpolation directions
and complete context/SR alternatives. Fixed-other groups require changes in
actual returned R0 for each used register argument. R7 also occupies its
declared incoming frame carrier; only those two copies of the same argument
are omitted from its held-other comparison. No caller attribution follows.


Partial, duplicate, changed, unmatched or broader withdrawals refuse.
The reserved namespace always refuses owning evidence, including identity,
scale and reverse-function donation. It is never neutral metadata for an
attached proof. Existing receipts and canonical sources remain under the
normal common-acceptance and publication boundary.



The original capture and controlled refusal sources cover complete raw
schema/streams/toolchain/sources, instruction reconstruction, all CPU/frame/
RAM/code bytes, physical event order and width, branch outcomes, natural
returns/delay slots, changed-output alternatives, full native document
preservation, original TEST contexts, physical scopes and exact writer
preflight. Software coverage does not establish hardware behavior.
