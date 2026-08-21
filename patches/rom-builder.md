# Unified ROM builder

`build_rom.py` is the production entry point for constructing a complete ROM.
It installs every current firmware runtime registered for the selected series,
recalculates all checksum domains, verifies the final closed write set, and
creates one ROM with digest sidecars and a machine-readable manifest.

The registered `sh7058_7mfkavn86` exact-code series contains JK00A, JK03A,
JK03B, and JK08A. JK08A is its canonical address and executable-code profile.
The registered `sh7058_8mfk` near-code series contains JK00C and JK00D. It uses
exact target address profiles and independently assembled target payloads.
The registered `sh7059_1nd` exact-code series contains 1ND0A and 1ND3B. It uses
a shared SH7059 address profile, independently assembled target payloads, Map
Switching, and custom CAN telemetry. Rolling Launch is not supported on this
series.
The registered `sh7058_jk78c` series contains JK78C. It uses an independent
SH7058 address profile, independently assembled target payloads, Map Switching,
and custom CAN telemetry. Rolling Launch is not supported on this series.
Every member retains its own stock identity, calibration, and checksum layout.
The command has two selection modes:

```bash
make rom-build INPUT=INPUT.bin OUTPUT=OUTPUT.bin
make rom-build INPUT=INPUT.bin OUTPUT=OUTPUT.bin ROM=JK08A
make rom-build INPUT=INPUT.bin OUTPUT=OUTPUT.bin ROM=JK00C
make rom-build INPUT=INPUT.bin OUTPUT=OUTPUT.bin ROM=JK78C
make rom-build INPUT=INPUT.bin OUTPUT=OUTPUT.bin ROM=1ND0A
```

The default `--rom auto` mode identifies the exact member from the registered
image size and immutable identity bytes at `0x8204..0x8219`. It does not inspect
the file name. An explicit selector bypasses selection ambiguity but does not
bypass image validation. Both modes require the selected stock identity, valid
input checksums, target-specific protected regions, and exact address-profile
anchors where the selected family declares them.

Every invocation validates `rom-images/roms.csv` and
`rom-images/homology.toml`. The selected stock image must match its registered
SHA-256 identity and its family contract before any composition is accepted.

Use `--verify-only` to run the complete in-memory composition and verification
without creating files:

```bash
make rom-verify INPUT=INPUT.bin
make rom-verify INPUT=INPUT.bin ROM=JK00D
```

## Registered-family pipeline

The common handler performs these operations in one invocation:

1. Validate image size, immutable identity, and all six stored checksum values.
2. Validate either the exact-family ownership ledger or the SHA-bound relocated
   address profile, erased allocation, capabilities, and target payload registry.
3. Classify the image as a compatible unpatched base or a complete runtime that
   can be migrated. The CAN telemetry layer must be wholly absent or match the
   exact current payload, configuration, mailbox record, hooks, and erased
   future reserve. After removing a validated telemetry layer in memory, the
   Rolling Launch layer, when supported, must be wholly absent, match the exact
   current payload and configuration schema, or match one registered historical
   unit fingerprint and its schema contract. A target without Rolling Launch
   must contain no Rolling Launch artifacts. Mixed hooks or DIDs, unknown
   payload bytes, partial pointer tables, invalid configuration records,
   occupied reserves, and unknown protected-code changes are rejected.
4. Normalize only the builder-owned Map Switching, optional Rolling Launch,
   CAN telemetry, and checksum ranges back to bytes from the selected stock
   member.
5. Apply the current Map Switching composition from the canonical payload
   manifest or the selected target section of
   `runtime-target-payloads.toml`.
6. Restore every Map 2 through Map 5 calibration byte when the input already
   contains a complete runtime. An unpatched base initializes these slots from
   its Map 1 values.
7. Apply the current Rolling Launch composition from the applicable payload
   registry and selected local profile when the target supports it. Otherwise
   require `observe` mode with no enabled maps and emit no Rolling Launch bytes.
8. Apply the current CAN telemetry composition from the applicable payload
   registry. The built-in profile installs the runtime in fail-closed
   disabled-at-startup mode. The SH7058 exact-code, JK78C, and SH7059 1ND
   families use mailbox 26; the 8MFK family uses stock-inactive mailbox 24. All
   four family layouts use mailbox 31 as the control receiver after each HCAN1
   initialization.
