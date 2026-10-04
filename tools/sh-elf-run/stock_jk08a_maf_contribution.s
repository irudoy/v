! JK08A per-bank MAF contribution and signed divide-by-64 helper.
! All instruction addresses and stock pools retain their ROM positions.
    .section .text
    .balign 4
    .org 0x2
P_000082b6:
    .byte 0x4d
P_000082b7:
    .byte 0x0c
P_000082b8:
    .byte 0xff
    .org 0x9
P_000082bd:
    .byte 0x2d
    .org 0x80f
P_00008ac3:
    .byte 0x80
    .org 0x1a246
L_000224fa:
    shar r0
L_000224fc:
    shar r0
L_000224fe:
    shar r0
L_00022500:
    shar r0
L_00022502:
    shar r0
L_00022504:
    rts
L_00022506:
    shar r0
    .org 0x32c8e
L_0003af42:
    mov.l r13,@-r15
L_0003af44:
    mov.l r14,@-r15
L_0003af46:
    sts.l pr,@-r15
L_0003af48:
    sts.l macl,@-r15
L_0003af4a:
    stc.l gbr,@-r15
L_0003af4c:
    mov.l P_0003b10c,r0
L_0003af4e:
    ldc r0,gbr
L_0003af50:
    add #-0x1c,r15
L_0003af52:
    mov.l P_0003b110,r2
L_0003af54:
    extu.b r4,r7
L_0003af56:
    mov r7,r13
L_0003af58:
    shll r13
L_0003af5a:
    mov.b @(0x1,r2),r0
L_0003af5c:
    mov r7,r14
L_0003af5e:
    stc gbr,r2
L_0003af60:
    and #0x80,r0
L_0003af62:
    add #0x4,r2
L_0003af64:
    mov r0,r6
L_0003af66:
    mov r13,r0
L_0003af68:
    mov.w @(r0,r2),r5
L_0003af6a:
    tst r6,r6
L_0003af6c:
    shll2 r14
L_0003af6e:
    bf/s L_0003af7a
L_0003af70:
    extu.w r5,r5
L_0003af72:
    mov.l P_0003b114,r4
L_0003af74:
    mov.b @(0x4,r4),r0
L_0003af76:
    tst #0x8,r0
L_0003af78:
    bt L_0003af84
L_0003af7a:
    mov.l P_0003b118,r2
L_0003af7c:
    mov #0x3,r4
L_0003af7e:
    mov r7,r0
L_0003af80:
    add #0x3,r2
L_0003af82:
    mov.b r4,@(r0,r2)
L_0003af84:
    mov.l P_0003b11c,r4
L_0003af86:
    mov.b @(0x2,r4),r0
L_0003af88:
    tst #0x1,r0
L_0003af8a:
    bf L_0003af90
L_0003af8c:
    bra L_0003b1c4
L_0003af8e:
    nop
L_0003af90:
    tst r6,r6
L_0003af92:
    bt L_0003af98
L_0003af94:
    bra L_0003b1c4
L_0003af96:
    nop
L_0003af98:
    mov.l P_0003b114,r6
L_0003af9a:
    mov.b @(0x4,r6),r0
L_0003af9c:
    tst #0x8,r0
L_0003af9e:
    bt L_0003afa4
L_0003afa0:
    bra L_0003b1c4
L_0003afa2:
    nop
L_0003afa4:
    mov.l P_0003b118,r2
L_0003afa6:
    mov r7,r0
L_0003afa8:
    add #0x3,r2
L_0003afaa:
    mov.b @(r0,r2),r6
L_0003afac:
    tst r6,r6
L_0003afae:
    bt L_0003afb4
L_0003afb0:
    bra L_0003b1c4
L_0003afb2:
    nop
L_0003afb4:
    stc gbr,r2
L_0003afb6:
    mov r5,r6
L_0003afb8:
    add #0x1c,r2
L_0003afba:
    mov.l P_0003b120,r5
L_0003afbc:
    mov r13,r0
L_0003afbe:
    mov.w @(r0,r2),r4
L_0003afc0:
    mov.b @(0x7,r5),r0
