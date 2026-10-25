! Complete stock shared weight producer, conditioning consumer and real helpers.
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
    mov.l P_00021cd8,r1
    .org 0x21c72-ORIGIN
L_00021c72:
    mov.l P_00021cdc,r2
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
P_00021cd8:
    .byte 0xff
    .org 0x21cd9-ORIGIN
P_00021cd9:
    .byte 0xff
    .org 0x21cda-ORIGIN
P_00021cda:
    .byte 0x98
    .org 0x21cdb-ORIGIN
P_00021cdb:
    .byte 0x18
    .org 0x21cdc-ORIGIN
P_00021cdc:
    .byte 0x00
    .org 0x21cdd-ORIGIN
P_00021cdd:
    .byte 0x00
    .org 0x21cde-ORIGIN
P_00021cde:
    .byte 0x04
    .org 0x21cdf-ORIGIN
P_00021cdf:
    .byte 0x4e
    .org 0x262a8-ORIGIN
L_000262a8:
    sts.l pr,@-r15
    .org 0x262aa-ORIGIN
L_000262aa:
    mov.l r4,@-r15
    .org 0x262ac-ORIGIN
L_000262ac:
    extu.w r7,r7
    .org 0x262ae-ORIGIN
L_000262ae:
    mov r5,r0
    .org 0x262b0-ORIGIN
L_000262b0:
    mov r7,r5
    .org 0x262b2-ORIGIN
L_000262b2:
    mov.l P_000262dc,r7
    .org 0x262b4-ORIGIN
L_000262b4:
    jsr @r7
    .org 0x262b6-ORIGIN
L_000262b6:
    mov #0x1e,r4
    .org 0x262b8-ORIGIN
L_000262b8:
    mov.l r5,@-r15
    .org 0x262ba-ORIGIN
L_000262ba:
    mov.l r4,@-r15
    .org 0x262bc-ORIGIN
L_000262bc:
    mov r6,r0
    .org 0x262be-ORIGIN
L_000262be:
    mov.l @(0x10,r15),r5
    .org 0x262c0-ORIGIN
L_000262c0:
    extu.w r5,r5
    .org 0x262c2-ORIGIN
L_000262c2:
    jsr @r7
    .org 0x262c4-ORIGIN
L_000262c4:
    mov #0x1e,r4
    .org 0x262c6-ORIGIN
L_000262c6:
    mov.l @r15+,r0
    .org 0x262c8-ORIGIN
L_000262c8:
    mov.l @r15+,r1
    .org 0x262ca-ORIGIN
L_000262ca:
    mov r4,r2
    .org 0x262cc-ORIGIN
L_000262cc:
    mov r5,r3
    .org 0x262ce-ORIGIN
L_000262ce:
    mov.l @r15+,r4
    .org 0x262d0-ORIGIN
L_000262d0:
    lds.l @r15+,pr
    .org 0x262d2-ORIGIN
L_000262d2:
    mov.l P_000262d8,r7
    .org 0x262d4-ORIGIN
L_000262d4:
    jmp @r7
    .org 0x262d6-ORIGIN
L_000262d6:
    mov #0x10,r5
    .org 0x262d8-ORIGIN
P_000262d8:
    .byte 0x00
    .org 0x262d9-ORIGIN
P_000262d9:
    .byte 0x02
    .org 0x262da-ORIGIN
P_000262da:
    .byte 0x68
    .org 0x262db-ORIGIN
P_000262db:
    .byte 0x48
    .org 0x262dc-ORIGIN
P_000262dc:
    .byte 0x00
    .org 0x262dd-ORIGIN
P_000262dd:
    .byte 0x02
    .org 0x262de-ORIGIN
P_000262de:
    .byte 0x69
    .org 0x262df-ORIGIN
P_000262df:
    .byte 0x84
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
    mov.l P_00026520,r7
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
    mov.l P_0002651c,r6
    .org 0x26516-ORIGIN
L_00026516:
    jmp @r6
    .org 0x26518-ORIGIN
L_00026518:
    extu.w r1,r0
    .org 0x2651c-ORIGIN
P_0002651c:
    .byte 0x00
    .org 0x2651d-ORIGIN
P_0002651d:
    .byte 0x02
    .org 0x2651e-ORIGIN
P_0002651e:
    .byte 0x67
    .org 0x2651f-ORIGIN
P_0002651f:
    .byte 0x40
    .org 0x26520-ORIGIN
P_00026520:
    .byte 0x00
    .org 0x26521-ORIGIN
P_00026521:
    .byte 0x02
    .org 0x26522-ORIGIN
P_00026522:
    .byte 0x69
    .org 0x26523-ORIGIN
P_00026523:
    .byte 0x84
    .org 0x26628-ORIGIN
L_00026628:
    sts.l pr,@-r15
    .org 0x2662a-ORIGIN
L_0002662a:
    mov.l r4,@-r15
    .org 0x2662c-ORIGIN
L_0002662c:
    extu.w r7,r7
    .org 0x2662e-ORIGIN
L_0002662e:
    mov r5,r0
    .org 0x26630-ORIGIN
L_00026630:
    mov r7,r5
    .org 0x26632-ORIGIN
L_00026632:
    mov.l P_0002665c,r7
    .org 0x26634-ORIGIN
L_00026634:
    jsr @r7
    .org 0x26636-ORIGIN
L_00026636:
    mov #0x1e,r4
    .org 0x26638-ORIGIN
L_00026638:
    mov.l r5,@-r15
    .org 0x2663a-ORIGIN
L_0002663a:
    mov.l r4,@-r15
    .org 0x2663c-ORIGIN
L_0002663c:
    mov r6,r0
    .org 0x2663e-ORIGIN
L_0002663e:
    mov.l @(0x10,r15),r5
    .org 0x26640-ORIGIN
L_00026640:
    extu.w r5,r5
    .org 0x26642-ORIGIN
L_00026642:
    jsr @r7
    .org 0x26644-ORIGIN
L_00026644:
    mov #0x1e,r4
    .org 0x26646-ORIGIN
L_00026646:
    mov.l @r15+,r0
    .org 0x26648-ORIGIN
L_00026648:
    mov.l @r15+,r1
    .org 0x2664a-ORIGIN
L_0002664a:
    mov r4,r2
    .org 0x2664c-ORIGIN
L_0002664c:
    mov r5,r3
    .org 0x2664e-ORIGIN
L_0002664e:
    mov.l @r15+,r4
    .org 0x26650-ORIGIN
L_00026650:
    lds.l @r15+,pr
    .org 0x26652-ORIGIN
L_00026652:
    mov.l P_00026658,r7
    .org 0x26654-ORIGIN
L_00026654:
    jmp @r7
    .org 0x26656-ORIGIN
L_00026656:
    mov #0x10,r5
    .org 0x26658-ORIGIN
P_00026658:
    .byte 0x00
    .org 0x26659-ORIGIN
P_00026659:
    .byte 0x02
    .org 0x2665a-ORIGIN
P_0002665a:
    .byte 0x6b
    .org 0x2665b-ORIGIN
P_0002665b:
    .byte 0x28
    .org 0x2665c-ORIGIN
P_0002665c:
    .byte 0x00
    .org 0x2665d-ORIGIN
P_0002665d:
    .byte 0x02
    .org 0x2665e-ORIGIN
P_0002665e:
    .byte 0x6b
    .org 0x2665f-ORIGIN
P_0002665f:
    .byte 0x84
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
    mov.l P_000268a0,r7
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
P_000268a0:
    .byte 0x00
    .org 0x268a1-ORIGIN
P_000268a1:
    .byte 0x02
    .org 0x268a2-ORIGIN
P_000268a2:
    .byte 0x67
    .org 0x268a3-ORIGIN
P_000268a3:
    .byte 0x40
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
    mov.l P_000269c0,r2
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
P_000269c0:
    .byte 0x00
    .org 0x269c1-ORIGIN
P_000269c1:
    .byte 0x02
    .org 0x269c2-ORIGIN
P_000269c2:
    .byte 0x6c
    .org 0x269c3-ORIGIN
P_000269c3:
    .byte 0x78
    .org 0x26af8-ORIGIN
L_00026af8:
    cmp/hs r0,r2
    .org 0x26afa-ORIGIN
L_00026afa:
    bt L_00026b14
    .org 0x26afc-ORIGIN
L_00026afc:
    mov.l r0,@-r15
    .org 0x26afe-ORIGIN
L_00026afe:
    sub r2,r0
    .org 0x26b00-ORIGIN
L_00026b00:
    sts macl,r1
    .org 0x26b02-ORIGIN
L_00026b02:
    mul.l r3,r0
    .org 0x26b04-ORIGIN
L_00026b04:
    sts macl,r0
    .org 0x26b06-ORIGIN
L_00026b06:
    lds r1,macl
    .org 0x26b08-ORIGIN
L_00026b08:
    swap.w r0,r0
    .org 0x26b0a-ORIGIN
L_00026b0a:
    mov.l @r15+,r2
    .org 0x26b0c-ORIGIN
L_00026b0c:
    extu.w r0,r0
    .org 0x26b0e-ORIGIN
L_00026b0e:
    sub r0,r2
    .org 0x26b10-ORIGIN
L_00026b10:
    rts
    .org 0x26b12-ORIGIN
L_00026b12:
    mov r2,r0
    .org 0x26b14-ORIGIN
L_00026b14:
    sub r0,r2
    .org 0x26b16-ORIGIN
L_00026b16:
    sts macl,r1
    .org 0x26b18-ORIGIN
L_00026b18:
    mul.l r3,r2
    .org 0x26b1a-ORIGIN
L_00026b1a:
    sts macl,r2
    .org 0x26b1c-ORIGIN
L_00026b1c:
    lds r1,macl
    .org 0x26b1e-ORIGIN
L_00026b1e:
    swap.w r2,r2
    .org 0x26b20-ORIGIN
L_00026b20:
    extu.w r2,r2
    .org 0x26b22-ORIGIN
L_00026b22:
    rts
    .org 0x26b24-ORIGIN
L_00026b24:
    add r2,r0
    .org 0x26b28-ORIGIN
L_00026b28:
    mov.l r8,@-r15
    .org 0x26b2a-ORIGIN
L_00026b2a:
    sts.l pr,@-r15
    .org 0x26b2c-ORIGIN
L_00026b2c:
    sts macl,r7
    .org 0x26b2e-ORIGIN
L_00026b2e:
    mulu.w r5,r0
    .org 0x26b30-ORIGIN
L_00026b30:
    add r2,r4
    .org 0x26b32-ORIGIN
L_00026b32:
    sts macl,r0
    .org 0x26b34-ORIGIN
L_00026b34:
    lds r7,macl
    .org 0x26b36-ORIGIN
L_00026b36:
    shll r5
    .org 0x26b38-ORIGIN
L_00026b38:
    add r0,r4
    .org 0x26b3a-ORIGIN
L_00026b3a:
    add r4,r5
    .org 0x26b3c-ORIGIN
L_00026b3c:
    mov r1,r8
    .org 0x26b3e-ORIGIN
