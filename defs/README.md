# ECU definition sources and projections

`defs/` contains canonical annotation layers, cross-ROM correspondence
registries, generated tuning-editor definitions, and pinned public
reference-definition submodules. Technical facts are separated from editor
presentation and generated output.

## Authority model

| File | Responsibility | Edit directly |
|---|---|---|
| `JK08A.interp.csv` | Interpolation entries and recovered geometry | no, `kb` projection |
| `JK00D.interp.csv` | JK00D interpolation entries and recovered geometry | no, `kb` projection |
| `JK78C.interp.csv` | SH7058 VQ37 interpolation entries and recovered geometry | no, `kb` projection |
| `1ND0A.interp.csv` | SH7059 1ND interpolation entries and recovered geometry | no, `kb` projection |
| `1ME3B.interp.csv` | SH7059 1ME3B fused interpolation leaves and recovered geometry | no, `kb` projection |
| `1EK7A.interp.csv` | SH7059 1EK7A fused interpolation leaves with exact 1ME3B counterparts | no, `kb` projection |
| `JK08A-JK00D.interp-correspondence.csv` | Reviewed cross-family interpolation wrapper pairs | no, `kb` projection |
| `JK08A-JK78C.interp-correspondence.csv` | Reviewed VQ25-to-VQ37 interpolation wrapper pairs and explicit source-only contracts | no, `kb` projection |
| `JK08A-1ND0A.interp-correspondence.csv` | Reviewed cross-generation interpolation wrapper pairs and explicit source-only contracts | no, `kb` projection |
| `1ND0A-1ME3B.census-correspondence.csv` | Table-level homology of the 1ME3B accessor census against the 1ND0A census | no, regenerate |
| `1ME3B-1EK7A.census-correspondence.csv` | Table-level homology of the 1EK7A accessor census against the 1ME3B census | no, regenerate |
| `JK08A.findings.csv` | Map semantics, role, scale, confidence, and evidence | no, `kb` projection |
| `JK08A.axes.csv` | Axis semantics, scale, confidence, and evidence | no, `kb` projection |
| `JK08A.funcs.csv` | Function semantics, callable contracts, and evidence | no, `kb` projection |
| `JK08A.vars.csv` | RAM and peripheral semantics and evidence | no, `kb` projection |
| `JK08A.diagnostic-bindings.csv` | Reviewed firmware-to-diagnostic claims | no, `kb` projection |
| `JK08A.tuning-signals.toml` | Current and missing tuning-observation coverage | no, `kb` projection |
| `JK08A.architecture.toml` | Functional blocks, endpoints, and calculation chains over the reviewed ledgers | no, `kb` projection |
| `JK08A.dtc.csv` | Exact DTC descriptor and attribute edit ranges | no, `kb` projection |
| `JK00C.dtc.csv`, `JK00D.dtc.csv`, `JK78C.dtc.csv`, `1ND0A.dtc.csv`, `1ND3B.dtc.csv`, `1ME3B.dtc.csv`, `1EK7A.dtc.csv` | Relocated DTC edit ranges read from the target image | no, regenerate |
| `JK08A.overrides.toml` | Editor presentation, visibility, categories, views, switches, and checksum declarations | no, `kb` projection |
| `rom-inheritance.toml` | Verified target-to-canonical annotation inheritance | yes |
| `definition-projections.toml` | SHA-bound relocated definition targets, capability gates, switches, and evidence | no, `kb` projection |
| `JK08A-*.definition-addresses.csv` | Reviewed source-to-target map and axis addresses | no, `kb` projection |
| `vq37-native-fuel-cut.toml` | Exact VQ37 coordinator, state-machine, pointer, cap, curve, and RAM bindings | no, `kb` projection |
| `vq37-native-tables.toml` | Exact VQ37 calibration tables and axes that have no canonical source, with stock value and accessor bindings and declared absent roles | no, `kb` projection |
| `rom-identities.toml` | Target-specific RomRaider and TunerPro identity metadata | yes |
| `JK08A.maps.csv` | Catalog ledger projected from Memgraph | no, regenerate |
| `<ROM>.xml` | Target-specific RomRaider definition projection | no, regenerate |
| `<ROM>.xdf` | Target-specific TunerPro XDF projection | no, regenerate |

