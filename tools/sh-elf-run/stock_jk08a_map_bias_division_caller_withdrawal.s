! Complete natural702C6 caller and all eight exact real helpers.
    .text
    .balign 4
    .set ORIGIN,0x21ce0
    .org 0x21ce0-ORIGIN
L_00021ce0:
    mov.l r2,@-r15
    .org 0x21ce2-ORIGIN
L_00021ce2:
    tst r0,r0
    .org 0x21ce4-ORIGIN
L_00021ce4:
    bt L_00021d6a
    .org 0x21ce6-ORIGIN
L_00021ce6:
    extu.w r0,r2
    .org 0x21ce8-ORIGIN
L_00021ce8:
    cmp/eq r2,r0
    .org 0x21cea-ORIGIN
L_00021cea:
    bf L_00021d76
    .org 0x21cec-ORIGIN
L_00021cec:
    div0u
    .org 0x21cee-ORIGIN
L_00021cee:
    shll8 r0
    .org 0x21cf0-ORIGIN
L_00021cf0:
    cmp/hi r1,r0
    .org 0x21cf2-ORIGIN
L_00021cf2:
    bf L_00021d0c
    .org 0x21cf4-ORIGIN
L_00021cf4:
    div1 r0,r1
    .org 0x21cf6-ORIGIN
L_00021cf6:
    div1 r0,r1
    .org 0x21cf8-ORIGIN
L_00021cf8:
    div1 r0,r1
    .org 0x21cfa-ORIGIN
L_00021cfa:
    div1 r0,r1
    .org 0x21cfc-ORIGIN
L_00021cfc:
    div1 r0,r1
    .org 0x21cfe-ORIGIN
L_00021cfe:
    div1 r0,r1
    .org 0x21d00-ORIGIN
L_00021d00:
    div1 r0,r1
    .org 0x21d02-ORIGIN
L_00021d02:
    div1 r0,r1
    .org 0x21d04-ORIGIN
L_00021d04:
    rotcl r1
    .org 0x21d06-ORIGIN
L_00021d06:
    mov.l @r15+,r2
    .org 0x21d08-ORIGIN
L_00021d08:
    rts
    .org 0x21d0a-ORIGIN
L_00021d0a:
    extu.b r1,r0
    .org 0x21d0c-ORIGIN
L_00021d0c:
    mov.l r3,@-r15
    .org 0x21d0e-ORIGIN
L_00021d0e:
    extu.w r1,r3
    .org 0x21d10-ORIGIN
L_00021d10:
    shll8 r0
    .org 0x21d12-ORIGIN
L_00021d12:
    shlr16 r1
    .org 0x21d14-ORIGIN
L_00021d14:
    div1 r0,r1
    .org 0x21d16-ORIGIN
L_00021d16:
    div1 r0,r1
    .org 0x21d18-ORIGIN
L_00021d18:
    div1 r0,r1
    .org 0x21d1a-ORIGIN
L_00021d1a:
    div1 r0,r1
    .org 0x21d1c-ORIGIN
L_00021d1c:
    div1 r0,r1
    .org 0x21d1e-ORIGIN
L_00021d1e:
    div1 r0,r1
    .org 0x21d20-ORIGIN
L_00021d20:
    div1 r0,r1
    .org 0x21d22-ORIGIN
L_00021d22:
    div1 r0,r1
    .org 0x21d24-ORIGIN
L_00021d24:
    div1 r0,r1
    .org 0x21d26-ORIGIN
L_00021d26:
    div1 r0,r1
    .org 0x21d28-ORIGIN
L_00021d28:
    div1 r0,r1
    .org 0x21d2a-ORIGIN
L_00021d2a:
    div1 r0,r1
    .org 0x21d2c-ORIGIN
L_00021d2c:
    div1 r0,r1
    .org 0x21d2e-ORIGIN
L_00021d2e:
    div1 r0,r1
    .org 0x21d30-ORIGIN
