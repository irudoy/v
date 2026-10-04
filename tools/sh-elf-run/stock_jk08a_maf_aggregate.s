! JK08A combined MAF sum, signed word correction, and unsigned word addition.
! Origin 0x3b250 preserves the stock entry, pools, and natural return.
    .text
    .balign 4
    .org 2
combined_maf:
    stc.l gbr,@-r15
    mov.l maf_window,r0
    ldc r0,gbr
    mov.w @(0x3e,gbr),r0
    mov.l auxiliary_window,r6
    mov r0,r1
    mov.l @(0xc,gbr),r0
    mov r0,r4
    mov.l @(0x10,gbr),r0
    add r0,r4
    mov #0x38,r0
    mov.w @(r0,r6),r2
    add r1,r4
    extu.w r2,r6
    add r6,r4
    cmp/pz r4
    bt publish
    mov #0,r4
publish:
    mov r4,r0
    mov.l r0,@(0x4c,gbr)
    rts
    ldc.l @r15+,gbr
    .org 0x3b390 - 0x3b250
maf_window:
    .long 0xffff1dec
auxiliary_window:
    .long 0xffff2330
