! Complete natural threshold-window caller and exact real signed divider.
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
    .org 0x847dc-ORIGIN
L_000847dc:
    mov.l r12,@-r15
    .org 0x847de-ORIGIN
L_000847de:
    mov.l r13,@-r15
    .org 0x847e0-ORIGIN
L_000847e0:
    sts.l pr,@-r15
    .org 0x847e2-ORIGIN
L_000847e2:
    stc.l gbr,@-r15
    .org 0x847e4-ORIGIN
L_000847e4:
    mov.l P_000849e0,r0
    .org 0x847e6-ORIGIN
L_000847e6:
    ldc r0,gbr
    .org 0x847e8-ORIGIN
L_000847e8:
    add #-0xc,r15
    .org 0x847ea-ORIGIN
L_000847ea:
    mov r6,r12
    .org 0x847ec-ORIGIN
L_000847ec:
    mov.l P_000849e4,r6
    .org 0x847ee-ORIGIN
L_000847ee:
    mov r5,r0
    .org 0x847f0-ORIGIN
L_000847f0:
    mov.b r0,@(0x3,r15)
    .org 0x847f2-ORIGIN
L_000847f2:
    mov.b @(0x5,r6),r0
    .org 0x847f4-ORIGIN
L_000847f4:
    tst #0x80,r0
    .org 0x847f6-ORIGIN
L_000847f6:
    bt L_00084890
    .org 0x847f8-ORIGIN
L_000847f8:
    mov.b @(0xae,gbr),r0
    .org 0x847fa-ORIGIN
L_000847fa:
    tst #0x2,r0
    .org 0x847fc-ORIGIN
L_000847fc:
    bt/s L_00084890
    .org 0x847fe-ORIGIN
L_000847fe:
    mov r0,r2
    .org 0x84800-ORIGIN
L_00084800:
    mov r2,r0
    .org 0x84802-ORIGIN
L_00084802:
    tst #0x1,r0
    .org 0x84804-ORIGIN
L_00084804:
    bt L_00084890
    .org 0x84806-ORIGIN
L_00084806:
    mov.l P_000849e8,r2
    .org 0x84808-ORIGIN
L_00084808:
    mov #0x20,r0
    .org 0x8480a-ORIGIN
L_0008480a:
    extu.w r4,r13
    .org 0x8480c-ORIGIN
L_0008480c:
    mov.w @(r0,r2),r5
    .org 0x8480e-ORIGIN
L_0008480e:
    mov r13,r2
    .org 0x84810-ORIGIN
L_00084810:
    add #-0x1e,r2
    .org 0x84812-ORIGIN
L_00084812:
    cmp/pz r2
    .org 0x84814-ORIGIN
L_00084814:
    bt/s L_0008481a
    .org 0x84816-ORIGIN
L_00084816:
    extu.w r5,r5
    .org 0x84818-ORIGIN
L_00084818:
    mov #0x0,r2
    .org 0x8481a-ORIGIN
L_0008481a:
    cmp/ge r2,r5
    .org 0x8481c-ORIGIN
L_0008481c:
    bf L_00084890
    .org 0x8481e-ORIGIN
L_0008481e:
    mov #-0x1,r6
    .org 0x84820-ORIGIN
L_00084820:
    add #0x1e,r13
    .org 0x84822-ORIGIN
L_00084822:
    extu.b r6,r6
    .org 0x84824-ORIGIN
L_00084824:
    cmp/gt r6,r13
    .org 0x84826-ORIGIN
L_00084826:
    bf/s L_0008482c
    .org 0x84828-ORIGIN
L_00084828:
    mov r13,r2
    .org 0x8482a-ORIGIN
L_0008482a:
    mov r6,r2
    .org 0x8482c-ORIGIN
L_0008482c:
    cmp/ge r2,r5
    .org 0x8482e-ORIGIN
L_0008482e:
    bt L_00084890
    .org 0x84830-ORIGIN
L_00084830:
    mov.b @(0x1a,gbr),r0
    .org 0x84832-ORIGIN
L_00084832:
    mov.l P_000849ec,r6
    .org 0x84834-ORIGIN
L_00084834:
    extu.b r0,r2
    .org 0x84836-ORIGIN
L_00084836:
    mov.b @(0x3,r15),r0
    .org 0x84838-ORIGIN
L_00084838:
    mov.l r2,@(0x8,r15)
    .org 0x8483a-ORIGIN
L_0008483a:
    extu.b r0,r1
    .org 0x8483c-ORIGIN
L_0008483c:
    shll2 r1
    .org 0x8483e-ORIGIN
L_0008483e:
    shll r1
    .org 0x84840-ORIGIN
L_00084840:
    jsr @r6
    .org 0x84842-ORIGIN
L_00084842:
    mov #0xa,r0
    .org 0x84844-ORIGIN
L_00084844:
    mov.l @(0x8,r15),r6
    .org 0x84846-ORIGIN
L_00084846:
    cmp/ge r0,r6
    .org 0x84848-ORIGIN
L_00084848:
    bf L_00084890
    .org 0x8484a-ORIGIN
L_0008484a:
    mov.b @(0x1a,gbr),r0
    .org 0x8484c-ORIGIN
L_0008484c:
    mov.l P_000849ec,r6
    .org 0x8484e-ORIGIN
L_0008484e:
    extu.b r0,r2
    .org 0x84850-ORIGIN
