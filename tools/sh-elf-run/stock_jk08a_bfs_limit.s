! JK08A normal BFS cap and diagnostic alternate schedule publication.
! The byte wrapper, four-shift body, finisher, and pools retain stock addresses.
    .section .text
    .balign 4
    .org 0x2
P_0000974e:
    .byte 0x36
P_0000974f:
    .byte 0x3c
P_00009750:
    .byte 0x4c
P_00009751:
    .byte 0x61
P_00009752:
    .byte 0x32
P_00009753:
    .byte 0x34
P_00009754:
    .byte 0x40
P_00009755:
    .byte 0x5a
P_00009756:
    .byte 0x30
P_00009757:
    .byte 0x31
P_00009758:
    .byte 0x38
P_00009759:
    .byte 0x54
    .org 0x9552
P_00012c9e:
    .byte 0x65
P_00012c9f:
    .byte 0x65
P_00012ca0:
    .byte 0xff
P_00012ca1:
    .byte 0xff
P_00012ca2:
    .byte 0xff
P_00012ca3:
    .byte 0xff
P_00012ca4:
    .byte 0xff
P_00012ca5:
    .byte 0xff
P_00012ca6:
    .byte 0xff
P_00012ca7:
    .byte 0xff
P_00012ca8:
    .byte 0xff
P_00012ca9:
    .byte 0xff
P_00012caa:
    .byte 0xff
P_00012cab:
    .byte 0xff
P_00012cac:
    .byte 0xff
P_00012cad:
    .byte 0xff
    .org 0x1cc3c
L_00026388:
    mov.w P_0002639a,r0
L_0002638a:
    extu.b r5,r5
L_0002638c:
    cmp/hs r0,r5
L_0002638e:
    bt L_00026396
L_00026390:
    mov.l P_0002639c,r6
L_00026392:
    jmp @r6
L_00026394:
    mov #0x0,r3
L_00026396:
    rts
L_00026398:
    mov.b @(0xf,r4),r0
P_0002639a:
    .byte 0x00
P_0002639b:
    .byte 0xf0
P_0002639c:
    .byte 0x00
P_0002639d:
    .byte 0x02
P_0002639e:
    .byte 0x6a
P_0002639f:
    .byte 0x84
    .org 0x1cff4
L_00026740:
    cmp/hs r0,r2
L_00026742:
    bt L_0002675c
L_00026744:
    mov.l r0,@-r15
L_00026746:
    sub r2,r0
L_00026748:
    sts macl,r1
L_0002674a:
    mul.l r3,r0
L_0002674c:
    sts macl,r0
L_0002674e:
    lds r1,macl
L_00026750:
    swap.w r0,r0
L_00026752:
    mov.l @r15+,r2
L_00026754:
    extu.w r0,r0
L_00026756:
    sub r0,r2
L_00026758:
    rts
L_0002675a:
    mov r2,r0
L_0002675c:
    sub r0,r2
L_0002675e:
    sts macl,r1
L_00026760:
    mul.l r3,r2
L_00026762:
    sts macl,r2
L_00026764:
    lds r1,macl
L_00026766:
    swap.w r2,r2
L_00026768:
    extu.w r2,r2
L_0002676a:
    rts
L_0002676c:
    add r2,r0
    .org 0x1d338
L_00026a84:
    shlr r5
L_00026a86:
    rotcr r3
L_00026a88:
    shlr r5
L_00026a8a:
    rotcr r3
L_00026a8c:
    shlr r5
L_00026a8e:
    rotcr r3
L_00026a90:
    shlr r5
L_00026a92:
    rotcr r3
L_00026a94:
    swap.w r3,r3
L_00026a96:
    shlr8 r0
L_00026a98:
    tst r0,r0
L_00026a9a:
    bt L_00026aaa
L_00026a9c:
    shll r5
L_00026a9e:
    add r5,r4
L_00026aa0:
    mov.w @r4,r1
L_00026aa2:
    mov.w @(0x2,r4),r0
L_00026aa4:
    extu.w r0,r2
