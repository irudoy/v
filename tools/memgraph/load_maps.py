#!/usr/bin/env python3
# Load the calibration layer described in tools/map-analysis-pipeline.md
# into Memgraph: :Interp/:Map/:Axis nodes and
# :ACCESSES/:VIA/:KERNEL/:AXIS_X/:AXIS_Y relationships. Adds what :CALLS does not
# contain: call operands identifying which table and axes an accessor passes in r4/r5/r6
# at indirect interpolation callsites.
#
# Four sources each own a distinct part:
#   defs/<source>.interp.csv - interpolation-entry registry: each row is an entry with
#                              geometry recovered from its code;
#   accessors.<kernel>.csv   - resolver censuses (ResolveAccessors.java): sites and operands
#                              recovered by decompiler data flow;
#   defs/<source>.findings.csv - manual map layer: facts established by a person that the
#                                census cannot provide (semantics, units, confidence, role);
#   defs/<source>.axes.csv   - manual axis layer: axis semantics and units.
# defs/rom-inheritance.toml resolves canonical <source>. An exact-code inheritor retains its
# own export, image, and graph layer without copying these files. Units belong to the manual
# layer rather than the census because a consumer trace establishes scaling, not a call
# operand. The resolver sees an array pointer but not how engine arithmetic transforms its
# value.
#
# The fifth source is the ROM image itself (rom-images/roms.csv registry -> dump file,
# verified by SHA-256). The census says which address and shape to read; the image supplies
# its contents. This is Stage 4: range, contents, and axis monotonicity.
#
# Load the complete layer from all censuses in one run. Layer nodes are recreated on every
# run, so loading one census at a time would make the second core delete maps from the first.
# The same reason keeps the manual layer here rather than in a separate pass: a finding lives
# on the same node as its census fact and would disappear when that node is recreated.
#
# Registry (one entry per row):
#   family       - explicit axis (breakpoint array in ROM, pointer in r5/r6) or implicit
#                  axis (no array; points 0..N-1 at uniform raw-input steps);
#   kernel       - shared entry engine and census filename; a fused entry (wrapper, kernel,
#                  and axis search in one leaf, as in 1ME3B) names itself here;
#   wrapper      - address of the entry itself;
#   width/height - axis point count; empty height means a one-dimensional entry;
#   step         - implicit-axis step (implicit only);
#   storagetype  - element type. A 1D entry reads it itself; a 2D entry delegates to its
#                  finisher, whose pointer it holds in a pool before a tail branch.
#                  For an implicit axis the element type follows from the limit, so declaring
#                  it here would create a second source for one fact;
#   axistype_x/_y - r5 and r6 axis-array element types (explicit only). Each axis can differ:
#                  an entry searches them independently. 0x262E0 uses byte core 0x26A0C
#                  for r5 and word core 0x26984 for r6; 0x26660 does the same with
#                  0x26BC4/0x26B84. The call delay-slot clamp establishes the element:
#                  (points - 1) * element size. A 16-point byte axis therefore clamps at 15,
#                  while a word axis clamps at 30. The same clamp confirms point count.
# A census absent from the registry has an unknown axis model. An entry with tables absent
# from the registry is a wrapper with unknown geometry. Either condition stops loading
# instead of receiving a guessed annotation.
#
# Both access models have the same structure: a slot pointing to a shared engine, a
# specialized entry, and jsr from an accessor. They therefore share a census and a bank
# primitive appears as a wrapper in the graph. Operand interpretation differs: r5/r6 are
# axis pointers for explicit axes, while arithmetic defines an implicit axis and no :Axis
# node exists.
#
# Run after load_graph.py. :Func nodes belong to that ROM layer; reloading it recreates ROM
# nodes and removes their :ACCESSES relationships. This loader creates an accessor absent
# from :Func and reports the count. A nonzero count means the graph was built before
# RecoverFuncs.java definitions (Stage 0) and must be re-exported.
#
# What becomes a fact and what does not:
#   - map bases (r4) and axes (r5/r6) become nodes only when their values point into ROM.
#     A runtime input (current RAM axis value, index, mask) is neither a base nor an axis.
#     Its recovered value remains on the :ACCESSES relationship in r4/r5/r6 without
#     creating a node.
#   - only df supplies the base. Linear backtrack (bt) remains the section 6 gate baseline
#     but contributes no facts. It is wrong in all ten base conflicts in the JK08A catalog:
#     it recovers an axis instead of a base (at 0x732a8 the delay slot `mov r7,r4` sets the
#     base while earlier code holds an axis pointer), loses delay-slot arithmetic
#     (`add 0x8,r4` at five bank sites), or chooses an arbitrary member of a selector set.
#   - map geometry is entry geometry because an entry specializes in table shape rather than
#     taking it as a parameter. Axis convention: r5 -> :AXIS_X and r6 -> :AXIS_Y. The
#     source register remains on the relationship (reg), allowing Stage 4 to refine
#     orientation without losing the fact. Only 2D entries read an axis from r6. A ROM
#     value also appears in r6 at 15 of 240 1D sites, but r6 is not an argument there; the
#     fallback recovered a register value at the site address. The report counts discarded
#     values.
#   - operand kind (pool | slice | const | copy | sp | gbrrel | dyn) is stored on :ACCESSES and in
#     map resolver_kinds. kind=sp means the decompiler did not reduce the base to one value
#     and the fallback recovered it. Branching defines r4 there, so the recovered base is
#     one member of a set (0x64344 selects six tables by r5; 0xbe39a selects two by r13).
#     All such sites feed Stage 6, where branching becomes :Flag {role:'selector'}.
#   - an axis named only by fallback evidence (k5/k6=sp at every site) has pattern rather
#     than candidate confidence. Fallback is a linear heuristic and fails on axes just as on
#     bases. Direct proof: site 0x735ac identifies 0x8000 as an axis, but it contains erased
#     flash (all 0xFFFF). A reduced site (any kind except sp) promotes the axis to candidate.
#     Stage 6 processes the full set of branching axes together with bases.
# The census layer has candidate confidence (section 5): the resolver supplied operands but
# did not trace semantics. Only a trace can promote it, through the manual layer.
#
# Invocation: uv run python tools/memgraph/load_maps.py \
#           <export_dir> <rom_label> [<registry.csv>] [<findings.csv>] [<axes.csv>]
# Defaults: export_dir = ~/tools/ghidra-projects/export-JK08A-exact, rom = JK08A.
# defs/rom-inheritance.toml resolves structural and manual-layer paths.
import csv
import glob
import os
import re
import sys
from neo4j import GraphDatabase

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mapkit import rom as romkit          # noqa: E402 - adjacent package is not installed
import rom_sources  # noqa: E402

