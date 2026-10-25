! Complete natural paired curve-normalization callers and exact real signed division and byte interpolation helpers.
    .text
    .balign 4
    .set ORIGIN,0x8710
    .org 0x8710-ORIGIN
P_00008710:
    .byte 0x7c
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
    .org 0x264a0-ORIGIN
L_000264a0:
    sts.l pr,@-r15
    .org 0x264a2-ORIGIN
L_000264a2:
    mov.l r4,@-r15
    .org 0x264a4-ORIGIN
L_000264a4:
    mov r5,r0
    .org 0x264a6-ORIGIN
L_000264a6:
    extu.b r6,r5
    .org 0x264a8-ORIGIN
L_000264a8:
    mov.l P_000264c8,r7
    .org 0x264aa-ORIGIN
L_000264aa:
    jsr @r7
    .org 0x264ac-ORIGIN
L_000264ac:
    mov #0xf,r4
    .org 0x264ae-ORIGIN
L_000264ae:
    mov.l @r15+,r6
    .org 0x264b0-ORIGIN
L_000264b0:
    add r4,r6
    .org 0x264b2-ORIGIN
L_000264b2:
    mov.b @(0x1,r6),r0
    .org 0x264b4-ORIGIN
L_000264b4:
    extu.b r0,r2
    .org 0x264b6-ORIGIN
L_000264b6:
    mov r5,r3
    .org 0x264b8-ORIGIN
L_000264b8:
    mov.b @r6,r1
    .org 0x264ba-ORIGIN
L_000264ba:
    lds.l @r15+,pr
    .org 0x264bc-ORIGIN
L_000264bc:
    mov.l P_000264c4,r6
    .org 0x264be-ORIGIN
L_000264be:
    jmp @r6
    .org 0x264c0-ORIGIN
L_000264c0:
    extu.b r1,r0
    .org 0x264c4-ORIGIN
P_000264c4:
    .byte 0x00
    .org 0x264c5-ORIGIN
P_000264c5:
    .byte 0x02
    .org 0x264c6-ORIGIN
P_000264c6:
    .byte 0x67
    .org 0x264c7-ORIGIN
P_000264c7:
    .byte 0x40
    .org 0x264c8-ORIGIN
P_000264c8:
    .byte 0x00
    .org 0x264c9-ORIGIN
P_000264c9:
    .byte 0x02
    .org 0x264ca-ORIGIN
P_000264ca:
    .byte 0x69
    .org 0x264cb-ORIGIN
P_000264cb:
    .byte 0x44
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
    mov.l P_00026980,r2
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
P_00026980:
    .byte 0x00
    .org 0x26981-ORIGIN
P_00026981:
    .byte 0x02
    .org 0x26982-ORIGIN
P_00026982:
    .byte 0x6c
    .org 0x26983-ORIGIN
P_00026983:
    .byte 0x78
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
    .org 0x655b4-ORIGIN
L_000655b4:
    mov.l r12,@-r15
    .org 0x655b6-ORIGIN
L_000655b6:
    mov.l r14,@-r15
    .org 0x655b8-ORIGIN
L_000655b8:
    sts.l pr,@-r15
    .org 0x655ba-ORIGIN
L_000655ba:
    sts.l macl,@-r15
    .org 0x655bc-ORIGIN
L_000655bc:
    stc.l gbr,@-r15
    .org 0x655be-ORIGIN
L_000655be:
    mov.l P_0006582c,r0
    .org 0x655c0-ORIGIN
L_000655c0:
    ldc r0,gbr
    .org 0x655c2-ORIGIN
L_000655c2:
    add #-0x8,r15
    .org 0x655c4-ORIGIN
L_000655c4:
    mov.l P_00065830,r6
    .org 0x655c6-ORIGIN
L_000655c6:
    mov.b @r6,r0
    .org 0x655c8-ORIGIN
L_000655c8:
    tst #0x20,r0
    .org 0x655ca-ORIGIN
L_000655ca:
    bf L_00065660
    .org 0x655cc-ORIGIN
L_000655cc:
    mov.b @(0x53,gbr),r0
    .org 0x655ce-ORIGIN
L_000655ce:
    mov.l P_00065834,r7
    .org 0x655d0-ORIGIN
L_000655d0:
    extu.b r0,r6
    .org 0x655d2-ORIGIN
L_000655d2:
    mov.l P_0006582c,r12
    .org 0x655d4-ORIGIN
L_000655d4:
    mov #0x35,r0
    .org 0x655d6-ORIGIN
L_000655d6:
    mov.b @(r0,r7),r2
    .org 0x655d8-ORIGIN
L_000655d8:
    mov #0x48,r0
    .org 0x655da-ORIGIN
L_000655da:
    mov.b @(r0,r7),r5
    .org 0x655dc-ORIGIN
L_000655dc:
    mov.w P_00065702,r0
    .org 0x655de-ORIGIN
