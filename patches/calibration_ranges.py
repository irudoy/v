"""Byte ranges that carry calibration between builds of one stock image.

The builder accepts calibration inside the compatible window of
``map_switching_layout``. Inside that window it owns or pins the ROM identity,
the component write sets, the checksum fields, and every byte that a layout
validates against its stock value: anchors, hook literals, the feedback CAN
record, erased regions, and runtime base records. The remaining window bytes
are calibration. The alternate map copies (Map 2 through Map 5) lie inside the
map write set and also carry calibration, so they are calibration ranges as
well. Rolling Launch and CAN telemetry configuration records are builder
write sets; their settings travel in a build profile, not as calibration. The
Rolling Launch efficiency table is a builder write set as well: the builder
derives it from the F table, which is calibration.
"""

from __future__ import annotations

from bisect import bisect_right
from dataclasses import dataclass
from functools import lru_cache
from itertools import chain

from patches import can_telemetry_compose
from patches import map_switching_compose
from patches import map_switching_layout
from patches import rolling_launch_compose
from patches import rom_checksums
from patches import runtime_targets


WINDOW_START = map_switching_layout.COMPATIBLE_CALIBRATION_START
WINDOW_END = map_switching_layout.COMPATIBLE_CALIBRATION_END
WINDOW_KEY = "calibration_window"


@dataclass(frozen=True)
class CalibrationRanges:
    rom: str
    window: tuple[map_switching_layout.AddressRange, ...]
    map_copies: tuple[map_switching_layout.AddressRange, ...]
    write_offsets: frozenset[int]
    checksum_offsets: frozenset[int]

    @property
    def ranges(self):
        return tuple(sorted(self.window + self.map_copies))

    def offsets(self):
        return frozenset(chain.from_iterable(
            range(item.start, item.end) for item in self.ranges
        ))

    def containing(self, offset):
        """Return the calibration range that holds ``offset``, or None."""
        ranges = self.ranges
        index = bisect_right([item.start for item in ranges], offset) - 1
        if index >= 0 and offset < ranges[index].end:
            return ranges[index]
        return None


def _offsets(spans):
    return frozenset(chain.from_iterable(
        range(start, start + size) for start, size in spans
    ))


def write_offsets(target):
    """Return every byte that the builder composes for ``target``."""
    ranges = map_switching_compose.composition_write_ranges(target.map_layout)
    if target.rolling_layout is not None:
        ranges += rolling_launch_compose.composition_write_ranges(
            target.rolling_layout
        )
    ranges += can_telemetry_compose.composition_write_ranges(
        target.telemetry_layout
    )
    return _offsets((item.start, item.size) for item in ranges)


def stock_pinned_offsets(target):
    """Return the bytes that the build layouts require to hold stock values."""
    map_layout = target.map_layout
    feedback = map_layout.feedback
    erased = map_switching_layout.erased_rom(map_layout)
    spans = [
        (
            map_switching_layout.COMPATIBLE_IDENTITY_START,
            map_switching_layout.COMPATIBLE_IDENTITY_END
            - map_switching_layout.COMPATIBLE_IDENTITY_START,
        ),
        (erased.start, erased.size),
        (feedback.config_record_address, 4),
        (feedback.serializer_payload_base_literal, 4),
    ]
    spans += [(item.address, item.width) for item in map_layout.anchors]
    spans += [(item.address, item.width) for item in map_layout.hooks]
    rolling = target.rolling_layout
    if rolling is not None:
        spans += [(item.start, item.size) for item in rolling.claimed_rom_ranges]
        spans += [(item.address, item.width) for item in rolling.hooks]
        spans += [(item.pointer_address, 4) for item in rolling.diagnostics]
    telemetry = target.telemetry_layout
    spans += [(item.span.start, item.span.size) for item in telemetry.assembly_units]
    spans += [
        (telemetry.configuration.start, telemetry.configuration.size),
        (telemetry.reserved_rom.start, telemetry.reserved_rom.size),
        (telemetry.mailbox_record_address, 4),
    ]
    spans += [(item.address, item.width) for item in telemetry.hooks]
    return _offsets(spans)


def _runs(offsets):
    runs = []
    for offset in sorted(offsets):
        if runs and runs[-1][1] == offset:
            runs[-1][1] = offset + 1
        else:
            runs.append([offset, offset + 1])
    return tuple(
        map_switching_layout.AddressRange(start, end, WINDOW_KEY)
        for start, end in runs
    )


def build_ranges(target):
    """Return the calibration ranges of one runtime target."""
    writes = write_offsets(target)
    checksums = rom_checksums.checksum_byte_offsets(target.checksum_layout)
    excluded = writes | checksums | stock_pinned_offsets(target)
    window = _runs(
        offset
        for offset in range(WINDOW_START, WINDOW_END)
        if offset not in excluded
    )
    map_copies = tuple(
        map_switching_layout.AddressRange(
            address, address + family.byte_length, f"{family.key}.map_{slot}"
        )
        for family in target.map_layout.families
        for slot, address in enumerate(family.copies, 2)
    )
    for item in map_copies:
        copy = range(item.start, item.end)
        if not writes.issuperset(copy) or not checksums.isdisjoint(copy):
            raise ValueError(
                f"{target.rom}: map copy {item.key} at {item.start:#x} is not "
                "a builder-owned calibration slot"
            )
    return CalibrationRanges(
        rom=target.rom,
        window=window,
        map_copies=tuple(sorted(map_copies)),
        write_offsets=writes,
        checksum_offsets=checksums,
    )


@lru_cache(maxsize=None)
def load(rom):
    """Return the calibration ranges of a registered ROM."""
    return build_ranges(runtime_targets.load_runtime_target(rom))