L_00084850:
    mov.b @(0x3,r15),r0
    .org 0x84852-ORIGIN
L_00084852:
    mov.l r2,@(0x4,r15)
    .org 0x84854-ORIGIN
L_00084854:
    extu.b r0,r4
    .org 0x84856-ORIGIN
L_00084856:
    mov r4,r1
    .org 0x84858-ORIGIN
L_00084858:
    shll r1
    .org 0x8485a-ORIGIN
L_0008485a:
    add r4,r1
    .org 0x8485c-ORIGIN
L_0008485c:
    shll2 r1
    .org 0x8485e-ORIGIN
L_0008485e:
    jsr @r6
    .org 0x84860-ORIGIN
L_00084860:
    mov #0xa,r0
    .org 0x84862-ORIGIN
L_00084862:
    mov.l @(0x4,r15),r6
    .org 0x84864-ORIGIN
L_00084864:
    cmp/ge r0,r6
    .org 0x84866-ORIGIN
L_00084866:
    bt L_00084890
    .org 0x84868-ORIGIN
L_00084868:
    extu.b r12,r12
    .org 0x8486a-ORIGIN
L_0008486a:
    mov #0x6e,r6
    .org 0x8486c-ORIGIN
L_0008486c:
    cmp/ge r6,r12
    .org 0x8486e-ORIGIN
L_0008486e:
    bf L_0008487c
    .org 0x84870-ORIGIN
L_00084870:
    mov.l P_000849f0,r5
    .org 0x84872-ORIGIN
L_00084872:
    mov.w P_0008489e,r0
    .org 0x84874-ORIGIN
L_00084874:
    mov.b @(r0,r5),r2
    .org 0x84876-ORIGIN
L_00084876:
    extu.b r2,r2
    .org 0x84878-ORIGIN
L_00084878:
    cmp/ge r6,r2
    .org 0x8487a-ORIGIN
L_0008487a:
    bt L_0008488c
    .org 0x8487c-ORIGIN
L_0008487c:
    cmp/ge r6,r12
    .org 0x8487e-ORIGIN
L_0008487e:
    bt L_00084890
    .org 0x84880-ORIGIN
L_00084880:
    mov.l P_000849f0,r5
    .org 0x84882-ORIGIN
L_00084882:
    mov.w P_0008489e,r0
    .org 0x84884-ORIGIN
L_00084884:
    mov.b @(r0,r5),r2
    .org 0x84886-ORIGIN
L_00084886:
    extu.b r2,r5
    .org 0x84888-ORIGIN
L_00084888:
    cmp/ge r6,r5
    .org 0x8488a-ORIGIN
L_0008488a:
    bt L_00084890
    .org 0x8488c-ORIGIN
L_0008488c:
    bra L_00084892
    .org 0x8488e-ORIGIN
L_0008488e:
    mov #0x1,r0
    .org 0x84890-ORIGIN
L_00084890:
    mov #0x0,r0
    .org 0x84892-ORIGIN
L_00084892:
    add #0xc,r15
    .org 0x84894-ORIGIN
L_00084894:
    ldc.l @r15+,gbr
    .org 0x84896-ORIGIN
L_00084896:
    lds.l @r15+,pr
    .org 0x84898-ORIGIN
L_00084898:
    mov.l @r15+,r13
    .org 0x8489a-ORIGIN
L_0008489a:
    rts
    .org 0x8489c-ORIGIN
L_0008489c:
    mov.l @r15+,r12
    .org 0x8489e-ORIGIN
P_0008489e:
    .byte 0x05
    .org 0x8489f-ORIGIN
P_0008489f:
    .byte 0xe0
    .org 0x849e0-ORIGIN
P_000849e0:
    .byte 0xff
    .org 0x849e1-ORIGIN
P_000849e1:
    .byte 0xff
    .org 0x849e2-ORIGIN
P_000849e2:
    .byte 0x41
    .org 0x849e3-ORIGIN
P_000849e3:
    .byte 0x24
    .org 0x849e4-ORIGIN
P_000849e4:
    .byte 0xff
    .org 0x849e5-ORIGIN
P_000849e5:
    .byte 0xff
    .org 0x849e6-ORIGIN
P_000849e6:
    .byte 0x42
    .org 0x849e7-ORIGIN
P_000849e7:
    .byte 0x4c
    .org 0x849e8-ORIGIN
P_000849e8:
    .byte 0xff
    .org 0x849e9-ORIGIN
P_000849e9:
    .byte 0xff
    .org 0x849ea-ORIGIN
P_000849ea:
    .byte 0x11
    .org 0x849eb-ORIGIN
P_000849eb:
    .byte 0x9c
    .org 0x849ec-ORIGIN
P_000849ec:
    .byte 0x00
    .org 0x849ed-ORIGIN
P_000849ed:
    .byte 0x02
    .org 0x849ee-ORIGIN
P_000849ee:
    .byte 0x1b
    .org 0x849ef-ORIGIN
P_000849ef:
    .byte 0xbc
    .org 0x849f0-ORIGIN
P_000849f0:
    .byte 0xff
    .org 0x849f1-ORIGIN
P_000849f1:
    .byte 0xff
    .org 0x849f2-ORIGIN
P_000849f2:
    .byte 0x39
    .org 0x849f3-ORIGIN
P_000849f3:
    .byte 0xc4
