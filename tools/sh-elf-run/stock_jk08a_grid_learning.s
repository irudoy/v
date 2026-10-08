! Complete bank learner with real absolute value, grid fill and auxiliary maintenance.
    .section .text
    .org 0x839c-0x839c
P_839c: .byte 0x6e,0x5a
    .org 0x88f5-0x839c
P_88f5: .byte 0x00
    .org 0x8a9d-0x839c
P_8a9d: .byte 0x1a,0x5a,0x6e
    .org 0x129c6-0x839c
P_129c6: .byte 0x1a,0x1a,0x10,0x08
    .org 0x22590-0x839c
L_22590:
    cmp/pl r4
    .org 0x22592-0x839c
L_22592:
    bt L_22596
    .org 0x22594-0x839c
L_22594:
    neg r4,r4
    .org 0x22596-0x839c
L_22596:
    rts
    .org 0x22598-0x839c
L_22598:
    mov r4,r0
    .org 0x57d1e-0x839c
L_57d1e:
    mov.l r8,@-r15
    .org 0x57d20-0x839c
L_57d20:
    mov.l r9,@-r15
    .org 0x57d22-0x839c
L_57d22:
    mov.l r10,@-r15
    .org 0x57d24-0x839c
L_57d24:
    mov.l r11,@-r15
    .org 0x57d26-0x839c
L_57d26:
    mov.l r12,@-r15
    .org 0x57d28-0x839c
L_57d28:
    mov.l r13,@-r15
    .org 0x57d2a-0x839c
L_57d2a:
    mov.l r14,@-r15
    .org 0x57d2c-0x839c
L_57d2c:
    sts.l pr,@-r15
    .org 0x57d2e-0x839c
L_57d2e:
    sts.l macl,@-r15
    .org 0x57d30-0x839c
L_57d30:
    add #-0x14,r15
    .org 0x57d32-0x839c
L_57d32:
    mov.l P_57e68,r5
    .org 0x57d34-0x839c
L_57d34:
    mov #0x73,r0
    .org 0x57d36-0x839c
L_57d36:
    shll2 r0
    .org 0x57d38-0x839c
L_57d38:
    mov.b @(r0,r5),r2
    .org 0x57d3a-0x839c
L_57d3a:
    extu.b r4,r11
    .org 0x57d3c-0x839c
L_57d3c:
    mov r11,r6
    .org 0x57d3e-0x839c
L_57d3e:
    add #0x1,r6
    .org 0x57d40-0x839c
L_57d40:
    extu.b r2,r2
    .org 0x57d42-0x839c
L_57d42:
    tst r6,r2
    .org 0x57d44-0x839c
L_57d44:
    bf L_57d4a
    .org 0x57d46-0x839c
L_57d46:
    bra L_57ed8
    .org 0x57d48-0x839c
L_57d48:
    nop
    .org 0x57d4a-0x839c
L_57d4a:
    mov.w P_57e30,r0
    .org 0x57d4c-0x839c
L_57d4c:
    mov.b @(r0,r5),r2
    .org 0x57d4e-0x839c
L_57d4e:
    extu.b r2,r2
    .org 0x57d50-0x839c
L_57d50:
    tst r6,r2
    .org 0x57d52-0x839c
L_57d52:
    bf L_57d58
    .org 0x57d54-0x839c
L_57d54:
    bra L_57ed8
    .org 0x57d56-0x839c
L_57d56:
    nop
    .org 0x57d58-0x839c
L_57d58:
    tst r11,r11
    .org 0x57d5a-0x839c
L_57d5a:
    mov.l P_57e78,r2
    .org 0x57d5c-0x839c
L_57d5c:
    bf L_57d60
    .org 0x57d5e-0x839c
L_57d5e:
    mov.l P_57e7c,r2
    .org 0x57d60-0x839c
L_57d60:
    mov.l P_57e74,r12
    .org 0x57d62-0x839c
L_57d62:
    mov #0x0,r13
    .org 0x57d64-0x839c
L_57d64:
    mov.l r2,@r15
    .org 0x57d66-0x839c
L_57d66:
    mov r11,r2
    .org 0x57d68-0x839c
