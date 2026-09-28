"""Address profiles and runtime correspondence (tools/kb/SPEC.md, sections 20.1
and 20.3).

- The key tables of the `7mfk` targets of `kb/feature/` give the `7mfk`
  symbols of their keys (`kb.targets`), and the hooks of the `map_switching`
  target of a layout join the per-layout key of a map hook to the canonical
  key of its `7mfk` word.
- Each image profile of `patches/rom-address-profiles.toml` gives the symbols
  of its layout: a symbol-table key names the meaning at its address, a
  telemetry source the source meaning of its field, and a hook the ROM word
  that its features redirect, which joins the `7mfk` word of its canonical key
  (`kb.adapters.layouts`). The other keys go to the targets of `runtime`,
  `map_switching`, `rolling_launch`, and `can_telemetry`: a key of
  `map_families` enters `families` of its target and a key of another symbol
  table `symbols`, the storage tables, the numbers, and the variants their
  own keys, and each evidence topic `basis`.
- A row of `patches/<layout>-runtime-correspondence.csv` joins its target
  symbol to the meaning of its source symbol, and an `unsupported` row gives a
  status. A symbol or map row whose key names no symbol-table key of the
  address profile on its layout enters `requires` of its target with its
  symbol, and an `unsupported` map row enters `unsupported` with the `7mfk`
  symbol of its source and its text. The text of a hook row of a later
  feature than the first that redirects its word is the `note` of the hook
  key in its target, the text of an allocation or a target number the entry
  of `notes`, and the text of a capability the `note` of the target; the
  sources of the allocation rows give the `7mfk` bounds of `runtime`.
- A `target-specific` row whose target a `mapped` row of another key of the
  same file places binds a role of its feature: the key and the symbol enter
  `roles` of the feature target of the layout, and neither the row nor the
  profile entry of the key on that layout joins a meaning. A `target-specific`
  telemetry row binds the role of its field in the same way: the telemetry
  source of the profile is a symbol of another meaning than the source of the
  field.
- A register is physical: a `reg` key at another address than on the
  canonical layout binds a role of its feature with the register at that
  address, whose symbols on every layout form one meaning.
- The records that the image-byte keys of `can_symbols` state are one 32-bit
  word each.
- `render_profiles` and `render_correspondence` give the canonical text of the
  address profiles and of a correspondence file.

From their conversion the registries are projections of the files, which
`render_registries` gives:

- `patches/rom-address-profiles.toml` has a profile for the image of each
  layout other than `7mfk` with a `runtime` target, and an `inherits`
  profile for each other image of the layout. A profile states the family of
  its layout, the `7mfk` image as `layout_source`, the keys of the `runtime`
  and `map_switching` targets, the status of each feature target as its
  capability, and the addresses of the `families` symbols. A hook key takes
  the address of its symbol, the stock word that the `target` link of its
  meaning reaches, and its replacement, and a later feature than map
  switching takes as `base` the replacement of the previous feature that
  redirects the word, or else the stock word. The DID allocations of
  `rolling_launch` give `rolling_diagnostics`, the symbols and the roles of a
  target its symbol table with the `can_telemetry` numbers and the
  image-byte words of its records, a field role or the symbol of the source
  meaning of a field its telemetry source, a field whose source meaning has
  a status on the layout `telemetry_unavailable`, and the `basis` of the
  targets `evidence`.
- `patches/<layout>-runtime-correspondence.csv` exists for each layout whose
  `runtime` target states `notes`: an `allocation` row for each note, whose
  source is the bound of the `7mfk` target and which is `mapped` where the
  target is the source plus the relocation of the profile; for each feature a
  row of each family, hook, symbol, role, required meaning, unsupported
  entry, and number of its target; a `telemetry` row for each field with its
  role, the symbol of its source meaning, or the status of that meaning; and
  a `capability` row for each target that states a `note`. The row item of a
  symbol is the first evidence item of its entry that is homology evidence
  toward `7mfk`, which gives `mapped`, or identity evidence of its own layout
  other than image bytes, which gives `target-specific`, and its note is the
  text of the row. A role row is `target-specific` with the note of the role,
  an unsupported entry or a status `unsupported` with its note, and a number
  `mapped` where it equals the `7mfk` value; a `target-specific` map row
  takes the domain `map_native`, and the hook row of a later feature than
  the first that redirects its word the `note` of its hook key.
"""

from collections import defaultdict
import csv
from dataclasses import dataclass
import io
from pathlib import Path
import re
import tomllib

from kb import match, repo, store, targets
from kb.adapters import layouts, telemetry
from kb.model import SymbolKey
from kb.repo import KbError
from kb.values import hexed

PROFILES = Path("patches/rom-address-profiles.toml")
PATCHES = Path("patches")
CORRESPONDENCE = "*-runtime-correspondence.csv"
CANONICAL = "7mfk"
FEATURES = layouts.FEATURES
RUNTIME = "runtime"
HOOK_TABLES = {"map_hooks": "map_switching", "rolling_hooks": "rolling_launch",
               "can_hooks": "can_telemetry"}
SYMBOL_TABLES = ("map_families", "map_symbols", "rolling_symbols", "can_symbols")
# The symbol table of the key table `symbols` of the `7mfk` target of each
# feature.
CANONICAL_TABLES = {"map_switching": "map_symbols", "rolling_launch": "rolling_symbols",
                    "can_telemetry": "can_symbols"}
# `can_symbols` keys whose values are no addresses: the image bytes at the
# address of another key, and keys of the `can_telemetry` target.
ROM_BYTES = targets.RECORD_WORDS
CAN_KEYS = (*targets.NUMBERS, "feedback_payload_offset")
# The keys whose records the image-byte keys state: one four-byte record each,
# as one 32-bit word.
RECORDS = frozenset(ROM_BYTES.values())
RECORD_STORAGE = "uint32"
RUNTIME_KEYS = ("rom_size", "rom_delta", "ram_delta", "free_rom_start", "free_rom_end",
                "injected_rom_start", "injected_rom_end", "free_ram_start", "free_ram_end",
                "injected_ram_start", "injected_ram_end", "map_variant",
                "telemetry_completion_variant", "telemetry_zero_source",
                "ignition_unreferenced_routine")
