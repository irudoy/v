! Complete 0008C942 with separate same-member OR08 and OR40 stores and the natural flag delay slot.
    .text
    .balign 4
    .set ORIGIN,0x8c942
L_0008c942:
    mov.l P_0008c98c,r1
    mov r4,r5
    shll r5
    mov r1,r6
    add r4,r5
    add r5,r6
    mov.b @(2,r6),r0
    mov #1,r2
    or #8,r0
    mov.b r0,@(2,r6)
    mov r1,r6
    add r5,r6
    mov.b @(2,r6),r0
    or #0x40,r0
    mov.b r0,@(2,r6)
    mov.l P_0008c998,r6
    mov.w P_0008c986,r0
    rts
    mov.b r2,@(r0,r6)
    .org 0x8c986-ORIGIN
P_0008c986:
    .word 0x0b27
    .org 0x8c98c-ORIGIN
P_0008c98c:
    .long 0xffff5718
    .org 0x8c998-ORIGIN
P_0008c998:
    .long 0xffff4558
