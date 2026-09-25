"""Address profiles, runtime correspondence, and the canonical feature layouts
(tools/kb/SPEC.md, sections 20.1 and 20.3).

- The symbol tables of `patches/runtime_targets.py` give the `7mfk` symbols of
  their keys, and its hook-key tables join the per-layout keys of a map hook to
  its canonical key. The module is read with `ast`, not imported.
- The `[[hook]]` entries of the canonical feature layouts give the `7mfk` words
  of the canonical hook keys, the `[[family]]` entries of the map layout the
  `7mfk` tables of the map families, and the `[[diagnostic]]` entries of the
  rolling layout the `7mfk` DID slots.
- Each image profile of `patches/rom-address-profiles.toml` gives the symbols
  of its layout: a symbol-table key names the meaning at its address, a
  telemetry source the source meaning of its field, and a hook the ROM word
  that its features redirect. The other keys go to the targets of `runtime`,
  `map_switching`, `rolling_launch`, and `can_telemetry`.
- A row of `patches/<layout>-runtime-correspondence.csv` joins its target
  symbol to the meaning of its source symbol, and an `unsupported` row gives a
  status.
"""

import ast
from collections import defaultdict
import csv
from dataclasses import dataclass
from pathlib import Path
import re
import tomllib

PROFILES = Path("patches/rom-address-profiles.toml")
RUNTIME_TARGETS = Path("patches/runtime_targets.py")
FEATURE_LAYOUTS = {
    "map_switching": Path("patches/map-switching-layout.toml"),
    "rolling_launch": Path("patches/rolling-launch-layout.toml"),
    "can_telemetry": Path("patches/can-telemetry-layout.toml"),
}
PATCHES = Path("patches")
CORRESPONDENCE = "*-runtime-correspondence.csv"
CANONICAL = "7mfk"
# Features in build order: a later feature redirects the replacement of an
# earlier one, and the first feature's key names a word without canonical key.
FEATURES = ("map_switching", "rolling_launch", "can_telemetry")
RUNTIME = "runtime"
HOOK_TABLES = {"map_hooks": "map_switching", "rolling_hooks": "rolling_launch",
               "can_hooks": "can_telemetry"}
SYMBOL_TABLES = ("map_families", "map_symbols", "rolling_symbols", "can_symbols")
CANONICAL_TABLES = {"CANONICAL_MAP_SYMBOLS": "map_symbols",
                    "CANONICAL_ROLLING_SYMBOLS": "rolling_symbols",
                    "CANONICAL_CAN_SYMBOLS": "can_symbols"}
TEMPLATE = "IGNITION_STATE_TEMPLATE"
HOOK_KEYS = {"dual-cvtc": "MAP_HOOK_KEYS"}
VQ37_HOOK_KEYS = "VQ37_MAP_HOOK_KEYS"
# `can_symbols` keys whose values are no addresses: the image bytes at the
# address of another key, and keys of the `can_telemetry` target.
ROM_BYTES = {"feedback_config_record_value": "feedback_config_record_address",
             "mailbox_record_stock": "mailbox_record_address",
             "occupied_mailbox_record_stock": "occupied_mailbox_record_address"}
CAN_KEYS = ("mailbox_index", "mailbox_mask", "feedback_payload_offset")
RUNTIME_KEYS = ("rom_size", "rom_delta", "ram_delta", "free_rom_start", "free_rom_end",
                "injected_rom_start", "injected_rom_end", "free_ram_start", "free_ram_end",
                "injected_ram_start", "injected_ram_end", "map_variant",
                "telemetry_completion_variant", "telemetry_zero_source",
                "ignition_unreferenced_routine")
MAP_KEYS = ("ascd_enabled_mask", "extra_cvtc_storage", "ignition_state_storage")
DERIVED = ("family", "layout_source", "inherits")
OTHER_KEYS = ("capabilities", "rolling_diagnostics", "telemetry_sources",
              "telemetry_unavailable", "evidence")
