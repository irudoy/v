! Natural CVTC state and duty paths with real curve and quotient/remainder helpers.
    .text
    .balign 4
    .set ORIGIN,0x8614
    .org 0x8615-ORIGIN
P_00008615:
    .byte 0xab
    .org 0x8de1-ORIGIN
P_00008de1:
    .byte 0x0a
    .org 0x9212-ORIGIN
P_00009212:
    .byte 0x22
    .org 0x9213-ORIGIN
P_00009213:
    .byte 0xa2
    .org 0x9214-ORIGIN
P_00009214:
    .byte 0x22
    .org 0x9215-ORIGIN
P_00009215:
    .byte 0xa2
    .org 0x1205a-ORIGIN
P_0001205a:
    .byte 0x66
    .org 0x1205b-ORIGIN
P_0001205b:
    .byte 0x66
    .org 0x1205c-ORIGIN
P_0001205c:
    .byte 0x66
    .org 0x1205d-ORIGIN
P_0001205d:
    .byte 0x6a
    .org 0x1205e-ORIGIN
P_0001205e:
    .byte 0x71
    .org 0x1205f-ORIGIN
P_0001205f:
    .byte 0x7b
    .org 0x12060-ORIGIN
P_00012060:
    .byte 0x80
    .org 0x12061-ORIGIN
P_00012061:
    .byte 0x80
    .org 0x12062-ORIGIN
P_00012062:
    .byte 0x14
    .org 0x12850-ORIGIN
P_00012850:
    .byte 0x32
    .org 0x12851-ORIGIN
P_00012851:
    .byte 0x5a
    .org 0x12852-ORIGIN
P_00012852:
    .byte 0x64
    .org 0x12853-ORIGIN
P_00012853:
    .byte 0x6e
    .org 0x12854-ORIGIN
P_00012854:
    .byte 0x78
    .org 0x12855-ORIGIN
P_00012855:
    .byte 0x82
    .org 0x12856-ORIGIN
P_00012856:
    .byte 0x87
    .org 0x12857-ORIGIN
P_00012857:
    .byte 0xaa
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
    .org 0xc1dec-ORIGIN
L_000c1dec:
    mov.l r12,@-r15
    .org 0xc1dee-ORIGIN
L_000c1dee:
    mov.l r13,@-r15
    .org 0xc1df0-ORIGIN
L_000c1df0:
    mov.l r14,@-r15
    .org 0xc1df2-ORIGIN
L_000c1df2:
    sts.l pr,@-r15
    .org 0xc1df4-ORIGIN
L_000c1df4:
    sts.l macl,@-r15
    .org 0xc1df6-ORIGIN
L_000c1df6:
    add #-0x14,r15
    .org 0xc1df8-ORIGIN
L_000c1df8:
    extu.b r4,r14
    .org 0xc1dfa-ORIGIN
L_000c1dfa:
    mov.l P_000c2010,r13
    .org 0xc1dfc-ORIGIN
L_000c1dfc:
    mov.w P_000c1ef8,r4
    .org 0xc1dfe-ORIGIN
L_000c1dfe:
    mov r14,r0
    .org 0xc1e00-ORIGIN
L_000c1e00:
    mov r13,r2
    .org 0xc1e02-ORIGIN
L_000c1e02:
    mov r14,r12
    .org 0xc1e04-ORIGIN
L_000c1e04:
    add r4,r2
    .org 0xc1e06-ORIGIN
L_000c1e06:
    mov.b @(r0,r2),r6
    .org 0xc1e08-ORIGIN
L_000c1e08:
    tst r6,r6
    .org 0xc1e0a-ORIGIN
L_000c1e0a:
    bf/s L_000c1e34
    .org 0xc1e0c-ORIGIN
L_000c1e0c:
    shll2 r12
    .org 0xc1e0e-ORIGIN
L_000c1e0e:
    mov.l P_000c2014,r5
    .org 0xc1e10-ORIGIN
L_000c1e10:
    mov #0x1b,r0
    .org 0xc1e12-ORIGIN
L_000c1e12:
    mov.b @(r0,r5),r0
    .org 0xc1e14-ORIGIN
L_000c1e14:
    and #0x5,r0
    .org 0xc1e16-ORIGIN
L_000c1e16:
    cmp/eq #0x5,r0
    .org 0xc1e18-ORIGIN
L_000c1e18:
    bf L_000c1e34
    .org 0xc1e1a-ORIGIN
L_000c1e1a:
    mov.l P_000c2018,r2
    .org 0xc1e1c-ORIGIN
L_000c1e1c:
    mov #0x38,r0
    .org 0xc1e1e-ORIGIN
L_000c1e1e:
    mov.b @(r0,r2),r5
    .org 0xc1e20-ORIGIN
L_000c1e20:
    mov r14,r2
    .org 0xc1e22-ORIGIN
L_000c1e22:
    add #0x1,r2
    .org 0xc1e24-ORIGIN
L_000c1e24:
    extu.b r5,r5
    .org 0xc1e26-ORIGIN
L_000c1e26:
    tst r2,r5
    .org 0xc1e28-ORIGIN
L_000c1e28:
    bt L_000c1e34
    .org 0xc1e2a-ORIGIN
L_000c1e2a:
    mov r13,r2
    .org 0xc1e2c-ORIGIN
L_000c1e2c:
    add r4,r2
    .org 0xc1e2e-ORIGIN
L_000c1e2e:
    mov #0x1,r6
    .org 0xc1e30-ORIGIN
L_000c1e30:
    mov r14,r0
    .org 0xc1e32-ORIGIN
L_000c1e32:
    mov.b r6,@(r0,r2)
    .org 0xc1e34-ORIGIN
L_000c1e34:
    extu.b r6,r6
    .org 0xc1e36-ORIGIN
L_000c1e36:
    mov r6,r0
    .org 0xc1e38-ORIGIN
L_000c1e38:
    cmp/eq #0x1,r0
    .org 0xc1e3a-ORIGIN
L_000c1e3a:
    bf L_000c1e68
    .org 0xc1e3c-ORIGIN
L_000c1e3c:
    mov.l P_000c2014,r5
    .org 0xc1e3e-ORIGIN
