! Complete RAM-only reference learner and real diagnostic predicate.
    .section .text
    .balign 4
    .org 0x884b - 0x8848
.byte 0xe0
    .org 0x8b3d - 0x8848
.byte 0x82
    .org 0x9282 - 0x8848
.word 0xffff
    .org 0x25e20 - 0x8848
L_25e20:
    mov.l P_25f10,r1
    .org 0x25e22 - 0x8848
L_25e22:
    exts.w r4,r0
    .org 0x25e24 - 0x8848
L_25e24:
    cmp/eq #-0x1,r0
    .org 0x25e26 - 0x8848
L_25e26:
    bt L_25e3e
    .org 0x25e28 - 0x8848
L_25e28:
    mov r1,r6
    .org 0x25e2a - 0x8848
L_25e2a:
    mov r0,r2
    .org 0x25e2c - 0x8848
L_25e2c:
    shll r2
    .org 0x25e2e - 0x8848
L_25e2e:
    add r0,r2
    .org 0x25e30 - 0x8848
L_25e30:
    add r2,r6
    .org 0x25e32 - 0x8848
L_25e32:
    mov.b @(0x1,r6),r0
    .org 0x25e34 - 0x8848
L_25e34:
    tst #0x80,r0
    .org 0x25e36 - 0x8848
L_25e36:
    movt r0
    .org 0x25e38 - 0x8848
L_25e38:
    xor #0x1,r0
    .org 0x25e3a - 0x8848
L_25e3a:
    bra L_25e40
    .org 0x25e3c - 0x8848
L_25e3c:
    extu.b r0,r2
    .org 0x25e3e - 0x8848
L_25e3e:
    mov #0x0,r2
    .org 0x25e40 - 0x8848
L_25e40:
    rts
    .org 0x25e42 - 0x8848
L_25e42:
    mov r2,r0
    .org 0x25f10 - 0x8848
P_25f10: .long 0xffff5718
    .org 0x4a118 - 0x8848
L_4a118:
    mov.l r8,@-r15
    .org 0x4a11a - 0x8848
L_4a11a:
    mov.l r9,@-r15
    .org 0x4a11c - 0x8848
L_4a11c:
    mov.l r10,@-r15
    .org 0x4a11e - 0x8848
L_4a11e:
    mov.l r11,@-r15
    .org 0x4a120 - 0x8848
L_4a120:
    mov.l r12,@-r15
    .org 0x4a122 - 0x8848
L_4a122:
    mov.l r13,@-r15
    .org 0x4a124 - 0x8848
L_4a124:
    mov.l r14,@-r15
    .org 0x4a126 - 0x8848
L_4a126:
    sts.l pr,@-r15
    .org 0x4a128 - 0x8848
L_4a128:
    sts.l macl,@-r15
    .org 0x4a12a - 0x8848
L_4a12a:
    mov.l P_4a1fc,r2
    .org 0x4a12c - 0x8848
L_4a12c:
    mov.b @r2,r0
    .org 0x4a12e - 0x8848
L_4a12e:
    tst #0x8,r0
    .org 0x4a130 - 0x8848
L_4a130:
    bt L_4a17c
    .org 0x4a132 - 0x8848
L_4a132:
    mov #0x1,r0
    .org 0x4a134 - 0x8848
L_4a134:
    mov.l P_4a200,r2
    .org 0x4a136 - 0x8848
L_4a136:
    shll8 r0
    .org 0x4a138 - 0x8848
L_4a138:
    add #0x4f,r0
    .org 0x4a13a - 0x8848
L_4a13a:
    mov.b @(r0,r2),r12
    .org 0x4a13c - 0x8848
L_4a13c:
    mov #0x1,r4
    .org 0x4a13e - 0x8848
L_4a13e:
    mov.l P_4a224,r6
    .org 0x4a140 - 0x8848
L_4a140:
    shll8 r4
    .org 0x4a142 - 0x8848
L_4a142:
    jsr @r6
    .org 0x4a144 - 0x8848
L_4a144:
    add #0x2d,r4
    .org 0x4a146 - 0x8848
L_4a146:
    tst r0,r0
    .org 0x4a148 - 0x8848
L_4a148:
    bt L_4a184
    .org 0x4a14a - 0x8848
L_4a14a:
    mov.l P_4a228,r2
    .org 0x4a14c - 0x8848
