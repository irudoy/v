# ECU definition sources and projections

`defs/` contains the canonical JK08A annotation layer, generated tuning-editor
definitions, and pinned public reference-definition submodules. Technical facts
are separated from editor presentation and generated output.

## Authority model

| File | Responsibility | Edit directly |
|---|---|---|
| `JK08A.interp.csv` | Interpolation entries and recovered geometry | yes |
| `JK08A.findings.csv` | Map semantics, role, scale, confidence, and evidence | yes |
| `JK08A.axes.csv` | Axis semantics, scale, confidence, and evidence | yes |
| `JK08A.funcs.csv` | Function semantics, callable contracts, and evidence | yes |
| `JK08A.vars.csv` | RAM and peripheral semantics and evidence | yes |
| `JK08A.diagnostic-bindings.csv` | Reviewed firmware-to-diagnostic claims | yes |
| `JK08A.dtc.csv` | Exact DTC descriptor and attribute edit ranges | yes |
| `JK08A.overrides.toml` | Editor presentation, visibility, categories, views, switches, and checksum declarations | yes |
| `rom-inheritance.toml` | Verified target-to-canonical annotation inheritance | yes |
| `JK08A.maps.csv` | Catalog ledger projected from Memgraph | no, regenerate |
| `JK08A.xml` | RomRaider definition projection | no, regenerate |
| `JK08A.xdf` | TunerPro XDF projection | no, regenerate |

The exact ROM supplies every map and axis value during ingestion. Handwritten
files must not duplicate image values. The graph is a reproducible relationship
projection and does not replace these tracked sources.

## Canonical exact-code layer

JK08A is the only live annotation and presentation source for its exact-code
family. `rom-inheritance.toml` binds another target only after verifying both
image hashes and declared executable-code ranges. An inherited ROM keeps its
own Ghidra export, value measurements, graph layer, and exact-ROM diagnostic
bindings. It does not receive copied CSV, ledger, XML, or XDF files.

The source model and exact image are validated before every complete ingest.
See `../tools/map-analysis-pipeline.md` and
`../tools/memgraph/README.md`.

## Evidence specifications

- `JK08A.notes.md` is a compact routing and evidence index, not a batch journal.
- `JK08A.fuel.md` models the main fuel calculation and calculated pulse words.
- `JK08A.dfco.md` models deceleration fuel cut.
- `JK08A.fuel-inhibit.md` models the complete fuel-output inhibit arbitration.
- `JK08A.limiters.md` models the main, stationary, and request limiter paths.
- `JK08A.ignition-output.md` models the final timing and APC output boundary.
- `JK08A.diagnostics.md` models diagnostic publication and monitor boundaries.
- `JK08A.can.md` models the exact HCAN1 mailbox table, stock transmit pipeline,
  payload boundaries, and safe extension mailbox.

These documents explain complete relationships and safety boundaries. Addressed
claims and evidence remain in the CSV layer rather than being copied into prose.

## Generated definitions

`tools/mapkit/emit_def.py` reads the live graph projection, exact ROM,
`JK08A.dtc.csv`, `JK08A.overrides.toml`, and current patch layout manifests. It
renders `JK08A.xml` and `JK08A.xdf` from one in-memory model.

```bash
uv run python tools/mapkit/emit_def.py JK08A
uv run python tools/maps/build_tracker.py JK08A
uv run python tools/mapkit/validate_map_switching.py
```

The generator validates ROM identity, map geometry, scaling, visibility, DTC
stock bytes, map-slot layout, and Rolling Launch controls. A visible map must
pass the definition gate. Hidden research maps remain in the graph and ledger.

The common definition keeps the unchanged JK08A identity. Map 1 uses canonical
stock storage; Map 2 through Map 5 are editor projections of reserved addresses
declared by `patches/map-switching-layout.toml`. Rolling Launch exposes only the
validated configuration controls declared by its layout. Neither projection
creates speculative canonical graph maps.

RomRaider and TunerPro receive equivalent calibration tables and controls in
their native formats. TunerPro does not own image checksum correction; complete
ROM output must pass the builder and checksum gates documented in
`../patches/rom-builder.md`.

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
