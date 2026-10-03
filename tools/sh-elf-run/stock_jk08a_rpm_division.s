! JK08A primary RPM producer and its unsigned divider, reconstructed at their
! stock addresses. The verifier links at 0x00021ce0 and checks both code spans
! and their pool words. The intervening assembly padding is not a fixture.
! The simulator uses the stock image and aliases only the declared RAM pools.
    .text
    .balign 4
unsigned_divide:
    mov.l r2,@-r15
    tst r0,r0
    bt divide_by_zero
    extu.w r0,r2
    cmp/eq r2,r0
    bf long_divisor
    div0u
    shll8 r0
    cmp/hi r1,r0
    bf large_quotient
    .rept 8
    div1 r0,r1
    .endr
    rotcl r1
    mov.l @r15+,r2
    rts
    extu.b r1,r0
large_quotient:
    mov.l r3,@-r15
    extu.w r1,r3
    shll8 r0
    shlr16 r1
    .rept 16
    div1 r0,r1
    .endr
    extu.w r1,r2
    xor r2,r1
    addc r2,r2
    shll16 r2
    add r3,r1
    .rept 16
    div1 r0,r1
    .endr
    rotcl r1
    extu.w r1,r0
    add r2,r0
    mov.l @r15+,r3
    rts
    mov.l @r15+,r2
divide_by_zero:
    mov.l fault_pointer,r1
    mov.l fault_value,r2
    mov.l r2,@r1
    mov #0,r0
    rts
    mov.l @r15+,r2
long_divisor:
    div0u
    extu.w r1,r2
    shll16 r2
    shlr16 r1
    rotcl r2
    .rept 16
    div1 r0,r1
    rotcl r2
    .endr
    mov r2,r0
    rts
    mov.l @r15+,r2
unsigned_divide_end:

    .org 0xe8
fault_pointer:
    .long 0xffff9818
fault_value:
    .long 0x0000044e

    .org 0x16592
rpm_producer:
    sts.l pr,@-r15
    mov.l mode_flags,r6
    mov.b @r6,r0
    tst #0x20,r0
    bf inhibited
    mov.l interval_base,r6
    mov.l divider,r2
    mov.l dividend,r1
    jsr @r2
    mov.l @(0x28,r6),r0
    mov #-1,r6
    extu.w r6,r6
    cmp/hi r6,r0
    bf/s store
    mov r0,r2
    bra store
    mov r6,r2
inhibited:
    mov #0,r2
store:
    mov.l speed_word,r5
    lds.l @r15+,pr
    rts
    mov.w r2,@r5
rpm_producer_end:

    .org 0x16690
mode_flags:
    .long 0xffff417f
interval_base:
    .long 0xffff11d4
divider:
    .long 0x00021ce0
dividend:
    .long 32000000
speed_word:
    .long 0xffff1196
