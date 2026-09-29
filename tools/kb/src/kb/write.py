"""Write commands (tools/kb/SPEC.md, section 12.3): `set`, `bind`, `absent`,
`unresolved`, `merge`, `move`, and `apply`, which applies a batch of them as
one change.

A change edits entity files as documents over the working tree. An operation
reads the file of its meaning from the change or from the disk, or starts it
with the entry of the home symbol, which joins the file with the registries
that state the meaning, and the change renders every document in canonical
form. A symbol that a file takes leaves `kb/names.csv`: its generated name
becomes the `name` of its entry in an unnamed meaning, and its other names
become `former` references.

- `set` writes keys of a meaning, of the entry of one of its symbols, of a
  designed entity, or of the target of a feature on a layout, after it
  removes the keys that `unset` names. A table joins the table of its key key
  by key, another value replaces the value of its key, and a dotted key names
  a key of a table. The names, symbols, statuses, links, and analogs of a
  meaning and the place and names of a symbol entry belong to the other
  commands.
- `bind` adds the symbol of a meaning on a layout without one. Its evidence is
  stated, or it is the evidence of the candidate that `match.search` finds at
  the address from a symbol of the meaning; a `to` that names a symbol becomes
  its location. The status of the layout leaves the file, and an unnamed
  meaning draws a generated name for the symbol and keeps its home.
- `absent` states with evidence that the mechanism does not exist on a layout.
- `unresolved` records the method, the target, and the count of the search
  from a symbol of the meaning, which finds no unique candidate, or of a
  stated search, with the L0 digest of the layout. A repeat of the search of
  the held status keeps its note unless the operation states one.
- `merge` joins another meaning into a meaning, or another file of one meaning
  into its file. Each symbol of the other meaning takes the evidence of the
  join, stated or found as `bind` finds it, and its entry moves into the file
  of the meaning, where a named meaning keeps its former name as a `former`
  reference. The statuses, keys, links, analogs, and former names of the other
  file join those of the file where they agree, the other file leaves the
  store, and every reference of the entity files to a name of the other
  meaning names the meaning.
- `move` corrects the address of a symbol on its layout. Its evidence is
  stated, or it is the evidence of the candidate that `match.search` finds at
  the address from another symbol of the meaning. The entry keeps its other
  keys, its previous full reference becomes its first `former` reference, and
  every reference and `[[...]]` citation of the entity files to that
  reference names the new one.

`plan` compiles the model with the rendered files in place of those on disk
and refuses the change with exit code 3 when the result has an issue of a
model check or a registry disagreement that the working tree lacks. `apply`
takes the lock, resolves the references on a current graph, plans, writes the
files through temporary files and renames, and loads the graph.
"""

import difflib
from pathlib import Path
import re
import tomllib
import weakref

from kb import checks, compile, graph, lock, match, names, refs, repo, store, vocab
from kb.model import MEANING_REF, SymbolKey
from kb.repo import KbError

# The keys of each operation of a batch besides `cmd`, and those it requires.
COMMANDS = {
    "set": ("ref", "layout", "keys", "unset"),
    "bind": ("meaning", "symbol", "evidence", "from", "level", "note"),
    "absent": ("meaning", "layout", "evidence", "note"),
    "unresolved": ("meaning", "layout", "from", "method", "target", "count", "note"),
    "merge": ("meaning", "other", "evidence", "from"),
    "move": ("symbol", "to", "evidence", "from", "level", "note"),
}
REQUIRED = {"set": ("ref",), "bind": ("meaning", "symbol"),
            "absent": ("meaning", "layout", "evidence"), "unresolved": ("meaning", "layout"),
            "merge": ("meaning", "other"), "move": ("symbol", "to")}
SEARCH = ("method", "target", "count")
# The keys that commands other than `set` write: the former names, symbols,
# statuses, links, and analogs of a meaning, and the place and the names of a
# symbol entry. A feature target takes every key besides its layout.
MEANING_OWNED = ("former", *(name for name, _ in store.ARRAYS))
ENTRY_OWNED = ("layout", "address", "name", "former")
SYMBOL_KEYS = {name: spec for name, spec in store.SYMBOL.keys if name not in ENTRY_OWNED}
# The keys of a meaning file that a merge joins by their own rules; the other
# keys move into a file that lacks them.
JOINED = ("symbol", "status", "link", "analog", "former", "home")
# The keys of a symbol entry that a merge of two entries of one symbol joins.
ENTRY = ("layout", "address", "name", "former", "evidence")
# A reference in a string of an entity file: the whole string, or a `[[...]]`
# citation of prose.
REFERENCE = re.compile(r"(?P<name>[a-z][a-z0-9_-]*)(?P<rest>/(?P<kind>[a-z]+)"
                       r"(?:/[0-9a-z]+(?:-[0-9a-f]{8})?)?)?")
CITATION = re.compile(r"\[\[(?P<ref>[^\[\]]+)\]\]")
_CHECKED = weakref.WeakKeyDictionary()


def parse_evidence(text):
    """An evidence item from a TOML inline table, with or without its braces."""
    body = text.strip()
    if not body.startswith("{"):
        body = "{" + body + "}"
    try:
        return tomllib.loads(f"item = {body}")["item"]
    except tomllib.TOMLDecodeError as error:
        raise KbError(f"evidence {text!r} is no TOML inline table: {error}", code=2) from None


