! Complete natural 7C494 dispatch, real 7C4E0 BSR and full 872D0 tail body with natural PR/MACL/frame restoration.
    .text
    .balign 4
    .set ORIGIN,0x8354
    .org 0x8354-ORIGIN
P_00008354:
    .byte 0x01
    .org 0x8656-ORIGIN
P_00008656:
    .byte 0x01
    .org 0x8bda-ORIGIN
P_00008bda:
    .byte 0x20
    .org 0x186ce-ORIGIN
P_000186ce:
    .byte 0x80
    .org 0x7c494-ORIGIN
L_0007c494:
    sts.l pr,@-r15
    .org 0x7c496-ORIGIN
L_0007c496:
    bsr L_0007c4e0
    .org 0x7c498-ORIGIN
L_0007c498:
    nop
    .org 0x7c49a-ORIGIN
L_0007c49a:
    mov.l P_0007c4a0,r2
    .org 0x7c49c-ORIGIN
L_0007c49c:
    jmp @r2
    .org 0x7c49e-ORIGIN
L_0007c49e:
    lds.l @r15+,pr
    .org 0x7c4a0-ORIGIN
P_0007c4a0:
    .byte 0x00
    .org 0x7c4a1-ORIGIN
P_0007c4a1:
    .byte 0x08
    .org 0x7c4a2-ORIGIN
P_0007c4a2:
    .byte 0x72
    .org 0x7c4a3-ORIGIN
P_0007c4a3:
    .byte 0xd0
    .org 0x7c4e0-ORIGIN
L_0007c4e0:
    mov.l P_0007c52c,r1
    .org 0x7c4e2-ORIGIN
L_0007c4e2:
    mov.l P_0007c530,r4
    .org 0x7c4e4-ORIGIN
L_0007c4e4:
    mov #0x16,r0
    .org 0x7c4e6-ORIGIN
L_0007c4e6:
    mov.l P_0007c534,r2
    .org 0x7c4e8-ORIGIN
L_0007c4e8:
    mov.b @r4,r5
    .org 0x7c4ea-ORIGIN
L_0007c4ea:
    mov.b @(r0,r2),r6
    .org 0x7c4ec-ORIGIN
L_0007c4ec:
    mov r5,r0
    .org 0x7c4ee-ORIGIN
L_0007c4ee:
    tst #0x80,r0
    .org 0x7c4f0-ORIGIN
L_0007c4f0:
    bt/s L_0007c4f6
    .org 0x7c4f2-ORIGIN
L_0007c4f2:
    extu.b r6,r6
    .org 0x7c4f4-ORIGIN
L_0007c4f4:
    add #0x4,r6
    .org 0x7c4f6-ORIGIN
L_0007c4f6:
    mov.l P_0007c538,r7
    .org 0x7c4f8-ORIGIN
L_0007c4f8:
    mov r5,r0
    .org 0x7c4fa-ORIGIN
L_0007c4fa:
    mov.b @r7,r2
    .org 0x7c4fc-ORIGIN
L_0007c4fc:
    extu.b r2,r2
    .org 0x7c4fe-ORIGIN
L_0007c4fe:
    cmp/hs r2,r6
    .org 0x7c500-ORIGIN
L_0007c500:
    bt/s L_0007c506
    .org 0x7c502-ORIGIN
L_0007c502:
    or #0x80,r0
    .org 0x7c504-ORIGIN
L_0007c504:
    and #0x7f,r0
    .org 0x7c506-ORIGIN
L_0007c506:
    mov.b r0,@r4
    .org 0x7c508-ORIGIN
L_0007c508:
    exts.b r0,r0
    .org 0x7c50a-ORIGIN
L_0007c50a:
    tst #0x80,r0
    .org 0x7c50c-ORIGIN
L_0007c50c:
    bt L_0007c520
    .org 0x7c50e-ORIGIN
L_0007c50e:
    mov.b @(0x2,r1),r0
    .org 0x7c510-ORIGIN
L_0007c510:
    mov #-0x1,r5
    .org 0x7c512-ORIGIN
L_0007c512:
    extu.b r5,r5
    .org 0x7c514-ORIGIN
L_0007c514:
    extu.b r0,r6
    .org 0x7c516-ORIGIN
L_0007c516:
    cmp/ge r5,r6
    .org 0x7c518-ORIGIN
L_0007c518:
    bt L_0007c526
    .org 0x7c51a-ORIGIN
L_0007c51a:
    add #0x1,r6
    .org 0x7c51c-ORIGIN
L_0007c51c:
    bra L_0007c522
    .org 0x7c51e-ORIGIN
L_0007c51e:
    mov r6,r0
    .org 0x7c520-ORIGIN
L_0007c520:
    mov #0x0,r0
    .org 0x7c522-ORIGIN
