# ROM atlas generator

`romviz` builds a self-contained interactive address-space atlas from tracked
repository evidence. A single HTML file can contain every registered stock ROM
while preserving the evidence boundary of each image.

The output contains no ROM bytes. It includes per-page entropy and erased-byte
ratios derived from each SHA-locked stock image, plus the structural functions,
reviewed semantics, definitions, diagnostics, patch allocations, hooks, and
checksum domains that are explicitly available for that ROM.

## Build

Build all flash ROMs registered in `rom-images/roms.csv`:

```bash
make romviz
```

The root target uses `ROMS=all` by default and rebuilds the ignored
`tmp/romviz/rom-atlas.html` artifact. Limit the output to an explicit selection
when needed:

```bash
make romviz ROMS="JK08A JK00C" \
  ROMVIZ_OUTPUT=tmp/romviz/selected-rom-atlas.html
```

The underlying command is available for direct tool development. An empty ROM
selection and the explicit `all` token both select the complete registry:

```bash
uv run python tools/romviz/build.py all \
  --output tmp/romviz/rom-atlas.html
uv run python tools/romviz/build.py --check
```

`all` cannot be combined with explicit ROM labels. The build fails if a flash
ROM in the image registry lacks a tracked manifest.

The interface supports mouse-wheel and trackpad-pinch zoom, pointer dragging,
trackpad horizontal panning, whole-ROM navigation, layer filters, reviewed-only
function filtering, text and address search, object details, and related-address
jumps. The URL fragment records the active ROM, viewport, and selected object
for reproducible local links.

## Evidence model

Each target has `tools/romviz/roms/<ROM>.toml`. Manifest schema version 2 keeps
stock identity mandatory and makes analysis layers independently declarable.
Tracked declared sources are strict: missing files, invalid geometry, wrong
image hashes, out-of-range objects, and unknown patch kinds fail the build.
Machine-local Ghidra exports are the documented exception and produce a warning
when unavailable. An undeclared layer remains absent and produces a visible
warning in the atlas.

| ROM family | Current atlas evidence |
|---|---|
| JK00A, JK03A, JK03B, JK08A | Exact-code JK08A function, map, axis, diagnostic, DTC, definition-control, composed-runtime, and checksum evidence with target identity |
| JK00C, JK00D | Target Ghidra structure, generated target-specific definition addresses, composed production runtime profiles, and target checksum layouts |
| 1ND0A, 1ND3B | Exact-family 1ND0A Ghidra structure, reviewed shared definition addresses, composed production runtime profiles, target identity, checksum layout, and stock-image metrics |
| JK78C | Target Ghidra structure, reviewed target definition addresses, composed production runtime profile, complete checksum layout, and stock-image metrics |
| 1ME3B | Projected DTC records and attributes read from the stock image; every other layer is undeclared and warned about |

The exact JK00A/JK03A/JK03B/JK08A family uses one canonical annotation layer
because its declared executable address ranges are byte-identical. Only the
explicit `{target_rom}` presentation token is materialized for a target;
provenance paths and source labels are preserved unchanged.

JK00C and JK00D do not inherit JK08A addresses. Their map, axis, and definition
control objects are loaded from the generated `defs/JK00C.xml` and
`defs/JK00D.xml` projections, which are backed by SHA-bound reviewed relocation
registries. Their runtime address profiles are labeled `composed` because the
production builder emits target-specific runtime payloads at those addresses.

1ND0A and 1ND3B load their generated target definitions from one reviewed
SH7059 address correspondence. Their checksum fields and domains come from the
project checksum registry. Their composed runtime profiles expose fourteen Map
Switching families, native fuel-cut caps and curves, Rolling Launch, custom CAN
telemetry, exact hooks, and the shared SH7059 allocation.

JK78C uses a target-specific SH7058 projection. Its composed runtime profile
exposes fourteen VQ37 Map Switching families, native fuel-cut caps and curves,
Rolling Launch, and custom CAN telemetry in the audited flash and RAM
allocations. The checksum layer covers both SUM16 domains and both runtime
SUM/XOR domains.

Ghidra exports provide exact function entry addresses and body byte counts. The
export does not preserve discontiguous body ranges, so the atlas draws each
function as a contiguous byte-count envelope anchored at its entry. Machine-local
exports are optional at rendering time: reviewed entries retain point extents,
and a missing structural export produces a warning.

Patch status is explicit. `composed` marks ranges owned by the current unified
builder, `available` marks reversible definition controls, and `candidate`
marks exact registered allocations that are not emitted by the production
builder for that target.

## Adding a ROM

1. Add the SHA-locked flash image to `rom-images/roms.csv`.
2. Add `tools/romviz/roms/<ROM>.toml` with schema version 2.
3. Declare only the evidence sources that are valid for the exact target.
4. Run the complete registry validation and regenerate the atlas.

```bash
uv run python tools/romviz/build.py --check
make romviz
```

No interface change or Makefile target change is required. The registry check
ensures that `all` includes the new flash ROM.

## Verification

```bash
node --check tools/romviz/app.js
uv run pytest -q tools/romviz/tests
make check
```

Generated atlas files belong under ignored `tmp/` or another explicit output
location and are not repository evidence.
