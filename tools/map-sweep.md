# Catalog-wide sweep contract

The map-catalog sweep turns an inventory of known tables into annotations. Claude Code
**Dynamic Workflows** orchestrate the sweep through the `Workflow` tool API. A parallel set of
ordinary `Agent` calls is not a substitute. Section 8.4 of `map-flag-pipeline.md` defines the
Dynamic Workflow architecture; this document defines the run contract: work unit, wave order,
pilot blinding, claim schema, and gates.

Input is the catalog after Stage 4, with shape and content recovered and values measured from the
image. Output is rows in canonical `defs/<source>.findings.csv` and
`defs/<source>.axes.csv`, from which the loader builds the layer and the generator re-emits the
definition. `defs/rom-inheritance.toml` resolves `<source>`; a sweep of an inheriting ROM does not
create a second annotation set.

## 1. Work unit: component, not map

A consumer trace identifies a map. One accessor reads several maps and one trace covers them all,
while one map may be read by multiple accessors. Assigning one agent per map would make N agents
repeat the same trace and assert different facts about one node.

The work unit is a **connected component** of the bipartite accessor -> map graph:

```cypher
MATCH p=(:Func {rom:$rom})-[:ACCESSES]->(:Map {rom:$rom})
WITH project(p) AS g
CALL weakly_connected_components.get(g) YIELD node, component_id
WITH component_id, collect(node) AS nodes
RETURN component_id,
       [n IN nodes WHERE 'Map'  IN labels(n) | n.addr] AS maps,
       [n IN nodes WHERE 'Func' IN labels(n) | n.addr] AS accessors
```

This unit has two required properties:

- components are independent **by construction**: two components share neither a map nor an
  accessor, so agents do not compete for a node or dispute one fact;
- all evidence for a map is available to one agent: its accessors, their traces, and maps read by
  the same code.

### Focused mode with a frozen worklist

Sequentially closing exact positions in an immutable worklist uses one `map-<addr>.md` as a
Dynamic Workflow item. The item boundary matches the batch position so synthesis cannot absorb
neighboring maps from the same component outside the frozen slice. The artifact still carries the
complete connected-component context: accessors, traces, and neighboring maps. Evidence therefore
remains component-scoped, while a map is only the packaging and result-write boundary. Multiple
items from one component may repeat context; synthesis accepts only the exact frozen batch
worklist. Complete waves without a positional boundary use a component as the item.

### Property-specific frozen backfill

Evidence backfill freezes claim identities `(rom, label, addr, property)`, not entire rows.
The `tools/sweep/evidence_backfill.py` manifest binds each claim to an immutable git blob, source
row digest, and blind-artifact SHA-256. JK03A freezes 78 claims across 58 nodes:
52 `Map.confidence`, 20 `Map.scale_conf`, and 6 `Axis.scale_conf`. Map semantics and scale are
resolved independently; confirming one property does not confirm another.

Map focus preserves component context for one frozen map. Axis focus builds `axis-<addr>.md` from
all directly related maps and accessors so a shared axis is not represented by an arbitrarily
selected map. Two independently built sets must match by name and SHA-256, pass blind audits, and
cover all 58 nodes before Workflow launch.

### Paired JK03A direct-caller-semantics experiment

`tools/sweep/caller_ab_experiment.py` provides a separate read-only control plane for measuring
the contribution of preverified direct-caller semantics to focused map analysis. Its CLI has no
command that applies results or writes `defs/*.csv`. The private manifest, execution inputs,
artifacts, Workflow archives, and reports are stored outside git.

Frozen `selection-v1` contains exactly 24 maps:

```text
0000a29a 0000ab4a 0000b23a 0000b33a 0000b71a 0000b81a
0000d78e 00011ede 00012262 000122b2 00012312 00012908
00012a32 00012a62 00012e1a 00012e3a 00012fc6 000131a2
00014114 0001462a 0001473a 0001488a 0001497a 00016f48
```

