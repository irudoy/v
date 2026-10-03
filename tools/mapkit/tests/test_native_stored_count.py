"""Unasserted native scales retain exact storage and count-domain editing."""

from dataclasses import replace
import tomllib
import xml.etree.ElementTree as ET

import pytest

from tools.mapkit import emit_def, rom as romkit, tunerpro, vq37_native_tables as native
from tools.mapkit.tests.test_vq37_native_tables import _projected_axes, _registry_text


def _row(kind):
    return tomllib.loads(_registry_text())["target"]["JK78C"][kind][0]


def _parse(kind, row):
    parser = native._parse_table if kind == "table" else native._parse_axis
    return parser(row, "native fixture")


@pytest.mark.parametrize("kind", ["table", "axis"])
@pytest.mark.parametrize("level", [None, "unknown", "pattern"])
def test_unasserted_conversion_renders_counts_without_scale_evidence(kind, level):
    row = _row(kind)
    if level is None:
        for key in native.SCALE_FIELDS:
            row.pop(key, None)
    else:
        row.update(units="deg", scale_expr="x*0.1", to_byte="x*10", scale_conf=level)
    entity = _parse(kind, row)
    assert entity.scale_conf == level
    model = (native._model(entity, "retained hypothesis") if kind == "table"
             else native._axis_model(entity, range(entity.length), "retained hypothesis"))
    view = native._editor_presentation(entity)
    assert model["units"] == "Stored count"
    assert model["scale_expr"] == model["to_byte"] == "x"
    assert model["scale_conf"] is None
    assert model["stored_count"] is True
    assert "no engineering conversion is established" in model["note"]
    assert view["name"].endswith("[stored count]")
    assert (view["format"], view["fine"], view["coarse"]) == ("0", 1, 10)
    if kind == "axis":
        assert model["scale_evidence"] == ""
        xml = ET.fromstring("\n".join(emit_def.axis_xml(
            "X Axis", model, {"axis": {model["addr"]: view}}, "sizex",
        )))
        root = ET.Element("root")
        tunerpro.add_embedded_axis(root, "x", model, view)
        assert root.find("XDFAXIS/units").text == "Stored count"
        assert root.find("XDFAXIS/MATH").get("equation") == "X"
    else:
        xml = ET.fromstring(emit_def.scaling(
            model["units"], model["scale_expr"], model["to_byte"], model["scale_conf"],
            view["format"], view["fine"], view["coarse"], 0,
        ))
    scale = xml.find("scaling") if kind == "axis" else xml
    assert scale.attrib == {
        "units": "Stored count", "expression": "x", "to_byte": "x", "format": "0",
        "fineincrement": "1", "coarseincrement": "10",
    }


@pytest.mark.parametrize("kind", ["table", "axis"])
@pytest.mark.parametrize("missing", sorted(native.SCALE_FIELDS))
def test_partial_engineering_conversion_is_refused(kind, missing):
    row = _row(kind)
    row.update(units="deg", scale_expr="x*0.1", to_byte="x*10", scale_conf="candidate")
    row.pop(missing)
    with pytest.raises(native.NativeTableError, match="engineering conversion is incomplete"):
        _parse(kind, row)


@pytest.mark.parametrize("kind", ["table", "axis"])
@pytest.mark.parametrize("defect", ["values", "pointer", "identity"])
def test_stored_count_keeps_exact_image_gates(monkeypatch, kind, defect):
    registry = native.load_registry()
    target = registry["JK78C"]
    entities = list(target.tables if kind == "table" else target.axes)
    entity = replace(entities[0], units=None, scale_expr=None, to_byte=None, scale_conf=None)
    if defect == "values":
        entity = replace(entity, values_sha256="0" * 64)
    elif defect == "pointer":
        entity = replace(entity, pointer_bindings=(replace(entity.pointer_bindings[0], offset=1),))
    entities[0] = entity
    target = replace(target, **{"tables" if kind == "table" else "axes": tuple(entities)})
    if defect == "identity":
        target = replace(target, stock_sha256="0" * 64)
    registry["JK78C"] = target
    monkeypatch.setattr(native, "load_registry", lambda path=native.DEFAULT_REGISTRY: registry)
    with pytest.raises(native.NativeTableError, match={
        "values": "values differ", "pointer": "pointer at", "identity": "stock SHA-256",
    }[defect]):
        native.apply_target("JK78C", {}, _projected_axes(target), {"table": {}}, romkit.load("JK78C"))