def parse_assignments(texts):
    """(keys, unset) of `<key>=<value>` arguments: a value is a TOML value or
    else a string, an empty value unsets its key, and a dotted key names a key
    of a table."""
    keys, unset = {}, []
    for text in texts:
        name, sign, value = text.partition("=")
        parts = name.strip().split(".")
        if not sign or not all(store.BARE_KEY.fullmatch(part) for part in parts):
            raise KbError(f"{text!r} is not <key>=<value> with a bare or dotted key", code=2)
        if not value:
            unset.append(".".join(parts))
            continue
        try:
            value = tomllib.loads(f"value = {value}")["value"]
        except tomllib.TOMLDecodeError:
            pass
        table = keys
        for part in parts[:-1]:
            table = table.setdefault(part, {})
            if not isinstance(table, dict):
                raise KbError(f"{text!r} names a key of {part}, which another argument sets",
                              code=2)
        if parts[-1] in table:
            raise KbError(f"{text!r} sets {'.'.join(parts)} again", code=2)
        table[parts[-1]] = value
    return keys, unset


def read_batch(path):
    """The operations of a batch file: an array of `[[op]]` tables."""
    try:
        document = tomllib.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise KbError(f"no batch {path}: {error.strerror}", code=2) from None
    except tomllib.TOMLDecodeError as error:
        raise KbError(f"{path} is no TOML: {error}", code=2) from None
    ops = document.get("op")
    unknown = sorted(set(document) - {"op"})
    if not isinstance(ops, list) or not ops or unknown:
        raise KbError(f"{path}: a batch holds only [[op]] tables", code=2)
    return ops


def evidence_item(item):
    """A copy of a stated evidence item; exit code 2 when it lacks a key of its
    kind or has a key outside section 7.6."""
    if not isinstance(item, dict):
        raise KbError("an evidence item is a table", code=2)
    unknown = sorted(set(item) - set(vocab.EVIDENCE_KEYS))
    if unknown:
        raise KbError(f"evidence takes no {', '.join(unknown)}; its keys are "
                      f"{', '.join(vocab.EVIDENCE_KEYS)}", code=2)
    kind = item.get("kind")
    if kind not in vocab.EVIDENCE_KINDS:
        raise KbError(f"evidence kind {kind!r}; the kinds are "
                      f"{', '.join(vocab.EVIDENCE_KINDS)}", code=2)
    required, _ = vocab.EVIDENCE_KINDS[kind]
    lacking = [key for key in required if item.get(key) in (None, "")]
    if lacking:
        raise KbError(f"{kind} evidence needs {', '.join(lacking)}", code=2)
    if item.get("supports", "identity") not in vocab.SUPPORTS:
        raise KbError(f"supports {item['supports']!r}; the values are "
                      f"{', '.join(vocab.SUPPORTS)}", code=2)
    return dict(item)


def summary(item):
    """One line of an evidence item: its kind and keys, without prose."""
    parts = [item["kind"]]
    parts += [f"{key} {item[key]}" for key in vocab.EVIDENCE_KEYS
              if key not in ("kind", "supports", "note") and item.get(key) not in (None, "")]
    return " ".join(parts)


def renamed(value, others, kind, target, key=None):
    """(value, count): a value of an entity file with each reference to a name
    of `others` of `kind` naming `target` instead, and the count of the
    references it rewrites. A reference is a whole string `<name>/<kind>`
    with an optional layout and address, or a `[[...]]` citation of prose,
    where a bare generated name counts too; `former` records names and stays."""
    if key == "former":
        return value, 0
    if isinstance(value, dict):
        found, count = {}, 0
        for name, item in value.items():
            found[name], added = renamed(item, others, kind, target, name)
            count += added
        return found, count
    if isinstance(value, list):
        found, count = [], 0
        for item in value:
            item, added = renamed(item, others, kind, target, key)
            found.append(item)
            count += added
        return found, count
    if not isinstance(value, str):
        return value, 0
    whole = REFERENCE.fullmatch(value)
    if whole and whole.group("name") in others and whole.group("kind") == kind:
        return target + whole.group("rest"), 1
    count = 0

    def cite(found):
        nonlocal count
        inner = REFERENCE.fullmatch(found.group("ref").strip())
        if inner and inner.group("name") in others and (
                inner.group("kind") == kind or inner.group("kind") is None
                and vocab.GENERATED_NAME.fullmatch(inner.group("name"))):
            count += 1
            return f"[[{target}{inner.group('rest') or ''}]]"
        return found.group(0)

    return CITATION.sub(cite, value), count


def relocated(value, old, new, key=None):
    """(value, count): a value of an entity file with each full reference
    `old`, a whole string or a `[[...]]` citation, naming `new`, and the count
    of the references it rewrites; `former` records references and stays."""
    if key == "former":
        return value, 0
    if isinstance(value, dict):
        found, count = {}, 0
        for name, item in value.items():
            found[name], added = relocated(item, old, new, name)
            count += added
        return found, count
    if isinstance(value, list):
        found, count = [], 0
        for item in value:
            item, added = relocated(item, old, new, key)
            found.append(item)
            count += added
        return found, count
    if not isinstance(value, str):
        return value, 0
    if value == old:
        return new, 1
    count = 0

    def cite(found):
        nonlocal count
        if found.group("ref").strip() != old:
            return found.group(0)
        count += 1
        return f"[[{new}]]"

    return CITATION.sub(cite, value), count


def checked(spec, name, value):
    """A value of the key `name` by the spec of its schema: an array of tables
    holds tables of its schema, a table takes the keys of its schema and an
    evidence item those of section 7.6, a hexadecimal or DID key takes an
    integer, and a level key a level; exit code 2 otherwise."""
    if isinstance(spec, store.Array):
        if not isinstance(value, list):
            raise KbError(f"{name} is an array of tables", code=2)
        return [checked(spec.table, name, item) for item in value]
    if isinstance(spec, store.Table):
        if not isinstance(value, dict):
            raise KbError(f"{name} is a table", code=2)
        if spec is store.EVIDENCE:
            return evidence_item(value)
        known = [key for key, _ in spec.keys]
        unknown = sorted(set(value) - set(known))
        if unknown:
            raise KbError(f"{name} takes no {', '.join(unknown)}; its keys are "
                          f"{', '.join(known)}", code=2)
        return {key: checked(spec.spec(key), f"{name}.{key}", item)
                for key, item in value.items()}
    if spec in (store.HEX, store.DID) and (isinstance(value, bool) or not isinstance(value, int)):
        raise KbError(f"{name} is an integer", code=2)
    if name.rpartition(".")[2] in checks.LEVEL_KEYS and value not in vocab.LEVELS:
        raise KbError(f"{name} {value!r}; the levels are {', '.join(vocab.LEVELS)}", code=2)
    return value