Addresses are joined with LF and no trailing LF. The list SHA-256 is
`4e9b97f9e9a46d183d96d549403e8264856e1128209f363c6dd1a85bdf3bcc94`. The selection
commit is `b02d3b7157d900a0654b1c63f2c200d8154d315b`; the closed-truth commit is
`849d76a6ea8f2fb931448bf7adb58b6739aa7a40`. The diversity objective is
`(24,16,7,-4,-12)`, and the SHA-256 selection tie-break is
`01889b5fbd018738bef760dd91cdd3fa8b4ef9660a4ed3923cee322d8ba77576`. The sample has
21 unique direct callers, 22 exposed maps, and 2 identical-input controls.

The execution contract freezes:

- model `claude-opus-4-8`, effort `high`, one stochastic replicate, and the same
  platform-default token budget for one response schema; no model alias is used;
- SHA-256 and complete embedded source for the three Workflow scripts
  `.claude/workflows/vq-caller-{prep,run,score}.js`, exact prompts, and project agent
  `.claude/agents/vq-ab-blind-worker.md`;
- `tools: []` for the blind worker and policy
  `embedded_artifact_no_tools_exact_single_structured_call`;
- fresh-only execution with explicit operator attestation and no resume, cache reuse, retry, or
  fallback model;
- the exact native Workflow root schema; if native output contains phase records, they form the
  canonical phase sequence; the complete expected label set, exactly one `StructuredOutput` tool
  call per agent run, nonzero aggregate totals, and one resolved model from the
  `claude-opus-4-8`/`claude-opus-4-8[1m]` allowlist;
- an archive envelope containing `runId`, actual `scriptPath`, `scriptSha256`, `scriptSource`,
  exact `args`, `result`, complete native `workflowOutput`, `status`, and `launch`. A persisted
  session copy of a Workflow script is permitted only when its source SHA-256 exactly matches the
  runtime binding. Historical validation uses embedded source, while the live agent/workflow
  SHA-256 must match the execution input before archiving. Python preflight additionally binds
  every embedded `artifact_text` to its `artifact_sha256`, and citation ranges/excerpts to
  permitted code fences in the same text. A saved Workflow is not an independent cryptographic
  trust boundary.

Claude Code loads the Workflow and project-agent registries at startup. After first adding or
changing definitions, restart the session before the smoke test. The smoke test verifies the
presence of `vq-ab-blind-worker`, actual `tools: []`, exactly one `StructuredOutput` call, no
fallback/retry/cache behavior, and invocation of all three `vq-caller-*` workflows through both
object and JSON-string args. A missing definition or mismatched native schema is a blocking
condition, not grounds to fall back to an ordinary agent with repository access.

Phase contract:

1. Two separate focus-map builder runs create the 24 source `map-<addr>.md` files in different
   directories using the standard command with `--audit-output`. `freeze` requires both
   directories and both audit JSON files, verifies distinct paths, exact inventories without stale
   files, and byte-identical SHA-256 for every address. Each audit records embedded builder source
   and SHA-256, the Ghidra export directory, budgets exactly `8`/`24`, and a successful blind gate.
   The CLI rejects negative budgets. An additional conservative literal/normalized scan searches
   both sets again for private truth.
2. `freeze` re-derives private schema v4 from pinned git blobs and frozen exports. It inventories
   the entire Ghidra export cohort root recursively: every regular file receives a relative path,
   size, and SHA-256, and symbolic links are prohibited. `calls.csv`, `funcs.csv`, `decomp_*.c`,
   and `accessors.*.csv` must be present in this inventory, and both blind audits must reference
   the same root. The manifest stores truth, `map -> accessor -> direct caller`, two artifact
   inventories, execution configuration, embedded builder, and the private condition mapping.
   Condition, pair, job, card, and score IDs are derived through HMAC-SHA256 with a private
   32-byte secret. Public worklists contain no secret, truth, or condition mapping.
3. `build-prep` constructs 21 caller-only artifacts exclusively from frozen Ghidra pseudocode and
   neutral `CALLS`. Comments and string/character literal contents are removed while line breaks
   are preserved. Human-authored function/data symbols and all other semantic identifiers are
   deterministically replaced with address-derived `FUN_`/`LAB_`/`DAT_` names or `ID_<n>`.
   This rule also covers automatic Ghidra names with prefixes such as `param`, `local`, and `uVar`.
   Current or historical `Func.role`/`Func.semantics`, relations to a selected map, and closed
   answers are prohibited. Sample addresses and matches to private truth are masked; the
   literal/normalized leak scan fails closed. Prep execution input removes `artifact_path` and
   embeds assigned `artifact_text` directly in the item. Opaque IDs and hashes remain with the
   Workflow parent and are attached to the structured result only after the blind worker responds;
   they are absent from the model prompt.
