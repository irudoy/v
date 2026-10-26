! Complete stock diagnostic reset, both natural callees and immutable signed native pools.
    .text
    .balign 4
    .set ORIGIN,0x2e76c
    .org 0x2e76e-ORIGIN
L_0002e76e:
    mov.w P_0002e780,r1
    .org 0x2e770-ORIGIN
L_0002e770:
    mov #0x0,r6
    .org 0x2e772-ORIGIN
L_0002e772:
    mov r6,r7
    .org 0x2e774-ORIGIN
L_0002e774:
    mov #0x4,r4
    .org 0x2e776-ORIGIN
L_0002e776:
    mov r1,r5
    .org 0x2e778-ORIGIN
L_0002e778:
    add #0x1,r6
    .org 0x2e77a-ORIGIN
L_0002e77a:
    mov.b r7,@r5
    .org 0x2e77c-ORIGIN
L_0002e77c:
    bra L_0002e782
    .org 0x2e77e-ORIGIN
L_0002e77e:
    extu.b r6,r6
    .org 0x2e780-ORIGIN
P_0002e780:
    .word 0x99c4
    .org 0x2e782-ORIGIN
L_0002e782:
    cmp/hs r4,r6
    .org 0x2e784-ORIGIN
L_0002e784:
    bf/s L_0002e778
    .org 0x2e786-ORIGIN
L_0002e786:
    add #0x1,r5
    .org 0x2e788-ORIGIN
L_0002e788:
    mov r1,r5
    .org 0x2e78a-ORIGIN
L_0002e78a:
    add #0x4,r5
    .org 0x2e78c-ORIGIN
L_0002e78c:
    mov #0x0,r6
    .org 0x2e78e-ORIGIN
L_0002e78e:
    add #0x1,r6
    .org 0x2e790-ORIGIN
L_0002e790:
    mov.b r7,@r5
    .org 0x2e792-ORIGIN
L_0002e792:
    extu.b r6,r6
    .org 0x2e794-ORIGIN
L_0002e794:
    cmp/hs r4,r6
    .org 0x2e796-ORIGIN
L_0002e796:
    bf/s L_0002e78e
    .org 0x2e798-ORIGIN
L_0002e798:
    add #0x1,r5
    .org 0x2e79a-ORIGIN
L_0002e79a:
    mov r1,r5
    .org 0x2e79c-ORIGIN
L_0002e79c:
    add #0x8,r5
    .org 0x2e79e-ORIGIN
L_0002e79e:
    mov #0x0,r6
    .org 0x2e7a0-ORIGIN
L_0002e7a0:
    add #0x1,r6
    .org 0x2e7a2-ORIGIN
L_0002e7a2:
    mov.b r7,@r5
    .org 0x2e7a4-ORIGIN
L_0002e7a4:
    extu.b r6,r6
    .org 0x2e7a6-ORIGIN
L_0002e7a6:
    cmp/hs r4,r6
    .org 0x2e7a8-ORIGIN
L_0002e7a8:
    bf/s L_0002e7a0
    .org 0x2e7aa-ORIGIN
L_0002e7aa:
    add #0x1,r5
    .org 0x2e7ac-ORIGIN
L_0002e7ac:
    mov r1,r5
    .org 0x2e7ae-ORIGIN
L_0002e7ae:
    add #0xc,r5
    .org 0x2e7b0-ORIGIN
L_0002e7b0:
    mov #0x0,r6
    .org 0x2e7b2-ORIGIN
L_0002e7b2:
    add #0x1,r6
    .org 0x2e7b4-ORIGIN
L_0002e7b4:
    mov.b r7,@r5
    .org 0x2e7b6-ORIGIN
L_0002e7b6:
    extu.b r6,r6
    .org 0x2e7b8-ORIGIN
L_0002e7b8:
    cmp/hs r4,r6
    .org 0x2e7ba-ORIGIN
L_0002e7ba:
    bf/s L_0002e7b2
    .org 0x2e7bc-ORIGIN
L_0002e7bc:
    add #0x1,r5
    .org 0x2e7be-ORIGIN
L_0002e7be:
    mov.w P_0002e8be,r5
    .org 0x2e7c0-ORIGIN
L_0002e7c0:
    mov #0x0,r6
    .org 0x2e7c2-ORIGIN