The exact ROM supplies every map and axis value during ingestion. Handwritten
files must not duplicate image values. The graph is a reproducible relationship
projection and does not replace these tracked sources.

The architecture view is generated from the stage, block, endpoint, and chain
entities of `kb`. Edit their owners with `kb`, then regenerate the view.

The JK08A ledgers and the curated function names in
`tools/ghidra/symbols/7mfk.csv` are views of the meanings in `kb/` from stage 5
of `tools/kb/SPEC.md`. Use `kb` to read and change their facts;
`tools/kb/src/kb/ledger_projection.py` owns their CSV rendering. Reproduced ledger sites carry
checked L0 contexts; unverified sites and constants retain their source claims
without grounding a level. The `levels` gate checks each claim independently.

This README identifies mechanisms and their source owners. Current row counts,
status totals, image identities and version values are read from those owners
or their generated reports. `tools/kb/projections.toml` declares the generator
and consistency check of each generated projection; prose is not a machine
input and does not carry an independent census snapshot.

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

`definition-projections.toml` and the `JK08A-*.definition-addresses.csv`
files are projections of the `definitions` targets of
`kb/feature/definitions.toml` and of the `tbl` and `axis` meanings in `kb/`
(stage 3 of `tools/kb/SPEC.md`), and `uv run kb project` regenerates them.
`definition-projections.toml` binds JK00C and JK00D to exact source and target
image hashes. Its per-target correspondence CSV relocates every visible stock
map and required axis with explicit status and evidence; `status`,
`function_kinds`, and `sites` state the evidence of each row as section 20.3
of `../tools/kb/SPEC.md` defines them. A source map without
a unique target homolog is recorded as unsupported instead of being guessed.
Both projections record the two end-of-injection angle tables as unsupported:
the homologous stage reads eight-cell `uint16` curves with an explicit axis
instead of the source `uint8` tables of the implicit eight-point primitive.
JK00C correspondences compose reviewed JK08A-to-JK00D operands only through
unique exact or normalized JK00D-to-JK00C function matches. The generator
validates the resulting target geometry and stock bytes before emission.

`tools/rom_correspondence.py` combines this registry with the function
signatures, call ordinals, and resolver censuses of the L0 of two layouts. Its function and
entity outputs are deterministic review candidates. They do not establish
semantic inheritance by themselves; promoted target claims remain explicit
tracked evidence.

The interpolation registries and correspondences are projections of the `fn`
meanings with `[interp]` in `kb/fn/` (stage 3 of `tools/kb/SPEC.md`), and `uv
run kb project` regenerates them. A registry lists, by wrapper address, the
wrappers of the layout of its image with their kernel entries. An
interpolation correspondence has six columns with `status` set to `mapped` or
`unsupported`: a mapped row is an `interp-contract` item of a target wrapper
toward its JK08A counterpart, and an unsupported row identifies the source
kernel and wrapper, leaves both target address fields empty, and carries the
note of the `unresolved` status of the wrapper's meaning on the target
layout, which cites a complete target-library census. This records a real
source-only interpolation contract without inventing a target pair.
Target-only wrappers remain in the target interpolation registry and do not
need correspondence rows.

The SH7059 1ND library retains the interpolation mechanics of JK08A, with
target-only mixed-axis and alternate-finisher wrappers and an unsupported
standard-finisher contract. `JK08A-1ND0A.interp-correspondence.csv` owns the
mapped and unsupported source contracts; `1ND0A.interp.csv` owns the target
library. The corresponding JK78C registries retain its independent SH7058
addresses. Equal wrapper bytes and reviewed library order establish a contract
pair; they do not establish map semantics or equal calibration geometry.

`1ME3B.interp.csv` registers a library that fuses wrapper, kernel, and axis
search into one leaf per access, so every row names the leaf as both `kernel`
and `wrapper`. Its rows are read from the leaf code and reproduce the 1ND0A
contract vocabulary without shared code; duplicate leaves retain their own
callers. The census runs
`ResolveAccessors.java` in `fused` mode per row. No interpolation
correspondence registry exists for it: the contracts are equal in geometry,
storage, and axis types, but pairing them with 1ND0A entries requires a
reviewed accessor-level comparison rather than equal wrapper bytes. That
comparison is recorded per map and axis in
`JK08A-1ME3B.definition-addresses.csv`, which names the leaf beside each
target address.

