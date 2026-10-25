! Complete stock request dispatcher, staged helpers and signed publication boundary.
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
    mov.l P_000260fc,r7
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
    mov.l P_000260f8,r5
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
P_000260f8:
    .byte 0x00
    .org 0x260f9-ORIGIN
P_000260f9:
    .byte 0x00
    .org 0x260fa-ORIGIN
P_000260fa:
    .byte 0x00
    .org 0x260fb-ORIGIN
P_000260fb:
    .byte 0x04
    .org 0x260fc-ORIGIN
P_000260fc:
    .byte 0x00
    .org 0x260fd-ORIGIN
P_000260fd:
    .byte 0x02
    .org 0x260fe-ORIGIN
P_000260fe:
    .byte 0x69
    .org 0x260ff-ORIGIN
P_000260ff:
    .byte 0x44
    .org 0x26388-ORIGIN
L_00026388:
    mov.w P_0002639a,r0
    .org 0x2638a-ORIGIN
L_0002638a:
    extu.b r5,r5
    .org 0x2638c-ORIGIN
L_0002638c:
    cmp/hs r0,r5
    .org 0x2638e-ORIGIN
L_0002638e:
    bt L_00026396
    .org 0x26390-ORIGIN
L_00026390:
    mov.l P_0002639c,r6
    .org 0x26392-ORIGIN
L_00026392:
    jmp @r6
    .org 0x26394-ORIGIN
L_00026394:
    mov #0x0,r3
    .org 0x26396-ORIGIN
L_00026396:
    rts
    .org 0x26398-ORIGIN
L_00026398:
    mov.b @(0xf,r4),r0
    .org 0x2639a-ORIGIN
P_0002639a:
    .byte 0x00
    .org 0x2639b-ORIGIN
P_0002639b:
    .byte 0xf0
    .org 0x2639c-ORIGIN
P_0002639c:
    .byte 0x00
    .org 0x2639d-ORIGIN
P_0002639d:
    .byte 0x02
    .org 0x2639e-ORIGIN
P_0002639e:
    .byte 0x6a
    .org 0x2639f-ORIGIN
P_0002639f:
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
    .org 0x79030-ORIGIN
L_00079030:
    mov.l r8,@-r15
    .org 0x79032-ORIGIN
L_00079032:
    mov.l r9,@-r15
    .org 0x79034-ORIGIN
L_00079034:
    mov.l r10,@-r15
    .org 0x79036-ORIGIN
L_00079036:
    mov.l r11,@-r15
    .org 0x79038-ORIGIN
L_00079038:
    mov.l r12,@-r15
    .org 0x7903a-ORIGIN
L_0007903a:
    mov.l r13,@-r15
    .org 0x7903c-ORIGIN
L_0007903c:
    mov.l r14,@-r15
    .org 0x7903e-ORIGIN
L_0007903e:
    mov.l P_00079218,r5
    .org 0x79040-ORIGIN
L_00079040:
    mov #0x12,r0
    .org 0x79042-ORIGIN
L_00079042:
    mov.l P_0007921c,r8
    .org 0x79044-ORIGIN
L_00079044:
    mov.b @(r0,r5),r6
    .org 0x79046-ORIGIN
L_00079046:
    mov.b @(0x7,r8),r0
    .org 0x79048-ORIGIN
L_00079048:
    mov.l P_00079220,r9
    .org 0x7904a-ORIGIN
L_0007904a:
    mov r0,r10
    .org 0x7904c-ORIGIN
L_0007904c:
    mov #0x7c,r0
    .org 0x7904e-ORIGIN
L_0007904e:
    mov.w @(r0,r9),r4
    .org 0x79050-ORIGIN
L_00079050:
    mov.l P_00079224,r7
    .org 0x79052-ORIGIN
L_00079052:
    mov.w P_000790fe,r0
    .org 0x79054-ORIGIN
L_00079054:
    mov.w @(r0,r7),r2
    .org 0x79056-ORIGIN
L_00079056:
    cmp/ge r4,r2
    .org 0x79058-ORIGIN
L_00079058:
    bt/s L_00079066
    .org 0x7905a-ORIGIN
L_0007905a:
    mov r6,r0
    .org 0x7905c-ORIGIN
L_0007905c:
    or #0x8,r0
    .org 0x7905e-ORIGIN
L_0007905e:
    mov r0,r6
    .org 0x79060-ORIGIN
L_00079060:
    mov #0x12,r0
    .org 0x79062-ORIGIN
L_00079062:
    bra L_00079070
    .org 0x79064-ORIGIN
L_00079064:
    mov.b r6,@(r0,r5)
    .org 0x79066-ORIGIN
L_00079066:
    and #0xf7,r0
    .org 0x79068-ORIGIN
L_00079068:
    mov.w P_00079100,r2
    .org 0x7906a-ORIGIN
L_0007906a:
    mov r0,r6
    .org 0x7906c-ORIGIN
L_0007906c:
    mov #0x12,r0
    .org 0x7906e-ORIGIN
L_0007906e:
    mov.b r6,@(r0,r5)
    .org 0x79070-ORIGIN
L_00079070:
    mov.l P_00079228,r5
    .org 0x79072-ORIGIN
L_00079072:
    mov.w P_00079102,r0
    .org 0x79074-ORIGIN
L_00079074:
    mov.w @(r0,r5),r6
    .org 0x79076-ORIGIN
L_00079076:
    cmp/pl r6
    .org 0x79078-ORIGIN
L_00079078:
    bf L_0007907c
    .org 0x7907a-ORIGIN
L_0007907a:
    mov #0x0,r6
    .org 0x7907c-ORIGIN
L_0007907c:
    exts.w r6,r5
    .org 0x7907e-ORIGIN
L_0007907e:
    mov.l P_0007922c,r6
    .org 0x79080-ORIGIN
L_00079080:
    mov.b @r6,r11
    .org 0x79082-ORIGIN
L_00079082:
    mov r11,r0
    .org 0x79084-ORIGIN
L_00079084:
    and #0x1,r0
    .org 0x79086-ORIGIN
L_00079086:
    tst r0,r0
    .org 0x79088-ORIGIN
L_00079088:
    bt/s L_0007909a
    .org 0x7908a-ORIGIN
L_0007908a:
    mov r0,r7
    .org 0x7908c-ORIGIN
L_0007908c:
    exts.w r2,r2
    .org 0x7908e-ORIGIN
L_0007908e:
    cmp/ge r5,r2
    .org 0x79090-ORIGIN
L_00079090:
    bt L_00079096
    .org 0x79092-ORIGIN
L_00079092:
    bra L_00079098
    .org 0x79094-ORIGIN
L_00079094:
    mov r5,r6
    .org 0x79096-ORIGIN
L_00079096:
    exts.w r2,r6
    .org 0x79098-ORIGIN
L_00079098:
    mov r6,r2
    .org 0x7909a-ORIGIN
L_0007909a:
    mov.l P_00079228,r3
    .org 0x7909c-ORIGIN
L_0007909c:
    mov r2,r12
    .org 0x7909e-ORIGIN
L_0007909e:
    mov.w P_00079104,r0
    .org 0x790a0-ORIGIN
L_000790a0:
    exts.w r2,r2
    .org 0x790a2-ORIGIN
L_000790a2:
    mov.w @(r0,r3),r6
    .org 0x790a4-ORIGIN
L_000790a4:
    cmp/gt r6,r2
    .org 0x790a6-ORIGIN
L_000790a6:
    bf L_000790ac
    .org 0x790a8-ORIGIN
L_000790a8:
    bra L_000790ae
    .org 0x790aa-ORIGIN
L_000790aa:
    mov r6,r2
    .org 0x790ac-ORIGIN
L_000790ac:
    exts.w r2,r2
    .org 0x790ae-ORIGIN
L_000790ae:
    tst r7,r7
    .org 0x790b0-ORIGIN
L_000790b0:
    exts.w r2,r14
    .org 0x790b2-ORIGIN
L_000790b2:
    bt/s L_000790be
    .org 0x790b4-ORIGIN
L_000790b4:
    mov r4,r2
    .org 0x790b6-ORIGIN
L_000790b6:
    cmp/ge r5,r2
    .org 0x790b8-ORIGIN
L_000790b8:
    bf L_000790bc
    .org 0x790ba-ORIGIN
L_000790ba:
    mov r2,r5
    .org 0x790bc-ORIGIN
L_000790bc:
    mov r5,r2
    .org 0x790be-ORIGIN
L_000790be:
    mov.l P_00079228,r3
    .org 0x790c0-ORIGIN
L_000790c0:
    exts.w r2,r2
    .org 0x790c2-ORIGIN
L_000790c2:
    mov.w P_00079106,r0
    .org 0x790c4-ORIGIN
L_000790c4:
    mov.w @(r0,r3),r7
    .org 0x790c6-ORIGIN
L_000790c6:
    cmp/gt r7,r2
    .org 0x790c8-ORIGIN
L_000790c8:
    bf L_000790ce
    .org 0x790ca-ORIGIN
L_000790ca:
    bra L_000790d0
    .org 0x790cc-ORIGIN
L_000790cc:
    mov r7,r6
    .org 0x790ce-ORIGIN
L_000790ce:
    exts.w r2,r6
    .org 0x790d0-ORIGIN
L_000790d0:
    mov.l P_00079228,r3
    .org 0x790d2-ORIGIN
L_000790d2:
    exts.w r6,r6
    .org 0x790d4-ORIGIN
L_000790d4:
    mov.w P_00079108,r0
    .org 0x790d6-ORIGIN
L_000790d6:
    mov.w @(r0,r3),r2
    .org 0x790d8-ORIGIN
L_000790d8:
    cmp/gt r2,r6
    .org 0x790da-ORIGIN
L_000790da:
    bf L_000790de
    .org 0x790dc-ORIGIN
L_000790dc:
    mov r2,r6
    .org 0x790de-ORIGIN
L_000790de:
    exts.w r6,r13
    .org 0x790e0-ORIGIN
L_000790e0:
    cmp/gt r13,r14
    .org 0x790e2-ORIGIN
L_000790e2:
    bf/s L_000790e8
    .org 0x790e4-ORIGIN
L_000790e4:
    mov r14,r6
    .org 0x790e6-ORIGIN
L_000790e6:
    mov r13,r6
    .org 0x790e8-ORIGIN
