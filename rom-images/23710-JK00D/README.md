# 23710-JK00D additional evidence

This is an owned read from a physical bench ECU made on 2026-07-26 with
PCMFlash 1.2.0 module 18 through Scanmatik-SM2 USB. The directory also retains
`1JK00D-20260726-pcmflash-identification.png` as the successful identification
record.

The calibration, software identifier, MCU class, and Hitachi CAN protocol in
the screenshot agree with the ROM strings tabulated in
`../README.md#identity-strings`. PCMFlash reports the main number from the
second identity block, so the `7MFKAVN86` string this image carries in the
first block does not identify it. The donor vehicle and market remain unknown.
The package contains no external EEPROM read; this does not establish that the
hardware lacks one.

Identity and stock hashes are authoritative in `../roms.csv` and
`../README.md`.
