! Exact disjoint natural RPM-state paths with selected native RAM-root absence.
    .text
    .balign 4
    .set ORIGIN,0x83d4
    .org 0x83d7-ORIGIN
P_000083d7:
    .byte 0x37
    .org 0x84d7-ORIGIN
P_000084d7:
    .byte 0x04
    .org 0x84db-ORIGIN
P_000084db:
    .byte 0x74
    .org 0x84dc-ORIGIN
P_000084dc:
    .byte 0x5c
    .org 0x84de-ORIGIN
P_000084de:
    .byte 0x0c
    .org 0x88a7-ORIGIN
P_000088a7:
    .byte 0x3c
    .org 0x88a8-ORIGIN
P_000088a8:
    .byte 0x55
    .org 0x88a9-ORIGIN
P_000088a9:
    .byte 0x6c
    .org 0x88aa-ORIGIN
P_000088aa:
    .byte 0x04
    .org 0x88ad-ORIGIN
P_000088ad:
    .byte 0x96
    .org 0x88ae-ORIGIN
P_000088ae:
    .byte 0x58
    .org 0x8b3f-ORIGIN
P_00008b3f:
    .byte 0x18
    .org 0x90e0-ORIGIN
P_000090e0:
    .byte 0x07
    .org 0x90e1-ORIGIN
P_000090e1:
    .byte 0xd0
    .org 0x4f7e0-ORIGIN
L_0004f7e0:
    sts.l macl,@-r15
    .org 0x4f7e2-ORIGIN
L_0004f7e2:
    mov.l P_0004f91c,r6
    .org 0x4f7e4-ORIGIN
L_0004f7e4:
    mov.b @r6,r0
    .org 0x4f7e6-ORIGIN
L_0004f7e6:
    tst #0x80,r0
    .org 0x4f7e8-ORIGIN
L_0004f7e8:
    bt L_0004f7ee
    .org 0x4f7ea-ORIGIN
L_0004f7ea:
    bra L_0004f902
    .org 0x4f7ec-ORIGIN
L_0004f7ec:
    nop
    .org 0x4f7ee-ORIGIN
L_0004f7ee:
    mov.l P_0004f940,r2
    .org 0x4f7f0-ORIGIN
L_0004f7f0:
    mov #-0x1,r6
    .org 0x4f7f2-ORIGIN
L_0004f7f2:
    mov.l P_0004f944,r4
    .org 0x4f7f4-ORIGIN
L_0004f7f4:
    extu.w r6,r6
    .org 0x4f7f6-ORIGIN
L_0004f7f6:
    mov.w @r2,r5
    .org 0x4f7f8-ORIGIN
L_0004f7f8:
    mov.b @(0x7,r4),r0
    .org 0x4f7fa-ORIGIN
L_0004f7fa:
    extu.w r5,r5
    .org 0x4f7fc-ORIGIN
L_0004f7fc:
    extu.b r0,r4
    .org 0x4f7fe-ORIGIN
L_0004f7fe:
    mul.l r5,r4
    .org 0x4f800-ORIGIN
L_0004f800:
    sts macl,r2
    .org 0x4f802-ORIGIN
L_0004f802:
    cmp/gt r6,r2
    .org 0x4f804-ORIGIN
L_0004f804:
    bf L_0004f80a
    .org 0x4f806-ORIGIN
L_0004f806:
    bra L_0004f814
    .org 0x4f808-ORIGIN
L_0004f808:
    mov r6,r2
    .org 0x4f80a-ORIGIN
L_0004f80a:
    mov.l P_0004f944,r3
    .org 0x4f80c-ORIGIN
L_0004f80c:
    mov.b @(0x7,r3),r0
    .org 0x4f80e-ORIGIN
L_0004f80e:
    extu.b r0,r6
    .org 0x4f810-ORIGIN
L_0004f810:
    mul.l r5,r6
    .org 0x4f812-ORIGIN
L_0004f812:
    sts macl,r2
    .org 0x4f814-ORIGIN
L_0004f814:
    mov.l P_0004f948,r6
    .org 0x4f816-ORIGIN
L_0004f816:
    mov.b @(0xc,r6),r0
    .org 0x4f818-ORIGIN