L_00026aa6:
    bra L_00026ab4
L_00026aa8:
    extu.w r1,r0
L_00026aaa:
    add r5,r4
L_00026aac:
    mov.b @r4,r1
L_00026aae:
    mov.b @(0x1,r4),r0
L_00026ab0:
    extu.b r0,r2
L_00026ab2:
    extu.b r1,r0
L_00026ab4:
    mov.l P_00026abc,r6
L_00026ab6:
    jmp @r6
L_00026ab8:
    nop
    .org 0x1d370
P_00026abc:
    .byte 0x00
P_00026abd:
    .byte 0x02
P_00026abe:
    .byte 0x67
P_00026abf:
    .byte 0x40
    .org 0x3243a
L_0003bb86:
    mov.l P_0003bbd0,r6
L_0003bb88:
    mov.b @(0x1,r6),r0
L_0003bb8a:
    tst #0x80,r0
L_0003bb8c:
    bf L_0003bc16
L_0003bb8e:
    tst r5,r5
L_0003bb90:
    bf L_0003bbac
L_0003bb92:
    mov.w @(0x2,gbr),r0
L_0003bb94:
    exts.w r7,r7
L_0003bb96:
    extu.w r0,r6
L_0003bb98:
    mov r6,r2
L_0003bb9a:
    add r7,r2
L_0003bb9c:
    cmp/pz r2
L_0003bb9e:
    bt L_0003bba4
L_0003bba0:
    bra L_0003bbaa
L_0003bba2:
    mov #0x0,r2
L_0003bba4:
    exts.w r7,r7
L_0003bba6:
    add r7,r6
L_0003bba8:
    mov r6,r2
L_0003bbaa:
    mov r2,r14
L_0003bbac:
    tst r5,r5
L_0003bbae:
    bt L_0003bbf4
L_0003bbb0:
    mov.w @(0x0,gbr),r0
L_0003bbb2:
    exts.w r7,r7
L_0003bbb4:
    extu.w r0,r6
L_0003bbb6:
    mov r6,r2
L_0003bbb8:
    add r7,r2
L_0003bbba:
    cmp/pz r2
L_0003bbbc:
    bt L_0003bbec
L_0003bbbe:
    bra L_0003bbf2
L_0003bbc0:
    mov #0x0,r2
    .org 0x32484
P_0003bbd0:
    .byte 0xff
P_0003bbd1:
    .byte 0xff
P_0003bbd2:
    .byte 0x24
P_0003bbd3:
    .byte 0x48
    .org 0x324a0
L_0003bbec:
    exts.w r7,r7
L_0003bbee:
    add r7,r6
L_0003bbf0:
    mov r6,r2
L_0003bbf2:
    mov r2,r14
L_0003bbf4:
    mov.l P_0003bde4,r7
L_0003bbf6:
    mov #0x17,r0
L_0003bbf8:
    mov.l P_0003bde8,r4
L_0003bbfa:
    mov.b @(r0,r7),r6
L_0003bbfc:
    mov.l P_0003bdec,r2
L_0003bbfe:
    jsr @r2
L_0003bc00:
    extu.b r6,r5
L_0003bc02:
    extu.b r0,r2
L_0003bc04:
    mov.b r0,@(0x5a,gbr)
L_0003bc06:
    shll8 r2
L_0003bc08:
    cmp/hi r2,r14
L_0003bc0a:
    bf/s L_0003bc10
L_0003bc0c:
    mov r14,r5
L_0003bc0e:
    mov r2,r5
L_0003bc10:
    mov.l P_0003bdf0,r9
L_0003bc12:
    bra L_0003bc78
L_0003bc14:
    nop
L_0003bc16:
    mov.l P_0003bde4,r7
L_0003bc18:
    mov #0x16,r0
L_0003bc1a:
    mov #0x3,r2
L_0003bc1c:
    mov.b @(r0,r7),r5
L_0003bc1e:
    mov #0x40,r6
L_0003bc20:
    extu.b r5,r5
