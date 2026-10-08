! Exact independent reconstruction of the natural signed additive entry.
    .text
    .balign 4
    .org 0x8b40 - 0x8b40
L_00008b40:
    .byte 0x00
    .org 0x52902 - 0x8b40
L_00052902:
    sts.l macl,@-r15
    .org 0x52904 - 0x8b40
L_00052904:
    mov.l L_00052964,r5
    .org 0x52906 - 0x8b40
L_00052906:
    mov.w L_0005295e,r0
    .org 0x52908 - 0x8b40
L_00052908:
    mov.b @(r0,r5),r2
    .org 0x5290a - 0x8b40
L_0005290a:
    mov.w L_00052960,r0
    .org 0x5290c - 0x8b40
L_0005290c:
    extu.b r2,r2
    .org 0x5290e - 0x8b40
L_0005290e:
    mov.w @(r0,r5),r6
    .org 0x52910 - 0x8b40
L_00052910:
    mul.l r6,r2
    .org 0x52912 - 0x8b40
L_00052912:
    sts macl,r6
    .org 0x52914 - 0x8b40
L_00052914:
    cmp/pz r6
    .org 0x52916 - 0x8b40
L_00052916:
    bt L_0005291e
    .org 0x52918 - 0x8b40
L_00052918:
    mov #-0x1,r2
    .org 0x5291a - 0x8b40
L_0005291a:
    extu.b r2,r2
    .org 0x5291c - 0x8b40
L_0005291c:
    add r2,r6
    .org 0x5291e - 0x8b40
L_0005291e:
    mov r6,r2
    .org 0x52920 - 0x8b40
L_00052920:
    shlr8 r2
    .org 0x52922 - 0x8b40
L_00052922:
    swap.w r2,r6
    .org 0x52924 - 0x8b40
L_00052924:
    exts.b r6,r2
    .org 0x52926 - 0x8b40
L_00052926:
    xtrct r2,r6
    .org 0x52928 - 0x8b40
L_00052928:
    cmp/pz r6
    .org 0x5292a - 0x8b40
L_0005292a:
    bf L_00052938
    .org 0x5292c - 0x8b40
L_0005292c:
    mov.w L_00052962,r2
    .org 0x5292e - 0x8b40
L_0005292e:
    cmp/gt r2,r6
    .org 0x52930 - 0x8b40
L_00052930:
    bf L_00052934
    .org 0x52932 - 0x8b40
L_00052932:
    mov r2,r6
    .org 0x52934 - 0x8b40
L_00052934:
    bra L_00052942
    .org 0x52936 - 0x8b40
L_00052936:
    mov r6,r5
    .org 0x52938 - 0x8b40
L_00052938:
    mov #-0x80,r5
    .org 0x5293a - 0x8b40
L_0005293a:
    shll8 r5
    .org 0x5293c - 0x8b40
L_0005293c:
    cmp/ge r5,r6
    .org 0x5293e - 0x8b40
L_0005293e:
    bf L_00052942
    .org 0x52940 - 0x8b40
L_00052940:
    mov r6,r5
    .org 0x52942 - 0x8b40
L_00052942:
    mov.l L_0005297c,r6
    .org 0x52944 - 0x8b40
L_00052944:
    mov.b @(0x1,r6),r0
    .org 0x52946 - 0x8b40
L_00052946:
    tst #0x20,r0
    .org 0x52948 - 0x8b40
L_00052948:
    bt L_00052954
    .org 0x5294a - 0x8b40
L_0005294a:
    mov.l L_0005298c,r6
    .org 0x5294c - 0x8b40
L_0005294c:
    mov.b @r6,r0
    .org 0x5294e - 0x8b40
L_0005294e:
    tst #0x4,r0
    .org 0x52950 - 0x8b40
L_00052950:
    bt L_00052954
    .org 0x52952 - 0x8b40
L_00052952:
    mov #0x0,r5
    .org 0x52954 - 0x8b40
L_00052954:
    mov.l L_00052990,r6
    .org 0x52956 - 0x8b40
L_00052956:
    mov r5,r0
    .org 0x52958 - 0x8b40
L_00052958:
    mov.w r0,@(0x8,r6)
    .org 0x5295a - 0x8b40
L_0005295a:
    rts
    .org 0x5295c - 0x8b40
L_0005295c:
    lds.l @r15+,macl
    .org 0x5295e - 0x8b40
L_0005295e:
    .word 0x027e
    .org 0x52960 - 0x8b40
L_00052960:
    .word 0x07da
    .org 0x52962 - 0x8b40
L_00052962:
    .word 0x7fff
    .org 0x52964 - 0x8b40
L_00052964:
    .long 0xffff128c
    .org 0x5297c - 0x8b40
L_0005297c:
    .long 0xffff245c
    .org 0x5298c - 0x8b40
L_0005298c:
    .long 0x00008b40
    .org 0x52990 - 0x8b40
L_00052990:
    .long 0xffff22f8
