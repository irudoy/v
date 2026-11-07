import tomllib

from kb import repo, runtime_projection, targets


def test_runtime_projection_matches_its_owners():
    document = tomllib.loads(runtime_projection.render())
    for feature, symbols in document["canonical_symbols"].items():
        assert symbols == targets.canonical_symbols(feature)
    for image, layout in document["images"].items():
        assert layout == targets.layout_of(image)
    for layout, row in document["layouts"].items():
        rolling = targets.target("rolling_launch", layout)
        if rolling.get("status", "supported") == "supported":
            fuel = targets.meaning("rolling_launch", layout, "fuel_inhibit")
            assert row["fuel_cut_address"] == targets.address(fuel, layout)
            assert row["fuel_cut_active_bit"] == targets.bit(fuel, layout, "active")
        else:
            assert "fuel_cut_address" not in row
            assert "fuel_cut_active_bit" not in row
        assert row["ascd_main_bit"] == targets.bit("ascd_state/ram", layout, "main")
        bits = {}
        for field, name in runtime_projection.MOVED_FIELD_BITS:
            meaning = targets.field_meaning("can_telemetry", field, layout)
            if meaning is not None:
                bits[field] = targets.bit(meaning, layout, name)
        assert row["field_bits"] == bits
        hooks = {int(address, 16): key for address, key in document["map_hook_keys"][layout].items()}
        assert hooks == targets.hook_keys("map_switching", layout)


def test_projection_reflects_changed_owner_bits(monkeypatch):
    original = targets.bit
    before = tomllib.loads(runtime_projection.render())

    def changed(ref, layout, name, root=repo.ROOT, overlay=None):
        value = original(ref, layout, name, root, overlay)
        return value ^ 1 if ref == "ascd_state/ram" else value

    monkeypatch.setattr(targets, "bit", changed)
    after = tomllib.loads(runtime_projection.render())
    for layout in before["layouts"]:
        expected = dict(before["layouts"][layout])
        expected["ascd_main_bit"] ^= 1
        assert after["layouts"][layout] == expected
    assert after["canonical_symbols"] == before["canonical_symbols"]


def test_the_canonical_layout_states_the_wire_bit_of_every_moved_field():
    document = tomllib.loads(runtime_projection.render())
    wire = document["layouts"][targets.CANONICAL]["field_bits"]
    assert set(wire) == {field for field, _name in runtime_projection.MOVED_FIELD_BITS}
    for layout, row in document["layouts"].items():
        assert set(row["field_bits"]) <= set(wire), layout


def test_tracked_runtime_projection_is_current():
    path = repo.ROOT / "patches/runtime-bindings.toml"
    assert path.read_text(encoding="utf-8") == runtime_projection.render()
