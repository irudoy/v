! Complete natural auxiliary-gated rate caller and exact real unsigned divider and auxiliary gate.
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
    .org 0x68d58-ORIGIN
L_00068d58:
    sts.l pr,@-r15
    .org 0x68d5a-ORIGIN
L_00068d5a:
    sts.l macl,@-r15
    .org 0x68d5c-ORIGIN
L_00068d5c:
    stc.l gbr,@-r15
    .org 0x68d5e-ORIGIN
L_00068d5e:
    mov.l P_00068ec0,r0
    .org 0x68d60-ORIGIN
L_00068d60:
    ldc r0,gbr
    .org 0x68d62-ORIGIN
L_00068d62:
    add #-0x8,r15
    .org 0x68d64-ORIGIN
L_00068d64:
    mov.l P_00068ecc,r6
    .org 0x68d66-ORIGIN
L_00068d66:
    mov.b @r6,r0
    .org 0x68d68-ORIGIN
L_00068d68:
    tst #0x4,r0
    .org 0x68d6a-ORIGIN
L_00068d6a:
    bt L_00068ddc
    .org 0x68d6c-ORIGIN
L_00068d6c:
    mov.l P_00068ee0,r4
    .org 0x68d6e-ORIGIN
L_00068d6e:
    mov.b @(0x5,r4),r0
    .org 0x68d70-ORIGIN
L_00068d70:
    tst #0x1,r0
    .org 0x68d72-ORIGIN
L_00068d72:
    bt L_00068d82
    .org 0x68d74-ORIGIN
L_00068d74:
    mov #0x64,r2
    .org 0x68d76-ORIGIN
L_00068d76:
    mov.l P_00068ee4,r5
    .org 0x68d78-ORIGIN
L_00068d78:
    shll2 r2
    .org 0x68d7a-ORIGIN
L_00068d7a:
    mov #0x2c,r0
    .org 0x68d7c-ORIGIN
L_00068d7c:
    mov.w r2,@(r0,r5)
    .org 0x68d7e-ORIGIN
L_00068d7e:
    mov #0x0,r0
    .org 0x68d80-ORIGIN
L_00068d80:
    mov.w r0,@(0x24,gbr)
    .org 0x68d82-ORIGIN
L_00068d82:
    mov.l P_00068ee4,r5
    .org 0x68d84-ORIGIN
L_00068d84:
    mov #0x2c,r0
    .org 0x68d86-ORIGIN
L_00068d86:
    mov.w @(r0,r5),r6
    .org 0x68d88-ORIGIN
L_00068d88:
    extu.w r6,r6
    .org 0x68d8a-ORIGIN
L_00068d8a:
    tst r6,r6
    .org 0x68d8c-ORIGIN
L_00068d8c:
    bt L_00068dc4
    .org 0x68d8e-ORIGIN
L_00068d8e:
    mov.w @(0x24,gbr),r0
    .org 0x68d90-ORIGIN
L_00068d90:
    mov.l r0,@(0x4,r15)
    .org 0x68d92-ORIGIN
L_00068d92:
    mov.l r0,@r15
    .org 0x68d94-ORIGIN
L_00068d94:
    mov.w @(0x26,gbr),r0
    .org 0x68d96-ORIGIN
L_00068d96:
    extu.w r0,r5
    .org 0x68d98-ORIGIN
L_00068d98:
    mov.w P_00068e94,r0
    .org 0x68d9a-ORIGIN
L_00068d9a:
    mul.l r6,r5
    .org 0x68d9c-ORIGIN
L_00068d9c:
    mov.l P_00068ee8,r6
    .org 0x68d9e-ORIGIN
L_00068d9e:
    jsr @r6
    .org 0x68da0-ORIGIN
L_00068da0:
    sts macl,r1
    .org 0x68da2-ORIGIN
L_00068da2:
    mov r0,r6
    .org 0x68da4-ORIGIN
L_00068da4:
    mov.w @(0x26,gbr),r0
    .org 0x68da6-ORIGIN
L_00068da6:
    mov.l @r15,r2
    .org 0x68da8-ORIGIN
L_00068da8:
    extu.w r0,r5
    .org 0x68daa-ORIGIN
L_00068daa:
    add r2,r6
    .org 0x68dac-ORIGIN
L_00068dac:
    mov r5,r2
    .org 0x68dae-ORIGIN
L_00068dae:
    add #-0x7d,r2
    .org 0x68db0-ORIGIN
L_00068db0:
    cmp/gt r2,r6
    .org 0x68db2-ORIGIN
L_00068db2:
    bf L_00068db8
    .org 0x68db4-ORIGIN
L_00068db4:
    add #-0x7d,r5
    .org 0x68db6-ORIGIN
L_00068db6:
    mov r5,r6
    .org 0x68db8-ORIGIN