L_0004f818:
    tst #0x20,r0
    .org 0x4f81a-ORIGIN
L_0004f81a:
    bf/s L_0004f82c
    .org 0x4f81c-ORIGIN
L_0004f81c:
    extu.w r2,r4
    .org 0x4f81e-ORIGIN
L_0004f81e:
    mov.l P_0004f92c,r2
    .org 0x4f820-ORIGIN
L_0004f820:
    mov.w P_0004f8d4,r0
    .org 0x4f822-ORIGIN
L_0004f822:
    mov.w @(r0,r2),r6
    .org 0x4f824-ORIGIN
L_0004f824:
    extu.w r6,r6
    .org 0x4f826-ORIGIN
L_0004f826:
    cmp/ge r4,r6
    .org 0x4f828-ORIGIN
L_0004f828:
    bt/s L_0004f82e
    .org 0x4f82a-ORIGIN
L_0004f82a:
    mov #0x0,r5
    .org 0x4f82c-ORIGIN
L_0004f82c:
    mov #0x1,r5
    .org 0x4f82e-ORIGIN
L_0004f82e:
    mov.l P_0004f948,r6
    .org 0x4f830-ORIGIN
L_0004f830:
    mov.b @(0x3,r6),r0
    .org 0x4f832-ORIGIN
L_0004f832:
    tst #0x4,r0
    .org 0x4f834-ORIGIN
L_0004f834:
    bf L_0004f8fa
    .org 0x4f836-ORIGIN
L_0004f836:
    mov.l P_0004f94c,r6
    .org 0x4f838-ORIGIN
L_0004f838:
    mov.b @(0x4,r6),r0
    .org 0x4f83a-ORIGIN
L_0004f83a:
    tst #0x40,r0
    .org 0x4f83c-ORIGIN
L_0004f83c:
    bf L_0004f8e8
    .org 0x4f83e-ORIGIN
L_0004f83e:
    mov.l P_0004f950,r6
    .org 0x4f840-ORIGIN
L_0004f840:
    mov.b @r6,r0
    .org 0x4f842-ORIGIN
L_0004f842:
    tst #0x1,r0
    .org 0x4f844-ORIGIN
L_0004f844:
    bt L_0004f84e
    .org 0x4f846-ORIGIN
L_0004f846:
    mov.l P_0004f954,r6
    .org 0x4f848-ORIGIN
L_0004f848:
    mov.b @(0x1,r6),r0
    .org 0x4f84a-ORIGIN
L_0004f84a:
    tst #0x20,r0
    .org 0x4f84c-ORIGIN
L_0004f84c:
    bf L_0004f8d6
    .org 0x4f84e-ORIGIN
L_0004f84e:
    mov.l P_0004f918,r6
    .org 0x4f850-ORIGIN
L_0004f850:
    mov #0x2b,r0
    .org 0x4f852-ORIGIN
L_0004f852:
    mov.b @(r0,r6),r0
    .org 0x4f854-ORIGIN
L_0004f854:
    tst #0x1,r0
    .org 0x4f856-ORIGIN
L_0004f856:
    bf L_0004f8d6
    .org 0x4f858-ORIGIN
L_0004f858:
    mov.l P_0004f934,r2
    .org 0x4f85a-ORIGIN
L_0004f85a:
    mov #0x7a,r0
    .org 0x4f85c-ORIGIN
L_0004f85c:
    mov.l P_0004f944,r3
    .org 0x4f85e-ORIGIN
L_0004f85e:
    mov.b @(r0,r2),r6
    .org 0x4f860-ORIGIN
L_0004f860:
    mov.b @r3,r2
    .org 0x4f862-ORIGIN
L_0004f862:
    cmp/hi r2,r6
    .org 0x4f864-ORIGIN
L_0004f864:
    bt L_0004f8ac
    .org 0x4f866-ORIGIN
L_0004f866:
    mov.l P_0004f914,r2
    .org 0x4f868-ORIGIN
L_0004f868:
    mov #0x17,r0
    .org 0x4f86a-ORIGIN
L_0004f86a:
    mov.l P_0004f944,r3
    .org 0x4f86c-ORIGIN
