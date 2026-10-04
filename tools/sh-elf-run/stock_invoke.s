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

! Record the word wrapper's MACL after a natural return.
! The fifth argument supplies the result-state pointer.
    .global _stock_invoke_word_curve
    .type _stock_invoke_word_curve,@function
_stock_invoke_word_curve:
    mov.l r8,@-r15
    mov.l @(4,r15),r8
    sts.l pr,@-r15
    sts.l macl,@-r15
    mov r4,r2
    mov r5,r4
    lds r7,macl
    jsr @r2
    mov r6,r5
    sts macl,r1
    mov.l r1,@r8
    lds.l @r15+,macl
    lds.l @r15+,pr
    mov.l @r15+,r8
    rts
    nop
    .size _stock_invoke_word_curve,.-_stock_invoke_word_curve

! The MAF slice receives its input-window base in R14. Its calls replace PR;
! only the boundary after the second-bank delay-slot store restores PR.
    .global _stock_invoke_maf_transfer
    .type _stock_invoke_maf_transfer,@function
_stock_invoke_maf_transfer:
    mov.l r8,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    mov r7,r8
    mov r4,r2
    mov r5,r14
    lds r6,macl
    mov.l transfer_gbr_seed,r0
    ldc r0,gbr
    mov.l transfer_continuation,r0
    mov.l r0,@-r15
    jsr @r2
    nop
transfer_record_return:
    add #4,r15
    sts macl,r1
    mov.l r1,@r8
    mov.l r14,@(4,r8)
    stc gbr,r1
    mov.l r1,@(8,r8)
    ldc.l @r15+,gbr
    lds.l @r15+,macl
    lds.l @r15+,pr
    mov.l @r15+,r14
    mov.l @r15+,r8
    rts
    nop
    .balign 4
transfer_gbr_seed:
    .long 0x76543210
transfer_continuation:
    .long transfer_record_return
    .size _stock_invoke_maf_transfer,.-_stock_invoke_maf_transfer

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

! Direct entry supplies a wide R2 to the working copy's otherwise unreachable
! signed cap and zero branches. The context holds the mapped base and value.
    .global _stock_invoke_working_cap
    .type _stock_invoke_working_cap,@function
_stock_invoke_working_cap:
    mov.l r8,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    mov r7,r8
    mov r4,r3
    extu.b r5,r4
    shll r4
    mov.l @r6,r5
    mov.l @(4,r6),r2
    mov #-1,r6
    extu.w r6,r6
    mov.l compensation_saved_macl,r0
    lds r0,macl
    mov.l compensation_saved_r12,r12
    mov.l compensation_saved_r13,r13
    mov.l compensation_saved_r14,r14
    mov.l compensation_saved_gbr,r0
    ldc r0,gbr
    jsr @r3
    nop
    bra compensation_record
    nop
    .size _stock_invoke_working_cap,.-_stock_invoke_working_cap

! Direct anti-stall entry receives input, previous, and weighted words, mapped
! filter GBR, and MACL. Its stock frame holds saved GBR above saved MACL.
    .global _stock_invoke_filter_tail
    .type _stock_invoke_filter_tail,@function
_stock_invoke_filter_tail:
    mov.l r8,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    mov r7,r8
    mov r4,r3
    mov r6,r2
    extu.b r5,r1
    shll r1
    mov.l @r2,r6
    mov.l @(4,r2),r4
    mov.l @(8,r2),r7
    mov.l @(12,r2),r0
    ldc r0,gbr
    mov.l @(16,r2),r0
    lds r0,macl
    mov.l compensation_saved_r12,r12
    mov.l compensation_saved_r13,r13
    mov.l compensation_saved_r14,r14
    sts.l macl,@-r15
    mov.l compensation_saved_gbr,r0
    mov.l r0,@-r15
    jsr @r3
    nop
    bra compensation_record
    nop
    .size _stock_invoke_filter_tail,.-_stock_invoke_filter_tail

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

! Supply the normalization slice with its cached unsigned BFS in R5 and the
! stock unsigned divider in R11. SP+0 holds a simulator continuation for the
! boundary after the byte store; all tested instructions remain unchanged.
    .global _stock_invoke_normalized_load
    .type _stock_invoke_normalized_load,@function
_stock_invoke_normalized_load:
    mov.l r8,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    mov r7,r8
    mov r4,r3
    lds r6,macl
    mov.l normalization_divider,r11
    mov.l normalization_seed_r12,r12
    mov.l normalization_seed_r13,r13
    mov.l normalization_seed_r14,r14
    mov.l normalization_seed_gbr,r0
    ldc r0,gbr
    add #-4,r15
    mov.l normalization_return_pointer,r0
    mov.l r0,@r15
    jsr @r3
    nop
normalization_return:
    add #4,r15
    sts macl,r2
    mov.l r2,@r8
    mov.l r12,@(4,r8)
    mov.l r13,@(8,r8)
    mov.l r14,@(12,r8)
    stc gbr,r2
    mov.l r2,@(16,r8)
    mov.l r11,@(20,r8)
    ldc.l @r15+,gbr
    lds.l @r15+,macl
    lds.l @r15+,pr
    mov.l @r15+,r14
    mov.l @r15+,r13
    mov.l @r15+,r12
    mov.l @r15+,r11
    mov.l @r15+,r8
    rts
    nop
    .size _stock_invoke_normalized_load,.-_stock_invoke_normalized_load
    .balign 4
normalization_divider:
    .long 0x00021ce0
normalization_seed_r12:
    .long 0x10203040
normalization_seed_r13:
    .long 0x13579bdf
normalization_seed_r14:
    .long 0x2468ace0
normalization_seed_gbr:
    .long 0x13572468
normalization_return_pointer:
    .long normalization_return

! The contribution tail receives mapped GBR, signed residual, base word, and
! MACL after base clamping. A complete stock frame lets its natural epilogue
! restore GBR, MACL, PR, R14, and R13. These artificial contexts execute the
! otherwise unreachable signed 24-bit residual and output bounds.
    .global _stock_invoke_contribution_tail
    .type _stock_invoke_contribution_tail,@function
_stock_invoke_contribution_tail:
    mov.l r8,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    mov r7,r8
    mov r4,r3
    mov r6,r7
    mov.l contribution_saved_r12,r12
    mov.l contribution_saved_r13,r13
    mov.l contribution_saved_r14,r14
    mov.l @(12,r7),r0
    lds r0,macl
    mov.l contribution_saved_gbr,r0
    ldc r0,gbr
    mov.l r13,@-r15
    mov.l r14,@-r15
    mov.l contribution_return_pointer,r0
    mov.l r0,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    add #-28,r15
    extu.b r5,r13
    mov r13,r14
    shll r13
    shll2 r14
    add #1,r5
    mov.b r5,@r15
    mov.l @(4,r7),r0
    mov.l r0,@(4,r15)
    mov.l @(8,r7),r0
    mov.w r0,@(8,r15)
    mov.l @r7,r0
    ldc r0,gbr
    jmp @r3
    nop
contribution_return:
    bra compensation_record
    nop
    .size _stock_invoke_contribution_tail,.-_stock_invoke_contribution_tail
    .balign 4
contribution_saved_r12:
    .long 0x10203040
contribution_saved_r13:
    .long 0x13579bdf
contribution_saved_r14:
    .long 0x2468ace0
contribution_saved_gbr:
    .long 0x13572468
contribution_return_pointer:
    .long contribution_return

! Execute the selected primary quarter-BFS slice or Q7 consumer with an
! explicit incoming mode/speed/cache context. SP+24 holds the continuation
! restored by the boundary at 0003b908, outside tested instructions. R9 holds
! the result record; neither the selected arithmetic nor its helpers use it.
    .global _stock_invoke_bfs_base
    .type _stock_invoke_bfs_base,@function
_stock_invoke_bfs_base:
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    mov r6,r9
    mov r4,r3
    mov r5,r7
    add #-28,r15
    mov.l bfs_base_return_pointer,r0
    mov.l r0,@(24,r15)
    mov.l @(12,r7),r0
    ldc r0,gbr
    mov.l @(16,r7),r12
    mov.l @(20,r7),r11
    mov.l @(8,r7),r6
    mov.l @(4,r7),r5
    mov.l @r7,r4
    jsr @r3
    nop
