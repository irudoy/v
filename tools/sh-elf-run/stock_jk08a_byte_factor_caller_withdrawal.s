! Complete natural4BA48 byte-factor caller and exact implicit-byte-curve helpers.
! The26A80 entry is bound inside its complete normal26A60 exported parent.
    .text
    .balign 4
    .set ORIGIN,0x8868
    .org 0x886b-ORIGIN
P_0000886b:
    .byte 0x00
    .org 0x886d-ORIGIN
P_0000886d:
    .byte 0x00
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
    .org 0x4ba48-ORIGIN
L_0004ba48:
    mov.l r13,@-r15
    .org 0x4ba4a-ORIGIN
L_0004ba4a:
    mov.l r14,@-r15
    .org 0x4ba4c-ORIGIN
L_0004ba4c:
    sts.l pr,@-r15
    .org 0x4ba4e-ORIGIN
L_0004ba4e:
    sts.l macl,@-r15
    .org 0x4ba50-ORIGIN
L_0004ba50:
    mov.l P_0004bc64,r6
    .org 0x4ba52-ORIGIN
L_0004ba52:
    mov.l P_0004bc44,r13
    .org 0x4ba54-ORIGIN
L_0004ba54:
    mov.b @(0x8,r6),r0
    .org 0x4ba56-ORIGIN
L_0004ba56:
    tst #0x2,r0
    .org 0x4ba58-ORIGIN
L_0004ba58:
    bt L_0004ba7a
    .org 0x4ba5a-ORIGIN
L_0004ba5a:
    mov.w P_0004ba62,r0
    .org 0x4ba5c-ORIGIN
L_0004ba5c:
    mov.l P_0004bc6c,r5
    .org 0x4ba5e-ORIGIN
L_0004ba5e:
    bra L_0004ba64
    .org 0x4ba60-ORIGIN
L_0004ba60:
    nop
    .org 0x4ba62-ORIGIN
P_0004ba62:
    .byte 0x03
    .org 0x4ba63-ORIGIN
P_0004ba63:
    .byte 0xcb
    .org 0x4ba64-ORIGIN
L_0004ba64:
    mov.b @(r0,r13),r6
    .org 0x4ba66-ORIGIN
L_0004ba66:
    mov.b @(0x2,r5),r0
    .org 0x4ba68-ORIGIN
L_0004ba68:
    extu.b r6,r6
    .org 0x4ba6a-ORIGIN
L_0004ba6a:
    extu.b r0,r2
    .org 0x4ba6c-ORIGIN
L_0004ba6c:
    shll r2
    .org 0x4ba6e-ORIGIN
L_0004ba6e:
    sub r2,r6
    .org 0x4ba70-ORIGIN
L_0004ba70:
    exts.w r6,r2
    .org 0x4ba72-ORIGIN
L_0004ba72:
    cmp/pz r2
    .org 0x4ba74-ORIGIN
L_0004ba74:
    bt L_0004bb5c
    .org 0x4ba76-ORIGIN
L_0004ba76:
    bra L_0004bb5c
    .org 0x4ba78-ORIGIN
L_0004ba78:
    mov #0x0,r2
    .org 0x4ba7a-ORIGIN
L_0004ba7a:
    mov.w P_0004bba2,r0
    .org 0x4ba7c-ORIGIN
L_0004ba7c:
    mov.w @(r0,r13),r2
    .org 0x4ba7e-ORIGIN
L_0004ba7e:
    mov.w P_0004bba4,r0
    .org 0x4ba80-ORIGIN
L_0004ba80:
    extu.w r2,r2
    .org 0x4ba82-ORIGIN
L_0004ba82:
    mov.w @(r0,r13),r6
    .org 0x4ba84-ORIGIN
L_0004ba84:
    sub r6,r2
    .org 0x4ba86-ORIGIN
L_0004ba86:
    cmp/pz r2
    .org 0x4ba88-ORIGIN
L_0004ba88:
    bt L_0004ba8c
    .org 0x4ba8a-ORIGIN
L_0004ba8a:
    mov #0x0,r2
    .org 0x4ba8c-ORIGIN
L_0004ba8c:
    mov.l P_0004bc70,r6
    .org 0x4ba8e-ORIGIN
L_0004ba8e:
    mov r2,r14
    .org 0x4ba90-ORIGIN
L_0004ba90:
    mov.b @r6,r2
    .org 0x4ba92-ORIGIN
L_0004ba92:
    extu.b r2,r0
    .org 0x4ba94-ORIGIN
L_0004ba94:
    tst #0x20,r0
    .org 0x4ba96-ORIGIN
