"""Preflash qualifies only a HEAD build of a green, clean commit."""

from dataclasses import replace
import hashlib
import json
from functools import lru_cache
from types import SimpleNamespace

import pytest

from patches import build_rom
from patches import map_switching_cruise_free
from patches import map_switching_eeprom
from patches import preflash
from patches import rolling_launch
from patches import rom_checksums
from patches import runtime_targets


COMMIT = "0123456789abcdef0123456789abcdef01234567"
RUN_URL = "https://github.com/irudoy/vhrev/actions/runs/7"


@lru_cache(maxsize=None)
def target(rom):
    return runtime_targets.load_runtime_target(rom)


@lru_cache(maxsize=None)
def built(rom):
    return build_rom.build_image(
        target(rom).stock_image.data, source_name=f"{rom} stock"
    ).data


def edited(rom, data, edits):
    data = bytearray(data)
    for address, value in edits:
        data[address] ^= value
    return bytes(rom_checksums.recalculate(data, target(rom).checksum_layout))


def map_edits(rom):
    return [(family.canonical_address, 0x01) for family in target(rom).map_layout.families]


def test_builder_output_qualifies_with_no_calibration():
    report = preflash.check_image(built("JK08A"), "JK08A")
    assert (report.rom, report.runtime, report.calibration_bytes) == ("JK08A", "current", 0)
    assert report.stock_sha256 == hashlib.sha256(target("JK08A").stock_image.data).hexdigest()


@pytest.mark.parametrize(("rom", "base", "runtime"), (
    ("JK08A", "build", "current"),
    ("JK00D", "build", "current"),
    ("JK08A", "stock", "absent"),
    ("1EK7A", "build", "current"),
    ("1EK7A", "stock", "absent"),
))
def test_calibrated_image_qualifies_when_it_rebuilds(rom, base, runtime):
    data = built(rom) if base == "build" else target(rom).stock_image.data
    report = preflash.check_image(edited(rom, data, map_edits(rom)), rom)
    assert report.runtime == runtime
    assert report.calibration_bytes == len(target(rom).map_layout.families)


@pytest.mark.parametrize("rom", ("JK08A", "JK00D", "1ME3B"))
def test_non_default_map_switching_settings_qualify(rom):
    profile = replace(
        build_rom.builtin_profile(rom),
        map_switching=map_switching_cruise_free.CruiseFreeConfig(
            flags=(
                map_switching_cruise_free.FLAG_ASCD_ENABLED
                | map_switching_cruise_free.FLAG_CRUISE_FREE_ENABLED
                | map_switching_cruise_free.FLAG_TACH_ALLOWED
            ),
            feedback_mode=map_switching_cruise_free.FEEDBACK_MODE_NAMES["all"],
        ),
        map_switching_eeprom=map_switching_eeprom.EepromPersistenceConfig(
            flags=0,
            write_delay_ticks=200,
            wip_timeout_ticks=15,
            max_retries_per_slot=3,
        ),
    )
    data = build_rom.build_image(
        target(rom).stock_image.data,
        rom=rom,
        profile=profile,
        source_name=f"{rom} stock",
    ).data
    report = preflash.check_image(data, rom)
    assert (report.rom, report.runtime, report.calibration_bytes) == (rom, "current", 0)


def built_with(rom, **changes):
    profile = build_rom.builtin_profile(rom)
    profile = replace(profile, calibration=replace(profile.calibration, **changes))
    return build_rom.build_image(
        target(rom).stock_image.data, rom=rom, profile=profile, source_name=f"{rom} stock"
    ).data


def without_hold_actuator(monkeypatch):
    stock = target("JK08A")
    patched = replace(
        stock, rolling_layout=replace(stock.rolling_layout, hold_actuator=False)
    )
    load = runtime_targets.load_runtime_target
    monkeypatch.setattr(
        runtime_targets,
        "load_runtime_target",
        lambda rom: patched if rom == "JK08A" else load(rom),
    )


def test_hold_mode_maps_qualify_with_the_hold_actuator():
    assert target("JK08A").rolling_layout.hold_actuator is True
    data = built_with("JK08A", mode=rolling_launch.Mode.HOLD, enable_mask=0x05)
    assert preflash.check_image(data, "JK08A").runtime == "current"


def test_hold_mode_map_is_refused_without_a_hold_actuator(monkeypatch):
    data = built_with("JK08A", mode=rolling_launch.Mode.HOLD, enable_mask=0x05)
    without_hold_actuator(monkeypatch)
    with pytest.raises(preflash.PreflashError, match=r"enables map 1, 3 in hold mode"):
        preflash.check_image(data, "JK08A")


