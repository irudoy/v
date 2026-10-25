! Full JK08A BFS producer and declared natural helper instructions.
! All tested words and natural returns retain stock bytes; no helper is stubbed.
    .text
    .balign 4
    .set ORIGIN,0x21ce0
    .org 0x21ce0-ORIGIN
L_00021ce0:
    mov.l r2,@-r15
    .org 0x21ce2-ORIGIN
L_00021ce2:
    tst r0,r0
    .org 0x21ce4-ORIGIN
L_00021ce4:
    bt L_00021d6a
    .org 0x21ce6-ORIGIN
L_00021ce6:
    extu.w r0,r2
    .org 0x21ce8-ORIGIN
L_00021ce8:
    cmp/eq r2,r0
    .org 0x21cea-ORIGIN
L_00021cea:
    bf L_00021d76
    .org 0x21cec-ORIGIN
L_00021cec:
    div0u
    .org 0x21cee-ORIGIN
L_00021cee:
    shll8 r0
    .org 0x21cf0-ORIGIN
L_00021cf0:
    cmp/hi r1,r0
    .org 0x21cf2-ORIGIN
L_00021cf2:
    bf L_00021d0c
    .org 0x21cf4-ORIGIN
L_00021cf4:
    div1 r0,r1
    .org 0x21cf6-ORIGIN
L_00021cf6:
    div1 r0,r1
    .org 0x21cf8-ORIGIN
L_00021cf8:
    div1 r0,r1
    .org 0x21cfa-ORIGIN
L_00021cfa:
    div1 r0,r1
    .org 0x21cfc-ORIGIN
L_00021cfc:
    div1 r0,r1
    .org 0x21cfe-ORIGIN
L_00021cfe:
    div1 r0,r1
    .org 0x21d00-ORIGIN
L_00021d00:
    div1 r0,r1
    .org 0x21d02-ORIGIN
L_00021d02:
    div1 r0,r1
    .org 0x21d04-ORIGIN
L_00021d04:
    rotcl r1
    .org 0x21d06-ORIGIN
L_00021d06:
    mov.l @r15+,r2
    .org 0x21d08-ORIGIN
L_00021d08:
    rts
    .org 0x21d0a-ORIGIN
L_00021d0a:
    extu.b r1,r0
    .org 0x21d0c-ORIGIN
L_00021d0c:
    mov.l r3,@-r15
    .org 0x21d0e-ORIGIN
L_00021d0e:
    extu.w r1,r3
    .org 0x21d10-ORIGIN
L_00021d10:
    shll8 r0
    .org 0x21d12-ORIGIN
L_00021d12:
    shlr16 r1
    .org 0x21d14-ORIGIN
L_00021d14:
    div1 r0,r1
    .org 0x21d16-ORIGIN
L_00021d16:
    div1 r0,r1
    .org 0x21d18-ORIGIN
L_00021d18:
    div1 r0,r1
    .org 0x21d1a-ORIGIN
L_00021d1a:
    div1 r0,r1
    .org 0x21d1c-ORIGIN
L_00021d1c:
    div1 r0,r1
    .org 0x21d1e-ORIGIN
L_00021d1e:
    div1 r0,r1
    .org 0x21d20-ORIGIN
L_00021d20:
    div1 r0,r1
    .org 0x21d22-ORIGIN
L_00021d22:
    div1 r0,r1
    .org 0x21d24-ORIGIN
L_00021d24:
    div1 r0,r1
    .org 0x21d26-ORIGIN
L_00021d26:
    div1 r0,r1
    .org 0x21d28-ORIGIN
L_00021d28:
    div1 r0,r1
    .org 0x21d2a-ORIGIN
L_00021d2a:
    div1 r0,r1
    .org 0x21d2c-ORIGIN
L_00021d2c:
    div1 r0,r1
    .org 0x21d2e-ORIGIN
L_00021d2e:
    div1 r0,r1
    .org 0x21d30-ORIGIN
L_00021d30:
    div1 r0,r1
    .org 0x21d32-ORIGIN
L_00021d32:
    div1 r0,r1
    .org 0x21d34-ORIGIN
L_00021d34:
    extu.w r1,r2
    .org 0x21d36-ORIGIN
L_00021d36:
    xor r2,r1
    .org 0x21d38-ORIGIN
L_00021d38:
    addc r2,r2
    .org 0x21d3a-ORIGIN
L_00021d3a:
    shll16 r2
    .org 0x21d3c-ORIGIN
L_00021d3c:
    add r3,r1
    .org 0x21d3e-ORIGIN
L_00021d3e:
    div1 r0,r1
    .org 0x21d40-ORIGIN
L_00021d40:
    div1 r0,r1
    .org 0x21d42-ORIGIN
L_00021d42:
    div1 r0,r1
    .org 0x21d44-ORIGIN
L_00021d44:
    div1 r0,r1
    .org 0x21d46-ORIGIN
L_00021d46:
    div1 r0,r1
    .org 0x21d48-ORIGIN
L_00021d48:
    div1 r0,r1
    .org 0x21d4a-ORIGIN
L_00021d4a:
    div1 r0,r1
    .org 0x21d4c-ORIGIN
L_00021d4c:
    div1 r0,r1
    .org 0x21d4e-ORIGIN
L_00021d4e:
    div1 r0,r1
    .org 0x21d50-ORIGIN
L_00021d50:
    div1 r0,r1
    .org 0x21d52-ORIGIN
L_00021d52:
    div1 r0,r1
    .org 0x21d54-ORIGIN
L_00021d54:
    div1 r0,r1
    .org 0x21d56-ORIGIN
L_00021d56:
    div1 r0,r1
    .org 0x21d58-ORIGIN
L_00021d58:
    div1 r0,r1
    .org 0x21d5a-ORIGIN
L_00021d5a:
    div1 r0,r1
    .org 0x21d5c-ORIGIN
L_00021d5c:
    div1 r0,r1
    .org 0x21d5e-ORIGIN
L_00021d5e:
    rotcl r1
    .org 0x21d60-ORIGIN
L_00021d60:
    extu.w r1,r0
    .org 0x21d62-ORIGIN
L_00021d62:
    add r2,r0
    .org 0x21d64-ORIGIN
L_00021d64:
    mov.l @r15+,r3
    .org 0x21d66-ORIGIN
L_00021d66:
    rts
    .org 0x21d68-ORIGIN
L_00021d68:
    mov.l @r15+,r2
    .org 0x21d6a-ORIGIN
L_00021d6a:
    mov.l L_00021dc8,r1
    .org 0x21d6c-ORIGIN
L_00021d6c:
    mov.l L_00021dcc,r2
    .org 0x21d6e-ORIGIN
L_00021d6e:
    mov.l r2,@r1
    .org 0x21d70-ORIGIN
L_00021d70:
    mov #0x0,r0
    .org 0x21d72-ORIGIN
L_00021d72:
    rts
    .org 0x21d74-ORIGIN
L_00021d74:
    mov.l @r15+,r2
    .org 0x21d76-ORIGIN
L_00021d76:
    div0u
    .org 0x21d78-ORIGIN
L_00021d78:
    extu.w r1,r2
    .org 0x21d7a-ORIGIN
L_00021d7a:
    shll16 r2
    .org 0x21d7c-ORIGIN
L_00021d7c:
    shlr16 r1
    .org 0x21d7e-ORIGIN
L_00021d7e:
    rotcl r2
    .org 0x21d80-ORIGIN
L_00021d80:
    div1 r0,r1
    .org 0x21d82-ORIGIN
L_00021d82:
    rotcl r2
    .org 0x21d84-ORIGIN
L_00021d84:
    div1 r0,r1
    .org 0x21d86-ORIGIN
L_00021d86:
    rotcl r2
    .org 0x21d88-ORIGIN
L_00021d88:
    div1 r0,r1
    .org 0x21d8a-ORIGIN
L_00021d8a:
    rotcl r2
    .org 0x21d8c-ORIGIN
L_00021d8c:
    div1 r0,r1
    .org 0x21d8e-ORIGIN
L_00021d8e:
    rotcl r2
    .org 0x21d90-ORIGIN
L_00021d90:
    div1 r0,r1
    .org 0x21d92-ORIGIN
L_00021d92:
    rotcl r2
    .org 0x21d94-ORIGIN
L_00021d94:
    div1 r0,r1
    .org 0x21d96-ORIGIN
L_00021d96:
    rotcl r2
    .org 0x21d98-ORIGIN
L_00021d98:
    div1 r0,r1
    .org 0x21d9a-ORIGIN
L_00021d9a:
    rotcl r2
    .org 0x21d9c-ORIGIN
L_00021d9c:
    div1 r0,r1
    .org 0x21d9e-ORIGIN
L_00021d9e:
    rotcl r2
    .org 0x21da0-ORIGIN
L_00021da0:
    div1 r0,r1
    .org 0x21da2-ORIGIN
L_00021da2:
    rotcl r2
    .org 0x21da4-ORIGIN
L_00021da4:
    div1 r0,r1
    .org 0x21da6-ORIGIN
L_00021da6:
    rotcl r2
    .org 0x21da8-ORIGIN
L_00021da8:
    div1 r0,r1
    .org 0x21daa-ORIGIN
L_00021daa:
    rotcl r2
    .org 0x21dac-ORIGIN
L_00021dac:
    div1 r0,r1
    .org 0x21dae-ORIGIN
L_00021dae:
    rotcl r2
    .org 0x21db0-ORIGIN
L_00021db0:
    div1 r0,r1
    .org 0x21db2-ORIGIN
L_00021db2:
    rotcl r2
    .org 0x21db4-ORIGIN
L_00021db4:
    div1 r0,r1
    .org 0x21db6-ORIGIN
L_00021db6:
    rotcl r2
    .org 0x21db8-ORIGIN
L_00021db8:
    div1 r0,r1
    .org 0x21dba-ORIGIN
L_00021dba:
    rotcl r2
    .org 0x21dbc-ORIGIN
L_00021dbc:
    div1 r0,r1
    .org 0x21dbe-ORIGIN
L_00021dbe:
    rotcl r2
    .org 0x21dc0-ORIGIN
L_00021dc0:
    mov r2,r0
    .org 0x21dc2-ORIGIN
L_00021dc2:
    rts
    .org 0x21dc4-ORIGIN
L_00021dc4:
    mov.l @r15+,r2
    .org 0x21dc8-ORIGIN
L_00021dc8:
    .long 0xffff9818
    .org 0x21dcc-ORIGIN
L_00021dcc:
    .long 0x0000044e
    .org 0x21f40-ORIGIN
L_00021f40:
    mov.l r2,@-r15
    .org 0x21f42-ORIGIN
L_00021f42:
    tst r0,r0
    .org 0x21f44-ORIGIN
L_00021f44:
    bt L_00021fd0
    .org 0x21f46-ORIGIN
L_00021f46:
    extu.w r0,r2
    .org 0x21f48-ORIGIN
L_00021f48:
    cmp/eq r2,r0
    .org 0x21f4a-ORIGIN
L_00021f4a:
    bf L_00021fdc
    .org 0x21f4c-ORIGIN
L_00021f4c:
    div0u
    .org 0x21f4e-ORIGIN
L_00021f4e:
    shll8 r0
    .org 0x21f50-ORIGIN
L_00021f50:
    cmp/hi r1,r0
    .org 0x21f52-ORIGIN
L_00021f52:
    bf L_00021f72
    .org 0x21f54-ORIGIN
L_00021f54:
    div1 r0,r1
    .org 0x21f56-ORIGIN
L_00021f56:
    div1 r0,r1
    .org 0x21f58-ORIGIN
L_00021f58:
    div1 r0,r1
    .org 0x21f5a-ORIGIN
L_00021f5a:
    div1 r0,r1
    .org 0x21f5c-ORIGIN
L_00021f5c:
    div1 r0,r1
    .org 0x21f5e-ORIGIN
L_00021f5e:
    div1 r0,r1
    .org 0x21f60-ORIGIN
L_00021f60:
    div1 r0,r1
    .org 0x21f62-ORIGIN
L_00021f62:
    div1 r0,r1
    .org 0x21f64-ORIGIN
L_00021f64:
    mov r1,r2
    .org 0x21f66-ORIGIN
L_00021f66:
    bt L_00021f6a
    .org 0x21f68-ORIGIN
L_00021f68:
    add r0,r2
    .org 0x21f6a-ORIGIN
L_00021f6a:
    shlr8 r2
    .org 0x21f6c-ORIGIN
