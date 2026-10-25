! Complete stock second-channel weight and output builder with all real callees.
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
    .org 0x265f0-ORIGIN
L_000265f0:
    sts.l pr,@-r15
    .org 0x265f2-ORIGIN
L_000265f2:
    mov.l r4,@-r15
    .org 0x265f4-ORIGIN
L_000265f4:
    extu.w r7,r7
    .org 0x265f6-ORIGIN
L_000265f6:
    mov r5,r0
    .org 0x265f8-ORIGIN
L_000265f8:
    mov r7,r5
    .org 0x265fa-ORIGIN
L_000265fa:
    mov.l P_00026624,r7
    .org 0x265fc-ORIGIN
L_000265fc:
    jsr @r7
    .org 0x265fe-ORIGIN
L_000265fe:
    mov #0xe,r4
    .org 0x26600-ORIGIN
L_00026600:
    mov.l r4,@-r15
    .org 0x26602-ORIGIN
L_00026602:
    mov.l r5,@-r15
    .org 0x26604-ORIGIN
L_00026604:
    mov r6,r0
    .org 0x26606-ORIGIN
L_00026606:
    mov.l @(0x10,r15),r5
    .org 0x26608-ORIGIN
L_00026608:
    extu.w r5,r5
    .org 0x2660a-ORIGIN
L_0002660a:
    jsr @r7
    .org 0x2660c-ORIGIN
L_0002660c:
    mov #0xe,r4
    .org 0x2660e-ORIGIN
L_0002660e:
    mov.l @r15+,r1
    .org 0x26610-ORIGIN
L_00026610:
    mov.l @r15+,r0
    .org 0x26612-ORIGIN
L_00026612:
    mov r4,r2
    .org 0x26614-ORIGIN
L_00026614:
    mov r5,r3
    .org 0x26616-ORIGIN
L_00026616:
    mov.l @r15+,r4
    .org 0x26618-ORIGIN
L_00026618:
    lds.l @r15+,pr
    .org 0x2661a-ORIGIN
L_0002661a:
    mov.l P_00026620,r7
    .org 0x2661c-ORIGIN
L_0002661c:
    jmp @r7
    .org 0x2661e-ORIGIN
L_0002661e:
    mov #0x8,r5
    .org 0x26620-ORIGIN
P_00026620:
    .byte 0x00
    .org 0x26621-ORIGIN
P_00026621:
    .byte 0x02
    .org 0x26622-ORIGIN
P_00026622:
    .byte 0x6b
    .org 0x26623-ORIGIN
P_00026623:
    .byte 0x28
    .org 0x26624-ORIGIN
P_00026624:
    .byte 0x00
    .org 0x26625-ORIGIN
P_00026625:
    .byte 0x02
    .org 0x26626-ORIGIN
P_00026626:
    .byte 0x6b
    .org 0x26627-ORIGIN
P_00026627:
    .byte 0x84
    .org 0x266e8-ORIGIN
L_000266e8:
    sts.l pr,@-r15
    .org 0x266ea-ORIGIN
L_000266ea:
    mov.l r4,@-r15
    .org 0x266ec-ORIGIN
L_000266ec:
    mov r5,r0
    .org 0x266ee-ORIGIN
L_000266ee:
    extu.w r6,r5
    .org 0x266f0-ORIGIN
L_000266f0:
    mov.l P_00026710,r7
    .org 0x266f2-ORIGIN
L_000266f2:
    jsr @r7
    .org 0x266f4-ORIGIN
L_000266f4:
    mov #0x1e,r4
    .org 0x266f6-ORIGIN
L_000266f6:
    mov.l @r15+,r6
    .org 0x266f8-ORIGIN
L_000266f8:
    add r4,r6
    .org 0x266fa-ORIGIN
L_000266fa:
    mov.w @(0x2,r6),r0
    .org 0x266fc-ORIGIN
L_000266fc:
    extu.w r0,r2
    .org 0x266fe-ORIGIN
L_000266fe:
    mov r5,r3
    .org 0x26700-ORIGIN
L_00026700:
    mov.w @r6,r1
    .org 0x26702-ORIGIN
L_00026702:
    lds.l @r15+,pr
    .org 0x26704-ORIGIN
L_00026704:
    mov.l P_0002670c,r6
    .org 0x26706-ORIGIN
L_00026706:
    jmp @r6
    .org 0x26708-ORIGIN