L_00026b3e:
    mov.l P_00026b80,r7
    .org 0x26b40-ORIGIN
L_00026b40:
    tst r3,r3
    .org 0x26b42-ORIGIN
L_00026b42:
    bt L_00026b6a
    .org 0x26b44-ORIGIN
L_00026b44:
    mov.w @r4,r1
    .org 0x26b46-ORIGIN
L_00026b46:
    mov.w @(0x2,r4),r0
    .org 0x26b48-ORIGIN
L_00026b48:
    extu.w r0,r2
    .org 0x26b4a-ORIGIN
L_00026b4a:
    jsr @r7
    .org 0x26b4c-ORIGIN
L_00026b4c:
    extu.w r1,r0
    .org 0x26b4e-ORIGIN
L_00026b4e:
    tst r8,r8
    .org 0x26b50-ORIGIN
L_00026b50:
    bt L_00026b7a
    .org 0x26b52-ORIGIN
L_00026b52:
    mov.l r0,@-r15
    .org 0x26b54-ORIGIN
L_00026b54:
    mov.w @r5,r1
    .org 0x26b56-ORIGIN
L_00026b56:
    mov.w @(0x2,r5),r0
    .org 0x26b58-ORIGIN
L_00026b58:
    extu.w r0,r2
    .org 0x26b5a-ORIGIN
L_00026b5a:
    jsr @r7
    .org 0x26b5c-ORIGIN
L_00026b5c:
    extu.w r1,r0
    .org 0x26b5e-ORIGIN
L_00026b5e:
    mov r0,r2
    .org 0x26b60-ORIGIN
L_00026b60:
    mov.l @r15+,r0
    .org 0x26b62-ORIGIN
L_00026b62:
    jsr @r7
    .org 0x26b64-ORIGIN
L_00026b64:
    mov r8,r3
    .org 0x26b66-ORIGIN
L_00026b66:
    bra L_00026b7a
    .org 0x26b68-ORIGIN
L_00026b68:
    nop
    .org 0x26b6a-ORIGIN
L_00026b6a:
    tst r8,r8
    .org 0x26b6c-ORIGIN
L_00026b6c:
    bt/s L_00026b7a
    .org 0x26b6e-ORIGIN
L_00026b6e:
    mov.w @r4,r0
    .org 0x26b70-ORIGIN
L_00026b70:
    mov.w @r5,r2
    .org 0x26b72-ORIGIN
L_00026b72:
    extu.w r0,r0
    .org 0x26b74-ORIGIN
L_00026b74:
    extu.w r2,r2
    .org 0x26b76-ORIGIN
L_00026b76:
    jsr @r7
    .org 0x26b78-ORIGIN
L_00026b78:
    mov r8,r3
    .org 0x26b7a-ORIGIN
L_00026b7a:
    lds.l @r15+,pr
    .org 0x26b7c-ORIGIN
L_00026b7c:
    rts
    .org 0x26b7e-ORIGIN
L_00026b7e:
    mov.l @r15+,r8
    .org 0x26b80-ORIGIN
P_00026b80:
    .byte 0x00
    .org 0x26b81-ORIGIN
P_00026b81:
    .byte 0x02
    .org 0x26b82-ORIGIN
P_00026b82:
    .byte 0x6a
    .org 0x26b83-ORIGIN
P_00026b83:
    .byte 0xf8
    .org 0x26b84-ORIGIN
L_00026b84:
    mov r4,r3
    .org 0x26b86-ORIGIN
L_00026b86:
    mov.w @(r0,r4),r1
    .org 0x26b88-ORIGIN
L_00026b88:
    extu.w r1,r1
    .org 0x26b8a-ORIGIN
L_00026b8a:
    cmp/eq r1,r5
    .org 0x26b8c-ORIGIN
L_00026b8c:
    bt L_00026bbc
    .org 0x26b8e-ORIGIN
L_00026b8e:
    cmp/hi r1,r5
    .org 0x26b90-ORIGIN
L_00026b90:
    bf L_00026bb4
    .org 0x26b92-ORIGIN
L_00026b92:
    cmp/eq r4,r3
    .org 0x26b94-ORIGIN
L_00026b94:
    bt L_00026bbc
    .org 0x26b96-ORIGIN
L_00026b96:
    sub r1,r5
    .org 0x26b98-ORIGIN
L_00026b98:
    shll16 r5
    .org 0x26b9a-ORIGIN
L_00026b9a:
    add r4,r0
    .org 0x26b9c-ORIGIN
L_00026b9c:
    mov.w @r0,r1
    .org 0x26b9e-ORIGIN
L_00026b9e:
    mov.w @(0x2,r0),r0
    .org 0x26ba0-ORIGIN
L_00026ba0:
    extu.w r1,r1
    .org 0x26ba2-ORIGIN
L_00026ba2:
    extu.w r0,r0
    .org 0x26ba4-ORIGIN
L_00026ba4:
    sts.l pr,@-r15
    .org 0x26ba6-ORIGIN
L_00026ba6:
    mov.l P_00026bc0,r2
    .org 0x26ba8-ORIGIN
L_00026ba8:
    sub r1,r0
    .org 0x26baa-ORIGIN
L_00026baa:
    jsr @r2
    .org 0x26bac-ORIGIN
L_00026bac:
    mov r5,r1
    .org 0x26bae-ORIGIN
L_00026bae:
    lds.l @r15+,pr
    .org 0x26bb0-ORIGIN
L_00026bb0:
    rts
    .org 0x26bb2-ORIGIN
L_00026bb2:
    mov r0,r5
    .org 0x26bb4-ORIGIN
L_00026bb4:
    add #-0x2,r4
    .org 0x26bb6-ORIGIN
L_00026bb6:
    cmp/pz r4
    .org 0x26bb8-ORIGIN
L_00026bb8:
    bt L_00026b86
    .org 0x26bba-ORIGIN
L_00026bba:
    mov #0x0,r4
    .org 0x26bbc-ORIGIN
L_00026bbc:
    rts
    .org 0x26bbe-ORIGIN
L_00026bbe:
    mov #0x0,r5
    .org 0x26bc0-ORIGIN
P_00026bc0:
    .byte 0x00
    .org 0x26bc1-ORIGIN
P_00026bc1:
    .byte 0x02
    .org 0x26bc2-ORIGIN
P_00026bc2:
    .byte 0x6d
    .org 0x26bc3-ORIGIN
P_00026bc3:
    .byte 0x10
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
    .org 0x26d10-ORIGIN
L_00026d10:
    tst r0,r0
    .org 0x26d12-ORIGIN
L_00026d12:
    bt L_00026da2
    .org 0x26d14-ORIGIN
L_00026d14:
    mov.l r2,@-r15
    .org 0x26d16-ORIGIN
L_00026d16:
    mov #0x0,r2
    .org 0x26d18-ORIGIN
L_00026d18:
    div0u
    .org 0x26d1a-ORIGIN
L_00026d1a:
    rotcl r1
    .org 0x26d1c-ORIGIN
L_00026d1c:
    div1 r0,r2
    .org 0x26d1e-ORIGIN
L_00026d1e:
    rotcl r1
    .org 0x26d20-ORIGIN
L_00026d20:
    div1 r0,r2
    .org 0x26d22-ORIGIN
L_00026d22:
    rotcl r1
    .org 0x26d24-ORIGIN
L_00026d24:
    div1 r0,r2
    .org 0x26d26-ORIGIN
L_00026d26:
    rotcl r1
    .org 0x26d28-ORIGIN
L_00026d28:
    div1 r0,r2
    .org 0x26d2a-ORIGIN
L_00026d2a:
    rotcl r1
    .org 0x26d2c-ORIGIN
L_00026d2c:
    div1 r0,r2
    .org 0x26d2e-ORIGIN
L_00026d2e:
    rotcl r1
    .org 0x26d30-ORIGIN
L_00026d30:
    div1 r0,r2
    .org 0x26d32-ORIGIN
L_00026d32:
    rotcl r1
    .org 0x26d34-ORIGIN
L_00026d34:
    div1 r0,r2
    .org 0x26d36-ORIGIN
L_00026d36:
    rotcl r1
    .org 0x26d38-ORIGIN
L_00026d38:
    div1 r0,r2
    .org 0x26d3a-ORIGIN
L_00026d3a:
    rotcl r1
    .org 0x26d3c-ORIGIN
L_00026d3c:
    div1 r0,r2
    .org 0x26d3e-ORIGIN
L_00026d3e:
    rotcl r1
    .org 0x26d40-ORIGIN
L_00026d40:
    div1 r0,r2
    .org 0x26d42-ORIGIN
L_00026d42:
    rotcl r1
    .org 0x26d44-ORIGIN
L_00026d44:
    div1 r0,r2
    .org 0x26d46-ORIGIN
L_00026d46:
    rotcl r1
    .org 0x26d48-ORIGIN
L_00026d48:
    div1 r0,r2
    .org 0x26d4a-ORIGIN
L_00026d4a:
    rotcl r1
    .org 0x26d4c-ORIGIN
L_00026d4c:
    div1 r0,r2
    .org 0x26d4e-ORIGIN
L_00026d4e:
    rotcl r1
    .org 0x26d50-ORIGIN
L_00026d50:
    div1 r0,r2
    .org 0x26d52-ORIGIN
L_00026d52:
    rotcl r1
    .org 0x26d54-ORIGIN
L_00026d54:
    div1 r0,r2
    .org 0x26d56-ORIGIN
L_00026d56:
    rotcl r1
    .org 0x26d58-ORIGIN
L_00026d58:
    div1 r0,r2
    .org 0x26d5a-ORIGIN
L_00026d5a:
    rotcl r1
    .org 0x26d5c-ORIGIN
L_00026d5c:
    div1 r0,r2
    .org 0x26d5e-ORIGIN
L_00026d5e:
    rotcl r1
    .org 0x26d60-ORIGIN
L_00026d60:
    div1 r0,r2
    .org 0x26d62-ORIGIN
L_00026d62:
    rotcl r1
    .org 0x26d64-ORIGIN
L_00026d64:
    div1 r0,r2
    .org 0x26d66-ORIGIN
L_00026d66:
    rotcl r1
    .org 0x26d68-ORIGIN
L_00026d68:
    div1 r0,r2
    .org 0x26d6a-ORIGIN
L_00026d6a:
    rotcl r1
    .org 0x26d6c-ORIGIN
L_00026d6c:
    div1 r0,r2
    .org 0x26d6e-ORIGIN
L_00026d6e:
    rotcl r1
    .org 0x26d70-ORIGIN
L_00026d70:
    div1 r0,r2
    .org 0x26d72-ORIGIN
L_00026d72:
    rotcl r1
    .org 0x26d74-ORIGIN
L_00026d74:
    div1 r0,r2
    .org 0x26d76-ORIGIN
L_00026d76:
    rotcl r1
    .org 0x26d78-ORIGIN
L_00026d78:
    div1 r0,r2
    .org 0x26d7a-ORIGIN
L_00026d7a:
    rotcl r1
    .org 0x26d7c-ORIGIN
