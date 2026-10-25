! Complete stock transmission completion and signed request-boundary entries.
    .text
    .balign 4
    .set ORIGIN,0x777f8
    .org 0x777fa-ORIGIN
L_000777fa:
    mov.l r13,@-r15
    .org 0x777fc-ORIGIN
L_000777fc:
    mov.l r14,@-r15
    .org 0x777fe-ORIGIN
L_000777fe:
    mov.l P_00077910,r1
    .org 0x77800-ORIGIN
L_00077800:
    mov.w P_0007787c,r0
    .org 0x77802-ORIGIN
L_00077802:
    mov.l P_00077914,r2
    .org 0x77804-ORIGIN
L_00077804:
    mov.w @(r0,r1),r13
    .org 0x77806-ORIGIN
L_00077806:
    mov.w P_0007787e,r0
    .org 0x77808-ORIGIN
L_00077808:
    mov.w @(r0,r1),r7
    .org 0x7780a-ORIGIN
L_0007780a:
    mov.w P_00077880,r0
    .org 0x7780c-ORIGIN
L_0007780c:
    mov.w @(r0,r1),r5
    .org 0x7780e-ORIGIN
L_0007780e:
    mov.w P_00077882,r0
    .org 0x77810-ORIGIN
L_00077810:
    mov.w @(r0,r1),r14
    .org 0x77812-ORIGIN
L_00077812:
    mov.b @r2,r0
    .org 0x77814-ORIGIN
L_00077814:
    tst #0x1,r0
    .org 0x77816-ORIGIN
L_00077816:
    bf L_00077864
    .org 0x77818-ORIGIN
L_00077818:
    mov.l P_00077918,r2
    .org 0x7781a-ORIGIN
L_0007781a:
    mov.l P_0007791c,r4
    .org 0x7781c-ORIGIN
L_0007781c:
    mov.b @r2,r0
    .org 0x7781e-ORIGIN
L_0007781e:
    and #0x1,r0
    .org 0x77820-ORIGIN
L_00077820:
    mov r0,r6
    .org 0x77822-ORIGIN
L_00077822:
    mov.b @(0x1,r4),r0
    .org 0x77824-ORIGIN
L_00077824:
    tst #0x8,r0
    .org 0x77826-ORIGIN
L_00077826:
    bt L_00077850
    .org 0x77828-ORIGIN
L_00077828:
    tst r6,r6
    .org 0x7782a-ORIGIN
L_0007782a:
    bt L_00077834
    .org 0x7782c-ORIGIN
L_0007782c:
    mov.l P_00077920,r5
    .org 0x7782e-ORIGIN
L_0007782e:
    mov #0x3e,r0
    .org 0x77830-ORIGIN
L_00077830:
    bra L_00077838
    .org 0x77832-ORIGIN
L_00077832:
    mov.w @(r0,r5),r13
    .org 0x77834-ORIGIN
L_00077834:
    mov.w P_00077884,r0
    .org 0x77836-ORIGIN
L_00077836:
    mov.w @(r0,r1),r13
    .org 0x77838-ORIGIN
L_00077838:
    mov.w P_00077886,r0
    .org 0x7783a-ORIGIN
L_0007783a:
    mov.l P_00077920,r5
    .org 0x7783c-ORIGIN
L_0007783c:
    mov.w @(r0,r1),r7
    .org 0x7783e-ORIGIN
L_0007783e:
    mov #0x3e,r0
    .org 0x77840-ORIGIN
L_00077840:
    mov.w @(r0,r5),r6
    .org 0x77842-ORIGIN
L_00077842:
    cmp/gt r7,r6
    .org 0x77844-ORIGIN
L_00077844:
    bt L_00077848
    .org 0x77846-ORIGIN
L_00077846:
    mov r6,r7
    .org 0x77848-ORIGIN
L_00077848:
    mov.w P_00077888,r0
    .org 0x7784a-ORIGIN
L_0007784a:
    mov.w @(r0,r1),r5
    .org 0x7784c-ORIGIN
L_0007784c:
    bra L_00077864
    .org 0x7784e-ORIGIN
L_0007784e:
    mov r5,r14
    .org 0x77850-ORIGIN
L_00077850:
    tst r6,r6
    .org 0x77852-ORIGIN
L_00077852:
    bf L_00077858
    .org 0x77854-ORIGIN
L_00077854:
    mov.w P_00077884,r0
    .org 0x77856-ORIGIN
