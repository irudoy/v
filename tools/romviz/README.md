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
jumps. The URL fragment records the active view, ROM, viewport, and selected
object for reproducible local links.

## Architecture view

The atlas carries two views. The address map draws the flash layout of one
image. The architecture view draws the firmware itself: functional blocks, the
data flow between them, the actuator and bus endpoints, and the calculation
chains that lead from the crank events and the sensors to each command.

Stages, blocks, endpoints, chains, and meaning placements belong to `kb`.
`tools/romviz/graph_atlas.py` reads one graph snapshot under the writer lock
after its fingerprint check. Every architecture node binds an actual symbol
applicable to the selected image in its declared layout. Its meaning carries the semantic or generated name,
cross-layout symbols, statuses, and analog hints. Analogs do not join meanings
or inherit knowledge levels.
Relations retain their origins: declared links, L0 calls, and L0 accesses.
The snapshot selects an L0 call when both function addresses have declared
function symbols in its layout. This is the architecture model's binding
criterion; calls without either binding cannot form a displayed edge. The
snapshot retains all meaning bindings, cross-layout symbols, statuses, and
analogs. Each build reads the current graph under the same freshness check.
Equivalent row orders produce the same bindings, derived ownership, flows,
and edge inventories. Construction uses stable meaning and indexed-edge
orders; unordered endpoint references, analog cards, and edge evidence have
stable presentation orders. Declared chain-step and through-reference orders
retain their explicit ordinal fields.
A literal or a parameter is an address reference, distinct from an actual
load or store. No citation or analog establishes a data-flow relationship.
The details identify the home layout of shared summaries and notes when
their address references describe that layout rather than the selected one.

`defs/JK08A.architecture.toml` is the generated JK08A view, whose
`tools/romviz/architecture.py` gate binds every step either to a relation of
the generated ledgers or to a specification the step names. `make check`
reproduces the canonical inventory and rebuilds the atlas.
The command-line inventory includes explicitly placed home-layout owners
whose facts have no legacy ledger row. Their node metadata identifies the
native `kb` source. An unowned address or a symbol on another layout cannot
enter that inventory through a placement in the generated view.

The view opens on the system map: input endpoints, the block columns of every
stage, output endpoints, and the support lane below them. Opening a block shows
its functions and tables with its upstream and downstream partners. Opening a
table, signal, or function shows its neighborhood. Opening a chain draws the
calculation from the sensors to the published quantity and gives every node the
sign of the effect that an increase has on that output: a raise, a lowering, no
established sign, or paths that disagree. A dashed edge has no connecting
relation within its source, destination, and function nodes in the displayed
graph. Its badge states named specification support or a declared step.
Connectivity is structural support, not proof of arithmetic. The trace route walks the
derived relations from one node to the registers that drive the actuators; a
relation records evidence rather than a signed effect, and the view labels it
as such.

The system map starts from the declared block order and exchanges neighbors
within a column while that reduces the weighted crossings of the flows. Stage
chips keep the blocks of the chosen stages, and Focus selection keeps the
selected block and the blocks that exchange flows with it; the URL fragment
records both. A block diagram aligns its partner columns with the rows of the
functions they connect when that reduces crossings. The `+`, `-`, and `0` keys
zoom in, zoom out, and fit, and Selection zooms to the selected box. A minimap
shows the visible part of a diagram larger than the canvas and moves the view
on click or drag. A node or trace route opens with its node in view.

The atlas carries one coverage matrix: for each block, its meanings and the
state of each on every layout, which is the level of a bound symbol, unresolved,
absent, or no record. Layout coverage on the system map draws the share of the
meanings of each block that the selected layout binds, and the block details
count the states by layout and list the meanings that the selected image does
not bind. A ROM switch keeps the route: the same block or chain, or the node of
the same meaning; a meaning that the new layout does not bind opens its block
with a notice. Open on a ROM, in the binding details and in the coverage list,
switches to a ROM that binds the meaning and opens its node. Evidence levels
colors the nodes of a diagram by the level of their symbols. A chain chip
counts the steps whose semantics remain unresolved; their original statements
stay source-bound until a review resolves them.