L_00021d30:
    div1 r0,r1
    .org 0x21d32-ORIGIN
L_00021d32:
    div1 r0,r1
    .org 0x21d34-ORIGIN
L_00021d34:
    extu.w r1,r2
    .org 0x21d36-ORIGIN
L_00021d36:
    xor r2,r1
    .org 0x21d38-ORIGIN
L_00021d38:
    addc r2,r2
    .org 0x21d3a-ORIGIN
L_00021d3a:
    shll16 r2
    .org 0x21d3c-ORIGIN
L_00021d3c:
    add r3,r1
    .org 0x21d3e-ORIGIN
L_00021d3e:
    div1 r0,r1
    .org 0x21d40-ORIGIN
L_00021d40:
    div1 r0,r1
    .org 0x21d42-ORIGIN
L_00021d42:
    div1 r0,r1
    .org 0x21d44-ORIGIN
L_00021d44:
    div1 r0,r1
    .org 0x21d46-ORIGIN
L_00021d46:
    div1 r0,r1
    .org 0x21d48-ORIGIN
L_00021d48:
    div1 r0,r1
    .org 0x21d4a-ORIGIN
L_00021d4a:
    div1 r0,r1
    .org 0x21d4c-ORIGIN
L_00021d4c:
    div1 r0,r1
    .org 0x21d4e-ORIGIN
L_00021d4e:
    div1 r0,r1
    .org 0x21d50-ORIGIN
L_00021d50:
    div1 r0,r1
    .org 0x21d52-ORIGIN
L_00021d52:
    div1 r0,r1
    .org 0x21d54-ORIGIN
L_00021d54:
    div1 r0,r1
    .org 0x21d56-ORIGIN
L_00021d56:
    div1 r0,r1
    .org 0x21d58-ORIGIN
L_00021d58:
    div1 r0,r1
    .org 0x21d5a-ORIGIN
L_00021d5a:
    div1 r0,r1
    .org 0x21d5c-ORIGIN
L_00021d5c:
    div1 r0,r1
    .org 0x21d5e-ORIGIN
L_00021d5e:
    rotcl r1
    .org 0x21d60-ORIGIN
L_00021d60:
    extu.w r1,r0
    .org 0x21d62-ORIGIN
L_00021d62:
    add r2,r0
    .org 0x21d64-ORIGIN
L_00021d64:
    mov.l @r15+,r3
    .org 0x21d66-ORIGIN
L_00021d66:
    rts
    .org 0x21d68-ORIGIN
L_00021d68:
    mov.l @r15+,r2
    .org 0x21d6a-ORIGIN
L_00021d6a:
    mov.l P_00021dc8,r1
    .org 0x21d6c-ORIGIN
L_00021d6c:
    mov.l P_00021dcc,r2
    .org 0x21d6e-ORIGIN
L_00021d6e:
    mov.l r2,@r1
    .org 0x21d70-ORIGIN
L_00021d70:
    mov #0x0,r0
    .org 0x21d72-ORIGIN
L_00021d72:
    rts
    .org 0x21d74-ORIGIN
L_00021d74:
    mov.l @r15+,r2
    .org 0x21d76-ORIGIN
L_00021d76:
    div0u
    .org 0x21d78-ORIGIN
L_00021d78:
    extu.w r1,r2
    .org 0x21d7a-ORIGIN
L_00021d7a:
    shll16 r2
    .org 0x21d7c-ORIGIN
L_00021d7c:
    shlr16 r1
    .org 0x21d7e-ORIGIN
L_00021d7e:
    rotcl r2
    .org 0x21d80-ORIGIN
L_00021d80:
    div1 r0,r1
    .org 0x21d82-ORIGIN
L_00021d82:
    rotcl r2
    .org 0x21d84-ORIGIN
L_00021d84:
    div1 r0,r1
    .org 0x21d86-ORIGIN
