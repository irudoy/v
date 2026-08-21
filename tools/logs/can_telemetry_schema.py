"""ROM-neutral CAN telemetry wire-schema identity helpers."""

from __future__ import annotations

import json


CONTROL_CAN_ID_EXPRESSION = "data_can_id + 1"


def crc16_ccitt_false(data):
    value = 0xFFFF
    for byte in bytes(data):
        value ^= byte << 8
        for _ in range(8):
            value = (
                ((value << 1) ^ 0x1021) & 0xFFFF
                if value & 0x8000
                else (value << 1) & 0xFFFF
            )
    return value


def _field_contract(field, *, fixed):
    result = {
        "name": field["name"],
        "width": field["width"],
        "signed": field["signed"],
        "scale": field["scale"],
    }
    if fixed:
        result["page"] = field["page"]
        result["offset"] = field["offset"]
    return result


def canonical_profile(profile, protocol_version):
    """Return the producer-independent profile identity document."""
    return {
        "protocol_version": protocol_version,
        "name": profile["name"],
        "id": profile["id"],
        "page_count": profile["page_count"],
        "fields": [
            _field_contract(field, fixed=True)
            for field in profile["fields"]
        ],
        "contexts": [
            {
                "page": context["page"],
                "tag": context["tag"],
                "name": context["name"],
                "fields": [
                    _field_contract(field, fixed=False)
                    for field in context["fields"]
                ],
            }
            for context in profile["contexts"]
        ],
    }


def profile_crc16(profile, protocol_version):
    canonical = canonical_profile(profile, protocol_version)
    encoded = json.dumps(
        canonical, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return crc16_ccitt_false(encoded)


def control_frame(document, data_can_id, command):
    """Return one schema-declared telemetry control frame."""
    if type(data_can_id) is not int or not 1 <= data_can_id <= 0x7FF:
        raise ValueError("data CAN ID must be a nonzero standard 11-bit ID")
    control = document.get("control") if isinstance(document, dict) else None
    if not isinstance(control, dict):
        raise ValueError("telemetry schema has no control contract")
    try:
        maximum = int(control.get("maximum_data_can_id"), 0)
    except (TypeError, ValueError) as error:
        raise ValueError("telemetry control maximum CAN ID is invalid") from error
    commands = control.get("commands")
    if (
        control.get("format") != "standard_11_bit_classical_can"
        or control.get("dlc") != 8
        or control.get("can_id") != CONTROL_CAN_ID_EXPRESSION
        or not 1 <= maximum <= 0x7FE
        or not isinstance(commands, dict)
    ):
        raise ValueError("telemetry control transport contract differs")
    if data_can_id > maximum:
        raise ValueError(
            f"data CAN ID must be in 0x001..0x{maximum:03X} for control"
        )
    encoded = commands.get(command)
    if not isinstance(encoded, str):
        raise ValueError(f"telemetry control command {command!r} is undefined")
    try:
        payload = bytes.fromhex(encoded)
    except ValueError as error:
        raise ValueError(
            f"telemetry control command {command!r} is not hexadecimal"
        ) from error
    if len(payload) != 8 or crc16_ccitt_false(payload[:6]) != int.from_bytes(
        payload[6:], "big"
    ):
        raise ValueError(
            f"telemetry control command {command!r} has an invalid payload"
        )
    return data_can_id + 1, payload
