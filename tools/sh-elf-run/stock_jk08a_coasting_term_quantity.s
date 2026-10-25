! Complete stock table producer and coasting-term consumer with real helpers.
    .text
    .balign 4
    .set ORIGIN,0x25e20
    .org 0x25e20-ORIGIN
L_00025e20:
    mov.l P_00025f10,r1
    .org 0x25e22-ORIGIN
L_00025e22:
    exts.w r4,r0
    .org 0x25e24-ORIGIN
L_00025e24:
    cmp/eq #-0x1,r0
    .org 0x25e26-ORIGIN
L_00025e26:
    bt L_00025e3e
    .org 0x25e28-ORIGIN
L_00025e28:
    mov r1,r6
    .org 0x25e2a-ORIGIN
L_00025e2a:
    mov r0,r2
    .org 0x25e2c-ORIGIN
L_00025e2c:
    shll r2
    .org 0x25e2e-ORIGIN
L_00025e2e:
    add r0,r2
    .org 0x25e30-ORIGIN
L_00025e30:
    add r2,r6
    .org 0x25e32-ORIGIN
L_00025e32:
    mov.b @(0x1,r6),r0
    .org 0x25e34-ORIGIN
L_00025e34:
    tst #0x80,r0
    .org 0x25e36-ORIGIN
L_00025e36:
    movt r0
    .org 0x25e38-ORIGIN
L_00025e38:
    xor #0x1,r0
    .org 0x25e3a-ORIGIN
L_00025e3a:
    bra L_00025e40
    .org 0x25e3c-ORIGIN
L_00025e3c:
    extu.b r0,r2
    .org 0x25e3e-ORIGIN
L_00025e3e:
    mov #0x0,r2
    .org 0x25e40-ORIGIN
L_00025e40:
    rts
    .org 0x25e42-ORIGIN
L_00025e42:
    mov r2,r0
    .org 0x25e4e-ORIGIN
L_00025e4e:
    sts.l pr,@-r15
    .org 0x25e50-ORIGIN
L_00025e50:
    bsr L_00025e20
    .org 0x25e52-ORIGIN
L_00025e52:
    mov #-0x1,r4
    .org 0x25e54-ORIGIN
L_00025e54:
    tst r0,r0
    .org 0x25e56-ORIGIN
L_00025e56:
    bf L_00025ec0
    .org 0x25e58-ORIGIN
L_00025e58:
    bsr L_00025e20
    .org 0x25e5a-ORIGIN
L_00025e5a:
    mov #-0x1,r4
    .org 0x25e5c-ORIGIN
L_00025e5c:
    tst r0,r0
    .org 0x25e5e-ORIGIN
L_00025e5e:
    bf L_00025ec0
    .org 0x25e60-ORIGIN
L_00025e60:
    bsr L_00025e20
    .org 0x25e62-ORIGIN
L_00025e62:
    mov #0x14,r4
    .org 0x25e64-ORIGIN
L_00025e64:
    tst r0,r0
    .org 0x25e66-ORIGIN
L_00025e66:
    bf L_00025ec0
    .org 0x25e68-ORIGIN
L_00025e68:
    bsr L_00025e20
    .org 0x25e6a-ORIGIN
L_00025e6a:
    mov #0x47,r4
    .org 0x25e6c-ORIGIN
L_00025e6c:
    tst r0,r0
    .org 0x25e6e-ORIGIN
L_00025e6e:
    bf L_00025ec0
    .org 0x25e70-ORIGIN
L_00025e70:
    bsr L_00025e20
    .org 0x25e72-ORIGIN
L_00025e72:
    mov #0x48,r4
    .org 0x25e74-ORIGIN
L_00025e74:
    tst r0,r0
    .org 0x25e76-ORIGIN
L_00025e76:
    bf L_00025ec0
    .org 0x25e78-ORIGIN
L_00025e78:
    bsr L_00025e20
    .org 0x25e7a-ORIGIN
L_00025e7a:
    mov #0x49,r4
    .org 0x25e7c-ORIGIN
L_00025e7c:
    tst r0,r0
    .org 0x25e7e-ORIGIN
L_00025e7e:
    bf L_00025ec0
    .org 0x25e80-ORIGIN
L_00025e80:
    bsr L_00025e20
    .org 0x25e82-ORIGIN
L_00025e82:
    mov #0x4a,r4
    .org 0x25e84-ORIGIN
L_00025e84:
    tst r0,r0
    .org 0x25e86-ORIGIN
L_00025e86:
    bf L_00025ec0
    .org 0x25e88-ORIGIN
L_00025e88:
    bsr L_00025e20
    .org 0x25e8a-ORIGIN
L_00025e8a:
    mov #0x4b,r4
    .org 0x25e8c-ORIGIN
L_00025e8c:
    tst r0,r0
    .org 0x25e8e-ORIGIN
L_00025e8e:
    bf L_00025ec0
    .org 0x25e90-ORIGIN
L_00025e90:
    bsr L_00025e20
    .org 0x25e92-ORIGIN
L_00025e92:
    mov #0x4c,r4
    .org 0x25e94-ORIGIN
L_00025e94:
    tst r0,r0
    .org 0x25e96-ORIGIN
L_00025e96:
    bf L_00025ec0
    .org 0x25e98-ORIGIN
L_00025e98:
    mov #-0x76,r3
    .org 0x25e9a-ORIGIN
L_00025e9a:
    extu.b r3,r4
    .org 0x25e9c-ORIGIN
L_00025e9c:
    bsr L_00025e20
    .org 0x25e9e-ORIGIN
L_00025e9e:
    nop
    .org 0x25ea0-ORIGIN
