"""Reserved wire bytes remain explicit, zero, and outside observed channels."""

import copy
import json
from pathlib import Path
import tempfile
import tomllib

import pytest

from patches import can_telemetry_profile as producer
from tools.logs import can_telemetry as host
from tools.logs import can_telemetry_schema as wire


def padded_source():
    raw = tomllib.loads(producer.DEFAULT_SOURCE.read_text())
    # Replace one complete fixed value and one trailing context value.
    field = next(field for field in raw["field"] if field["page"] == 3)
    raw["field"].remove(field)
    context = next(row for row in raw["context"] if row["page"] == 10 and row["tag"] == 1)
    trailing = context["field"].pop()
    raw["padding_source"] = raw["configuration_address"] + 7
    raw["padding"] = raw.get("padding", []) + [
        {key: field[key] for key in ("page", "offset", "width")},
        {"page": 10, "tag": 1,
         "offset": 2 + sum(field["width"] for field in context["field"]),
         "width": trailing["width"]},
    ]
    return raw, field["name"], trailing["name"]


def load_source(raw):
    from kb.adapters import telemetry

    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "profile.toml"
        path.write_text(telemetry.render_profile(raw))
        return producer.load_manifest(path)


def test_padding_repeats_config_zero_without_observation_fields():
    raw, fixed_name, context_name = padded_source()
    manifest = load_source(raw)
    document = json.loads(producer.render_schema(manifest))
    profile = document["profiles"][0]
    assert wire.profile_crc16(profile, manifest.protocol_version) == manifest.profiles[0].crc16
    names = {field["name"] for field in host.profile_fields(profile)}
    assert fixed_name not in names and context_name not in names
    pad = next(pad for pad in manifest.padding if pad.tag is None)
    start = pad.page * 7 + pad.offset - 1
    assert manifest.page_sources[start:start + pad.width] == (raw["padding_source"],) * pad.width
    context = next(row for row in manifest.contexts if row.page == 10 and row.tag == 1)
    assert context.byte_sources[-context.padding[0].width:] == context.padding[0].byte_sources


@pytest.mark.parametrize("mutation", ("missing", "overlap", "source", "context"))
def test_producer_refuses_implicit_gaps_or_untrusted_zero_sources(mutation):
    raw, _, _ = padded_source()
    if mutation == "missing":
        raw["padding"].pop(0)
    elif mutation == "overlap":
        raw["padding"][0]["offset"] += 1
    elif mutation == "source":
        raw["padding_source"] += 1
    else:
        next(row for row in raw["padding"] if "tag" in row)["offset"] -= 1
    with pytest.raises(ValueError):
        load_source(raw)


def test_host_refuses_padding_overlap_and_binds_reserved_placement_to_crc():
    raw, _, _ = padded_source()
    document = json.loads(producer.render_schema(load_source(raw)))
    profile = document["profiles"][0]
    changed = copy.deepcopy(document)
    changed["profiles"][0]["padding"][0]["offset"] += 1
    assert wire.profile_crc16(changed["profiles"][0], 2) != wire.profile_crc16(profile, 2)
    with pytest.raises(host.DecodeError):
        host.parse_schema(changed)


@pytest.mark.parametrize("tag", (None, 1))
def test_decoder_rejects_nonzero_reserved_bytes(tag):
    raw, _, _ = padded_source()
    manifest = load_source(raw)
    document = json.loads(producer.render_schema(manifest))
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "schema.json"
        path.write_text(json.dumps(document))
        decoder = host.Decoder("tuning", 0x6F0, path)
    padding = next(pad for pad in manifest.padding if pad.tag == tag)
    pages = [bytearray(8) for _ in range(11)]
    for page, data in enumerate(pages):
        data[0] = 0x10 | page
    pages[0][2] = 1
    for page in manifest.context_pages:
        pages[page][1] = 1
    pages[padding.page][padding.offset] = 1
    assert all(decoder.feed(0x6F0, data) is None for data in pages)
    assert decoder.malformed_frames == 1
