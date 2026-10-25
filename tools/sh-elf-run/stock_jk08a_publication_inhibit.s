! Conditional publication-inhibit producer and bounded snapshot window.
! Natural helpers retain exact stock instructions; scheduler reachability is explicit.
    .text
    .balign 4
    .set ORIGIN,0x20f1c
    .org 0x20f1c-ORIGIN
L_00020f1c:
    mov.l L_00021124,r4
    .org 0x20f1e-ORIGIN
L_00020f1e:
    mov.l L_00021128,r6
    .org 0x20f20-ORIGIN
L_00020f20:
    mov.b @r4,r2
    .org 0x20f22-ORIGIN
L_00020f22:
    mov.b @(0x1,r4),r0
    .org 0x20f24-ORIGIN
L_00020f24:
    mov.b r2,@r6
    .org 0x20f26-ORIGIN
L_00020f26:
    mov.b r0,@(0x1,r6)
    .org 0x20f28-ORIGIN
L_00020f28:
    mov.l L_0002112c,r6
    .org 0x20f2a-ORIGIN
L_00020f2a:
    mov.l L_00021130,r1
    .org 0x20f2c-ORIGIN
L_00020f2c:
    mov.b @r6,r2
    .org 0x20f2e-ORIGIN
L_00020f2e:
    mov.b @(0x1,r6),r0
    .org 0x20f30-ORIGIN
L_00020f30:
    mov.b r2,@r4
    .org 0x20f32-ORIGIN
L_00020f32:
    mov.l L_00021134,r2
    .org 0x20f34-ORIGIN
L_00020f34:
    mov.b r0,@(0x1,r4)
    .org 0x20f36-ORIGIN
L_00020f36:
    jsr @r11
    .org 0x20f38-ORIGIN
L_00020f38:
    mov #0x8,r0
    .org 0x21124-ORIGIN
L_00021124:
    .long 0xffff1064
    .org 0x21128-ORIGIN
L_00021128:
    .long 0xffff1068
    .org 0x2112c-ORIGIN
L_0002112c:
    .long 0xffff1066
    .org 0x21130-ORIGIN
L_00021130:
    .long 0xffff106a
    .org 0x21134-ORIGIN
L_00021134:
    .long 0xffff1072
    .org 0x22558-ORIGIN
L_00022558:
    mov.l r2,@-r15
    .org 0x2255a-ORIGIN
L_0002255a:
    mov.l r3,@-r15
    .org 0x2255c-ORIGIN
L_0002255c:
    mov.l r4,@-r15
    .org 0x2255e-ORIGIN
L_0002255e:
    cmp/eq #0,r0
    .org 0x22560-ORIGIN
L_00022560:
    bt L_00022588
    .org 0x22562-ORIGIN
L_00022562:
    mov r2,r4
    .org 0x22564-ORIGIN
L_00022564:
    add r0,r4
    .org 0x22566-ORIGIN
L_00022566:
    mov.b @r2+,r0
    .org 0x22568-ORIGIN
L_00022568:
    mov.b r0,@r1
    .org 0x2256a-ORIGIN
L_0002256a:
    cmp/hi r2,r4
    .org 0x2256c-ORIGIN
L_0002256c:
    bf L_00022588
    .org 0x2256e-ORIGIN
L_0002256e:
    mov.b @r2+,r0
    .org 0x22570-ORIGIN
L_00022570:
    mov.b r0,@(1,r1)
    .org 0x22572-ORIGIN
L_00022572:
    cmp/hi r2,r4
    .org 0x22574-ORIGIN
L_00022574:
    bf L_00022588
    .org 0x22576-ORIGIN
L_00022576:
    mov.b @r2+,r0
    .org 0x22578-ORIGIN
L_00022578:
    mov.b r0,@(2,r1)
    .org 0x2257a-ORIGIN
L_0002257a:
    cmp/hi r2,r4
    .org 0x2257c-ORIGIN
L_0002257c:
    bf L_00022588
    .org 0x2257e-ORIGIN
L_0002257e:
    mov.b @r2+,r0
    .org 0x22580-ORIGIN
L_00022580:
    mov.b r0,@(3,r1)
    .org 0x22582-ORIGIN
L_00022582:
    cmp/hi r2,r4
    .org 0x22584-ORIGIN
L_00022584:
    add #4,r1
    .org 0x22586-ORIGIN
L_00022586:
    bt L_00022566
    .org 0x22588-ORIGIN
L_00022588:
    mov.l @r15+,r4
    .org 0x2258a-ORIGIN
L_0002258a:
    mov.l @r15+,r3
    .org 0x2258c-ORIGIN
L_0002258c:
    rts
    .org 0x2258e-ORIGIN
L_0002258e:
    mov.l @r15+,r2
    .org 0x25e20-ORIGIN
L_00025e20:
    mov.l L_00025f10,r1
    .org 0x25e22-ORIGIN