`1ND0A-1ME3B.census-correspondence.csv` classifies every ROM operand of the
1ME3B accessor census against the 1ND0A census. Operands used as both maps and
axes are represented as maps; axis-only operands retain their own rows.
`tools/census_homology.py` writes it from the L0 of layouts `1nd` and `1me3b`
and applies three methods in order. `aligned-reference` aligns a 1ND0A function with its
best 1ME3B function by the instruction-shape threshold owned by that tool, and
pairs the census operands loaded by aligned instructions when every vote of the
source operand names one target of equal geometry. `unique-exact-content` pairs
a remaining target whose stored bytes and geometry occur once in each census.
`published-registry` adds the pairs that the definition correspondences and the
target-native table registry publish under one role. A published pair may
share its source with a census pair when target readers use separate copies
of one source surface, and it may cross a storage change. The ledger owns
pair status, the geometry of the source operand, byte equality and the
reason for each ambiguous or unpaired operand in `note`. Byte equality holds
when both operands have one geometry and store the same bytes over that
extent; a pair across a storage change keeps its role with `bytes_equal = no`.
The reasons in `note` are: `flat-content` for
uniform stock bytes, `duplicate-content` for bytes
that recur in the census, and `no-content-match` for bytes absent from the
1ND0A census. The ledger is a candidate-level address index and assigns no
semantics. `make check` validates it against both stock images and the
published registries and requires it to equal the ledger that L0 produces.

The target-native table registry `vq37-native-tables.toml` and the
target-native fuel-cut registry `vq37-native-fuel-cut.toml` are projections of
the `tbl`, `axis`, `fn`, `ram`, and `const` meanings with symbols on the
layouts `jk78c`, `1nd`, and `1me3b` in `kb/` (stage 3 of `tools/kb/SPEC.md`),
and `uv run kb project` regenerates them. A table entry carries the keys of
its symbol, the accessor bindings from the evidence of its `reader` links,
its axes from its `axis` links, and the digest of its stock values; an absent
role is an `absent` status of its meaning on the layout.

`JK08A-JK78C.definition-addresses.csv` owns the mapped source maps and axes
and the unsupported source roles. The unsupported entries cover removed
dispatcher slots, the exhaust-cam surfaces and standstill exhaust-VTC override
constants of the removed exhaust valve timing subsystem, target algorithms
whose table geometry differs, and the three
canonical ignition surfaces, whose homologs sit in the coordinator half that
the stock configuration leaves unexecuted. The JK78C registry enables native
RomRaider checksum handling, target-specific Map Switching, and the CAN
telemetry startup switch from the validated runtime profile. The target-native fuel-cut projection adds the adjacent activation and
release caps plus independent eight-point curves used by the registered
native state machine. The target-native table registry adds the
alternate selector arms and the VVEL target set modelled in `JK78C.vvel.md`:
duration, intake-CVTC, shaft-angle, and monitor tables with their declared
axes, each bound to the literal pool of its reading function. The set
includes the byte-identical second copies of the shaft-angle conversion and of
both monitor floors, and the hot-intake idle pair of the state-code dispatcher
`0x0657E4`. The registry also publishes the two 16x16 ignition surfaces that
the stock configuration executes, `0x00A10A` and `0x00A20A`: stock
`ROM8[0x8965]` = `0xBA` sends the ignition coordinator `0x069AB8` through its
mode-selected half, which picks the surface by the coolant byte against the
thresholds `0x008AC1` and `0x008AC2`. Both surfaces are Map Switching families,
so the definition carries five slot tables of each. The homologs of the
canonical trio, `0x0095CA`, `0x0096CA`, and `0x0097CA`, hold three
byte-identical copies in the gated half that the stock byte leaves unexecuted;
the trio is recorded as unsupported. A registry table may declare a `mask`, a
contiguous partial bit field of its cell; the ignition surfaces carry `7F`
because the low seven bits hold the timing field. The registry publishes the
calibration of the request transition conditioner, JK78C `0x096CE0`, 1ND
`0x0ABC6E`, and 1ME3B `0x0B2F2C`, as stored counts on all four images: the
gate thresholds and the hold reload, the 8x8 duration and offset surfaces
over static gear-index axes, the three 4x4 rate surfaces with their axes, the
reference multiplier and floor, the error-correction gain and limit, and the
recovery decrement. The stock calibration runs the conditioner on 1ND0A and
1ME3B; on JK78C and 1ND3B the mode flags `0x80` leave it unexecuted. A
registry table may declare `constant_content = true`, which accepts a stock
block of all one bits as a reviewed value: the two gate thresholds carry it
for the stock `0xFF` and `0xFFFF` of JK78C and 1ND3B, and the registry
rejects an unmarked all-ones block as erased flash. The
XML/XDF files expose editor controls; the unified builder remains responsible
for runtime composition and complete checksum closure.

