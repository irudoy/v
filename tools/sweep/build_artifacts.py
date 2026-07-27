#!/usr/bin/env python3
"""Build an "accessor -> map" graph-component artifact for a batch pass.

The pass contract is tools/map-sweep.md, specifically section 2 here. The work unit is a
connected component of the bipartite "accessor -> map" graph. Components are independent
by construction (no two share a map or accessor), and all evidence about a map lies within
one component.

The artifact is the pass worker's only input; the worker has no Memgraph access. Blinding is
therefore structural rather than a promise: this script defines what the worker sees. A
worker querying the graph cannot be blinded because annotations and shape live together and
one query would return the answer with the question.

Blinding uses an ALLOWLIST (the RETURN clauses in MAP_FACTS/AXIS_FACTS), not a denylist.
Annotations and measurements share a node, and a property added later must be invisible by
default; a denylist would silently expose it. The worker must independently derive its claim:
semantics/role/units/scale_expr/confidence. Every run verifies blinding (verify_blind) by
comparing artifact text with the exact annotation strings it must not contain.

Map values come from the image rather than the graph. A node stores only
vmin/vmax/values_hash; placing 256 cells in the graph would duplicate image contents
(Stage 4).

No component list is stored; a query derives it on every run (P5). A component key is its
lowest accessor address. MAGE component_id is unstable between runs and cannot serve as a
filename.

Build an artifact for a component (a claim for each map), a map (`--focus-map`), or an axis
(`--focus-axis`). Map focus narrows evidence to accessors of the target map. Axis focus
aggregates all maps using that axis and all their accessors. In both cases, only the target
requires a claim; neighboring maps and axes remain context.

Invocation: uv run --no-project --with neo4j python tools/sweep/build_artifacts.py \
          <out_dir> [--rom JK08A] [--accessor <addr>] [--min-maps N] [--max-maps N] \
          [--focus-map <addr> | --focus-maps-file <path> | \
           --focus-axis <addr> | --focus-axes-file <path>] [--export-dir <dir>]
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from neo4j import GraphDatabase

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mapkit import rom as romkit          # noqa: E402 - adjacent package is not installed

BOLT = "bolt://localhost:7687"
EXPORT = os.path.expanduser("~/tools/ghidra-projects/export-{rom}")

# --- Blinding boundary ---------------------------------------------------------------
# The queries below return component map and axis data. Their RETURN clauses form the
# allowlist: annotation remains in the database instead of being filtered after retrieval.
# Properties absent here (semantics, role, units, scale_expr, to_byte, scale_conf,
# confidence, evidence, and note on :Map; kind, units, scale_expr, to_byte, confidence, and
# note on :Axis) are the worker's claim.
MAP_FACTS = """
MATCH (m:Map {rom:$rom}) WHERE m.addr IN $addrs
OPTIONAL MATCH (m)-[:VIA]->(w:Interp {rom:$rom})
OPTIONAL MATCH (w)-[:KERNEL]->(k:Interp {rom:$rom})
OPTIONAL MATCH (m)-[:AXIS_X]->(ax:Axis {rom:$rom})
OPTIONAL MATCH (m)-[:AXIS_Y]->(ay:Axis {rom:$rom})
RETURN m.addr AS addr, m.family AS family, m.dims AS dims, m.width AS width,
       m.height AS height, m.storagetype AS storagetype, m.vmin AS vmin, m.vmax AS vmax,
       m.values_hash AS values_hash,
       collect(DISTINCT w.addr) AS via, collect(DISTINCT k.addr) AS kernel,
       collect(DISTINCT ax.addr) AS axis_x, collect(DISTINCT ay.addr) AS axis_y
ORDER BY addr
"""

AXIS_FACTS = """
MATCH (a:Axis {rom:$rom}) WHERE a.addr IN $addrs
RETURN a.addr AS addr, a.len AS len, a.storagetype AS storagetype,
       a.values AS values, a.monotonic AS monotonic
ORDER BY addr
"""

# Component annotations are its answers. A separate query retrieves them without placing
# them in the artifact; verify_blind uses them to ensure the artifact does not contain them.
MAP_ANSWERS = """
MATCH (m:Map {rom:$rom}) WHERE m.addr IN $addrs
RETURN m.addr AS addr, m.semantics AS semantics, m.note AS note, m.role AS role,
       m.units AS units, m.scale_expr AS scale_expr, m.to_byte AS to_byte,
       m.confidence AS confidence, m.evidence AS evidence,
       m.scale_evidence AS scale_evidence
"""

AXIS_ANSWERS = """
MATCH (a:Axis {rom:$rom}) WHERE a.addr IN $addrs
RETURN a.addr AS addr, a.kind AS kind, a.units AS units, a.scale_expr AS scale_expr,
       a.to_byte AS to_byte, a.note AS note, a.confidence AS confidence,
       a.scale_evidence AS scale_evidence
"""

# Function annotations are also answers. Code-layer semantics accumulates project knowledge
# with references to specific maps ("multiply map X by constant Y"). Only a map-independent
# contract enters the artifact from this layer. This query verifies the boundary instead of
# trusting CONTRACTS' RETURN clause. It reads the whole ROM rather than only displayed
# functions because a neighboring annotation can leak through another field.
FUNC_ANSWERS = """
MATCH (f:Func {rom:$rom})
WHERE f.semantics <> '' OR f.note <> '' OR f.evidence <> '' OR f.contract_evidence <> ''
RETURN f.addr AS addr, f.semantics AS semantics, f.note AS note,
       f.evidence AS evidence, f.contract_evidence AS contract_evidence
"""

# --- Component enumeration ----------------------------------------------------------
COMPONENTS = """
MATCH p=(:Func {rom:$rom})-[:ACCESSES]->(:Map {rom:$rom})
WITH project(p) AS g
CALL weakly_connected_components.get(g) YIELD node, component_id
WITH component_id, collect(node) AS nodes
RETURN component_id,
       [n IN nodes WHERE 'Map'  IN labels(n) | n.addr] AS maps,
       [n IN nodes WHERE 'Func' IN labels(n) | n.addr] AS accessors
"""

# Axis focus does not pick one arbitrary representative map. A shared axis can connect
# several maps and components. Context includes EVERY map directly connected to the axis
# and EVERY accessor of those maps. OPTIONAL MATCH preserves an axis and a map without an
# accessor so graph incompleteness cannot hide the target.
AXIS_CONTEXTS = """
MATCH (a:Axis {rom:$rom}) WHERE a.addr IN $addrs
OPTIONAL MATCH (m:Map {rom:$rom})-[:AXIS_X|AXIS_Y]->(a)
OPTIONAL MATCH (f:Func {rom:$rom})-[:ACCESSES]->(m)
RETURN a.addr AS axis, m.addr AS map, f.addr AS accessor
ORDER BY axis, map, accessor
"""

# Focus: accessors that read one specified map. A component defines map MEMBERSHIP, but
# evidence about a map lies in its own neighborhood: accessors that read it and consumers of
# their output. A component accessor unrelated to the target map is at least two hops away,
# does not belong in its trace, and only adds artifact volume. Volume cost is nonlinear:
# usage grows as "turns x context", and a large artifact increases both factors because it is
# read in chunks and context grows each turn.
FOCUS_ACC = """
MATCH (f:Func {rom:$rom})-[:ACCESSES]->(m:Map {rom:$rom, addr:$map})
RETURN collect(DISTINCT f.addr) AS accessors
"""

SITES = """
MATCH (f:Func {rom:$rom})-[x:ACCESSES]->(m:Map {rom:$rom})
WHERE f.addr IN $addrs
RETURN f.addr AS accessor, f.name AS name, f.size AS size, m.addr AS tbl,
       x.callsite AS callsite, x.r4 AS r4, x.r5 AS r5, x.r6 AS r6,
       x.kind AS kind, x.kind5 AS kind5, x.kind6 AS kind6, x.verdict AS verdict
ORDER BY accessor, callsite, tbl
"""

CALLERS = """
MATCH (c:Func {rom:$rom})-[:CALLS]->(f:Func {rom:$rom})
WHERE f.addr IN $addrs
RETURN f.addr AS accessor, c.addr AS caller, c.name AS name, c.size AS size
ORDER BY accessor, caller
"""

USES = """
MATCH (f:Func {rom:$rom})-[u:USES]->(r:Reg {rom:$rom})
WHERE f.addr IN $addrs
RETURN f.addr AS accessor, r.addr AS reg, r.region AS region, r.name AS name,
       collect(DISTINCT u.kind) AS kinds
ORDER BY accessor, region, reg
"""

# Interpolation machinery: a map uses VIA to reach a wrapper, and the wrapper uses KERNEL
# to reach a core. The wrapper enters the core through jmp rather than jsr, so no CALLS
# relationship exists and core size is empty because Ghidra does not define it as a function
# (RecoverFuncs.java addresses this; section 7 of map-flag-pipeline.md). Empty size is an
# artifact fact: no trace through that core is available. The query also includes finishers
# called by the core that implement saturation and map element access.
KERNELS = """
MATCH (m:Map {rom:$rom})-[:VIA]->(w:Interp {rom:$rom})
WHERE m.addr IN $maps
OPTIONAL MATCH (w)-[:KERNEL]->(k:Interp {rom:$rom})
WITH collect(DISTINCT {a:w.addr, r:w.role}) + collect(DISTINCT {a:k.addr, r:k.role}) AS xs
UNWIND xs AS x
WITH DISTINCT x WHERE x.a IS NOT NULL
OPTIONAL MATCH (f:Func {rom:$rom, addr:x.a})
OPTIONAL MATCH (f)-[:CALLS]->(c:Func {rom:$rom})
RETURN x.a AS addr, x.r AS role, f.size AS size,
       collect(DISTINCT {addr:c.addr, size:c.size}) AS callees
