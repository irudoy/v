! Exact masked one-shot and declared synthetic register storage.
    .text
    .balign 4
    .org 0x2c13c - 0x2c13c
L_0002c13c:
    mov.l r8,@-r15
    .org 0x2c13e - 0x2c13c
L_0002c13e:
    mov.l r9,@-r15
    .org 0x2c140 - 0x2c13c
L_0002c140:
    mov.l r10,@-r15
    .org 0x2c142 - 0x2c13c
L_0002c142:
    mov.l r11,@-r15
    .org 0x2c144 - 0x2c13c
L_0002c144:
    mov.l r12,@-r15
    .org 0x2c146 - 0x2c13c
L_0002c146:
    mov.l r13,@-r15
    .org 0x2c148 - 0x2c13c
L_0002c148:
    mov.l r14,@-r15
    .org 0x2c14a - 0x2c13c
L_0002c14a:
    sts.l macl,@-r15
    .org 0x2c14c - 0x2c13c
L_0002c14c:
    stc.l gbr,@-r15
    .org 0x2c14e - 0x2c13c
L_0002c14e:
    mov.l L_0002c240,r0
    .org 0x2c150 - 0x2c13c
L_0002c150:
    ldc r0,gbr
    .org 0x2c152 - 0x2c13c
L_0002c152:
    add #-0xc,r15
    .org 0x2c154 - 0x2c13c
L_0002c154:
    mov.l L_0002c244,r6
    .org 0x2c156 - 0x2c13c
L_0002c156:
    mov r5,r14
    .org 0x2c158 - 0x2c13c
L_0002c158:
    mov.b @r6,r0
    .org 0x2c15a - 0x2c13c
L_0002c15a:
    tst #0x80,r0
    .org 0x2c15c - 0x2c13c
L_0002c15c:
    bt/s L_0002c21e
    .org 0x2c15e - 0x2c13c
L_0002c15e:
    mov r4,r11
    .org 0x2c160 - 0x2c13c
L_0002c160:
    mov.w L_0002c234,r12
    .org 0x2c162 - 0x2c13c
L_0002c162:
    mov #-0x1,r8
    .org 0x2c164 - 0x2c13c
L_0002c164:
    extu.w r8,r8
    .org 0x2c166 - 0x2c13c
L_0002c166:
    mov.w L_0002c238,r9
    .org 0x2c168 - 0x2c13c
L_0002c168:
    mov r12,r10
    .org 0x2c16a - 0x2c13c
L_0002c16a:
    mov #0x1,r2
    .org 0x2c16c - 0x2c13c
L_0002c16c:
    mov #0x6,r13
    .org 0x2c16e - 0x2c13c
L_0002c16e:
    extu.b r2,r2
    .org 0x2c170 - 0x2c13c
L_0002c170:
    extu.b r11,r11
    .org 0x2c172 - 0x2c13c
L_0002c172:
    tst r2,r11
    .org 0x2c174 - 0x2c13c
L_0002c174:
    bt L_0002c20e
    .org 0x2c176 - 0x2c13c
L_0002c176:
    mov.l L_0002c248,r3
    .org 0x2c178 - 0x2c13c
L_0002c178:
    mov.b @(0x4,r3),r0
    .org 0x2c17a - 0x2c13c
L_0002c17a:
    tst r11,r0
    .org 0x2c17c - 0x2c13c
L_0002c17c:
    bf/s L_0002c18a
    .org 0x2c17e - 0x2c13c
L_0002c17e:
    mov.w @r14,r4
    .org 0x2c180 - 0x2c13c
L_0002c180:
    mov.l L_0002c24c,r3
    .org 0x2c182 - 0x2c13c
L_0002c182:
    mov.w L_0002c23a,r0
    .org 0x2c184 - 0x2c13c
L_0002c184:
    mov.b @(r0,r3),r6
    .org 0x2c186 - 0x2c13c
L_0002c186:
    tst r11,r6
    .org 0x2c188 - 0x2c13c
L_0002c188:
    bt L_0002c198
    .org 0x2c18a - 0x2c13c
L_0002c18a:
    mov.w @(0x7a,gbr),r0
    .org 0x2c18c - 0x2c13c
L_0002c18c:
    mov.l L_0002c24c,r1
    .org 0x2c18e - 0x2c13c
L_0002c18e:
    mov r0,r4
    .org 0x2c190 - 0x2c13c
L_0002c190:
    mov.w L_0002c23a,r0
    .org 0x2c192 - 0x2c13c
L_0002c192:
    mov.b @(r0,r1),r6
    .org 0x2c194 - 0x2c13c
