#!/usr/bin/env python3
"""Hold repeated project constants and published counts to their sources.

A value that several files need has one owning file. The Memgraph compose file
publishes the Bolt port, `tools/rom_sources.py` the Ghidra export root, the
telemetry profile the data CAN ID, the dashboard package its product identity,
`tools/kb/bench.toml` the acceptance questions of the kb specification, and
the ROM registries the label sets. A copy that a standalone script, a command
default, or a document keeps is compared here with its owner, and every ROM
list and count a document publishes is compared with the registry, profile,
or image that determines it.
"""

import argparse
import csv
from dataclasses import dataclass
import io
from pathlib import Path
import re
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import can_telemetry_profile
from patches import rom_address_profiles
from patches import runtime_targets
from tools.can_dashboard import (
    PRODUCT_NAME,
    PRODUCT_SHORT_NAME,
    PRODUCT_SLUG,
    recording,
)
from tools.mapkit import dtc_projection
from tools.mapkit import rom as romkit

COMPOSE = "tools/memgraph/docker-compose.yml"
EXPORT_OWNER = "tools/rom_sources.py"
PRODUCT_OWNER = "tools/can_dashboard/__init__.py"
TELEMETRY_PROFILE = "patches/can-telemetry-profile.toml"
IMAGE_REGISTRY = "rom-images/roms.csv"
IDENTITY_REGISTRY = "defs/rom-identities.toml"
HOMOLOGY_REGISTRY = "rom-images/homology.toml"
CHECKSUM_REGISTRY = "patches/checksum-layouts.toml"
INHERITANCE_REGISTRY = "defs/rom-inheritance.toml"
MAP_LAYOUT = "patches/map-switching-layout.toml"
ATLAS_MANIFESTS = "tools/romviz/roms/"
INTAKE_GUIDE = "rom-images/new-rom-intake.md"
CORRESPONDENCE = {"1ME3B": "patches/1me3b-runtime-correspondence.csv"}
KB_SPEC = "tools/kb/SPEC.md"
KB_BENCH = "tools/kb/bench.toml"
KB_QUESTIONS = "## 18. Acceptance questions"
DID_TABLE_EVIDENCE = "Aligned diagnostic pointer tables of 1ND0A and 1ME3B"

# Primary references are transcriptions of external documents.
UNSCANNED = ("refs/", "defs/reference/")
# The tests of this gate carry drifted copies on purpose.
DRIFT_FIXTURES = ("tools/tests/test_single_source.py",)
TEXT_SUFFIXES = (".md", ".py", ".sh", ".toml", ".yml", ".java", ".js")
LOOPBACK_HOSTS = ("localhost", "127.0.0.1")
EXPORT_PATH = re.compile(r"(?:~|\$\{?HOME\}?)((?:/[\w.-]+)*?/ghidra-projects)(?![\w.-])")
CAN_ID_DEFAULTS = (
    re.compile(
        r"\b(?:DEFAULT_CAN_ID|can_id|candidate_id)(?:\s*:\s*int)?\s*=\s*"
        r"(0x[0-9A-Fa-f]+)"
    ),
    re.compile(r'"--(?:can|candidate)-id",[^\n]*?\bdefault=(0x[0-9A-Fa-f]+)'),
)
CAN_ID_COMMAND = re.compile(r"--(?:can|candidate)-id[ =](0x[0-9A-Fa-f]+)")

NUMBER_WORDS = (
    "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
    "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
    "sixteen", "seventeen", "eighteen", "nineteen", "twenty",
)
NUMBER = r"(\d+|(?i:" + "|".join(NUMBER_WORDS) + r"))"
ADDRESS = r"(0x[0-9A-Fa-f]+)"
LIST_SEPARATOR = r"(?:, and |, | and |/)"


class SourceError(Exception):
    """A copy or a published fact differs from the file that owns it."""


def _text(path):
    return (ROOT / path).read_text(encoding="utf-8")


def _toml(path):
    return tomllib.loads(_text(path))


def _single(path, pattern):
    """Read the one capture an owning file is required to carry."""
    found = re.findall(pattern, _text(path), re.MULTILINE)
    if len(found) != 1:
        raise SourceError(
            f"{path} carries {len(found)} values matching {pattern!r}, "
            "exactly one is required"
        )
    return found[0]


