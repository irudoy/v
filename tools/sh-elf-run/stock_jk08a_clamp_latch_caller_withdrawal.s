! Complete natural39316 state-monitor caller and exact real22590 absolute helper.
    .text
    .balign 4
    .set ORIGIN,0x8690
    .org 0x8692-ORIGIN
P_00008692:
    .byte 0x00
    .org 0x8693-ORIGIN
P_00008693:
    .byte 0xff
    .org 0x8b7e-ORIGIN
P_00008b7e:
    .byte 0x64
    .org 0x22590-ORIGIN
L_00022590:
    cmp/pl r4
    .org 0x22592-ORIGIN
L_00022592:
    bt L_00022596
    .org 0x22594-ORIGIN
L_00022594:
    neg r4,r4
    .org 0x22596-ORIGIN
L_00022596:
    rts
    .org 0x22598-ORIGIN
L_00022598:
    mov r4,r0
    .org 0x39316-ORIGIN
L_00039316:
    sts.l pr,@-r15
    .org 0x39318-ORIGIN
L_00039318:
    stc.l gbr,@-r15
    .org 0x3931a-ORIGIN
L_0003931a:
    mov.l P_0003945c,r0
    .org 0x3931c-ORIGIN
L_0003931c:
    ldc r0,gbr
    .org 0x3931e-ORIGIN
L_0003931e:
    mov.l P_00039470,r6
    .org 0x39320-ORIGIN
L_00039320:
    mov.b @r6,r0
    .org 0x39322-ORIGIN
L_00039322:
    and #0x20,r0
    .org 0x39324-ORIGIN
L_00039324:
    tst r0,r0
    .org 0x39326-ORIGIN
L_00039326:
    bf/s L_00039334
    .org 0x39328-ORIGIN
L_00039328:
    mov r0,r2
    .org 0x3932a-ORIGIN
L_0003932a:
    mov.l P_00039474,r5
    .org 0x3932c-ORIGIN
L_0003932c:
    mov #0x69,r0
    .org 0x3932e-ORIGIN
L_0003932e:
    mov.b @r5,r6
    .org 0x39330-ORIGIN
L_00039330:
    mov.l P_00039478,r5
    .org 0x39332-ORIGIN
L_00039332:
    mov.b r6,@(r0,r5)
    .org 0x39334-ORIGIN
L_00039334:
    mov.l P_0003947c,r5
    .org 0x39336-ORIGIN
L_00039336:
    mov.b @r5,r0
    .org 0x39338-ORIGIN
L_00039338:
    tst #0x80,r0
    .org 0x3933a-ORIGIN
L_0003933a:
    bt L_000393e4
    .org 0x3933c-ORIGIN
L_0003933c:
    tst #0x40,r0
    .org 0x3933e-ORIGIN
L_0003933e:
    bf L_000393e4
    .org 0x39340-ORIGIN
L_00039340:
    mov.l P_00039480,r5
    .org 0x39342-ORIGIN
L_00039342:
    mov.b @r5,r0
    .org 0x39344-ORIGIN
L_00039344:
    tst #0x20,r0
    .org 0x39346-ORIGIN
L_00039346:
    bt L_000393e4
    .org 0x39348-ORIGIN
L_00039348:
    mov.l P_00039484,r5
    .org 0x3934a-ORIGIN
L_0003934a:
    mov.b @r5,r0
    .org 0x3934c-ORIGIN
L_0003934c:
    tst #0x80,r0
    .org 0x3934e-ORIGIN
L_0003934e:
    bf L_000393e4
    .org 0x39350-ORIGIN
L_00039350:
    mov.l P_00039488,r5
    .org 0x39352-ORIGIN
L_00039352:
    mov.b @(0x4,r5),r0
    .org 0x39354-ORIGIN
L_00039354:
    tst #0x40,r0
    .org 0x39356-ORIGIN
L_00039356:
    bf L_000393e4
    .org 0x39358-ORIGIN
L_00039358:
    tst r2,r2
    .org 0x3935a-ORIGIN
L_0003935a:
    bt L_000393a0
    .org 0x3935c-ORIGIN
L_0003935c:
    mov.l P_0003948c,r6
    .org 0x3935e-ORIGIN
