! Natural scalar RAM leaf arithmetic with original branch and RTS delay slots.
    .text
    .balign 4
    .set ORIGIN,0x8440
    .org 0x8440-ORIGIN
P_00008440:
    .byte 0x0a
    .org 0x870c-ORIGIN
P_0000870c:
    .byte 0x44
    .org 0x8b3f-ORIGIN
P_00008b3f:
    .byte 0x18
    .org 0x259be-ORIGIN
L_000259be:
    extu.b r7,r7
    .org 0x259c0-ORIGIN
L_000259c0:
    tst r7,r7
    .org 0x259c2-ORIGIN
L_000259c2:
    bf/s L_000259c8
    .org 0x259c4-ORIGIN
L_000259c4:
    mov r4,r2
    .org 0x259c6-ORIGIN
L_000259c6:
    sub r6,r2
    .org 0x259c8-ORIGIN
L_000259c8:
    cmp/gt r5,r2
    .org 0x259ca-ORIGIN
L_000259ca:
    movt r2
    .org 0x259cc-ORIGIN
L_000259cc:
    rts
    .org 0x259ce-ORIGIN
L_000259ce:
    extu.b r2,r0
    .org 0x39588-ORIGIN
L_00039588:
    stc.l gbr,@-r15
    .org 0x3958a-ORIGIN
L_0003958a:
    mov.l P_000396f4,r0
    .org 0x3958c-ORIGIN
L_0003958c:
    ldc r0,gbr
    .org 0x3958e-ORIGIN
L_0003958e:
    mov.b @(0x73,gbr),r0
    .org 0x39590-ORIGIN
L_00039590:
    mov.l P_00039708,r2
    .org 0x39592-ORIGIN
L_00039592:
    extu.b r0,r5
    .org 0x39594-ORIGIN
L_00039594:
    mov.b @(0x7,r2),r0
    .org 0x39596-ORIGIN
L_00039596:
    extu.b r0,r4
    .org 0x39598-ORIGIN
L_00039598:
    cmp/gt r4,r5
    .org 0x3959a-ORIGIN
L_0003959a:
    bt L_000395a6
    .org 0x3959c-ORIGIN
L_0003959c:
    mov r5,r2
    .org 0x3959e-ORIGIN
L_0003959e:
    add #0x2,r2
    .org 0x395a0-ORIGIN
L_000395a0:
    cmp/gt r4,r2
    .org 0x395a2-ORIGIN
L_000395a2:
    bt L_000395a8
    .org 0x395a4-ORIGIN
L_000395a4:
    add #0x2,r5
    .org 0x395a6-ORIGIN
L_000395a6:
    mov r5,r4
    .org 0x395a8-ORIGIN
L_000395a8:
    extu.b r4,r0
    .org 0x395aa-ORIGIN
L_000395aa:
    rts
    .org 0x395ac-ORIGIN
L_000395ac:
    ldc.l @r15+,gbr
    .org 0x396f4-ORIGIN
P_000396f4:
    .byte 0xff
    .org 0x396f5-ORIGIN
P_000396f5:
    .byte 0xff
    .org 0x396f6-ORIGIN
P_000396f6:
    .byte 0x11
    .org 0x396f7-ORIGIN
P_000396f7:
    .byte 0x14
    .org 0x39708-ORIGIN
P_00039708:
    .byte 0xff
    .org 0x39709-ORIGIN
P_00039709:
    .byte 0xff
    .org 0x3970a-ORIGIN
P_0003970a:
    .byte 0x10
    .org 0x3970b-ORIGIN
P_0003970b:
    .byte 0x7a
    .org 0x39874-ORIGIN
L_00039874:
    mov.l P_000399ac,r2
    .org 0x39876-ORIGIN
L_00039876:
    mov.w P_000398f4,r0
    .org 0x39878-ORIGIN
L_00039878:
    mov.b @(r0,r2),r5
    .org 0x3987a-ORIGIN
L_0003987a:
    mov.l P_000399c4,r2
    .org 0x3987c-ORIGIN
L_0003987c:
    extu.b r5,r5
    .org 0x3987e-ORIGIN
L_0003987e:
    mov.b @(0x2,r2),r0
    .org 0x39880-ORIGIN
L_00039880:
    extu.b r0,r4
    .org 0x39882-ORIGIN
L_00039882:
    cmp/gt r4,r5
    .org 0x39884-ORIGIN
L_00039884:
    bt L_00039890
    .org 0x39886-ORIGIN
L_00039886:
    mov r5,r2
    .org 0x39888-ORIGIN
L_00039888:
    add #0x2,r2
    .org 0x3988a-ORIGIN
L_0003988a:
    cmp/gt r4,r2
    .org 0x3988c-ORIGIN
L_0003988c:
    bt L_00039892
    .org 0x3988e-ORIGIN
L_0003988e:
    add #0x2,r5
    .org 0x39890-ORIGIN
L_00039890:
    mov r5,r4
    .org 0x39892-ORIGIN
L_00039892:
    rts
    .org 0x39894-ORIGIN
L_00039894:
    extu.b r4,r0
    .org 0x398f4-ORIGIN
P_000398f4:
    .byte 0x01
    .org 0x398f5-ORIGIN
P_000398f5:
    .byte 0x29
    .org 0x399ac-ORIGIN
P_000399ac:
    .byte 0xff
    .org 0x399ad-ORIGIN
P_000399ad:
    .byte 0xff
    .org 0x399ae-ORIGIN
P_000399ae:
    .byte 0x1e
    .org 0x399af-ORIGIN
P_000399af:
    .byte 0x60
    .org 0x399c4-ORIGIN
P_000399c4:
    .byte 0xff
    .org 0x399c5-ORIGIN
P_000399c5:
    .byte 0xff
    .org 0x399c6-ORIGIN
P_000399c6:
    .byte 0x10
    .org 0x399c7-ORIGIN
P_000399c7:
    .byte 0x7a
    .org 0x468b0-ORIGIN
L_000468b0:
    mov.l r14,@-r15
    .org 0x468b2-ORIGIN
L_000468b2:
    mov.l P_00046928,r1
    .org 0x468b4-ORIGIN
L_000468b4:
    mov.w P_00046918,r0
    .org 0x468b6-ORIGIN
L_000468b6:
    mov.w @(r0,r1),r2
    .org 0x468b8-ORIGIN