L_000655de:
    sub r5,r2
    .org 0x655e0-ORIGIN
L_000655e0:
    sub r6,r2
    .org 0x655e2-ORIGIN
L_000655e2:
    mov.b @(r0,r12),r6
    .org 0x655e4-ORIGIN
L_000655e4:
    extu.b r6,r6
    .org 0x655e6-ORIGIN
L_000655e6:
    sub r6,r2
    .org 0x655e8-ORIGIN
L_000655e8:
    cmp/pz r2
    .org 0x655ea-ORIGIN
L_000655ea:
    bt/s L_000655f0
    .org 0x655ec-ORIGIN
L_000655ec:
    mov r2,r6
    .org 0x655ee-ORIGIN
L_000655ee:
    mov #0x0,r6
    .org 0x655f0-ORIGIN
L_000655f0:
    mov #-0x1,r14
    .org 0x655f2-ORIGIN
L_000655f2:
    exts.w r6,r6
    .org 0x655f4-ORIGIN
L_000655f4:
    extu.b r14,r14
    .org 0x655f6-ORIGIN
L_000655f6:
    cmp/gt r14,r6
    .org 0x655f8-ORIGIN
L_000655f8:
    bf L_000655fc
    .org 0x655fa-ORIGIN
L_000655fa:
    mov r14,r6
    .org 0x655fc-ORIGIN
L_000655fc:
    mov.l P_00065838,r4
    .org 0x655fe-ORIGIN
L_000655fe:
    mov.l P_0006583c,r5
    .org 0x65600-ORIGIN
L_00065600:
    mov.l P_00065840,r2
    .org 0x65602-ORIGIN
L_00065602:
    mov.b r6,@r15
    .org 0x65604-ORIGIN
L_00065604:
    jsr @r2
    .org 0x65606-ORIGIN
L_00065606:
    extu.b r6,r6
    .org 0x65608-ORIGIN
L_00065608:
    mov.b r0,@(0x4,r15)
    .org 0x6560a-ORIGIN
L_0006560a:
    mov.b @(0x53,gbr),r0
    .org 0x6560c-ORIGIN
L_0006560c:
    mov.l P_00065844,r7
    .org 0x6560e-ORIGIN
L_0006560e:
    extu.b r0,r5
    .org 0x65610-ORIGIN
L_00065610:
    mov.w P_00065702,r0
    .org 0x65612-ORIGIN
L_00065612:
    mov.b @r15,r6
    .org 0x65614-ORIGIN
L_00065614:
    mov.b @(r0,r12),r2
    .org 0x65616-ORIGIN
L_00065616:
    mov #0x26,r0
    .org 0x65618-ORIGIN
L_00065618:
    mov.b @(r0,r7),r4
    .org 0x6561a-ORIGIN
L_0006561a:
    extu.b r6,r6
    .org 0x6561c-ORIGIN
L_0006561c:
    extu.b r2,r2
    .org 0x6561e-ORIGIN
L_0006561e:
    add r4,r6
    .org 0x65620-ORIGIN
L_00065620:
    add r5,r6
    .org 0x65622-ORIGIN
L_00065622:
    add r2,r6
    .org 0x65624-ORIGIN
L_00065624:
    cmp/pz r6
    .org 0x65626-ORIGIN
L_00065626:
    bt/s L_0006562c
    .org 0x65628-ORIGIN
L_00065628:
    mov r6,r2
    .org 0x6562a-ORIGIN
L_0006562a:
    mov #0x0,r2
    .org 0x6562c-ORIGIN
L_0006562c:
    exts.w r2,r6
    .org 0x6562e-ORIGIN
L_0006562e:
    cmp/gt r14,r6
    .org 0x65630-ORIGIN
L_00065630:
    bf L_00065634
    .org 0x65632-ORIGIN
L_00065632:
    mov r14,r6
    .org 0x65634-ORIGIN
L_00065634:
    mov.l P_00065838,r4
    .org 0x65636-ORIGIN
L_00065636:
    mov.l P_0006583c,r5
    .org 0x65638-ORIGIN
L_00065638:
    mov.l P_00065840,r2
    .org 0x6563a-ORIGIN
L_0006563a:
    jsr @r2
    .org 0x6563c-ORIGIN
L_0006563c:
    extu.b r6,r6
    .org 0x6563e-ORIGIN
L_0006563e:
    extu.b r0,r5
    .org 0x65640-ORIGIN
L_00065640:
    mov.b @(0x4,r15),r0
    .org 0x65642-ORIGIN
L_00065642:
    mov #0x1,r6
    .org 0x65644-ORIGIN
L_00065644:
    extu.b r0,r7
    .org 0x65646-ORIGIN
L_00065646:
    mov.w P_00065704,r0
    .org 0x65648-ORIGIN
L_00065648:
    shll8 r6
    .org 0x6564a-ORIGIN