def _merged(held, value):
    """`value` over `held`: two tables join key by key, and another value
    replaces the held one."""
    if isinstance(held, dict) and isinstance(value, dict):
        return {**held, **{key: _merged(held.get(key), item) for key, item in value.items()}}
    return value


def _paths(keys, prefix=""):
    """The dotted paths of the values that a table of keys writes."""
    found = []
    for name, value in keys.items():
        path = f"{prefix}{name}"
        found += _paths(value, f"{path}.") if isinstance(value, dict) and value else [path]
    return found


def _unset(table, path, subject):
    """Remove the key of a dotted path from a table, and the tables that the
    removal empties; exit code 3 when the table lacks the key."""
    parts = path.split(".")
    tables = [table]
    for part in parts[:-1]:
        held = tables[-1].get(part)
        if not isinstance(held, dict):
            raise KbError(f"{subject} has no {path}", code=3)
        tables.append(held)
    if parts[-1] not in tables[-1]:
        raise KbError(f"{subject} has no {path}", code=3)
    del tables[-1][parts[-1]]
    for part, parent, held in zip(reversed(parts[:-1]), reversed(tables[:-1]),
                                  reversed(tables[1:])):
        if held:
            break
        del parent[part]


def _union(items, added):
    return [*items, *(item for item in added if item not in items)]


def _link_key(link):
    return link.get("type"), link.get("to"), link.get("slot"), link.get("offset")


def joined_links(links):
    """Links with one entry for each type, target, slot, and offset whose
    other keys agree: the evidence of the entries joins in the order of its
    locations, and their lists join."""
    found = []
    for link in links:
        held = next((held for held in found if _link_key(held) == _link_key(link)
                     and all(held[key] == value for key, value in link.items()
                             if key in held and not isinstance(value, list))), None)
        if held is None:
            found.append(dict(link))
            continue
        for key, value in link.items():
            if key not in held:
                held[key] = value
            elif isinstance(value, list):
                held[key] = _union(held[key], value)
        held["evidence"] = sorted(held.get("evidence", ()), key=lambda item: str(item.get("at")))
    return found


def model_resolver(model):
    """A resolver over the model alone: a meaning key `<name>/<kind>` or a
    location `<layout>:<address>`, for callers without a graph."""
    meanings = {meaning.key: meaning for meaning in model.meanings}

    def resolve(text):
        place = refs.LOCATION.fullmatch(text)
        if place:
            found = [symbol for key, symbol in model.symbols.items()
                     if key.layout == place.group("layout")
                     and key.address == int(place.group("address"), 16)
                     and symbol.meaning is not None]
            if len(found) > 1:
                raise KbError(f"{text!r} names {len(found)} symbols", code=4)
            if found:
                return found[0].meaning, found[0]
        elif text in meanings:
            return meanings[text], None
        raise KbError(f"no meaning {text!r}", code=5)

    return resolve


def graph_resolver(session, model, root=repo.ROOT, log=print):
    """A resolver by the references of section 5.2 on a graph that the model
    loaded: (meaning, symbol, or None for a meaning reference)."""
    meanings = {meaning.key: meaning for meaning in model.meanings}

    def resolve(text):
        ref = refs.resolve(session, text, root=root)
        if ref.note:
            log(f"{text}: {ref.note}")
        if ref.kind == "symbol":
            symbol = model.symbols.get(SymbolKey(ref.layout, ref.node["kind"], ref.address))
            if symbol is not None and symbol.meaning is not None:
                return symbol.meaning, symbol
        elif ref.kind == "meaning" and ref.node["key"] in meanings:
            return meanings[ref.node["key"]], None
        elif ref.kind == "entity":
            raise KbError(f"{ref.text} is a designed entity, not a meaning", code=2)
        raise KbError(f"{text!r} names no meaning", code=5)

    return resolve


