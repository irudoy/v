! Complete stock EVAP result writer and its real interpolation and division helpers.
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
    mov.l P_00021dc8,r1
    .org 0x21d6c-ORIGIN
L_00021d6c:
    mov.l P_00021dcc,r2
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
P_00021dc8:
    .byte 0xff
    .org 0x21dc9-ORIGIN
P_00021dc9:
    .byte 0xff
    .org 0x21dca-ORIGIN
P_00021dca:
    .byte 0x98
    .org 0x21dcb-ORIGIN
P_00021dcb:
    .byte 0x18
    .org 0x21dcc-ORIGIN
P_00021dcc:
    .byte 0x00
    .org 0x21dcd-ORIGIN
P_00021dcd:
    .byte 0x00
    .org 0x21dce-ORIGIN
P_00021dce:
    .byte 0x04
    .org 0x21dcf-ORIGIN
P_00021dcf:
    .byte 0x4e
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
    mov.l P_00022030,r1
    .org 0x21fd2-ORIGIN
L_00021fd2:
    mov.l P_00022034,r2
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
P_00022030:
    .byte 0xff
    .org 0x22031-ORIGIN
P_00022031:
    .byte 0xff
    .org 0x22032-ORIGIN
P_00022032:
    .byte 0x98
    .org 0x22033-ORIGIN
P_00022033:
    .byte 0x18
    .org 0x22034-ORIGIN
P_00022034:
    .byte 0x00
    .org 0x22035-ORIGIN
P_00022035:
    .byte 0x00
    .org 0x22036-ORIGIN
P_00022036:
    .byte 0x04
    .org 0x22037-ORIGIN
P_00022037:
    .byte 0x4e
    .org 0x26388-ORIGIN
L_00026388:
    mov.w P_0002639a,r0
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
    mov.l P_0002639c,r6
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
P_0002639a:
    .byte 0x00
    .org 0x2639b-ORIGIN
P_0002639b:
    .byte 0xf0
    .org 0x2639c-ORIGIN
P_0002639c:
    .byte 0x00
    .org 0x2639d-ORIGIN
P_0002639d:
    .byte 0x02
    .org 0x2639e-ORIGIN
P_0002639e:
    .byte 0x6a
    .org 0x2639f-ORIGIN
P_0002639f:
    .byte 0x84
    .org 0x26474-ORIGIN
L_00026474:
    sts.l pr,@-r15
    .org 0x26476-ORIGIN
L_00026476:
    mov.l r4,@-r15
    .org 0x26478-ORIGIN
L_00026478:
    mov r5,r0
    .org 0x2647a-ORIGIN
L_0002647a:
    extu.b r6,r5
    .org 0x2647c-ORIGIN
L_0002647c:
    mov.l P_0002649c,r7
    .org 0x2647e-ORIGIN
L_0002647e:
    jsr @r7
    .org 0x26480-ORIGIN
L_00026480:
    mov #0x7,r4
    .org 0x26482-ORIGIN
L_00026482:
    mov.l @r15+,r6
    .org 0x26484-ORIGIN
L_00026484:
    add r4,r6
    .org 0x26486-ORIGIN
L_00026486:
    mov.b @(0x1,r6),r0
    .org 0x26488-ORIGIN
L_00026488:
    extu.b r0,r2
    .org 0x2648a-ORIGIN
L_0002648a:
    mov r5,r3
    .org 0x2648c-ORIGIN
L_0002648c:
    mov.b @r6,r1
    .org 0x2648e-ORIGIN
L_0002648e:
    lds.l @r15+,pr
    .org 0x26490-ORIGIN
L_00026490:
    mov.l P_00026498,r6
    .org 0x26492-ORIGIN
L_00026492:
    jmp @r6
    .org 0x26494-ORIGIN
L_00026494:
    extu.b r1,r0
    .org 0x26498-ORIGIN
P_00026498:
    .byte 0x00
    .org 0x26499-ORIGIN
P_00026499:
    .byte 0x02
    .org 0x2649a-ORIGIN
P_0002649a:
    .byte 0x67
    .org 0x2649b-ORIGIN
P_0002649b:
    .byte 0x40
    .org 0x2649c-ORIGIN
P_0002649c:
    .byte 0x00
    .org 0x2649d-ORIGIN
P_0002649d:
    .byte 0x02
    .org 0x2649e-ORIGIN
P_0002649e:
    .byte 0x69
    .org 0x2649f-ORIGIN
P_0002649f:
    .byte 0x44
    .org 0x264f8-ORIGIN
L_000264f8:
    sts.l pr,@-r15
    .org 0x264fa-ORIGIN
L_000264fa:
    mov.l r4,@-r15
    .org 0x264fc-ORIGIN
L_000264fc:
    mov r5,r0
    .org 0x264fe-ORIGIN
L_000264fe:
    extu.w r6,r5
    .org 0x26500-ORIGIN
L_00026500:
    mov.l P_00026520,r7
    .org 0x26502-ORIGIN
L_00026502:
    jsr @r7
    .org 0x26504-ORIGIN
L_00026504:
    mov #0x1e,r4
    .org 0x26506-ORIGIN
L_00026506:
    mov.l @r15+,r6
    .org 0x26508-ORIGIN
L_00026508:
    add r4,r6
    .org 0x2650a-ORIGIN
L_0002650a:
    mov.w @(0x2,r6),r0
    .org 0x2650c-ORIGIN
L_0002650c:
    extu.w r0,r2
    .org 0x2650e-ORIGIN
L_0002650e:
    mov r5,r3
    .org 0x26510-ORIGIN
L_00026510:
    mov.w @r6,r1
    .org 0x26512-ORIGIN
L_00026512:
    lds.l @r15+,pr
    .org 0x26514-ORIGIN
L_00026514:
    mov.l P_0002651c,r6
    .org 0x26516-ORIGIN
L_00026516:
    jmp @r6
    .org 0x26518-ORIGIN
L_00026518:
    extu.w r1,r0
    .org 0x2651c-ORIGIN