4. One `vq-caller-prep` run performs 21 `Analyze` and 21 adversarial `Verify` calls. Workflow
   displays the artifact as `N|RAW_LINE`; each structured citation stores a one-based range and
   exact raw excerpt without the line-number prefix. Verify must return role, semantics, and
   citations verbatim. Workflow checks this equality and binds citations to the embedded artifact,
   and the pre-archive validator repeats those checks. Verifier rationale passes the same
   arm-neutrality validation. `validate-prep` accepts only complete coverage, single-line
   target-independent printable-ASCII-English `role`/`semantics`, ranges and excerpts inside the
   `Machine evidence` fence, and no direct or HTML-encoded arm markers `verified`, `placebo`,
   `baseline`, `treatment`, or `enriched`. The command produces schema
   `vq.caller-card-candidates/v1`, not final cards. Every candidate contains an exact-payload
   digest. A separate manual review compares free text with the cited frozen caller artifact and
   creates a complete `vq.caller-card-approvals/v1` with exact payload digests,
   `manual_exact_payload_against_cited_frozen_artifact`, and operator attestation.
   `finalize-cards` rejects missing approvals, rejections, and digest drift, re-derives candidates
   from the immutable worklist, execution input, and complete Workflow archive, and only then
   creates `vq.caller-semantics-cards/v4`.
5. `build-conditions` accepts only finalized cards with revalidated candidates and approvals and
   inserts an identically formatted caller-card block into source map artifacts. In the private
   `verified` condition, each exposed map receives frozen cards. In the `placebo` condition, the
   same card IDs, card count, and layout receive naturally worded deterministic neutral
   `role`/`semantics` selected by opaque card ID. Every control map receives the same neutral sham
   card and a fully byte-identical artifact in both conditions. The estimand is the observed
   operational contrast between verified caller text and neutral placebo, not an abstract semantic
   effect under tokenizer-identical input. Each condition has two byte-identical
   `integrity_copies`; all four directories and their file sets must be distinct. These are file
   checks, not additional LLM runs. Only copy 1 executes, with `stochastic_replicates=1`.
   `verify-artifacts` checks exact schemas, inventories, SHA-256 values, absence of symbolic links,
   card inventory, bytes outside the block, the exact block for each condition, and identical
   controls.
6. The same `vq-caller-run` executes separately with two opaque execution inputs. Each item
   contains embedded artifact text without a path or sibling condition, and the model sees lines
   as `N|RAW_LINE`. Each condition requires 24 `Analyze` and 24 adversarial `Verify` calls. Run
   schema v4 stores `machine_references`, not a directed trace: it is a sequence of 8-hex addresses
   used for membership validation and score coverage, and textual order creates no edge. Short
   scalar constants are excluded. Only the canonical parser in `tools/memgraph/provenance.py`
   parses evidence. Because the current frozen artifact has no separate typed-support registry,
   dependency tokens `role:addr[+offset]@target_prop` are prohibited in run responses. A raw
   machine location is recorded as `site:addr`, while addressless terminals require a
   case-sensitive literal boundary match in the citation. `rom_const` requires `addr=value` with a
   nonempty canonical literal. Every evidence machine anchor, result target, and machine reference
   must occur both in the artifact and in an exact nonempty citation from a fenced code block;
   unused citations are rejected. Validation derives no directed edge from line adjacency or
   address order. `accept_code` requires at least two unique machine references and a resolved
   disposition; `accept_code + unresolved` is prohibited. Semantic correctness of `role`,
   `disposition`, target, and semantics remains the responsibility of blind Analyze, adversarial
   Verify, and private scoring rather than heuristic C-text keyword parsing. Arm and condition
   markers in all free-form run-payload fields and verifier rationale are rejected before score
   worklist construction; validation decodes HTML and removes comments and Unicode format
   controls. Verifier returns the complete Analyze object verbatim, and both Workflow and the
   pre-archive validator require exact equality. If the two fresh archives contain native phase
   records, those records must form the canonical phase sequence. The frozen agent record type
   must cover exactly 48 labels, contain exactly one `StructuredOutput` call per agent run,
   satisfy `totalToolCalls == agentCount`, report nonzero `totalTokens`, use one resolved model from
   the `claude-opus-4-8`/`claude-opus-4-8[1m]` allowlist, contain no fallback/retry/cache/error
   provenance in metadata fields or values, and contain the exact result. Before writing a
   completed archive, `archive-workflow` validates result schema, types, anchors, and completeness.
   Prep, both runs, and score must use one resolved model. The report is re-derived from source
   archives.