L_57d68:
    shll r2
    .org 0x57d6a-0x839c
L_57d6a:
    mov r13,r0
    .org 0x57d6c-0x839c
L_57d6c:
    mov #-0x64,r9
    .org 0x57d6e-0x839c
L_57d6e:
    mov.b r0,@(0x4,r15)
    .org 0x57d70-0x839c
L_57d70:
    add r2,r12
    .org 0x57d72-0x839c
L_57d72:
    mov.l r2,@(0x8,r15)
    .org 0x57d74-0x839c
L_57d74:
    shll8 r9
    .org 0x57d76-0x839c
L_57d76:
    mov.l P_57e80,r8
    .org 0x57d78-0x839c
L_57d78:
    mov.l P_57e84,r10
    .org 0x57d7a-0x839c
L_57d7a:
    mov.w @r12,r2
    .org 0x57d7c-0x839c
L_57d7c:
    extu.b r13,r13
    .org 0x57d7e-0x839c
L_57d7e:
    mov r13,r0
    .org 0x57d80-0x839c
L_57d80:
    extu.w r2,r4
    .org 0x57d82-0x839c
L_57d82:
    mov.b @(r0,r8),r2
    .org 0x57d84-0x839c
L_57d84:
    add r9,r4
    .org 0x57d86-0x839c
L_57d86:
    jsr @r10
    .org 0x57d88-0x839c
L_57d88:
    extu.b r2,r14
    .org 0x57d8a-0x839c
L_57d8a:
    shll8 r14
    .org 0x57d8c-0x839c
L_57d8c:
    cmp/gt r14,r0
    .org 0x57d8e-0x839c
L_57d8e:
    bf L_57d9e
    .org 0x57d90-0x839c
L_57d90:
    add #0x1,r13
    .org 0x57d92-0x839c
L_57d92:
    mov r13,r0
    .org 0x57d94-0x839c
L_57d94:
    extu.b r13,r13
    .org 0x57d96-0x839c
L_57d96:
    mov #0x3,r6
    .org 0x57d98-0x839c
L_57d98:
    cmp/ge r6,r13
    .org 0x57d9a-0x839c
L_57d9a:
    bf/s L_57d7a
    .org 0x57d9c-0x839c
L_57d9c:
    mov.b r0,@(0x4,r15)
    .org 0x57d9e-0x839c
L_57d9e:
    mov.l P_57e88,r2
    .org 0x57da0-0x839c
L_57da0:
    extu.b r13,r0
    .org 0x57da2-0x839c
L_57da2:
    mov.l @r15,r5
    .org 0x57da4-0x839c
L_57da4:
    mov.b @(r0,r2),r6
    .org 0x57da6-0x839c
L_57da6:
    mov.l P_57e8c,r2
    .org 0x57da8-0x839c
L_57da8:
    mov r6,r0
    .org 0x57daa-0x839c
L_57daa:
    mov.b r0,@(0xc,r15)
    .org 0x57dac-0x839c
L_57dac:
    mov r11,r0
    .org 0x57dae-0x839c
L_57dae:
    mov.b @(r0,r2),r7
    .org 0x57db0-0x839c
L_57db0:
    extu.b r7,r7
    .org 0x57db2-0x839c
L_57db2:
    mov r7,r0
    .org 0x57db4-0x839c
L_57db4:
    mov.b @(r0,r5),r2
    .org 0x57db6-0x839c
L_57db6:
    tst r2,r2
    .org 0x57db8-0x839c
L_57db8:
    bf L_57dc2
    .org 0x57dba-0x839c
L_57dba:
    mov.l P_57e90,r6
    .org 0x57dbc-0x839c
L_57dbc:
    mov.b @r6,r6
    .org 0x57dbe-0x839c
L_57dbe:
    mov r6,r0
    .org 0x57dc0-0x839c
L_57dc0:
    mov.b r0,@(0xc,r15)
    .org 0x57dc2-0x839c
L_57dc2:
    mov.l @(0x8,r15),r0
    .org 0x57dc4-0x839c
L_57dc4:
    extu.b r6,r6
    .org 0x57dc6-0x839c
L_57dc6:
    mov.l P_57e74,r4
    .org 0x57dc8-0x839c