L_0003bc22:
    cmp/hi r5,r6
L_0003bc24:
    bf L_0003bc30
L_0003bc26:
    shlr2 r6
L_0003bc28:
    shlr2 r6
L_0003bc2a:
    shlr2 r6
L_0003bc2c:
    bra L_0003bc38
L_0003bc2e:
    mov r6,r5
L_0003bc30:
    dt r2
L_0003bc32:
    bf/s L_0003bc22
L_0003bc34:
    add #0x40,r6
L_0003bc36:
    mov #0x4,r5
L_0003bc38:
    mov r5,r0
L_0003bc3a:
    cmp/eq #0x4,r0
L_0003bc3c:
    bf L_0003bc42
L_0003bc3e:
    bra L_0003bc76
L_0003bc40:
    mov #0x0,r5
L_0003bc42:
    mov.l P_0003bdf4,r4
L_0003bc44:
    mov.b @(0x3,r4),r0
L_0003bc46:
    mov #0x7,r4
L_0003bc48:
    extu.b r0,r6
L_0003bc4a:
    cmp/ge r4,r6
L_0003bc4c:
    bt L_0003bc52
L_0003bc4e:
    bra L_0003bc66
L_0003bc50:
    mov #0x0,r6
L_0003bc52:
    mov #0xf,r4
L_0003bc54:
    cmp/ge r4,r6
L_0003bc56:
    bt L_0003bc5c
L_0003bc58:
    bra L_0003bc66
L_0003bc5a:
    mov #0x1,r6
L_0003bc5c:
    mov #0x16,r2
L_0003bc5e:
    cmp/ge r2,r6
L_0003bc60:
    bt/s L_0003bc66
L_0003bc62:
    mov #0x3,r6
L_0003bc64:
    mov #0x2,r6
L_0003bc66:
    mov r5,r0
L_0003bc68:
    add #-0x1,r0
L_0003bc6a:
    mov.l P_0003bdf8,r4
L_0003bc6c:
    shll2 r0
L_0003bc6e:
    add r6,r0
L_0003bc70:
    mov.b @(r0,r4),r6
L_0003bc72:
    extu.b r6,r5
L_0003bc74:
    shll8 r5
L_0003bc76:
    mov.l P_0003bdf0,r9
L_0003bc78:
    mov.l P_0003bdfc,r14
L_0003bc7a:
    mov r5,r0
L_0003bc7c:
    mov.l P_0003be00,r4
L_0003bc7e:
    mov.w r0,@(0x2,r9)
    .org 0x32698
P_0003bde4:
    .byte 0xff
P_0003bde5:
    .byte 0xff
P_0003bde6:
    .byte 0x11
P_0003bde7:
    .byte 0xd4
P_0003bde8:
    .byte 0x00
P_0003bde9:
    .byte 0x01
P_0003bdea:
    .byte 0x2c
P_0003bdeb:
    .byte 0x9e
P_0003bdec:
    .byte 0x00
P_0003bded:
    .byte 0x02
P_0003bdee:
    .byte 0x63
P_0003bdef:
    .byte 0x88
P_0003bdf0:
    .byte 0xff
P_0003bdf1:
    .byte 0xff
P_0003bdf2:
    .byte 0x10
P_0003bdf3:
    .byte 0x24
P_0003bdf4:
    .byte 0xff
P_0003bdf5:
    .byte 0xff
P_0003bdf6:
    .byte 0x10
P_0003bdf7:
    .byte 0x72
P_0003bdf8:
    .byte 0x00
P_0003bdf9:
    .byte 0x00
P_0003bdfa:
    .byte 0x97
P_0003bdfb:
    .byte 0x4e
P_0003bdfc:
    .byte 0xff
P_0003bdfd:
    .byte 0xff
P_0003bdfe:
    .byte 0x5b
P_0003bdff:
    .byte 0x2e
P_0003be00:
    .byte 0xff
P_0003be01:
    .byte 0xff
P_0003be02:
    .byte 0x24
P_0003be03:
    .byte 0xac