L_000c1e3e:
    mov #0x1b,r0
    .org 0xc1e40-ORIGIN
L_000c1e40:
    mov.b @(r0,r5),r0
    .org 0xc1e42-ORIGIN
L_000c1e42:
    tst #0x1,r0
    .org 0xc1e44-ORIGIN
L_000c1e44:
    bf L_000c1e4e
    .org 0xc1e46-ORIGIN
L_000c1e46:
    mov r13,r2
    .org 0xc1e48-ORIGIN
L_000c1e48:
    add r4,r2
    .org 0xc1e4a-ORIGIN
L_000c1e4a:
    bra L_000c1e64
    .org 0xc1e4c-ORIGIN
L_000c1e4c:
    mov #0x0,r6
    .org 0xc1e4e-ORIGIN
L_000c1e4e:
    mov.l P_000c2018,r2
    .org 0xc1e50-ORIGIN
L_000c1e50:
    mov #0x38,r0
    .org 0xc1e52-ORIGIN
L_000c1e52:
    mov.b @(r0,r2),r5
    .org 0xc1e54-ORIGIN
L_000c1e54:
    mov r14,r2
    .org 0xc1e56-ORIGIN
L_000c1e56:
    add #0x1,r2
    .org 0xc1e58-ORIGIN
L_000c1e58:
    extu.b r5,r5
    .org 0xc1e5a-ORIGIN
L_000c1e5a:
    tst r2,r5
    .org 0xc1e5c-ORIGIN
L_000c1e5c:
    bf L_000c1e68
    .org 0xc1e5e-ORIGIN
L_000c1e5e:
    mov r13,r2
    .org 0xc1e60-ORIGIN
L_000c1e60:
    add r4,r2
    .org 0xc1e62-ORIGIN
L_000c1e62:
    mov #0x2,r6
    .org 0xc1e64-ORIGIN
L_000c1e64:
    mov r14,r0
    .org 0xc1e66-ORIGIN
L_000c1e66:
    mov.b r6,@(r0,r2)
    .org 0xc1e68-ORIGIN
L_000c1e68:
    extu.b r6,r0
    .org 0xc1e6a-ORIGIN
L_000c1e6a:
    cmp/eq #0x2,r0
    .org 0xc1e6c-ORIGIN
L_000c1e6c:
    bf L_000c1eb6
    .org 0xc1e6e-ORIGIN
L_000c1e6e:
    mov.w P_000c1efa,r2
    .org 0xc1e70-ORIGIN
L_000c1e70:
    mov r13,r5
    .org 0xc1e72-ORIGIN
L_000c1e72:
    mov r14,r0
    .org 0xc1e74-ORIGIN
L_000c1e74:
    shll r0
    .org 0xc1e76-ORIGIN
L_000c1e76:
    add r2,r5
    .org 0xc1e78-ORIGIN
L_000c1e78:
    mov.w @(r0,r5),r2
    .org 0xc1e7a-ORIGIN
L_000c1e7a:
    mov #0x1b,r0
    .org 0xc1e7c-ORIGIN
L_000c1e7c:
    mov.l P_000c2014,r5
    .org 0xc1e7e-ORIGIN
L_000c1e7e:
    tst r2,r2
    .org 0xc1e80-ORIGIN
L_000c1e80:
    bt/s L_000c1e8a
    .org 0xc1e82-ORIGIN
L_000c1e82:
    mov.b @(r0,r5),r5
    .org 0xc1e84-ORIGIN
L_000c1e84:
    mov r5,r0
    .org 0xc1e86-ORIGIN
L_000c1e86:
    tst #0x1,r0
    .org 0xc1e88-ORIGIN
L_000c1e88:
    bf L_000c1e94
    .org 0xc1e8a-ORIGIN
L_000c1e8a:
    mov r13,r2
    .org 0xc1e8c-ORIGIN
L_000c1e8c:
    add r4,r2
    .org 0xc1e8e-ORIGIN
L_000c1e8e:
    mov #0x0,r6
    .org 0xc1e90-ORIGIN
L_000c1e90:
    mov r14,r0
    .org 0xc1e92-ORIGIN
L_000c1e92:
    mov.b r6,@(r0,r2)
    .org 0xc1e94-ORIGIN
L_000c1e94:
    mov r5,r0
    .org 0xc1e96-ORIGIN
L_000c1e96:
    and #0x5,r0
    .org 0xc1e98-ORIGIN
L_000c1e98:
    cmp/eq #0x5,r0
    .org 0xc1e9a-ORIGIN
L_000c1e9a:
    bf L_000c1eb6
    .org 0xc1e9c-ORIGIN
L_000c1e9c:
    mov.l P_000c2018,r2
    .org 0xc1e9e-ORIGIN
L_000c1e9e:
    mov #0x38,r0
    .org 0xc1ea0-ORIGIN
L_000c1ea0:
    mov.b @(r0,r2),r6
    .org 0xc1ea2-ORIGIN
L_000c1ea2:
    mov r14,r2
    .org 0xc1ea4-ORIGIN
L_000c1ea4:
    add #0x1,r2
    .org 0xc1ea6-ORIGIN
L_000c1ea6:
    extu.b r6,r6
    .org 0xc1ea8-ORIGIN
L_000c1ea8:
    tst r2,r6
    .org 0xc1eaa-ORIGIN
L_000c1eaa:
    bt L_000c1eb6
    .org 0xc1eac-ORIGIN
L_000c1eac:
    mov r13,r2
    .org 0xc1eae-ORIGIN
L_000c1eae:
    add r4,r2
    .org 0xc1eb0-ORIGIN
L_000c1eb0:
    mov #0x1,r6
    .org 0xc1eb2-ORIGIN
L_000c1eb2:
    mov r14,r0
    .org 0xc1eb4-ORIGIN
L_000c1eb4:
    mov.b r6,@(r0,r2)
    .org 0xc1eb6-ORIGIN
L_000c1eb6:
    mov r13,r2
    .org 0xc1eb8-ORIGIN
L_000c1eb8:
    add r4,r2
    .org 0xc1eba-ORIGIN
L_000c1eba:
    mov r14,r0
    .org 0xc1ebc-ORIGIN