L_0002e7c2:
    mov #0x20,r4
    .org 0x2e7c4-ORIGIN
L_0002e7c4:
    add #0x1,r6
    .org 0x2e7c6-ORIGIN
L_0002e7c6:
    mov.b r7,@r5
    .org 0x2e7c8-ORIGIN
L_0002e7c8:
    extu.b r6,r6
    .org 0x2e7ca-ORIGIN
L_0002e7ca:
    cmp/hs r4,r6
    .org 0x2e7cc-ORIGIN
L_0002e7cc:
    bf/s L_0002e7c4
    .org 0x2e7ce-ORIGIN
L_0002e7ce:
    add #0x1,r5
    .org 0x2e7d0-ORIGIN
L_0002e7d0:
    mov.w P_0002e8c0,r5
    .org 0x2e7d2-ORIGIN
L_0002e7d2:
    mov #0x0,r6
    .org 0x2e7d4-ORIGIN
L_0002e7d4:
    add #0x1,r6
    .org 0x2e7d6-ORIGIN
L_0002e7d6:
    mov.b r7,@r5
    .org 0x2e7d8-ORIGIN
L_0002e7d8:
    extu.b r6,r6
    .org 0x2e7da-ORIGIN
L_0002e7da:
    cmp/hs r4,r6
    .org 0x2e7dc-ORIGIN
L_0002e7dc:
    bf/s L_0002e7d4
    .org 0x2e7de-ORIGIN
L_0002e7de:
    add #0x1,r5
    .org 0x2e7e0-ORIGIN
L_0002e7e0:
    mov.w P_0002e8c2,r5
    .org 0x2e7e2-ORIGIN
L_0002e7e2:
    mov #0x0,r6
    .org 0x2e7e4-ORIGIN
L_0002e7e4:
    add #0x1,r6
    .org 0x2e7e6-ORIGIN
L_0002e7e6:
    mov.b r7,@r5
    .org 0x2e7e8-ORIGIN
L_0002e7e8:
    extu.b r6,r6
    .org 0x2e7ea-ORIGIN
L_0002e7ea:
    cmp/hs r4,r6
    .org 0x2e7ec-ORIGIN
L_0002e7ec:
    bf/s L_0002e7e4
    .org 0x2e7ee-ORIGIN
L_0002e7ee:
    add #0x1,r5
    .org 0x2e7f0-ORIGIN
L_0002e7f0:
    mov.w P_0002e8c4,r5
    .org 0x2e7f2-ORIGIN
L_0002e7f2:
    mov #0x0,r6
    .org 0x2e7f4-ORIGIN
L_0002e7f4:
    mov #0x40,r4
    .org 0x2e7f6-ORIGIN
L_0002e7f6:
    add #0x1,r6
    .org 0x2e7f8-ORIGIN
L_0002e7f8:
    mov.b r7,@r5
    .org 0x2e7fa-ORIGIN
L_0002e7fa:
    extu.b r6,r6
    .org 0x2e7fc-ORIGIN
L_0002e7fc:
    cmp/hs r4,r6
    .org 0x2e7fe-ORIGIN
L_0002e7fe:
    bf/s L_0002e7f6
    .org 0x2e800-ORIGIN
L_0002e800:
    add #0x1,r5
    .org 0x2e802-ORIGIN
L_0002e802:
    mov.l P_0002e904,r6
    .org 0x2e804-ORIGIN
L_0002e804:
    mov #-0x1,r2
    .org 0x2e806-ORIGIN
L_0002e806:
    mov.w P_0002e8c6,r0
    .org 0x2e808-ORIGIN
L_0002e808:
    mov.b r2,@(r0,r6)
    .org 0x2e80a-ORIGIN
L_0002e80a:
    mov #0x15,r0
    .org 0x2e80c-ORIGIN
L_0002e80c:
    mov.l P_0002e908,r6
    .org 0x2e80e-ORIGIN
L_0002e80e:
    mov.b @(r0,r6),r0
    .org 0x2e810-ORIGIN
L_0002e810:
    and #0xdf,r0
    .org 0x2e812-ORIGIN
L_0002e812:
    mov r0,r2
    .org 0x2e814-ORIGIN
L_0002e814:
    mov #0x15,r0
    .org 0x2e816-ORIGIN
L_0002e816:
    rts
    .org 0x2e818-ORIGIN
