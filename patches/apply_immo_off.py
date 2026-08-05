#!/usr/bin/env python3
"""One-bit ECM immo-off for supported Nissan HR ROMs.

The script reads only an exact stock ROM from rom-images/roms.csv, verifies its
SHA-256, and clears bit 0 of the factory Developer Immobilizer flag. Checksum
correction is left to the flasher.
"""

import argparse
import csv
import hashlib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROMDIR = ROOT / "rom-images"
REGISTRY = ROMDIR / "roms.csv"
MOD_RELEASE_DATE = "20260727"

PATCHES = {
    "1ND0A": {"offset": 0x8668, "stock": 0x01, "patched": 0x00},
    "1ND3B": {"offset": 0x8668, "stock": 0x01, "patched": 0x00},
    "JK78C": {"offset": 0x861C, "stock": 0x01, "patched": 0x00},
    "JK03A": {"offset": 0x8725, "stock": 0x01, "patched": 0x00},
    "JK08A": {"offset": 0x8725, "stock": 0x01, "patched": 0x00},
    "JK00D": {"offset": 0x8740, "stock": 0x01, "patched": 0x00},
}

IMAGE_IDS = {
    "1ND0A": "11ND0A",
    "1ND3B": "11ND3B",
    "JK78C": "1JK78C",
    "JK03A": "1JK03A",
    "JK08A": "1JK08A",
    "JK00D": "1JK00D",
}


class PatchError(ValueError):
    pass


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def md5(data):
    return hashlib.md5(data).hexdigest()


def default_output_path(rom):
    return ROOT / "tmp" / (
        f"{IMAGE_IDS[rom]}-{MOD_RELEASE_DATE}-immo-off.bin"
    )


def load_registry(path=REGISTRY):
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    result = {}
    for row in rows:
        rom = row["rom"]
        if not rom:
            continue
        if rom in result:
            raise PatchError(f"duplicate ROM {rom} in {path}")
        result[rom] = row
    return result


def load_stock(rom, registry=None):
    if rom not in PATCHES:
        raise PatchError(f"ROM {rom} is not supported")
    rows = registry or load_registry()
    row = rows.get(rom)
    if row is None:
        raise PatchError(f"ROM {rom} is missing from {REGISTRY}")
    path = ROMDIR / row["path"]
    data = path.read_bytes()
    actual = sha256(data)
    if actual != row["sha256"]:
        raise PatchError(
            f"{rom}: stock ROM SHA-256 is {actual}, expected {row['sha256']}"
        )
    return path, data


def patch_image(rom, source):
    cfg = PATCHES[rom]
    offset = cfg["offset"]
    if offset >= len(source):
        raise PatchError(f"{rom}: offset {offset:#x} is outside the ROM")
    actual = source[offset]
    if actual != cfg["stock"]:
        raise PatchError(
            f"{rom}: found {actual:#04x} at {offset:#x}, "
            f"expected {cfg['stock']:#04x}"
        )
    result = bytearray(source)
    result[offset] = cfg["patched"]
    return bytes(result)


def write_output(path, image):
    if path.exists():
        current = path.read_bytes()
        if current == image:
            return False
        raise PatchError(f"existing output differs: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("xb") as fh:
        fh.write(image)
    return True


def write_md5_sidecar(path, image):
    sidecar = path.with_name(path.name + ".md5")
    content = f"{md5(image)} *{path.name}\n"
    if sidecar.exists():
        current = sidecar.read_text(encoding="ascii")
        if current == content:
            return False
        raise PatchError(f"existing MD5 sidecar differs: {sidecar}")
    sidecar.write_text(content, encoding="ascii")
    return True


def write_mod_readme(path, rom, source_path, image):
    readme = path.parent / "README.md"
    if readme.exists():
        return False
    cfg = PATCHES[rom]
    release_date = (
        f"{MOD_RELEASE_DATE[:4]}-{MOD_RELEASE_DATE[4:6]}-"
        f"{MOD_RELEASE_DATE[6:]}"
    )
    content = f"""# {IMAGE_IDS[rom]} immo-off

One-bit modification for `23710-{rom}`, released on {release_date} from the exact
`../../{source_path.name}`.

## Contents

- `{path.name}` - derived flash ROM, {len(image)} bytes;
- `{path.name}.md5` - MD5 sidecar.

ROM hashes:

- SHA-256: `{sha256(image)}`;
- MD5: `{md5(image)}`.

## Change

```text
ROM[{cfg["offset"]:#010x}]: {cfg["stock"]:#04x} -> {cfg["patched"]:#04x}
```

Only bit 0 of the factory Developer Immobilizer flag changes. The derived image
differs from stock by exactly one bit. Stored checksum fields match stock; the
flasher corrects the checksums while writing.
"""
    readme.write_text(content, encoding="utf-8")
    return True


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Clear the Developer Immobilizer flag in an exact stock HR ROM"
    )
    parser.add_argument("--rom", choices=sorted(PATCHES), default="JK08A")
    parser.add_argument("--out", type=Path)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args(argv)

    source_path, source = load_stock(args.rom)
    image = patch_image(args.rom, source)
    cfg = PATCHES[args.rom]

    print(f"ROM: {args.rom}")
    print(f"source: {source_path}")
    print(
        f"patch: {cfg['offset']:#08x} "
        f"{cfg['stock']:#04x} -> {cfg['patched']:#04x}"
    )
    print(f"source sha256: {sha256(source)}")
    print(f"patched sha256: {sha256(image)}")

    if args.verify_only:
        return 0

    output = args.out or default_output_path(args.rom)
    created = write_output(output, image)
    write_md5_sidecar(output, image)
    print(f"output: {output} ({'created' if created else 'already exact'})")
    print(f"md5: {md5(image)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
