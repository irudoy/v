# ECU definition sources and projections

`defs/` contains canonical annotation layers, cross-ROM correspondence
registries, generated tuning-editor definitions, and pinned public
reference-definition submodules. Technical facts are separated from editor
presentation and generated output.

## Authority model

| File | Responsibility | Edit directly |
|---|---|---|
| `JK08A.interp.csv` | Interpolation entries and recovered geometry | yes |
| `JK00D.interp.csv` | JK00D interpolation entries and recovered geometry | yes |
| `JK78C.interp.csv` | SH7058 VQ37 interpolation entries and recovered geometry | yes |
| `1ND0A.interp.csv` | SH7059 1ND interpolation entries and recovered geometry | yes |
| `1ME3B.interp.csv` | SH7059 1ME3B fused interpolation leaves and recovered geometry | yes |
| `JK08A-JK00D.interp-correspondence.csv` | Reviewed cross-family interpolation wrapper pairs | yes |
| `JK08A-JK78C.interp-correspondence.csv` | Reviewed VQ25-to-VQ37 interpolation wrapper pairs and explicit source-only contracts | yes |
| `JK08A-1ND0A.interp-correspondence.csv` | Reviewed cross-generation interpolation wrapper pairs and explicit source-only contracts | yes |
| `JK08A.findings.csv` | Map semantics, role, scale, confidence, and evidence | yes |
| `JK08A.axes.csv` | Axis semantics, scale, confidence, and evidence | yes |
| `JK08A.funcs.csv` | Function semantics, callable contracts, and evidence | yes |
| `JK08A.vars.csv` | RAM and peripheral semantics and evidence | yes |
| `JK08A.diagnostic-bindings.csv` | Reviewed firmware-to-diagnostic claims | yes |
| `JK08A.tuning-signals.toml` | Current and missing tuning-observation coverage | yes |
| `JK08A.dtc.csv` | Exact DTC descriptor and attribute edit ranges | yes |
| `JK00C.dtc.csv`, `JK00D.dtc.csv`, `JK78C.dtc.csv`, `1ND0A.dtc.csv`, `1ND3B.dtc.csv`, `1ME3B.dtc.csv` | Relocated DTC edit ranges read from the target image | no, regenerate |
| `JK08A.overrides.toml` | Editor presentation, visibility, categories, views, switches, and checksum declarations | yes |
| `rom-inheritance.toml` | Verified target-to-canonical annotation inheritance | yes |
| `definition-projections.toml` | SHA-bound relocated definition targets, capability gates, switches, and evidence | yes |
| `JK08A-*.definition-addresses.csv` | Reviewed source-to-target map and axis addresses | yes |
| `vq37-native-fuel-cut.toml` | Exact VQ37 coordinator, state-machine, pointer, cap, curve, and RAM bindings | yes |
| `vq37-native-tables.toml` | Exact VQ37 calibration tables and axes that have no canonical source, with stock value and accessor bindings and declared absent roles | yes |
| `rom-identities.toml` | Target-specific RomRaider and TunerPro identity metadata | yes |
| `JK08A.maps.csv` | Catalog ledger projected from Memgraph | no, regenerate |
| `<ROM>.xml` | Target-specific RomRaider definition projection | no, regenerate |
| `<ROM>.xdf` | Target-specific TunerPro XDF projection | no, regenerate |

The exact ROM supplies every map and axis value during ingestion. Handwritten
files must not duplicate image values. The graph is a reproducible relationship
projection and does not replace these tracked sources.

## Canonical exact-code layer

JK08A is the only live annotation and presentation source for its exact-code
family. `rom-inheritance.toml` binds JK00A, JK03A, and JK03B only after
verifying both image hashes and the declared executable-code ranges. An
inherited ROM keeps its own stock image and value measurements. It does not
receive copied semantic CSV or presentation TOML files. Its XML/XDF outputs use
the canonical structure with the selected stock image and target identity.

The source model and exact image are validated before every complete ingest.
See `../tools/map-analysis-pipeline.md` and
`../tools/memgraph/README.md`.

## Cross-family correspondence

JK00C and JK00D use a distinct calibration layout and cannot inherit addressed
JK08A claims. `JK08A-JK00D.interp-correspondence.csv` binds each reviewed
source wrapper to its relocated JK00D homolog. The registry covers every
JK08A wrapper and permits target-only JK00D wrappers. Pair validation requires
equal geometry, storage type, axis types, and interpolation family outside the
addresses.

`definition-projections.toml` binds JK00C and JK00D to exact source and target
image hashes. Its per-target correspondence CSV relocates every visible stock
map and required axis with explicit status and evidence. A source map without
a unique target homolog is recorded as unsupported instead of being guessed.
JK00C correspondences compose reviewed JK08A-to-JK00D operands only through
unique exact or normalized JK00D-to-JK00C function matches. The generator
validates the resulting target geometry and stock bytes before emission.

