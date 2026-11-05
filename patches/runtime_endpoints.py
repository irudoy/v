"""Classify the runtime layers of an image built from a registered stock image.

An image carries no runtime, the current builder runtime, or a registered
historical Rolling Launch endpoint under an optional current or registered
historical CAN telemetry layer. Each signature names the ROMs it describes, and
classification considers only the signatures of the selected ROM. A historical
Rolling Launch signature places its units, hooks, DID slots and record by its
own addresses. A historical CAN telemetry endpoint places its units, hooks,
record, reserve and mailbox record by its own addresses and decodes the record
under its frozen protocol. A change of the current layouts or protocol leaves
both classifications intact. Partial, unknown, or mixed layers are rejected
with a named reason.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import struct

from patches import can_telemetry
from patches import can_telemetry_history
from patches import jk08a_checksums as canonical_checksums
from patches import map_switching_compose
from patches import map_switching_layout
from patches import rolling_launch
from patches import rom_checksums
from patches import runtime_targets


class EndpointError(ValueError):
    """Raised when an image holds a partial or unknown runtime state."""


def sha256(data):
    return hashlib.sha256(bytes(data)).hexdigest()


@dataclass(frozen=True)
class EndpointAddresses:
    """The ROM placement of one generation of historical runtimes: the span
    of each unit, the word of each hook, the pointer slot and RAM target of
    each DID, and the record span of each configuration schema. It is a
    record of the images that the generation built and does not follow the
    current layout."""

    unit_spans: tuple[tuple[str, int, int], ...]
    hook_words: tuple[tuple[str, int, int], ...]
    did_slots: tuple[tuple[int, int, int], ...]
    record_spans: tuple[tuple[int, int, int], ...]
    byte_order: str = "big"


# The placement of every registered exact-family endpoint: the unit spans,
# hook words, DID pointer slots and record spans of the builder through the
# per-map slot runtime.
EXACT_ENDPOINT_ADDRESSES = EndpointAddresses(
    unit_spans=(
        ("wrappers", 0x000D3860, 0x000D38E4),
        ("engine", 0x000D38E4, 0x000D3EA0),
        ("ignition_adapter", 0x000D3EA0, 0x000D3F60),
        ("speed_controller", 0x000D40C0, 0x000D41E0),
        ("feedback_arbiter", 0x000D41E0, 0x000D4280),
        ("fuel_cut_wrapper", 0x000D6000, 0x000D6040),
        ("rpm_ceiling", 0x000D6068, 0x000D60C0),
        ("spark_cut", 0x000D60C0, 0x000D6220),
        ("trim", 0x000D6268, 0x000D6320),
    ),
    hook_words=(
        ("displaced_periodic_task", 0x00021970, 4),
        ("selector_arbitration", 0x000CE8DC, 4),
        ("startup_state_clear", 0x00027D28, 4),
        ("primary_ignition_command", 0x0004E198, 4),
        ("feedback_arbitration", 0x000C3FA4, 4),
        ("fuel_cut_coordinator", 0x000219DC, 4),
        ("spark_handler", 0x000202E4, 4),
    ),
    did_slots=(
        (0x1211, 0x000228E0, 0xFFFF5D40),
        (0x1212, 0x000228E4, 0xFFFF5D42),
        (0x1213, 0x000228E8, 0xFFFF5D44),
        (0x1216, 0x000228F4, 0xFFFF5D46),
        (0x1217, 0x000228F8, 0xFFFF5D48),
        (0x1224, 0x0002292C, 0xFFFF5D4A),
        (0x1227, 0x00022938, 0xFFFF5D4C),
        (0x1228, 0x0002293C, 0xFFFF5D4E),
        (0x1229, 0x00022940, 0xFFFF5D50),
        (0x121D, 0x00022910, 0xFFFF5D52),
        (0x121E, 0x00022914, 0xFFFF5D54),
        (0x121F, 0x00022918, 0xFFFF5D56),
        (0x1231, 0x00022960, 0xFFFF5D58),
        (0x1232, 0x00022964, 0xFFFF5D5C),
    ),
    record_spans=(
        (1, 0x000D3F60, 32),
        (2, 0x000D3F60, 32),
        (3, 0x000D3F60, 32),
        (4, 0x000D6040, 40),
        (5, 0x000D6220, 72),
    ),
)


@dataclass(frozen=True)
class EndpointUnit:
    key: str
    start: int
    end: int
    sha256: str


@dataclass(frozen=True)
class EndpointHook:
    key: str
    address: int
    width: int
    value: int


@dataclass(frozen=True)
class EndpointDid:
    did: int
    pointer_address: int
    target: int


@dataclass(frozen=True)
class RollingEndpointSignature:
    """One historical Rolling Launch endpoint: the digest of each unit, the
    value of each hook, the published DIDs and the record schema, placed by
    the endpoint's own addresses."""

    key: str
    roms: tuple[str, ...]
    configuration_schema_version: int
    unit_sha256: tuple[tuple[str, str], ...]
    hook_values: tuple[tuple[str, int], ...]
    carries_current_telemetry: bool = False
    # The Rolling Launch DIDs that the endpoint publishes; None names the
    # nine DIDs of every endpoint before the RPM ceiling.
    published_dids: frozenset[int] | None = None
    addresses: EndpointAddresses = EXACT_ENDPOINT_ADDRESSES

    @property
    def units(self):
        spans = {key: (start, end) for key, start, end in self.addresses.unit_spans}
        return tuple(
            EndpointUnit(key, *spans[key], digest)
            for key, digest in self.unit_sha256
        )

    @property
    def hooks(self):
        words = {key: (address, width) for key, address, width in self.addresses.hook_words}
        return tuple(
            EndpointHook(key, *words[key], value)
            for key, value in self.hook_values
        )

    @property
    def dids(self):
        published = (
            HISTORICAL_ROLLING_DIDS if self.published_dids is None
            else self.published_dids
        )
        return tuple(
            EndpointDid(did, pointer, target)
            for did, pointer, target in self.addresses.did_slots
            if did in published
        )

    @property
    def record(self):
        """Return the span of the endpoint's configuration record."""
        for schema, start, size in self.addresses.record_spans:
            if schema == self.configuration_schema_version:
                return map_switching_layout.AddressRange(
                    start, start + size, f"{self.key}.configuration"
                )
        raise EndpointError(
            f"internal historical Rolling Launch endpoint {self.key!r} "
            "has no record span"
        )

    def write_ranges(self):
        """Return every span that the endpoint writes or keeps erased."""
        ranges = [
            map_switching_layout.AddressRange(unit.start, unit.end, f"unit.{unit.key}")
            for unit in self.units
        ]
        ranges += [
            map_switching_layout.AddressRange(
                hook.address, hook.address + hook.width, f"hook.{hook.key}"
            )
            for hook in self.hooks
        ]
        ranges += [
            map_switching_layout.AddressRange(
                item.pointer_address, item.pointer_address + 4, f"did.{item.did:04x}"
            )
            for item in self.dids
        ]
        ranges.append(self.record)
        return tuple(sorted(ranges, key=lambda item: (item.start, item.end)))

    def write_offsets(self):
        return frozenset(
            offset
            for item in self.write_ranges()
            for offset in range(item.start, item.end)
        )