L_0004ba96:
    bt L_0004bac0
    .org 0x4ba98-ORIGIN
L_0004ba98:
    mov.l P_0004bc6c,r5
    .org 0x4ba9a-ORIGIN
L_0004ba9a:
    mov.b @r5,r6
    .org 0x4ba9c-ORIGIN
L_0004ba9c:
    extu.b r6,r2
    .org 0x4ba9e-ORIGIN
L_0004ba9e:
    mul.l r2,r14
    .org 0x4baa0-ORIGIN
L_0004baa0:
    mov #0x64,r6
    .org 0x4baa2-ORIGIN
L_0004baa2:
    sts macl,r2
    .org 0x4baa4-ORIGIN
L_0004baa4:
    mul.l r2,r6
    .org 0x4baa6-ORIGIN
L_0004baa6:
    mov #-0x1,r2
    .org 0x4baa8-ORIGIN
L_0004baa8:
    extu.b r2,r2
    .org 0x4baaa-ORIGIN
L_0004baaa:
    sts macl,r6
    .org 0x4baac-ORIGIN
L_0004baac:
    shlr8 r6
    .org 0x4baae-ORIGIN
L_0004baae:
    shlr2 r6
    .org 0x4bab0-ORIGIN
L_0004bab0:
    shlr2 r6
    .org 0x4bab2-ORIGIN
L_0004bab2:
    shlr2 r6
    .org 0x4bab4-ORIGIN
L_0004bab4:
    cmp/hi r2,r6
    .org 0x4bab6-ORIGIN
L_0004bab6:
    bf L_0004baba
    .org 0x4bab8-ORIGIN
L_0004bab8:
    mov #-0x1,r6
    .org 0x4baba-ORIGIN
L_0004baba:
    mov.w P_0004bba6,r0
    .org 0x4babc-ORIGIN
L_0004babc:
    bra L_0004bb60
    .org 0x4babe-ORIGIN
L_0004babe:
    mov.b r6,@(r0,r13)
    .org 0x4bac0-ORIGIN
L_0004bac0:
    mov.l P_0004bc48,r2
    .org 0x4bac2-ORIGIN
L_0004bac2:
    mov #-0x1,r5
    .org 0x4bac4-ORIGIN
L_0004bac4:
    extu.b r5,r5
    .org 0x4bac6-ORIGIN
L_0004bac6:
    mov.w @r2,r6
    .org 0x4bac8-ORIGIN
L_0004bac8:
    extu.w r6,r2
    .org 0x4baca-ORIGIN
L_0004baca:
    shlr2 r2
    .org 0x4bacc-ORIGIN
L_0004bacc:
    shlr2 r2
    .org 0x4bace-ORIGIN
L_0004bace:
    shlr2 r2
    .org 0x4bad0-ORIGIN
L_0004bad0:
    shlr r2
    .org 0x4bad2-ORIGIN
L_0004bad2:
    cmp/gt r5,r2
    .org 0x4bad4-ORIGIN
L_0004bad4:
    bt L_0004bad8
    .org 0x4bad6-ORIGIN
L_0004bad6:
    mov r2,r5
    .org 0x4bad8-ORIGIN
L_0004bad8:
    mov.l P_0004bc74,r4
    .org 0x4bada-ORIGIN
L_0004bada:
    extu.b r5,r5
    .org 0x4badc-ORIGIN
L_0004badc:
    mov.l P_0004bc50,r7
    .org 0x4bade-ORIGIN
L_0004bade:
    jsr @r7
    .org 0x4bae0-ORIGIN
L_0004bae0:
    add #0x8,r4
    .org 0x4bae2-ORIGIN
L_0004bae2:
    mov r0,r2
    .org 0x4bae4-ORIGIN
L_0004bae4:
    mov.w P_0004bba8,r0
    .org 0x4bae6-ORIGIN
L_0004bae6:
    mov.b r2,@(r0,r13)
    .org 0x4bae8-ORIGIN
L_0004bae8:
    mov #0x20,r0
    .org 0x4baea-ORIGIN
L_0004baea:
    mov.l P_0004bc54,r2
    .org 0x4baec-ORIGIN
L_0004baec:
    mov.w @(r0,r2),r6
    .org 0x4baee-ORIGIN
L_0004baee:
    extu.w r6,r5
    .org 0x4baf0-ORIGIN
L_0004baf0:
    mov r5,r2
    .org 0x4baf2-ORIGIN
L_0004baf2:
    add #-0x20,r2
    .org 0x4baf4-ORIGIN
L_0004baf4:
    cmp/pz r2
    .org 0x4baf6-ORIGIN