MAP_KEYS = ("ascd_enabled_mask", "extra_cvtc_storage", "ignition_state_storage")
# Target keys whose values are addresses, or tables and lists of addresses; the
# other keys hold sizes, deltas, masks, indices, and names.
ADDRESS_KEYS = frozenset({"free_rom_start", "free_rom_end", "injected_rom_start",
                          "injected_rom_end", "free_ram_start", "free_ram_end",
                          "injected_ram_start", "injected_ram_end", "telemetry_zero_source",
                          "ignition_unreferenced_routine", "extra_cvtc_storage",
                          "ignition_state_storage"})
DERIVED = ("family", "layout_source", "inherits")
OTHER_KEYS = ("capabilities", "rolling_diagnostics", "telemetry_sources",
              "telemetry_unavailable", "evidence")
EVIDENCE = {"free_rom": RUNTIME, "free_ram": RUNTIME, "maps": "map_switching",
            "rolling": "rolling_launch", "can": "can_telemetry", "telemetry": "can_telemetry"}
TABLE_FEATURE = {"map_families": "map_switching", "map_symbols": "map_switching",
                 "rolling_symbols": "rolling_launch", "can_symbols": "can_telemetry"}
# The key table of a feature target that states the keys of a symbol table.
KEY_TABLE = {"map_families": "families", "map_symbols": "symbols",
             "rolling_symbols": "symbols", "can_symbols": "symbols"}
# Domains of the rows that enter `requires` of their target where their key
# names no symbol-table key of the address profile.
REQUIRING = ("map", "map_native", "map_symbol", "rolling_symbol", "can_symbol")
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
Hook = layouts.Hook


@dataclass
class Row:
    """A correspondence row with the symbols it names: `right` on its layout,
    `left` on `7mfk`, and `hook` for a hook row; `role` when the row binds a
    role of its feature."""

    layout: str
    path: str
    row: dict
    left: object = None
    right: object = None
    hook: Hook | None = None
    role: bool = False


def inputs(root):
    """The registries, and the feature files of the `7mfk` key tables."""
    found = [PROFILES.as_posix()]
    found += [store.path_of("feature", feature).as_posix() for feature in CANONICAL_TABLES]
    found += [path.relative_to(root).as_posix()
              for path in sorted((root / PATCHES).glob(CORRESPONDENCE))]
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


def _value(key, value):
    return hexed(value) if key in ADDRESS_KEYS else value


def _state(text):
    return "unresolved" if UNRESOLVED.search(text or "") else "absent"


class Profiles:
    """The facts of the registries of this adapter, before they enter the model."""

    def __init__(self, b, root):
        self.root, self.overlay = root, b.overlay
        # {feature: {key: value}} of the `7mfk` targets.
        self.canonical = {feature: targets.canonical_symbols(feature, root, b.overlay)
                          for feature in CANONICAL_TABLES}
        self.document = tomllib.loads((root / PROFILES).read_text(encoding="utf-8"))
        self.layouts_doc = layouts.documents(root)
        self.rows = correspondence(root)
        # The rows with the symbols they name, as `_declare_rows` resolves them.
        self.resolved = []
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
        self.roles = self._roles()
        self.canonical_map_keys = layouts.canonical_keys(self.layouts_doc)
        # The `7mfk` words, which the layouts state.
        self.canonical_words = {hook.address
                                for hook in layouts.canonical_hooks(self.layouts_doc)}
        self.hooks = self._hooks()
        self.words = layouts.words(self.hooks)
        # The hook words of every layout, which the canonical layouts state on
        # `7mfk` and the address profiles elsewhere.
        self.all_words = frozenset({*self.words,
                                    *((CANONICAL, word) for word in self.canonical_words)})

    def _roles(self):
        """{(layout, key): (target, row)} of the `target-specific` symbol rows
        whose target a `mapped` row of another key of the same file places,
        and of the `target-specific` telemetry rows: there the key fills a
        role of its feature with the symbol of another meaning, as the VQ37
        rolling launch drives the final inhibit mask and the JK78C telemetry
        reads the Fuel Compensation Main column that the target maps take."""
        found = {}
        for layout, (path, rows) in self.rows.items():
            placed = defaultdict(set)
            for row in rows:
                if row["status"] == "mapped" and row["target"]:
                    placed[_hex(row["target"])].add(row["key"])
            for row in rows:
                target = _hex(row["target"])
                if row["status"] != "target-specific":
                    continue
                if row["domain"] == "telemetry" or (
                        row["domain"] in SYMBOL_DOMAINS
                        and placed.get(target, set()) - {row["key"]}):
                    found[(layout, row["key"])] = (target, row)
        return found

    def hook_keys(self, layout):
        """{per-layout key: canonical key} of the map hooks of a layout: the
        key of the `7mfk` word of the meaning of each hook of its
        `map_switching` target in the canonical map layout."""
        words = {entry["address"]: entry["key"]
                 for entry in self.layouts_doc[FEATURES[0]].get("hook", ())}
        return {key: words[word] for word, key in targets.hook_keys(
            FEATURES[0], layout, self.root, self.overlay).items() if word in words}

    def _hooks(self):
        found = []
        src = PROFILES.as_posix()
        for layout, (rom, profile) in self.profiles.items():
            canonical = self.hook_keys(layout)
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

    def canonical_numbers(self):
        """The `can_telemetry` numbers of `7mfk`: the mailbox of its target, and
        the payload offset of the feedback record of the map layout."""
        found = {key: value for key, value in self.canonical["can_telemetry"].items()
                 if key in CAN_KEYS}
        feedback = self.layouts_doc["map_switching"].get("feedback", {})
        if "payload_offset" in feedback:
            found["feedback_payload_offset"] = feedback["payload_offset"]
        return found

    def key_entries(self):
        """{key: [(layout, address, table, src)]} of the symbol tables, and the
        image-byte and target keys of `can_symbols` by layout."""
        entries = defaultdict(list)
        values = defaultdict(dict)
        for feature, table in CANONICAL_TABLES.items():
            src = store.path_of("feature", feature).as_posix()
            for key, value in self.canonical[feature].items():
                if key in ROM_BYTES or key in CAN_KEYS:
                    values[CANONICAL][key] = (value, src)
                else:
                    entries[key].append((CANONICAL, value, table, src))
        src = PROFILES.as_posix()
        for layout, (rom, profile) in self.profiles.items():
            for table in SYMBOL_TABLES:
                for key, value in profile.get(table, {}).items():
                    if key in ROM_BYTES or key in CAN_KEYS:
                        values[layout][key] = (value, src)
                    else:
                        entries[key].append((layout, value, table, src))
        return entries, values