L_00026d7c:
    div1 r0,r2
    .org 0x26d7e-ORIGIN
L_00026d7e:
    rotcl r1
    .org 0x26d80-ORIGIN
L_00026d80:
    div1 r0,r2
    .org 0x26d82-ORIGIN
L_00026d82:
    rotcl r1
    .org 0x26d84-ORIGIN
L_00026d84:
    div1 r0,r2
    .org 0x26d86-ORIGIN
L_00026d86:
    rotcl r1
    .org 0x26d88-ORIGIN
L_00026d88:
    div1 r0,r2
    .org 0x26d8a-ORIGIN
L_00026d8a:
    rotcl r1
    .org 0x26d8c-ORIGIN
L_00026d8c:
    div1 r0,r2
    .org 0x26d8e-ORIGIN
L_00026d8e:
    rotcl r1
    .org 0x26d90-ORIGIN
L_00026d90:
    div1 r0,r2
    .org 0x26d92-ORIGIN
L_00026d92:
    rotcl r1
    .org 0x26d94-ORIGIN
L_00026d94:
    div1 r0,r2
    .org 0x26d96-ORIGIN
L_00026d96:
    rotcl r1
    .org 0x26d98-ORIGIN
L_00026d98:
    div1 r0,r2
    .org 0x26d9a-ORIGIN
L_00026d9a:
    rotcl r1
    .org 0x26d9c-ORIGIN
L_00026d9c:
    mov.l @r15+,r2
    .org 0x26d9e-ORIGIN
L_00026d9e:
    rts
    .org 0x26da0-ORIGIN
L_00026da0:
    mov r1,r0
    .org 0x26da2-ORIGIN
L_00026da2:
    rts
    .org 0x26da4-ORIGIN
L_00026da4:
    mov #0x0,r0
    .org 0x70e4c-ORIGIN
L_00070e4c:
    mov.l r10,@-r15
    .org 0x70e4e-ORIGIN
L_00070e4e:
    mov.l r11,@-r15
    .org 0x70e50-ORIGIN
L_00070e50:
    mov.l r12,@-r15
    .org 0x70e52-ORIGIN
L_00070e52:
    mov.l r13,@-r15
    .org 0x70e54-ORIGIN
L_00070e54:
    mov.l r14,@-r15
    .org 0x70e56-ORIGIN
L_00070e56:
    sts.l pr,@-r15
    .org 0x70e58-ORIGIN
L_00070e58:
    sts.l macl,@-r15
    .org 0x70e5a-ORIGIN
L_00070e5a:
    stc.l gbr,@-r15
    .org 0x70e5c-ORIGIN
L_00070e5c:
    mov.l P_00071058,r0
    .org 0x70e5e-ORIGIN
L_00070e5e:
    ldc r0,gbr
    .org 0x70e60-ORIGIN
L_00070e60:
    add #-0xc,r15
    .org 0x70e62-ORIGIN
L_00070e62:
    mov.w @(0x3e,gbr),r0
    .org 0x70e64-ORIGIN
L_00070e64:
    mov.l P_0007105c,r4
    .org 0x70e66-ORIGIN
L_00070e66:
    mov.w r0,@(0x2,r15)
    .org 0x70e68-ORIGIN
L_00070e68:
    mov.w @(0x17c,gbr),r0
    .org 0x70e6a-ORIGIN
L_00070e6a:
    mov.l P_00071060,r12
    .org 0x70e6c-ORIGIN
L_00070e6c:
    mov.l P_00071064,r14
    .org 0x70e6e-ORIGIN
L_00070e6e:
    extu.w r0,r7
    .org 0x70e70-ORIGIN
L_00070e70:
    mov.l P_00071068,r13
    .org 0x70e72-ORIGIN
L_00070e72:
    mov r12,r5
    .org 0x70e74-ORIGIN
L_00070e74:
    mov.l P_0007106c,r11
    .org 0x70e76-ORIGIN
L_00070e76:
    jsr @r13
    .org 0x70e78-ORIGIN
L_00070e78:
    mov r14,r6
    .org 0x70e7a-ORIGIN
L_00070e7a:
    mov r0,r2
    .org 0x70e7c-ORIGIN
L_00070e7c:
    mov #-0x52,r0
    .org 0x70e7e-ORIGIN
L_00070e7e:
    extu.b r0,r0
    .org 0x70e80-ORIGIN
L_00070e80:
    mov.l P_00071070,r4
    .org 0x70e82-ORIGIN
L_00070e82:
    mov.w r2,@(r0,r11)
    .org 0x70e84-ORIGIN
L_00070e84:
    mov r12,r5
    .org 0x70e86-ORIGIN
L_00070e86:
    mov.w @(0x3e,gbr),r0
    .org 0x70e88-ORIGIN
L_00070e88:
    mov r14,r6
    .org 0x70e8a-ORIGIN
L_00070e8a:
    mov.l P_00071074,r12
    .org 0x70e8c-ORIGIN
L_00070e8c:
    mov.w r0,@(0x2,r15)
    .org 0x70e8e-ORIGIN
L_00070e8e:
    mov.w @(0x17c,gbr),r0
    .org 0x70e90-ORIGIN
L_00070e90:
    jsr @r13
    .org 0x70e92-ORIGIN
L_00070e92:
    extu.w r0,r7
    .org 0x70e94-ORIGIN
L_00070e94:
    mov r0,r2
    .org 0x70e96-ORIGIN
L_00070e96:
    mov #-0x50,r0
    .org 0x70e98-ORIGIN
L_00070e98:
    extu.b r0,r0
    .org 0x70e9a-ORIGIN
L_00070e9a:
    mov.w r2,@(r0,r11)
    .org 0x70e9c-ORIGIN
L_00070e9c:
    mov.b @r12,r0
    .org 0x70e9e-ORIGIN
L_00070e9e:
    tst #0x8,r0
    .org 0x70ea0-ORIGIN
L_00070ea0:
    bt L_00070eac
    .org 0x70ea2-ORIGIN
L_00070ea2:
    mov.w @(0x3e,gbr),r0
    .org 0x70ea4-ORIGIN
L_00070ea4:
    mov.l r0,@(0x8,r15)
    .org 0x70ea6-ORIGIN
L_00070ea6:
    mov r0,r2
    .org 0x70ea8-ORIGIN
L_00070ea8:
    mov.w P_00070f66,r0
    .org 0x70eaa-ORIGIN
L_00070eaa:
    mov.w r2,@(r0,r11)
    .org 0x70eac-ORIGIN
L_00070eac:
    mov.w P_00070f66,r0
    .org 0x70eae-ORIGIN
L_00070eae:
    mov.l P_00071078,r4
    .org 0x70eb0-ORIGIN
L_00070eb0:
    mov.w @(r0,r11),r7
    .org 0x70eb2-ORIGIN
L_00070eb2:
    mov.l P_0007107c,r5
    .org 0x70eb4-ORIGIN
L_00070eb4:
    mov.l P_00071080,r2
    .org 0x70eb6-ORIGIN
L_00070eb6:
    mov.l P_00071084,r10
    .org 0x70eb8-ORIGIN
L_00070eb8:
    jsr @r2
    .org 0x70eba-ORIGIN
L_00070eba:
    extu.w r7,r6
    .org 0x70ebc-ORIGIN
L_00070ebc:
    extu.w r0,r6
    .org 0x70ebe-ORIGIN
L_00070ebe:
    mov.w P_00070f68,r0
    .org 0x70ec0-ORIGIN
L_00070ec0:
    mov #0x1,r2
    .org 0x70ec2-ORIGIN
L_00070ec2:
    mov.w r6,@(r0,r11)
    .org 0x70ec4-ORIGIN
L_00070ec4:
    mov #-0x52,r0
    .org 0x70ec6-ORIGIN
L_00070ec6:
    extu.b r0,r0
    .org 0x70ec8-ORIGIN
L_00070ec8:
    mov.w @(r0,r11),r5
    .org 0x70eca-ORIGIN
L_00070eca:
    shll16 r2
    .org 0x70ecc-ORIGIN
L_00070ecc:
    sub r6,r2
    .org 0x70ece-ORIGIN
L_00070ece:
    extu.w r5,r5
    .org 0x70ed0-ORIGIN
L_00070ed0:
    mov #-0x50,r0
    .org 0x70ed2-ORIGIN
L_00070ed2:
    mul.l r2,r5
    .org 0x70ed4-ORIGIN
L_00070ed4:
    extu.b r0,r0
    .org 0x70ed6-ORIGIN
L_00070ed6:
    mov.w @(r0,r11),r2
    .org 0x70ed8-ORIGIN
L_00070ed8:
    sts macl,r5
    .org 0x70eda-ORIGIN
L_00070eda:
    extu.w r2,r2
    .org 0x70edc-ORIGIN
L_00070edc:
    mul.l r6,r2
    .org 0x70ede-ORIGIN
L_00070ede:
    sts macl,r2
    .org 0x70ee0-ORIGIN
L_00070ee0:
    add r2,r5
    .org 0x70ee2-ORIGIN
L_00070ee2:
    shlr16 r5
    .org 0x70ee4-ORIGIN
L_00070ee4:
    extu.w r5,r7
    .org 0x70ee6-ORIGIN
L_00070ee6:
    mov r7,r0
    .org 0x70ee8-ORIGIN
L_00070ee8:
    mov.w r0,@(0x17e,gbr)
    .org 0x70eea-ORIGIN
L_00070eea:
    mov.b @r10,r0
    .org 0x70eec-ORIGIN
L_00070eec:
    tst #0x40,r0
    .org 0x70eee-ORIGIN
L_00070eee:
    bf L_00070efa
    .org 0x70ef0-ORIGIN
L_00070ef0:
    mov #-0x5c,r0
    .org 0x70ef2-ORIGIN
L_00070ef2:
    mov.l P_00071088,r13
    .org 0x70ef4-ORIGIN
L_00070ef4:
    extu.b r0,r0
    .org 0x70ef6-ORIGIN
L_00070ef6:
    bra L_00070f8a
    .org 0x70ef8-ORIGIN
L_00070ef8:
    mov.w r7,@(r0,r11)
    .org 0x70efa-ORIGIN
L_00070efa:
    mov.l P_0007108c,r5
    .org 0x70efc-ORIGIN
L_00070efc:
    mov.w @(0x3e,gbr),r0
    .org 0x70efe-ORIGIN
L_00070efe:
    mov.w @r5,r2
    .org 0x70f00-ORIGIN
L_00070f00:
    cmp/hi r2,r0
    .org 0x70f02-ORIGIN
L_00070f02:
    bt L_00070f6a
    .org 0x70f04-ORIGIN
L_00070f04:
    mov.l P_00071090,r6
    .org 0x70f06-ORIGIN
L_00070f06:
    mov.b @(0x3,r6),r0
    .org 0x70f08-ORIGIN
L_00070f08:
    tst #0x80,r0
    .org 0x70f0a-ORIGIN
L_00070f0a:
    bf L_00070f6a
    .org 0x70f0c-ORIGIN