BOLT = "bolt://localhost:7687"

# ROM bounds: interrupt vectors lie below ROM_LO, while small values recovered from r6/r7
# are runtime scalars (index or mask), not bases. ROM_HI is the image size.
ROM_LO = 0x1000
ROM_HI = 0x180000

FAMILIES = ("explicit", "implicit")           # access models understood by the census
ROLES = ("table", "threshold", "dead")        # base role in calibration
LEVELS = ("pattern", "candidate", "code", "silicon")   # section 5 confidence ladder
AXIS_KINDS = ("rpm", "load", "temp", "raw")   # axis semantics and Stage 5 match key
FINDING_FIELDS = [
    "addr", "family", "width", "height", "storagetype", "accessor",
    "confidence", "evidence", "role", "semantics", "units", "scale_expr",
    "to_byte", "scale_conf", "scale_evidence", "note",
]
AXIS_FIELDS = [
    "addr", "kind", "units", "scale_expr", "to_byte", "scale_conf",
    "scale_evidence", "note",
]

# Scaling-expression vocabulary: constants, x, and arithmetic. Nothing broader is needed
# because RomRaider evaluates the same expression; anything not reducible to it is not map
# scaling.
SCALE_CHARS = re.compile(r"^[0-9x+\-*/(). ]+$")

def scale_roundtrip(expr, to_byte):
    """Return an expression-pair mismatch, or None when the pair round-trips.

    The inverse expression is declared rather than derived: the loader has no symbolic
    algebra and must not guess the inverse of 1881.6/x. It does validate the pair
    numerically. Substitution x -> scale_expr -> to_byte must return x, catching a mismatch
    exactly when one expression is edited without the other.
    """
    for v in (1, 7, 64, 100, 255):
        try:
            y = eval(expr, {"__builtins__": {}}, {"x": v})
            back = eval(to_byte, {"__builtins__": {}}, {"x": y})
        except ZeroDivisionError:
            continue
        if abs(back - v) > 1e-6 * max(1.0, abs(v)):
            return f"x={v}: {expr} = {y}, inverse {to_byte} = {back}"
    return None


def check_scale(path, who, r, conf_col):
    """Validate scaling units, forward and inverse expressions, and claim confidence.

    Identity (x) asserts no units. It is an intentional absence of a claim rather than a
    candidate-level fact and therefore has no confidence. Conversely, nonempty scaling
    without confidence would present a multiplier as given.
    """
    units, expr, tb, conf = r["units"], r["scale_expr"], r["to_byte"], r[conf_col]
    if not expr:
        extra = [c for c in ("units", "to_byte", conf_col) if r[c]]
        if extra:
            sys.exit(f"{path}: {who} - {', '.join(extra)} without scale_expr")
        return
    if not (units and tb):
        sys.exit(f"{path}: {who} - scaling lacks units or an inverse expression")
    for e in (expr, tb):
        if not SCALE_CHARS.match(e):
            sys.exit(f"{path}: {who} - expression {e!r} is outside the scaling vocabulary")
    bad = scale_roundtrip(expr, tb)
    if bad:
        sys.exit(f"{path}: {who} - to_byte is not the inverse of scale_expr ({bad})")
    if expr.strip() == "x":
        if conf:
            sys.exit(f"{path}: {who} - identity x asserts no units and cannot have confidence")
    elif conf not in LEVELS:
        sys.exit(f"{path}: {who} - scaling confidence {conf!r} is outside the section 5 ladder")


