# VQ HR map and flag discovery pipeline

This specification defines a reproducible pipeline for inventorying calibration tables (maps) and
control flags in Nissan/Infiniti HR firmware for Hitachi ECMs using Renesas SH7058/59 SH-2E
cores. Its scope is the repository's reverse-engineering track at `~/src/docs/vq`; the
human-oriented plan and knowledge base remain in the Obsidian vault, as described by the
two-track model in `AGENTS.md`.

The pipeline uses the deployed stack documented in `tools/README.md`: headless Ghidra 12.1.2,
Memgraph MAGE, the `neo4j` driver for loaders, and the `mcp-memgraph` MCP server for agent graph
access in section 8.2. GhydraMCP is an optional interactive tool for live sessions. It requires a
GUI and is outside the critical path; see section 8.4. This specification fixes **what the stack
produces, in what order, and under which numeric gates**, replacing one-off manual passes with a
deterministic flow, one data model, and measurable effectiveness.

## 1. Thesis

The Memgraph graph is the project's **system of record**, not a side-effect dump. Ghidra is the
**extractor**, using headless scripts over decompiler data flow rather than manual listing review.
The RomRaider and TunerPro definitions and the catalog ledger are **graph projections**, with
presentation overrides added to the definitions, not handwritten fact sources. Annotation
confidence is **gated data** (`pattern -> candidate -> code -> silicon`), not a prose label.
Effectiveness is defined by **measured metrics** in section 11 rather than subjective assessment.

Every element addresses a named process problem in section 3.

## 2. Definitions from recovered HR mechanics

**Map/table.** A calibration array in ROM read through a stereotyped access path:

- a shared **interpolation kernel**, a leaf function performing reverse linear axis search
  (`0x26944` in JK03A), reached **indirectly** through a literal-pool pointer
  (`mov.l PTR,rN; jsr @rN`);
- a dimension-specific **wrapper** for shapes such as 16x16, 8x8, 4x4, and 1D-16, consisting of
  one search per axis plus a specific **finisher**, all reached through pointer slots. The
  search-call delay-slot constant is a **clamp** equal to
  `(points - 1) * axis_element_size`. It determines both axis length and element type, and the
  extractor derives both from it. Each axis has its own search slot, and wrapper slots may differ.
  `0x262E0` calls byte search `0x26A0C` for `r5`, clamp 15, and word search `0x26984` for `r6`,
  clamp 30. `0x26660` uses the same pairing through `0x26BC4`/`0x26B84`. Axis element type is
  therefore a property of the `(wrapper, axis)` pair rather than the kernel. It differs between
  axes in 2 of the 22 two-axis JK03A wrappers;
- an **accessor**, a function that also calls the wrapper **indirectly**
  (`mov.l WRAP,r2; jsr @r2`) with `r4` as table base, `r5`/`r6` as axis pointers, and `r7`/stack
  as current values. The finisher addresses `table + idxY + idxX*width`.

Both transitions are indirect, accessor -> wrapper and wrapper -> kernel/finisher. This is central
to the resolver, which must handle `jsr @rN` (CALLIND) rather than only direct calls; see section 6.
Ghidra resolves an indirect target backed by a pool constant into a `COMPUTED_CALL` reference, and
`getCalledFunctions()` exposes it as a `:CALLS` edge. In JK03A this includes
`0x82c8a -> 0x26320`, while kernel `0x26944` has 11 wrapper callers. Every one of the 124 sites in
the `0x26944` kernel census is a `COMPUTED_CALL`; none has a genuinely dynamic target.

Edges disappear because of **caller marking**, not target dynamism. Ghidra does not mark code with
no direct incoming calls as functions, while `ExportGraph` enumerates calls by function. Wrappers
`0x26100` and `0x26230` are active and call the kernel but initially have no graph callers. In
JK03A the gap comprises 38,627 instructions in 494 regions, including 17 of 124 census sites.
Marking regions by flow from a prologue closes the gap completely. Stage 0
`RecoverFuncs.java` creates 353 functions, increasing the total from 1958 to 2312, and wrapper
callers appear. What remains missing from the graph is then not call edges but **operands**: which
table and axes were passed in `r4/r5/r6` (P2).

A complete map description is `{base, axis_X, axis_Y, width, height, storagetype, scaling,
accessor, wrapper, kernel, axis_RAM_inputs, RAM_output, A2L_identity, confidence}`.

**Flag.** A bit or small scalar tested at a branch to control selection. Roles:

- **selector** selects one of several maps or axes, such as `gbr+0x93 bit0` selecting
  Cold/HiOct/HiDet ignition and previous-cycle `0xFFFF246D bit7` selecting the
  accelerator-pedal activation or release threshold;
- **gate** enables or disables a code path. This includes calibration gates such as decel detect
  at `0xFFFF24D2 bit0x10` and `0xFFFF245D bit5`, plus the immo class. In JK03A/JK08A,
  `ROM[0x8725].bit0` gates the Developer Immobilizer state machine and generation of
  `0xFFFF4198.bit1` motor inhibit; `patches/immo-off-developer-flag.md` documents the complete
  chain. Registered and Lock states belong to an adjacent status path rather than the active
  immo-off flag;
- **threshold** is a ROM comparison constant, such as load delta `0x87FD`,
  accelerator-pedal high-state thresholds `0x8FDC/0x8FDE`, or the working
  engine-speed fuel-cut table at `0x934E`.

A flag can use direct RAM addressing (`0xFFFFxxxx`), GBR-relative addressing in the global
calibration structure, or a ROM immediate. The same data flow that resolves accessor operands also
resolves GBR-relative flags and axes; see section 6.

## 3. Current process problems

| # | Problem | Root cause | Resolution |
|---|---------|------------|------------|
| P1 | Axes and operands are lost: 18 of 124 sites lack `r4`, and axes are empty | `MapInventory` recovers only PC literals through a linear 14-instruction scan. It cannot distinguish a reachable branch from a dead end, fold computed (`add`) or stack operands, or see sites outside marked functions | Section 6 data-flow resolver |
| P2 | The catalog is computed outside the graph in CSV and scratchpad Python | The graph contains calls but not operands: edges do not express which table and axes were passed in `r4/r5/r6`, and `:Map`/`:Axis` are absent. Constant-target indirect calls already exist in `:CALLS`, while callers outside marked functions, 17 of 124, are missing | Section 5 `:ACCESSES`/`:VIA` edges and Stage 2 |
| P3 | MAGE algorithms do not localize the table-access subsystem | Louvain is the wrong tool: the access library is a hub layer of service functions rather than a dense cluster. In JK03A its 60 functions span 4 communities; 37 lie in the largest, where they are only 10%. Centrality on a call-graph projection provides the answer | Section 8.2 and Stage 1 centrality instead of communities |
| P4 | Annotation tools are ephemeral | `find_maps`, `ptrscan`, `viz`, and `a2l_geom` live in session scratchpads outside git | Section 10 `tools/mapkit/` |
| P5 | Two drifting truth sources: prose notes and manually edited XML | Findings and confidence live in prose, and prose is manually copied into the definition | Section 5 graph plus section 9 generator and overrides |
| P6 | "Pattern != semantics" is a lesson rather than a mechanism | Confidence is subjective, and pattern-scan hypotheses have failed twice | Section 5 confidence levels plus section 8.4 gates |
| P7 | Cross-ROM homology is unused | The graph is multi-ROM through the `rom` label, but no homology join is built | Stage 5 and section 8.3 |

## 4. Architecture: one graph, two extractors, generated outputs

```
ROM (.bin) --import--> Ghidra project (vq-hr)
    |                       |
    |       headless extractors (tools/ghidra/*.java)
    |                       |  funcs/calls/xrefs/accessors/flags CSV
    |                       v
    |  handwritten ----> Memgraph <---- HR catalogs (ROM-independent, no addresses):
    |  sources in git   (system of record,    A2L.xml ----> :A2LEntry (shape)
    |  interp.csv,       multi-ROM)           refs/vendor/ -> :VendorEntry,
    |  findings.csv,        |                                  :VendorFact
    |  axes.csv             |                                  (meaning/defaults)
    |                       v
    +-- image values --> Cypher + MAGE ----> generators
       (Stage 4 mapkit     (discovery)          |
        through roms.csv)      |                +-> defs/<source>.maps.csv (ledger)
                          candidates/homology   +-> defs/<source>.xml
                                                   (+ overrides.toml presentation)

factory manuals + exact-ROM DTC tables + pinned public sources
    -> source-preserving diagnostic corpus
    -> reviewed defs/<source>.diagnostic-bindings.csv
    -> DiagnosticBinding claims connected to the firmware graph

defs/<source>.notes.md is the handwritten journal for the canonical source. It contains the
basis for facts, including listings, traces, and evidence, rather than a projection of the facts.
It is neither loaded into nor emitted from the graph. defs/rom-inheritance.toml defines the
target-to-source relation.
```

Invariants:

- **Edit facts in canonical sources and presentation in
  `defs/<source>.overrides.toml`.** Git sources are `defs/<source>.interp.csv` for
  interpolation-entry geometry; `defs/<source>.findings.csv` for map semantics, units,
  confidence, role, and maps outside access models; `defs/<source>.axes.csv` for axis semantics
  and units; `defs/<source>.diagnostic-bindings.csv` for reviewed firmware-to-diagnostic claims;
  `symbols.csv` for function names; and `defs/rom-inheritance.toml` for target -> source
  relationships. The graph is the system of record where addresses, geometry, axes, scaling,
  RAM bindings, diagnostic context, and confidence converge, but it is not edited directly. The
  loader recreates calibration-layer nodes, so direct changes would not survive a run. Overrides
  contain aliases, categories, ordering, cosmetic changes, and manual additions outside the graph.
  Ledger and XML are generated only for a ROM with its own presentation layer. Direct edits to
  generated output are not persistent and are overwritten by the next run.
- **Handwritten sources do not declare table or axis values.** The image does. Stage 4 reads values
  on every run using census addresses and shapes. A handwritten number could silently diverge from
  the image and appear indistinguishable from fact in the graph, so range, content, and
  monotonicity are measured only.
- **`defs/<source>.notes.md` is handwritten and never generated.** It contains the basis for
  facts: listings, decompiler traces, evidence, and methodological lessons. The graph stores the
  facts themselves, so generating the journal from the graph would replace evidence with a render
  of the claims it is meant to support. The ledger is the readable catalog projection.
- **Every map and flag carries a confidence level and evidence list**; see section 5.
- **Diagnostic confidence and source applicability remain separate.** A strong
  code association does not make a homologous manual exact for the target ROM.
- **No active table below `code` is emitted**; `candidate` output is explicitly marked.

## 5. Data model (graph schema)

The node key is `{rom, addr}`, where `addr` is a hex string without `0x`, matching current
loaders. Existing `load_graph.py` and `load_xrefs.py` structures remain, and the calibration layer
is added.

The catalog layer, `:A2LEntry`, `:VendorEntry`, and `:VendorFact`, has no addresses because the
dictionaries define classes rather than locations. Its key is `family` plus name, and vendor
entries also include `vendor`. Names remain verbatim, and two dictionaries use different names for
the same entity, such as `BFS Multiplier (K-Factor)` and `K - Fuel Multiplier`. A global name key
would merge distinct entries while failing to connect equivalent ones.

### Nodes