L_00021d86:
    rotcl r2
    .org 0x21d88-ORIGIN
L_00021d88:
    div1 r0,r1
    .org 0x21d8a-ORIGIN
L_00021d8a:
    rotcl r2
    .org 0x21d8c-ORIGIN
L_00021d8c:
    div1 r0,r1
    .org 0x21d8e-ORIGIN
L_00021d8e:
    rotcl r2
    .org 0x21d90-ORIGIN
L_00021d90:
    div1 r0,r1
    .org 0x21d92-ORIGIN
L_00021d92:
    rotcl r2
    .org 0x21d94-ORIGIN
L_00021d94:
    div1 r0,r1
    .org 0x21d96-ORIGIN
L_00021d96:
    rotcl r2
    .org 0x21d98-ORIGIN
L_00021d98:
    div1 r0,r1
    .org 0x21d9a-ORIGIN
L_00021d9a:
    rotcl r2
    .org 0x21d9c-ORIGIN
L_00021d9c:
    div1 r0,r1
    .org 0x21d9e-ORIGIN
L_00021d9e:
    rotcl r2
    .org 0x21da0-ORIGIN
L_00021da0:
    div1 r0,r1
    .org 0x21da2-ORIGIN
L_00021da2:
    rotcl r2
    .org 0x21da4-ORIGIN
L_00021da4:
    div1 r0,r1
    .org 0x21da6-ORIGIN
L_00021da6:
    rotcl r2
    .org 0x21da8-ORIGIN
L_00021da8:
    div1 r0,r1
    .org 0x21daa-ORIGIN
L_00021daa:
    rotcl r2
    .org 0x21dac-ORIGIN
L_00021dac:
    div1 r0,r1
    .org 0x21dae-ORIGIN
L_00021dae:
    rotcl r2
    .org 0x21db0-ORIGIN
L_00021db0:
    div1 r0,r1
    .org 0x21db2-ORIGIN
L_00021db2:
    rotcl r2
    .org 0x21db4-ORIGIN
L_00021db4:
    div1 r0,r1
    .org 0x21db6-ORIGIN
L_00021db6:
    rotcl r2
    .org 0x21db8-ORIGIN
L_00021db8:
    div1 r0,r1
    .org 0x21dba-ORIGIN
L_00021dba:
    rotcl r2
    .org 0x21dbc-ORIGIN
L_00021dbc:
    div1 r0,r1
    .org 0x21dbe-ORIGIN
L_00021dbe:
    rotcl r2
    .org 0x21dc0-ORIGIN
L_00021dc0:
    mov r2,r0
    .org 0x21dc2-ORIGIN
L_00021dc2:
    rts
    .org 0x21dc4-ORIGIN
L_00021dc4:
    mov.l @r15+,r2
    .org 0x21dc8-ORIGIN
P_00021dc8:
    .byte 0xff
    .org 0x21dc9-ORIGIN
P_00021dc9:
    .byte 0xff
    .org 0x21dca-ORIGIN
P_00021dca:
    .byte 0x98
    .org 0x21dcb-ORIGIN
P_00021dcb:
    .byte 0x18
    .org 0x21dcc-ORIGIN
P_00021dcc:
    .byte 0x00
    .org 0x21dcd-ORIGIN
P_00021dcd:
    .byte 0x00
    .org 0x21dce-ORIGIN
P_00021dce:
    .byte 0x04
    .org 0x21dcf-ORIGIN
P_00021dcf:
    .byte 0x4e
    .org 0x22590-ORIGIN
L_00022590:
    cmp/pl r4
    .org 0x22592-ORIGIN
L_00022592:
    bt L_00022596
    .org 0x22594-ORIGIN
L_00022594:
    neg r4,r4
    .org 0x22596-ORIGIN
L_00022596:
    rts
    .org 0x22598-ORIGIN
L_00022598:
    mov r4,r0
    .org 0x262e0-ORIGIN
