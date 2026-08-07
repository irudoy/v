# 23710-JK00C additional evidence

This is an owned pre-write physical-ECU read made on 2026-08-03 with PCMFlash
1.2.0 module 18 through Scanmatik-SM2 USB. The original PCMFlash filename was
`1JK00C_8MFKPCN14-20260803-221649_MEC100-120-C1-6Z03.bin`; it preserves the
Hitachi hardware identifier `MEC100-120 C1` and lot `6Z03`.

The same physical ECU was later used for a controlled map-switching boot-failure
reproduction. This stock file is the pre-write baseline, not a readback of a
JK08A or modified image. It has no Ghidra export or Memgraph layer.

Public listings associate the `MEC100-120 C1` hardware family with an automatic
JDM PV36 Skyline 350GT and VQ35HR. No exact `23710-JK00C` public catalog record
was found, so the application remains hardware-family evidence. JK00C and
JK00D use different software IDs and are not an exact-code pair.

Application source: https://www.ebay.com/itm/284029944805

Identity and stock hashes are authoritative in `../roms.csv` and
`../README.md`; modified-image outcomes are in
`../../patches/hardware-results.toml`.