L_0007c522:
    rts
    .org 0x7c524-ORIGIN
L_0007c524:
    mov.b r0,@(0x2,r1)
    .org 0x7c526-ORIGIN
L_0007c526:
    rts
    .org 0x7c528-ORIGIN
L_0007c528:
    nop
    .org 0x7c52c-ORIGIN
P_0007c52c:
    .byte 0xff
    .org 0x7c52d-ORIGIN
P_0007c52d:
    .byte 0xff
    .org 0x7c52e-ORIGIN
P_0007c52e:
    .byte 0x40
    .org 0x7c52f-ORIGIN
P_0007c52f:
    .byte 0x94
    .org 0x7c530-ORIGIN
P_0007c530:
    .byte 0xff
    .org 0x7c531-ORIGIN
P_0007c531:
    .byte 0xff
    .org 0x7c532-ORIGIN
P_0007c532:
    .byte 0x24
    .org 0x7c533-ORIGIN
P_0007c533:
    .byte 0xc4
    .org 0x7c534-ORIGIN
P_0007c534:
    .byte 0xff
    .org 0x7c535-ORIGIN
P_0007c535:
    .byte 0xff
    .org 0x7c536-ORIGIN
P_0007c536:
    .byte 0x11
    .org 0x7c537-ORIGIN
P_0007c537:
    .byte 0x9c
    .org 0x7c538-ORIGIN
P_0007c538:
    .byte 0x00
    .org 0x7c539-ORIGIN
P_0007c539:
    .byte 0x00
    .org 0x7c53a-ORIGIN
P_0007c53a:
    .byte 0x8b
    .org 0x7c53b-ORIGIN
P_0007c53b:
    .byte 0xda
    .org 0x872d0-ORIGIN
L_000872d0:
    sts.l macl,@-r15
    .org 0x872d2-ORIGIN
L_000872d2:
    mov.l P_000873a0,r1
    .org 0x872d4-ORIGIN
L_000872d4:
    add #-0x8,r15
    .org 0x872d6-ORIGIN
L_000872d6:
    mov.l P_000873a4,r6
    .org 0x872d8-ORIGIN
L_000872d8:
    mov.b @(0x6,r6),r0
    .org 0x872da-ORIGIN
L_000872da:
    tst #0x80,r0
    .org 0x872dc-ORIGIN
L_000872dc:
    bt L_00087398
    .org 0x872de-ORIGIN
L_000872de:
    mov.l P_000873a8,r5
    .org 0x872e0-ORIGIN
L_000872e0:
    mov #-0x38,r4
    .org 0x872e2-ORIGIN
L_000872e2:
    extu.b r4,r4
    .org 0x872e4-ORIGIN
L_000872e4:
    mov.w @(0xa,r1),r0
    .org 0x872e6-ORIGIN
L_000872e6:
    mov.b @r5,r2
    .org 0x872e8-ORIGIN
L_000872e8:
    extu.w r0,r6
    .org 0x872ea-ORIGIN
L_000872ea:
    extu.b r2,r2
    .org 0x872ec-ORIGIN
L_000872ec:
    mul.l r2,r4
    .org 0x872ee-ORIGIN
L_000872ee:
    sts macl,r2
    .org 0x872f0-ORIGIN
L_000872f0:
    cmp/ge r2,r6
    .org 0x872f2-ORIGIN
L_000872f2:
    bf L_00087302
    .org 0x872f4-ORIGIN
L_000872f4:
    mov.l P_000873ac,r6
    .org 0x872f6-ORIGIN
L_000872f6:
    mov #0x0,r0
    .org 0x872f8-ORIGIN
L_000872f8:
    mov.w r0,@(0xa,r1)
    .org 0x872fa-ORIGIN
L_000872fa:
    mov.b @(0x1,r6),r0
    .org 0x872fc-ORIGIN
L_000872fc:
    mov.l P_000873ac,r5
    .org 0x872fe-ORIGIN
L_000872fe:
    or #0x20,r0
    .org 0x87300-ORIGIN
L_00087300:
    mov.b r0,@(0x1,r5)
    .org 0x87302-ORIGIN
L_00087302:
    mov.w @(0xc,r1),r0
    .org 0x87304-ORIGIN
L_00087304:
    mov.w P_0008739e,r6
    .org 0x87306-ORIGIN
L_00087306:
    extu.w r0,r2
    .org 0x87308-ORIGIN
L_00087308:
    cmp/ge r6,r2
    .org 0x8730a-ORIGIN
L_0008730a:
    bf L_0008731a
    .org 0x8730c-ORIGIN
L_0008730c:
    mov.l P_000873ac,r6
    .org 0x8730e-ORIGIN