def read_registry(path):
    """Read the interpolation-entry registry, one entry with its geometry per row."""
    if not os.path.exists(path):
        sys.exit(f"interpolation-entry registry not found: {path}")
    with open(path, newline="") as f:
        reg = list(csv.DictReader(f))
    seen = set()
    for e in reg:
        w = e["wrapper"] or "?"
        if e["family"] not in FAMILIES:
            sys.exit(f"{path}: entry {w} declares family {e['family']!r}")
        if not (e["kernel"] and e["wrapper"] and e["width"]):
            sys.exit(f"{path}: entry {w} lacks a core, address, or point count")
        if e["wrapper"] in seen:
            sys.exit(f"{path}: entry {w} is declared twice")
        seen.add(e["wrapper"])
        if e["family"] == "implicit":
            if not e["step"]:
                sys.exit(f"{path}: implicit entry {w} lacks an axis step")
            if e["height"]:
                sys.exit(f"{path}: implicit entry {w}: a bank primitive has one dimension")
            if e["storagetype"]:
                sys.exit(f"{path}: implicit entry {w}: its limit determines element type")
            if e["axistype_x"] or e["axistype_y"]:
                sys.exit(f"{path}: implicit entry {w}: no axis array or axis element exists")
        else:
            if e["step"]:
                sys.exit(f"{path}: explicit entry {w}: an array axis has no step")
            if not e["storagetype"]:
                sys.exit(f"{path}: explicit entry {w} lacks an element type: a 1D entry "
                         f"reads it directly and a 2D entry uses its finisher")
            if not e["axistype_x"]:
                sys.exit(f"{path}: explicit entry {w} lacks an r5 axis element type")
            # Exactly 2D entries have an r6 axis; 1D code has no second search.
            if bool(e["axistype_y"]) != bool(e["height"]):
                state = ("declared without a second axis" if e["axistype_y"]
                         else "not declared for the second axis")
                sys.exit(f"{path}: explicit entry {w}: r6 axis element is {state}")
    return reg


def census_path(outdir, kernel):
    """Return a census filename; the resolver writes the core without leading zeroes."""
    return os.path.join(outdir, "accessors.%x.csv" % int(kernel, 16))


def read_censuses(outdir, reg, registry):
    """Read declared-core censuses; each row carries its entry geometry.

    An entry appears in the census of every core whose slot it holds. 0x26474 holds both
    kernel 0x26944 and finisher 0x26740, so the same 47 sites appear in both censuses.
    Look up each row by (core, entry) in the registry; counting only by entry address would
    count them twice.
    """
    declared = {(e["kernel"], e["wrapper"]): e for e in reg}
    known = {e["wrapper"] for e in reg}
    rows, taken, seen, unknown = [], set(), set(), {}
    for kernel in dict.fromkeys(e["kernel"] for e in reg):
        p = census_path(outdir, kernel)
        if not os.path.exists(p):
            sys.exit(f"core {kernel} is declared but census {os.path.basename(p)} is absent")
        taken.add(os.path.realpath(p))
        with open(p, newline="") as f:
            for r in csv.DictReader(f):
                e = declared.get((kernel, r["wrapper"]))
                if e is None:
                    # An entry that reads no tables is an internal interpolation node rather
                    # than a wrapper. Core 0x26740 has five: 2D finisher 0x26770 and four
                    # internal entries. An entry with a ROM base is a wrapper and its geometry
                    # must be declared.
                    if r["wrapper"] not in known and rom_addr(r["df_r4"]):
                        unknown.setdefault(r["wrapper"], kernel)
                    continue
                for c in ("family", "width", "height", "step", "storagetype",
                          "axistype_x", "axistype_y"):
                    r[c] = e[c]
                rows.append(r)
                seen.add((kernel, r["wrapper"]))
    if unknown:
        sys.exit("census found tables through an undeclared entry: "
                 + ", ".join(f"{w} (core {k})" for w, k in sorted(unknown.items()))
                 + f" - geometry is unknown; declare it in {os.path.basename(registry)}")
    idle = sorted(set(declared) - seen)
    if idle:
        sys.exit("entry is declared but has no sites: "
                 + ", ".join(f"{w} (core {k})" for k, w in idle))
    extra = sorted(os.path.basename(p)
                   for p in glob.glob(os.path.join(outdir, "accessors.*.csv"))
                   if os.path.realpath(p) not in taken)
    if extra:
        sys.exit(f"censuses outside the registry: {', '.join(extra)} - axis model is unknown; "
                 f"declare entries in {os.path.basename(registry)}")
    return rows, taken


def rom_addr(v):
    """Return a ROM address for a map base or axis, or None when the value cannot be a base."""
    if not v:
        return None
    return v if ROM_LO <= int(v, 16) < ROM_HI else None


def geometry(e):
    """Return entry geometry from the registry.

    Implicit axis: the axis is arithmetic, with points 0..(width-1) at step increments and
    the final point as its limit. The limit determines element type: chain merge 0x26a94
    applies SHLR8 R0; TST R0,R0 to the limit, and limit >= 256 selects the word branch.
    Both branches end with EXTU, making values unsigned. The code has no separate width flag.

    Explicit axis: the axis is a breakpoint array with no step. Entry code supplies point
    count through the delay-slot clamp. A 1D entry reads its element itself (MOV.B/MOV.W
    before the tail branch); a 2D entry uses a finisher from its pool. All five 2D finishers
    read both interpolation operands as unsigned (EXTU.B or EXTU.W).
    """
    w = int(e["width"])
    h = int(e["height"]) if e["height"] else None
    g = {"dims": 2 if h else 1, "width": w, "height": h, "step": None, "limit": None,
         "storagetype": e["storagetype"] or None}
    if e["family"] == "implicit":
        g["step"] = int(e["step"])
        g["limit"] = (w - 1) * g["step"]
        g["storagetype"] = "uint16" if g["limit"] >= 256 else "uint8"
    return g


