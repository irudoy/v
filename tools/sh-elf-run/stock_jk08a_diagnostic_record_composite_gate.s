! Complete 25A12 caller and full 259E4 predicate with actual sentinel calls and natural frame restoration.
    .text
    .balign 4
    .set ORIGIN,0x259e4
    .org 0x259e4-ORIGIN
L_000259e4:
    mov.l P_00025b98,r1
    .org 0x259e6-ORIGIN
L_000259e6:
    exts.w r4,r0
    .org 0x259e8-ORIGIN
L_000259e8:
    cmp/eq #-0x1,r0
    .org 0x259ea-ORIGIN
L_000259ea:
    bt L_00025a0c
    .org 0x259ec-ORIGIN
L_000259ec:
    mov r0,r7
    .org 0x259ee-ORIGIN
L_000259ee:
    shll r7
    .org 0x259f0-ORIGIN
L_000259f0:
    mov r1,r2
    .org 0x259f2-ORIGIN
L_000259f2:
    add r0,r7
    .org 0x259f4-ORIGIN
L_000259f4:
    add r7,r2
    .org 0x259f6-ORIGIN
L_000259f6:
    mov.b @(0x2,r2),r0
    .org 0x259f8-ORIGIN
L_000259f8:
    tst #0x40,r0
    .org 0x259fa-ORIGIN
L_000259fa:
    bf/s L_00025a0e
    .org 0x259fc-ORIGIN
L_000259fc:
    mov #0x1,r5
    .org 0x259fe-ORIGIN
L_000259fe:
    mov r1,r2
    .org 0x25a00-ORIGIN
L_00025a00:
    add r7,r2
    .org 0x25a02-ORIGIN
L_00025a02:
    mov.b @(0x2,r2),r0
    .org 0x25a04-ORIGIN
L_00025a04:
    tst #0x20,r0
    .org 0x25a06-ORIGIN
L_00025a06:
    bf L_00025a0e
    .org 0x25a08-ORIGIN
L_00025a08:
    bra L_00025a0e
    .org 0x25a0a-ORIGIN
L_00025a0a:
    mov #0x0,r5
    .org 0x25a0c-ORIGIN
L_00025a0c:
    mov #0x0,r5
    .org 0x25a0e-ORIGIN
L_00025a0e:
    rts
    .org 0x25a10-ORIGIN
L_00025a10:
    mov r5,r0
    .org 0x25a12-ORIGIN
L_00025a12:
    sts.l pr,@-r15
    .org 0x25a14-ORIGIN
L_00025a14:
    bsr L_000259e4
    .org 0x25a16-ORIGIN
L_00025a16:
    mov #-0x1,r4
    .org 0x25a18-ORIGIN
L_00025a18:
    tst r0,r0
    .org 0x25a1a-ORIGIN
L_00025a1a:
    bf L_00025a84
    .org 0x25a1c-ORIGIN
L_00025a1c:
    bsr L_000259e4
    .org 0x25a1e-ORIGIN
L_00025a1e:
    mov #-0x1,r4
    .org 0x25a20-ORIGIN
L_00025a20:
    tst r0,r0
    .org 0x25a22-ORIGIN
L_00025a22:
    bf L_00025a84
    .org 0x25a24-ORIGIN
L_00025a24:
    bsr L_000259e4
    .org 0x25a26-ORIGIN
L_00025a26:
    mov #0x14,r4
    .org 0x25a28-ORIGIN
L_00025a28:
    tst r0,r0
    .org 0x25a2a-ORIGIN
L_00025a2a:
    bf L_00025a84
    .org 0x25a2c-ORIGIN
L_00025a2c:
    bsr L_000259e4
    .org 0x25a2e-ORIGIN
L_00025a2e:
    mov #0x47,r4
    .org 0x25a30-ORIGIN
L_00025a30:
    tst r0,r0
    .org 0x25a32-ORIGIN
L_00025a32:
    bf L_00025a84
    .org 0x25a34-ORIGIN