L_00026708:
    extu.w r1,r0
    .org 0x2670c-ORIGIN
P_0002670c:
    .byte 0x00
    .org 0x2670d-ORIGIN
P_0002670d:
    .byte 0x02
    .org 0x2670e-ORIGIN
P_0002670e:
    .byte 0x6a
    .org 0x2670f-ORIGIN
P_0002670f:
    .byte 0xf8
    .org 0x26710-ORIGIN
P_00026710:
    .byte 0x00
    .org 0x26711-ORIGIN
P_00026711:
    .byte 0x02
    .org 0x26712-ORIGIN
P_00026712:
    .byte 0x6b
    .org 0x26713-ORIGIN
P_00026713:
    .byte 0x84
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
    .org 0x7a804-ORIGIN
L_0007a804:
    mov.l r8,@-r15
    .org 0x7a806-ORIGIN
L_0007a806:
    mov.l r9,@-r15
    .org 0x7a808-ORIGIN
L_0007a808:
    mov.l r10,@-r15
    .org 0x7a80a-ORIGIN
L_0007a80a:
    mov.l r11,@-r15
    .org 0x7a80c-ORIGIN
L_0007a80c:
    mov.l r12,@-r15
    .org 0x7a80e-ORIGIN
L_0007a80e:
    mov.l r13,@-r15
    .org 0x7a810-ORIGIN
L_0007a810:
    mov.l r14,@-r15
    .org 0x7a812-ORIGIN
L_0007a812:
    sts.l pr,@-r15
    .org 0x7a814-ORIGIN
L_0007a814:
    sts.l macl,@-r15
    .org 0x7a816-ORIGIN
L_0007a816:
    add #-0x4,r15
    .org 0x7a818-ORIGIN
L_0007a818:
    mov.l P_0007a9a4,r6
    .org 0x7a81a-ORIGIN
L_0007a81a:
    mov #0x2f,r0
    .org 0x7a81c-ORIGIN
L_0007a81c:
    mov.b @(r0,r6),r0
    .org 0x7a81e-ORIGIN
L_0007a81e:
    tst #0x2,r0
    .org 0x7a820-ORIGIN
L_0007a820:
    bt L_0007a838
    .org 0x7a822-ORIGIN
L_0007a822:
    mov.l P_0007a9a8,r8
    .org 0x7a824-ORIGIN
L_0007a824:
    mov.l P_0007a9ac,r4
    .org 0x7a826-ORIGIN
L_0007a826:
    mov.w @(0x1e,r8),r0
    .org 0x7a828-ORIGIN
L_0007a828:
    mov.l P_0007a9b0,r11
    .org 0x7a82a-ORIGIN
L_0007a82a:
    mov.l P_0007a9b4,r12
    .org 0x7a82c-ORIGIN
L_0007a82c:
    extu.w r0,r6
    .org 0x7a82e-ORIGIN
L_0007a82e:
    jsr @r12
    .org 0x7a830-ORIGIN
L_0007a830:
    mov r11,r5
    .org 0x7a832-ORIGIN
L_0007a832:
    mov.l P_0007a9b8,r4
    .org 0x7a834-ORIGIN
L_0007a834:
    bra L_0007a84c
    .org 0x7a836-ORIGIN
L_0007a836:
    extu.w r0,r13
    .org 0x7a838-ORIGIN
L_0007a838:
    mov.l P_0007a9a8,r8
    .org 0x7a83a-ORIGIN
L_0007a83a:
    mov.l P_0007a9bc,r4
    .org 0x7a83c-ORIGIN
L_0007a83c:
    mov.w @(0x1e,r8),r0
    .org 0x7a83e-ORIGIN
L_0007a83e:
    mov.l P_0007a9b0,r11
    .org 0x7a840-ORIGIN
L_0007a840:
    mov.l P_0007a9b4,r12
    .org 0x7a842-ORIGIN
L_0007a842:
    extu.w r0,r6
    .org 0x7a844-ORIGIN
L_0007a844:
    jsr @r12
    .org 0x7a846-ORIGIN
L_0007a846:
    mov r11,r5
    .org 0x7a848-ORIGIN
L_0007a848:
    mov.l P_0007a9c0,r4
    .org 0x7a84a-ORIGIN
L_0007a84a:
    extu.w r0,r13
    .org 0x7a84c-ORIGIN