def key_kind(b, entries, words=frozenset()):
    """The kind of a symbol-table key: `tbl` for a map family, `hook` when a
    feature redirects the word at every address of the key, as the hook
    symbols or the (layout, address) `words` state, else the kind of the
    symbols registered at its addresses, else the kind its addresses admit."""
    if any(table == "map_families" for _, _, table, _ in entries):
        return "tbl"
    kinds = [{key.kind for key in b.at(layout, address)}
             | ({"hook"} if (layout, address) in words else set())
             for layout, address, _, _ in entries]
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
    layouts.declare_words(b, facts.words, targets, facts.canonical_map_keys)
    _declare_dids(b, facts, targets)
    keys = _declare_keys(b, facts, targets)
    _declare_telemetry(b, facts, targets)
    unavailable = _declare_profiles(b, facts, targets)
    _declare_rows(b, facts, keys, targets)
    _declare_unavailable(b, unavailable)
    for (feature, layout), props in sorted(targets.items()):
        b.entity("feature", feature, PROFILES.as_posix())
        status = props.pop("status", "supported")
        srcs = props.pop("src", None) or {PROFILES.as_posix()}
        target = b.target(feature, layout, sorted(srcs)[0], status=status, props=props)
        target.sources.update(srcs)


def _declare_dids(b, facts, targets):
    src = PROFILES.as_posix()
    layouts.declare_dids(b, [
        (layout, name, did, pointer, target, width, src)
        for layout, (rom, profile) in facts.profiles.items()
        for name, (did, pointer, target, width) in profile.get("rolling_diagnostics", {}).items()],
        targets)


def _entry(targets, feature, layout, src):
    """The keys of the target of a feature on a layout, which `src` states."""
    entry = targets[(feature, layout)]
    entry.setdefault("src", set()).add(src)
    return entry


def _declare_keys(b, facts, targets):
    """Symbols of the symbol-table keys, and the keys of the symbol tables of
    the targets; returns {(layout, key): symbol key}."""
    entries, values = facts.key_entries()
    found = {}
    for name, rows in sorted(entries.items()):
        kind = key_kind(b, rows, facts.all_words)
        if kind is None:
            b.issue("symbols", rows[0][3], name,
                    "the addresses of the key lie in different spaces")
            continue
        group = (kind, "key", name)
        if name in RECORDS:
            b.props(group, {"storage": RECORD_STORAGE}, rows[0][3])
        home = {address for layout, address, _, _ in rows if layout == CANONICAL}
        for layout, address, table, src in rows:
            role = facts.roles.get((layout, name))
            if role is None and kind == "reg" and home and address not in home:
                found[(layout, name)] = key = b.symbol(
                    layout, kind, address, src, group=(kind, "register", address))
                targets[(TABLE_FEATURE[table], layout)].setdefault("roles", {}).setdefault(
                    name, {})["symbol"] = key
                continue
            if role is None:
                found[(layout, name)] = key = b.symbol(layout, kind, address, src, group=group)
                if table in KEY_TABLE:
                    _entry(targets, TABLE_FEATURE[table], layout, src).setdefault(
                        KEY_TABLE[table], {})[name] = key
                continue
            if address != role[0]:
                b.issue("audit", src, f"{name}@{layout}",
                        f"address {address:08x} disagrees with the role row {role[0]:08x}")
            found[(layout, name)] = key = b.symbol(layout, kind, address, src)
            targets[(TABLE_FEATURE[table], layout)].setdefault("roles", {}).setdefault(
                name, {})["symbol"] = key
        # A key of the canonical layout names a meaning that several keys join.
        canonical = any(layout == CANONICAL for layout, _, _, _ in rows)
        b.name(group, name, "symbol_key", rows[0][3], rank=0 if canonical else 1)
    for layout, items in values.items():
        for name, (value, src) in items.items():
            if name in CAN_KEYS:
                _entry(targets, "can_telemetry", layout, src)[name] = value
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
    """Symbols of the telemetry sources: the source meaning of the field, or
    the symbol that fills the role of the field on the layout."""
    src = PROFILES.as_posix()
    for layout, (rom, profile) in sorted(facts.profiles.items()):
        for field, address in profile.get("telemetry_sources", {}).items():
            kind = b.data_kind(layout, address)
            if kind is None:
                b.issue("symbols", src, f"{field}@{layout}",
                        "a telemetry source outside RAM and the peripherals")
                continue
            role = facts.roles.get((layout, field))
            if role is not None:
                if address != role[0]:
                    b.issue("audit", src, f"{field}@{layout}",
                            f"address {address:08x} disagrees with the role row {role[0]:08x}")
                targets[("can_telemetry", layout)].setdefault("roles", {}).setdefault(
                    field, {})["symbol"] = b.symbol(layout, kind, address, src)
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


def _declare_profiles(b, facts, targets):
    """Keys of the feature targets; returns the unavailable fields that no
    correspondence row states."""
    src = PROFILES.as_posix()
    pending = []
    for layout, (rom, profile) in sorted(facts.profiles.items()):
        runtime = _entry(targets, RUNTIME, layout, src)
        runtime.update({key: _value(key, profile[key]) for key in RUNTIME_KEYS if key in profile})
        for key in MAP_KEYS:
            if key in profile:
                _entry(targets, "map_switching", layout, src)[key] = _value(key, profile[key])
        for feature, supported in profile.get("capabilities", {}).items():
            _entry(targets, feature, layout, src)["status"] = (
                "supported" if supported else "unsupported")
        unavailable = profile.get("telemetry_unavailable", [])
        evidence = profile.get("evidence", {})
        for topic, text in evidence.items():
            feature = EVIDENCE.get(topic)
            if feature is None:
                b.issue("schema", src, f"profile.{rom}.evidence", f"unknown topic {topic}")
                continue
            _entry(targets, feature, layout, src).setdefault("basis", {})[topic] = text
        rows = {row["key"]: row for row in facts.rows.get(layout, ("", []))[1]
                if row["domain"] == "telemetry"}
        for field in unavailable:
            row = rows.get(field)
            if row is not None and row["status"] == "unsupported":
                continue
            pending.append((layout, field, evidence.get("telemetry", ""), src,
                            f"profile.{rom}.telemetry_unavailable"))
    return pending


