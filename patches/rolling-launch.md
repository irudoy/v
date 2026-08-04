# JK08A Rolling Launch

## Status

Rolling Launch is an exact-JK08A extension of the complete five-slot
map-switching runtime. It implements a rolling RPM hold with an optional
retard-only ignition command. It does not implement turbo anti-lag, fuel
enrichment, spark cut, or throttle intervention.

The tracked in-memory fixture remains valid and fail-closed: its map enable
mask is zero and its composer never writes a ROM. A separate strict patcher
produces one locked hardware-test profile. That profile enables mode 1 only for
Map 1, leaves ignition retard and the unverified brake gate disabled,
recalculates all six checksum references, and refuses any input other than the
exact complete ten-family map-switching stage-19 endpoint.

The resulting complete ROM is software-verified and eligible for the staged
bench and engine test sequence below. It is not hardware-validated and is not a
road-test image. Map-switching stages 15 through 19 remain mandatory isolation
gates before Rolling RPM Hold activation.

The implementation is bound to:

- exact stock JK08A SHA-256
  `ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23`;
- complete map-switching in-memory endpoint SHA-256
  `ee274610baedd42a46f555589fbc10206d66cc912662cef8eebef219a353b6cd`;
- default Rolling Launch in-memory endpoint SHA-256
  `7d4a642c1b19d5dc7267c388750997cf53aeb2bcaee65e4bdd68ed4f3512e2af`;
- exact checksum-valid map-switching stage-19 source SHA-256
  `e2fb90d5d9f2ba23c09cb55ee77732175ae0753aabe77f8e7363a84554218ea1`;
- Map 1 RPM Hold hardware-test ROM SHA-256
  `f6ab51aeb005b49333656090df2287b7834596f473eb37a869436f5c63eadbf4`.

## Runtime contract

The exact periodic scheduler table entry at `0x21970` runs the displaced stock
task at `0xA9554` and then advances Rolling Launch once. One runtime tick is one
periodic scheduler pass:

```text
tick_seconds = 204800 / Pphi
```

The current `Pphi = 20 MHz` candidate gives `10.24 ms` per tick. Timeout and
rearm calibration values are stored as tick counts. Hardware timing must be
confirmed before those values are treated as physical durations.

The state machine is:

```text
IDLE --all gates pass--> ACTIVE --abort/release/timeout--> COOLDOWN
  ^                                                        |
  +---------------- released for rearm_ticks --------------+
```

Any phase value outside `0..2`, invalid snapshot, or impossible timer state
uses corrupt-state recovery. Recovery restores Map 1 through the existing
SR-protected limiter commit, clears all 20 Rolling Launch state bytes, and
enters `COOLDOWN` with reason `STATE_CORRUPT`.

### Activation gates

All gates are evaluated on every `IDLE` and `ACTIVE` tick. Flags report every
satisfied condition while the abort reason retains the first failure by fixed
priority:

1. configuration integrity and ranges;
2. active map index in `0..4`;
3. active map enabled by the configuration mask;
4. map selector phase, selection count, and elapsed count are zero;
5. map feedback pulse, phase, tick, and reserved bytes are zero;
6. ASCD is inactive;
7. stable cruise button code is `CANCEL` (`0x02`);
8. vehicle speed meets its minimum;
9. native RPM meets its minimum;
10. accelerator pedal meets its minimum;
11. coolant lies inside the inclusive window;
12. optional brake candidate gate passes;
13. timeout configuration is valid.

`SET` remains reserved for map switching. While Rolling Launch is `ACTIVE` or
`COOLDOWN`, the selector arbiter bypasses the map selector and tail-calls the
displaced stock ASCD host. An `ACTIVE` transition to `SET` aborts with
`MAP_REQUEST`; release aborts with `BUTTON_RELEASED`.

### Modes

| Value | Mode | Fuel threshold write | Ignition command write |
| ---: | --- | --- | --- |
| 0 | `OBSERVE` | none | none |
| 1 | `RPM_HOLD` | temporary Cut/Restore overlay | none |
| 2 | `RPM_HOLD_RETARD` | temporary Cut/Restore overlay | retard-only maximum |

On activation, the engine captures native `uint16` RPM at `0xFFFF11BC`:

```text
Cut = saturate_u16(captured_rpm + rpm_offset)
Restore = Cut - hysteresis
```

Static scaling is `12.5 RPM` per native unit. The overlay writes exactly the
first eight bytes of the existing fuel limiter shadow at `0xFFFF5D10`:

```text
Cut, Cut, Restore, Restore
```

The final four bytes remain unchanged. SR interrupt masking protects all four
word stores. Abort from modes 1 or 2 invokes the existing limiter commit at
`0xD3660` with the captured map index, restoring the complete map-specific
shadow. Mode 0 performs no limiter write.