ORDER BY addr
"""

# Contracts for called functions from the code-understanding layer. RETURN is again an
# allowlist and intentionally excludes `semantics`, which accumulates project knowledge
# referencing specific maps ("multiply 0x145ca by constant 0x1495a = 50000") and therefore
# contains an answer. A contract describes an operation, register convention, and side
# effects independent of maps; it remains evidence rather than a hint.
CONTRACTS = """
MATCH (f:Func {rom:$rom}) WHERE f.addr IN $addrs AND f.contract <> ''
RETURN f.addr AS addr, f.role AS role, f.size AS size, f.contract AS contract,
       f.contract_conf AS contract_conf
ORDER BY addr
"""

# Functions called by displayed code. Pseudocode text cannot identify them because the
# library is called through a register loaded from a literal pool and Ghidra prints
# `(*pcVar26)()` without an address. CALLS knows the target because analysis resolves it
# before rendering.
CALLED = """
MATCH (f:Func {rom:$rom})-[:CALLS]->(g:Func {rom:$rom})
WHERE f.addr IN $addrs AND g.contract <> ''
RETURN DISTINCT g.addr AS addr
"""

# Output consumers are functions that read RAM written by a component accessor. Map meaning
# comes from what happens to its output, and that output is a RAM write. Reader-count
# filtering measures specificity: a register with few readers is private to the component,
# while one read by many is a shared bus whose consumers reveal nothing about the map. A
# threshold of 8 retains moderately shared outputs (2-8 consumers cover most cases where a
# trace reaches meaning) and removes hot sinks/buses with 9+ readers. Their full consumer
# sets are expensive and give the worker a haystack. Cost lies in TEXT, not machine code:
# consumer decompilation is approximately 5-7 times longer than its size. For the widest ROM
# accessor (000b29b8, 65 written registers), an artifact at 8 is already approximately
# 800 KB; at 32 it reaches several megabytes. Raising the threshold increases pass cost,
# not annotation quality.
#
# Sharedness filtering is neither the only nor the main source of volume. A wide accessor
# can hold a hundred private registers with one reader each, and all pass any threshold.
# For map 0001218e, 56 of 305 consumers arrive through 119 registers with exactly one reader.
# Consumer decompilation therefore has a separate budget (--max-consumer-decomp), while the
# FULL consumer table remains visible. Code is included for the most specific subset.
# Selection order is min(readers) across connecting registers, then size: a private register
# is closer to map output than a moderately shared one.
CONSUMERS = """
MATCH (a:Func {rom:$rom})-[:USES {kind:'W'}]->(g:Reg {rom:$rom})
WHERE a.addr IN $addrs
OPTIONAL MATCH (c:Func {rom:$rom})-[:USES {kind:'R'}]->(g) WHERE NOT c.addr IN $addrs
WITH g, count(DISTINCT c) AS readers
WHERE readers >= 1 AND readers <= $maxr
MATCH (c2:Func {rom:$rom})-[:USES {kind:'R'}]->(g) WHERE NOT c2.addr IN $addrs
RETURN c2.addr AS consumer, c2.size AS size, collect(DISTINCT g.addr) AS regs,
       min(readers) AS spec
ORDER BY spec, size, consumer
"""

# Consumers of an attributed output. This differs from CONSUMERS in the source register set:
# CONSUMERS derives it from every accessor write and therefore mixes unrelated values;
# attribution supplies only the target map's value. No sharedness filter is needed because
# the set is already specific. Sharedness of an attributed register is itself a map fact,
# and filtering it would discard evidence.
CONSUMERS_OF = """
UNWIND $regs AS reg
MATCH (c:Func {rom:$rom})-[:USES {kind:'R'}]->(g:Reg {rom:$rom, addr:reg})
WHERE NOT c.addr IN $addrs
RETURN c.addr AS consumer, c.size AS size, collect(DISTINCT g.addr) AS regs, 1 AS spec
ORDER BY size, consumer
"""

# Diagnose an empty consumer section. Three causes have different meanings: the accessor
# writes no RAM at all (trace ends in the accessor), no external function reads written
# values (output is dead or read by the same accessor), or many functions read them
# (register is a shared bus removed by specificity filtering). Silently omitting the
# section would make these cases indistinguishable.
WRITE_REGS = """
MATCH (a:Func {rom:$rom})-[:USES {kind:'W'}]->(g:Reg {rom:$rom})
WHERE a.addr IN $addrs
OPTIONAL MATCH (c:Func {rom:$rom})-[:USES {kind:'R'}]->(g) WHERE NOT c.addr IN $addrs
RETURN g.addr AS reg, g.name AS name, count(DISTINCT c) AS readers
ORDER BY readers DESC, reg
"""

# Registers of decompiled functions validate pool resolution. The decompiler prints a
# literal as `DAT_<address>`, and an access such as
# `*(byte *)(DAT_0008625c + DAT_0008608e)` does not name its address even though the graph
# knows it. Image-based resolution supplies a candidate address; this query supplies the
# validation set. A match confirms the interpretation.
FUNC_REGS = """
MATCH (f:Func {rom:$rom})-[u:USES]->(g:Reg {rom:$rom})
WHERE f.addr IN $addrs
RETURN f.addr AS func, collect(DISTINCT {addr:g.addr, kind:u.kind}) AS regs
"""

# Every known RAM and peripheral address in the ROM provides a second, weaker resolution
# check. Ghidra does not resolve an access whose address is assembled in a register and
# creates no USES relationship, even when an address node exists. This yields three binding
# states rather than two.
ALL_REGS = """
MATCH (g:Reg {rom:$rom}) RETURN collect(g.addr) AS addrs
"""

# Reference catalog. Geometry is the key because it is the only one of three match keys
# (dims, scale family, axis semantics) present on the blinded side. Axis semantics and scale
# family would come from annotations absent from the artifact. The match is weak and the
# artifact says so directly: 16 catalog entries have a 16x16 shape (section 5 calls this a
# candidate hint, not identification).
A2L_BY_SHAPE = """
MATCH (e:A2LEntry {family:'HR'}) WHERE e.dims = $dims AND e.shape = $shape
RETURN e.name AS name, e.kind AS kind, e.unit AS unit, e.scale_expr AS scale_expr,
       e.storagetype AS storagetype, e.axis_x_sem AS axis_x_sem,
       e.axis_y_sem AS axis_y_sem, e.category AS category, e.concept AS concept
ORDER BY name
"""

# Match vendor vocabulary through A2L concept rather than directly. ProECU has none of the
# three match keys because tree screenshots contain only names, and blind name matching is
# exactly the failure P6 prevents. The chain is map geometry -> A2L entry -> its concept ->
# vendor entries with the same concept.
#
# origin=factory is mandatory. Of 371 entries, 128 are not factory (RaceROM and ARC patches
# are external code absent from stock). Matching a stock map to a patch entry would be wrong
# rather than merely weak evidence.
VENDOR_BY_CONCEPT = """
MATCH (e:VendorEntry {family:'HR', origin:'factory'}) WHERE e.concept IN $concepts
RETURN e.vendor AS vendor, e.name AS name, e.group AS grp, e.axis_x AS axis_x,
       e.axis_y AS axis_y, e.output AS output, e.concept AS concept
ORDER BY concept, vendor, name
"""

# Content anchor: search documented defaults directly in component values. Print applies_to
# because EcuTek documents VQ37VHR while JK03A is VQ25HR without VVEL. Applicability is a
# worker decision rather than a filter here.
VENDOR_CONSTS = """
MATCH (f:VendorFact {family:'HR', kind:'const'})
RETURN f.vendor AS vendor, f.subject AS subject, f.value AS value, f.units AS units,
       f.statement AS statement, f.applies_to AS applies_to, f.concept AS concept
