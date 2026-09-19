import hashlib

import pytest

from tools.mapkit import rom as romkit
from tools.mapkit import vq37_native_tables


TARGETS = ("JK78C", "1ND0A", "1ND3B", "1ME3B")
SELECTOR_ROLES = {
    "fuel_compensation_alternate",
    "timing_state_addend_alternate",
}
VVEL_TABLE_ROLES = {
    "vvel_duration_running",
    "vvel_duration_throttled",
    "vvel_duration_hot_intake_idle",
    "vvel_duration_hot_intake_idle_knock",
    "vvel_duration_hot_intake_idle_floor",
    "vvel_duration_hot_intake_idle_knock_floor",
    "vvel_duration_mode_14",
    "vvel_duration_cold",
    "vvel_duration_startup",
    "vvel_duration_model_hot_intake_idle",
    "vvel_duration_model_hot_intake_idle_knock",
    "vvel_duration_throttled_ramp_delay",
    "vvel_duration_startup_blend",
    "intake_cvtc_target_running",
    "intake_cvtc_target_throttled",
    "intake_cvtc_target_cold",
    "vvel_command_shaft_angle",
    "vvel_shaft_angle_limit_engine_speed",
    "vvel_shaft_angle_limit_cvtc",
    "vvel_shaft_angle_monitor_floor_a",
    "vvel_shaft_angle_monitor_floor_b",
    "vvel_command_shaft_angle_second",
    "vvel_shaft_angle_monitor_floor_a_second",
    "vvel_shaft_angle_monitor_floor_b_second",
}
VVEL_AXIS_ROLES = {
    "vvel_duration_running_axis",
    "vvel_duration_throttled_axis",
    "vvel_duration_hot_intake_idle_axis_x",
    "vvel_duration_hot_intake_idle_axis_y",
    "vvel_duration_hot_intake_idle_floor_axis",
    "vvel_cold_axis",
    "vvel_duration_startup_axis",
    "vvel_duration_model_hot_intake_idle_axis_x",
    "vvel_duration_model_hot_intake_idle_axis_y",
    "vvel_duration_throttled_ramp_delay_axis",
    "vvel_duration_startup_blend_axis",
    "intake_cvtc_target_running_axis",
    "intake_cvtc_target_throttled_axis_x",
    "intake_cvtc_target_throttled_axis_y",
    "vvel_shaft_angle_axis",
    "vvel_shaft_angle_limit_engine_speed_axis",
    "vvel_shaft_angle_limit_cvtc_axis",
    "vvel_shaft_angle_monitor_floor_a_axis",
    "vvel_shaft_angle_monitor_floor_b_axis",
    "vvel_shaft_angle_second_axis",
    "vvel_shaft_angle_monitor_floor_a_second_axis",
    "vvel_shaft_angle_monitor_floor_b_second_axis",
}
ROLES = SELECTOR_ROLES | VVEL_TABLE_ROLES | VVEL_AXIS_ROLES
# The stepped approach to the throttled duration and the start-up blend target
# exist only in the 1ME3B resolver.
ONE_ME3B_ONLY_ROLES = {
    "vvel_duration_throttled_ramp_delay",
    "vvel_duration_throttled_ramp_delay_axis",
    "vvel_duration_startup_blend",
    "vvel_duration_startup_blend_axis",
}
# The 1ND state-code dispatcher reads the resolver surfaces in place of a
# separate hot-intake idle pair.
STATE_WORD_PAIR_ROLES = {
    "vvel_duration_model_hot_intake_idle",
    "vvel_duration_model_hot_intake_idle_knock",
    "vvel_duration_model_hot_intake_idle_axis_x",
    "vvel_duration_model_hot_intake_idle_axis_y",
}
ABSENT = {
    "JK78C": {"vvel_duration_mode_14"} | ONE_ME3B_ONLY_ROLES,
    "1ND0A": {
        "vvel_duration_hot_intake_idle_floor",
        "vvel_duration_hot_intake_idle_knock_floor",
        "vvel_duration_hot_intake_idle_floor_axis",
    } | STATE_WORD_PAIR_ROLES | ONE_ME3B_ONLY_ROLES,
    "1ME3B": {"vvel_duration_mode_14"},
}
ABSENT["1ND3B"] = ABSENT["1ND0A"]


def _projected_axes(target):
    """Stub the canonical axes that the projection supplies before the registry runs."""
    native = {axis.address for axis in target.axes}
    return {
        f"{address:08x}": {}
        for table in target.tables
        for address in table.axis_x + table.axis_y
        if address not in native
    }


def _registry_text():
    with open(vq37_native_tables.DEFAULT_REGISTRY, encoding="utf-8") as handle:
        return handle.read()


def _edited_registry(tmp_path, old, new):
    text = _registry_text()
    assert text.count(old) == 1
    path = tmp_path / "native.toml"
    path.write_text(text.replace(old, new), encoding="utf-8")
    return path


