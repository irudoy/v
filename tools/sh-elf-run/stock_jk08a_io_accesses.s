! Exact bounded mailbox writes, descriptor stride/read and captured input formation.
    .text
    .balign 4
    .set ORIGIN,0x2040
    .org 0x2040-ORIGIN
L_00002040:
    mov.l r14,@-r15
    .org 0x2042-ORIGIN
L_00002042:
    sts.l pr,@-r15
    .org 0x2044-ORIGIN
L_00002044:
    add #-0xc,r15
    .org 0x2046-ORIGIN
L_00002046:
    mov.w L_00002198,r2
    .org 0x2048-ORIGIN
L_00002048:
    extu.w r4,r14
    .org 0x204a-ORIGIN
L_0000204a:
    mov #0x4,r5
    .org 0x204c-ORIGIN
L_0000204c:
    mov r15,r4
    .org 0x204e-ORIGIN
L_0000204e:
    mov.l @(0x10,r2),r0
    .org 0x2050-ORIGIN
L_00002050:
    mov r14,r2
    .org 0x2052-ORIGIN
L_00002052:
    shll16 r2
    .org 0x2054-ORIGIN
L_00002054:
    extu.w r0,r6
    .org 0x2056-ORIGIN
L_00002056:
    mov.w r0,@(0x4,r15)
    .org 0x2058-ORIGIN
L_00002058:
    add r6,r2
    .org 0x205a-ORIGIN
L_0000205a:
    .org 0x2198-ORIGIN
L_00002198:
    .word 0xf420
    .org 0xa6dc8-ORIGIN
L_000a6dc8:
    mov.l L_000a701c,r0
    .org 0xa6dca-ORIGIN
L_000a6dca:
    ldc r0,gbr
    .org 0xa6dcc-ORIGIN
L_000a6dcc:
    add #-0x8,r15
    .org 0xa6dce-ORIGIN
L_000a6dce:
    mov r4,r0
    .org 0xa6dd0-ORIGIN
L_000a6dd0:
    shll2 r0
    .org 0xa6dd2-ORIGIN
L_000a6dd2:
    shll r0
    .org 0xa6dd4-ORIGIN
L_000a6dd4:
    sub r4,r0
    .org 0xa6dd6-ORIGIN
L_000a6dd6:
    shll2 r0
    .org 0xa6dd8-ORIGIN
L_000a6dd8:
    stc gbr,r6
    .org 0xa6dda-ORIGIN
L_000a6dda:
    shll r0
    .org 0xa6ddc-ORIGIN
L_000a6ddc:
    mov.l @(r0,r6),r2
    .org 0xa6dde-ORIGIN
L_000a6dde:
    tst r2,r2
    .org 0xa6de0-ORIGIN
L_000a6de0:
    bf/s L_000a6de8
    .org 0xa6de2-ORIGIN
L_000a6de2:
    mov r0,r4
    .org 0xa6de8-ORIGIN
L_000a6de8:
    .org 0xa6e9e-ORIGIN
L_000a6e9e:
    stc gbr,r2
    .org 0xa6ea0-ORIGIN
L_000a6ea0:
    mov r4,r0
    .org 0xa6ea2-ORIGIN
L_000a6ea2:
    mov.l @(r0,r2),r6
    .org 0xa6ea4-ORIGIN
L_000a6ea4:
    mov.w @r6,r5
    .org 0xa6ea6-ORIGIN
L_000a6ea6:
    stc gbr,r6
    .org 0xa6ea8-ORIGIN
L_000a6ea8:
    add #0x4,r6
    .org 0xa6eaa-ORIGIN
L_000a6eaa:
    mov.w @(r0,r6),r2
    .org 0xa6eac-ORIGIN
L_000a6eac:
    extu.w r2,r2
    .org 0xa6eae-ORIGIN
L_000a6eae:
    tst r2,r5
    .org 0xa6eb0-ORIGIN
L_000a6eb0:
    .org 0xa701c-ORIGIN
L_000a701c:
    .long 0x00023ac4
    .org 0xc2fe4-ORIGIN
L_000c2fe4:
    mov.l L_000c31b4,r3
    .org 0xc2fe6-ORIGIN
L_000c2fe6:
    mov r11,r13
    .org 0xc2fe8-ORIGIN
L_000c2fe8:
    shll2 r13
    .org 0xc2fea-ORIGIN
L_000c2fea:
    mov r13,r6
    .org 0xc2fec-ORIGIN
L_000c2fec:
    add r3,r6
    .org 0xc2fee-ORIGIN
L_000c2fee:
    mov.b @r6,r2
    .org 0xc2ff0-ORIGIN
L_000c2ff0:
    extu.b r2,r0
    .org 0xc2ff2-ORIGIN
L_000c2ff2:
    cmp/eq #0x1,r0
    .org 0xc2ff4-ORIGIN
L_000c2ff4:
    bt L_000c3028
    .org 0xc2ff6-ORIGIN
L_000c2ff6:
    cmp/eq #0x2,r0
    .org 0xc2ff8-ORIGIN
L_000c2ff8:
    bt L_000c3012
    .org 0xc2ffa-ORIGIN
L_000c2ffa:
    cmp/eq #0x3,r0
    .org 0xc2ffc-ORIGIN