`JK08A-1ND.definition-addresses.csv` projects the reviewed VQ37 semantic set
to the SH7059 1ND layout. It owns the mapped and unsupported roles, including
the reviewed target mixture map and its high-detonation multiplier. Their
stage, target axes and remaining conversion qualifications are described in
`JK08A.fuel.md`. The projection is established from
reviewed JK78C-to-1ND0A structural functions, exact storage, interpolation-call
order, selector branches, and target literals. 1ND3B reuses the address layout
because all address-bearing executable code is byte-identical to 1ND0A, while
its identity, stock calibration values, and image hash remain independent.
Both 1ND definitions expose target-specific Map Switching storage and the CAN
telemetry startup switch. The project checksum implementation covers the
fields owned by the selected checksum layout, but native RomRaider checksum
metadata cannot represent the complete layout. Their target-native fuel-cut maps are shared at the same
addresses, while each definition remains bound to its independent stock image
hash. The
1ND VVEL registry carries its target-native tables and axes at
shared addresses: the 1ND resolver indexes the hot-intake idle surfaces by two
temperature-coded bytes instead of engine speed and torque, reads a mode 14
surface that JK78C replaces with a constant, and has no floor curves and no
demand axis, which the registry declares as absent roles. The 1ND state-code
dispatcher `0x070514` reads the resolver surfaces in place of a separate
hot-intake idle pair, so that pair is absent too; the second copies of the
shaft-angle conversion and of both monitor floors are present. The registry
also publishes the six ignition surfaces that the stock 1ND configuration
executes: stock `ROM8[0x8A2B]` = `0xBA` and `ROM8[0x8A2C]` = `0x1C` send the
ignition coordinator `0x074D98` through its mode-selected half with state-code
selection, and the mapper `0x04C4B8` derives the state code from the VVEL mode.
State codes 2 and 8 read the 16x16 surface `0x00A410`, state code 1 reads
`0x00A510`, and state codes 3, 4, 5, and 6 with 7 read the 8x8 surfaces
`0x00A610`, `0x00A710`, `0x00A690`, and `0x00A6D0` over the native axes
`0x013FE2` and `0x013FDA`. All six surfaces are Map Switching families, so the
definition carries five slot tables of each; the four 8x8 families are selected
by the adapter of the separate 8x8 lookup `0x0285B4`. The homologs of the
canonical trio, `0x009880`, `0x009980`, and `0x009A80`, hold three
byte-identical copies in the gated half that the stock byte leaves unexecuted;
the trio is recorded as unsupported.

The native registry publishes the additional composite, transient and
four-factor fuel multipliers on JK78C, 1ND0A, 1ND3B and 1ME3B. Each uses
stored-count views and its own reader, pointer and axis evidence. The 1ME3B
composite multiplier uses a word column axis where the other layouts use a
byte axis; its direct input contract remains explicit in the owning meaning.

