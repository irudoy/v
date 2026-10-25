! Explicit stock sexy-tamarin entry and natural byte-lookup/division closure.
! Index zero reads 0001252A and 000123F2. A nonzero index reads 00012532 and 000123FA.
    .text
    .balign 4
    .set ORIGIN,0x21bbc
    .org 0x21bbc-ORIGIN
L_00021bbc:
    mov.l r2,@-r15
    .org 0x21bbe-ORIGIN
L_00021bbe:
    tst r0,r0
    .org 0x21bc0-ORIGIN
L_00021bc0:
    bt L_00021c70
    .org 0x21bc2-ORIGIN
L_00021bc2:
    mov.l r3,@-r15
    .org 0x21bc4-ORIGIN
L_00021bc4:
    div0s r0,r1
    .org 0x21bc6-ORIGIN
L_00021bc6:
    movt r3
    .org 0x21bc8-ORIGIN
L_00021bc8:
    cmp/pl r0
    .org 0x21bca-ORIGIN
L_00021bca:
    bt L_00021bd0
    .org 0x21bcc-ORIGIN
L_00021bcc:
    add #-0x1,r0
    .org 0x21bce-ORIGIN
L_00021bce:
    not r0,r0
    .org 0x21bd0-ORIGIN
L_00021bd0:
    cmp/pl r1
    .org 0x21bd2-ORIGIN
L_00021bd2:
    bt L_00021bd8
    .org 0x21bd4-ORIGIN
L_00021bd4:
    add #-0x1,r1
    .org 0x21bd6-ORIGIN
L_00021bd6:
    not r1,r1
    .org 0x21bd8-ORIGIN
L_00021bd8:
    extu.w r0,r2
    .org 0x21bda-ORIGIN
L_00021bda:
    cmp/eq r2,r0
    .org 0x21bdc-ORIGIN
L_00021bdc:
    bf L_00021c7c
    .org 0x21bde-ORIGIN
L_00021bde:
    div0u
    .org 0x21be0-ORIGIN
L_00021be0:
    shll8 r0
    .org 0x21be2-ORIGIN
L_00021be2:
    cmp/hi r1,r0
    .org 0x21be4-ORIGIN
L_00021be4:
    bf L_00021c08
    .org 0x21be6-ORIGIN
L_00021be6:
    div1 r0,r1
    .org 0x21be8-ORIGIN
L_00021be8:
    div1 r0,r1
    .org 0x21bea-ORIGIN
L_00021bea:
    div1 r0,r1
    .org 0x21bec-ORIGIN
L_00021bec:
    div1 r0,r1
    .org 0x21bee-ORIGIN
L_00021bee:
    div1 r0,r1
    .org 0x21bf0-ORIGIN
L_00021bf0:
    div1 r0,r1
    .org 0x21bf2-ORIGIN
L_00021bf2:
    div1 r0,r1
    .org 0x21bf4-ORIGIN
L_00021bf4:
    div1 r0,r1
    .org 0x21bf6-ORIGIN
L_00021bf6:
    rotcl r1
    .org 0x21bf8-ORIGIN
L_00021bf8:
    extu.b r1,r0
    .org 0x21bfa-ORIGIN
L_00021bfa:
    rotcr r3
    .org 0x21bfc-ORIGIN
L_00021bfc:
    bf L_00021c02
    .org 0x21bfe-ORIGIN
L_00021bfe:
    not r0,r0
    .org 0x21c00-ORIGIN
L_00021c00:
    add #0x1,r0
    .org 0x21c02-ORIGIN
L_00021c02:
    mov.l @r15+,r3
    .org 0x21c04-ORIGIN
L_00021c04:
    rts
    .org 0x21c06-ORIGIN
L_00021c06:
    mov.l @r15+,r2
    .org 0x21c08-ORIGIN
L_00021c08:
    mov.l r4,@-r15
    .org 0x21c0a-ORIGIN
L_00021c0a:
    extu.w r1,r4
    .org 0x21c0c-ORIGIN
L_00021c0c:
    shll8 r0
    .org 0x21c0e-ORIGIN
L_00021c0e:
    shlr16 r1
    .org 0x21c10-ORIGIN
L_00021c10:
    div1 r0,r1
    .org 0x21c12-ORIGIN
L_00021c12:
    div1 r0,r1
    .org 0x21c14-ORIGIN
L_00021c14:
    div1 r0,r1
    .org 0x21c16-ORIGIN
L_00021c16:
    div1 r0,r1
    .org 0x21c18-ORIGIN
L_00021c18:
    div1 r0,r1
    .org 0x21c1a-ORIGIN
L_00021c1a:
    div1 r0,r1
    .org 0x21c1c-ORIGIN
L_00021c1c:
    div1 r0,r1
    .org 0x21c1e-ORIGIN
L_00021c1e:
    div1 r0,r1
    .org 0x21c20-ORIGIN
L_00021c20:
    div1 r0,r1
    .org 0x21c22-ORIGIN
L_00021c22:
    div1 r0,r1
    .org 0x21c24-ORIGIN
L_00021c24:
    div1 r0,r1
    .org 0x21c26-ORIGIN
L_00021c26:
    div1 r0,r1
    .org 0x21c28-ORIGIN
L_00021c28:
    div1 r0,r1
    .org 0x21c2a-ORIGIN
L_00021c2a:
    div1 r0,r1
    .org 0x21c2c-ORIGIN
L_00021c2c:
    div1 r0,r1
    .org 0x21c2e-ORIGIN
L_00021c2e:
    div1 r0,r1
    .org 0x21c30-ORIGIN
L_00021c30:
    extu.w r1,r2
    .org 0x21c32-ORIGIN
L_00021c32:
    xor r2,r1
    .org 0x21c34-ORIGIN
L_00021c34:
    addc r2,r2
    .org 0x21c36-ORIGIN
L_00021c36:
    shll16 r2
    .org 0x21c38-ORIGIN
L_00021c38:
    add r4,r1
    .org 0x21c3a-ORIGIN
L_00021c3a:
    div1 r0,r1
    .org 0x21c3c-ORIGIN
L_00021c3c:
    div1 r0,r1
    .org 0x21c3e-ORIGIN
L_00021c3e:
    div1 r0,r1
    .org 0x21c40-ORIGIN
L_00021c40:
    div1 r0,r1
    .org 0x21c42-ORIGIN
L_00021c42:
    div1 r0,r1
    .org 0x21c44-ORIGIN
L_00021c44:
    div1 r0,r1
    .org 0x21c46-ORIGIN
L_00021c46:
    div1 r0,r1
    .org 0x21c48-ORIGIN
L_00021c48:
    div1 r0,r1
    .org 0x21c4a-ORIGIN
L_00021c4a:
    div1 r0,r1
    .org 0x21c4c-ORIGIN
L_00021c4c:
    div1 r0,r1
    .org 0x21c4e-ORIGIN
L_00021c4e:
    div1 r0,r1
    .org 0x21c50-ORIGIN
L_00021c50:
    div1 r0,r1
    .org 0x21c52-ORIGIN
L_00021c52:
    div1 r0,r1
    .org 0x21c54-ORIGIN
L_00021c54:
    div1 r0,r1
    .org 0x21c56-ORIGIN
L_00021c56:
    div1 r0,r1
    .org 0x21c58-ORIGIN
L_00021c58:
    div1 r0,r1
    .org 0x21c5a-ORIGIN
L_00021c5a:
    rotcl r1
    .org 0x21c5c-ORIGIN
L_00021c5c:
    extu.w r1,r0
    .org 0x21c5e-ORIGIN
L_00021c5e:
    add r2,r0
    .org 0x21c60-ORIGIN
L_00021c60:
    rotcr r3
    .org 0x21c62-ORIGIN
L_00021c62:
    bf L_00021c68
    .org 0x21c64-ORIGIN
L_00021c64:
    not r0,r0
    .org 0x21c66-ORIGIN
L_00021c66:
    add #0x1,r0
    .org 0x21c68-ORIGIN
L_00021c68:
    mov.l @r15+,r4
    .org 0x21c6a-ORIGIN
L_00021c6a:
    mov.l @r15+,r3
    .org 0x21c6c-ORIGIN
L_00021c6c:
    rts
    .org 0x21c6e-ORIGIN
L_00021c6e:
    mov.l @r15+,r2
    .org 0x21c70-ORIGIN
L_00021c70:
    mov.l L_00021cd8,r1
    .org 0x21c72-ORIGIN
L_00021c72:
    mov.l L_00021cdc,r2
    .org 0x21c74-ORIGIN
L_00021c74:
    mov.l r2,@r1
    .org 0x21c76-ORIGIN
L_00021c76:
    mov #0x0,r0
    .org 0x21c78-ORIGIN
L_00021c78:
    rts
    .org 0x21c7a-ORIGIN
L_00021c7a:
    mov.l @r15+,r2
    .org 0x21c7c-ORIGIN
L_00021c7c:
    div0u
    .org 0x21c7e-ORIGIN
L_00021c7e:
    extu.w r1,r2
    .org 0x21c80-ORIGIN
L_00021c80:
    shll16 r2
    .org 0x21c82-ORIGIN
L_00021c82:
    shlr16 r1
    .org 0x21c84-ORIGIN
L_00021c84:
    rotcl r2
    .org 0x21c86-ORIGIN
L_00021c86:
    div1 r0,r1
    .org 0x21c88-ORIGIN
L_00021c88:
    rotcl r2
    .org 0x21c8a-ORIGIN
L_00021c8a:
    div1 r0,r1
    .org 0x21c8c-ORIGIN
L_00021c8c:
    rotcl r2
    .org 0x21c8e-ORIGIN
L_00021c8e:
    div1 r0,r1
    .org 0x21c90-ORIGIN
L_00021c90:
    rotcl r2
    .org 0x21c92-ORIGIN
L_00021c92:
    div1 r0,r1
    .org 0x21c94-ORIGIN
L_00021c94:
    rotcl r2
    .org 0x21c96-ORIGIN
L_00021c96:
    div1 r0,r1
    .org 0x21c98-ORIGIN
L_00021c98:
    rotcl r2
    .org 0x21c9a-ORIGIN
