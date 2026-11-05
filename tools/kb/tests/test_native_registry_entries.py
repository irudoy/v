"""Native registry entries carry the keys of their kind and their editor
presentation."""

from types import SimpleNamespace
import tomllib

from kb.adapters import native
from kb.model import Meaning, Symbol, SymbolKey


def _document(tmp_path, monkeypatch, meaning):
    image_path = tmp_path / "stock.bin"
    image_path.write_bytes(bytes(range(16)))
    image = SimpleNamespace(path=image_path, sha256="0" * 64)
    monkeypatch.setattr(native, "targets", lambda model: [("JK78C", "jk78c", image)])
    meaning.symbols = {
        "jk78c": Symbol(SymbolKey("jk78c", meaning.kind, 4), props={}, meaning=meaning)}
    model = SimpleNamespace(meanings=[meaning], layouts={
        "jk78c": SimpleNamespace(id="jk78c", images=["JK78C"])})
    return native.tables_document(model, notes={})


def test_native_projection_renders_the_static_axes_of_a_2d_table(tmp_path, monkeypatch):
    editor = {"name": "Probe", "static_axis_x": [0, 1], "static_axis_x_name": "Column",
              "static_axis_y": ["low", "high"], "static_axis_y_name": "Row"}
    document = _document(tmp_path, monkeypatch, Meaning("tbl", name="static_axis_probe", props={
        "home": "jk78c", "storage": "uint8", "cols": 2, "rows": 2, "editor": editor}))

    [entry] = document["target"]["JK78C"]["table"]
    assert {key: entry[key] for key in editor} == editor
    rendered = native.render_tables(document)
    assert tomllib.loads(rendered)["schema_version"] == 4
    lines = [line.split(" = ")[0] for line in rendered.splitlines() if " = " in line]
    assert lines[lines.index("static_axis_x_name"):lines.index("static_axis_y") + 1] == [
        "static_axis_x_name", "static_axis_x", "static_axis_y_name", "static_axis_y"]


def test_native_projection_renders_reviewed_constant_content(tmp_path, monkeypatch):
    document = _document(tmp_path, monkeypatch, Meaning("tbl", name="constant_probe", props={
        "home": "jk78c", "storage": "uint8", "cols": 1, "rows": 1,
        "editor": {"name": "Probe", "constant_content": True}}))

    rendered = native.render_tables(document)
    assert "\nconstant_content = true\n" in rendered
    [entry] = tomllib.loads(rendered)["target"]["JK78C"]["table"]
    assert entry["constant_content"] is True


def test_native_axis_entry_leaves_out_the_summary_of_its_meaning(tmp_path, monkeypatch):
    document = _document(tmp_path, monkeypatch, Meaning("axis", name="axis_probe", props={
        "home": "jk78c", "storage": "uint8", "points": 2, "quantity": "raw",
        "summary": "Axis summary.", "editor": {"name": "Probe Axis"}}))

    [entry] = document["target"]["JK78C"]["axis"]
    assert "semantics" not in entry
    assert "Axis summary." not in native.render_tables(document)