PRE_FEEDBACK_ROLLING_HOOK_VALUES = (
    ("displaced_periodic_task", 0x000D3860),
    ("selector_arbitration", 0x000D3880),
    ("startup_state_clear", 0x000D38A0),
    ("primary_ignition_command", 0x000D3EA0),
    ("feedback_arbitration", 0x000D35E0),
    ("fuel_cut_coordinator", 0x0004ED88),
    ("spark_handler", 0x0002AB24),
)
# The hooks of the endpoints that hold RPM through the fuel-cut shadow: the
# arbiter dashboard hook is installed and the fuel-cut coordinator is stock.
FUEL_SHADOW_ROLLING_HOOK_VALUES = (
    ("displaced_periodic_task", 0x000D3860),
    ("selector_arbitration", 0x000D3880),
    ("startup_state_clear", 0x000D38A0),
    ("primary_ignition_command", 0x000D3EA0),
    ("feedback_arbitration", 0x000D41E0),
    ("fuel_cut_coordinator", 0x0004ED88),
    ("spark_handler", 0x0002AB24),
)
# The hooks of the endpoints that hold through the fuel-cut coordinator
# wrapper, which the current runtime keeps. Every historical endpoint leaves
# the GR11A spark vector at the stock handler.
FUEL_CUT_WRAPPER_ROLLING_HOOK_VALUES = (
    ("displaced_periodic_task", 0x000D3860),
    ("selector_arbitration", 0x000D3880),
    ("startup_state_clear", 0x000D38A0),
    ("primary_ignition_command", 0x000D3EA0),
    ("feedback_arbitration", 0x000D41E0),
    ("fuel_cut_coordinator", 0x000D6000),
    ("spark_handler", 0x0002AB24),
)
ERASED_FEEDBACK_ARBITER_SHA256 = (
    "0052516839b94ee314a4e3b398c8036de3790d672194987a394ee60323848539"
)
ERASED_FUEL_CUT_WRAPPER_SHA256 = (
    "8667e718294e9e0df1d30600ba3eeb201f764aad2dad72748643e4a285e1d1f7"
)
# Every historical endpoint leaves the RPM-ceiling span 0xD6068..0xD60C0
# erased: 88 bytes of 0xFF.
ERASED_RPM_CEILING_SHA256 = (
    "fc351643198ac4ec4e78649c99ad06b4cd45b554005990cdc70e520b49dd9bf0"
)
# Every historical endpoint leaves the spark-cut span 0xD60C0..0xD6220
# erased: 352 bytes of 0xFF.
ERASED_SPARK_CUT_SHA256 = (
    "a8aa961e3bbac0826d6d3fabce5dee4889e5c218e4b1216908e66bc53264d89a"
)
# Every historical endpoint leaves the trim span 0xD6268..0xD6320 erased:
# 184 bytes of 0xFF.
ERASED_TRIM_SHA256 = (
    "ba151f705f188cd9fcab95d6d24c0da135a4f334778b139684f38b8b4fbe728f"
)
# The hooks of the schema 4 endpoint, which installs every current hook.
SPARK_CUT_ROLLING_HOOK_VALUES = (
    ("displaced_periodic_task", 0x000D3860),
    ("selector_arbitration", 0x000D3880),
    ("startup_state_clear", 0x000D38A0),
    ("primary_ignition_command", 0x000D3EA0),
    ("feedback_arbitration", 0x000D41E0),
    ("fuel_cut_coordinator", 0x000D6000),
    ("spark_handler", 0x000D60C0),
)
# The speed-controller span 0xD40C0..0xD41E0 joins the former ignition
# controller span 0xD40C0..0xD4140 and the former threshold-helper span
# 0xD4140..0xD41E0, so each historical digest covers both former units.
# Erased controller and helper: 288 bytes of 0xFF.
ERASED_SPEED_CONTROLLER_SHA256 = (
    "c49fd3b652e068233b78f7300696e2201ddf3932072b8b303de297e7d0354827"
)
# The schema-2 band controller with an erased helper.
SCHEMA_2_SPEED_CONTROLLER_SHA256 = (
    "60ddce862b8f857b382d55ccb64a492d48321a81cf4de834af78b60c591106d9"
)
# The guarded schema-3 controller with the threshold helper.
GUARDED_SPEED_CONTROLLER_SHA256 = (
    "c66f18ba5f3f26bece4ba2ce3973292e1b613c26e1ba465abb301dd0c14203f8"
)
# The bounded schema-3 controller with the threshold helper.
BOUNDED_SPEED_CONTROLLER_SHA256 = (
    "0b0cede4221a03624990ba79d9df1ca827b947f29da705f14c3b702158a5a9b3"
)
# Every endpoint before the RPM ceiling publishes these nine DIDs and leaves
# the later Rolling Launch DID slots stock.
HISTORICAL_ROLLING_DIDS = frozenset(
    {0x1211, 0x1212, 0x1213, 0x1216, 0x1217, 0x1224, 0x1227, 0x1228, 0x1229}
)
# The fourteen DIDs of the spark-cut endpoints.
SPARK_CUT_ROLLING_DIDS = frozenset({
    0x1211, 0x1212, 0x1213, 0x1216, 0x1217, 0x1224, 0x1227, 0x1228,
    0x1229, 0x121D, 0x121E, 0x121F, 0x1231, 0x1232,
})
# Mode names of configuration schemas 1 to 3.
HISTORICAL_MODE_NAMES = ("observe", "rpm_hold", "rpm_hold_retard")
# Wrapper and engine bytes of every endpoint that holds RPM through the
# fuel-cut shadow and clears a 20-byte state.
FUEL_SHADOW_WRAPPERS_SHA256 = (
    "7e650ae06bbfdd33f9da9b99488de8202de64160440bced19719a07c74881e45"
)