L_000790e8:
    mov.l P_00079228,r3
    .org 0x790ea-ORIGIN
L_000790ea:
    exts.w r6,r6
    .org 0x790ec-ORIGIN
L_000790ec:
    mov.w P_0007910a,r0
    .org 0x790ee-ORIGIN
L_000790ee:
    mov.w r6,@(r0,r3)
    .org 0x790f0-ORIGIN
L_000790f0:
    mov r11,r0
    .org 0x790f2-ORIGIN
L_000790f2:
    tst #0x2,r0
    .org 0x790f4-ORIGIN
L_000790f4:
    bt/s L_0007910c
    .org 0x790f6-ORIGIN
L_000790f6:
    mov #0x78,r0
    .org 0x790f8-ORIGIN
L_000790f8:
    mov.w r12,@(r0,r9)
    .org 0x790fa-ORIGIN
L_000790fa:
    bra L_0007910e
    .org 0x790fc-ORIGIN
L_000790fc:
    mov r12,r14
    .org 0x790fe-ORIGIN
P_000790fe:
    .byte 0x07
    .org 0x790ff-ORIGIN
P_000790ff:
    .byte 0x36
    .org 0x79100-ORIGIN
P_00079100:
    .byte 0x7f
    .org 0x79101-ORIGIN
P_00079101:
    .byte 0xff
    .org 0x79102-ORIGIN
P_00079102:
    .byte 0x0b
    .org 0x79103-ORIGIN
P_00079103:
    .byte 0xd2
    .org 0x79104-ORIGIN
P_00079104:
    .byte 0x0b
    .org 0x79105-ORIGIN
P_00079105:
    .byte 0xc0
    .org 0x79106-ORIGIN
P_00079106:
    .byte 0x0b
    .org 0x79107-ORIGIN
P_00079107:
    .byte 0xc2
    .org 0x79108-ORIGIN
P_00079108:
    .byte 0x0b
    .org 0x79109-ORIGIN
P_00079109:
    .byte 0xbc
    .org 0x7910a-ORIGIN
P_0007910a:
    .byte 0x0b
    .org 0x7910b-ORIGIN
P_0007910b:
    .byte 0xac
    .org 0x7910c-ORIGIN
L_0007910c:
    mov.w r14,@(r0,r9)
    .org 0x7910e-ORIGIN
L_0007910e:
    mov.l P_00079228,r3
    .org 0x79110-ORIGIN
L_00079110:
    exts.w r14,r14
    .org 0x79112-ORIGIN
L_00079112:
    mov.w P_0007920a,r0
    .org 0x79114-ORIGIN
L_00079114:
    mov.w @(r0,r3),r5
    .org 0x79116-ORIGIN
L_00079116:
    cmp/ge r5,r14
    .org 0x79118-ORIGIN
L_00079118:
    bf L_0007911c
    .org 0x7911a-ORIGIN
L_0007911a:
    exts.w r14,r5
    .org 0x7911c-ORIGIN
L_0007911c:
    mov.l P_00079228,r3
    .org 0x7911e-ORIGIN
L_0007911e:
    exts.w r5,r5
    .org 0x79120-ORIGIN
L_00079120:
    mov.w P_0007920c,r0
    .org 0x79122-ORIGIN
L_00079122:
    mov.w @(r0,r3),r2
    .org 0x79124-ORIGIN
L_00079124:
    cmp/gt r2,r5
    .org 0x79126-ORIGIN
L_00079126:
    bf L_0007912a
    .org 0x79128-ORIGIN
L_00079128:
    mov r2,r5
    .org 0x7912a-ORIGIN
L_0007912a:
    mov.l P_00079230,r2
    .org 0x7912c-ORIGIN
L_0007912c:
    mov.b @r2,r9
    .org 0x7912e-ORIGIN
L_0007912e:
    mov r9,r0
    .org 0x79130-ORIGIN
L_00079130:
    tst #0x20,r0
    .org 0x79132-ORIGIN
L_00079132:
    bf/s L_00079144
    .org 0x79134-ORIGIN
L_00079134:
    exts.w r5,r5
    .org 0x79136-ORIGIN
L_00079136:
    mov.l P_00079234,r3
    .org 0x79138-ORIGIN
L_00079138:
    mov.w @(0x16,r3),r0
    .org 0x7913a-ORIGIN
L_0007913a:
    cmp/ge r0,r5
    .org 0x7913c-ORIGIN
L_0007913c:
    bf/s L_00079142
    .org 0x7913e-ORIGIN
L_0007913e:
    mov r0,r2
    .org 0x79140-ORIGIN
L_00079140:
    mov r5,r2
    .org 0x79142-ORIGIN
L_00079142:
    mov r2,r5
    .org 0x79144-ORIGIN
L_00079144:
    mov.l P_00079224,r3
    .org 0x79146-ORIGIN
L_00079146:
    mov.w P_0007920e,r0
    .org 0x79148-ORIGIN
L_00079148:
    mov.l P_00079228,r1
    .org 0x7914a-ORIGIN
L_0007914a:
    mov.w r5,@(r0,r3)
    .org 0x7914c-ORIGIN
L_0007914c:
    mov.w P_00079210,r0
    .org 0x7914e-ORIGIN
L_0007914e:
    mov.w @(r0,r1),r5
    .org 0x79150-ORIGIN
L_00079150:
    cmp/ge r5,r13
    .org 0x79152-ORIGIN
L_00079152:
    bf L_00079156
    .org 0x79154-ORIGIN
L_00079154:
    mov r13,r5
    .org 0x79156-ORIGIN
L_00079156:
    mov.l P_00079228,r3
    .org 0x79158-ORIGIN
L_00079158:
    exts.w r5,r5
    .org 0x7915a-ORIGIN
L_0007915a:
    mov.w P_00079212,r0
    .org 0x7915c-ORIGIN
L_0007915c:
    mov.w @(r0,r3),r2
    .org 0x7915e-ORIGIN
L_0007915e:
    cmp/gt r2,r5
    .org 0x79160-ORIGIN
L_00079160:
    bf L_00079164
    .org 0x79162-ORIGIN
L_00079162:
    mov r2,r5
    .org 0x79164-ORIGIN
L_00079164:
    mov.l P_00079234,r2
    .org 0x79166-ORIGIN
L_00079166:
    exts.w r5,r12
    .org 0x79168-ORIGIN
L_00079168:
    mov r12,r5
    .org 0x7916a-ORIGIN
L_0007916a:
    mov.w @(0x16,r2),r0
    .org 0x7916c-ORIGIN
L_0007916c:
    cmp/ge r0,r12
    .org 0x7916e-ORIGIN
L_0007916e:
    bt/s L_00079174
    .org 0x79170-ORIGIN
L_00079170:
    mov r0,r11
    .org 0x79172-ORIGIN
L_00079172:
    mov r11,r5
    .org 0x79174-ORIGIN
L_00079174:
    mov.l P_00079234,r3
    .org 0x79176-ORIGIN
L_00079176:
    exts.w r5,r14
    .org 0x79178-ORIGIN
L_00079178:
    mov.w @(0x14,r3),r0
    .org 0x7917a-ORIGIN
L_0007917a:
    cmp/gt r0,r14
    .org 0x7917c-ORIGIN
L_0007917c:
    bf/s L_00079182
    .org 0x7917e-ORIGIN
L_0007917e:
    mov r0,r5
    .org 0x79180-ORIGIN
L_00079180:
    mov r5,r14
    .org 0x79182-ORIGIN
L_00079182:
    mov.l P_00079228,r3
    .org 0x79184-ORIGIN
L_00079184:
    exts.w r14,r13
    .org 0x79186-ORIGIN
L_00079186:
    mov.w P_00079214,r0
    .org 0x79188-ORIGIN
L_00079188:
    mov.w @(r0,r3),r14
    .org 0x7918a-ORIGIN
L_0007918a:
    cmp/gt r14,r13
    .org 0x7918c-ORIGIN
L_0007918c:
    bt L_00079190
    .org 0x7918e-ORIGIN
L_0007918e:
    mov r13,r14
    .org 0x79190-ORIGIN
L_00079190:
    exts.w r14,r2
    .org 0x79192-ORIGIN
L_00079192:
    exts.w r7,r7
    .org 0x79194-ORIGIN
L_00079194:
    cmp/gt r7,r2
    .org 0x79196-ORIGIN
L_00079196:
    bf L_0007919c
    .org 0x79198-ORIGIN
L_00079198:
    bra L_0007919e
    .org 0x7919a-ORIGIN
L_0007919a:
    exts.w r7,r7
    .org 0x7919c-ORIGIN
L_0007919c:
    mov r2,r7
    .org 0x7919e-ORIGIN
L_0007919e:
    mov r9,r0
    .org 0x791a0-ORIGIN
L_000791a0:
    tst #0x1,r0
    .org 0x791a2-ORIGIN
L_000791a2:
    bt L_000791ae
    .org 0x791a4-ORIGIN
L_000791a4:
    mov.l P_00079224,r3
    .org 0x791a6-ORIGIN
L_000791a6:
    mov.w P_00079216,r0
    .org 0x791a8-ORIGIN
L_000791a8:
    mov.w r13,@(r0,r3)
    .org 0x791aa-ORIGIN
L_000791aa:
    bra L_000791b4
    .org 0x791ac-ORIGIN
L_000791ac:
    nop
    .org 0x791ae-ORIGIN
L_000791ae:
    mov.l P_00079224,r3
    .org 0x791b0-ORIGIN
L_000791b0:
    mov.w P_00079216,r0
    .org 0x791b2-ORIGIN
L_000791b2:
    mov.w r7,@(r0,r3)
    .org 0x791b4-ORIGIN
L_000791b4:
    cmp/gt r4,r12
    .org 0x791b6-ORIGIN
L_000791b6:
    mov r10,r0
    .org 0x791b8-ORIGIN
L_000791b8:
    bf/s L_000791be
    .org 0x791ba-ORIGIN
L_000791ba:
    and #0xef,r0
    .org 0x791bc-ORIGIN
L_000791bc:
    or #0x10,r0
    .org 0x791be-ORIGIN
L_000791be:
    exts.w r5,r5
    .org 0x791c0-ORIGIN
L_000791c0:
    cmp/gt r5,r6
    .org 0x791c2-ORIGIN
L_000791c2:
    bf/s L_000791ca
    .org 0x791c4-ORIGIN
