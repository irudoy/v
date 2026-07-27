# Tools

> Local mirror of a NissanECU RE wiki page. Source: https://nissanecu.miraheze.org/wiki/Tools
> Retrieved: 2026-07-15. License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) ()

---

# Some software tools

To help with haxing ROMs etc. 

## freediag

  * Project page and some builds: [freediag @ sourceforge](<http://freediag.sourceforge.net>)
  * Source code : [freediag @ github](<http://github.com/fenugrec/freediag>)



## Nisprog

Nisprog is a tuning utility for SH7051, SH7055, and SH7058 Nissan/Infiniti ECU's. It's primarily used for dumping and reflashing the ROM image stored within the vehicle's ECU. However, it is capable of various other things as well. 

For the moment, nisprog is just the name I give to special freediag builds that include some Nissan functionality. Eventually it will be forked, and link to freediag's "libdiag" backend. I post some of these builds on the RR forums. 

**Download Links;  
** **Non-Compiled Nisprog - >** <https://github.com/fenugrec/nisprog>   
**Compiled Nisprog - >** [https://romraider.com/forum/viewtopic.php?f=45&t=13259](<https://romraider.com/forum/viewtopic.php?f=45&t=13259>)

## IDA

'nuff said. 

  
Adding extra processor defines can be useful to show the peripheral register names, and fill in the reset vector (IVT) with vector names. 

User dschultz @ RR forums started this with a [sh3.cfg](<http://www.romraider.com/forum/viewtopic.php?f=40&t=5825>) file to replace the stock file included with IDA. I expanded on the idea and added definitions for the secondary vector table so popular in Nissan ROMs. That is, they have only a partial vector table at address 0; the power-on reset code then sets the vbr register to point at the complete table either @ 0x1000 , 0x2000, or 0x0002 0004 depending on the firmware revision. 

I keep my expanded configs on my [github repo](<https://github.com/fenugrec/nisprog/tree/master/ida_helpers/cfg>)

**Download Link;**  
**IDA Pro - > ** <https://www.hex-rays.com/cgi-bin/quote.cgi>

## Ghidra

The IDA killer.   


A free disassembler that can do just about anything non-hardcore enthusiasts could want it to do. 

**Download Link;**  
**Ghidra - > ** <https://ghidra-sre.org/>

## Notepad++

Extremely useful tool for viewing xml files. The color coding helps you identify the attributes and make proper changes. 

Hint: Go to Plugins Tab -> Plugins Admin and download "XML Tools" and "Npp Xml Treeview"

**Download Link;**   
**Notepad++ - > ** <https://notepad-plus-plus.org/downloads/>

## WinOLS

Useful even in its demo version, it makes it easier to find, visualize & edit maps in a ROM. 

**Download Link;**  
_**WinOLS Demo Version - >**_ <https://www.evc.de/en/download/down_winols.asp>

## Renesas HEW

Renesas [High-performance Embedded Workshop](<https://www.renesas.com/en-us/products/software-tools/tools/ide/hew.html>), their complete IDE including compiler, assembler and simulator (very useful for analyzing sections of code). Note, apparently HEW isn't available on its own, but is included with [the C compiler package](<https://www.renesas.com/en-us/software/D3017586.html>) ! 

NOTE concerning simulator : it simulates the core quite well, but is *very* limited in peripheral support. Only some DMA features and very very simple timers are simulated. Important stuff missing: 

  * SCI
  * HCAN
  * Everything ATU related
  * Everything else



Very cool thread on how to get started with HEW : [Hacking with HEW](<http://www.romraider.com/forum/viewtopic.php?f=40&t=7680>)

## Renesas FDT

Renesas [Flash Development Toolkit](<http://am.renesas.com/products/tools/flash_prom_programming/fdt/index.jsp>), utilities for reflashing SuperH mcus.
