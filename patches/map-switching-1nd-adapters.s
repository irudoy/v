// SH7059 1ND lookup adapters for the five-slot map-switching runtime.
//
// The target keeps separate fuel-compensation and warm-idle tables for both
// banks. The second fuel family reuses the canonical exhaust storage slots;
// the second warm-idle family reuses the canonical fuel-cut storage slots.
// All unrecognized bases tail-call the exact stock lookup.

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
mov.l @(high_octane_timing_state_base,pc),r0
cmp/eq r0,r4
bt select_high_octane_timing_state
mov.l @(high_detonation_timing_state_base,pc),r0
cmp/eq r0,r4
bt select_high_detonation_timing_state
jmp @r3
nop
select_high_octane_timing_state:
mov.l @(high_octane_timing_state_pointers,pc),r2
bra 0x000D2270
nop
select_high_detonation_timing_state:
mov.l @(high_detonation_timing_state_pointers,pc),r2
bra 0x000D2270
nop

.org 0x000D2360
high_octane_timing_state_base:
.long 0x00009A1A
high_detonation_timing_state_base:
.long 0x00009B1A
ignition_stock_wrapper:
.long 0x00026230
high_octane_timing_state_pointers:
.long 0x000D3568
high_detonation_timing_state_pointers:
.long 0x000D357C

.org 0x000D2380
fuel_compensation_adapter:
mov.l @(fuel_compensation_stock_wrapper,pc),r3
mov.l @(fuel_compensation_bank_1_base,pc),r0
cmp/eq r0,r4
bt fuel_compensation_select_bank_1
mov.l @(fuel_compensation_bank_2_base,pc),r0
cmp/eq r0,r4
bt fuel_compensation_select_bank_2
jmp @r3
nop
fuel_compensation_select_bank_1:
mov.l @(fuel_compensation_bank_1_pointers,pc),r2
bra 0x000D2270
nop
fuel_compensation_select_bank_2:
mov.l @(fuel_compensation_bank_2_pointers,pc),r2
bra 0x000D2270
nop

.align 4
fuel_compensation_bank_1_base:
.long 0x0000A29A
fuel_compensation_bank_2_base:
.long 0x0000B33A
fuel_compensation_stock_wrapper:
.long 0x000261F0
fuel_compensation_bank_1_pointers:
.long 0x000D35A4
fuel_compensation_bank_2_pointers:
.long 0x000D3590

.org 0x000D23C0
idle_ignition_bank_2_adapter:
mov.l @(idle_bank_2_stock_wrapper,pc),r3
mov.l @(cold_idle_bank_2_base,pc),r0
cmp/eq r0,r4
bt idle_bank_2_select_cold
mov.l @(warm_idle_bank_2_base,pc),r0
cmp/eq r0,r4
bt idle_bank_2_select_warm
jmp @r3
nop
idle_bank_2_select_cold:
mov.l @(cold_idle_bank_2_pointers,pc),r2
bra 0x000D2270
nop
idle_bank_2_select_warm:
mov.l @(warm_idle_bank_2_pointers,pc),r2
bra 0x000D2270
nop

.org 0x000D23E0
cold_idle_bank_2_base:
.long 0x00012196
warm_idle_bank_2_base:
.long 0x0000934E
idle_bank_2_stock_wrapper:
.long 0x00026370
cold_idle_bank_2_pointers:
.long 0x000D4040
warm_idle_bank_2_pointers:
.long 0x000D35B8
