"""The canonical feature layouts (tools/kb/SPEC.md, sections 7.9 and 20.3),
which own the patch design of `7mfk`.

- The `[[hook]]` entries of `patches/map-switching-layout.toml`,
  `patches/rolling-launch-layout.toml`, and `patches/can-telemetry-layout.toml`
  give the `7mfk` hook words and, under the canonical keys of their features,
  their replacements in the `7mfk` targets. The features apply in that order:
  a later feature redirects the replacement of an earlier one, the stock of the
  first feature is the stock word, and its key names the word.
- The `[[family]]` entries of the map layout give the `7mfk` tables of the map
  families under their keys, which enter `families` of the `7mfk` target of
  `map_switching`.
- The payload offset of the `[feedback]` record of the map layout is
  `feedback_payload_offset` of the `7mfk` target of `can_telemetry`, as the
  address profiles state it on the other layouts.
- The `[[diagnostic]]` entries of the rolling layout give the `7mfk` DID slots
  with `number` and the allocations of the `rolling_launch` target.
- A hook word links to the meaning at its stock value with `target`.

The address profiles state the same facts of the other layouts with the
helpers of this module.
"""

from dataclasses import dataclass
from pathlib import Path
import tomllib

from kb.values import hexed

LAYOUTS = {
    "map_switching": Path("patches/map-switching-layout.toml"),
    "rolling_launch": Path("patches/rolling-launch-layout.toml"),
    "can_telemetry": Path("patches/can-telemetry-layout.toml"),
}
CANONICAL = "7mfk"
# Features in build order: a later feature redirects the replacement of an
# earlier one, and the first feature's key names a word without canonical key.
FEATURES = tuple(LAYOUTS)
HOOK_WIDTH = 32


@dataclass
class Hook:
    """One feature's redirection of a ROM word. `base` is the word before the
    feature redirects it; `stock` is the stock word where the registry states
    it."""

    layout: str
    address: int
    feature: str
    key: str
    canonical: str | None
    stock: int | None
    base: int
    replacement: int
    src: str


def inputs(root):
    return [path.as_posix() for path in LAYOUTS.values()]


def documents(root):
    """{feature: document} of the canonical feature layouts."""
    return {feature: tomllib.loads((root / path).read_text(encoding="utf-8"))
            for feature, path in LAYOUTS.items()}


def canonical_hooks(found):
    """The `7mfk` hooks of the layout documents `found`: the first feature
    states the stock word, and its key is the canonical key of the word."""
    hooks = []
    for feature, document in found.items():
        src = LAYOUTS[feature].as_posix()
        first = feature == FEATURES[0]
        for entry in document.get("hook", ()):
            hooks.append(Hook(CANONICAL, entry["address"], feature, entry["key"],
                              entry["key"] if first else None,
                              entry["stock"] if first else None, entry["stock"],
                              entry["replacement"], src))
    return hooks


def canonical_keys(found):
    """The canonical keys of the map hooks."""
    return {entry["key"] for entry in found["map_switching"].get("hook", ())}


def words(hooks):
    """{(layout, address): hooks} in build order."""
    found = {}
    for hook in hooks:
        found.setdefault((hook.layout, hook.address), []).append(hook)
    for chain in found.values():
        chain.sort(key=lambda hook: FEATURES.index(hook.feature))
    return found


def declare_words(b, found, targets, canonical):
    """The `hook` symbols of the words `found` in the groups of their keys,
    and their keys and replacements in `targets[(feature, layout)]["hooks"]`.
    `canonical` holds the canonical keys of the map hooks: a per-layout key
    that equals the canonical key of another word gives no name."""
    for (layout, address), hooks in sorted(found.items()):
        before = hooks[0].base
        first = hooks[0]
        for hook in hooks:
            if hook.stock is not None and hook.stock != first.base:
                b.issue("audit", hook.src, f"{hook.feature} {hook.key}@{layout}",
                        f"stock {hook.stock:08x} disagrees with {first.base:08x} of "
                        f"{first.feature} {first.key}")
            if hook.base != before:
                b.issue("audit", hook.src, f"{hook.feature} {hook.key}@{layout}",
                        f"base {hook.base:08x} is not {before:08x}, the word before "
                        f"{hook.feature} redirects it")
            before = hook.replacement
            if hook.feature == FEATURES[0]:
                group = (("hook", hook.feature, hook.canonical) if hook.canonical
                         else ("hook", hook.feature, "own", hook.key))
            else:
                group = ("hook", hook.feature, hook.key)
            key = b.symbol(layout, "hook", address, hook.src, group=group)
            b.props(key, {"width": HOOK_WIDTH}, hook.src)
            targets.setdefault((hook.feature, layout), {}).setdefault("hooks", {})[hook.key] = {
                "hook": key, "replacement": hexed(hook.replacement)}
        # The canonical key of the first feature names the word, or else its
        # own key unless that is the canonical key of another word.
        name = first.canonical or first.key
        if first.canonical or first.key not in canonical:
            b.name(key, name, "hook", first.src, rank=FEATURES.index(first.feature))


def declare_dids(b, entries, targets):
    """The `did` symbols of `entries` [(layout, name, did, pointer, target,
    width, src)] in the groups of their numbers, and their allocations in the
    `rolling_launch` targets."""
    for layout, name, did, pointer, target, width, src in entries:
        group = ("did", "number", did)
        key = b.symbol(layout, "did", pointer, src, group=group)
        b.props(group, {"number": did}, src)
        allocations = targets.setdefault(("rolling_launch", layout), {}).setdefault(
            "allocations", {})
        allocations[name] = {"address": hexed(target), "width": width, "did": key}


def link_words(b, found):
    """A `target` link from each word to the meaning at its stock value."""
    for (layout, address), hooks in sorted(found.items()):
        first = hooks[0]
        key = b.symbol(layout, "hook", address, first.src)
        to = b.resolve(layout, first.base, ("fn", "tbl", "const"), first.src)
        if to is None:
            b.issue("references", first.src, key.key,
                    f"stock {first.base:08x} is no ROM function, table, or constant")
            continue
        b.link(key, "target", to, first.src)


def declare(b, root):
    found = documents(root)
    chains = words(canonical_hooks(found))
    b.stash[__name__] = chains
    targets = {}
    declare_words(b, chains, targets, canonical_keys(found))
    src = LAYOUTS["rolling_launch"].as_posix()
    declare_dids(b, [(CANONICAL, entry["name"], entry["did"], entry["pointer_address"],
                      entry["target"], entry["width"], src)
                     for entry in found["rolling_launch"].get("diagnostic", ())], targets)
    src = LAYOUTS["map_switching"].as_posix()
    families = targets.setdefault(("map_switching", CANONICAL), {}).setdefault("families", {})
    for family in found["map_switching"].get("family", ()):
        group = ("tbl", "key", family["key"])
        families[family["key"]] = b.symbol(CANONICAL, "tbl", family["canonical_address"], src,
                                           group=group)
        b.name(group, family["key"], "symbol_key", src)
    for feature in FEATURES:
        b.entity("feature", feature, LAYOUTS[feature].as_posix())
        props = targets.get((feature, CANONICAL), {})
        b.target(feature, CANONICAL, LAYOUTS[feature].as_posix(), status="supported",
                 props=props)
    feedback = found["map_switching"].get("feedback", {})
    if "payload_offset" in feedback:
        b.target("can_telemetry", CANONICAL, src,
                 props={"feedback_payload_offset": feedback["payload_offset"]})


def relate(b, root):
    chains = b.stash.get(__name__)
    if chains is not None:
        link_words(b, chains)
