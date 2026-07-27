# SID22

> Local mirror of a NissanECU RE wiki page. Source: https://nissanecu.miraheze.org/wiki/SID22
> Retrieved: 2026-07-15. License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) ()

---

## misc info  
  
SID 22 requests retrieves data for a certain 16-bit "Common ID" (hereafter "CID"), for example 0x120D. They can be split in high byte and low byte, such that CIDH=0x12 and CIDL = 0x0D. This is just to categorize the CIDs. 

## Response length

I think this is common accross all ECUs : 

  * CIDH = 0x11 : 1 byte response
  * CIDH = 0x12 : 2 byte response
  * CIDH = 0x13 : 4 byte response
  * CIDH = 0x14 : 1 byte response
  * CIDH = 0x15 : 4 byte response



There are some exceptions, i.e. CID 120B that has something to do with DTCs.
