! Complete injector event ISR with actual selector, correction and one-shot callees.
    .text
    .balign 4
    .org 0x85f7 - 0x85f4
L_000085f7:
    .byte 0x80
    .org 0x8d92 - 0x85f4
L_00008d92:
    .byte 0x7a
    .org 0x94e8 - 0x85f4
L_000094e8:
    .word 0x00aa
    .org 0x2219c - 0x85f4
L_0002219c:
    .byte 0x0e,0x0c,0x0a,0x08,0x06,0x04,0x02,0x00,0x20,0x1e,0x1c,0x1a,0x18,0x16,0x14,0x12,0x34,0x32,0x30,0x2e,0x2c,0x2a,0x28,0x26,0x40,0x3e,0x3c,0x3a,0x48,0x56,0x62,0x6c
    .org 0x221bc - 0x85f4
L_000221bc:
    mov.l r2,@-r15
    .org 0x221be - 0x85f4
L_000221be:
    cmp/pz r1
    .org 0x221c0 - 0x85f4
L_000221c0:
    bf/s L_000221f4
    .org 0x221c2 - 0x85f4
L_000221c2:
    mov #0x20,r2
    .org 0x221c4 - 0x85f4
L_000221c4:
    cmp/ge r2,r1
    .org 0x221c6 - 0x85f4
L_000221c6:
    bt L_000221e0
    .org 0x221c8 - 0x85f4
L_000221c8:
    mov.l L_000221dc,r2
    .org 0x221ca - 0x85f4
L_000221ca:
    add r1,r2
    .org 0x221cc - 0x85f4
L_000221cc:
    mov.b @r2,r2
    .org 0x221ce - 0x85f4
L_000221ce:
    mov.l L_000221d8,r1
    .org 0x221d0 - 0x85f4
L_000221d0:
    add r2,r1
    .org 0x221d2 - 0x85f4
L_000221d2:
    jmp @r1
    .org 0x221d4 - 0x85f4
L_000221d4:
    nop
    .org 0x221d8 - 0x85f4
L_000221d8:
    .long 0x000221e6
    .org 0x221dc - 0x85f4
L_000221dc:
    .long 0x0002219c
    .org 0x221e0 - 0x85f4
L_000221e0:
    mov #0x0,r0
    .org 0x221e2 - 0x85f4
L_000221e2:
    rts
    .org 0x221e4 - 0x85f4
L_000221e4:
    mov.l @r15+,r2
    .org 0x221e6 - 0x85f4
L_000221e6:
    shll r0
    .org 0x221e8 - 0x85f4
L_000221e8:
    shll r0
    .org 0x221ea - 0x85f4
L_000221ea:
    shll r0
    .org 0x221ec - 0x85f4
L_000221ec:
    shll r0
    .org 0x221ee - 0x85f4
L_000221ee:
    shll r0
    .org 0x221f0 - 0x85f4
L_000221f0:
    shll r0
    .org 0x221f2 - 0x85f4
L_000221f2:
    shll r0
    .org 0x221f4 - 0x85f4
L_000221f4:
    rts
    .org 0x221f6 - 0x85f4
L_000221f6:
    mov.l @r15+,r2
    .org 0x2be40 - 0x85f4
L_0002be40:
    mov.l r0,@-r15
    .org 0x2be42 - 0x85f4
L_0002be42:
    mov.l r1,@-r15
    .org 0x2be44 - 0x85f4
L_0002be44:
    mov.l r2,@-r15
    .org 0x2be46 - 0x85f4
L_0002be46:
    mov.l r3,@-r15
    .org 0x2be48 - 0x85f4
L_0002be48:
    mov.l r4,@-r15
    .org 0x2be4a - 0x85f4
L_0002be4a:
    mov.l r5,@-r15
    .org 0x2be4c - 0x85f4
L_0002be4c:
    mov.l r6,@-r15
    .org 0x2be4e - 0x85f4
L_0002be4e:
    mov.l r7,@-r15
    .org 0x2be50 - 0x85f4
L_0002be50:
    mov.l r12,@-r15
    .org 0x2be52 - 0x85f4
L_0002be52:
    mov.l r13,@-r15
    .org 0x2be54 - 0x85f4
L_0002be54:
    mov.l r14,@-r15
    .org 0x2be56 - 0x85f4
L_0002be56:
    sts.l pr,@-r15
    .org 0x2be58 - 0x85f4
L_0002be58:
    stc.l gbr,@-r15
    .org 0x2be5a - 0x85f4
L_0002be5a:
    mov.l L_0002c0bc,r0
    .org 0x2be5c - 0x85f4
L_0002be5c:
    ldc r0,gbr
    .org 0x2be5e - 0x85f4
L_0002be5e:
    add #-0x4,r15
    .org 0x2be60 - 0x85f4
L_0002be60:
    mov.w L_0002bf7a,r14
    .org 0x2be62 - 0x85f4
L_0002be62:
    mov.w L_0002bf7c,r6
    .org 0x2be64 - 0x85f4
L_0002be64:
    mov.w @(0x1e,r14),r0
    .org 0x2be66 - 0x85f4
L_0002be66:
    mov.w r0,@r15
    .org 0x2be68 - 0x85f4
L_0002be68:
    mov.w L_0002bf7e,r0
    .org 0x2be6a - 0x85f4
L_0002be6a:
    mov.w r0,@(0x1e,r14)
    .org 0x2be6c - 0x85f4
L_0002be6c:
    mov.b @r6,r0
    .org 0x2be6e - 0x85f4
L_0002be6e:
    and #0x7f,r0
    .org 0x2be70 - 0x85f4
L_0002be70:
    mov.b r0,@r6
    .org 0x2be72 - 0x85f4
L_0002be72:
    mov.w L_0002bf80,r6
    .org 0x2be74 - 0x85f4
L_0002be74:
    mov.b @r6,r0
    .org 0x2be76 - 0x85f4
L_0002be76:
    tst #0x80,r0
    .org 0x2be78 - 0x85f4
L_0002be78:
    bt L_0002be80
    .org 0x2be7a - 0x85f4
L_0002be7a:
    mov.l L_0002c0c0,r2
    .org 0x2be7c - 0x85f4
L_0002be7c:
    bra L_0002be90
    .org 0x2be7e - 0x85f4
L_0002be7e:
    mov #0x3,r4
    .org 0x2be80 - 0x85f4
L_0002be80:
    mov.l L_0002c0bc,r12
    .org 0x2be82 - 0x85f4
L_0002be82:
    mov #0x3,r6
    .org 0x2be84 - 0x85f4
L_0002be84:
    mov.w L_0002bf82,r0
    .org 0x2be86 - 0x85f4
L_0002be86:
    mov.b @(r0,r12),r2
    .org 0x2be88 - 0x85f4
L_0002be88:
    cmp/hi r6,r2
    .org 0x2be8a - 0x85f4
L_0002be8a:
    mov.l L_0002c0c0,r2
    .org 0x2be8c - 0x85f4
L_0002be8c:
    bt L_0002be98
    .org 0x2be8e - 0x85f4
L_0002be8e:
    mov #0x2,r4
    .org 0x2be90 - 0x85f4
L_0002be90:
    jsr @r2
    .org 0x2be92 - 0x85f4
L_0002be92:
    nop
    .org 0x2be94 - 0x85f4
L_0002be94:
    bra L_0002bea4
    .org 0x2be96 - 0x85f4
