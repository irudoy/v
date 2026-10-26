! Independent reconstruction of the redirected fuel-cut literal consumer.
! Instructions, branches and pools retain their original ROM addresses.
    .text
    .balign 4
    .set ORIGIN,0x0004f280
    .org 0x0004f282-ORIGIN
    stc.l gbr,@-r15
    mov.l .Lstate_base,r0
    ldc r0,gbr
    mov.b @(0x4b,gbr),r0
    mov.l .Lconfiguration,r6
    mov r0,r1
    mov.b @r6,r0
    tst #0x80,r0
    bf .Loverride
    mov.b @(0x1c,gbr),r0
    tst #0x10,r0
    bf .Lsecond_pair
    bra .Lfirst_pair
    nop
.Loverride:
    mov.b @(0x4d,gbr),r0
    tst #0x2,r0
    bt .Lfallback
    mov.b @(0x48,gbr),r0
    tst #0x20,r0
    bt .Lfallback
    mov.b @(0x3,gbr),r0
    tst #0x4,r0
    bt .Lfallback
    mov.l .Lthresholds,r4
    mov.w @(0x8,r4),r0
    extu.w r0,r5
    bra .Lcompare
    mov.w @(0xa,r4),r0
.Lfallback:
    mov.b @(0x1c,gbr),r0
    tst #0x10,r0
    bt .Lfirst_pair
.Lsecond_pair:
    mov.l .Lthresholds,r4
    mov.w @(0x2,r4),r0
    extu.w r0,r5
    bra .Lcompare
    mov.w @(0x6,r4),r0
.Lfirst_pair:
    mov.l .Lthresholds,r4
    mov.w @r4,r2
    mov.w @(0x4,r4),r0
    extu.w r2,r5
.Lcompare:
    mov.l .Lrpm_base,r4
    extu.w r0,r6
    mov r1,r0
    tst #0x4,r0
    mov #0x20,r0
    bt/s .Linactive
    mov.w @(r0,r4),r2
    extu.w r2,r2
    cmp/ge r6,r2
    bt .Lresult
    mov r1,r0
    bra .Lstore
    and #0xf9,r0
.Linactive:
    extu.w r2,r6
    cmp/ge r5,r6
    bf .Lbelow
    mov r1,r0
    tst #0x2,r0
    bf .Ltimer
    mov.l .Ldelay,r6
    mov.b @r6,r0
    mov.b r0,@(0xa5,gbr)
    mov r1,r0
    or #0x2,r0
    mov.b r0,@(0x4b,gbr)
.Ltimer:
    mov.b @(0xa5,gbr),r0
    tst r0,r0
    bf .Lresult
    mov #0x4b,r0
    bra .Lresult
    or.b #0x4,@(r0,gbr)
.Lbelow:
    mov r1,r0
    and #0xfd,r0
.Lstore:
    mov.b r0,@(0x4b,gbr)
.Lresult:
    mov.b @(0x4b,gbr),r0
    tst #0x4,r0
    movt r0
    xor #0x1,r0
    extu.b r0,r0
    rts
    ldc.l @r15+,gbr
    .org 0x0004f460-ORIGIN
.Lstate_base:    .long 0xffff244c
.Lconfiguration: .long 0x00008b38
.Lthresholds:    .long 0x0000934e
.Lrpm_base:      .long 0xffff119c
.Ldelay:         .long 0x00008c69