L_00077856:
    mov.w @(r0,r1),r13
    .org 0x77858-ORIGIN
L_00077858:
    mov.w P_00077886,r0
    .org 0x7785a-ORIGIN
L_0007785a:
    mov.w @(r0,r1),r2
    .org 0x7785c-ORIGIN
L_0007785c:
    cmp/gt r2,r7
    .org 0x7785e-ORIGIN
L_0007785e:
    bt L_00077862
    .org 0x77860-ORIGIN
L_00077860:
    mov r7,r2
    .org 0x77862-ORIGIN
L_00077862:
    mov r2,r7
    .org 0x77864-ORIGIN
L_00077864:
    mov.w P_0007788a,r0
    .org 0x77866-ORIGIN
L_00077866:
    mov.w r13,@(r0,r1)
    .org 0x77868-ORIGIN
L_00077868:
    mov.w P_0007788c,r0
    .org 0x7786a-ORIGIN
L_0007786a:
    mov.w r7,@(r0,r1)
    .org 0x7786c-ORIGIN
L_0007786c:
    mov.w P_0007788e,r0
    .org 0x7786e-ORIGIN
L_0007786e:
    mov.w r5,@(r0,r1)
    .org 0x77870-ORIGIN
L_00077870:
    mov.w P_00077890,r0
    .org 0x77872-ORIGIN
L_00077872:
    mov.w r14,@(r0,r1)
    .org 0x77874-ORIGIN
L_00077874:
    mov.l @r15+,r14
    .org 0x77876-ORIGIN
L_00077876:
    rts
    .org 0x77878-ORIGIN
L_00077878:
    mov.l @r15+,r13
    .org 0x7787c-ORIGIN
P_0007787c:
    .byte 0x0b
    .org 0x7787d-ORIGIN
P_0007787d:
    .byte 0x90
    .org 0x7787e-ORIGIN
P_0007787e:
    .byte 0x0b
    .org 0x7787f-ORIGIN
P_0007787f:
    .byte 0x94
    .org 0x77880-ORIGIN
P_00077880:
    .byte 0x0b
    .org 0x77881-ORIGIN
P_00077881:
    .byte 0x8e
    .org 0x77882-ORIGIN
P_00077882:
    .byte 0x0b
    .org 0x77883-ORIGIN
P_00077883:
    .byte 0x92
    .org 0x77884-ORIGIN
P_00077884:
    .byte 0x0b
    .org 0x77885-ORIGIN
P_00077885:
    .byte 0xa8
    .org 0x77886-ORIGIN
P_00077886:
    .byte 0x0b
    .org 0x77887-ORIGIN
P_00077887:
    .byte 0xd0
    .org 0x77888-ORIGIN
P_00077888:
    .byte 0x0b
    .org 0x77889-ORIGIN
P_00077889:
    .byte 0xa4
    .org 0x7788a-ORIGIN
P_0007788a:
    .byte 0x0b
    .org 0x7788b-ORIGIN
P_0007788b:
    .byte 0x88
    .org 0x7788c-ORIGIN
P_0007788c:
    .byte 0x0b
    .org 0x7788d-ORIGIN
P_0007788d:
    .byte 0x8c
    .org 0x7788e-ORIGIN
P_0007788e:
    .byte 0x0b
    .org 0x7788f-ORIGIN
P_0007788f:
    .byte 0x86
    .org 0x77890-ORIGIN
P_00077890:
    .byte 0x0b
    .org 0x77891-ORIGIN
P_00077891:
    .byte 0x8a
    .org 0x77910-ORIGIN
P_00077910:
    .byte 0xff
    .org 0x77911-ORIGIN
P_00077911:
    .byte 0xff
    .org 0x77912-ORIGIN
P_00077912:
    .byte 0x28
    .org 0x77913-ORIGIN
P_00077913:
    .byte 0xf8
    .org 0x77914-ORIGIN
P_00077914:
    .byte 0x00
    .org 0x77915-ORIGIN
P_00077915:
    .byte 0x00
    .org 0x77916-ORIGIN
P_00077916:
    .byte 0x83
    .org 0x77917-ORIGIN
P_00077917:
    .byte 0xc1
    .org 0x77918-ORIGIN
P_00077918:
    .byte 0x00
    .org 0x77919-ORIGIN
P_00077919:
    .byte 0x00
    .org 0x7791a-ORIGIN
P_0007791a:
    .byte 0x89
    .org 0x7791b-ORIGIN
