#!/usr/bin/env python3
"""Project static firmware-to-diagnostic claims into Memgraph.

The CSV layer is target-ROM scoped and preserves three independent facts:

* confidence in the machine-code association;
* applicability of the external semantic source to the target ROM;
* inheritance scope across an explicitly verified exact-code ROM pair.

This loader owns only :DiagnosticBinding nodes and their outgoing relationships.
It must run after the global diagnostic corpus and after load_code.py.

Invocation:
  uv run python \
      tools/memgraph/load_diagnostic_bindings.py [rom]
"""

from __future__ import annotations

import csv
import os
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from neo4j import GraphDatabase

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import rom_sources  # noqa: E402
from provenance import (  # noqa: E402
    ADDR_RE,
    EDGE_ROLES,
    LEVEL_RANK,
    STRUCTURAL,
    evidence_machine_anchor,
    parse_evidence,
    target_property_allowed,
)


BOLT = "bolt://localhost:7687"

FIELDS = [
    "id",
    "kind",
    "firmware_label",
    "firmware_addr",
    "diagnostic_label",
    "diagnostic_key",
    "source_claim_label",
    "source_claim_id",
    "confidence",
    "applicability",
    "rom_scope",
    "priority",
    "evidence",
    "note",
]

ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
DTC_RE = re.compile(r"^[PBCU][0-9A-F]{4}$")

FIRMWARE_LABELS = frozenset({"Func", "Reg", "Map", "Axis"})
FIRMWARE_CONFIDENCE_PROP = {
    "Func": "confidence",
    "Reg": "confidence",
    "Map": "confidence",
    "Axis": "scale_conf",
}
STATIC_LEVELS = frozenset({"pattern", "candidate", "code"})
KINDS = frozenset({
    "runtime_value",
    "monitor",
    "monitor_calibration",
    "calibration_context",
})
APPLICABILITIES = frozenset({
    "exact_rom",
    "exact_code",
    "homologous_community",
    "homologous_vq35hr",
    "nissan_family_candidate",
})
ROM_SCOPES = frozenset({"exact-rom", "exact-code"})

# Canonical diagnostic node -> source-specific claim -> required relationship.
DIAGNOSTIC_SOURCES = {
    "DiagnosticParameter": {
        "key": "id",
        "claims": {"ParameterDefinition": "DEFINES"},
    },
    "DtcCode": {
        "key": "code",
        "claims": {
            "DtcDefinition": "DEFINES",
            "RomDtcDescriptor": "ENCODES",
        },
    },
    "CanSignal": {
        "key": "id",
        "claims": {
            "CanSignalDefinition": "DEFINES",
            "CanSignalBinding": "BINDS_SIGNAL",
        },
    },
}


class BindingError(ValueError):
    """A static binding source or graph projection violates its contract."""


def read_rows(path: str | Path) -> list[dict[str, str]]:
    path = Path(path)
    if not path.is_file():
        raise BindingError(f"diagnostic binding source not found: {path}")
    with path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != FIELDS:
            raise BindingError(
                f"{path}: header {reader.fieldnames}; expected {FIELDS}"
            )
        rows = list(reader)
    return rows


def _row_error(path: str | Path, number: int, message: str) -> BindingError:
    return BindingError(f"{path}:{number}: {message}")