L_000468b8:
    mov.w P_0004691a,r0
    .org 0x468ba-ORIGIN
L_000468ba:
    extu.w r2,r2
    .org 0x468bc-ORIGIN
L_000468bc:
    mov.b @(r0,r1),r5
    .org 0x468be-ORIGIN
L_000468be:
    mov.w P_0004691c,r0
    .org 0x468c0-ORIGIN
L_000468c0:
    extu.b r5,r6
    .org 0x468c2-ORIGIN
L_000468c2:
    mov.l P_0004692c,r5
    .org 0x468c4-ORIGIN
L_000468c4:
    mov.w @(r0,r1),r4
    .org 0x468c6-ORIGIN
L_000468c6:
    shll 2 r6
    .org 0x468c8-ORIGIN
L_000468c8:
    mov.w P_0004691e,r0
    .org 0x468ca-ORIGIN
L_000468ca:
    add r6,r2
    .org 0x468cc-ORIGIN
L_000468cc:
    extu.w r4,r4
    .org 0x468ce-ORIGIN
L_000468ce:
    mov.b @(r0,r1),r7
    .org 0x468d0-ORIGIN
L_000468d0:
    add r4,r2
    .org 0x468d2-ORIGIN
L_000468d2:
    mov.w P_00046920,r0
    .org 0x468d4-ORIGIN
L_000468d4:
    extu.b r7,r7
    .org 0x468d6-ORIGIN
L_000468d6:
    mov.b @(r0,r1),r14
    .org 0x468d8-ORIGIN
L_000468d8:
    mov #0x22,r0
    .org 0x468da-ORIGIN
L_000468da:
    mov.w @(r0,r5),r6
    .org 0x468dc-ORIGIN
L_000468dc:
    mov.w P_00046922,r0
    .org 0x468de-ORIGIN
L_000468de:
    extu.b r14,r14
    .org 0x468e0-ORIGIN
L_000468e0:
    mov.l P_00046930,r5
    .org 0x468e2-ORIGIN
L_000468e2:
    add r6,r2
    .org 0x468e4-ORIGIN
L_000468e4:
    add r7,r2
    .org 0x468e6-ORIGIN
L_000468e6:
    mov.w @(r0,r1),r6
    .org 0x468e8-ORIGIN
L_000468e8:
    mov.b @r5,r0
    .org 0x468ea-ORIGIN
L_000468ea:
    add r14,r2
    .org 0x468ec-ORIGIN
L_000468ec:
    add r6,r2
    .org 0x468ee-ORIGIN
L_000468ee:
    tst #0x80,r0
    .org 0x468f0-ORIGIN
L_000468f0:
    bt/s L_000468fe
    .org 0x468f2-ORIGIN
L_000468f2:
    mov r2,r6
    .org 0x468f4-ORIGIN
L_000468f4:
    mov.l P_00046934,r5
    .org 0x468f6-ORIGIN
L_000468f6:
    mov.w P_00046924,r0
    .org 0x468f8-ORIGIN
L_000468f8:
    mov.b @(r0,r5),r2
    .org 0x468fa-ORIGIN
L_000468fa:
    extu.b r2,r2
    .org 0x468fc-ORIGIN
L_000468fc:
    add r2,r6
    .org 0x468fe-ORIGIN
L_000468fe:
    cmp/pz r6
    .org 0x46900-ORIGIN
L_00046900:
    bt/s L_00046906
    .org 0x46902-ORIGIN
L_00046902:
    mov r6,r2
    .org 0x46904-ORIGIN
L_00046904:
    mov #0x0,r2
    .org 0x46906-ORIGIN
L_00046906:
    mov #-0x1,r6
    .org 0x46908-ORIGIN
L_00046908:
    extu.w r6,r6
    .org 0x4690a-ORIGIN
L_0004690a:
    cmp/gt r6,r2
    .org 0x4690c-ORIGIN
L_0004690c:
    bf L_00046910
    .org 0x4690e-ORIGIN
L_0004690e:
    mov r6,r2
    .org 0x46910-ORIGIN
L_00046910:
    mov.w P_00046926,r0
    .org 0x46912-ORIGIN
L_00046912:
    mov.w r2,@(r0,r1)
    .org 0x46914-ORIGIN
L_00046914:
    rts
    .org 0x46916-ORIGIN
L_00046916:
    mov.l @r15+,r14
    .org 0x46918-ORIGIN
P_00046918:
    .byte 0x04
    .org 0x46919-ORIGIN
P_00046919:
    .byte 0xc6
    .org 0x4691a-ORIGIN
P_0004691a:
    .byte 0x04
    .org 0x4691b-ORIGIN
P_0004691b:
    .byte 0xd9
    .org 0x4691c-ORIGIN
P_0004691c:
    .byte 0x04
    .org 0x4691d-ORIGIN
P_0004691d:
    .byte 0xbc
    .org 0x4691e-ORIGIN
P_0004691e:
    .byte 0x03
    .org 0x4691f-ORIGIN
P_0004691f:
    .byte 0x20
    .org 0x46920-ORIGIN
P_00046920:
    .byte 0x01
    .org 0x46921-ORIGIN
P_00046921:
    .byte 0x6b
    .org 0x46922-ORIGIN
P_00046922:
    .byte 0x04
    .org 0x46923-ORIGIN
P_00046923:
    .byte 0x7e
    .org 0x46924-ORIGIN
P_00046924:
    .byte 0x01
    .org 0x46925-ORIGIN
P_00046925:
    .byte 0x02
    .org 0x46926-ORIGIN
P_00046926:
    .byte 0x04
    .org 0x46927-ORIGIN
P_00046927:
    .byte 0xae
    .org 0x46928-ORIGIN
P_00046928:
    .byte 0xff
    .org 0x46929-ORIGIN
P_00046929:
    .byte 0xff
    .org 0x4692a-ORIGIN
P_0004692a:
    .byte 0x12
    .org 0x4692b-ORIGIN
P_0004692b:
    .byte 0x8c
    .org 0x4692c-ORIGIN
P_0004692c:
    .byte 0xff
    .org 0x4692d-ORIGIN
P_0004692d:
    .byte 0xff
    .org 0x4692e-ORIGIN
P_0004692e:
    .byte 0x12
    .org 0x4692f-ORIGIN