L_00070f0c:
    mov.l P_00071094,r6
    .org 0x70f0e-ORIGIN
L_00070f0e:
    mov.b @(0x2,r6),r0
    .org 0x70f10-ORIGIN
L_00070f10:
    tst #0x40,r0
    .org 0x70f12-ORIGIN
L_00070f12:
    bf L_00070f6a
    .org 0x70f14-ORIGIN
L_00070f14:
    mov.l P_00071088,r13
    .org 0x70f16-ORIGIN
L_00070f16:
    mov #0x14,r0
    .org 0x70f18-ORIGIN
L_00070f18:
    mov.b @(r0,r13),r0
    .org 0x70f1a-ORIGIN
L_00070f1a:
    tst #0x1,r0
    .org 0x70f1c-ORIGIN
L_00070f1c:
    bf L_00070f6a
    .org 0x70f1e-ORIGIN
L_00070f1e:
    mov.b @(0x1,r6),r0
    .org 0x70f20-ORIGIN
L_00070f20:
    tst #0x1,r0
    .org 0x70f22-ORIGIN
L_00070f22:
    bf L_00070f6a
    .org 0x70f24-ORIGIN
L_00070f24:
    mov.l P_00071098,r5
    .org 0x70f26-ORIGIN
L_00070f26:
    mov.w @(0x1e,gbr),r0
    .org 0x70f28-ORIGIN
L_00070f28:
    mov.b @r5,r2
    .org 0x70f2a-ORIGIN
L_00070f2a:
    extu.w r0,r6
    .org 0x70f2c-ORIGIN
L_00070f2c:
    mov.l P_0007109c,r5
    .org 0x70f2e-ORIGIN
L_00070f2e:
    extu.b r2,r2
    .org 0x70f30-ORIGIN
L_00070f30:
    mul.l r6,r2
    .org 0x70f32-ORIGIN
L_00070f32:
    mov.b @r5,r4
    .org 0x70f34-ORIGIN
L_00070f34:
    mov #0x64,r0
    .org 0x70f36-ORIGIN
L_00070f36:
    mov.l P_000710a0,r6
    .org 0x70f38-ORIGIN
L_00070f38:
    sts macl,r1
    .org 0x70f3a-ORIGIN
L_00070f3a:
    extu.b r4,r5
    .org 0x70f3c-ORIGIN
L_00070f3c:
    jsr @r6
    .org 0x70f3e-ORIGIN
L_00070f3e:
    mov.l r5,@(0x4,r15)
    .org 0x70f40-ORIGIN
L_00070f40:
    mov r0,r5
    .org 0x70f42-ORIGIN
L_00070f42:
    mov.w @(0x17c,gbr),r0
    .org 0x70f44-ORIGIN
L_00070f44:
    mov.l @(0x4,r15),r2
    .org 0x70f46-ORIGIN
L_00070f46:
    extu.w r0,r6
    .org 0x70f48-ORIGIN
L_00070f48:
    mov.w @(0x17e,gbr),r0
    .org 0x70f4a-ORIGIN
L_00070f4a:
    sub r2,r5
    .org 0x70f4c-ORIGIN
L_00070f4c:
    extu.w r0,r7
    .org 0x70f4e-ORIGIN
L_00070f4e:
    sub r7,r6
    .org 0x70f50-ORIGIN
L_00070f50:
    cmp/gt r6,r5
    .org 0x70f52-ORIGIN
L_00070f52:
    bf L_00070f56
    .org 0x70f54-ORIGIN
L_00070f54:
    mov r6,r5
    .org 0x70f56-ORIGIN
L_00070f56:
    cmp/pz r5
    .org 0x70f58-ORIGIN
L_00070f58:
    bt/s L_00070f5e
    .org 0x70f5a-ORIGIN
L_00070f5a:
    mov r5,r2
    .org 0x70f5c-ORIGIN
L_00070f5c:
    mov #0x0,r2
    .org 0x70f5e-ORIGIN
L_00070f5e:
    mov #-0x64,r0
    .org 0x70f60-ORIGIN
L_00070f60:
    extu.b r0,r0
    .org 0x70f62-ORIGIN
L_00070f62:
    bra L_00070f74
    .org 0x70f64-ORIGIN
L_00070f64:
    mov.w r2,@(r0,r11)
    .org 0x70f66-ORIGIN
P_00070f66:
    .byte 0x07
    .org 0x70f67-ORIGIN
P_00070f67:
    .byte 0xec
    .org 0x70f68-ORIGIN
P_00070f68:
    .byte 0x06
    .org 0x70f69-ORIGIN
P_00070f69:
    .byte 0x82
    .org 0x70f6a-ORIGIN
L_00070f6a:
    mov #-0x64,r0
    .org 0x70f6c-ORIGIN
L_00070f6c:
    mov.l P_00071088,r13
    .org 0x70f6e-ORIGIN
L_00070f6e:
    mov #0x0,r2
    .org 0x70f70-ORIGIN
L_00070f70:
    extu.b r0,r0
    .org 0x70f72-ORIGIN
L_00070f72:
    mov.w r2,@(r0,r11)
    .org 0x70f74-ORIGIN
L_00070f74:
    extu.w r2,r2
    .org 0x70f76-ORIGIN
L_00070f76:
    mov r7,r6
    .org 0x70f78-ORIGIN
L_00070f78:
    add r2,r6
    .org 0x70f7a-ORIGIN
L_00070f7a:
    mov #-0x1,r2
    .org 0x70f7c-ORIGIN
L_00070f7c:
    extu.w r2,r2
    .org 0x70f7e-ORIGIN
L_00070f7e:
    cmp/hi r2,r6
    .org 0x70f80-ORIGIN
L_00070f80:
    bf L_00070f84
    .org 0x70f82-ORIGIN
L_00070f82:
    mov r2,r6
    .org 0x70f84-ORIGIN
L_00070f84:
    mov #-0x5c,r0
    .org 0x70f86-ORIGIN
L_00070f86:
    extu.b r0,r0
    .org 0x70f88-ORIGIN
L_00070f88:
    mov.w r6,@(r0,r11)
    .org 0x70f8a-ORIGIN
L_00070f8a:
    mov #0x5c,r0
    .org 0x70f8c-ORIGIN
L_00070f8c:
    mov.b @(r0,r13),r14
    .org 0x70f8e-ORIGIN
L_00070f8e:
    mov r14,r0
    .org 0x70f90-ORIGIN
L_00070f90:
    and #0x4,r0
    .org 0x70f92-ORIGIN
L_00070f92:
    tst r0,r0
    .org 0x70f94-ORIGIN
L_00070f94:
    bf/s L_00070fbe
    .org 0x70f96-ORIGIN
L_00070f96:
    mov r0,r2
    .org 0x70f98-ORIGIN
L_00070f98:
    mov.l P_000710a4,r5
    .org 0x70f9a-ORIGIN
L_00070f9a:
    mov.b @r5,r0
    .org 0x70f9c-ORIGIN
L_00070f9c:
    tst #0x8,r0
    .org 0x70f9e-ORIGIN
L_00070f9e:
    bt L_00070fbe
    .org 0x70fa0-ORIGIN
L_00070fa0:
    mov.b @r12,r0
    .org 0x70fa2-ORIGIN
L_00070fa2:
    tst #0x8,r0
    .org 0x70fa4-ORIGIN
L_00070fa4:
    bf L_00070fbe
    .org 0x70fa6-ORIGIN
L_00070fa6:
    mov.l P_00071094,r5
    .org 0x70fa8-ORIGIN
L_00070fa8:
    mov.b @(0x1,r5),r0
    .org 0x70faa-ORIGIN
L_00070faa:
    tst #0x1,r0
    .org 0x70fac-ORIGIN
L_00070fac:
    bf L_00070fbe
    .org 0x70fae-ORIGIN
L_00070fae:
    mov.l P_000710a8,r4
    .org 0x70fb0-ORIGIN
L_00070fb0:
    mov.w @(0x3e,gbr),r0
    .org 0x70fb2-ORIGIN
L_00070fb2:
    mov.w @r4,r6
    .org 0x70fb4-ORIGIN
L_00070fb4:
    cmp/hs r6,r0
    .org 0x70fb6-ORIGIN
L_00070fb6:
    bt L_00070fbe
    .org 0x70fb8-ORIGIN
L_00070fb8:
    mov r14,r0
    .org 0x70fba-ORIGIN
L_00070fba:
    bra L_00070ff0
    .org 0x70fbc-ORIGIN
L_00070fbc:
    or #0x4,r0
    .org 0x70fbe-ORIGIN
L_00070fbe:
    tst r2,r2
    .org 0x70fc0-ORIGIN
L_00070fc0:
    bt L_00070ff6
    .org 0x70fc2-ORIGIN
L_00070fc2:
    mov.w @(0x1ba,gbr),r0
    .org 0x70fc4-ORIGIN
L_00070fc4:
    extu.w r0,r4
    .org 0x70fc6-ORIGIN
L_00070fc6:
    mov.w @(0x1bc,gbr),r0
    .org 0x70fc8-ORIGIN
L_00070fc8:
    extu.w r0,r6
    .org 0x70fca-ORIGIN
L_00070fca:
    cmp/ge r6,r4
    .org 0x70fcc-ORIGIN
L_00070fcc:
    bt L_00070fd6
    .org 0x70fce-ORIGIN
L_00070fce:
    mov.w @(0x17c,gbr),r0
    .org 0x70fd0-ORIGIN
L_00070fd0:
    extu.w r0,r5
    .org 0x70fd2-ORIGIN
L_00070fd2:
    cmp/ge r7,r5
    .org 0x70fd4-ORIGIN
L_00070fd4:
    bt L_00070fec
    .org 0x70fd6-ORIGIN
L_00070fd6:
    cmp/gt r6,r4
    .org 0x70fd8-ORIGIN
L_00070fd8:
    bf L_00070ff6
    .org 0x70fda-ORIGIN
L_00070fda:
    mov.w @(0x17c,gbr),r0
    .org 0x70fdc-ORIGIN
L_00070fdc:
    extu.w r0,r6
    .org 0x70fde-ORIGIN
L_00070fde:
    cmp/gt r7,r6
    .org 0x70fe0-ORIGIN
L_00070fe0:
    bt L_00070ff6
    .org 0x70fe2-ORIGIN
L_00070fe2:
    mov.l P_000710ac,r5
    .org 0x70fe4-ORIGIN
L_00070fe4:
    mov.w @r5,r2
    .org 0x70fe6-ORIGIN
L_00070fe6:
    extu.w r2,r2
    .org 0x70fe8-ORIGIN
L_00070fe8:
    cmp/gt r2,r6
    .org 0x70fea-ORIGIN
L_00070fea:
    bt L_00070ff6
    .org 0x70fec-ORIGIN
L_00070fec:
    mov r14,r0
    .org 0x70fee-ORIGIN
L_00070fee:
    and #0xfb,r0
    .org 0x70ff0-ORIGIN
L_00070ff0:
    mov r0,r14
    .org 0x70ff2-ORIGIN
L_00070ff2:
    mov #0x5c,r0
    .org 0x70ff4-ORIGIN