ORDER BY subject
"""


def shape(width, height):
    """Express table shape in the annotation-ledger vocabulary shared with the A2L catalog."""
    if width is None:
        return ""
    return f"{width}x{height}" if height else f"1D-{width}"


def group(rows, key):
    out = {}
    for r in rows:
        out.setdefault(r[key], []).append(r)
    return out


def components(session, rom):
    """Return graph components keyed by their lowest accessor address.

    The list is not stored because annotation changes the graph and a recorded list would
    become a second source of truth (P5, contract section 1).
    """
    out = []
    for r in session.run(COMPONENTS, rom=rom):
        if not r["accessors"]:
            continue
        out.append({"key": min(r["accessors"]),
                    "maps": sorted(r["maps"]),
                    "accessors": sorted(r["accessors"])})
    out.sort(key=lambda c: (-len(c["maps"]), c["key"]))
    return out


def read_values(image, m):
    """Read map values from the image; the graph stores only vmin/vmax/values_hash."""
    try:
        return image.table(m["addr"], m["width"], m["height"], m["storagetype"])
    except ValueError as e:
        return [[f"READ FAILED: {e}"]]


def grid(rows):
    """Render a map by rows: r5 (:AXIS_X) points are rows and r6 points are columns."""
    if not rows or isinstance(rows[0][0], str):
        return "    " + str(rows[0][0] if rows else "")
    w = max(len(str(v)) for row in rows for v in row)
    return "\n".join("    " + " ".join(str(v).rjust(w) for v in row) for row in rows)


def dumped(export_dir, addr, kind):
    """Read preparation-pass output; a missing file is an artifact fact, not an omission.

    A listing begins at the site address rather than the function because operands resolve
    there and a DumpListing window of +-24 instructions around the function entry does not
    reach the site.
    """
    path = os.path.join(export_dir, f"{kind}_{addr}.{'c' if kind == 'decomp' else 'txt'}")
    if not os.path.exists(path):
        return None, path
    with open(path) as f:
        return f.read().rstrip(), path


def render_site_listing(A, export_dir, site):
    """Render a listing only for a map with a census call site."""
    callsite = site["callsite"]
    A(f"##### Site `{callsite}` -> map `{site['tbl']}`")
    A("")
    if not callsite:
        A("No call site exists: the manual layer added this map outside the resolver "
          "census, so it has no site listing.")
    else:
        text, path = dumped(export_dir, callsite, "listing")
        if text is None:
            A(f"File `{os.path.basename(path)}` is missing: the preparation pass did not "
              f"cover this site.")
        else:
            A("```")
            A(text)
            A("```")
    A("")


# Calls whose addresses are directly visible in text: pseudocode `FUN_00021bbc` and listing
# `jsr` target (`-> 00021bbc`). :CALLS (query CALLED) is the primary channel because a call
# through a register leaves no address in text. This pattern supplements what the graph lacks.
CALLED_ADDR = re.compile(r"(?:\bFUN_|-> )(00[0-9a-f]{6})\b")
POOL_SYM = re.compile(r"\b((?:PTR_)?(?:DAT|FUN)_00([0-9a-f]{6}))\b")
POOL_ALIAS = re.compile(
    r"(?<![!<>=])\b(\w+)\s*=(?!=)\s*((?:PTR_)?(?:DAT|FUN)_00[0-9a-f]{6})\s*$"
)
POOL_EXPR = re.compile(r"\(\s*(\w+)\s*\+\s*(\w+|0x[0-9a-fA-F]+)\s*\)")
ASSIGN = re.compile(r"(?<![!<>=])\b(\w+)\s*=(?!=)\s*(.+)$")
NUMERIC = re.compile(r"0x[0-9a-fA-F]+[uUlL]*|\d+[uUlL]*")


def literal(image, addr):
    """Return interpretations of a pool literal at an address.

    Width is not visible in pseudocode: `mov.l @(disp,pc)` loads 32 bits with alignment 4,
    while `mov.w @(disp,pc)` loads 16 bits with sign extension. Return both because choosing
    between them requires validation rather than a builder guess.
    """
    d, out = image.data, {}
    if addr % 4 == 0 and addr + 4 <= len(d):
        out["mov.l"] = int.from_bytes(d[addr:addr + 4], "big")
    if addr % 2 == 0 and addr + 2 <= len(d):
        v = int.from_bytes(d[addr:addr + 2], "big")
        out["mov.w"] = v | 0xFFFF0000 if v & 0x8000 else v
    return out


def stable_addrs(values):
    """Return a canonical ordering of an address set."""
    return sorted(set(values))


def stable_map_facts(rows):
    """Return maps and their multivalued relationships in canonical order."""
    out = []
    for row in rows:
        fact = dict(row)
        for field in ("via", "kernel", "axis_x", "axis_y"):
            fact[field] = stable_addrs(fact.get(field) or [])
        out.append(fact)
    return sorted(out, key=lambda row: row["addr"])


def axis_contexts(session, rom, addrs):
    """Return complete deterministic context for every target axis.

    Select maps through direct AXIS_X/AXIS_Y relationships and accessors through direct
    ACCESSES relationships to those maps. Aggregate sets by axis so a shared axis is not
    reduced to the context of one arbitrary map.
    """
    wanted = stable_addrs(addrs)
    grouped = {}
    for row in session.run(AXIS_CONTEXTS, rom=rom, addrs=wanted):
        axis = row["axis"]
        context = grouped.setdefault(axis, {"maps": set(), "accessors": set()})
        if row["map"]:
            context["maps"].add(row["map"])
        if row["accessor"]:
            context["accessors"].add(row["accessor"])
    return {
        axis: {
            "key": axis,
            "maps": stable_addrs(context["maps"]),
            "accessors": stable_addrs(context["accessors"]),
        }
        for axis, context in sorted(grouped.items())
    }


def axis_focus_jobs(session, rom, addrs):
    """Return axis-<addr>.md jobs with full context or a precise membership error."""
    wanted = stable_addrs(addrs)
    contexts = axis_contexts(session, rom, wanted)
    missing = sorted(set(wanted) - set(contexts))
    if missing:
        raise SystemExit(f"axes are absent from the graph: {', '.join(missing)}")
    unlinked = [axis for axis in wanted if not contexts[axis]["maps"]]
    if unlinked:
        raise SystemExit(f"axes are not connected to maps: {', '.join(unlinked)}")
    return [(contexts[axis], None, axis, f"axis-{axis}.md") for axis in wanted]


def kinds_by_addr(rows):
    """Combine all access kinds per address independently of relationship order."""
    kinds = {}
    for row in rows:
        kinds.setdefault(int(row["addr"], 16), set()).add(row["kind"])
    return {addr: "".join(sorted(values)) for addr, values in kinds.items()}


def stable_sites(rows):
    """Return accesses in canonical order when accessor and call site match."""
    return sorted(rows, key=lambda row: (row["accessor"], row["callsite"], row["tbl"]))


def stable_callees(rows):
    """Return called functions in canonical order."""
    return sorted(rows, key=lambda row: (row.get("addr") or "", row.get("size") or -1))


def alias_snapshots(stmts, syms):
    """Track local alias values before each pseudocode statement.

    Ghidra reuses one local name for different RAM bases. A global alias dictionary would
    assign the final value to an earlier write and bind map output to the wrong register.
    Use the nearest preceding assignment; any non-pool assignment removes the previous alias.
    """
    aliases, snapshots = {}, []
    for stmt in stmts:
        snapshots.append(dict(aliases))
        assigned = ASSIGN.search(stmt)
        if not assigned:
            continue
        direct = POOL_ALIAS.search(stmt)
        name = assigned.group(1)
        if direct and direct.group(1) == name and direct.group(2) in syms:
            aliases[name] = direct.group(2)
        else:
            aliases.pop(name, None)
    return snapshots


def pool(image, text, regs):
    """Resolve pseudocode pool literals and position-specific expression bindings to registers.

    The decompiler prints a literal as `DAT_<address>` without substituting its value. In
    `*(byte *)(DAT_0008625c + DAT_0008608e)`, both base and displacement are symbols, so
    pseudocode does not reveal the register even though the artifact's USES table knows it.
    Without resolution, a consumer trace ends at the function name before showing what it
    does with the value, preventing a map claim from rising above `candidate`.

    The builder does not choose literal width. Arithmetic checked against the graph does:
    compare `base + displacement` first with this function's registers and then with every
    known ROM address. These states differ in strength and are not simply true/false.
    Ghidra does not resolve an access whose address is assembled in a register and creates no
    USES relationship, so the first check cannot confirm a real address in that case.
    """
    syms = {}
    for full, hexa in POOL_SYM.findall(text):
        addr = int(hexa, 16)
        if addr < len(image.data):
            syms[full] = (addr, literal(image, addr))
    known = kinds_by_addr(regs)
    stmts = split_stmts(text)
    aliases = alias_snapshots(stmts, syms)

    def base(term, current=None):
        sym = (current or {}).get(term, term)
        return syms.get(sym, (None, {}))[1].get("mov.l"), sym

    def disp(term, current=None):
        if NUMERIC.fullmatch(term):
            # The decompiler emits C suffixes (0x1c00U, ...L) and prints small displacements
            # in decimal (`iVar3 + 100`). One unusual literal must not abort the build; the
            # caller skips None.
            try:
                return int(term.rstrip("uUlL"), 0), term
            except ValueError:
                return None, term
        sym = (current or {}).get(term, term)
        v = syms.get(sym, (None, {}))[1]
        return v.get("mov.w"), sym

    binds, raw = {}, {}
    for index, (stmt, current) in enumerate(zip(stmts, aliases)):
        for match in POOL_EXPR.finditer(stmt):
            lhs, rhs = match.groups()
            b, bsym = base(lhs, current)
            o, osym = disp(rhs, current)
            if b is None or o is None or not 0xFFFF0000 <= b <= 0xFFFFFFFF:
                continue
            target = (b + o) & 0xFFFFFFFF
            binds[(bsym, osym)] = (target, known.get(target))
            # The same expression text can mean different addresses after local-base
            # reassignment, so the statement index is part of the key.
            key = re.sub(r"\s+", " ", match.group(0))
            raw[(index, key)] = target
    return syms, binds, raw, base, aliases, stmts


CALL = re.compile(r"(?:\(\*\(code \*\)\s*(?:\w+)\s*\)|\bFUN_[0-9a-f]{8})\s*\(")
VAR = re.compile(r"\b([a-zA-Z_]\w*)\b")
# `*(type *)(A + B) = rhs` or `*(type *)A = rhs`; the asterisk is required because without
# it the assignment targets a local variable rather than memory.
STORE = re.compile(r"\*\s*\(\s*(\w+)\s*\*\s*\)\s*(\([^;]*?\)|\w+)\s*=\s*([^;=][^;]*)$")
# Store width determines which addresses can read the value. A 16-bit store occupies two
# bytes; a reader of the high half accesses A and a reader of the low half accesses A+1.
STORE_WIDTH = {"char": 1, "uchar": 1, "byte": 1, "undefined1": 1,
               "short": 2, "ushort": 2, "undefined2": 2,
               "int": 4, "uint": 4, "undefined4": 4, "float": 4}
# Limit by reassignment count rather than textual distance. Unrelated statements can appear
# between a call and store while the variable remains unchanged. Taint spreads with depth,
# not distance.
#
# On JK03A, limits 2, 3, 4, and 6 produce the same result: 254 bindings across 586
# relationships. In this ROM a value either reaches memory within a few assignments or never
# does. The 135 trace breaks are a code property rather than a limit effect. The parameter
# remains protection against differently shaped code, not tuning toward an answer.
TAINT_DEPTH = 2


def attribute(image, text, regs, bases):
    """Find RAM registers receiving a map value from wrapper call sites.

    Accessors are wide: the widest ROM accessor writes 274 registers, and a consumer section
    built from all of them obscures the map value. The graph does not link them: ACCESSES
    knows site and base, while USES knows written registers. Pseudocode provides the link:
    the wrapper receives the map base as its first argument, its result gets a local name,
    and a store of that name is visible in text.

    A trace break is a fact rather than a gap. A value that does not reach memory is returned
    to the caller or consumed locally, and the map has no output register.
    """
    _syms, _binds, raw, resolve, aliases, stmts = pool(image, text, regs)
    known = {int(r["addr"], 16) for r in regs}
    out = []
    for i, st in enumerate(stmts):
        m = CALL.search(st)
        if not m:
            continue
        args = call_args(st, st.index("(", m.end() - 1))
        if not args:
            continue
        target, _sym = resolve(args[0], aliases[i])
        if target is None or f"{target:08x}" not in bases:
            continue
        rec = {"base": f"{target:08x}", "sink": None, "kind": None, "width": 0,
               "stmt": st}
        name = re.fullmatch(r"\w+", st[:m.start()].strip().rstrip("=").strip())
        if not name:
            # The result has no local name: it is returned or immediately consumed by the
            # expression containing the call.
            rec["kind"] = "return" if st.startswith("return") else "inline"
            out.append(rec)
            continue
        rec.update(trace_sink(stmts, i, name.group(0), raw, resolve, aliases, known))
        out.append(rec)
    return out


def trace_sink(stmts, call, name, raw, resolve, aliases, known):
    """Find the first memory store reachable from a call result.

    The value passes through intermediate names before a store, so trace forward through
    assignments rather than inspecting one statement.
    """
    live = {name: 0}
    for j in range(call + 1, len(stmts)):
        st = stmts[j]
        used = set(VAR.findall(st)) & set(live)
        if not used:
            continue
        sm = STORE.match(st) or STORE.search(st)
        if sm and set(VAR.findall(sm.group(3))) & set(live):
            key = re.sub(r"\s+", " ", sm.group(2))
            addr = raw.get((j, key))
            if addr is None and re.fullmatch(r"\w+", key):
                # Store without a displacement: the base is the register address.
                v, _sym = resolve(key, aliases[j])
                addr = v if v is not None and 0xFFFF0000 <= v <= 0xFFFFFFFF else None
            if addr is None:
                return {"sink": key, "kind": "unresolved", "width": 0}
            return {"sink": f"{addr:08x}",
                    "kind": "reg" if addr in known else "ram",
                    "width": STORE_WIDTH.get(sm.group(1), 1)}
        asg = re.fullmatch(r"(\w+) = (.*)", st)
        if asg:
            src = set(VAR.findall(asg.group(2))) & set(live)
            if src:
                d = min(live[v] for v in src) + 1
                if d <= TAINT_DEPTH:
                    live[asg.group(1)] = min(live.get(asg.group(1), d), d)
            elif asg.group(1) in live:
                # The name was reassigned an unrelated value. Remove taint so it does not
                # move to that value and select the wrong store.
                del live[asg.group(1)]
    return {"sink": None, "kind": "lost", "width": 0}


def split_stmts(text):
    """Split a function body into statements, joining long lines wrapped by Ghidra."""
    body = text[text.index("{", text.index(")")) + 1:]
    out, cur = [], []
    for ch in body:
        if ch in "{};":
            if "".join(cur).strip():
                out.append("".join(cur).strip())
            cur = []
            continue
        cur.append(" " if ch == "\n" else ch)
    return [re.sub(r"\s+", " ", s) for s in out]


def call_args(text, open_paren):
    """Extract call arguments up to the matching parenthesis, split on top-level commas."""
    depth, start, out = 0, open_paren + 1, []
    for i in range(open_paren, len(text)):
        c = text[i]
        if c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                out.append(text[start:i].strip())
                return [a for a in out if a]
        elif c == "," and depth == 1:
            out.append(text[start:i].strip())
            start = i + 1
    return []


ATTRIB_MISS = {
    "return": "the call result has no local name and is returned. This accessor has no "
              "map output register; the caller receives the value.",
    "inline": "the call result has no local name and is consumed by its containing "
              "expression. The statement itself shows what happens to it.",
    "unresolved": "a store was found but its address is assembled in a register and pool-"
                  "literal arithmetic cannot recover it. The address is real but no binding "
                  "was derived.",
    "lost": "no memory store was found within the trace. The value remains in processor "
            "registers and is either compared locally or passed through another call.",
}


def render_library(A, data, export_dir):
    """Render called-function contracts and complete listings.

    Use listings rather than pseudocode: these functions contain an unrolled loop, and the
    decompiler produces 31 KB for 282 bytes of code. Assembly for the same 282 bytes is
    directly readable and occupies 4 KB.
    """
    if not data["library"]:
        return
    A("## Called functions with analyzed contracts")
    A("")
    A("Functions called from the code shown above and analyzed separately. They receive "
      "arguments in REGISTERS rather than through the ABI, so Ghidra does not recover the "
      "convention: pseudocode shows calls without arguments and inputs as undeclared "
      "`in_r0`, `in_r1`. A map value enters such a function this way, and without a contract "
      "the trace would end there.")
    A("")
    A("A contract describes operation, argument and result registers, and side effects. It "
      "says nothing about a map because it belongs to a function shared across the ROM. The "
      "trace must still establish that THIS map's value passes through it.")
    A("")
    A("| Address | Role | Size | Confidence | Contract |")
    A("|---|---|---|---|---|")
    for f in data["library"]:
        size = f["size"] if f["size"] is not None else "-"
        A(f"| `{f['addr']}` | {f['role'] or '-'} | {size} | {f['contract_conf']} | "
          f"{f['contract']} |")
    A("")
    for f in data["library"]:
        text, path = dumped(export_dir, f["addr"], "funclisting")
        A(f"### Listing `{f['addr']}`")
        A("")
        if text is None:
            A(f"File `{os.path.basename(path)}` is missing: the preparation pass did not "
              f"process this function.")
        else:
            A("```")
            A(text)
            A("```")
        A("")


def render_attrib(A, data):
    """Render target-map output attribution."""
    A("## Output attribution")
    A("")
    A("The RAM register receiving this map's value. An accessor writes many registers at "
      "once, so consumers of the complete set reveal nothing about the map because its value "
      "is mixed with unrelated ones. Pseudocode provides attribution: the wrapper receives "
      "the map base as its first argument and its named result remains visible until a "
      "memory store.")
    A("")
    if not data["attrib"]:
        A("No wrapper call site with this map base was found in accessor pseudocode. The "
          "usual cause is a base selected by branching or arithmetic, so the first argument "
          "is not a literal. The consumer set below is derived from every accessor write and "
          "is not map-specific.")
        A("")
        return
    A("| Accessor | Sink | Width | State |")
    A("|---|---|---|---|")
    for r in data["attrib"]:
        if r["kind"] in ("reg", "ram"):
            state = ("confirmed by a graph relationship" if r["kind"] == "reg"
                     else "address recovered but no USES relationship exists")
            A(f"| `{r['acc']}` | `{r['sink']}` | {r['width']} | {state} |")
        else:
            A(f"| `{r['acc']}` | none | - | {ATTRIB_MISS[r['kind']]} |")
    A("")
    # A call statement is the shortest possible evidence because it contains both the map
    # base and the destination of its value. Without a sink, it is the only output evidence.
    miss = [r for r in data["attrib"] if r["kind"] not in ("reg", "ram")]
    if miss:
        A("Call statement for sites without a sink:")
        A("")
        A("```c")
        for r in miss:
            A(f"// {r['acc']}")
            A(r["stmt"][:400] + ";")
        A("```")
        A("")
    A(f"The value is traced through {TAINT_DEPTH} reassignments without a textual distance "
      "limit. Unrelated statements may separate a call and store; taint expands with depth "
      "rather than distance. An absent sink is a map fact rather than an artifact gap: a "
      "value that does not reach memory is consumed locally.")
    A("")


def bind_state(target, kind, all_regs):
    """Describe binding strength: graph relationship, graph node, or neither."""
    if kind:
        return f"access known ({kind})"
    if f"{target:08x}" in all_regs:
        return "address known, access unknown"
    return "address unknown"


def render_pool(A, image, text, regs, addr, all_regs):
    """Render pool resolution below function pseudocode."""
    syms, binds, _raw, _res, _aliases, _stmts = pool(image, text, regs)
    if not syms:
        return
    A(f"#### Pool symbols `{addr}`")
    A("")
    A("The decompiler does not substitute literal values and prints `DAT_<address>`. "
      "Pseudocode does not expose literal width (`mov.l` is 32 bits; `mov.w` is 16 bits "
      "with sign extension), so both interpretations are shown. Arithmetic chooses between "
      "them: for `base + displacement`, the valid pair is the one whose address the graph "
      "confirms as a register used by this function. A register named through the pool is "
      "the same register, so an address from this table has equal status to one from a "
      "listing.")
    A("")
    A("| Symbol | `mov.l` (32) | `mov.w` (16, signed) |")
    A("|---|---|---|")
    for sym, (a, lit) in sorted(syms.items(), key=lambda kv: kv[1][0]):
        l32 = f"`{lit['mov.l']:08x}`" if "mov.l" in lit else "-"
        l16 = f"`0x{lit['mov.w']:04x}`" if "mov.w" in lit else "-"
        A(f"| `{sym}` | {l32} | {l16} |")
    A("")
    if binds:
        A("| Expression | Address | Graph |")
        A("|---|---|---|")
        for (b, o), (t, kind) in sorted(binds.items(), key=lambda kv: kv[1][0]):
            A(f"| `{b} + {o}` | `{t:08x}` | {bind_state(t, kind, all_regs)} |")
        A("")
        A("The builder assembles each address in this table from image values. The `Graph` "
          "column only reports whether an independent witness exists and distinguishes three "
          "states. Confirmation strengthens a claim; lack of confirmation does not refute "
          "it. No state means \"wrong\":")
        A("")
        A("- `access known (R/W/L/D)` - the graph knows this access for this exact function. "
          "The image and graph independently converge on one address.")
        A("- `address known, access unknown` - a resolved reference uses the address "
          "somewhere in the ROM, but no relationship connects it to this function.")
        A("- `address unknown` - no resolved reference uses the address. This can mean an "
          "incorrect literal-width interpretation or a structure field accessed only by "
          "offset from a base held in a register. Ghidra does not resolve such an access, "
          "writes no reference, and creates no address node. In JK03A, the latter case "
          "includes the entire `ffff119c` structure and RAM axis input `ffff11ae`.")
        A("")
        A("Code rather than the table distinguishes these cases: in a valid pair, the base "
          "is a base obtained by the function and neighboring field offsets are contiguous.")
        A("")


def render(comp, rom, data, export_dir):
    """Render the component or focused target artifact used as the run agent's only input."""
    L = []
    A = L.append
    focus = data.get("focus")
    focus_axis = data.get("focus_axis")
    if focus_axis:
        A(f"# Axis `{focus_axis}` ({rom})")
    elif focus:
        A(f"# Map `{focus}` in component `{comp['key']}` ({rom})")
    else:
        A(f"# Component `{comp['key']}` ({rom})")
    A("")
    if focus_axis:
        A(f"Maps directly connected to the axis: {len(comp['maps'])}. "
          f"Accessors for these maps: {len(comp['accessors'])}.")
        A("")
        A(f"The target-axis context for `{focus_axis}` is aggregated over direct "
          f"`AXIS_X`/`AXIS_Y` relationships. It includes ALL connected maps "
          f"({', '.join(f'`{m}`' for m in comp['maps'])}) and ALL their accessors "
          f"({', '.join(f'`{a}`' for a in comp['accessors']) or 'none'}). A shared axis "
          f"can serve maps from different components, so one representative map does not "
          f"define the context boundary.")
        A("")
        A("Maps and accessors provide context for tracing the axis input. The interpolation "
          "machinery shows how axis points index a cell, while RAM and accessor code show "
          "where the current value comes from and which units represent it.")
    else:
        A(f"Maps in the component: {len(comp['maps'])}. "
          f"Accessors: {len(comp['accessors'])}.")
        A("")
        A("This is a connected component of the \"accessor -> map\" graph: none of its maps "
          "is read by an accessor outside the component, which defines its map membership. "
          "The component boundary limits membership, not evidence. A map's physical "
          "quantity is established by the interpolation machinery (wrapper, kernel, and "
          "finisher) and by what a RAM consumer does with the output. Both lie beyond the "
          "component and both appear in this artifact under \"Interpolation machinery\" and "
          "\"Output consumers\". A trace that stops at a RAM write has not reached semantics: "
          "`code` confidence requires tracing the value to a consumer.")
    A("")
    if focus:
        A(f"The target map is `{focus}`, and evidence is limited to its neighborhood. The "
          f"\"Accessors\", \"Interpolation machinery\", and \"Output consumers\" sections "
          f"are built from the {len(data['acc'])} accessors that read this map "
          f"({', '.join(f'`{a}`' for a in data['acc'])}), rather than all "
          f"{len(comp['accessors'])} accessors in the component. This omits no evidence "
          f"about the target map: an accessor that does not read it says nothing about it. "
          f"It does reduce evidence about NEIGHBORING maps, which remain in the \"Maps\" "
          f"section as values and geometry without their code.")
        A("")
        A("Task: follow section 6 of the `tools/map-sweep.md` contract and return a claim "
          f"(`semantics`, `role`, `units`, `scale_expr`, `confidence`) for EXACTLY map "
          f"`{focus}` and its axes. Neighboring maps are context: they show what else a "
          f"shared accessor reads and require distinguishing which map a trace belongs to.")
    elif focus_axis:
        A("Task: follow section 6 of the `tools/map-sweep.md` contract and return a claim "
          f"(`kind`, `units`, `scale_expr`, `to_byte`, `scale_conf`, `scale_evidence`, "
          f"`note`) for EXACTLY axis `{focus_axis}`. Connected maps, their other axes, and "
          f"their accessors are context rather than additional claim targets.")
    else:
        A("Task: follow section 6 of the `tools/map-sweep.md` contract and return a claim for "
          "each map (`semantics`, `role`, `units`, `scale_expr`, `confidence`) and each axis.")
    A("")
    A("Annotations are intentionally absent from the artifact because they are the required "
      "output. A claim without a trace is `candidate`, not `code`, however convincing a "
      "match appears. An all-`0xFF` map is not classified by shape.")
    A("")

    A("## Maps")
    A("")
    A("| Map | Shape | Element | Family | Entry | Kernel | X axis | Y axis | Values |")
    A("|---|---|---|---|---|---|---|---|---|")
    for m in data["maps"]:
        A(f"| `{m['addr']}` | {shape(m['width'], m['height'])} | {m['storagetype']} "
          f"| {m['family']} | {';'.join(m['via']) or '-'} | {';'.join(m['kernel']) or '-'} "
          f"| {';'.join(m['axis_x']) or '-'} | {';'.join(m['axis_y']) or '-'} "
          f"| {m['vmin']}..{m['vmax']} |")
    A("")
    A("Geometry is a property of the interpolation entry rather than the map: an entry is "
      "specialized for the table shape. The element type of a 2D map comes from its "
      "finisher, and every map is read as unsigned.")
    A("")

    for m in data["maps"]:
        tag = " - TARGET" if m["addr"] == focus else ""
        A(f"### Map `{m['addr']}` - {shape(m['width'], m['height'])} "
          f"{m['storagetype']}{tag}")
        A("")
        A(f"Range {m['vmin']}..{m['vmax']}, content hash `{m['values_hash']}`.")
        A("")
        A("```")
        A(grid(m["values"]))
        A("```")
        A("")

    if data["axes"]:
        A("## Axes")
        A("")
        A("| Axis | Points | Element | Increasing | Values |")
        A("|---|---|---|---|---|")
        for a in data["axes"]:
            tag = " - TARGET" if a["addr"] == focus_axis else ""
            A(f"| `{a['addr']}`{tag} | {a['len']} | {a['storagetype']} "
              f"| {'yes' if a['monotonic'] else 'NO'} "
              f"| {', '.join(str(v) for v in a['values'])} |")
        A("")
        A("Increasing order is a kernel requirement (a reverse linear scan from the highest "
          "point down to the first value `<=` the current input), not a semantic guess. An "
          "array that violates this rule cannot function as an axis. What the axis represents "
          "and how it is measured are code-derived conclusions established by tracing its "
          "RAM input.")
        A("")

    A("## Accessors")
    A("")
    if focus:
        A(f"Accessors for target map `{focus}`. Every call site is shown, including sites for "
          f"neighboring maps, because they distinguish which map a trace belongs to.")
        A("")
    elif focus_axis:
        A(f"All accessors for maps directly connected to target axis `{focus_axis}`. Every "
          f"accessor's call sites are shown in full: the `r5`/`r6` columns identify which "
          f"call uses the target axis and which belongs to neighboring context.")
        A("")
    for f_addr in data["acc"]:
        sites = [s for s in data["sites"] if s["accessor"] == f_addr]
        name = sites[0]["name"] if sites else f_addr
        A(f"### `{f_addr}` ({name})")
        A("")
        A("Call sites and resolver rewrite operands:")
        A("")
        A("| Site | Map | r4 | kind | r5 | kind5 | r6 | kind6 | verdict |")
        A("|---|---|---|---|---|---|---|---|---|")
        for s in sites:
            A(f"| `{s['callsite']}` | `{s['tbl']}` | `{s['r4']}` | {s['kind']} "
              f"| `{s['r5']}` | {s['kind5']} | `{s['r6']}` | {s['kind6']} "
              f"| {s['verdict']} |")
        A("")
        A("`kind=sp` means the decompiler did not fold the operand and a linear fallback "
          "recovered the value. The operand is branch-dependent, so the recovered value is "
          "one member of a set rather than a fact. `pool` is a pool pointer, `slice` is "
          "computed, and `const` is immediate.")
        A("")

        callers = [c for c in data["callers"] if c["accessor"] == f_addr]
        A(f"Callers ({len(callers)}): "
          + (", ".join(f"`{c['caller']}`" for c in callers) or "none - root"))
        A("")
        if callers:
            A("A caller produces the accessor input. An argument received through a register "
              "or the stack has no writer inside the accessor, so caller code establishes "
              "its physical quantity. The units of an axis obtained from an argument are "
              "established there.")
            A("")

        uses = [u for u in data["uses"] if u["accessor"] == f_addr]
        if uses:
            A(f"RAM and peripheral accesses ({len(uses)}):")
            A("")
            A("| Address | Region | Name | Access |")
            A("|---|---|---|---|")
            for u in uses:
                A(f"| `{u['reg']}` | {u['region']} | {u['name'] or '-'} "
                  f"| {''.join(sorted(u['kinds']))} |")
            A("")
            A("Access: `R` is read, `W` is write, `L` is address load, and `D` is data. "
              "A RAM axis input establishes its units; a RAM interpolation output establishes "
              "the map's meaning.")
            A("")

        text, path = dumped(export_dir, f_addr, "decomp")
        A(f"#### C pseudocode `{f_addr}`")
        A("")
        if text is None:
            A(f"File `{os.path.basename(path)}` is missing: the preparation pass did not "
              f"process this function. This is a missing preparation step rather than a "
              f"component property, and the trace cannot proceed without it.")
        else:
            A("```c")
            A(text)
            A("```")
            A("")
            render_pool(A, data["image"], text, data["func_regs"].get(f_addr, []), f_addr,
                        data["all_regs"])
        A("")

        for c in callers:
            text, path = dumped(export_dir, c["caller"], "decomp")
            A(f"#### Caller C pseudocode `{c['caller']}`")
            A("")
            if text is None:
                A(f"File `{os.path.basename(path)}` is missing: the preparation pass did not "
                  f"process this function. This is a missing preparation step rather than a "
                  f"component property.")
            else:
                A("```c")
                A(text)
                A("```")
                A("")
                render_pool(A, data["image"], text,
                            data["func_regs"].get(c["caller"], []), c["caller"],
                            data["all_regs"])
            A("")

        A(f"#### Site listings `{f_addr}`")
        A("")
        for s in sites:
            render_site_listing(A, export_dir, s)

    A("## Interpolation machinery")
    A("")
    A("The accessor does not read a map cell. A wrapper specialized for the table shape and "
      "its kernel read it; the kernel calls a finisher that defines saturation and element "
      "type. This is the code between the map and the RAM output write, so this section, "
      "rather than the call site, shows what the cell becomes before it is written.")
    A("")
    A("| Address | Role | Size | Calls |")
    A("|---|---|---|---|")
    for k in data["kernels"]:
        cs = ", ".join(f"`{c['addr']}` ({c['size']} B)"
                       for c in stable_callees(k["callees"]) if c.get("addr"))
        A(f"| `{k['addr']}` | {k['role']} | "
          f"{k['size'] if k['size'] is not None else 'UNDEFINED'} | {cs or '-'} |")
    A("")
    if data["kernel_listings"]:
        A("`UNDEFINED`: the wrapper reaches this kernel through `jmp` rather than `jsr`, and "
          "the region has not been defined as a function. Such a kernel has no C pseudocode, "
          "but its listing appears below. Function definition is required by the decompiler, "
          "not the disassembler. Trace through this kernel using the listing; its undefined "
          "function boundary alone does not limit claim confidence.")
        A("")
    for f_addr in data["kernel_funcs"]:
        text, path = dumped(export_dir, f_addr, "decomp")
        A(f"### C pseudocode `{f_addr}`")
        A("")
        if text is None:
            A(f"File `{os.path.basename(path)}` is missing: the preparation pass did not "
              f"process this function.")
        else:
            A("```c")
            A(text)
            A("```")
            A("")
            render_pool(A, data["image"], text, data["func_regs"].get(f_addr, []), f_addr,
                        data["all_regs"])
        A("")

    for k_addr in data["kernel_listings"]:
        text, path = dumped(export_dir, k_addr, "listing")
        A(f"### Listing `{k_addr}` - kernel without a function definition")
        A("")
        if text is None:
            A(f"File `{os.path.basename(path)}` is missing: the preparation pass did not "
              f"process this address.")
        else:
            A("```")
            A(text)
            A("```")
        A("")

    render_library(A, data, export_dir)

    if data["focus"]:
        render_attrib(A, data)

    A("## Output consumers")
    A("")
    if not data["consumers"]:
        regs = data["write_regs"]
        A("There are no consumers. The section is empty because of graph state rather than "
          "a builder omission, which is a fact about this accessor set rather than an "
          "artifact gap.")
        A("")
        if data["sinks"]:
            named = ", ".join("`%s`" % s for s in data["sinks"])
            A(f"Output attribution defines the set: output {named} has no readers outside "
              "the accessor. The map value is either consumed inside the accessor or not "
              "consumed at all. Both cases are established from accessor code rather than "
              "neighbor code. Other accessor registers carry unrelated quantities and say "
              "nothing about the target map.")
        elif not regs:
            A("The component accessor writes no RAM register. The trace ends inside the "
              "accessor: the map output either returns to the caller as a value or is "
              "compared locally. Its meaning, if established, comes from accessor and call "
              "site code.")
        else:
            hot = [r for r in regs if r["readers"] > data["maxr"]]
            cold = [r for r in regs if r["readers"] == 0]
            A(f"The accessor writes {len(regs)} RAM registers, but none passed selection: "
              f"{len(cold)} have no reader outside the component and {len(hot)} exceed the "
              f"reader cutoff of {data['maxr']}.")
            A("")
            A("| Register | External readers |")
            A("|---|---|")
            for r in regs[:24]:
                A(f"| `{r['reg']}` | {r['readers']} |")
            if len(regs) > 24:
                A(f"| ... {len(regs) - 24} more | |")
            A("")
            A("A register without external readers is an unconsumed output: either its branch "
              "is dead or the accessor itself reads it. A register above the cutoff is a "
              "shared bus whose consumers reveal nothing about the map. Neither case "
              "establishes map semantics, so the claim remains `candidate`.")
        A("")
    else:
        A("Functions that read RAM written by the accessor. What happens to the output next "
          "establishes map meaning: a RAM write is the middle of a trace, not its end.")
        A("")
        if data["sinks"]:
            named = ", ".join("`%s`" % s for s in data["sinks"])
            A(f"Output attribution defines the set: these are readers of output {named} and "
              "nothing else. Other accessor registers carry unrelated quantities and are "
              "excluded, so no sharing cutoff is needed because the set is map-specific by "
              "construction. Sharing of the attributed register itself remains visible: if "
              "dozens of functions read it, every one appears here, which is a fact about "
              "the map.")
        else:
            A("No output attribution exists, so the set is derived from every accessor write "
              "and mixes unrelated quantities with the map value. It includes consumers of "
              f"registers with no more than {data['maxr']} readers: a register with one "
              "reader is private to this accessor, while a register with dozens of readers "
              "is a shared global whose consumers reveal nothing about the map. This table "
              "does not establish that a consumer belongs to this specific map; code must "
              "verify that relationship.")
        A("")
        A("The table is complete and contains every selected consumer. C pseudocode has a "
          "separate budget, and the \"Code\" column identifies which consumers have it below. "
          "Consumers are ordered first by relationship specificity (the fewest readers of "
          "the connecting register), then by size. A private register is closer to the map "
          "output than a moderately shared one.")
        A("")
        A("| Consumer | Size | Register readers | Registers read | Code | Registers |")
        A("|---|---|---|---|---|---|")
        shown = {c["consumer"] for c in data["consumers_decomp"]}
        for c in data["consumers"]:
            A(f"| `{c['consumer']}` | {c['size']} | {c['spec']} | {len(c['regs'])} "
              f"| {'yes' if c['consumer'] in shown else 'no'} "
              f"| {', '.join('`%s`' % r for r in sorted(c['regs']))} |")
        A("")
        if data["consumers_cut"]:
            A(f"Pseudocode is absent for {data['consumers_cut']} of "
              f"{len(data['consumers'])} consumers. The decompilation budget covers the "
              f"{len(data['consumers_decomp'])} most specific consumers. This is an artifact "
              f"boundary rather than a map fact. If a trace reaches a consumer without code, "
              f"submit a `candidate` claim with its address in `note`; do not infer meaning "
              f"from the register name.")
            A("")
        for c in data["consumers_decomp"]:
            text, path = dumped(export_dir, c["consumer"], "decomp")
            A(f"### C pseudocode `{c['consumer']}`")
            A("")
            if text is None:
                A(f"File `{os.path.basename(path)}` is missing: the preparation pass did not "
                  f"process this function.")
            else:
                A("```c")
                A(text)
                A("```")
                A("")
                render_pool(A, data["image"], text,
                            data["func_regs"].get(c["consumer"], []), c["consumer"],
                            data["all_regs"])
            A("")

    A("## Reference catalogs")
    A("")
    A("Catalogs contain no addresses: they define classes rather than placement. A catalog "
      "name provides `candidate` identity, not semantics. Units and a scale multiplier are "
      "also catalog annotations; when obtained from a shape match, they support `candidate`, "
      "not `code` (P6).")
    A("")
    by_shape = {}
    for m in data["maps"]:
        by_shape.setdefault((m["dims"], shape(m["width"], m["height"])),
                            []).append(m["addr"])
    for (dims, sh), addrs in sorted(by_shape.items(), key=lambda kv: kv[0]):
        cands = data["a2l"].get((dims, sh), [])
        A(f"### Shape {sh}: maps {', '.join('`%s`' % a for a in addrs)}")
        A("")
        if not cands:
            A("The catalog has no entry with this shape.")
            A("")
            continue
        A(f"Catalog entries with this shape: {len(cands)}.")
        A("")
        A("| Name | Unit | Scale | Element | X axis | Y axis | Category |")
        A("|---|---|---|---|---|---|---|")
        for c in cands:
            A(f"| {c['name']} | {c['unit'] or '-'} | {c['scale_expr'] or '-'} "
              f"| {c['storagetype'] or '-'} | {c['axis_x_sem'] or '-'} "
              f"| {c['axis_y_sem'] or '-'} | {c['category'] or '-'} |")
        A("")
    A("Geometry is the only available key. Of the three match keys (`dims`, scale family, "
      "and axis semantics), the latter two are themselves annotations intentionally absent "
      "from the artifact. Sixteen catalog entries have a 16x16 shape, so shape is a clue, "
      "not identification; tracing the RAM axis inputs distinguishes them.")
    A("")

    A("### Vendor dictionaries linked through A2L `concept` (`origin=factory` only)")
    A("")
    if not data["concepts"]:
        A("Shape-matched catalog entries have no `concept`, so no vendor-dictionary link is "
          "established. Blind name matching is prohibited (P6).")
        A("")
    elif not data["vendor"]:
        A(f"The A2L concepts for entries with this shape "
          f"({', '.join('`%s`' % c for c in data['concepts'])}) have no factory vendor "
          f"entries.")
        A("")
    else:
        A(f"Chain: map geometry -> A2L entry -> its `concept` -> vendor entries. "
          f"Concepts: {', '.join('`%s`' % c for c in data['concepts'])}.")
        A("")
        A("| Vendor | Name | Group | X axis | Y axis | Output | concept |")
        A("|---|---|---|---|---|---|---|")
        for v in data["vendor"]:
            A(f"| {v['vendor']} | {v['name']} | {v['grp'] or '-'} | {v['axis_x'] or '-'} "
              f"| {v['axis_y'] or '-'} | {v['output'] or '-'} | {v['concept'] or '-'} |")
        A("")
        A("A `concept` represents a calibration family rather than one table. Variants of "
          "one function share it, so one concept can have multiple entries.")
        A("")

    A("### Content anchors: documented defaults against flat maps")
    A("")
    if not data["anchors"]:
        A("No matches: no flat-map constant in the component equals a documented dictionary "
          "default.")
        A("")
    else:
        A("| Value | Vendor | Subject | Unit | Applies to | Maps |")
        A("|---|---|---|---|---|---|")
        for a in data["anchors"]:
            A(f"| {a['value']} | {a['vendor']} | {a['subject']} | {a['units'] or '-'} "
              f"| {a['applies_to']} | {', '.join('`%s`' % x for x in a['in_maps'])} |")
        A("")
        A("A value match alone supports `pattern`, not `candidate`: shorter numbers occur "
          "by chance more often. A homologous block signature or consumer trace raises the "
          "finding to `candidate`. Applicability must be checked: EcuTek documents VQ37VHR "
          "with VVEL, while JK03A is VQ25HR without VVEL.")
        A("")
    A("Defaults are compared only with flat maps (`vmin == vmax`). Almost any byte occurs in "
      "a 256-cell surface, so a match there would have no significance.")
    A("")

    return "\n".join(L) + "\n"


