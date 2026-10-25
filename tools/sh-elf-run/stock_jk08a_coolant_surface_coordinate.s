! Complete stock coolant-coordinate caller and implicit surface/word helper closure.
    .text
    .balign 4
    .set ORIGIN,0x26040
    .org 0x26040-ORIGIN
L_00026040:
    sts.l pr,@-r15
    .org 0x26042-ORIGIN
L_00026042:
    mov.l r8,@-r15
    .org 0x26044-ORIGIN
L_00026044:
    mov.l r4,@-r15
    .org 0x26046-ORIGIN
L_00026046:
    extu.b r6,r3
    .org 0x26048-ORIGIN
L_00026048:
    mov.l P_00026080,r7
    .org 0x2604a-ORIGIN
L_0002604a:
    extu.b r5,r4
    .org 0x2604c-ORIGIN
L_0002604c:
    jsr @r7
    .org 0x2604e-ORIGIN
L_0002604e:
    mov #0x0,r5
    .org 0x26050-ORIGIN
L_00026050:
    mov r4,r0
    .org 0x26052-ORIGIN
L_00026052:
    mov r5,r1
    .org 0x26054-ORIGIN
L_00026054:
    mov r3,r4
    .org 0x26056-ORIGIN
L_00026056:
    jsr @r7
    .org 0x26058-ORIGIN
L_00026058:
    mov #0x0,r5
    .org 0x2605a-ORIGIN
L_0002605a:
    mov r4,r2
    .org 0x2605c-ORIGIN
L_0002605c:
    mov r5,r3
    .org 0x2605e-ORIGIN
L_0002605e:
    mov.l @r15+,r4
    .org 0x26060-ORIGIN
L_00026060:
    mov #0x7,r8
    .org 0x26062-ORIGIN
L_00026062:
    cmp/eq r8,r0
    .org 0x26064-ORIGIN
L_00026064:
    bf L_00026068
    .org 0x26066-ORIGIN
L_00026066:
    mov.l P_00026078,r1
    .org 0x26068-ORIGIN
L_00026068:
    cmp/eq r8,r2
    .org 0x2606a-ORIGIN
L_0002606a:
    bf L_0002606e
    .org 0x2606c-ORIGIN
L_0002606c:
    mov.l P_00026078,r3
    .org 0x2606e-ORIGIN
L_0002606e:
    mov.l @r15+,r8
    .org 0x26070-ORIGIN
L_00026070:
    lds.l @r15+,pr
    .org 0x26072-ORIGIN
L_00026072:
    mov.l P_0002607c,r7
    .org 0x26074-ORIGIN
L_00026074:
    jmp @r7
    .org 0x26076-ORIGIN
L_00026076:
    mov #0x8,r5
    .org 0x26078-ORIGIN
P_00026078:
    .long 0x00000000
    .org 0x2607c-ORIGIN
P_0002607c:
    .long 0x00026770
    .org 0x26080-ORIGIN
P_00026080:
    .long 0x00026ae0
    .org 0x263d8-ORIGIN
L_000263d8:
    mov.l P_000263f0,r0
    .org 0x263da-ORIGIN
L_000263da:
    extu.w r5,r5
    .org 0x263dc-ORIGIN
L_000263dc:
    cmp/hs r0,r5
    .org 0x263de-ORIGIN
L_000263de:
    bt L_000263e6
    .org 0x263e0-ORIGIN
L_000263e0:
    mov.l P_000263ec,r6
    .org 0x263e2-ORIGIN
L_000263e2:
    jmp @r6
    .org 0x263e4-ORIGIN
L_000263e4:
    mov #0x0,r3
    .org 0x263e6-ORIGIN
L_000263e6:
    rts
    .org 0x263e8-ORIGIN
L_000263e8:
    mov.w @(0xe,r4),r0
    .org 0x263ec-ORIGIN
P_000263ec:
    .long 0x00026a60
    .org 0x263f0-ORIGIN
P_000263f0:
    .long 0x0000e000
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
    .org 0x26770-ORIGIN
L_00026770:
    mov.l r8,@-r15
    .org 0x26772-ORIGIN
L_00026772:
    sts.l pr,@-r15
    .org 0x26774-ORIGIN
L_00026774:
    sts macl,r7
    .org 0x26776-ORIGIN
L_00026776:
    mulu.w r5,r0
    .org 0x26778-ORIGIN
L_00026778:
    add r2,r4
    .org 0x2677a-ORIGIN
L_0002677a:
    sts macl,r0
    .org 0x2677c-ORIGIN
L_0002677c:
    lds r7,macl
    .org 0x2677e-ORIGIN
L_0002677e:
    add r0,r4
    .org 0x26780-ORIGIN