L_000c1ebc:
    mov.b @(r0,r2),r6
    .org 0xc1ebe-ORIGIN
L_000c1ebe:
    tst r6,r6
    .org 0xc1ec0-ORIGIN
L_000c1ec0:
    bf L_000c1ec6
    .org 0xc1ec2-ORIGIN
L_000c1ec2:
    bra L_000c1fdc
    .org 0xc1ec4-ORIGIN
L_000c1ec4:
    mov #0x0,r5
    .org 0xc1ec6-ORIGIN
L_000c1ec6:
    mov.l P_000c201c,r6
    .org 0xc1ec8-ORIGIN
L_000c1ec8:
    mov #-0x8,r0
    .org 0xc1eca-ORIGIN
L_000c1eca:
    extu.b r0,r0
    .org 0xc1ecc-ORIGIN
L_000c1ecc:
    mov.l P_000c2020,r4
    .org 0xc1ece-ORIGIN
L_000c1ece:
    mov.b @(r0,r6),r7
    .org 0xc1ed0-ORIGIN
L_000c1ed0:
    mov.l P_000c2024,r5
    .org 0xc1ed2-ORIGIN
L_000c1ed2:
    mov.l P_000c2028,r2
    .org 0xc1ed4-ORIGIN
L_000c1ed4:
    jsr @r2
    .org 0xc1ed6-ORIGIN
L_000c1ed6:
    extu.b r7,r6
    .org 0xc1ed8-ORIGIN
L_000c1ed8:
    extu.b r0,r6
    .org 0xc1eda-ORIGIN
L_000c1eda:
    mov.l P_000c2010,r2
    .org 0xc1edc-ORIGIN
L_000c1edc:
    mov.w P_000c1efc,r0
    .org 0xc1ede-ORIGIN
L_000c1ede:
    mov r14,r7
    .org 0xc1ee0-ORIGIN
L_000c1ee0:
    shll r7
    .org 0xc1ee2-ORIGIN
L_000c1ee2:
    mov.b r6,@(r0,r2)
    .org 0xc1ee4-ORIGIN
L_000c1ee4:
    mov.l P_000c202c,r2
    .org 0xc1ee6-ORIGIN
L_000c1ee6:
    mov.b @r2,r0
    .org 0xc1ee8-ORIGIN
L_000c1ee8:
    tst #0x8,r0
    .org 0xc1eea-ORIGIN
L_000c1eea:
    bt L_000c1f6e
    .org 0xc1eec-ORIGIN
L_000c1eec:
    tst r14,r14
    .org 0xc1eee-ORIGIN
L_000c1eee:
    mov.l P_000c2030,r5
    .org 0xc1ef0-ORIGIN
L_000c1ef0:
    bf L_000c1efe
    .org 0xc1ef2-ORIGIN
L_000c1ef2:
    mov.w @r5,r4
    .org 0xc1ef4-ORIGIN
L_000c1ef4:
    bra L_000c1f02
    .org 0xc1ef6-ORIGIN
L_000c1ef6:
    extu.w r4,r4
    .org 0xc1ef8-ORIGIN
P_000c1ef8:
    .byte 0x08
    .org 0xc1ef9-ORIGIN
P_000c1ef9:
    .byte 0x90
    .org 0xc1efa-ORIGIN
P_000c1efa:
    .byte 0x08
    .org 0xc1efb-ORIGIN
P_000c1efb:
    .byte 0x20
    .org 0xc1efc-ORIGIN
P_000c1efc:
    .byte 0x01
    .org 0xc1efd-ORIGIN
P_000c1efd:
    .byte 0xae
    .org 0xc1efe-ORIGIN
L_000c1efe:
    mov.w @(0x2,r5),r0
    .org 0xc1f00-ORIGIN
L_000c1f00:
    extu.w r0,r4
    .org 0xc1f02-ORIGIN
L_000c1f02:
    mov.w P_000c2004,r5
    .org 0xc1f04-ORIGIN
L_000c1f04:
    mov r13,r2
    .org 0xc1f06-ORIGIN
L_000c1f06:
    mov r7,r0
    .org 0xc1f08-ORIGIN
L_000c1f08:
    mov.l P_000c2034,r7
    .org 0xc1f0a-ORIGIN
L_000c1f0a:
    add r5,r2
    .org 0xc1f0c-ORIGIN
L_000c1f0c:
    mov.w @(r0,r2),r5
    .org 0xc1f0e-ORIGIN
L_000c1f0e:
    mov.w P_000c2006,r0
    .org 0xc1f10-ORIGIN
L_000c1f10:
    extu.w r5,r5
    .org 0xc1f12-ORIGIN
L_000c1f12:
    mul.l r4,r5
    .org 0xc1f14-ORIGIN
L_000c1f14:
    mov.l r0,@(0x8,r15)
    .org 0xc1f16-ORIGIN
L_000c1f16:
    sts macl,r2
    .org 0xc1f18-ORIGIN
L_000c1f18:
    mov.l r2,@r15
    .org 0xc1f1a-ORIGIN
L_000c1f1a:
    shlr16 r2
    .org 0xc1f1c-ORIGIN
L_000c1f1c:
    mul.l r2,r6
    .org 0xc1f1e-ORIGIN
L_000c1f1e:
    sts macl,r5
    .org 0xc1f20-ORIGIN
L_000c1f20:
    shll r5
    .org 0xc1f22-ORIGIN
L_000c1f22:
    mov.l r5,@(0x4,r15)
    .org 0xc1f24-ORIGIN
L_000c1f24:
    jsr @r7
    .org 0xc1f26-ORIGIN
L_000c1f26:
    mov r5,r1
    .org 0xc1f28-ORIGIN
L_000c1f28:
    mov r0,r5
    .org 0xc1f2a-ORIGIN
L_000c1f2a:
    mov.l P_000c2010,r1
    .org 0xc1f2c-ORIGIN
L_000c1f2c:
    mov.w P_000c2008,r0
    .org 0xc1f2e-ORIGIN
L_000c1f2e:
    shll16 r5
    .org 0xc1f30-ORIGIN