L_57dc8:
    mov.w @(r0,r4),r5
    .org 0x57dca-0x839c
L_57dca:
    extu.w r5,r5
    .org 0x57dcc-0x839c
L_57dcc:
    mov r5,r2
    .org 0x57dce-0x839c
L_57dce:
    add r9,r2
    .org 0x57dd0-0x839c
L_57dd0:
    mul.l r6,r2
    .org 0x57dd2-0x839c
L_57dd2:
    sts macl,r2
    .org 0x57dd4-0x839c
L_57dd4:
    cmp/pz r2
    .org 0x57dd6-0x839c
L_57dd6:
    bt L_57dde
    .org 0x57dd8-0x839c
L_57dd8:
    mov #-0x1,r6
    .org 0x57dda-0x839c
L_57dda:
    extu.b r6,r6
    .org 0x57ddc-0x839c
L_57ddc:
    add r6,r2
    .org 0x57dde-0x839c
L_57dde:
    mov r2,r6
    .org 0x57de0-0x839c
L_57de0:
    shlr8 r6
    .org 0x57de2-0x839c
L_57de2:
    swap.w r6,r2
    .org 0x57de4-0x839c
L_57de4:
    mov.l P_57e94,r4
    .org 0x57de6-0x839c
L_57de6:
    mov.l @(0x8,r15),r0
    .org 0x57de8-0x839c
L_57de8:
    exts.b r2,r6
    .org 0x57dea-0x839c
L_57dea:
    xtrct r6,r2
    .org 0x57dec-0x839c
L_57dec:
    mov.w @(r0,r4),r6
    .org 0x57dee-0x839c
L_57dee:
    mov #0x64,r4
    .org 0x57df0-0x839c
L_57df0:
    shll8 r4
    .org 0x57df2-0x839c
L_57df2:
    extu.w r6,r6
    .org 0x57df4-0x839c
L_57df4:
    cmp/eq r4,r6
    .org 0x57df6-0x839c
L_57df6:
    bt/s L_57e0a
    .org 0x57df8-0x839c
L_57df8:
    mov.l r2,@(0x10,r15)
    .org 0x57dfa-0x839c
L_57dfa:
    tst r2,r2
    .org 0x57dfc-0x839c
L_57dfc:
    bf L_57e0a
    .org 0x57dfe-0x839c
L_57dfe:
    mov #0x1,r2
    .org 0x57e00-0x839c
L_57e00:
    cmp/ge r4,r5
    .org 0x57e02-0x839c
L_57e02:
    bt/s L_57e0a
    .org 0x57e04-0x839c
L_57e04:
    mov.l r2,@(0x10,r15)
    .org 0x57e06-0x839c
L_57e06:
    mov #-0x1,r2
    .org 0x57e08-0x839c
L_57e08:
    mov.l r2,@(0x10,r15)
    .org 0x57e0a-0x839c
L_57e0a:
    mov.l P_57e98,r5
    .org 0x57e0c-0x839c
L_57e0c:
    mov.l @(0x8,r15),r0
    .org 0x57e0e-0x839c
L_57e0e:
    mov.w @(r0,r5),r6
    .org 0x57e10-0x839c
L_57e10:
    extu.w r6,r5
    .org 0x57e12-0x839c
L_57e12:
    add r2,r5
    .org 0x57e14-0x839c
L_57e14:
    mov.l P_57e9c,r2
    .org 0x57e16-0x839c
L_57e16:
    mov.b @r2,r6
    .org 0x57e18-0x839c
L_57e18:
    extu.b r6,r6
    .org 0x57e1a-0x839c
L_57e1a:
    mov r6,r2
    .org 0x57e1c-0x839c
L_57e1c:
    shll8 r2
    .org 0x57e1e-0x839c
L_57e1e:
    cmp/gt r2,r5
    .org 0x57e20-0x839c
L_57e20:
    bf L_57e26
    .org 0x57e22-0x839c
L_57e22:
    shll8 r6
    .org 0x57e24-0x839c
L_57e24:
    mov r6,r5
    .org 0x57e26-0x839c