def _declare_rows(b, facts, keys, targets):
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
                _entry(targets, row["key"], layout, path)["note"] = text
                continue
            if feature is None:
                b.issue("schema", where, subject, f"unknown domain {domain}")
                continue
            entry = _entry(targets, feature, layout, path)
            if domain == "allocation":
                _allocation(b, targets, layout, profile, row, path, where, subject,
                            source, target)
                continue
            if domain in HOOK_DOMAINS:
                _hook_row(b, facts, targets, layout, row, path, where, subject, source, target)
                continue
            if row["key"] in CAN_KEYS:
                _can_key(b, facts, targets, layout, row, path, where, subject, source, target)
                continue
            known = keys.get((layout, row["key"])) or keys.get((CANONICAL, row["key"]))
            kind = known.kind if known else _row_kind(b, domain, layout, source, target)
            if kind is None:
                b.issue("symbols", where, subject, "no kind for the row's addresses")
                continue
            if facts.roles.get((layout, row["key"]), (None, None))[1] is row:
                role = entry.setdefault("roles", {}).setdefault(row["key"], {})
                right = b.symbol(layout, kind, target, path)
                role.update({"symbol": right, "note": text})
                left = None
                if source is not None and domain == "telemetry":
                    left = b.symbol(CANONICAL, kind, source, path,
                                    group=(kind, "field", row["key"]), strength="field")
                elif source is not None:
                    left = b.symbol(CANONICAL, kind, source, path, group=(kind, "key", row["key"]))
                facts.resolved.append(Row(layout, path, row, left, right, role=True))
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
            facts.resolved.append(Row(layout, path, row, left, right))
            if row["variant"]:
                if right is None:
                    b.issue("schema", where, subject, "a variant without a target")
                else:
                    entry.setdefault("variants", []).append(
                        {"symbol": right, "variant": row["variant"]})
            if status == "unsupported":
                if domain in MAP_DOMAINS and left is None:
                    b.issue("schema", where, subject, "an unsupported map row without a source")
                elif domain in MAP_DOMAINS:
                    entry.setdefault("unsupported", []).append({"symbol": left, "note": text})
                b.status(group, layout, _state(text), path, props={"note": text},
                         evidence=[{"kind": "registry", "supports": "identity", "path": path,
                                    "key": subject, "note": text}],
                         yields=domain in MAP_DOMAINS)
                continue
            if domain in REQUIRING and right is not None and (layout, row["key"]) not in keys:
                entry.setdefault("requires", []).append(right)
            if left is not None and right is not None:
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


def _allocation(b, targets, layout, profile, row, path, where, subject, source, target):
    """The text of an allocation row in `notes` of the `runtime` target, and
    its source as the `7mfk` bound of its key."""
    name = row["key"]
    stated = profile.get(name)
    if stated is not None and stated != target:
        b.issue("audit", where, subject,
                f"target {target:08x} disagrees with the profile {stated:08x}")
    _entry(targets, RUNTIME, layout, path).setdefault("notes", {})[name] = row["evidence"]
    if source is None:
        return
    canonical = _entry(targets, RUNTIME, CANONICAL, path)
    if canonical.setdefault(name, _value(name, source)) != _value(name, source):
        b.issue("audit", where, subject,
                f"source {source:08x} disagrees with {canonical[name]} of {CANONICAL}")


def _can_key(b, facts, targets, layout, row, path, where, subject, source, target):
    """The text of a row of a `can_telemetry` number in `notes` of its target;
    the target and the source of the row agree with the numbers of the
    layout and of `7mfk`."""
    name = row["key"]
    stated = targets[("can_telemetry", layout)].get(name)
    if stated is not None and stated != target:
        b.issue("audit", where, subject, f"target {target:x} disagrees with the profile {stated:x}")
    canonical = facts.canonical_numbers().get(name)
    if canonical is not None and source is not None and canonical != source:
        b.issue("audit", where, subject, f"source {source:x} disagrees with {canonical:x} of "
                                         f"{CANONICAL}")
    _entry(targets, "can_telemetry", layout, path).setdefault("notes", {})[name] = (
        row["evidence"])


def _hook_row(b, facts, targets, layout, row, path, where, subject, source, target):
    """The text of the row of the first feature that redirects a word is the
    note of its symbol, and the text of a later feature the `note` of the hook
    key in the target of that feature."""
    hooks = facts.words.get((layout, target))
    if not hooks:
        b.issue("references", where, subject, f"no hook of the profile at {target:08x}")
        return
    stock = _hex(row["stock"])
    if stock is not None and stock != facts.stock((layout, target)):
        b.issue("audit", where, subject, f"stock {stock:08x} disagrees with the profile "
                                         f"{facts.stock((layout, target)):08x}")
    feature = DOMAIN_FEATURE[row["domain"]]
    hook = next((hook for hook in hooks if hook.feature == feature), None)
    if hook is None or hook.key != row["key"]:
        b.issue("references", where, subject, f"no {feature} hook {row['key']} at {target:08x}")
        return
    if hook is hooks[0]:
        key = b.symbol(layout, "hook", target, path, props={"note": row["evidence"]})
    else:
        key = b.symbol(layout, "hook", target, path)
        entry = _entry(targets, feature, layout, path)
        entry["hooks"][hook.key]["note"] = row["evidence"]
    other = None
    if source is not None and source in facts.canonical_words:
        other = b.symbol(CANONICAL, "hook", source, path)
        b.join(other, key, where, "homology" if row["status"] == "mapped" else "role")
    facts.resolved.append(Row(layout, path, row, other, key, hook=hook))


