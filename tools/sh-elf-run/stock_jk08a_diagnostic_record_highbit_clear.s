! Complete natural stored-fault high-bit clearer with both stock RTS delay slots.
    .text
    .balign 4
    .set ORIGIN,0x8c348
L_0008c348:
    mov.l P_0008c45c,r1
    mov r4,r0
    cmp/eq #-1,r0
    bt L_0008c362
    mov r1,r6
    mov r4,r2
    shll r2
    add r4,r2
    add r2,r6
    mov.b @(1,r6),r0
    and #0x7f,r0
    rts
    mov.b r0,@(1,r6)
L_0008c362:
    rts
    nop
    .org 0x8c45c-ORIGIN
P_0008c45c:
    .long 0xffff5718