L_0002c194:
    or r11,r6
    .org 0x2c196 - 0x2c13c
L_0002c196:
    mov.b r6,@(r0,r1)
    .org 0x2c198 - 0x2c13c
L_0002c198:
    mov #0x26,r0
    .org 0x2c19a - 0x2c13c
L_0002c19a:
    mov.w @(r0,r10),r5
    .org 0x2c19c - 0x2c13c
L_0002c19c:
    tst r2,r5
    .org 0x2c19e - 0x2c13c
L_0002c19e:
    bt L_0002c1b2
    .org 0x2c1a0 - 0x2c13c
L_0002c1a0:
    mov.w @(0x7a,gbr),r0
    .org 0x2c1a2 - 0x2c13c
L_0002c1a2:
    extu.w r4,r5
    .org 0x2c1a4 - 0x2c13c
L_0002c1a4:
    extu.w r0,r7
    .org 0x2c1a6 - 0x2c13c
L_0002c1a6:
    cmp/ge r7,r5
    .org 0x2c1a8 - 0x2c13c
L_0002c1a8:
    bt L_0002c1ae
    .org 0x2c1aa - 0x2c13c
L_0002c1aa:
    bra L_0002c1b0
    .org 0x2c1ac - 0x2c13c
L_0002c1ac:
    mov #0x0,r5
    .org 0x2c1ae - 0x2c13c
L_0002c1ae:
    sub r7,r5
    .org 0x2c1b0 - 0x2c13c
L_0002c1b0:
    mov r5,r4
    .org 0x2c1b2 - 0x2c13c
L_0002c1b2:
    mov.w L_0002c23c,r5
    .org 0x2c1b4 - 0x2c13c
L_0002c1b4:
    extu.w r4,r4
    .org 0x2c1b6 - 0x2c13c
L_0002c1b6:
    mul.l r4,r5
    .org 0x2c1b8 - 0x2c13c
L_0002c1b8:
    sts macl,r6
    .org 0x2c1ba - 0x2c13c
L_0002c1ba:
    shlr8 r6
    .org 0x2c1bc - 0x2c13c
L_0002c1bc:
    swap.w r6,r5
    .org 0x2c1be - 0x2c13c
L_0002c1be:
    exts.b r5,r6
    .org 0x2c1c0 - 0x2c13c
L_0002c1c0:
    xtrct r6,r5
    .org 0x2c1c2 - 0x2c13c
L_0002c1c2:
    cmp/hi r8,r5
    .org 0x2c1c4 - 0x2c13c
L_0002c1c4:
    bf L_0002c1c8
    .org 0x2c1c6 - 0x2c13c
L_0002c1c6:
    mov r8,r5
    .org 0x2c1c8 - 0x2c13c
L_0002c1c8:
    mov r5,r4
    .org 0x2c1ca - 0x2c13c
L_0002c1ca:
    mov r5,r0
    .org 0x2c1cc - 0x2c13c
L_0002c1cc:
    mov.l L_0002c250,r5
    .org 0x2c1ce - 0x2c13c
L_0002c1ce:
    mov.w r0,@(0x8,r15)
    .org 0x2c1d0 - 0x2c13c
L_0002c1d0:
    mov.b @(0x5,r5),r0
    .org 0x2c1d2 - 0x2c13c
L_0002c1d2:
    tst #0x1,r0
    .org 0x2c1d4 - 0x2c13c
L_0002c1d4:
    bt L_0002c1dc
    .org 0x2c1d6 - 0x2c13c
L_0002c1d6:
    mov.w L_0002c23e,r4
    .org 0x2c1d8 - 0x2c13c
L_0002c1d8:
    mov r4,r0
    .org 0x2c1da - 0x2c13c
L_0002c1da:
    mov.w r0,@(0x8,r15)
    .org 0x2c1dc - 0x2c13c
L_0002c1dc:
    stc sr,r0
    .org 0x2c1de - 0x2c13c
L_0002c1de:
    shlr2 r0
    .org 0x2c1e0 - 0x2c13c
L_0002c1e0:
    shlr2 r0
    .org 0x2c1e2 - 0x2c13c
L_0002c1e2:
    and #0xf,r0
    .org 0x2c1e4 - 0x2c13c
L_0002c1e4:
    mov r0,r6
    .org 0x2c1e6 - 0x2c13c
L_0002c1e6:
    stc sr,r0
    .org 0x2c1e8 - 0x2c13c
L_0002c1e8:
    and r9,r0
    .org 0x2c1ea - 0x2c13c
