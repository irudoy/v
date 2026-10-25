! Complete stock producer, conditional consumer and all natural helper bodies.
    .text
    .balign 4
    .set ORIGIN,0x870c
    .org 0x870e-ORIGIN
P_0000870e:
    .byte 0x28
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
    .org 0x259e4-ORIGIN
L_000259e4:
    mov.l P_00025b98,r1
    .org 0x259e6-ORIGIN
L_000259e6:
    exts.w r4,r0
    .org 0x259e8-ORIGIN
L_000259e8:
    cmp/eq #-0x1,r0
    .org 0x259ea-ORIGIN
L_000259ea:
    bt L_00025a0c
    .org 0x259ec-ORIGIN
L_000259ec:
    mov r0,r7
    .org 0x259ee-ORIGIN
L_000259ee:
    shll r7
    .org 0x259f0-ORIGIN
L_000259f0:
    mov r1,r2
    .org 0x259f2-ORIGIN
L_000259f2:
    add r0,r7
    .org 0x259f4-ORIGIN
L_000259f4:
    add r7,r2
    .org 0x259f6-ORIGIN
L_000259f6:
    mov.b @(0x2,r2),r0
    .org 0x259f8-ORIGIN
L_000259f8:
    tst #0x40,r0
    .org 0x259fa-ORIGIN
L_000259fa:
    bf/s L_00025a0e
    .org 0x259fc-ORIGIN
L_000259fc:
    mov #0x1,r5
    .org 0x259fe-ORIGIN
L_000259fe:
    mov r1,r2
    .org 0x25a00-ORIGIN
L_00025a00:
    add r7,r2
    .org 0x25a02-ORIGIN
L_00025a02:
    mov.b @(0x2,r2),r0
    .org 0x25a04-ORIGIN
L_00025a04:
    tst #0x20,r0
    .org 0x25a06-ORIGIN
L_00025a06:
    bf L_00025a0e
    .org 0x25a08-ORIGIN
L_00025a08:
    bra L_00025a0e
    .org 0x25a0a-ORIGIN
L_00025a0a:
    mov #0x0,r5
    .org 0x25a0c-ORIGIN
L_00025a0c:
    mov #0x0,r5
    .org 0x25a0e-ORIGIN
L_00025a0e:
    rts
    .org 0x25a10-ORIGIN
L_00025a10:
    mov r5,r0
    .org 0x25b98-ORIGIN
P_00025b98:
    .byte 0xff
    .org 0x25b99-ORIGIN
P_00025b99:
    .byte 0xff
    .org 0x25b9a-ORIGIN
P_00025b9a:
    .byte 0x57
    .org 0x25b9b-ORIGIN
P_00025b9b:
    .byte 0x18
    .org 0x263f4-ORIGIN
L_000263f4:
    mov.l P_0002640c,r0
    .org 0x263f6-ORIGIN
L_000263f6:
    extu.w r5,r5
    .org 0x263f8-ORIGIN
L_000263f8:
    cmp/hs r0,r5
    .org 0x263fa-ORIGIN
L_000263fa:
    bt L_00026402
    .org 0x263fc-ORIGIN
L_000263fc:
    mov.l P_00026408,r6
    .org 0x263fe-ORIGIN
L_000263fe:
    jmp @r6
    .org 0x26400-ORIGIN
L_00026400:
    mov #0x0,r3
    .org 0x26402-ORIGIN
L_00026402:
    rts
    .org 0x26404-ORIGIN
L_00026404:
    mov.w @(0x1e,r4),r0
    .org 0x26408-ORIGIN
P_00026408:
    .byte 0x00
    .org 0x26409-ORIGIN
P_00026409:
    .byte 0x02
    .org 0x2640a-ORIGIN
P_0002640a:
    .byte 0x6a
    .org 0x2640b-ORIGIN
P_0002640b:
    .byte 0x64
    .org 0x2640c-ORIGIN
P_0002640c:
    .byte 0x00
    .org 0x2640d-ORIGIN
P_0002640d:
    .byte 0x00
    .org 0x2640e-ORIGIN
P_0002640e:
    .byte 0xf0
    .org 0x2640f-ORIGIN
P_0002640f:
    .byte 0x00
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
    .org 0x8083c-ORIGIN
L_0008083c:
    mov.l r14,@-r15
    .org 0x8083e-ORIGIN
L_0008083e:
    sts.l pr,@-r15
    .org 0x80840-ORIGIN
L_00080840:
    mov.l P_000808a4,r6
    .org 0x80842-ORIGIN
L_00080842:
    mov.l P_000808a8,r14
    .org 0x80844-ORIGIN
L_00080844:
    mov.b @r6,r0
    .org 0x80846-ORIGIN