L_00025ea0:
    tst r0,r0
    .org 0x25ea2-ORIGIN
L_00025ea2:
    bf L_00025ec0
    .org 0x25ea4-ORIGIN
L_00025ea4:
    mov #-0x75,r3
    .org 0x25ea6-ORIGIN
L_00025ea6:
    extu.b r3,r4
    .org 0x25ea8-ORIGIN
L_00025ea8:
    bsr L_00025e20
    .org 0x25eaa-ORIGIN
L_00025eaa:
    nop
    .org 0x25eac-ORIGIN
L_00025eac:
    tst r0,r0
    .org 0x25eae-ORIGIN
L_00025eae:
    bf L_00025ec0
    .org 0x25eb0-ORIGIN
L_00025eb0:
    mov #-0x74,r3
    .org 0x25eb2-ORIGIN
L_00025eb2:
    extu.b r3,r4
    .org 0x25eb4-ORIGIN
L_00025eb4:
    bsr L_00025e20
    .org 0x25eb6-ORIGIN
L_00025eb6:
    nop
    .org 0x25eb8-ORIGIN
L_00025eb8:
    tst r0,r0
    .org 0x25eba-ORIGIN
L_00025eba:
    bf L_00025ec0
    .org 0x25ebc-ORIGIN
L_00025ebc:
    bra L_00025ec2
    .org 0x25ebe-ORIGIN
L_00025ebe:
    mov #0x0,r2
    .org 0x25ec0-ORIGIN
L_00025ec0:
    mov #0x1,r2
    .org 0x25ec2-ORIGIN
L_00025ec2:
    lds.l @r15+,pr
    .org 0x25ec4-ORIGIN
L_00025ec4:
    rts
    .org 0x25ec6-ORIGIN
L_00025ec6:
    mov r2,r0
    .org 0x25f10-ORIGIN
P_00025f10:
    .byte 0xff
    .org 0x25f11-ORIGIN
P_00025f11:
    .byte 0xff
    .org 0x25f12-ORIGIN
P_00025f12:
    .byte 0x57
    .org 0x25f13-ORIGIN
P_00025f13:
    .byte 0x18
    .org 0x26370-ORIGIN
L_00026370:
    mov.w P_00026382,r0
    .org 0x26372-ORIGIN
L_00026372:
    extu.b r5,r5
    .org 0x26374-ORIGIN
L_00026374:
    cmp/hs r0,r5
    .org 0x26376-ORIGIN
L_00026376:
    bt L_0002637e
    .org 0x26378-ORIGIN
L_00026378:
    mov.l P_00026384,r6
    .org 0x2637a-ORIGIN
L_0002637a:
    jmp @r6
    .org 0x2637c-ORIGIN
L_0002637c:
    mov #0x0,r3
    .org 0x2637e-ORIGIN
L_0002637e:
    rts
    .org 0x26380-ORIGIN
L_00026380:
    mov.b @(0x7,r4),r0
    .org 0x26382-ORIGIN
P_00026382:
    .byte 0x00
    .org 0x26383-ORIGIN
P_00026383:
    .byte 0xe0
    .org 0x26384-ORIGIN
P_00026384:
    .byte 0x00
    .org 0x26385-ORIGIN
P_00026385:
    .byte 0x02
    .org 0x26386-ORIGIN
P_00026386:
    .byte 0x6a
    .org 0x26387-ORIGIN
P_00026387:
    .byte 0x80
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
    .org 0x2c626-ORIGIN
L_0002c626:
    sts.l pr,@-r15
    .org 0x2c628-ORIGIN
L_0002c628:
    mov.l P_0002c7dc,r5
    .org 0x2c62a-ORIGIN
L_0002c62a:
    mov.l P_0002c810,r4
    .org 0x2c62c-ORIGIN
L_0002c62c:
    mov.b @(0x5,r5),r0
    .org 0x2c62e-ORIGIN
L_0002c62e:
    mov.l P_0002c804,r2
    .org 0x2c630-ORIGIN
L_0002c630:
    jsr @r2
    .org 0x2c632-ORIGIN
L_0002c632:
    extu.b r0,r5
    .org 0x2c634-ORIGIN
L_0002c634:
    mov.l P_0002c814,r5
    .org 0x2c636-ORIGIN
L_0002c636:
    extu.b r0,r6
    .org 0x2c638-ORIGIN
L_0002c638:
    mov.l P_0002c818,r2
    .org 0x2c63a-ORIGIN
L_0002c63a:
    mov #0x22,r0
    .org 0x2c63c-ORIGIN
L_0002c63c:
    mov.w r6,@(r0,r5)
    .org 0x2c63e-ORIGIN
L_0002c63e:
    lds.l @r15+,pr
    .org 0x2c640-ORIGIN
L_0002c640:
    rts
    .org 0x2c642-ORIGIN
L_0002c642:
    mov.w r6,@(r0,r2)
    .org 0x2c7dc-ORIGIN
P_0002c7dc:
    .byte 0xff
    .org 0x2c7dd-ORIGIN
P_0002c7dd:
    .byte 0xff
    .org 0x2c7de-ORIGIN
P_0002c7de:
    .byte 0x10
    .org 0x2c7df-ORIGIN
P_0002c7df:
    .byte 0x72
    .org 0x2c804-ORIGIN
P_0002c804:
    .byte 0x00
    .org 0x2c805-ORIGIN
P_0002c805:
    .byte 0x02
    .org 0x2c806-ORIGIN
P_0002c806:
    .byte 0x63
    .org 0x2c807-ORIGIN
P_0002c807:
    .byte 0x70
    .org 0x2c810-ORIGIN