def relate(b, root):
    facts = b.stash.get(__name__)
    if facts is not None:
        layouts.link_words(b, facts.words)


# Rendering -----------------------------------------------------------------

HEADER = (
    "# Exact stock-address and runtime-allocation profiles for near-code ROMs.\n"
    "#\n"
    "# JK08A is an explicit coordinate source for the existing runtime layouts. It\n"
    "# is not a default ROM selector. Every target profile names an exact stock ROM\n"
    "# and all nonuniform stock addresses remain explicit below.\n")
# Keys of a profile in the order of the file: the scalars, then the tables.
SCALAR_ORDER = ("family", "layout_source", "inherits", "rom_size", "rom_delta", "ram_delta",
                "free_rom_start", "free_rom_end", "injected_rom_start", "injected_rom_end",
                "free_ram_start", "free_ram_end", "injected_ram_start", "injected_ram_end",
                "map_variant", "telemetry_completion_variant", "telemetry_unavailable",
                "telemetry_zero_source", "ascd_enabled_mask")
TABLE_ORDER = ("capabilities", "map_families", "map_hooks", "map_symbols", "rolling_hooks",
               "rolling_diagnostics", "rolling_symbols", "can_hooks", "can_symbols",
               "telemetry_sources", "extra_cvtc_storage", "ignition_state_storage",
               "ignition_unreferenced_routine", "evidence")
# Tables whose keys sort by name; the storage tables keep the order of their keys.
KEY_TABLES = ("map_families", "map_hooks", "map_symbols", "rolling_hooks", "rolling_symbols",
              "can_hooks", "can_symbols")
STORAGE_ORDER = ("adapter_start", "adapter_end", "pointer_table", "copies", "start", "end")
# Numbers that are no 32-bit words; a negative delta is decimal, since TOML
# has no signed hexadecimal integers.
NUMBER_FORMAT = {"rom_size": "0x{:X}", "feedback_payload_offset": "0x{:X}",
                 "ascd_enabled_mask": "0x{:02X}", "mailbox_mask": "0x{:04X}",
                 "mailbox_index": "{}"}
# Lists of names that sort by name.
SORTED = ("telemetry_unavailable",)
LINE = 79
CSV_FIELDS = ("domain", "key", "source", "target", "stock", "variant", "status", "evidence")
# Domains in the order of their blocks; `map_native` rows share the block of `map`.
DOMAIN_ORDER = ("allocation", "map", "map_hook", "map_symbol", "rolling_hook",
                "rolling_symbol", "can_hook", "can_symbol", "telemetry", "capability")
BLOCK = {"map_native": "map"}


def telemetry_fields(root):
    """The `ecu_ram` fields of the CAN telemetry profile in its order: the
    stream fields, then the fields of each context."""
    document = tomllib.loads((root / telemetry.PROFILE).read_text(encoding="utf-8"))
    fields = [*document.get("field", ()),
              *(field for context in document.get("context", ())
                for field in context.get("field", ()))]
    return [field["name"] for field in fields if field.get("kind") == "ecu_ram"]


def render_profiles(document, fields):
    """The text of `patches/rom-address-profiles.toml` from its document: the
    profiles by image id, the scalars and tables of a profile in the order of
    the file, the keys of a symbol or hook table and the unavailable fields by
    name, the diagnostics by DID number, and the telemetry sources in the
    order of `fields`."""
    blocks = [HEADER + f"\nschema_version = {document['schema_version']}"]
    for rom in sorted(document.get("profile", {})):
        profile = document["profile"][rom]
        _known(profile, (*SCALAR_ORDER, *TABLE_ORDER), f"profile.{rom}")
        lines = [f"[profile.{rom}]"]
        for key in SCALAR_ORDER:
            if key in profile:
                value = profile[key]
                lines += _assignment(key, sorted(value) if key in SORTED else value)
        blocks.append("\n".join(lines))
        for table in TABLE_ORDER:
            if table in profile:
                blocks += _table(f"profile.{rom}.{table}", table, profile[table], fields)
    return "\n\n".join(blocks) + "\n"


def _table(header, name, table, fields):
    """The blocks of one table of a profile."""
    if name == "capabilities":
        order = [key for key in FEATURES if key in table]
    elif name in KEY_TABLES:
        order = sorted(table)
    elif name == "rolling_diagnostics":
        order = sorted(table, key=lambda key: (table[key][0], key))
    elif name == "telemetry_sources":
        _known(table, fields, header)
        order = [key for key in fields if key in table]
    elif name == "evidence":
        _known(table, EVIDENCE, header)
        order = [key for key in EVIDENCE if key in table]
    else:
        surfaces = sorted(key for key, value in table.items() if isinstance(value, dict))
        _known(table, (*STORAGE_ORDER, *surfaces), header)
        lines = [f"[{header}]"]
        for key in STORAGE_ORDER:
            if key in table:
                lines += _assignment(key, table[key])
        found = ["\n".join(lines)]
        for surface in surfaces:
            found += _table(f"{header}.{surface}", "storage", table[surface], fields)
        return found
    lines = [f"[{header}]"]
    for key in order:
        value = table[key]
        if name == "rolling_diagnostics":
            did, pointer, target, width = value
            lines.append(f"{key} = [0x{did:04X}, 0x{pointer:08X}, 0x{target:08X}, {width}]")
        else:
            lines += _assignment(key, value)
    return ["\n".join(lines)]


def _assignment(key, value):
    if isinstance(value, bool):
        return [f"{key} = {'true' if value else 'false'}"]
    if isinstance(value, str):
        return [f'{key} = "{store.escape(value)}"']
    if isinstance(value, int):
        return [f"{key} = {_number(key, value)}"]
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        items = [f'"{store.escape(item)}"' for item in value]
        inline = f"{key} = [{', '.join(items)}]"
        if len(inline) <= LINE:
            return [inline]
        return [f"{key} = ["] + [f"    {item}," for item in items] + ["]"]
    if isinstance(value, list) and all(isinstance(item, int) for item in value):
        return [f"{key} = [{', '.join(f'0x{item:08X}' for item in value)}]"]
    raise KbError(f"{key}: no rendering of {value!r}", code=3)


