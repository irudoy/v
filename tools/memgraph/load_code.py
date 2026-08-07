#!/usr/bin/env python3
# Code-understanding layer and claim provenance. The contract is in
# tools/map-analysis-pipeline.md; defs/rom-inheritance.toml resolves canonical sources.
# Canonical JK08A holds the only live funcs/vars/findings/axes set; exact-code ROMs inherit
# it. Memgraph nodes and :RESTS_ON relationships are projections and are rebuilt completely.
#
# This loader must run after load_graph.py, load_xrefs.py, and load_maps.py. Each owns its
# nodes and recreates them with DETACH DELETE.
#
# Invocation: uv run python tools/memgraph/load_code.py [rom]
# Default ROM: JK08A.
import csv
import os
import sys
from collections import Counter

from neo4j import GraphDatabase

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from load_xrefs import classify  # noqa: E402
import rom_sources  # noqa: E402
from provenance import (  # noqa: E402
    ADDR_RE,
    CATALOG_ROLES,
    EDGE_ROLES,
    LEVELS,
    STRUCTURAL,
    ClaimKey,
    Dependency,
    ProvenanceError,
    analyze_claims,
    compare_projection,
    parse_evidence,
    target_property_allowed,
)

BOLT = "bolt://localhost:7687"

FUNC_ROLES = {
    "", "accessor", "consumer", "monitor", "driver", "init", "kernel",
    "wrapper", "finisher", "service", "dispatch", "handler", "selector",
}

FUNC_FIELDS = [
    "addr", "role", "semantics", "contract", "contract_conf",
    "contract_evidence", "confidence", "evidence", "note",
]
VAR_FIELDS = ["addr", "semantics", "units", "confidence", "evidence", "note"]
MAP_FIELDS = [
    "addr", "family", "width", "height", "storagetype", "accessor",
    "confidence", "evidence", "role", "semantics", "units", "scale_expr",
    "to_byte", "scale_conf", "scale_evidence", "note",
]
AXIS_FIELDS = [
    "addr", "kind", "units", "scale_expr", "to_byte", "scale_conf",
    "scale_evidence", "note",
]

# Every evidence column belongs to exactly one ranked claim.
SOURCE_COLUMNS = {
    "Func": (("confidence", "evidence", True),
             ("contract_conf", "contract_evidence", True)),
    "Reg": (("confidence", "evidence", True),),
    "Map": (("confidence", "evidence", True),
            ("scale_conf", "scale_evidence", True)),
    "Axis": (("scale_conf", "scale_evidence", True),),
}


class LoadError(ProvenanceError):
    pass


