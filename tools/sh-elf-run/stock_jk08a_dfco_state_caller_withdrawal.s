! Complete natural DFCO state and restore callers with their real helper closures.
    .text
    .balign 4
    .set ORIGIN,0x85f4
    .org 0x85f6-ORIGIN
P_000085f6:
    .byte 0x14
    .org 0x8711-ORIGIN
P_00008711:
    .byte 0x00
    .org 0x8a40-ORIGIN
P_00008a40:
    .byte 0x04
    .org 0x8b3f-ORIGIN
P_00008b3f:
    .byte 0x18
    .org 0x8c1a-ORIGIN
P_00008c1a:
    .byte 0x05
    .org 0x8c1b-ORIGIN
P_00008c1b:
    .byte 0x04
    .org 0x8c1c-ORIGIN
P_00008c1c:
    .byte 0x00
    .org 0x8c1d-ORIGIN
P_00008c1d:
    .byte 0x00
    .org 0x8c1e-ORIGIN
P_00008c1e:
    .byte 0x70
    .org 0x25c36-ORIGIN
L_00025c36:
    mov.l P_00025d28,r1
    .org 0x25c38-ORIGIN
L_00025c38:
    exts.w r4,r0
    .org 0x25c3a-ORIGIN
L_00025c3a:
    cmp/eq #-0x1,r0
    .org 0x25c3c-ORIGIN
L_00025c3c:
    bt L_00025c54
    .org 0x25c3e-ORIGIN
L_00025c3e:
    mov r1,r6
    .org 0x25c40-ORIGIN
L_00025c40:
    mov r0,r2
    .org 0x25c42-ORIGIN
L_00025c42:
    shll r2
    .org 0x25c44-ORIGIN
L_00025c44:
    add r0,r2
    .org 0x25c46-ORIGIN
L_00025c46:
    add r2,r6
    .org 0x25c48-ORIGIN
L_00025c48:
    mov.b @(0x2,r6),r0
    .org 0x25c4a-ORIGIN
L_00025c4a:
    tst #0x20,r0
    .org 0x25c4c-ORIGIN
L_00025c4c:
    movt r0
    .org 0x25c4e-ORIGIN
L_00025c4e:
    xor #0x1,r0
    .org 0x25c50-ORIGIN
L_00025c50:
    bra L_00025c56
    .org 0x25c52-ORIGIN
L_00025c52:
    extu.b r0,r2
    .org 0x25c54-ORIGIN
L_00025c54:
    mov #0x0,r2
    .org 0x25c56-ORIGIN
L_00025c56:
    rts
    .org 0x25c58-ORIGIN
L_00025c58:
    mov r2,r0
    .org 0x25d28-ORIGIN
P_00025d28:
    .byte 0xff
    .org 0x25d29-ORIGIN
P_00025d29:
    .byte 0xff
    .org 0x25d2a-ORIGIN
P_00025d2a:
    .byte 0x57
    .org 0x25d2b-ORIGIN
P_00025d2b:
    .byte 0x18
    .org 0x26388-ORIGIN
L_00026388:
    mov.w P_0002639a,r0
    .org 0x2638a-ORIGIN
L_0002638a:
    extu.b r5,r5
    .org 0x2638c-ORIGIN
L_0002638c:
    cmp/hs r0,r5
    .org 0x2638e-ORIGIN
L_0002638e:
    bt L_00026396
    .org 0x26390-ORIGIN
L_00026390:
    mov.l P_0002639c,r6
    .org 0x26392-ORIGIN
L_00026392:
    jmp @r6
    .org 0x26394-ORIGIN
L_00026394:
    mov #0x0,r3
    .org 0x26396-ORIGIN
L_00026396:
    rts
    .org 0x26398-ORIGIN
L_00026398:
    mov.b @(0xf,r4),r0
    .org 0x2639a-ORIGIN
P_0002639a:
    .byte 0x00
    .org 0x2639b-ORIGIN
P_0002639b:
    .byte 0xf0
    .org 0x2639c-ORIGIN
P_0002639c:
    .byte 0x00
    .org 0x2639d-ORIGIN
P_0002639d:
    .byte 0x02
    .org 0x2639e-ORIGIN
P_0002639e:
    .byte 0x6a
    .org 0x2639f-ORIGIN
P_0002639f:
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
    .org 0x50018-ORIGIN
L_00050018:
    mov.l r11,@-r15
    .org 0x5001a-ORIGIN
L_0005001a:
    mov.l r12,@-r15
    .org 0x5001c-ORIGIN
L_0005001c:
    mov.l r13,@-r15
    .org 0x5001e-ORIGIN
L_0005001e:
    mov.l r14,@-r15
    .org 0x50020-ORIGIN
L_00050020:
    sts.l pr,@-r15
    .org 0x50022-ORIGIN
L_00050022:
    stc.l gbr,@-r15
    .org 0x50024-ORIGIN
L_00050024:
    mov.l P_0005022c,r0
    .org 0x50026-ORIGIN
L_00050026:
    ldc r0,gbr
    .org 0x50028-ORIGIN
L_00050028:
    add #-0xc,r15
    .org 0x5002a-ORIGIN
L_0005002a:
    mov.l P_00050230,r11
    .org 0x5002c-ORIGIN
L_0005002c:
    mov #0x0,r7
    .org 0x5002e-ORIGIN
L_0005002e:
    mov.l P_00050234,r6
    .org 0x50030-ORIGIN
L_00050030:
    mov.b @r11,r2
    .org 0x50032-ORIGIN
L_00050032:
    mov.l r7,@r15
    .org 0x50034-ORIGIN
L_00050034:
    extu.b r2,r13
    .org 0x50036-ORIGIN
L_00050036:
    mov.b @r6,r2
    .org 0x50038-ORIGIN
L_00050038:
    mov.l P_00050238,r7
    .org 0x5003a-ORIGIN
L_0005003a:
    mov.w P_0005014a,r0
    .org 0x5003c-ORIGIN
L_0005003c:
    extu.b r2,r12
    .org 0x5003e-ORIGIN
L_0005003e:
    mov.l P_0005023c,r6
    .org 0x50040-ORIGIN
L_00050040:
    mov.w P_0005014c,r4
    .org 0x50042-ORIGIN
L_00050042:
    jsr @r6
    .org 0x50044-ORIGIN
L_00050044:
    mov.b r12,@(r0,r7)
    .org 0x50046-ORIGIN
L_00050046:
    tst r0,r0
    .org 0x50048-ORIGIN
L_00050048:
    bt L_0005004e
    .org 0x5004a-ORIGIN
L_0005004a:
    bra L_0005017a
    .org 0x5004c-ORIGIN
L_0005004c:
    nop
    .org 0x5004e-ORIGIN
L_0005004e:
    mov.l P_00050240,r5
    .org 0x50050-ORIGIN
L_00050050:
    mov.b @(0x4,r5),r0
    .org 0x50052-ORIGIN
L_00050052:
    tst #0x40,r0
    .org 0x50054-ORIGIN
L_00050054:
    bt L_0005005a
    .org 0x50056-ORIGIN
L_00050056:
    bra L_0005017a
    .org 0x50058-ORIGIN
L_00050058:
    nop
    .org 0x5005a-ORIGIN
L_0005005a:
    mov.l P_0005023c,r6
    .org 0x5005c-ORIGIN
L_0005005c:
    mov.w P_0005014e,r4
    .org 0x5005e-ORIGIN
L_0005005e:
    jsr @r6
    .org 0x50060-ORIGIN
L_00050060:
    nop
    .org 0x50062-ORIGIN
L_00050062:
    tst r0,r0
    .org 0x50064-ORIGIN
L_00050064:
    bt L_0005006a
    .org 0x50066-ORIGIN
L_00050066:
    bra L_0005017a
    .org 0x50068-ORIGIN
L_00050068:
    nop
    .org 0x5006a-ORIGIN
L_0005006a:
    mov.l P_00050244,r5
    .org 0x5006c-ORIGIN
L_0005006c:
    mov #0x28,r0
    .org 0x5006e-ORIGIN
L_0005006e:
    mov.b @(r0,r5),r2
    .org 0x50070-ORIGIN
L_00050070:
    mov r2,r0
    .org 0x50072-ORIGIN
L_00050072:
    tst #0x80,r0
    .org 0x50074-ORIGIN
L_00050074:
    bt L_0005007a
    .org 0x50076-ORIGIN
L_00050076:
    bra L_0005017a
    .org 0x50078-ORIGIN
L_00050078:
    nop
    .org 0x5007a-ORIGIN
L_0005007a:
    mov r2,r0
    .org 0x5007c-ORIGIN
L_0005007c:
    tst #0x4,r0
    .org 0x5007e-ORIGIN
L_0005007e:
    bt L_00050084
    .org 0x50080-ORIGIN
L_00050080:
    bra L_0005017a
    .org 0x50082-ORIGIN
L_00050082:
    nop
    .org 0x50084-ORIGIN
L_00050084:
    mov #0x27,r0
    .org 0x50086-ORIGIN
L_00050086:
    mov.b @(r0,r5),r0
    .org 0x50088-ORIGIN
L_00050088:
    tst #0x1,r0
    .org 0x5008a-ORIGIN
L_0005008a:
    bf L_0005017a
    .org 0x5008c-ORIGIN
L_0005008c:
    mov r2,r0
    .org 0x5008e-ORIGIN
L_0005008e:
    tst #0x1,r0
    .org 0x50090-ORIGIN
L_00050090:
    bf L_0005017a
    .org 0x50092-ORIGIN
L_00050092:
    mov.l P_00050248,r6
    .org 0x50094-ORIGIN
L_00050094:
    mov.w P_00050150,r0
    .org 0x50096-ORIGIN
L_00050096:
    mov.b @(r0,r6),r2
    .org 0x50098-ORIGIN
L_00050098:
    tst r2,r2
    .org 0x5009a-ORIGIN
L_0005009a:
    bf L_0005017a
    .org 0x5009c-ORIGIN
L_0005009c:
    mov.l P_0005024c,r6
    .org 0x5009e-ORIGIN
L_0005009e:
    mov.b @(0x1,r6),r0
    .org 0x500a0-ORIGIN
L_000500a0:
    tst #0x2,r0
    .org 0x500a2-ORIGIN
L_000500a2:
    bf L_0005017a
    .org 0x500a4-ORIGIN
L_000500a4:
    mov.l P_00050250,r3
    .org 0x500a6-ORIGIN
L_000500a6:
    mov.l P_00050254,r4
    .org 0x500a8-ORIGIN
L_000500a8:
    mov.b @(0x7,r3),r0
    .org 0x500aa-ORIGIN
L_000500aa:
    mov.l P_00050258,r6
    .org 0x500ac-ORIGIN
L_000500ac:
    jsr @r6
    .org 0x500ae-ORIGIN
L_000500ae:
    extu.b r0,r5
    .org 0x500b0-ORIGIN
L_000500b0:
    mov.l P_00050250,r1
    .org 0x500b2-ORIGIN
L_000500b2:
    extu.b r0,r2
    .org 0x500b4-ORIGIN
L_000500b4:
    mov.l P_0005025c,r4
    .org 0x500b6-ORIGIN
L_000500b6:
    mov.b @(0x7,r1),r0
    .org 0x500b8-ORIGIN
L_000500b8:
    mov.l P_00050258,r6
    .org 0x500ba-ORIGIN
L_000500ba:
    extu.b r0,r5
    .org 0x500bc-ORIGIN
L_000500bc:
    jsr @r6
    .org 0x500be-ORIGIN
L_000500be:
    mov.l r2,@(0x4,r15)
    .org 0x500c0-ORIGIN
L_000500c0:
    mov.l P_00050240,r6
    .org 0x500c2-ORIGIN
L_000500c2:
    extu.b r0,r2
    .org 0x500c4-ORIGIN