L_0003afc2:
    extu.w r4,r4
L_0003afc4:
    sub r4,r6
L_0003afc6:
    extu.b r0,r2
L_0003afc8:
    mov r13,r0
L_0003afca:
    mul.l r6,r2
L_0003afcc:
    stc gbr,r5
L_0003afce:
    sts macl,r2
L_0003afd0:
    mov r7,r6
L_0003afd2:
    add #0x1,r6
L_0003afd4:
    add #0x44,r5
L_0003afd6:
    mov.b r6,@r15
L_0003afd8:
    mov.w @(r0,r5),r6
L_0003afda:
    cmp/pz r2
L_0003afdc:
    bt/s L_0003afe8
L_0003afde:
    extu.w r6,r6
L_0003afe0:
    mov r2,r0
L_0003afe2:
    tst #0x7,r0
L_0003afe4:
    bt L_0003afe8
L_0003afe6:
    add #0x8,r2
L_0003afe8:
    shar r2
L_0003afea:
    mov.b @(0x48,gbr),r0
L_0003afec:
    shar r2
L_0003afee:
    shar r2
L_0003aff0:
    extu.b r0,r5
L_0003aff2:
    add #0x1,r7
L_0003aff4:
    add r4,r2
L_0003aff6:
    tst r7,r5
L_0003aff8:
    bt/s L_0003b000
L_0003affa:
    mov r2,r4
L_0003affc:
    bra L_0003b004
L_0003affe:
    mov.l r6,@(0x4,r15)
L_0003b000:
    neg r6,r2
L_0003b002:
    mov.l r2,@(0x4,r15)
L_0003b004:
    cmp/pz r4
L_0003b006:
    bt L_0003b01e
L_0003b008:
    stc gbr,r2
L_0003b00a:
    add #0x14,r2
L_0003b00c:
    mov r13,r0
L_0003b00e:
    mov #0x0,r6
L_0003b010:
    mov.w r6,@(r0,r2)
L_0003b012:
    mov r6,r0
L_0003b014:
    mov.l @(0x4,r15),r2
L_0003b016:
    mov.w r0,@(0x8,r15)
L_0003b018:
    add r4,r2
L_0003b01a:
    bra L_0003b042
L_0003b01c:
    mov.l r2,@(0x4,r15)
L_0003b01e:
    mov #-0x1,r2
L_0003b020:
    extu.w r2,r2
L_0003b022:
    cmp/gt r2,r4
L_0003b024:
    bt L_0003b028
L_0003b026:
    mov r4,r2
L_0003b028:
    stc gbr,r6
L_0003b02a:
    add #0x14,r6
L_0003b02c:
    mov r13,r0
L_0003b02e:
    mov.w r2,@(r0,r6)
L_0003b030:
    mov r2,r0
L_0003b032:
    extu.w r2,r2
L_0003b034:
    sub r2,r4
L_0003b036:
    cmp/pl r4
L_0003b038:
    bf/s L_0003b042
L_0003b03a:
    mov.w r0,@(0x8,r15)
L_0003b03c:
    mov.l @(0x4,r15),r2
L_0003b03e:
    add r4,r2
L_0003b040:
    mov.l r2,@(0x4,r15)
L_0003b042:
    mov.l @(0x4,r15),r2
L_0003b044:
    cmp/pz r2
L_0003b046:
    bt L_0003b05e
L_0003b048:
    mov.b @r15,r6
L_0003b04a:
    mov.b @(0x48,gbr),r0
L_0003b04c:
    not r6,r2
L_0003b04e:
    mov.l @(0x4,r15),r6
L_0003b050:
    and r2,r0
L_0003b052:
    mov.l P_0003b124,r2
L_0003b054:
    cmp/ge r2,r6
L_0003b056:
    bf/s L_0003b072
L_0003b058:
    mov.b r0,@(0x48,gbr)
L_0003b05a:
    bra L_0003b072
L_0003b05c:
    mov.l @(0x4,r15),r2
L_0003b05e:
    mov.b @r15,r3
L_0003b060:
    mov.b @(0x48,gbr),r0
L_0003b062:
    mov.l @(0x4,r15),r6