P_0002c810:
    .byte 0x00
    .org 0x2c811-ORIGIN
P_0002c811:
    .byte 0x01
    .org 0x2c812-ORIGIN
P_0002c812:
    .byte 0x22
    .org 0x2c813-ORIGIN
P_0002c813:
    .byte 0xe2
    .org 0x2c814-ORIGIN
P_0002c814:
    .byte 0xff
    .org 0x2c815-ORIGIN
P_0002c815:
    .byte 0xff
    .org 0x2c816-ORIGIN
P_0002c816:
    .byte 0x12
    .org 0x2c817-ORIGIN
P_0002c817:
    .byte 0x0e
    .org 0x2c818-ORIGIN
P_0002c818:
    .byte 0xff
    .org 0x2c819-ORIGIN
P_0002c819:
    .byte 0xff
    .org 0x2c81a-ORIGIN
P_0002c81a:
    .byte 0x12
    .org 0x2c81b-ORIGIN
P_0002c81b:
    .byte 0x4c
    .org 0x47120-ORIGIN
L_00047120:
    mov.l r12,@-r15
    .org 0x47122-ORIGIN
L_00047122:
    mov.l r13,@-r15
    .org 0x47124-ORIGIN
L_00047124:
    sts.l pr,@-r15
    .org 0x47126-ORIGIN
L_00047126:
    stc.l gbr,@-r15
    .org 0x47128-ORIGIN
L_00047128:
    mov.l P_00047368,r0
    .org 0x4712a-ORIGIN
L_0004712a:
    ldc r0,gbr
    .org 0x4712c-ORIGIN
L_0004712c:
    add #-0x20,r15
    .org 0x4712e-ORIGIN
L_0004712e:
    mov.l P_0004736c,r12
    .org 0x47130-ORIGIN
L_00047130:
    mov.w P_0004727c,r0
    .org 0x47132-ORIGIN
L_00047132:
    mov.w @(r0,r12),r13
    .org 0x47134-ORIGIN
L_00047134:
    mov.b @(0xc,gbr),r0
    .org 0x47136-ORIGIN
L_00047136:
    tst #0x20,r0
    .org 0x47138-ORIGIN
L_00047138:
    bf L_0004713e
    .org 0x4713a-ORIGIN
L_0004713a:
    bra L_0004734a
    .org 0x4713c-ORIGIN
L_0004713c:
    nop
    .org 0x4713e-ORIGIN
L_0004713e:
    mov.b @(0x3,gbr),r0
    .org 0x47140-ORIGIN
L_00047140:
    tst #0x4,r0
    .org 0x47142-ORIGIN
L_00047142:
    bt L_00047148
    .org 0x47144-ORIGIN
L_00047144:
    bra L_0004734a
    .org 0x47146-ORIGIN
L_00047146:
    nop
    .org 0x47148-ORIGIN
L_00047148:
    mov.l P_00047370,r7
    .org 0x4714a-ORIGIN
L_0004714a:
    mov #0x7a,r0
    .org 0x4714c-ORIGIN
L_0004714c:
    mov.l P_00047374,r5
    .org 0x4714e-ORIGIN
L_0004714e:
    mov.b @(r0,r7),r6
    .org 0x47150-ORIGIN
L_00047150:
    mov.b @r5,r2
    .org 0x47152-ORIGIN
L_00047152:
    cmp/hs r2,r6
    .org 0x47154-ORIGIN
L_00047154:
    bt L_0004715a
    .org 0x47156-ORIGIN
L_00047156:
    bra L_0004734a
    .org 0x47158-ORIGIN
L_00047158:
    nop
    .org 0x4715a-ORIGIN
L_0004715a:
    mov.l P_00047378,r6
    .org 0x4715c-ORIGIN
L_0004715c:
    mov.b @(0x3,r6),r0
    .org 0x4715e-ORIGIN
L_0004715e:
    tst #0x40,r0
    .org 0x47160-ORIGIN
L_00047160:
    bt L_00047166
    .org 0x47162-ORIGIN
L_00047162:
    bra L_0004734a
    .org 0x47164-ORIGIN
L_00047164:
    nop
    .org 0x47166-ORIGIN
L_00047166:
    mov.l P_0004737c,r2
    .org 0x47168-ORIGIN
L_00047168:
    jsr @r2
    .org 0x4716a-ORIGIN
L_0004716a:
    nop
    .org 0x4716c-ORIGIN
L_0004716c:
    tst r0,r0
    .org 0x4716e-ORIGIN
L_0004716e:
    bt L_00047174
    .org 0x47170-ORIGIN
L_00047170:
    bra L_0004734a
    .org 0x47172-ORIGIN
L_00047172:
    nop
    .org 0x47174-ORIGIN
L_00047174:
    mov.l P_00047380,r2
    .org 0x47176-ORIGIN
L_00047176:
    jsr @r2
    .org 0x47178-ORIGIN
L_00047178:
    mov #-0x1,r4
    .org 0x4717a-ORIGIN
L_0004717a:
    tst r0,r0
    .org 0x4717c-ORIGIN
L_0004717c:
    bt L_00047182
    .org 0x4717e-ORIGIN
L_0004717e:
    bra L_0004734a
    .org 0x47180-ORIGIN
L_00047180:
    nop
    .org 0x47182-ORIGIN
L_00047182:
    mov.l P_00047384,r2
    .org 0x47184-ORIGIN
L_00047184:
    mov.b @(0x2,r2),r0
    .org 0x47186-ORIGIN
L_00047186:
    extu.b r0,r2
    .org 0x47188-ORIGIN