7. `build-score` creates 48 opaque items. The blind scorer sees only one JSON-encoded object with
   `reference_semantics` and `candidate_semantics`, without hashes, pair ID, condition ID, mapping,
   or sibling response. Strings are treated as quoted data, and JSON encoding prevents their
   content from closing a text delimiter. The Workflow parent attaches score ID and candidate
   SHA-256 after the response. `vq-caller-score` executes and stores all 48 independent calls.
   Even byte-identical control payloads retain two raw scorer observations; there is no pooling,
   duplicate averaging, or repeat call. Controls can therefore observe stochastic scorer drift
   with one replicate.
8. `compare` joins results only through the private mapping. Reference factual evidence is
   projected into the same terminal-only run domain; prohibited dependency and process tokens are
   excluded from the denominator. Seven substantive components remain as raw scores. A verifier
   `refute` sets the gated total to zero. The falsification gate checks every control and every
   component separately: the maximum absolute delta among `decision`, `role`, `disposition`,
   `target`, `factual_evidence`, `machine_reference_coverage`, `semantics`, `raw_total`,
   `verifier_accepted`, and `total` must be `<= 1/7`; any `verifier_accepted` mismatch also
   invalidates the gate. Opposing control deltas do not cancel. On failure, status is
   `invalid_controls`, `observed_paired` is `null`, and raw output is retained for diagnosis. On
   success, status is `controls_passed` and `observed_paired` reports mean/median,
   wins/ties/losses, and field deltas for 22 exposed maps. One stochastic replicate does not
   support causal interpretation, so `causal_claim=false`. Native output attests aggregate run
   token/tool totals but not per-item monetary costs, so costs have `measured=false`.
   `automatic_application=false` is mandatory.

One complete execution contains 186 agent runs: 21 prep Analyze, 21 prep Verify, 48 map Analyze,
48 map Verify, and 48 blind semantics scores. Manual card approval creates no LLM runs.
Independent code review is excluded from this count.

The CLI provides `freeze`, `build-prep`, `archive-workflow`, `validate-prep`,
`finalize-cards`, `build-conditions`, `verify-artifacts`, `validate-run`, `build-score`,
`validate-score`, `compare`, `status`, and standard `--help` commands; every path is explicit.
`freeze` requires `--map-artifacts`/`--blind-audit` and an independent
`--map-artifacts-replica`/`--blind-audit-replica` pair. Workflow receives the content of the
corresponding `*-execution.json` through `args` as a JSON object. Saved workflows also accept a
complete JSON object string, but not a file path. Before the first `pipeline` or `agent` call, they
validate exact top-level and item schemas, counts, IDs, prompts, runtime-binding paths, and
SHA-256 format. The Python control plane verifies exact live source digests, execution-config
digest, and the binding between embedded artifact text and its hash; this layer remains the
trusted local-launch boundary. Blind agent source must contain exactly one top-level `tools: []`
field in YAML frontmatter; a nested decoy string or a line in the definition body does not satisfy
the policy. `archive-workflow` accepts stored native output, fresh run ID, actual script path, and
mandatory `--fresh-launch-attested`; it validates the exact execution schema, live
execution-config digest, canonical runtime binding, native result schema/types/completeness,
citation ranges/excerpts against embedded artifacts, exact Analyze/Verify linkage, and progress
provenance, then embeds script source and its SHA-256. The experiment is not considered launched
under this contract until these conditions hold.

