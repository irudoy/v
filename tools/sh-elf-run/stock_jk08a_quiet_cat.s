! Explicit stock quiet-cat entry and natural byte-lookup/division closure.
! Index zero reads 000123EA. A nonzero index reads 00012412. R0 at 000BE41E is 100.
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
    .org 0x26140-ORIGIN
L_00026140:
    sts.l pr,@-r15
    .org 0x26142-ORIGIN
L_00026142:
    mov.l r4,@-r15
    .org 0x26144-ORIGIN
L_00026144:
    extu.b r7,r7
    .org 0x26146-ORIGIN
L_00026146:
    mov r5,r0
    .org 0x26148-ORIGIN
L_00026148:
    mov r7,r5
    .org 0x2614a-ORIGIN
L_0002614a:
    mov.l L_00026174,r7
    .org 0x2614c-ORIGIN
L_0002614c:
    jsr @r7
    .org 0x2614e-ORIGIN
L_0002614e:
    mov #0x7,r4
    .org 0x26150-ORIGIN
L_00026150:
    mov.l r4,@-r15
    .org 0x26152-ORIGIN
L_00026152:
    mov.l r5,@-r15
    .org 0x26154-ORIGIN
L_00026154:
    mov r6,r0
    .org 0x26156-ORIGIN
L_00026156:
    mov.l @(0x10,r15),r5
    .org 0x26158-ORIGIN
L_00026158:
    extu.b r5,r5
    .org 0x2615a-ORIGIN
L_0002615a:
    jsr @r7
    .org 0x2615c-ORIGIN
L_0002615c:
    mov #0x7,r4
    .org 0x2615e-ORIGIN
L_0002615e:
    mov.l @r15+,r1
    .org 0x26160-ORIGIN
L_00026160:
    mov.l @r15+,r0
    .org 0x26162-ORIGIN
L_00026162:
    mov r4,r2
    .org 0x26164-ORIGIN
L_00026164:
    mov r5,r3
    .org 0x26166-ORIGIN
L_00026166:
    mov.l @r15+,r4
    .org 0x26168-ORIGIN
L_00026168:
    lds.l @r15+,pr
    .org 0x2616a-ORIGIN
L_0002616a:
    mov.l L_00026170,r7
    .org 0x2616c-ORIGIN
L_0002616c:
    jmp @r7
    .org 0x2616e-ORIGIN
L_0002616e:
    mov #0x8,r5
    .org 0x26170-ORIGIN
L_00026170:
    .long 0x00026770
    .org 0x26174-ORIGIN
L_00026174:
    .long 0x00026944
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
    mov.l L_000267c8,r7
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
L_000267c8:
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
    .org 0xbe32a-ORIGIN
L_000be32a:
    mov.l r8,@-r15
    .org 0xbe32c-ORIGIN
L_000be32c:
    mov.l r9,@-r15
    .org 0xbe32e-ORIGIN
L_000be32e:
    mov.l r10,@-r15
    .org 0xbe330-ORIGIN
L_000be330:
    mov.l r11,@-r15
    .org 0xbe332-ORIGIN
L_000be332:
    mov.l r12,@-r15
    .org 0xbe334-ORIGIN
L_000be334:
    mov.l r13,@-r15
    .org 0xbe336-ORIGIN
L_000be336:
    mov.l r14,@-r15
    .org 0xbe338-ORIGIN
L_000be338:
    sts.l pr,@-r15
    .org 0xbe33a-ORIGIN
L_000be33a:
    sts.l macl,@-r15
    .org 0xbe33c-ORIGIN
L_000be33c:
    add #-0x8,r15
    .org 0xbe33e-ORIGIN
L_000be33e:
    mov.l L_000be480,r2
    .org 0xbe340-ORIGIN
L_000be340:
    extu.b r4,r13
    .org 0xbe342-ORIGIN
L_000be342:
    mov r13,r8
    .org 0xbe344-ORIGIN
L_000be344:
    shll2 r8
    .org 0xbe346-ORIGIN
L_000be346:
    mov.b @r2,r0
    .org 0xbe348-ORIGIN
L_000be348:
    mov.l L_000be484,r4
    .org 0xbe34a-ORIGIN
L_000be34a:
    and #0x1,r0
    .org 0xbe34c-ORIGIN
L_000be34c:
    tst r0,r0
    .org 0xbe34e-ORIGIN
L_000be34e:
    bt/s L_000be354
    .org 0xbe350-ORIGIN