P_0002651c:
    .byte 0x00
    .org 0x2651d-ORIGIN
P_0002651d:
    .byte 0x02
    .org 0x2651e-ORIGIN
P_0002651e:
    .byte 0x67
    .org 0x2651f-ORIGIN
P_0002651f:
    .byte 0x40
    .org 0x26520-ORIGIN
P_00026520:
    .byte 0x00
    .org 0x26521-ORIGIN
P_00026521:
    .byte 0x02
    .org 0x26522-ORIGIN
P_00026522:
    .byte 0x69
    .org 0x26523-ORIGIN
P_00026523:
    .byte 0x84
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
    .org 0x26944-ORIGIN
L_00026944:
    mov r4,r3
    .org 0x26946-ORIGIN
L_00026946:
    mov.b @(r0,r4),r1
    .org 0x26948-ORIGIN
L_00026948:
    extu.b r1,r1
    .org 0x2694a-ORIGIN
L_0002694a:
    cmp/eq r1,r5
    .org 0x2694c-ORIGIN
L_0002694c:
    bt L_0002697c
    .org 0x2694e-ORIGIN
L_0002694e:
    cmp/hi r1,r5
    .org 0x26950-ORIGIN
L_00026950:
    bf L_00026974
    .org 0x26952-ORIGIN
L_00026952:
    cmp/eq r4,r3
    .org 0x26954-ORIGIN
L_00026954:
    bt L_0002697c
    .org 0x26956-ORIGIN
L_00026956:
    sub r1,r5
    .org 0x26958-ORIGIN
L_00026958:
    shll16 r5
    .org 0x2695a-ORIGIN
L_0002695a:
    add r4,r0
    .org 0x2695c-ORIGIN
L_0002695c:
    mov.b @r0,r1
    .org 0x2695e-ORIGIN
L_0002695e:
    mov.b @(0x1,r0),r0
    .org 0x26960-ORIGIN
L_00026960:
    extu.b r1,r1
    .org 0x26962-ORIGIN
L_00026962:
    extu.b r0,r0
    .org 0x26964-ORIGIN
L_00026964:
    sts.l pr,@-r15
    .org 0x26966-ORIGIN
L_00026966:
    mov.l P_00026980,r2
    .org 0x26968-ORIGIN
L_00026968:
    sub r1,r0
    .org 0x2696a-ORIGIN
L_0002696a:
    jsr @r2
    .org 0x2696c-ORIGIN
L_0002696c:
    mov r5,r1
    .org 0x2696e-ORIGIN
L_0002696e:
    lds.l @r15+,pr
    .org 0x26970-ORIGIN
L_00026970:
    rts
    .org 0x26972-ORIGIN
L_00026972:
    mov r0,r5
    .org 0x26974-ORIGIN
L_00026974:
    add #-0x1,r4
    .org 0x26976-ORIGIN
L_00026976:
    cmp/pz r4
    .org 0x26978-ORIGIN
L_00026978:
    bt L_00026946
    .org 0x2697a-ORIGIN
L_0002697a:
    mov #0x0,r4
    .org 0x2697c-ORIGIN
L_0002697c:
    rts
    .org 0x2697e-ORIGIN
L_0002697e:
    mov #0x0,r5
    .org 0x26980-ORIGIN
P_00026980:
    .byte 0x00
    .org 0x26981-ORIGIN
P_00026981:
    .byte 0x02
    .org 0x26982-ORIGIN
P_00026982:
    .byte 0x6c
    .org 0x26983-ORIGIN
P_00026983:
    .byte 0x78
    .org 0x26984-ORIGIN
L_00026984:
    mov r4,r3
    .org 0x26986-ORIGIN
L_00026986:
    mov.w @(r0,r4),r1
    .org 0x26988-ORIGIN
L_00026988:
    extu.w r1,r1
    .org 0x2698a-ORIGIN
L_0002698a:
    cmp/eq r1,r5
    .org 0x2698c-ORIGIN
L_0002698c:
    bt L_000269bc
    .org 0x2698e-ORIGIN
L_0002698e:
    cmp/hi r1,r5
    .org 0x26990-ORIGIN
L_00026990:
    bf L_000269b4
    .org 0x26992-ORIGIN
L_00026992:
    cmp/eq r4,r3
    .org 0x26994-ORIGIN
L_00026994:
    bt L_000269bc
    .org 0x26996-ORIGIN
L_00026996:
    sub r1,r5
    .org 0x26998-ORIGIN
L_00026998:
    shll16 r5
    .org 0x2699a-ORIGIN
L_0002699a:
    add r4,r0
    .org 0x2699c-ORIGIN
L_0002699c:
    mov.w @r0,r1
    .org 0x2699e-ORIGIN
L_0002699e:
    mov.w @(0x2,r0),r0
    .org 0x269a0-ORIGIN
L_000269a0:
    extu.w r1,r1
    .org 0x269a2-ORIGIN
L_000269a2:
    extu.w r0,r0
    .org 0x269a4-ORIGIN
L_000269a4:
    sts.l pr,@-r15
    .org 0x269a6-ORIGIN
L_000269a6:
    mov.l P_000269c0,r2
    .org 0x269a8-ORIGIN
L_000269a8:
    sub r1,r0
    .org 0x269aa-ORIGIN
L_000269aa:
    jsr @r2
    .org 0x269ac-ORIGIN
L_000269ac:
    mov r5,r1
    .org 0x269ae-ORIGIN
L_000269ae:
    lds.l @r15+,pr
    .org 0x269b0-ORIGIN
L_000269b0:
    rts
    .org 0x269b2-ORIGIN
L_000269b2:
    mov r0,r5
    .org 0x269b4-ORIGIN
L_000269b4:
    add #-0x2,r4
    .org 0x269b6-ORIGIN
L_000269b6:
    cmp/pz r4
    .org 0x269b8-ORIGIN
L_000269b8:
    bt L_00026986
    .org 0x269ba-ORIGIN
L_000269ba:
    mov #0x0,r4
    .org 0x269bc-ORIGIN
L_000269bc:
    rts
    .org 0x269be-ORIGIN
