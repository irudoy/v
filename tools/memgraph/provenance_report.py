#!/usr/bin/env python3
"""Read-only audit of weakest links and reverse impact in Memgraph.

Invocation:
  uv run python tools/memgraph/provenance_report.py audit JK08A
  uv run python tools/memgraph/provenance_report.py \
      weakest JK08A Func 00021ce0 confidence
  uv run python tools/memgraph/provenance_report.py \
      impact JK08A Map 0001495a structural
"""
import argparse
import os
import sys

from neo4j import GraphDatabase

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import rom_sources  # noqa: E402
from load_code import (  # noqa: E402
    AXIS_FIELDS,
    FUNC_FIELDS,
    MAP_FIELDS,
    SOURCE_COLUMNS,
    VAR_FIELDS,
    actual_projection,
    check_func_contracts,
    check_source_claim_properties,
    read_rows,
    resolve_dependencies,
    source_claims,
)
from provenance import (  # noqa: E402
    STRUCTURAL,
    ClaimKey,
    ProvenanceError,
    StructuralKey,
    analyze_claims,
    compare_projection,
    dependency_path,
    reverse_impact,
)

BOLT = "bolt://localhost:7687"


def read_source_claims(rom):
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
    sources = {
        "Func": funcs,
        "Reg": vars_,
        "Map": maps,
        "Axis": axes,
    }
    claims = source_claims(rom, [
        (label, rows, paths[label]) for label, rows in sources.items()
    ])
    return model, claims, sources


def check_graph_source_model(session, model):
    row = session.run(
        """
        MATCH (r:Rom {id:$rom})
        RETURN r.annotation_source AS source,
               r.source_kind AS kind,
               r.source_evidence AS evidence,
               r.target_sha256 AS target_sha256,
               r.source_sha256 AS source_sha256,
               r.source_ranges AS source_ranges
        """,
        rom=model.target,
    ).single()
    expected = {
        "source": model.source,
        "kind": model.kind,
        "evidence": model.evidence,
        "target_sha256": model.target_sha256,
        "source_sha256": model.source_sha256,
        "source_ranges": list(model.ranges),
    }
    if row is None:
        raise ProvenanceError(
            f"Rom:{model.target} has no source model; run a complete ingest"
        )
    actual = {
        key: (
            list(row[key] or [])
            if key == "source_ranges" else
            (row[key] or "")
        )
        for key in expected
    }
    if actual != expected:
        raise ProvenanceError(
            f"Rom:{model.target} source model differs: "
            f"graph={actual}, registry={expected}"
        )
    edges = [
        {
            "source": item["source"],
            "kind": item["kind"] or "",
            "evidence": item["evidence"] or "",
            "target_sha256": item["target_sha256"] or "",
            "source_sha256": item["source_sha256"] or "",
            "source_ranges": list(item["source_ranges"] or []),
        }
        for item in session.run(
            """
            MATCH (:Rom {id:$rom})-[e:ANNOTATIONS_FROM]->(s:Rom)
            RETURN s.id AS source, e.kind AS kind, e.evidence AS evidence,
                   e.target_sha256 AS target_sha256,
                   e.source_sha256 AS source_sha256,
                   e.ranges AS source_ranges
            """,
            rom=model.target,
        )
    ]
    expected_edges = (
        [{
            "source": model.source,
            "kind": model.kind,
            "evidence": model.evidence,
            "target_sha256": model.target_sha256,
            "source_sha256": model.source_sha256,
            "source_ranges": list(model.ranges),
        }]
        if model.inherited else
        []
    )
    if edges != expected_edges:
        raise ProvenanceError(
            f"Rom:{model.target} ANNOTATIONS_FROM differs: "
            f"graph={edges}, registry={expected_edges}"
        )


def load_claim_graph(session, rom):
    model, claims, sources = read_source_claims(rom)
    check_graph_source_model(session, model)
    for label, rows in sources.items():
        check_source_claim_properties(session, rom, label, rows)
    dependencies, gaps, levels, grounded = resolve_dependencies(
        session, rom, claims
    )
    expected = [dep.projection_key() for dep in dependencies]
    projection = compare_projection(expected, actual_projection(session, rom))
    return model, levels, dependencies, grounded, gaps, projection


def projection_count(counter):
    return sum(counter.values())