@pytest.mark.parametrize(("mode", "mask"), (
    (rolling_launch.Mode.OBSERVE, 0x1F),
    (rolling_launch.Mode.HOLD, 0x00),
))
def test_observe_or_disabled_hold_qualifies_without_a_hold_actuator(
    monkeypatch, mode, mask
):
    data = built_with("JK08A", mode=mode, enable_mask=mask)
    without_hold_actuator(monkeypatch)
    report = preflash.check_image(data, "JK08A")
    assert (report.rom, report.runtime) == ("JK08A", "current")


def trimmed_map_4():
    slots = (rolling_launch.Slot(integral_gain=2),) * 3 + (
        rolling_launch.Slot(
            integral_gain=2, max_trim_rpm=20, max_trim_speed=20, floor_command=120
        ),
        rolling_launch.Slot(),
    )
    return built_with(
        "JK08A", mode=rolling_launch.Mode.HOLD, enable_mask=0x0E, slots=slots
    )


def test_trimmed_slot_qualifies_with_the_efficiency_of_the_image():
    data = trimmed_map_4()
    assert preflash.check_image(data, "JK08A").runtime == "current"


@pytest.mark.parametrize("field", ("efficiency", "table"))
def test_trim_efficiency_that_differs_from_the_image_is_refused(field):
    if field == "efficiency":
        # The low byte of E[20] in the efficiency table.
        edit = (target("JK08A").rolling_layout.efficiency.start + 2 * 20 + 1, 0x01)
    else:
        # The F point of a trim of 20 APC counts.
        edit = (build_rom.TRIM_TABLE_ADDRESS + 7, 0x01)
    data = edited("JK08A", trimmed_map_4(), [edit])
    with pytest.raises(preflash.PreflashError, match="refresh_rolling_launch.py"):
        preflash.check_image(data, "JK08A")


def test_efficiency_check_compares_the_whole_table_with_f():
    data = trimmed_map_4()
    extraction = SimpleNamespace(rolling=rolling_launch.Calibration())
    preflash.require_trim_efficiency(data, target("JK08A"), extraction)
    span = target("JK08A").rolling_layout.efficiency
    for word in (0, 1, 40):
        stale = bytearray(data)
        stale[span.start + 2 * word + 1] ^= 0x01
        with pytest.raises(
            preflash.PreflashError,
            match="trim efficiency table differs from the F table",
        ):
            preflash.require_trim_efficiency(bytes(stale), target("JK08A"), extraction)
    # An image without Rolling Launch settings carries no table to compare.
    preflash.require_trim_efficiency(
        bytes(stale), target("JK08A"), SimpleNamespace(rolling=None)
    )


def test_misfire_calibration_equal_to_the_marker_is_refused():
    address = rolling_launch.MISFIRE_CALIBRATION_ADDRESS
    stock = target("JK08A").stock_image.data[address]
    data = edited("JK08A", built("JK08A"), [(address, stock ^ rolling_launch.MISFIRE_MARKER)])
    with pytest.raises(preflash.PreflashError, match="misfire marker"):
        preflash.check_image(data, "JK08A")


def test_image_of_another_rom_is_refused():
    with pytest.raises(preflash.PreflashError, match="identity is JK00D, not JK08A"):
        preflash.check_image(built("JK00D"), "JK08A")


def test_change_outside_the_calibration_ranges_is_refused():
    with pytest.raises(preflash.PreflashError, match="outside the calibration ranges"):
        preflash.check_image(edited("JK08A", built("JK08A"), [(0x200, 0x01)]), "JK08A")


def test_invalid_checksum_is_refused():
    data = bytearray(edited("JK08A", built("JK08A"), map_edits("JK08A")))
    data[target("JK08A").map_layout.families[0].canonical_address] ^= 0x01
    with pytest.raises(preflash.PreflashError, match="checksum"):
        preflash.check_image(data, "JK08A")


def test_1ek7a_rebuilt_image_requires_its_exact_stock_prefix():
    data = bytearray(built("1EK7A"))
    assert data[0x6EFE:0x6F00] == bytes.fromhex("7c56")
    data[0x6EFE:0x6F00] = bytes.fromhex("73da")
    with pytest.raises(preflash.PreflashError, match=r"below 0x8200 differ from stock"):
        preflash.check_image(data, "1EK7A")


def test_damaged_runtime_payload_is_refused():
    unit = target("JK08A").map_layout.assembly_units[0]
    with pytest.raises(preflash.PreflashError):
        preflash.check_image(edited("JK08A", built("JK08A"), [(unit.span.start, 0x01)]), "JK08A")


def test_image_that_does_not_rebuild_is_refused(monkeypatch):
    original = preflash._rebuild

    def drift(stock, target, extraction):
        data, runtime = original(stock, target, extraction)
        data = bytearray(data)
        data[0x400] ^= 0x01
        return bytes(data), runtime

    monkeypatch.setattr(preflash, "_rebuild", drift)
    with pytest.raises(preflash.PreflashError, match="differs from its rebuild at 0x400"):
        preflash.check_image(built("JK08A"), "JK08A")


