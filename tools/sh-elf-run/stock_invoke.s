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

! stock_invoke_curve(entry, table, coordinate): call the stock implicit entry.
    .global _stock_invoke_curve
    .type _stock_invoke_curve,@function
_stock_invoke_curve:
    sts.l pr,@-r15
    mov r4,r2
    mov r5,r4
    jsr @r2
    mov r6,r5
    lds.l @r15+,pr
    rts
    nop
    .size _stock_invoke_curve,.-_stock_invoke_curve

! Direct shared-body entry selects byte or word cells through R0.
! It receives only coordinates below the wrapper's last-cell boundary.
    .global _stock_invoke_format_curve
    .type _stock_invoke_format_curve,@function
_stock_invoke_format_curve:
    sts.l pr,@-r15
    mov r4,r2
    mov r5,r0
    mov r6,r4
    mov r7,r5
    jsr @r2
    mov #0,r3
    lds.l @r15+,pr
    rts
    nop
    .size _stock_invoke_format_curve,.-_stock_invoke_format_curve

! The MAF slice reads R4 from its already established MMIO-base context.
    .global _stock_invoke_adc
    .type _stock_invoke_adc,@function
_stock_invoke_adc:
    sts.l pr,@-r15
    mov r4,r2
    jsr @r2
    mov r5,r4
    lds.l @r15+,pr
    rts
    nop
    .size _stock_invoke_adc,.-_stock_invoke_adc

! stock_invoke_maf(entry, bank, macl, state): supply a bank byte or call the
! coefficient guard directly. Record MACL, R13, and R14 after the stock RTS.
    .global _stock_invoke_maf
    .type _stock_invoke_maf,@function
_stock_invoke_maf:
    mov.l r8,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l macl,@-r15
    mov r7,r8
    mov r4,r2
    lds r6,macl
    mov.l maf_saved_r13,r13
    mov.l maf_saved_r14,r14
    jsr @r2
    mov r5,r4
    bra maf_record_return
    nop
    .size _stock_invoke_maf,.-_stock_invoke_maf

! stock_invoke_maf_scale(entry, raw, destination, macl, state): call the
! scaler with a full register input and a guarded output word.
    .global _stock_invoke_maf_scale
    .type _stock_invoke_maf_scale,@function
_stock_invoke_maf_scale:
    mov.l r8,@-r15
    mov.l @(4,r15),r8
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l macl,@-r15
    mov r4,r2
    mov r5,r4
    mov r6,r5
    lds r7,macl
    mov.l maf_saved_r13,r13
    mov.l maf_saved_r14,r14
    jsr @r2
    nop
    bra maf_record_return
    nop
    .size _stock_invoke_maf_scale,.-_stock_invoke_maf_scale

! The producer's cap branch follows EXTU.W, which makes its taken outcome
! unreachable from the function entry. Direct entry at the stock CMP/GT
! supplies a wide R5 and the producer's saved PR/R14/R13 frame. The frame and
! continuation lie outside the tested code, and its natural epilogue returns.
    .global _stock_invoke_maf_cap
    .type _stock_invoke_maf_cap,@function
_stock_invoke_maf_cap:
    mov.l r8,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l macl,@-r15
    mov r7,r8
    mov r4,r2
    mov.l maf_cap_macl,r0
    lds r0,macl
    add #-16,r15
    mov #0,r0
    mov.l r0,@r15
    mov.l maf_cap_return_pointer,r0
    mov.l r0,@(4,r15)
    mov.l maf_saved_r14,r0
    mov.l r0,@(8,r15)
    mov.l maf_saved_r13,r0
    mov.l r0,@(12,r15)
    extu.b r6,r13
    shll r13
    mov #-1,r6
    extu.w r6,r6
    jmp @r2
    nop
maf_cap_return:
maf_record_return:
    sts macl,r2
    mov.l r2,@r8
    mov.l r13,@(4,r8)
    mov.l r14,@(8,r8)
    lds.l @r15+,macl
    lds.l @r15+,pr
    mov.l @r15+,r14
    mov.l @r15+,r13
    mov.l @r15+,r8
    rts
    nop
    .size _stock_invoke_maf_cap,.-_stock_invoke_maf_cap
    .balign 4
maf_saved_r13:
    .long 0x13579bdf