L_00068db8:
    mov #0x7d,r2
    .org 0x68dba-ORIGIN
L_00068dba:
    cmp/ge r2,r6
    .org 0x68dbc-ORIGIN
L_00068dbc:
    bt L_00068dc0
    .org 0x68dbe-ORIGIN
L_00068dbe:
    mov #0x7d,r6
    .org 0x68dc0-ORIGIN
L_00068dc0:
    bra L_00068dc6
    .org 0x68dc2-ORIGIN
L_00068dc2:
    mov r6,r0
    .org 0x68dc4-ORIGIN
L_00068dc4:
    mov #0x0,r0
    .org 0x68dc6-ORIGIN
L_00068dc6:
    mov.l P_00068eec,r2
    .org 0x68dc8-ORIGIN
L_00068dc8:
    jsr @r2
    .org 0x68dca-ORIGIN
L_00068dca:
    mov.w r0,@(0x2a,gbr)
    .org 0x68dcc-ORIGIN
L_00068dcc:
    tst r0,r0
    .org 0x68dce-ORIGIN
L_00068dce:
    bt L_00068ddc
    .org 0x68dd0-ORIGIN
L_00068dd0:
    mov.l P_00068ee0,r4
    .org 0x68dd2-ORIGIN
L_00068dd2:
    mov.b @(0x5,r4),r0
    .org 0x68dd4-ORIGIN
L_00068dd4:
    tst #0x1,r0
    .org 0x68dd6-ORIGIN
L_00068dd6:
    bf L_00068ddc
    .org 0x68dd8-ORIGIN
L_00068dd8:
    mov #0x0,r0
    .org 0x68dda-ORIGIN
L_00068dda:
    mov.w r0,@(0x2a,gbr)
    .org 0x68ddc-ORIGIN
L_00068ddc:
    add #0x8,r15
    .org 0x68dde-ORIGIN
L_00068dde:
    ldc.l @r15+,gbr
    .org 0x68de0-ORIGIN
L_00068de0:
    lds.l @r15+,macl
    .org 0x68de2-ORIGIN
L_00068de2:
    lds.l @r15+,pr
    .org 0x68de4-ORIGIN
L_00068de4:
    rts
    .org 0x68de6-ORIGIN
L_00068de6:
    nop
    .org 0x68e94-ORIGIN
P_00068e94:
    .byte 0x0f
    .org 0x68e95-ORIGIN
P_00068e95:
    .byte 0xa0
    .org 0x68ec0-ORIGIN
P_00068ec0:
    .byte 0xff
    .org 0x68ec1-ORIGIN
P_00068ec1:
    .byte 0xff
    .org 0x68ec2-ORIGIN
P_00068ec2:
    .byte 0x1f
    .org 0x68ec3-ORIGIN
P_00068ec3:
    .byte 0xf4
    .org 0x68ecc-ORIGIN
P_00068ecc:
    .byte 0xff
    .org 0x68ecd-ORIGIN
P_00068ecd:
    .byte 0xff
    .org 0x68ece-ORIGIN
P_00068ece:
    .byte 0x24
    .org 0x68ecf-ORIGIN
P_00068ecf:
    .byte 0xc0
    .org 0x68ee0-ORIGIN
P_00068ee0:
    .byte 0xff
    .org 0x68ee1-ORIGIN
P_00068ee1:
    .byte 0xff
    .org 0x68ee2-ORIGIN
P_00068ee2:
    .byte 0x42
    .org 0x68ee3-ORIGIN
P_00068ee3:
    .byte 0x4c
    .org 0x68ee4-ORIGIN
P_00068ee4:
    .byte 0xff
    .org 0x68ee5-ORIGIN
P_00068ee5:
    .byte 0xff
    .org 0x68ee6-ORIGIN
P_00068ee6:
    .byte 0x23
    .org 0x68ee7-ORIGIN
P_00068ee7:
    .byte 0x30
    .org 0x68ee8-ORIGIN
P_00068ee8:
    .byte 0x00
    .org 0x68ee9-ORIGIN
P_00068ee9:
    .byte 0x02
    .org 0x68eea-ORIGIN
P_00068eea:
    .byte 0x1c
    .org 0x68eeb-ORIGIN
P_00068eeb:
    .byte 0xe0
    .org 0x68eec-ORIGIN
P_00068eec:
    .byte 0x00
    .org 0x68eed-ORIGIN
P_00068eed:
    .byte 0x08
    .org 0x68eee-ORIGIN
P_00068eee:
    .byte 0xc3
    .org 0x68eef-ORIGIN
P_00068eef:
    .byte 0xfa
    .org 0x8c3fa-ORIGIN
L_0008c3fa:
    stc.l gbr,@-r15
    .org 0x8c3fc-ORIGIN
L_0008c3fc:
    mov.l P_0008c468,r0
    .org 0x8c3fe-ORIGIN