L_00070ff4:
    mov.b r14,@(r0,r13)
    .org 0x70ff6-ORIGIN
L_00070ff6:
    mov.l P_000710b0,r5
    .org 0x70ff8-ORIGIN
L_00070ff8:
    mov #0x36,r0
    .org 0x70ffa-ORIGIN
L_00070ffa:
    mov.b @(r0,r5),r6
    .org 0x70ffc-ORIGIN
L_00070ffc:
    extu.b r6,r0
    .org 0x70ffe-ORIGIN
L_00070ffe:
    cmp/eq #0x1,r0
    .org 0x71000-ORIGIN
L_00071000:
    bt L_0007103a
    .org 0x71002-ORIGIN
L_00071002:
    cmp/eq #0x4,r0
    .org 0x71004-ORIGIN
L_00071004:
    bt L_0007103a
    .org 0x71006-ORIGIN
L_00071006:
    mov #0x66,r0
    .org 0x71008-ORIGIN
L_00071008:
    mov.b @(r0,r5),r0
    .org 0x7100a-ORIGIN
L_0007100a:
    cmp/eq #0x3,r0
    .org 0x7100c-ORIGIN
L_0007100c:
    bt L_0007103a
    .org 0x7100e-ORIGIN
L_0007100e:
    mov.b @r10,r0
    .org 0x71010-ORIGIN
L_00071010:
    tst #0x8,r0
    .org 0x71012-ORIGIN
L_00071012:
    bt L_0007103a
    .org 0x71014-ORIGIN
L_00071014:
    mov.l P_000710b4,r2
    .org 0x71016-ORIGIN
L_00071016:
    mov.b @r2,r0
    .org 0x71018-ORIGIN
L_00071018:
    tst #0x1,r0
    .org 0x7101a-ORIGIN
L_0007101a:
    bf L_0007103a
    .org 0x7101c-ORIGIN
L_0007101c:
    mov.l P_000710b8,r6
    .org 0x7101e-ORIGIN
L_0007101e:
    mov.b @r6,r0
    .org 0x71020-ORIGIN
L_00071020:
    tst #0x80,r0
    .org 0x71022-ORIGIN
L_00071022:
    bf L_0007103a
    .org 0x71024-ORIGIN
L_00071024:
    mov #0x5c,r0
    .org 0x71026-ORIGIN
L_00071026:
    mov.b @(r0,r13),r0
    .org 0x71028-ORIGIN
L_00071028:
    tst #0x4,r0
    .org 0x7102a-ORIGIN
L_0007102a:
    bt L_0007103a
    .org 0x7102c-ORIGIN
L_0007102c:
    mov #-0x5c,r0
    .org 0x7102e-ORIGIN
L_0007102e:
    extu.b r0,r0
    .org 0x71030-ORIGIN
L_00071030:
    mov.w @(r0,r11),r2
    .org 0x71032-ORIGIN
L_00071032:
    mov #-0x5a,r0
    .org 0x71034-ORIGIN
L_00071034:
    extu.b r0,r0
    .org 0x71036-ORIGIN
L_00071036:
    bra L_00071044
    .org 0x71038-ORIGIN
L_00071038:
    mov.w r2,@(r0,r11)
    .org 0x7103a-ORIGIN
L_0007103a:
    mov.w @(0x17c,gbr),r0
    .org 0x7103c-ORIGIN
L_0007103c:
    mov r0,r14
    .org 0x7103e-ORIGIN
L_0007103e:
    mov #-0x5a,r0
    .org 0x71040-ORIGIN
L_00071040:
    extu.b r0,r0
    .org 0x71042-ORIGIN
L_00071042:
    mov.w r14,@(r0,r11)
    .org 0x71044-ORIGIN
L_00071044:
    add #0xc,r15
    .org 0x71046-ORIGIN
L_00071046:
    ldc.l @r15+,gbr
    .org 0x71048-ORIGIN
L_00071048:
    lds.l @r15+,macl
    .org 0x7104a-ORIGIN
L_0007104a:
    lds.l @r15+,pr
    .org 0x7104c-ORIGIN
L_0007104c:
    mov.l @r15+,r14
    .org 0x7104e-ORIGIN
L_0007104e:
    mov.l @r15+,r13
    .org 0x71050-ORIGIN
L_00071050:
    mov.l @r15+,r12
    .org 0x71052-ORIGIN
L_00071052:
    mov.l @r15+,r11
    .org 0x71054-ORIGIN
L_00071054:
    rts
    .org 0x71056-ORIGIN
L_00071056:
    mov.l @r15+,r10
    .org 0x71058-ORIGIN
P_00071058:
    .byte 0xff
    .org 0x71059-ORIGIN
P_00071059:
    .byte 0xff
    .org 0x7105a-ORIGIN
P_0007105a:
    .byte 0x10
    .org 0x7105b-ORIGIN
P_0007105b:
    .byte 0x94
    .org 0x7105c-ORIGIN
P_0007105c:
    .byte 0x00
    .org 0x7105d-ORIGIN
P_0007105d:
    .byte 0x01
    .org 0x7105e-ORIGIN
P_0007105e:
    .byte 0x05
    .org 0x7105f-ORIGIN
P_0007105f:
    .byte 0x0e
    .org 0x71060-ORIGIN
P_00071060:
    .byte 0x00
    .org 0x71061-ORIGIN
P_00071061:
    .byte 0x01
    .org 0x71062-ORIGIN
P_00071062:
    .byte 0x31
    .org 0x71063-ORIGIN
P_00071063:
    .byte 0xe2
    .org 0x71064-ORIGIN
P_00071064:
    .byte 0x00
    .org 0x71065-ORIGIN
P_00071065:
    .byte 0x01
    .org 0x71066-ORIGIN
P_00071066:
    .byte 0x5f
    .org 0x71067-ORIGIN
P_00071067:
    .byte 0x20
    .org 0x71068-ORIGIN
P_00071068:
    .byte 0x00
    .org 0x71069-ORIGIN
P_00071069:
    .byte 0x02
    .org 0x7106a-ORIGIN
P_0007106a:
    .byte 0x62
    .org 0x7106b-ORIGIN
P_0007106b:
    .byte 0xa8
    .org 0x7106c-ORIGIN
P_0007106c:
    .byte 0xff
    .org 0x7106d-ORIGIN
P_0007106d:
    .byte 0xff
    .org 0x7106e-ORIGIN
P_0007106e:
    .byte 0x12
    .org 0x7106f-ORIGIN
P_0007106f:
    .byte 0x8c
    .org 0x71070-ORIGIN
P_00071070:
    .byte 0x00
    .org 0x71071-ORIGIN
P_00071071:
    .byte 0x01
    .org 0x71072-ORIGIN
P_00071072:
    .byte 0x07
    .org 0x71073-ORIGIN
P_00071073:
    .byte 0x0e
    .org 0x71074-ORIGIN
P_00071074:
    .byte 0xff
    .org 0x71075-ORIGIN
P_00071075:
    .byte 0xff
    .org 0x71076-ORIGIN
P_00071076:
    .byte 0x41
    .org 0x71077-ORIGIN
P_00071077:
    .byte 0x7e
    .org 0x71078-ORIGIN
P_00071078:
    .byte 0x00
    .org 0x71079-ORIGIN
P_00071079:
    .byte 0x01
    .org 0x7107a-ORIGIN
P_0007107a:
    .byte 0x48
    .org 0x7107b-ORIGIN
P_0007107b:
    .byte 0x8a
    .org 0x7107c-ORIGIN
P_0007107c:
    .byte 0x00
    .org 0x7107d-ORIGIN
P_0007107d:
    .byte 0x01
    .org 0x7107e-ORIGIN
P_0007107e:
    .byte 0x4c
    .org 0x7107f-ORIGIN
P_0007107f:
    .byte 0x7a
    .org 0x71080-ORIGIN
P_00071080:
    .byte 0x00
    .org 0x71081-ORIGIN
P_00071081:
    .byte 0x02
    .org 0x71082-ORIGIN
P_00071082:
    .byte 0x64
    .org 0x71083-ORIGIN
P_00071083:
    .byte 0xf8
    .org 0x71084-ORIGIN
P_00071084:
    .byte 0x00
    .org 0x71085-ORIGIN
P_00071085:
    .byte 0x00
    .org 0x71086-ORIGIN
P_00071086:
    .byte 0x89
    .org 0x71087-ORIGIN
P_00071087:
    .byte 0xfb
    .org 0x71088-ORIGIN
P_00071088:
    .byte 0xff
    .org 0x71089-ORIGIN
P_00071089:
    .byte 0xff
    .org 0x7108a-ORIGIN
P_0007108a:
    .byte 0x41
    .org 0x7108b-ORIGIN
P_0007108b:
    .byte 0xa9
    .org 0x7108c-ORIGIN
P_0007108c:
    .byte 0x00
    .org 0x7108d-ORIGIN
P_0007108d:
    .byte 0x00
    .org 0x7108e-ORIGIN
P_0007108e:
    .byte 0x95
    .org 0x7108f-ORIGIN
P_0007108f:
    .byte 0xd2
    .org 0x71090-ORIGIN
P_00071090:
    .byte 0xff
    .org 0x71091-ORIGIN
P_00071091:
    .byte 0xff
    .org 0x71092-ORIGIN
P_00071092:
    .byte 0x24
    .org 0x71093-ORIGIN
P_00071093:
    .byte 0x4c
    .org 0x71094-ORIGIN
P_00071094:
    .byte 0xff
    .org 0x71095-ORIGIN
P_00071095:
    .byte 0xff
    .org 0x71096-ORIGIN
P_00071096:
    .byte 0x24
    .org 0x71097-ORIGIN
P_00071097:
    .byte 0x5c
    .org 0x71098-ORIGIN
P_00071098:
    .byte 0x00
    .org 0x71099-ORIGIN
P_00071099:
    .byte 0x00
    .org 0x7109a-ORIGIN
P_0007109a:
    .byte 0x87
    .org 0x7109b-ORIGIN
P_0007109b:
    .byte 0x75
    .org 0x7109c-ORIGIN
P_0007109c:
    .byte 0x00
    .org 0x7109d-ORIGIN
P_0007109d:
    .byte 0x00
    .org 0x7109e-ORIGIN
P_0007109e:
    .byte 0x84
    .org 0x7109f-ORIGIN
P_0007109f:
    .byte 0x0f
    .org 0x710a0-ORIGIN
P_000710a0:
    .byte 0x00
    .org 0x710a1-ORIGIN
P_000710a1:
    .byte 0x02
    .org 0x710a2-ORIGIN
P_000710a2:
    .byte 0x1b
    .org 0x710a3-ORIGIN
P_000710a3:
    .byte 0xbc
    .org 0x710a4-ORIGIN
P_000710a4:
    .byte 0xff
    .org 0x710a5-ORIGIN
P_000710a5:
    .byte 0xff
    .org 0x710a6-ORIGIN
P_000710a6:
    .byte 0x41
    .org 0x710a7-ORIGIN
