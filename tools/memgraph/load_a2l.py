#!/usr/bin/env python3
# Load the A2L catalog described in tools/map-analysis-pipeline.md into
# Memgraph. :A2LEntry nodes are the ROM-independent reference for the HR family.
#
# Source: refs/nissan-definitions/Pytrex-NissanDefinitions/Nissan Definitions/A2L.xml, the base
# RomRaider definition containing names, categories, geometry, scaling, and descriptions.
# It has no addresses; ROM definitions inheriting this base provide them. The rule that
# addresses do not transfer (JDM 2.5L layout != USDM 3.5L layout) is therefore structural:
# nothing can be transferred because the catalog defines classes rather than placement.
#
# RomRaider notation trap: type="2D" means a table with ONE axis, "3D" means two axes,
# and "1D" means a scalar without axes. In the graph, dims is the number of axes
# (:Map, load_maps.py), so normalize the notation: 2D -> dims=1, 3D -> dims=2,
# 1D -> dims=0. Without normalization, a join on dims would treat "2D" as two and silently
# match every entry to the wrong map class.
#
# shape uses the annotation-ledger vocabulary (defs/JK08A.maps.csv, dim column):
# 3D 16x16 -> "16x16", 2D sizex=8 -> "1D-8". A wrapper determines map geometry
# unambiguously (all 36 ledger wrappers have uniform dimensions), so the shared vocabulary
# makes future matching a direct string join rather than a comparison of two notations.
#
# This loader does not create :MATCHES relationships. Section 7 match keys are
# (dims, scale family, axis semantics). On the :Map side only dims exists at this point;
# scale_expr and axis semantics appear in Stage 4 (geometry and axis interpretation).
# Matching only on dims would connect all 37 "3D" entries to every dims=2 map, producing
# noise rather than a clue and exactly the failure P6 prevents ("pattern != semantics").
# The loader places the reference in the graph; Stage 5 creates relationships after Stage 4.
#
# Switch bits remain a list on the entry node. The catalog's unit of identity is a switch
# (one byte/dword at one address), while a bit is a field within it. Stage 6 owns
# :Flag {addr,bit} granularity; splitting catalog entries by bit before its matching model
# exists would be premature.
#
# The concept column is a curated identity annotation and a join key to the vendor catalog
# (:VendorEntry, refs/vendor/catalog.csv). Entries sharing a value describe one entity.
# All three vocabularies name it differently (`K-Value` versus `BFS Multiplier (K-Factor)`
# versus `K - Fuel Multiplier`), so an exact name join would fail entirely while fuzzy name
# matching would merge different entities. An empty concept means "link not established",
# not "no link exists".
#
# A link is based on entry description and geometry compared with vendor prose, not name
# similarity. Rejection precedent: by name, A2L 'MAF Voltage Lower Limit' matches EcuTek
# 'MAF Voltage Min Allowed', but their descriptions conflict. A2L says the threshold raises
# P0102, while EcuTek says no DTC is set. Therefore no link is assigned; see the analysis in
# refs/vendor/facts.csv.
#
# The vendor catalog defines the concept vocabulary. A value absent there joins to nothing
# and silently leaves dead annotation, so validate both vocabulary and names before loading.
#
# Annotate only maps and scalars. Stage 6 handles flags (Options//Flags, DTC, Supmask) under
# its own model: vendors represent them as bits within a switch rather than maps.
#
# Invocation: uv run python tools/memgraph/load_a2l.py [a2l_xml] [family]
# Defaults: xml = refs/nissan-definitions/.../A2L.xml, family = HR.
import csv
import os
import re
import sys
import xml.etree.ElementTree as ET



ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

DEFAULT_XML = os.path.join(
    ROOT,
    "refs",
    "nissan-definitions",
    "Pytrex-NissanDefinitions",
    "Nissan Definitions",
    "A2L.xml",
)

CATALOG = os.path.join(ROOT, "refs", "vendor", "catalog.csv")

# RomRaider type -> (kind, dims). dims is the axis count, not the notation label.
KIND = {
    "3D": ("map", 2),
    "2D": ("map", 1),
    "1D": ("scalar", 0),
    "BitwiseSwitch": ("switch", 0),
}

# "Axis RPM (x*50)" -> ("RPM", "x*50"); "- (x)" -> ("-", "x").
SCALE_RE = re.compile(r"^\s*(.*?)\s*\(([^)]*)\)\s*$")