def _number(key, value):
    if value < 0:
        return str(value)
    return NUMBER_FORMAT.get(key, "0x{:08X}").format(value)


def _known(table, order, subject):
    unknown = sorted(set(table) - set(order))
    if unknown:
        raise KbError(f"{subject}: no rendering of {', '.join(unknown)}", code=3)


def render_correspondence(rows, fields):
    """The text of a correspondence file from its rows: the blocks of the
    domains in order, the allocation rows in the order of the runtime keys,
    the telemetry rows in the order of `fields`, the capability rows in the
    order of the features, and the other rows by key and variant."""
    orders = {"allocation": RUNTIME_KEYS, "telemetry": tuple(fields), "capability": FEATURES}

    def order(row):
        domain = row["domain"]
        block = BLOCK.get(domain, domain)
        if block not in DOMAIN_ORDER:
            raise KbError(f"{domain}:{row['key']}: an unknown domain", code=3)
        if domain in orders:
            if row["key"] not in orders[domain]:
                raise KbError(f"{domain}:{row['key']}: an unknown key", code=3)
            return DOMAIN_ORDER.index(block), orders[domain].index(row["key"]), ""
        return DOMAIN_ORDER.index(block), row["key"], row["variant"]

    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(CSV_FIELDS)
    writer.writerows([row[field] for field in CSV_FIELDS] for row in sorted(rows, key=order))
    return out.getvalue()


# Projections ---------------------------------------------------------------

SCHEMA_VERSION = 2
# The prefix of the domains of the hook and symbol rows of each feature, and
# the hook and symbol tables of each feature in a profile.
PREFIX = {"map_switching": "map", "rolling_launch": "rolling", "can_telemetry": "can"}
PROFILE_HOOKS = {feature: table for table, feature in HOOK_TABLES.items()}
PROFILE_SYMBOLS = {feature: f"{prefix}_symbols" for feature, prefix in PREFIX.items()}
# The delta of a profile that relocates each allocation bound of `7mfk`.
BOUND_DELTA = {"free_rom_start": "rom_delta", "free_rom_end": "rom_delta",
               "injected_rom_start": "rom_delta", "injected_rom_end": "rom_delta",
               "free_ram_start": "ram_delta", "free_ram_end": "ram_delta",
               "injected_ram_start": "ram_delta", "injected_ram_end": "ram_delta"}
MAPPED, SPECIFIC, UNSUPPORTED = "mapped", "target-specific", "unsupported"