L_00021f6c:
    mov r2,r0
    .org 0x21f6e-ORIGIN
L_00021f6e:
    rts
    .org 0x21f70-ORIGIN
L_00021f70:
    mov.l @r15+,r2
    .org 0x21f72-ORIGIN
L_00021f72:
    mov.l r3,@-r15
    .org 0x21f74-ORIGIN
L_00021f74:
    extu.w r1,r3
    .org 0x21f76-ORIGIN
L_00021f76:
    shll8 r0
    .org 0x21f78-ORIGIN
L_00021f78:
    shlr16 r1
    .org 0x21f7a-ORIGIN
L_00021f7a:
    div1 r0,r1
    .org 0x21f7c-ORIGIN
L_00021f7c:
    div1 r0,r1
    .org 0x21f7e-ORIGIN
L_00021f7e:
    div1 r0,r1
    .org 0x21f80-ORIGIN
L_00021f80:
    div1 r0,r1
    .org 0x21f82-ORIGIN
L_00021f82:
    div1 r0,r1
    .org 0x21f84-ORIGIN
L_00021f84:
    div1 r0,r1
    .org 0x21f86-ORIGIN
L_00021f86:
    div1 r0,r1
    .org 0x21f88-ORIGIN
L_00021f88:
    div1 r0,r1
    .org 0x21f8a-ORIGIN
L_00021f8a:
    div1 r0,r1
    .org 0x21f8c-ORIGIN
L_00021f8c:
    div1 r0,r1
    .org 0x21f8e-ORIGIN
L_00021f8e:
    div1 r0,r1
    .org 0x21f90-ORIGIN
L_00021f90:
    div1 r0,r1
    .org 0x21f92-ORIGIN
L_00021f92:
    div1 r0,r1
    .org 0x21f94-ORIGIN
L_00021f94:
    div1 r0,r1
    .org 0x21f96-ORIGIN
L_00021f96:
    div1 r0,r1
    .org 0x21f98-ORIGIN
L_00021f98:
    div1 r0,r1
    .org 0x21f9a-ORIGIN
L_00021f9a:
    extu.w r1,r2
    .org 0x21f9c-ORIGIN
L_00021f9c:
    xor r2,r1
    .org 0x21f9e-ORIGIN
L_00021f9e:
    add r3,r1
    .org 0x21fa0-ORIGIN
L_00021fa0:
    div1 r0,r1
    .org 0x21fa2-ORIGIN
L_00021fa2:
    div1 r0,r1
    .org 0x21fa4-ORIGIN
L_00021fa4:
    div1 r0,r1
    .org 0x21fa6-ORIGIN
L_00021fa6:
    div1 r0,r1
    .org 0x21fa8-ORIGIN
L_00021fa8:
    div1 r0,r1
    .org 0x21faa-ORIGIN
L_00021faa:
    div1 r0,r1
    .org 0x21fac-ORIGIN
L_00021fac:
    div1 r0,r1
    .org 0x21fae-ORIGIN
L_00021fae:
    div1 r0,r1
    .org 0x21fb0-ORIGIN
L_00021fb0:
    div1 r0,r1
    .org 0x21fb2-ORIGIN
L_00021fb2:
    div1 r0,r1
    .org 0x21fb4-ORIGIN
L_00021fb4:
    div1 r0,r1
    .org 0x21fb6-ORIGIN
L_00021fb6:
    div1 r0,r1
    .org 0x21fb8-ORIGIN
L_00021fb8:
    div1 r0,r1
    .org 0x21fba-ORIGIN
L_00021fba:
    div1 r0,r1
    .org 0x21fbc-ORIGIN
L_00021fbc:
    div1 r0,r1
    .org 0x21fbe-ORIGIN
L_00021fbe:
    div1 r0,r1
    .org 0x21fc0-ORIGIN
L_00021fc0:
    mov r1,r2
    .org 0x21fc2-ORIGIN
L_00021fc2:
    bt L_00021fc6
    .org 0x21fc4-ORIGIN
L_00021fc4:
    add r0,r2
    .org 0x21fc6-ORIGIN
L_00021fc6:
    mov r2,r0
    .org 0x21fc8-ORIGIN
L_00021fc8:
    shlr16 r0
    .org 0x21fca-ORIGIN
L_00021fca:
    mov.l @r15+,r3
    .org 0x21fcc-ORIGIN
L_00021fcc:
    rts
    .org 0x21fce-ORIGIN
L_00021fce:
    mov.l @r15+,r2
    .org 0x21fd0-ORIGIN
L_00021fd0:
    mov.l L_00022030,r1
    .org 0x21fd2-ORIGIN
L_00021fd2:
    mov.l L_00022034,r2
    .org 0x21fd4-ORIGIN
L_00021fd4:
    mov.l r2,@r1
    .org 0x21fd6-ORIGIN
L_00021fd6:
    mov #0x0,r0
    .org 0x21fd8-ORIGIN
L_00021fd8:
    rts
    .org 0x21fda-ORIGIN
L_00021fda:
    mov.l @r15+,r2
    .org 0x21fdc-ORIGIN
L_00021fdc:
    div0u
    .org 0x21fde-ORIGIN
L_00021fde:
    extu.w r1,r2
    .org 0x21fe0-ORIGIN
L_00021fe0:
    shll16 r2
    .org 0x21fe2-ORIGIN
L_00021fe2:
    shlr16 r1
    .org 0x21fe4-ORIGIN
L_00021fe4:
    rotcl r2
    .org 0x21fe6-ORIGIN
L_00021fe6:
    div1 r0,r1
    .org 0x21fe8-ORIGIN
L_00021fe8:
    rotcl r2
    .org 0x21fea-ORIGIN
L_00021fea:
    div1 r0,r1
    .org 0x21fec-ORIGIN
L_00021fec:
    rotcl r2
    .org 0x21fee-ORIGIN
L_00021fee:
    div1 r0,r1
    .org 0x21ff0-ORIGIN
L_00021ff0:
    rotcl r2
    .org 0x21ff2-ORIGIN
L_00021ff2:
    div1 r0,r1
    .org 0x21ff4-ORIGIN
L_00021ff4:
    rotcl r2
    .org 0x21ff6-ORIGIN
L_00021ff6:
    div1 r0,r1
    .org 0x21ff8-ORIGIN
L_00021ff8:
    rotcl r2
    .org 0x21ffa-ORIGIN
L_00021ffa:
    div1 r0,r1
    .org 0x21ffc-ORIGIN
L_00021ffc:
    rotcl r2
    .org 0x21ffe-ORIGIN
L_00021ffe:
    div1 r0,r1
    .org 0x22000-ORIGIN
L_00022000:
    rotcl r2
    .org 0x22002-ORIGIN
L_00022002:
    div1 r0,r1
    .org 0x22004-ORIGIN
L_00022004:
    rotcl r2
    .org 0x22006-ORIGIN
L_00022006:
    div1 r0,r1
    .org 0x22008-ORIGIN
L_00022008:
    rotcl r2
    .org 0x2200a-ORIGIN
L_0002200a:
    div1 r0,r1
    .org 0x2200c-ORIGIN
L_0002200c:
    rotcl r2
    .org 0x2200e-ORIGIN
L_0002200e:
    div1 r0,r1
    .org 0x22010-ORIGIN
L_00022010:
    rotcl r2
    .org 0x22012-ORIGIN
L_00022012:
    div1 r0,r1
    .org 0x22014-ORIGIN
L_00022014:
    rotcl r2
    .org 0x22016-ORIGIN
L_00022016:
    div1 r0,r1
    .org 0x22018-ORIGIN
L_00022018:
    rotcl r2
    .org 0x2201a-ORIGIN
L_0002201a:
    div1 r0,r1
    .org 0x2201c-ORIGIN
L_0002201c:
    rotcl r2
    .org 0x2201e-ORIGIN
L_0002201e:
    div1 r0,r1
    .org 0x22020-ORIGIN
L_00022020:
    rotcl r2
    .org 0x22022-ORIGIN
L_00022022:
    div1 r0,r1
    .org 0x22024-ORIGIN
L_00022024:
    bt L_00022028
    .org 0x22026-ORIGIN
L_00022026:
    add r0,r1
    .org 0x22028-ORIGIN
L_00022028:
    mov r1,r0
    .org 0x2202a-ORIGIN
L_0002202a:
    rts
    .org 0x2202c-ORIGIN
L_0002202c:
    mov.l @r15+,r2
    .org 0x22030-ORIGIN
L_00022030:
    .long 0xffff9818
    .org 0x22034-ORIGIN
L_00022034:
    .long 0x0000044e
    .org 0x224fa-ORIGIN
L_000224fa:
    shar r0
    .org 0x224fc-ORIGIN
L_000224fc:
    shar r0
    .org 0x224fe-ORIGIN
L_000224fe:
    shar r0
    .org 0x22500-ORIGIN
L_00022500:
    shar r0
    .org 0x22502-ORIGIN
L_00022502:
    shar r0
    .org 0x22504-ORIGIN
L_00022504:
    rts
    .org 0x22506-ORIGIN
L_00022506:
    shar r0
    .org 0x22508-ORIGIN
L_00022508:
    mov.l r1,@-r15
    .org 0x2250a-ORIGIN
L_0002250a:
    shlr8 r0
    .org 0x2250c-ORIGIN
L_0002250c:
    swap.w r0,r0
    .org 0x2250e-ORIGIN
L_0002250e:
    exts.b r0,r1
    .org 0x22510-ORIGIN
L_00022510:
    xtrct r1,r0
    .org 0x22512-ORIGIN
L_00022512:
    shar r0
    .org 0x22514-ORIGIN
L_00022514:
    shar r0
    .org 0x22516-ORIGIN
L_00022516:
    rts
    .org 0x22518-ORIGIN
L_00022518:
    mov.l @r15+,r1
    .org 0x259e4-ORIGIN
L_000259e4:
    mov.l L_00025b98,r1
    .org 0x259e6-ORIGIN
L_000259e6:
    exts.w r4,r0
    .org 0x259e8-ORIGIN
L_000259e8:
    cmp/eq #-1,r0
    .org 0x259ea-ORIGIN
L_000259ea:
    bt L_00025a0c
    .org 0x259ec-ORIGIN
L_000259ec:
    mov r0,r7
    .org 0x259ee-ORIGIN
L_000259ee:
    shll r7
    .org 0x259f0-ORIGIN
L_000259f0:
    mov r1,r2
    .org 0x259f2-ORIGIN
L_000259f2:
    add r0,r7
    .org 0x259f4-ORIGIN
L_000259f4:
    add r7,r2
    .org 0x259f6-ORIGIN
L_000259f6:
    mov.b @(2,r2),r0
    .org 0x259f8-ORIGIN
L_000259f8:
    tst #0x40,r0
    .org 0x259fa-ORIGIN
L_000259fa:
    bf/s L_00025a0e
    .org 0x259fc-ORIGIN
L_000259fc:
    mov #1,r5
    .org 0x259fe-ORIGIN
L_000259fe:
    mov r1,r2
    .org 0x25a00-ORIGIN
L_00025a00:
    add r7,r2
    .org 0x25a02-ORIGIN
L_00025a02:
    mov.b @(2,r2),r0
    .org 0x25a04-ORIGIN
L_00025a04:
    tst #0x20,r0
    .org 0x25a06-ORIGIN
L_00025a06:
    bf L_00025a0e
    .org 0x25a08-ORIGIN
L_00025a08:
    bra L_00025a0e
    .org 0x25a0a-ORIGIN
L_00025a0a:
    mov #0,r5
    .org 0x25a0c-ORIGIN
L_00025a0c:
    mov #0,r5
    .org 0x25a0e-ORIGIN
L_00025a0e:
    rts
    .org 0x25a10-ORIGIN
L_00025a10:
    mov r5,r0
    .org 0x25b98-ORIGIN
L_00025b98:
    .long 0xffff5718
    .org 0x26388-ORIGIN
L_00026388:
    mov.w L_0002639a,r0
    .org 0x2638a-ORIGIN
L_0002638a:
    extu.b r5,r5
    .org 0x2638c-ORIGIN
L_0002638c:
    cmp/hs r0,r5
    .org 0x2638e-ORIGIN
L_0002638e:
    bt L_00026396
    .org 0x26390-ORIGIN
L_00026390:
    mov.l L_0002639c,r6
    .org 0x26392-ORIGIN
