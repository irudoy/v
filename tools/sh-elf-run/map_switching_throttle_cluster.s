! Independent reconstruction of the redirected throttle-cluster prefix.
! The enabled-body boundary is simulator-only; it preserves R0 and the frame.
    .text
    .balign 4
    .set ORIGIN,0x0007584c
    .org 0x0007584e-ORIGIN
    mov.l r8,@-r15
    mov.l r9,@-r15
    mov.l r10,@-r15
    mov.l r11,@-r15
    mov.l r12,@-r15
    mov.l r13,@-r15
    mov.l r14,@-r15
    sts.l pr,@-r15
    sts.l macl,@-r15
    add #-0xc,r15
    mov.l .Lcluster,r9
    mov #-1,r6
    extu.w r6,r6
    mov.w @(8,r9),r0
    extu.w r0,r7
    cmp/eq r6,r7
    bf .Lboundary
    mov.w .Ldisabled,r2
    mov.l .Lrequest_base,r10
    mov.w .Lrequest_offset,r0
    bra .Lepilogue
    mov.w r2,@(r0,r10)
.Lboundary:
    bra .Lepilogue
    nop
    .org 0x00075938-ORIGIN
.Ldisabled: .word 0x7fff
.Lrequest_offset: .word 0x074c
    .org 0x00075958-ORIGIN
.Lrequest_base: .long 0xffff128c
    .org 0x00075964-ORIGIN
.Lcluster: .long 0x00009424
    .org 0x00075c32-ORIGIN
.Lepilogue:
    add #0xc,r15
    lds.l @r15+,macl
    lds.l @r15+,pr
    mov.l @r15+,r14
    mov.l @r15+,r13
    mov.l @r15+,r12
    mov.l @r15+,r11
    mov.l @r15+,r10
    mov.l @r15+,r9
    rts
    mov.l @r15+,r8