# Exact code fingerprints of registered historical Rolling Launch endpoints.
# Each signature names the ROMs whose layout it describes. Configuration bytes
# remain calibration-specific and are validated against the record contract.
HISTORICAL_ROLLING_ENDPOINTS = (
    RollingEndpointSignature(
        key="schema-1-bandless",
        roms=runtime_targets.EXACT_ROMS,
        configuration_schema_version=1,
        unit_sha256=(
            ("wrappers", FUEL_SHADOW_WRAPPERS_SHA256),
            (
                "engine",
                "599c859dffe2f2b88eefa0c2add63ceecf3232a08625b1acc2481bd9c4658673",
            ),
            (
                "ignition_adapter",
                "542aab5999c39903c6614daa4b44ca41a77fe37273ee57dc2c4390e53844311d",
            ),
            ("speed_controller", ERASED_SPEED_CONTROLLER_SHA256),
            ("feedback_arbiter", ERASED_FEEDBACK_ARBITER_SHA256),
            ("fuel_cut_wrapper", ERASED_FUEL_CUT_WRAPPER_SHA256),
            ("rpm_ceiling", ERASED_RPM_CEILING_SHA256),
            ("spark_cut", ERASED_SPARK_CUT_SHA256),
            ("trim", ERASED_TRIM_SHA256),
        ),
        hook_values=PRE_FEEDBACK_ROLLING_HOOK_VALUES,
    ),
    RollingEndpointSignature(
        key="schema-2-speed-required",
        roms=runtime_targets.EXACT_ROMS,
        configuration_schema_version=2,
        unit_sha256=(
            ("wrappers", FUEL_SHADOW_WRAPPERS_SHA256),
            (
                "engine",
                "6fbe61494983b09c45565b02409f1d768c1633cbe3c088d6e378d10c0ed9d3c6",
            ),
            (
                "ignition_adapter",
                "82452974b158d34cc8d7c69b990f327428ff01f92e047c6a15cb2f9251e90952",
            ),
            ("speed_controller", SCHEMA_2_SPEED_CONTROLLER_SHA256),
            ("feedback_arbiter", ERASED_FEEDBACK_ARBITER_SHA256),
            ("fuel_cut_wrapper", ERASED_FUEL_CUT_WRAPPER_SHA256),
            ("rpm_ceiling", ERASED_RPM_CEILING_SHA256),
            ("spark_cut", ERASED_SPARK_CUT_SHA256),
            ("trim", ERASED_TRIM_SHA256),
        ),
        hook_values=PRE_FEEDBACK_ROLLING_HOOK_VALUES,
    ),
    RollingEndpointSignature(
        key="schema-2-zero-speed",
        roms=runtime_targets.EXACT_ROMS,
        configuration_schema_version=2,
        unit_sha256=(
            ("wrappers", FUEL_SHADOW_WRAPPERS_SHA256),
            (
                "engine",
                "e7e940b866526ea9feeab044f072fdee1ce157de600dd61482fbbe2905203661",
            ),
            (
                "ignition_adapter",
                "82452974b158d34cc8d7c69b990f327428ff01f92e047c6a15cb2f9251e90952",
            ),
            ("speed_controller", SCHEMA_2_SPEED_CONTROLLER_SHA256),
            ("feedback_arbiter", ERASED_FEEDBACK_ARBITER_SHA256),
            ("fuel_cut_wrapper", ERASED_FUEL_CUT_WRAPPER_SHA256),
            ("rpm_ceiling", ERASED_RPM_CEILING_SHA256),
            ("spark_cut", ERASED_SPARK_CUT_SHA256),
            ("trim", ERASED_TRIM_SHA256),
        ),
        hook_values=PRE_FEEDBACK_ROLLING_HOOK_VALUES,
    ),
    RollingEndpointSignature(
        key="schema-3-pre-feedback-indicators",
        roms=runtime_targets.EXACT_ROMS,
        configuration_schema_version=3,
        unit_sha256=(
            ("wrappers", FUEL_SHADOW_WRAPPERS_SHA256),
            (
                "engine",
                "6420e4f75b36a1ac86691f2d16952c235862db62b57d297a51b8efc0f3379729",
            ),
            (
                "ignition_adapter",
                "ed76618204bb4f3838f806e090d45882409ad1fb0aa9462ae91d531806d9ca7b",
            ),
            ("speed_controller", GUARDED_SPEED_CONTROLLER_SHA256),
            ("feedback_arbiter", ERASED_FEEDBACK_ARBITER_SHA256),
            ("fuel_cut_wrapper", ERASED_FUEL_CUT_WRAPPER_SHA256),
            ("rpm_ceiling", ERASED_RPM_CEILING_SHA256),
            ("spark_cut", ERASED_SPARK_CUT_SHA256),
            ("trim", ERASED_TRIM_SHA256),
        ),
        hook_values=PRE_FEEDBACK_ROLLING_HOOK_VALUES,
    ),
    # The arbiter of this endpoint emits ASCD state 6 for a failed held attempt
    # and state 7 for ACTIVE. It pairs that arbiter with the guarded ignition
    # controller and the schema-3 hooks. The CAN telemetry layer is compatible
    # with this complete registered lower endpoint.
    RollingEndpointSignature(
        key="schema-3-state-6-7-indicators",
        roms=runtime_targets.EXACT_ROMS,
        configuration_schema_version=3,
        unit_sha256=(
            ("wrappers", FUEL_SHADOW_WRAPPERS_SHA256),
            (
                "engine",
                "6420e4f75b36a1ac86691f2d16952c235862db62b57d297a51b8efc0f3379729",
            ),
            (
                "ignition_adapter",
                "ed76618204bb4f3838f806e090d45882409ad1fb0aa9462ae91d531806d9ca7b",
            ),
            ("speed_controller", GUARDED_SPEED_CONTROLLER_SHA256),
            (
                "feedback_arbiter",
                "0ec18b26a0ef6556bcb5f6056a2a9b988f8c895f65ec6b2b3665352ce73fb4dc",
            ),
            ("fuel_cut_wrapper", ERASED_FUEL_CUT_WRAPPER_SHA256),
            ("rpm_ceiling", ERASED_RPM_CEILING_SHA256),
            ("spark_cut", ERASED_SPARK_CUT_SHA256),
            ("trim", ERASED_TRIM_SHA256),
        ),
        hook_values=FUEL_SHADOW_ROLLING_HOOK_VALUES,
        carries_current_telemetry=True,
    ),
    RollingEndpointSignature(
        key="schema-3-guarded-controller",
        roms=runtime_targets.EXACT_ROMS,
        configuration_schema_version=3,
        unit_sha256=(
            ("wrappers", FUEL_SHADOW_WRAPPERS_SHA256),
            ("engine", "6420e4f75b36a1ac86691f2d16952c235862db62b57d297a51b8efc0f3379729"),
            ("ignition_adapter", "ed76618204bb4f3838f806e090d45882409ad1fb0aa9462ae91d531806d9ca7b"),
            ("speed_controller", GUARDED_SPEED_CONTROLLER_SHA256),
            ("feedback_arbiter", "1e1a884eee649ec5cfea48af0c2129c8290628401d11118253c5265e965b0da6"),
            ("fuel_cut_wrapper", ERASED_FUEL_CUT_WRAPPER_SHA256),
            ("rpm_ceiling", ERASED_RPM_CEILING_SHA256),
            ("spark_cut", ERASED_SPARK_CUT_SHA256),
            ("trim", ERASED_TRIM_SHA256),
        ),
        hook_values=FUEL_SHADOW_ROLLING_HOOK_VALUES,
        carries_current_telemetry=True,
    ),
    # The last endpoint that holds RPM through the fuel-cut shadow, before the
    # fuel-cut coordinator wrapper and the 24-byte state.
    RollingEndpointSignature(
        key="schema-3-fuel-shadow-hold",
        roms=runtime_targets.EXACT_ROMS,
        configuration_schema_version=3,
        unit_sha256=(
            ("wrappers", FUEL_SHADOW_WRAPPERS_SHA256),
            ("engine", "6420e4f75b36a1ac86691f2d16952c235862db62b57d297a51b8efc0f3379729"),
            ("ignition_adapter", "ed76618204bb4f3838f806e090d45882409ad1fb0aa9462ae91d531806d9ca7b"),
            ("speed_controller", BOUNDED_SPEED_CONTROLLER_SHA256),
            ("feedback_arbiter", "1e1a884eee649ec5cfea48af0c2129c8290628401d11118253c5265e965b0da6"),
            ("fuel_cut_wrapper", ERASED_FUEL_CUT_WRAPPER_SHA256),
            ("rpm_ceiling", ERASED_RPM_CEILING_SHA256),
            ("spark_cut", ERASED_SPARK_CUT_SHA256),
            ("trim", ERASED_TRIM_SHA256),
        ),
        hook_values=FUEL_SHADOW_ROLLING_HOOK_VALUES,
        carries_current_telemetry=True,
    ),
    # The last RPM-hold endpoint: the fuel-cut coordinator wrapper ORs the
    # request into the final cylinder mask, and the state has 24 bytes.
    RollingEndpointSignature(
        key="schema-3-fuel-cut-wrapper",
        roms=runtime_targets.EXACT_ROMS,
        configuration_schema_version=3,
        unit_sha256=(
            ("wrappers", "348049909aac6c5370fc7c91558cc1319e3b9edd4840927e82833aaeaa594155"),
            ("engine", "c5cf1751362ee50a8e3962ee0d70041a776659e17b8c2bc1c230d1bc1c922db6"),
            ("ignition_adapter", "ed76618204bb4f3838f806e090d45882409ad1fb0aa9462ae91d531806d9ca7b"),
            ("speed_controller", BOUNDED_SPEED_CONTROLLER_SHA256),
            ("feedback_arbiter", "1e1a884eee649ec5cfea48af0c2129c8290628401d11118253c5265e965b0da6"),
            ("fuel_cut_wrapper", "7f0911a9b534511fbf5dfc3957cfba5fb5cab04a5daaa8fa0832deffb7e86abd"),
            ("rpm_ceiling", ERASED_RPM_CEILING_SHA256),
            ("spark_cut", ERASED_SPARK_CUT_SHA256),
            ("trim", ERASED_TRIM_SHA256),
        ),
        hook_values=FUEL_CUT_WRAPPER_ROLLING_HOOK_VALUES,
        carries_current_telemetry=True,
    ),
    # The speed hold with the spark-cut actuator and one integral gain: the
    # 40-byte schema 4 record at 0xD6040 and the hooks and DIDs of the spark cut.
    RollingEndpointSignature(
        key="schema-4-uniform-gain",
        roms=runtime_targets.EXACT_ROMS,
        configuration_schema_version=4,
        unit_sha256=(
            ("wrappers", "11232a674dcb39fcbe03354e2e6e3ae91e23bed27706c6b48db6e52ce95b3cf8"),
            ("engine", "7108080044c54a4eded9313657ce39af4729f5924beb3baa2380322274dd5e76"),
            ("ignition_adapter", "66b1f07d71af484080746829ccb0f8a2a3b6513b6e4f1a87b1dc38c3c3d44c8a"),
            ("speed_controller", "52d1a9ef8a671b731ff5c8fa3c86ae42a9ccf2d898e9a8d286e567dfb9793ef8"),
            ("feedback_arbiter", "1e1a884eee649ec5cfea48af0c2129c8290628401d11118253c5265e965b0da6"),
            ("fuel_cut_wrapper", "7f0911a9b534511fbf5dfc3957cfba5fb5cab04a5daaa8fa0832deffb7e86abd"),
            ("rpm_ceiling", "5de36173709c7fd3880724eb9f13474f1b515ba725869205a7f48eeeb4c2c2dd"),
            ("spark_cut", "94127a113032ff40012973e8ddd3bb368bf36029ba806460b328848c2ef19743"),
            ("trim", ERASED_TRIM_SHA256),
        ),
        hook_values=SPARK_CUT_ROLLING_HOOK_VALUES,
        carries_current_telemetry=True,
        published_dids=SPARK_CUT_ROLLING_DIDS,
    ),
    # The speed hold with per-map slots and the fixed retard trim: the 72-byte
    # schema 5 record at 0xD6220, the fuel-cut wrapper and the RPM ceiling, as
    # flashed on JK08A.
    RollingEndpointSignature(
        key="schema-5-fixed-trim",
        roms=("JK08A",),
        configuration_schema_version=5,
        unit_sha256=(
            ("wrappers", "11232a674dcb39fcbe03354e2e6e3ae91e23bed27706c6b48db6e52ce95b3cf8"),
            ("engine", "3c5a576220a3ca2695ee0d4655044f2e5373a56cf01a5539e121242e666df399"),
            ("ignition_adapter", "da55e2ccb8801d14dba33e4d7ea17e2a13eb1b2f4fe229ef62caffbe2770d1f6"),
            ("speed_controller", "7e08454cb05803d5c18ee4d69a501bc43bde0ae8b60164a97cdfd4d83cacecb5"),
            ("feedback_arbiter", "1e1a884eee649ec5cfea48af0c2129c8290628401d11118253c5265e965b0da6"),
            ("fuel_cut_wrapper", "7f0911a9b534511fbf5dfc3957cfba5fb5cab04a5daaa8fa0832deffb7e86abd"),
            ("rpm_ceiling", "5de36173709c7fd3880724eb9f13474f1b515ba725869205a7f48eeeb4c2c2dd"),
            ("spark_cut", "30e69c6ac042bc21354fbf0f83a6ce7231bb58aab75fd5d654076e7f44ad181e"),
            ("trim", "e01b86a6a7aea6d8f359e1c92caf342466faf821b714998de49659c33e3d823d"),
        ),
        hook_values=SPARK_CUT_ROLLING_HOOK_VALUES,
        carries_current_telemetry=True,
        published_dids=SPARK_CUT_ROLLING_DIDS,
    ),
)
TELEMETRY_LOWER_ROLLING_STATES = frozenset(
    {"current"}
    | {
        endpoint.key
        for endpoint in HISTORICAL_ROLLING_ENDPOINTS
        if endpoint.carries_current_telemetry
    }
)

