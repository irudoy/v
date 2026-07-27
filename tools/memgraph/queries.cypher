// Graph queries: catalog, batch-pass unit, centrality, and gates.
//
// This file is a catalog rather than a script; run queries individually. It makes the
// section 11 specification metrics (tools/map-flag-pipeline.md) reproducible instead of
// rebuilding them in a scratchpad for every run. They are regression gates: a run that
// lowers a metric fails the gate rather than establishing a new baseline. A one-off,
// irreproducible metric cannot serve as a gate.
//
// A metric anchor is its JK03A value when Stage 4 closed. It is a cross-check rather than
// a source: the graph is the source. A query differing from its anchor means either the
// graph changed, requiring an anchor update in section 11, or the query changed and needs
// correction.
//
// Parameter $rom is the image label in the graph (rom-images/roms.csv registry). The graph
// contains two ROMs (JK03A is annotated; 1ND0A has only :Func and :Reg). A query without a
// ROM filter counts both.
//
// mgconsole:  :param rom "JK03A";
// driver:     session.run(q, rom="JK03A")
// mcp-memgraph run_query accepts no parameters; substitute the label into query text.
//
// A PROJECTION IS MANDATORY for MAGE algorithms (section 8.2). An algorithm without an
// argument uses all storage, where :USES (78k relationships) dominates :CALLS (6k) and
// :Reg connects any two functions touching a shared address. Raw pagerank.get() ranks RAM
// registers above code, while community_detection.get() collapses the graph into one
// megacluster. MCP analytical tools (get_page_rank, get_betweenness_centrality) operate on
// all storage; use run_query with project() for these queries.


// ════════════════════════════════════════════════════════════════════════════════════
// Section 7. Catalog
// ════════════════════════════════════════════════════════════════════════════════════

// Stage 2: accessor catalog for one core. The catalog is a graph query, not CSV traversal.
// $kernel: 00026944 | 00026984 | 00026b84 | ... (13 engines; see :Interp {role:'kernel'})
MATCH (a:Func {rom:$rom})-[x:ACCESSES]->(m:Map {rom:$rom})-[:VIA]->(w:Interp {role:'wrapper'})
MATCH (w)-[:KERNEL]->(:Interp {role:'kernel', addr:$kernel})
RETURN a.addr AS accessor, w.width AS width, w.height AS height,
       m.addr AS table, x.callsite AS site
ORDER BY w.width DESC, table;

// Open analysis work: candidate maps with empty semantics. This is the sweep worklist.
// Anchor: 377 of 439.
MATCH (m:Map {rom:$rom})
WHERE m.confidence = 'candidate' AND m.semantics = ''
RETURN m.addr AS table, m.family AS family, m.width AS width, m.height AS height,
       m.storagetype AS storagetype, m.vmin AS vmin, m.vmax AS vmax
ORDER BY m.width DESC, table;

// Flat maps: one value across the entire table. They require different analysis from a
// surface and more often end with a dead or threshold role. Do not infer all-0xFF meaning
// from shape because unprogrammed flash and a saturated limit look identical; a trace
// distinguishes them. Anchor: 162 flat maps, 18 entirely 0xFF/0xFFFF.
MATCH (m:Map {rom:$rom})
WHERE m.vmin = m.vmax
RETURN m.addr AS table, m.width AS width, m.height AS height, m.storagetype AS storagetype,
       m.vmin AS value, m.confidence AS confidence, m.semantics AS semantics
ORDER BY value DESC, table;

// Sites with an unresolved base (kind=sp): the decompiler did not reduce the operand and
// linear fallback recovered one set member rather than a fact. Branching defines the base.
// The complete set feeds Stage 6, where branching becomes :Flag{role:'selector'}.
// Anchor: 15 projected base accesses; 16 census rows due to one full duplicate.
MATCH (a:Func {rom:$rom})-[x:ACCESSES]->(m:Map {rom:$rom})
WHERE x.kind = 'sp'
RETURN a.addr AS accessor, x.callsite AS site, m.addr AS table, x.r4 AS r4,
       x.kind5 AS kind5, x.kind6 AS kind6
ORDER BY accessor, site;