L_000269be:
    mov #0x0,r5
    .org 0x269c0-ORIGIN
P_000269c0:
    .byte 0x00
    .org 0x269c1-ORIGIN
P_000269c1:
    .byte 0x02
    .org 0x269c2-ORIGIN
P_000269c2:
    .byte 0x6c
    .org 0x269c3-ORIGIN
P_000269c3:
    .byte 0x78
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
    .org 0x26c78-ORIGIN
L_00026c78:
    tst r0,r0
    .org 0x26c7a-ORIGIN
L_00026c7a:
    bt L_00026d0a
    .org 0x26c7c-ORIGIN
L_00026c7c:
    mov.l r2,@-r15
    .org 0x26c7e-ORIGIN
L_00026c7e:
    mov #0x0,r2
    .org 0x26c80-ORIGIN
L_00026c80:
    div0u
    .org 0x26c82-ORIGIN
L_00026c82:
    rotcl r1
    .org 0x26c84-ORIGIN
L_00026c84:
    div1 r0,r2
    .org 0x26c86-ORIGIN
L_00026c86:
    rotcl r1
    .org 0x26c88-ORIGIN
L_00026c88:
    div1 r0,r2
    .org 0x26c8a-ORIGIN
L_00026c8a:
    rotcl r1
    .org 0x26c8c-ORIGIN
L_00026c8c:
    div1 r0,r2
    .org 0x26c8e-ORIGIN
L_00026c8e:
    rotcl r1
    .org 0x26c90-ORIGIN
L_00026c90:
    div1 r0,r2
    .org 0x26c92-ORIGIN
L_00026c92:
    rotcl r1
    .org 0x26c94-ORIGIN
L_00026c94:
    div1 r0,r2
    .org 0x26c96-ORIGIN
L_00026c96:
    rotcl r1
    .org 0x26c98-ORIGIN
L_00026c98:
    div1 r0,r2
    .org 0x26c9a-ORIGIN
L_00026c9a:
    rotcl r1
    .org 0x26c9c-ORIGIN
L_00026c9c:
    div1 r0,r2
    .org 0x26c9e-ORIGIN
L_00026c9e:
    rotcl r1
    .org 0x26ca0-ORIGIN
L_00026ca0:
    div1 r0,r2
    .org 0x26ca2-ORIGIN
L_00026ca2:
    rotcl r1
    .org 0x26ca4-ORIGIN
L_00026ca4:
    div1 r0,r2
    .org 0x26ca6-ORIGIN
L_00026ca6:
    rotcl r1
    .org 0x26ca8-ORIGIN
L_00026ca8:
    div1 r0,r2
    .org 0x26caa-ORIGIN
L_00026caa:
    rotcl r1
    .org 0x26cac-ORIGIN
L_00026cac:
    div1 r0,r2
    .org 0x26cae-ORIGIN
L_00026cae:
    rotcl r1
    .org 0x26cb0-ORIGIN
L_00026cb0:
    div1 r0,r2
    .org 0x26cb2-ORIGIN
L_00026cb2:
    rotcl r1
    .org 0x26cb4-ORIGIN
L_00026cb4:
    div1 r0,r2
    .org 0x26cb6-ORIGIN
L_00026cb6:
    rotcl r1
    .org 0x26cb8-ORIGIN
L_00026cb8:
    div1 r0,r2
    .org 0x26cba-ORIGIN
L_00026cba:
    rotcl r1
    .org 0x26cbc-ORIGIN
L_00026cbc:
    div1 r0,r2
    .org 0x26cbe-ORIGIN
L_00026cbe:
    rotcl r1
    .org 0x26cc0-ORIGIN
L_00026cc0:
    div1 r0,r2
    .org 0x26cc2-ORIGIN
L_00026cc2:
    rotcl r1
    .org 0x26cc4-ORIGIN
L_00026cc4:
    div1 r0,r2
    .org 0x26cc6-ORIGIN
L_00026cc6:
    rotcl r1
    .org 0x26cc8-ORIGIN
L_00026cc8:
    div1 r0,r2
    .org 0x26cca-ORIGIN
L_00026cca:
    rotcl r1
    .org 0x26ccc-ORIGIN
L_00026ccc:
    div1 r0,r2
    .org 0x26cce-ORIGIN
L_00026cce:
    rotcl r1
    .org 0x26cd0-ORIGIN
L_00026cd0:
    div1 r0,r2
    .org 0x26cd2-ORIGIN
L_00026cd2:
    rotcl r1
    .org 0x26cd4-ORIGIN
L_00026cd4:
    div1 r0,r2
    .org 0x26cd6-ORIGIN
L_00026cd6:
    rotcl r1
    .org 0x26cd8-ORIGIN
L_00026cd8:
    div1 r0,r2
    .org 0x26cda-ORIGIN
L_00026cda:
    rotcl r1
    .org 0x26cdc-ORIGIN
L_00026cdc:
    div1 r0,r2
    .org 0x26cde-ORIGIN
L_00026cde:
    rotcl r1
    .org 0x26ce0-ORIGIN
L_00026ce0:
    div1 r0,r2
    .org 0x26ce2-ORIGIN
L_00026ce2:
    rotcl r1
    .org 0x26ce4-ORIGIN
L_00026ce4:
    div1 r0,r2
    .org 0x26ce6-ORIGIN
L_00026ce6:
    rotcl r1
    .org 0x26ce8-ORIGIN
L_00026ce8:
    div1 r0,r2
    .org 0x26cea-ORIGIN
L_00026cea:
    rotcl r1
    .org 0x26cec-ORIGIN
L_00026cec:
    div1 r0,r2
    .org 0x26cee-ORIGIN
L_00026cee:
    rotcl r1
    .org 0x26cf0-ORIGIN
L_00026cf0:
    div1 r0,r2
    .org 0x26cf2-ORIGIN
L_00026cf2:
    rotcl r1
    .org 0x26cf4-ORIGIN
L_00026cf4:
    div1 r0,r2
    .org 0x26cf6-ORIGIN