L_00025e22:
    exts.w r4,r0
    .org 0x25e24-ORIGIN
L_00025e24:
    cmp/eq #-0x1,r0
    .org 0x25e26-ORIGIN
L_00025e26:
    bt L_00025e3e
    .org 0x25e28-ORIGIN
L_00025e28:
    mov r1,r6
    .org 0x25e2a-ORIGIN
L_00025e2a:
    mov r0,r2
    .org 0x25e2c-ORIGIN
L_00025e2c:
    shll r2
    .org 0x25e2e-ORIGIN
L_00025e2e:
    add r0,r2
    .org 0x25e30-ORIGIN
L_00025e30:
    add r2,r6
    .org 0x25e32-ORIGIN
L_00025e32:
    mov.b @(0x1,r6),r0
    .org 0x25e34-ORIGIN
L_00025e34:
    tst #0x80,r0
    .org 0x25e36-ORIGIN
L_00025e36:
    movt r0
    .org 0x25e38-ORIGIN
L_00025e38:
    xor #0x1,r0
    .org 0x25e3a-ORIGIN
L_00025e3a:
    bra L_00025e40
    .org 0x25e3c-ORIGIN
L_00025e3c:
    extu.b r0,r2
    .org 0x25e3e-ORIGIN
L_00025e3e:
    mov #0x0,r2
    .org 0x25e40-ORIGIN
L_00025e40:
    rts
    .org 0x25e42-ORIGIN
L_00025e42:
    mov r2,r0
    .org 0x25e4e-ORIGIN
L_00025e4e:
    sts.l pr,@-r15
    .org 0x25e50-ORIGIN
L_00025e50:
    bsr L_00025e20
    .org 0x25e52-ORIGIN
L_00025e52:
    mov #-0x1,r4
    .org 0x25e54-ORIGIN
L_00025e54:
    tst r0,r0
    .org 0x25e56-ORIGIN
L_00025e56:
    bf L_00025ec0
    .org 0x25e58-ORIGIN
L_00025e58:
    bsr L_00025e20
    .org 0x25e5a-ORIGIN
L_00025e5a:
    mov #-0x1,r4
    .org 0x25e5c-ORIGIN
L_00025e5c:
    tst r0,r0
    .org 0x25e5e-ORIGIN
L_00025e5e:
    bf L_00025ec0
    .org 0x25e60-ORIGIN
L_00025e60:
    bsr L_00025e20
    .org 0x25e62-ORIGIN
L_00025e62:
    mov #0x14,r4
    .org 0x25e64-ORIGIN
L_00025e64:
    tst r0,r0
    .org 0x25e66-ORIGIN
L_00025e66:
    bf L_00025ec0
    .org 0x25e68-ORIGIN
L_00025e68:
    bsr L_00025e20
    .org 0x25e6a-ORIGIN
L_00025e6a:
    mov #0x47,r4
    .org 0x25e6c-ORIGIN
L_00025e6c:
    tst r0,r0
    .org 0x25e6e-ORIGIN
L_00025e6e:
    bf L_00025ec0
    .org 0x25e70-ORIGIN
L_00025e70:
    bsr L_00025e20
    .org 0x25e72-ORIGIN
L_00025e72:
    mov #0x48,r4
    .org 0x25e74-ORIGIN
L_00025e74:
    tst r0,r0
    .org 0x25e76-ORIGIN
L_00025e76:
    bf L_00025ec0
    .org 0x25e78-ORIGIN
L_00025e78:
    bsr L_00025e20
    .org 0x25e7a-ORIGIN
L_00025e7a:
    mov #0x49,r4
    .org 0x25e7c-ORIGIN
L_00025e7c:
    tst r0,r0
    .org 0x25e7e-ORIGIN
L_00025e7e:
    bf L_00025ec0
    .org 0x25e80-ORIGIN
L_00025e80:
    bsr L_00025e20
    .org 0x25e82-ORIGIN
L_00025e82:
    mov #0x4a,r4
    .org 0x25e84-ORIGIN
L_00025e84:
    tst r0,r0
    .org 0x25e86-ORIGIN
L_00025e86:
    bf L_00025ec0
    .org 0x25e88-ORIGIN
L_00025e88:
    bsr L_00025e20
    .org 0x25e8a-ORIGIN
L_00025e8a:
    mov #0x4b,r4
    .org 0x25e8c-ORIGIN
L_00025e8c:
    tst r0,r0
    .org 0x25e8e-ORIGIN
L_00025e8e:
    bf L_00025ec0
    .org 0x25e90-ORIGIN
L_00025e90:
    bsr L_00025e20
    .org 0x25e92-ORIGIN
L_00025e92:
    mov #0x4c,r4
    .org 0x25e94-ORIGIN
L_00025e94:
    tst r0,r0
    .org 0x25e96-ORIGIN
L_00025e96:
    bf L_00025ec0
    .org 0x25e98-ORIGIN