L_0006564a:
    mov r6,r2
    .org 0x6564c-ORIGIN
L_0006564c:
    sub r5,r2
    .org 0x6564e-ORIGIN
L_0006564e:
    mov.w @(r0,r12),r5
    .org 0x65650-ORIGIN
L_00065650:
    sub r7,r6
    .org 0x65652-ORIGIN
L_00065652:
    mov r6,r0
    .org 0x65654-ORIGIN
L_00065654:
    mul.l r5,r2
    .org 0x65656-ORIGIN
L_00065656:
    mov.l P_00065848,r5
    .org 0x65658-ORIGIN
L_00065658:
    jsr @r5
    .org 0x6565a-ORIGIN
L_0006565a:
    sts macl,r1
    .org 0x6565c-ORIGIN
L_0006565c:
    bra L_000656de
    .org 0x6565e-ORIGIN
L_0006565e:
    mov r0,r2
    .org 0x65660-ORIGIN
L_00065660:
    mov.l P_00065844,r7
    .org 0x65662-ORIGIN
L_00065662:
    mov.w @(0x4,r7),r0
    .org 0x65664-ORIGIN
L_00065664:
    mov r0,r4
    .org 0x65666-ORIGIN
L_00065666:
    mov.w @(0x2,r7),r0
    .org 0x65668-ORIGIN
L_00065668:
    cmp/eq r4,r0
    .org 0x6566a-ORIGIN
L_0006566a:
    bf L_00065674
    .org 0x6566c-ORIGIN
L_0006566c:
    mov.l P_0006582c,r12
    .org 0x6566e-ORIGIN
L_0006566e:
    mov.w P_00065706,r0
    .org 0x65670-ORIGIN
L_00065670:
    bra L_000656de
    .org 0x65672-ORIGIN
L_00065672:
    mov.w @(r0,r12),r2
    .org 0x65674-ORIGIN
L_00065674:
    mov.l P_00065834,r7
    .org 0x65676-ORIGIN
L_00065676:
    mov #0x26,r0
    .org 0x65678-ORIGIN
L_00065678:
    mov.l P_0006584c,r2
    .org 0x6567a-ORIGIN
L_0006567a:
    mov.b @(r0,r7),r6
    .org 0x6567c-ORIGIN
L_0006567c:
    mov #0x1b,r0
    .org 0x6567e-ORIGIN
L_0006567e:
    mov.b @(r0,r2),r5
    .org 0x65680-ORIGIN
L_00065680:
    add r6,r4
    .org 0x65682-ORIGIN
L_00065682:
    extu.b r5,r5
    .org 0x65684-ORIGIN
L_00065684:
    exts.w r5,r6
    .org 0x65686-ORIGIN
L_00065686:
    neg r6,r2
    .org 0x65688-ORIGIN
L_00065688:
    cmp/gt r2,r4
    .org 0x6568a-ORIGIN
L_0006568a:
    bf L_00065692
    .org 0x6568c-ORIGIN
L_0006568c:
    exts.w r5,r5
    .org 0x6568e-ORIGIN
L_0006568e:
    bra L_00065694
    .org 0x65690-ORIGIN
L_00065690:
    neg r5,r6
    .org 0x65692-ORIGIN
L_00065692:
    mov r4,r6
    .org 0x65694-ORIGIN
L_00065694:
    mov #0x48,r0
    .org 0x65696-ORIGIN
L_00065696:
    mov.b @(r0,r7),r2
    .org 0x65698-ORIGIN
L_00065698:
    mov #0x35,r0
    .org 0x6569a-ORIGIN
L_0006569a:
    add r2,r6
    .org 0x6569c-ORIGIN
L_0006569c:
    mov.b @(r0,r7),r2
    .org 0x6569e-ORIGIN
L_0006569e:
    sub r6,r2
    .org 0x656a0-ORIGIN
L_000656a0:
    cmp/pz r2
    .org 0x656a2-ORIGIN
L_000656a2:
    bt/s L_000656a8
    .org 0x656a4-ORIGIN
L_000656a4:
    mov r2,r6
    .org 0x656a6-ORIGIN
L_000656a6:
    mov #0x0,r6
    .org 0x656a8-ORIGIN
L_000656a8:
    mov #-0x1,r14
    .org 0x656aa-ORIGIN
L_000656aa:
    extu.b r14,r14
    .org 0x656ac-ORIGIN
L_000656ac:
    cmp/gt r14,r6
    .org 0x656ae-ORIGIN
L_000656ae:
    bf L_000656b2
    .org 0x656b0-ORIGIN
L_000656b0:
    mov r14,r6
    .org 0x656b2-ORIGIN
L_000656b2:
    mov.l P_00065838,r4
    .org 0x656b4-ORIGIN
L_000656b4:
    mov.l P_0006583c,r5
    .org 0x656b6-ORIGIN
