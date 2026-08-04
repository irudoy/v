// Minimal startup execution gate for the exact JK08A marker readback.
//
// The stock thunk loads its target through ROM32[0x27D28] and enters it with
// the original caller's PR. This gate restores r0 to the exact stock target
// and tail-jumps there, preserving PR and every other register.

.org 0x000D22A0
startup_trampoline:
mov.l @(startup_stock_initializer,pc),r0
jmp @r0
nop

.align 4
startup_stock_initializer:
.long 0x0002C648