L_00026cf6:
    rotcl r1
    .org 0x26cf8-ORIGIN
L_00026cf8:
    div1 r0,r2
    .org 0x26cfa-ORIGIN
L_00026cfa:
    rotcl r1
    .org 0x26cfc-ORIGIN
L_00026cfc:
    div1 r0,r2
    .org 0x26cfe-ORIGIN
L_00026cfe:
    rotcl r1
    .org 0x26d00-ORIGIN
L_00026d00:
    div1 r0,r2
    .org 0x26d02-ORIGIN
L_00026d02:
    rotcl r1
    .org 0x26d04-ORIGIN
L_00026d04:
    mov.l @r15+,r2
    .org 0x26d06-ORIGIN
L_00026d06:
    rts
    .org 0x26d08-ORIGIN
L_00026d08:
    mov r1,r0
    .org 0x26d0a-ORIGIN
L_00026d0a:
    rts
    .org 0x26d0c-ORIGIN
L_00026d0c:
    mov #0x0,r0
    .org 0xb2096-ORIGIN
L_000b2096:
    mov.l r11,@-r15
    .org 0xb2098-ORIGIN
L_000b2098:
    mov.l r12,@-r15
    .org 0xb209a-ORIGIN
L_000b209a:
    mov.l r13,@-r15
    .org 0xb209c-ORIGIN
L_000b209c:
    mov.l r14,@-r15
    .org 0xb209e-ORIGIN
L_000b209e:
    sts.l pr,@-r15
    .org 0xb20a0-ORIGIN
L_000b20a0:
    sts.l macl,@-r15
    .org 0xb20a2-ORIGIN
L_000b20a2:
    add #-0x10,r15
    .org 0xb20a4-ORIGIN
L_000b20a4:
    mov.l P_000b21b0,r2
    .org 0xb20a6-ORIGIN
L_000b20a6:
    mov r6,r12
    .org 0xb20a8-ORIGIN
L_000b20a8:
    mov r4,r13
    .org 0xb20aa-ORIGIN
L_000b20aa:
    mov.b @r2,r0
    .org 0xb20ac-ORIGIN
L_000b20ac:
    tst #0x40,r0
    .org 0xb20ae-ORIGIN
L_000b20ae:
    bf/s L_000b20c6
    .org 0xb20b0-ORIGIN
L_000b20b0:
    mov r5,r14
    .org 0xb20b2-ORIGIN
L_000b20b2:
    mov.l P_000b21b4,r4
    .org 0xb20b4-ORIGIN
L_000b20b4:
    mov #-0x50,r0
    .org 0xb20b6-ORIGIN
L_000b20b6:
    extu.b r0,r0
    .org 0xb20b8-ORIGIN
L_000b20b8:
    bra L_000b20ca
    .org 0xb20ba-ORIGIN
L_000b20ba:
    mov.w @(r0,r4),r2
    .org 0xb20c6-ORIGIN
L_000b20c6:
    mov.l P_000b21b8,r6
    .org 0xb20c8-ORIGIN
L_000b20c8:
    mov.w @r6,r2
    .org 0xb20ca-ORIGIN
L_000b20ca:
    mov.l P_000b2190,r11
    .org 0xb20cc-ORIGIN
L_000b20cc:
    mov.w P_000b2178,r0
    .org 0xb20ce-ORIGIN
L_000b20ce:
    mov.w r2,@(r0,r11)
    .org 0xb20d0-ORIGIN
L_000b20d0:
    mov.l P_000b21bc,r2
    .org 0xb20d2-ORIGIN
L_000b20d2:
    mov.b @r2,r0
    .org 0xb20d4-ORIGIN
L_000b20d4:
    tst #0x10,r0
    .org 0xb20d6-ORIGIN
L_000b20d6:
    bt L_000b2128
    .org 0xb20d8-ORIGIN
L_000b20d8:
    mov.l P_000b2184,r6
    .org 0xb20da-ORIGIN
L_000b20da:
    mov #0x3c,r0
    .org 0xb20dc-ORIGIN
L_000b20dc:
    mov.b @(r0,r6),r0
    .org 0xb20de-ORIGIN
L_000b20de:
    tst #0x4,r0
    .org 0xb20e0-ORIGIN
L_000b20e0:
    bt L_000b2128
    .org 0xb20e2-ORIGIN
L_000b20e2:
    mov.l P_000b218c,r7
    .org 0xb20e4-ORIGIN
L_000b20e4:
    mov #0x66,r0
    .org 0xb20e6-ORIGIN
L_000b20e6:
    mov.l P_000b21c0,r4
    .org 0xb20e8-ORIGIN
L_000b20e8:
    mov.b @(r0,r7),r6
    .org 0xb20ea-ORIGIN
L_000b20ea:
    mov.l P_000b21c4,r2
    .org 0xb20ec-ORIGIN
L_000b20ec:
    jsr @r2
    .org 0xb20ee-ORIGIN
L_000b20ee:
    extu.b r6,r5
    .org 0xb20f0-ORIGIN
L_000b20f0:
    mov r0,r2
    .org 0xb20f2-ORIGIN
L_000b20f2:
    mov.w P_000b217a,r0
    .org 0xb20f4-ORIGIN
L_000b20f4:
    mov.l P_000b218c,r7
    .org 0xb20f6-ORIGIN
L_000b20f6:
    mov.b r2,@(r0,r11)
    .org 0xb20f8-ORIGIN
L_000b20f8:
    mov #0x65,r0
    .org 0xb20fa-ORIGIN
L_000b20fa:
    mov.b @(r0,r7),r5
    .org 0xb20fc-ORIGIN
L_000b20fc:
    mov #-0x50,r0
    .org 0xb20fe-ORIGIN
L_000b20fe:
    mov.l P_000b21c8,r2
    .org 0xb2100-ORIGIN
L_000b2100:
    extu.b r0,r0
    .org 0xb2102-ORIGIN
L_000b2102:
    mov.l P_000b21b4,r4
    .org 0xb2104-ORIGIN