def validate_rows(
    rows: Iterable[dict[str, str]], path: str | Path
) -> list[dict[str, Any]]:
    """Validate the complete CSV contract without accessing Memgraph."""
    validated: list[dict[str, Any]] = []
    ids: set[str] = set()
    for number, source in enumerate(rows, 2):
        if None in source or any(value is None for value in source.values()):
            raise _row_error(path, number, "field count does not match the header")
        row = {key: str(value).strip() for key, value in source.items()}
        identity = row["id"]
        if not ID_RE.fullmatch(identity):
            raise _row_error(path, number, f"invalid id {identity!r}")
        if identity in ids:
            raise _row_error(path, number, f"duplicate id {identity!r}")
        ids.add(identity)

        if row["kind"] not in KINDS:
            raise _row_error(
                path, number,
                f"kind {row['kind']!r} is outside {sorted(KINDS)}",
            )
        if row["firmware_label"] not in FIRMWARE_LABELS:
            raise _row_error(
                path, number,
                f"firmware_label {row['firmware_label']!r} is outside "
                f"{sorted(FIRMWARE_LABELS)}",
            )
        if not ADDR_RE.fullmatch(row["firmware_addr"]):
            raise _row_error(
                path, number,
                "firmware_addr is not eight lowercase hexadecimal digits",
            )

        diagnostic = DIAGNOSTIC_SOURCES.get(row["diagnostic_label"])
        if diagnostic is None:
            raise _row_error(
                path, number,
                f"diagnostic_label {row['diagnostic_label']!r} is outside "
                f"{sorted(DIAGNOSTIC_SOURCES)}",
            )
        if not row["diagnostic_key"]:
            raise _row_error(path, number, "diagnostic_key is empty")
        if (
            row["diagnostic_label"] == "DtcCode"
            and not DTC_RE.fullmatch(row["diagnostic_key"])
        ):
            raise _row_error(path, number, "diagnostic_key is not a canonical DTC")
        if row["source_claim_label"] not in diagnostic["claims"]:
            raise _row_error(
                path, number,
                f"{row['source_claim_label']!r} cannot support "
                f"{row['diagnostic_label']}",
            )
        if not row["source_claim_id"]:
            raise _row_error(path, number, "source_claim_id is empty")

        if row["confidence"] not in STATIC_LEVELS:
            raise _row_error(
                path, number,
                f"confidence {row['confidence']!r} is outside "
                f"{sorted(STATIC_LEVELS)}",
            )
        if row["applicability"] not in APPLICABILITIES:
            raise _row_error(
                path, number,
                f"applicability {row['applicability']!r} is outside "
                f"{sorted(APPLICABILITIES)}",
            )
        if row["rom_scope"] not in ROM_SCOPES:
            raise _row_error(
                path, number,
                f"rom_scope {row['rom_scope']!r} is outside "
                f"{sorted(ROM_SCOPES)}",
            )
        try:
            priority = int(row["priority"], 10)
        except ValueError as error:
            raise _row_error(path, number, "priority is not a decimal integer") from error
        if not 0 <= priority <= 100:
            raise _row_error(path, number, "priority is outside 0..100")

        context = f"{path}:{number}:{identity}.evidence"
        try:
            tokens = parse_evidence(row["evidence"], "confidence", context)
        except ValueError as error:
            raise _row_error(path, number, str(error)) from error
        if not tokens:
            raise _row_error(path, number, "evidence is empty")
        if not any(
            evidence_machine_anchor(token) for token in tokens
        ):
            raise _row_error(
                path, number,
                "a static binding requires at least one machine-address anchor",
            )

        validated.append({
            **row,
            "priority": priority,
            "tokens": tokens,
        })
    return validated