// Fallback-only axes (pattern confidence): only backtrack names them and it fails on axes
// as on bases. The definition gate rejects them. Anchor: 14 of 229, including 0x8000,
// which is erased flash rather than an axis.
MATCH (m:Map {rom:$rom})-[e:AXIS_X|AXIS_Y]->(a:Axis {rom:$rom})
WHERE a.confidence = 'pattern'
RETURN a.addr AS axis, a.len AS len, a.storagetype AS storagetype,
       a.monotonic AS monotonic, collect(DISTINCT m.addr) AS tables
ORDER BY axis;

// Shared axes: one axis used by several maps. Contents rather than address form the key.
// Nodes contain every point, so identical axes converge by list comparison without reading
// the image.
MATCH (m:Map {rom:$rom})-[:AXIS_X|AXIS_Y]->(a:Axis {rom:$rom})
WITH a.values AS values, collect(DISTINCT a.addr) AS axes,
     collect(DISTINCT a.storagetype) AS storagetypes,
     collect(DISTINCT m.addr) AS tables
WHERE size(tables) > 1
RETURN axes, size(axes) AS n_axes, storagetypes,
       size(tables) AS n_tables, tables, values
ORDER BY n_tables DESC, axes;

// Identical contents across maps converge by hash. Map values are absent from the graph
// because placing 256 cells on a node would duplicate image contents.
MATCH (m:Map {rom:$rom})
WITH m.values_hash AS h, m.width AS width, m.height AS height,
     m.storagetype AS storagetype, collect(m.addr) AS tables
WHERE size(tables) > 1
RETURN h AS values_hash, width, height, storagetype, size(tables) AS n, tables
ORDER BY n DESC, values_hash, width, height, storagetype;


// ════════════════════════════════════════════════════════════════════════════════════
// Section 8.4. The batch-pass unit is a component, not a map
// ════════════════════════════════════════════════════════════════════════════════════

// Connected components of the bipartite "accessor -> map" graph
// (contract: section 1 of tools/map-sweep.md). Components are independent by construction:
// no two share a map or accessor, so workers do not compete for a node or one fact.
//
// No component list is stored because annotation changes the graph and a recorded list
// would become a second source of truth (P5). Anchor: 171 components, 439 maps, 230 accessors.
MATCH p=(:Func {rom:$rom})-[:ACCESSES]->(:Map {rom:$rom})
WITH project(p) AS g
CALL weakly_connected_components.get(g) YIELD node, component_id
WITH component_id, collect(node) AS nodes
RETURN component_id,
       [n IN nodes WHERE 'Map'  IN labels(n) | n.addr] AS maps,
       [n IN nodes WHERE 'Func' IN labels(n) | n.addr] AS accessors;

// Component size distribution defines wave order (contract section 7). Process large
// components first: they provide the best ratio of names to one trace, and harness
// weaknesses appear there rather than at the tail. Anchor: 13-21 maps: 3 components;
// 8-12: 5; 4-7: 23; 2-3: 66; 1: 74.
MATCH p=(:Func {rom:$rom})-[:ACCESSES]->(:Map {rom:$rom})
WITH project(p) AS g
CALL weakly_connected_components.get(g) YIELD node, component_id
WITH component_id, collect(node) AS nodes
WITH size([n IN nodes WHERE 'Map' IN labels(n)]) AS n_maps,
     size([n IN nodes WHERE 'Func' IN labels(n)]) AS n_acc
WITH CASE
       WHEN n_maps > 21 THEN '>21'
       WHEN n_maps >= 13 THEN '13-21'
       WHEN n_maps >= 8 THEN '8-12'
       WHEN n_maps >= 4 THEN '4-7'
       WHEN n_maps >= 2 THEN '2-3'
       ELSE '1'
     END AS bucket,
     CASE
       WHEN n_maps > 21 THEN 0
       WHEN n_maps >= 13 THEN 1
       WHEN n_maps >= 8 THEN 2
       WHEN n_maps >= 4 THEN 3
       WHEN n_maps >= 2 THEN 4
       ELSE 5
     END AS bucket_order,
     n_maps, n_acc
RETURN bucket_order, bucket, count(*) AS components,
       sum(n_maps) AS maps, sum(n_acc) AS accessors
ORDER BY bucket_order;


// ════════════════════════════════════════════════════════════════════════════════════
// Section 8.2. Centrality on the call-graph projection
// ════════════════════════════════════════════════════════════════════════════════════