L_0002e818:
    mov.b r2,@(r0,r6)
    .org 0x2e81a-ORIGIN
L_0002e81a:
    mov.l r14,@-r15
    .org 0x2e81c-ORIGIN
L_0002e81c:
    sts.l pr,@-r15
    .org 0x2e81e-ORIGIN
L_0002e81e:
    stc.l gbr,@-r15
    .org 0x2e820-ORIGIN
L_0002e820:
    mov.l P_0002e90c,r0
    .org 0x2e822-ORIGIN
L_0002e822:
    ldc r0,gbr
    .org 0x2e824-ORIGIN
L_0002e824:
    bsr L_0002e76e
    .org 0x2e826-ORIGIN
L_0002e826:
    nop
    .org 0x2e828-ORIGIN
L_0002e828:
    mov.w P_0002e8c8,r5
    .org 0x2e82a-ORIGIN
L_0002e82a:
    mov #0x0,r6
    .org 0x2e82c-ORIGIN
L_0002e82c:
    mov r6,r14
    .org 0x2e82e-ORIGIN
L_0002e82e:
    mov #0x6,r7
    .org 0x2e830-ORIGIN
L_0002e830:
    mov r5,r4
    .org 0x2e832-ORIGIN
L_0002e832:
    add #0x1c,r4
    .org 0x2e834-ORIGIN
L_0002e834:
    add #0x1,r6
    .org 0x2e836-ORIGIN
L_0002e836:
    mov.b r14,@r4
    .org 0x2e838-ORIGIN
L_0002e838:
    extu.b r6,r6
    .org 0x2e83a-ORIGIN
L_0002e83a:
    cmp/hs r7,r6
    .org 0x2e83c-ORIGIN
L_0002e83c:
    bf/s L_0002e834
    .org 0x2e83e-ORIGIN
L_0002e83e:
    add #0x1,r4
    .org 0x2e840-ORIGIN
L_0002e840:
    mov r5,r4
    .org 0x2e842-ORIGIN
L_0002e842:
    add #0x4,r4
    .org 0x2e844-ORIGIN
L_0002e844:
    mov #0x0,r6
    .org 0x2e846-ORIGIN
L_0002e846:
    mov #0x18,r7
    .org 0x2e848-ORIGIN
L_0002e848:
    add #0x1,r6
    .org 0x2e84a-ORIGIN
L_0002e84a:
    mov.b r14,@r4
    .org 0x2e84c-ORIGIN
L_0002e84c:
    extu.b r6,r6
    .org 0x2e84e-ORIGIN
L_0002e84e:
    cmp/hs r7,r6
    .org 0x2e850-ORIGIN
L_0002e850:
    bf/s L_0002e848
    .org 0x2e852-ORIGIN
L_0002e852:
    add #0x1,r4
    .org 0x2e854-ORIGIN
L_0002e854:
    mov #0x0,r6
    .org 0x2e856-ORIGIN
L_0002e856:
    mov #0x2,r4
    .org 0x2e858-ORIGIN
L_0002e858:
    add #0x1,r6
    .org 0x2e85a-ORIGIN
L_0002e85a:
    mov.b r14,@r5
    .org 0x2e85c-ORIGIN
L_0002e85c:
    extu.b r6,r6
    .org 0x2e85e-ORIGIN
L_0002e85e:
    cmp/hs r4,r6
    .org 0x2e860-ORIGIN
L_0002e860:
    bf/s L_0002e858
    .org 0x2e862-ORIGIN
L_0002e862:
    add #0x1,r5
    .org 0x2e864-ORIGIN
L_0002e864:
    mov.w P_0002e8ca,r6
    .org 0x2e866-ORIGIN
L_0002e866:
    mov.l P_0002e910,r5
    .org 0x2e868-ORIGIN
L_0002e868:
    mov.b @r6,r0
    .org 0x2e86a-ORIGIN
L_0002e86a:
    mov.l P_0002e914,r2
    .org 0x2e86c-ORIGIN
L_0002e86c:
    and #0x3f,r0
    .org 0x2e86e-ORIGIN
L_0002e86e:
    mov.b r0,@r6
    .org 0x2e870-ORIGIN
L_0002e870:
    mov #0x0,r0
    .org 0x2e872-ORIGIN
L_0002e872:
    mov.w P_0002e8cc,r6
    .org 0x2e874-ORIGIN
