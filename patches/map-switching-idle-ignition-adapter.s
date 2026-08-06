// Ghidra SuperH source for the exact JK08A idle-ignition map-switching
// adapter.
//
// The stock function at 0x0004AFDC loads the shared implicit-axis wrapper
// through literal 0x0004B224. This adapter replaces that one wrapper literal,
// selects slot storage only for the two hardware-confirmed idle-ignition
// bases, and passes every other base to the stock wrapper unchanged.
//
// Every BRA delay slot must remain NOP. On SH-2E, a PC-relative MOV in that
// slot uses the branch destination plus two as its PC basis, not the static
// address of the delay-slot instruction.

.org 0x000D4000
idle_ignition_adapter:
mov.l @(idle_ignition_stock_wrapper,pc),r3
mov.l @(cold_idle_ignition_base,pc),r0
cmp/eq r0,r4
bt idle_ignition_select_cold
mov.l @(idle_ignition_base,pc),r0
cmp/eq r0,r4
bt idle_ignition_select_main
jmp @r3
nop
idle_ignition_select_cold:
mov.l @(cold_idle_ignition_pointers,pc),r2
mov.l @(map_switching_selector,pc),r0
jmp @r0
nop
idle_ignition_select_main:
mov.l @(idle_ignition_pointers,pc),r2
mov.l @(map_switching_selector,pc),r0
jmp @r0
nop

.org 0x000D4024
cold_idle_ignition_base:
.long 0x00012196
idle_ignition_base:
.long 0x0001219E
idle_ignition_stock_wrapper:
.long 0x00026370
map_switching_selector:
.long 0x000D2270
cold_idle_ignition_pointers:
.long 0x000D4040
idle_ignition_pointers:
.long 0x000D4054