L_0002be96:
    nop
    .org 0x2be98 - 0x85f4
L_0002be98:
    jsr @r2
    .org 0x2be9a - 0x85f4
L_0002be9a:
    mov #0x4,r4
    .org 0x2be9c - 0x85f4
L_0002be9c:
    mov.w L_0002bf80,r6
    .org 0x2be9e - 0x85f4
L_0002be9e:
    mov.b @r6,r0
    .org 0x2bea0 - 0x85f4
L_0002bea0:
    or #0x80,r0
    .org 0x2bea2 - 0x85f4
L_0002bea2:
    mov.b r0,@r6
    .org 0x2bea4 - 0x85f4
L_0002bea4:
    mov.b @(0xc1,gbr),r0
    .org 0x2bea6 - 0x85f4
L_0002bea6:
    mov.l L_0002c0bc,r12
    .org 0x2bea8 - 0x85f4
L_0002bea8:
    mov r0,r13
    .org 0x2beaa - 0x85f4
L_0002beaa:
    mov.w L_0002bf84,r0
    .org 0x2beac - 0x85f4
L_0002beac:
    mov.b @(r0,r12),r4
    .org 0x2beae - 0x85f4
L_0002beae:
    or r4,r13
    .org 0x2beb0 - 0x85f4
L_0002beb0:
    mov r13,r0
    .org 0x2beb2 - 0x85f4
L_0002beb2:
    mov.b r0,@(0xc1,gbr)
    .org 0x2beb4 - 0x85f4
L_0002beb4:
    mov.l L_0002c0c4,r13
    .org 0x2beb6 - 0x85f4
L_0002beb6:
    mov.w L_0002bf86,r0
    .org 0x2beb8 - 0x85f4
L_0002beb8:
    mov.b @(r0,r13),r2
    .org 0x2beba - 0x85f4
L_0002beba:
    or r4,r2
    .org 0x2bebc - 0x85f4
L_0002bebc:
    mov.b r2,@(r0,r13)
    .org 0x2bebe - 0x85f4
L_0002bebe:
    mov.w L_0002bf88,r0
    .org 0x2bec0 - 0x85f4
L_0002bec0:
    mov.b @(r0,r13),r2
    .org 0x2bec2 - 0x85f4
L_0002bec2:
    or r4,r2
    .org 0x2bec4 - 0x85f4
L_0002bec4:
    mov.b r2,@(r0,r13)
    .org 0x2bec6 - 0x85f4
L_0002bec6:
    not r4,r2
    .org 0x2bec8 - 0x85f4
L_0002bec8:
    mov.w L_0002bf8a,r0
    .org 0x2beca - 0x85f4
L_0002beca:
    mov.b r4,@(r0,r13)
    .org 0x2becc - 0x85f4
L_0002becc:
    mov.w L_0002bf8c,r0
    .org 0x2bece - 0x85f4
L_0002bece:
    mov.b @(r0,r13),r5
    .org 0x2bed0 - 0x85f4
L_0002bed0:
    and r2,r5
    .org 0x2bed2 - 0x85f4
L_0002bed2:
    mov.b r5,@(r0,r13)
    .org 0x2bed4 - 0x85f4
L_0002bed4:
    mov.w L_0002bf8e,r0
    .org 0x2bed6 - 0x85f4
L_0002bed6:
    mov.b @(r0,r13),r6
    .org 0x2bed8 - 0x85f4
L_0002bed8:
    tst r6,r6
    .org 0x2beda - 0x85f4
L_0002beda:
    bt L_0002bef2
    .org 0x2bedc - 0x85f4
L_0002bedc:
    mov.l L_0002c0c8,r7
    .org 0x2bede - 0x85f4
L_0002bede:
    mov.b @(0x4,r7),r0
    .org 0x2bee0 - 0x85f4
L_0002bee0:
    tst r0,r0
    .org 0x2bee2 - 0x85f4
L_0002bee2:
    bt L_0002bef2
    .org 0x2bee4 - 0x85f4
L_0002bee4:
    mov.w L_0002bf8e,r0
    .org 0x2bee6 - 0x85f4
L_0002bee6:
    add #-0x1,r6
    .org 0x2bee8 - 0x85f4
L_0002bee8:
    extu.b r6,r6
    .org 0x2beea - 0x85f4
L_0002beea:
    or r4,r5
    .org 0x2beec - 0x85f4
L_0002beec:
    mov.b r6,@(r0,r13)
    .org 0x2beee - 0x85f4
L_0002beee:
    mov.w L_0002bf8c,r0
    .org 0x2bef0 - 0x85f4
L_0002bef0:
    mov.b r5,@(r0,r13)
    .org 0x2bef2 - 0x85f4
L_0002bef2:
    mov.l L_0002c0bc,r5
    .org 0x2bef4 - 0x85f4
L_0002bef4:
    mov.w L_0002bf90,r2
    .org 0x2bef6 - 0x85f4
L_0002bef6:
    bsr L_0002c13c
    .org 0x2bef8 - 0x85f4
L_0002bef8:
    add r2,r5
    .org 0x2befa - 0x85f4
L_0002befa:
    mov #0x22,r0
    .org 0x2befc - 0x85f4
L_0002befc:
    mov.w @(r0,r14),r2
    .org 0x2befe - 0x85f4
L_0002befe:
    mov #-0x2,r5
    .org 0x2bf00 - 0x85f4
L_0002bf00:
    extu.w r2,r6
    .org 0x2bf02 - 0x85f4
L_0002bf02:
    mov.l L_0002c0cc,r2
    .org 0x2bf04 - 0x85f4
L_0002bf04:
    and r5,r6
    .org 0x2bf06 - 0x85f4
L_0002bf06:
    mov.w r6,@(r0,r14)
    .org 0x2bf08 - 0x85f4
L_0002bf08:
    mov.b @r2,r0
    .org 0x2bf0a - 0x85f4
L_0002bf0a:
    and #0x8,r0
    .org 0x2bf0c - 0x85f4
L_0002bf0c:
    tst r0,r0
    .org 0x2bf0e - 0x85f4
L_0002bf0e:
    bf/s L_0002bf40
    .org 0x2bf10 - 0x85f4
L_0002bf10:
    mov r0,r6
    .org 0x2bf12 - 0x85f4
L_0002bf12:
    mov.w L_0002bf92,r0
    .org 0x2bf14 - 0x85f4
L_0002bf14:
    mov #-0x1,r4
    .org 0x2bf16 - 0x85f4
L_0002bf16:
    extu.b r4,r4
    .org 0x2bf18 - 0x85f4
L_0002bf18:
    mov.b @(r0,r12),r5
    .org 0x2bf1a - 0x85f4
L_0002bf1a:
    extu.b r5,r5
    .org 0x2bf1c - 0x85f4
L_0002bf1c:
    cmp/eq r4,r5
    .org 0x2bf1e - 0x85f4
L_0002bf1e:
    bt L_0002bf24
    .org 0x2bf20 - 0x85f4
L_0002bf20:
    add #0x1,r5
    .org 0x2bf22 - 0x85f4
L_0002bf22:
    mov.b r5,@(r0,r12)
    .org 0x2bf24 - 0x85f4
L_0002bf24:
    mov.w L_0002bf94,r0
    .org 0x2bf26 - 0x85f4
L_0002bf26:
    mov.b @(r0,r12),r5
    .org 0x2bf28 - 0x85f4