def _tracked(*suffixes):
    listed = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    ).stdout.decode("utf-8")
    for path in sorted(filter(None, listed.split("\0"))):
        if (
            path.startswith(UNSCANNED)
            or path in DRIFT_FIXTURES
            or not (ROOT / path).is_file()
        ):
            continue
        if not suffixes or path.endswith(suffixes):
            yield path


def _is_test(path):
    return "/tests/" in path or Path(path).name.startswith("test_")


def bolt_uri():
    port = _single(COMPOSE, r'^\s*- "127\.0\.0\.1:(\d+):7687"')
    return f"bolt://localhost:{port}"


def check_graph_endpoint():
    """Require every Bolt URI to reach the port the compose file publishes."""
    expected = bolt_uri()
    port = expected.rsplit(":", 1)[1]
    constants = 0
    for path in _tracked(*TEXT_SUFFIXES):
        text = _text(path)
        if path.endswith(".py"):
            for value in re.findall(r'^BOLT = "([^"]*)"$', text, re.MULTILINE):
                constants += 1
                if value != expected:
                    raise SourceError(
                        f"{path} connects to {value}, {COMPOSE} publishes "
                        f"{expected}"
                    )
        for host, found in re.findall(r"bolt://([\w.-]+):(\d+)", text):
            if host not in LOOPBACK_HOSTS or found != port:
                raise SourceError(
                    f"{path} names bolt://{host}:{found}, {COMPOSE} publishes "
                    f"{expected}"
                )
    if not constants:
        raise SourceError("no tracked module declares a BOLT endpoint")
    return constants


def export_root():
    return _single(
        EXPORT_OWNER, r'^EXPORT_ROOT = Path\("([^"]+)"\)\.expanduser\(\)$'
    )


def check_export_root():
    """Require every Ghidra export path to sit under the one export root."""
    expected = export_root()
    for path in _tracked(*TEXT_SUFFIXES):
        for found in EXPORT_PATH.findall(_text(path)):
            if "~" + found != expected:
                raise SourceError(
                    f"{path} names ~{found}, {EXPORT_OWNER} exports under "
                    f"{expected}"
                )
    return expected


def telemetry_can_id():
    return int(
        _single(TELEMETRY_PROFILE, r"^candidate_can_id = (0x[0-9A-Fa-f]+)$"), 16
    )


def check_can_id():
    """Require every default and documented command to use the profile CAN ID."""
    expected = telemetry_can_id()
    copies = 0
    for path in _tracked(".py", ".md", ".sh"):
        if _is_test(path):
            continue
        text = _text(path)
        patterns = (*CAN_ID_DEFAULTS, CAN_ID_COMMAND)
        if not path.endswith(".py"):
            patterns = (CAN_ID_COMMAND,)
        for pattern in patterns:
            for value in pattern.findall(text):
                copies += 1
                if int(value, 16) != expected:
                    raise SourceError(
                        f"{path} defaults the telemetry CAN ID to {value}, "
                        f"{TELEMETRY_PROFILE} declares {expected:#X}"
                    )
    return copies


def check_product_identity():
    """Require code to take the product name and slug from the package."""
    for path in (*_tracked(".py"), "Makefile"):
        if path == PRODUCT_OWNER or _is_test(path):
            continue
        text = _text(path)
        for value in (PRODUCT_NAME, PRODUCT_SHORT_NAME, PRODUCT_SLUG):
            if value in text:
                raise SourceError(
                    f"{path} spells the product identity {value!r}; "
                    f"{PRODUCT_OWNER} is its one record"
                )


def published_questions():
    """The acceptance questions of the kb specification as (id, question,
    command, budget, stage) rows."""
    section = _text(KB_SPEC).split("\n" + KB_QUESTIONS + "\n", 1)[1].split("\n## ", 1)[0]
    rows = []
    for line in section.splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not line.startswith("| ") or not cells[0].isdigit():
            continue
        number, question, command, budget, stage = cells
        rows.append((int(number), question, command.strip("`"), int(budget), int(stage)))
    return rows