Each manifest declares `[architecture]` with `layout`. The graph's image
membership must agree with it. All ROM views use one graph snapshot. A
symbol's `images` list limits its applicability within a layout; an absent list
admits every image of that layout. The images of a layout that every
image-restricted symbol treats alike share one architecture model, keyed by
their joined names such as `JK00A+JK03A+JK03B`; its bindings name no single
image, and the view names the selected ROM. Excluded symbols and their incident relations do not enter the image's
architecture or semantic object bindings. Address-map geometry follows its
declared sources, and a layout without ledgers adds its `kb` bindings as the
evidence model describes. Binding details expose image restrictions and retain
cross-layout symbols, statuses, and analogs. A calculation chain is available
only when its output and every source, destination, and intervening function
have symbols applicable to the selected image.
The chain list reports incomplete binding counts and missing meanings with
their statuses. The atlas requires the configured graph; an unavailable graph
fails the build.

## Architecture command line

The same model answers structural questions without the browser:

```bash
uv run python tools/romviz/architecture.py check
uv run python tools/romviz/architecture.py blocks
uv run python tools/romviz/architecture.py block ignition-timing
uv run python tools/romviz/architecture.py node 0x991a
uv run python tools/romviz/architecture.py impact 0x991a
uv run python tools/romviz/architecture.py path 0003de4c ffff1702
uv run python tools/romviz/architecture.py chains ignition-advance
uv run python tools/romviz/architecture.py suggest 0003de4c
uv run python tools/romviz/architecture.py json --output tmp/architecture.json
```

`check` reports the gate result and the inventory of the model, with the maps
that have no functional role: those whose block belongs to the `unattributed`
stage, and those without a block, which the gate admits only below code
confidence or in the `dead` role. `blocks` and `block` list the functional
structure. `node` prints one node with its ledger
relations. `impact` states the sign an increase of a table or signal has on the
output of every chain that names it, followed by the unsigned derived reach to
the nearest actuator registers. `path` prints the shortest derived data or
control path between two addresses. `chains` prints one chain step by step with
its support and notes. `suggest` ranks candidate blocks for a function, which
is how a newly reviewed function finds its place. `json` writes the exported
model that the atlas embeds.

## Evidence model

Each target has `tools/romviz/roms/<ROM>.toml`. Manifest schema version 2 keeps
stock identity mandatory and makes analysis layers independently declarable.
Tracked declared sources are strict: missing files, invalid geometry, wrong
image hashes, out-of-range objects, and unknown patch kinds fail the build.
The function structure of every ROM is the L0 of its layout in
`l0/<layout>/`, and function labels without a reviewed annotation come from
`tools/ghidra/symbols/<layout>.csv` or read `FUN_<addr>`. An undeclared layer
remains absent and produces a visible warning in the atlas.

| ROM family | Current atlas evidence |
|---|---|
| JK00A, JK03A, JK03B, JK08A | Exact-code JK08A function, map, axis, diagnostic, DTC, definition-control, composed-runtime, and checksum evidence with target identity |
| JK00C, JK00D | Target L0 structure, `kb` function, table and axis bindings, generated target-specific definition addresses, projected DTC registry, composed production runtime profiles, and target checksum layouts |
| 1ND0A, 1ND3B | Exact-family 1ND0A L0 structure, `kb` function, table and axis bindings, reviewed shared definition addresses, projected DTC registry, composed production runtime profiles, target identity, checksum layout, and stock-image metrics |
| JK78C | Target L0 structure, `kb` function, table and axis bindings, reviewed target definition addresses, projected DTC registry, composed production runtime profile, complete checksum layout, and stock-image metrics |
| 1ME3B | Target L0 structure, `kb` function, table and axis bindings, reviewed target definitions, projected DTC records and attributes, composed production runtime profile, checksum layout, stock-image metrics, and architecture from its bound symbols |

