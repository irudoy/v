! Exact constant-root byte-curve callers and real interpolation/signed-division helper closure.
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
    .org 0x26370-ORIGIN
L_00026370:
    mov.w P_00026382,r0
    .org 0x26372-ORIGIN
L_00026372:
    extu.b r5,r5
    .org 0x26374-ORIGIN
L_00026374:
    cmp/hs r0,r5
    .org 0x26376-ORIGIN
L_00026376:
    bt L_0002637e
    .org 0x26378-ORIGIN
L_00026378:
    mov.l P_00026384,r6
    .org 0x2637a-ORIGIN
L_0002637a:
    jmp @r6
    .org 0x2637c-ORIGIN
L_0002637c:
    mov #0x0,r3
    .org 0x2637e-ORIGIN
L_0002637e:
    rts
    .org 0x26380-ORIGIN
L_00026380:
    mov.b @(0x7,r4),r0
    .org 0x26382-ORIGIN
P_00026382:
    .byte 0x00
    .org 0x26383-ORIGIN
P_00026383:
    .byte 0xe0
    .org 0x26384-ORIGIN
P_00026384:
    .byte 0x00
    .org 0x26385-ORIGIN
P_00026385:
    .byte 0x02
    .org 0x26386-ORIGIN
P_00026386:
    .byte 0x6a
    .org 0x26387-ORIGIN
P_00026387:
    .byte 0x80
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
    .byte 0x00
    .org 0x26abd-ORIGIN
P_00026abd:
    .byte 0x02
    .org 0x26abe-ORIGIN
P_00026abe:
    .byte 0x67
    .org 0x26abf-ORIGIN
P_00026abf:
    .byte 0x40
    .org 0x2c59c-ORIGIN
L_0002c59c:
    sts.l pr,@-r15
    .org 0x2c59e-ORIGIN
L_0002c59e:
    stc.l gbr,@-r15
    .org 0x2c5a0-ORIGIN
L_0002c5a0:
    mov.l P_0002c7fc,r0
    .org 0x2c5a2-ORIGIN
L_0002c5a2:
    ldc r0,gbr
    .org 0x2c5a4-ORIGIN
L_0002c5a4:
    mov.l P_0002c7dc,r5
    .org 0x2c5a6-ORIGIN
L_0002c5a6:
    mov.l P_0002c800,r4
    .org 0x2c5a8-ORIGIN
L_0002c5a8:
    mov.b @(0x5,r5),r0
    .org 0x2c5aa-ORIGIN
L_0002c5aa:
    mov.l P_0002c804,r2
    .org 0x2c5ac-ORIGIN
L_0002c5ac:
    jsr @r2
    .org 0x2c5ae-ORIGIN
L_0002c5ae:
    extu.b r0,r5
    .org 0x2c5b0-ORIGIN
L_0002c5b0:
    mov.b r0,@(0xd4,gbr)
    .org 0x2c5b2-ORIGIN
L_0002c5b2:
    extu.b r0,r0
    .org 0x2c5b4-ORIGIN
L_0002c5b4:
    shll8 r0
    .org 0x2c5b6-ORIGIN
L_0002c5b6:
    mov.w r0,@(0x4,gbr)
    .org 0x2c5b8-ORIGIN
L_0002c5b8:
    ldc.l @r15+,gbr
    .org 0x2c5ba-ORIGIN
L_0002c5ba:
    lds.l @r15+,pr
    .org 0x2c5bc-ORIGIN
L_0002c5bc:
    rts
    .org 0x2c5be-ORIGIN
L_0002c5be:
    nop
    .org 0x2c7dc-ORIGIN
P_0002c7dc:
    .byte 0xff
    .org 0x2c7dd-ORIGIN
P_0002c7dd:
    .byte 0xff
    .org 0x2c7de-ORIGIN
P_0002c7de:
    .byte 0x10
    .org 0x2c7df-ORIGIN
P_0002c7df:
    .byte 0x72
    .org 0x2c7fc-ORIGIN
P_0002c7fc:
    .byte 0xff
    .org 0x2c7fd-ORIGIN
P_0002c7fd:
    .byte 0xff
    .org 0x2c7fe-ORIGIN
P_0002c7fe:
    .byte 0x1e
    .org 0x2c7ff-ORIGIN
P_0002c7ff:
    .byte 0x50
    .org 0x2c800-ORIGIN