P_0007791b:
    .byte 0xc5
    .org 0x7791c-ORIGIN
P_0007791c:
    .byte 0xff
    .org 0x7791d-ORIGIN
P_0007791d:
    .byte 0xff
    .org 0x7791e-ORIGIN
P_0007791e:
    .byte 0x41
    .org 0x7791f-ORIGIN
P_0007791f:
    .byte 0xa5
    .org 0x77920-ORIGIN
P_00077920:
    .byte 0xff
    .org 0x77921-ORIGIN
P_00077921:
    .byte 0xff
    .org 0x77922-ORIGIN
P_00077922:
    .byte 0x41
    .org 0x77923-ORIGIN
P_00077923:
    .byte 0x24
    .org 0x79030-ORIGIN
L_00079030:
    mov.l r8,@-r15
    .org 0x79032-ORIGIN
L_00079032:
    mov.l r9,@-r15
    .org 0x79034-ORIGIN
L_00079034:
    mov.l r10,@-r15
    .org 0x79036-ORIGIN
L_00079036:
    mov.l r11,@-r15
    .org 0x79038-ORIGIN
L_00079038:
    mov.l r12,@-r15
    .org 0x7903a-ORIGIN
L_0007903a:
    mov.l r13,@-r15
    .org 0x7903c-ORIGIN
L_0007903c:
    mov.l r14,@-r15
    .org 0x7903e-ORIGIN
L_0007903e:
    mov.l P_00079218,r5
    .org 0x79040-ORIGIN
L_00079040:
    mov #0x12,r0
    .org 0x79042-ORIGIN
L_00079042:
    mov.l P_0007921c,r8
    .org 0x79044-ORIGIN
L_00079044:
    mov.b @(r0,r5),r6
    .org 0x79046-ORIGIN
L_00079046:
    mov.b @(0x7,r8),r0
    .org 0x79048-ORIGIN
L_00079048:
    mov.l P_00079220,r9
    .org 0x7904a-ORIGIN
L_0007904a:
    mov r0,r10
    .org 0x7904c-ORIGIN
L_0007904c:
    mov #0x7c,r0
    .org 0x7904e-ORIGIN
L_0007904e:
    mov.w @(r0,r9),r4
    .org 0x79050-ORIGIN
L_00079050:
    mov.l P_00079224,r7
    .org 0x79052-ORIGIN
L_00079052:
    mov.w P_000790fe,r0
    .org 0x79054-ORIGIN
L_00079054:
    mov.w @(r0,r7),r2
    .org 0x79056-ORIGIN
L_00079056:
    cmp/ge r4,r2
    .org 0x79058-ORIGIN
L_00079058:
    bt/s L_00079066
    .org 0x7905a-ORIGIN
L_0007905a:
    mov r6,r0
    .org 0x7905c-ORIGIN
L_0007905c:
    or #0x8,r0
    .org 0x7905e-ORIGIN
L_0007905e:
    mov r0,r6
    .org 0x79060-ORIGIN
L_00079060:
    mov #0x12,r0
    .org 0x79062-ORIGIN
L_00079062:
    bra L_00079070
    .org 0x79064-ORIGIN
L_00079064:
    mov.b r6,@(r0,r5)
    .org 0x79066-ORIGIN
L_00079066:
    and #0xf7,r0
    .org 0x79068-ORIGIN
L_00079068:
    mov.w P_00079100,r2
    .org 0x7906a-ORIGIN
L_0007906a:
    mov r0,r6
    .org 0x7906c-ORIGIN
L_0007906c:
    mov #0x12,r0
    .org 0x7906e-ORIGIN
L_0007906e:
    mov.b r6,@(r0,r5)
    .org 0x79070-ORIGIN
L_00079070:
    mov.l P_00079228,r5
    .org 0x79072-ORIGIN
L_00079072:
    mov.w P_00079102,r0
    .org 0x79074-ORIGIN
L_00079074:
    mov.w @(r0,r5),r6
    .org 0x79076-ORIGIN
L_00079076:
    cmp/pl r6
    .org 0x79078-ORIGIN
L_00079078:
    bf L_0007907c
    .org 0x7907a-ORIGIN
L_0007907a:
    mov #0x0,r6
    .org 0x7907c-ORIGIN
L_0007907c:
    exts.w r6,r5
    .org 0x7907e-ORIGIN
L_0007907e:
    mov.l P_0007922c,r6
    .org 0x79080-ORIGIN
