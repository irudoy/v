#!/usr/bin/env python3
"""Validate and project the reproducible diagnostic catalogs into Memgraph."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[2]
DIAGNOSTICS = ROOT / "refs" / "diagnostics"
sys.path.insert(0, str(ROOT / "tools" / "diagnostics"))

from catalog import (  # noqa: E402
    CatalogError,
    extract_dtc_codes,
    normalize_hex,
    read_csv,
    read_jsonl,
    slug,
)


BOLT = "bolt://localhost:7687"
GRAPH_SCOPE = "vq-diagnostics-v1"
LEGACY_DATASET_IDS = ("obd2ools-d27c9a2",)
DTC_RE = re.compile(r"^[PBCU][0-9A-F]{4}$")

COLLECTION_FILES = {
    "documents": ("documents.csv", read_csv),
    "fragments": ("fragments.jsonl", read_jsonl),
    "dtc_definitions": ("dtc_definitions.csv", read_csv),
    "rom_dtc_descriptors": ("rom_dtc_descriptors.csv", read_csv),
    "diagnostic_parameters": ("diagnostic_parameters.csv", read_csv),
    "diagnostic_requests": ("diagnostic_requests.csv", read_csv),
    "request_parameters": ("request_parameters.csv", read_csv),
    "diagnostic_operations": ("diagnostic_operations.csv", read_csv),
    "can_frames": ("can_frames.csv", read_csv),
    "can_signals": ("can_signals.csv", read_csv),
    "can_bindings": ("can_bindings.csv", read_csv),
}

EXPECTED_KEYS = {
    "expected_documents": "documents",
    "expected_descriptors": "rom_dtc_descriptors",
    "expected_parameters": "diagnostic_parameters",
    "expected_requests": "diagnostic_requests",
    "expected_operations": "diagnostic_operations",
    "expected_can_frames": "can_frames",
    "expected_can_signals": "can_signals",
    "expected_can_bindings": "can_bindings",
    "expected_request_parameter_links": "request_parameters",
}

SECTION_KINDS = {
    "dtc_index",
    "dtc_detail",
    "data_monitor",
    "active_test",
    "work_support",
    "fail_safe",
    "can_signal_matrix",
    "terminal_reference",
    "freeze_frame",
    "srt",
    "service_06",
    "register_table",
}

BOOL_FIELDS = {
    "executable",
    "read_only",
    "signed",
    "manual_send",
    "dtc_index",
    "data_monitor",
    "active_test",
    "work_support",
    "fail_safe",
    "can_signal_matrix",
    "terminal_reference",
    "freeze_frame",
    "srt",
    "service_06",
}
INT_FIELDS = {
    "page_count",
    "pdf_page",
    "line_start",
    "line_end",
    "index",
    "dlc",
    "byte_offset",
    "byte_length",
    "bit_offset",
    "bit_length",
    "response_offset",
    "response_length",
    "first_byte",
    "model_year",
    "expected_documents",
    "expected_pages",
    "expected_ecm_dtc",
    "expected_can_signals",
    "expected_descriptors",
    "expected_parameters",
    "expected_requests",
    "expected_operations",
    "expected_can_frames",
    "expected_can_bindings",
    "expected_service_22",
    "expected_request_parameter_links",
}
FLOAT_FIELDS = {"factor", "addend", "period_ms"}
LIST_FIELDS = {"transmitters", "receivers", "dtc_codes"}

INDEXES = (
    ("SourcePack", "id"),
    ("SourceDocument", "id"),
    ("SourceDocument", "dataset_id"),
    ("SourceFragment", "id"),
    ("SourceFragment", "dataset_id"),
    ("VehicleVariant", "id"),
    ("Ecu", "id"),
    ("DtcCode", "code"),
    ("DtcDefinition", "id"),
    ("DtcDefinition", "dataset_id"),
    ("DiagnosticSection", "id"),
    ("RomDtcDescriptor", "id"),
    ("RomDtcDescriptor", "dataset_id"),
    ("DiagnosticParameter", "id"),
    ("ParameterDefinition", "id"),
    ("ParameterDefinition", "dataset_id"),
    ("DiagnosticRequest", "id"),
    ("DiagnosticRequest", "dataset_id"),
    ("DiagnosticService", "id"),
    ("DiagnosticOperation", "id"),
    ("DiagnosticOperation", "dataset_id"),
    ("CanSignal", "id"),
    ("CanSignalDefinition", "id"),
    ("CanFrame", "id"),
    ("CanFrameDefinition", "id"),
    ("CanSignalBinding", "id"),
)


@dataclass
class Dataset:
    directory: Path
    pack: dict[str, Any]
    collections: dict[str, list[dict[str, Any]]] = field(default_factory=dict)

    @property
    def id(self) -> str:
        return str(self.pack["id"])


@dataclass
class Catalog:
    datasets: list[Dataset]

    def all(self, collection: str) -> list[dict[str, Any]]:
        return [
            row
            for dataset in self.datasets
            for row in dataset.collections.get(collection, [])
        ]

    @property
    def dataset_ids(self) -> list[str]:
        return [dataset.id for dataset in self.datasets]


def load_catalog(root: Path = DIAGNOSTICS) -> Catalog:
    datasets = []
    for pack_path in sorted(root.rglob("source_pack.toml")):
        with pack_path.open("rb") as source:
            pack = tomllib.load(source)
        if not str(pack.get("id", "")).strip():
            raise CatalogError(f"{pack_path}: id is required")
        collections = {}
        for name, (filename, reader) in COLLECTION_FILES.items():
            path = pack_path.parent / filename
            collections[name] = reader(path) if path.is_file() else []
        datasets.append(Dataset(pack_path.parent, pack, collections))
    if not datasets:
        raise CatalogError(f"{root}: no source_pack.toml files found")
    catalog = Catalog(datasets)
    validate_catalog(catalog)
    return catalog


def require_unique_ids(rows: Iterable[dict[str, Any]], label: str) -> None:
    seen = {}
    for row in rows:
        identity = str(row.get("id", "")).strip()
        if not identity:
            raise CatalogError(f"{label}: row without id")
        if identity in seen:
            raise CatalogError(f"{label}: duplicate id {identity!r}")
        seen[identity] = True


def split_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return [item for item in str(value or "").split(";") if item]


def validate_expected(dataset: Dataset) -> None:
    for pack_key, collection in EXPECTED_KEYS.items():
        if pack_key not in dataset.pack:
            continue
        actual = len(dataset.collections[collection])
        expected = int(dataset.pack[pack_key])
        if actual != expected:
            raise CatalogError(
                f"{dataset.id}: {collection}={actual}, expected {expected}"
            )
    if "expected_service_22" in dataset.pack:
        actual = sum(
            str(row.get("service_id", "")).lower() == "0x22"
            for row in dataset.collections["diagnostic_requests"]
        )
        expected = int(dataset.pack["expected_service_22"])
        if actual != expected:
            raise CatalogError(
                f"{dataset.id}: service 0x22 requests={actual}, expected {expected}"
            )
    if "expected_ecm_dtc" in dataset.pack:
        rows = dataset.collections["dtc_definitions"]
        actual = len(
            {
                str(row["code"])
                for row in rows
                if str(row.get("ecu_id", "")).endswith(":ecm")
            }
        )
        expected = int(dataset.pack["expected_ecm_dtc"])
        if actual != expected:
            raise CatalogError(
                f"{dataset.id}: ECM DTC={actual}, expected {expected}"
            )
    expected_unique = dataset.pack.get("expected_unique_dtc")
    if isinstance(expected_unique, dict):
        rows = dataset.collections["rom_dtc_descriptors"]
        for rom, expected in expected_unique.items():
            actual = len(
                {str(row["code"]) for row in rows if row.get("rom") == rom}
            )
            if actual != int(expected):
                raise CatalogError(
                    f"{dataset.id}: {rom} unique DTC={actual}, expected {expected}"
                )


def validate_catalog(catalog: Catalog) -> None:
    require_unique_ids(
        [{"id": dataset.id} for dataset in catalog.datasets], "SourcePack"
    )
    for dataset in catalog.datasets:
        validate_expected(dataset)
        for collection, rows in dataset.collections.items():
            require_unique_ids(rows, f"{dataset.id}:{collection}")
            for row in rows:
                if str(row.get("dataset_id", "")) != dataset.id:
                    raise CatalogError(
                        f"{dataset.id}:{collection}:{row.get('id')}: "
                        f"dataset_id={row.get('dataset_id')!r}"
                    )

        documents = {
            str(row["id"]): row for row in dataset.collections["documents"]
        }
        fragments = {
            str(row["id"]): row for row in dataset.collections["fragments"]
        }
        for fragment in fragments.values():
            if str(fragment.get("document_id", "")) not in documents:
                raise CatalogError(
                    f"{fragment['id']}: unknown document {fragment.get('document_id')!r}"
                )
        for collection in (
            "dtc_definitions",
            "rom_dtc_descriptors",
            "diagnostic_parameters",
            "diagnostic_requests",
            "diagnostic_operations",
            "can_frames",
            "can_signals",
            "can_bindings",
        ):
            for row in dataset.collections[collection]:
                fragment_id = str(row.get("source_fragment_id", ""))
                if fragment_id not in fragments:
                    raise CatalogError(
                        f"{row['id']}: unknown source fragment {fragment_id!r}"
                    )

        requests = {
            str(row["id"]): row
            for row in dataset.collections["diagnostic_requests"]
        }
        parameters = {
            str(row["id"]): row
            for row in dataset.collections["diagnostic_parameters"]
        }
        for link in dataset.collections["request_parameters"]:
            if str(link.get("request_id", "")) not in requests:
                raise CatalogError(
                    f"{link['id']}: unknown request {link.get('request_id')!r}"
                )
            if str(link.get("parameter_id", "")) not in parameters:
                raise CatalogError(
                    f"{link['id']}: unknown parameter {link.get('parameter_id')!r}"
                )
            direction = str(link.get("direction", "receive")).strip().lower()
            if direction not in {"receive", "send"}:
                raise CatalogError(
                    f"{link['id']}: invalid parameter direction {direction!r}"
                )

        for row in dataset.collections["dtc_definitions"]:
            code = str(row.get("code", "")).upper()
            if not DTC_RE.fullmatch(code):
                raise CatalogError(f"{row['id']}: invalid DTC {code!r}")
        for row in dataset.collections["rom_dtc_descriptors"]:
            code = str(row.get("code", "")).upper()
            if not DTC_RE.fullmatch(code):
                raise CatalogError(f"{row['id']}: invalid DTC {code!r}")
        for fragment in fragments.values():
            for code in split_list(fragment.get("dtc_codes", [])):
                if not DTC_RE.fullmatch(code.upper()):
                    raise CatalogError(
                        f"{fragment['id']}: invalid referenced DTC {code!r}"
                    )
        for row in dataset.collections["diagnostic_requests"]:
            request = str(row.get("request_hex", "")).strip()
            if request:
                normalize_hex(request)
        for row in dataset.collections["diagnostic_operations"]:
            if str(row.get("executable", "")).lower() != "false":
                raise CatalogError(
                    f"{row['id']}: diagnostic operations must remain non-executable"
                )


def typed_value(field: str, value: Any) -> Any:
    if value is None or value == "":
        return None
    if isinstance(value, (bool, int, float, list)):
        return value
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    text = str(value)
    if field in LIST_FIELDS:
        return split_list(text)
    if field in BOOL_FIELDS:
        if text.lower() not in {"true", "false"}:
            raise CatalogError(f"{field}: invalid boolean {value!r}")
        return text.lower() == "true"
    if field in INT_FIELDS:
        try:
            return int(float(text))
        except ValueError:
            return text
    if field in FLOAT_FIELDS:
        try:
            return float(text)
        except ValueError:
            return text
    return text


def properties(row: dict[str, Any], **extra: Any) -> dict[str, Any]:
    result = {
        key: typed_value(key, value)
        for key, value in row.items()
        if not key.startswith("_") and typed_value(key, value) is not None
    }
    result.update(
        {
            key: typed_value(key, value)
            for key, value in extra.items()
            if typed_value(key, value) is not None
        }
    )
    return result


def canonical_parameter_id(row: dict[str, Any]) -> str:
    request = str(row.get("request_hex", "")).strip()
    if request:
        return f"diagnostic-parameter:request:{normalize_hex(request)}"
    protocol = str(row.get("protocol", "")).strip()
    external = str(row.get("external_id", "")).strip()
    if protocol and external:
        return f"diagnostic-parameter:{slug(protocol)}:{slug(external)}"
    name = str(row.get("name", "")).strip()
    if not name:
        raise CatalogError(f"{row.get('id')}: parameter name is empty")
    return f"diagnostic-parameter:semantic:{slug(name)}"


def canonical_signal_id(name: str) -> str:
    return f"can-signal:{slug(name)}"


def canonical_frame_id(row: dict[str, Any]) -> str:
    return ":".join(
        (
            "can-frame",
            slug(str(row.get("vehicle_id", "unknown"))),
            slug(str(row.get("bus", "unknown"))),
            slug(str(row["can_id"])),
        )
    )


def canonical_service_id(row: dict[str, Any]) -> str:
    protocol = str(row.get("protocol", "unknown"))
    service = str(row.get("service_id", "")).strip()
    if not service:
        request = str(row.get("request_hex", "")).strip()
        service = f"0x{normalize_hex(request)[:2].upper()}" if request else "unknown"
    return f"diagnostic-service:{slug(protocol)}:{slug(service)}"


def collect_projection(catalog: Catalog) -> dict[str, Any]:
    projection: dict[str, Any] = defaultdict(list)
    vehicle_ids = set()
    ecu_ids = set()

    for dataset in catalog.datasets:
        pack = properties(
            dataset.pack,
            dataset_id=dataset.id,
            graph_scope=GRAPH_SCOPE,
        )
        projection["SourcePack"].append(pack)
        vehicle = str(dataset.pack.get("vehicle_id", "")).strip()
        if vehicle:
            vehicle_ids.add(vehicle)

    for row in catalog.all("documents"):
        projection["SourceDocument"].append(
            properties(row, graph_scope=GRAPH_SCOPE)
        )
        projection["document_pack"].append(
            {"from": row["id"], "to": row["dataset_id"]}
        )

    for row in catalog.all("fragments"):
        fragment = properties(row, graph_scope=GRAPH_SCOPE)
        projection["SourceFragment"].append(fragment)
        projection["fragment_document"].append(
            {"from": row["id"], "to": row["document_id"]}
        )
        vehicle = str(row.get("vehicle_id", "")).strip()
        ecu = str(row.get("ecu_id", "")).strip()
        if vehicle:
            vehicle_ids.add(vehicle)
        if ecu:
            ecu_ids.add(ecu)
        for code in split_list(row.get("dtc_codes", [])):
            code = code.upper()
            projection["DtcCode"].append(
                {"code": code, "graph_scope": GRAPH_SCOPE}
            )
            projection["fragment_dtc"].append(
                {"from": row["id"], "to": code}
            )
        if str(row.get("kind", "")) in SECTION_KINDS:
            section_id = f"{row['id']}:section"
            projection["DiagnosticSection"].append(
                properties(
                    {
                        key: value
                        for key, value in row.items()
                        if key
                        in {
                            "dataset_id",
                            "kind",
                            "heading",
                            "ecu_id",
                            "vehicle_id",
                            "pdf_page",
                            "page_label",
                            "info_id",
                        }
                    },
                    id=section_id,
                    graph_scope=GRAPH_SCOPE,
                )
            )
            projection["claim_source"].append(
                {
                    "label": "DiagnosticSection",
                    "from": section_id,
                    "to": row["id"],
                    "source_prop": "section",
                }
            )
            for code in split_list(row.get("dtc_codes", [])):
                projection["section_dtc"].append(
                    {"from": section_id, "to": code.upper()}
                )

    for row in catalog.all("dtc_definitions"):
        code = str(row["code"]).upper()
        claim = properties(row, code=code, graph_scope=GRAPH_SCOPE)
        projection["DtcDefinition"].append(claim)
        projection["DtcCode"].append({"code": code, "graph_scope": GRAPH_SCOPE})
        projection["dtc_definition_code"].append(
            {"from": row["id"], "to": code}
        )
        projection["claim_source"].append(
            {
                "label": "DtcDefinition",
                "from": row["id"],
                "to": row["source_fragment_id"],
                "source_prop": "definition",
            }
        )
        vehicle = str(row.get("vehicle_id", "")).strip()
        ecu = str(row.get("ecu_id", "")).strip()
        if vehicle:
            vehicle_ids.add(vehicle)
            projection["claim_vehicle"].append(
                {"label": "DtcDefinition", "from": row["id"], "to": vehicle}
            )
        if ecu:
            ecu_ids.add(ecu)
            projection["claim_ecu"].append(
                {"label": "DtcDefinition", "from": row["id"], "to": ecu}
            )

    for row in catalog.all("rom_dtc_descriptors"):
        code = str(row["code"]).upper()
        claim = properties(row, code=code, graph_scope=GRAPH_SCOPE)
        projection["RomDtcDescriptor"].append(claim)
        projection["DtcCode"].append({"code": code, "graph_scope": GRAPH_SCOPE})
        projection["rom_descriptor_code"].append(
            {"from": row["id"], "to": code}
        )
        projection["rom_descriptor_rom"].append(
            {"from": row["id"], "to": row["rom"]}
        )
        projection["claim_source"].append(
            {
                "label": "RomDtcDescriptor",
                "from": row["id"],
                "to": row["source_fragment_id"],
                "source_prop": "descriptor",
            }
        )

    parameter_claim_to_canonical = {}
    request_parameters_by_dataset: dict[tuple[str, str], list[str]] = defaultdict(list)
    for row in catalog.all("diagnostic_parameters"):
        canonical_id = canonical_parameter_id(row)
        parameter_claim_to_canonical[str(row["id"])] = canonical_id
        claim = properties(row, canonical_id=canonical_id, graph_scope=GRAPH_SCOPE)
        projection["ParameterDefinition"].append(claim)
        projection["DiagnosticParameter"].append(
            {
                "id": canonical_id,
                "name": str(row.get("name", "")),
                "graph_scope": GRAPH_SCOPE,
            }
        )
        projection["parameter_definition"].append(
            {"from": row["id"], "to": canonical_id}
        )
        projection["claim_source"].append(
            {
                "label": "ParameterDefinition",
                "from": row["id"],
                "to": row["source_fragment_id"],
                "source_prop": "definition",
            }
        )
        request = str(row.get("request_hex", "")).strip()
        if request:
            request_parameters_by_dataset[
                (str(row["dataset_id"]), normalize_hex(request))
            ].append(canonical_id)
        ecu = str(row.get("ecu_id", "")).strip()
        if ecu:
            ecu_ids.add(ecu)
            projection["claim_ecu"].append(
                {"label": "ParameterDefinition", "from": row["id"], "to": ecu}
            )

    request_ids = set()
    for row in catalog.all("diagnostic_requests"):
        request_ids.add(str(row["id"]))
        service_id = canonical_service_id(row)
        projection["DiagnosticRequest"].append(
            properties(row, service_node_id=service_id, graph_scope=GRAPH_SCOPE)
        )
        projection["DiagnosticService"].append(
            {
                "id": service_id,
                "protocol": str(row.get("protocol", "")),
                "service_id": str(row.get("service_id", "")),
                "graph_scope": GRAPH_SCOPE,
            }
        )
        projection["request_service"].append(
            {"from": row["id"], "to": service_id}
        )
        projection["claim_source"].append(
            {
                "label": "DiagnosticRequest",
                "from": row["id"],
                "to": row["source_fragment_id"],
                "source_prop": "request",
            }
        )
        request = str(row.get("request_hex", "")).strip()
        if request:
            for canonical_id in request_parameters_by_dataset.get(
                (str(row["dataset_id"]), normalize_hex(request)), []
            ):
                projection["request_output_parameter"].append(
                    {"from": row["id"], "to": canonical_id, "direction": "receive"}
                )
        ecu = str(row.get("ecu_id", "")).strip()
        vehicle = str(row.get("vehicle_id", "")).strip()
        if ecu:
            ecu_ids.add(ecu)
            projection["claim_ecu"].append(
                {"label": "DiagnosticRequest", "from": row["id"], "to": ecu}
            )
        if vehicle:
            vehicle_ids.add(vehicle)
            projection["claim_vehicle"].append(
                {"label": "DiagnosticRequest", "from": row["id"], "to": vehicle}
            )

    for row in catalog.all("request_parameters"):
        canonical_id = parameter_claim_to_canonical[str(row["parameter_id"])]
        direction = str(row.get("direction", "receive")).strip().lower()
        collection = (
            "request_input_parameter"
            if direction == "send"
            else "request_output_parameter"
        )
        projection[collection].append(
            properties(
                row,
                **{
                    "from": row["request_id"],
                    "to": canonical_id,
                },
            )
        )

    for row in catalog.all("diagnostic_operations"):
        projection["DiagnosticOperation"].append(
            properties(row, graph_scope=GRAPH_SCOPE)
        )
        projection["claim_source"].append(
            {
                "label": "DiagnosticOperation",
                "from": row["id"],
                "to": row["source_fragment_id"],
                "source_prop": "operation",
            }
        )
        ecu = str(row.get("ecu_id", "")).strip()
        if ecu:
            ecu_ids.add(ecu)
            projection["claim_ecu"].append(
                {"label": "DiagnosticOperation", "from": row["id"], "to": ecu}
            )

    for row in catalog.all("can_frames"):
        canonical_id = canonical_frame_id(row)
        projection["CanFrameDefinition"].append(
            properties(row, canonical_id=canonical_id, graph_scope=GRAPH_SCOPE)
        )
        projection["CanFrame"].append(
            properties(
                {
                    "id": canonical_id,
                    "vehicle_id": row.get("vehicle_id", ""),
                    "bus": row.get("bus", ""),
                    "can_id": row.get("can_id", ""),
                },
                graph_scope=GRAPH_SCOPE,
            )
        )
        projection["frame_definition"].append(
            {"from": row["id"], "to": canonical_id}
        )
        projection["claim_source"].append(
            {
                "label": "CanFrameDefinition",
                "from": row["id"],
                "to": row["source_fragment_id"],
                "source_prop": "definition",
            }
        )
        vehicle = str(row.get("vehicle_id", "")).strip()
        if vehicle:
            vehicle_ids.add(vehicle)
            projection["claim_vehicle"].append(
                {"label": "CanFrameDefinition", "from": row["id"], "to": vehicle}
            )

    for row in catalog.all("can_signals"):
        signal_id = canonical_signal_id(str(row["name"]))
        projection["CanSignalDefinition"].append(
            properties(row, canonical_id=signal_id, graph_scope=GRAPH_SCOPE)
        )
        projection["CanSignal"].append(
            {"id": signal_id, "name": row["name"], "graph_scope": GRAPH_SCOPE}
        )
        projection["signal_definition"].append(
            {"from": row["id"], "to": signal_id}
        )
        projection["claim_source"].append(
            {
                "label": "CanSignalDefinition",
                "from": row["id"],
                "to": row["source_fragment_id"],
                "source_prop": "definition",
            }
        )
        vehicle = str(row.get("vehicle_id", "")).strip()
        if vehicle:
            vehicle_ids.add(vehicle)
        for transmitter in split_list(row.get("transmitters", [])):
            ecu = f"{vehicle}:{slug(transmitter)}"
            ecu_ids.add(ecu)
            projection["signal_transmitter"].append(
                {"from": row["id"], "to": ecu}
            )
        for receiver in split_list(row.get("receivers", [])):
            ecu = f"{vehicle}:{slug(receiver)}"
            ecu_ids.add(ecu)
            projection["signal_receiver"].append(
                {"from": row["id"], "to": ecu}
            )

    for row in catalog.all("can_bindings"):
        signal_id = canonical_signal_id(str(row["signal_name"]))
        frame_id = canonical_frame_id(row)
        projection["CanSignalBinding"].append(
            properties(
                row,
                signal_id=signal_id,
                frame_id=frame_id,
                graph_scope=GRAPH_SCOPE,
            )
        )
        projection["CanSignal"].append(
            {
                "id": signal_id,
                "name": row["signal_name"],
                "graph_scope": GRAPH_SCOPE,
            }
        )
        projection["CanFrame"].append(
            properties(
                {
                    "id": frame_id,
                    "vehicle_id": row.get("vehicle_id", ""),
                    "bus": row.get("bus", ""),
                    "can_id": row.get("can_id", ""),
                },
                graph_scope=GRAPH_SCOPE,
            )
        )
        projection["binding_signal"].append(
            {"from": row["id"], "to": signal_id}
        )
        projection["binding_frame"].append(
            {"from": row["id"], "to": frame_id}
        )
        projection["claim_source"].append(
            {
                "label": "CanSignalBinding",
                "from": row["id"],
                "to": row["source_fragment_id"],
                "source_prop": "binding",
            }
        )

    for vehicle in sorted(vehicle_ids):
        projection["VehicleVariant"].append(
            {"id": vehicle, "graph_scope": GRAPH_SCOPE}
        )
    for ecu in sorted(ecu_ids):
        vehicle = next(
            (
                candidate
                for candidate in sorted(vehicle_ids, key=len, reverse=True)
                if ecu == candidate or ecu.startswith(candidate + ":")
            ),
            "",
        )
        projection["Ecu"].append(
            {"id": ecu, "vehicle_id": vehicle, "graph_scope": GRAPH_SCOPE}
        )
        if vehicle:
            projection["ecu_vehicle"].append({"from": ecu, "to": vehicle})

    for label in (
        "DtcCode",
        "DiagnosticParameter",
        "DiagnosticService",
        "CanSignal",
        "CanFrame",
        "VehicleVariant",
        "Ecu",
    ):
        key = "code" if label == "DtcCode" else "id"
        merged = {}
        for row in projection[label]:
            identity = row[key]
            merged.setdefault(identity, {}).update(row)
        projection[label] = list(merged.values())

    for edge_name, rows in list(projection.items()):
        if edge_name in {
            "SourcePack",
            "SourceDocument",
            "SourceFragment",
            "VehicleVariant",
            "Ecu",
            "DtcCode",
            "DtcDefinition",
            "DiagnosticSection",
            "RomDtcDescriptor",
            "DiagnosticParameter",
            "ParameterDefinition",
            "DiagnosticRequest",
            "DiagnosticService",
            "DiagnosticOperation",
            "CanSignal",
            "CanSignalDefinition",
            "CanFrame",
            "CanFrameDefinition",
            "CanSignalBinding",
        }:
            continue
        unique = {}
        for row in rows:
            key = json.dumps(row, sort_keys=True, default=str)
            unique[key] = row
        projection[edge_name] = list(unique.values())
    return projection


def chunks(rows: list[dict[str, Any]], size: int = 500) -> Iterable[list[dict[str, Any]]]:
    for offset in range(0, len(rows), size):
        yield rows[offset : offset + size]


def merge_nodes(tx: Any, label: str, key: str, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    for batch in chunks(rows):
        tx.run(
            f"UNWIND $rows AS r MERGE (n:{label} {{{key}:r.{key}}}) SET n += r",
            rows=batch,
        ).consume()


def merge_claim_nodes(
    tx: Any, label: str, rows: list[dict[str, Any]]
) -> None:
    if not rows:
        return
    for batch in chunks(rows):
        tx.run(
            f"UNWIND $rows AS r "
            f"MERGE (n:{label}:Claim {{id:r.id}}) SET n += r",
            rows=batch,
        ).consume()


def merge_edges(
    tx: Any,
    from_label: str,
    to_label: str,
    relationship: str,
    rows: list[dict[str, Any]],
    *,
    from_key: str = "id",
    to_key: str = "id",
    properties_expr: str = "",
) -> None:
    if not rows:
        return
    setting = f" SET e += {properties_expr}" if properties_expr else ""
    for batch in chunks(rows):
        tx.run(
            f"UNWIND $rows AS r "
            f"MATCH (a:{from_label} {{{from_key}:r.from}}) "
            f"MATCH (b:{to_label} {{{to_key}:r.to}}) "
            f"MERGE (a)-[e:{relationship}]->(b){setting}",
            rows=batch,
        ).consume()


def create_indexes(session: Any) -> None:
    for label, prop in INDEXES:
        try:
            session.run(f"CREATE INDEX ON :{label}({prop})").consume()
        except Exception as error:
            message = str(error).lower()
            if "already exists" not in message and "exists" not in message:
                raise


def delete_graph_scope_claims(tx: Any) -> None:
    # Static firmware bindings rest on source-specific diagnostic claims. A
    # corpus replacement invalidates those edges, so remove the dependent
    # projection instead of leaving apparently valid orphan claims. Per-ROM
    # ingest recreates it after this global loader completes.
    tx.run("MATCH (b:DiagnosticBinding) DETACH DELETE b").consume()
    tx.run(
        "MATCH (n) "
        "WHERE n.graph_scope = $scope AND n.dataset_id IS NOT NULL "
        "DETACH DELETE n",
        scope=GRAPH_SCOPE,
    ).consume()
    tx.run(
        "MATCH (n) WHERE n.dataset_id IN $dataset_ids DETACH DELETE n",
        dataset_ids=list(LEGACY_DATASET_IDS),
    ).consume()


def write_projection(tx: Any, projection: dict[str, Any]) -> None:
    merge_nodes(tx, "SourcePack", "id", projection["SourcePack"])
    merge_nodes(tx, "SourceDocument", "id", projection["SourceDocument"])
    merge_nodes(tx, "SourceFragment", "id", projection["SourceFragment"])
    merge_nodes(tx, "VehicleVariant", "id", projection["VehicleVariant"])
    merge_nodes(tx, "Ecu", "id", projection["Ecu"])
    merge_nodes(tx, "DtcCode", "code", projection["DtcCode"])
    merge_nodes(tx, "DiagnosticParameter", "id", projection["DiagnosticParameter"])
    merge_nodes(tx, "DiagnosticService", "id", projection["DiagnosticService"])
    merge_nodes(tx, "CanSignal", "id", projection["CanSignal"])
    merge_nodes(tx, "CanFrame", "id", projection["CanFrame"])
    for label in (
        "DtcDefinition",
        "DiagnosticSection",
        "RomDtcDescriptor",
        "ParameterDefinition",
        "DiagnosticRequest",
        "DiagnosticOperation",
        "CanSignalDefinition",
        "CanFrameDefinition",
        "CanSignalBinding",
    ):
        merge_claim_nodes(tx, label, projection[label])

    merge_edges(
        tx, "SourceDocument", "SourcePack", "IN_PACK", projection["document_pack"]
    )
    merge_edges(
        tx,
        "SourceFragment",
        "SourceDocument",
        "IN_DOCUMENT",
        projection["fragment_document"],
    )
    merge_edges(
        tx,
        "SourceFragment",
        "DtcCode",
        "DESCRIBES_DTC",
        projection["fragment_dtc"],
        to_key="code",
    )
    merge_edges(
        tx,
        "DiagnosticSection",
        "DtcCode",
        "DESCRIBES_DTC",
        projection["section_dtc"],
        to_key="code",
    )
    merge_edges(
        tx,
        "DtcDefinition",
        "DtcCode",
        "DEFINES",
        projection["dtc_definition_code"],
        to_key="code",
    )
    merge_edges(
        tx,
        "RomDtcDescriptor",
        "DtcCode",
        "ENCODES",
        projection["rom_descriptor_code"],
        to_key="code",
    )
    for batch in chunks(projection["rom_descriptor_rom"]):
        tx.run(
            "UNWIND $rows AS r "
            "MATCH (d:RomDtcDescriptor {id:r.from}) "
            "MERGE (rom:Rom {id:r.to}) "
            "MERGE (d)-[:IN_ROM]->(rom) "
            "MERGE (rom)-[:CONTAINS]->(d)",
            rows=batch,
        ).consume()
    merge_edges(
        tx,
        "ParameterDefinition",
        "DiagnosticParameter",
        "DEFINES",
        projection["parameter_definition"],
    )
    merge_edges(
        tx,
        "DiagnosticRequest",
        "DiagnosticService",
        "USES_SERVICE",
        projection["request_service"],
    )
    merge_edges(
        tx,
        "DiagnosticRequest",
        "DiagnosticParameter",
        "RETURNS",
        projection["request_output_parameter"],
        properties_expr=(
            "{first_byte:r.first_byte, bit_offset:r.bit_offset, "
            "byte_order:r.byte_order}"
        ),
    )
    merge_edges(
        tx,
        "DiagnosticRequest",
        "DiagnosticParameter",
        "SENDS",
        projection["request_input_parameter"],
        properties_expr=(
            "{first_byte:r.first_byte, bit_offset:r.bit_offset, "
            "byte_order:r.byte_order}"
        ),
    )
    merge_edges(
        tx,
        "CanFrameDefinition",
        "CanFrame",
        "DEFINES",
        projection["frame_definition"],
    )
    merge_edges(
        tx,
        "CanSignalDefinition",
        "CanSignal",
        "DEFINES",
        projection["signal_definition"],
    )
    merge_edges(
        tx,
        "CanSignalDefinition",
        "Ecu",
        "TRANSMITTER",
        projection["signal_transmitter"],
    )
    merge_edges(
        tx,
        "CanSignalDefinition",
        "Ecu",
        "RECEIVER",
        projection["signal_receiver"],
    )
    merge_edges(
        tx,
        "CanSignalBinding",
        "CanSignal",
        "BINDS_SIGNAL",
        projection["binding_signal"],
    )
    merge_edges(
        tx,
        "CanSignalBinding",
        "CanFrame",
        "BINDS_FRAME",
        projection["binding_frame"],
    )
    merge_edges(tx, "Ecu", "VehicleVariant", "ON_VEHICLE", projection["ecu_vehicle"])

    for label in (
        "DtcDefinition",
        "DiagnosticSection",
        "RomDtcDescriptor",
        "ParameterDefinition",
        "DiagnosticRequest",
        "DiagnosticOperation",
        "CanSignalDefinition",
        "CanFrameDefinition",
        "CanSignalBinding",
    ):
        rows = [row for row in projection["claim_source"] if row["label"] == label]
        merge_edges(
            tx,
            label,
            "SourceFragment",
            "RESTS_ON",
            rows,
            properties_expr="{role:'source', source_prop:r.source_prop}",
        )
    for label in (
        "DtcDefinition",
        "ParameterDefinition",
        "DiagnosticRequest",
        "DiagnosticOperation",
    ):
        rows = [row for row in projection["claim_ecu"] if row["label"] == label]
        merge_edges(tx, label, "Ecu", "FOR_ECU", rows)
    for label in ("DtcDefinition", "DiagnosticRequest", "CanFrameDefinition"):
        rows = [row for row in projection["claim_vehicle"] if row["label"] == label]
        merge_edges(tx, label, "VehicleVariant", "APPLIES_TO", rows)


def cleanup_orphans(tx: Any) -> None:
    statements = (
        "MATCH (n:DiagnosticParameter {graph_scope:$scope}) "
        "WHERE NOT ()-[:DEFINES]->(n) "
        "AND NOT ()-[:RETURNS|SENDS]->(n) DETACH DELETE n",
        "MATCH (n:DtcCode {graph_scope:$scope}) "
        "WHERE NOT ()-[:DEFINES|ENCODES|DESCRIBES_DTC]->(n) DETACH DELETE n",
        "MATCH (n:DiagnosticService {graph_scope:$scope}) "
        "WHERE NOT ()-[:USES_SERVICE]->(n) DETACH DELETE n",
        "MATCH (n:CanSignal {graph_scope:$scope}) "
        "WHERE NOT ()-[:DEFINES|BINDS_SIGNAL]->(n) DETACH DELETE n",
        "MATCH (n:CanFrame {graph_scope:$scope}) "
        "WHERE NOT ()-[:DEFINES|BINDS_FRAME]->(n) DETACH DELETE n",
        "MATCH (n:Ecu {graph_scope:$scope}) "
        "WHERE NOT (n)--() DETACH DELETE n",
        "MATCH (n:VehicleVariant {graph_scope:$scope}) "
        "WHERE NOT (n)--() DETACH DELETE n",
    )
    for statement in statements:
        tx.run(statement, scope=GRAPH_SCOPE).consume()


def projection_counts(projection: dict[str, Any]) -> dict[str, int]:
    labels = (
        "SourcePack",
        "SourceDocument",
        "SourceFragment",
        "DtcCode",
        "DtcDefinition",
        "RomDtcDescriptor",
        "DiagnosticParameter",
        "ParameterDefinition",
        "DiagnosticRequest",
        "DiagnosticOperation",
        "CanSignal",
        "CanSignalDefinition",
        "CanFrame",
        "CanFrameDefinition",
        "CanSignalBinding",
    )
    return {label: len(projection[label]) for label in labels}


def audit(runner: Any, expected: dict[str, int]) -> None:
    mismatches = []
    for label, count in expected.items():
        key = "code" if label == "DtcCode" else "id"
        actual = runner.run(
            f"MATCH (n:{label}) "
            "WHERE n.graph_scope = $scope "
            f"RETURN count(DISTINCT n.{key}) AS count",
            scope=GRAPH_SCOPE,
        ).single()["count"]
        if actual != count:
            mismatches.append(f"{label}: graph={actual}, input={count}")
    if mismatches:
        raise CatalogError("Memgraph audit failed: " + "; ".join(mismatches))


def replace_projection(
    tx: Any, projection: dict[str, Any], counts: dict[str, int]
) -> None:
    delete_graph_scope_claims(tx)
    write_projection(tx, projection)
    cleanup_orphans(tx)
    audit(tx, counts)


def format_counts(counts: dict[str, int]) -> str:
    return ", ".join(f"{label}={count}" for label, count in counts.items())


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--root", type=Path, default=DIAGNOSTICS)
    result.add_argument("--bolt", default=BOLT)
    result.add_argument("--dry-run", action="store_true")
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        catalog = load_catalog(args.root)
        projection = collect_projection(catalog)
    except (OSError, ValueError, CatalogError, tomllib.TOMLDecodeError) as error:
        print(error, file=sys.stderr)
        return 1
    counts = projection_counts(projection)
    print(
        f"Preflight: datasets={len(catalog.datasets)} "
        f"({', '.join(catalog.dataset_ids)})"
    )
    print("Projection: " + format_counts(counts))
    if args.dry_run:
        return 0

    try:
        from neo4j import GraphDatabase
    except ImportError:
        print(
            "neo4j package is required; run with "
            "`uv run python tools/memgraph/ingest_diagnostics.py`",
            file=sys.stderr,
        )
        return 1
    driver = GraphDatabase.driver(args.bolt, auth=("", ""))
    try:
        with driver.session() as session:
            create_indexes(session)
            with session.begin_transaction() as tx:
                replace_projection(tx, projection, counts)
                tx.commit()
    except Exception as error:
        print(f"Memgraph ingest failed: {error}", file=sys.stderr)
        return 1
    finally:
        driver.close()
    print("Memgraph: diagnostic projection committed and audited")
    return 0


if __name__ == "__main__":
    sys.exit(main())