L_0003935e:
    mov #0x16,r0
    .org 0x39360-ORIGIN
L_00039360:
    mov.b @(r0,r6),r2
    .org 0x39362-ORIGIN
L_00039362:
    mov.l P_00039490,r6
    .org 0x39364-ORIGIN
L_00039364:
    extu.b r2,r4
    .org 0x39366-ORIGIN
L_00039366:
    mov.b @(0x8,r6),r0
    .org 0x39368-ORIGIN
L_00039368:
    mov.l P_00039494,r6
    .org 0x3936a-ORIGIN
L_0003936a:
    extu.b r0,r2
    .org 0x3936c-ORIGIN
L_0003936c:
    jsr @r6
    .org 0x3936e-ORIGIN
L_0003936e:
    sub r2,r4
    .org 0x39370-ORIGIN
L_00039370:
    mov #0xa,r6
    .org 0x39372-ORIGIN
L_00039372:
    cmp/ge r6,r0
    .org 0x39374-ORIGIN
L_00039374:
    bt L_000393a0
    .org 0x39376-ORIGIN
L_00039376:
    mov.l P_00039498,r6
    .org 0x39378-ORIGIN
L_00039378:
    mov.l P_00039454,r5
    .org 0x3937a-ORIGIN
L_0003937a:
    mov.w @(0x1a,r6),r0
    .org 0x3937c-ORIGIN
L_0003937c:
    mov.l P_00039494,r6
    .org 0x3937e-ORIGIN
L_0003937e:
    extu.w r0,r4
    .org 0x39380-ORIGIN
L_00039380:
    mov #0x51,r0
    .org 0x39382-ORIGIN
L_00039382:
    shll2 r0
    .org 0x39384-ORIGIN
L_00039384:
    mov.w @(r0,r5),r2
    .org 0x39386-ORIGIN
L_00039386:
    shll2 r4
    .org 0x39388-ORIGIN
L_00039388:
    extu.w r2,r2
    .org 0x3938a-ORIGIN
L_0003938a:
    jsr @r6
    .org 0x3938c-ORIGIN
L_0003938c:
    sub r2,r4
    .org 0x3938e-ORIGIN
L_0003938e:
    mov #-0x80,r6
    .org 0x39390-ORIGIN
L_00039390:
    extu.b r6,r6
    .org 0x39392-ORIGIN
L_00039392:
    cmp/ge r6,r0
    .org 0x39394-ORIGIN
L_00039394:
    bt L_000393a0
    .org 0x39396-ORIGIN
L_00039396:
    mov.l P_00039478,r5
    .org 0x39398-ORIGIN
L_00039398:
    mov #0x69,r0
    .org 0x3939a-ORIGIN
L_0003939a:
    mov.b @(r0,r5),r2
    .org 0x3939c-ORIGIN
L_0003939c:
    tst r2,r2
    .org 0x3939e-ORIGIN
L_0003939e:
    bt L_000393b0
    .org 0x393a0-ORIGIN
L_000393a0:
    mov.l P_00039458,r2
    .org 0x393a2-ORIGIN
L_000393a2:
    mov #0x6a,r0
    .org 0x393a4-ORIGIN
L_000393a4:
    mov.w @(r0,r2),r6
    .org 0x393a6-ORIGIN
L_000393a6:
    mov.b @(0x2a,gbr),r0
    .org 0x393a8-ORIGIN
L_000393a8:
    extu.w r6,r6
    .org 0x393aa-ORIGIN
L_000393aa:
    extu.b r0,r2
    .org 0x393ac-ORIGIN
L_000393ac:
    cmp/ge r2,r6
    .org 0x393ae-ORIGIN
L_000393ae:
    bt L_000393e4
    .org 0x393b0-ORIGIN
L_000393b0:
    mov.b @(0x2a,gbr),r0
    .org 0x393b2-ORIGIN
L_000393b2:
    mov.l P_00039454,r5
    .org 0x393b4-ORIGIN
L_000393b4:
    extu.b r0,r6
    .org 0x393b6-ORIGIN
L_000393b6:
    mov.l P_0003949c,r4
    .org 0x393b8-ORIGIN
L_000393b8:
    mov #-0x7e,r0
    .org 0x393ba-ORIGIN