# Annotation fields whose values are free text. A matching value in the artifact is a leak.
# Map role, confidence, units, and axis kind are intentionally excluded: their vocabularies
# are closed and short ('table', 'code', 'deg', 'rpm'), so substring matches would occur by
# chance and create noise in both directions. The RETURN allowlist, rather than this check,
# excludes them; the two mechanisms serve different purposes.
ANSWER_TEXT = ("semantics", "note", "scale_expr", "to_byte", "evidence",
               "contract_evidence", "scale_evidence")


def answer_occurs(text, value, field):
    """Match an answer in text without false substrings for short to_byte expressions."""
    if field == "to_byte" and len(value.strip()) < 4:
        # `x`, `x/2`, and `x/4` are valid inverse scales. A plain substring search would
        # match `x` inside `scale_expr` and `x/2` inside `x/20`; expression boundaries keep
        # the audit effective while removing these known false matches.
        pattern = rf"(?<![\w.+*/%-]){re.escape(value)}(?![\w.+*/%-])"
        return re.search(pattern, text) is not None
    return value in text


def catalog_strings(data):
    """Return strings that may legitimately enter the artifact from a catalog.

    The contract requires a catalog in the artifact (section 2), and annotations often
    originate from that same catalog. A2L itself declares the 'x-64' scale for 16x16
    ignition maps, while the graph marks it [cand] because the catalog multiplier is not
    confirmed by code. An annotation that matches a catalog string exactly is excluded
    from leak detection: an independent source explains its presence, and the agent sees
    the catalog rather than the answer.
    """
    out = set()
    for rows in list(data["a2l"].values()) + [data["vendor"], data["anchors"]]:
        for r in rows:
            out |= {v for v in r.values() if isinstance(v, str)}
    return out