L_00026392:
    jmp @r6
    .org 0x26394-ORIGIN
L_00026394:
    mov #0x0,r3
    .org 0x26396-ORIGIN
L_00026396:
    rts
    .org 0x26398-ORIGIN
L_00026398:
    mov.b @(0xf,r4),r0
    .org 0x2639a-ORIGIN
L_0002639a:
    .word 0x00f0
    .org 0x2639c-ORIGIN
L_0002639c:
    .long 0x00026a84
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
    mov.l L_00026abc,r6
    .org 0x26ab6-ORIGIN
L_00026ab6:
    jmp @r6
    .org 0x26ab8-ORIGIN
L_00026ab8:
    nop
    .org 0x26abc-ORIGIN
L_00026abc:
    .long 0x00026740
    .org 0x3b75c-ORIGIN
L_0003b75c:
    mov.l r8,@-r15
    .org 0x3b75e-ORIGIN
L_0003b75e:
    mov.l r9,@-r15
    .org 0x3b760-ORIGIN
L_0003b760:
    mov.l r10,@-r15
    .org 0x3b762-ORIGIN
L_0003b762:
    mov.l r11,@-r15
    .org 0x3b764-ORIGIN
L_0003b764:
    mov.l r12,@-r15
    .org 0x3b766-ORIGIN
L_0003b766:
    mov.l r13,@-r15
    .org 0x3b768-ORIGIN
L_0003b768:
    mov.l r14,@-r15
    .org 0x3b76a-ORIGIN
L_0003b76a:
    sts.l pr,@-r15
    .org 0x3b76c-ORIGIN
L_0003b76c:
    sts.l macl,@-r15
    .org 0x3b76e-ORIGIN
L_0003b76e:
    stc.l gbr,@-r15
    .org 0x3b770-ORIGIN
L_0003b770:
    mov.l L_0003b98c,r0
    .org 0x3b772-ORIGIN
L_0003b772:
    ldc r0,gbr
    .org 0x3b774-ORIGIN
L_0003b774:
    add #-0x18,r15
    .org 0x3b776-ORIGIN
L_0003b776:
    mov.l L_0003b990,r2
    .org 0x3b778-ORIGIN
L_0003b778:
    mov.b @r2,r4
    .org 0x3b77a-ORIGIN
L_0003b77a:
    mov r4,r0
    .org 0x3b77c-ORIGIN
L_0003b77c:
    and #0x80,r0
    .org 0x3b77e-ORIGIN
L_0003b77e:
    tst r0,r0
    .org 0x3b780-ORIGIN
L_0003b780:
    bf/s L_0003b790
    .org 0x3b782-ORIGIN
L_0003b782:
    mov r0,r6
    .org 0x3b784-ORIGIN
L_0003b784:
    mov.l L_0003b994,r5
    .org 0x3b786-ORIGIN
L_0003b786:
    mov #-0x59,r0
    .org 0x3b788-ORIGIN
L_0003b788:
    mov.l L_0003b998,r7
    .org 0x3b78a-ORIGIN
L_0003b78a:
    extu.b r0,r0
    .org 0x3b78c-ORIGIN
L_0003b78c:
    mov.b @r5,r2
    .org 0x3b78e-ORIGIN
L_0003b78e:
    mov.b r2,@(r0,r7)
    .org 0x3b790-ORIGIN
L_0003b790:
    mov.l L_0003b99c,r2
    .org 0x3b792-ORIGIN
L_0003b792:
    mov #-0x7a,r0
    .org 0x3b794-ORIGIN
L_0003b794:
    extu.b r0,r0
    .org 0x3b796-ORIGIN
L_0003b796:
    mov.b @(r0,r2),r5
    .org 0x3b798-ORIGIN
L_0003b798:
    extu.b r5,r5
    .org 0x3b79a-ORIGIN
L_0003b79a:
    tst r5,r5
    .org 0x3b79c-ORIGIN
L_0003b79c:
    bf L_0003b7a2
    .org 0x3b79e-ORIGIN
L_0003b79e:
    bra L_0003b8bc
    .org 0x3b7a0-ORIGIN
L_0003b7a0:
    nop
    .org 0x3b7a2-ORIGIN
L_0003b7a2:
    tst r6,r6
    .org 0x3b7a4-ORIGIN
L_0003b7a4:
    bt L_0003b7b6
    .org 0x3b7a6-ORIGIN
L_0003b7a6:
    mov.l L_0003b998,r7
    .org 0x3b7a8-ORIGIN
L_0003b7a8:
    mov #-0x59,r0
    .org 0x3b7aa-ORIGIN
L_0003b7aa:
    extu.b r0,r0
    .org 0x3b7ac-ORIGIN
L_0003b7ac:
    mov.b @(r0,r7),r2
    .org 0x3b7ae-ORIGIN
L_0003b7ae:
    tst r2,r2
    .org 0x3b7b0-ORIGIN
L_0003b7b0:
    bt L_0003b7b6
    .org 0x3b7b2-ORIGIN
L_0003b7b2:
    bra L_0003b8bc
    .org 0x3b7b4-ORIGIN
L_0003b7b4:
    nop
    .org 0x3b7b6-ORIGIN
L_0003b7b6:
    mov r4,r0
    .org 0x3b7b8-ORIGIN
L_0003b7b8:
    and #0x40,r0
    .org 0x3b7ba-ORIGIN
L_0003b7ba:
    tst r0,r0
    .org 0x3b7bc-ORIGIN
L_0003b7bc:
    bt/s L_0003b7c6
    .org 0x3b7be-ORIGIN
L_0003b7be:
    mov r0,r4
    .org 0x3b7c0-ORIGIN
L_0003b7c0:
    mov #0x20,r6
    .org 0x3b7c2-ORIGIN
L_0003b7c2:
    cmp/ge r6,r5
    .org 0x3b7c4-ORIGIN
L_0003b7c4:
    bf L_0003b8bc
    .org 0x3b7c6-ORIGIN
L_0003b7c6:
    tst r4,r4
    .org 0x3b7c8-ORIGIN
L_0003b7c8:
    bf L_0003b7f2
    .org 0x3b7ca-ORIGIN
L_0003b7ca:
    mov.l L_0003b9a0,r12
    .org 0x3b7cc-ORIGIN
L_0003b7cc:
    mov.l L_0003b9a4,r7
    .org 0x3b7ce-ORIGIN
L_0003b7ce:
    mov.b @(0x1,r12),r0
    .org 0x3b7d0-ORIGIN
L_0003b7d0:
    tst #0x20,r0
    .org 0x3b7d2-ORIGIN
L_0003b7d2:
    bt L_0003b7e2
    .org 0x3b7d4-ORIGIN
L_0003b7d4:
    mov.w @(0x8,r7),r0
    .org 0x3b7d6-ORIGIN
L_0003b7d6:
    mov #0x40,r5
    .org 0x3b7d8-ORIGIN
L_0003b7d8:
    extu.w r0,r6
    .org 0x3b7da-ORIGIN
L_0003b7da:
    cmp/ge r5,r6
    .org 0x3b7dc-ORIGIN
L_0003b7dc:
    bt L_0003b7ee
    .org 0x3b7de-ORIGIN
L_0003b7de:
    bra L_0003b7ee
    .org 0x3b7e0-ORIGIN
L_0003b7e0:
    mov #0x40,r6
    .org 0x3b7e2-ORIGIN
L_0003b7e2:
    mov.w @(0x14,r7),r0
    .org 0x3b7e4-ORIGIN
L_0003b7e4:
    mov #0x40,r5
    .org 0x3b7e6-ORIGIN
L_0003b7e6:
    extu.w r0,r6
    .org 0x3b7e8-ORIGIN
L_0003b7e8:
    cmp/ge r5,r6
    .org 0x3b7ea-ORIGIN
L_0003b7ea:
    bt L_0003b7ee
    .org 0x3b7ec-ORIGIN
L_0003b7ec:
    mov #0x40,r6
    .org 0x3b7ee-ORIGIN
L_0003b7ee:
    bra L_0003b802
    .org 0x3b7f0-ORIGIN
L_0003b7f0:
    mov r6,r14
    .org 0x3b7f2-ORIGIN
L_0003b7f2:
    shll2 r5
    .org 0x3b7f4-ORIGIN
L_0003b7f4:
    mov.l L_0003b9a0,r12
    .org 0x3b7f6-ORIGIN
L_0003b7f6:
    shll r5
    .org 0x3b7f8-ORIGIN
L_0003b7f8:
    mov #0x40,r2
    .org 0x3b7fa-ORIGIN
L_0003b7fa:
    cmp/hs r2,r5
    .org 0x3b7fc-ORIGIN
L_0003b7fc:
    bt L_0003b800
    .org 0x3b7fe-ORIGIN
L_0003b7fe:
    mov #0x40,r5
    .org 0x3b800-ORIGIN
L_0003b800:
    mov r5,r14
    .org 0x3b802-ORIGIN
L_0003b802:
    mov.l @(0x4c,gbr),r0
    .org 0x3b804-ORIGIN
L_0003b804:
    cmp/pl r0
    .org 0x3b806-ORIGIN
L_0003b806:
    bt/s L_0003b80e
    .org 0x3b808-ORIGIN
L_0003b808:
    mov r0,r6
    .org 0x3b80a-ORIGIN
L_0003b80a:
    bra L_0003b86a
    .org 0x3b80c-ORIGIN
L_0003b80c:
    mov #0x0,r2
    .org 0x3b80e-ORIGIN
L_0003b80e:
    mov.l L_0003b9a8,r5
    .org 0x3b810-ORIGIN
L_0003b810:
    mov r6,r2
    .org 0x3b812-ORIGIN
L_0003b812:
    shlr16 r2
    .org 0x3b814-ORIGIN
L_0003b814:
    mov.w @r5,r4
    .org 0x3b816-ORIGIN
L_0003b816:
    extu.w r4,r4
    .org 0x3b818-ORIGIN
L_0003b818:
    mul.l r2,r4
    .org 0x3b81a-ORIGIN
L_0003b81a:
    extu.w r6,r2
    .org 0x3b81c-ORIGIN
L_0003b81c:
    sts macl,r5
    .org 0x3b81e-ORIGIN
L_0003b81e:
    mul.l r2,r4
    .org 0x3b820-ORIGIN
L_0003b820:
    mov.l L_0003b9ac,r4
    .org 0x3b822-ORIGIN
L_0003b822:
    sts macl,r2
    .org 0x3b824-ORIGIN
L_0003b824:
    mov.b @r4,r7
    .org 0x3b826-ORIGIN
L_0003b826:
    mov r2,r6
    .org 0x3b828-ORIGIN
L_0003b828:
    shlr8 r6
    .org 0x3b82a-ORIGIN
L_0003b82a:
    extu.b r7,r7
    .org 0x3b82c-ORIGIN
L_0003b82c:
    mul.l r6,r7
    .org 0x3b82e-ORIGIN
L_0003b82e:
    extu.b r2,r2
    .org 0x3b830-ORIGIN
L_0003b830:
    sts macl,r4
    .org 0x3b832-ORIGIN
L_0003b832:
    mul.l r2,r7
    .org 0x3b834-ORIGIN
L_0003b834:
    sts macl,r2
    .org 0x3b836-ORIGIN
L_0003b836:
    shlr8 r2
    .org 0x3b838-ORIGIN
L_0003b838:
    add r2,r4
    .org 0x3b83a-ORIGIN
L_0003b83a:
    mov r5,r2
    .org 0x3b83c-ORIGIN
L_0003b83c:
    shlr8 r2
    .org 0x3b83e-ORIGIN
L_0003b83e:
    mul.l r2,r7
    .org 0x3b840-ORIGIN
L_0003b840:
    extu.b r5,r5
    .org 0x3b842-ORIGIN
L_0003b842:
    sts macl,r1
    .org 0x3b844-ORIGIN
L_0003b844:
    mul.l r5,r7
    .org 0x3b846-ORIGIN
L_0003b846:
    shll8 r1
    .org 0x3b848-ORIGIN
L_0003b848:
    sts macl,r2
    .org 0x3b84a-ORIGIN
L_0003b84a:
    add r2,r1
    .org 0x3b84c-ORIGIN
L_0003b84c:
    mov r4,r2
    .org 0x3b84e-ORIGIN
L_0003b84e:
    shlr8 r2
    .org 0x3b850-ORIGIN
L_0003b850:
    add r2,r1
    .org 0x3b852-ORIGIN