L_00021c9a:
    div1 r0,r1
    .org 0x21c9c-ORIGIN
L_00021c9c:
    rotcl r2
    .org 0x21c9e-ORIGIN
L_00021c9e:
    div1 r0,r1
    .org 0x21ca0-ORIGIN
L_00021ca0:
    rotcl r2
    .org 0x21ca2-ORIGIN
L_00021ca2:
    div1 r0,r1
    .org 0x21ca4-ORIGIN
L_00021ca4:
    rotcl r2
    .org 0x21ca6-ORIGIN
L_00021ca6:
    div1 r0,r1
    .org 0x21ca8-ORIGIN
L_00021ca8:
    rotcl r2
    .org 0x21caa-ORIGIN
L_00021caa:
    div1 r0,r1
    .org 0x21cac-ORIGIN
L_00021cac:
    rotcl r2
    .org 0x21cae-ORIGIN
L_00021cae:
    div1 r0,r1
    .org 0x21cb0-ORIGIN
L_00021cb0:
    rotcl r2
    .org 0x21cb2-ORIGIN
L_00021cb2:
    div1 r0,r1
    .org 0x21cb4-ORIGIN
L_00021cb4:
    rotcl r2
    .org 0x21cb6-ORIGIN
L_00021cb6:
    div1 r0,r1
    .org 0x21cb8-ORIGIN
L_00021cb8:
    rotcl r2
    .org 0x21cba-ORIGIN
L_00021cba:
    div1 r0,r1
    .org 0x21cbc-ORIGIN
L_00021cbc:
    rotcl r2
    .org 0x21cbe-ORIGIN
L_00021cbe:
    div1 r0,r1
    .org 0x21cc0-ORIGIN
L_00021cc0:
    rotcl r2
    .org 0x21cc2-ORIGIN
L_00021cc2:
    div1 r0,r1
    .org 0x21cc4-ORIGIN
L_00021cc4:
    rotcl r2
    .org 0x21cc6-ORIGIN
L_00021cc6:
    mov r2,r0
    .org 0x21cc8-ORIGIN
L_00021cc8:
    rotcr r3
    .org 0x21cca-ORIGIN
L_00021cca:
    bf L_00021cd0
    .org 0x21ccc-ORIGIN
L_00021ccc:
    not r0,r0
    .org 0x21cce-ORIGIN
L_00021cce:
    add #0x1,r0
    .org 0x21cd0-ORIGIN
L_00021cd0:
    mov.l @r15+,r3
    .org 0x21cd2-ORIGIN
L_00021cd2:
    rts
    .org 0x21cd4-ORIGIN
L_00021cd4:
    mov.l @r15+,r2
    .org 0x21cd8-ORIGIN
L_00021cd8:
    .long 0xffff9818
    .org 0x21cdc-ORIGIN
L_00021cdc:
    .long 0x0000044e
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
    .org 0x26270-ORIGIN
L_00026270:
    sts.l pr,@-r15
    .org 0x26272-ORIGIN
L_00026272:
    mov.l r4,@-r15
    .org 0x26274-ORIGIN
L_00026274:
    extu.w r7,r7
    .org 0x26276-ORIGIN
L_00026276:
    mov r5,r0
    .org 0x26278-ORIGIN
L_00026278:
    mov r7,r5
    .org 0x2627a-ORIGIN
L_0002627a:
    mov.l L_000262a4,r7
    .org 0x2627c-ORIGIN
L_0002627c:
    jsr @r7
    .org 0x2627e-ORIGIN
L_0002627e:
    mov #0xe,r4
    .org 0x26280-ORIGIN
L_00026280:
    mov.l r4,@-r15
    .org 0x26282-ORIGIN
L_00026282:
    mov.l r5,@-r15
    .org 0x26284-ORIGIN
L_00026284:
    mov r6,r0
    .org 0x26286-ORIGIN
L_00026286:
    mov.l @(0x10,r15),r5
    .org 0x26288-ORIGIN
L_00026288:
    extu.w r5,r5
    .org 0x2628a-ORIGIN
L_0002628a:
    jsr @r7
    .org 0x2628c-ORIGIN
L_0002628c:
    mov #0xe,r4
    .org 0x2628e-ORIGIN
L_0002628e:
    mov.l @r15+,r1
    .org 0x26290-ORIGIN
L_00026290:
    mov.l @r15+,r0
    .org 0x26292-ORIGIN
L_00026292:
    mov r4,r2
    .org 0x26294-ORIGIN
L_00026294:
    mov r5,r3
    .org 0x26296-ORIGIN
L_00026296:
    mov.l @r15+,r4
    .org 0x26298-ORIGIN
L_00026298:
    lds.l @r15+,pr
    .org 0x2629a-ORIGIN
L_0002629a:
    mov.l L_000262a0,r7
    .org 0x2629c-ORIGIN
L_0002629c:
    jmp @r7
    .org 0x2629e-ORIGIN
L_0002629e:
    mov #0x8,r5
    .org 0x262a0-ORIGIN
L_000262a0:
    .long 0x00026848
    .org 0x262a4-ORIGIN
L_000262a4:
    .long 0x00026984
    .org 0x26474-ORIGIN
L_00026474:
    sts.l pr,@-r15
    .org 0x26476-ORIGIN
L_00026476:
    mov.l r4,@-r15
    .org 0x26478-ORIGIN
L_00026478:
    mov r5,r0
    .org 0x2647a-ORIGIN
L_0002647a:
    extu.b r6,r5
    .org 0x2647c-ORIGIN
L_0002647c:
    mov.l L_0002649c,r7
    .org 0x2647e-ORIGIN
L_0002647e:
    jsr @r7
    .org 0x26480-ORIGIN
L_00026480:
    mov #0x7,r4
    .org 0x26482-ORIGIN
L_00026482:
    mov.l @r15+,r6
    .org 0x26484-ORIGIN
L_00026484:
    add r4,r6
    .org 0x26486-ORIGIN
L_00026486:
    mov.b @(0x1,r6),r0
    .org 0x26488-ORIGIN
L_00026488:
    extu.b r0,r2
    .org 0x2648a-ORIGIN
L_0002648a:
    mov r5,r3
    .org 0x2648c-ORIGIN
L_0002648c:
    mov.b @r6,r1
    .org 0x2648e-ORIGIN
L_0002648e:
    lds.l @r15+,pr
    .org 0x26490-ORIGIN
L_00026490:
    mov.l L_00026498,r6
    .org 0x26492-ORIGIN
L_00026492:
    jmp @r6
    .org 0x26494-ORIGIN
L_00026494:
    extu.b r1,r0
    .org 0x26498-ORIGIN
L_00026498:
    .long 0x00026740
    .org 0x2649c-ORIGIN
L_0002649c:
    .long 0x00026944
    .org 0x264f8-ORIGIN
L_000264f8:
    sts.l pr,@-r15
    .org 0x264fa-ORIGIN
L_000264fa:
    mov.l r4,@-r15
    .org 0x264fc-ORIGIN
L_000264fc:
    mov r5,r0
    .org 0x264fe-ORIGIN
L_000264fe:
    extu.w r6,r5
    .org 0x26500-ORIGIN
L_00026500:
    mov.l L_00026520,r7
    .org 0x26502-ORIGIN
L_00026502:
    jsr @r7
    .org 0x26504-ORIGIN
L_00026504:
    mov #0x1e,r4
    .org 0x26506-ORIGIN
L_00026506:
    mov.l @r15+,r6
    .org 0x26508-ORIGIN
L_00026508:
    add r4,r6
    .org 0x2650a-ORIGIN
L_0002650a:
    mov.w @(0x2,r6),r0
    .org 0x2650c-ORIGIN
L_0002650c:
    extu.w r0,r2
    .org 0x2650e-ORIGIN
L_0002650e:
    mov r5,r3
    .org 0x26510-ORIGIN
L_00026510:
    mov.w @r6,r1
    .org 0x26512-ORIGIN
L_00026512:
    lds.l @r15+,pr
    .org 0x26514-ORIGIN
L_00026514:
    mov.l L_0002651c,r6
    .org 0x26516-ORIGIN
L_00026516:
    jmp @r6
    .org 0x26518-ORIGIN
L_00026518:
    extu.w r1,r0
    .org 0x2651c-ORIGIN
L_0002651c:
    .long 0x00026740
    .org 0x26520-ORIGIN
L_00026520:
    .long 0x00026984
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
    .org 0x26848-ORIGIN
L_00026848:
    mov.l r8,@-r15
    .org 0x2684a-ORIGIN
L_0002684a:
    sts.l pr,@-r15
    .org 0x2684c-ORIGIN
L_0002684c:
    sts macl,r7
    .org 0x2684e-ORIGIN
L_0002684e:
    mulu.w r5,r0
    .org 0x26850-ORIGIN
L_00026850:
    add r2,r4
    .org 0x26852-ORIGIN
L_00026852:
    sts macl,r0
    .org 0x26854-ORIGIN
L_00026854:
    lds r7,macl
    .org 0x26856-ORIGIN
L_00026856:
    shll r5
    .org 0x26858-ORIGIN
L_00026858:
    add r0,r4
    .org 0x2685a-ORIGIN
L_0002685a:
    add r4,r5
    .org 0x2685c-ORIGIN
L_0002685c:
    mov r1,r8
    .org 0x2685e-ORIGIN
L_0002685e:
    mov.l L_000268a0,r7
    .org 0x26860-ORIGIN
L_00026860:
    tst r3,r3
    .org 0x26862-ORIGIN
L_00026862:
    bt L_0002688a
    .org 0x26864-ORIGIN
L_00026864:
    mov.w @r4,r1
    .org 0x26866-ORIGIN
L_00026866:
    mov.w @(0x2,r4),r0
    .org 0x26868-ORIGIN
L_00026868:
    extu.w r0,r2
    .org 0x2686a-ORIGIN
L_0002686a:
    jsr @r7
    .org 0x2686c-ORIGIN
L_0002686c:
    extu.w r1,r0
    .org 0x2686e-ORIGIN
L_0002686e:
    tst r8,r8
    .org 0x26870-ORIGIN
