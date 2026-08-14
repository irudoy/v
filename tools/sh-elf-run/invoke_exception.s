    .text
    .balign 2
    .global _invoke_exception_probe
    .type _invoke_exception_probe,@function
_invoke_exception_probe:
    sts.l pr,@-r15
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov r4,r9

    mov #1,r0
    mov #2,r1
    mov #3,r2
    mov #4,r3
    mov #5,r4
    mov #6,r5
    mov #7,r6
    mov #8,r7
    trapa #0x40
    mov.l r0,@r9
    add #4,r9
    mov.l r1,@r9
    add #4,r9
    mov.l r2,@r9
    add #4,r9
    mov.l r3,@r9
    add #4,r9
    mov.l r4,@r9
    add #4,r9
    mov.l r5,@r9
    add #4,r9
    mov.l r6,@r9
    add #4,r9
    mov.l r7,@r9

    mov.l @r15+,r9
    mov.l @r15+,r8
    lds.l @r15+,pr
    rts
    nop

    .size _invoke_exception_probe,.-_invoke_exception_probe