L_0002bf28:
    extu.b r5,r5
    .org 0x2bf2a - 0x85f4
L_0002bf2a:
    cmp/eq r4,r5
    .org 0x2bf2c - 0x85f4
L_0002bf2c:
    bt L_0002bf32
    .org 0x2bf2e - 0x85f4
L_0002bf2e:
    add #0x1,r5
    .org 0x2bf30 - 0x85f4
L_0002bf30:
    mov.b r5,@(r0,r12)
    .org 0x2bf32 - 0x85f4
L_0002bf32:
    mov.w L_0002bf96,r0
    .org 0x2bf34 - 0x85f4
L_0002bf34:
    mov.b @(r0,r12),r5
    .org 0x2bf36 - 0x85f4
L_0002bf36:
    extu.b r5,r5
    .org 0x2bf38 - 0x85f4
L_0002bf38:
    cmp/eq r4,r5
    .org 0x2bf3a - 0x85f4
L_0002bf3a:
    bt L_0002bf40
    .org 0x2bf3c - 0x85f4
L_0002bf3c:
    add #0x1,r5
    .org 0x2bf3e - 0x85f4
L_0002bf3e:
    mov.b r5,@(r0,r12)
    .org 0x2bf40 - 0x85f4
L_0002bf40:
    tst r6,r6
    .org 0x2bf42 - 0x85f4
L_0002bf42:
    bt L_0002bf5a
    .org 0x2bf44 - 0x85f4
L_0002bf44:
    mov.w L_0002bf98,r0
    .org 0x2bf46 - 0x85f4
L_0002bf46:
    mov.b @(r0,r13),r6
    .org 0x2bf48 - 0x85f4
L_0002bf48:
    mov.w L_0002bf84,r0
    .org 0x2bf4a - 0x85f4
L_0002bf4a:
    mov.b @(r0,r12),r2
    .org 0x2bf4c - 0x85f4
L_0002bf4c:
    mov.w L_0002bf98,r0
    .org 0x2bf4e - 0x85f4
L_0002bf4e:
    or r2,r6
    .org 0x2bf50 - 0x85f4
L_0002bf50:
    mov.b r6,@(r0,r13)
    .org 0x2bf52 - 0x85f4
L_0002bf52:
    mov.w L_0002bf9a,r0
    .org 0x2bf54 - 0x85f4
L_0002bf54:
    mov.b @(r0,r13),r6
    .org 0x2bf56 - 0x85f4
L_0002bf56:
    or r2,r6
    .org 0x2bf58 - 0x85f4
L_0002bf58:
    mov.b r6,@(r0,r13)
    .org 0x2bf5a - 0x85f4
L_0002bf5a:
    add #0x4,r15
    .org 0x2bf5c - 0x85f4
L_0002bf5c:
    ldc.l @r15+,gbr
    .org 0x2bf5e - 0x85f4
L_0002bf5e:
    lds.l @r15+,pr
    .org 0x2bf60 - 0x85f4
L_0002bf60:
    mov.l @r15+,r14
    .org 0x2bf62 - 0x85f4
L_0002bf62:
    mov.l @r15+,r13
    .org 0x2bf64 - 0x85f4
L_0002bf64:
    mov.l @r15+,r12
    .org 0x2bf66 - 0x85f4
L_0002bf66:
    mov.l @r15+,r7
    .org 0x2bf68 - 0x85f4
L_0002bf68:
    mov.l @r15+,r6
    .org 0x2bf6a - 0x85f4
L_0002bf6a:
    mov.l @r15+,r5
    .org 0x2bf6c - 0x85f4
L_0002bf6c:
    mov.l @r15+,r4
    .org 0x2bf6e - 0x85f4
L_0002bf6e:
    mov.l @r15+,r3
    .org 0x2bf70 - 0x85f4
L_0002bf70:
    mov.l @r15+,r2
    .org 0x2bf72 - 0x85f4
L_0002bf72:
    mov.l @r15+,r1
    .org 0x2bf74 - 0x85f4
L_0002bf74:
    mov.l @r15+,r0
    .org 0x2bf76 - 0x85f4
L_0002bf76:
    rte
    .org 0x2bf78 - 0x85f4
L_0002bf78:
    nop
    .org 0x2bf7a - 0x85f4
L_0002bf7a:
    .word 0xf440
    .org 0x2bf7c - 0x85f4
L_0002bf7c:
    .word 0x84ec
    .org 0x2bf7e - 0x85f4
L_0002bf7e:
    .word 0x01fe
    .org 0x2bf80 - 0x85f4
L_0002bf80:
    .word 0x8514
    .org 0x2bf82 - 0x85f4
L_0002bf82:
    .word 0x02a4
    .org 0x2bf84 - 0x85f4
L_0002bf84:
    .word 0x0234
    .org 0x2bf86 - 0x85f4
L_0002bf86:
    .word 0x02f2
    .org 0x2bf88 - 0x85f4
L_0002bf88:
    .word 0x0472
    .org 0x2bf8a - 0x85f4
L_0002bf8a:
    .word 0x06aa
    .org 0x2bf8c - 0x85f4
L_0002bf8c:
    .word 0x06a9
    .org 0x2bf8e - 0x85f4
L_0002bf8e:
    .word 0x06ab
    .org 0x2bf90 - 0x85f4
L_0002bf90:
    .word 0x025a
    .org 0x2bf92 - 0x85f4
L_0002bf92:
    .word 0x027c
    .org 0x2bf94 - 0x85f4
L_0002bf94:
    .word 0x027b
    .org 0x2bf96 - 0x85f4
L_0002bf96:
    .word 0x027a
    .org 0x2bf98 - 0x85f4
L_0002bf98:
    .word 0x0237
    .org 0x2bf9a - 0x85f4
L_0002bf9a:
    .word 0x0236
    .org 0x2c0bc - 0x85f4
L_0002c0bc:
    .long 0xffff1ff4
    .org 0x2c0c0 - 0x85f4
L_0002c0c0:
    .long 0x00054d3e
    .org 0x2c0c4 - 0x85f4
L_0002c0c4:
    .long 0xffff128c
    .org 0x2c0c8 - 0x85f4
L_0002c0c8:
    .long 0xffff22dc
    .org 0x2c0cc - 0x85f4
L_0002c0cc:
    .long 0x00008d92
    .org 0x2c13c - 0x85f4
L_0002c13c:
    mov.l r8,@-r15
    .org 0x2c13e - 0x85f4
L_0002c13e:
    mov.l r9,@-r15
    .org 0x2c140 - 0x85f4
L_0002c140:
    mov.l r10,@-r15
    .org 0x2c142 - 0x85f4
L_0002c142:
    mov.l r11,@-r15
    .org 0x2c144 - 0x85f4
L_0002c144:
    mov.l r12,@-r15
    .org 0x2c146 - 0x85f4
L_0002c146:
    mov.l r13,@-r15
    .org 0x2c148 - 0x85f4
L_0002c148:
    mov.l r14,@-r15
    .org 0x2c14a - 0x85f4
L_0002c14a:
    sts.l macl,@-r15
    .org 0x2c14c - 0x85f4
L_0002c14c:
    stc.l gbr,@-r15
    .org 0x2c14e - 0x85f4
L_0002c14e:
    mov.l L_0002c240,r0
    .org 0x2c150 - 0x85f4