L_000656b6:
    mov.l P_00065840,r2
    .org 0x656b8-ORIGIN
L_000656b8:
    mov.l P_0006582c,r12
    .org 0x656ba-ORIGIN
L_000656ba:
    jsr @r2
    .org 0x656bc-ORIGIN
L_000656bc:
    extu.b r6,r6
    .org 0x656be-ORIGIN
L_000656be:
    extu.b r0,r6
    .org 0x656c0-ORIGIN
L_000656c0:
    mov.w P_00065704,r0
    .org 0x656c2-ORIGIN
L_000656c2:
    mov #0x1,r2
    .org 0x656c4-ORIGIN
L_000656c4:
    shll8 r2
    .org 0x656c6-ORIGIN
L_000656c6:
    sub r6,r2
    .org 0x656c8-ORIGIN
L_000656c8:
    mov.w @(r0,r12),r6
    .org 0x656ca-ORIGIN
L_000656ca:
    mul.l r6,r2
    .org 0x656cc-ORIGIN
L_000656cc:
    sts macl,r2
    .org 0x656ce-ORIGIN
L_000656ce:
    cmp/pz r2
    .org 0x656d0-ORIGIN
L_000656d0:
    bt L_000656d4
    .org 0x656d2-ORIGIN
L_000656d2:
    add r14,r2
    .org 0x656d4-ORIGIN
L_000656d4:
    mov r2,r6
    .org 0x656d6-ORIGIN
L_000656d6:
    shlr8 r6
    .org 0x656d8-ORIGIN
L_000656d8:
    swap.w r6,r2
    .org 0x656da-ORIGIN
L_000656da:
    exts.b r2,r6
    .org 0x656dc-ORIGIN
L_000656dc:
    xtrct r6,r2
    .org 0x656de-ORIGIN
L_000656de:
    mov.w P_00065708,r6
    .org 0x656e0-ORIGIN
L_000656e0:
    cmp/gt r6,r2
    .org 0x656e2-ORIGIN
L_000656e2:
    bt L_000656e6
    .org 0x656e4-ORIGIN
L_000656e4:
    mov r2,r6
    .org 0x656e6-ORIGIN
L_000656e6:
    mov #-0x80,r2
    .org 0x656e8-ORIGIN
L_000656e8:
    shll8 r2
    .org 0x656ea-ORIGIN
L_000656ea:
    cmp/ge r2,r6
    .org 0x656ec-ORIGIN
L_000656ec:
    bf L_000656f0
    .org 0x656ee-ORIGIN
L_000656ee:
    mov r6,r2
    .org 0x656f0-ORIGIN
L_000656f0:
    mov.w P_0006570a,r0
    .org 0x656f2-ORIGIN
L_000656f2:
    mov.w r2,@(r0,r12)
    .org 0x656f4-ORIGIN
L_000656f4:
    add #0x8,r15
    .org 0x656f6-ORIGIN
L_000656f6:
    ldc.l @r15+,gbr
    .org 0x656f8-ORIGIN
L_000656f8:
    lds.l @r15+,macl
    .org 0x656fa-ORIGIN
L_000656fa:
    lds.l @r15+,pr
    .org 0x656fc-ORIGIN
L_000656fc:
    mov.l @r15+,r14
    .org 0x656fe-ORIGIN
L_000656fe:
    rts
    .org 0x65700-ORIGIN
L_00065700:
    mov.l @r15+,r12
    .org 0x65702-ORIGIN
P_00065702:
    .byte 0x03
    .org 0x65703-ORIGIN
P_00065703:
    .byte 0x5e
    .org 0x65704-ORIGIN
P_00065704:
    .byte 0x06
    .org 0x65705-ORIGIN
P_00065705:
    .byte 0x40
    .org 0x65706-ORIGIN
P_00065706:
    .byte 0x06
    .org 0x65707-ORIGIN
P_00065707:
    .byte 0x42
    .org 0x65708-ORIGIN
P_00065708:
    .byte 0x7f
    .org 0x65709-ORIGIN
P_00065709:
    .byte 0xff
    .org 0x6570a-ORIGIN
P_0006570a:
    .byte 0x06
    .org 0x6570b-ORIGIN
P_0006570b:
    .byte 0x48
    .org 0x6582c-ORIGIN
P_0006582c:
    .byte 0xff
    .org 0x6582d-ORIGIN
P_0006582d:
    .byte 0xff
    .org 0x6582e-ORIGIN
P_0006582e:
    .byte 0x12
    .org 0x6582f-ORIGIN
P_0006582f:
    .byte 0x8c
    .org 0x65830-ORIGIN
P_00065830:
    .byte 0x00
    .org 0x65831-ORIGIN
P_00065831:
    .byte 0x00
    .org 0x65832-ORIGIN
P_00065832:
    .byte 0x87
    .org 0x65833-ORIGIN