L_0007a84c:
    mov.w @(0x1e,r8),r0
    .org 0x7a84e-ORIGIN
L_0007a84e:
    mov r11,r5
    .org 0x7a850-ORIGIN
L_0007a850:
    jsr @r12
    .org 0x7a852-ORIGIN
L_0007a852:
    extu.w r0,r6
    .org 0x7a854-ORIGIN
L_0007a854:
    mov.l P_0007a9c4,r6
    .org 0x7a856-ORIGIN
L_0007a856:
    extu.w r0,r14
    .org 0x7a858-ORIGIN
L_0007a858:
    mov.b @r6,r0
    .org 0x7a85a-ORIGIN
L_0007a85a:
    tst #0x80,r0
    .org 0x7a85c-ORIGIN
L_0007a85c:
    bt L_0007a866
    .org 0x7a85e-ORIGIN
L_0007a85e:
    mov.l P_0007a9c8,r6
    .org 0x7a860-ORIGIN
L_0007a860:
    mov.l P_0007a9cc,r9
    .org 0x7a862-ORIGIN
L_0007a862:
    bra L_0007a888
    .org 0x7a864-ORIGIN
L_0007a864:
    mov.w @r6,r5
    .org 0x7a866-ORIGIN
L_0007a866:
    mov.l P_0007a9cc,r9
    .org 0x7a868-ORIGIN
L_0007a868:
    mov.w P_0007a914,r0
    .org 0x7a86a-ORIGIN
L_0007a86a:
    mov.l P_0007a9d0,r7
    .org 0x7a86c-ORIGIN
L_0007a86c:
    mov.b @(r0,r9),r2
    .org 0x7a86e-ORIGIN
L_0007a86e:
    mov.l P_0007a9d4,r6
    .org 0x7a870-ORIGIN
L_0007a870:
    extu.b r2,r0
    .org 0x7a872-ORIGIN
L_0007a872:
    mov.l P_0007a9d8,r4
    .org 0x7a874-ORIGIN
L_0007a874:
    shll8 r0
    .org 0x7a876-ORIGIN
L_0007a876:
    mov.l P_0007a9dc,r2
    .org 0x7a878-ORIGIN
L_0007a878:
    mov.w r0,@(0x2,r15)
    .org 0x7a87a-ORIGIN
L_0007a87a:
    mov #0x28,r0
    .org 0x7a87c-ORIGIN
L_0007a87c:
    mov.w @(r0,r7),r10
    .org 0x7a87e-ORIGIN
L_0007a87e:
    mov r6,r5
    .org 0x7a880-ORIGIN
L_0007a880:
    add #0x10,r5
    .org 0x7a882-ORIGIN
L_0007a882:
    jsr @r2
    .org 0x7a884-ORIGIN
L_0007a884:
    extu.w r10,r7
    .org 0x7a886-ORIGIN
L_0007a886:
    mov r0,r5
    .org 0x7a888-ORIGIN
L_0007a888:
    mov.w P_0007a916,r0
    .org 0x7a88a-ORIGIN
L_0007a88a:
    mov.l P_0007a9e0,r2
    .org 0x7a88c-ORIGIN
L_0007a88c:
    mov.w r5,@(r0,r9)
    .org 0x7a88e-ORIGIN
L_0007a88e:
    extu.w r5,r5
    .org 0x7a890-ORIGIN
L_0007a890:
    sub r5,r2
    .org 0x7a892-ORIGIN
L_0007a892:
    mul.l r13,r2
    .org 0x7a894-ORIGIN
L_0007a894:
    mov.l P_0007a9e4,r2
    .org 0x7a896-ORIGIN
L_0007a896:
    sts macl,r6
    .org 0x7a898-ORIGIN
L_0007a898:
    mul.l r14,r5
    .org 0x7a89a-ORIGIN
L_0007a89a:
    sts macl,r5
    .org 0x7a89c-ORIGIN
L_0007a89c:
    cmp/hi r2,r5
    .org 0x7a89e-ORIGIN
L_0007a89e:
    bt L_0007a8aa
    .org 0x7a8a0-ORIGIN
L_0007a8a0:
    neg r6,r2
    .org 0x7a8a2-ORIGIN
L_0007a8a2:
    cmp/gt r2,r5
    .org 0x7a8a4-ORIGIN
L_0007a8a4:
    bt L_0007a8aa
    .org 0x7a8a6-ORIGIN