def read_rows(path, expected):
    if not os.path.exists(path):
        raise LoadError(f"git source not found: {path}")
    with open(path, newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames != expected:
            raise LoadError(
                f"{path}: header {reader.fieldnames}; expected {expected}"
            )
        rows = []
        for line_number, row in enumerate(reader, 2):
            if None in row:
                raise LoadError(
                    f"{path}:{line_number}: row has extra columns {row[None]!r}"
                )
            missing = [field for field, value in row.items() if value is None]
            if missing:
                raise LoadError(
                    f"{path}:{line_number}: row is missing columns {missing}"
                )
            rows.append(row)
        return rows


def check_unique(rows, path):
    counts = Counter(r["addr"] for r in rows)
    bad_addr = sorted(a for a in counts if not ADDR_RE.match(a))
    if bad_addr:
        raise LoadError(f"{path}: addr is not eight lowercase hexadecimal digits: {bad_addr[:5]}")
    dup = sorted(a for a, n in counts.items() if n > 1)
    if dup:
        raise LoadError(f"{path}: nonunique addr values, {len(dup)}: {dup[:5]}")


def source_claims(rom, sources):
    """Build claims and evidence tokens and apply local gates before accessing the graph."""
    claims = []
    for label, rows, path in sources:
        check_unique(rows, path)
        for row in rows:
            if label == "Func" and row["role"] not in FUNC_ROLES:
                raise LoadError(
                    f"{path}:{row['addr']}: role {row['role']!r} is outside {sorted(FUNC_ROLES)}"
                )
            for prop, evidence_col, strict in SOURCE_COLUMNS[label]:
                level = row[prop]
                evidence = row[evidence_col]
                if level and level not in LEVELS:
                    raise LoadError(
                        f"{path}:{row['addr']}.{prop}: confidence {level!r} "
                        f"is outside {list(LEVELS)}"
                    )
                if evidence and not level:
                    raise LoadError(
                        f"{path}:{row['addr']}: {evidence_col} exists without {prop}"
                    )
                if not level:
                    continue
                claim = ClaimKey(rom, label, row["addr"], prop)
                tokens = parse_evidence(
                    evidence, prop, f"{path}:{row['addr']}.{evidence_col}"
                )
                if strict and level in ("code", "silicon"):
                    factual = [t for t in tokens if not t.is_process]
                    if not factual:
                        raise LoadError(
                            f"confidence gate: {claim.short()} {level} without evidence"
                        )
                claims.append({
                    "claim": claim,
                    "level": level,
                    "tokens": tokens,
                    "strict": strict,
                    "path": path,
                })
    return claims


def check_func_contracts(funcs, path):
    for row in funcs:
        contract = bool(row["contract"])
        level = bool(row["contract_conf"])
        evidence = bool(row["contract_evidence"])
        if contract != level:
            raise LoadError(
                f"{path}:{row['addr']}: contract and contract_conf must appear together"
            )
        if evidence and not contract:
            raise LoadError(
                f"{path}:{row['addr']}: contract_evidence exists without contract"
            )


def check_catalog_claim_levels(tx, rom, label, rows):
    """Verify that the Map/Axis owner already projected confidence levels from CSV."""
    props = [prop for prop, _, _ in SOURCE_COLUMNS[label]]
    returns = ", ".join(f"n.{prop} AS {prop}" for prop in props)
    graph = {
        row["addr"]: {prop: row[prop] or "" for prop in props}
        for row in tx.run(
            f"MATCH (n:{label} {{rom:$rom}}) WHERE n.addr IN $addrs "
            f"RETURN n.addr AS addr, {returns}",
            rom=rom, addrs=[row["addr"] for row in rows],
        )
    }
    missing = sorted(row["addr"] for row in rows if row["addr"] not in graph)
    mismatches = []
    for row in rows:
        if row["addr"] not in graph:
            continue
        for prop in props:
            if graph[row["addr"]][prop] != row[prop]:
                mismatches.append(
                    f"{label}:{row['addr']}.{prop} CSV={row[prop]!r}, "
                    f"graph={graph[row['addr']][prop]!r}"
                )
    if missing or mismatches:
        details = []
        if missing:
            details.append(f"missing nodes {missing[:10]}")
        details.extend(mismatches[:10])
        raise LoadError(
            "Map/Axis confidence levels were not projected by load_maps.py: "
            + "; ".join(details)
        )


def check_source_claim_properties(tx, rom, label, rows):
    """Compare claim-specific node properties with canonical CSV files."""
    columns = [
        column
        for prop, evidence, _ in SOURCE_COLUMNS[label]
        for column in (prop, evidence)
    ]
    returns = ", ".join(f"n.{column} AS {column}" for column in columns)
    graph = {
        row["addr"]: {column: row[column] or "" for column in columns}
        for row in tx.run(
            f"MATCH (n:{label} {{rom:$rom}}) WHERE n.addr IN $addrs "
            f"RETURN n.addr AS addr, {returns}",
            rom=rom, addrs=[row["addr"] for row in rows],
        )
    }
    missing = sorted(row["addr"] for row in rows if row["addr"] not in graph)
    mismatches = []
    for row in rows:
        current = graph.get(row["addr"])
        if current is None:
            continue
        for column in columns:
            expected = row[column] or ""
            if current[column] != expected:
                mismatches.append(
                    f"{label}:{row['addr']}.{column} CSV={expected!r}, "
                    f"graph={current[column]!r}"
                )
    if missing or mismatches:
        details = []
        if missing:
            details.append(f"missing nodes {missing[:10]}")
        details.extend(mismatches[:10])
        raise LoadError(
            "claim-specific properties do not match CSV: " + "; ".join(details)
        )


def ensure_sources(tx, rom, funcs, vars_, maps, axes):
    func_addrs = [r["addr"] for r in funcs]
    present = {
        r["addr"] for r in tx.run(
            "MATCH (n:Func {rom:$rom}) WHERE n.addr IN $addrs "
            "RETURN n.addr AS addr",
            rom=rom, addrs=func_addrs,
        )
    }
    missing = sorted(set(func_addrs) - present)
    if missing:
        raise LoadError(f"funcs.csv: {len(missing)} addresses do not resolve to :Func: {missing}")

    # Some manual Reg nodes use base+offset addressing and have no direct xref. vars.csv may
    # legitimately introduce such a Reg; an arbitrary evidence target without a vars row
    # still fails.
    var_rows = []
    for row in vars_:
        region, name = classify(int(row["addr"], 16))
        var_rows.append({**row, "region": region, "name": name})
    tx.run(
        """
        UNWIND $rows AS r
        MERGE (n:Reg {rom:$rom, addr:r.addr})
        ON CREATE SET n.region = r.region, n.name = r.name
        """,
        rom=rom, rows=var_rows,
    )

    for label, rows in (("Map", maps), ("Axis", axes)):
        addrs = [r["addr"] for r in rows]
        present = {
            r["addr"] for r in tx.run(
                f"MATCH (n:{label} {{rom:$rom}}) WHERE n.addr IN $addrs "
                "RETURN n.addr AS addr",
                rom=rom, addrs=addrs,
            )
        }
        missing = sorted(set(addrs) - present)
        if missing:
            raise LoadError(
                f"{label}: {len(missing)} manual-layer addresses do not resolve: {missing}"
            )
        check_catalog_claim_levels(tx, rom, label, rows)
    return var_rows


def project_properties(tx, rom, source_rom, funcs, vars_, maps, axes):
    # Removing stale annotations is mandatory: a row deleted from CSV must not survive in the graph.
    tx.run(
        "MATCH (n:Func {rom:$rom}) REMOVE n.role, n.semantics, n.contract, "
        "n.contract_conf, n.contract_evidence, n.confidence, n.evidence, "
        "n.annotation_source",
        rom=rom,
    )
    tx.run(
        "MATCH (n:Reg {rom:$rom}) REMOVE n.semantics, n.units, n.confidence, "
        "n.evidence, n.annotation_source",
        rom=rom,
    )
    tx.run(
        "MATCH (n:Map {rom:$rom}) REMOVE n.evidence, n.scale_evidence",
        rom=rom,
    )
    tx.run(
        "MATCH (n:Axis {rom:$rom}) REMOVE n.scale_evidence",
        rom=rom,
    )

    tx.run(
        """
        UNWIND $rows AS r
        MATCH (n:Func {rom:$rom, addr:r.addr})
        SET n.role = r.role, n.semantics = r.semantics,
            n.contract = r.contract, n.contract_conf = r.contract_conf,
            n.contract_evidence = r.contract_evidence,
            n.confidence = r.confidence, n.evidence = r.evidence,
            n.annotation_source = $source_rom
        """,
        rom=rom, source_rom=source_rom, rows=funcs,
    )
    tx.run(
        """
        UNWIND $rows AS r
        MATCH (n:Reg {rom:$rom, addr:r.addr})
        SET n.semantics = r.semantics, n.units = r.units,
            n.confidence = r.confidence, n.evidence = r.evidence,
            n.annotation_source = $source_rom
        """,
        rom=rom, source_rom=source_rom, rows=vars_,
    )
    tx.run(
        """
        UNWIND $rows AS r
        MATCH (n:Map {rom:$rom, addr:r.addr})
        SET n.evidence = r.evidence, n.scale_evidence = r.scale_evidence,
            n.annotation_source = $source_rom
        """,
        rom=rom, source_rom=source_rom, rows=maps,
    )
    tx.run(
        """
        UNWIND $rows AS r
        MATCH (n:Axis {rom:$rom, addr:r.addr})
        SET n.scale_evidence = r.scale_evidence,
            n.annotation_source = $source_rom
        """,
        rom=rom, source_rom=source_rom, rows=axes,
    )


def project_source_model(tx, model):
    """Record the annotation source as a verifiable ROM-level relationship."""
    tx.run(
        """
        MERGE (r:Rom {id:$target})
        SET r.annotation_source = $source,
            r.source_kind = $kind,
            r.source_evidence = $evidence,
            r.target_sha256 = $target_sha256,
            r.source_sha256 = $source_sha256,
            r.source_ranges = $source_ranges
        WITH r
        OPTIONAL MATCH (r)-[old:ANNOTATIONS_FROM]->(:Rom)
        DELETE old
        """,
        target=model.target,
        source=model.source,
        kind=model.kind,
        evidence=model.evidence,
        target_sha256=model.target_sha256,
        source_sha256=model.source_sha256,
        source_ranges=list(model.ranges),
    )
    if model.inherited:
        tx.run(
            """
            MATCH (r:Rom {id:$target})
            MERGE (s:Rom {id:$source})
            MERGE (r)-[e:ANNOTATIONS_FROM]->(s)
            SET e.kind = $kind,
                e.evidence = $evidence,
                e.target_sha256 = $target_sha256,
                e.source_sha256 = $source_sha256,
                e.ranges = $source_ranges
            """,
            target=model.target,
            source=model.source,
            kind=model.kind,
            evidence=model.evidence,
            target_sha256=model.target_sha256,
            source_sha256=model.source_sha256,
            source_ranges=list(model.ranges),
        )


def node_inventory(tx, rom, wanted):
    labels = sorted({label for choices in EDGE_ROLES.values() for label in choices})
    props = {
        "Func": ("confidence", "contract_conf"),
        "Reg": ("confidence",),
        "Map": ("confidence", "scale_conf"),
        "Axis": ("confidence", "scale_conf"),
    }
    inventory = {}
    for label in labels:
        returns = ", ".join(f"n.{p} AS {p}" for p in props[label])
        rows = tx.run(
            f"MATCH (n:{label} {{rom:$rom}}) WHERE n.addr IN $addrs "
            f"RETURN n.addr AS addr, {returns}",
            rom=rom, addrs=wanted,
        )
        inventory[label] = {
            row["addr"]: {prop: row[prop] or "" for prop in props[label]}
            for row in rows
        }
    return inventory


def resolve_claim_dependencies(rom, claims, inventory):
    """Resolve evidence tokens against the completed node and confidence inventory."""
    dependencies = []
    gaps = []
    levels = {item["claim"]: item["level"] for item in claims}
    grounded = set()

    for item in claims:
        source = item["claim"]
        for token in item["tokens"]:
            if token.is_terminal:
                grounded.add(source)
                continue
            if not token.is_dependency:
                continue
            label = next(
                (candidate for candidate in EDGE_ROLES[token.role]
                 if token.target_addr in inventory[candidate]),
                None,
            )
            if label is None:
                miss = f"{source.short()} {token.role}:{token.value}@{token.target_prop}"
                if token.role in CATALOG_ROLES:
                    gaps.append(miss)
                    continue
                raise LoadError(f"unresolvable evidence: {miss}")
            if not target_property_allowed(label, token.target_prop):
                raise LoadError(
                    f"{source.short()}: {label}.{token.target_prop} does not exist"
                )
            if token.target_prop != STRUCTURAL:
                level = inventory[label][token.target_addr].get(token.target_prop, "")
                if level not in LEVELS:
                    raise LoadError(
                        f"{source.short()}: target {label}:{token.target_addr}."
                        f"{token.target_prop} has no confidence level"
                    )
                target = ClaimKey(rom, label, token.target_addr, token.target_prop)
                previous = levels.setdefault(target, level)
                if previous != level:
                    raise LoadError(
                        f"{target.short()}: source confidence {previous}; graph confidence {level}"
                    )
            dependencies.append(Dependency(
                source=source,
                role=token.role,
                target_label=label,
                target_addr=token.target_addr,
                target_prop=token.target_prop,
                ref=token.value,
            ))
    return dependencies, gaps, levels, grounded


def resolve_dependencies(tx, rom, claims):
    wanted = sorted({
        token.target_addr
        for item in claims
        for token in item["tokens"]
        if token.is_dependency
    })
    inventory = node_inventory(tx, rom, wanted)
    return resolve_claim_dependencies(rom, claims, inventory)


def require_no_gaps(gaps):
    if gaps:
        raise LoadError(f"catalog gaps in evidence: {len(gaps)}: {gaps[:10]}")


def project_edges(tx, rom, dependencies):
    for label in ("Func", "Reg", "Map", "Axis"):
        tx.run(
            f"MATCH (n:{label} {{rom:$rom}})-[e:RESTS_ON]->() DELETE e",
            rom=rom,
        )
    rows = [{
        "source": dep.source.addr,
        "source_prop": dep.source.prop,
        "role": dep.role,
        "target": dep.target_addr,
        "target_prop": dep.target_prop,
        "ref": dep.ref,
        "source_label": dep.source.label,
        "target_label": dep.target_label,
    } for dep in dependencies]
    for source_label in ("Func", "Reg", "Map", "Axis"):
        for target_label in ("Func", "Reg", "Map", "Axis"):
            part = [
                row for row in rows
                if row["source_label"] == source_label
                and row["target_label"] == target_label
            ]
            if not part:
                continue
            tx.run(
                f"""
                UNWIND $rows AS r
                MATCH (a:{source_label} {{rom:$rom, addr:r.source}})
                MATCH (b:{target_label} {{rom:$rom, addr:r.target}})
                MERGE (a)-[:RESTS_ON {{source_prop:r.source_prop, role:r.role,
                                      target_prop:r.target_prop, ref:r.ref}}]->(b)
                """,
                rom=rom, rows=part,
            )


def actual_projection(tx, rom):
    actual = []
    for source_label in ("Func", "Reg", "Map", "Axis"):
        for target_label in ("Func", "Reg", "Map", "Axis"):
            rows = tx.run(
                f"""
                MATCH (a:{source_label} {{rom:$rom}})-[e:RESTS_ON]->
                      (b:{target_label} {{rom:$rom}})
                RETURN a.addr AS source, e.source_prop AS source_prop,
                       e.role AS role, b.addr AS target,
                       e.target_prop AS target_prop, e.ref AS ref
                """,
                rom=rom,
            )
            actual.extend((
                source_label,
                row["source"],
                row["source_prop"] or "",
                row["role"] or "",
                target_label,
                row["target"],
                row["target_prop"] or "",
                row["ref"] or "",
            ) for row in rows)
    return actual


def exact_audit(tx, rom, dependencies):
    expected = [dep.projection_key() for dep in dependencies]
    actual = actual_projection(tx, rom)
    diff = compare_projection(expected, actual)
    if not diff.clean:
        def sample(counter):
            return list(counter.items())[:10]
        raise LoadError(
            "RESTS_ON projection differs from its source: "
            f"missing={sample(diff.missing)}, extra={sample(diff.extra)}, "
            f"duplicate_expected={sample(diff.duplicate_expected)}, "
            f"duplicate_actual={sample(diff.duplicate_actual)}"
        )
    return len(expected)


def report_analysis(claims, dependencies, levels, grounded, gaps):
    analysis = analyze_claims(levels, dependencies, grounded)
    declared_code = {
        claim: level for claim, level in levels.items()
        if level in ("code", "silicon")
    }
    below = {
        claim: effective
        for claim, effective in analysis.below_declared(levels).items()
        if claim in declared_code
    }
    ungrounded = [
        claim for claim in declared_code if not analysis.grounded[claim]
    ]
    source_keys = {item["claim"] for item in claims}
    report_only = {
        item["claim"] for item in claims if not item["strict"]
    }
    debt = sorted(
        claim for claim in report_only
        if claim in declared_code and not analysis.grounded[claim]
    )

    roles = Counter(dep.role for dep in dependencies)
    targets = Counter(dep.target_label for dep in dependencies)
    print(f"  :RESTS_ON: {len(dependencies)} "
          f"(targets: {', '.join(f'{k}={n}' for k, n in targets.most_common())})")
    print("  by role: " + ", ".join(f"{k}={n}" for k, n in roles.most_common()))
    print(f"  ranked claims: {len(levels)}; source claims: {len(source_keys)}; "
          f"cyclic SCCs: {len(analysis.cyclic_components)}")
    print(f"  effective below declared for code/silicon: {len(below)}; "
          f"without grounding: {len(ungrounded)}")
    print(f"  report-only debt for Map/Axis code without grounding: {len(debt)}")
    if gaps:
        print(f"  catalog gaps: {len(gaps)}")
    if below:
        print("  weakest links (first 10):")
        for claim in sorted(below)[:10]:
            weak = analysis.weakest[claim]
            print(f"    {claim.short()} {levels[claim]} -> {below[claim]} "
                  f"through {weak.short()}")
    if analysis.ungrounded_cycles:
        print(f"  ungrounded cycles: {len(analysis.ungrounded_cycles)}")
    return analysis


def main():
    rom = sys.argv[1] if len(sys.argv) > 1 else "JK08A"
    try:
        model = rom_sources.resolve(rom)
        rom_sources.verify_image_binding(model)
        paths = rom_sources.definition_paths(model)
        funcs = read_rows(paths["Func"], FUNC_FIELDS)
        vars_ = read_rows(paths["Reg"], VAR_FIELDS)
        maps = read_rows(paths["Map"], MAP_FIELDS)
        axes = read_rows(paths["Axis"], AXIS_FIELDS)
        funcs = rom_sources.materialize_rows(model, "Func", funcs)
        vars_ = rom_sources.materialize_rows(model, "Reg", vars_)
        maps = rom_sources.materialize_rows(model, "Map", maps)
        axes = rom_sources.materialize_rows(model, "Axis", axes)
        check_func_contracts(funcs, paths["Func"])
        claims = source_claims(rom, [
            ("Func", funcs, paths["Func"]),
            ("Reg", vars_, paths["Reg"]),
            ("Map", maps, paths["Map"]),
            ("Axis", axes, paths["Axis"]),
        ])
    except ProvenanceError as error:
        sys.exit(str(error))

    print(
        f"Provenance layer {rom}: annotation source={model.source}, "
        f"mode={model.kind}; {len(funcs)} functions, {len(vars_)} variables, "
        f"{len(maps)} map findings, {len(axes)} axis findings"
    )

    driver = GraphDatabase.driver(BOLT, auth=("", ""))
    try:
        with driver.session() as session:
            tx = session.begin_transaction()
            try:
                ensure_sources(tx, rom, funcs, vars_, maps, axes)
                project_properties(
                    tx, rom, model.source, funcs, vars_, maps, axes
                )
                for label, rows in (
                    ("Func", funcs), ("Reg", vars_),
                    ("Map", maps), ("Axis", axes),
                ):
                    check_source_claim_properties(tx, rom, label, rows)
                dependencies, gaps, levels, grounded = resolve_dependencies(
                    tx, rom, claims
                )
                require_no_gaps(gaps)
                project_edges(tx, rom, dependencies)
                exact_audit(tx, rom, dependencies)
                project_source_model(tx, model)
                report_analysis(claims, dependencies, levels, grounded, gaps)
                tx.commit()
            except Exception:
                tx.rollback()
                raise
    except ProvenanceError as error:
        sys.exit(str(error))
    finally:
        driver.close()


if __name__ == "__main__":
    main()
