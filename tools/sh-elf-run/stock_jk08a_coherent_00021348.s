! Bounded coherent snapshot caller and natural helper path.
! Separate ELF per caller keeps every observation boundary outside tested bytes.
    .text
    .balign 4
    .org 0x21338 - 0x21338
L_00021338:
    mov.l L_000213c4,r6
    .org 0x2133a - 0x21338
L_0002133a:
    mov.l L_000213c8,r1
    .org 0x2133c - 0x21338
L_0002133c:
    mov.b @r6,r2
    .org 0x2133e - 0x21338
L_0002133e:
    mov.l L_000213cc,r6
    .org 0x21340 - 0x21338
L_00021340:
    mov.b r2,@r6
    .org 0x21342 - 0x21338
L_00021342:
    mov.l L_000213d0,r6
    .org 0x21344 - 0x21338
L_00021344:
    mov.b r2,@r6
    .org 0x21346 - 0x21338
L_00021346:
    mov.l L_000213d4,r2
    .org 0x21348 - 0x21338
L_00021348:
    jsr @r11
    .org 0x2134a - 0x21338
L_0002134a:
    mov #0x6,r0
    .org 0x213c4 - 0x21338
L_000213c4:
    .long 0xffff24c6
    .org 0x213c8 - 0x21338
L_000213c8:
    .long 0xffff24c8
    .org 0x213cc - 0x21338
L_000213cc:
    .long 0xffff24c5
    .org 0x213d0 - 0x21338
L_000213d0:
    .long 0xffff24c7
    .org 0x213d4 - 0x21338
L_000213d4:
    .long 0xffff24ce
    .org 0x22558 - 0x21338
L_00022558:
    mov.l r2,@-r15
    .org 0x2255a - 0x21338
L_0002255a:
    mov.l r3,@-r15
    .org 0x2255c - 0x21338
L_0002255c:
    mov.l r4,@-r15
    .org 0x2255e - 0x21338
L_0002255e:
    cmp/eq #0,r0
    .org 0x22560 - 0x21338
L_00022560:
    bt L_00022588
    .org 0x22562 - 0x21338
L_00022562:
    mov r2,r4
    .org 0x22564 - 0x21338
L_00022564:
    add r0,r4
    .org 0x22566 - 0x21338
L_00022566:
    mov.b @r2+,r0
    .org 0x22568 - 0x21338
L_00022568:
    mov.b r0,@r1
    .org 0x2256a - 0x21338
L_0002256a:
    cmp/hi r2,r4
    .org 0x2256c - 0x21338
L_0002256c:
    bf L_00022588
    .org 0x2256e - 0x21338
L_0002256e:
    mov.b @r2+,r0
    .org 0x22570 - 0x21338
L_00022570:
    mov.b r0,@(1,r1)
    .org 0x22572 - 0x21338
L_00022572:
    cmp/hi r2,r4
    .org 0x22574 - 0x21338
L_00022574:
    bf L_00022588
    .org 0x22576 - 0x21338
L_00022576:
    mov.b @r2+,r0
    .org 0x22578 - 0x21338
L_00022578:
    mov.b r0,@(2,r1)
    .org 0x2257a - 0x21338
L_0002257a:
    cmp/hi r2,r4
    .org 0x2257c - 0x21338
L_0002257c:
    bf L_00022588
    .org 0x2257e - 0x21338
L_0002257e:
    mov.b @r2+,r0
    .org 0x22580 - 0x21338
L_00022580:
    mov.b r0,@(3,r1)
    .org 0x22582 - 0x21338
L_00022582:
    cmp/hi r2,r4
    .org 0x22584 - 0x21338
L_00022584:
    add #4,r1
    .org 0x22586 - 0x21338
L_00022586:
    bt L_00022566
    .org 0x22588 - 0x21338
L_00022588:
    mov.l @r15+,r4
    .org 0x2258a - 0x21338
L_0002258a:
    mov.l @r15+,r3
    .org 0x2258c - 0x21338
L_0002258c:
    rts
    .org 0x2258e - 0x21338
L_0002258e:
    mov.l @r15+,r2