L_0004baf6:
    bt L_0004bafc
    .org 0x4baf8-ORIGIN
L_0004baf8:
    bra L_0004bafe
    .org 0x4bafa-ORIGIN
L_0004bafa:
    mov #0x0,r5
    .org 0x4bafc-ORIGIN
L_0004bafc:
    add #-0x20,r5
    .org 0x4bafe-ORIGIN
L_0004bafe:
    mov #-0x1,r2
    .org 0x4bb00-ORIGIN
L_0004bb00:
    extu.b r2,r2
    .org 0x4bb02-ORIGIN
L_0004bb02:
    cmp/hi r2,r5
    .org 0x4bb04-ORIGIN
L_0004bb04:
    bf L_0004bb08
    .org 0x4bb06-ORIGIN
L_0004bb06:
    mov #-0x1,r5
    .org 0x4bb08-ORIGIN
L_0004bb08:
    mov.l P_0004bc74,r4
    .org 0x4bb0a-ORIGIN
L_0004bb0a:
    mov.l P_0004bc50,r7
    .org 0x4bb0c-ORIGIN
L_0004bb0c:
    jsr @r7
    .org 0x4bb0e-ORIGIN
L_0004bb0e:
    extu.b r5,r5
    .org 0x4bb10-ORIGIN
L_0004bb10:
    mov r0,r2
    .org 0x4bb12-ORIGIN
L_0004bb12:
    mov.w P_0004bbaa,r0
    .org 0x4bb14-ORIGIN
L_0004bb14:
    mov.b r2,@(r0,r13)
    .org 0x4bb16-ORIGIN
L_0004bb16:
    extu.b r2,r2
    .org 0x4bb18-ORIGIN
L_0004bb18:
    mov.w P_0004bba8,r0
    .org 0x4bb1a-ORIGIN
L_0004bb1a:
    mov.b @(r0,r13),r5
    .org 0x4bb1c-ORIGIN
L_0004bb1c:
    extu.b r5,r6
    .org 0x4bb1e-ORIGIN
L_0004bb1e:
    mulu.w r6,r2
    .org 0x4bb20-ORIGIN
L_0004bb20:
    mov #0x64,r6
    .org 0x4bb22-ORIGIN
L_0004bb22:
    sts macl,r2
    .org 0x4bb24-ORIGIN
L_0004bb24:
    mul.l r14,r6
    .org 0x4bb26-ORIGIN
L_0004bb26:
    extu.w r2,r2
    .org 0x4bb28-ORIGIN
L_0004bb28:
    sts macl,r5
    .org 0x4bb2a-ORIGIN
L_0004bb2a:
    extu.w r5,r6
    .org 0x4bb2c-ORIGIN
L_0004bb2c:
    mul.l r2,r6
    .org 0x4bb2e-ORIGIN
L_0004bb2e:
    shlr16 r5
    .org 0x4bb30-ORIGIN
L_0004bb30:
    extu.w r5,r5
    .org 0x4bb32-ORIGIN
L_0004bb32:
    sts macl,r4
    .org 0x4bb34-ORIGIN
L_0004bb34:
    mul.l r2,r5
    .org 0x4bb36-ORIGIN
L_0004bb36:
    mov #-0x1,r6
    .org 0x4bb38-ORIGIN
L_0004bb38:
    extu.w r6,r6
    .org 0x4bb3a-ORIGIN
L_0004bb3a:
    sts macl,r2
    .org 0x4bb3c-ORIGIN
L_0004bb3c:
    shlr16 r4
    .org 0x4bb3e-ORIGIN
L_0004bb3e:
    cmp/hi r6,r2
    .org 0x4bb40-ORIGIN
L_0004bb40:
    bt L_0004bb44
    .org 0x4bb42-ORIGIN
L_0004bb42:
    mov r2,r6
    .org 0x4bb44-ORIGIN
L_0004bb44:
    extu.w r4,r4
    .org 0x4bb46-ORIGIN
L_0004bb46:
    extu.w r6,r2
    .org 0x4bb48-ORIGIN
L_0004bb48:
    add r2,r4
    .org 0x4bb4a-ORIGIN
L_0004bb4a:
    shlr2 r4
    .org 0x4bb4c-ORIGIN
L_0004bb4c:
    shlr2 r4
    .org 0x4bb4e-ORIGIN
L_0004bb4e:
    mov #-0x1,r6
    .org 0x4bb50-ORIGIN
L_0004bb50:
    shlr r4
    .org 0x4bb52-ORIGIN
L_0004bb52:
    extu.b r6,r6
    .org 0x4bb54-ORIGIN