P_00065833:
    .byte 0x10
    .org 0x65834-ORIGIN
P_00065834:
    .byte 0xff
    .org 0x65835-ORIGIN
P_00065835:
    .byte 0xff
    .org 0x65836-ORIGIN
P_00065836:
    .byte 0x23
    .org 0x65837-ORIGIN
P_00065837:
    .byte 0xbc
    .org 0x65838-ORIGIN
P_00065838:
    .byte 0x00
    .org 0x65839-ORIGIN
P_00065839:
    .byte 0x01
    .org 0x6583a-ORIGIN
P_0006583a:
    .byte 0x1d
    .org 0x6583b-ORIGIN
P_0006583b:
    .byte 0x24
    .org 0x6583c-ORIGIN
P_0006583c:
    .byte 0x00
    .org 0x6583d-ORIGIN
P_0006583d:
    .byte 0x01
    .org 0x6583e-ORIGIN
P_0006583e:
    .byte 0x19
    .org 0x6583f-ORIGIN
P_0006583f:
    .byte 0x9e
    .org 0x65840-ORIGIN
P_00065840:
    .byte 0x00
    .org 0x65841-ORIGIN
P_00065841:
    .byte 0x02
    .org 0x65842-ORIGIN
P_00065842:
    .byte 0x64
    .org 0x65843-ORIGIN
P_00065843:
    .byte 0xa0
    .org 0x65844-ORIGIN
P_00065844:
    .byte 0xff
    .org 0x65845-ORIGIN
P_00065845:
    .byte 0xff
    .org 0x65846-ORIGIN
P_00065846:
    .byte 0x11
    .org 0x65847-ORIGIN
P_00065847:
    .byte 0x9c
    .org 0x65848-ORIGIN
P_00065848:
    .byte 0x00
    .org 0x65849-ORIGIN
P_00065849:
    .byte 0x02
    .org 0x6584a-ORIGIN
P_0006584a:
    .byte 0x1b
    .org 0x6584b-ORIGIN
P_0006584b:
    .byte 0xbc
    .org 0x6584c-ORIGIN
P_0006584c:
    .byte 0xff
    .org 0x6584d-ORIGIN
P_0006584d:
    .byte 0xff
    .org 0x6584e-ORIGIN
P_0006584e:
    .byte 0x41
    .org 0x6584f-ORIGIN
P_0006584f:
    .byte 0x24
    .org 0x65b08-ORIGIN
L_00065b08:
    mov.l r12,@-r15
    .org 0x65b0a-ORIGIN
L_00065b0a:
    mov.l r14,@-r15
    .org 0x65b0c-ORIGIN
L_00065b0c:
    sts.l pr,@-r15
    .org 0x65b0e-ORIGIN
L_00065b0e:
    sts.l macl,@-r15
    .org 0x65b10-ORIGIN
L_00065b10:
    stc.l gbr,@-r15
    .org 0x65b12-ORIGIN
L_00065b12:
    mov.l P_00065d74,r0
    .org 0x65b14-ORIGIN
L_00065b14:
    ldc r0,gbr
    .org 0x65b16-ORIGIN
L_00065b16:
    add #-0x8,r15
    .org 0x65b18-ORIGIN
L_00065b18:
    mov.l P_00065d78,r6
    .org 0x65b1a-ORIGIN
L_00065b1a:
    mov.b @r6,r0
    .org 0x65b1c-ORIGIN
L_00065b1c:
    tst #0x20,r0
    .org 0x65b1e-ORIGIN
L_00065b1e:
    bf L_00065bb6
    .org 0x65b20-ORIGIN
L_00065b20:
    mov.b @(0x53,gbr),r0
    .org 0x65b22-ORIGIN
L_00065b22:
    mov.l P_00065d7c,r2
    .org 0x65b24-ORIGIN
L_00065b24:
    extu.b r0,r6
    .org 0x65b26-ORIGIN
L_00065b26:
    mov.l P_00065d74,r12
    .org 0x65b28-ORIGIN
L_00065b28:
    mov #0x35,r0
    .org 0x65b2a-ORIGIN
L_00065b2a:
    mov.b @(r0,r2),r4
    .org 0x65b2c-ORIGIN
L_00065b2c:
    mov #0x48,r0
    .org 0x65b2e-ORIGIN
L_00065b2e:
    mov.b @(r0,r2),r5
    .org 0x65b30-ORIGIN
L_00065b30:
    mov.w P_00065c76,r0
    .org 0x65b32-ORIGIN
L_00065b32:
    mov r4,r2
    .org 0x65b34-ORIGIN
L_00065b34:
    sub r5,r2
    .org 0x65b36-ORIGIN
L_00065b36:
    sub r6,r2
    .org 0x65b38-ORIGIN
L_00065b38:
    mov.b @(r0,r12),r6
    .org 0x65b3a-ORIGIN