L_000500c4:
    mov.l r2,@(0x8,r15)
    .org 0x500c6-ORIGIN
L_000500c6:
    mov.b @(0x4,r6),r0
    .org 0x500c8-ORIGIN
L_000500c8:
    tst #0x80,r0
    .org 0x500ca-ORIGIN
L_000500ca:
    bt L_0005010c
    .org 0x500cc-ORIGIN
L_000500cc:
    mov.l P_00050260,r2
    .org 0x500ce-ORIGIN
L_000500ce:
    mov #-0x1,r6
    .org 0x500d0-ORIGIN
L_000500d0:
    mov.l @(0x4,r15),r5
    .org 0x500d2-ORIGIN
L_000500d2:
    extu.b r6,r6
    .org 0x500d4-ORIGIN
L_000500d4:
    mov.b @r2,r4
    .org 0x500d6-ORIGIN
L_000500d6:
    extu.b r4,r4
    .org 0x500d8-ORIGIN
L_000500d8:
    add r4,r5
    .org 0x500da-ORIGIN
L_000500da:
    cmp/gt r6,r5
    .org 0x500dc-ORIGIN
L_000500dc:
    bf L_000500e2
    .org 0x500de-ORIGIN
L_000500de:
    bra L_000500e6
    .org 0x500e0-ORIGIN
L_000500e0:
    mov r6,r2
    .org 0x500e2-ORIGIN
L_000500e2:
    mov.l @(0x4,r15),r2
    .org 0x500e4-ORIGIN
L_000500e4:
    add r4,r2
    .org 0x500e6-ORIGIN
L_000500e6:
    mov.l @(0x8,r15),r3
    .org 0x500e8-ORIGIN
L_000500e8:
    add r4,r3
    .org 0x500ea-ORIGIN
L_000500ea:
    cmp/gt r6,r3
    .org 0x500ec-ORIGIN
L_000500ec:
    bf/s L_000500f4
    .org 0x500ee-ORIGIN
L_000500ee:
    mov.l r2,@(0x4,r15)
    .org 0x500f0-ORIGIN
L_000500f0:
    bra L_000500f8
    .org 0x500f2-ORIGIN
L_000500f2:
    mov r6,r2
    .org 0x500f4-ORIGIN
L_000500f4:
    mov.l @(0x8,r15),r2
    .org 0x500f6-ORIGIN
L_000500f6:
    add r4,r2
    .org 0x500f8-ORIGIN
L_000500f8:
    mov.l r2,@(0x8,r15)
    .org 0x500fa-ORIGIN
L_000500fa:
    mov r13,r2
    .org 0x500fc-ORIGIN
L_000500fc:
    add r4,r2
    .org 0x500fe-ORIGIN
L_000500fe:
    cmp/gt r6,r2
    .org 0x50100-ORIGIN
L_00050100:
    bf L_00050106
    .org 0x50102-ORIGIN
L_00050102:
    bra L_0005010a
    .org 0x50104-ORIGIN
L_00050104:
    mov r6,r2
    .org 0x50106-ORIGIN
L_00050106:
    add r4,r13
    .org 0x50108-ORIGIN
L_00050108:
    mov r13,r2
    .org 0x5010a-ORIGIN
L_0005010a:
    mov r2,r13
    .org 0x5010c-ORIGIN
L_0005010c:
    mov.l P_00050250,r3
    .org 0x5010e-ORIGIN
L_0005010e:
    mov.l P_00050264,r1
    .org 0x50110-ORIGIN
L_00050110:
    mov.b @(0x2,r3),r0
    .org 0x50112-ORIGIN
L_00050112:
    mov.b @r1,r2
    .org 0x50114-ORIGIN
L_00050114:
    extu.b r0,r4
    .org 0x50116-ORIGIN
L_00050116:
    extu.b r2,r2
    .org 0x50118-ORIGIN
L_00050118:
    cmp/ge r2,r4
    .org 0x5011a-ORIGIN
L_0005011a:
    bf/s L_00050138
    .org 0x5011c-ORIGIN
L_0005011c:
    mov #0x0,r5
    .org 0x5011e-ORIGIN
L_0005011e:
    mov #0x3,r14
    .org 0x50120-ORIGIN
L_00050120:
    extu.b r5,r5
    .org 0x50122-ORIGIN
L_00050122:
    cmp/ge r14,r5
    .org 0x50124-ORIGIN
L_00050124:
    bt L_00050138
    .org 0x50126-ORIGIN
L_00050126:
    add #0x1,r5
    .org 0x50128-ORIGIN
L_00050128:
    mov.l P_00050264,r3
    .org 0x5012a-ORIGIN
L_0005012a:
    extu.b r5,r5
    .org 0x5012c-ORIGIN
L_0005012c:
    mov r5,r0
    .org 0x5012e-ORIGIN
L_0005012e:
    mov.b @(r0,r3),r2
    .org 0x50130-ORIGIN
L_00050130:
    extu.b r4,r4
    .org 0x50132-ORIGIN
L_00050132:
    extu.b r2,r2
    .org 0x50134-ORIGIN
L_00050134:
    cmp/ge r2,r4
    .org 0x50136-ORIGIN
L_00050136:
    bt L_00050120
    .org 0x50138-ORIGIN
L_00050138:
    mov.l P_00050268,r6
    .org 0x5013a-ORIGIN
L_0005013a:
    extu.b r5,r0
    .org 0x5013c-ORIGIN
L_0005013c:
    mov.l @(0x4,r15),r5
    .org 0x5013e-ORIGIN
L_0005013e:
    mov.b @(r0,r6),r2
    .org 0x50140-ORIGIN
L_00050140:
    extu.b r2,r6
    .org 0x50142-ORIGIN
L_00050142:
    cmp/ge r6,r5
    .org 0x50144-ORIGIN
L_00050144:
    bt L_00050152
    .org 0x50146-ORIGIN
L_00050146:
    bra L_00050154
    .org 0x50148-ORIGIN
L_00050148:
    mov r6,r4
    .org 0x5014a-ORIGIN
P_0005014a:
    .byte 0x02
    .org 0x5014b-ORIGIN
P_0005014b:
    .byte 0x60
    .org 0x5014c-ORIGIN
P_0005014c:
    .byte 0x01
    .org 0x5014d-ORIGIN
P_0005014d:
    .byte 0x29
    .org 0x5014e-ORIGIN
P_0005014e:
    .byte 0x01
    .org 0x5014f-ORIGIN
P_0005014f:
    .byte 0x2a
    .org 0x50150-ORIGIN
P_00050150:
    .byte 0x03
    .org 0x50151-ORIGIN
P_00050151:
    .byte 0x89
    .org 0x50152-ORIGIN
L_00050152:
    mov.l @(0x4,r15),r4
    .org 0x50154-ORIGIN
L_00050154:
    mov.l @(0x8,r15),r2
    .org 0x50156-ORIGIN
L_00050156:
    cmp/ge r6,r2
    .org 0x50158-ORIGIN
L_00050158:
    bf L_0005015c
    .org 0x5015a-ORIGIN
L_0005015a:
    mov.l @(0x8,r15),r6
    .org 0x5015c-ORIGIN
L_0005015c:
    mov r6,r14
    .org 0x5015e-ORIGIN
L_0005015e:
    mov.l P_0005026c,r6
    .org 0x50160-ORIGIN
L_00050160:
    mov.b @(0x1,r6),r0
    .org 0x50162-ORIGIN
L_00050162:
    tst #0x10,r0
    .org 0x50164-ORIGIN
L_00050164:
    bf L_000501a4
    .org 0x50166-ORIGIN
L_00050166:
    mov.b @(0x5,r11),r0
    .org 0x50168-ORIGIN
L_00050168:
    extu.b r0,r6
    .org 0x5016a-ORIGIN
L_0005016a:
    cmp/ge r6,r4
    .org 0x5016c-ORIGIN
L_0005016c:
    bt L_00050170
    .org 0x5016e-ORIGIN
L_0005016e:
    mov r6,r4
    .org 0x50170-ORIGIN
L_00050170:
    cmp/ge r6,r14
    .org 0x50172-ORIGIN
L_00050172:
    bf L_00050176
    .org 0x50174-ORIGIN
L_00050174:
    mov r14,r6
    .org 0x50176-ORIGIN
L_00050176:
    bra L_000501a4
    .org 0x50178-ORIGIN
L_00050178:
    mov r6,r14
    .org 0x5017a-ORIGIN
L_0005017a:
    mov.b @(0x4,r11),r0
    .org 0x5017c-ORIGIN
L_0005017c:
    mov.l P_00050240,r6
    .org 0x5017e-ORIGIN
L_0005017e:
    extu.b r0,r14
    .org 0x50180-ORIGIN
L_00050180:
    mov.b @(0x4,r6),r0
    .org 0x50182-ORIGIN
L_00050182:
    tst #0x80,r0
    .org 0x50184-ORIGIN
L_00050184:
    bt/s L_000501a4
    .org 0x50186-ORIGIN
L_00050186:
    mov r14,r4
    .org 0x50188-ORIGIN
L_00050188:
    mov.l P_00050260,r2
    .org 0x5018a-ORIGIN
L_0005018a:
    mov #-0x1,r6
    .org 0x5018c-ORIGIN
L_0005018c:
    extu.b r6,r6
    .org 0x5018e-ORIGIN
L_0005018e:
    mov.b @r2,r5
    .org 0x50190-ORIGIN
L_00050190:
    mov r13,r2
    .org 0x50192-ORIGIN
L_00050192:
    extu.b r5,r5
    .org 0x50194-ORIGIN
L_00050194:
    add r5,r2
    .org 0x50196-ORIGIN
L_00050196:
    cmp/gt r6,r2
    .org 0x50198-ORIGIN
L_00050198:
    bf L_0005019e
    .org 0x5019a-ORIGIN
L_0005019a:
    bra L_000501a2
    .org 0x5019c-ORIGIN
L_0005019c:
    mov r6,r2
    .org 0x5019e-ORIGIN
L_0005019e:
    add r5,r13
    .org 0x501a0-ORIGIN
L_000501a0:
    mov r13,r2
    .org 0x501a2-ORIGIN
L_000501a2:
    mov r2,r13
    .org 0x501a4-ORIGIN
L_000501a4:
    mov.l P_00050238,r7
    .org 0x501a6-ORIGIN
L_000501a6:
    mov.w P_00050226,r0
    .org 0x501a8-ORIGIN
L_000501a8:
    mov.l P_00050270,r6
    .org 0x501aa-ORIGIN
L_000501aa:
    mov.b r4,@(r0,r7)
    .org 0x501ac-ORIGIN
L_000501ac:
    mov.w P_00050228,r0
    .org 0x501ae-ORIGIN
L_000501ae:
    mov.b r14,@(r0,r7)
    .org 0x501b0-ORIGIN
L_000501b0:
    mov.b @r6,r0
    .org 0x501b2-ORIGIN
L_000501b2:
    tst #0x40,r0
    .org 0x501b4-ORIGIN
L_000501b4:
    bt L_000501ba
    .org 0x501b6-ORIGIN
L_000501b6:
    bra L_0005036a
    .org 0x501b8-ORIGIN
L_000501b8:
    nop
    .org 0x501ba-ORIGIN
L_000501ba:
    mov.l P_00050274,r6
    .org 0x501bc-ORIGIN
L_000501bc:
    mov.b @(0xc,r6),r0
    .org 0x501be-ORIGIN
L_000501be:
    tst #0x20,r0
    .org 0x501c0-ORIGIN
L_000501c0:
    bf/s L_000501c8
    .org 0x501c2-ORIGIN
L_000501c2:
    mov r0,r2
    .org 0x501c4-ORIGIN
L_000501c4:
    bra L_00050366
    .org 0x501c6-ORIGIN
