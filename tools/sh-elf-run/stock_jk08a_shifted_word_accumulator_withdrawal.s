! Complete natural gated shifted-word accumulator; no stock-function stubs.
    .text
    .balign 4
    .set ORIGIN,0xa5398
    .org 0xa5398-ORIGIN
L_000a5398:
    sts.l macl,@-r15
    .org 0xa539a-ORIGIN
L_000a539a:
    mov.l P_000a54f8,r6
    .org 0xa539c-ORIGIN
L_000a539c:
    mov.b @r6,r0
    .org 0xa539e-ORIGIN
L_000a539e:
    tst 0x20,r0
    .org 0xa53a0-ORIGIN
L_000a53a0:
    bt L_000a5430
    .org 0xa53a2-ORIGIN
L_000a53a2:
    mov.w P_000a54c0,r6
    .org 0xa53a4-ORIGIN
L_000a53a4:
    mov.b @r6,r0
    .org 0xa53a6-ORIGIN
L_000a53a6:
    tst 0x40,r0
    .org 0xa53a8-ORIGIN
L_000a53a8:
    bt L_000a5438
    .org 0xa53aa-ORIGIN
L_000a53aa:
    mov.l P_000a54d0,r2
    .org 0xa53ac-ORIGIN
L_000a53ac:
    mov.w P_000a54c2,r0
    .org 0xa53ae-ORIGIN
L_000a53ae:
    mov.b @(r0,r2),r4
    .org 0xa53b0-ORIGIN
L_000a53b0:
    mov.l P_000a54fc,r2
    .org 0xa53b2-ORIGIN
L_000a53b2:
    extu.b r4,r4
    .org 0xa53b4-ORIGIN
L_000a53b4:
    mov.b @r2,r5
    .org 0xa53b6-ORIGIN
L_000a53b6:
    extu.b r5,r5
    .org 0xa53b8-ORIGIN
L_000a53b8:
    cmp/gt r5,r4
    .org 0xa53ba-ORIGIN
L_000a53ba:
    bf L_000a5438
    .org 0xa53bc-ORIGIN
L_000a53bc:
    mov.l P_000a5500,r6
    .org 0xa53be-ORIGIN
L_000a53be:
    mov.l P_000a5504,r2
    .org 0xa53c0-ORIGIN
L_000a53c0:
    mov.w @(0x14,r6),r0
    .org 0xa53c2-ORIGIN
L_000a53c2:
    mov.b @r2,r6
    .org 0xa53c4-ORIGIN
L_000a53c4:
    extu.w r0,r7
    .org 0xa53c6-ORIGIN
L_000a53c6:
    extu.b r6,r2
    .org 0xa53c8-ORIGIN
L_000a53c8:
    mul.l r7,r2
    .org 0xa53ca-ORIGIN
L_000a53ca:
    mov #-0x1,r6
    .org 0xa53cc-ORIGIN
L_000a53cc:
    extu.w r6,r6
    .org 0xa53ce-ORIGIN
L_000a53ce:
    sts macl,r2
    .org 0xa53d0-ORIGIN
L_000a53d0:
    shlr8 r2
    .org 0xa53d2-ORIGIN
L_000a53d2:
    cmp/hi r6,r2
    .org 0xa53d4-ORIGIN
L_000a53d4:
    bf L_000a53d8
    .org 0xa53d6-ORIGIN
L_000a53d6:
    mov #-0x1,r2
    .org 0xa53d8-ORIGIN
L_000a53d8:
    extu.w r2,r6
    .org 0xa53da-ORIGIN
L_000a53da:
    mov.l P_000a5508,r2
    .org 0xa53dc-ORIGIN
L_000a53dc:
    sub r5,r4
    .org 0xa53de-ORIGIN
L_000a53de:
    mul.l r6,r4
    .org 0xa53e0-ORIGIN
L_000a53e0:
    mov.b @r2,r7
    .org 0xa53e2-ORIGIN
L_000a53e2:
    extu.b r7,r7
    .org 0xa53e4-ORIGIN
L_000a53e4:
    tst r7,r7
    .org 0xa53e6-ORIGIN
L_000a53e6:
    bt/s L_000a540e
    .org 0xa53e8-ORIGIN
L_000a53e8:
    sts macl,r5
    .org 0xa53ea-ORIGIN
L_000a53ea:
    mov #-0x80,r4
    .org 0xa53ec-ORIGIN
L_000a53ec:
    extu.b r4,r4
    .org 0xa53ee-ORIGIN