// Stage 1 independent interpolation-core cross-check: PageRank ranks the access library
// near the top. It is available before Stage 3 because indirect calls with a constant target
// already create :CALLS relationships. The signal is independent of the FindInterpCore.java
// data scan and therefore cross-checks it rather than repeating the same evidence.
// JK03A anchor: 0x26740, 0x26c78, 0x26370, 0x26944, 0x26388 near the top.
MATCH p=(:Func {rom:$rom})-[:CALLS]->(:Func {rom:$rom})
WITH project(p) AS g
CALL pagerank.get(g) YIELD node, rank
RETURN node.addr AS addr, node.name AS name, rank
ORDER BY rank DESC LIMIT 15;

// Betweenness on the same projection is a second hub-layer signal.
MATCH p=(:Func {rom:$rom})-[:CALLS]->(:Func {rom:$rom})
WITH project(p) AS g
CALL betweenness_centrality.get(g) YIELD node, betweenness_centrality
RETURN node.addr AS addr, node.name AS name, betweenness_centrality AS bc
ORDER BY bc DESC LIMIT 15;

// Accessor caller tree (Stage 2): higher levels are closer to the subsystem.
MATCH path = (c:Func {rom:$rom})-[:CALLS*1..3]->(a:Func {rom:$rom, addr:$accessor})
RETURN [n IN nodes(path) | n.addr] AS chain, length(path) AS depth
ORDER BY depth, chain;


// ════════════════════════════════════════════════════════════════════════════════════
// Section 7, Stage 5. Reference catalogs
// ════════════════════════════════════════════════════════════════════════════════════

// Catalog candidates by geometry. The key is intentionally weak: of three match keys
// (dims, scale family, axis semantics), only dims exists on the map side before Stage 4.
// Matching on dims alone would connect 37 two-axis entries to every dims=2 map, producing
// noise rather than a clue (P6). Geometry narrows the set: 16 catalog entries have a 16x16
// shape. A trace of axis input RAM sensors is the actual discriminator.
MATCH (m:Map {rom:$rom}), (e:A2LEntry {family:'HR'})
WHERE e.dims = m.dims
  AND e.shape = CASE WHEN m.height IS NULL THEN '1D-' + toString(m.width)
                     ELSE toString(m.width) + 'x' + toString(m.height) END
RETURN m.addr AS table, m.vmin AS vmin, m.vmax AS vmax, e.shape AS shape,
       collect(e.name) AS candidates
ORDER BY table;

// Vocabulary convergence: concepts covered by both vendors. The concept property links
// vocabularies rather than name because names remain verbatim and the two vocabularies use
// different terms for one entity ("BFS Multiplier (K-Factor)" versus
// "K - Fuel Multiplier"). Anchor: 27 of 49.
MATCH (e:VendorEntry {family:'HR'}) WHERE e.concept <> ''
WITH e.concept AS concept, collect(DISTINCT e.vendor) AS vendors,
     collect(DISTINCT e.name) AS names
WHERE size(vendors) > 1
RETURN concept, vendors, names
ORDER BY concept;

// Factory entries in vendor vocabularies. origin=factory is mandatory for stock ROM
// annotation. Of 371 entries, 128 are not factory; 126 describe vendor patches
// (EcuTek RaceROM or UpRev ARC), which are external code absent from stock. Matching a
// stock map to a patch entry would be wrong rather than merely weak evidence. Group labels
// cannot filter them: Rev Limit Per Gear Mode1-4 sits under Limiters beside factory entries.
MATCH (e:VendorEntry {family:'HR', origin:'factory'})
RETURN e.vendor AS vendor, e.name AS name, e.group AS grp, e.dims AS dims,
       e.axis_x AS axis_x, e.axis_y AS axis_y, e.concept AS concept
ORDER BY vendor, name;

// Documented defaults are the only catalog key usable before Stage 3. They require neither
// resolved operands nor axis semantics and can be searched directly in the image. A value
// match alone gives pattern rather than candidate confidence: shorter numbers collide more
// often by chance. A homologous block signature or trace promotes it to candidate. Dump
// value search lies outside Cypher because the image is absent from the graph
// (tools/mapkit/rom.py, scan()). Anchor: 22 kind=const facts; one found in the image through
// a block signature (K-Factor 26806).
MATCH (f:VendorFact {family:'HR', kind:'const'})
RETURN f.vendor AS vendor, f.subject AS subject, f.value AS value, f.units AS units,
       f.applies_to AS applies_to, f.anchor AS anchor, f.statement AS statement