L_0004f86c:
    mov.b @(r0,r2),r7
    .org 0x4f86e-ORIGIN
L_0004f86e:
    mov.b @(0x5,r3),r0
    .org 0x4f870-ORIGIN
L_0004f870:
    extu.b r7,r7
    .org 0x4f872-ORIGIN
L_0004f872:
    extu.b r0,r2
    .org 0x4f874-ORIGIN
L_0004f874:
    cmp/ge r2,r7
    .org 0x4f876-ORIGIN
L_0004f876:
    bf L_0004f8ac
    .org 0x4f878-ORIGIN
L_0004f878:
    mov.l P_0004f944,r3
    .org 0x4f87a-ORIGIN
L_0004f87a:
    mov.b @(0x4,r3),r0
    .org 0x4f87c-ORIGIN
L_0004f87c:
    extu.b r0,r2
    .org 0x4f87e-ORIGIN
L_0004f87e:
    cmp/gt r2,r7
    .org 0x4f880-ORIGIN
L_0004f880:
    bt L_0004f8ac
    .org 0x4f882-ORIGIN
L_0004f882:
    mov.l P_0004f92c,r2
    .org 0x4f884-ORIGIN
L_0004f884:
    mov.w P_0004f8d4,r0
    .org 0x4f886-ORIGIN
L_0004f886:
    mov.l P_0004f944,r3
    .org 0x4f888-ORIGIN
L_0004f888:
    mov.w @(r0,r2),r7
    .org 0x4f88a-ORIGIN
L_0004f88a:
    mov.b @(0x7,r3),r0
    .org 0x4f88c-ORIGIN
L_0004f88c:
    extu.w r7,r7
    .org 0x4f88e-ORIGIN
L_0004f88e:
    extu.b r0,r6
    .org 0x4f890-ORIGIN
L_0004f890:
    mov r7,r2
    .org 0x4f892-ORIGIN
L_0004f892:
    add r6,r2
    .org 0x4f894-ORIGIN
L_0004f894:
    cmp/gt r4,r2
    .org 0x4f896-ORIGIN
L_0004f896:
    bt L_0004f8a2
    .org 0x4f898-ORIGIN
L_0004f898:
    mov.l P_0004f944,r3
    .org 0x4f89a-ORIGIN
L_0004f89a:
    mov.b @(0x7,r3),r0
    .org 0x4f89c-ORIGIN
L_0004f89c:
    extu.b r0,r5
    .org 0x4f89e-ORIGIN
L_0004f89e:
    add r5,r7
    .org 0x4f8a0-ORIGIN
L_0004f8a0:
    mov r7,r4
    .org 0x4f8a2-ORIGIN
L_0004f8a2:
    mov.l P_0004f92c,r3
    .org 0x4f8a4-ORIGIN
L_0004f8a4:
    mov.w P_0004f8d4,r0
    .org 0x4f8a6-ORIGIN
L_0004f8a6:
    mov.w r4,@(r0,r3)
    .org 0x4f8a8-ORIGIN
L_0004f8a8:
    bra L_0004f902
    .org 0x4f8aa-ORIGIN
L_0004f8aa:
    nop
    .org 0x4f8ac-ORIGIN
L_0004f8ac:
    extu.b r5,r0
    .org 0x4f8ae-ORIGIN
L_0004f8ae:
    cmp/eq #0x1,r0
    .org 0x4f8b0-ORIGIN
L_0004f8b0:
    bf L_0004f902
    .org 0x4f8b2-ORIGIN
L_0004f8b2:
    mov.l P_0004f92c,r2
    .org 0x4f8b4-ORIGIN
L_0004f8b4:
    mov.w P_0004f8d4,r0
    .org 0x4f8b6-ORIGIN
L_0004f8b6:
    mov.w @(r0,r2),r6
    .org 0x4f8b8-ORIGIN
L_0004f8b8:
    extu.w r6,r6
    .org 0x4f8ba-ORIGIN
L_0004f8ba:
    mov r6,r2
    .org 0x4f8bc-ORIGIN
L_0004f8bc:
    add #-0x1,r2
    .org 0x4f8be-ORIGIN
