! Complete natural register arithmetic helpers with their original returns.
    .text
    .balign 4
    .set ORIGIN,0x224f8
    .org 0x224f8-ORIGIN
L_000224f8:
    shar r0
    .org 0x224fa-ORIGIN
L_000224fa:
    shar r0
    .org 0x224fc-ORIGIN
L_000224fc:
    shar r0
    .org 0x224fe-ORIGIN
L_000224fe:
    shar r0
    .org 0x22500-ORIGIN
L_00022500:
    shar r0
    .org 0x22502-ORIGIN
L_00022502:
    shar r0
    .org 0x22504-ORIGIN
L_00022504:
    rts
    .org 0x22506-ORIGIN
L_00022506:
    shar r0
    .org 0x2251c-ORIGIN
L_0002251c:
    mov.l r1,@-r15
    .org 0x2251e-ORIGIN
L_0002251e:
    shlr8 r0
    .org 0x22520-ORIGIN
L_00022520:
    swap.w r0,r0
    .org 0x22522-ORIGIN
L_00022522:
    exts.b r0,r1
    .org 0x22524-ORIGIN
L_00022524:
    xtrct r1,r0
    .org 0x22526-ORIGIN
L_00022526:
    shar r0
    .org 0x22528-ORIGIN
L_00022528:
    shar r0
    .org 0x2252a-ORIGIN
L_0002252a:
    shar r0
    .org 0x2252c-ORIGIN
L_0002252c:
    rts
    .org 0x2252e-ORIGIN
L_0002252e:
    mov.l @r15+,r1
    .org 0x259d0-ORIGIN
L_000259d0:
    extu.b r7,r7
    .org 0x259d2-ORIGIN
L_000259d2:
    tst r7,r7
    .org 0x259d4-ORIGIN
L_000259d4:
    bt/s L_000259da
    .org 0x259d6-ORIGIN
L_000259d6:
    mov r4,r2
    .org 0x259d8-ORIGIN
L_000259d8:
    sub r6,r2
    .org 0x259da-ORIGIN
L_000259da:
    cmp/gt r5,r2
    .org 0x259dc-ORIGIN
L_000259dc:
    movt r0
    .org 0x259de-ORIGIN
L_000259de:
    xor #0x1,r0
    .org 0x259e0-ORIGIN
L_000259e0:
    rts
    .org 0x259e2-ORIGIN
L_000259e2:
    extu.b r0,r0
    .org 0x26740-ORIGIN
L_00026740:
    cmp/hs r0,r2
    .org 0x26742-ORIGIN
L_00026742:
    bt L_0002675c
    .org 0x26744-ORIGIN
L_00026744:
    mov.l r0,@-r15
    .org 0x26746-ORIGIN
L_00026746:
    sub r2,r0
    .org 0x26748-ORIGIN
L_00026748:
    sts macl,r1
    .org 0x2674a-ORIGIN
L_0002674a:
    mul.l r3,r0
    .org 0x2674c-ORIGIN
L_0002674c:
    sts macl,r0
    .org 0x2674e-ORIGIN
L_0002674e:
    lds r1,macl
    .org 0x26750-ORIGIN
L_00026750:
    swap.w r0,r0
    .org 0x26752-ORIGIN
L_00026752:
    mov.l @r15+,r2
    .org 0x26754-ORIGIN
L_00026754:
    extu.w r0,r0
    .org 0x26756-ORIGIN
L_00026756:
    sub r0,r2
    .org 0x26758-ORIGIN
L_00026758:
    rts
    .org 0x2675a-ORIGIN
L_0002675a:
    mov r2,r0
    .org 0x2675c-ORIGIN
L_0002675c:
    sub r0,r2
    .org 0x2675e-ORIGIN
L_0002675e:
    sts macl,r1
    .org 0x26760-ORIGIN
L_00026760:
    mul.l r3,r2
    .org 0x26762-ORIGIN
L_00026762:
    sts macl,r2
    .org 0x26764-ORIGIN
L_00026764:
    lds r1,macl
    .org 0x26766-ORIGIN
L_00026766:
    swap.w r2,r2
    .org 0x26768-ORIGIN
L_00026768:
    extu.w r2,r2
    .org 0x2676a-ORIGIN
L_0002676a:
    rts
    .org 0x2676c-ORIGIN
L_0002676c:
    add r2,r0
    .org 0x50a4c-ORIGIN
L_00050a4c:
    or r6,r4
    .org 0x50a4e-ORIGIN
L_00050a4e:
    or r5,r4
    .org 0x50a50-ORIGIN
L_00050a50:
    mov r4,r0
    .org 0x50a52-ORIGIN
L_00050a52:
    rts
    .org 0x50a54-ORIGIN
L_00050a54:
    and #0x3f,r0
