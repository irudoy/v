    .text
    .balign 2
! stock_invoke(entry, r12, r0): call a stock region at `entry` with the base
! register r12 and r0 of its entry state and GBR 0, as the stock firmware runs;
! a block returns through the boundary RTS of the fixture and a whole function
! through its own RTS. r12, r13, GBR, and PR are restored for the caller, and
! the r0 of the return is the result.
    .global _stock_invoke
    .type _stock_invoke,@function
_stock_invoke:
    sts.l pr,@-r15
    stc.l gbr,@-r15
    mov.l r13,@-r15
    mov.l r12,@-r15
    mov r5,r12
    mov #0,r1
    ldc r1,gbr
    mov r6,r0
    jsr @r4
    nop
    mov.l @r15+,r12
    mov.l @r15+,r13
    ldc.l @r15+,gbr
    lds.l @r15+,pr
    rts
    nop
    .size _stock_invoke,.-_stock_invoke
