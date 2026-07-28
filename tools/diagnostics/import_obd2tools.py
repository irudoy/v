#!/usr/bin/env python3
"""Normalize pinned obd2tools Nissan SID 0x22 definitions without executing them."""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path
from typing import Any

from catalog import (
    CatalogError,
    REFS,
    ROOT,
    keyed_slug,
    normalize_hex,
    require_pinned_git_tree,
    require_unique,
    sha256_file,
    sha256_text,
    slug,
    write_csv,
    write_jsonl,
)


DATASET_ID = "obd2tools-d27c9a2"
REVISION = "d27c9a203a03cf02b953f1bb06c79f7bb5885d53"
SOURCE_URL = "https://github.com/elvisfox/obd2tools"
VEHICLE_ID = "nissan-community-unspecified"
ECU_ID = f"{VEHICLE_ID}:ecm"
DEFAULT_OUTPUT = REFS / "public" / "obd2tools"
SOURCE_FILES = ("pids/parsed.py", "pids/nissan.py")

DOCUMENT_FIELDS = (
    "id",
    "dataset_id",
    "filename",
    "title",
    "kind",
    "sha256",
    "source_url",
    "revision",
    "license",
    "applicability_status",
)
PARAMETER_FIELDS = (
    "id",
    "dataset_id",
    "name",
    "ecu_id",
    "unit",
    "description",
    "remarks",
    "protocol",
    "external_id",
    "request_hex",
    "response_offset",
    "response_length",
    "byte_order",
    "signed",
    "factor",
    "addend",
    "formula",
    "value_map",
    "applicability_status",
    "verification_status",
    "source_fragment_id",
)
REQUEST_FIELDS = (
    "id",
    "dataset_id",
    "protocol",
    "service_id",
    "identifier",
    "request_hex",
    "request_can_id",
    "response_can_id",
    "session",
    "response_length",
    "read_only",
    "operation_kind",
    "ecu_id",
    "vehicle_id",
    "applicability_status",
    "verification_status",
    "source_fragment_id",
)


def document_id(relative_path: str) -> str:
    return f"{DATASET_ID}:{slug(relative_path)}"


def expression_value(node: ast.AST) -> Any:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.List):
        return [expression_value(item) for item in node.elts]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
        value = expression_value(node.operand)
        return -value if isinstance(node.op, ast.USub) else value
    if isinstance(node, ast.BinOp):
        left = expression_value(node.left)
        right = expression_value(node.right)
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
    raise CatalogError(
        f"unsupported expression in PID definition at line "
        f"{getattr(node, 'lineno', '?')}"
    )


def definition_entries(
    path: Path, variable: str
) -> tuple[str, list[tuple[int, int, list[Any], str]]]:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text, filename=str(path))
    value_node = None
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == variable for target in node.targets):
            value_node = node.value
            break
    if not isinstance(value_node, ast.List):
        raise CatalogError(f"{path}: list assignment {variable} not found")
    result = []
    for item in value_node.elts:
        if not isinstance(item, ast.List):
            raise CatalogError(f"{path}:{item.lineno}: PID row is not a list")
        values = expression_value(item)
        if not isinstance(values, list):
            raise CatalogError(f"{path}:{item.lineno}: invalid PID row")
        segment = ast.get_source_segment(text, item) or ""
        result.append((item.lineno, item.end_lineno or item.lineno, values, segment))
    return text, result


def source_fragment(
    relative_path: str,
    line_start: int,
    line_end: int,
    ordinal: int,
    text: str,
) -> dict[str, object]:
    return {
        "id": (
            f"{document_id(relative_path)}:"
            f"l{line_start:04d}-l{line_end:04d}:entry-{ordinal:04d}"
        ),
        "dataset_id": DATASET_ID,
        "document_id": document_id(relative_path),
        "line_start": line_start,
        "line_end": line_end,
        "kind": "pid_definition",
        "heading": "",
        "ecu_id": ECU_ID,
        "vehicle_id": VEHICLE_ID,
        "text_sha256": sha256_text(text),
        "text": text,
    }


def formula_fields(function: str, params: list[Any], source_kind: str) -> dict[str, object]:
    if source_kind == "parsed":
        return {
            "signed": "",
            "factor": "",
            "addend": "",
            "formula": "",
            "verification_status": "community_name_only",
        }
    if function == "linear" and len(params) >= 2:
        gain, offset = params[0], params[1]
        return {
            "signed": False,
            "factor": gain,
            "addend": offset,
            "formula": f"raw * {gain} + {offset}",
            "verification_status": "community_defined",
        }
    if function == "signed" and len(params) >= 2:
        bits, gain = params[0], params[1]
        return {
            "signed": True,
            "factor": gain,
            "addend": "",
            "formula": f"signed(raw, {bits}) * {gain}",
            "verification_status": "community_defined",
        }
    return {
        "signed": "",
        "factor": "",
        "addend": "",
        "formula": "",
        "verification_status": "semantic_unknown",
    }


