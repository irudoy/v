! Complete 0008C968 with independent SH-2E mnemonics and immutable stock PC literals.
    .text
    .balign 4
    .set ORIGIN,0x8c968
L_0008c968:
    mov.l P_0008c98c,r1
    mov r1,r6
    mov r4,r2
    shll r2
    add r4,r2
    add r2,r6
    mov.b @(2,r6),r0
    mov #1,r2
    or #0x10,r0
    mov.b r0,@(2,r6)
    mov.l P_0008c998,r6
    mov.w P_0008c988,r0
    rts
    mov.b r2,@(r0,r6)
    .org 0x8c988-ORIGIN
P_0008c988:
    .word 0x0b34
    .org 0x8c98c-ORIGIN
P_0008c98c:
    .long 0xffff5718
    .org 0x8c998-ORIGIN
P_0008c998:
    .long 0xffff4558