L_000a53ee:
    shll16 r4
    .org 0xa53f0-ORIGIN
L_000a53f0:
    mov #0x0,r6
    .org 0xa53f2-ORIGIN
L_000a53f2:
    mov #0x8,r1
    .org 0xa53f4-ORIGIN
L_000a53f4:
    extu.b r6,r6
    .org 0xa53f6-ORIGIN
L_000a53f6:
    cmp/ge r7,r6
    .org 0xa53f8-ORIGIN
L_000a53f8:
    bf L_000a53fe
    .org 0xa53fa-ORIGIN
L_000a53fa:
    cmp/ge r1,r6
    .org 0xa53fc-ORIGIN
L_000a53fc:
    bt L_000a540e
    .org 0xa53fe-ORIGIN
L_000a53fe:
    cmp/hs r4,r5
    .org 0xa5400-ORIGIN
L_000a5400:
    bf L_000a5408
    .org 0xa5402-ORIGIN
L_000a5402:
    mov.l P_000a550c,r5
    .org 0xa5404-ORIGIN
L_000a5404:
    bra L_000a540e
    .org 0xa5406-ORIGIN
L_000a5406:
    nop
    .org 0xa5408-ORIGIN
L_000a5408:
    shll r5
    .org 0xa540a-ORIGIN
L_000a540a:
    bra L_000a53f4
    .org 0xa540c-ORIGIN
L_000a540c:
    add 0x1,r6
    .org 0xa540e-ORIGIN
L_000a540e:
    mov.l P_000a54d0,r3
    .org 0xa5410-ORIGIN
L_000a5410:
    mov r5,r2
    .org 0xa5412-ORIGIN
L_000a5412:
    mov.w P_000a54c4,r0
    .org 0xa5414-ORIGIN
L_000a5414:
    shlr16 r2
    .org 0xa5416-ORIGIN
L_000a5416:
    mov.w @(r0,r3),r5
    .org 0xa5418-ORIGIN
L_000a5418:
    extu.w r5,r5
    .org 0xa541a-ORIGIN
L_000a541a:
    add r2,r5
    .org 0xa541c-ORIGIN
L_000a541c:
    mov #-0x1,r2
    .org 0xa541e-ORIGIN
L_000a541e:
    extu.w r2,r2
    .org 0xa5420-ORIGIN
L_000a5420:
    cmp/hi r2,r5
    .org 0xa5422-ORIGIN
L_000a5422:
    bf L_000a5426
    .org 0xa5424-ORIGIN
L_000a5424:
    mov #-0x1,r5
    .org 0xa5426-ORIGIN
L_000a5426:
    mov.l P_000a54d0,r3
    .org 0xa5428-ORIGIN
L_000a5428:
    mov.w P_000a54c4,r0
    .org 0xa542a-ORIGIN
L_000a542a:
    mov.w r5,@(r0,r3)
    .org 0xa542c-ORIGIN
L_000a542c:
    bra L_000a5438
    .org 0xa542e-ORIGIN
L_000a542e:
    nop
    .org 0xa5430-ORIGIN
L_000a5430:
    mov.l P_000a54d0,r3
    .org 0xa5432-ORIGIN
L_000a5432:
    mov #0x0,r2
    .org 0xa5434-ORIGIN
L_000a5434:
    mov.w P_000a54c4,r0
    .org 0xa5436-ORIGIN
L_000a5436:
    mov.w r2,@(r0,r3)
    .org 0xa5438-ORIGIN
L_000a5438:
    rts
    .org 0xa543a-ORIGIN
L_000a543a:
    lds.l @r15+,macl
    .org 0xa54c0-ORIGIN
P_000a54c0:
    .word 0x84c3
    .org 0xa54c2-ORIGIN
P_000a54c2:
    .word 0x0a92
    .org 0xa54c4-ORIGIN
P_000a54c4:
    .word 0x0a3c
    .org 0xa54d0-ORIGIN
P_000a54d0:
    .long 0xffff28f8
    .org 0xa54f8-ORIGIN
P_000a54f8:
    .long 0xffff244f
    .org 0xa54fc-ORIGIN
P_000a54fc:
    .long 0x00008cba
    .org 0xa5500-ORIGIN
P_000a5500:
    .long 0xffff102c
    .org 0xa5504-ORIGIN
P_000a5504:
    .long 0x000083ec
    .org 0xa5508-ORIGIN
P_000a5508:
    .long 0x00008a0d
    .org 0xa550c-ORIGIN
P_000a550c:
    .long 0x00ffffff