`tools/rom_correspondence.py` combines this registry with machine-local Ghidra
function signatures, call ordinals, and resolver censuses. Its function and
entity outputs are deterministic review candidates. They do not establish
semantic inheritance by themselves; promoted target claims remain explicit
tracked evidence.

An interpolation correspondence may use the six-column format with `status`
set to `mapped` or `unsupported`. An unsupported row must identify the source
kernel and wrapper, leave both target address fields empty, and cite a complete
target-library census. This records a real source-only interpolation contract
without inventing a target pair. Target-only wrappers remain in the target
interpolation registry and do not need correspondence rows.

The SH7059 1ND library retains the same interpolation mechanics but adds two
mixed-axis wrappers and an alternate-finisher 8x8 byte wrapper while omitting
the standard-finisher 16x16 byte wrapper used by JK08A.
`JK08A-1ND0A.interp-correspondence.csv` records every source contract,
including the explicit unsupported entry, while `1ND0A.interp.csv` retains the
three target-only contracts.

JK78C contains the same 36 interpolation contracts as 1ND0A at SH7058
addresses. Its 33 mapped JK08A contracts, one explicit source-only contract,
and three VQ37-only contracts are recorded independently. Equal wrapper bytes
and reviewed library order establish the contract registry; they do not by
themselves establish map semantics or equal calibration geometry.

`1ME3B.interp.csv` registers a library that fuses wrapper, kernel, and axis
search into one leaf per access, so every row names the leaf as both `kernel`
and `wrapper`. Its 34 rows are read from the leaf code and reproduce the 1ND0A
contract vocabulary without any shared code; seven rows are byte-identical
copies of another leaf with their own callers. The census runs
`ResolveAccessors.java` in `fused` mode per row. No interpolation
correspondence registry exists for it: the contracts are equal in geometry,
storage, and axis types, but pairing them with 1ND0A entries requires a
reviewed accessor-level comparison rather than equal wrapper bytes. That
comparison is recorded per map and axis in
`JK08A-1ME3B.definition-addresses.csv`, which names the leaf beside each
target address.

`JK08A-JK78C.definition-addresses.csv` projects 29 visible source-map roles to
31 JK78C tables, including explicit bank variants, and records thirteen source
maps as unsupported. The unsupported entries cover removed dispatcher slots,
the three exhaust-cam surfaces and the four standstill exhaust-VTC override
constants of the removed exhaust valve timing subsystem, and target
algorithms whose table geometry differs. Thirteen reviewed axis
pairs complete the emitted geometry. The JK78C registry enables native
RomRaider checksum handling, fourteen-family target-specific Map Switching,
Rolling Launch, and the CAN telemetry startup switch from the validated runtime
profile. The target-native fuel-cut projection adds the adjacent activation and
release caps plus the two independent eight-point curves used by the exact
190-byte state machine. The target-native table registry adds the two
alternate selector arms and the VVEL target set modelled in `JK78C.vvel.md`:
sixteen duration, intake-CVTC, shaft-angle, and monitor tables with fifteen
exact axes, each bound to the literal pool of its reading function. The
XML/XDF files expose editor controls; the unified builder remains responsible
for runtime composition and complete checksum closure.

`JK08A-1ND.definition-addresses.csv` projects the same reviewed VQ37 semantic
set to the SH7059 1ND layout. It records 31 target maps, thirteen axes, and
thirteen explicitly unsupported source maps. The projection is established from
reviewed JK78C-to-1ND0A structural functions, exact storage, interpolation-call
order, selector branches, and target literals. 1ND3B reuses the address layout
because all address-bearing executable code is byte-identical to 1ND0A, while
its identity, stock calibration values, and image hash remain independent.
Both 1ND definitions expose target-specific Map Switching storage and the CAN
telemetry startup switch. The project checksum implementation covers their six
checksum fields, but native RomRaider checksum metadata cannot represent the
complete layout. Their target-native fuel-cut maps, Rolling Launch controls,
and exact scheduler-to-coordinator bindings are shared at the same addresses,
while each definition remains bound to its independent stock image hash. The
1ND VVEL registry carries fifteen target-native tables and fourteen axes at
shared addresses: the 1ND resolver indexes the hot-intake idle surfaces by two
temperature-coded bytes instead of engine speed and torque, reads a mode 14
surface that JK78C replaces with a constant, and has no floor curves and no
demand axis, which the registry declares as absent roles.