ORDER BY subject;

// Vocabulary applicability boundaries are narrower by default. EcuTek documents VQ37VHR
// (370Z, VVEL), while donor JK03A is VQ25HR without VVEL. VVEL Valve Duration does not
// apply to JK03A at all; VTC Valve Advance does.
// Anchor: vq37vhr=78, nissan=41, hr=18, racerom=1.
MATCH (f:VendorFact {family:'HR'})
RETURN f.applies_to AS applies_to, f.kind AS kind, count(*) AS facts
ORDER BY applies_to, kind;


// ════════════════════════════════════════════════════════════════════════════════════
// Section 11. Structural graph gates
// ════════════════════════════════════════════════════════════════════════════════════

// Metrics computed only from the current graph. provenance_report.py performs exact
// expected-versus-actual checks for :RESTS_ON, effective confidence, grounding, and SCCs.
// Cypher does not read canonical CSV files and therefore cannot prove projection completeness.
//
// This query does not contain every section 11 metric. Vendor anchors are searched in an
// image absent from the graph (tools/mapkit/rom.py, scan()) and are omitted here.
//
// Count with count(CASE WHEN ... THEN 1 END), not WHERE + count(*). WHERE removes rows
// before aggregation, so a zero-valued metric returns zero rows rather than "0" and
// disappears exactly when the gate passes. That would look like "not measured" and make a
// passing metric indistinguishable from a broken query. The form below always returns one
// row per metric.
MATCH (:Func {rom:$rom})-[r:ACCESSES]->()
WITH count(CASE WHEN r.r4 <> '' THEN 1 END) AS resolved, count(*) AS sites
RETURN 'Operand resolution' AS metric,
       toString(resolved) + '/' + toString(sites) AS fact,
       '583/586 (99.5%)' AS anchor, '>= 95%, zero silently lost' AS gate
UNION ALL
MATCH (:Func {rom:$rom})-[r:ACCESSES]->()
WITH count(CASE WHEN r.verdict = 'conflict' THEN 1 END) AS n
RETURN 'Latent catalog defects (bt != df)' AS metric,
       toString(n) AS fact,
       '14, all analyzed' AS anchor,
       'all analyzed' AS gate
UNION ALL
MATCH (:Func {rom:$rom})-[r:ACCESSES]->()
WITH count(CASE WHEN r.verdict = 'bt_only' THEN 1 END) AS n
RETURN 'No regression versus backtrack' AS metric,
       toString(n) AS fact,
       '1, analyzed (0x56cd8)' AS anchor,
       'all analyzed' AS gate
UNION ALL
MATCH (m:Map {rom:$rom})
RETURN 'Catalog completeness (:Map in graph)' AS metric,
       toString(count(*)) AS fact,
       '439 of 441' AS anchor,
       'all :Map nodes in graph; two outside belong to Stage 6' AS gate
UNION ALL
MATCH (m:Map {rom:$rom})
WITH count(CASE WHEN m.role = 'table' AND m.semantics <> '' AND m.scale_expr <> ''
                 AND m.confidence IN ['candidate', 'code', 'silicon'] THEN 1 END) AS n
RETURN 'Definition gate: emitted tables' AS metric,
       toString(n) AS fact,
       '20' AS anchor,
       'grows with analysis' AS gate
UNION ALL
MATCH (m:Map {rom:$rom})
WITH count(CASE WHEN m.role = 'table' AND m.semantics <> '' AND m.scale_expr <> ''
                 AND m.confidence = 'code' THEN 1 END) AS n
RETURN 'Definition gate: active subset (code)' AS metric,
       toString(n) AS fact,
       '18' AS anchor,
       'only code is emitted as active' AS gate
UNION ALL
MATCH (m:Map {rom:$rom})
WITH count(CASE WHEN m.role = 'table' AND m.semantics <> '' AND m.scale_expr <> ''
                 AND m.confidence = 'candidate' THEN 1 END) AS n
RETURN 'Definition gate: marked (candidate)' AS metric,
       toString(n) AS fact,
       '2' AS anchor,
       '(candidate) category suffix' AS gate