L_000c1f30:
    mov.l @r15,r2
    .org 0xc1f32-ORIGIN
L_000c1f32:
    mov.b @(r0,r1),r6
    .org 0xc1f34-ORIGIN
L_000c1f34:
    extu.w r2,r4
    .org 0xc1f36-ORIGIN
L_000c1f36:
    mov.l @(0x4,r15),r1
    .org 0xc1f38-ORIGIN
L_000c1f38:
    extu.b r6,r6
    .org 0xc1f3a-ORIGIN
L_000c1f3a:
    mov.l @(0x8,r15),r0
    .org 0xc1f3c-ORIGIN
L_000c1f3c:
    mul.l r4,r6
    .org 0xc1f3e-ORIGIN
L_000c1f3e:
    mov.l P_000c2038,r4
    .org 0xc1f40-ORIGIN
L_000c1f40:
    mov.l r5,@(0xc,r15)
    .org 0xc1f42-ORIGIN
L_000c1f42:
    sts macl,r6
    .org 0xc1f44-ORIGIN
L_000c1f44:
    shll r6
    .org 0xc1f46-ORIGIN
L_000c1f46:
    jsr @r4
    .org 0xc1f48-ORIGIN
L_000c1f48:
    mov.l r6,@(0x10,r15)
    .org 0xc1f4a-ORIGIN
L_000c1f4a:
    mov.l @(0x10,r15),r6
    .org 0xc1f4c-ORIGIN
L_000c1f4c:
    mov r0,r2
    .org 0xc1f4e-ORIGIN
L_000c1f4e:
    shll16 r2
    .org 0xc1f50-ORIGIN
L_000c1f50:
    mov.l P_000c2034,r7
    .org 0xc1f52-ORIGIN
L_000c1f52:
    mov.l @(0x8,r15),r0
    .org 0xc1f54-ORIGIN
L_000c1f54:
    add r2,r6
    .org 0xc1f56-ORIGIN
L_000c1f56:
    jsr @r7
    .org 0xc1f58-ORIGIN
L_000c1f58:
    mov r6,r1
    .org 0xc1f5a-ORIGIN
L_000c1f5a:
    mov.l @(0xc,r15),r5
    .org 0xc1f5c-ORIGIN
L_000c1f5c:
    mov #0x4,r2
    .org 0xc1f5e-ORIGIN
L_000c1f5e:
    shll8 r2
    .org 0xc1f60-ORIGIN
L_000c1f60:
    add r0,r5
    .org 0xc1f62-ORIGIN
L_000c1f62:
    shll16 r2
    .org 0xc1f64-ORIGIN
L_000c1f64:
    cmp/hi r2,r5
    .org 0xc1f66-ORIGIN
L_000c1f66:
    bt L_000c1f6a
    .org 0xc1f68-ORIGIN
L_000c1f68:
    mov r5,r2
    .org 0xc1f6a-ORIGIN
L_000c1f6a:
    bra L_000c1fdc
    .org 0xc1f6c-ORIGIN
L_000c1f6c:
    mov r2,r5
    .org 0xc1f6e-ORIGIN
L_000c1f6e:
    mov.w P_000c200a,r2
    .org 0xc1f70-ORIGIN
L_000c1f70:
    mov r13,r5
    .org 0xc1f72-ORIGIN
L_000c1f72:
    mov r7,r0
    .org 0xc1f74-ORIGIN
L_000c1f74:
    add r2,r5
    .org 0xc1f76-ORIGIN
L_000c1f76:
    add #0x12,r2
    .org 0xc1f78-ORIGIN
L_000c1f78:
    mov.w @(r0,r5),r4
    .org 0xc1f7a-ORIGIN
L_000c1f7a:
    mov r13,r5
    .org 0xc1f7c-ORIGIN
L_000c1f7c:
    add r2,r5
    .org 0xc1f7e-ORIGIN
L_000c1f7e:
    mov.w @(r0,r5),r2
    .org 0xc1f80-ORIGIN
L_000c1f80:
    extu.w r4,r4
    .org 0xc1f82-ORIGIN
L_000c1f82:
    mov.w P_000c200c,r5
    .org 0xc1f84-ORIGIN
L_000c1f84:
    mov r12,r0
    .org 0xc1f86-ORIGIN
L_000c1f86:
    extu.w r2,r2
    .org 0xc1f88-ORIGIN
L_000c1f88:
    add r2,r4
    .org 0xc1f8a-ORIGIN
L_000c1f8a:
    mov.l P_000c203c,r2
    .org 0xc1f8c-ORIGIN
L_000c1f8c:
    add r2,r4
    .org 0xc1f8e-ORIGIN
L_000c1f8e:
    mov r13,r2
    .org 0xc1f90-ORIGIN
L_000c1f90:
    add r5,r2
    .org 0xc1f92-ORIGIN
L_000c1f92:
    mov.l @(r0,r2),r5
    .org 0xc1f94-ORIGIN
L_000c1f94:
    mov #0x8,r2
    .org 0xc1f96-ORIGIN
L_000c1f96:
    shll8 r2
    .org 0xc1f98-ORIGIN
L_000c1f98:
    shll16 r2
    .org 0xc1f9a-ORIGIN
L_000c1f9a:
    shll16 r4
    .org 0xc1f9c-ORIGIN
L_000c1f9c:
    sub r2,r5
    .org 0xc1f9e-ORIGIN
L_000c1f9e:
    add r5,r4
    .org 0xc1fa0-ORIGIN
L_000c1fa0:
    cmp/pl r4
    .org 0xc1fa2-ORIGIN
L_000c1fa2:
    bf/s L_000c1fdc
    .org 0xc1fa4-ORIGIN
L_000c1fa4:
    mov r4,r5
    .org 0xc1fa6-ORIGIN
L_000c1fa6:
    swap.w r5,r2
    .org 0xc1fa8-ORIGIN
L_000c1fa8:
    exts.w r2,r2
    .org 0xc1faa-ORIGIN
L_000c1faa:
    mul.l r2,r6
    .org 0xc1fac-ORIGIN
L_000c1fac:
    extu.w r5,r2
    .org 0xc1fae-ORIGIN