| Label | Key properties | Meaning | Status |
|-------|----------------|---------|--------|
| `:Rom` | id, annotation_source, source_kind, source_evidence, target_sha256, source_sha256, source_ranges | Canonical annotation-source metadata and verified exact-code binding | existing |
| `:Func` | rom, addr, name, size, is_thunk, community, role, semantics, confidence, evidence, contract, contract_conf, contract_evidence | Function; semantics and contract are separate claims projected from `defs/<source>.funcs.csv` | existing |
| `:Reg` | rom, addr, region, name, semantics, units, confidence, evidence | Peripheral/RAM sensor or output; code-understanding layer projected from `defs/<source>.vars.csv` | existing |
| `:Interp` | rom, addr, role(`kernel`\|`wrapper`\|`finisher`), family, slot, dims, width, height, storagetype, step, limit | Interpolation primitives. Geometry (`width`/`height`/`storagetype`, plus `step`/`limit` for implicit-axis) is recovered from entry and finisher code and declared in `defs/<source>.interp.csv` | new |
| `:Map` | rom, addr, family, dims, width, height, storagetype, resolver_kinds, units, scale_expr, to_byte, scale_conf, scale_evidence, vmin, vmax, values_hash, semantics, role(`table`\|`threshold`\|`dead`), note, category, confidence, evidence, a2l_id | Table. `resolver_kinds` records mechanical base provenance; `evidence` and `scale_evidence` belong to separate claims; geometry comes from the entry | new |
| `:Axis` | rom, addr, len, storagetype, values, monotonic, kind(`rpm`\|`load`\|`temp`\|`raw`), units, scale_expr, to_byte, scale_conf, scale_evidence, confidence | Table axis. Search clamp in the entry defines `len` and `storagetype`; scale has separate evidence | new |
| `:Flag` | rom, addr, bit, role(`selector`\|`gate`\|`threshold`), semantics, confidence | Control bit or scalar | new |
| `:A2LEntry` | family(`HR`), name, kind(`map`\|`scalar`\|`switch`), dims, shape, width, height, storagetype, unit, scale_expr, axis_x_sem, axis_y_sem, axis_x_scale, axis_y_scale, category, userlevel, bits, concept | ROM-independent reference catalog | new |
| `:VendorEntry` | family(`HR`), vendor(`ecutek`\|`uprev`), name, doc, section, group, dims, axis_x, axis_y, output, origin(`factory`\|`patch`\|`unknown`), concept, level, source, note | Vendor-dictionary entry with verbatim calibration name; UpRev also supplies axes and output meaning | new |
| `:VendorFact` | family(`HR`), vendor(`ecutek`\|`uprev`\|`a2l`\|`derived`), subject, doc, kind(`const`\|`unit`\|`axis`\|`geometry`\|`mechanics`\|`hardware`\|`gap`\|`hypothesis`), concept, statement, value, units, applies_to, anchor, note | Vendor-documentation anchor: documented default, unit, mechanics, or declared gap | new |

### Edges

| Edge | Meaning |
|------|---------|
| `(:Rom)-[:ANNOTATIONS_FROM]->(:Rom)` | Target uses canonical source annotations; exact-code binding contains SHA-256, ranges, and basis |
| `(:Func)-[:CALLS]->(:Func)` | Resolved call, existing |
| `(:Func)-[:USES {kind}]->(:Reg)` | Peripheral/RAM access, existing |
| `(:Func)-[:ACCESSES {callsite,r4,r5,r6}]->(:Map)` | Accessor -> map with call operands absent from `:CALLS` |
| `(:Map)-[:VIA]->(:Interp)` | Map is interpolated by this wrapper |
| `(:Interp)-[:KERNEL]->(:Interp)` | Wrapper -> shared kernel |
| `(:Map)-[:AXIS_X]->(:Axis)`, `(:Map)-[:AXIS_Y]->(:Axis)` | Map axes |
| `(:Axis)-[:INDEXED_BY]->(:Reg)` | RAM source of the current axis value, typically a sensor |
| `(:Map)-[:WRITES]->(:Reg)` | Downstream RAM output of interpolation |
| `(:Flag)-[:SELECTS]->(:Map)` | Flag selects this map |
| `(:Flag)-[:GATES]->(:Func)` | Flag gates this path, including immo |
| `(:Map)-[:MATCHES {score}]->(:A2LEntry)` | Candidate catalog identity |
| `(:Map)-[:HOMOLOG {score}]->(:Map)` | Same map in another ROM |
| `(:Func)-[:HOMOLOG {score}]->(:Func)` | Function homolog in another ROM |
| `(:Func\|:Reg\|:Map\|:Axis)-[:RESTS_ON {source_prop,role,target_prop,ref}]->(:Func\|:Reg\|:Map\|:Axis)` | Claim-specific dependency. The complete key distinguishes semantics, contract, scale, and structural support. Projection of `evidence`, `contract_evidence`, and `scale_evidence` columns |

An address evidence token has form `role:addr@target_prop` or
`role:addr+offset@target_prop`. Address roles are `consumer`, `writes`, `indexed_by`, `selector`,
`threshold`, `from_map`, `trace`, `homolog`, `base`, and `match`; target properties are
`confidence`, `contract_conf`, `scale_conf`, and `structural`. `from_map` always targets
`@structural`. Terminals `rom_const`, `spec`, `registry`, and `site` ground a claim without a
node. `wave` and `arg` are process metadata rather than evidence.

The strict parser in `tools/memgraph/provenance.py` rejects legacy addresses without target
properties, unknown roles, empty values, duplicate normalized tokens, and unresolvable
references. The complete edge key consists of source label/address/property, role, target
label/address/property, and original offset-bearing `ref`.

The catalog layer has no internal edges. The `concept` property joins `:A2LEntry` and
`:VendorEntry`, because entries sharing a value describe one entity. A materialized edge would
duplicate that property and create precisely the second source of truth prohibited by P5. A
property join is one Cypher line. Stage 5 creates `:MATCHES` edges from maps to catalog entries
after Stage 4 supplies matching keys; catalog loaders do not create them.

`concept` granularity is a calibration family rather than one table. `vvel-duration` has seven
ProECU entries including Cold, Main, Overrun, and WOT; `idle-ignition` has nine. Variants of one
function, such as Cold/High Detonation/High Octane and Trustful, share a concept. The vendor
catalog defines this vocabulary; a missing concept joins to nothing.

For `:VendorFact`, `concept` is a prose topic rather than an identity key. A fact can cover an
entire family, such as `rev-limit` covering cut, restore, and maximum, or a subject with no table
at all, such as `rom-size`, `can-bus`, or `applications`. Its vocabulary only partially overlaps
the map catalog, so joining `:A2LEntry` to facts by `concept` retrieves documented defaults only
where the topic matches an entity.

### Confidence levels for claim-specific properties

The ladder is identical for `confidence`, `contract_conf`, and `scale_conf`, but each property
ranks a separate claim. Sources store local confidence. Effective confidence is the minimum of
local confidence and ranked `:RESTS_ON` dependencies. `@structural` participates in grounding and
reverse impact but does not constrain the minimum.

| Level | Promotion criterion | Trust |
|-------|---------------------|-------|
| `pattern` | Found by structural/data scan, such as a monotonic axis pair, 16x16 block, or pointer hit; no semantics | do not emit |
| `candidate` | Accessor exists, `r4/r5/r6` resolve through data flow, geometry is consistent, and an A2L/homology match exists | emit marked as candidate |
| `code` | The specific claim is traced in code and has claim-specific evidence | emit under its claim-type gates |
| `silicon` | Verified on a bench or through CONSULT3P live data under the `AGENTS.md` ground-truth-in-silicon rule | flash to the engine |

`pattern -> candidate` can be machine-driven. `candidate -> code` requires a trace and evidence.
`code -> silicon` is manual hardware verification. Effective confidence is not stored on the node
as a second source of truth; `provenance.py` and `provenance_report.py` compute it.

## 6. Operand resolver (linchpin, resolves P1)

This replaces manual backtracking in `MapInventory.backtrack` with decompiler data flow. The
target call site is an indirect wrapper call, `jsr @r2` (CALLIND), with `r4/r5/r6` assigned above
it. Three requirements are mandatory and are missed by manual scanning or a naive "read call
parameters" approach: lift and dereference call arguments (A), resolve GBR-relative operands
locally (B), and ensure the site belongs to a function (C).

**Condition A: CALLIND arguments are lifted and the operand is a pool pointer.** A typical access
site is `mov.l #PTR,rN; jsr @rN`, where `PTR` is a literal-pool slot. Ghidra resolves this indirect
target as a `COMPUTED_CALL` reference. Without a custom signature, the decompiler still lifts
`r4/r5/r6/r7` as ordered call inputs. Order follows the calling convention, so `in[1]=r4`,
`in[2]=r5`, and `in[3]=r6` represent table, axisX, and axisY. This is verified in JK03A: accessor
`0x82c8a` has three calls to `0x26320`, with `r4/r5/r6` pool slots `0x83368/6c/70`, table bases
`0xb81a/0xb61a/0xb71a`, and axes `0x11b6b/0x11b8b`.

An argument pointer is represented by the pool-slot varnode, such as `ram:0x83368`, rather than a
constant. The table or axis base is the ROM word stored in the slot. The resolver core reads call
input varnodes from `HighFunction`, dereferences RAM slots, and treats the ROM word at the slot
address as the base. Runtime inputs, such as current axis values in register/unique/stack space,
are not bases and are rejected because they do not point into ROM. This is more robust than
`MapInventory.backtrack`: data flow follows true define-use relationships, is independent of
distance and instruction order, handles `r5` in a delay slot that a backward-only scan misses, and
does not cross branch boundaries. Data flow alone recovers 12 of the 18 census-missed sites; the
remaining 6 are outside marked functions and are recovered under condition C.

**Signature override is refinement, not an unblocker.** Typing `:Interp` with custom `r4..r7`
storage pins argument count and order and removes over-approximation from the default prototype,
such as extra `r0` or stack inputs. A callee signature does not propagate into an indirect call:
forcing custom storage on `0x26320` does not change inputs at its CALLIND sites. Cleaning those
inputs would require a call-site prototype override through `HighFunctionDBUtil.writeOverride` at
the `jsr` address, not a target signature. Base recovery does not require it.

**Folding and fallback.** A register/unique argument varnode is folded through a p-code backward
slice from its last definition down define-use chains to a constant, including operations such as
`COPY`, `CAST`, `INT_ADD`, `PTRSUB`, and `LOAD`. `MULTIEQUAL` stops scalar folding because it
represents multiple values. This is a branch signal, not a failure. An unresolved operand falls
back to instruction-level `SymbolicPropogator`: `recordStartEndState` gives the register value at
the site, while a register-relative result indicates a caller-provided base. Fallback output is
marked `sp`. An `sp` base therefore means one of several paths was recovered and signals a
selector, not merely a less precise mechanism. Across 13 JK03A censuses and 553 sites excluding
the `0x26740` census, base sources are 406 pool-slot dereferences, 102 backward slices, 27
expanded merges (`phi`, section 6), 15 fallbacks, and 3 unresolved dynamic cases (`dyn`).

**Condition B: GBR is local.** GBR-relative axes and bases (`stc gbr,rN; add #off`) fold within
the function because the function assigns GBR itself through `ldc rN,gbr` in its prologue, and the
value differs by function. JK03A uses both a RAM base in `FUN_0003b75c`, where
gbr=`0xffff1dec`, and a ROM base in `0x4e2xx` accessors, where gbr=`0x11ebe`. Both the decompiler
and `SymbolicPropogator` therefore fold GBR from function entry. Setting a global GBR register
context through `ProgramContext.setValue` would be incorrect because it would impose one value on
the entire program. JK03A has no global GBR register context by design, not as a gap; Ghidra
creates GBR-relative references by propagating from `ldc`. Functions that receive GBR from their
caller remain register-relative (`gbrrel`) and require interprocedural context.

**Condition C: the site must belong to a function.** The decompiler operates on functions only,
while Ghidra does not mark regions without direct calls as functions; see section 2. Data flow is
unavailable there even though linear backtracking still works, producing `bt_only`. Recover a
region by flow from its beginning, the prologue after the preceding function's `rts`. A region can
contain several consecutive unmarked functions, so repeat passes while coverage grows. The
resolver does this for its own sites, recovering 9 JK03A functions and all 17 sites, so it does not
depend on stage order. Stage 0 `RecoverFuncs.java` permanently marks all code; afterward every one
of the 124 sites belongs to a function and the resolver has nothing to recover.

**Algorithm.** For each call site: (0) recover a function if the site is unmarked, satisfying C;
(1) read call input varnodes from `HighFunction`, satisfying A; (2) classify each operand:
dereference a RAM pool slot to obtain its ROM-word base; use an immediate constant directly; fold
register/unique through a p-code backward slice, including local GBR under B; fall back to
`SymbolicPropogator` if folding fails; reject runtime axis values as bases; (3) if a genuinely
dynamic base does not fold, mark it `dyn`/`gbrrel`, retain the call site as a base-less `candidate`,
and **do not drop it**. Output is
`accessor, callsite, wrapper, bt_r4/5/6, df_r4/5/6/7, operand source, verdict`, projected into
`:Map`, `:Axis`, and `:ACCESSES`. Section 11 defines the resolution metric.

