# 1JK08A Rolling RPM Hold superseded hardware-test image

This directory contains the original JK08A Rolling RPM Hold candidate. Its
runtime treats steering-switch code `0x00` as released. Target-vehicle CAN
frame `0x239`, byte 4, reports `0x20` with all buttons released. A vehicle test
of the byte-identical runtime in the custom Overlay 20 passes startup and first
activation but cannot rearm. This image is retained for provenance and is not a
hardware-test or road-test candidate.

## Contents

- `1JK08A-20260804-map-switching-rolling-launch-rpm-hold-map1-test.bin` -
  complete flash ROM, 1,048,576 bytes (`0x100000`);
- `1JK08A-20260804-map-switching-rolling-launch-rpm-hold-map1-test.bin.md5` -
  MD5 sidecar.

ROM hashes:

- SHA-256: `a1b4c674e77adeb629d330a8ffd264dde4484d20946248a36ec5c7f3f9f4d081`;
- MD5: `544288a26f96459d4fba24efa7dd661a`.

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

The installed ignition adapter checks `0xFFFF24C9.bit6` before all mode and
target validation. A set bit preserves the stock command for the crank/cam
position-diagnostic APC fallback path. Retard remains disabled in this profile.

The current 10.24 ms tick is based on the `Pphi=20 MHz` board candidate, so the
physical timeout and rearm estimates are 3.072 s and 1.024 s. The bounded tick
counts are exact; the conversion to physical time requires hardware
measurement.

## Verification

- all six stored checksum references match independent recalculation;
- 1,705 bytes differ from stage 19, all inside the 1,876-byte Rolling Launch
  write set or the 20 checksum bytes;
- 18 checksum bytes change;
- 755 Rolling Launch instructions, five code entries, and nine diagnostic DIDs
  match the SHA-locked Ghidra payload;
- independent GNU `sh-elf-as --isa=sh2e` output is byte-identical;
- the original GNU simulator gate passed 116 map-switching and 96 Rolling
  Launch cases but did not exercise the target-vehicle `0x20` release code.

The corrected runtime gate passes 116 map-switching and 98 Rolling Launch
cases. The checksum-valid Overlay 20 upgrade is
`tmp/1JK08A-multimap-1-3-overlay-21-button-release-fix.bin`, documented in
`patches/rolling-launch.md`. Target-vehicle testing confirms repeated Map 1
RPM Hold activation after `0x20` release. Overlay 22 changes only the mode to
`RPM_HOLD_RETARD`; CONSULT logs confirm its configured `-5 deg` command and
also show an immediate torque collapse. Overlay 22 is not a further dynamic
test candidate.

The common `defs/JK08A.xml` and `defs/JK08A.xdf` expose five independent
per-map Rolling Launch enable controls at configuration byte `0xD3F64`. Each
masked control preserves the other four map bits. The custom diagnostic DIDs
remain internal verification points; the current vehicle logger cannot request
them and the hardware procedure does not depend on them.

The current strict patcher accepts corrected map-switching stage-19 SHA-256
`52568ec1006df01c2524afe505a4ed9c8b00aa15bf5ea2a946d74107bbd97b84`
and produces corrected generic Map 1 RPM Hold SHA-256
`6e74ae82d22e9d975c64e2002c8ad30dec0f33f8f72b5ecd9906aab7598d480b`.
Those hashes are separate from this retained historical artifact.