L_0002e874:
    mov.b r0,@(0x1,r6)
    .org 0x2e876-ORIGIN
L_0002e876:
    mov.b r0,@r6
    .org 0x2e878-ORIGIN
L_0002e878:
    mov.w P_0002e8ce,r6
    .org 0x2e87a-ORIGIN
L_0002e87a:
    mov.b r0,@(0x1,r6)
    .org 0x2e87c-ORIGIN
L_0002e87c:
    mov.b r0,@r6
    .org 0x2e87e-ORIGIN
L_0002e87e:
    mov #0x4,r0
    .org 0x2e880-ORIGIN
L_0002e880:
    and.b #0xef,@(r0,gbr)
    .org 0x2e882-ORIGIN
L_0002e882:
    mov.b @(0xa,r5),r0
    .org 0x2e884-ORIGIN
L_0002e884:
    jsr @r2
    .org 0x2e886-ORIGIN
L_0002e886:
    extu.b r0,r4
    .org 0x2e888-ORIGIN
L_0002e888:
    mov.l P_0002e910,r5
    .org 0x2e88a-ORIGIN
L_0002e88a:
    mov #0x0,r0
    .org 0x2e88c-ORIGIN
L_0002e88c:
    mov.l P_0002e904,r6
    .org 0x2e88e-ORIGIN
L_0002e88e:
    mov #0x0,r2
    .org 0x2e890-ORIGIN
L_0002e890:
    mov.b r0,@(0xa,r5)
    .org 0x2e892-ORIGIN
L_0002e892:
    mov #0x4a,r0
    .org 0x2e894-ORIGIN
L_0002e894:
    and.b #0xfe,@(r0,gbr)
    .org 0x2e896-ORIGIN
L_0002e896:
    mov #0x10,r0
    .org 0x2e898-ORIGIN
L_0002e898:
    and.b #0x9f,@(r0,gbr)
    .org 0x2e89a-ORIGIN
L_0002e89a:
    mov #-0x73,r0
    .org 0x2e89c-ORIGIN
L_0002e89c:
    extu.b r0,r0
    .org 0x2e89e-ORIGIN
L_0002e89e:
    mov.b r2,@(r0,r6)
    .org 0x2e8a0-ORIGIN
L_0002e8a0:
    ldc.l @r15+,gbr
    .org 0x2e8a2-ORIGIN
L_0002e8a2:
    lds.l @r15+,pr
    .org 0x2e8a4-ORIGIN
L_0002e8a4:
    rts
    .org 0x2e8a6-ORIGIN
L_0002e8a6:
    mov.l @r15+,r14
    .org 0x2e8be-ORIGIN
P_0002e8be:
    .word 0x9924
    .org 0x2e8c0-ORIGIN
P_0002e8c0:
    .word 0x9944
    .org 0x2e8c2-ORIGIN
P_0002e8c2:
    .word 0x9964
    .org 0x2e8c4-ORIGIN
P_0002e8c4:
    .word 0x9984
    .org 0x2e8c6-ORIGIN
P_0002e8c6:
    .word 0x029e
    .org 0x2e8c8-ORIGIN
P_0002e8c8:
    .word 0x99d8
    .org 0x2e8ca-ORIGIN
P_0002e8ca:
    .word 0x9a6b
    .org 0x2e8cc-ORIGIN
P_0002e8cc:
    .word 0x8422
    .org 0x2e8ce-ORIGIN
P_0002e8ce:
    .word 0x8462
    .org 0x2e904-ORIGIN
P_0002e904:
    .long 0xffff28f8
    .org 0x2e908-ORIGIN
P_0002e908:
    .long 0xffff421d
    .org 0x2e90c-ORIGIN
P_0002e90c:
    .long 0xffff4194
    .org 0x2e910-ORIGIN
P_0002e910:
    .long 0xffff40b4
    .org 0x2e914-ORIGIN
P_0002e914:
    .long 0x000cd75c
    .org 0xcd75c-ORIGIN
L_000cd75c:
    mov.l r14,@-r15
    .org 0xcd75e-ORIGIN
L_000cd75e:
    sts.l macl,@-r15
    .org 0xcd760-ORIGIN
L_000cd760:
    stc.l gbr,@-r15
    .org 0xcd762-ORIGIN