The implementation is `ResolveAccessors.java`. A JK03A note from wrapper `0x261b8`: axes can be
computed GBR-relative values that differ by map, so the resolver must recover `gbr+offset` under
condition B rather than the nearest PC literal.

**Differential deployment, not blind replacement.** Run the resolver alongside
`MapInventory.backtrack`, not instead of it. Emit both triples, `bt_r4/5/6` and `df_r4/5/6`, plus
`agree|df_only|bt_only|conflict` for every site. The acceptance invariant is `df >= bt`: data flow
must recover everything linear backtracking recovered and close additional gaps. `bt_only` is a
parsing regression. A `conflict`, where base `bt != df`, is a latent error in the existing census
`nearestLoad` heuristic and therefore a finding rather than noise. This makes the replacement
additive with demonstrated non-regression.

**Operand sets.** A branch-selected base or axis reaches a call through a phi node
(`MULTIEQUAL`). Folding it to one value is semantically wrong: both tables exist and calibration
selects the active one. Emit one row per branch with a `branch` column, `selector` verdict, and
`phi` operand source. Assemble the triple by merge-input index rather than a Cartesian product.
The i-th input of each phi in one block arrives through the i-th edge, so branch i forms a
consistent triple. If an operand's branches do not fold to values, such as a runtime RAM input
beside ROM pointers, exclude it from expansion and retain its prior resolution.

The folding defect was not that the selected element was invalid, but that one element was
presented as the complete set with no verdict exposing the loss. For the `0x12e3a`/`0x12e32` pair,
the catalog contained the branch disabled by config byte `0x8616` and omitted the executing branch.
Both censuses selected the same disabled branch and reported `agree`. JK03A has 40 branching sites,
28 outside the `0x26740` census: 37 have two branches, one has three, and two have six. The
six-branch cases match the known `0x64344` selector set.

JK03A results across 13 `accessors.<kernel>.csv` censuses from canonical registry
`defs/JK08A.interp.csv`: 587 rows for 554 call sites, with data-flow ROM bases at 551 sites versus
493 for backtracking. Excluding the `0x26740` census gives 586 rows for 553 call sites and
550 versus 492. Resolution counts call sites rather than rows because an operand-set site emits
one row per branch. Unresolved bases are marked `dyn`. Site `0x4a02c` also has an empty backtrack
result, so it is dynamic rather than missed. Dominance is proven **over bases**: there is no site
where backtracking recovers an in-ROM value and data flow does not. The resolver reproduces both
reference censuses site-for-site, 327 for kernel `MapInventory` and 227 for bank
`DirectLookupInventory`, despite their independent discovery methods: Ghidra call-reference
enumeration versus forward scanning from a slot. Data flow becomes the catalog source.

The gate evaluates bases rather than every recovered value. Raw `bt_only` for `0x26984` is 1 at
site `0x62708`, but backtracked `r6 = 0x9a24963d` does not point into ROM and is not a base. It is
third-class noise described below, not a resolver regression.

All 18 `conflict` cases were analyzed. **Backtracking is wrong in every one of the ten base
conflicts.** No conflict represents a second valid base, so the baseline contributes no facts and
remains only a comparison point:

- **Branch-selected base** at 4 sites, all with `k4=sp`. At `0x64344`, five
  `mov.l @(pc),r4` instructions lie on `cmp/eq` branches over `r5`, and delay slot
  `mov.l r4,@r15` carries references to **six** tables. At `0xbe39a`,
  `tst r13,r13; bt` skips a load, so the base is either `0xa05a` or `0xa09a`. Neither `bt` nor
  scalar `df` is authoritative because the decompiler did not fold the base to one value, hence
  `sp`, and each mechanism names an arbitrary set element. `sp`, not `conflict`, signals a
  selector. Branch enumeration provides the complete set in Stage 6 through
  `:Flag {role:'selector'}`.
- **Axis mistaken for base** at `0x732a8`. The delay slot sets the base
  (`mov r7,r4` -> `0x15500`), while axis pointer `0x15690` appears earlier and is selected by
  backtracking. This is one base and one axis, not a map pair.
- **Delay-slot arithmetic** at 5 bank sites:
  `mov.l @(pc),r4; jsr @r7; _add 0x8,r4`. The base changes after `jsr` but before callee
  execution. The difference always equals the table stride, such as
  `0x12a22` -> `0x12a2a`, where 8 bytes hold 8 u8 points. Data flow models this and backtracking
  does not.
- **Value from an unreachable branch** at `0x56cd8`. Backtracking reports `r6 = 0x8729` from a
  branch that cannot reach the site because of `bra 0x56e46`.
- **Residual `r6` registers** at 2 bank sites. The primitive does not take `r6` as an argument, so
  the recovered register value is not an operand.
- **Pool constant read wider than its instruction width** at 5 sites, all on `0x26984`.
  Baseline `nearestLoad` always reads pool slots as 32-bit through `mem.getInt`, while the operand
  uses sign-extending 16-bit `mov.w`. Backtracking joins the constant with the next two pool bytes,
  while data flow yields the constant itself: for `0x9135`, `bt = 0x91358de6` versus
  `df = 0xffff9135`; for `0x0b5c`, `bt = 0x0b5c04ac` versus `df = 0x00000b5c`. Sign confirms
  the interpretation: `df` yields `ffff` when the s16 high bit is set and `0000` otherwise. The
  defect is invisible on kernel `0x26944`, whose operands use `mov.l`, and appears precisely on the
  word kernels that motivated the expanded census.

## 7. Pipeline stages

Run notation follows `tools/README.md`
(`headless-analyze.sh ... -postScript <Script>.java <args>`).

### Stage 0 - Ingest per ROM

Headless scripts perform import with `SuperH:BE:32:SH-2A`, BinaryLoader, and baseAddr 0x0;
autoanalysis; application of `symbols.csv` through `RenameFuncs`; and export preparation. A
complete ingest set contains `funcs.csv`, `calls.csv`, `xrefs.csv`, and one
`accessors.<kernel>.csv` per registered kernel.

- Run `RenameFuncs` + `RecoverFuncs` + `ExportGraph` in one project-mutating invocation.
  `ExportXrefs` and `ResolveAccessors` produce the remaining CSV files.
- `tools/memgraph/ingest.py <rom>` performs offline preflight and the fixed order
  `load_graph -> load_xrefs -> load_maps -> load_code ->
  load_diagnostic_bindings -> provenance audit`.
- Output includes `:Func`, `:CALLS`, `:Reg`, `:USES`, the calibration layer, claim-specific
  properties and `:RESTS_ON`, reviewed `:DiagnosticBinding` claims, Louvain
  `community`, and exact node/property/edge audit.

`--dry-run` validates CSV headers, value formats, foreign keys, the complete census set, ROM/SHA,
evidence resolution, and factual evidence for every `code`/`silicon` Func/Reg/Map/Axis property,
the diagnostic-binding source contract, then prints reproducible commands without
changing Memgraph. The exact source gate runs before the first node deletion. Global
`--strict` is a separate diagnostic for effective confidence and whole-graph
grounding. The source-preserving diagnostic corpus is loaded independently before
per-ROM ingestion.

Autoanalysis does not mark all code as functions. A region with no direct incoming calls does not
become a function, and its calls do not enter the graph; see section 2. `RecoverFuncs.java` marks
such regions by creating a function at each beginning, with Ghidra deriving the body from flow, and
repeats while coverage grows. A region can contain multiple consecutive functions, and each
created function separates its own prologue. In JK03A this converts 38,627 instructions across 494
regions into 353 functions, increasing 1958 to 2312. No instructions remain outside functions,
wrappers `0x26100`/`0x26230` gain callers, and Stage 3 operand resolution reproduces unchanged.
The pass groups already disassembled instructions and creates no code. Under `-readOnly` it only
counts and reports as a dry run.

### Stage 1 - Locate interpolation kernels (resolves P3)

**Primary signal: data scan.** `FindInterpCore.java` scans for 4-byte-aligned ROM slots whose
values point to code and for entries that read a slot and branch through it with `jsr @rN` or
`jmp @rN`. A direct call needs no slot, so this distinguishes the access library from other code.
**Code confirmation:** decompile 2-3 known accessors to confirm a shared first-stage call and
finisher pointer slot. Output is `:Interp` kernel/wrapper/finisher nodes and `:KERNEL` edges. This
replaces manual "find `0x26944`" work.

The layer is small. An accessor calls an entry through the same mechanism, so one slot signature
captures the whole indirect-call layer. Entries rank above kernels because they have more callers:
`0x26370` has 62 versus 11 for `0x26944`. A second indirection level distinguishes kernels:
kernel callers are themselves slot targets, while accessors are not. Three properties do **not**
identify a kernel:

- **leaf status**: 5 of 13 kernels call shared helpers. Both `0x26944` and `0x26984` call
  `0x26c78`, and `0x26a60` calls kernel `0x26740`; requiring a slot target to be a leaf would
  discard the primary kernel;
- **caller count**: 253 JK03A functions have at least 2 callers, but only 4 are kernels;
- **function marking**: implicit-axis bank entries form one shift chain, and Ghidra does not mark
  `0x26a80`/`0x26a84`/`0x26a88` as functions at all; the `0x26a5c` body is only 4 bytes. Validate
  a slot target as code rather than a function entry because function marking is Ghidra metadata.

The scan localizes the library, not the kernel level within it. A kernel and its helper can share
the same signature; `0x26c78` ranks 11th in output but is not a kernel. The
`defs/<source>.interp.csv` registry identifies kernels within the layer by clamp. JK03A results:
all 13 kernels found; hub kernels rank 2, 3, 6, and 8 among 799 candidates; bank kernels rank
53-63 because each has one entry and cannot be distinguished by entry count.

**Independent centrality check, available before Stage 3.** Constant-target indirect calls already
produce `:CALLS` edges, so PageRank over a ROM call-graph projection ranks the access library
highest. JK03A examples are `0x26740`, `0x26c78`, `0x26370`, `0x26944`, and `0x26388`. The
projection is mandatory because `:Reg` nodes connect the full storage graph; see section 8.2.
Louvain is unsuitable because the hub layer clusters with callers rather than itself (P3), so
communities are not a validation signal. `FindInterpCore.java` detects the slot-plus-wrapper
signature, while centrality is a second independent signal for the same kernel.

### Stage 2 - Enumerate accessors to build the catalog (resolves P2)

After Stage 3 builds `:ACCESSES`, the catalog is a **graph query**, not a CSV scan:

```cypher
MATCH (a:Func {rom:$rom})-[x:ACCESSES]->(m:Map {rom:$rom})-[:VIA]->(w:Interp {role:'wrapper'})
MATCH (w)-[:KERNEL]->(:Interp {role:'kernel', addr:$kernel})
RETURN a.addr AS accessor, w.width AS width, w.height AS height,
       m.addr AS table, x.callsite AS site
ORDER BY w.width DESC, table
```

Before `:ACCESSES` exists, `MapInventory` bootstraps a candidate catalog through
kernel-value slots -> wrappers -> references. The final catalog lives in the graph; section 11
defines its completeness metric.

### Stage 3 - Resolve operands

Run the section 6 resolver, `ResolveAccessors.java`, for every call site and once per kernel,
producing `accessors.<kernel>.csv`. `load_maps.py` projects it into `:Interp`, `:Map` with
`r4` as base, and `:Axis` with `r5 -> :AXIS_X` and `r6 -> :AXIS_Y`. The source register remains
on the edge, allowing Stage 4 to refine orientation without losing the fact. It also creates
`:ACCESSES`, `:VIA`, and `:KERNEL` edges. Initial confidence is `candidate`. The loader runs after
`load_graph.py`, which owns `:Func` and deletes functions and their `:ACCESSES` edges when a ROM is
reloaded.

