# 23710-JK00C additional evidence

This is an owned pre-write physical-ECU read made on 2026-08-03 with PCMFlash
1.2.0 module 18 through Scanmatik-SM2 USB. The original PCMFlash filename was
`1JK00C_8MFKPCN14-20260803-221649_MEC100-120-C1-6Z03.bin`; it preserves the
Hitachi hardware identifier `MEC100-120 C1` and lot `6Z03`.

The same physical ECU was later used for a controlled map-switching boot-failure
reproduction. This stock file is the pre-write baseline, not a readback of a
JK08A or modified image. The stock image is imported into the project Ghidra
workspace and has a complete local function, call, xref, and interpolation
resolver export. Its durable semantic layer remains tracked in Git.

ROM strings confirm the local identification; they are tabulated in
`../README.md#identity-strings`. PCMFlash reports the main number from the
second identity block, so the `7MFKAVN86` string this image carries in the
first block does not identify it.

Public listings associate the `MEC100-120 C1` hardware family with an automatic
JDM PV36 Skyline 350GT and VQ35HR. No exact `23710-JK00C` public catalog record
was found, so the application remains hardware-family evidence. JK00C and
JK00D use different software IDs and are not an exact-code pair.

Application sources are in `../README.md#sources`.

Identity and stock hashes are authoritative in `../roms.csv` and
`../README.md`; modified-image outcomes are in
`../../patches/hardware-results.toml`.
