# Unified ROM builder

`build_rom.py` is the production entry point for constructing a complete ROM.
Its default input is the registered stock image of the selected ROM. It installs every
current firmware runtime registered for the selected series, closes its
registered checksum fields, verifies the final closed write set, and creates one ROM with
digest sidecars and a machine-readable manifest. Calibration of an existing
image moves to a fresh build through the [calibration transfer](#calibration-transfer).

The registered `sh7058_7mfkavn86` exact-code series contains JK00A, JK03A,
JK03B, and JK08A. JK08A is its canonical address and executable-code profile.
The registered `sh7058_8mfk` near-code series contains JK00C and JK00D. It uses
exact target address profiles and independently assembled target payloads.
The registered `sh7059_1nd` exact-code series contains 1ND0A and 1ND3B. It uses
a shared SH7059 address profile, independently assembled target payloads, Map
Switching, and custom CAN telemetry.
The registered `sh7059_1me3b` series contains 1ME3B. It uses its own SH7059
address profile, independently assembled target payloads, Map Switching, and
custom CAN telemetry.
The registered `sh7059_1ek7a` series contains 1EK7A. It uses an independent
SH7059 address profile and target payloads for Map Switching and custom CAN
telemetry. It retains the exact stock prefix below `0x8200`. The manifest's
`audit.retained_checksums` records the stored and calculated vector values.
The registered `sh7058_jk78c` series contains JK78C. It uses an independent
SH7058 address profile, independently assembled target payloads, Map Switching,
and custom CAN telemetry.
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
bypass image validation. Without `UPGRADE=1`, both modes require the input to be byte-identical to
the registered stock image of the selected member. A built, calibrated, or
otherwise modified image is rejected before composition, and the message names
the calibration transfer commands.

An existing complete image upgrades in one invocation of the same builder:

```bash
make rom-build INPUT=tmp/in-car-profile7.bin OUTPUT=tmp/current-runtime.bin \
  UPGRADE=1 PROFILE=tmp/launch-profile.toml
make rom-build INPUT=tmp/in-car-profile7.bin OUTPUT=tmp/current-runtime.bin \
  UPGRADE=1 DISABLE_ROLLING_LAUNCH=1
```

`UPGRADE=1` selects `--upgrade`. The builder validates the source through the
calibration extractor, builds the current runtime from the registered stock
image, and applies every calibration element through the calibration writer.
The Rolling Launch settings of the output come from one of three sources:

- without `PROFILE`, the extracted settings of a current record, which the
  output must match;
- `PROFILE` (`--profile`), whose Rolling Launch settings replace those of the
  source; the profile scope must include the source ROM;
- `DISABLE_ROLLING_LAUNCH=1` (`--disable-rolling-launch`), the built-in
  `observe` profile with every map disabled; it requires `UPGRADE=1` and no
  `PROFILE`.

A registered historical Rolling Launch endpoint has no profile schema 4 form,
so its upgrade requires `PROFILE` or `DISABLE_ROLLING_LAUNCH=1`. The CAN
telemetry settings always come from the source and must match; the command
uses no `REPLACE_SETTINGS` bypass. Its manifest records source runtime
identities, the settings match or replacement, the fresh runtime stage, and
the calibration transfer. The output remains untested on hardware.

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
   registered stock image, and verify every stored checksum value declared by
   the selected layout in `checksum-layouts.toml`.
2. Validate either the exact-family ownership ledger or the SHA-bound relocated
   address profile, erased allocation, capabilities, and target payload registry.
3. Apply the current Map Switching composition from the canonical payload
   manifest or the selected target section of
   `runtime-target-payloads.toml`. Each Map 2 through Map 5 slot starts as a
   copy of the stock Map 1 values.
4. Apply the current Rolling Launch composition from the applicable payload
   registry and selected local profile when the target supports it. The
   `sh7058_7mfkavn86` family has the Rolling Launch stage; the relocated
   families have none.
5. Apply the current CAN telemetry composition from the applicable payload
   registry. The built-in profile installs the runtime in fail-closed
   disabled-at-startup mode. The control receiver is physical mailbox 22 on
   1ME3B and physical mailbox 31 on the other targets; telemetry transmits
   through stock-inactive mailbox 26. `can-telemetry.md` defines the preserved
   stock reception and the primary/recovery initialization boundaries.
6. Recalculate the selected layout's checksum domains in their declared
   dependency order, then verify every stored value again. The SH7058 layout
   uses self-test B, self-test A, SUM16 A, and SUM16 B; the SH7059 layouts use
   their declared SUM16 fields and runtime XOR/SUM domains.
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

`UPGRADE=1` performs the transfer in memory through the unified builder. The
same stages are available as an explicit local workflow: extraction into
local files, then application over a build of the stock image.

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
runtime. The CAN telemetry layer must be wholly absent or match a complete
current or registered historical payload, configuration, mailbox record, and
hooks. `can-telemetry-history.toml` owns the exact schema-2 components of
profile 7 of the 7mfk family and of profile 9 of JK08A. A historical telemetry
endpoint places its unit payloads, hook words, configuration record, erased
reserve and mailbox record by its own addresses and decodes the record under
the frozen contract of its protocol; every part of the current telemetry
layout outside it must hold the bytes below the telemetry layer. After
removing a validated telemetry layer in memory, the Rolling Launch layer, when
supported, must be wholly absent, match the exact current payload and configuration
schema, or match one registered historical endpoint. An endpoint places its
unit fingerprints, hook values, DID slots and record by its own addresses and
validates the record against the frozen contract of its schema; every other
offset of the current Rolling Launch layout and of the other registered
Rolling Launch and CAN telemetry endpoints of the ROM must hold the bytes below
the Rolling Launch layer: stock bytes, and the Map Switching replacement at the
hook words that both layers share.
Extraction and `UPGRADE` admit the writes of the registered endpoints of the selected ROM. A current telemetry layer is accepted only above the current Rolling
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
`[settings]` table binds configuration settings by SHA-256; it is a check,
not a second source. CAN telemetry uses the configuration record bytes. The
Rolling Launch binding is the SHA-256 of the current schema 6 record, which
holds only logical settings. The derived efficiency table lies outside the
record, so the binding holds when a calibrated F table changes it; the F bytes
travel as calibration elements.
The historical telemetry wire identity is omitted from that settings binding;
its enabled state, CAN ID, and divisor transfer through the current profile
format. The
extracted profile carries the settings in the strict profile format below and
is read back through the profile loader before it is written. A source without
Rolling Launch settings yields the calibration file only. Every registered
historical Rolling Launch record, configuration schemas 1 through 5, has no
profile schema 4 form: it is reported with its fields, and the command then
writes the calibration file only and exits with status 3.

`apply_calibration.py` accepts only an image that a rebuild of the registered
stock image with the settings of its own configuration records reproduces byte
for byte. Each configuration record that the calibration file binds must hold
the extracted settings, so a transfer cannot fall back to the built-in profile
unnoticed; `REPLACE_SETTINGS=1` (`--replace-settings`) replaces them
explicitly. The command writes the calibration elements, derives the Rolling
Launch efficiency table again from F of the result, recalculates every
checksum, requires every difference from the build to lie inside the
calibration ranges, the efficiency table or checksum fields, and requires
the output to remain an extraction input. It creates the ROM with SHA-256,
MD5, and JSON manifest
sidecars under the same publication rules as the builder. Its manifest binds
the input, the calibration file and the result of its settings check, and the
output, which is marked `hardware_status=UNTESTED`.

Calibration files, profiles, and calibrated images are local artifacts. Both
commands write only outside the repository or to a path that Git ignores, such
as `tmp/`.

### Map calibration copy

`copy_map_slot.py` gives other maps the calibration of one map of an image
with the current Map Switching runtime:

```bash
uv run python patches/copy_map_slot.py tmp/upgraded.bin --source-map 3 \
  --output tmp/map-3-base.bin
uv run python patches/copy_map_slot.py tmp/upgraded.bin --source-map 3 \
  --target-maps 1 5 --output tmp/maps-1-5-from-3.bin
```

For every Map Switching family of the layout of the ROM, the command copies
the slot of `--source-map` over the slot of each target map; Map 1 is the
canonical stock table. `--target-maps` defaults to every other map. The
command recalculates the checksum fields and requires every changed byte to
lie in a target slot or a checksum field, and the result to remain an
extraction input that a build of the registered stock image followed by its
calibration reproduces byte for byte. It refuses an image without the current
Map Switching runtime, a source map among the targets, and an output path
equal to the input. It writes the ROM with SHA-256, MD5, and JSON manifest
sidecars under the publication rules of the builder; the manifest names the
families whose target slots changed and the changed byte count, and marks the
output `hardware_status=UNTESTED`. The Rolling Launch flash gates and the
commit and CI qualification remain those of `make preflash`.

## Pre-flash qualification

`preflash.py` (`make preflash`) accepts an image for flashing only when the
builder at HEAD reproduces it byte for byte from the registered stock image.
An image without a runtime must equal the stock image with its calibration
elements and recalculated checksums. An image with the current runtime must
equal a build with the Rolling Launch and CAN telemetry settings of its own
configuration records, followed by the application of its calibration
elements. A registered historical runtime endpoint and settings that the
profile schema cannot express are refused. The Rolling Launch efficiency table
must equal the table derived from F of the image; a stale table is refused
with the refresh command of the editor section below. A record that enables a
map in `hold` mode is refused while the Rolling Launch layout declares no hold
actuator. The commit, CI, and test conditions are in the root `README.md`.

## Relocated address profiles

`rom-address-profiles.toml` records the exact stock addresses, capabilities,
and runtime allocations of the relocated targets.
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
state machine.
Telemetry uses mailbox 26 and a register-preserving completion wrapper that
tail-chains to the complete stock ISR.

The 1ME3B runtime uses a uniform ROM relocation of `0x69000` and a RAM
relocation of `-0x5100`, with explicit nonuniform SH7059 stock hooks and
application-RAM sources. The audited erased ROM envelope is
`0x00139DC4..0x0013FF00`, of which the runtime claims
`0x0013B108..0x0013F000`; the audited RAM allocation is
`0xFFFF0C00..0xFFFF1000`, of which the runtime claims
`0xFFFF0C00..0xFFFF0F00`. The adapter, limiter, and telemetry contract equals
the 1ND contract. The compiler lays out the bitfield status
bytes of this image independently: the active and armed flags of the native
fuel-cut state byte are bits 3 and 2, and the MAIN switch bit of the ASCD flag
byte `0xFFFEB985` is bit 1. Bytes tested through explicit masks keep the 1ND
layout. Telemetry uses mailbox 26 and the same register-preserving completion wrapper.

The JK78C runtime uses a uniform ROM relocation of `-0xB5600` from the VQ37
assembly layout and a RAM relocation of `-0x5100`, with explicit nonuniform
stock hooks and SH7058 application-RAM sources. The audited erased ROM envelope
is `0x0001CAAC..0x00020000`; active generated units end at `0x0001FA80`, leaving
a `0x580`-byte reserve. The audited RAM allocation is
`0xFFFF0C00..0xFFFF1000`, of which the runtime claims
`0xFFFF0C00..0xFFFF0F00`. Separate adapters cover both fuel-compensation banks
and both warm-idle banks. The limiter publishes the same native cap, curve, and
throttle contract as 1ND through JK78C-specific pointers and state bits.
Telemetry uses mailbox 26 and a register-preserving
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
The selector host tests the named bit `main` of `ascd_state/ram` on each
layout, and the Rolling Launch engine tests it on JK08A: bit 7 on JK08A, JK00C,
and JK00D, bit 4 of
`0xFFFF450B` on JK78C, bit 5 on 1ND0A and 1ND3B, and bit 1 on 1ME3B.
`runtime-target-payloads.toml` locks the GNU-assembled unit bytes and
the capability-specific stage hashes for each exact relocated stock image.
Regenerate the registry only through:

```bash
make runtime-targets-generate
```

The production builder and executable gate consume the same projected layouts
and locked payloads for every relocated target.

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
[`JK78C.cvtc.md`](../defs/analysis/valve-timing/JK78C.cvtc.md)). The knock branch field reads the
target direct-difference inhibit state in its role, and the knock branch and
LTFT neutral control bytes keep their bit in another bit than 7mfk; the
capture moves each bit into the bit that the wire contract decodes and clears
the other bits of the byte. A field whose source meaning has a
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
use the 16-bit duty scheme of 1ND. The knock surface and LTFT neutral control
fields read target bytes that keep their bit in another bit than 7mfk; the
capture moves each bit into the bit that the wire contract decodes and clears
the other bits of the byte (`uv run kb show knock_surface_state/ram`,
`uv run kb show ltft_publication_neutral_control/ram`). A field whose source meaning has a
status on the layout is encoded from cleared reserved RAM and remains
identified as unavailable in metadata;
`uv run kb gaps --feature can_telemetry --layout 1me3b` lists those fields with
the evidence of each status.