L_000262e0:
    sts.l pr,@-r15
    .org 0x262e2-ORIGIN
L_000262e2:
    mov.l r4,@-r15
    .org 0x262e4-ORIGIN
L_000262e4:
    extu.w r7,r7
    .org 0x262e6-ORIGIN
L_000262e6:
    mov r5,r0
    .org 0x262e8-ORIGIN
L_000262e8:
    mov r7,r5
    .org 0x262ea-ORIGIN
L_000262ea:
    mov.l P_00026318,r7
    .org 0x262ec-ORIGIN
L_000262ec:
    jsr @r7
    .org 0x262ee-ORIGIN
L_000262ee:
    mov #0xf,r4
    .org 0x262f0-ORIGIN
L_000262f0:
    mov.l r5,@-r15
    .org 0x262f2-ORIGIN
L_000262f2:
    mov.l r4,@-r15
    .org 0x262f4-ORIGIN
L_000262f4:
    mov r6,r0
    .org 0x262f6-ORIGIN
L_000262f6:
    mov.l @(0x10,r15),r5
    .org 0x262f8-ORIGIN
L_000262f8:
    extu.w r5,r5
    .org 0x262fa-ORIGIN
L_000262fa:
    mov.l P_0002631c,r7
    .org 0x262fc-ORIGIN
L_000262fc:
    jsr @r7
    .org 0x262fe-ORIGIN
L_000262fe:
    mov #0x1e,r4
    .org 0x26300-ORIGIN
L_00026300:
    mov.l @r15+,r0
    .org 0x26302-ORIGIN
L_00026302:
    mov.l @r15+,r1
    .org 0x26304-ORIGIN
L_00026304:
    shll r0
    .org 0x26306-ORIGIN
L_00026306:
    mov r4,r2
    .org 0x26308-ORIGIN
L_00026308:
    mov r5,r3
    .org 0x2630a-ORIGIN
L_0002630a:
    mov.l @r15+,r4
    .org 0x2630c-ORIGIN
L_0002630c:
    lds.l @r15+,pr
    .org 0x2630e-ORIGIN
L_0002630e:
    mov.l P_00026314,r7
    .org 0x26310-ORIGIN
L_00026310:
    jmp @r7
    .org 0x26312-ORIGIN
L_00026312:
    mov #0x10,r5
    .org 0x26314-ORIGIN
P_00026314:
    .byte 0x00
    .org 0x26315-ORIGIN
P_00026315:
    .byte 0x02
    .org 0x26316-ORIGIN
P_00026316:
    .byte 0x68
    .org 0x26317-ORIGIN
P_00026317:
    .byte 0x48
    .org 0x26318-ORIGIN
P_00026318:
    .byte 0x00
    .org 0x26319-ORIGIN
P_00026319:
    .byte 0x02
    .org 0x2631a-ORIGIN
P_0002631a:
    .byte 0x6a
    .org 0x2631b-ORIGIN
P_0002631b:
    .byte 0x0c
    .org 0x2631c-ORIGIN
P_0002631c:
    .byte 0x00
    .org 0x2631d-ORIGIN
P_0002631d:
    .byte 0x02
    .org 0x2631e-ORIGIN
P_0002631e:
    .byte 0x69
    .org 0x2631f-ORIGIN
P_0002631f:
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
    .org 0x26a0c-ORIGIN
L_00026a0c:
    mov r4,r3
    .org 0x26a0e-ORIGIN
L_00026a0e:
    mov.b @(r0,r4),r1
    .org 0x26a10-ORIGIN
L_00026a10:
    extu.b r1,r1
    .org 0x26a12-ORIGIN
L_00026a12:
    shll2 r1
    .org 0x26a14-ORIGIN
L_00026a14:
    shll2 r1
    .org 0x26a16-ORIGIN
L_00026a16:
    cmp/eq r5,r1
    .org 0x26a18-ORIGIN