The layer has four sources with distinct responsibilities: entry registry
`defs/<source>.interp.csv`, one row per entry with geometry recovered from its code; resolver
censuses for the target ROM, containing sites and operands; and the manual layer,
`defs/<source>.findings.csv` for maps and `defs/<source>.axes.csv` for axes. The manual layer
contains conclusions a census cannot supply: semantics, confidence, map role, units, axis
semantics, and maps outside access models. `defs/rom-inheritance.toml` resolves `<source>`. For a
normal ROM it equals `<rom>`; an exact-code inheritor uses canonical annotations with its own
export and image. Load the manual layer in the same run because findings share nodes with census
facts and would be deleted if loaded separately.

Load the complete layer across every census at once because the loader recreates its nodes. One
census per run would make a second kernel delete the first kernel's maps. Select census rows by
the `(kernel, entry)` registry pair. An entry appears in every census for a kernel whose slot it
holds: the same 47 `0x26474` sites occur in both the `0x26944` census and the `0x26740` finisher
census, so counting by entry address alone would duplicate them. The loader verifies that access
families share no table. A shared table would be a finding rather than normal variation.

JK03A has 587 rows for 554 call sites, producing 446 maps (248 explicit-axis,
188 implicit-axis, and 10 manual non-census maps across 4 families), 229 axes,
592 unique accesses, and 47 interpolation nodes
(34 entries plus 13 engines). No table is shared between census families.

Both families load in one pass because their census mechanism is shared. The bank primitive is a
wrapper around its shift chain: engine-pointer slot, specialized entry, and accessor `jsr`.
Operand interpretation differs. In the explicit-axis family, `r5`/`r6` are axis pointers. In the
implicit-axis family, arithmetic defines the axis, no `:Axis` node exists, and
`points`/`step`/`limit`/`width` belong to the primitive. Recovered ROM addresses in `r5`/`r6`,
22 and 49 values respectively, are not interpreted as axes. The primitive does not take `r6` at
all, while `r5` is assigned in a delay slot, so fallback reading the register at the call address
sees its prior value.

Only a value pointing into ROM is a base. Runtime inputs such as current axis value, index, or mask
remain as recovered edge values without creating nodes. Geometry is an **entry** property because
the entry specializes by table shape rather than receiving shape as a parameter. The registry
supplies geometry recovered from entry code: a delay-slot clamp defines point count, while an
implicit-axis limit defines both count and range. Dimension follows from the same code.
`storagetype` is recovered where the element is read: directly in a 1D entry, or in the finisher
reached by a 2D entry's tail jump. All five 2D finishers read unsigned elements with `EXTU` on both
interpolation operands, so every catalog map has a known `storagetype`.

An independent dimension signal is the `r6` axis. It appears at 86 of 87 2D-entry sites but only
15 of 240 1D-entry sites; the highest 1D rate is one of seven at `0x26550`. At those 1D sites `r6`
is not an argument, only a fallback-recovered register value. The loader compares declared
dimension against the majority and stops on disagreement. All 24 JK03A explicit-axis entries
agree. Only 2D entries interpret `r6` as an axis; rejected values are printed, 15 in JK03A, so the
catalog is not silently narrowed.

Entry geometry makes map geometry unambiguous. The loader enforces this as fact: a map read through
entries of different shapes would have two incompatible shape definitions. JK03A has no such map.

Only data flow creates graph bases; `bt` creates no maps because section 6 shows it is wrong in all
ten base conflicts. A branch-selected operand is visible as `kind`/`kind5`/`kind6 = sp` on the
`:ACCESSES` edge: the decompiler did not fold it, fallback recovered one set element, and the value
is incomplete. JK03A has 15 projected base accesses with `sp`, stored in
`Map.resolver_kinds` rather than claim evidence, plus 256 axis accesses at 247 call sites. These
are Stage 6 inputs. Four maps remain behind them, named only by backtracking, whose output is not a
fact.

Fallback is as unreliable for axes as for bases. An axis named only by fallback is `pattern`, not
`candidate`. Any folded site promotes it to `candidate`; without one, the value is heuristic.
JK03A has 14 such axes among 229, including `0x8000`, which is erased flash containing only
`0xFFFF` and therefore not an axis. Definition gates exclude them.

### Stage 4 - Characterize

This stage **measures but does not infer**. Range, content, and monotonicity are properties of
target-image bytes and are read identically for every map regardless of semantics. Axis identity
and units are code conclusions supplied by consumer traces and canonical
`defs/<source>.axes.csv`. Inferring them from array shape is the same failure mode that caused the
pattern scan to fail twice (P6).

- **Axis:** read the array into `values`, check `monotonic`, and locate the RAM source of the
  current value through `:INDEXED_BY` and the xref layer. The node stores all points because an
  axis is short and defined by them. Shared axes can be compared as lists, and an RPM staircase is
  visible in the graph without reopening the image. The RAM input defines units:
  `0xFFFF11AE` is a proven RPM index, so every axis it indexes stores `rpm/50`.
- **Map:** read the block and compute `vmin`, `vmax`, and `values_hash`. Do not copy cell values
  into the node; 256 cells in the graph would merely duplicate image content, while hashes identify
  equal maps. Stage 3 supplies `storagetype` from 1D entry code or a 2D finisher. Accessor
  decompilation supplies the interpolation RAM output through `:WRITES`.

Monotonicity is exempt from the "do not infer" rule because ascending order is an interpolation
kernel requirement, not a semantic guess: the kernel scans backward from the highest point to the
first point `<=` current value. An array that violates this order cannot function as an axis,
regardless of the resolver's label. JK03A has one such axis among 229, `0x119B2`, whose map
`0x9C5A` is a 4x4 block of `0xFF`, indicating unprogrammed flash. The image contains no literal
`0x119B2` (`k6=slice`; the pointer is computed rather than pooled). An all-`0xFF` block alone is
not evidence because a saturated limit looks the same; the trace distinguishes them.

This stage is a Stage 5 prerequisite. Of three match keys, `dims`, scale family, and axis
semantics, the final two come from this stage and the manual layer rather than the catalog.

Reading tools live in `tools/mapkit/`, not a scratchpad; see section 10. The image is selected by
`rom` from `rom-images/roms.csv` and verified by SHA-256. A substituted dump could otherwise
produce 229 axes of plausible values from the wrong image, an error indistinguishable from fact in
the graph.

### Stage 4.5 - Bind static diagnostic semantics

This stage connects the source-preserving diagnostic corpus to firmware targets
only when machine-code evidence establishes the association. It does not infer
identity from matching names, units, table shapes, DID values, or same-function
RAM references.

`defs/<source>.diagnostic-bindings.csv` records one reviewed association per
row. The loader resolves and connects:

```text
Rom -> DiagnosticBinding -> Func / Reg / Map / Axis
                         -> DiagnosticParameter / DtcCode / CanSignal
                         -> source-specific definition or ROM descriptor
```

Four dimensions remain independent:

- `confidence` is the static firmware association strength: `pattern`,
  `candidate`, or `code`;
- `applicability` describes the relationship between the diagnostic source and
  the target ROM;
- `rom_scope` permits either exact-ROM use or transfer across the explicitly
  verified JK08A/JK03A exact-code relation;
- `priority` orders the map worklist but does not promote confidence.

The source claim and every machine dependency are resolved before the loader
replaces a ROM's binding projection. Exact-ROM rows do not transfer to JK03A.
Replacing the global diagnostic corpus removes dependent bindings; per-ROM
ingest reconstructs them against the replacement source claims.

`ExportDiagnosticRefs.java` and
`diagnostics/extract_static_bindings.py` provide a review queue for service
`0x22`. The exporter records semantic-free 16-bit ROM references and
instruction immediates. The extractor joins exact DID values and lists
same-function RAM references. Its CSV cannot be consumed by the binding loader:
a dispatcher-to-response data-flow trace must resolve the request, returned
value, and conversion first. With the JK08A exact-code export and tracked
diagnostic corpus, it emits 937 source-specific queue rows from 383 known DIDs.
Collapsing duplicate diagnostic claims leaves 197 distinct firmware reference
hits for 34 matched DIDs; 58 hits occur in functions containing more than one
known DID.

The JK08A binding projection contains 145 reviewed claims:

- engine speed at `0xFFFF11AE` has `code` association and homologous VQ35HR
  monitor applicability;
- exact UDS DID `0x1201` returns word `0xFFFF11F4`. Its common producer with
  RPM/25 `0xFFFF11B3` and RPM/50 `0xFFFF11AE` establishes the JK08A
  representation as RPM/12.5;
- calculated load at `0xFFFF413E` has a `code` association through the exact
  Mode 01 PID `0x04` dispatcher path and homologous VQ35HR monitor applicability;
- exact UDS DID `0x1101` returns coolant byte `0xFFFF1079`. Code normalizes it
  through `0xFFFF1077` into previous-cycle calibration index `0xFFFF106F`;
  homologous measured diagnostic data supplies conversion `raw-50 deg C`;
- ignition angle at `0xFFFF23EE` and two MAF transfer maps at `0x141F4` and
  `0x14274` remain `candidate` associations with homologous monitor semantics;
- exact UDS DIDs `0x1107` through `0x110A` are four pointer-table aliases for
  response byte `0xFFFF2022`. On the normal path, `FUN_0004DF82` writes
  `110 - uint8[0xFFFF11D4]`; a community formula for DID `0x110A` exactly
  inverts that transform. The upstream code chain reaches conditional
  subtractive correction map `0x147DA` through `0xFFFF12D6` and
  `FUN_0004DBE8`. Its operating-mode qualifier, physical degree unit, and axis
  input producer remain unresolved;
- exact UDS DIDs `0x1123` through `0x1126` return the high bytes of four
  Q8.8-percent fuel-trim words. Exact Mode 01 branches map the same words to
  standard PIDs `0x06` through `0x09` in STFT B1, LTFT B1, STFT B2, LTFT B2
  order and divide each word by 200. Neutral initialization `0x6400`, the
  standard PID transform, and the community `raw-100` UDS conversion agree.
  STFT is published from two closed-loop working words; LTFT is selected and
  updated in two bank-specific 8x8 adaptive RAM grids before final limits and
  fail-safe neutralization;
- UDS DIDs `0x1206` and `0x1207` have `code` associations with the two-byte
  big-endian values at `0xFFFF23C8` and `0xFFFF23CA`. Homologous VQ35HR
  diagnostic sources identify the values as injection pulse width for banks 1
  and 2. Exact runtime writer `0x4EBA2` produces six consecutive channel words
  through the Q1.7 direct-indexed multiplier at `0x129C0`;
- UDS DID `0x1135` has a `code` association with byte `0xFFFF2442`. Exact code
  writes it as the first member of a centered two-bank angle pair through
  `0xBD9F0`, while homologous VQ35HR sources identify the value as intake valve
  timing bank 1;
- exact UDS DIDs `0x120F`, `0x1210`, `0x124B`, and `0x124C` return the four
  bank-specific throttle-position sensor words at `0xFFFF2756`, `0xFFFF275E`,
  `0xFFFF285C`, and `0xFFFF2864`. DID `0x130A` exposes the throttle-relay status
  at `0xFFFF2C56` bit 4. These values provide observable feedback for validating
  the `0x942C` throttle-limiter candidate without asserting a static edge from
  the limiter request coordinate to the feedback producers;
- exact UDS DIDs `0x130D` and `0x130E` expose ASCD switch and lamp status at
  `0xFFFF2A83` and `0xFFFF2A84`. Stable one-hot switch code `0xFFFF2A85` is
  accepted after five equal samples and feeds the exact P1564 monitor at
  `0x913D0`;
- knock-monitor maps `0xABBA` and `0xABFA`, function `0xA52E4`, and state byte
  `0xFFFF4204` have exact-ROM, code-traced links to P0327, P0328, P0332, and
  P0333;
- misfire coordinator `0x82C8A`, detection core `0x85A70`, and local reporter
  `0x84CD0` have exact-ROM links to P0300..P0306. The reporter maps
  `0xFFFF4200.bit7` and `0xFFFF41FF.bits0..4` to cylinder descriptors P0306
  through P0301, while `0xFFFF4200.bit6` or the no-cylinder fallback selects
  P0300;