L_0003b852:
    mov.l L_0003b9b0,r2
    .org 0x3b854-ORIGIN
L_0003b854:
    extu.b r4,r4
    .org 0x3b856-ORIGIN
L_0003b856:
    mov.l r1,@r15
    .org 0x3b858-ORIGIN
L_0003b858:
    mov.b @r2,r6
    .org 0x3b85a-ORIGIN
L_0003b85a:
    mov.l r4,@(0x4,r15)
    .org 0x3b85c-ORIGIN
L_0003b85c:
    extu.b r6,r2
    .org 0x3b85e-ORIGIN
L_0003b85e:
    mul.l r14,r2
    .org 0x3b860-ORIGIN
L_0003b860:
    sts macl,r0
    .org 0x3b862-ORIGIN
L_0003b862:
    tst r0,r0
    .org 0x3b864-ORIGIN
L_0003b864:
    bf/s L_0003b870
    .org 0x3b866-ORIGIN
L_0003b866:
    mov.l r0,@(0x8,r15)
    .org 0x3b868-ORIGIN
L_0003b868:
    mov.l L_0003b9b4,r2
    .org 0x3b86a-ORIGIN
L_0003b86a:
    mov.l L_0003b9b8,r11
    .org 0x3b86c-ORIGIN
L_0003b86c:
    bra L_0003b8aa
    .org 0x3b86e-ORIGIN
L_0003b86e:
    nop
    .org 0x3b870-ORIGIN
L_0003b870:
    mov.l L_0003b9b8,r11
    .org 0x3b872-ORIGIN
L_0003b872:
    jsr @r11
    .org 0x3b874-ORIGIN
L_0003b874:
    nop
    .org 0x3b876-ORIGIN
L_0003b876:
    mov.w L_0003b8b8,r2
    .org 0x3b878-ORIGIN
L_0003b878:
    cmp/hs r2,r0
    .org 0x3b87a-ORIGIN
L_0003b87a:
    bt/s L_0003b8a8
    .org 0x3b87c-ORIGIN
L_0003b87c:
    mov r0,r6
    .org 0x3b87e-ORIGIN
L_0003b87e:
    mov r6,r5
    .org 0x3b880-ORIGIN
L_0003b880:
    mov.l L_0003b9bc,r6
    .org 0x3b882-ORIGIN
L_0003b882:
    mov.l @r15,r1
    .org 0x3b884-ORIGIN
L_0003b884:
    shll8 r5
    .org 0x3b886-ORIGIN
L_0003b886:
    mov.l @(0x8,r15),r0
    .org 0x3b888-ORIGIN
L_0003b888:
    jsr @r6
    .org 0x3b88a-ORIGIN
L_0003b88a:
    mov.l r5,@(0xc,r15)
    .org 0x3b88c-ORIGIN
L_0003b88c:
    mov.l @(0x4,r15),r4
    .org 0x3b88e-ORIGIN
L_0003b88e:
    mov r0,r1
    .org 0x3b890-ORIGIN
L_0003b890:
    shll8 r1
    .org 0x3b892-ORIGIN
L_0003b892:
    mov.l @(0x8,r15),r0
    .org 0x3b894-ORIGIN
L_0003b894:
    jsr @r11
    .org 0x3b896-ORIGIN
L_0003b896:
    add r4,r1
    .org 0x3b898-ORIGIN
L_0003b898:
    mov.l @(0xc,r15),r5
    .org 0x3b89a-ORIGIN
L_0003b89a:
    mov.l L_0003b9b4,r6
    .org 0x3b89c-ORIGIN
L_0003b89c:
    add r0,r5
    .org 0x3b89e-ORIGIN
L_0003b89e:
    cmp/hi r6,r5
    .org 0x3b8a0-ORIGIN
L_0003b8a0:
    bt L_0003b8a4
    .org 0x3b8a2-ORIGIN
L_0003b8a2:
    mov r5,r6
    .org 0x3b8a4-ORIGIN
L_0003b8a4:
    bra L_0003b8aa
    .org 0x3b8a6-ORIGIN
L_0003b8a6:
    mov r6,r2
    .org 0x3b8a8-ORIGIN
L_0003b8a8:
    mov.l L_0003b9b4,r2
    .org 0x3b8aa-ORIGIN
L_0003b8aa:
    mov.w L_0003b8ba,r6
    .org 0x3b8ac-ORIGIN
L_0003b8ac:
    mul.l r2,r6
    .org 0x3b8ae-ORIGIN
L_0003b8ae:
    sts macl,r0
    .org 0x3b8b0-ORIGIN
L_0003b8b0:
    shlr16 r0
    .org 0x3b8b2-ORIGIN
L_0003b8b2:
    mov r0,r6
    .org 0x3b8b4-ORIGIN
L_0003b8b4:
    bra L_0003b8da
    .org 0x3b8b6-ORIGIN
L_0003b8b6:
    mov.l r0,@(0x54,gbr)
    .org 0x3b8b8-ORIGIN
L_0003b8b8:
    .word 0x0727
    .org 0x3b8ba-ORIGIN
L_0003b8ba:
    .word 0x23cb
    .org 0x3b8bc-ORIGIN
L_0003b8bc:
    mov.l L_0003b9c0,r4
    .org 0x3b8be-ORIGIN
L_0003b8be:
    mov.l L_0003b9c4,r2
    .org 0x3b8c0-ORIGIN
L_0003b8c0:
    mov.b @(0x5,r4),r0
    .org 0x3b8c2-ORIGIN
L_0003b8c2:
    mov.l L_0003b9c8,r4
    .org 0x3b8c4-ORIGIN
L_0003b8c4:
    extu.b r0,r5
    .org 0x3b8c6-ORIGIN
L_0003b8c6:
    mov.l L_0003b9a0,r12
    .org 0x3b8c8-ORIGIN
L_0003b8c8:
    shll8 r5
    .org 0x3b8ca-ORIGIN
L_0003b8ca:
    mov.l L_0003b9b8,r11
    .org 0x3b8cc-ORIGIN
L_0003b8cc:
    jsr @r2
    .org 0x3b8ce-ORIGIN
L_0003b8ce:
    extu.w r5,r5
    .org 0x3b8d0-ORIGIN
L_0003b8d0:
    mov.w r0,@(0x58,gbr)
    .org 0x3b8d2-ORIGIN
L_0003b8d2:
    extu.w r0,r0
    .org 0x3b8d4-ORIGIN
L_0003b8d4:
    shlr2 r0
    .org 0x3b8d6-ORIGIN
L_0003b8d6:
    mov r0,r6
    .org 0x3b8d8-ORIGIN
L_0003b8d8:
    mov.l r0,@(0x54,gbr)
    .org 0x3b8da-ORIGIN
L_0003b8da:
    mov.l L_0003b9cc,r8
    .org 0x3b8dc-ORIGIN
L_0003b8dc:
    mov #0x4c,r0
    .org 0x3b8de-ORIGIN
L_0003b8de:
    mov #-0x1,r13
    .org 0x3b8e0-ORIGIN
L_0003b8e0:
    mov.b @(r0,r8),r2
    .org 0x3b8e2-ORIGIN
L_0003b8e2:
    extu.w r13,r13
    .org 0x3b8e4-ORIGIN
L_0003b8e4:
    extu.b r2,r5
    .org 0x3b8e6-ORIGIN
L_0003b8e6:
    mul.l r6,r5
    .org 0x3b8e8-ORIGIN
L_0003b8e8:
    mov.l L_0003b9d0,r5
    .org 0x3b8ea-ORIGIN
L_0003b8ea:
    sts macl,r6
    .org 0x3b8ec-ORIGIN
L_0003b8ec:
    mov.b @(0x5,r5),r0
    .org 0x3b8ee-ORIGIN
L_0003b8ee:
    shlr2 r6
    .org 0x3b8f0-ORIGIN
L_0003b8f0:
    shlr2 r6
    .org 0x3b8f2-ORIGIN
L_0003b8f2:
    shlr2 r6
    .org 0x3b8f4-ORIGIN
L_0003b8f4:
    shlr r6
    .org 0x3b8f6-ORIGIN
L_0003b8f6:
    cmp/hi r13,r6
    .org 0x3b8f8-ORIGIN
L_0003b8f8:
    extu.b r0,r14
    .org 0x3b8fa-ORIGIN
L_0003b8fa:
    bf/s L_0003b900
    .org 0x3b8fc-ORIGIN
L_0003b8fc:
    mov r6,r5
    .org 0x3b8fe-ORIGIN
L_0003b8fe:
    mov r13,r5
    .org 0x3b900-ORIGIN
L_0003b900:
    mov.l L_0003b9d4,r10
    .org 0x3b902-ORIGIN
L_0003b902:
    extu.w r5,r5
    .org 0x3b904-ORIGIN
L_0003b904:
    mov r5,r0
    .org 0x3b906-ORIGIN
L_0003b906:
    mov.w r0,@(0x1a,r10)
    .org 0x3b908-ORIGIN
L_0003b908:
    mov #0x48,r0
    .org 0x3b90a-ORIGIN
L_0003b90a:
    mov.w @(r0,r8),r6
    .org 0x3b90c-ORIGIN
L_0003b90c:
    extu.w r6,r2
    .org 0x3b90e-ORIGIN
L_0003b90e:
    mul.l r2,r5
    .org 0x3b910-ORIGIN
L_0003b910:
    mov #0x40,r6
    .org 0x3b912-ORIGIN
L_0003b912:
    shll8 r6
    .org 0x3b914-ORIGIN
L_0003b914:
    sts macl,r2
    .org 0x3b916-ORIGIN
L_0003b916:
    shll16 r6
    .org 0x3b918-ORIGIN
L_0003b918:
    cmp/hs r6,r2
    .org 0x3b91a-ORIGIN
L_0003b91a:
    bt L_0003b922
    .org 0x3b91c-ORIGIN
L_0003b91c:
    shll2 r2
    .org 0x3b91e-ORIGIN
L_0003b91e:
    bra L_0003b924
    .org 0x3b920-ORIGIN
L_0003b920:
    mov r2,r6
    .org 0x3b922-ORIGIN
L_0003b922:
    mov #-0x1,r6
    .org 0x3b924-ORIGIN
L_0003b924:
    mov.w @(0x144,gbr),r0
    .org 0x3b926-ORIGIN
L_0003b926:
    extu.w r0,r9
    .org 0x3b928-ORIGIN
L_0003b928:
    mov.w @(0x1a,gbr),r0
    .org 0x3b92a-ORIGIN
L_0003b92a:
    extu.w r0,r7
    .org 0x3b92c-ORIGIN
L_0003b92c:
    mov r14,r0
    .org 0x3b92e-ORIGIN
L_0003b92e:
    mul.l r9,r7
    .org 0x3b930-ORIGIN
L_0003b930:
    tst #0x10,r0
    .org 0x3b932-ORIGIN
L_0003b932:
    bf/s L_0003b970
    .org 0x3b934-ORIGIN
L_0003b934:
    sts macl,r4
    .org 0x3b936-ORIGIN
L_0003b936:
    not r4,r2
    .org 0x3b938-ORIGIN
L_0003b938:
    cmp/hs r2,r6
    .org 0x3b93a-ORIGIN
L_0003b93a:
    bt L_0003b94a
    .org 0x3b93c-ORIGIN
L_0003b93c:
    add r4,r6
    .org 0x3b93e-ORIGIN
L_0003b93e:
    shlr8 r6
    .org 0x3b940-ORIGIN
L_0003b940:
    shlr2 r6
    .org 0x3b942-ORIGIN
L_0003b942:
    shlr2 r6
    .org 0x3b944-ORIGIN
L_0003b944:
    shlr2 r6
    .org 0x3b946-ORIGIN
L_0003b946:
    bra L_0003b94c
    .org 0x3b948-ORIGIN
L_0003b948:
    shlr r6
    .org 0x3b94a-ORIGIN
L_0003b94a:
    mov #-0x1,r6
    .org 0x3b94c-ORIGIN
L_0003b94c:
    cmp/hi r13,r6
    .org 0x3b94e-ORIGIN
L_0003b94e:
    bf/s L_0003b954
    .org 0x3b950-ORIGIN
L_0003b950:
    mov r6,r2
    .org 0x3b952-ORIGIN
L_0003b952:
    mov r13,r2
    .org 0x3b954-ORIGIN
L_0003b954:
    mov r2,r6
    .org 0x3b956-ORIGIN