L_4a14c:
    mov #0x3,r4
    .org 0x4a14e - 0x8848
L_4a14e:
    mov.l P_4a22c,r7
    .org 0x4a150 - 0x8848
L_4a150:
    mov.w @r2,r5
    .org 0x4a152 - 0x8848
L_4a152:
    mov #0x8,r6
    .org 0x4a154 - 0x8848
L_4a154:
    mov r7,r2
    .org 0x4a156 - 0x8848
L_4a156:
    dt r6
    .org 0x4a158 - 0x8848
L_4a158:
    mov.w r5,@r2
    .org 0x4a15a - 0x8848
L_4a15a:
    mov r5,r0
    .org 0x4a15c - 0x8848
L_4a15c:
    mov.w r0,@(0x10,r2)
    .org 0x4a15e - 0x8848
L_4a15e:
    bf/s L_4a156
    .org 0x4a160 - 0x8848
L_4a160:
    add #0x2,r2
    .org 0x4a162 - 0x8848
L_4a162:
    dt r4
    .org 0x4a164 - 0x8848
L_4a164:
    bf/s L_4a152
    .org 0x4a166 - 0x8848
L_4a166:
    add #0x20,r7
    .org 0x4a168 - 0x8848
L_4a168:
    lds.l @r15+,macl
    .org 0x4a16a - 0x8848
L_4a16a:
    lds.l @r15+,pr
    .org 0x4a16c - 0x8848
L_4a16c:
    mov.l @r15+,r14
    .org 0x4a16e - 0x8848
L_4a16e:
    mov.l @r15+,r13
    .org 0x4a170 - 0x8848
L_4a170:
    mov.l @r15+,r12
    .org 0x4a172 - 0x8848
L_4a172:
    mov.l @r15+,r11
    .org 0x4a174 - 0x8848
L_4a174:
    mov.l @r15+,r10
    .org 0x4a176 - 0x8848
L_4a176:
    mov.l @r15+,r9
    .org 0x4a178 - 0x8848
L_4a178:
    rts
    .org 0x4a17a - 0x8848
L_4a17a:
    mov.l @r15+,r8
    .org 0x4a17c - 0x8848
L_4a17c:
    mov.l P_4a208,r6
    .org 0x4a17e - 0x8848
L_4a17e:
    mov.b @(0xa,r6),r0
    .org 0x4a180 - 0x8848
L_4a180:
    bra L_4a13c
    .org 0x4a182 - 0x8848
L_4a182:
    mov r0,r12
    .org 0x4a184 - 0x8848
L_4a184:
    mov #0x1,r4
    .org 0x4a186 - 0x8848
L_4a186:
    mov.l P_4a224,r6
    .org 0x4a188 - 0x8848
L_4a188:
    shll8 r4
    .org 0x4a18a - 0x8848
L_4a18a:
    jsr @r6
    .org 0x4a18c - 0x8848
L_4a18c:
    add #0x3f,r4
    .org 0x4a18e - 0x8848
L_4a18e:
    tst r0,r0
    .org 0x4a190 - 0x8848
L_4a190:
    bf L_4a14a
    .org 0x4a192 - 0x8848
L_4a192:
    extu.b r12,r12
    .org 0x4a194 - 0x8848
L_4a194:
    mov.l P_4a22c,r9
    .org 0x4a196 - 0x8848
L_4a196:
    mov r12,r6
    .org 0x4a198 - 0x8848
L_4a198:
    shll2 r6
    .org 0x4a19a - 0x8848
L_4a19a:
    shll2 r6
    .org 0x4a19c - 0x8848
L_4a19c:
    mov.l P_4a230,r2
    .org 0x4a19e - 0x8848
L_4a19e:
    mov r9,r10
    .org 0x4a1a0 - 0x8848
L_4a1a0:
    add r6,r10
    .org 0x4a1a2 - 0x8848
L_4a1a2:
    mov #-0x1,r8
    .org 0x4a1a4 - 0x8848
L_4a1a4:
    mov.b @r2,r13
    .org 0x4a1a6 - 0x8848
L_4a1a6:
    mov #-0x1,r11
    .org 0x4a1a8 - 0x8848
L_4a1a8:
    add #-0x10,r10
    .org 0x4a1aa - 0x8848
L_4a1aa:
    extu.b r8,r8
    .org 0x4a1ac - 0x8848
L_4a1ac:
    extu.w r11,r11
    .org 0x4a1ae - 0x8848