L_000501c6:
    nop
    .org 0x501c8-ORIGIN
L_000501c8:
    mov.l P_00050278,r5
    .org 0x501ca-ORIGIN
L_000501ca:
    mov #0x7a,r0
    .org 0x501cc-ORIGIN
L_000501cc:
    mov.b @(r0,r5),r6
    .org 0x501ce-ORIGIN
L_000501ce:
    extu.b r6,r5
    .org 0x501d0-ORIGIN
L_000501d0:
    cmp/ge r12,r5
    .org 0x501d2-ORIGIN
L_000501d2:
    bt L_000501ec
    .org 0x501d4-ORIGIN
L_000501d4:
    mov.b @(0x17,gbr),r0
    .org 0x501d6-ORIGIN
L_000501d6:
    extu.b r0,r6
    .org 0x501d8-ORIGIN
L_000501d8:
    cmp/gt r14,r6
    .org 0x501da-ORIGIN
L_000501da:
    bt L_000501e0
    .org 0x501dc-ORIGIN
L_000501dc:
    bra L_00050360
    .org 0x501de-ORIGIN
L_000501de:
    nop
    .org 0x501e0-ORIGIN
L_000501e0:
    cmp/gt r4,r6
    .org 0x501e2-ORIGIN
L_000501e2:
    bt L_000501e8
    .org 0x501e4-ORIGIN
L_000501e4:
    bra L_00050340
    .org 0x501e6-ORIGIN
L_000501e6:
    nop
    .org 0x501e8-ORIGIN
L_000501e8:
    bra L_00050378
    .org 0x501ea-ORIGIN
L_000501ea:
    nop
    .org 0x501ec-ORIGIN
L_000501ec:
    mov.l P_0005027c,r6
    .org 0x501ee-ORIGIN
L_000501ee:
    mov.b @r6,r0
    .org 0x501f0-ORIGIN
L_000501f0:
    mov.l P_00050280,r6
    .org 0x501f2-ORIGIN
L_000501f2:
    and #0x80,r0
    .org 0x501f4-ORIGIN
L_000501f4:
    mov r0,r5
    .org 0x501f6-ORIGIN
L_000501f6:
    mov.b @r6,r0
    .org 0x501f8-ORIGIN
L_000501f8:
    tst #0x80,r0
    .org 0x501fa-ORIGIN
L_000501fa:
    bt L_00050200
    .org 0x501fc-ORIGIN
L_000501fc:
    bra L_00050328
    .org 0x501fe-ORIGIN
L_000501fe:
    nop
    .org 0x50200-ORIGIN
L_00050200:
    tst r5,r5
    .org 0x50202-ORIGIN
L_00050202:
    bt L_00050208
    .org 0x50204-ORIGIN
L_00050204:
    bra L_000502ec
    .org 0x50206-ORIGIN
L_00050206:
    nop
    .org 0x50208-ORIGIN
L_00050208:
    mov.l P_0005026c,r7
    .org 0x5020a-ORIGIN
L_0005020a:
    mov.b @(0x1,r7),r0
    .org 0x5020c-ORIGIN
L_0005020c:
    tst #0x10,r0
    .org 0x5020e-ORIGIN
L_0005020e:
    bt L_000502ec
    .org 0x50210-ORIGIN
L_00050210:
    mov r2,r0
    .org 0x50212-ORIGIN
L_00050212:
    tst #0x80,r0
    .org 0x50214-ORIGIN
L_00050214:
    bf L_00050284
    .org 0x50216-ORIGIN
L_00050216:
    mov.b @(0x17,gbr),r0
    .org 0x50218-ORIGIN
L_00050218:
    extu.b r0,r6
    .org 0x5021a-ORIGIN
L_0005021a:
    cmp/gt r14,r6
    .org 0x5021c-ORIGIN
L_0005021c:
    bt L_00050222
    .org 0x5021e-ORIGIN
L_0005021e:
    bra L_00050360
    .org 0x50220-ORIGIN
L_00050220:
    nop
    .org 0x50222-ORIGIN
L_00050222:
    bra L_00050378
    .org 0x50224-ORIGIN
L_00050224:
    nop
    .org 0x50226-ORIGIN
P_00050226:
    .byte 0x04
    .org 0x50227-ORIGIN
P_00050227:
    .byte 0xec
    .org 0x50228-ORIGIN
P_00050228:
    .byte 0x04
    .org 0x50229-ORIGIN
P_00050229:
    .byte 0x1e
    .org 0x5022c-ORIGIN
P_0005022c:
    .byte 0xff
    .org 0x5022d-ORIGIN
P_0005022d:
    .byte 0xff
    .org 0x5022e-ORIGIN
P_0005022e:
    .byte 0x11
    .org 0x5022f-ORIGIN
P_0005022f:
    .byte 0x9c
    .org 0x50230-ORIGIN
P_00050230:
    .byte 0x00
    .org 0x50231-ORIGIN
P_00050231:
    .byte 0x00
    .org 0x50232-ORIGIN
P_00050232:
    .byte 0x8a
    .org 0x50233-ORIGIN
P_00050233:
    .byte 0x3a
    .org 0x50234-ORIGIN
P_00050234:
    .byte 0x00
    .org 0x50235-ORIGIN
P_00050235:
    .byte 0x00
    .org 0x50236-ORIGIN
P_00050236:
    .byte 0x85
    .org 0x50237-ORIGIN
P_00050237:
    .byte 0xfa
    .org 0x50238-ORIGIN
P_00050238:
    .byte 0xff
    .org 0x50239-ORIGIN
P_00050239:
    .byte 0xff
    .org 0x5023a-ORIGIN
P_0005023a:
    .byte 0x12
    .org 0x5023b-ORIGIN
P_0005023b:
    .byte 0x8c
    .org 0x5023c-ORIGIN
P_0005023c:
    .byte 0x00
    .org 0x5023d-ORIGIN
P_0005023d:
    .byte 0x02
    .org 0x5023e-ORIGIN
P_0005023e:
    .byte 0x5c
    .org 0x5023f-ORIGIN
P_0005023f:
    .byte 0x36
    .org 0x50240-ORIGIN
P_00050240:
    .byte 0xff
    .org 0x50241-ORIGIN
P_00050241:
    .byte 0xff
    .org 0x50242-ORIGIN
P_00050242:
    .byte 0x42
    .org 0x50243-ORIGIN
P_00050243:
    .byte 0x4c
    .org 0x50244-ORIGIN
P_00050244:
    .byte 0xff
    .org 0x50245-ORIGIN
P_00050245:
    .byte 0xff
    .org 0x50246-ORIGIN
P_00050246:
    .byte 0x41
    .org 0x50247-ORIGIN
P_00050247:
    .byte 0xa9
    .org 0x50248-ORIGIN
P_00050248:
    .byte 0xff
    .org 0x50249-ORIGIN
P_00050249:
    .byte 0xff
    .org 0x5024a-ORIGIN
P_0005024a:
    .byte 0x45
    .org 0x5024b-ORIGIN
P_0005024b:
    .byte 0x58
    .org 0x5024c-ORIGIN
P_0005024c:
    .byte 0xff
    .org 0x5024d-ORIGIN
P_0005024d:
    .byte 0xff
    .org 0x5024e-ORIGIN
P_0005024e:
    .byte 0x24
    .org 0x5024f-ORIGIN
P_0005024f:
    .byte 0x5c
    .org 0x50250-ORIGIN
P_00050250:
    .byte 0xff
    .org 0x50251-ORIGIN
P_00050251:
    .byte 0xff
    .org 0x50252-ORIGIN
P_00050252:
    .byte 0x10
    .org 0x50253-ORIGIN
P_00050253:
    .byte 0x68
    .org 0x50254-ORIGIN
P_00050254:
    .byte 0x00
    .org 0x50255-ORIGIN
P_00050255:
    .byte 0x01
    .org 0x50256-ORIGIN
P_00050256:
    .byte 0x29
    .org 0x50257-ORIGIN
P_00050257:
    .byte 0x8c
    .org 0x50258-ORIGIN
P_00050258:
    .byte 0x00
    .org 0x50259-ORIGIN
P_00050259:
    .byte 0x02
    .org 0x5025a-ORIGIN
P_0005025a:
    .byte 0x63
    .org 0x5025b-ORIGIN
P_0005025b:
    .byte 0x88
    .org 0x5025c-ORIGIN
P_0005025c:
    .byte 0x00
    .org 0x5025d-ORIGIN
P_0005025d:
    .byte 0x01
    .org 0x5025e-ORIGIN
P_0005025e:
    .byte 0x28
    .org 0x5025f-ORIGIN
P_0005025f:
    .byte 0x18
    .org 0x50260-ORIGIN
P_00050260:
    .byte 0x00
    .org 0x50261-ORIGIN
P_00050261:
    .byte 0x00
    .org 0x50262-ORIGIN
P_00050262:
    .byte 0x84
    .org 0x50263-ORIGIN
P_00050263:
    .byte 0xe8
    .org 0x50264-ORIGIN
P_00050264:
    .byte 0x00
    .org 0x50265-ORIGIN
P_00050265:
    .byte 0x01
    .org 0x50266-ORIGIN
P_00050266:
    .byte 0x1c
    .org 0x50267-ORIGIN
P_00050267:
    .byte 0xb5
    .org 0x50268-ORIGIN
P_00050268:
    .byte 0x00
    .org 0x50269-ORIGIN
P_00050269:
    .byte 0x01
    .org 0x5026a-ORIGIN
P_0005026a:
    .byte 0x29
    .org 0x5026b-ORIGIN
P_0005026b:
    .byte 0x9c
    .org 0x5026c-ORIGIN
P_0005026c:
    .byte 0xff
    .org 0x5026d-ORIGIN
P_0005026d:
    .byte 0xff
    .org 0x5026e-ORIGIN
P_0005026e:
    .byte 0x24
    .org 0x5026f-ORIGIN
P_0005026f:
    .byte 0xce
    .org 0x50270-ORIGIN
P_00050270:
    .byte 0xff
    .org 0x50271-ORIGIN
P_00050271:
    .byte 0xff
    .org 0x50272-ORIGIN
P_00050272:
    .byte 0x24
    .org 0x50273-ORIGIN
P_00050273:
    .byte 0x68
    .org 0x50274-ORIGIN
P_00050274:
    .byte 0xff
    .org 0x50275-ORIGIN
P_00050275:
    .byte 0xff
    .org 0x50276-ORIGIN
P_00050276:
    .byte 0x24
    .org 0x50277-ORIGIN
P_00050277:
    .byte 0x4c
    .org 0x50278-ORIGIN
P_00050278:
    .byte 0xff
    .org 0x50279-ORIGIN
P_00050279:
    .byte 0xff
    .org 0x5027a-ORIGIN
P_0005027a:
    .byte 0x10
    .org 0x5027b-ORIGIN
P_0005027b:
    .byte 0x94
    .org 0x5027c-ORIGIN
P_0005027c:
    .byte 0x00
    .org 0x5027d-ORIGIN
P_0005027d:
    .byte 0x00
    .org 0x5027e-ORIGIN
P_0005027e:
    .byte 0x8b
    .org 0x5027f-ORIGIN
P_0005027f:
    .byte 0x3f
    .org 0x50280-ORIGIN
P_00050280:
    .byte 0x00
    .org 0x50281-ORIGIN
P_00050281:
    .byte 0x00
    .org 0x50282-ORIGIN
P_00050282:
    .byte 0x87
    .org 0x50283-ORIGIN
P_00050283:
    .byte 0x0c
    .org 0x50284-ORIGIN
L_00050284:
    mov.l P_00050444,r6
    .org 0x50286-ORIGIN
L_00050286:
    mov.b @(0x1,r6),r0
    .org 0x50288-ORIGIN
L_00050288:
    cmp/eq #0x2,r0
    .org 0x5028a-ORIGIN