L_000b2104:
    mov.b @r2,r6
    .org 0xb2106-ORIGIN
L_000b2106:
    mov.w @(r0,r4),r2
    .org 0xb2108-ORIGIN
L_000b2108:
    cmp/hs r6,r5
    .org 0xb210a-ORIGIN
L_000b210a:
    extu.w r2,r6
    .org 0xb210c-ORIGIN
L_000b210c:
    shlr8 r6
    .org 0xb210e-ORIGIN
L_000b210e:
    bt L_000b2122
    .org 0xb2110-ORIGIN
L_000b2110:
    mov.l P_000b21cc,r4
    .org 0xb2112-ORIGIN
L_000b2112:
    mov.l P_000b21d0,r5
    .org 0xb2114-ORIGIN
L_000b2114:
    mov.l P_000b21d4,r2
    .org 0xb2116-ORIGIN
L_000b2116:
    jsr @r2
    .org 0xb2118-ORIGIN
L_000b2118:
    extu.b r6,r6
    .org 0xb211a-ORIGIN
L_000b211a:
    mov r0,r2
    .org 0xb211c-ORIGIN
L_000b211c:
    mov.w P_000b217c,r0
    .org 0xb211e-ORIGIN
L_000b211e:
    bra L_000b215a
    .org 0xb2120-ORIGIN
L_000b2120:
    mov.b r2,@(r0,r11)
    .org 0xb2122-ORIGIN
L_000b2122:
    mov.l P_000b21d8,r4
    .org 0xb2124-ORIGIN
L_000b2124:
    bra L_000b214c
    .org 0xb2126-ORIGIN
L_000b2126:
    nop
    .org 0xb2128-ORIGIN
L_000b2128:
    mov.l P_000b218c,r7
    .org 0xb212a-ORIGIN
L_000b212a:
    mov #0x66,r0
    .org 0xb212c-ORIGIN
L_000b212c:
    mov.l P_000b21dc,r4
    .org 0xb212e-ORIGIN
L_000b212e:
    mov.b @(r0,r7),r6
    .org 0xb2130-ORIGIN
L_000b2130:
    mov.l P_000b21c4,r2
    .org 0xb2132-ORIGIN
L_000b2132:
    jsr @r2
    .org 0xb2134-ORIGIN
L_000b2134:
    extu.b r6,r5
    .org 0xb2136-ORIGIN
L_000b2136:
    mov r0,r6
    .org 0xb2138-ORIGIN
L_000b2138:
    mov.w P_000b217a,r0
    .org 0xb213a-ORIGIN
L_000b213a:
    mov.l P_000b21b4,r4
    .org 0xb213c-ORIGIN
L_000b213c:
    mov.b r6,@(r0,r11)
    .org 0xb213e-ORIGIN
L_000b213e:
    mov #-0x50,r0
    .org 0xb2140-ORIGIN
L_000b2140:
    extu.b r0,r0
    .org 0xb2142-ORIGIN
L_000b2142:
    mov.w @(r0,r4),r2
    .org 0xb2144-ORIGIN
L_000b2144:
    mov.l P_000b21d8,r4
    .org 0xb2146-ORIGIN
L_000b2146:
    extu.w r2,r6
    .org 0xb2148-ORIGIN
L_000b2148:
    shlr8 r6
    .org 0xb214a-ORIGIN
L_000b214a:
    add #0x8,r4
    .org 0xb214c-ORIGIN
L_000b214c:
    mov.l P_000b21d0,r5
    .org 0xb214e-ORIGIN
L_000b214e:
    mov.l P_000b21d4,r2
    .org 0xb2150-ORIGIN
L_000b2150:
    jsr @r2
    .org 0xb2152-ORIGIN
L_000b2152:
    extu.b r6,r6
    .org 0xb2154-ORIGIN
L_000b2154:
    mov r0,r6
    .org 0xb2156-ORIGIN
L_000b2156:
    mov.w P_000b217c,r0
    .org 0xb2158-ORIGIN
L_000b2158:
    mov.b r6,@(r0,r11)
    .org 0xb215a-ORIGIN
L_000b215a:
    mov.w P_000b217e,r0
    .org 0xb215c-ORIGIN
L_000b215c:
    extu.w r14,r14
    .org 0xb215e-ORIGIN
L_000b215e:
    mov.l P_000b21e0,r4
    .org 0xb2160-ORIGIN
L_000b2160:
    mov.w @(r0,r11),r7
    .org 0xb2162-ORIGIN
L_000b2162:
    mov.l P_000b21e4,r5
    .org 0xb2164-ORIGIN
L_000b2164:
    mov.l P_000b21e8,r2
    .org 0xb2166-ORIGIN
L_000b2166:
    jsr @r2
    .org 0xb2168-ORIGIN
L_000b2168:
    extu.w r7,r6
    .org 0xb216a-ORIGIN
L_000b216a:
    extu.w r0,r6
    .org 0xb216c-ORIGIN
L_000b216c:
    mov.w P_000b2180,r0
    .org 0xb216e-ORIGIN
L_000b216e:
    cmp/gt r14,r6
    .org 0xb2170-ORIGIN
L_000b2170:
    bt/s L_000b21ec
    .org 0xb2172-ORIGIN
L_000b2172:
    mov.w r6,@(r0,r11)
    .org 0xb2174-ORIGIN
L_000b2174:
    bra L_000b227a
    .org 0xb2176-ORIGIN
L_000b2176:
    mov #0x0,r2
    .org 0xb2178-ORIGIN
P_000b2178:
    .byte 0x07
    .org 0xb2179-ORIGIN
P_000b2179:
    .byte 0x6a
    .org 0xb217a-ORIGIN
P_000b217a:
    .byte 0x06
    .org 0xb217b-ORIGIN
P_000b217b:
    .byte 0x95
    .org 0xb217c-ORIGIN
P_000b217c:
    .byte 0x06
    .org 0xb217d-ORIGIN
P_000b217d:
    .byte 0x9c
    .org 0xb217e-ORIGIN
P_000b217e:
    .byte 0x03
    .org 0xb217f-ORIGIN
