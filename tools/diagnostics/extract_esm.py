#!/usr/bin/env python3
"""Extract diagnostic inventories from a Nissan factory ESM source pack."""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
import tomllib
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from catalog import (
    CatalogError,
    REFS,
    ROOT,
    extract_dtc_codes,
    keyed_slug,
    require_unique,
    sha256_file,
    sha256_text,
    slug,
    write_csv,
    write_jsonl,
)


DEFAULT_PACK = REFS / "nissan-esm-2007-g35-sedan" / "source_pack.toml"
DATASET_ID = "nissan-esm-2007-g35-sedan-v1"
VEHICLE_ID = "infiniti-g35-sedan-2007-usdm-vq35hr"
EXPECTED_DOCUMENTS = 29


@dataclass(frozen=True)
class SourcePack:
    """Dataset identity and retained-document count for one ESM corpus."""

    path: Path
    dataset_id: str
    vehicle_id: str
    expected_documents: int

    @property
    def output(self) -> Path:
        return self.path.parent


def load_pack(path: Path) -> SourcePack:
    with path.open("rb") as source:
        raw = tomllib.load(source)
    missing = [
        key
        for key in ("id", "vehicle_id", "expected_documents")
        if key not in raw
    ]
    if missing:
        raise CatalogError(f"{path}: source pack omits {', '.join(missing)}")
    return SourcePack(
        path=path,
        dataset_id=str(raw["id"]),
        vehicle_id=str(raw["vehicle_id"]),
        expected_documents=int(raw["expected_documents"]),
    )