L_000be350:
    mov r0,r5
    .org 0xbe352-ORIGIN
L_000be352:
    mov.l L_000be488,r4
    .org 0xbe354-ORIGIN
L_000be354:
    mov.l L_000be48c,r2
    .org 0xbe356-ORIGIN
L_000be356:
    mov r13,r0
    .org 0xbe358-ORIGIN
L_000be358:
    tst r5,r5
    .org 0xbe35a-ORIGIN
L_000be35a:
    add #0x16,r2
    .org 0xbe35c-ORIGIN
L_000be35c:
    mov.b @(r0,r2),r6
    .org 0xbe35e-ORIGIN
L_000be35e:
    extu.b r6,r11
    .org 0xbe360-ORIGIN
L_000be360:
    bt/s L_000be37e
    .org 0xbe362-ORIGIN
L_000be362:
    add #-0x80,r11
    .org 0xbe364-ORIGIN
L_000be364:
    tst r13,r13
    .org 0xbe366-ORIGIN
L_000be366:
    bt L_000be36a
    .org 0xbe368-ORIGIN
L_000be368:
    mov.l L_000be490,r4
    .org 0xbe36a-ORIGIN
L_000be36a:
    mov.l L_000be494,r7
    .org 0xbe36c-ORIGIN
L_000be36c:
    mov #-0x8,r0
    .org 0xbe36e-ORIGIN
L_000be36e:
    extu.b r0,r0
    .org 0xbe370-ORIGIN
L_000be370:
    mov.l L_000be498,r5
    .org 0xbe372-ORIGIN
L_000be372:
    mov.l L_000be49c,r6
    .org 0xbe374-ORIGIN
L_000be374:
    bra L_000be38e
    .org 0xbe376-ORIGIN
L_000be376:
    mov.b @(r0,r7),r0
    .org 0xbe37e-ORIGIN
L_000be37e:
    tst r13,r13
    .org 0xbe380-ORIGIN
L_000be380:
    bt L_000be384
    .org 0xbe382-ORIGIN
L_000be382:
    mov.l L_000be4a0,r4
    .org 0xbe384-ORIGIN
L_000be384:
    mov.l L_000be49c,r6
    .org 0xbe386-ORIGIN
L_000be386:
    mov.l L_000be4a4,r7
    .org 0xbe388-ORIGIN
L_000be388:
    add #0x8,r6
    .org 0xbe38a-ORIGIN
L_000be38a:
    mov.l L_000be498,r5
    .org 0xbe38c-ORIGIN
L_000be38c:
    mov.b @(0x7,r7),r0
    .org 0xbe38e-ORIGIN
L_000be38e:
    mov.l L_000be4a8,r7
    .org 0xbe390-ORIGIN
L_000be390:
    mov.b r0,@(0x3,r15)
    .org 0xbe392-ORIGIN
L_000be392:
    mov #0x12,r0
    .org 0xbe394-ORIGIN
L_000be394:
    mov.b @(r0,r7),r14
    .org 0xbe396-ORIGIN
L_000be396:
    mov.l L_000be4ac,r2
    .org 0xbe398-ORIGIN
L_000be398:
    mov.l L_000be47c,r12
    .org 0xbe39a-ORIGIN
L_000be39a:
    jsr @r2
    .org 0xbe39c-ORIGIN
L_000be39c:
    extu.b r14,r7
    .org 0xbe39e-ORIGIN
L_000be39e:
    mov.w L_000be460,r5
    .org 0xbe3a0-ORIGIN
L_000be3a0:
    mov r12,r2
    .org 0xbe3a2-ORIGIN
L_000be3a2:
    mov r0,r6
    .org 0xbe3a4-ORIGIN
L_000be3a4:
    mov r13,r0
    .org 0xbe3a6-ORIGIN
L_000be3a6:
    add r5,r2
    .org 0xbe3a8-ORIGIN
L_000be3a8:
    mov.l L_000be4b0,r9
    .org 0xbe3aa-ORIGIN
L_000be3aa:
    mov.b r6,@(r0,r2)
    .org 0xbe3ac-ORIGIN
L_000be3ac:
    mov r12,r2
    .org 0xbe3ae-ORIGIN
L_000be3ae:
    add r5,r2
    .org 0xbe3b0-ORIGIN
L_000be3b0:
    mov r13,r0
    .org 0xbe3b2-ORIGIN