def test_registry_requires_the_complete_vq37_target_set(tmp_path):
    path = tmp_path / "native.toml"
    path.write_text(
        "schema_version = 2\n[target.JK78C]\n",
        encoding="utf-8",
    )

    with pytest.raises(
        vq37_native_tables.NativeTableError,
        match="target set differs",
    ):
        vq37_native_tables.load_registry(path)


def test_registry_declares_every_role_on_every_target():
    registry = vq37_native_tables.load_registry()

    assert set(registry) == set(TARGETS)
    for rom in TARGETS:
        target = registry[rom]
        tables = {table.identifier for table in target.tables}
        axes = {axis.identifier for axis in target.axes}

        assert tables <= SELECTOR_ROLES | VVEL_TABLE_ROLES
        assert axes <= VVEL_AXIS_ROLES
        assert set(target.absent) == ABSENT[rom]
        assert tables | axes | set(target.absent) == ROLES
        for reason in target.absent.values():
            assert reason.strip()


def test_registry_binds_exact_stock_values_and_accessor_literals():
    registry = vq37_native_tables.load_registry()

    for rom in TARGETS:
        target = registry[rom]
        image = romkit.load(rom)

        assert hashlib.sha256(image.data).hexdigest() == target.stock_sha256
        entities = [
            (table.address, table.width * table.height, table.storagetype,
             table.values_sha256, table.pointer_bindings)
            for table in target.tables
        ] + [
            (axis.address, axis.length, axis.storagetype,
             axis.values_sha256, axis.pointer_bindings)
            for axis in target.axes
        ]
        for address, length, storagetype, values_sha256, bindings in entities:
            element = romkit.ELEM[storagetype]
            block = image.data[address : address + length * element]

            assert hashlib.sha256(block).hexdigest() == values_sha256
            assert bindings
            for pointer in bindings:
                stored = int.from_bytes(
                    image.data[pointer.site : pointer.site + 4], "big"
                )

                assert stored + pointer.offset == address
                assert pointer.accessor < pointer.site


def test_registry_shares_the_1nd_layout_between_1nd0a_and_1nd3b():
    registry = vq37_native_tables.load_registry()
    layouts = {}
    for rom in ("1ND0A", "1ND3B"):
        target = registry[rom]
        layouts[rom] = (
            {(t.identifier, t.address, t.pointer_bindings) for t in target.tables},
            {(a.identifier, a.address, a.pointer_bindings) for a in target.axes},
        )

    assert layouts["1ND0A"] == layouts["1ND3B"]
    assert registry["1ND0A"].stock_sha256 != registry["1ND3B"].stock_sha256


def test_registry_binds_the_1me3b_roles_to_undisplaced_literals():
    registry = vq37_native_tables.load_registry()
    target = registry["1ME3B"]
    reference = registry["JK78C"]

    identifiers = {e.identifier for e in (*target.tables, *target.axes)}
    assert identifiers == {
        e.identifier for e in (*reference.tables, *reference.axes)
    } | ONE_ME3B_ONLY_ROLES
    assert all(
        pointer.offset == 0
        for entity in (*target.tables, *target.axes)
        for pointer in entity.pointer_bindings
    )
    floors = {
        t.identifier: t for t in target.tables if t.identifier.endswith("_floor")
    }
    assert {t.address for t in floors.values()} == {0x165DC, 0x165EC}
    assert all(t.axis_x == (0x165CC,) for t in floors.values())


def test_registry_rejects_a_missing_role_declaration(tmp_path):
    path = _edited_registry(
        tmp_path,
        "[target.JK78C.absent]\nvvel_duration_mode_14 = ",
        "[target.JK78C.absent]\nvvel_duration_mode_14_removed = ",
    )

    with pytest.raises(
        vq37_native_tables.NativeTableError,
        match="roles differ; missing=\\['vvel_duration_mode_14'\\]",
    ):
        vq37_native_tables.load_registry(path)


def test_registry_rejects_an_absent_role_that_is_present(tmp_path):
    path = _edited_registry(
        tmp_path,
        "[target.JK78C.absent]\n",
        "[target.JK78C.absent]\nvvel_duration_running = \"stated\"\n",
    )

    with pytest.raises(
        vq37_native_tables.NativeTableError,
        match="absent roles are present",
    ):
        vq37_native_tables.load_registry(path)


def test_registry_rejects_a_curve_with_a_second_axis(tmp_path):
    path = _edited_registry(
        tmp_path,
        "axis_x = 0x00016CA4\nname = \"VVEL Duration Target - Running\"",
        "axis_x = 0x00016CA4\naxis_y = 0x00016C84\n"
        "name = \"VVEL Duration Target - Running\"",
    )

    with pytest.raises(
        vq37_native_tables.NativeTableError,
        match="one-dimensional table declares axis_y",
    ):
        vq37_native_tables.load_registry(path)