P_000b217f:
    .byte 0x9a
    .org 0xb2180-ORIGIN
P_000b2180:
    .byte 0x09
    .org 0xb2181-ORIGIN
P_000b2181:
    .byte 0x48
    .org 0xb2184-ORIGIN
P_000b2184:
    .byte 0xff
    .org 0xb2185-ORIGIN
P_000b2185:
    .byte 0xff
    .org 0xb2186-ORIGIN
P_000b2186:
    .byte 0x41
    .org 0xb2187-ORIGIN
P_000b2187:
    .byte 0xa9
    .org 0xb218c-ORIGIN
P_000b218c:
    .byte 0xff
    .org 0xb218d-ORIGIN
P_000b218d:
    .byte 0xff
    .org 0xb218e-ORIGIN
P_000b218e:
    .byte 0x10
    .org 0xb218f-ORIGIN
P_000b218f:
    .byte 0x94
    .org 0xb2190-ORIGIN
P_000b2190:
    .byte 0xff
    .org 0xb2191-ORIGIN
P_000b2191:
    .byte 0xff
    .org 0xb2192-ORIGIN
P_000b2192:
    .byte 0x28
    .org 0xb2193-ORIGIN
P_000b2193:
    .byte 0xf8
    .org 0xb21b0-ORIGIN
P_000b21b0:
    .byte 0x00
    .org 0xb21b1-ORIGIN
P_000b21b1:
    .byte 0x00
    .org 0xb21b2-ORIGIN
P_000b21b2:
    .byte 0x89
    .org 0xb21b3-ORIGIN
P_000b21b3:
    .byte 0x3e
    .org 0xb21b4-ORIGIN
P_000b21b4:
    .byte 0xff
    .org 0xb21b5-ORIGIN
P_000b21b5:
    .byte 0xff
    .org 0xb21b6-ORIGIN
P_000b21b6:
    .byte 0x26
    .org 0xb21b7-ORIGIN
P_000b21b7:
    .byte 0x7a
    .org 0xb21b8-ORIGIN
P_000b21b8:
    .byte 0x00
    .org 0xb21b9-ORIGIN
P_000b21b9:
    .byte 0x00
    .org 0xb21ba-ORIGIN
P_000b21ba:
    .byte 0x94
    .org 0xb21bb-ORIGIN
P_000b21bb:
    .byte 0xcc
    .org 0xb21bc-ORIGIN
P_000b21bc:
    .byte 0x00
    .org 0xb21bd-ORIGIN
P_000b21bd:
    .byte 0x00
    .org 0xb21be-ORIGIN
P_000b21be:
    .byte 0x89
    .org 0xb21bf-ORIGIN
P_000b21bf:
    .byte 0x3f
    .org 0xb21c0-ORIGIN
P_000b21c0:
    .byte 0x00
    .org 0xb21c1-ORIGIN
P_000b21c1:
    .byte 0x01
    .org 0xb21c2-ORIGIN
P_000b21c2:
    .byte 0x22
    .org 0xb21c3-ORIGIN
P_000b21c3:
    .byte 0xb2
    .org 0xb21c4-ORIGIN
P_000b21c4:
    .byte 0x00
    .org 0xb21c5-ORIGIN
P_000b21c5:
    .byte 0x02
    .org 0xb21c6-ORIGIN
P_000b21c6:
    .byte 0x63
    .org 0xb21c7-ORIGIN
P_000b21c7:
    .byte 0x88
    .org 0xb21c8-ORIGIN
P_000b21c8:
    .byte 0x00
    .org 0xb21c9-ORIGIN
P_000b21c9:
    .byte 0x00
    .org 0xb21ca-ORIGIN
P_000b21ca:
    .byte 0x85
    .org 0xb21cb-ORIGIN
P_000b21cb:
    .byte 0xc1
    .org 0xb21cc-ORIGIN
P_000b21cc:
    .byte 0x00
    .org 0xb21cd-ORIGIN
P_000b21cd:
    .byte 0x01
    .org 0xb21ce-ORIGIN
P_000b21ce:
    .byte 0x25
    .org 0xb21cf-ORIGIN
P_000b21cf:
    .byte 0x9a
    .org 0xb21d0-ORIGIN
P_000b21d0:
    .byte 0x00
    .org 0xb21d1-ORIGIN
P_000b21d1:
    .byte 0x01
    .org 0xb21d2-ORIGIN
P_000b21d2:
    .byte 0x2a
    .org 0xb21d3-ORIGIN
P_000b21d3:
    .byte 0x5a
    .org 0xb21d4-ORIGIN
P_000b21d4:
    .byte 0x00
    .org 0xb21d5-ORIGIN
P_000b21d5:
    .byte 0x02
    .org 0xb21d6-ORIGIN
P_000b21d6:
    .byte 0x64
    .org 0xb21d7-ORIGIN
P_000b21d7:
    .byte 0x74
    .org 0xb21d8-ORIGIN
P_000b21d8:
    .byte 0x00
    .org 0xb21d9-ORIGIN
P_000b21d9:
    .byte 0x01
    .org 0xb21da-ORIGIN
P_000b21da:
    .byte 0x25
    .org 0xb21db-ORIGIN
P_000b21db:
    .byte 0xa2
    .org 0xb21dc-ORIGIN
P_000b21dc:
    .byte 0x00
    .org 0xb21dd-ORIGIN
P_000b21dd:
    .byte 0x01
    .org 0xb21de-ORIGIN
P_000b21de:
    .byte 0x22
    .org 0xb21df-ORIGIN
P_000b21df:
    .byte 0x82
    .org 0xb21e0-ORIGIN
P_000b21e0:
    .byte 0x00
    .org 0xb21e1-ORIGIN
P_000b21e1:
    .byte 0x01
    .org 0xb21e2-ORIGIN
P_000b21e2:
    .byte 0x52
    .org 0xb21e3-ORIGIN
P_000b21e3:
    .byte 0xd6
    .org 0xb21e4-ORIGIN
P_000b21e4:
    .byte 0x00
    .org 0xb21e5-ORIGIN
