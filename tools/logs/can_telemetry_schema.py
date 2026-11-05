"""ROM-neutral CAN telemetry wire-schema identity and scale helpers."""

from __future__ import annotations

from fractions import Fraction
import json
import re


CONTROL_CAN_ID_EXPRESSION = "data_can_id + 1"
# A term of the arithmetic of a scale: the raw value, a decimal number, or an
# operator.
SCALE_TERM = re.compile(r"raw|\d+(?:\.\d+)?|[-+*/]")
RAW_WORD = re.compile(r"\braw\b")
CANDIDATE = "candidate "
# The prefix of the named entries of an enumeration and of a bit list, the
# schema key of the entries, and the key of the number of each entry.
NAMED_SCALES = (
    ("enumeration: ", "values", "value"),
    ("bits: ", "bits", "bit"),
)
NAMED_ENTRY = re.compile(r"(\d+) ([A-Z][A-Z0-9_]*)")
# A value in a run of bits with named bits beside it: the bit range, the
# scale of the value, and the named bits.
PACKED_SCALE = re.compile(r"field (\d+) through (\d+) ([^;]+); (bits: .+)")
PACKED_BITS = 32
# The commands of the dynamic page by opcode.
PAGE_COMMANDS = {0xC0: "page-default", 0xC1: "page-set", 0xC2: "page-commit"}


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
        "width": field["width"],
        "signed": field["signed"],
    }
    if fixed:
        result["page"] = field["page"]
        result["offset"] = field["offset"]
    return result


def canonical_profile(profile, protocol_version):
    """Return the wire-layout identity document covered by the profile CRC.

    Field names, context names, and scale strings are outside the document:
    the CRC identifies byte placement and the dynamic page, and the profile
    ID identifies which quantity each slot carries.
    """
    result = {
        "protocol_version": protocol_version,
        "id": profile["id"],
        "page_count": profile["page_count"],
        "fields": sorted(
            (
                _field_contract(field, fixed=True)
                for field in profile["fields"]
            ),
            key=lambda item: (item["page"], item["offset"]),
        ),
        "contexts": [
            {
                "page": context["page"],
                "tag": context["tag"],
                "fields": [
                    _field_contract(field, fixed=False)
                    for field in context["fields"]
                ],
            }
            for context in profile["contexts"]
        ],
    }
    if profile.get("padding"):
        result["padding"] = sorted(profile["padding"],
                                   key=lambda row: (row["page"], row.get("tag", -1), row["offset"]))
    if profile.get("dynamic"):
        result["dynamic"] = dict(profile["dynamic"])
    return result


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


def _page_payload(encoded, context):
    try:
        payload = bytes.fromhex(encoded)
    except (TypeError, ValueError) as error:
        raise ValueError(f"{context} is not hexadecimal") from error
    if len(payload) != 8 or crc16_ccitt_false(payload[:6]) != int.from_bytes(
        payload[6:], "big"
    ):
        raise ValueError(f"{context} has an invalid payload")
    return payload


def configuration_commands(frames, profile, data_can_id, configuration_id):
    """Return the control CAN ID and the (command, payload) frames that
    install one configuration of the dynamic page of a profile.

    ``frames`` is the generated command document of one ROM. ID 0 installs
    the default configuration. The frames of any other ID stage every slot
    of the groups that the schema states, in order and at the width of its
    field, under that ID, and end with the COMMIT of those slot counts.
    """
    if type(data_can_id) is not int or not 1 <= data_can_id <= 0x7FE:
        raise ValueError("data CAN ID must be in 0x001..0x7FE for control")
    if (
        not isinstance(frames, dict)
        or frames.get("schema_version") != 1
        or frames.get("profile") != profile.get("name")
        or frames.get("can_id") != CONTROL_CAN_ID_EXPRESSION
        or profile.get("dynamic") is None
    ):
        raise ValueError("configuration frames do not match the selected profile")
    if configuration_id == 0:
        payload = _page_payload(frames.get("default"), "the DEFAULT frame")
        if payload[:6] != bytes((0xC0, 0, 0, 0, 0, 0)):
            raise ValueError("the DEFAULT frame differs from C0 00 00 00 00 00")
        return data_can_id + 1, (("page-default", payload),)
    groups = next(
        (
            row["groups"]
            for row in profile.get("configurations", ())
            if row["id"] == configuration_id
        ),
        None,
    )
    row = next(
        (
            row
            for row in frames.get("configurations", ())
            if isinstance(row, dict) and row.get("id") == configuration_id
        ),
        None,
    )
    if groups is None or row is None or not isinstance(row.get("frames"), list):
        raise ValueError(f"configuration {configuration_id} is undefined")
    widths = {
        field["name"]: field["width"]
        for field in profile.get("dynamic_fields", ())
    }
    expected = [
        bytes((
            0xC1,
            configuration_id,
            group_index << 7 | slot_index << 4 | widths[name],
        ))
        for group_index, group in enumerate(groups)
        for slot_index, name in enumerate(group)
    ]
    counts = [len(group) for group in groups] + [0] * (2 - len(groups))
    expected.append(bytes((0xC2, configuration_id, len(groups), *counts, 0)))
    payloads = [
        _page_payload(encoded, f"configuration {configuration_id} frame {index}")
        for index, encoded in enumerate(row["frames"])
    ]
    if len(payloads) != len(expected) or any(
        payload[:len(prefix)] != prefix
        for payload, prefix in zip(payloads, expected)
    ):
        raise ValueError(
            f"configuration {configuration_id} frames differ from its schema groups"
        )
    return data_can_id + 1, tuple(
        (PAGE_COMMANDS[payload[0]], payload) for payload in payloads
    )