L_000791c4:
    mov.b r0,@(0x7,r8)
    .org 0x791c6-ORIGIN
L_000791c6:
    exts.w r5,r5
    .org 0x791c8-ORIGIN
L_000791c8:
    mov r5,r6
    .org 0x791ca-ORIGIN
L_000791ca:
    exts.w r6,r6
    .org 0x791cc-ORIGIN
L_000791cc:
    exts.w r11,r11
    .org 0x791ce-ORIGIN
L_000791ce:
    cmp/ge r11,r6
    .org 0x791d0-ORIGIN
L_000791d0:
    bt L_000791d6
    .org 0x791d2-ORIGIN
L_000791d2:
    exts.w r11,r11
    .org 0x791d4-ORIGIN
L_000791d4:
    mov r11,r6
    .org 0x791d6-ORIGIN
L_000791d6:
    mov.l P_00079234,r3
    .org 0x791d8-ORIGIN
L_000791d8:
    exts.w r4,r4
    .org 0x791da-ORIGIN
L_000791da:
    exts.w r5,r5
    .org 0x791dc-ORIGIN
L_000791dc:
    mov #0x3a,r0
    .org 0x791de-ORIGIN
L_000791de:
    cmp/gt r5,r4
    .org 0x791e0-ORIGIN
L_000791e0:
    mov.w r6,@(r0,r3)
    .org 0x791e2-ORIGIN
L_000791e2:
    bf L_000791e8
    .org 0x791e4-ORIGIN
L_000791e4:
    bra L_000791ea
    .org 0x791e6-ORIGIN
L_000791e6:
    exts.w r5,r2
    .org 0x791e8-ORIGIN
L_000791e8:
    exts.w r4,r2
    .org 0x791ea-ORIGIN
L_000791ea:
    exts.w r2,r6
    .org 0x791ec-ORIGIN
L_000791ec:
    exts.w r11,r11
    .org 0x791ee-ORIGIN
L_000791ee:
    cmp/ge r11,r6
    .org 0x791f0-ORIGIN
L_000791f0:
    bt L_000791f4
    .org 0x791f2-ORIGIN
L_000791f2:
    exts.w r11,r6
    .org 0x791f4-ORIGIN
L_000791f4:
    mov.l P_00079234,r3
    .org 0x791f6-ORIGIN
L_000791f6:
    mov #0x3c,r0
    .org 0x791f8-ORIGIN
L_000791f8:
    mov.w r6,@(r0,r3)
    .org 0x791fa-ORIGIN
L_000791fa:
    mov.l @r15+,r14
    .org 0x791fc-ORIGIN
L_000791fc:
    mov.l @r15+,r13
    .org 0x791fe-ORIGIN
L_000791fe:
    mov.l @r15+,r12
    .org 0x79200-ORIGIN
L_00079200:
    mov.l @r15+,r11
    .org 0x79202-ORIGIN
L_00079202:
    mov.l @r15+,r10
    .org 0x79204-ORIGIN
L_00079204:
    mov.l @r15+,r9
    .org 0x79206-ORIGIN
L_00079206:
    rts
    .org 0x79208-ORIGIN
L_00079208:
    mov.l @r15+,r8
    .org 0x7920a-ORIGIN
P_0007920a:
    .byte 0x0b
    .org 0x7920b-ORIGIN
P_0007920b:
    .byte 0x8a
    .org 0x7920c-ORIGIN
P_0007920c:
    .byte 0x0b
    .org 0x7920d-ORIGIN
P_0007920d:
    .byte 0x86
    .org 0x7920e-ORIGIN
P_0007920e:
    .byte 0x07
    .org 0x7920f-ORIGIN
P_0007920f:
    .byte 0x40
    .org 0x79210-ORIGIN
P_00079210:
    .byte 0x0b
    .org 0x79211-ORIGIN
P_00079211:
    .byte 0x8c
    .org 0x79212-ORIGIN
P_00079212:
    .byte 0x0b
    .org 0x79213-ORIGIN
P_00079213:
    .byte 0x88
    .org 0x79214-ORIGIN
P_00079214:
    .byte 0x0b
    .org 0x79215-ORIGIN
P_00079215:
    .byte 0xa2
    .org 0x79216-ORIGIN
P_00079216:
    .byte 0x07
    .org 0x79217-ORIGIN
P_00079217:
    .byte 0x3a
    .org 0x79218-ORIGIN
P_00079218:
    .byte 0xff
    .org 0x79219-ORIGIN
P_00079219:
    .byte 0xff
    .org 0x7921a-ORIGIN
P_0007921a:
    .byte 0x41
    .org 0x7921b-ORIGIN
P_0007921b:
    .byte 0xa9
    .org 0x7921c-ORIGIN
P_0007921c:
    .byte 0xff
    .org 0x7921d-ORIGIN
P_0007921d:
    .byte 0xff
    .org 0x7921e-ORIGIN
P_0007921e:
    .byte 0x42
    .org 0x7921f-ORIGIN
P_0007921f:
    .byte 0x4c
    .org 0x79220-ORIGIN
P_00079220:
    .byte 0xff
    .org 0x79221-ORIGIN
P_00079221:
    .byte 0xff
    .org 0x79222-ORIGIN
P_00079222:
    .byte 0x23
    .org 0x79223-ORIGIN
P_00079223:
    .byte 0xbc
    .org 0x79224-ORIGIN
P_00079224:
    .byte 0xff
    .org 0x79225-ORIGIN
P_00079225:
    .byte 0xff
    .org 0x79226-ORIGIN
P_00079226:
    .byte 0x12
    .org 0x79227-ORIGIN
P_00079227:
    .byte 0x8c
    .org 0x79228-ORIGIN
P_00079228:
    .byte 0xff
    .org 0x79229-ORIGIN
P_00079229:
    .byte 0xff
    .org 0x7922a-ORIGIN
P_0007922a:
    .byte 0x28
    .org 0x7922b-ORIGIN
P_0007922b:
    .byte 0xf8
    .org 0x7922c-ORIGIN
P_0007922c:
    .byte 0x00
    .org 0x7922d-ORIGIN
P_0007922d:
    .byte 0x00
    .org 0x7922e-ORIGIN
P_0007922e:
    .byte 0x8b
    .org 0x7922f-ORIGIN
P_0007922f:
    .byte 0x38
    .org 0x79230-ORIGIN
P_00079230:
    .byte 0x00
    .org 0x79231-ORIGIN
P_00079231:
    .byte 0x00
    .org 0x79232-ORIGIN
P_00079232:
    .byte 0x83
    .org 0x79233-ORIGIN
P_00079233:
    .byte 0xc1
    .org 0x79234-ORIGIN
P_00079234:
    .byte 0xff
    .org 0x79235-ORIGIN
P_00079235:
    .byte 0xff
    .org 0x79236-ORIGIN
P_00079236:
    .byte 0x41
    .org 0x79237-ORIGIN
P_00079237:
    .byte 0x24
    .org 0x79358-ORIGIN
L_00079358:
    mov.l r14,@-r15
    .org 0x7935a-ORIGIN
L_0007935a:
    sts.l pr,@-r15
    .org 0x7935c-ORIGIN
L_0007935c:
    mov.l P_000795bc,r14
    .org 0x7935e-ORIGIN
L_0007935e:
    mov #-0x1,r5
    .org 0x79360-ORIGIN
L_00079360:
    mov.w P_000793cc,r0
    .org 0x79362-ORIGIN
L_00079362:
    extu.b r5,r5
    .org 0x79364-ORIGIN
L_00079364:
    mov.b @(r0,r14),r7
    .org 0x79366-ORIGIN
L_00079366:
    extu.b r7,r7
    .org 0x79368-ORIGIN
L_00079368:
    mov r7,r6
    .org 0x7936a-ORIGIN
L_0007936a:
    add #0xa,r6
    .org 0x7936c-ORIGIN
L_0007936c:
    extu.w r6,r6
    .org 0x7936e-ORIGIN
L_0007936e:
    cmp/gt r5,r6
    .org 0x79370-ORIGIN
L_00079370:
    bf L_00079376
    .org 0x79372-ORIGIN
L_00079372:
    mov #-0x1,r6
    .org 0x79374-ORIGIN
L_00079374:
    extu.b r6,r6
    .org 0x79376-ORIGIN
L_00079376:
    mov.w P_000793ce,r0
    .org 0x79378-ORIGIN
L_00079378:
    extu.w r6,r2
    .org 0x7937a-ORIGIN
L_0007937a:
    mov.b @(r0,r14),r4
    .org 0x7937c-ORIGIN
L_0007937c:
    extu.b r4,r4
    .org 0x7937e-ORIGIN
L_0007937e:
    cmp/ge r2,r4
    .org 0x79380-ORIGIN
L_00079380:
    bt/s L_00079386
    .org 0x79382-ORIGIN
L_00079382:
    mov r6,r5
    .org 0x79384-ORIGIN
L_00079384:
    mov r4,r5
    .org 0x79386-ORIGIN
L_00079386:
    extu.w r5,r6
    .org 0x79388-ORIGIN
L_00079388:
    cmp/gt r7,r6
    .org 0x7938a-ORIGIN
L_0007938a:
    bf L_00079392
    .org 0x7938c-ORIGIN
L_0007938c:
    mov.w P_000793ce,r0
    .org 0x7938e-ORIGIN
L_0007938e:
    bra L_00079398
    .org 0x79390-ORIGIN
L_00079390:
    mov.b r6,@(r0,r14)
    .org 0x79392-ORIGIN
L_00079392:
    mov.w P_000793ce,r0
    .org 0x79394-ORIGIN
L_00079394:
    mov r7,r6
    .org 0x79396-ORIGIN
L_00079396:
    mov.b r7,@(r0,r14)
    .org 0x79398-ORIGIN
L_00079398:
    mov.l P_000795c0,r2
    .org 0x7939a-ORIGIN
L_0007939a:
    mov.b @r2,r0
    .org 0x7939c-ORIGIN
L_0007939c:
    tst #0x2,r0
    .org 0x7939e-ORIGIN
L_0007939e:
    bt L_000793be
    .org 0x793a0-ORIGIN
L_000793a0:
    extu.b r6,r6
    .org 0x793a2-ORIGIN
L_000793a2:
    mov r6,r1
    .org 0x793a4-ORIGIN