def materialize_rows(
    model: rom_sources.SourceModel, rows: Iterable[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Apply exact-code inheritance without projecting target-only ROM claims."""
    selected = [
        row for row in rows
        if not model.inherited or row["rom_scope"] == "exact-code"
    ]
    return rom_sources.materialize_rows(model, "DiagnosticBinding", selected)


def _single(tx: Any, query: str, **parameters: Any) -> dict[str, Any] | None:
    row = tx.run(query, **parameters).single()
    return row.data() if row is not None else None


def _firmware_node(
    tx: Any, rom: str, label: str, addr: str
) -> dict[str, Any] | None:
    return _single(
        tx,
        f"MATCH (n:{label} {{rom:$rom, addr:$addr}}) "
        "RETURN n.confidence AS confidence, "
        "n.contract_conf AS contract_conf, "
        "n.scale_conf AS scale_conf, "
        "n.semantics AS semantics, n.note AS note",
        rom=rom,
        addr=addr,
    )


def _diagnostic_source(
    tx: Any, row: dict[str, Any]
) -> dict[str, Any] | None:
    diagnostic = DIAGNOSTIC_SOURCES[row["diagnostic_label"]]
    relationship = diagnostic["claims"][row["source_claim_label"]]
    key = diagnostic["key"]
    return _single(
        tx,
        f"MATCH (s:{row['source_claim_label']} {{id:$claim_id}})"
        f"-[:{relationship}]->"
        f"(d:{row['diagnostic_label']} {{{key}:$diagnostic_key}}) "
        "RETURN coalesce(s.name, s.title, d.name, d.code, d.id) AS name, "
        "coalesce(s.applicability_status, '') AS source_applicability, "
        "coalesce(s.verification_status, '') AS source_verification, "
        "coalesce(s.dataset_id, '') AS source_dataset_id",
        claim_id=row["source_claim_id"],
        diagnostic_key=row["diagnostic_key"],
    )


def _resolve_token(
    tx: Any, rom: str, token: Any
) -> dict[str, Any]:
    for label in EDGE_ROLES[token.role]:
        node = _firmware_node(tx, rom, label, token.target_addr)
        if node is None:
            continue
        if not target_property_allowed(label, token.target_prop):
            raise BindingError(
                f"{label}.{token.target_prop} does not exist for "
                f"{token.role}:{token.value}"
            )
        level = (
            node.get(token.target_prop) or ""
            if token.target_prop != STRUCTURAL
            else ""
        )
        return {
            "label": label,
            "addr": token.target_addr,
            "target_prop": token.target_prop,
            "level": level,
            "role": token.role,
            "ref": token.value,
        }
    raise BindingError(
        f"unresolvable evidence token {token.role}:{token.value}"
    )


def resolve_rows(
    tx: Any, rom: str, rows: Iterable[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Resolve every target and evidence dependency before replacing bindings."""
    resolved = []
    for row in rows:
        firmware = _firmware_node(
            tx, rom, row["firmware_label"], row["firmware_addr"]
        )
        if firmware is None:
            raise BindingError(
                f"{row['id']}: firmware target "
                f"{row['firmware_label']}:{row['firmware_addr']} is absent"
            )
        firmware_prop = FIRMWARE_CONFIDENCE_PROP[row["firmware_label"]]
        firmware_level = firmware.get(firmware_prop) or ""
        if firmware_level not in LEVEL_RANK:
            raise BindingError(
                f"{row['id']}: firmware target has no {firmware_prop} level"
            )
        if LEVEL_RANK[firmware_level] < LEVEL_RANK[row["confidence"]]:
            raise BindingError(
                f"{row['id']}: binding confidence {row['confidence']} exceeds "
                f"firmware target confidence {firmware_level}"
            )

        source = _diagnostic_source(tx, row)
        if source is None:
            raise BindingError(
                f"{row['id']}: source claim {row['source_claim_label']}:"
                f"{row['source_claim_id']} does not support "
                f"{row['diagnostic_label']}:{row['diagnostic_key']}"
            )

        dependencies = [
            _resolve_token(tx, rom, token)
            for token in row["tokens"]
            if token.is_dependency
        ]
        weak = [
            dep for dep in dependencies
            if dep["target_prop"] != STRUCTURAL
            and dep["level"] in LEVEL_RANK
            and LEVEL_RANK[dep["level"]] < LEVEL_RANK[row["confidence"]]
        ]
        if weak:
            dep = weak[0]
            raise BindingError(
                f"{row['id']}: evidence {dep['label']}:{dep['addr']}."
                f"{dep['target_prop']}={dep['level']} is weaker than "
                f"{row['confidence']}"
            )

        resolved.append({
            **{key: value for key, value in row.items() if key != "tokens"},
            **source,
            "rom": rom,
            "graph_id": f"diagnostic-binding:{rom}:{row['id']}",
            "firmware_confidence_prop": firmware_prop,
            "firmware_confidence": firmware_level,
            "annotation_source": row.get("annotation_source", ""),
            "dependencies": dependencies,
        })
    return resolved


def chunks(
    rows: list[dict[str, Any]], size: int = 500
) -> Iterable[list[dict[str, Any]]]:
    for offset in range(0, len(rows), size):
        yield rows[offset : offset + size]


def create_indexes(session: Any) -> None:
    for prop in ("id", "rom"):
        try:
            session.run(f"CREATE INDEX ON :DiagnosticBinding({prop})").consume()
        except Exception as error:
            message = str(error).lower()
            if "already exists" not in message and "exists" not in message:
                raise


def write_projection(tx: Any, rom: str, rows: list[dict[str, Any]]) -> None:
    tx.run(
        "MATCH (b:DiagnosticBinding {rom:$rom}) DETACH DELETE b",
        rom=rom,
    ).consume()
    if not rows:
        return

    node_rows = [{
        key: value
        for key, value in row.items()
        if key not in {"dependencies"}
    } for row in rows]
    for batch in chunks(node_rows):
        tx.run(
            """
            UNWIND $rows AS r
            CREATE (b:DiagnosticBinding:Claim {
                id:r.graph_id,
                local_id:r.id,
                rom:r.rom,
                kind:r.kind,
                confidence:r.confidence,
                applicability:r.applicability,
                rom_scope:r.rom_scope,
                priority:r.priority,
                diagnostic_label:r.diagnostic_label,
                diagnostic_key:r.diagnostic_key,
                diagnostic_name:r.name,
                source_claim_label:r.source_claim_label,
                source_claim_id:r.source_claim_id,
                source_applicability:r.source_applicability,
                source_verification:r.source_verification,
                source_dataset_id:r.source_dataset_id,
                firmware_confidence_prop:r.firmware_confidence_prop,
                firmware_confidence:r.firmware_confidence,
                annotation_source:r.annotation_source,
                evidence:r.evidence,
                note:r.note
            })
            WITH b, r
            MATCH (rom:Rom {id:r.rom})
            MERGE (rom)-[:HAS_DIAGNOSTIC_BINDING]->(b)
            """,
            rows=batch,
        ).consume()

    for label in FIRMWARE_LABELS:
        part = [row for row in rows if row["firmware_label"] == label]
        for batch in chunks(part):
            tx.run(
                f"""
                UNWIND $rows AS r
                MATCH (b:DiagnosticBinding {{id:r.graph_id}})
                MATCH (n:{label} {{rom:r.rom, addr:r.firmware_addr}})
                MERGE (b)-[:BINDS_FIRMWARE]->(n)
                """,
                rows=batch,
            ).consume()

    for label, spec in DIAGNOSTIC_SOURCES.items():
        part = [row for row in rows if row["diagnostic_label"] == label]
        key = spec["key"]
        for batch in chunks(part):
            tx.run(
                f"""
                UNWIND $rows AS r
                MATCH (b:DiagnosticBinding {{id:r.graph_id}})
                MATCH (d:{label} {{{key}:r.diagnostic_key}})
                MERGE (b)-[:BINDS_DIAGNOSTIC]->(d)
                """,
                rows=batch,
            ).consume()

    source_labels = sorted({
        row["source_claim_label"] for row in rows
    })
    for label in source_labels:
        part = [row for row in rows if row["source_claim_label"] == label]
        for batch in chunks(part):
            tx.run(
                f"""
                UNWIND $rows AS r
                MATCH (b:DiagnosticBinding {{id:r.graph_id}})
                MATCH (s:{label} {{id:r.source_claim_id}})
                MERGE (b)-[:RESTS_ON {{
                    role:'diagnostic_source',
                    source_prop:'confidence'
                }}]->(s)
                """,
                rows=batch,
            ).consume()

    dependencies = [
        {
            "graph_id": row["graph_id"],
            "rom": row["rom"],
            **dependency,
        }
        for row in rows
        for dependency in row["dependencies"]
    ]
    for label in FIRMWARE_LABELS:
        part = [dep for dep in dependencies if dep["label"] == label]
        for batch in chunks(part):
            tx.run(
                f"""
                UNWIND $rows AS r
                MATCH (b:DiagnosticBinding {{id:r.graph_id}})
                MATCH (n:{label} {{rom:r.rom, addr:r.addr}})
                MERGE (b)-[e:RESTS_ON {{
                    role:r.role,
                    source_prop:'confidence',
                    target_prop:r.target_prop,
                    ref:r.ref
                }}]->(n)
                """,
                rows=batch,
            ).consume()


def audit(tx: Any, rom: str, expected: int) -> None:
    row = tx.run(
        """
        MATCH (b:DiagnosticBinding {rom:$rom})
        OPTIONAL MATCH (b)-[f:BINDS_FIRMWARE]->()
        OPTIONAL MATCH (b)-[d:BINDS_DIAGNOSTIC]->()
        OPTIONAL MATCH (b)-[s:RESTS_ON {role:'diagnostic_source'}]->()
        RETURN count(DISTINCT b) AS bindings,
               count(DISTINCT f) AS firmware_edges,
               count(DISTINCT d) AS diagnostic_edges,
               count(DISTINCT s) AS source_edges
        """,
        rom=rom,
    ).single()
    actual = {
        "bindings": row["bindings"],
        "firmware_edges": row["firmware_edges"],
        "diagnostic_edges": row["diagnostic_edges"],
        "source_edges": row["source_edges"],
    }
    bad = {
        key: value for key, value in actual.items()
        if value != expected
    }
    if bad:
        raise BindingError(
            f"DiagnosticBinding audit failed for {rom}: "
            + ", ".join(
                f"{key}={value}, expected={expected}"
                for key, value in bad.items()
            )
        )


def report(rom: str, rows: list[dict[str, Any]]) -> None:
    print(f"Diagnostic bindings {rom}: {len(rows)} claims")
    for field in ("kind", "confidence", "applicability", "rom_scope"):
        counts = Counter(row[field] for row in rows)
        print(
            f"  {field}: "
            + ", ".join(f"{key}={counts[key]}" for key in sorted(counts))
        )


def load_source(rom: str) -> tuple[
    rom_sources.SourceModel, Path, list[dict[str, Any]]
]:
    model = rom_sources.resolve(rom)
    rom_sources.verify_image_binding(model)
    path = rom_sources.definition_paths(model)["DiagnosticBinding"]
    rows = validate_rows(read_rows(path), path)
    rows = materialize_rows(model, rows)
    for row in rows:
        row["annotation_source"] = model.source
    return model, path, rows


def main() -> int:
    rom = sys.argv[1] if len(sys.argv) > 1 else "JK08A"
    try:
        model, path, rows = load_source(rom)
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1

    print(
        f"Preflight {rom}: source={model.source}, mode={model.kind}, "
        f"file={path}"
    )
    driver = GraphDatabase.driver(BOLT, auth=("", ""))
    try:
        with driver.session() as session:
            create_indexes(session)
            tx = session.begin_transaction()
            try:
                resolved = resolve_rows(tx, rom, rows)
                write_projection(tx, rom, resolved)
                audit(tx, rom, len(resolved))
                tx.commit()
            except Exception:
                tx.rollback()
                raise
    except Exception as error:
        print(f"Diagnostic binding ingest failed: {error}", file=sys.stderr)
        return 1
    finally:
        driver.close()
    report(rom, resolved)
    return 0


if __name__ == "__main__":
    sys.exit(main())
