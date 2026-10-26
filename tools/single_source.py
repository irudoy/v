#!/usr/bin/env python3
"""Check executable constants and registry bindings against machine owners."""

import argparse
import csv
import io
from pathlib import Path
import re
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import runtime_targets
from kb import spec as kb_spec
from kb.repo import KbError
from tools.can_dashboard import (
    PRODUCT_NAME,
    PRODUCT_SHORT_NAME,
    PRODUCT_SLUG,
)
from tools.mapkit import dtc_projection

COMPOSE = "tools/memgraph/docker-compose.yml"
EXPORT_OWNER = "tools/rom_sources.py"
PRODUCT_OWNER = "tools/can_dashboard/__init__.py"
TELEMETRY_PROFILE = "patches/can-telemetry-profile.toml"
IMAGE_REGISTRY = "rom-images/roms.csv"
IDENTITY_REGISTRY = "defs/rom-identities.toml"
HOMOLOGY_REGISTRY = "rom-images/homology.toml"
CHECKSUM_REGISTRY = "patches/checksum-layouts.toml"
INHERITANCE_REGISTRY = "defs/rom-inheritance.toml"
ATLAS_MANIFESTS = "tools/romviz/roms/"
KB_BENCH = "tools/kb/bench.toml"

# Primary references are transcriptions of external documents.
UNSCANNED = ("refs/", "defs/reference/")
# The tests of this gate carry drifted copies on purpose.
DRIFT_FIXTURES = ("tools/tests/test_single_source.py",)
TEXT_SUFFIXES = (".py", ".sh", ".toml", ".yml", ".java", ".js")
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

class SourceError(Exception):
    """An executable copy or registry binding differs from its machine owner."""


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
    """Scan tracked and new non-ignored files before they enter a commit."""
    listed = subprocess.run(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        cwd=ROOT,
        capture_output=True,
        check=True,
    ).stdout.decode("utf-8")
    for path in sorted(set(filter(None, listed.split("\0")))):
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
    """Require executable defaults and commands to use the profile CAN ID."""
    expected = telemetry_can_id()
    copies = 0
    for path in _tracked(".py", ".sh"):
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


def check_kb_questions():
    """Validate benchmark contracts directly in their machine owner."""
    questions = _toml(KB_BENCH)["question"]
    identifiers = set()
    for question in questions:
        try:
            kb_spec.expectations(question)
        except KbError as error:
            raise SourceError(f"{KB_BENCH}: {error}") from error
        number = question.get("id")
        if not isinstance(number, int) or number in identifiers:
            raise SourceError(f"{KB_BENCH}: duplicate or invalid question id {number!r}")
        identifiers.add(number)
        if not isinstance(question.get("budget"), int) or question["budget"] <= 0:
            raise SourceError(f"{KB_BENCH}: question {number} requires a positive budget")
        if not isinstance(question.get("command"), str) or not question["command"].startswith("kb "):
            raise SourceError(f"{KB_BENCH}: question {number} requires a KB command")
    return len(questions)


def _image_rows():
    return list(csv.DictReader(io.StringIO(_text(IMAGE_REGISTRY))))


def registered_labels():
    labels = [row["rom"] for row in _image_rows() if row["rom"]]
    if len(labels) != len(set(labels)):
        raise SourceError(f"{IMAGE_REGISTRY} repeats a ROM label")
    return tuple(labels)


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
    return len(labels)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate executable constants and machine registry bindings",
    )
    parser.parse_args(argv)
    try:
        check_graph_endpoint()
        check_export_root()
        check_can_id()
        check_product_identity()
        check_kb_questions()
        check_rom_registries()
    except (
        SourceError,
        dtc_projection.DtcProjectionError,
        OSError,
        ValueError,
        KeyError,
    ) as error:
        print(f"single source: {error}", file=sys.stderr)
        return 1
    print("single source: machine constants and ROM registries match")
    return 0


if __name__ == "__main__":
    sys.exit(main())
