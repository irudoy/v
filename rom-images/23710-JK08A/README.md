# 23710-JK08A target evidence

This is the owned stock read from the physical V36 Skyline 250GT target ECU,
made on 2026-07-26 with PCMFlash 1.2.0 module 18 through Scanmatik-SM2 USB.
The PCMFlash MD5 agrees with the stored sidecar. No identification screenshot
or external EEPROM read is part of the package.

Donor JK03A uses the same MCU class and software ID. The images differ only in
calibration/configuration regions; known executable ranges are byte-identical.
The delta includes the ROM identity, checksum fields, four unnamed candidate
curves, and diagnostic descriptors. The live JK08A definition excludes those
four candidates; all other exposed table and axis bytes are identical to the
donor projection.

Identity and stock hashes are authoritative in `../roms.csv` and
`../README.md`. Current definition evidence is under `../../defs/`; derived
image outcomes are in `../../patches/hardware-results.toml`.