L_00026780:
    add r4,r5
    .org 0x26782-ORIGIN
L_00026782:
    mov r1,r8
    .org 0x26784-ORIGIN
L_00026784:
    mov.l P_000267c8,r7
    .org 0x26786-ORIGIN
L_00026786:
    tst r3,r3
    .org 0x26788-ORIGIN
L_00026788:
    bt L_000267b0
    .org 0x2678a-ORIGIN
L_0002678a:
    mov.b @r4,r1
    .org 0x2678c-ORIGIN
L_0002678c:
    mov.b @(0x1,r4),r0
    .org 0x2678e-ORIGIN
L_0002678e:
    extu.b r0,r2
    .org 0x26790-ORIGIN
L_00026790:
    jsr @r7
    .org 0x26792-ORIGIN
L_00026792:
    extu.b r1,r0
    .org 0x26794-ORIGIN
L_00026794:
    tst r8,r8
    .org 0x26796-ORIGIN
L_00026796:
    bt L_000267c0
    .org 0x26798-ORIGIN
L_00026798:
    mov.l r0,@-r15
    .org 0x2679a-ORIGIN
L_0002679a:
    mov.b @r5,r1
    .org 0x2679c-ORIGIN
L_0002679c:
    mov.b @(0x1,r5),r0
    .org 0x2679e-ORIGIN
L_0002679e:
    extu.b r0,r2
    .org 0x267a0-ORIGIN
L_000267a0:
    jsr @r7
    .org 0x267a2-ORIGIN
L_000267a2:
    extu.b r1,r0
    .org 0x267a4-ORIGIN
L_000267a4:
    mov r0,r2
    .org 0x267a6-ORIGIN
L_000267a6:
    mov.l @r15+,r0
    .org 0x267a8-ORIGIN
L_000267a8:
    jsr @r7
    .org 0x267aa-ORIGIN
L_000267aa:
    mov r8,r3
    .org 0x267ac-ORIGIN
L_000267ac:
    bra L_000267c0
    .org 0x267ae-ORIGIN
L_000267ae:
    nop
    .org 0x267b0-ORIGIN
L_000267b0:
    tst r8,r8
    .org 0x267b2-ORIGIN
L_000267b2:
    bt/s L_000267c0
    .org 0x267b4-ORIGIN
L_000267b4:
    mov.b @r4,r0
    .org 0x267b6-ORIGIN
L_000267b6:
    mov.b @r5,r2
    .org 0x267b8-ORIGIN
L_000267b8:
    extu.b r0,r0
    .org 0x267ba-ORIGIN
L_000267ba:
    extu.b r2,r2
    .org 0x267bc-ORIGIN
L_000267bc:
    jsr @r7
    .org 0x267be-ORIGIN
L_000267be:
    mov r8,r3
    .org 0x267c0-ORIGIN
L_000267c0:
    lds.l @r15+,pr
    .org 0x267c2-ORIGIN
L_000267c2:
    rts
    .org 0x267c4-ORIGIN
L_000267c4:
    mov.l @r15+,r8
    .org 0x267c8-ORIGIN
P_000267c8:
    .long 0x00026740
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
    mov.l P_00026abc,r6
    .org 0x26ab6-ORIGIN
L_00026ab6:
    jmp @r6
    .org 0x26ab8-ORIGIN
L_00026ab8:
    nop
    .org 0x26abc-ORIGIN
P_00026abc:
    .long 0x00026740
    .org 0x26ae0-ORIGIN
L_00026ae0:
    shlr r4
    .org 0x26ae2-ORIGIN
L_00026ae2:
    rotcr r5
    .org 0x26ae4-ORIGIN
L_00026ae4:
    shlr r4
    .org 0x26ae6-ORIGIN
L_00026ae6:
    rotcr r5
    .org 0x26ae8-ORIGIN
L_00026ae8:
    shlr r4
    .org 0x26aea-ORIGIN
L_00026aea:
    rotcr r5
    .org 0x26aec-ORIGIN
L_00026aec:
    shlr r4
    .org 0x26aee-ORIGIN
L_00026aee:
    rotcr r5
    .org 0x26af0-ORIGIN
L_00026af0:
    shlr r4
    .org 0x26af2-ORIGIN
L_00026af2:
    rotcr r5
    .org 0x26af4-ORIGIN
L_00026af4:
    rts
    .org 0x26af6-ORIGIN
L_00026af6:
    swap.w r5,r5
    .org 0x52576-ORIGIN
L_00052576:
    mov.l r14,@-r15
    .org 0x52578-ORIGIN
L_00052578:
    sts.l pr,@-r15
    .org 0x5257a-ORIGIN
L_0005257a:
    sts.l macl,@-r15
    .org 0x5257c-ORIGIN