L_000c1fae:
    sts macl,r0
    .org 0xc1fb0-ORIGIN
L_000c1fb0:
    mul.l r2,r6
    .org 0xc1fb2-ORIGIN
L_000c1fb2:
    mov r0,r5
    .org 0xc1fb4-ORIGIN
L_000c1fb4:
    and #0x7f,r0
    .org 0xc1fb6-ORIGIN
L_000c1fb6:
    shll16 r0
    .org 0xc1fb8-ORIGIN
L_000c1fb8:
    sts macl,r6
    .org 0xc1fba-ORIGIN
L_000c1fba:
    shlr2 r5
    .org 0xc1fbc-ORIGIN
L_000c1fbc:
    shlr2 r5
    .org 0xc1fbe-ORIGIN
L_000c1fbe:
    add r0,r6
    .org 0xc1fc0-ORIGIN
L_000c1fc0:
    shlr2 r6
    .org 0xc1fc2-ORIGIN
L_000c1fc2:
    shlr2 r5
    .org 0xc1fc4-ORIGIN
L_000c1fc4:
    shlr2 r6
    .org 0xc1fc6-ORIGIN
L_000c1fc6:
    shlr r5
    .org 0xc1fc8-ORIGIN
L_000c1fc8:
    shlr2 r6
    .org 0xc1fca-ORIGIN
L_000c1fca:
    mov #0x4,r2
    .org 0xc1fcc-ORIGIN
L_000c1fcc:
    shll16 r5
    .org 0xc1fce-ORIGIN
L_000c1fce:
    shlr r6
    .org 0xc1fd0-ORIGIN
L_000c1fd0:
    shll8 r2
    .org 0xc1fd2-ORIGIN
L_000c1fd2:
    add r6,r5
    .org 0xc1fd4-ORIGIN
L_000c1fd4:
    shll16 r2
    .org 0xc1fd6-ORIGIN
L_000c1fd6:
    cmp/hi r2,r5
    .org 0xc1fd8-ORIGIN
L_000c1fd8:
    bf L_000c1fdc
    .org 0xc1fda-ORIGIN
L_000c1fda:
    mov r2,r5
    .org 0xc1fdc-ORIGIN
L_000c1fdc:
    cmp/pz r5
    .org 0xc1fde-ORIGIN
L_000c1fde:
    bt L_000c1fe2
    .org 0xc1fe0-ORIGIN
L_000c1fe0:
    mov #0x0,r5
    .org 0xc1fe2-ORIGIN
L_000c1fe2:
    mov #0x4,r2
    .org 0xc1fe4-ORIGIN
L_000c1fe4:
    shll8 r2
    .org 0xc1fe6-ORIGIN
L_000c1fe6:
    shll16 r2
    .org 0xc1fe8-ORIGIN
L_000c1fe8:
    cmp/gt r2,r5
    .org 0xc1fea-ORIGIN
L_000c1fea:
    bt L_000c1fee
    .org 0xc1fec-ORIGIN
L_000c1fec:
    mov r5,r2
    .org 0xc1fee-ORIGIN
L_000c1fee:
    mov.w P_000c200e,r6
    .org 0xc1ff0-ORIGIN
L_000c1ff0:
    mov r12,r0
    .org 0xc1ff2-ORIGIN
L_000c1ff2:
    add r6,r13
    .org 0xc1ff4-ORIGIN
L_000c1ff4:
    mov.l r2,@(r0,r13)
    .org 0xc1ff6-ORIGIN
L_000c1ff6:
    add #0x14,r15
    .org 0xc1ff8-ORIGIN
L_000c1ff8:
    lds.l @r15+,macl
    .org 0xc1ffa-ORIGIN
L_000c1ffa:
    lds.l @r15+,pr
    .org 0xc1ffc-ORIGIN
L_000c1ffc:
    mov.l @r15+,r14
    .org 0xc1ffe-ORIGIN
L_000c1ffe:
    mov.l @r15+,r13
    .org 0xc2000-ORIGIN
L_000c2000:
    rts
    .org 0xc2002-ORIGIN
L_000c2002:
    mov.l @r15+,r12
    .org 0xc2004-ORIGIN
P_000c2004:
    .byte 0x08
    .org 0xc2005-ORIGIN
P_000c2005:
    .byte 0x8c
    .org 0xc2006-ORIGIN
P_000c2006:
    .byte 0x02
    .org 0xc2007-ORIGIN
P_000c2007:
    .byte 0x71
    .org 0xc2008-ORIGIN
P_000c2008:
    .byte 0x01
    .org 0xc2009-ORIGIN
P_000c2009:
    .byte 0xae
    .org 0xc200a-ORIGIN
P_000c200a:
    .byte 0x07
    .org 0xc200b-ORIGIN
P_000c200b:
    .byte 0xfa
    .org 0xc200c-ORIGIN
P_000c200c:
    .byte 0x08
    .org 0xc200d-ORIGIN
P_000c200d:
    .byte 0x04
    .org 0xc200e-ORIGIN
P_000c200e:
    .byte 0x08
    .org 0xc200f-ORIGIN
P_000c200f:
    .byte 0x18
    .org 0xc2010-ORIGIN
P_000c2010:
    .byte 0xff
    .org 0xc2011-ORIGIN
P_000c2011:
    .byte 0xff
    .org 0xc2012-ORIGIN
P_000c2012:
    .byte 0x12
    .org 0xc2013-ORIGIN
P_000c2013:
    .byte 0x8c
    .org 0xc2014-ORIGIN
P_000c2014:
    .byte 0xff
    .org 0xc2015-ORIGIN
P_000c2015:
    .byte 0xff
    .org 0xc2016-ORIGIN
P_000c2016:
    .byte 0x24
    .org 0xc2017-ORIGIN
P_000c2017:
    .byte 0x70
    .org 0xc2018-ORIGIN
P_000c2018:
    .byte 0xff
    .org 0xc2019-ORIGIN
P_000c2019:
    .byte 0xff
    .org 0xc201a-ORIGIN
P_000c201a:
    .byte 0x12
    .org 0xc201b-ORIGIN
P_000c201b:
    .byte 0x0e
    .org 0xc201c-ORIGIN
