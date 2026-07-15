# Rom db

> Зеркало страницы NissanECU RE wiki. Источник: https://nissanecu.miraheze.org/wiki/Rom_db
> Retrieved: 2026-07-15. License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) ()

---

# Known ROMs & ECUIDs

**Not updated since ~ 2017** \-- refer to the [Stock ROM list](<http://www.romraider.com/forum/viewtopic.php?f=35&t=11098>) @ RR forums. Updating that one and this copy here is tedious and unpleasant, and I've proven to be too lazy to maintain both. I'm open to suggestions (i.e. give me a script !) to automate this; the source data is an .ods spreadsheet. 

## master list

Model  | Year  | Engine  | ECUID  | FID  | FID IC  | LOADER  | Checksum  | IVT2  | PCB type  | sauce  | Notes   
---|---|---|---|---|---|---|---|---|---|---|---  
|  |  |  |  |  |  |  |  |  |  |   
Juke  | 10?  | YF15  | 1KA6A  | 1XHK14CDG  | 705828 | 80, 705828  | alt,alt2,RM160  | 0x2 0004 |  | Shuher @ RR  |   
Juke  | 10?  | YF15  | 1KE9C  | 2XHK19BDF1  | 705828 | 80, 705828  | alt,alt2,RM160  | 0x2 0004 |  | Shuher @ RR  | Bad altcks ?   
Juke  | 10?  | YF15  | 1KN0B  | 0KHD95DZ3  | 705828 | 80, 705828  | alt,alt2,RM160  | 0x2 0004 |  | Shuher @ RR  | Bad altcks ?   
I30?  | 01  | ?  | 5Y006  | 1ZVMAT0NH  | 705507 | N/A  | std  | N/A |  | murphys_law @ RR  | AT   
Maxima  | 02-03  | VQ35  | 5Y702  | 1TKE8Z5N53  | 705507 | N/A  | std,alt  | N/A |  | murphys_law @ RR  | MT   
Maxima C/A33  | 02  | VQ35  | 5Y724  | 1TKE8Z5N53  | 705507 | N/A  | std,alt  | N/A |  | murphys_law @ RR  | AT, TCS, ECUID6Y324 Replaces 5Y724, 6Y320-6Y323, also used in MY03-04 Infiniti I35   
Maxima  | 02-03  | VQ35  | 6Y300  | 1TKE8Z5N56  | 705507 | N/A  | std,alt  | N/A |  | murphys_law @ RR  | MT   
Maxima A33  | 02-03  | VQ35DE  | 6Y303  | 1TKE8Z5N59  | 705507 | N/A  | std,alt  | N/A | ? | murphys_law @ RR  | 6MT, MY02-03. â€œUnisia Jecsâ€   
Sentra B15  | 05  | QG18DE  | 6Z68A  | 5X6E58STZNM  | 705821 | 50, 705521  | std,alt  | 0x1000 | A | fenugrec | MT   
Maxima  | 05  | VQ35DE  | 7Y210  | 5ZVTDNK  | 705821 | 50, 705521  | std,alt  | 0x1000 | A | AKEyes @ RR | Type A pcb with silkscreen !. Maxima SE, ATX. Model BLJALVN-EU5   
Sentra B15  | 02  | QR25DE  | 8U023  | 3TREE21N14  | 705507 | N/A  | std,alt  | N/A | F | Moldbruja @ NDS | MT, Incomplete dump,bad std_cks, possibly corrupt FID   
Sentra B15  | 02  | QR25DE  | 8U07A  | 3TREE21N15  | 705507 | N/A  | std,alt  | N/A |  | murphys_law @ RR | MT, NDS forums. 02 Spec V USDM Fed emission + NATS   
Sentra B15  | 04  | QR25DE  | 8U92A  | 5X61BECCNA  | 705513 | 10, 705513  | std,alt  | 0x1000 |  | fenugrec | MT, no ABS, cruise ctl; OBD K line only, ASCD + NATS immo   
Altima L32  | 11-12  | ?  | 9HA7D  | 2TRKH4SN05  | 705828 | 80, 705828  | alt,alt2,RM160  | 0x2 0004 | ? | hs- @ RR | CVT. Bad altcks ?   
G35  | 04  | ?  | AC011  | 3GIMBN06  | 705513 | 10, 705513  | std,alt  | 0x1000 |  | nosajton @ RR | 5AT   
G35/V35  | 04  | VQ35DE  | AC401  | 5ZVS8N02  | 705821 | 50, 705521  | std,alt  | 0x1000 |  | nosajton @ RR | Skyline/G35 Coupe 5AT "dual bosch wideband ctl", 2WD   
G35/V35  | 04  | VQ35DE  | AC405  | 5ZVP8N00  | 705821 | 50, 705521  | std,alt  | 0x1000 |  | nosajton @ RR | USDM 6MT Coupe. 512k file but sh7058 is reported => bad cks   
Gloria Y34  | ?  | VQ30  | AG920  | 9QE4V3DQ  | 705101 | N/A  | std, ?  | N/A | E | Jchau1 @ RR | Y34 Gloria; no alt checksum ? didnâ€™t check thoroughly. Dual 7051   
G35  | 03  | VQ35  | AM604  | 3MFED18N8  | 705507 | N/A  | std,alt  | N/A |  | nosajton @ RR | AT   
Primera P12  | 02  | QR20DE  | AU40B  | 0TRE6Z8D8  | 705507 | N/A  | std,alt  | N/A | F | Shuher @ RR |   
?  | ?  | ?  | AV722  | 1MC3QMEP0  | 705513 | 10, 705513  | std,alt  | 0x1000 |  | Piasini @ OE | Probably corrupt (std checksum fails)   
Almera?  | ?  | N16E?  | BN915  | 1MC3FVEM  | 705513 | 10, 705513  | std,alt  | 0x1000 |  | Shuher @ RR  |   
350Z Z33  | 03  | VQ35DE  | CD002  | 3GILXN05  | 705513 | 10, 705513  | std,alt  | 0x1000 |  | repro file @ OE | Decrypted from repro file; MT ASCD TCS   
350Z  | ?  | VQ35DE?  | CD405  | 2WLGHD10  | 705513 | 10, 705513  | std,alt  | 0x1000 |  | NDS2 |   
350Z  | 03  | VQ35DE  | CD415  | 2WLGHD10  | 705513 | 10, 705513  | std,alt  | 0x1000 |  | _Leo_ @ RR | JDM AT, 7055F40 topcode   
350Z  | 05  | VQ35DE  | CF000  | 5ZVSUNH  | 705821 | 50, 705521  | std,alt  | 0x1000 |  | AKEyes @ RR |  Touring Model, Non-RevUp motor (redline 6500), MT, Cruise, ABS   
350Z  | 05  |  | CF065  | 5ZVSVNJ  | 705821 | 50, 705521  | std,alt  | 0x1000 |  | Swami @ RR | JDM. Posted a corrupt ROM, fixing IVT1 first entries solves it   
350Z  | 06  | VQ35DE  | CF43D  | 6GI5VN6  | 705823 | 60, 705823  | std,alt  | 0x2000 | A | AKEyes @ RR | MT, base, no cruise, with RevUp (variable exh valve timing)   
G35  | 06  |  | CM31C  | 6GI5VN6  | 705823 | 60, 705823  | std,alt  | 0x2000 |  | murphys_law @ RR | 6 MT Rev up Sport   
Q45  | 04  | VK45  | CS500  | M4ZHEPEN3  | 705507 | N/A  | std, ?  | N/A |  | Spawn32 @ RR |   
Note/Tiida?  | 04-07?  | HR16DE  | EC80A  | 5CMCE3E6  | 705520 | 40, 705520  | std,alt  | 0x1000 | D | Shuher @ RR | Probable corruption @ 0x76,77,300,301. Almost identical to EC82A   
Note/Tiida?  | 04-07?  | HR16DE  | EC82A  | 5CMCE3E6  | 705520 | 40, 705520  | std,alt  | 0x1000 | D | Shuher @ RR |   
Note/Tiida?  | 04-07?  | HR16DE  | EC87A  | 5CMC9EE5  | 705520 | 40, 705520  | std,alt  | 0x1000 | D | Shuher @ RR |   
Fuga Y50?  | 04-09?  | VQ35DE  | EG03E  | 5ZVPCN116  | 705821 | 50, 705521  | std,alt  | 0x1000 |  | _Leo_ @ RR | JDM, dual WB O2   
Tiida  | 04-12?  | HR16DE  | EM62B  | 1CMC7QPD401  | 705519 | 80, 705519  | alt,alt2,RM160  | 0x10004 |  | Shuher @ RR | special loader80; bad altcks ?, CAN only   
Note/Tiida?  | 04-07?  | HR16DE  | EM63A  | 9CMCS5E0  | 705520 | 40, 705520  | std,alt  | 0x1000 | D? | Shuher @ RR |   
?  | ?  |  | ET81A  | 7TRKEWBTN6  | 705822 | 80, 705822  | alt,alt2,RM160  | 0x2 0004 |  | Piasini |   
350Z  | ?  | VQ35HR  | EV15A  | 7MFKAWNE  | 705822 | 80, 705822  | alt,alt2,RM160  | N/A |  | Piasini | Hacked / tuned 350Z ROM, IVT2 @ 0x1FF2C   
X-trail  | 05  | QR25DE  | EQ910  | 3TRTTE6  | 705513 | 10, 705513  | std,alt  | 0x1000 | B | jaf @ NDS2 | MT   
Altima L32  | 08?  | QR25DE  | JA90C  | 8TRKEJJN8  | 705822 | 80, 705822  | alt,alt2,RM160  | 0x2 0004 |  | Piasini | CVT 2WD ABS ASCD   
Patrol  | 02?  | TB48  | VC85A  | M1APEGSE9  | 705507 | N/A  | std, ?  | N/A |  | Spawn32 @ RR | throttle by wire; 2x knock sensor + VCT   
Patrol  | 09  | TB48  | VD70A  | M4APE3RE3  | 705507 | N/A  | std  | N/A |  | Spawn32 @ RR | A/T; M/T model would lack the secondary 7051 ?   
Altima L31  | 06  | QR25DE  | ZD89A  | 6X6E58SYMN36  | 705823 | 60, 705823  | std,alt  | 0x2000 | C | AKEyes @ RR | AT, ASCD 50 State ULEV
