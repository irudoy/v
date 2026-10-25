! Exact runtime-record byte1 predicate and bounded MAF summary-bit call.
    .text
    .balign 4
    .org 0x25e20 - 0x25e20
L_25e20:
    mov.l P_25f10,r1
    .org 0x25e22 - 0x25e20
L_25e22:
    exts.w r4,r0
    .org 0x25e24 - 0x25e20
L_25e24:
    cmp/eq #-0x1,r0
    .org 0x25e26 - 0x25e20
L_25e26:
    bt L_25e3e
    .org 0x25e28 - 0x25e20
L_25e28:
    mov r1,r6
    .org 0x25e2a - 0x25e20
L_25e2a:
    mov r0,r2
    .org 0x25e2c - 0x25e20
L_25e2c:
    shll r2
    .org 0x25e2e - 0x25e20
L_25e2e:
    add r0,r2
    .org 0x25e30 - 0x25e20
L_25e30:
    add r2,r6
    .org 0x25e32 - 0x25e20
L_25e32:
    mov.b @(0x1,r6),r0
    .org 0x25e34 - 0x25e20
L_25e34:
    tst #0x80,r0
    .org 0x25e36 - 0x25e20
L_25e36:
    movt r0
    .org 0x25e38 - 0x25e20
L_25e38:
    xor #0x1,r0
    .org 0x25e3a - 0x25e20
L_25e3a:
    bra L_25e40
    .org 0x25e3c - 0x25e20
L_25e3c:
    extu.b r0,r2
    .org 0x25e3e - 0x25e20
L_25e3e:
    mov #0x0,r2
    .org 0x25e40 - 0x25e20
L_25e40:
    rts
    .org 0x25e42 - 0x25e20
L_25e42:
    mov r2,r0
    .org 0x25f10 - 0x25e20
P_25f10: .long 0xffff5718
    .org 0x3c3c6 - 0x25e20
summary_record_caller:
    mov.l summary_predicate,r2
    mov.w summary_index,r4
    jsr @r2
    nop
    tst r0,r0
    bt/s summary_clear
    mov #0,r0
    bra summary_end
    or.b #0x80,@(r0,gbr)
summary_clear:
    and.b #0x7f,@(r0,gbr)
summary_end:
    .org 0x3c470 - 0x25e20
summary_index: .word 0x0129
    .org 0x3c47c - 0x25e20
summary_predicate: .long L_25e20