P_0002c800:
    .byte 0x00
    .org 0x2c801-ORIGIN
P_0002c801:
    .byte 0x01
    .org 0x2c802-ORIGIN
P_0002c802:
    .byte 0x23
    .org 0x2c803-ORIGIN
P_0002c803:
    .byte 0x32
    .org 0x2c804-ORIGIN
P_0002c804:
    .byte 0x00
    .org 0x2c805-ORIGIN
P_0002c805:
    .byte 0x02
    .org 0x2c806-ORIGIN
P_0002c806:
    .byte 0x63
    .org 0x2c807-ORIGIN
P_0002c807:
    .byte 0x70
    .org 0x6e3d8-ORIGIN
L_0006e3d8:
    sts.l pr,@-r15
    .org 0x6e3da-ORIGIN
L_0006e3da:
    sts.l macl,@-r15
    .org 0x6e3dc-ORIGIN
L_0006e3dc:
    mov.l P_0006e5cc,r6
    .org 0x6e3de-ORIGIN
L_0006e3de:
    mov.b @r6,r0
    .org 0x6e3e0-ORIGIN
L_0006e3e0:
    tst #0x2,r0
    .org 0x6e3e2-ORIGIN
L_0006e3e2:
    bt L_0006e3f4
    .org 0x6e3e4-ORIGIN
L_0006e3e4:
    mov.l P_0006e5d0,r5
    .org 0x6e3e6-ORIGIN
L_0006e3e6:
    mov.l P_0006e5d4,r4
    .org 0x6e3e8-ORIGIN
L_0006e3e8:
    mov.b @(0x5,r5),r0
    .org 0x6e3ea-ORIGIN
L_0006e3ea:
    mov.l P_0006e5d8,r2
    .org 0x6e3ec-ORIGIN
L_0006e3ec:
    jsr @r2
    .org 0x6e3ee-ORIGIN
L_0006e3ee:
    extu.b r0,r5
    .org 0x6e3f0-ORIGIN
L_0006e3f0:
    bra L_0006e436
    .org 0x6e3f2-ORIGIN
L_0006e3f2:
    mov r0,r2
    .org 0x6e3f4-ORIGIN
L_0006e3f4:
    mov.l P_0006e5c4,r7
    .org 0x6e3f6-ORIGIN
L_0006e3f6:
    mov.w P_0006e4dc,r0
    .org 0x6e3f8-ORIGIN
L_0006e3f8:
    mov.b @(r0,r7),r2
    .org 0x6e3fa-ORIGIN
L_0006e3fa:
    tst r2,r2
    .org 0x6e3fc-ORIGIN
L_0006e3fc:
    bf L_0006e402
    .org 0x6e3fe-ORIGIN
L_0006e3fe:
    bra L_0006e438
    .org 0x6e400-ORIGIN
L_0006e400:
    mov #-0x1,r2
    .org 0x6e402-ORIGIN
L_0006e402:
    mov.l P_0006e5d0,r5
    .org 0x6e404-ORIGIN
L_0006e404:
    mov.l P_0006e5d4,r4
    .org 0x6e406-ORIGIN
L_0006e406:
    mov.b @(0x5,r5),r0
    .org 0x6e408-ORIGIN
L_0006e408:
    mov.l P_0006e5d8,r2
    .org 0x6e40a-ORIGIN
L_0006e40a:
    jsr @r2
    .org 0x6e40c-ORIGIN
L_0006e40c:
    extu.b r0,r5
    .org 0x6e40e-ORIGIN
L_0006e40e:
    extu.b r0,r6
    .org 0x6e410-ORIGIN
L_0006e410:
    mov.l P_0006e5c4,r7
    .org 0x6e412-ORIGIN
L_0006e412:
    mov.w P_0006e4e0,r0
    .org 0x6e414-ORIGIN
L_0006e414:
    mov.b @(r0,r7),r2
    .org 0x6e416-ORIGIN
L_0006e416:
    mov.w P_0006e4dc,r0
    .org 0x6e418-ORIGIN
L_0006e418:
    extu.b r2,r2
    .org 0x6e41a-ORIGIN
L_0006e41a:
    mul.l r6,r2
    .org 0x6e41c-ORIGIN
L_0006e41c:
    mov.b @(r0,r7),r5
    .org 0x6e41e-ORIGIN
L_0006e41e:
    mov.l P_0006e5dc,r6
    .org 0x6e420-ORIGIN
