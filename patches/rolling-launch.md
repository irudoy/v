# JK08A Rolling Launch

## Status

Rolling Launch is an exact-JK08A extension of the complete five-slot
map-switching runtime. It implements a rolling RPM hold with an optional
retard-only ignition command. It does not implement turbo anti-lag, fuel
enrichment, spark cut, or throttle intervention.

The tracked in-memory fixture remains valid and fail-closed: its map enable
mask is zero and its composer never writes a ROM. A separate strict patcher
produces one locked hardware-test profile. That profile enables mode 1 only for
Map 1, requires a nonzero accelerator-pedal signal, leaves ignition retard
disabled, contains no brake gate, recalculates all six checksum references,
and refuses any input other than the exact corrected complete twelve-family
map-switching stage-20 endpoint.

The brake-status read and brake gate are absent from the current executable.
This runtime revision has software status `PASS` and hardware status `UNTESTED`;
the earlier vehicle results below remain evidence for their exact historical
images and do not validate the changed instruction bytes.

The vehicle-tested custom Overlay 20 passes application startup and PCMFlash
identification and activates RPM hold once, but it cannot rearm after CANCEL is
released. Map switching in the same image does not arm. CAN frame `0x239`, byte
4 counted from one, reports `0x20` with all buttons released, while both
runtimes treated `0x00` as released. The current implementation uses `0x20` for
release and rearm and treats `0x00` as invalid.

Corrected Overlay 21 passes the target-vehicle selector and repeated Map 1 RPM
Hold checks. Overlay 22 confirms that the primary ignition adapter can publish
the configured `-5 deg` diagnostic target, but its unconditional ACTIVE-phase
retard causes an immediate torque collapse and has hardware status
`FUNCTIONAL_FAIL`. Both custom profiles retain `enable_mask=0x01`; Rolling
Launch rejection on Maps 2 through 5 is the configured `MAP_DISABLED` result.
The converted MLG files and evidence table remain local scratch evidence and
are not tracked build inputs.

A separate 2026-08-06 vehicle test confirms that late values in idle-ignition
tables `0x12196` and `0x1219E` produce lift-off exhaust events without holding
the accelerator. This establishes a useful retard calibration reference, not a
Rolling Launch control rule: those tables run under different stock state and
load conditions. A future Rolling Launch retard phase must remain stock below
the hold band and may apply a late command only during a fuel-present recovery
phase near an actual limiter transition.

The common `defs/JK08A.xml` and `defs/JK08A.xdf` expose minimum coolant
temperature, minimum vehicle speed, minimum engine speed, RPM offset, and RPM
hysteresis as calibration tables. A native switch at `0xD3F6C` enables or
disables the accelerator-pedal requirement by writing `min_pedal=1` or
`min_pedal=0`. RomRaider also exposes one native `BitwiseSwitch` at
configuration byte `0xD3F64`, with one checkbox for each of Maps 1 through 5.
TunerPro represents the same byte as five `XDFFLAG` items. Every per-map control
edits one bit of `enable_mask` and preserves the other bits. The raw aggregate
mask and raw pedal threshold are not exposed as tables.

The implementation is bound to:

- exact stock JK08A SHA-256
  `ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23`;
- complete map-switching in-memory endpoint SHA-256
  `b8174722d155ba18937307e103a629ffe10540cb142d7a2c4c433f466d5bff56`;
- default Rolling Launch in-memory endpoint SHA-256
  `55eb17589b0195c2b61c0440c47fdcde66419825d51e11d54fbf7db5dc333e6c`;
- corrected checksum-valid map-switching stage-20 source SHA-256
  `8c604b3c6760fdea02a76f724b3daa09e7a799eab4204e0cec991f45d51e8a2d`;
- corrected Map 1 RPM Hold candidate SHA-256
  `01555a7bdd21306881e177d4407bed1f2123d730cac5d7857554ec189bb5db3d`;
- historical brake-gated Map 1 RPM Hold candidate SHA-256
  `c19207c4ad4c7494be6119db423a2eb927e2fe2f14695dc1dd2ff7309ce9d345`;
- historical checksum-valid map-switching stage-19 source SHA-256
  `e2fb90d5d9f2ba23c09cb55ee77732175ae0753aabe77f8e7363a84554218ea1`;
- historical Map 1 RPM Hold candidate SHA-256
  `a1b4c674e77adeb629d330a8ffd264dde4484d20946248a36ec5c7f3f9f4d081`;
- vehicle-tested custom Overlay 20 SHA-256
  `0b07f7b7dc49eaaf27bc26c859befcdf13d817b924cf0bc41748ccb47cfcc796`;
- corrected custom Overlay 21 SHA-256
  `1e6866e96e77fba203166b38f5efcfd83b6bcad609b7e0ada67727cd5fddc0c9`;