L_00047188:
    mov.l r2,@r15
    .org 0x4718a-ORIGIN
L_0004718a:
    mov.l P_00047388,r2
    .org 0x4718c-ORIGIN
L_0004718c:
    mov.l @r15,r6
    .org 0x4718e-ORIGIN
L_0004718e:
    mov.b @(0x3,r2),r0
    .org 0x47190-ORIGIN
L_00047190:
    extu.b r0,r2
    .org 0x47192-ORIGIN
L_00047192:
    mov.b @(0x27,gbr),r0
    .org 0x47194-ORIGIN
L_00047194:
    cmp/ge r2,r6
    .org 0x47196-ORIGIN
L_00047196:
    mov.l r2,@(0x4,r15)
    .org 0x47198-ORIGIN
L_00047198:
    bf/s L_000471a0
    .org 0x4719a-ORIGIN
L_0004719a:
    mov.b r0,@(0x8,r15)
    .org 0x4719c-ORIGIN
L_0004719c:
    bra L_0004734a
    .org 0x4719e-ORIGIN
L_0004719e:
    nop
    .org 0x471a0-ORIGIN
L_000471a0:
    mov.l P_0004738c,r2
    .org 0x471a2-ORIGIN
L_000471a2:
    mov.b @r2,r0
    .org 0x471a4-ORIGIN
L_000471a4:
    and #0x80,r0
    .org 0x471a6-ORIGIN
L_000471a6:
    tst r0,r0
    .org 0x471a8-ORIGIN
L_000471a8:
    bt/s L_000471b6
    .org 0x471aa-ORIGIN
L_000471aa:
    mov.b r0,@(0xc,r15)
    .org 0x471ac-ORIGIN
L_000471ac:
    mov.b @(0x1a,gbr),r0
    .org 0x471ae-ORIGIN
L_000471ae:
    tst #0x80,r0
    .org 0x471b0-ORIGIN
L_000471b0:
    bf L_000471b6
    .org 0x471b2-ORIGIN
L_000471b2:
    bra L_0004734a
    .org 0x471b4-ORIGIN
L_000471b4:
    nop
    .org 0x471b6-ORIGIN
L_000471b6:
    mov.b @(0xc,r15),r0
    .org 0x471b8-ORIGIN
L_000471b8:
    tst r0,r0
    .org 0x471ba-ORIGIN
L_000471ba:
    bt L_000471ea
    .org 0x471bc-ORIGIN
L_000471bc:
    mov.b @(0xc,gbr),r0
    .org 0x471be-ORIGIN
L_000471be:
    tst #0x80,r0
    .org 0x471c0-ORIGIN
L_000471c0:
    bt L_000471ea
    .org 0x471c2-ORIGIN
L_000471c2:
    mov.l P_00047370,r7
    .org 0x471c4-ORIGIN
L_000471c4:
    mov #0x7a,r0
    .org 0x471c6-ORIGIN
L_000471c6:
    mov.l P_00047390,r5
    .org 0x471c8-ORIGIN
L_000471c8:
    mov.b @(r0,r7),r2
    .org 0x471ca-ORIGIN
L_000471ca:
    mov.b @r5,r6
    .org 0x471cc-ORIGIN
L_000471cc:
    extu.b r2,r2
    .org 0x471ce-ORIGIN
L_000471ce:
    sub r6,r2
    .org 0x471d0-ORIGIN
L_000471d0:
    mov #-0x1,r6
    .org 0x471d2-ORIGIN
L_000471d2:
    exts.w r2,r2
    .org 0x471d4-ORIGIN
L_000471d4:
    extu.b r6,r6
    .org 0x471d6-ORIGIN
L_000471d6:
    cmp/gt r6,r2
    .org 0x471d8-ORIGIN
L_000471d8:
    bt L_000471dc
    .org 0x471da-ORIGIN
L_000471da:
    mov r2,r6
    .org 0x471dc-ORIGIN
L_000471dc:
    exts.w r6,r2
    .org 0x471de-ORIGIN
L_000471de:
    cmp/pz r2
    .org 0x471e0-ORIGIN
L_000471e0:
    bt L_000471e4
    .org 0x471e2-ORIGIN
L_000471e2:
    mov #0x0,r2
    .org 0x471e4-ORIGIN
L_000471e4:
    mov #0x10,r0
    .org 0x471e6-ORIGIN
L_000471e6:
    bra L_000471f0
    .org 0x471e8-ORIGIN
L_000471e8:
    mov.b r2,@(r0,r15)
    .org 0x471ea-ORIGIN
L_000471ea:
    mov.l P_00047370,r7
    .org 0x471ec-ORIGIN
L_000471ec:
    mov #0x7a,r0
    .org 0x471ee-ORIGIN
L_000471ee:
    mov.b @(r0,r7),r2
    .org 0x471f0-ORIGIN
L_000471f0:
    mov.w P_0004727e,r0
    .org 0x471f2-ORIGIN
L_000471f2:
    mov.b r2,@(r0,r12)
    .org 0x471f4-ORIGIN
L_000471f4:
    mov.b @(0x8,r15),r0
    .org 0x471f6-ORIGIN
L_000471f6:
    and #0x4,r0
    .org 0x471f8-ORIGIN
L_000471f8:
    mov r0,r2
    .org 0x471fa-ORIGIN
L_000471fa:
    mov r0,r7
    .org 0x471fc-ORIGIN
L_000471fc:
    mov #0x14,r0
    .org 0x471fe-ORIGIN
L_000471fe:
    tst r2,r2
    .org 0x47200-ORIGIN
L_00047200:
    bf/s L_0004725e
    .org 0x47202-ORIGIN