L_00025e98:
    mov #-0x76,r3
    .org 0x25e9a-ORIGIN
L_00025e9a:
    extu.b r3,r4
    .org 0x25e9c-ORIGIN
L_00025e9c:
    bsr L_00025e20
    .org 0x25e9e-ORIGIN
L_00025e9e:
    nop
    .org 0x25ea0-ORIGIN
L_00025ea0:
    tst r0,r0
    .org 0x25ea2-ORIGIN
L_00025ea2:
    bf L_00025ec0
    .org 0x25ea4-ORIGIN
L_00025ea4:
    mov #-0x75,r3
    .org 0x25ea6-ORIGIN
L_00025ea6:
    extu.b r3,r4
    .org 0x25ea8-ORIGIN
L_00025ea8:
    bsr L_00025e20
    .org 0x25eaa-ORIGIN
L_00025eaa:
    nop
    .org 0x25eac-ORIGIN
L_00025eac:
    tst r0,r0
    .org 0x25eae-ORIGIN
L_00025eae:
    bf L_00025ec0
    .org 0x25eb0-ORIGIN
L_00025eb0:
    mov #-0x74,r3
    .org 0x25eb2-ORIGIN
L_00025eb2:
    extu.b r3,r4
    .org 0x25eb4-ORIGIN
L_00025eb4:
    bsr L_00025e20
    .org 0x25eb6-ORIGIN
L_00025eb6:
    nop
    .org 0x25eb8-ORIGIN
L_00025eb8:
    tst r0,r0
    .org 0x25eba-ORIGIN
L_00025eba:
    bf L_00025ec0
    .org 0x25ebc-ORIGIN
L_00025ebc:
    bra L_00025ec2
    .org 0x25ebe-ORIGIN
L_00025ebe:
    mov #0x0,r2
    .org 0x25ec0-ORIGIN
L_00025ec0:
    mov #0x1,r2
    .org 0x25ec2-ORIGIN
L_00025ec2:
    lds.l @r15+,pr
    .org 0x25ec4-ORIGIN
L_00025ec4:
    rts
    .org 0x25ec6-ORIGIN
L_00025ec6:
    mov r2,r0
    .org 0x25f10-ORIGIN
L_00025f10:
    .long 0xffff5718
    .org 0x26358-ORIGIN
L_00026358:
    mov.w L_0002636a,r0
    .org 0x2635a-ORIGIN
L_0002635a:
    extu.b r5,r5
    .org 0x2635c-ORIGIN
L_0002635c:
    cmp/hs r0,r5
    .org 0x2635e-ORIGIN
L_0002635e:
    bt L_00026366
    .org 0x26360-ORIGIN
L_00026360:
    mov.l L_0002636c,r6
    .org 0x26362-ORIGIN
L_00026362:
    jmp @r6
    .org 0x26364-ORIGIN
L_00026364:
    mov #0x0,r3
    .org 0x26366-ORIGIN
L_00026366:
    rts
    .org 0x26368-ORIGIN
L_00026368:
    mov.b @(0x3,r4),r0
    .org 0x2636a-ORIGIN
L_0002636a:
    .word 0x00c0
    .org 0x2636c-ORIGIN
L_0002636c:
    .long 0x00026a7c
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
    .org 0x26a60-ORIGIN
L_00026a60:
    shlr r5
    .org 0x26a62-ORIGIN
L_00026a62:
    rotcr r3
    .org 0x26a64-ORIGIN
L_00026a64:
    shlr r5
    .org 0x26a66-ORIGIN
L_00026a66:
    rotcr r3
    .org 0x26a68-ORIGIN
L_00026a68:
    shlr r5
    .org 0x26a6a-ORIGIN
L_00026a6a:
    rotcr r3
    .org 0x26a6c-ORIGIN
L_00026a6c:
    shlr r5
    .org 0x26a6e-ORIGIN
L_00026a6e:
    rotcr r3
    .org 0x26a70-ORIGIN
L_00026a70:
    shlr r5
    .org 0x26a72-ORIGIN
L_00026a72:
    rotcr r3
    .org 0x26a74-ORIGIN
L_00026a74:
    shlr r5
    .org 0x26a76-ORIGIN
L_00026a76:
    rotcr r3
    .org 0x26a78-ORIGIN
L_00026a78:
    shlr r5
    .org 0x26a7a-ORIGIN
L_00026a7a:
    rotcr r3
    .org 0x26a7c-ORIGIN
L_00026a7c:
    shlr r5
    .org 0x26a7e-ORIGIN
L_00026a7e:
    rotcr r3
    .org 0x26a80-ORIGIN
L_00026a80:
    shlr r5
    .org 0x26a82-ORIGIN
L_00026a82:
    rotcr r3
    .org 0x26a84-ORIGIN
L_00026a84:
    shlr r5
    .org 0x26a86-ORIGIN
L_00026a86:
    rotcr r3
    .org 0x26a88-ORIGIN