L_0008730e:
    mov #0x0,r0
    .org 0x87310-ORIGIN
L_00087310:
    mov.w r0,@(0xc,r1)
    .org 0x87312-ORIGIN
L_00087312:
    mov.b @(0x1,r6),r0
    .org 0x87314-ORIGIN
L_00087314:
    mov.l P_000873ac,r5
    .org 0x87316-ORIGIN
L_00087316:
    or #0x80,r0
    .org 0x87318-ORIGIN
L_00087318:
    mov.b r0,@(0x1,r5)
    .org 0x8731a-ORIGIN
L_0008731a:
    mov.l P_000873b0,r5
    .org 0x8731c-ORIGIN
L_0008731c:
    mov.w @(0xe,r1),r0
    .org 0x8731e-ORIGIN
L_0008731e:
    mov.b @r5,r2
    .org 0x87320-ORIGIN
L_00087320:
    extu.w r0,r7
    .org 0x87322-ORIGIN
L_00087322:
    extu.b r2,r2
    .org 0x87324-ORIGIN
L_00087324:
    mul.l r2,r4
    .org 0x87326-ORIGIN
L_00087326:
    sts macl,r2
    .org 0x87328-ORIGIN
L_00087328:
    cmp/ge r2,r7
    .org 0x8732a-ORIGIN
L_0008732a:
    bf L_0008733c
    .org 0x8732c-ORIGIN
L_0008732c:
    mov.l P_000873ac,r6
    .org 0x8732e-ORIGIN
L_0008732e:
    mov #0x0,r7
    .org 0x87330-ORIGIN
L_00087330:
    mov r7,r0
    .org 0x87332-ORIGIN
L_00087332:
    mov.w r0,@(0xe,r1)
    .org 0x87334-ORIGIN
L_00087334:
    mov.b @(0x1,r6),r0
    .org 0x87336-ORIGIN
L_00087336:
    mov.l P_000873ac,r5
    .org 0x87338-ORIGIN
L_00087338:
    or #0x40,r0
    .org 0x8733a-ORIGIN
L_0008733a:
    mov.b r0,@(0x1,r5)
    .org 0x8733c-ORIGIN
L_0008733c:
    mov.l P_000873ac,r6
    .org 0x8733e-ORIGIN
L_0008733e:
    mov #0x11,r0
    .org 0x87340-ORIGIN
L_00087340:
    mov.b @(r0,r6),r0
    .org 0x87342-ORIGIN
L_00087342:
    tst #0x80,r0
    .org 0x87344-ORIGIN
L_00087344:
    bt L_00087390
    .org 0x87346-ORIGIN
L_00087346:
    mov.l P_000873b4,r6
    .org 0x87348-ORIGIN
L_00087348:
    mov #0x29,r0
    .org 0x8734a-ORIGIN
L_0008734a:
    mov.b @(r0,r6),r0
    .org 0x8734c-ORIGIN
L_0008734c:
    tst #0x2,r0
    .org 0x8734e-ORIGIN
L_0008734e:
    bt L_00087390
    .org 0x87350-ORIGIN
L_00087350:
    tst #0x1,r0
    .org 0x87352-ORIGIN
L_00087352:
    bt L_00087390
    .org 0x87354-ORIGIN
L_00087354:
    mov.l P_000873b8,r6
    .org 0x87356-ORIGIN
L_00087356:
    mov #0x57,r0
    .org 0x87358-ORIGIN
L_00087358:
    shll2 r0
    .org 0x8735a-ORIGIN
L_0008735a:
    mov.b @(r0,r6),r2
    .org 0x8735c-ORIGIN
L_0008735c:
    mov #0x1f,r6
    .org 0x8735e-ORIGIN
L_0008735e:
    cmp/hs r6,r2
    .org 0x87360-ORIGIN
L_00087360:
    bf L_00087398
    .org 0x87362-ORIGIN
L_00087362:
    mov.l P_000873bc,r6
    .org 0x87364-ORIGIN
L_00087364:
    mov #-0x7a,r0
    .org 0x87366-ORIGIN
L_00087366:
    extu.b r0,r0
    .org 0x87368-ORIGIN
L_00087368:
    mov.b @(r0,r6),r2
    .org 0x8736a-ORIGIN
L_0008736a:
    tst r2,r2
    .org 0x8736c-ORIGIN
L_0008736c:
    bf L_0008737e
    .org 0x8736e-ORIGIN
L_0008736e:
    mov.w @(0xa,r1),r0
    .org 0x87370-ORIGIN
L_00087370:
    mov.l r0,@r15
    .org 0x87372-ORIGIN
L_00087372:
    add #0x1,r0
    .org 0x87374-ORIGIN
L_00087374:
    mov.w r0,@(0xa,r1)
    .org 0x87376-ORIGIN