L_0008c3fe:
    ldc r0,gbr
    .org 0x8c400-ORIGIN
L_0008c400:
    add #-0x4,r15
    .org 0x8c402-ORIGIN
L_0008c402:
    mov.b @(0x0,gbr),r0
    .org 0x8c404-ORIGIN
L_0008c404:
    tst #0x40,r0
    .org 0x8c406-ORIGIN
L_0008c406:
    bf/s L_0008c43e
    .org 0x8c408-ORIGIN
L_0008c408:
    mov #0x0,r1
    .org 0x8c40a-ORIGIN
L_0008c40a:
    mov.l P_0008c46c,r6
    .org 0x8c40c-ORIGIN
L_0008c40c:
    mov.b @r6,r0
    .org 0x8c40e-ORIGIN
L_0008c40e:
    tst #0x20,r0
    .org 0x8c410-ORIGIN
L_0008c410:
    bt L_0008c43e
    .org 0x8c412-ORIGIN
L_0008c412:
    mov.b @(0x21,gbr),r0
    .org 0x8c414-ORIGIN
L_0008c414:
    mov #0x1,r6
    .org 0x8c416-ORIGIN
L_0008c416:
    tst #0x4,r0
    .org 0x8c418-ORIGIN
L_0008c418:
    bt/s L_0008c43c
    .org 0x8c41a-ORIGIN
L_0008c41a:
    mov.l r6,@r15
    .org 0x8c41c-ORIGIN
L_0008c41c:
    mov.b @(0x39,gbr),r0
    .org 0x8c41e-ORIGIN
L_0008c41e:
    tst #0x1,r0
    .org 0x8c420-ORIGIN
L_0008c420:
    bf L_0008c43c
    .org 0x8c422-ORIGIN
L_0008c422:
    mov.l P_0008c464,r5
    .org 0x8c424-ORIGIN
L_0008c424:
    mov #0x14,r4
    .org 0x8c426-ORIGIN
L_0008c426:
    mov.w P_0008c44a,r0
    .org 0x8c428-ORIGIN
L_0008c428:
    mov.w @(r0,r5),r2
    .org 0x8c42a-ORIGIN
L_0008c42a:
    cmp/hs r4,r2
    .org 0x8c42c-ORIGIN
L_0008c42c:
    bt L_0008c43c
    .org 0x8c42e-ORIGIN
L_0008c42e:
    mov.w P_0008c44c,r0
    .org 0x8c430-ORIGIN
L_0008c430:
    mov.w @(r0,r5),r2
    .org 0x8c432-ORIGIN
L_0008c432:
    extu.w r2,r2
    .org 0x8c434-ORIGIN
L_0008c434:
    cmp/ge r4,r2
    .org 0x8c436-ORIGIN
L_0008c436:
    bt L_0008c43c
    .org 0x8c438-ORIGIN
L_0008c438:
    mov #0x0,r6
    .org 0x8c43a-ORIGIN
L_0008c43a:
    mov.l r6,@r15
    .org 0x8c43c-ORIGIN
L_0008c43c:
    mov.l @r15,r1
    .org 0x8c43e-ORIGIN
L_0008c43e:
    extu.b r1,r0
    .org 0x8c440-ORIGIN
L_0008c440:
    add #0x4,r15
    .org 0x8c442-ORIGIN
L_0008c442:
    rts
    .org 0x8c444-ORIGIN
L_0008c444:
    ldc.l @r15+,gbr
    .org 0x8c44a-ORIGIN
P_0008c44a:
    .byte 0x0b
    .org 0x8c44b-ORIGIN
P_0008c44b:
    .byte 0xec
    .org 0x8c44c-ORIGIN
P_0008c44c:
    .byte 0x0b
    .org 0x8c44d-ORIGIN
P_0008c44d:
    .byte 0xee
    .org 0x8c464-ORIGIN
P_0008c464:
    .byte 0xff
    .org 0x8c465-ORIGIN
P_0008c465:
    .byte 0xff
    .org 0x8c466-ORIGIN
P_0008c466:
    .byte 0x28
    .org 0x8c467-ORIGIN
P_0008c467:
    .byte 0xf8
    .org 0x8c468-ORIGIN
P_0008c468:
    .byte 0xff
    .org 0x8c469-ORIGIN
P_0008c469:
    .byte 0xff
    .org 0x8c46a-ORIGIN
P_0008c46a:
    .byte 0x41
    .org 0x8c46b-ORIGIN
P_0008c46b:
    .byte 0x84
    .org 0x8c46c-ORIGIN
P_0008c46c:
    .byte 0xff
    .org 0x8c46d-ORIGIN
P_0008c46d:
    .byte 0xff
    .org 0x8c46e-ORIGIN
P_0008c46e:
    .byte 0x24
    .org 0x8c46f-ORIGIN
P_0008c46f:
    .byte 0x4f