L_0007a8a6:
    bra L_0007a8b8
    .org 0x7a8a8-ORIGIN
L_0007a8a8:
    mov #0x0,r6
    .org 0x7a8aa-ORIGIN
L_0007a8aa:
    add r6,r5
    .org 0x7a8ac-ORIGIN
L_0007a8ac:
    mov r5,r6
    .org 0x7a8ae-ORIGIN
L_0007a8ae:
    shlr8 r6
    .org 0x7a8b0-ORIGIN
L_0007a8b0:
    shlr2 r6
    .org 0x7a8b2-ORIGIN
L_0007a8b2:
    shlr2 r6
    .org 0x7a8b4-ORIGIN
L_0007a8b4:
    shlr2 r6
    .org 0x7a8b6-ORIGIN
L_0007a8b6:
    shlr r6
    .org 0x7a8b8-ORIGIN
L_0007a8b8:
    mov #-0x1,r2
    .org 0x7a8ba-ORIGIN
L_0007a8ba:
    extu.w r2,r2
    .org 0x7a8bc-ORIGIN
L_0007a8bc:
    cmp/hi r2,r6
    .org 0x7a8be-ORIGIN
L_0007a8be:
    bt L_0007a8c2
    .org 0x7a8c0-ORIGIN
L_0007a8c0:
    mov r6,r2
    .org 0x7a8c2-ORIGIN
L_0007a8c2:
    mov.w P_0007a918,r0
    .org 0x7a8c4-ORIGIN
L_0007a8c4:
    mov r11,r5
    .org 0x7a8c6-ORIGIN
L_0007a8c6:
    mov.l P_0007a9e8,r4
    .org 0x7a8c8-ORIGIN
L_0007a8c8:
    mov.w r2,@(r0,r9)
    .org 0x7a8ca-ORIGIN
L_0007a8ca:
    mov.w @(0x1e,r8),r0
    .org 0x7a8cc-ORIGIN
L_0007a8cc:
    jsr @r12
    .org 0x7a8ce-ORIGIN
L_0007a8ce:
    extu.w r0,r6
    .org 0x7a8d0-ORIGIN
L_0007a8d0:
    mov r0,r2
    .org 0x7a8d2-ORIGIN
L_0007a8d2:
    mov.w P_0007a91a,r0
    .org 0x7a8d4-ORIGIN
L_0007a8d4:
    mov.l P_0007a9ec,r5
    .org 0x7a8d6-ORIGIN
L_0007a8d6:
    mov.w r2,@(r0,r9)
    .org 0x7a8d8-ORIGIN
L_0007a8d8:
    mov.b @(0x2,r5),r0
    .org 0x7a8da-ORIGIN
L_0007a8da:
    tst #0x40,r0
    .org 0x7a8dc-ORIGIN
L_0007a8dc:
    bt L_0007a8f6
    .org 0x7a8de-ORIGIN
L_0007a8de:
    mov.w P_0007a918,r0
    .org 0x7a8e0-ORIGIN
L_0007a8e0:
    extu.w r2,r2
    .org 0x7a8e2-ORIGIN
L_0007a8e2:
    mov.w @(r0,r9),r6
    .org 0x7a8e4-ORIGIN
L_0007a8e4:
    extu.w r6,r5
    .org 0x7a8e6-ORIGIN
L_0007a8e6:
    mul.l r5,r2
    .org 0x7a8e8-ORIGIN
L_0007a8e8:
    sts macl,r14
    .org 0x7a8ea-ORIGIN
L_0007a8ea:
    shlr8 r14
    .org 0x7a8ec-ORIGIN
L_0007a8ec:
    shlr2 r14
    .org 0x7a8ee-ORIGIN
L_0007a8ee:
    shlr2 r14
    .org 0x7a8f0-ORIGIN
L_0007a8f0:
    shlr2 r14
    .org 0x7a8f2-ORIGIN
L_0007a8f2:
    bra L_0007a8fc
    .org 0x7a8f4-ORIGIN
L_0007a8f4:
    shlr r14
    .org 0x7a8f6-ORIGIN
L_0007a8f6:
    mov.w P_0007a918,r0
    .org 0x7a8f8-ORIGIN
L_0007a8f8:
    mov.w @(r0,r9),r6
    .org 0x7a8fa-ORIGIN
L_0007a8fa:
    extu.w r6,r14
    .org 0x7a8fc-ORIGIN
