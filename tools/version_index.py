#!/usr/bin/env python3
"""Check execution image tags and provide packaging version readers."""

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

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


def simulator_version():
    """Read the GDB SH simulator version the execution gate demands."""
    return _single(
        "tools/sh-elf-run/verify_map_switching.py",
        r'^EXPECTED_SIMULATOR_VERSION = "(\S+)"$',
    )


def python_version():
    return _single("pyproject.toml", r'^requires-python = ">=(\d+\.\d+),')


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


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate execution image tags against the simulator version",
    )
    parser.parse_args(argv)
    try:
        check_execution_image()
    except VersionError as error:
        print(f"version index: {error}", file=sys.stderr)
        return 1
    print("version pins: execution image tags match the simulator")
    return 0


if __name__ == "__main__":
    sys.exit(main())