EVIDENCE = {"free_rom": RUNTIME, "free_ram": RUNTIME, "maps": "map_switching",
            "rolling": "rolling_launch", "can": "can_telemetry", "telemetry": "can_telemetry"}
DOMAIN_FEATURE = {"map": "map_switching", "map_native": "map_switching",
                  "map_symbol": "map_switching", "map_hook": "map_switching",
                  "rolling_symbol": "rolling_launch", "rolling_hook": "rolling_launch",
                  "can_symbol": "can_telemetry", "can_hook": "can_telemetry",
                  "telemetry": "can_telemetry", "allocation": RUNTIME}
HOOK_DOMAINS = ("map_hook", "rolling_hook", "can_hook")
SYMBOL_DOMAINS = ("map_symbol", "rolling_symbol", "can_symbol")
MAP_DOMAINS = ("map", "map_native")
# Kinds that a symbol-table key takes from the symbols that registries place
# at its addresses, in precedence order.
KIND_ORDER = ("hook", "fn", "tbl", "axis", "const", "did", "dtc", "ram", "reg")
# Evidence that a search found no symbol states `unresolved`; other evidence of
# an unsupported entry states that the mechanism is `absent`.
UNRESOLVED = re.compile(r"\bno homolog\b|\bnot traced\b|\bno match\b", re.IGNORECASE)
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
    found = [PROFILES.as_posix(), RUNTIME_TARGETS.as_posix()]
    found += [path.as_posix() for path in FEATURE_LAYOUTS.values()]
    found += [path.relative_to(root).as_posix()
              for path in sorted((root / PATCHES).glob(CORRESPONDENCE))]
    return found


def runtime_tables(root):
    """The literal tables of `patches/runtime_targets.py` by name."""
    wanted = {*CANONICAL_TABLES, *HOOK_KEYS.values(), VQ37_HOOK_KEYS, TEMPLATE}
    found = {}
    tree = ast.parse((root / RUNTIME_TARGETS).read_text(encoding="utf-8"))
    for node in tree.body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name) and node.targets[0].id in wanted):
            found[node.targets[0].id] = ast.literal_eval(node.value)
    return found


def correspondence(root):
    """{layout: (path, rows)} of the correspondence files."""
    found = {}
    for path in sorted((root / PATCHES).glob(CORRESPONDENCE)):
        layout = path.name.removesuffix(CORRESPONDENCE[1:])
        with path.open(newline="", encoding="utf-8") as source:
            found[layout] = (path.relative_to(root).as_posix(), list(csv.DictReader(source)))
    return found


def _hex(text):
    return int(text, 16) if text else None


def _state(text):
    return "unresolved" if UNRESOLVED.search(text or "") else "absent"