L_00047202:
    mov.b r7,@(r0,r15)
    .org 0x47204-ORIGIN
L_00047204:
    mov.b @(0x54,gbr),r0
    .org 0x47206-ORIGIN
L_00047206:
    tst #0x1,r0
    .org 0x47208-ORIGIN
L_00047208:
    bf L_0004725e
    .org 0x4720a-ORIGIN
L_0004720a:
    mov.l P_00047394,r6
    .org 0x4720c-ORIGIN
L_0004720c:
    mov #0x16,r0
    .org 0x4720e-ORIGIN
L_0004720e:
    mov.l P_00047398,r4
    .org 0x47210-ORIGIN
L_00047210:
    mov.b @(r0,r6),r5
    .org 0x47212-ORIGIN
L_00047212:
    mov.b @(0x8,r4),r0
    .org 0x47214-ORIGIN
L_00047214:
    mov.l P_00047388,r3
    .org 0x47216-ORIGIN
L_00047216:
    extu.b r5,r5
    .org 0x47218-ORIGIN
L_00047218:
    extu.b r0,r6
    .org 0x4721a-ORIGIN
L_0004721a:
    mov.b @(0x2,r3),r0
    .org 0x4721c-ORIGIN
L_0004721c:
    extu.b r0,r2
    .org 0x4721e-ORIGIN
L_0004721e:
    add r2,r6
    .org 0x47220-ORIGIN
L_00047220:
    cmp/gt r6,r5
    .org 0x47222-ORIGIN
L_00047222:
    bf L_0004725e
    .org 0x47224-ORIGIN
L_00047224:
    mov.w P_0004727e,r0
    .org 0x47226-ORIGIN
L_00047226:
    mov.l P_00047388,r3
    .org 0x47228-ORIGIN
L_00047228:
    mov.b @(r0,r12),r4
    .org 0x4722a-ORIGIN
L_0004722a:
    mov.b @(0x6,r3),r0
    .org 0x4722c-ORIGIN
L_0004722c:
    cmp/hs r0,r4
    .org 0x4722e-ORIGIN
L_0004722e:
    bf L_0004725e
    .org 0x47230-ORIGIN
L_00047230:
    mov.l P_00047388,r3
    .org 0x47232-ORIGIN
L_00047232:
    mov.l P_00047384,r1
    .org 0x47234-ORIGIN
L_00047234:
    mov.b @(0x5,r3),r0
    .org 0x47236-ORIGIN
L_00047236:
    extu.b r0,r6
    .org 0x47238-ORIGIN
L_00047238:
    mov.b @(0x9,r1),r0
    .org 0x4723a-ORIGIN
L_0004723a:
    extu.b r0,r5
    .org 0x4723c-ORIGIN
L_0004723c:
    cmp/gt r5,r6
    .org 0x4723e-ORIGIN
L_0004723e:
    bt L_0004725e
    .org 0x47240-ORIGIN
L_00047240:
    mov.l P_00047388,r3
    .org 0x47242-ORIGIN
L_00047242:
    mov.b @(0x4,r3),r0
    .org 0x47244-ORIGIN
L_00047244:
    extu.b r0,r2
    .org 0x47246-ORIGIN
L_00047246:
    cmp/gt r2,r5
    .org 0x47248-ORIGIN
L_00047248:
    bt L_0004725e
    .org 0x4724a-ORIGIN
L_0004724a:
    mov.b @(0x8,r15),r0
    .org 0x4724c-ORIGIN
L_0004724c:
    or #0x4,r0
    .org 0x4724e-ORIGIN
L_0004724e:
    mov.b r0,@(0x8,r15)
    .org 0x47250-ORIGIN
L_00047250:
    exts.b r0,r0
    .org 0x47252-ORIGIN
L_00047252:
    mov.b r0,@(0x27,gbr)
    .org 0x47254-ORIGIN
L_00047254:
    exts.b r0,r0
    .org 0x47256-ORIGIN
L_00047256:
    and #0x4,r0
    .org 0x47258-ORIGIN
L_00047258:
    mov r0,r7
    .org 0x4725a-ORIGIN
L_0004725a:
    mov #0x14,r0
    .org 0x4725c-ORIGIN
L_0004725c:
    mov.b r7,@(r0,r15)
    .org 0x4725e-ORIGIN
L_0004725e:
    mov #0x14,r0
    .org 0x47260-ORIGIN
L_00047260:
    mov.b @(r0,r15),r7
    .org 0x47262-ORIGIN
L_00047262:
    tst r7,r7
    .org 0x47264-ORIGIN
L_00047264:
    bt L_0004731e
    .org 0x47266-ORIGIN
L_00047266:
    mov.w P_00047280,r0
    .org 0x47268-ORIGIN
L_00047268:
    mov.l P_0004739c,r7
    .org 0x4726a-ORIGIN
L_0004726a:
    mov.w @(r0,r12),r5
    .org 0x4726c-ORIGIN
L_0004726c:
    mov #0x22,r0
    .org 0x4726e-ORIGIN
L_0004726e:
    mov.w @(r0,r7),r4
    .org 0x47270-ORIGIN
L_00047270:
    extu.w r5,r5
    .org 0x47272-ORIGIN
L_00047272:
    add r5,r4
    .org 0x47274-ORIGIN
L_00047274:
    cmp/pz r4
    .org 0x47276-ORIGIN
L_00047276:
    bt L_00047282
    .org 0x47278-ORIGIN
L_00047278:
    bra L_00047286
    .org 0x4727a-ORIGIN
L_0004727a:
    mov #0x0,r7
    .org 0x4727c-ORIGIN
