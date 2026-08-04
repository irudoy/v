    .text
    .balign 2
    .global _invoke_r4
    .type _invoke_r4,@function
_invoke_r4:
    sts.l pr,@-r15
    mov r4,r0
    mov r5,r4
    jsr @r0
    nop
    mov r4,r0
    lds.l @r15+,pr
    rts
    nop
    .size _invoke_r4,.-_invoke_r4