- Map 1 retard-only Overlay 22 SHA-256
  `21f532b924e24deede30c07bbf7d253bf4c908355bca44c7c863fee592aa2a84`.

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
  +-------------- code 0x20 for rearm_ticks ---------------+
```

`0x20` is the released/all-buttons-off code. `0x00` is fail-closed: it cannot
activate Rolling Launch and does not advance the cooldown rearm counter.

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
10. accelerator pedal meets its minimum; `min_pedal=0` makes this condition
    unconditional;
11. coolant lies inside the inclusive window;
12. timeout configuration is valid.

`SET` remains reserved for map switching. While Rolling Launch is `ACTIVE` or
`COOLDOWN`, the selector arbiter bypasses the map selector and tail-calls the
displaced stock ASCD host. An `ACTIVE` transition to `SET` aborts with
`MAP_REQUEST`; release code `0x20` aborts with `BUTTON_RELEASED`.

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
records stock and effective command bytes, then reads exact APC mode snapshot
`0xFFFF24C9`. Bit 6 selects a crank/cam position-diagnostic fallback path in
both stock compare schedulers, so a set bit immediately tail-calls the stock
consumer with the unchanged command. A clear bit permits validation of active
mode, map enable, configuration integrity markers, and the per-map target
range, followed by:

```text
effective_command = max(stock_command, target_command)
```

The accepted target range is `110..117`. The adapter cannot advance the command
below the stock value. It writes the effective byte to `0xFFFF2022` and
tail-calls the displaced stock consumer at `0x2A892`. Other bits, including
bit 5, do not activate the fail-closed gate. Physical spark angle, output-driver
polarity, and safe combustion behavior require timing-light and bench
correlation before enablement.

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
| `0x05` | 1 | reserved options | zero |
| `0x06` | 1 | coolant minimum | `<=` maximum |
| `0x07` | 1 | coolant maximum | `>=` minimum |
| `0x08` | 1 | minimum speed | nonzero |
| `0x09` | 1 | padding | zero |
| `0x0A` | 2 | minimum native RPM | nonzero |
| `0x0C` | 2 | minimum pedal | `0..0xFFFF`; zero disables the requirement |
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
`300` ticks, rearm `100` ticks, and target command `115` for every map. Its
minimum coolant value is raw `0` (`-40 deg C`), minimum speed is raw `1`
(`2 km/h [cand]`), and `min_pedal=1` enables the pedal requirement.

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

These DIDs document the internal runtime state and remain covered by static and
executable tests. The current PCMFlash/CONSULT logging workflow has no client
path for requesting them, so they are not required by the hardware acceptance
procedure. Vehicle testing uses available CONSULT parameters, CAN capture, and
direct behavior.

The abort reason values are `0` none, `1` invalid configuration, `2` invalid
map index, `3` disabled map, `4` selector busy, `5` feedback busy, `6` ASCD
active, `7` button released, `8` invalid button, `9` speed low, `10` RPM low,
`11` pedal low, `12` coolant outside, `13` reserved, `14` timeout, `15`
map request, `16` corrupt state, `17` map changed, and `18` mode changed.

## Artifacts and verification

- `rolling_launch.py` is the independent host reference model.
- `rolling-launch-layout.toml` owns addresses, hooks, RAM, DIDs, and SHA locks.
- `rolling-launch-payloads.toml` stores the complete Ghidra assembly spans.
- `rolling_launch_layout.py`, `rolling_launch_assembly.py`, and
  `rolling_launch_compose.py` validate and compose the fail-closed fixture only
  in memory.
- `apply_rolling_launch.py` accepts only the corrected locked stage-20 source,
  applies the Map 1 RPM Hold profile through the same closed write set,
  recalculates every checksum domain, and creates a non-overwriting ROM plus
  MD5 sidecar.
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
byte and control-flow address, and executes 98 Rolling Launch cases in addition
to the existing map-switching gate.

## Hardware-test images

The corrected generic feedback engine changes the rejected byte-5 low-bit
command to mask `0x60`, on value `0x60`, and off value `0x00`. Its GNU SH-2E
and Ghidra p-code executable gates pass. Target-vehicle testing confirms the
correct one-through-five meter pulse count. The hardware-tested 10/10-frame
timing is visually too fast; the current stage-20 endpoint uses 15/15 frames
and retains a hardware gate for the revised duration. Concrete calibration
profiles, generated ROMs, checksum sidecars, and logs remain local artifacts
outside the repository.

Historical stage-19 and Overlay 20 candidates contain the superseded `0x00`
release assumption. The Overlay 20 runtime has hardware status
`FUNCTIONAL_FAIL`: startup and identification pass, the first Rolling Launch
activation works, and the state cannot rearm after CANCEL release. Derived
artifacts are not retained under `rom-images/`.

The historical corrected full-ROM upgrade is identified as:

```text
1JK08A-multimap-1-3-overlay-21-button-release-fix.bin
SHA-256 1e6866e96e77fba203166b38f5efcfd83b6bcad609b7e0ada67727cd5fddc0c9
MD5    cdfbcd5a528fbf785f0e88648506968a
```

It is derived only from exact Overlay 20 SHA-256
`0b07f7b7dc49eaaf27bc26c859befcdf13d817b924cf0bc41748ccb47cfcc796`.
Five executable bytes change: two selector compare immediates, one Rolling
Launch release immediate, and the two-byte cooldown comparison instruction.
The approved calibration changes 114 bytes: 40 cells in the global cold
ignition-trim table and 74 bytes in Map 1 and Map 3 DFCO families. Twelve
checksum bytes also change, for 131 changed bytes total. The 32-byte Rolling
Launch configuration remains identical. All six stored checksum references
are valid. Its calibration provenance remains in the local hardware record;
the historical generated image is not a build input.

The calibration revision changes no executable byte beyond the five existing
button-release corrections, so it does not require a new instruction gate.

The Map 1-only ignition-retard hardware candidate is:

```text
1JK08A-multimap-1-3-overlay-22-rpm-hold-retard.bin
SHA-256 21f532b924e24deede30c07bbf7d253bf4c908355bca44c7c863fee592aa2a84
MD5    0fb23c4801250651c95c1c826868b334
```

It is derived only from exact Overlay 21 and changes the configuration mode
at `0xD3F63` from `RPM_HOLD` (`1`) to `RPM_HOLD_RETARD` (`2`). Four stored
checksum bytes also change, for five changed bytes total. The executable code,
vehicle calibration, Map 1-only enable mask, `200 RPM` offset, `100 RPM`
hysteresis, and per-map ignition target command `115` remain identical. All six
stored checksum references are valid. Its calibration provenance is locked by
the local hardware record; the historical generated image is not a build input.

Hardware status is `FUNCTIONAL_FAIL`. CONSULT logs contain the exact `-5 deg`
target during five separate Map 1 CANCEL intervals and normal `14..43 deg`
timing during Map 2 and Map 3 attempts. The immediate retard removes engine
torque before the engine can establish a stable temporary limiter cycle. Base
injection remains positive in every sampled CANCEL interval. Physical spark
angle remains subject to timing-light verification, but the command polarity
and runtime adapter activation are established by the diagnostic trace.

The calibration-independent corrected regression chain is generated by the
tracked patch tools with prefix `1JK08A-map-switching-safe-v5`. Its stage-20
map-switching endpoint has SHA-256
`8c604b3c6760fdea02a76f724b3daa09e7a799eab4204e0cec991f45d51e8a2d`.
Applying the locked generic Map 1 RPM Hold profile produces SHA-256
`01555a7bdd21306881e177d4407bed1f2123d730cac5d7857554ec189bb5db3d`
and MD5 `957414243a7c50ba430657ec028863cb`. This regression image does not contain
the custom calibration of Overlay 21.

The target-vehicle result is:

1. Overlay 21 and Overlay 22 pass PCMFlash identification and application
   startup.
2. Map selection reaches Maps 2 and 3 through the corrected
   `SET -> CANCEL -> SET` sequence.
3. Map 1 RPM Hold rearms and activates repeatedly after release code `0x20`.
4. Maps 2 through 5 reject Rolling Launch because the hardware-test profile is
   intentionally Map 1-only.
5. Overlay 21 is the safe `RPM_HOLD` baseline without retard. The common defs
   provide minimum coolant temperature, minimum vehicle speed, minimum engine
   speed, RPM offset, RPM hysteresis, the pedal-requirement switch, and five
   independent per-map enable controls. Hardware acceptance uses only
   parameters available in the current logger.
6. A complete Rolling Launch implementation requires an RPM-conditioned
   ignition controller. Retard must remain stock below the hold band, enter
   only near an actual limiter event, and restore torque through explicit
   hysteresis or staged commands. The controller requires separate engine
   validation before any exhaust-combustion objective is evaluated. Overlay 22
   is not a further dynamic-test candidate.
7. The one-through-five CRUISE indication encoding and count pass in the
   integrated vehicle image. The next local no-retard candidate verifies the
   revised 15/15-frame duration, then repeats the established Map 1 RPM Hold
   and Map 2/Map 3 selection checks.

The remaining gesture risk is the decoded code sequence produced when CANCEL
is pressed while SET remains held. A CAN capture of that combined gesture must
show a usable `SET -> CANCEL -> SET` transition before the selector result is
treated as functionally closed.