P_0004692f:
    .byte 0x0e
    .org 0x46930-ORIGIN
P_00046930:
    .byte 0x00
    .org 0x46931-ORIGIN
P_00046931:
    .byte 0x00
    .org 0x46932-ORIGIN
P_00046932:
    .byte 0x87
    .org 0x46933-ORIGIN
P_00046933:
    .byte 0x0c
    .org 0x46934-ORIGIN
P_00046934:
    .byte 0xff
    .org 0x46935-ORIGIN
P_00046935:
    .byte 0xff
    .org 0x46936-ORIGIN
P_00046936:
    .byte 0x1e
    .org 0x46937-ORIGIN
P_00046937:
    .byte 0x60
    .org 0x4ab94-ORIGIN
L_0004ab94:
    sts.l macl,@-r15
    .org 0x4ab96-ORIGIN
L_0004ab96:
    stc.l gbr,@-r15
    .org 0x4ab98-ORIGIN
L_0004ab98:
    mov.l P_0004ad00,r0
    .org 0x4ab9a-ORIGIN
L_0004ab9a:
    ldc r0,gbr
    .org 0x4ab9c-ORIGIN
L_0004ab9c:
    mov.w @(0x3e,gbr),r0
    .org 0x4ab9e-ORIGIN
L_0004ab9e:
    extu.w r0,r5
    .org 0x4aba0-ORIGIN
L_0004aba0:
    mov.w @(0x30,gbr),r0
    .org 0x4aba2-ORIGIN
L_0004aba2:
    extu.w r0,r4
    .org 0x4aba4-ORIGIN
L_0004aba4:
    cmp/ge r4,r5
    .org 0x4aba6-ORIGIN
L_0004aba6:
    bf L_0004abc6
    .org 0x4aba8-ORIGIN
L_0004aba8:
    mov.w @(0xc,gbr),r0
    .org 0x4abaa-ORIGIN
L_0004abaa:
    sub r4,r5
    .org 0x4abac-ORIGIN
L_0004abac:
    mov #-0x1,r6
    .org 0x4abae-ORIGIN
L_0004abae:
    extu.w r0,r2
    .org 0x4abb0-ORIGIN
L_0004abb0:
    mul.l r2,r5
    .org 0x4abb2-ORIGIN
L_0004abb2:
    extu.w r6,r6
    .org 0x4abb4-ORIGIN
L_0004abb4:
    sts macl,r2
    .org 0x4abb6-ORIGIN
L_0004abb6:
    shlr 8 r2
    .org 0x4abb8-ORIGIN
L_0004abb8:
    shlr 2 r2
    .org 0x4abba-ORIGIN
L_0004abba:
    shlr 2 r2
    .org 0x4abbc-ORIGIN
L_0004abbc:
    shlr 2 r2
    .org 0x4abbe-ORIGIN
L_0004abbe:
    cmp/hi r6,r2
    .org 0x4abc0-ORIGIN
L_0004abc0:
    bf L_0004abc8
    .org 0x4abc2-ORIGIN
L_0004abc2:
    bra L_0004abc8
    .org 0x4abc4-ORIGIN
L_0004abc4:
    mov r6,r2
    .org 0x4abc6-ORIGIN
L_0004abc6:
    mov #0x0,r2
    .org 0x4abc8-ORIGIN
L_0004abc8:
    mov.l P_0004acfc,r5
    .org 0x4abca-ORIGIN
L_0004abca:
    mov.w P_0004abd6,r0
    .org 0x4abcc-ORIGIN
L_0004abcc:
    mov.w r2,@(r0,r5)
    .org 0x4abce-ORIGIN
L_0004abce:
    ldc.l @r15+,gbr
    .org 0x4abd0-ORIGIN
L_0004abd0:
    rts
    .org 0x4abd2-ORIGIN
L_0004abd2:
    lds.l @r15+,macl
    .org 0x4abd6-ORIGIN
P_0004abd6:
    .byte 0x06
    .org 0x4abd7-ORIGIN
P_0004abd7:
    .byte 0x56
    .org 0x4acfc-ORIGIN
P_0004acfc:
    .byte 0xff
    .org 0x4acfd-ORIGIN
P_0004acfd:
    .byte 0xff
    .org 0x4acfe-ORIGIN
P_0004acfe:
    .byte 0x12
    .org 0x4acff-ORIGIN
P_0004acff:
    .byte 0x8c
    .org 0x4ad00-ORIGIN
P_0004ad00:
    .byte 0xff
    .org 0x4ad01-ORIGIN
P_0004ad01:
    .byte 0xff
    .org 0x4ad02-ORIGIN
P_0004ad02:
    .byte 0x22
    .org 0x4ad03-ORIGIN
P_0004ad03:
    .byte 0xdc
    .org 0x4af38-ORIGIN
L_0004af38:
    stc.l gbr,@-r15
    .org 0x4af3a-ORIGIN
L_0004af3a:
    mov.l P_0004afc4,r0
    .org 0x4af3c-ORIGIN
L_0004af3c:
    ldc r0,gbr
    .org 0x4af3e-ORIGIN
L_0004af3e:
    mov.l P_0004afc4,r5
    .org 0x4af40-ORIGIN
L_0004af40:
    mov.w P_0004af8a,r0
    .org 0x4af42-ORIGIN
L_0004af42:
    mov.l P_0004afd8,r4
    .org 0x4af44-ORIGIN
L_0004af44:
    mov.b @(r0,r5),r0
    .org 0x4af46-ORIGIN
L_0004af46:
    and #0x7f,r0
    .org 0x4af48-ORIGIN
L_0004af48:
    mov r0,r6
    .org 0x4af4a-ORIGIN
L_0004af4a:
    mov.b r0,@(0x52,gbr)
    .org 0x4af4c-ORIGIN
L_0004af4c:
    mov.w P_0004af8c,r0
    .org 0x4af4e-ORIGIN
L_0004af4e:
    mov.b @(r0,r5),r0
    .org 0x4af50-ORIGIN
L_0004af50:
    and #0x7f,r0
    .org 0x4af52-ORIGIN
L_0004af52:
    mov r0,r5
    .org 0x4af54-ORIGIN
L_0004af54:
    mov.b r0,@(0x54,gbr)
    .org 0x4af56-ORIGIN
L_0004af56:
    mov.b @r4,r0
    .org 0x4af58-ORIGIN