DOCUMENT_FIELDS = (
    "id",
    "dataset_id",
    "filename",
    "title",
    "section_code",
    "sha256",
    "page_count",
    "source_path",
)
DISCOVERY_FIELDS = (
    "document_id",
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
    "fragments",
    "dtc_tokens",
)
DTC_FIELDS = (
    "id",
    "dataset_id",
    "code",
    "native_code",
    "title",
    "ecu_id",
    "vehicle_id",
    "applicability_status",
    "definition_kind",
    "source_fragment_id",
)
PARAMETER_FIELDS = (
    "id",
    "dataset_id",
    "name",
    "ecu_id",
    "unit",
    "description",
    "conditions",
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
CAN_FIELDS = (
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
UNPARSED_FIELDS = (
    "id",
    "dataset_id",
    "document_id",
    "pdf_page",
    "page_label",
    "kind",
    "reason",
    "source_fragment_id",
)

KIND_PATTERNS = {
    "dtc_index": re.compile(r"(?mi)^\s*DTC Index\s*(?:INFOID|$)"),
    "data_monitor": re.compile(
        r"(?mi)^\s*(?:DATA MONITOR MODE|DATA MONITOR)\s*"
        r"(?:[A-Z]{1,4}\s*)?(?:INFOID|$)"
    ),
    "active_test": re.compile(
        r"(?mi)^\s*(?:ACTIVE TEST MODE|ACTIVE TEST)\s*"
        r"(?:[A-Z]{1,4}\s*)?(?:INFOID|$)"
    ),
    "work_support": re.compile(
        r"(?mi)^\s*(?:DTC )?(?:WORK SUPPORT MODE|WORK SUPPORT)\s*"
        r"(?:[A-Z]{1,4}\s*)?(?:INFOID|$)"
    ),
    "fail_safe": re.compile(r"(?mi)^\s*Fail[- ]?Safe\s*(?:INFOID|$)"),
    "can_signal_matrix": re.compile(
        r"(?mi)^\s*CAN Communication Signal Chart\s*(?:INFOID|$)"
    ),
    "terminal_reference": re.compile(
        r"(?mi)^\s*(?:ECU DIAGNOSIS|ECM Terminals and Reference Value|"
        r"Reference Value)\s*(?:INFOID|$)"
    ),
    "freeze_frame": re.compile(
        r"(?mi)^\s*(?:DTC AND FREEZE FRAME DATA|Freeze Frame Data)"
    ),
    "srt": re.compile(
        r"(?mi)^\s*(?:How to Set SRT Code|SRT STATUS|SRT WORK SUPPORT)"
    ),
    "service_06": re.compile(
        r"(?mi)^\s*(?:Test Value and Test Limit|Service \$06)"
    ),
}
MENTION_PATTERNS = {
    kind: re.compile(pattern, re.IGNORECASE)
    for kind, pattern in {
        "dtc_index": r"\bDTC Index\b",
        "data_monitor": r"\bDATA MONITOR\b",
        "active_test": r"\bACTIVE TEST\b",
        "work_support": r"\bWORK SUPPORT\b",
        "fail_safe": r"\bFail[- ]?Safe\b",
        "can_signal_matrix": r"\bCAN Communication Signal Chart\b",
        "terminal_reference": r"\bterminal(?:s)? and reference value\b",
        "freeze_frame": r"\bfreeze frame\b",
        "srt": r"\bSRT\b",
        "service_06": r"(?:Service \$06|Test Value and Test Limit)",
    }.items()
}
INFOID_RE = re.compile(r"INFOID:\s*([0-9]+)")
PAGE_LABEL_RE = re.compile(r"\b([A-Z]{1,4}-\d{1,4})\b")
QUOTED_OPERATION_RE = re.compile(
    r"[\"\u201c]([^\"\u201d]{2,60})[\"\u201d]\s+in\s+"
    r"[\"\u201c](WORK SUPPORT|ACTIVE TEST)",
    re.IGNORECASE,
)
UNIT_ATOMS = {
    "%",
    "0.0/8",
    "0/1/2/3/4/5",
    "a",
    "auto",
    "btdc",
    "btcd",
    "count",
    "counts",
    "bar",
    "d/s",
    "deg",
    "deg/s",
    "degree",
    "g/s",
    "g·m/s",
    "hi/low",
    "hz",
    "kpa",
    "km/h",
    "km/h (mph)",
    "kg/h",
    "km",
    "l",
    "lit.",
    "ma",
    "m",
    "mm",
    "mile",
    "m/s",
    "m/s2",
    "mpa",
    "mph",
    "ms",
    "msec",
    "mv",
    "off/on",
    "off",
    "ohm",
    "ok/\u2013",
    "on/off",
    "psi",
    "rich/lean",
    "rpm",
    "run/stop",
    "sec",
    "steps",
    "shor/mid/long",
    "v",
    "tr/min (rpm)",
    "yet/cmplt",
    "yet",
    "done",
    "°c",
    "°ca",
    "°f",
    "°",
    "°",
}
NAME_CONTINUATIONS = {
    "ANCE",
    "BACK",
    "CONT",
    "CONT/V",
    "ING",
    "LAY",
    "SEN",
    "SENSOR",
    "SETTING",
    "TEMP",
    "TION",
    "TROL",
    "TROL/V",
}
HEADER_NAMES = {
    "CAUTION",
    "CAUTION:",
    "CONTENTS",
    "DTC WORK SUPPORT",
    "MONITORED ITEM",
    "TEST ITEM",
    "TEST ITEM LIST",
    "WORK ITEM",
    "CONDITION",
    "DESCRIPTION",
    "REMARKS",
    "UNIT",
    "JUDGEMENT",
    "CHECK ITEM",
    "USAGE",
    "SIGNALS",
    "MENU",
    "FROM",
    "MAIN",
    "SELECTION",
    "PLAY",
    "NORMAL OPERATION",
}
RESERVED_PREFIXES = (
    "ACTIVE TEST",
    "CONSULT",
    "DATA MONITOR",
    "DIAGNOSIS",
    "ECU DIAGNOSIS",
    "FUNCTION DIAGNOSIS",
    "SELF-DIAG",
    "SELECTION FROM MENU",
    "WORK SUPPORT",
)
TABLE_MARKERS = {
    "data_monitor": re.compile(
        r"(?i)\b(?:Monitored item|Monitor item|Display item(?: List)?)\b"
    ),
    "active_test": re.compile(r"(?i)\bTEST ITEM\b"),
    "work_support": re.compile(r"(?i)\bWORK ITEM\b"),
}
MODE_HEADING_RE = re.compile(
    r"^\s*(DATA (?:MONITOR|MIONITOR)(?: MODE)?|ACTIVE TEST(?: MODE)?|"
    r"(?:DTC )?WORK SUPPORT(?: MODE)?)\s*(?:[A-Z]{1,4})?\s*$",
    re.IGNORECASE,
)


def run_text(command: list[str]) -> str:
    try:
        completed = subprocess.run(
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
        message = error.stderr.strip() or f"exit status {error.returncode}"
        raise CatalogError(f"{' '.join(command)}: {message}") from error
    return completed.stdout


def pdf_page_count(path: Path) -> int:
    output = run_text(["pdfinfo", str(path)])
    match = re.search(r"(?m)^Pages:\s+(\d+)\s*$", output)
    if not match:
        raise CatalogError(f"{path}: pdfinfo did not report a page count")
    return int(match.group(1))


def pdf_pages(path: Path) -> list[str]:
    output = run_text(["pdftotext", "-layout", str(path), "-"])
    pages = output.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    return [page.rstrip() + "\n" for page in pages]


def page_label(text: str) -> str:
    tail = "\n".join(text.splitlines()[-30:])
    labels = PAGE_LABEL_RE.findall(tail)
    return labels[-1] if labels else ""


def section_code(labels: Iterable[str], fallback: str) -> str:
    for label in labels:
        if label:
            return label.split("-", 1)[0]
    return slug(fallback).upper().replace("-", "_")


def page_heading(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines[:15]:
        if (
            not line.startswith("<")
            and "Revision:" not in line
            and "2007 G35 Sedan" not in line
            and len(line) <= 100
        ):
            return re.sub(r"\s+", " ", line)
    return ""


def table_of_contents_page(text: str) -> bool:
    leader_rows = sum(
        bool(re.search(r"\.{3,}\s*\d+(?:\s|$)", line))
        for line in text.splitlines()
    )
    return leader_rows >= 3


def explicit_kinds(text: str) -> list[str]:
    matches = []
    for kind, pattern in KIND_PATTERNS.items():
        match = pattern.search(text)
        if match:
            matches.append((match.start(), kind))
    result = [kind for _position, kind in sorted(matches)]
    if not result:
        dtcs = extract_dtc_codes(text)
        if dtcs and not table_of_contents_page(text) and re.search(
            r"(?i)\b(?:DTC Logic|Diagnosis Procedure|Possible Cause|"
            r"Confirmation Procedure|Component Diagnosis)\b",
            text,
        ):
            result.append("dtc_detail")
    return result


def carry_kind(previous: str, text: str, distance: int) -> str:
    if not previous or distance > 8:
        return ""
    dtcs = extract_dtc_codes(text)
    if previous == "dtc_index" and len(dtcs) >= 3:
        return previous
    if previous == "data_monitor" and (
        re.search(r"(?i)\b(?:Monitored item|Monitor item|Display item)\b", text)
    ):
        return previous
    if previous in {"active_test", "work_support"} and distance <= 4:
        marker = "TEST ITEM" if previous == "active_test" else "WORK ITEM"
        if marker in text.upper():
            return previous
    if previous == "can_signal_matrix" and distance <= 3:
        if "Signal name/Connecting unit" in text or route_character_count(text) >= 8:
            return previous
    return ""


def fragment_id(document_id: str, pdf_page: int, kind: str) -> str:
    return f"{document_id}:p{pdf_page:04d}:{kind}"


ECU_LABEL_ALIASES = (
    ("ABS ACTUATOR AND ELECTRIC UNIT (CONTROL UNIT)", "abs"),
    ("UNIFIED METER AND A/C AMP.", "unified-meter-and-a-c-amp"),
    ("ICC SENSOR INTEGRATED UNIT", "icc-sensor-integrated-unit"),
    ("4WAS FRONT CONTROL UNIT", "4was-front-control-unit"),
    ("4WAS MAIN CONTROL UNIT", "4was-main-control-unit"),
    ("DRIVER SEAT CONTROL UNIT", "driver-seat-c-u"),
    ("DRIVER SEAT C/U", "driver-seat-c-u"),
    ("DIAGNOSIS SENSOR UNIT", "srs-diagnosis-sensor-unit"),
    ("AV CONTROL UNIT", "av-control-unit"),
    ("AWD CONTROL UNIT", "awd-control-unit"),
    ("AFS CONTROL UNIT", "afs"),
    ("COMBINATION METER", "combination-meter"),
    ("METER/M&A", "unified-meter-and-a-c-amp"),
    ("IPDM E/R", "ipdm-e-r"),
    ("AUTO AMP.", "auto-amp"),
    ("TRANSMISSION", "tcm"),
    ("BCM", "bcm"),
    ("TCM", "tcm"),
    ("ECM", "ecm"),
    ("ABS", "abs"),
    ("AFS", "afs"),
)


def canonical_ecu_key(name: str) -> str:
    normalized = re.sub(r"\s+", " ", name.strip()).upper()
    for label, key in ECU_LABEL_ALIASES:
        if (
            normalized == label
            or normalized.startswith(f"{label} ")
            or normalized.startswith(f"{label}-")
        ):
            return key
    return slug(name)


def infer_ecu_id(
    document_title: str,
    text: str,
    vehicle_id: str = VEHICLE_ID,
) -> str:
    header_lines = [
        re.sub(r"\s+", " ", line.strip())
        for line in text.splitlines()
        if line.strip()
    ][:20]
    top_line = header_lines[0] if header_lines else ""
    if top_line.upper().startswith("DIAGNOSIS SYSTEM"):
        explicit = re.search(
            r"(?i)\bDIAGNOSIS SYSTEM\s*\[([^\]]+)\]",
            top_line,
        )
        if not explicit:
            explicit = re.search(
                r"(?i)\bDIAGNOSIS SYSTEM\s*\((.+)\)",
                top_line,
            )
        if explicit:
            return f"{vehicle_id}:{canonical_ecu_key(explicit.group(1))}"

    normalized = top_line.upper()
    for label, key in ECU_LABEL_ALIASES:
        if (
            normalized == label
            or normalized.startswith(f"{label} (")
        ):
            return f"{vehicle_id}:{key}"

    known = {
        "ENGINE CONTROL SYSTEM": "ecm",
        "TRANSAXLE & TRANSMISSION": "tcm",
        "BODY CONTROL SYSTEM": "bcm",
        "BRAKE CONTROL SYSTEM": "abs",
        "LAN SYSTEM": "can-network",
        "SECURITY CONTROL SYSTEM": "security-system",
        "METER, WARNING LAMP & INDICATOR": "meter",
        "HEATER & AIR CONDITIONING CONTROL SYSTEM": "hvac",
        "AUDIO, VISUAL & NAVIGATION SYSTEM": "av",
        "POWER SUPPLY, GROUND & CIRCUIT ELEMENTS": "power-distribution",
    }
    key = known.get(document_title.upper(), slug(document_title))
    return f"{vehicle_id}:{key}"


def parse_dtc_title(line: str, code: str) -> tuple[str, str]:
    chunks = [
        re.sub(r"\s+", " ", chunk.strip())
        for chunk in re.split(r"\s{2,}", line)
        if chunk.strip()
    ]
    normalized = [chunk.strip("[]() ").upper() for chunk in chunks]
    native = ""
    code_indexes = [
        index
        for index, chunk in enumerate(normalized)
        if re.fullmatch(r"[PBCU][0-9A-F]{4}(?:\*\d+)?", chunk)
    ]
    for index in code_indexes:
        if normalized[index].split("*", 1)[0] == code:
            if index + 1 < len(normalized) and re.fullmatch(
                r"[0-9A-F]{4}(?:\*\d+)?", normalized[index + 1]
            ):
                native = normalized[index + 1][:4]
            break
    last_code = max(code_indexes, default=-1)
    if native and last_code + 1 < len(normalized):
        last_code += 1
    for chunk in chunks[last_code + 1 :]:
        candidate = chunk.strip()
        prefixed = re.match(
            r"^(?:[PBCU][0-9A-F]{4}(?:\s*,\s*)?)+\s*:\s*(.+)$",
            candidate,
            re.IGNORECASE,
        )
        if prefixed:
            candidate = prefixed.group(1).strip()
        upper = candidate.upper()
        if (
            not candidate
            or re.fullmatch(r"[PBCU]?[0-9A-F]{4}(?:\*\d+)?", upper)
            or re.fullmatch(r"[A-Z]{1,4}-\d{1,4}", upper)
            or re.fullmatch(r"[A-Z]", upper)
            or not re.search(r"[A-Za-z]", candidate)
            or any(character.islower() for character in candidate)
            or upper in {"CRNT", "PAST", "CURRENT", "REFERENCE PAGE"}
            or set(candidate) <= {"-", "\u2014", "\u00d7", " ", "/"}
        ):
            continue
        return native, candidate[:120].rstrip()
    return native, ""


def dtc_first_column_text(line: str) -> str:
    if len(line) - len(line.lstrip()) >= 40:
        return ""
    return re.split(r"\s{2,}", line.strip(), maxsplit=1)[0].strip()


def previous_dtc_title(lines: list[str], index: int) -> str:
    continuations = []
    for previous_index in range(index - 1, max(-1, index - 21), -1):
        previous = lines[previous_index]
        candidate = dtc_first_column_text(previous)
        candidate = candidate.lstrip("•*- ").strip()
        upper = candidate.upper()
        if (
            not candidate
            or len(candidate) > 50
            or any(character.islower() for character in candidate)
            or extract_dtc_codes(candidate)
            or re.fullmatch(r"[A-Z]", upper)
            or upper.startswith(("DTC ", "NOTE", "REVISION", "CRNT", "PAST"))
            or upper in HEADER_NAMES
            or re.fullmatch(r"\[[A-Z0-9 _,/-]{2,}\]", upper)
            or not re.search(r"[A-Z]", candidate)
        ):
            continue
        if upper in {"DETECTION", "TECTION"}:
            continuations.insert(0, candidate)
            continue
        if upper == "ULE":
            prefix = ""
            for prefix_index in range(
                previous_index - 1,
                max(-1, previous_index - 6),
                -1,
            ):
                prefix = dtc_first_column_text(lines[prefix_index])
                if not prefix:
                    continue
                if prefix.endswith("-"):
                    continuations.insert(0, candidate)
                    break
                prefix = ""
                break
            if prefix:
                continue
        return join_table_text([candidate, *continuations])
    return ""


def previous_dtc_qualifier(lines: list[str], index: int) -> str:
    for previous in reversed(lines[max(0, index - 20) : index]):
        candidate = dtc_first_column_text(previous)
        upper = candidate.upper()
        if not candidate or extract_dtc_codes(candidate):
            continue
        if re.fullmatch(r"\[[A-Z0-9 _,/-]{2,}\]", upper):
            return candidate
        if (
            not any(character.islower() for character in candidate)
            and re.search(r"[A-Z]", candidate)
        ):
            return ""
    return ""


def next_dtc_qualifier(lines: list[str], index: int) -> str:
    for following in lines[index + 1 : index + 3]:
        candidate = dtc_first_column_text(following)
        if not candidate:
            continue
        if extract_dtc_codes(candidate):
            return ""
        if re.fullmatch(r"\[[A-Z0-9 _/-]{2,}\]", candidate):
            return candidate
        return ""
    return ""


def title_score(title: str) -> tuple[int, int]:
    if not title or title in {"]", "[", "-", "\u2014"}:
        return (-100, 0)
    if re.fullmatch(r"[A-Z]{1,4}-\d{1,4}", title):
        return (-50, len(title))
    if re.fullmatch(r"[A-Z]", title):
        return (-50, len(title))
    if re.fullmatch(
        r"\[?[PBCU][0-9A-F]{4}\s*(?:-|TO)\s*"
        r"(?:[PBCU])?[0-9A-F]{4}\]?",
        title,
        re.IGNORECASE,
    ):
        return (-50, len(title))
    letters = sum(character.isalpha() for character in title)
    words = len(title.split())
    return (letters + words * 2, min(len(title), 120))


def dtc_definitions(fragment: dict[str, object]) -> list[dict[str, object]]:
    if fragment["kind"] != "dtc_index":
        return []
    text = str(fragment["text"])
    lines = text.splitlines()
    headings = [
        index
        for index, line in enumerate(lines)
        if re.match(r"^\s*DTC Index\b", line, re.IGNORECASE)
    ]
    if headings:
        lines = lines[headings[-1] + 1 :]
    srs_layout = "srs-airbag-control-system" in str(fragment["id"])
    candidates: defaultdict[str, list[tuple[str, str]]] = defaultdict(list)
    for line_index, line in enumerate(lines):
        line_codes = extract_dtc_codes(line)
        line_codes = [code for code in line_codes if code != "P0000"]
        if not line_codes:
            continue
        stripped = line.lstrip()
        starts_with_code = re.match(
            r"^(?:\[|[-*\u2014]\s*)?[PBCU][0-9A-F]{4}\b",
            stripped,
            re.IGNORECASE,
        )
        suffix_codes = {
            match.group(1).upper()
            for match in re.finditer(
                r"\[([PBCU][0-9A-F]{4})\]",
                line,
                re.IGNORECASE,
            )
        }
        if not starts_with_code and not suffix_codes:
            continue
        for code in line_codes:
            native, title = parse_dtc_title(line, code)
            if code in suffix_codes and not starts_with_code:
                title = ""
            code_position = line.upper().find(code)
            before = line[:code_position].strip() if code_position >= 0 else ""
            before_chunks = [
                re.sub(r"\s+", " ", chunk.strip())
                for chunk in re.split(r"\s{2,}", before)
                if chunk.strip()
            ]
            if before_chunks:
                candidate = (
                    before_chunks[-1]
                    .lstrip("•*- ")
                    .rstrip("[ ")
                    .strip()
                )
                if (
                    not re.fullmatch(r"\d+(?:-\d+)?", candidate)
                    and not re.fullmatch(
                        r"\[?[PBCU][0-9A-F]{4}\s*(?:-|TO)\s*"
                        r"(?:[PBCU])?[0-9A-F]{4}\]?",
                        candidate,
                        re.IGNORECASE,
                    )
                ):
                    candidates[code].append((native, candidate))
            if code in suffix_codes and before:
                candidate = (
                    re.sub(r"\s+", " ", before)
                    .lstrip("•*- ")
                    .rstrip("[ ")
                    .strip()
                )
                if candidate:
                    candidates[code].append((native, candidate[:120]))
            candidates[code].append((native, title))
            if starts_with_code:
                qualifier = (
                    previous_dtc_qualifier(lines, line_index)
                    or next_dtc_qualifier(lines, line_index)
                )
            else:
                qualifier = ""
            if starts_with_code and (
                title_score(title)[0] < 0
                or (srs_layout and qualifier)
            ):
                previous = previous_dtc_title(lines, line_index)
                if previous:
                    if qualifier:
                        previous = f"{previous} {qualifier}"
                    candidates[code].append((native, previous))

    rows = []
    for code, choices in sorted(candidates.items()):
        native, title = max(choices, key=lambda item: title_score(item[1]))
        rows.append(
            {
                "id": f"{fragment['id']}:{code.lower()}",
                "dataset_id": fragment["dataset_id"],
                "code": code,
                "native_code": native,
                "title": title,
                "ecu_id": fragment["ecu_id"],
                "vehicle_id": fragment["vehicle_id"],
                "applicability_status": "exact_manual",
                "definition_kind": "dtc_index",
                "source_fragment_id": fragment["id"],
            }
        )
    return rows


def valid_item_name(name: str) -> bool:
    normalized = name.strip("[]<> ").upper()
    if len(normalized) < 3 or normalized in HEADER_NAMES:
        return False
    if name.startswith(("<", "[", "(")) or name.endswith(">"):
        return False
    if name.endswith(")") and not re.search(r"\(B[12]\)$", normalized):
        return False
    if name.endswith("]") and not re.fullmatch(
        r"(?:HSV|USV)\s+\[(?:FL-RR|FR-RL)\]",
        name.strip().upper(),
    ):
        return False
    if any(normalized.startswith(prefix) for prefix in RESERVED_PREFIXES):
        return False
    if re.fullmatch(r"[A-Z]\d*", normalized):
        return False
    if re.fullmatch(r"[A-Z]\d{1,3}(?:\s+\d+){0,2}", normalized):
        return False
    return True


def unit_value(candidate: str) -> str:
    value = candidate.strip("[] \"\u201c\u201d").strip()
    if not value or value in {"-", "\u2013", "\u2014"}:
        return ""
    atoms = [
        atom.strip().lower()
        for atom in re.split(r"\s*(?:,|\bor\b)\s*", value, flags=re.IGNORECASE)
        if atom.strip()
    ]
    if atoms and all(atom in UNIT_ATOMS for atom in atoms):
        return value
    if (
        "/" in value
        and len(value) <= 40
        and all(
            0 < len(part.strip()) <= 12
            and re.fullmatch(r"[A-Za-z0-9 -]+", part.strip())
            for part in value.split("/")
        )
    ):
        return value
    if re.fullmatch(
        r"(?:[A-Z]|\d+)\s*[-\u2212\u2013]\s*\d+",
        value,
        re.IGNORECASE,
    ):
        return value
    if (
        "," in value
        and len(value) <= 120
        and all(
            len(atom.strip()) <= 12
            and
            re.fullmatch(r"[A-Za-z0-9&/ -]+", atom)
            for atom in re.split(r"\s*,\s*", value)
        )
    ):
        return value
    return ""


def split_name_unit(value: str) -> tuple[str, str]:
    match = re.fullmatch(
        r"(.+?)\s*(?:"
        r"\[([^\]]{1,30})\](?:\s+or\s+\[([^\]]{1,30})\])?"
        r"|\(([^()]{1,30})\)"
        r")",
        value,
        re.IGNORECASE,
    )
    if not match:
        return value, ""
    candidates = [candidate for candidate in match.groups()[1:] if candidate]
    unit = unit_value(" or ".join(candidates))
    if not unit:
        return value, ""
    name = re.sub(
        r"\s+\((?:high|low)\)$",
        "",
        match.group(1).strip(),
        flags=re.IGNORECASE,
    )
    return name, unit


def repeated_section_heading(lines: list[str], index: int, heading: str) -> bool:
    if not heading or len(lines[index]) - len(lines[index].lstrip()) > 1:
        return False
    for following in lines[index + 1 : index + 4]:
        candidate = following.strip()
        if not candidate:
            continue
        if re.fullmatch(r"[A-P]", candidate):
            continue
        return candidate.startswith(f"{heading} :")
    return False


def first_column_rows(text: str, width: int) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    lines = text.splitlines()
    last_row_line = -100
    consumed_until = -1
    for index, line in enumerate(lines):
        if index <= consumed_until:
            continue
        stripped = line.strip()
        if stripped.startswith("Revision:"):
            break
        if not stripped or line.lstrip().startswith(("•", "-", "*", "NOTE:")):
            continue
        indentation = len(line) - len(line.lstrip())
        if indentation > min(16, width // 2):
            continue
        cells = re.split(r"\s{2,}", line.lstrip(), maxsplit=1)
        first = re.sub(r"\s+", " ", cells[0].strip())
        rest = cells[1].strip() if len(cells) > 1 else ""
        if rows and first.upper() in {
            "AV COMM MONITOR",
            "CAN DIAGNOSTIC SUPPORT MONITOR",
        }:
            break
        if rows and re.fullmatch(
            r"DTC\s*&\s*SRT CONFIRMATION MODE",
            first,
            re.IGNORECASE,
        ):
            break
        if (
            rows
            and re.fullmatch(r"\(?NOTE\s+\d+\)?", first, re.IGNORECASE)
            and index - last_row_line <= 3
        ):
            rows[-1]["end_line"] = index
            last_row_line = index
            continue
        parenthesized_unit = re.fullmatch(r"\(([^)]{1,30})\)", first)
        if parenthesized_unit and rows and index - last_row_line <= 3:
            unit = unit_value(parenthesized_unit.group(1))
            if unit:
                rows[-1]["unit"] = rows[-1]["unit"] or unit
                rows[-1]["end_line"] = index
                last_row_line = index
                continue
        if rows and indentation <= 1 and len(first) > 42:
            break
        if repeated_section_heading(lines, index, first):
            break
        bracket_unit = re.fullmatch(r"\[([^\]]{1,30})\]", first)
        if bracket_unit and rows and index - last_row_line <= 3:
            unit = unit_value(bracket_unit.group(1))
            if unit and not rows[-1]["unit"]:
                rows[-1]["unit"] = unit
            rows[-1]["end_line"] = index
            continue
        if (
            first.startswith("[")
            and not first.endswith("]")
            and rows
            and index - last_row_line <= 3
        ):
            parts = [first]
            following_index = index
            for following_index in range(
                index + 1,
                min(index + 4, len(lines)),
            ):
                following_line = lines[following_index].lstrip()
                following_cell = re.split(
                    r"\s{2,}",
                    following_line,
                    maxsplit=1,
                )[0]
                parts.append(
                    re.sub(r"\s+", " ", following_cell.strip())
                )
                if following_cell.rstrip().endswith("]"):
                    break
            combined = " ".join(parts)
            if combined.endswith("]"):
                unit = unit_value(combined[1:-1])
                if unit:
                    rows[-1]["unit"] = rows[-1]["unit"] or unit
                    rows[-1]["end_line"] = following_index
                    last_row_line = following_index
                    consumed_until = following_index
                    continue
        first, embedded_unit = split_name_unit(first)
        if (
            rows
            and index - last_row_line <= 3
            and str(rows[-1]["name"]).endswith("-")
            and re.fullmatch(r"B[12]", first)
        ):
            rows[-1]["name"] = f"{rows[-1]['name']}{first}"
            rows[-1]["end_line"] = index
            last_row_line = index
            continue
        if not first or not valid_item_name(first):
            continue
        if any(character.islower() for character in first) and not embedded_unit:
            continue
        if not re.search(r"[A-Z]", first) or len(first) > 42:
            continue
        unit = embedded_unit
        if rest:
            candidate = re.split(r"\s{2,}", rest, maxsplit=1)[0].strip()
            unit = unit or unit_value(candidate)
        if rows and index - last_row_line <= 3 and (
            str(rows[-1]["name"]).endswith("-")
            or first in NAME_CONTINUATIONS
            or (
                first == "DUTY"
                and str(rows[-1]["name"]) == "ALTERNATOR"
            )
        ):
            previous = str(rows[-1]["name"])
            separator = "" if previous.endswith("-") else " "
            rows[-1]["name"] = f"{previous.rstrip('-')}{separator}{first}"
            rows[-1]["unit"] = rows[-1]["unit"] or unit
            rows[-1]["end_line"] = index
            last_row_line = index
            continue
        rows.append(
            {
                "name": first,
                "unit": unit,
                "start_line": index,
                "end_line": index,
            }
        )
        last_row_line = index
    for row in rows:
        row["name"] = str(row["name"]).rstrip("-").strip()
    return rows


def first_column_names(text: str, width: int) -> list[tuple[str, str]]:
    return [
        (str(row["name"]), str(row["unit"]))
        for row in first_column_rows(text, width)
    ]


TABLE_COLUMN_PATTERNS = {
    "data_monitor": (
        ("name", re.compile(r"\b(?:MONITORED ITEM|MONITOR ITEM|DISPLAY ITEM)\b", re.I)),
        ("unit", re.compile(r"\bUNIT\b", re.I)),
        (
            "description",
            re.compile(
                r"\b(?:DESCRIPTION|CONTENTS|DISPLAY CONTENT|VEHICLE STATUS)\b",
                re.I,
            ),
        ),
        ("conditions", re.compile(r"\bCONDITION\b", re.I)),
        (
            "remarks",
            re.compile(
                r"\b(?:REMARKS|REFERENCE VALUE(?:\s+IN)?|SPECIFICATION)\b",
                re.I,
            ),
        ),
    ),
    "active_test": (
        ("name", re.compile(r"\bTEST ITEM\b", re.I)),
        (
            "conditions",
            re.compile(
                r"\b(?:CONDITION|OPERATION(?: ITEM)?|CONTROL SIGNAL)\b",
                re.I,
            ),
        ),
        (
            "description",
            re.compile(r"\b(?:JUDGEMENT|DESCRIPTION|REMARKS)\b", re.I),
        ),
        ("usage", re.compile(r"\bCHECK ITEM(?:\s+\(REMEDY\))?\b", re.I)),
    ),
    "work_support": (
        (
            "name",
            re.compile(
                r"\b(?:DTC WORK SUPPORT ITEM|WORK ITEM|MONITOR ITEM)\b",
                re.I,
            ),
        ),
        ("conditions", re.compile(r"\bCONDITION\b", re.I)),
        ("description", re.compile(r"\bDESCRIPTION\b", re.I)),
        ("usage", re.compile(r"\b(?:CHECK ITEM|USAGE)\b", re.I)),
    ),
}

PAGE_SIDEBAR_CODES = {
    "ADP",
    "AV",
    "BCS",
    "BRC",
    "CCS",
    "DEF",
    "DLK",
    "DLN",
    "EC",
    "EXL",
    "INL",
    "MIR",
    "MWI",
    "PCS",
    "PWC",
    "RF",
    "SEC",
    "STC",
    "TM",
    "WCS",
    "WT",
}


def page_sidebar_start(lines: list[str]) -> int | None:
    positions = []
    preferred = []
    for line in lines:
        match = re.search(r"\s{3,}([A-Z]{1,4})\s*$", line)
        if not match:
            continue
        code = match.group(1)
        if code in PAGE_SIDEBAR_CODES:
            preferred.append(match.start(1))
        elif len(code) == 1 and code in "ABCDEFGHIJKLMNOP":
            positions.append(match.start(1))
    candidates = preferred or positions
    if not candidates:
        return None
    clusters: list[list[int]] = []
    for position in sorted(candidates):
        if clusters and position - clusters[-1][-1] <= 3:
            clusters[-1].append(position)
        else:
            clusters.append([position])
    cluster = max(clusters, key=lambda values: (len(values), max(values)))
    return sorted(cluster)[len(cluster) // 2]


def strip_page_sidebar(
    line: str,
    sidebar_start: int | None = None,
) -> str:
    match = re.search(r"\s{3,}([A-Z]{1,4})\s*$", line)
    if match and (
        sidebar_start is not None
        and match.start(1) >= sidebar_start - 3
        and (
            (
                len(match.group(1)) == 1
                and match.group(1) in "ABCDEFGHIJKLMNOP"
            )
            or match.group(1) in PAGE_SIDEBAR_CODES
        )
    ):
        return line[: match.start()]
    return line


def join_table_text(parts: Iterable[str]) -> str:
    result = ""
    for part in parts:
        value = re.sub(r"\s+", " ", part.strip())
        if not value or value.upper() in HEADER_NAMES:
            continue
        if not re.search(r"[A-Za-z0-9]", value):
            continue
        if result.endswith("-") and not result.endswith(" -"):
            if value.startswith("* "):
                value = value[2:].lstrip()
            if re.search(r"\bCONSULT-$", result):
                result += value
            else:
                result = result[:-1] + value
        else:
            result = f"{result} {value}".strip()
    return result


def semantic_table_end(lines: list[str], rows: list[dict[str, object]]) -> int:
    last_anchor = int(rows[-1]["end_line"])
    previous_blank = False
    for index in range(last_anchor + 1, len(lines)):
        clean_line = strip_page_sidebar(lines[index])
        stripped = clean_line.strip()
        if not stripped:
            previous_blank = True
            continue
        indentation = len(clean_line) - len(clean_line.lstrip())
        if (
            "INFOID:" in stripped
            or stripped.startswith("Revision:")
            or stripped in {"NOTE:", "CAUTION:"}
            or re.match(r"^\*+(?:\d+)?\s*:", stripped)
            or MODE_HEADING_RE.match(clean_line)
            or repeated_section_heading(lines, index, stripped)
            or (
                previous_blank
                and indentation <= 1
                and stripped == stripped.upper()
                and stripped not in {"NOTE:", "CAUTION:"}
            )
        ):
            return index
        previous_blank = False
    return len(lines)


def first_following_cell_positions(
    lines: list[str], rows: list[dict[str, object]]
) -> list[int]:
    positions = []
    for row in rows:
        line = strip_page_sidebar(lines[int(row["start_line"])])
        indentation = len(line) - len(line.lstrip())
        content = line[indentation:]
        separator = re.search(r"\s{2,}(?=\S)", content)
        if separator:
            cell_start = indentation + separator.end()
            tail = line[cell_start:]
            markers = re.match(
                r"(?:(?:X|\u00d7|\u274f|\u2013|\u2014|-)"
                r"(?:\s{2,}|$))+",
                tail,
            )
            if markers:
                following = re.search(r"[A-Za-z0-9•]", tail[markers.end() :])
                if following:
                    positions.append(
                        cell_start + markers.end() + following.start()
                    )
                continue
            positions.append(cell_start)
    return positions


def semantic_only_cell_positions(
    lines: list[str],
    header_index: int,
    rows: list[dict[str, object]],
    width: int,
) -> list[int]:
    anchors = {int(row["start_line"]) for row in rows}
    positions = []
    first_anchor = min(anchors)
    for index, line in enumerate(lines[first_anchor:], first_anchor):
        if index in anchors or not line.strip():
            continue
        normalized = re.sub(
            r"\s+",
            " ",
            strip_page_sidebar(line).strip(),
        ).upper()
        if (
            normalized.strip("[] ") in HEADER_NAMES
            or re.fullmatch(
                r"(?:X|\u00d7|\u274f|\u2013|\u2014|-)+",
                normalized,
            )
            or (
                normalized
                and set(normalized.split())
                <= {
                    "FROM",
                    "MAIN",
                    "MENU",
                    "SELECTION",
                    "SIGNALS",
                }
            )
        ):
            continue
        indentation = len(line) - len(line.lstrip())
        if max(15, width // 2) <= indentation <= 80:
            content = line[indentation:]
            markers = re.match(
                r"(?:(?:X|\u00d7|\u274f|\u2013|\u2014|-)"
                r"(?:\s{2,}|$))+",
                content,
            )
            if markers:
                following = re.search(
                    r"[A-Za-z0-9•]",
                    content[markers.end() :],
                )
                if following:
                    positions.append(
                        indentation + markers.end() + following.start()
                    )
                continue
            positions.append(indentation)
    return positions


def bullet_column_positions(
    lines: list[str],
    first_line: int,
    minimum: int,
) -> list[int]:
    positions = sorted(
        match.start()
        for line in lines[first_line:]
        for match in re.finditer(r"•", strip_page_sidebar(line))
        if match.start() >= minimum
    )
    clusters: list[list[int]] = []
    for position in positions:
        if clusters and position - clusters[-1][-1] <= 8:
            clusters[-1].append(position)
        else:
            clusters.append([position])
    return [
        sorted(cluster)[len(cluster) // 2]
        for cluster in clusters
    ]


def semantic_content_column_positions(
    lines: list[str],
    rows: list[dict[str, object]],
    width: int,
    first_line: int | None = None,
) -> list[int]:
    first_anchor = int(rows[0]["start_line"])
    last_line = semantic_table_end(lines, rows)
    positions = []
    content_start = (
        first_line
        if first_line is not None
        else max(0, first_anchor - 8)
    )
    for line in lines[content_start:last_line]:
        first = re.search(r"\S", line)
        candidates = [first.start()] if first else []
        candidates.extend(
            match.end()
            for match in re.finditer(
                r"(?<=\S)\s{2,}(?=\S)",
                line,
            )
        )
        positions.extend(
            position
            for position in candidates
            if position >= max(15, width // 2)
        )
    clusters: list[list[int]] = []
    for position in sorted(positions):
        if clusters and position - clusters[-1][-1] <= 4:
            clusters[-1].append(position)
        else:
            clusters.append([position])
    return [
        min(cluster)
        for cluster in clusters
        if len(cluster) >= 2
    ]


def table_layout(
    lines: list[str],
    kind: str,
    rows: list[dict[str, object]],
    width: int,
) -> tuple[int, list[tuple[str, int, int | None]]]:
    def columns_for_line(line: str) -> list[tuple[str, int, int]]:
        columns = []
        for field, pattern in TABLE_COLUMN_PATTERNS[kind]:
            match = pattern.search(line)
            if match:
                columns.append((field, match.start(), match.end()))
        if kind == "data_monitor" and re.search(
            r"\b(?:MONITORED ITEM|MONITOR ITEM|DISPLAY ITEM)"
            r"\s*[\[(]\s*UNIT\s*[\])]",
            line,
            re.IGNORECASE,
        ):
            columns = [
                column for column in columns if column[0] != "unit"
            ]
        return sorted(columns, key=lambda column: column[1])

    best_index = 0
    best_columns: list[tuple[str, int, int]] = []
    first_anchor = int(rows[0]["start_line"]) if rows else len(lines)
    for index, line in enumerate(lines[: first_anchor + 1]):
        columns = columns_for_line(line)
        if len(columns) > len(best_columns):
            best_index = index
            best_columns = columns

    merged_columns = {field: (field, start, end) for field, start, end in best_columns}
    for line in lines[max(0, best_index - 2) : first_anchor]:
        header_text = re.sub(
            r"\s+",
            " ",
            strip_page_sidebar(line).strip(),
        ).upper()
        header_labels = {
            "CONDITION",
            "CONTENTS",
            "DESCRIPTION",
            "DISPLAY CONTENT",
            "MONITOR",
            "REFERENCE VALUE",
            "REFERENCE VALUE IN",
            "REMARKS",
            "SPECIFICATION",
            "UNIT",
            "VEHICLE STATUS",
        }
        if (
            header_text.strip("[] ") not in header_labels
            and not set(header_text.split()) <= header_labels
            and not re.search(
                r"\b(?:MONITORED ITEM|MONITOR ITEM|DISPLAY ITEM)"
                r"(?: LIST)?\b",
                header_text,
            )
        ):
            continue
        for field, start, end in columns_for_line(line):
            merged_columns.setdefault(field, (field, start, end))
    if len(merged_columns) > len(best_columns):
        best_columns = sorted(
            merged_columns.values(),
            key=lambda column: column[1],
        )
    if kind == "data_monitor" and any(
        re.fullmatch(r"\s*\[\s*UNIT\s*\]\s*", line, re.IGNORECASE)
        for line in lines[best_index:first_anchor]
    ):
        best_columns = [
            column for column in best_columns if column[0] != "unit"
        ]

    if len(best_columns) < 2:
        positions = first_following_cell_positions(lines, rows)
        bullet_starts = [
            len(line) - len(line.lstrip())
            for line in lines[first_anchor + 1 :]
            if line.lstrip().startswith("•")
        ]
        boundary = (
            min(positions)
            if positions
            else (
                min(bullet_starts)
                if bullet_starts
                else max(1, width - 2)
            )
        )
        fallback_field = "description"
        return best_index, [
            ("name", 0, boundary),
            (fallback_field, boundary, None),
        ]

    starts = [0]
    following_positions = first_following_cell_positions(lines, rows)
    if len(best_columns) == 2:
        following_positions.extend(
            semantic_only_cell_positions(
                lines,
                best_index,
                rows,
                width,
            )
        )
    boundary_candidates = list(following_positions)
    if len(best_columns) > 2:
        boundary_candidates.append(best_columns[1][1])
    first_boundary = (
        min(boundary_candidates)
        if boundary_candidates
        else (
            max(1, width - 2)
            if len(best_columns) == 2
            else (best_columns[0][1] + best_columns[1][1]) // 2
        )
    )
    starts.append(first_boundary)
    for previous, current in zip(best_columns[1:], best_columns[2:]):
        previous_center = (previous[1] + previous[2]) // 2
        current_center = (current[1] + current[2]) // 2
        starts.append((previous_center + current_center) // 2)

    fields = [column[0] for column in best_columns]
    if kind in {"active_test", "work_support"}:
        content_positions = semantic_content_column_positions(
            lines,
            rows,
            width,
            best_index + 1,
        )
        used_positions: set[int] = set()
        for field_index, field in enumerate(fields):
            if field in {"name", "unit"}:
                continue
            candidates = [
                position
                for position in content_positions
                if position not in used_positions
                and (
                    field_index == 0
                    or position > starts[field_index - 1]
                )
            ]
            if not candidates:
                continue
            selected = min(
                candidates,
                key=lambda position: abs(position - starts[field_index]),
            )
            starts[field_index] = selected
            used_positions.add(selected)
    semantic_indexes = [
        index
        for index, field in enumerate(fields)
        if field in {"description", "remarks"}
    ]
    if kind == "data_monitor" and semantic_indexes:
        bullet_positions = bullet_column_positions(
            lines,
            best_index + 1,
            first_boundary + 4,
        )
        if len(bullet_positions) >= len(semantic_indexes):
            for field_index, position in zip(
                semantic_indexes,
                bullet_positions,
            ):
                starts[field_index] = position
        elif bullet_positions:
            for field_index, position in zip(
                semantic_indexes,
                bullet_positions,
            ):
                starts[field_index] = position
            dropped = set(semantic_indexes[len(bullet_positions) :])
            fields = [
                field
                for index, field in enumerate(fields)
                if index not in dropped
            ]
            starts = [
                start
                for index, start in enumerate(starts)
                if index not in dropped
            ]
    if kind == "data_monitor" and "remarks" in fields:
        remarks_index = fields.index("remarks")
        reference_starts = [
            match.start()
            for line in lines[best_index:first_anchor]
            if (
                match := re.search(
                    r"\bREFERENCE VALUE(?:\s+IN)?\b",
                    line,
                    re.IGNORECASE,
                )
            )
        ]
        if reference_starts:
            starts[remarks_index] = max(
                starts[remarks_index],
                min(reference_starts) - 2,
            )
    result = []
    for index, field in enumerate(fields):
        start = starts[index]
        end = starts[index + 1] if index + 1 < len(starts) else None
        result.append((field, start, end))
    return best_index, result


def paired_monitor_item_key(name: str) -> str:
    normalized = re.sub(r"\s+", " ", name.upper()).strip()
    if re.fullmatch(
        r"(?:AIR PRESS|ID REGST)\s+(?:FL|FR|RL|RR)",
        normalized,
    ):
        return re.sub(r"\s+(?:FL|FR|RL|RR)$", " SIDE", normalized)
    if re.fullmatch(r"(?:DUTY|PLS WIDTH)-(?:HI|LOW)", normalized):
        return "PROBE VALUE"
    sensor_pair = re.sub(
        r"\bSEN\s*[12](?=-B[12]\b|$)",
        "SEN #",
        normalized,
    )
    if sensor_pair != normalized:
        return sensor_pair
    paired = re.sub(r"\bB[12]\b", "B#", normalized)
    return paired if paired != normalized else ""


def data_monitor_row_groups(
    rows: list[dict[str, object]],
) -> list[list[int]]:
    groups = []
    index = 0
    while index < len(rows):
        members = [index]
        key = paired_monitor_item_key(str(rows[index]["name"]))
        following = index + 1
        while key and following < len(rows):
            following_key = paired_monitor_item_key(
                str(rows[following]["name"])
            )
            distance = (
                int(rows[following]["start_line"])
                - int(rows[members[-1]]["start_line"])
            )
            if following_key != key or distance > 8:
                break
            members.append(following)
            following += 1
        groups.append(members)
        index = following
    return groups


def grouped_table_boundaries(
    rows: list[dict[str, object]],
    groups: list[list[int]],
    header_index: int,
    table_end: int,
) -> list[int]:
    boundaries = [header_index + 1]
    for left_group, right_group in zip(groups, groups[1:]):
        left = int(rows[left_group[-1]]["end_line"])
        right = int(rows[right_group[0]]["start_line"])
        boundaries.append(
            max(
                left + 1,
                (left + right) // 2 + (1 if right - left <= 4 else 0),
            )
        )
    boundaries.append(table_end)
    return boundaries


def semantic_cell_text(
    line: str,
    field: str,
    start: int,
    end: int | None,
) -> str:
    if field == "description" and end is not None:
        segment = line[start:end]
        first = re.search(r"\S", segment)
        if (
            first
            and start + first.start() >= end - 8
            and line[end:].strip()
        ):
            return ""
        following_bullet = line.find("•", start + 1, end)
        if following_bullet >= end - 8 and line[end:].strip():
            return line[start:following_bullet]
    if field != "remarks" and start > 0 and line[start:].strip():
        left_end = len(line[:start].rstrip())
        right_match = re.search(r"\S", line[start:])
        right_start = start + right_match.start() if right_match else start
        if left_end > 0 and right_start - left_end < 2:
            return ""
    if (
        end is not None
        and end < len(line)
        and line[start:end].strip()
        and line[end:].strip()
    ):
        left_end = len(line[:end].rstrip())
        right_match = re.search(r"\S", line[end:])
        right_start = end + right_match.start() if right_match else end
        if right_start - left_end < 2:
            following_separator = re.search(
                r"\s{2,}(?=\S)",
                line[right_start:],
            )
            end = (
                right_start + following_separator.start()
                if following_separator
                else None
            )
    if field == "remarks":
        early_start = max(0, start - 8)
        prefix = line[early_start:start]
        bullet = prefix.find("•")
        if bullet >= 0:
            start = early_start + bullet
        elif (
            start < len(line)
            and start > 0
            and not line[start].isspace()
            and not line[start - 1].isspace()
        ):
            token = re.search(r"\S+$", prefix)
            if not token:
                return ""
            candidate = early_start + token.start()
            if candidate < 2 or line[candidate - 2 : candidate].strip():
                return ""
            start = candidate
    return line[start:end] if end is not None else line[start:]


def semantic_table_data_start(
    lines: list[str],
    header_index: int,
    first_anchor: int,
) -> int:
    header_continuations = {
        "CONDITION",
        "DATA MONITOR",
        "FROM",
        "MAIN",
        "MENU",
        "NORMAL OPERATION",
        "PLAY",
        "REFERENCE VALUE",
        "REFERENCE VALUE IN",
        "SELECTION",
        "SIGNALS",
    }
    repeatable_header_words = {
        "CONDITION",
        "FROM",
        "IN",
        "INPUT",
        "MAIN",
        "MENU",
        "MONITOR",
        "NALS",
        "PUT",
        "SELECTION",
        "SELEC",
        "SIG",
        "SIGNALS",
        "SPECIFICATION",
        "TCM",
        "TION",
    }
    start = header_index + 1
    for index in range(start, first_anchor + 1):
        value = re.sub(
            r"\s+",
            " ",
            strip_page_sidebar(lines[index]).strip(),
        ).upper()
        header_words = set(value.replace("-", " ").split())
        if (
            not value
            or value in header_continuations
            or header_words <= repeatable_header_words
        ):
            start = index + 1
            continue
        break
    return min(start, first_anchor)


def semantic_text_continues(previous: str, current: str) -> bool:
    if previous.rstrip().endswith("-"):
        return True
    if previous.rstrip().upper().endswith("NOTE:"):
        return True
    if current.lstrip().startswith("("):
        return True
    if re.match(
        r"^(?:CMPLT|CUT|LEAN|NON|OFF|ON|RICH|YET):\s",
        current.lstrip(),
        re.IGNORECASE,
    ):
        return True
    if re.search(
        r"\b(?:and|from|of|or|the|through|to|using|with)\s*$",
        previous,
        re.IGNORECASE,
    ):
        return True
    if re.match(
        r"^(?:AND|AS|BY|FOR|FROM|IN|OF|OR|THAT|THE|TO|UNDER|VALVE|WITH)\b",
        current.lstrip(),
    ):
        return True
    if re.match(r"^[a-z]", current.lstrip()):
        return True
    if semantic_text_is_terminal(previous):
        return False
    return False


def semantic_text_is_terminal(value: str) -> bool:
    return bool(re.search(r"""[.!?;)]["'\u201d]?$""", value.rstrip()))


def semantic_keywords(value: str) -> set[str]:
    ignored = {
        "active",
        "condition",
        "control",
        "displayed",
        "inactive",
        "operation",
        "signal",
        "status",
        "the",
        "unit",
        "when",
    }
    return {
        word
        for word in re.findall(r"[A-Za-z]+", value.lower())
        if len(word) >= 3 and word not in ignored
    }


def semantic_prefix(value: str) -> tuple[str, ...]:
    return tuple(re.findall(r"[A-Za-z0-9]+", value.lower())[:3])


def clean_semantic_value(value: str) -> str:
    result = re.sub(r"\s+", " ", value.strip())
    result = re.sub(
        r"^(?:[A-Z]{2,}\d{3,}[A-Z]{2}\s+)+",
        "",
        result,
    )
    result = re.sub(
        r"^(?:Setting item\s+Setting\s+)+",
        "",
        result,
        flags=re.IGNORECASE,
    )
    result = re.sub(
        r"^(?:(?:\u00d7|\u274f|\u2013|\u2014|-)\s*)+"
        r"(?=[A-Za-z0-9•(])",
        "",
        result,
    )
    return re.sub(r"^\[Unit\]\s*", "", result, flags=re.IGNORECASE)


def semantic_column_paragraphs(
    lines: list[str],
    field: str,
    start: int,
    end: int | None,
    first_line: int,
    last_line: int,
    rows: list[dict[str, object]],
    groups: list[list[int]],
    boundaries: list[int],
    anchor_lines: set[int],
    split_short_conditions: bool = False,
) -> list[tuple[int, int, str, int | None]]:
    paragraphs = []
    current_start: int | None = None
    current_end = 0
    current_parts: list[str] = []
    current_group: int | None = None
    current_hint: int | None = None
    previous_value = ""
    previous_index: int | None = None
    for index in range(first_line, last_line):
        line = strip_page_sidebar(lines[index])
        value = semantic_cell_text(line, field, start, end)
        value = clean_semantic_value(value)
        if (
            not value
            or value.upper() in HEADER_NAMES
            or not re.search(r"[A-Za-z0-9]", value)
        ):
            continue
        line_group = next(
            (
                group_index
                for group_index in range(len(groups))
                if boundaries[group_index]
                <= index
                < boundaries[group_index + 1]
            ),
            len(groups) - 1,
        )
        blank_gap = bool(
            previous_index is not None
            and any(
                not re.search(
                    r"[A-Za-z0-9]",
                    clean_semantic_value(
                        semantic_cell_text(
                            strip_page_sidebar(lines[gap]),
                            field,
                            start,
                            end,
                        )
                    )
                )
                for gap in range(previous_index + 1, index)
            )
        )
        continuation = semantic_text_continues(previous_value, value) and (
            not blank_gap
            or (
                previous_index is not None
                and index - previous_index <= 4
            )
        )
        starts_paragraph = (
            current_start is None
            or value.startswith("•")
            or (
                split_short_conditions
                and field == "conditions"
                and not continuation
                and len(value) <= 24
                and len(previous_value) <= 24
            )
            or (
                field == "conditions"
                and index in anchor_lines
                and index != current_start
            )
            or (
                not continuation
                and (
                    blank_gap
                    or semantic_text_is_terminal(previous_value)
                    or line_group != current_group
                    or (
                        previous_value.startswith("•")
                        and not value.startswith("•")
                        and re.match(r"^[A-Z]", value)
                    )
                    or (
                        current_group is not None
                        and current_group + 1 < len(groups)
                        and index == boundaries[current_group + 1] - 1
                    )
                )
            )
        )
        if starts_paragraph:
            if current_start is not None:
                paragraphs.append(
                    (
                        current_start,
                        current_end,
                        join_table_text(current_parts),
                        current_hint,
                    )
            )
            target_hint = None
            current_keywords = semantic_keywords(value)
            next_group_keywords = (
                {
                    keyword
                    for row_index in groups[line_group + 1]
                    for keyword in semantic_keywords(
                        str(rows[row_index]["name"])
                    )
                }
                if line_group + 1 < len(groups)
                else set()
            )
            next_group_semantic_prefix = False
            if (
                line_group + 1 < len(groups)
                and index == boundaries[line_group + 1] - 1
            ):
                next_anchor = int(
                    rows[groups[line_group + 1][0]]["start_line"]
                )
                for probe_index in range(
                    index + 1,
                    min(last_line, next_anchor + 3),
                ):
                    probe_value = clean_semantic_value(
                        semantic_cell_text(
                            strip_page_sidebar(lines[probe_index]),
                            field,
                            start,
                            end,
                        )
                    )
                    if not probe_value:
                        continue
                    current_prefix = semantic_prefix(value)
                    next_group_semantic_prefix = (
                        len(current_prefix) == 3
                        and semantic_prefix(probe_value) == current_prefix
                    )
                    break
            if (
                line_group + 1 < len(groups)
                and index == boundaries[line_group + 1] - 1
                and index not in anchor_lines
                and (
                    current_keywords.intersection(next_group_keywords)
                    or next_group_semantic_prefix
                )
            ):
                target_hint = line_group + 1
            current_start = index
            current_parts = [value]
            current_group = line_group
            current_hint = target_hint
        else:
            current_parts.append(value)
            current_group = line_group
        current_end = index
        previous_value = value
        previous_index = index
    if current_start is not None:
        paragraphs.append(
            (
                current_start,
                current_end,
                join_table_text(current_parts),
                current_hint,
            )
        )
    return [paragraph for paragraph in paragraphs if paragraph[2]]


def status_reference_paragraphs(
    lines: list[str],
    start: int,
    end: int | None,
    first_line: int,
    last_line: int,
) -> list[tuple[int, int, str, int | None]] | None:
    values = []
    for index in range(first_line, last_line):
        value = semantic_cell_text(
            strip_page_sidebar(lines[index]),
            "remarks",
            start,
            end,
        )
        value = re.sub(r"\s+", " ", value.strip()).upper()
        if not value or not re.search(r"[A-Z0-9]", value):
            continue
        if value not in {"AUTO", "OFF", "ON"}:
            return None
        values.append((index, value))
    if not values:
        return None

    paragraphs: list[tuple[int, int, str, int | None]] = []
    current: list[tuple[int, str]] = []

    def flush() -> None:
        if not current:
            return
        paragraphs.append(
            (
                current[0][0],
                current[-1][0],
                " ".join(value for _index, value in current),
                None,
            )
        )
        current.clear()

    for index, value in values:
        if value == "AUTO":
            flush()
            current.append((index, value))
            flush()
        elif value == "ON":
            flush()
            current.append((index, value))
        elif current and current[0][1] == "ON":
            current.append((index, value))
            flush()
        else:
            flush()
            current.append((index, value))
    flush()
    return paragraphs


def closest_row_group(
    rows: list[dict[str, object]],
    groups: list[list[int]],
    paragraph_start: int,
    paragraph_end: int,
) -> int:
    paragraph_center = (paragraph_start + paragraph_end) / 2
    candidates = []
    for index, group in enumerate(groups):
        first = int(rows[group[0]]["start_line"])
        last = int(rows[group[-1]]["start_line"])
        if paragraph_end < first:
            distance = first - paragraph_end
        elif paragraph_start > last:
            distance = paragraph_start - last
        else:
            distance = 0
        center = (first + last) / 2
        candidates.append((distance, abs(paragraph_center - center), index))
    return min(candidates)[2]


def standalone_active_test_items(
    lines: list[str],
) -> dict[int, tuple[str, str]]:
    items: dict[int, tuple[str, str]] = {}
    for index, line in enumerate(lines[:-1]):
        name = line.strip()
        if (
            line != line.lstrip()
            or not name
            or name != name.upper()
            or name in {"CAUTION:", "NOTE:"}
            or not valid_item_name(name)
        ):
            continue
        next_index = index + 1
        while next_index < len(lines) and not lines[next_index].strip():
            next_index += 1
        if (
            next_index >= len(lines)
            or not lines[next_index].lstrip().startswith("•")
        ):
            continue
        parts = []
        for description_line in lines[next_index:]:
            if re.match(
                r"^\s*(?:Operation|Test item)\s{2,}",
                description_line,
                re.IGNORECASE,
            ):
                break
            if (
                description_line == description_line.lstrip()
                and description_line.strip() == description_line.strip().upper()
                and description_line.strip() not in {"CAUTION:", "NOTE:"}
            ):
                break
            parts.append(description_line)
        items[index] = (name, join_table_text(parts))
    return items


def standalone_work_support_items(
    lines: list[str],
) -> dict[int, tuple[str, str]]:
    candidate_pattern = re.compile(
        r"(?:[A-Z]{2,}|[A-Z][a-z]+)"
        r"(?:\s+(?:[A-Z]{2,}|[A-Z][a-z]+)){0,5}"
    )
    section_end = next(
        (
            index
            for index, line in enumerate(lines[1:], 1)
            if re.fullmatch(
                r"(?:SELF-DIAG(?: RESULTS)?|DATA MONITOR|ACTIVE TEST|"
                r"ECU PART NUMBER)(?: MODE)?",
                re.sub(r"\s+", " ", line.strip()),
                re.IGNORECASE,
            )
        ),
        len(lines),
    )
    candidates = []
    for index, line in enumerate(lines[:section_end]):
        name = re.sub(r"\s+", " ", line.strip())
        normalized_name = name.upper()
        if (
            not candidate_pattern.fullmatch(name)
            or normalized_name in HEADER_NAMES
            or normalized_name in {"AUTO", "OFF", "ON"}
            or normalized_name.endswith((" DESCRIPTION", " MODE"))
            or re.search(
                r"\b(?:APPLICATION|MONITOR|SERVICE|TEST|WORK) ITEM\b",
                normalized_name,
            )
            or not valid_item_name(name)
        ):
            continue
        next_index = index + 1
        while next_index < len(lines) and not lines[next_index].strip():
            next_index += 1
        if next_index >= len(lines):
            continue
        next_value = re.sub(r"\s+", " ", lines[next_index].strip())
        if (
            not any(character.islower() for character in next_value)
            or not re.search(r"[.!?\"']$", next_value)
        ):
            continue
        candidates.append((index, name))

    items = {}
    for position, (index, name) in enumerate(candidates):
        next_candidate = (
            candidates[position + 1][0]
            if position + 1 < len(candidates)
            else section_end
        )
        parts = [
            line
            for line in lines[index + 1 : next_candidate]
            if line.strip()
        ]
        description = join_table_text(parts)
        if description:
            items[index] = (name, description)
    return items


def remove_semantic_column_overlap(
    description: str,
    remarks: str,
) -> str:
    if not description or not remarks:
        return description
    description_words = list(re.finditer(r"\S+", description))
    remark_words = list(re.finditer(r"\S+", remarks))

    def normalized_word(match: re.Match[str]) -> str:
        return match.group(0).strip(".,;:!?()[]{}•").lower()

    left = [normalized_word(match) for match in description_words]
    right = [normalized_word(match) for match in remark_words]
    maximum = min(len(left), len(right))
    for length in range(maximum, 2, -1):
        if left[-length:] == right[:length]:
            return description[: description_words[-length].start()].rstrip()
    return description


def semantic_table_rows(
    text: str, kind: str, width: int
) -> list[dict[str, str]]:
    lines = text.splitlines()
    sidebar_start = page_sidebar_start(lines)
    lines = [
        strip_page_sidebar(line, sidebar_start)
        for line in lines
    ]
    rows = first_column_rows("\n".join(lines), width)
    if not rows:
        return []
    table_cutoff = len(lines)
    if kind == "active_test":
        standalone_lines = set(standalone_active_test_items(lines))
        terminators = [
            index
            for index, line in enumerate(lines)
            if re.sub(r"\s+", " ", line.strip()).upper()
            in {"ECU IDENTIFICATION", "STANDARD VALUE"}
        ]
        if terminators:
            table_cutoff = min(terminators)
        rows = [
            row
            for row in rows
            if (
                int(row["start_line"]) not in standalone_lines
                and int(row["start_line"]) < table_cutoff
            )
        ]
        if not rows:
            return []
    header_index, layout = table_layout(lines, kind, rows, width)
    data_start = semantic_table_data_start(
        lines,
        header_index,
        int(rows[0]["start_line"]),
    )
    if layout and layout[0] == ("name", 0, 0):
        data_start = max(data_start, int(rows[0]["start_line"]) + 1)
    anchors = [int(row["start_line"]) for row in rows]
    table_end = min(semantic_table_end(lines, rows), table_cutoff)
    groups = (
        data_monitor_row_groups(rows)
        if kind == "data_monitor"
        else [[index] for index in range(len(rows))]
    )
    boundaries = grouped_table_boundaries(
        rows,
        groups,
        header_index,
        table_end,
    )
    boundaries[0] = data_start
    if (
        kind == "active_test"
        and len(layout) == 2
        and layout[1][0] == "description"
    ):
        description_start = layout[1][1]
        row_starts = []
        for index, anchor in enumerate(anchors):
            lower = header_index + 1 if index == 0 else anchors[index - 1] + 1
            candidates = []
            for line_index in range(lower, anchor + 1):
                candidate = join_table_text(
                    [strip_page_sidebar(lines[line_index])[description_start:]]
                )
                if re.match(
                    r"(?i)^(?:this (?:test|item)|the active test)\b",
                    candidate,
                ):
                    candidates.append(line_index)
            row_starts.append(candidates[-1] if candidates else boundaries[index])
        if all(
            left < right for left, right in zip(row_starts, row_starts[1:])
        ):
            boundaries = row_starts + [boundaries[-1]]

    paragraph_values: dict[str, dict[int, str]] = {}
    semantic_line_groups: dict[int, int] = {}
    reference_value_table = any(
        re.search(r"\bREFERENCE VALUE(?:\s+IN)?\b", line, re.IGNORECASE)
        for line in lines[header_index : int(rows[0]["start_line"])]
    )
    operation_value_table = (
        kind == "active_test"
        and len(layout) >= 3
        and re.search(
            r"\bOPERATION(?:\s+ITEM)?\b",
            lines[header_index],
            re.IGNORECASE,
        )
        is not None
    )
    operation_condition_column = next(
        (
            (start, end)
            for field, start, end in layout
            if field == "conditions"
        ),
        None,
    )
    if kind in {"data_monitor", "active_test", "work_support"}:
        semantic_layout = (
            sorted(
                layout,
                key=lambda column: {
                    "description": 0,
                    "conditions": 1,
                    "usage": 2,
                }.get(column[0], 3),
            )
            if operation_value_table
            else layout
        )
        for field, start, end in semantic_layout:
            if field in {"name", "unit"}:
                continue
            paragraphs = (
                status_reference_paragraphs(
                    lines,
                    start,
                    end,
                    data_start,
                    table_end,
                )
                if (
                    kind == "data_monitor"
                    and field == "remarks"
                    and reference_value_table
                )
                else None
            )
            if paragraphs is None:
                paragraphs = semantic_column_paragraphs(
                    lines,
                    field,
                    start,
                    end,
                    data_start,
                    table_end,
                    rows,
                    groups,
                    boundaries,
                    set(anchors),
                    operation_value_table,
                )
            if not paragraphs:
                continue
            assigned: defaultdict[int, list[str]] = defaultdict(list)
            prior_field_line_groups = dict(semantic_line_groups)
            previous_assigned_group: int | None = None
            previous_paragraph_value = ""
            for paragraph_start, paragraph_end, value, group_hint in paragraphs:
                exact_aligned_groups = [
                    prior_field_line_groups[line_index]
                    for line_index in range(
                        paragraph_start,
                        paragraph_end + 1,
                    )
                    if line_index in prior_field_line_groups
                ]
                neighbor_aligned_groups = []
                if not exact_aligned_groups:
                    neighbor_aligned_groups = [
                        prior_field_line_groups[line_index]
                        for line_index in (
                            paragraph_start - 1,
                            paragraph_end + 1,
                        )
                        if line_index in prior_field_line_groups
                    ]
                boundary_groups = [
                    group_index
                    for group_index in range(len(groups))
                    if (
                        boundaries[group_index]
                        <= paragraph_start
                        < boundaries[group_index + 1]
                        and boundaries[group_index]
                        <= paragraph_end
                        < boundaries[group_index + 1]
                    )
                ]
                start_boundary_group = next(
                    (
                        group_index
                        for group_index in range(len(groups))
                        if (
                            boundaries[group_index]
                            <= paragraph_start
                            < boundaries[group_index + 1]
                        )
                    ),
                    None,
                )
                operation_signals = (
                    [
                        clean_semantic_value(
                            semantic_cell_text(
                                lines[line_index],
                                "conditions",
                                operation_condition_column[0],
                                operation_condition_column[1],
                            )
                        )
                        for line_index in range(
                            paragraph_start,
                            paragraph_end + 1,
                        )
                        if clean_semantic_value(
                            semantic_cell_text(
                                lines[line_index],
                                "conditions",
                                operation_condition_column[0],
                                operation_condition_column[1],
                            )
                        )
                    ]
                    if operation_value_table
                    and operation_condition_column is not None
                    else []
                )
                prefix_next_group = None
                if (
                    start_boundary_group is not None
                    and start_boundary_group + 1 < len(groups)
                    and paragraph_start
                    == boundaries[start_boundary_group + 1] - 1
                    and paragraph_start not in set(anchors)
                    and start_boundary_group in assigned
                    and (
                        kind == "data_monitor"
                        or not value.startswith("•")
                    )
                    and not (
                        operation_value_table
                        and field == "description"
                        and value.upper() == "OFF"
                        and (
                            int(
                                rows[
                                    groups[start_boundary_group + 1][0]
                                ]["start_line"]
                            )
                            - paragraph_start
                            > 1
                        )
                    )
                ):
                    previous_keywords = semantic_keywords(
                        join_table_text(assigned[start_boundary_group])
                    )
                    current_keywords = semantic_keywords(value)
                    if (
                        previous_keywords
                        and current_keywords
                        and (
                            (
                                kind == "work_support"
                                and field == "description"
                                and not value.startswith("•")
                            )
                            or previous_keywords.isdisjoint(
                                current_keywords
                            )
                        )
                    ):
                        prefix_next_group = start_boundary_group + 1
                operation_name_group = None
                if (
                    (kind == "work_support" and field == "conditions")
                    or (
                        operation_value_table
                        and field == "description"
                    )
                ):
                    value_keywords = semantic_keywords(value)
                    name_scores = []
                    for candidate, group in enumerate(groups):
                        name_keywords = {
                            keyword
                            for row_index in group
                            for keyword in semantic_keywords(
                                str(rows[row_index]["name"])
                            )
                        }
                        score = sum(
                            any(
                                keyword == name_keyword
                                or (
                                    len(keyword) >= 3
                                    and len(name_keyword) >= 3
                                    and keyword[:3] == name_keyword[:3]
                                )
                                for name_keyword in name_keywords
                            )
                            for keyword in value_keywords
                        )
                        minimum_score = 2
                        if score >= minimum_score:
                            name_scores.append((score, candidate))
                    if name_scores:
                        best_score = max(score for score, _ in name_scores)
                        operation_name_group = min(
                            (
                                candidate
                                for score, candidate in name_scores
                                if score == best_score
                            ),
                            key=lambda candidate: abs(
                                int(
                                    rows[groups[candidate][0]][
                                        "start_line"
                                    ]
                                )
                                - (paragraph_start + paragraph_end) / 2
                            ),
                        )
                        if (
                            boundary_groups
                            and operation_name_group
                            < boundary_groups[0]
                            and any(
                                signal.upper() in {"ON", "OFF"}
                                for signal in operation_signals
                            )
                        ):
                            operation_name_group = None
                continue_bullet_group = (
                    previous_assigned_group is not None
                    and kind in {"active_test", "work_support"}
                    and (
                        (
                            kind == "work_support"
                            and field in {"description", "usage"}
                        )
                        or (
                            kind == "active_test"
                            and field == "description"
                        )
                        or (
                            kind == "work_support"
                            and field == "conditions"
                        )
                    )
                    and start_boundary_group
                    == previous_assigned_group + 1
                    and paragraph_start
                    < int(
                        rows[groups[start_boundary_group][0]][
                            "start_line"
                        ]
                    )
                    and value.startswith("•")
                    and previous_paragraph_value.startswith("•")
                )
                active_transition = (
                    previous_assigned_group is not None
                    and kind == "active_test"
                    and start_boundary_group
                    == previous_assigned_group + 1
                    and paragraph_start
                    < int(
                        rows[groups[start_boundary_group][0]][
                            "start_line"
                        ]
                    )
                )
                continue_active_condition_group = (
                    active_transition
                    and field == "conditions"
                    and value.startswith("•")
                    and not re.match(
                        r"^•\s*(?:Engine|Ignition switch)\s*:",
                        value,
                        re.IGNORECASE,
                    )
                )
                continue_active_usage_group = (
                    active_transition
                    and field == "usage"
                    and value.startswith("•")
                    and not re.match(
                        r"^•\s*(?:Harness and connectors|Perform)\b",
                        value,
                        re.IGNORECASE,
                    )
                )
                continue_active_description_group = (
                    active_transition
                    and operation_value_table
                    and field == "description"
                    and operation_signals
                    and operation_signals[0].upper() == "OFF"
                    and re.match(
                        r"^Stops?\b",
                        value,
                        re.IGNORECASE,
                    )
                    is not None
                )
                continue_short_value_group = (
                    previous_assigned_group is not None
                    and kind == "active_test"
                    and field == "conditions"
                    and start_boundary_group
                    == previous_assigned_group + 1
                    and paragraph_start
                    < int(
                        rows[groups[start_boundary_group][0]][
                            "start_line"
                        ]
                    )
                    and len(value) <= 24
                    and len(previous_paragraph_value) <= 24
                    and not value.startswith("•")
                    and not previous_paragraph_value.startswith("•")
                    and not value.upper().startswith("ORIGIN")
                    and (
                        not operation_value_table
                        or paragraph_end
                        == int(
                            rows[groups[start_boundary_group][0]][
                                "start_line"
                            ]
                        )
                        - 1
                    )
                )
                if exact_aligned_groups:
                    group_index = max(
                        set(exact_aligned_groups),
                        key=lambda candidate: (
                            exact_aligned_groups.count(candidate),
                            -abs(
                                (
                                    int(rows[groups[candidate][0]][
                                        "start_line"
                                    ])
                                    + int(rows[groups[candidate][-1]][
                                        "start_line"
                                    ])
                                )
                                / 2
                                - (paragraph_start + paragraph_end) / 2
                            ),
                            -candidate,
                        ),
                    )
                elif operation_name_group is not None:
                    group_index = operation_name_group
                elif (
                    kind == "data_monitor"
                    and group_hint is not None
                ):
                    group_index = group_hint
                elif (
                    continue_bullet_group
                    or continue_active_condition_group
                    or continue_active_usage_group
                    or continue_active_description_group
                    or continue_short_value_group
                ):
                    group_index = previous_assigned_group
                elif prefix_next_group is not None:
                    group_index = prefix_next_group
                elif boundary_groups:
                    group_index = boundary_groups[0]
                elif neighbor_aligned_groups:
                    group_index = max(
                        set(neighbor_aligned_groups),
                        key=lambda candidate: (
                            neighbor_aligned_groups.count(candidate),
                            -abs(
                                (
                                    int(rows[groups[candidate][0]][
                                        "start_line"
                                    ])
                                    + int(rows[groups[candidate][-1]][
                                        "start_line"
                                    ])
                                )
                                / 2
                                - (paragraph_start + paragraph_end) / 2
                            ),
                            -candidate,
                        ),
                    )
                else:
                    group_index = closest_row_group(
                        rows,
                        groups,
                        paragraph_start,
                        paragraph_end,
                    )
                assigned[group_index].append(value)
                previous_assigned_group = group_index
                previous_paragraph_value = value
                for line_index in range(
                    paragraph_start,
                    paragraph_end + 1,
                ):
                    semantic_line_groups.setdefault(
                        line_index,
                        group_index,
                    )
            paragraph_values[field] = {
                group_index: join_table_text(values)
                for group_index, values in assigned.items()
            }

    result = []
    for group_index, group in enumerate(groups):
        block = [
            strip_page_sidebar(line)
            for line in lines[
                boundaries[group_index] : boundaries[group_index + 1]
            ]
            if not line.lstrip().startswith("Revision:")
        ]
        shared_values = {
            "description": "",
            "remarks": "",
            "conditions": "",
            "usage": "",
        }
        shared_unit = ""
        for field, start, end in layout:
            if field == "name":
                continue
            if field == "unit":
                unit_text = " ".join(
                    re.sub(
                        r"\s+",
                        " ",
                        (
                            line[start:end]
                            if end is not None
                            else line[start:]
                        ).strip(),
                    )
                    for line in block
                    if (
                        line[start:end]
                        if end is not None
                        else line[start:]
                    ).strip()
                )
                shared_unit = unit_value(unit_text)
                continue
            if field in paragraph_values:
                shared_values[field] = paragraph_values[field].get(
                    group_index,
                    "",
                )
                continue
            parts = [
                semantic_cell_text(line, field, start, end)
                for line in block
            ]
            shared_values[field] = join_table_text(parts)
            if (
                shared_values[field]
                and len(shared_values[field]) < 3
                and shared_values[field].upper()
                not in {"ON", "OK", "NG", "HI", "LO"}
            ):
                shared_values[field] = ""
        if not paragraph_values and not any(
            shared_values[field]
            for field in ("description", "remarks", "conditions", "usage")
        ):
            semantic_start = next(
                (
                    start
                    for field, start, _end in layout
                    if field not in {"name", "unit"}
                ),
                width,
            )
            shared_values["description"] = join_table_text(
                clean_semantic_value(line[semantic_start:])
                for line in block
            )
        shared_values["description"] = remove_semantic_column_overlap(
            shared_values["description"],
            shared_values["remarks"],
        )
        for row_index in group:
            row = rows[row_index]
            result.append(
                {
                    "name": str(row["name"]),
                    "unit": str(row["unit"]) or shared_unit,
                    **shared_values,
                }
            )
    for left, right in zip(result, result[1:]):
        left_key = re.sub(
            r"\b(?:L|LH|R|RH)\b$",
            "SIDE",
            left["name"].upper(),
        )
        right_key = re.sub(
            r"\b(?:L|LH|R|RH)\b$",
            "SIDE",
            right["name"].upper(),
        )
        if left_key == right_key and left_key != left["name"].upper():
            for field in ("description", "remarks", "conditions", "usage"):
                if left[field] and not right[field]:
                    right[field] = left[field]
                elif right[field] and not left[field]:
                    left[field] = right[field]
    return result


def structured_section(text: str, kind: str) -> str:
    marker = TABLE_MARKERS[kind]
    lines = text.splitlines()
    starts = []
    for index, line in enumerate(lines):
        match = MODE_HEADING_RE.match(lines[index])
        heading = match.group(1).strip() if match else ""
        canonical_heading = heading.replace("MIONITOR", "MONITOR")
        if (
            heading
            and heading == heading.upper()
            and kind.replace("_", " ") in canonical_heading.lower()
        ):
            starts.append(index)
    if starts:
        start = starts[0]
        marker_indexes = [
            index
            for index, line in enumerate(lines[start:], start)
            if marker.search(line)
        ]
        if marker_indexes:
            start = marker_indexes[0]
    else:
        marker_indexes = [
            index for index, line in enumerate(lines) if marker.search(line)
        ]
        if not marker_indexes:
            return ""
        start = 0
        marker_index = marker_indexes[0]
        for index in range(marker_index, -1, -1):
            if not lines[index].strip():
                start = index + 1
                break
    end = len(lines)
    for index in range(start + 1, len(lines)):
        match = MODE_HEADING_RE.match(lines[index])
        heading = match.group(1).strip() if match else ""
        if heading and heading == heading.upper():
            end = index
            break
    return "\n".join(lines[start:end])


def leading_table_kind(text: str, previous_kind: str) -> str:
    lines = text.splitlines()
    first_mode = next(
        (
            index
            for index, line in enumerate(lines)
            if MODE_HEADING_RE.match(line)
        ),
        len(lines),
    )
    prefix = "\n".join(lines[:first_mode])
    if not prefix.strip():
        return ""
    if re.search(
        r"(?im)^\s*(?:Service item|Work item)\b",
        prefix,
    ):
        return "work_support"
    if (
        previous_kind == "work_support"
        and re.search(r"(?im)^\s*Monitor item\b", prefix)
        and not re.search(r"(?i)\[Unit\]", prefix)
    ):
        return "work_support"
    if re.search(r"(?im)^\s*Test item\b", prefix):
        header = "\n".join(
            line
            for line in lines[: min(first_mode, 12)]
            if re.search(r"(?i)\bTest item\b", line)
        )
        if not re.search(r"(?i)\bDiagnosis mode\b", header):
            return "active_test"
    if (
        not re.search(r"(?i)Cause of Auto-Cancel Display Item List", prefix)
        and re.search(
            r"(?im)^\s*(?:Monitor(?:ed)?|Display) item\b",
            prefix,
        )
    ):
        return "data_monitor"
    return ""


def leading_structured_section(text: str) -> str:
    lines = text.splitlines()
    first_mode = next(
        (
            index
            for index, line in enumerate(lines)
            if MODE_HEADING_RE.match(line)
        ),
        len(lines),
    )
    return "\n".join(lines[:first_mode])


def structured_sections(
    fragment: dict[str, object],
    kind: str,
) -> list[str]:
    text = str(fragment["text"])
    sections = []
    if fragment.get("page_start_kind") == kind:
        leading = leading_structured_section(text)
        if leading.strip():
            sections.append(leading)
    section = structured_section(text, kind)
    if section.strip() and section not in sections:
        sections.append(section)
    return sections


def service_setting_rows(text: str) -> list[dict[str, str]]:
    lines = text.splitlines()
    sidebar_start = page_sidebar_start(lines)
    lines = [
        strip_page_sidebar(line, sidebar_start)
        for line in lines
    ]
    text = "\n".join(lines)
    header_index = next(
        (
            index
            for index, line in enumerate(lines)
            if re.search(r"\bService item\b", line, re.IGNORECASE)
            and re.search(r"\bSetting item\b", line, re.IGNORECASE)
        ),
        -1,
    )
    if header_index < 0:
        return []
    setting_start = lines[header_index].lower().find("setting item")
    if setting_start < 20:
        return []
    names = first_column_rows(text, setting_start)
    if not names:
        return []
    group_starts = []
    for index in range(header_index + 1, len(lines)):
        value = lines[index][setting_start:]
        if re.match(
            r"\s*(?:MODE\s+1\*?\b|ON\*(?=\s|$))",
            value,
        ):
            group_starts.append(index)
    if len(group_starts) != len(names):
        return []
    result = []
    for group_index, (start, row) in enumerate(
        zip(group_starts, names)
    ):
        end = (
            group_starts[group_index + 1]
            if group_index + 1 < len(group_starts)
            else semantic_table_end(lines, names)
        )
        description = join_table_text(
            clean_semantic_value(
                line[setting_start:]
            )
            for line in lines[start:end]
        )
        description = re.sub(
            r"\bWithout the funcMODE 2 tion\b",
            "MODE 2 Without the function",
            description,
        )
        result.append(
            {
                "name": str(row["name"]),
                "description": description,
                "conditions": "",
                "usage": "",
            }
        )
    return result


def diagnostic_parameters(fragment: dict[str, object]) -> list[dict[str, object]]:
    if fragment["kind"] != "data_monitor":
        return []
    sections = structured_sections(fragment, "data_monitor")
    if not sections:
        return []
    rows = []
    rows_by_key = {}
    for section in sections:
        for parsed in semantic_table_rows(section, "data_monitor", 34):
            name = parsed["name"]
            unit = parsed["unit"]
            key = name.upper()
            if key in rows_by_key:
                existing = rows_by_key[key]
                for field, value in (
                    ("unit", unit),
                    ("description", parsed["description"]),
                    ("conditions", parsed["conditions"]),
                    ("remarks", parsed["remarks"]),
                ):
                    if value and not existing[field]:
                        existing[field] = value
                continue
            row = {
                "id": f"{fragment['id']}:{keyed_slug(name)}",
                "dataset_id": fragment["dataset_id"],
                "name": name,
                "ecu_id": fragment["ecu_id"],
                "unit": unit,
                "description": parsed["description"],
                "conditions": parsed["conditions"],
                "remarks": parsed["remarks"],
                "protocol": "consult-iii",
                "external_id": "",
                "request_hex": "",
                "response_offset": "",
                "response_length": "",
                "byte_order": "",
                "signed": "",
                "factor": "",
                "addend": "",
                "formula": "",
                "applicability_status": "exact_manual",
                "verification_status": "factory_defined",
                "source_fragment_id": fragment["id"],
            }
            rows_by_key[key] = row
            rows.append(row)
    return rows


def diagnostic_operations(fragment: dict[str, object]) -> list[dict[str, object]]:
    kind = str(fragment["kind"])
    if kind not in {"active_test", "work_support"}:
        return []
    sections = structured_sections(fragment, kind)
    if not sections:
        return []
    parsed_by_name = {}
    names = []
    for section in sections:
        parsed_rows = (
            service_setting_rows(section)
            if kind == "work_support"
            else []
        )
        if not parsed_rows:
            parsed_rows = semantic_table_rows(section, kind, 34)
        for parsed in parsed_rows:
            parsed_by_name.setdefault(parsed["name"], parsed)
        section_lines = section.splitlines()
        sidebar_start = page_sidebar_start(section_lines)
        section_lines = [
            strip_page_sidebar(line, sidebar_start)
            for line in section_lines
        ]
        standalone_items = (
            standalone_active_test_items(section_lines)
            if kind == "active_test"
            else standalone_work_support_items(section_lines)
        )
        for _line_index, (name, description) in standalone_items.items():
            parsed = parsed_by_name.setdefault(
                name,
                {
                    "name": name,
                    "description": "",
                    "conditions": "",
                    "usage": "",
                },
            )
            if description and not parsed["description"]:
                parsed["description"] = description
        footnotes = [
            join_table_text([match.group(1)])
            for line in section.splitlines()
            if (match := re.match(r"^\*:\s*(.+)$", line.strip()))
        ]
        if footnotes:
            for name, parsed in parsed_by_name.items():
                if (
                    name.endswith("*")
                    and not any(
                        parsed.get(field, "")
                        for field in ("description", "conditions", "usage")
                    )
                ):
                    parsed["description"] = footnotes[0]
        names.extend(parsed_by_name)
        for quoted, mode in QUOTED_OPERATION_RE.findall(section):
            expected = (
                "work_support"
                if mode.upper() == "WORK SUPPORT"
                else "active_test"
            )
            if expected == kind and valid_item_name(quoted):
                names.append(re.sub(r"\s+", " ", quoted).strip())
    rows = []
    for name in sorted(set(names)):
        parsed = parsed_by_name.get(name, {})
        rows.append(
            {
                "id": f"{fragment['id']}:{keyed_slug(name)}",
                "dataset_id": fragment["dataset_id"],
                "kind": kind,
                "name": name,
                "ecu_id": fragment["ecu_id"],
                "description": parsed.get("description", ""),
                "conditions": parsed.get("conditions", ""),
                "usage": parsed.get("usage", ""),
                "protocol": "consult-iii",
                "request_hex": "",
                "read_only": False,
                "executable": False,
                "applicability_status": "exact_manual",
                "verification_status": "factory_defined",
                "source_fragment_id": fragment["id"],
            }
        )
    return rows


def route_character_count(text: str) -> int:
    return len(re.findall(r"(?m)(?<![A-Z])[TR](?![A-Z])", text))


def header_positions(lines: list[str]) -> list[tuple[str, int]]:
    order = (
        "ECM",
        "4WD",
        "AV",
        "BCM",
        "TCM",
        "AFS",
        "M&A",
        "STRG",
        "RAS",
        "ADP",
        "ABS",
        "ICC",
        "IPDM-E",
    )
    positions: dict[str, int] = {}
    for line in lines:
        if "ECM" not in line and not (line.strip() == "AV"):
            continue
        for name in order:
            match = re.search(rf"(?<!\S){re.escape(name)}(?!\S)", line)
            if match:
                positions[name] = match.start()
    return [(name, positions[name]) for name in order if name in positions]


def can_signals(fragment: dict[str, object]) -> list[dict[str, object]]:
    if fragment["kind"] != "can_signal_matrix":
        return []
    lines = str(fragment["text"]).splitlines()
    positions = header_positions(lines[:35])
    if len(positions) < 6:
        return []
    try:
        matrix_start = next(
            index
            for index, line in enumerate(lines)
            if "Signal name/Connecting unit" in line
        )
    except StopIteration:
        return []
    boundary = min(position for _name, position in positions)
    current = ""
    rows: dict[str, dict[str, set[str]]] = {}
    pending = ""
    for line in lines[matrix_start + 1 :]:
        if line.lstrip().startswith("Revision:"):
            break
        left = re.sub(r"\s+", " ", line[:boundary].strip())
        routes = {}
        for name, position in positions:
            window = line[max(0, position - 1) : position + max(2, len(name))]
            match = re.search(r"(?<![A-Z])([TR])(?![A-Z])", window)
            if match:
                routes[name] = match.group(1)
        if left and "Signal name/Connecting unit" not in left:
            if not routes and not left.lower().endswith(("signal", "signal*")):
                if len(left) <= 50 and any(character.islower() for character in left):
                    pending = f"{pending} {left}".strip()
                continue
            current = f"{pending} {left}".strip()
            pending = ""
            current = current.rstrip("*").strip()
        if not current or not routes:
            continue
        entry = rows.setdefault(current, {"transmitters": set(), "receivers": set()})
        for ecu, direction in routes.items():
            target = "transmitters" if direction == "T" else "receivers"
            entry[target].add(ecu)

    result = []
    for name, routes in sorted(rows.items()):
        result.append(
            {
                "id": f"{fragment['id']}:{keyed_slug(name)}",
                "dataset_id": fragment["dataset_id"],
                "name": name,
                "vehicle_id": fragment["vehicle_id"],
                "bus": "v36-primary-can",
                "transmitters": sorted(routes["transmitters"]),
                "receivers": sorted(routes["receivers"]),
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
                "source_fragment_id": fragment["id"],
            }
        )
    return result


def build(
    source_root: Path,
    pack: SourcePack,
) -> dict[str, list[dict[str, object]]]:
    pdfs = sorted(source_root.glob("*.pdf"), key=lambda path: path.name.casefold())
    if len(pdfs) != pack.expected_documents:
        raise CatalogError(
            f"{source_root}: found {len(pdfs)} PDF files, "
            f"expected {pack.expected_documents}"
        )

    documents = []
    fragments = []
    discoveries = []
    dtcs = []
    parameters = []
    operations = []
    signals = []
    unparsed = []

    for number, path in enumerate(pdfs, 1):
        print(f"[{number:02d}/{len(pdfs)}] {path.name}", flush=True)
        pages = pdf_pages(path)
        expected_pages = pdf_page_count(path)
        if len(pages) != expected_pages:
            raise CatalogError(
                f"{path}: pdftotext returned {len(pages)} pages, pdfinfo reports "
                f"{expected_pages}"
            )
        labels = [page_label(page) for page in pages]
        code = section_code(labels, path.stem)
        document_id = f"{pack.dataset_id}:{slug(path.stem)}"
        document = {
            "id": document_id,
            "dataset_id": pack.dataset_id,
            "filename": path.name,
            "title": path.stem,
            "section_code": code,
            "sha256": sha256_file(path),
            "page_count": expected_pages,
            "source_path": path.name,
        }
        documents.append(document)

        all_text = "\n".join(pages)
        discovery = {
            "document_id": document_id,
            **{
                kind: bool(pattern.search(all_text))
                for kind, pattern in MENTION_PATTERNS.items()
            },
            "fragments": 0,
            "dtc_tokens": len(set(extract_dtc_codes(all_text))),
        }

        previous_kind = ""
        previous_page = 0
        for pdf_page, text in enumerate(pages, 1):
            explicit = explicit_kinds(text)
            page_start_kind = (
                leading_table_kind(text, previous_kind)
                if set(explicit)
                & {"data_monitor", "active_test", "work_support"}
                else ""
            )
            inherited = carry_kind(
                previous_kind,
                text,
                pdf_page - previous_page,
            )
            kinds = list(explicit)
            if inherited and inherited not in kinds:
                kinds.insert(0, inherited)
            if page_start_kind and page_start_kind not in kinds:
                kinds.insert(0, page_start_kind)
            if explicit:
                previous_kind = kinds[-1]
                previous_page = pdf_page
            elif not kinds:
                previous_kind = ""
                previous_page = 0
            for kind in kinds:
                fid = fragment_id(document_id, pdf_page, kind)
                info_match = INFOID_RE.search(text)
                fragment = {
                    "id": fid,
                    "dataset_id": pack.dataset_id,
                    "document_id": document_id,
                    "pdf_page": pdf_page,
                    "page_label": labels[pdf_page - 1],
                    "info_id": info_match.group(1) if info_match else "",
                    "kind": kind,
                    "heading": page_heading(text),
                    "ecu_id": infer_ecu_id(path.stem, text, pack.vehicle_id),
                    "vehicle_id": pack.vehicle_id,
                    **(
                        {"page_start_kind": page_start_kind}
                        if page_start_kind
                        else {}
                    ),
                    "dtc_codes": extract_dtc_codes(text),
                    "text_sha256": sha256_text(text),
                    "text": text,
                }
                fragments.append(fragment)
                discovery["fragments"] += 1
                dtcs.extend(dtc_definitions(fragment))
                parsed_parameters = diagnostic_parameters(fragment)
                parameters.extend(parsed_parameters)
                parsed_operations = diagnostic_operations(fragment)
                operations.extend(parsed_operations)
                parsed_signals = can_signals(fragment)
                signals.extend(parsed_signals)

                expected_rows = kind in {
                    "dtc_index",
                    "data_monitor",
                    "active_test",
                    "work_support",
                    "can_signal_matrix",
                }
                parsed_count = (
                    len(dtc_definitions(fragment))
                    + len(parsed_parameters)
                    + len(parsed_operations)
                    + len(parsed_signals)
                )
                if expected_rows and parsed_count == 0:
                    unparsed.append(
                        {
                            "id": f"{fid}:unparsed",
                            "dataset_id": pack.dataset_id,
                            "document_id": document_id,
                            "pdf_page": pdf_page,
                            "page_label": labels[pdf_page - 1],
                            "kind": kind,
                            "reason": "recognized section produced no structured rows",
                            "source_fragment_id": fid,
                        }
                    )
        discoveries.append(discovery)

    for rows, fields in (
        (documents, ("id",)),
        (fragments, ("id",)),
        (dtcs, ("id",)),
        (parameters, ("id",)),
        (operations, ("id",)),
        (signals, ("id",)),
        (unparsed, ("id",)),
    ):
        require_unique(rows, fields)
    return {
        "documents": documents,
        "discovery": discoveries,
        "fragments": fragments,
        "dtc_definitions": dtcs,
        "diagnostic_parameters": parameters,
        "diagnostic_operations": operations,
        "can_signals": signals,
        "unparsed": unparsed,
    }


def write(output: Path, catalog: dict[str, list[dict[str, object]]]) -> None:
    write_csv(output / "documents.csv", DOCUMENT_FIELDS, catalog["documents"])
    write_csv(output / "discovery.csv", DISCOVERY_FIELDS, catalog["discovery"])
    write_jsonl(output / "fragments.jsonl", catalog["fragments"])
    write_csv(output / "dtc_definitions.csv", DTC_FIELDS, catalog["dtc_definitions"])
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
    write_csv(output / "can_signals.csv", CAN_FIELDS, catalog["can_signals"])
    write_csv(output / "unparsed.csv", UNPARSED_FIELDS, catalog["unparsed"])


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("source_root", type=Path)
    result.add_argument(
        "--pack",
        type=Path,
        default=DEFAULT_PACK,
        help="source pack TOML that names the dataset and its output directory",
    )
    result.add_argument(
        "--output",
        type=Path,
        default=None,
        help="output directory; defaults to the source pack directory",
    )
    result.add_argument("--check", action="store_true", help="extract without writing")
    return result


def main() -> int:
    args = parser().parse_args()
    source_root = args.source_root.expanduser().resolve()
    try:
        pack = load_pack(args.pack.expanduser().resolve())
        catalog = build(source_root, pack)
    except (OSError, CatalogError, tomllib.TOMLDecodeError) as error:
        print(error, file=sys.stderr)
        return 1
    print(
        "ESM: "
        f"documents={len(catalog['documents'])}, "
        f"fragments={len(catalog['fragments'])}, "
        f"dtc_definitions={len(catalog['dtc_definitions'])}, "
        f"parameters={len(catalog['diagnostic_parameters'])}, "
        f"operations={len(catalog['diagnostic_operations'])}, "
        f"can_signals={len(catalog['can_signals'])}, "
        f"unparsed={len(catalog['unparsed'])}"
    )
    if not args.check:
        output = args.output if args.output is not None else pack.output
        write(output, catalog)
        try:
            shown = output.relative_to(ROOT)
        except ValueError:
            shown = output
        print(f"Wrote {shown}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