L_00025a34:
    bsr L_000259e4
    .org 0x25a36-ORIGIN
L_00025a36:
    mov #0x48,r4
    .org 0x25a38-ORIGIN
L_00025a38:
    tst r0,r0
    .org 0x25a3a-ORIGIN
L_00025a3a:
    bf L_00025a84
    .org 0x25a3c-ORIGIN
L_00025a3c:
    bsr L_000259e4
    .org 0x25a3e-ORIGIN
L_00025a3e:
    mov #0x49,r4
    .org 0x25a40-ORIGIN
L_00025a40:
    tst r0,r0
    .org 0x25a42-ORIGIN
L_00025a42:
    bf L_00025a84
    .org 0x25a44-ORIGIN
L_00025a44:
    bsr L_000259e4
    .org 0x25a46-ORIGIN
L_00025a46:
    mov #0x4a,r4
    .org 0x25a48-ORIGIN
L_00025a48:
    tst r0,r0
    .org 0x25a4a-ORIGIN
L_00025a4a:
    bf L_00025a84
    .org 0x25a4c-ORIGIN
L_00025a4c:
    bsr L_000259e4
    .org 0x25a4e-ORIGIN
L_00025a4e:
    mov #0x4b,r4
    .org 0x25a50-ORIGIN
L_00025a50:
    tst r0,r0
    .org 0x25a52-ORIGIN
L_00025a52:
    bf L_00025a84
    .org 0x25a54-ORIGIN
L_00025a54:
    bsr L_000259e4
    .org 0x25a56-ORIGIN
L_00025a56:
    mov #0x4c,r4
    .org 0x25a58-ORIGIN
L_00025a58:
    tst r0,r0
    .org 0x25a5a-ORIGIN
L_00025a5a:
    bf L_00025a84
    .org 0x25a5c-ORIGIN
L_00025a5c:
    mov #-0x76,r3
    .org 0x25a5e-ORIGIN
L_00025a5e:
    extu.b r3,r4
    .org 0x25a60-ORIGIN
L_00025a60:
    bsr L_000259e4
    .org 0x25a62-ORIGIN
L_00025a62:
    nop
    .org 0x25a64-ORIGIN
L_00025a64:
    tst r0,r0
    .org 0x25a66-ORIGIN
L_00025a66:
    bf L_00025a84
    .org 0x25a68-ORIGIN
L_00025a68:
    mov #-0x75,r3
    .org 0x25a6a-ORIGIN
L_00025a6a:
    extu.b r3,r4
    .org 0x25a6c-ORIGIN
L_00025a6c:
    bsr L_000259e4
    .org 0x25a6e-ORIGIN
L_00025a6e:
    nop
    .org 0x25a70-ORIGIN
L_00025a70:
    tst r0,r0
    .org 0x25a72-ORIGIN
L_00025a72:
    bf L_00025a84
    .org 0x25a74-ORIGIN
L_00025a74:
    mov #-0x74,r3
    .org 0x25a76-ORIGIN
L_00025a76:
    extu.b r3,r4
    .org 0x25a78-ORIGIN
L_00025a78:
    bsr L_000259e4
    .org 0x25a7a-ORIGIN
L_00025a7a:
    nop
    .org 0x25a7c-ORIGIN
L_00025a7c:
    tst r0,r0
    .org 0x25a7e-ORIGIN
L_00025a7e:
    bf L_00025a84
    .org 0x25a80-ORIGIN
L_00025a80:
    bra L_00025a86
    .org 0x25a82-ORIGIN
L_00025a82:
    mov #0x0,r2
    .org 0x25a84-ORIGIN
L_00025a84:
    mov #0x1,r2
    .org 0x25a86-ORIGIN
L_00025a86:
    lds.l @r15+,pr
    .org 0x25a88-ORIGIN
L_00025a88:
    rts
    .org 0x25a8a-ORIGIN
L_00025a8a:
    mov r2,r0
    .org 0x25b98-ORIGIN
P_00025b98:
    .long 0xffff5718