L_0003b064:
    mov.l P_0003b128,r2
L_0003b066:
    mov.l r0,@(0x10,r15)
L_0003b068:
    or r3,r0
L_0003b06a:
    cmp/gt r2,r6
L_0003b06c:
    bt/s L_0003b072
L_0003b06e:
    mov.b r0,@(0x48,gbr)
L_0003b070:
    mov.l @(0x4,r15),r2
L_0003b072:
    stc gbr,r6
L_0003b074:
    mov.w @(0x8,r15),r0
L_0003b076:
    add #0x2c,r6
L_0003b078:
    mov.l P_0003b120,r3
L_0003b07a:
    mov.l r2,@(0x4,r15)
L_0003b07c:
    extu.w r0,r5
L_0003b07e:
    mov r13,r0
L_0003b080:
    mov.w @(r0,r6),r2
L_0003b082:
    mov.b @(0x1,r3),r0
L_0003b084:
    extu.w r2,r2
L_0003b086:
    sub r2,r5
L_0003b088:
    extu.b r0,r2
L_0003b08a:
    mul.l r5,r2
L_0003b08c:
    sts macl,r2
L_0003b08e:
    cmp/pz r2
L_0003b090:
    bt L_0003b0a2
L_0003b092:
    mov.w P_0003b098,r6
L_0003b094:
    bra L_0003b09a
L_0003b096:
    tst r6,r2
P_0003b098:
    .byte 0x01
P_0003b099:
    .byte 0xff
L_0003b09a:
    bt L_0003b0a2
L_0003b09c:
    mov #0x2,r6
L_0003b09e:
    shll8 r6
L_0003b0a0:
    add r6,r2
L_0003b0a2:
    mov r2,r6
L_0003b0a4:
    shlr8 r6
L_0003b0a6:
    swap.w r6,r4
L_0003b0a8:
    mov.l P_0003b120,r3
L_0003b0aa:
    exts.b r4,r6
L_0003b0ac:
    xtrct r6,r4
L_0003b0ae:
    mov.b @(0x2,r3),r0
L_0003b0b0:
    stc gbr,r6
L_0003b0b2:
    add #0x30,r6
L_0003b0b4:
    extu.b r0,r5
L_0003b0b6:
    mov r13,r0
L_0003b0b8:
    mov.w @(r0,r6),r2
L_0003b0ba:
    shar r4
L_0003b0bc:
    mul.l r2,r5
L_0003b0be:
    sts macl,r2
L_0003b0c0:
    cmp/pz r2
L_0003b0c2:
    bt L_0003b0d0
L_0003b0c4:
    mov r2,r0
L_0003b0c6:
    tst #0xff,r0
L_0003b0c8:
    bt L_0003b0d0
L_0003b0ca:
    mov #0x1,r7
L_0003b0cc:
    shll8 r7
L_0003b0ce:
    add r7,r2
L_0003b0d0:
    mov r2,r6
L_0003b0d2:
    shlr8 r6
L_0003b0d4:
    swap.w r6,r2
L_0003b0d6:
    exts.b r2,r6
L_0003b0d8:
    xtrct r6,r2
L_0003b0da:
    mov.w P_0003b0f0,r6
L_0003b0dc:
    add r2,r4
L_0003b0de:
    cmp/gt r6,r4
L_0003b0e0:
    bt L_0003b0e4
L_0003b0e2:
    mov r4,r6
L_0003b0e4:
    mov #-0x80,r2
L_0003b0e6:
    shll8 r2
L_0003b0e8:
    cmp/ge r2,r6
L_0003b0ea:
    bt L_0003b12e
L_0003b0ec:
    bra L_0003b12c
L_0003b0ee:
    nop
P_0003b0f0:
    .byte 0x7f
P_0003b0f1:
    .byte 0xff
    .org 0x32e58
P_0003b10c:
    .byte 0xff
P_0003b10d:
    .byte 0xff
P_0003b10e:
    .byte 0x1d
P_0003b10f:
    .byte 0xec
P_0003b110:
    .byte 0xff
P_0003b111:
    .byte 0xff
