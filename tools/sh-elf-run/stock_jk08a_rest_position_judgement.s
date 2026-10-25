! Complete stock native-index1 rest-position judgement with natural GBR return.
    .text
    .balign 4
    .set ORIGIN,0x90254
    .org 0x90256-ORIGIN
L_00090256:
    stc.l gbr,@-r15
    .org 0x90258-ORIGIN
L_00090258:
    mov.l P_000903f8,r0
    .org 0x9025a-ORIGIN
L_0009025a:
    ldc r0,gbr
    .org 0x9025c-ORIGIN
L_0009025c:
    add #-0x4,r15
    .org 0x9025e-ORIGIN
L_0009025e:
    tst r5,r5
    .org 0x90260-ORIGIN
L_00090260:
    bf/s L_00090268
    .org 0x90262-ORIGIN
L_00090262:
    mov r4,r7
    .org 0x90264-ORIGIN
L_00090264:
    bra L_00090460
    .org 0x90266-ORIGIN
L_00090266:
    nop
    .org 0x90268-ORIGIN
L_00090268:
    mov.l P_00090408,r6
    .org 0x9026a-ORIGIN
L_0009026a:
    mov #-0x80,r5
    .org 0x9026c-ORIGIN
L_0009026c:
    extu.b r5,r5
    .org 0x9026e-ORIGIN
L_0009026e:
    mov.b @(0x3,r6),r0
    .org 0x90270-ORIGIN
L_00090270:
    extu.b r0,r2
    .org 0x90272-ORIGIN
L_00090272:
    cmp/eq r5,r2
    .org 0x90274-ORIGIN
L_00090274:
    bt L_0009027a
    .org 0x90276-ORIGIN
L_00090276:
    bra L_00090460
    .org 0x90278-ORIGIN
L_00090278:
    nop
    .org 0x9027a-ORIGIN
L_0009027a:
    mov.b @(0xf0,gbr),r0
    .org 0x9027c-ORIGIN
L_0009027c:
    tst r0,r0
    .org 0x9027e-ORIGIN
L_0009027e:
    bf L_0009028e
    .org 0x90280-ORIGIN
L_00090280:
    mov.l P_0009040c,r6
    .org 0x90282-ORIGIN
L_00090282:
    mov #0x3b,r0
    .org 0x90284-ORIGIN
L_00090284:
    mov.b @(r0,r6),r0
    .org 0x90286-ORIGIN
L_00090286:
    tst #0x40,r0
    .org 0x90288-ORIGIN
L_00090288:
    bt L_0009028e
    .org 0x9028a-ORIGIN
L_0009028a:
    tst #0x10,r0
    .org 0x9028c-ORIGIN
L_0009028c:
    bf L_000902aa
    .org 0x9028e-ORIGIN
L_0009028e:
    mov.l P_00090410,r4
    .org 0x90290-ORIGIN
L_00090290:
    mov r7,r0
    .org 0x90292-ORIGIN
L_00090292:
    stc gbr,r2
    .org 0x90294-ORIGIN
L_00090294:
    mov.b @r4,r6
    .org 0x90296-ORIGIN
L_00090296:
    add #0x23,r2
    .org 0x90298-ORIGIN
L_00090298:
    mov.l P_00090404,r1
    .org 0x9029a-ORIGIN
L_0009029a:
    mov.b r6,@(r0,r2)
    .org 0x9029c-ORIGIN
L_0009029c:
    mov r7,r2
    .org 0x9029e-ORIGIN
L_0009029e:
    mov.w P_0009035e,r0
    .org 0x902a0-ORIGIN
L_000902a0:
    add #0x1,r2
    .org 0x902a2-ORIGIN
L_000902a2:
    not r2,r2
    .org 0x902a4-ORIGIN
L_000902a4:
    mov.b @(r0,r1),r6
    .org 0x902a6-ORIGIN
L_000902a6:
    and r2,r6
    .org 0x902a8-ORIGIN
L_000902a8:
    mov.b r6,@(r0,r1)
    .org 0x902aa-ORIGIN
