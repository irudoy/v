# Sh docs

> Local mirror of a NissanECU RE wiki page. Source: https://nissanecu.miraheze.org/wiki/Sh_docs
> Retrieved: 2026-07-15. License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) ()

---

[Renesas](<http://am.renesas.com/>) (previously Hitachi) makes the [SuperH microcontrollers](<http://am.renesas.com/products/mpumcu/superh/index.jsp?campaign=tb_prod>) used in Nissan ECUs: 

  * [SH7055 (older version, mfg by Hitachi)](<https://static.miraheze.org/nissanecuwiki/c/ce/Sh7055h.pdf>)
  * SH7055s
  * HD64F7058 - older version, mfg by Hitachi
  * [SH7058](<http://am.renesas.com/products/mpumcu/superh/sh7050/sh7058/index.jsp>) \- Renesas
  * SH7058S
  * SH72531 ?



You need BOTH these documents: 

  1. the datasheet for your particular ECU, such as "[REJ09B0046](<https://www.renesas.com/en-us/doc/products/mpumcu/001/rej09b0046_sh7058.pdf>)" for sh7058.
  2. the appropriate "software manual" for the ECU family, like [REJ09B0316 - SH-2E Software manual](<https://www.renesas.com/en-us/doc/products/mpumcu/001/rej09b0316_sh_2esm.pdf>) . This describes the architecture and instruction set.



## 7055 / 7058 "versions"

These 705x ICs were manufactured by Hitachi until ~2002-2003, when Renesas was formed (2003/04/01). 

Rough chronology of 705x products : 

  * 7055F (0.35um), [(1998 news release)](<http://www.hitachi.com/New/cnews/E/1998/980715B.html>) to ~ 2003 ? (Hitachi datasheet 3rd edition April 2000)
  * 7055SF (0.18um), ~ 2003 onwards ? (Renesas datasheet: 1st edition May 2002).
  * 7058 a.k.a. 7058F (0.18um, see [2002/09/24 news release](<http://www.hitachi.co.jp/New/cnews/2002/0924/index.html>)), 2002 to at least 2004+ . Hitachi datasheet says "1st edition, April 2002", Renesas DS says July 2002.
  * 7058S (0.18um), 2007-? (Renesas datasheet : Rev.1.00, feb 21, 2007)



For 7055F, around 2003 the silicon process size changed from 0.35um to 0.18um. The impact of this is major when it comes to reflashing. The ROM/FLASH registers are totally different; they require vastly different code to reflash them. 

As for the old vs new 7058 ICs, there appears to be no such change, i.e. the same registers are used and the reflash process is the same, hence the same code can be used. 

### How to tell between 7055 versions

  * Package markings for 7055 : 
    * First line : "64F7055F40", no help there
    * Datecode : 4-digit number below the first line (format: YYWW, WW is week #). Datecodes up to 2002 are probably 0.35um, and somewhere during 2003 it would changeto 0.18um -- any additional info about this would be appreciated !!


  * Package markings for 7058 : 
    * 7058 : both "64F7058F80", but it's a non-issue (always 0.18um)


  * The "model name" may be different (not sure how to determine this, however). Note that Hitachi and Renesas were not very rigorous about the naming, sometimes they had the trailing 'F', some datasheets have typos, etc... 
    * 7055 : old = HD64F7055R, new = HD64F7055S
    * 7058 : probable typo in the old datasheet; old=HD64F7055S, new = HD64F7058BF80(L/K)


  * "Supported Device Inquiry" command in SHBootmode, unfortunately the DS isn't overly clear about the expected response. The .fcf files included in Renesas FDT list these device codes : 
    * (0402 for 0.35um 7052)
    * 0405 for 0.35um 7055
    * (0406 for 0.35um 7065)
    * 0601 for 0.18um 7058


  * FID IC code in the ROM ? This is unverified, but maybe "705507" and "705513" is 0.35um, and "705519" and onwards is 0.18um ?
  * It's possible to read/write certain FLASH registers and observe behavior. For instance, FKEY is only implemented on 0.18um devices, etc.