L_00087376:
    mov.w @(0xc,r1),r0
    .org 0x87378-ORIGIN
L_00087378:
    mov.l r0,@(0x4,r15)
    .org 0x8737a-ORIGIN
L_0008737a:
    add #0x1,r0
    .org 0x8737c-ORIGIN
L_0008737c:
    mov.w r0,@(0xc,r1)
    .org 0x8737e-ORIGIN
L_0008737e:
    mov.l P_000873bc,r6
    .org 0x87380-ORIGIN
L_00087380:
    mov #-0x7b,r0
    .org 0x87382-ORIGIN
L_00087382:
    extu.b r0,r0
    .org 0x87384-ORIGIN
L_00087384:
    mov.b @(r0,r6),r2
    .org 0x87386-ORIGIN
L_00087386:
    tst r2,r2
    .org 0x87388-ORIGIN
L_00087388:
    bf L_00087398
    .org 0x8738a-ORIGIN
L_0008738a:
    add #0x1,r7
    .org 0x8738c-ORIGIN
L_0008738c:
    bra L_00087396
    .org 0x8738e-ORIGIN
L_0008738e:
    mov r7,r0
    .org 0x87390-ORIGIN
L_00087390:
    mov #0x0,r0
    .org 0x87392-ORIGIN
L_00087392:
    mov.w r0,@(0xa,r1)
    .org 0x87394-ORIGIN
L_00087394:
    mov.w r0,@(0xc,r1)
    .org 0x87396-ORIGIN
L_00087396:
    mov.w r0,@(0xe,r1)
    .org 0x87398-ORIGIN
L_00087398:
    add #0x8,r15
    .org 0x8739a-ORIGIN
L_0008739a:
    rts
    .org 0x8739c-ORIGIN
L_0008739c:
    lds.l @r15+,macl
    .org 0x8739e-ORIGIN
P_0008739e:
    .byte 0x03
    .org 0x8739f-ORIGIN
P_0008739f:
    .byte 0xe8
    .org 0x873a0-ORIGIN
P_000873a0:
    .byte 0xff
    .org 0x873a1-ORIGIN
P_000873a1:
    .byte 0xff
    .org 0x873a2-ORIGIN
P_000873a2:
    .byte 0x40
    .org 0x873a3-ORIGIN
P_000873a3:
    .byte 0x94
    .org 0x873a4-ORIGIN
P_000873a4:
    .byte 0x00
    .org 0x873a5-ORIGIN
P_000873a5:
    .byte 0x01
    .org 0x873a6-ORIGIN
P_000873a6:
    .byte 0x86
    .org 0x873a7-ORIGIN
P_000873a7:
    .byte 0xc8
    .org 0x873a8-ORIGIN
P_000873a8:
    .byte 0x00
    .org 0x873a9-ORIGIN
P_000873a9:
    .byte 0x00
    .org 0x873aa-ORIGIN
P_000873aa:
    .byte 0x83
    .org 0x873ab-ORIGIN
P_000873ab:
    .byte 0x54
    .org 0x873ac-ORIGIN
P_000873ac:
    .byte 0xff
    .org 0x873ad-ORIGIN
P_000873ad:
    .byte 0xff
    .org 0x873ae-ORIGIN
P_000873ae:
    .byte 0x42
    .org 0x873af-ORIGIN
P_000873af:
    .byte 0x40
    .org 0x873b0-ORIGIN
P_000873b0:
    .byte 0x00
    .org 0x873b1-ORIGIN
P_000873b1:
    .byte 0x00
    .org 0x873b2-ORIGIN
P_000873b2:
    .byte 0x86
    .org 0x873b3-ORIGIN
P_000873b3:
    .byte 0x56
    .org 0x873b4-ORIGIN
P_000873b4:
    .byte 0xff
    .org 0x873b5-ORIGIN
P_000873b5:
    .byte 0xff
    .org 0x873b6-ORIGIN
P_000873b6:
    .byte 0x41
    .org 0x873b7-ORIGIN
P_000873b7:
    .byte 0xa9
    .org 0x873b8-ORIGIN
P_000873b8:
    .byte 0xff
    .org 0x873b9-ORIGIN
P_000873b9:
    .byte 0xff
    .org 0x873ba-ORIGIN
P_000873ba:
    .byte 0x36
    .org 0x873bb-ORIGIN
P_000873bb:
    .byte 0xd8
    .org 0x873bc-ORIGIN
P_000873bc:
    .byte 0xff
    .org 0x873bd-ORIGIN
P_000873bd:
    .byte 0xff
    .org 0x873be-ORIGIN
P_000873be:
    .byte 0x43
    .org 0x873bf-ORIGIN
P_000873bf:
    .byte 0xc7