HISTORICAL_FEEDBACK_FRAME_COUNTS = ((10, 10), (15, 15))
# Exact JK08A engine fingerprints that emit ASCD state 6 during the ON phase:
# the partial 0x9F mask and the full 0x8F mask, each with 10/10, 15/15, and
# 30/30 phase counts.
HISTORICAL_FEEDBACK_ENGINE_SHA256 = frozenset(
    {
        "925a7ebc321e965bfed0fdfdc7e06287b6b794b0525226c4bd9a11187bc1f66f",
        "22c9c42f228cd827610a7e5ef848942e219e0461cbd2c9ba362ca8817130435f",
        "22c69075abb5f0c48207eb3c14a8c538f0fc17cf14f79951d55799186fc1a448",
        "0e0501f3d91e18a17c6a9bf7c4ebd187809c094fbf701f9d2864fd4792f9b32e",
        "017a1c01d0f2fba835a93714d1ce9e20a07e5ff709fc41ed997bf92e7124a13a",
        "d64600dd5be497cf49df077956e2ac86159b0366ecc485b33c5633e146b4e66a",
    }
)


def read_integer(data, address, width, byte_order="big"):
    return int.from_bytes(data[address : address + width], byte_order)


def _expected_pointer_table(layout, family):
    return b"".join(
        address.to_bytes(4, layout.byte_order)
        for address in family.all_slot_addresses
    )