L_0004af58:
    tst #0x2,r0
    .org 0x4af5a-ORIGIN
L_0004af5a:
    bt L_0004af6a
    .org 0x4af5c-ORIGIN
L_0004af5c:
    sub r6,r5
    .org 0x4af5e-ORIGIN
L_0004af5e:
    exts.w r5,r2
    .org 0x4af60-ORIGIN
L_0004af60:
    cmp/pz r2
    .org 0x4af62-ORIGIN
L_0004af62:
    bt L_0004af66
    .org 0x4af64-ORIGIN
L_0004af64:
    mov #0x0,r2
    .org 0x4af66-ORIGIN
L_0004af66:
    bra L_0004af6c
    .org 0x4af68-ORIGIN
L_0004af68:
    mov r2,r0
    .org 0x4af6a-ORIGIN
L_0004af6a:
    mov #0x0,r0
    .org 0x4af6c-ORIGIN
L_0004af6c:
    mov.l P_0004af94,r5
    .org 0x4af6e-ORIGIN
L_0004af6e:
    mov.b r0,@(0x53,gbr)
    .org 0x4af70-ORIGIN
L_0004af70:
    mov #0x13,r0
    .org 0x4af72-ORIGIN
L_0004af72:
    mov.b @(r0,r5),r2
    .org 0x4af74-ORIGIN
L_0004af74:
    extu.b r2,r2
    .org 0x4af76-ORIGIN
L_0004af76:
    sub r2,r6
    .org 0x4af78-ORIGIN
L_0004af78:
    exts.w r6,r2
    .org 0x4af7a-ORIGIN
L_0004af7a:
    cmp/pz r2
    .org 0x4af7c-ORIGIN
L_0004af7c:
    bt L_0004af80
    .org 0x4af7e-ORIGIN
L_0004af7e:
    mov #0x0,r2
    .org 0x4af80-ORIGIN
L_0004af80:
    mov r2,r0
    .org 0x4af82-ORIGIN
L_0004af82:
    mov.l P_0004afd4,r2
    .org 0x4af84-ORIGIN
L_0004af84:
    mov.b r0,@(0x1,r2)
    .org 0x4af86-ORIGIN
L_0004af86:
    rts
    .org 0x4af88-ORIGIN
L_0004af88:
    ldc.l @r15+,gbr
    .org 0x4af8a-ORIGIN
P_0004af8a:
    .byte 0x03
    .org 0x4af8b-ORIGIN
P_0004af8b:
    .byte 0x83
    .org 0x4af8c-ORIGIN
P_0004af8c:
    .byte 0x03
    .org 0x4af8d-ORIGIN
P_0004af8d:
    .byte 0x84
    .org 0x4af94-ORIGIN
P_0004af94:
    .byte 0xff
    .org 0x4af95-ORIGIN
P_0004af95:
    .byte 0xff
    .org 0x4af96-ORIGIN
P_0004af96:
    .byte 0x11
    .org 0x4af97-ORIGIN
P_0004af97:
    .byte 0x9c
    .org 0x4afc4-ORIGIN
P_0004afc4:
    .byte 0xff
    .org 0x4afc5-ORIGIN
P_0004afc5:
    .byte 0xff
    .org 0x4afc6-ORIGIN
P_0004afc6:
    .byte 0x12
    .org 0x4afc7-ORIGIN
P_0004afc7:
    .byte 0x8c
    .org 0x4afd4-ORIGIN
P_0004afd4:
    .byte 0xff
    .org 0x4afd5-ORIGIN
P_0004afd5:
    .byte 0xff
    .org 0x4afd6-ORIGIN
P_0004afd6:
    .byte 0x23
    .org 0x4afd7-ORIGIN
P_0004afd7:
    .byte 0xbc
    .org 0x4afd8-ORIGIN
P_0004afd8:
    .byte 0x00
    .org 0x4afd9-ORIGIN
P_0004afd9:
    .byte 0x00
    .org 0x4afda-ORIGIN
P_0004afda:
    .byte 0x8b
    .org 0x4afdb-ORIGIN
P_0004afdb:
    .byte 0x3f
    .org 0x4bb6a-ORIGIN
L_0004bb6a:
    mov.l P_0004bc68,r7
    .org 0x4bb6c-ORIGIN
L_0004bb6c:
    mov.l P_0004bc44,r5
    .org 0x4bb6e-ORIGIN
L_0004bb6e:
    mov.b @(0x6,r7),r0
    .org 0x4bb70-ORIGIN
L_0004bb70:
    mov.b @r7,r4
    .org 0x4bb72-ORIGIN
L_0004bb72:
    extu.b r0,r6
    .org 0x4bb74-ORIGIN
L_0004bb74:
    mov.w P_0004bba6,r0
    .org 0x4bb76-ORIGIN
L_0004bb76:
    extu.b r4,r4
    .org 0x4bb78-ORIGIN
L_0004bb78:
    mov.b @(r0,r5),r2
    .org 0x4bb7a-ORIGIN
L_0004bb7a:
    add r4,r6
    .org 0x4bb7c-ORIGIN
L_0004bb7c:
    exts.w r6,r6
    .org 0x4bb7e-ORIGIN
L_0004bb7e:
    extu.b r2,r5
    .org 0x4bb80-ORIGIN
L_0004bb80:
    shlr 2 r5
    .org 0x4bb82-ORIGIN
L_0004bb82:
    shlr 2 r5
    .org 0x4bb84-ORIGIN
L_0004bb84:
    sub r5,r6
    .org 0x4bb86-ORIGIN
L_0004bb86:
    exts.w r6,r6
    .org 0x4bb88-ORIGIN
L_0004bb88:
    cmp/pz r6
    .org 0x4bb8a-ORIGIN
L_0004bb8a:
    bt L_0004bb8e
    .org 0x4bb8c-ORIGIN
L_0004bb8c:
    mov #0x0,r6
    .org 0x4bb8e-ORIGIN
L_0004bb8e:
    exts.w r6,r2
    .org 0x4bb90-ORIGIN
L_0004bb90:
    mov #-0x1,r6
    .org 0x4bb92-ORIGIN
L_0004bb92:
    extu.b r6,r6
    .org 0x4bb94-ORIGIN
L_0004bb94:
    cmp/gt r6,r2
    .org 0x4bb96-ORIGIN