L_00026a88:
    shlr r5
    .org 0x26a8a-ORIGIN
L_00026a8a:
    rotcr r3
    .org 0x26a8c-ORIGIN
L_00026a8c:
    shlr r5
    .org 0x26a8e-ORIGIN
L_00026a8e:
    rotcr r3
    .org 0x26a90-ORIGIN
L_00026a90:
    shlr r5
    .org 0x26a92-ORIGIN
L_00026a92:
    rotcr r3
    .org 0x26a94-ORIGIN
L_00026a94:
    swap.w r3,r3
    .org 0x26a96-ORIGIN
L_00026a96:
    shlr8 r0
    .org 0x26a98-ORIGIN
L_00026a98:
    tst r0,r0
    .org 0x26a9a-ORIGIN
L_00026a9a:
    bt L_00026aaa
    .org 0x26a9c-ORIGIN
L_00026a9c:
    shll r5
    .org 0x26a9e-ORIGIN
L_00026a9e:
    add r5,r4
    .org 0x26aa0-ORIGIN
L_00026aa0:
    mov.w @r4,r1
    .org 0x26aa2-ORIGIN
L_00026aa2:
    mov.w @(0x2,r4),r0
    .org 0x26aa4-ORIGIN
L_00026aa4:
    extu.w r0,r2
    .org 0x26aa6-ORIGIN
L_00026aa6:
    bra L_00026ab4
    .org 0x26aa8-ORIGIN
L_00026aa8:
    extu.w r1,r0
    .org 0x26aaa-ORIGIN
L_00026aaa:
    add r5,r4
    .org 0x26aac-ORIGIN
L_00026aac:
    mov.b @r4,r1
    .org 0x26aae-ORIGIN
L_00026aae:
    mov.b @(0x1,r4),r0
    .org 0x26ab0-ORIGIN
L_00026ab0:
    extu.b r0,r2
    .org 0x26ab2-ORIGIN
L_00026ab2:
    extu.b r1,r0
    .org 0x26ab4-ORIGIN
L_00026ab4:
    mov.l L_00026abc,r6
    .org 0x26ab6-ORIGIN
L_00026ab6:
    jmp @r6
    .org 0x26ab8-ORIGIN
L_00026ab8:
    nop
    .org 0x26abc-ORIGIN
L_00026abc:
    .long 0x00026740
    .org 0x3e1da-ORIGIN
L_0003e1da:
    mov.l r14,@-r15
    .org 0x3e1dc-ORIGIN
L_0003e1dc:
    sts.l pr,@-r15
    .org 0x3e1de-ORIGIN
L_0003e1de:
    sts.l macl,@-r15
    .org 0x3e1e0-ORIGIN
L_0003e1e0:
    stc.l gbr,@-r15
    .org 0x3e1e2-ORIGIN
L_0003e1e2:
    mov.l L_0003e3d0,r0
    .org 0x3e1e4-ORIGIN
L_0003e1e4:
    ldc r0,gbr
    .org 0x3e1e6-ORIGIN
L_0003e1e6:
    add #-0x10,r15
    .org 0x3e1e8-ORIGIN
L_0003e1e8:
    mov.l L_0003e3d4,r2
    .org 0x3e1ea-ORIGIN
L_0003e1ea:
    jsr @r2
    .org 0x3e1ec-ORIGIN
L_0003e1ec:
    nop
    .org 0x3e1ee-ORIGIN
L_0003e1ee:
    tst r0,r0
    .org 0x3e1f0-ORIGIN
L_0003e1f0:
    bf L_0003e290
    .org 0x3e1f2-ORIGIN
L_0003e1f2:
    mov.l L_0003e3d8,r6
    .org 0x3e1f4-ORIGIN
L_0003e1f4:
    mov.b @(0x4,r6),r0
    .org 0x3e1f6-ORIGIN
L_0003e1f6:
    tst #0x40,r0
    .org 0x3e1f8-ORIGIN
L_0003e1f8:
    bf L_0003e1fe
    .org 0x3e1fa-ORIGIN
L_0003e1fa:
    bra L_0003e298
    .org 0x3e1fc-ORIGIN
L_0003e1fc:
    mov #0x0,r0
    .org 0x3e1fe-ORIGIN
L_0003e1fe:
    mov.w @(0x126,gbr),r0
    .org 0x3e200-ORIGIN
L_0003e200:
    mov.l L_0003e3cc,r2
    .org 0x3e202-ORIGIN
L_0003e202:
    extu.w r0,r6
    .org 0x3e204-ORIGIN
L_0003e204:
    mov #0x36,r0
    .org 0x3e206-ORIGIN
L_0003e206:
    mov.w @(r0,r2),r5
    .org 0x3e208-ORIGIN
L_0003e208:
    extu.w r5,r5
    .org 0x3e20a-ORIGIN
L_0003e20a:
    cmp/ge r5,r6
    .org 0x3e20c-ORIGIN