L_0002c150:
    ldc r0,gbr
    .org 0x2c152 - 0x85f4
L_0002c152:
    add #-0xc,r15
    .org 0x2c154 - 0x85f4
L_0002c154:
    mov.l L_0002c244,r6
    .org 0x2c156 - 0x85f4
L_0002c156:
    mov r5,r14
    .org 0x2c158 - 0x85f4
L_0002c158:
    mov.b @r6,r0
    .org 0x2c15a - 0x85f4
L_0002c15a:
    tst #0x80,r0
    .org 0x2c15c - 0x85f4
L_0002c15c:
    bt/s L_0002c21e
    .org 0x2c15e - 0x85f4
L_0002c15e:
    mov r4,r11
    .org 0x2c160 - 0x85f4
L_0002c160:
    mov.w L_0002c234,r12
    .org 0x2c162 - 0x85f4
L_0002c162:
    mov #-0x1,r8
    .org 0x2c164 - 0x85f4
L_0002c164:
    extu.w r8,r8
    .org 0x2c166 - 0x85f4
L_0002c166:
    mov.w L_0002c238,r9
    .org 0x2c168 - 0x85f4
L_0002c168:
    mov r12,r10
    .org 0x2c16a - 0x85f4
L_0002c16a:
    mov #0x1,r2
    .org 0x2c16c - 0x85f4
L_0002c16c:
    mov #0x6,r13
    .org 0x2c16e - 0x85f4
L_0002c16e:
    extu.b r2,r2
    .org 0x2c170 - 0x85f4
L_0002c170:
    extu.b r11,r11
    .org 0x2c172 - 0x85f4
L_0002c172:
    tst r2,r11
    .org 0x2c174 - 0x85f4
L_0002c174:
    bt L_0002c20e
    .org 0x2c176 - 0x85f4
L_0002c176:
    mov.l L_0002c248,r3
    .org 0x2c178 - 0x85f4
L_0002c178:
    mov.b @(0x4,r3),r0
    .org 0x2c17a - 0x85f4
L_0002c17a:
    tst r11,r0
    .org 0x2c17c - 0x85f4
L_0002c17c:
    bf/s L_0002c18a
    .org 0x2c17e - 0x85f4
L_0002c17e:
    mov.w @r14,r4
    .org 0x2c180 - 0x85f4
L_0002c180:
    mov.l L_0002c24c,r3
    .org 0x2c182 - 0x85f4
L_0002c182:
    mov.w L_0002c23a,r0
    .org 0x2c184 - 0x85f4
L_0002c184:
    mov.b @(r0,r3),r6
    .org 0x2c186 - 0x85f4
L_0002c186:
    tst r11,r6
    .org 0x2c188 - 0x85f4
L_0002c188:
    bt L_0002c198
    .org 0x2c18a - 0x85f4
L_0002c18a:
    mov.w @(0x7a,gbr),r0
    .org 0x2c18c - 0x85f4
L_0002c18c:
    mov.l L_0002c24c,r1
    .org 0x2c18e - 0x85f4
L_0002c18e:
    mov r0,r4
    .org 0x2c190 - 0x85f4
L_0002c190:
    mov.w L_0002c23a,r0
    .org 0x2c192 - 0x85f4
L_0002c192:
    mov.b @(r0,r1),r6
    .org 0x2c194 - 0x85f4
L_0002c194:
    or r11,r6
    .org 0x2c196 - 0x85f4
L_0002c196:
    mov.b r6,@(r0,r1)
    .org 0x2c198 - 0x85f4
L_0002c198:
    mov #0x26,r0
    .org 0x2c19a - 0x85f4
L_0002c19a:
    mov.w @(r0,r10),r5
    .org 0x2c19c - 0x85f4
L_0002c19c:
    tst r2,r5
    .org 0x2c19e - 0x85f4
L_0002c19e:
    bt L_0002c1b2
    .org 0x2c1a0 - 0x85f4
L_0002c1a0:
    mov.w @(0x7a,gbr),r0
    .org 0x2c1a2 - 0x85f4
L_0002c1a2:
    extu.w r4,r5
    .org 0x2c1a4 - 0x85f4
L_0002c1a4:
    extu.w r0,r7
    .org 0x2c1a6 - 0x85f4
L_0002c1a6:
    cmp/ge r7,r5
    .org 0x2c1a8 - 0x85f4
L_0002c1a8:
    bt L_0002c1ae
    .org 0x2c1aa - 0x85f4
L_0002c1aa:
    bra L_0002c1b0
    .org 0x2c1ac - 0x85f4
L_0002c1ac:
    mov #0x0,r5
    .org 0x2c1ae - 0x85f4
L_0002c1ae:
    sub r7,r5
    .org 0x2c1b0 - 0x85f4
L_0002c1b0:
    mov r5,r4
    .org 0x2c1b2 - 0x85f4
L_0002c1b2:
    mov.w L_0002c23c,r5
    .org 0x2c1b4 - 0x85f4
L_0002c1b4:
    extu.w r4,r4
    .org 0x2c1b6 - 0x85f4
L_0002c1b6:
    mul.l r4,r5
    .org 0x2c1b8 - 0x85f4
L_0002c1b8:
    sts macl,r6
    .org 0x2c1ba - 0x85f4
L_0002c1ba:
    shlr8 r6
    .org 0x2c1bc - 0x85f4
L_0002c1bc:
    swap.w r6,r5
    .org 0x2c1be - 0x85f4
L_0002c1be:
    exts.b r5,r6
    .org 0x2c1c0 - 0x85f4
L_0002c1c0:
    xtrct r6,r5
    .org 0x2c1c2 - 0x85f4
L_0002c1c2:
    cmp/hi r8,r5
    .org 0x2c1c4 - 0x85f4
L_0002c1c4:
    bf L_0002c1c8
    .org 0x2c1c6 - 0x85f4
L_0002c1c6:
    mov r8,r5
    .org 0x2c1c8 - 0x85f4
L_0002c1c8:
    mov r5,r4
    .org 0x2c1ca - 0x85f4
L_0002c1ca:
    mov r5,r0
    .org 0x2c1cc - 0x85f4
L_0002c1cc:
    mov.l L_0002c250,r5
    .org 0x2c1ce - 0x85f4
L_0002c1ce:
    mov.w r0,@(0x8,r15)
    .org 0x2c1d0 - 0x85f4
L_0002c1d0:
    mov.b @(0x5,r5),r0
    .org 0x2c1d2 - 0x85f4
L_0002c1d2:
    tst #0x1,r0
    .org 0x2c1d4 - 0x85f4
L_0002c1d4:
    bt L_0002c1dc
    .org 0x2c1d6 - 0x85f4
L_0002c1d6:
    mov.w L_0002c23e,r4
    .org 0x2c1d8 - 0x85f4
L_0002c1d8:
    mov r4,r0
    .org 0x2c1da - 0x85f4
L_0002c1da:
    mov.w r0,@(0x8,r15)
    .org 0x2c1dc - 0x85f4
L_0002c1dc:
    stc sr,r0
    .org 0x2c1de - 0x85f4
L_0002c1de:
    shlr2 r0
    .org 0x2c1e0 - 0x85f4
L_0002c1e0:
    shlr2 r0
    .org 0x2c1e2 - 0x85f4
L_0002c1e2:
    and #0xf,r0
    .org 0x2c1e4 - 0x85f4