def check_dims(rows, declared):
    """Cross-check registry dimensions against the independent r6-axis signal.

    The signal separates JK08A explicit-axis entries by majority rather than perfectly:
    86 of 87 2D sites carry an axis in r6, while 15 of 240 1D sites do. The largest 1D
    share is one of seven sites at 0x26550. Therefore compare majorities: an isolated ROM
    value in r6 for a 1D entry is not an argument.
    """
    total, with_y = {}, {}
    for r in rows:
        if r["family"] != "explicit":
            continue
        w = r["wrapper"]
        total[w] = total.get(w, 0) + 1
        if rom_addr(r["df_r6"]):
            with_y[w] = with_y.get(w, 0) + 1
    bad = [f"{w}: registry {declared[w]}D, sites {2 if with_y.get(w, 0) * 2 > n else 1}D "
           f"({with_y.get(w, 0)} of {n} with an axis in r6)"
           for w, n in sorted(total.items())
           if (2 if with_y.get(w, 0) * 2 > n else 1) != declared[w]]
    if bad:
        sys.exit("entry dimensions differ from its sites: " + "; ".join(bad))


def build(rows):
    """Convert resolver censuses into calibration-layer nodes and relationships."""
    maps, axes, interps, accesses = {}, {}, {}, []
    kernels = {}                                  # entry -> core (:KERNEL relationship)
    dropped = 0                                   # r6 values at 1D entries are not axes

    for r in rows:
        kern, w, family = r["kernel"], r["wrapper"], r["family"]
        g = geometry(r)

        # A fused entry is its own core: one node carries the geometry and no :KERNEL
        # relationship exists.
        if kern != w:
            interps.setdefault(kern, {"addr": kern, "role": "kernel", "family": None,
                                      "slot": "", "dims": None, "width": None,
                                      "height": None, "step": None, "limit": None,
                                      "storagetype": None})
        interps.setdefault(w, dict(g, addr=w, role="fused" if kern == w else "wrapper",
                                   family=family, slot=r["slot"]))
        kernels[w] = kern

        # An axis is an object only in the explicit-axis model. A bank axis is arithmetic,
        # and recovered r5/r6 values there are residual register values rather than call
        # arguments.
        explicit = family == "explicit"
        ax = rom_addr(r["df_r5"]) if explicit else None
        ay = rom_addr(r["df_r6"]) if explicit and g["dims"] == 2 else None
        if explicit and g["dims"] == 1 and rom_addr(r["df_r6"]):
            dropped += 1

        base = rom_addr(r["df_r4"])
        if not base:
            continue
        # Create an axis only for a map. At a site without a base (kind=dyn), a recovered
        # pointer is an axis of an unknown object; a node without a relationship would be
        # the axis of no table. The value is retained in the census and returns with its base
        # in Stage 6. Axis length and element are not intrinsic facts: the entry clamp gives
        # point count and core code gives element type. Conflicting readers of one axis stop
        # loading here, like other geometry conflicts.
        for a, n, k, el in ((ax, g["width"], r["k5"], r["axistype_x"]),
                            (ay, g["height"], r["k6"], r["axistype_y"])):
            if a:
                x = axes.setdefault(a, {"addr": a, "confidence": "pattern", "kind": "",
                                        "units": "", "scale_expr": "", "to_byte": "",
                                        "scale_conf": "", "scale_evidence": "", "note": "",
                                        "len": n, "storagetype": el})
                if x["storagetype"] != el:
                    sys.exit(f"axis {a} is read by entries with different elements: "
                             f"{x['storagetype']} and {el}")
                if x["len"] != n:
                    sys.exit(f"axis {a} is read by entries with different lengths: {x['len']} and {n}")
                if k != "sp":
                    x["confidence"] = "candidate"
        m = maps.setdefault(base, dict(g, addr=base, family=family,
                                       confidence="candidate", resolver_kinds=[],
                                       evidence="", scale_evidence="",
                                       role="table", semantics="", note="",
                                       units="", scale_expr="", to_byte="",
                                       scale_conf=""))
        # A table read by both axis models or by entries of different shapes is a finding,
        # not normal variation: two incompatible mechanisms define its geometry.
        if m["family"] != family:
            sys.exit(f"table {base} is addressed by families {m['family']} and {family}")
        if (m["width"], m["height"], m["storagetype"], m["step"]) != (
                g["width"], g["height"], g["storagetype"], g["step"]):
            sys.exit(f"table {base} is read by entries with different geometry: "
                     f"{m['width']}x{m['height']}/{m['storagetype']}/step {m['step']} and "
                     f"{g['width']}x{g['height']}/{g['storagetype']}/step {g['step']}")
        if r["k4"] not in m["resolver_kinds"]:
            m["resolver_kinds"].append(r["k4"])
        accesses.append({"accessor": r["accessor"], "callsite": r["callsite"],
                         "base": base, "wrapper": w, "kernel": kern, "family": family,
                         "kind": r["k4"], "kind5": r["k5"], "kind6": r["k6"],
                         "verdict": r["verdict"], "r4": r["df_r4"],
                         "r5": r["df_r5"], "r6": r["df_r6"],
                         "axis_x": ax or "", "axis_y": ay or ""})

    for m in maps.values():
        m["resolver_kinds"] = sorted(m["resolver_kinds"])
    return maps, axes, interps, kernels, accesses, dropped


