"""Resolve the Ghidra program that holds a registered stock ROM.

A program keeps the file name it was imported under, which need not be the
file name of the registered stock image. The project index lists the stored
names; the executable SHA-256 that Ghidra records at import binds the chosen
program to the registered image.

Usage:
    python -m tools.ghidra.program_name ROM [--project-dir DIR]
        [--project-name NAME] [--program PROGRAM]

Prints "<program>\t<sha256 of the registered image>".
"""
import argparse
import hashlib
import os
import re
import sys
from pathlib import Path

_ENTRY = re.compile(r"^  [0-9a-fA-F]{8}:(?P<name>.*):[^:]*$")


def root_programs(index_text):
    """Program names stored in the root folder of a Ghidra project index."""
    names = []
    folder = None
    for line in index_text.splitlines():
        if line.startswith("/"):
            folder = line.strip()
            continue
        match = _ENTRY.match(line)
        if match and folder == "/":
            names.append(match.group("name"))
    return names


def resolve(rom_key, image_name, programs):
    """Pick the program of `rom_key` among the stored program names.

    The file name of the registered image wins. Otherwise the only program
    whose name contains the ROM key is taken. `programs=None` stands for an
    unreadable index and keeps the image file name.
    """
    if programs is None or image_name in programs:
        return image_name
    candidates = [name for name in programs if rom_key in name]
    if len(candidates) == 1:
        return candidates[0]
    listed = ", ".join(sorted(programs)) or "none"
    reason = "several programs match" if candidates else "no program matches"
    raise LookupError(
        f"{reason} ROM {rom_key} (registered image {image_name}); "
        f"programs in the project: {listed}; select one with -p"
    )


def read_index(project_dir, project_name):
    index = Path(project_dir) / f"{project_name}.rep" / "idata" / "~index.dat"
    try:
        return root_programs(index.read_text())
    except OSError:
        return None


def main(argv=None):
    from tools.mapkit import rom

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("rom")
    parser.add_argument("--project-dir",
                        default=os.path.expanduser("~/tools/ghidra-projects"))
    parser.add_argument("--project-name", default="vq-hr")
    parser.add_argument("--program", default="")
    args = parser.parse_args(argv)

    image = rom.load(args.rom)
    sha256 = hashlib.sha256(bytes(image.data)).hexdigest()
    try:
        program = args.program or resolve(
            args.rom, os.path.basename(image.path),
            read_index(args.project_dir, args.project_name))
    except LookupError as error:
        print(error, file=sys.stderr)
        return 1
    print(f"{program}\t{sha256}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
