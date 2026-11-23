# 23710-1EK7A flash image

PCMFlash 1.2.0 module 18, DLL 1.0.0.124, read this flash on 2026-11-22
through a Scanmatik SM2 USB interface using the Hitachi CAN
`EFI SH705927N (Hitachi SH7059/1.5MB)` protocol. The identification log
and donor note describe a 2013 Nissan 370Z Z34 with a VQ37VHR engine and
manual transmission. The read consists of internal flash. The ECU label
and hardware lot are unknown. PCMFlash reported a successful checksum
verification after reading. The stock vector SUM16 discrepancy found by
independent verification is documented in
[`rom-selftest-checksum.md`](../../patches/rom-selftest-checksum.md).

The image holds `SH705927N` at `0x004E5A` and `0x022A7A`, `2FZ35YN21` at
`0x006F09`, and two copies of `11EK7A00000` starting at `0x008204`. The
identity blocks at `0x006F00` and `0x007000` begin with `1UX0A` and `1EK7A`
respectively. The first holds the base string and the second has an empty
software field.

The image uses a distinct address layout. Its registered fused interpolation
functions have exact L0 function hashes at offset `+0xB94` from their 1ME3B
counterparts. The application reset vectors start at `0x020004` and
the diagnostic descriptors and attribute pointers start at `0x01C998` and
`0x01DA3C`. The ROM catalog owns the image digest and
[`homology.csv`](../homology.csv) holds the pairwise code-window comparison.
