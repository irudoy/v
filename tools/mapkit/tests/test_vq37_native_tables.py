import hashlib

import pytest

from tools.mapkit import rom as romkit
from tools.mapkit import vq37_native_tables


TARGETS = ("JK78C", "1ND0A", "1ND3B")
ROLES = ("fuel_compensation_alternate", "timing_state_addend_alternate")


def _axes(target):
    return {
        f"{address:08x}": {}
        for table in target.tables
        for address in table.axis_x + table.axis_y
    }


def test_registry_requires_the_complete_vq37_target_set(tmp_path):
    path = tmp_path / "native.toml"
    path.write_text(
        "schema_version = 1\n[target.JK78C]\n",
        encoding="utf-8",
    )

    with pytest.raises(
        vq37_native_tables.NativeTableError,
        match="target set differs",
    ):
        vq37_native_tables.load_registry(path)


def test_registry_binds_exact_stock_values_and_accessor_literals():
    registry = vq37_native_tables.load_registry()

    assert set(registry) == set(TARGETS)
    for rom in TARGETS:
        target = registry[rom]
        image = romkit.load(rom)

        assert {table.identifier for table in target.tables} == set(ROLES)
        assert hashlib.sha256(image.data).hexdigest() == target.stock_sha256
        for table in target.tables:
            length = table.width * table.height
            element = romkit.ELEM[table.storagetype]
            block = image.data[table.address : table.address + length * element]

            assert hashlib.sha256(block).hexdigest() == table.values_sha256
            assert table.pointer_bindings
            for pointer in table.pointer_bindings:
                stored = int.from_bytes(
                    image.data[pointer.site : pointer.site + 4], "big"
                )

                assert stored == table.address
                assert pointer.accessor < pointer.site


def test_apply_target_publishes_every_registered_table():
    for rom in TARGETS:
        target = vq37_native_tables.load_registry()[rom]
        image = romkit.load(rom)
        maps, overrides = vq37_native_tables.apply_target(
            rom, {}, _axes(target), {"table": {}}, image
        )
        keys = {f"{table.address:08x}" for table in target.tables}

        assert set(maps) == keys
        assert set(overrides["table"]) == keys
        for table in target.tables:
            key = f"{table.address:08x}"
            model = maps[key]

            assert model["width"] == table.width
            assert model["storagetype"] == table.storagetype
            assert model["confidence"] == table.confidence
            assert model["scale_conf"] == table.scale_conf
            assert overrides["table"][key]["name"] == table.name
            assert overrides["table"][key]["emit"] is True
            assert model["accessors"] == [
                f"{pointer.accessor:08x}"
                for pointer in table.pointer_bindings
            ]


def test_apply_target_rejects_an_unprojected_axis():
    rom = "JK78C"
    image = romkit.load(rom)

    with pytest.raises(
        vq37_native_tables.NativeTableError,
        match="unprojected axis",
    ):
        vq37_native_tables.apply_target(rom, {}, {}, {"table": {}}, image)


def test_apply_target_rejects_a_projection_collision():
    rom = "JK78C"
    target = vq37_native_tables.load_registry()[rom]
    image = romkit.load(rom)
    occupied = {f"{target.tables[0].address:08x}": {}}

    with pytest.raises(
        vq37_native_tables.NativeTableError,
        match="collides with the projection",
    ):
        vq37_native_tables.apply_target(
            rom, occupied, _axes(target), {"table": {}}, image
        )


def test_apply_target_rejects_a_foreign_image():
    target = vq37_native_tables.load_registry()["JK78C"]

    with pytest.raises(
        vq37_native_tables.NativeTableError,
        match="native table target is JK78C",
    ):
        vq37_native_tables.apply_target(
            "JK78C", {}, _axes(target), {"table": {}}, romkit.load("1ND0A")
        )


def test_apply_target_ignores_a_rom_without_native_tables():
    maps, overrides = vq37_native_tables.apply_target(
        "JK08A", {}, {}, {"table": {}}, romkit.load("JK08A")
    )

    assert maps == {}
    assert overrides == {"table": {}}
