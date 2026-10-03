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

! stock_invoke_crank_period(entry, context): supply R8, R9, R10, R13,
! R6, the masked synchronization byte at SP+4, and R11 from context words.
! SP+0 is scratch space for the fallback caller; SP+8 holds the fixture's
! return continuation for a boundary that follows a stock JSR. Preserve the nonvolatile
! registers that either period slice changes, GBR, and PR for the harness.
    .global _stock_invoke_crank_period
    .type _stock_invoke_crank_period,@function
_stock_invoke_crank_period:
    sts.l pr,@-r15
    stc.l gbr,@-r15
    mov.l r13,@-r15
    mov.l r12,@-r15
    mov.l r11,@-r15
    mov.l r10,@-r15
    mov.l r9,@-r15
    mov.l r8,@-r15
    add #-12,r15
    mov.l @r5,r8
    mov.l @(4,r5),r9
    mov.l @(8,r5),r10
    mov.l @(12,r5),r13
    mov.l @(16,r5),r6
    mov.l @(20,r5),r0
    mov.b r0,@(4,r15)
    mov.l @(24,r5),r11
    mov.l crank_period_return_pointer,r0
    mov.l r0,@(8,r15)
    mov #0,r7
    ldc r7,gbr
    jsr @r4
    nop
crank_period_return:
    add #12,r15
    mov.l @r15+,r8
    mov.l @r15+,r9
    mov.l @r15+,r10
    mov.l @r15+,r11
    mov.l @r15+,r12
    mov.l @r15+,r13
    ldc.l @r15+,gbr
    lds.l @r15+,pr
    rts
    nop
    .size _stock_invoke_crank_period,.-_stock_invoke_crank_period
    .balign 4
crank_period_return_pointer:
    .long crank_period_return

! stock_invoke_axis(entry, last_offset, coordinate, axis, result): preserve
! the caller's R8 and PR, supply the kernel's R0/R4/R5 inputs, and return
! its offset and fraction registers through the fifth argument on the stack.
    .global _stock_invoke_axis
    .type _stock_invoke_axis,@function
_stock_invoke_axis:
    mov.l r8,@-r15
    mov.l @(4,r15),r8
    sts.l pr,@-r15
    mov r4,r2
    mov r5,r4
    mov r6,r5
    mov r7,r0
    jsr @r2
    nop
    mov.l r4,@r8
    mov.l r5,@(4,r8)
    lds.l @r15+,pr
    mov.l @r15+,r8
    rts
    nop
    .size _stock_invoke_axis,.-_stock_invoke_axis