P_000c201c:
    .byte 0xff
    .org 0xc201d-ORIGIN
P_000c201d:
    .byte 0xff
    .org 0xc201e-ORIGIN
P_000c201e:
    .byte 0x26
    .org 0xc201f-ORIGIN
P_000c201f:
    .byte 0x7a
    .org 0xc2020-ORIGIN
P_000c2020:
    .byte 0x00
    .org 0xc2021-ORIGIN
P_000c2021:
    .byte 0x01
    .org 0xc2022-ORIGIN
P_000c2022:
    .byte 0x20
    .org 0xc2023-ORIGIN
P_000c2023:
    .byte 0x5a
    .org 0xc2024-ORIGIN
P_000c2024:
    .byte 0x00
    .org 0xc2025-ORIGIN
P_000c2025:
    .byte 0x01
    .org 0xc2026-ORIGIN
P_000c2026:
    .byte 0x28
    .org 0xc2027-ORIGIN
P_000c2027:
    .byte 0x50
    .org 0xc2028-ORIGIN
P_000c2028:
    .byte 0x00
    .org 0xc2029-ORIGIN
P_000c2029:
    .byte 0x02
    .org 0xc202a-ORIGIN
P_000c202a:
    .byte 0x64
    .org 0xc202b-ORIGIN
P_000c202b:
    .byte 0x74
    .org 0xc202c-ORIGIN
P_000c202c:
    .byte 0x00
    .org 0xc202d-ORIGIN
P_000c202d:
    .byte 0x00
    .org 0xc202e-ORIGIN
P_000c202e:
    .byte 0x86
    .org 0xc202f-ORIGIN
P_000c202f:
    .byte 0x15
    .org 0xc2030-ORIGIN
P_000c2030:
    .byte 0x00
    .org 0xc2031-ORIGIN
P_000c2031:
    .byte 0x00
    .org 0xc2032-ORIGIN
P_000c2032:
    .byte 0x92
    .org 0xc2033-ORIGIN
P_000c2033:
    .byte 0x12
    .org 0xc2034-ORIGIN
P_000c2034:
    .byte 0x00
    .org 0xc2035-ORIGIN
P_000c2035:
    .byte 0x02
    .org 0xc2036-ORIGIN
P_000c2036:
    .byte 0x1c
    .org 0xc2037-ORIGIN
P_000c2037:
    .byte 0xe0
    .org 0xc2038-ORIGIN
P_000c2038:
    .byte 0x00
    .org 0xc2039-ORIGIN
P_000c2039:
    .byte 0x02
    .org 0xc203a-ORIGIN
P_000c203a:
    .byte 0x1f
    .org 0xc203b-ORIGIN
P_000c203b:
    .byte 0x40
    .org 0xc203c-ORIGIN
P_000c203c:
    .byte 0xff
    .org 0xc203d-ORIGIN
P_000c203d:
    .byte 0xff
    .org 0xc203e-ORIGIN
P_000c203e:
    .byte 0x00
    .org 0xc203f-ORIGIN
P_000c203f:
    .byte 0x00
    .org 0xc2040-ORIGIN
L_000c2040:
    mov.l r9,@-r15
    .org 0xc2042-ORIGIN
L_000c2042:
    mov.l r10,@-r15
    .org 0xc2044-ORIGIN
L_000c2044:
    mov.l r11,@-r15
    .org 0xc2046-ORIGIN
L_000c2046:
    mov.l r12,@-r15
    .org 0xc2048-ORIGIN
L_000c2048:
    mov.l r13,@-r15
    .org 0xc204a-ORIGIN
L_000c204a:
    mov.l r14,@-r15
    .org 0xc204c-ORIGIN
L_000c204c:
    sts.l pr,@-r15
    .org 0xc204e-ORIGIN
L_000c204e:
    sts.l macl,@-r15
    .org 0xc2050-ORIGIN
L_000c2050:
    mov.l P_000c2288,r9
    .org 0xc2052-ORIGIN
L_000c2052:
    extu.b r4,r10
    .org 0xc2054-ORIGIN
L_000c2054:
    mov.w P_000c21a8,r2
    .org 0xc2056-ORIGIN
L_000c2056:
    mov r10,r0
    .org 0xc2058-ORIGIN
L_000c2058:
    mov r9,r6
    .org 0xc205a-ORIGIN
L_000c205a:
    shll2 r0
    .org 0xc205c-ORIGIN
L_000c205c:
    add r2,r6
    .org 0xc205e-ORIGIN
L_000c205e:
    mov.l @(r0,r6),r12
    .org 0xc2060-ORIGIN
L_000c2060:
    mov #-0x6a,r13
    .org 0xc2062-ORIGIN
L_000c2062:
    extu.b r13,r13
    .org 0xc2064-ORIGIN
L_000c2064:
    mov.l P_000c228c,r6
    .org 0xc2066-ORIGIN
L_000c2066:
    mov r12,r2
    .org 0xc2068-ORIGIN
L_000c2068:
    shlr16 r2
    .org 0xc206a-ORIGIN
L_000c206a:
    mul.l r2,r13
    .org 0xc206c-ORIGIN
L_000c206c:
    mov.l P_000c2290,r2
    .org 0xc206e-ORIGIN
L_000c206e:
    mov #0x74,r0
    .org 0xc2070-ORIGIN
L_000c2070:
    shlr8 r12
    .org 0xc2072-ORIGIN
L_000c2072:
    sts macl,r1
    .org 0xc2074-ORIGIN
L_000c2074:
    mov.b @(r0,r2),r11
    .org 0xc2076-ORIGIN
L_000c2076:
    extu.b r11,r11
    .org 0xc2078-ORIGIN
L_000c2078:
    jsr @r6
    .org 0xc207a-ORIGIN
L_000c207a:
    mov r11,r0
    .org 0xc207c-ORIGIN
L_000c207c:
    extu.b r12,r2
    .org 0xc207e-ORIGIN
L_000c207e:
    mov.l P_000c228c,r6
    .org 0xc2080-ORIGIN
L_000c2080:
    mul.l r2,r13
    .org 0xc2082-ORIGIN
L_000c2082:
    mov r0,r14
    .org 0xc2084-ORIGIN
