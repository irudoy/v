! Complete natural72C3C paired word-curve sum caller and all four exact real helpers.
    .text
    .balign 4
    .set ORIGIN,0x26524
    .org 0x26524-ORIGIN
L_00026524:
    sts.l pr,@-r15
    .org 0x26526-ORIGIN
L_00026526:
    mov.l r4,@-r15
    .org 0x26528-ORIGIN
L_00026528:
    mov r5,r0
    .org 0x2652a-ORIGIN
L_0002652a:
    extu.w r6,r5
    .org 0x2652c-ORIGIN
L_0002652c:
    mov.l P_0002654c,r7
    .org 0x2652e-ORIGIN
L_0002652e:
    jsr @r7
    .org 0x26530-ORIGIN
L_00026530:
    mov #0x3e,r4
    .org 0x26532-ORIGIN
L_00026532:
    mov.l @r15+,r6
    .org 0x26534-ORIGIN
L_00026534:
    add r4,r6
    .org 0x26536-ORIGIN
L_00026536:
    mov.w @(0x2,r6),r0
    .org 0x26538-ORIGIN
L_00026538:
    extu.w r0,r2
    .org 0x2653a-ORIGIN
L_0002653a:
    mov r5,r3
    .org 0x2653c-ORIGIN
L_0002653c:
    mov.w @r6,r1
    .org 0x2653e-ORIGIN
L_0002653e:
    lds.l @r15+,pr
    .org 0x26540-ORIGIN
L_00026540:
    mov.l P_00026548,r6
    .org 0x26542-ORIGIN
L_00026542:
    jmp @r6
    .org 0x26544-ORIGIN
L_00026544:
    extu.w r1,r0
    .org 0x26548-ORIGIN
P_00026548:
    .byte 0x00
    .org 0x26549-ORIGIN
P_00026549:
    .byte 0x02
    .org 0x2654a-ORIGIN
P_0002654a:
    .byte 0x67
    .org 0x2654b-ORIGIN
P_0002654b:
    .byte 0x40
    .org 0x2654c-ORIGIN
P_0002654c:
    .byte 0x00
    .org 0x2654d-ORIGIN
P_0002654d:
    .byte 0x02
    .org 0x2654e-ORIGIN
P_0002654e:
    .byte 0x69
    .org 0x2654f-ORIGIN
P_0002654f:
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
    .org 0x72c3c-ORIGIN
L_00072c3c:
    mov.l r12,@-r15
    .org 0x72c3e-ORIGIN
L_00072c3e:
    mov.l r13,@-r15
    .org 0x72c40-ORIGIN
L_00072c40:
    mov.l r14,@-r15
    .org 0x72c42-ORIGIN
L_00072c42:
    sts.l pr,@-r15
    .org 0x72c44-ORIGIN
L_00072c44:
    stc.l gbr,@-r15
    .org 0x72c46-ORIGIN
L_00072c46:
    mov.l P_00072cfc,r0
    .org 0x72c48-ORIGIN
L_00072c48:
    ldc r0,gbr
    .org 0x72c4a-ORIGIN
L_00072c4a:
    add #-0x4,r15
    .org 0x72c4c-ORIGIN
L_00072c4c:
    mov.l P_00072d00,r6
    .org 0x72c4e-ORIGIN
L_00072c4e:
    mov.b @(0x4,r6),r0
    .org 0x72c50-ORIGIN
L_00072c50:
    tst #0x1,r0
    .org 0x72c52-ORIGIN
L_00072c52:
    bf L_00072ca6
    .org 0x72c54-ORIGIN
L_00072c54:
    mov.b @r6,r0
    .org 0x72c56-ORIGIN
L_00072c56:
    tst #0x4,r0
    .org 0x72c58-ORIGIN
L_00072c58:
    bf L_00072ca6
    .org 0x72c5a-ORIGIN
L_00072c5a:
    mov.l P_00072cfc,r7
    .org 0x72c5c-ORIGIN
L_00072c5c:
    mov.w P_00072cf4,r0
    .org 0x72c5e-ORIGIN
L_00072c5e:
    mov.l P_00072d04,r4
    .org 0x72c60-ORIGIN
L_00072c60:
    mov.w @(r0,r7),r5
    .org 0x72c62-ORIGIN
L_00072c62:
    mov.w @(0xb4,gbr),r0
    .org 0x72c64-ORIGIN
L_00072c64:
    extu.w r5,r5
    .org 0x72c66-ORIGIN
L_00072c66:
    extu.w r0,r2
    .org 0x72c68-ORIGIN
L_00072c68:
    mov r5,r6
    .org 0x72c6a-ORIGIN
L_00072c6a:
    add r2,r6
    .org 0x72c6c-ORIGIN
L_00072c6c:
    mov.w @r4,r2
    .org 0x72c6e-ORIGIN
