#!/usr/bin/env python3
"""Bind the project version table to the pins the repository executes.

`tools/README.md` is the single project record for machine-local component
versions. Every version it publishes also lives in a file that a build, a
container, an editor session, or a gate reads. This module reads those files
and requires the table, and only the table, to repeat them.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "tools/README.md"
INDEX_SECTION = "## Local deployment"
REPEAT_ROOT = ROOT / "tools"

REQUIREMENTS = (
    "tools/can_dashboard/requirements-windows.txt",
    "tools/can_dashboard/requirements-macos.txt",
    "tools/can_dashboard/requirements-macos-build.txt",
)
IMAGE_SCRIPTS = (
    "tools/sh-elf-run/run.sh",
    "tools/sh-elf-run/run-npkern.sh",
    "tools/sh-elf-run/generate-targets.sh",
)


class VersionError(Exception):
    """A published version differs from the pin the repository executes."""


def _text(path):
    return (ROOT / path).read_text(encoding="utf-8")


def _single(path, pattern):
    """Read the one capture a pinning file is required to carry."""
    found = re.findall(pattern, _text(path), re.MULTILINE)
    if len(found) != 1:
        raise VersionError(
            f"{path} carries {len(found)} pins matching {pattern!r}, "
            "exactly one is required"
        )
    return found[0]


def requirement_pin(path, package):
    """Read one `package==version` pin from a requirements file."""
    return _single(
        path,
        rf"^\s*{re.escape(package)}(?:\[[^\]]*\])?==([^\s#]+)\s*$",
    )


def dashboard_version():
    return _single("tools/can_dashboard/__init__.py", r'^__version__ = "(.+)"$')


def poppler_version():
    """Read the reference release reported by the ESM extraction entry point."""
    return _single("tools/diagnostics/extract_esm.py", r'^REFERENCE_POPPLER_VERSION = "(.+)"$')


def python_can_version():
    """Read the one `python-can` pin every platform package installs."""
    pins = {path: requirement_pin(path, "python-can") for path in REQUIREMENTS}
    carried = set(pins.values())
    if len(carried) != 1:
        raise VersionError(
            "the platform packages pin different python-can versions: "
            + ", ".join(f"{path} {pin}" for path, pin in sorted(pins.items()))
        )
    return carried.pop()


def compose_tag(image):
    return _single(
        "tools/memgraph/docker-compose.yml",
        rf"^\s*image: {re.escape(image)}:(\S+)",
    )


def mcp_memgraph_version():
    """Read the version the project-scoped MCP server resolves.

    The configuration is machine-local and untracked, so a checkout without it
    leaves the row unchecked rather than failing the gate.
    """
    if not (ROOT / ".mcp.json").is_file():
        return None
    config = json.loads(_text(".mcp.json"))
    arguments = config["mcpServers"]["memgraph"]["args"]
    pins = [item for item in arguments if item.startswith("mcp-memgraph==")]
    if len(pins) != 1:
        raise VersionError(
            f".mcp.json pins mcp-memgraph {len(pins)} times, one pin is required"
        )
    return pins[0].split("==", 1)[1]


def simulator_version():
    """Read the GDB SH simulator version the execution gate demands."""
    return _single(
        "tools/sh-elf-run/verify_map_switching.py",
        r'^EXPECTED_SIMULATOR_VERSION = "(\S+)"$',
    )


def toolchain_versions():
    """Read the upstream part of the Debian pins the execution image installs.

    A Debian pin carries a packaging suffix the table does not publish, so the
    comparison uses the leading upstream version alone.
    """
    return tuple(
        _single("tools/sh-elf-run/Dockerfile", rf"^ARG {name}=(\d[\d.]*)")
        for name in ("GCC_SH_ELF_VERSION", "BINUTILS_SH_ELF_VERSION")
    )


def python_version():
    return _single("pyproject.toml", r'^requires-python = ">=(\d+\.\d+),')


COMPONENTS = (
    ("Ghidra", "tools/ghidra/headless-analyze.sh", lambda: (
        _single("tools/ghidra/headless-analyze.sh", r"^GHIDRA_VERSION=(\S+)$"),
    )),
    ("Memgraph MAGE", "tools/memgraph/docker-compose.yml", lambda: (
        compose_tag("memgraph/memgraph-mage"),
    )),
    ("Memgraph Lab", "tools/memgraph/docker-compose.yml", lambda: (
        compose_tag("memgraph/lab"),
    )),
    ("`mcp-memgraph`", ".mcp.json", lambda: tuple(
        version for version in (mcp_memgraph_version(),) if version
    )),
    ("GNU SH toolchain", "tools/sh-elf-run/", lambda: (
        *toolchain_versions(), simulator_version(),
    )),
    ("Python", "pyproject.toml", lambda: (python_version(),)),
    ("Poppler", "tools/diagnostics/extract_esm.py", lambda: (poppler_version(),)),
    ("CAN dashboard", "tools/can_dashboard/__init__.py", lambda: (
        dashboard_version(),
    )),
    ("PyInstaller", REQUIREMENTS[2], lambda: (
        requirement_pin(REQUIREMENTS[2], "pyinstaller"),
    )),
    ("`python-can`", "the platform requirements", lambda: (
        python_can_version(),
    )),
    ("`tzdata`", REQUIREMENTS[0], lambda: (
        requirement_pin(REQUIREMENTS[0], "tzdata"),
    )),
)


def published_versions():
    """Read the component and version cells the deployment table carries."""
    section = _text("tools/README.md").split(INDEX_SECTION, 1)
    if len(section) != 2:
        raise VersionError(f"tools/README.md has no {INDEX_SECTION!r} section")
    published = {}
    for line in section[1].split("\n## ", 1)[0].splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 3 or cells[0] == "Component" or set(cells[0]) <= {"-"}:
            continue
        published[cells[0]] = cells[1]
    return published


def _carries(cell, version):
    return re.search(rf"(?<![\w.]){re.escape(version)}(?![\w.])", cell) is not None


def check_index():
    """Require every published version to be the pin the repository reads."""
    published = published_versions()
    pinned = {}
    for component, source, read in COMPONENTS:
        if component not in published:
            raise VersionError(
                f"the deployment table has no {component} row"
            )
        versions = read()
        if not versions:
            continue
        for version in versions:
            if not _carries(published[component], version):
                raise VersionError(
                    f"the deployment table publishes {component} as "
                    f"'{published[component]}', {source} pins {version}"
                )
        pinned[component] = versions
    return pinned


def _split_code(text):
    """Separate prose from fenced command blocks.

    Prose is where a document publishes a version, and the table is its one
    record. A fenced block is a command an operator runs, so a version there is
    a selector that `check_launchers` holds to the same pin instead.
    """
    parts = re.split(r"\n[ \t]*```", "\n" + text)
    return "\n".join(parts[::2]), "\n".join(parts[1::2])


def _documents():
    for path in sorted(REPEAT_ROOT.rglob("*.md")):
        if path == INDEX or "node_modules" in path.parts:
            continue
        yield path, path.read_text(encoding="utf-8")


def check_repeats(pinned):
    """Require the table to be the only tool document publishing a version."""
    for path, text in _documents():
        prose, _commands = _split_code(text)
        for component, versions in pinned.items():
            for version in versions:
                if _carries(prose, version):
                    raise VersionError(
                        f"{path.relative_to(ROOT)} repeats the {component} "
                        f"version {version}; the deployment table in "
                        "tools/README.md is its one project record"
                    )


def check_execution_image():
    """Require the execution image tag to name the simulator the gate demands."""
    expected = simulator_version()
    for path in IMAGE_SCRIPTS:
        tag = _single(
            path, r"^image_name=\$\{VQ_SH_ELF_IMAGE:-vq-sh-elf-run:(\S+)\}$"
        )
        if tag != expected:
            raise VersionError(
                f"{path} runs vq-sh-elf-run:{tag}, the gate requires the "
                f"GDB SH simulator {expected}"
            )


def check_launchers():
    """Require a documented `py` launcher selector to be the pinned Python."""
    expected = python_version()
    for path, text in _documents():
        _prose, commands = _split_code(text)
        for selected in set(re.findall(r"\bpy -(\d+\.\d+)\b", commands)):
            if selected != expected:
                raise VersionError(
                    f"{path.relative_to(ROOT)} runs the launcher as "
                    f"py -{selected}, pyproject.toml requires {expected}"
                )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail when a published version differs from an executed pin",
    )
    parser.parse_args(argv)
    try:
        pinned = check_index()
        check_repeats(pinned)
        check_execution_image()
        check_launchers()
    except VersionError as error:
        print(f"version index: {error}", file=sys.stderr)
        return 1
    unchecked = len(COMPONENTS) - len(pinned)
    summary = f"version index: {len(pinned)} components match their pins"
    if unchecked:
        summary += f", {unchecked} carry no configuration on this machine"
    print(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