L_0002c1e4:
    mov r0,r6
    .org 0x2c1e6 - 0x85f4
L_0002c1e6:
    stc sr,r0
    .org 0x2c1e8 - 0x85f4
L_0002c1e8:
    and r9,r0
    .org 0x2c1ea - 0x85f4
L_0002c1ea:
    or #0xf0,r0
    .org 0x2c1ec - 0x85f4
L_0002c1ec:
    ldc r0,sr
    .org 0x2c1ee - 0x85f4
L_0002c1ee:
    mov.w @r12,r5
    .org 0x2c1f0 - 0x85f4
L_0002c1f0:
    mov r6,r0
    .org 0x2c1f2 - 0x85f4
L_0002c1f2:
    and #0xf,r0
    .org 0x2c1f4 - 0x85f4
L_0002c1f4:
    add r4,r5
    .org 0x2c1f6 - 0x85f4
L_0002c1f6:
    mov.w r5,@r12
    .org 0x2c1f8 - 0x85f4
L_0002c1f8:
    mov r0,r5
    .org 0x2c1fa - 0x85f4
L_0002c1fa:
    shll2 r5
    .org 0x2c1fc - 0x85f4
L_0002c1fc:
    shll2 r5
    .org 0x2c1fe - 0x85f4
L_0002c1fe:
    stc sr,r6
    .org 0x2c200 - 0x85f4
L_0002c200:
    and r9,r6
    .org 0x2c202 - 0x85f4
L_0002c202:
    or r5,r6
    .org 0x2c204 - 0x85f4
L_0002c204:
    ldc r6,sr
    .org 0x2c206 - 0x85f4
L_0002c206:
    mov #0x26,r0
    .org 0x2c208 - 0x85f4
L_0002c208:
    mov.w @(r0,r10),r6
    .org 0x2c20a - 0x85f4
L_0002c20a:
    or r2,r6
    .org 0x2c20c - 0x85f4
L_0002c20c:
    mov.w r6,@(r0,r10)
    .org 0x2c20e - 0x85f4
L_0002c20e:
    add #0x2,r12
    .org 0x2c210 - 0x85f4
L_0002c210:
    shll r2
    .org 0x2c212 - 0x85f4
L_0002c212:
    mov.l r12,@r15
    .org 0x2c214 - 0x85f4
L_0002c214:
    dt r13
    .org 0x2c216 - 0x85f4
L_0002c216:
    mov r2,r0
    .org 0x2c218 - 0x85f4
L_0002c218:
    add #0x2,r14
    .org 0x2c21a - 0x85f4
L_0002c21a:
    bf/s L_0002c16e
    .org 0x2c21c - 0x85f4
L_0002c21c:
    mov.b r0,@(0x4,r15)
    .org 0x2c21e - 0x85f4
L_0002c21e:
    add #0xc,r15
    .org 0x2c220 - 0x85f4
L_0002c220:
    ldc.l @r15+,gbr
    .org 0x2c222 - 0x85f4
L_0002c222:
    lds.l @r15+,macl
    .org 0x2c224 - 0x85f4
L_0002c224:
    mov.l @r15+,r14
    .org 0x2c226 - 0x85f4
L_0002c226:
    mov.l @r15+,r13
    .org 0x2c228 - 0x85f4
L_0002c228:
    mov.l @r15+,r12
    .org 0x2c22a - 0x85f4
L_0002c22a:
    mov.l @r15+,r11
    .org 0x2c22c - 0x85f4
L_0002c22c:
    mov.l @r15+,r10
    .org 0x2c22e - 0x85f4
L_0002c22e:
    mov.l @r15+,r9
    .org 0x2c230 - 0x85f4
L_0002c230:
    rts
    .org 0x2c232 - 0x85f4
L_0002c232:
    mov.l @r15+,r8
    .org 0x2c234 - 0x85f4
L_0002c234:
    .word 0xf640
    .org 0x2c238 - 0x85f4
L_0002c238:
    .word 0xff0f
    .org 0x2c23a - 0x85f4
L_0002c23a:
    .word 0x06a9
    .org 0x2c23c - 0x85f4
L_0002c23c:
    .word 0x0320
    .org 0x2c23e - 0x85f4
L_0002c23e:
    .word 0x03e8
    .org 0x2c240 - 0x85f4
L_0002c240:
    .long 0xffff2330
    .org 0x2c244 - 0x85f4
L_0002c244:
    .long 0xffff4184
    .org 0x2c248 - 0x85f4
L_0002c248:
    .long 0xffff22dc
    .org 0x2c24c - 0x85f4
L_0002c24c:
    .long 0xffff128c
    .org 0x2c250 - 0x85f4
L_0002c250:
    .long 0xffff424c
    .org 0x54d3e - 0x85f4
L_00054d3e:
    mov.l r14,@-r15
    .org 0x54d40 - 0x85f4
L_00054d40:
    sts.l pr,@-r15
    .org 0x54d42 - 0x85f4
L_00054d42:
    sts.l macl,@-r15
    .org 0x54d44 - 0x85f4
L_00054d44:
    stc.l gbr,@-r15
    .org 0x54d46 - 0x85f4
L_00054d46:
    mov.l L_00054ea4,r0
    .org 0x54d48 - 0x85f4
L_00054d48:
    ldc r0,gbr
    .org 0x54d4a - 0x85f4
L_00054d4a:
    add #-0x4,r15
    .org 0x54d4c - 0x85f4
L_00054d4c:
    mov.l L_00054ea8,r6
    .org 0x54d4e - 0x85f4
L_00054d4e:
    mov.b @(0x4,r6),r0
    .org 0x54d50 - 0x85f4
L_00054d50:
    tst #0x2,r0
    .org 0x54d52 - 0x85f4
L_00054d52:
    bt/s L_00054d5a
    .org 0x54d54 - 0x85f4
L_00054d54:
    extu.b r4,r4
    .org 0x54d56 - 0x85f4
L_00054d56:
    bra L_00054e5a
    .org 0x54d58 - 0x85f4
L_00054d58:
    nop
    .org 0x54d5a - 0x85f4
L_00054d5a:
    mov.l L_00054eac,r6
    .org 0x54d5c - 0x85f4
L_00054d5c:
    mov #0x30,r0
    .org 0x54d5e - 0x85f4
L_00054d5e:
    mov.b @(r0,r6),r0
    .org 0x54d60 - 0x85f4
L_00054d60:
    tst #0x40,r0
    .org 0x54d62 - 0x85f4
L_00054d62:
    bf L_00054e5a
    .org 0x54d64 - 0x85f4
L_00054d64:
    tst r4,r4
    .org 0x54d66 - 0x85f4
L_00054d66:
    bf L_00054d80
    .org 0x54d68 - 0x85f4
L_00054d68:
    mov.l L_00054e8c,r2
    .org 0x54d6a - 0x85f4
L_00054d6a:
    mov #0x6,r6
    .org 0x54d6c - 0x85f4
L_00054d6c:
    mov.w L_00054dcc,r5
    .org 0x54d6e - 0x85f4
L_00054d6e:
    mov.w @(0x5a,gbr),r0
    .org 0x54d70 - 0x85f4
L_00054d70:
    add r5,r2
    .org 0x54d72 - 0x85f4
L_00054d72:
    mov r0,r5
    .org 0x54d74 - 0x85f4
L_00054d74:
    dt r6
    .org 0x54d76 - 0x85f4