L_000902aa:
    mov.b @(0xef,gbr),r0
    .org 0x902ac-ORIGIN
L_000902ac:
    tst r0,r0
    .org 0x902ae-ORIGIN
L_000902ae:
    bf L_000902ca
    .org 0x902b0-ORIGIN
L_000902b0:
    mov.l P_0009040c,r6
    .org 0x902b2-ORIGIN
L_000902b2:
    mov #0x3a,r0
    .org 0x902b4-ORIGIN
L_000902b4:
    mov.b @(r0,r6),r0
    .org 0x902b6-ORIGIN
L_000902b6:
    tst #0x10,r0
    .org 0x902b8-ORIGIN
L_000902b8:
    bt L_000902ca
    .org 0x902ba-ORIGIN
L_000902ba:
    tst #0x8,r0
    .org 0x902bc-ORIGIN
L_000902bc:
    bt L_000902ca
    .org 0x902be-ORIGIN
L_000902be:
    tst #0x40,r0
    .org 0x902c0-ORIGIN
L_000902c0:
    bt L_000902ca
    .org 0x902c2-ORIGIN
L_000902c2:
    mov.l P_00090414,r6
    .org 0x902c4-ORIGIN
L_000902c4:
    mov.b @r6,r0
    .org 0x902c6-ORIGIN
L_000902c6:
    tst #0x20,r0
    .org 0x902c8-ORIGIN
L_000902c8:
    bf L_000902e6
    .org 0x902ca-ORIGIN
L_000902ca:
    mov.l P_00090418,r4
    .org 0x902cc-ORIGIN
L_000902cc:
    mov r7,r0
    .org 0x902ce-ORIGIN
L_000902ce:
    stc gbr,r2
    .org 0x902d0-ORIGIN
L_000902d0:
    mov.b @r4,r6
    .org 0x902d2-ORIGIN
L_000902d2:
    add #0x37,r2
    .org 0x902d4-ORIGIN
L_000902d4:
    mov.l P_00090404,r1
    .org 0x902d6-ORIGIN
L_000902d6:
    mov.b r6,@(r0,r2)
    .org 0x902d8-ORIGIN
L_000902d8:
    mov r7,r2
    .org 0x902da-ORIGIN
L_000902da:
    mov.w P_0009035e,r0
    .org 0x902dc-ORIGIN
L_000902dc:
    add #0x1,r2
    .org 0x902de-ORIGIN
L_000902de:
    not r2,r2
    .org 0x902e0-ORIGIN
L_000902e0:
    mov.b @(r0,r1),r6
    .org 0x902e2-ORIGIN
L_000902e2:
    and r2,r6
    .org 0x902e4-ORIGIN
L_000902e4:
    mov.b r6,@(r0,r1)
    .org 0x902e6-ORIGIN
L_000902e6:
    stc gbr,r2
    .org 0x902e8-ORIGIN
L_000902e8:
    add #0x23,r2
    .org 0x902ea-ORIGIN
L_000902ea:
    mov r7,r0
    .org 0x902ec-ORIGIN
L_000902ec:
    mov.b @(r0,r2),r6
    .org 0x902ee-ORIGIN
L_000902ee:
    tst r6,r6
    .org 0x902f0-ORIGIN
L_000902f0:
    bf L_00090366
    .org 0x902f2-ORIGIN
L_000902f2:
    mov.l P_00090404,r1
    .org 0x902f4-ORIGIN
L_000902f4:
    mov r7,r2
    .org 0x902f6-ORIGIN
L_000902f6:
    mov.w P_0009035e,r0
    .org 0x902f8-ORIGIN
L_000902f8:
    add #0x1,r2
    .org 0x902fa-ORIGIN
L_000902fa:
    mov.b r2,@r15
    .org 0x902fc-ORIGIN
L_000902fc:
    mov.b @(r0,r1),r6
    .org 0x902fe-ORIGIN
L_000902fe:
    mov.l P_0009041c,r3
    .org 0x90300-ORIGIN