L_0006e420:
    sts macl,r1
    .org 0x6e422-ORIGIN
L_0006e422:
    extu.b r5,r4
    .org 0x6e424-ORIGIN
L_0006e424:
    mov r4,r5
    .org 0x6e426-ORIGIN
L_0006e426:
    jsr @r6
    .org 0x6e428-ORIGIN
L_0006e428:
    mov r4,r0
    .org 0x6e42a-ORIGIN
L_0006e42a:
    mov #-0x1,r5
    .org 0x6e42c-ORIGIN
L_0006e42c:
    extu.w r0,r6
    .org 0x6e42e-ORIGIN
L_0006e42e:
    extu.b r5,r2
    .org 0x6e430-ORIGIN
L_0006e430:
    cmp/gt r2,r6
    .org 0x6e432-ORIGIN
L_0006e432:
    bt L_0006e436
    .org 0x6e434-ORIGIN
L_0006e434:
    mov r6,r2
    .org 0x6e436-ORIGIN
L_0006e436:
    mov.l P_0006e5c4,r7
    .org 0x6e438-ORIGIN
L_0006e438:
    mov.w P_0006e4e2,r0
    .org 0x6e43a-ORIGIN
L_0006e43a:
    lds.l @r15+,macl
    .org 0x6e43c-ORIGIN
L_0006e43c:
    lds.l @r15+,pr
    .org 0x6e43e-ORIGIN
L_0006e43e:
    rts
    .org 0x6e440-ORIGIN
L_0006e440:
    mov.b r2,@(r0,r7)
    .org 0x6e4dc-ORIGIN
P_0006e4dc:
    .byte 0x04
    .org 0x6e4dd-ORIGIN
P_0006e4dd:
    .byte 0x25
    .org 0x6e4e0-ORIGIN
P_0006e4e0:
    .byte 0x04
    .org 0x6e4e1-ORIGIN
P_0006e4e1:
    .byte 0x22
    .org 0x6e4e2-ORIGIN
P_0006e4e2:
    .byte 0x04
    .org 0x6e4e3-ORIGIN
P_0006e4e3:
    .byte 0xda
    .org 0x6e5c4-ORIGIN
P_0006e5c4:
    .byte 0xff
    .org 0x6e5c5-ORIGIN
P_0006e5c5:
    .byte 0xff
    .org 0x6e5c6-ORIGIN
P_0006e5c6:
    .byte 0x12
    .org 0x6e5c7-ORIGIN
P_0006e5c7:
    .byte 0x8c
    .org 0x6e5cc-ORIGIN
P_0006e5cc:
    .byte 0xff
    .org 0x6e5cd-ORIGIN
P_0006e5cd:
    .byte 0xff
    .org 0x6e5ce-ORIGIN
P_0006e5ce:
    .byte 0x24
    .org 0x6e5cf-ORIGIN
P_0006e5cf:
    .byte 0x4f
    .org 0x6e5d0-ORIGIN
P_0006e5d0:
    .byte 0xff
    .org 0x6e5d1-ORIGIN
P_0006e5d1:
    .byte 0xff
    .org 0x6e5d2-ORIGIN
P_0006e5d2:
    .byte 0x10
    .org 0x6e5d3-ORIGIN
P_0006e5d3:
    .byte 0x6a
    .org 0x6e5d4-ORIGIN
P_0006e5d4:
    .byte 0x00
    .org 0x6e5d5-ORIGIN
P_0006e5d5:
    .byte 0x01
    .org 0x6e5d6-ORIGIN
P_0006e5d6:
    .byte 0x29
    .org 0x6e5d7-ORIGIN
P_0006e5d7:
    .byte 0x6c
    .org 0x6e5d8-ORIGIN
P_0006e5d8:
    .byte 0x00
    .org 0x6e5d9-ORIGIN
P_0006e5d9:
    .byte 0x02
    .org 0x6e5da-ORIGIN
P_0006e5da:
    .byte 0x63
    .org 0x6e5db-ORIGIN
P_0006e5db:
    .byte 0x70
    .org 0x6e5dc-ORIGIN
P_0006e5dc:
    .byte 0x00
    .org 0x6e5dd-ORIGIN
P_0006e5dd:
    .byte 0x02
    .org 0x6e5de-ORIGIN
P_0006e5de:
    .byte 0x1b
    .org 0x6e5df-ORIGIN
P_0006e5df:
    .byte 0xbc
