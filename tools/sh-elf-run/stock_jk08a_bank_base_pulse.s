! Complete bank base-pulse function with natural stock return.
    .section .text
    .balign 4
    .org 0x893d - 0x893c
.byte 0x51
    .org 0x8940 - 0x893c
.byte 0x01
    .org 0x4ead4 - 0x893c
L_4ead4:
    sts.l macl,@-r15
    .org 0x4ead6 - 0x893c
L_4ead6:
    stc.l gbr,@-r15
    .org 0x4ead8 - 0x893c
L_4ead8:
    mov.l P_4ec08,r0
    .org 0x4eada - 0x893c
L_4eada:
    ldc r0,gbr
    .org 0x4eadc - 0x893c
L_4eadc:
    extu.b r4,r1
    .org 0x4eade - 0x893c
L_4eade:
    mov.l P_4ec18,r7
    .org 0x4eae0 - 0x893c
L_4eae0:
    stc gbr,r2
    .org 0x4eae2 - 0x893c
L_4eae2:
    shll r1
    .org 0x4eae4 - 0x893c
L_4eae4:
    mov r1,r0
    .org 0x4eae6 - 0x893c
L_4eae6:
    mov.w @(r0,r2),r5
    .org 0x4eae8 - 0x893c
L_4eae8:
    mov.l P_4ec00,r2
    .org 0x4eaea - 0x893c
L_4eaea:
    mov #0x4b,r6
    .org 0x4eaec - 0x893c
L_4eaec:
    shll2 r6
    .org 0x4eaee - 0x893c
L_4eaee:
    add r6,r2
    .org 0x4eaf0 - 0x893c
L_4eaf0:
    mov.w @(r0,r2),r6
    .org 0x4eaf2 - 0x893c
L_4eaf2:
    extu.w r5,r5
    .org 0x4eaf4 - 0x893c
L_4eaf4:
    mov.b @r7,r0
    .org 0x4eaf6 - 0x893c
L_4eaf6:
    tst #0x2,r0
    .org 0x4eaf8 - 0x893c
L_4eaf8:
    bt/s L_4eb0c
    .org 0x4eafa - 0x893c
L_4eafa:
    extu.w r6,r6
    .org 0x4eafc - 0x893c
L_4eafc:
    stc gbr,r2
    .org 0x4eafe - 0x893c
L_4eafe:
    add #0x26,r2
    .org 0x4eb00 - 0x893c
L_4eb00:
    mov r5,r4
    .org 0x4eb02 - 0x893c
L_4eb02:
    mov r1,r0
    .org 0x4eb04 - 0x893c
L_4eb04:
    mov.w @(r0,r2),r5
    .org 0x4eb06 - 0x893c
L_4eb06:
    extu.w r5,r5
    .org 0x4eb08 - 0x893c
L_4eb08:
    bra L_4eb48
    .org 0x4eb0a - 0x893c
L_4eb0a:
    add r5,r4
    .org 0x4eb0c - 0x893c
L_4eb0c:
    mov.b @(0x3,r7),r0
    .org 0x4eb0e - 0x893c
L_4eb0e:
    tst #0x10,r0
    .org 0x4eb10 - 0x893c
L_4eb10:
    bt L_4eb22
    .org 0x4eb12 - 0x893c
L_4eb12:
    mov.w @(0xc,gbr),r0
    .org 0x4eb14 - 0x893c
L_4eb14:
    mov #0x40,r4
    .org 0x4eb16 - 0x893c
L_4eb16:
    shll8 r4
    .org 0x4eb18 - 0x893c
L_4eb18:
    extu.w r0,r2
    .org 0x4eb1a - 0x893c
L_4eb1a:
    cmp/gt r4,r2
    .org 0x4eb1c - 0x893c
L_4eb1c:
    bt L_4eb2e
    .org 0x4eb1e - 0x893c
L_4eb1e:
    bra L_4eb3a
    .org 0x4eb20 - 0x893c
L_4eb20:
    nop
    .org 0x4eb22 - 0x893c
L_4eb22:
    mov.w @(0xa,gbr),r0
    .org 0x4eb24 - 0x893c
L_4eb24:
    mov #0x40,r4
    .org 0x4eb26 - 0x893c
L_4eb26:
    shll8 r4
    .org 0x4eb28 - 0x893c
L_4eb28:
    extu.w r0,r2
    .org 0x4eb2a - 0x893c
L_4eb2a:
    cmp/gt r4,r2
    .org 0x4eb2c - 0x893c
L_4eb2c:
    bf L_4eb3a
    .org 0x4eb2e - 0x893c
L_4eb2e:
    mov #-0x64,r2
    .org 0x4eb30 - 0x893c
L_4eb30:
    add r6,r5
    .org 0x4eb32 - 0x893c
L_4eb32:
    shll8 r2
    .org 0x4eb34 - 0x893c
L_4eb34:
    add r2,r5
    .org 0x4eb36 - 0x893c
L_4eb36:
    bra L_4eb4e
    .org 0x4eb38 - 0x893c
L_4eb38:
    mov r5,r4
    .org 0x4eb3a - 0x893c
L_4eb3a:
    mov r5,r4
    .org 0x4eb3c - 0x893c
L_4eb3c:
    mov r1,r0
    .org 0x4eb3e - 0x893c
