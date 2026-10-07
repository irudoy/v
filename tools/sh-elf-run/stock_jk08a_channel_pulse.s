! Full stock channel builder, arithmetic shift, and affine floor.
    .text
    .balign 4
    .org 0x8d92 - 0x8d90
L_00008d92:
    .byte 0x7a
    .org 0x91da - 0x8d90
L_000091da:
    .word 13656,16384,4250,0
    .org 0x129c0 - 0x8d90
L_000129c0:
    .byte 128,128,128,128,128,128
    .org 0x224f8 - 0x8d90
L_000224f8:
    shar r0
    .org 0x224fa - 0x8d90
L_000224fa:
    shar r0
    .org 0x224fc - 0x8d90
L_000224fc:
    shar r0
    .org 0x224fe - 0x8d90
L_000224fe:
    shar r0
    .org 0x22500 - 0x8d90
L_00022500:
    shar r0
    .org 0x22502 - 0x8d90
L_00022502:
    shar r0
    .org 0x22504 - 0x8d90
L_00022504:
    rts
    .org 0x22506 - 0x8d90
L_00022506:
    shar r0
    .org 0x4eba2 - 0x8d90
L_0004eba2:
    mov.l r14,@-r15
    .org 0x4eba4 - 0x8d90
L_0004eba4:
    sts.l pr,@-r15
    .org 0x4eba6 - 0x8d90
L_0004eba6:
    sts.l macl,@-r15
    .org 0x4eba8 - 0x8d90
L_0004eba8:
    stc.l gbr,@-r15
    .org 0x4ebaa - 0x8d90
L_0004ebaa:
    mov.l L_0004ec20,r0
    .org 0x4ebac - 0x8d90
L_0004ebac:
    ldc r0,gbr
    .org 0x4ebae - 0x8d90
L_0004ebae:
    add #-0x4,r15
    .org 0x4ebb0 - 0x8d90
L_0004ebb0:
    extu.b r4,r4
    .org 0x4ebb2 - 0x8d90
L_0004ebb2:
    mov r4,r14
    .org 0x4ebb4 - 0x8d90
L_0004ebb4:
    shll r14
    .org 0x4ebb6 - 0x8d90
L_0004ebb6:
    cmp/pl r4
    .org 0x4ebb8 - 0x8d90
L_0004ebb8:
    mov #0x1,r2
    .org 0x4ebba - 0x8d90
L_0004ebba:
    bf/s L_0004ebc6
    .org 0x4ebbc - 0x8d90
L_0004ebbc:
    mov #0x0,r6
    .org 0x4ebbe - 0x8d90
L_0004ebbe:
    add #0x1,r6
    .org 0x4ebc0 - 0x8d90
L_0004ebc0:
    shll r2
    .org 0x4ebc2 - 0x8d90
L_0004ebc2:
    cmp/ge r4,r6
    .org 0x4ebc4 - 0x8d90
L_0004ebc4:
    bf L_0004ebbe
    .org 0x4ebc6 - 0x8d90
L_0004ebc6:
    mov.l L_0004ec08,r5
    .org 0x4ebc8 - 0x8d90
L_0004ebc8:
    mov.b @(0x4,r5),r0
    .org 0x4ebca - 0x8d90
L_0004ebca:
    extu.b r0,r5
    .org 0x4ebcc - 0x8d90
L_0004ebcc:
    tst r2,r5
    .org 0x4ebce - 0x8d90
L_0004ebce:
    bt L_0004ec24
    .org 0x4ebd0 - 0x8d90
L_0004ebd0:
    stc gbr,r2
    .org 0x4ebd2 - 0x8d90
L_0004ebd2:
    mov.w @(0x7a,gbr),r0
    .org 0x4ebd4 - 0x8d90
L_0004ebd4:
    add #0x18,r2
    .org 0x4ebd6 - 0x8d90
L_0004ebd6:
    mov r0,r6
    .org 0x4ebd8 - 0x8d90
