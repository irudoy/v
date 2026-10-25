! Exact natural RPM helper paths with selected native RAM-root absence.
    .text
    .balign 4
    .set ORIGIN,0x84d8
    .org 0x84da-ORIGIN
P_000084da:
    .byte 0x48
    .org 0x84dd-ORIGIN
P_000084dd:
    .byte 0x3c
    .org 0x84de-ORIGIN
P_000084de:
    .byte 0x0c
    .org 0x870c-ORIGIN
P_0000870c:
    .byte 0x44
    .org 0x8a40-ORIGIN
P_00008a40:
    .byte 0x04
    .org 0x8b3f-ORIGIN
P_00008b3f:
    .byte 0x18
    .org 0x8c40-ORIGIN
P_00008c40:
    .byte 0x00
    .org 0x8c41-ORIGIN
P_00008c41:
    .byte 0x00
    .org 0x8c4b-ORIGIN
P_00008c4b:
    .byte 0x00
    .org 0x8c4c-ORIGIN
P_00008c4c:
    .byte 0x00
    .org 0x8c4d-ORIGIN
P_00008c4d:
    .byte 0x00
    .org 0x90e0-ORIGIN
P_000090e0:
    .byte 0x07
    .org 0x90e1-ORIGIN
P_000090e1:
    .byte 0xd0
    .org 0x4f736-ORIGIN
L_0004f736:
    mov.l P_0004f910,r6
    .org 0x4f738-ORIGIN
L_0004f738:
    mov.b @r6,r0
    .org 0x4f73a-ORIGIN
L_0004f73a:
    tst #0x80,r0
    .org 0x4f73c-ORIGIN
L_0004f73c:
    bt L_0004f752
    .org 0x4f73e-ORIGIN
L_0004f73e:
    mov.l P_0004f914,r6
    .org 0x4f740-ORIGIN
L_0004f740:
    mov #0x16,r0
    .org 0x4f742-ORIGIN
L_0004f742:
    mov.b @(r0,r6),r2
    .org 0x4f744-ORIGIN
L_0004f744:
    mov #-0x40,r6
    .org 0x4f746-ORIGIN
L_0004f746:
    extu.b r6,r6
    .org 0x4f748-ORIGIN
L_0004f748:
    extu.b r2,r2
    .org 0x4f74a-ORIGIN
L_0004f74a:
    cmp/ge r6,r2
    .org 0x4f74c-ORIGIN
L_0004f74c:
    bf L_0004f752
    .org 0x4f74e-ORIGIN
L_0004f74e:
    bra L_0004f754
    .org 0x4f750-ORIGIN
L_0004f750:
    mov #0x1,r2
    .org 0x4f752-ORIGIN
L_0004f752:
    mov #0x0,r2
    .org 0x4f754-ORIGIN
L_0004f754:
    rts
    .org 0x4f756-ORIGIN
L_0004f756:
    mov r2,r0
    .org 0x4f910-ORIGIN
P_0004f910:
    .byte 0xff
    .org 0x4f911-ORIGIN
P_0004f911:
    .byte 0xff
    .org 0x4f912-ORIGIN
P_0004f912:
    .byte 0x24
    .org 0x4f913-ORIGIN
P_0004f913:
    .byte 0x48
    .org 0x4f914-ORIGIN
P_0004f914:
    .byte 0xff
    .org 0x4f915-ORIGIN
P_0004f915:
    .byte 0xff
    .org 0x4f916-ORIGIN
P_0004f916:
    .byte 0x11
    .org 0x4f917-ORIGIN
P_0004f917:
    .byte 0x9c
    .org 0x4f958-ORIGIN
L_0004f958:
    sts.l macl,@-r15
    .org 0x4f95a-ORIGIN
L_0004f95a:
    stc.l gbr,@-r15
    .org 0x4f95c-ORIGIN
L_0004f95c:
    mov.l P_0004fb70,r0
    .org 0x4f95e-ORIGIN
L_0004f95e:
    ldc r0,gbr
    .org 0x4f960-ORIGIN
L_0004f960:
    mov.l P_0004fb74,r6
    .org 0x4f962-ORIGIN