L_0003b956:
    mov r5,r2
    .org 0x3b958-ORIGIN
L_0003b958:
    shll2 r2
    .org 0x3b95a-ORIGIN
L_0003b95a:
    cmp/hi r13,r2
    .org 0x3b95c-ORIGIN
L_0003b95c:
    bf L_0003b960
    .org 0x3b95e-ORIGIN
L_0003b95e:
    mov r13,r2
    .org 0x3b960-ORIGIN
L_0003b960:
    cmp/hs r2,r6
    .org 0x3b962-ORIGIN
L_0003b962:
    bt L_0003b9da
    .org 0x3b964-ORIGIN
L_0003b964:
    mov.w @(0x2,gbr),r0
    .org 0x3b966-ORIGIN
L_0003b966:
    extu.w r0,r2
    .org 0x3b968-ORIGIN
L_0003b968:
    cmp/eq r2,r6
    .org 0x3b96a-ORIGIN
L_0003b96a:
    bf L_0003b9da
    .org 0x3b96c-ORIGIN
L_0003b96c:
    bra L_0003b9da
    .org 0x3b96e-ORIGIN
L_0003b96e:
    add #0x1,r6
    .org 0x3b970-ORIGIN
L_0003b970:
    cmp/hs r6,r4
    .org 0x3b972-ORIGIN
L_0003b972:
    bf L_0003b9d8
    .org 0x3b974-ORIGIN
L_0003b974:
    sub r6,r4
    .org 0x3b976-ORIGIN
L_0003b976:
    shlr8 r4
    .org 0x3b978-ORIGIN
L_0003b978:
    shlr2 r4
    .org 0x3b97a-ORIGIN
L_0003b97a:
    shlr2 r4
    .org 0x3b97c-ORIGIN
L_0003b97c:
    shlr2 r4
    .org 0x3b97e-ORIGIN
L_0003b97e:
    shlr r4
    .org 0x3b980-ORIGIN
L_0003b980:
    cmp/hi r13,r4
    .org 0x3b982-ORIGIN
L_0003b982:
    bf/s L_0003b988
    .org 0x3b984-ORIGIN
L_0003b984:
    mov r4,r2
    .org 0x3b986-ORIGIN
L_0003b986:
    mov r13,r2
    .org 0x3b988-ORIGIN
L_0003b988:
    bra L_0003b9da
    .org 0x3b98a-ORIGIN
L_0003b98a:
    mov r2,r6
    .org 0x3b98c-ORIGIN
L_0003b98c:
    .long 0xffff1dec
    .org 0x3b990-ORIGIN
L_0003b990:
    .long 0xffff4185
    .org 0x3b994-ORIGIN
L_0003b994:
    .long 0x00008c80
    .org 0x3b998-ORIGIN
L_0003b998:
    .long 0xffff42d3
    .org 0x3b99c-ORIGIN
L_0003b99c:
    .long 0xffff277e
    .org 0x3b9a0-ORIGIN
L_0003b9a0:
    .long 0xffff2460
    .org 0x3b9a4-ORIGIN
L_0003b9a4:
    .long 0xffff11d4
    .org 0x3b9a8-ORIGIN
L_0003b9a8:
    .long 0x00009284
    .org 0x3b9ac-ORIGIN
L_0003b9ac:
    .long 0x00008a27
    .org 0x3b9b0-ORIGIN
L_0003b9b0:
    .long 0x000088fb
    .org 0x3b9b4-ORIGIN
L_0003b9b4:
    .long 0x000726f9
    .org 0x3b9b8-ORIGIN
L_0003b9b8:
    .long 0x00021ce0
    .org 0x3b9bc-ORIGIN
L_0003b9bc:
    .long 0x00021f40
    .org 0x3b9c0-ORIGIN
L_0003b9c0:
    .long 0xffff1072
    .org 0x3b9c4-ORIGIN
L_0003b9c4:
    .long 0x000263d8
    .org 0x3b9c8-ORIGIN
L_0003b9c8:
    .long 0x00015630
    .org 0x3b9cc-ORIGIN
L_0003b9cc:
    .long 0xffff1114
    .org 0x3b9d0-ORIGIN
L_0003b9d0:
    .long 0xffff24ac
    .org 0x3b9d4-ORIGIN
L_0003b9d4:
    .long 0xffff1048
    .org 0x3b9d8-ORIGIN
L_0003b9d8:
    mov #0x0,r6
    .org 0x3b9da-ORIGIN
L_0003b9da:
    mov.l L_0003bbc4,r3
    .org 0x3b9dc-ORIGIN
L_0003b9dc:
    mov r6,r0
    .org 0x3b9de-ORIGIN
L_0003b9de:
    mov.w r0,@(0x2,gbr)
    .org 0x3b9e0-ORIGIN
L_0003b9e0:
    mov #0x5c,r0
    .org 0x3b9e2-ORIGIN
L_0003b9e2:
    mov.b @(r0,r8),r4
    .org 0x3b9e4-ORIGIN
L_0003b9e4:
    mov.b @r3,r2
    .org 0x3b9e6-ORIGIN
L_0003b9e6:
    extu.b r4,r4
    .org 0x3b9e8-ORIGIN
L_0003b9e8:
    extu.b r2,r2
    .org 0x3b9ea-ORIGIN
L_0003b9ea:
    cmp/ge r2,r4
    .org 0x3b9ec-ORIGIN
L_0003b9ec:
    bf L_0003b9fc
    .org 0x3b9ee-ORIGIN
L_0003b9ee:
    shll2 r5
    .org 0x3b9f0-ORIGIN
L_0003b9f0:
    cmp/hs r5,r7
    .org 0x3b9f2-ORIGIN
L_0003b9f2:
    bf L_0003b9fc
    .org 0x3b9f4-ORIGIN
L_0003b9f4:
    mov r14,r0
    .org 0x3b9f6-ORIGIN
L_0003b9f6:
    mov.l L_0003bbc8,r2
    .org 0x3b9f8-ORIGIN
L_0003b9f8:
    bra L_0003ba0c
    .org 0x3b9fa-ORIGIN
L_0003b9fa:
    or #0x80,r0
    .org 0x3b9fc-ORIGIN
L_0003b9fc:
    mov.l L_0003bbcc,r6
    .org 0x3b9fe-ORIGIN
L_0003b9fe:
    mov.b @r6,r2
    .org 0x3ba00-ORIGIN
L_0003ba00:
    extu.b r2,r2
    .org 0x3ba02-ORIGIN
L_0003ba02:
    cmp/ge r2,r4
    .org 0x3ba04-ORIGIN
L_0003ba04:
    bt L_0003ba10
    .org 0x3ba06-ORIGIN
L_0003ba06:
    mov r14,r0
    .org 0x3ba08-ORIGIN
L_0003ba08:
    and #0x7f,r0
    .org 0x3ba0a-ORIGIN
L_0003ba0a:
    mov.l L_0003bbc8,r2
    .org 0x3ba0c-ORIGIN
L_0003ba0c:
    mov r0,r14
    .org 0x3ba0e-ORIGIN
L_0003ba0e:
    mov.b r0,@(0x5,r2)
    .org 0x3ba10-ORIGIN
L_0003ba10:
    mov.l L_0003bbd0,r6
    .org 0x3ba12-ORIGIN
L_0003ba12:
    mov.b @(0x1,r6),r0
    .org 0x3ba14-ORIGIN
L_0003ba14:
    tst #0x80,r0
    .org 0x3ba16-ORIGIN
L_0003ba16:
    bt L_0003ba1e
    .org 0x3ba18-ORIGIN
L_0003ba18:
    mov #0x4,r4
    .org 0x3ba1a-ORIGIN
L_0003ba1a:
    bra L_0003ba36
    .org 0x3ba1c-ORIGIN
L_0003ba1c:
    mov r4,r0
    .org 0x3ba1e-ORIGIN
L_0003ba1e:
    mov.b @(0x34,gbr),r0
    .org 0x3ba20-ORIGIN
L_0003ba20:
    extu.b r0,r6
    .org 0x3ba22-ORIGIN
L_0003ba22:
    exts.w r6,r2
    .org 0x3ba24-ORIGIN
L_0003ba24:
    add #-0x1,r2
    .org 0x3ba26-ORIGIN
L_0003ba26:
    cmp/pz r2
    .org 0x3ba28-ORIGIN
L_0003ba28:
    bt L_0003ba2e
    .org 0x3ba2a-ORIGIN
L_0003ba2a:
    bra L_0003ba32
    .org 0x3ba2c-ORIGIN
L_0003ba2c:
    mov #0x0,r6
    .org 0x3ba2e-ORIGIN
L_0003ba2e:
    exts.w r6,r6
    .org 0x3ba30-ORIGIN
L_0003ba30:
    add #-0x1,r6
    .org 0x3ba32-ORIGIN
L_0003ba32:
    mov r6,r4
    .org 0x3ba34-ORIGIN
L_0003ba34:
    mov r6,r0
    .org 0x3ba36-ORIGIN
L_0003ba36:
    mov.l L_0003bbd4,r6
    .org 0x3ba38-ORIGIN
L_0003ba38:
    mov.b r0,@(0x34,gbr)
    .org 0x3ba3a-ORIGIN
L_0003ba3a:
    mov.b @(0x4,r6),r0
    .org 0x3ba3c-ORIGIN
L_0003ba3c:
    tst #0x40,r0
    .org 0x3ba3e-ORIGIN
L_0003ba3e:
    bt L_0003ba44
    .org 0x3ba40-ORIGIN
L_0003ba40:
    bra L_0003ba5a
    .org 0x3ba42-ORIGIN
L_0003ba42:
    mov #0x4,r0
    .org 0x3ba44-ORIGIN
L_0003ba44:
    mov.b @(0x5b,gbr),r0
    .org 0x3ba46-ORIGIN
L_0003ba46:
    extu.b r0,r6
    .org 0x3ba48-ORIGIN
L_0003ba48:
    exts.w r6,r2
    .org 0x3ba4a-ORIGIN
L_0003ba4a:
    add #-0x1,r2
    .org 0x3ba4c-ORIGIN
L_0003ba4c:
    cmp/pz r2
    .org 0x3ba4e-ORIGIN
L_0003ba4e:
    bt L_0003ba54
    .org 0x3ba50-ORIGIN
L_0003ba50:
    bra L_0003ba58
    .org 0x3ba52-ORIGIN
L_0003ba52:
    mov #0x0,r2
    .org 0x3ba54-ORIGIN
L_0003ba54:
    exts.w r6,r2
    .org 0x3ba56-ORIGIN
L_0003ba56:
    add #-0x1,r2
    .org 0x3ba58-ORIGIN
L_0003ba58:
    mov r2,r0
    .org 0x3ba5a-ORIGIN
L_0003ba5a:
    mov.l L_0003bbd8,r13
    .org 0x3ba5c-ORIGIN
L_0003ba5c:
    mov.b r0,@(0x5b,gbr)
    .org 0x3ba5e-ORIGIN
L_0003ba5e:
    mov.b @r13,r0
    .org 0x3ba60-ORIGIN
L_0003ba60:
    tst #0x8,r0
    .org 0x3ba62-ORIGIN
L_0003ba62:
    bt L_0003bab8
    .org 0x3ba64-ORIGIN
L_0003ba64:
    mov.l L_0003bbdc,r2
    .org 0x3ba66-ORIGIN
L_0003ba66:
    jsr @r2
    .org 0x3ba68-ORIGIN
L_0003ba68:
    mov #-0x1,r4
    .org 0x3ba6a-ORIGIN
L_0003ba6a:
    tst r0,r0
    .org 0x3ba6c-ORIGIN
L_0003ba6c:
    bt L_0003ba74
    .org 0x3ba6e-ORIGIN
L_0003ba6e:
    mov #0x4,r7
    .org 0x3ba70-ORIGIN
L_0003ba70:
    bra L_0003ba8c
    .org 0x3ba72-ORIGIN
L_0003ba72:
    mov r7,r0
    .org 0x3ba74-ORIGIN
L_0003ba74:
    mov.b @(0x60,gbr),r0
    .org 0x3ba76-ORIGIN
L_0003ba76:
    extu.b r0,r6
    .org 0x3ba78-ORIGIN
L_0003ba78:
    exts.w r6,r2
    .org 0x3ba7a-ORIGIN
L_0003ba7a:
    add #-0x1,r2
    .org 0x3ba7c-ORIGIN