9. Recalculate self-test B, self-test A, SUM16 A, and SUM16 B in dependency
   order, then verify all stored values again.
10. Require every final difference from the input to be inside the union of the
    enabled component write sets and the checksum fields.

The builder preserves calibration and configuration outside its declared
ranges, including the Developer Immobilizer bit edited through the matching
`defs/<ROM>.xml` or `defs/<ROM>.xdf`. Map 1 and every newly initialized Map 2
through Map 5 copy come from the selected input, never from JK08A. The builder
does not call an Immobilizer patcher. Historical image identities and hardware
outcomes are retained in `hardware-results.toml`; the production path imports
only the current composition modules.

## Relocated address profiles

`rom-address-profiles.toml` records exact JK00C, JK00D, JK78C, 1ND0A, and 1ND3B
stock addresses, capabilities, and audited runtime allocations.
`rom_address_profiles.py` binds every profile to its registered stock image,
verifies all original hook words, requires the complete erased ROM envelope,
preserves occupied stock mailboxes, and rejects incomplete variant contracts or
semantic tables. The registry has no implicit ROM selector.

The 8MFK runtime uses a uniform ROM relocation of `0xC700` and a RAM relocation
of `0x300`, while retaining explicit nonuniform stock hooks and application-RAM
sources. Its exhaust-CVTC target is two independent bank families. The second
adapter and its four map copies occupy the beginning of the former telemetry
future reserve. The target limiter copies the two-byte-aligned stock throttle
container with `MOV.W`; using the canonical `MOV.L` loop would fault on SH-2E.
Telemetry uses stock-inactive mailbox 24 and a completion ISR that handles that
mailbox before tail-chaining to the complete stock ISR. Its final `JMP` delay
slot restores `r0`, preserving the interrupted register file at the stock ISR
boundary.

The 1ND runtime uses a uniform ROM relocation of `0x60000` and a RAM relocation
of `-0x5100`, with explicit nonuniform SH7059 stock hooks and application-RAM
sources. Separate adapters cover both fuel-compensation banks and both warm-idle
banks. The target limiter publishes only the selected throttle scalar because
the canonical 2x2 rev-limit fuel-cut actuator has no verified 1ND homolog.
Telemetry uses mailbox 26 and a register-preserving completion wrapper that
tail-chains to the complete stock ISR.

The JK78C runtime uses a uniform ROM relocation of `-0xB5600` from the VQ37
assembly layout and a RAM relocation of `-0x5100`, with explicit nonuniform
stock hooks and SH7058 application-RAM sources. The audited erased ROM envelope
is `0x0001CAAC..0x00020000`; active generated units end at `0x0001FA00`, leaving
a `0x600`-byte reserve. The audited RAM allocation is
`0xFFFF0C00..0xFFFF1000`, of which the runtime claims
`0xFFFF0C00..0xFFFF0F00`. Separate adapters cover both fuel-compensation banks
and both warm-idle banks. The limiter publishes only the selected throttle
scalar. Telemetry uses mailbox 26 and a register-preserving completion wrapper
that tail-chains to the complete stock ISR.

`runtime_targets.py` renders every target source through explicit stock and RAM
bindings. `runtime-target-payloads.toml` locks the GNU-assembled unit bytes and
the capability-specific stage hashes for each exact relocated stock image.
Regenerate the registry only through:

```bash
make runtime-targets-generate
```

The production builder and executable gate consume the same projected layouts
and locked payloads for JK00C, JK00D, JK78C, 1ND0A, and 1ND3B.

## SH7059 1ND correspondence

`1nd-runtime-correspondence.csv` records the reviewed 1ND0A runtime allocation,
stock hooks, target-specific map topology, CAN bindings, and all 63 ECU-RAM
telemetry fields. 1ND3B shares the exact executable image and therefore the
same addresses. The file distinguishes direct mappings from target-specific
adapters and unsupported source semantics.