## SH7059 1EK7A correspondence

`1ek7a-runtime-correspondence.csv` records the stock hooks, native map
families, CAN bindings, and supported telemetry sources. The runtime uses
its own SH7059 flash and RAM reservations. The fused ignition coordinator
routes the hot and cold surfaces and the four state-code surfaces through
target-specific lookup literals. The executable fixture binds every redirected
lookup and checks pass-through calls using the original table and axis operands.
The stock CAN completion ISR remains the tail-call target. Mailbox 26 carries
payloads, and mailbox 31 accepts control commands.

The on-request service `0xA0` mode `0x01` tests RAM across the runtime window.
For each tested word the stock routine masks ordinary interrupts, writes the
test patterns, and restores the original on success and on either mismatch
path before unmasking. The 1ME3B routine uses the same sequence across its
runtime allocation. The 1EK7A application NMI leaf at `0x0002EE9C` accesses
the interrupted stack, `SYSCR1`, `SYSCR2`, and `DMAOR`. The resolved DMA
configuration writes target channel 2. The executable patch fixtures cover
their declared simulator contexts. NMI stack depth, state restoration after an
asynchronous reset, and the live DMA channel 3 configuration remain hardware
validation questions.

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
(`uv run kb show diamond-macaque/ram`). The knock branch field reads the
target direct-difference inhibit state in its role, and the capture moves the
bits of the knock branch and LTFT neutral control bytes into the bits that the
wire contract decodes. The profile also binds both SUM16 regions and both runtime SUM/XOR
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
the combined Map Switching and CAN telemetry write ranges.
It conservatively preserves the disjoint audit candidates `0x1FE00`,
`0x1FFFE`, and `0x1FFFF`. The exported 32-bit load query has no exact match for
`0x1FE00`; its use remains unclassified, and absence of a match does not
establish absence of runtime access.