L_000be3b2:
    mov.b @(r0,r2),r6
    .org 0xbe3b4-ORIGIN
L_000be3b4:
    mov #0x64,r0
    .org 0xbe3b6-ORIGIN
L_000be3b6:
    extu.b r6,r6
    .org 0xbe3b8-ORIGIN
L_000be3b8:
    mul.l r6,r11
    .org 0xbe3ba-ORIGIN
L_000be3ba:
    sts macl,r1
    .org 0xbe3bc-ORIGIN
L_000be3bc:
    jsr @r9
    .org 0xbe3be-ORIGIN
L_000be3be:
    shll8 r1
    .org 0xbe3c0-ORIGIN
L_000be3c0:
    mov.l L_000be4b4,r6
    .org 0xbe3c2-ORIGIN
L_000be3c2:
    add r6,r0
    .org 0xbe3c4-ORIGIN
L_000be3c4:
    cmp/pz r0
    .org 0xbe3c6-ORIGIN
L_000be3c6:
    bt/s L_000be3cc
    .org 0xbe3c8-ORIGIN
L_000be3c8:
    mov r0,r6
    .org 0xbe3ca-ORIGIN
L_000be3ca:
    mov #0x0,r6
    .org 0xbe3cc-ORIGIN
L_000be3cc:
    mov #-0x1,r2
    .org 0xbe3ce-ORIGIN
L_000be3ce:
    extu.w r2,r2
    .org 0xbe3d0-ORIGIN
L_000be3d0:
    cmp/gt r2,r6
    .org 0xbe3d2-ORIGIN
L_000be3d2:
    bf L_000be3d6
    .org 0xbe3d4-ORIGIN
L_000be3d4:
    mov r2,r6
    .org 0xbe3d6-ORIGIN
L_000be3d6:
    mov.w L_000be462,r5
    .org 0xbe3d8-ORIGIN
L_000be3d8:
    mov r13,r10
    .org 0xbe3da-ORIGIN
L_000be3da:
    shll r10
    .org 0xbe3dc-ORIGIN
L_000be3dc:
    mov r12,r2
    .org 0xbe3de-ORIGIN
L_000be3de:
    add r5,r2
    .org 0xbe3e0-ORIGIN
L_000be3e0:
    mov r10,r0
    .org 0xbe3e2-ORIGIN
L_000be3e2:
    mov.w r6,@(r0,r2)
    .org 0xbe3e4-ORIGIN
L_000be3e4:
    mov r13,r0
    .org 0xbe3e6-ORIGIN
L_000be3e6:
    mov.l L_000be4b8,r2
    .org 0xbe3e8-ORIGIN
L_000be3e8:
    tst r13,r13
    .org 0xbe3ea-ORIGIN
L_000be3ea:
    mov.l L_000be4bc,r4
    .org 0xbe3ec-ORIGIN
L_000be3ec:
    add #0x16,r2
    .org 0xbe3ee-ORIGIN
L_000be3ee:
    mov.b @(r0,r2),r6
    .org 0xbe3f0-ORIGIN
L_000be3f0:
    extu.b r6,r14
    .org 0xbe3f2-ORIGIN
L_000be3f2:
    bt/s L_000be3f8
    .org 0xbe3f4-ORIGIN
L_000be3f4:
    add #-0x80,r14
    .org 0xbe3f6-ORIGIN
L_000be3f6:
    mov.l L_000be4c0,r4
    .org 0xbe3f8-ORIGIN
L_000be3f8:
    mov.l L_000be4a8,r3
    .org 0xbe3fa-ORIGIN
L_000be3fa:
    mov #0x12,r0
    .org 0xbe3fc-ORIGIN
L_000be3fc:
    mov.l L_000be4c4,r5
    .org 0xbe3fe-ORIGIN
L_000be3fe:
    mov.b @(r0,r3),r7
    .org 0xbe400-ORIGIN
L_000be400:
    mov.l L_000be4c8,r2
    .org 0xbe402-ORIGIN
L_000be402:
    jsr @r2
    .org 0xbe404-ORIGIN
L_000be404:
    extu.b r7,r6
    .org 0xbe406-ORIGIN
L_000be406:
    mov.w L_000be464,r5
    .org 0xbe408-ORIGIN
L_000be408:
    mov r12,r2
    .org 0xbe40a-ORIGIN
L_000be40a:
    mov r0,r6
    .org 0xbe40c-ORIGIN
