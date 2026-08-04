// Ghidra SuperH source for the exact JK08A four-family DFCO adapter.
//
// Both stock hook literals are shared by two callers. The adapter therefore
// identifies the requested table base in r4 and selects the corresponding
// five-slot pointer table. Unknown bases pass through to the stock wrapper.
// The helper at 0x000D2270 validates the active slot and preserves r4 when it
// falls back to Map 1.
//
// Every branch delay slot must remain NOP.

.org 0x000D2480
full_dfco_adapter:
mov.l @(full_dfco_stock_wrapper,pc),r3
mov.l @(full_dfco_hold_base,pc),r0
cmp/eq r0,r4
bt full_dfco_select_hold
mov.l @(full_dfco_entry_base,pc),r0
cmp/eq r0,r4
bt full_dfco_select_entry
mov.l @(full_dfco_full_restore_base,pc),r0
cmp/eq r0,r4
bt full_dfco_select_full_restore
mov.l @(full_dfco_intermediate_restore_base,pc),r0
cmp/eq r0,r4
bt full_dfco_select_intermediate_restore
jmp @r3
nop
full_dfco_select_hold:
mov.l @(full_dfco_hold_pointers,pc),r2
bra 0x000D2270
nop
full_dfco_select_entry:
mov.l @(full_dfco_entry_pointers,pc),r2
bra 0x000D2270
nop
full_dfco_select_full_restore:
mov.l @(full_dfco_full_restore_pointers,pc),r2
bra 0x000D2270
nop
full_dfco_select_intermediate_restore:
mov.l @(full_dfco_intermediate_restore_pointers,pc),r2
bra 0x000D2270
nop

.org 0x000D24B8
full_dfco_hold_base:
.long 0x000126E4
full_dfco_entry_base:
.long 0x00012718
full_dfco_full_restore_base:
.long 0x00012818
full_dfco_intermediate_restore_base:
.long 0x0001298C
full_dfco_stock_wrapper:
.long 0x00026388
full_dfco_hold_pointers:
.long 0x000D24E0
full_dfco_entry_pointers:
.long 0x000D3540
full_dfco_full_restore_pointers:
.long 0x000D3554
full_dfco_intermediate_restore_pointers:
.long 0x000D3528
