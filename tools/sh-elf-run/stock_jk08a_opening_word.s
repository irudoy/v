! Stock opening word and actual signed arithmetic-shift helper.
    .text
    .balign 4
    .org 0x84f6 - 0x84f4
L_000084f6:
    .byte 0x5c
    .org 0x8c9e - 0x84f4
L_00008c9e:
    .byte 0x46
    .org 0x224f8 - 0x84f4
L_000224f8:
    shar r0
    .org 0x224fa - 0x84f4
L_000224fa:
    shar r0
    .org 0x224fc - 0x84f4
L_000224fc:
    shar r0
    .org 0x224fe - 0x84f4
L_000224fe:
    shar r0
    .org 0x22500 - 0x84f4
L_00022500:
    shar r0
    .org 0x22502 - 0x84f4
L_00022502:
    shar r0
    .org 0x22504 - 0x84f4
L_00022504:
    rts
    .org 0x22506 - 0x84f4
L_00022506:
    shar r0
    .org 0x56fc0 - 0x84f4
L_00056fc0:
    mov.l r14,@-r15
    .org 0x56fc2 - 0x84f4
L_00056fc2:
    sts.l pr,@-r15
    .org 0x56fc4 - 0x84f4
L_00056fc4:
    sts.l macl,@-r15
    .org 0x56fc6 - 0x84f4
L_00056fc6:
    mov.l L_0005700c,r2
    .org 0x56fc8 - 0x84f4
L_00056fc8:
    mov #0x74,r0
    .org 0x56fca - 0x84f4
L_00056fca:
    mov.l L_00057010,r5
    .org 0x56fcc - 0x84f4
L_00056fcc:
    mov.b @(r0,r2),r6
    .org 0x56fce - 0x84f4
L_00056fce:
    mov #-0x51,r2
    .org 0x56fd0 - 0x84f4
L_00056fd0:
    extu.b r2,r2
    .org 0x56fd2 - 0x84f4
L_00056fd2:
    extu.b r6,r6
    .org 0x56fd4 - 0x84f4
L_00056fd4:
    sub r6,r2
    .org 0x56fd6 - 0x84f4
L_00056fd6:
    mov.b @r5,r6
    .org 0x56fd8 - 0x84f4
L_00056fd8:
    mov.l L_00057014,r5
    .org 0x56fda - 0x84f4
L_00056fda:
    extu.b r6,r6
    .org 0x56fdc - 0x84f4
L_00056fdc:
    mul.l r2,r6
    .org 0x56fde - 0x84f4
L_00056fde:
    mov.b @r5,r14
    .org 0x56fe0 - 0x84f4
L_00056fe0:
    mov.l L_00057018,r6
    .org 0x56fe2 - 0x84f4
L_00056fe2:
    sts macl,r0
    .org 0x56fe4 - 0x84f4
L_00056fe4:
    jsr @r6
    .org 0x56fe6 - 0x84f4
L_00056fe6:
    extu.b r14,r14
    .org 0x56fe8 - 0x84f4
L_00056fe8:
    add r14,r0
    .org 0x56fea - 0x84f4
L_00056fea:
    cmp/pz r0
    .org 0x56fec - 0x84f4
L_00056fec:
    bt/s L_00056ff2
    .org 0x56fee - 0x84f4
L_00056fee:
    mov r0,r6
    .org 0x56ff0 - 0x84f4
L_00056ff0:
    mov #0x0,r6
    .org 0x56ff2 - 0x84f4
L_00056ff2:
    mov #-0x1,r2
    .org 0x56ff4 - 0x84f4
L_00056ff4:
    extu.w r2,r2
    .org 0x56ff6 - 0x84f4
L_00056ff6:
    cmp/gt r2,r6
    .org 0x56ff8 - 0x84f4
L_00056ff8:
    bt L_00056ffc
    .org 0x56ffa - 0x84f4
L_00056ffa:
    mov r6,r2
    .org 0x56ffc - 0x84f4
L_00056ffc:
    mov r2,r6
    .org 0x56ffe - 0x84f4
L_00056ffe:
    mov.l L_0005701c,r2
    .org 0x57000 - 0x84f4
L_00057000:
    mov #0x7a,r0
    .org 0x57002 - 0x84f4
L_00057002:
    mov.w r6,@(r0,r2)
    .org 0x57004 - 0x84f4
L_00057004:
    lds.l @r15+,macl
    .org 0x57006 - 0x84f4
L_00057006:
    lds.l @r15+,pr
    .org 0x57008 - 0x84f4
L_00057008:
    rts
    .org 0x5700a - 0x84f4
L_0005700a:
    mov.l @r15+,r14
    .org 0x5700c - 0x84f4
L_0005700c:
    .long 0xffff1094
    .org 0x57010 - 0x84f4
L_00057010:
    .long 0x000084f6
    .org 0x57014 - 0x84f4
L_00057014:
    .long 0x00008c9e
    .org 0x57018 - 0x84f4
L_00057018:
    .long 0x000224f8
    .org 0x5701c - 0x84f4
L_0005701c:
    .long 0xffff23bc