Audit JSON, aggregate cohort digest, and Workflow archive are local reproducibility checks, not
cryptographic attestation by a trusted runner. Operator attestation records the asserted fresh
launch but is not independent external attestation. A local user able to modify artifacts, audits,
private manifest, and native output together remains inside the trust boundary. Two independent
builds detect nondeterminism and accidental drift but do not prevent deliberate coordinated
falsification of all local inputs.

**This document does not store the component list.** A query derives it from the graph on every
run. Annotation changes the graph, so a recorded list would become a second source of truth (P5).
The counts below reflect the state when Stage 4 closed. They are comparison anchors, not a source.

| Maps per component | Components | Maps | Accessors | Flat maps |
|---|---:|---:|---:|---:|
| 13-20 | 3 | 55 | 29 | 21 |
| 8-12 | 5 | 47 | 6 | 12 |
| 4-7 | 23 | 113 | 41 | 36 |
| 2-3 | 66 | 150 | 75 | 60 |
| 1 | 74 | 74 | 79 | 33 |
| **total** | **171** | **439** | **230** | **162** |

## 2. Agents read artifacts, not the graph

A sweep agent has no Memgraph access. Preparation determines what it sees: one artifact is built
for each component, and artifact content is contractual rather than agent-selected.

This constraint makes blinding structural. An agent that queries the graph cannot be blinded
because annotation and shape coexist there, so `run_query` would return the answer with the
question.

A component artifact contains:

- maps: address, geometry, element type, image values, and range;
- axes: address, points, monotonicity, length, and element type;
- accessors: address, C pseudocode from `DecompileFuncs`, listing from `DumpListing`, upward call
  tree, and RAM/peripheral accesses through `:USES`;
- code between a map and the output write: interpolation wrapper, kernel, and finisher. A kernel
  not marked as a function, entered by wrapper `jmp` rather than `jsr`, is included as a listing.
  Function marking is required by the decompiler but not by the disassembler, so the kernel code
  remains readable;
- site operands from resolver censuses: values passed in `r4`/`r5`/`r6` and their recovery source,
  `pool`, `slice`, `const`, or `sp`;
- the binding between lookup result and destination RAM. A local address base is resolved at the
  write position; a decompiler variable name reused elsewhere does not inherit the last value from
  another function branch;
- called-function contracts from the code layer (`:Func.contract`) plus complete listings from
  `DumpFuncListing`. The arithmetic library at `0x21000..0x23000` receives arguments in registers
  rather than through the ABI. Ghidra does not recover these conventions, and calls through a
  literal-pool register print as `(*pcVar)()` with no address in pseudocode. Map values enter such
  functions this way, so a trace would stop without the contract. `:CALLS` edges, rather than text
  parsing, identify called targets because analysis resolves them before printing;
- reference catalogs: name candidates from `:A2LEntry` and `:VendorEntry` by geometry and axis
  semantics, plus `:VendorFact` anchors such as documented defaults, units, and mechanics.

The artifact **does not contain** its own component's map-annotation layer: `semantics`, `role`,
`units`, `scale_expr`, and `confidence`. Those fields are the answer the agent must derive. Axes
are blinded in the same way: artifacts contain measurements, not `kind`, `units`, or `scale_expr`.

The code layer is blinded by field rather than file. `:Func.contract` is included, while
`:Func.semantics` and `:Func.note` are excluded. A contract describes an operation and register
convention independently of maps. `semantics` accumulates project knowledge that references
specific maps and constants and would therefore reveal the answer for the map under analysis.

Blinding uses an **allowlist**, the `RETURN` projections in `build_artifacts.py`, rather than a
denylist. Annotation and measurement share a node, and any property added later must be hidden by
default; a denylist could silently expose it. A second layer, `verify_blind`, validates every run
by comparing artifact text against the annotation it must exclude. This catches both projection
errors and leaks through another field, such as a function name from `symbols.csv` or pseudocode.
Annotation is a leak only when the artifact has no independent source for it. A2L itself declares
the `x-64` scale for its 16x16 triples, and the annotation derives from that catalog, marked
`[cand]` in the graph. Verbatim agreement with this catalog is not a leak because the agent reads
the catalog rather than the answer.

On the blinded side, geometry is the only catalog-match key. Of the three keys, `dims`, scale
family, and axis semantics, the final two are themselves annotation. The match is weak and the
artifact says so: 16 catalog entries have a 16x16 shape.