bfs_base_return:
    add #28,r15
    sts macl,r2
    mov.l r2,@r9
    mov.l r6,@(4,r9)
    mov.l r13,@(8,r9)
    mov.l r14,@(12,r9)
    stc gbr,r2
    mov.l r2,@(16,r9)
    mov.l r11,@(20,r9)
    mov.l r12,@(24,r9)
    ldc.l @r15+,gbr
    lds.l @r15+,macl
    lds.l @r15+,pr
    mov.l @r15+,r14
    mov.l @r15+,r13
    mov.l @r15+,r12
    mov.l @r15+,r11
    mov.l @r15+,r10
    mov.l @r15+,r9
    mov.l @r15+,r8
    rts
    nop
    .size _stock_invoke_bfs_base,.-_stock_invoke_bfs_base
    .balign 4
bfs_base_return_pointer:
    .long bfs_base_return

! Supply the already selected word mode, correction cache, GBR, and MACL.
! The boundary after BFS publication restores PR from SP+0 outside stock code.
    .global _stock_invoke_bfs_limit
    .type _stock_invoke_bfs_limit,@function
_stock_invoke_bfs_limit:
    sts.l pr,@-r15
    stc.l gbr,@-r15
    sts.l macl,@-r15
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    mov r6,r8
    mov r4,r2
    mov.l @(4,r5),r7
    mov.l @(8,r5),r0
    ldc r0,gbr
    mov.l @(12,r5),r0
    lds r0,macl
    mov.l @r5,r5
    add #-4,r15
    mov.l bfs_limit_return_pointer,r0
    mov.l r0,@r15
    jsr @r2
    nop
bfs_limit_return:
    sts macl,r1
    mov.l r1,@r8
    stc gbr,r1
    mov.l r1,@(4,r8)
    mov.l r9,@(8,r8)
    add #4,r15
    mov.l @r15+,r14
    mov.l @r15+,r13
    mov.l @r15+,r12
    mov.l @r15+,r11
    mov.l @r15+,r10
    mov.l @r15+,r9
    mov.l @r15+,r8
    lds.l @r15+,macl
    ldc.l @r15+,gbr
    lds.l @r15+,pr
    rts
    nop
    .size _stock_invoke_bfs_limit,.-_stock_invoke_bfs_limit
    .balign 4
bfs_limit_return_pointer:
    .long bfs_limit_return

! The coordinator slice receives a coherent R10 base and unsigned RPM in R12.
! SP+0 is the byte-wrapper argument slot; SP+4 holds the return continuation.
    .global _stock_invoke_fuel_compensation
    .type _stock_invoke_fuel_compensation,@function
_stock_invoke_fuel_compensation:
    sts.l pr,@-r15
    stc.l gbr,@-r15
    sts.l macl,@-r15
    mov.l r8,@-r15
    mov.l r10,@-r15
    mov.l r12,@-r15
    add #-8,r15
    mov r6,r8
    mov r4,r2
    mov.l @r5,r10
    mov.l @(4,r5),r12
    mov.l @(8,r5),r0
    lds r0,macl
    mov.l @(12,r5),r0
    ldc r0,gbr
    mov.l compensation_return_pointer,r0
    mov.l r0,@(4,r15)
    jsr @r2
    nop
compensation_return:
    sts macl,r1
    mov.l r1,@r8
    stc gbr,r1
    mov.l r1,@(4,r8)
    mov.l r10,@(8,r8)
    mov.l r12,@(12,r8)
    mov.l r2,@(16,r8)
    add #8,r15
    mov.l @r15+,r12
    mov.l @r15+,r10
    mov.l @r15+,r8
    lds.l @r15+,macl
    ldc.l @r15+,gbr
    lds.l @r15+,pr
    rts
    nop
    .size _stock_invoke_fuel_compensation,.-_stock_invoke_fuel_compensation
    .balign 4
compensation_return_pointer:
    .long compensation_return

! Supply table and two axes in registers and the column byte at SP+3.
! Stack arguments are the row word, column byte, and recorded MACL pointer.
    .global _stock_invoke_surface
    .type _stock_invoke_surface,@function
_stock_invoke_surface:
    mov.l r8,@-r15
    mov.l @(4,r15),r0
    mov.l @(8,r15),r1
    mov.l @(12,r15),r8
    sts.l pr,@-r15
    sts.l macl,@-r15
    add #-4,r15
    mov r0,r3
    mov r1,r0
    mov.b r0,@(3,r15)
    mov r4,r2
    mov r5,r4
    mov r6,r5
    mov r7,r6
    mov r3,r7
    mov.l surface_macl_seed,r0
    lds r0,macl
    jsr @r2
    nop
    sts macl,r1
    mov.l r1,@r8
    add #4,r15
    lds.l @r15+,macl
    lds.l @r15+,pr
    mov.l @r15+,r8
    rts
    nop
    .size _stock_invoke_surface,.-_stock_invoke_surface
    .balign 4
surface_macl_seed:
    .long 0x12345678

! Simulator invokers distinguish the stock fragment frame from the C ABI.
! Exit fields hold SR, PR, MACL, MACH, GBR, R14..R0, and the fragment SP.
! The external continuation at SP+24 changes R1 after all tested instructions.
    .section .text
    .balign 4
    .global _stock_invoke_bfs_rate
    .type _stock_invoke_bfs_rate,@function
_stock_invoke_bfs_rate:
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l mach,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    add #-8,r15
    mov.l r6,@r15
    mov.l L_bfs_rate_abi8,r8
    mov.l L_bfs_rate_abi9,r9
    mov.l L_bfs_rate_abi10,r10
    mov.l L_bfs_rate_abi11,r11
    mov.l L_bfs_rate_abi12,r12
    mov.l L_bfs_rate_abi13,r13
    mov.l L_bfs_rate_abi14,r14
    mov.l L_bfs_rate_abigbr,r0
    ldc r0,gbr
    mov.l L_bfs_rate_abimach,r0
    lds r0,mach
    mov.l L_bfs_rate_abimacl,r0
    lds r0,macl
    bsr L_bfs_rate_inner
    nop
L_bfs_rate_outer_return:
    mov.l @r15,r3
    mov r3,r2
    add #100,r2
    add #36,r2
    mov.l r8,@r2
    add #4,r2
    mov.l r9,@r2
    add #4,r2
    mov.l r10,@r2
    add #4,r2
    mov.l r11,@r2
    add #4,r2
    mov.l r12,@r2
    add #4,r2
    mov.l r13,@r2
    add #4,r2
    mov.l r14,@r2
    add #4,r2
    stc gbr,r0
    mov.l r0,@r2
    add #4,r2
    sts mach,r0
    mov.l r0,@r2
    add #4,r2
    sts macl,r0
    mov.l r0,@r2
    add #4,r2
    mov.l r15,@r2
    add #4,r2
    sts pr,r0
    mov.l r0,@r2
    add #8,r15
    ldc.l @r15+,gbr
    lds.l @r15+,macl
    lds.l @r15+,mach
    lds.l @r15+,pr
    mov.l @r15+,r14
    mov.l @r15+,r13
    mov.l @r15+,r12
    mov.l @r15+,r11
    mov.l @r15+,r10
    mov.l @r15+,r9
    mov.l @r15+,r8
    rts
    mov #0,r0
    .balign 4
L_bfs_rate_abi8: .long 0x18283848
L_bfs_rate_abi9: .long 0x19293949
L_bfs_rate_abi10: .long 0x1a2a3a4a
L_bfs_rate_abi11: .long 0x1b2b3b4b
L_bfs_rate_abi12: .long 0x1c2c3c4c
L_bfs_rate_abi13: .long 0x1d2d3d4d
L_bfs_rate_abi14: .long 0x1e2e3e4e
L_bfs_rate_abigbr: .long 0x12344321
L_bfs_rate_abimach: .long 0x10203040
L_bfs_rate_abimacl: .long 0x50607080

L_bfs_rate_inner:
    mov r6,r2
    add #88,r2
    mov.l r8,@r2
    add #4,r2
    mov.l r9,@r2
    add #4,r2
    mov.l r10,@r2
    add #4,r2
    mov.l r11,@r2
    add #4,r2
    mov.l r12,@r2
    add #4,r2
    mov.l r13,@r2
    add #4,r2
    mov.l r14,@r2
    add #4,r2
    stc gbr,r0
    mov.l r0,@r2
    add #4,r2
    sts mach,r0
    mov.l r0,@r2
    add #4,r2
    sts macl,r0
    mov.l r0,@r2
    add #4,r2
    mov.l r15,@r2
    add #4,r2
    sts pr,r0
    mov.l r0,@r2
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l mach,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    add #-32,r15
    mov.l L_bfs_rate_frame_seed,r0
    mov r15,r1
    mov #8,r2