L_000793a4:
    shll r1
    .org 0x793a6-ORIGIN
L_000793a6:
    add r6,r1
    .org 0x793a8-ORIGIN
L_000793a8:
    mov.l P_000795c4,r6
    .org 0x793aa-ORIGIN
L_000793aa:
    mov #-0x1,r5
    .org 0x793ac-ORIGIN
L_000793ac:
    shll r1
    .org 0x793ae-ORIGIN
L_000793ae:
    jsr @r6
    .org 0x793b0-ORIGIN
L_000793b0:
    extu.b r5,r0
    .org 0x793b2-ORIGIN
L_000793b2:
    mov #0x6,r6
    .org 0x793b4-ORIGIN
L_000793b4:
    sub r0,r6
    .org 0x793b6-ORIGIN
L_000793b6:
    extu.b r6,r2
    .org 0x793b8-ORIGIN
L_000793b8:
    shll r2
    .org 0x793ba-ORIGIN
L_000793ba:
    bra L_000793c0
    .org 0x793bc-ORIGIN
L_000793bc:
    add r6,r2
    .org 0x793be-ORIGIN
L_000793be:
    mov #0x0,r2
    .org 0x793c0-ORIGIN
L_000793c0:
    mov.l P_000795c8,r5
    .org 0x793c2-ORIGIN
L_000793c2:
    mov.w P_000793d0,r0
    .org 0x793c4-ORIGIN
L_000793c4:
    mov.b r2,@(r0,r5)
    .org 0x793c6-ORIGIN
L_000793c6:
    lds.l @r15+,pr
    .org 0x793c8-ORIGIN
L_000793c8:
    rts
    .org 0x793ca-ORIGIN
L_000793ca:
    mov.l @r15+,r14
    .org 0x793cc-ORIGIN
P_000793cc:
    .byte 0x05
    .org 0x793cd-ORIGIN
P_000793cd:
    .byte 0xd8
    .org 0x793ce-ORIGIN
P_000793ce:
    .byte 0x05
    .org 0x793cf-ORIGIN
P_000793cf:
    .byte 0xdf
    .org 0x793d0-ORIGIN
P_000793d0:
    .byte 0x0a
    .org 0x793d1-ORIGIN
P_000793d1:
    .byte 0x73
    .org 0x793d2-ORIGIN
L_000793d2:
    mov.l r8,@-r15
    .org 0x793d4-ORIGIN
L_000793d4:
    mov.l r9,@-r15
    .org 0x793d6-ORIGIN
L_000793d6:
    mov.l r10,@-r15
    .org 0x793d8-ORIGIN
L_000793d8:
    mov.l r11,@-r15
    .org 0x793da-ORIGIN
L_000793da:
    mov.l r12,@-r15
    .org 0x793dc-ORIGIN
L_000793dc:
    mov.l r13,@-r15
    .org 0x793de-ORIGIN
L_000793de:
    sts.l pr,@-r15
    .org 0x793e0-ORIGIN
L_000793e0:
    stc.l gbr,@-r15
    .org 0x793e2-ORIGIN
L_000793e2:
    mov.l P_000795cc,r0
    .org 0x793e4-ORIGIN
L_000793e4:
    ldc r0,gbr
    .org 0x793e6-ORIGIN
L_000793e6:
    add #-0x1c,r15
    .org 0x793e8-ORIGIN
L_000793e8:
    mov.l P_000795d0,r5
    .org 0x793ea-ORIGIN
L_000793ea:
    mov.l P_000795d4,r4
    .org 0x793ec-ORIGIN
L_000793ec:
    mov.b @(0x5,r5),r0
    .org 0x793ee-ORIGIN
L_000793ee:
    mov.l P_000795d8,r2
    .org 0x793f0-ORIGIN
L_000793f0:
    mov.l P_000795c8,r8
    .org 0x793f2-ORIGIN
L_000793f2:
    jsr @r2
    .org 0x793f4-ORIGIN
L_000793f4:
    extu.b r0,r5
    .org 0x793f6-ORIGIN
L_000793f6:
    mov r0,r2
    .org 0x793f8-ORIGIN
L_000793f8:
    mov.w P_00079532,r0
    .org 0x793fa-ORIGIN
L_000793fa:
    mov.l P_000795dc,r10
    .org 0x793fc-ORIGIN
L_000793fc:
    extu.b r2,r5
    .org 0x793fe-ORIGIN
L_000793fe:
    mov.l P_000795e0,r9
    .org 0x79400-ORIGIN
L_00079400:
    mov.b r2,@(r0,r8)
    .org 0x79402-ORIGIN
L_00079402:
    mov #0x16,r0
    .org 0x79404-ORIGIN
L_00079404:
    mov.b @(r0,r10),r13
    .org 0x79406-ORIGIN
L_00079406:
    mov.b @(0x1,r9),r0
    .org 0x79408-ORIGIN
L_00079408:
    extu.b r13,r4
    .org 0x7940a-ORIGIN
L_0007940a:
    extu.b r0,r2
    .org 0x7940c-ORIGIN
L_0007940c:
    mov.b @(0x86,gbr),r0
    .org 0x7940e-ORIGIN
L_0007940e:
    add r2,r5
    .org 0x79410-ORIGIN
L_00079410:
    extu.b r0,r0
    .org 0x79412-ORIGIN
L_00079412:
    mov.l r5,@r15
    .org 0x79414-ORIGIN
L_00079414:
    tst #0x2,r0
    .org 0x79416-ORIGIN
L_00079416:
    movt r2
    .org 0x79418-ORIGIN
L_00079418:
    mov.l P_000795e4,r11
    .org 0x7941a-ORIGIN
L_0007941a:
    add #-0x1,r2
    .org 0x7941c-ORIGIN
L_0007941c:
    neg r2,r7
    .org 0x7941e-ORIGIN
L_0007941e:
    extu.b r7,r7
    .org 0x79420-ORIGIN
L_00079420:
    jsr @r11
    .org 0x79422-ORIGIN
L_00079422:
    mov #0x4,r6
    .org 0x79424-ORIGIN
L_00079424:
    mov.b r0,@(0x4,r15)
    .org 0x79426-ORIGIN
L_00079426:
    mov.b @(0x86,gbr),r0
    .org 0x79428-ORIGIN
L_00079428:
    mov r0,r6
    .org 0x7942a-ORIGIN
L_0007942a:
    mov.b @(0x4,r15),r0
    .org 0x7942c-ORIGIN
L_0007942c:
    tst #0x1,r0
    .org 0x7942e-ORIGIN
L_0007942e:
    mov r6,r0
    .org 0x79430-ORIGIN
L_00079430:
    bf/s L_00079436
    .org 0x79432-ORIGIN
L_00079432:
    or #0x2,r0
    .org 0x79434-ORIGIN
L_00079434:
    and #0xfd,r0
    .org 0x79436-ORIGIN
L_00079436:
    mov.b r0,@(0x86,gbr)
    .org 0x79438-ORIGIN
L_00079438:
    mov.b @(0x4,r9),r0
    .org 0x7943a-ORIGIN
L_0007943a:
    mov.l P_000795e8,r2
    .org 0x7943c-ORIGIN
L_0007943c:
    extu.b r0,r5
    .org 0x7943e-ORIGIN
L_0007943e:
    mov.b @(0x87,gbr),r0
    .org 0x79440-ORIGIN
L_00079440:
    mov.w @r2,r12
    .org 0x79442-ORIGIN
L_00079442:
    extu.b r0,r0
    .org 0x79444-ORIGIN
L_00079444:
    tst #0x80,r0
    .org 0x79446-ORIGIN
L_00079446:
    extu.w r12,r4
    .org 0x79448-ORIGIN
L_00079448:
    movt r2
    .org 0x7944a-ORIGIN
L_0007944a:
    add #-0x1,r2
    .org 0x7944c-ORIGIN
L_0007944c:
    neg r2,r7
    .org 0x7944e-ORIGIN
L_0007944e:
    extu.b r7,r7
    .org 0x79450-ORIGIN
L_00079450:
    jsr @r11
    .org 0x79452-ORIGIN
L_00079452:
    mov #0x5,r6
    .org 0x79454-ORIGIN
L_00079454:
    mov.b r0,@(0x8,r15)
    .org 0x79456-ORIGIN
L_00079456:
    mov.b @(0x87,gbr),r0
    .org 0x79458-ORIGIN
L_00079458:
    mov r0,r6
    .org 0x7945a-ORIGIN
L_0007945a:
    mov.b @(0x8,r15),r0
    .org 0x7945c-ORIGIN
L_0007945c:
    tst #0x1,r0
    .org 0x7945e-ORIGIN
L_0007945e:
    mov r6,r0
    .org 0x79460-ORIGIN
L_00079460:
    bf/s L_00079466
    .org 0x79462-ORIGIN
L_00079462:
    or #0x80,r0
    .org 0x79464-ORIGIN
L_00079464:
    and #0x7f,r0
    .org 0x79466-ORIGIN
L_00079466:
    mov.b r0,@(0x87,gbr)
    .org 0x79468-ORIGIN
L_00079468:
    mov #0x16,r0
    .org 0x7946a-ORIGIN
L_0007946a:
    mov.b @(r0,r10),r6
    .org 0x7946c-ORIGIN
L_0007946c:
    mov.w P_00079532,r0
    .org 0x7946e-ORIGIN
L_0007946e:
    extu.b r6,r4
    .org 0x79470-ORIGIN
L_00079470:
    mov.b @(r0,r8),r13
    .org 0x79472-ORIGIN
L_00079472:
    mov #0x4,r6
    .org 0x79474-ORIGIN
L_00079474:
    mov.b @(0x86,gbr),r0
    .org 0x79476-ORIGIN
L_00079476:
    extu.b r13,r5
    .org 0x79478-ORIGIN
L_00079478:
    and #0x1,r0
    .org 0x7947a-ORIGIN
L_0007947a:
    jsr @r11
    .org 0x7947c-ORIGIN
L_0007947c:
    mov r0,r7
    .org 0x7947e-ORIGIN
L_0007947e:
    mov.b r0,@(0xc,r15)
    .org 0x79480-ORIGIN
L_00079480:
    mov.b @(0x86,gbr),r0
    .org 0x79482-ORIGIN
L_00079482:
    mov r0,r6
    .org 0x79484-ORIGIN