L_0005257c:
    stc.l gbr,@-r15
    .org 0x5257e-ORIGIN
L_0005257e:
    mov.l P_00052750,r0
    .org 0x52580-ORIGIN
L_00052580:
    ldc r0,gbr
    .org 0x52582-ORIGIN
L_00052582:
    mov.b @(0x7,gbr),r0
    .org 0x52584-ORIGIN
L_00052584:
    mov.l P_00052754,r4
    .org 0x52586-ORIGIN
L_00052586:
    extu.b r0,r5
    .org 0x52588-ORIGIN
L_00052588:
    mov.b @(0x88,gbr),r0
    .org 0x5258a-ORIGIN
L_0005258a:
    mov.l P_00052758,r2
    .org 0x5258c-ORIGIN
L_0005258c:
    jsr @r2
    .org 0x5258e-ORIGIN
L_0005258e:
    extu.b r0,r6
    .org 0x52590-ORIGIN
L_00052590:
    extu.b r0,r14
    .org 0x52592-ORIGIN
L_00052592:
    mov.w @(0x1ba,gbr),r0
    .org 0x52594-ORIGIN
L_00052594:
    mov #-0x1,r7
    .org 0x52596-ORIGIN
L_00052596:
    extu.w r0,r2
    .org 0x52598-ORIGIN
L_00052598:
    shll2 r2
    .org 0x5259a-ORIGIN
L_0005259a:
    shll2 r2
    .org 0x5259c-ORIGIN
L_0005259c:
    shll r2
    .org 0x5259e-ORIGIN
L_0005259e:
    extu.w r7,r5
    .org 0x525a0-ORIGIN
L_000525a0:
    cmp/hi r5,r2
    .org 0x525a2-ORIGIN
L_000525a2:
    bt L_000525a6
    .org 0x525a4-ORIGIN
L_000525a4:
    mov r2,r5
    .org 0x525a6-ORIGIN
L_000525a6:
    mov.l P_0005275c,r4
    .org 0x525a8-ORIGIN
L_000525a8:
    mov.l P_00052760,r2
    .org 0x525aa-ORIGIN
L_000525aa:
    jsr @r2
    .org 0x525ac-ORIGIN
L_000525ac:
    extu.w r5,r5
    .org 0x525ae-ORIGIN
L_000525ae:
    extu.w r0,r2
    .org 0x525b0-ORIGIN
L_000525b0:
    mul.l r14,r2
    .org 0x525b2-ORIGIN
L_000525b2:
    mov #-0x1,r7
    .org 0x525b4-ORIGIN
L_000525b4:
    extu.w r7,r7
    .org 0x525b6-ORIGIN
L_000525b6:
    sts macl,r6
    .org 0x525b8-ORIGIN
L_000525b8:
    shlr2 r6
    .org 0x525ba-ORIGIN
L_000525ba:
    shlr2 r6
    .org 0x525bc-ORIGIN
L_000525bc:
    shlr2 r6
    .org 0x525be-ORIGIN
L_000525be:
    shlr r6
    .org 0x525c0-ORIGIN
L_000525c0:
    cmp/hi r7,r6
    .org 0x525c2-ORIGIN
L_000525c2:
    bf L_000525c6
    .org 0x525c4-ORIGIN
L_000525c4:
    mov r7,r6
    .org 0x525c6-ORIGIN
L_000525c6:
    mov r6,r2
    .org 0x525c8-ORIGIN
L_000525c8:
    mov.l P_00052764,r6
    .org 0x525ca-ORIGIN
L_000525ca:
    mov.w P_0005269a,r0
    .org 0x525cc-ORIGIN
L_000525cc:
    mov.w r2,@(r0,r6)
    .org 0x525ce-ORIGIN
L_000525ce:
    ldc.l @r15+,gbr
    .org 0x525d0-ORIGIN
L_000525d0:
    lds.l @r15+,macl
    .org 0x525d2-ORIGIN
L_000525d2:
    lds.l @r15+,pr
    .org 0x525d4-ORIGIN
L_000525d4:
    rts
    .org 0x525d6-ORIGIN
L_000525d6:
    mov.l @r15+,r14
    .org 0x5269a-ORIGIN
P_0005269a:
    .word 0x03c6
    .org 0x52750-ORIGIN
P_00052750:
    .long 0xffff1068
    .org 0x52754-ORIGIN
P_00052754:
    .long 0x0000a8ea
    .org 0x52758-ORIGIN
P_00052758:
    .long 0x00026040
    .org 0x5275c-ORIGIN
P_0005275c:
    .long 0x00014ed2
    .org 0x52760-ORIGIN
P_00052760:
    .long 0x000263d8
    .org 0x52764-ORIGIN
P_00052764:
    .long 0xffff128c