L_000cd762:
    mov.l P_000cdac0,r0
    .org 0xcd764-ORIGIN
L_000cd764:
    ldc r0,gbr
    .org 0xcd766-ORIGIN
L_000cd766:
    mov #-0x58,r2
    .org 0xcd768-ORIGIN
L_000cd768:
    mov.l P_000cdac4,r14
    .org 0xcd76a-ORIGIN
L_000cd76a:
    extu.b r2,r0
    .org 0xcd76c-ORIGIN
L_000cd76c:
    mov.w P_000cd844,r7
    .org 0xcd76e-ORIGIN
L_000cd76e:
    and.b #0xfe,@(r0,gbr)
    .org 0xcd770-ORIGIN
L_000cd770:
    mov #0x35,r0
    .org 0xcd772-ORIGIN
L_000cd772:
    and.b #0xfb,@(r0,gbr)
    .org 0xcd774-ORIGIN
L_000cd774:
    mov #0x8,r0
    .org 0xcd776-ORIGIN
L_000cd776:
    mov #0x0,r4
    .org 0xcd778-ORIGIN
L_000cd778:
    shll8 r0
    .org 0xcd77a-ORIGIN
L_000cd77a:
    mov r4,r5
    .org 0xcd77c-ORIGIN
L_000cd77c:
    mov.l r4,@(r0,r14)
    .org 0xcd77e-ORIGIN
L_000cd77e:
    mov #0x20,r1
    .org 0xcd780-ORIGIN
L_000cd780:
    mov.w P_000cd846,r0
    .org 0xcd782-ORIGIN
L_000cd782:
    mov.w r4,@(r0,r14)
    .org 0xcd784-ORIGIN
L_000cd784:
    mov.w P_000cd848,r0
    .org 0xcd786-ORIGIN
L_000cd786:
    mov.w r4,@(r0,r14)
    .org 0xcd788-ORIGIN
L_000cd788:
    mov.w P_000cd84a,r0
    .org 0xcd78a-ORIGIN
L_000cd78a:
    mov.b r4,@(r0,r14)
    .org 0xcd78c-ORIGIN
L_000cd78c:
    mov.w P_000cd84c,r0
    .org 0xcd78e-ORIGIN
L_000cd78e:
    mov.w r4,@(r0,r14)
    .org 0xcd790-ORIGIN
L_000cd790:
    mov.w P_000cd84e,r0
    .org 0xcd792-ORIGIN
L_000cd792:
    mov.w r4,@(r0,r14)
    .org 0xcd794-ORIGIN
L_000cd794:
    mov.w P_000cd850,r0
    .org 0xcd796-ORIGIN
L_000cd796:
    mov.w r4,@(r0,r14)
    .org 0xcd798-ORIGIN
L_000cd798:
    mov.w P_000cd852,r0
    .org 0xcd79a-ORIGIN
L_000cd79a:
    mov.w r4,@(r0,r14)
    .org 0xcd79c-ORIGIN
L_000cd79c:
    mov.w P_000cd854,r0
    .org 0xcd79e-ORIGIN
L_000cd79e:
    mov.b r4,@(r0,r14)
    .org 0xcd7a0-ORIGIN
L_000cd7a0:
    mov.w P_000cd856,r0
    .org 0xcd7a2-ORIGIN
L_000cd7a2:
    mov.b r4,@(r0,r14)
    .org 0xcd7a4-ORIGIN
L_000cd7a4:
    mov r14,r6
    .org 0xcd7a6-ORIGIN
L_000cd7a6:
    mov r7,r2
    .org 0xcd7a8-ORIGIN
L_000cd7a8:
    add r7,r6
    .org 0xcd7aa-ORIGIN
L_000cd7aa:
    extu.b r5,r0
    .org 0xcd7ac-ORIGIN
L_000cd7ac:
    add #0x20,r2
    .org 0xcd7ae-ORIGIN
L_000cd7ae:
    mov.b r4,@(r0,r6)
    .org 0xcd7b0-ORIGIN
L_000cd7b0:
    mov r14,r6
    .org 0xcd7b2-ORIGIN
L_000cd7b2:
    add r2,r6
    .org 0xcd7b4-ORIGIN
L_000cd7b4:
    mov.b r4,@(r0,r6)
    .org 0xcd7b6-ORIGIN