L_4eb3e:
    stc gbr,r5
    .org 0x4eb40 - 0x893c
L_4eb40:
    add #0x26,r5
    .org 0x4eb42 - 0x893c
L_4eb42:
    mov.w @(r0,r5),r2
    .org 0x4eb44 - 0x893c
L_4eb44:
    extu.w r2,r2
    .org 0x4eb46 - 0x893c
L_4eb46:
    add r2,r4
    .org 0x4eb48 - 0x893c
L_4eb48:
    mov.l P_4ec1c,r2
    .org 0x4eb4a - 0x893c
L_4eb4a:
    add r6,r4
    .org 0x4eb4c - 0x893c
L_4eb4c:
    add r2,r4
    .org 0x4eb4e - 0x893c
L_4eb4e:
    cmp/pz r4
    .org 0x4eb50 - 0x893c
L_4eb50:
    bt L_4eb54
    .org 0x4eb52 - 0x893c
L_4eb52:
    mov #0x0,r4
    .org 0x4eb54 - 0x893c
L_4eb54:
    mov.l P_4ec04,r7
    .org 0x4eb56 - 0x893c
L_4eb56:
    mov r1,r0
    .org 0x4eb58 - 0x893c
L_4eb58:
    mov.w P_4ebe2,r6
    .org 0x4eb5a - 0x893c
L_4eb5a:
    mov r7,r2
    .org 0x4eb5c - 0x893c
L_4eb5c:
    add r6,r2
    .org 0x4eb5e - 0x893c
L_4eb5e:
    mov.w @(r0,r2),r6
    .org 0x4eb60 - 0x893c
L_4eb60:
    mov.w @(0x15a,gbr),r0
    .org 0x4eb62 - 0x893c
L_4eb62:
    extu.w r6,r6
    .org 0x4eb64 - 0x893c
L_4eb64:
    mul.l r4,r6
    .org 0x4eb66 - 0x893c
L_4eb66:
    extu.w r0,r5
    .org 0x4eb68 - 0x893c
L_4eb68:
    tst r6,r6
    .org 0x4eb6a - 0x893c
L_4eb6a:
    sts macl,r2
    .org 0x4eb6c - 0x893c
L_4eb6c:
    shlr16 r2
    .org 0x4eb6e - 0x893c
L_4eb6e:
    add r5,r2
    .org 0x4eb70 - 0x893c
L_4eb70:
    bt/s L_4eb8a
    .org 0x4eb72 - 0x893c
L_4eb72:
    mov r2,r5
    .org 0x4eb74 - 0x893c
L_4eb74:
    stc gbr,r6
    .org 0x4eb76 - 0x893c
L_4eb76:
    add #0x34,r6
    .org 0x4eb78 - 0x893c
L_4eb78:
    mov r1,r0
    .org 0x4eb7a - 0x893c
L_4eb7a:
    mov.w @(r0,r6),r2
    .org 0x4eb7c - 0x893c
L_4eb7c:
    shll8 r5
    .org 0x4eb7e - 0x893c
L_4eb7e:
    extu.w r2,r6
    .org 0x4eb80 - 0x893c
L_4eb80:
    mov #-0x80,r2
    .org 0x4eb82 - 0x893c
L_4eb82:
    shll8 r2
    .org 0x4eb84 - 0x893c
L_4eb84:
    add r2,r6
    .org 0x4eb86 - 0x893c
L_4eb86:
    add r6,r5
    .org 0x4eb88 - 0x893c
L_4eb88:
    shlr8 r5
    .org 0x4eb8a - 0x893c
L_4eb8a:
    mov #-0x1,r2
    .org 0x4eb8c - 0x893c
L_4eb8c:
    extu.w r2,r2
    .org 0x4eb8e - 0x893c
L_4eb8e:
    cmp/hi r2,r5
    .org 0x4eb90 - 0x893c
L_4eb90:
    bt L_4eb94
    .org 0x4eb92 - 0x893c
L_4eb92:
    mov r5,r2
    .org 0x4eb94 - 0x893c
L_4eb94:
    mov.w P_4ebe4,r6
    .org 0x4eb96 - 0x893c
L_4eb96:
    mov r1,r0
    .org 0x4eb98 - 0x893c
L_4eb98:
    add r6,r7
    .org 0x4eb9a - 0x893c
L_4eb9a:
    mov.w r2,@(r0,r7)
    .org 0x4eb9c - 0x893c
L_4eb9c:
    ldc.l @r15+,gbr
    .org 0x4eb9e - 0x893c
L_4eb9e:
    rts
    .org 0x4eba0 - 0x893c
L_4eba0:
    lds.l @r15+,macl
    .org 0x4ebe2 - 0x893c
P_4ebe2: .word 0x634
    .org 0x4ebe4 - 0x893c
P_4ebe4: .word 0x690
    .org 0x4ec00 - 0x893c
P_4ec00: .long 0xffff28f8
    .org 0x4ec04 - 0x893c
P_4ec04: .long 0xffff128c
    .org 0x4ec08 - 0x893c
P_4ec08: .long 0xffff22dc
    .org 0x4ec18 - 0x893c
P_4ec18: .long 0x893d
    .org 0x4ec1c - 0x893c
P_4ec1c: .long 0xffff3800
