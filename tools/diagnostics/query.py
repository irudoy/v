#!/usr/bin/env python3
"""Read-only queries and verified DBC export for the diagnostic Memgraph layer."""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
import textwrap
from decimal import Decimal, InvalidOperation
from itertools import product
from pathlib import Path
from typing import Any


BOLT = "bolt://localhost:7687"

STATIC_BINDING_QUERY = """
MATCH (binding:DiagnosticBinding)-[:BINDS_DIAGNOSTIC]->(diagnostic)
MATCH (binding)-[:BINDS_FIRMWARE]->(firmware)
WITH binding, diagnostic, firmware,
     toLower(
       coalesce(binding.diagnostic_name, '') + ' ' +
       coalesce(binding.diagnostic_key, '') + ' ' +
       coalesce(binding.kind, '') + ' ' +
       coalesce(binding.note, '') + ' ' +
       coalesce(firmware.addr, '')
     ) AS search_text
WHERE ($rom = '' OR binding.rom = $rom)
  AND (
    $term = ''
    OR (
      $is_identifier
      AND (
        toLower(binding.diagnostic_key) = $identifier
        OR toLower(firmware.addr) = $identifier
      )
    )
    OR (NOT $is_identifier AND search_text CONTAINS toLower($term))
  )
RETURN binding.rom AS rom,
       binding.kind AS kind,
       labels(firmware) AS firmware_labels,
       firmware.addr AS firmware_addr,
       binding.diagnostic_label AS diagnostic_label,
       binding.diagnostic_key AS diagnostic_key,
       binding.diagnostic_name AS diagnostic_name,
       binding.confidence AS confidence,
       binding.firmware_confidence_prop AS firmware_confidence_prop,
       binding.firmware_confidence AS firmware_confidence,
       binding.applicability AS applicability,
       binding.rom_scope AS rom_scope,
       binding.priority AS priority,
       binding.source_claim_label AS source_claim_label,
       binding.source_claim_id AS source_claim_id,
       binding.source_applicability AS source_applicability,
       binding.source_verification AS source_verification,
       binding.source_dataset_id AS source_dataset_id,
       binding.evidence AS evidence,
       binding.note AS note
ORDER BY priority DESC, rom, diagnostic_key, firmware_addr
LIMIT $limit
"""

DTC_EXISTS_QUERY = """
MATCH (code:DtcCode {code:$code})
RETURN code.code AS code
"""

DTC_DESCRIPTOR_QUERY = """
MATCH (descriptor:RomDtcDescriptor)-[:ENCODES]->(code:DtcCode {code:$code})
MATCH (descriptor)-[:IN_ROM]->(rom:Rom)
RETURN DISTINCT rom.id AS rom,
       descriptor.index AS index,
       descriptor.record_addr AS record_addr,
       descriptor.attribute_addr AS attribute_addr,
       descriptor.attribute_hex AS attribute_hex
ORDER BY rom, index
"""

DTC_DEFINITION_QUERY = """
MATCH (definition:DtcDefinition)-[:DEFINES]->(:DtcCode {code:$code})
OPTIONAL MATCH (definition)-[:RESTS_ON]->(fragment:SourceFragment)
RETURN DISTINCT definition.title AS title,
       definition.native_code AS native_code,
       definition.ecu_id AS ecu_id,
       definition.applicability_status AS applicability,
       definition.dataset_id AS dataset_id,
       fragment.document_id AS document_id,
       fragment.pdf_page AS pdf_page,
       fragment.page_label AS page_label
ORDER BY dataset_id, document_id, pdf_page, title
"""

DTC_DETAIL_QUERY = """
MATCH (detail:SourceFragment)-[:DESCRIBES_DTC]->(code:DtcCode {code:$code})
WHERE detail.kind = 'dtc_detail'
  AND (
    $include_mentions
    OR toUpper(coalesce(detail.heading, '')) CONTAINS code.code
  )
RETURN DISTINCT detail.heading AS heading,
       detail.document_id AS document_id,
       detail.pdf_page AS pdf_page,
       detail.page_label AS page_label,
       detail.dataset_id AS dataset_id,
       toUpper(coalesce(detail.heading, '')) CONTAINS code.code AS primary,
       CASE WHEN $include_detail_text THEN detail.text ELSE null END AS text
ORDER BY primary DESC, document_id, pdf_page
"""

DTC_SEARCH_QUERY = """
MATCH (definition:DtcDefinition)-[:DEFINES]->(code:DtcCode)
OPTIONAL MATCH (definition)-[:RESTS_ON]->(fragment:SourceFragment)
WITH definition, code, fragment,
     toLower(
       coalesce(code.code, '') + ' ' +
       coalesce(definition.title, '') + ' ' +
       coalesce(definition.native_code, '')
     ) AS search_text
WITH definition, code, fragment,
     search_text CONTAINS toLower($term) AS name_match,
     any(phrase IN $phrases WHERE search_text CONTAINS phrase) AS semantic_match,
     any(alias IN $aliases WHERE search_text CONTAINS alias) AS alias_match
WHERE name_match OR semantic_match OR alias_match
RETURN DISTINCT code.code AS code,
       definition.title AS title,
       definition.native_code AS native_code,
       definition.ecu_id AS ecu_id,
       definition.applicability_status AS applicability,
       definition.dataset_id AS dataset_id,
       fragment.document_id AS document_id,
       fragment.pdf_page AS pdf_page,
       fragment.page_label AS page_label,
       CASE
         WHEN name_match THEN 'name'
         WHEN semantic_match THEN 'semantics'
         ELSE 'alias'
       END AS match_scope
ORDER BY
  CASE definition.applicability_status
    WHEN 'exact_manual' THEN 0
    WHEN 'homologous_community' THEN 1
    WHEN 'homologous_profile' THEN 2
    WHEN 'nissan_family_candidate' THEN 3
    WHEN 'generic_legacy' THEN 4
    ELSE 9
  END,
  CASE WHEN coalesce(definition.ecu_id, '') ENDS WITH ':ecm' THEN 0 ELSE 1 END,
  code, title, dataset_id
LIMIT $limit
"""

