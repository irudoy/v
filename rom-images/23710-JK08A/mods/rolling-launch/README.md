# 1JK08A Rolling RPM Hold hardware-test image

This directory contains the software-verified JK08A Rolling RPM Hold candidate
for staged bench and engine validation. It is not hardware-validated and is not
a road-test image.

## Contents

- `1JK08A-20260804-map-switching-rolling-launch-rpm-hold-map1-test.bin` -
  complete flash ROM, 1,048,576 bytes (`0x100000`);
- `1JK08A-20260804-map-switching-rolling-launch-rpm-hold-map1-test.bin.md5` -
  MD5 sidecar.

ROM hashes:

- SHA-256: `f6ab51aeb005b49333656090df2287b7834596f473eb37a869436f5c63eadbf4`;
- MD5: `705b67c5d7c57bc3baba3c0b2c762dd2`.

## Provenance

The exact input is the complete checksum-valid ten-family map-switching
stage-19 endpoint
with SHA-256
`e2fb90d5d9f2ba23c09cb55ee77732175ae0753aabe77f8e7363a84554218ea1`.
That endpoint is built from the exact successful lookup Overlay 14 readback
with SHA-256
`f0a03f6fef205aa1ac42e4471dd0bad995a7082c35d24bdb639fc342ccdda892`
through the locked full-DFCO, selector, and feedback stages 15 through 19.

The input includes the existing `immo-e2-pops-fuel-throttle-ofc-v2`
calibration and configuration. The Rolling Launch patch preserves every input
byte outside its declared write set and checksum fields.

## Profile

```text
mode                  = 1 (RPM_HOLD)
enable_mask           = 0x01 (Map 1 only)
brake_gate            = disabled
ignition_retard       = disabled
minimum_native_rpm    = 160 (2000 RPM)
rpm_offset_native     = 16 (200 RPM)
hysteresis_native     = 8 (100 RPM)
run_timeout_ticks     = 300
rearm_ticks           = 100
configuration_hex     = 524c0101010000ff010000a0000100100008012c0064737373737300adb3a55a
```

The current 10.24 ms tick is based on the `Pphi=20 MHz` board candidate, so the
physical timeout and rearm estimates are 3.072 s and 1.024 s. The bounded tick
counts are exact; the conversion to physical time requires hardware
measurement.

## Verification

- all six stored checksum references match independent recalculation;
- 1,695 bytes differ from stage 19, all inside the 1,876-byte Rolling Launch
  write set or the 20 checksum bytes;
- 18 checksum bytes change;
- 751 Rolling Launch instructions, five code entries, and nine diagnostic DIDs
  match the SHA-locked Ghidra payload;
- independent GNU `sh-elf-as --isa=sh2e` output is byte-identical;
- GNU simulator 16.3 passes 116 map-switching and 94 Rolling Launch cases.

Reproduce the final image with `patches/apply_rolling_launch.py`. The full
runtime contract and mandatory staged hardware procedure are in
`patches/rolling-launch.md`.
