"""The service 0x22 table of the canonical layout (tools/kb/SPEC.md, section
20.5).

- `tools/diagnostics/sid22_inventory.py` decodes the DID tables of the JK08A
  image, whose publisher, table extents, and digests it fixes. Every other
  image of `7mfk` must decode to the same table.
- Each DID that the table declares gives the `did` symbol of `7mfk` at its
  table slot, in the meaning of its number, with `number`, `width` (the
  response length in bytes), and `did-table` evidence of the pointer words of
  the slot, which ground the level `code`.
- Each byte source gives a `source` link to the datum at its address. A DID
  that assembles its response from single bytes gives each link the position
  of its byte in the response as `offset`.
"""

from collections import defaultdict
import importlib.util
from pathlib import Path
import sys

from kb import repo

DECODER = Path("tools/diagnostics/sid22_inventory.py")
CANONICAL = "7mfk"
SOURCE_KINDS = ("ram", "reg", "tbl", "const")
ASSEMBLED = "paired"
SENTINEL = "ffffffff"
DYNAMIC = ("The publisher builds the response in a dedicated branch; the table slot holds "
           f"{SENTINEL}.")


def inputs(root):
    return [DECODER.as_posix()]


def _decoder(root):
    name = "kb_sid22_inventory"
    spec = importlib.util.spec_from_file_location(name, root / DECODER)
    module = importlib.util.module_from_spec(spec)
    # The dataclasses of the module resolve their annotations through sys.modules.
    sys.modules[name] = module
    try:
        spec.loader.exec_module(module)
    finally:
        sys.modules.pop(name, None)
    return module


def declare(b, root):
    src = DECODER.as_posix()
    catalog = repo.images(root)
    layout = b.layouts[CANONICAL]
    decoder = _decoder(root)
    try:
        entries = decoder.read_inventory(catalog[layout.image].path)
    except ValueError as error:
        b.issue("schema", src, layout.image, str(error))
        return
    for rom in layout.images:
        if rom == layout.image:
            continue
        other = decoder.build_inventory(catalog[rom].path.read_bytes())
        differ = sorted({entry.did for entry in set(other) ^ set(entries)})
        if differ:
            b.issue("audit", src, rom, f"the service 0x22 table differs from {layout.image} "
                    f"at DID {', '.join(f'{did:04x}' for did in differ)}")
    pending = []
    for entry in entries:
        group = ("did", "number", entry.did)
        words = " ".join(f"{source:08x}" for source in entry.sources) or SENTINEL
        key = b.symbol(CANONICAL, "did", entry.record_address, src, group=group, evidence=[{
            "kind": "did-table", "supports": "identity",
            "at": f"{CANONICAL}:{entry.record_address:08x}", "value": words}])
        b.props(group, {"number": entry.did, "width": entry.width, "level": "code"}, src)
        if not entry.sources:
            b.props(group, {"note": DYNAMIC}, src)
        assembled = entry.source_layout == ASSEMBLED
        pending.extend((key, entry.did, source, offset if assembled else None)
                       for offset, source in enumerate(entry.sources))
    b.stash["dids"] = pending


def relate(b, root):
    """Link each DID to its sources; `did_sources` of the stash gives the DIDs
    that return each source symbol."""
    src = DECODER.as_posix()
    returned = b.stash.setdefault("did_sources", defaultdict(set))
    for key, number, address, offset in b.stash.get("dids", ()):
        to = b.resolve(CANONICAL, address, SOURCE_KINDS, src)
        if to is None:
            b.issue("references", src, key.key,
                    f"source {address:08x} is no datum address of {CANONICAL}")
            continue
        b.link(key, "source", to, src, props={} if offset is None else {"offset": offset})
        returned[to].add(number)