L_0003e20c:
    bf L_0003e268
    .org 0x3e20e-ORIGIN
L_0003e20e:
    mov.w @(0x126,gbr),r0
    .org 0x3e210-ORIGIN
L_0003e210:
    mov #0x1,r7
    .org 0x3e212-ORIGIN
L_0003e212:
    mov.l L_0003e3dc,r1
    .org 0x3e214-ORIGIN
L_0003e214:
    shll8 r7
    .org 0x3e216-ORIGIN
L_0003e216:
    extu.w r0,r6
    .org 0x3e218-ORIGIN
L_0003e218:
    mov r7,r4
    .org 0x3e21a-ORIGIN
L_0003e21a:
    mov.b @(0x1,r1),r0
    .org 0x3e21c-ORIGIN
L_0003e21c:
    sub r5,r6
    .org 0x3e21e-ORIGIN
L_0003e21e:
    extu.b r0,r2
    .org 0x3e220-ORIGIN
L_0003e220:
    mov r0,r1
    .org 0x3e222-ORIGIN
L_0003e222:
    sub r2,r4
    .org 0x3e224-ORIGIN
L_0003e224:
    extu.b r0,r2
    .org 0x3e226-ORIGIN
L_0003e226:
    mov.w @(0x8,gbr),r0
    .org 0x3e228-ORIGIN
L_0003e228:
    mul.l r6,r2
    .org 0x3e22a-ORIGIN
L_0003e22a:
    extu.w r0,r2
    .org 0x3e22c-ORIGIN
L_0003e22c:
    sts macl,r6
    .org 0x3e22e-ORIGIN
L_0003e22e:
    mul.l r2,r4
    .org 0x3e230-ORIGIN
L_0003e230:
    shll8 r6
    .org 0x3e232-ORIGIN
L_0003e232:
    sts macl,r2
    .org 0x3e234-ORIGIN
L_0003e234:
    add r2,r6
    .org 0x3e236-ORIGIN
L_0003e236:
    mov #-0x1,r2
    .org 0x3e238-ORIGIN
L_0003e238:
    shlr8 r6
    .org 0x3e23a-ORIGIN
L_0003e23a:
    extu.w r2,r2
    .org 0x3e23c-ORIGIN
L_0003e23c:
    cmp/hi r2,r6
    .org 0x3e23e-ORIGIN
L_0003e23e:
    bt L_0003e264
    .org 0x3e240-ORIGIN
L_0003e240:
    mov.w @(0x126,gbr),r0
    .org 0x3e242-ORIGIN
L_0003e242:
    mov.l L_0003e3dc,r1
    .org 0x3e244-ORIGIN
L_0003e244:
    extu.w r0,r6
    .org 0x3e246-ORIGIN
L_0003e246:
    mov.b @(0x1,r1),r0
    .org 0x3e248-ORIGIN
L_0003e248:
    sub r5,r6
    .org 0x3e24a-ORIGIN
L_0003e24a:
    extu.b r0,r2
    .org 0x3e24c-ORIGIN
L_0003e24c:
    mul.l r6,r2
    .org 0x3e24e-ORIGIN
L_0003e24e:
    extu.b r0,r4
    .org 0x3e250-ORIGIN
L_0003e250:
    mov.w @(0x8,gbr),r0
    .org 0x3e252-ORIGIN
L_0003e252:
    sub r4,r7
    .org 0x3e254-ORIGIN
L_0003e254:
    extu.w r0,r6
    .org 0x3e256-ORIGIN
L_0003e256:
    mov r0,r1
    .org 0x3e258-ORIGIN
L_0003e258:
    sts macl,r2
    .org 0x3e25a-ORIGIN
L_0003e25a:
    mul.l r6,r7
    .org 0x3e25c-ORIGIN
L_0003e25c:
    shll8 r2
    .org 0x3e25e-ORIGIN
L_0003e25e:
    sts macl,r6
    .org 0x3e260-ORIGIN
L_0003e260:
    add r6,r2
    .org 0x3e262-ORIGIN
L_0003e262:
    shlr8 r2
    .org 0x3e264-ORIGIN
L_0003e264:
    bra L_0003e26a
    .org 0x3e266-ORIGIN
L_0003e266:
    mov r2,r0
    .org 0x3e268-ORIGIN
L_0003e268:
    mov #0x0,r0
    .org 0x3e26a-ORIGIN
L_0003e26a:
    mov.w r0,@(0x0,gbr)
    .org 0x3e26c-ORIGIN
L_0003e26c:
    mov.w @(0x124,gbr),r0
    .org 0x3e26e-ORIGIN
L_0003e26e:
    mov.l r0,@r15
    .org 0x3e270-ORIGIN
L_0003e270:
    mov.w r0,@(0x126,gbr)
    .org 0x3e272-ORIGIN
