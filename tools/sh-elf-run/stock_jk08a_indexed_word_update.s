! Exact natural indexed word update and interrupt-mask restoration; selected native RAM writer absence.
    .text
    .balign 4
    .set ORIGIN,0x87fc
    .org 0x87fe-ORIGIN
P_000087fe:
    .byte 0x05
    .org 0x8d92-ORIGIN
P_00008d92:
    .byte 0x7a
    .org 0x52034-ORIGIN
L_00052034:
    stc.l gbr,@-r15
    .org 0x52036-ORIGIN
L_00052036:
    mov.l P_00052174,r0
    .org 0x52038-ORIGIN
L_00052038:
    ldc r0,gbr
    .org 0x5203a-ORIGIN
L_0005203a:
    add #-0x8,r15
    .org 0x5203c-ORIGIN
L_0005203c:
    mov.l P_00052170,r6
    .org 0x5203e-ORIGIN
L_0005203e:
    mov r4,r7
    .org 0x52040-ORIGIN
L_00052040:
    mov.b @r6,r0
    .org 0x52042-ORIGIN
L_00052042:
    tst #0x8,r0
    .org 0x52044-ORIGIN
L_00052044:
    bt/s L_000520e6
    .org 0x52046-ORIGIN
L_00052046:
    extu.b r5,r4
    .org 0x52048-ORIGIN
L_00052048:
    mov.l P_00052180,r6
    .org 0x5204a-ORIGIN
L_0005204a:
    mov.b @r6,r2
    .org 0x5204c-ORIGIN
L_0005204c:
    mov.l P_00052184,r6
    .org 0x5204e-ORIGIN
L_0005204e:
    extu.b r2,r5
    .org 0x52050-ORIGIN
L_00052050:
    shll2 r5
    .org 0x52052-ORIGIN
L_00052052:
    mov.b @(0x4,r6),r0
    .org 0x52054-ORIGIN
L_00052054:
    shll2 r5
    .org 0x52056-ORIGIN
L_00052056:
    shll2 r5
    .org 0x52058-ORIGIN
L_00052058:
    shll r5
    .org 0x5205a-ORIGIN
L_0005205a:
    tst r4,r0
    .org 0x5205c-ORIGIN
L_0005205c:
    bf L_000520de
    .org 0x5205e-ORIGIN
L_0005205e:
    mov.l P_00052178,r2
    .org 0x52060-ORIGIN
L_00052060:
    extu.b r7,r7
    .org 0x52062-ORIGIN
L_00052062:
    mov.w P_00052130,r6
    .org 0x52064-ORIGIN
L_00052064:
    shll r7
    .org 0x52066-ORIGIN
L_00052066:
    mov r7,r0
    .org 0x52068-ORIGIN
L_00052068:
    exts.w r5,r5
    .org 0x5206a-ORIGIN
L_0005206a:
    add r6,r2
    .org 0x5206c-ORIGIN
L_0005206c:
    mov.w @(r0,r2),r6
    .org 0x5206e-ORIGIN
L_0005206e:
    cmp/ge r5,r6
    .org 0x52070-ORIGIN
L_00052070:
    bf L_000520de
    .org 0x52072-ORIGIN
L_00052072:
    mov.l P_00052178,r6
    .org 0x52074-ORIGIN
L_00052074:
    mov.w P_00052132,r0
    .org 0x52076-ORIGIN
L_00052076:
    mov.b @(r0,r6),r2
    .org 0x52078-ORIGIN
L_00052078:
    tst r4,r2
    .org 0x5207a-ORIGIN
L_0005207a:
    bf L_000520de
    .org 0x5207c-ORIGIN
L_0005207c:
    mov.b @(0x12,gbr),r0
    .org 0x5207e-ORIGIN
L_0005207e:
    mov.l r0,@(0x4,r15)
    .org 0x52080-ORIGIN
L_00052080:
    or r4,r0
    .org 0x52082-ORIGIN
L_00052082:
    mov.b r0,@(0x12,gbr)
    .org 0x52084-ORIGIN
L_00052084:
    mov.b @(0x50,gbr),r0
    .org 0x52086-ORIGIN
L_00052086:
    tst r4,r0
    .org 0x52088-ORIGIN
L_00052088:
    bf L_000520e6
    .org 0x5208a-ORIGIN
L_0005208a:
    stc sr,r0
    .org 0x5208c-ORIGIN
L_0005208c:
    shlr2 r0
    .org 0x5208e-ORIGIN
L_0005208e:
    shlr2 r0
    .org 0x52090-ORIGIN
L_00052090:
    and #0xf,r0
    .org 0x52092-ORIGIN
L_00052092:
    mov r0,r2
    .org 0x52094-ORIGIN
L_00052094:
    stc sr,r0
    .org 0x52096-ORIGIN
L_00052096:
    mov.w P_00052128,r5
    .org 0x52098-ORIGIN
L_00052098:
    and r5,r0
    .org 0x5209a-ORIGIN
L_0005209a:
    or #0xf0,r0
    .org 0x5209c-ORIGIN
L_0005209c:
    ldc r0,sr
    .org 0x5209e-ORIGIN
L_0005209e:
    mov.l P_00052188,r6
    .org 0x520a0-ORIGIN
L_000520a0:
    mov r7,r0
    .org 0x520a2-ORIGIN
L_000520a2:
    mov.l r6,@r15
    .org 0x520a4-ORIGIN
L_000520a4:
    add #0x18,r6
    .org 0x520a6-ORIGIN