L_000c2ffc:
    bt L_000c300e
    .org 0xc2ffe-ORIGIN
L_000c2ffe:
    cmp/eq #0x4,r0
    .org 0xc3000-ORIGIN
L_000c3000:
    bt L_000c300a
    .org 0xc3002-ORIGIN
L_000c3002:
    cmp/eq #0x5,r0
    .org 0xc3004-ORIGIN
L_000c3004:
    bf L_000c3006
    .org 0xc3006-ORIGIN
L_000c3006:
    bra L_000c302a
    .org 0xc3008-ORIGIN
L_000c3008:
    mov #0x7,r5
    .org 0xc300a-ORIGIN
L_000c300a:
    bra L_000c3014
    .org 0xc300c-ORIGIN
L_000c300c:
    mov #0x0,r5
    .org 0xc300e-ORIGIN
L_000c300e:
    bra L_000c302a
    .org 0xc3010-ORIGIN
L_000c3010:
    mov #0x0,r5
    .org 0xc3012-ORIGIN
L_000c3012:
    mov #0x2,r5
    .org 0xc3014-ORIGIN
L_000c3014:
    bra L_000c302a
    .org 0xc3016-ORIGIN
L_000c3016:
    or r7,r9
    .org 0xc3028-ORIGIN
L_000c3028:
    mov #0x2,r5
    .org 0xc302a-ORIGIN
L_000c302a:
    mov.l L_000c31b4,r1
    .org 0xc302c-ORIGIN
L_000c302c:
    mov r13,r2
    .org 0xc302e-ORIGIN
L_000c302e:
    mov r11,r14
    .org 0xc3030-ORIGIN
L_000c3030:
    shll2 r14
    .org 0xc3032-ORIGIN
L_000c3032:
    add r1,r2
    .org 0xc3034-ORIGIN
L_000c3034:
    mov.w L_000c319e,r3
    .org 0xc3036-ORIGIN
L_000c3036:
    mov.b @(0x2,r2),r0
    .org 0xc3038-ORIGIN
L_000c3038:
    mov r13,r2
    .org 0xc303a-ORIGIN
L_000c303a:
    add r1,r2
    .org 0xc303c-ORIGIN
L_000c303c:
    extu.b r0,r6
    .org 0xc303e-ORIGIN
L_000c303e:
    mov.b @(0x3,r2),r0
    .org 0xc3040-ORIGIN
L_000c3040:
    shll2 r14
    .org 0xc3042-ORIGIN
L_000c3042:
    shll8 r6
    .org 0xc3044-ORIGIN
L_000c3044:
    shll r14
    .org 0xc3046-ORIGIN
L_000c3046:
    extu.w r6,r2
    .org 0xc3048-ORIGIN
L_000c3048:
    extu.b r0,r6
    .org 0xc304a-ORIGIN
L_000c304a:
    add r3,r14
    .org 0xc304c-ORIGIN
L_000c304c:
    mov.w L_000c31a0,r3
    .org 0xc304e-ORIGIN
L_000c304e:
    add r6,r2
    .org 0xc3050-ORIGIN
L_000c3050:
    shar r2
    .org 0xc3052-ORIGIN
L_000c3052:
    mov r2,r6
    .org 0xc3054-ORIGIN
L_000c3054:
    and r3,r2
    .org 0xc3056-ORIGIN
L_000c3056:
    mov #0x0,r3
    .org 0xc3058-ORIGIN
L_000c3058:
    mov.w r2,@r14
    .org 0xc305a-ORIGIN
L_000c305a:
    mov r3,r0
    .org 0xc305c-ORIGIN
L_000c305c:
    mov.w r0,@(0x2,r14)
    .org 0xc305e-ORIGIN
L_000c305e:
    mov r1,r2
    .org 0xc3060-ORIGIN
L_000c3060:
    add r13,r2
    .org 0xc3062-ORIGIN
L_000c3062:
    mov.b @(0x1,r2),r0
    .org 0xc3064-ORIGIN
L_000c3064:
    extu.b r5,r4
    .org 0xc3066-ORIGIN
L_000c3066:
    shll8 r4
    .org 0xc3068-ORIGIN
L_000c3068:
    extu.b r0,r5
    .org 0xc306a-ORIGIN
L_000c306a:
    add r5,r4
    .org 0xc306c-ORIGIN
L_000c306c:
    mov r4,r0
    .org 0xc306e-ORIGIN
L_000c306e:
    mov.w r0,@(0x4,r14)
    .org 0xc3070-ORIGIN
L_000c3070:
    mov r3,r0
    .org 0xc3072-ORIGIN
L_000c3072:
    mov.w r0,@(0x6,r14)
    .org 0xc3074-ORIGIN
L_000c3074:
    mov.w r0,@(0x10,r14)
    .org 0xc3076-ORIGIN
L_000c3076:
    extu.w r6,r6
    .org 0xc3078-ORIGIN
L_000c3078:
    mov.w r0,@(0x12,r14)
    .org 0xc307a-ORIGIN
L_000c307a:
    .org 0xc319e-ORIGIN
L_000c319e:
    .word 0xd920
    .org 0xc31a0-ORIGIN
L_000c31a0:
    .word 0x7ff0
    .org 0xc31b4-ORIGIN
L_000c31b4:
    .long 0x0000975a
