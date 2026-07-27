# 1JK08A immo-off

One-bit modification for `23710-JK08A`, released on 2026-07-27 from the exact
`../../1JK08A-20260726-stock.bin`.

## Contents

- `1JK08A-20260727-immo-off.bin` - derived flash ROM, 1,048,576 bytes
  (`0x100000`);
- `1JK08A-20260727-immo-off.bin.md5` - MD5 sidecar.

ROM hashes:

- SHA-256: `de7f99cfb592d1cd1d83706f08cbea99ad0aef8602090d009cb37e9d37080d8c`;
- MD5: `1ae5f50b6f8697b168285b92ade28b7b`.

## Change

```text
ROM[0x00008725]: 0x01 -> 0x00
```

Only bit 0 of the factory Developer Immobilizer flag changes. The derived image
differs from stock by exactly one bit. Stored checksum fields match stock; the
flasher corrects the checksums while writing.

Reproduce the patch with:

```bash
python3 patches/apply_immo_off.py --rom JK08A
```

The execution path was confirmed in code and by a hardware test on 2026-07-27.
The image was written to the replacement JK00D and tested in a V36 Skyline 250GT
with a VQ25HR engine: the engine starts and runs normally. The ECM stores DTC
P1610; it reappears after clearing but does not affect engine starting or
operation.