L_00079080:
    mov.b @r6,r11
    .org 0x79082-ORIGIN
L_00079082:
    mov r11,r0
    .org 0x79084-ORIGIN
L_00079084:
    and #0x1,r0
    .org 0x79086-ORIGIN
L_00079086:
    tst r0,r0
    .org 0x79088-ORIGIN
L_00079088:
    bt/s L_0007909a
    .org 0x7908a-ORIGIN
L_0007908a:
    mov r0,r7
    .org 0x7908c-ORIGIN
L_0007908c:
    exts.w r2,r2
    .org 0x7908e-ORIGIN
L_0007908e:
    cmp/ge r5,r2
    .org 0x79090-ORIGIN
L_00079090:
    bt L_00079096
    .org 0x79092-ORIGIN
L_00079092:
    bra L_00079098
    .org 0x79094-ORIGIN
L_00079094:
    mov r5,r6
    .org 0x79096-ORIGIN
L_00079096:
    exts.w r2,r6
    .org 0x79098-ORIGIN
L_00079098:
    mov r6,r2
    .org 0x7909a-ORIGIN
L_0007909a:
    mov.l P_00079228,r3
    .org 0x7909c-ORIGIN
L_0007909c:
    mov r2,r12
    .org 0x7909e-ORIGIN
L_0007909e:
    mov.w P_00079104,r0
    .org 0x790a0-ORIGIN
L_000790a0:
    exts.w r2,r2
    .org 0x790a2-ORIGIN
L_000790a2:
    mov.w @(r0,r3),r6
    .org 0x790a4-ORIGIN
L_000790a4:
    cmp/gt r6,r2
    .org 0x790a6-ORIGIN
L_000790a6:
    bf L_000790ac
    .org 0x790a8-ORIGIN
L_000790a8:
    bra L_000790ae
    .org 0x790aa-ORIGIN
L_000790aa:
    mov r6,r2
    .org 0x790ac-ORIGIN
L_000790ac:
    exts.w r2,r2
    .org 0x790ae-ORIGIN
L_000790ae:
    tst r7,r7
    .org 0x790b0-ORIGIN
L_000790b0:
    exts.w r2,r14
    .org 0x790b2-ORIGIN
L_000790b2:
    bt/s L_000790be
    .org 0x790b4-ORIGIN
L_000790b4:
    mov r4,r2
    .org 0x790b6-ORIGIN
L_000790b6:
    cmp/ge r5,r2
    .org 0x790b8-ORIGIN
L_000790b8:
    bf L_000790bc
    .org 0x790ba-ORIGIN
L_000790ba:
    mov r2,r5
    .org 0x790bc-ORIGIN
L_000790bc:
    mov r5,r2
    .org 0x790be-ORIGIN
L_000790be:
    mov.l P_00079228,r3
    .org 0x790c0-ORIGIN
L_000790c0:
    exts.w r2,r2
    .org 0x790c2-ORIGIN
L_000790c2:
    mov.w P_00079106,r0
    .org 0x790c4-ORIGIN
L_000790c4:
    mov.w @(r0,r3),r7
    .org 0x790c6-ORIGIN
L_000790c6:
    cmp/gt r7,r2
    .org 0x790c8-ORIGIN
L_000790c8:
    bf L_000790ce
    .org 0x790ca-ORIGIN
L_000790ca:
    bra L_000790d0
    .org 0x790cc-ORIGIN
L_000790cc:
    mov r7,r6
    .org 0x790ce-ORIGIN
L_000790ce:
    exts.w r2,r6
    .org 0x790d0-ORIGIN
L_000790d0:
    mov.l P_00079228,r3
    .org 0x790d2-ORIGIN
L_000790d2:
    exts.w r6,r6
    .org 0x790d4-ORIGIN
L_000790d4:
    mov.w P_00079108,r0
    .org 0x790d6-ORIGIN
L_000790d6:
    mov.w @(r0,r3),r2
    .org 0x790d8-ORIGIN
L_000790d8:
    cmp/gt r2,r6
    .org 0x790da-ORIGIN
L_000790da:
    bf L_000790de
    .org 0x790dc-ORIGIN
L_000790dc:
    mov r2,r6
    .org 0x790de-ORIGIN
L_000790de:
    exts.w r6,r13
    .org 0x790e0-ORIGIN
L_000790e0:
    cmp/gt r13,r14
    .org 0x790e2-ORIGIN
L_000790e2:
    bf/s L_000790e8
    .org 0x790e4-ORIGIN