L_0004bb96:
    bf L_0004bb9a
    .org 0x4bb98-ORIGIN
L_0004bb98:
    mov r6,r2
    .org 0x4bb9a-ORIGIN
L_0004bb9a:
    mov r2,r0
    .org 0x4bb9c-ORIGIN
L_0004bb9c:
    mov.l P_0004bc78,r2
    .org 0x4bb9e-ORIGIN
L_0004bb9e:
    rts
    .org 0x4bba0-ORIGIN
L_0004bba0:
    mov.b r0,@(0x9,r2)
    .org 0x4bba6-ORIGIN
P_0004bba6:
    .byte 0x03
    .org 0x4bba7-ORIGIN
P_0004bba7:
    .byte 0xcb
    .org 0x4bc44-ORIGIN
P_0004bc44:
    .byte 0xff
    .org 0x4bc45-ORIGIN
P_0004bc45:
    .byte 0xff
    .org 0x4bc46-ORIGIN
P_0004bc46:
    .byte 0x12
    .org 0x4bc47-ORIGIN
P_0004bc47:
    .byte 0x8c
    .org 0x4bc68-ORIGIN
P_0004bc68:
    .byte 0xff
    .org 0x4bc69-ORIGIN
P_0004bc69:
    .byte 0xff
    .org 0x4bc6a-ORIGIN
P_0004bc6a:
    .byte 0x22
    .org 0x4bc6b-ORIGIN
P_0004bc6b:
    .byte 0xf8
    .org 0x4bc78-ORIGIN
P_0004bc78:
    .byte 0xff
    .org 0x4bc79-ORIGIN
P_0004bc79:
    .byte 0xff
    .org 0x4bc7a-ORIGIN
P_0004bc7a:
    .byte 0x23
    .org 0x4bc7b-ORIGIN
P_0004bc7b:
    .byte 0xbc
    .org 0x4c136-ORIGIN
L_0004c136:
    stc.l gbr,@-r15
    .org 0x4c138-ORIGIN
L_0004c138:
    mov.l P_0004c1d8,r0
    .org 0x4c13a-ORIGIN
L_0004c13a:
    ldc r0,gbr
    .org 0x4c13c-ORIGIN
L_0004c13c:
    mov.l P_0004c1a8,r6
    .org 0x4c13e-ORIGIN
L_0004c13e:
    mov.l P_0004c1dc,r5
    .org 0x4c140-ORIGIN
L_0004c140:
    mov.b @r6,r0
    .org 0x4c142-ORIGIN
L_0004c142:
    and #0x40,r0
    .org 0x4c144-ORIGIN
L_0004c144:
    mov r0,r2
    .org 0x4c146-ORIGIN
L_0004c146:
    tst r0,r0
    .org 0x4c148-ORIGIN
L_0004c148:
    mov.b @(0x4,r5),r0
    .org 0x4c14a-ORIGIN
L_0004c14a:
    bf/s L_0004c150
    .org 0x4c14c-ORIGIN
L_0004c14c:
    or #0x2,r0
    .org 0x4c14e-ORIGIN
L_0004c14e:
    and #0xfd,r0
    .org 0x4c150-ORIGIN
L_0004c150:
    mov.l P_0004c1e0,r6
    .org 0x4c152-ORIGIN
L_0004c152:
    mov.b r0,@(0x4,r5)
    .org 0x4c154-ORIGIN
L_0004c154:
    mov #0x2b,r0
    .org 0x4c156-ORIGIN
L_0004c156:
    mov.b @(r0,r6),r5
    .org 0x4c158-ORIGIN
L_0004c158:
    extu.b r5,r0
    .org 0x4c15a-ORIGIN
L_0004c15a:
    cmp/eq #0x1,r0
    .org 0x4c15c-ORIGIN
L_0004c15c:
    bt L_0004c174
    .org 0x4c15e-ORIGIN
L_0004c15e:
    cmp/eq #0x2,r0
    .org 0x4c160-ORIGIN
L_0004c160:
    bt L_0004c174
    .org 0x4c162-ORIGIN
L_0004c162:
    tst r2,r2
    .org 0x4c164-ORIGIN
L_0004c164:
    bf L_0004c16c
    .org 0x4c166-ORIGIN
L_0004c166:
    mov.b @(0x9c,gbr),r0
    .org 0x4c168-ORIGIN
L_0004c168:
    tst #0x20,r0
    .org 0x4c16a-ORIGIN
L_0004c16a:
    bt L_0004c174
    .org 0x4c16c-ORIGIN
L_0004c16c:
    mov.l P_0004c1a0,r6
    .org 0x4c16e-ORIGIN
L_0004c16e:
    mov.w P_0004c182,r0
    .org 0x4c170-ORIGIN
L_0004c170:
    bra L_0004c17a
    .org 0x4c172-ORIGIN
L_0004c172:
    mov.b @(r0,r6),r0
    .org 0x4c174-ORIGIN
L_0004c174:
    mov.l P_0004c1a0,r6
    .org 0x4c176-ORIGIN
L_0004c176:
    mov.w P_0004c184,r0
    .org 0x4c178-ORIGIN
L_0004c178:
    mov.b @(r0,r6),r0
    .org 0x4c17a-ORIGIN
L_0004c17a:
    mov.b r0,@(0x48,gbr)
    .org 0x4c17c-ORIGIN
L_0004c17c:
    rts
    .org 0x4c17e-ORIGIN
L_0004c17e:
    ldc.l @r15+,gbr
    .org 0x4c182-ORIGIN
P_0004c182:
    .byte 0x05
    .org 0x4c183-ORIGIN
P_0004c183:
    .byte 0xa5
    .org 0x4c184-ORIGIN
P_0004c184:
    .byte 0x05
    .org 0x4c185-ORIGIN
P_0004c185:
    .byte 0xa4
    .org 0x4c1a0-ORIGIN
P_0004c1a0:
    .byte 0xff
    .org 0x4c1a1-ORIGIN
P_0004c1a1:
    .byte 0xff
    .org 0x4c1a2-ORIGIN
P_0004c1a2:
    .byte 0x12
    .org 0x4c1a3-ORIGIN
P_0004c1a3:
    .byte 0x8c
    .org 0x4c1a8-ORIGIN
P_0004c1a8:
    .byte 0xff
    .org 0x4c1a9-ORIGIN