L_00080846:
    tst #0x20,r0
    .org 0x80848-ORIGIN
L_00080848:
    bf L_000808ac
    .org 0x8084a-ORIGIN
L_0008084a:
    mov #-0x44,r4
    .org 0x8084c-ORIGIN
L_0008084c:
    jsr @r14
    .org 0x8084e-ORIGIN
L_0008084e:
    extu.b r4,r4
    .org 0x80850-ORIGIN
L_00080850:
    tst r0,r0
    .org 0x80852-ORIGIN
L_00080852:
    bf L_0008090e
    .org 0x80854-ORIGIN
L_00080854:
    jsr @r14
    .org 0x80856-ORIGIN
L_00080856:
    mov #0x9,r4
    .org 0x80858-ORIGIN
L_00080858:
    tst r0,r0
    .org 0x8085a-ORIGIN
L_0008085a:
    bt L_00080914
    .org 0x8085c-ORIGIN
L_0008085c:
    bra L_0008090e
    .org 0x8085e-ORIGIN
L_0008085e:
    nop
    .org 0x808a4-ORIGIN
P_000808a4:
    .byte 0xff
    .org 0x808a5-ORIGIN
P_000808a5:
    .byte 0xff
    .org 0x808a6-ORIGIN
P_000808a6:
    .byte 0x24
    .org 0x808a7-ORIGIN
P_000808a7:
    .byte 0x4f
    .org 0x808a8-ORIGIN
P_000808a8:
    .byte 0x00
    .org 0x808a9-ORIGIN
P_000808a9:
    .byte 0x02
    .org 0x808aa-ORIGIN
P_000808aa:
    .byte 0x59
    .org 0x808ab-ORIGIN
P_000808ab:
    .byte 0xe4
    .org 0x808ac-ORIGIN
L_000808ac:
    mov #-0x45,r4
    .org 0x808ae-ORIGIN
L_000808ae:
    jsr @r14
    .org 0x808b0-ORIGIN
L_000808b0:
    extu.b r4,r4
    .org 0x808b2-ORIGIN
L_000808b2:
    tst r0,r0
    .org 0x808b4-ORIGIN
L_000808b4:
    bf L_00080914
    .org 0x808b6-ORIGIN
L_000808b6:
    jsr @r14
    .org 0x808b8-ORIGIN
L_000808b8:
    mov #0x8,r4
    .org 0x808ba-ORIGIN
L_000808ba:
    tst r0,r0
    .org 0x808bc-ORIGIN
L_000808bc:
    bf L_00080914
    .org 0x808be-ORIGIN
L_000808be:
    jsr @r14
    .org 0x808c0-ORIGIN
L_000808c0:
    mov #-0x1,r4
    .org 0x808c2-ORIGIN
L_000808c2:
    tst r0,r0
    .org 0x808c4-ORIGIN
L_000808c4:
    bf L_00080914
    .org 0x808c6-ORIGIN
L_000808c6:
    mov.l P_00080aa4,r2
    .org 0x808c8-ORIGIN
L_000808c8:
    mov #0x17,r0
    .org 0x808ca-ORIGIN
L_000808ca:
    mov.l P_00080aa8,r4
    .org 0x808cc-ORIGIN
L_000808cc:
    mov.b @(r0,r2),r6
    .org 0x808ce-ORIGIN
L_000808ce:
    mov.l P_00080aac,r2
    .org 0x808d0-ORIGIN
L_000808d0:
    extu.b r6,r5
    .org 0x808d2-ORIGIN
L_000808d2:
    shll8 r5
    .org 0x808d4-ORIGIN
L_000808d4:
    jsr @r2
    .org 0x808d6-ORIGIN
L_000808d6:
    extu.w r5,r5
    .org 0x808d8-ORIGIN
L_000808d8:
    mov.l P_00080ab0,r5
    .org 0x808da-ORIGIN
L_000808da:
    extu.w r0,r0
    .org 0x808dc-ORIGIN
L_000808dc:
    mov.l P_00080ab4,r4
    .org 0x808de-ORIGIN
L_000808de:
    mov.w @r5,r2
    .org 0x808e0-ORIGIN
L_000808e0:
    extu.w r2,r1
    .org 0x808e2-ORIGIN
L_000808e2:
    jsr @r4
    .org 0x808e4-ORIGIN
L_000808e4:
    shll8 r1
    .org 0x808e6-ORIGIN
L_000808e6:
    mov.l P_00080ab8,r5
    .org 0x808e8-ORIGIN
L_000808e8:
    mov r0,r6
    .org 0x808ea-ORIGIN
L_000808ea:
    mov.b @r5,r0
    .org 0x808ec-ORIGIN
