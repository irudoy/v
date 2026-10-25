! Bounded scheduler copy call with explicit entry registers.
! The GNU gate binds all caller, helper and dispatch bytes to the owned stock image.
    .text
    .balign 4
    .org 0x20ce0 - 0x20ce0
L_00020ce0:
    mov.l L_00020e90,r1
    .org 0x20ce2 - 0x20ce0
L_00020ce2:
    mov.l L_00020e94,r2
    .org 0x20ce4 - 0x20ce0
L_00020ce4:
    mov.l L_00020e70,r5
    .org 0x20ce6 - 0x20ce0
L_00020ce6:
    jsr @r5
    .org 0x20ce8 - 0x20ce0
L_00020ce8:
    mov #0x10,r0
    .org 0x20e70 - 0x20ce0
L_00020e70:
    .long 0x00022558
    .org 0x20e90 - 0x20ce0
L_00020e90:
    .long 0xffff39b4
    .org 0x20e94 - 0x20ce0
L_00020e94:
    .long 0xffff39a4
    .org 0x22558 - 0x20ce0
L_00022558:
    mov.l r2,@-r15
    .org 0x2255a - 0x20ce0
L_0002255a:
    mov.l r3,@-r15
    .org 0x2255c - 0x20ce0
L_0002255c:
    mov.l r4,@-r15
    .org 0x2255e - 0x20ce0
L_0002255e:
    cmp/eq #0,r0
    .org 0x22560 - 0x20ce0
L_00022560:
    bt L_00022588
    .org 0x22562 - 0x20ce0
L_00022562:
    mov r2,r4
    .org 0x22564 - 0x20ce0
L_00022564:
    add r0,r4
    .org 0x22566 - 0x20ce0
L_00022566:
    mov.b @r2+,r0
    .org 0x22568 - 0x20ce0
L_00022568:
    mov.b r0,@r1
    .org 0x2256a - 0x20ce0
L_0002256a:
    cmp/hi r2,r4
    .org 0x2256c - 0x20ce0
L_0002256c:
    bf L_00022588
    .org 0x2256e - 0x20ce0
L_0002256e:
    mov.b @r2+,r0
    .org 0x22570 - 0x20ce0
L_00022570:
    mov.b r0,@(1,r1)
    .org 0x22572 - 0x20ce0
L_00022572:
    cmp/hi r2,r4
    .org 0x22574 - 0x20ce0
L_00022574:
    bf L_00022588
    .org 0x22576 - 0x20ce0
L_00022576:
    mov.b @r2+,r0
    .org 0x22578 - 0x20ce0
L_00022578:
    mov.b r0,@(2,r1)
    .org 0x2257a - 0x20ce0
L_0002257a:
    cmp/hi r2,r4
    .org 0x2257c - 0x20ce0
L_0002257c:
    bf L_00022588
    .org 0x2257e - 0x20ce0
L_0002257e:
    mov.b @r2+,r0
    .org 0x22580 - 0x20ce0
L_00022580:
    mov.b r0,@(3,r1)
    .org 0x22582 - 0x20ce0
L_00022582:
    cmp/hi r2,r4
    .org 0x22584 - 0x20ce0
L_00022584:
    add #4,r1
    .org 0x22586 - 0x20ce0
L_00022586:
    bt L_00022566
    .org 0x22588 - 0x20ce0
L_00022588:
    mov.l @r15+,r4
    .org 0x2258a - 0x20ce0
L_0002258a:
    mov.l @r15+,r3
    .org 0x2258c - 0x20ce0
L_0002258c:
    rts
    .org 0x2258e - 0x20ce0
L_0002258e:
    mov.l @r15+,r2
