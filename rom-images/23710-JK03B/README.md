# 23710-JK03B additional evidence

This is an owned pre-write physical-ECU read made on 2026-08-04 with PCMFlash
1.2.0 module 18 through Scanmatik-SM2 USB. The original PCMFlash filename was
`1JK03B_7MFKAVN86-20260804-013935_MEC100-191-A1-7911.bin`; it preserves the
Hitachi hardware identifier `MEC100-191 A1` and lot `7911`.

Exact-part and hardware-family sources associate the ECU with a JDM V36
Skyline 250GT, VQ25HR, and automatic transmission. Its known executable ranges
are byte-identical to JK00A, JK03A, and JK08A. JK03B has no Ghidra export,
Memgraph layer, or annotation inheritance entry.

The complete pre-write line `[0x8080, 0x8100)` contains `0xEE`. A later
marker-only readback from the same programming workflow contains zero there,
which rules out an unconditional PCMFlash read transformation. The remaining
evidence does not distinguish checksum correction from a module-18 programming
rule.

Application sources:

- https://otomotiv-forum.com/threads/chip-ttyuning-nissan-skyline-v36-at-2-5i-proshivka-yevro-2-tyun.63512/
- https://yahoo.aleado.com/lot?auctionID=m403371593

Identity and stock hashes are authoritative in `../roms.csv` and
`../README.md`; derived-image identities are in
`../../patches/hardware-results.toml`.