L_00026a18:
    bt L_00026a52
    .org 0x26a1a-ORIGIN
L_00026a1a:
    cmp/hi r5,r1
    .org 0x26a1c-ORIGIN
L_00026a1c:
    bt L_00026a4a
    .org 0x26a1e-ORIGIN
L_00026a1e:
    cmp/eq r4,r3
    .org 0x26a20-ORIGIN
L_00026a20:
    bt L_00026a52
    .org 0x26a22-ORIGIN
L_00026a22:
    sub r1,r5
    .org 0x26a24-ORIGIN
L_00026a24:
    shll16 r5
    .org 0x26a26-ORIGIN
L_00026a26:
    mov r4,r3
    .org 0x26a28-ORIGIN
L_00026a28:
    add r0,r3
    .org 0x26a2a-ORIGIN
L_00026a2a:
    mov.b @r3,r1
    .org 0x26a2c-ORIGIN
L_00026a2c:
    mov.b @(0x1,r3),r0
    .org 0x26a2e-ORIGIN
L_00026a2e:
    extu.b r1,r1
    .org 0x26a30-ORIGIN
L_00026a30:
    extu.b r0,r0
    .org 0x26a32-ORIGIN
L_00026a32:
    shll2 r0
    .org 0x26a34-ORIGIN
L_00026a34:
    shll2 r1
    .org 0x26a36-ORIGIN
L_00026a36:
    shll2 r0
    .org 0x26a38-ORIGIN
L_00026a38:
    shll2 r1
    .org 0x26a3a-ORIGIN
L_00026a3a:
    sts.l pr,@-r15
    .org 0x26a3c-ORIGIN
L_00026a3c:
    mov.l P_00026a58,r2
    .org 0x26a3e-ORIGIN
L_00026a3e:
    sub r1,r0
    .org 0x26a40-ORIGIN
L_00026a40:
    jsr @r2
    .org 0x26a42-ORIGIN
L_00026a42:
    mov r5,r1
    .org 0x26a44-ORIGIN
L_00026a44:
    lds.l @r15+,pr
    .org 0x26a46-ORIGIN
L_00026a46:
    rts
    .org 0x26a48-ORIGIN
L_00026a48:
    mov r0,r5
    .org 0x26a4a-ORIGIN
L_00026a4a:
    add #-0x1,r4
    .org 0x26a4c-ORIGIN
L_00026a4c:
    cmp/pz r4
    .org 0x26a4e-ORIGIN
L_00026a4e:
    bt L_00026a0e
    .org 0x26a50-ORIGIN
L_00026a50:
    mov #0x0,r4
    .org 0x26a52-ORIGIN
L_00026a52:
    rts
    .org 0x26a54-ORIGIN
L_00026a54:
    mov #0x0,r5
    .org 0x26a58-ORIGIN
P_00026a58:
    .byte 0x00
    .org 0x26a59-ORIGIN
P_00026a59:
    .byte 0x02
    .org 0x26a5a-ORIGIN
P_00026a5a:
    .byte 0x6c
    .org 0x26a5b-ORIGIN
P_00026a5b:
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
    .org 0x702c6-ORIGIN
L_000702c6:
    mov.l r12,@-r15
    .org 0x702c8-ORIGIN
L_000702c8:
    mov.l r13,@-r15
    .org 0x702ca-ORIGIN
L_000702ca:
    mov.l r14,@-r15
    .org 0x702cc-ORIGIN
L_000702cc:
    sts.l pr,@-r15
    .org 0x702ce-ORIGIN
L_000702ce:
    stc.l gbr,@-r15
    .org 0x702d0-ORIGIN
L_000702d0:
    mov.l P_000704b0,r0
    .org 0x702d2-ORIGIN
L_000702d2:
    ldc r0,gbr
    .org 0x702d4-ORIGIN
L_000702d4:
    add #-0x4,r15
    .org 0x702d6-ORIGIN
