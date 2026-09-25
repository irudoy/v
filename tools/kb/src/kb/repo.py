"""Repository paths, the image catalog, the layouts, and the kb configuration."""

from dataclasses import dataclass
import csv
import hashlib
from pathlib import Path
import re
import tomllib

ROOT = Path(__file__).resolve().parents[4]
CATALOG = Path("rom-images/roms.csv")
HOMOLOGY = Path("rom-images/homology.toml")
CONFIG = Path("tools/kb/config.toml")
GHIDRA_PIN = Path("tools/ghidra/headless-analyze.sh")
GHIDRA_SCRIPTS = Path("tools/ghidra")
L0 = Path("l0")
STATE = Path(".kb")


class KbError(Exception):
    """A usage or data error that a command reports with its exit code."""

    def __init__(self, message, code=1):
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class Image:
    rom: str
    path: Path
    sha256: str


@dataclass(frozen=True)
class Layout:
    id: str
    family: str
    kind: str
    mcu: str
    image: str
    images: tuple


def images(root=ROOT):
    """Return {ROM key: Image} of the image catalog."""
    with (root / CATALOG).open(newline="", encoding="utf-8") as source:
        return {
            row["rom"]: Image(row["rom"], root / "rom-images" / row["path"], row["sha256"])
            for row in csv.DictReader(source)
        }


def layouts(root=ROOT):
    """Return {layout id: Layout} in canonical order, from the family registry."""
    document = tomllib.loads((root / HOMOLOGY).read_text(encoding="utf-8"))
    found = {}
    for family, row in document["family"].items():
        for layout, image in row["layouts"].items():
            members = tuple(row["members"]) if row["same_address_inheritance"] else (image,)
            found[layout] = Layout(layout, family, row["kind"], row["mcu"], image, members)
    return dict(sorted(found.items()))


def layout(layout_id, root=ROOT):
    known = layouts(root)
    if layout_id not in known:
        raise KbError(
            f"unknown layout {layout_id!r}; layouts: {', '.join(known)}", code=5
        )
    return known[layout_id]


def config(root=ROOT):
    return tomllib.loads((root / CONFIG).read_text(encoding="utf-8"))


def signatures(layout_id, root=ROOT):
    """{function entry: (size, SHA-256 of its exact bytes)} from the L0 of a layout."""
    path = root / L0 / layout_id / "function_signatures.csv"
    with path.open(newline="", encoding="utf-8") as source:
        return {int(row["addr"], 16): (int(row["size"]), row["exact_sha256"])
                for row in csv.DictReader(source)}


def ghidra_version(root=ROOT):
    """The Ghidra release that the headless wrapper pins."""
    found = re.findall(
        r"^GHIDRA_VERSION=(\S+)$", (root / GHIDRA_PIN).read_text(encoding="utf-8"), re.M
    )
    if len(found) != 1:
        raise KbError(f"{GHIDRA_PIN}: expected one GHIDRA_VERSION pin")
    return found[0]


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()