L_000790e4:
    mov r14,r6
    .org 0x790e6-ORIGIN
L_000790e6:
    mov r13,r6
    .org 0x790e8-ORIGIN
L_000790e8:
    mov.l P_00079228,r3
    .org 0x790ea-ORIGIN
L_000790ea:
    exts.w r6,r6
    .org 0x790ec-ORIGIN
L_000790ec:
    mov.w P_0007910a,r0
    .org 0x790ee-ORIGIN
L_000790ee:
    mov.w r6,@(r0,r3)
    .org 0x790f0-ORIGIN
L_000790f0:
    mov r11,r0
    .org 0x790f2-ORIGIN
L_000790f2:
    tst #0x2,r0
    .org 0x790f4-ORIGIN
L_000790f4:
    bt/s L_0007910c
    .org 0x790f6-ORIGIN
L_000790f6:
    mov #0x78,r0
    .org 0x790f8-ORIGIN
L_000790f8:
    mov.w r12,@(r0,r9)
    .org 0x790fa-ORIGIN
L_000790fa:
    bra L_0007910e
    .org 0x790fc-ORIGIN
L_000790fc:
    mov r12,r14
    .org 0x790fe-ORIGIN
P_000790fe:
    .byte 0x07
    .org 0x790ff-ORIGIN
P_000790ff:
    .byte 0x36
    .org 0x79100-ORIGIN
P_00079100:
    .byte 0x7f
    .org 0x79101-ORIGIN
P_00079101:
    .byte 0xff
    .org 0x79102-ORIGIN
P_00079102:
    .byte 0x0b
    .org 0x79103-ORIGIN
P_00079103:
    .byte 0xd2
    .org 0x79104-ORIGIN
P_00079104:
    .byte 0x0b
    .org 0x79105-ORIGIN
P_00079105:
    .byte 0xc0
    .org 0x79106-ORIGIN
P_00079106:
    .byte 0x0b
    .org 0x79107-ORIGIN
P_00079107:
    .byte 0xc2
    .org 0x79108-ORIGIN
P_00079108:
    .byte 0x0b
    .org 0x79109-ORIGIN
P_00079109:
    .byte 0xbc
    .org 0x7910a-ORIGIN
P_0007910a:
    .byte 0x0b
    .org 0x7910b-ORIGIN
P_0007910b:
    .byte 0xac
    .org 0x7910c-ORIGIN
L_0007910c:
    mov.w r14,@(r0,r9)
    .org 0x7910e-ORIGIN
L_0007910e:
    mov.l P_00079228,r3
    .org 0x79110-ORIGIN
L_00079110:
    exts.w r14,r14
    .org 0x79112-ORIGIN
L_00079112:
    mov.w P_0007920a,r0
    .org 0x79114-ORIGIN
L_00079114:
    mov.w @(r0,r3),r5
    .org 0x79116-ORIGIN
L_00079116:
    cmp/ge r5,r14
    .org 0x79118-ORIGIN
L_00079118:
    bf L_0007911c
    .org 0x7911a-ORIGIN
L_0007911a:
    exts.w r14,r5
    .org 0x7911c-ORIGIN
L_0007911c:
    mov.l P_00079228,r3
    .org 0x7911e-ORIGIN
L_0007911e:
    exts.w r5,r5
    .org 0x79120-ORIGIN
L_00079120:
    mov.w P_0007920c,r0
    .org 0x79122-ORIGIN
L_00079122:
    mov.w @(r0,r3),r2
    .org 0x79124-ORIGIN
L_00079124:
    cmp/gt r2,r5
    .org 0x79126-ORIGIN
L_00079126:
    bf L_0007912a
    .org 0x79128-ORIGIN
L_00079128:
    mov r2,r5
    .org 0x7912a-ORIGIN
L_0007912a:
    mov.l P_00079230,r2
    .org 0x7912c-ORIGIN
L_0007912c:
    mov.b @r2,r9
    .org 0x7912e-ORIGIN
L_0007912e:
    mov r9,r0
    .org 0x79130-ORIGIN
L_00079130:
    tst #0x20,r0
    .org 0x79132-ORIGIN
L_00079132:
    bf/s L_00079144
    .org 0x79134-ORIGIN
L_00079134:
    exts.w r5,r5
    .org 0x79136-ORIGIN
L_00079136:
    mov.l P_00079234,r3
    .org 0x79138-ORIGIN