L_0002c1ea:
    or #0xf0,r0
    .org 0x2c1ec - 0x2c13c
L_0002c1ec:
    ldc r0,sr
    .org 0x2c1ee - 0x2c13c
L_0002c1ee:
    mov.w @r12,r5
    .org 0x2c1f0 - 0x2c13c
L_0002c1f0:
    mov r6,r0
    .org 0x2c1f2 - 0x2c13c
L_0002c1f2:
    and #0xf,r0
    .org 0x2c1f4 - 0x2c13c
L_0002c1f4:
    add r4,r5
    .org 0x2c1f6 - 0x2c13c
L_0002c1f6:
    mov.w r5,@r12
    .org 0x2c1f8 - 0x2c13c
L_0002c1f8:
    mov r0,r5
    .org 0x2c1fa - 0x2c13c
L_0002c1fa:
    shll2 r5
    .org 0x2c1fc - 0x2c13c
L_0002c1fc:
    shll2 r5
    .org 0x2c1fe - 0x2c13c
L_0002c1fe:
    stc sr,r6
    .org 0x2c200 - 0x2c13c
L_0002c200:
    and r9,r6
    .org 0x2c202 - 0x2c13c
L_0002c202:
    or r5,r6
    .org 0x2c204 - 0x2c13c
L_0002c204:
    ldc r6,sr
    .org 0x2c206 - 0x2c13c
L_0002c206:
    mov #0x26,r0
    .org 0x2c208 - 0x2c13c
L_0002c208:
    mov.w @(r0,r10),r6
    .org 0x2c20a - 0x2c13c
L_0002c20a:
    or r2,r6
    .org 0x2c20c - 0x2c13c
L_0002c20c:
    mov.w r6,@(r0,r10)
    .org 0x2c20e - 0x2c13c
L_0002c20e:
    add #0x2,r12
    .org 0x2c210 - 0x2c13c
L_0002c210:
    shll r2
    .org 0x2c212 - 0x2c13c
L_0002c212:
    mov.l r12,@r15
    .org 0x2c214 - 0x2c13c
L_0002c214:
    dt r13
    .org 0x2c216 - 0x2c13c
L_0002c216:
    mov r2,r0
    .org 0x2c218 - 0x2c13c
L_0002c218:
    add #0x2,r14
    .org 0x2c21a - 0x2c13c
L_0002c21a:
    bf/s L_0002c16e
    .org 0x2c21c - 0x2c13c
L_0002c21c:
    mov.b r0,@(0x4,r15)
    .org 0x2c21e - 0x2c13c
L_0002c21e:
    add #0xc,r15
    .org 0x2c220 - 0x2c13c
L_0002c220:
    ldc.l @r15+,gbr
    .org 0x2c222 - 0x2c13c
L_0002c222:
    lds.l @r15+,macl
    .org 0x2c224 - 0x2c13c
L_0002c224:
    mov.l @r15+,r14
    .org 0x2c226 - 0x2c13c
L_0002c226:
    mov.l @r15+,r13
    .org 0x2c228 - 0x2c13c
L_0002c228:
    mov.l @r15+,r12
    .org 0x2c22a - 0x2c13c
L_0002c22a:
    mov.l @r15+,r11
    .org 0x2c22c - 0x2c13c
L_0002c22c:
    mov.l @r15+,r10
    .org 0x2c22e - 0x2c13c
L_0002c22e:
    mov.l @r15+,r9
    .org 0x2c230 - 0x2c13c
L_0002c230:
    rts
    .org 0x2c232 - 0x2c13c
L_0002c232:
    mov.l @r15+,r8
    .org 0x2c234 - 0x2c13c
L_0002c234:
    .word 0xf640
    .org 0x2c238 - 0x2c13c
L_0002c238:
    .word 0xff0f
    .org 0x2c23a - 0x2c13c
L_0002c23a:
    .word 0x06a9
    .org 0x2c23c - 0x2c13c
L_0002c23c:
    .word 0x0320
    .org 0x2c23e - 0x2c13c
L_0002c23e:
    .word 0x03e8
    .org 0x2c240 - 0x2c13c
L_0002c240:
    .long 0xffff2330
    .org 0x2c244 - 0x2c13c
L_0002c244:
    .long 0xffff4184
    .org 0x2c248 - 0x2c13c
L_0002c248:
    .long 0xffff22dc
    .org 0x2c24c - 0x2c13c
L_0002c24c:
    .long 0xffff128c
    .org 0x2c250 - 0x2c13c
L_0002c250:
    .long 0xffff424c
