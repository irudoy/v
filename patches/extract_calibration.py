#!/usr/bin/env python3
"""Extract the calibration and runtime settings of a ROM image.

The input is a registered stock image or an image built from one: the stock
image with calibration edits, a current builder output, or a registered
historical runtime endpoint of the selected ROM. Every difference from the
stock image must lie in the calibration ranges, the builder write sets, the
writes of the registered historical endpoints, or the checksum fields, and
these write sets must hold no runtime or one complete runtime. Partial and
unknown states are rejected with a named reason.

The command writes a local calibration file and, when the source carries
Rolling Launch settings that the current profile schema expresses, a local
build profile with the Rolling Launch and CAN telemetry settings of the
source. A source without runtime settings yields the calibration file only.
A historical Rolling Launch record that the profile schema cannot express is
reported with its fields; the command then writes the calibration file only
and exits with status 3. The Rolling Launch efficiency table derives from F
and is neither a setting nor calibration: the calibration carries F, and a
build or an application derives the table again.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import apply_map_switching
from patches import build_rom
from patches import calibration_file
from patches import calibration_ranges
from patches import can_telemetry
from patches import can_telemetry_history
from patches import map_switching_cruise_free
from patches import rolling_launch
from patches import rom_checksums
from patches import runtime_endpoints
from patches import runtime_targets


EXIT_SETTINGS_NOT_EXPRESSED = 3
ABSENT = "absent"


class ExtractionError(ValueError):
    """Raised when an image is not a supported extraction input."""


@dataclass(frozen=True)
class Extraction:
    calibration: calibration_file.CalibrationFile
    rolling: rolling_launch.Calibration | None
    telemetry: can_telemetry.Configuration | None
    unexpressed: tuple[tuple[str, str, int, dict], ...]
    map_switching: map_switching_cruise_free.CruiseFreeConfig | None = None

    @property
    def has_profile(self):
        return self.rolling is not None and not self.unexpressed


def sha256(data):
    return hashlib.sha256(bytes(data)).hexdigest()


def fresh_build_reference(target):
    """Return the calibration bytes of a fresh stock build of ``target``:
    stock bytes, with each Map 2 through Map 5 slot holding Map 1."""
    data = bytearray(target.stock_image.data)
    for family in target.map_layout.families:
        table = data[
            family.canonical_address :
            family.canonical_address + family.byte_length
        ]
        for address in family.copies:
            data[address : address + family.byte_length] = table
    return bytes(data)


def _elements(source, reference, ranges):
    elements = []
    for item in ranges.ranges:
        start = None
        for offset in range(item.start, item.end + 1):
            differs = offset < item.end and source[offset] != reference[offset]
            if differs and start is None:
                start = offset
            elif not differs and start is not None:
                elements.append(
                    calibration_file.Element(start, bytes(source[start:offset]))
                )
                start = None
    return tuple(elements)


def _rolling_settings(source, layout, state):
    record = runtime_endpoints.configuration_record(source, layout, state)
    if state == "current":
        schema_version = rolling_launch.CONFIG_SCHEMA_VERSION
    else:
        schema_version = runtime_endpoints.historical_endpoint(
            state
        ).configuration_schema_version
    if schema_version != rolling_launch.CONFIG_SCHEMA_VERSION:
        fields = runtime_endpoints.historical_configuration_fields(
            record, schema_version
        )
        return record, None, (("rolling_launch", state, schema_version, fields),)
    calibration = rolling_launch.Calibration.from_bytes(record)
    if not calibration.is_valid() or calibration.to_bytes() != record:
        raise ExtractionError(
            f"Rolling Launch record of endpoint {state!r} does not round trip"
        )
    return record, calibration, ()


def extract(source, *, rom=build_rom.AUTO_ROM, source_name="<memory>"):
    """Extract the calibration and settings of one image in memory."""
    source = bytes(source)
    try:
        selected, _detection = build_rom.select_rom(source, rom)
    except build_rom.BuildError as error:
        raise ExtractionError(str(error)) from error
    target = runtime_targets.load_runtime_target(selected)
    stock = target.stock_image.data
    if len(source) != len(stock):
        raise ExtractionError(
            f"{source_name}: image has {len(source)} bytes, expected "
            f"{len(stock)} for {selected}"
        )
    try:
        rom_checksums.require_valid(source, target.checksum_layout, source_name)
    except rom_checksums.ChecksumError as error:
        raise ExtractionError(str(error)) from error

    ranges = calibration_ranges.load(selected)
    # A registered historical endpoint may write outside the current builder
    # write sets; classification then requires exactly one complete endpoint.
    permitted = (
        ranges.write_offsets
        | ranges.checksum_offsets
        | runtime_endpoints.historical_write_offsets(selected)
        | frozenset(
            offset for item in ranges.window
            for offset in range(item.start, item.end)
        )
    )
    outside = [
        offset
        for offset, (actual, expected) in enumerate(zip(source, stock))
        if actual != expected and offset not in permitted
    ]
    if outside:
        raise ExtractionError(
            f"{source_name}: change at {outside[0]:#x} is outside the "
            f"calibration ranges of {selected} ({len(outside)} bytes)"
        )

    if all(source[offset] == stock[offset] for offset in ranges.write_offsets):
        map_state = rolling_state = telemetry_state = ABSENT
        reference = stock
    else:
        try:
            classification = runtime_endpoints.classify_runtime(
                source, target, source_name
            )
        except runtime_endpoints.EndpointError as error:
            raise ExtractionError(str(error)) from error
        map_state = "current"
        rolling_state = classification.rolling
        telemetry_state = classification.telemetry
        reference = fresh_build_reference(target)

    settings = []
    rolling = None
    unexpressed = ()
    if map_state != ABSENT and target.rolling_layout is None:
        # A target without a Rolling Launch layer builds the observe
        # calibration of its built-in profile.
        rolling = rolling_launch.Calibration()
    if rolling_state != ABSENT:
        record, rolling, unexpressed = _rolling_settings(
            source, target.rolling_layout, rolling_state
        )
        # A current record holds logical settings only; a historical record
        # binds its exact bytes, which no current build reproduces.
        settings.append(("rolling_launch", sha256(record)))
    telemetry = None
    if telemetry_state != ABSENT:
        historical = can_telemetry_history.endpoint(telemetry_state)
        if historical is not None:
            # Transfer logical settings through the current profile format;
            # the historical wire identity is not a calibration setting.
            telemetry = historical.configuration(historical.record(source))
        else:
            layout = target.telemetry_layout
            record = source[layout.configuration.start : layout.configuration.end]
            telemetry = can_telemetry.Configuration.from_bytes(record)
            if telemetry.to_bytes() != record:
                raise ExtractionError(
                    f"{source_name}: CAN telemetry record does not round trip"
                )
            settings.append(("can_telemetry", sha256(record)))

    map_switching_cfg = None
    if map_state != ABSENT and target.map_layout.cruise_free is not None:
        cf_span = target.map_layout.cruise_free.config
        cf_record = bytes(source[cf_span.start : cf_span.end])
        if cf_record != bytes([0xFF]) * cf_span.size:
            map_switching_cfg = (
                map_switching_cruise_free.CruiseFreeConfig.from_bytes(
                    cf_record
                )
            )
            if map_switching_cfg.to_bytes() != cf_record:
                raise ExtractionError(
                    f"{source_name}: map_switching record does not round trip"
                )
    calibration = calibration_file.CalibrationFile(
        rom=selected,
        stock_sha256=sha256(stock),
        source=(
            ("sha256", sha256(source)),
            ("map_switching", map_state),
            ("rolling_launch", rolling_state),
            ("can_telemetry", telemetry_state),
        ),
        settings=tuple(settings),
        elements=_elements(source, reference, ranges),
    )
    return Extraction(
        calibration=calibration,
        rolling=rolling,
        telemetry=telemetry,
        unexpressed=unexpressed,
        map_switching=map_switching_cfg,
    )


def profile_bytes(extraction, name):
    """Return the verified local profile text of an extraction."""
    text = build_rom.profile_text(
        name,
        extraction.calibration.rom,
        extraction.rolling,
        extraction.telemetry,
        extraction.map_switching,
    )
    profile = build_rom.parse_profile(text.encode("utf-8"), name)
    telemetry = extraction.telemetry or can_telemetry.default_configuration()
    expected_ms = (
        extraction.map_switching
        or map_switching_cruise_free.CruiseFreeConfig()
    )
    if (
        profile.calibration != extraction.rolling
        or profile.telemetry != telemetry
        or profile.map_switching != expected_ms
    ):
        raise ExtractionError("extracted profile does not round trip")
    return text.encode("utf-8")


def default_paths(source):
    source = Path(source)
    return (
        source.with_name(f"{source.stem}-calibration.toml"),
        source.with_name(f"{source.stem}-profile.toml"),
    )


def _format_fields(fields):
    return " ".join(
        f"{key}={list(value) if isinstance(value, tuple) else value}"
        for key, value in fields.items()
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="input ROM image")
    parser.add_argument(
        "--rom",
        default=build_rom.AUTO_ROM,
        metavar="auto|ROM",
        help="exact ROM selector; defaults to immutable-byte detection",
    )
    parser.add_argument(
        "--calibration",
        type=Path,
        help="calibration file; defaults to INPUT-calibration.toml",
    )
    parser.add_argument(
        "--profile",
        type=Path,
        help="build profile; defaults to INPUT-profile.toml",
    )
    args = parser.parse_args(argv)
    default_calibration, default_profile = default_paths(args.input)
    calibration_path = args.calibration or default_calibration
    profile_path = args.profile or default_profile

    try:
        paths = (
            args.input.resolve(),
            calibration_file.require_local_path(calibration_path),
            calibration_file.require_local_path(profile_path),
        )
        if len(set(paths)) != len(paths):
            parser.error("input, calibration, and profile paths must differ")
        source = args.input.read_bytes()
        extraction = extract(source, rom=args.rom, source_name=str(args.input))
        artifacts = {
            paths[1]: calibration_file.dumps(extraction.calibration).encode("utf-8")
        }
        if extraction.has_profile:
            artifacts[paths[2]] = profile_bytes(
                extraction, f"extracted-{args.input.stem}"
            )
        created = apply_map_switching._publish_artifacts(
            artifacts, paths[1], kind="calibration artifact"
        )
    except (
        OSError,
        ExtractionError,
        build_rom.BuildError,
        calibration_file.CalibrationFileError,
        apply_map_switching.PatchError,
    ) as error:
        parser.error(str(error))

    calibration = extraction.calibration
    source_state = " ".join(f"{key}={value}" for key, value in calibration.source[1:])
    print(f"rom={calibration.rom} source={args.input} source_sha256={calibration.source[0][1]}")
    print(f"source_runtime {source_state}")
    for path in artifacts:
        state = "created" if path in created else "already_exact"
        print(f"output={path} status={state}")
    print(
        f"calibration_elements={len(calibration.elements)} "
        f"calibration_bytes={sum(len(item.data) for item in calibration.elements)}"
    )
    if extraction.unexpressed:
        for component, record, schema_version, fields in extraction.unexpressed:
            print(
                f"{component} record={record} schema={schema_version} "
                f"is not expressible by profile schema "
                f"{build_rom.PROFILE_SCHEMA_VERSION}: {_format_fields(fields)}"
            )
        print("status=PARTIAL profile=not_written")
        return EXIT_SETTINGS_NOT_EXPRESSED
    if not extraction.has_profile:
        print(
            "status=PASS profile=not_written reason=source carries no "
            "Rolling Launch settings"
        )
        return 0
    print("status=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