HISTORICAL_SCHEMA_FORMATS = {
    1: ">H8B6H5sBHH",
    2: ">H8B6H5sBHH",
    3: ">H8B3H2B2H5sBHH",
}
# The 40-byte head of the schema 4 and 5 records. The word at +0x16 holds the
# integral gain of schema 4 and a reserved zero of schema 5, whose five
# 6-byte map slots and end marker follow the head.
SPEED_HOLD_HEAD_FORMAT = ">H6B4HhBB3H2B3H2B2H"
SPEED_HOLD_HEAD_FIELDS = (
    "magic", "schema_version", "mode", "enable_mask", "options",
    "coolant_min", "coolant_max", "min_speed", "max_speed", "min_rpm_native",
    "min_pedal", "target_speed_offset", "window_width", "window_top",
    "u_rate_limit", "gain_word", "integrator_limit", "abort_above",
    "abort_below", "rpm_ceiling_offset_native", "run_timeout_ticks",
    "rearm_ticks", "speed_frame_age_limit", "rpm_ceiling_hysteresis_native",
    "magic_inverse", "end_marker",
)
SPEED_HOLD_SLOT_FORMAT = "hBBH"
SPEED_HOLD_SLOT_FIELDS = (
    "integral_gain", "max_trim", "floor_command", "trim_efficiency",
)
SPEED_HOLD_SLOT_COUNT = 5
SPEED_HOLD_SCHEMA_FORMATS = {
    4: SPEED_HOLD_HEAD_FORMAT,
    5: SPEED_HOLD_HEAD_FORMAT
    + SPEED_HOLD_SLOT_FORMAT * SPEED_HOLD_SLOT_COUNT + "H",
}
# Mode names and limits of the schema 4 and 5 records.
SPEED_HOLD_MODE_NAMES = ("observe", "hold")
SPEED_HOLD_TRIM_MAX = 40
SPEED_HOLD_U_ONE = 1000
SPEED_HOLD_FRAME_AGE_LIMIT_MAX = 254


def _speed_hold_fields(configuration, schema_version):
    """Return the named values of a schema 4 or 5 record, or None when its
    size or format differs."""
    try:
        values = struct.unpack(
            SPEED_HOLD_SCHEMA_FORMATS[schema_version], bytes(configuration)
        )
    except (TypeError, struct.error):
        return None
    head = dict(zip(SPEED_HOLD_HEAD_FIELDS, values))
    if schema_version == 4:
        return head, ()
    slot_size = len(SPEED_HOLD_SLOT_FIELDS)
    slots = tuple(
        dict(zip(SPEED_HOLD_SLOT_FIELDS, values[start : start + slot_size]))
        for start in range(
            len(SPEED_HOLD_HEAD_FIELDS),
            len(SPEED_HOLD_HEAD_FIELDS) + slot_size * SPEED_HOLD_SLOT_COUNT,
            slot_size,
        )
    )
    head["slot_end_marker"] = values[-1]
    return head, slots


def _speed_hold_record_is_valid(configuration, schema_version):
    parsed = _speed_hold_fields(configuration, schema_version)
    if parsed is None:
        return False
    head, slots = parsed
    gain_word = (
        0 <= head["gain_word"] <= 0x7FFF if schema_version == 4
        else head["gain_word"] == 0
    )
    common = all((
        head["magic"] == rolling_launch.CONFIG_MAGIC,
        head["schema_version"] == schema_version,
        0 <= head["mode"] < len(SPEED_HOLD_MODE_NAMES),
        0 <= head["enable_mask"] <= 0x1F,
        head["options"] == 0,
        0 <= head["coolant_min"] <= head["coolant_max"] <= 0xFF,
        head["min_speed"] == 0
        or head["max_speed"] == 0
        or head["min_speed"] <= head["max_speed"],
        0 < head["min_rpm_native"] <= 0xFFFF,
        0 < head["abort_above"] <= 0xFF,
        0 < head["abort_below"] <= 0xFF,
        -head["abort_above"] < head["target_speed_offset"] < head["abort_below"],
        0 < head["window_width"] <= 0xFF,
        0 < head["u_rate_limit"] <= SPEED_HOLD_U_ONE,
        gain_word,
        0 <= head["integrator_limit"] <= SPEED_HOLD_U_ONE,
        0 < head["rpm_ceiling_offset_native"] <= 0xFFFF,
        0 < head["run_timeout_ticks"] <= 0x7FFF,
        0 < head["rearm_ticks"] <= 0x7FFF,
        0 < head["speed_frame_age_limit"] <= SPEED_HOLD_FRAME_AGE_LIMIT_MAX,
        0 < head["rpm_ceiling_hysteresis_native"]
        <= min(0xFF, head["rpm_ceiling_offset_native"]),
        head["magic_inverse"] == rolling_launch.CONFIG_MAGIC_INVERSE,
        head["end_marker"] == rolling_launch.CONFIG_END_MARKER,
    ))
    if schema_version == 4:
        return common
    return common and head["slot_end_marker"] == rolling_launch.CONFIG_END_MARKER and all(
        0 <= slot["integral_gain"] <= 0x7FFF
        and 0 <= slot["max_trim"] <= SPEED_HOLD_TRIM_MAX
        and 0 < slot["trim_efficiency"] <= SPEED_HOLD_U_ONE
        and (slot["max_trim"] != 0 or slot["trim_efficiency"] == SPEED_HOLD_U_ONE)
        for slot in slots
    )


def historical_configuration_fields(configuration, schema_version):
    """Return the named settings of a valid historical Rolling Launch record,
    which the current profile schema cannot express."""
    if not historical_configuration_is_valid(configuration, schema_version):
        raise EndpointError(
            f"no valid schema {schema_version} Rolling Launch record"
        )
    if schema_version in SPEED_HOLD_SCHEMA_FORMATS:
        head, slots = _speed_hold_fields(configuration, schema_version)
        fields = {
            name: value for name, value in head.items()
            if name not in (
                "magic", "schema_version", "magic_inverse", "end_marker",
                "slot_end_marker", "options", "gain_word",
            )
        }
        fields["mode"] = SPEED_HOLD_MODE_NAMES[head["mode"]]
        if schema_version == 4:
            fields["integral_gain"] = head["gain_word"]
        else:
            fields["slots"] = slots
        return fields
    values = struct.unpack(
        HISTORICAL_SCHEMA_FORMATS[schema_version], bytes(configuration)
    )
    fields = {
        "mode": HISTORICAL_MODE_NAMES[values[2]],
        "enable_mask": values[3],
        "coolant_min": values[5],
        "coolant_max": values[6],
        "min_speed": values[7],
    }
    if schema_version == 3:
        fields.update({
            "retard_ramp_native": values[8],
            "min_rpm_native": values[9],
            "min_pedal": values[10],
            "rpm_offset_native": values[11],
            "min_hysteresis_native": values[12],
            "max_hysteresis_native": values[13],
            "run_timeout_ticks": values[14],
            "rearm_ticks": values[15],
            "target_commands": tuple(values[16]),
            "hysteresis_ratio_tenths": values[17],
        })
        return fields
    fields.update({
        ("speed_padding" if schema_version == 1 else "retard_ramp_native"): (
            values[8]
        ),
        "min_rpm_native": values[9],
        "min_pedal": values[10],
        "rpm_offset_native": values[11],
        "hysteresis_native": values[12],
        "run_timeout_ticks": values[13],
        "rearm_ticks": values[14],
        "target_commands": tuple(values[15]),
    })
    return fields