P_0004727c:
    .byte 0x01
    .org 0x4727d-ORIGIN
P_0004727d:
    .byte 0x5e
    .org 0x4727e-ORIGIN
P_0004727e:
    .byte 0x07
    .org 0x4727f-ORIGIN
P_0004727f:
    .byte 0xee
    .org 0x47280-ORIGIN
P_00047280:
    .byte 0x04
    .org 0x47281-ORIGIN
P_00047281:
    .byte 0xbc
    .org 0x47282-ORIGIN
L_00047282:
    mov.w @(r0,r7),r7
    .org 0x47284-ORIGIN
L_00047284:
    add r5,r7
    .org 0x47286-ORIGIN
L_00047286:
    mov.w P_00047364,r0
    .org 0x47288-ORIGIN
L_00047288:
    mov #-0x1,r6
    .org 0x4728a-ORIGIN
L_0004728a:
    extu.b r6,r5
    .org 0x4728c-ORIGIN
L_0004728c:
    mov.l r7,@(0x18,r15)
    .org 0x4728e-ORIGIN
L_0004728e:
    mov.b @(r0,r12),r4
    .org 0x47290-ORIGIN
L_00047290:
    extu.b r4,r4
    .org 0x47292-ORIGIN
L_00047292:
    mov r4,r2
    .org 0x47294-ORIGIN
L_00047294:
    shll2 r2
    .org 0x47296-ORIGIN
L_00047296:
    cmp/gt r5,r2
    .org 0x47298-ORIGIN
L_00047298:
    bt L_0004729e
    .org 0x4729a-ORIGIN
L_0004729a:
    shll2 r4
    .org 0x4729c-ORIGIN
L_0004729c:
    mov r4,r5
    .org 0x4729e-ORIGIN
L_0004729e:
    mov #0x10,r0
    .org 0x472a0-ORIGIN
L_000472a0:
    mov.l P_000473a0,r4
    .org 0x472a2-ORIGIN
L_000472a2:
    mov.l P_000473a4,r2
    .org 0x472a4-ORIGIN
L_000472a4:
    mov.b r5,@(r0,r15)
    .org 0x472a6-ORIGIN
L_000472a6:
    jsr @r2
    .org 0x472a8-ORIGIN
L_000472a8:
    extu.b r5,r5
    .org 0x472aa-ORIGIN
L_000472aa:
    mov.l @(0x18,r15),r7
    .org 0x472ac-ORIGIN
L_000472ac:
    extu.b r0,r2
    .org 0x472ae-ORIGIN
L_000472ae:
    cmp/hi r7,r2
    .org 0x472b0-ORIGIN
L_000472b0:
    bt L_000472c0
    .org 0x472b2-ORIGIN
L_000472b2:
    mov #0x10,r0
    .org 0x472b4-ORIGIN
L_000472b4:
    mov.l P_000473a0,r4
    .org 0x472b6-ORIGIN
L_000472b6:
    mov.b @(r0,r15),r5
    .org 0x472b8-ORIGIN
L_000472b8:
    mov.l P_000473a4,r2
    .org 0x472ba-ORIGIN
L_000472ba:
    jsr @r2
    .org 0x472bc-ORIGIN
L_000472bc:
    extu.b r5,r5
    .org 0x472be-ORIGIN
L_000472be:
    extu.b r0,r7
    .org 0x472c0-ORIGIN
L_000472c0:
    shll2 r7
    .org 0x472c2-ORIGIN
L_000472c2:
    mov.l P_00047394,r6
    .org 0x472c4-ORIGIN
L_000472c4:
    shll2 r7
    .org 0x472c6-ORIGIN
L_000472c6:
    mov.l P_00047398,r4
    .org 0x472c8-ORIGIN
L_000472c8:
    shll2 r7
    .org 0x472ca-ORIGIN
L_000472ca:
    mov.l P_00047388,r3
    .org 0x472cc-ORIGIN
L_000472cc:
    shll r7
    .org 0x472ce-ORIGIN
L_000472ce:
    mov r7,r0
    .org 0x472d0-ORIGIN
L_000472d0:
    mov.w r0,@(0x1c,r15)
    .org 0x472d2-ORIGIN
L_000472d2:
    mov #0x16,r0
    .org 0x472d4-ORIGIN
L_000472d4:
    mov.b @(r0,r6),r2
    .org 0x472d6-ORIGIN
L_000472d6:
    mov.b @(0x8,r4),r0
    .org 0x472d8-ORIGIN
L_000472d8:
    mov.b @r3,r6
    .org 0x472da-ORIGIN
L_000472da:
    extu.b r2,r5
    .org 0x472dc-ORIGIN
L_000472dc:
    extu.b r0,r2
    .org 0x472de-ORIGIN
L_000472de:
    extu.b r6,r6
    .org 0x472e0-ORIGIN
L_000472e0:
    add r6,r2
    .org 0x472e2-ORIGIN
L_000472e2:
    cmp/gt r2,r5
    .org 0x472e4-ORIGIN
L_000472e4:
    bf L_00047316
    .org 0x472e6-ORIGIN
L_000472e6:
    mov.b @(0x19,gbr),r0
    .org 0x472e8-ORIGIN
L_000472e8:
    tst #0x40,r0
    .org 0x472ea-ORIGIN
L_000472ea:
    bf L_00047316
    .org 0x472ec-ORIGIN
L_000472ec:
    mov.w P_00047364,r0
    .org 0x472ee-ORIGIN
L_000472ee:
    mov.l P_00047388,r3
    .org 0x472f0-ORIGIN