L_00026870:
    bt L_0002689a
    .org 0x26872-ORIGIN
L_00026872:
    mov.l r0,@-r15
    .org 0x26874-ORIGIN
L_00026874:
    mov.w @r5,r1
    .org 0x26876-ORIGIN
L_00026876:
    mov.w @(0x2,r5),r0
    .org 0x26878-ORIGIN
L_00026878:
    extu.w r0,r2
    .org 0x2687a-ORIGIN
L_0002687a:
    jsr @r7
    .org 0x2687c-ORIGIN
L_0002687c:
    extu.w r1,r0
    .org 0x2687e-ORIGIN
L_0002687e:
    mov r0,r2
    .org 0x26880-ORIGIN
L_00026880:
    mov.l @r15+,r0
    .org 0x26882-ORIGIN
L_00026882:
    jsr @r7
    .org 0x26884-ORIGIN
L_00026884:
    mov r8,r3
    .org 0x26886-ORIGIN
L_00026886:
    bra L_0002689a
    .org 0x26888-ORIGIN
L_00026888:
    nop
    .org 0x2688a-ORIGIN
L_0002688a:
    tst r8,r8
    .org 0x2688c-ORIGIN
L_0002688c:
    bt/s L_0002689a
    .org 0x2688e-ORIGIN
L_0002688e:
    mov.w @r4,r0
    .org 0x26890-ORIGIN
L_00026890:
    mov.w @r5,r2
    .org 0x26892-ORIGIN
L_00026892:
    extu.w r0,r0
    .org 0x26894-ORIGIN
L_00026894:
    extu.w r2,r2
    .org 0x26896-ORIGIN
L_00026896:
    jsr @r7
    .org 0x26898-ORIGIN
L_00026898:
    mov r8,r3
    .org 0x2689a-ORIGIN
L_0002689a:
    lds.l @r15+,pr
    .org 0x2689c-ORIGIN
L_0002689c:
    rts
    .org 0x2689e-ORIGIN
L_0002689e:
    mov.l @r15+,r8
    .org 0x268a0-ORIGIN
L_000268a0:
    .long 0x00026740
    .org 0x26944-ORIGIN
L_00026944:
    mov r4,r3
    .org 0x26946-ORIGIN
L_00026946:
    mov.b @(r0,r4),r1
    .org 0x26948-ORIGIN
L_00026948:
    extu.b r1,r1
    .org 0x2694a-ORIGIN
L_0002694a:
    cmp/eq r1,r5
    .org 0x2694c-ORIGIN
L_0002694c:
    bt L_0002697c
    .org 0x2694e-ORIGIN
L_0002694e:
    cmp/hi r1,r5
    .org 0x26950-ORIGIN
L_00026950:
    bf L_00026974
    .org 0x26952-ORIGIN
L_00026952:
    cmp/eq r4,r3
    .org 0x26954-ORIGIN
L_00026954:
    bt L_0002697c
    .org 0x26956-ORIGIN
L_00026956:
    sub r1,r5
    .org 0x26958-ORIGIN
L_00026958:
    shll16 r5
    .org 0x2695a-ORIGIN
L_0002695a:
    add r4,r0
    .org 0x2695c-ORIGIN
L_0002695c:
    mov.b @r0,r1
    .org 0x2695e-ORIGIN
L_0002695e:
    mov.b @(0x1,r0),r0
    .org 0x26960-ORIGIN
L_00026960:
    extu.b r1,r1
    .org 0x26962-ORIGIN
L_00026962:
    extu.b r0,r0
    .org 0x26964-ORIGIN
L_00026964:
    sts.l pr,@-r15
    .org 0x26966-ORIGIN
L_00026966:
    mov.l L_00026980,r2
    .org 0x26968-ORIGIN
L_00026968:
    sub r1,r0
    .org 0x2696a-ORIGIN
L_0002696a:
    jsr @r2
    .org 0x2696c-ORIGIN
L_0002696c:
    mov r5,r1
    .org 0x2696e-ORIGIN
L_0002696e:
    lds.l @r15+,pr
    .org 0x26970-ORIGIN
L_00026970:
    rts
    .org 0x26972-ORIGIN
L_00026972:
    mov r0,r5
    .org 0x26974-ORIGIN
L_00026974:
    add #-0x1,r4
    .org 0x26976-ORIGIN
L_00026976:
    cmp/pz r4
    .org 0x26978-ORIGIN
L_00026978:
    bt L_00026946
    .org 0x2697a-ORIGIN
L_0002697a:
    mov #0x0,r4
    .org 0x2697c-ORIGIN
L_0002697c:
    rts
    .org 0x2697e-ORIGIN
L_0002697e:
    mov #0x0,r5
    .org 0x26980-ORIGIN
L_00026980:
    .long 0x00026c78
    .org 0x26984-ORIGIN
L_00026984:
    mov r4,r3
    .org 0x26986-ORIGIN
L_00026986:
    mov.w @(r0,r4),r1
    .org 0x26988-ORIGIN
L_00026988:
    extu.w r1,r1
    .org 0x2698a-ORIGIN
L_0002698a:
    cmp/eq r1,r5
    .org 0x2698c-ORIGIN
L_0002698c:
    bt L_000269bc
    .org 0x2698e-ORIGIN
L_0002698e:
    cmp/hi r1,r5
    .org 0x26990-ORIGIN
L_00026990:
    bf L_000269b4
    .org 0x26992-ORIGIN
L_00026992:
    cmp/eq r4,r3
    .org 0x26994-ORIGIN
L_00026994:
    bt L_000269bc
    .org 0x26996-ORIGIN
L_00026996:
    sub r1,r5
    .org 0x26998-ORIGIN
L_00026998:
    shll16 r5
    .org 0x2699a-ORIGIN
L_0002699a:
    add r4,r0
    .org 0x2699c-ORIGIN
L_0002699c:
    mov.w @r0,r1
    .org 0x2699e-ORIGIN
L_0002699e:
    mov.w @(0x2,r0),r0
    .org 0x269a0-ORIGIN
L_000269a0:
    extu.w r1,r1
    .org 0x269a2-ORIGIN
L_000269a2:
    extu.w r0,r0
    .org 0x269a4-ORIGIN
L_000269a4:
    sts.l pr,@-r15
    .org 0x269a6-ORIGIN
L_000269a6:
    mov.l L_000269c0,r2
    .org 0x269a8-ORIGIN
L_000269a8:
    sub r1,r0
    .org 0x269aa-ORIGIN
L_000269aa:
    jsr @r2
    .org 0x269ac-ORIGIN
L_000269ac:
    mov r5,r1
    .org 0x269ae-ORIGIN
L_000269ae:
    lds.l @r15+,pr
    .org 0x269b0-ORIGIN
L_000269b0:
    rts
    .org 0x269b2-ORIGIN
L_000269b2:
    mov r0,r5
    .org 0x269b4-ORIGIN
L_000269b4:
    add #-0x2,r4
    .org 0x269b6-ORIGIN
L_000269b6:
    cmp/pz r4
    .org 0x269b8-ORIGIN
L_000269b8:
    bt L_00026986
    .org 0x269ba-ORIGIN
L_000269ba:
    mov #0x0,r4
    .org 0x269bc-ORIGIN
L_000269bc:
    rts
    .org 0x269be-ORIGIN
L_000269be:
    mov #0x0,r5
    .org 0x269c0-ORIGIN
L_000269c0:
    .long 0x00026c78
    .org 0x26c78-ORIGIN
L_00026c78:
    tst r0,r0
    .org 0x26c7a-ORIGIN
L_00026c7a:
    bt L_00026d0a
    .org 0x26c7c-ORIGIN
L_00026c7c:
    mov.l r2,@-r15
    .org 0x26c7e-ORIGIN
L_00026c7e:
    mov #0x0,r2
    .org 0x26c80-ORIGIN
L_00026c80:
    div0u
    .org 0x26c82-ORIGIN
L_00026c82:
    rotcl r1
    .org 0x26c84-ORIGIN
L_00026c84:
    div1 r0,r2
    .org 0x26c86-ORIGIN
L_00026c86:
    rotcl r1
    .org 0x26c88-ORIGIN
L_00026c88:
    div1 r0,r2
    .org 0x26c8a-ORIGIN
L_00026c8a:
    rotcl r1
    .org 0x26c8c-ORIGIN
L_00026c8c:
    div1 r0,r2
    .org 0x26c8e-ORIGIN
L_00026c8e:
    rotcl r1
    .org 0x26c90-ORIGIN
L_00026c90:
    div1 r0,r2
    .org 0x26c92-ORIGIN
L_00026c92:
    rotcl r1
    .org 0x26c94-ORIGIN
L_00026c94:
    div1 r0,r2
    .org 0x26c96-ORIGIN
L_00026c96:
    rotcl r1
    .org 0x26c98-ORIGIN
L_00026c98:
    div1 r0,r2
    .org 0x26c9a-ORIGIN
L_00026c9a:
    rotcl r1
    .org 0x26c9c-ORIGIN
L_00026c9c:
    div1 r0,r2
    .org 0x26c9e-ORIGIN
L_00026c9e:
    rotcl r1
    .org 0x26ca0-ORIGIN
L_00026ca0:
    div1 r0,r2
    .org 0x26ca2-ORIGIN
L_00026ca2:
    rotcl r1
    .org 0x26ca4-ORIGIN
L_00026ca4:
    div1 r0,r2
    .org 0x26ca6-ORIGIN
L_00026ca6:
    rotcl r1
    .org 0x26ca8-ORIGIN
L_00026ca8:
    div1 r0,r2
    .org 0x26caa-ORIGIN
L_00026caa:
    rotcl r1
    .org 0x26cac-ORIGIN
L_00026cac:
    div1 r0,r2
    .org 0x26cae-ORIGIN
L_00026cae:
    rotcl r1
    .org 0x26cb0-ORIGIN
L_00026cb0:
    div1 r0,r2
    .org 0x26cb2-ORIGIN
L_00026cb2:
    rotcl r1
    .org 0x26cb4-ORIGIN
L_00026cb4:
    div1 r0,r2
    .org 0x26cb6-ORIGIN