L_0003e272:
    mov.w @(0x122,gbr),r0
    .org 0x3e274-ORIGIN
L_0003e274:
    mov.l r0,@(0x4,r15)
    .org 0x3e276-ORIGIN
L_0003e276:
    mov.w r0,@(0x124,gbr)
    .org 0x3e278-ORIGIN
L_0003e278:
    mov.w @(0x120,gbr),r0
    .org 0x3e27a-ORIGIN
L_0003e27a:
    mov.l r0,@(0x8,r15)
    .org 0x3e27c-ORIGIN
L_0003e27c:
    mov.w r0,@(0x122,gbr)
    .org 0x3e27e-ORIGIN
L_0003e27e:
    mov.w @(0x11e,gbr),r0
    .org 0x3e280-ORIGIN
L_0003e280:
    bra L_0003e2a8
    .org 0x3e282-ORIGIN
L_0003e282:
    mov.l r0,@(0xc,r15)
    .org 0x3e290-ORIGIN
L_0003e290:
    mov.l L_0003e3dc,r3
    .org 0x3e292-ORIGIN
L_0003e292:
    mov.b @r3,r2
    .org 0x3e294-ORIGIN
L_0003e294:
    extu.b r2,r0
    .org 0x3e296-ORIGIN
L_0003e296:
    shll8 r0
    .org 0x3e298-ORIGIN
L_0003e298:
    mov.l L_0003e3cc,r2
    .org 0x3e29a-ORIGIN
L_0003e29a:
    mov.w r0,@(0x0,gbr)
    .org 0x3e29c-ORIGIN
L_0003e29c:
    mov #0x36,r0
    .org 0x3e29e-ORIGIN
L_0003e29e:
    mov.w @(r0,r2),r5
    .org 0x3e2a0-ORIGIN
L_0003e2a0:
    mov r5,r0
    .org 0x3e2a2-ORIGIN
L_0003e2a2:
    mov.w r0,@(0x126,gbr)
    .org 0x3e2a4-ORIGIN
L_0003e2a4:
    mov.w r0,@(0x124,gbr)
    .org 0x3e2a6-ORIGIN
L_0003e2a6:
    mov.w r0,@(0x122,gbr)
    .org 0x3e2a8-ORIGIN
L_0003e2a8:
    mov.l L_0003e3e0,r14
    .org 0x3e2aa-ORIGIN
L_0003e2aa:
    mov.w r0,@(0x120,gbr)
    .org 0x3e2ac-ORIGIN
L_0003e2ac:
    mov r5,r0
    .org 0x3e2ae-ORIGIN
L_0003e2ae:
    mov.w r0,@(0x11e,gbr)
    .org 0x3e2b0-ORIGIN
L_0003e2b0:
    mov.b @r14,r0
    .org 0x3e2b2-ORIGIN
L_0003e2b2:
    and #0x20,r0
    .org 0x3e2b4-ORIGIN
L_0003e2b4:
    tst r0,r0
    .org 0x3e2b6-ORIGIN
L_0003e2b6:
    bf/s L_0003e2e6
    .org 0x3e2b8-ORIGIN
L_0003e2b8:
    mov r0,r6
    .org 0x3e2ba-ORIGIN
L_0003e2ba:
    extu.w r5,r2
    .org 0x3e2bc-ORIGIN
L_0003e2bc:
    add #-0x60,r2
    .org 0x3e2be-ORIGIN
L_0003e2be:
    cmp/pz r2
    .org 0x3e2c0-ORIGIN
L_0003e2c0:
    bt L_0003e2c4
    .org 0x3e2c2-ORIGIN
L_0003e2c2:
    mov #0x0,r2
    .org 0x3e2c4-ORIGIN
L_0003e2c4:
    mov #-0x1,r7
    .org 0x3e2c6-ORIGIN
L_0003e2c6:
    extu.b r7,r5
    .org 0x3e2c8-ORIGIN
L_0003e2c8:
    cmp/gt r5,r2
    .org 0x3e2ca-ORIGIN
L_0003e2ca:
    bt L_0003e2ce
    .org 0x3e2cc-ORIGIN
L_0003e2cc:
    mov r2,r5
    .org 0x3e2ce-ORIGIN
L_0003e2ce:
    mov.l L_0003e3e4,r4
    .org 0x3e2d0-ORIGIN
L_0003e2d0:
    mov.l L_0003e3e8,r2
    .org 0x3e2d2-ORIGIN
L_0003e2d2:
    jsr @r2
    .org 0x3e2d4-ORIGIN
L_0003e2d4:
    extu.b r5,r5
    .org 0x3e2d6-ORIGIN
L_0003e2d6:
    mov.l L_0003e3ec,r5
    .org 0x3e2d8-ORIGIN
L_0003e2d8:
    mov r0,r2
    .org 0x3e2da-ORIGIN
L_0003e2da:
    mov.b r0,@(0x90,gbr)
    .org 0x3e2dc-ORIGIN