L_0005028a:
    bt L_0005029c
    .org 0x5028c-ORIGIN
L_0005028c:
    mov.b @(0x17,gbr),r0
    .org 0x5028e-ORIGIN
L_0005028e:
    extu.b r0,r6
    .org 0x50290-ORIGIN
L_00050290:
    cmp/gt r13,r6
    .org 0x50292-ORIGIN
L_00050292:
    bf L_00050360
    .org 0x50294-ORIGIN
L_00050294:
    cmp/gt r14,r6
    .org 0x50296-ORIGIN
L_00050296:
    bf L_00050360
    .org 0x50298-ORIGIN
L_00050298:
    bra L_00050378
    .org 0x5029a-ORIGIN
L_0005029a:
    nop
    .org 0x5029c-ORIGIN
L_0005029c:
    mov.l P_00050448,r3
    .org 0x5029e-ORIGIN
L_0005029e:
    mov #0x7a,r0
    .org 0x502a0-ORIGIN
L_000502a0:
    mov.l P_0005044c,r5
    .org 0x502a2-ORIGIN
L_000502a2:
    mov.b @(r0,r3),r6
    .org 0x502a4-ORIGIN
L_000502a4:
    mov.b @r5,r2
    .org 0x502a6-ORIGIN
L_000502a6:
    cmp/hs r2,r6
    .org 0x502a8-ORIGIN
L_000502a8:
    bt L_000502ba
    .org 0x502aa-ORIGIN
L_000502aa:
    mov.b @(0x17,gbr),r0
    .org 0x502ac-ORIGIN
L_000502ac:
    extu.b r0,r6
    .org 0x502ae-ORIGIN
L_000502ae:
    cmp/gt r13,r6
    .org 0x502b0-ORIGIN
L_000502b0:
    bf L_00050360
    .org 0x502b2-ORIGIN
L_000502b2:
    cmp/gt r14,r6
    .org 0x502b4-ORIGIN
L_000502b4:
    bf L_00050360
    .org 0x502b6-ORIGIN
L_000502b6:
    bra L_00050378
    .org 0x502b8-ORIGIN
L_000502b8:
    nop
    .org 0x502ba-ORIGIN
L_000502ba:
    mov.l P_00050450,r2
    .org 0x502bc-ORIGIN
L_000502bc:
    mov #-0x80,r0
    .org 0x502be-ORIGIN
L_000502be:
    mov.l P_00050454,r5
    .org 0x502c0-ORIGIN
L_000502c0:
    extu.b r0,r0
    .org 0x502c2-ORIGIN
L_000502c2:
    mov.b @(r0,r2),r6
    .org 0x502c4-ORIGIN
L_000502c4:
    mov.b @r5,r2
    .org 0x502c6-ORIGIN
L_000502c6:
    cmp/hi r2,r6
    .org 0x502c8-ORIGIN
L_000502c8:
    bt/s L_000502de
    .org 0x502ca-ORIGIN
L_000502ca:
    mov.b @(0x17,gbr),r0
    .org 0x502cc-ORIGIN
L_000502cc:
    extu.b r0,r5
    .org 0x502ce-ORIGIN
L_000502ce:
    mov.b @(0x1,r11),r0
    .org 0x502d0-ORIGIN
L_000502d0:
    extu.b r0,r2
    .org 0x502d2-ORIGIN
L_000502d2:
    cmp/gt r2,r5
    .org 0x502d4-ORIGIN
L_000502d4:
    bf L_00050360
    .org 0x502d6-ORIGIN
L_000502d6:
    cmp/gt r14,r5
    .org 0x502d8-ORIGIN
L_000502d8:
    bf L_00050360
    .org 0x502da-ORIGIN
L_000502da:
    bra L_00050378
    .org 0x502dc-ORIGIN
L_000502dc:
    nop
    .org 0x502de-ORIGIN
L_000502de:
    extu.b r0,r6
    .org 0x502e0-ORIGIN
L_000502e0:
    cmp/gt r13,r6
    .org 0x502e2-ORIGIN
L_000502e2:
    bf L_00050360
    .org 0x502e4-ORIGIN
L_000502e4:
    cmp/gt r14,r6
    .org 0x502e6-ORIGIN
L_000502e6:
    bf L_00050360
    .org 0x502e8-ORIGIN
L_000502e8:
    bra L_00050378
    .org 0x502ea-ORIGIN
L_000502ea:
    nop
    .org 0x502ec-ORIGIN
L_000502ec:
    tst r5,r5
    .org 0x502ee-ORIGIN
L_000502ee:
    bt L_00050308
    .org 0x502f0-ORIGIN
L_000502f0:
    mov.l P_00050458,r5
    .org 0x502f2-ORIGIN
L_000502f2:
    mov.b @(0x4,r5),r0
    .org 0x502f4-ORIGIN
L_000502f4:
    tst #0x40,r0
    .org 0x502f6-ORIGIN
L_000502f6:
    bf L_00050308
    .org 0x502f8-ORIGIN
L_000502f8:
    mov.b @(0x17,gbr),r0
    .org 0x502fa-ORIGIN
L_000502fa:
    extu.b r0,r6
    .org 0x502fc-ORIGIN
L_000502fc:
    cmp/gt r14,r6
    .org 0x502fe-ORIGIN
L_000502fe:
    bf L_00050360
    .org 0x50300-ORIGIN
L_00050300:
    cmp/gt r4,r6
    .org 0x50302-ORIGIN
L_00050302:
    bf L_00050340
    .org 0x50304-ORIGIN
L_00050304:
    bra L_00050378
    .org 0x50306-ORIGIN
L_00050306:
    nop
    .org 0x50308-ORIGIN
L_00050308:
    mov r2,r0
    .org 0x5030a-ORIGIN
L_0005030a:
    tst #0x80,r0
    .org 0x5030c-ORIGIN
L_0005030c:
    bt/s L_0005031e
    .org 0x5030e-ORIGIN
L_0005030e:
    mov.b @(0x17,gbr),r0
    .org 0x50310-ORIGIN
L_00050310:
    extu.b r0,r6
    .org 0x50312-ORIGIN
L_00050312:
    cmp/gt r13,r6
    .org 0x50314-ORIGIN
L_00050314:
    bf L_00050360
    .org 0x50316-ORIGIN
L_00050316:
    cmp/gt r14,r6
    .org 0x50318-ORIGIN
L_00050318:
    bf L_00050360
    .org 0x5031a-ORIGIN
L_0005031a:
    bra L_00050378
    .org 0x5031c-ORIGIN
L_0005031c:
    nop
    .org 0x5031e-ORIGIN
L_0005031e:
    extu.b r0,r2
    .org 0x50320-ORIGIN
L_00050320:
    cmp/gt r14,r2
    .org 0x50322-ORIGIN
L_00050322:
    bf L_00050360
    .org 0x50324-ORIGIN
L_00050324:
    bra L_00050378
    .org 0x50326-ORIGIN
L_00050326:
    nop
    .org 0x50328-ORIGIN
L_00050328:
    tst r5,r5
    .org 0x5032a-ORIGIN
L_0005032a:
    bt L_00050344
    .org 0x5032c-ORIGIN
L_0005032c:
    mov.l P_00050458,r5
    .org 0x5032e-ORIGIN
L_0005032e:
    mov.b @(0x4,r5),r0
    .org 0x50330-ORIGIN
L_00050330:
    tst #0x40,r0
    .org 0x50332-ORIGIN
L_00050332:
    bf L_00050344
    .org 0x50334-ORIGIN
L_00050334:
    mov.b @(0x17,gbr),r0
    .org 0x50336-ORIGIN
L_00050336:
    extu.b r0,r6
    .org 0x50338-ORIGIN
L_00050338:
    cmp/gt r14,r6
    .org 0x5033a-ORIGIN
L_0005033a:
    bf L_00050360
    .org 0x5033c-ORIGIN
L_0005033c:
    cmp/gt r4,r6
    .org 0x5033e-ORIGIN
L_0005033e:
    bt L_00050378
    .org 0x50340-ORIGIN
L_00050340:
    bra L_00050362
    .org 0x50342-ORIGIN
L_00050342:
    mov #0x2,r7
    .org 0x50344-ORIGIN
L_00050344:
    mov r2,r0
    .org 0x50346-ORIGIN
L_00050346:
    tst #0x80,r0
    .org 0x50348-ORIGIN
L_00050348:
    bt/s L_0005035a
    .org 0x5034a-ORIGIN
L_0005034a:
    mov.b @(0x17,gbr),r0
    .org 0x5034c-ORIGIN
L_0005034c:
    extu.b r0,r6
    .org 0x5034e-ORIGIN
L_0005034e:
    cmp/gt r13,r6
    .org 0x50350-ORIGIN
L_00050350:
    bf L_00050360
    .org 0x50352-ORIGIN
L_00050352:
    cmp/gt r14,r6
    .org 0x50354-ORIGIN
L_00050354:
    bf L_00050360
    .org 0x50356-ORIGIN
L_00050356:
    bra L_00050378
    .org 0x50358-ORIGIN
L_00050358:
    nop
    .org 0x5035a-ORIGIN
L_0005035a:
    extu.b r0,r2
    .org 0x5035c-ORIGIN
L_0005035c:
    cmp/gt r14,r2
    .org 0x5035e-ORIGIN
L_0005035e:
    bt L_00050378
    .org 0x50360-ORIGIN
L_00050360:
    mov #0x3,r7
    .org 0x50362-ORIGIN
L_00050362:
    bra L_00050378
    .org 0x50364-ORIGIN
L_00050364:
    mov.l r7,@r15
    .org 0x50366-ORIGIN
L_00050366:
    mov #0x1,r7
    .org 0x50368-ORIGIN
L_00050368:
    mov.l r7,@r15
    .org 0x5036a-ORIGIN
L_0005036a:
    mov.l P_0005045c,r6
    .org 0x5036c-ORIGIN
L_0005036c:
    mov #0x2d,r0
    .org 0x5036e-ORIGIN
L_0005036e:
    mov.b @(r0,r6),r0
    .org 0x50370-ORIGIN
L_00050370:
    or #0x80,r0
    .org 0x50372-ORIGIN
L_00050372:
    mov r0,r2
    .org 0x50374-ORIGIN
L_00050374:
    mov #0x2d,r0
    .org 0x50376-ORIGIN
L_00050376:
    mov.b r2,@(r0,r6)
    .org 0x50378-ORIGIN
L_00050378:
    mov.l @r15,r0
    .org 0x5037a-ORIGIN
L_0005037a:
    add #0xc,r15
    .org 0x5037c-ORIGIN
L_0005037c:
    ldc.l @r15+,gbr
    .org 0x5037e-ORIGIN
L_0005037e:
    lds.l @r15+,pr
    .org 0x50380-ORIGIN
L_00050380:
    mov.l @r15+,r14
    .org 0x50382-ORIGIN
L_00050382:
    mov.l @r15+,r13
    .org 0x50384-ORIGIN
L_00050384:
    mov.l @r15+,r12
    .org 0x50386-ORIGIN
L_00050386:
    rts
    .org 0x50388-ORIGIN
L_00050388:
    mov.l @r15+,r11
    .org 0x503e0-ORIGIN
L_000503e0:
    mov.l r9,@-r15
    .org 0x503e2-ORIGIN
L_000503e2:
    mov.l r10,@-r15
    .org 0x503e4-ORIGIN
L_000503e4:
    mov.l r11,@-r15
    .org 0x503e6-ORIGIN
L_000503e6:
    mov.l r12,@-r15
    .org 0x503e8-ORIGIN
L_000503e8:
    mov.l r13,@-r15
    .org 0x503ea-ORIGIN
L_000503ea:
    mov.l r14,@-r15
    .org 0x503ec-ORIGIN
