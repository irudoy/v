// Ghidra SuperH source for the four exact JK08A map-switching lookup
// adapters.
//
// This is an independently assembled implementation slice, not a complete
// firmware patch. The selector host, limiter transaction, startup wrapper, and
// CAN feedback wrapper are intentionally absent. The external helper at
// 0x000D2270 is assembled from map-switching-adapter-helper.s.
//
// Every BRA delay slot must remain NOP. On SH-2E, a PC-relative MOV in that
// slot uses the branch destination plus two as its PC basis, not the static
// address of the delay-slot instruction.

.org 0x000D2300
overrun_adapter:
mov.l @(overrun_stock_wrapper,pc),r3
mov.l @(overrun_cut_base,pc),r0
cmp/eq r0,r4
bt overrun_select_cut
mov.l @(overrun_restore_base,pc),r0
cmp/eq r0,r4
bt overrun_select_restore
jmp @r3
nop
overrun_select_cut:
mov.l @(overrun_cut_pointers,pc),r2
bra 0x000D2270
nop
overrun_select_restore:
mov.l @(overrun_restore_pointers,pc),r2
bra 0x000D2270
nop

.org 0x000D2320
overrun_cut_base:
.long 0x00012718
overrun_restore_base:
.long 0x00012818
overrun_stock_wrapper:
.long 0x00026388
overrun_cut_pointers:
.long 0x000D3540
overrun_restore_pointers:
.long 0x000D3554

.org 0x000D2340
ignition_adapter:
mov.l @(ignition_stock_wrapper,pc),r3
mov.l @(ignition_main_base,pc),r0
cmp/eq r0,r4
bt ignition_select_main
mov.l @(ignition_high_det_base,pc),r0
cmp/eq r0,r4
bt ignition_select_high_det
jmp @r3
nop
ignition_select_main:
mov.l @(ignition_main_pointers,pc),r2
bra 0x000D2270
nop
ignition_select_high_det:
mov.l @(ignition_high_det_pointers,pc),r2
bra 0x000D2270
nop

.org 0x000D2360
ignition_main_base:
.long 0x00009A1A
ignition_high_det_base:
.long 0x00009B1A
ignition_stock_wrapper:
.long 0x00026230
ignition_main_pointers:
.long 0x000D3568
ignition_high_det_pointers:
.long 0x000D357C

.org 0x000D2380
fuel_compensation_adapter:
mov.l @(fuel_compensation_stock_wrapper,pc),r3
mov.l @(fuel_compensation_base,pc),r0
cmp/eq r0,r4
bt fuel_compensation_select
jmp @r3
nop
fuel_compensation_select:
mov.l @(fuel_compensation_pointers,pc),r2
bra 0x000D2270
nop

.org 0x000D23A0
fuel_compensation_base:
.long 0x0000A29A
fuel_compensation_stock_wrapper:
.long 0x000261F0
fuel_compensation_pointers:
.long 0x000D35A4

.org 0x000D23C0
exhaust_cvtc_target_adapter:
mov.l @(exhaust_cvtc_target_stock_wrapper,pc),r3
mov.l @(exhaust_cvtc_target_base,pc),r0
cmp/eq r0,r4
bt exhaust_cvtc_target_select
jmp @r3
nop
exhaust_cvtc_target_select:
mov.l @(exhaust_cvtc_target_pointers,pc),r2
bra 0x000D2270
nop

.org 0x000D23E0
exhaust_cvtc_target_base:
.long 0x0000B33A
exhaust_cvtc_target_stock_wrapper:
.long 0x000261B8
exhaust_cvtc_target_pointers:
.long 0x000D3590