def verify_blind(text, answers, allowed):
    """Treat blinding as a verifiable run property rather than query-author intent.

    Compare artifact text against the annotations it must not contain. This catches both
    mistakes in RETURN clauses and annotations that leak through another field: a function
    name from symbols.csv, semantically named C pseudocode, or a rewrite string. A leak is
    an annotation without an independent source in `allowed`. A finding aborts the run:
    an artifact containing the answer turns calibration into a rehearsal and invalidates
    the only run that can test the harness.
    """
    leaks = []
    for row in answers:
        for field in ANSWER_TEXT:
            value = row.get(field)
            if not value or not isinstance(value, str):
                continue
            if len(value.strip()) < 4 and field != "to_byte":
                continue
            if not answer_occurs(text, value, field):
                continue
            # Validate the independent source with the same match used for the leak. The
            # `x-128` scale occurs inside the catalog string `Degrees (x-128)*0.5`, and that
            # independent source explains its presence just as an exact match would. Using a
            # substring for the leak but exact equality for the source would abort runs on
            # short common values, which dominate offset-binary scales.
            if any(answer_occurs(a, value, field) for a in allowed):
                continue
            leaks.append(f"{row['addr']}.{field} = {value!r}")
    return leaks


def build(session, image, rom, comp, export_dir, catalog, maxr, focus=None,
          maxdec=24, focus_axis=None):
    # The component or complete axis context defines map membership, while focus defines
    # evidence membership. Without focus the whole component is the neighborhood; with a
    # map focus, its accessors are the neighborhood. For an axis, comp already contains the
    # exact union of all directly connected maps and accessors.
    if focus and focus_axis:
        raise ValueError("map and axis focus are mutually exclusive")
    if focus:
        acc = stable_addrs(session.run(FOCUS_ACC, rom=rom, map=focus).single()["accessors"])
        if not acc:
            raise SystemExit(f"no accessor reads map {focus}")
    else:
        acc = stable_addrs(comp["accessors"])
    maps = stable_map_facts(
        r.data() for r in session.run(MAP_FACTS, rom=rom, addrs=stable_addrs(comp["maps"]))
    )
    for m in maps:
        m["values"] = read_values(image, m)
    axes = sorted({a for m in maps for a in m["axis_x"] + m["axis_y"]})
    if focus_axis and focus_axis not in axes:
        raise SystemExit(f"axis {focus_axis} is not connected to the context maps")
    kernels = sorted(
        (r.data() for r in session.run(KERNELS, rom=rom,
                                       maps=[focus] if focus else stable_addrs(comp["maps"]))),
        key=lambda row: row["addr"],
    )
    data = {
        "maps": maps,
        "focus": focus,
        "focus_axis": focus_axis,
        "acc": acc,
        "axes": sorted(
            (r.data() for r in session.run(AXIS_FACTS, rom=rom, addrs=axes)),
            key=lambda row: row["addr"],
        ),
        "sites": stable_sites([r.data() for r in session.run(SITES, rom=rom, addrs=acc)]),
        "callers": [r.data() for r in session.run(CALLERS, rom=rom, addrs=acc)],
        "uses": [r.data() for r in session.run(USES, rom=rom, addrs=acc)],
        "kernels": kernels,
        "write_regs": [r.data() for r in session.run(WRITE_REGS, rom=rom, addrs=acc)],
        "maxr": maxr,
        "a2l": {},
        "vendor": [],
        "concepts": [],
        "anchors": [],
    }
    # Output attribution precedes consumer discovery and defines the consumer set. Without
    # focus there is no single output to attribute: a component contains multiple maps
    # whose outputs cannot be combined into one set.
    data["all_regs"] = set(session.run(ALL_REGS, rom=rom).single()["addrs"])
    acc_regs = {r["func"]: r["regs"] for r in session.run(FUNC_REGS, rom=rom, addrs=acc)}
    data["attrib"] = []
    if focus:
        bases = {m["addr"] for m in maps}
        for a in acc:
            text, _p = dumped(export_dir, a, "decomp")
            if text is None:
                continue
            for rec in attribute(image, text, acc_regs.get(a, []), bases):
                if rec["base"] == focus:
                    data["attrib"].append({"acc": a, **rec})
    sinks = sorted({r["sink"] for r in data["attrib"] if r["kind"] in ("reg", "ram")})
    # A value wider than one byte occupies multiple addresses, and a reader may access any
    # of them. The write width defines the window rather than an assumption about adjacency.
    span = sorted({f"{int(r['sink'], 16) + k:08x}"
                   for r in data["attrib"] if r["kind"] in ("reg", "ram")
                   for k in range(max(r["width"], 1))})
    data["sinks"] = sinks
    if sinks:
        data["consumers"] = [r.data() for r in
                             session.run(CONSUMERS_OF, rom=rom, addrs=acc, regs=span)]
    else:
        data["consumers"] = [r.data() for r in
                             session.run(CONSUMERS, rom=rom, addrs=acc, maxr=maxr)]
    # The consumer table is complete, while code has a budget. The query already orders
    # consumers by specificity, so the head of the list is closest to the map output.
    data["consumers_decomp"] = data["consumers"][:maxdec]
    data["consumers_cut"] = len(data["consumers"]) - len(data["consumers_decomp"])
    # Only defined functions can be decompiled. A kernel reached by jmp has no size or file.
    data["kernel_funcs"] = sorted(
        {k["addr"] for k in kernels if k["size"] is not None}
        | {c["addr"] for k in kernels for c in k["callees"] if c.get("addr")}
    )
    # A kernel reached by jmp is provided as a listing: the decompiler needs a function
    # definition, but the disassembler does not. Without this listing the agent would see
    # the kernel address without seeing the kernel itself.
    data["kernel_listings"] = sorted({k["addr"] for k in kernels if k["size"] is None})
    # Pool resolution: the image supplies a literal value and the graph supplies a set
    # against which to verify it.
    data["image"] = image
    decompiled = sorted(set(acc) | set(data["kernel_funcs"])
                        | {c["consumer"] for c in data["consumers_decomp"]}
                        | {c["caller"] for c in data["callers"]})
    data["func_regs"] = {r["func"]: r["regs"] for r in
                         session.run(FUNC_REGS, rom=rom, addrs=decompiled)}
    # Functions called by displayed code and analyzed by the code layer. The arithmetic
    # library (0x21000..0x23000) passes arguments in registers. Ghidra does not recover the
    # convention and renders these calls without arguments, so a map value can enter such
    # a function and end the trace. A contract bridges that gap.
    shown = sorted(set(decompiled) | set(data["kernel_listings"]))
    called = {r["addr"] for r in session.run(CALLED, rom=rom, addrs=shown)}
    # Listings show a jsr target directly (`-> 00021bbc`). Where Ghidra did not build a
    # relationship, text remains the only source. Combine both channels.
    for a in shown:
        text, _p = dumped(export_dir, a, "decomp")
        if text is None:
            text, _p = dumped(export_dir, a, "listing")
        if text:
            called |= {m.group(1) for m in CALLED_ADDR.finditer(text)}
    called -= set(decompiled)
    data["library"] = [r.data() for r in
                       session.run(CONTRACTS, rom=rom, addrs=sorted(called))]
    for m in maps:
        key = (m["dims"], shape(m["width"], m["height"]))
        if key not in data["a2l"]:
            data["a2l"][key] = catalog["a2l"].get(key, [])
    concepts = sorted({c["concept"] for rows in data["a2l"].values() for c in rows
                       if c.get("concept")})
    data["concepts"] = concepts
    data["vendor"] = [v for v in catalog["vendor"] if v["concept"] in set(concepts)]

    # Search for anchors only in flat maps (vmin == vmax). Almost any byte occurs in a
    # 256-cell surface, so a documented-default match there has no significance. Pattern
    # scanning has already made this data-shape error twice (P6). In a flat map the constant
    # is the map itself, so a default match is a useful signal.
    flat = {m["addr"]: m["vmin"] for m in maps if m["vmin"] == m["vmax"]}
    for c in catalog["consts"]:
        hits = sorted(a for a, v in flat.items() if v == c["number"])
        if hits:
            data["anchors"].append(dict(c, in_maps=hits))

    text = render(comp, rom, data, export_dir)
    answers = [r.data() for r in session.run(MAP_ANSWERS, rom=rom, addrs=comp["maps"])]
    answers += [r.data() for r in session.run(AXIS_ANSWERS, rom=rom, addrs=axes)]
    answers += [r.data() for r in session.run(FUNC_ANSWERS, rom=rom)]
    return text, verify_blind(text, answers, catalog_strings(data))