def check_kb_questions():
    """Require the question table of the kb specification to equal the
    questions, budgets, and stages that `tools/kb/bench.toml` owns."""
    owned = [
        (item["id"], item["question"], item["command"], item["budget"], item["stage"])
        for item in _toml(KB_BENCH)["question"]
    ]
    published = published_questions()
    if published != owned:
        differing = sorted(set(published) ^ set(owned))
        raise SourceError(
            f"{KB_SPEC} publishes acceptance questions that differ from {KB_BENCH}: "
            f"{differing}"
        )
    return len(owned)


def _image_rows():
    return list(csv.DictReader(io.StringIO(_text(IMAGE_REGISTRY))))


def registered_labels():
    labels = [row["rom"] for row in _image_rows() if row["rom"]]
    if len(labels) != len(set(labels)):
        raise SourceError(f"{IMAGE_REGISTRY} repeats a ROM label")
    return tuple(labels)


def check_stock_hashes():
    """Require documents to cite the image registry instead of a stock hash."""
    hashes = {row["sha256"]: row["path"] for row in _image_rows() if row["sha256"]}
    for path in _tracked(".md"):
        text = _text(path)
        for digest, image in hashes.items():
            if digest in text:
                raise SourceError(
                    f"{path} repeats the SHA-256 of {image}; {IMAGE_REGISTRY} "
                    "is its one record"
                )


def _layout_labels():
    labels = [
        rom
        for layout in _toml(CHECKSUM_REGISTRY)["layout"].values()
        for rom in layout["roms"]
    ]
    if len(labels) != len(set(labels)):
        raise SourceError(f"{CHECKSUM_REGISTRY} assigns a ROM to two layouts")
    return frozenset(labels)


def _homology_members():
    return {
        name: frozenset(family["members"])
        for name, family in _toml(HOMOLOGY_REGISTRY)["family"].items()
    }


RUNTIME_FAMILIES = (
    (runtime_targets.EXACT_FAMILY, runtime_targets.EXACT_ROMS),
    (runtime_targets.RELOCATED_8MFK_FAMILY, runtime_targets.RELOCATED_8MFK_ROMS),
    (runtime_targets.SH7059_1ND_FAMILY, runtime_targets.SH7059_1ND_ROMS),
    (runtime_targets.SH7059_1ME3B_FAMILY, runtime_targets.SH7059_1ME3B_ROMS),
    (runtime_targets.SH7058_JK78C_FAMILY, runtime_targets.SH7058_JK78C_ROMS),
)


def check_rom_registries():
    """Hold every ROM label set to the image registry and to its family."""
    labels = frozenset(registered_labels())
    manifests = frozenset(
        Path(path).stem
        for path in _tracked(".toml")
        if path.startswith(ATLAS_MANIFESTS)
    )
    if manifests != labels:
        raise SourceError(
            f"atlas manifests {sorted(manifests)} differ from the images "
            f"{sorted(labels)} of {IMAGE_REGISTRY}"
        )
    identities = frozenset(_toml(IDENTITY_REGISTRY)["rom"])
    layouts = _layout_labels()
    for registry, found in (
        (IDENTITY_REGISTRY, identities),
        (CHECKSUM_REGISTRY, layouts),
    ):
        if not found <= labels:
            raise SourceError(
                f"{registry} names unregistered images {sorted(found - labels)}"
            )
    if not identities <= layouts:
        raise SourceError(
            f"definition targets {sorted(identities - layouts)} have no "
            f"layout in {CHECKSUM_REGISTRY}"
        )
    members = _homology_members()
    for family, roms in RUNTIME_FAMILIES:
        if not set(roms) <= members.get(family, frozenset()):
            raise SourceError(
                f"patches/runtime_targets.py places {sorted(roms)} in {family}, "
                f"{HOMOLOGY_REGISTRY} declares {sorted(members.get(family, ()))}"
            )
    inheritors = frozenset(_toml(INHERITANCE_REGISTRY)["inherit"])
    if inheritors != set(dtc_projection.INHERITED_ROMS):
        raise SourceError(
            f"tools/mapkit/dtc_projection.py shares the canonical registry with "
            f"{sorted(dtc_projection.INHERITED_ROMS)}, {INHERITANCE_REGISTRY} "
            f"declares {sorted(inheritors)}"
        )
    registries = frozenset(
        Path(path).name.removesuffix(".dtc.csv")
        for path in _tracked(".dtc.csv")
        if path.startswith("defs/")
    )
    projected = {dtc_projection.SOURCE_ROM, *dtc_projection.PROJECTED_ROMS}
    if registries != projected:
        raise SourceError(
            f"defs holds DTC registries for {sorted(registries)}, "
            f"tools/mapkit/dtc_projection.py projects {sorted(projected)}"
        )
    intake = _text(INTAKE_GUIDE)
    for registry in (
        IMAGE_REGISTRY,
        HOMOLOGY_REGISTRY,
        IDENTITY_REGISTRY,
        CHECKSUM_REGISTRY,
        ATLAS_MANIFESTS,
    ):
        name = registry.removeprefix("rom-images/")
        if name not in intake:
            raise SourceError(f"{INTAKE_GUIDE} does not name {name}")
    return len(labels)