L_00026cb6:
    rotcl r1
    .org 0x26cb8-ORIGIN
L_00026cb8:
    div1 r0,r2
    .org 0x26cba-ORIGIN
L_00026cba:
    rotcl r1
    .org 0x26cbc-ORIGIN
L_00026cbc:
    div1 r0,r2
    .org 0x26cbe-ORIGIN
L_00026cbe:
    rotcl r1
    .org 0x26cc0-ORIGIN
L_00026cc0:
    div1 r0,r2
    .org 0x26cc2-ORIGIN
L_00026cc2:
    rotcl r1
    .org 0x26cc4-ORIGIN
L_00026cc4:
    div1 r0,r2
    .org 0x26cc6-ORIGIN
L_00026cc6:
    rotcl r1
    .org 0x26cc8-ORIGIN
L_00026cc8:
    div1 r0,r2
    .org 0x26cca-ORIGIN
L_00026cca:
    rotcl r1
    .org 0x26ccc-ORIGIN
L_00026ccc:
    div1 r0,r2
    .org 0x26cce-ORIGIN
L_00026cce:
    rotcl r1
    .org 0x26cd0-ORIGIN
L_00026cd0:
    div1 r0,r2
    .org 0x26cd2-ORIGIN
L_00026cd2:
    rotcl r1
    .org 0x26cd4-ORIGIN
L_00026cd4:
    div1 r0,r2
    .org 0x26cd6-ORIGIN
L_00026cd6:
    rotcl r1
    .org 0x26cd8-ORIGIN
L_00026cd8:
    div1 r0,r2
    .org 0x26cda-ORIGIN
L_00026cda:
    rotcl r1
    .org 0x26cdc-ORIGIN
L_00026cdc:
    div1 r0,r2
    .org 0x26cde-ORIGIN
L_00026cde:
    rotcl r1
    .org 0x26ce0-ORIGIN
L_00026ce0:
    div1 r0,r2
    .org 0x26ce2-ORIGIN
L_00026ce2:
    rotcl r1
    .org 0x26ce4-ORIGIN
L_00026ce4:
    div1 r0,r2
    .org 0x26ce6-ORIGIN
L_00026ce6:
    rotcl r1
    .org 0x26ce8-ORIGIN
L_00026ce8:
    div1 r0,r2
    .org 0x26cea-ORIGIN
L_00026cea:
    rotcl r1
    .org 0x26cec-ORIGIN
L_00026cec:
    div1 r0,r2
    .org 0x26cee-ORIGIN
L_00026cee:
    rotcl r1
    .org 0x26cf0-ORIGIN
L_00026cf0:
    div1 r0,r2
    .org 0x26cf2-ORIGIN
L_00026cf2:
    rotcl r1
    .org 0x26cf4-ORIGIN
L_00026cf4:
    div1 r0,r2
    .org 0x26cf6-ORIGIN
L_00026cf6:
    rotcl r1
    .org 0x26cf8-ORIGIN
L_00026cf8:
    div1 r0,r2
    .org 0x26cfa-ORIGIN
L_00026cfa:
    rotcl r1
    .org 0x26cfc-ORIGIN
L_00026cfc:
    div1 r0,r2
    .org 0x26cfe-ORIGIN
L_00026cfe:
    rotcl r1
    .org 0x26d00-ORIGIN
L_00026d00:
    div1 r0,r2
    .org 0x26d02-ORIGIN
L_00026d02:
    rotcl r1
    .org 0x26d04-ORIGIN
L_00026d04:
    mov.l @r15+,r2
    .org 0x26d06-ORIGIN
L_00026d06:
    rts
    .org 0x26d08-ORIGIN
L_00026d08:
    mov r1,r0
    .org 0x26d0a-ORIGIN
L_00026d0a:
    rts
    .org 0x26d0c-ORIGIN
L_00026d0c:
    mov #0x0,r0
    .org 0xc0d90-ORIGIN
L_000c0d90:
    mov.l r8,@-r15
    .org 0xc0d92-ORIGIN
L_000c0d92:
    mov.l r9,@-r15
    .org 0xc0d94-ORIGIN
L_000c0d94:
    mov.l r10,@-r15
    .org 0xc0d96-ORIGIN
L_000c0d96:
    mov.l r11,@-r15
    .org 0xc0d98-ORIGIN
L_000c0d98:
    mov.l r12,@-r15
    .org 0xc0d9a-ORIGIN
L_000c0d9a:
    mov.l r13,@-r15
    .org 0xc0d9c-ORIGIN
L_000c0d9c:
    mov.l r14,@-r15
    .org 0xc0d9e-ORIGIN
L_000c0d9e:
    sts.l pr,@-r15
    .org 0xc0da0-ORIGIN
L_000c0da0:
    sts.l macl,@-r15
    .org 0xc0da2-ORIGIN
L_000c0da2:
    stc.l gbr,@-r15
    .org 0xc0da4-ORIGIN
L_000c0da4:
    mov.l L_000c0ec0,r0
    .org 0xc0da6-ORIGIN
L_000c0da6:
    ldc r0,gbr
    .org 0xc0da8-ORIGIN
L_000c0da8:
    add #-0x10,r15
    .org 0xc0daa-ORIGIN
L_000c0daa:
    mov.l L_000c0ec4,r8
    .org 0xc0dac-ORIGIN
L_000c0dac:
    extu.b r4,r11
    .org 0xc0dae-ORIGIN
L_000c0dae:
    mov r11,r0
    .org 0xc0db0-ORIGIN
L_000c0db0:
    tst r11,r11
    .org 0xc0db2-ORIGIN
L_000c0db2:
    mov r8,r2
    .org 0xc0db4-ORIGIN
L_000c0db4:
    add #0x32,r2
    .org 0xc0db6-ORIGIN
L_000c0db6:
    mov.b @(r0,r2),r6
    .org 0xc0db8-ORIGIN
L_000c0db8:
    mov r11,r10
    .org 0xc0dba-ORIGIN
L_000c0dba:
    mov.l L_000c0ec8,r2
    .org 0xc0dbc-ORIGIN
L_000c0dbc:
    shll2 r10
    .org 0xc0dbe-ORIGIN
L_000c0dbe:
    extu.b r6,r14
    .org 0xc0dc0-ORIGIN
L_000c0dc0:
    mov.l L_000c0ecc,r4
    .org 0xc0dc2-ORIGIN
L_000c0dc2:
    add #0x32,r2
    .org 0xc0dc4-ORIGIN
L_000c0dc4:
    mov.b @(r0,r2),r6
    .org 0xc0dc6-ORIGIN
L_000c0dc6:
    add #-0x80,r14
    .org 0xc0dc8-ORIGIN
L_000c0dc8:
    extu.b r6,r12
    .org 0xc0dca-ORIGIN
L_000c0dca:
    bf/s L_000c0dd0
    .org 0xc0dcc-ORIGIN
L_000c0dcc:
    add #-0x80,r12
    .org 0xc0dce-ORIGIN
L_000c0dce:
    mov.l L_000c0ed0,r4
    .org 0xc0dd0-ORIGIN
L_000c0dd0:
    mov.l L_000c0ed4,r9
    .org 0xc0dd2-ORIGIN
L_000c0dd2:
    mov #0x12,r0
    .org 0xc0dd4-ORIGIN
L_000c0dd4:
    mov.l L_000c0ed8,r5
    .org 0xc0dd6-ORIGIN
L_000c0dd6:
    mov.b @(r0,r9),r2
    .org 0xc0dd8-ORIGIN
L_000c0dd8:
    mov.l L_000c0edc,r13
    .org 0xc0dda-ORIGIN
L_000c0dda:
    mov.l L_000c0ec0,r9
    .org 0xc0ddc-ORIGIN
L_000c0ddc:
    jsr @r13
    .org 0xc0dde-ORIGIN
L_000c0dde:
    extu.b r2,r6
    .org 0xc0de0-ORIGIN
L_000c0de0:
    mov.w L_000c0e46,r5
    .org 0xc0de2-ORIGIN
L_000c0de2:
    mov r9,r2
    .org 0xc0de4-ORIGIN
L_000c0de4:
    mov r0,r6
    .org 0xc0de6-ORIGIN
L_000c0de6:
    mov r11,r0
    .org 0xc0de8-ORIGIN
L_000c0de8:
    add r5,r2
    .org 0xc0dea-ORIGIN
L_000c0dea:
    mov.l L_000c0ee0,r7
    .org 0xc0dec-ORIGIN
L_000c0dec:
    mov.b r6,@(r0,r2)
    .org 0xc0dee-ORIGIN
L_000c0dee:
    extu.b r6,r6
    .org 0xc0df0-ORIGIN
L_000c0df0:
    mul.l r6,r14
    .org 0xc0df2-ORIGIN
L_000c0df2:
    mov #0x64,r0
    .org 0xc0df4-ORIGIN
L_000c0df4:
    sts macl,r1
    .org 0xc0df6-ORIGIN
L_000c0df6:
    jsr @r7
    .org 0xc0df8-ORIGIN
L_000c0df8:
    shll8 r1
    .org 0xc0dfa-ORIGIN
L_000c0dfa:
    mov.l L_000c0ee4,r6
    .org 0xc0dfc-ORIGIN
L_000c0dfc:
    add r6,r0
    .org 0xc0dfe-ORIGIN
L_000c0dfe:
    cmp/pz r0
    .org 0xc0e00-ORIGIN
L_000c0e00:
    bt/s L_000c0e06
    .org 0xc0e02-ORIGIN
L_000c0e02:
    mov r0,r6
    .org 0xc0e04-ORIGIN
L_000c0e04:
    mov #0x0,r6
    .org 0xc0e06-ORIGIN
L_000c0e06:
    mov #-0x1,r2
    .org 0xc0e08-ORIGIN
L_000c0e08:
    extu.w r2,r2
    .org 0xc0e0a-ORIGIN
L_000c0e0a:
    cmp/gt r2,r6
    .org 0xc0e0c-ORIGIN
L_000c0e0c:
    bf L_000c0e10
    .org 0xc0e0e-ORIGIN