P_0003b112:
    .byte 0x24
P_0003b113:
    .byte 0x48
P_0003b114:
    .byte 0xff
P_0003b115:
    .byte 0xff
P_0003b116:
    .byte 0x24
P_0003b117:
    .byte 0xb4
P_0003b118:
    .byte 0xff
P_0003b119:
    .byte 0xff
P_0003b11a:
    .byte 0x43
P_0003b11b:
    .byte 0xc7
P_0003b11c:
    .byte 0xff
P_0003b11d:
    .byte 0xff
P_0003b11e:
    .byte 0x24
P_0003b11f:
    .byte 0x60
P_0003b120:
    .byte 0x00
P_0003b121:
    .byte 0x00
P_0003b122:
    .byte 0x82
P_0003b123:
    .byte 0xb6
P_0003b124:
    .byte 0xff
P_0003b125:
    .byte 0x00
P_0003b126:
    .byte 0x00
P_0003b127:
    .byte 0x01
P_0003b128:
    .byte 0x00
P_0003b129:
    .byte 0xff
P_0003b12a:
    .byte 0xff
P_0003b12b:
    .byte 0xff
L_0003b12c:
    mov r2,r6
L_0003b12e:
    stc gbr,r2
L_0003b130:
    exts.w r6,r6
L_0003b132:
    mov r13,r0
L_0003b134:
    add #0x30,r2
L_0003b136:
    cmp/pz r6
L_0003b138:
    bt/s L_0003b140
L_0003b13a:
    mov.w r6,@(r0,r2)
L_0003b13c:
    bra L_0003b146
L_0003b13e:
    mov #0x40,r2
L_0003b140:
    mov.l P_0003b37c,r3
L_0003b142:
    mov.b @r3,r2
L_0003b144:
    extu.b r2,r2
L_0003b146:
    mul.l r6,r2
L_0003b148:
    mov.w @(0x8,r15),r0
L_0003b14a:
    sts macl,r2
L_0003b14c:
    extu.w r0,r6
L_0003b14e:
    mov r0,r5
L_0003b150:
    mov.l r6,@(0xc,r15)
L_0003b152:
    mov.l P_0003b380,r6
L_0003b154:
    jsr @r6
L_0003b156:
    mov r2,r0
L_0003b158:
    mov.l @(0xc,r15),r6
L_0003b15a:
    mov.l @(0x4,r15),r5
L_0003b15c:
    add r6,r0
L_0003b15e:
    cmp/pz r0
L_0003b160:
    add r5,r0
L_0003b162:
    bt/s L_0003b174
L_0003b164:
    mov r0,r6
L_0003b166:
    stc gbr,r2
L_0003b168:
    add #0xc,r2
L_0003b16a:
    mov r14,r0
L_0003b16c:
    mov #0x0,r5
L_0003b16e:
    mov r6,r4
L_0003b170:
    bra L_0003b192
L_0003b172:
    mov.l r5,@(r0,r2)
L_0003b174:
    cmp/pz r6
L_0003b176:
    bt/s L_0003b180
L_0003b178:
    mov r6,r5
L_0003b17a:
    mov r5,r4
L_0003b17c:
    bra L_0003b182
L_0003b17e:
    mov #0x0,r5
L_0003b180:
    mov #0x0,r4
L_0003b182:
    mov.l P_0003b384,r6
L_0003b184:
    cmp/gt r6,r5
L_0003b186:
    bt L_0003b18a
L_0003b188:
    mov r5,r6
L_0003b18a:
    stc gbr,r2
L_0003b18c:
    add #0xc,r2
L_0003b18e:
    mov r14,r0
L_0003b190:
    mov.l r6,@(r0,r2)
L_0003b192:
    cmp/pz r4
L_0003b194:
    bt L_0003b1a6
L_0003b196:
    mov.b @r15,r6
L_0003b198:
    neg r4,r4
L_0003b19a:
    mov.b @(0x48,gbr),r0
L_0003b19c:
    not r6,r2
L_0003b19e:
    mov.l r0,@(0x14,r15)
L_0003b1a0:
    and r2,r0