MONITOR_QUERY = """
MATCH (definition:ParameterDefinition)-[:DEFINES]->(parameter:DiagnosticParameter)
WITH definition, parameter,
     toLower(
       coalesce(definition.name, '') + ' ' +
       coalesce(definition.external_id, '')
     ) AS name_text,
     toLower(
       coalesce(definition.name, '') + ' ' +
       coalesce(definition.external_id, '') + ' ' +
       coalesce(definition.description, '') + ' ' +
       coalesce(definition.conditions, '') + ' ' +
       coalesce(definition.remarks, '') + ' ' +
       coalesce(definition.formula, '')
     ) AS semantic_text
WITH definition, parameter,
     (
       name_text CONTAINS toLower($term)
     ) AS name_match,
     (
       any(phrase IN $phrases WHERE semantic_text CONTAINS phrase)
     ) AS semantic_match,
     any(alias IN $aliases WHERE semantic_text CONTAINS alias) AS alias_match
WHERE (
    $is_identifier
    AND (
      toLower(replace(
        toLower(coalesce(definition.external_id, '')), '0x', ''
      )) = $identifier
      OR toLower(coalesce(definition.request_hex, '')) = $identifier
    )
  )
  OR (
    NOT $is_identifier
    AND (name_match OR semantic_match OR alias_match)
  )
OPTIONAL MATCH (request:DiagnosticRequest)-[:RETURNS]->(parameter)
WHERE request.dataset_id = definition.dataset_id
OPTIONAL MATCH (definition)-[:RESTS_ON]->(fragment:SourceFragment)
OPTIONAL MATCH (request)-[:RESTS_ON]->(request_fragment:SourceFragment)
WITH parameter, definition, fragment,
     name_match, semantic_match, alias_match,
     collect(DISTINCT CASE WHEN request IS NULL THEN null ELSE {
       id:request.id, request_hex:request.request_hex,
       service_id:request.service_id, protocol:request.protocol,
       applicability:request.applicability_status,
       verification:request.verification_status,
       dataset_id:request.dataset_id,
       document_id:request_fragment.document_id,
       pdf_page:request_fragment.pdf_page
     } END) AS requests
RETURN parameter.id AS parameter_id,
       definition.name AS name,
       definition.ecu_id AS ecu_id,
       definition.external_id AS external_id,
       definition.request_hex AS definition_request,
       definition.unit AS unit,
       definition.description AS description,
       definition.conditions AS conditions,
       definition.remarks AS remarks,
       definition.formula AS formula,
       definition.factor AS factor,
       definition.addend AS addend,
       definition.protocol AS protocol,
       definition.applicability_status AS applicability,
       definition.verification_status AS verification,
       definition.dataset_id AS dataset_id,
       fragment.document_id AS document_id,
       fragment.pdf_page AS pdf_page,
       CASE
         WHEN $is_identifier THEN 'identifier'
         WHEN name_match THEN 'name'
         WHEN semantic_match THEN 'semantics'
         ELSE 'alias'
       END AS match_scope,
       requests
ORDER BY
  CASE definition.applicability_status
    WHEN 'exact_manual' THEN 0
    WHEN 'homologous_community' THEN 1
    WHEN 'homologous_profile' THEN 2
    WHEN 'nissan_family_candidate' THEN 3
    WHEN 'generic_legacy' THEN 4
    ELSE 9
  END,
  CASE WHEN coalesce(definition.ecu_id, '') ENDS WITH ':ecm' THEN 0 ELSE 1 END,
  CASE
    WHEN $is_identifier THEN 0
    WHEN name_match THEN 0
    WHEN semantic_match THEN 1
    ELSE 2
  END,
  definition_request, name, dataset_id
LIMIT $limit
"""