P_000710a7:
    .byte 0x80
    .org 0x710a8-ORIGIN
P_000710a8:
    .byte 0x00
    .org 0x710a9-ORIGIN
P_000710a9:
    .byte 0x00
    .org 0x710aa-ORIGIN
P_000710aa:
    .byte 0x90
    .org 0x710ab-ORIGIN
P_000710ab:
    .byte 0x20
    .org 0x710ac-ORIGIN
P_000710ac:
    .byte 0x00
    .org 0x710ad-ORIGIN
P_000710ad:
    .byte 0x00
    .org 0x710ae-ORIGIN
P_000710ae:
    .byte 0x90
    .org 0x710af-ORIGIN
P_000710af:
    .byte 0x22
    .org 0x710b0-ORIGIN
P_000710b0:
    .byte 0xff
    .org 0x710b1-ORIGIN
P_000710b1:
    .byte 0xff
    .org 0x710b2-ORIGIN
P_000710b2:
    .byte 0x26
    .org 0x710b3-ORIGIN
P_000710b3:
    .byte 0x7a
    .org 0x710b4-ORIGIN
P_000710b4:
    .byte 0x00
    .org 0x710b5-ORIGIN
P_000710b5:
    .byte 0x00
    .org 0x710b6-ORIGIN
P_000710b6:
    .byte 0x89
    .org 0x710b7-ORIGIN
P_000710b7:
    .byte 0xfa
    .org 0x710b8-ORIGIN
P_000710b8:
    .byte 0x00
    .org 0x710b9-ORIGIN
P_000710b9:
    .byte 0x00
    .org 0x710ba-ORIGIN
P_000710ba:
    .byte 0x8b
    .org 0x710bb-ORIGIN
P_000710bb:
    .byte 0x3f
    .org 0x720c4-ORIGIN
L_000720c4:
    mov.l r10,@-r15
    .org 0x720c6-ORIGIN
L_000720c6:
    mov.l r11,@-r15
    .org 0x720c8-ORIGIN
L_000720c8:
    mov.l r12,@-r15
    .org 0x720ca-ORIGIN
L_000720ca:
    mov.l r13,@-r15
    .org 0x720cc-ORIGIN
L_000720cc:
    mov.l r14,@-r15
    .org 0x720ce-ORIGIN
L_000720ce:
    sts.l pr,@-r15
    .org 0x720d0-ORIGIN
L_000720d0:
    sts.l macl,@-r15
    .org 0x720d2-ORIGIN
L_000720d2:
    stc.l gbr,@-r15
    .org 0x720d4-ORIGIN
L_000720d4:
    mov.l P_000722d0,r0
    .org 0x720d6-ORIGIN
L_000720d6:
    ldc r0,gbr
    .org 0x720d8-ORIGIN
L_000720d8:
    add #-0xc,r15
    .org 0x720da-ORIGIN
L_000720da:
    mov.w @(0x3e,gbr),r0
    .org 0x720dc-ORIGIN
L_000720dc:
    mov.l P_000722d4,r4
    .org 0x720de-ORIGIN
L_000720de:
    mov.w r0,@(0x2,r15)
    .org 0x720e0-ORIGIN
L_000720e0:
    mov.w @(0x1b4,gbr),r0
    .org 0x720e2-ORIGIN
L_000720e2:
    mov.l P_000722d8,r12
    .org 0x720e4-ORIGIN
L_000720e4:
    mov.l P_000722dc,r14
    .org 0x720e6-ORIGIN
L_000720e6:
    extu.w r0,r7
    .org 0x720e8-ORIGIN
L_000720e8:
    mov.l P_000722e0,r13
    .org 0x720ea-ORIGIN
L_000720ea:
    mov r12,r5
    .org 0x720ec-ORIGIN
L_000720ec:
    mov.l P_000722e4,r11
    .org 0x720ee-ORIGIN
L_000720ee:
    jsr @r13
    .org 0x720f0-ORIGIN
L_000720f0:
    mov r14,r6
    .org 0x720f2-ORIGIN
L_000720f2:
    mov r0,r2
    .org 0x720f4-ORIGIN
L_000720f4:
    mov.w P_000721fc,r0
    .org 0x720f6-ORIGIN
L_000720f6:
    mov.l P_000722e8,r4
    .org 0x720f8-ORIGIN
L_000720f8:
    mov r12,r5
    .org 0x720fa-ORIGIN
L_000720fa:
    mov.w r2,@(r0,r11)
    .org 0x720fc-ORIGIN
L_000720fc:
    mov r14,r6
    .org 0x720fe-ORIGIN
L_000720fe:
    mov.w @(0x3e,gbr),r0
    .org 0x72100-ORIGIN
L_00072100:
    mov.l P_000722ec,r12
    .org 0x72102-ORIGIN
L_00072102:
    mov.w r0,@(0x2,r15)
    .org 0x72104-ORIGIN
L_00072104:
    mov.w @(0x1b4,gbr),r0
    .org 0x72106-ORIGIN
L_00072106:
    mov.l P_000722f0,r10
    .org 0x72108-ORIGIN
L_00072108:
    jsr @r13
    .org 0x7210a-ORIGIN
L_0007210a:
    extu.w r0,r7
    .org 0x7210c-ORIGIN
L_0007210c:
    mov r0,r6
    .org 0x7210e-ORIGIN
L_0007210e:
    mov.w P_000721fe,r0
    .org 0x72110-ORIGIN
L_00072110:
    mov #0x1,r2
    .org 0x72112-ORIGIN
L_00072112:
    mov.w r6,@(r0,r11)
    .org 0x72114-ORIGIN
L_00072114:
    shll16 r2
    .org 0x72116-ORIGIN
L_00072116:
    mov.w P_00072200,r0
    .org 0x72118-ORIGIN
L_00072118:
    extu.w r6,r6
    .org 0x7211a-ORIGIN
L_0007211a:
    mov.w @(r0,r11),r5
    .org 0x7211c-ORIGIN
L_0007211c:
    mov.w P_000721fc,r0
    .org 0x7211e-ORIGIN
L_0007211e:
    extu.w r5,r7
    .org 0x72120-ORIGIN
L_00072120:
    mov.w @(r0,r11),r4
    .org 0x72122-ORIGIN
L_00072122:
    sub r7,r2
    .org 0x72124-ORIGIN
L_00072124:
    extu.w r4,r4
    .org 0x72126-ORIGIN
L_00072126:
    mul.l r2,r4
    .org 0x72128-ORIGIN
L_00072128:
    sts macl,r2
    .org 0x7212a-ORIGIN
L_0007212a:
    mul.l r7,r6
    .org 0x7212c-ORIGIN
L_0007212c:
    sts macl,r6
    .org 0x7212e-ORIGIN
L_0007212e:
    add r6,r2
    .org 0x72130-ORIGIN
L_00072130:
    shlr16 r2
    .org 0x72132-ORIGIN
L_00072132:
    extu.w r2,r13
    .org 0x72134-ORIGIN
L_00072134:
    mov r13,r0
    .org 0x72136-ORIGIN
L_00072136:
    mov.w r0,@(0x1b6,gbr)
    .org 0x72138-ORIGIN
L_00072138:
    mov #0x6b,r0
    .org 0x7213a-ORIGIN
L_0007213a:
    mov.b @(r0,r12),r14
    .org 0x7213c-ORIGIN
L_0007213c:
    mov r14,r0
    .org 0x7213e-ORIGIN
L_0007213e:
    mov.b r0,@(0x4,r15)
    .org 0x72140-ORIGIN
L_00072140:
    mov.b @r10,r0
    .org 0x72142-ORIGIN
L_00072142:
    tst #0x40,r0
    .org 0x72144-ORIGIN
L_00072144:
    bt L_000721c4
    .org 0x72146-ORIGIN
L_00072146:
    mov.l P_000722f4,r2
    .org 0x72148-ORIGIN
L_00072148:
    mov.w @(0x3e,gbr),r0
    .org 0x7214a-ORIGIN
L_0007214a:
    mov.w @r2,r6
    .org 0x7214c-ORIGIN
L_0007214c:
    cmp/hi r6,r0
    .org 0x7214e-ORIGIN
L_0007214e:
    bt L_000721a8
    .org 0x72150-ORIGIN
L_00072150:
    mov.l P_000722f8,r5
    .org 0x72152-ORIGIN
L_00072152:
    mov.b @(0x3,r5),r0
    .org 0x72154-ORIGIN
L_00072154:
    tst #0x80,r0
    .org 0x72156-ORIGIN
L_00072156:
    bf L_000721a8
    .org 0x72158-ORIGIN
L_00072158:
    mov.l P_000722fc,r5
    .org 0x7215a-ORIGIN
L_0007215a:
    mov.b @(0x2,r5),r0
    .org 0x7215c-ORIGIN
L_0007215c:
    tst #0x40,r0
    .org 0x7215e-ORIGIN
L_0007215e:
    bf L_000721a8
    .org 0x72160-ORIGIN
L_00072160:
    mov #0x14,r0
    .org 0x72162-ORIGIN
L_00072162:
    mov.b @(r0,r12),r0
    .org 0x72164-ORIGIN
L_00072164:
    tst #0x1,r0
    .org 0x72166-ORIGIN
L_00072166:
    bf L_000721a8
    .org 0x72168-ORIGIN
L_00072168:
    mov.b @(0x1,r5),r0
    .org 0x7216a-ORIGIN
L_0007216a:
    tst #0x1,r0
    .org 0x7216c-ORIGIN
L_0007216c:
    bf L_000721a8
    .org 0x7216e-ORIGIN
L_0007216e:
    mov.l P_00072300,r2
    .org 0x72170-ORIGIN
L_00072170:
    mov.w @(0x1e,gbr),r0
    .org 0x72172-ORIGIN
L_00072172:
    mov.b @r2,r6
    .org 0x72174-ORIGIN
L_00072174:
    extu.w r0,r5
    .org 0x72176-ORIGIN
L_00072176:
    mov.l P_00072304,r2
    .org 0x72178-ORIGIN
L_00072178:
    extu.b r6,r6
    .org 0x7217a-ORIGIN
L_0007217a:
    mul.l r5,r6
    .org 0x7217c-ORIGIN
L_0007217c:
    mov.b @r2,r4
    .org 0x7217e-ORIGIN
L_0007217e:
    mov #0x64,r0
    .org 0x72180-ORIGIN
L_00072180:
    mov.l P_00072308,r5
    .org 0x72182-ORIGIN
L_00072182:
    sts macl,r6
    .org 0x72184-ORIGIN
L_00072184:
    extu.b r4,r2
    .org 0x72186-ORIGIN
L_00072186:
    mov.l r2,@(0x8,r15)
    .org 0x72188-ORIGIN
L_00072188:
    jsr @r5
    .org 0x7218a-ORIGIN
L_0007218a:
    mov r6,r1
    .org 0x7218c-ORIGIN
L_0007218c:
    mov r0,r4
    .org 0x7218e-ORIGIN
L_0007218e:
    mov.w @(0x1b4,gbr),r0
    .org 0x72190-ORIGIN
