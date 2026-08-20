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
| Patch layout manifests | Common map-slot and Rolling Launch configuration projections |
| `rom-images/roms.csv` | Exact source-image identity and path |

`defs/rom-inheritance.toml` may project a canonical annotation layer onto an
exact-code target, but every target keeps its own image measurements and graph
layer.

## Paired editor definitions

Generate the canonical RomRaider XML and TunerPro XDF together:

```bash
uv run python tools/mapkit/emit_def.py JK08A
```

The optional second and third positional arguments select alternate XML and XDF
paths for a reproducibility comparison. The generator validates the exact ROM,
graph facts, definition gate, DTC storage, presentation schema, map-switching
layout, and Rolling Launch controls before writing either projection.

The generated headers identify their inputs and warn that manual changes do not
survive regeneration. Change the tracked source layer, ingest the ROM, and run
the generator again instead of editing `defs/JK08A.xml` or `defs/JK08A.xdf`.

## Map ledger

Render the canonical review ledger from the graph:

```bash
uv run python tools/maps/build_tracker.py JK08A
```

The default output is `defs/JK08A.maps.csv`. An inherited target such as JK03A
requires an explicit temporary output path because no copied ledger is stored
under `defs/`. The ledger contains measured values, structural relationships,
reviewed semantics, provenance confidence, and diagnostic context; it does not
own any of those facts.

## Projection verification

Validate the live graph model against both tracked common definition files
without writing a ROM:

```bash
uv run python tools/mapkit/validate_map_switching.py
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
- ROM identity and every addressed stock value are validated before emission.
- XML and XDF are rendered from the same in-memory model in one invocation.
- Canonical category paths use ` / ` internally. RomRaider XML renders those
  paths with its `//` hierarchy separator, while TunerPro retains flat category
  names.
- Map slots remain in their canonical functional categories and use the slot
  number in the editor name; no separate ROM identity is created.
- Hidden or unresolved maps remain in the graph and ledger unless their source
  facts are removed. Visibility is a presentation decision, not deletion.
- Generated counts are reported by the command rather than copied into this
  document.

The complete source, schema, confidence, and ingest model is defined in
`../map-analysis-pipeline.md`.
