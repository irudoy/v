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
| `JK08A.overrides.toml` | Editor presentation, visibility, categories, views, switches, and checksum declarations | yes |
| `rom-inheritance.toml` | Verified target-to-canonical annotation inheritance | yes |
| `definition-projections.toml` | SHA-bound relocated definition targets, capability gates, switches, and evidence | yes |
| `JK08A-*.definition-addresses.csv` | Reviewed source-to-target map and axis addresses | yes |
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

`JK08A-JK78C.definition-addresses.csv` projects 29 visible source-map roles to
31 JK78C tables, including explicit bank variants, and records five source
maps as unsupported. The unsupported entries cover removed dispatcher slots
and target algorithms whose table geometry differs. Thirteen reviewed axis
pairs complete the emitted geometry. The JK78C registry enables native
RomRaider checksum handling, target-specific Map Switching storage, and the CAN
telemetry startup switch from the validated runtime profile. Rolling Launch is
disabled because the required target fuel-cut actuator is not localized. The
XML/XDF files expose editor controls; the unified builder remains responsible
for runtime composition and complete checksum closure.

`JK08A-1ND.definition-addresses.csv` projects the same reviewed VQ37 semantic
set to the SH7059 1ND layout. It records 31 target maps, thirteen axes, and five
explicitly unsupported source maps. The projection is established from
reviewed JK78C-to-1ND0A structural functions, exact storage, interpolation-call
order, selector branches, and target literals. 1ND3B reuses the address layout
because all address-bearing executable code is byte-identical to 1ND0A, while
its identity, stock calibration values, and image hash remain independent.
Both 1ND definitions expose target-specific Map Switching storage and the CAN
telemetry startup switch. The project checksum implementation covers their six
checksum fields, but native RomRaider checksum metadata cannot represent the
complete layout. Rolling Launch remains disabled because the required target
fuel-cut actuator is not localized.

## Evidence specifications

- `JK08A.notes.md` is a compact routing and evidence index, not a batch journal.
- `JK08A.fuel.md` models the main fuel calculation and calculated pulse words.
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
  SIGNAL, battery-voltage acquisition, and selected-temperature sentinel.
- `JK08A.diagnostics.md` models diagnostic publication and monitor boundaries.
- `JK08A.tuning-telemetry.md` defines schema-2 custom-CAN coverage, stock-CAN
  context, closed-loop observation groups, and measurements that still require
  new instrumentation or external equipment.
- `JK08A.definition-presentation.md` defines editor naming, category taxonomy,
  validation-copy terminology, and the non-tuning visibility boundary.
- `JK08A.can.md` models the exact HCAN1 mailbox table, stock transmit pipeline,
  payload boundaries, and safe extension mailbox.

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
