"""Native registry publication respects the editor policy of each layout."""

from types import SimpleNamespace

import pytest

from kb.adapters import native
from kb.model import Meaning, Symbol, SymbolKey


@pytest.mark.parametrize("kind", ["tbl", "axis"])
@pytest.mark.parametrize("meaning_editor,symbol_editor,emitted", [
    ({"emit": False}, None, False),
    ({"name": "Visible"}, None, True),
    ({"name": "Visible", "emit": True}, None, True),
    ({"emit": False}, {"name": "Override"}, True),
    ({"name": "Visible"}, {"emit": False}, False),
    (None, {"emit": False}, False),
])
def test_native_projection_respects_layout_editor_visibility(
        tmp_path, monkeypatch, kind, meaning_editor, symbol_editor, emitted):
    image_path = tmp_path / "stock.bin"
    image_path.write_bytes(bytes(16))
    image = SimpleNamespace(path=image_path, sha256="0" * 64)
    monkeypatch.setattr(native, "targets", lambda model: [
        ("JK78C", "jk78c", image), ("1ND0A", "1nd", image)])
    props = {"home": "jk78c", "storage": "uint8"}
    props.update({"points": 2} if kind == "axis" else {"cols": 2, "rows": 1})
    if meaning_editor is not None:
        props["editor"] = meaning_editor
    if kind == "tbl":
        props["summary"] = ("Published calibration contract." if emitted
                            else "Hidden calibration contract.")
    meaning = Meaning(kind, name="visibility_probe", props=props)
    overrides = {"editor": symbol_editor} if symbol_editor is not None else {}
    meaning.symbols = {
        "jk78c": Symbol(SymbolKey("jk78c", kind, 0), props=overrides, meaning=meaning),
        "1nd": Symbol(SymbolKey("1nd", kind, 0),
                      props={"editor": {"name": "Other layout"}, "summary": None},
                      meaning=meaning),
    }
    model = SimpleNamespace(meanings=[meaning], layouts={
        "jk78c": SimpleNamespace(id="jk78c", images=["JK78C"]),
        "1nd": SimpleNamespace(id="1nd", images=["1ND0A"]),
    })

    document = native.tables_document(model, notes={})
    entry_kind = "table" if kind == "tbl" else "axis"
    assert bool(document["target"]["JK78C"].get(entry_kind)) is emitted
    assert len(document["target"]["1ND0A"][entry_kind]) == 1
    rendered = native.render_tables(document)
    assert "Hidden calibration contract." not in rendered
    assert ("Published calibration contract." in rendered) is (emitted and kind == "tbl")