class Profiles:
    """The facts of the registries of this adapter, before they enter the model."""

    def __init__(self, b, root):
        self.tables = runtime_tables(root)
        self.document = tomllib.loads((root / PROFILES).read_text(encoding="utf-8"))
        self.layouts_doc = {feature: tomllib.loads((root / path).read_text(encoding="utf-8"))
                            for feature, path in FEATURE_LAYOUTS.items()}
        self.rows = correspondence(root)
        by_image = {image: layout.id for layout in b.layouts.values() for image in layout.images}
        self.profiles = {}
        src = PROFILES.as_posix()
        for rom, profile in self.document.get("profile", {}).items():
            layout = by_image.get(rom)
            if layout is None:
                b.issue("schema", src, f"profile.{rom}", "an image outside every layout")
                continue
            if "inherits" in profile:
                if by_image.get(profile["inherits"]) != layout or len(profile) != 1:
                    b.issue("schema", src, f"profile.{rom}",
                            f"inherits {profile['inherits']} across layouts or with keys")
                continue
            if layout in self.profiles:
                b.issue("schema", src, f"profile.{rom}",
                        f"a second profile of layout {layout}")
                continue
            unknown = sorted(set(profile) - {*RUNTIME_KEYS, *MAP_KEYS, *DERIVED, *OTHER_KEYS,
                                               *HOOK_TABLES, *SYMBOL_TABLES})
            if unknown:
                b.issue("schema", src, f"profile.{rom}", f"unknown keys {', '.join(unknown)}")
            self.profiles[layout] = (rom, profile)
        self.canonical_map_keys = {hook["key"] for hook in
                                   self.layouts_doc["map_switching"].get("hook", ())}
        self.hooks = self._hooks()
        self.words = defaultdict(list)
        for hook in self.hooks:
            self.words[(hook.layout, hook.address)].append(hook)
        for hooks in self.words.values():
            hooks.sort(key=lambda hook: FEATURES.index(hook.feature))

    def hook_keys(self, profile):
        """{per-layout key: canonical key} of the map hooks of a profile."""
        table = HOOK_KEYS.get(profile.get("map_variant"), VQ37_HOOK_KEYS)
        return {value: key for key, value in self.tables[table].items()}

    def _hooks(self):
        found = []
        for feature, document in self.layouts_doc.items():
            src = FEATURE_LAYOUTS[feature].as_posix()
            for entry in document.get("hook", ()):
                stock = entry["stock"] if feature == FEATURES[0] else None
                found.append(Hook(CANONICAL, entry["address"], feature, entry["key"],
                                  entry["key"] if feature == FEATURES[0] else None,
                                  stock, entry["stock"], entry["replacement"], src))
        src = PROFILES.as_posix()
        for layout, (rom, profile) in self.profiles.items():
            canonical = self.hook_keys(profile)
            for table, feature in HOOK_TABLES.items():
                for key, values in profile.get(table, {}).items():
                    if feature == FEATURES[0]:
                        address, stock, replacement = values
                        found.append(Hook(layout, address, feature, key, canonical.get(key),
                                          stock, stock, replacement, src))
                    else:
                        address, stock, base, replacement = values
                        found.append(Hook(layout, address, feature, key, None, stock, base,
                                          replacement, src))
        return found

    def stock(self, word):
        """The stock value of a hook word: the base of its first feature."""
        return self.words[word][0].base

    def key_entries(self):
        """{key: [(layout, address, table, src)]} of the symbol tables, and the
        image-byte and target keys of `can_symbols` by layout."""
        entries = defaultdict(list)
        values = defaultdict(dict)
        src = RUNTIME_TARGETS.as_posix()
        for name, table in CANONICAL_TABLES.items():
            for key, value in self.tables[name].items():
                if key in ROM_BYTES or key in CAN_KEYS:
                    values[CANONICAL][key] = (value, src)
                else:
                    entries[key].append((CANONICAL, value, table, src))
        for key, (base, _) in self.tables[TEMPLATE].items():
            entries[key].append(("1nd", base, "map_families", src))
        src = FEATURE_LAYOUTS["map_switching"].as_posix()
        for family in self.layouts_doc["map_switching"].get("family", ()):
            entries[family["key"]].append((CANONICAL, family["canonical_address"],
                                           "map_families", src))
        src = PROFILES.as_posix()
        for layout, (rom, profile) in self.profiles.items():
            for table in SYMBOL_TABLES:
                for key, value in profile.get(table, {}).items():
                    if key in ROM_BYTES or key in CAN_KEYS:
                        values[layout][key] = (value, src)
                    else:
                        entries[key].append((layout, value, table, src))
        return entries, values


def key_kind(b, entries):
    """The kind of a symbol-table key: `tbl` for a map family, `hook` when a
    feature redirects the word at every address of the key, else the kind of
    the symbols registered at its addresses, else the kind its addresses
    admit."""
    if any(table == "map_families" for _, _, table, _ in entries):
        return "tbl"
    kinds = [{key.kind for key in b.at(layout, address)} for layout, address, _, _ in entries]
    if all("hook" in found for found in kinds):
        return "hook"
    registered = set().union(*kinds) - {"hook"}
    for kind in KIND_ORDER:
        if kind in registered:
            return kind
    if any(b.is_function(layout, address) for layout, address, _, _ in entries):
        return "fn"
    spaces = {b.space(layout, address) for layout, address, _, _ in entries}
    if spaces == {"ram"}:
        return "ram"
    if spaces == {"io"}:
        return "reg"
    if spaces == {"rom"}:
        inside = any(b.rom_data_kind(layout, address) == "tbl"
                     for layout, address, _, _ in entries)
        return "tbl" if inside else "const"
    return None


