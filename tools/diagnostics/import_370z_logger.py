#!/usr/bin/env python3
"""Normalize the pinned 370Z-CAN-Logger source tree into diagnostic catalogs."""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from check_projection import check as check_projection
from pathlib import Path
from typing import Iterable

from catalog import (
    CatalogError,
    REFS,
    ROOT,
    keyed_slug,
    normalize_hex,
    require_pinned_git_tree,
    require_pinned_snapshot,
    require_unique,
    sha256_file,
    sha256_text,
    slug,
    write_csv,
    write_jsonl,
)


DATASET_ID = "370z-can-logger-2025-07-05"
REVISION = "2decbc957523ee46dd39b3e3a7594e23ad7eee97"
SOURCE_URL = "https://github.com/TihanPelser/370Z-CAN-Logger"
SOURCE_LICENSE = "MIT"
VEHICLE_ID = "nissan-370z-z34-community"
ECU_ID = f"{VEHICLE_ID}:ecm"
DEFAULT_OUTPUT = REFS / "public" / "370z-can-logger"
DEFAULT_SOURCE_ROOT = ROOT / "refs" / "diagnostic-sources" / "370z-can-logger"

SOURCE_FILES = (
    "candata/consult.csv",
    "candata/extended_pids.csv",
    "candata/standard_pids.csv",
    "candata/370z_can.csv",
    "candata/ids.csv",
    "candata/signals.csv",
    "candata/more_signals.csv",
    "can_decoder_cli.py",
    "LICENSE",
)

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
CAN_FRAME_FIELDS = (
    "id",
    "dataset_id",
    "vehicle_id",
    "bus",
    "can_id",
    "dlc",
    "period_ms",
    "source",
    "function",
    "interpretation",
    "verification_status",
    "applicability_status",
    "source_fragment_id",
)
CAN_SIGNAL_FIELDS = (
    "id",
    "dataset_id",
    "name",
    "vehicle_id",
    "bus",
    "transmitters",
    "receivers",
    "can_id",
    "dlc",
    "period_ms",
    "start_bit",
    "bit_length",
    "byte_order",
    "signed",
    "factor",
    "addend",
    "unit",
    "binding_status",
    "source_fragment_id",
)
CAN_BINDING_FIELDS = (
    "id",
    "dataset_id",
    "vehicle_id",
    "bus",
    "can_id",
    "signal_name",
    "byte_offset",
    "byte_length",
    "bit_offset",
    "bit_length",
    "byte_order",
    "signed",
    "factor",
    "addend",
    "unit",
    "formula",
    "value_map",
    "verification_status",
    "applicability_status",
    "source_fragment_id",
)


def document_id(relative_path: str) -> str:
    return f"{DATASET_ID}:{slug(relative_path)}"


def source_fragment(
    relative_path: str,
    line_start: int,
    line_end: int,
    kind: str,
    text: str,
    heading: str = "",
) -> dict[str, object]:
    fragment = {
        "id": (
            f"{document_id(relative_path)}:"
            f"l{line_start:04d}-l{line_end:04d}:{slug(kind)}"
        ),
        "dataset_id": DATASET_ID,
        "document_id": document_id(relative_path),
        "line_start": line_start,
        "line_end": line_end,
        "kind": kind,
        "heading": heading,
        "ecu_id": ECU_ID,
        "vehicle_id": VEHICLE_ID,
        "text_sha256": sha256_text(text),
        "text": text,
    }
    return fragment


def read_csv_rows(
    source_root: Path, relative_path: str, *, delimiter: str = ","
) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
    path = source_root / relative_path
    rows: list[dict[str, str]] = []
    fragments: list[dict[str, object]] = []
    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source, delimiter=delimiter)
        previous_line = 1
        for row in reader:
            start = previous_line + 1
            end = reader.line_num
            previous_line = end
            normalized = {
                str(key): (value or "").strip()
                for key, value in row.items()
                if key is not None
            }
            text = json.dumps(normalized, ensure_ascii=False, sort_keys=True)
            fragment = source_fragment(
                relative_path,
                start,
                end,
                f"source_row_{Path(relative_path).stem}",
                text,
                next(iter(normalized.values()), ""),
            )
            normalized["_fragment_id"] = str(fragment["id"])
            normalized["_line_start"] = str(start)
            normalized["_line_end"] = str(end)
            rows.append(normalized)
            fragments.append(fragment)
    return rows, fragments