L_0007a8fc:
    mov.w P_0007a91c,r0
    .org 0x7a8fe-ORIGIN
L_0007a8fe:
    mov #-0x1,r1
    .org 0x7a900-ORIGIN
L_0007a900:
    mov.l P_0007a9f0,r4
    .org 0x7a902-ORIGIN
L_0007a902:
    mov.w @(r0,r9),r2
    .org 0x7a904-ORIGIN
L_0007a904:
    extu.w r2,r6
    .org 0x7a906-ORIGIN
L_0007a906:
    jsr @r4
    .org 0x7a908-ORIGIN
L_0007a908:
    mov r6,r0
    .org 0x7a90a-ORIGIN
L_0007a90a:
    cmp/hi r0,r14
    .org 0x7a90c-ORIGIN
L_0007a90c:
    bf L_0007a920
    .org 0x7a90e-ORIGIN
L_0007a90e:
    mov.w P_0007a91e,r14
    .org 0x7a910-ORIGIN
L_0007a910:
    bra L_0007a93e
    .org 0x7a912-ORIGIN
L_0007a912:
    nop
    .org 0x7a914-ORIGIN
P_0007a914:
    .byte 0x03
    .org 0x7a915-ORIGIN
P_0007a915:
    .byte 0x79
    .org 0x7a916-ORIGIN
P_0007a916:
    .byte 0x0c
    .org 0x7a917-ORIGIN
P_0007a917:
    .byte 0xfc
    .org 0x7a918-ORIGIN
P_0007a918:
    .byte 0x0c
    .org 0x7a919-ORIGIN
P_0007a919:
    .byte 0xd2
    .org 0x7a91a-ORIGIN
P_0007a91a:
    .byte 0x0d
    .org 0x7a91b-ORIGIN
P_0007a91b:
    .byte 0x04
    .org 0x7a91c-ORIGIN
P_0007a91c:
    .byte 0x08
    .org 0x7a91d-ORIGIN
P_0007a91d:
    .byte 0xea
    .org 0x7a91e-ORIGIN
P_0007a91e:
    .byte 0x03
    .org 0x7a91f-ORIGIN
P_0007a91f:
    .byte 0x20
    .org 0x7a920-ORIGIN
L_0007a920:
    mov.w P_0007a998,r0
    .org 0x7a922-ORIGIN
L_0007a922:
    mov.w @(r0,r9),r6
    .org 0x7a924-ORIGIN
L_0007a924:
    extu.w r6,r2
    .org 0x7a926-ORIGIN
L_0007a926:
    mul.l r14,r2
    .org 0x7a928-ORIGIN
L_0007a928:
    mov.w P_0007a99a,r2
    .org 0x7a92a-ORIGIN
L_0007a92a:
    sts macl,r6
    .org 0x7a92c-ORIGIN
L_0007a92c:
    shlr8 r6
    .org 0x7a92e-ORIGIN
L_0007a92e:
    shlr2 r6
    .org 0x7a930-ORIGIN
L_0007a930:
    shlr2 r6
    .org 0x7a932-ORIGIN
L_0007a932:
    shlr2 r6
    .org 0x7a934-ORIGIN
L_0007a934:
    shlr r6
    .org 0x7a936-ORIGIN
L_0007a936:
    cmp/hi r2,r6
    .org 0x7a938-ORIGIN
L_0007a938:
    bf L_0007a93c
    .org 0x7a93a-ORIGIN
L_0007a93a:
    mov r2,r6
    .org 0x7a93c-ORIGIN
L_0007a93c:
    mov r6,r14
    .org 0x7a93e-ORIGIN
L_0007a93e:
    mov.w @(0x1e,r8),r0
    .org 0x7a940-ORIGIN
L_0007a940:
    mov.w P_0007a99a,r5
    .org 0x7a942-ORIGIN
L_0007a942:
    extu.w r0,r6
    .org 0x7a944-ORIGIN
L_0007a944:
    cmp/ge r5,r6
    .org 0x7a946-ORIGIN
L_0007a946:
    bf L_0007a94a
    .org 0x7a948-ORIGIN
L_0007a948:
    mov r6,r14
    .org 0x7a94a-ORIGIN
L_0007a94a:
    mov.w P_0007a99c,r0
    .org 0x7a94c-ORIGIN
L_0007a94c:
    mov.w @(r0,r9),r6
    .org 0x7a94e-ORIGIN
