#!/usr/bin/env python3
"""Validate machine version pins and execution and packaging bindings."""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

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
    """Machine configuration and the executable consumer disagree."""


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
    has no optional server pin to validate.
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
    """Read upstream versions from the execution image's Debian package pins."""
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
    """Check the generated installer and the build tool the packager invokes."""
    from tools.can_dashboard import package_macos, package_windows

    expected = python_version()
    selected = set(re.findall(r"\bpy -(\d+\.\d+)\b", package_windows.INSTALL_CMD))
    if selected != {expected}:
        raise VersionError(
            f"the Windows installer selects Python {sorted(selected)}, "
            f"pyproject.toml requires {expected}"
        )
    expected_pyinstaller = requirement_pin(package_macos.BUILD_REQUIREMENTS, "pyinstaller")
    if package_macos.PYINSTALLER_VERSION != expected_pyinstaller:
        raise VersionError(
            f"the macOS packager requires PyInstaller {package_macos.PYINSTALLER_VERSION}, "
            f"{package_macos.BUILD_REQUIREMENTS} pins {expected_pyinstaller}"
        )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate machine version pins and executable consumers",
    )
    parser.parse_args(argv)
    try:
        for _component, _source, read in COMPONENTS:
            read()
        check_execution_image()
        check_launchers()
    except VersionError as error:
        print(f"version index: {error}", file=sys.stderr)
        return 1
    print("version pins: machine configuration and execution bindings match")
    return 0


if __name__ == "__main__":
    sys.exit(main())