L_0004f8be:
    cmp/pz r2
    .org 0x4f8c0-ORIGIN
L_0004f8c0:
    bt L_0004f8c6
    .org 0x4f8c2-ORIGIN
L_0004f8c2:
    bra L_0004f8ca
    .org 0x4f8c4-ORIGIN
L_0004f8c4:
    mov #0x0,r2
    .org 0x4f8c6-ORIGIN
L_0004f8c6:
    add #-0x1,r6
    .org 0x4f8c8-ORIGIN
L_0004f8c8:
    mov r6,r2
    .org 0x4f8ca-ORIGIN
L_0004f8ca:
    mov.l P_0004f92c,r3
    .org 0x4f8cc-ORIGIN
L_0004f8cc:
    mov.w P_0004f8d4,r0
    .org 0x4f8ce-ORIGIN
L_0004f8ce:
    mov.w r2,@(r0,r3)
    .org 0x4f8d0-ORIGIN
L_0004f8d0:
    bra L_0004f902
    .org 0x4f8d2-ORIGIN
L_0004f8d2:
    nop
    .org 0x4f8d4-ORIGIN
P_0004f8d4:
    .byte 0x06
    .org 0x4f8d5-ORIGIN
P_0004f8d5:
    .byte 0xa6
    .org 0x4f8d6-ORIGIN
L_0004f8d6:
    extu.b r5,r0
    .org 0x4f8d8-ORIGIN
L_0004f8d8:
    cmp/eq #0x1,r0
    .org 0x4f8da-ORIGIN
L_0004f8da:
    bf L_0004f902
    .org 0x4f8dc-ORIGIN
L_0004f8dc:
    mov.l P_0004f92c,r3
    .org 0x4f8de-ORIGIN
L_0004f8de:
    mov #0x0,r2
    .org 0x4f8e0-ORIGIN
L_0004f8e0:
    mov.w P_0004f906,r0
    .org 0x4f8e2-ORIGIN
L_0004f8e2:
    mov.w r2,@(r0,r3)
    .org 0x4f8e4-ORIGIN
L_0004f8e4:
    bra L_0004f902
    .org 0x4f8e6-ORIGIN
L_0004f8e6:
    nop
    .org 0x4f8e8-ORIGIN
L_0004f8e8:
    extu.b r5,r0
    .org 0x4f8ea-ORIGIN
L_0004f8ea:
    cmp/eq #0x1,r0
    .org 0x4f8ec-ORIGIN
L_0004f8ec:
    bf L_0004f902
    .org 0x4f8ee-ORIGIN
L_0004f8ee:
    mov.l P_0004f92c,r3
    .org 0x4f8f0-ORIGIN
L_0004f8f0:
    mov #0x0,r2
    .org 0x4f8f2-ORIGIN
L_0004f8f2:
    mov.w P_0004f906,r0
    .org 0x4f8f4-ORIGIN
L_0004f8f4:
    mov.w r2,@(r0,r3)
    .org 0x4f8f6-ORIGIN
L_0004f8f6:
    bra L_0004f902
    .org 0x4f8f8-ORIGIN
L_0004f8f8:
    nop
    .org 0x4f8fa-ORIGIN
L_0004f8fa:
    mov.l P_0004f92c,r3
    .org 0x4f8fc-ORIGIN
L_0004f8fc:
    mov #0x0,r2
    .org 0x4f8fe-ORIGIN
L_0004f8fe:
    mov.w P_0004f906,r0
    .org 0x4f900-ORIGIN
L_0004f900:
    mov.w r2,@(r0,r3)
    .org 0x4f902-ORIGIN
L_0004f902:
    rts
    .org 0x4f904-ORIGIN
L_0004f904:
    lds.l @r15+,macl
    .org 0x4f906-ORIGIN
P_0004f906:
    .byte 0x06
    .org 0x4f907-ORIGIN
P_0004f907:
    .byte 0xa6
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
    .org 0x4f918-ORIGIN
P_0004f918:
    .byte 0xff
    .org 0x4f919-ORIGIN
P_0004f919:
    .byte 0xff
    .org 0x4f91a-ORIGIN