L_0004ebd8:
    mov r14,r0
    .org 0x4ebda - 0x8d90
L_0004ebda:
    mov.w r6,@(r0,r2)
    .org 0x4ebdc - 0x8d90
L_0004ebdc:
    extu.w r6,r6
    .org 0x4ebde - 0x8d90
L_0004ebde:
    bra L_0004ec96
    .org 0x4ebe0 - 0x8d90
L_0004ebe0:
    mov.l r6,@r15
    .org 0x4ec08 - 0x8d90
L_0004ec08:
    .long 0xffff22dc
    .org 0x4ec20 - 0x8d90
L_0004ec20:
    .long 0xffff23bc
    .org 0x4ec24 - 0x8d90
L_0004ec24:
    mov r4,r0
    .org 0x4ec26 - 0x8d90
L_0004ec26:
    tst #0x1,r0
    .org 0x4ec28 - 0x8d90
L_0004ec28:
    mov.l L_0004ed70,r7
    .org 0x4ec2a - 0x8d90
L_0004ec2a:
    bt L_0004ec34
    .org 0x4ec2c - 0x8d90
L_0004ec2c:
    mov.w L_0004ed60,r0
    .org 0x4ec2e - 0x8d90
L_0004ec2e:
    mov.w @(r0,r7),r6
    .org 0x4ec30 - 0x8d90
L_0004ec30:
    bra L_0004ec3a
    .org 0x4ec32 - 0x8d90
L_0004ec32:
    extu.w r6,r6
    .org 0x4ec34 - 0x8d90
L_0004ec34:
    mov.w L_0004ed62,r0
    .org 0x4ec36 - 0x8d90
L_0004ec36:
    mov.w @(r0,r7),r2
    .org 0x4ec38 - 0x8d90
L_0004ec38:
    extu.w r2,r6
    .org 0x4ec3a - 0x8d90
L_0004ec3a:
    mov.w L_0004ed64,r5
    .org 0x4ec3c - 0x8d90
L_0004ec3c:
    mov r7,r2
    .org 0x4ec3e - 0x8d90
L_0004ec3e:
    mov r14,r0
    .org 0x4ec40 - 0x8d90
L_0004ec40:
    add r5,r2
    .org 0x4ec42 - 0x8d90
L_0004ec42:
    mov.w @(r0,r2),r5
    .org 0x4ec44 - 0x8d90
L_0004ec44:
    add r5,r6
    .org 0x4ec46 - 0x8d90
L_0004ec46:
    mov.l L_0004ed74,r5
    .org 0x4ec48 - 0x8d90
L_0004ec48:
    mov.b @r5,r2
    .org 0x4ec4a - 0x8d90
L_0004ec4a:
    extu.b r2,r5
    .org 0x4ec4c - 0x8d90
L_0004ec4c:
    mov r5,r0
    .org 0x4ec4e - 0x8d90
L_0004ec4e:
    tst #0x8,r0
    .org 0x4ec50 - 0x8d90
L_0004ec50:
    bt L_0004ec5c
    .org 0x4ec52 - 0x8d90
L_0004ec52:
    mov.w L_0004ed66,r2
    .org 0x4ec54 - 0x8d90
L_0004ec54:
    mov r14,r0
    .org 0x4ec56 - 0x8d90
L_0004ec56:
    add r2,r7
    .org 0x4ec58 - 0x8d90
L_0004ec58:
    mov.w @(r0,r7),r2
    .org 0x4ec5a - 0x8d90
L_0004ec5a:
    sub r2,r6
    .org 0x4ec5c - 0x8d90
L_0004ec5c:
    cmp/pl r6
    .org 0x4ec5e - 0x8d90
L_0004ec5e:
    bf L_0004ec7e
    .org 0x4ec60 - 0x8d90
L_0004ec60:
    mov.l L_0004ed78,r5
    .org 0x4ec62 - 0x8d90
