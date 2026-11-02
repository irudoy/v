"""Calibration applies only over a fresh stock build with the extracted settings."""

from dataclasses import replace
from functools import lru_cache
import json

import pytest

from patches import apply_calibration
from patches import build_rom
from patches import calibration_file
from patches import extract_calibration
from patches import rolling_launch
from patches import rom_checksums
from patches import runtime_targets


@lru_cache(maxsize=None)
def target(rom):
    return runtime_targets.load_runtime_target(rom)


@lru_cache(maxsize=None)
def built(rom, profile=None):
    return build_rom.build_image(
        target(rom).stock_image.data, profile=profile, source_name=f"{rom} stock"
    ).data


def edited(rom, data, edits):
    data = bytearray(data)
    for address, value in edits:
        data[address] ^= value
    return bytes(rom_checksums.recalculate(data, target(rom).checksum_layout))


def map_edits(rom):
    families = target(rom).map_layout.families
    edits = [(family.canonical_address, 0x01) for family in families]
    edits += [
        (address, 0x02 + slot)
        for family in families
        for slot, address in enumerate(family.copies)
    ]
    return edits


def custom_profile():
    profile = build_rom.builtin_profile()
    return replace(
        profile,
        name="custom",
        calibration=replace(profile.calibration, enable_mask=0x03),
        telemetry=replace(profile.telemetry, enabled=True),
    )


def test_calibration_of_another_rom_is_refused():
    calibration = extract_calibration.extract(
        target("JK08A").stock_image.data
    ).calibration
    with pytest.raises(apply_calibration.ApplicationError, match="belongs to JK08A"):
        apply_calibration.apply(target("JK00A").stock_image.data, calibration)


def test_calibration_bound_to_another_stock_image_is_refused():
    calibration = extract_calibration.extract(
        target("JK08A").stock_image.data
    ).calibration
    foreign = replace(calibration, stock_sha256="0" * 64)
    with pytest.raises(apply_calibration.ApplicationError, match="stock SHA-256"):
        apply_calibration.apply(target("JK08A").stock_image.data, foreign)


@pytest.mark.parametrize(("rom", "refused"), (("JK08A", True), ("JK00D", False)))
def test_misfire_calibration_equal_to_the_spark_cut_marker_is_refused(rom, refused):
    address = rolling_launch.MISFIRE_CALIBRATION_ADDRESS
    stock = target(rom).stock_image.data[address]
    source = edited(rom, built(rom), [(address, stock ^ rolling_launch.MISFIRE_MARKER)])
    calibration = extract_calibration.extract(source, source_name="calibrated build").calibration
    if not refused:
        assert apply_calibration.apply(built(rom), calibration).data == source
        return
    with pytest.raises(apply_calibration.ApplicationError, match="misfire marker 0x01"):
        apply_calibration.apply(built(rom), calibration)


@pytest.mark.slow
@pytest.mark.parametrize("rom", runtime_targets.SUPPORTED_ROMS)
def test_application_over_a_fresh_build_reproduces_the_source(rom):
    source = edited(rom, built(rom), map_edits(rom))
    extraction = extract_calibration.extract(source, source_name="calibrated build")
    profile = build_rom.parse_profile(
        extract_calibration.profile_bytes(extraction, "transfer"), "transfer"
    )
    fresh = built(rom, profile)
    result = apply_calibration.apply(fresh, extraction.calibration)
    assert result.data == source
    expected = {"can_telemetry": "matched"}
    if target(rom).rolling_layout is not None:
        expected["rolling_launch"] = "matched"
    assert dict(result.settings) == expected


@pytest.mark.slow
def test_build_with_other_settings_is_refused_unless_replaced():
    source = edited("JK08A", built("JK08A", custom_profile()), ((0x8725, 0x01),))
    calibration = extract_calibration.extract(source).calibration
    with pytest.raises(
        apply_calibration.ApplicationError,
        match="differ from the extracted settings: rolling_launch, can_telemetry",
    ):
        apply_calibration.apply(built("JK08A"), calibration)
    result = apply_calibration.apply(
        built("JK08A"), calibration, replace_settings=True
    )
    assert dict(result.settings) == {
        "rolling_launch": "replaced",
        "can_telemetry": "replaced",
    }
    assert result.data == edited("JK08A", built("JK08A"), ((0x8725, 0x01),))


@pytest.mark.slow
@pytest.mark.parametrize(
    ("make_input", "message"),
    (
        (lambda: edited("JK08A", built("JK08A"), ((0x8725, 0x01),)),
         "first difference at 0x8725"),
        (lambda: target("JK08A").stock_image.data, "is not a fresh build"),
    ),
)
def test_input_that_is_not_a_fresh_build_is_refused(make_input, message):
    calibration = extract_calibration.extract(
        edited("JK08A", target("JK08A").stock_image.data, ((0x8725, 0x01),))
    ).calibration
    with pytest.raises(apply_calibration.ApplicationError, match=message):
        apply_calibration.apply(make_input(), calibration)


@pytest.mark.slow
def test_cli_creates_four_artifacts_once_and_refuses_tracked_output(tmp_path, capsys):
    source = edited("JK08A", built("JK08A"), ((0x8725, 0x01),))
    calibration = extract_calibration.extract(source).calibration
    fresh = tmp_path / "fresh.bin"
    fresh.write_bytes(built("JK08A"))
    calibration_path = tmp_path / "calibration.toml"
    calibration_path.write_text(calibration_file.dumps(calibration))
    output = tmp_path / "calibrated.bin"
    arguments = [
        str(fresh), "--calibration", str(calibration_path), "--output", str(output),
    ]
    assert apply_calibration.main(arguments) == 0
    assert "status=created" in capsys.readouterr().out
    assert output.read_bytes() == source
    manifest = json.loads((tmp_path / "calibrated.bin.manifest.json").read_text())
    assert manifest["calibration"]["settings"] == {
        "rolling_launch": "matched",
        "can_telemetry": "matched",
    }
    assert manifest["output"]["hardware_status"] == "UNTESTED"
    assert (tmp_path / "calibrated.bin.sha256").exists()
    assert (tmp_path / "calibrated.bin.md5").exists()
    assert apply_calibration.main(arguments) == 0
    assert "status=already_exact" in capsys.readouterr().out
    tracked = calibration_file.ROOT / "patches/calibrated.bin"
    with pytest.raises(SystemExit):
        apply_calibration.main(arguments[:-1] + [str(tracked)])
    assert not tracked.exists()