A manifest without `reviewed_functions` and `map_ledger` takes its annotations
from the `kb` symbols of its layout that apply to the image. A bound function
symbol makes its L0 function a reviewed function labelled with the meaning
name. A definition object at the address of a bound table or axis keeps its XML
name and geometry and carries the binding. A bound table or axis without such
an object becomes a hidden `kb-map` or `kb-axis` object. Its details state the
editor decision: `emit = false`, no editor declaration, or declared but not
published for the image. When a definition object of the other kind starts at
the same address, the range serves as both a table and an axis: the `kb` object
is not hidden, and its details name the definition object and the meaning that
publish the range. Its extent comes from the symbol geometry, then the
meaning geometry, then the census `Map` or `Axis` of the image; without any of
them it is one byte with an unknown extent. Related addresses come from the
`kb` axis links, then from the census axis links. The build fails when `kb`
geometry differs from the extent of the published definition object of its
kind, or from the dimension or element width of the census entry of the image
at that address. A `kb` table of R rows can instead group R adjacent census
curves of its columns that share one census axis set. The exact JK08A family
keeps its ledger annotations and takes none from `kb`.

Every registered image declares its DTC registry, so the diagnostics layer is
populated independently of how much structure a target carries. The reviewed
`diagnostic-binding` objects stay exclusive to the exact JK08A family, which is
the only one with a tracked binding registry.

The exact JK00A/JK03A/JK03B/JK08A family uses one canonical annotation layer
because its declared executable address ranges are byte-identical. Only the
explicit `{target_rom}` presentation token is materialized for a target;
provenance paths and source labels are preserved unchanged.

The definition XML that the editor loads is the published definition of a ROM.
`definition_xml` names it for a manifest that loads its maps from it, and
`published_definition` names it for a manifest whose maps come from a canonical
source, such as the exact JK08A family; a manifest declares at most one of them.
The architecture view frames and tags every table that the published definition
names, lists the published tables of the view by editor category on the system
map, and lists the editable tables of a calculation chain in step order. A node
title takes the `kb` editor name, then the meaning title, then a semantic
meaning name; a generated name gives way to the first sentence of the summary.

JK00C and JK00D do not inherit JK08A addresses. Their map, axis, and definition
control objects are loaded from the generated `defs/JK00C.xml` and
`defs/JK00D.xml` projections, which are backed by SHA-bound reviewed relocation
registries. Their runtime address profiles are labeled `composed` because the
production builder emits target-specific runtime payloads at those addresses.

1ND0A and 1ND3B load their generated target definitions from one reviewed
SH7059 address correspondence. Their checksum fields and domains come from the
project checksum registry. Their composed runtime profiles expose eighteen Map
Switching families, the four 8x8 state-code ignition surfaces included, native
fuel-cut caps and curves, Rolling Launch, custom CAN
telemetry, exact hooks, and the shared SH7059 allocation.

JK78C uses a target-specific SH7058 projection. Its composed runtime profile
exposes fourteen VQ37 Map Switching families, native fuel-cut caps and curves,
Rolling Launch, and custom CAN telemetry in the audited flash and RAM
allocations. The checksum layer covers both SUM16 domains and both runtime
SUM/XOR domains.

L0 provides exact function entry addresses and body byte counts. The atlas
draws each function as a contiguous byte-count envelope anchored at its entry,
although the instruction addresses of a body in `function_tokens.csv` can be
non-contiguous.

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
uv run python tools/romviz/architecture.py check
node --check tools/romviz/architecture.js
node --check tools/romviz/app.js
uv run pytest -q tools/romviz/tests
make check
```

`make check` runs the architecture gate and rebuilds `ROMVIZ_OUTPUT` from the
tracked sources, so a stale atlas, an unplaced reviewed function, or a
code-confidence map without a block fails the check rather than the reader.

Generated atlas files belong under ignored `tmp/` or another explicit output
location and are not repository evidence.