L_00072c6e:
    extu.w r2,r4
    .org 0x72c70-ORIGIN
L_00072c70:
    shlr2 r4
    .org 0x72c72-ORIGIN
L_00072c72:
    sub r4,r6
    .org 0x72c74-ORIGIN
L_00072c74:
    cmp/pz r6
    .org 0x72c76-ORIGIN
L_00072c76:
    bt/s L_00072c7c
    .org 0x72c78-ORIGIN
L_00072c78:
    mov r6,r2
    .org 0x72c7a-ORIGIN
L_00072c7a:
    mov #0x0,r2
    .org 0x72c7c-ORIGIN
L_00072c7c:
    mov #-0x1,r6
    .org 0x72c7e-ORIGIN
L_00072c7e:
    extu.w r6,r6
    .org 0x72c80-ORIGIN
L_00072c80:
    cmp/gt r6,r2
    .org 0x72c82-ORIGIN
L_00072c82:
    bf L_00072c86
    .org 0x72c84-ORIGIN
L_00072c84:
    mov r6,r2
    .org 0x72c86-ORIGIN
L_00072c86:
    mov.l P_00072cfc,r7
    .org 0x72c88-ORIGIN
L_00072c88:
    mov.w P_00072cf6,r0
    .org 0x72c8a-ORIGIN
L_00072c8a:
    mov.l P_00072d08,r6
    .org 0x72c8c-ORIGIN
L_00072c8c:
    mov.w r2,@(r0,r7)
    .org 0x72c8e-ORIGIN
L_00072c8e:
    mov #0x49,r0
    .org 0x72c90-ORIGIN
L_00072c90:
    shll2 r0
    .org 0x72c92-ORIGIN
L_00072c92:
    mov.w @(r0,r6),r2
    .org 0x72c94-ORIGIN
L_00072c94:
    extu.w r2,r6
    .org 0x72c96-ORIGIN
L_00072c96:
    mov r5,r2
    .org 0x72c98-ORIGIN
L_00072c98:
    mov #-0x1,r5
    .org 0x72c9a-ORIGIN
L_00072c9a:
    add r6,r2
    .org 0x72c9c-ORIGIN
L_00072c9c:
    extu.w r5,r5
    .org 0x72c9e-ORIGIN
L_00072c9e:
    cmp/hi r5,r2
    .org 0x72ca0-ORIGIN
L_00072ca0:
    bf L_00072ce2
    .org 0x72ca2-ORIGIN
L_00072ca2:
    bra L_00072ce2
    .org 0x72ca4-ORIGIN
L_00072ca4:
    mov r5,r2
    .org 0x72ca6-ORIGIN
L_00072ca6:
    mov.l P_00072d0c,r14
    .org 0x72ca8-ORIGIN
L_00072ca8:
    mov #0x24,r0
    .org 0x72caa-ORIGIN
L_00072caa:
    mov.l P_00072d10,r12
    .org 0x72cac-ORIGIN
L_00072cac:
    mov.w @(r0,r14),r6
    .org 0x72cae-ORIGIN
L_00072cae:
    mov.l P_00072d14,r13
    .org 0x72cb0-ORIGIN
L_00072cb0:
    mov r12,r4
    .org 0x72cb2-ORIGIN
L_00072cb2:
    mov.l P_00072d18,r2
    .org 0x72cb4-ORIGIN
L_00072cb4:
    extu.w r6,r6
    .org 0x72cb6-ORIGIN
L_00072cb6:
    jsr @r2
    .org 0x72cb8-ORIGIN
L_00072cb8:
    mov r13,r5
    .org 0x72cba-ORIGIN
L_00072cba:
    mov.w r0,@r15
    .org 0x72cbc-ORIGIN
L_00072cbc:
    mov #0x26,r0
    .org 0x72cbe-ORIGIN
L_00072cbe:
    mov.w @(r0,r14),r6
    .org 0x72cc0-ORIGIN
L_00072cc0:
    mov r12,r4
    .org 0x72cc2-ORIGIN
L_00072cc2:
    mov.l P_00072d18,r2
    .org 0x72cc4-ORIGIN
L_00072cc4:
    mov r13,r5
    .org 0x72cc6-ORIGIN
L_00072cc6:
    jsr @r2
    .org 0x72cc8-ORIGIN
L_00072cc8:
    extu.w r6,r6
    .org 0x72cca-ORIGIN
L_00072cca:
    mov.w @r15,r7
    .org 0x72ccc-ORIGIN
L_00072ccc:
    extu.w r0,r2
    .org 0x72cce-ORIGIN
L_00072cce:
    mov #-0x1,r5
    .org 0x72cd0-ORIGIN
L_00072cd0:
    extu.w r7,r7
    .org 0x72cd2-ORIGIN
L_00072cd2:
    add r2,r7
    .org 0x72cd4-ORIGIN