class Runner:
    """Answer the commands of preflash and record them in order."""

    def __init__(self, *, status="", runs=None, pytest=0, gate=0):
        self.answers = {"status": status, "runs": runs, "pytest": pytest, "gate": gate}
        self.commands = []

    def __call__(self, command, **kwargs):
        self.commands.append(command)
        if command[:2] == ["git", "status"]:
            return SimpleNamespace(returncode=0, stdout=self.answers["status"], stderr="")
        if command[:2] == ["git", "rev-parse"]:
            return SimpleNamespace(returncode=0, stdout=COMMIT + "\n", stderr="")
        if command[:3] == ["gh", "run", "list"]:
            runs = self.answers["runs"]
            if runs is None:
                runs = [dict(databaseId=7, status="completed", conclusion="success", url=RUN_URL)]
            return SimpleNamespace(returncode=0, stdout=json.dumps(runs), stderr="")
        if command[0].endswith("run.sh"):
            return SimpleNamespace(returncode=self.answers["gate"])
        return SimpleNamespace(returncode=self.answers["pytest"])


def test_green_run_is_looked_up_for_the_exact_commit_only():
    runner = Runner()
    assert preflash.green_run(COMMIT, runner)["url"] == RUN_URL
    [command] = runner.commands
    assert command[command.index("--commit") + 1] == COMMIT
    assert command[command.index("--workflow") + 1] == "Verify"


@pytest.mark.parametrize(("runs", "message"), (
    ([], "has no Verify run"),
    ([dict(databaseId=7, status="in_progress", conclusion="", url=RUN_URL)], "has not finished"),
    ([dict(databaseId=7, status="completed", conclusion="failure", url=RUN_URL)], "concluded failure"),
    ([dict(databaseId=7, status="completed", conclusion="cancelled", url=RUN_URL)], "concluded cancelled"),
))
def test_commit_without_a_green_run_is_refused(runs, message):
    with pytest.raises(preflash.PreflashError, match=message):
        preflash.green_run(COMMIT, Runner(runs=runs))


def test_any_green_run_of_the_commit_qualifies_it():
    runs = [
        dict(databaseId=8, status="completed", conclusion="failure", url="failed"),
        dict(databaseId=7, status="completed", conclusion="success", url=RUN_URL),
    ]
    assert preflash.green_run(COMMIT, Runner(runs=runs))["databaseId"] == 7


def test_dirty_tracked_worktree_is_refused():
    with pytest.raises(preflash.PreflashError, match="tracked files differ from HEAD"):
        preflash.head_commit(Runner(status=" M patches/build_rom.py\n"))


@pytest.fixture
def image(tmp_path):
    path = tmp_path / "JK08A-built.bin"
    path.write_bytes(built("JK08A"))
    return path


def test_qualified_image_runs_the_rom_tests_then_the_rom_gate(image, capsys):
    runner = Runner()
    assert preflash.main([str(image), "--rom", "JK08A", "--pytest", "uv run pytest"], runner) == 0
    tests, gate = runner.commands[3:]
    assert tests[:4] == ["uv", "run", "pytest", "-q"]
    assert tests[tests.index("--rom") + 1] == "JK08A" and set(preflash.TESTS) <= set(tests)
    assert gate == [str(preflash.GATE), "--rom", "JK08A"]
    image_sha256 = hashlib.sha256(built("JK08A")).hexdigest()
    final = capsys.readouterr().out.splitlines()[-1]
    assert final.startswith(f"PREFLASH status=PASS rom=JK08A image_sha256={image_sha256} ")
    assert final.endswith(f" commit={COMMIT} ci_run={RUN_URL}")


@pytest.mark.parametrize(("answers", "executed"), (
    (dict(runs=[]), 3),
    (dict(pytest=1), 4),
    (dict(gate=1), 5),
))
def test_refusal_stops_the_qualification(image, capsys, answers, executed):
    runner = Runner(**answers)
    assert preflash.main([str(image), "--rom", "JK08A"], runner) == 1
    assert len(runner.commands) == executed
    assert "PREFLASH status=REFUSE rom=JK08A" in capsys.readouterr().err


def test_refused_image_runs_no_command(tmp_path, capsys):
    path = tmp_path / "JK00D-built.bin"
    path.write_bytes(built("JK00D"))
    runner = Runner()
    assert preflash.main([str(path), "--rom", "JK08A"], runner) == 1
    assert runner.commands == []
    assert "identity is JK00D" in capsys.readouterr().err


def test_auto_rom_selector_is_not_accepted(image):
    with pytest.raises(SystemExit) as error:
        preflash.main([str(image), "--rom", "auto"], Runner())
    assert error.value.code == 2