L_00054d76:
    mov.w r5,@r2
    .org 0x54d78 - 0x85f4
L_00054d78:
    bf/s L_00054d74
    .org 0x54d7a - 0x85f4
L_00054d7a:
    add #0x2,r2
    .org 0x54d7c - 0x85f4
L_00054d7c:
    bra L_00054e6e
    .org 0x54d7e - 0x85f4
L_00054d7e:
    nop
    .org 0x54d80 - 0x85f4
L_00054d80:
    mov r4,r0
    .org 0x54d82 - 0x85f4
L_00054d82:
    cmp/eq #0x1,r0
    .org 0x54d84 - 0x85f4
L_00054d84:
    bt L_00054dd0
    .org 0x54d86 - 0x85f4
L_00054d86:
    cmp/eq #0x2,r0
    .org 0x54d88 - 0x85f4
L_00054d88:
    bt L_00054dd0
    .org 0x54d8a - 0x85f4
L_00054d8a:
    mov r4,r0
    .org 0x54d8c - 0x85f4
L_00054d8c:
    cmp/eq #0x4,r0
    .org 0x54d8e - 0x85f4
L_00054d8e:
    bt L_00054dd0
    .org 0x54d90 - 0x85f4
L_00054d90:
    mov.w @(0x60,gbr),r0
    .org 0x54d92 - 0x85f4
L_00054d92:
    mov #0x6,r7
    .org 0x54d94 - 0x85f4
L_00054d94:
    mov.l L_00054e8c,r5
    .org 0x54d96 - 0x85f4
L_00054d96:
    extu.w r0,r2
    .org 0x54d98 - 0x85f4
L_00054d98:
    mov.l r2,@r15
    .org 0x54d9a - 0x85f4
L_00054d9a:
    mov.w L_00054dcc,r2
    .org 0x54d9c - 0x85f4
L_00054d9c:
    stc gbr,r4
    .org 0x54d9e - 0x85f4
L_00054d9e:
    add r2,r5
    .org 0x54da0 - 0x85f4
L_00054da0:
    mov.l @r15,r14
    .org 0x54da2 - 0x85f4
L_00054da2:
    add #0x18,r4
    .org 0x54da4 - 0x85f4
L_00054da4:
    mov.w @r4,r2
    .org 0x54da6 - 0x85f4
L_00054da6:
    extu.w r2,r2
    .org 0x54da8 - 0x85f4
L_00054da8:
    cmp/ge r14,r2
    .org 0x54daa - 0x85f4
L_00054daa:
    bt L_00054db0
    .org 0x54dac - 0x85f4
L_00054dac:
    mov.w @(0x60,gbr),r0
    .org 0x54dae - 0x85f4
L_00054dae:
    mov r0,r2
    .org 0x54db0 - 0x85f4
L_00054db0:
    dt r7
    .org 0x54db2 - 0x85f4
L_00054db2:
    mov.w r2,@r5
    .org 0x54db4 - 0x85f4
L_00054db4:
    add #0x2,r4
    .org 0x54db6 - 0x85f4
L_00054db6:
    bf/s L_00054da4
    .org 0x54db8 - 0x85f4
L_00054db8:
    add #0x2,r5
    .org 0x54dba - 0x85f4
L_00054dba:
    bra L_00054e6e
    .org 0x54dbc - 0x85f4
L_00054dbc:
    nop
    .org 0x54dcc - 0x85f4
L_00054dcc:
    .word 0x025a
    .org 0x54dd0 - 0x85f4
L_00054dd0:
    mov.l L_00054eb0,r5
    .org 0x54dd2 - 0x85f4
L_00054dd2:
    mov.w @(0x7a,gbr),r0
    .org 0x54dd4 - 0x85f4
L_00054dd4:
    mov.w @r5,r2
    .org 0x54dd6 - 0x85f4
L_00054dd6:
    extu.w r2,r2
    .org 0x54dd8 - 0x85f4
L_00054dd8:
    mov #0x64,r6
    .org 0x54dda - 0x85f4
L_00054dda:
    mul.l r2,r6
    .org 0x54ddc - 0x85f4
L_00054ddc:
    sts macl,r2
    .org 0x54dde - 0x85f4
L_00054dde:
    cmp/pz r2
    .org 0x54de0 - 0x85f4
L_00054de0:
    bt/s L_00054dea
    .org 0x54de2 - 0x85f4
L_00054de2:
    extu.w r0,r5
    .org 0x54de4 - 0x85f4
L_00054de4:
    mov #-0x1,r6
    .org 0x54de6 - 0x85f4
L_00054de6:
    extu.b r6,r6
    .org 0x54de8 - 0x85f4
L_00054de8:
    add r6,r2
    .org 0x54dea - 0x85f4
L_00054dea:
    mov r2,r6
    .org 0x54dec - 0x85f4
L_00054dec:
    shlr8 r6
    .org 0x54dee - 0x85f4
L_00054dee:
    swap.w r6,r2
    .org 0x54df0 - 0x85f4
L_00054df0:
    exts.b r2,r6
    .org 0x54df2 - 0x85f4
L_00054df2:
    xtrct r6,r2
    .org 0x54df4 - 0x85f4
L_00054df4:
    add r2,r5
    .org 0x54df6 - 0x85f4
L_00054df6:
    mov #-0x1,r2
    .org 0x54df8 - 0x85f4
L_00054df8:
    extu.w r2,r2
    .org 0x54dfa - 0x85f4
L_00054dfa:
    cmp/hi r2,r5
    .org 0x54dfc - 0x85f4
L_00054dfc:
    bf L_00054e00
    .org 0x54dfe - 0x85f4
L_00054dfe:
    mov r2,r5
    .org 0x54e00 - 0x85f4
L_00054e00:
    mov.w @(0x58,gbr),r0
    .org 0x54e02 - 0x85f4
L_00054e02:
    extu.w r0,r6
    .org 0x54e04 - 0x85f4
L_00054e04:
    mov.w @(0x56,gbr),r0
    .org 0x54e06 - 0x85f4
L_00054e06:
    cmp/hi r5,r6
    .org 0x54e08 - 0x85f4
L_00054e08:
    bf/s L_00054e18
    .org 0x54e0a - 0x85f4
L_00054e0a:
    extu.w r0,r5
    .org 0x54e0c - 0x85f4
L_00054e0c:
    mov.w @(0x5a,gbr),r0
    .org 0x54e0e - 0x85f4
L_00054e0e:
    extu.w r0,r2
    .org 0x54e10 - 0x85f4
L_00054e10:
    sub r2,r5
    .org 0x54e12 - 0x85f4
L_00054e12:
    cmp/pz r5
    .org 0x54e14 - 0x85f4
L_00054e14:
    bt L_00054e18
    .org 0x54e16 - 0x85f4
L_00054e16:
    mov #0x0,r5
    .org 0x54e18 - 0x85f4
L_00054e18:
    mov r4,r0
    .org 0x54e1a - 0x85f4
L_00054e1a:
    cmp/eq #0x1,r0
    .org 0x54e1c - 0x85f4
L_00054e1c:
    bf L_00054e2a
    .org 0x54e1e - 0x85f4
L_00054e1e:
    mov.w @(0x5c,gbr),r0
    .org 0x54e20 - 0x85f4
L_00054e20:
    extu.w r0,r6
    .org 0x54e22 - 0x85f4