L_000c2084:
    mov r11,r0
    .org 0xc2086-ORIGIN
L_000c2086:
    mov #0x4,r13
    .org 0xc2088-ORIGIN
L_000c2088:
    sts macl,r1
    .org 0xc208a-ORIGIN
L_000c208a:
    jsr @r6
    .org 0xc208c-ORIGIN
L_000c208c:
    shll8 r13
    .org 0xc208e-ORIGIN
L_000c208e:
    mov #-0x80,r6
    .org 0xc2090-ORIGIN
L_000c2090:
    extu.b r6,r6
    .org 0xc2092-ORIGIN
L_000c2092:
    add r6,r0
    .org 0xc2094-ORIGIN
L_000c2094:
    shlr8 r0
    .org 0xc2096-ORIGIN
L_000c2096:
    add r0,r14
    .org 0xc2098-ORIGIN
L_000c2098:
    cmp/gt r13,r14
    .org 0xc209a-ORIGIN
L_000c209a:
    bf L_000c209e
    .org 0xc209c-ORIGIN
L_000c209c:
    mov r13,r14
    .org 0xc209e-ORIGIN
L_000c209e:
    mov.w P_000c21aa,r6
    .org 0xc20a0-ORIGIN
L_000c20a0:
    extu.w r14,r4
    .org 0xc20a2-ORIGIN
L_000c20a2:
    mov r10,r14
    .org 0xc20a4-ORIGIN
L_000c20a4:
    shll r14
    .org 0xc20a6-ORIGIN
L_000c20a6:
    mov r9,r2
    .org 0xc20a8-ORIGIN
L_000c20a8:
    add r6,r2
    .org 0xc20aa-ORIGIN
L_000c20aa:
    mov.l P_000c2294,r6
    .org 0xc20ac-ORIGIN
L_000c20ac:
    mov r14,r0
    .org 0xc20ae-ORIGIN
L_000c20ae:
    mov.w r4,@(r0,r2)
    .org 0xc20b0-ORIGIN
L_000c20b0:
    mov #0x38,r0
    .org 0xc20b2-ORIGIN
L_000c20b2:
    mov.b @(r0,r6),r2
    .org 0xc20b4-ORIGIN
L_000c20b4:
    mov r10,r7
    .org 0xc20b6-ORIGIN
L_000c20b6:
    add #0x1,r7
    .org 0xc20b8-ORIGIN
L_000c20b8:
    extu.b r2,r2
    .org 0xc20ba-ORIGIN
L_000c20ba:
    tst r7,r2
    .org 0xc20bc-ORIGIN
L_000c20bc:
    bt L_000c20dc
    .org 0xc20be-ORIGIN
L_000c20be:
    mov.l P_000c2298,r6
    .org 0xc20c0-ORIGIN
L_000c20c0:
    mov #0x38,r0
    .org 0xc20c2-ORIGIN
L_000c20c2:
    mov.b @(r0,r6),r2
    .org 0xc20c4-ORIGIN
L_000c20c4:
    extu.b r2,r2
    .org 0xc20c6-ORIGIN
L_000c20c6:
    tst r7,r2
    .org 0xc20c8-ORIGIN
L_000c20c8:
    bf L_000c20dc
    .org 0xc20ca-ORIGIN
L_000c20ca:
    mov.w P_000c21ac,r6
    .org 0xc20cc-ORIGIN
L_000c20cc:
    mov r9,r5
    .org 0xc20ce-ORIGIN
L_000c20ce:
    mov r14,r0
    .org 0xc20d0-ORIGIN
L_000c20d0:
    add r6,r5
    .org 0xc20d2-ORIGIN
L_000c20d2:
    mov.w @(r0,r5),r2
    .org 0xc20d4-ORIGIN
L_000c20d4:
    add #0x8,r6
    .org 0xc20d6-ORIGIN
L_000c20d6:
    mov r9,r5
    .org 0xc20d8-ORIGIN
L_000c20d8:
    add r6,r5
    .org 0xc20da-ORIGIN
L_000c20da:
    mov.w r2,@(r0,r5)
    .org 0xc20dc-ORIGIN
L_000c20dc:
    mov.w P_000c21ae,r6
    .org 0xc20de-ORIGIN
L_000c20de:
    mov r9,r2
    .org 0xc20e0-ORIGIN
L_000c20e0:
    mov r10,r0
    .org 0xc20e2-ORIGIN
L_000c20e2:
    add r6,r2
    .org 0xc20e4-ORIGIN
L_000c20e4:
    mov.b @(r0,r2),r6
    .org 0xc20e6-ORIGIN
L_000c20e6:
    extu.b r6,r0
    .org 0xc20e8-ORIGIN
L_000c20e8:
    tst r0,r0
    .org 0xc20ea-ORIGIN
L_000c20ea:
    bf L_000c20f0
    .org 0xc20ec-ORIGIN
L_000c20ec:
    bra L_000c2130
    .org 0xc20ee-ORIGIN
L_000c20ee:
    mov #0x0,r4
    .org 0xc20f0-ORIGIN
L_000c20f0:
    cmp/eq #0x1,r0
    .org 0xc20f2-ORIGIN
L_000c20f2:
    bt L_000c2130
    .org 0xc20f4-ORIGIN
L_000c20f4:
    mov.l P_000c2298,r6
    .org 0xc20f6-ORIGIN
L_000c20f6:
    mov #0x38,r0
    .org 0xc20f8-ORIGIN
L_000c20f8:
    mov.b @(r0,r6),r2
    .org 0xc20fa-ORIGIN
L_000c20fa:
    extu.b r2,r6
    .org 0xc20fc-ORIGIN
L_000c20fc:
    tst r7,r6
    .org 0xc20fe-ORIGIN
L_000c20fe:
    bf L_000c2130
    .org 0xc2100-ORIGIN
L_000c2100:
    mov.w P_000c21ac,r2
    .org 0xc2102-ORIGIN
L_000c2102:
    mov r9,r5
    .org 0xc2104-ORIGIN
L_000c2104:
    mov r14,r0
    .org 0xc2106-ORIGIN