class Change:
    """The documents that operations edit over the model of the working tree,
    and one line per operation."""

    def __init__(self, model, resolve, root=repo.ROOT):
        self.model, self.resolve, self.root = model, resolve, root
        self.documents = {}
        self.removed = set()
        self.rows = {row.key: row for row in model.names}
        self.rows_changed = False
        self.lines = []
        self._taken = self._domain = None

    # Operations ------------------------------------------------------------

    def run(self, op, number=None):
        """Apply one operation; errors name its position in a batch."""
        try:
            if not isinstance(op, dict) or op.get("cmd") not in COMMANDS:
                cmd = op.get("cmd") if isinstance(op, dict) else None
                raise KbError(f"cmd {cmd!r}; the commands are {', '.join(COMMANDS)}", code=2)
            cmd = op["cmd"]
            unknown = sorted(set(op) - set(COMMANDS[cmd]) - {"cmd"})
            if unknown:
                raise KbError(f"{cmd} takes no {', '.join(unknown)}; its keys are "
                              f"{', '.join(COMMANDS[cmd])}", code=2)
            lacking = [key for key in REQUIRED[cmd] if op.get(key) in (None, "", [])]
            if lacking:
                raise KbError(f"{cmd} needs {', '.join(lacking)}", code=2)
            getattr(self, cmd)(op)
        except KbError as error:
            if number is None:
                raise
            raise KbError(f"op {number}: {error}", code=error.code) from None

    def set(self, op):
        keys, unset = op.get("keys") or {}, op.get("unset") or []
        if not isinstance(keys, dict) or not isinstance(unset, list) \
                or not all(isinstance(path, str) and path for path in unset):
            raise KbError("set takes keys as a table and unset as an array of dotted keys",
                          code=2)
        if not keys and not unset:
            raise KbError("set needs keys or unset", code=2)
        written = _paths(keys)
        both = sorted(set(written) & set(unset))
        if both:
            raise KbError(f"set writes and unsets {', '.join(both)}", code=2)
        table, specs, subject = self._settable(op["ref"], op.get("layout"))
        for name in [path.split(".", 1)[0] for path in unset] + list(keys):
            refused = name == "layout" if specs is None else name not in specs
            if refused:
                allowed = "every key besides layout" if specs is None else ", ".join(specs)
                raise KbError(f"set writes no {name} of {subject}; it writes {allowed}", code=2)
        for path in unset:
            _unset(table, path, subject)
        for name, value in keys.items():
            spec = specs.get(name) if specs is not None else None
            table[name] = _merged(table.get(name), checked(spec, name, value))
        parts = [", ".join(sorted(written))] if written else []
        parts += [f"unset {', '.join(sorted(unset))}"] if unset else []
        self.lines.append(f"set {subject}: {'; '.join(parts)}")

    def _settable(self, text, layout):
        """(table, {key: spec}, subject) of a reference of `set`: a designed
        entity, the target of a feature on `layout`, whose specs are None
        since it takes every key besides its layout, a meaning, or the entry
        of the symbol that the reference or `layout` names."""
        found = MEANING_REF.fullmatch(str(text).strip())
        if found and found.group("kind") in store.DESIGNED:
            kind, slug = found.group("kind"), found.group("name")
            if (kind, slug) not in self.model.entities:
                raise KbError(f"no designed entity {slug}/{kind}", code=5)
            _, document = self.designed(kind, slug)
            if layout is None:
                return document, {name: spec for name, spec in store.DESIGNED[kind].keys
                                  if not isinstance(spec, store.Array)}, f"{slug}/{kind}"
            if kind != "feature":
                raise KbError(f"a layout names a target of a feature; {slug}/{kind} is a {kind}",
                              code=2)
            layout = self._layout(layout)
            targets = [entry for entry in document.get("target", ())
                       if entry.get("layout") == layout]
            if not targets:
                raise KbError(f"{slug}/feature has no target on {layout}", code=5)
            return targets[0], None, f"{slug}/feature on {layout}"
        meaning, named = self.resolve(text)
        if layout is not None:
            layout = self._layout(layout)
            if named is not None and named.layout != layout:
                raise KbError(f"{self._ref(named)} lies on {named.layout}, not on {layout}",
                              code=2)
            named = meaning.symbols.get(layout)
            if named is None:
                raise KbError(f"{meaning.key} has no symbol on {layout}", code=5)
        _, document = self.document(meaning)
        if named is None:
            return document, {name: spec for name, spec in store.schema(meaning.kind).keys
                              if name not in MEANING_OWNED}, meaning.key
        return self._entry(meaning, document, named), SYMBOL_KEYS, self._ref(named)

    def bind(self, op):
        meaning, named = self.resolve(op["meaning"])
        layout, address = self._location(op["symbol"])
        self._free(meaning, layout)
        key = SymbolKey(layout, meaning.kind, address)
        held = self.model.symbols.get(key)
        if held is not None and held.meaning is not None:
            raise KbError(f"{key.location} is {self._ref(held)}; `kb merge` joins two "
                          "meanings", code=3)
        level = op.get("level")
        if level is not None and level not in vocab.LEVELS:
            raise KbError(f"level {level!r}; the levels are {', '.join(vocab.LEVELS)}", code=2)
        if op.get("evidence"):
            evidence = [evidence_item(item) for item in op["evidence"]]
        else:
            evidence = self._found(self._source(meaning, named, op.get("from")), key)
        path, document = self.document(meaning)
        name = meaning.name if meaning.semantic else self._draw()
        entry = {"layout": layout, "address": f"{address:08x}"}
        if not meaning.semantic:
            entry["name"] = name
            self._keep_home(meaning, [layout], document)
        entry.update({"level": level, "note": op.get("note"), "evidence": evidence})
        document["symbol"] = [*document.get("symbol", ()), entry]
        document["status"] = [status for status in document.get("status", ())
                              if status.get("layout") != layout]
        self.lines.append(f"bind {name}/{meaning.kind}/{layout}-{address:08x}: "
                          f"{'; '.join(summary(item) for item in evidence)}")

    def absent(self, op):
        meaning, _ = self.resolve(op["meaning"])
        layout = self._layout(op["layout"])
        evidence = [evidence_item(item) for item in op["evidence"]]
        self._free(meaning, layout)
        self._status(meaning, {"layout": layout, "state": "absent", "note": op.get("note"),
                               "evidence": evidence})
        self.lines.append(f"absent {meaning.key} on {layout}: "
                          f"{'; '.join(summary(item) for item in evidence)}")

    def unresolved(self, op):
        meaning, named = self.resolve(op["meaning"])
        layout = self._layout(op["layout"])
        self._free(meaning, layout)
        stated = [op.get(key) for key in SEARCH]
        if any(value is not None for value in stated):
            if any(value is None for value in stated):
                raise KbError("method, target, and count state a search together", code=2)
            method, target, count = stated
            try:
                count = int(count)
            except ValueError:
                raise KbError(f"count {count!r} is no integer", code=2) from None
        else:
            source = self._source(meaning, named, op.get("from"))
            found = match.search(self.model, source, layout)
            if found.count == 1:
                [address] = found.candidates
                raise KbError(
                    f"the {found.method} search from {source.key.location} finds one "
                    f"candidate, {layout}:{address:08x}; `kb bind {meaning.key} "
                    f"{layout}:{address:08x}` records it", code=3)
            method, target, count = found.method, found.target, found.count
        note = op.get("note")
        if note is None:
            # A repeat of the held search on a new L0 keeps the note of its status.
            _, document = self.document(meaning)
            held = next((entry for entry in document.get("status", ())
                         if entry.get("layout") == layout), {})
            if held.get("state") == "unresolved" and (
                    held.get("method"), held.get("target"), held.get("count")) == (
                    method, target, count):
                note = held.get("note")
        self._status(meaning, {"layout": layout, "state": "unresolved", "method": method,
                               "target": target, "count": count,
                               "l0": match.l0_digest(layout, self.root),
                               "note": note})
        self.lines.append(f"unresolved {meaning.key} on {layout}: {method} search of {target}, "
                          f"{count} matches")

    def merge(self, op):
        meaning, named, path = self._file_of(op["meaning"])
        other, _, other_path = self._file_of(op["other"])
        if meaning.kind != other.kind:
            raise KbError(f"{op['meaning']} is a {meaning.kind} meaning and {op['other']} a "
                          f"{other.kind} one", code=2)
        if meaning is other:
            self._merge_files(meaning, path, other_path, op)
        else:
            self._merge_meanings(meaning, named, other, other_path, op)

    def _merge_meanings(self, meaning, named, other, other_path, op):
        """Join the symbols and the file of `other` into `meaning`."""
        if other.semantic and not meaning.semantic:
            raise KbError(f"{other.key} has a semantic name and {meaning.key} a generated one; "
                          f"`kb merge {other.key} {meaning.key}` keeps the semantic name",
                          code=2)
        path, document = self.document(meaning)
        source = self._open(other_path) if other_path is not None else {}
        held = set(meaning.symbols) | {entry.get("layout") for entry in document.get("symbol", ())}
        for layout, symbol in sorted(other.symbols.items()):
            if layout in held:
                current = meaning.symbols.get(layout)
                raise KbError(
                    f"{meaning.key} has {self._ref(current) if current else 'a symbol'} on "
                    f"{layout}, where {other.key} has {self._ref(symbol)}; `kb move` corrects a "
                    "wrong symbol", code=3)
        stated = [evidence_item(item) for item in op.get("evidence") or ()]
        several = len(other.symbols) > 1
        if several and any((match.location(item.get("at")) or (None,))[0] not in other.symbols
                           for item in stated):
            raise KbError(f"{other.key} has {len(other.symbols)} symbols; each evidence item "
                          "names the layout of one in `at`", code=2)
        entries = {(entry.get("layout"), entry.get("address")): entry
                   for entry in source.get("symbol", ())}
        moved, joins = [], []
        for layout, symbol in sorted(other.symbols.items()):
            items = [item for item in stated
                     if not several or match.location(item.get("at"))[0] == layout]
            evidence = items or self._joining(meaning, named, op.get("from"), symbol)
            entry = entries.get((layout, f"{symbol.address:08x}"))
            entry = self._entry_of(meaning, other, symbol,
                                   dict(entry) if entry is not None
                                   else self.adopt(meaning, symbol))
            entry["evidence"] = _union(entry.get("evidence", []), evidence)
            moved.append(entry)
            joins.append(f"{symbol.key.location} {'; '.join(summary(item) for item in evidence)}")
        if not meaning.semantic:
            self._keep_home(meaning, [entry["layout"] for entry in moved], document)
        document["symbol"] = [*document.get("symbol", ()), *moved]
        layouts = set(meaning.symbols) | {entry.get("layout") for entry in document["symbol"]}
        formers = ([other.name] if other.semantic else []) + list(source.get("former", ()))
        self._absorb(document, source, layouts, meaning, formers if meaning.semantic else [],
                     meaning.name, f"{meaning.key} and {other.key}")
        if other_path is not None:
            self._remove(other_path)
        others = {other.name, *(symbol.generated for symbol in other.symbols.values()),
                  *(entry.get("name") for entry in source.get("symbol", ()))}
        count = self._rename(others - {None, meaning.name}, meaning.kind, meaning.name, path)
        self.lines.append(f"merge {other.key} into {meaning.key}: {', '.join(joins)}"
                          f"{self._renames(count)}")

    def _merge_files(self, meaning, path, other_path, op):
        """Join the file `other_path` of a meaning into its file `path`: an
        entry of one symbol in both joins, and the name of the other file
        becomes a former reference of that symbol."""
        if path is None or other_path is None or path == other_path:
            raise KbError(f"{op['meaning']} and {op['other']} name one meaning, {meaning.key}",
                          code=2)
        if op.get("evidence") or op.get("from"):
            raise KbError("the files of one meaning join without evidence", code=2)
        kind, own, name = meaning.kind, path.stem, other_path.stem
        semantic = bool(vocab.SEMANTIC_NAME.fullmatch(own))
        if not semantic and vocab.SEMANTIC_NAME.fullmatch(name):
            raise KbError(f"{name}/{kind} is a semantic name and {own}/{kind} a generated one; "
                          f"`kb merge {name}/{kind} {own}/{kind}` keeps the semantic name", code=2)
        document, source = self._open(path), self._open(other_path)
        symbols = document.setdefault("symbol", [])
        home = next((entry.get("layout") for entry in symbols if entry.get("name") == own), None)
        for entry in source.get("symbol", ()):
            layout, address = entry.get("layout"), entry.get("address")
            reference = f"{entry.get('name') or name}/{kind}/{layout}-{address}"
            held = next((item for item in symbols
                         if (item.get("layout"), item.get("address")) == (layout, address)), None)
            if held is None:
                if any(item.get("layout") == layout for item in symbols):
                    raise KbError(f"{path.as_posix()} and {other_path.as_posix()} hold two "
                                  f"symbols on {layout}; `kb move` corrects a wrong symbol",
                                  code=3)
                entry = dict(entry)
                if semantic:
                    entry.pop("name", None)
                    entry["former"] = _union([reference], entry.get("former", []))
                symbols.append(entry)
                continue
            for key, value in entry.items():
                if key in ENTRY:
                    continue
                if key not in held:
                    held[key] = value
                elif held[key] != value:
                    raise KbError(f"the entries of {layout}:{address} in {path.as_posix()} and "
                                  f"{other_path.as_posix()} disagree on {key}", code=3)
            current = f"{held.get('name') or own}/{kind}/{layout}-{address}"
            former = [reference] if reference != current else []
            held["former"] = _union(held.get("former", []),
                                    former + list(entry.get("former", ())))
            held["evidence"] = _union(held.get("evidence", []), entry.get("evidence", ()))
        layouts = {entry.get("layout") for entry in symbols}
        if not semantic and home is not None and "home" not in document:
            if ("7mfk" if "7mfk" in layouts else min(layouts)) != home:
                document["home"] = home
        formers = ([name] if vocab.SEMANTIC_NAME.fullmatch(name) else []) \
            + list(source.get("former", ()))
        self._absorb(document, source, layouts, None, formers if semantic else [], own,
                     f"{path.as_posix()} and {other_path.as_posix()}")
        self._remove(other_path)
        others = {name, *(entry.get("name") for entry in source.get("symbol", ()))}
        count = self._rename(others - {None, own}, kind, own, path)
        self.lines.append(f"merge {name}/{kind} into {own}/{kind}: {other_path.as_posix()} "
                          f"joins {path.as_posix()}{self._renames(count)}")

    def _joining(self, meaning, named, layout, symbol):
        """The evidence of the candidate at the address of a symbol that the
        search from a symbol of the meaning finds on the symbol's layout."""
        return self._found(self._source(meaning, named, layout), symbol.key)

    def _found(self, source, key):
        """The evidence of the candidate at the location of `key` that the
        search from the symbol `source` finds on its layout; exit code 3 with
        the candidates when the location is none."""
        found = match.search(self.model, source, key.layout)
        candidate = found.candidates.get(key.address)
        if candidate is None:
            listed = ", ".join(f"{key.layout}:{other:08x}" for other in sorted(found.candidates))
            raise KbError(
                f"the {found.method} search from {source.key.location} finds "
                f"{listed or 'no candidate'} on {key.layout}, not {key.location}; state the "
                "evidence", code=3)
        return [self._stored(candidate.evidence)]

    @staticmethod
    def _entry_of(meaning, other, symbol, entry):
        """The entry of a symbol of `other` in the file of `meaning`: a named
        meaning keeps the name of the symbol in `other` as the first former
        reference."""
        if not meaning.semantic:
            return entry
        name = entry.pop("name", None)
        current = other.name if other.semantic else name or symbol.generated
        former = [f"{current}/{symbol.kind}/{symbol.layout}-{symbol.address:08x}"] \
            if current else []
        former = _union(former, entry.get("former", ()))
        if former:
            entry["former"] = former
        return entry

    @staticmethod
    def _absorb(document, source, layouts, meaning, formers, own, pair):
        """Join the statuses, keys, links, analogs, and former names of the
        file `source` into `document`, whose meaning has symbols on `layouts`:
        a status of such a layout leaves both, and a status or key that both
        state, or that `meaning` states from a registry, agrees."""
        statuses = {entry.get("layout"): entry for entry in document.get("status", ())
                    if entry.get("layout") not in layouts}
        stated = meaning.statuses if meaning is not None else {}
        for entry in source.get("status", ()):
            layout = entry.get("layout")
            if layout in layouts:
                continue
            held = statuses.get(layout)
            state = (held.get("state") if held is not None
                     else stated[layout].state if layout in stated else None)
            if state is None:
                statuses[layout] = entry
            elif state != entry.get("state"):
                raise KbError(f"{pair} disagree on {layout}: {state} and {entry.get('state')}",
                              code=3)
        document["status"] = list(statuses.values())
        for key, value in source.items():
            if key in JOINED:
                continue
            current = document.get(key)
            if current is None and meaning is not None:
                current = meaning.props.get(key, meaning.tables.get(key))
            if current is None:
                document[key] = value
            elif current != value:
                raise KbError(f"{pair} disagree on {key}", code=3)
        analogs = {entry.get("to"): entry for entry in document.get("analog", ())}
        for entry in source.get("analog", ()):
            analogs.setdefault(entry.get("to"), entry)
        document["analog"] = list(analogs.values())
        document["link"] = [*document.get("link", ()), *source.get("link", ())]
        former = _union(document.get("former", []), [name for name in formers if name != own])
        if former:
            document["former"] = former

    def _rename(self, others, kind, target, own):
        """Rewrite the references of the entity files to a name of `others` of
        `kind` as references to `target`, join the links that the rewrite
        makes equal, and drop the links of the file `own` to its own meaning;
        returns the count of rewritten references."""
        paths = {path for _, _, path in store.files(self.root, self.model.overlay)}
        total = 0
        for path in sorted((paths | set(self.documents)) - self.removed,
                           key=lambda item: item.as_posix()):
            document = self.documents.get(path)
            if document is None:
                document = store.load(self.root, path, self.model.overlay)
            document, count = renamed(document, others, kind, target)
            if path == own:
                document["link"] = [
                    link for link in document.get("link", ())
                    if not ((found := REFERENCE.fullmatch(str(link.get("to"))))
                            and found.group("name") == target and found.group("kind") == kind)]
            if count or path == own:
                document["link"] = joined_links(document.get("link", ()))
                self.documents[path] = document
            total += count
        return total

    @staticmethod
    def _renames(count):
        return f"; {count} reference{'' if count == 1 else 's'} rewritten" if count else ""

    def move(self, op):
        meaning, named = self.resolve(op["symbol"])
        if named is None:
            raise KbError(f"{op['symbol']} names the meaning {meaning.key}; `kb move` takes one "
                          "of its symbols", code=2)
        layout, address = self._location(op["to"])
        if layout != named.layout:
            raise KbError(f"{self._ref(named)} lies on {named.layout}, not on {layout}; a symbol "
                          "moves within its layout", code=2)
        if address == named.address:
            raise KbError(f"{self._ref(named)} lies at {op['to']}", code=2)
        key = SymbolKey(layout, meaning.kind, address)
        held = self.model.symbols.get(key)
        if held is not None and held.meaning is not None:
            raise KbError(f"{key.location} is {self._ref(held)}; `kb merge` joins two "
                          "meanings", code=3)
        level = op.get("level")
        if level is not None and level not in vocab.LEVELS:
            raise KbError(f"level {level!r}; the levels are {', '.join(vocab.LEVELS)}", code=2)
        if op.get("evidence"):
            evidence = [evidence_item(item) for item in op["evidence"]]
        else:
            source = self._source(meaning, None, op.get("from"))
            if source is named:
                raise KbError(f"{self._ref(named)} is the home symbol of {meaning.key}; `from` "
                              "names the symbol that the search starts from, or the evidence "
                              "is stated", code=2)
            evidence = self._found(source, key)
        path, document = self.document(meaning)
        entry = self._entry(meaning, document, named)
        name = entry.get("name") or meaning.name
        old = f"{name}/{meaning.kind}/{layout}-{entry['address']}"
        new = f"{name}/{meaning.kind}/{layout}-{address:08x}"
        entry["address"] = f"{address:08x}"
        entry["former"] = _union([old], entry.get("former", []))
        entry["evidence"] = evidence
        entry.update({item: op[item] for item in ("level", "note") if op.get(item) is not None})
        count = self._relocate(old, new)
        self.lines.append(f"move {old} to {key.location}: "
                          f"{'; '.join(summary(item) for item in evidence)}"
                          f"{self._renames(count)}")

    def _entry(self, meaning, document, symbol):
        """The entry of a symbol in the document of its meaning, the one entry
        of its layout, which an earlier operation of the change may have
        moved; the symbol of a registry enters the document."""
        for entry in document.get("symbol", ()):
            if entry.get("layout") == symbol.layout:
                return entry
        entry = self.adopt(meaning, symbol)
        document["symbol"] = [*document.get("symbol", ()), entry]
        return entry

    def _relocate(self, old, new):
        """Rewrite the references of the entity files to the full reference
        `old` as references to `new`; returns their count."""
        paths = {path for _, _, path in store.files(self.root, self.model.overlay)}
        total = 0
        for path in sorted((paths | set(self.documents)) - self.removed,
                           key=lambda item: item.as_posix()):
            document = self.documents.get(path)
            if document is None:
                document = store.load(self.root, path, self.model.overlay)
            document, count = relocated(document, old, new)
            if count:
                self.documents[path] = document
            total += count
        return total

    # Documents -------------------------------------------------------------

    def texts(self):
        """{repository path: text, or None for a file that leaves the store} of
        the files that the change rewrites."""
        found = {}
        for path, document in self.documents.items():
            text = store.render(path.parent.name, document)
            if self._current(path) != text:
                found[path] = text
        for path in self.removed:
            if self._current(path) is not None:
                found[path] = None
        if self.rows_changed:
            text = names.render(self.rows.values())
            if self._current(names.PATH) != text:
                found[names.PATH] = text
        return dict(sorted(found.items(), key=lambda item: item[0].as_posix()))

    def diff(self, texts):
        """The unified diff of `texts` against the working tree."""
        out = []
        for path, text in texts.items():
            before = self._current(path) or ""
            out.extend(difflib.unified_diff(
                before.splitlines(keepends=True), (text or "").splitlines(keepends=True),
                f"a/{path.as_posix()}" if before else "/dev/null",
                f"b/{path.as_posix()}" if text is not None else "/dev/null"))
        return "".join(out)

    def _current(self, path):
        """The text of a file in the base of the change: the overlay of its
        model, or else the working tree; None for no file."""
        if path in self.model.overlay:
            return self.model.overlay[path]
        target = self.root / path
        return target.read_text(encoding="utf-8") if target.exists() else None

    def document(self, meaning):
        """(path, document) of the file of a meaning; a meaning without one
        starts a file with the entry of its home symbol."""
        path = self._path(meaning)
        if path is None:
            path = store.path_of(meaning.kind, meaning.name)
            if path not in self.documents and self._current(path) is not None:
                raise KbError(f"{path.as_posix()} holds another meaning than {meaning.key}",
                              code=3)
        if path not in self.documents:
            if self._current(path) is not None:
                self._open(path)
            else:
                self.documents[path] = {"symbol": [self.adopt(meaning, meaning.home_symbol)]}
        return path, self.documents[path]

    def _path(self, meaning):
        """The file of a meaning: the file of its name, or else its only file."""
        held = self.model.files.get((meaning.kind, meaning.name))
        if held is not None and held[0] is meaning:
            return Path(held[1])
        return next((Path(src) for owner, src in self.model.files.values()
                     if owner is meaning), None)

    def _file_of(self, text):
        """(meaning, symbol or None, path of its file or None) of a reference;
        `<name>/<kind>` of a meaning file names that file, so that the files of
        one meaning resolve apart."""
        found = MEANING_REF.fullmatch(str(text).strip())
        held = found and self.model.files.get((found.group("kind"), found.group("name")))
        if held and held[0] is not None:
            return held[0], None, Path(held[1])
        meaning, symbol = self.resolve(text)
        return meaning, symbol, self._path(meaning)

    def _open(self, path):
        """The document of an entity file of the change or the working tree."""
        if path in self.removed:
            raise KbError(f"{path.as_posix()} leaves the store in this change", code=3)
        if path not in self.documents:
            self.documents[path] = store.load(self.root, path, self.model.overlay)
        return self.documents[path]

    def _remove(self, path):
        self.documents.pop(path, None)
        self.removed.add(path)

    def designed(self, kind, slug):
        """(path, document) of the file of a designed entity; an entity without
        one starts an empty file."""
        path = store.path_of(kind, slug)
        if path not in self.documents:
            self.documents[path] = ({} if self._current(path) is None
                                    else store.load(self.root, path, self.model.overlay))
        return path, self.documents[path]

    def adopt(self, meaning, symbol):
        """The entry of a symbol that a registry states; its row of
        `kb/names.csv` moves into the entry."""
        entry = {"layout": symbol.layout, "address": f"{symbol.address:08x}"}
        row = self.rows.pop((symbol.layout, symbol.kind, symbol.address), None)
        former = list(row.former) if row else []
        if row is not None:
            self.rows_changed = True
        if not meaning.semantic:
            entry["name"] = row.name if row else symbol.generated or self._draw()
        elif row is not None:
            former.insert(0, row.name)
        if former:
            entry["former"] = [f"{name}/{symbol.kind}/{symbol.layout}-{symbol.address:08x}"
                               for name in former]
        return entry

    def _status(self, meaning, status):
        _, document = self.document(meaning)
        kept = [entry for entry in document.get("status", ())
                if entry.get("layout") != status["layout"]]
        document["status"] = kept + [status]

    @staticmethod
    def _keep_home(meaning, layouts, document):
        """Pin the home of an unnamed meaning, whose name is the generated name
        of its home symbol, when symbols on `layouts` would move it."""
        if "home" in meaning.props or "home" in document:
            return
        layouts = set(meaning.symbols) | set(layouts)
        after = "7mfk" if "7mfk" in layouts else min(layouts)
        if after != meaning.home:
            document["home"] = meaning.home

    # Arguments -------------------------------------------------------------

    def _layout(self, text):
        return repo.layout(str(text), self.root).id

    def _location(self, text):
        found = refs.LOCATION.fullmatch(str(text).strip())
        if not found:
            raise KbError(f"{text!r} is not <layout>:<address>", code=2)
        return self._layout(found.group("layout")), int(found.group("address"), 16)

    def _free(self, meaning, layout):
        """Refuse a layout where the meaning has a symbol."""
        symbol = meaning.symbols.get(layout)
        if symbol is not None:
            raise KbError(f"{meaning.key} has {self._ref(symbol)} on {layout}; `kb move` "
                          "corrects a wrong symbol", code=3)

    def _source(self, meaning, named, layout):
        """The symbol that a search starts from: that of `from`, the symbol
        that the reference names, or the home symbol."""
        if layout is not None:
            symbol = meaning.symbols.get(self._layout(layout))
            if symbol is None:
                raise KbError(f"{meaning.key} has no symbol on {layout}", code=5)
            return symbol
        symbol = named or meaning.home_symbol
        if symbol is None:
            raise KbError(f"{meaning.key} has no symbol to search from", code=5)
        return symbol

    @staticmethod
    def _ref(symbol):
        return f"{symbol.name or '?'}/{symbol.kind}/{symbol.layout}-{symbol.address:08x}"

    @staticmethod
    def _stored(item):
        """An evidence item of a search with a symbol `to` as its location."""
        found = dict(item)
        if isinstance(found.get("to"), SymbolKey):
            found["to"] = found["to"].location
        return found

    def _draw(self):
        if self._taken is None:
            self._taken = names.Taken(names.reserved(self.model, self.model.names))
            self._domain = names.domain_dictionary(self.model, self.root)
        attempts = self.model.config.get("names", {}).get("attempts", 1000)
        return names.draw(self._taken, self._domain, attempts)


