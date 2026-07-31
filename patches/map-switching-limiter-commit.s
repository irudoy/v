// Atomic limiter-shadow commit for the exact JK08A five-slot selector.
//
// Input:
//   r4 - requested zero-based slot index
//
// Output:
//   r4 - normalized slot index, with every invalid value resolved to zero
//
// The function uses caller-saved r0..r7. It preserves the entry SR exactly,
// masks interrupts before the first runtime write, and publishes active_index
// as the final write before restoring SR.

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
mov.l @(fuel_cut_pointer_table,pc),r3
mov.l @(r0,r3),r2
mov.l @(fuel_cut_shadow,pc),r6
mov #0x4,r1
fuel_map_copy_loop:
mov.w @r2+,r0
mov.w r0,@r6
add 0x2,r6
dt r1
bf fuel_map_copy_loop
mov.l @(fuel_cut_stock_tail,pc),r5
mov #0x2,r1
fuel_tail_copy_loop:
mov.w @r5+,r0
mov.w r0,@r6
add 0x2,r6
dt r1
bf fuel_tail_copy_loop

mov.l @(throttle_stock_cluster,pc),r5
mov.l @(throttle_shadow,pc),r6
mov #0x7,r1
throttle_copy_loop:
mov.l @r5+,r2
mov.l r2,@r6
add 0x4,r6
dt r1
bf throttle_copy_loop

mov r4,r0
shll2 r0
mov.l @(throttle_pointer_table,pc),r3
mov.l @(r0,r3),r2
mov.w @r2,r0
mov.l @(throttle_selected_shadow,pc),r5
mov.w r0,@r5
mov.l @(throttle_runtime_scalar,pc),r5
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

.org 0x000D3720
fuel_cut_pointer_table:
.long 0x000D35B8
fuel_cut_shadow:
.long 0xFFFF5D10
fuel_cut_stock_tail:
.long 0x00009356
throttle_stock_cluster:
.long 0x00009424
throttle_shadow:
.long 0xFFFF5D20
throttle_pointer_table:
.long 0x000D35CC
throttle_selected_shadow:
.long 0xFFFF5D28
throttle_runtime_scalar:
.long 0xFFFF1796
selector_state:
.long 0xFFFF5D00