P_0004f91a:
    .byte 0x41
    .org 0x4f91b-ORIGIN
P_0004f91b:
    .byte 0xa9
    .org 0x4f91c-ORIGIN
P_0004f91c:
    .byte 0x00
    .org 0x4f91d-ORIGIN
P_0004f91d:
    .byte 0x00
    .org 0x4f91e-ORIGIN
P_0004f91e:
    .byte 0x8b
    .org 0x4f91f-ORIGIN
P_0004f91f:
    .byte 0x3f
    .org 0x4f92c-ORIGIN
P_0004f92c:
    .byte 0xff
    .org 0x4f92d-ORIGIN
P_0004f92d:
    .byte 0xff
    .org 0x4f92e-ORIGIN
P_0004f92e:
    .byte 0x12
    .org 0x4f92f-ORIGIN
P_0004f92f:
    .byte 0x8c
    .org 0x4f934-ORIGIN
P_0004f934:
    .byte 0xff
    .org 0x4f935-ORIGIN
P_0004f935:
    .byte 0xff
    .org 0x4f936-ORIGIN
P_0004f936:
    .byte 0x10
    .org 0x4f937-ORIGIN
P_0004f937:
    .byte 0x94
    .org 0x4f940-ORIGIN
P_0004f940:
    .byte 0x00
    .org 0x4f941-ORIGIN
P_0004f941:
    .byte 0x00
    .org 0x4f942-ORIGIN
P_0004f942:
    .byte 0x90
    .org 0x4f943-ORIGIN
P_0004f943:
    .byte 0xe0
    .org 0x4f944-ORIGIN
P_0004f944:
    .byte 0x00
    .org 0x4f945-ORIGIN
P_0004f945:
    .byte 0x00
    .org 0x4f946-ORIGIN
P_0004f946:
    .byte 0x84
    .org 0x4f947-ORIGIN
P_0004f947:
    .byte 0xd7
    .org 0x4f948-ORIGIN
P_0004f948:
    .byte 0xff
    .org 0x4f949-ORIGIN
P_0004f949:
    .byte 0xff
    .org 0x4f94a-ORIGIN
P_0004f94a:
    .byte 0x24
    .org 0x4f94b-ORIGIN
P_0004f94b:
    .byte 0x4c
    .org 0x4f94c-ORIGIN
P_0004f94c:
    .byte 0xff
    .org 0x4f94d-ORIGIN
P_0004f94d:
    .byte 0xff
    .org 0x4f94e-ORIGIN
P_0004f94e:
    .byte 0x42
    .org 0x4f94f-ORIGIN
P_0004f94f:
    .byte 0x4c
    .org 0x4f950-ORIGIN
P_0004f950:
    .byte 0x00
    .org 0x4f951-ORIGIN
P_0004f951:
    .byte 0x00
    .org 0x4f952-ORIGIN
P_0004f952:
    .byte 0x83
    .org 0x4f953-ORIGIN
P_0004f953:
    .byte 0xd7
    .org 0x4f954-ORIGIN
P_0004f954:
    .byte 0xff
    .org 0x4f955-ORIGIN
P_0004f955:
    .byte 0xff
    .org 0x4f956-ORIGIN
P_0004f956:
    .byte 0x24
    .org 0x4f957-ORIGIN
P_0004f957:
    .byte 0xce
    .org 0x4f9c4-ORIGIN
L_0004f9c4:
    stc.l gbr,@-r15
    .org 0x4f9c6-ORIGIN
L_0004f9c6:
    mov.l P_0004fb88,r0
    .org 0x4f9c8-ORIGIN
L_0004f9c8:
    ldc r0,gbr
    .org 0x4f9ca-ORIGIN
L_0004f9ca:
    mov.b @(0x4b,gbr),r0
    .org 0x4f9cc-ORIGIN
L_0004f9cc:
    mov.l P_0004fb74,r6
    .org 0x4f9ce-ORIGIN
L_0004f9ce:
    mov r0,r1
    .org 0x4f9d0-ORIGIN
L_0004f9d0:
    mov.b @r6,r0
    .org 0x4f9d2-ORIGIN