L_0004bb54:
    cmp/hi r6,r4
    .org 0x4bb56-ORIGIN
L_0004bb56:
    bf/s L_0004bb5c
    .org 0x4bb58-ORIGIN
L_0004bb58:
    mov r4,r2
    .org 0x4bb5a-ORIGIN
L_0004bb5a:
    mov #-0x1,r2
    .org 0x4bb5c-ORIGIN
L_0004bb5c:
    mov.w P_0004bba6,r0
    .org 0x4bb5e-ORIGIN
L_0004bb5e:
    mov.b r2,@(r0,r13)
    .org 0x4bb60-ORIGIN
L_0004bb60:
    lds.l @r15+,macl
    .org 0x4bb62-ORIGIN
L_0004bb62:
    lds.l @r15+,pr
    .org 0x4bb64-ORIGIN
L_0004bb64:
    mov.l @r15+,r14
    .org 0x4bb66-ORIGIN
L_0004bb66:
    rts
    .org 0x4bb68-ORIGIN
L_0004bb68:
    mov.l @r15+,r13
    .org 0x4bba2-ORIGIN
P_0004bba2:
    .byte 0x03
    .org 0x4bba3-ORIGIN
P_0004bba3:
    .byte 0x70
    .org 0x4bba4-ORIGIN
P_0004bba4:
    .byte 0x03
    .org 0x4bba5-ORIGIN
P_0004bba5:
    .byte 0x72
    .org 0x4bba6-ORIGIN
P_0004bba6:
    .byte 0x03
    .org 0x4bba7-ORIGIN
P_0004bba7:
    .byte 0xcb
    .org 0x4bba8-ORIGIN
P_0004bba8:
    .byte 0x03
    .org 0x4bba9-ORIGIN
P_0004bba9:
    .byte 0xcd
    .org 0x4bbaa-ORIGIN
P_0004bbaa:
    .byte 0x03
    .org 0x4bbab-ORIGIN
P_0004bbab:
    .byte 0xcc
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
    .org 0x4bc48-ORIGIN
P_0004bc48:
    .byte 0xff
    .org 0x4bc49-ORIGIN
P_0004bc49:
    .byte 0xff
    .org 0x4bc4a-ORIGIN
P_0004bc4a:
    .byte 0x10
    .org 0x4bc4b-ORIGIN
P_0004bc4b:
    .byte 0x24
    .org 0x4bc50-ORIGIN
P_0004bc50:
    .byte 0x00
    .org 0x4bc51-ORIGIN
P_0004bc51:
    .byte 0x02
    .org 0x4bc52-ORIGIN
P_0004bc52:
    .byte 0x63
    .org 0x4bc53-ORIGIN
P_0004bc53:
    .byte 0x70
    .org 0x4bc54-ORIGIN
P_0004bc54:
    .byte 0xff
    .org 0x4bc55-ORIGIN
P_0004bc55:
    .byte 0xff
    .org 0x4bc56-ORIGIN
P_0004bc56:
    .byte 0x11
    .org 0x4bc57-ORIGIN
P_0004bc57:
    .byte 0x9c
    .org 0x4bc64-ORIGIN
P_0004bc64:
    .byte 0xff
    .org 0x4bc65-ORIGIN
P_0004bc65:
    .byte 0xff
    .org 0x4bc66-ORIGIN
P_0004bc66:
    .byte 0x24
    .org 0x4bc67-ORIGIN
P_0004bc67:
    .byte 0x70
    .org 0x4bc6c-ORIGIN
P_0004bc6c:
    .byte 0x00
    .org 0x4bc6d-ORIGIN
P_0004bc6d:
    .byte 0x00
    .org 0x4bc6e-ORIGIN
P_0004bc6e:
    .byte 0x88
    .org 0x4bc6f-ORIGIN
P_0004bc6f:
    .byte 0x6b
    .org 0x4bc70-ORIGIN
P_0004bc70:
    .byte 0xff
    .org 0x4bc71-ORIGIN
P_0004bc71:
    .byte 0xff
    .org 0x4bc72-ORIGIN
P_0004bc72:
    .byte 0x24
    .org 0x4bc73-ORIGIN
P_0004bc73:
    .byte 0x58
    .org 0x4bc74-ORIGIN
P_0004bc74:
    .byte 0x00
    .org 0x4bc75-ORIGIN
P_0004bc75:
    .byte 0x01
    .org 0x4bc76-ORIGIN
P_0004bc76:
    .byte 0x26
    .org 0x4bc77-ORIGIN
P_0004bc77:
    .byte 0xa0