P_0004c1a9:
    .byte 0xff
    .org 0x4c1aa-ORIGIN
P_0004c1aa:
    .byte 0x41
    .org 0x4c1ab-ORIGIN
P_0004c1ab:
    .byte 0x84
    .org 0x4c1d8-ORIGIN
P_0004c1d8:
    .byte 0xff
    .org 0x4c1d9-ORIGIN
P_0004c1d9:
    .byte 0xff
    .org 0x4c1da-ORIGIN
P_0004c1da:
    .byte 0x23
    .org 0x4c1db-ORIGIN
P_0004c1db:
    .byte 0xbc
    .org 0x4c1dc-ORIGIN
P_0004c1dc:
    .byte 0xff
    .org 0x4c1dd-ORIGIN
P_0004c1dd:
    .byte 0xff
    .org 0x4c1de-ORIGIN
P_0004c1de:
    .byte 0x24
    .org 0x4c1df-ORIGIN
P_0004c1df:
    .byte 0xce
    .org 0x4c1e0-ORIGIN
P_0004c1e0:
    .byte 0xff
    .org 0x4c1e1-ORIGIN
P_0004c1e1:
    .byte 0xff
    .org 0x4c1e2-ORIGIN
P_0004c1e2:
    .byte 0x12
    .org 0x4c1e3-ORIGIN
P_0004c1e3:
    .byte 0x0e
    .org 0x4e112-ORIGIN
L_0004e112:
    mov.l P_0004e1b0,r1
    .org 0x4e114-ORIGIN
L_0004e114:
    mov.l P_0004e1b4,r6
    .org 0x4e116-ORIGIN
L_0004e116:
    mov #0x1d,r0
    .org 0x4e118-ORIGIN
L_0004e118:
    mov.b @(r0,r6),r0
    .org 0x4e11a-ORIGIN
L_0004e11a:
    tst #0x10,r0
    .org 0x4e11c-ORIGIN
L_0004e11c:
    bt L_0004e156
    .org 0x4e11e-ORIGIN
L_0004e11e:
    mov.b @(0x2,r1),r0
    .org 0x4e120-ORIGIN
L_0004e120:
    tst r0,r0
    .org 0x4e122-ORIGIN
L_0004e122:
    bf L_0004e15e
    .org 0x4e124-ORIGIN
L_0004e124:
    mov.l P_0004e1b8,r5
    .org 0x4e126-ORIGIN
L_0004e126:
    mov.w P_0004e17c,r0
    .org 0x4e128-ORIGIN
L_0004e128:
    mov.b @(r0,r5),r6
    .org 0x4e12a-ORIGIN
L_0004e12a:
    exts.w r6,r2
    .org 0x4e12c-ORIGIN
L_0004e12c:
    cmp/pl r2
    .org 0x4e12e-ORIGIN
L_0004e12e:
    bf L_0004e134
    .org 0x4e130-ORIGIN
L_0004e130:
    bra L_0004e13a
    .org 0x4e132-ORIGIN
L_0004e132:
    add #-0x1,r2
    .org 0x4e134-ORIGIN
L_0004e134:
    cmp/pz r2
    .org 0x4e136-ORIGIN
L_0004e136:
    bt L_0004e13a
    .org 0x4e138-ORIGIN
L_0004e138:
    add #0x1,r2
    .org 0x4e13a-ORIGIN
L_0004e13a:
    exts.w r2,r2
    .org 0x4e13c-ORIGIN
L_0004e13c:
    mov #0x7f,r6
    .org 0x4e13e-ORIGIN
L_0004e13e:
    cmp/gt r6,r2
    .org 0x4e140-ORIGIN
L_0004e140:
    bf L_0004e146
    .org 0x4e142-ORIGIN
L_0004e142:
    bra L_0004e148
    .org 0x4e144-ORIGIN
L_0004e144:
    mov #0x7f,r6
    .org 0x4e146-ORIGIN
L_0004e146:
    exts.w r2,r6
    .org 0x4e148-ORIGIN
L_0004e148:
    exts.w r6,r2
    .org 0x4e14a-ORIGIN
L_0004e14a:
    mov #-0x80,r6
    .org 0x4e14c-ORIGIN
L_0004e14c:
    cmp/ge r6,r2
    .org 0x4e14e-ORIGIN
L_0004e14e:
    bt L_0004e152
    .org 0x4e150-ORIGIN
L_0004e150:
    mov #-0x80,r2
    .org 0x4e152-ORIGIN
L_0004e152:
    mov.w P_0004e17c,r0
    .org 0x4e154-ORIGIN
L_0004e154:
    mov.b r2,@(r0,r5)
    .org 0x4e156-ORIGIN
L_0004e156:
    mov.l P_0004e1bc,r6
    .org 0x4e158-ORIGIN
L_0004e158:
    mov.b @r6,r0
    .org 0x4e15a-ORIGIN
L_0004e15a:
    rts
    .org 0x4e15c-ORIGIN
L_0004e15c:
    mov.b r0,@(0x2,r1)
    .org 0x4e15e-ORIGIN
L_0004e15e:
    rts
    .org 0x4e160-ORIGIN
L_0004e160:
    nop
    .org 0x4e17c-ORIGIN
P_0004e17c:
    .byte 0x02
    .org 0x4e17d-ORIGIN
P_0004e17d:
    .byte 0x87
    .org 0x4e1b0-ORIGIN
P_0004e1b0:
    .byte 0xff
    .org 0x4e1b1-ORIGIN
P_0004e1b1:
    .byte 0xff
    .org 0x4e1b2-ORIGIN
P_0004e1b2:
    .byte 0x25
    .org 0x4e1b3-ORIGIN
P_0004e1b3:
    .byte 0xfb
    .org 0x4e1b4-ORIGIN
P_0004e1b4:
    .byte 0xff
    .org 0x4e1b5-ORIGIN
P_0004e1b5:
    .byte 0xff
    .org 0x4e1b6-ORIGIN
P_0004e1b6:
    .byte 0x24
    .org 0x4e1b7-ORIGIN
P_0004e1b7:
    .byte 0x70
    .org 0x4e1b8-ORIGIN
P_0004e1b8:
    .byte 0xff
    .org 0x4e1b9-ORIGIN
P_0004e1b9:
    .byte 0xff
    .org 0x4e1ba-ORIGIN