L_bfs_rate_seed_frame:
    mov.l r0,@r1
    add #4,r1
    add #17,r0
    dt r2
    bf L_bfs_rate_seed_frame
    mov.l r6,@r15
    mov.l r4,@(4,r15)
    mov r5,r3
    mov.l L_bfs_rate_return_pointer,r0
    mov.l r0,@(24,r15)
    mov r3,r2
    add #64,r2
    mov.l @r2+,r0
    lds r0,mach
    mov.l @r2+,r0
    lds r0,macl
    mov.l @r2,r0
    mov r0,r2
    mov #16,r0
    mov.b r2,@(r0,r15)
    mov.l @r15,r2
    add #100,r2
    add #84,r2
    mov r15,r1
    mov #8,r0
L_bfs_rate_copy_frame_before:
    mov.l @r1+,r4
    mov.l r4,@r2
    add #4,r2
    dt r0
    bf L_bfs_rate_copy_frame_before
    mov.l @(60,r3),r0
    ldc r0,gbr
    mov.l @(16,r3),r4
    mov.l @(20,r3),r5
    mov.l @(24,r3),r6
    mov.l @(28,r3),r7
    mov.l @(32,r3),r8
    mov.l @(36,r3),r9
    mov.l @(40,r3),r10
    mov.l @(44,r3),r11
    mov.l @(48,r3),r12
    mov.l @(52,r3),r13
    mov.l @(56,r3),r14
    mov.l @(0,r3),r0
    mov.l @(8,r3),r2
    mov.l @(12,r3),r3
    mov.l @(4,r15),r1
    jsr @r1
    nop
L_bfs_rate_return:
    mov.l r0,@-r15
    mov.l r1,@-r15
    mov.l r2,@-r15
    mov.l r3,@-r15
    mov.l r4,@-r15
    mov.l r5,@-r15
    mov.l r6,@-r15
    mov.l r7,@-r15
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    stc.l gbr,@-r15
    sts.l mach,@-r15
    sts.l macl,@-r15
    sts.l pr,@-r15
    stc.l sr,@-r15
    mov r15,r1
    mov r15,r0
    add #80,r0
    mov.l @r0,r3
    mov r3,r2
    mov #20,r4
L_bfs_rate_copy_exit:
    mov.l @r1+,r5
    mov.l r5,@r2
    add #4,r2
    dt r4
    bf L_bfs_rate_copy_exit
    mov.l r0,@r2
    add #4,r2
    mov r0,r1
    add #24,r1
    mov.l @r1,r5
    mov.l r5,@r2
    mov r3,r2
    add #108,r2
    add #108,r2
    mov r0,r1
    mov #8,r4
L_bfs_rate_copy_frame_after:
    mov.l @r1+,r5
    mov.l r5,@r2
    add #4,r2
    dt r4
    bf L_bfs_rate_copy_frame_after
    add #80,r15
    add #32,r15
    ldc.l @r15+,gbr
    lds.l @r15+,macl
    lds.l @r15+,mach
    lds.l @r15+,pr
    mov.l @r15+,r14
    mov.l @r15+,r13
    mov.l @r15+,r12
    mov.l @r15+,r11
    mov.l @r15+,r10
    mov.l @r15+,r9
    mov.l @r15+,r8
    rts
    nop
    .balign 4
L_bfs_rate_return_pointer: .long L_bfs_rate_return
L_bfs_rate_frame_seed: .long 0xd1e2f304
    .size _stock_invoke_bfs_rate,.-_stock_invoke_bfs_rate

! Simulator helper records the complete stock exit separately from the C caller ABI.
! R7 supplies the driver call target; the tested entries do not read incoming R7.
! The positive 80-byte exit buffer preserves the stock stack footprint below SP.
    .section .text
    .balign 4
    .global _stock_invoke_knock_threshold
    .type _stock_invoke_knock_threshold,@function
_stock_invoke_knock_threshold:
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l mach,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    add #-8,r15
    mov.l r6,@r15
    mov.l L_knock_threshold_abi8,r8
    mov.l L_knock_threshold_abi9,r9
    mov.l L_knock_threshold_abi10,r10
    mov.l L_knock_threshold_abi11,r11
    mov.l L_knock_threshold_abi12,r12
    mov.l L_knock_threshold_abi13,r13
    mov.l L_knock_threshold_abi14,r14
    mov.l L_knock_threshold_abigbr,r0
    ldc r0,gbr
    mov.l L_knock_threshold_abimach,r0
    lds r0,mach
    mov.l L_knock_threshold_abimacl,r0
    lds r0,macl
    bsr L_knock_threshold_inner
    nop
L_knock_threshold_outer_return:
    mov.l @r15,r6
    mov r6,r2
    add #100,r2
    add #36,r2
    mov.l r8,@r2
    add #4,r2
    mov.l r9,@r2
    add #4,r2
    mov.l r10,@r2
    add #4,r2
    mov.l r11,@r2
    add #4,r2
    mov.l r12,@r2
    add #4,r2
    mov.l r13,@r2
    add #4,r2
    mov.l r14,@r2
    add #4,r2
    stc gbr,r0
    mov.l r0,@r2
    add #4,r2
    sts mach,r0
    mov.l r0,@r2
    add #4,r2
    sts macl,r0
    mov.l r0,@r2
    add #4,r2
    mov.l r15,@r2
    add #4,r2
    sts pr,r0
    mov.l r0,@r2
    add #8,r15
    ldc.l @r15+,gbr
    lds.l @r15+,macl
    lds.l @r15+,mach
    lds.l @r15+,pr
    mov.l @r15+,r14
    mov.l @r15+,r13
    mov.l @r15+,r12
    mov.l @r15+,r11
    mov.l @r15+,r10
    mov.l @r15+,r9
    mov.l @r15+,r8
    rts
    mov #0,r0
    .balign 4
L_knock_threshold_abi8: .long 0x18283848
L_knock_threshold_abi9: .long 0x19293949
L_knock_threshold_abi10: .long 0x1a2a3a4a
L_knock_threshold_abi11: .long 0x1b2b3b4b
L_knock_threshold_abi12: .long 0x1c2c3c4c
L_knock_threshold_abi13: .long 0x1d2d3d4d
L_knock_threshold_abi14: .long 0x1e2e3e4e
L_knock_threshold_abigbr: .long 0x12344321
L_knock_threshold_abimach: .long 0x10203040
L_knock_threshold_abimacl: .long 0x50607080
L_knock_threshold_inner:
    mov r6,r2
    add #88,r2
    mov.l r8,@r2
    add #4,r2
    mov.l r9,@r2
    add #4,r2
    mov.l r10,@r2
    add #4,r2
    mov.l r11,@r2
    add #4,r2
    mov.l r12,@r2
    add #4,r2
    mov.l r13,@r2
    add #4,r2
    mov.l r14,@r2
    add #4,r2
    stc gbr,r0
    mov.l r0,@r2
    add #4,r2
    sts mach,r0
    mov.l r0,@r2
    add #4,r2
    sts macl,r0
    mov.l r0,@r2
    add #4,r2
    mov.l r15,@r2
    add #4,r2
    sts pr,r0
    mov.l r0,@r2
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l mach,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    add #-88,r15
    mov #80,r0
    mov.l r6,@(r0,r15)
    add #4,r0
    mov.l r4,@(r0,r15)
    mov r5,r3
    mov r15,r1
    add #-32,r1
    mov.l L_knock_threshold_frame_seed,r0
    mov #8,r2
L_knock_threshold_seed_frame:
    mov.l r0,@r1
    add #4,r1
    add #17,r0
    dt r2
    bf L_knock_threshold_seed_frame
    mov r6,r2
    add #100,r2
    add #84,r2
    mov r15,r1
    add #-32,r1
    mov #8,r0