L_000393ba:
    extu.b r0,r0
    .org 0x393bc-ORIGIN
L_000393bc:
    mov.w @(r0,r5),r2
    .org 0x393be-ORIGIN
L_000393be:
    mov.b @r4,r5
    .org 0x393c0-ORIGIN
L_000393c0:
    add r2,r6
    .org 0x393c2-ORIGIN
L_000393c2:
    extu.b r5,r0
    .org 0x393c4-ORIGIN
L_000393c4:
    cmp/ge r0,r6
    .org 0x393c6-ORIGIN
L_000393c6:
    bf L_000393d2
    .org 0x393c8-ORIGIN
L_000393c8:
    mov.b @(0x1,r4),r0
    .org 0x393ca-ORIGIN
L_000393ca:
    extu.b r0,r0
    .org 0x393cc-ORIGIN
L_000393cc:
    cmp/ge r0,r6
    .org 0x393ce-ORIGIN
L_000393ce:
    bt L_000393d2
    .org 0x393d0-ORIGIN
L_000393d0:
    mov r6,r0
    .org 0x393d2-ORIGIN
L_000393d2:
    mov.l P_000394a0,r6
    .org 0x393d4-ORIGIN
L_000393d4:
    mov.b r0,@(0x2a,gbr)
    .org 0x393d6-ORIGIN
L_000393d6:
    mov #0x13,r0
    .org 0x393d8-ORIGIN
L_000393d8:
    mov.b @(r0,r6),r0
    .org 0x393da-ORIGIN
L_000393da:
    mov.l P_000394a0,r5
    .org 0x393dc-ORIGIN
L_000393dc:
    or #0x4,r0
    .org 0x393de-ORIGIN
L_000393de:
    mov r0,r2
    .org 0x393e0-ORIGIN
L_000393e0:
    mov #0x13,r0
    .org 0x393e2-ORIGIN
L_000393e2:
    mov.b r2,@(r0,r5)
    .org 0x393e4-ORIGIN
L_000393e4:
    mov.l P_000394a4,r6
    .org 0x393e6-ORIGIN
L_000393e6:
    mov #0x51,r0
    .org 0x393e8-ORIGIN
L_000393e8:
    mov.l P_00039454,r5
    .org 0x393ea-ORIGIN
L_000393ea:
    shll2 r0
    .org 0x393ec-ORIGIN
L_000393ec:
    mov.w @r6,r2
    .org 0x393ee-ORIGIN
L_000393ee:
    mov.w r2,@(r0,r5)
    .org 0x393f0-ORIGIN
L_000393f0:
    ldc.l @r15+,gbr
    .org 0x393f2-ORIGIN
L_000393f2:
    lds.l @r15+,pr
    .org 0x393f4-ORIGIN
L_000393f4:
    rts
    .org 0x393f6-ORIGIN
L_000393f6:
    nop
    .org 0x39454-ORIGIN
P_00039454:
    .byte 0xff
    .org 0x39455-ORIGIN
P_00039455:
    .byte 0xff
    .org 0x39456-ORIGIN
P_00039456:
    .byte 0x1e
    .org 0x39457-ORIGIN
P_00039457:
    .byte 0x60
    .org 0x39458-ORIGIN
P_00039458:
    .byte 0xff
    .org 0x39459-ORIGIN
P_00039459:
    .byte 0xff
    .org 0x3945a-ORIGIN
P_0003945a:
    .byte 0x11
    .org 0x3945b-ORIGIN
P_0003945b:
    .byte 0x14
    .org 0x3945c-ORIGIN
P_0003945c:
    .byte 0xff
    .org 0x3945d-ORIGIN
P_0003945d:
    .byte 0xff
    .org 0x3945e-ORIGIN
P_0003945e:
    .byte 0x55
    .org 0x3945f-ORIGIN
P_0003945f:
    .byte 0xbc
    .org 0x39470-ORIGIN
P_00039470:
    .byte 0xff
    .org 0x39471-ORIGIN
P_00039471:
    .byte 0xff
    .org 0x39472-ORIGIN
P_00039472:
    .byte 0x24
    .org 0x39473-ORIGIN
P_00039473:
    .byte 0x59
    .org 0x39474-ORIGIN
P_00039474:
    .byte 0x00
    .org 0x39475-ORIGIN
