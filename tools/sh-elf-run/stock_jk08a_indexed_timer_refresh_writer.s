! Complete stock 9018C leaf with exact native850C MOV.W and natural R14/GBR/frame restoration.
    .text
    .balign 4
    .set ORIGIN,0x9018c
    .org 0x9018c-ORIGIN
L_0009018c:
    mov.l r14,@-r15
    .org 0x9018e-ORIGIN
L_0009018e:
    stc.l gbr,@-r15
    .org 0x90190-ORIGIN
L_00090190:
    mov.l P_00090400,r0
    .org 0x90192-ORIGIN
L_00090192:
    ldc r0,gbr
    .org 0x90194-ORIGIN
L_00090194:
    add #-0x4,r15
    .org 0x90196-ORIGIN
L_00090196:
    mov.l P_00090404,r1
    .org 0x90198-ORIGIN
L_00090198:
    mov r4,r7
    .org 0x9019a-ORIGIN
L_0009019a:
    mov.w P_00090250,r0
    .org 0x9019c-ORIGIN
L_0009019c:
    add #0x1,r4
    .org 0x9019e-ORIGIN
L_0009019e:
    mov r7,r14
    .org 0x901a0-ORIGIN
L_000901a0:
    mov.b @(r0,r1),r2
    .org 0x901a2-ORIGIN
L_000901a2:
    extu.b r2,r6
    .org 0x901a4-ORIGIN
L_000901a4:
    tst r4,r6
    .org 0x901a6-ORIGIN
L_000901a6:
    bf/s L_00090240
    .org 0x901a8-ORIGIN
L_000901a8:
    add #0x1,r14
    .org 0x901aa-ORIGIN
L_000901aa:
    tst r5,r5
    .org 0x901ac-ORIGIN
L_000901ac:
    bt L_00090224
    .org 0x901ae-ORIGIN
L_000901ae:
    mov.b @(0x55,gbr),r0
    .org 0x901b0-ORIGIN
L_000901b0:
    extu.b r0,r5
    .org 0x901b2-ORIGIN
L_000901b2:
    tst r4,r5
    .org 0x901b4-ORIGIN
L_000901b4:
    bf L_000901f4
    .org 0x901b6-ORIGIN
L_000901b6:
    mov.b @(0x54,gbr),r0
    .org 0x901b8-ORIGIN
L_000901b8:
    extu.b r0,r2
    .org 0x901ba-ORIGIN
L_000901ba:
    tst r4,r2
    .org 0x901bc-ORIGIN
L_000901bc:
    bf L_000901f4
    .org 0x901be-ORIGIN
L_000901be:
    stc sr,r0
    .org 0x901c0-ORIGIN
L_000901c0:
    shlr2 r0
    .org 0x901c2-ORIGIN
L_000901c2:
    shlr2 r0
    .org 0x901c4-ORIGIN
L_000901c4:
    and #0xf,r0
    .org 0x901c6-ORIGIN
L_000901c6:
    mov r0,r2
    .org 0x901c8-ORIGIN
L_000901c8:
    stc sr,r0
    .org 0x901ca-ORIGIN
L_000901ca:
    mov.w P_00090252,r3
    .org 0x901cc-ORIGIN
L_000901cc:
    and r3,r0
    .org 0x901ce-ORIGIN
L_000901ce:
    or #0xf0,r0
    .org 0x901d0-ORIGIN
L_000901d0:
    ldc r0,sr
    .org 0x901d2-ORIGIN
L_000901d2:
    or r14,r5
    .org 0x901d4-ORIGIN
L_000901d4:
    mov r5,r0
    .org 0x901d6-ORIGIN
L_000901d6:
    mov.w P_00090254,r5
    .org 0x901d8-ORIGIN
L_000901d8:
    mov.b r0,@(0x55,gbr)
    .org 0x901da-ORIGIN
L_000901da:
    mov.b @r5,r0
    .org 0x901dc-ORIGIN
L_000901dc:
    or #0x80,r0
    .org 0x901de-ORIGIN
L_000901de:
    mov.b r0,@r5
    .org 0x901e0-ORIGIN
L_000901e0:
    mov r2,r0
    .org 0x901e2-ORIGIN
L_000901e2:
    and #0xf,r0
    .org 0x901e4-ORIGIN
L_000901e4:
    shll2 r0
    .org 0x901e6-ORIGIN
L_000901e6:
    shll2 r0
    .org 0x901e8-ORIGIN
L_000901e8:
    stc sr,r2
    .org 0x901ea-ORIGIN
L_000901ea:
    and r3,r2
    .org 0x901ec-ORIGIN
L_000901ec:
    or r0,r2
    .org 0x901ee-ORIGIN
L_000901ee:
    ldc r2,sr
    .org 0x901f0-ORIGIN
L_000901f0:
    bra L_000901fc
    .org 0x901f2-ORIGIN