L_0007a94e:
    extu.w r6,r6
    .org 0x7a950-ORIGIN
L_0007a950:
    cmp/hi r6,r14
    .org 0x7a952-ORIGIN
L_0007a952:
    bt L_0007a956
    .org 0x7a954-ORIGIN
L_0007a954:
    mov r14,r6
    .org 0x7a956-ORIGIN
L_0007a956:
    mov r6,r5
    .org 0x7a958-ORIGIN
L_0007a958:
    mov.l P_0007a9f4,r6
    .org 0x7a95a-ORIGIN
L_0007a95a:
    mov #0x6b,r0
    .org 0x7a95c-ORIGIN
L_0007a95c:
    mov.b @(r0,r6),r0
    .org 0x7a95e-ORIGIN
L_0007a95e:
    tst #0x40,r0
    .org 0x7a960-ORIGIN
L_0007a960:
    bt L_0007a968
    .org 0x7a962-ORIGIN
L_0007a962:
    mov.w P_0007a99e,r0
    .org 0x7a964-ORIGIN
L_0007a964:
    mov.w @(r0,r9),r2
    .org 0x7a966-ORIGIN
L_0007a966:
    extu.w r2,r5
    .org 0x7a968-ORIGIN
L_0007a968:
    mov.w P_0007a9a0,r6
    .org 0x7a96a-ORIGIN
L_0007a96a:
    mov.w P_0007a9a2,r0
    .org 0x7a96c-ORIGIN
L_0007a96c:
    mul.l r5,r6
    .org 0x7a96e-ORIGIN
L_0007a96e:
    mov.l P_0007a9f0,r4
    .org 0x7a970-ORIGIN
L_0007a970:
    add #0x49,r6
    .org 0x7a972-ORIGIN
L_0007a972:
    mov.w r5,@(r0,r9)
    .org 0x7a974-ORIGIN
L_0007a974:
    mov r6,r0
    .org 0x7a976-ORIGIN
L_0007a976:
    jsr @r4
    .org 0x7a978-ORIGIN
L_0007a978:
    sts macl,r1
    .org 0x7a97a-ORIGIN
L_0007a97a:
    mov.l P_0007a9f8,r6
    .org 0x7a97c-ORIGIN
L_0007a97c:
    mov r0,r2
    .org 0x7a97e-ORIGIN
L_0007a97e:
    mov #0x3a,r0
    .org 0x7a980-ORIGIN
L_0007a980:
    mov.w r2,@(r0,r6)
    .org 0x7a982-ORIGIN
L_0007a982:
    add #0x4,r15
    .org 0x7a984-ORIGIN
L_0007a984:
    lds.l @r15+,macl
    .org 0x7a986-ORIGIN
L_0007a986:
    lds.l @r15+,pr
    .org 0x7a988-ORIGIN
L_0007a988:
    mov.l @r15+,r14
    .org 0x7a98a-ORIGIN
L_0007a98a:
    mov.l @r15+,r13
    .org 0x7a98c-ORIGIN
L_0007a98c:
    mov.l @r15+,r12
    .org 0x7a98e-ORIGIN
L_0007a98e:
    mov.l @r15+,r11
    .org 0x7a990-ORIGIN
L_0007a990:
    mov.l @r15+,r10
    .org 0x7a992-ORIGIN
L_0007a992:
    mov.l @r15+,r9
    .org 0x7a994-ORIGIN
L_0007a994:
    rts
    .org 0x7a996-ORIGIN
L_0007a996:
    mov.l @r15+,r8
    .org 0x7a998-ORIGIN
P_0007a998:
    .byte 0x08
    .org 0x7a999-ORIGIN
P_0007a999:
    .byte 0xea
    .org 0x7a99a-ORIGIN
P_0007a99a:
    .byte 0x03
    .org 0x7a99b-ORIGIN
P_0007a99b:
    .byte 0x20
    .org 0x7a99c-ORIGIN
P_0007a99c:
    .byte 0x07
    .org 0x7a99d-ORIGIN
P_0007a99d:
    .byte 0x2c
    .org 0x7a99e-ORIGIN
P_0007a99e:
    .byte 0x0c
    .org 0x7a99f-ORIGIN
P_0007a99f:
    .byte 0xf2
    .org 0x7a9a0-ORIGIN