def parse_float(value: str) -> str:
    text = value.strip().lower()
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    return match.group(0) if match else ""


def parse_period_ms(value: str) -> str:
    match = re.search(r"(\d+(?:\.\d+)?)\s*ms", value, re.IGNORECASE)
    return match.group(1) if match else ""


def clean_can_id(value: str) -> str:
    compact = value.strip().upper()
    if compact.startswith("0X"):
        compact = compact[2:]
    if not re.fullmatch(r"[0-9A-F]{1,8}", compact):
        raise CatalogError(f"invalid CAN identifier: {value!r}")
    return f"0x{int(compact, 16):03X}"


def build_documents(source_root: Path) -> list[dict[str, object]]:
    documents = []
    for relative_path in SOURCE_FILES:
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
                "license": SOURCE_LICENSE,
                "applicability_status": "homologous_community",
            }
        )
    return documents


def parameter_row(
    *,
    fragment_id: str,
    name: str,
    unit: str = "",
    description: str = "",
    remarks: str = "",
    protocol: str,
    external_id: str = "",
    request_hex: str = "",
    response_length: str = "",
    formula: str = "",
    verification_status: str = "community_defined",
) -> dict[str, object]:
    identity = external_id or name
    return {
        "id": f"{fragment_id}:parameter:{keyed_slug(identity)}",
        "dataset_id": DATASET_ID,
        "name": name,
        "ecu_id": ECU_ID,
        "unit": unit,
        "description": description,
        "remarks": remarks,
        "protocol": protocol,
        "external_id": external_id,
        "request_hex": request_hex,
        "response_offset": "",
        "response_length": response_length,
        "byte_order": "",
        "signed": "",
        "factor": "",
        "addend": "",
        "formula": formula,
        "applicability_status": "homologous_community",
        "verification_status": verification_status,
        "source_fragment_id": fragment_id,
    }


def request_row(
    *,
    fragment_id: str,
    protocol: str,
    service_id: str,
    identifier: str,
    request_hex: str,
    response_length: str,
) -> dict[str, object]:
    return {
        "id": f"{fragment_id}:request:{normalize_hex(request_hex)}",
        "dataset_id": DATASET_ID,
        "protocol": protocol,
        "service_id": service_id,
        "identifier": identifier,
        "request_hex": normalize_hex(request_hex),
        "response_length": response_length,
        "read_only": True,
        "operation_kind": "data_read",
        "ecu_id": ECU_ID,
        "vehicle_id": VEHICLE_ID,
        "applicability_status": "homologous_community",
        "verification_status": "community_reported",
        "source_fragment_id": fragment_id,
    }


