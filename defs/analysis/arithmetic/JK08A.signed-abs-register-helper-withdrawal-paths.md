# Standalone full raw32 signed-magnitude helper

The natural entry is `00022590`; it has no callee.

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


Fixed-other alternatives vary the complete raw32 R4 input and require changed
actual computed R0. Separate controls vary individual raw bytes at and beside
the selected native root, without declaring a semantic width or array extent.
Complete CPU, frame and all other RAM bytes remain equal under those controls;
the controlled raw bytes retain their own unchanged input values. Input echoes
supply no computed-source admission.