- primary rear O2 dispatcher `0x89D92` links bank-indexed metrics
  `0xFFFF26E9`, `0xFFFF26EB`, `0xFFFF2726`, and `0xFFFF2724` to exact
  P0139/P0159, P0137/P0157, and path-A P0138/P0158 descriptors. Alternate
  dispatcher `0x8A258` links working arrays `0xFFFF42B0` and `0xFFFF42B2` to
  the separate path-B P0138/P0158 descriptors;
- rear O2 heater dispatcher `0x8B93A` compares bank-indexed feedback byte
  `0xFFFF2722` with exact ROM thresholds `0x8AAF=0x0C` and `0x8AB0=0xEC`,
  linking the low branches to P0037/P0057 and the high branches to P0038/P0058.
  Exact DID `0x130B` independently packs command-state bits from `0xFFFF2377`
  into supported response bits 1 and 0 at `0xFFFF2C57`. Whole-program scans
  found no writer for either input state, so the physical feedback producer and
  output driver remain unresolved;
- catalyst dispatcher `0xA2254` directly selects exact P0420/P0430 descriptors.
  Separate per-bank path `0xA38DC -> 0xA2D66 -> 0xA2EE4 -> 0xA2F56`
  compares averaged metric `0xFFFF314D` with map-derived limit `0xFFFF2B6F`.
  Limit table `0x11FB6` has eight zero cells, making this unsigned below-limit
  branch unreachable in stock JK08A without removing the independent
  `0xA2254` result path;
- the EVAP slice resolves 13 exact descriptor paths for P0441 through P0456.
  Common dispatcher `0x7D8B8` proves direct fault branches, while `0xB4EF8`
  records complementary descriptor-aware state. All eight paths coordinated by
  `0xABCA2` are skipped by stock JK08A configuration bytes. The separate P0451,
  P0442, and P0455 direct branches have no recovered static configuration
  disable. P0447 path B is independently configuration-disabled, and only the
  complementary P0456 branches are resolved.

The injection response path reaches calibration `0x129C0` through its exact
runtime writer. For intake CVTC, exact code proves
`clamp_u8(0x80 + reference - capture)` and the ATU-II capture path. Community
diagnostic definitions supply candidate conversion `raw*0.5-64 degCA`; hardware
validation remains required. Unsupported community candidates `0x1211/0x1212`
and `0x1127/0x1128` are excluded because the exact JK08A pointer tables contain
`0xFFFFFFFF` for those DIDs. JK03A receives the 29 exact-code claims and none
of the 116 exact-ROM DTC claims.

The static milestone ends at `code`. `silicon` is rejected by the loader, and
hardware-loop verification is not a completion gate for this stage.

### Stage 5 - Match catalogs and build cross-ROM homology (resolves P7)

Two catalogs provide complementary evidence. A2L supplies **shape**, including geometry, element
type, scaling, and axis semantics. ProECU and UpRev vendor dictionaries supply calibration
**meaning**, calculation chains, and **documented defaults**, which are numeric anchors searched
directly in the image. None is complete and their gaps differ. ProECU states that the rev-limit
map input axis is unknown, while A2L identifies `State` with `Normal` and `Reverse` points.
Neither vendor knows the knock-threshold scale, while A2L supplies a 16x6 `Knock Slice Map` with
`x*0.0015259`. Conversely, shape without meaning supplies neither identity nor a useful value
anchor.

- `load_a2l.py` loads `:A2LEntry` from
  **`defs/reference/.../Nissan Definitions/A2L.xml`**, a ROM-independent HR catalog with
  `family=HR`. EV18A/CF92A are instances that provide sample names and scaling. The catalog has
  188 entries: 106 maps (37 two-axis and 69 one-axis), 36 scalars, and 46 switches
  (19 `Options//Flags`, 18 DTC lists, and 9 OBD support masks; 152 bits under `Flags`).
  **Addresses do not transfer** because JDM 2.5L and USDM 3.5L layouts differ. The base definition
  has no addresses and describes classes rather than locations; this is a structural property,
  not merely a loader convention.
- RomRaider notation is normalized by axis count: `2D -> dims=1`, `3D -> dims=2`, and
  `1D -> dims=0`. In the graph `dims` means number of axes; without normalization a join would
  interpret `"2D"` as 2 and match every entry to the wrong class. `shape` uses the annotation
  journal vocabulary shared with wrapper geometry, such as `16x16`, `8x8`, and `1D-8`. All eight
  JK03A wrapper shapes exist in the catalog, confirming A2L as an HR-family reference.
- `load_vendor.py` loads 371 `:VendorEntry` and 138 `:VendorFact` nodes from `refs/vendor/`,
  reconciling ProECU and UpRev dictionaries under `family=HR`; see `refs/vendor/README.md` for
  method and annotation. Like A2L, they contain no addresses. `refs/vendor/catalog.csv` is
  generated by `tools/vendor/build_catalog.py` from two handwritten transcriptions. Edit the
  transcriptions rather than the generated catalog.
- **`origin=factory` filtering is mandatory** for stock-ROM annotation. Of 371 entries, 128 are
  not factory: 126 describe vendor patches, EcuTek RaceROM or UpRev ARC, which are third-party code
  absent from stock, and 2 remain unresolved. Matching a stock map to a patch entry is incorrect,
  not a weak hint. Group labels cannot filter these entries: `Rev Limit Per Gear Mode1-4` RaceROM
  maps live under `Limiters` beside factory maps. The source document determines origin.
- Build `:Map -> :A2LEntry` matches on `(dims, scale-family, axis semantics)` after Stage 4 and
  store `:MATCHES {score}`. Before Stage 4 a `:Map` has only `dims`; `scale_expr` and axis
  semantics come from axis reading and RAM-input traces. Matching only `dims` would join all
  37 two-axis entries to every `dims=2` map, producing noise rather than a hint (P6). Even
  geometry plus value range is **weak**, because many maps share 16x16 or 8x8 shape. It supports
  `candidate`, not identity. The discriminating evidence is the trace of axis RAM sensors in
  Stages 4 and 7, not value shape.
- The vendor catalog does not match directly. It joins **through A2L by `concept`**. ProECU has
  none of the three structural keys because tree screenshots contain names only. UpRev describes
  axes in prose, such as `Base Fuel Schedule` and `coolant temp`, with axes present in 63 of 76
  entries. Blind name matching is exactly the P6 failure mode. Both catalogs therefore carry
  `concept`: 45 of 188 A2L entries and 170 of 371 vendor entries, representing 49 concepts of
  which both dictionaries cover 27. All three dictionaries converge on 23 concepts, 17 with both
  vendors. One query follows `:Map -> :A2LEntry -> concept -> :VendorEntry`, taking shape from A2L
  and meaning/defaults from vendors. An empty `concept` means "relation not established", not
  "no relation exists".
- Descriptions and geometry support `concept`, not name similarity. Names can mislead: A2L
  `MAF Voltage Lower Limit` resembles EcuTek `MAF Voltage Min Allowed`, but the thresholds differ.
  A2L ties its threshold to P0102, while EcuTek states no DTC is set, so they are not linked.
  Conversely, shape resolves a naming dispute: UpRev `Throttle A` and EcuTek `Torque Demand`
  describe one `QH0/ Torque Conversion Map`, shown by matching axes, output scale, and validation
  copy, although the vendors interpret it differently. Validate concept annotation before loading.
  A value absent from the vendor concept vocabulary joins to nothing, and dead annotation in the
  graph is indistinguishable from missing annotation.
- **A documented default is an image-content anchor** and the only catalog key usable before
  Stage 3 because it requires neither resolved operands nor axis semantics.
  `:VendorFact {kind:'const'}` carries 22 such values, including K-Factor 26806,
  `100% Engine Load = 39.8 BFS`, cold/warm threshold 70 degC, and VTC reference 118 degCrank.
  Search them directly in the image. A value match alone gives `pattern`, not `candidate`; shorter
  values occur more often by chance, as measured in JK03A below. A homologous block signature or
  consumer trace promotes the finding to `candidate`.
- **`applies_to` defines dictionary applicability**, which is narrow by default. EcuTek documents
  VQ37VHR in the 370Z with VVEL, while target JK08A is VQ25HR **without VVEL**. Of 138 facts,
  78 are `vq37vhr` as documented, 41 are `nissan` generalizations from UpRev, and only 18 are `hr`
  facts proven architecturally. K-Factor is one example, with the same value in 2.5L and 3.7L
  images. `VVEL Valve Duration` does not apply to JK08A, while `VTC Valve Advance` does.
- Axis orientation: 29 of 37 two-axis catalog entries use `Engine Speed` on Y and cylinder filling
  on X. Stage 4 validates the `r5 -> :AXIS_X` / `r6 -> :AXIS_Y` convention from section 5 and
  refines orientation using the axis RAM input.
- Cross-ROM matching uses call-graph neighborhoods for accessor homologs,
  `(:Func)-[:HOMOLOG]->(:Func)`, then transfers map identity through
  `(:Map)-[:HOMOLOG]->(:Map)`. This accelerates an unfamiliar dump from an annotated one, such as
  JK08A <-> 1ND0A/JK78C/JK00D. It requires resolution of the second dump: 1ND0A currently has 1909
  `:Func` nodes and `:Reg` but no `:Map`. MAGE node2vec/embeddings are an optional neighborhood
  signal. Target JK08A and donor JK03A have separate code/map layers.
  `defs/rom-inheritance.toml` binds JK03A to the single live JK08A annotation set and verifies the
  relationship through SHA-256 and exact-code ranges. Transfer validation finds no differences
  across 2312 functions and 16 `rom_const` values; Stage 4 measures each image independently.
  Four unnamed candidate curves differ among 446 maps, while all 229 axes match.
- A constant anchor supplies a second homology signal independent of the call graph and does not
  wait for second-dump resolution. The anchor is a **block signature, not the number alone**.
  K-Factor `26806` (`0x68B6`) is identified by `0000 5E24 A5F0 FFFF [68B6]`, homologous across
  all six registered images: 1ND0A and 1ND3B at `0x9106`, JK78C at `0x8F80`, JK03A and JK08A
  at `0x9284`, and JK00D at `0x931C`. The value alone is insufficient. It occurs once at word
  alignment in four images but twice in exact-code pair JK03A/JK08A. The second occurrence at
  `0x162FA` lacks the signature, lies in data not covered by any of 446 catalog maps or 229 axes,
  and has no functions. It is a table cell whose value happens to match, not a second K-Factor.
  Exact code identifies `0x8FDC`/`0x8FDE` through `FUN_00047a56` as
  accelerator-pedal high-state hysteresis, so the nearby ProECU `Rev Limit - Fuel Cut
  Maximum` catalog entry cannot be assigned to that address. The working
  engine-speed fuel-cut table is independently localized at `0x934E`.

Matches provide `candidate` identity, not final semantics, encoding P6.

### Stage 6 - Flags: detect from a map, not through a global scan

The **primary path starts from an annotated map or code path**, not a full scan among thousands of
bit tests:

- **selector:** at an accessor or wrapper, identify what branches the `r4` load or axis pointer.
  The section 6 resolver follows both call-site branches to two bases and creates
  `(:Flag)-[:SELECTS]->(:Map)` for both.
- **gate:** identify a bit test that dominates the accessor call through a conditional skip and
  create `(:Flag)-[:GATES]->(:Func)`. Apply the same detection to immo guard functions found by
  `ScanImmoAnchors` from DTC anchors.
- **threshold:** identify a ROM constant in a path `cmp`, such as `0x934E`. It is a scalar and
  becomes editable in the definition after comparison semantics are identified.

Flag mechanics use the "GBR load - bit test - branch" triple:
`mov.b @(0x93,gbr),r0`, which Ghidra resolves to `0xFFFF4217`; `tst 0x1,r0`; and `bt`/`bf`.
A bit is set with `or.b 0x20,@(r0,gbr)` and cleared with `and.b 0xdf,@(r0,gbr)`.
**GBR has no global base.** Firmware reassigns it: `0x68cb8` contains both `ldc r0,gbr` and
`ldc.l @r15+,gbr` to address a different structure. Use Ghidra's resolved reference for the flag
address rather than adding base and offset manually; manual addition would produce plausible
addresses for the wrong cells.