L_000be40c:
    mov r13,r0
    .org 0xbe40e-ORIGIN
L_000be40e:
    add r5,r2
    .org 0xbe410-ORIGIN
L_000be410:
    mov.b r6,@(r0,r2)
    .org 0xbe412-ORIGIN
L_000be412:
    extu.b r6,r6
    .org 0xbe414-ORIGIN
L_000be414:
    mov r11,r2
    .org 0xbe416-ORIGIN
L_000be416:
    sub r14,r2
    .org 0xbe418-ORIGIN
L_000be418:
    mul.l r6,r2
    .org 0xbe41a-ORIGIN
L_000be41a:
    mov #0x64,r6
    .org 0xbe41c-ORIGIN
L_000be41c:
    mov r6,r0
    .org 0xbe41e-ORIGIN
L_000be41e:
    jsr @r9
    .org 0xbe420-ORIGIN
L_000be420:
    sts macl,r1
    .org 0xbe422-ORIGIN
L_000be422:
    mov #-0x80,r6
    .org 0xbe424-ORIGIN
L_000be424:
    extu.b r6,r6
    .org 0xbe426-ORIGIN
L_000be426:
    add r6,r0
    .org 0xbe428-ORIGIN
L_000be428:
    cmp/pz r0
    .org 0xbe42a-ORIGIN
L_000be42a:
    bt/s L_000be430
    .org 0xbe42c-ORIGIN
L_000be42c:
    mov r0,r4
    .org 0xbe42e-ORIGIN
L_000be42e:
    mov #0x0,r4
    .org 0xbe430-ORIGIN
L_000be430:
    mov #-0x1,r2
    .org 0xbe432-ORIGIN
L_000be432:
    extu.b r2,r2
    .org 0xbe434-ORIGIN
L_000be434:
    cmp/gt r2,r4
    .org 0xbe436-ORIGIN
L_000be436:
    bf L_000be43a
    .org 0xbe438-ORIGIN
L_000be438:
    mov r2,r4
    .org 0xbe43a-ORIGIN
L_000be43a:
    mov.w L_000be466,r6
    .org 0xbe43c-ORIGIN
L_000be43c:
    mov r12,r2
    .org 0xbe43e-ORIGIN
L_000be43e:
    mov r4,r0
    .org 0xbe440-ORIGIN
L_000be440:
    mov.b r0,@(0x4,r15)
    .org 0xbe442-ORIGIN
L_000be442:
    add r6,r2
    .org 0xbe444-ORIGIN
L_000be444:
    mov.l L_000be4cc,r6
    .org 0xbe446-ORIGIN
L_000be446:
    mov r13,r0
    .org 0xbe448-ORIGIN
L_000be448:
    mov.b r4,@(r0,r2)
    .org 0xbe44a-ORIGIN
L_000be44a:
    mov #0x37,r0
    .org 0xbe44c-ORIGIN
L_000be44c:
    mov.b @(r0,r6),r0
    .org 0xbe44e-ORIGIN
L_000be44e:
    tst #0x1,r0
    .org 0xbe450-ORIGIN
L_000be450:
    bf L_000be51c
    .org 0xbe452-ORIGIN
L_000be452:
    mov.l L_000be4d0,r4
    .org 0xbe454-ORIGIN
L_000be454:
    mov.b @(0x3,r4),r0
    .org 0xbe456-ORIGIN
L_000be456:
    extu.b r0,r6
    .org 0xbe458-ORIGIN
L_000be458:
    cmp/gt r6,r11
    .org 0xbe45a-ORIGIN
L_000be45a:
    bt L_000be4da
    .org 0xbe45c-ORIGIN
L_000be45c:
    bra L_000be4d4
    .org 0xbe45e-ORIGIN
L_000be45e:
    nop
    .org 0xbe460-ORIGIN
L_000be460:
    .word 0x0368
    .org 0xbe462-ORIGIN
L_000be462:
    .word 0x0860
    .org 0xbe464-ORIGIN
L_000be464:
    .word 0x0348
    .org 0xbe466-ORIGIN
L_000be466:
    .word 0x07f8
    .org 0xbe47c-ORIGIN
L_000be47c:
    .long 0xffff128c
    .org 0xbe480-ORIGIN
L_000be480:
    .long 0x00008616
    .org 0xbe484-ORIGIN
L_000be484:
    .long 0x0000a01a
    .org 0xbe488-ORIGIN
