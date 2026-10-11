"""Repository paths, the image catalog, the layouts, and the kb configuration."""

from collections import OrderedDict
from dataclasses import dataclass
import csv
import hashlib
from pathlib import Path
import pickle
import re
from threading import Lock
import tomllib

ROOT = Path(__file__).resolve().parents[4]
CATALOG = Path("rom-images/roms.csv")
HOMOLOGY = Path("rom-images/homology.toml")
CONFIG = Path("tools/kb/config.toml")
OWNER_CONFIG = Path("tools/kb/owners.toml")
GHIDRA_PIN = Path("tools/ghidra/headless-analyze.sh")
GHIDRA_SCRIPTS = Path("tools/ghidra")
L0 = Path("l0")
STATE = Path(".kb")


class _ConfigurationDocuments:
    """Bounded immutable preparation of exact configuration text.

    Readers still select and read their sources on every call. Each result
    is separate, and owner validation executes after preparation. The budget
    counts UTF-8 source bytes and serialized documents, not object overhead.
    """

    def __init__(self, parser=tomllib.loads, capacity=64 << 20):
        self.parser = parser
        self.capacity = capacity
        self.entries = OrderedDict()
        self.bytes = 0
        self.lock = Lock()

    def loads(self, text):
        if type(text) is not str:
            return self.parser(text)
        with self.lock:
            held = self.entries.get(text)
            if held is not None:
                self.entries.move_to_end(text)
        if held is not None:
            return pickle.loads(held[0])
        document = self.parser(text)
        try:
            packed = pickle.dumps(document, protocol=pickle.HIGHEST_PROTOCOL)
        except (pickle.PicklingError, TypeError, RecursionError):
            return document
        try:
            size = len(text.encode('utf-8')) + len(packed)
        except UnicodeError:
            return document
        if size <= self.capacity:
            with self.lock:
                if text not in self.entries:
                    while self.entries and self.bytes + size > self.capacity:
                        _, (_, removed) = self.entries.popitem(last=False)
                        self.bytes -= removed
                    self.entries[text] = packed, size
                    self.bytes += size
                self.entries.move_to_end(text)
        return document


_CONFIG_DOCUMENTS = _ConfigurationDocuments()


def _configuration_document(text):
    # A supplied parser owns its preparation and must execute on every call.
    if tomllib.loads is not _CONFIG_DOCUMENTS.parser:
        return tomllib.loads(text)
    return _CONFIG_DOCUMENTS.loads(text)


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


def layouts(root=ROOT, overlay=None):
    """Return {layout id: Layout} in canonical order, from the family registry."""
    text = (overlay or {}).get(HOMOLOGY)
    if text is None:
        text = (root / HOMOLOGY).read_text(encoding="utf-8")
    document = tomllib.loads(text)
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


def config(root=ROOT, overlay=None):
    """Execution settings plus narrowly scoped knowledge-owner declarations."""
    overlay = overlay or {}
    text = overlay.get(CONFIG)
    if text is None:
        text = (root / CONFIG).read_text(encoding="utf-8")
    document = _configuration_document(text)
    if OWNER_CONFIG in overlay:
        owner_text = overlay[OWNER_CONFIG]
    elif (root / OWNER_CONFIG).is_file():
        owner_text = (root / OWNER_CONFIG).read_text(encoding="utf-8")
    else:
        owner_text = None
    if owner_text is not None:
        owners = _configuration_document(owner_text)
        if (set(owners) != {'schema_version', 'names', 'reconciliation', 'source_bindings'}
                or type(owners['schema_version']) is not int or owners['schema_version'] != 1
                or not isinstance(owners['names'], dict)
                or set(owners['names']) != {'owners_checked', 'reserved'}
                or owners['names']['owners_checked'] is not True
                or not isinstance(owners['names']['reserved'], list)
                or any(not isinstance(owners[key], dict)
                       or set(owners[key]) != {'enabled', 'review'}
                       or owners[key]['enabled'] is not True
                       or not isinstance(owners[key]['review'], list)
                       for key in ('reconciliation', 'source_bindings'))):
            raise KbError(f'{OWNER_CONFIG}: only name ownership and source-bound reviews are allowed')
        document.setdefault('names', {}).update(owners['names'])
        document['reconciliation'] = owners['reconciliation']
        document['source_bindings'] = owners['source_bindings']
    return document


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
