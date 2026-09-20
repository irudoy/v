// VQ37 duplicated-table lookup adapters for the five-slot map-switching runtime.
//
// The target reads two fuel-compensation surfaces and two warm-idle tables
// through one index byte and one interpolator, so the pairs carry no engine-
// bank identity and are named by the selector arm that reaches them. The
// alternate fuel family reuses the canonical exhaust storage slots; the
// alternate warm-idle family reuses the canonical fuel-cut storage slots.
// The ignition adapter selects the two 16x16 surfaces of the mode-selected
// coordinator half, the half that the stock configuration byte executes; they
// reuse the storage of the two canonical 16x16 ignition families, and the
// three byte-identical surfaces of the gated half pass through.
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
mov.l @(ignition_surface_hot_base,pc),r0
cmp/eq r0,r4
bt select_ignition_surface_hot
mov.l @(ignition_surface_cold_base,pc),r0
cmp/eq r0,r4
bt select_ignition_surface_cold
jmp @r3
nop
select_ignition_surface_hot:
mov.l @(ignition_surface_hot_pointers,pc),r2
bra 0x000D2270
nop
select_ignition_surface_cold:
mov.l @(ignition_surface_cold_pointers,pc),r2
bra 0x000D2270
nop

.org 0x000D2360
ignition_surface_hot_base:
.long 0x00009A1A
ignition_surface_cold_base:
.long 0x00009B1A
ignition_stock_wrapper:
.long 0x00026230
ignition_surface_hot_pointers:
.long 0x000D3568
ignition_surface_cold_pointers:
.long 0x000D357C

.org 0x000D2380
fuel_compensation_adapter:
mov.l @(fuel_compensation_stock_wrapper,pc),r3
mov.l @(fuel_compensation_default_base,pc),r0
cmp/eq r0,r4
bt fuel_compensation_select_default
mov.l @(fuel_compensation_alternate_base,pc),r0
cmp/eq r0,r4
bt fuel_compensation_select_alternate
jmp @r3
nop
fuel_compensation_select_default:
mov.l @(fuel_compensation_default_pointers,pc),r2
bra 0x000D2270
nop
fuel_compensation_select_alternate:
mov.l @(fuel_compensation_alternate_pointers,pc),r2
bra 0x000D2270
nop

.align 4
fuel_compensation_default_base:
.long 0x0000A29A
fuel_compensation_alternate_base:
.long 0x0000B33A
fuel_compensation_stock_wrapper:
.long 0x000261F0
fuel_compensation_default_pointers:
.long 0x000D35A4
fuel_compensation_alternate_pointers:
.long 0x000D3590

.org 0x000D23C0
idle_ignition_pool_2_adapter:
mov.l @(idle_pool_2_stock_wrapper,pc),r3
mov.l @(cold_idle_pool_2_base,pc),r0
cmp/eq r0,r4
bt idle_pool_2_select_cold
mov.l @(warm_idle_pool_2_base,pc),r0
cmp/eq r0,r4
bt idle_pool_2_select_warm
jmp @r3
nop
idle_pool_2_select_cold:
mov.l @(cold_idle_pool_2_pointers,pc),r2
bra 0x000D2270
nop
idle_pool_2_select_warm:
mov.l @(warm_idle_pool_2_pointers,pc),r2
bra 0x000D2270
nop

.org 0x000D23E0
cold_idle_pool_2_base:
.long 0x00012196
warm_idle_pool_2_base:
.long 0x0000934E
idle_pool_2_stock_wrapper:
.long 0x00026370
cold_idle_pool_2_pointers:
.long 0x000D4040
warm_idle_pool_2_pointers:
.long 0x000D35B8