L_0004f962:
    mov.b @r6,r0
    .org 0x4f964-ORIGIN
L_0004f964:
    tst #0x80,r0
    .org 0x4f966-ORIGIN
L_0004f966:
    bf L_0004f9b0
    .org 0x4f968-ORIGIN
L_0004f968:
    mov.l P_0004fb78,r2
    .org 0x4f96a-ORIGIN
L_0004f96a:
    mov #-0x1,r6
    .org 0x4f96c-ORIGIN
L_0004f96c:
    mov.l P_0004fb7c,r7
    .org 0x4f96e-ORIGIN
L_0004f96e:
    extu.w r6,r6
    .org 0x4f970-ORIGIN
L_0004f970:
    mov.w @r2,r4
    .org 0x4f972-ORIGIN
L_0004f972:
    mov.b @(0x4,r7),r0
    .org 0x4f974-ORIGIN
L_0004f974:
    extu.w r4,r4
    .org 0x4f976-ORIGIN
L_0004f976:
    extu.b r0,r5
    .org 0x4f978-ORIGIN
L_0004f978:
    mul.l r4,r5
    .org 0x4f97a-ORIGIN
L_0004f97a:
    sts macl,r2
    .org 0x4f97c-ORIGIN
L_0004f97c:
    cmp/gt r6,r2
    .org 0x4f97e-ORIGIN
L_0004f97e:
    bt L_0004f984
    .org 0x4f980-ORIGIN
L_0004f980:
    mul.l r4,r5
    .org 0x4f982-ORIGIN
L_0004f982:
    sts macl,r6
    .org 0x4f984-ORIGIN
L_0004f984:
    mov.l P_0004fb80,r5
    .org 0x4f986-ORIGIN
L_0004f986:
    mov.w P_0004fa9c,r0
    .org 0x4f988-ORIGIN
L_0004f988:
    extu.w r6,r2
    .org 0x4f98a-ORIGIN
L_0004f98a:
    mov.w @(r0,r5),r6
    .org 0x4f98c-ORIGIN
L_0004f98c:
    extu.w r6,r6
    .org 0x4f98e-ORIGIN
L_0004f98e:
    cmp/ge r2,r6
    .org 0x4f990-ORIGIN
L_0004f990:
    bf L_0004f9b0
    .org 0x4f992-ORIGIN
L_0004f992:
    mov.l P_0004fb84,r2
    .org 0x4f994-ORIGIN
L_0004f994:
    mov #0x17,r0
    .org 0x4f996-ORIGIN
L_0004f996:
    mov.b @(r0,r2),r5
    .org 0x4f998-ORIGIN
L_0004f998:
    mov.b @(0x3,r7),r0
    .org 0x4f99a-ORIGIN
L_0004f99a:
    extu.b r5,r5
    .org 0x4f99c-ORIGIN
L_0004f99c:
    extu.b r0,r2
    .org 0x4f99e-ORIGIN
L_0004f99e:
    cmp/ge r2,r5
    .org 0x4f9a0-ORIGIN
L_0004f9a0:
    bf L_0004f9b0
    .org 0x4f9a2-ORIGIN
L_0004f9a2:
    mov.b @r7,r2
    .org 0x4f9a4-ORIGIN
L_0004f9a4:
    extu.b r2,r2
    .org 0x4f9a6-ORIGIN
L_0004f9a6:
    cmp/ge r2,r5
    .org 0x4f9a8-ORIGIN
L_0004f9a8:
    bf L_0004f9b4
    .org 0x4f9aa-ORIGIN
L_0004f9aa:
    mov #0xc,r0
    .org 0x4f9ac-ORIGIN
L_0004f9ac:
    bra L_0004f9b4
    .org 0x4f9ae-ORIGIN
L_0004f9ae:
    or.b #0x80,@(r0,gbr)
    .org 0x4f9b0-ORIGIN
L_0004f9b0:
    mov #0xc,r0
    .org 0x4f9b2-ORIGIN
L_0004f9b2:
    and.b #0x7f,@(r0,gbr)
    .org 0x4f9b4-ORIGIN
L_0004f9b4:
    mov.b @(0xc,gbr),r0
    .org 0x4f9b6-ORIGIN