L_00090300:
    or r2,r6
    .org 0x90302-ORIGIN
L_00090302:
    mov.l P_00090420,r2
    .org 0x90304-ORIGIN
L_00090304:
    mov.b r6,@(r0,r1)
    .org 0x90306-ORIGIN
L_00090306:
    mov r7,r0
    .org 0x90308-ORIGIN
L_00090308:
    mov.w P_00090360,r6
    .org 0x9030a-ORIGIN
L_0009030a:
    add r6,r2
    .org 0x9030c-ORIGIN
L_0009030c:
    mov.b @(r0,r2),r6
    .org 0x9030e-ORIGIN
L_0009030e:
    mov.b @r3,r2
    .org 0x90310-ORIGIN
L_00090310:
    extu.b r6,r4
    .org 0x90312-ORIGIN
L_00090312:
    extu.b r2,r2
    .org 0x90314-ORIGIN
L_00090314:
    add r5,r2
    .org 0x90316-ORIGIN
L_00090316:
    cmp/gt r2,r4
    .org 0x90318-ORIGIN
L_00090318:
    bt L_00090328
    .org 0x9031a-ORIGIN
L_0009031a:
    mov.l P_00090424,r2
    .org 0x9031c-ORIGIN
L_0009031c:
    mov.b @r2,r6
    .org 0x9031e-ORIGIN
L_0009031e:
    mov r5,r2
    .org 0x90320-ORIGIN
L_00090320:
    extu.b r6,r6
    .org 0x90322-ORIGIN
L_00090322:
    sub r6,r2
    .org 0x90324-ORIGIN
L_00090324:
    cmp/ge r2,r4
    .org 0x90326-ORIGIN
L_00090326:
    bt L_00090366
    .org 0x90328-ORIGIN
L_00090328:
    mov #-0x13,r6
    .org 0x9032a-ORIGIN
L_0009032a:
    mov r7,r0
    .org 0x9032c-ORIGIN
L_0009032c:
    stc gbr,r2
    .org 0x9032e-ORIGIN
L_0009032e:
    extu.b r6,r6
    .org 0x90330-ORIGIN
L_00090330:
    add r6,r2
    .org 0x90332-ORIGIN
L_00090332:
    mov.b @(r0,r2),r6
    .org 0x90334-ORIGIN
L_00090334:
    tst r6,r6
    .org 0x90336-ORIGIN
L_00090336:
    bf L_00090342
    .org 0x90338-ORIGIN
L_00090338:
    mov.w P_00090362,r0
    .org 0x9033a-ORIGIN
L_0009033a:
    mov.b @r15,r6
    .org 0x9033c-ORIGIN
L_0009033c:
    mov.b @(r0,r1),r2
    .org 0x9033e-ORIGIN
L_0009033e:
    or r6,r2
    .org 0x90340-ORIGIN
L_00090340:
    mov.b r2,@(r0,r1)
    .org 0x90342-ORIGIN
L_00090342:
    mov #-0x1d,r6
    .org 0x90344-ORIGIN
L_00090344:
    mov r7,r0
    .org 0x90346-ORIGIN
L_00090346:
    stc gbr,r2
    .org 0x90348-ORIGIN
L_00090348:
    extu.b r6,r6
    .org 0x9034a-ORIGIN
L_0009034a:
    add r6,r2
    .org 0x9034c-ORIGIN
L_0009034c:
    mov.b @(r0,r2),r6
    .org 0x9034e-ORIGIN
L_0009034e:
    tst r6,r6
    .org 0x90350-ORIGIN
L_00090350:
    bf L_00090384
    .org 0x90352-ORIGIN
L_00090352:
    mov.w P_00090364,r0
    .org 0x90354-ORIGIN
L_00090354:
    mov.b @r15,r6
    .org 0x90356-ORIGIN
L_00090356:
    mov.b @(r0,r1),r2
    .org 0x90358-ORIGIN
L_00090358:
    or r6,r2
    .org 0x9035a-ORIGIN