def print_projection(projection, gaps):
    print(
        "RESTS_ON projection: "
        f"missing={projection_count(projection.missing)}, "
        f"extra={projection_count(projection.extra)}, "
        f"duplicate_expected={projection_count(projection.duplicate_expected)}, "
        f"duplicate_actual={projection_count(projection.duplicate_actual)}, "
        f"unresolved={len(gaps)}"
    )
    for title, counter in (
        ("missing", projection.missing),
        ("extra", projection.extra),
        ("duplicate_expected", projection.duplicate_expected),
        ("duplicate_actual", projection.duplicate_actual),
    ):
        for key, count in sorted(counter.items())[:10]:
            print(f"  {title} x{count}: {key}")
    for gap in gaps[:10]:
        print(f"  unresolved: {gap}")


def audit(levels, dependencies, grounded, gaps, projection, strict=False):
    analysis = analyze_claims(levels, dependencies, grounded)
    code = {
        claim for claim, level in levels.items()
        if level in ("code", "silicon")
    }
    below = {
        claim: analysis.effective[claim]
        for claim in code
        if analysis.effective[claim] != levels[claim]
    }
    ungrounded = sorted(claim for claim in code if not analysis.grounded[claim])
    print_projection(projection, gaps)
    print(f"claims={len(levels)}, RESTS_ON expected={len(dependencies)}, "
          f"cyclic_SCC={len(analysis.cyclic_components)}")
    print(f"code/silicon below declared={len(below)}, without grounding={len(ungrounded)}, "
          f"ungrounded cycles={len(analysis.ungrounded_cycles)}")
    for claim in sorted(below)[:20]:
        weak = analysis.weakest[claim]
        print(f"  {claim.short()}: {levels[claim]} -> {below[claim]} "
              f"through {weak.short()}")
    for claim in ungrounded[:20]:
        print(f"  without grounding: {claim.short()} [{levels[claim]}]")
    projection_bad = not projection.clean or bool(gaps)
    confidence_bad = bool(below or ungrounded)
    return 1 if projection_bad or (strict and confidence_bad) else 0


def require_current_projection(projection, gaps):
    if projection.clean and not gaps:
        return
    raise ProvenanceError(
        "RESTS_ON projection does not match CSV; run a complete ingest first"
    )


def weakest(levels, dependencies, grounded, rom, label, addr, prop):
    claim = ClaimKey(rom, label, addr, prop)
    if claim not in levels:
        raise ProvenanceError(f"claim {claim.short()} not found")
    analysis = analyze_claims(levels, dependencies, grounded)
    weak = analysis.weakest[claim]
    path = dependency_path(claim, weak, dependencies)
    print(f"{claim.short()}: declared={levels[claim]}, "
          f"effective={analysis.effective[claim]}, grounded={analysis.grounded[claim]}")
    print("weakest: " + weak.short())
    print("path: " + " -> ".join(item.short() for item in path))
    return 0


def impact(dependencies, rom, label, addr, prop):
    changed = (StructuralKey(rom, label, addr) if prop == STRUCTURAL
               else ClaimKey(rom, label, addr, prop))
    affected = reverse_impact(changed, dependencies)
    print(f"change to {changed.short()}: {len(affected) - 1} dependent claims")
    for claim, depth in sorted(affected.items(), key=lambda item: (item[1], item[0])):
        if claim == changed:
            continue
        print(f"  depth={depth} {claim.short()}")
    return 0


def parser():
    out = argparse.ArgumentParser(description=__doc__)
    sub = out.add_subparsers(dest="command", required=True)
    audit_parser = sub.add_parser("audit")
    audit_parser.add_argument("rom")
    audit_parser.add_argument("--strict", action="store_true")
    for name in ("weakest", "impact"):
        command = sub.add_parser(name)
        command.add_argument("rom")
        command.add_argument("label", choices=SOURCE_COLUMNS)
        command.add_argument("addr")
        command.add_argument("prop")
    return out


def main():
    args = parser().parse_args()
    driver = GraphDatabase.driver(BOLT, auth=("", ""))
    try:
        with driver.session() as session:
            graph = load_claim_graph(session, args.rom)
        model, levels, dependencies, grounded, gaps, projection = graph
        print(
            f"annotation source={model.source}, mode={model.kind}, "
            f"value image={model.target}"
        )
        if args.command == "audit":
            return audit(
                levels, dependencies, grounded, gaps, projection, args.strict
            )
        require_current_projection(projection, gaps)
        if args.command == "weakest":
            return weakest(
                levels, dependencies, grounded,
                args.rom, args.label, args.addr, args.prop,
            )
        return impact(
            dependencies, args.rom, args.label, args.addr, args.prop
        )
    except ProvenanceError as error:
        sys.exit(str(error))
    finally:
        driver.close()


if __name__ == "__main__":
    sys.exit(main())