L_knock_threshold_frame_before:
    mov.l @r1+,r4
    mov.l r4,@r2
    add #4,r2
    dt r0
    bf L_knock_threshold_frame_before
    mov.l @(60,r3),r0
    ldc r0,gbr
    mov r3,r2
    add #64,r2
    mov.l @r2+,r0
    lds r0,mach
    mov.l @r2,r0
    lds r0,macl
    mov.l @(16,r3),r4
    mov.l @(20,r3),r5
    mov.l @(24,r3),r6
    mov.l @(28,r3),r7
    mov.l @(32,r3),r8
    mov.l @(36,r3),r9
    mov.l @(40,r3),r10
    mov.l @(44,r3),r11
    mov.l @(48,r3),r12
    mov.l @(52,r3),r13
    mov.l @(56,r3),r14
    mov.l @(0,r3),r0
    mov.l @(4,r3),r1
    mov.l @(8,r3),r2
    mov.l @(12,r3),r3
    mov r15,r7
    add #84,r7
    mov.l @r7,r7
    jsr @r7
    nop
L_knock_threshold_stock_return:
    add #80,r15
    mov.l r0,@-r15
    mov.l r1,@-r15
    mov.l r2,@-r15
    mov.l r3,@-r15
    mov.l r4,@-r15
    mov.l r5,@-r15
    mov.l r6,@-r15
    mov.l r7,@-r15
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    stc.l gbr,@-r15
    sts.l mach,@-r15
    sts.l macl,@-r15
    sts.l pr,@-r15
    stc.l sr,@-r15
    mov r15,r1
    mov r15,r0
    add #80,r0
    mov.l @r0,r3
    mov r3,r2
    mov #20,r4
L_knock_threshold_copy_exit:
    mov.l @r1+,r5
    mov.l r5,@r2
    add #4,r2
    dt r4
    bf L_knock_threshold_copy_exit
    mov.l r15,@r2
    add #4,r2
    mov.l L_knock_threshold_return_pointer,r0
    mov.l r0,@r2
    mov r3,r2
    add #108,r2
    add #108,r2
    mov r15,r1
    add #-32,r1
    mov #8,r4
L_knock_threshold_frame_after:
    mov.l @r1+,r5
    mov.l r5,@r2
    add #4,r2
    dt r4
    bf L_knock_threshold_frame_after
    add #88,r15
    ldc.l @r15+,gbr
    lds.l @r15+,macl
    lds.l @r15+,mach
    lds.l @r15+,pr
    mov.l @r15+,r14
    mov.l @r15+,r13
    mov.l @r15+,r12
    mov.l @r15+,r11
    mov.l @r15+,r10
    mov.l @r15+,r9
    mov.l @r15+,r8
    rts
    nop
    .balign 4
L_knock_threshold_frame_seed: .long 0xa3b4c5d6
L_knock_threshold_return_pointer: .long L_knock_threshold_stock_return
    .size _stock_invoke_knock_threshold,.-_stock_invoke_knock_threshold

! Simulator helper records the complete stock exit separately from the C caller ABI.
! R7 supplies the driver call target; the tested entries do not read incoming R7.
! The 20-byte local frame precedes the 80-byte exit buffer.
! Comparison changes only local byte SP+12; SP+16 holds the boundary continuation.
! The boundary restores driver PR and R1 outside every checked code span.
    .section .text
    .balign 4
    .global _stock_invoke_knock_comparison
    .type _stock_invoke_knock_comparison,@function
_stock_invoke_knock_comparison:
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l mach,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    add #-8,r15
    mov.l r6,@r15
    mov.l L_knock_comparison_abi8,r8
    mov.l L_knock_comparison_abi9,r9
    mov.l L_knock_comparison_abi10,r10
    mov.l L_knock_comparison_abi11,r11
    mov.l L_knock_comparison_abi12,r12
    mov.l L_knock_comparison_abi13,r13
    mov.l L_knock_comparison_abi14,r14
    mov.l L_knock_comparison_abigbr,r0
    ldc r0,gbr
    mov.l L_knock_comparison_abimach,r0
    lds r0,mach
    mov.l L_knock_comparison_abimacl,r0
    lds r0,macl
    bsr L_knock_comparison_inner
    nop
L_knock_comparison_outer_return:
    mov.l @r15,r6
    mov r6,r2
    add #100,r2
    add #36,r2
    mov.l r8,@r2
    add #4,r2
    mov.l r9,@r2
    add #4,r2
    mov.l r10,@r2
    add #4,r2
    mov.l r11,@r2
    add #4,r2
    mov.l r12,@r2
    add #4,r2
    mov.l r13,@r2
    add #4,r2
    mov.l r14,@r2
    add #4,r2
    stc gbr,r0
    mov.l r0,@r2
    add #4,r2
    sts mach,r0
    mov.l r0,@r2
    add #4,r2
    sts macl,r0
    mov.l r0,@r2
    add #4,r2
    mov.l r15,@r2
    add #4,r2
    sts pr,r0
    mov.l r0,@r2
    add #8,r15
    ldc.l @r15+,gbr
    lds.l @r15+,macl
    lds.l @r15+,mach
    lds.l @r15+,pr
    mov.l @r15+,r14
    mov.l @r15+,r13
    mov.l @r15+,r12
    mov.l @r15+,r11
    mov.l @r15+,r10
    mov.l @r15+,r9
    mov.l @r15+,r8
    rts
    mov #0,r0
    .balign 4
L_knock_comparison_abi8: .long 0x18283848
L_knock_comparison_abi9: .long 0x19293949
L_knock_comparison_abi10: .long 0x1a2a3a4a
L_knock_comparison_abi11: .long 0x1b2b3b4b
L_knock_comparison_abi12: .long 0x1c2c3c4c
L_knock_comparison_abi13: .long 0x1d2d3d4d
L_knock_comparison_abi14: .long 0x1e2e3e4e
L_knock_comparison_abigbr: .long 0x12344321
L_knock_comparison_abimach: .long 0x10203040
L_knock_comparison_abimacl: .long 0x50607080
L_knock_comparison_inner:
    mov r6,r2
    add #88,r2
    mov.l r8,@r2
    add #4,r2
    mov.l r9,@r2
    add #4,r2
    mov.l r10,@r2
    add #4,r2
    mov.l r11,@r2
    add #4,r2
    mov.l r12,@r2
    add #4,r2
    mov.l r13,@r2
    add #4,r2
    mov.l r14,@r2
    add #4,r2
    stc gbr,r0
    mov.l r0,@r2
    add #4,r2
    sts mach,r0
    mov.l r0,@r2
    add #4,r2
    sts macl,r0
    mov.l r0,@r2
    add #4,r2
    mov.l r15,@r2
    add #4,r2
    sts pr,r0
    mov.l r0,@r2
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l mach,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    add #-108,r15
    mov #100,r0
    mov.l r6,@(r0,r15)
    add #4,r0
    mov.l r4,@(r0,r15)
    mov r5,r3
    mov r15,r1
    add #-32,r1
    mov.l L_knock_comparison_frame_seed,r0
    mov #8,r2
L_knock_comparison_seed_frame:
    mov.l r0,@r1
    add #4,r1
    add #17,r0
    dt r2
    bf L_knock_comparison_seed_frame
    mov r15,r1
    mov #5,r2
L_knock_comparison_seed_local:
    mov.l r0,@r1
    add #4,r1
    add #17,r0
    dt r2
    bf L_knock_comparison_seed_local
    mov.l L_knock_comparison_return_pointer,r0
    mov.l r0,@(16,r15)
    mov r6,r2
    add #100,r2
    add #84,r2
    mov r15,r1
    add #-32,r1
    mov #13,r0
L_knock_comparison_frame_before:
    mov.l @r1+,r4
    mov.l r4,@r2
    add #4,r2
    dt r0
    bf L_knock_comparison_frame_before
    mov.l @(60,r3),r0
    ldc r0,gbr
    mov r3,r2
    add #64,r2
    mov.l @r2+,r0
    lds r0,mach
    mov.l @r2,r0
    lds r0,macl
    mov.l @(16,r3),r4
    mov.l @(20,r3),r5
    mov.l @(24,r3),r6
    mov.l @(28,r3),r7
    mov.l @(32,r3),r8
    mov.l @(36,r3),r9
    mov.l @(40,r3),r10
    mov.l @(44,r3),r11
    mov.l @(48,r3),r12
    mov.l @(52,r3),r13
    mov.l @(56,r3),r14
    mov.l @(0,r3),r0
    mov.l @(4,r3),r1
    mov.l @(8,r3),r2
    mov.l @(12,r3),r3
    mov r15,r7
    add #104,r7
    mov.l @r7,r7
    jsr @r7
    nop