# --- concept: exact A2L name -> vendor-catalog entity ---
# Catalog granularity defines a concept as a calibration family rather than one table.
# `vvel-duration` has seven ProECU entries (Cold, Main, Overrun, WOT...), while
# `idle-ignition` has nine. Variants of one function (Cold/High Detonation/High Octane,
# Trustful) therefore share a concept.
A2L_CONCEPT = {
    # MAF -> BFS -> load path. A2L descriptions state the relationship directly:
    # 'MAF Factor' is "what Nissan uses to scale MAF from factory",
    # 'Load Base Fuel Schedule Table' is "The 100% BFS value... used to calculate
    # Calculated Load", and 'Cylinder Filling Up Efficiency Scaler' is
    # "BFS at which maximum airflow occurs".
    'MAF Table': 'maf-curve',
    'MAF Factor': 'maf-gps-scalar',
    'K-Value': 'bfs-multiplier',
    'Load Base Fuel Schedule Table': 'load-100pct',
    'Cylinder Filling Up Efficiency Scaler': 'load-point-scaler',
    # AFR target. EcuTek retains the stock 8x8 map, and both A2L geometries belong together.
    'Target AFR Map (16x16)': 'fuel-target',
    'Target AFR Map (8x8)': 'fuel-target',
    'Target AFR Table (High Detonation)': 'fuel-target',
    # Fuel corrections. 'Fuel Compensation Map' axes QH0 Flow Quantity x Engine Speed match
    # what UpRev calls Volumetric Flow Ratio x RPM for 'Fuel Compensation Main'; both adjust
    # BFS. The KHOT pair is high-temperature enrichment, also called
    # 'Fuel Enrichment - Hot' by EcuTek.
    'Fuel Compensation Map (16x16)': 'fuel-comp',
    'High Coolant Temperature Increase Compensation Table': 'fuel-comp',
    'High Temperature Fuel Compensation Map': 'fuel-comp',
    'Individual Cylinder Fuel Trims': 'cylinder-trim',
    # Injectors. The latency pair directly implements UpRev y = m * X + B:
    # 'at 14V' supplies B and 'Adder' supplies the slope.
    'Fuel Injector Latency at 14V': 'injector-latency',
    'Fuel Injector Latency Adder': 'injector-latency',
    'Minimum Injector Pulse Width': 'injector-minimum',
    # Cranking: the axis is coolant temperature and the value is pulse width (BFS in ms),
    # matching UpRev 'Cranking Enrichment Initial Value'.
    'Cranking Base Fuel Schedule Table': 'cranking-initial',
    # Deceleration cut rather than a rev limiter: "fuel cut will occur (on decel) until the
    # RPM's hit the recover speed". Two sets exist for ECU lines (Bosch and JECS/Hitachi),
    # matching exactly four EcuTek maps: Overrun Fuel Cut #1, #1 Restore, #2, and #2 Restore.
    'Bosch Fuel Cut Table': 'overrun-fuel-cut',
    'Bosch Fuel Restore Table': 'overrun-fuel-cut',
    'JECS Fuel Cut Table': 'overrun-fuel-cut',
    'JECS Fuel Restore Table': 'overrun-fuel-cut',
    # Rev and speed limiters. One A2L 2x2 map contains both cut and restore
    # (Fuel axis = Cut/Restore), while EcuTek displays them as two maps. Assign the concept
    # from the entry name; facts.csv contains the axis analysis.
    'Rev Limit (Fuel Cut - 3D)': 'rev-limit-fuel',
    'Throttle Rev Limiter': 'rev-limit-throttle',
    'Speed Limiter': 'speed-limit',
    'Speed Limiter (Fuel Cut)': 'speed-limit',
    'Speed Limiter (Fuel Restore)': 'speed-limit',
    # Ignition: three correction maps for calculated MBT ("this trimming map value is added/
    # subtracted from that value") match the three UpRev tables (Main, High Det, Cold).
    # The ECU has no base timing table because a formula calculates MBT.
    'Cold Ignition Timing Map (16x16)': 'ignition-trim',
    'High Detonation Ignition Timing Map (16x16)': 'ignition-trim',
    'High Octane Ignition Timing Map (16x16)': 'ignition-trim',
    # Knock windows pair one-to-one with correction maps, as EcuTek has five
    # 'Knock Control Enable A1' maps matching the five 'Mode A1 Adj' variants.
    'Cold Ignition Timing Map Knock Window': 'knock-enable',
    'High Detonation Ignition Timing Map Knock Window': 'knock-enable',
    'High Octane Ignition Timing Map Knock Window': 'knock-enable',
    # Knock thresholds: 16x6 with cylinder number on the Y axis. EcuTek describes the same
    # map and notes elevated thresholds for middle cylinders 3 and 4.
    'Knock Slice Map': 'knock-threshold',
    # Idle: timing at idle and overrun outside calculated MBT (GOV tables).
    'Idle Ignition Timing Table': 'idle-ignition',
    'Cold Idle Ignition Timing Table': 'idle-ignition',
    'Lean Burn Idle Ignition Timing Table': 'idle-ignition',
    # VTC is intake camshaft angle. The High Detonation map ("only used when knock is
    # detected") independently confirms the ETD suffix interpretation in the ProECU tree.
    # Exhaust Cam Timing is not annotated because the vendor catalog has no counterpart.
    'Intake Cam Timing Map (16x16)': 'vtc-advance',
    'Cold Intake Cam Timing Map (8x8)': 'vtc-advance',
    'High Detonation Intake Cam Timing Map (4x4)': 'vtc-advance',
    # Pedal -> requested flow -> requested torque -> throttle opening. The Lo/Hi pair plus
    # the pair of verification copies match the four EcuTek
    # 'Accel to Throttle Hi/Lo' (+Trustful) entries.
    'Throttle Flow Potential Table': 'accel-throttle',
    'Throttle Flow Potential Table (High Flow-Quantity)': 'accel-throttle',
    'Throttle Flow Potential Table Trustful': 'accel-throttle',
    'Throttle Flow Potential Table (High Flow-Quantity) Trustful': 'accel-throttle',
    'QH0/ Torque Conversion Map': 'torque-demand',
    'QH0/ Torque Conversion Map Trustful': 'torque-demand',
    # Torque for TCM line pressure, also UpRev 'Estimated Torque Delivered': the same torque
    # scale as the request map, with cylinder filling rather than BFS as the load axis.
    'Engine Torque Map': 'torque-actual',
}