`JK08A-1ME3B.definition-addresses.csv` projects the same reviewed VQ37
semantic set to the fused-library 1ME3B image. It records 27 target maps,
thirteen axes, and sixteen explicitly unsupported source maps. No code relocates
from any modelled ROM, so every row is established through the 1ND0A
structural export: exact-bytes or normalized-shape function pairs that read
the target address at the same call ordinal, target functions that reproduce
the 1ND0A reader's operand set, selector arms, and call order, the fused leaf
whose contract equals the 1ND0A wrapper, exact target storage, and target
literals. The unsupported rows are the thirteen VQ37 rows and the three canonical
ignition surfaces: the target ignition coordinator `0x0797CC` carries only its
mode-selected surfaces and no target function reproduces the gated stock-inert
trio path of 1ND0A `0x074D98`. The projection declares checksum support with
native RomRaider metadata over the `sh7059_1me3b` layout and no runtime
allocation: Map Switching, Rolling Launch, and the CAN telemetry switch are
absent from the definition. The target-native table registry adds the two
alternate selector arms and the VVEL target set to the 1ME3B definition:
eighteen tables and fifteen axes, each bound to an undisplaced literal-pool
word of its reading function. The 1ME3B resolver `0x062FAC` carries the JK78C
role set, with the JK78C engine-speed and torque axes on the hot-intake idle
surfaces, two floor curves over the demand axis, and the constant 50.0 in the
mode 14 pair. It reads the shaft-angle conversion and the cold pair inline and
leaves the throttled pair to `0x063534`, which publishes the throttled duration
as the curve value or as a stepped approach to it from 50.0.

## Evidence specifications

- `JK08A.notes.md` is a compact routing and evidence index, not a batch journal.
- `JK08A.fuel.md` models the main fuel calculation, calculated pulse words, and
  crank-angle placement of the injection pulses.
- `JK08A.load.md` separates the internal normalized-BFS map coordinate from
  J1979 Calculated Load and records their exact producers and scheduling.
- `JK08A.maf-range-monitor.md` models the paired P0101/P010B range-performance
  monitor, its RPM-dependent factor composition, stock selector, and captured
  diagnostic context.
- `JK08A.cvtc.md` models the intake- and exhaust-CVTC target surfaces, exact
  interpolation, coolant selection, downstream target conditioning, and log
  replay.
- `JK08A.dfco.md` models deceleration fuel cut.
- `JK08A.fuel-inhibit.md` models the complete fuel-output inhibit arbitration.
- `JK08A.limiters.md` models the main, stationary, and request limiter paths.
- `JK08A.request-conditioning.md` models the paired zero-surface request
  stages, live `0..800` normalization endpoints, and stock-disabled centered
  correction surface.
- `JK08A.throttle-control.md` models the complete accelerator-pedal, shared
  request, target, feedback-regulator, and ATU-II PWM path.
- `JK08A.ignition-state.md` models the cold, high-octane, and high-detonation
  timing-state surfaces, their masked fields, selector, and knock-state path.
- `JK08A.rpm-drop-state.md` models the RPM/12.5 source, positive RPM-drop
  filter, Boolean calibration gate, scheduled class, and DFCO floor selection.
- `JK08A.knock-detection.md` models the active per-channel knock-threshold
  lookup, evaluator outputs, and the unreferenced neighboring calibration bank.
- `JK08A.ignition-output.md` models the final timing and APC output boundary.
- `JK08A.start-signal-temperature-selector.md` models the computed START
  SIGNAL, battery-voltage acquisition, and the coolant temperature latched at
  engine start.
- `JK08A.diagnostics.md` models diagnostic publication and monitor boundaries.
- `JK08A.tuning-telemetry.md` defines schema-2 custom-CAN coverage, stock-CAN
  context, closed-loop observation groups, and measurements that still require
  new instrumentation or external equipment.
- `JK08A.definition-presentation.md` defines editor naming, category taxonomy,
  validation-copy terminology, and the non-tuning visibility boundary.
- `JK08A.can.md` models the exact HCAN1 mailbox table, stock transmit pipeline,
  payload boundaries, and safe extension mailbox.
- `JK78C.can.md` models the two exact HCAN controllers, the private-bus
  mailbox table, receive signal placement, transmit composition, and the
  calibration boundary of the private bus.
- `JK78C.vvel.md` models the VVEL target task, the fifteen-mode target
  selector, the exact sensor and diagnostic bindings of the selector inputs,
  the MAP and brake-booster pressure channel, and the unit boundary of the
  target surfaces.

These documents explain complete relationships and safety boundaries. Addressed
claims and evidence remain in the CSV layer rather than being copied into prose.

## Generated definitions

`tools/mapkit/emit_def.py` resolves the selected ROM through either exact-code
inheritance or a SHA-bound relocated definition projection. It reads the
canonical live graph projection, applicable DTC manifest,
`JK08A.overrides.toml`, `rom-identities.toml`, the selected exact stock image,
and current patch layout manifests. It renders one target-specific XML/XDF
pair from a single in-memory model. The `all` mode renders every identity
registered in `rom-identities.toml`; it stages the full set and leaves existing
outputs unchanged if any target fails.