L_00072cd4:
    extu.w r5,r2
    .org 0x72cd6-ORIGIN
L_00072cd6:
    cmp/hi r2,r7
    .org 0x72cd8-ORIGIN
L_00072cd8:
    bt L_00072cdc
    .org 0x72cda-ORIGIN
L_00072cda:
    mov r7,r2
    .org 0x72cdc-ORIGIN
L_00072cdc:
    mov.l P_00072cfc,r7
    .org 0x72cde-ORIGIN
L_00072cde:
    mov.w P_00072cf6,r0
    .org 0x72ce0-ORIGIN
L_00072ce0:
    mov.w r2,@(r0,r7)
    .org 0x72ce2-ORIGIN
L_00072ce2:
    mov.w P_00072cf8,r0
    .org 0x72ce4-ORIGIN
L_00072ce4:
    mov.w r2,@(r0,r7)
    .org 0x72ce6-ORIGIN
L_00072ce6:
    add #0x4,r15
    .org 0x72ce8-ORIGIN
L_00072ce8:
    ldc.l @r15+,gbr
    .org 0x72cea-ORIGIN
L_00072cea:
    lds.l @r15+,pr
    .org 0x72cec-ORIGIN
L_00072cec:
    mov.l @r15+,r14
    .org 0x72cee-ORIGIN
L_00072cee:
    mov.l @r15+,r13
    .org 0x72cf0-ORIGIN
L_00072cf0:
    rts
    .org 0x72cf2-ORIGIN
L_00072cf2:
    mov.l @r15+,r12
    .org 0x72cf4-ORIGIN
P_00072cf4:
    .byte 0x05
    .org 0x72cf5-ORIGIN
P_00072cf5:
    .byte 0xb2
    .org 0x72cf6-ORIGIN
P_00072cf6:
    .byte 0x07
    .org 0x72cf7-ORIGIN
P_00072cf7:
    .byte 0x26
    .org 0x72cf8-ORIGIN
P_00072cf8:
    .byte 0x07
    .org 0x72cf9-ORIGIN
P_00072cf9:
    .byte 0x2a
    .org 0x72cfc-ORIGIN
P_00072cfc:
    .byte 0xff
    .org 0x72cfd-ORIGIN
P_00072cfd:
    .byte 0xff
    .org 0x72cfe-ORIGIN
P_00072cfe:
    .byte 0x12
    .org 0x72cff-ORIGIN
P_00072cff:
    .byte 0x8c
    .org 0x72d00-ORIGIN
P_00072d00:
    .byte 0xff
    .org 0x72d01-ORIGIN
P_00072d01:
    .byte 0xff
    .org 0x72d02-ORIGIN
P_00072d02:
    .byte 0x24
    .org 0x72d03-ORIGIN
P_00072d03:
    .byte 0xce
    .org 0x72d04-ORIGIN
P_00072d04:
    .byte 0xff
    .org 0x72d05-ORIGIN
P_00072d05:
    .byte 0xff
    .org 0x72d06-ORIGIN
P_00072d06:
    .byte 0x12
    .org 0x72d07-ORIGIN
P_00072d07:
    .byte 0x0e
    .org 0x72d08-ORIGIN
P_00072d08:
    .byte 0xff
    .org 0x72d09-ORIGIN
P_00072d09:
    .byte 0xff
    .org 0x72d0a-ORIGIN
P_00072d0a:
    .byte 0x28
    .org 0x72d0b-ORIGIN
P_00072d0b:
    .byte 0xf8
    .org 0x72d0c-ORIGIN
P_00072d0c:
    .byte 0xff
    .org 0x72d0d-ORIGIN
P_00072d0d:
    .byte 0xff
    .org 0x72d0e-ORIGIN
P_00072d0e:
    .byte 0x28
    .org 0x72d0f-ORIGIN
P_00072d0f:
    .byte 0x98
    .org 0x72d10-ORIGIN
P_00072d10:
    .byte 0x00
    .org 0x72d11-ORIGIN
P_00072d11:
    .byte 0x01
    .org 0x72d12-ORIGIN
P_00072d12:
    .byte 0x32
    .org 0x72d13-ORIGIN
P_00072d13:
    .byte 0x02
    .org 0x72d14-ORIGIN
P_00072d14:
    .byte 0x00
    .org 0x72d15-ORIGIN
P_00072d15:
    .byte 0x01
    .org 0x72d16-ORIGIN
P_00072d16:
    .byte 0x55
    .org 0x72d17-ORIGIN
P_00072d17:
    .byte 0xa0
    .org 0x72d18-ORIGIN
P_00072d18:
    .byte 0x00
    .org 0x72d19-ORIGIN
P_00072d19:
    .byte 0x02
    .org 0x72d1a-ORIGIN
P_00072d1a:
    .byte 0x65
    .org 0x72d1b-ORIGIN
P_00072d1b:
    .byte 0x24
