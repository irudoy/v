"""Address profiles and runtime correspondence (tools/kb/SPEC.md, sections 20.1
and 20.3).

- The symbol tables of `patches/runtime_targets.py` give the `7mfk` symbols of
  their keys, and its hook-key tables join the per-layout keys of a map hook to
  its canonical key. The module is read with `ast`, not imported.
- Each image profile of `patches/rom-address-profiles.toml` gives the symbols
  of its layout: a symbol-table key names the meaning at its address, a
  telemetry source the source meaning of its field, and a hook the ROM word
  that its features redirect, which joins the `7mfk` word of its canonical key
  (`kb.adapters.layouts`). The other keys go to the targets of `runtime`,
  `map_switching`, `rolling_launch`, and `can_telemetry`.
- A row of `patches/<layout>-runtime-correspondence.csv` joins its target
  symbol to the meaning of its source symbol, and an `unsupported` row gives a
  status.
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
"""

import ast
from collections import defaultdict
import csv
import io
from pathlib import Path
import re
import tomllib

from kb import store
from kb.adapters import layouts, telemetry
from kb.repo import KbError
from kb.values import hexed

PROFILES = Path("patches/rom-address-profiles.toml")
RUNTIME_TARGETS = Path("patches/runtime_targets.py")
PATCHES = Path("patches")
CORRESPONDENCE = "*-runtime-correspondence.csv"
CANONICAL = "7mfk"
FEATURES = layouts.FEATURES
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


def inputs(root):
    found = [PROFILES.as_posix(), RUNTIME_TARGETS.as_posix()]
    found += layouts.inputs(root)
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


def _value(key, value):
    return hexed(value) if key in ADDRESS_KEYS else value


def _state(text):
    return "unresolved" if UNRESOLVED.search(text or "") else "absent"


class Profiles:
    """The facts of the registries of this adapter, before they enter the model."""

    def __init__(self, b, root):
        self.tables = runtime_tables(root)
        self.document = tomllib.loads((root / PROFILES).read_text(encoding="utf-8"))
        self.layouts_doc = layouts.documents(root)
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
        self.roles = self._roles()
        self.canonical_map_keys = layouts.canonical_keys(self.layouts_doc)
        # The `7mfk` words, which the layouts state.
        self.canonical_words = {hook.address
                                for hook in layouts.canonical_hooks(self.layouts_doc)}
        self.hooks = self._hooks()
        self.words = layouts.words(self.hooks)

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

    def hook_keys(self, profile):
        """{per-layout key: canonical key} of the map hooks of a profile."""
        table = HOOK_KEYS.get(profile.get("map_variant"), VQ37_HOOK_KEYS)
        return {value: key for key, value in self.tables[table].items()}

    def _hooks(self):
        found = []
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
    layouts.declare_words(b, facts.words, targets, facts.canonical_map_keys)
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


def _declare_dids(b, facts, targets):
    src = PROFILES.as_posix()
    layouts.declare_dids(b, [
        (layout, name, did, pointer, target, width, src)
        for layout, (rom, profile) in facts.profiles.items()
        for name, (did, pointer, target, width) in profile.get("rolling_diagnostics", {}).items()],
        targets)


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
                found[(layout, name)] = b.symbol(layout, kind, address, src, group=group)
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


def _declare_profiles(b, facts, targets, notes):
    """Keys of the feature targets; returns the unavailable fields that no
    correspondence row states."""
    src = PROFILES.as_posix()
    pending = []
    for layout, (rom, profile) in sorted(facts.profiles.items()):
        runtime = targets[(RUNTIME, layout)]
        runtime.update({key: _value(key, profile[key]) for key in RUNTIME_KEYS if key in profile})
        for key in MAP_KEYS:
            if key in profile:
                targets[("map_switching", layout)][key] = _value(key, profile[key])
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
                     "address": hexed(target)})
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
            if facts.roles.get((layout, row["key"]), (None, None))[1] is row:
                role = entry.setdefault("roles", {}).setdefault(row["key"], {})
                role.update({"symbol": b.symbol(layout, kind, target, path), "note": text})
                if source is not None and domain == "telemetry":
                    b.symbol(CANONICAL, kind, source, path, group=(kind, "field", row["key"]),
                             strength="field")
                elif source is not None:
                    b.symbol(CANONICAL, kind, source, path, group=(kind, "key", row["key"]))
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
    if source is not None and source in facts.canonical_words:
        other = b.symbol(CANONICAL, "hook", source, path)
        b.join(other, key, where, "homology" if row["status"] == "mapped" else "role")


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
