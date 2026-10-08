! Independent reconstruction of the natural full-width base accumulator.
    .text
    .balign 4
    .org 0x554ae-0x554ac
.global stock_base_accumulator
stock_base_accumulator:
    stc.l gbr,@-r15
    mov.l .Lram22f8,r0
    ldc r0,gbr
    mov.l .Lram128c,r1
    mov #0x40,r6
    mov.w .Lterm_offset,r0
    shll8 r6
    mov.l @(r0,r1),r2
    mov.w @(0x14,gbr),r0
    add r6,r2
    extu.w r0,r4
    mov.w .Lcoolant_offset,r0
    mov r2,r5
    add r4,r2
    mov.w @(r0,r1),r7
    mov #-1,r6
    extu.w r6,r6
    extu.w r7,r7
    add r7,r2
    cmp/gt r6,r2
    bf .Lwithin_upper
    bra .Llower_test
    mov r6,r2
.Lwithin_upper:
    add r4,r5
    add r7,r5
    mov r5,r2
.Llower_test:
    cmp/pz r2
    bt .Lpublish
    mov #0,r2
.Lpublish:
    mov r2,r0
    mov.w r0,@(0x22,gbr)
    rts
    ldc.l @r15+,gbr
    .org 0x554f4-0x554ac
.Lcoolant_offset:
    .word 0x034e
.Lterm_offset:
    .word 0x036c
    .org 0x555c8-0x554ac
.Lram128c:
    .long 0xffff128c
    .org 0x555ec-0x554ac
.Lram22f8:
    .long 0xffff22f8