`ScanFlags.java` runs **locally around accessors/dominators and guard functions**, not across the
whole firmware. A global bit-test scan is an optional noisy net for unresolved areas, not the
primary mechanism. Branch contents determine role, and branches come from the instruction CFG
through `getFlows()` and `getFallThrough()`. The containing block's exits are unsuitable because
there can be more than two with no indication of branch ownership. A branch whose sides cannot be
distinguished is emitted as `unknown`, a trace request rather than absence of a flag. At JK03A
accessor `0x82c8a`, 62 findings include selector `gbr+0x93 bit0`, which branches `r4` between
`0xb61a` and `0xb71a`. This previously traced annotation validates the detector.

Detection covers GBR-addressed flags. It does not cover a flag reached through a pool pointer to
an absolute RAM address.

### Stage 7 - Promote and verify

Apply section 5 gates. For `candidate -> code`, trace the specific semantics, contract, or scale in
code and provide evidence for that claim. A universal RAM-input/output pair is not mandatory:
inline comparison, return without a RAM write, and a proven dead branch require their own output
dispositions. `code -> silicon` requires CONSULT3P live data or a bench test. Store local levels in
`confidence`, `contract_conf`, and `scale_conf`, and their basis in the corresponding evidence
columns. Compute weakest-link confidence and grounding separately.

A reviewed `tools/pin-tracer` export can support this stage by linking an ESM terminal label through
the observed board topology to an MCU package pin. Use that link to verify the exact PFC
multiplexing, select peripheral registers, and prioritize their firmware xrefs. Continuity is
evidence for physical connectivity only: it does not establish Map/Axis semantics or runtime
behavior and cannot by itself promote such a claim to `silicon`. The current pipeline has no
pin-tracer JSON loader, so exports remain operator artifacts until board provenance, canonical
storage, and ingestion are implemented.

### Stage 8 - Emit the definition (resolves P5)

`tools/mapkit/emit_def.py` combines graph facts, `defs/<rom>.dtc.csv` DTC data, and
`defs/<rom>.overrides.toml` presentation into RomRaider `defs/<rom>.xml` and TunerPro
`defs/<rom>.xdf`. Section 9 defines the contract. Store projections only for a ROM with its own
live presentation layer. JK03A remains a graph measurement layer without separate `maps.csv`,
`overrides.toml`, XML, or XDF.

The presentation layer may define `presentation.default_emit = false` and opt individual
tables in with `emit = true`. This produces a stable tuner-facing allowlist while preserving
the complete reverse-engineering catalog in the graph and ledger.

For JK08A, `[map_switching].enabled = true` expands selected calibration families into
Map 1 through Map 5 inside the common `JK08A` definition identity. The canonical graph
catalog remains unchanged at 446 maps. The projected editor model contains 478 maps:
Map 1 reuses each canonical stock address, while Map 2 through Map 5 use the erased flash
allocations declared in `patches/map-switching-layout.toml`. Those additional slots contain
`0xFF` and are inactive under stock firmware; the map-switching patch is required before
they can affect runtime behavior. The slot number is part of each table name, while every
copy remains in the canonical functional category beside the original calibration family.
No separate map-switching definition identity is emitted.

The `defs/<rom>.maps.csv` ledger is a projection of the same catalog through
`tools/maps/build_tracker.py`: a reviewable graph snapshot visible in diffs and the analysis
worklist. `diag_priority` orders otherwise equivalent work toward maps with reviewed
diagnostic relevance, and `diagnostic_context` renders diagnostic identity,
firmware confidence, and source applicability without changing map semantics.
Context follows only a direct Map binding or an explicit Map/Axis `RESTS_ON`
path. An indirect result includes the path and evidence role, for example
`via map evidence: indexed_by` or `via map evidence: writes`. The same context
is emitted into RomRaider comments and TunerPro descriptions.
Open work is a `candidate` with empty `semantics`. There is no separate status
column because it would render confidence, role, and semantics and duplicate
neighboring facts, creating the type of divergence this design prevents.
Ledger, XML, and XDF are regenerated; edit the entry registry, manual layer,
diagnostic bindings, and overrides rather than generated files.

## 8. Explicitly unused tool capabilities

### 8.1 Ghidra decompiler data flow

Section 6 `ResolveAccessors` uses `HighFunction`, `PcodeOpAST`, and varnode define-use to
dereference argument pool pointers under condition A, fold backward slices, fall back to
`SymbolicPropogator`, and recover functions for unmarked sites under condition C. This resolves
P1. Other uses of `DecompInterface` currently produce text C only through `DecompileFuncs` and
`PoolUsers`. Unused capabilities include call-site prototype overrides through
`HighFunctionDBUtil.writeOverride` to clean CALLIND inputs, reconstruction of the GBR-based
calibration structure by typing `gbr` into named flag fields instead of `gbr+0x93`, and map-local
flag detection from Stage 6.

### 8.2 Memgraph/MAGE algorithms

**Projection is mandatory.** An algorithm called without a graph argument operates on all storage,
where 78k `:USES` edges dominate 6k `:CALLS` edges and `:Reg` connects any functions touching a
shared address. The effects are measured: raw `pagerank.get()` ranks RAM registers rather than
code, and `community_detection.get()` collapses 60% of ROM functions into one megacluster. Use a
single-ROM call-graph projection:

```cypher
MATCH p=(:Func {rom:$rom})-[:CALLS]->(:Func {rom:$rom})
WITH project(p) AS g
CALL pagerank.get(g) YIELD node, rank
RETURN node.addr, rank ORDER BY rank DESC LIMIT 15
```

Uses: PageRank/betweenness validates interpolation hubs in Stage 1 before Stage 3; BFS/path builds
caller trees in Stage 2; node2vec/embeddings can support cross-ROM homology in Stage 5. Louvain on
the projection gives a balanced subsystem map but does not isolate the access library (P3). Add
`:Map(addr)`, `:Axis(addr)`, and `:Flag(addr)` indexes to existing indexes.

**Agent access uses the `mcp-memgraph` MCP server** through project-scope `.mcp.json`, with
`run_query`,
`get_schema`, `get_page_rank`, `get_betweenness_centrality`, `get_node_neighborhood`).
It is headless-native and read-only: server-side policy blocks write Cypher, so the agent reads
through MCP while loaders retain all mutations. MCP analytical tools operate on complete storage;
use `run_query` with `project()` for project queries.

### 8.3 Multi-ROM graph as a homology join

Stage 5 homology turns annotation from one dump into an initial hypothesis for others. This is the
primary accelerator between VQ37VHR images 1ND0A/1ND3B/JK78C and annotated VQ25HR JK08A in both
directions.

### 8.4 Catalog-wide workflow over headless artifacts

Stage 2 deterministically identifies a catalog of 446 maps across census and manual families and
233 accessors: 141 use explicit axes, 114 use the bank, 25 use both census
families, and 3 additional accessors belong only to manual direct families. A catalog pass is therefore fan-out,
not discovery. Orchestration replaces a manual sweep and runs **over headless-produced artifacts
without a live GUI**. Stage 3 resolution and batch accessor decompilation through `DecompileFuncs`
over the Stage 2 list run headlessly first, producing graph facts, resolved operands, C pseudocode,
and listings. The flow is then **fan-out -> adversarial verify -> synthesize**. A separate verifier
checks every `code` claim: does the trace support the asserted semantics and does RAM attribution
agree? This is the P6 gate. The generator then re-emits the definition. GhydraMCP does not
participate in autonomous runs because it requires a GUI and one HTTP plugin would bottleneck
16 parallel agents. It remains optional for a live session with an open GUI. The project's immo
reverse engineering followed this same pattern.

Claude Code **Dynamic Workflows** are the runtime orchestrator; the tool API name is `Workflow`.
One Dynamic Workflow runs the primary package with `Analyze` and `Verify` stages connected by
`pipeline()`. A component claim enters verification immediately after analysis without a global
barrier. A parallel set of ordinary `Agent` calls is not a Dynamic Workflow, even if it preserves
the same artifacts, prompts, and blinding, and its results cannot enter synthesis.

Pass the frozen worklist through `Workflow` `args` as the actual item array, not a string or a
selection from the current ledger. Store `runId`, `scriptPath`, analysis count, and verified
`code`-claim count with the result. A targeted rerun or adjudication uses a separate one-item
Dynamic Workflow or continues the original run, never a direct `Agent` call. If `Workflow` is
unavailable or fails, the stage is blocked. Replacing it with ordinary subagents requires a
separate explicit decision; silent fallback is prohibited.

Evidence backfill uses property identity `(rom,label,addr,property)` rather than complete rows.
The JK03A manifest contains 78 claims on 58 nodes: 52 map-semantics claims, 20 map-scale claims,
and 6 axis-scale claims. Recovery replaces a complete frozen node with all properties, reads its
assigned blind artifact through EOF, and performs separate adversarial verification for every
field. Map semantics and scale resolve independently.

Caller-semantics harness `tools/sweep/caller_ab_experiment.py` has a closed-inconclusive
provider-neutral profile and a preserved historical profile. Frozen `closure-v1` defines an
operational contrast over six exposed JK08A maps and two identical-input controls:

```text
0000b23a 0000b33a 0000b71a 0000b81a
0000d78e 00011ede 00012262 0001462a
```

Selection and truth use commit `0269c11b7fc18b7e9619144ba8ffdf7eb7642bc5`. The LF-joined
address-list SHA-256 is
`e38b166b6bf48325e06bed365312fc8734db102b7ada073087c50e721ff6dd23`; the
diversity objective is `(8,6,2,5,3)`, and the tie-break SHA-256 is
`b2364bf70c978c7f3e36369d4318104c945409da4725860669c4b2457ddac944`.

`closure-v1` binds `tools/sweep/agent_protocol.py`, not a provider runtime. The protocol produces
isolated task batches containing only a worker prompt and JSON response schema. An
operator-selected Claude, Codex, other hosted, or local agent environment supplies exact
`vq.agent-task-results/v1` bundles. Receipts attest one fresh invocation per task, no domain tools,
fallback, retry, resume, or cache reuse, and embed raw output with its digest. Prep, both opaque
arms, and scoring must use the same provider/backend/model/effort/adapter descriptor. The complete
small-footprint execution contains 58 calls: 5 prep Analyze, 5 prep Verify, 16 map Analyze,
16 map Verify, and 16 blind scores. `tools/sweep/agent-workflow.md` defines the complete neutral
execution contract.

The registered `closure-v1` run stopped after the 10 Prep calls on 2026-07-30. Adversarial Verify
accepted two of five caller cards and refuted three; caller `000bef6e` also failed exact citation
binding. The mandatory Prep gate therefore prevented condition construction. No map-arm or score
calls ran, no operational contrast was estimated, and no claim entered the definition. The frozen
run is not retried or continued. A future attempt requires a separately preregistered experiment.

The historical `full-v4` profile measures the same contrast over 24 frozen focused JK03A map
items using Claude Code Dynamic Workflow v3. The selection commit is
`b02d3b7157d900a0654b1c63f2c200d8154d315b`, truth commit –
`849d76a6ea8f2fb931448bf7adb58b6739aa7a40`, SHA-256 of the LF-joined address list –
`4e9b97f9e9a46d183d96d549403e8264856e1128209f363c6dd1a85bdf3bcc94`, diversity objective
`(24,16,7,-4,-12)`, and selection tie-break SHA-256
`01889b5fbd018738bef760dd91cdd3fa8b4ef9660a4ed3923cee322d8ba77576`. Private schema v4
requires two separate builds of the 24 map artifacts and two blind audits. Exact inventories must
match byte-for-byte and contain no stale files or symbolic links. Each audit records frozen
budgets `8`/`24` and builder SHA-256, while the manifest embeds builder source for historical
validation. The complete Ghidra export root receives a recursive inventory of regular files with
paths, sizes, and SHA-256. Explicit call, function, decompilation, and accessor sources must be
included. HMAC-SHA256 with a private 32-byte secret hides condition/pair/job/card/score mappings;
public worklists contain neither truth nor mappings.