L_0003ba7c:
    cmp/pz r2
    .org 0x3ba7e-ORIGIN
L_0003ba7e:
    bt L_0003ba84
    .org 0x3ba80-ORIGIN
L_0003ba80:
    bra L_0003ba88
    .org 0x3ba82-ORIGIN
L_0003ba82:
    mov #0x0,r2
    .org 0x3ba84-ORIGIN
L_0003ba84:
    exts.w r6,r2
    .org 0x3ba86-ORIGIN
L_0003ba86:
    add #-0x1,r2
    .org 0x3ba88-ORIGIN
L_0003ba88:
    mov r2,r7
    .org 0x3ba8a-ORIGIN
L_0003ba8a:
    mov r2,r0
    .org 0x3ba8c-ORIGIN
L_0003ba8c:
    mov.b r0,@(0x60,gbr)
    .org 0x3ba8e-ORIGIN
L_0003ba8e:
    mov.b @(0x34,gbr),r0
    .org 0x3ba90-ORIGIN
L_0003ba90:
    mov.l L_0003bbd0,r5
    .org 0x3ba92-ORIGIN
L_0003ba92:
    mov r0,r4
    .org 0x3ba94-ORIGIN
L_0003ba94:
    tst r0,r0
    .org 0x3ba96-ORIGIN
L_0003ba96:
    mov.b @(0x6,r5),r0
    .org 0x3ba98-ORIGIN
L_0003ba98:
    bf/s L_0003bab0
    .org 0x3ba9a-ORIGIN
L_0003ba9a:
    mov r0,r5
    .org 0x3ba9c-ORIGIN
L_0003ba9c:
    mov.b @(0x5b,gbr),r0
    .org 0x3ba9e-ORIGIN
L_0003ba9e:
    tst r0,r0
    .org 0x3baa0-ORIGIN
L_0003baa0:
    bf L_0003bab0
    .org 0x3baa2-ORIGIN
L_0003baa2:
    extu.b r7,r7
    .org 0x3baa4-ORIGIN
L_0003baa4:
    tst r7,r7
    .org 0x3baa6-ORIGIN
L_0003baa6:
    bf L_0003bab0
    .org 0x3baa8-ORIGIN
L_0003baa8:
    mov r5,r0
    .org 0x3baaa-ORIGIN
L_0003baaa:
    mov.l L_0003bbd0,r2
    .org 0x3baac-ORIGIN
L_0003baac:
    bra L_0003bab6
    .org 0x3baae-ORIGIN
L_0003baae:
    and #0x7f,r0
    .org 0x3bab0-ORIGIN
L_0003bab0:
    mov r5,r0
    .org 0x3bab2-ORIGIN
L_0003bab2:
    or #0x80,r0
    .org 0x3bab4-ORIGIN
L_0003bab4:
    mov.l L_0003bbd0,r2
    .org 0x3bab6-ORIGIN
L_0003bab6:
    mov.b r0,@(0x6,r2)
    .org 0x3bab8-ORIGIN
L_0003bab8:
    mov.b @(0x2,r12),r0
    .org 0x3baba-ORIGIN
L_0003baba:
    and #0x1,r0
    .org 0x3babc-ORIGIN
L_0003babc:
    mov r0,r2
    .org 0x3babe-ORIGIN
L_0003babe:
    mov #0x10,r0
    .org 0x3bac0-ORIGIN
L_0003bac0:
    tst r2,r2
    .org 0x3bac2-ORIGIN
L_0003bac2:
    bt/s L_0003bb34
    .org 0x3bac4-ORIGIN
L_0003bac4:
    mov.b r2,@(r0,r15)
    .org 0x3bac6-ORIGIN
L_0003bac6:
    mov.l L_0003bbc8,r5
    .org 0x3bac8-ORIGIN
L_0003bac8:
    mov #0x11,r0
    .org 0x3baca-ORIGIN
L_0003baca:
    mov.b @(r0,r5),r0
    .org 0x3bacc-ORIGIN
L_0003bacc:
    tst #0x4,r0
    .org 0x3bace-ORIGIN
L_0003bace:
    bt L_0003bb34
    .org 0x3bad0-ORIGIN
L_0003bad0:
    mov.b @(0x5,r5),r0
    .org 0x3bad2-ORIGIN
L_0003bad2:
    tst #0x80,r0
    .org 0x3bad4-ORIGIN
L_0003bad4:
    bf L_0003bb34
    .org 0x3bad6-ORIGIN
L_0003bad6:
    extu.b r4,r4
    .org 0x3bad8-ORIGIN
L_0003bad8:
    tst r4,r4
    .org 0x3bada-ORIGIN
L_0003bada:
    bf L_0003bb34
    .org 0x3badc-ORIGIN
L_0003badc:
    mov.b @(0x5b,gbr),r0
    .org 0x3bade-ORIGIN
L_0003bade:
    tst r0,r0
    .org 0x3bae0-ORIGIN
L_0003bae0:
    bf L_0003bb34
    .org 0x3bae2-ORIGIN
L_0003bae2:
    mov.w @(0x2,gbr),r0
    .org 0x3bae4-ORIGIN
L_0003bae4:
    mov.l L_0003bbe0,r2
    .org 0x3bae6-ORIGIN
L_0003bae6:
    extu.w r0,r6
    .org 0x3bae8-ORIGIN
L_0003bae8:
    mov.w @(0x1a,gbr),r0
    .org 0x3baea-ORIGIN
L_0003baea:
    mov.b @r2,r7
    .org 0x3baec-ORIGIN
L_0003baec:
    extu.w r0,r5
    .org 0x3baee-ORIGIN
L_0003baee:
    mov.l L_0003bbe4,r4
    .org 0x3baf0-ORIGIN
L_0003baf0:
    extu.b r7,r7
    .org 0x3baf2-ORIGIN
L_0003baf2:
    sub r5,r6
    .org 0x3baf4-ORIGIN
L_0003baf4:
    mul.l r6,r7
    .org 0x3baf6-ORIGIN
L_0003baf6:
    jsr @r4
    .org 0x3baf8-ORIGIN
L_0003baf8:
    sts macl,r0
    .org 0x3bafa-ORIGIN
L_0003bafa:
    mov #-0x80,r5
    .org 0x3bafc-ORIGIN
L_0003bafc:
    shll8 r5
    .org 0x3bafe-ORIGIN
L_0003bafe:
    cmp/ge r5,r0
    .org 0x3bb00-ORIGIN
L_0003bb00:
    bf L_0003bb1c
    .org 0x3bb02-ORIGIN
L_0003bb02:
    mov.w @(0x2,gbr),r0
    .org 0x3bb04-ORIGIN
L_0003bb04:
    mov.l L_0003bbe0,r3
    .org 0x3bb06-ORIGIN
L_0003bb06:
    extu.w r0,r6
    .org 0x3bb08-ORIGIN
L_0003bb08:
    mov.w @(0x1a,gbr),r0
    .org 0x3bb0a-ORIGIN
L_0003bb0a:
    mov.b @r3,r7
    .org 0x3bb0c-ORIGIN
L_0003bb0c:
    extu.w r0,r5
    .org 0x3bb0e-ORIGIN
L_0003bb0e:
    mov.l L_0003bbe4,r4
    .org 0x3bb10-ORIGIN
L_0003bb10:
    extu.b r7,r7
    .org 0x3bb12-ORIGIN
L_0003bb12:
    sub r5,r6
    .org 0x3bb14-ORIGIN
L_0003bb14:
    mul.l r6,r7
    .org 0x3bb16-ORIGIN
L_0003bb16:
    jsr @r4
    .org 0x3bb18-ORIGIN
L_0003bb18:
    sts macl,r0
    .org 0x3bb1a-ORIGIN
L_0003bb1a:
    mov r0,r5
    .org 0x3bb1c-ORIGIN
L_0003bb1c:
    mov.w L_0003bb22,r6
    .org 0x3bb1e-ORIGIN
L_0003bb1e:
    bra L_0003bb24
    .org 0x3bb20-ORIGIN
L_0003bb20:
    mov r5,r14
    .org 0x3bb22-ORIGIN
L_0003bb22:
    .word 0x7fff
    .org 0x3bb24-ORIGIN
L_0003bb24:
    cmp/gt r6,r5
    .org 0x3bb26-ORIGIN
L_0003bb26:
    bt L_0003bb2a
    .org 0x3bb28-ORIGIN
L_0003bb28:
    mov r14,r6
    .org 0x3bb2a-ORIGIN
L_0003bb2a:
    mov.l L_0003bbe8,r3
    .org 0x3bb2c-ORIGIN
L_0003bb2c:
    mov r6,r0
    .org 0x3bb2e-ORIGIN
L_0003bb2e:
    mov.w r0,@(0x18,r3)
    .org 0x3bb30-ORIGIN
L_0003bb30:
    bra L_0003bb3c
    .org 0x3bb32-ORIGIN
L_0003bb32:
    mov r6,r7
    .org 0x3bb34-ORIGIN
L_0003bb34:
    mov.l L_0003bbe8,r3
    .org 0x3bb36-ORIGIN
L_0003bb36:
    mov #0x0,r7
    .org 0x3bb38-ORIGIN
L_0003bb38:
    mov r7,r0
    .org 0x3bb3a-ORIGIN
L_0003bb3a:
    mov.w r0,@(0x18,r3)
    .org 0x3bb3c-ORIGIN
L_0003bb3c:
    mov.b @r13,r0
    .org 0x3bb3e-ORIGIN
L_0003bb3e:
    and #0x10,r0
    .org 0x3bb40-ORIGIN
L_0003bb40:
    tst r0,r0
    .org 0x3bb42-ORIGIN
L_0003bb42:
    bt/s L_0003bb86
    .org 0x3bb44-ORIGIN
L_0003bb44:
    mov r0,r5
    .org 0x3bb46-ORIGIN
L_0003bb46:
    mov #0x10,r0
    .org 0x3bb48-ORIGIN
L_0003bb48:
    mov.b @(r0,r15),r2
    .org 0x3bb4a-ORIGIN
L_0003bb4a:
    tst r2,r2
    .org 0x3bb4c-ORIGIN
L_0003bb4c:
    bt L_0003bb80
    .org 0x3bb4e-ORIGIN
L_0003bb4e:
    mov.l L_0003bbc8,r6
    .org 0x3bb50-ORIGIN
L_0003bb50:
    mov #0x11,r0
    .org 0x3bb52-ORIGIN
L_0003bb52:
    mov.b @(r0,r6),r0
    .org 0x3bb54-ORIGIN
L_0003bb54:
    tst #0x4,r0
    .org 0x3bb56-ORIGIN
L_0003bb56:
    bf L_0003bb80
    .org 0x3bb58-ORIGIN
L_0003bb58:
    mov.l L_0003bbc8,r6
    .org 0x3bb5a-ORIGIN
L_0003bb5a:
    mov.b @(0x5,r6),r0
    .org 0x3bb5c-ORIGIN
L_0003bb5c:
    tst #0x80,r0
    .org 0x3bb5e-ORIGIN
L_0003bb5e:
    bt L_0003bb80
    .org 0x3bb60-ORIGIN
L_0003bb60:
    mov.b @(0xf5,gbr),r0
    .org 0x3bb62-ORIGIN
L_0003bb62:
    mov #0x1,r6
    .org 0x3bb64-ORIGIN
L_0003bb64:
    shll8 r6
    .org 0x3bb66-ORIGIN
L_0003bb66:
    extu.b r0,r4
    .org 0x3bb68-ORIGIN
L_0003bb68:
    mov.w @(0x2,gbr),r0
    .org 0x3bb6a-ORIGIN
L_0003bb6a:
    sub r4,r6
    .org 0x3bb6c-ORIGIN
L_0003bb6c:
    extu.w r0,r2
    .org 0x3bb6e-ORIGIN
L_0003bb6e:
    mov.w @(0x18,gbr),r0
    .org 0x3bb70-ORIGIN
L_0003bb70:
    mul.l r4,r2
    .org 0x3bb72-ORIGIN
L_0003bb72:
    extu.w r0,r4
    .org 0x3bb74-ORIGIN
L_0003bb74:
    sts macl,r0
    .org 0x3bb76-ORIGIN
L_0003bb76:
    mul.l r6,r4
    .org 0x3bb78-ORIGIN
L_0003bb78:
    sts macl,r6
    .org 0x3bb7a-ORIGIN
L_0003bb7a:
    add r6,r0
    .org 0x3bb7c-ORIGIN