UNION ALL
MATCH (m:Map {rom:$rom})
WITH count(CASE WHEN m.storagetype IS NULL OR m.storagetype = '' THEN 1 END) AS n
RETURN 'Catalog geometry: :Map without storagetype' AS metric,
       toString(n) AS fact,
       '0' AS anchor,
       '0 - emission is impossible without it' AS gate
UNION ALL
MATCH (m:Map {rom:$rom})
WITH count(CASE WHEN m.role = 'table' AND m.semantics <> '' AND m.scale_expr = ''
                THEN 1 END) AS n
RETURN 'Interpretability: semantics without scaling' AS metric,
       toString(n) AS fact,
       '9, excluded from definition' AS anchor,
       '0 without scaling' AS gate
UNION ALL
MATCH (a:Axis {rom:$rom})
WITH count(CASE WHEN a.confidence = 'pattern' THEN 1 END) AS n, count(*) AS t
RETURN 'Fallback-only axes (pattern confidence)' AS metric,
       toString(n) + '/' + toString(t) AS fact,
       '14 of 229' AS anchor,
       '0, handled by Stage 6' AS gate
UNION ALL
MATCH (a:Axis {rom:$rom})
WITH count(CASE WHEN a.monotonic = false THEN 1 END) AS n, count(*) AS t
RETURN 'Axis conflicts with core code (monotonic=false)' AS metric,
       toString(n) + '/' + toString(t) AS fact,
       '1 of 229 (0x119b2)' AS anchor,
       '0' AS gate
UNION ALL
MATCH (m:Map {rom:$rom})
WITH count(CASE WHEN m.values_hash IS NULL OR m.values_hash = '' THEN 1 END) AS n,
     count(*) AS t
RETURN 'Layer measurement: :Map without values' AS metric,
       toString(n) + '/' + toString(t) AS fact,
       '0 of 439' AS anchor,
       '0, a read miss stops loading' AS gate
UNION ALL
MATCH (a:Axis {rom:$rom})
WITH count(CASE WHEN a.values IS NULL OR size(a.values) = 0 THEN 1 END) AS n,
     count(*) AS t
RETURN 'Layer measurement: :Axis without values' AS metric,
       toString(n) + '/' + toString(t) AS fact,
       '0 of 229' AS anchor,
       '0, a read miss stops loading' AS gate
UNION ALL
MATCH (m:Map {rom:$rom}) WHERE m.confidence IN ['code', 'silicon']
WITH count(CASE WHEN coalesce(m.evidence, '') = '' THEN 1 END) AS debt,
     count(*) AS total
RETURN 'Provenance of Map.confidence code/silicon' AS metric,
       toString(debt) + '/' + toString(total) AS fact,
       '0 after backfill; frozen debt 52/52' AS anchor,
       '0 without evidence' AS gate
UNION ALL
MATCH (m:Map {rom:$rom}) WHERE m.scale_conf IN ['code', 'silicon']
WITH count(CASE WHEN coalesce(m.scale_evidence, '') = '' THEN 1 END) AS debt,
     count(*) AS total
RETURN 'Provenance of Map.scale_conf code/silicon' AS metric,
       toString(debt) + '/' + toString(total) AS fact,
       '0 after backfill; frozen debt 20/20' AS anchor,
       '0 without scale_evidence' AS gate
UNION ALL
MATCH (a:Axis {rom:$rom}) WHERE a.scale_conf IN ['code', 'silicon']
WITH count(CASE WHEN coalesce(a.scale_evidence, '') = '' THEN 1 END) AS debt,
     count(*) AS total
RETURN 'Provenance of Axis.scale_conf code/silicon' AS metric,
       toString(debt) + '/' + toString(total) AS fact,
       '0 after backfill; frozen debt 6/6' AS anchor,
       '0 without scale_evidence' AS gate
UNION ALL
MATCH (m:Map {rom:$rom})
OPTIONAL MATCH (m)-[x:MATCHES]->(:A2LEntry)
OPTIONAL MATCH (m)-[h:HOMOLOG]->(:Map)
WITH m, count(x) + count(h) AS links
WITH count(CASE WHEN links > 0 THEN 1 END) AS linked, count(*) AS total
RETURN 'Identity coverage (:MATCHES/:HOMOLOG)' AS metric,
       toString(linked) + '/' + toString(total) AS fact,
       '0' AS anchor,
       'advisory, grows' AS gate