def test_registry_rejects_a_negative_pointer_offset(tmp_path):
    path = _edited_registry(
        tmp_path,
        "{ site = 0x00056678, accessor = 0x000564A4, offset = 0x10 }",
        "{ site = 0x00056678, accessor = 0x000564A4, offset = -16 }",
    )

    with pytest.raises(
        vq37_native_tables.NativeTableError,
        match="offset is invalid",
    ):
        vq37_native_tables.load_registry(path)


def test_apply_target_publishes_every_registered_table_and_axis():
    for rom in TARGETS:
        target = vq37_native_tables.load_registry()[rom]
        image = romkit.load(rom)
        projected = _projected_axes(target)
        maps, axes, overrides = vq37_native_tables.apply_target(
            rom, {}, projected, {"table": {}}, image
        )
        table_keys = {f"{table.address:08x}" for table in target.tables}
        axis_keys = {f"{axis.address:08x}" for axis in target.axes}

        assert set(maps) == table_keys
        assert set(overrides["table"]) == table_keys
        assert set(axes) == axis_keys | set(projected)
        assert set(overrides["axis"]) == axis_keys
        for table in target.tables:
            key = f"{table.address:08x}"
            model = maps[key]

            assert model["width"] == table.width
            assert model["dims"] == (2 if table.height > 1 else 1)
            assert model["storagetype"] == table.storagetype
            assert model["confidence"] == table.confidence
            assert model["scale_conf"] == table.scale_conf
            assert model["note"].startswith(
                f"Exact {rom} target-native table at {table.address:#x}"
            )
            assert overrides["table"][key]["name"] == table.name
            assert overrides["table"][key]["emit"] is True
            assert model["accessors"] == sorted({
                f"{pointer.accessor:08x}"
                for pointer in table.pointer_bindings
            })
            for axis_key in model["axis_x"] + model["axis_y"]:
                assert axis_key in axes
        for axis in target.axes:
            key = f"{axis.address:08x}"
            model = axes[key]

            assert model["kind"] == axis.kind
            assert model["len"] == axis.length
            assert len(model["values"]) == axis.length
            assert model["values"] == sorted(model["values"])
            assert model["confidence"] == axis.confidence
            assert model["scale_expr"] == axis.scale_expr
            assert model["scale_evidence"] == "registry:target-native"
            assert model["note"].startswith(
                f"Exact {rom} target-native axis at {axis.address:#x}"
            )
            assert overrides["axis"][key] == {
                "name": axis.name,
                "format": axis.format,
                "fine": axis.fine,
                "coarse": axis.coarse,
            }


def test_apply_target_describes_a_displaced_base_literal():
    rom = "JK78C"
    target = vq37_native_tables.load_registry()[rom]
    image = romkit.load(rom)
    maps, axes, _overrides = vq37_native_tables.apply_target(
        rom, {}, _projected_axes(target), {"table": {}}, image
    )
    floor = maps["0001600a"]
    rpm_axis = axes["000160ca"]

    assert floor["axis_x"] == ["00015ffa"]
    assert "through literal 0x56678 + 0x10" in floor["note"]
    assert "through literal 0x56678 + 0xd0" in rpm_axis["note"]
    assert rpm_axis["values"] == [128, 192, 256, 320, 384, 448, 512, 640]


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
            rom, occupied, _projected_axes(target), {"table": {}}, image
        )


def test_apply_target_rejects_a_native_axis_collision():
    rom = "JK78C"
    target = vq37_native_tables.load_registry()[rom]
    image = romkit.load(rom)
    axes = _projected_axes(target)
    axes[f"{target.axes[0].address:08x}"] = {}

    with pytest.raises(
        vq37_native_tables.NativeTableError,
        match="native axis .* collides with the projection",
    ):
        vq37_native_tables.apply_target(rom, {}, axes, {"table": {}}, image)


def test_apply_target_rejects_a_displaced_pointer_that_misses():
    rom = "JK78C"
    image = romkit.load(rom)
    binding = vq37_native_tables.PointerBinding(
        site=0x56678, accessor=0x564A4, offset=0x12
    )

    with pytest.raises(
        vq37_native_tables.NativeTableError,
        match="pointer at 0x56678 is 0x15ffa \\+ 0x12, expected 0x1600a",
    ):
        vq37_native_tables._verify_bindings(rom, image, 0x1600A, [binding])


def test_apply_target_rejects_a_foreign_image():
    target = vq37_native_tables.load_registry()["JK78C"]

    with pytest.raises(
        vq37_native_tables.NativeTableError,
        match="native table target is JK78C",
    ):
        vq37_native_tables.apply_target(
            "JK78C", {}, _projected_axes(target), {"table": {}},
            romkit.load("1ND0A"),
        )


def test_apply_target_ignores_a_rom_without_native_tables():
    maps, axes, overrides = vq37_native_tables.apply_target(
        "JK08A", {}, {}, {"table": {}}, romkit.load("JK08A")
    )

    assert maps == {}
    assert axes == {}
    assert overrides == {"table": {}}