L_knock_comparison_stock_return:
    add #100,r15
    mov.l r0,@-r15
    mov.l r1,@-r15
    mov.l r2,@-r15
    mov.l r3,@-r15
    mov.l r4,@-r15
    mov.l r5,@-r15
    mov.l r6,@-r15
    mov.l r7,@-r15
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    stc.l gbr,@-r15
    sts.l mach,@-r15
    sts.l macl,@-r15
    sts.l pr,@-r15
    stc.l sr,@-r15
    mov r15,r1
    mov r15,r0
    add #80,r0
    mov.l @r0,r3
    mov r3,r2
    mov #20,r4
L_knock_comparison_copy_exit:
    mov.l @r1+,r5
    mov.l r5,@r2
    add #4,r2
    dt r4
    bf L_knock_comparison_copy_exit
    mov r15,r0
    add #-20,r0
    mov.l r0,@r2
    add #4,r2
    mov.l L_knock_comparison_return_pointer,r0
    mov.l r0,@r2
    mov r3,r2
    add #118,r2
    add #118,r2
    mov r15,r1
    add #-52,r1
    mov #13,r4
L_knock_comparison_frame_after:
    mov.l @r1+,r5
    mov.l r5,@r2
    add #4,r2
    dt r4
    bf L_knock_comparison_frame_after
    add #88,r15
    ldc.l @r15+,gbr
    lds.l @r15+,macl
    lds.l @r15+,mach
    lds.l @r15+,pr
    mov.l @r15+,r14
    mov.l @r15+,r13
    mov.l @r15+,r12
    mov.l @r15+,r11
    mov.l @r15+,r10
    mov.l @r15+,r9
    mov.l @r15+,r8
    rts
    nop
    .balign 4
L_knock_comparison_frame_seed: .long 0xa3b4c5d6
L_knock_comparison_return_pointer: .long L_knock_comparison_stock_return

    .size _stock_invoke_knock_comparison,.-_stock_invoke_knock_comparison

! Simulator helper records the complete stock exit separately from the C caller ABI.
! R7 supplies the driver call target; the tested entries do not read incoming R7.
! The 20-byte local frame precedes the 80-byte exit buffer.
! The stock slice preserves the seeded local frame and every stack neighbor.
! The ordinary RTS/NOP boundary returns through incoming driver PR.
    .section .text
    .balign 4
    .global _stock_invoke_knock_timing_byte
    .type _stock_invoke_knock_timing_byte,@function
_stock_invoke_knock_timing_byte:
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l mach,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    add #-8,r15
    mov.l r6,@r15
    mov.l L_knock_timing_byte_abi8,r8
    mov.l L_knock_timing_byte_abi9,r9
    mov.l L_knock_timing_byte_abi10,r10
    mov.l L_knock_timing_byte_abi11,r11
    mov.l L_knock_timing_byte_abi12,r12
    mov.l L_knock_timing_byte_abi13,r13
    mov.l L_knock_timing_byte_abi14,r14
    mov.l L_knock_timing_byte_abigbr,r0
    ldc r0,gbr
    mov.l L_knock_timing_byte_abimach,r0
    lds r0,mach
    mov.l L_knock_timing_byte_abimacl,r0
    lds r0,macl
    bsr L_knock_timing_byte_inner
    nop
L_knock_timing_byte_outer_return:
    mov.l @r15,r6
    mov r6,r2
    add #100,r2
    add #36,r2
    mov.l r8,@r2
    add #4,r2
    mov.l r9,@r2
    add #4,r2
    mov.l r10,@r2
    add #4,r2
    mov.l r11,@r2
    add #4,r2
    mov.l r12,@r2
    add #4,r2
    mov.l r13,@r2
    add #4,r2
    mov.l r14,@r2
    add #4,r2
    stc gbr,r0
    mov.l r0,@r2
    add #4,r2
    sts mach,r0
    mov.l r0,@r2
    add #4,r2
    sts macl,r0
    mov.l r0,@r2
    add #4,r2
    mov.l r15,@r2
    add #4,r2
    sts pr,r0
    mov.l r0,@r2
    add #8,r15
    ldc.l @r15+,gbr
    lds.l @r15+,macl
    lds.l @r15+,mach
    lds.l @r15+,pr
    mov.l @r15+,r14
    mov.l @r15+,r13
    mov.l @r15+,r12
    mov.l @r15+,r11
    mov.l @r15+,r10
    mov.l @r15+,r9
    mov.l @r15+,r8
    rts
    mov #0,r0
    .balign 4
L_knock_timing_byte_abi8: .long 0x18283848
L_knock_timing_byte_abi9: .long 0x19293949
L_knock_timing_byte_abi10: .long 0x1a2a3a4a
L_knock_timing_byte_abi11: .long 0x1b2b3b4b
L_knock_timing_byte_abi12: .long 0x1c2c3c4c
L_knock_timing_byte_abi13: .long 0x1d2d3d4d
L_knock_timing_byte_abi14: .long 0x1e2e3e4e
L_knock_timing_byte_abigbr: .long 0x12344321
L_knock_timing_byte_abimach: .long 0x10203040
L_knock_timing_byte_abimacl: .long 0x50607080
L_knock_timing_byte_inner:
    mov r6,r2
    add #88,r2
    mov.l r8,@r2
    add #4,r2
    mov.l r9,@r2
    add #4,r2
    mov.l r10,@r2
    add #4,r2
    mov.l r11,@r2
    add #4,r2
    mov.l r12,@r2
    add #4,r2
    mov.l r13,@r2
    add #4,r2
    mov.l r14,@r2
    add #4,r2
    stc gbr,r0
    mov.l r0,@r2
    add #4,r2
    sts mach,r0
    mov.l r0,@r2
    add #4,r2
    sts macl,r0
    mov.l r0,@r2
    add #4,r2
    mov.l r15,@r2
    add #4,r2
    sts pr,r0
    mov.l r0,@r2
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l mach,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    add #-108,r15
    mov #100,r0
    mov.l r6,@(r0,r15)
    add #4,r0
    mov.l r4,@(r0,r15)
    mov r5,r3
    mov r15,r1
    add #-32,r1
    mov.l L_knock_timing_byte_frame_seed,r0
    mov #8,r2
L_knock_timing_byte_seed_frame:
    mov.l r0,@r1
    add #4,r1
    add #17,r0
    dt r2
    bf L_knock_timing_byte_seed_frame
    mov r15,r1
    mov #5,r2
L_knock_timing_byte_seed_local:
    mov.l r0,@r1
    add #4,r1
    add #17,r0
    dt r2
    bf L_knock_timing_byte_seed_local
    mov.l L_knock_timing_byte_return_pointer,r0
    mov.l r0,@(16,r15)
    mov r6,r2
    add #100,r2
    add #84,r2
    mov r15,r1
    add #-32,r1
    mov #13,r0
L_knock_timing_byte_frame_before:
    mov.l @r1+,r4
    mov.l r4,@r2
    add #4,r2
    dt r0
    bf L_knock_timing_byte_frame_before
    mov.l @(60,r3),r0
    ldc r0,gbr
    mov r3,r2
    add #64,r2
    mov.l @r2+,r0
    lds r0,mach
    mov.l @r2,r0
    lds r0,macl
    mov.l @(16,r3),r4
    mov.l @(20,r3),r5
    mov.l @(24,r3),r6
    mov.l @(28,r3),r7
    mov.l @(32,r3),r8
    mov.l @(36,r3),r9
    mov.l @(40,r3),r10
    mov.l @(44,r3),r11
    mov.l @(48,r3),r12
    mov.l @(52,r3),r13
    mov.l @(56,r3),r14
    mov.l @(0,r3),r0
    mov.l @(4,r3),r1
    mov.l @(8,r3),r2
    mov.l @(12,r3),r3
    mov r15,r7
    add #104,r7
    mov.l @r7,r7
    jsr @r7
    nop