P_0004e1ba:
    .byte 0x12
    .org 0x4e1bb-ORIGIN
P_0004e1bb:
    .byte 0x8c
    .org 0x4e1bc-ORIGIN
P_0004e1bc:
    .byte 0x00
    .org 0x4e1bd-ORIGIN
P_0004e1bd:
    .byte 0x00
    .org 0x4e1be-ORIGIN
P_0004e1be:
    .byte 0x84
    .org 0x4e1bf-ORIGIN
P_0004e1bf:
    .byte 0x40
    .org 0x554ae-ORIGIN
L_000554ae:
    stc.l gbr,@-r15
    .org 0x554b0-ORIGIN
L_000554b0:
    mov.l P_000555ec,r0
    .org 0x554b2-ORIGIN
L_000554b2:
    ldc r0,gbr
    .org 0x554b4-ORIGIN
L_000554b4:
    mov.l P_000555c8,r1
    .org 0x554b6-ORIGIN
L_000554b6:
    mov #0x40,r6
    .org 0x554b8-ORIGIN
L_000554b8:
    mov.w P_000554f6,r0
    .org 0x554ba-ORIGIN
L_000554ba:
    shll 8 r6
    .org 0x554bc-ORIGIN
L_000554bc:
    mov.l @(r0,r1),r2
    .org 0x554be-ORIGIN
L_000554be:
    mov.w @(0x14,gbr),r0
    .org 0x554c0-ORIGIN
L_000554c0:
    add r6,r2
    .org 0x554c2-ORIGIN
L_000554c2:
    extu.w r0,r4
    .org 0x554c4-ORIGIN
L_000554c4:
    mov.w P_000554f4,r0
    .org 0x554c6-ORIGIN
L_000554c6:
    mov r2,r5
    .org 0x554c8-ORIGIN
L_000554c8:
    add r4,r2
    .org 0x554ca-ORIGIN
L_000554ca:
    mov.w @(r0,r1),r7
    .org 0x554cc-ORIGIN
L_000554cc:
    mov #-0x1,r6
    .org 0x554ce-ORIGIN
L_000554ce:
    extu.w r6,r6
    .org 0x554d0-ORIGIN
L_000554d0:
    extu.w r7,r7
    .org 0x554d2-ORIGIN
L_000554d2:
    add r7,r2
    .org 0x554d4-ORIGIN
L_000554d4:
    cmp/gt r6,r2
    .org 0x554d6-ORIGIN
L_000554d6:
    bf L_000554dc
    .org 0x554d8-ORIGIN
L_000554d8:
    bra L_000554e2
    .org 0x554da-ORIGIN
L_000554da:
    mov r6,r2
    .org 0x554dc-ORIGIN
L_000554dc:
    add r4,r5
    .org 0x554de-ORIGIN
L_000554de:
    add r7,r5
    .org 0x554e0-ORIGIN
L_000554e0:
    mov r5,r2
    .org 0x554e2-ORIGIN
L_000554e2:
    cmp/pz r2
    .org 0x554e4-ORIGIN
L_000554e4:
    bt L_000554e8
    .org 0x554e6-ORIGIN
L_000554e6:
    mov #0x0,r2
    .org 0x554e8-ORIGIN
L_000554e8:
    mov r2,r0
    .org 0x554ea-ORIGIN
L_000554ea:
    mov.w r0,@(0x22,gbr)
    .org 0x554ec-ORIGIN
L_000554ec:
    rts
    .org 0x554ee-ORIGIN
L_000554ee:
    ldc.l @r15+,gbr
    .org 0x554f4-ORIGIN
P_000554f4:
    .byte 0x03
    .org 0x554f5-ORIGIN
P_000554f5:
    .byte 0x4e
    .org 0x554f6-ORIGIN
P_000554f6:
    .byte 0x03
    .org 0x554f7-ORIGIN
P_000554f7:
    .byte 0x6c
    .org 0x555c8-ORIGIN
P_000555c8:
    .byte 0xff
    .org 0x555c9-ORIGIN
P_000555c9:
    .byte 0xff
    .org 0x555ca-ORIGIN
P_000555ca:
    .byte 0x12
    .org 0x555cb-ORIGIN
P_000555cb:
    .byte 0x8c
    .org 0x555ec-ORIGIN
P_000555ec:
    .byte 0xff
    .org 0x555ed-ORIGIN
P_000555ed:
    .byte 0xff
    .org 0x555ee-ORIGIN
P_000555ee:
    .byte 0x22
    .org 0x555ef-ORIGIN
P_000555ef:
    .byte 0xf8
    .org 0x70d82-ORIGIN
L_00070d82:
    stc.l gbr,@-r15
    .org 0x70d84-ORIGIN
L_00070d84:
    mov.l P_00070e30,r0
    .org 0x70d86-ORIGIN
L_00070d86:
    ldc r0,gbr
    .org 0x70d88-ORIGIN
L_00070d88:
    mov.b @(0xd4,gbr),r0
    .org 0x70d8a-ORIGIN
L_00070d8a:
    tst #0x2,r0
    .org 0x70d8c-ORIGIN
L_00070d8c:
    bf L_00070d94
    .org 0x70d8e-ORIGIN
L_00070d8e:
    mov.w @(0x7e,gbr),r0
    .org 0x70d90-ORIGIN
L_00070d90:
    bra L_00070db6
    .org 0x70d92-ORIGIN
L_00070d92:
    mov r0,r2
    .org 0x70d94-ORIGIN
L_00070d94:
    mov.l P_00070e34,r6
    .org 0x70d96-ORIGIN
L_00070d96:
    mov #0x6c,r0
    .org 0x70d98-ORIGIN
L_00070d98:
    mov.l P_00070e2c,r5
    .org 0x70d9a-ORIGIN
L_00070d9a:
    mov.b @(r0,r6),r2
    .org 0x70d9c-ORIGIN
L_00070d9c:
    mov.w P_00070e22,r0
    .org 0x70d9e-ORIGIN
L_00070d9e:
    tst r2,r2
    .org 0x70da0-ORIGIN
L_00070da0:
    bf/s L_00070db4
    .org 0x70da2-ORIGIN
L_00070da2:
    mov.w @(r0,r5),r2
    .org 0x70da4-ORIGIN