def apply_findings(path, maps, accesses, source_model=None):
    """Apply the manual layer: facts established by a person that the census cannot supply.

    A row with a nonempty family declares a map outside the access models. No declared
    entry reads it, so the resolver does not find it (0x8fdc is a direct word comparator
    without a lookup; 0x9eda and 0xa8ea are 2D through 0x26040 with both axes implicit).
    An empty family is a finding about a map found by the resolver.

    The direct-row-major family represents direct access to a rectangular map whose X
    dimension is inner in the array: width corresponds to sizex and height to sizey. The
    definition's presentation layer supplies static labels for both axes because this access
    has no :AXIS_X/:AXIS_Y relationships.

    The file contains only what the graph cannot state. A census-derived map's wrapper,
    geometry, axes, and accessor are graph facts; repeating them in a finding would create
    a second source for one fact. A trace raises confidence here: the census supplies the
    whole candidate layer and only analysis can promote it.

    Scaling (units/scale_expr/to_byte) belongs here for the same reason: a call operand says
    where a table is, not how engine arithmetic transforms its byte. Scaling has independent
    confidence. Code establishes the address and shape of 0xB61A, while the x-64 multiplier
    comes from the A2L catalog; map confidence does not cover it.
    """
    if not os.path.exists(path):
        sys.exit(f"manual layer not found: {path}")
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != FINDING_FIELDS:
            sys.exit(f"{path}: header {reader.fieldnames}; expected {FINDING_FIELDS}")
        rows = list(reader)
    if source_model is not None:
        rows = rom_sources.materialize_rows(source_model, "Map", rows)
    declared = 0
    for r in rows:
        a, fam = r["addr"], r["family"]
        if r["confidence"] not in LEVELS:
            sys.exit(f"{path}: {a} - confidence {r['confidence']!r} is outside the section 5 ladder")
        if r["role"] not in ROLES:
            sys.exit(f"{path}: {a} - role {r['role']!r} is outside vocabulary {ROLES}")
        check_scale(path, a, r, "scale_conf")
        if fam:
            if fam in FAMILIES:
                sys.exit(f"{path}: {a} declares family {fam!r}, which is an access model; "
                         f"its maps come from the census rather than findings")
            if a in maps:
                sys.exit(f"{path}: {a} is declared manually but the resolver found it through "
                         f"{maps[a]['family']}; remove the stale declaration row")
            if not (r["width"] and r["storagetype"]):
                sys.exit(f"{path}: {a} is declared without a point count or element type; "
                         f"its row cannot read the map from the image")
            declared += 1
            maps[a] = {"addr": a, "family": fam, "resolver_kinds": ["manual"],
                       "dims": 2 if r["height"] else 1,
                       "width": int(r["width"]) if r["width"] else None,
                       "height": int(r["height"]) if r["height"] else None,
                       "storagetype": r["storagetype"] or None,
                       "step": None, "limit": None}
            maps[a].update(units="", scale_expr="", to_byte="", scale_conf="",
                           evidence="", scale_evidence="")
            if r["accessor"]:
                accesses.append({"accessor": r["accessor"], "callsite": "", "base": a,
                                 "wrapper": "", "kernel": "", "family": fam,
                                 "kind": "manual", "kind5": "manual", "kind6": "manual",
                                 "verdict": "", "r4": "", "r5": "", "r6": "",
                                 "axis_x": "", "axis_y": ""})
        elif a not in maps:
            sys.exit(f"{path}: finding refers to map {a}, which is absent from the graph; "
                     f"either the address is wrong or the row outlived its map")
        else:
            dup = [c for c in ("width", "height", "storagetype", "accessor") if r[c]]
            if dup:
                sys.exit(f"{path}: {a} - the census supplies {', '.join(dup)}; "
                         f"a finding must not override this field")
        maps[a].update(confidence=r["confidence"], evidence=r["evidence"],
                       role=r["role"], semantics=r["semantics"], note=r["note"],
                       units=r["units"], scale_expr=r["scale_expr"],
                       to_byte=r["to_byte"], scale_conf=r["scale_conf"],
                       scale_evidence=r["scale_evidence"])
    return len(rows), declared


