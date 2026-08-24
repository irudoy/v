// Second CVTC-target adapter template for the dual-CVTC layout.
//
// The 8MFK layout switches an intake-cam target family and an exhaust-cam
// target family. The intake family reuses the canonical CVTC adapter and
// storage; this template serves the exhaust family. The target projection
// relocates it into the former telemetry reserve and replaces all stock, map,
// pointer-table, and selector addresses from the exact ROM address profile.
// The slot-selection logic is local because the shared adapter helper lies
// outside SH BRA displacement range.

.org 0x000D5000
secondary_cvtc_target_adapter:
mov.l @(secondary_cvtc_target_stock_wrapper,pc),r3
mov.l @(secondary_cvtc_target_base,pc),r0
cmp/eq r0,r4
bt secondary_cvtc_target_select
jmp @r3
nop
secondary_cvtc_target_select:
mov.l @(secondary_cvtc_target_pointers,pc),r2
mov.l @(secondary_cvtc_target_selector,pc),r1
mov.b @r1,r0
extu.b r0,r0
mov #0x5,r1
cmp/hs r1,r0
bf secondary_cvtc_target_index_valid
mov #0x0,r0
secondary_cvtc_target_index_valid:
shll2 r0
mov.l @(r0,r2),r4
jmp @r3
nop

.align 4
secondary_cvtc_target_base:
.long 0x0000B33A
secondary_cvtc_target_stock_wrapper:
.long 0x000261B8
secondary_cvtc_target_pointers:
.long 0x000D5050
secondary_cvtc_target_selector:
.long 0xFFFF5D00