L_00065b3a:
    extu.b r6,r6
    .org 0x65b3c-ORIGIN
L_00065b3c:
    sub r6,r2
    .org 0x65b3e-ORIGIN
L_00065b3e:
    cmp/pz r2
    .org 0x65b40-ORIGIN
L_00065b40:
    bt/s L_00065b46
    .org 0x65b42-ORIGIN
L_00065b42:
    mov r2,r6
    .org 0x65b44-ORIGIN
L_00065b44:
    mov #0x0,r6
    .org 0x65b46-ORIGIN
L_00065b46:
    mov #-0x1,r14
    .org 0x65b48-ORIGIN
L_00065b48:
    extu.w r6,r2
    .org 0x65b4a-ORIGIN
L_00065b4a:
    extu.b r14,r14
    .org 0x65b4c-ORIGIN
L_00065b4c:
    cmp/gt r14,r2
    .org 0x65b4e-ORIGIN
L_00065b4e:
    bf L_00065b52
    .org 0x65b50-ORIGIN
L_00065b50:
    mov r14,r2
    .org 0x65b52-ORIGIN
L_00065b52:
    mov.b r2,@r15
    .org 0x65b54-ORIGIN
L_00065b54:
    mov.l P_00065d80,r4
    .org 0x65b56-ORIGIN
L_00065b56:
    extu.b r2,r6
    .org 0x65b58-ORIGIN
L_00065b58:
    mov.l P_00065d84,r5
    .org 0x65b5a-ORIGIN
L_00065b5a:
    mov.l P_00065d88,r2
    .org 0x65b5c-ORIGIN
L_00065b5c:
    jsr @r2
    .org 0x65b5e-ORIGIN
L_00065b5e:
    nop
    .org 0x65b60-ORIGIN
L_00065b60:
    mov.b r0,@(0x4,r15)
    .org 0x65b62-ORIGIN
L_00065b62:
    mov.b @(0x53,gbr),r0
    .org 0x65b64-ORIGIN
L_00065b64:
    mov.l P_00065d8c,r7
    .org 0x65b66-ORIGIN
L_00065b66:
    extu.b r0,r2
    .org 0x65b68-ORIGIN
L_00065b68:
    mov.w P_00065c76,r0
    .org 0x65b6a-ORIGIN
L_00065b6a:
    mov.b @r15,r6
    .org 0x65b6c-ORIGIN
L_00065b6c:
    mov.b @(r0,r12),r5
    .org 0x65b6e-ORIGIN
L_00065b6e:
    mov #0x25,r0
    .org 0x65b70-ORIGIN
L_00065b70:
    mov.b @(r0,r7),r4
    .org 0x65b72-ORIGIN
L_00065b72:
    extu.b r6,r6
    .org 0x65b74-ORIGIN
L_00065b74:
    extu.b r5,r5
    .org 0x65b76-ORIGIN
L_00065b76:
    add r4,r6
    .org 0x65b78-ORIGIN
L_00065b78:
    add r2,r6
    .org 0x65b7a-ORIGIN
L_00065b7a:
    add r5,r6
    .org 0x65b7c-ORIGIN
L_00065b7c:
    cmp/pz r6
    .org 0x65b7e-ORIGIN
L_00065b7e:
    bt L_00065b82
    .org 0x65b80-ORIGIN
L_00065b80:
    mov #0x0,r6
    .org 0x65b82-ORIGIN
L_00065b82:
    extu.w r6,r6
    .org 0x65b84-ORIGIN
L_00065b84:
    cmp/gt r14,r6
    .org 0x65b86-ORIGIN
L_00065b86:
    bf L_00065b8a
    .org 0x65b88-ORIGIN
L_00065b88:
    mov r14,r6
    .org 0x65b8a-ORIGIN
L_00065b8a:
    mov.l P_00065d80,r4
    .org 0x65b8c-ORIGIN
L_00065b8c:
    mov.l P_00065d84,r5
    .org 0x65b8e-ORIGIN
L_00065b8e:
    mov.l P_00065d88,r2
    .org 0x65b90-ORIGIN
L_00065b90:
    jsr @r2
    .org 0x65b92-ORIGIN
L_00065b92:
    extu.b r6,r6
    .org 0x65b94-ORIGIN
L_00065b94:
    extu.b r0,r5
    .org 0x65b96-ORIGIN
L_00065b96:
    mov.b @(0x4,r15),r0
    .org 0x65b98-ORIGIN
L_00065b98:
    mov #0x1,r6
    .org 0x65b9a-ORIGIN
L_00065b9a:
    extu.b r0,r7
    .org 0x65b9c-ORIGIN
L_00065b9c:
    mov.w P_00065c78,r0
    .org 0x65b9e-ORIGIN
L_00065b9e:
    shll8 r6
    .org 0x65ba0-ORIGIN
L_00065ba0:
    mov r6,r2
    .org 0x65ba2-ORIGIN