L_000503ec:
    sts.l pr,@-r15
    .org 0x503ee-ORIGIN
L_000503ee:
    sts.l macl,@-r15
    .org 0x503f0-ORIGIN
L_000503f0:
    add #-0x4,r15
    .org 0x503f2-ORIGIN
L_000503f2:
    mov r6,r0
    .org 0x503f4-ORIGIN
L_000503f4:
    mov.w r0,@(0x2,r15)
    .org 0x503f6-ORIGIN
L_000503f6:
    mov.l P_00050478,r9
    .org 0x503f8-ORIGIN
L_000503f8:
    mov.w P_00050400,r0
    .org 0x503fa-ORIGIN
L_000503fa:
    mov.l P_0005047c,r10
    .org 0x503fc-ORIGIN
L_000503fc:
    bra L_00050402
    .org 0x503fe-ORIGIN
L_000503fe:
    mov r5,r12
    .org 0x50400-ORIGIN
P_00050400:
    .byte 0x02
    .org 0x50401-ORIGIN
P_00050401:
    .byte 0x35
    .org 0x50402-ORIGIN
L_00050402:
    mov.b @(r0,r9),r2
    .org 0x50404-ORIGIN
L_00050404:
    mov.b @r10,r0
    .org 0x50406-ORIGIN
L_00050406:
    mov.l r6,@r15
    .org 0x50408-ORIGIN
L_00050408:
    mov #0x0,r6
    .org 0x5040a-ORIGIN
L_0005040a:
    tst #0x40,r0
    .org 0x5040c-ORIGIN
L_0005040c:
    extu.b r2,r11
    .org 0x5040e-ORIGIN
L_0005040e:
    mov r6,r13
    .org 0x50410-ORIGIN
L_00050410:
    bt/s L_00050418
    .org 0x50412-ORIGIN
L_00050412:
    mov r6,r14
    .org 0x50414-ORIGIN
L_00050414:
    bra L_000505f4
    .org 0x50416-ORIGIN
L_00050416:
    nop
    .org 0x50418-ORIGIN
L_00050418:
    mov r11,r0
    .org 0x5041a-ORIGIN
L_0005041a:
    cmp/eq #0x4,r0
    .org 0x5041c-ORIGIN
L_0005041c:
    bf L_00050436
    .org 0x5041e-ORIGIN
L_0005041e:
    mov.l P_00050468,r5
    .org 0x50420-ORIGIN
L_00050420:
    mov.b @r5,r0
    .org 0x50422-ORIGIN
L_00050422:
    tst #0x20,r0
    .org 0x50424-ORIGIN
L_00050424:
    bt L_00050436
    .org 0x50426-ORIGIN
L_00050426:
    mov.l P_00050480,r2
    .org 0x50428-ORIGIN
L_00050428:
    mov.l P_00050470,r3
    .org 0x5042a-ORIGIN
L_0005042a:
    mov.b @(0x2,r2),r0
    .org 0x5042c-ORIGIN
L_0005042c:
    mov.b @r3,r2
    .org 0x5042e-ORIGIN
L_0005042e:
    cmp/hs r2,r0
    .org 0x50430-ORIGIN
L_00050430:
    bf L_00050436
    .org 0x50432-ORIGIN
L_00050432:
    bra L_000505f4
    .org 0x50434-ORIGIN
L_00050434:
    nop
    .org 0x50436-ORIGIN
L_00050436:
    mov #0x2,r5
    .org 0x50438-ORIGIN
L_00050438:
    cmp/gt r5,r11
    .org 0x5043a-ORIGIN
L_0005043a:
    bt L_000504ca
    .org 0x5043c-ORIGIN
L_0005043c:
    tst r12,r12
    .org 0x5043e-ORIGIN
L_0005043e:
    bt L_00050484
    .org 0x50440-ORIGIN
L_00050440:
    bra L_00050498
    .org 0x50442-ORIGIN
L_00050442:
    mov #0x0,r11
    .org 0x50444-ORIGIN
P_00050444:
    .byte 0xff
    .org 0x50445-ORIGIN
P_00050445:
    .byte 0xff
    .org 0x50446-ORIGIN
P_00050446:
    .byte 0x10
    .org 0x50447-ORIGIN
P_00050447:
    .byte 0x82
    .org 0x50448-ORIGIN
P_00050448:
    .byte 0xff
    .org 0x50449-ORIGIN
P_00050449:
    .byte 0xff
    .org 0x5044a-ORIGIN
P_0005044a:
    .byte 0x10
    .org 0x5044b-ORIGIN
P_0005044b:
    .byte 0x94
    .org 0x5044c-ORIGIN
P_0005044c:
    .byte 0x00
    .org 0x5044d-ORIGIN
P_0005044d:
    .byte 0x00
    .org 0x5044e-ORIGIN
P_0005044e:
    .byte 0x85
    .org 0x5044f-ORIGIN
P_0005044f:
    .byte 0xfc
    .org 0x50450-ORIGIN
P_00050450:
    .byte 0xff
    .org 0x50451-ORIGIN
P_00050451:
    .byte 0xff
    .org 0x50452-ORIGIN
P_00050452:
    .byte 0x28
    .org 0x50453-ORIGIN
P_00050453:
    .byte 0xf8
    .org 0x50454-ORIGIN
P_00050454:
    .byte 0x00
    .org 0x50455-ORIGIN
P_00050455:
    .byte 0x00
    .org 0x50456-ORIGIN
P_00050456:
    .byte 0x8a
    .org 0x50457-ORIGIN
P_00050457:
    .byte 0x2f
    .org 0x50458-ORIGIN
P_00050458:
    .byte 0xff
    .org 0x50459-ORIGIN
P_00050459:
    .byte 0xff
    .org 0x5045a-ORIGIN
P_0005045a:
    .byte 0x24
    .org 0x5045b-ORIGIN
P_0005045b:
    .byte 0x4c
    .org 0x5045c-ORIGIN
P_0005045c:
    .byte 0xff
    .org 0x5045d-ORIGIN
P_0005045d:
    .byte 0xff
    .org 0x5045e-ORIGIN
P_0005045e:
    .byte 0x24
    .org 0x5045f-ORIGIN
P_0005045f:
    .byte 0x70
    .org 0x50468-ORIGIN
P_00050468:
    .byte 0xff
    .org 0x50469-ORIGIN
P_00050469:
    .byte 0xff
    .org 0x5046a-ORIGIN
P_0005046a:
    .byte 0x24
    .org 0x5046b-ORIGIN
P_0005046b:
    .byte 0x58
    .org 0x50470-ORIGIN
P_00050470:
    .byte 0x00
    .org 0x50471-ORIGIN
P_00050471:
    .byte 0x00
    .org 0x50472-ORIGIN
P_00050472:
    .byte 0x8a
    .org 0x50473-ORIGIN
P_00050473:
    .byte 0x40
    .org 0x50478-ORIGIN
P_00050478:
    .byte 0xff
    .org 0x50479-ORIGIN
P_00050479:
    .byte 0xff
    .org 0x5047a-ORIGIN
P_0005047a:
    .byte 0x12
    .org 0x5047b-ORIGIN
P_0005047b:
    .byte 0x8c
    .org 0x5047c-ORIGIN
P_0005047c:
    .byte 0xff
    .org 0x5047d-ORIGIN
P_0005047d:
    .byte 0xff
    .org 0x5047e-ORIGIN
P_0005047e:
    .byte 0x24
    .org 0x5047f-ORIGIN
P_0005047f:
    .byte 0x68
    .org 0x50480-ORIGIN
P_00050480:
    .byte 0xff
    .org 0x50481-ORIGIN
P_00050481:
    .byte 0xff
    .org 0x50482-ORIGIN
P_00050482:
    .byte 0x10
    .org 0x50483-ORIGIN
P_00050483:
    .byte 0x68
    .org 0x50484-ORIGIN
L_00050484:
    tst r4,r4
    .org 0x50486-ORIGIN
L_00050486:
    bt L_00050498
    .org 0x50488-ORIGIN
L_00050488:
    tst r11,r11
    .org 0x5048a-ORIGIN
L_0005048a:
    bf L_00050498
    .org 0x5048c-ORIGIN
L_0005048c:
    mov r15,r5
    .org 0x5048e-ORIGIN
L_0005048e:
    add #0x2,r5
    .org 0x50490-ORIGIN
L_00050490:
    mov.b @r5,r0
    .org 0x50492-ORIGIN
L_00050492:
    mov #0x1,r11
    .org 0x50494-ORIGIN
L_00050494:
    mov.l P_000506b0,r4
    .org 0x50496-ORIGIN
L_00050496:
    mov.b r0,@(0x7,r4)
    .org 0x50498-ORIGIN
L_00050498:
    extu.b r11,r11
    .org 0x5049a-ORIGIN
L_0005049a:
    mov r11,r0
    .org 0x5049c-ORIGIN
L_0005049c:
    cmp/eq #0x1,r0
    .org 0x5049e-ORIGIN
L_0005049e:
    bf L_000504b2
    .org 0x504a0-ORIGIN
L_000504a0:
    mov.l P_000506b0,r4
    .org 0x504a2-ORIGIN
L_000504a2:
    mov.b @(0x7,r4),r0
    .org 0x504a4-ORIGIN
L_000504a4:
    tst r0,r0
    .org 0x504a6-ORIGIN
L_000504a6:
    bf L_000504b2
    .org 0x504a8-ORIGIN
L_000504a8:
    mov r15,r5
    .org 0x504aa-ORIGIN
L_000504aa:
    add #0x2,r5
    .org 0x504ac-ORIGIN
L_000504ac:
    mov.b @(0x1,r5),r0
    .org 0x504ae-ORIGIN
L_000504ae:
    mov #0x2,r11
    .org 0x504b0-ORIGIN
L_000504b0:
    mov.b r0,@(0x8,r4)
    .org 0x504b2-ORIGIN
L_000504b2:
    extu.b r11,r11
    .org 0x504b4-ORIGIN
L_000504b4:
    mov r11,r0
    .org 0x504b6-ORIGIN
L_000504b6:
    cmp/eq #0x2,r0
    .org 0x504b8-ORIGIN
L_000504b8:
    bt L_000504be
    .org 0x504ba-ORIGIN
L_000504ba:
    bra L_000505ae
    .org 0x504bc-ORIGIN
L_000504bc:
    nop
    .org 0x504be-ORIGIN
L_000504be:
    mov.l P_000506b0,r4
    .org 0x504c0-ORIGIN
L_000504c0:
    mov.b @(0x8,r4),r0
    .org 0x504c2-ORIGIN
L_000504c2:
    tst r0,r0
    .org 0x504c4-ORIGIN
L_000504c4:
    bf L_000505ae
    .org 0x504c6-ORIGIN
L_000504c6:
    bra L_000505ae
    .org 0x504c8-ORIGIN
L_000504c8:
    mov #0x3,r11
    .org 0x504ca-ORIGIN
L_000504ca:
    tst r4,r4
    .org 0x504cc-ORIGIN
L_000504cc:
    bt L_000504d6
    .org 0x504ce-ORIGIN
L_000504ce:
    tst r12,r12
    .org 0x504d0-ORIGIN
L_000504d0:
    bf L_000504d6
    .org 0x504d2-ORIGIN
L_000504d2:
    bra L_0005059e
    .org 0x504d4-ORIGIN
L_000504d4:
    mov #0x3,r11
    .org 0x504d6-ORIGIN
L_000504d6:
    tst r12,r12
    .org 0x504d8-ORIGIN
L_000504d8:
    bt L_000505ae
    .org 0x504da-ORIGIN
L_000504da:
    mov r11,r0
    .org 0x504dc-ORIGIN
L_000504dc:
    cmp/eq #0x3,r0
    .org 0x504de-ORIGIN
L_000504de:
    bf L_000505ae
    .org 0x504e0-ORIGIN