L_0004f9b6:
    tst #0x80,r0
    .org 0x4f9b8-ORIGIN
L_0004f9b8:
    movt r0
    .org 0x4f9ba-ORIGIN
L_0004f9ba:
    xor #0x1,r0
    .org 0x4f9bc-ORIGIN
L_0004f9bc:
    extu.b r0,r0
    .org 0x4f9be-ORIGIN
L_0004f9be:
    ldc.l @r15+,gbr
    .org 0x4f9c0-ORIGIN
L_0004f9c0:
    rts
    .org 0x4f9c2-ORIGIN
L_0004f9c2:
    lds.l @r15+,macl
    .org 0x4fa9c-ORIGIN
P_0004fa9c:
    .byte 0x06
    .org 0x4fa9d-ORIGIN
P_0004fa9d:
    .byte 0xa6
    .org 0x4fb70-ORIGIN
P_0004fb70:
    .byte 0xff
    .org 0x4fb71-ORIGIN
P_0004fb71:
    .byte 0xff
    .org 0x4fb72-ORIGIN
P_0004fb72:
    .byte 0x24
    .org 0x4fb73-ORIGIN
P_0004fb73:
    .byte 0x70
    .org 0x4fb74-ORIGIN
P_0004fb74:
    .byte 0x00
    .org 0x4fb75-ORIGIN
P_0004fb75:
    .byte 0x00
    .org 0x4fb76-ORIGIN
P_0004fb76:
    .byte 0x8b
    .org 0x4fb77-ORIGIN
P_0004fb77:
    .byte 0x3f
    .org 0x4fb78-ORIGIN
P_0004fb78:
    .byte 0x00
    .org 0x4fb79-ORIGIN
P_0004fb79:
    .byte 0x00
    .org 0x4fb7a-ORIGIN
P_0004fb7a:
    .byte 0x90
    .org 0x4fb7b-ORIGIN
P_0004fb7b:
    .byte 0xe0
    .org 0x4fb7c-ORIGIN
P_0004fb7c:
    .byte 0x00
    .org 0x4fb7d-ORIGIN
P_0004fb7d:
    .byte 0x00
    .org 0x4fb7e-ORIGIN
P_0004fb7e:
    .byte 0x84
    .org 0x4fb7f-ORIGIN
P_0004fb7f:
    .byte 0xda
    .org 0x4fb80-ORIGIN
P_0004fb80:
    .byte 0xff
    .org 0x4fb81-ORIGIN
P_0004fb81:
    .byte 0xff
    .org 0x4fb82-ORIGIN
P_0004fb82:
    .byte 0x12
    .org 0x4fb83-ORIGIN
P_0004fb83:
    .byte 0x8c
    .org 0x4fb84-ORIGIN
P_0004fb84:
    .byte 0xff
    .org 0x4fb85-ORIGIN
P_0004fb85:
    .byte 0xff
    .org 0x4fb86-ORIGIN
P_0004fb86:
    .byte 0x11
    .org 0x4fb87-ORIGIN
P_0004fb87:
    .byte 0x9c
    .org 0x5038a-ORIGIN
L_0005038a:
    mov.l P_00050460,r1
    .org 0x5038c-ORIGIN
L_0005038c:
    mov.l P_00050464,r6
    .org 0x5038e-ORIGIN
L_0005038e:
    mov.b @(0x4,r6),r0
    .org 0x50390-ORIGIN
L_00050390:
    tst #0x80,r0
    .org 0x50392-ORIGIN
L_00050392:
    bf L_000503da
    .org 0x50394-ORIGIN
L_00050394:
    mov.l P_00050468,r6
    .org 0x50396-ORIGIN
L_00050396:
    mov.b @r6,r0
    .org 0x50398-ORIGIN
L_00050398:
    tst #0x20,r0
    .org 0x5039a-ORIGIN
L_0005039a:
    bt L_000503a8
    .org 0x5039c-ORIGIN
L_0005039c:
    mov.l P_0005046c,r2
    .org 0x5039e-ORIGIN
L_0005039e:
    mov.l P_00050470,r5
    .org 0x503a0-ORIGIN
