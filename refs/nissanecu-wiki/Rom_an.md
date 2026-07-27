# Rom an

> Local mirror of a NissanECU RE wiki page. Source: https://nissanecu.miraheze.org/wiki/Rom_an
> Retrieved: 2026-07-15. License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) ()

---

# Intro

These are ROMs which I (fenugrec) initially analyzed as part of the crowdfunding campaing for the reflashing kernel. 

All additional observations, notes and data are *very* useful ! Feel free to add stuff here; if it's something tentative or unconfirmed, it should still be added, with the note "unconfirmed". 

A lot of concepts are covered elsewhere ( <https://nissanecu.miraheze.org/wiki/Firmware_re> ). Most of this assumes that the reader will be familiar with microcontrollers and low level programming in general. 

It goes without saying that the SuperH docs (datasheet and software reference Manual), listed on <https://nissanecu.miraheze.org/wiki/Sh_docs> , should be kept handy. 

# Definitions and conventions

Everything is of course based only on my limited experience, and can therefore be wrong or misleading. Some of the naming conventions are my own and are just the first names I came up with when analyzing code. 

To lighten the text, I will often write " in every ROM" or " always"; what I really mean is " in every ROM I've seen", which consists of only about 30 ROMs. 

In general I use a notation very similar to standard C. Some examples: 

  * << means binary left shift
  * & between numbers or register names means a bitwise AND, which is **not** the same thing as the logic AND operator &&. (0x55 & 0xF0) == 0x50.
  * & prefixed to a name means "address of". i.e. "r4=&table_axis" would mean " write the address of table_axis to the register r4".



For table(map) names, I use mostly "t_<elem_size>_aXb_addr", and a few of a previous notation "t<size>_AxB_addr". Axis : ax_<num_elems>_<elem_size>_addr. 

Examples: 

  * _t_b_8X8_8EED_ means an 8x8 table, where each value is a byte; table stored at 0x8EED in the ROM.
  * _t16u_1x32_DE58_ is a 1x32 table of 16bit words.
  * _ax_16_u8_DDA8_ is a 16-element axis of bytes, at 0xDDA8.



# Function naming, abbreviations

  * alt_ : alternate
  * s27, s36: related to SID 27 or 36
  * _encr_* : parts of the [security algorithm](<https://nissanecu.miraheze.org/wiki/Firmware_re#security_.2F_encryption> "Firmware re")
  * cks: checksum
  * div: division functions. There are many variations of these
  * RDtable_<size>_<table_dimensions>  : read data from table
  * interp: interpolation functions
  * TPS: throttle position sensor
  * APS : accelerator position sensor
  * INT_ : interrupt handlers
  * ASCD: cruise control
  * test_every_instr : a weird function that seems to test all the functionality, all the opcodes of the CPU core



Hopefully the rest will be self-explanatory. 

# Analyzed ROMs

  * [AL500 - '01 Skyline V35, VQ25DD](<https://nissanecu.miraheze.org/wiki/Rom_an_al500> "Rom an al500")
  * [CF43D - '06 350Z, VQ35DE](<https://nissanecu.miraheze.org/wiki/Rom_an_cf43d> "Rom an cf43d")