L_000702d6:
    mov.l P_000704b0,r12
    .org 0x702d8-ORIGIN
L_000702d8:
    mov.w P_000703fa,r0
    .org 0x702da-ORIGIN
L_000702da:
    mov.b @(r0,r12),r6
    .org 0x702dc-ORIGIN
L_000702dc:
    mov.w P_000703fc,r0
    .org 0x702de-ORIGIN
L_000702de:
    mov.b @(r0,r12),r2
    .org 0x702e0-ORIGIN
L_000702e0:
    mov.w P_000703fe,r0
    .org 0x702e2-ORIGIN
L_000702e2:
    cmp/eq r2,r6
    .org 0x702e4-ORIGIN
L_000702e4:
    bf/s L_000702fc
    .org 0x702e6-ORIGIN
L_000702e6:
    mov.w @(r0,r12),r2
    .org 0x702e8-ORIGIN
L_000702e8:
    mov #0x6,r0
    .org 0x702ea-ORIGIN
L_000702ea:
    mov.l P_000704b4,r13
    .org 0x702ec-ORIGIN
L_000702ec:
    shll8 r0
    .org 0x702ee-ORIGIN
L_000702ee:
    extu.w r2,r4
    .org 0x702f0-ORIGIN
L_000702f0:
    mov.w @(r0,r12),r2
    .org 0x702f2-ORIGIN
L_000702f2:
    extu.w r2,r2
    .org 0x702f4-ORIGIN
L_000702f4:
    jsr @r13
    .org 0x702f6-ORIGIN
L_000702f6:
    sub r2,r4
    .org 0x702f8-ORIGIN
L_000702f8:
    bra L_00070316
    .org 0x702fa-ORIGIN
L_000702fa:
    nop
    .org 0x702fc-ORIGIN
L_000702fc:
    mov #0x6,r0
    .org 0x702fe-ORIGIN
L_000702fe:
    mov.l P_000704b4,r13
    .org 0x70300-ORIGIN
L_00070300:
    shll8 r0
    .org 0x70302-ORIGIN
L_00070302:
    extu.w r2,r6
    .org 0x70304-ORIGIN
L_00070304:
    mov.w @(r0,r12),r2
    .org 0x70306-ORIGIN
L_00070306:
    mov #-0x1,r5
    .org 0x70308-ORIGIN
L_00070308:
    extu.w r2,r2
    .org 0x7030a-ORIGIN
L_0007030a:
    add r2,r6
    .org 0x7030c-ORIGIN
L_0007030c:
    extu.w r5,r5
    .org 0x7030e-ORIGIN
L_0007030e:
    cmp/hi r5,r6
    .org 0x70310-ORIGIN
L_00070310:
    bf L_00070314
    .org 0x70312-ORIGIN
L_00070312:
    mov r5,r6
    .org 0x70314-ORIGIN
L_00070314:
    mov r6,r0
    .org 0x70316-ORIGIN
L_00070316:
    mov.w r0,@(0x19e,gbr)
    .org 0x70318-ORIGIN
L_00070318:
    mov #-0x1,r0
    .org 0x7031a-ORIGIN
L_0007031a:
    mov.w r0,@(0x2,r15)
    .org 0x7031c-ORIGIN
L_0007031c:
    mov.w P_00070400,r0
    .org 0x7031e-ORIGIN
L_0007031e:
    mov.l P_000704b8,r4
    .org 0x70320-ORIGIN
L_00070320:
    mov.w @(r0,r12),r14
    .org 0x70322-ORIGIN
L_00070322:
    mov.l P_000704bc,r5
    .org 0x70324-ORIGIN
L_00070324:
    mov.l P_000704c0,r6
    .org 0x70326-ORIGIN
L_00070326:
    mov.l P_000704c4,r2
    .org 0x70328-ORIGIN
L_00070328:
    jsr @r2
    .org 0x7032a-ORIGIN