P_000b21e5:
    .byte 0x01
    .org 0xb21e6-ORIGIN
P_000b21e6:
    .byte 0x3c
    .org 0xb21e7-ORIGIN
P_000b21e7:
    .byte 0x18
    .org 0xb21e8-ORIGIN
P_000b21e8:
    .byte 0x00
    .org 0xb21e9-ORIGIN
P_000b21e9:
    .byte 0x02
    .org 0xb21ea-ORIGIN
P_000b21ea:
    .byte 0x64
    .org 0xb21eb-ORIGIN
P_000b21eb:
    .byte 0xf8
    .org 0xb21ec-ORIGIN
L_000b21ec:
    extu.w r13,r13
    .org 0xb21ee-ORIGIN
L_000b21ee:
    tst r13,r13
    .org 0xb21f0-ORIGIN
L_000b21f0:
    bt L_000b2278
    .org 0xb21f2-ORIGIN
L_000b21f2:
    mov.l P_000b2464,r5
    .org 0xb21f4-ORIGIN
L_000b21f4:
    mov.w P_000b234a,r0
    .org 0xb21f6-ORIGIN
L_000b21f6:
    mov.b @r5,r2
    .org 0xb21f8-ORIGIN
L_000b21f8:
    mov.w @(r0,r11),r5
    .org 0xb21fa-ORIGIN
L_000b21fa:
    extu.b r2,r4
    .org 0xb21fc-ORIGIN
L_000b21fc:
    extu.w r5,r2
    .org 0xb21fe-ORIGIN
L_000b21fe:
    mov r6,r5
    .org 0xb2200-ORIGIN
L_000b2200:
    mul.l r4,r2
    .org 0xb2202-ORIGIN
L_000b2202:
    sub r14,r5
    .org 0xb2204-ORIGIN
L_000b2204:
    mov r5,r2
    .org 0xb2206-ORIGIN
L_000b2206:
    shlr8 r2
    .org 0xb2208-ORIGIN
L_000b2208:
    sts macl,r4
    .org 0xb220a-ORIGIN
L_000b220a:
    extu.b r5,r6
    .org 0xb220c-ORIGIN
L_000b220c:
    mul.l r4,r2
    .org 0xb220e-ORIGIN
L_000b220e:
    sts macl,r2
    .org 0xb2210-ORIGIN
L_000b2210:
    mul.l r4,r6
    .org 0xb2212-ORIGIN
L_000b2212:
    mov.l P_000b2468,r6
    .org 0xb2214-ORIGIN
L_000b2214:
    sts macl,r5
    .org 0xb2216-ORIGIN
L_000b2216:
    mov.l r5,@(0x4,r15)
    .org 0xb2218-ORIGIN
L_000b2218:
    shlr8 r5
    .org 0xb221a-ORIGIN
L_000b221a:
    add r5,r2
    .org 0xb221c-ORIGIN
L_000b221c:
    cmp/hi r6,r2
    .org 0xb221e-ORIGIN
L_000b221e:
    bt/s L_000b2278
    .org 0xb2220-ORIGIN
L_000b2220:
    mov.l r2,@r15
    .org 0xb2222-ORIGIN
L_000b2222:
    mov.l P_000b246c,r5
    .org 0xb2224-ORIGIN
L_000b2224:
    mov r2,r1
    .org 0xb2226-ORIGIN
L_000b2226:
    shlr8 r1
    .org 0xb2228-ORIGIN
L_000b2228:
    mov r13,r0
    .org 0xb222a-ORIGIN
L_000b222a:
    jsr @r5
    .org 0xb222c-ORIGIN
L_000b222c:
    mov.l r1,@(0x8,r15)
    .org 0xb222e-ORIGIN
L_000b222e:
    mov #0x1f,r2
    .org 0xb2230-ORIGIN
L_000b2230:
    cmp/hi r2,r0
    .org 0xb2232-ORIGIN
L_000b2232:
    bt/s L_000b2278
    .org 0xb2234-ORIGIN
L_000b2234:
    mov r0,r5
    .org 0xb2236-ORIGIN
L_000b2236:
    mov r5,r4
    .org 0xb2238-ORIGIN
L_000b2238:
    mov.l P_000b2470,r5
    .org 0xb223a-ORIGIN
L_000b223a:
    mov.l @(0x8,r15),r1
    .org 0xb223c-ORIGIN
L_000b223c:
    shll16 r4
    .org 0xb223e-ORIGIN
L_000b223e:
    mov.l r4,@(0xc,r15)
    .org 0xb2240-ORIGIN
L_000b2240:
    jsr @r5
    .org 0xb2242-ORIGIN
L_000b2242:
    mov r13,r0
    .org 0xb2244-ORIGIN
L_000b2244:
    mov.l @r15,r2
    .org 0xb2246-ORIGIN
L_000b2246:
    mov r0,r1
    .org 0xb2248-ORIGIN
L_000b2248:
    mov.l @(0x4,r15),r4
    .org 0xb224a-ORIGIN
L_000b224a:
    shll16 r1
    .org 0xb224c-ORIGIN
L_000b224c:
    extu.b r2,r6
    .org 0xb224e-ORIGIN
L_000b224e:
    mov r13,r0
    .org 0xb2250-ORIGIN
L_000b2250:
    shll8 r6
    .org 0xb2252-ORIGIN
L_000b2252:
    extu.b r4,r2
    .org 0xb2254-ORIGIN
L_000b2254:
    or r2,r6
    .org 0xb2256-ORIGIN
L_000b2256:
    mov.l P_000b246c,r2
    .org 0xb2258-ORIGIN
L_000b2258:
    jsr @r2
    .org 0xb225a-ORIGIN
L_000b225a:
    add r6,r1
    .org 0xb225c-ORIGIN
L_000b225c:
    mov.l @(0xc,r15),r4
    .org 0xb225e-ORIGIN
L_000b225e:
    mov #-0x1,r5
    .org 0xb2260-ORIGIN
L_000b2260:
    extu.w r5,r5
    .org 0xb2262-ORIGIN