def declare(b, root):
    facts = Profiles(b, root)
    b.stash[__name__] = facts
    targets = defaultdict(dict)
    notes = defaultdict(list)
    _declare_hooks(b, facts, targets)
    _declare_dids(b, facts, targets)
    keys = _declare_keys(b, facts, targets)
    _declare_telemetry(b, facts, targets)
    unavailable = _declare_profiles(b, facts, targets, notes)
    _declare_rows(b, facts, keys, targets, notes)
    _declare_unavailable(b, unavailable)
    for (feature, layout), props in sorted(targets.items()):
        b.entity("feature", feature, PROFILES.as_posix())
        status = props.pop("status", "supported")
        srcs = props.pop("src", {PROFILES.as_posix()})
        target = b.target(feature, layout, sorted(srcs)[0], status=status, props=props)
        target.sources.update(srcs)
        for note in notes.get((feature, layout), ()):
            b.target(feature, layout, note[1], props={"note": note[0]})


def _declare_hooks(b, facts, targets):
    for (layout, address), hooks in sorted(facts.words.items()):
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
            targets[(hook.feature, layout)].setdefault("hooks", {})[hook.key] = {
                "hook": key, "replacement": hook.replacement}
        # The canonical key of the first feature names the word, or else its
        # own key unless that is the canonical key of another word.
        name = first.canonical or first.key
        if first.canonical or first.key not in facts.canonical_map_keys:
            b.name(key, name, "hook", first.src, rank=FEATURES.index(first.feature))


def _declare_dids(b, facts, targets):
    src = FEATURE_LAYOUTS["rolling_launch"].as_posix()
    entries = [(CANONICAL, entry["name"], entry["did"], entry["pointer_address"],
                entry["target"], entry["width"], src)
               for entry in facts.layouts_doc["rolling_launch"].get("diagnostic", ())]
    src = PROFILES.as_posix()
    for layout, (rom, profile) in facts.profiles.items():
        for name, (did, pointer, target, width) in profile.get("rolling_diagnostics", {}).items():
            entries.append((layout, name, did, pointer, target, width, src))
    for layout, name, did, pointer, target, width, src in entries:
        group = ("did", "number", did)
        key = b.symbol(layout, "did", pointer, src, group=group)
        b.props(group, {"number": did}, src)
        allocations = targets[("rolling_launch", layout)].setdefault("allocations", {})
        allocations[name] = {"address": target, "width": width, "did": key}


def _declare_keys(b, facts, targets):
    """Symbols of the symbol-table keys; returns {(layout, key): symbol key}."""
    entries, values = facts.key_entries()
    found = {}
    for name, rows in sorted(entries.items()):
        kind = key_kind(b, rows)
        if kind is None:
            b.issue("symbols", rows[0][3], name,
                    "the addresses of the key lie in different spaces")
            continue
        group = (kind, "key", name)
        for layout, address, table, src in rows:
            found[(layout, name)] = b.symbol(layout, kind, address, src, group=group)
        # A key of the canonical layout names a meaning that several keys join.
        canonical = any(layout == CANONICAL for layout, _, _, _ in rows)
        b.name(group, name, "symbol_key", rows[0][3], rank=0 if canonical else 1)
    for layout, items in values.items():
        for name, (value, src) in items.items():
            if name in CAN_KEYS:
                targets[("can_telemetry", layout)][name] = value
                continue
            key = found.get((layout, ROM_BYTES[name]))
            if key is None:
                b.issue("references", src, f"{name}@{layout}",
                        f"no {ROM_BYTES[name]} symbol for its image bytes")
                continue
            b.symbol(layout, key.kind, key.address, src, evidence=[{
                "kind": "rom-bytes", "supports": "identity", "at": key.location,
                "value": f"{value:08x}", "note": name}])
    return found


