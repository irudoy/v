// Ignition state-code surface adapter template for the SH7059 1ND layout.
//
// The mode-selected half of the 1ND ignition coordinator 0x00074D98 reads
// four 8x8 state-code surfaces through one literal that holds the 8x8 lookup
// 0x000285B4. The adapter identifies the requested table base in r4 and
// substitutes the active slot of the matching family; every other base
// reaches the stock lookup unchanged. The lookup takes r4 to r7 and one stack
// argument and returns through PR, so the adapter leaves r4 to r7, r15, and
// PR untouched apart from the substituted r4; r0 to r3 carry no lookup input.
//
// The source uses the canonical coordinates of the injected block and the
// 1ND0A stock addresses. The target projection relocates the block behind the
// VQ37 fuel-cut coordinator wrapper and binds the stock lookup, the four
// table bases, and the four pointer tables from the exact ROM address
// profile. The slot-selection logic is local because the shared adapter
// helper lies outside SH BRA displacement range.
//
// Every JMP delay slot must remain NOP.

.org 0x000D5080
ignition_state_adapter:
mov.l @(ignition_state_stock_lookup,pc),r3
mov.l @(ignition_state_3_base,pc),r0
mov.l @(ignition_state_3_pointers,pc),r2
cmp/eq r0,r4
bt ignition_state_select
mov.l @(ignition_state_4_base,pc),r0
mov.l @(ignition_state_4_pointers,pc),r2
cmp/eq r0,r4
bt ignition_state_select
mov.l @(ignition_state_5_base,pc),r0
mov.l @(ignition_state_5_pointers,pc),r2
cmp/eq r0,r4
bt ignition_state_select
mov.l @(ignition_state_6_7_base,pc),r0
mov.l @(ignition_state_6_7_pointers,pc),r2
cmp/eq r0,r4
bt ignition_state_select
jmp @r3
nop
ignition_state_select:
mov.l @(ignition_state_selector,pc),r1
mov.b @r1,r0
extu.b r0,r0
mov #0x5,r1
cmp/hs r1,r0
bf ignition_state_index_valid
mov #0x0,r0
ignition_state_index_valid:
shll2 r0
mov.l @(r0,r2),r4
jmp @r3
nop

.align 4
ignition_state_stock_lookup:
.long 0x000285B4
ignition_state_3_base:
.long 0x0000A610
ignition_state_3_pointers:
.long 0x000D5100
ignition_state_4_base:
.long 0x0000A710
ignition_state_4_pointers:
.long 0x000D5114
ignition_state_5_base:
.long 0x0000A690
ignition_state_5_pointers:
.long 0x000D5128
ignition_state_6_7_base:
.long 0x0000A6D0
ignition_state_6_7_pointers:
.long 0x000D513C
ignition_state_selector:
.long 0xFFFF5D00