L_00079484:
    mov.b @(0xc,r15),r0
    .org 0x79486-ORIGIN
L_00079486:
    tst #0x1,r0
    .org 0x79488-ORIGIN
L_00079488:
    mov r6,r0
    .org 0x7948a-ORIGIN
L_0007948a:
    bf/s L_00079490
    .org 0x7948c-ORIGIN
L_0007948c:
    or #0x1,r0
    .org 0x7948e-ORIGIN
L_0007948e:
    and #0xfe,r0
    .org 0x79490-ORIGIN
L_00079490:
    mov.b r0,@(0x86,gbr)
    .org 0x79492-ORIGIN
L_00079492:
    mov #0x16,r0
    .org 0x79494-ORIGIN
L_00079494:
    mov.b @(r0,r10),r13
    .org 0x79496-ORIGIN
L_00079496:
    mov.w P_00079532,r0
    .org 0x79498-ORIGIN
L_00079498:
    mov.b @r9,r2
    .org 0x7949a-ORIGIN
L_0007949a:
    extu.b r13,r4
    .org 0x7949c-ORIGIN
L_0007949c:
    mov.b @(r0,r8),r6
    .org 0x7949e-ORIGIN
L_0007949e:
    mov.b @(0x86,gbr),r0
    .org 0x794a0-ORIGIN
L_000794a0:
    extu.b r2,r2
    .org 0x794a2-ORIGIN
L_000794a2:
    extu.b r6,r5
    .org 0x794a4-ORIGIN
L_000794a4:
    extu.b r0,r0
    .org 0x794a6-ORIGIN
L_000794a6:
    add r2,r5
    .org 0x794a8-ORIGIN
L_000794a8:
    tst #0x4,r0
    .org 0x794aa-ORIGIN
L_000794aa:
    mov.l r5,@(0x10,r15)
    .org 0x794ac-ORIGIN
L_000794ac:
    movt r2
    .org 0x794ae-ORIGIN
L_000794ae:
    add #-0x1,r2
    .org 0x794b0-ORIGIN
L_000794b0:
    neg r2,r7
    .org 0x794b2-ORIGIN
L_000794b2:
    mov #0x4,r6
    .org 0x794b4-ORIGIN
L_000794b4:
    jsr @r11
    .org 0x794b6-ORIGIN
L_000794b6:
    extu.b r7,r7
    .org 0x794b8-ORIGIN
L_000794b8:
    mov r0,r2
    .org 0x794ba-ORIGIN
L_000794ba:
    mov #0x14,r0
    .org 0x794bc-ORIGIN
L_000794bc:
    mov.b r2,@(r0,r15)
    .org 0x794be-ORIGIN
L_000794be:
    mov.b @(0x86,gbr),r0
    .org 0x794c0-ORIGIN
L_000794c0:
    mov r0,r6
    .org 0x794c2-ORIGIN
L_000794c2:
    mov #0x14,r0
    .org 0x794c4-ORIGIN
L_000794c4:
    mov.b @(r0,r15),r0
    .org 0x794c6-ORIGIN
L_000794c6:
    tst #0x1,r0
    .org 0x794c8-ORIGIN
L_000794c8:
    mov r6,r0
    .org 0x794ca-ORIGIN
L_000794ca:
    bf/s L_000794d0
    .org 0x794cc-ORIGIN
L_000794cc:
    or #0x4,r0
    .org 0x794ce-ORIGIN
L_000794ce:
    and #0xfb,r0
    .org 0x794d0-ORIGIN
L_000794d0:
    mov.b r0,@(0x86,gbr)
    .org 0x794d2-ORIGIN
L_000794d2:
    mov.b @(0x0,gbr),r0
    .org 0x794d4-ORIGIN
L_000794d4:
    tst #0x40,r0
    .org 0x794d6-ORIGIN
L_000794d6:
    bf L_00079518
    .org 0x794d8-ORIGIN
L_000794d8:
    mov.l P_000795ec,r6
    .org 0x794da-ORIGIN
L_000794da:
    mov.b @r6,r0
    .org 0x794dc-ORIGIN
L_000794dc:
    tst #0x2,r0
    .org 0x794de-ORIGIN
L_000794de:
    bf L_00079518
    .org 0x794e0-ORIGIN
L_000794e0:
    mov.b @(0x86,gbr),r0
    .org 0x794e2-ORIGIN
L_000794e2:
    mov r0,r6
    .org 0x794e4-ORIGIN
L_000794e4:
    mov #0x18,r0
    .org 0x794e6-ORIGIN
L_000794e6:
    mov.b r6,@(r0,r15)
    .org 0x794e8-ORIGIN
L_000794e8:
    mov r6,r0
    .org 0x794ea-ORIGIN
L_000794ea:
    tst #0x2,r0
    .org 0x794ec-ORIGIN
L_000794ec:
    bt L_000794f4
    .org 0x794ee-ORIGIN
L_000794ee:
    mov.b @(0x87,gbr),r0
    .org 0x794f0-ORIGIN
L_000794f0:
    tst #0x80,r0
    .org 0x794f2-ORIGIN
L_000794f2:
    bf L_00079518
    .org 0x794f4-ORIGIN
L_000794f4:
    mov #0x18,r0
    .org 0x794f6-ORIGIN
L_000794f6:
    mov.b @(r0,r15),r0
    .org 0x794f8-ORIGIN
L_000794f8:
    tst #0x1,r0
    .org 0x794fa-ORIGIN
L_000794fa:
    bf L_00079518
    .org 0x794fc-ORIGIN
L_000794fc:
    tst #0x4,r0
    .org 0x794fe-ORIGIN
L_000794fe:
    mov.w P_00079534,r0
    .org 0x79500-ORIGIN
L_00079500:
    bt L_00079514
    .org 0x79502-ORIGIN
L_00079502:
    mov.l P_000795f0,r2
    .org 0x79504-ORIGIN
L_00079504:
    mov.b @(r0,r8),r5
    .org 0x79506-ORIGIN
L_00079506:
    mov.b @r2,r4
    .org 0x79508-ORIGIN
L_00079508:
    extu.b r5,r5
    .org 0x7950a-ORIGIN
L_0007950a:
    extu.b r4,r2
    .org 0x7950c-ORIGIN
L_0007950c:
    cmp/gt r2,r5
    .org 0x7950e-ORIGIN
L_0007950e:
    bt L_0007951a
    .org 0x79510-ORIGIN
L_00079510:
    bra L_0007951a
    .org 0x79512-ORIGIN
L_00079512:
    mov r5,r2
    .org 0x79514-ORIGIN
L_00079514:
    bra L_0007951a
    .org 0x79516-ORIGIN
L_00079516:
    mov.b @(r0,r8),r2
    .org 0x79518-ORIGIN
L_00079518:
    mov #0x0,r2
    .org 0x7951a-ORIGIN
L_0007951a:
    mov.w P_00079536,r0
    .org 0x7951c-ORIGIN
L_0007951c:
    mov.b r2,@(r0,r8)
    .org 0x7951e-ORIGIN
L_0007951e:
    add #0x1c,r15
    .org 0x79520-ORIGIN
L_00079520:
    ldc.l @r15+,gbr
    .org 0x79522-ORIGIN
L_00079522:
    lds.l @r15+,pr
    .org 0x79524-ORIGIN
L_00079524:
    mov.l @r15+,r13
    .org 0x79526-ORIGIN
L_00079526:
    mov.l @r15+,r12
    .org 0x79528-ORIGIN
L_00079528:
    mov.l @r15+,r11
    .org 0x7952a-ORIGIN
L_0007952a:
    mov.l @r15+,r10
    .org 0x7952c-ORIGIN
L_0007952c:
    mov.l @r15+,r9
    .org 0x7952e-ORIGIN
L_0007952e:
    rts
    .org 0x79530-ORIGIN
L_00079530:
    mov.l @r15+,r8
    .org 0x79532-ORIGIN
P_00079532:
    .byte 0x0c
    .org 0x79533-ORIGIN
P_00079533:
    .byte 0x23
    .org 0x79534-ORIGIN
P_00079534:
    .byte 0x0a
    .org 0x79535-ORIGIN
P_00079535:
    .byte 0x73
    .org 0x79536-ORIGIN
P_00079536:
    .byte 0x0a
    .org 0x79537-ORIGIN
P_00079537:
    .byte 0x70
    .org 0x79538-ORIGIN
L_00079538:
    mov.l r11,@-r15
    .org 0x7953a-ORIGIN
L_0007953a:
    mov.l r12,@-r15
    .org 0x7953c-ORIGIN
L_0007953c:
    mov.l r13,@-r15
    .org 0x7953e-ORIGIN
L_0007953e:
    mov.l r14,@-r15
    .org 0x79540-ORIGIN
L_00079540:
    sts.l pr,@-r15
    .org 0x79542-ORIGIN
L_00079542:
    sts.l macl,@-r15
    .org 0x79544-ORIGIN
L_00079544:
    stc.l gbr,@-r15
    .org 0x79546-ORIGIN
L_00079546:
    mov.l P_000795f4,r0
    .org 0x79548-ORIGIN
L_00079548:
    ldc r0,gbr
    .org 0x7954a-ORIGIN
L_0007954a:
    add #-0x10,r15
    .org 0x7954c-ORIGIN
L_0007954c:
    mov.l P_000795c8,r11
    .org 0x7954e-ORIGIN
L_0007954e:
    mov #0x0,r12
    .org 0x79550-ORIGIN
L_00079550:
    mov.w P_000795b4,r0
    .org 0x79552-ORIGIN
L_00079552:
    mov.b @(r0,r11),r7
    .org 0x79554-ORIGIN
L_00079554:
    mov.w P_000795b6,r0
    .org 0x79556-ORIGIN
L_00079556:
    extu.b r7,r7
    .org 0x79558-ORIGIN
L_00079558:
    mov.b @(r0,r11),r4
    .org 0x7955a-ORIGIN
L_0007955a:
    extu.b r4,r2
    .org 0x7955c-ORIGIN
L_0007955c:
    cmp/ge r2,r7
    .org 0x7955e-ORIGIN
L_0007955e:
    bf/s L_00079564
    .org 0x79560-ORIGIN
L_00079560:
    mov r12,r5
    .org 0x79562-ORIGIN
L_00079562:
    mov r7,r2
    .org 0x79564-ORIGIN