L_knock_timing_byte_stock_return:
    add #100,r15
    mov.l r0,@-r15
    mov.l r1,@-r15
    mov.l r2,@-r15
    mov.l r3,@-r15
    mov.l r4,@-r15
    mov.l r5,@-r15
    mov.l r6,@-r15
    mov.l r7,@-r15
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    stc.l gbr,@-r15
    sts.l mach,@-r15
    sts.l macl,@-r15
    sts.l pr,@-r15
    stc.l sr,@-r15
    mov r15,r1
    mov r15,r0
    add #80,r0
    mov.l @r0,r3
    mov r3,r2
    mov #20,r4
L_knock_timing_byte_copy_exit:
    mov.l @r1+,r5
    mov.l r5,@r2
    add #4,r2
    dt r4
    bf L_knock_timing_byte_copy_exit
    mov r15,r0
    add #-20,r0
    mov.l r0,@r2
    add #4,r2
    mov.l L_knock_timing_byte_return_pointer,r0
    mov.l r0,@r2
    mov r3,r2
    add #118,r2
    add #118,r2
    mov r15,r1
    add #-52,r1
    mov #13,r4
L_knock_timing_byte_frame_after:
    mov.l @r1+,r5
    mov.l r5,@r2
    add #4,r2
    dt r4
    bf L_knock_timing_byte_frame_after
    add #88,r15
    ldc.l @r15+,gbr
    lds.l @r15+,macl
    lds.l @r15+,mach
    lds.l @r15+,pr
    mov.l @r15+,r14
    mov.l @r15+,r13
    mov.l @r15+,r12
    mov.l @r15+,r11
    mov.l @r15+,r10
    mov.l @r15+,r9
    mov.l @r15+,r8
    rts
    nop
    .balign 4
L_knock_timing_byte_frame_seed: .long 0xa3b4c5d6
L_knock_timing_byte_return_pointer: .long L_knock_timing_byte_stock_return

    .size _stock_invoke_knock_timing_byte,.-_stock_invoke_knock_timing_byte

! Simulator helper records the complete stock exit separately from the C caller ABI.
! R7 supplies the driver call target; the tested entries do not read incoming R7.
! The 20-byte local frame precedes the 80-byte exit buffer.
! The stock slice preserves the seeded local frame and every stack neighbor.
! The ordinary RTS/NOP boundary returns through incoming driver PR.
    .section .text
    .balign 4
    .global _stock_invoke_knock_integration
    .type _stock_invoke_knock_integration,@function
_stock_invoke_knock_integration:
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l mach,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    add #-8,r15
    mov.l r6,@r15
    mov.l L_knock_integration_abi8,r8
    mov.l L_knock_integration_abi9,r9
    mov.l L_knock_integration_abi10,r10
    mov.l L_knock_integration_abi11,r11
    mov.l L_knock_integration_abi12,r12
    mov.l L_knock_integration_abi13,r13
    mov.l L_knock_integration_abi14,r14
    mov.l L_knock_integration_abigbr,r0
    ldc r0,gbr
    mov.l L_knock_integration_abimach,r0
    lds r0,mach
    mov.l L_knock_integration_abimacl,r0
    lds r0,macl
    bsr L_knock_integration_inner
    nop
L_knock_integration_outer_return:
    mov.l @r15,r6
    mov r6,r2
    add #100,r2
    add #36,r2
    mov.l r8,@r2
    add #4,r2
    mov.l r9,@r2
    add #4,r2
    mov.l r10,@r2
    add #4,r2
    mov.l r11,@r2
    add #4,r2
    mov.l r12,@r2
    add #4,r2
    mov.l r13,@r2
    add #4,r2
    mov.l r14,@r2
    add #4,r2
    stc gbr,r0
    mov.l r0,@r2
    add #4,r2
    sts mach,r0
    mov.l r0,@r2
    add #4,r2
    sts macl,r0
    mov.l r0,@r2
    add #4,r2
    mov.l r15,@r2
    add #4,r2
    sts pr,r0
    mov.l r0,@r2
    add #8,r15
    ldc.l @r15+,gbr
    lds.l @r15+,macl
    lds.l @r15+,mach
    lds.l @r15+,pr
    mov.l @r15+,r14
    mov.l @r15+,r13
    mov.l @r15+,r12
    mov.l @r15+,r11
    mov.l @r15+,r10
    mov.l @r15+,r9
    mov.l @r15+,r8
    rts
    mov #0,r0
    .balign 4
L_knock_integration_abi8: .long 0x18283848
L_knock_integration_abi9: .long 0x19293949
L_knock_integration_abi10: .long 0x1a2a3a4a
L_knock_integration_abi11: .long 0x1b2b3b4b
L_knock_integration_abi12: .long 0x1c2c3c4c
L_knock_integration_abi13: .long 0x1d2d3d4d
L_knock_integration_abi14: .long 0x1e2e3e4e
L_knock_integration_abigbr: .long 0x12344321
L_knock_integration_abimach: .long 0x10203040
L_knock_integration_abimacl: .long 0x50607080
L_knock_integration_inner:
    mov r6,r2
    add #88,r2
    mov.l r8,@r2
    add #4,r2
    mov.l r9,@r2
    add #4,r2
    mov.l r10,@r2
    add #4,r2
    mov.l r11,@r2
    add #4,r2
    mov.l r12,@r2
    add #4,r2
    mov.l r13,@r2
    add #4,r2
    mov.l r14,@r2
    add #4,r2
    stc gbr,r0
    mov.l r0,@r2
    add #4,r2
    sts mach,r0
    mov.l r0,@r2
    add #4,r2
    sts macl,r0
    mov.l r0,@r2
    add #4,r2
    mov.l r15,@r2
    add #4,r2
    sts pr,r0
    mov.l r0,@r2
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l mach,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    add #-108,r15
    mov #100,r0
    mov.l r6,@(r0,r15)
    add #4,r0
    mov.l r4,@(r0,r15)
    mov r5,r3
    mov r15,r1
    add #-32,r1
    mov.l L_knock_integration_frame_seed,r0
    mov #8,r2
L_knock_integration_seed_frame:
    mov.l r0,@r1
    add #4,r1
    add #17,r0
    dt r2
    bf L_knock_integration_seed_frame
    mov r15,r1
    mov #5,r2
L_knock_integration_seed_local:
    mov.l r0,@r1
    add #4,r1
    add #17,r0
    dt r2
    bf L_knock_integration_seed_local
    mov.l L_knock_integration_return_pointer,r0
    mov.l r0,@(16,r15)
    mov r6,r2
    add #100,r2
    add #84,r2
    mov r15,r1
    add #-32,r1
    mov #13,r0
L_knock_integration_frame_before:
    mov.l @r1+,r4
    mov.l r4,@r2
    add #4,r2
    dt r0
    bf L_knock_integration_frame_before
    mov.l @(60,r3),r0
    ldc r0,gbr
    mov r3,r2
    add #64,r2
    mov.l @r2+,r0
    lds r0,mach
    mov.l @r2,r0
    lds r0,macl
    mov.l @(16,r3),r4
    mov.l @(20,r3),r5
    mov.l @(24,r3),r6
    mov.l @(28,r3),r7
    mov.l @(32,r3),r8
    mov.l @(36,r3),r9
    mov.l @(40,r3),r10
    mov.l @(44,r3),r11
    mov.l @(48,r3),r12
    mov.l @(52,r3),r13
    mov.l @(56,r3),r14
    mov.l @(0,r3),r0
    mov.l @(4,r3),r1
    mov.l @(8,r3),r2
    mov.l @(12,r3),r3
    mov r15,r7
    add #104,r7
    mov.l @r7,r7
    jsr @r7
    nop
L_knock_integration_stock_return:
    add #100,r15
    mov.l r0,@-r15
    mov.l r1,@-r15
    mov.l r2,@-r15
    mov.l r3,@-r15
    mov.l r4,@-r15
    mov.l r5,@-r15
    mov.l r6,@-r15
    mov.l r7,@-r15
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    stc.l gbr,@-r15
    sts.l mach,@-r15
    sts.l macl,@-r15
    sts.l pr,@-r15
    stc.l sr,@-r15
    mov r15,r1
    mov r15,r0
    add #80,r0
    mov.l @r0,r3
    mov r3,r2
    mov #20,r4
L_knock_integration_copy_exit:
    mov.l @r1+,r5
    mov.l r5,@r2
    add #4,r2
    dt r4
    bf L_knock_integration_copy_exit
    mov r15,r0
    add #-20,r0
    mov.l r0,@r2
    add #4,r2
    mov.l L_knock_integration_return_pointer,r0
    mov.l r0,@r2
    mov r3,r2
    add #118,r2
    add #118,r2
    mov r15,r1
    add #-52,r1
    mov #13,r4