A full instruction and p-code RAM audit found no stock access to the claimed RAM
range. These static results establish software ownership only; JK78C remains
`UNTESTED` on bench and vehicle hardware.

## Rolling Launch profile

Without `--profile`, every target uses the built-in `observe` profile with
every map disabled. It is a valid disabled record, not a hardware test
profile. `make preflash` refuses a `hold` profile with an enabled map while
the Rolling Launch layout declares no hold actuator. The relocated targets
carry Map Switching and CAN telemetry. A separate local TOML file of
profile schema 4 selects the mode, the enabled maps, and every Rolling Launch
field on a Rolling Launch-capable family. The values below show the format and
are not recommended settings:

```toml
schema_version = 4
rom = "sh7058_7mfkavn86"
name = "launch-maps-1-3"

[rolling_launch]
mode = "hold"
enabled_maps = [1, 3]
coolant_min = 10
coolant_max = 220
min_speed = 200
max_speed = 1200
min_rpm_native = 160
min_pedal = 3
target_speed_offset = 0
window_width = 40
window_top = 20
u_rate_limit = 50
integrator_limit = 500
abort_above = 150
abort_below = 100
run_timeout_ticks = 781
rearm_ticks = 98
speed_frame_age_limit = 10
launch_rpm_native = [400, 400, 360, 400, 400]
launch_speed_threshold = 30
launch_soft_width_native = [0, 0, 16, 0, 0]
integral_gain = [0, 0, 2, 0, 0]
max_trim_rpm = [0, 0, 10, 0, 0]
max_trim_speed = [0, 0, 20, 0, 0]
floor_command = [0, 0, 120, 0, 0]

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

The accepted mode names are `observe` and `hold`. `enabled_maps` uses one-based
map numbers. `launch_rpm_native`, `launch_speed_threshold`,
`launch_soft_width_native`, `integral_gain`, `max_trim_rpm`,
`max_trim_speed`, and `floor_command` are map-slot fields: a scalar sets all
five maps, and a list of five values sets Maps 1 through 5 in order.
`max_trim_rpm`, `max_trim_speed`, and `floor_command` are optional and default
to 0; every other field is mandatory. Unknown fields are rejected; the single
`max_trim` field is refused as ambiguous, and the RPM-ceiling fields and
profile schemas 1 through 3 have no automatic conversion. Every slot must
satisfy its field contract whether or not its map is enabled, and the
resulting 102-byte configuration must pass the independent fail-closed model.
The builder writes the efficiency table from F of the image it builds; the
table is not a profile field.
`rom` may name an applicable registered family or one exact member. Enabled
Rolling Launch settings require a member of `sh7058_7mfkavn86`. A relocated
target uses the disabled record and applies its CAN telemetry settings.
Speeds and the window and abort fields are km/h*10; `min_speed = 0` and
`max_speed = 0` disable their side of the activation range, and
`min_pedal = 0` disables the pedal-position activation gate. RPM fields are
native counts of 12.5 RPM, `launch_speed_threshold` is km/h*10, the trims and
the floor are APC command counts, the controller fractions are thousandths,
the timers count runtime ticks, and `rolling-launch.md` states the regulators
and the contract of every field.
Concrete profiles remain local and are not versioned.

### Editor changes to map slots

RomRaider and TunerPro expose each map's launch speed threshold in km/h, the
launch RPM and the soft width in RPM, the RPM trim and the speed-hold trim in
degrees, the integral gain, and the timing floor in degrees ATDC. A zero soft
width is the hard two-step. The floor display is `floor_command - 110`; a
negative ATDC value is before TDC. The unsigned stored gain has the runtime's
signed-positive limit of 32767. Each trim is limited to 0..40 degrees. The
efficiency table is hidden from the editors. A map-slot edit leaves the table
current.

After editing the F table, normalize the image into a new file:

```bash
uv run python patches/refresh_rolling_launch.py tmp/edited.bin \
  --output tmp/ready.bin