L_0004f9d2:
    tst #0x80,r0
    .org 0x4f9d4-ORIGIN
L_0004f9d4:
    bf L_0004fa88
    .org 0x4f9d6-ORIGIN
L_0004f9d6:
    mov.b @(0x3,gbr),r0
    .org 0x4f9d8-ORIGIN
L_0004f9d8:
    tst #0x4,r0
    .org 0x4f9da-ORIGIN
L_0004f9da:
    bt L_0004f9e0
    .org 0x4f9dc-ORIGIN
L_0004f9dc:
    bra L_0004f9e8
    .org 0x4f9de-ORIGIN
L_0004f9de:
    mov #-0x1,r5
    .org 0x4f9e0-ORIGIN
L_0004f9e0:
    mov.b @(0x7,gbr),r0
    .org 0x4f9e2-ORIGIN
L_0004f9e2:
    tst #0x4,r0
    .org 0x4f9e4-ORIGIN
L_0004f9e4:
    bt L_0004f9f0
    .org 0x4f9e6-ORIGIN
L_0004f9e6:
    mov #0x0,r5
    .org 0x4f9e8-ORIGIN
L_0004f9e8:
    mov.l P_0004fb80,r7
    .org 0x4f9ea-ORIGIN
L_0004f9ea:
    mov.w P_0004fa9e,r0
    .org 0x4f9ec-ORIGIN
L_0004f9ec:
    bra L_0004fa12
    .org 0x4f9ee-ORIGIN
L_0004f9ee:
    mov.b r5,@(r0,r7)
    .org 0x4f9f0-ORIGIN
L_0004f9f0:
    mov.l P_0004fb80,r7
    .org 0x4f9f2-ORIGIN
L_0004f9f2:
    mov #-0x1,r5
    .org 0x4f9f4-ORIGIN
L_0004f9f4:
    mov.w P_0004fa9e,r0
    .org 0x4f9f6-ORIGIN
L_0004f9f6:
    extu.b r5,r5
    .org 0x4f9f8-ORIGIN
L_0004f9f8:
    mov.b @(r0,r7),r6
    .org 0x4f9fa-ORIGIN
L_0004f9fa:
    extu.b r6,r6
    .org 0x4f9fc-ORIGIN
L_0004f9fc:
    mov r6,r2
    .org 0x4f9fe-ORIGIN
L_0004f9fe:
    add #0x1,r2
    .org 0x4fa00-ORIGIN
L_0004fa00:
    cmp/gt r5,r2
    .org 0x4fa02-ORIGIN
L_0004fa02:
    bf L_0004fa08
    .org 0x4fa04-ORIGIN
L_0004fa04:
    bra L_0004fa0c
    .org 0x4fa06-ORIGIN
L_0004fa06:
    mov r5,r2
    .org 0x4fa08-ORIGIN
L_0004fa08:
    add #0x1,r6
    .org 0x4fa0a-ORIGIN
L_0004fa0a:
    mov r6,r2
    .org 0x4fa0c-ORIGIN
L_0004fa0c:
    mov.w P_0004fa9e,r0
    .org 0x4fa0e-ORIGIN
L_0004fa0e:
    mov r2,r5
    .org 0x4fa10-ORIGIN
L_0004fa10:
    mov.b r2,@(r0,r7)
    .org 0x4fa12-ORIGIN
L_0004fa12:
    mov r1,r0
    .org 0x4fa14-ORIGIN
L_0004fa14:
    tst #0x80,r0
    .org 0x4fa16-ORIGIN
L_0004fa16:
    bt L_0004fa40
    .org 0x4fa18-ORIGIN
L_0004fa18:
    mov.l P_0004fb84,r2
    .org 0x4fa1a-ORIGIN
L_0004fa1a:
    mov #0x17,r0
    .org 0x4fa1c-ORIGIN
L_0004fa1c:
    mov.l P_0004fb8c,r4
    .org 0x4fa1e-ORIGIN
L_0004fa1e:
    mov.b @(r0,r2),r6
    .org 0x4fa20-ORIGIN
L_0004fa20:
    mov.b @(0x7,r4),r0
    .org 0x4fa22-ORIGIN