L_000503a0:
    mov.b @r2,r6
    .org 0x503a2-ORIGIN
L_000503a2:
    mov.b @r5,r2
    .org 0x503a4-ORIGIN
L_000503a4:
    cmp/hs r2,r6
    .org 0x503a6-ORIGIN
L_000503a6:
    bt L_000503da
    .org 0x503a8-ORIGIN
L_000503a8:
    mov r4,r0
    .org 0x503aa-ORIGIN
L_000503aa:
    cmp/eq #0x1,r0
    .org 0x503ac-ORIGIN
L_000503ac:
    bf L_000503b2
    .org 0x503ae-ORIGIN
L_000503ae:
    bra L_000503d6
    .org 0x503b0-ORIGIN
L_000503b0:
    mov.b @(0xb,r1),r0
    .org 0x503b2-ORIGIN
L_000503b2:
    mov.l P_00050474,r6
    .org 0x503b4-ORIGIN
L_000503b4:
    mov.b @r6,r0
    .org 0x503b6-ORIGIN
L_000503b6:
    and #0x80,r0
    .org 0x503b8-ORIGIN
L_000503b8:
    mov r0,r2
    .org 0x503ba-ORIGIN
L_000503ba:
    mov r4,r0
    .org 0x503bc-ORIGIN
L_000503bc:
    cmp/eq #0x2,r0
    .org 0x503be-ORIGIN
L_000503be:
    bf L_000503cc
    .org 0x503c0-ORIGIN
L_000503c0:
    tst r2,r2
    .org 0x503c2-ORIGIN
L_000503c2:
    bf L_000503c8
    .org 0x503c4-ORIGIN
L_000503c4:
    bra L_000503d6
    .org 0x503c6-ORIGIN
L_000503c6:
    mov.b @(0x1,r1),r0
    .org 0x503c8-ORIGIN
L_000503c8:
    bra L_000503d6
    .org 0x503ca-ORIGIN
L_000503ca:
    mov.b @r1,r0
    .org 0x503cc-ORIGIN
L_000503cc:
    tst r2,r2
    .org 0x503ce-ORIGIN
L_000503ce:
    bf L_000503d4
    .org 0x503d0-ORIGIN
L_000503d0:
    bra L_000503d6
    .org 0x503d2-ORIGIN
L_000503d2:
    mov.b @(0xd,r1),r0
    .org 0x503d4-ORIGIN
L_000503d4:
    mov.b @(0xc,r1),r0
    .org 0x503d6-ORIGIN
L_000503d6:
    bra L_000503dc
    .org 0x503d8-ORIGIN
L_000503d8:
    extu.b r0,r2
    .org 0x503da-ORIGIN
L_000503da:
    mov #0x0,r2
    .org 0x503dc-ORIGIN
L_000503dc:
    rts
    .org 0x503de-ORIGIN
L_000503de:
    mov r2,r0
    .org 0x50460-ORIGIN
P_00050460:
    .byte 0x00
    .org 0x50461-ORIGIN
P_00050461:
    .byte 0x00
    .org 0x50462-ORIGIN
P_00050462:
    .byte 0x8c
    .org 0x50463-ORIGIN
P_00050463:
    .byte 0x40
    .org 0x50464-ORIGIN
P_00050464:
    .byte 0xff
    .org 0x50465-ORIGIN
P_00050465:
    .byte 0xff
    .org 0x50466-ORIGIN
P_00050466:
    .byte 0x42
    .org 0x50467-ORIGIN
P_00050467:
    .byte 0x4c
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
    .org 0x5046c-ORIGIN
P_0005046c:
    .byte 0xff
    .org 0x5046d-ORIGIN
P_0005046d:
    .byte 0xff
    .org 0x5046e-ORIGIN
P_0005046e:
    .byte 0x10
    .org 0x5046f-ORIGIN
P_0005046f:
    .byte 0x6a
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
    .org 0x50474-ORIGIN
P_00050474:
    .byte 0x00
    .org 0x50475-ORIGIN
P_00050475:
    .byte 0x00
    .org 0x50476-ORIGIN
P_00050476:
    .byte 0x87
    .org 0x50477-ORIGIN
P_00050477:
    .byte 0x0c