L_00079564:
    mov.w P_000795b8,r0
    .org 0x79566-ORIGIN
L_00079566:
    extu.b r2,r4
    .org 0x79568-ORIGIN
L_00079568:
    mov.l P_000795cc,r6
    .org 0x7956a-ORIGIN
L_0007956a:
    mov.b r4,@(r0,r11)
    .org 0x7956c-ORIGIN
L_0007956c:
    mov.b @r6,r0
    .org 0x7956e-ORIGIN
L_0007956e:
    tst #0x80,r0
    .org 0x79570-ORIGIN
L_00079570:
    bt L_0007957a
    .org 0x79572-ORIGIN
L_00079572:
    mov.l P_000795ec,r6
    .org 0x79574-ORIGIN
L_00079574:
    mov.b @r6,r0
    .org 0x79576-ORIGIN
L_00079576:
    tst #0x20,r0
    .org 0x79578-ORIGIN
L_00079578:
    bf L_00079582
    .org 0x7957a-ORIGIN
L_0007957a:
    mov #0x1,r5
    .org 0x7957c-ORIGIN
L_0007957c:
    mov r4,r0
    .org 0x7957e-ORIGIN
L_0007957e:
    mov r5,r12
    .org 0x79580-ORIGIN
L_00079580:
    mov.b r0,@(0x4,r15)
    .org 0x79582-ORIGIN
L_00079582:
    extu.w r5,r5
    .org 0x79584-ORIGIN
L_00079584:
    tst r5,r5
    .org 0x79586-ORIGIN
L_00079586:
    bt L_0007958c
    .org 0x79588-ORIGIN
L_00079588:
    bra L_0007974a
    .org 0x7958a-ORIGIN
L_0007958a:
    nop
    .org 0x7958c-ORIGIN
L_0007958c:
    mov.l P_000795f8,r13
    .org 0x7958e-ORIGIN
L_0007958e:
    mov #0x38,r0
    .org 0x79590-ORIGIN
L_00079590:
    mov.b @(r0,r13),r14
    .org 0x79592-ORIGIN
L_00079592:
    mov r14,r0
    .org 0x79594-ORIGIN
L_00079594:
    tst #0x1,r0
    .org 0x79596-ORIGIN
L_00079596:
    bf/s L_00079632
    .org 0x79598-ORIGIN
L_00079598:
    mov #0x3,r6
    .org 0x7959a-ORIGIN
L_0007959a:
    cmp/ge r6,r4
    .org 0x7959c-ORIGIN
L_0007959c:
    bf L_00079602
    .org 0x7959e-ORIGIN
L_0007959e:
    mov.w P_000795ba,r0
    .org 0x795a0-ORIGIN
L_000795a0:
    mov #-0x1,r5
    .org 0x795a2-ORIGIN
L_000795a2:
    extu.b r5,r5
    .org 0x795a4-ORIGIN
L_000795a4:
    mov.b @(r0,r11),r6
    .org 0x795a6-ORIGIN
L_000795a6:
    extu.b r6,r6
    .org 0x795a8-ORIGIN
L_000795a8:
    mov r6,r2
    .org 0x795aa-ORIGIN
L_000795aa:
    add #0x1,r2
    .org 0x795ac-ORIGIN
L_000795ac:
    cmp/gt r5,r2
    .org 0x795ae-ORIGIN
L_000795ae:
    bf L_000795fc
    .org 0x795b0-ORIGIN
L_000795b0:
    bra L_000795fe
    .org 0x795b2-ORIGIN
L_000795b2:
    mov #-0x1,r6
    .org 0x795b4-ORIGIN
P_000795b4:
    .byte 0x0a
    .org 0x795b5-ORIGIN
P_000795b5:
    .byte 0x70
    .org 0x795b6-ORIGIN
P_000795b6:
    .byte 0x05
    .org 0x795b7-ORIGIN
P_000795b7:
    .byte 0xcb
    .org 0x795b8-ORIGIN
P_000795b8:
    .byte 0x0a
    .org 0x795b9-ORIGIN
P_000795b9:
    .byte 0x71
    .org 0x795ba-ORIGIN
P_000795ba:
    .byte 0x0b
    .org 0x795bb-ORIGIN
P_000795bb:
    .byte 0x50
    .org 0x795bc-ORIGIN
P_000795bc:
    .byte 0xff
    .org 0x795bd-ORIGIN
P_000795bd:
    .byte 0xff
    .org 0x795be-ORIGIN
P_000795be:
    .byte 0x12
    .org 0x795bf-ORIGIN
P_000795bf:
    .byte 0x8c
    .org 0x795c0-ORIGIN
P_000795c0:
    .byte 0x00
    .org 0x795c1-ORIGIN
P_000795c1:
    .byte 0x00
    .org 0x795c2-ORIGIN
P_000795c2:
    .byte 0x8b
    .org 0x795c3-ORIGIN
P_000795c3:
    .byte 0x38
    .org 0x795c4-ORIGIN
P_000795c4:
    .byte 0x00
    .org 0x795c5-ORIGIN
P_000795c5:
    .byte 0x02
    .org 0x795c6-ORIGIN
P_000795c6:
    .byte 0x1b
    .org 0x795c7-ORIGIN
P_000795c7:
    .byte 0xbc
    .org 0x795c8-ORIGIN
P_000795c8:
    .byte 0xff
    .org 0x795c9-ORIGIN
P_000795c9:
    .byte 0xff
    .org 0x795ca-ORIGIN
P_000795ca:
    .byte 0x28
    .org 0x795cb-ORIGIN
P_000795cb:
    .byte 0xf8
    .org 0x795cc-ORIGIN
P_000795cc:
    .byte 0xff
    .org 0x795cd-ORIGIN
P_000795cd:
    .byte 0xff
    .org 0x795ce-ORIGIN
P_000795ce:
    .byte 0x41
    .org 0x795cf-ORIGIN
P_000795cf:
    .byte 0x84
    .org 0x795d0-ORIGIN
P_000795d0:
    .byte 0xff
    .org 0x795d1-ORIGIN
P_000795d1:
    .byte 0xff
    .org 0x795d2-ORIGIN
P_000795d2:
    .byte 0x10
    .org 0x795d3-ORIGIN
P_000795d3:
    .byte 0x6a
    .org 0x795d4-ORIGIN
P_000795d4:
    .byte 0x00
    .org 0x795d5-ORIGIN
P_000795d5:
    .byte 0x01
    .org 0x795d6-ORIGIN
P_000795d6:
    .byte 0x2e
    .org 0x795d7-ORIGIN
P_000795d7:
    .byte 0x1a
    .org 0x795d8-ORIGIN
P_000795d8:
    .byte 0x00
    .org 0x795d9-ORIGIN
P_000795d9:
    .byte 0x02
    .org 0x795da-ORIGIN
P_000795da:
    .byte 0x63
    .org 0x795db-ORIGIN
P_000795db:
    .byte 0x88
    .org 0x795dc-ORIGIN
P_000795dc:
    .byte 0xff
    .org 0x795dd-ORIGIN
P_000795dd:
    .byte 0xff
    .org 0x795de-ORIGIN
P_000795de:
    .byte 0x11
    .org 0x795df-ORIGIN
P_000795df:
    .byte 0x9c
    .org 0x795e0-ORIGIN
P_000795e0:
    .byte 0x00
    .org 0x795e1-ORIGIN
P_000795e1:
    .byte 0x00
    .org 0x795e2-ORIGIN
P_000795e2:
    .byte 0x8d
    .org 0x795e3-ORIGIN
P_000795e3:
    .byte 0x36
    .org 0x795e4-ORIGIN
P_000795e4:
    .byte 0x00
    .org 0x795e5-ORIGIN
P_000795e5:
    .byte 0x02
    .org 0x795e6-ORIGIN
P_000795e6:
    .byte 0x59
    .org 0x795e7-ORIGIN
P_000795e7:
    .byte 0xd0
    .org 0x795e8-ORIGIN
P_000795e8:
    .byte 0xff
    .org 0x795e9-ORIGIN
P_000795e9:
    .byte 0xff
    .org 0x795ea-ORIGIN
P_000795ea:
    .byte 0x40
    .org 0x795eb-ORIGIN
P_000795eb:
    .byte 0xc6
    .org 0x795ec-ORIGIN
P_000795ec:
    .byte 0xff
    .org 0x795ed-ORIGIN
P_000795ed:
    .byte 0xff
    .org 0x795ee-ORIGIN
P_000795ee:
    .byte 0x24
    .org 0x795ef-ORIGIN
P_000795ef:
    .byte 0x4f
    .org 0x795f0-ORIGIN
P_000795f0:
    .byte 0x00
    .org 0x795f1-ORIGIN
P_000795f1:
    .byte 0x00
    .org 0x795f2-ORIGIN
P_000795f2:
    .byte 0x88
    .org 0x795f3-ORIGIN
P_000795f3:
    .byte 0xc2
    .org 0x795f4-ORIGIN
P_000795f4:
    .byte 0xff
    .org 0x795f5-ORIGIN
P_000795f5:
    .byte 0xff
    .org 0x795f6-ORIGIN
P_000795f6:
    .byte 0x28
    .org 0x795f7-ORIGIN
P_000795f7:
    .byte 0xc8
    .org 0x795f8-ORIGIN
P_000795f8:
    .byte 0xff
    .org 0x795f9-ORIGIN
P_000795f9:
    .byte 0xff
    .org 0x795fa-ORIGIN
P_000795fa:
    .byte 0x41
    .org 0x795fb-ORIGIN
P_000795fb:
    .byte 0xa9
    .org 0x795fc-ORIGIN
L_000795fc:
    add #0x1,r6
    .org 0x795fe-ORIGIN
L_000795fe:
    mov.w P_00079706,r0
    .org 0x79600-ORIGIN
L_00079600:
    mov.b r6,@(r0,r11)
    .org 0x79602-ORIGIN
L_00079602:
    mov r4,r0
    .org 0x79604-ORIGIN
L_00079604:
    mov.b r0,@(0x4,r15)
    .org 0x79606-ORIGIN
L_00079606:
    mov.w P_00079706,r0
    .org 0x79608-ORIGIN
L_00079608:
    mov.l P_000797ec,r2
    .org 0x7960a-ORIGIN
L_0007960a:
    mov.b @(r0,r11),r7
    .org 0x7960c-ORIGIN
