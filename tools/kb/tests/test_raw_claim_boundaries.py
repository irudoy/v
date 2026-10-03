"""Telemetry count presentation and archived observations assert no physical scale."""

import tomllib

import pytest

from kb import compile, repo
from kb.adapters import telemetry
from kb.model import SymbolKey
from tools.logs import can_telemetry_schema


RAW = (
    ("alpha_n_flow", 1, False),
    ("request_flow", 2, False),
    ("engine_torque_state", 2, True),
    ("throttle_request_bounded", 2, True),
    ("throttle_target_shared", 2, False),
)


def notes(symbol_or_meaning):
    value = symbol_or_meaning.props.get("note", ())
    return value if isinstance(value, str) else "\n".join(value)


@pytest.mark.parametrize("name, width, signed", RAW)
def test_unknown_ram_engineering_scale_has_a_separate_count_view(name, width, signed):
    model = compile.cached(repo.ROOT)
    entity = model.entities[("field", name + "_raw")]
    meaning = model.meaning_of(entity.refs["source"][0])
    assert not {"unit", "scale", "to_raw", "scale_level"} & meaning.props.keys()
    assert "Retained hypothesis:" in notes(meaning)
    assert "Source references:" in notes(meaning)
    assert (entity.props["width"], entity.props["signed"]) == (width, signed)
    assert entity.props["dashboard"]["digits"] == 0
    source = telemetry._source(model, entity, {})
    assert source["scale"] == "raw count"
    assert can_telemetry_schema.scale_terms(source["scale"]) == {
        "conversion": {"factor": 1.0, "offset": 0.0}, "candidate": False, "unit": "count",
    }
    if "feed" in entity.props["dashboard"]:
        feed = entity.props["dashboard"]["feed"]
        assert feed["key"] == name + "_count"
        assert (feed["minimum"], feed["maximum"], feed["format"]) == (0, 2**(8*width)-1, "0")
        assert meaning.props["logparam"]["scale"] == "x"


def test_dead_alternative_retains_the_q7_hypothesis_without_asserting_its_scale():
    symbol = compile.cached(repo.ROOT).symbols[SymbolKey("7mfk", "tbl", 0x000122B2)]
    assert (symbol.value("level"), symbol.value("role")) == ("code", "dead")
    assert symbol.value("scale") in (None, "")
    assert symbol.value("scale_level") is None
    assert "Q0.7" in notes(symbol.meaning)
    assert "x/128" in notes(symbol.meaning)
    assert "does not fix" in notes(symbol.meaning)


def test_main_capture_is_retained_without_a_hardware_identity_claim():
    symbol = compile.cached(repo.ROOT).symbols[SymbolKey("7mfk", "ram", 0xFFFF2A85)]
    assert symbol.value("level") == "code"
    assert symbol.evidence
    assert not any(item["kind"] == "hardware" for item in symbol.evidence)
    assert "map_switching.ascd_main_vehicle_2026_09_21" in notes(symbol.meaning)
    assert "code-derived" in notes(symbol.meaning)
    record = tomllib.loads((repo.ROOT / "patches/hardware-results.toml").read_text())[
        "map_switching"]["ascd_main_vehicle_2026_09_21"]
    assert record.get("hardware_status") is None
    assert record.get("target_ecu") is None