L_knock_integration_frame_after:
    mov.l @r1+,r5
    mov.l r5,@r2
    add #4,r2
    dt r4
    bf L_knock_integration_frame_after
    add #88,r15
    ldc.l @r15+,gbr
    lds.l @r15+,macl
    lds.l @r15+,mach
    lds.l @r15+,pr
    mov.l @r15+,r14
    mov.l @r15+,r13
    mov.l @r15+,r12
    mov.l @r15+,r11
    mov.l @r15+,r10
    mov.l @r15+,r9
    mov.l @r15+,r8
    rts
    nop
    .balign 4
L_knock_integration_frame_seed: .long 0xa3b4c5d6
L_knock_integration_return_pointer: .long L_knock_integration_stock_return

    .size _stock_invoke_knock_integration,.-_stock_invoke_knock_integration

! Simulator helper records the complete stock exit separately from the C caller ABI.
! R7 supplies the driver call target; the tested entries do not read incoming R7.
! The 20-byte local frame precedes the 80-byte exit buffer.
! The stock slice preserves the seeded local frame and every stack neighbor.
! The ordinary RTS/NOP boundary returns through incoming driver PR.
    .section .text
    .balign 4
    .global _stock_invoke_knock_event_retard
    .type _stock_invoke_knock_event_retard,@function
_stock_invoke_knock_event_retard:
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l mach,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    add #-8,r15
    mov.l r6,@r15
    mov.l L_knock_event_retard_abi8,r8
    mov.l L_knock_event_retard_abi9,r9
    mov.l L_knock_event_retard_abi10,r10
    mov.l L_knock_event_retard_abi11,r11
    mov.l L_knock_event_retard_abi12,r12
    mov.l L_knock_event_retard_abi13,r13
    mov.l L_knock_event_retard_abi14,r14
    mov.l L_knock_event_retard_abigbr,r0
    ldc r0,gbr
    mov.l L_knock_event_retard_abimach,r0
    lds r0,mach
    mov.l L_knock_event_retard_abimacl,r0
    lds r0,macl
    bsr L_knock_event_retard_inner
    nop
L_knock_event_retard_outer_return:
    mov.l @r15,r6
    mov r6,r2
    add #100,r2
    add #36,r2
    mov.l r8,@r2
    add #4,r2
    mov.l r9,@r2
    add #4,r2
    mov.l r10,@r2
    add #4,r2
    mov.l r11,@r2
    add #4,r2
    mov.l r12,@r2
    add #4,r2
    mov.l r13,@r2
    add #4,r2
    mov.l r14,@r2
    add #4,r2
    stc gbr,r0
    mov.l r0,@r2
    add #4,r2
    sts mach,r0
    mov.l r0,@r2
    add #4,r2
    sts macl,r0
    mov.l r0,@r2
    add #4,r2
    mov.l r15,@r2
    add #4,r2
    sts pr,r0
    mov.l r0,@r2
    add #8,r15
    ldc.l @r15+,gbr
    lds.l @r15+,macl
    lds.l @r15+,mach
    lds.l @r15+,pr
    mov.l @r15+,r14
    mov.l @r15+,r13
    mov.l @r15+,r12
    mov.l @r15+,r11
    mov.l @r15+,r10
    mov.l @r15+,r9
    mov.l @r15+,r8
    rts
    mov #0,r0
    .balign 4
L_knock_event_retard_abi8: .long 0x18283848
L_knock_event_retard_abi9: .long 0x19293949
L_knock_event_retard_abi10: .long 0x1a2a3a4a
L_knock_event_retard_abi11: .long 0x1b2b3b4b
L_knock_event_retard_abi12: .long 0x1c2c3c4c
L_knock_event_retard_abi13: .long 0x1d2d3d4d
L_knock_event_retard_abi14: .long 0x1e2e3e4e
L_knock_event_retard_abigbr: .long 0x12344321
L_knock_event_retard_abimach: .long 0x10203040
L_knock_event_retard_abimacl: .long 0x50607080
L_knock_event_retard_inner:
    mov r6,r2
    add #88,r2
    mov.l r8,@r2
    add #4,r2
    mov.l r9,@r2
    add #4,r2
    mov.l r10,@r2
    add #4,r2
    mov.l r11,@r2
    add #4,r2
    mov.l r12,@r2
    add #4,r2
    mov.l r13,@r2
    add #4,r2
    mov.l r14,@r2
    add #4,r2
    stc gbr,r0
    mov.l r0,@r2
    add #4,r2
    sts mach,r0
    mov.l r0,@r2
    add #4,r2
    sts macl,r0
    mov.l r0,@r2
    add #4,r2
    mov.l r15,@r2
    add #4,r2
    sts pr,r0
    mov.l r0,@r2
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l mach,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    add #-108,r15
    mov #100,r0
    mov.l r6,@(r0,r15)
    add #4,r0
    mov.l r4,@(r0,r15)
    mov r5,r3
    mov r15,r1
    add #-32,r1
    mov.l L_knock_event_retard_frame_seed,r0
    mov #8,r2
L_knock_event_retard_seed_frame:
    mov.l r0,@r1
    add #4,r1
    add #17,r0
    dt r2
    bf L_knock_event_retard_seed_frame
    mov r15,r1
    mov #5,r2
L_knock_event_retard_seed_local:
    mov.l r0,@r1
    add #4,r1
    add #17,r0
    dt r2
    bf L_knock_event_retard_seed_local
    mov.l L_knock_event_retard_return_pointer,r0
    mov.l r0,@(16,r15)
    mov r6,r2
    add #100,r2
    add #84,r2
    mov r15,r1
    add #-32,r1
    mov #13,r0
L_knock_event_retard_frame_before:
    mov.l @r1+,r4
    mov.l r4,@r2
    add #4,r2
    dt r0
    bf L_knock_event_retard_frame_before
    mov.l @(60,r3),r0
    ldc r0,gbr
    mov r3,r2
    add #64,r2
    mov.l @r2+,r0
    lds r0,mach
    mov.l @r2,r0
    lds r0,macl
    mov.l @(16,r3),r4
    mov.l @(20,r3),r5
    mov.l @(24,r3),r6
    mov.l @(28,r3),r7
    mov.l @(32,r3),r8
    mov.l @(36,r3),r9
    mov.l @(40,r3),r10
    mov.l @(44,r3),r11
    mov.l @(48,r3),r12
    mov.l @(52,r3),r13
    mov.l @(56,r3),r14
    mov.l @(0,r3),r0
    mov.l @(4,r3),r1
    mov.l @(8,r3),r2
    mov.l @(12,r3),r3
    mov r15,r7
    add #104,r7
    mov.l @r7,r7
    jsr @r7
    nop
L_knock_event_retard_stock_return:
    add #100,r15
    mov.l r0,@-r15
    mov.l r1,@-r15
    mov.l r2,@-r15
    mov.l r3,@-r15
    mov.l r4,@-r15
    mov.l r5,@-r15
    mov.l r6,@-r15
    mov.l r7,@-r15
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    stc.l gbr,@-r15
    sts.l mach,@-r15
    sts.l macl,@-r15
    sts.l pr,@-r15
    stc.l sr,@-r15
    mov r15,r1
    mov r15,r0
    add #80,r0
    mov.l @r0,r3
    mov r3,r2
    mov #20,r4
L_knock_event_retard_copy_exit:
    mov.l @r1+,r5
    mov.l r5,@r2
    add #4,r2
    dt r4
    bf L_knock_event_retard_copy_exit
    mov r15,r0
    add #-20,r0
    mov.l r0,@r2
    add #4,r2
    mov.l L_knock_event_retard_return_pointer,r0
    mov.l r0,@r2
    mov r3,r2
    add #118,r2
    add #118,r2
    mov r15,r1
    add #-52,r1
    mov #13,r4
L_knock_event_retard_frame_after:
    mov.l @r1+,r5
    mov.l r5,@r2
    add #4,r2
    dt r4
    bf L_knock_event_retard_frame_after
    add #88,r15
    ldc.l @r15+,gbr
    lds.l @r15+,macl
    lds.l @r15+,mach
    lds.l @r15+,pr
    mov.l @r15+,r14
    mov.l @r15+,r13
    mov.l @r15+,r12
    mov.l @r15+,r11
    mov.l @r15+,r10
    mov.l @r15+,r9
    mov.l @r15+,r8
    rts
    nop
    .balign 4