L_000c0e0e:
    mov #-0x1,r6
    .org 0xc0e10-ORIGIN
L_000c0e10:
    mov r11,r2
    .org 0xc0e12-ORIGIN
L_000c0e12:
    shll r2
    .org 0xc0e14-ORIGIN
L_000c0e14:
    mov.w L_000c0e48,r5
    .org 0xc0e16-ORIGIN
L_000c0e16:
    mov.l r2,@(0x4,r15)
    .org 0xc0e18-ORIGIN
L_000c0e18:
    mov r9,r2
    .org 0xc0e1a-ORIGIN
L_000c0e1a:
    add r5,r2
    .org 0xc0e1c-ORIGIN
L_000c0e1c:
    mov.l @(0x4,r15),r5
    .org 0xc0e1e-ORIGIN
L_000c0e1e:
    mov r5,r0
    .org 0xc0e20-ORIGIN
L_000c0e20:
    mov.w r6,@(r0,r2)
    .org 0xc0e22-ORIGIN
L_000c0e22:
    mov.l L_000c0ec0,r6
    .org 0xc0e24-ORIGIN
L_000c0e24:
    mov.w L_000c0e4a,r0
    .org 0xc0e26-ORIGIN
L_000c0e26:
    mov.b @(r0,r6),r2
    .org 0xc0e28-ORIGIN
L_000c0e28:
    mov r11,r6
    .org 0xc0e2a-ORIGIN
L_000c0e2a:
    add #0x1,r6
    .org 0xc0e2c-ORIGIN
L_000c0e2c:
    extu.b r2,r2
    .org 0xc0e2e-ORIGIN
L_000c0e2e:
    tst r6,r2
    .org 0xc0e30-ORIGIN
L_000c0e30:
    bt/s L_000c0e4e
    .org 0xc0e32-ORIGIN
L_000c0e32:
    mov.l r6,@(0x8,r15)
    .org 0xc0e34-ORIGIN
L_000c0e34:
    mov.w L_000c0e4c,r6
    .org 0xc0e36-ORIGIN
L_000c0e36:
    mov r9,r2
    .org 0xc0e38-ORIGIN
L_000c0e38:
    add r6,r2
    .org 0xc0e3a-ORIGIN
L_000c0e3a:
    mov #-0x80,r6
    .org 0xc0e3c-ORIGIN
L_000c0e3c:
    extu.b r6,r6
    .org 0xc0e3e-ORIGIN
L_000c0e3e:
    bra L_000c0ea4
    .org 0xc0e40-ORIGIN
L_000c0e40:
    shll16 r6
    .org 0xc0e46-ORIGIN
L_000c0e46:
    .word 0x036a
    .org 0xc0e48-ORIGIN
L_000c0e48:
    .word 0x086c
    .org 0xc0e4a-ORIGIN
L_000c0e4a:
    .word 0x0840
    .org 0xc0e4c-ORIGIN
L_000c0e4c:
    .word 0x0838
    .org 0xc0e4e-ORIGIN
L_000c0e4e:
    mov.l L_000c0ee8,r2
    .org 0xc0e50-ORIGIN
L_000c0e50:
    mov.b @(0x7,r2),r0
    .org 0xc0e52-ORIGIN
L_000c0e52:
    extu.b r0,r6
    .org 0xc0e54-ORIGIN
L_000c0e54:
    cmp/gt r6,r14
    .org 0xc0e56-ORIGIN
L_000c0e56:
    bt L_000c0e5e
    .org 0xc0e58-ORIGIN
L_000c0e58:
    neg r6,r2
    .org 0xc0e5a-ORIGIN
L_000c0e5a:
    cmp/ge r2,r14
    .org 0xc0e5c-ORIGIN
L_000c0e5c:
    bt L_000c0ea8
    .org 0xc0e5e-ORIGIN
L_000c0e5e:
    mov.w L_000c0eba,r6
    .org 0xc0e60-ORIGIN
L_000c0e60:
    mov r9,r2
    .org 0xc0e62-ORIGIN
L_000c0e62:
    mov r10,r0
    .org 0xc0e64-ORIGIN
L_000c0e64:
    tst r11,r11
    .org 0xc0e66-ORIGIN
L_000c0e66:
    add r6,r2
    .org 0xc0e68-ORIGIN
L_000c0e68:
    mov.l @(r0,r2),r6
    .org 0xc0e6a-ORIGIN
L_000c0e6a:
    bf/s L_000c0e74
    .org 0xc0e6c-ORIGIN
L_000c0e6c:
    mov.l r6,@(0xc,r15)
    .org 0xc0e6e-ORIGIN
L_000c0e6e:
    mov.l L_000c0eec,r6
    .org 0xc0e70-ORIGIN
L_000c0e70:
    bra L_000c0e78
    .org 0xc0e72-ORIGIN
L_000c0e72:
    mov.b @r6,r2
    .org 0xc0e74-ORIGIN
L_000c0e74:
    mov.l L_000c0ef0,r6
    .org 0xc0e76-ORIGIN
L_000c0e76:
    mov.b @r6,r2
    .org 0xc0e78-ORIGIN
L_000c0e78:
    extu.b r2,r2
    .org 0xc0e7a-ORIGIN
L_000c0e7a:
    mov.l L_000c0ee0,r7
    .org 0xc0e7c-ORIGIN
L_000c0e7c:
    mul.l r2,r14
    .org 0xc0e7e-ORIGIN
L_000c0e7e:
    mov #0x64,r6
    .org 0xc0e80-ORIGIN
L_000c0e80:
    mov r6,r0
    .org 0xc0e82-ORIGIN
L_000c0e82:
    sts macl,r1
    .org 0xc0e84-ORIGIN
L_000c0e84:
    shll8 r1
    .org 0xc0e86-ORIGIN
L_000c0e86:
    jsr @r7
    .org 0xc0e88-ORIGIN
L_000c0e88:
    shll r1
    .org 0xc0e8a-ORIGIN
L_000c0e8a:
    mov.l @(0xc,r15),r6
    .org 0xc0e8c-ORIGIN
L_000c0e8c:
    add r6,r0
    .org 0xc0e8e-ORIGIN
L_000c0e8e:
    cmp/pz r0
    .org 0xc0e90-ORIGIN
L_000c0e90:
    bt/s L_000c0e96
    .org 0xc0e92-ORIGIN
L_000c0e92:
    mov r0,r2
    .org 0xc0e94-ORIGIN
L_000c0e94:
    mov #0x0,r2
    .org 0xc0e96-ORIGIN
L_000c0e96:
    mov.l L_000c0ef4,r6
    .org 0xc0e98-ORIGIN
L_000c0e98:
    cmp/gt r6,r2
    .org 0xc0e9a-ORIGIN
L_000c0e9a:
    bt L_000c0e9e
    .org 0xc0e9c-ORIGIN
L_000c0e9c:
    mov r2,r6
    .org 0xc0e9e-ORIGIN
L_000c0e9e:
    mov.w L_000c0eba,r5
    .org 0xc0ea0-ORIGIN
L_000c0ea0:
    mov r9,r2
    .org 0xc0ea2-ORIGIN
L_000c0ea2:
    add r5,r2
    .org 0xc0ea4-ORIGIN
L_000c0ea4:
    mov r10,r0
    .org 0xc0ea6-ORIGIN
L_000c0ea6:
    mov.l r6,@(r0,r2)
    .org 0xc0ea8-ORIGIN
L_000c0ea8:
    tst r11,r11
    .org 0xc0eaa-ORIGIN
L_000c0eaa:
    bf L_000c0f00
    .org 0xc0eac-ORIGIN
L_000c0eac:
    mov.l L_000c0ed4,r3
    .org 0xc0eae-ORIGIN
L_000c0eae:
    mov #0x12,r0
    .org 0xc0eb0-ORIGIN
L_000c0eb0:
    mov.l L_000c0ef8,r4
    .org 0xc0eb2-ORIGIN
L_000c0eb2:
    mov.b @(r0,r3),r2
    .org 0xc0eb4-ORIGIN
L_000c0eb4:
    mov.l L_000c0efc,r5
    .org 0xc0eb6-ORIGIN
L_000c0eb6:
    bra L_000c0f0a
    .org 0xc0eb8-ORIGIN
L_000c0eb8:
    nop
    .org 0xc0eba-ORIGIN
L_000c0eba:
    .word 0x0838
    .org 0xc0ec0-ORIGIN
L_000c0ec0:
    .long 0xffff128c
    .org 0xc0ec4-ORIGIN
L_000c0ec4:
    .long 0xffff120e
    .org 0xc0ec8-ORIGIN
L_000c0ec8:
    .long 0xffff124c
    .org 0xc0ecc-ORIGIN
L_000c0ecc:
    .long 0x00012532
    .org 0xc0ed0-ORIGIN
L_000c0ed0:
    .long 0x0001252a
    .org 0xc0ed4-ORIGIN
L_000c0ed4:
    .long 0xffff119c
    .org 0xc0ed8-ORIGIN
L_000c0ed8:
    .long 0x0001302e
    .org 0xc0edc-ORIGIN
L_000c0edc:
    .long 0x00026474
    .org 0xc0ee0-ORIGIN
L_000c0ee0:
    .long 0x00021bbc
    .org 0xc0ee4-ORIGIN
L_000c0ee4:
    .long 0x00008000
    .org 0xc0ee8-ORIGIN
L_000c0ee8:
    .long 0x00008d61
    .org 0xc0eec-ORIGIN
L_000c0eec:
    .long 0x000087b0
    .org 0xc0ef0-ORIGIN
L_000c0ef0:
    .long 0x000087b1
    .org 0xc0ef4-ORIGIN
L_000c0ef4:
    .long 0x00ffffff
    .org 0xc0ef8-ORIGIN
L_000c0ef8:
    .long 0x000123f2
    .org 0xc0efc-ORIGIN
L_000c0efc:
    .long 0x00011beb
    .org 0xc0f00-ORIGIN
L_000c0f00:
    mov.l L_000c1190,r3
    .org 0xc0f02-ORIGIN
L_000c0f02:
    mov #0x12,r0
    .org 0xc0f04-ORIGIN
