! Bounded accepted lookup, zero-delta selection and negative-delta clear.
    .text
    .balign 4
    .org 0x22695 - 0x22694
pending_masks:
    .byte 2,4,8,16,32,1
    .org 0x54bdc - 0x22694
zero_entry:
    mov.w pending_offset_a,r0
    mov #0,r2
    mov #6,r5
    mov.b r2,@(r0,r14)
    mov.w cursor_offset_a,r0
    mov.b @(r0,r14),r2
    extu.b r2,r6
    add #1,r6
    cmp/ge r5,r6
    bf next_slot_ready
    mov #0,r6
next_slot_ready:
    mov.b @(192,gbr),r0
    extu.b r0,r5
    cmp/eq r5,r6
    bt accepted_slot
    bra pending_boundary
    nop
accepted_slot:
    mov.l ram_base,r14
    add #7,r8
    mov.w cursor_offset_a,r0
    mov.b r5,@(r0,r14)
    bra lookup_entry
    mov r5,r0
    .org 0x54c0e - 0x22694
negative_entry:
    mov.l ram_base,r3
    mov #0,r2
    mov.w pending_offset_a,r0
    mov.b r2,@(r0,r3)
    bra pending_boundary
    nop
    .org 0x54c1a - 0x22694
pending_offset_a:
    .word 0x0234
    .org 0x54c2c - 0x22694
cursor_offset_a:
    .word 0x022a
    .org 0x54c30 - 0x22694
ram_base:
    .long 0xffff1ff4
    .org 0x54d06 - 0x22694
lookup_entry:
    mov.b @(r0,r8),r2
    mov.w pending_offset_b,r0
    mov.b r2,@(r0,r14)
pending_boundary:
    .org 0x54dca - 0x22694
pending_offset_b:
    .word 0x0234