def build(source_root: Path) -> dict[str, list[dict[str, object]]]:
    require_pinned_git_tree(source_root, REVISION, SOURCE_FILES)
    documents = []
    fragments = []
    parameters = []
    requests_by_command: dict[str, dict[str, object]] = {}

    for relative_path, variable, source_kind in (
        ("pids/parsed.py", "parsed_pids", "parsed"),
        ("pids/nissan.py", "nissan_pids", "nissan"),
    ):
        path = source_root / relative_path
        if not path.is_file():
            raise CatalogError(f"{path}: required source file is missing")
        documents.append(
            {
                "id": document_id(relative_path),
                "dataset_id": DATASET_ID,
                "filename": relative_path,
                "title": Path(relative_path).name,
                "kind": "source_file",
                "sha256": sha256_file(path),
                "source_url": f"{SOURCE_URL}/blob/{REVISION}/{relative_path}",
                "revision": REVISION,
                "license": "unspecified",
                "applicability_status": "nissan_family_candidate",
            }
        )
        _text, entries = definition_entries(path, variable)
        for ordinal, (line_start, line_end, values, segment) in enumerate(entries, 1):
            if len(values) < 8:
                raise CatalogError(f"{path}:{line_start}: expected eight PID fields")
            fragment = source_fragment(
                relative_path, line_start, line_end, ordinal, segment
            )
            fragments.append(fragment)
            header, command, example, name, unit, display, function, params = values[:8]
            command = normalize_hex(str(command))
            if not command.startswith("22") or len(command) != 6:
                continue
            if not isinstance(params, list):
                raise CatalogError(f"{path}:{line_start}: formula params are not a list")
            fields = formula_fields(str(function), params, source_kind)
            identifier = f"0x{command[2:].upper()}"
            response_length = (
                len(normalize_hex(str(example))) // 2 if str(example).strip() else ""
            )
            row_id = (
                f"{fragment['id']}:parameter:"
                f"{keyed_slug(str(name) + '-' + command)}"
            )
            parameters.append(
                {
                    "id": row_id,
                    "dataset_id": DATASET_ID,
                    "name": str(name),
                    "ecu_id": ECU_ID,
                    "unit": str(unit),
                    "description": "",
                    "remarks": f"display={display}",
                    "protocol": "iso-14229-service-22",
                    "external_id": identifier,
                    "request_hex": command,
                    "response_offset": "",
                    "response_length": response_length,
                    "byte_order": "big",
                    **fields,
                    "value_map": "",
                    "applicability_status": "nissan_family_candidate",
                    "source_fragment_id": fragment["id"],
                }
            )
            if command not in requests_by_command:
                requests_by_command[command] = {
                    "id": f"{DATASET_ID}:request:{command}",
                    "dataset_id": DATASET_ID,
                    "protocol": "iso-15765-can",
                    "service_id": "0x22",
                    "identifier": identifier,
                    "request_hex": command,
                    "request_can_id": f"0x{int(header):03X}",
                    "response_can_id": "0x7E8" if int(header) == 0x7E0 else "",
                    "session": "10c0",
                    "response_length": response_length,
                    "read_only": True,
                    "operation_kind": "data_read",
                    "ecu_id": ECU_ID,
                    "vehicle_id": VEHICLE_ID,
                    "applicability_status": "nissan_family_candidate",
                    "verification_status": "community_defined",
                    "source_fragment_id": fragment["id"],
                }

    requests = [requests_by_command[key] for key in sorted(requests_by_command)]
    for rows in (documents, fragments, parameters, requests):
        require_unique(rows, ("id",))
    return {
        "documents": documents,
        "fragments": fragments,
        "diagnostic_parameters": parameters,
        "diagnostic_requests": requests,
    }


def write(output: Path, catalog: dict[str, list[dict[str, object]]]) -> None:
    write_csv(output / "documents.csv", DOCUMENT_FIELDS, catalog["documents"])
    write_jsonl(output / "fragments.jsonl", catalog["fragments"])
    write_csv(
        output / "diagnostic_parameters.csv",
        PARAMETER_FIELDS,
        catalog["diagnostic_parameters"],
    )
    write_csv(
        output / "diagnostic_requests.csv",
        REQUEST_FIELDS,
        catalog["diagnostic_requests"],
    )


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("source_root", type=Path)
    result.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    result.add_argument("--check", action="store_true", help="validate without writing")
    return result


def main() -> int:
    args = parser().parse_args()
    source_root = args.source_root.expanduser().resolve()
    try:
        catalog = build(source_root)
    except (OSError, SyntaxError, CatalogError) as error:
        print(error, file=sys.stderr)
        return 1
    print(
        "obd2tools: "
        f"documents={len(catalog['documents'])}, "
        f"fragments={len(catalog['fragments'])}, "
        f"parameters={len(catalog['diagnostic_parameters'])}, "
        f"requests={len(catalog['diagnostic_requests'])}"
    )
    if not args.check:
        write(args.output, catalog)
        try:
            shown = args.output.relative_to(ROOT)
        except ValueError:
            shown = args.output
        print(f"Wrote {shown}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