L_0003e2dc:
    mov #0x10,r0
    .org 0x3e2de-ORIGIN
L_0003e2de:
    mov.b r2,@(r0,r5)
    .org 0x3e2e0-ORIGIN
L_0003e2e0:
    mov.b @r14,r0
    .org 0x3e2e2-ORIGIN
L_0003e2e2:
    and #0x20,r0
    .org 0x3e2e4-ORIGIN
L_0003e2e4:
    mov r0,r6
    .org 0x3e2e6-ORIGIN
L_0003e2e6:
    extu.b r6,r6
    .org 0x3e2e8-ORIGIN
L_0003e2e8:
    tst r6,r6
    .org 0x3e2ea-ORIGIN
L_0003e2ea:
    bt L_0003e316
    .org 0x3e2ec-ORIGIN
L_0003e2ec:
    mov.l L_0003e3ec,r5
    .org 0x3e2ee-ORIGIN
L_0003e2ee:
    mov #0x10,r0
    .org 0x3e2f0-ORIGIN
L_0003e2f0:
    mov.b @(r0,r5),r2
    .org 0x3e2f2-ORIGIN
L_0003e2f2:
    tst r2,r2
    .org 0x3e2f4-ORIGIN
L_0003e2f4:
    bt L_0003e2fe
    .org 0x3e2f6-ORIGIN
L_0003e2f6:
    mov.l L_0003e3f0,r6
    .org 0x3e2f8-ORIGIN
L_0003e2f8:
    mov.b @r6,r0
    .org 0x3e2fa-ORIGIN
L_0003e2fa:
    tst #0x80,r0
    .org 0x3e2fc-ORIGIN
L_0003e2fc:
    bt L_0003e316
    .org 0x3e2fe-ORIGIN
L_0003e2fe:
    mov.w @(0x0,gbr),r0
    .org 0x3e300-ORIGIN
L_0003e300:
    extu.w r0,r5
    .org 0x3e302-ORIGIN
L_0003e302:
    cmp/pz r5
    .org 0x3e304-ORIGIN
L_0003e304:
    bt L_0003e30c
    .org 0x3e306-ORIGIN
L_0003e306:
    mov #-0x1,r7
    .org 0x3e308-ORIGIN
L_0003e308:
    extu.b r7,r7
    .org 0x3e30a-ORIGIN
L_0003e30a:
    add r7,r5
    .org 0x3e30c-ORIGIN
L_0003e30c:
    shlr8 r5
    .org 0x3e30e-ORIGIN
L_0003e30e:
    swap.w r5,r2
    .org 0x3e310-ORIGIN
L_0003e310:
    exts.b r2,r6
    .org 0x3e312-ORIGIN
L_0003e312:
    bra L_0003e318
    .org 0x3e314-ORIGIN
L_0003e314:
    xtrct r6,r2
    .org 0x3e316-ORIGIN
L_0003e316:
    mov #0x0,r2
    .org 0x3e318-ORIGIN
L_0003e318:
    mov.l L_0003e3f4,r5
    .org 0x3e31a-ORIGIN
L_0003e31a:
    mov.b r2,@r5
    .org 0x3e31c-ORIGIN
L_0003e31c:
    mov.l L_0003e3f8,r5
    .org 0x3e31e-ORIGIN
L_0003e31e:
    mov.b @(0x9,r5),r0
    .org 0x3e320-ORIGIN
L_0003e320:
    tst #0x8,r0
    .org 0x3e322-ORIGIN
L_0003e322:
    bf/s L_0003e33a
    .org 0x3e324-ORIGIN
L_0003e324:
    mov r0,r6
    .org 0x3e326-ORIGIN
L_0003e326:
    mov.l L_0003e3c4,r7
    .org 0x3e328-ORIGIN
L_0003e328:
    mov #0x20,r0
    .org 0x3e32a-ORIGIN
L_0003e32a:
    mov.l L_0003e3fc,r4
    .org 0x3e32c-ORIGIN
L_0003e32c:
    mov.w @(r0,r7),r2
    .org 0x3e32e-ORIGIN
L_0003e32e:
    mov.w L_0003e3ba,r0
    .org 0x3e330-ORIGIN
L_0003e330:
    mov.w r2,@(r0,r4)
    .org 0x3e332-ORIGIN
L_0003e332:
    mov r6,r0
    .org 0x3e334-ORIGIN
L_0003e334:
    or #0x8,r0
    .org 0x3e336-ORIGIN
L_0003e336:
    bra L_0003e376
    .org 0x3e338-ORIGIN
L_0003e338:
    mov.b r0,@(0x9,r5)
    .org 0x3e33a-ORIGIN
L_0003e33a:
    mov.w L_0003e3bc,r6
    .org 0x3e33c-ORIGIN
L_0003e33c:
    mov.b @r6,r0
    .org 0x3e33e-ORIGIN