L_000472f0:
    mov.b @(r0,r12),r2
    .org 0x472f2-ORIGIN
L_000472f2:
    mov.b @(0x1,r3),r0
    .org 0x472f4-ORIGIN
L_000472f4:
    cmp/hs r0,r2
    .org 0x472f6-ORIGIN
L_000472f6:
    bf L_00047316
    .org 0x472f8-ORIGIN
L_000472f8:
    mov.w @(0x1c,r15),r0
    .org 0x472fa-ORIGIN
L_000472fa:
    mov.l P_000473a8,r5
    .org 0x472fc-ORIGIN
L_000472fc:
    extu.w r0,r4
    .org 0x472fe-ORIGIN
L_000472fe:
    mov.b @(0x1,r5),r0
    .org 0x47300-ORIGIN
L_00047300:
    extu.b r0,r7
    .org 0x47302-ORIGIN
L_00047302:
    mov.w P_00047366,r0
    .org 0x47304-ORIGIN
L_00047304:
    mov.w @(r0,r12),r6
    .org 0x47306-ORIGIN
L_00047306:
    extu.w r6,r5
    .org 0x47308-ORIGIN
L_00047308:
    add r5,r7
    .org 0x4730a-ORIGIN
L_0004730a:
    cmp/hi r4,r7
    .org 0x4730c-ORIGIN
L_0004730c:
    bf/s L_00047312
    .org 0x4730e-ORIGIN
L_0004730e:
    mov r7,r6
    .org 0x47310-ORIGIN
L_00047310:
    mov r4,r6
    .org 0x47312-ORIGIN
L_00047312:
    bra L_0004731e
    .org 0x47314-ORIGIN
L_00047314:
    mov r6,r13
    .org 0x47316-ORIGIN
L_00047316:
    mov #0x27,r0
    .org 0x47318-ORIGIN
L_00047318:
    and.b #0xfb,@(r0,gbr)
    .org 0x4731a-ORIGIN
L_0004731a:
    mov #0x54,r0
    .org 0x4731c-ORIGIN
L_0004731c:
    or.b #0x1,@(r0,gbr)
    .org 0x4731e-ORIGIN
L_0004731e:
    mov.b @(0x54,gbr),r0
    .org 0x47320-ORIGIN
L_00047320:
    tst #0x1,r0
    .org 0x47322-ORIGIN
L_00047322:
    bt/s L_00047354
    .org 0x47324-ORIGIN
L_00047324:
    mov r0,r4
    .org 0x47326-ORIGIN
L_00047326:
    mov.w P_00047366,r0
    .org 0x47328-ORIGIN
L_00047328:
    mov.l P_000473a8,r3
    .org 0x4732a-ORIGIN
L_0004732a:
    mov.w @(r0,r12),r7
    .org 0x4732c-ORIGIN
L_0004732c:
    mov.b @r3,r5
    .org 0x4732e-ORIGIN
L_0004732e:
    extu.w r7,r6
    .org 0x47330-ORIGIN
L_00047330:
    extu.b r5,r5
    .org 0x47332-ORIGIN
L_00047332:
    cmp/ge r5,r6
    .org 0x47334-ORIGIN
L_00047334:
    bt L_0004733a
    .org 0x47336-ORIGIN
L_00047336:
    bra L_0004733c
    .org 0x47338-ORIGIN
L_00047338:
    mov #0x0,r6
    .org 0x4733a-ORIGIN
L_0004733a:
    sub r5,r6
    .org 0x4733c-ORIGIN
L_0004733c:
    extu.w r6,r13
    .org 0x4733e-ORIGIN
L_0004733e:
    tst r13,r13
    .org 0x47340-ORIGIN
L_00047340:
    bf L_00047354
    .org 0x47342-ORIGIN
L_00047342:
    mov r4,r0
    .org 0x47344-ORIGIN
L_00047344:
    and #0xfe,r0
    .org 0x47346-ORIGIN
L_00047346:
    bra L_00047354
    .org 0x47348-ORIGIN
L_00047348:
    mov.b r0,@(0x54,gbr)
    .org 0x4734a-ORIGIN
L_0004734a:
    mov #0x27,r0
    .org 0x4734c-ORIGIN
L_0004734c:
    and.b #0xfb,@(r0,gbr)
    .org 0x4734e-ORIGIN
L_0004734e:
    mov #0x54,r0
    .org 0x47350-ORIGIN
L_00047350:
    and.b #0xfe,@(r0,gbr)
    .org 0x47352-ORIGIN
L_00047352:
    mov #0x0,r13
    .org 0x47354-ORIGIN
L_00047354:
    mov.w P_00047366,r0
    .org 0x47356-ORIGIN
L_00047356:
    mov.w r13,@(r0,r12)
    .org 0x47358-ORIGIN
L_00047358:
    add #0x20,r15
    .org 0x4735a-ORIGIN
L_0004735a:
    ldc.l @r15+,gbr
    .org 0x4735c-ORIGIN
L_0004735c:
    lds.l @r15+,pr
    .org 0x4735e-ORIGIN
L_0004735e:
    mov.l @r15+,r13
    .org 0x47360-ORIGIN
L_00047360:
    rts
    .org 0x47362-ORIGIN
L_00047362:
    mov.l @r15+,r12
    .org 0x47364-ORIGIN
P_00047364:
    .byte 0x07
    .org 0x47365-ORIGIN
P_00047365:
    .byte 0xee
    .org 0x47366-ORIGIN
P_00047366:
    .byte 0x01
    .org 0x47367-ORIGIN
P_00047367:
    .byte 0x5e
    .org 0x47368-ORIGIN