L_0007960c:
    mov.b @r2,r6
    .org 0x7960e-ORIGIN
L_0007960e:
    extu.b r7,r7
    .org 0x79610-ORIGIN
L_00079610:
    extu.b r6,r6
    .org 0x79612-ORIGIN
L_00079612:
    cmp/ge r6,r7
    .org 0x79614-ORIGIN
L_00079614:
    bt L_00079628
    .org 0x79616-ORIGIN
L_00079616:
    tst r7,r7
    .org 0x79618-ORIGIN
L_00079618:
    bf L_0007961e
    .org 0x7961a-ORIGIN
L_0007961a:
    bra L_0007974a
    .org 0x7961c-ORIGIN
L_0007961c:
    nop
    .org 0x7961e-ORIGIN
L_0007961e:
    mov #0x3,r2
    .org 0x79620-ORIGIN
L_00079620:
    cmp/ge r2,r4
    .org 0x79622-ORIGIN
L_00079622:
    bf L_00079628
    .org 0x79624-ORIGIN
L_00079624:
    bra L_0007974a
    .org 0x79626-ORIGIN
L_00079626:
    nop
    .org 0x79628-ORIGIN
L_00079628:
    mov #0x1,r0
    .org 0x7962a-ORIGIN
L_0007962a:
    or r0,r14
    .org 0x7962c-ORIGIN
L_0007962c:
    mov #0x38,r0
    .org 0x7962e-ORIGIN
L_0007962e:
    bra L_0007974a
    .org 0x79630-ORIGIN
L_00079630:
    mov.b r14,@(r0,r13)
    .org 0x79632-ORIGIN
L_00079632:
    cmp/ge r6,r4
    .org 0x79634-ORIGIN
L_00079634:
    bf L_00079658
    .org 0x79636-ORIGIN
L_00079636:
    mov.l P_000797f0,r5
    .org 0x79638-ORIGIN
L_00079638:
    mov.b @r5,r2
    .org 0x7963a-ORIGIN
L_0007963a:
    extu.b r2,r2
    .org 0x7963c-ORIGIN
L_0007963c:
    cmp/ge r2,r4
    .org 0x7963e-ORIGIN
L_0007963e:
    bf L_00079658
    .org 0x79640-ORIGIN
L_00079640:
    mov.l P_000797f4,r2
    .org 0x79642-ORIGIN
L_00079642:
    mov #0x12,r6
    .org 0x79644-ORIGIN
L_00079644:
    mov.b @r2,r5
    .org 0x79646-ORIGIN
L_00079646:
    extu.b r5,r5
    .org 0x79648-ORIGIN
L_00079648:
    cmp/gt r6,r5
    .org 0x7964a-ORIGIN
L_0007964a:
    bf L_0007964e
    .org 0x7964c-ORIGIN
L_0007964c:
    mov #0x12,r5
    .org 0x7964e-ORIGIN
L_0007964e:
    extu.w r5,r0
    .org 0x79650-ORIGIN
L_00079650:
    cmp/ge r0,r4
    .org 0x79652-ORIGIN
L_00079652:
    bf L_0007965a
    .org 0x79654-ORIGIN
L_00079654:
    bra L_0007965a
    .org 0x79656-ORIGIN
L_00079656:
    mov r4,r0
    .org 0x79658-ORIGIN
L_00079658:
    mov #0x0,r0
    .org 0x7965a-ORIGIN
L_0007965a:
    mov.l P_000797f8,r2
    .org 0x7965c-ORIGIN
L_0007965c:
    mov.b r0,@(0x4,r15)
    .org 0x7965e-ORIGIN
L_0007965e:
    mov.w @r2,r5
    .org 0x79660-ORIGIN
L_00079660:
    extu.w r5,r5
    .org 0x79662-ORIGIN
L_00079662:
    cmp/pz r5
    .org 0x79664-ORIGIN
L_00079664:
    bt/s L_0007966a
    .org 0x79666-ORIGIN
L_00079666:
    mov r5,r6
    .org 0x79668-ORIGIN
L_00079668:
    add #0x3,r6
    .org 0x7966a-ORIGIN
L_0007966a:
    shar r6
    .org 0x7966c-ORIGIN
L_0007966c:
    mov #-0x1,r2
    .org 0x7966e-ORIGIN
L_0007966e:
    shar r6
    .org 0x79670-ORIGIN
L_00079670:
    extu.b r2,r2
    .org 0x79672-ORIGIN
L_00079672:
    cmp/gt r2,r6
    .org 0x79674-ORIGIN
L_00079674:
    bf L_0007967a
    .org 0x79676-ORIGIN
L_00079676:
    bra L_00079686
    .org 0x79678-ORIGIN
L_00079678:
    mov #-0x1,r6
    .org 0x7967a-ORIGIN
L_0007967a:
    cmp/pz r5
    .org 0x7967c-ORIGIN
L_0007967c:
    bt/s L_00079682
    .org 0x7967e-ORIGIN
L_0007967e:
    mov r5,r6
    .org 0x79680-ORIGIN
L_00079680:
    add #0x3,r6
    .org 0x79682-ORIGIN
L_00079682:
    shar r6
    .org 0x79684-ORIGIN
L_00079684:
    shar r6
    .org 0x79686-ORIGIN
L_00079686:
    mov.l P_000797fc,r7
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
    mov.l P_00079800,r14
    .org 0x79692-ORIGIN
L_00079692:
    mov.l P_00079804,r4
    .org 0x79694-ORIGIN
L_00079694:
    extu.b r2,r7
    .org 0x79696-ORIGIN
L_00079696:
    mov.l P_00079808,r2
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
    mov.l P_000797f8,r3
    .org 0x796a2-ORIGIN
L_000796a2:
    mov r0,r6
    .org 0x796a4-ORIGIN
L_000796a4:
    mov.w P_00079708,r0
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
    mov.l P_000797fc,r3
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
    mov.l P_0007980c,r4
    .org 0x796de-ORIGIN
L_000796de:
    mov.l P_00079808,r1
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
    mov.w P_0007970a,r0
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
    mov.w P_0007970c,r0
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
    .org 0x79706-ORIGIN
P_00079706:
    .byte 0x0b
    .org 0x79707-ORIGIN
P_00079707:
    .byte 0x50
    .org 0x79708-ORIGIN
P_00079708:
    .byte 0x0c
    .org 0x79709-ORIGIN
P_00079709:
    .byte 0x24
    .org 0x7970a-ORIGIN
P_0007970a:
    .byte 0x0b
    .org 0x7970b-ORIGIN
P_0007970b:
    .byte 0x51
    .org 0x7970c-ORIGIN
P_0007970c:
    .byte 0x0b
    .org 0x7970d-ORIGIN
P_0007970d:
    .byte 0x4e
    .org 0x7970e-ORIGIN
L_0007970e:
    add #0x1,r4
    .org 0x79710-ORIGIN
L_00079710:
    mov r4,r6
    .org 0x79712-ORIGIN
L_00079712:
    mov.w P_000797de,r0
    .org 0x79714-ORIGIN
L_00079714:
    mov.w r6,@(r0,r11)
    .org 0x79716-ORIGIN
L_00079716:
    mov.w P_000797e0,r0
    .org 0x79718-ORIGIN
L_00079718:
    mov.b @(r0,r11),r4
    .org 0x7971a-ORIGIN
L_0007971a:
    mov.w P_000797e2,r0
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
    mov.l P_00079810,r4
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
    mov.w P_000797e4,r0
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
    mov.w P_000797de,r0
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
    .org 0x7974a-ORIGIN
L_0007974a:
    mov.l P_00079814,r13
    .org 0x7974c-ORIGIN
L_0007974c:
    extu.b r12,r12
    .org 0x7974e-ORIGIN
L_0007974e:
    mov #0x5b,r0
    .org 0x79750-ORIGIN
L_00079750:
    tst r12,r12
    .org 0x79752-ORIGIN
L_00079752:
    bt/s L_0007976c
    .org 0x79754-ORIGIN
L_00079754:
    mov.b @(r0,r13),r14
    .org 0x79756-ORIGIN
L_00079756:
    mov #0x38,r0
    .org 0x79758-ORIGIN
L_00079758:
    mov.b @(r0,r13),r0
    .org 0x7975a-ORIGIN
L_0007975a:
    mov #0x0,r2
    .org 0x7975c-ORIGIN
L_0007975c:
    and #0xfe,r0
    .org 0x7975e-ORIGIN
L_0007975e:
    mov r0,r6
    .org 0x79760-ORIGIN
L_00079760:
    mov #0x38,r0
    .org 0x79762-ORIGIN
L_00079762:
    mov.b r6,@(r0,r13)
    .org 0x79764-ORIGIN
L_00079764:
    mov.w P_000797e0,r0
    .org 0x79766-ORIGIN
L_00079766:
    mov.b r2,@(r0,r11)
    .org 0x79768-ORIGIN
L_00079768:
    mov.w P_000797de,r0
    .org 0x7976a-ORIGIN
L_0007976a:
    mov.w r2,@(r0,r11)
    .org 0x7976c-ORIGIN
L_0007976c:
    mov.b @(0x4,r15),r0
    .org 0x7976e-ORIGIN
L_0007976e:
    mov r0,r2
    .org 0x79770-ORIGIN
L_00079770:
    mov r0,r6
    .org 0x79772-ORIGIN
L_00079772:
    mov.w P_000797e6,r0
    .org 0x79774-ORIGIN
L_00079774:
    extu.b r2,r1
    .org 0x79776-ORIGIN
L_00079776:
    mov.b r6,@(r0,r11)
    .org 0x79778-ORIGIN
L_00079778:
    mov.l P_00079810,r6
    .org 0x7977a-ORIGIN
L_0007977a:
    jsr @r6
    .org 0x7977c-ORIGIN
L_0007977c:
    mov #0x3,r0
    .org 0x7977e-ORIGIN
L_0007977e:
    mov.l P_00079818,r5
    .org 0x79780-ORIGIN
L_00079780:
    extu.b r0,r6
    .org 0x79782-ORIGIN
L_00079782:
    mov r0,r2
    .org 0x79784-ORIGIN
L_00079784:
    mov r6,r0
    .org 0x79786-ORIGIN
L_00079786:
    mov.b r0,@(0x4,r5)
    .org 0x79788-ORIGIN
