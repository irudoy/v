! Independent reconstruction of the redirected throttle-scalar clamp.
! Only [0x77ac0,0x77ace) executes as the consumer under test.
! The following two original instructions bind the observation boundary;
! a simulator-only RTS/NOP replaces them outside the tested window.
    .text
    .balign 4
    .set ORIGIN,0x00077ac0
    mov.l .Lthreshold,r2
    mov.w @r2,r6
    extu.w r6,r6
    cmp/hi r6,r0
    bf/s .Lcontinuation
    mov r0,r4
    mov r6,r4
.Lcontinuation:
    mov.l .Llower_bound,r7
    extu.w r4,r4
    .org 0x00077bac-ORIGIN
.Lthreshold:
    .long 0x0000942c
.Llower_bound:
