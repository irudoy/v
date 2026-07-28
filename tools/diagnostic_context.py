"""Shared rendering for graph-backed static diagnostic bindings."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Iterable


FIELDS = (
    "diagnostic_label",
    "diagnostic_key",
    "diagnostic_name",
    "confidence",
    "applicability",
    "priority",
)

MAP_BINDING_QUERIES = (
    (
        "direct",
        """
        MATCH (b:DiagnosticBinding {rom:$rom})-[:BINDS_FIRMWARE]->
              (m:Map {rom:$rom})
        RETURN m.addr AS map_addr, b.diagnostic_label AS diagnostic_label,
               b.diagnostic_key AS diagnostic_key,
               b.diagnostic_name AS diagnostic_name,
               b.confidence AS confidence,
               b.applicability AS applicability,
               b.priority AS priority
        """,
    ),
    (
        "map_evidence",
        """
        MATCH (m:Map {rom:$rom})-[evidence:RESTS_ON]->(firmware)
        MATCH (b:DiagnosticBinding {rom:$rom})-[:BINDS_FIRMWARE]->(firmware)
        RETURN m.addr AS map_addr, b.diagnostic_label AS diagnostic_label,
               b.diagnostic_key AS diagnostic_key,
               b.diagnostic_name AS diagnostic_name,
               b.confidence AS confidence,
               b.applicability AS applicability,
               b.priority AS priority,
               collect(DISTINCT evidence.role) AS relation_roles
        """,
    ),
    (
        "axis",
        """
        MATCH (m:Map {rom:$rom})-[axis_edge]->(axis:Axis {rom:$rom})
        MATCH (b:DiagnosticBinding {rom:$rom})-[:BINDS_FIRMWARE]->(axis)
        WHERE type(axis_edge) IN ['AXIS_X', 'AXIS_Y']
        RETURN m.addr AS map_addr, b.diagnostic_label AS diagnostic_label,
               b.diagnostic_key AS diagnostic_key,
               b.diagnostic_name AS diagnostic_name,
               b.confidence AS confidence,
               b.applicability AS applicability,
               b.priority AS priority
        """,
    ),
    (
        "axis_evidence",
        """
        MATCH (m:Map {rom:$rom})-[axis_edge]->(axis:Axis {rom:$rom})
              -[evidence:RESTS_ON]->(firmware)
        MATCH (b:DiagnosticBinding {rom:$rom})-[:BINDS_FIRMWARE]->(firmware)
        WHERE type(axis_edge) IN ['AXIS_X', 'AXIS_Y']
        RETURN m.addr AS map_addr, b.diagnostic_label AS diagnostic_label,
               b.diagnostic_key AS diagnostic_key,
               b.diagnostic_name AS diagnostic_name,
               b.confidence AS confidence,
               b.applicability AS applicability,
               b.priority AS priority,
               collect(DISTINCT evidence.role) AS relation_roles
        """,
    ),
)

RELATION_TEXT = {
    "direct": "",
    "map_evidence": "via map evidence",
    "axis": "via map axis",
    "axis_evidence": "via axis evidence",
}
RELATION_RANK = {
    relation: rank for rank, relation in enumerate(RELATION_TEXT)
}


def map_bindings(session: Any, rom: str) -> dict[str, list[dict[str, Any]]]:
    """Return direct and provenance-reachable bindings for each map."""
    result: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for relation, query in MAP_BINDING_QUERIES:
        for row in session.run(query, rom=rom):
            binding = {
                **{field: row[field] for field in FIELDS},
                "relation": relation,
            }
            roles = row.get("relation_roles")
            if roles:
                binding["relation_roles"] = sorted(set(roles))
            result[row["map_addr"]].append(binding)
    return dict(result)


def binding_label(binding: dict[str, Any]) -> str:
    key = str(binding.get("diagnostic_key") or "")
    if binding.get("diagnostic_label") == "DtcCode":
        return f"DTC {key}"
    return str(binding.get("diagnostic_name") or key)


def summarize(
    bindings: Iterable[dict[str, Any]],
) -> tuple[int, list[str]]:
    """Return maximum worklist priority and stable, de-duplicated summaries."""
    normalized = []
    for binding in bindings:
        if not binding or not binding.get("diagnostic_key"):
            continue
        priority = int(binding.get("priority") or 0)
        label = binding_label(binding)
        confidence = str(binding.get("confidence") or "")
        applicability = str(binding.get("applicability") or "")
        relation = str(binding.get("relation") or "direct")
        relation_text = RELATION_TEXT.get(relation, relation)
        relation_roles = sorted({
            str(role)
            for role in binding.get("relation_roles", [])
            if role
        })
        if relation_text and relation_roles:
            relation_text += ": " + "/".join(relation_roles)
        suffix = ", ".join(
            value
            for value in (confidence, applicability, relation_text)
            if value
        )
        text = f"{label} [{suffix}]" if suffix else label
        identity = (
            str(binding.get("diagnostic_label") or ""),
            str(binding.get("diagnostic_key") or ""),
            confidence,
            applicability,
        )
        normalized.append((
            priority,
            RELATION_RANK.get(relation, len(RELATION_RANK)),
            label.lower(),
            text,
            identity,
        ))

    unique = {}
    for item in normalized:
        previous = unique.get(item[4])
        if (
            previous is None
            or item[1] < previous[1]
            or (item[1] == previous[1] and item[0] > previous[0])
        ):
            unique[item[4]] = item
    ordered = sorted(
        unique.values(),
        key=lambda item: (-item[0], item[2], item[3]),
    )
    return (
        max((item[0] for item in ordered), default=0),
        [item[3] for item in ordered],
    )