def build_parameters_and_requests(
    source_root: Path,
) -> tuple[
    list[dict[str, object]],
    list[dict[str, object]],
    list[dict[str, object]],
]:
    parameters: list[dict[str, object]] = []
    requests: list[dict[str, object]] = []
    fragments: list[dict[str, object]] = []

    consult_rows, source_fragments = read_csv_rows(
        source_root, "candata/consult.csv"
    )
    fragments.extend(source_fragments)
    for row in consult_rows:
        name = row["Monitor Item"]
        if not name:
            continue
        remarks = "; ".join(
            value
            for value in (
                row.get("Condition", ""),
                row.get("Values/Status", ""),
                row.get("Notes", ""),
            )
            if value
        )
        parameters.append(
            parameter_row(
                fragment_id=row["_fragment_id"],
                name=name,
                unit=row.get("Units", ""),
                description=row.get("Description", ""),
                remarks=remarks,
                protocol="consult",
                external_id=row.get("#", ""),
                verification_status="community_transcribed",
            )
        )

    extended_rows, source_fragments = read_csv_rows(
        source_root, "candata/extended_pids.csv"
    )
    fragments.extend(source_fragments)
    for row in extended_rows:
        pid = row["PID"].upper()
        if not re.fullmatch(r"[0-9A-F]{4}", pid):
            continue
        request = f"22{pid}"
        name = row.get("Name", "") or f"Unknown CID 0x{pid}"
        notes = "; ".join(
            value
            for value in (
                row.get("Notes:", ""),
                row.get("Unnamed: 11", ""),
            )
            if value
        )
        parameters.append(
            parameter_row(
                fragment_id=row["_fragment_id"],
                name=name,
                description=row.get("Description", ""),
                remarks=notes,
                protocol="iso-14229-service-22",
                external_id=f"0x{pid}",
                request_hex=request,
                response_length=parse_float(row.get("Bytes", "")),
                formula=row.get("Description", ""),
                verification_status="community_measured",
            )
        )
        requests.append(
            request_row(
                fragment_id=row["_fragment_id"],
                protocol="iso-14229-service-22",
                service_id="0x22",
                identifier=f"0x{pid}",
                request_hex=request,
                response_length=parse_float(row.get("Bytes", "")),
            )
        )

    standard_rows, source_fragments = read_csv_rows(
        source_root, "candata/standard_pids.csv"
    )
    fragments.extend(source_fragments)
    for row in standard_rows:
        pid = row["PID"].upper()
        if not re.fullmatch(r"[0-9A-F]{2}", pid):
            continue
        request = f"01{pid}"
        description = row.get("Description", "")
        notes = "; ".join(
            value
            for value in (
                row.get("Min value", ""),
                row.get("Max value", ""),
                row.get("Notes:", ""),
                row.get("Unnamed: 9", ""),
            )
            if value
        )
        parameters.append(
            parameter_row(
                fragment_id=row["_fragment_id"],
                name=description or f"SAE PID 0x{pid}",
                unit=row.get("Units", ""),
                description=description,
                remarks=notes,
                protocol="sae-j1979-service-01",
                external_id=f"0x{pid}",
                request_hex=request,
                response_length=parse_float(row.get("Bytes", "")),
                formula=row.get("Formula", ""),
                verification_status="standard_definition",
            )
        )
        requests.append(
            request_row(
                fragment_id=row["_fragment_id"],
                protocol="sae-j1979-service-01",
                service_id="0x01",
                identifier=f"0x{pid}",
                request_hex=request,
                response_length=parse_float(row.get("Bytes", "")),
            )
        )

    return parameters, requests, fragments