CAN_QUERY = """
MATCH (signal:CanSignal)
OPTIONAL MATCH (definition:CanSignalDefinition)-[:DEFINES]->(signal)
OPTIONAL MATCH (definition)-[:TRANSMITTER]->(transmitter:Ecu)
OPTIONAL MATCH (definition)-[:RECEIVER]->(receiver:Ecu)
OPTIONAL MATCH (definition)-[:RESTS_ON]->(fragment:SourceFragment)
OPTIONAL MATCH
  (fragment)-[:IN_DOCUMENT]->(:SourceDocument)-[:IN_PACK]->(pack:SourcePack)
WITH signal, definition, fragment, pack,
     collect(DISTINCT transmitter.id) AS transmitters,
     collect(DISTINCT receiver.id) AS receivers
WITH signal,
     collect(DISTINCT CASE WHEN definition IS NULL THEN null ELSE {
       id:definition.id, name:definition.name,
       vehicle_id:definition.vehicle_id, bus:definition.bus,
       can_id:definition.can_id, transmitters:transmitters,
       receivers:receivers, dataset_id:definition.dataset_id,
       applicability:pack.applicability_status,
       source_kind:pack.kind, source_tier:pack.source_tier,
       binding_status:definition.binding_status,
       document_id:fragment.document_id, pdf_page:fragment.pdf_page
     } END) AS definitions
OPTIONAL MATCH (binding:CanSignalBinding)-[:BINDS_SIGNAL]->(signal)
OPTIONAL MATCH (binding)-[:BINDS_FRAME]->(frame:CanFrame)
OPTIONAL MATCH (binding)-[:RESTS_ON]->(binding_fragment:SourceFragment)
WITH signal, definitions,
     collect(DISTINCT CASE WHEN binding IS NULL THEN null ELSE {
       id:binding.id,
       vehicle_id:coalesce(binding.vehicle_id, frame.vehicle_id),
       bus:coalesce(binding.bus, frame.bus), can_id:frame.can_id,
       byte_offset:binding.byte_offset, bit_offset:binding.bit_offset,
       bit_length:binding.bit_length, byte_order:binding.byte_order,
       signed:binding.signed, factor:binding.factor,
       addend:binding.addend, unit:binding.unit,
       verification:binding.verification_status,
       applicability:binding.applicability_status,
       dataset_id:binding.dataset_id,
       document_id:binding_fragment.document_id,
       pdf_page:binding_fragment.pdf_page
     } END) AS bindings
WHERE toLower(coalesce(signal.name, '')) CONTAINS toLower($term)
   OR any(definition IN definitions WHERE
       toLower(coalesce(definition.name, '')) CONTAINS toLower($term)
       OR toLower(coalesce(definition.can_id, '')) = toLower($can_id))
   OR any(phrase IN $phrases WHERE
       toLower(coalesce(signal.name, '')) CONTAINS phrase
       OR any(definition IN definitions WHERE
         toLower(coalesce(definition.name, '')) CONTAINS phrase))
   OR any(alias IN $aliases WHERE
     toLower(coalesce(signal.name, '')) CONTAINS alias
     OR any(definition IN definitions WHERE
       toLower(coalesce(definition.name, '')) CONTAINS alias))
   OR any(binding IN bindings WHERE
       toLower(coalesce(binding.can_id, '')) = toLower($can_id))
RETURN signal.id AS signal_id, signal.name AS signal, definitions, bindings
ORDER BY
  CASE
    WHEN any(definition IN definitions WHERE
      definition.applicability = 'exact_manual')
      OR any(binding IN bindings WHERE
        binding.applicability = 'exact_manual') THEN 0
    WHEN any(definition IN definitions WHERE
      definition.applicability = 'homologous_community')
      OR any(binding IN bindings WHERE
        binding.applicability = 'homologous_community') THEN 1
    WHEN any(definition IN definitions WHERE
      definition.applicability = 'homologous_profile')
      OR any(binding IN bindings WHERE
        binding.applicability = 'homologous_profile') THEN 2
    WHEN any(definition IN definitions WHERE
      definition.applicability = 'nissan_family_candidate')
      OR any(binding IN bindings WHERE
        binding.applicability = 'nissan_family_candidate') THEN 3
    WHEN any(definition IN definitions WHERE
      definition.applicability = 'generic_legacy')
      OR any(binding IN bindings WHERE
        binding.applicability = 'generic_legacy') THEN 4
    ELSE 9
  END,
  signal
LIMIT $limit
"""

OPERATION_QUERY = """
MATCH (operation:DiagnosticOperation)
WITH operation,
     toLower(coalesce(operation.name, '')) AS name_text,
     toLower(
       coalesce(operation.name, '') + ' ' +
       coalesce(operation.description, '') + ' ' +
       coalesce(operation.conditions, '') + ' ' +
       coalesce(operation.usage, '')
     ) AS semantic_text
WITH operation,
     name_text CONTAINS toLower($term) AS name_match,
     toLower(coalesce(operation.kind, '')) CONTAINS $kind_term AS kind_match,
     any(phrase IN $phrases WHERE semantic_text CONTAINS phrase)
       AS semantic_match,
     any(alias IN $aliases WHERE semantic_text CONTAINS alias) AS alias_match
WHERE name_match OR kind_match OR semantic_match OR alias_match
OPTIONAL MATCH (operation)-[:RESTS_ON]->(fragment:SourceFragment)
RETURN operation.name AS name,
       operation.kind AS kind,
       operation.ecu_id AS ecu_id,
       operation.description AS description,
       operation.conditions AS conditions,
       operation.usage AS usage,
       operation.protocol AS protocol,
       operation.request_hex AS request_hex,
       operation.read_only AS read_only,
       operation.executable AS executable,
       operation.applicability_status AS applicability,
       operation.dataset_id AS dataset_id,
       fragment.document_id AS document_id,
       fragment.pdf_page AS pdf_page,
       CASE
         WHEN name_match THEN 'name'
         WHEN kind_match THEN 'kind'
         WHEN semantic_match THEN 'semantics'
         ELSE 'alias'
       END AS match_scope
ORDER BY
  CASE operation.applicability_status
    WHEN 'exact_manual' THEN 0
    WHEN 'homologous_community' THEN 1
    WHEN 'homologous_profile' THEN 2
    WHEN 'nissan_family_candidate' THEN 3
    WHEN 'generic_legacy' THEN 4
    ELSE 9
  END,
  CASE WHEN coalesce(operation.ecu_id, '') ENDS WITH ':ecm' THEN 0 ELSE 1 END,
  CASE
    WHEN name_match OR kind_match THEN 0
    WHEN semantic_match THEN 1
    ELSE 2
  END,
  kind, name, dataset_id
LIMIT $limit
"""

