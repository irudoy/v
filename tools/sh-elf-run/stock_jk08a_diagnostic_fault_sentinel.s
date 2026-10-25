! Exact stock instructions and pools at their natural addresses.
    .text
    .balign 4
    .org 0x259e4 - 0x259e4
L_000259e4:
    mov.l L_00025b98,r1
    .org 0x259e6 - 0x259e4
L_000259e6:
    exts.w r4,r0
    .org 0x259e8 - 0x259e4
L_000259e8:
    cmp/eq -0x1,r0
    .org 0x259ea - 0x259e4
L_000259ea:
    bt L_00025a0c
    .org 0x259ec - 0x259e4
L_000259ec:
    mov r0,r7
    .org 0x259ee - 0x259e4
L_000259ee:
    shll r7
    .org 0x259f0 - 0x259e4
L_000259f0:
    mov r1,r2
    .org 0x259f2 - 0x259e4
L_000259f2:
    add r0,r7
    .org 0x259f4 - 0x259e4
L_000259f4:
    add r7,r2
    .org 0x259f6 - 0x259e4
L_000259f6:
    mov.b @(0x2,r2),r0
    .org 0x259f8 - 0x259e4
L_000259f8:
    tst #0x40,r0
    .org 0x259fa - 0x259e4
L_000259fa:
    bf/s L_00025a0e
    .org 0x259fc - 0x259e4
L_000259fc:
    mov #0x1,r5
    .org 0x259fe - 0x259e4
L_000259fe:
    mov r1,r2
    .org 0x25a00 - 0x259e4
L_00025a00:
    add r7,r2
    .org 0x25a02 - 0x259e4
L_00025a02:
    mov.b @(0x2,r2),r0
    .org 0x25a04 - 0x259e4
L_00025a04:
    tst #0x20,r0
    .org 0x25a06 - 0x259e4
L_00025a06:
    bf L_00025a0e
    .org 0x25a08 - 0x259e4
L_00025a08:
    bra L_00025a0e
    .org 0x25a0a - 0x259e4
L_00025a0a:
    mov #0x0,r5
    .org 0x25a0c - 0x259e4
L_00025a0c:
    mov #0x0,r5
    .org 0x25a0e - 0x259e4
L_00025a0e:
    rts
    .org 0x25a10 - 0x259e4
L_00025a10:
    mov r5,r0
    .org 0x25b98 - 0x259e4
L_00025b98:
    .long 0xffff5718