L_0009035a:
    bra L_00090384
    .org 0x9035c-ORIGIN
L_0009035c:
    mov.b r2,@(r0,r1)
    .org 0x9035e-ORIGIN
P_0009035e:
    .byte 0x0c
    .org 0x9035f-ORIGIN
P_0009035f:
    .byte 0xa1
    .org 0x90360-ORIGIN
P_00090360:
    .byte 0x04
    .org 0x90361-ORIGIN
P_00090361:
    .byte 0x2e
    .org 0x90362-ORIGIN
P_00090362:
    .byte 0x0c
    .org 0x90363-ORIGIN
P_00090363:
    .byte 0x93
    .org 0x90364-ORIGIN
P_00090364:
    .byte 0x0c
    .org 0x90365-ORIGIN
P_00090365:
    .byte 0x8a
    .org 0x90366-ORIGIN
L_00090366:
    mov #-0x13,r6
    .org 0x90368-ORIGIN
L_00090368:
    mov.l P_00090428,r1
    .org 0x9036a-ORIGIN
L_0009036a:
    extu.b r6,r2
    .org 0x9036c-ORIGIN
L_0009036c:
    stc gbr,r6
    .org 0x9036e-ORIGIN
L_0009036e:
    mov.b @(0x9,r1),r0
    .org 0x90370-ORIGIN
L_00090370:
    add r2,r6
    .org 0x90372-ORIGIN
L_00090372:
    add #-0xa,r2
    .org 0x90374-ORIGIN
L_00090374:
    mov r0,r4
    .org 0x90376-ORIGIN
L_00090376:
    mov r7,r0
    .org 0x90378-ORIGIN
L_00090378:
    mov.b r4,@(r0,r6)
    .org 0x9037a-ORIGIN
L_0009037a:
    mov r7,r0
    .org 0x9037c-ORIGIN
L_0009037c:
    stc gbr,r6
    .org 0x9037e-ORIGIN
L_0009037e:
    add r2,r6
    .org 0x90380-ORIGIN
L_00090380:
    mov.b @r1,r2
    .org 0x90382-ORIGIN
L_00090382:
    mov.b r2,@(r0,r6)
    .org 0x90384-ORIGIN
L_00090384:
    stc gbr,r2
    .org 0x90386-ORIGIN
L_00090386:
    add #0x37,r2
    .org 0x90388-ORIGIN
L_00090388:
    mov r7,r0
    .org 0x9038a-ORIGIN
L_0009038a:
    mov.b @(r0,r2),r6
    .org 0x9038c-ORIGIN
L_0009038c:
    tst r6,r6
    .org 0x9038e-ORIGIN
L_0009038e:
    bf L_00090440
    .org 0x90390-ORIGIN
L_00090390:
    mov.l P_00090404,r1
    .org 0x90392-ORIGIN
L_00090392:
    mov r7,r2
    .org 0x90394-ORIGIN
L_00090394:
    mov.w P_000903f2,r0
    .org 0x90396-ORIGIN
L_00090396:
    add #0x1,r2
    .org 0x90398-ORIGIN
L_00090398:
    mov.b r2,@r15
    .org 0x9039a-ORIGIN
L_0009039a:
    mov.b @(r0,r1),r6
    .org 0x9039c-ORIGIN
L_0009039c:
    mov.l P_0009042c,r3
    .org 0x9039e-ORIGIN
L_0009039e:
    or r2,r6
    .org 0x903a0-ORIGIN
L_000903a0:
    mov.l P_00090420,r2
    .org 0x903a2-ORIGIN
L_000903a2:
    mov.b r6,@(r0,r1)
    .org 0x903a4-ORIGIN
L_000903a4:
    mov r7,r0
    .org 0x903a6-ORIGIN
L_000903a6:
    mov.w P_000903f4,r6
    .org 0x903a8-ORIGIN
L_000903a8:
    add r6,r2
    .org 0x903aa-ORIGIN
L_000903aa:
    mov.b @(r0,r2),r6
    .org 0x903ac-ORIGIN