def build_can_frames(
    source_root: Path,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    frames: list[dict[str, object]] = []
    fragments: list[dict[str, object]] = []

    id_rows, source_fragments = read_csv_rows(source_root, "candata/ids.csv")
    fragments.extend(source_fragments)
    for row in id_rows:
        raw_id = row.get("CAN IDs", "")
        if not re.fullmatch(r"[0-9A-Fa-f]{1,8}", raw_id):
            continue
        can_id = clean_can_id(raw_id)
        fragment_id = row["_fragment_id"]
        frames.append(
            {
                "id": f"{fragment_id}:frame:{can_id.lower()}",
                "dataset_id": DATASET_ID,
                "vehicle_id": VEHICLE_ID,
                "bus": "z34-primary-can",
                "can_id": can_id,
                "dlc": parse_float(row.get("Unnamed: 1", "")),
                "period_ms": "",
                "source": "",
                "function": "",
                "interpretation": row.get("NOTES", ""),
                "verification_status": "community_observed",
                "applicability_status": "homologous_community",
                "source_fragment_id": fragment_id,
            }
        )

    description_rows, source_fragments = read_csv_rows(
        source_root, "candata/370z_can.csv", delimiter=";"
    )
    fragments.extend(source_fragments)
    for row in description_rows:
        can_id = clean_can_id(row["CAN ID (Hexadecimal)"])
        fragment_id = row["_fragment_id"]
        frames.append(
            {
                "id": f"{fragment_id}:frame:{can_id.lower()}",
                "dataset_id": DATASET_ID,
                "vehicle_id": VEHICLE_ID,
                "bus": "z34-primary-can",
                "can_id": can_id,
                "dlc": "",
                "period_ms": parse_period_ms(row.get("Frequency/Interval", "")),
                "source": row.get("Source/Function (Inferred)", ""),
                "function": row.get("Source/Function (Inferred)", ""),
                "interpretation": row.get(
                    "Data Bytes (Interpretation of Key Bytes)", ""
                ),
                "verification_status": "community_inferred",
                "applicability_status": "homologous_community",
                "source_fragment_id": fragment_id,
            }
        )
    return frames, fragments


def build_can_signals(
    source_root: Path,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    signals: list[dict[str, object]] = []
    fragments: list[dict[str, object]] = []
    for relative_path in ("candata/signals.csv", "candata/more_signals.csv"):
        rows, source_fragments = read_csv_rows(source_root, relative_path)
        fragments.extend(source_fragments)
        for row in rows:
            name = row.get("Signal name/Connecting unit", "")
            if not name:
                continue
            transmitters = []
            receivers = []
            for column, value in row.items():
                if column.startswith("_") or column.startswith("Unnamed:"):
                    continue
                normalized = value.upper().strip()
                ecu = column.rstrip("*0123456789").strip()
                if normalized == "T":
                    transmitters.append(ecu)
                elif normalized == "R":
                    receivers.append(ecu)
            if not transmitters and not receivers:
                continue
            fragment_id = row["_fragment_id"]
            signals.append(
                {
                    "id": f"{fragment_id}:signal:{keyed_slug(name)}",
                    "dataset_id": DATASET_ID,
                    "name": name,
                    "vehicle_id": VEHICLE_ID,
                    "bus": "z34-primary-can",
                    "transmitters": sorted(transmitters),
                    "receivers": sorted(receivers),
                    "can_id": "",
                    "dlc": "",
                    "period_ms": "",
                    "start_bit": "",
                    "bit_length": "",
                    "byte_order": "",
                    "signed": "",
                    "factor": "",
                    "addend": "",
                    "unit": "",
                    "binding_status": "unknown",
                    "source_fragment_id": fragment_id,
                }
            )
    return signals, fragments


def decoder_fragments(
    source_root: Path,
) -> tuple[dict[str, dict[str, object]], list[dict[str, object]]]:
    relative_path = "can_decoder_cli.py"
    lines = (source_root / relative_path).read_text(encoding="utf-8").splitlines()
    starts = []
    for number, line in enumerate(lines, 1):
        match = re.search(r"\b(?:if|elif) can_id == (0x[0-9A-Fa-f]+)", line)
        if match:
            starts.append((number, clean_can_id(match.group(1))))
    result: dict[str, dict[str, object]] = {}
    fragments = []
    for index, (start, can_id) in enumerate(starts):
        end = starts[index + 1][0] - 1 if index + 1 < len(starts) else start
        if index + 1 == len(starts):
            for number in range(start + 1, len(lines) + 1):
                if re.match(r"\s*return decoded\s*$", lines[number - 1]):
                    end = number - 1
                    break
        text = "\n".join(lines[start - 1 : end]) + "\n"
        fragment = source_fragment(
            relative_path, start, end, "can_decoder", text, can_id
        )
        result[can_id] = fragment
        fragments.append(fragment)
    return result, fragments


def binding(
    fragments: dict[str, dict[str, object]],
    can_id: str,
    signal_name: str,
    byte_offset: int,
    byte_length: int,
    byte_order: str,
    signed: bool,
    factor: object,
    addend: object,
    unit: str,
    formula: str,
    *,
    value_map: str = "",
    approximate: bool = False,
) -> dict[str, object]:
    fragment_id = str(fragments[can_id]["id"])
    return {
        "id": f"{fragment_id}:binding:{keyed_slug(signal_name)}",
        "dataset_id": DATASET_ID,
        "vehicle_id": VEHICLE_ID,
        "bus": "z34-primary-can",
        "can_id": can_id,
        "signal_name": signal_name,
        "byte_offset": byte_offset,
        "byte_length": byte_length,
        "bit_offset": 0,
        "bit_length": byte_length * 8,
        "byte_order": byte_order,
        "signed": signed,
        "factor": factor,
        "addend": addend,
        "unit": unit,
        "formula": formula,
        "value_map": value_map,
        "verification_status": (
            "community_approximate" if approximate else "community_defined"
        ),
        "applicability_status": "homologous_community",
        "source_fragment_id": fragment_id,
    }


def build_can_bindings(
    source_root: Path,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    fragments, source_fragments = decoder_fragments(source_root)
    rows = [
        binding(
            fragments,
            "0x180",
            "Engine speed",
            0,
            2,
            "big",
            False,
            0.125,
            0,
            "rpm",
            "((A << 8) + B) / 8",
        ),
        binding(
            fragments,
            "0x180",
            "Throttle pedal position",
            5,
            1,
            "big",
            False,
            100 / 255,
            0,
            "%",
            "F / 255 * 100",
        ),
        binding(
            fragments,
            "0x1F9",
            "Engine speed",
            2,
            2,
            "big",
            False,
            0.125,
            0,
            "rpm",
            "((C << 8) + D) / 8",
        ),
        binding(
            fragments,
            "0x280",
            "Vehicle speed",
            4,
            2,
            "big",
            False,
            0.01,
            0,
            "km/h",
            "((E << 8) + F) / 100",
            approximate=True,
        ),
        binding(
            fragments,
            "0x002",
            "Steering angle",
            0,
            2,
            "little",
            True,
            0.1,
            0,
            "degree",
            "signed16((B << 8) + A) / 10",
        ),
        binding(
            fragments,
            "0x551",
            "Engine coolant temperature",
            0,
            1,
            "big",
            False,
            1,
            -40,
            "degC",
            "A - 40",
            approximate=True,
        ),
        binding(
            fragments,
            "0x551",
            "Cruise control set point",
            4,
            1,
            "big",
            False,
            1,
            0,
            "km/h",
            "E; zero means unavailable",
        ),
        binding(
            fragments,
            "0x551",
            "Cruise control status",
            5,
            1,
            "big",
            False,
            1,
            0,
            "",
            "F == 2",
            value_map="2=Active;other=Inactive",
        ),
        binding(
            fragments,
            "0x216",
            "Clutch position",
            0,
            1,
            "big",
            False,
            1,
            0,
            "",
            "A",
            value_map="100=Engaged;108=Pressed",
        ),
        binding(
            fragments,
            "0x421",
            "Gear position",
            0,
            1,
            "big",
            False,
            1,
            0,
            "",
            "A",
            value_map="16=Reverse;24=Neutral;128=First",
        ),
    ]
    return rows, source_fragments


def build(source_root: Path) -> dict[str, list[dict[str, object]]]:
    if source_root.resolve() == DEFAULT_SOURCE_ROOT.resolve():
        require_pinned_snapshot(
            source_root, REVISION, SOURCE_URL, SOURCE_FILES, expected_license=SOURCE_LICENSE
        )
    else:
        require_pinned_git_tree(source_root, REVISION, SOURCE_FILES)
    documents = build_documents(source_root)
    parameters, requests, parameter_fragments = build_parameters_and_requests(
        source_root
    )
    frames, frame_fragments = build_can_frames(source_root)
    signals, signal_fragments = build_can_signals(source_root)
    bindings, decoder_source_fragments = build_can_bindings(source_root)
    fragments = (
        parameter_fragments
        + frame_fragments
        + signal_fragments
        + decoder_source_fragments
    )

    for rows, key in (
        (documents, ("id",)),
        (fragments, ("id",)),
        (parameters, ("id",)),
        (requests, ("id",)),
        (frames, ("id",)),
        (signals, ("id",)),
        (bindings, ("id",)),
    ):
        require_unique(rows, key)
    fragment_ids = {str(row["id"]) for row in fragments}
    for collection in (parameters, requests, frames, signals, bindings):
        for row in collection:
            if row["source_fragment_id"] not in fragment_ids:
                raise CatalogError(
                    f"{row['id']}: missing fragment {row['source_fragment_id']}"
                )
    return {
        "documents": documents,
        "fragments": fragments,
        "diagnostic_parameters": parameters,
        "diagnostic_requests": requests,
        "can_frames": frames,
        "can_signals": signals,
        "can_bindings": bindings,
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
    write_csv(output / "can_frames.csv", CAN_FRAME_FIELDS, catalog["can_frames"])
    write_csv(output / "can_signals.csv", CAN_SIGNAL_FIELDS, catalog["can_signals"])
    write_csv(
        output / "can_bindings.csv", CAN_BINDING_FIELDS, catalog["can_bindings"]
    )


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("source_root", type=Path, nargs="?", default=DEFAULT_SOURCE_ROOT)
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
    except (OSError, KeyError, CatalogError) as error:
        print(error, file=sys.stderr)
        return 1
    print(
        "370Z-CAN-Logger: "
        f"documents={len(catalog['documents'])}, "
        f"fragments={len(catalog['fragments'])}, "
        f"parameters={len(catalog['diagnostic_parameters'])}, "
        f"requests={len(catalog['diagnostic_requests'])}, "
        f"can_frames={len(catalog['can_frames'])}, "
        f"can_signals={len(catalog['can_signals'])}, "
        f"can_bindings={len(catalog['can_bindings'])}"
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