L_000be488:
    .long 0x0000a09a
    .org 0xbe48c-ORIGIN
L_000be48c:
    .long 0xffff120e
    .org 0xbe490-ORIGIN
L_000be490:
    .long 0x0000a0da
    .org 0xbe494-ORIGIN
L_000be494:
    .long 0xffff267a
    .org 0xbe498-ORIGIN
L_000be498:
    .long 0x00013026
    .org 0xbe49c-ORIGIN
L_000be49c:
    .long 0x00013046
    .org 0xbe4a0-ORIGIN
L_000be4a0:
    .long 0x0000a05a
    .org 0xbe4a4-ORIGIN
L_000be4a4:
    .long 0xffff106a
    .org 0xbe4a8-ORIGIN
L_000be4a8:
    .long 0xffff119c
    .org 0xbe4ac-ORIGIN
L_000be4ac:
    .long 0x00026140
    .org 0xbe4b0-ORIGIN
L_000be4b0:
    .long 0x00021bbc
    .org 0xbe4b4-ORIGIN
L_000be4b4:
    .long 0x00008000
    .org 0xbe4b8-ORIGIN
L_000be4b8:
    .long 0xffff124c
    .org 0xbe4bc-ORIGIN
L_000be4bc:
    .long 0x000123ea
    .org 0xbe4c0-ORIGIN
L_000be4c0:
    .long 0x00012412
    .org 0xbe4c4-ORIGIN
L_000be4c4:
    .long 0x00011be3
    .org 0xbe4c8-ORIGIN
L_000be4c8:
    .long 0x00026474
    .org 0xbe4cc-ORIGIN
L_000be4cc:
    .long 0xffff2470
    .org 0xbe4d0-ORIGIN
L_000be4d0:
    .long 0x00008d64
    .org 0xbe4d4-ORIGIN
L_000be4d4:
    neg r6,r2
    .org 0xbe4d6-ORIGIN
L_000be4d6:
    cmp/ge r2,r11
    .org 0xbe4d8-ORIGIN
L_000be4d8:
    bt L_000be51c
    .org 0xbe4da-ORIGIN
L_000be4da:
    mov.l L_000be73c,r6
    .org 0xbe4dc-ORIGIN
L_000be4dc:
    tst r13,r13
    .org 0xbe4de-ORIGIN
L_000be4de:
    mov.b @r6,r2
    .org 0xbe4e0-ORIGIN
L_000be4e0:
    bt/s L_000be4ea
    .org 0xbe4e2-ORIGIN
L_000be4e2:
    extu.b r2,r2
    .org 0xbe4e4-ORIGIN
L_000be4e4:
    mov.l L_000be740,r6
    .org 0xbe4e6-ORIGIN
L_000be4e6:
    mov.b @r6,r2
    .org 0xbe4e8-ORIGIN
L_000be4e8:
    extu.b r2,r2
    .org 0xbe4ea-ORIGIN
L_000be4ea:
    mul.l r2,r11
    .org 0xbe4ec-ORIGIN
L_000be4ec:
    mov #0x64,r6
    .org 0xbe4ee-ORIGIN
L_000be4ee:
    mov r6,r0
    .org 0xbe4f0-ORIGIN
L_000be4f0:
    sts macl,r1
    .org 0xbe4f2-ORIGIN
L_000be4f2:
    shll8 r1
    .org 0xbe4f4-ORIGIN
L_000be4f4:
    jsr @r9
    .org 0xbe4f6-ORIGIN
L_000be4f6:
    shll r1
    .org 0xbe4f8-ORIGIN
L_000be4f8:
    mov.w L_000be60c,r7
    .org 0xbe4fa-ORIGIN
L_000be4fa:
    mov r12,r2
    .org 0xbe4fc-ORIGIN
L_000be4fc:
    mov r0,r5
    .org 0xbe4fe-ORIGIN
L_000be4fe:
    mov r8,r0
    .org 0xbe500-ORIGIN
L_000be500:
    add r7,r2
    .org 0xbe502-ORIGIN
L_000be502:
    mov.l @(r0,r2),r6
    .org 0xbe504-ORIGIN
L_000be504:
    add r6,r5
    .org 0xbe506-ORIGIN
L_000be506:
    cmp/pz r5
    .org 0xbe508-ORIGIN
L_000be508:
    bt L_000be50c
    .org 0xbe50a-ORIGIN
L_000be50a:
    mov #0x0,r5
    .org 0xbe50c-ORIGIN