L_000cd7b6:
    add #0x1,r0
    .org 0xcd7b8-ORIGIN
L_000cd7b8:
    extu.b r0,r5
    .org 0xcd7ba-ORIGIN
L_000cd7ba:
    cmp/ge r1,r5
    .org 0xcd7bc-ORIGIN
L_000cd7bc:
    bf L_000cd7a4
    .org 0xcd7be-ORIGIN
L_000cd7be:
    mov.w P_000cd858,r6
    .org 0xcd7c0-ORIGIN
L_000cd7c0:
    mov #0x0,r0
    .org 0xcd7c2-ORIGIN
L_000cd7c2:
    mov #0x10,r14
    .org 0xcd7c4-ORIGIN
L_000cd7c4:
    mov.b r0,@r6
    .org 0xcd7c6-ORIGIN
L_000cd7c6:
    mov #0x11,r2
    .org 0xcd7c8-ORIGIN
L_000cd7c8:
    mov.b r0,@(0x1,r6)
    .org 0xcd7ca-ORIGIN
L_000cd7ca:
    mov #0x49,r0
    .org 0xcd7cc-ORIGIN
L_000cd7cc:
    and.b #0xbf,@(r0,gbr)
    .org 0xcd7ce-ORIGIN
L_000cd7ce:
    mov #0x53,r0
    .org 0xcd7d0-ORIGIN
L_000cd7d0:
    and.b #0x7f,@(r0,gbr)
    .org 0xcd7d2-ORIGIN
L_000cd7d2:
    mov #0x55,r0
    .org 0xcd7d4-ORIGIN
L_000cd7d4:
    and.b #0xfd,@(r0,gbr)
    .org 0xcd7d6-ORIGIN
L_000cd7d6:
    mov r14,r0
    .org 0xcd7d8-ORIGIN
L_000cd7d8:
    and.b #0x5f,@(r0,gbr)
    .org 0xcd7da-ORIGIN
L_000cd7da:
    mov r2,r0
    .org 0xcd7dc-ORIGIN
L_000cd7dc:
    and.b #0xef,@(r0,gbr)
    .org 0xcd7de-ORIGIN
L_000cd7de:
    mov r14,r0
    .org 0xcd7e0-ORIGIN
L_000cd7e0:
    and.b #0xbf,@(r0,gbr)
    .org 0xcd7e2-ORIGIN
L_000cd7e2:
    mov r2,r0
    .org 0xcd7e4-ORIGIN
L_000cd7e4:
    and.b #0x7f,@(r0,gbr)
    .org 0xcd7e6-ORIGIN
L_000cd7e6:
    mov r14,r0
    .org 0xcd7e8-ORIGIN
L_000cd7e8:
    and.b #0xef,@(r0,gbr)
    .org 0xcd7ea-ORIGIN
L_000cd7ea:
    mov #0x12,r0
    .org 0xcd7ec-ORIGIN
L_000cd7ec:
    and.b #0xfb,@(r0,gbr)
    .org 0xcd7ee-ORIGIN
L_000cd7ee:
    mov r14,r0
    .org 0xcd7f0-ORIGIN
L_000cd7f0:
    and.b #0xf7,@(r0,gbr)
    .org 0xcd7f2-ORIGIN
L_000cd7f2:
    mov #0x38,r0
    .org 0xcd7f4-ORIGIN
L_000cd7f4:
    and.b #0xdf,@(r0,gbr)
    .org 0xcd7f6-ORIGIN
L_000cd7f6:
    mov #0x4c,r0
    .org 0xcd7f8-ORIGIN
L_000cd7f8:
    and.b #0xf7,@(r0,gbr)
    .org 0xcd7fa-ORIGIN
L_000cd7fa:
    mov.b @(0x38,gbr),r0
    .org 0xcd7fc-ORIGIN
L_000cd7fc:
    tst #0x40,r0
    .org 0xcd7fe-ORIGIN
L_000cd7fe:
    bt L_000cd83c
    .org 0xcd800-ORIGIN
L_000cd800:
    mov.l P_000cdac8,r7
    .org 0xcd802-ORIGIN
L_000cd802:
    mov #0x7d,r4
    .org 0xcd804-ORIGIN
L_000cd804:
    mov.w P_000cd85a,r6
    .org 0xcd806-ORIGIN