L_0003e33e:
    tst #0x40,r0
    .org 0x3e340-ORIGIN
L_0003e340:
    bt L_0003e376
    .org 0x3e342-ORIGIN
L_0003e342:
    mov.l L_0003e3c4,r7
    .org 0x3e344-ORIGIN
L_0003e344:
    mov #0x20,r0
    .org 0x3e346-ORIGIN
L_0003e346:
    mov.l L_0003e3fc,r6
    .org 0x3e348-ORIGIN
L_0003e348:
    mov.w @(r0,r7),r4
    .org 0x3e34a-ORIGIN
L_0003e34a:
    mov.w L_0003e3ba,r0
    .org 0x3e34c-ORIGIN
L_0003e34c:
    extu.w r4,r4
    .org 0x3e34e-ORIGIN
L_0003e34e:
    mov.w @(r0,r6),r2
    .org 0x3e350-ORIGIN
L_0003e350:
    extu.w r2,r6
    .org 0x3e352-ORIGIN
L_0003e352:
    cmp/gt r6,r4
    .org 0x3e354-ORIGIN
L_0003e354:
    bf/s L_0003e35c
    .org 0x3e356-ORIGIN
L_0003e356:
    sub r4,r6
    .org 0x3e358-ORIGIN
L_0003e358:
    extu.w r6,r2
    .org 0x3e35a-ORIGIN
L_0003e35a:
    neg r2,r6
    .org 0x3e35c-ORIGIN
L_0003e35c:
    mov #-0x1,r7
    .org 0x3e35e-ORIGIN
L_0003e35e:
    extu.w r6,r6
    .org 0x3e360-ORIGIN
L_0003e360:
    extu.b r7,r2
    .org 0x3e362-ORIGIN
L_0003e362:
    cmp/gt r2,r6
    .org 0x3e364-ORIGIN
L_0003e364:
    bt L_0003e368
    .org 0x3e366-ORIGIN
L_0003e366:
    mov r6,r2
    .org 0x3e368-ORIGIN
L_0003e368:
    mov r2,r6
    .org 0x3e36a-ORIGIN
L_0003e36a:
    mov.l L_0003e400,r2
    .org 0x3e36c-ORIGIN
L_0003e36c:
    mov #0x67,r0
    .org 0x3e36e-ORIGIN
L_0003e36e:
    mov.l L_0003e3fc,r3
    .org 0x3e370-ORIGIN
L_0003e370:
    mov.b r6,@(r0,r2)
    .org 0x3e372-ORIGIN
L_0003e372:
    mov.w L_0003e3ba,r0
    .org 0x3e374-ORIGIN
L_0003e374:
    mov.w r4,@(r0,r3)
    .org 0x3e376-ORIGIN
L_0003e376:
    add #0x10,r15
    .org 0x3e378-ORIGIN
L_0003e378:
    ldc.l @r15+,gbr
    .org 0x3e37a-ORIGIN
L_0003e37a:
    lds.l @r15+,macl
    .org 0x3e37c-ORIGIN
L_0003e37c:
    lds.l @r15+,pr
    .org 0x3e37e-ORIGIN
L_0003e37e:
    rts
    .org 0x3e380-ORIGIN
L_0003e380:
    mov.l @r15+,r14
    .org 0x3e3ba-ORIGIN
L_0003e3ba:
    .word 0x04e2
    .org 0x3e3bc-ORIGIN
L_0003e3bc:
    .word 0x84c3
    .org 0x3e3c4-ORIGIN
L_0003e3c4:
    .long 0xffff11d4
    .org 0x3e3cc-ORIGIN
L_0003e3cc:
    .long 0xffff1114
    .org 0x3e3d0-ORIGIN
L_0003e3d0:
    .long 0xffff1e50
    .org 0x3e3d4-ORIGIN
L_0003e3d4:
    .long 0x00025e4e
    .org 0x3e3d8-ORIGIN
L_0003e3d8:
    .long 0xffff24b4
    .org 0x3e3dc-ORIGIN
L_0003e3dc:
    .long 0x000084a3
    .org 0x3e3e0-ORIGIN
L_0003e3e0:
    .long 0xffff2459
    .org 0x3e3e4-ORIGIN
L_0003e3e4:
    .long 0x0001202e
    .org 0x3e3e8-ORIGIN
L_0003e3e8:
    .long 0x00026358
    .org 0x3e3ec-ORIGIN
L_0003e3ec:
    .long 0xffff256a
    .org 0x3e3f0-ORIGIN
L_0003e3f0:
    .long 0xffff2451
    .org 0x3e3f4-ORIGIN
L_0003e3f4:
    .long 0xffff1072
    .org 0x3e3f8-ORIGIN
L_0003e3f8:
    .long 0xffff421d
    .org 0x3e3fc-ORIGIN
L_0003e3fc:
    .long 0xffff39c4
    .org 0x3e400-ORIGIN
L_0003e400:
    .long 0xffff277e