def parse_scaling(el):
    """Return the unit (match scale family) and exact expression from the scaling base."""
    if el is None:
        return "", ""
    sc = el.find("scaling")
    if sc is None:
        return "", ""
    base = (sc.get("base") or "").strip()
    m = SCALE_RE.match(base)
    if not m:
        return base, ""
    unit, expr = m.group(1).strip(), m.group(2).strip()
    if unit.startswith("Axis "):
        unit = unit[5:]           # "Axis RPM" and "RPM" are one family: axis and value
    return unit, expr


def shape_of(kind, dims, sx, sy):
    """Express geometry in the annotation-ledger vocabulary: 16x16, 8x8, 1D-8, 1D-16."""
    if kind != "map":
        return ""
    if dims == 2:
        return f"{sx}x{sy}" if sx and sy else ""
    return f"1D-{sx}" if sx else ""


def axis_of(t, want):
    """Read a table axis; 'X Axis' and 'Static X Axis' share one role."""
    for a in t.findall("table"):
        typ = (a.get("type") or "").replace("Static ", "")
        if typ == want:
            return a
    return None


def build(path, family):
    root = ET.parse(path).getroot()
    entries, skipped = [], []
    for t in root.findall("table"):
        typ = t.get("type")
        if typ not in KIND:
            skipped.append(typ)
            continue
        kind, dims = KIND[typ]
        sx, sy = t.get("sizex"), t.get("sizey")
        unit, expr = parse_scaling(t)
        ax, ay = axis_of(t, "X Axis"), axis_of(t, "Y Axis")
        ax_unit, ax_expr = parse_scaling(ax)
        ay_unit, ay_expr = parse_scaling(ay)
        desc = t.find("description")
        bits = t.findall("bit")
        entries.append(
            {
                "family": family,
                "name": t.get("name") or "",
                "category": t.get("category") or "",
                "kind": kind,
                "dims": dims,
                "shape": shape_of(kind, dims, sx, sy),
                "width": int(sx) if sx and sx.isdigit() else None,
                "height": int(sy) if sy and sy.isdigit() else None,
                "storagetype": t.get("storagetype") or "",
                "unit": unit,
                "scale_expr": expr,
                "axis_x_sem": (ax.get("name") or "") if ax is not None else "",
                "axis_y_sem": (ay.get("name") or "") if ay is not None else "",
                "axis_x_scale": ax_expr,
                "axis_y_scale": ay_expr,
                "axis_x_unit": ax_unit,
                "axis_y_unit": ay_unit,
                "userlevel": int(t.get("userlevel")) if t.get("userlevel") else None,
                "bits": [f"{b.get('position')}={b.get('name')}" for b in bits],
                "description": "".join(desc.itertext()).strip() if desc is not None else "",
                "concept": A2L_CONCEPT.get(t.get("name") or "", ""),
            }
        )
    return entries, skipped


def vocabulary(catalog=CATALOG):
    """Return the concept vocabulary defined by the vendor catalog."""
    with open(catalog, newline="", encoding="utf-8") as f:
        return {r["concept"] for r in csv.DictReader(f) if r["concept"]}


def check(entries, catalog=CATALOG):
    """Reject dead annotations before loading because the graph cannot distinguish them from omissions."""
    stale = sorted(set(A2L_CONCEPT) - {e["name"] for e in entries})
    if stale:
        sys.exit(f"concept references names absent from A2L: {stale}")
    unknown = sorted(set(A2L_CONCEPT.values()) - vocabulary(catalog))
    if unknown:
        sys.exit(f"concepts are absent from the vendor catalog and would join to nothing: {unknown}")