The 1ND firmware does not retain the separate signed Q8 knock timing state
used by JK08A. Its ignition path selects the high- or low-octane surface
directly and keeps byte-sized results. `knock_timing_state_raw` is therefore
explicitly unsupported instead of being assigned to an unrelated RAM word.
The surface selector itself remains available at `0xFFFE9488`, where bit 6 is
consumed by the target ignition and correction paths.

The 1ND address profile binds twelve switched families: four DFCO rows, two
ignition surfaces, shared cold-idle timing, separate warm-idle timing for both
banks, separate fuel compensation for both banks, and the throttle-limiter
scalar. Custom CAN telemetry binds 62 available schema fields. The unavailable
knock timing field is encoded from cleared reserved RAM and remains identified
as unavailable in metadata. 1ND0A and 1ND3B share executable payload bytes but
retain separate stock identities, stage hashes, and six-field checksum closure.

## SH7058 JK78C correspondence

`jk78c-runtime-correspondence.csv` records the reviewed JK78C runtime
allocation, stock hooks, VQ37 map topology, CAN bindings, and all 63 ECU-RAM
telemetry fields. It distinguishes direct mappings from target-specific
adapters and unsupported source semantics.

The JK78C address profile binds the same twelve semantic families as 1ND while
retaining independent SH7058 addresses and stock code. Custom CAN telemetry
binds 62 available schema fields. The unavailable signed Q8 knock timing field
is encoded from cleared reserved RAM and remains identified as unavailable in
metadata. The profile also binds both SUM16 regions and both runtime SUM/XOR
regions to the independently reproduced stock checksum values.

The complete flash-envelope reference audit found four erased stock targets
inside the free span. None intersects a generated runtime write. A full
instruction and p-code RAM audit found no stock access to the claimed RAM
range. These static results establish software ownership only; JK78C remains
`UNTESTED` on bench and vehicle hardware.

## Rolling Launch profile

Without `--profile`, a Rolling Launch-capable target uses the conservative
built-in `rpm-hold-map1-test` profile: Map 1 enabled, RPM Hold mode, and
ignition retard disabled. A VQ37 target uses `observe` mode with no enabled maps
and emits no Rolling Launch stage. A separate local TOML file selects all
Rolling Launch calibration, including the bounded-retard mode:

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
make rom-build INPUT=INPUT.bin OUTPUT=OUTPUT.bin \
  PROFILE=LOCAL-PROFILE.toml
```

The accepted mode names are `observe`, `rpm_hold`, and `rpm_hold_retard`.
`enabled_maps` uses one-based map numbers. Every field is mandatory, unknown
fields are rejected, and the resulting 32-byte configuration must pass the
independent fail-closed model. `rom` may name the complete
applicable `sh7058_7mfkavn86`, `sh7058_8mfk`, `sh7058_jk78c`, or `sh7059_1nd`
series, or bind the profile to one exact member. A profile for
`sh7058_jk78c`, JK78C, `sh7059_1nd`, 1ND0A, or 1ND3B must use `observe` with an
empty `enabled_maps` array because the series has no Rolling Launch capability.
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

Every profile changes the selected stock-inactive mailbox record from type 5
to interrupt-enabled transmit type 4 and encodes the selected data ID as
`STDID << 5`. The SH7058 exact-code family writes mailbox 26 at `0x000097BE`;
JK78C writes mailbox 26 at `0x000094AE`; 1ND writes mailbox 26 at `0x0000974C`;
JK00C and JK00D write mailbox 24 at their profile-specific record address.
`enabled` controls whether sampling starts
after reset; an idle type-4 mailbox does not request CAN traffic. A validated
START command on `can_id + 1` activates streaming until reset even when
`enabled = false`, and STOP forces it off. The builder validates the exact
mailbox record against the configuration and rejects a partial or mismatched
endpoint.

A profile can start transmission automatically only after a passive
whole-vehicle capture proves both adjacent IDs unused and a measured bus-load
review selects the page profile and divisor. The generated XML/XDF switch edits
the same target-specific startup flag: `0x000D4E03` for the exact SH7058
family, `0x000E1503` for 8MFK, `0x0001F803` for JK78C, and `0x00134E03` for
1ND.

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