L_0004ec62:
    mov r4,r0
    .org 0x4ec64 - 0x8d90
L_0004ec64:
    mov.b @(r0,r5),r2
    .org 0x4ec66 - 0x8d90
L_0004ec66:
    extu.b r2,r2
    .org 0x4ec68 - 0x8d90
L_0004ec68:
    mul.l r6,r2
    .org 0x4ec6a - 0x8d90
L_0004ec6a:
    mov.l L_0004ed7c,r6
    .org 0x4ec6c - 0x8d90
L_0004ec6c:
    jsr @r6
    .org 0x4ec6e - 0x8d90
L_0004ec6e:
    sts macl,r0
    .org 0x4ec70 - 0x8d90
L_0004ec70:
    mov #-0x1,r6
    .org 0x4ec72 - 0x8d90
L_0004ec72:
    extu.w r6,r6
    .org 0x4ec74 - 0x8d90
L_0004ec74:
    cmp/gt r6,r0
    .org 0x4ec76 - 0x8d90
L_0004ec76:
    bt/s L_0004ec84
    .org 0x4ec78 - 0x8d90
L_0004ec78:
    mov r0,r2
    .org 0x4ec7a - 0x8d90
L_0004ec7a:
    bra L_0004ec84
    .org 0x4ec7c - 0x8d90
L_0004ec7c:
    mov r2,r6
    .org 0x4ec7e - 0x8d90
L_0004ec7e:
    cmp/pz r6
    .org 0x4ec80 - 0x8d90
L_0004ec80:
    bt L_0004ec84
    .org 0x4ec82 - 0x8d90
L_0004ec82:
    mov #0x0,r6
    .org 0x4ec84 - 0x8d90
L_0004ec84:
    mov.l L_0004ed80,r2
    .org 0x4ec86 - 0x8d90
L_0004ec86:
    extu.w r6,r4
    .org 0x4ec88 - 0x8d90
L_0004ec88:
    jsr @r2
    .org 0x4ec8a - 0x8d90
L_0004ec8a:
    mov.l r6,@r15
    .org 0x4ec8c - 0x8d90
L_0004ec8c:
    mov r0,r2
    .org 0x4ec8e - 0x8d90
L_0004ec8e:
    mov r14,r0
    .org 0x4ec90 - 0x8d90
L_0004ec90:
    stc gbr,r5
    .org 0x4ec92 - 0x8d90
L_0004ec92:
    add #0x18,r5
    .org 0x4ec94 - 0x8d90
L_0004ec94:
    mov.w r2,@(r0,r5)
    .org 0x4ec96 - 0x8d90
L_0004ec96:
    stc gbr,r2
    .org 0x4ec98 - 0x8d90
L_0004ec98:
    mov.l @r15,r6
    .org 0x4ec9a - 0x8d90
L_0004ec9a:
    add #0xc,r2
    .org 0x4ec9c - 0x8d90
L_0004ec9c:
    mov r14,r0
    .org 0x4ec9e - 0x8d90
L_0004ec9e:
    mov.w r6,@(r0,r2)
    .org 0x4eca0 - 0x8d90
L_0004eca0:
    add #0x4,r15
    .org 0x4eca2 - 0x8d90
L_0004eca2:
    ldc.l @r15+,gbr
    .org 0x4eca4 - 0x8d90
L_0004eca4:
    lds.l @r15+,macl
    .org 0x4eca6 - 0x8d90
L_0004eca6:
    lds.l @r15+,pr
    .org 0x4eca8 - 0x8d90
L_0004eca8:
    rts
    .org 0x4ecaa - 0x8d90
L_0004ecaa:
    mov.l @r15+,r14
    .org 0x4ed60 - 0x8d90
L_0004ed60:
    .word 0x0692
    .org 0x4ed62 - 0x8d90
L_0004ed62:
    .word 0x0690
    .org 0x4ed64 - 0x8d90
L_0004ed64:
    .word 0x010a
    .org 0x4ed66 - 0x8d90