Execution configuration pins model `claude-opus-4-8`, effort `high`, the same platform-default
token budget, exact embedded prompts, Workflow scripts, and a project agent with exactly one
top-level `tools: []` field in YAML frontmatter, plus SHA-256 for every runtime source. No model
alias is used. Before the first agent call, saved workflows validate exact execution/item schemas,
counts, prompts, runtime-binding paths, and SHA-256 format. Execution input contains the frozen
schema, execution-config digest, and canonical live runtime binding. The Python control plane
binds embedded artifact text to its hash, binds citation ranges/excerpts to permitted code fences
in the same text, and verifies live source digests. `archive-workflow` repeats these checks before
archiving. A saved Workflow is not an independent cryptographic trust boundary.

The blind worker receives only embedded `artifact_text`; filesystem paths, parent-only opaque IDs,
and hashes are absent from its prompt. Prep uses only frozen Ghidra pseudocode and neutral `CALLS`,
without current or historical `Func.role`/`Func.semantics`. Comments and literal contents are
removed. Every semantic identifier, including automatic Ghidra `param`/`local`/`uVar` names, is
replaced with an address-derived neutral name or `ID_<n>`. Twenty-one
`Analyze -> adversarial Verify` pairs produce `caller-card-candidates/v1` with exact payload
digests rather than final cards. `role` and `semantics` must be printable ASCII English, and arm
markers are prohibited. Separate manual review compares every free-form `role`/`semantics` with
the cited frozen artifact. `finalize-cards` requires complete `caller-card-approvals/v1`, the
manual-review policy, operator attestation, and exact digests, then re-derives candidates from the
prep archive and creates cards v4. `build-conditions` does not accept candidates directly. Claude
Code loads the project-definition registry at startup; after definitions change, restart and run
the registry smoke test before first execution.

The two opaque conditions share one source map artifact and differ only in the caller-card block.
An exposed map receives approved role/semantics under `verified`; `placebo` keeps the same card
IDs, card count, and layout but inserts naturally worded deterministic neutral role/semantics.
Every control map receives one identical neutral sham card and a byte-identical artifact in both
conditions. The four directories for two `integrity_copies` must be distinct. The copies validate
files, while there is one stochastic LLM replicate using copy 1. The estimand is therefore the
observed contrast between approved caller text and neutral placebo, not a causal semantic effect
under tokenizer-identical input.

The same `vq-caller-run` performs 48 Map Analyze and 48 Map Verify calls. Run schema v4 stores
`machine_references`, not a directed trace. The order of 8-hex addresses creates no edge; scoring
measures coverage of the legacy truth-trace address set. Arm/condition markers are prohibited in
all free-form run-payload fields and verifier rationale before blind scoring. Validation decodes
HTML and removes comments and Unicode format controls. `accept_code` requires at least two unique
machine references. Short scalar constants are not machine references. The canonical
`provenance.py` parser handles evidence, and process tokens are prohibited. The current artifact
has no frozen typed-support registry, so run responses cannot contain dependency tokens
`role:addr[+offset]@target_prop`. Raw locations use terminal `site:addr`; addressless terminals
require a case-sensitive literal boundary match, and `rom_const` requires exact `addr=value` with
a nonempty canonical literal. Evidence anchors, targets, and machine references must appear in
both the artifact and exact nonempty fenced citations; unused citations are rejected. The
validator neither assigns semantic roles to C code by keywords nor derives directed edges from
line order. Blind verification and private scoring judge the semantic correctness of
role/disposition/target/semantics. Verifier returns the complete Analyze payload verbatim, and
Workflow plus pre-archive validation require exact equality.

The archive embeds actual script path, exact script source and SHA-256, args/result, complete
native Workflow output, and fresh-launch attestation. A persisted session script is accepted only
when its source hash exactly matches the runtime binding. Native root and result schemas are exact.
Result types, anchors, citation ranges/excerpts against embedded artifacts, Analyze/Verify
linkage, and completeness are validated before a completed archive is written. If progress
contains phase records, they must form the canonical sequence. Frozen agent records cover frozen
labels, contain exactly one `StructuredOutput` tool call per agent, report nonzero aggregate
totals, use one resolved model from the `claude-opus-4-8`/`claude-opus-4-8[1m]` allowlist, and
contain no fallback/retry/cache/error provenance in metadata fields or values. Prep, both runs,
and scoring use one resolved model. The validated run report is re-derived from source archives
and embedded sources.

Blind scoring creates 48 opaque worklist items. The scorer receives one JSON-encoded object with
reference/candidate semantics and no hashes, pair/condition ID, or sibling response; string
content cannot close the prompt delimiter. `factual_evidence` projects reference truth into the
same terminal-only run domain, excluding prohibited dependency/process tokens from the
denominator. All 48 calls and raw scores are stored independently, with no pooling, averaging of
byte-identical payloads, retry, or fallback. The falsification gate checks every control and every
component, including `machine_reference_coverage` and `verifier_accepted`, separately. Any
verifier split invalidates the gate; maximum absolute delta must be `<= 1/7`; opposing control
deltas do not cancel. Failure yields `status=invalid_controls` and `observed_paired=null`.
Success yields `status=controls_passed`. With one replicate, the result remains an observed paired
contrast and `causal_claim=false`. The complete experiment contains 186 agent runs. Saved
workflows accept an execution object or complete JSON object string, not a file path. The harness
does not write canonical CSV, does not promote claims to `silicon`, and always emits
`automatic_application=false`. `map-sweep.md` defines the complete contract, frozen addresses,
and phase CLI. The experiment is not considered launched under this contract before all required
checks complete.

Blind audit, cohort digest, runtime binding, manual card approval, and Workflow archive validate
local reproducibility but do not cryptographically attest a trusted runner. Operator attestation
records the asserted fresh launch. A user able to modify all local inputs consistently remains
inside the trust boundary.

The fan-out unit is a connected accessor -> map component, not a map. One consumer trace covers
all maps read by an accessor, while multiple accessors can read one map. One agent per map would
repeat the same trace N times and assert different facts about one node. Agents read artifacts
rather than the graph because annotation and shape coexist there, making graph-access blinding
impossible. Preparation defines artifact content. `map-sweep.md` defines the work unit, wave order,
pilot blinding, claim schema, and gates.

## 9. Definition generator contract (graph + DTC + overrides -> XML + XDF)

`emit_def.py <rom>` reads the graph, `defs/<rom>.dtc.csv`, and
`defs/<rom>.overrides.toml`, then writes `defs/<rom>.xml` for RomRaider and
`defs/<rom>.xdf` for TunerPro. Optional second and third arguments select the two output
paths. The command targets a canonical ROM with its own presentation layer. JK08A is
the current user-facing definition for the exact-code JK03A ROM:

- **Facts from the graph**: addresses, dimensions, storage type, axes, scaling
  (`units`/`scale_expr`/`to_byte`), and local map and scale confidence
  (`confidence`, `scale_conf`). Editor orientation is derived from finisher geometry:
  `cell = table + idxY + idxX*width` gives columns from the graph Y axis and rows from
  the graph X axis. RomRaider receives child `<table>` axes and evidence comments.
  TunerPro receives `XDFAXIS` objects and evidence descriptions. Claim evidence remains
  in the source and graph rather than becoming a second fact source in either artifact.
- **DTC registry** (`defs/<rom>.dtc.csv`, tracked in git): index, code, address of the
  12-byte descriptor, address of the associated uint16 attribute, and its stock and
  disabled values. The generator verifies each record against the exact stock ROM from
  `rom-images/roms.csv`. In RomRaider, every `code`-level row receives a native
  descriptor `TableSwitch`; a second attribute `TableSwitch` is emitted when the stock
  and disabled attribute values differ. The controls are numbered `1/2 Descriptor`
  and `2/2 Attribute`, remain adjacent in one `Diagnostics / DTC` category, and must
  use the same state before the ROM is saved. In TunerPro, every row receives one
  atomic `XDFPATCH` containing one or two entries. The generator also emits one atomic
  patch for each manifest `group`. The 36 individual patches and seven group patches
  each cover the same 71 mutable ranges at their respective scope; no all-DTC patch is
  emitted. P1610 has a stock-zero attribute and therefore receives only a descriptor
  switch or patch entry.
- **Presentation overrides** (`defs/<rom>.overrides.toml`, tracked in git):
  tuner-definition visibility, human-readable names, `category`, table ordering, editor increments
  (`format`/`fine`/`coarse`), the `romid` block, `<checksum>` parameters, a `mask` for
  independent editing of element bit fields, cosmetic comments, and cell labels for a
  map without an axis. `presentation.default_emit` defaults to `true` for compatibility;
  a table-level Boolean `emit` overrides it. JK08A sets the default to `false` and explicitly
  selects its working calibration set. Hidden tables retain their graph facts and override
  records and remain visible in the ledger. The manual `direct-row-major` family defines both static axes in
  this layer: `static_axis_x` has `width` elements and `static_axis_y` has `height`
  elements; geometry and element type remain facts in `findings.csv`. An implicit
  one-dimensional map may define `static_axis` labels that replace the generated raw
  input nodes when a physical conversion is reviewed; its implicit step and geometry
  remain graph facts. The optional `[map_switching]` table enables a definition-only
  projection from `patches/map-switching-layout.toml`. The projection retains the
  canonical ROM identity, uses canonical storage for Map 1, and adds Map 2 through
  Map 5 at their reserved addresses without adding speculative `:Map` nodes to the
  graph. A
  `[[masked_view]]` array creates an additional view of the same cells: `source`
  references an emitted map, its separate `mask` does not overlap the primary table
  mask, and shape and axes are reused from the Map fact. This exposes a value field and
  bit flag independently without a second map node. RomRaider applies its native table
  mask. XDF has no table-mask attribute, so TunerPro receives an invertible per-cell
  conversion with a same-address raw variable: editing one field preserves the
  complementary bits. Records merge on `{rom, addr}`. An override that replaces a fact
  is an error (`static_axis` with a live `:Axis` stops the run), as are an unknown map
  address and an unnamed visible map that passes the interpretation gate.
- **Presentation gate**: evaluate only maps selected by the presentation policy for
  tuner-definition output. Hidden maps are counted separately from interpretation
  failures and are not required to carry complete editor geometry.
- **Interpretation gate**: emit selected content that can be interpreted: role `table`, nonempty
  semantics, and nonempty scaling at `confidence >= candidate`; levels below
  `candidate` are not emitted. A map without semantics is only an address and shape; a
  map without scaling is only a grid of raw bytes. Both are already represented in the
  ledger. The generator lists rejected selected records because silent omission would be
  read as an incomplete working definition. Ambiguous geometry, such as a branch-selected axis represented by
  more than one axis on an edge, closes the gate and moves to Stage 6. A direct
  rectangular map without axis edges passes only as `direct-row-major` and only with a
  complete pair of static axes. A manual one-dimensional `direct-indexed` map passes
  only with one static label per cell.
- **Confidence labeling** is attached to the claim it qualifies: a map below `code`
  is marked `[candidate]` in the generated evidence comment, while a scale below
  `code` receives a unit suffix `[cand]`. Categories remain functional and do not
  partition maps by confidence. The multiplier is a claim about values, not
  identification of the table, so these levels can differ. At `0xB61A`, for example,
  code establishes the address while the `x-64` multiplier comes from the A2L catalog.
  Overrides may specify an ordered `<checksum>` array for RomRaider. For JK08A, the
  native handlers `alt` and `alt2` reproduce the stock fields and run in B -> A order.
  The XDF contains no `XDFCHECKSUM`; checksum correction belongs to the flashing
  workflow rather than the TunerPro definition contract.

The generator template follows the `AGENTS.md` rules for declarative prose, en dashes,
ASCII arrows, quotes, and comparison operators. Table and axis names are English
because they are editor interface strings and the definitions are used outside this
project.

## 10. Build backlog

The existing toolset remains in use:
`ExportGraph`/`ExportXrefs`/`FindTableRefs`/`DumpListing`/`DecompileFuncs`/
`RenameFuncs`/`RecoverFuncs`/`MapInventory`/`DirectLookupInventory`/`ResolveAccessors`/
`ScanImmoAnchors`/`FindInterpCore`/`ScanFlags`/`ExportDiagnosticRefs`/`TraceRamAccesses`/
`load_graph`/`load_xrefs`/`load_maps`/`load_code`/`load_diagnostic_bindings`/
`ingest`/`provenance_report`/`load_a2l`/`load_vendor`/`build_catalog`/
`extract_static_bindings`/`build_tracker`/`build_artifacts`/`mapkit`/
`queries.cypher`.