L_000c0f04:
    mov.l L_000c1194,r4
    .org 0xc0f06-ORIGIN
L_000c0f06:
    mov.b @(r0,r3),r2
    .org 0xc0f08-ORIGIN
L_000c0f08:
    mov.l L_000c1198,r5
    .org 0xc0f0a-ORIGIN
L_000c0f0a:
    jsr @r13
    .org 0xc0f0c-ORIGIN
L_000c0f0c:
    extu.b r2,r6
    .org 0xc0f0e-ORIGIN
L_000c0f0e:
    mov.w L_000c1028,r5
    .org 0xc0f10-ORIGIN
L_000c0f10:
    mov r9,r2
    .org 0xc0f12-ORIGIN
L_000c0f12:
    mov r0,r6
    .org 0xc0f14-ORIGIN
L_000c0f14:
    mov r11,r0
    .org 0xc0f16-ORIGIN
L_000c0f16:
    add r5,r2
    .org 0xc0f18-ORIGIN
L_000c0f18:
    mov.l L_000c119c,r7
    .org 0xc0f1a-ORIGIN
L_000c0f1a:
    mov.b r6,@(r0,r2)
    .org 0xc0f1c-ORIGIN
L_000c0f1c:
    extu.b r6,r6
    .org 0xc0f1e-ORIGIN
L_000c0f1e:
    mov r14,r2
    .org 0xc0f20-ORIGIN
L_000c0f20:
    sub r12,r2
    .org 0xc0f22-ORIGIN
L_000c0f22:
    mul.l r6,r2
    .org 0xc0f24-ORIGIN
L_000c0f24:
    mov #0x64,r6
    .org 0xc0f26-ORIGIN
L_000c0f26:
    mov r6,r0
    .org 0xc0f28-ORIGIN
L_000c0f28:
    jsr @r7
    .org 0xc0f2a-ORIGIN
L_000c0f2a:
    sts macl,r1
    .org 0xc0f2c-ORIGIN
L_000c0f2c:
    mov #-0x80,r6
    .org 0xc0f2e-ORIGIN
L_000c0f2e:
    extu.b r6,r6
    .org 0xc0f30-ORIGIN
L_000c0f30:
    add r6,r0
    .org 0xc0f32-ORIGIN
L_000c0f32:
    cmp/pz r0
    .org 0xc0f34-ORIGIN
L_000c0f34:
    bt/s L_000c0f3a
    .org 0xc0f36-ORIGIN
L_000c0f36:
    mov r0,r6
    .org 0xc0f38-ORIGIN
L_000c0f38:
    mov #0x0,r6
    .org 0xc0f3a-ORIGIN
L_000c0f3a:
    mov #-0x1,r2
    .org 0xc0f3c-ORIGIN
L_000c0f3c:
    extu.b r2,r2
    .org 0xc0f3e-ORIGIN
L_000c0f3e:
    cmp/gt r2,r6
    .org 0xc0f40-ORIGIN
L_000c0f40:
    bt L_000c0f44
    .org 0xc0f42-ORIGIN
L_000c0f42:
    mov r6,r2
    .org 0xc0f44-ORIGIN
L_000c0f44:
    mov.w L_000c102a,r6
    .org 0xc0f46-ORIGIN
L_000c0f46:
    mov r2,r4
    .org 0xc0f48-ORIGIN
L_000c0f48:
    mov r9,r2
    .org 0xc0f4a-ORIGIN
L_000c0f4a:
    mov r11,r0
    .org 0xc0f4c-ORIGIN
L_000c0f4c:
    add r6,r2
    .org 0xc0f4e-ORIGIN
L_000c0f4e:
    mov.b r4,@(r0,r2)
    .org 0xc0f50-ORIGIN
L_000c0f50:
    mov #-0x80,r5
    .org 0xc0f52-ORIGIN
L_000c0f52:
    mov.l L_000c11a0,r2
    .org 0xc0f54-ORIGIN
L_000c0f54:
    extu.b r5,r5
    .org 0xc0f56-ORIGIN
L_000c0f56:
    mov.b @(0xa,r2),r0
    .org 0xc0f58-ORIGIN
L_000c0f58:
    extu.b r0,r6
    .org 0xc0f5a-ORIGIN
L_000c0f5a:
    cmp/gt r6,r14
    .org 0xc0f5c-ORIGIN
L_000c0f5c:
    bt/s L_000c0f66
    .org 0xc0f5e-ORIGIN
L_000c0f5e:
    shll16 r5
    .org 0xc0f60-ORIGIN
L_000c0f60:
    neg r6,r2
    .org 0xc0f62-ORIGIN
L_000c0f62:
    cmp/ge r2,r14
    .org 0xc0f64-ORIGIN
L_000c0f64:
    bt L_000c0f7e
    .org 0xc0f66-ORIGIN
L_000c0f66:
    mov.w L_000c102c,r6
    .org 0xc0f68-ORIGIN
L_000c0f68:
    mov r9,r2
    .org 0xc0f6a-ORIGIN
L_000c0f6a:
    mov.l @(0x4,r15),r0
    .org 0xc0f6c-ORIGIN
L_000c0f6c:
    add r6,r2
    .org 0xc0f6e-ORIGIN
L_000c0f6e:
    mov.w @(r0,r2),r6
    .org 0xc0f70-ORIGIN
L_000c0f70:
    mov #-0x80,r2
    .org 0xc0f72-ORIGIN
L_000c0f72:
    shll8 r2
    .org 0xc0f74-ORIGIN
L_000c0f74:
    extu.w r6,r6
    .org 0xc0f76-ORIGIN
L_000c0f76:
    add r2,r6
    .org 0xc0f78-ORIGIN
L_000c0f78:
    shll8 r6
    .org 0xc0f7a-ORIGIN
L_000c0f7a:
    add r5,r6
    .org 0xc0f7c-ORIGIN
L_000c0f7c:
    mov r6,r5
    .org 0xc0f7e-ORIGIN
L_000c0f7e:
    mov.w L_000c102e,r6
    .org 0xc0f80-ORIGIN
L_000c0f80:
    mov r9,r2
    .org 0xc0f82-ORIGIN
L_000c0f82:
    mov r10,r0
    .org 0xc0f84-ORIGIN
L_000c0f84:
    mov.l L_000c11a0,r3
    .org 0xc0f86-ORIGIN
L_000c0f86:
    add r6,r2
    .org 0xc0f88-ORIGIN
L_000c0f88:
    mov.l @(r0,r2),r6
    .org 0xc0f8a-ORIGIN
L_000c0f8a:
    mov #-0x80,r2
    .org 0xc0f8c-ORIGIN
L_000c0f8c:
    extu.b r2,r2
    .org 0xc0f8e-ORIGIN
L_000c0f8e:
    mov.b @(0x4,r3),r0
    .org 0xc0f90-ORIGIN
L_000c0f90:
    shll16 r2
    .org 0xc0f92-ORIGIN
L_000c0f92:
    sub r2,r6
    .org 0xc0f94-ORIGIN
L_000c0f94:
    add r6,r5
    .org 0xc0f96-ORIGIN
L_000c0f96:
    extu.b r0,r6
    .org 0xc0f98-ORIGIN
L_000c0f98:
    cmp/gt r6,r14
    .org 0xc0f9a-ORIGIN
L_000c0f9a:
    bt L_000c0fa2
    .org 0xc0f9c-ORIGIN
L_000c0f9c:
    neg r6,r2
    .org 0xc0f9e-ORIGIN
L_000c0f9e:
    cmp/ge r2,r14
    .org 0xc0fa0-ORIGIN
L_000c0fa0:
    bt L_000c0faa
    .org 0xc0fa2-ORIGIN
L_000c0fa2:
    extu.b r4,r2
    .org 0xc0fa4-ORIGIN
L_000c0fa4:
    add #-0x80,r2
    .org 0xc0fa6-ORIGIN
L_000c0fa6:
    shll16 r2
    .org 0xc0fa8-ORIGIN
L_000c0fa8:
    add r2,r5
    .org 0xc0faa-ORIGIN
L_000c0faa:
    cmp/pz r5
    .org 0xc0fac-ORIGIN
L_000c0fac:
    bt/s L_000c0fb2
    .org 0xc0fae-ORIGIN
L_000c0fae:
    mov r5,r2
    .org 0xc0fb0-ORIGIN
L_000c0fb0:
    mov #0x0,r2
    .org 0xc0fb2-ORIGIN
L_000c0fb2:
    mov.l L_000c11a4,r6
    .org 0xc0fb4-ORIGIN
L_000c0fb4:
    cmp/gt r6,r2
    .org 0xc0fb6-ORIGIN
L_000c0fb6:
    bt L_000c0fba
    .org 0xc0fb8-ORIGIN
L_000c0fb8:
    mov r2,r6
    .org 0xc0fba-ORIGIN
L_000c0fba:
    mov.w L_000c1030,r5
    .org 0xc0fbc-ORIGIN
L_000c0fbc:
    mov r9,r2
    .org 0xc0fbe-ORIGIN
L_000c0fbe:
    mov r10,r0
    .org 0xc0fc0-ORIGIN
L_000c0fc0:
    mov.l L_000c11a8,r14
    .org 0xc0fc2-ORIGIN
L_000c0fc2:
    add r5,r2
    .org 0xc0fc4-ORIGIN
L_000c0fc4:
    mov.l L_000c11ac,r5
    .org 0xc0fc6-ORIGIN
L_000c0fc6:
    mov.l r6,@(r0,r2)
    .org 0xc0fc8-ORIGIN
L_000c0fc8:
    add r14,r6
    .org 0xc0fca-ORIGIN
L_000c0fca:
    mov.b @r5,r2
    .org 0xc0fcc-ORIGIN
L_000c0fcc:
    mov.l L_000c11b0,r4
    .org 0xc0fce-ORIGIN
L_000c0fce:
    extu.b r2,r2
    .org 0xc0fd0-ORIGIN
L_000c0fd0:
    mov.l L_000c119c,r7
    .org 0xc0fd2-ORIGIN
L_000c0fd2:
    mul.l r6,r2
    .org 0xc0fd4-ORIGIN