L_0003bb7c:
    bra L_0003bb84
    .org 0x3bb7e-ORIGIN
L_0003bb7e:
    shlr8 r0
    .org 0x3bb80-ORIGIN
L_0003bb80:
    mov.w @(0x2,gbr),r0
    .org 0x3bb82-ORIGIN
L_0003bb82:
    mov.l r0,@(0x14,r15)
    .org 0x3bb84-ORIGIN
L_0003bb84:
    mov.w r0,@(0x0,gbr)
    .org 0x3bb86-ORIGIN
L_0003bb86:
    mov.l L_0003bbd0,r6
    .org 0x3bb88-ORIGIN
L_0003bb88:
    mov.b @(0x1,r6),r0
    .org 0x3bb8a-ORIGIN
L_0003bb8a:
    tst #0x80,r0
    .org 0x3bb8c-ORIGIN
L_0003bb8c:
    bf L_0003bc16
    .org 0x3bb8e-ORIGIN
L_0003bb8e:
    tst r5,r5
    .org 0x3bb90-ORIGIN
L_0003bb90:
    bf L_0003bbac
    .org 0x3bb92-ORIGIN
L_0003bb92:
    mov.w @(0x2,gbr),r0
    .org 0x3bb94-ORIGIN
L_0003bb94:
    exts.w r7,r7
    .org 0x3bb96-ORIGIN
L_0003bb96:
    extu.w r0,r6
    .org 0x3bb98-ORIGIN
L_0003bb98:
    mov r6,r2
    .org 0x3bb9a-ORIGIN
L_0003bb9a:
    add r7,r2
    .org 0x3bb9c-ORIGIN
L_0003bb9c:
    cmp/pz r2
    .org 0x3bb9e-ORIGIN
L_0003bb9e:
    bt L_0003bba4
    .org 0x3bba0-ORIGIN
L_0003bba0:
    bra L_0003bbaa
    .org 0x3bba2-ORIGIN
L_0003bba2:
    mov #0x0,r2
    .org 0x3bba4-ORIGIN
L_0003bba4:
    exts.w r7,r7
    .org 0x3bba6-ORIGIN
L_0003bba6:
    add r7,r6
    .org 0x3bba8-ORIGIN
L_0003bba8:
    mov r6,r2
    .org 0x3bbaa-ORIGIN
L_0003bbaa:
    mov r2,r14
    .org 0x3bbac-ORIGIN
L_0003bbac:
    tst r5,r5
    .org 0x3bbae-ORIGIN
L_0003bbae:
    bt L_0003bbf4
    .org 0x3bbb0-ORIGIN
L_0003bbb0:
    mov.w @(0x0,gbr),r0
    .org 0x3bbb2-ORIGIN
L_0003bbb2:
    exts.w r7,r7
    .org 0x3bbb4-ORIGIN
L_0003bbb4:
    extu.w r0,r6
    .org 0x3bbb6-ORIGIN
L_0003bbb6:
    mov r6,r2
    .org 0x3bbb8-ORIGIN
L_0003bbb8:
    add r7,r2
    .org 0x3bbba-ORIGIN
L_0003bbba:
    cmp/pz r2
    .org 0x3bbbc-ORIGIN
L_0003bbbc:
    bt L_0003bbec
    .org 0x3bbbe-ORIGIN
L_0003bbbe:
    bra L_0003bbf2
    .org 0x3bbc0-ORIGIN
L_0003bbc0:
    mov #0x0,r2
    .org 0x3bbc4-ORIGIN
L_0003bbc4:
    .long 0x00008319
    .org 0x3bbc8-ORIGIN
L_0003bbc8:
    .long 0xffff24ac
    .org 0x3bbcc-ORIGIN
L_0003bbcc:
    .long 0x0000831a
    .org 0x3bbd0-ORIGIN
L_0003bbd0:
    .long 0xffff2448
    .org 0x3bbd4-ORIGIN
L_0003bbd4:
    .long 0xffff424c
    .org 0x3bbd8-ORIGIN
L_0003bbd8:
    .long 0x00008d92
    .org 0x3bbdc-ORIGIN
L_0003bbdc:
    .long 0x000259e4
    .org 0x3bbe0-ORIGIN
L_0003bbe0:
    .long 0x0000865a
    .org 0x3bbe4-ORIGIN
L_0003bbe4:
    .long 0x000224fa
    .org 0x3bbe8-ORIGIN
L_0003bbe8:
    .long 0xffff1048
    .org 0x3bbec-ORIGIN
L_0003bbec:
    exts.w r7,r7
    .org 0x3bbee-ORIGIN
L_0003bbee:
    add r7,r6
    .org 0x3bbf0-ORIGIN
L_0003bbf0:
    mov r6,r2
    .org 0x3bbf2-ORIGIN
L_0003bbf2:
    mov r2,r14
    .org 0x3bbf4-ORIGIN
L_0003bbf4:
    mov.l L_0003bde4,r7
    .org 0x3bbf6-ORIGIN
L_0003bbf6:
    mov #0x17,r0
    .org 0x3bbf8-ORIGIN
L_0003bbf8:
    mov.l L_0003bde8,r4
    .org 0x3bbfa-ORIGIN
L_0003bbfa:
    mov.b @(r0,r7),r6
    .org 0x3bbfc-ORIGIN
L_0003bbfc:
    mov.l L_0003bdec,r2
    .org 0x3bbfe-ORIGIN
L_0003bbfe:
    jsr @r2
    .org 0x3bc00-ORIGIN
L_0003bc00:
    extu.b r6,r5
    .org 0x3bc02-ORIGIN
L_0003bc02:
    extu.b r0,r2
    .org 0x3bc04-ORIGIN
L_0003bc04:
    mov.b r0,@(0x5a,gbr)
    .org 0x3bc06-ORIGIN
L_0003bc06:
    shll8 r2
    .org 0x3bc08-ORIGIN
L_0003bc08:
    cmp/hi r2,r14
    .org 0x3bc0a-ORIGIN
L_0003bc0a:
    bf/s L_0003bc10
    .org 0x3bc0c-ORIGIN
L_0003bc0c:
    mov r14,r5
    .org 0x3bc0e-ORIGIN
L_0003bc0e:
    mov r2,r5
    .org 0x3bc10-ORIGIN
L_0003bc10:
    mov.l L_0003bdf0,r9
    .org 0x3bc12-ORIGIN
L_0003bc12:
    bra L_0003bc78
    .org 0x3bc14-ORIGIN
L_0003bc14:
    nop
    .org 0x3bc16-ORIGIN
L_0003bc16:
    mov.l L_0003bde4,r7
    .org 0x3bc18-ORIGIN
L_0003bc18:
    mov #0x16,r0
    .org 0x3bc1a-ORIGIN
L_0003bc1a:
    mov #0x3,r2
    .org 0x3bc1c-ORIGIN
L_0003bc1c:
    mov.b @(r0,r7),r5
    .org 0x3bc1e-ORIGIN
L_0003bc1e:
    mov #0x40,r6
    .org 0x3bc20-ORIGIN
L_0003bc20:
    extu.b r5,r5
    .org 0x3bc22-ORIGIN
L_0003bc22:
    cmp/hi r5,r6
    .org 0x3bc24-ORIGIN
L_0003bc24:
    bf L_0003bc30
    .org 0x3bc26-ORIGIN
L_0003bc26:
    shlr2 r6
    .org 0x3bc28-ORIGIN
L_0003bc28:
    shlr2 r6
    .org 0x3bc2a-ORIGIN
L_0003bc2a:
    shlr2 r6
    .org 0x3bc2c-ORIGIN
L_0003bc2c:
    bra L_0003bc38
    .org 0x3bc2e-ORIGIN
L_0003bc2e:
    mov r6,r5
    .org 0x3bc30-ORIGIN
L_0003bc30:
    dt r2
    .org 0x3bc32-ORIGIN
L_0003bc32:
    bf/s L_0003bc22
    .org 0x3bc34-ORIGIN
L_0003bc34:
    add #0x40,r6
    .org 0x3bc36-ORIGIN
L_0003bc36:
    mov #0x4,r5
    .org 0x3bc38-ORIGIN
L_0003bc38:
    mov r5,r0
    .org 0x3bc3a-ORIGIN
L_0003bc3a:
    cmp/eq #0x4,r0
    .org 0x3bc3c-ORIGIN
L_0003bc3c:
    bf L_0003bc42
    .org 0x3bc3e-ORIGIN
L_0003bc3e:
    bra L_0003bc76
    .org 0x3bc40-ORIGIN
L_0003bc40:
    mov #0x0,r5
    .org 0x3bc42-ORIGIN
L_0003bc42:
    mov.l L_0003bdf4,r4
    .org 0x3bc44-ORIGIN
L_0003bc44:
    mov.b @(0x3,r4),r0
    .org 0x3bc46-ORIGIN
L_0003bc46:
    mov #0x7,r4
    .org 0x3bc48-ORIGIN
L_0003bc48:
    extu.b r0,r6
    .org 0x3bc4a-ORIGIN
L_0003bc4a:
    cmp/ge r4,r6
    .org 0x3bc4c-ORIGIN
L_0003bc4c:
    bt L_0003bc52
    .org 0x3bc4e-ORIGIN
L_0003bc4e:
    bra L_0003bc66
    .org 0x3bc50-ORIGIN
L_0003bc50:
    mov #0x0,r6
    .org 0x3bc52-ORIGIN
L_0003bc52:
    mov #0xf,r4
    .org 0x3bc54-ORIGIN
L_0003bc54:
    cmp/ge r4,r6
    .org 0x3bc56-ORIGIN
L_0003bc56:
    bt L_0003bc5c
    .org 0x3bc58-ORIGIN
L_0003bc58:
    bra L_0003bc66
    .org 0x3bc5a-ORIGIN
L_0003bc5a:
    mov #0x1,r6
    .org 0x3bc5c-ORIGIN
L_0003bc5c:
    mov #0x16,r2
    .org 0x3bc5e-ORIGIN
L_0003bc5e:
    cmp/ge r2,r6
    .org 0x3bc60-ORIGIN
L_0003bc60:
    bt/s L_0003bc66
    .org 0x3bc62-ORIGIN
L_0003bc62:
    mov #0x3,r6
    .org 0x3bc64-ORIGIN
L_0003bc64:
    mov #0x2,r6
    .org 0x3bc66-ORIGIN
L_0003bc66:
    mov r5,r0
    .org 0x3bc68-ORIGIN
L_0003bc68:
    add #-0x1,r0
    .org 0x3bc6a-ORIGIN
L_0003bc6a:
    mov.l L_0003bdf8,r4
    .org 0x3bc6c-ORIGIN
L_0003bc6c:
    shll2 r0
    .org 0x3bc6e-ORIGIN
L_0003bc6e:
    add r6,r0
    .org 0x3bc70-ORIGIN
L_0003bc70:
    mov.b @(r0,r4),r6
    .org 0x3bc72-ORIGIN
L_0003bc72:
    extu.b r6,r5
    .org 0x3bc74-ORIGIN
L_0003bc74:
    shll8 r5
    .org 0x3bc76-ORIGIN
L_0003bc76:
    mov.l L_0003bdf0,r9
    .org 0x3bc78-ORIGIN
L_0003bc78:
    mov.l L_0003bdfc,r14
    .org 0x3bc7a-ORIGIN
L_0003bc7a:
    mov r5,r0
    .org 0x3bc7c-ORIGIN
L_0003bc7c:
    mov.l L_0003be00,r4
    .org 0x3bc7e-ORIGIN
L_0003bc7e:
    mov.w r0,@(0x2,r9)
    .org 0x3bc80-ORIGIN
L_0003bc80:
    mov.b @r14,r2
    .org 0x3bc82-ORIGIN
L_0003bc82:
    mov.b @(0x3,r4),r0
    .org 0x3bc84-ORIGIN
L_0003bc84:
    mov r0,r13
    .org 0x3bc86-ORIGIN
L_0003bc86:
    mov r2,r0
    .org 0x3bc88-ORIGIN
L_0003bc88:
    tst #0x80,r0
    .org 0x3bc8a-ORIGIN
L_0003bc8a:
    bf L_0003bc98
    .org 0x3bc8c-ORIGIN
L_0003bc8c:
    mov.l L_0003be04,r10
    .org 0x3bc8e-ORIGIN
L_0003bc8e:
    mov r5,r0
    .org 0x3bc90-ORIGIN
