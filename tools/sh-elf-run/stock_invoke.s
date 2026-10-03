    .text
    .balign 2
! stock_invoke(entry, r12, r0): call a stock region at `entry` with the base
! register r12 and r0 of its entry state and GBR 0;
! a block returns through the boundary RTS of the fixture and a whole function
! through its own RTS. r12, r13, GBR, and PR are restored for the caller, and
! the r0 of the return is the result.
    .global _stock_invoke
    .type _stock_invoke,@function
_stock_invoke:
    mov #0,r7
! stock_invoke_gbr(entry, r12, r0, gbr): the same preserved entry and return
! contract with the explicit GBR of a block inside a producer.
    .global _stock_invoke_gbr
    .type _stock_invoke_gbr,@function
_stock_invoke_gbr:
    sts.l pr,@-r15
    stc.l gbr,@-r15
    mov.l r13,@-r15
    mov.l r12,@-r15
    mov r5,r12
    ldc r7,gbr
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
    .size _stock_invoke_gbr,.-_stock_invoke_gbr

! stock_invoke_r1(entry, r1, r0): supply the unsigned divider's operands.
    .global _stock_invoke_r1
    .type _stock_invoke_r1,@function
_stock_invoke_r1:
    mov r5,r1
    mov #0,r5
    bra _stock_invoke
    nop
    .size _stock_invoke_r1,.-_stock_invoke_r1