A documented default is compared only with flat maps where `vmin == vmax`. A 256-cell surface
contains almost every possible byte, so a matching value there carries no meaning. This is the
same inference from data shape that caused the pattern scan to fail twice (P6).

## 3. Pilot: accessor `0x82C8A` component

The first run covers one component selected for its built-in answer key: of its 14 maps,
**6 already have `code` confidence** from earlier traces.

| Map | Values | Element | Confidence | Semantics |
|---|---|---|---|---|
| `0000b61a` | 40..128 | uint8 | code | Rotation monitor threshold [flag=clr] |
| `0000b71a` | 34..128 | uint8 | code | Rotation monitor threshold [flag=set] |
| `0000b81a` | 33..63 | uint8 | code | Rotation monitor threshold [always] |
| `0001261a` | 16..255 | uint8 | code | Load-classifier boundary (upper) |
| `0001263a` | 15..42 | uint8 | code | Load-classifier boundary (lower) |
| `00012cbe` | 15..42 | uint8 | code | Diagnostic-inhibit threshold (duplicate of `0x1263a`) |
| `00012026` | 0..0 | uint8 | candidate | - |
| `0001265a` | 255..255 | uint8 | candidate | - |
| `0001266a` | 254..254 | uint8 | candidate | - |
| `0001267a` | 253..253 | uint8 | candidate | - |
| `0001268a` | 252..252 | uint8 | candidate | - |
| `00012de2` | 43..255 | uint8 | candidate | - |
| `0001497a` | 33..33 | uint16 | candidate | - |
| `00014982` | 60..60 | uint16 | candidate | - |

This component exercises the full work range at once: surfaces, comparators, flat maps, both
element sizes, and the `flag=set`/`clr` selector, so it also reaches Stage 6. It tests annotation
against catalogs: the project has three 16x16 maps, A2L names three, UpRev names three, and ProECU
counts nine ignition maps; see `refs/vendor/README.md`. The pilot resolves the discrepancy by
trace rather than count. The `0xB61A/0xB71A/0xB81A` triple contains rotation-irregularity-monitor
thresholds, not ignition maps, as documented in `defs/JK08A.notes.md`. The "Ignition Adj Map" name
and `x-64` scale came from an A2L shape match (P6) and the trace refutes them. The same analysis
corrected the `0x1261A`/`0x1263A` pair boundaries, whose upper and lower labels had been reversed.
Both discrepancies are recorded under section 6 rather than settled by voting.

An open item within the component is the `0x1265A`, `0x1266A`, `0x1267A`, `0x1268A` series with
values 255, 254, 253, and 252. Four flat tables whose constants decrease by one are not four
independent findings.

**Pilot blinding.** Build the pilot component artifact under section 2 without its map annotation
layer. Keep the six known answers outside the run and compare them with claims afterward. An
artifact containing semantics turns calibration into rehearsal and invalidates the only run that
can test the harness.

## 4. Run structure

Headless preparation before Workflow has three steps:

```bash
D=~/tools/ghidra-projects/export-JK03A
H() {
  tools/ghidra/headless-analyze.sh "$HOME/tools/ghidra-projects" vq-hr \
    -process as7058.bin -noanalysis -scriptPath tools/ghidra "$@"
}
H -postScript DecompileFuncs.java "$D" <wave_accessors>
H -postScript DumpListing.java    "$D" <wave_sites> <unmarked_wave_kernels>
uv run --no-project --with neo4j python tools/sweep/build_artifacts.py <out> --accessor <addr>
```

The section 1 query returns wave accessors. Query their sites and unmarked kernels rather than
storing a list, for the same reason components are not stored:

```cypher
MATCH (f:Func {rom:$rom})-[x:ACCESSES]->(m:Map {rom:$rom})
WHERE f.addr IN $accessors
OPTIONAL MATCH (m)-[:VIA]->(:Interp {rom:$rom})-[:KERNEL]->(k:Interp {rom:$rom})
OPTIONAL MATCH (kf:Func {rom:$rom, addr:k.addr})
RETURN collect(DISTINCT f.addr) AS funcs, collect(DISTINCT x.callsite) AS sites,
       collect(DISTINCT CASE WHEN kf IS NULL THEN k.addr ELSE NULL END) AS bare_kernels
```