L_00072190:
    mov.l @(0x8,r15),r2
    .org 0x72192-ORIGIN
L_00072192:
    extu.w r0,r5
    .org 0x72194-ORIGIN
L_00072194:
    sub r2,r4
    .org 0x72196-ORIGIN
L_00072196:
    sub r13,r5
    .org 0x72198-ORIGIN
L_00072198:
    cmp/gt r5,r4
    .org 0x7219a-ORIGIN
L_0007219a:
    bf L_0007219e
    .org 0x7219c-ORIGIN
L_0007219c:
    mov r5,r4
    .org 0x7219e-ORIGIN
L_0007219e:
    cmp/pz r4
    .org 0x721a0-ORIGIN
L_000721a0:
    bt/s L_000721aa
    .org 0x721a2-ORIGIN
L_000721a2:
    mov r4,r6
    .org 0x721a4-ORIGIN
L_000721a4:
    bra L_000721aa
    .org 0x721a6-ORIGIN
L_000721a6:
    mov #0x0,r6
    .org 0x721a8-ORIGIN
L_000721a8:
    mov #0x0,r6
    .org 0x721aa-ORIGIN
L_000721aa:
    mov.w P_00072202,r0
    .org 0x721ac-ORIGIN
L_000721ac:
    mov r13,r5
    .org 0x721ae-ORIGIN
L_000721ae:
    mov.w r6,@(r0,r11)
    .org 0x721b0-ORIGIN
L_000721b0:
    extu.w r6,r6
    .org 0x721b2-ORIGIN
L_000721b2:
    add r6,r5
    .org 0x721b4-ORIGIN
L_000721b4:
    mov #-0x1,r6
    .org 0x721b6-ORIGIN
L_000721b6:
    extu.w r6,r6
    .org 0x721b8-ORIGIN
L_000721b8:
    cmp/hi r6,r5
    .org 0x721ba-ORIGIN
L_000721ba:
    bf L_000721be
    .org 0x721bc-ORIGIN
L_000721bc:
    mov r6,r5
    .org 0x721be-ORIGIN
L_000721be:
    mov.w P_00072204,r0
    .org 0x721c0-ORIGIN
L_000721c0:
    bra L_000721c8
    .org 0x721c2-ORIGIN
L_000721c2:
    mov.w r5,@(r0,r11)
    .org 0x721c4-ORIGIN
L_000721c4:
    mov.w P_00072204,r0
    .org 0x721c6-ORIGIN
L_000721c6:
    mov.w r13,@(r0,r11)
    .org 0x721c8-ORIGIN
L_000721c8:
    mov.b @(0x4,r15),r0
    .org 0x721ca-ORIGIN
L_000721ca:
    mov r0,r2
    .org 0x721cc-ORIGIN
L_000721cc:
    and #0x4,r0
    .org 0x721ce-ORIGIN
L_000721ce:
    tst r0,r0
    .org 0x721d0-ORIGIN
L_000721d0:
    bf/s L_00072206
    .org 0x721d2-ORIGIN
L_000721d2:
    mov r0,r4
    .org 0x721d4-ORIGIN
L_000721d4:
    mov.l P_0007230c,r5
    .org 0x721d6-ORIGIN
L_000721d6:
    mov.b @r5,r0
    .org 0x721d8-ORIGIN
L_000721d8:
    tst #0x8,r0
    .org 0x721da-ORIGIN
L_000721da:
    bt L_00072206
    .org 0x721dc-ORIGIN
L_000721dc:
    mov.l P_00072310,r5
    .org 0x721de-ORIGIN
L_000721de:
    mov.b @r5,r0
    .org 0x721e0-ORIGIN
L_000721e0:
    tst #0x8,r0
    .org 0x721e2-ORIGIN
L_000721e2:
    bf L_00072206
    .org 0x721e4-ORIGIN
L_000721e4:
    mov.l P_000722fc,r5
    .org 0x721e6-ORIGIN
L_000721e6:
    mov.b @(0x1,r5),r0
    .org 0x721e8-ORIGIN
L_000721e8:
    tst #0x1,r0
    .org 0x721ea-ORIGIN
L_000721ea:
    bf L_00072206
    .org 0x721ec-ORIGIN
L_000721ec:
    mov.l P_00072314,r7
    .org 0x721ee-ORIGIN
L_000721ee:
    mov.w @(0x3e,gbr),r0
    .org 0x721f0-ORIGIN
L_000721f0:
    mov.w @r7,r6
    .org 0x721f2-ORIGIN
L_000721f2:
    cmp/hs r6,r0
    .org 0x721f4-ORIGIN
L_000721f4:
    bt L_00072206
    .org 0x721f6-ORIGIN
L_000721f6:
    mov r2,r0
    .org 0x721f8-ORIGIN
L_000721f8:
    bra L_00072238
    .org 0x721fa-ORIGIN
L_000721fa:
    or #0x4,r0
    .org 0x721fc-ORIGIN
P_000721fc:
    .byte 0x0a
    .org 0x721fd-ORIGIN
P_000721fd:
    .byte 0x2e
    .org 0x721fe-ORIGIN
P_000721fe:
    .byte 0x0a
    .org 0x721ff-ORIGIN
P_000721ff:
    .byte 0x30
    .org 0x72200-ORIGIN
P_00072200:
    .byte 0x06
    .org 0x72201-ORIGIN
P_00072201:
    .byte 0x82
    .org 0x72202-ORIGIN
P_00072202:
    .byte 0x0a
    .org 0x72203-ORIGIN
P_00072203:
    .byte 0x26
    .org 0x72204-ORIGIN
P_00072204:
    .byte 0x0a
    .org 0x72205-ORIGIN
P_00072205:
    .byte 0x28
    .org 0x72206-ORIGIN
L_00072206:
    tst r4,r4
    .org 0x72208-ORIGIN
L_00072208:
    bt L_00072240
    .org 0x7220a-ORIGIN
L_0007220a:
    mov.w @(0x1f2,gbr),r0
    .org 0x7220c-ORIGIN
L_0007220c:
    extu.w r0,r7
    .org 0x7220e-ORIGIN
L_0007220e:
    mov.w @(0x1f4,gbr),r0
    .org 0x72210-ORIGIN
L_00072210:
    extu.w r0,r5
    .org 0x72212-ORIGIN
L_00072212:
    cmp/ge r5,r7
    .org 0x72214-ORIGIN
L_00072214:
    bt L_0007221e
    .org 0x72216-ORIGIN
L_00072216:
    mov.w @(0x1b4,gbr),r0
    .org 0x72218-ORIGIN
L_00072218:
    extu.w r0,r4
    .org 0x7221a-ORIGIN
L_0007221a:
    cmp/ge r13,r4
    .org 0x7221c-ORIGIN
L_0007221c:
    bt L_00072234
    .org 0x7221e-ORIGIN
L_0007221e:
    cmp/gt r5,r7
    .org 0x72220-ORIGIN
L_00072220:
    bf L_00072240
    .org 0x72222-ORIGIN
L_00072222:
    mov.w @(0x1b4,gbr),r0
    .org 0x72224-ORIGIN
L_00072224:
    extu.w r0,r5
    .org 0x72226-ORIGIN
L_00072226:
    cmp/gt r13,r5
    .org 0x72228-ORIGIN
L_00072228:
    bt L_00072240
    .org 0x7222a-ORIGIN
L_0007222a:
    mov.l P_00072318,r4
    .org 0x7222c-ORIGIN
L_0007222c:
    mov.w @r4,r6
    .org 0x7222e-ORIGIN
L_0007222e:
    extu.w r6,r6
    .org 0x72230-ORIGIN
L_00072230:
    cmp/gt r6,r5
    .org 0x72232-ORIGIN
L_00072232:
    bt L_00072240
    .org 0x72234-ORIGIN
L_00072234:
    mov r2,r0
    .org 0x72236-ORIGIN
L_00072236:
    and #0xfb,r0
    .org 0x72238-ORIGIN
L_00072238:
    mov r0,r2
    .org 0x7223a-ORIGIN
L_0007223a:
    mov #0x6b,r0
    .org 0x7223c-ORIGIN
L_0007223c:
    mov.b r2,@(r0,r12)
    .org 0x7223e-ORIGIN
L_0007223e:
    exts.b r2,r14
    .org 0x72240-ORIGIN
L_00072240:
    mov #0x5c,r0
    .org 0x72242-ORIGIN
L_00072242:
    mov.b @(r0,r12),r4
    .org 0x72244-ORIGIN
L_00072244:
    mov r4,r0
    .org 0x72246-ORIGIN
L_00072246:
    tst #0x4,r0
    .org 0x72248-ORIGIN
L_00072248:
    movt r0
    .org 0x7224a-ORIGIN
L_0007224a:
    xor #0x1,r0
    .org 0x7224c-ORIGIN
L_0007224c:
    extu.b r0,r5
    .org 0x7224e-ORIGIN
L_0007224e:
    mov r14,r0
    .org 0x72250-ORIGIN
L_00072250:
    tst #0x4,r0
    .org 0x72252-ORIGIN
L_00072252:
    movt r0
    .org 0x72254-ORIGIN
L_00072254:
    xor #0x1,r0
    .org 0x72256-ORIGIN
L_00072256:
    extu.b r0,r6
    .org 0x72258-ORIGIN
L_00072258:
    cmp/eq r6,r5
    .org 0x7225a-ORIGIN
L_0007225a:
    bt L_00072270
    .org 0x7225c-ORIGIN
L_0007225c:
    mov r4,r0
    .org 0x7225e-ORIGIN
L_0007225e:
    and #0xfb,r0
    .org 0x72260-ORIGIN
L_00072260:
    mov r0,r2
    .org 0x72262-ORIGIN
L_00072262:
    mov #0x5c,r0
    .org 0x72264-ORIGIN
L_00072264:
    mov.b r2,@(r0,r12)
    .org 0x72266-ORIGIN
L_00072266:
    mov r14,r0
    .org 0x72268-ORIGIN
L_00072268:
    and #0xfb,r0
    .org 0x7226a-ORIGIN
L_0007226a:
    mov r0,r2
    .org 0x7226c-ORIGIN
L_0007226c:
    mov #0x6b,r0
    .org 0x7226e-ORIGIN
L_0007226e:
    mov.b r2,@(r0,r12)
    .org 0x72270-ORIGIN
L_00072270:
    mov.l P_0007231c,r5
    .org 0x72272-ORIGIN
L_00072272:
    mov #0x36,r0
    .org 0x72274-ORIGIN
L_00072274:
    mov.b @(r0,r5),r6
    .org 0x72276-ORIGIN
L_00072276:
    extu.b r6,r0
    .org 0x72278-ORIGIN
L_00072278:
    cmp/eq #0x1,r0
    .org 0x7227a-ORIGIN
L_0007227a:
    bt L_000722b0
    .org 0x7227c-ORIGIN
L_0007227c:
    cmp/eq #0x4,r0
    .org 0x7227e-ORIGIN
L_0007227e:
    bt L_000722b0
    .org 0x72280-ORIGIN
