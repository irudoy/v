! JK08A median producer and its signed divider, independently reconstructed
! at their stock addresses. Only declared RAM pools are simulator aliases.
    .text
    .balign 4
signed_divide:
    mov.l r2,@-r15
    tst r0,r0
    bt divide_by_zero
    mov.l r3,@-r15
    div0s r0,r1
    movt r3
    cmp/pl r0
    bt positive_divisor
    add #-1,r0
    not r0,r0
positive_divisor:
    cmp/pl r1
    bt positive_dividend
    add #-1,r1
    not r1,r1
positive_dividend:
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
    extu.b r1,r0
    rotcr r3
    bf short_positive
    not r0,r0
    add #1,r0
short_positive:
    mov.l @r15+,r3
    rts
    mov.l @r15+,r2
large_quotient:
    mov.l r4,@-r15
    extu.w r1,r4
    shll8 r0
    shlr16 r1
    .rept 16
    div1 r0,r1
    .endr
    extu.w r1,r2
    xor r2,r1
    addc r2,r2
    shll16 r2
    add r4,r1
    .rept 16
    div1 r0,r1
    .endr
    rotcl r1
    extu.w r1,r0
    add r2,r0
    rotcr r3
    bf large_positive
    not r0,r0
    add #1,r0
large_positive:
    mov.l @r15+,r4
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
    .rept 16
    rotcl r2
    div1 r0,r1
    .endr
    rotcl r2
    mov r2,r0
    rotcr r3
    bf long_positive
    not r0,r0
    add #1,r0
long_positive:
    mov.l @r15+,r3
    rts
    mov.l @r15+,r2
signed_divide_end:

    .org 0x11c
fault_pointer:
    .long 0xffff9818
fault_value:
    .long 0x0000044e

    .org 0x1c370
median_producer:
    mov.l r14,@-r15
    sts.l pr,@-r15
    mov.l mode_base,r6
    mov.b @(1,r6),r0
    tst #0x20,r0
    bt update_history
    mov.l live_base,r6
    mov #0x16,r0
    mov.b @(r0,r6),r2
    mov #-0x7a,r0
    mov.l output_base,r6
    extu.b r0,r0
    bra producer_return
    mov.b r2,@(r0,r6)
update_history:
    mov.l history_base,r14
    mov.w previous_offset,r0
    mov.l period_base,r6
    mov.b @(r0,r14),r4
    mov.w older_offset,r0
    mov.l dividend,r1
    mov.b r4,@(r0,r14)
    mov.w newest_offset,r0
    mov.b @(r0,r14),r2
    mov.w previous_offset,r0
    mov.b r2,@(r0,r14)
    mov.w period_offset,r0
    mov.w @(r0,r6),r2
    mov.l divider,r6
    jsr @r6
    extu.w r2,r0
    mov #-1,r5
    extu.w r0,r6
    extu.b r5,r2
    cmp/gt r2,r6
    bt store_sample
    mov r6,r2
store_sample:
    mov.w newest_offset,r0
    extu.b r2,r5
    extu.b r2,r6
    mov.b r5,@(r0,r14)
    mov.w previous_offset,r0
    mov.b @(r0,r14),r4
    extu.b r4,r4
    cmp/eq r4,r6
    bt store_newest
    mov.w older_offset,r0
    cmp/ge r4,r5
    mov.b @(r0,r14),r7
    bt/s newer_is_larger
    extu.b r7,r7
    cmp/gt r7,r4
    bf store_previous
    cmp/ge r7,r5
    bt store_newest
    bra store_older
    nop
newer_is_larger:
    cmp/gt r7,r5
    bf store_newest
    cmp/ge r7,r4
    bf store_older
store_previous:
    mov.l output_base,r6
    mov #-0x7a,r0
    extu.b r0,r0
    bra producer_return
    mov.b r4,@(r0,r6)
store_older:
    mov.l output_base,r6
    mov #-0x7a,r0
    extu.b r0,r0
    bra producer_return
    mov.b r7,@(r0,r6)
store_newest:
    mov.l output_base,r6
    mov #-0x7a,r0
    extu.b r0,r0
    mov.b r5,@(r0,r6)
producer_return:
    lds.l @r15+,pr
    rts
    mov.l @r15+,r14
median_producer_end:

    .org 0x1c45c
period_offset:
    .word 0x02c8
previous_offset:
    .word 0x0471
older_offset:
    .word 0x0472
newest_offset:
    .word 0x0470

    .org 0x1c58c
mode_base:
    .long 0xffff24c8
period_base:
    .long 0xffff1ff4
dividend:
    .long 0x0000a2c2
divider:
    .long 0x00021bbc
live_base:
    .long 0xffff11d4
output_base:
    .long 0xffff277e
history_base:
    .long 0xffff39c4
