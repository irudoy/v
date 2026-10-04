! JK08A BFS history and the scheduler's 28-byte load snapshot.
! Link at 0x20f04; the selected copier path retains its natural return.
    .text
    .balign 4
snapshot_slice:
    mov.l current_bfs,r4
    mov.l previous_bfs,r6
    mov.w @r4,r2
    mov.l snapshot_pointer,r1
    mov.w r2,@r6
    mov.l newest_bfs,r6
    mov.w @r6,r2
    mov.l copier_pointer,r6
    mov.w r2,@r4
    mov.l live_pointer,r2
    jsr @r6
    mov #28,r0
    .org 0x2110c - 0x20f04
current_bfs:
    .long 0xffff1024
previous_bfs:
    .long 0xffff1028
snapshot_pointer:
    .long 0xffff102c
newest_bfs:
    .long 0xffff1026
copier_pointer:
    .long copy_dispatch
live_pointer:
    .long 0xffff1048

    .org 0x22104 - 0x20f04
copy_dispatch:
    mov.l r3,@-r15
    mov.l dispatch_table,r3
    mov.l @(r0,r3),r3
    add #-4,r0
    jmp @r3
    mov.l @(r0,r2),r3
dispatch_table:
    .long 0x00022158
    .org 0x2213a - 0x20f04
copy_28_bytes:
    mov.l @(20,r2),r0
    mov.l r3,@(24,r1)
    mov.l @(16,r2),r3
    mov.l r0,@(20,r1)
    mov.l @(12,r2),r0
    mov.l r3,@(16,r1)
    mov.l @(8,r2),r3
    mov.l r0,@(12,r1)
    mov.l @(4,r2),r0
    mov.l r3,@(8,r1)
    mov.l @r2,r3
    mov.l r0,@(4,r1)
    mov.l r3,@r1
    rts
    mov.l @r15+,r3
    .org 0x22174 - 0x20f04
copy_28_dispatch:
    .long copy_28_bytes