L_000be50c:
    mov.l L_000be744,r2
    .org 0xbe50e-ORIGIN
L_000be50e:
    cmp/gt r2,r5
    .org 0xbe510-ORIGIN
L_000be510:
    bf L_000be514
    .org 0xbe512-ORIGIN
L_000be512:
    mov r2,r5
    .org 0xbe514-ORIGIN
L_000be514:
    mov r12,r2
    .org 0xbe516-ORIGIN
L_000be516:
    add r7,r2
    .org 0xbe518-ORIGIN
L_000be518:
    mov r8,r0
    .org 0xbe51a-ORIGIN
L_000be51a:
    mov.l r5,@(r0,r2)
    .org 0xbe51c-ORIGIN
L_000be51c:
    mov.l L_000be748,r4
    .org 0xbe51e-ORIGIN
L_000be51e:
    mov #-0x80,r7
    .org 0xbe520-ORIGIN
L_000be520:
    extu.b r7,r7
    .org 0xbe522-ORIGIN
L_000be522:
    mov.b @(0x6,r4),r0
    .org 0xbe524-ORIGIN
L_000be524:
    shll16 r7
    .org 0xbe526-ORIGIN
L_000be526:
    extu.b r0,r6
    .org 0xbe528-ORIGIN
L_000be528:
    cmp/gt r6,r11
    .org 0xbe52a-ORIGIN
L_000be52a:
    bt/s L_000be534
    .org 0xbe52c-ORIGIN
L_000be52c:
    mov r7,r5
    .org 0xbe52e-ORIGIN
L_000be52e:
    neg r6,r2
    .org 0xbe530-ORIGIN
L_000be530:
    cmp/ge r2,r11
    .org 0xbe532-ORIGIN
L_000be532:
    bt L_000be54a
    .org 0xbe534-ORIGIN
L_000be534:
    mov.w L_000be60e,r6
    .org 0xbe536-ORIGIN
L_000be536:
    mov r12,r2
    .org 0xbe538-ORIGIN
L_000be538:
    mov r10,r0
    .org 0xbe53a-ORIGIN
L_000be53a:
    add r6,r2
    .org 0xbe53c-ORIGIN
L_000be53c:
    mov.w @(r0,r2),r6
    .org 0xbe53e-ORIGIN
L_000be53e:
    extu.w r6,r5
    .org 0xbe540-ORIGIN
L_000be540:
    mov #-0x80,r6
    .org 0xbe542-ORIGIN
L_000be542:
    shll8 r6
    .org 0xbe544-ORIGIN
L_000be544:
    add r6,r5
    .org 0xbe546-ORIGIN
L_000be546:
    shll8 r5
    .org 0xbe548-ORIGIN
L_000be548:
    add r7,r5
    .org 0xbe54a-ORIGIN
L_000be54a:
    mov.w L_000be60c,r7
    .org 0xbe54c-ORIGIN
L_000be54c:
    mov r12,r2
    .org 0xbe54e-ORIGIN
L_000be54e:
    mov r8,r0
    .org 0xbe550-ORIGIN
L_000be550:
    add r7,r2
    .org 0xbe552-ORIGIN
L_000be552:
    mov.l @(r0,r2),r6
    .org 0xbe554-ORIGIN
L_000be554:
    mov #-0x80,r2
    .org 0xbe556-ORIGIN
L_000be556:
    extu.b r2,r2
    .org 0xbe558-ORIGIN
L_000be558:
    shll16 r2
    .org 0xbe55a-ORIGIN
L_000be55a:
    sub r2,r6
    .org 0xbe55c-ORIGIN
L_000be55c:
    add r6,r5
    .org 0xbe55e-ORIGIN
L_000be55e:
    mov.b @r4,r6
    .org 0xbe560-ORIGIN
L_000be560:
    extu.b r6,r6
    .org 0xbe562-ORIGIN
L_000be562:
    cmp/gt r6,r11
    .org 0xbe564-ORIGIN
L_000be564:
    bt L_000be56c
    .org 0xbe566-ORIGIN
L_000be566:
    neg r6,r2
    .org 0xbe568-ORIGIN
L_000be568:
    cmp/ge r2,r11
    .org 0xbe56a-ORIGIN
L_000be56a:
    bt L_000be576
    .org 0xbe56c-ORIGIN
L_000be56c:
    mov.b @(0x4,r15),r0
    .org 0xbe56e-ORIGIN