L_000c0fd4:
    mov.b @r4,r5
    .org 0xc0fd6-ORIGIN
L_000c0fd6:
    sts macl,r1
    .org 0xc0fd8-ORIGIN
L_000c0fd8:
    extu.b r5,r5
    .org 0xc0fda-ORIGIN
L_000c0fda:
    jsr @r7
    .org 0xc0fdc-ORIGIN
L_000c0fdc:
    mov r5,r0
    .org 0xc0fde-ORIGIN
L_000c0fde:
    cmp/gt r14,r0
    .org 0xc0fe0-ORIGIN
L_000c0fe0:
    bt/s L_000c0fe8
    .org 0xc0fe2-ORIGIN
L_000c0fe2:
    mov r0,r6
    .org 0xc0fe4-ORIGIN
L_000c0fe4:
    bra L_000c1004
    .org 0xc0fe6-ORIGIN
L_000c0fe6:
    mov #0x0,r6
    .org 0xc0fe8-ORIGIN
L_000c0fe8:
    mov.l L_000c11b4,r2
    .org 0xc0fea-ORIGIN
L_000c0fea:
    cmp/gt r2,r6
    .org 0xc0fec-ORIGIN
L_000c0fec:
    bf L_000c0ff4
    .org 0xc0fee-ORIGIN
L_000c0fee:
    mov.l L_000c11b8,r6
    .org 0xc0ff0-ORIGIN
L_000c0ff0:
    bra L_000c1004
    .org 0xc0ff2-ORIGIN
L_000c0ff2:
    nop
    .org 0xc0ff4-ORIGIN
L_000c0ff4:
    mov r6,r2
    .org 0xc0ff6-ORIGIN
L_000c0ff6:
    mov #0x8,r6
    .org 0xc0ff8-ORIGIN
L_000c0ff8:
    shll2 r2
    .org 0xc0ffa-ORIGIN
L_000c0ffa:
    shll8 r6
    .org 0xc0ffc-ORIGIN
L_000c0ffc:
    shll2 r2
    .org 0xc0ffe-ORIGIN
L_000c0ffe:
    shll16 r6
    .org 0xc1000-ORIGIN
L_000c1000:
    add r6,r2
    .org 0xc1002-ORIGIN
L_000c1002:
    mov r2,r6
    .org 0xc1004-ORIGIN
L_000c1004:
    mov.w L_000c1032,r5
    .org 0xc1006-ORIGIN
L_000c1006:
    mov r9,r2
    .org 0xc1008-ORIGIN
L_000c1008:
    mov r10,r0
    .org 0xc100a-ORIGIN
L_000c100a:
    mov.l L_000c11bc,r3
    .org 0xc100c-ORIGIN
L_000c100c:
    add r5,r2
    .org 0xc100e-ORIGIN
L_000c100e:
    mov.l r6,@(r0,r2)
    .org 0xc1010-ORIGIN
L_000c1010:
    mov.w L_000c1034,r0
    .org 0xc1012-ORIGIN
L_000c1012:
    mov.l @(0x8,r15),r6
    .org 0xc1014-ORIGIN
L_000c1014:
    mov.b @(r0,r3),r2
    .org 0xc1016-ORIGIN
L_000c1016:
    extu.b r2,r2
    .org 0xc1018-ORIGIN
L_000c1018:
    tst r6,r2
    .org 0xc101a-ORIGIN
L_000c101a:
    bt L_000c1036
    .org 0xc101c-ORIGIN
L_000c101c:
    mov.l L_000c1190,r3
    .org 0xc101e-ORIGIN
L_000c101e:
    mov #0x12,r0
    .org 0xc1020-ORIGIN
L_000c1020:
    mov.l L_000c11c0,r4
    .org 0xc1022-ORIGIN
L_000c1022:
    mov.b @(r0,r3),r6
    .org 0xc1024-ORIGIN
L_000c1024:
    bra L_000c1040
    .org 0xc1026-ORIGIN
L_000c1026:
    extu.b r6,r6
    .org 0xc1028-ORIGIN
L_000c1028:
    .word 0x034a
    .org 0xc102a-ORIGIN
L_000c102a:
    .word 0x07fe
    .org 0xc102c-ORIGIN
L_000c102c:
    .word 0x086c
    .org 0xc102e-ORIGIN
L_000c102e:
    .word 0x0838
    .org 0xc1030-ORIGIN
L_000c1030:
    .word 0x0880
    .org 0xc1032-ORIGIN
L_000c1032:
    .word 0x0804
    .org 0xc1034-ORIGIN
L_000c1034:
    .word 0x023c
    .org 0xc1036-ORIGIN
L_000c1036:
    mov.l L_000c1190,r3
    .org 0xc1038-ORIGIN
L_000c1038:
    mov #0x12,r0
    .org 0xc103a-ORIGIN
L_000c103a:
    mov.l L_000c11c4,r4
    .org 0xc103c-ORIGIN
L_000c103c:
    mov.b @(r0,r3),r2
    .org 0xc103e-ORIGIN
L_000c103e:
    extu.b r2,r6
    .org 0xc1040-ORIGIN
L_000c1040:
    mov.l L_000c11c8,r5
    .org 0xc1042-ORIGIN
L_000c1042:
    mov.l L_000c11cc,r2
    .org 0xc1044-ORIGIN
L_000c1044:
    jsr @r2
    .org 0xc1046-ORIGIN
L_000c1046:
    nop
    .org 0xc1048-ORIGIN
L_000c1048:
    mov.w L_000c118a,r5
    .org 0xc104a-ORIGIN
L_000c104a:
    mov r0,r6
    .org 0xc104c-ORIGIN
L_000c104c:
    mov.l @(0x4,r15),r0
    .org 0xc104e-ORIGIN
L_000c104e:
    mov r9,r2
    .org 0xc1050-ORIGIN
L_000c1050:
    add r5,r2
    .org 0xc1052-ORIGIN
L_000c1052:
    tst r11,r11
    .org 0xc1054-ORIGIN
L_000c1054:
    bf/s L_000c1096
    .org 0xc1056-ORIGIN
L_000c1056:
    mov.w r6,@(r0,r2)
    .org 0xc1058-ORIGIN
L_000c1058:
    mov.l L_000c1190,r3
    .org 0xc105a-ORIGIN
L_000c105a:
    mov #0x12,r0
    .org 0xc105c-ORIGIN
L_000c105c:
    mov.l L_000c11d0,r4
    .org 0xc105e-ORIGIN
L_000c105e:
    mov.b @(r0,r3),r6
    .org 0xc1060-ORIGIN
L_000c1060:
    mov.l L_000c11d4,r10
    .org 0xc1062-ORIGIN
L_000c1062:
    extu.b r6,r7
    .org 0xc1064-ORIGIN
L_000c1064:
    mov.l L_000c11d8,r6
    .org 0xc1066-ORIGIN
L_000c1066:
    mov.l L_000c11dc,r13
    .org 0xc1068-ORIGIN
L_000c1068:
    mov r10,r5
    .org 0xc106a-ORIGIN
L_000c106a:
    mov.b @(0x3,r6),r0
    .org 0xc106c-ORIGIN
L_000c106c:
    mov.l L_000c11e0,r12
    .org 0xc106e-ORIGIN
L_000c106e:
    mov r13,r6
    .org 0xc1070-ORIGIN
L_000c1070:
    extu.b r0,r0
    .org 0xc1072-ORIGIN
L_000c1072:
    jsr @r12
    .org 0xc1074-ORIGIN
L_000c1074:
    mov.w r0,@(0x2,r15)
    .org 0xc1076-ORIGIN
L_000c1076:
    mov.l L_000c1190,r1
    .org 0xc1078-ORIGIN
L_000c1078:
    mov r0,r14
    .org 0xc107a-ORIGIN
L_000c107a:
    mov #0x12,r0
    .org 0xc107c-ORIGIN
L_000c107c:
    mov.l L_000c11d8,r6
    .org 0xc107e-ORIGIN
L_000c107e:
    mov.b @(r0,r1),r2
    .org 0xc1080-ORIGIN
L_000c1080:
    mov r11,r0
    .org 0xc1082-ORIGIN
L_000c1082:
    mov.l L_000c11d0,r4
    .org 0xc1084-ORIGIN
L_000c1084:
    mov r10,r5
    .org 0xc1086-ORIGIN
L_000c1086:
    extu.b r2,r7
    .org 0xc1088-ORIGIN
L_000c1088:
    mov.b @(r0,r6),r2
    .org 0xc108a-ORIGIN
L_000c108a:
    mov r13,r6
    .org 0xc108c-ORIGIN
L_000c108c:
    extu.b r2,r0
    .org 0xc108e-ORIGIN
L_000c108e:
    jsr @r12
    .org 0xc1090-ORIGIN
L_000c1090:
    mov.w r0,@(0x2,r15)
    .org 0xc1092-ORIGIN
L_000c1092:
    bra L_000c10d0
    .org 0xc1094-ORIGIN
L_000c1094:
    nop
    .org 0xc1096-ORIGIN
L_000c1096:
    mov.l L_000c1190,r3
    .org 0xc1098-ORIGIN
L_000c1098:
    mov #0x12,r0
    .org 0xc109a-ORIGIN
L_000c109a:
    mov.l L_000c11e4,r4
    .org 0xc109c-ORIGIN
L_000c109c:
    mov.b @(r0,r3),r6
    .org 0xc109e-ORIGIN
L_000c109e:
    mov.l L_000c11d4,r10
    .org 0xc10a0-ORIGIN
L_000c10a0:
    extu.b r6,r7
    .org 0xc10a2-ORIGIN
L_000c10a2:
    mov.l L_000c11d8,r6
    .org 0xc10a4-ORIGIN
L_000c10a4:
    mov.l L_000c11dc,r12
    .org 0xc10a6-ORIGIN
L_000c10a6:
    mov r10,r5
    .org 0xc10a8-ORIGIN
L_000c10a8:
    mov.b @(0x3,r6),r0
    .org 0xc10aa-ORIGIN
L_000c10aa:
    mov.l L_000c11e0,r13
    .org 0xc10ac-ORIGIN