L_0004ed66:
    .word 0x01da
    .org 0x4ed70 - 0x8d90
L_0004ed70:
    .long 0xffff128c
    .org 0x4ed74 - 0x8d90
L_0004ed74:
    .long 0x00008d92
    .org 0x4ed78 - 0x8d90
L_0004ed78:
    .long 0x000129c0
    .org 0x4ed7c - 0x8d90
L_0004ed7c:
    .long 0x000224f8
    .org 0x4ed80 - 0x8d90
L_0004ed80:
    .long 0x0005b7ec
    .org 0x5b7ec - 0x8d90
L_0005b7ec:
    mov.l r14,@-r15
    .org 0x5b7ee - 0x8d90
L_0005b7ee:
    sts.l macl,@-r15
    .org 0x5b7f0 - 0x8d90
L_0005b7f0:
    stc.l gbr,@-r15
    .org 0x5b7f2 - 0x8d90
L_0005b7f2:
    mov.l L_0005b884,r0
    .org 0x5b7f4 - 0x8d90
L_0005b7f4:
    ldc r0,gbr
    .org 0x5b7f6 - 0x8d90
L_0005b7f6:
    mov.w @(0x0,gbr),r0
    .org 0x5b7f8 - 0x8d90
L_0005b7f8:
    extu.w r4,r7
    .org 0x5b7fa - 0x8d90
L_0005b7fa:
    mov #0x64,r3
    .org 0x5b7fc - 0x8d90
L_0005b7fc:
    extu.w r0,r2
    .org 0x5b7fe - 0x8d90
L_0005b7fe:
    mov.w @(0x4,gbr),r0
    .org 0x5b800 - 0x8d90
L_0005b800:
    mul.l r2,r7
    .org 0x5b802 - 0x8d90
L_0005b802:
    extu.w r0,r4
    .org 0x5b804 - 0x8d90
L_0005b804:
    mov #-0x1,r1
    .org 0x5b806 - 0x8d90
L_0005b806:
    sts macl,r14
    .org 0x5b808 - 0x8d90
L_0005b808:
    mul.l r4,r3
    .org 0x5b80a - 0x8d90
L_0005b80a:
    mov r14,r6
    .org 0x5b80c - 0x8d90
L_0005b80c:
    extu.w r1,r1
    .org 0x5b80e - 0x8d90
L_0005b80e:
    sts macl,r2
    .org 0x5b810 - 0x8d90
L_0005b810:
    add r2,r6
    .org 0x5b812 - 0x8d90
L_0005b812:
    shlr8 r6
    .org 0x5b814 - 0x8d90
L_0005b814:
    shlr2 r6
    .org 0x5b816 - 0x8d90
L_0005b816:
    shlr2 r6
    .org 0x5b818 - 0x8d90
L_0005b818:
    shlr2 r6
    .org 0x5b81a - 0x8d90
L_0005b81a:
    cmp/hi r1,r6
    .org 0x5b81c - 0x8d90
L_0005b81c:
    bf L_0005b822
    .org 0x5b81e - 0x8d90
L_0005b81e:
    bra L_0005b834
    .org 0x5b820 - 0x8d90
L_0005b820:
    mov r1,r4
    .org 0x5b822 - 0x8d90
L_0005b822:
    mov #0x64,r3
    .org 0x5b824 - 0x8d90
L_0005b824:
    mul.l r4,r3
    .org 0x5b826 - 0x8d90
L_0005b826:
    sts macl,r2
    .org 0x5b828 - 0x8d90
L_0005b828:
    add r2,r14
    .org 0x5b82a - 0x8d90
L_0005b82a:
    shlr8 r14
    .org 0x5b82c - 0x8d90
L_0005b82c:
    shlr2 r14
    .org 0x5b82e - 0x8d90
L_0005b82e:
    shlr2 r14
    .org 0x5b830 - 0x8d90