COVERAGE_QUERY = """
MATCH (rom:Rom)<-[:IN_ROM]-(descriptor:RomDtcDescriptor)-[:ENCODES]->(code:DtcCode)
WITH rom, count(descriptor) AS descriptors, count(DISTINCT code) AS unique_codes,
     collect(DISTINCT code) AS codes
UNWIND codes AS code
OPTIONAL MATCH (definition:DtcDefinition)-[:DEFINES]->(code)
WITH rom, descriptors, unique_codes,
     count(DISTINCT CASE WHEN definition IS NOT NULL THEN code END) AS documented_codes,
     count(DISTINCT CASE
       WHEN definition.applicability_status = 'exact_manual'
        AND definition.ecu_id ENDS WITH ':ecm' THEN code END
     ) AS exact_manual_codes
RETURN rom.id AS rom, descriptors, unique_codes, documented_codes,
       exact_manual_codes,
       toFloat(exact_manual_codes) * 100.0 / unique_codes AS exact_manual_percent
ORDER BY rom
"""

SOURCE_COVERAGE_QUERY = """
MATCH (pack:SourcePack)
OPTIONAL MATCH (document:SourceDocument)-[:IN_PACK]->(pack)
OPTIONAL MATCH (fragment:SourceFragment)-[:IN_DOCUMENT]->(document)
RETURN pack.id AS dataset_id, pack.kind AS kind, pack.title AS title,
       pack.applicability_status AS applicability,
       count(DISTINCT document) AS documents,
       count(DISTINCT fragment) AS fragments
ORDER BY dataset_id
"""

CONFLICT_QUERY = """
MATCH (request:DiagnosticRequest)-[:RETURNS]->(parameter:DiagnosticParameter)
      <-[:DEFINES]-(definition:ParameterDefinition)
WHERE request.service_id = '0x22'
  AND coalesce(request.request_hex, '') <> ''
  AND (definition.formula IS NOT NULL OR definition.factor IS NOT NULL)
WITH DISTINCT request.request_hex AS request_hex, definition
WITH request_hex,
     collect(DISTINCT {
       dataset_id:definition.dataset_id, name:definition.name,
       formula:definition.formula, factor:definition.factor,
       addend:definition.addend, unit:definition.unit,
       verification:definition.verification_status
     }) AS definitions
RETURN request_hex, definitions
ORDER BY request_hex
"""

DBC_QUERY = """
MATCH (binding:CanSignalBinding)-[:BINDS_SIGNAL]->(signal:CanSignal)
MATCH (binding)-[:BINDS_FRAME]->(frame:CanFrame)
WHERE binding.verification_status = 'hardware_verified'
OPTIONAL MATCH (definition:CanFrameDefinition)-[:DEFINES]->(frame)
RETURN frame.can_id AS can_id,
       max(coalesce(definition.dlc, binding.byte_offset + binding.byte_length)) AS dlc,
       signal.name AS signal_name,
       binding.byte_offset AS byte_offset,
       binding.bit_offset AS bit_offset,
       binding.bit_length AS bit_length,
       binding.byte_order AS byte_order,
       binding.signed AS signed,
       binding.factor AS factor,
       binding.addend AS addend,
       binding.unit AS unit
ORDER BY can_id, byte_offset, bit_offset, signal_name
"""


def record_dicts(result: Any) -> list[dict[str, Any]]:
    return [dict(record) for record in result]


