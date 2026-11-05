"""Upgrade a flashed historical Rolling Launch endpoint through the builder."""

import contextlib
from functools import lru_cache
import io

import pytest

from patches import build_rom, calibration_ranges, extract_calibration
from patches import rolling_launch, rom_checksums, runtime_targets
from patches.tests import rolling_endpoint_images as endpoint_images
from patches.tests.test_build_rom import parse, profile_text


KEY = "schema-5-fixed-trim"


def target():
    return runtime_targets.load_runtime_target("JK08A")


@lru_cache(maxsize=1)
def historical_image():
    """Return a schema 5 endpoint with calibration in Map 1 and a Map 3 copy."""
    current = target()
    built = build_rom.build_image(
        current.stock_image.data, source_name="JK08A stock"
    ).data
    data = endpoint_images.with_endpoint(
        current, built, KEY, endpoint_images.record(KEY)
    )
    family = current.map_layout.families[0]
    data[family.canonical_address] ^= 1
    data[family.copies[1] + 3] ^= 0x11
    return bytes(rom_checksums.recalculate(data, current.checksum_layout))


def efficiency(data):
    span = target().rolling_layout.efficiency
    return bytes(data[span.start : span.end])


def test_historical_settings_have_no_automatic_upgrade():
    extraction = extract_calibration.extract(historical_image())
    assert extraction.rolling is None
    ((component, record, schema_version, _fields),) = extraction.unexpressed
    assert (component, record, schema_version) == ("rolling_launch", KEY, 5)
    with pytest.raises(build_rom.BuildError, match="no profile schema 4 form"):
        build_rom.upgrade_image(historical_image())


@pytest.mark.parametrize("disabled", (False, True))
def test_explicit_settings_replace_the_endpoint_and_keep_calibration(disabled):
    source = historical_image()
    profile = (
        build_rom.builtin_profile()
        if disabled
        else parse(profile_text(mode='"observe"', max_trim_rpm="12"))
    )
    result = build_rom.upgrade_image(source, profile=profile)
    for offset in calibration_ranges.load("JK08A").offsets():
        assert result.data[offset] == source[offset], hex(offset)
    span = target().rolling_layout.configuration
    assert result.data[span.start : span.end] == profile.calibration.to_bytes()
    assert efficiency(result.data) == build_rom.efficiency_table(source).to_bytes()
    assert result.calibration_transfer["source_runtime"]["rolling_launch"] == KEY
    assert result.calibration_transfer["settings"]["rolling_launch"] == "replaced"
    before = extract_calibration.extract(source)
    after = extract_calibration.extract(result.data)
    assert dict(after.calibration.source)["rolling_launch"] == "current"
    assert after.rolling == profile.calibration
    assert after.telemetry == before.telemetry
    assert after.calibration.elements == before.calibration.elements
    if disabled:
        assert after.rolling == rolling_launch.Calibration()


def test_explicit_profile_of_another_rom_scope_is_refused():
    other = build_rom.builtin_profile(runtime_targets.RELOCATED_8MFK_FAMILY)
    with pytest.raises(build_rom.BuildError, match="does not match selected ROM"):
        build_rom.upgrade_image(historical_image(), profile=other)


def test_cli_disable_option_requires_upgrade_and_no_profile(tmp_path):
    source = tmp_path / "source.bin"
    for arguments in (
        ["--disable-rolling-launch"],
        ["--disable-rolling-launch", "--upgrade", "--profile", str(tmp_path / "p.toml")],
    ):
        error = io.StringIO()
        with contextlib.redirect_stderr(error), pytest.raises(SystemExit) as stopped:
            build_rom.main([str(source), *arguments])
        assert stopped.value.code == 2
        assert "--disable-rolling-launch takes --upgrade and no --profile" in error.getvalue()