L_0005b830:
    shlr2 r14
    .org 0x5b832 - 0x8d90
L_0005b832:
    mov r14,r4
    .org 0x5b834 - 0x8d90
L_0005b834:
    mov.w @(0x2,gbr),r0
    .org 0x5b836 - 0x8d90
L_0005b836:
    mov #0x64,r3
    .org 0x5b838 - 0x8d90
L_0005b838:
    extu.w r0,r2
    .org 0x5b83a - 0x8d90
L_0005b83a:
    mov.w @(0x6,gbr),r0
    .org 0x5b83c - 0x8d90
L_0005b83c:
    mul.l r2,r7
    .org 0x5b83e - 0x8d90
L_0005b83e:
    extu.w r0,r5
    .org 0x5b840 - 0x8d90
L_0005b840:
    sts macl,r14
    .org 0x5b842 - 0x8d90
L_0005b842:
    mul.l r5,r3
    .org 0x5b844 - 0x8d90
L_0005b844:
    mov r14,r6
    .org 0x5b846 - 0x8d90
L_0005b846:
    sts macl,r2
    .org 0x5b848 - 0x8d90
L_0005b848:
    add r2,r6
    .org 0x5b84a - 0x8d90
L_0005b84a:
    shlr8 r6
    .org 0x5b84c - 0x8d90
L_0005b84c:
    shlr2 r6
    .org 0x5b84e - 0x8d90
L_0005b84e:
    shlr2 r6
    .org 0x5b850 - 0x8d90
L_0005b850:
    shlr2 r6
    .org 0x5b852 - 0x8d90
L_0005b852:
    cmp/hi r1,r6
    .org 0x5b854 - 0x8d90
L_0005b854:
    bt/s L_0005b86a
    .org 0x5b856 - 0x8d90
L_0005b856:
    extu.w r4,r4
    .org 0x5b858 - 0x8d90
L_0005b858:
    mov #0x64,r3
    .org 0x5b85a - 0x8d90
L_0005b85a:
    mul.l r5,r3
    .org 0x5b85c - 0x8d90
L_0005b85c:
    sts macl,r2
    .org 0x5b85e - 0x8d90
L_0005b85e:
    add r2,r14
    .org 0x5b860 - 0x8d90
L_0005b860:
    shlr8 r14
    .org 0x5b862 - 0x8d90
L_0005b862:
    shlr2 r14
    .org 0x5b864 - 0x8d90
L_0005b864:
    shlr2 r14
    .org 0x5b866 - 0x8d90
L_0005b866:
    shlr2 r14
    .org 0x5b868 - 0x8d90
L_0005b868:
    mov r14,r1
    .org 0x5b86a - 0x8d90
L_0005b86a:
    cmp/ge r4,r7
    .org 0x5b86c - 0x8d90
L_0005b86c:
    bt/s L_0005b872
    .org 0x5b86e - 0x8d90
L_0005b86e:
    extu.w r1,r5
    .org 0x5b870 - 0x8d90
L_0005b870:
    mov r4,r7
    .org 0x5b872 - 0x8d90
L_0005b872:
    extu.w r7,r2
    .org 0x5b874 - 0x8d90
L_0005b874:
    cmp/ge r5,r2
    .org 0x5b876 - 0x8d90
L_0005b876:
    bt L_0005b87a
    .org 0x5b878 - 0x8d90
L_0005b878:
    mov r5,r2
    .org 0x5b87a - 0x8d90
L_0005b87a:
    extu.w r2,r0
    .org 0x5b87c - 0x8d90
L_0005b87c:
    ldc.l @r15+,gbr
    .org 0x5b87e - 0x8d90
L_0005b87e:
    lds.l @r15+,macl
    .org 0x5b880 - 0x8d90
L_0005b880:
    rts
    .org 0x5b882 - 0x8d90
L_0005b882:
    mov.l @r15+,r14
    .org 0x5b884 - 0x8d90
L_0005b884:
    .long 0x000091da