L_000808ec:
    tst #0x10,r0
    .org 0x808ee-ORIGIN
L_000808ee:
    bt L_00080916
    .org 0x808f0-ORIGIN
L_000808f0:
    mov.l P_00080abc,r2
    .org 0x808f2-ORIGIN
L_000808f2:
    mov.w P_000809ce,r0
    .org 0x808f4-ORIGIN
L_000808f4:
    mov.b @(r0,r2),r7
    .org 0x808f6-ORIGIN
L_000808f6:
    extu.b r7,r0
    .org 0x808f8-ORIGIN
L_000808f8:
    tst r0,r0
    .org 0x808fa-ORIGIN
L_000808fa:
    bt L_0008090e
    .org 0x808fc-ORIGIN
L_000808fc:
    shll2 r6
    .org 0x808fe-ORIGIN
L_000808fe:
    mov.l P_00080ab4,r4
    .org 0x80900-ORIGIN
L_00080900:
    shll2 r6
    .org 0x80902-ORIGIN
L_00080902:
    shll2 r6
    .org 0x80904-ORIGIN
L_00080904:
    shll r6
    .org 0x80906-ORIGIN
L_00080906:
    jsr @r4
    .org 0x80908-ORIGIN
L_00080908:
    mov r6,r1
    .org 0x8090a-ORIGIN
L_0008090a:
    bra L_00080916
    .org 0x8090c-ORIGIN
L_0008090c:
    mov r0,r6
    .org 0x8090e-ORIGIN
L_0008090e:
    mov #-0x1,r2
    .org 0x80910-ORIGIN
L_00080910:
    bra L_00080916
    .org 0x80912-ORIGIN
L_00080912:
    extu.b r2,r6
    .org 0x80914-ORIGIN
L_00080914:
    mov #0x0,r6
    .org 0x80916-ORIGIN
L_00080916:
    mov #-0x1,r2
    .org 0x80918-ORIGIN
L_00080918:
    extu.b r2,r2
    .org 0x8091a-ORIGIN
L_0008091a:
    cmp/hi r2,r6
    .org 0x8091c-ORIGIN
L_0008091c:
    bt L_00080920
    .org 0x8091e-ORIGIN
L_0008091e:
    mov r6,r2
    .org 0x80920-ORIGIN
L_00080920:
    mov r2,r6
    .org 0x80922-ORIGIN
L_00080922:
    mov.l P_00080ac0,r2
    .org 0x80924-ORIGIN
L_00080924:
    mov #0x1a,r0
    .org 0x80926-ORIGIN
L_00080926:
    mov.b r6,@(r0,r2)
    .org 0x80928-ORIGIN
L_00080928:
    lds.l @r15+,pr
    .org 0x8092a-ORIGIN
L_0008092a:
    rts
    .org 0x8092c-ORIGIN
L_0008092c:
    mov.l @r15+,r14
    .org 0x809ce-ORIGIN
P_000809ce:
    .byte 0x09
    .org 0x809cf-ORIGIN
P_000809cf:
    .byte 0xa7
    .org 0x80aa4-ORIGIN
P_00080aa4:
    .byte 0xff
    .org 0x80aa5-ORIGIN
P_00080aa5:
    .byte 0xff
    .org 0x80aa6-ORIGIN
P_00080aa6:
    .byte 0x11
    .org 0x80aa7-ORIGIN
P_00080aa7:
    .byte 0x9c
    .org 0x80aa8-ORIGIN
P_00080aa8:
    .byte 0x00
    .org 0x80aa9-ORIGIN
P_00080aa9:
    .byte 0x01
    .org 0x80aaa-ORIGIN
P_00080aaa:
    .byte 0x49
    .org 0x80aab-ORIGIN
P_00080aab:
    .byte 0x1a
    .org 0x80aac-ORIGIN
P_00080aac:
    .byte 0x00
    .org 0x80aad-ORIGIN
P_00080aad:
    .byte 0x02
    .org 0x80aae-ORIGIN
P_00080aae:
    .byte 0x63
    .org 0x80aaf-ORIGIN
P_00080aaf:
    .byte 0xf4
    .org 0x80ab0-ORIGIN
P_00080ab0:
    .byte 0xff
    .org 0x80ab1-ORIGIN
P_00080ab1:
    .byte 0xff
    .org 0x80ab2-ORIGIN
P_00080ab2:
    .byte 0x10
    .org 0x80ab3-ORIGIN
P_00080ab3:
    .byte 0x24
    .org 0x80ab4-ORIGIN
P_00080ab4:
    .byte 0x00
    .org 0x80ab5-ORIGIN
P_00080ab5:
    .byte 0x02
    .org 0x80ab6-ORIGIN