L_57e26:
    mov.l P_57ea0,r2
    .org 0x57e28-0x839c
L_57e28:
    mov.b @r2,r6
    .org 0x57e2a-0x839c
L_57e2a:
    extu.b r6,r6
    .org 0x57e2c-0x839c
L_57e2c:
    bra L_57ea4
    .org 0x57e2e-0x839c
L_57e2e:
    mov r6,r2
    .org 0x57e30-0x839c
P_57e30: .word 0x01cb
    .org 0x57e68-0x839c
P_57e68: .long 0xffff128c
    .org 0x57e74-0x839c
P_57e74: .long 0xffff134e
    .org 0x57e78-0x839c
P_57e78: .long 0xffff49b0
    .org 0x57e7c-0x839c
P_57e7c: .long 0xffff49f0
    .org 0x57e80-0x839c
P_57e80: .long 0xffff2c21
    .org 0x57e84-0x839c
P_57e84: .long 0x00022590
    .org 0x57e88-0x839c
P_57e88: .long 0x000129c6
    .org 0x57e8c-0x839c
P_57e8c: .long 0xffff130a
    .org 0x57e90-0x839c
P_57e90: .long 0x00008a9d
    .org 0x57e94-0x839c
P_57e94: .long 0xffff22dc
    .org 0x57e98-0x839c
P_57e98: .long 0xffff2306
    .org 0x57e9c-0x839c
P_57e9c: .long 0x00008a9f
    .org 0x57ea0-0x839c
P_57ea0: .long 0x00008a9e
    .org 0x57ea4-0x839c
L_57ea4:
    shll8 r2
    .org 0x57ea6-0x839c
L_57ea6:
    cmp/ge r2,r5
    .org 0x57ea8-0x839c
L_57ea8:
    bt L_57eb0
    .org 0x57eaa-0x839c
L_57eaa:
    mov r6,r2
    .org 0x57eac-0x839c
L_57eac:
    bra L_57eb2
    .org 0x57eae-0x839c
L_57eae:
    shll8 r2
    .org 0x57eb0-0x839c
L_57eb0:
    mov r5,r2
    .org 0x57eb2-0x839c
L_57eb2:
    tst r11,r11
    .org 0x57eb4-0x839c
L_57eb4:
    bf/s L_57ec4
    .org 0x57eb6-0x839c
L_57eb6:
    mov r2,r5
    .org 0x57eb8-0x839c
L_57eb8:
    mov.l P_580c4,r4
    .org 0x57eba-0x839c
L_57eba:
    bsr L_58092
    .org 0x57ebc-0x839c
L_57ebc:
    mov r7,r6
    .org 0x57ebe-0x839c
L_57ebe:
    mov.l P_580c8,r4
    .org 0x57ec0-0x839c
L_57ec0:
    bra L_57ece
    .org 0x57ec2-0x839c
L_57ec2:
    mov r11,r6
    .org 0x57ec4-0x839c
L_57ec4:
    mov.l P_580cc,r4
    .org 0x57ec6-0x839c
L_57ec6:
    bsr L_58092
    .org 0x57ec8-0x839c
L_57ec8:
    mov r7,r6
    .org 0x57eca-0x839c
L_57eca:
    mov r11,r6
    .org 0x57ecc-0x839c
L_57ecc:
    mov.l P_580d0,r4
    .org 0x57ece-0x839c
L_57ece:
    mov.l P_580d4,r2
    .org 0x57ed0-0x839c
L_57ed0:
    mov r6,r0
    .org 0x57ed2-0x839c
L_57ed2:
    mov.b @(r0,r2),r5
    .org 0x57ed4-0x839c
L_57ed4:
    bsr L_580e8
    .org 0x57ed6-0x839c
L_57ed6:
    extu.b r5,r5
    .org 0x57ed8-0x839c
L_57ed8:
    add #0x14,r15
    .org 0x57eda-0x839c
L_57eda:
    lds.l @r15+,macl
    .org 0x57edc-0x839c
L_57edc:
    lds.l @r15+,pr
    .org 0x57ede-0x839c
L_57ede:
    mov.l @r15+,r14
    .org 0x57ee0-0x839c
