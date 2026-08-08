# Unified ROM builder

`build_rom.py` is the production entry point for constructing a complete ROM.
It installs every current firmware runtime registered for the selected series,
recalculates all checksum domains, verifies the final closed write set, and
creates one ROM with digest sidecars and a machine-readable manifest.

JK08A is the only registered series. The command has two selection modes:

```bash
uv run python patches/build_rom.py INPUT.bin --output OUTPUT.bin
uv run python patches/build_rom.py INPUT.bin --rom JK08A --output OUTPUT.bin
```

The default `--rom auto` mode identifies JK08A from the one-MiB image size and
the immutable identity bytes at `0x8204..0x8219`. It does not inspect the file
name. `--rom JK08A` bypasses selection ambiguity but does not bypass image
validation. Both modes require the exact JK08A identity, valid input checksums,
stock anchors, and no unknown protected-code changes.

Use `--verify-only` to run the complete in-memory composition and verification
without creating files:

```bash
uv run python patches/build_rom.py INPUT.bin --verify-only
```

## JK08A pipeline

The JK08A handler performs these operations in one invocation:

1. Validate image size, immutable identity, and all six stored checksum values.
2. Classify the image as a compatible unpatched base or a complete runtime that
   can be migrated. The Rolling Launch layer must be wholly absent, match the
   exact current payload and configuration schema, or match one registered
   historical unit fingerprint and its schema contract. Mixed hooks or DIDs,
   unknown payload bytes, partial pointer tables, invalid configuration records,
   and unknown protected-code changes are rejected.
3. Normalize only the combined builder-owned map-switching, Rolling Launch, and
   checksum ranges back to exact stock bytes.
4. Apply the current map-switching composition directly from
   `map-switching-payloads.toml`.
5. Restore every Map 2 through Map 5 calibration byte when the input already
   contains a complete runtime. An unpatched base initializes these slots from
   its Map 1 values.
6. Apply the current Rolling Launch composition directly from
   `rolling-launch-payloads.toml` and the selected local profile.
7. Recalculate self-test B, self-test A, SUM16 A, and SUM16 B in dependency
   order, then verify all stored values again.
8. Require every final difference from the input to be inside the union of the
   two component write sets and the checksum fields.

The builder preserves calibration and configuration outside its declared
ranges, including the Developer Immobilizer bit edited through `defs/JK08A.xml`
or `defs/JK08A.xdf`. It does not call an Immobilizer patcher. Historical image
identities and hardware outcomes are retained in `hardware-results.toml`; the
production path imports only the current composition modules.

## Rolling Launch profile

Without `--profile`, the builder uses the conservative built-in
`rpm-hold-map1-test` profile: Map 1 enabled, RPM Hold mode, and ignition retard
disabled. A separate local TOML file selects all Rolling Launch calibration,
including the bounded-retard mode:

```toml
schema_version = 2
rom = "JK08A"
name = "rpm-hold-retard-maps-1-3"

[rolling_launch]
mode = "rpm_hold_retard"
enabled_maps = [1, 3]
coolant_min = 10
coolant_max = 220
min_speed = 2
retard_ramp_native = 12
min_rpm_native = 160
min_pedal = 3
rpm_offset_native = 16
min_hysteresis_native = 4
max_hysteresis_native = 12
hysteresis_ratio_tenths = 20
run_timeout_ticks = 300
rearm_ticks = 100
target_commands = [115, 114, 113, 112, 111]
```

Run it with:

```bash
uv run python patches/build_rom.py INPUT.bin \
  --profile LOCAL-PROFILE.toml \
  --output OUTPUT.bin
```

The accepted mode names are `observe`, `rpm_hold`, and `rpm_hold_retard`.
`enabled_maps` uses one-based map numbers. Every field is mandatory, unknown
fields are rejected, the profile ROM must equal the selected ROM, and the
resulting 32-byte configuration must pass the independent fail-closed model.
`min_speed = 0` disables the vehicle-speed activation gate, and
`min_pedal = 0` disables the pedal-position activation gate.
`hysteresis_ratio_tenths = 20` means 2.0 percent of captured RPM. The runtime
rounds that proportional value and clamps it between the configured native-RPM
minimum and maximum. The effective ignition-retard ramp is at least the
configured minimum, at least twice the effective hysteresis, and no wider than
the RPM offset.
Concrete profiles remain local and are not versioned.

## Output contract

One successful file build creates four non-overwriting artifacts:

- `OUTPUT.bin`;
- `OUTPUT.bin.sha256`;
- `OUTPUT.bin.md5`;
- `OUTPUT.bin.manifest.json`.

An existing byte-identical set is accepted as idempotent. A conflicting file
causes the invocation to fail before any missing artifact is created. The JSON
manifest binds the input, normalized stage, map-switching stage, profile digest
and configuration, final output, checksum values, write-set counts, and exact
instruction audit counts. Every new image is marked `hardware_status=UNTESTED`;
software verification does not make it eligible for flashing without the
project hardware gates.
