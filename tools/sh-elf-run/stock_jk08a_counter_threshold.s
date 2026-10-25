! Explicit lower-knot4x4 lookup, counter increment and signed ratio-factor window.
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
    .org 0x260bc-ORIGIN
L_000260bc:
    sts.l pr,@-r15
    .org 0x260be-ORIGIN
L_000260be:
    mov.l r4,@-r15
    .org 0x260c0-ORIGIN
L_000260c0:
    extu.b r7,r7
    .org 0x260c2-ORIGIN
L_000260c2:
    mov r5,r0
    .org 0x260c4-ORIGIN
L_000260c4:
    mov r7,r5
    .org 0x260c6-ORIGIN
L_000260c6:
    mov.l L_000260fc,r7
    .org 0x260c8-ORIGIN
L_000260c8:
    jsr @r7
    .org 0x260ca-ORIGIN
L_000260ca:
    mov #0x3,r4
    .org 0x260cc-ORIGIN
L_000260cc:
    mov.l r4,@-r15
    .org 0x260ce-ORIGIN
L_000260ce:
    mov.l r5,@-r15
    .org 0x260d0-ORIGIN
L_000260d0:
    mov r6,r0
    .org 0x260d2-ORIGIN
L_000260d2:
    mov.l @(0x10,r15),r5
    .org 0x260d4-ORIGIN
L_000260d4:
    extu.b r5,r5
    .org 0x260d6-ORIGIN
L_000260d6:
    jsr @r7
    .org 0x260d8-ORIGIN
L_000260d8:
    mov #0x3,r4
    .org 0x260da-ORIGIN
L_000260da:
    mov.l @r15+,r1
    .org 0x260dc-ORIGIN
L_000260dc:
    mov.l @r15+,r0
    .org 0x260de-ORIGIN
L_000260de:
    mov r4,r2
    .org 0x260e0-ORIGIN
L_000260e0:
    mov r5,r3
    .org 0x260e2-ORIGIN
L_000260e2:
    mov.l @r15+,r4
    .org 0x260e4-ORIGIN
L_000260e4:
    mov.l L_000260f8,r5
    .org 0x260e6-ORIGIN
L_000260e6:
    lds.l @r15+,pr
    .org 0x260e8-ORIGIN
L_000260e8:
    sts macl,r7
    .org 0x260ea-ORIGIN
L_000260ea:
    mulu.w r5,r0
    .org 0x260ec-ORIGIN
L_000260ec:
    add r2,r4
    .org 0x260ee-ORIGIN
L_000260ee:
    sts macl,r0
    .org 0x260f0-ORIGIN
L_000260f0:
    lds r7,macl
    .org 0x260f2-ORIGIN
L_000260f2:
    add r0,r4
    .org 0x260f4-ORIGIN
L_000260f4:
    rts
    .org 0x260f6-ORIGIN
L_000260f6:
    mov.b @r4,r0
    .org 0x260f8-ORIGIN
L_000260f8:
    .long 0x00000004
    .org 0x260fc-ORIGIN
L_000260fc:
    .long 0x00026944
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
    .org 0x79686-ORIGIN
L_00079686:
    mov.l L_000797fc,r7
    .org 0x79688-ORIGIN
L_00079688:
    mov r6,r0
    .org 0x7968a-ORIGIN
L_0007968a:
    mov.b r0,@(0x3,r15)
    .org 0x7968c-ORIGIN
L_0007968c:
    mov #0x12,r0
    .org 0x7968e-ORIGIN
L_0007968e:
    mov.b @(r0,r7),r2
    .org 0x79690-ORIGIN
L_00079690:
    mov.l L_00079800,r14
    .org 0x79692-ORIGIN
L_00079692:
    mov.l L_00079804,r4
    .org 0x79694-ORIGIN
L_00079694:
    extu.b r2,r7
    .org 0x79696-ORIGIN
L_00079696:
    mov.l L_00079808,r2
    .org 0x79698-ORIGIN
L_00079698:
    mov r14,r6
    .org 0x7969a-ORIGIN
L_0007969a:
    add #0x4,r6
    .org 0x7969c-ORIGIN
L_0007969c:
    jsr @r2
    .org 0x7969e-ORIGIN
L_0007969e:
    mov r14,r5
    .org 0x796a0-ORIGIN