The ignition adapter replaces the primary consumer literal at `0x4E198`. It
records stock and effective command bytes, validates active mode, map enable,
configuration integrity markers, and the per-map target range, then applies:

```text
effective_command = max(stock_command, target_command)
```

The accepted target range is `110..117`. The adapter cannot advance the command
below the stock value. It writes the effective byte to `0xFFFF2022` and
tail-calls the displaced stock consumer at `0x2A892`. Physical ignition meaning
and safe targets require CONSULT3P or bench correlation before enablement.

## Allocation and hooks

| Purpose | Range or address |
| --- | --- |
| Periodic, selector, startup wrappers | `0xD3860..0xD38E4` |
| State engine and helpers | `0xD38E4..0xD3EA0` |
| Ignition adapter | `0xD3EA0..0xD3F60` |
| Configuration record | `0xD3F60..0xD3F80` |
| Dedicated state RAM | `0xFFFF5D40..0xFFFF5D54` |
| Shared fuel shadow | `0xFFFF5D10..0xFFFF5D1C` |
| Periodic table hook | `0x21970`: `0xA9554` -> `0xD3860` |
| Selector call hook | `0xCE8DC`: `0xD2108` -> `0xD3880` |
| Startup hook | `0x27D28`: `0xD22A0` -> `0xD38A0` |
| Ignition command hook | `0x4E198`: `0x2A892` -> `0xD3EA0` |

The ROM allocation is inside the Ghidra-audited erased region ending at
`0xE1C2A`. The state allocation is disjoint from map-switching RAM
`0xFFFF5D00..0xFFFF5D3C` and inside the wider no-xref RAM interval ending at
`0xFFFF7000`.

## Configuration record

All multi-byte values are big-endian.

| Offset | Size | Field | Validation |
| ---: | ---: | --- | --- |
| `0x00` | 2 | magic | `0x524C` |
| `0x02` | 1 | schema | `1` |
| `0x03` | 1 | mode | `0..2` |
| `0x04` | 1 | map enable mask | bits `0..4` only |
| `0x05` | 1 | options | bit 0 is the brake candidate gate |
| `0x06` | 1 | coolant minimum | `<=` maximum |
| `0x07` | 1 | coolant maximum | `>=` minimum |
| `0x08` | 1 | minimum speed | nonzero |
| `0x09` | 1 | padding | zero |
| `0x0A` | 2 | minimum native RPM | nonzero |
| `0x0C` | 2 | minimum pedal | nonzero |
| `0x0E` | 2 | native RPM offset | nonzero |
| `0x10` | 2 | native hysteresis | `0 < value < minimum RPM` |
| `0x12` | 2 | run timeout ticks | `1..0x7FFF` |
| `0x14` | 2 | rearm ticks | `1..0x7FFF` |
| `0x16` | 5 | per-map ignition targets | each `110..117` |
| `0x1B` | 1 | reserved | zero |
| `0x1C` | 2 | inverse magic | `0xADB3` |
| `0x1E` | 2 | end marker | `0xA55A` |

The tracked default is:

```text
524c0100000000ff010000a0000100100008012c0064737373737300adb3a55a
```

It selects `OBSERVE`, enables no map, uses native minimum RPM `160`
(`2000 RPM`), offset `16` (`200 RPM`), hysteresis `8` (`100 RPM`), timeout
`300` ticks, rearm `100` ticks, and target command `115` for every map.

The locked hardware-test profile is:

```text
524c0101010000ff010000a0000100100008012c0064737373737300adb3a55a
```

It changes only mode to `RPM_HOLD` and the enable mask to Map 1. With the
candidate 10.24 ms scheduler tick, 300 timeout counts and 100 rearm counts are
approximately 3.072 s and 1.024 s. These physical durations remain candidates
until the scheduler period is measured on hardware; the count limits remain
bounded independently of that conversion.

## State and diagnostics

| State offset | Type | Meaning |
| ---: | --- | --- |
| `0x00` | `uint8` | phase |
| `0x01` | `uint8` | abort reason |
| `0x02` | `uint16` | gate and output flags |
| `0x04` | `uint8` | active map snapshot |
| `0x05` | `uint8` | active mode snapshot |
| `0x06` | `uint16` | run ticks |
| `0x08` | `uint16` | rearm ticks |
| `0x0A` | `uint16` | captured native RPM |
| `0x0C` | `uint16` | temporary Cut threshold |
| `0x0E` | `uint16` | temporary Restore threshold |
| `0x10` | `uint8` | stock ignition command |
| `0x11` | `uint8` | effective ignition command |
| `0x12` | `uint16` | reserved, zero after startup/recovery |

