# Definition and ledger projection

`tools/mapkit/` renders reviewed firmware knowledge for tuning editors and
provides small read-only inspection utilities. `tools/maps/build_tracker.py`
renders the catalog ledger. These outputs are generated projections and must
not be edited by hand.

## Inputs

| Input | Responsibility |
|---|---|
| Memgraph ROM layer | Measured map geometry, accessors, axes, values, and projected reviewed claims |
| `defs/JK08A.findings.csv` | Canonical map semantics and map-specific evidence |
| `defs/JK08A.axes.csv` | Canonical axis semantics and scaling evidence |
| `defs/JK08A.interp.csv` | Registered interpolation families and resolver census contract |
| `defs/JK08A.dtc.csv` | Addressed DTC descriptor and attribute controls |
| `defs/JK08A.overrides.toml` | Editor names, categories, visibility, layout, scaling presentation, and native switches |
| `defs/JK08A.diagnostic-bindings.csv` | Reviewed diagnostic context shown in projections |
| `defs/rom-inheritance.toml` | Exact target-to-canonical source binding and SHA-256 evidence |
| `defs/definition-projections.toml` | Relocated target registry and exact image bindings |
| `defs/JK08A-<ROM>.definition-addresses.csv` | Reviewed target map and axis addresses |
| `defs/rom-identities.toml` | Target-specific RomRaider and TunerPro identity fields |
| Patch layout manifests | Common map-slot and Rolling Launch configuration projections |
| `rom-images/roms.csv` | Exact source-image identity and path |

JK00A, JK03A, and JK03B inherit the canonical JK08A structural and semantic
sources. Every generated definition is bound to its own verified stock image
and target identity; calibration values are not copied into the output.
JK00C and JK00D instead use SHA-bound reviewed address projections because
their calibration and executable layouts are relocated. The projection omits
non-unique source maps explicitly and validates every emitted target map and
axis against the selected stock image.

## Paired editor definitions

Generate every registered RomRaider XML and TunerPro XDF pair:

```bash
make defs-generate
```

The all-target mode obtains its ordered target set from
`defs/rom-identities.toml`, reuses each canonical graph projection, and stages
the complete output set before replacing tracked artifacts. A failure for one
target leaves every existing XML/XDF unchanged. Use
`make defs-generate DEFS_ROM=<ROM>` to generate only one target while retaining
the independently selected canonical ledger. The lower-level script's optional
second and third positional arguments select alternate XML and XDF paths for a
reproducibility comparison.
The generator validates the selected ROM identity, inheritance or relocated
projection hashes, canonical graph facts, definition gate, applicable target
DTC storage, presentation schema, map-switching layout, and Rolling Launch
controls before writing either projection. Target-specific wording uses only
the explicit `{target_rom}` presentation token. Canonical source labels and
evidence paths are preserved verbatim.

The generated headers identify their inputs and warn that manual changes do not
survive regeneration. Change the tracked canonical source layer or target
identity and run the generator again instead of editing generated XML/XDF.

## Map ledger

Render the canonical review ledger from the graph:

```bash
uv run python tools/maps/build_tracker.py JK08A
```

With no selector, the tracker regenerates one ledger for every unique canonical
source derived from the registered targets. A single canonical ROM writes
`defs/<ROM>.maps.csv`. An inherited target such as JK03A requires an explicit
temporary output path because no copied ledger is stored under `defs/`. The
ledger contains measured values, structural relationships, reviewed semantics,
provenance confidence, and diagnostic context; it does not own any of those
facts.

## Projection verification

Audit the canonical editor names, functional taxonomy, and explicit non-tuning
exclusions without requiring a running graph:

```bash
uv run python tools/mapkit/presentation_audit.py
```

Validate the live graph model against both tracked common definition files
without writing a ROM:

```bash
uv run python tools/mapkit/validate_map_switching.py
```

Validate every relocated definition registry, stock-image hash, address bound,
checksum layout, and target runtime layout without selecting a default ROM:

```bash
uv run python tools/mapkit/definition_projections.py --check
```

For a byte-for-byte regeneration check, emit XML and XDF into a temporary
directory and compare them with the tracked files. The full Python unit contract
also exercises XML, XDF, DTC, map-switching, and TunerPro behavior:

```bash
uv run pytest -q tools/mapkit/tests
```

## Read-only inspection

`show.py` prints maps or axes using graph geometry and exact ROM values while
keeping raw values visible beside physical scaling:

```bash
uv run python tools/mapkit/show.py JK08A 0x1495a
```

`ptrscan.py` searches the exact ROM for 16-bit and 32-bit values that may point
to an address:

```bash
uv run python tools/mapkit/ptrscan.py JK08A 0x1495a
```

Pointer-scan hits are candidates, not references. Confirm each site with the
Ghidra inspection tools documented in `../ghidra/README.md`.

`throttle_limiter.py` is a pure integer state model of stock function
`0x0007584E`. It reads the limiter calibration directly from a verified ROM and
keeps the per-RPM baseline lookup as an explicit input. Fast unit tests cover
state transitions and arithmetic boundaries; the exact-ROM p-code harness in
`../ghidra/EmulateThrottleLimiter.java` remains the independent executable
reference, including the baseline lookup and downstream target projection.

## Generator invariants

- A visible table must pass geometry, axis, scaling, and presentation gates.
- A static axis cannot overlap a recovered graph axis.
- Target ROM identity, exact inheritance ranges, DTC stock bytes, and projected
  address bounds are validated before emission.
- Relocated definitions retain canonical provenance while applying only
  explicit target-address bindings.
- XML and XDF are rendered from the same in-memory model in one invocation.
- Canonical category paths use ` / ` internally. RomRaider XML renders those
  paths with its `//` hierarchy separator, while TunerPro retains flat category
  names.
- Map slots remain in their canonical functional categories and use the slot
  number in the editor name; each target retains its own ROM identity.
- Hidden or unresolved maps remain in the graph and ledger unless their source
  facts are removed. Visibility is a presentation decision, not deletion.
- Generated counts are reported by the command rather than copied into this
  document.

The complete source, schema, confidence, and ingest model is defined in
`../map-analysis-pipeline.md`.