def load_catalog(session):
    """Load ROM-independent catalogs once per run rather than once per component."""
    pairs = [(r["dims"], r["shape"]) for r in
             session.run("MATCH (e:A2LEntry {family:'HR'}) RETURN DISTINCT "
                         "e.dims AS dims, e.shape AS shape")]
    a2l = {}
    for dims, sh in pairs:
        a2l[(dims, sh)] = [x.data() for x in session.run(A2L_BY_SHAPE, dims=dims,
                                                         shape=sh)]
    concepts = [r["c"] for r in session.run(
        "MATCH (e:A2LEntry {family:'HR'}) WHERE e.concept <> '' RETURN DISTINCT e.concept AS c")]
    vendor = [x.data() for x in session.run(VENDOR_BY_CONCEPT, concepts=concepts)]
    consts = []
    for r in session.run(VENDOR_CONSTS):
        c = r.data()
        num = re.match(r"^-?\d+(\.\d+)?$", str(c["value"]).strip())
        if not num:
            continue
        v = float(c["value"])
        if v != int(v) or not 0 <= v <= 0xFFFF:
            continue          # A map cell is an integer within the element range.
        consts.append(dict(c, number=int(v)))
    return {"a2l": a2l, "vendor": vendor, "consts": consts}


def nonnegative_int(value):
    """Parse an integer >= 0 for artifact budgets."""
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("value must be >= 0")
    return parsed