L_00070da4:
    mov.w @(0x7e,gbr),r0
    .org 0x70da6-ORIGIN
L_00070da6:
    cmp/gt r2,r0
    .org 0x70da8-ORIGIN
L_00070da8:
    bf/s L_00070dae
    .org 0x70daa-ORIGIN
L_00070daa:
    mov r0,r6
    .org 0x70dac-ORIGIN
L_00070dac:
    mov r2,r6
    .org 0x70dae-ORIGIN
L_00070dae:
    mov r6,r2
    .org 0x70db0-ORIGIN
L_00070db0:
    bra L_00070db6
    .org 0x70db2-ORIGIN
L_00070db2:
    mov r6,r0
    .org 0x70db4-ORIGIN
L_00070db4:
    mov r2,r0
    .org 0x70db6-ORIGIN
L_00070db6:
    mov.w r0,@(0x7c,gbr)
    .org 0x70db8-ORIGIN
L_00070db8:
    mov.l P_00070e2c,r5
    .org 0x70dba-ORIGIN
L_00070dba:
    mov.w P_00070e24,r0
    .org 0x70dbc-ORIGIN
L_00070dbc:
    mov.w r2,@(r0,r5)
    .org 0x70dbe-ORIGIN
L_00070dbe:
    rts
    .org 0x70dc0-ORIGIN
L_00070dc0:
    ldc.l @r15+,gbr
    .org 0x70e22-ORIGIN
P_00070e22:
    .byte 0x07
    .org 0x70e23-ORIGIN
P_00070e23:
    .byte 0x34
    .org 0x70e24-ORIGIN
P_00070e24:
    .byte 0x07
    .org 0x70e25-ORIGIN
P_00070e25:
    .byte 0x36
    .org 0x70e2c-ORIGIN
P_00070e2c:
    .byte 0xff
    .org 0x70e2d-ORIGIN
P_00070e2d:
    .byte 0xff
    .org 0x70e2e-ORIGIN
P_00070e2e:
    .byte 0x12
    .org 0x70e2f-ORIGIN
P_00070e2f:
    .byte 0x8c
    .org 0x70e30-ORIGIN
P_00070e30:
    .byte 0xff
    .org 0x70e31-ORIGIN
P_00070e31:
    .byte 0xff
    .org 0x70e32-ORIGIN
P_00070e32:
    .byte 0x23
    .org 0x70e33-ORIGIN
P_00070e33:
    .byte 0xbc
    .org 0x70e34-ORIGIN
P_00070e34:
    .byte 0xff
    .org 0x70e35-ORIGIN
P_00070e35:
    .byte 0xff
    .org 0x70e36-ORIGIN
P_00070e36:
    .byte 0x25
    .org 0x70e37-ORIGIN
P_00070e37:
    .byte 0x6a
    .org 0xa5530-ORIGIN
L_000a5530:
    mov.l P_000a5770,r4
    .org 0xa5532-ORIGIN
L_000a5532:
    mov #0x5b,r0
    .org 0xa5534-ORIGIN
L_000a5534:
    mov.b @(r0,r4),r5
    .org 0xa5536-ORIGIN
L_000a5536:
    mov r5,r0
    .org 0xa5538-ORIGIN
L_000a5538:
    tst #0x8,r0
    .org 0xa553a-ORIGIN
L_000a553a:
    bf L_000a555c
    .org 0xa553c-ORIGIN
L_000a553c:
    mov.l P_000a5774,r6
    .org 0xa553e-ORIGIN
L_000a553e:
    mov.b @r6,r0
    .org 0xa5540-ORIGIN
L_000a5540:
    tst #0x20,r0
    .org 0xa5542-ORIGIN
L_000a5542:
    bt L_000a555c
    .org 0xa5544-ORIGIN
L_000a5544:
    mov.l P_000a5778,r7
    .org 0xa5546-ORIGIN
L_000a5546:
    mov.w P_000a5650,r0
    .org 0xa5548-ORIGIN
L_000a5548:
    mov.w @(r0,r7),r6
    .org 0xa554a-ORIGIN
L_000a554a:
    mov.w P_000a5652,r0
    .org 0xa554c-ORIGIN
L_000a554c:
    mov.w @(r0,r7),r2
    .org 0xa554e-ORIGIN
L_000a554e:
    cmp/hi r2,r6
    .org 0xa5550-ORIGIN
L_000a5550:
    bf L_000a555c
    .org 0xa5552-ORIGIN
L_000a5552:
    mov #0x8,r0
    .org 0xa5554-ORIGIN
L_000a5554:
    or r0,r5
    .org 0xa5556-ORIGIN
L_000a5556:
    mov #0x5b,r0
    .org 0xa5558-ORIGIN
L_000a5558:
    rts
    .org 0xa555a-ORIGIN
L_000a555a:
    mov.b r5,@(r0,r4)
    .org 0xa555c-ORIGIN
L_000a555c:
    rts
    .org 0xa555e-ORIGIN
L_000a555e:
    nop
    .org 0xa5650-ORIGIN
P_000a5650:
    .byte 0x0a
    .org 0xa5651-ORIGIN
P_000a5651:
    .byte 0x3c
    .org 0xa5652-ORIGIN
P_000a5652:
    .byte 0x09
    .org 0xa5653-ORIGIN
P_000a5653:
    .byte 0xf6
    .org 0xa5770-ORIGIN
P_000a5770:
    .byte 0xff
    .org 0xa5771-ORIGIN
P_000a5771:
    .byte 0xff
    .org 0xa5772-ORIGIN
P_000a5772:
    .byte 0x41
    .org 0xa5773-ORIGIN
P_000a5773:
    .byte 0xa9
    .org 0xa5774-ORIGIN
P_000a5774:
    .byte 0xff
    .org 0xa5775-ORIGIN
P_000a5775:
    .byte 0xff
    .org 0xa5776-ORIGIN
P_000a5776:
    .byte 0x24
    .org 0xa5777-ORIGIN
P_000a5777:
    .byte 0x4f
    .org 0xa5778-ORIGIN
P_000a5778:
    .byte 0xff
    .org 0xa5779-ORIGIN
P_000a5779:
    .byte 0xff
    .org 0xa577a-ORIGIN
P_000a577a:
    .byte 0x28
    .org 0xa577b-ORIGIN
P_000a577b:
    .byte 0xf8