def clean_optional_evidence(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    for row in rows:
        for field in (
            "descriptors",
            "definitions",
            "details",
            "requests",
            "bindings",
        ):
            values = row.get(field)
            if isinstance(values, list):
                row[field] = [
                    value
                    for value in values
                    if isinstance(value, dict)
                    and any(item is not None for item in value.values())
                ]
    return rows


def query_dtc(
    session: Any,
    code: str,
    include_mentions: bool,
    include_detail_text: bool,
) -> list[dict[str, Any]]:
    matches = record_dicts(session.run(DTC_EXISTS_QUERY, code=code))
    if not matches:
        return []
    row = {
        "code": matches[0]["code"],
        "descriptors": record_dicts(
            session.run(DTC_DESCRIPTOR_QUERY, code=code)
        ),
        "definitions": record_dicts(
            session.run(DTC_DEFINITION_QUERY, code=code)
        ),
        "details": record_dicts(
            session.run(
                DTC_DETAIL_QUERY,
                code=code,
                include_mentions=include_mentions,
                include_detail_text=include_detail_text,
            )
        ),
    }
    return prepare_dtc_rows([row], include_detail_text)


def prepare_dtc_rows(
    rows: list[dict[str, Any]], include_detail_text: bool
) -> list[dict[str, Any]]:
    clean_optional_evidence(rows)
    if include_detail_text:
        return rows
    for row in rows:
        details = row.get("details", [])
        if isinstance(details, list):
            details.sort(
                key=lambda detail: (
                    not bool(detail.get("primary")),
                    str(detail.get("document_id") or ""),
                    int(detail.get("pdf_page") or 0),
                )
                if isinstance(detail, dict)
                else (True, "", 0)
            )
        for detail in row.get("details", []):
            if isinstance(detail, dict):
                detail.pop("text", None)
    return rows


def canonical_dtc_code(value: str) -> str | None:
    code = value.strip().upper()
    return code if re.fullmatch(r"[PBCU][0-9A-F]{4}", code) else None


SEARCH_STOP_WORDS = {
    "a",
    "an",
    "and",
    "for",
    "of",
    "the",
    "to",
}

SEMANTIC_SEARCH_ALIASES = {
    "accelerator": ("accel",),
    "accelerator pedal": ("accel",),
    "accelerator pedal position": ("accel",),
    "cam timing": ("int/v", "ex vtc", "exh/v", "exh v/t", "ext v/t"),
    "camshaft position sensor": ("cmp sen",),
    "coolant": ("coolan",),
    "coolant temperature": ("coolan",),
    "crankshaft position sensor": ("ckp sen",),
    "engine coolant temperature": ("coolan",),
    "exhaust valve timing": (
        "ex vtc",
        "exh/v",
        "exh v/t",
        "ext v/t",
        "exhaust camshaft",
    ),
    "injection pulse": ("inj pulse",),
    "intake valve timing": ("int/v", "intake camshaft"),
    "mass air flow": ("maf", "mass airflow"),
    "throttle": ("thrtl",),
    "throttle position": ("thrtl", "tp sen"),
    "throttle position sensor": ("thrtl", "tp sen"),
    "valve lift": ("vvel",),
    "variable valve event lift": ("vvel",),
    "vehicle speed": ("veh speed",),
}

DTC_SEARCH_ALIASES = {
    **SEMANTIC_SEARCH_ALIASES,
    "camshaft position sensor": ("cmp sen",),
    "coolant": ("coolan", "ect sen"),
    "coolant temperature": ("coolan", "ect sen"),
    "crankshaft position sensor": ("ckp sen",),
    "engine coolant temperature": ("coolan", "ect sen"),
    "intake air temperature": ("iat sen",),
    "knock sensor": ("knock sen",),
    "mass air flow": ("maf sen",),
    "throttle position": ("thrtl", "tp sen"),
    "throttle position sensor": ("thrtl", "tp sen"),
}


def normalized_search_phrase(value: str) -> str:
    return " ".join(
        token
        for token in re.findall(r"[a-z0-9]+", value.casefold())
        if len(token) >= 2 and token not in SEARCH_STOP_WORDS
    )


def semantic_search_tokens(value: str) -> list[str]:
    return list(dict.fromkeys(normalized_search_phrase(value).split()))


def semantic_search_phrases(value: str) -> list[str]:
    tokens = semantic_search_tokens(value)
    if len(tokens) <= 1:
        return tokens
    if len(tokens) > 5:
        return [" ".join(tokens)]
    return [
        "".join(
            token + (separators[index] if index < len(separators) else "")
            for index, token in enumerate(tokens)
        )
        for separators in product((" ", "-", "/"), repeat=len(tokens) - 1)
    ]


def semantic_search_aliases(value: str) -> list[str]:
    return list(SEMANTIC_SEARCH_ALIASES.get(normalized_search_phrase(value), ()))


def dtc_search_aliases(value: str) -> list[str]:
    return list(DTC_SEARCH_ALIASES.get(normalized_search_phrase(value), ()))


APPLICABILITY_ORDER = {
    "exact_manual": 0,
    "homologous_community": 1,
    "homologous_profile": 2,
    "nissan_family_candidate": 3,
    "generic_legacy": 4,
}


def evidence_sort_key(value: Any) -> tuple[int, str, str, int]:
    if not isinstance(value, dict):
        return 99, "", "", 0
    return (
        APPLICABILITY_ORDER.get(str(value.get("applicability") or ""), 9),
        str(value.get("dataset_id") or ""),
        str(value.get("document_id") or ""),
        int(value.get("pdf_page") or 0),
    )


def sort_can_evidence(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    clean_optional_evidence(rows)
    for row in rows:
        for field in ("definitions", "bindings"):
            values = row.get(field)
            if isinstance(values, list):
                values.sort(key=evidence_sort_key)
    return rows


def canonical_can_identifier(value: str) -> str | None:
    compact = re.sub(r"[\s_]+", "", value.strip())
    match = re.fullmatch(r"(?:0[xX])?([0-9a-fA-F]{1,8})", compact)
    if not match:
        return None
    return f"0x{int(match.group(1), 16):X}"


def canonical_can_term(value: str) -> str:
    return canonical_can_identifier(value) or value


def filter_can_evidence(
    rows: list[dict[str, Any]],
    can_id: str | None,
) -> list[dict[str, Any]]:
    sort_can_evidence(rows)
    if can_id is None:
        return rows
    normalized = can_id.lower()
    result = []
    for row in rows:
        item = dict(row)
        for field in ("definitions", "bindings"):
            item[field] = [
                evidence
                for evidence in item.get(field, [])
                if isinstance(evidence, dict)
                and str(evidence.get("can_id") or "").lower() == normalized
            ]
        if item["definitions"] or item["bindings"]:
            result.append(item)
    return result


def canonical_monitor_identifier(value: str) -> str | None:
    compact = re.sub(r"(?i)0x", "", value.strip())
    compact = re.sub(r"[\s,_:-]+", "", compact)
    if not re.fullmatch(r"[0-9a-fA-F]+", compact):
        return None
    if not any(character.isdigit() for character in compact):
        return None
    return compact.lower()


def canonical_operation_kind(value: str) -> str:
    return re.sub(r"[\s-]+", "_", value.strip().lower())


def canonical_binding_identifier(value: str) -> str | None:
    code = canonical_dtc_code(value)
    if code is not None:
        return code.lower()
    address = value.strip().lower()
    if address.startswith("0x"):
        address = address[2:]
    return address if re.fullmatch(r"[0-9a-f]{8}", address) else None


def nonnegative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be greater than or equal to zero")
    return parsed


UNIT_ALIASES = {
    "deg": "degc",
    "degc": "degc",
    "degca": "degca",
    "g/s": "g/s",
    "gm/s": "g/s",
    "kph": "km/h",
    "km/h": "km/h",
    "km/час": "km/h",
    "msec": "ms",
    "ms": "ms",
    "rpm": "rpm",
    "v": "v",
    "вольт": "v",
    "об/мин": "rpm",
    "°": "degc",
    "°c": "degc",
    "°с": "degc",
    "°ca": "degca",
}


def canonical_unit(value: Any) -> str:
    text = re.sub(r"\s+", "", str(value or "").strip().lower())
    return UNIT_ALIASES.get(text, text)


def decimal_value(value: Any) -> Decimal | None:
    if value is None or value == "":
        return None
    try:
        return Decimal(str(value))
    except InvalidOperation:
        return None


def affine_expression(node: ast.AST) -> tuple[Decimal, Decimal]:
    if isinstance(node, ast.Expression):
        return affine_expression(node.body)
    if isinstance(node, ast.Name) and node.id.lower() in {"a", "raw"}:
        return Decimal(1), Decimal(0)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return Decimal(0), Decimal(str(node.value))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        factor, addend = affine_expression(node.operand)
        if isinstance(node.op, ast.USub):
            return -factor, -addend
        return factor, addend
    if not isinstance(node, ast.BinOp):
        raise ValueError("formula is not affine")
    left_factor, left_addend = affine_expression(node.left)
    right_factor, right_addend = affine_expression(node.right)
    if isinstance(node.op, ast.Add):
        return left_factor + right_factor, left_addend + right_addend
    if isinstance(node.op, ast.Sub):
        return left_factor - right_factor, left_addend - right_addend
    if isinstance(node.op, ast.Mult):
        if left_factor == 0:
            return (
                right_factor * left_addend,
                right_addend * left_addend,
            )
        if right_factor == 0:
            return (
                left_factor * right_addend,
                left_addend * right_addend,
            )
        raise ValueError("formula multiplies two variable expressions")
    if isinstance(node.op, ast.Div) and right_factor == 0 and right_addend != 0:
        return left_factor / right_addend, left_addend / right_addend
    raise ValueError("formula is not affine")


def formula_interpretation(formula: str) -> tuple[Decimal, Decimal, str] | None:
    primary = re.split(r",|\bor\b", formula, maxsplit=1, flags=re.IGNORECASE)[0]
    left, separator, right = primary.partition("=")
    expression = right.strip() if separator else left.strip()
    unit = canonical_unit(left) if separator else ""
    expression = re.sub(
        r"\(\s*A\s*\*\s*256\s*\+\s*B\s*\)",
        "raw",
        expression,
        flags=re.IGNORECASE,
    )
    expression = re.sub(
        r"\(\s*\(\s*A\s*<<\s*8\s*\)\s*\+\s*B\s*\)",
        "raw",
        expression,
        flags=re.IGNORECASE,
    )
    try:
        factor, addend = affine_expression(ast.parse(expression, mode="eval"))
    except (SyntaxError, ValueError, ZeroDivisionError):
        return None
    return factor, addend, unit


def decimal_key(value: Decimal) -> str:
    if value == 0:
        return "0"
    return format(value.normalize(), "f")


def interpretation_key(
    definition: dict[str, Any],
) -> tuple[str, str, str] | None:
    factor = decimal_value(definition.get("factor"))
    addend = decimal_value(definition.get("addend"))
    formula = str(definition.get("formula") or "").strip()
    formula_result = formula_interpretation(formula) if formula else None
    unit = canonical_unit(definition.get("unit"))
    if factor is None and formula_result:
        factor, parsed_addend, formula_unit = formula_result
        addend = parsed_addend
        unit = unit or formula_unit
    if factor is not None:
        return decimal_key(factor), decimal_key(addend or Decimal(0)), unit
    return None


def conflicting_interpretations(
    rows: list[dict[str, Any]], limit: int
) -> list[dict[str, Any]]:
    if limit == 0:
        return []
    result = []
    for row in rows:
        definitions = [
            definition
            for definition in row.get("definitions", [])
            if isinstance(definition, dict)
        ]
        keyed = []
        for definition in definitions:
            key = interpretation_key(definition)
            if key is not None:
                keyed.append((str(definition.get("dataset_id") or ""), key))
        cross_source_conflict = any(
            left_source
            and right_source
            and left_source != right_source
            and left_key != right_key
            for left_index, (left_source, left_key) in enumerate(keyed)
            for right_source, right_key in keyed[left_index + 1 :]
        )
        if not cross_source_conflict:
            continue
        item = dict(row)
        item["interpretations"] = [
            {"factor": factor, "addend": addend, "unit": unit}
            for factor, addend, unit in sorted({key for _source, key in keyed})
        ]
        result.append(item)
        if len(result) >= limit:
            break
    return result


def render_value(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, sort_keys=True)
    return str(value)


def row_headers(rows: list[dict[str, Any]]) -> list[str]:
    return list(dict.fromkeys(key for row in rows for key in row))


def print_scalar(label: str, value: Any, indent: str = "") -> None:
    rendered = render_value(value)
    if not rendered:
        print(f"{indent}{label}:")
        return
    prefix = f"{indent}{label}: "
    continuation = " " * len(prefix)
    logical_lines = rendered.splitlines() or [""]
    first = True
    for logical_line in logical_lines:
        wrapped = textwrap.wrap(
            logical_line,
            width=max(20, 110 - len(prefix)),
            replace_whitespace=False,
            drop_whitespace=False,
        ) or [""]
        for line in wrapped:
            print(f"{prefix if first else continuation}{line.rstrip()}")
            first = False


def print_records(rows: list[dict[str, Any]]) -> None:
    for index, row in enumerate(rows, 1):
        if len(rows) > 1:
            print(f"[{index}]")
        for field, value in row.items():
            if isinstance(value, list):
                print(f"{field}:")
                if not value:
                    print("  []")
                    continue
                for item in value:
                    if isinstance(item, dict):
                        print("  -")
                        for nested_field, nested_value in item.items():
                            print_scalar(nested_field, nested_value, "    ")
                    else:
                        print_scalar("-", item, "  ")
            elif isinstance(value, dict):
                print(f"{field}:")
                for nested_field, nested_value in value.items():
                    print_scalar(nested_field, nested_value, "  ")
            else:
                print_scalar(field, value)
        if index != len(rows):
            print()


def print_flat_table(rows: list[dict[str, Any]]) -> None:
    headers = row_headers(rows)
    widths = {
        header: min(
            80,
            max(
                len(header),
                *(len(render_value(row.get(header))) for row in rows),
            ),
        )
        for header in headers
    }
    print("  ".join(header.ljust(widths[header]) for header in headers))
    print("  ".join("-" * widths[header] for header in headers))
    for row in rows:
        values = []
        for header in headers:
            value = render_value(row.get(header))
            if len(value) > widths[header]:
                value = value[: widths[header] - 3] + "..."
            values.append(value.ljust(widths[header]))
        print("  ".join(values))


def print_table(rows: list[dict[str, Any]]) -> None:
    if not rows:
        print("No rows.")
        return
    sections = list(
        dict.fromkeys(str(row.get("section")) for row in rows if row.get("section"))
    )
    if sections:
        for index, section in enumerate(sections):
            if index:
                print()
            print(section)
            section_rows = [
                {key: value for key, value in row.items() if key != "section"}
                for row in rows
                if row.get("section") == section
            ]
            print_table(section_rows)
        return
    needs_records = any(
        isinstance(value, (dict, list))
        or "\n" in render_value(value)
        or len(render_value(value)) > 80
        for row in rows
        for value in row.values()
    )
    if needs_records:
        print_records(rows)
    else:
        print_flat_table(rows)


def safe_name(value: str, prefix: str) -> str:
    result = re.sub(r"[^A-Za-z0-9_]+", "_", value).strip("_")
    if not result:
        result = prefix
    if result[0].isdigit():
        result = f"{prefix}_{result}"
    return result


def dbc_start_bit(row: dict[str, Any]) -> int:
    byte_offset = int(row["byte_offset"])
    bit_offset = int(row.get("bit_offset") or 0)
    byte_order = str(row.get("byte_order") or "little").lower()
    if byte_order == "little":
        return byte_offset * 8 + bit_offset
    if byte_order == "big":
        return byte_offset * 8 + 7 - bit_offset
    raise ValueError(f"unsupported byte order {byte_order!r}")


def render_dbc(rows: list[dict[str, Any]]) -> str:
    lines = [
        'VERSION "VQ diagnostic catalog hardware-verified export"',
        "",
        "NS_ :",
        "",
        "BS_:",
        "",
        "BU_: ECU",
        "",
    ]
    grouped: dict[int, list[dict[str, Any]]] = {}
    for row in rows:
        can_id = int(str(row["can_id"]), 16)
        grouped.setdefault(can_id, []).append(row)
    for can_id, signals in sorted(grouped.items()):
        dlc = max(int(row.get("dlc") or 0) for row in signals)
        dlc = max(
            dlc,
            max(
                int(row["byte_offset"]) + (int(row["bit_length"]) + 7) // 8
                for row in signals
            ),
        )
        lines.append(f"BO_ {can_id} FRAME_{can_id:03X}: {dlc} ECU")
        for row in signals:
            name = safe_name(str(row["signal_name"]), "Signal")
            start = dbc_start_bit(row)
            length = int(row["bit_length"])
            endian = "1" if str(row.get("byte_order", "")).lower() == "little" else "0"
            sign = "-" if bool(row.get("signed")) else "+"
            factor = float(row.get("factor") if row.get("factor") is not None else 1)
            addend = float(row.get("addend") if row.get("addend") is not None else 0)
            unit = str(row.get("unit") or "").replace('"', "'")
            lines.append(
                f' SG_ {name} : {start}|{length}@{endian}{sign} '
                f"({factor:g},{addend:g}) [0|0] \"{unit}\" ECU"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--bolt", default=BOLT)
    result.add_argument("--json", action="store_true")
    subparsers = result.add_subparsers(dest="command", required=True)

    dtc = subparsers.add_parser("dtc", help="show ROM and source claims for a DTC")
    dtc.add_argument("code")
    dtc.add_argument(
        "--details",
        action="store_true",
        help="include complete factory DTC detail fragment text",
    )
    dtc.add_argument(
        "--all-mentions",
        action="store_true",
        help="include secondary DTC mentions in addition to primary procedures",
    )

    dtc_search = subparsers.add_parser(
        "dtc-search",
        help="find factory DTC definitions by code or semantic title",
    )
    dtc_search.add_argument("term")
    dtc_search.add_argument("--limit", type=nonnegative_int, default=100)

    monitor = subparsers.add_parser(
        "monitor", help="find diagnostic parameters and requests"
    )
    monitor.add_argument("term")
    monitor.add_argument("--limit", type=nonnegative_int, default=100)

    can = subparsers.add_parser("can", help="find CAN signals and bindings")
    can.add_argument("term")
    can.add_argument("--limit", type=nonnegative_int, default=100)

    operation = subparsers.add_parser(
        "operation", help="list operation definitions without executing them"
    )
    operation.add_argument("term", nargs="?", default="")
    operation.add_argument("--limit", type=nonnegative_int, default=100)

    binding = subparsers.add_parser(
        "binding",
        help="list static firmware-to-diagnostic claims",
    )
    binding.add_argument("term", nargs="?", default="")
    binding.add_argument("--rom", default="")
    binding.add_argument("--limit", type=nonnegative_int, default=100)

    subparsers.add_parser("coverage", help="show source and ROM semantic coverage")

    conflicts = subparsers.add_parser(
        "conflicts", help="show conflicting parameter interpretations"
    )
    conflicts.add_argument("--limit", type=nonnegative_int, default=100)

    dbc = subparsers.add_parser(
        "export-dbc", help="export hardware-verified CAN bindings only"
    )
    dbc.add_argument("output", type=Path)
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        from neo4j import GraphDatabase
        from neo4j.exceptions import DriverError, Neo4jError
    except ImportError:
        print(
            "neo4j package is required; run with "
            "`uv run --no-project --with neo4j python tools/diagnostics/query.py`",
            file=sys.stderr,
        )
        return 1

    driver = None
    try:
        driver = GraphDatabase.driver(args.bolt, auth=("", ""))
        with driver.session(default_access_mode="READ") as session:
            if args.command == "dtc":
                code = canonical_dtc_code(args.code)
                if code is None:
                    raise ValueError(f"invalid DTC code: {args.code!r}")
                rows = query_dtc(
                    session,
                    code,
                    include_mentions=args.all_mentions,
                    include_detail_text=args.details,
                )
            elif args.command == "dtc-search":
                term = args.term.strip()
                rows = record_dicts(
                    session.run(
                        DTC_SEARCH_QUERY,
                        term=term,
                        phrases=semantic_search_phrases(term),
                        aliases=dtc_search_aliases(term),
                        limit=args.limit,
                    )
                )
            elif args.command == "monitor":
                term = args.term.strip()
                identifier = canonical_monitor_identifier(args.term)
                rows = clean_optional_evidence(
                    record_dicts(
                        session.run(
                            MONITOR_QUERY,
                            term=term,
                            identifier=identifier or "",
                            is_identifier=identifier is not None,
                            phrases=semantic_search_phrases(term),
                            aliases=semantic_search_aliases(term),
                            limit=args.limit,
                        )
                    )
                )
            elif args.command == "can":
                term = args.term.strip()
                can_id = canonical_can_identifier(args.term)
                rows = filter_can_evidence(
                    record_dicts(
                        session.run(
                            CAN_QUERY,
                            term=term,
                            can_id=can_id or term,
                            phrases=semantic_search_phrases(term),
                            aliases=semantic_search_aliases(term),
                            limit=args.limit,
                        )
                    ),
                    can_id,
                )
            elif args.command == "operation":
                term = args.term.strip()
                rows = record_dicts(
                    session.run(
                        OPERATION_QUERY,
                        term=term,
                        kind_term=canonical_operation_kind(term),
                        phrases=semantic_search_phrases(term),
                        aliases=semantic_search_aliases(term),
                        limit=args.limit,
                    )
                )
            elif args.command == "binding":
                identifier = canonical_binding_identifier(args.term)
                rows = record_dicts(
                    session.run(
                        STATIC_BINDING_QUERY,
                        term=args.term.strip(),
                        identifier=identifier or "",
                        is_identifier=identifier is not None,
                        rom=args.rom.strip(),
                        limit=args.limit,
                    )
                )
            elif args.command == "coverage":
                rows = [
                    {"section": "ROM coverage", **row}
                    for row in record_dicts(session.run(COVERAGE_QUERY))
                ]
                rows.extend(
                    {"section": "Source coverage", **row}
                    for row in record_dicts(session.run(SOURCE_COVERAGE_QUERY))
                )
            elif args.command == "conflicts":
                rows = conflicting_interpretations(
                    record_dicts(session.run(CONFLICT_QUERY)),
                    args.limit,
                )
            elif args.command == "export-dbc":
                rows = record_dicts(session.run(DBC_QUERY))
                output = args.output.expanduser().resolve()
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text(render_dbc(rows), encoding="utf-8")
                print(
                    f"Wrote {output} with {len(rows)} hardware-verified signal bindings"
                )
                return 0
            else:
                raise AssertionError(args.command)
    except (DriverError, Neo4jError, OSError, ValueError) as error:
        print(error, file=sys.stderr)
        return 1
    finally:
        if driver is not None:
            driver.close()

    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print_table(rows)
    return 0


if __name__ == "__main__":
    sys.exit(main())