def focus_addrs(values, path=None):
    """Collect stable, deduplicated lowercase addresses from repeated flags and a file."""
    out = [value.strip().lower() for value in values if value.strip()]
    if path:
        with open(path, encoding="utf-8") as source:
            out.extend(line.strip().lower() for line in source if line.strip())
    return stable_addrs(out)


def main():
    p = argparse.ArgumentParser(description="Component artifacts for sweep (map-sweep.md)")
    p.add_argument("out_dir")
    p.add_argument("--rom", default="JK08A")
    p.add_argument("--accessor", action="append", default=[],
                   help="component key: one of its accessor addresses (wave 0: 00082c8a)")
    p.add_argument("--focus-map", action="append", default=[],
                   help="build an artifact for one map rather than a component: evidence is "
                        "limited to the map's accessors and the file is map-<addr>.md")
    p.add_argument("--focus-maps-file", default=None,
                   help="same operation from a file containing one map address per line")
    p.add_argument("--focus-axis", action="append", default=[],
                   help="build an axis artifact with the complete context of every connected "
                        "map and accessor; the file is axis-<addr>.md")
    p.add_argument("--focus-axes-file", default=None,
                   help="same operation from a file containing one axis address per line")
    p.add_argument("--min-maps", type=int, default=0)
    p.add_argument("--max-maps", type=int, default=10 ** 6)
    p.add_argument("--max-readers", type=nonnegative_int, default=8,
                   help="maximum register reader count for including a consumer in the "
                        "artifact: a measure of output specificity")
    p.add_argument("--max-consumer-decomp", type=nonnegative_int, default=24,
                   help="consumer C-pseudocode budget; the table remains complete and code "
                        "is shown for this many most-specific consumers")
    p.add_argument("--export-dir", default=None,
                   help="preparation-pass directory containing decomp_<addr>.c and "
                        "listing_<addr>.txt")
    p.add_argument("--audit-output", default=None,
                   help="JSON report for a successful blind gate and artifact SHA-256 values")
    args = p.parse_args()
    focus_maps = focus_addrs(args.focus_map, args.focus_maps_file)
    focus_axes = focus_addrs(args.focus_axis, args.focus_axes_file)
    if focus_maps and focus_axes:
        p.error("map focus and axis focus are mutually exclusive")

    export_dir = args.export_dir or EXPORT.format(rom=args.rom)
    image = romkit.load(args.rom)
    driver = GraphDatabase.driver(BOLT, auth=("", ""))
    os.makedirs(args.out_dir, exist_ok=True)

    with driver.session() as s:
        comps = components(s, args.rom)
        if not comps:
            sys.exit(f"the graph has no components for rom={args.rom}; build the layer with "
                     f"tools/memgraph/load_maps.py")
        if focus_axes:
            jobs = axis_focus_jobs(s, args.rom, focus_axes)
        elif focus_maps:
            by_map = {m: c for c in comps for m in c["maps"]}
            missed = [m for m in focus_maps if m not in by_map]
            if missed:
                sys.exit(f"maps are absent from the graph: {', '.join(sorted(missed))}")
            jobs = [(by_map[m], m, None, f"map-{m}.md") for m in focus_maps]
        else:
            if args.accessor:
                want = {a.lower() for a in args.accessor}
                picked = [c for c in comps if want & set(c["accessors"])]
                missed = want - {a for c in picked for a in c["accessors"]}
                if missed:
                    sys.exit(f"accessors are absent from the graph: "
                             f"{', '.join(sorted(missed))}")
            else:
                picked = [c for c in comps
                          if args.min_maps <= len(c["maps"]) <= args.max_maps]
            jobs = [(c, None, None, f"comp-{c['key']}.md") for c in picked]
        catalog = load_catalog(s)
        print(f"components in graph: {len(comps)}, artifacts to build: {len(jobs)}")

        leaked = 0
        audit_artifacts = []
        for c, focus, focus_axis, fname in jobs:
            text, leaks = build(
                s, image, args.rom, c, export_dir, catalog, args.max_readers,
                focus=focus, maxdec=args.max_consumer_decomp, focus_axis=focus_axis,
            )
            path = os.path.join(args.out_dir, fname)
            with open(path, "w") as f:
                f.write(text)
            with open(path, "rb") as artifact_stream:
                artifact_sha256 = hashlib.sha256(artifact_stream.read()).hexdigest()
            audit_artifacts.append({
                "target_address": focus or focus_axis or c["key"],
                "path": str(Path(path).resolve()),
                "sha256": artifact_sha256,
                "blind_verified": not leaks,
            })
            if focus_axis:
                note = (f"axis {focus_axis}, {len(c['maps'])} maps, "
                        f"{len(c['accessors'])} accessors")
            elif focus:
                note = f"component {c['key']}, {len(c['maps'])} maps"
            else:
                note = f"{len(c['maps'])} maps, {len(c['accessors'])} accessors"
            if leaks:
                leaked += 1
                print(f"  {os.path.basename(path)}: {note} - BLINDING VIOLATION")
                for x in leaks:
                    print(f"      leaked: {x}")
            else:
                print(f"  {os.path.basename(path)}: {note}")
    driver.close()

    if leaked:
        sys.exit(f"artifacts containing annotations: {leaked}; the run is invalid because "
                 f"an agent that can read the answer does not test the harness")

    if args.audit_output:
        builder_path = str(Path(__file__).resolve())
        with open(builder_path, "rb") as builder_stream:
            builder_sha256 = hashlib.sha256(builder_stream.read()).hexdigest()
        audit = {
            "schema": "vq.blind-artifact-audit/v1",
            "rom": args.rom,
            "mode": "focus-maps" if focus_maps else "focus-axes" if focus_axes else "components",
            "targets": focus_maps or focus_axes or [item["target_address"] for item in audit_artifacts],
            "builder_path": builder_path,
            "builder_sha256": builder_sha256,
            "export_dir": str(Path(export_dir).resolve()),
            "max_readers": args.max_readers,
            "max_consumer_decomp": args.max_consumer_decomp,
            "artifacts": audit_artifacts,
        }
        audit_path = str(Path(args.audit_output).resolve())
        os.makedirs(os.path.dirname(audit_path), exist_ok=True)
        data = (json.dumps(audit, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
        if os.path.exists(audit_path):
            with open(audit_path, "rb") as existing:
                if existing.read() != data:
                    sys.exit(f"blind audit already exists with different content: {audit_path}")
        with open(audit_path, "wb") as audit_stream:
            audit_stream.write(data)


if __name__ == "__main__":
    main()