P_00039475:
    .byte 0x00
    .org 0x39476-ORIGIN
P_00039476:
    .byte 0x8b
    .org 0x39477-ORIGIN
P_00039477:
    .byte 0x7e
    .org 0x39478-ORIGIN
P_00039478:
    .byte 0xff
    .org 0x39479-ORIGIN
P_00039479:
    .byte 0xff
    .org 0x3947a-ORIGIN
P_0003947a:
    .byte 0x25
    .org 0x3947b-ORIGIN
P_0003947b:
    .byte 0x6a
    .org 0x3947c-ORIGIN
P_0003947c:
    .byte 0xff
    .org 0x3947d-ORIGIN
P_0003947d:
    .byte 0xff
    .org 0x3947e-ORIGIN
P_0003947e:
    .byte 0x41
    .org 0x3947f-ORIGIN
P_0003947f:
    .byte 0x85
    .org 0x39480-ORIGIN
P_00039480:
    .byte 0xff
    .org 0x39481-ORIGIN
P_00039481:
    .byte 0xff
    .org 0x39482-ORIGIN
P_00039482:
    .byte 0x24
    .org 0x39483-ORIGIN
P_00039483:
    .byte 0x51
    .org 0x39484-ORIGIN
P_00039484:
    .byte 0xff
    .org 0x39485-ORIGIN
P_00039485:
    .byte 0xff
    .org 0x39486-ORIGIN
P_00039486:
    .byte 0x24
    .org 0x39487-ORIGIN
P_00039487:
    .byte 0x49
    .org 0x39488-ORIGIN
P_00039488:
    .byte 0xff
    .org 0x39489-ORIGIN
P_00039489:
    .byte 0xff
    .org 0x3948a-ORIGIN
P_0003948a:
    .byte 0x42
    .org 0x3948b-ORIGIN
P_0003948b:
    .byte 0x4c
    .org 0x3948c-ORIGIN
P_0003948c:
    .byte 0xff
    .org 0x3948d-ORIGIN
P_0003948d:
    .byte 0xff
    .org 0x3948e-ORIGIN
P_0003948e:
    .byte 0x11
    .org 0x3948f-ORIGIN
P_0003948f:
    .byte 0xd4
    .org 0x39490-ORIGIN
P_00039490:
    .byte 0xff
    .org 0x39491-ORIGIN
P_00039491:
    .byte 0xff
    .org 0x39492-ORIGIN
P_00039492:
    .byte 0x22
    .org 0x39493-ORIGIN
P_00039493:
    .byte 0xdc
    .org 0x39494-ORIGIN
P_00039494:
    .byte 0x00
    .org 0x39495-ORIGIN
P_00039495:
    .byte 0x02
    .org 0x39496-ORIGIN
P_00039496:
    .byte 0x25
    .org 0x39497-ORIGIN
P_00039497:
    .byte 0x90
    .org 0x39498-ORIGIN
P_00039498:
    .byte 0xff
    .org 0x39499-ORIGIN
P_00039499:
    .byte 0xff
    .org 0x3949a-ORIGIN
P_0003949a:
    .byte 0x10
    .org 0x3949b-ORIGIN
P_0003949b:
    .byte 0x48
    .org 0x3949c-ORIGIN
P_0003949c:
    .byte 0x00
    .org 0x3949d-ORIGIN
P_0003949d:
    .byte 0x00
    .org 0x3949e-ORIGIN
P_0003949e:
    .byte 0x86
    .org 0x3949f-ORIGIN
P_0003949f:
    .byte 0x92
    .org 0x394a0-ORIGIN
P_000394a0:
    .byte 0xff
    .org 0x394a1-ORIGIN
P_000394a1:
    .byte 0xff
    .org 0x394a2-ORIGIN
P_000394a2:
    .byte 0x42
    .org 0x394a3-ORIGIN
P_000394a3:
    .byte 0x1c
    .org 0x394a4-ORIGIN
P_000394a4:
    .byte 0xff
    .org 0x394a5-ORIGIN
P_000394a5:
    .byte 0xff
    .org 0x394a6-ORIGIN
P_000394a6:
    .byte 0x10
    .org 0x394a7-ORIGIN
P_000394a7:
    .byte 0x26