P_0007a9a0:
    .byte 0x02
    .org 0x7a9a1-ORIGIN
P_0007a9a1:
    .byte 0xd7
    .org 0x7a9a2-ORIGIN
P_0007a9a2:
    .byte 0x0c
    .org 0x7a9a3-ORIGIN
P_0007a9a3:
    .byte 0xd4
    .org 0x7a9a4-ORIGIN
P_0007a9a4:
    .byte 0xff
    .org 0x7a9a5-ORIGIN
P_0007a9a5:
    .byte 0xff
    .org 0x7a9a6-ORIGIN
P_0007a9a6:
    .byte 0x24
    .org 0x7a9a7-ORIGIN
P_0007a9a7:
    .byte 0x70
    .org 0x7a9a8-ORIGIN
P_0007a9a8:
    .byte 0xff
    .org 0x7a9a9-ORIGIN
P_0007a9a9:
    .byte 0xff
    .org 0x7a9aa-ORIGIN
P_0007a9aa:
    .byte 0x26
    .org 0x7a9ab-ORIGIN
P_0007a9ab:
    .byte 0x7a
    .org 0x7a9ac-ORIGIN
P_0007a9ac:
    .byte 0x00
    .org 0x7a9ad-ORIGIN
P_0007a9ad:
    .byte 0x01
    .org 0x7a9ae-ORIGIN
P_0007a9ae:
    .byte 0x90
    .org 0x7a9af-ORIGIN
P_0007a9af:
    .byte 0x90
    .org 0x7a9b0-ORIGIN
P_0007a9b0:
    .byte 0x00
    .org 0x7a9b1-ORIGIN
P_0007a9b1:
    .byte 0x01
    .org 0x7a9b2-ORIGIN
P_0007a9b2:
    .byte 0x8f
    .org 0x7a9b3-ORIGIN
P_0007a9b3:
    .byte 0x76
    .org 0x7a9b4-ORIGIN
P_0007a9b4:
    .byte 0x00
    .org 0x7a9b5-ORIGIN
P_0007a9b5:
    .byte 0x02
    .org 0x7a9b6-ORIGIN
P_0007a9b6:
    .byte 0x66
    .org 0x7a9b7-ORIGIN
P_0007a9b7:
    .byte 0xe8
    .org 0x7a9b8-ORIGIN
P_0007a9b8:
    .byte 0x00
    .org 0x7a9b9-ORIGIN
P_0007a9b9:
    .byte 0x01
    .org 0x7a9ba-ORIGIN
P_0007a9ba:
    .byte 0x90
    .org 0x7a9bb-ORIGIN
P_0007a9bb:
    .byte 0xb0
    .org 0x7a9bc-ORIGIN
P_0007a9bc:
    .byte 0x00
    .org 0x7a9bd-ORIGIN
P_0007a9bd:
    .byte 0x01
    .org 0x7a9be-ORIGIN
P_0007a9be:
    .byte 0x8c
    .org 0x7a9bf-ORIGIN
P_0007a9bf:
    .byte 0xf6
    .org 0x7a9c0-ORIGIN
P_0007a9c0:
    .byte 0x00
    .org 0x7a9c1-ORIGIN
P_0007a9c1:
    .byte 0x01
    .org 0x7a9c2-ORIGIN
P_0007a9c2:
    .byte 0x8d
    .org 0x7a9c3-ORIGIN
P_0007a9c3:
    .byte 0x16
    .org 0x7a9c4-ORIGIN
P_0007a9c4:
    .byte 0x00
    .org 0x7a9c5-ORIGIN
P_0007a9c5:
    .byte 0x00
    .org 0x7a9c6-ORIGIN
P_0007a9c6:
    .byte 0x83
    .org 0x7a9c7-ORIGIN
P_0007a9c7:
    .byte 0xc1
    .org 0x7a9c8-ORIGIN
P_0007a9c8:
    .byte 0x00
    .org 0x7a9c9-ORIGIN
P_0007a9c9:
    .byte 0x01
    .org 0x7a9ca-ORIGIN
P_0007a9ca:
    .byte 0x63
    .org 0x7a9cb-ORIGIN
P_0007a9cb:
    .byte 0x0c
    .org 0x7a9cc-ORIGIN
P_0007a9cc:
    .byte 0xff
    .org 0x7a9cd-ORIGIN
P_0007a9cd:
    .byte 0xff
    .org 0x7a9ce-ORIGIN