L_000b2262:
    add r0,r4
    .org 0xb2264-ORIGIN
L_000b2264:
    shlr2 r4
    .org 0xb2266-ORIGIN
L_000b2266:
    shlr2 r4
    .org 0xb2268-ORIGIN
L_000b2268:
    shlr r4
    .org 0xb226a-ORIGIN
L_000b226a:
    cmp/hi r5,r4
    .org 0xb226c-ORIGIN
L_000b226c:
    bt L_000b2270
    .org 0xb226e-ORIGIN
L_000b226e:
    mov r4,r5
    .org 0xb2270-ORIGIN
L_000b2270:
    mov.w P_000b234c,r0
    .org 0xb2272-ORIGIN
L_000b2272:
    mov r5,r2
    .org 0xb2274-ORIGIN
L_000b2274:
    bra L_000b227e
    .org 0xb2276-ORIGIN
L_000b2276:
    mov.w r5,@(r0,r11)
    .org 0xb2278-ORIGIN
L_000b2278:
    mov #-0x1,r2
    .org 0xb227a-ORIGIN
L_000b227a:
    mov.w P_000b234c,r0
    .org 0xb227c-ORIGIN
L_000b227c:
    mov.w r2,@(r0,r11)
    .org 0xb227e-ORIGIN
L_000b227e:
    mov.w P_000b234e,r0
    .org 0xb2280-ORIGIN
L_000b2280:
    extu.w r2,r2
    .org 0xb2282-ORIGIN
L_000b2282:
    mov.b @(r0,r11),r6
    .org 0xb2284-ORIGIN
L_000b2284:
    mov.w P_000b2350,r0
    .org 0xb2286-ORIGIN
L_000b2286:
    extu.b r6,r5
    .org 0xb2288-ORIGIN
L_000b2288:
    mul.l r5,r2
    .org 0xb228a-ORIGIN
L_000b228a:
    mov.b @(r0,r11),r6
    .org 0xb228c-ORIGIN
L_000b228c:
    sts macl,r2
    .org 0xb228e-ORIGIN
L_000b228e:
    extu.b r6,r5
    .org 0xb2290-ORIGIN
L_000b2290:
    mul.l r2,r5
    .org 0xb2292-ORIGIN
L_000b2292:
    mov #-0x1,r5
    .org 0xb2294-ORIGIN
L_000b2294:
    extu.w r5,r5
    .org 0xb2296-ORIGIN
L_000b2296:
    sts macl,r6
    .org 0xb2298-ORIGIN
L_000b2298:
    shlr8 r6
    .org 0xb229a-ORIGIN
L_000b229a:
    shlr2 r6
    .org 0xb229c-ORIGIN
L_000b229c:
    shlr2 r6
    .org 0xb229e-ORIGIN
L_000b229e:
    shlr2 r6
    .org 0xb22a0-ORIGIN
L_000b22a0:
    cmp/hi r5,r6
    .org 0xb22a2-ORIGIN
L_000b22a2:
    bf L_000b22a6
    .org 0xb22a4-ORIGIN
L_000b22a4:
    mov r5,r6
    .org 0xb22a6-ORIGIN
L_000b22a6:
    mov.w r6,@r12
    .org 0xb22a8-ORIGIN
L_000b22a8:
    add #0x10,r15
    .org 0xb22aa-ORIGIN
L_000b22aa:
    lds.l @r15+,macl
    .org 0xb22ac-ORIGIN
L_000b22ac:
    lds.l @r15+,pr
    .org 0xb22ae-ORIGIN
L_000b22ae:
    mov.l @r15+,r14
    .org 0xb22b0-ORIGIN
L_000b22b0:
    mov.l @r15+,r13
    .org 0xb22b2-ORIGIN
L_000b22b2:
    mov.l @r15+,r12
    .org 0xb22b4-ORIGIN
L_000b22b4:
    rts
    .org 0xb22b6-ORIGIN
L_000b22b6:
    mov.l @r15+,r11
    .org 0xb234a-ORIGIN
P_000b234a:
    .byte 0x07
    .org 0xb234b-ORIGIN
P_000b234b:
    .byte 0x6a
    .org 0xb234c-ORIGIN
P_000b234c:
    .byte 0x07
    .org 0xb234d-ORIGIN
P_000b234d:
    .byte 0x20
    .org 0xb234e-ORIGIN
P_000b234e:
    .byte 0x06
    .org 0xb234f-ORIGIN
P_000b234f:
    .byte 0x95
    .org 0xb2350-ORIGIN
P_000b2350:
    .byte 0x06
    .org 0xb2351-ORIGIN
P_000b2351:
    .byte 0x9c
    .org 0xb2464-ORIGIN
P_000b2464:
    .byte 0x00
    .org 0xb2465-ORIGIN
P_000b2465:
    .byte 0x00
    .org 0xb2466-ORIGIN
P_000b2466:
    .byte 0x88
    .org 0xb2467-ORIGIN
P_000b2467:
    .byte 0x13
    .org 0xb2468-ORIGIN
P_000b2468:
    .byte 0x1f
    .org 0xb2469-ORIGIN
P_000b2469:
    .byte 0xff
    .org 0xb246a-ORIGIN
P_000b246a:
    .byte 0xc0
    .org 0xb246b-ORIGIN
P_000b246b:
    .byte 0x00
    .org 0xb246c-ORIGIN
P_000b246c:
    .byte 0x00
    .org 0xb246d-ORIGIN
P_000b246d:
    .byte 0x02
    .org 0xb246e-ORIGIN
P_000b246e:
    .byte 0x1c
    .org 0xb246f-ORIGIN
P_000b246f:
    .byte 0xe0
    .org 0xb2470-ORIGIN
P_000b2470:
    .byte 0x00
    .org 0xb2471-ORIGIN
P_000b2471:
    .byte 0x02
    .org 0xb2472-ORIGIN
P_000b2472:
    .byte 0x1f
    .org 0xb2473-ORIGIN
P_000b2473:
    .byte 0x40