L_000c10ac:
    mov r12,r6
    .org 0xc10ae-ORIGIN
L_000c10ae:
    extu.b r0,r0
    .org 0xc10b0-ORIGIN
L_000c10b0:
    jsr @r13
    .org 0xc10b2-ORIGIN
L_000c10b2:
    mov.w r0,@(0x2,r15)
    .org 0xc10b4-ORIGIN
L_000c10b4:
    mov.l L_000c1190,r1
    .org 0xc10b6-ORIGIN
L_000c10b6:
    mov r0,r14
    .org 0xc10b8-ORIGIN
L_000c10b8:
    mov #0x12,r0
    .org 0xc10ba-ORIGIN
L_000c10ba:
    mov.l L_000c11d8,r6
    .org 0xc10bc-ORIGIN
L_000c10bc:
    mov.b @(r0,r1),r2
    .org 0xc10be-ORIGIN
L_000c10be:
    mov r11,r0
    .org 0xc10c0-ORIGIN
L_000c10c0:
    mov.l L_000c11e4,r4
    .org 0xc10c2-ORIGIN
L_000c10c2:
    mov r10,r5
    .org 0xc10c4-ORIGIN
L_000c10c4:
    extu.b r2,r7
    .org 0xc10c6-ORIGIN
L_000c10c6:
    mov.b @(r0,r6),r2
    .org 0xc10c8-ORIGIN
L_000c10c8:
    mov r12,r6
    .org 0xc10ca-ORIGIN
L_000c10ca:
    extu.b r2,r0
    .org 0xc10cc-ORIGIN
L_000c10cc:
    jsr @r13
    .org 0xc10ce-ORIGIN
L_000c10ce:
    mov.w r0,@(0x2,r15)
    .org 0xc10d0-ORIGIN
L_000c10d0:
    mov #0x56,r2
    .org 0xc10d2-ORIGIN
L_000c10d2:
    mov r0,r4
    .org 0xc10d4-ORIGIN
L_000c10d4:
    stc gbr,r6
    .org 0xc10d6-ORIGIN
L_000c10d6:
    shll2 r2
    .org 0xc10d8-ORIGIN
L_000c10d8:
    mov.l @(0x4,r15),r0
    .org 0xc10da-ORIGIN
L_000c10da:
    add r2,r6
    .org 0xc10dc-ORIGIN
L_000c10dc:
    mov.w r14,@(r0,r6)
    .org 0xc10de-ORIGIN
L_000c10de:
    add #-0x4,r2
    .org 0xc10e0-ORIGIN
L_000c10e0:
    stc gbr,r6
    .org 0xc10e2-ORIGIN
L_000c10e2:
    extu.w r4,r4
    .org 0xc10e4-ORIGIN
L_000c10e4:
    add r2,r6
    .org 0xc10e6-ORIGIN
L_000c10e6:
    add #0x32,r8
    .org 0xc10e8-ORIGIN
L_000c10e8:
    mov.w r4,@(r0,r6)
    .org 0xc10ea-ORIGIN
L_000c10ea:
    mov r11,r0
    .org 0xc10ec-ORIGIN
L_000c10ec:
    mov.b @(r0,r8),r2
    .org 0xc10ee-ORIGIN
L_000c10ee:
    extu.b r2,r6
    .org 0xc10f0-ORIGIN
L_000c10f0:
    add #-0x80,r6
    .org 0xc10f2-ORIGIN
L_000c10f2:
    cmp/pz r6
    .org 0xc10f4-ORIGIN
L_000c10f4:
    bt L_000c10f8
    .org 0xc10f6-ORIGIN
L_000c10f6:
    neg r6,r6
    .org 0xc10f8-ORIGIN
L_000c10f8:
    mov.l L_000c11a0,r3
    .org 0xc10fa-ORIGIN
L_000c10fa:
    mov.b @r3,r2
    .org 0xc10fc-ORIGIN
L_000c10fc:
    extu.b r2,r2
    .org 0xc10fe-ORIGIN
L_000c10fe:
    cmp/ge r2,r6
    .org 0xc1100-ORIGIN
L_000c1100:
    bf L_000c112e
    .org 0xc1102-ORIGIN
L_000c1102:
    mov.l L_000c11e8,r6
    .org 0xc1104-ORIGIN
L_000c1104:
    extu.w r14,r5
    .org 0xc1106-ORIGIN
L_000c1106:
    sub r4,r5
    .org 0xc1108-ORIGIN
L_000c1108:
    mov r4,r14
    .org 0xc110a-ORIGIN
L_000c110a:
    mov.b @r6,r2
    .org 0xc110c-ORIGIN
L_000c110c:
    extu.b r2,r6
    .org 0xc110e-ORIGIN
L_000c110e:
    add #-0x80,r6
    .org 0xc1110-ORIGIN
L_000c1110:
    mul.l r6,r5
    .org 0xc1112-ORIGIN
L_000c1112:
    mov.l L_000c11ec,r6
    .org 0xc1114-ORIGIN
L_000c1114:
    jsr @r6
    .org 0xc1116-ORIGIN
L_000c1116:
    sts macl,r0
    .org 0xc1118-ORIGIN
L_000c1118:
    add r14,r0
    .org 0xc111a-ORIGIN
L_000c111a:
    cmp/pz r0
    .org 0xc111c-ORIGIN
L_000c111c:
    bt/s L_000c1122
    .org 0xc111e-ORIGIN
L_000c111e:
    mov r0,r6
    .org 0xc1120-ORIGIN
L_000c1120:
    mov #0x0,r6
    .org 0xc1122-ORIGIN
L_000c1122:
    mov #-0x1,r2
    .org 0xc1124-ORIGIN
L_000c1124:
    extu.w r2,r2
    .org 0xc1126-ORIGIN
L_000c1126:
    cmp/gt r2,r6
    .org 0xc1128-ORIGIN
L_000c1128:
    bf L_000c1130
    .org 0xc112a-ORIGIN
L_000c112a:
    bra L_000c1130
    .org 0xc112c-ORIGIN
L_000c112c:
    mov #-0x1,r6
    .org 0xc112e-ORIGIN
L_000c112e:
    mov r4,r6
    .org 0xc1130-ORIGIN
L_000c1130:
    mov r6,r2
    .org 0xc1132-ORIGIN
L_000c1132:
    mov.w L_000c118c,r6
    .org 0xc1134-ORIGIN
L_000c1134:
    mov.l @(0x4,r15),r0
    .org 0xc1136-ORIGIN
L_000c1136:
    add r6,r9
    .org 0xc1138-ORIGIN
L_000c1138:
    mov.w r2,@(r0,r9)
    .org 0xc113a-ORIGIN
L_000c113a:
    add #0x10,r15
    .org 0xc113c-ORIGIN
L_000c113c:
    ldc.l @r15+,gbr
    .org 0xc113e-ORIGIN
L_000c113e:
    lds.l @r15+,macl
    .org 0xc1140-ORIGIN
L_000c1140:
    lds.l @r15+,pr
    .org 0xc1142-ORIGIN
L_000c1142:
    mov.l @r15+,r14
    .org 0xc1144-ORIGIN
L_000c1144:
    mov.l @r15+,r13
    .org 0xc1146-ORIGIN
L_000c1146:
    mov.l @r15+,r12
    .org 0xc1148-ORIGIN
L_000c1148:
    mov.l @r15+,r11
    .org 0xc114a-ORIGIN
L_000c114a:
    mov.l @r15+,r10
    .org 0xc114c-ORIGIN
L_000c114c:
    mov.l @r15+,r9
    .org 0xc114e-ORIGIN
L_000c114e:
    rts
    .org 0xc1150-ORIGIN
L_000c1150:
    mov.l @r15+,r8
    .org 0xc118a-ORIGIN
L_000c118a:
    .word 0x080c
    .org 0xc118c-ORIGIN
L_000c118c:
    .word 0x07fa
    .org 0xc1190-ORIGIN
L_000c1190:
    .long 0xffff119c
    .org 0xc1194-ORIGIN
L_000c1194:
    .long 0x000123fa
    .org 0xc1198-ORIGIN
L_000c1198:
    .long 0x00011beb
    .org 0xc119c-ORIGIN
L_000c119c:
    .long 0x00021bbc
    .org 0xc11a0-ORIGIN
L_000c11a0:
    .long 0x00008d61
    .org 0xc11a4-ORIGIN
L_000c11a4:
    .long 0x00ffffff
    .org 0xc11a8-ORIGIN
L_000c11a8:
    .long 0xff800000
    .org 0xc11ac-ORIGIN
L_000c11ac:
    .long 0x0000833c
    .org 0xc11b0-ORIGIN
L_000c11b0:
    .long 0x00008dd9
    .org 0xc11b4-ORIGIN
L_000c11b4:
    .long 0x007fffff
    .org 0xc11b8-ORIGIN
L_000c11b8:
    .long 0x0fffffff
    .org 0xc11bc-ORIGIN
L_000c11bc:
    .long 0xffff128c
    .org 0xc11c0-ORIGIN
L_000c11c0:
    .long 0x00015ad0
    .org 0xc11c4-ORIGIN
L_000c11c4:
    .long 0x00015b10
    .org 0xc11c8-ORIGIN
L_000c11c8:
    .long 0x000149ca
    .org 0xc11cc-ORIGIN
L_000c11cc:
    .long 0x000264f8
    .org 0xc11d0-ORIGIN
L_000c11d0:
    .long 0x0000f38e
    .org 0xc11d4-ORIGIN
L_000c11d4:
    .long 0x0001498a
    .org 0xc11d8-ORIGIN
L_000c11d8:
    .long 0xffff2324
    .org 0xc11dc-ORIGIN
L_000c11dc:
    .long 0x000149aa
    .org 0xc11e0-ORIGIN
L_000c11e0:
    .long 0x00026270
    .org 0xc11e4-ORIGIN
L_000c11e4:
    .long 0x0000f40e
    .org 0xc11e8-ORIGIN
L_000c11e8:
    .long 0x0000879a
    .org 0xc11ec-ORIGIN
L_000c11ec:
    .long 0x000224f8
