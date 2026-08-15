# ROM atlas generator

`romviz` builds a self-contained interactive address-space atlas from the
repository evidence model. The generated HTML places structural functions,
reviewed semantics, maps, axes, diagnostic records, custom patch allocations,
hooks, and checksum domains on one flash address axis.

The output contains no ROM bytes. It includes per-page entropy and erased-byte
ratios derived from the stock image, object metadata from repository sources,
and patch ranges from declared manifests.

## JK08A build

```bash
make romviz
```

The root target always rebuilds `tmp/romviz/jk08a-rom-atlas.html`. The HTML is
self-contained and opens directly from the filesystem. The underlying command
is available for direct tool development:

```bash
uv run python tools/romviz/build.py JK08A \
  --output tmp/romviz/jk08a-rom-atlas.html
```

The interface supports mouse-wheel and trackpad-pinch zoom, pointer dragging,
trackpad horizontal panning, whole-ROM navigation, layer filters, reviewed-only
function filtering, text and address search, object details, and related-address
jumps. Custom per-slot map copies appear both as map-switching allocations and
as maps in the calibration lane. The URL fragment records the active ROM,
viewport, and selected object for reproducible local links.

## Source model

The JK08A manifest is `roms/JK08A.toml`. It references existing evidence rather
than copying object addresses into visualization code.

| Layer | Source |
|---|---|
| Stock image identity and size | `rom-images/roms.csv` and the SHA-locked image |
| Function starts and body byte counts | machine-local Ghidra `funcs.csv` export |
| Reviewed function semantics | `defs/JK08A.funcs.csv` |
| Map ranges and semantics | generated `defs/JK08A.maps.csv` projection |
| Axis semantics and inferred extents | `defs/JK08A.axes.csv`, `defs/JK08A.interp.csv`, and map geometry |
| Diagnostic bindings and DTC storage | `defs/JK08A.diagnostic-bindings.csv` and `defs/JK08A.dtc.csv` |
| Definition-controlled byte patches | `defs/JK08A.overrides.toml` |
| Composed runtime layouts | map-switching, Rolling Launch, and CAN telemetry layout manifests |
| Checksum fields and domains | `patches.jk08a_checksums` constants |

Ghidra exports provide exact function entry addresses and body byte counts. The
export does not preserve discontiguous body ranges, so the atlas draws each
function as a contiguous byte-count envelope anchored at its entry. Reviewed
objects remain distinguishable from structure-only functions. Unknown extents
are point-sized and identified in the details view.

Patch status is explicit. `composed` marks ranges owned by the current unified
builder, `available` marks reversible definition controls, and `candidate`
marks declared allocations that are not part of the composed builder layout.

## Adding another ROM

Add `tools/romviz/roms/<ROM>.toml` with the same schema and point each field at
that ROM's image registry entry, reviewed sources, structural export, patch
manifests, and checksum module. No interface changes are required. Multiple
ROMs can be embedded in one atlas:

```bash
make romviz ROMS="JK08A <ROM>" \
  ROMVIZ_OUTPUT=tmp/romviz/vq-rom-atlas.html
```

An optional patch source may be absent without failing the build. Required
evidence, image identity, object bounds, unsupported map geometry, duplicate
object IDs, and unknown patch source kinds fail the build.

## Verification

```bash
node --check tools/romviz/app.js
uv run pytest -q tools/romviz/tests
```

Generated atlas files belong under ignored `tmp/` or another explicit output
location and are not repository evidence.