L_00072280:
    mov #0x66,r0
    .org 0x72282-ORIGIN
L_00072282:
    mov.b @(r0,r5),r0
    .org 0x72284-ORIGIN
L_00072284:
    cmp/eq #0x3,r0
    .org 0x72286-ORIGIN
L_00072286:
    bt L_000722b0
    .org 0x72288-ORIGIN
L_00072288:
    mov.b @r10,r0
    .org 0x7228a-ORIGIN
L_0007228a:
    tst #0x8,r0
    .org 0x7228c-ORIGIN
L_0007228c:
    bt L_000722b0
    .org 0x7228e-ORIGIN
L_0007228e:
    mov.l P_00072320,r6
    .org 0x72290-ORIGIN
L_00072290:
    mov.b @r6,r0
    .org 0x72292-ORIGIN
L_00072292:
    tst #0x1,r0
    .org 0x72294-ORIGIN
L_00072294:
    bf L_000722b0
    .org 0x72296-ORIGIN
L_00072296:
    mov.l P_00072324,r2
    .org 0x72298-ORIGIN
L_00072298:
    mov.b @r2,r0
    .org 0x7229a-ORIGIN
L_0007229a:
    tst #0x80,r0
    .org 0x7229c-ORIGIN
L_0007229c:
    bf L_000722b0
    .org 0x7229e-ORIGIN
L_0007229e:
    mov #0x6b,r0
    .org 0x722a0-ORIGIN
L_000722a0:
    mov.b @(r0,r12),r0
    .org 0x722a2-ORIGIN
L_000722a2:
    tst #0x4,r0
    .org 0x722a4-ORIGIN
L_000722a4:
    bt L_000722b0
    .org 0x722a6-ORIGIN
L_000722a6:
    mov.w P_000722cc,r0
    .org 0x722a8-ORIGIN
L_000722a8:
    mov.w @(r0,r11),r2
    .org 0x722aa-ORIGIN
L_000722aa:
    mov.w P_000722ce,r0
    .org 0x722ac-ORIGIN
L_000722ac:
    bra L_000722b8
    .org 0x722ae-ORIGIN
L_000722ae:
    mov.w r2,@(r0,r11)
    .org 0x722b0-ORIGIN
L_000722b0:
    mov.w @(0x1b4,gbr),r0
    .org 0x722b2-ORIGIN
L_000722b2:
    mov r0,r14
    .org 0x722b4-ORIGIN
L_000722b4:
    mov.w P_000722ce,r0
    .org 0x722b6-ORIGIN
L_000722b6:
    mov.w r14,@(r0,r11)
    .org 0x722b8-ORIGIN
L_000722b8:
    add #0xc,r15
    .org 0x722ba-ORIGIN
L_000722ba:
    ldc.l @r15+,gbr
    .org 0x722bc-ORIGIN
L_000722bc:
    lds.l @r15+,macl
    .org 0x722be-ORIGIN
L_000722be:
    lds.l @r15+,pr
    .org 0x722c0-ORIGIN
L_000722c0:
    mov.l @r15+,r14
    .org 0x722c2-ORIGIN
L_000722c2:
    mov.l @r15+,r13
    .org 0x722c4-ORIGIN
L_000722c4:
    mov.l @r15+,r12
    .org 0x722c6-ORIGIN
L_000722c6:
    mov.l @r15+,r11
    .org 0x722c8-ORIGIN
L_000722c8:
    rts
    .org 0x722ca-ORIGIN
L_000722ca:
    mov.l @r15+,r10
    .org 0x722cc-ORIGIN
P_000722cc:
    .byte 0x0a
    .org 0x722cd-ORIGIN
P_000722cd:
    .byte 0x28
    .org 0x722ce-ORIGIN
P_000722ce:
    .byte 0x0a
    .org 0x722cf-ORIGIN
P_000722cf:
    .byte 0x2a
    .org 0x722d0-ORIGIN
P_000722d0:
    .byte 0xff
    .org 0x722d1-ORIGIN
P_000722d1:
    .byte 0xff
    .org 0x722d2-ORIGIN
P_000722d2:
    .byte 0x10
    .org 0x722d3-ORIGIN
P_000722d3:
    .byte 0x94
    .org 0x722d4-ORIGIN
P_000722d4:
    .byte 0x00
    .org 0x722d5-ORIGIN
P_000722d5:
    .byte 0x01
    .org 0x722d6-ORIGIN
P_000722d6:
    .byte 0x7c
    .org 0x722d7-ORIGIN
P_000722d7:
    .byte 0xc8
    .org 0x722d8-ORIGIN
P_000722d8:
    .byte 0x00
    .org 0x722d9-ORIGIN
P_000722d9:
    .byte 0x01
    .org 0x722da-ORIGIN
P_000722da:
    .byte 0x87
    .org 0x722db-ORIGIN
P_000722db:
    .byte 0x46
    .org 0x722dc-ORIGIN
P_000722dc:
    .byte 0x00
    .org 0x722dd-ORIGIN
P_000722dd:
    .byte 0x01
    .org 0x722de-ORIGIN
P_000722de:
    .byte 0x93
    .org 0x722df-ORIGIN
P_000722df:
    .byte 0x40
    .org 0x722e0-ORIGIN
P_000722e0:
    .byte 0x00
    .org 0x722e1-ORIGIN
P_000722e1:
    .byte 0x02
    .org 0x722e2-ORIGIN
P_000722e2:
    .byte 0x66
    .org 0x722e3-ORIGIN
P_000722e3:
    .byte 0x28
    .org 0x722e4-ORIGIN
P_000722e4:
    .byte 0xff
    .org 0x722e5-ORIGIN
P_000722e5:
    .byte 0xff
    .org 0x722e6-ORIGIN
P_000722e6:
    .byte 0x12
    .org 0x722e7-ORIGIN
P_000722e7:
    .byte 0x8c
    .org 0x722e8-ORIGIN
P_000722e8:
    .byte 0x00
    .org 0x722e9-ORIGIN
P_000722e9:
    .byte 0x01
    .org 0x722ea-ORIGIN
P_000722ea:
    .byte 0x7e
    .org 0x722eb-ORIGIN
P_000722eb:
    .byte 0xc8
    .org 0x722ec-ORIGIN
P_000722ec:
    .byte 0xff
    .org 0x722ed-ORIGIN
P_000722ed:
    .byte 0xff
    .org 0x722ee-ORIGIN
P_000722ee:
    .byte 0x41
    .org 0x722ef-ORIGIN
P_000722ef:
    .byte 0xa9
    .org 0x722f0-ORIGIN
P_000722f0:
    .byte 0x00
    .org 0x722f1-ORIGIN
P_000722f1:
    .byte 0x00
    .org 0x722f2-ORIGIN
P_000722f2:
    .byte 0x89
    .org 0x722f3-ORIGIN
P_000722f3:
    .byte 0xfb
    .org 0x722f4-ORIGIN
P_000722f4:
    .byte 0x00
    .org 0x722f5-ORIGIN
P_000722f5:
    .byte 0x01
    .org 0x722f6-ORIGIN
P_000722f6:
    .byte 0x63
    .org 0x722f7-ORIGIN
P_000722f7:
    .byte 0x38
    .org 0x722f8-ORIGIN
P_000722f8:
    .byte 0xff
    .org 0x722f9-ORIGIN
P_000722f9:
    .byte 0xff
    .org 0x722fa-ORIGIN
P_000722fa:
    .byte 0x24
    .org 0x722fb-ORIGIN
P_000722fb:
    .byte 0x4c
    .org 0x722fc-ORIGIN
P_000722fc:
    .byte 0xff
    .org 0x722fd-ORIGIN
P_000722fd:
    .byte 0xff
    .org 0x722fe-ORIGIN
P_000722fe:
    .byte 0x24
    .org 0x722ff-ORIGIN
P_000722ff:
    .byte 0x5c
    .org 0x72300-ORIGIN
P_00072300:
    .byte 0x00
    .org 0x72301-ORIGIN
P_00072301:
    .byte 0x01
    .org 0x72302-ORIGIN
P_00072302:
    .byte 0x5f
    .org 0x72303-ORIGIN
P_00072303:
    .byte 0x69
    .org 0x72304-ORIGIN
P_00072304:
    .byte 0x00
    .org 0x72305-ORIGIN
P_00072305:
    .byte 0x01
    .org 0x72306-ORIGIN
P_00072306:
    .byte 0x5f
    .org 0x72307-ORIGIN
P_00072307:
    .byte 0x55
    .org 0x72308-ORIGIN
P_00072308:
    .byte 0x00
    .org 0x72309-ORIGIN
P_00072309:
    .byte 0x02
    .org 0x7230a-ORIGIN
P_0007230a:
    .byte 0x1b
    .org 0x7230b-ORIGIN
P_0007230b:
    .byte 0xbc
    .org 0x7230c-ORIGIN
P_0007230c:
    .byte 0xff
    .org 0x7230d-ORIGIN
P_0007230d:
    .byte 0xff
    .org 0x7230e-ORIGIN
P_0007230e:
    .byte 0x41
    .org 0x7230f-ORIGIN
P_0007230f:
    .byte 0x80
    .org 0x72310-ORIGIN
P_00072310:
    .byte 0xff
    .org 0x72311-ORIGIN
P_00072311:
    .byte 0xff
    .org 0x72312-ORIGIN
P_00072312:
    .byte 0x41
    .org 0x72313-ORIGIN
P_00072313:
    .byte 0x7e
    .org 0x72314-ORIGIN
P_00072314:
    .byte 0x00
    .org 0x72315-ORIGIN
P_00072315:
    .byte 0x01
    .org 0x72316-ORIGIN
P_00072316:
    .byte 0x5f
    .org 0x72317-ORIGIN
P_00072317:
    .byte 0x9a
    .org 0x72318-ORIGIN
P_00072318:
    .byte 0x00
    .org 0x72319-ORIGIN
P_00072319:
    .byte 0x01
    .org 0x7231a-ORIGIN
P_0007231a:
    .byte 0x5f
    .org 0x7231b-ORIGIN
P_0007231b:
    .byte 0x9c
    .org 0x7231c-ORIGIN
P_0007231c:
    .byte 0xff
    .org 0x7231d-ORIGIN
P_0007231d:
    .byte 0xff
    .org 0x7231e-ORIGIN
P_0007231e:
    .byte 0x26
    .org 0x7231f-ORIGIN
P_0007231f:
    .byte 0x7a
    .org 0x72320-ORIGIN
P_00072320:
    .byte 0x00
    .org 0x72321-ORIGIN
P_00072321:
    .byte 0x00
    .org 0x72322-ORIGIN
P_00072322:
    .byte 0x89
    .org 0x72323-ORIGIN
P_00072323:
    .byte 0xfa
    .org 0x72324-ORIGIN
P_00072324:
    .byte 0x00
    .org 0x72325-ORIGIN
P_00072325:
    .byte 0x00
    .org 0x72326-ORIGIN
P_00072326:
    .byte 0x8b
    .org 0x72327-ORIGIN
P_00072327:
    .byte 0x3f