def historical_configuration_is_valid(configuration, schema_version):
    """Check a historical record against the contract of its schema."""
    if schema_version in SPEED_HOLD_SCHEMA_FORMATS:
        return _speed_hold_record_is_valid(configuration, schema_version)
    if schema_version not in HISTORICAL_SCHEMA_FORMATS:
        raise EndpointError(
            "internal historical Rolling Launch schema is unsupported"
        )
    try:
        values = struct.unpack(
            HISTORICAL_SCHEMA_FORMATS[schema_version], bytes(configuration)
        )
        options = rolling_launch.Option(values[4])
    except (TypeError, ValueError, struct.error):
        return False
    common = all((
        values[0] == rolling_launch.CONFIG_MAGIC,
        values[1] == schema_version,
        0 <= values[2] < len(HISTORICAL_MODE_NAMES),
        0 <= values[3] <= 0x1F,
        options == rolling_launch.Option.NONE,
        0 <= values[5] <= values[6] <= 0xFF,
        0 < values[9] <= 0xFFFF,
        values[-2] == rolling_launch.CONFIG_MAGIC_INVERSE,
        values[-1] == rolling_launch.CONFIG_END_MARKER,
    ))
    if schema_version == 3:
        return all((
            common,
            0 < values[8] <= 0xFF,
            0 < values[11] <= 0xFFFF,
            0 < values[12] <= values[13] <= 0xFF,
            values[13] < values[11],
            values[8] <= values[11],
            0 < values[14] <= 0x7FFF,
            0 < values[15] <= 0x7FFF,
            len(values[16]) == rolling_launch.SLOT_COUNT,
            all(110 <= value <= 117 for value in values[16]),
            0 < values[17] <= 0xFF,
        ))
    common = all((
        common,
        0 < values[11] <= 0xFFFF,
        0 < values[12] < values[9],
        0 < values[13] <= 0x7FFF,
        0 < values[14] <= 0x7FFF,
        len(values[15]) == rolling_launch.SLOT_COUNT,
        all(110 <= value <= 117 for value in values[15]),
        values[16] == 0,
    ))
    if schema_version == 1:
        return common and 0 < values[7] <= 0xFF and values[8] == 0
    return all((
        common,
        0 <= values[7] <= 0xFF,
        0 < values[8] <= 0xFF,
        values[12] < values[8] <= values[11],
    ))


def configuration_record(source, layout, state):
    """Return the Rolling Launch record of an endpoint state: the current
    record, or the record in the span of a historical endpoint."""
    if state == "current":
        span = layout.configuration
    else:
        span = historical_endpoint(state).record
    return bytes(source[span.start : span.end])


def historical_endpoint(key):
    """Return the registered historical Rolling Launch endpoint of a key."""
    for endpoint in HISTORICAL_ROLLING_ENDPOINTS:
        if endpoint.key == key:
            return endpoint
    raise EndpointError(f"unknown historical Rolling Launch endpoint {key!r}")


def _erased(source, span):
    return source[span.start : span.end] == bytes([0xFF]) * span.size


def require_valid_signature(endpoint):
    """Check that a signature names each unit, hook and DID of its own
    addresses once, with lowercase SHA-256 text, and that its writes do not
    overlap."""
    spans = {key for key, _start, _end in endpoint.addresses.unit_spans}
    words = {key for key, _address, _width in endpoint.addresses.hook_words}
    unit_keys = [key for key, _digest in endpoint.unit_sha256]
    hook_keys = [key for key, _value in endpoint.hook_values]
    published = (
        HISTORICAL_ROLLING_DIDS if endpoint.published_dids is None
        else endpoint.published_dids
    )
    valid = all((
        endpoint.roms,
        len(set(unit_keys)) == len(unit_keys),
        len(set(hook_keys)) == len(hook_keys),
        set(unit_keys) <= spans,
        set(hook_keys) <= words,
        set(published) <= {did for did, _pointer, _target in endpoint.addresses.did_slots},
        all(
            len(digest) == 64
            and all(character in "0123456789abcdef" for character in digest)
            for _key, digest in endpoint.unit_sha256
        ),
        any(
            schema == endpoint.configuration_schema_version
            for schema, _start, _size in endpoint.addresses.record_spans
        ),
    ))
    if valid:
        ranges = endpoint.write_ranges()
        valid = not any(
            left.overlaps(right) for left, right in zip(ranges, ranges[1:])
        )
    if not valid:
        raise EndpointError(
            f"internal historical Rolling Launch endpoint "
            f"{endpoint.key!r} is invalid"
        )


def _layout_stock_bytes(layout):
    """Return the stock byte of every offset that the layout writes: erased
    claimed ROM and records, the stock hook words and DID slots, and the stock
    words that the layout restores."""
    stock = {}
    for span in (
        *layout.claimed_rom_ranges,
        layout.configuration,
        *layout.retired_configuration_spans,
    ):
        stock.update((offset, 0xFF) for offset in range(span.start, span.end))
    for hook in layout.hooks:
        stock.update(zip(
            range(hook.address, hook.address + hook.width),
            hook.stock.to_bytes(hook.width, layout.byte_order),
        ))
    for item in layout.diagnostics:
        stock.update(zip(
            range(item.pointer_address, item.pointer_address + 4),
            item.stock.to_bytes(4, layout.byte_order),
        ))
    for item in layout.restored_words:
        stock.update(zip(
            range(item.address, item.address + item.width),
            item.value.to_bytes(item.width, layout.byte_order),
        ))
    return stock


def _matches_historical(source, layout, endpoint):
    """Return whether ``source`` holds exactly the endpoint: its units, hooks,
    DIDs and a valid record at its own addresses, and stock bytes at every
    other offset that the current layout writes."""
    require_valid_signature(endpoint)
    byte_order = endpoint.addresses.byte_order
    footprint = endpoint.write_offsets()
    record = endpoint.record
    return all((
        all(
            sha256(source[unit.start : unit.end]) == unit.sha256
            for unit in endpoint.units
        ),
        all(
            read_integer(source, hook.address, hook.width, byte_order) == hook.value
            for hook in endpoint.hooks
        ),
        all(
            read_integer(source, item.pointer_address, 4, byte_order) == item.target
            for item in endpoint.dids
        ),
        historical_configuration_is_valid(
            source[record.start : record.end],
            endpoint.configuration_schema_version,
        ),
        all(
            source[offset] == value
            for offset, value in _layout_stock_bytes(layout).items()
            if offset not in footprint
        ),
    ))


