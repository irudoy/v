# Unified ROM builder

`build_rom.py` is the production entry point for constructing a complete ROM.
Its input is the registered stock image of the selected ROM. It installs every
current firmware runtime registered for the selected series, recalculates all
checksum domains, verifies the final closed write set, and creates one ROM with
digest sidecars and a machine-readable manifest. Calibration of an existing
image moves to a fresh build through the [calibration transfer](#calibration-transfer).

The registered `sh7058_7mfkavn86` exact-code series contains JK00A, JK03A,
JK03B, and JK08A. JK08A is its canonical address and executable-code profile.
The registered `sh7058_8mfk` near-code series contains JK00C and JK00D. It uses
exact target address profiles and independently assembled target payloads.
The registered `sh7059_1nd` exact-code series contains 1ND0A and 1ND3B. It uses
a shared SH7059 address profile, independently assembled target payloads, Map
Switching, Rolling Launch, and custom CAN telemetry.
The registered `sh7059_1me3b` series contains 1ME3B. It uses its own SH7059
address profile, independently assembled target payloads, Map Switching,
Rolling Launch, and custom CAN telemetry.
The registered `sh7058_jk78c` series contains JK78C. It uses an independent
SH7058 address profile, independently assembled target payloads, Map Switching,
Rolling Launch, and custom CAN telemetry.
Every member retains its own stock identity, calibration, and checksum layout.

The `apply_*.py` scripts are isolated diagnostic stages for one runtime each.
They are not the production image workflow, and the composition and assembly
modules behind them operate in memory without a flashable output path.

The command has two selection modes:

```bash
make rom-build INPUT=STOCK.bin OUTPUT=OUTPUT.bin
make rom-build INPUT=STOCK.bin OUTPUT=OUTPUT.bin ROM=JK08A
make rom-build INPUT=STOCK.bin OUTPUT=OUTPUT.bin ROM=JK00C
make rom-build INPUT=STOCK.bin OUTPUT=OUTPUT.bin ROM=JK78C
make rom-build INPUT=STOCK.bin OUTPUT=OUTPUT.bin ROM=1ND0A
```

The default `--rom auto` mode identifies the exact member from the registered
image size and immutable identity bytes at `0x8204..0x8219`. It does not inspect
the file name. An explicit selector bypasses selection ambiguity but does not
bypass image validation. Both modes require the input to be byte-identical to
the registered stock image of the selected member. A built, calibrated, or
otherwise modified image is rejected before composition, and the message names
the calibration transfer commands.

Every invocation validates `rom-images/roms.csv` and
`rom-images/homology.toml`. The selected stock image must match its registered
SHA-256 identity and its family contract before any composition is accepted.

Use `--verify-only` to run the complete in-memory composition and verification
without creating files:

```bash
make rom-verify INPUT=STOCK.bin
make rom-verify INPUT=STOCK.bin ROM=JK00D
```

## Registered-family pipeline

The common handler performs these operations in one invocation:

1. Validate image size and immutable identity, require the input to equal the
   registered stock image, and verify all six stored checksum values.
2. Validate either the exact-family ownership ledger or the SHA-bound relocated
   address profile, erased allocation, capabilities, and target payload registry.
3. Apply the current Map Switching composition from the canonical payload
   manifest or the selected target section of
   `runtime-target-payloads.toml`. Each Map 2 through Map 5 slot starts as a
   copy of the stock Map 1 values.
4. Apply the current Rolling Launch composition from the applicable payload
   registry and selected local profile when the target supports it. Every
   currently registered family has a target-specific Rolling Launch stage.
5. Apply the current CAN telemetry composition from the applicable payload
   registry. The built-in profile installs the runtime in fail-closed
   disabled-at-startup mode. All five family layouts use mailbox 31 as the
   control receiver after each HCAN1 initialization and stock-inactive mailbox
   26 for telemetry.
6. Recalculate self-test B, self-test A, SUM16 A, and SUM16 B in dependency
   order, then verify all stored values again.
7. Require every final difference from the input to be inside the union of the
   enabled component write sets and the checksum fields.

Calibration edits, including Map 1 through Map 5 tables, the Developer
Immobilizer bit, and the cruise control configuration byte of the Cruise
Control Switch, are made on a built image through the matching
`defs/<ROM>.xml` or `defs/<ROM>.xdf`. Map 1 and the initial Map 2 through Map 5
copies come from the selected stock image, never from JK08A. The builder does
not call an Immobilizer patcher. Historical image identities and hardware
outcomes are retained in `hardware-results.toml`; the production path imports
only the current composition modules.

## Calibration transfer

Calibration moves from an existing image to a fresh build in two explicit
steps: extraction into local files, then application over a build of the stock
image.

```bash
make rom-extract INPUT=tmp/tuned.bin \
  CALIBRATION=tmp/tuned-calibration.toml PROFILE=tmp/tuned-profile.toml
make rom-build INPUT=STOCK.bin OUTPUT=tmp/fresh.bin \
  PROFILE=tmp/tuned-profile.toml
make rom-calibrate INPUT=tmp/fresh.bin \
  CALIBRATION=tmp/tuned-calibration.toml OUTPUT=tmp/calibrated.bin
```

`calibration_ranges.py` declares the calibration ranges of each registered
ROM: the compatible window `0x8200..0x20000` without the ROM identity, the
builder write sets, the checksum fields, and every byte that a build layout
pins to its stock value, plus each Map 2 through Map 5 slot. The Rolling
Launch and CAN telemetry configuration records are builder write sets; their
settings travel in a build profile. Editor elements outside these ranges, such
as the load axis of the Engine Torque Map, are rejected by address.

`extract_calibration.py` accepts a registered stock image or an image built
from one: a calibrated stock image, a current builder output, or a registered
historical runtime endpoint of the selected ROM. It requires valid checksums
and every difference from the stock image inside the calibration ranges, the
builder write sets, or the checksum fields; any other difference is rejected
by address. The builder write sets must hold no runtime or one complete
runtime. The CAN telemetry layer must be wholly absent or match the exact
current payload, configuration, mailbox record, and hooks. After removing a
validated telemetry layer in memory, the Rolling Launch layer, when supported,
must be wholly absent, match the exact current payload and configuration
schema, or match one registered historical unit fingerprint and its schema
contract. A current telemetry layer is accepted only above the current Rolling
Launch endpoint or above a registered complete endpoint explicitly marked
compatible with that telemetry contract. The previous guarded ignition
controller remains a registered endpoint on every ROM that accepts a complete
Rolling Launch layer, including the JK08A ASCD state-6/7 arbiter variant. A
target without Rolling Launch must contain no Rolling Launch artifacts. Mixed
hooks or DIDs, unknown payload bytes, partial pointer tables, and invalid
configuration records are rejected as partial or unknown states.

The calibration file is local TOML schema 1. It binds the exact ROM and the
SHA-256 of its registered stock image, records the SHA-256 and runtime states
of the source, and lists each contiguous run of calibration bytes that differs
from a fresh stock build: the stock bytes for the window and the Map 1 bytes
for each Map 2 through Map 5 slot. No run crosses a range boundary. Its
`[settings]` table holds the SHA-256 of each Rolling Launch and CAN telemetry
configuration record of the source; it is a check, not a second source. The
extracted profile carries the settings in the strict profile format below and
is read back through the profile loader before it is written. A source without
Rolling Launch settings yields the calibration file only. A historical schema 1
or schema 2 Rolling Launch record, which the profile schema cannot express, is
reported with its fields; the command then writes the calibration file only
and exits with status 3.

`apply_calibration.py` accepts only an image that a rebuild of the registered
stock image with the settings of its own configuration records reproduces byte
for byte. Each configuration record that the calibration file binds must hold
the extracted settings, so a transfer cannot fall back to the built-in profile
unnoticed; `REPLACE_SETTINGS=1` (`--replace-settings`) replaces them
explicitly. The command writes the calibration elements, recalculates every
checksum, requires every difference from the build to lie inside the
calibration ranges or the checksum fields, and requires the output to remain
an extraction input. It creates the ROM with SHA-256, MD5, and JSON manifest
sidecars under the same publication rules as the builder. Its manifest binds
the input, the calibration file and the result of its settings check, and the
output, which is marked `hardware_status=UNTESTED`.

Calibration files, profiles, and calibrated images are local artifacts. Both
commands write only outside the repository or to a path that Git ignores, such
as `tmp/`.

## Relocated address profiles

`rom-address-profiles.toml` records exact JK00C, JK00D, JK78C, 1ND0A, 1ND3B,
and 1ME3B stock addresses, capabilities, and audited runtime allocations.
`rom_address_profiles.py` binds every profile to its registered stock image,
verifies all original hook words, requires the complete erased ROM envelope,
preserves occupied stock mailboxes, and rejects incomplete variant contracts or
semantic tables. The registry has no implicit ROM selector.

The 8MFK runtime uses a uniform ROM relocation of `0xC700` and a RAM relocation
of `0x300`, while retaining explicit nonuniform stock hooks and application-RAM
sources. It switches an intake-cam target family and an exhaust-cam target
family independently. The intake family reuses the canonical CVTC allocation;
the exhaust family adds a second adapter and four map copies at the beginning
of the former telemetry future reserve. The target limiter copies the
two-byte-aligned stock throttle container with `MOV.W`; using the canonical
`MOV.L` loop would fault on SH-2E.
Telemetry uses stock-inactive mailbox 26 and a completion ISR that handles that
mailbox before tail-chaining to the complete stock ISR. Its final `JMP` delay
slot restores `r0`, preserving the interrupted register file at the stock ISR
boundary. JK00C and JK00D telemetry binds the ECU-RAM fields to target source
symbols, whose meanings hold the producer correspondence of each binding, for
example `uv run kb show alpha_n_flow/ram`;
`uv run kb gaps --feature can_telemetry --layout jk00c` lists any unavailable
field.

The 1ND runtime uses a uniform ROM relocation of `0x60000` and a RAM relocation
of `-0x5100`, with explicit nonuniform SH7059 stock hooks and application-RAM
sources. Separate adapters cover both fuel-compensation banks and both warm-idle
banks. Its limiter atomically publishes two native fuel-cut caps, independent
eight-point activation and release curves, and the selected throttle scalar.
Exact pointer redirects feed those RAM shadows to the stock 190-byte hysteresis
state machine. Rolling Launch runs the stock final-mask coordinator first and
adds an exact all-cylinder request in an active non-observe state from the
captured cut until engine speed falls below restore.
Telemetry uses mailbox 26 and a register-preserving completion wrapper that
tail-chains to the complete stock ISR.

The 1ME3B runtime uses a uniform ROM relocation of `0x69000` and a RAM
relocation of `-0x5100`, with explicit nonuniform SH7059 stock hooks and
application-RAM sources. The audited erased ROM envelope is
`0x00139DC4..0x0013FF00`, of which the runtime claims
`0x0013B108..0x0013F000`; the audited RAM allocation is
`0xFFFF0C00..0xFFFF1000`, of which the runtime claims
`0xFFFF0C00..0xFFFF0F00`. The adapter, limiter, Rolling Launch, and telemetry
contract equals the 1ND contract. The compiler lays out the bitfield status
bytes of this image independently: the active and armed flags of the native
fuel-cut state byte are bits 3 and 2, and the MAIN switch bit of the ASCD flag
byte `0xFFFEB985` is bit 1. Bytes tested through explicit masks keep the 1ND
layout. Rolling Launch wraps the final-mask coordinator `0x07A740`. Telemetry
uses mailbox 26 and the same register-preserving completion wrapper.

The JK78C runtime uses a uniform ROM relocation of `-0xB5600` from the VQ37
assembly layout and a RAM relocation of `-0x5100`, with explicit nonuniform
stock hooks and SH7058 application-RAM sources. The audited erased ROM envelope
is `0x0001CAAC..0x00020000`; active generated units end at `0x0001FA80`, leaving
a `0x580`-byte reserve. The audited RAM allocation is
`0xFFFF0C00..0xFFFF1000`, of which the runtime claims
`0xFFFF0C00..0xFFFF0F00`. Separate adapters cover both fuel-compensation banks
and both warm-idle banks. The limiter publishes the same native cap, curve, and
throttle contract as 1ND through JK78C-specific pointers and state bits.
Rolling Launch wraps the JK78C final-mask coordinator without replacing stock
inhibit contributions. Telemetry uses mailbox 26 and a register-preserving
completion wrapper that tail-chains to the complete stock ISR.

Every telemetry target binds the knock margin wrapper to its own slice
evaluator through hook `knock_margin_latch`, the only literal of that
evaluator, and reads the target selector byte, both channel bytes, the metric
array, and the threshold array through profile symbols. The wrapper tests
selector bit 3 at run time, so one source serves the stock primary selection
of JK08A and the stock alternate selection of the other targets:

| Target | Evaluator | Literal | Selector byte and stock value | Channel primary, alternate | Metric base | Threshold base |
| --- | ---: | ---: | --- | --- | ---: | ---: |
| JK08A | `0x04A238` | `0x04A9C0` | `0x8B3D` = `0x82` | `FFFF11DE`, `FFFF2143` | `FFFF21D8` | `FFFF2144` |
| JK00C | `0x04B27C` | `0x04BA04` | `0x8B70` = `0x8A` | `FFFF11EE`, `FFFF21B3` | `FFFF2248` | `FFFF21B4` |
| JK00D | `0x04B280` | `0x04BA08` | `0x8B71` = `0x8A` | `FFFF11EE`, `FFFF21BB` | `FFFF2250` | `FFFF21BC` |
| JK78C | `0x063AC8` | `0x06429C` | `0x8965` = `0xBA` | `FFFF11C8`, `FFFF2097` | `FFFF212C` | `FFFF2098` |
| 1ND0A, 1ND3B | `0x06EA18` | `0x06F17C` | `0x8A2B` = `0xBA` | `FFFE81D6`, `FFFE9137` | `FFFE91CC` | `FFFE9138` |
| 1ME3B | `0x072920` | `0x07308C` | `0x8A7C` = `0xBA` | `FFFE81BC`, `FFFE90FF` | `FFFE9194` | `FFFE9100` |

`runtime_targets.py` renders every target source through explicit stock and RAM
bindings. The JK08A values of the key tables of the feature targets and the
hook keys of each map target come from the entity files through `kb.targets`.
The selector host and the Rolling Launch engine test the named bit `main` of
`ascd_state/ram` on each layout: bit 7 on JK08A, JK00C, and JK00D, bit 4 of
`0xFFFF450B` on JK78C, bit 5 on 1ND0A and 1ND3B, and bit 1 on 1ME3B.
`runtime-target-payloads.toml` locks the GNU-assembled unit bytes and
the capability-specific stage hashes for each exact relocated stock image.
Regenerate the registry only through:

```bash
make runtime-targets-generate
```

The production builder and executable gate consume the same projected layouts
and locked payloads for JK00C, JK00D, JK78C, 1ND0A, 1ND3B, and 1ME3B.

## SH7059 1ND correspondence

`1nd-runtime-correspondence.csv` records the reviewed 1ND0A runtime allocation,
stock hooks, target-specific map topology, CAN bindings, and all 60 ECU-RAM
telemetry fields. 1ND3B shares the exact executable image and therefore the
same addresses. The file distinguishes direct mappings from target-specific
adapters and unsupported source semantics.

The 1ND knock function `0x06D948` stores the signed Q8 knock timing state
`0xFFFE8214` at `0x06DD78` only while bit 5 of `ROM8[0x8A2B]` is clear.
`knock_timing_state_raw` reads that word, which the stock configuration never
stores and so leaves at its start value. Bit 6 of `0xFFFE9488`, which the target
correction paths also consume, selects the high- or low-octane surface only
inside the gated half of the ignition coordinator `0x074D98`. Stock `ROM8[0x8A2B]` = `0xBA` (bit 5 set) executes the
mode-selected half instead, which picks its surface by the state code derived
from the VVEL mode.

The two ignition families are the executed 16x16 surfaces `0x00A410` and
`0x00A510` of that half. They reuse the geometry, slot storage, and pointer
tables of the two canonical 16x16 ignition families. The three surfaces of the
gated half, `0x009880`, `0x009980`, and `0x009A80`, hold equal stock bytes and
belong to no family. The ignition hook at `0x0757B8` serves a literal that only
the gated half reads, so every call through it passes through the adapter to
the stock lookup. The profile validator requires bit 5
of the stock configuration byte, equal stock bytes in the three gated
surfaces, and their absence from the family set.

The four 8x8 state-code surfaces `0x00A610`, `0x00A710`, `0x00A690`, and
`0x00A6D0` are four further ignition families. The coordinator reads them
through the separate 8x8 lookup `0x0285B4`, whose pointer it takes from the
single literal `0x074FB0`; the hook `ignition_state_lookup` redirects that
literal to the adapter `ignition_state_adapter`. The lookup takes `r4` to `r7`
and one stack argument, so the adapter substitutes only `r4`, leaves `r15` and
`PR` untouched, and tail-jumps to the stock lookup; any other table base
passes through unchanged. Its slot selection is local because the shared
helper lies outside `BRA` range. The second literal of the lookup, `0x075570`,
serves only the reference surface `0x00A650` of the stock-inert path and stays
stock. The adapter, four pointer tables, and sixteen 64-byte slot copies occupy
`0x135080..0x135580`, directly behind the fuel-cut coordinator wrapper, and the
telemetry reserve starts at `0x135580`. The profile table
`ignition_state_storage` declares that allocation, and the target validator
requires each of the four table bases to occur exactly once in the stock
image, inside the literal pool of the hooked literal.

The 1ND address profile binds eighteen switched families: four DFCO rows, the
two executed 16x16 ignition surfaces, the four 8x8 state-code ignition
surfaces, shared cold-idle timing, default and alternate warm-idle
timing, default and alternate fuel compensation, native fuel-cut caps and
curves, and the throttle-limiter scalar. Custom CAN telemetry binds the schema
fields to 1ND0A source symbols, which hold the evidence of each binding. The two
intake CVTC duty command fields read 8-bit command cells: in the 16-bit duty
scheme that the stock calibration selects, the BFR programmer writes BFR7B and
BFR7A from 16-bit duty words, and the cells hold their high bytes after two
scheduler copies. The source symbols record the cell scale of that scheme
(`uv run kb show intake_cvtc_duty_command_b1/ram`,
[`JK78C.cvtc.md`](../defs/JK78C.cvtc.md)). A field whose source meaning has a
status on the layout is encoded from cleared reserved RAM and remains
identified as unavailable in metadata;
`uv run kb gaps --feature can_telemetry --layout 1nd` lists those fields with
the evidence of each status.
1ND0A and 1ND3B share executable payload bytes but retain separate stock
identities, stage hashes, and six-field checksum closure.

## SH7059 1ME3B correspondence

`1me3b-runtime-correspondence.csv` records the reviewed 1ME3B runtime
allocation, stock hooks, target-specific map topology, CAN bindings, and all 60
ECU-RAM telemetry fields. It distinguishes direct mappings from
target-specific adapters and unsupported source semantics, and its test
requires every target and stock word to equal the validated address profile.

The 1ME3B address profile binds the eighteen 1ND families. Stock
`ROM8[0x8A7D]` = `0x1C` has bit 3 set for the state-code dispatch. The two
16x16 surfaces `0x00A344` and `0x00A444` use lookup `0x029BA8` through five
aligned literals: `0x079420`, `0x0796F4`, `0x0799A4`, `0x079CAC`, and
`0x079E24`. Each literal redirects to the adapter at `0x13B340`. The four
8x8 state-code surfaces `0x00A544`, `0x00A644`, `0x00A5C4`, and `0x00A604`
use lookup `0x0293D8` through literals `0x079404` and `0x079994`, both of
which redirect to the adapter at `0x13E080`. The state adapter, four pointer
tables, and sixteen 64-byte slot copies occupy `0x13E080..0x13E580`.

Positive call-window obligations bind each lookup load, its actual indirect
JSR register, delay slot, table and axis operands, and any intervening stack
argument store. The executable gate reconstructs these stock instructions
independently and observes the changed lookup paths through the adapters.
The unchanged interpolation body is an observing simulator stub; interpolation
arithmetic, scheduler reachability, arbitrary computed consumers, and hardware
behavior remain outside this boundary. The reference surface `0x00A584`
remains outside the switched families.

The legacy profile key `ignition_unreferenced_routine` names
`0x0791A4..0x0797CB` for a bounded image scan. That scan rejects aligned
inbound pointer values and direct PC-relative branch encodings to the entry.
It does not establish absence of interior or computed control-flow entries.
No lookup pointer is excluded from coverage because of this region key.

Custom CAN telemetry binds the ECU-RAM fields to 1ME3B source symbols, which
hold the evidence of each binding. The two intake solenoid duty command fields
use the 16-bit duty scheme of 1ND. The knock surface field reads the target
high-detonation state byte; the capture moves the state bit into the bit that
the wire contract decodes and clears the other bits of the byte
(`uv run kb show knock_surface_state/ram`). A field whose source meaning has a
status on the layout is encoded from cleared reserved RAM and remains
identified as unavailable in metadata;
`uv run kb gaps --feature can_telemetry --layout 1me3b` lists those fields with
the evidence of each status.

## SH7058 JK78C correspondence

`jk78c-runtime-correspondence.csv` records the reviewed JK78C runtime
allocation, stock hooks, VQ37 map topology, CAN bindings, and all 60 ECU-RAM
telemetry fields. It distinguishes direct mappings from target-specific
adapters and unsupported source semantics.

The JK78C address profile binds fourteen families, the 1ND set without the
four state-code ignition surfaces that the JK78C coordinator does not carry,
while retaining independent SH7058 addresses and stock code. Its two ignition families
are the executed surfaces `0x00A10A` and `0x00A20A` of the mode-selected half of
the coordinator `0x069AB8`, which stock `ROM8[0x8965]` = `0xBA` (bit 5 set)
executes and which picks the surface by coolant temperature. The three
equal-byte surfaces of the gated half, `0x0095CA`, `0x0096CA`, and `0x0097CA`,
belong to no family and pass through the adapter under the same validator
rules as 1ND. The ignition hooks at `0x062F10` and `0x069DB0` serve the knock
path and the gated half only, so every call through them passes through. Custom CAN telemetry
binds the schema fields to JK78C source symbols, which hold the evidence of
each binding. Under the stock calibration the knock timing field carries the
start value of its word (`uv run kb show knock_timing_state/ram`), and the Fuel
Compensation Main column field reads the column word of the target Fuel
Compensation surfaces in place of the JK08A coordinate cell
(`uv run kb show diamond-macaque/ram`). The profile also binds both SUM16 regions and both runtime SUM/XOR
regions to the independently reproduced stock checksum values.

The flash-envelope audit distinguishes comparison operands from executable
address references. The reviewed literal loads have these uses:

| Value | Load instructions | Use |
| --- | --- | --- |
| `0x1E30C` | `0x0DA356`, `0x0DA462` | Unsigned comparison limit at `0x0DA35C` and `0x0DA468` |
| `0x1FFFE` | `0x088196` | Saturation comparisons at `0x0881A0` and `0x0881B0` |
| `0x1FFFF` | `0x001816`, `0x002C98` | Unsigned range bounds at `0x001818` and `0x002C9E` |

These sites compare the loaded values rather than dereferencing them or
transferring control to them. A numeric operand equal to a flash address does
not by itself establish a memory access. The reference exclusion check covers
the combined Map Switching, Rolling Launch, and CAN telemetry write ranges.
It conservatively preserves the disjoint audit candidates `0x1FE00`,
`0x1FFFE`, and `0x1FFFF`. The exported 32-bit load query has no exact match for
`0x1FE00`; its use remains unclassified, and absence of a match does not
establish absence of runtime access.

A full instruction and p-code RAM audit found no stock access to the claimed RAM
range. These static results establish software ownership only; JK78C remains
`UNTESTED` on bench and vehicle hardware.

## Rolling Launch profile

Without `--profile`, a Rolling Launch-capable target
uses the conservative built-in `rpm-hold-map1-test` profile: Map 1 enabled, RPM Hold mode, and
ignition retard disabled. A VQ37 target installs its complete Rolling Launch
stage with the built-in `observe` profile and no enabled maps. A separate local
TOML file can enable RPM Hold or bounded-retard mode on any registered family:

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
applicable `sh7058_7mfkavn86`, `sh7058_8mfk`, `sh7058_jk78c`, `sh7059_1nd`, or
`sh7059_1me3b` series, or bind the profile to one exact member. A profile for
`sh7058_jk78c`, JK78C, `sh7059_1nd`, 1ND0A, 1ND3B, `sh7059_1me3b`, or 1ME3B
accepts the same three modes and one-based map mask as the SH7058
VQ25HR/VQ35HR families.
`min_speed = 0` disables the vehicle-speed activation gate, and
`min_pedal = 0` disables the pedal-position activation gate.
`hysteresis_ratio_tenths = 20` means 2.0 percent of captured RPM. The runtime
rounds that proportional value and clamps it between the configured native-RPM
minimum and maximum. The effective ignition-retard ramp is at least the
configured minimum, at least twice the effective hysteresis, and no wider than
the RPM offset.
Concrete profiles remain local and are not versioned.

Rolling Launch and CAN telemetry settings edited in a built image through an
editor travel in the extracted profile of the calibration transfer. Application
of a calibration file refuses a build whose configuration records differ from
the extracted settings and names the differing components, such as
`rolling_launch` or `can_telemetry`. Disabling Map 1 RPM Hold through an editor
therefore carries over only through the extracted profile or an explicit
replacement.

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
JK00C and JK00D write mailbox 26 at `0x00009882` and `0x00009892`.
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
found before staging causes the invocation to fail before any missing artifact
is created. Missing artifacts are written to temporary sibling files, flushed,
synchronized, and read back before publication. Sidecars are published before
the ROM, using atomic links that cannot replace existing files. An ordinary
publication failure removes only unchanged files created by that invocation;
identical files from an earlier attempt remain available for a retry. An
interruption can leave complete sidecars or temporary files, but cannot expose
a partially written ROM at its final path. The default output is adjacent to
the input; inputs under `rom-images/` require an explicit `--output`.

The JSON manifest binds the stock input, Map Switching stage, Rolling Launch
stage, both runtime configurations, CAN mailbox record, final output, checksum
values, write-set counts, and exact instruction audit counts. Manifest schema 4
records both the series and exact member. Every new image is marked
`hardware_status=UNTESTED`; software verification does not make it eligible for
flashing without target-specific bench and vehicle gates.

Manifest input and output paths are resolved absolute paths. Relative and
absolute spellings of the same paths produce byte-identical manifests.

The `input` section holds the path, SHA-256, and checksum values of the stock
image. `output.configuration` contains the Rolling Launch and CAN telemetry
records, their decoded settings, and the telemetry mailbox record; a target
without Rolling Launch has `null` in its place. The `profile` section describes
the selected output profile.