`JK08A-1ME3B.definition-addresses.csv` projects the reviewed 1ND semantic set
to the fused-library 1ME3B image. It owns the mapped and unsupported roles.
No code relocates from any modelled ROM, so every row is established through the 1ND0A
structural export: exact-bytes or normalized-shape function pairs that read
the target address at the same call ordinal, target functions that reproduce
the 1ND0A reader's operand set, selector arms, and call order, the fused leaf
whose contract equals the 1ND0A wrapper, exact target storage, and target
literals. The unsupported roles follow the 1ND projection; the
canonical ignition surfaces among them have no homolog at all: the target ignition coordinator `0x0797CC` carries only its
mode-selected surfaces and no target function reproduces the gated stock-inert
trio path of 1ND0A `0x074D98`. The projection declares checksum support with
native RomRaider metadata over the `sh7059_1me3b` layout. The definition
exposes the 1ME3B runtime allocation of `rom-address-profiles.toml`: Map 2-5
storage for the registered switched families, the target-native fuel-cut caps
and curves of the VQ37 registry, and the CAN telemetry
startup switch at their declared target addresses. The target-native table registry adds the
alternate selector arms, the VVEL target set, and the six executed ignition
surfaces to the 1ME3B definition, each
bound to an undisplaced literal-pool word of its reading function. The ignition
surfaces are the mode-selected set of the coordinator `0x0797CC`: the 16x16
surfaces `0x00A344` and `0x00A444` over the projected ignition axes and the 8x8
surfaces `0x00A544`, `0x00A644`, `0x00A5C4`, and `0x00A604` over the native
axes `0x013DCE` and `0x013DC6`, selected by the state code that the mapper
`0x050310` derives from the VVEL mode. `0x071D64` reads a fourth 16x16 surface
`0x00A774` with axis copies at `0x013599` and `0x0135A9`; it has no 1ND0A
counterpart and no canonical role. The MAF factor `0x008965` holds the value 133
and is read by `0x045634`, `0x04570A`, and `0x048298`; the last combines it with
the K-value `0x009170`, the `0x9F38` reference `0x0094D4`, and the value-3 scalar
`0x00885C` exactly as the 1ND0A consumer `0x0C188C` combines its four scalars.
Two curves exist only in this image
and are declared absent on the other three: the delay curve `0x01457A` of the
stepped approach to the throttled duration and the start-up blend target
`0x017136`. The 1ME3B resolver `0x062FAC` carries the JK78C
role set, with the JK78C engine-speed and torque axes on the hot-intake idle
surfaces, two floor curves over the demand axis, and the constant 50.0 in the
mode 14 pair. It reads the shaft-angle conversion and the cold pair inline and
leaves the throttled pair to `0x063534`, which publishes the throttled duration
as the curve value or as a stepped approach to it from 50.0.

## Functional architecture

`JK08A.architecture.toml` is the curated functional layer over the reviewed
ledgers. It declares stages, blocks, actuator and bus endpoints, and the
calculation chains that lead from the crank events and the sensors to each
command, with the sign of the effect that an increase of every table and signal
has on the published quantity. Nodes are addresses of `JK08A.findings.csv`,
`JK08A.axes.csv`, `JK08A.funcs.csv`, and `JK08A.vars.csv`, and every chain step
is bound either to a relation those ledgers record or to a specification named
in the step. `tools/romviz/architecture.py check`, which `make check` runs,
requires every reviewed function to sit in exactly one block and every
code-confidence map outside the `dead` role to reach a block, through a
function that reads it or a pin in the `maps` array of a block. It rejects an
address, a relation, or a step that the ledgers and the named specifications do
not carry, and counts the maps whose block belongs to the `unattributed` stage,
whose functional role the ledgers do not establish yet. The ROM atlas renders the model as the interactive architecture
view, and the same command answers block, node, impact, path, and chain
questions on the command line.

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
- `JK08A.work-support.md` models service `0x3B`, its session status, and the
  stored work-support timing and idle-speed adjustments behind DIDs `0x112D`
  and `0x112E`.
- `JK08A.diagnostics.md` models diagnostic publication and monitor boundaries.
- `JK08A.tuning-telemetry.md` defines schema-2 custom-CAN coverage, stock-CAN
  context, closed-loop observation groups, and measurements that still require
  new instrumentation or external equipment.
- `JK08A.definition-presentation.md` defines editor naming, category taxonomy,
  validation-copy terminology, and the non-tuning visibility boundary.
- `JK08A.can.md` models the exact HCAN1 mailbox table, stock transmit pipeline,
  payload boundaries, and safe extension mailbox.
- `JK78C.can.md` models the two exact HCAN controllers, the private-bus
  mailbox table, receive signal placement, transmit composition, the
  calibration boundary of the private bus, the VVEL identifier publication, and
  the removal of exhaust camshaft timing control on VQ37.
- `JK78C.vvel.md` models the VVEL target task, the fifteen-mode target
  selector, the exact sensor and diagnostic bindings of the selector inputs,
  the MAP and brake-booster pressure channel, and the unit boundary of the
  target surfaces.
- `VQ37.manual-unit-boundaries.md` reconciles factory quantities and service
  references with raw VVEL, pressure and load words, retaining unestablished
  scales and hardware acceptance boundaries.