L_0007032a:
    extu.w r14,r7
    .org 0x7032c-ORIGIN
L_0007032c:
    mov #-0x80,r5
    .org 0x7032e-ORIGIN
L_0007032e:
    extu.w r0,r6
    .org 0x70330-ORIGIN
L_00070330:
    shll8 r5
    .org 0x70332-ORIGIN
L_00070332:
    mov r6,r2
    .org 0x70334-ORIGIN
L_00070334:
    add r5,r2
    .org 0x70336-ORIGIN
L_00070336:
    mov #0xa,r4
    .org 0x70338-ORIGIN
L_00070338:
    cmp/ge r4,r2
    .org 0x7033a-ORIGIN
L_0007033a:
    bt L_00070340
    .org 0x7033c-ORIGIN
L_0007033c:
    bra L_00070344
    .org 0x7033e-ORIGIN
L_0007033e:
    mov #0xa,r2
    .org 0x70340-ORIGIN
L_00070340:
    add r5,r6
    .org 0x70342-ORIGIN
L_00070342:
    mov r6,r2
    .org 0x70344-ORIGIN
L_00070344:
    mov.w P_00070402,r0
    .org 0x70346-ORIGIN
L_00070346:
    mov r2,r6
    .org 0x70348-ORIGIN
L_00070348:
    mov.w r2,@(r0,r12)
    .org 0x7034a-ORIGIN
L_0007034a:
    extu.w r2,r2
    .org 0x7034c-ORIGIN
L_0007034c:
    add #-0x5,r2
    .org 0x7034e-ORIGIN
L_0007034e:
    cmp/pz r2
    .org 0x70350-ORIGIN
L_00070350:
    bt L_00070356
    .org 0x70352-ORIGIN
L_00070352:
    bra L_00070358
    .org 0x70354-ORIGIN
L_00070354:
    mov #0x0,r6
    .org 0x70356-ORIGIN
L_00070356:
    add #-0x5,r6
    .org 0x70358-ORIGIN
L_00070358:
    mov r6,r14
    .org 0x7035a-ORIGIN
L_0007035a:
    mov.l P_000704c8,r6
    .org 0x7035c-ORIGIN
L_0007035c:
    mov #0x7e,r0
    .org 0x7035e-ORIGIN
L_0007035e:
    jsr @r13
    .org 0x70360-ORIGIN
L_00070360:
    mov.w @(r0,r6),r4
    .org 0x70362-ORIGIN
L_00070362:
    mov.l P_000704cc,r6
    .org 0x70364-ORIGIN
L_00070364:
    mov r0,r1
    .org 0x70366-ORIGIN
L_00070366:
    shll16 r1
    .org 0x70368-ORIGIN
L_00070368:
    jsr @r6
    .org 0x7036a-ORIGIN
L_0007036a:
    extu.w r14,r0
    .org 0x7036c-ORIGIN
L_0007036c:
    mov #-0x1,r5
    .org 0x7036e-ORIGIN
L_0007036e:
    extu.w r5,r5
    .org 0x70370-ORIGIN
L_00070370:
    cmp/hi r5,r0
    .org 0x70372-ORIGIN
L_00070372:
    bf/s L_00070378
    .org 0x70374-ORIGIN
L_00070374:
    mov r0,r2
    .org 0x70376-ORIGIN
L_00070376:
    mov r5,r2
    .org 0x70378-ORIGIN
L_00070378:
    mov.w P_000703fe,r0
    .org 0x7037a-ORIGIN
L_0007037a:
    mov.w r2,@(r0,r12)
    .org 0x7037c-ORIGIN
L_0007037c:
    add #0x4,r15
    .org 0x7037e-ORIGIN
L_0007037e:
    ldc.l @r15+,gbr
    .org 0x70380-ORIGIN
L_00070380:
    lds.l @r15+,pr
    .org 0x70382-ORIGIN
