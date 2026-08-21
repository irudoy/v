// Dual-bank 8MFK exhaust-CVTC adapter template.
//
// The target projection relocates this source into the former telemetry
// reserve and replaces all stock, map, pointer-table, and selector addresses
// from the exact ROM address profile. The slot-selection logic is local
// because the shared adapter helper lies outside SH BRA displacement range.

.org 0x000D5000
exhaust_cvtc_target_odd_adapter:
mov.l @(exhaust_cvtc_target_odd_stock_wrapper,pc),r3
mov.l @(exhaust_cvtc_target_odd_base,pc),r0
cmp/eq r0,r4
bt exhaust_cvtc_target_odd_select
jmp @r3
nop
exhaust_cvtc_target_odd_select:
mov.l @(exhaust_cvtc_target_odd_pointers,pc),r2
mov.l @(exhaust_cvtc_target_odd_selector,pc),r1
mov.b @r1,r0
extu.b r0,r0
mov #0x5,r1
cmp/hs r1,r0
bf exhaust_cvtc_target_odd_index_valid
mov #0x0,r0
exhaust_cvtc_target_odd_index_valid:
shll2 r0
mov.l @(r0,r2),r4
jmp @r3
nop

.align 4
exhaust_cvtc_target_odd_base:
.long 0x0000B33A
exhaust_cvtc_target_odd_stock_wrapper:
.long 0x000261B8
exhaust_cvtc_target_odd_pointers:
.long 0x000D5050
exhaust_cvtc_target_odd_selector:
.long 0xFFFF5D00
