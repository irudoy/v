! JK08A 0x0003e1fe..0x0003e26b: the enabled non-fault RPM-drop arithmetic.
! The verifier links at 0x0003e1fc; the first two bytes are outside the region.
! GBR is the aliased 0xffff1e50 supplied by the invocation wrapper. The two
! pool words remain at their stock addresses. No instruction is relocated.
! The fixture returns at 0x0003e26c before history shifting and publication.
    .text
    .balign 4
    .org 2
arithmetic:
    mov.w   @(0x126,gbr),r0
    mov.l   speed_base,r2
    extu.w  r0,r6
    mov     #0x36,r0
    mov.w   @(r0,r2),r5
    extu.w  r5,r5
    cmp/ge  r5,r6
    bf      rising
    mov.w   @(0x126,gbr),r0
    mov     #1,r7
    mov.l   coefficient_base,r1
    shll8   r7
    extu.w  r0,r6
    mov     r7,r4
    mov.b   @(1,r1),r0
    sub     r5,r6
    extu.b  r0,r2
    mov     r0,r1
    sub     r2,r4
    extu.b  r0,r2
    mov.w   @(8,gbr),r0
    mul.l   r6,r2
    extu.w  r0,r2
    sts     macl,r6
    mul.l   r2,r4
    shll8   r6
    sts     macl,r2
    add     r2,r6
    mov     #-1,r2
    shlr8   r6
    extu.w  r2,r2
    cmp/hi  r2,r6
    bt      saturated
    mov.w   @(0x126,gbr),r0
    mov.l   coefficient_base,r1
    extu.w  r0,r6
    mov.b   @(1,r1),r0
    sub     r5,r6
    extu.b  r0,r2
    mul.l   r6,r2
    extu.b  r0,r4
    mov.w   @(8,gbr),r0
    sub     r4,r7
    extu.w  r0,r6
    mov     r0,r1
    sts     macl,r2
    mul.l   r6,r7
    shll8   r2
    sts     macl,r6
    add     r6,r2
    shlr8   r2
saturated:
    bra     store
    mov     r2,r0
rising:
    mov     #0,r0
store:
    mov.w   r0,@(0,gbr)
arithmetic_end:

    .org 0x1d0
speed_base:
    .long 0xffff1114
    .org 0x1e0
coefficient_base:
    .long 0x000084a3