L_00079788:
    mov.w P_000797e8,r0
    .org 0x7978a-ORIGIN
L_0007978a:
    mov.b r2,@(r0,r11)
    .org 0x7978c-ORIGIN
L_0007978c:
    mov.b @(0x4,gbr),r0
    .org 0x7978e-ORIGIN
L_0007978e:
    tst r0,r0
    .org 0x79790-ORIGIN
L_00079790:
    bt L_000797a0
    .org 0x79792-ORIGIN
L_00079792:
    tst r6,r6
    .org 0x79794-ORIGIN
L_00079794:
    bf L_000797a0
    .org 0x79796-ORIGIN
L_00079796:
    mov.l P_0007981c,r5
    .org 0x79798-ORIGIN
L_00079798:
    mov #0x22,r0
    .org 0x7979a-ORIGIN
L_0007979a:
    mov.b @r5,r2
    .org 0x7979c-ORIGIN
L_0007979c:
    mov.l P_00079820,r5
    .org 0x7979e-ORIGIN
L_0007979e:
    mov.b r2,@(r0,r5)
    .org 0x797a0-ORIGIN
L_000797a0:
    tst r6,r6
    .org 0x797a2-ORIGIN
L_000797a2:
    bf L_000797b4
    .org 0x797a4-ORIGIN
L_000797a4:
    mov.l P_00079820,r5
    .org 0x797a6-ORIGIN
L_000797a6:
    mov #0x22,r0
    .org 0x797a8-ORIGIN
L_000797a8:
    mov.b @(r0,r5),r2
    .org 0x797aa-ORIGIN
L_000797aa:
    tst r2,r2
    .org 0x797ac-ORIGIN
L_000797ac:
    bf L_000797b4
    .org 0x797ae-ORIGIN
L_000797ae:
    mov r14,r0
    .org 0x797b0-ORIGIN
L_000797b0:
    bra L_000797b8
    .org 0x797b2-ORIGIN
L_000797b2:
    and #0x7f,r0
    .org 0x797b4-ORIGIN
L_000797b4:
    mov r14,r0
    .org 0x797b6-ORIGIN
L_000797b6:
    or #0x80,r0
    .org 0x797b8-ORIGIN
L_000797b8:
    mov r0,r14
    .org 0x797ba-ORIGIN
L_000797ba:
    mov #0x5b,r0
    .org 0x797bc-ORIGIN
L_000797bc:
    mov.b r14,@(r0,r13)
    .org 0x797be-ORIGIN
L_000797be:
    add #0x10,r15
    .org 0x797c0-ORIGIN
L_000797c0:
    ldc.l @r15+,gbr
    .org 0x797c2-ORIGIN
L_000797c2:
    lds.l @r15+,macl
    .org 0x797c4-ORIGIN
L_000797c4:
    lds.l @r15+,pr
    .org 0x797c6-ORIGIN
L_000797c6:
    mov.l @r15+,r14
    .org 0x797c8-ORIGIN
L_000797c8:
    mov.l @r15+,r13
    .org 0x797ca-ORIGIN
L_000797ca:
    mov.l @r15+,r12
    .org 0x797cc-ORIGIN
L_000797cc:
    rts
    .org 0x797ce-ORIGIN
L_000797ce:
    mov.l @r15+,r11
    .org 0x797d0-ORIGIN
L_000797d0:
    sts.l pr,@-r15
    .org 0x797d2-ORIGIN
L_000797d2:
    bsr L_00079358
    .org 0x797d4-ORIGIN
L_000797d4:
    nop
    .org 0x797d6-ORIGIN
L_000797d6:
    bsr L_000793d2
    .org 0x797d8-ORIGIN
L_000797d8:
    nop
    .org 0x797da-ORIGIN
L_000797da:
    bra L_00079538
    .org 0x797dc-ORIGIN
L_000797dc:
    lds.l @r15+,pr
    .org 0x797de-ORIGIN
P_000797de:
    .byte 0x0b
    .org 0x797df-ORIGIN
P_000797df:
    .byte 0x4e
    .org 0x797e0-ORIGIN
P_000797e0:
    .byte 0x0b
    .org 0x797e1-ORIGIN
P_000797e1:
    .byte 0x50
    .org 0x797e2-ORIGIN
P_000797e2:
    .byte 0x0c
    .org 0x797e3-ORIGIN
P_000797e3:
    .byte 0x24
    .org 0x797e4-ORIGIN
P_000797e4:
    .byte 0x0b
    .org 0x797e5-ORIGIN
P_000797e5:
    .byte 0x51
    .org 0x797e6-ORIGIN
P_000797e6:
    .byte 0x0a
    .org 0x797e7-ORIGIN
P_000797e7:
    .byte 0x72
    .org 0x797e8-ORIGIN
P_000797e8:
    .byte 0x05
    .org 0x797e9-ORIGIN
P_000797e9:
    .byte 0xd6
    .org 0x797ec-ORIGIN
P_000797ec:
    .byte 0x00
    .org 0x797ed-ORIGIN
P_000797ed:
    .byte 0x00
    .org 0x797ee-ORIGIN
P_000797ee:
    .byte 0x8c
    .org 0x797ef-ORIGIN
P_000797ef:
    .byte 0xab
    .org 0x797f0-ORIGIN
P_000797f0:
    .byte 0x00
    .org 0x797f1-ORIGIN
P_000797f1:
    .byte 0x00
    .org 0x797f2-ORIGIN
P_000797f2:
    .byte 0x88
    .org 0x797f3-ORIGIN
P_000797f3:
    .byte 0x68
    .org 0x797f4-ORIGIN
P_000797f4:
    .byte 0x00
    .org 0x797f5-ORIGIN
P_000797f5:
    .byte 0x00
    .org 0x797f6-ORIGIN
P_000797f6:
    .byte 0x88
    .org 0x797f7-ORIGIN
P_000797f7:
    .byte 0x4a
    .org 0x797f8-ORIGIN
P_000797f8:
    .byte 0xff
    .org 0x797f9-ORIGIN
P_000797f9:
    .byte 0xff
    .org 0x797fa-ORIGIN
P_000797fa:
    .byte 0x40
    .org 0x797fb-ORIGIN
P_000797fb:
    .byte 0xc6
    .org 0x797fc-ORIGIN
P_000797fc:
    .byte 0xff
    .org 0x797fd-ORIGIN
P_000797fd:
    .byte 0xff
    .org 0x797fe-ORIGIN
P_000797fe:
    .byte 0x11
    .org 0x797ff-ORIGIN
P_000797ff:
    .byte 0x9c
    .org 0x79800-ORIGIN
P_00079800:
    .byte 0x00
    .org 0x79801-ORIGIN
P_00079801:
    .byte 0x01
    .org 0x79802-ORIGIN
P_00079802:
    .byte 0x2f
    .org 0x79803-ORIGIN
P_00079803:
    .byte 0xee
    .org 0x79804-ORIGIN
P_00079804:
    .byte 0x00
    .org 0x79805-ORIGIN
P_00079805:
    .byte 0x00
    .org 0x79806-ORIGIN
P_00079806:
    .byte 0xaa
    .org 0x79807-ORIGIN
P_00079807:
    .byte 0xfa
    .org 0x79808-ORIGIN
P_00079808:
    .byte 0x00
    .org 0x79809-ORIGIN
P_00079809:
    .byte 0x02
    .org 0x7980a-ORIGIN
P_0007980a:
    .byte 0x60
    .org 0x7980b-ORIGIN
P_0007980b:
    .byte 0xbc
    .org 0x7980c-ORIGIN
P_0007980c:
    .byte 0x00
    .org 0x7980d-ORIGIN
P_0007980d:
    .byte 0x00
    .org 0x7980e-ORIGIN
P_0007980e:
    .byte 0xaa
    .org 0x7980f-ORIGIN
P_0007980f:
    .byte 0xea
    .org 0x79810-ORIGIN
P_00079810:
    .byte 0x00
    .org 0x79811-ORIGIN
P_00079811:
    .byte 0x02
    .org 0x79812-ORIGIN
P_00079812:
    .byte 0x1b
    .org 0x79813-ORIGIN
P_00079813:
    .byte 0xbc
    .org 0x79814-ORIGIN
P_00079814:
    .byte 0xff
    .org 0x79815-ORIGIN
P_00079815:
    .byte 0xff
    .org 0x79816-ORIGIN
P_00079816:
    .byte 0x41
    .org 0x79817-ORIGIN
P_00079817:
    .byte 0xa9
    .org 0x79818-ORIGIN
P_00079818:
    .byte 0xff
    .org 0x79819-ORIGIN
P_00079819:
    .byte 0xff
    .org 0x7981a-ORIGIN
P_0007981a:
    .byte 0x28
    .org 0x7981b-ORIGIN
P_0007981b:
    .byte 0x98
    .org 0x7981c-ORIGIN
P_0007981c:
    .byte 0x00
    .org 0x7981d-ORIGIN
P_0007981d:
    .byte 0x00
    .org 0x7981e-ORIGIN
P_0007981e:
    .byte 0x84
    .org 0x7981f-ORIGIN
P_0007981f:
    .byte 0x23
    .org 0x79820-ORIGIN
P_00079820:
    .byte 0xff
    .org 0x79821-ORIGIN
P_00079821:
    .byte 0xff
    .org 0x79822-ORIGIN
P_00079822:
    .byte 0x43
    .org 0x79823-ORIGIN
P_00079823:
    .byte 0xc7
    .org 0x79dd8-ORIGIN
L_00079dd8:
    sts.l pr,@-r15
    .org 0x79dda-ORIGIN
L_00079dda:
    bsr L_000797d0
    .org 0x79ddc-ORIGIN
L_00079ddc:
    nop
    .org 0x79dde-ORIGIN
L_00079dde:
    mov.l P_00079e14,r2
    .org 0x79de0-ORIGIN
L_00079de0:
    jmp @r2
    .org 0x79de2-ORIGIN
L_00079de2:
    lds.l @r15+,pr
    .org 0x79e14-ORIGIN
P_00079e14:
    .byte 0x00
    .org 0x79e15-ORIGIN
P_00079e15:
    .byte 0x07
    .org 0x79e16-ORIGIN
P_00079e16:
    .byte 0x90
    .org 0x79e17-ORIGIN
P_00079e17:
    .byte 0x30