```bash
make defs-generate
```

Use `make defs-generate DEFS_ROM=JK00A` to regenerate only one target. Canonical
ledgers are derived independently from the registered inheritance sources. The
generated RomRaider identity intentionally omits the optional `flashmethod`
field. A dump tool or a community definition does not establish a validated
flashing path for this ECU family.

The generator validates ROM identity, exact inheritance or projection hashes,
map geometry, scaling, visibility, DTC stock bytes, and every target capability
enabled in `definition-projections.toml`. The `checksum` capability binds a
target to a verified project checksum layout, while `romraider_checksum`
independently controls native RomRaider checksum metadata. A visible map must
pass the definition gate. Hidden research maps remain in the graph and ledger.
Presentation text uses the explicit `{target_rom}` token where a target label
is required; source ROM labels and evidence filenames are never rewritten as
target labels.

Each definition keeps the selected ROM identity. A target with map switching
enabled uses its own stock Map 1 storage. The exact-code family derives Map 2
through Map 5 from `patches/map-switching-layout.toml`; relocated targets with
that capability use an explicit `patches/rom-address-profiles.toml` allocation,
including separate exhaust-bank families. Rolling Launch and native checksum
metadata are emitted only when their independent target capabilities are
enabled.
Neither projection creates speculative canonical graph maps or copies JK08A
calibration values into another ROM.

RomRaider and TunerPro receive equivalent calibration tables and controls in
their native formats. TunerPro does not own image checksum correction. A ROM
with a verified builder must pass the builder and checksum gates documented in
`../patches/rom-builder.md`; a definition-only target remains ineligible for
flashing.

## DTC controls

`JK08A.dtc.csv` identifies exact descriptor and associated attribute storage.
The generator validates stock bytes before creating controls. RomRaider uses
coordinated native switches for descriptor and attribute ranges. TunerPro uses
atomic individual and declared group patches. Duplicate public codes remain
separate records when the ROM contains distinct paths. No implicit all-DTC
control exists.

Every image stores its descriptors as twelve-byte records followed immediately
by one 32-bit attribute pointer per record. That pointer table is the ECU's own
attribute reference: it reproduces all 48 canonical JK08A attribute addresses
exactly. `../tools/mapkit/dtc_projection.py` therefore reads a target binding
out of the target image instead of deriving it from an offset.

A canonical record is carried to a relocated target only when exactly one target
record is byte-identical to it, which fixes group, sub-index, monitor class,
code, and trailing flag together. JK00C and JK00D carry all 48 codes; JK78C and
`1ND` carry 39, because VQ37 declares no P1422 record and none of the eight
exhaust valve timing records; 1ME3B carries 38, because it declares no P0443
record either. The exact-code members of `7MFKAVN86`
reproduce the canonical registry from their own images and share it rather than
tracking a copy.

Byte identity carries a record across a relocation that is not uniform. The
projection needs no address model: it locates the descriptor run and the pointer
table in the target image and matches records. 1ME3B is the case that separates
the two, and it also shows that this registry precedes every other analysis
layer. Its 334 descriptor records at `0x1bf58` hold the 31 codes it shares with
the 331 records of `1ND0A` at three different relocations and at index offsets
of `-1`, `0`, and `+1`, and the projection matches them without reference to the
structural export, checksum layout, or definition correspondence of the image.

The Developer Immobilizer flag is a definition-controlled data edit, not a
standalone instruction patch. Its execution path and safety boundary are in
`../patches/immo-off-developer-flag.md`.

## Reference submodules

`reference/` contains pinned public Nissan definition repositories for
comparison only:

| Path | Upstream | Role |
|---|---|---|
| `reference/Pytrex-NissanDefinitions` | `Pytrex/NissanDefinitions` | Canonical public Nissan RomRaider collection and address-free A2L vocabulary |
| `reference/a33b-NissanDefs` | `a33b/NissanDefs` | Earlier collection and VQ37VHR comparison definitions |

The submodules have no upstream license file and are not republished by this
repository; Git stores their pinned commit references. Their addresses belong
to other ECUIDs and cannot be copied to JK08A. Geometry, vocabulary, and scaling
remain candidate comparison evidence until exact target code establishes a
claim.

Initialize or update the pinned content with standard Git submodule commands.
Changing a pin is a reviewed source update and must be accompanied by the
relevant catalog and definition verification.

## Verification

```bash
uv run pytest -q tools/mapkit/tests tools/memgraph/tests
```

Definition regeneration also requires a running, current Memgraph projection.
Use alternate output paths for byte-for-byte comparison before replacing the
tracked XML and XDF. Generated file headers identify their inputs and explicitly
reject manual authority.