`build_artifacts.py` reads pseudocode and listings from `<D>`. A missing file is reported in the
artifact rather than silently bypassed because a trace cannot proceed without pseudocode. Capture
a listing at the site address rather than the function entry: operands resolve at the site, which
may lie outside the `DumpListing` window around the entry. A kernel address is its entry, so the
window covers the full kernel. A manually declared map outside the resolver census has no
`callsite` by construction. It can appear in a focused artifact as neighboring context, but no
site listing exists and this is not a preparation omission.

The GUI and GhydraMCP do not participate in the run. The plugin requires a GUI and would become a
bottleneck for ten parallel agents.

The run is one Dynamic Workflow launched through the `Workflow` tool. Its `pipeline()` moves items
through stages without a barrier. Ordinary `Agent` calls, including parallel calls, neither
replace this run nor provide synthesis results. `args.items` contains the exact frozen wave
worklist, and output is bound to its `runId` and `scriptPath`.

1. **Analyze**: the Dynamic Workflow `Analyze` agent reads the artifact, traces the consumer, and
   returns Stage 4-6 claims.
2. **Adversarial Verify**: for every `code` claim, a separate Dynamic Workflow `Verify` agent must
   **refute** it. Does the trace lead to the asserted semantics? Does RAM attribution agree? Any
   uncertainty counts as refutation. A claim that fails verification is downgraded to `candidate`
   rather than discarded.

No stage barrier is required because components are independent: component A claims can be
verified while component B is still being analyzed.

JK03A backfill used 58 blind analyses and 78 separate property-specific verifications. Recovery
replaces only a complete frozen node with all its properties and must read the assigned artifact
through EOF; the control plane prohibits partial replacement of one identity.

3. **Synthesis**: outside agents, as defined in section 5.

## 5. Writes occur outside agents

Dynamic Workflow agents return claims. After verification, synthesis writes rows to
`defs/<source>.findings.csv` and `defs/<source>.axes.csv`. Synthesis accepts only a `Workflow`
tool result with a recorded `runId`, `scriptPath`, complete frozen worklist, and count of `code`
verifications. Free-form ordinary `Agent` responses are not inputs. Writes are separate because
parallel agents would contend for one CSV and direct graph writes would not survive the next run:
the loader recreates layer nodes, so changes belong in the source.

The control plane accepts exactly one decision per frozen identity: `accept`, evidence-backed
`revise`, or `downgrade` with a specific blocker. Verified evidence transfers unchanged. Only
explicitly recorded syntactic normalization is permitted: an edge token containing a ROM address
becomes `site:<same-address>`, and an unresolvable RAM dependency without a ranked claim is
removed. Addresses cannot be changed or added. The result passes the factual-evidence parser and
offline preflight again.

The post-synthesis chain is standard: `ingest.py` (`load_graph.py -> load_xrefs.py ->
load_maps.py -> load_code.py -> provenance_report.py audit`) -> `build_tracker.py` ->
`mapkit/emit_def.py`.

## 6. Claim schema

A map claim uses the `findings.csv` columns below. The census already supplies shape and accessor,
so the agent does not rediscover them.

| Field | Meaning |
|---|---|
| `addr` | map |
| `confidence` | `code` when a trace proves semantics; `candidate` for a match or similarity |
| `evidence` | claim-specific tokens supporting map semantics |
| `role` | `table` \| `threshold` \| `dead` |
| `semantics` | what the map represents |
| `units`, `scale_expr`, `to_byte`, `scale_conf` | scale and confidence |
| `scale_evidence` | claim-specific tokens supporting scale |
| `note` | human trace context; never converted into evidence automatically |

An axis claim uses `axes.csv` columns `addr`, `kind`, `units`, `scale_expr`, `to_byte`,
`scale_conf`, `scale_evidence`, and `note`. A Stage 6 flag claim includes address, bit, role
(`selector`, `gate`, or `threshold`), semantics, and confidence.

Structured Workflow output additionally records output disposition as `writes`, `consumer`,
`inline_comparison`, `return`, `dead_control_flow`, or `unresolved`, plus the exact target.
There is no dedicated CSV column. Synthesis uses it to validate role and attribution, then stores
machine anchors in `evidence` and the complete trace in `note`.