P_00080ab6:
    .byte 0x1c
    .org 0x80ab7-ORIGIN
P_00080ab7:
    .byte 0xe0
    .org 0x80ab8-ORIGIN
P_00080ab8:
    .byte 0x00
    .org 0x80ab9-ORIGIN
P_00080ab9:
    .byte 0x00
    .org 0x80aba-ORIGIN
P_00080aba:
    .byte 0x87
    .org 0x80abb-ORIGIN
P_00080abb:
    .byte 0x0e
    .org 0x80abc-ORIGIN
P_00080abc:
    .byte 0xff
    .org 0x80abd-ORIGIN
P_00080abd:
    .byte 0xff
    .org 0x80abe-ORIGIN
P_00080abe:
    .byte 0x28
    .org 0x80abf-ORIGIN
P_00080abf:
    .byte 0xf8
    .org 0x80ac0-ORIGIN
P_00080ac0:
    .byte 0xff
    .org 0x80ac1-ORIGIN
P_00080ac1:
    .byte 0xff
    .org 0x80ac2-ORIGIN
P_00080ac2:
    .byte 0x41
    .org 0x80ac3-ORIGIN
P_00080ac3:
    .byte 0x24
    .org 0xb997c-ORIGIN
L_000b997c:
    sts.l pr,@-r15
    .org 0xb997e-ORIGIN
L_000b997e:
    mov.l P_000b99a0,r6
    .org 0xb9980-ORIGIN
L_000b9980:
    mov.l P_000b99a4,r4
    .org 0xb9982-ORIGIN
L_000b9982:
    mov.w @(0x10,r6),r0
    .org 0xb9984-ORIGIN
L_000b9984:
    mov.l P_000b99a8,r5
    .org 0xb9986-ORIGIN
L_000b9986:
    extu.w r0,r6
    .org 0xb9988-ORIGIN
L_000b9988:
    mov.l P_000b99ac,r2
    .org 0xb998a-ORIGIN
L_000b998a:
    shlr8 r6
    .org 0xb998c-ORIGIN
L_000b998c:
    jsr @r2
    .org 0xb998e-ORIGIN
L_000b998e:
    extu.b r6,r6
    .org 0xb9990-ORIGIN
L_000b9990:
    mov r0,r2
    .org 0xb9992-ORIGIN
L_000b9992:
    mov.l P_000b99b0,r6
    .org 0xb9994-ORIGIN
L_000b9994:
    mov.w P_000b999c,r0
    .org 0xb9996-ORIGIN
L_000b9996:
    lds.l @r15+,pr
    .org 0xb9998-ORIGIN
L_000b9998:
    rts
    .org 0xb999a-ORIGIN
L_000b999a:
    mov.b r2,@(r0,r6)
    .org 0xb999c-ORIGIN
P_000b999c:
    .byte 0x09
    .org 0xb999d-ORIGIN
P_000b999d:
    .byte 0xa7
    .org 0xb99a0-ORIGIN
P_000b99a0:
    .byte 0xff
    .org 0xb99a1-ORIGIN
P_000b99a1:
    .byte 0xff
    .org 0xb99a2-ORIGIN
P_000b99a2:
    .byte 0x45
    .org 0xb99a3-ORIGIN
P_000b99a3:
    .byte 0x14
    .org 0xb99a4-ORIGIN
P_000b99a4:
    .byte 0x00
    .org 0xb99a5-ORIGIN
P_000b99a5:
    .byte 0x01
    .org 0xb99a6-ORIGIN
P_000b99a6:
    .byte 0x29
    .org 0xb99a7-ORIGIN
P_000b99a7:
    .byte 0xd2
    .org 0xb99a8-ORIGIN
P_000b99a8:
    .byte 0x00
    .org 0xb99a9-ORIGIN
P_000b99a9:
    .byte 0x01
    .org 0xb99aa-ORIGIN
P_000b99aa:
    .byte 0x1b
    .org 0xb99ab-ORIGIN
P_000b99ab:
    .byte 0x7b
    .org 0xb99ac-ORIGIN
P_000b99ac:
    .byte 0x00
    .org 0xb99ad-ORIGIN
P_000b99ad:
    .byte 0x02
    .org 0xb99ae-ORIGIN
P_000b99ae:
    .byte 0x64
    .org 0xb99af-ORIGIN
P_000b99af:
    .byte 0xa0
    .org 0xb99b0-ORIGIN
P_000b99b0:
    .byte 0xff
    .org 0xb99b1-ORIGIN
P_000b99b1:
    .byte 0xff
    .org 0xb99b2-ORIGIN
P_000b99b2:
    .byte 0x28
    .org 0xb99b3-ORIGIN
P_000b99b3:
    .byte 0xf8