L_000504e0:
    mov.l P_000506b4,r5
    .org 0x504e2-ORIGIN
L_000504e2:
    mov.b @r5,r0
    .org 0x504e4-ORIGIN
L_000504e4:
    tst #0x20,r0
    .org 0x504e6-ORIGIN
L_000504e6:
    bf L_00050596
    .org 0x504e8-ORIGIN
L_000504e8:
    mov.l P_000506b8,r2
    .org 0x504ea-ORIGIN
L_000504ea:
    mov.b @r2,r0
    .org 0x504ec-ORIGIN
L_000504ec:
    tst #0x2,r0
    .org 0x504ee-ORIGIN
L_000504ee:
    bf L_00050500
    .org 0x504f0-ORIGIN
L_000504f0:
    mov.l P_000506bc,r5
    .org 0x504f2-ORIGIN
L_000504f2:
    mov.b @r5,r0
    .org 0x504f4-ORIGIN
L_000504f4:
    tst #0x80,r0
    .org 0x504f6-ORIGIN
L_000504f6:
    bf L_00050596
    .org 0x504f8-ORIGIN
L_000504f8:
    mov.l P_000506c0,r5
    .org 0x504fa-ORIGIN
L_000504fa:
    mov.b @(0x1,r5),r0
    .org 0x504fc-ORIGIN
L_000504fc:
    tst #0x10,r0
    .org 0x504fe-ORIGIN
L_000504fe:
    bt L_00050596
    .org 0x50500-ORIGIN
L_00050500:
    mov.l P_000506c4,r2
    .org 0x50502-ORIGIN
L_00050502:
    mov #0x17,r0
    .org 0x50504-ORIGIN
L_00050504:
    mov.l P_000506c8,r4
    .org 0x50506-ORIGIN
L_00050506:
    mov.b @(r0,r2),r5
    .org 0x50508-ORIGIN
L_00050508:
    mov.b @(0x4,r4),r0
    .org 0x5050a-ORIGIN
L_0005050a:
    cmp/hi r0,r5
    .org 0x5050c-ORIGIN
L_0005050c:
    bt/s L_0005058e
    .org 0x5050e-ORIGIN
L_0005050e:
    mov #0x0,r11
    .org 0x50510-ORIGIN
L_00050510:
    mov.l P_000506bc,r5
    .org 0x50512-ORIGIN
L_00050512:
    mov.b @r5,r0
    .org 0x50514-ORIGIN
L_00050514:
    tst #0x80,r0
    .org 0x50516-ORIGIN
L_00050516:
    bt L_0005054a
    .org 0x50518-ORIGIN
L_00050518:
    mov.l P_000506c4,r3
    .org 0x5051a-ORIGIN
L_0005051a:
    mov.l P_000506cc,r2
    .org 0x5051c-ORIGIN
L_0005051c:
    mov.w @(0x1a,r3),r0
    .org 0x5051e-ORIGIN
L_0005051e:
    mov.l P_000506c8,r1
    .org 0x50520-ORIGIN
L_00050520:
    extu.w r0,r4
    .org 0x50522-ORIGIN
L_00050522:
    mov #0x7a,r0
    .org 0x50524-ORIGIN
L_00050524:
    mov.b @(r0,r2),r7
    .org 0x50526-ORIGIN
L_00050526:
    mov.b @(0x3,r1),r0
    .org 0x50528-ORIGIN
L_00050528:
    extu.b r7,r7
    .org 0x5052a-ORIGIN
L_0005052a:
    extu.b r0,r2
    .org 0x5052c-ORIGIN
L_0005052c:
    mul.l r7,r2
    .org 0x5052e-ORIGIN
L_0005052e:
    sts macl,r2
    .org 0x50530-ORIGIN
L_00050530:
    cmp/gt r2,r4
    .org 0x50532-ORIGIN
L_00050532:
    bf L_0005056e
    .org 0x50534-ORIGIN
L_00050534:
    mov.l P_000506c4,r3
    .org 0x50536-ORIGIN
L_00050536:
    mov.w @(0x1a,r3),r0
    .org 0x50538-ORIGIN
L_00050538:
    extu.w r0,r4
    .org 0x5053a-ORIGIN
L_0005053a:
    mov.b @(0x2,r1),r0
    .org 0x5053c-ORIGIN
L_0005053c:
    extu.b r0,r2
    .org 0x5053e-ORIGIN
L_0005053e:
    mul.l r7,r2
    .org 0x50540-ORIGIN
L_00050540:
    sts macl,r2
    .org 0x50542-ORIGIN
L_00050542:
    cmp/gt r2,r4
    .org 0x50544-ORIGIN
L_00050544:
    bf L_0005056a
    .org 0x50546-ORIGIN
L_00050546:
    bra L_00050570
    .org 0x50548-ORIGIN
L_00050548:
    nop
    .org 0x5054a-ORIGIN
L_0005054a:
    mov.w P_00050552,r0
    .org 0x5054c-ORIGIN
L_0005054c:
    mov.l P_000506c8,r3
    .org 0x5054e-ORIGIN
L_0005054e:
    bra L_00050554
    .org 0x50550-ORIGIN
L_00050550:
    nop
    .org 0x50552-ORIGIN
P_00050552:
    .byte 0x02
    .org 0x50553-ORIGIN
P_00050553:
    .byte 0x8b
    .org 0x50554-ORIGIN
L_00050554:
    mov.b @(r0,r9),r4
    .org 0x50556-ORIGIN
L_00050556:
    mov.b @r3,r2
    .org 0x50558-ORIGIN
L_00050558:
    extu.b r4,r4
    .org 0x5055a-ORIGIN
L_0005055a:
    extu.b r2,r2
    .org 0x5055c-ORIGIN
L_0005055c:
    cmp/ge r2,r4
    .org 0x5055e-ORIGIN
L_0005055e:
    bt L_0005056e
    .org 0x50560-ORIGIN
L_00050560:
    mov.l P_000506c8,r3
    .org 0x50562-ORIGIN
L_00050562:
    mov.b @(0x1,r3),r0
    .org 0x50564-ORIGIN
L_00050564:
    extu.b r0,r2
    .org 0x50566-ORIGIN
L_00050566:
    cmp/ge r2,r4
    .org 0x50568-ORIGIN
L_00050568:
    bf L_00050570
    .org 0x5056a-ORIGIN
L_0005056a:
    bra L_00050570
    .org 0x5056c-ORIGIN
L_0005056c:
    mov #0x1,r6
    .org 0x5056e-ORIGIN
L_0005056e:
    mov #0x2,r6
    .org 0x50570-ORIGIN
L_00050570:
    mov.w P_0005068c,r0
    .org 0x50572-ORIGIN
L_00050572:
    mov.l P_000506d0,r5
    .org 0x50574-ORIGIN
L_00050574:
    mov.b r6,@(r0,r9)
    .org 0x50576-ORIGIN
L_00050576:
    extu.b r6,r6
    .org 0x50578-ORIGIN
L_00050578:
    mov r6,r0
    .org 0x5057a-ORIGIN
L_0005057a:
    mov.b @(r0,r5),r2
    .org 0x5057c-ORIGIN
L_0005057c:
    mov.w P_0005068e,r0
    .org 0x5057e-ORIGIN
L_0005057e:
    mov.l P_000506d4,r5
    .org 0x50580-ORIGIN
L_00050580:
    mov.b r2,@(r0,r9)
    .org 0x50582-ORIGIN
L_00050582:
    mov r6,r0
    .org 0x50584-ORIGIN
L_00050584:
    mov.b @(r0,r5),r2
    .org 0x50586-ORIGIN
L_00050586:
    mov #-0x1,r6
    .org 0x50588-ORIGIN
L_00050588:
    mov.w P_00050690,r0
    .org 0x5058a-ORIGIN
L_0005058a:
    bra L_000505ae
    .org 0x5058c-ORIGIN
L_0005058c:
    mov.b r2,@(r0,r9)
    .org 0x5058e-ORIGIN
L_0005058e:
    mov.w P_0005068c,r0
    .org 0x50590-ORIGIN
L_00050590:
    mov #0xa,r2
    .org 0x50592-ORIGIN
L_00050592:
    bra L_0005059e
    .org 0x50594-ORIGIN
L_00050594:
    mov.b r2,@(r0,r9)
    .org 0x50596-ORIGIN
L_00050596:
    mov.l P_000506b0,r4
    .org 0x50598-ORIGIN
L_00050598:
    mov r7,r0
    .org 0x5059a-ORIGIN
L_0005059a:
    mov #0x4,r11
    .org 0x5059c-ORIGIN
L_0005059c:
    mov.b r0,@(0x9,r4)
    .org 0x5059e-ORIGIN
L_0005059e:
    mov.w P_0005068e,r0
    .org 0x505a0-ORIGIN
L_000505a0:
    mov #-0x1,r2
    .org 0x505a2-ORIGIN
L_000505a2:
    mov.b r2,@(r0,r9)
    .org 0x505a4-ORIGIN
L_000505a4:
    mov #0x0,r2
    .org 0x505a6-ORIGIN
L_000505a6:
    mov.w P_00050690,r0
    .org 0x505a8-ORIGIN
L_000505a8:
    mov.b r2,@(r0,r9)
    .org 0x505aa-ORIGIN
L_000505aa:
    mov.w P_00050692,r0
    .org 0x505ac-ORIGIN
L_000505ac:
    mov.b r2,@(r0,r9)
    .org 0x505ae-ORIGIN
L_000505ae:
    extu.b r11,r11
    .org 0x505b0-ORIGIN
L_000505b0:
    mov r11,r0
    .org 0x505b2-ORIGIN
L_000505b2:
    cmp/eq #0x4,r0
    .org 0x505b4-ORIGIN
L_000505b4:
    bf L_000505c0
    .org 0x505b6-ORIGIN
L_000505b6:
    mov.l P_000506b0,r4
    .org 0x505b8-ORIGIN
L_000505b8:
    mov.b @(0x9,r4),r0
    .org 0x505ba-ORIGIN
L_000505ba:
    tst r0,r0
    .org 0x505bc-ORIGIN
L_000505bc:
    bf L_000505c0
    .org 0x505be-ORIGIN
L_000505be:
    mov #0x0,r11
    .org 0x505c0-ORIGIN
L_000505c0:
    mov.w P_0005068e,r0
    .org 0x505c2-ORIGIN
L_000505c2:
    mov #-0x1,r4
    .org 0x505c4-ORIGIN
L_000505c4:
    extu.b r4,r4
    .org 0x505c6-ORIGIN
L_000505c6:
    mov.b @(r0,r9),r5
    .org 0x505c8-ORIGIN
L_000505c8:
    extu.b r5,r5
    .org 0x505ca-ORIGIN
L_000505ca:
    cmp/eq r4,r5
    .org 0x505cc-ORIGIN
L_000505cc:
    bt L_000505f6
    .org 0x505ce-ORIGIN
L_000505ce:
    extu.b r6,r6
    .org 0x505d0-ORIGIN
L_000505d0:
    cmp/eq r4,r6
    .org 0x505d2-ORIGIN
L_000505d2:
    bt L_000505de
    .org 0x505d4-ORIGIN
L_000505d4:
    tst r5,r5
    .org 0x505d6-ORIGIN
L_000505d6:
    bt L_000505de
    .org 0x505d8-ORIGIN
L_000505d8:
    add #-0x1,r5
    .org 0x505da-ORIGIN
L_000505da:
    extu.b r5,r5
    .org 0x505dc-ORIGIN
L_000505dc:
    mov.b r5,@(r0,r9)
    .org 0x505de-ORIGIN
L_000505de:
    extu.b r5,r5
    .org 0x505e0-ORIGIN
L_000505e0:
    tst r5,r5
    .org 0x505e2-ORIGIN
