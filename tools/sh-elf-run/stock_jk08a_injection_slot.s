! Bounded event-slot construction with explicit R2/R5/R14/GBR entry contexts.
    .text
    .balign 4
    .org 0x2268e - 0x2268c
event_order:
    .byte 0,1,2,3,4,5,6,2,4,8,16,32,1,0,1,2,3,4,5,6
    .org 0x54a64 - 0x2268c
slot_entry:
    mov.b @r14,r4
    mov.b @(3,r5),r0
    extu.b r4,r4
    cmp/ge r2,r4
    bt/s counter_done
    mov r0,r7
    add #1,r4
    mov.b r4,@r14
counter_done:
    mov.l event_source,r2
    mov.l order_pointer,r8
    mov.b @(10,r2),r0
    extu.b r0,r0
    mov.b @(r0,r8),r2
    extu.b r2,r4
    mov r8,r2
    add #13,r2
    mov.b @(r0,r2),r5
    mov #1,r2
    cmp/hi r2,r4
    bf/s mask_done
    add #-1,r5
    mov #1,r6
mask_loop:
    add #1,r6
    shll r2
    cmp/hs r4,r6
    bf mask_loop
mask_done:
    mov.l mask_base,r3
    mov.w mask_offset,r0
    mov.b @(r0,r3),r6
    or r2,r6
    mov.b r6,@(r0,r3)
    mov r7,r0
    tst #32,r0
    bf live_lead
    bra slot_arithmetic
    mov #3,r9
live_lead:
    mov.l snapshot_base,r4
    mov #52,r0
    mov.b @(r0,r4),r9
    extu.b r9,r9
slot_arithmetic:
    mov r5,r0
    and #15,r0
    sub r9,r0
    cmp/pz r0
    bt/s slot_store
    mov r0,r2
    add #6,r2
slot_store:
    mov.l control_base,r6
    mov r2,r0
    mov.b r0,@(192,gbr)
    .org 0x54b52 - 0x2268c
flag_base:
    .word 0x8510
mask_offset:
    .word 0x029a
    .org 0x54c30 - 0x2268c
gbr_base:
    .long 0xffff1ff4
counter_pointer:
    .long 0xffff4555
event_source:
    .long 0xffff11d4
order_pointer:
    .long 0x0002268e
mask_base:
    .long 0xffff128c
snapshot_base:
    .long 0xffff2330
control_base:
    .long 0xffff24c8
