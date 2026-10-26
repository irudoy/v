# Standalone full raw32 signed-magnitude helper

The descriptor binds one complete function body, 5 stock instructions and
10 immutable code bytes at natural entry `00022590`. It has 0 literal pools,
0 pointer aliases and no callee. The existing ordinary profile supplies an
80-byte input context, 572-byte observation record and complete 192-byte frame.
The observer, runner and instruction engine retain their existing interfaces.

`CMP/PL R4` tests the complete signed raw32 argument. A positive argument takes
the branch to `RTS`; zero and negative arguments execute `NEG R4,R4`. The real
return delay slot copies the full R4 carrier to R0. The zero case executes NEG
and retains zero. Raw `80000000` retains `80000000`; it is neither clamped to
`7fffffff` nor narrowed to an unsigned word. Within SR, only T changes, according to the strict positive comparison.
The remaining observed GPRs, GBR, MACH, MACL, PR and SP retain their
incoming values. The complete frame and ordinary RAM remain unchanged.

Separate numerical equations bind the complete returned carriers. Independent
five-instruction equations bind every incoming and outgoing GPR/SR/special
state, both conditional paths, the natural return and its real delay slot.
Exact data-access and call streams are empty. Code observation uses the
existing immutable ROM transport with `calibration_input = false`; no code
byte is an adjustable calibration. Independent GNU assembly must reproduce
all stock words in the complete owned image.

The exact original under review is
`782dacc59731fbc23c8a52ec82e8f9cc0468235c9826a1eee5214cbe5d571417`:
the reader from `wandering-grasshopper/ram` at `ffff2c1c` to
`clay-capuchin/fn`. The withdrawal removes only that direct reader and its
owner-end ledger selector. The raw-difference unit, unset semantic types,
both channel inputs, the real writer `gay-labrador/fn`, complete evidence,
ledger positions and TEST origins remain bound. The complete native function
remains unchanged. Its existing W-25600 caller notes and bounded caller TESTs
retain their separate meaning; they do not qualify this standalone original.

Fixed-other alternatives vary the complete raw32 R4 input and require changed
actual computed R0. Separate controls vary individual raw bytes at and beside
the selected native root, without declaring a semantic width or array extent.
Complete CPU, frame and all other RAM bytes remain equal under those controls;
the controlled raw bytes retain their own unchanged input values. Input echoes
supply no computed-source admission.

The independent consumer requires the complete original COPY primary, exact
consumed source files, pinned GNU tools and actual state snapshots. Its owning
result grants only the exact direct-reader withdrawal. It grants no logical
dependency replacement, new unit, scale, native geometry, scheduler inference,
caller reachability, native publication or hardware qualification. Source
preparation establishes no accepted execution.