L_000cd806:
    mov.b @r7,r2
    .org 0xcd808-ORIGIN
L_000cd808:
    extu.b r2,r5
    .org 0xcd80a-ORIGIN
L_000cd80a:
    mulu.w r5,r4
    .org 0xcd80c-ORIGIN
L_000cd80c:
    mov #0x0,r5
    .org 0xcd80e-ORIGIN
L_000cd80e:
    sts macl,r2
    .org 0xcd810-ORIGIN
L_000cd810:
    mov r2,r0
    .org 0xcd812-ORIGIN
L_000cd812:
    mov.w r0,@(0x8,r6)
    .org 0xcd814-ORIGIN
L_000cd814:
    mov r5,r0
    .org 0xcd816-ORIGIN
L_000cd816:
    mov.w r0,@(0x10,r6)
    .org 0xcd818-ORIGIN
L_000cd818:
    mov r2,r0
    .org 0xcd81a-ORIGIN
L_000cd81a:
    mov.w r0,@(0xa,r6)
    .org 0xcd81c-ORIGIN
L_000cd81c:
    mov r5,r0
    .org 0xcd81e-ORIGIN
L_000cd81e:
    mov.w r0,@(0x12,r6)
    .org 0xcd820-ORIGIN
L_000cd820:
    mov.b @(0x1,r7),r0
    .org 0xcd822-ORIGIN
L_000cd822:
    extu.b r0,r7
    .org 0xcd824-ORIGIN
L_000cd824:
    mulu.w r7,r4
    .org 0xcd826-ORIGIN
L_000cd826:
    sts macl,r2
    .org 0xcd828-ORIGIN
L_000cd828:
    mov r2,r0
    .org 0xcd82a-ORIGIN
L_000cd82a:
    mov.w r0,@(0xc,r6)
    .org 0xcd82c-ORIGIN
L_000cd82c:
    mov r5,r0
    .org 0xcd82e-ORIGIN
L_000cd82e:
    mov.w r0,@(0x14,r6)
    .org 0xcd830-ORIGIN
L_000cd830:
    mov r2,r0
    .org 0xcd832-ORIGIN
L_000cd832:
    mov.w r0,@(0xe,r6)
    .org 0xcd834-ORIGIN
L_000cd834:
    mov r5,r0
    .org 0xcd836-ORIGIN
L_000cd836:
    mov.w r0,@(0x16,r6)
    .org 0xcd838-ORIGIN
L_000cd838:
    mov #0x38,r0
    .org 0xcd83a-ORIGIN
L_000cd83a:
    and.b #0xbf,@(r0,gbr)
    .org 0xcd83c-ORIGIN
L_000cd83c:
    ldc.l @r15+,gbr
    .org 0xcd83e-ORIGIN
L_000cd83e:
    lds.l @r15+,macl
    .org 0xcd840-ORIGIN
L_000cd840:
    rts
    .org 0xcd842-ORIGIN
L_000cd842:
    mov.l @r15+,r14
    .org 0xcd844-ORIGIN
P_000cd844:
    .word 0x07ba
    .org 0xcd846-ORIGIN
P_000cd846:
    .word 0x078c
    .org 0xcd848-ORIGIN
P_000cd848:
    .word 0x07b8
    .org 0xcd84a-ORIGIN
P_000cd84a:
    .word 0x078e
    .org 0xcd84c-ORIGIN
P_000cd84c:
    .word 0x0790
    .org 0xcd84e-ORIGIN
P_000cd84e:
    .word 0x0792
    .org 0xcd850-ORIGIN
P_000cd850:
    .word 0x07b4
    .org 0xcd852-ORIGIN
P_000cd852:
    .word 0x07fa
    .org 0xcd854-ORIGIN
P_000cd854:
    .word 0x07b6
    .org 0xcd856-ORIGIN
P_000cd856:
    .word 0x07fc
    .org 0xcd858-ORIGIN
P_000cd858:
    .word 0x9f08
    .org 0xcd85a-ORIGIN
P_000cd85a:
    .word 0xf580
    .org 0xcdac0-ORIGIN
P_000cdac0:
    .long 0xffff41a9
    .org 0xcdac4-ORIGIN
P_000cdac4:
    .long 0xffff28f8
    .org 0xcdac8-ORIGIN
P_000cdac8:
    .long 0x00008dfc