L_000796a0:
    mov.l L_000797f8,r3
    .org 0x796a2-ORIGIN
L_000796a2:
    mov r0,r6
    .org 0x796a4-ORIGIN
L_000796a4:
    mov.w L_00079708,r0
    .org 0x796a6-ORIGIN
L_000796a6:
    mov.w @r3,r5
    .org 0x796a8-ORIGIN
L_000796a8:
    mov.l r14,@(0x8,r15)
    .org 0x796aa-ORIGIN
L_000796aa:
    extu.w r5,r5
    .org 0x796ac-ORIGIN
L_000796ac:
    mov.b r6,@(r0,r11)
    .org 0x796ae-ORIGIN
L_000796ae:
    cmp/pz r5
    .org 0x796b0-ORIGIN
L_000796b0:
    bt/s L_000796b6
    .org 0x796b2-ORIGIN
L_000796b2:
    mov r5,r6
    .org 0x796b4-ORIGIN
L_000796b4:
    add #0x3,r6
    .org 0x796b6-ORIGIN
L_000796b6:
    shar r6
    .org 0x796b8-ORIGIN
L_000796b8:
    mov #-0x1,r2
    .org 0x796ba-ORIGIN
L_000796ba:
    shar r6
    .org 0x796bc-ORIGIN
L_000796bc:
    extu.b r2,r2
    .org 0x796be-ORIGIN
L_000796be:
    cmp/gt r2,r6
    .org 0x796c0-ORIGIN
L_000796c0:
    bf L_000796c6
    .org 0x796c2-ORIGIN
L_000796c2:
    bra L_000796d0
    .org 0x796c4-ORIGIN
L_000796c4:
    mov #-0x1,r5
    .org 0x796c6-ORIGIN
L_000796c6:
    cmp/pz r5
    .org 0x796c8-ORIGIN
L_000796c8:
    bt L_000796cc
    .org 0x796ca-ORIGIN
L_000796ca:
    add #0x3,r5
    .org 0x796cc-ORIGIN
L_000796cc:
    shar r5
    .org 0x796ce-ORIGIN
L_000796ce:
    shar r5
    .org 0x796d0-ORIGIN
L_000796d0:
    mov.l L_000797fc,r3
    .org 0x796d2-ORIGIN
L_000796d2:
    mov r5,r0
    .org 0x796d4-ORIGIN
L_000796d4:
    mov.b r0,@(0x3,r15)
    .org 0x796d6-ORIGIN
L_000796d6:
    mov #0x12,r0
    .org 0x796d8-ORIGIN
L_000796d8:
    mov r14,r5
    .org 0x796da-ORIGIN
L_000796da:
    mov.b @(r0,r3),r2
    .org 0x796dc-ORIGIN
L_000796dc:
    mov.l L_0007980c,r4
    .org 0x796de-ORIGIN
L_000796de:
    mov.l L_00079808,r1
    .org 0x796e0-ORIGIN
L_000796e0:
    extu.b r2,r7
    .org 0x796e2-ORIGIN
L_000796e2:
    mov.l r14,@(0xc,r15)
    .org 0x796e4-ORIGIN
L_000796e4:
    add #0x4,r14
    .org 0x796e6-ORIGIN
L_000796e6:
    jsr @r1
    .org 0x796e8-ORIGIN
L_000796e8:
    mov r14,r6
    .org 0x796ea-ORIGIN
L_000796ea:
    mov r0,r5
    .org 0x796ec-ORIGIN
L_000796ec:
    mov.w L_0007970a,r0
    .org 0x796ee-ORIGIN
L_000796ee:
    mov #-0x1,r7
    .org 0x796f0-ORIGIN
L_000796f0:
    mov.b r5,@(r0,r11)
    .org 0x796f2-ORIGIN
L_000796f2:
    extu.w r7,r7
    .org 0x796f4-ORIGIN
L_000796f4:
    mov.w L_0007970c,r0
    .org 0x796f6-ORIGIN
L_000796f6:
    mov.w @(r0,r11),r4
    .org 0x796f8-ORIGIN
L_000796f8:
    extu.w r4,r4
    .org 0x796fa-ORIGIN
L_000796fa:
    mov r4,r6
    .org 0x796fc-ORIGIN
L_000796fc:
    add #0x1,r6
    .org 0x796fe-ORIGIN