L_00065ba2:
    sub r5,r2
    .org 0x65ba4-ORIGIN
L_00065ba4:
    mov.w @(r0,r12),r5
    .org 0x65ba6-ORIGIN
L_00065ba6:
    sub r7,r6
    .org 0x65ba8-ORIGIN
L_00065ba8:
    mov r6,r0
    .org 0x65baa-ORIGIN
L_00065baa:
    mul.l r5,r2
    .org 0x65bac-ORIGIN
L_00065bac:
    mov.l P_00065d90,r5
    .org 0x65bae-ORIGIN
L_00065bae:
    jsr @r5
    .org 0x65bb0-ORIGIN
L_00065bb0:
    sts macl,r1
    .org 0x65bb2-ORIGIN
L_00065bb2:
    bra L_00065c02
    .org 0x65bb4-ORIGIN
L_00065bb4:
    mov r0,r2
    .org 0x65bb6-ORIGIN
L_00065bb6:
    mov.l P_00065d8c,r7
    .org 0x65bb8-ORIGIN
L_00065bb8:
    mov.l P_00065d7c,r2
    .org 0x65bba-ORIGIN
L_00065bba:
    mov.b @(0x6,r7),r0
    .org 0x65bbc-ORIGIN
L_00065bbc:
    mov r0,r5
    .org 0x65bbe-ORIGIN
L_00065bbe:
    mov #0x35,r0
    .org 0x65bc0-ORIGIN
L_00065bc0:
    mov.b @(r0,r2),r2
    .org 0x65bc2-ORIGIN
L_00065bc2:
    sub r5,r2
    .org 0x65bc4-ORIGIN
L_00065bc4:
    cmp/pz r2
    .org 0x65bc6-ORIGIN
L_00065bc6:
    bt L_00065bca
    .org 0x65bc8-ORIGIN
L_00065bc8:
    mov #0x0,r2
    .org 0x65bca-ORIGIN
L_00065bca:
    mov #-0x1,r14
    .org 0x65bcc-ORIGIN
L_00065bcc:
    extu.b r2,r6
    .org 0x65bce-ORIGIN
L_00065bce:
    extu.b r14,r14
    .org 0x65bd0-ORIGIN
L_00065bd0:
    cmp/gt r14,r6
    .org 0x65bd2-ORIGIN
L_00065bd2:
    bf L_00065bd6
    .org 0x65bd4-ORIGIN
L_00065bd4:
    mov r14,r6
    .org 0x65bd6-ORIGIN
L_00065bd6:
    mov.l P_00065d80,r4
    .org 0x65bd8-ORIGIN
L_00065bd8:
    mov.l P_00065d84,r5
    .org 0x65bda-ORIGIN
L_00065bda:
    mov.l P_00065d88,r2
    .org 0x65bdc-ORIGIN
L_00065bdc:
    mov.l P_00065d74,r12
    .org 0x65bde-ORIGIN
L_00065bde:
    jsr @r2
    .org 0x65be0-ORIGIN
L_00065be0:
    extu.b r6,r6
    .org 0x65be2-ORIGIN
L_00065be2:
    extu.b r0,r6
    .org 0x65be4-ORIGIN
L_00065be4:
    mov.w P_00065c78,r0
    .org 0x65be6-ORIGIN
L_00065be6:
    mov #0x1,r2
    .org 0x65be8-ORIGIN
L_00065be8:
    shll8 r2
    .org 0x65bea-ORIGIN
L_00065bea:
    sub r6,r2
    .org 0x65bec-ORIGIN
L_00065bec:
    mov.w @(r0,r12),r6
    .org 0x65bee-ORIGIN
L_00065bee:
    mul.l r6,r2
    .org 0x65bf0-ORIGIN
L_00065bf0:
    sts macl,r2
    .org 0x65bf2-ORIGIN
L_00065bf2:
    cmp/pz r2
    .org 0x65bf4-ORIGIN
L_00065bf4:
    bt L_00065bf8
    .org 0x65bf6-ORIGIN
L_00065bf6:
    add r14,r2
    .org 0x65bf8-ORIGIN
L_00065bf8:
    mov r2,r6
    .org 0x65bfa-ORIGIN
L_00065bfa:
    shlr8 r6
    .org 0x65bfc-ORIGIN
L_00065bfc:
    swap.w r6,r2
    .org 0x65bfe-ORIGIN
L_00065bfe:
    exts.b r2,r6
    .org 0x65c00-ORIGIN
L_00065c00:
    xtrct r6,r2
    .org 0x65c02-ORIGIN
L_00065c02:
    mov.w P_00065c7a,r6
    .org 0x65c04-ORIGIN
L_00065c04:
    cmp/gt r6,r2
    .org 0x65c06-ORIGIN
L_00065c06:
    bt L_00065c0a
    .org 0x65c08-ORIGIN
