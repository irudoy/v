// Reusable read-only firmware and map-analysis queries.
//
// Run each query independently. Parameter $rom is a label from
// rom-images/roms.csv. The graph is a reproducible projection; query output is
// not a durable claim. Claim-specific exact audits belong to
// provenance_report.py.
//
// mgconsole:  :param rom "JK08A";
// driver:     session.run(query, rom="JK08A")
// mcp-memgraph has no parameter binding; substitute the reviewed ROM label.


// Map inventory by current confidence and role.
MATCH (m:Map {rom:$rom})
RETURN m.confidence AS confidence, m.role AS role, count(*) AS maps
ORDER BY confidence, role;


// Open semantic work.
MATCH (m:Map {rom:$rom})
WHERE m.confidence = 'candidate' AND m.semantics = ''
RETURN m.addr AS table, m.family AS family, m.width AS width,
       m.height AS height, m.storagetype AS storagetype,
       m.vmin AS vmin, m.vmax AS vmax
ORDER BY m.width DESC, table;


// Accessor catalog for one interpolation kernel. Supply $kernel as a
// lowercase eight-digit address.
MATCH (a:Func {rom:$rom})-[x:ACCESSES]->(m:Map {rom:$rom})
MATCH (m)-[:VIA]->(w:Interp)-[:KERNEL]->
      (:Interp {rom:$rom, role:'kernel', addr:$kernel})
RETURN a.addr AS accessor, x.callsite AS callsite, m.addr AS table,
       w.addr AS wrapper, m.width AS width, m.height AS height,
       x.r4 AS r4, x.r5 AS r5, x.r6 AS r6,
       x.kind AS base_kind, x.verdict AS verdict
ORDER BY accessor, callsite, table;


// Data-flow findings that require review rather than silent collapse.
MATCH (a:Func {rom:$rom})-[x:ACCESSES]->(m:Map {rom:$rom})
WHERE x.verdict IN ['selector', 'conflict', 'bt_only'] OR x.kind IN ['sp', 'dyn', 'gbrrel']
RETURN a.addr AS accessor, x.callsite AS callsite, m.addr AS table,
       x.verdict AS verdict, x.kind AS base_kind,
       x.r4 AS r4, x.r5 AS r5, x.r6 AS r6
ORDER BY verdict, accessor, callsite, table;


// Flat maps. Fill values and saturated thresholds remain structurally
// indistinguishable until a code trace assigns a role.
MATCH (m:Map {rom:$rom})
WHERE m.vmin = m.vmax
RETURN m.addr AS table, m.family AS family, m.width AS width,
       m.height AS height, m.storagetype AS storagetype,
       m.vmin AS value, m.confidence AS confidence,
       m.role AS role, m.semantics AS semantics
ORDER BY value DESC, table;


// Fallback axes that cannot pass the definition gate.
MATCH (m:Map {rom:$rom})-[:AXIS_X|AXIS_Y]->(a:Axis {rom:$rom})
WHERE a.confidence = 'pattern'
RETURN a.addr AS axis, a.len AS len, a.storagetype AS storagetype,
       a.monotonic AS monotonic, collect(DISTINCT m.addr) AS tables
ORDER BY axis;


// Shared axis contents. Nodes carry measured axis values, so list equality is
// an image-derived comparison rather than a semantic identity claim.
MATCH (m:Map {rom:$rom})-[:AXIS_X|AXIS_Y]->(a:Axis {rom:$rom})
WITH a.values AS values, collect(DISTINCT a.addr) AS axes,
     collect(DISTINCT a.storagetype) AS storagetypes,
     collect(DISTINCT m.addr) AS tables
WHERE size(tables) > 1
RETURN axes, storagetypes, tables, values
ORDER BY size(tables) DESC, axes;


// Maps with identical measured contents and geometry.
MATCH (m:Map {rom:$rom})
WITH m.values_hash AS values_hash, m.width AS width,
     m.height AS height, m.storagetype AS storagetype,
     collect(m.addr) AS tables
WHERE size(tables) > 1
RETURN values_hash, width, height, storagetype, tables
ORDER BY size(tables) DESC, values_hash;


// Callers up to three levels above a reviewed accessor. Supply $accessor.
MATCH path=(caller:Func {rom:$rom})-[:CALLS*1..3]->
           (:Func {rom:$rom, addr:$accessor})
RETURN [node IN nodes(path) | node.addr] AS chain, length(path) AS depth
ORDER BY depth, chain;


// PageRank on the call-only projection. Never run graph algorithms over all
// stored labels because shared Reg nodes dominate firmware call structure.
MATCH path=(:Func {rom:$rom})-[:CALLS]->(:Func {rom:$rom})
WITH project(path) AS graph
CALL pagerank.get(graph) YIELD node, rank
RETURN node.addr AS addr, node.name AS name, rank
ORDER BY rank DESC LIMIT 15;


// Address-free A2L candidates with matching geometry. Geometry narrows a
// review set but does not assign semantics.
MATCH (m:Map {rom:$rom}), (entry:A2LEntry {family:'HR'})
WHERE entry.dims = m.dims
  AND entry.shape = CASE
    WHEN m.height IS NULL THEN '1D-' + toString(m.width)
    ELSE toString(m.width) + 'x' + toString(m.height)
  END
RETURN m.addr AS table, m.vmin AS vmin, m.vmax AS vmax,
       entry.shape AS shape, collect(entry.name) AS candidates
ORDER BY table;


// Concepts covered independently by more than one vendor dictionary.
MATCH (entry:VendorEntry {family:'HR'})
WHERE entry.concept <> ''
WITH entry.concept AS concept,
     collect(DISTINCT entry.vendor) AS vendors,
     collect(DISTINCT entry.name) AS names
WHERE size(vendors) > 1
RETURN concept, vendors, names
ORDER BY concept;


// Factory-only vendor entries eligible for stock-ROM comparison.
MATCH (entry:VendorEntry {family:'HR', origin:'factory'})
RETURN entry.vendor AS vendor, entry.name AS name, entry.group AS group,
       entry.dims AS dims, entry.axis_x AS axis_x,
       entry.axis_y AS axis_y, entry.concept AS concept
ORDER BY vendor, name;


// Documentary constants suitable for exact-image block-signature searches.
MATCH (fact:VendorFact {family:'HR', kind:'const'})
RETURN fact.vendor AS vendor, fact.subject AS subject,
       fact.value AS value, fact.units AS units,
       fact.applies_to AS applies_to, fact.anchor AS anchor,
       fact.statement AS statement
ORDER BY subject;


// Structural projection gaps. Strict source and provenance equality remains a
// separate provenance_report.py audit.
MATCH (m:Map {rom:$rom})
WHERE m.storagetype IS NULL OR m.values_hash IS NULL
   OR (m.semantics <> '' AND (m.scale_expr IS NULL OR m.scale_expr = ''))
RETURN m.addr AS table, m.storagetype AS storagetype,
       m.values_hash AS values_hash, m.semantics AS semantics,
       m.scale_expr AS scale_expr
ORDER BY table;


// Maps with no structural access path.
MATCH (m:Map {rom:$rom})
WHERE NOT (:Func {rom:$rom})-[:ACCESSES]->(m)
  AND NOT (m)-[:VIA]->(:Interp {rom:$rom})
RETURN m.addr AS table, m.family AS family, m.role AS role,
       m.confidence AS confidence, m.semantics AS semantics
ORDER BY table;
