# Unified ROM builder

`build_rom.py` is the production entry point for constructing a complete ROM.
It installs every current firmware runtime registered for the selected series,
recalculates all checksum domains, verifies the final closed write set, and
creates one ROM with digest sidecars and a machine-readable manifest.

The registered `sh7058_7mfkavn86` exact-code series contains JK00A, JK03A,
JK03B, and JK08A. JK08A is the canonical address and executable-code profile;
each member retains its own stock identity and calibration. The command has two
selection modes:

```bash
uv run python patches/build_rom.py INPUT.bin --output OUTPUT.bin
uv run python patches/build_rom.py INPUT.bin --rom JK08A --output OUTPUT.bin
uv run python patches/build_rom.py INPUT.bin --rom JK00A --output OUTPUT.bin
```

The default `--rom auto` mode identifies the exact member from the one-MiB image
size and immutable identity bytes at `0x8204..0x8219`. It does not inspect the
file name. An explicit selector bypasses selection ambiguity but does not
bypass image validation. Both modes require the selected stock identity, valid
input checksums, stock anchors, an exact vector/code prefix at
`0x000000..0x0081ff`, and an exact protected partition at
`0x020000..0x0fffff`.

Every invocation validates `rom-images/roms.csv` and
`rom-images/homology.toml`. The four registered stock images must match their
SHA-256 identities and the declared exact-code ranges before any composition
is accepted.

Use `--verify-only` to run the complete in-memory composition and verification
without creating files:

```bash
uv run python patches/build_rom.py INPUT.bin --verify-only
```

## Exact-family pipeline

The common handler performs these operations in one invocation:

1. Validate image size, immutable identity, and all six stored checksum values.
2. Validate the shared active-RAM and future ROM/RAM reservation ledger.
3. Classify the image as a compatible unpatched base or a complete runtime that
   can be migrated. The CAN telemetry layer must be wholly absent or match the
   exact current payload, configuration, mailbox record, hooks, and erased
   future reserve. After removing a validated telemetry layer in memory, the
   Rolling Launch layer must be wholly absent, match the exact current payload
   and configuration schema, or match one registered historical unit
   fingerprint and its schema contract. Mixed hooks or DIDs, unknown payload
   bytes, partial pointer tables, invalid configuration records, occupied
   reserves, and unknown protected-code changes are rejected.
4. Normalize only the combined builder-owned Map Switching, Rolling Launch,
   CAN telemetry, and checksum ranges back to bytes from the selected stock
   member.
5. Apply the current Map Switching composition directly from
   `map-switching-payloads.toml`.
6. Restore every Map 2 through Map 5 calibration byte when the input already
   contains a complete runtime. An unpatched base initializes these slots from
   its Map 1 values.
7. Apply the current Rolling Launch composition directly from
   `rolling-launch-payloads.toml` and the selected local profile.
8. Apply the current CAN telemetry composition directly from
   `can-telemetry-payloads.toml`. The built-in profile installs the runtime in
   fail-closed disabled-at-startup mode, configures mailbox 26 as the idle
   telemetry transmitter, and configures mailbox 31 as the control receiver
   after each HCAN1 initialization.
9. Recalculate self-test B, self-test A, SUM16 A, and SUM16 B in dependency
   order, then verify all stored values again.
10. Require every final difference from the input to be inside the union of the
   three component write sets and the checksum fields.

The builder preserves calibration and configuration outside its declared
ranges, including the Developer Immobilizer bit edited through the matching
`defs/<ROM>.xml` or `defs/<ROM>.xdf`. Map 1 and every newly initialized Map 2
through Map 5 copy come from the selected input, never from JK08A. The builder
does not call an Immobilizer patcher. Historical image identities and hardware
outcomes are retained in `hardware-results.toml`; the production path imports
only the current composition modules.

## Rolling Launch profile

Without `--profile`, the builder uses the conservative built-in
`rpm-hold-map1-test` profile: Map 1 enabled, RPM Hold mode, and ignition retard
disabled. A separate local TOML file selects all Rolling Launch calibration,
including the bounded-retard mode:

```toml
schema_version = 2
rom = "sh7058_7mfkavn86"
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

[can_telemetry]
enabled = false
can_id = 0x6F0
profile = "tuning"
tick_divisor = 1
```

Run it with:

```bash
uv run python patches/build_rom.py INPUT.bin \
  --profile LOCAL-PROFILE.toml \
  --output OUTPUT.bin
```

The accepted mode names are `observe`, `rpm_hold`, and `rpm_hold_retard`.
`enabled_maps` uses one-based map numbers. Every field is mandatory, unknown
fields are rejected, and the resulting 32-byte configuration must pass the
independent fail-closed model. `rom` may name the complete
`sh7058_7mfkavn86` series or bind the profile to one exact member.
`min_speed = 0` disables the vehicle-speed activation gate, and
`min_pedal = 0` disables the pedal-position activation gate.
`hysteresis_ratio_tenths = 20` means 2.0 percent of captured RPM. The runtime
rounds that proportional value and clamps it between the configured native-RPM
minimum and maximum. The effective ignition-retard ramp is at least the
configured minimum, at least twice the effective hysteresis, and no wider than
the RPM offset.
Concrete profiles remain local and are not versioned.

## CAN telemetry profile

The optional `[can_telemetry]` table is strict: all four fields are required
when the table is present. Omitting it selects the same disabled default shown
above. `profile` is the schema-2 `tuning` profile; `can_id` is in
`0x001..0x7FE`; and `tick_divisor` is in `1..255` relative to the natural
`FUN_00020DFE` snapshot cadence. The adjacent standard ID is reserved for
runtime control.

Every profile changes mailbox-26 record `0x000097BE` from stock-inactive type 5
to interrupt-enabled transmit type 4 and encodes the selected data ID as
`STDID << 5`. `enabled` controls whether sampling starts after reset; an idle
type-4 mailbox does not request CAN traffic. A validated START command on
`can_id + 1` activates streaming until reset even when `enabled = false`, and
STOP forces it off. The builder validates the exact mailbox record against the
configuration and rejects a partial or mismatched endpoint.

A profile can start transmission automatically only after a passive
whole-vehicle capture proves both adjacent IDs unused and a measured bus-load
review selects the page profile and divisor. The generated XML/XDF switch at
`0x000D4E03` edits the same startup flag.

The generated runtime configuration is 16 bytes and binds enable state,
profile ID, page count, divisor, CAN ID, profile CRC16, and an integrity word.
The firmware validates these fields before sampling. The current active and
future allocations are listed in `runtime-reservations.md`.

## Output contract

One successful file build creates four non-overwriting artifacts:

- `OUTPUT.bin`;
- `OUTPUT.bin.sha256`;
- `OUTPUT.bin.md5`;
- `OUTPUT.bin.manifest.json`.

An existing byte-identical set is accepted as idempotent. A conflicting file
causes the invocation to fail before any missing artifact is created. The JSON
manifest binds the input, normalized stage, Map Switching stage, Rolling
Launch stage, both runtime configurations, CAN mailbox record, final output,
checksum values, write-set counts, and exact instruction audit counts. Manifest
schema 3 records both the series and exact member. Every new image is marked
`hardware_status=UNTESTED`; software verification does not make it eligible for
flashing without target-specific bench and vehicle gates.