def apply_axis_facts(path, axes, source_model=None):
    """Apply the manual axis layer: axis semantics and units.

    The census supplies the axis object through an r5/r6 pointer, and the core supplies its
    element type. Neither says what the axis represents or how it is measured; a consumer
    trace does. This requires a separate file rather than map-layer columns because several
    maps share an axis (all three ignition maps use 0x11B6B). Declaring it per map would
    duplicate one fact across rows.
    """
    if not os.path.exists(path):
        sys.exit(f"axis layer not found: {path}")
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames != AXIS_FIELDS:
            sys.exit(f"{path}: header {reader.fieldnames}; expected {AXIS_FIELDS}")
        rows = list(reader)
    if source_model is not None:
        rows = rom_sources.materialize_rows(source_model, "Axis", rows)
    seen = set()
    for r in rows:
        a = r["addr"]
        if a in seen:
            sys.exit(f"{path}: axis {a} is declared twice")
        seen.add(a)
        if a not in axes:
            sys.exit(f"{path}: finding refers to axis {a}, which is absent from the graph; "
                     f"either the address is wrong or the row outlived its axis")
        if r["kind"] not in AXIS_KINDS:
            sys.exit(f"{path}: axis {a} - kind {r['kind']!r} is outside vocabulary {AXIS_KINDS}")
        check_scale(path, f"axis {a}", r, "scale_conf")
        axes[a].update(kind=r["kind"], units=r["units"], scale_expr=r["scale_expr"],
                       to_byte=r["to_byte"], scale_conf=r["scale_conf"],
                       scale_evidence=r["scale_evidence"], note=r["note"])
    return len(rows)


def characterize(img, maps, axes):
    """Stage 4: measure what the image itself says about the layer.

    Run this in the same pass that creates nodes for the same reason as the manual layer:
    a measurement lives on the same node as its census fact and would disappear when the
    node is recreated. No second source exists here because the image is the source; the
    census only says which address and shape to read.

    An axis stores all its points because it is short and those points define it. Shared axes
    converge by list comparison, and an RPM progression is visible in the graph without
    reading the image. A map stores its range and hash: putting 256 cells on a node would
    duplicate image contents in the graph, while a hash identifies identical maps.

    A read miss stops loading. A map absent from the image is not a map but a wrong address
    or shape, leaving nothing to measure. The census bounds bases to 0x1000..0x180000,
    the largest family dump rather than this image; only the image knows its actual bound.
    """
    for a, m in sorted(maps.items()):
        try:
            rows = img.table(a, m["width"], m["height"], m["storagetype"])
        except ValueError as e:
            sys.exit(f"map {a} ({m['width']}x{m['height']} {m['storagetype']}): {e}")
        m.update(romkit.measure([v for r in rows for v in r]))
    for a, x in sorted(axes.items()):
        try:
            vals = img.values(a, x["len"], x["storagetype"])
        except ValueError as e:
            sys.exit(f"axis {a} ({x['len']} x {x['storagetype']}): {e}")
        x.update(values=vals, monotonic=romkit.monotone(vals))


def report(rows, maps, axes, interps, kernels, accesses, dropped, taken, findings, naxes):
    nfind, nmanual = findings
    d2 = sum(1 for i in interps.values() if i["dims"] == 2)
    callsites = {row["callsite"] for row in rows}
    projected = {
        (row["accessor"], row["callsite"], row["base"])
        for row in accesses
    }
    print(f"censuses: {', '.join(sorted(os.path.basename(p) for p in taken))}")
    print(f"CSV: {len(rows)} rows for {len(callsites)} call sites, "
          f"{len(set(kernels.values()))} cores, {len(kernels)} entries")
    print(f"Layer: {len(maps)} maps, {len(axes)} axes, {len(interps)} interpolation nodes "
          f"({d2} 2D entries), {len(accesses)} access rows / "
          f"{len(projected)} unique")
    if dropped:
        print(f"  r6 at 1D entries not treated as an axis: {dropped} values (not a call argument)")

    # Census disjointness: a table shared by two access families is a finding rather than
    # normal variation. The table at the end of the report gives map counts per entry.
    per_table, per_family = {}, {}
    for a in accesses:
        if a["kernel"]:
            per_table.setdefault(a["base"], set()).add(a["kernel"])
    for m in maps.values():
        per_family.setdefault(m["family"], set()).add(m["addr"])
    for f in sorted(per_family):
        print(f"  family {f}: {len(per_family[f])} maps")
    shared = {b: ks for b, ks in per_table.items() if len(ks) > 1}
    for b, ks in sorted(shared.items()):
        print(f"  WARNING: table {b} is addressed by censuses {sorted(ks)}")
    if not shared:
        print(f"  table censuses are disjoint ({len(per_table)} bases)")

    print(f"  manual layer: {nfind} findings, of which {nmanual} declare a map outside "
          f"access models; {naxes} axes annotated")
    scaled = sum(1 for m in maps.values() if m["scale_expr"])
    named = sum(1 for m in maps.values() if m["semantics"])
    both = sum(1 for m in maps.values() if m["semantics"] and m["scale_expr"])
    print(f"  interpretable (semantics + scaling): {both} maps; semantics on {named}, "
          f"scaling on {scaled}")
    lvl = {}
    for m in maps.values():
        lvl[m["confidence"]] = lvl.get(m["confidence"], 0) + 1
    print("  confidence levels: " + ", ".join(f"{k}={lvl[k]}" for k in LEVELS if k in lvl))
    role = {}
    for m in maps.values():
        role[m["role"]] = role.get(m["role"], 0) + 1
    print("  roles: " + ", ".join(f"{k}={role[k]}" for k in ROLES if k in role))

    # Sites where an operand did not reduce to one value: fallback recovered one path or no
    # value. These feed Stage 6 because branching selects the operand.
    sel = [a for a in accesses if a["kind"] == "sp"]
    sel_projected = {
        (a["accessor"], a["callsite"], a["base"])
        for a in sel
    }
    print(f"  base not reduced by the decompiler (kind=sp): {len(sel)} rows / "
          f"{len(sel_projected)} unique accesses - Stage 6 input")
    axsel = [a for a in accesses if "sp" in (a["kind5"], a["kind6"])]
    axsel_sites = {a["callsite"] for a in axsel}
    weak = [x for x in axes.values() if x["confidence"] == "pattern"]
    print(f"  axis not reduced by the decompiler (kind5/kind6=sp): "
          f"{len(axsel)} accesses at {len(axsel_sites)} call sites; "
          f"{len(weak)} axes rely only on fallback evidence (pattern confidence) - same input")

    # Stage 4 captures what the image itself says about the layer. Deduplication includes
    # both contents and shape: identical bytes with different shapes are different tables.
    print(f"  measured from the image: {len(maps)} maps, {len(axes)} axes")
    seen_ax = {tuple(x["values"]) for x in axes.values()}
    seen_m = {(m["values_hash"], m["width"], m["height"], m["storagetype"])
              for m in maps.values()}
    print(f"    distinct by contents: {len(seen_ax)} axes of {len(axes)} "
          f"(several maps sharing an axis is normal), {len(seen_m)} maps of {len(maps)}")

    # Increasing order is a core requirement rather than a semantic guess. A reverse linear
    # scan from the highest point reads only an increasing array; a nonincreasing array
    # cannot work as an axis.
    bad = sorted(x["addr"] for x in axes.values() if not x["monotonic"])
    if bad:
        print(f"    WARNING: array is not increasing and the core cannot read it with reverse linear search: "
              f"{', '.join(bad)}")
    blank_ax = [x["addr"] for x in axes.values()
                if romkit.erased(x["values"], x["storagetype"])]
    blank_m = [m["addr"] for m in maps.values()
               if m["vmin"] == m["vmax"] == romkit.ERASED[m["storagetype"]]]
    if blank_ax or blank_m:
        print(f"    all 0xFF (unprogrammed flash or saturated limit; a trace distinguishes them): "
              f"{len(blank_ax)} axes, {len(blank_m)} maps")