@dataclass(frozen=True)
class Labels:
    """A ROM label set a document publishes as a list."""

    roms: frozenset


@dataclass(frozen=True)
class Fact:
    """One document statement and the values its captures must equal."""

    path: str
    pattern: str
    expected: tuple


def _number(token):
    if token.lower() in NUMBER_WORDS:
        return NUMBER_WORDS.index(token.lower())
    if token.lower().startswith("0x"):
        return int(token, 16)
    return int(token)


class Sources:
    """The registry, profile, and image values the documents publish."""

    def __init__(self):
        self.labels = registered_labels()
        self.identities = frozenset(_toml(IDENTITY_REGISTRY)["rom"])
        self.layouts = _layout_labels()
        self.members = _homology_members()
        self.profiles = rom_address_profiles.load_registry()
        self.layout_families = _toml(MAP_LAYOUT)["family"]
        manifest = can_telemetry_profile.load_manifest()
        fields = (*manifest.fields, *(f for c in manifest.contexts for f in c.fields))
        self.ecu_fields = sum(field.kind == "ecu_ram" for field in fields)
        self.protocol = manifest.protocol_version
        tuning = manifest.profile_by_name["tuning"]
        self.identity = (tuning.profile_id, tuning.crc16)
        self.bindings = len(recording.build_bindings("tuning"))
        roms = (dtc_projection.SOURCE_ROM, *dtc_projection.PROJECTED_ROMS)
        self.registries = {rom: dtc_projection.read_registry(rom) for rom in roms}
        self.tables = {
            rom: dtc_projection.locate_tables(romkit.load(rom).data)
            for rom in ("1ND0A", "1ME3B")
        }

    def switched(self, roms):
        """Return the one switched-family count the ROMs share."""
        counts = {
            len(self.profiles[rom].map_families)
            if rom in self.profiles
            else len(self.layout_families)
            for rom in roms
        }
        if len(counts) != 1:
            raise SourceError(f"{sorted(roms)} switch different family counts")
        return counts.pop()

    def codes(self, roms):
        """Return the one DTC registry size the ROMs share."""
        counts = {len(self.registries[rom]) for rom in roms}
        if len(counts) != 1:
            raise SourceError(f"{sorted(roms)} carry different DTC counts")
        return counts.pop()

    def shared_codes(self, rom, other):
        codes = {row["dtc"] for row in self.registries[other]}
        return sum(row["dtc"] in codes for row in self.registries[rom])

    def bound(self, rom):
        return len(self.profiles[rom].telemetry_sources)

    def unavailable(self, roms):
        """Return the one unavailable telemetry field count the ROMs share."""
        counts = {len(self.profiles[rom].telemetry_unavailable) for rom in roms}
        if len(counts) != 1:
            raise SourceError(f"{sorted(roms)} leave different field counts unavailable")
        return counts.pop()

    def did_confirmed(self, rom):
        """Count the telemetry cells the target DID pointer table confirms."""
        rows = csv.DictReader(io.StringIO(_text(CORRESPONDENCE[rom])))
        return sum(
            row["domain"] == "telemetry"
            and row["status"] == "mapped"
            and row["evidence"].startswith(DID_TABLE_EVIDENCE)
            for row in rows
        )

    def onboarded_families(self):
        return sum(bool(roms & self.identities) for roms in self.members.values())


def published_facts(sources=None):
    """Return every ROM list and count a document publishes, with its source."""
    s = sources or Sources()
    exact = runtime_targets.EXACT_ROMS
    eight = runtime_targets.RELOCATED_8MFK_ROMS
    nd = runtime_targets.SH7059_1ND_ROMS
    me = runtime_targets.SH7059_1ME3B_ROMS
    jk78 = runtime_targets.SH7058_JK78C_ROMS
    relocated = Labels(frozenset(runtime_targets.RELOCATED_ROMS))
    supported = runtime_targets.SUPPORTED_ROMS
    me_tables, nd_tables = s.tables["1ME3B"], s.tables["1ND0A"]
    shared = s.shared_codes("1ME3B", "1ND0A")
    adapters = sum("adapter" in family for family in s.layout_families)
    canonical = _toml(HOMOLOGY_REGISTRY)["family"][runtime_targets.EXACT_FAMILY][
        "canonical"
    ]
    matrix = "rom-images/support-matrix.md"
    defs = "defs/README.md"
    builder = "patches/rom-builder.md"
    selector = "patches/map-switching-selector.md"
    profiles = "patches/rom-address-profiles.toml"
    telemetry = "patches/can-telemetry.md"
    return (
        Fact(
            matrix,
            r"its registries hold {n} codes rather than {n},",
            (s.codes(jk78 + nd), s.codes((dtc_projection.SOURCE_ROM,))),
        ),
        Fact(matrix, r"which is why it holds {n}\.", (s.codes(me),)),
        Fact(
            matrix,
            r"Its {n} descriptor records start at `{a}` and its attribute "
            r"pointers at `{a}`, against {n} records at `{a}` for `1ND0A`",
            (
                me_tables.count,
                me_tables.start,
                me_tables.pointer_base,
                nd_tables.count,
                nd_tables.start,
            ),
        ),
        Fact(matrix, r"the {n} codes the two images share", (shared,)),
        Fact(
            matrix,
            r"Of the {n} telemetry fields, {n} bind to 1ME3B ECU RAM; {n} of "
            r"those sources are confirmed against the DID pointer table",
            (s.ecu_fields, s.bound("1ME3B"), s.did_confirmed("1ME3B")),
        ),
        Fact(defs, r"\| {dtc} \| Relocated DTC edit ranges", (relocated,)),
        Fact(defs, r"Map 2-5 storage for {n} switched families", (s.switched(me),)),
        Fact(
            defs,
            r"it reproduces all {n} canonical JK08A attribute addresses",
            (s.codes((dtc_projection.SOURCE_ROM,)),),
        ),
        Fact(
            defs,
            r"JK00C and JK00D carry all {n} codes; JK78C and `1ND` carry {n}, because",
            (s.codes(eight), s.codes(jk78 + nd)),
        ),
        Fact(defs, r"1ME3B carries {n}, because it declares no P0443", (s.codes(me),)),
        Fact(
            defs,
            r"Its {n} descriptor records at `{a}` hold the {n} codes it shares "
            r"with the {n} records of `1ND0A`",
            (me_tables.count, me_tables.start, shared, nd_tables.count),
        ),
        Fact(
            "rom-images/README.md",
            r"All {n} reviewed DTC descriptor and attribute pairs are identical "
            r"in all {n} images",
            (s.codes((dtc_projection.SOURCE_ROM,)), len(s.members[runtime_targets.EXACT_FAMILY])),
        ),
        Fact(
            INTAKE_GUIDE,
            r"The branches are read from {n} onboarded families",
            (s.onboarded_families(),),
        ),
        Fact(INTAKE_GUIDE, r"branch: 1ME3B carries {n} codes with", (s.codes(me),)),
        Fact(
            "rom-images/23710-1ME3B/README.md",
            r"The descriptor region holds {n} twelve-byte records at `{a}` "
            r"followed by their {n} attribute pointers at `{a}`, against {n} "
            r"records at `{a}` in `1ND0A`",
            (
                me_tables.count,
                me_tables.start,
                me_tables.count,
                me_tables.pointer_base,
                nd_tables.count,
                nd_tables.start,
            ),
        ),
        Fact(
            "rom-images/23710-1ME3B/README.md",
            r"`\.\./\.\./defs/1ME3B\.dtc\.csv` carries {n} canonical codes",
            (s.codes(me),),
        ),
        Fact(
            "rom-images/23710-1ME3B/README.md",
            r"across the {n} codes shared with `1ND0A`",
            (shared,),
        ),
        Fact(
            builder,
            r"All {n} family layouts use mailbox 31",
            (len(RUNTIME_FAMILIES),),
        ),
        Fact(
            builder,
            r"`rom-address-profiles\.toml` records exact {list} stock addresses",
            (Labels(frozenset(s.profiles)),),
        ),
        Fact(builder, r"and locked payloads for {list}\.", (relocated,)),
        *(
            Fact(
                builder,
                rf"`{name}-runtime-correspondence\.csv` records the reviewed "
                rf"{rom} runtime allocation, [^.]*, and all {{n}} ECU-RAM "
                r"telemetry fields",
                (s.ecu_fields,),
            )
            for name, rom in (("1nd", nd[0]), ("1me3b", me[0]), ("jk78c", jk78[0]))
        ),
        Fact(
            builder,
            r"JK00C and JK00D telemetry binds {n} of the {n} ECU-RAM fields",
            (s.ecu_fields - s.unavailable(eight), s.ecu_fields),
        ),
        Fact(
            builder,
            r"The 1ND address profile binds {n} switched families",
            (s.switched(nd),),
        ),
        Fact(
            builder,
            r"Custom CAN telemetry binds {n} of the {n} schema fields",
            (s.bound(nd[0]), s.ecu_fields),
        ),
        Fact(
            builder,
            r"The 1ME3B address profile binds the {n} 1ND families",
            (s.switched(me),),
        ),
        Fact(
            builder,
            r"Custom CAN telemetry binds {n} of the {n} ECU-RAM fields",
            (s.bound(me[0]), s.ecu_fields),
        ),
        Fact(
            builder,
            r"The JK78C address profile binds {n} families",
            (s.switched(jk78),),
        ),
        Fact(
            builder,
            r"Custom CAN telemetry binds {n} available schema fields",
            (s.bound(jk78[0]),),
        ),
        Fact(selector, r"The {n} adapter-backed families", (adapters,)),
        Fact(
            selector,
            r"The {n} limiter families use RAM shadows",
            (len(s.layout_families) - adapters,),
        ),
        Fact(
            selector,
            r"JK78C uses {n} target-specific families; {list} use {n},",
            (s.switched(jk78), Labels(frozenset(nd + me)), s.switched(nd + me)),
        ),
        Fact(
            selector,
            r"Only \w+ of the {n} switched families differ",
            (len(s.layout_families),),
        ),
        Fact(
            "patches/rolling-launch.md",
            r"The {list} and {list} variants use a temporary map-specific "
            r"fuel-cut window\. {list} use a final-mask coordinator request",
            (
                Labels(frozenset(exact)),
                Labels(frozenset(eight)),
                Labels(frozenset(runtime_targets.VQ37_RUNTIME_ROMS)),
            ),
        ),
        Fact(
            "patches/rom-selftest-checksum.md",
            r"Exact layouts are registered for {list}\.",
            (Labels(s.layouts),),
        ),
        Fact(
            "tools/sh-elf-run/README.md",
            r"every rendered {list} target unit",
            (relocated,),
        ),
        Fact(
            "tools/sh-elf-run/README.md",
            r"fixtures for {list} and enforce",
            (Labels(relocated.roms | {canonical}),),
        ),
        Fact(
            "README.md",
            r"code profile for the exact {list} family",
            (Labels(frozenset(exact)),),
        ),
        Fact(
            "README.md",
            r"capability-specific runtime for {list}\. Map Switching, Rolling "
            r"Launch, and custom CAN telemetry are available on all {n} targets",
            (Labels(frozenset(supported)), len(supported)),
        ),
        Fact(
            "README.md",
            r"files for all {n} stock identities",
            (len(s.identities),),
        ),
        Fact("README.md", r"and the target-specific {list} projections", (relocated,)),
        Fact(
            "tools/can_dashboard/README.md",
            r"The `tuning` MLG schema has {n} channels",
            (s.bindings,),
        ),
        Fact(
            "tools/can_dashboard/README.md",
            r"The bundled schema declares profile ID {n} with CRC16 `{a}`",
            s.identity,
        ),
        Fact(
            telemetry,
            r"\| 4 \| 1 \| profile ID `{n}` \|",
            (s.identity[0],),
        ),
        Fact(
            telemetry,
            r"\| 10 \| 2 \| profile CRC16 `{a}` \|",
            (s.identity[1],),
        ),
        Fact(
            telemetry,
            r"until page 9 tag 3 reports version {n}, profile ID {n}, and CRC "
            r"`{a}`\.",
            (s.protocol, *s.identity),
        ),
        Fact(
            telemetry,
            r"- version {n}, profile ID {n}, and CRC `{a}` health identity",
            (s.protocol, *s.identity),
        ),
        Fact(
            "defs/JK08A.tuning-telemetry.md",
            r"Schema 2 uses protocol version {n}, profile ID {n}, generated "
            r"CRC16 `{a}`",
            (s.protocol, *s.identity),
        ),
        Fact(
            "tools/logs/README.md",
            r"The `tuning` output contains {n} fields",
            (s.bindings,),
        ),
        Fact(
            profiles,
            r"and 1ND bank structure bind {n} supported families",
            (s.switched(nd),),
        ),
        Fact(
            profiles,
            r"and 1ME3B bank structure bind {n} supported families",
            (s.switched(me),),
        ),
        Fact(
            profiles,
            r"fuel-cut state machine bind {n} supported VQ37 families",
            (s.switched(jk78),),
        ),
    )