L_000903ac:
    mov.b @r3,r2
    .org 0x903ae-ORIGIN
L_000903ae:
    extu.b r6,r4
    .org 0x903b0-ORIGIN
L_000903b0:
    extu.b r2,r2
    .org 0x903b2-ORIGIN
L_000903b2:
    add r5,r2
    .org 0x903b4-ORIGIN
L_000903b4:
    cmp/gt r2,r4
    .org 0x903b6-ORIGIN
L_000903b6:
    bt L_000903c4
    .org 0x903b8-ORIGIN
L_000903b8:
    mov.l P_00090430,r6
    .org 0x903ba-ORIGIN
L_000903ba:
    mov.b @r6,r2
    .org 0x903bc-ORIGIN
L_000903bc:
    extu.b r2,r2
    .org 0x903be-ORIGIN
L_000903be:
    sub r2,r5
    .org 0x903c0-ORIGIN
L_000903c0:
    cmp/ge r5,r4
    .org 0x903c2-ORIGIN
L_000903c2:
    bt L_00090440
    .org 0x903c4-ORIGIN
L_000903c4:
    mov #-0x1f,r2
    .org 0x903c6-ORIGIN
L_000903c6:
    mov r7,r0
    .org 0x903c8-ORIGIN
L_000903c8:
    stc gbr,r6
    .org 0x903ca-ORIGIN
L_000903ca:
    extu.b r2,r2
    .org 0x903cc-ORIGIN
L_000903cc:
    add r2,r6
    .org 0x903ce-ORIGIN
L_000903ce:
    mov.b @(r0,r6),r2
    .org 0x903d0-ORIGIN
L_000903d0:
    tst r2,r2
    .org 0x903d2-ORIGIN
L_000903d2:
    bf L_000903de
    .org 0x903d4-ORIGIN
L_000903d4:
    mov.w P_000903f6,r0
    .org 0x903d6-ORIGIN
L_000903d6:
    mov.b @r15,r6
    .org 0x903d8-ORIGIN
L_000903d8:
    mov.b @(r0,r1),r2
    .org 0x903da-ORIGIN
L_000903da:
    or r6,r2
    .org 0x903dc-ORIGIN
L_000903dc:
    mov.b r2,@(r0,r1)
    .org 0x903de-ORIGIN
L_000903de:
    mov #-0x25,r6
    .org 0x903e0-ORIGIN
L_000903e0:
    mov r7,r0
    .org 0x903e2-ORIGIN
L_000903e2:
    stc gbr,r2
    .org 0x903e4-ORIGIN
L_000903e4:
    extu.b r6,r6
    .org 0x903e6-ORIGIN
L_000903e6:
    add r6,r2
    .org 0x903e8-ORIGIN
L_000903e8:
    mov.b @(r0,r2),r6
    .org 0x903ea-ORIGIN
L_000903ea:
    tst r6,r6
    .org 0x903ec-ORIGIN
L_000903ec:
    bf L_000904bc
    .org 0x903ee-ORIGIN
L_000903ee:
    bra L_00090434
    .org 0x903f0-ORIGIN
L_000903f0:
    nop
    .org 0x903f2-ORIGIN
P_000903f2:
    .byte 0x0c
    .org 0x903f3-ORIGIN
P_000903f3:
    .byte 0xa1
    .org 0x903f4-ORIGIN
P_000903f4:
    .byte 0x04
    .org 0x903f5-ORIGIN
P_000903f5:
    .byte 0x2e
    .org 0x903f6-ORIGIN
P_000903f6:
    .byte 0x0c
    .org 0x903f7-ORIGIN
P_000903f7:
    .byte 0x93
    .org 0x903f8-ORIGIN
P_000903f8:
    .byte 0xff
    .org 0x903f9-ORIGIN
P_000903f9:
    .byte 0xff
    .org 0x903fa-ORIGIN
P_000903fa:
    .byte 0x42
    .org 0x903fb-ORIGIN
P_000903fb:
    .byte 0xd3
    .org 0x90404-ORIGIN