L_00054e22:
    cmp/ge r6,r5
    .org 0x54e24 - 0x85f4
L_00054e24:
    bf L_00054e44
    .org 0x54e26 - 0x85f4
L_00054e26:
    bra L_00054e46
    .org 0x54e28 - 0x85f4
L_00054e28:
    nop
    .org 0x54e2a - 0x85f4
L_00054e2a:
    mov r4,r0
    .org 0x54e2c - 0x85f4
L_00054e2c:
    cmp/eq #0x2,r0
    .org 0x54e2e - 0x85f4
L_00054e2e:
    bf L_00054e3c
    .org 0x54e30 - 0x85f4
L_00054e30:
    mov.w @(0x5e,gbr),r0
    .org 0x54e32 - 0x85f4
L_00054e32:
    extu.w r0,r6
    .org 0x54e34 - 0x85f4
L_00054e34:
    cmp/ge r6,r5
    .org 0x54e36 - 0x85f4
L_00054e36:
    bf L_00054e44
    .org 0x54e38 - 0x85f4
L_00054e38:
    bra L_00054e46
    .org 0x54e3a - 0x85f4
L_00054e3a:
    nop
    .org 0x54e3c - 0x85f4
L_00054e3c:
    mov.w @(0x62,gbr),r0
    .org 0x54e3e - 0x85f4
L_00054e3e:
    extu.w r0,r6
    .org 0x54e40 - 0x85f4
L_00054e40:
    cmp/ge r6,r5
    .org 0x54e42 - 0x85f4
L_00054e42:
    bt L_00054e46
    .org 0x54e44 - 0x85f4
L_00054e44:
    mov r6,r5
    .org 0x54e46 - 0x85f4
L_00054e46:
    mov.l L_00054e8c,r2
    .org 0x54e48 - 0x85f4
L_00054e48:
    mov #0x6,r6
    .org 0x54e4a - 0x85f4
L_00054e4a:
    mov.w L_00054e88,r4
    .org 0x54e4c - 0x85f4
L_00054e4c:
    add r4,r2
    .org 0x54e4e - 0x85f4
L_00054e4e:
    dt r6
    .org 0x54e50 - 0x85f4
L_00054e50:
    mov.w r5,@r2
    .org 0x54e52 - 0x85f4
L_00054e52:
    bf/s L_00054e4e
    .org 0x54e54 - 0x85f4
L_00054e54:
    add #0x2,r2
    .org 0x54e56 - 0x85f4
L_00054e56:
    bra L_00054e6e
    .org 0x54e58 - 0x85f4
L_00054e58:
    nop
    .org 0x54e5a - 0x85f4
L_00054e5a:
    mov.l L_00054e8c,r2
    .org 0x54e5c - 0x85f4
L_00054e5c:
    mov #0x6,r6
    .org 0x54e5e - 0x85f4
L_00054e5e:
    mov.w L_00054e88,r5
    .org 0x54e60 - 0x85f4
L_00054e60:
    mov.w @(0x7a,gbr),r0
    .org 0x54e62 - 0x85f4
L_00054e62:
    add r5,r2
    .org 0x54e64 - 0x85f4
L_00054e64:
    mov r0,r5
    .org 0x54e66 - 0x85f4
L_00054e66:
    dt r6
    .org 0x54e68 - 0x85f4
L_00054e68:
    mov.w r5,@r2
    .org 0x54e6a - 0x85f4
L_00054e6a:
    bf/s L_00054e66
    .org 0x54e6c - 0x85f4
L_00054e6c:
    add #0x2,r2
    .org 0x54e6e - 0x85f4
L_00054e6e:
    mov.l L_00054e94,r6
    .org 0x54e70 - 0x85f4
L_00054e70:
    mov.b @r6,r0
    .org 0x54e72 - 0x85f4
L_00054e72:
    tst #0x8,r0
    .org 0x54e74 - 0x85f4
L_00054e74:
    bt L_00054e7c
    .org 0x54e76 - 0x85f4
L_00054e76:
    mov.l L_00054eb4,r2
    .org 0x54e78 - 0x85f4
L_00054e78:
    jsr @r2
    .org 0x54e7a - 0x85f4
L_00054e7a:
    nop
    .org 0x54e7c - 0x85f4
L_00054e7c:
    add #0x4,r15
    .org 0x54e7e - 0x85f4
L_00054e7e:
    ldc.l @r15+,gbr
    .org 0x54e80 - 0x85f4
L_00054e80:
    lds.l @r15+,macl
    .org 0x54e82 - 0x85f4
L_00054e82:
    lds.l @r15+,pr
    .org 0x54e84 - 0x85f4
L_00054e84:
    rts
    .org 0x54e86 - 0x85f4
L_00054e86:
    mov.l @r15+,r14
    .org 0x54e88 - 0x85f4
L_00054e88:
    .word 0x025a
    .org 0x54e8c - 0x85f4
L_00054e8c:
    .long 0xffff1ff4
    .org 0x54e94 - 0x85f4
L_00054e94:
    .long 0x00008d92
    .org 0x54ea4 - 0x85f4
L_00054ea4:
    .long 0xffff2330
    .org 0x54ea8 - 0x85f4
L_00054ea8:
    .long 0xffff4188
    .org 0x54eac - 0x85f4
L_00054eac:
    .long 0xffff2470
    .org 0x54eb0 - 0x85f4
L_00054eb0:
    .long 0x000094e8
    .org 0x54eb4 - 0x85f4
L_00054eb4:
    .long 0x000571c0
    .org 0x571c0 - 0x85f4
L_000571c0:
    mov.l r8,@-r15
    .org 0x571c2 - 0x85f4
L_000571c2:
    mov.l r9,@-r15
    .org 0x571c4 - 0x85f4
L_000571c4:
    mov.l r10,@-r15
    .org 0x571c6 - 0x85f4
L_000571c6:
    mov.l r11,@-r15
    .org 0x571c8 - 0x85f4
L_000571c8:
    mov.l r12,@-r15
    .org 0x571ca - 0x85f4
L_000571ca:
    mov.l r13,@-r15
    .org 0x571cc - 0x85f4
L_000571cc:
    mov.l r14,@-r15
    .org 0x571ce - 0x85f4
L_000571ce:
    sts.l pr,@-r15
    .org 0x571d0 - 0x85f4
L_000571d0:
    sts.l macl,@-r15
    .org 0x571d2 - 0x85f4
L_000571d2:
    stc.l gbr,@-r15
    .org 0x571d4 - 0x85f4
L_000571d4:
    mov.l L_00057354,r0
    .org 0x571d6 - 0x85f4
L_000571d6:
    ldc r0,gbr
    .org 0x571d8 - 0x85f4
L_000571d8:
    mov.l L_00057358,r2
    .org 0x571da - 0x85f4
L_000571da:
    mov #0x0,r14
    .org 0x571dc - 0x85f4
L_000571dc:
    mov.w L_0005729c,r0
    .org 0x571de - 0x85f4
L_000571de:
    mov #0x1,r10
    .org 0x571e0 - 0x85f4
L_000571e0:
    mov.l L_0005735c,r11
    .org 0x571e2 - 0x85f4
L_000571e2:
    mov #0x6,r9
    .org 0x571e4 - 0x85f4
L_000571e4:
    mov.b @(r0,r2),r13
    .org 0x571e6 - 0x85f4
L_000571e6:
    mov #0x12,r0
    .org 0x571e8 - 0x85f4