L_00065c08:
    mov r2,r6
    .org 0x65c0a-ORIGIN
L_00065c0a:
    mov #-0x80,r2
    .org 0x65c0c-ORIGIN
L_00065c0c:
    shll8 r2
    .org 0x65c0e-ORIGIN
L_00065c0e:
    cmp/ge r2,r6
    .org 0x65c10-ORIGIN
L_00065c10:
    bf L_00065c14
    .org 0x65c12-ORIGIN
L_00065c12:
    mov r6,r2
    .org 0x65c14-ORIGIN
L_00065c14:
    mov.w P_00065c7c,r0
    .org 0x65c16-ORIGIN
L_00065c16:
    mov.w r2,@(r0,r12)
    .org 0x65c18-ORIGIN
L_00065c18:
    add #0x8,r15
    .org 0x65c1a-ORIGIN
L_00065c1a:
    ldc.l @r15+,gbr
    .org 0x65c1c-ORIGIN
L_00065c1c:
    lds.l @r15+,macl
    .org 0x65c1e-ORIGIN
L_00065c1e:
    lds.l @r15+,pr
    .org 0x65c20-ORIGIN
L_00065c20:
    mov.l @r15+,r14
    .org 0x65c22-ORIGIN
L_00065c22:
    rts
    .org 0x65c24-ORIGIN
L_00065c24:
    mov.l @r15+,r12
    .org 0x65c76-ORIGIN
P_00065c76:
    .byte 0x03
    .org 0x65c77-ORIGIN
P_00065c77:
    .byte 0x5e
    .org 0x65c78-ORIGIN
P_00065c78:
    .byte 0x06
    .org 0x65c79-ORIGIN
P_00065c79:
    .byte 0x40
    .org 0x65c7a-ORIGIN
P_00065c7a:
    .byte 0x7f
    .org 0x65c7b-ORIGIN
P_00065c7b:
    .byte 0xff
    .org 0x65c7c-ORIGIN
P_00065c7c:
    .byte 0x06
    .org 0x65c7d-ORIGIN
P_00065c7d:
    .byte 0x42
    .org 0x65d74-ORIGIN
P_00065d74:
    .byte 0xff
    .org 0x65d75-ORIGIN
P_00065d75:
    .byte 0xff
    .org 0x65d76-ORIGIN
P_00065d76:
    .byte 0x12
    .org 0x65d77-ORIGIN
P_00065d77:
    .byte 0x8c
    .org 0x65d78-ORIGIN
P_00065d78:
    .byte 0x00
    .org 0x65d79-ORIGIN
P_00065d79:
    .byte 0x00
    .org 0x65d7a-ORIGIN
P_00065d7a:
    .byte 0x87
    .org 0x65d7b-ORIGIN
P_00065d7b:
    .byte 0x10
    .org 0x65d7c-ORIGIN
P_00065d7c:
    .byte 0xff
    .org 0x65d7d-ORIGIN
P_00065d7d:
    .byte 0xff
    .org 0x65d7e-ORIGIN
P_00065d7e:
    .byte 0x23
    .org 0x65d7f-ORIGIN
P_00065d7f:
    .byte 0xbc
    .org 0x65d80-ORIGIN
P_00065d80:
    .byte 0x00
    .org 0x65d81-ORIGIN
P_00065d81:
    .byte 0x01
    .org 0x65d82-ORIGIN
P_00065d82:
    .byte 0x1d
    .org 0x65d83-ORIGIN
P_00065d83:
    .byte 0x24
    .org 0x65d84-ORIGIN
P_00065d84:
    .byte 0x00
    .org 0x65d85-ORIGIN
P_00065d85:
    .byte 0x01
    .org 0x65d86-ORIGIN
P_00065d86:
    .byte 0x19
    .org 0x65d87-ORIGIN
P_00065d87:
    .byte 0x9e
    .org 0x65d88-ORIGIN
P_00065d88:
    .byte 0x00
    .org 0x65d89-ORIGIN
P_00065d89:
    .byte 0x02
    .org 0x65d8a-ORIGIN
P_00065d8a:
    .byte 0x64
    .org 0x65d8b-ORIGIN
P_00065d8b:
    .byte 0xa0
    .org 0x65d8c-ORIGIN
P_00065d8c:
    .byte 0xff
    .org 0x65d8d-ORIGIN
P_00065d8d:
    .byte 0xff
    .org 0x65d8e-ORIGIN
P_00065d8e:
    .byte 0x11
    .org 0x65d8f-ORIGIN
P_00065d8f:
    .byte 0x9c
    .org 0x65d90-ORIGIN
P_00065d90:
    .byte 0x00
    .org 0x65d91-ORIGIN
P_00065d91:
    .byte 0x02
    .org 0x65d92-ORIGIN
P_00065d92:
    .byte 0x1b
    .org 0x65d93-ORIGIN
P_00065d93:
    .byte 0xbc