L_00079138:
    mov.w @(0x16,r3),r0
    .org 0x7913a-ORIGIN
L_0007913a:
    cmp/ge r0,r5
    .org 0x7913c-ORIGIN
L_0007913c:
    bf/s L_00079142
    .org 0x7913e-ORIGIN
L_0007913e:
    mov r0,r2
    .org 0x79140-ORIGIN
L_00079140:
    mov r5,r2
    .org 0x79142-ORIGIN
L_00079142:
    mov r2,r5
    .org 0x79144-ORIGIN
L_00079144:
    mov.l P_00079224,r3
    .org 0x79146-ORIGIN
L_00079146:
    mov.w P_0007920e,r0
    .org 0x79148-ORIGIN
L_00079148:
    mov.l P_00079228,r1
    .org 0x7914a-ORIGIN
L_0007914a:
    mov.w r5,@(r0,r3)
    .org 0x7914c-ORIGIN
L_0007914c:
    mov.w P_00079210,r0
    .org 0x7914e-ORIGIN
L_0007914e:
    mov.w @(r0,r1),r5
    .org 0x79150-ORIGIN
L_00079150:
    cmp/ge r5,r13
    .org 0x79152-ORIGIN
L_00079152:
    bf L_00079156
    .org 0x79154-ORIGIN
L_00079154:
    mov r13,r5
    .org 0x79156-ORIGIN
L_00079156:
    mov.l P_00079228,r3
    .org 0x79158-ORIGIN
L_00079158:
    exts.w r5,r5
    .org 0x7915a-ORIGIN
L_0007915a:
    mov.w P_00079212,r0
    .org 0x7915c-ORIGIN
L_0007915c:
    mov.w @(r0,r3),r2
    .org 0x7915e-ORIGIN
L_0007915e:
    cmp/gt r2,r5
    .org 0x79160-ORIGIN
L_00079160:
    bf L_00079164
    .org 0x79162-ORIGIN
L_00079162:
    mov r2,r5
    .org 0x79164-ORIGIN
L_00079164:
    mov.l P_00079234,r2
    .org 0x79166-ORIGIN
L_00079166:
    exts.w r5,r12
    .org 0x79168-ORIGIN
L_00079168:
    mov r12,r5
    .org 0x7916a-ORIGIN
L_0007916a:
    mov.w @(0x16,r2),r0
    .org 0x7916c-ORIGIN
L_0007916c:
    cmp/ge r0,r12
    .org 0x7916e-ORIGIN
L_0007916e:
    bt/s L_00079174
    .org 0x79170-ORIGIN
L_00079170:
    mov r0,r11
    .org 0x79172-ORIGIN
L_00079172:
    mov r11,r5
    .org 0x79174-ORIGIN
L_00079174:
    mov.l P_00079234,r3
    .org 0x79176-ORIGIN
L_00079176:
    exts.w r5,r14
    .org 0x79178-ORIGIN
L_00079178:
    mov.w @(0x14,r3),r0
    .org 0x7917a-ORIGIN
L_0007917a:
    cmp/gt r0,r14
    .org 0x7917c-ORIGIN
L_0007917c:
    bf/s L_00079182
    .org 0x7917e-ORIGIN
L_0007917e:
    mov r0,r5
    .org 0x79180-ORIGIN
L_00079180:
    mov r5,r14
    .org 0x79182-ORIGIN
L_00079182:
    mov.l P_00079228,r3
    .org 0x79184-ORIGIN
L_00079184:
    exts.w r14,r13
    .org 0x79186-ORIGIN
L_00079186:
    mov.w P_00079214,r0
    .org 0x79188-ORIGIN
L_00079188:
    mov.w @(r0,r3),r14
    .org 0x7918a-ORIGIN
L_0007918a:
    cmp/gt r14,r13
    .org 0x7918c-ORIGIN
L_0007918c:
    bt L_00079190
    .org 0x7918e-ORIGIN
L_0007918e:
    mov r13,r14
    .org 0x79190-ORIGIN
L_00079190:
    exts.w r14,r2
    .org 0x79192-ORIGIN
L_00079192:
    exts.w r7,r7
    .org 0x79194-ORIGIN
L_00079194:
    cmp/gt r7,r2
    .org 0x79196-ORIGIN
L_00079196:
    bf L_0007919c
    .org 0x79198-ORIGIN
L_00079198:
    bra L_0007919e
    .org 0x7919a-ORIGIN
L_0007919a:
    exts.w r7,r7
    .org 0x7919c-ORIGIN
