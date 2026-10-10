#!/usr/bin/env python3
"""Normalize the legacy Generic Nissan ECU Register Table PDF."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tomllib
from pathlib import Path
from check_projection import check as check_projection

from catalog import (
    CatalogError,
    REFS,
    ROOT,
    keyed_slug,
    normalize_hex,
    require_unique,
    sha256_file,
    sha256_text,
    slug,
    write_csv,
    write_jsonl,
)


DATASET_ID = "generic-nissan-datatable-2003-v1"
VEHICLE_ID = "generic-nissan-legacy"
DEFAULT_OUTPUT = REFS / "public" / "nissan-datatable"
SOURCE_MANIFEST = REFS.parent / "nissan-datatable" / "source.toml"
EXPECTED_PAGES = 7


def source_pdf(path=None, *, manifest=SOURCE_MANIFEST):
    """Bind this dataset to its declared immutable source PDF."""
    with manifest.open('rb') as source:
        pin = tomllib.load(source)
    if set(pin) != {'filename', 'source_url', 'sha256', 'pages'}:
        raise CatalogError(f'{manifest}: invalid source pin keys')
    name = pin['filename']
    digest = pin['sha256']
    if not isinstance(name, str) or Path(name).name != name or not name.endswith('.pdf'):
        raise CatalogError(f'{manifest}: filename must name one PDF')
    if not isinstance(digest, str) or not re.fullmatch('[0-9a-f]{64}', digest):
        raise CatalogError(f'{manifest}: invalid sha256')
    if type(pin['pages']) is not int or pin['pages'] != EXPECTED_PAGES:
        raise CatalogError(f'{manifest}: pages must match the dataset page contract')
    if not isinstance(pin['source_url'], str) or not pin['source_url'].startswith('https://'):
        raise CatalogError(f'{manifest}: source_url must be HTTPS')
    path = (manifest.parent / name if path is None else path).expanduser().resolve()
    if path.name != name:
        raise CatalogError(f'{path}: filename differs from source pin {name}')
    if sha256_file(path) != digest:
        raise CatalogError(f'{path}: sha256 differs from source pin')
    return path

DOCUMENT_FIELDS = (
    "id",
    "dataset_id",
    "filename",
    "title",
    "kind",
    "sha256",
    "page_count",
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
    "response_length",
    "read_only",
    "operation_kind",
    "ecu_id",
    "vehicle_id",
    "applicability_status",
    "verification_status",
    "source_fragment_id",
)
OPERATION_FIELDS = (
    "id",
    "dataset_id",
    "kind",
    "name",
    "ecu_id",
    "description",
    "conditions",
    "usage",
    "protocol",
    "request_hex",
    "read_only",
    "executable",
    "applicability_status",
    "verification_status",
    "source_fragment_id",
)

ECU_BY_PAGE = {
    1: "engine",
    2: "engine",
    3: "engine",
    4: "automatic-transmission",
    5: "s-hicas",
    6: "air-conditioning",
    7: "air-conditioning",
}
COMMAND_NAMES = (
    "INITIALISATION",
    "STREAM ALL AVAILABLE SENSORS",
    "SELF DIAGNOSTIC",
    "ERASE ERROR CODES",
    "CLEAR ERROR CODES",
    "ECU INFO",
)
COMMAND_RE = re.compile(
    rf"^\s*({'|'.join(re.escape(name) for name in COMMAND_NAMES)})"
    r"\s{2,}((?:0x[0-9A-Fa-f]{2}\s*)+)\s*$"
)
REGISTER_RE = re.compile(
    r"^\s*(?P<name>[A-Za-z][A-Za-z0-9 /%().,&-]*?)\s{2,}"
    r"(?:(?P<width>MSB|LSB|LSD|Single [Bb]yte|Dual)\s{2,})?"
    r"(?P<registers>0x[0-9A-Fa-f]{2}(?:\s*,\s*0x[0-9A-Fa-f]{2})?)"
    r"(?:\s{2,}(?P<rest>.*?))?\s*$"
)
ACTIVE_RE = re.compile(
    r"^\s*(?P<name>[A-Z][A-Z0-9 ./&()-]*?)\s{2,}"
    r"(?P<register>0x[0-9A-Fa-f]{2})\s*(?P<rest>.*)$"
)


def run_text(command: list[str]) -> str:
    try:
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except FileNotFoundError as error:
        raise CatalogError(f"required command not found: {command[0]}") from error
    except subprocess.CalledProcessError as error:
        detail = error.stderr.strip() or f"exit status {error.returncode}"
        raise CatalogError(f"{' '.join(command)}: {detail}") from error
    return result.stdout


def pdf_pages(path: Path) -> list[str]:
    output = run_text(["pdftotext", "-layout", str(path), "-"])
    pages = output.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    return [page.rstrip() + "\n" for page in pages]


def pdf_page_count(path: Path) -> int:
    output = run_text(["pdfinfo", str(path)])
    match = re.search(r"(?m)^Pages:\s+(\d+)\s*$", output)
    if not match:
        raise CatalogError(f"{path}: page count is unavailable")
    return int(match.group(1))


def fragment_id(document_id: str, page: int, kind: str) -> str:
    return f"{document_id}:p{page:04d}:{slug(kind)}"


def ecu_id(page: int) -> str:
    return f"{VEHICLE_ID}:{ECU_BY_PAGE[page]}"


def page_fragment(
    document_id: str, page: int, kind: str, text: str
) -> dict[str, object]:
    return {
        "id": fragment_id(document_id, page, kind),
        "dataset_id": DATASET_ID,
        "document_id": document_id,
        "pdf_page": page,
        "kind": kind,
        "heading": next(
            (re.sub(r"\s+", " ", line.strip()) for line in text.splitlines() if line.strip()),
            "",
        ),
        "ecu_id": ecu_id(page),
        "vehicle_id": VEHICLE_ID,
        "text_sha256": sha256_text(text),
        "text": text,
    }


def parameter_lines(page: int, text: str) -> list[str]:
    lines = text.splitlines()
    start = 0
    end = len(lines)
    if page == 1:
        start = next(
            (index + 1 for index, line in enumerate(lines) if "Data Name" in line),
            len(lines),
        )
    elif page == 2:
        end = next(
            (
                index
                for index, line in enumerate(lines)
                if "Digital (Bit) registers" in line
            ),
            len(lines),
        )
    elif page in {4, 5, 6}:
        start = next(
            (
                index + 1
                for index, line in enumerate(lines)
                if re.search(r"\b(?:NAME|Name)\b.*\b(?:REG|Register No)\b", line)
            ),
            len(lines),
        )
        end = next(
            (
                index
                for index, line in enumerate(lines[start:], start)
                if re.search(r"\bDigital \(Bit\) registers\b|^\s*Register\s+Bit", line)
            ),
            len(lines),
        )
    else:
        return []
    return lines[start:end]


def unit_from_text(text: str) -> str:
    for pattern, unit in (
        (r"\bRPM\b", "rpm"),
        (r"\bKPH\b|\bKM/H\b", "km/h"),
        (r"\bMV\b", "mV"),
        (r"\bVOLT\b", "V"),
        (r"\bCELCIUS\b|\bDEG C\b|°C", "degC"),
        (r"\bDEG(?:REES)?\b", "degree"),
        (r"\bMSEC\b|\bMS\b", "ms"),
        (r"%", "%"),
        (r"\bAMPERE\b", "A"),
        (r"\bKCAL\b", "kcal"),
    ):
        if re.search(pattern, text, re.IGNORECASE):
            return unit
    return ""


def build_parameters(
    fragments_by_page: dict[int, dict[str, object]]
) -> list[dict[str, object]]:
    rows = []
    for page, fragment in sorted(fragments_by_page.items()):
        for line in parameter_lines(page, str(fragment["text"])):
            match = REGISTER_RE.match(line)
            if not match:
                continue
            name = re.sub(r"\s+", " ", match.group("name")).strip(" ,")
            registers = [
                f"0x{int(value, 16):02X}"
                for value in re.findall(r"0x[0-9A-Fa-f]{2}", match.group("registers"))
            ]
            rest = re.sub(r"\s+", " ", match.group("rest") or "").strip()
            width = re.sub(r"\s+", " ", match.group("width") or "").strip()
            external_id = ";".join(registers)
            rows.append(
                {
                    "id": (
                        f"{fragment['id']}:parameter:"
                        f"{keyed_slug(name + '-' + external_id)}"
                    ),
                    "dataset_id": DATASET_ID,
                    "name": name,
                    "ecu_id": fragment["ecu_id"],
                    "unit": unit_from_text(rest),
                    "description": "",
                    "remarks": width,
                    "protocol": "nissan-consult-i-register",
                    "external_id": external_id,
                    "request_hex": "",
                    "response_offset": "",
                    "response_length": (
                        "2"
                        if width.lower() in {"msb", "lsb", "lsd", "dual"}
                        or "word" in rest.lower()
                        else "1"
                    ),
                    "byte_order": "big" if width.lower() in {"msb", "lsb", "lsd"} else "",
                    "signed": "",
                    "factor": "",
                    "addend": "",
                    "formula": rest,
                    "applicability_status": "generic_legacy",
                    "verification_status": "community_defined",
                    "source_fragment_id": fragment["id"],
                }
            )
    return rows


def command_rows(
    fragments_by_page: dict[int, dict[str, object]]
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    operations = []
    requests = []
    for page, fragment in sorted(fragments_by_page.items()):
        for line in str(fragment["text"]).splitlines():
            match = COMMAND_RE.match(line)
            if not match:
                continue
            name = match.group(1)
            request = "".join(
                value[2:] for value in re.findall(r"0x[0-9A-Fa-f]{2}", match.group(2))
            ).lower()
            read_only = name not in {"ERASE ERROR CODES", "CLEAR ERROR CODES"}
            kind = "initialization" if name == "INITIALISATION" else "command"
            operation_id = f"{fragment['id']}:operation:{keyed_slug(name)}"
            operations.append(
                {
                    "id": operation_id,
                    "dataset_id": DATASET_ID,
                    "kind": kind,
                    "name": name,
                    "ecu_id": fragment["ecu_id"],
                    "description": "",
                    "conditions": "",
                    "usage": "",
                    "protocol": "nissan-consult-i",
                    "request_hex": request,
                    "read_only": read_only,
                    "executable": False,
                    "applicability_status": "generic_legacy",
                    "verification_status": "community_defined",
                    "source_fragment_id": fragment["id"],
                }
            )
            requests.append(
                {
                    "id": f"{operation_id}:request",
                    "dataset_id": DATASET_ID,
                    "protocol": "nissan-consult-i",
                    "service_id": "",
                    "identifier": name,
                    "request_hex": request,
                    "response_length": "",
                    "read_only": read_only,
                    "operation_kind": kind,
                    "ecu_id": fragment["ecu_id"],
                    "vehicle_id": VEHICLE_ID,
                    "applicability_status": "generic_legacy",
                    "verification_status": "community_defined",
                    "source_fragment_id": fragment["id"],
                }
            )
    return operations, requests


def active_test_rows(
    fragments_by_page: dict[int, dict[str, object]]
) -> list[dict[str, object]]:
    rows = []
    for page in (3, 5, 7):
        fragment = fragments_by_page[page]
        lines = str(fragment["text"]).splitlines()
        active_index = next(
            (
                index
                for index, line in enumerate(lines)
                if "ACTIVE TESTS" in line.upper()
            ),
            -1,
        )
        if active_index < 0:
            continue
        for line in lines[active_index + 1 :]:
            match = ACTIVE_RE.match(line)
            if not match:
                continue
            name = re.sub(r"\s+", " ", match.group("name")).strip()
            if name.startswith("REGISTER "):
                break
            register = normalize_hex(match.group("register"))
            description = re.sub(r"\s+", " ", match.group("rest")).strip()
            register_label = f"control register 0x{register.upper()}"
            rows.append(
                {
                    "id": f"{fragment['id']}:active-test:{keyed_slug(name)}",
                    "dataset_id": DATASET_ID,
                    "kind": "active_test",
                    "name": name,
                    "ecu_id": fragment["ecu_id"],
                    "description": "; ".join(
                        value for value in (register_label, description) if value
                    ),
                    "conditions": "",
                    "usage": (
                        "Service 0x0A requires a control value; the complete request "
                        "is not defined by this catalog."
                    ),
                    "protocol": "nissan-consult-i",
                    "request_hex": "",
                    "read_only": False,
                    "executable": False,
                    "applicability_status": "generic_legacy",
                    "verification_status": "community_defined",
                    "source_fragment_id": fragment["id"],
                }
            )
    return rows


def build(source_path: Path) -> dict[str, list[dict[str, object]]]:
    pages = pdf_pages(source_path)
    page_count = pdf_page_count(source_path)
    if page_count != EXPECTED_PAGES or len(pages) != EXPECTED_PAGES:
        raise CatalogError(
            f"{source_path}: got {len(pages)} text pages and {page_count} PDF pages, "
            f"expected {EXPECTED_PAGES}"
        )
    document_id = f"{DATASET_ID}:{slug(source_path.stem)}"
    documents = [
        {
            "id": document_id,
            "dataset_id": DATASET_ID,
            "filename": source_path.name,
            "title": "Generic Nissan Engine ECU Register Table",
            "kind": "source_file",
            "sha256": sha256_file(source_path),
            "page_count": page_count,
            "license": "unspecified",
            "applicability_status": "generic_legacy",
        }
    ]
    fragments = []
    fragments_by_page = {}
    for page, text in enumerate(pages, 1):
        kind = "active_test" if "ACTIVE TESTS" in text.upper() else "register_table"
        fragment = page_fragment(document_id, page, kind, text)
        fragments.append(fragment)
        fragments_by_page[page] = fragment
    parameters = build_parameters(fragments_by_page)
    operations, requests = command_rows(fragments_by_page)
    operations.extend(active_test_rows(fragments_by_page))

    for rows in (documents, fragments, parameters, operations, requests):
        require_unique(rows, ("id",))
    fragment_ids = {row["id"] for row in fragments}
    for row in parameters + operations + requests:
        if row["source_fragment_id"] not in fragment_ids:
            raise CatalogError(
                f"{row['id']}: missing fragment {row['source_fragment_id']}"
            )
    return {
        "documents": documents,
        "fragments": fragments,
        "diagnostic_parameters": parameters,
        "diagnostic_operations": operations,
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
        output / "diagnostic_operations.csv",
        OPERATION_FIELDS,
        catalog["diagnostic_operations"],
    )
    write_csv(
        output / "diagnostic_requests.csv",
        REQUEST_FIELDS,
        catalog["diagnostic_requests"],
    )


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("source_path", type=Path, nargs='?', help='PDF path; defaults to the tracked source pin')
    result.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    result.add_argument("--check", action="store_true", help="validate and byte-compare outputs without writing")
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        source_path = source_pdf(args.source_path)
        catalog = build(source_path)
        if args.check:
            check_projection(args.output, catalog, write)
    except (OSError, CatalogError, tomllib.TOMLDecodeError) as error:
        print(error, file=sys.stderr)
        return 1
    print(
        "NissanDatatable: "
        f"documents={len(catalog['documents'])}, "
        f"fragments={len(catalog['fragments'])}, "
        f"parameters={len(catalog['diagnostic_parameters'])}, "
        f"operations={len(catalog['diagnostic_operations'])}, "
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