def load(driver, path, family, catalog):
    """Load the pinned A2L source through the compiler's connection."""
    entries, skipped = build(path, family)
    check(entries, catalog)
    kinds = {}
    for e in entries:
        kinds[e["kind"]] = kinds.get(e["kind"], 0) + 1
    print(f"A2L: {len(entries)} entries from {os.path.basename(path)}; family={family}")
    print(
        f"Catalog: {kinds.get('map', 0)} maps ("
        f"{sum(1 for e in entries if e['dims'] == 2)} with two axes, "
        f"{sum(1 for e in entries if e['dims'] == 1)} with one), "
        f"{kinds.get('scalar', 0)} scalars, {kinds.get('switch', 0)} switches"
    )
    if skipped:
        print(f"  unparsed types: {sorted(set(skipped))}")

    # Name is the node key; a collision would silently merge two catalog entries.
    names = [e["name"] for e in entries]
    dup = sorted({n for n in names if names.count(n) > 1})
    if dup:
        print(f"WARNING: nonunique names ({len(dup)}): {dup[:5]}")

    with driver.session() as s:
        s.run("MATCH (n:A2LEntry {family:$f}) DETACH DELETE n", f=family)
        for prop in ("family", "name", "concept"):
            try:
                s.run(f"CREATE INDEX ON :A2LEntry({prop})")
            except Exception:
                pass

        s.run(
            """
            UNWIND $rows AS r
            MERGE (e:A2LEntry {family:r.family, name:r.name})
            SET e.category = r.category, e.kind = r.kind, e.dims = r.dims,
                e.shape = r.shape, e.width = r.width, e.height = r.height,
                e.storagetype = r.storagetype, e.unit = r.unit,
                e.scale_expr = r.scale_expr,
                e.axis_x_sem = r.axis_x_sem, e.axis_y_sem = r.axis_y_sem,
                e.axis_x_scale = r.axis_x_scale, e.axis_y_scale = r.axis_y_scale,
                e.axis_x_unit = r.axis_x_unit, e.axis_y_unit = r.axis_y_unit,
                e.userlevel = r.userlevel, e.bits = r.bits, e.description = r.description,
                e.concept = r.concept
            """,
            rows=entries,
            family=family,
        )
        n = s.run(
            "MATCH (e:A2LEntry {family:$f}) RETURN count(e) AS n", f=family
        ).single()["n"]
        print(f"Memgraph: {n} :A2LEntry")

        print("Catalog map geometry (annotation-ledger vocabulary):")
        for r in s.run(
            """
            MATCH (e:A2LEntry {family:$f, kind:'map'})
            RETURN e.shape AS shape, count(*) AS n ORDER BY n DESC, shape
            """,
            f=family,
        ):
            print(f"  {r['shape']:<8} {r['n']:>3}")

        print("Catalog flags (Stage 6 input):")
        for r in s.run(
            """
            MATCH (e:A2LEntry {family:$f, kind:'switch'})
            RETURN split(e.category,'//')[1] AS grp, count(*) AS n,
                   sum(size(e.bits)) AS bits ORDER BY n DESC
            """,
            f=family,
        ):
            print(f"  {r['grp']:<10} entries {r['n']:>3}, bits {r['bits']:>4}")

        # Three-vocabulary join: A2L supplies shape and path location; vendors supply meaning
        # and defaults.
        print("Three-vocabulary convergence (concept: A2L + ProECU + UpRev):")
        rows = list(
            s.run(
                """
                MATCH (a:A2LEntry {family:$f}) WHERE a.concept <> ''
                WITH a.concept AS c, count(a) AS a2l
                MATCH (v:VendorEntry {family:$f, origin:'factory', concept:c})
                WITH c, a2l, collect(DISTINCT v.vendor) AS vs, count(v) AS vend
                RETURN c, a2l, vend, vs ORDER BY c
                """,
                f=family,
            )
        )
        for r in rows:
            print(f"  {r['c']:<20} A2L {r['a2l']:>2} <-> vendors {r['vend']:>2} "
                  f"({', '.join(sorted(r['vs']))})")
        both = sum(1 for r in rows if len(r["vs"]) > 1)
        marked = sum(1 for e in entries if e["concept"])
        print(f"  total concepts: {len(rows)}; covered by both vendor vocabularies: {both}")
        print(f"  annotated A2L entries: {marked} of {len(entries)}")



def main():
    raise SystemExit("This layer belongs to the kb compiler; use `uv run kb sync`.")


if __name__ == "__main__":
    main()