L_000571e8:
    mov.l L_00057360,r2
    .org 0x571ea - 0x85f4
L_000571ea:
    mov.w L_0005729e,r8
    .org 0x571ec - 0x85f4
L_000571ec:
    mov.b @(r0,r2),r12
    .org 0x571ee - 0x85f4
L_000571ee:
    extu.b r14,r14
    .org 0x571f0 - 0x85f4
L_000571f0:
    mov r10,r0
    .org 0x571f2 - 0x85f4
L_000571f2:
    mov r14,r1
    .org 0x571f4 - 0x85f4
L_000571f4:
    jsr @r11
    .org 0x571f6 - 0x85f4
L_000571f6:
    extu.b r13,r13
    .org 0x571f8 - 0x85f4
L_000571f8:
    extu.b r0,r2
    .org 0x571fa - 0x85f4
L_000571fa:
    tst r2,r13
    .org 0x571fc - 0x85f4
L_000571fc:
    bt L_0005725c
    .org 0x571fe - 0x85f4
L_000571fe:
    stc gbr,r6
    .org 0x57200 - 0x85f4
L_00057200:
    extu.b r12,r12
    .org 0x57202 - 0x85f4
L_00057202:
    mov r14,r4
    .org 0x57204 - 0x85f4
L_00057204:
    shll r4
    .org 0x57206 - 0x85f4
L_00057206:
    tst r2,r12
    .org 0x57208 - 0x85f4
L_00057208:
    add r8,r6
    .org 0x5720a - 0x85f4
L_0005720a:
    mov r4,r0
    .org 0x5720c - 0x85f4
L_0005720c:
    mov #0x0,r5
    .org 0x5720e - 0x85f4
L_0005720e:
    bf/s L_0005725c
    .org 0x57210 - 0x85f4
L_00057210:
    mov.w r5,@(r0,r6)
    .org 0x57212 - 0x85f4
L_00057212:
    mov.l L_00057364,r3
    .org 0x57214 - 0x85f4
L_00057214:
    mov.l L_00057354,r5
    .org 0x57216 - 0x85f4
L_00057216:
    mov.b @(0x4,r3),r0
    .org 0x57218 - 0x85f4
L_00057218:
    tst r2,r0
    .org 0x5721a - 0x85f4
L_0005721a:
    bt L_0005724e
    .org 0x5721c - 0x85f4
L_0005721c:
    mov.w L_000572a0,r7
    .org 0x5721e - 0x85f4
L_0005721e:
    mov r5,r2
    .org 0x57220 - 0x85f4
L_00057220:
    mov.l L_00057368,r3
    .org 0x57222 - 0x85f4
L_00057222:
    mov r4,r0
    .org 0x57224 - 0x85f4
L_00057224:
    add r7,r2
    .org 0x57226 - 0x85f4
L_00057226:
    mov.w @(r0,r2),r6
    .org 0x57228 - 0x85f4
L_00057228:
    mov.b @r3,r2
    .org 0x5722a - 0x85f4
L_0005722a:
    extu.w r6,r6
    .org 0x5722c - 0x85f4
L_0005722c:
    extu.b r2,r1
    .org 0x5722e - 0x85f4
L_0005722e:
    mul.l r6,r1
    .org 0x57230 - 0x85f4
L_00057230:
    sts macl,r2
    .org 0x57232 - 0x85f4
L_00057232:
    cmp/pz r2
    .org 0x57234 - 0x85f4
L_00057234:
    bt L_0005723c
    .org 0x57236 - 0x85f4
L_00057236:
    mov #-0x1,r6
    .org 0x57238 - 0x85f4
L_00057238:
    extu.b r6,r6
    .org 0x5723a - 0x85f4
L_0005723a:
    add r6,r2
    .org 0x5723c - 0x85f4
L_0005723c:
    mov r2,r6
    .org 0x5723e - 0x85f4
L_0005723e:
    shlr8 r6
    .org 0x57240 - 0x85f4
L_00057240:
    swap.w r6,r2
    .org 0x57242 - 0x85f4
L_00057242:
    mov r4,r0
    .org 0x57244 - 0x85f4
L_00057244:
    exts.b r2,r6
    .org 0x57246 - 0x85f4
L_00057246:
    xtrct r6,r2
    .org 0x57248 - 0x85f4
L_00057248:
    add r7,r5
    .org 0x5724a - 0x85f4
L_0005724a:
    bra L_0005725c
    .org 0x5724c - 0x85f4
L_0005724c:
    mov.w r2,@(r0,r5)
    .org 0x5724e - 0x85f4
L_0005724e:
    mov.l L_0005736c,r2
    .org 0x57250 - 0x85f4
L_00057250:
    mov r4,r0
    .org 0x57252 - 0x85f4
L_00057252:
    mov.w L_000572a0,r7
    .org 0x57254 - 0x85f4
L_00057254:
    add #0x68,r2
    .org 0x57256 - 0x85f4
L_00057256:
    mov.w @(r0,r2),r6
    .org 0x57258 - 0x85f4
L_00057258:
    add r7,r5
    .org 0x5725a - 0x85f4
L_0005725a:
    mov.w r6,@(r0,r5)
    .org 0x5725c - 0x85f4
L_0005725c:
    add #0x1,r14
    .org 0x5725e - 0x85f4
L_0005725e:
    extu.b r14,r14
    .org 0x57260 - 0x85f4
L_00057260:
    cmp/ge r9,r14
    .org 0x57262 - 0x85f4
L_00057262:
    bf L_000571ee
    .org 0x57264 - 0x85f4
L_00057264:
    ldc.l @r15+,gbr
    .org 0x57266 - 0x85f4
L_00057266:
    lds.l @r15+,macl
    .org 0x57268 - 0x85f4
L_00057268:
    lds.l @r15+,pr
    .org 0x5726a - 0x85f4
L_0005726a:
    mov.l @r15+,r14
    .org 0x5726c - 0x85f4
L_0005726c:
    mov.l @r15+,r13
    .org 0x5726e - 0x85f4
L_0005726e:
    mov.l @r15+,r12
    .org 0x57270 - 0x85f4
L_00057270:
    mov.l @r15+,r11
    .org 0x57272 - 0x85f4
L_00057272:
    mov.l @r15+,r10
    .org 0x57274 - 0x85f4
L_00057274:
    mov.l @r15+,r9
    .org 0x57276 - 0x85f4
L_00057276:
    rts
    .org 0x57278 - 0x85f4
L_00057278:
    mov.l @r15+,r8
    .org 0x5729c - 0x85f4
L_0005729c:
    .word 0x0234
    .org 0x5729e - 0x85f4
L_0005729e:
    .word 0x01da
    .org 0x572a0 - 0x85f4
L_000572a0:
    .word 0x06d2
    .org 0x57354 - 0x85f4
L_00057354:
    .long 0xffff128c
    .org 0x57358 - 0x85f4
L_00057358:
    .long 0xffff1ff4
    .org 0x5735c - 0x85f4
L_0005735c:
    .long 0x000221bc
    .org 0x57360 - 0x85f4
L_00057360:
    .long 0xffff120e
    .org 0x57364 - 0x85f4
L_00057364:
    .long 0xffff22dc
    .org 0x57368 - 0x85f4
L_00057368:
    .long 0x000085f7
    .org 0x5736c - 0x85f4
L_0005736c:
    .long 0xffff2330