L_0007919c:
    mov r2,r7
    .org 0x7919e-ORIGIN
L_0007919e:
    mov r9,r0
    .org 0x791a0-ORIGIN
L_000791a0:
    tst #0x1,r0
    .org 0x791a2-ORIGIN
L_000791a2:
    bt L_000791ae
    .org 0x791a4-ORIGIN
L_000791a4:
    mov.l P_00079224,r3
    .org 0x791a6-ORIGIN
L_000791a6:
    mov.w P_00079216,r0
    .org 0x791a8-ORIGIN
L_000791a8:
    mov.w r13,@(r0,r3)
    .org 0x791aa-ORIGIN
L_000791aa:
    bra L_000791b4
    .org 0x791ac-ORIGIN
L_000791ac:
    nop
    .org 0x791ae-ORIGIN
L_000791ae:
    mov.l P_00079224,r3
    .org 0x791b0-ORIGIN
L_000791b0:
    mov.w P_00079216,r0
    .org 0x791b2-ORIGIN
L_000791b2:
    mov.w r7,@(r0,r3)
    .org 0x791b4-ORIGIN
L_000791b4:
    cmp/gt r4,r12
    .org 0x791b6-ORIGIN
L_000791b6:
    mov r10,r0
    .org 0x791b8-ORIGIN
L_000791b8:
    bf/s L_000791be
    .org 0x791ba-ORIGIN
L_000791ba:
    and #0xef,r0
    .org 0x791bc-ORIGIN
L_000791bc:
    or #0x10,r0
    .org 0x791be-ORIGIN
L_000791be:
    exts.w r5,r5
    .org 0x791c0-ORIGIN
L_000791c0:
    cmp/gt r5,r6
    .org 0x791c2-ORIGIN
L_000791c2:
    bf/s L_000791ca
    .org 0x791c4-ORIGIN
L_000791c4:
    mov.b r0,@(0x7,r8)
    .org 0x791c6-ORIGIN
L_000791c6:
    exts.w r5,r5
    .org 0x791c8-ORIGIN
L_000791c8:
    mov r5,r6
    .org 0x791ca-ORIGIN
L_000791ca:
    exts.w r6,r6
    .org 0x791cc-ORIGIN
L_000791cc:
    exts.w r11,r11
    .org 0x791ce-ORIGIN
L_000791ce:
    cmp/ge r11,r6
    .org 0x791d0-ORIGIN
L_000791d0:
    bt L_000791d6
    .org 0x791d2-ORIGIN
L_000791d2:
    exts.w r11,r11
    .org 0x791d4-ORIGIN
L_000791d4:
    mov r11,r6
    .org 0x791d6-ORIGIN
L_000791d6:
    mov.l P_00079234,r3
    .org 0x791d8-ORIGIN
L_000791d8:
    exts.w r4,r4
    .org 0x791da-ORIGIN
L_000791da:
    exts.w r5,r5
    .org 0x791dc-ORIGIN
L_000791dc:
    mov #0x3a,r0
    .org 0x791de-ORIGIN
L_000791de:
    cmp/gt r5,r4
    .org 0x791e0-ORIGIN
L_000791e0:
    mov.w r6,@(r0,r3)
    .org 0x791e2-ORIGIN
L_000791e2:
    bf L_000791e8
    .org 0x791e4-ORIGIN
L_000791e4:
    bra L_000791ea
    .org 0x791e6-ORIGIN
L_000791e6:
    exts.w r5,r2
    .org 0x791e8-ORIGIN
L_000791e8:
    exts.w r4,r2
    .org 0x791ea-ORIGIN
L_000791ea:
    exts.w r2,r6
    .org 0x791ec-ORIGIN
L_000791ec:
    exts.w r11,r11
    .org 0x791ee-ORIGIN
L_000791ee:
    cmp/ge r11,r6
    .org 0x791f0-ORIGIN
L_000791f0:
    bt L_000791f4
    .org 0x791f2-ORIGIN
L_000791f2:
    exts.w r11,r6
    .org 0x791f4-ORIGIN
L_000791f4:
    mov.l P_00079234,r3
    .org 0x791f6-ORIGIN
L_000791f6:
    mov #0x3c,r0
    .org 0x791f8-ORIGIN
L_000791f8:
    mov.w r6,@(r0,r3)
    .org 0x791fa-ORIGIN
L_000791fa:
    mov.l @r15+,r14
    .org 0x791fc-ORIGIN