L_000be56e:
    extu.b r0,r4
    .org 0xbe570-ORIGIN
L_000be570:
    add #-0x80,r4
    .org 0xbe572-ORIGIN
L_000be572:
    shll16 r4
    .org 0xbe574-ORIGIN
L_000be574:
    add r4,r5
    .org 0xbe576-ORIGIN
L_000be576:
    mov.l L_000be74c,r2
    .org 0xbe578-ORIGIN
L_000be578:
    mov.b @r2,r0
    .org 0xbe57a-ORIGIN
L_000be57a:
    tst #0x40,r0
    .org 0xbe57c-ORIGIN
L_000be57c:
    bf L_000be590
    .org 0xbe57e-ORIGIN
L_000be57e:
    mov.w L_000be610,r6
    .org 0xbe580-ORIGIN
L_000be580:
    mov r12,r2
    .org 0xbe582-ORIGIN
L_000be582:
    mov r13,r0
    .org 0xbe584-ORIGIN
L_000be584:
    add r6,r2
    .org 0xbe586-ORIGIN
L_000be586:
    mov.b @(r0,r2),r6
    .org 0xbe588-ORIGIN
L_000be588:
    extu.b r6,r2
    .org 0xbe58a-ORIGIN
L_000be58a:
    add #-0x80,r2
    .org 0xbe58c-ORIGIN
L_000be58c:
    shll16 r2
    .org 0xbe58e-ORIGIN
L_000be58e:
    add r2,r5
    .org 0xbe590-ORIGIN
L_000be590:
    cmp/pz r5
    .org 0xbe592-ORIGIN
L_000be592:
    bt L_000be596
    .org 0xbe594-ORIGIN
L_000be594:
    mov #0x0,r5
    .org 0xbe596-ORIGIN
L_000be596:
    mov.l L_000be744,r2
    .org 0xbe598-ORIGIN
L_000be598:
    cmp/gt r2,r5
    .org 0xbe59a-ORIGIN
L_000be59a:
    bf L_000be59e
    .org 0xbe59c-ORIGIN
L_000be59c:
    mov r2,r5
    .org 0xbe59e-ORIGIN
L_000be59e:
    mov.w L_000be612,r2
    .org 0xbe5a0-ORIGIN
L_000be5a0:
    mov r8,r0
    .org 0xbe5a2-ORIGIN
L_000be5a2:
    add r2,r12
    .org 0xbe5a4-ORIGIN
L_000be5a4:
    mov.l r5,@(r0,r12)
    .org 0xbe5a6-ORIGIN
L_000be5a6:
    add #0x8,r15
    .org 0xbe5a8-ORIGIN
L_000be5a8:
    lds.l @r15+,macl
    .org 0xbe5aa-ORIGIN
L_000be5aa:
    lds.l @r15+,pr
    .org 0xbe5ac-ORIGIN
L_000be5ac:
    mov.l @r15+,r14
    .org 0xbe5ae-ORIGIN
L_000be5ae:
    mov.l @r15+,r13
    .org 0xbe5b0-ORIGIN
L_000be5b0:
    mov.l @r15+,r12
    .org 0xbe5b2-ORIGIN
L_000be5b2:
    mov.l @r15+,r11
    .org 0xbe5b4-ORIGIN
L_000be5b4:
    mov.l @r15+,r10
    .org 0xbe5b6-ORIGIN
L_000be5b6:
    mov.l @r15+,r9
    .org 0xbe5b8-ORIGIN
L_000be5b8:
    rts
    .org 0xbe5ba-ORIGIN
L_000be5ba:
    mov.l @r15+,r8
    .org 0xbe60c-ORIGIN
L_000be60c:
    .word 0x0830
    .org 0xbe60e-ORIGIN
L_000be60e:
    .word 0x0860
    .org 0xbe610-ORIGIN
L_000be610:
    .word 0x07f2
    .org 0xbe612-ORIGIN
L_000be612:
    .word 0x0870
    .org 0xbe73c-ORIGIN
L_000be73c:
    .long 0x000087af
    .org 0xbe740-ORIGIN
L_000be740:
    .long 0x000087b4
    .org 0xbe744-ORIGIN
L_000be744:
    .long 0x00ffffff
    .org 0xbe748-ORIGIN
L_000be748:
    .long 0x00008d64
    .org 0xbe74c-ORIGIN
L_000be74c:
    .long 0x00008615