L_57ee0:
    mov.l @r15+,r13
    .org 0x57ee2-0x839c
L_57ee2:
    mov.l @r15+,r12
    .org 0x57ee4-0x839c
L_57ee4:
    mov.l @r15+,r11
    .org 0x57ee6-0x839c
L_57ee6:
    mov.l @r15+,r10
    .org 0x57ee8-0x839c
L_57ee8:
    mov.l @r15+,r9
    .org 0x57eea-0x839c
L_57eea:
    rts
    .org 0x57eec-0x839c
L_57eec:
    mov.l @r15+,r8
    .org 0x58092-0x839c
L_58092:
    mov #-0x1,r3
    .org 0x58094-0x839c
L_58094:
    extu.b r6,r6
    .org 0x58096-0x839c
L_58096:
    extu.b r3,r3
    .org 0x58098-0x839c
L_58098:
    cmp/eq r3,r6
    .org 0x5809a-0x839c
L_5809a:
    bf/s L_580a4
    .org 0x5809c-0x839c
L_5809c:
    mov r5,r7
    .org 0x5809e-0x839c
L_5809e:
    mov #0x3f,r5
    .org 0x580a0-0x839c
L_580a0:
    bra L_580a6
    .org 0x580a2-0x839c
L_580a2:
    mov #0x0,r6
    .org 0x580a4-0x839c
L_580a4:
    mov r6,r5
    .org 0x580a6-0x839c
L_580a6:
    extu.b r5,r5
    .org 0x580a8-0x839c
L_580a8:
    extu.b r6,r6
    .org 0x580aa-0x839c
L_580aa:
    cmp/gt r5,r6
    .org 0x580ac-0x839c
L_580ac:
    bt L_580be
    .org 0x580ae-0x839c
L_580ae:
    extu.b r6,r6
    .org 0x580b0-0x839c
L_580b0:
    mov r6,r0
    .org 0x580b2-0x839c
L_580b2:
    add #0x1,r6
    .org 0x580b4-0x839c
L_580b4:
    extu.b r6,r6
    .org 0x580b6-0x839c
L_580b6:
    shll r0
    .org 0x580b8-0x839c
L_580b8:
    cmp/gt r5,r6
    .org 0x580ba-0x839c
L_580ba:
    bf/s L_580ae
    .org 0x580bc-0x839c
L_580bc:
    mov.w r7,@(r0,r4)
    .org 0x580be-0x839c
L_580be:
    rts
    .org 0x580c0-0x839c
L_580c0:
    nop
    .org 0x580c4-0x839c
P_580c4: .long 0xffff4b90
    .org 0x580c8-0x839c
P_580c8: .long 0xffff49f0
    .org 0x580cc-0x839c
P_580cc: .long 0xffff4b10
    .org 0x580d0-0x839c
P_580d0: .long 0xffff49b0
    .org 0x580d4-0x839c
P_580d4: .long 0xffff130a
    .org 0x580e8-0x839c
L_580e8:
    mov.l r14,@-r15
    .org 0x580ea-0x839c
L_580ea:
    mov r6,r2
    .org 0x580ec-0x839c
L_580ec:
    mov #-0x1,r6
    .org 0x580ee-0x839c
L_580ee:
    extu.b r5,r1
    .org 0x580f0-0x839c
L_580f0:
    extu.b r6,r6
    .org 0x580f2-0x839c
L_580f2:
    cmp/eq r6,r1
    .org 0x580f4-0x839c
L_580f4:
    bf/s L_5810e
    .org 0x580f6-0x839c
L_580f6:
    mov r4,r14
    .org 0x580f8-0x839c
L_580f8:
    mov #0x0,r2
    .org 0x580fa-0x839c
L_580fa:
    mov r2,r5
    .org 0x580fc-0x839c
L_580fc:
    mov #0x40,r6
    .org 0x580fe-0x839c
L_580fe:
    extu.b r2,r0
    .org 0x58100-0x839c
L_58100:
    mov.b r5,@(r0,r14)
    .org 0x58102-0x839c
L_58102:
    add #0x1,r0
    .org 0x58104-0x839c
L_58104:
    extu.b r0,r2
    .org 0x58106-0x839c
