! Bounded positive-delta cursor and mask accumulation before flag/call dispatch.
    .text
    .balign 4
    .org 0x22695 - 0x22694
pending_masks:
    .byte 2,4,8,16,32,1
    .org 0x54c54 - 0x22694
catchup_entry:
    extu.b r6,r10
    mov #0,r11
    cmp/pl r10
    mov.l r11,@(12,r15)
    mov r11,r6
    bf/s catchup_boundary
    mov.l r11,@(16,r15)
    mov.l ram_base,r3
    mov.w cursor_offset,r0
    mov.l masks_base,r2
    mov.b @(r0,r3),r12
    mov.b @(193,gbr),r0
    mov.l r9,@r15
    mov #6,r9
    mov r0,r7
    mov.w mask_a_offset,r0
    mov.b @(r0,r2),r13
    mov.w mask_b_offset,r0
    mov.b @(r0,r2),r14
    mov.w clear_offset,r0
    mov.b @(r0,r2),r4
loop:
    mov.l ram_base,r3
    add #1,r12
    mov.w cursor_offset,r0
    mov.b r12,@(r0,r3)
    extu.b r12,r12
    cmp/ge r9,r12
    bf cursor_ready
    mov.l ram_base,r3
    mov #0,r12
    mov.b r12,@(r0,r3)
cursor_ready:
    mov r8,r2
    add #7,r2
    extu.b r12,r12
    mov r12,r0
    mov.b @(r0,r2),r5
    add #1,r11
    extu.b r5,r2
    cmp/ge r10,r11
    or r2,r6
    not r6,r2
    mov.l r6,@(16,r15)
    or r6,r7
    or r6,r13
    and r2,r4
    bf/s loop
    or r6,r14
    mov.l masks_base,r2
    mov.w clear_offset,r0
    mov.l r11,@(12,r15)
    mov.b r4,@(r0,r2)
    mov.w mask_b_offset,r0
    mov.l @r15,r9
    mov.b r14,@(r0,r2)
    mov.w mask_a_offset,r0
    mov.b r13,@(r0,r2)
    mov r7,r0
    mov.b r0,@(193,gbr)
catchup_boundary:
    .org 0x54dbe - 0x22694
cursor_offset: .word 0x022a
mask_a_offset: .word 0x02f2
mask_b_offset: .word 0x0472
clear_offset: .word 0x06a9
    .org 0x54e8c - 0x22694
ram_base: .long 0xffff1ff4
masks_base: .long 0xffff128c
