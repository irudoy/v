# Main Page

> Зеркало страницы NissanECU RE wiki. Источник: https://nissanecu.miraheze.org/wiki/Main_Page
> Retrieved: 2026-07-15. License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0) ()

---

# Nissan Consult-II ECU reverse-engineering & reflashing

Notes and resources concerning Nissan / Infiniti ECUs. The focus is those units based on Renesas SuperH microcontrollers (typically SH7055 or SH7058 but also SH7051 and SH7054 on earlier models). These seem to be used in vehicles from approx MY01-MY10. 

## Goal

Reflashing those ECUs safely and reliably, without needing to open the (sealed) case. This means through the OBD2 K line, or CAN bus. This has been done; typically those who have gone through this RE process have then disappeared or started a business selling their services. Hence, everybody keeps reinventing the wheel, and this is why the Nissan tuning scene is about 15 years behind Subaru ! Hopefully this wiki can help share painstakingly obtained knowledge. 

## Main external resources

These are the main places where work is being done on these ECUs. 

  * Ongoing discussion and analysis of ROMs on the RomRaider forums: [Main Nissan Forums](<https://www.romraider.com/forum/viewforum.php?f=45>)
  * List of known ECUIDs and basic information @ RR ["Nissan stock ROM list" thread](<http://www.romraider.com/forum/viewtopic.php?f=35&t=11098>)
  * [Nissan ECU unbricking tutorial with "shbootmode"](<http://www.romraider.com/forum/viewtopic.php?f=7&t=12821>)



## ECU Analysis Pages

  * Hardware Related 
    * [ECU Hardware Versions](<https://nissanecu.miraheze.org/wiki/Ecu_hw> "Ecu hw")
    * [SuperH Documents](<https://nissanecu.miraheze.org/wiki/Sh_docs> "Sh docs")
    * [EEPROM Dumps](<https://nissanecu.miraheze.org/wiki/Eeprom_dumps> "Eeprom dumps")
    * [Firmware Analysis , RE, Algorithms](<https://nissanecu.miraheze.org/wiki/Firmware_re> "Firmware re")
    * [Writing Code for the SuperH (Kernel Focused)](<https://nissanecu.miraheze.org/wiki/Sh_dev> "Sh dev")


  * [Connecting to the ECU](<https://nissanecu.miraheze.org/wiki/Connect> "Connect")
    * ["SHBootmode" Flashing / Unbricking / etc](<https://nissanecu.miraheze.org/wiki/Bootmode> "Bootmode")
    * [AUD](<https://nissanecu.miraheze.org/wiki/AUD> "AUD")
    * [Software tools](<https://nissanecu.miraheze.org/wiki/Tools> "Tools")


  * [Analysis notes for certain ROMs](<https://nissanecu.miraheze.org/wiki/Rom_an> "Rom an")
    * [AL500 - '01 Skyline V35, VQ25DD](<https://nissanecu.miraheze.org/wiki/Rom_an_al500> "Rom an al500")
    * [CF43D - '06 350Z, VQ35DE](<https://nissanecu.miraheze.org/wiki/Rom_an_cf43d> "Rom an cf43d")