L_00070382:
    mov.l @r15+,r14
    .org 0x70384-ORIGIN
L_00070384:
    mov.l @r15+,r13
    .org 0x70386-ORIGIN
L_00070386:
    rts
    .org 0x70388-ORIGIN
L_00070388:
    mov.l @r15+,r12
    .org 0x703fa-ORIGIN
P_000703fa:
    .byte 0x05
    .org 0x703fb-ORIGIN
P_000703fb:
    .byte 0xf4
    .org 0x703fc-ORIGIN
P_000703fc:
    .byte 0x06
    .org 0x703fd-ORIGIN
P_000703fd:
    .byte 0x28
    .org 0x703fe-ORIGIN
P_000703fe:
    .byte 0x05
    .org 0x703ff-ORIGIN
P_000703ff:
    .byte 0xec
    .org 0x70400-ORIGIN
P_00070400:
    .byte 0x04
    .org 0x70401-ORIGIN
P_00070401:
    .byte 0x76
    .org 0x70402-ORIGIN
P_00070402:
    .byte 0x07
    .org 0x70403-ORIGIN
P_00070403:
    .byte 0x38
    .org 0x704b0-ORIGIN
P_000704b0:
    .byte 0xff
    .org 0x704b1-ORIGIN
P_000704b1:
    .byte 0xff
    .org 0x704b2-ORIGIN
P_000704b2:
    .byte 0x12
    .org 0x704b3-ORIGIN
P_000704b3:
    .byte 0x8c
    .org 0x704b4-ORIGIN
P_000704b4:
    .byte 0x00
    .org 0x704b5-ORIGIN
P_000704b5:
    .byte 0x02
    .org 0x704b6-ORIGIN
P_000704b6:
    .byte 0x25
    .org 0x704b7-ORIGIN
P_000704b7:
    .byte 0x90
    .org 0x704b8-ORIGIN
P_000704b8:
    .byte 0x00
    .org 0x704b9-ORIGIN
P_000704b9:
    .byte 0x00
    .org 0x704ba-ORIGIN
P_000704ba:
    .byte 0xe9
    .org 0x704bb-ORIGIN
P_000704bb:
    .byte 0x8e
    .org 0x704bc-ORIGIN
P_000704bc:
    .byte 0x00
    .org 0x704bd-ORIGIN
P_000704bd:
    .byte 0x01
    .org 0x704be-ORIGIN
P_000704be:
    .byte 0x1d
    .org 0x704bf-ORIGIN
P_000704bf:
    .byte 0x0c
    .org 0x704c0-ORIGIN
P_000704c0:
    .byte 0x00
    .org 0x704c1-ORIGIN
P_000704c1:
    .byte 0x01
    .org 0x704c2-ORIGIN
P_000704c2:
    .byte 0x41
    .org 0x704c3-ORIGIN
P_000704c3:
    .byte 0x14
    .org 0x704c4-ORIGIN
P_000704c4:
    .byte 0x00
    .org 0x704c5-ORIGIN
P_000704c5:
    .byte 0x02
    .org 0x704c6-ORIGIN
P_000704c6:
    .byte 0x62
    .org 0x704c7-ORIGIN
P_000704c7:
    .byte 0xe0
    .org 0x704c8-ORIGIN
P_000704c8:
    .byte 0xff
    .org 0x704c9-ORIGIN
P_000704c9:
    .byte 0xff
    .org 0x704ca-ORIGIN
P_000704ca:
    .byte 0x23
    .org 0x704cb-ORIGIN
P_000704cb:
    .byte 0xbc
    .org 0x704cc-ORIGIN
P_000704cc:
    .byte 0x00
    .org 0x704cd-ORIGIN
P_000704cd:
    .byte 0x02
    .org 0x704ce-ORIGIN
P_000704ce:
    .byte 0x1c
    .org 0x704cf-ORIGIN
P_000704cf:
    .byte 0xe0