L_000505e2:
    bf L_000505f6
    .org 0x505e4-ORIGIN
L_000505e4:
    mov.w P_0005068e,r0
    .org 0x505e6-ORIGIN
L_000505e6:
    mov #-0x1,r2
    .org 0x505e8-ORIGIN
L_000505e8:
    mov.b r2,@(r0,r9)
    .org 0x505ea-ORIGIN
L_000505ea:
    mov.w P_00050690,r0
    .org 0x505ec-ORIGIN
L_000505ec:
    mov.b @(r0,r9),r2
    .org 0x505ee-ORIGIN
L_000505ee:
    mov.w P_00050692,r0
    .org 0x505f0-ORIGIN
L_000505f0:
    bra L_000505f6
    .org 0x505f2-ORIGIN
L_000505f2:
    mov.b r2,@(r0,r9)
    .org 0x505f4-ORIGIN
L_000505f4:
    mov #0x0,r11
    .org 0x505f6-ORIGIN
L_000505f6:
    mov.l P_000506d8,r6
    .org 0x505f8-ORIGIN
L_000505f8:
    mov.b @(0x4,r6),r0
    .org 0x505fa-ORIGIN
L_000505fa:
    tst #0x80,r0
    .org 0x505fc-ORIGIN
L_000505fc:
    bt L_0005060e
    .org 0x505fe-ORIGIN
L_000505fe:
    mov.w P_0005068e,r0
    .org 0x50600-ORIGIN
L_00050600:
    mov #-0x1,r2
    .org 0x50602-ORIGIN
L_00050602:
    mov.b r2,@(r0,r9)
    .org 0x50604-ORIGIN
L_00050604:
    mov #0x0,r2
    .org 0x50606-ORIGIN
L_00050606:
    mov.w P_00050690,r0
    .org 0x50608-ORIGIN
L_00050608:
    mov.b r2,@(r0,r9)
    .org 0x5060a-ORIGIN
L_0005060a:
    mov.w P_00050692,r0
    .org 0x5060c-ORIGIN
L_0005060c:
    mov.b r2,@(r0,r9)
    .org 0x5060e-ORIGIN
L_0005060e:
    mov.l P_000506b0,r4
    .org 0x50610-ORIGIN
L_00050610:
    mov #0x32,r0
    .org 0x50612-ORIGIN
L_00050612:
    mov.b @(r0,r4),r2
    .org 0x50614-ORIGIN
L_00050614:
    tst r2,r2
    .org 0x50616-ORIGIN
L_00050616:
    bt L_00050628
    .org 0x50618-ORIGIN
L_00050618:
    mov.w P_0005068e,r0
    .org 0x5061a-ORIGIN
L_0005061a:
    mov #-0x1,r2
    .org 0x5061c-ORIGIN
L_0005061c:
    mov.b r2,@(r0,r9)
    .org 0x5061e-ORIGIN
L_0005061e:
    mov #0x0,r2
    .org 0x50620-ORIGIN
L_00050620:
    mov.w P_00050690,r0
    .org 0x50622-ORIGIN
L_00050622:
    mov.b r2,@(r0,r9)
    .org 0x50624-ORIGIN
L_00050624:
    mov.w P_00050692,r0
    .org 0x50626-ORIGIN
L_00050626:
    mov.b r2,@(r0,r9)
    .org 0x50628-ORIGIN
L_00050628:
    mov.w P_00050694,r0
    .org 0x5062a-ORIGIN
L_0005062a:
    mov #0x6,r12
    .org 0x5062c-ORIGIN
L_0005062c:
    mov.b r11,@(r0,r9)
    .org 0x5062e-ORIGIN
L_0005062e:
    mov.w P_00050696,r0
    .org 0x50630-ORIGIN
L_00050630:
    mov.b @(r0,r9),r4
    .org 0x50632-ORIGIN
L_00050632:
    mov.w P_00050692,r0
    .org 0x50634-ORIGIN
L_00050634:
    extu.b r13,r13
    .org 0x50636-ORIGIN
L_00050636:
    mov.b @(r0,r9),r2
    .org 0x50638-ORIGIN
L_00050638:
    extu.b r2,r5
    .org 0x5063a-ORIGIN
L_0005063a:
    cmp/ge r5,r13
    .org 0x5063c-ORIGIN
L_0005063c:
    bt L_0005064e
    .org 0x5063e-ORIGIN
L_0005063e:
    add #0x1,r13
    .org 0x50640-ORIGIN
L_00050640:
    extu.b r4,r4
    .org 0x50642-ORIGIN
L_00050642:
    bsr L_00050766
    .org 0x50644-ORIGIN
L_00050644:
    extu.b r13,r13
    .org 0x50646-ORIGIN
L_00050646:
    cmp/ge r12,r13
    .org 0x50648-ORIGIN
L_00050648:
    mov r0,r4
    .org 0x5064a-ORIGIN
L_0005064a:
    bf/s L_00050632
    .org 0x5064c-ORIGIN
L_0005064c:
    or r0,r14
    .org 0x5064e-ORIGIN
L_0005064e:
    mov.w P_00050694,r0
    .org 0x50650-ORIGIN
L_00050650:
    mov.l P_000506dc,r2
    .org 0x50652-ORIGIN
L_00050652:
    mov.b @(r0,r9),r6
    .org 0x50654-ORIGIN
L_00050654:
    mov.l P_000506e0,r13
    .org 0x50656-ORIGIN
L_00050656:
    extu.b r6,r0
    .org 0x50658-ORIGIN
L_00050658:
    mov.b @(r0,r2),r6
    .org 0x5065a-ORIGIN
L_0005065a:
    mov #0x2f,r0
    .org 0x5065c-ORIGIN
L_0005065c:
    mov.b @(r0,r13),r4
    .org 0x5065e-ORIGIN
L_0005065e:
    mov r6,r2
    .org 0x50660-ORIGIN
L_00050660:
    or r14,r2
    .org 0x50662-ORIGIN
L_00050662:
    extu.b r2,r5
    .org 0x50664-ORIGIN
L_00050664:
    tst r5,r5
    .org 0x50666-ORIGIN
L_00050666:
    bf/s L_000506fc
    .org 0x50668-ORIGIN
L_00050668:
    extu.b r4,r2
    .org 0x5066a-ORIGIN
L_0005066a:
    mov.b @r10,r0
    .org 0x5066c-ORIGIN
L_0005066c:
    tst #0x40,r0
    .org 0x5066e-ORIGIN
L_0005066e:
    bf L_000506a4
    .org 0x50670-ORIGIN
L_00050670:
    mov r2,r0
    .org 0x50672-ORIGIN
L_00050672:
    tst #0x20,r0
    .org 0x50674-ORIGIN
L_00050674:
    bt L_000506a4
    .org 0x50676-ORIGIN
L_00050676:
    mov.l P_000506b4,r7
    .org 0x50678-ORIGIN
L_00050678:
    mov.b @r7,r0
    .org 0x5067a-ORIGIN
L_0005067a:
    tst #0x20,r0
    .org 0x5067c-ORIGIN
L_0005067c:
    bt L_00050698
    .org 0x5067e-ORIGIN
L_0005067e:
    mov r2,r0
    .org 0x50680-ORIGIN
L_00050680:
    or #0x80,r0
    .org 0x50682-ORIGIN
L_00050682:
    mov r0,r2
    .org 0x50684-ORIGIN
L_00050684:
    mov #0x2f,r0
    .org 0x50686-ORIGIN
L_00050686:
    mov.b r2,@(r0,r13)
    .org 0x50688-ORIGIN
L_00050688:
    bra L_000506a4
    .org 0x5068a-ORIGIN
L_0005068a:
    exts.b r2,r4
    .org 0x5068c-ORIGIN
P_0005068c:
    .byte 0x06
    .org 0x5068d-ORIGIN
P_0005068d:
    .byte 0xad
    .org 0x5068e-ORIGIN
P_0005068e:
    .byte 0x06
    .org 0x5068f-ORIGIN
P_0005068f:
    .byte 0xae
    .org 0x50690-ORIGIN
P_00050690:
    .byte 0x06
    .org 0x50691-ORIGIN
P_00050691:
    .byte 0xac
    .org 0x50692-ORIGIN
P_00050692:
    .byte 0x06
    .org 0x50693-ORIGIN
P_00050693:
    .byte 0xab
    .org 0x50694-ORIGIN
P_00050694:
    .byte 0x02
    .org 0x50695-ORIGIN
P_00050695:
    .byte 0x35
    .org 0x50696-ORIGIN
P_00050696:
    .byte 0x06
    .org 0x50697-ORIGIN
P_00050697:
    .byte 0xaa
    .org 0x50698-ORIGIN
L_00050698:
    mov #0x1f,r0
    .org 0x5069a-ORIGIN
L_0005069a:
    mov.b @(r0,r13),r0
    .org 0x5069c-ORIGIN
L_0005069c:
    or #0x40,r0
    .org 0x5069e-ORIGIN
L_0005069e:
    mov r0,r2
    .org 0x506a0-ORIGIN
L_000506a0:
    mov #0x1f,r0
    .org 0x506a2-ORIGIN
L_000506a2:
    mov.b r2,@(r0,r13)
    .org 0x506a4-ORIGIN
L_000506a4:
    mov.w P_000506ae,r0
    .org 0x506a6-ORIGIN
L_000506a6:
    mov #0x0,r2
    .org 0x506a8-ORIGIN
L_000506a8:
    mov.l P_000506e4,r5
    .org 0x506aa-ORIGIN
L_000506aa:
    bra L_000506e8
    .org 0x506ac-ORIGIN
L_000506ac:
    mov.b r2,@(r0,r9)
    .org 0x506ae-ORIGIN
P_000506ae:
    .byte 0x02
    .org 0x506af-ORIGIN
P_000506af:
    .byte 0x38
    .org 0x506b0-ORIGIN
P_000506b0:
    .byte 0xff
    .org 0x506b1-ORIGIN
P_000506b1:
    .byte 0xff
    .org 0x506b2-ORIGIN
P_000506b2:
    .byte 0x25
    .org 0x506b3-ORIGIN
P_000506b3:
    .byte 0x6a
    .org 0x506b4-ORIGIN
P_000506b4:
    .byte 0xff
    .org 0x506b5-ORIGIN
P_000506b5:
    .byte 0xff
    .org 0x506b6-ORIGIN
P_000506b6:
    .byte 0x24
    .org 0x506b7-ORIGIN
P_000506b7:
    .byte 0x58
    .org 0x506b8-ORIGIN
P_000506b8:
    .byte 0x00
    .org 0x506b9-ORIGIN
P_000506b9:
    .byte 0x00
    .org 0x506ba-ORIGIN
P_000506ba:
    .byte 0x87
    .org 0x506bb-ORIGIN
P_000506bb:
    .byte 0x11
    .org 0x506bc-ORIGIN
P_000506bc:
    .byte 0x00
    .org 0x506bd-ORIGIN
P_000506bd:
    .byte 0x00
    .org 0x506be-ORIGIN
P_000506be:
    .byte 0x8b
    .org 0x506bf-ORIGIN
P_000506bf:
    .byte 0x3f
    .org 0x506c0-ORIGIN
P_000506c0:
    .byte 0xff
    .org 0x506c1-ORIGIN
P_000506c1:
    .byte 0xff
    .org 0x506c2-ORIGIN
P_000506c2:
    .byte 0x24
    .org 0x506c3-ORIGIN
P_000506c3:
    .byte 0xce
    .org 0x506c4-ORIGIN
P_000506c4:
    .byte 0xff
    .org 0x506c5-ORIGIN
P_000506c5:
    .byte 0xff
    .org 0x506c6-ORIGIN
P_000506c6:
    .byte 0x11
    .org 0x506c7-ORIGIN
P_000506c7:
    .byte 0x9c
    .org 0x506c8-ORIGIN