L_0004fa22:
    cmp/hs r0,r6
    .org 0x4fa24-ORIGIN
L_0004fa24:
    bf L_0004fa30
    .org 0x4fa26-ORIGIN
L_0004fa26:
    mov.b @(0x6,r4),r0
    .org 0x4fa28-ORIGIN
L_0004fa28:
    extu.b r5,r5
    .org 0x4fa2a-ORIGIN
L_0004fa2a:
    extu.b r0,r2
    .org 0x4fa2c-ORIGIN
L_0004fa2c:
    cmp/ge r2,r5
    .org 0x4fa2e-ORIGIN
L_0004fa2e:
    bf L_0004fa40
    .org 0x4fa30-ORIGIN
L_0004fa30:
    mov r1,r0
    .org 0x4fa32-ORIGIN
L_0004fa32:
    and #0x7f,r0
    .org 0x4fa34-ORIGIN
L_0004fa34:
    mov.b r0,@(0x4b,gbr)
    .org 0x4fa36-ORIGIN
L_0004fa36:
    mov #-0x1,r2
    .org 0x4fa38-ORIGIN
L_0004fa38:
    mov.l P_0004fb80,r7
    .org 0x4fa3a-ORIGIN
L_0004fa3a:
    mov.w P_0004fa9e,r0
    .org 0x4fa3c-ORIGIN
L_0004fa3c:
    bra L_0004fa8e
    .org 0x4fa3e-ORIGIN
L_0004fa3e:
    mov.b r2,@(r0,r7)
    .org 0x4fa40-ORIGIN
L_0004fa40:
    mov.b @(0x11,gbr),r0
    .org 0x4fa42-ORIGIN
L_0004fa42:
    tst #0x40,r0
    .org 0x4fa44-ORIGIN
L_0004fa44:
    bf L_0004fa8e
    .org 0x4fa46-ORIGIN
L_0004fa46:
    mov.l P_0004fb90,r6
    .org 0x4fa48-ORIGIN
L_0004fa48:
    mov #0x2b,r0
    .org 0x4fa4a-ORIGIN
L_0004fa4a:
    mov.b @(r0,r6),r0
    .org 0x4fa4c-ORIGIN
L_0004fa4c:
    tst #0x1,r0
    .org 0x4fa4e-ORIGIN
L_0004fa4e:
    bf L_0004fa8e
    .org 0x4fa50-ORIGIN
L_0004fa50:
    mov.l P_0004fb84,r2
    .org 0x4fa52-ORIGIN
L_0004fa52:
    mov #0x17,r0
    .org 0x4fa54-ORIGIN
L_0004fa54:
    mov.l P_0004fb8c,r4
    .org 0x4fa56-ORIGIN
L_0004fa56:
    mov.b @(r0,r2),r6
    .org 0x4fa58-ORIGIN
L_0004fa58:
    mov.b @(0x2,r4),r0
    .org 0x4fa5a-ORIGIN
L_0004fa5a:
    cmp/hs r0,r6
    .org 0x4fa5c-ORIGIN
L_0004fa5c:
    bf L_0004fa8e
    .org 0x4fa5e-ORIGIN
L_0004fa5e:
    mov.l P_0004fb94,r2
    .org 0x4fa60-ORIGIN
L_0004fa60:
    mov.b @(0x9,r2),r0
    .org 0x4fa62-ORIGIN
L_0004fa62:
    mov r0,r6
    .org 0x4fa64-ORIGIN
L_0004fa64:
    mov.b @(0x1,r4),r0
    .org 0x4fa66-ORIGIN
L_0004fa66:
    cmp/hs r0,r6
    .org 0x4fa68-ORIGIN
L_0004fa68:
    bf L_0004fa8e
    .org 0x4fa6a-ORIGIN
L_0004fa6a:
    mov.l P_0004fb98,r2
    .org 0x4fa6c-ORIGIN
L_0004fa6c:
    mov #0x7a,r0
    .org 0x4fa6e-ORIGIN
L_0004fa6e:
    mov.b @(r0,r2),r6
    .org 0x4fa70-ORIGIN
L_0004fa70:
    mov.b @(0x3,r4),r0
    .org 0x4fa72-ORIGIN