def require_coherent_rolling_endpoint(
    source, layout, payloads, context, rom
):
    """Accept only an absent, current, or registered historical endpoint of
    the ROM."""
    expected_units = set(layout.assembly_unit_by_key)
    if set(payloads) != expected_units:
        raise EndpointError(
            "internal Rolling Launch payload set differs from the layout"
        )

    unit_bytes = {
        unit.key: source[unit.span.start : unit.span.end]
        for unit in layout.assembly_units
    }
    hook_values = {
        hook.key: read_integer(
            source, hook.address, hook.width, layout.byte_order
        )
        for hook in layout.hooks
    }
    did_values = {
        item.did: read_integer(
            source, item.pointer_address, 4, layout.byte_order
        )
        for item in layout.diagnostics
    }
    configuration = configuration_record(source, layout, "current")

    claimed_erased = all(
        source[span.start : span.end] == bytes([0xFF]) * span.size
        for span in layout.claimed_rom_ranges
    )
    hooks_stock = all(
        hook_values[hook.key] == hook.stock for hook in layout.hooks
    )
    dids_stock = all(
        did_values[item.did] == item.stock for item in layout.diagnostics
    )
    if claimed_erased and hooks_stock and dids_stock:
        return "absent"

    hooks_current = all(
        hook_values[hook.key] == hook.replacement for hook in layout.hooks
    )
    dids_current = all(
        did_values[item.did] == item.target for item in layout.diagnostics
    )
    if hooks_current and dids_current:
        # The current runtime keeps its retired records and removed code
        # erased and restores the stock words of the removed fuel path.
        current_units = all(
            unit_bytes[unit.key] == payloads[unit.key]
            for unit in layout.assembly_units
        ) and all(
            _erased(source, span)
            for span in (
                *layout.retired_configuration_spans, *layout.erased_rom_ranges
            )
        ) and all(
            read_integer(source, item.address, item.width, layout.byte_order)
            == item.value
            for item in layout.restored_words
        )
        try:
            current_configuration = rolling_launch.Calibration.from_bytes(
                configuration
            ).is_valid()
        except (TypeError, ValueError):
            current_configuration = False
        if current_units and current_configuration:
            return "current"

    for endpoint in historical_endpoints(rom):
        if _matches_historical(source, layout, endpoint):
            return endpoint.key

    raise EndpointError(
        f"{context}: partial or unknown Rolling Launch state"
    )


def require_coherent_telemetry_endpoint(
    source, layout, payloads, context, launch_layout=None, rom=None
):
    """Accept an absent, current, or exactly registered historical endpoint."""
    expected_units = set(layout.assembly_unit_by_key)
    if set(payloads) != expected_units:
        raise EndpointError(
            "internal CAN telemetry payload set differs from the layout"
        )

    erased_units = all(
        source[unit.span.start : unit.span.end]
        == bytes([0xFF]) * unit.span.size
        for unit in layout.assembly_units
    )
    current_units = all(
        source[unit.span.start : unit.span.end] == payloads[unit.key]
        for unit in layout.assembly_units
    )
    configuration = source[
        layout.configuration.start : layout.configuration.end
    ]
    configuration_erased = (
        configuration == bytes([0xFF]) * layout.configuration.size
    )
    reserve_erased = (
        source[layout.reserved_rom.start : layout.reserved_rom.end]
        == bytes([0xFF]) * layout.reserved_rom.size
    )
    hook_values = {
        hook.key: read_integer(
            source, hook.address, hook.width, layout.byte_order
        )
        for hook in layout.hooks
    }
    lower_hook_values = {}
    if launch_layout is not None:
        lower_hook_values = {
            hook.address: hook.stock for hook in launch_layout.hooks
        }

    def hook_is_lower(hook):
        allowed = {hook.stock}
        if hook.address in lower_hook_values:
            allowed.add(lower_hook_values[hook.address])
        return hook_values[hook.key] in allowed

    hooks_stock = all(hook_is_lower(hook) for hook in layout.hooks)
    hooks_current = all(
        hook_values[hook.key] == hook.replacement for hook in layout.hooks
    )
    record_start = layout.mailbox_record_address
    mailbox_record = source[record_start : record_start + 4]
    stock_mailbox_record = layout.mailbox_record_stock.to_bytes(
        4, layout.byte_order
    )
    if all((
        erased_units,
        configuration_erased,
        reserve_erased,
        hooks_stock,
        mailbox_record == stock_mailbox_record,
    )):
        return "absent"

    try:
        model = can_telemetry.Configuration.from_bytes(configuration)
        configuration_current = model.to_bytes() == configuration
    except (TypeError, ValueError):
        model = None
        configuration_current = False
    if all((
        current_units,
        configuration_current,
        reserve_erased,
        hooks_current,
        model is not None and mailbox_record == model.mailbox_record(),
    )):
        return "current"

    # A historical endpoint matches at its own addresses; every part of the
    # current layout outside it holds the bytes below the telemetry layer.
    erased_offsets = {
        offset
        for span in (
            *(unit.span for unit in layout.assembly_units),
            layout.configuration,
            layout.reserved_rom,
        )
        for offset in range(span.start, span.end)
    }
    # Each current hook word and the mailbox record, and whether it holds
    # the value below the telemetry layer.
    lower_words = [
        (hook.address, hook.address + hook.width, hook_is_lower(hook))
        for hook in layout.hooks
    ]
    lower_words.append(
        (record_start, record_start + 4, mailbox_record == stock_mailbox_record)
    )
    for endpoint in can_telemetry_history.endpoints():
        if (rom or layout.rom) not in endpoint.roms or not endpoint.matches(source):
            continue
        own = endpoint.write_offsets()
        if all(
            source[offset] == 0xFF for offset in erased_offsets - own
        ) and all(
            own.issuperset(range(start, end))
            or (own.isdisjoint(range(start, end)) and lower)
            for start, end, lower in lower_words
        ):
            return endpoint.key

    raise EndpointError(f"{context}: partial or unknown CAN telemetry state")


def strip_telemetry_endpoint(
    source, layout, state, checksum_layout=None
):
    """Restore the exact lower-layer bytes used by endpoint validation: those
    of the current layout, or of a historical endpoint at its own
    addresses."""
    if state == "absent":
        return bytes(source)
    checksum_layout = checksum_layout or canonical_checksums.LAYOUT
    if state != "current":
        historical = can_telemetry_history.endpoint(state)
        if historical is None:
            raise EndpointError(f"unsupported CAN telemetry endpoint {state!r}")
        return bytes(
            rom_checksums.recalculate(historical.strip(source), checksum_layout)
        )
    data = bytearray(source)
    for unit in layout.assembly_units:
        data[unit.span.start : unit.span.end] = (
            bytes([0xFF]) * unit.span.size
        )
    data[layout.configuration.start : layout.configuration.end] = (
        bytes([0xFF]) * layout.configuration.size
    )
    for hook in layout.hooks:
        data[hook.address : hook.address + hook.width] = hook.stock.to_bytes(
            hook.width, layout.byte_order
        )
    start = layout.mailbox_record_address
    data[start : start + 4] = layout.mailbox_record_stock.to_bytes(
        4, layout.byte_order
    )
    return bytes(rom_checksums.recalculate(data, checksum_layout))