UNION ALL
MATCH (m:Map {rom:$rom})
WITH count(CASE WHEN m.confidence = 'silicon' THEN 1 END) AS n,
     count(CASE WHEN m.confidence = 'code' THEN 1 END) AS c
RETURN 'Verification: silicon from code' AS metric,
       toString(n) + '/' + toString(c) AS fact,
       'selective' AS anchor,
       'as bench testing progresses' AS gate;


// ── Claim-specific provenance ───────────────────────────────────────────────────────

// Legacy or incomplete relationship. Anchor after ingestion: 0.
MATCH (source)-[e:RESTS_ON]->(target)
WHERE source.rom = $rom AND target.rom = $rom
  AND (e.source_prop IS NULL OR e.source_prop = ''
       OR e.role IS NULL OR e.role = ''
       OR e.target_prop IS NULL OR e.target_prop = ''
       OR e.ref IS NULL OR e.ref = '')
RETURN labels(source) AS source_label, source.addr AS source,
       labels(target) AS target_label, target.addr AS target,
       properties(e) AS edge;

// Projection composition by claim type. JK03A total after ingestion: 2759.
MATCH (source)-[e:RESTS_ON]->(target)
WHERE source.rom = $rom AND target.rom = $rom
RETURN labels(source) AS source_label, e.source_prop AS source_prop,
       e.role AS role, labels(target) AS target_label,
       e.target_prop AS target_prop, count(*) AS edges
ORDER BY source_label, source_prop, role, target_label, target_prop;

// Direct reverse impact of one claim identity. A transitive traversal must match
// target_prop of each following relationship to source_prop of the previous one.
// provenance.py contains the cycle-safe implementation.
MATCH (dependent)-[e:RESTS_ON]->(changed)
WHERE changed.rom = $rom AND changed.addr = $claim_addr
  AND $claim_label IN labels(changed) AND e.target_prop = $claim_prop
RETURN labels(dependent) AS dependent_label, dependent.addr AS dependent,
       e.source_prop AS dependent_prop, e.role AS role, e.ref AS ref
ORDER BY dependent_label, dependent, dependent_prop;

// Run exact projection, weakest path, transitive reverse impact, and SCC analysis with:
//   provenance_report.py audit <rom>
//   provenance_report.py weakest <rom> <label> <addr> <prop>
//   provenance_report.py impact <rom> <label> <addr> <prop>
// The Python model condenses SCCs into a DAG and prevents a cycle from substantiating
// itself. Cypher sees only entity nodes and would mix properties at one address without
// separate claim nodes.


// ── Gate-failure analysis: individual metrics ───────────────────────────────────────

// Sites where the resolver census differs from its baseline. Anchor: 14, all analyzed:
// six base conflicts where the baseline is wrong, three unreachable-branch and residual
// register cases, and five mov.w constants read as 32-bit by the baseline. Four earlier
// conflicts disappear as a class after expanding set-valued operands because they are
// different branches of one selector.
MATCH (a:Func {rom:$rom})-[x:ACCESSES]->(m:Map {rom:$rom})
WHERE x.verdict = 'conflict'
RETURN a.addr AS accessor, x.callsite AS site, m.addr AS table, x.r4 AS r4,
       x.base AS base, x.kind AS kind
ORDER BY site;

// A map read by entries with different shapes has its shape defined in two incompatible
// ways. Entry geometry makes map geometry unambiguous, and the loader enforces this fact.
// Anchor: 0; no map is read through two entry shapes.
MATCH (m:Map {rom:$rom})-[:VIA]->(w:Interp {rom:$rom})
WITH m, collect(DISTINCT w.addr) AS wrappers,
     collect(DISTINCT toString(w.width) + 'x' + coalesce(toString(w.height), '-')) AS shapes
WHERE size(shapes) > 1
RETURN m.addr AS table, wrappers, shapes;

// Table-census disjointness: a table shared by two access families is a finding rather
// than normal variation. Anchor: 0; the families share no table.
MATCH (m:Map {rom:$rom})
WITH m.family AS family, collect(m.addr) AS tables
RETURN family, size(tables) AS n
ORDER BY family;

// Orphan nodes: a map without an entry or accessor. Anchor: 0.
MATCH (m:Map {rom:$rom})
WHERE NOT (m)-[:VIA]->(:Interp) AND NOT (:Func)-[:ACCESSES]->(m)
RETURN m.addr AS table, m.family AS family, m.confidence AS confidence;