The structural pipeline and claim-specific Map/Axis evidence backfill are implemented.
Open work consists of follow-up analysis of `candidate` maps without semantics, flags,
homology, the throttle-based cutoff path, and hardware validation of the bound
injection and intake-CVTC diagnostic values. Hardware-loop verification is outside
the static pipeline milestone.

`tools/memgraph/ingest.py` enforces the graph build sequence:
`load_graph -> load_xrefs -> load_maps -> load_code ->
load_diagnostic_bindings -> audit`. Catalog references (`load_a2l.py` +
`load_vendor.py`) and the diagnostic corpus are family-wide; the ledger and XML
are built only after a successful audit. The catalog covers both access families
plus the manual layer: all 446 catalog maps are graph nodes. Three call sites
retain an explicit dynamic base and create no speculative map node.

The work sequence is therefore catalog sweep (section 8.4; contract in `map-sweep.md`;
unit of work is one of 171 connected accessor -> map graph components; the first wave
is a pilot on component `0x82C8A`, where traces have established 6 of 14 maps and
provide an answer key) -> flags (Stage 6, `ScanFlags.java`; inputs are accessors for
maps labeled by the sweep and 14 `pattern`-level axes).

Flags follow the catalog because Stage 6 detects them relative to a labeled map, so its
yield grows with coverage. The sweep, rather than the 15 projected accesses with an
unresolved base, supplies its input. `ScanFlags` finds no flags across the 25 accessors
for those sites, although GBR accesses and `tst` are present. On SP-based sites, the
base is selected by an index rather than a bit. Operand-set expansion identifies
register-indexed table arrays (`0x64344`: six tables through `r5`; `0xbe39a`: two
through `r13`), while `0x68cb8` branches on `cmp`. Resolver branch enumeration, not
flag detection, closes the final four maps and SP-based sites. The same treatment
applies to the other half of this mechanism: a branch-selected axis. `0x14114` carries
two axes on one edge (`0xE98E` and `0x8000`, where the flash is erased), and
backtracking alone reports both.

The canonical working allowlist selects 12 of the 446 catalog maps and adds three
masked ignition views. The common JK08A projection expands eight selected calibration
families into 40 Map 1 through Map 5 tables and two masked families into ten slot views.
The emitted definition therefore contains 44 calibration tables and 11 masked views
without standalone reference axes. The other 434 canonical maps remain available for
reverse engineering in the graph and ledger. The catalog contains 308 `code` maps and
138 `candidate` maps. Semantics are present for 389 maps and `scale_expr` for 355. The
ledger has 57 open `candidate` maps without semantics. The `vals` column divides this
work: 17 open maps contain one value across the entire table. `mapkit` also closes
Stage 5 `:MATCHES`: reading the axes, rather than the catalog, provides match keys such
as scale family and axis semantics. Cross-ROM homology, the second half of P7, awaits
resolution of 1ND0A.

## 11. Metrics and effectiveness gates

"Effective" is measurable from the graph with one query. The historical baseline was
measured on the exact-code JK03A donor. The current JK08A fact was rebuilt from 553
sites, 61 without `r4`, for **492/553 = 89%** resolution. Target gates:

| Metric | Query | Baseline -> JK08A fact | Target |
|--------|-------|------------------------|--------|
| Operand resolution | share of call sites with resolved `r4`, otherwise explicit `dynamic` | 89% -> **99.5%** (583/586) | >= 95%; 0 silently lost |
| No regression against backtracking | sites where backtracking returned an in-ROM value but data flow did not | n/a -> **1, reviewed** (`0x56cd8`: value from an unreachable branch, not a base) | all reviewed |
| Latent catalog defects | number of `conflict` results (`bt != df` at a site) | not measured -> **14, all reviewed** (6 base conflicts: reference wrong in every case; 3: unreachable branch and stale registers; 5: `mov.w` constant read as 32-bit by the reference). Four more base differences moved out of this class after operand-set expansion (section 6): the mechanisms selected different branches of one selector | all reviewed |
| Catalog completeness | number of `:Map` nodes against known inventory; 0 maps outside graph | 223 bases in ledger, 0 in graph -> **446 of 446 in graph** across census and manual families; three dynamic call sites create no speculative map | every catalog map in graph; dynamic bases remain explicit |
| Definition gate | number of emitted maps below `code` without explicit `[candidate]` evidence comment | not tracked -> **0**: the common definition emits 44 `code` maps and 11 masked views; it emits no standalone reference axes | 0 unmarked |
| Catalog geometry | number of `:Map` nodes without `storagetype`, which prevents emission | 66 of 441, all 2D -> **0**: 2D element type comes from the finisher | 0 |
| Definition readability | number of emitted maps whose scale is below `code` | not tracked -> **33** of 44; candidate scale remains visibly marked | traces remove `[cand]` without inventing scale |
| Deferred axes | number of `pattern`-level `:Axis` nodes reported only by backtracking with `k5`/`k6=sp` | not measured -> **14 of 229**; `0x8000` is erased flash; none pass emission | 0; Stage 6 resolves them |
| Axis against core code | number of `:Axis` nodes with `monotonic=false`; reverse linear search cannot read such an array | not measured -> **1 of 229** (`0x119B2`; its map `0x9C5A` is entirely `0xFF`). This caught an axis element declared from the core rather than the wrapper/axis pair: 2 of 22 wrappers and 2 axes had been read as words instead of bytes | 0 |
| Measured layer | number of `:Map`/`:Axis` nodes without values from the image, meaning shape without contents | not tracked -> **0 of 446 and 229**: the same run that builds the layer reads the image | 0; a read miss stops loading |
| Output disposition of `code` maps | structured evidence distinguishes writes, consumer, inline comparison, return, and dead control flow | format active: focused positions 50-395 covered 346/346; backfill retained 41 prior `code` Map semantics claims with a disposition and downgraded 11 unsupported claims | 100% of `code` Map semantics |
| Static diagnostic bindings | reviewed claims with resolved firmware, diagnostic, source-claim, and evidence targets; exact-ROM rows must not cross inheritance | **JK08A 145, JK03A 29**; JK08A has 116 exact-ROM DTC claims and 29 exact-code parameter claims; direct or provenance-reachable context prioritizes 49 of 446 JK08A maps and 35 of 446 JK03A maps | every loaded row resolves exactly once; hardware validation remains explicit |
| Identity coverage | share of `:Map` nodes with `:MATCHES` or `:HOMOLOG` | 0; references are in the graph (188 `:A2LEntry`, including 106 maps; 371 `:VendorEntry`, including 243 factory entries); match keys follow Stage 4 | advisory, increasing |
| Dictionary convergence | number of `concept` values shared by A2L and both vendors | not measured -> **17 of 23** labeled; `concept` is present on 45 of 188 A2L records and 170 of 371 vendor records, representing 49 values | increases with analysis; 100% is impossible because A2L has no VVEL entries (0); Stage 6 labels flags |
| Vendor anchors in image | number of `:VendorFact {kind:'const'}` values found in the dump | 22 documented -> **1 found** (K-Factor `26806`: block signature in all 6 registered ROMs) | search all; a bare value match is `pattern` (two in JK03A/JK08A), block signature is `candidate`, trace is `code` |
| Static completion | reviewed diagnostic and map claims required by the software-only worklist | confidence is capped at `code`; hardware-loop evidence is unavailable | no hardware or `silicon` gate in this milestone |

These values define pipeline effectiveness and regression control. A run that lowers
resolution or admits a map below `code` into the active definition fails the gate.

### Claim-specific provenance

Offline preflight and `provenance_report.py audit` calculate metrics using the complete
identity `(rom,label,addr,property)`. Source nodes, factual evidence for every
`code`/`silicon` property, and exact edge projection are mandatory local gates. Global
`--strict` additionally requires no effective downgrade and no ungrounded claims
anywhere in the graph. It is a separate diagnostic, not a condition of local backfill.

| Metric | Check | JK08A fact | Target |
|--------|-------|------------|--------|
| Source claims | strict rows across all four CSV files | **1227**; manual files contain 367 annotated functions in `funcs.csv`, 311 variables in `vars.csv`, 389 map findings in `findings.csv`, and 24 axis findings in `axes.csv` | entire schema resolves |
| Evidence projection | expected against actual by complete edge key | **3867 expected `:RESTS_ON` edges**; `missing=0`, `extra=0`, `duplicate_expected=0`, `duplicate_actual=0`, `unresolved=0` | all five counters are 0 after ingestion |
| Local code-layer gate | `code`/`silicon` Func/Reg/Map/Axis without factual evidence | **0**; frozen debt of Map semantics 52, Map scale 20, and Axis scale 6 is closed | 0 |
| Weakest link | `code`/`silicon` where effective level is below declared | **0**; all `code` claims retain their declared level | 0 |
| Transitive grounding | `code`/`silicon` without a terminal, structural support, or grounded leaf | **0** | 0 |
| Cycles | SCCs and ungrounded SCCs | **39 SCCs, 0 ungrounded** | a cycle cannot support itself |
| Map/Axis evidence backfill | frozen decisions by property identity | **78 of 78**: 28 `accept`, 27 `revise`, 23 `downgrade`; result is 55 `code` and 23 `candidate` | unresolved=0, local debt=0 |
| Core code in artifact | cores without a `:Func` whose listing is present in an artifact | **6 of 6** | 100% |

`from_map@structural` separates a dependency on map existence and geometry from a
dependency on its semantic confidence. Consequently, 141 `candidate` maps out of 446
do not automatically downgrade proven table-reading code.

## 12. Reproducibility and invariants

- Repository sources tracked in git: extractors and loaders, queries, `mapkit`,
  `symbols.csv`, the A2L donor (submodule `defs/reference`), vendor dictionaries in
  `refs/vendor/`, and the image registry `rom-images/roms.csv`.
  The P5 calibration layer consists of `defs/<source>.interp.csv`,
  `defs/<source>.findings.csv`, `defs/<source>.axes.csv`, and
  `defs/<source>.diagnostic-bindings.csv`, and
  `defs/<source>.overrides.toml`; the code and provenance layer consists of
  `defs/<source>.funcs.csv` and `defs/<source>.vars.csv`. The canonical `<source>` is
  selected by `defs/rom-inheritance.toml`, which is tracked in git and fixes the
  exact-code relationship using SHA-256 and code ranges. The Ghidra project and
  Memgraph data are reproducible and untracked. After preparing the headless export,
  `tools/memgraph/ingest.py <rom>` reconstructs them.
- Handwritten sources: `symbols.csv` for function names,
  `defs/<source>.interp.csv` for interpolation input geometry and axis element type,
  `defs/<source>.findings.csv` for map findings, units, and confidence,
  `defs/<source>.axes.csv` for axis semantics and units,
  `defs/<source>.overrides.toml` for presentation, `defs/<source>.notes.md` for the
  evidence journal, `defs/rom-inheritance.toml` for target -> canonical source,
  `rom-images/roms.csv` for ROM label -> dump path and SHA-256,
  `refs/vendor/proecu-maps.csv` and `refs/vendor/uprev-maps.csv` for verbatim vendor
  dictionary transcription, and `refs/vendor/facts.csv` for documentary anchor facts.
  Table and axis values do not enter source files: the image itself supplies them, and
  Stage 4 reads them on every run. `refs/vendor/catalog.csv` is generated by
  `tools/vendor/build_catalog.py`; it combines both transcriptions and carries derived
  columns (`origin`, `concept`). Editing it directly could silently diverge from the
  dictionaries. The graph, ledger, and XML are generated. Changes belong in their
  sources because the loader recreates layer nodes and direct graph edits would not
  survive ingestion.
- Gate: the active definition emits maps at `candidate` or higher. Every `candidate`
  map is explicitly marked in its category, units, and comments. Only `silicon`
  claims may be flashed to an engine. Per `AGENTS.md`, ground truth is in the silicon
  and graph structure is not semantics.
- Direction: edit CSV sources and overrides -> Ghidra + Memgraph + definition. Changes
  in the opposite direction, such as renaming in the GUI/Lab or editing the graph or
  generated XML, do not return to git.
