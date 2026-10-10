#!/usr/bin/env python3
"""Normalize the pinned ecudocs P32M diagnostic profile."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from check_projection import check as check_projection
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


DATASET_ID = "ecudocs-p32m-997c5a9"
REVISION = "997c5a98b4f7fe5a7dfebfeeaefce1710a11f385"
SOURCE_URL = "https://github.com/laravelcompany/ecudocs.com"
PROFILE_PATH = "public/ecus/N_P32M_ECM_TR25_20080313.json"
VEHICLE_ID = "nissan-p32m-tr25-2008"
ECU_ID = f"{VEHICLE_ID}:ecm"
DEFAULT_OUTPUT = REFS / "public" / "ecudocs-p32m"

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
    "name",
    "request_hex",
    "response_template_hex",
    "request_can_id",
    "response_can_id",
    "session",
    "response_length",
    "read_only",
    "operation_kind",
    "manual_send",
    "ecu_id",
    "vehicle_id",
    "applicability_status",
    "verification_status",
    "source_fragment_id",
)
LINK_FIELDS = (
    "id",
    "dataset_id",
    "request_id",
    "parameter_id",
    "direction",
    "first_byte",
    "bit_offset",
    "byte_order",
    "source_fragment_id",
)


def document_id() -> str:
    return f"{DATASET_ID}:{slug(PROFILE_PATH)}"


def data_parameter_id(name: str) -> str:
    return f"{DATASET_ID}:data:{keyed_slug(name)}"


def json_fragment(
    pointer: str, kind: str, heading: str, value: Any
) -> dict[str, object]:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return {
        "id": f"{document_id()}:{kind}:{keyed_slug(pointer)}",
        "dataset_id": DATASET_ID,
        "document_id": document_id(),
        "json_pointer": pointer,
        "kind": kind,
        "heading": heading,
        "ecu_id": ECU_ID,
        "vehicle_id": VEHICLE_ID,
        "text_sha256": sha256_text(text),
        "text": text,
    }


def formula_fields(item: dict[str, Any]) -> dict[str, object]:
    if not item.get("scaled"):
        return {"factor": "", "addend": "", "formula": ""}
    step = item.get("step", 1)
    divide = item.get("divideby", 1)
    offset = item.get("offset", 0)
    factor = step / divide
    return {
        "factor": factor,
        "addend": offset,
        "formula": f"raw * {step} / {divide} + {offset}",
    }


def value_map(item: dict[str, Any]) -> str:
    values = item.get("lists")
    if not isinstance(values, dict):
        return ""
    return ";".join(f"{key}={value}" for key, value in values.items())


def response_length(item: dict[str, Any]) -> object:
    if item.get("bytescount") is not None:
        return item["bytescount"]
    if item.get("bitscount") is not None:
        return max(1, math.ceil(int(item["bitscount"]) / 8))
    if item.get("byte"):
        return 1
    return ""


def request_kind(service: str) -> tuple[bool, str]:
    read_services = {
        "17": "dtc_read",
        "18": "dtc_read",
        "19": "dtc_read",
        "1a": "identification_read",
        "21": "data_read",
        "22": "data_read",
        "23": "memory_read",
    }
    if service in read_services:
        return True, read_services[service]
    mapping = {
        "10": "session_control",
        "11": "ecu_reset",
        "14": "dtc_clear",
        "27": "security_access",
        "2c": "dynamic_definition",
        "30": "io_control",
        "31": "routine_control",
        "32": "routine_control",
        "3e": "tester_present",
    }
    return False, mapping.get(service, "command")


def build(source_root: Path) -> dict[str, list[dict[str, object]]]:
    require_pinned_git_tree(source_root, REVISION, (PROFILE_PATH,))
    profile_path = source_root / PROFILE_PATH
    if not profile_path.is_file():
        raise CatalogError(f"{profile_path}: required source file is missing")
    with profile_path.open(encoding="utf-8") as source:
        profile = json.load(source)
    data = profile.get("data")
    requests_source = profile.get("requests")
    obd = profile.get("obd")
    if not isinstance(data, dict) or not isinstance(requests_source, list):
        raise CatalogError(f"{profile_path}: data and requests have invalid types")
    if not isinstance(obd, dict):
        raise CatalogError(f"{profile_path}: obd metadata is missing")

    documents = [
        {
            "id": document_id(),
            "dataset_id": DATASET_ID,
            "filename": PROFILE_PATH,
            "title": str(profile.get("ecuname", Path(PROFILE_PATH).stem)),
            "kind": "source_file",
            "sha256": sha256_file(profile_path),
            "source_url": f"{SOURCE_URL}/blob/{REVISION}/{PROFILE_PATH}",
            "revision": REVISION,
            "license": "GPL-3.0",
            "applicability_status": "homologous_profile",
        }
    ]
    fragments = []
    parameters = []
    parameter_ids = {}
    for name, item in data.items():
        if not isinstance(item, dict):
            raise CatalogError(f"{profile_path}: data item {name!r} is not an object")
        pointer = f"#/data/{name.replace('~', '~0').replace('/', '~1')}"
        fragment = json_fragment(pointer, "data-item", name, item)
        fragments.append(fragment)
        parameter_id = data_parameter_id(name)
        parameter_ids[name] = parameter_id
        parameters.append(
            {
                "id": parameter_id,
                "dataset_id": DATASET_ID,
                "name": name,
                "ecu_id": ECU_ID,
                "unit": item.get("unit", ""),
                "description": item.get("comment", ""),
                "remarks": "",
                "protocol": "nissan-structured-diagnostic-profile",
                "external_id": "",
                "request_hex": "",
                "response_offset": "",
                "response_length": response_length(item),
                "byte_order": "big" if profile.get("endian") == "Big" else "",
                "signed": item.get("signed", ""),
                **formula_fields(item),
                "value_map": value_map(item),
                "applicability_status": "homologous_profile",
                "verification_status": "profile_defined",
                "source_fragment_id": fragment["id"],
            }
        )

    request_rows = []
    links = []
    send_id = normalize_hex(str(obd.get("send_id", "")))
    recv_id = normalize_hex(str(obd.get("recv_id", "")))
    for index, request in enumerate(requests_source):
        if not isinstance(request, dict):
            raise CatalogError(f"{profile_path}: request {index} is not an object")
        sent = normalize_hex(str(request["sentbytes"]))
        service = sent[:2]
        read_only, operation_kind = request_kind(service)
        fragment = json_fragment(
            f"#/requests/{index}", "request", str(request["name"]), request
        )
        fragments.append(fragment)
        request_id = f"{DATASET_ID}:request:{index:04d}:{sent}"
        identifier = (
            f"0x{sent[2:6].upper()}" if service == "22" and len(sent) >= 6 else ""
        )
        request_rows.append(
            {
                "id": request_id,
                "dataset_id": DATASET_ID,
                "protocol": "iso-15765-can",
                "service_id": f"0x{service.upper()}",
                "identifier": identifier,
                "name": request["name"],
                "request_hex": sent,
                "response_template_hex": (
                    normalize_hex(str(request["replybytes"]))
                    if request.get("replybytes")
                    else ""
                ),
                "request_can_id": f"0x{int(send_id, 16):03X}",
                "response_can_id": f"0x{int(recv_id, 16):03X}",
                "session": "",
                "response_length": request.get("minbytes", ""),
                "read_only": read_only,
                "operation_kind": operation_kind,
                "manual_send": bool(request.get("manualsend", False)),
                "ecu_id": ECU_ID,
                "vehicle_id": VEHICLE_ID,
                "applicability_status": "homologous_profile",
                "verification_status": "profile_defined",
                "source_fragment_id": fragment["id"],
            }
        )
        for direction, collection_name in (
            ("send", "sendbyte_dataitems"),
            ("receive", "receivebyte_dataitems"),
        ):
            collection = request.get(collection_name, {})
            if not isinstance(collection, dict):
                raise CatalogError(
                    f"{profile_path}: request {index} {collection_name} is not an object"
                )
            for parameter_name, placement in collection.items():
                if parameter_name not in parameter_ids:
                    raise CatalogError(
                        f"{profile_path}: request {index} references unknown data item "
                        f"{parameter_name!r}"
                    )
                if not isinstance(placement, dict):
                    raise CatalogError(
                        f"{profile_path}: invalid placement for {parameter_name!r}"
                    )
                links.append(
                    {
                        "id": (
                            f"{request_id}:{direction}:"
                            f"{keyed_slug(parameter_name)}"
                        ),
                        "dataset_id": DATASET_ID,
                        "request_id": request_id,
                        "parameter_id": parameter_ids[parameter_name],
                        "direction": direction,
                        "first_byte": placement.get("firstbyte", ""),
                        "bit_offset": placement.get("bitoffset", ""),
                        "byte_order": placement.get("endian", ""),
                        "source_fragment_id": fragment["id"],
                    }
                )

    for rows in (documents, fragments, parameters, request_rows, links):
        require_unique(rows, ("id",))
    return {
        "documents": documents,
        "fragments": fragments,
        "diagnostic_parameters": parameters,
        "diagnostic_requests": request_rows,
        "request_parameters": links,
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
    write_csv(
        output / "request_parameters.csv",
        LINK_FIELDS,
        catalog["request_parameters"],
    )


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("source_root", type=Path)
    result.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    result.add_argument("--check", action="store_true", help="validate and byte-compare outputs without writing")
    return result


def main() -> int:
    args = parser().parse_args()
    source_root = args.source_root.expanduser().resolve()
    try:
        catalog = build(source_root)
        if args.check:
            check_projection(args.output, catalog, write)
    except (OSError, KeyError, ValueError, json.JSONDecodeError, CatalogError) as error:
        print(error, file=sys.stderr)
        return 1
    service_22 = sum(
        row["service_id"] == "0x22" for row in catalog["diagnostic_requests"]
    )
    print(
        "ecudocs P32M: "
        f"documents={len(catalog['documents'])}, "
        f"fragments={len(catalog['fragments'])}, "
        f"parameters={len(catalog['diagnostic_parameters'])}, "
        f"requests={len(catalog['diagnostic_requests'])}, "
        f"service_22={service_22}, "
        f"request_parameter_links={len(catalog['request_parameters'])}"
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