P_00090404:
    .byte 0xff
    .org 0x90405-ORIGIN
P_00090405:
    .byte 0xff
    .org 0x90406-ORIGIN
P_00090406:
    .byte 0x28
    .org 0x90407-ORIGIN
P_00090407:
    .byte 0xf8
    .org 0x90408-ORIGIN
P_00090408:
    .byte 0xff
    .org 0x90409-ORIGIN
P_00090409:
    .byte 0xff
    .org 0x9040a-ORIGIN
P_0009040a:
    .byte 0x23
    .org 0x9040b-ORIGIN
P_0009040b:
    .byte 0x24
    .org 0x9040c-ORIGIN
P_0009040c:
    .byte 0xff
    .org 0x9040d-ORIGIN
P_0009040d:
    .byte 0xff
    .org 0x9040e-ORIGIN
P_0009040e:
    .byte 0x24
    .org 0x9040f-ORIGIN
P_0009040f:
    .byte 0x70
    .org 0x90410-ORIGIN
P_00090410:
    .byte 0x00
    .org 0x90411-ORIGIN
P_00090411:
    .byte 0x00
    .org 0x90412-ORIGIN
P_00090412:
    .byte 0x85
    .org 0x90413-ORIGIN
P_00090413:
    .byte 0x5d
    .org 0x90414-ORIGIN
P_00090414:
    .byte 0xff
    .org 0x90415-ORIGIN
P_00090415:
    .byte 0xff
    .org 0x90416-ORIGIN
P_00090416:
    .byte 0x24
    .org 0x90417-ORIGIN
P_00090417:
    .byte 0x58
    .org 0x90418-ORIGIN
P_00090418:
    .byte 0x00
    .org 0x90419-ORIGIN
P_00090419:
    .byte 0x00
    .org 0x9041a-ORIGIN
P_0009041a:
    .byte 0x87
    .org 0x9041b-ORIGIN
P_0009041b:
    .byte 0x1f
    .org 0x9041c-ORIGIN
P_0009041c:
    .byte 0x00
    .org 0x9041d-ORIGIN
P_0009041d:
    .byte 0x00
    .org 0x9041e-ORIGIN
P_0009041e:
    .byte 0x89
    .org 0x9041f-ORIGIN
P_0009041f:
    .byte 0x51
    .org 0x90420-ORIGIN
P_00090420:
    .byte 0xff
    .org 0x90421-ORIGIN
P_00090421:
    .byte 0xff
    .org 0x90422-ORIGIN
P_00090422:
    .byte 0x12
    .org 0x90423-ORIGIN
P_00090423:
    .byte 0x8c
    .org 0x90424-ORIGIN
P_00090424:
    .byte 0x00
    .org 0x90425-ORIGIN
P_00090425:
    .byte 0x00
    .org 0x90426-ORIGIN
P_00090426:
    .byte 0x89
    .org 0x90427-ORIGIN
P_00090427:
    .byte 0x52
    .org 0x90428-ORIGIN
P_00090428:
    .byte 0x00
    .org 0x90429-ORIGIN
P_00090429:
    .byte 0x00
    .org 0x9042a-ORIGIN
P_0009042a:
    .byte 0x8e
    .org 0x9042b-ORIGIN
P_0009042b:
    .byte 0x1c
    .org 0x9042c-ORIGIN
P_0009042c:
    .byte 0x00
    .org 0x9042d-ORIGIN
P_0009042d:
    .byte 0x00
    .org 0x9042e-ORIGIN
P_0009042e:
    .byte 0x87
    .org 0x9042f-ORIGIN
P_0009042f:
    .byte 0x36
    .org 0x90430-ORIGIN
P_00090430:
    .byte 0x00
    .org 0x90431-ORIGIN
P_00090431:
    .byte 0x00
    .org 0x90432-ORIGIN
P_00090432:
    .byte 0x87
    .org 0x90433-ORIGIN
P_00090433:
    .byte 0x37
    .org 0x90434-ORIGIN
L_00090434:
    mov.w P_000905a4,r0
    .org 0x90436-ORIGIN