P_0007a9ce:
    .byte 0x28
    .org 0x7a9cf-ORIGIN
P_0007a9cf:
    .byte 0xf8
    .org 0x7a9d0-ORIGIN
P_0007a9d0:
    .byte 0xff
    .org 0x7a9d1-ORIGIN
P_0007a9d1:
    .byte 0xff
    .org 0x7a9d2-ORIGIN
P_0007a9d2:
    .byte 0x10
    .org 0x7a9d3-ORIGIN
P_0007a9d3:
    .byte 0x94
    .org 0x7a9d4-ORIGIN
P_0007a9d4:
    .byte 0x00
    .org 0x7a9d5-ORIGIN
P_0007a9d5:
    .byte 0x01
    .org 0x7a9d6-ORIGIN
P_0007a9d6:
    .byte 0x8a
    .org 0x7a9d7-ORIGIN
P_0007a9d7:
    .byte 0x86
    .org 0x7a9d8-ORIGIN
P_0007a9d8:
    .byte 0x00
    .org 0x7a9d9-ORIGIN
P_0007a9d9:
    .byte 0x01
    .org 0x7a9da-ORIGIN
P_0007a9da:
    .byte 0x6f
    .org 0x7a9db-ORIGIN
P_0007a9db:
    .byte 0x48
    .org 0x7a9dc-ORIGIN
P_0007a9dc:
    .byte 0x00
    .org 0x7a9dd-ORIGIN
P_0007a9dd:
    .byte 0x02
    .org 0x7a9de-ORIGIN
P_0007a9de:
    .byte 0x65
    .org 0x7a9df-ORIGIN
P_0007a9df:
    .byte 0xf0
    .org 0x7a9e0-ORIGIN
P_0007a9e0:
    .byte 0x00
    .org 0x7a9e1-ORIGIN
P_0007a9e1:
    .byte 0x00
    .org 0x7a9e2-ORIGIN
P_0007a9e2:
    .byte 0x80
    .org 0x7a9e3-ORIGIN
P_0007a9e3:
    .byte 0x00
    .org 0x7a9e4-ORIGIN
P_0007a9e4:
    .byte 0x7f
    .org 0x7a9e5-ORIGIN
P_0007a9e5:
    .byte 0xff
    .org 0x7a9e6-ORIGIN
P_0007a9e6:
    .byte 0xff
    .org 0x7a9e7-ORIGIN
P_0007a9e7:
    .byte 0xff
    .org 0x7a9e8-ORIGIN
P_0007a9e8:
    .byte 0x00
    .org 0x7a9e9-ORIGIN
P_0007a9e9:
    .byte 0x01
    .org 0x7a9ea-ORIGIN
P_0007a9ea:
    .byte 0x8d
    .org 0x7a9eb-ORIGIN
P_0007a9eb:
    .byte 0x36
    .org 0x7a9ec-ORIGIN
P_0007a9ec:
    .byte 0xff
    .org 0x7a9ed-ORIGIN
P_0007a9ed:
    .byte 0xff
    .org 0x7a9ee-ORIGIN
P_0007a9ee:
    .byte 0x24
    .org 0x7a9ef-ORIGIN
P_0007a9ef:
    .byte 0x5c
    .org 0x7a9f0-ORIGIN
P_0007a9f0:
    .byte 0x00
    .org 0x7a9f1-ORIGIN
P_0007a9f1:
    .byte 0x02
    .org 0x7a9f2-ORIGIN
P_0007a9f2:
    .byte 0x1c
    .org 0x7a9f3-ORIGIN
P_0007a9f3:
    .byte 0xe0
    .org 0x7a9f4-ORIGIN
P_0007a9f4:
    .byte 0xff
    .org 0x7a9f5-ORIGIN
P_0007a9f5:
    .byte 0xff
    .org 0x7a9f6-ORIGIN
P_0007a9f6:
    .byte 0x41
    .org 0x7a9f7-ORIGIN
P_0007a9f7:
    .byte 0xa9
    .org 0x7a9f8-ORIGIN
P_0007a9f8:
    .byte 0xff
    .org 0x7a9f9-ORIGIN
P_0007a9f9:
    .byte 0xff
    .org 0x7a9fa-ORIGIN
P_0007a9fa:
    .byte 0x12
    .org 0x7a9fb-ORIGIN
P_0007a9fb:
    .byte 0x0e
