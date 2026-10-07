! Real reciprocal splitter at its original address.
    .text
    .balign 4
splitter:
    sts.l macl,@-r15
    mov.w reciprocal,r3
    mov r6,r7
    mul.l r4,r3
    sts macl,r2
    shlr16 r2
    mov r2,r6
    shll2 r6
    add r2,r6
    shll r6
    tst r6,r6
    bt/s remainder_store
    mov.w r2,@r5
    sub r6,r4
remainder_store:
    mov.b r4,@r7
    rts
    lds.l @r15+,macl
    .org 0x28ea0 - 0x28e7c
reciprocal:
    .word 0x199a

    .org 0x2b6ce - 0x28e7c
count_entry:
    mov.w @(0x12c,gbr),r0
    tst r0,r0
    bf saved_return
offset_entry:
    mov.l period_base,r2
    mov.w period_offset,r0
    mov.l ram_base,r13
    mov.w @(r0,r2),r6
    mov.w remainder_offset,r0
    extu.w r6,r6
    mov.b @(r0,r13),r2
    extu.b r2,r5
    mov.w output_offset,r2
    mul.l r6,r5
    mov r13,r5
    add r2,r5
    add #-0x56,r2
    mov r13,r6
    sts macl,r4
    mov.l splitter_pointer,r3
    jsr @r3
    add r2,r6
    .org 0x2b74a - 0x28e7c
saved_return:
    ldc.l @r15+,gbr
    lds.l @r15+,macl
    lds.l @r15+,pr
    mov.l @r15+,r14
    rts
    mov.l @r15+,r13
    .org 0x2b75e - 0x28e7c
remainder_offset: .word 0x06af
period_offset: .word 0x02c8
output_offset: .word 0x0436
    .org 0x2b864 - 0x28e7c
ram_base: .long 0xffff128c
    .org 0x2b86c - 0x28e7c
splitter_pointer: .long 0x00028e7c
    .org 0x2b874 - 0x28e7c
period_base: .long 0xffff1ff4