L_0004fa72:
    cmp/hi r0,r6
    .org 0x4fa74-ORIGIN
L_0004fa74:
    bt L_0004fa8e
    .org 0x4fa76-ORIGIN
L_0004fa76:
    mov.l P_0004fb80,r7
    .org 0x4fa78-ORIGIN
L_0004fa78:
    mov.w P_0004fa9e,r0
    .org 0x4fa7a-ORIGIN
L_0004fa7a:
    mov.b @r4,r2
    .org 0x4fa7c-ORIGIN
L_0004fa7c:
    mov.b @(r0,r7),r5
    .org 0x4fa7e-ORIGIN
L_0004fa7e:
    cmp/hs r2,r5
    .org 0x4fa80-ORIGIN
L_0004fa80:
    bt L_0004fa8e
    .org 0x4fa82-ORIGIN
L_0004fa82:
    mov r1,r0
    .org 0x4fa84-ORIGIN
L_0004fa84:
    bra L_0004fa8c
    .org 0x4fa86-ORIGIN
L_0004fa86:
    or #0x80,r0
    .org 0x4fa88-ORIGIN
L_0004fa88:
    mov r1,r0
    .org 0x4fa8a-ORIGIN
L_0004fa8a:
    and #0x7f,r0
    .org 0x4fa8c-ORIGIN
L_0004fa8c:
    mov.b r0,@(0x4b,gbr)
    .org 0x4fa8e-ORIGIN
L_0004fa8e:
    mov.b @(0x4b,gbr),r0
    .org 0x4fa90-ORIGIN
L_0004fa90:
    tst #0x80,r0
    .org 0x4fa92-ORIGIN
L_0004fa92:
    movt r0
    .org 0x4fa94-ORIGIN
L_0004fa94:
    xor #0x1,r0
    .org 0x4fa96-ORIGIN
L_0004fa96:
    extu.b r0,r0
    .org 0x4fa98-ORIGIN
L_0004fa98:
    rts
    .org 0x4fa9a-ORIGIN
L_0004fa9a:
    ldc.l @r15+,gbr
    .org 0x4fa9e-ORIGIN
P_0004fa9e:
    .byte 0x04
    .org 0x4fa9f-ORIGIN
P_0004fa9f:
    .byte 0x04
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
    .org 0x4fb88-ORIGIN
P_0004fb88:
    .byte 0xff
    .org 0x4fb89-ORIGIN
P_0004fb89:
    .byte 0xff
    .org 0x4fb8a-ORIGIN
P_0004fb8a:
    .byte 0x24
    .org 0x4fb8b-ORIGIN
P_0004fb8b:
    .byte 0x4c
    .org 0x4fb8c-ORIGIN
P_0004fb8c:
    .byte 0x00
    .org 0x4fb8d-ORIGIN
P_0004fb8d:
    .byte 0x00
    .org 0x4fb8e-ORIGIN
P_0004fb8e:
    .byte 0x88
    .org 0x4fb8f-ORIGIN
P_0004fb8f:
    .byte 0xa7
    .org 0x4fb90-ORIGIN
P_0004fb90:
    .byte 0xff
    .org 0x4fb91-ORIGIN
P_0004fb91:
    .byte 0xff
    .org 0x4fb92-ORIGIN
P_0004fb92:
    .byte 0x41
    .org 0x4fb93-ORIGIN
P_0004fb93:
    .byte 0xa9
    .org 0x4fb94-ORIGIN
P_0004fb94:
    .byte 0xff
    .org 0x4fb95-ORIGIN
P_0004fb95:
    .byte 0xff
    .org 0x4fb96-ORIGIN
P_0004fb96:
    .byte 0x10
    .org 0x4fb97-ORIGIN
P_0004fb97:
    .byte 0x68
    .org 0x4fb98-ORIGIN
P_0004fb98:
    .byte 0xff
    .org 0x4fb99-ORIGIN
P_0004fb99:
    .byte 0xff
    .org 0x4fb9a-ORIGIN
P_0004fb9a:
    .byte 0x10
    .org 0x4fb9b-ORIGIN
P_0004fb9b:
    .byte 0x94