P_000506c8:
    .byte 0x00
    .org 0x506c9-ORIGIN
P_000506c9:
    .byte 0x00
    .org 0x506ca-ORIGIN
P_000506ca:
    .byte 0x8c
    .org 0x506cb-ORIGIN
P_000506cb:
    .byte 0x1a
    .org 0x506cc-ORIGIN
P_000506cc:
    .byte 0xff
    .org 0x506cd-ORIGIN
P_000506cd:
    .byte 0xff
    .org 0x506ce-ORIGIN
P_000506ce:
    .byte 0x10
    .org 0x506cf-ORIGIN
P_000506cf:
    .byte 0x94
    .org 0x506d0-ORIGIN
P_000506d0:
    .byte 0x00
    .org 0x506d1-ORIGIN
P_000506d1:
    .byte 0x01
    .org 0x506d2-ORIGIN
P_000506d2:
    .byte 0x26
    .org 0x506d3-ORIGIN
P_000506d3:
    .byte 0x9d
    .org 0x506d4-ORIGIN
P_000506d4:
    .byte 0x00
    .org 0x506d5-ORIGIN
P_000506d5:
    .byte 0x01
    .org 0x506d6-ORIGIN
P_000506d6:
    .byte 0x26
    .org 0x506d7-ORIGIN
P_000506d7:
    .byte 0x9a
    .org 0x506d8-ORIGIN
P_000506d8:
    .byte 0xff
    .org 0x506d9-ORIGIN
P_000506d9:
    .byte 0xff
    .org 0x506da-ORIGIN
P_000506da:
    .byte 0x42
    .org 0x506db-ORIGIN
P_000506db:
    .byte 0x4c
    .org 0x506dc-ORIGIN
P_000506dc:
    .byte 0x00
    .org 0x506dd-ORIGIN
P_000506dd:
    .byte 0x02
    .org 0x506de-ORIGIN
P_000506de:
    .byte 0x37
    .org 0x506df-ORIGIN
P_000506df:
    .byte 0x1c
    .org 0x506e0-ORIGIN
P_000506e0:
    .byte 0xff
    .org 0x506e1-ORIGIN
P_000506e1:
    .byte 0xff
    .org 0x506e2-ORIGIN
P_000506e2:
    .byte 0x24
    .org 0x506e3-ORIGIN
P_000506e3:
    .byte 0x70
    .org 0x506e4-ORIGIN
P_000506e4:
    .byte 0x00
    .org 0x506e5-ORIGIN
P_000506e5:
    .byte 0x00
    .org 0x506e6-ORIGIN
P_000506e6:
    .byte 0x85
    .org 0x506e7-ORIGIN
P_000506e7:
    .byte 0xf6
    .org 0x506e8-ORIGIN
L_000506e8:
    mov r4,r0
    .org 0x506ea-ORIGIN
L_000506ea:
    and #0xdf,r0
    .org 0x506ec-ORIGIN
L_000506ec:
    mov r0,r2
    .org 0x506ee-ORIGIN
L_000506ee:
    mov #0x2f,r0
    .org 0x506f0-ORIGIN
L_000506f0:
    mov.b r2,@(r0,r13)
    .org 0x506f2-ORIGIN
L_000506f2:
    mov #0x22,r0
    .org 0x506f4-ORIGIN
L_000506f4:
    mov.b @r5,r2
    .org 0x506f6-ORIGIN
L_000506f6:
    mov.l P_000508e8,r5
    .org 0x506f8-ORIGIN
L_000506f8:
    bra L_0005074e
    .org 0x506fa-ORIGIN
L_000506fa:
    mov.b r2,@(r0,r5)
    .org 0x506fc-ORIGIN
L_000506fc:
    mov r2,r0
    .org 0x506fe-ORIGIN
L_000506fe:
    tst #0x20,r0
    .org 0x50700-ORIGIN
L_00050700:
    bf L_00050730
    .org 0x50702-ORIGIN
L_00050702:
    mov.l P_000508ec,r3
    .org 0x50704-ORIGIN
L_00050704:
    mov #0x7a,r0
    .org 0x50706-ORIGIN
L_00050706:
    mov #-0x2,r1
    .org 0x50708-ORIGIN
L_00050708:
    mov.b @(r0,r3),r5
    .org 0x5070a-ORIGIN
L_0005070a:
    mov #-0x3,r3
    .org 0x5070c-ORIGIN
L_0005070c:
    mov.w P_0005082a,r0
    .org 0x5070e-ORIGIN
L_0005070e:
    mov.b r5,@(r0,r9)
    .org 0x50710-ORIGIN
L_00050710:
    mov.w P_0005082c,r0
    .org 0x50712-ORIGIN
L_00050712:
    mov.b @(r0,r9),r7
    .org 0x50714-ORIGIN
L_00050714:
    mov.w P_0005082e,r0
    .org 0x50716-ORIGIN
L_00050716:
    extu.b r7,r7
    .org 0x50718-ORIGIN
L_00050718:
    mov.b @(r0,r9),r4
    .org 0x5071a-ORIGIN
L_0005071a:
    and r1,r7
    .org 0x5071c-ORIGIN
L_0005071c:
    extu.b r7,r5
    .org 0x5071e-ORIGIN
L_0005071e:
    mov.w P_0005082c,r0
    .org 0x50720-ORIGIN
L_00050720:
    extu.b r4,r4
    .org 0x50722-ORIGIN
L_00050722:
    and r1,r4
    .org 0x50724-ORIGIN
L_00050724:
    and r3,r5
    .org 0x50726-ORIGIN
L_00050726:
    mov.b r5,@(r0,r9)
    .org 0x50728-ORIGIN
L_00050728:
    extu.b r4,r5
    .org 0x5072a-ORIGIN
L_0005072a:
    mov.w P_0005082e,r0
    .org 0x5072c-ORIGIN
L_0005072c:
    and r3,r5
    .org 0x5072e-ORIGIN
L_0005072e:
    mov.b r5,@(r0,r9)
    .org 0x50730-ORIGIN
L_00050730:
    mov #0x20,r0
    .org 0x50732-ORIGIN
L_00050732:
    or r0,r2
    .org 0x50734-ORIGIN
L_00050734:
    mov #0x2f,r0
    .org 0x50736-ORIGIN
L_00050736:
    mov.b r2,@(r0,r13)
    .org 0x50738-ORIGIN
L_00050738:
    exts.b r2,r0
    .org 0x5073a-ORIGIN
L_0005073a:
    and #0x7f,r0
    .org 0x5073c-ORIGIN
L_0005073c:
    mov r0,r2
    .org 0x5073e-ORIGIN
L_0005073e:
    mov #0x2f,r0
    .org 0x50740-ORIGIN
L_00050740:
    mov.b r2,@(r0,r13)
    .org 0x50742-ORIGIN
L_00050742:
    mov #0x1f,r0
    .org 0x50744-ORIGIN
L_00050744:
    mov.b @(r0,r13),r0
    .org 0x50746-ORIGIN
L_00050746:
    and #0xbf,r0
    .org 0x50748-ORIGIN
L_00050748:
    mov r0,r2
    .org 0x5074a-ORIGIN
L_0005074a:
    mov #0x1f,r0
    .org 0x5074c-ORIGIN
L_0005074c:
    mov.b r2,@(r0,r13)
    .org 0x5074e-ORIGIN
L_0005074e:
    or r14,r6
    .org 0x50750-ORIGIN
L_00050750:
    extu.b r6,r0
    .org 0x50752-ORIGIN
L_00050752:
    add #0x4,r15
    .org 0x50754-ORIGIN
L_00050754:
    lds.l @r15+,macl
    .org 0x50756-ORIGIN
L_00050756:
    lds.l @r15+,pr
    .org 0x50758-ORIGIN
L_00050758:
    mov.l @r15+,r14
    .org 0x5075a-ORIGIN
L_0005075a:
    mov.l @r15+,r13
    .org 0x5075c-ORIGIN
L_0005075c:
    mov.l @r15+,r12
    .org 0x5075e-ORIGIN
L_0005075e:
    mov.l @r15+,r11
    .org 0x50760-ORIGIN
L_00050760:
    mov.l @r15+,r10
    .org 0x50762-ORIGIN
L_00050762:
    rts
    .org 0x50764-ORIGIN
L_00050764:
    mov.l @r15+,r9
    .org 0x50766-ORIGIN
L_00050766:
    extu.b r4,r0
    .org 0x50768-ORIGIN
L_00050768:
    cmp/eq #0x1,r0
    .org 0x5076a-ORIGIN
L_0005076a:
    bt/s L_00050796
    .org 0x5076c-ORIGIN
L_0005076c:
    mov #0x0,r2
    .org 0x5076e-ORIGIN
L_0005076e:
    cmp/eq #0x2,r0
    .org 0x50770-ORIGIN
L_00050770:
    bt L_00050792
    .org 0x50772-ORIGIN
L_00050772:
    cmp/eq #0x4,r0
    .org 0x50774-ORIGIN
L_00050774:
    bt L_0005078e
    .org 0x50776-ORIGIN
L_00050776:
    cmp/eq #0x8,r0
    .org 0x50778-ORIGIN
L_00050778:
    bt L_0005078a
    .org 0x5077a-ORIGIN
L_0005077a:
    cmp/eq #0x10,r0
    .org 0x5077c-ORIGIN
L_0005077c:
    bt L_00050786
    .org 0x5077e-ORIGIN
L_0005077e:
    cmp/eq #0x20,r0
    .org 0x50780-ORIGIN
L_00050780:
    bf L_00050798
    .org 0x50782-ORIGIN
L_00050782:
    bra L_00050798
    .org 0x50784-ORIGIN
L_00050784:
    mov #0x1,r2
    .org 0x50786-ORIGIN
L_00050786:
    bra L_00050798
    .org 0x50788-ORIGIN
L_00050788:
    mov #0x20,r2
    .org 0x5078a-ORIGIN
L_0005078a:
    bra L_00050798
    .org 0x5078c-ORIGIN
L_0005078c:
    mov #0x10,r2
    .org 0x5078e-ORIGIN
L_0005078e:
    bra L_00050798
    .org 0x50790-ORIGIN
L_00050790:
    mov #0x8,r2
    .org 0x50792-ORIGIN
L_00050792:
    bra L_00050798
    .org 0x50794-ORIGIN
L_00050794:
    mov #0x4,r2
    .org 0x50796-ORIGIN
L_00050796:
    mov #0x2,r2
    .org 0x50798-ORIGIN
L_00050798:
    rts
    .org 0x5079a-ORIGIN
L_0005079a:
    extu.b r2,r0
    .org 0x5082a-ORIGIN
P_0005082a:
    .byte 0x02
    .org 0x5082b-ORIGIN
P_0005082b:
    .byte 0x38
    .org 0x5082c-ORIGIN
P_0005082c:
    .byte 0x02
    .org 0x5082d-ORIGIN
P_0005082d:
    .byte 0xb0
    .org 0x5082e-ORIGIN
P_0005082e:
    .byte 0x05
    .org 0x5082f-ORIGIN
P_0005082f:
    .byte 0x31
    .org 0x508e8-ORIGIN
P_000508e8:
    .byte 0xff
    .org 0x508e9-ORIGIN
P_000508e9:
    .byte 0xff
    .org 0x508ea-ORIGIN
P_000508ea:
    .byte 0x24
    .org 0x508eb-ORIGIN
P_000508eb:
    .byte 0xf9
    .org 0x508ec-ORIGIN
P_000508ec:
    .byte 0xff
    .org 0x508ed-ORIGIN
P_000508ed:
    .byte 0xff
    .org 0x508ee-ORIGIN
P_000508ee:
    .byte 0x10
    .org 0x508ef-ORIGIN
P_000508ef:
    .byte 0x94
