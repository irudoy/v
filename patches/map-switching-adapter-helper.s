// Shared fail-closed slot-selection helper for the exact JK08A lookup
// adapters. This is an independently assembled implementation slice, not a
// complete firmware patch.

.org 0x000D2270
adapter_select_helper:
mov.l @(selector_state_address,pc),r1
mov.b @r1,r0
extu.b r0,r0
mov #0x5,r1
cmp/hs r1,r0
bf adapter_index_valid
mov #0x0,r0
adapter_index_valid:
shll2 r0
mov.l @(r0,r2),r4
jmp @r3
nop

.org 0x000D229C
selector_state_address:
.long 0xFFFF5D00
