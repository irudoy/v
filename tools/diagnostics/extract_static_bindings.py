#!/usr/bin/env python3
"""Build a review-only SID 0x22 firmware-binding candidate worklist.

The extractor joins three exact artifacts:

* service 0x22 DIDs and parameter claims from the diagnostic corpus;
* ROM constants and instruction immediates from ExportDiagnosticRefs.java;
* function-to-RAM references from ExportXrefs.java.

The output never feeds load_diagnostic_bindings.py directly. A DID literal can
be unrelated data, and every RAM address in the same function is only a hint
until a dispatcher-to-response data-flow trace establishes the path.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "memgraph"))

import rom_sources  # noqa: E402
from ingest_diagnostics import collect_projection, load_catalog  # noqa: E402


REF_FIELDS = [
    "func_addr", "site", "source_kind", "literal_addr", "value_hex"
]
XREF_FIELDS = ["func_addr", "periph_addr", "kind"]
CANDIDATE_FIELDS = [
    "request_hex",
    "did",
    "diagnostic_key",
    "name",
    "source_applicability",
    "source_verification",
    "source_dataset_id",
    "source_claim_id",
    "func_addr",
    "site",
    "source_kind",
    "literal_addr",
    "function_did_count",
    "ram_candidates",
    "ram_candidate_count",
    "source_formula",
    "source_factor",
    "source_addend",
    "source_unit",
    "status",
]


class ExtractError(ValueError):
    pass


def read_csv(path: Path, fields: list[str]) -> list[dict[str, str]]:
    if not path.is_file():
        raise ExtractError(f"input not found: {path}")
    with path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != fields:
            raise ExtractError(
                f"{path}: header {reader.fieldnames}; expected {fields}"
            )
        return list(reader)


def request_did(value: Any) -> tuple[str, str] | None:
    compact = re.sub(r"(?i)0x", "", str(value or "").strip())
    compact = re.sub(r"[\s,_:-]+", "", compact).lower()
    if (
        len(compact) < 6
        or not compact.startswith("22")
        or not re.fullmatch(r"[0-9a-f]+", compact)
    ):
        return None
    return compact, compact[2:6]


def diagnostic_dids() -> dict[str, list[dict[str, Any]]]:
    """Return source-specific parameter definitions keyed by exact 16-bit DID."""
    projection = collect_projection(load_catalog())
    parameter_nodes = {
        row["id"]: row for row in projection["DiagnosticParameter"]
    }
    definitions_by_parameter: dict[str, list[dict[str, Any]]] = defaultdict(list)
    claim_by_id = {
        row["id"]: row for row in projection["ParameterDefinition"]
    }
    for edge in projection["parameter_definition"]:
        definitions_by_parameter[edge["to"]].append(
            claim_by_id[edge["from"]]
        )

    returns_by_request: dict[str, set[str]] = defaultdict(set)
    for edge in projection["request_output_parameter"]:
        returns_by_request[edge["from"]].add(edge["to"])

    result: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for request in projection["DiagnosticRequest"]:
        parsed = request_did(request.get("request_hex"))
        if parsed is None:
            continue
        request_hex, did = parsed
        dataset_id = str(request.get("dataset_id") or "")
        for parameter_id in sorted(returns_by_request.get(request["id"], ())):
            definitions = [
                row for row in definitions_by_parameter.get(parameter_id, [])
                if str(row.get("dataset_id") or "") == dataset_id
            ]
            if not definitions:
                definitions = definitions_by_parameter.get(parameter_id, [])
            for definition in definitions:
                result[did].append({
                    "request_hex": request_hex,
                    "did": did,
                    "diagnostic_key": parameter_id,
                    "name": (
                        definition.get("name")
                        or parameter_nodes.get(parameter_id, {}).get("name")
                        or parameter_id
                    ),
                    "source_applicability": definition.get(
                        "applicability_status", ""
                    ),
                    "source_verification": definition.get(
                        "verification_status", ""
                    ),
                    "source_dataset_id": definition.get("dataset_id", ""),
                    "source_claim_id": definition.get("id", ""),
                    "source_formula": definition.get("formula", ""),
                    "source_factor": definition.get("factor", ""),
                    "source_addend": definition.get("addend", ""),
                    "source_unit": definition.get("unit", ""),
                })

    for did, rows in result.items():
        unique = {
            tuple(str(row.get(field, "")) for field in (
                "request_hex", "diagnostic_key", "source_dataset_id",
                "source_claim_id",
            )): row
            for row in rows
        }
        result[did] = sorted(
            unique.values(),
            key=lambda row: (
                row["request_hex"],
                row["diagnostic_key"],
                str(row["source_dataset_id"]),
                str(row["source_claim_id"]),
                str(row["name"]),
            ),
        )
    return dict(result)


def ram_by_function(
    rows: Iterable[dict[str, str]]
) -> dict[str, list[str]]:
    result: dict[str, set[str]] = defaultdict(set)
    for row in rows:
        address = row["periph_addr"].lower()
        if address.startswith(("fffe", "ffff")):
            result[row["func_addr"]].add(address)
    return {
        function: sorted(addresses)
        for function, addresses in result.items()
    }


def build_candidates(
    definitions: dict[str, list[dict[str, Any]]],
    refs: Iterable[dict[str, str]],
    ram: dict[str, list[str]],
) -> list[dict[str, Any]]:
    refs = [
        ref for ref in refs
        if ref["value_hex"].lower() in definitions
    ]
    dids_by_function: dict[str, set[str]] = defaultdict(set)
    for ref in refs:
        dids_by_function[ref["func_addr"]].add(
            ref["value_hex"].lower()
        )

    candidates = []
    for ref in refs:
        did = ref["value_hex"].lower()
        addresses = ram.get(ref["func_addr"], [])
        function_did_count = len(dids_by_function[ref["func_addr"]])
        if function_did_count >= 4:
            status = "did-cluster"
        elif function_did_count >= 2:
            status = "multi-did-function"
        elif len(addresses) == 1:
            status = "single-function-ram-hint"
        else:
            status = "unresolved"
        for definition in definitions[did]:
            candidates.append({
                **definition,
                "func_addr": ref["func_addr"],
                "site": ref["site"],
                "source_kind": ref["source_kind"],
                "literal_addr": ref["literal_addr"],
                "function_did_count": function_did_count,
                "ram_candidates": ";".join(addresses),
                "ram_candidate_count": len(addresses),
                "status": status,
            })
    unique = {
        tuple(str(row.get(field, "")) for field in CANDIDATE_FIELDS): row
        for row in candidates
    }
    return sorted(
        unique.values(),
        key=lambda row: (
            {
                "did-cluster": 0,
                "multi-did-function": 1,
                "single-function-ram-hint": 2,
                "unresolved": 3,
            }[row["status"]],
            row["request_hex"],
            row["diagnostic_key"],
            row["func_addr"],
            row["site"],
            row["source_kind"],
            row["literal_addr"],
        ),
    )


def write_candidates(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(
            target, fieldnames=CANDIDATE_FIELDS, lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("rom", nargs="?", default="JK08A")
    result.add_argument(
        "--export-dir",
        type=Path,
        help="Ghidra export directory; default: canonical directory registered for the ROM",
    )
    result.add_argument(
        "--output",
        type=Path,
        help="candidate CSV; default: <export-dir>/diagnostic-binding-candidates.csv",
    )
    return result


def main() -> int:
    args = parser().parse_args()
    export_dir = (
        args.export_dir.expanduser().resolve()
        if args.export_dir
        else rom_sources.default_export_dir(args.rom)
    )
    output = (
        args.output.expanduser().resolve()
        if args.output
        else export_dir / "diagnostic-binding-candidates.csv"
    )
    try:
        model = rom_sources.resolve(args.rom)
        rom_sources.verify_image_binding(model)
        definitions = diagnostic_dids()
        refs = read_csv(export_dir / "diagnostic_refs.csv", REF_FIELDS)
        xrefs = read_csv(export_dir / "xrefs.csv", XREF_FIELDS)
        rows = build_candidates(
            definitions, refs, ram_by_function(xrefs)
        )
        write_candidates(output, rows)
    except (OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1

    print(
        f"{output}: {len(rows)} review candidates from "
        f"{len(definitions)} known service 0x22 DIDs"
    )
    clustered = sum(
        1 for row in rows
        if row["status"] in {"did-cluster", "multi-did-function"}
    )
    print(f"  multi-DID function candidates: {clustered}")
    print(
        "No row is loadable as a DiagnosticBinding until a machine data-flow "
        "trace resolves the dispatcher, response value, and conversion."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