L_00090436:
    mov.b @r15,r6
    .org 0x90438-ORIGIN
L_00090438:
    mov.b @(r0,r1),r2
    .org 0x9043a-ORIGIN
L_0009043a:
    or r6,r2
    .org 0x9043c-ORIGIN
L_0009043c:
    bra L_000904bc
    .org 0x9043e-ORIGIN
L_0009043e:
    mov.b r2,@(r0,r1)
    .org 0x90440-ORIGIN
L_00090440:
    mov #-0x1f,r6
    .org 0x90442-ORIGIN
L_00090442:
    mov.l P_000906e0,r1
    .org 0x90444-ORIGIN
L_00090444:
    extu.b r6,r2
    .org 0x90446-ORIGIN
L_00090446:
    stc gbr,r6
    .org 0x90448-ORIGIN
L_00090448:
    mov.b @(0x9,r1),r0
    .org 0x9044a-ORIGIN
L_0009044a:
    add r2,r6
    .org 0x9044c-ORIGIN
L_0009044c:
    add #-0x6,r2
    .org 0x9044e-ORIGIN
L_0009044e:
    mov r0,r5
    .org 0x90450-ORIGIN
L_00090450:
    mov r7,r0
    .org 0x90452-ORIGIN
L_00090452:
    mov.b r5,@(r0,r6)
    .org 0x90454-ORIGIN
L_00090454:
    mov r7,r0
    .org 0x90456-ORIGIN
L_00090456:
    stc gbr,r6
    .org 0x90458-ORIGIN
L_00090458:
    add r2,r6
    .org 0x9045a-ORIGIN
L_0009045a:
    mov.b @r1,r2
    .org 0x9045c-ORIGIN
L_0009045c:
    bra L_000904bc
    .org 0x9045e-ORIGIN
L_0009045e:
    mov.b r2,@(r0,r6)
    .org 0x90460-ORIGIN
L_00090460:
    mov.l P_000906e4,r1
    .org 0x90462-ORIGIN
L_00090462:
    mov r7,r2
    .org 0x90464-ORIGIN
L_00090464:
    mov.w P_000905a6,r0
    .org 0x90466-ORIGIN
L_00090466:
    add #0x1,r2
    .org 0x90468-ORIGIN
L_00090468:
    not r2,r2
    .org 0x9046a-ORIGIN
L_0009046a:
    mov.l P_000906e8,r4
    .org 0x9046c-ORIGIN
L_0009046c:
    mov.b @(r0,r1),r6
    .org 0x9046e-ORIGIN
L_0009046e:
    and r2,r6
    .org 0x90470-ORIGIN
L_00090470:
    stc gbr,r2
    .org 0x90472-ORIGIN
L_00090472:
    mov.b r6,@(r0,r1)
    .org 0x90474-ORIGIN
L_00090474:
    add #0x37,r2
    .org 0x90476-ORIGIN
L_00090476:
    mov.b @r4,r6
    .org 0x90478-ORIGIN
L_00090478:
    mov r7,r0
    .org 0x9047a-ORIGIN
L_0009047a:
    mov.l P_000906ec,r4
    .org 0x9047c-ORIGIN
L_0009047c:
    mov.b r6,@(r0,r2)
    .org 0x9047e-ORIGIN
L_0009047e:
    mov r7,r0
    .org 0x90480-ORIGIN
L_00090480:
    stc gbr,r2
    .org 0x90482-ORIGIN
L_00090482:
    mov.b @r4,r6
    .org 0x90484-ORIGIN
L_00090484:
    add #0x23,r2
    .org 0x90486-ORIGIN
L_00090486:
    mov.l P_000906e0,r1
    .org 0x90488-ORIGIN
L_00090488:
    mov.b r6,@(r0,r2)
    .org 0x9048a-ORIGIN
L_0009048a:
    mov #-0x13,r2
    .org 0x9048c-ORIGIN
L_0009048c:
    extu.b r2,r6
    .org 0x9048e-ORIGIN