L_knock_event_retard_frame_seed: .long 0xa3b4c5d6
L_knock_event_retard_return_pointer: .long L_knock_event_retard_stock_return

    .size _stock_invoke_knock_event_retard,.-_stock_invoke_knock_event_retard

! Simulator helper records the complete stock exit separately from the C caller ABI.
! R7 supplies the driver call target; the tested entries do not read incoming R7.
! The 20-byte local frame precedes the 80-byte exit buffer.
! The stock slice preserves the seeded local frame and every stack neighbor.
! The ordinary RTS/NOP boundary returns through incoming driver PR.
    .section .text
    .balign 4
    .global _stock_invoke_knock_event_publication
    .type _stock_invoke_knock_event_publication,@function
_stock_invoke_knock_event_publication:
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l mach,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    add #-8,r15
    mov.l r6,@r15
    mov.l L_knock_event_publication_abi8,r8
    mov.l L_knock_event_publication_abi9,r9
    mov.l L_knock_event_publication_abi10,r10
    mov.l L_knock_event_publication_abi11,r11
    mov.l L_knock_event_publication_abi12,r12
    mov.l L_knock_event_publication_abi13,r13
    mov.l L_knock_event_publication_abi14,r14
    mov.l L_knock_event_publication_abigbr,r0
    ldc r0,gbr
    mov.l L_knock_event_publication_abimach,r0
    lds r0,mach
    mov.l L_knock_event_publication_abimacl,r0
    lds r0,macl
    bsr L_knock_event_publication_inner
    nop
L_knock_event_publication_outer_return:
    mov.l @r15,r6
    mov r6,r2
    add #100,r2
    add #36,r2
    mov.l r8,@r2
    add #4,r2
    mov.l r9,@r2
    add #4,r2
    mov.l r10,@r2
    add #4,r2
    mov.l r11,@r2
    add #4,r2
    mov.l r12,@r2
    add #4,r2
    mov.l r13,@r2
    add #4,r2
    mov.l r14,@r2
    add #4,r2
    stc gbr,r0
    mov.l r0,@r2
    add #4,r2
    sts mach,r0
    mov.l r0,@r2
    add #4,r2
    sts macl,r0
    mov.l r0,@r2
    add #4,r2
    mov.l r15,@r2
    add #4,r2
    sts pr,r0
    mov.l r0,@r2
    add #8,r15
    ldc.l @r15+,gbr
    lds.l @r15+,macl
    lds.l @r15+,mach
    lds.l @r15+,pr
    mov.l @r15+,r14
    mov.l @r15+,r13
    mov.l @r15+,r12
    mov.l @r15+,r11
    mov.l @r15+,r10
    mov.l @r15+,r9
    mov.l @r15+,r8
    rts
    mov #0,r0
    .balign 4
L_knock_event_publication_abi8: .long 0x18283848
L_knock_event_publication_abi9: .long 0x19293949
L_knock_event_publication_abi10: .long 0x1a2a3a4a
L_knock_event_publication_abi11: .long 0x1b2b3b4b
L_knock_event_publication_abi12: .long 0x1c2c3c4c
L_knock_event_publication_abi13: .long 0x1d2d3d4d
L_knock_event_publication_abi14: .long 0x1e2e3e4e
L_knock_event_publication_abigbr: .long 0x12344321
L_knock_event_publication_abimach: .long 0x10203040
L_knock_event_publication_abimacl: .long 0x50607080
L_knock_event_publication_inner:
    mov r6,r2
    add #88,r2
    mov.l r8,@r2
    add #4,r2
    mov.l r9,@r2
    add #4,r2
    mov.l r10,@r2
    add #4,r2
    mov.l r11,@r2
    add #4,r2
    mov.l r12,@r2
    add #4,r2
    mov.l r13,@r2
    add #4,r2
    mov.l r14,@r2
    add #4,r2
    stc gbr,r0
    mov.l r0,@r2
    add #4,r2
    sts mach,r0
    mov.l r0,@r2
    add #4,r2
    sts macl,r0
    mov.l r0,@r2
    add #4,r2
    mov.l r15,@r2
    add #4,r2
    sts pr,r0
    mov.l r0,@r2
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l mach,@-r15
    sts.l macl,@-r15
    stc.l gbr,@-r15
    add #-108,r15
    mov #100,r0
    mov.l r6,@(r0,r15)
    add #4,r0
    mov.l r4,@(r0,r15)
    mov r5,r3
    mov r15,r1
    add #-32,r1
    mov.l L_knock_event_publication_frame_seed,r0
    mov #8,r2
L_knock_event_publication_seed_frame:
    mov.l r0,@r1
    add #4,r1
    add #17,r0
    dt r2
    bf L_knock_event_publication_seed_frame
    mov r15,r1
    mov #5,r2
L_knock_event_publication_seed_local:
    mov.l r0,@r1
    add #4,r1
    add #17,r0
    dt r2
    bf L_knock_event_publication_seed_local
    mov.l L_knock_event_publication_return_pointer,r0
    mov.l r0,@(16,r15)
    mov r6,r2
    add #100,r2
    add #84,r2
    mov r15,r1
    add #-32,r1
    mov #13,r0
L_knock_event_publication_frame_before:
    mov.l @r1+,r4
    mov.l r4,@r2
    add #4,r2
    dt r0
    bf L_knock_event_publication_frame_before
    mov.l @(60,r3),r0
    ldc r0,gbr
    mov r3,r2
    add #64,r2
    mov.l @r2+,r0
    lds r0,mach
    mov.l @r2,r0
    lds r0,macl
    mov.l @(16,r3),r4
    mov.l @(20,r3),r5
    mov.l @(24,r3),r6
    mov.l @(28,r3),r7
    mov.l @(32,r3),r8
    mov.l @(36,r3),r9
    mov.l @(40,r3),r10
    mov.l @(44,r3),r11
    mov.l @(48,r3),r12
    mov.l @(52,r3),r13
    mov.l @(56,r3),r14
    mov.l @(0,r3),r0
    mov.l @(4,r3),r1
    mov.l @(8,r3),r2
    mov.l @(12,r3),r3
    mov r15,r7
    add #104,r7
    mov.l @r7,r7
    jsr @r7
    nop
L_knock_event_publication_stock_return:
    add #100,r15
    mov.l r0,@-r15
    mov.l r1,@-r15
    mov.l r2,@-r15
    mov.l r3,@-r15
    mov.l r4,@-r15
    mov.l r5,@-r15
    mov.l r6,@-r15
    mov.l r7,@-r15
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    stc.l gbr,@-r15
    sts.l mach,@-r15
    sts.l macl,@-r15
    sts.l pr,@-r15
    stc.l sr,@-r15
    mov r15,r1
    mov r15,r0
    add #80,r0
    mov.l @r0,r3
    mov r3,r2
    mov #20,r4
L_knock_event_publication_copy_exit:
    mov.l @r1+,r5
    mov.l r5,@r2
    add #4,r2
    dt r4
    bf L_knock_event_publication_copy_exit
    mov r15,r0
    add #-20,r0
    mov.l r0,@r2
    add #4,r2
    mov.l L_knock_event_publication_return_pointer,r0
    mov.l r0,@r2
    mov r3,r2
    add #118,r2
    add #118,r2
    mov r15,r1
    add #-52,r1
    mov #13,r4
L_knock_event_publication_frame_after:
    mov.l @r1+,r5
    mov.l r5,@r2
    add #4,r2
    dt r4
    bf L_knock_event_publication_frame_after
    add #88,r15
    ldc.l @r15+,gbr
    lds.l @r15+,macl
    lds.l @r15+,mach
    lds.l @r15+,pr
    mov.l @r15+,r14
    mov.l @r15+,r13
    mov.l @r15+,r12
    mov.l @r15+,r11
    mov.l @r15+,r10
    mov.l @r15+,r9
    mov.l @r15+,r8
    rts
    nop
    .balign 4
L_knock_event_publication_frame_seed: .long 0xa3b4c5d6
L_knock_event_publication_return_pointer: .long L_knock_event_publication_stock_return

    .size _stock_invoke_knock_event_publication,.-_stock_invoke_knock_event_publication