L_000c2106:
    add r2,r5
    .org 0xc2108-ORIGIN
L_000c2108:
    mov.w @(r0,r5),r6
    .org 0xc210a-ORIGIN
L_000c210a:
    add #0x8,r2
    .org 0xc210c-ORIGIN
L_000c210c:
    mov.l P_000c229c,r5
    .org 0xc210e-ORIGIN
L_000c210e:
    extu.w r6,r4
    .org 0xc2110-ORIGIN
L_000c2110:
    mov r9,r6
    .org 0xc2112-ORIGIN
L_000c2112:
    add r2,r6
    .org 0xc2114-ORIGIN
L_000c2114:
    mov.w @(r0,r6),r2
    .org 0xc2116-ORIGIN
L_000c2116:
    extu.w r2,r6
    .org 0xc2118-ORIGIN
L_000c2118:
    mov.b @r5,r2
    .org 0xc211a-ORIGIN
L_000c211a:
    extu.b r2,r2
    .org 0xc211c-ORIGIN
L_000c211c:
    mul.l r6,r2
    .org 0xc211e-ORIGIN
L_000c211e:
    sts macl,r6
    .org 0xc2120-ORIGIN
L_000c2120:
    shlr8 r6
    .org 0xc2122-ORIGIN
L_000c2122:
    swap.w r6,r2
    .org 0xc2124-ORIGIN
L_000c2124:
    exts.b r2,r6
    .org 0xc2126-ORIGIN
L_000c2126:
    xtrct r6,r2
    .org 0xc2128-ORIGIN
L_000c2128:
    sub r2,r4
    .org 0xc212a-ORIGIN
L_000c212a:
    cmp/pz r4
    .org 0xc212c-ORIGIN
L_000c212c:
    bt L_000c2130
    .org 0xc212e-ORIGIN
L_000c212e:
    mov #0x0,r4
    .org 0xc2130-ORIGIN
L_000c2130:
    cmp/gt r13,r4
    .org 0xc2132-ORIGIN
L_000c2132:
    bf/s L_000c2138
    .org 0xc2134-ORIGIN
L_000c2134:
    mov r4,r2
    .org 0xc2136-ORIGIN
L_000c2136:
    mov r13,r2
    .org 0xc2138-ORIGIN
L_000c2138:
    mov.w P_000c21ac,r6
    .org 0xc213a-ORIGIN
L_000c213a:
    mov r14,r0
    .org 0xc213c-ORIGIN
L_000c213c:
    add r6,r9
    .org 0xc213e-ORIGIN
L_000c213e:
    mov.w r2,@(r0,r9)
    .org 0xc2140-ORIGIN
L_000c2140:
    lds.l @r15+,macl
    .org 0xc2142-ORIGIN
L_000c2142:
    lds.l @r15+,pr
    .org 0xc2144-ORIGIN
L_000c2144:
    mov.l @r15+,r14
    .org 0xc2146-ORIGIN
L_000c2146:
    mov.l @r15+,r13
    .org 0xc2148-ORIGIN
L_000c2148:
    mov.l @r15+,r12
    .org 0xc214a-ORIGIN
L_000c214a:
    mov.l @r15+,r11
    .org 0xc214c-ORIGIN
L_000c214c:
    mov.l @r15+,r10
    .org 0xc214e-ORIGIN
L_000c214e:
    rts
    .org 0xc2150-ORIGIN
L_000c2150:
    mov.l @r15+,r9
    .org 0xc21a8-ORIGIN
P_000c21a8:
    .byte 0x08
    .org 0xc21a9-ORIGIN
P_000c21a9:
    .byte 0x18
    .org 0xc21aa-ORIGIN
P_000c21aa:
    .byte 0x09
    .org 0xc21ab-ORIGIN
P_000c21ab:
    .byte 0xe4
    .org 0xc21ac-ORIGIN
P_000c21ac:
    .byte 0x08
    .org 0xc21ad-ORIGIN
P_000c21ad:
    .byte 0x20
    .org 0xc21ae-ORIGIN
P_000c21ae:
    .byte 0x08
    .org 0xc21af-ORIGIN
P_000c21af:
    .byte 0x90
    .org 0xc2288-ORIGIN
P_000c2288:
    .byte 0xff
    .org 0xc2289-ORIGIN
P_000c2289:
    .byte 0xff
    .org 0xc228a-ORIGIN
P_000c228a:
    .byte 0x12
    .org 0xc228b-ORIGIN
P_000c228b:
    .byte 0x8c
    .org 0xc228c-ORIGIN
P_000c228c:
    .byte 0x00
    .org 0xc228d-ORIGIN
P_000c228d:
    .byte 0x02
    .org 0xc228e-ORIGIN
P_000c228e:
    .byte 0x1c
    .org 0xc228f-ORIGIN
P_000c228f:
    .byte 0xe0
    .org 0xc2290-ORIGIN
P_000c2290:
    .byte 0xff
    .org 0xc2291-ORIGIN
P_000c2291:
    .byte 0xff
    .org 0xc2292-ORIGIN
P_000c2292:
    .byte 0x10
    .org 0xc2293-ORIGIN
P_000c2293:
    .byte 0x94
    .org 0xc2294-ORIGIN
P_000c2294:
    .byte 0xff
    .org 0xc2295-ORIGIN
P_000c2295:
    .byte 0xff
    .org 0xc2296-ORIGIN
P_000c2296:
    .byte 0x12
    .org 0xc2297-ORIGIN
P_000c2297:
    .byte 0x4c
    .org 0xc2298-ORIGIN
P_000c2298:
    .byte 0xff
    .org 0xc2299-ORIGIN
P_000c2299:
    .byte 0xff
    .org 0xc229a-ORIGIN
P_000c229a:
    .byte 0x12
    .org 0xc229b-ORIGIN
P_000c229b:
    .byte 0x0e
    .org 0xc229c-ORIGIN
P_000c229c:
    .byte 0x00
    .org 0xc229d-ORIGIN
P_000c229d:
    .byte 0x00
    .org 0xc229e-ORIGIN
P_000c229e:
    .byte 0x8d
    .org 0xc229f-ORIGIN
P_000c229f:
    .byte 0xe1