L_58106:
    cmp/ge r6,r2
    .org 0x58108-0x839c
L_58108:
    bf L_580fe
    .org 0x5810a-0x839c
L_5810a:
    bra L_58164
    .org 0x5810c-0x839c
L_5810c:
    nop
    .org 0x5810e-0x839c
L_5810e:
    mov r1,r0
    .org 0x58110-0x839c
L_58110:
    mov.b @(r0,r14),r4
    .org 0x58112-0x839c
L_58112:
    mov.l P_58344,r5
    .org 0x58114-0x839c
L_58114:
    add #0x1,r4
    .org 0x58116-0x839c
L_58116:
    extu.b r4,r4
    .org 0x58118-0x839c
L_58118:
    mov.b r4,@(r0,r14)
    .org 0x5811a-0x839c
L_5811a:
    mov r4,r6
    .org 0x5811c-0x839c
L_5811c:
    mov.b @r5,r7
    .org 0x5811e-0x839c
L_5811e:
    mov #-0x1,r5
    .org 0x58120-0x839c
L_58120:
    extu.b r5,r5
    .org 0x58122-0x839c
L_58122:
    extu.b r7,r7
    .org 0x58124-0x839c
L_58124:
    add r7,r6
    .org 0x58126-0x839c
L_58126:
    cmp/gt r5,r6
    .org 0x58128-0x839c
L_58128:
    bf L_5813a
    .org 0x5812a-0x839c
L_5812a:
    cmp/ge r7,r4
    .org 0x5812c-0x839c
L_5812c:
    bt L_58132
    .org 0x5812e-0x839c
L_5812e:
    bra L_58136
    .org 0x58130-0x839c
L_58130:
    mov #0x0,r6
    .org 0x58132-0x839c
L_58132:
    sub r7,r4
    .org 0x58134-0x839c
L_58134:
    mov r4,r6
    .org 0x58136-0x839c
L_58136:
    mov r1,r0
    .org 0x58138-0x839c
L_58138:
    mov.b r6,@(r0,r14)
    .org 0x5813a-0x839c
L_5813a:
    mov.l P_58348,r5
    .org 0x5813c-0x839c
L_5813c:
    extu.b r2,r0
    .org 0x5813e-0x839c
L_5813e:
    shll r0
    .org 0x58140-0x839c
L_58140:
    mov.w @(r0,r5),r2
    .org 0x58142-0x839c
L_58142:
    mov.l P_5834c,r5
    .org 0x58144-0x839c
L_58144:
    extu.w r2,r2
    .org 0x58146-0x839c
L_58146:
    mov.b @r5,r6
    .org 0x58148-0x839c
L_58148:
    extu.b r6,r6
    .org 0x5814a-0x839c
L_5814a:
    shll8 r6
    .org 0x5814c-0x839c
L_5814c:
    cmp/ge r6,r2
    .org 0x5814e-0x839c
L_5814e:
    bt L_5815e
    .org 0x58150-0x839c
L_58150:
    mov.l P_58350,r5
    .org 0x58152-0x839c
L_58152:
    mov r2,r6
    .org 0x58154-0x839c
L_58154:
    mov.b @r5,r2
    .org 0x58156-0x839c
L_58156:
    extu.b r2,r5
    .org 0x58158-0x839c
L_58158:
    shll8 r5
    .org 0x5815a-0x839c
L_5815a:
    cmp/ge r5,r6
    .org 0x5815c-0x839c
L_5815c:
    bt L_58164
    .org 0x5815e-0x839c
L_5815e:
    mov #0x0,r5
    .org 0x58160-0x839c
L_58160:
    mov r1,r0
    .org 0x58162-0x839c
L_58162:
    mov.b r5,@(r0,r14)
    .org 0x58164-0x839c
L_58164:
    rts
    .org 0x58166-0x839c
L_58166:
    mov.l @r15+,r14
    .org 0x58344-0x839c
P_58344: .long 0x000088f5
    .org 0x58348-0x839c
P_58348: .long 0xffff134e
    .org 0x5834c-0x839c
P_5834c: .long 0x0000839c
    .org 0x58350-0x839c
P_58350: .long 0x0000839d