def _fact_pattern(pattern, labels):
    label = "(?:" + "|".join(sorted(map(re.escape, labels), key=len, reverse=True)) + ")"
    label = rf"(?<![\w-]){label}(?![\w-])"
    items = rf"({label}(?:{LIST_SEPARATOR}{label})*)"
    files = rf"(`{label}\.dtc\.csv`(?:, `{label}\.dtc\.csv`)*)"
    return (
        pattern.replace("{n}", NUMBER)
        .replace("{a}", ADDRESS)
        .replace("{list}", items)
        .replace("{dtc}", files)
    ), label


def check_published(facts=None):
    """Require every published ROM list and count to equal its source."""
    labels = registered_labels()
    for fact in facts if facts is not None else published_facts():
        pattern, label = _fact_pattern(fact.pattern, labels)
        text = " ".join(_text(fact.path).split())
        found = [match for match in re.finditer(pattern, text)]
        if len(found) != 1:
            raise SourceError(
                f"{fact.path} carries {len(found)} statements matching "
                f"{fact.pattern!r}, exactly one is required"
            )
        match = found[0]
        for token, expected in zip(match.groups(), fact.expected, strict=True):
            if isinstance(expected, Labels):
                published = re.findall(label, token)
                if (
                    len(published) != len(set(published))
                    or set(published) != expected.roms
                ):
                    raise SourceError(
                        f"{fact.path} publishes '{match[0]}', the sources hold "
                        f"{sorted(expected.roms)}"
                    )
            elif _number(token) != expected:
                raise SourceError(
                    f"{fact.path} publishes '{match[0]}', the sources hold "
                    f"{expected} for {token}"
                )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail when a copy or a published fact differs from its source",
    )
    parser.parse_args(argv)
    try:
        endpoints = check_graph_endpoint()
        check_export_root()
        can_ids = check_can_id()
        check_product_identity()
        check_stock_hashes()
        questions = check_kb_questions()
        images = check_rom_registries()
        facts = published_facts()
        check_published(facts)
    except (
        SourceError,
        rom_address_profiles.AddressProfileError,
        dtc_projection.DtcProjectionError,
        OSError,
        ValueError,
        KeyError,
    ) as error:
        print(f"single source: {error}", file=sys.stderr)
        return 1
    print(
        f"single source: {endpoints} Bolt endpoints, {can_ids} CAN ID copies, "
        f"{questions} kb questions, {images} registered images, and "
        f"{len(facts)} published facts match their sources"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