def _unhexed(value):
    """The addresses of a target value as integers."""
    if isinstance(value, str):
        return int(value, 16)
    if isinstance(value, dict):
        return {key: _unhexed(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_unhexed(item) for item in value]
    return value


def _held(model, key, layout, subject):
    """The symbol of a key that a target of `layout` names, on that layout."""
    symbol = model.symbols.get(key) if isinstance(key, SymbolKey) else None
    if symbol is None or symbol.layout != layout:
        raise KbError(f"{subject} name {getattr(key, 'key', key)}, which is no symbol of "
                      f"{layout}", code=3)
    return symbol


def _targets(model):
    """{layout: {feature: target}} of the model."""
    found = defaultdict(dict)
    for (feature, layout), target in model.targets.items():
        found[layout][feature] = target
    return found


def _stocks(model):
    """{hook symbol key: stock word}: the address on the layout of a word of
    the symbol of the meaning that the `target` link of the word names there."""
    found = {}
    for link in model.links:
        if link.type != "target":
            continue
        for layout in link.stated:
            owner, to = link.owner.symbols.get(layout), link.to.symbols.get(layout)
            if owner is None or owner.kind != "hook" or to is None:
                continue
            if found.setdefault(owner.key, to.address) != to.address:
                raise KbError(f"{owner.key.key}: target links name the stock words "
                              f"{found[owner.key]:08x} and {to.address:08x}", code=3)
    return found


def _chains(targets):
    """{word symbol key: [(feature, key, entry)]} of the hooks of the targets
    of a layout, in the order of the features."""
    found = defaultdict(list)
    for feature in FEATURES:
        target = targets.get(feature)
        for key, entry in (target.props.get("hooks", {}) if target else {}).items():
            found[entry["hook"]].append((feature, key, entry))
    return found


def _field_source(model, field):
    """The source meaning of a telemetry field."""
    entity = model.entities.get(("field", field))
    keys = list(entity.refs.get("source", ())) if entity is not None else []
    meaning = model.meaning_of(keys[0]) if len(keys) == 1 else None
    if meaning is None:
        raise KbError(f"the field {field} names no source meaning", code=3)
    return meaning


def _record_word(model, key, layout, subject):
    """The image word of a record: the value of the `rom-bytes` identity item
    at its symbol."""
    values = _bytes(_held(model, key, layout, subject))
    if not values:
        raise KbError(f"{subject}: {key.key} states no image bytes of its record", code=3)
    return int(values, 16)


def _bytes(symbol):
    """The value of the `rom-bytes` identity item at a symbol, or ""."""
    values = {item.get("value") for item in symbol.evidence
              if item.get("kind") == "rom-bytes"
              and item.get("supports", "identity") == "identity"
              and match.location(item.get("at")) == (symbol.layout, symbol.address)}
    if len(values) > 1:
        raise KbError(f"{symbol.key.key} states the image bytes {', '.join(sorted(values))}",
                      code=3)
    return values.pop() if values else ""


def profiles_document(model, fields, targets, stocks):
    """The document of `patches/rom-address-profiles.toml`: a profile of the
    image of each layout other than `7mfk` with a `runtime` target, and one
    that inherits it for each other image of the layout."""
    found = {}
    for layout in model.layouts.values():
        held = targets.get(layout.id, {})
        if layout.id == CANONICAL or RUNTIME not in held:
            continue
        found[layout.image] = _profile(model, layout, held, fields, stocks)
        found.update({image: {"inherits": layout.image}
                      for image in layout.images if image != layout.image})
    return {"schema_version": SCHEMA_VERSION, "profile": found}


def _profile(model, layout, targets, fields, stocks):
    """The profile of a layout from its targets: the runtime and map keys, the
    capabilities, the families, the hooks with the stock word of their
    `target` link and the replacement of the previous feature as their base,
    the DID slots of the allocations, the symbol tables with the non-field
    roles, the numbers, and the record words, the telemetry sources, the
    fields whose source has a status on the layout, and the basis."""
    subject = f"the targets of {layout.id}"
    runtime = targets[RUNTIME].props
    profile = {"family": layout.family, "layout_source": model.layouts[CANONICAL].image}
    profile.update({key: _unhexed(runtime[key]) if key in ADDRESS_KEYS else runtime[key]
                    for key in RUNTIME_KEYS if key in runtime})
    maps = targets.get(FEATURES[0])
    props = maps.props if maps is not None else {}
    profile.update({key: _unhexed(props[key]) if key in ADDRESS_KEYS else props[key]
                    for key in MAP_KEYS if key in props})
    profile["capabilities"] = {feature: targets[feature].status == "supported"
                               for feature in FEATURES if feature in targets}
    if "families" in props:
        profile["map_families"] = {key: _held(model, value, layout.id, subject).address
                                   for key, value in props["families"].items()}
    for word, chain in _chains(targets).items():
        symbol = _held(model, word, layout.id, subject)
        if word not in stocks:
            raise KbError(f"{symbol.key.key}: no target link states the stock word", code=3)
        stock = base = stocks[word]
        for feature, key, entry in chain:
            replacement = int(entry["replacement"], 16)
            value = [symbol.address, stock, replacement]
            if feature != FEATURES[0]:
                value[2:2] = [base]
            profile.setdefault(PROFILE_HOOKS[feature], {})[key] = value
            base = replacement
    rolling = targets.get("rolling_launch")
    diagnostics = {}
    for name, entry in (rolling.props.get("allocations", {}) if rolling else {}).items():
        if "did" in entry:
            did = _held(model, entry["did"], layout.id, subject)
            diagnostics[name] = [did.value("number"), did.address, int(entry["address"], 16),
                                 entry["width"]]
    if diagnostics:
        profile["rolling_diagnostics"] = diagnostics
    sources = {}
    for feature, table in PROFILE_SYMBOLS.items():
        target = targets.get(feature)
        if target is None:
            continue
        symbols = target.props.get("symbols", {})
        found = {key: _held(model, value, layout.id, subject).address
                 for key, value in symbols.items()}
        for key, role in target.props.get("roles", {}).items():
            address = _held(model, role["symbol"], layout.id, subject).address
            (sources if key in fields else found)[key] = address
        found.update({key: target.props[key] for key in CAN_KEYS if key in target.props})
        found.update({key: _record_word(model, symbols[record], layout.id, subject)
                      for key, record in ROM_BYTES.items() if record in symbols})
        if found:
            profile[table] = found
    if "can_telemetry" in targets:
        unavailable = []
        for field in fields:
            if field in sources:
                continue
            meaning = _field_source(model, field)
            symbol = meaning.symbols.get(layout.id)
            if symbol is not None:
                sources[field] = symbol.address
            elif layout.id in meaning.statuses:
                unavailable.append(field)
            else:
                raise KbError(f"the source {meaning.key} of the field {field} has neither a "
                              f"symbol nor a status on {layout.id}", code=3)
        profile["telemetry_sources"] = sources
        profile["telemetry_unavailable"] = unavailable
    basis = {}
    for feature in (RUNTIME, *FEATURES):
        if feature in targets:
            basis.update(targets[feature].props.get("basis", {}))
    if basis:
        profile["evidence"] = basis
    return profile


def _to(item):
    """(layout, address) that the `to` of an evidence item locates."""
    to = item.get("to")
    if isinstance(to, SymbolKey):
        return to.layout, to.address
    return match.location(to)


def row_item(symbol, subject):
    """(status, item) of the row of a symbol: its first evidence item that is
    homology evidence toward `7mfk`, `mapped`, or identity evidence of the
    symbol on its own layout other than image bytes, `target-specific`."""
    for item in symbol.evidence:
        kind, supports = item.get("kind"), item.get("supports", "identity")
        to = _to(item)
        if (supports == "homology" and kind in match.HOMOLOGY_KINDS and to is not None
                and to[0] == CANONICAL):
            return MAPPED, item
        if supports == "identity" and kind != "rom-bytes":
            at = match.location(item.get("at"))
            if at is None or at[0] == symbol.layout:
                return SPECIFIC, item
    raise KbError(f"{subject}: {symbol.key.key} has neither homology evidence toward "
                  f"{CANONICAL} nor identity evidence on {symbol.layout}", code=3)


def _text(value, subject):
    """The one text of a note."""
    texts = [value] if isinstance(value, str) else list(value or ())
    if len(texts) != 1 or not texts[0].strip():
        raise KbError(f"{subject}: {len(texts)} texts where the row takes one", code=3)
    return texts[0]


def _row(domain, key, source=None, target=None, stock="", variant="", status=SPECIFIC,
         text=""):
    return {"domain": domain, "key": key,
            "source": f"{source:08x}" if source is not None else "",
            "target": f"{target:08x}" if target is not None else "",
            "stock": stock, "variant": variant, "status": status, "evidence": text}


def _origin(symbol):
    """The address of the `7mfk` symbol of the meaning of a symbol, or None."""
    origin = symbol.meaning.symbols.get(CANONICAL) if symbol.meaning is not None else None
    return origin.address if origin is not None else None


def _symbol_row(domain, key, symbol, variants, subject):
    """The row of a symbol with the status and the note of its row item."""
    where = f"{subject}: {domain}:{key}"
    status, item = row_item(symbol, where)
    return _row(domain, key, _origin(symbol), symbol.address, _bytes(symbol),
                variants.get(symbol.key, ""), status, _text(item.get("note"), where))


def _map_domain(row):
    """`map` of a mapped table and `map_native` of a target-specific one."""
    if row["status"] == SPECIFIC:
        row["domain"] = "map_native"
    return row


def correspondence_rows(model, layout, targets, fields, stocks):
    """The rows of the correspondence file of a layout from its targets."""
    subject = f"the targets of {layout}"
    rows = []
    runtime = targets[RUNTIME].props
    canonical = model.targets.get((RUNTIME, CANONICAL))
    bounds = canonical.props if canonical is not None else {}
    for key, text in runtime.get("notes", {}).items():
        target = int(runtime[key], 16)
        source = int(bounds[key], 16) if key in bounds else None
        mapped = (source is not None
                  and (source + runtime[BOUND_DELTA[key]]) % (1 << 32) == target)
        rows.append(_row("allocation", key, source, target, status=MAPPED if mapped else SPECIFIC,
                         text=_text(text, f"{subject}: allocation:{key}")))
    chains = _chains(targets)
    for feature in FEATURES:
        target = targets.get(feature)
        if target is None:
            continue
        props, prefix = target.props, PREFIX[feature]
        home = model.targets.get((feature, CANONICAL))
        home = home.props if home is not None else {}
        variants = {entry["symbol"]: entry["variant"] for entry in props.get("variants", ())}
        for key, value in props.get("families", {}).items():
            rows.append(_map_domain(_symbol_row(
                "map", key, _held(model, value, layout, subject), variants, subject)))
        for key, entry in props.get("hooks", {}).items():
            symbol = _held(model, entry["hook"], layout, subject)
            where = f"{subject}: {prefix}_hook:{key}"
            status, item = row_item(symbol, where)
            first = chains[entry["hook"]][0][0] == feature
            rows.append(_row(f"{prefix}_hook", key, _origin(symbol), symbol.address,
                             f"{stocks[entry['hook']]:08x}", "", status,
                             _text(item.get("note") if first else entry.get("note"), where)))
        for key, value in props.get("symbols", {}).items():
            rows.append(_symbol_row(f"{prefix}_symbol", key,
                                    _held(model, value, layout, subject), variants, subject))
        for key, role in props.get("roles", {}).items():
            if key in fields:
                continue
            symbol = _held(model, role["symbol"], layout, subject)
            source = home.get("symbols", {}).get(key)
            rows.append(_row(f"{prefix}_symbol", key,
                             source.address if isinstance(source, SymbolKey) else None,
                             symbol.address, _bytes(symbol), "", SPECIFIC,
                             _text(role.get("note"), f"{subject}: role {key}")))
        for value in props.get("requires", ()):
            meaning = model.meaning_of(value)
            symbol = meaning.symbols.get(layout) if meaning is not None else None
            if symbol is None:
                raise KbError(f"{subject}: {feature} requires "
                              f"{meaning.key if meaning else value}, which has no symbol on "
                              f"{layout}", code=3)
            if feature == FEATURES[0] and meaning.kind == "tbl":
                rows.append(_map_domain(_symbol_row("map", meaning.name, symbol, variants,
                                                    subject)))
            else:
                rows.append(_symbol_row(f"{prefix}_symbol", meaning.name, symbol, variants,
                                        subject))
        for entry in props.get("unsupported", ()):
            meaning = model.meaning_of(entry["symbol"])
            origin = meaning.symbols.get(CANONICAL) if meaning is not None else None
            if origin is None:
                raise KbError(f"{subject}: an unsupported entry of {feature} names no meaning "
                              f"with a {CANONICAL} symbol", code=3)
            rows.append(_row("map" if feature == FEATURES[0] else f"{prefix}_symbol",
                             meaning.name, origin.address, status=UNSUPPORTED,
                             text=_text(entry.get("note"), f"{subject}: {meaning.key}")))
        for key, text in props.get("notes", {}).items():
            source, value = home.get(key), props.get(key)
            rows.append(_row(f"{prefix}_symbol", key, source, value,
                             status=MAPPED if source == value else SPECIFIC,
                             text=_text(text, f"{subject}: {prefix}_symbol:{key}")))
    can = targets.get("can_telemetry")
    roles = can.props.get("roles", {}) if can is not None else {}
    for field in fields:
        meaning = _field_source(model, field)
        origin = meaning.symbols.get(CANONICAL)
        source = origin.address if origin is not None else None
        where = f"{subject}: telemetry:{field}"
        if field in roles:
            symbol = _held(model, roles[field]["symbol"], layout, subject)
            rows.append(_row("telemetry", field, source, symbol.address,
                             text=_text(roles[field].get("note"), where)))
            continue
        symbol = meaning.symbols.get(layout)
        if symbol is not None:
            rows.append(_symbol_row("telemetry", field, symbol, {}, subject))
            continue
        status = meaning.statuses.get(layout)
        if status is None:
            raise KbError(f"{where}: {meaning.key} has neither a symbol nor a status", code=3)
        rows.append(_row("telemetry", field, source, status=UNSUPPORTED,
                         text=_text(status.props.get("note"), where)))
    for feature in FEATURES:
        target = targets.get(feature)
        if target is not None and target.props.get("note"):
            rows.append(_row("capability", feature,
                             text=_text(target.props["note"], f"{subject}: {feature}")))
    return rows


def render_registries(model):
    """{path: text} of the address profiles and of the correspondence file of
    each layout whose `runtime` target states the notes of its allocation
    rows."""
    fields = telemetry_fields(model.root)
    targets = _targets(model)
    stocks = _stocks(model)
    found = {PROFILES.as_posix(): render_profiles(
        profiles_document(model, fields, targets, stocks), fields)}
    for layout, held in sorted(targets.items()):
        if layout == CANONICAL or "notes" not in getattr(held.get(RUNTIME), "props", {}):
            continue
        path = PATCHES / f"{layout}{CORRESPONDENCE[1:]}"
        found[path.as_posix()] = render_correspondence(
            correspondence_rows(model, layout, held, fields, stocks), fields)
    return found


def address_profiles(root=repo.ROOT):
    """The text of `patches/rom-address-profiles.toml` from the model."""
    from kb import compile
    return render_registries(compile.cached(root))[PROFILES.as_posix()]


def correspondences(root=repo.ROOT):
    """{path: text} of the correspondence file of every layout from the model."""
    from kb import compile
    found = render_registries(compile.cached(root))
    del found[PROFILES.as_posix()]
    return found
