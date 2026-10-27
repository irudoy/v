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

    .global _invoke_r0
    .type _invoke_r0,@function
_invoke_r0:
    sts.l pr,@-r15
    jsr @r4
    nop
    lds.l @r15+,pr
    rts
    nop
    .size _invoke_r0,.-_invoke_r0

    ! Supply the incoming coordinator result and observe the clamp R4/SR.
    ! The return boundary is outside the exact consumer instruction window.
    .global _invoke_throttle_scalar
    .type _invoke_throttle_scalar,@function
_invoke_throttle_scalar:
    sts.l pr,@-r15
    mov.l r6,@-r15
    mov r5,r0
    jsr @r4
    nop
    mov.l @r15+,r1
    stc sr,r2
    mov.l r2,@r1
    mov r4,r0
    lds.l @r15+,pr
    rts
    nop
    .size _invoke_throttle_scalar,.-_invoke_throttle_scalar