L_0003bc90:
    mov.w r0,@(0x4,r10)
    .org 0x3bc92-ORIGIN
L_0003bc92:
    mov r2,r0
    .org 0x3bc94-ORIGIN
L_0003bc94:
    or #0x80,r0
    .org 0x3bc96-ORIGIN
L_0003bc96:
    mov.b r0,@r14
    .org 0x3bc98-ORIGIN
L_0003bc98:
    mov.l L_0003be08,r2
    .org 0x3bc9a-ORIGIN
L_0003bc9a:
    extu.w r5,r5
    .org 0x3bc9c-ORIGIN
L_0003bc9c:
    mov.l L_0003be04,r10
    .org 0x3bc9e-ORIGIN
L_0003bc9e:
    mov.b @r2,r4
    .org 0x3bca0-ORIGIN
L_0003bca0:
    mov #0x4,r2
    .org 0x3bca2-ORIGIN
L_0003bca2:
    mov.w @(0x4,r10),r0
    .org 0x3bca4-ORIGIN
L_0003bca4:
    shll8 r2
    .org 0x3bca6-ORIGIN
L_0003bca6:
    extu.b r4,r4
    .org 0x3bca8-ORIGIN
L_0003bca8:
    extu.w r0,r12
    .org 0x3bcaa-ORIGIN
L_0003bcaa:
    sub r4,r2
    .org 0x3bcac-ORIGIN
L_0003bcac:
    mul.l r12,r2
    .org 0x3bcae-ORIGIN
L_0003bcae:
    sts macl,r0
    .org 0x3bcb0-ORIGIN
L_0003bcb0:
    mul.l r5,r4
    .org 0x3bcb2-ORIGIN
L_0003bcb2:
    sts macl,r2
    .org 0x3bcb4-ORIGIN
L_0003bcb4:
    add r2,r0
    .org 0x3bcb6-ORIGIN
L_0003bcb6:
    mov.l L_0003be0c,r2
    .org 0x3bcb8-ORIGIN
L_0003bcb8:
    jsr @r2
    .org 0x3bcba-ORIGIN
L_0003bcba:
    nop
    .org 0x3bcbc-ORIGIN
L_0003bcbc:
    mov r0,r6
    .org 0x3bcbe-ORIGIN
L_0003bcbe:
    mov.w @(0x2,r9),r0
    .org 0x3bcc0-ORIGIN
L_0003bcc0:
    extu.w r0,r5
    .org 0x3bcc2-ORIGIN
L_0003bcc2:
    cmp/hs r5,r6
    .org 0x3bcc4-ORIGIN
L_0003bcc4:
    bt L_0003bccc
    .org 0x3bcc6-ORIGIN
L_0003bcc6:
    cmp/eq r12,r6
    .org 0x3bcc8-ORIGIN
L_0003bcc8:
    bf L_0003bccc
    .org 0x3bcca-ORIGIN
L_0003bcca:
    add #0x1,r6
    .org 0x3bccc-ORIGIN
L_0003bccc:
    mov r6,r0
    .org 0x3bcce-ORIGIN
L_0003bcce:
    mov.w r0,@(0x4,r10)
    .org 0x3bcd0-ORIGIN
L_0003bcd0:
    extu.w r6,r0
    .org 0x3bcd2-ORIGIN
L_0003bcd2:
    mov.l L_0003be10,r3
    .org 0x3bcd4-ORIGIN
L_0003bcd4:
    shlr8 r0
    .org 0x3bcd6-ORIGIN
L_0003bcd6:
    mov.b r0,@(0x2,r10)
    .org 0x3bcd8-ORIGIN
L_0003bcd8:
    mov.w @(0x2,gbr),r0
    .org 0x3bcda-ORIGIN
L_0003bcda:
    extu.w r0,r6
    .org 0x3bcdc-ORIGIN
L_0003bcdc:
    mov.w @(0x1a,r3),r0
    .org 0x3bcde-ORIGIN
L_0003bcde:
    extu.w r0,r4
    .org 0x3bce0-ORIGIN
L_0003bce0:
    shll2 r4
    .org 0x3bce2-ORIGIN
L_0003bce2:
    cmp/hs r6,r4
    .org 0x3bce4-ORIGIN
L_0003bce4:
    bt L_0003bcee
    .org 0x3bce6-ORIGIN
L_0003bce6:
    mov r13,r0
    .org 0x3bce8-ORIGIN
L_0003bce8:
    mov.l L_0003be00,r2
    .org 0x3bcea-ORIGIN
L_0003bcea:
    bra L_0003bcf4
    .org 0x3bcec-ORIGIN
L_0003bcec:
    or #0x80,r0
    .org 0x3bcee-ORIGIN
L_0003bcee:
    mov r13,r0
    .org 0x3bcf0-ORIGIN
L_0003bcf0:
    and #0x7f,r0
    .org 0x3bcf2-ORIGIN
L_0003bcf2:
    mov.l L_0003be00,r2
    .org 0x3bcf4-ORIGIN
L_0003bcf4:
    mov.l L_0003be00,r6
    .org 0x3bcf6-ORIGIN
L_0003bcf6:
    mov.b r0,@(0x3,r2)
    .org 0x3bcf8-ORIGIN
L_0003bcf8:
    mov.b @(0x3,r6),r0
    .org 0x3bcfa-ORIGIN
L_0003bcfa:
    tst #0x80,r0
    .org 0x3bcfc-ORIGIN
L_0003bcfc:
    movt r0
    .org 0x3bcfe-ORIGIN
L_0003bcfe:
    mov.l L_0003be00,r6
    .org 0x3bd00-ORIGIN
L_0003bd00:
    xor #0x1,r0
    .org 0x3bd02-ORIGIN
L_0003bd02:
    extu.b r0,r4
    .org 0x3bd04-ORIGIN
L_0003bd04:
    mov.b @(0x4,r6),r0
    .org 0x3bd06-ORIGIN
L_0003bd06:
    tst #0x80,r0
    .org 0x3bd08-ORIGIN
L_0003bd08:
    movt r0
    .org 0x3bd0a-ORIGIN
L_0003bd0a:
    xor #0x1,r0
    .org 0x3bd0c-ORIGIN
L_0003bd0c:
    extu.b r0,r6
    .org 0x3bd0e-ORIGIN
L_0003bd0e:
    cmp/eq r6,r4
    .org 0x3bd10-ORIGIN
L_0003bd10:
    bt L_0003bd1c
    .org 0x3bd12-ORIGIN
L_0003bd12:
    mov.l L_0003be00,r6
    .org 0x3bd14-ORIGIN
L_0003bd14:
    mov.l L_0003be00,r4
    .org 0x3bd16-ORIGIN
L_0003bd16:
    mov.b @(0x5,r6),r0
    .org 0x3bd18-ORIGIN
L_0003bd18:
    or #0x20,r0
    .org 0x3bd1a-ORIGIN
L_0003bd1a:
    mov.b r0,@(0x5,r4)
    .org 0x3bd1c-ORIGIN
L_0003bd1c:
    mov.l L_0003be14,r6
    .org 0x3bd1e-ORIGIN
L_0003bd1e:
    mov r5,r1
    .org 0x3bd20-ORIGIN
L_0003bd20:
    shll2 r1
    .org 0x3bd22-ORIGIN
L_0003bd22:
    shll2 r1
    .org 0x3bd24-ORIGIN
L_0003bd24:
    mov.w @r6,r2
    .org 0x3bd26-ORIGIN
L_0003bd26:
    shll2 r1
    .org 0x3bd28-ORIGIN
L_0003bd28:
    shll r1
    .org 0x3bd2a-ORIGIN
L_0003bd2a:
    jsr @r11
    .org 0x3bd2c-ORIGIN
L_0003bd2c:
    extu.w r2,r0
    .org 0x3bd2e-ORIGIN
L_0003bd2e:
    mov #-0x1,r6
    .org 0x3bd30-ORIGIN
L_0003bd30:
    extu.b r6,r6
    .org 0x3bd32-ORIGIN
L_0003bd32:
    cmp/hi r6,r0
    .org 0x3bd34-ORIGIN
L_0003bd34:
    bt L_0003bd54
    .org 0x3bd36-ORIGIN
L_0003bd36:
    mov.l L_0003bdf0,r6
    .org 0x3bd38-ORIGIN
L_0003bd38:
    mov.l L_0003be14,r5
    .org 0x3bd3a-ORIGIN
L_0003bd3a:
    mov.w @(0x2,r6),r0
    .org 0x3bd3c-ORIGIN
L_0003bd3c:
    mov.w @r5,r6
    .org 0x3bd3e-ORIGIN
L_0003bd3e:
    extu.w r0,r1
    .org 0x3bd40-ORIGIN
L_0003bd40:
    mov.l L_0003be18,r2
    .org 0x3bd42-ORIGIN
L_0003bd42:
    shll2 r1
    .org 0x3bd44-ORIGIN
L_0003bd44:
    shll2 r1
    .org 0x3bd46-ORIGIN
L_0003bd46:
    shll2 r1
    .org 0x3bd48-ORIGIN
L_0003bd48:
    shll r1
    .org 0x3bd4a-ORIGIN
L_0003bd4a:
    extu.w r6,r5
    .org 0x3bd4c-ORIGIN
L_0003bd4c:
    jsr @r2
    .org 0x3bd4e-ORIGIN
L_0003bd4e:
    mov r5,r0
    .org 0x3bd50-ORIGIN
L_0003bd50:
    bra L_0003bd56
    .org 0x3bd52-ORIGIN
L_0003bd52:
    mov r0,r2
    .org 0x3bd54-ORIGIN
L_0003bd54:
    mov #-0x1,r2
    .org 0x3bd56-ORIGIN
L_0003bd56:
    mov r2,r6
    .org 0x3bd58-ORIGIN
L_0003bd58:
    mov.l L_0003be10,r2
    .org 0x3bd5a-ORIGIN
L_0003bd5a:
    mov.b r6,@r2
    .org 0x3bd5c-ORIGIN
L_0003bd5c:
    add #0x18,r15
    .org 0x3bd5e-ORIGIN
L_0003bd5e:
    ldc.l @r15+,gbr
    .org 0x3bd60-ORIGIN
L_0003bd60:
    lds.l @r15+,macl
    .org 0x3bd62-ORIGIN
L_0003bd62:
    lds.l @r15+,pr
    .org 0x3bd64-ORIGIN
L_0003bd64:
    mov.l @r15+,r14
    .org 0x3bd66-ORIGIN
L_0003bd66:
    mov.l @r15+,r13
    .org 0x3bd68-ORIGIN
L_0003bd68:
    mov.l @r15+,r12
    .org 0x3bd6a-ORIGIN
L_0003bd6a:
    mov.l @r15+,r11
    .org 0x3bd6c-ORIGIN
L_0003bd6c:
    mov.l @r15+,r10
    .org 0x3bd6e-ORIGIN
L_0003bd6e:
    mov.l @r15+,r9
    .org 0x3bd70-ORIGIN
L_0003bd70:
    rts
    .org 0x3bd72-ORIGIN
L_0003bd72:
    mov.l @r15+,r8
    .org 0x3bde4-ORIGIN
L_0003bde4:
    .long 0xffff11d4
    .org 0x3bde8-ORIGIN
L_0003bde8:
    .long 0x00012c9e
    .org 0x3bdec-ORIGIN
L_0003bdec:
    .long 0x00026388
    .org 0x3bdf0-ORIGIN
L_0003bdf0:
    .long 0xffff1024
    .org 0x3bdf4-ORIGIN
L_0003bdf4:
    .long 0xffff1072
    .org 0x3bdf8-ORIGIN
L_0003bdf8:
    .long 0x0000974e
    .org 0x3bdfc-ORIGIN
L_0003bdfc:
    .long 0xffff5b2e
    .org 0x3be00-ORIGIN
L_0003be00:
    .long 0xffff24ac
    .org 0x3be04-ORIGIN
L_0003be04:
    .long 0xffff55b4
    .org 0x3be08-ORIGIN
L_0003be08:
    .long 0x0000830f
    .org 0x3be0c-ORIGIN
L_0003be0c:
    .long 0x00022508
    .org 0x3be10-ORIGIN
L_0003be10:
    .long 0xffff1048
    .org 0x3be14-ORIGIN
L_0003be14:
    .long 0x00009534
    .org 0x3be18-ORIGIN
L_0003be18:
    .long 0x00021ce0
