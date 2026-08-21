// Atomic scalar-only limiter commit for SH7059 1ND.
//
// Input:
//   r4 - requested zero-based slot index
//
// The target has no homolog of the canonical 2x2 fuel-cut limiter table. The
// transaction therefore publishes only the selected throttle limiter scalar
// and the selector state. Rolling Launch is not supported by this target.

.org 0x000D3660
limiter_commit:
stc sr,r7
extu.b r4,r4
mov #0x5,r0
cmp/hs r0,r4
bf limiter_index_valid
mov #0x0,r4
limiter_index_valid:
mov r7,r0
or 0xF0,r0
ldc r0,sr

mov r4,r0
shll2 r0
mov.l @(throttle_pointer_table,pc),r3
mov.l @(r0,r3),r2
mov.w @r2,r0
mov.l @(throttle_selected_shadow,pc),r5
mov.w r0,@r5

mov.l @(selector_state,pc),r5
mov #0x0,r0
mov.b r0,@(0x1,r5)
mov.b r0,@(0x2,r5)
mov.b r0,@(0x3,r5)
mov r5,r6
add 0x4,r6
mov.l r0,@r6
mov.b r4,@r5
ldc r7,sr
rts
nop

.align 4
throttle_pointer_table:
.long 0x000D35CC
throttle_selected_shadow:
.long 0xFFFF5D20
selector_state:
.long 0xFFFF5D00