def require_complete_map_endpoint(
    source,
    map_layout,
    launch_layout,
    map_payloads,
    launch_payloads,
    context,
    rom,
):
    """Accept one current map endpoint with an optional Rolling Launch layer."""
    for unit in map_layout.assembly_units:
        expected = map_switching_compose.endpoint_unit_bytes(
            map_layout, map_payloads, unit
        )
        actual = source[unit.span.start : unit.span.end]
        if actual != expected and unit.key == "cruise_feedback_engine":
            offset = (
                map_layout.feedback.phase_counts_address - unit.span.start
            )
            historical = []
            for on_frames, off_frames in HISTORICAL_FEEDBACK_FRAME_COUNTS:
                candidate = bytearray(expected)
                candidate[offset : offset + 2] = bytes(
                    (on_frames, off_frames)
                )
                historical.append(bytes(candidate))
            if (
                actual in historical
                or sha256(actual) in HISTORICAL_FEEDBACK_ENGINE_SHA256
            ):
                continue
        if actual != expected:
            raise EndpointError(
                f"{context}: partial or unknown patch state; "
                f"map unit {unit.key} differs"
            )

    # A Rolling Launch layer may own a map hook word: the current layer with
    # its replacement, or a registered historical endpoint with its value.
    rolling_hook_values = {}
    if launch_layout is not None:
        for hook in launch_layout.hooks:
            rolling_hook_values.setdefault(hook.address, set()).add(
                hook.replacement
            )
        for endpoint in historical_endpoints(rom):
            for hook in endpoint.hooks:
                rolling_hook_values.setdefault(hook.address, set()).add(
                    hook.value
                )
    for hook in map_layout.hooks:
        actual = read_integer(
            source, hook.address, hook.width, map_layout.byte_order
        )
        allowed = {hook.replacement} | rolling_hook_values.get(
            hook.address, set()
        )
        if actual not in allowed:
            raise EndpointError(
                f"{context}: partial or unknown patch state; "
                f"map hook {hook.key} is {actual:#x}"
            )

    for family in map_layout.families:
        start = family.pointer_table
        expected = _expected_pointer_table(map_layout, family)
        actual = source[start : start + len(expected)]
        if actual != expected:
            raise EndpointError(
                f"{context}: partial or unknown patch state; "
                f"pointer table {family.key} differs"
            )

    if launch_layout is None:
        if launch_payloads:
            raise EndpointError(
                "disabled Rolling Launch has unexpected payloads"
            )
        return "current"
    return require_coherent_rolling_endpoint(
        source, launch_layout, launch_payloads, context, rom
    )


@dataclass(frozen=True)
class Classification:
    """The runtime layers of an image: each state is "absent", "current", or
    the key of a registered historical Rolling Launch endpoint."""

    telemetry: str
    rolling: str


def historical_endpoints(rom):
    """Return the registered historical Rolling Launch endpoints of a ROM."""
    return tuple(
        endpoint for endpoint in HISTORICAL_ROLLING_ENDPOINTS
        if rom in endpoint.roms
    )


def _historical_rolling_offsets(rom):
    """Return every offset that a registered historical Rolling Launch
    endpoint of the ROM writes or keeps erased."""
    offsets = set()
    for endpoint in historical_endpoints(rom):
        offsets |= endpoint.write_offsets()
    return frozenset(offsets)


def historical_write_offsets(rom):
    """Return every offset that a registered historical Rolling Launch
    endpoint of the ROM writes or keeps erased, or that a registered
    historical CAN telemetry endpoint writes."""
    return _historical_rolling_offsets(rom) | can_telemetry_history.write_offsets(
        rom
    )


def _current_write_offsets(layout):
    """Return the offsets that the current runtime composes: its units,
    records, efficiency table, hook words, DID slots and restored words."""
    spans = [
        (unit.span.start, unit.span.end) for unit in layout.assembly_units
    ]
    spans += [
        (span.start, span.end)
        for span in (
            layout.configuration,
            layout.efficiency,
            *layout.retired_configuration_spans,
            *layout.erased_rom_ranges,
        )
    ]
    spans += [
        (hook.address, hook.address + hook.width) for hook in layout.hooks
    ]
    spans += [
        (item.address, item.address + item.width)
        for item in layout.restored_words
    ]
    spans += [
        (item.pointer_address, item.pointer_address + 4)
        for item in layout.diagnostics
    ]
    return {offset for start, end in spans for offset in range(start, end)}


def _telemetry_layout_offsets(layout):
    """Return the offsets that the current CAN telemetry layout writes or
    keeps erased."""
    spans = [(unit.span.start, unit.span.end) for unit in layout.assembly_units]
    spans += [
        (span.start, span.end)
        for span in (layout.configuration, layout.reserved_rom)
    ]
    spans.append(
        (layout.mailbox_record_address, layout.mailbox_record_address + 4)
    )
    spans += [
        (hook.address, hook.address + hook.width) for hook in layout.hooks
    ]
    return {offset for start, end in spans for offset in range(start, end)}


def _require_stock_outside_history(
    source, target, state, telemetry_state, context
):
    """Refuse the bytes of another registered Rolling Launch or CAN telemetry
    endpoint that lie outside the offsets that the classified states
    verified: for each layer the current composition, or the current layout
    and the endpoint's own writes."""
    layout = target.rolling_layout
    if state == "current":
        covered = _current_write_offsets(layout)
    else:
        covered = set(_layout_stock_bytes(layout))
        if state != "absent":
            covered |= historical_endpoint(state).write_offsets()
    covered |= _telemetry_layout_offsets(target.telemetry_layout)
    telemetry = can_telemetry_history.endpoint(telemetry_state)
    if telemetry is not None:
        covered |= telemetry.write_offsets()
    # Below the Rolling Launch layer a hook word that Map Switching shares
    # holds the Map Switching replacement; every other byte is stock.
    below = bytearray(target.stock_image.data)
    map_layout = target.map_layout
    for hook in map_layout.hooks:
        below[hook.address : hook.address + hook.width] = hook.replacement.to_bytes(
            hook.width, map_layout.byte_order
        )
    for layer, offsets in (
        ("Rolling Launch", _historical_rolling_offsets(target.rom)),
        ("CAN telemetry", can_telemetry_history.write_offsets(target.rom)),
    ):
        if any(source[offset] != below[offset] for offset in offsets - covered):
            raise EndpointError(f"{context}: partial or unknown {layer} state")


def classify_runtime(source, target, context):
    """Classify the complete runtime of an image that differs from its stock
    image inside the builder write sets."""
    telemetry_state = require_coherent_telemetry_endpoint(
        source,
        target.telemetry_layout,
        target.telemetry_payloads,
        context,
        target.rolling_layout,
        rom=target.rom,
    )
    lower_source = strip_telemetry_endpoint(
        source, target.telemetry_layout, telemetry_state, target.checksum_layout
    )
    rolling_state = require_complete_map_endpoint(
        lower_source,
        target.map_layout,
        target.rolling_layout,
        target.map_payloads,
        target.rolling_payloads,
        context,
        target.rom,
    )
    if target.rolling_layout is not None:
        _require_stock_outside_history(
            lower_source, target, rolling_state, telemetry_state, context
        )
    if (
        telemetry_state != "absent"
        and rolling_state not in TELEMETRY_LOWER_ROLLING_STATES
    ):
        raise EndpointError(
            f"{context}: CAN telemetry is not layered "
            "over the current lower runtime endpoint"
        )
    if target.rolling_layout is None:
        # The map endpoint is the complete lower runtime of a target
        # without a Rolling Launch layer.
        rolling_state = "absent"
    return Classification(telemetry=telemetry_state, rolling=rolling_state)