Unused entries in the exact high-`0x12` UDS DID table expose nine live pairs:

| DID | State pair |
| ---: | --- |
| `0x1211` | phase and abort reason |
| `0x1212` | flags |
| `0x1213` | map and mode snapshots |
| `0x1216` | run ticks |
| `0x1217` | rearm ticks |
| `0x1224` | captured native RPM |
| `0x1227` | Cut threshold |
| `0x1228` | Restore threshold |
| `0x1229` | stock and effective ignition commands |

The abort reason values are `0` none, `1` invalid configuration, `2` invalid
map index, `3` disabled map, `4` selector busy, `5` feedback busy, `6` ASCD
active, `7` button released, `8` invalid button, `9` speed low, `10` RPM low,
`11` pedal low, `12` coolant outside, `13` brake active, `14` timeout, `15`
map request, `16` corrupt state, `17` map changed, and `18` mode changed.

## Artifacts and verification

- `rolling_launch.py` is the independent host reference model.
- `rolling-launch-layout.toml` owns addresses, hooks, RAM, DIDs, and SHA locks.
- `rolling-launch-payloads.toml` stores the complete Ghidra assembly spans.
- `rolling_launch_layout.py`, `rolling_launch_assembly.py`, and
  `rolling_launch_compose.py` validate and compose the fail-closed fixture only
  in memory.
- `apply_rolling_launch.py` accepts only the locked stage-19 source, applies the
  Map 1 RPM Hold profile through the same closed write set, recalculates every
  checksum domain, and creates a non-overwriting ROM plus MD5 sidecar.
- `rolling-launch-wrappers.s`, `rolling-launch-engine.s`, and
  `rolling-launch-ignition-adapter.s` are the SH-2E implementation.
- `tools/sh-elf-run/verify_rolling_launch.py` and
  `rolling_launch_harness.c` provide independent GNU assembly and executable
  behavior checks.

Host checks:

```bash
python3 patches/rolling_launch_assembly.py
python3 patches/rolling_launch_compose.py
python3 -m unittest \
  patches.tests.test_apply_rolling_launch \
  patches.tests.test_rolling_launch \
  patches.tests.test_rolling_launch_composition \
  patches.tests.test_sh_elf_run_verifier -v
```

The mandatory instruction gate is the repository-wide command:

```bash
tools/sh-elf-run/run.sh --verbose
```

It independently assembles the exact source with GNU `sh-elf-as --isa=sh2e`,
requires byte identity with all Ghidra payloads, relocates only validated
high-RAM `.long` literals for the simulator, preserves every new instruction
byte and control-flow address, and executes 94 Rolling Launch cases in addition
to the existing map-switching gate.

## Hardware-test image

The tracked candidate is:

```text
rom-images/23710-JK08A/mods/rolling-launch/
  1JK08A-20260804-map-switching-rolling-launch-rpm-hold-map1-test.bin
```

It is derived from the exact checksum-valid stage-19 endpoint and differs from
that source at 1,695 byte positions. Every change is inside the 1,876-byte
Rolling Launch composition write set or the 20 checksum-byte set; 18 checksum
bytes change. The final image contains 751 locked Rolling Launch instructions,
five entries, nine diagnostics, and valid stored checksum references.

Reproduce and verify it with:

```bash
python3 patches/apply_rolling_launch.py \
  tmp/hardware-full-dfco/\
1JK08A-map-switching-safe-v3-19-can-feedback-full-runtime.bin \
  --output rom-images/23710-JK08A/mods/rolling-launch/\
1JK08A-20260804-map-switching-rolling-launch-rpm-hold-map1-test.bin
tools/sh-elf-run/run.sh --verbose
```

The hardware sequence is cumulative:

1. Write and validate stage 15 with inactive full-DFCO code and storage.
2. Write and validate stages 16 and 17, activating the two shared DFCO hooks
   independently.
3. Write and validate selector stage 18 without any selection gesture.
4. Write and validate stage 19, including Map 1-5 selection and feedback.
5. Write the Rolling RPM Hold candidate to the same known-good recoverable ECU.
6. Confirm identification, reset to Map 1, all nine engineering DIDs, and
   inactive pass-through behavior before enabling engine output.
7. Perform the first active test on a dynamometer with a warmed engine, a fixed
   transmission gear, independent RPM observation, and immediate button-release
   abort. Road activation is not the first dynamic test.

Unexpected CAN loss, selector state, limiter shadow, DTC, fuel cut, RPM rise,
or failure to return to `COOLDOWN` and then `IDLE` terminates the test. Ignition
retard remains disabled until the physical APC command polarity and safe range
are established separately.