maf_saved_r14:
    .long 0x2468ace0
maf_cap_macl:
    .long 0x89abcdef
maf_cap_return_pointer:
    .long maf_cap_return

! stock_invoke_battery(entry, macl, state): seed a distinct GBR, call the
! complete stock battery publisher, and record MACL, R13, R14, and GBR.
    .global _stock_invoke_battery
    .type _stock_invoke_battery,@function
_stock_invoke_battery:
    mov.l r8,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    mov r6,r8
    mov r4,r2
    lds r5,macl
    mov.l battery_saved_r13,r13
    mov.l battery_saved_r14,r14
    mov.l battery_seed_gbr,r0
    ldc r0,gbr
    jsr @r2
    nop
    sts macl,r2
    mov.l r2,@r8
    mov.l r13,@(4,r8)
    mov.l r14,@(8,r8)
    stc gbr,r2
    mov.l r2,@(12,r8)
    ldc.l @r15+,gbr
    lds.l @r15+,macl
    lds.l @r15+,pr
    mov.l @r15+,r14
    mov.l @r15+,r13
    mov.l @r15+,r8
    rts
    nop
    .size _stock_invoke_battery,.-_stock_invoke_battery
    .balign 4
battery_saved_r13:
    .long 0x13579bdf
battery_saved_r14:
    .long 0x2468ace0
battery_seed_gbr:
    .long 0x13572468

! stock_invoke_compensation(entry, bank, macl, state): record MACL, R12,
! R13, R14, and GBR after the complete producer's natural stock return.
    .global _stock_invoke_compensation
    .type _stock_invoke_compensation,@function
_stock_invoke_compensation:
    mov.l r8,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    mov r7,r8
    mov r4,r2
    lds r6,macl
    mov.l compensation_saved_r12,r12
    mov.l compensation_saved_r13,r13
    mov.l compensation_saved_r14,r14
    mov.l compensation_saved_gbr,r0
    ldc r0,gbr
    jsr @r2
    mov r5,r4
    bra compensation_record
    nop
    .size _stock_invoke_compensation,.-_stock_invoke_compensation

! Stock bias 80 makes a zero denominator unreachable for a previous word.
! Direct entry at TST R7,R7 supplies zero and the producer's full saved frame.
! The natural epilogue restores GBR, MACL, PR, R14, R13, and R12; its tested
! instruction bytes are unchanged. The fifth argument is the state pointer.
    .global _stock_invoke_compensation_zero
    .type _stock_invoke_compensation_zero,@function
_stock_invoke_compensation_zero:
    mov.l r8,@-r15
    mov.l @(4,r15),r8
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    mov r4,r2
    mov r7,r14
    extu.b r5,r13
    shll r13
    add #-28,r15
    mov.w r6,@r15
    mov.l compensation_saved_gbr,r0
    mov.l r0,@(4,r15)
    mov.l compensation_saved_macl,r0
    mov.l r0,@(8,r15)
    mov.l compensation_zero_return_pointer,r0
    mov.l r0,@(12,r15)
    mov.l compensation_saved_r14,r0
    mov.l r0,@(16,r15)
    mov.l compensation_saved_r13,r0
    mov.l r0,@(20,r15)
    mov.l compensation_saved_r12,r0
    mov.l r0,@(24,r15)
    mov #0,r7
    jmp @r2
    nop
compensation_zero_return:
compensation_record:
    sts macl,r2
    mov.l r2,@r8
    mov.l r12,@(4,r8)
    mov.l r13,@(8,r8)
    mov.l r14,@(12,r8)
    stc gbr,r2
    mov.l r2,@(16,r8)
    ldc.l @r15+,gbr
    lds.l @r15+,macl
    lds.l @r15+,pr
    mov.l @r15+,r14
    mov.l @r15+,r13
    mov.l @r15+,r12
    mov.l @r15+,r8
    rts
    nop
    .size _stock_invoke_compensation_zero,.-_stock_invoke_compensation_zero
    .balign 4
compensation_saved_r12:
    .long 0x10203040
compensation_saved_r13:
    .long 0x13579bdf
compensation_saved_r14:
    .long 0x2468ace0
compensation_saved_gbr:
    .long 0x13572468
compensation_saved_macl:
    .long 0x89abcdef
compensation_zero_return_pointer:
    .long compensation_zero_return