make preflash INPUT=tmp/ready.bin ROM=JK08A
```

The command rewrites only the efficiency table from F of the edited image and
the checksum fields. It rejects invalid independent settings, unknown or
partial runtimes, illegal calibration changes, and a result that does not
rebuild byte for byte. It never replaces the input. The image remains
`UNTESTED`; the clean-commit, exact-commit CI and executable checks of preflash
remain mandatory. A direct editor save of F with a stale table is refused by
preflash with the normalization command.

The efficiency table covers every retard count 0..40 of the F axis, so no
slot field depends on it, and an editor never computes it. Calibration
extraction and `rom-calibrate` preserve all logical map-slot settings and
derive the table again after F-table calibration bytes are applied.

Rolling Launch and CAN telemetry settings edited in a built image through an
editor travel in the extracted profile of the calibration transfer. Application
of a calibration file refuses a build whose configuration records differ from
the extracted settings and names the differing components, such as
`rolling_launch` or `can_telemetry`. Disabling Map 1 Rolling Launch through an
editor therefore carries over only through the extracted profile or an explicit
replacement. On a Rolling Launch layout with the spark-cut hold actuator, the
application also refuses a calibration that sets the misfire-latch byte
`ROM8[0x00008C2E]` to the actuator marker `0x01`, and `make preflash` refuses
such an image through its rebuild.

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
1ME3B and 1EK7A write mailbox 26 at `0x00009830` and `0x000099A8`
respectively. The `mailbox_record_address/tbl`
symbols own these addresses and the `can_telemetry` targets project them to
`rom-address-profiles.toml`; the 1ME3B control mailbox 22 and preserved stock
mailbox 31 are specified in `can-telemetry.md`.
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
family, `0x000E1503` for 8MFK, `0x0001F803` for JK78C, `0x00134E03` for
1ND, `0x0013DE03` for 1ME3B, and `0x00164E03` for 1EK7A. The `can_telemetry` targets own these
addresses; `runtime_targets.py` renders the selected configuration.

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
values, write-set counts, and exact instruction audit counts. Manifest schema 5
records both the series and exact member. Every new image is marked
`hardware_status=UNTESTED`; software verification does not make it eligible for
flashing without target-specific bench and vehicle gates.

Manifest input and output paths are resolved absolute paths. Relative and
absolute spellings of the same paths produce byte-identical manifests.

The `input` section holds the path, SHA-256, and checksum values of the stock
image. `output.configuration` contains the Rolling Launch and CAN telemetry
records, their decoded settings, the Rolling Launch efficiency table of the
output as `efficiency_hex`, and the telemetry mailbox record; a target
without Rolling Launch has `null` in its place. The `profile` section describes
the selected output profile.
