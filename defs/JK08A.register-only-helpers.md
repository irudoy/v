# JK08A natural register-only helper withdrawals

The source boundary contains six natural entries, 56 stock instructions and
112 bound code bytes. The exact descriptor is
`defs/JK08A.register-only-helpers.toml`; the twelve original identities and
eleven complete native preimages/postimages are in
`defs/JK08A.register-only-withdrawals.toml`.

| Datum | Natural function | Exact unsupported original |
|---|---|---|
| `7mfk:00008e3a` | `7mfk:000259d0` | `cd417736058f07670ae507ef446d43392b8d8ecde4713ccd0e3365e0e496a23f` |
| `7mfk:00008e3c` | `7mfk:000259d0` | `78b98855222718d37d5cf0aaae145cc7ac5e71d354b30b19c4dcdef22d20d0cc` |
| `7mfk:00012126` | `7mfk:0002251c` | `ed84fe25ec83532689390f7b9d04b3531a34dd9103356a70ba45ff3a19e10dd0` |
| `7mfk:00012126` | `7mfk:00026740` | `5186363c50a9f125349ef101af5f897ba27bec04e605a56e6ace7fcdb125cba0` |
| `7mfk:00012196` | `7mfk:00026740` | `4daaf757d0d4108cbe66e6dae6f187beafcb44debeae6aaa337aa98a484178c8` |
| `7mfk:000122ea` | `7mfk:000224f8` | `a8551a2692510cfcee624615b58da94d86b47559240459536f7e10cb54d2d324` |
| `7mfk:000122f2` | `7mfk:000224f8` | `8b77d2de1849f696423a548f8467dbb8006a8f316a009c4af3613af7adcf4ce4` |
| `7mfk:00012552` | `7mfk:000224f8` | `4869ba8f1d939a6484364443f430305417f6417d63840eca0956d52855010cad` |
| `7mfk:00012c02` | `7mfk:000224f8` | `72e8b93d48245f80a6f5f29c61b731aa095d4e7f77c617731ffaf1feeb65dbca` |
| `7mfk:00012d72` | `7mfk:000224f8` | `b90096e16bf4aa1873a67229932cc0a5aea343bd2007bdae1ccb426c67aaeee5` |
| `7mfk:0001300e` | `7mfk:000224fa` | `bf9a3872d4ab3d6a035157cefdf6ced78cac704a1a02e04720a27649ec15a4c0` |
| `7mfk:ffff22e0` | `7mfk:00050a4c` | `58c006e6754df9b157888cee4f461ad85788ace7edc48ee9801477e08eff7bab` |

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

The existing COPY primary carries `register_only_helper_paths`. The standard
input-only adapter uses the existing 80/572 observer and shared raw transport.
The producer grants no semantic admission. Its independent consumer requires
both `exact_register_only_paths` and `no_datum_access`; a syntactic instruction
scan or unchanged output cannot substitute for executable absence coverage.
There are no ROM relocations, aliases, observing returns or stock-function
stubs in this fixture.

The `register-only-withdrawal` ordinary registration has an explicit
withdrawal-only policy. Its normal writer batch contains exactly twelve
`unlink` operations. Each exact original is present before and absent after;
there is no replacement owning relation or evidence item. The fourteen exact
matching ledger selectors are removed. All other native fields, symbol
types/evidence, layouts, surviving link order, TEST origins and complete
contexts, ledger identities/fields/notes and existing proof scopes remain
exact. The normal TOML formatter omits containers emptied by these deletions.
The six complete function documents have no matching reverse ledger selector.

Partial, duplicate, changed, unmatched or broader withdrawals refuse.
The reserved namespace always refuses owning evidence, including identity,
scale and reverse-function donation. It is never neutral metadata for an
attached proof. Existing receipts and canonical sources remain under the
normal common-acceptance and publication boundary.

The source grants no native geometry, units, scale, caller reachability,
automatic resolution, hardware qualification or publication. The existing
ordinary registry contains thirteen families and forty-seven capture bindings.

The original capture and controlled refusal sources cover complete raw
schema/streams/toolchain/sources, instruction reconstruction, all CPU/frame/
RAM/code bytes, physical event order and width, branch outcomes, natural
returns/delay slots, changed-output alternatives, full native document
preservation, original TEST contexts, physical scopes and exact writer
preflight. Software coverage does not establish hardware behavior.