P_00047368:
    .byte 0xff
    .org 0x47369-ORIGIN
P_00047369:
    .byte 0xff
    .org 0x4736a-ORIGIN
P_0004736a:
    .byte 0x24
    .org 0x4736b-ORIGIN
P_0004736b:
    .byte 0x4c
    .org 0x4736c-ORIGIN
P_0004736c:
    .byte 0xff
    .org 0x4736d-ORIGIN
P_0004736d:
    .byte 0xff
    .org 0x4736e-ORIGIN
P_0004736e:
    .byte 0x12
    .org 0x4736f-ORIGIN
P_0004736f:
    .byte 0x8c
    .org 0x47370-ORIGIN
P_00047370:
    .byte 0xff
    .org 0x47371-ORIGIN
P_00047371:
    .byte 0xff
    .org 0x47372-ORIGIN
P_00047372:
    .byte 0x10
    .org 0x47373-ORIGIN
P_00047373:
    .byte 0x94
    .org 0x47374-ORIGIN
P_00047374:
    .byte 0x00
    .org 0x47375-ORIGIN
P_00047375:
    .byte 0x00
    .org 0x47376-ORIGIN
P_00047376:
    .byte 0x86
    .org 0x47377-ORIGIN
P_00047377:
    .byte 0xfd
    .org 0x47378-ORIGIN
P_00047378:
    .byte 0xff
    .org 0x47379-ORIGIN
P_00047379:
    .byte 0xff
    .org 0x4737a-ORIGIN
P_0004737a:
    .byte 0x41
    .org 0x4737b-ORIGIN
P_0004737b:
    .byte 0x94
    .org 0x4737c-ORIGIN
P_0004737c:
    .byte 0x00
    .org 0x4737d-ORIGIN
P_0004737d:
    .byte 0x02
    .org 0x4737e-ORIGIN
P_0004737e:
    .byte 0x5e
    .org 0x4737f-ORIGIN
P_0004737f:
    .byte 0x4e
    .org 0x47380-ORIGIN
P_00047380:
    .byte 0x00
    .org 0x47381-ORIGIN
P_00047381:
    .byte 0x02
    .org 0x47382-ORIGIN
P_00047382:
    .byte 0x5e
    .org 0x47383-ORIGIN
P_00047383:
    .byte 0x20
    .org 0x47384-ORIGIN
P_00047384:
    .byte 0xff
    .org 0x47385-ORIGIN
P_00047385:
    .byte 0xff
    .org 0x47386-ORIGIN
P_00047386:
    .byte 0x10
    .org 0x47387-ORIGIN
P_00047387:
    .byte 0x68
    .org 0x47388-ORIGIN
P_00047388:
    .byte 0x00
    .org 0x47389-ORIGIN
P_00047389:
    .byte 0x00
    .org 0x4738a-ORIGIN
P_0004738a:
    .byte 0x87
    .org 0x4738b-ORIGIN
P_0004738b:
    .byte 0x60
    .org 0x4738c-ORIGIN
P_0004738c:
    .byte 0x00
    .org 0x4738d-ORIGIN
P_0004738d:
    .byte 0x00
    .org 0x4738e-ORIGIN
P_0004738e:
    .byte 0x87
    .org 0x4738f-ORIGIN
P_0004738f:
    .byte 0x0c
    .org 0x47390-ORIGIN
P_00047390:
    .byte 0x00
    .org 0x47391-ORIGIN
P_00047391:
    .byte 0x00
    .org 0x47392-ORIGIN
P_00047392:
    .byte 0x82
    .org 0x47393-ORIGIN
P_00047393:
    .byte 0x52
    .org 0x47394-ORIGIN
P_00047394:
    .byte 0xff
    .org 0x47395-ORIGIN
P_00047395:
    .byte 0xff
    .org 0x47396-ORIGIN
P_00047396:
    .byte 0x11
    .org 0x47397-ORIGIN
P_00047397:
    .byte 0x9c
    .org 0x47398-ORIGIN
P_00047398:
    .byte 0xff
    .org 0x47399-ORIGIN
P_00047399:
    .byte 0xff
    .org 0x4739a-ORIGIN
P_0004739a:
    .byte 0x22
    .org 0x4739b-ORIGIN
P_0004739b:
    .byte 0xdc
    .org 0x4739c-ORIGIN
P_0004739c:
    .byte 0xff
    .org 0x4739d-ORIGIN
P_0004739d:
    .byte 0xff
    .org 0x4739e-ORIGIN
P_0004739e:
    .byte 0x12
    .org 0x4739f-ORIGIN
P_0004739f:
    .byte 0x0e
    .org 0x473a0-ORIGIN
P_000473a0:
    .byte 0x00
    .org 0x473a1-ORIGIN
P_000473a1:
    .byte 0x01
    .org 0x473a2-ORIGIN
P_000473a2:
    .byte 0x1f
    .org 0x473a3-ORIGIN
P_000473a3:
    .byte 0xf6
    .org 0x473a4-ORIGIN
P_000473a4:
    .byte 0x00
    .org 0x473a5-ORIGIN
P_000473a5:
    .byte 0x02
    .org 0x473a6-ORIGIN
P_000473a6:
    .byte 0x63
    .org 0x473a7-ORIGIN
P_000473a7:
    .byte 0x88
    .org 0x473a8-ORIGIN
P_000473a8:
    .byte 0x00
    .org 0x473a9-ORIGIN
P_000473a9:
    .byte 0x00
    .org 0x473aa-ORIGIN
P_000473aa:
    .byte 0x84
    .org 0x473ab-ORIGIN
P_000473ab:
    .byte 0xd8