L_0009048e:
    mov.b @(0x9,r1),r0
    .org 0x90490-ORIGIN
L_00090490:
    stc gbr,r2
    .org 0x90492-ORIGIN
L_00090492:
    add r6,r2
    .org 0x90494-ORIGIN
L_00090494:
    mov r0,r4
    .org 0x90496-ORIGIN
L_00090496:
    mov r7,r0
    .org 0x90498-ORIGIN
L_00090498:
    mov.b r4,@(r0,r2)
    .org 0x9049a-ORIGIN
L_0009049a:
    stc gbr,r2
    .org 0x9049c-ORIGIN
L_0009049c:
    add #-0xa,r6
    .org 0x9049e-ORIGIN
L_0009049e:
    mov.b @r1,r5
    .org 0x904a0-ORIGIN
L_000904a0:
    add r6,r2
    .org 0x904a2-ORIGIN
L_000904a2:
    mov r7,r0
    .org 0x904a4-ORIGIN
L_000904a4:
    mov.b r5,@(r0,r2)
    .org 0x904a6-ORIGIN
L_000904a6:
    mov r6,r2
    .org 0x904a8-ORIGIN
L_000904a8:
    stc gbr,r6
    .org 0x904aa-ORIGIN
L_000904aa:
    add #-0x2,r2
    .org 0x904ac-ORIGIN
L_000904ac:
    mov r7,r0
    .org 0x904ae-ORIGIN
L_000904ae:
    add r2,r6
    .org 0x904b0-ORIGIN
L_000904b0:
    mov.b r4,@(r0,r6)
    .org 0x904b2-ORIGIN
L_000904b2:
    add #-0x6,r2
    .org 0x904b4-ORIGIN
L_000904b4:
    stc gbr,r6
    .org 0x904b6-ORIGIN
L_000904b6:
    add r2,r6
    .org 0x904b8-ORIGIN
L_000904b8:
    mov r7,r0
    .org 0x904ba-ORIGIN
L_000904ba:
    mov.b r5,@(r0,r6)
    .org 0x904bc-ORIGIN
L_000904bc:
    add #0x4,r15
    .org 0x904be-ORIGIN
L_000904be:
    rts
    .org 0x904c0-ORIGIN
L_000904c0:
    ldc.l @r15+,gbr
    .org 0x905a4-ORIGIN
P_000905a4:
    .byte 0x0c
    .org 0x905a5-ORIGIN
P_000905a5:
    .byte 0x8a
    .org 0x905a6-ORIGIN
P_000905a6:
    .byte 0x0c
    .org 0x905a7-ORIGIN
P_000905a7:
    .byte 0xa1
    .org 0x906e0-ORIGIN
P_000906e0:
    .byte 0x00
    .org 0x906e1-ORIGIN
P_000906e1:
    .byte 0x00
    .org 0x906e2-ORIGIN
P_000906e2:
    .byte 0x8e
    .org 0x906e3-ORIGIN
P_000906e3:
    .byte 0x1c
    .org 0x906e4-ORIGIN
P_000906e4:
    .byte 0xff
    .org 0x906e5-ORIGIN
P_000906e5:
    .byte 0xff
    .org 0x906e6-ORIGIN
P_000906e6:
    .byte 0x28
    .org 0x906e7-ORIGIN
P_000906e7:
    .byte 0xf8
    .org 0x906e8-ORIGIN
P_000906e8:
    .byte 0x00
    .org 0x906e9-ORIGIN
P_000906e9:
    .byte 0x00
    .org 0x906ea-ORIGIN
P_000906ea:
    .byte 0x87
    .org 0x906eb-ORIGIN
P_000906eb:
    .byte 0x1f
    .org 0x906ec-ORIGIN
P_000906ec:
    .byte 0x00
    .org 0x906ed-ORIGIN
P_000906ed:
    .byte 0x00
    .org 0x906ee-ORIGIN
P_000906ee:
    .byte 0x85
    .org 0x906ef-ORIGIN
P_000906ef:
    .byte 0x5d