- `JK78C.cvtc.md` models the intake CVTC solenoid output stage of the VQ37
  layouts: the scheme selector, the channel-7 cycle and buffer registers, the
  command path from the 16-bit duty words to the 8-bit command cells, and the
  units of the cells.
- `1ME3B.interp.md` models the fused calibration access library that replaces
  the `1ND` library, its recovered contracts, the fused census, and the tool
  boundary of `FindInterpCore.java`.

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
states that native RomRaider handlers maintain every checksum field that a
definition entity can invalidate: a checksum domain without a native handler
is admissible only when its whole region lies below the editable floor, the
first primary SUM16 field, and `emit_def.py` fails when a published entity
lies outside every native checksum region. A visible map must
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
Its `evidence` column holds three expected `rom_const:<address>=<hex-bytes>`
items, in order: the complete twelve-byte descriptor, its four-byte attribute
pointer slot, and the two-byte stock attribute, including a zero attribute.
The canonical geometry comes from `../refs/diagnostics/rom-dtc/layouts.toml`.
The `kb` ledger adapter rejects a duplicate or out-of-range index and requires
`record_addr`, the full packed P/C/B/U code, `attribute_addr`, and
`stock_attribute` to agree with those expected spans. It emits typed
`rom-bytes` identity evidence without a legacy exemption; `kb check --only
image-bytes` verifies each span on every applicable image of `7mfk`. The
expected values are reviewed stock snapshots, not values refreshed by the
compiler. These bytes ground descriptor identity and its storage bindings,
not the complete physical meaning of a monitor or complete disabling.
Relocated registries retain their nine-column format and carry no canonical
byte evidence.

The generator validates stock bytes before creating controls. RomRaider uses
coordinated native switches for descriptor and attribute ranges. TunerPro uses
atomic individual and declared group patches. Duplicate public codes remain
separate records when the ROM contains distinct paths. No implicit all-DTC
control exists.

A descriptor and its attribute reach different readers of the same record
index, so neither switch covers the readers of the other. In exact JK08A code,
`FUN_0003614C` and `FUN_00036E2C` publish the code of a record only while its
attribute has bit 7 (`0x80`) set, together with bit 2 or bit 3 of byte 2 of its
runtime state at `0xFFFF5718 + 3*index`. `FUN_00032C7C`, `FUN_0007FD10`, and
`FUN_00098A18` select records by runtime state alone and read the descriptor
without reading the attribute. `FUN_0008C366` walks the attribute pointer table
at `0x1A14C` and, through `FUN_0008C348`, clears the stored-fault bit (byte 1
bit 7) of every record whose attribute has bit 5 (`0x20`) set. Stock P1610
carries attribute `0000`, and its code returns after clearing while the
descriptor is intact (`../patches/immo-off-developer-flag.md`).

Every image stores its descriptors as twelve-byte records followed immediately
by one 32-bit attribute pointer per record. That pointer table is the ECU's own
attribute reference: it reproduces the canonical JK08A attribute addresses
exactly. `../tools/mapkit/dtc_projection.py` therefore reads a target binding
out of the target image instead of deriving it from an offset.

A canonical record is carried to a relocated target only when exactly one target
record is byte-identical to it, which fixes group, sub-index, monitor class,
code, and trailing flag together. Each target's DTC projection owns its record
inventory. VQ37 declares no P1422 or exhaust valve timing records, and 1ME3B
also declares no P0443 record. The exact-code members of `7MFKAVN86`
reproduce the canonical registry from their own images and share it rather than
tracking a copy.

Byte identity carries a record across a relocation that is not uniform. The
projection needs no address model: it locates the descriptor run and the pointer
table in the target image and matches records. 1ME3B is the case that separates
the two, and it also shows that this registry precedes every other analysis
layer. Its descriptor records share codes with `1ND0A` at nonuniform address
and index relocations, and the projection matches them without reference to the
structural export, checksum layout, or definition correspondence of the image.

The Developer Immobilizer flag is a definition-controlled data edit, not a
standalone instruction patch. Its execution path and safety boundary are in
`../patches/immo-off-developer-flag.md`.

The Cruise Control Switch is a definition-controlled data edit of the cruise
control configuration byte, not a standalone instruction patch. Its sites,
decoders, and hardware checks are in `../patches/cruise-control-switch.md`.

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
