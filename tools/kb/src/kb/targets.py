"""The feature targets and the symbols of their meanings, read from the entity
files without compiling the model (tools/kb/SPEC.md, section 20.3).

`patches/runtime_targets.py` relocates the canonical runtime, whose sources
and layouts use `7mfk` addresses, onto every other layout. It takes here the
`7mfk` values of the key tables of the feature targets, the per-layout keys
of the hooks of a target by their `7mfk` words, the keys of a target, the
meaning that fills a key on a layout, and the named bits that its payloads
test.
The functions read only the files they name and use only the standard
library and the modules of this package that do, since the firmware gate
imports them with the Python of its container.
"""

from kb import repo, store
from kb.repo import KbError

CANONICAL = "7mfk"
# The keys of a target that hold numbers, not symbols.
NUMBERS = ("mailbox_index", "mailbox_mask")
# The record words of `can_telemetry`: the image bytes at the symbol of a key.
RECORD_WORDS = {"feedback_config_record_value": "feedback_config_record_address",
                "mailbox_record_stock": "mailbox_record_address",
                "occupied_mailbox_record_stock": "occupied_mailbox_record_address"}


def _document(kind, name, root, overlay):
    path = store.path_of(kind, name)
    if (overlay[path] is None if overlay and path in overlay
            else not (root / path).is_file()):
        raise KbError(f"{path.as_posix()}: no entity file", code=3)
    return store.load(root, path, overlay)


def _symbols(ref, layout, root, overlay):
    name, _, kind = ref.rpartition("/")
    return [entry for entry in _document(kind, name, root, overlay).get("symbol", ())
            if entry.get("layout") == layout]


def layout_of(image, root=repo.ROOT):
    """The layout of an image."""
    found = [layout.id for layout in repo.layouts(root).values() if image in layout.images]
    if len(found) != 1:
        raise KbError(f"image {image}: {len(found)} layouts", code=5)
    return found[0]


def target(feature, layout, root=repo.ROOT, overlay=None):
    """The `[[target]]` table of a feature on a layout."""
    found = [entry for entry in _document("feature", feature, root, overlay).get("target", ())
             if entry.get("layout") == layout]
    if len(found) != 1:
        raise KbError(f"{feature}: {len(found)} targets on {layout}", code=3)
    return found[0]


def symbol(ref, layout, root=repo.ROOT, overlay=None):
    """The symbol entry on a layout of the meaning `<name>/<kind>`."""
    found = _symbols(ref, layout, root, overlay)
    if len(found) != 1:
        raise KbError(f"{ref}: {len(found)} symbols on {layout}", code=3)
    return found[0]


def address(ref, layout, root=repo.ROOT, overlay=None):
    return int(symbol(ref, layout, root, overlay)["address"], 16)


def meaning(feature, layout, key, root=repo.ROOT, overlay=None):
    """The meaning that fills a key of the target of a feature on a layout:
    that of the key in `symbols`, or else that of its role."""
    held = target(feature, layout, root, overlay)
    if key in held.get("symbols", {}):
        return held["symbols"][key]
    role = held.get("roles", {}).get(key)
    if role is None:
        raise KbError(f"{feature}: no key {key} on {layout}", code=3)
    return role["symbol"]


def bit(ref, layout, name, root=repo.ROOT, overlay=None):
    """The number of the named bit `name` of the meaning `<name>/<kind>` on a
    layout: that of the `[[bit]]` of its symbol entry, which replaces the bits
    of the meaning on the layout, or else that of the meaning."""
    meaning, _, kind = ref.rpartition("/")
    document = _document(kind, meaning, root, overlay)
    entries = [entry for entry in document.get("symbol", ()) if entry.get("layout") == layout]
    if len(entries) != 1:
        raise KbError(f"{ref}: {len(entries)} symbols on {layout}", code=3)
    found = [item.get("bit") for item in entries[0].get("bit", document.get("bit", ()))
             if item.get("name") == name]
    if len(found) != 1:
        raise KbError(f"{ref}: {len(found)} bits {name} on {layout}", code=3)
    return found[0]


def record_word(ref, layout, root=repo.ROOT, overlay=None):
    """The word that the `rom-bytes` identity item of a symbol states at its
    address."""
    entry = symbol(ref, layout, root, overlay)
    at = f"{layout}:{entry['address']}"
    values = {item.get("value") for item in entry.get("evidence", ())
              if item.get("kind") == "rom-bytes"
              and item.get("supports", "identity") == "identity" and item.get("at") == at}
    if len(values) != 1:
        raise KbError(f"{ref}: {len(values)} image-byte words at {at}", code=3)
    return int(values.pop(), 16)


def canonical_symbols(feature, root=repo.ROOT, overlay=None):
    """{key: value} of the `7mfk` target of a feature: the address of the
    symbol of each key of `symbols`, the numbers, and the record words."""
    held = target(feature, CANONICAL, root, overlay)
    symbols = held.get("symbols", {})
    found = {key: address(ref, CANONICAL, root, overlay) for key, ref in symbols.items()}
    found.update((key, held[key]) for key in NUMBERS if key in held)
    found.update((key, record_word(symbols[record], CANONICAL, root, overlay))
                 for key, record in RECORD_WORDS.items() if record in symbols)
    return found


def hook_keys(feature, layout, root=repo.ROOT, overlay=None):
    """{`7mfk` word: key} of the hooks of the target of a feature on a layout
    whose meaning has a `7mfk` symbol."""
    found = {}
    for key, entry in target(feature, layout, root, overlay).get("hooks", {}).items():
        held = _symbols(entry["hook"], CANONICAL, root, overlay)
        if held:
            found[int(held[0]["address"], 16)] = key
    return found