def _declare_telemetry(b, facts, targets):
    src = PROFILES.as_posix()
    for layout, (rom, profile) in sorted(facts.profiles.items()):
        for field, address in profile.get("telemetry_sources", {}).items():
            kind = b.data_kind(layout, address)
            if kind is None:
                b.issue("symbols", src, f"{field}@{layout}",
                        "a telemetry source outside RAM and the peripherals")
                continue
            group = (kind, "field", field)
            b.symbol(layout, kind, address, src, group=group, strength="field")
            b.name(group, field.removesuffix("_raw"), "field", src)


def _declare_unavailable(b, pending):
    """Statuses of the source meanings of the fields that a profile lists as
    unavailable and no correspondence row states."""
    for layout, field, text, path, key in pending:
        kind = "reg" if ("reg", "field", field) in b.group_kind else "ram"
        b.status((kind, "field", field), layout, _state(text), path, props={"note": text},
                 evidence=[{"kind": "registry", "supports": "identity", "path": path,
                            "key": key, "note": text}])


def _declare_profiles(b, facts, targets, notes):
    """Keys of the feature targets; returns the unavailable fields that no
    correspondence row states."""
    src = PROFILES.as_posix()
    pending = []
    for layout, (rom, profile) in sorted(facts.profiles.items()):
        runtime = targets[(RUNTIME, layout)]
        runtime.update({key: profile[key] for key in RUNTIME_KEYS if key in profile})
        for key in MAP_KEYS:
            if key in profile:
                targets[("map_switching", layout)][key] = profile[key]
        for feature, supported in profile.get("capabilities", {}).items():
            targets[(feature, layout)]["status"] = "supported" if supported else "unsupported"
        unavailable = profile.get("telemetry_unavailable", [])
        targets[("can_telemetry", layout)]["unavailable"] = list(unavailable)
        evidence = profile.get("evidence", {})
        for topic, text in evidence.items():
            feature = EVIDENCE.get(topic)
            if feature is None:
                b.issue("schema", src, f"profile.{rom}.evidence", f"unknown topic {topic}")
                continue
            notes[(feature, layout)].append((text, src))
        rows = {row["key"]: row for row in facts.rows.get(layout, ("", []))[1]
                if row["domain"] == "telemetry"}
        for field in unavailable:
            row = rows.get(field)
            if row is not None and row["status"] == "unsupported":
                continue
            pending.append((layout, field, evidence.get("telemetry", ""), src,
                            f"profile.{rom}.telemetry_unavailable"))
    for feature in FEATURES:
        targets[(feature, CANONICAL)].setdefault("status", "supported")
    return pending