L_4a1ae:
    mov #0x8,r14
    .org 0x4a1b0 - 0x8848
L_4a1b0:
    mov #0x0,r7
    .org 0x4a1b2 - 0x8848
L_4a1b2:
    mov.l P_4a234,r5
    .org 0x4a1b4 - 0x8848
L_4a1b4:
    mov r7,r0
    .org 0x4a1b6 - 0x8848
L_4a1b6:
    mov.w @(r0,r10),r6
    .org 0x4a1b8 - 0x8848
L_4a1b8:
    mov r7,r0
    .org 0x4a1ba - 0x8848
L_4a1ba:
    mov.w @(r0,r5),r2
    .org 0x4a1bc - 0x8848
L_4a1bc:
    extu.b r13,r13
    .org 0x4a1be - 0x8848
L_4a1be:
    extu.w r6,r6
    .org 0x4a1c0 - 0x8848
L_4a1c0:
    mov r8,r4
    .org 0x4a1c2 - 0x8848
L_4a1c2:
    extu.w r2,r2
    .org 0x4a1c4 - 0x8848
L_4a1c4:
    mul.l r2,r13
    .org 0x4a1c6 - 0x8848
L_4a1c6:
    sub r13,r4
    .org 0x4a1c8 - 0x8848
L_4a1c8:
    sts macl,r5
    .org 0x4a1ca - 0x8848
L_4a1ca:
    mul.l r6,r4
    .org 0x4a1cc - 0x8848
L_4a1cc:
    sts macl,r2
    .org 0x4a1ce - 0x8848
L_4a1ce:
    add r2,r5
    .org 0x4a1d0 - 0x8848
L_4a1d0:
    shlr8 r5
    .org 0x4a1d2 - 0x8848
L_4a1d2:
    cmp/hs r6,r5
    .org 0x4a1d4 - 0x8848
L_4a1d4:
    bt L_4a1d8
    .org 0x4a1d6 - 0x8848
L_4a1d6:
    add #0x1,r5
    .org 0x4a1d8 - 0x8848
L_4a1d8:
    cmp/hi r11,r5
    .org 0x4a1da - 0x8848
L_4a1da:
    bf L_4a1f8
    .org 0x4a1dc - 0x8848
L_4a1dc:
    mov r11,r4
    .org 0x4a1de - 0x8848
L_4a1de:
    extu.b r12,r12
    .org 0x4a1e0 - 0x8848
L_4a1e0:
    mov r9,r6
    .org 0x4a1e2 - 0x8848
L_4a1e2:
    mov r12,r0
    .org 0x4a1e4 - 0x8848
L_4a1e4:
    shll2 r0
    .org 0x4a1e6 - 0x8848
L_4a1e6:
    shll2 r0
    .org 0x4a1e8 - 0x8848
L_4a1e8:
    add #-0x10,r6
    .org 0x4a1ea - 0x8848
L_4a1ea:
    add r7,r0
    .org 0x4a1ec - 0x8848
L_4a1ec:
    dt r14
    .org 0x4a1ee - 0x8848
L_4a1ee:
    mov.w r4,@(r0,r6)
    .org 0x4a1f0 - 0x8848
L_4a1f0:
    bf/s L_4a1b2
    .org 0x4a1f2 - 0x8848
L_4a1f2:
    add #0x2,r7
    .org 0x4a1f4 - 0x8848
L_4a1f4:
    bra L_4a168
    .org 0x4a1f6 - 0x8848
L_4a1f6:
    nop
    .org 0x4a1f8 - 0x8848
L_4a1f8:
    bra L_4a1de
    .org 0x4a1fa - 0x8848
L_4a1fa:
    mov r5,r4
    .org 0x4a1fc - 0x8848
P_4a1fc: .long 0x00008b3d
    .org 0x4a200 - 0x8848
P_4a200: .long 0xffff1ff4
    .org 0x4a208 - 0x8848
P_4a208: .long 0xffff11d4
    .org 0x4a224 - 0x8848
P_4a224: .long 0x00025e20
    .org 0x4a228 - 0x8848
P_4a228: .long 0x00009282
    .org 0x4a22c - 0x8848
P_4a22c: .long 0xffff2178
    .org 0x4a230 - 0x8848
P_4a230: .long 0x0000884b
    .org 0x4a234 - 0x8848
P_4a234: .long 0xffff20c2