Confidence rules:

- every Map/Axis property at `code` or `silicon` must have its own factual `evidence` or
  `scale_evidence`; process-only `wave`/`arg` tokens fail local source gates;
- a claim without a trace is `candidate`, not `code`, regardless of how convincing a match seems;
- narrow operational semantics receive `code` when the complete trace proves them. An unknown
  physical quantity name does not downgrade a proven formula, multiplier role, or threshold
  polarity;
- an A2L or vendor catalog name supplies `candidate` identity, not semantics (P6);
- **all `0xFF` cannot be classified by shape**: erased flash and a saturated limit have the same
  pattern, and only a trace distinguishes them;
- `role=dead` requires `output_disposition=dead_control_flow`: calibration disables the branch,
  proven by a branch trace. A RAM write without indexed readers remains `writes`, not `dead`;
- identity `x` in raw units is not a scale claim and receives no `scale_conf`. To preserve a raw
  representation use `units=raw`, `scale_expr=x`, `to_byte=x`. If units are unknown, leave all
  scale fields empty. A clamped or conditional conversion remains in `note` when the loader
  vocabulary cannot express it exactly as an invertible `scale_expr`/`to_byte` arithmetic pair;
- record source disagreement as disagreement rather than resolving it by vote.

## 7. Wave order

Large components run first because they provide more names per trace and expose harness weaknesses
before the long tail.

| Wave | Scope | Components | Maps |
|---|---|---:|---:|
| 0 | pilot, component `0x82C8A` | 1 | 14 |
| 1 | components with >= 8 maps, including the 19-map/22-accessor stress case | 7 | 91 |
| 2 | components with 4-7 maps | 22 | 105 |
| 3 | components with 2-3 maps | 63 | 144 |
| 4 | singletons | 79 | 79 |

Between waves: synthesize, re-emit the definition, inspect specification section 11 metrics, and
decide whether to continue. A wave does not automatically launch its successor.

## 8. Gates

**Local evidence gate.** `evidence_backfill.py status --require-zero` requires zero debt in
frozen classes, while `ingest.py <rom> --dry-run` validates factual evidence and dependency
resolution before graph mutation. JK03A debt `52 + 20 + 6` is zero. The post-ingest exact audit
separately requires `missing=extra=duplicate_expected=duplicate_actual=unresolved=0`. Global
`--strict` does not replace these gates; it additionally checks effective confidence and grounding
for the complete graph as a separate diagnostic.

**Pilot.** Determine whether the harness reproduces the six known answers. A miss is investigated
rather than automatically counted against the harness because the answer key is annotation and
some annotation derives from a catalog (P6), not code. A miss on a trace-derived fact implicates
the harness. A miss on a catalog-name-derived fact implicates the key and follows section 6:
record the disagreement rather than vote. Wave 1 cannot launch before this investigation.

The pilot passed: the harness reproduced confidence for 5 of 6 claims, role for 6 of 6, and avoided
the `x-64` scale trap. It did not reproduce the semantics of the
`0xB61A/0xB71A/0xB81A` triple, and investigation attributed the miss to the key rather than the
harness. "Ignition Adj Map" came from an A2L shape match (P6), while the consumer trace identifies
rotation-irregularity-monitor thresholds; see `defs/JK08A.notes.md`. Blinding held during the run:
all 318 agent accesses stayed within the artifact.

**Waves.** Apply specification section 11 gates as regression gates: operand resolution cannot
decrease, no map below `code` can enter the active definition, and the fraction of `code` claims
surviving adversarial verification must be measured and recorded.

A run that reduces a metric fails the gate; it does not establish a new baseline.

## 9. What the sweep does not do

- **It does not split by the flat-map layer.** The 152 flat maps cross components. The same
  consumer trace answers both "why is it constant?" and "what does the surface represent?".
  Output differs, not the work: flat maps remain within their components and more often end with a
  `dead` or threshold role.
- **It does not split by access family.** Explicit-axis and implicit-axis families interpret
  operands differently, but one component can contain both; 25 accessors use both families.
- **It does not hardcode a component list**; see section 1.
- **Agents do not write source files**; see section 5.
- **It does not start a GUI**; see section 4.