L_000796fe:
    cmp/gt r7,r6
    .org 0x79700-ORIGIN
L_00079700:
    bf L_0007970e
    .org 0x79702-ORIGIN
L_00079702:
    bra L_00079712
    .org 0x79704-ORIGIN
L_00079704:
    mov r7,r6
    .org 0x79708-ORIGIN
L_00079708:
    .word 0x0c24
    .org 0x7970a-ORIGIN
L_0007970a:
    .word 0x0b51
    .org 0x7970c-ORIGIN
L_0007970c:
    .word 0x0b4e
    .org 0x7970e-ORIGIN
L_0007970e:
    add #0x1,r4
    .org 0x79710-ORIGIN
L_00079710:
    mov r4,r6
    .org 0x79712-ORIGIN
L_00079712:
    mov.w L_000797de,r0
    .org 0x79714-ORIGIN
L_00079714:
    mov.w r6,@(r0,r11)
    .org 0x79716-ORIGIN
L_00079716:
    mov.w L_000797e0,r0
    .org 0x79718-ORIGIN
L_00079718:
    mov.b @(r0,r11),r4
    .org 0x7971a-ORIGIN
L_0007971a:
    mov.w L_000797e2,r0
    .org 0x7971c-ORIGIN
L_0007971c:
    extu.b r4,r4
    .org 0x7971e-ORIGIN
L_0007971e:
    mov.b @(r0,r11),r6
    .org 0x79720-ORIGIN
L_00079720:
    mov #0xa,r0
    .org 0x79722-ORIGIN
L_00079722:
    extu.b r6,r2
    .org 0x79724-ORIGIN
L_00079724:
    mul.l r4,r2
    .org 0x79726-ORIGIN
L_00079726:
    mov.l L_00079810,r4
    .org 0x79728-ORIGIN
L_00079728:
    jsr @r4
    .org 0x7972a-ORIGIN
L_0007972a:
    sts macl,r1
    .org 0x7972c-ORIGIN
L_0007972c:
    mov r0,r4
    .org 0x7972e-ORIGIN
L_0007972e:
    extu.w r0,r7
    .org 0x79730-ORIGIN
L_00079730:
    mov.w L_000797e4,r0
    .org 0x79732-ORIGIN
L_00079732:
    mov.b @(r0,r11),r5
    .org 0x79734-ORIGIN
L_00079734:
    extu.b r5,r5
    .org 0x79736-ORIGIN
L_00079736:
    cmp/ge r5,r7
    .org 0x79738-ORIGIN
L_00079738:
    bt L_0007973c
    .org 0x7973a-ORIGIN
L_0007973a:
    mov r5,r4
    .org 0x7973c-ORIGIN
L_0007973c:
    mov.w L_000797de,r0
    .org 0x7973e-ORIGIN
L_0007973e:
    extu.w r4,r4
    .org 0x79740-ORIGIN
L_00079740:
    mov.w @(r0,r11),r2
    .org 0x79742-ORIGIN
L_00079742:
    extu.w r2,r5
    .org 0x79744-ORIGIN
L_00079744:
    cmp/ge r4,r5
    .org 0x79746-ORIGIN
L_00079746:
    bf L_0007974a
    .org 0x79748-ORIGIN
L_00079748:
    mov #0x1,r12
    .org 0x797de-ORIGIN
L_000797de:
    .word 0x0b4e
    .org 0x797e0-ORIGIN
L_000797e0:
    .word 0x0b50
    .org 0x797e2-ORIGIN
L_000797e2:
    .word 0x0c24
    .org 0x797e4-ORIGIN
L_000797e4:
    .word 0x0b51
    .org 0x797f8-ORIGIN
L_000797f8:
    .long 0xffff40c6
    .org 0x797fc-ORIGIN
L_000797fc:
    .long 0xffff119c
    .org 0x79800-ORIGIN
L_00079800:
    .long 0x00012fee
    .org 0x79804-ORIGIN
L_00079804:
    .long 0x0000aafa
    .org 0x79808-ORIGIN
L_00079808:
    .long 0x000260bc
    .org 0x7980c-ORIGIN
L_0007980c:
    .long 0x0000aaea
    .org 0x79810-ORIGIN
L_00079810:
    .long 0x00021bbc