L_000901f2:
    nop
    .org 0x901f4-ORIGIN
L_000901f4:
    or r14,r5
    .org 0x901f6-ORIGIN
L_000901f6:
    mov r5,r0
    .org 0x901f8-ORIGIN
L_000901f8:
    mov.w P_00090254,r5
    .org 0x901fa-ORIGIN
L_000901fa:
    mov.b r0,@(0x55,gbr)
    .org 0x901fc-ORIGIN
L_000901fc:
    mov.b @(0x1,r5),r0
    .org 0x901fe-ORIGIN
L_000901fe:
    extu.b r0,r0
    .org 0x90200-ORIGIN
L_00090200:
    shlr2 r0
    .org 0x90202-ORIGIN
L_00090202:
    shlr2 r0
    .org 0x90204-ORIGIN
L_00090204:
    and #0x3,r0
    .org 0x90206-ORIGIN
L_00090206:
    tst r4,r0
    .org 0x90208-ORIGIN
L_00090208:
    bt L_0009022e
    .org 0x9020a-ORIGIN
L_0009020a:
    mov.l P_000903f8,r2
    .org 0x9020c-ORIGIN
L_0009020c:
    mov #-0x1b,r6
    .org 0x9020e-ORIGIN
L_0009020e:
    extu.b r6,r6
    .org 0x90210-ORIGIN
L_00090210:
    mov r7,r0
    .org 0x90212-ORIGIN
L_00090212:
    add r6,r2
    .org 0x90214-ORIGIN
L_00090214:
    mov.b @(r0,r2),r6
    .org 0x90216-ORIGIN
L_00090216:
    tst r6,r6
    .org 0x90218-ORIGIN
L_00090218:
    bf L_00090248
    .org 0x9021a-ORIGIN
L_0009021a:
    mov.w P_00090250,r0
    .org 0x9021c-ORIGIN
L_0009021c:
    mov.b @(r0,r1),r2
    .org 0x9021e-ORIGIN
L_0009021e:
    or r14,r2
    .org 0x90220-ORIGIN
L_00090220:
    bra L_00090248
    .org 0x90222-ORIGIN
L_00090222:
    mov.b r2,@(r0,r1)
    .org 0x90224-ORIGIN
L_00090224:
    mov.b @(0x55,gbr),r0
    .org 0x90226-ORIGIN
L_00090226:
    not r14,r2
    .org 0x90228-ORIGIN
L_00090228:
    mov.l r0,@r15
    .org 0x9022a-ORIGIN
L_0009022a:
    and r2,r0
    .org 0x9022c-ORIGIN
L_0009022c:
    mov.b r0,@(0x55,gbr)
    .org 0x9022e-ORIGIN
L_0009022e:
    mov.l P_000903f8,r2
    .org 0x90230-ORIGIN
L_00090230:
    mov #-0x1b,r6
    .org 0x90232-ORIGIN
L_00090232:
    mov.l P_000903fc,r5
    .org 0x90234-ORIGIN
L_00090234:
    extu.b r6,r6
    .org 0x90236-ORIGIN
L_00090236:
    add r6,r2
    .org 0x90238-ORIGIN
L_00090238:
    mov r7,r0
    .org 0x9023a-ORIGIN
L_0009023a:
    mov.b @r5,r6
    .org 0x9023c-ORIGIN
L_0009023c:
    bra L_00090248
    .org 0x9023e-ORIGIN
L_0009023e:
    mov.b r6,@(r0,r2)
    .org 0x90240-ORIGIN
L_00090240:
    mov.b @(0x55,gbr),r0
    .org 0x90242-ORIGIN
L_00090242:
    not r14,r2
    .org 0x90244-ORIGIN
L_00090244:
    and r2,r0
    .org 0x90246-ORIGIN
L_00090246:
    mov.b r0,@(0x55,gbr)
    .org 0x90248-ORIGIN
L_00090248:
    add #0x4,r15
    .org 0x9024a-ORIGIN
L_0009024a:
    ldc.l @r15+,gbr
    .org 0x9024c-ORIGIN
L_0009024c:
    rts
    .org 0x9024e-ORIGIN
L_0009024e:
    mov.l @r15+,r14
    .org 0x90250-ORIGIN
P_00090250:
    .word 0x0c89
    .org 0x90252-ORIGIN
P_00090252:
    .word 0xff0f
    .org 0x90254-ORIGIN
P_00090254:
    .word 0x850c
    .org 0x903f8-ORIGIN
P_000903f8:
    .long 0xffff42d3
    .org 0x903fc-ORIGIN
P_000903fc:
    .long 0x00008e23
    .org 0x90400-ORIGIN
P_00090400:
    .long 0xffff4124
    .org 0x90404-ORIGIN
P_00090404:
    .long 0xffff28f8