def main():
    rom = sys.argv[2] if len(sys.argv) > 2 else "JK08A"
    default_dir = str(rom_sources.default_export_dir(rom))
    outdir = sys.argv[1] if len(sys.argv) > 1 else default_dir
    try:
        source_model = rom_sources.resolve(rom)
        rom_sources.verify_image_binding(source_model)
    except ValueError as error:
        sys.exit(str(error))
    source_paths = rom_sources.definition_paths(source_model)
    registry = (
        sys.argv[3] if len(sys.argv) > 3 else str(source_paths["Interp"])
    )
    findings = (
        sys.argv[4] if len(sys.argv) > 4 else str(source_paths["Map"])
    )
    axfile = (
        sys.argv[5] if len(sys.argv) > 5 else str(source_paths["Axis"])
    )

    reg = read_registry(registry)
    rows, taken = read_censuses(outdir, reg, registry)
    check_dims(rows, {e["wrapper"]: 2 if e["height"] else 1 for e in reg})
    maps, axes, interps, kernels, accesses, dropped = build(rows)
    found = apply_findings(findings, maps, accesses, source_model)
    naxes = apply_axis_facts(axfile, axes, source_model)
    try:
        img = romkit.load(rom)
    except ValueError as e:
        sys.exit(str(e))
    characterize(img, maps, axes)
    print(f"rom={rom}; registry: {os.path.relpath(registry)} ({len(reg)} entries); "
          f"manual layer: {os.path.relpath(findings)}, {os.path.relpath(axfile)}")
    print(
        f"annotation source={source_model.source}, mode={source_model.kind}"
    )
    print(f"image: {os.path.relpath(img.path)} ({len(img)} B, SHA-256 verified)")
    report(rows, maps, axes, interps, kernels, accesses, dropped, taken, found, naxes)

    driver = GraphDatabase.driver(BOLT, auth=("", ""))
    with driver.session() as s:
        for lbl in ("Map", "Axis", "Interp"):
            s.run(f"MATCH (n:{lbl} {{rom:$rom}}) DETACH DELETE n", rom=rom)
            for prop in ("addr", "rom"):
                try:
                    s.run(f"CREATE INDEX ON :{lbl}({prop})")
                except Exception:
                    pass

        # An accessor without a :Func node indicates a graph built before Stage 0 definitions.
        orphan = s.run(
            """
            UNWIND $addrs AS a
            OPTIONAL MATCH (f:Func {rom:$rom, addr:a})
            WITH a, f WHERE f IS NULL
            RETURN count(DISTINCT a) AS n
            """,
            addrs=sorted({x["accessor"] for x in accesses}),
            rom=rom,
        ).single()["n"]

        s.run(
            """
            UNWIND $rows AS r
            MERGE (i:Interp {rom:$rom, addr:r.addr})
            SET i.role = r.role, i.family = r.family, i.slot = r.slot, i.dims = r.dims,
                i.width = r.width, i.height = r.height, i.step = r.step,
                i.limit = r.limit, i.storagetype = r.storagetype,
                i.annotation_source = $source_rom
            """,
            rows=list(interps.values()),
            rom=rom,
            source_rom=source_model.source,
        )
        s.run(
            """
            UNWIND $rows AS r
            MERGE (m:Map {rom:$rom, addr:r.addr})
            SET m.dims = toInteger(r.dims), m.family = r.family, m.width = r.width,
                m.height = r.height, m.storagetype = r.storagetype,
                m.confidence = r.confidence, m.resolver_kinds = r.resolver_kinds,
                m.evidence = r.evidence, m.scale_evidence = r.scale_evidence,
                m.role = r.role,
                m.semantics = r.semantics, m.note = r.note, m.units = r.units,
                m.scale_expr = r.scale_expr, m.to_byte = r.to_byte,
                m.scale_conf = r.scale_conf, m.vmin = r.vmin, m.vmax = r.vmax,
                m.values_hash = r.values_hash,
                m.annotation_source = $source_rom
            """,
            rows=list(maps.values()),
            rom=rom,
            source_rom=source_model.source,
        )
        s.run(
            """
            UNWIND $rows AS r
            MERGE (x:Axis {rom:$rom, addr:r.addr})
            SET x.confidence = r.confidence, x.storagetype = r.storagetype,
                x.len = r.len, x.kind = r.kind, x.units = r.units,
                x.scale_expr = r.scale_expr, x.to_byte = r.to_byte,
                x.scale_conf = r.scale_conf, x.scale_evidence = r.scale_evidence,
                x.note = r.note, x.values = r.values,
                x.monotonic = r.monotonic,
                x.annotation_source = $source_rom
            """,
            rows=list(axes.values()),
            rom=rom,
            source_rom=source_model.source,
        )
        s.run(
            """
            UNWIND $rows AS r
            MATCH (w:Interp {rom:$rom, addr:r.wrapper}), (k:Interp {rom:$rom, addr:r.kernel})
            MERGE (w)-[:KERNEL]->(k)
            """,
            rows=[{"wrapper": w, "kernel": k} for w, k in sorted(kernels.items()) if w != k],
            rom=rom,
        )
        s.run(
            """
            UNWIND $rows AS r
            MERGE (a:Func {rom:$rom, addr:r.accessor})
            WITH a, r
            MATCH (m:Map {rom:$rom, addr:r.base})
            MERGE (a)-[x:ACCESSES {callsite:r.callsite, base:r.base}]->(m)
            SET x.r4 = r.r4, x.r5 = r.r5, x.r6 = r.r6, x.kind = r.kind,
                x.kind5 = r.kind5, x.kind6 = r.kind6, x.verdict = r.verdict
            """,
            rows=accesses,
            rom=rom,
        )
        s.run(
            """
            UNWIND $rows AS r
            MATCH (m:Map {rom:$rom, addr:r.base}), (w:Interp {rom:$rom, addr:r.wrapper})
            MERGE (m)-[:VIA]->(w)
            """,
            rows=[r for r in accesses if r["wrapper"]],
            rom=rom,
        )
        for reg_name, edge, key in (("r5", "AXIS_X", "axis_x"), ("r6", "AXIS_Y", "axis_y")):
            s.run(
                f"""
                UNWIND $rows AS r
                MATCH (m:Map {{rom:$rom, addr:r.base}}), (x:Axis {{rom:$rom, addr:r.{key}}})
                MERGE (m)-[e:{edge}]->(x)
                SET e.reg = '{reg_name}'
                """,
                rows=[r for r in accesses if r[key]],
                rom=rom,
            )

        counts = s.run(
            """
            MATCH (m:Map {rom:$rom}) WITH count(m) AS maps
            MATCH (x:Axis {rom:$rom}) WITH maps, count(x) AS axes
            MATCH (:Func {rom:$rom})-[a:ACCESSES]->(:Map {rom:$rom})
            WITH maps, axes, count(a) AS acc
            MATCH (:Map {rom:$rom})-[v:VIA]->(:Interp {rom:$rom})
            RETURN maps, axes, acc, count(v) AS via
            """,
            rom=rom,
        ).single()
        print(f"Memgraph: {counts['maps']} :Map, {counts['axes']} :Axis, "
              f"{counts['acc']} :ACCESSES, {counts['via']} :VIA")
        if orphan:
            print(f"WARNING: {orphan} accessors are absent from :Func - the graph predates "
                  f"Stage 0 definitions; re-export with RecoverFuncs.java + ExportGraph.java")

        print("Maps by interpolation entry (Stage 2 catalog):")
        rows_out = s.run(
            """
            MATCH (m:Map {rom:$rom})-[:VIA]->(w:Interp {rom:$rom})
            RETURN w.addr AS wrapper, w.family AS family, w.width AS width,
                   w.height AS height, count(DISTINCT m) AS maps
            ORDER BY family, maps DESC
            """,
            rom=rom,
        )
        for r in rows_out:
            shape = f"{r['width']}x{r['height']}" if r["height"] else f"1D-{r['width']}"
            print(f"  {r['family']:<8} entry {r['wrapper']}  {shape:<7}  "
                  f"maps {r['maps']:>3}")

    driver.close()


if __name__ == "__main__":
    main()