def scale_terms(scale):
    """Return what the scale string of a field states for a host.

    Arithmetic in ``raw`` opens the scale, after ``candidate`` for a
    candidate conversion: the terms ``raw`` and decimal numbers joined by
    ``+``, ``-``, ``*``, and ``/`` with the usual precedence, each separated
    by a space, then an optional unit, then an optional ``; note``. It gives
    ``conversion``, the factor and offset of the affine value in ``raw``,
    ``candidate``, and the ``unit`` it names. ``enumeration: <n> <NAME>,
    ...`` gives ``values`` and ``bits: <n> <NAME>, ...`` gives ``bits``, each
    entry with its number and name. ``field <low> through <high> <scale>;
    bits: <n> <NAME>, ...`` packs a value into bits ``low`` through ``high``
    beside named bits outside them: it gives ``field``, the bit range with
    the arithmetic or enumeration terms of the value, and ``bits``. Any other
    scale describes the value and gives nothing. A scale that names ``raw``
    states arithmetic, so one that does not parse raises ValueError, as does
    a named entry that is not ``<n> <NAME>`` or that repeats a number or a
    name, and a packed scale whose value states nothing, whose named values
    exceed its bit range, or whose bits leave the 32-bit word or meet the
    value.
    """
    packed = PACKED_SCALE.fullmatch(scale)
    if packed is not None:
        low, high = int(packed[1]), int(packed[2])
        value = scale_terms(packed[3])
        bits = scale_terms(packed[4])["bits"]
        if not 0 <= low <= high < PACKED_BITS or not (
            "conversion" in value or "values" in value
        ):
            raise ValueError(f"scale {scale!r}: the field states no value")
        if any(
            item["value"] >> (high - low + 1) for item in value.get("values", ())
        ):
            raise ValueError(f"scale {scale!r}: a named value exceeds the field")
        if any(
            not 0 <= item["bit"] < PACKED_BITS or low <= item["bit"] <= high
            for item in bits
        ):
            raise ValueError(f"scale {scale!r}: a named bit meets the field")
        return {"field": {"low": low, "high": high, **value}, "bits": bits}
    for prefix, key, number in NAMED_SCALES:
        if scale.startswith(prefix):
            entries = []
            for item in scale[len(prefix):].split(", "):
                match = NAMED_ENTRY.fullmatch(item)
                if match is None:
                    raise ValueError(
                        f"scale {scale!r}: {item!r} is not <n> <NAME>"
                    )
                entries.append({number: int(match[1]), "name": match[2]})
            if len({item[number] for item in entries}) != len(entries) or len(
                {item["name"] for item in entries}
            ) != len(entries):
                raise ValueError(f"scale {scale!r} repeats a number or a name")
            return {key: sorted(entries, key=lambda item: item[number])}
    if not RAW_WORD.search(scale):
        return {}
    head = scale.split(";", 1)[0]
    candidate = head.startswith(CANDIDATE)
    words = (head[len(CANDIDATE):] if candidate else head).split()
    count = 0
    while count < len(words) and SCALE_TERM.fullmatch(words[count]):
        count += 1
    unit = words[count:]
    if len(unit) > 1:
        raise ValueError(f"scale {scale!r}: {' '.join(unit)!r} is no unit")
    factor, offset = _affine(words[:count], scale)
    terms = {
        "conversion": {"factor": float(factor), "offset": float(offset)},
        "candidate": candidate,
    }
    if unit:
        terms["unit"] = unit[0]
    return terms


def _affine(tokens, scale):
    """Return (factor, offset) of affine arithmetic in ``raw`` as fractions."""
    position = 0

    def fail(reason):
        raise ValueError(f"scale {scale!r}: {reason}")

    def operand():
        nonlocal position
        if position == len(tokens):
            fail("the arithmetic ends without a term")
        token = tokens[position]
        position += 1
        if token == "raw":
            return Fraction(1), Fraction(0)
        if token in ("+", "-", "*", "/"):
            fail(f"{token} stands where a term belongs")
        return Fraction(0), Fraction(token)

    def product():
        nonlocal position
        factor, offset = operand()
        while position < len(tokens) and tokens[position] in ("*", "/"):
            operator = tokens[position]
            position += 1
            other_factor, other_offset = operand()
            if operator == "*":
                if factor and other_factor:
                    fail("the arithmetic multiplies raw by raw")
                factor, offset = (
                    factor * other_offset + other_factor * offset,
                    offset * other_offset,
                )
            else:
                if other_factor or not other_offset:
                    fail("the arithmetic divides by raw or by zero")
                factor, offset = factor / other_offset, offset / other_offset
        return factor, offset

    factor, offset = product()
    while position < len(tokens):
        operator = tokens[position]
        position += 1
        if operator not in ("+", "-"):
            fail(f"{operator} stands where an operator belongs")
        other_factor, other_offset = product()
        sign = 1 if operator == "+" else -1
        factor = factor + sign * other_factor
        offset = offset + sign * other_offset
    if tokens.count("raw") != 1 or not factor:
        fail("the arithmetic holds raw once")
    return factor, offset