L_000791fc:
    mov.l @r15+,r13
    .org 0x791fe-ORIGIN
L_000791fe:
    mov.l @r15+,r12
    .org 0x79200-ORIGIN
L_00079200:
    mov.l @r15+,r11
    .org 0x79202-ORIGIN
L_00079202:
    mov.l @r15+,r10
    .org 0x79204-ORIGIN
L_00079204:
    mov.l @r15+,r9
    .org 0x79206-ORIGIN
L_00079206:
    rts
    .org 0x79208-ORIGIN
L_00079208:
    mov.l @r15+,r8
    .org 0x7920a-ORIGIN
P_0007920a:
    .byte 0x0b
    .org 0x7920b-ORIGIN
P_0007920b:
    .byte 0x8a
    .org 0x7920c-ORIGIN
P_0007920c:
    .byte 0x0b
    .org 0x7920d-ORIGIN
P_0007920d:
    .byte 0x86
    .org 0x7920e-ORIGIN
P_0007920e:
    .byte 0x07
    .org 0x7920f-ORIGIN
P_0007920f:
    .byte 0x40
    .org 0x79210-ORIGIN
P_00079210:
    .byte 0x0b
    .org 0x79211-ORIGIN
P_00079211:
    .byte 0x8c
    .org 0x79212-ORIGIN
P_00079212:
    .byte 0x0b
    .org 0x79213-ORIGIN
P_00079213:
    .byte 0x88
    .org 0x79214-ORIGIN
P_00079214:
    .byte 0x0b
    .org 0x79215-ORIGIN
P_00079215:
    .byte 0xa2
    .org 0x79216-ORIGIN
P_00079216:
    .byte 0x07
    .org 0x79217-ORIGIN
P_00079217:
    .byte 0x3a
    .org 0x79218-ORIGIN
P_00079218:
    .byte 0xff
    .org 0x79219-ORIGIN
P_00079219:
    .byte 0xff
    .org 0x7921a-ORIGIN
P_0007921a:
    .byte 0x41
    .org 0x7921b-ORIGIN
P_0007921b:
    .byte 0xa9
    .org 0x7921c-ORIGIN
P_0007921c:
    .byte 0xff
    .org 0x7921d-ORIGIN
P_0007921d:
    .byte 0xff
    .org 0x7921e-ORIGIN
P_0007921e:
    .byte 0x42
    .org 0x7921f-ORIGIN
P_0007921f:
    .byte 0x4c
    .org 0x79220-ORIGIN
P_00079220:
    .byte 0xff
    .org 0x79221-ORIGIN
P_00079221:
    .byte 0xff
    .org 0x79222-ORIGIN
P_00079222:
    .byte 0x23
    .org 0x79223-ORIGIN
P_00079223:
    .byte 0xbc
    .org 0x79224-ORIGIN
P_00079224:
    .byte 0xff
    .org 0x79225-ORIGIN
P_00079225:
    .byte 0xff
    .org 0x79226-ORIGIN
P_00079226:
    .byte 0x12
    .org 0x79227-ORIGIN
P_00079227:
    .byte 0x8c
    .org 0x79228-ORIGIN
P_00079228:
    .byte 0xff
    .org 0x79229-ORIGIN
P_00079229:
    .byte 0xff
    .org 0x7922a-ORIGIN
P_0007922a:
    .byte 0x28
    .org 0x7922b-ORIGIN
P_0007922b:
    .byte 0xf8
    .org 0x7922c-ORIGIN
P_0007922c:
    .byte 0x00
    .org 0x7922d-ORIGIN
P_0007922d:
    .byte 0x00
    .org 0x7922e-ORIGIN
P_0007922e:
    .byte 0x8b
    .org 0x7922f-ORIGIN
P_0007922f:
    .byte 0x38
    .org 0x79230-ORIGIN
P_00079230:
    .byte 0x00
    .org 0x79231-ORIGIN
P_00079231:
    .byte 0x00
    .org 0x79232-ORIGIN
P_00079232:
    .byte 0x83
    .org 0x79233-ORIGIN
P_00079233:
    .byte 0xc1
    .org 0x79234-ORIGIN
P_00079234:
    .byte 0xff
    .org 0x79235-ORIGIN
P_00079235:
    .byte 0xff
    .org 0x79236-ORIGIN
P_00079236:
    .byte 0x41
    .org 0x79237-ORIGIN
P_00079237:
    .byte 0x24