L_0003b1a2:
    bra L_0003b1b0
L_0003b1a4:
    mov.b r0,@(0x48,gbr)
L_0003b1a6:
    mov.b @(0x48,gbr),r0
L_0003b1a8:
    mov.b @r15,r3
L_0003b1aa:
    mov.l r0,@(0x18,r15)
L_0003b1ac:
    or r3,r0
L_0003b1ae:
    mov.b r0,@(0x48,gbr)
L_0003b1b0:
    mov #-0x1,r2
L_0003b1b2:
    extu.w r2,r6
L_0003b1b4:
    cmp/gt r6,r4
L_0003b1b6:
    bt L_0003b1ba
L_0003b1b8:
    mov r4,r6
L_0003b1ba:
    stc gbr,r2
L_0003b1bc:
    add #0x44,r2
L_0003b1be:
    mov r13,r0
L_0003b1c0:
    bra L_0003b216
L_0003b1c2:
    mov.w r6,@(r0,r2)
L_0003b1c4:
    mov.l P_0003b388,r2
L_0003b1c6:
    mov #0x1,r7
L_0003b1c8:
    shll8 r7
L_0003b1ca:
    mov r14,r0
L_0003b1cc:
    mov.b @r2,r4
L_0003b1ce:
    stc gbr,r2
L_0003b1d0:
    add #0x24,r2
L_0003b1d2:
    extu.b r4,r4
L_0003b1d4:
    mov.l @(r0,r2),r6
L_0003b1d6:
    sub r4,r7
L_0003b1d8:
    mul.l r6,r7
L_0003b1da:
    sts macl,r6
L_0003b1dc:
    mul.l r5,r4
L_0003b1de:
    shlr2 r6
L_0003b1e0:
    shlr2 r6
L_0003b1e2:
    sts macl,r2
L_0003b1e4:
    shar r2
L_0003b1e6:
    shar r2
L_0003b1e8:
    shar r2
L_0003b1ea:
    shar r2
L_0003b1ec:
    add r2,r6
L_0003b1ee:
    shlr2 r6
L_0003b1f0:
    mov r6,r5
L_0003b1f2:
    mov.l P_0003b384,r6
L_0003b1f4:
    shlr2 r5
L_0003b1f6:
    cmp/hi r6,r5
L_0003b1f8:
    bt L_0003b1fc
L_0003b1fa:
    mov r5,r6
L_0003b1fc:
    stc gbr,r2
L_0003b1fe:
    add #0xc,r2
L_0003b200:
    mov r14,r0
L_0003b202:
    mov.l r6,@(r0,r2)
L_0003b204:
    mov #-0x1,r6
L_0003b206:
    extu.w r6,r6
L_0003b208:
    cmp/hi r6,r5
L_0003b20a:
    bt L_0003b20e
L_0003b20c:
    mov r5,r6
L_0003b20e:
    stc gbr,r2
L_0003b210:
    add #0x14,r2
L_0003b212:
    mov r13,r0
L_0003b214:
    mov.w r6,@(r0,r2)
L_0003b216:
    add #0x1c,r15
L_0003b218:
    ldc.l @r15+,gbr
L_0003b21a:
    lds.l @r15+,macl
L_0003b21c:
    lds.l @r15+,pr
L_0003b21e:
    mov.l @r15+,r14
L_0003b220:
    rts
L_0003b222:
    mov.l @r15+,r13
    .org 0x330c8
P_0003b37c:
    .byte 0x00
P_0003b37d:
    .byte 0x00
P_0003b37e:
    .byte 0x82
P_0003b37f:
    .byte 0xb6
P_0003b380:
    .byte 0x00
P_0003b381:
    .byte 0x02
P_0003b382:
    .byte 0x24
P_0003b383:
    .byte 0xfa
P_0003b384:
    .byte 0x00
P_0003b385:
    .byte 0xff
P_0003b386:
    .byte 0xff
P_0003b387:
    .byte 0xff
P_0003b388:
    .byte 0x00
P_0003b389:
    .byte 0x00
P_0003b38a:
    .byte 0x8a
P_0003b38b:
    .byte 0xc3