def _declare_rows(b, facts, keys, targets, notes):
    for layout, (path, rows) in sorted(facts.rows.items()):
        if layout not in b.layouts:
            b.issue("schema", path, layout, "a correspondence file of an unknown layout")
            continue
        rom, profile = facts.profiles.get(layout, (None, {}))
        for number, row in enumerate(rows, start=2):
            subject = f"{row['domain']}:{row['key']}"
            where = f"{path}:{number}"
            domain, status, text = row["domain"], row["status"], row["evidence"]
            source, target = _hex(row["source"]), _hex(row["target"])
            feature = DOMAIN_FEATURE.get(domain)
            if domain == "capability":
                notes[(row["key"], layout)].append((text, path))
                continue
            if feature is None:
                b.issue("schema", where, subject, f"unknown domain {domain}")
                continue
            entry = targets[(feature, layout)]
            entry.setdefault("src", {PROFILES.as_posix()}).add(path)
            if row["variant"]:
                entry.setdefault("variants", []).append(
                    {"domain": domain, "key": row["key"], "variant": row["variant"],
                     "address": target})
            if domain == "allocation":
                stated = profile.get(row["key"])
                if stated is not None and stated != target:
                    b.issue("audit", where, subject,
                            f"target {target:08x} disagrees with the profile {stated:08x}")
                entry.setdefault("allocation_notes", {})[row["key"]] = text
                continue
            if domain in HOOK_DOMAINS:
                _hook_row(b, facts, layout, row, path, where, subject, source, target)
                continue
            if row["key"] in CAN_KEYS:
                stated = targets[("can_telemetry", layout)].get(row["key"])
                if stated is not None and stated != target:
                    b.issue("audit", where, subject,
                            f"target {target:x} disagrees with the profile {stated:x}")
                continue
            known = keys.get((layout, row["key"])) or keys.get((CANONICAL, row["key"]))
            kind = known.kind if known else _row_kind(b, domain, layout, source, target)
            if kind is None:
                b.issue("symbols", where, subject, "no kind for the row's addresses")
                continue
            if domain == "telemetry":
                group, strength = (kind, "field", row["key"]), "field"
                b.name(group, row["key"].removesuffix("_raw"), "field", path)
            else:
                group, strength = (kind, "key", row["key"]), "key"
                b.name(group, row["key"], "symbol_key", path, rank=1)
            left = right = None
            if source is not None:
                left = b.symbol(CANONICAL, kind, source, path, group=group, strength=strength)
            if target is not None:
                right = b.symbol(layout, kind, target, path, group=group, strength=strength,
                                 props={"note": text})
                if row["stock"]:
                    b.symbol(layout, kind, target, path, evidence=[{
                        "kind": "rom-bytes", "supports": "identity", "at": right.location,
                        "value": row["stock"], "note": row["key"]}])
            if status == "unsupported":
                if domain in MAP_DOMAINS:
                    entry.setdefault("unsupported", []).append(
                        {"key": row["key"], "note": text})
                b.status(group, layout, _state(text), path, props={"note": text},
                         evidence=[{"kind": "registry", "supports": "identity", "path": path,
                                    "key": subject, "note": text}],
                         yields=domain in MAP_DOMAINS)
            elif left is not None and right is not None:
                b.join(left, right, where, "homology" if status == "mapped" else "role")


def _row_kind(b, domain, layout, source, target):
    if source is None and target is None:
        return None
    if domain == "telemetry":
        return b.data_kind(layout, target) if target is not None else b.data_kind(CANONICAL, source)
    if domain in MAP_DOMAINS:
        return "tbl"
    found = {key.kind for key in b.at(layout, target)} if target is not None else set()
    if source is not None:
        found |= {key.kind for key in b.at(CANONICAL, source)}
    for kind in KIND_ORDER:
        if kind in found:
            return kind
    address, where = (target, layout) if target is not None else (source, CANONICAL)
    if b.is_function(where, address):
        return "fn"
    return b.data_kind(where, address) or b.rom_data_kind(where, address)


def _hook_row(b, facts, layout, row, path, where, subject, source, target):
    hooks = facts.words.get((layout, target))
    if not hooks:
        b.issue("references", where, subject, f"no hook of the profile at {target:08x}")
        return
    stock = _hex(row["stock"])
    if stock is not None and stock != facts.stock((layout, target)):
        b.issue("audit", where, subject, f"stock {stock:08x} disagrees with the profile "
                                         f"{facts.stock((layout, target)):08x}")
    key = b.symbol(layout, "hook", target, path, props={"note": row["evidence"]})
    if source is not None and (CANONICAL, source) in facts.words:
        other = b.symbol(CANONICAL, "hook", source, path)
        b.join(other, key, where, "homology" if row["status"] == "mapped" else "role")


def relate(b, root):
    facts = b.stash.get(__name__)
    if facts is None:
        return
    for (layout, address), hooks in sorted(facts.words.items()):
        first = hooks[0]
        key = b.symbol(layout, "hook", address, first.src)
        to = b.resolve(layout, first.base, ("fn", "tbl", "const"), first.src)
        if to is None:
            b.issue("references", first.src, key.key,
                    f"stock {first.base:08x} is no ROM function, table, or constant")
            continue
        b.link(key, "target", to, first.src)