def _issues(model):
    """{(check, subject, message): issue} of the model checks and the registry
    disagreements of a model, computed once per model."""
    if model not in _CHECKED:
        found = {}
        for check in checks.CHECKS.values():
            for issue in check(model):
                found.setdefault((issue.check, issue.subject, issue.message), issue)
        for issue in checks.audit(model, ("disagreements",))["disagreements"]:
            found.setdefault(("audit", issue.subject, issue.message), issue)
        _CHECKED[model] = found
    return _CHECKED[model]


def refusals(base, result):
    """The issues of the model checks and the registry disagreements of
    `result` that `base` lacks."""
    before, after = _issues(base), _issues(result)
    return [issue for key, issue in sorted(after.items()) if key not in before]


def plan(ops, base, resolve, root=repo.ROOT):
    """(change, texts, result) of operations over the model `base` of the
    working tree and its overlay; exit code 3 when the result adds an issue."""
    change = Change(base, resolve, root)
    for number, op in enumerate(ops, 1):
        change.run(op, number if len(ops) > 1 else None)
    texts = change.texts()
    result = compile.build(root, {**base.overlay, **texts})
    refused = refusals(base, result)
    if refused:
        lines = [f"the change adds {len(refused)} issues; nothing is written"]
        lines += [f"  {issue.check}: {issue.path}: {issue.subject}: {issue.message}"
                  for issue in refused]
        raise KbError("\n".join(lines), code=3)
    return change, texts, result


def apply(ops, root=repo.ROOT, dry_run=False, log=print):
    """Apply operations as one change under the lock; returns (change, texts).
    A dry run plans and writes nothing."""
    with lock.held(root):
        with graph.fresh(root, log=log, held=True) as session:
            base = compile.build(root)
            change, texts, result = plan(ops, base, graph_resolver(session, base, root, log),
                                         root)
        if not dry_run and texts:
            store.write(root, texts)
            compile.cached.cache_clear()
            graph.sync_held(root, False, log, result)
    return change, texts