L_000520a6:
    mov.w @(r0,r6),r5
    .org 0x520a8-ORIGIN
L_000520a8:
    mov #0x62,r6
    .org 0x520aa-ORIGIN
L_000520aa:
    shll2 r6
    .org 0x520ac-ORIGIN
L_000520ac:
    extu.w r5,r4
    .org 0x520ae-ORIGIN
L_000520ae:
    stc gbr,r5
    .org 0x520b0-ORIGIN
L_000520b0:
    add r6,r5
    .org 0x520b2-ORIGIN
L_000520b2:
    mov.w @(r0,r5),r6
    .org 0x520b4-ORIGIN
L_000520b4:
    sub r6,r4
    .org 0x520b6-ORIGIN
L_000520b6:
    cmp/pz r4
    .org 0x520b8-ORIGIN
L_000520b8:
    bt/s L_000520be
    .org 0x520ba-ORIGIN
L_000520ba:
    mov r4,r6
    .org 0x520bc-ORIGIN
L_000520bc:
    mov #0x0,r6
    .org 0x520be-ORIGIN
L_000520be:
    mov.l @r15,r5
    .org 0x520c0-ORIGIN
L_000520c0:
    mov r7,r0
    .org 0x520c2-ORIGIN
L_000520c2:
    add #0x18,r5
    .org 0x520c4-ORIGIN
L_000520c4:
    mov.w r6,@(r0,r5)
    .org 0x520c6-ORIGIN
L_000520c6:
    mov r2,r0
    .org 0x520c8-ORIGIN
L_000520c8:
    and #0xf,r0
    .org 0x520ca-ORIGIN
L_000520ca:
    mov.l r5,@r15
    .org 0x520cc-ORIGIN
L_000520cc:
    shll2 r0
    .org 0x520ce-ORIGIN
L_000520ce:
    shll2 r0
    .org 0x520d0-ORIGIN
L_000520d0:
    stc sr,r2
    .org 0x520d2-ORIGIN
L_000520d2:
    mov.w P_00052128,r5
    .org 0x520d4-ORIGIN
L_000520d4:
    and r5,r2
    .org 0x520d6-ORIGIN
L_000520d6:
    or r0,r2
    .org 0x520d8-ORIGIN
L_000520d8:
    ldc r2,sr
    .org 0x520da-ORIGIN
L_000520da:
    bra L_000520e6
    .org 0x520dc-ORIGIN
L_000520dc:
    nop
    .org 0x520de-ORIGIN
L_000520de:
    mov.b @(0x12,gbr),r0
    .org 0x520e0-ORIGIN
L_000520e0:
    not r4,r2
    .org 0x520e2-ORIGIN
L_000520e2:
    and r2,r0
    .org 0x520e4-ORIGIN
L_000520e4:
    mov.b r0,@(0x12,gbr)
    .org 0x520e6-ORIGIN
L_000520e6:
    add #0x8,r15
    .org 0x520e8-ORIGIN
L_000520e8:
    rts
    .org 0x520ea-ORIGIN
L_000520ea:
    ldc.l @r15+,gbr
    .org 0x52128-ORIGIN
P_00052128:
    .byte 0xff
    .org 0x52129-ORIGIN
P_00052129:
    .byte 0x0f
    .org 0x52130-ORIGIN
P_00052130:
    .byte 0x01
    .org 0x52131-ORIGIN
P_00052131:
    .byte 0xa2
    .org 0x52132-ORIGIN
P_00052132:
    .byte 0x04
    .org 0x52133-ORIGIN
P_00052133:
    .byte 0x73
    .org 0x52170-ORIGIN
P_00052170:
    .byte 0x00
    .org 0x52171-ORIGIN
P_00052171:
    .byte 0x00
    .org 0x52172-ORIGIN
P_00052172:
    .byte 0x8d
    .org 0x52173-ORIGIN
P_00052173:
    .byte 0x92
    .org 0x52174-ORIGIN
P_00052174:
    .byte 0xff
    .org 0x52175-ORIGIN
P_00052175:
    .byte 0xff
    .org 0x52176-ORIGIN
P_00052176:
    .byte 0x12
    .org 0x52177-ORIGIN
P_00052177:
    .byte 0x0e
    .org 0x52178-ORIGIN
P_00052178:
    .byte 0xff
    .org 0x52179-ORIGIN
P_00052179:
    .byte 0xff
    .org 0x5217a-ORIGIN
P_0005217a:
    .byte 0x12
    .org 0x5217b-ORIGIN
P_0005217b:
    .byte 0x8c
    .org 0x52180-ORIGIN
P_00052180:
    .byte 0x00
    .org 0x52181-ORIGIN
P_00052181:
    .byte 0x00
    .org 0x52182-ORIGIN
P_00052182:
    .byte 0x87
    .org 0x52183-ORIGIN
P_00052183:
    .byte 0xfe
    .org 0x52184-ORIGIN
P_00052184:
    .byte 0xff
    .org 0x52185-ORIGIN
P_00052185:
    .byte 0xff
    .org 0x52186-ORIGIN
P_00052186:
    .byte 0x22
    .org 0x52187-ORIGIN
P_00052187:
    .byte 0xdc
    .org 0x52188-ORIGIN
P_00052188:
    .byte 0xff
    .org 0x52189-ORIGIN
P_00052189:
    .byte 0xff
    .org 0x5218a-ORIGIN
P_0005218a:
    .byte 0x23
    .org 0x5218b-ORIGIN
P_0005218b:
    .byte 0x30
