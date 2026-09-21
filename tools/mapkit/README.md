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
| `defs/<target>.dtc.csv` | Relocated DTC controls projected by `dtc_projection.py` |
| `defs/JK08A.overrides.toml` | Editor names, categories, visibility, layout, scaling presentation, native switches, and the Logger parameters of lookup operands |
| `defs/JK08A.diagnostic-bindings.csv` | Reviewed diagnostic context shown in projections |
| `defs/rom-inheritance.toml` | Exact target-to-canonical source binding and SHA-256 evidence |
| `defs/definition-projections.toml` | Relocated target registry and exact image bindings |
| `defs/JK08A-*.definition-addresses.csv` | Reviewed target map and axis addresses |
| `defs/vq37-native-fuel-cut.toml` | Exact target-native VQ37 fuel-cut maps and executable bindings |
| `defs/vq37-native-tables.toml` | Exact target-native VQ37 calibration tables and axes with no canonical source, including the VVEL target set and declared absent roles |
| `defs/rom-identities.toml` | Target-specific RomRaider and TunerPro identity fields |
| Runtime layout manifests | Canonical and target-specific map-slot and Rolling Launch projections |
| `rom-images/roms.csv` | Exact source-image identity and path |

JK00A, JK03A, and JK03B inherit the canonical JK08A structural and semantic
sources. Every generated definition is bound to its own verified stock image
and target identity; calibration values are not copied into the output.
JK00C and JK00D instead use SHA-bound reviewed address projections because
their calibration and executable layouts are relocated. The projection omits
non-unique source maps explicitly and validates every emitted target map and
axis against the selected stock image.
JK78C, 1ND0A, and 1ND3B use independently reviewed VQ37 address projections.
The two SH7059 images share one address layout because their address-bearing
executable code is byte-identical, but retain independent image hashes,
identities, and stock calibration values. The JK78C definition exposes fourteen
target-specific Map Switching families and the 1ND definitions eighteen, the
four 8x8 state-code ignition surfaces included, together with the native fuel-cut cap and curve
tables, Rolling Launch controls, and CAN telemetry control from the same
validated runtime target consumed by the production builder.

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
DTC storage, presentation schema, and each capability enabled for a relocated
target before writing either projection. The registry distinguishes a verified
project checksum layout from native RomRaider metadata that maintains every
checksum field a definition entity can invalidate. `alt2` covers the runtime
XOR and SUM pair together with both primary SUM16 fields, and `alt` covers a
second runtime pair when the layout declares one. A layout domain without a
native handler is admissible only when its whole region lies below the lowest
published entity, and the generator fails when any entity falls outside the
declared regions.
Native checksum metadata, map switching, Rolling Launch, and editor switches
remain absent when the target registry does not declare their contracts.
Target-specific wording uses only the explicit
`{target_rom}` presentation token. Canonical source labels and evidence paths
are preserved verbatim.

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

`make check` runs the same audit as `--check`, which prints one status line and
fails on the same violations.

Validate the live graph model against both tracked common definition files
without writing a ROM:

```bash
uv run python tools/mapkit/validate_map_switching.py
```

Validate every relocated definition registry, stock-image hash, address bound,
and each enabled checksum or runtime capability without selecting a default
ROM:

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
- `[logparam.<operand>]` in the presentation layer declares the Logger ID and
  the axis units for one runtime lookup operand. A RomRaider axis names a
  Logger parameter in `logparam` only when code establishes its scaling, its
  scale evidence names exactly that one `indexed_by` operand without an offset,
  and its units equal the declared units. The declared IDs are parameters of
  the CAN dashboard live value feed.
- Canonical category paths use ` / ` internally. RomRaider XML renders those
  paths with its `//` hierarchy separator, while TunerPro retains flat category
  names.
- Map slots remain in their canonical functional categories and use the slot
  number in the editor name; each target retains its own ROM identity.
- `presentation.default_emit` sets default visibility, and `emit = false` hides
  a research table from editor output without removing its graph or ledger
  facts. Candidate semantic and scaling claims are labeled in generated
  descriptions; functional categories never encode confidence.
- A relocated address projection never carries `silicon` to its target: a
  hardware result holds for the measured ROM, so a reviewed target keeps
  `code` and a call-level homolog lowers `code` and `silicon` to `candidate`.
  Exact-code inheritors share the canonical claims unchanged.
- Hidden or unresolved maps remain in the graph and ledger unless their source
  facts are removed. Visibility is a presentation decision, not deletion.
- RomRaider `Overlay Log` follows a Logger parameter along an axis that names
  it in `logparam`. A relocated axis whose scaling confidence falls below
  `code`, an axis with several operands, and an axis without a recorded operand
  stay without live data. A three-dimensional table supports the overlay only
  when both of its axes name a parameter. TunerPro XDF has no counterpart and
  is unchanged by the declaration.
- DTC records are checked against the exact stock descriptor and attribute
  bytes. RomRaider receives coordinated native switches and TunerPro receives
  atomic patches for individual records and declared groups; there is no
  implicit all-DTC patch.
- The map-switching projection reuses canonical Map 1 storage and adds only the
  reserved Map 2 through Map 5 editor views declared by the current layout, and
  the Rolling Launch projection exposes only validated configuration controls.
  These editor-only copies create neither speculative canonical `Map` nodes nor
  another ROM identity.
- Generated counts are reported by the command rather than copied into this
  document.

The complete source, schema, confidence, and ingest model is defined in
`../map-analysis-pipeline.md`.
