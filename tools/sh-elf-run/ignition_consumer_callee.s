! Simulator-only stand-in for the unchanged stock lookup callee.
! The call windows and real injected adapters retain their exact bytes.
! Record complete entry state before using scratch registers, preserve the
! original call frame, and return one declared sentinel result.
    .text
    .balign 4
    .global ignition_consumer_callee
ignition_consumer_callee:
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
    mov.l .Lobservation,r2
    mov #20,r0
.Lcopy:
    mov.l @r1+,r3
    mov.l r3,@r2
    add #4,r2
    dt r0
    bf .Lcopy
    mov r15,r0
    add #80,r0
    mov.l r0,@r2
    add #4,r2
    mov.l @r0,r0
    mov.l r0,@r2
    add #4,r2
    mov.l @r2,r0
    add #1,r0
    mov.l r0,@r2
    add #4,r2
    mov.l .Lstock_entry,r0
    mov.l r0,@r2
    ldc.l @r15+,sr
    lds.l @r15+,pr
    lds.l @r15+,macl
    lds.l @r15+,mach
    ldc.l @r15+,gbr
    mov.l @r15+,r14
    mov.l @r15+,r13
    mov.l @r15+,r12
    mov.l @r15+,r11
    mov.l @r15+,r10
    mov.l @r15+,r9
    mov.l @r15+,r8
    mov.l @r15+,r7
    mov.l @r15+,r6
    mov.l @r15+,r5
    mov.l @r15+,r4
    mov.l @r15+,r3
    mov.l @r15+,r2
    mov.l @r15+,r1
    mov.l @r15+,r0
    mov.l .Lresult,r0
    rts
    nop
    .balign 4
.Lobservation:
    .long 0x01010000
.Lstock_entry:
    .long STOCK_LOOKUP_ENTRY
.Lresult:
    .long 0xa1b2c3d4
