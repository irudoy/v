"""Canonical native writer with locked validation and supported batch operations.

Historical evidence is retained as data. Stock-proof publication and
qualification operations belong to the local archive.
"""

import copy
import difflib
import random
from pathlib import Path
import re
import tomllib

from kb import (checks, compile, evidence_ref, graph, ledger_projection, lock, match, names, refs, repo,
                store, tokens, vocab)
from kb.adapters import files as file_adapter
from kb.allocation import allocation_phase
from kb.model import MEANING_REF, Meaning, Symbol, SymbolKey
from kb.repo import KbError

# The keys of each operation of a batch besides `cmd`, and those it requires.
COMMANDS = {'new': ('kind', 'symbol', 'slug', 'name', 'evidence', 'level', 'note'),
 'set': ('ref', 'layout', 'keys', 'unset'),
 'bind': ('meaning', 'symbol', 'evidence', 'from', 'level', 'note'),
 'absent': ('meaning', 'layout', 'evidence', 'note'),
 'unresolved': ('meaning', 'layout', 'from', 'method', 'target', 'count', 'note'),
 'link': ('meaning', 'type', 'to', 'keys', 'evidence'),
 'unlink': ('meaning', 'type', 'to', 'keys'),
 'set-link': ('meaning', 'type', 'to', 'selector', 'keys', 'unset'),
 'select': ('meaning', 'registry', 'order', 'dependency'),
 'merge': ('meaning', 'other', 'evidence', 'from'),
 'rename': ('meaning', 'name'),
 'move': ('symbol', 'to', 'evidence', 'from', 'level', 'note'),
 'retire': ('ref', 'withdraw_ledger'),
 'rebase-reviews': ('layout', 'from_l0', 'reasons_reviewed')}
REQUIRED = {'new': ('kind',),
 'set': ('ref',),
 'bind': ('meaning', 'symbol'),
 'absent': ('meaning', 'layout', 'evidence'),
 'unresolved': ('meaning', 'layout'),
 'link': ('meaning', 'type', 'to'),
 'unlink': ('meaning', 'type', 'to'),
 'set-link': ('meaning', 'type', 'to'),
 'select': ('meaning', 'registry', 'order', 'dependency'),
 'merge': ('meaning', 'other'),
 'rename': ('meaning', 'name'),
 'move': ('symbol', 'to'),
 'retire': ('ref',),
 'rebase-reviews': ('layout', 'from_l0')}
SEARCH = ("method", "target", "count")
# The keys of a link besides its type, target, and evidence, and those that
# choose among the links of one type and target.
LINK_KEYS = {name: spec for name, spec in store.LINK.keys
             if name not in ("type", "to", "evidence")}
LINK_CHOICE = ("slot", "offset")
LINK_VOCABULARY = {"relies": vocab.RELIES, "reverse_relies": vocab.RELIES,
                   "supports": vocab.SUPPORTS, "reverse_supports": vocab.SUPPORTS}
# The keys of a link that hold arrays, and those whose values join those of the
# held link; the other keys agree with it.
LINK_LISTS = ("via", "layouts")
LINK_JOINED = (*LINK_LISTS, "supports", "reverse_supports")
# The keys that commands other than `set` write: the former names, symbols,
# statuses, links, and analogs of a meaning, and the place and the names of a
# symbol entry.
MEANING_OWNED = ("retired", "former", *(name for name, _ in store.ARRAYS))
# The keys of every feature target (tools/kb/SPEC.md, section 7.9); a target
# also takes the keys that a target of its feature states.
TARGET_KEYS = ("layout", "status", "note", "basis", "requires", "unsupported")
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
    if key in ("former", "research"):
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


def relocated(value, moves, key=None):
    """(value, count): a value of an entity file with each reference of
    `moves` {old: new}, a whole string or a `[[...]]` citation, naming its new
    reference, and the count of the references it rewrites; `former` records
    references and stays."""
    if key in ("former", "research"):
        return value, 0
    if isinstance(value, dict):
        found, count = {}, 0
        for name, item in value.items():
            found[name], added = relocated(item, moves, name)
            count += added
        return found, count
    if isinstance(value, list):
        found, count = [], 0
        for item in value:
            item, added = relocated(item, moves, key)
            found.append(item)
            count += added
        return found, count
    if not isinstance(value, str):
        return value, 0
    if value in moves:
        return moves[value], 1
    count = 0

    def cite(found):
        nonlocal count
        new = moves.get(found.group("ref").strip())
        if new is None:
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
    if spec == store.TEXT and not isinstance(value, str):
        raise KbError(f"{name} is a string", code=2)
    if spec == store.INTEGER and (isinstance(value, bool) or not isinstance(value, int)):
        raise KbError(f"{name} is an integer", code=2)
    if spec == store.BOOLEAN and not isinstance(value, bool):
        raise KbError(f"{name} is a boolean", code=2)
    if spec == store.STRINGS and (not isinstance(value, list)
                                 or any(not isinstance(item, str) for item in value)):
        raise KbError(f"{name} is an array of strings", code=2)
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


def _bare(keys, subject, prefix=""):
    """Refuse a key at any depth of `keys` that is no bare key; a quoted key
    of dotted bare parts names the nested key that it spells."""
    for name, value in keys.items():
        if not store.BARE_KEY.fullmatch(name):
            parts = name.split(".")
            nested = (f", and the nested key {prefix}{name} names a key of a table"
                      if len(parts) > 1 and all(store.BARE_KEY.fullmatch(part) for part in parts)
                      else "")
            raise KbError(f'set writes no "{name}" of {subject}; a key is bare{nested}', code=2)
        for item in value if isinstance(value, list) else [value]:
            if isinstance(item, dict):
                _bare(item, subject, f"{prefix}{name}.")


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


def _listed(value):
    return value if isinstance(value, list) else [value]


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
        self.model, self._resolve, self.root = model, resolve, root
        self.documents = {}
        self.removed = set()
        self.rows = {row.key: row for row in model.names}
        self.rows_changed = False
        self.lines = []
        self.review_text = None
        # {meaning key: new key} of the renames of the change, the symbols
        # and the (kind, slug) of the designed entities that `new` starts, and
        # the checks of the compiled result that the operations expect, each a
        # function of the result that returns a message when the result
        # contradicts it.
        self.renamed = {}
        self.created, self.started = set(), set()
        # Private objects for meanings created in the change. The source
        # model stays intact until the complete rendered change is checked.
        self.new_meanings = {}
        self.bound_meanings = {}
        self.expected = []
        self._taken = self._domain = None

    def resolve(self, text):
        """Resolve pending bindings and new meanings against their documents,
        retaining source object identities and refusing ambiguous references."""
        text = str(text).strip()
        pending = self._pending_references(text)
        full = refs.FULL.fullmatch(text)
        if full:
            key = SymbolKey(full.group("layout"), full.group("kind"),
                            int(full.group("address"), 16))
            symbol = self._pending_symbol(key)
            if symbol is not None and symbol.meaning is not None:
                return symbol.meaning, symbol
        if not pending:
            return self._resolve(text)
        try:
            existing = self._resolve(text)
        except KbError as error:
            if error.code != 5:
                raise
        else:
            # A named reference takes precedence over a bare hexadecimal
            # address, including when that address was created in the batch.
            if refs.ADDRESS.fullmatch(text) and text in self._reference_names(existing[0]) \
                    and not any(text in self._reference_names(meaning) for meaning, _ in pending):
                return existing
            if not any(meaning is existing[0]
                       and (symbol.key if symbol is not None else None)
                       == (existing[1].key if existing[1] is not None else None)
                       for meaning, symbol in pending):
                pending.append(existing)
        if len(pending) != 1:
            raise KbError(f"{text!r} names {len(pending)} entities", code=4)
        return pending[0]

    def _symbols(self, meaning):
        """Original symbols and pending bindings of a meaning. New symbols are
        reconstructed from their entries so later assignments remain visible;
        the source meaning and its original symbols stay unchanged."""
        new = self.new_meanings.get(meaning.key) is meaning
        symbols = {} if new else dict(meaning.symbols)
        path = self._path(meaning)
        document = self.documents.get(path, {})
        for entry in document.get("symbol", ()):
            layout = entry["layout"]
            if not new and layout in meaning.symbols:
                continue
            key = SymbolKey(layout, meaning.kind, int(entry["address"], 16))
            symbols[layout] = Symbol(
                key, props={name: value for name, value in entry.items() if name not in ENTRY},
                evidence=entry.get("evidence", []), sources={path.as_posix()}, implicit=False,
                name=entry.get("name") or meaning.name, generated=entry.get("name"),
                former=tuple(entry.get("former", ())), meaning=meaning)
        return symbols

    def _pending_symbol(self, key):
        """The held symbol at a location, including earlier batch bindings."""
        for meaning in (*self.new_meanings.values(), *self.bound_meanings.values()):
            symbol = self._symbols(meaning).get(key.layout)
            if symbol is not None and symbol.key == key:
                return symbol
        return self.model.symbols.get(key)

    def _pending_references(self, text):
        """Meaning and symbol references among the pending documents."""
        full = refs.FULL.fullmatch(text)
        location = refs.LOCATION.fullmatch(text)
        named = refs.NAMED.fullmatch(text)
        address = refs.ADDRESS.fullmatch(text)
        found, addressed = [], []
        for meaning in (*self.new_meanings.values(), *self.bound_meanings.values()):
            path = self._path(meaning)
            if path not in self.documents:
                continue
            document = self.documents[path]
            symbols = self._symbols(meaning)
            if self.new_meanings.get(meaning.key) is meaning:
                meaning.props = {key: value for key, value in document.items()
                                 if key not in {name for name, _ in store.ARRAYS}}
                meaning.symbols = symbols
            if full:
                found.extend((meaning, symbol) for symbol in symbols.values()
                             if symbol.layout == full.group("layout")
                             and symbol.kind == full.group("kind")
                             and full.group("name") in {
                                 symbol.name, *(former.partition("/")[0]
                                                for former in symbol.former)})
                continue
            if location or address:
                match = location or address
                addressed.extend((meaning, symbol) for symbol in symbols.values()
                                 if symbol.address == int(match.group("address"), 16)
                                 and (location is None or symbol.layout == location.group("layout")))
            if named:
                name, second, third = named.group("name", "second", "third")
                kind = second if second in vocab.KINDS else None
                layout = third if kind else second
                aliases = self._reference_names(meaning, symbols)
                if name not in aliases or (kind is not None and kind != meaning.kind):
                    continue
                generated = [symbol for symbol in symbols.values()
                             if symbol.generated == name and name != meaning.name]
                if generated:
                    found.extend((meaning, symbol) for symbol in generated)
                    continue
                if layout is None:
                    found.append((meaning, None))
                elif layout in symbols:
                    found.append((meaning, symbols[layout]))
        return found or addressed

    @staticmethod
    def _reference_names(meaning, symbols=None):
        symbols = meaning.symbols if symbols is None else symbols
        return Change._names(meaning, symbols) | {
            former.partition("/")[0] for symbol in symbols.values()
            for former in symbol.former}

    # Operations ------------------------------------------------------------

    def rebase_reviews(self, op):
        from kb import reconciliation

        current = (compile.build(self.root, {**self.model.overlay, **self.texts()})
                   if self.review_text is not None else self.model)
        text, lines = reconciliation.rebase_export(
            current, op['layout'], op['from_l0'],
            reasons_reviewed=op.get('reasons_reviewed', False))
        if text is not None:
            self.review_text = text
        self.lines.extend(lines)

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
            getattr(self, cmd.replace("-", "_"))(op)
        except KbError as error:
            if number is None:
                raise
            raise KbError(f"op {number}: {error}", code=error.code) from None

    def new(self, op):
        kind = op["kind"]
        if kind not in vocab.KINDS:
            raise KbError(f"kind {kind!r}; the kinds are {', '.join(vocab.KINDS)}", code=2)
        if (op.get("symbol") is None) == (op.get("slug") is None):
            raise KbError("new takes a symbol <layout>:<address> or a slug", code=2)
        if op.get("slug") is not None:
            self._new_entity(kind, op)
        else:
            self._new_meaning(kind, op)

    def _new_meaning(self, kind, op):
        """A meaning file with the symbol at a location that holds none, with
        the evidence of its identity on its layout: named by `name`, or else
        by the generated name of the symbol, which its row of `kb/names.csv`
        gives or a draw."""
        if kind not in vocab.MEANING_KINDS:
            raise KbError(f"a {kind} is a designed entity; `kb new {kind} <slug>` starts one",
                          code=2)
        layout, address = self._location(op["symbol"])
        key = SymbolKey(layout, kind, address)
        if key in self.created:
            raise KbError(f"{key.location} starts a meaning earlier in this change", code=3)
        held = self._pending_symbol(key)
        if held is not None and held.meaning is not None:
            hint = "" if held.meaning.semantic else (
                f"; `kb rename {held.meaning.key} <semantic-name>` names its meaning")
            raise KbError(f"{key.location} is {self._ref(held)}{hint}", code=3)
        if not op.get("evidence"):
            raise KbError("new needs the evidence of the identity of the symbol on its layout",
                          code=2)
        evidence = [evidence_item(item) for item in op["evidence"]]
        level = op.get("level")
        if level is not None and level not in vocab.LEVELS:
            raise KbError(f"level {level!r}; the levels are {', '.join(vocab.LEVELS)}", code=2)
        row = self.rows.get((layout, kind, address))
        former = [row.name, *row.former] if row is not None else []
        entry = {"layout": layout, "address": f"{address:08x}"}
        name = op.get("name")
        if name is not None:
            self._semantic(name, kind)
        else:
            name = former.pop(0) if former else self._draw(key)
            entry["name"] = name
        path = store.path_of(kind, name)
        self._fresh(path)
        if row is not None:
            del self.rows[(layout, kind, address)]
            self.rows_changed = True
        if former:
            entry["former"] = [f"{item}/{kind}/{layout}-{address:08x}" for item in former]
        entry.update({"level": level, "note": op.get("note"), "evidence": evidence})
        self.documents[path] = {"symbol": [entry]}
        self.created.add(key)
        meaning = Meaning(kind, name, semantic=op.get("name") is not None,
                          sources={path.as_posix()},
                          name_sources=(path.as_posix(),) if op.get("name") is not None else ())
        self.new_meanings[meaning.key] = meaning
        self.lines.append(f"new {name}/{kind}/{layout}-{address:08x}: "
                          f"{'; '.join(summary(item) for item in evidence)}")

    def _new_entity(self, kind, op):
        """An empty file of a designed entity of a kind that the store holds."""
        slug = op["slug"]
        if kind not in vocab.DESIGNED_KINDS:
            raise KbError(f"a {kind} meaning starts with a symbol: `kb new {kind} "
                          "<layout>:<address>`", code=2)
        if op.get("name") is not None:
            raise KbError("a designed entity takes its slug as its name", code=2)
        stated = [key for key in ("evidence", "level", "note") if op.get(key)]
        if stated:
            raise KbError(f"a designed entity takes no {', '.join(stated)}", code=2)
        if not isinstance(slug, str) or not self._grammar(slug):
            raise KbError(f"{slug!r} is no slug: 3 to 48 characters of "
                          "[a-z][a-z0-9]*(_[a-z0-9]+)*", code=2)
        if kind not in file_adapter.CONVERTED_KINDS:
            raise KbError(f"the store holds no {kind} entities before their conversion stage",
                          code=3)
        if (kind, slug) in self.model.entities:
            raise KbError(f"{slug}/{kind} exists", code=3)
        path = store.path_of(kind, slug)
        self._fresh(path)
        self.documents[path] = {}
        self.started.add((kind, slug))
        self.lines.append(f"new {slug}/{kind}")

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
        table, specs, subject, hint = self._settable(op["ref"], op.get("layout"))
        _bare(keys, subject)
        whole = isinstance(specs, str)
        for name in [path.split(".", 1)[0] for path in unset] + list(keys):
            refused = name == 'retired' or (name == specs if whole else name not in specs)
            if refused:
                allowed = f"every key besides {specs}" if whole else ", ".join(specs)
                raise KbError(f"set writes no {name} of {subject}; it writes {allowed}{hint}",
                              code=2)
        for path in unset:
            _unset(table, path, subject)
        for name, value in keys.items():
            spec = None if whole else specs.get(name)
            table[name] = _merged(table.get(name), checked(spec, name, value))
        parts = [", ".join(sorted(written))] if written else []
        parts += [f"unset {', '.join(sorted(unset))}"] if unset else []
        self.lines.append(f"set {subject}: {'; '.join(parts)}")

    def _settable(self, text, layout):
        """(table, specs, subject, hint) of a reference of `set`: a designed
        entity, the target of a feature on `layout`, a meaning, or the entry
        of the symbol that the reference or `layout` names. The specs are
        {key: spec} of the keys that the table takes, or else the one key that
        it refuses where it takes every other: `target` of a feature, whose
        file states the facts of the feature under keys of its own. A target
        takes the keys of every target and those that a target of its feature
        states besides its layout; the hint of a refused key says that a new
        one needs a declared key schema. A designed entity is one of the
        working tree or one that an earlier `new` of the change starts, so
        that a batch starts an entity with its keys."""
        found = MEANING_REF.fullmatch(str(text).strip())
        if found and found.group("kind") in store.DESIGNED:
            kind, slug = found.group("kind"), found.group("name")
            if (kind, slug) not in self.model.entities and (kind, slug) not in self.started:
                raise KbError(f"no designed entity {slug}/{kind}", code=5)
            _, document = self.designed(kind, slug)
            if layout is None and kind == "feature":
                return document, "target", f"{slug}/{kind}", ""
            if layout is None:
                return document, dict(store.DESIGNED[kind].keys), f"{slug}/{kind}", ""
            if kind != "feature":
                raise KbError(f"a layout names a target of a feature; {slug}/{kind} is a {kind}",
                              code=2)
            layout = self._layout(layout)
            targets = [entry for entry in document.get("target", ())
                       if entry.get("layout") == layout]
            if not targets:
                raise KbError(f"{slug}/feature has no target on {layout}", code=5)
            known = [*TARGET_KEYS[1:], *sorted({name for entry in document["target"]
                                                for name in entry} - set(TARGET_KEYS))]
            return (targets[0], {name: store.TARGET.spec(name) for name in known},
                    f"{slug}/feature on {layout}",
                    "; a new target key needs a declared key schema of the feature")
        meaning, named = self.resolve(text)
        if layout is not None:
            layout = self._layout(layout)
            if named is not None and named.layout != layout:
                raise KbError(f"{self._ref(named)} lies on {named.layout}, not on {layout}",
                              code=2)
            named = self._symbols(meaning).get(layout)
            if named is None:
                raise KbError(f"{meaning.key} has no symbol on {layout}", code=5)
        _, document = self.document(meaning)
        if named is None:
            return document, {name: spec for name, spec in store.schema(meaning.kind).keys
                              if name not in MEANING_OWNED}, meaning.key, ""
        return self._entry(meaning, document, named), SYMBOL_KEYS, self._ref(named), ""


    def bind(self, op):
        meaning, named = self.resolve(op["meaning"])
        layout, address = self._location(op["symbol"])
        self._free(meaning, layout)
        key = SymbolKey(layout, meaning.kind, address)
        held = self._pending_symbol(key)
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
        name = meaning.name if meaning.semantic else self._draw(key)
        entry = {"layout": layout, "address": f"{address:08x}"}
        if not meaning.semantic:
            entry["name"] = name
            self._keep_home(meaning, [layout], document)
        entry.update({"level": level, "note": op.get("note"), "evidence": evidence})
        document["symbol"] = [*document.get("symbol", ()), entry]
        document["status"] = [status for status in document.get("status", ())
                              if status.get("layout") != layout]
        if self.new_meanings.get(meaning.key) is not meaning:
            self.bound_meanings[meaning.key] = meaning
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
                               "l0": match.search_digest(layout, self.root),
                               "note": note})
        self.lines.append(f"unresolved {meaning.key} on {layout}: {method} search of {target}, "
                          f"{count} matches")

    def link(self, op):
        meaning, to, type_ = self._ends(op)
        owners, targets = vocab.LINK_TYPES[type_]
        if meaning.kind not in owners or to.kind not in targets:
            raise KbError(f"the {type_} type joins {'/'.join(owners)} to {'/'.join(targets)}, "
                          f"not {meaning.kind} to {to.kind}", code=2)
        keys = self._link_keys(op.get("keys"), tuple(LINK_KEYS))
        if type_ == "depends" and "role" not in keys:
            raise KbError("a depends link states its role", code=2)
        evidence = [evidence_item(item) for item in op.get("evidence") or ()]
        _, document = self.document(meaning)
        links = document.setdefault("link", [])
        entry = {"type": type_, "to": to.key, **keys}
        held = next((link for link in links if self._same_link(link, entry, to)), None)
        if held is None:
            if evidence:
                entry["evidence"] = evidence
            links.append(entry)
        else:
            added = {}
            for name, value in keys.items():
                if name not in held:
                    added[name] = value
                elif name in LINK_JOINED:
                    joined = _union(_listed(held[name]), _listed(value))
                    if joined != _listed(held[name]):
                        added[name] = joined
                elif held[name] != value:
                    raise KbError(f"the {type_} link of {meaning.key} to {to.key} holds {name} = "
                                  f"{held[name]!r}; `kb unlink` removes it", code=3)
            evidence = [item for item in evidence if item not in held.get("evidence", ())]
            if not added and not evidence:
                raise KbError(f"{meaning.key} has this {type_} link to {to.key}", code=3)
            held.update(added)
            if evidence:
                held["evidence"] = [*held.get("evidence", ()), *evidence]
        described = "; ".join(summary(item) for item in evidence) or "no evidence"
        self.lines.append(f"link {meaning.key} {type_} {to.key}: {described}")

    def set_link(self, op):
        """Replace mutable properties or archive equivalent evidence refs in place."""
        meaning, to, type_ = self._ends(op)
        if any(op.get(name) is not None and not isinstance(op[name], dict)
               for name in ("selector", "keys")):
            raise KbError("set-link selector and keys are tables", code=2)
        selector = self._link_keys(op.get("selector"), LINK_CHOICE)
        if "slot" in selector and (not isinstance(selector["slot"], str)
                                   or not selector["slot"]):
            raise KbError("set-link slot is a nonempty string", code=2)
        if "offset" in selector and selector["offset"] < 0:
            raise KbError("set-link offset is nonnegative", code=2)
        allowed = tuple(key for key in LINK_KEYS if key not in LINK_CHOICE)
        archive = "evidence" in (op.get("keys") or {})
        if archive:
            if set(op["keys"]) != {"evidence"} or op.get("unset") not in (None, []):
                raise KbError("set-link archives evidence without other property changes", code=2)
            evidence = op["keys"]["evidence"]
            if not isinstance(evidence, list) or not evidence:
                raise KbError("set-link archives a nonempty evidence array", code=2)
            keys = {"evidence": [evidence_item(item) for item in evidence]}
        else:
            keys = self._link_keys(op.get("keys"), allowed)
        unset = [] if op.get("unset") is None else op["unset"]
        if not isinstance(unset, list) or not all(isinstance(key, str) and key in allowed
                                                  for key in unset):
            raise KbError("set-link unsets only mutable property names", code=2)
        if len(set(unset)) != len(unset) or set(keys) & set(unset):
            raise KbError("set-link has repeated or conflicting unset keys", code=2)
        if not keys and not unset:
            raise KbError("set-link needs keys or unset", code=2)
        _, _, path = self._file_of(op["meaning"])
        if path is None or not any(owner is meaning and src is not None and Path(src) == path
                                   for owner, src in self.model.files.values()):
            raise KbError(f"{meaning.key}: set-link needs an existing owned file", code=3)
        entry = {"type": type_, "to": to.key, **selector}
        source = store.load(self.root, path, self.model.overlay)
        original = [link for link in source.get("link", ())
                    if self._same_link(link, entry, to)]
        if len(original) != 1:
            raise KbError(f"{meaning.key}: set-link needs one existing native relation; "
                          f"found {len(original)}", code=3)
        held_offset = original[0].get("offset")
        if held_offset is not None and (isinstance(held_offset, bool)
                                        or not isinstance(held_offset, int)
                                        or held_offset < 0):
            raise KbError("set-link native offset is a nonnegative integer", code=3)
        document = self._open(path)
        selected = [link for link in document.get("link", ())
                    if self._same_link(link, entry, to)]
        if len(selected) != 1:
            raise KbError(f"{meaning.key}: set-link needs one current native relation; "
                          f"found {len(selected)}", code=3)
        held = selected[0]
        if archive:
            if not evidence_ref.archive_equivalent(original[0], {**original[0], **keys}):
                raise KbError("set-link only replaces evidence refs with equivalent stock archive refs",
                              code=2)
            if not evidence_ref.archive_equivalent(original[0], held):
                raise KbError(f"{meaning.key}: set-link retains the original relation and evidence",
                              code=3)
            if not evidence_ref.archive_equivalent(held, {**held, **keys}):
                raise KbError("set-link cannot restore or replace archived evidence", code=2)
        immutable = ("type", "to", "slot", "offset", "evidence")
        if not archive and ({key: held[key] for key in immutable if key in held}
                != {key: original[0][key] for key in immutable if key in original[0]}):
            raise KbError(f"{meaning.key}: set-link retains the original identity and evidence",
                          code=3)
        if any(key not in held for key in unset):
            missing = next(key for key in unset if key not in held)
            raise KbError(f"{meaning.key}: the selected link has no {missing}", code=3)

        def dependencies(document):
            return [(marker.get("registry"), marker.get("order"), marker.get("binding"),
                     copy.deepcopy(marker["dependency"]))
                    for marker in document.get("ledger", ()) if "dependency" in marker]

        owned = {
            Path(src): store.load(self.root, Path(src), self.model.overlay)
            for owner, src in self.model.files.values()
            if src is not None and (owner is meaning or owner is to)}
        selectors = {src: dependencies(document) for src, document in owned.items()}
        claims = []
        archive_claims = []
        for owner, src in self.model.files.values():
            if src is None or (owner is not meaning and owner is not to):
                continue
            for marker in store.load(self.root, Path(src), self.model.overlay).get("ledger", ()):
                for item in marker.get("dependency", ()):
                    other = to if owner is meaning else meaning
                    end = "owner" if owner is meaning else "to"
                    if (item.get("type") == type_ and item.get("end") == end
                            and self.resolve(item.get("to"))[0] is other
                            and item.get("offset", 0 if type_ == "base" else None)
                            == held.get("offset", 0 if type_ == "base" else None)):
                        claim = (owner.key, marker["registry"], marker["order"],
                                 copy.deepcopy(item))
                        if archive:
                            _, symbol, _, _ = _selection_row(self.model, *claim[:3])
                            projected = ledger_projection.dependency(self.model, symbol, item)
                            archive_claims.append((claim, projected))
                        else:
                            _selection(self.model, *claim)
                            claims.append(claim)
        for key in unset:
            del held[key]
        held.update(keys)
        expected = copy.deepcopy(held)
        identity = _link_key(expected)

        def retained(result):
            try:
                final = store.load(self.root, path, result.overlay)
                found = [link for link in final.get("link", ()) if _link_key(link) == identity]
                if found != [expected]:
                    return f"{meaning.key}: updated native link is not retained"
                for claim in claims:
                    _selection(result, *claim)
                for claim, projected in archive_claims:
                    _, symbol, _, _ = _selection_row(result, *claim[:3])
                    if ledger_projection.dependency(result, symbol, claim[3]) != projected:
                        return f"{meaning.key}: set-link does not retain ledger claims"
                for src, before in selectors.items():
                    current = store.load(self.root, src, result.overlay)
                    if dependencies(current) != before:
                        return f"{meaning.key}: set-link does not retain ledger dependencies"
                    if archive:
                        previous, updated = owned[src].get("link", []), current.get("link", [])
                        if len(previous) != len(updated) or any(
                            set(old) != set(new) or not evidence_ref.archive_equivalent(
                                {**old, "evidence": old.get("evidence", [])},
                                {**new, "evidence": new.get("evidence", [])})
                            for old, new in zip(previous, updated)):
                            return f"{meaning.key}: set-link does not retain native relations"
            except (KbError, OSError, TypeError, AttributeError, KeyError):
                return f"{meaning.key}: set-link does not retain its owned documents"
            return None

        self.expected.append(retained)
        self.lines.append(f"set-link {meaning.key} {type_} {to.key}")

    def unlink(self, op):
        meaning, to, type_ = self._ends(op)
        keys = self._link_keys(op.get("keys"), LINK_CHOICE)
        document = self._held(meaning) or {}
        links = document.get("link", [])
        found = [link for link in links if self._same_link(link, {"type": type_, **keys}, to,
                                                           keys=tuple(keys))]
        if not found:
            stated = sorted({src for link in meaning.links
                             if link.type == type_ and link.to is to for src in link.sources
                             if not src.startswith(f"{store.TREE.as_posix()}/")})
            if stated:
                raise KbError(f"{', '.join(stated)} states the {type_} link of {meaning.key} to "
                              f"{to.key}; a registry owns its facts until its conversion",
                              code=3)
            raise KbError(f"{meaning.key} has no {type_} link to {to.key}", code=5)
        if len(found) > 1:
            choices = "; ".join(", ".join(f"{name} = {link[name]!r}" for name in LINK_CHOICE
                                          if name in link) or "no slot or offset"
                                for link in found)
            raise KbError(f"{meaning.key} has {len(found)} {type_} links to {to.key} ({choices}); "
                          "slot or offset chooses one", code=4)
        document["link"] = [link for link in links if link is not found[0]]
        self._unselect_link(meaning, to, found[0])
        self.lines.append(f"unlink {meaning.key} {type_} {to.key}")

    def _unselect_link(self, meaning, to, removed):
        """Remove ledger selectors of this relation at both claiming ends."""
        type_ = removed["type"]
        offset = removed.get("offset", 0) if type_ == "base" else None
        for subject, other, end in ((meaning, to, "owner"), (to, meaning, "to")):
            document = self._held(subject)
            if document is None:
                continue
            for marker in document.get("ledger", ()):
                marker["dependency"] = [
                    item for item in marker.get("dependency", ())
                    if not (item.get("end") == end
                            and self._same_link(item, {"type": type_}, other, keys=())
                            and (item.get("offset", 0) if type_ == "base" else None)
                            == offset)]
                if (subject is meaning and type_ == "reader"
                        and removed.get("role") == "accessor"):
                    marker["fields"] = [field for field in marker.get("fields", ())
                                        if field != "accessor"]

    def select(self, op):
        registry, order = op["registry"], op["order"]
        if not isinstance(registry, str) or registry not in ledger_projection.HEADERS:
            raise KbError(f"invalid ledger registry {registry!r}", code=2)
        if isinstance(order, bool) or not isinstance(order, int) or order < 0:
            raise KbError("a ledger order is a nonnegative integer", code=2)
        item = checked(store.LEDGER_DEPENDENCY, "dependency", op["dependency"])
        required = ("role", "to", "type", "end", "relies", "supports")
        if any(not isinstance(item.get(key), str) or not item[key] for key in required):
            raise KbError("dependency needs string role, to, type, end, relies, and supports",
                          code=2)
        if ("link_role" in item and not isinstance(item["link_role"], str)
                or "offset_text" in item and (not isinstance(item["offset_text"], str)
                                               or "offset" not in item)
                or "offset" in item and item["offset"] < 0):
            raise KbError("invalid dependency link_role or offset spelling", code=2)
        meaning, _ = self.resolve(op["meaning"])
        to, _ = self.resolve(item["to"])
        self._gate(meaning)
        self._gate(to)
        item["to"] = to.key
        _, _, original_path, _ = _selection_row(self.model, meaning.key, registry, order)
        texts = self.texts()
        current = (compile.build(self.root, {**self.model.overlay, **texts})
                   if texts else self.model)
        path, marker = _selection(current, meaning.key, registry, order, item)
        if path != original_path:
            raise KbError(f"{meaning.key}: ledger row changes its owned file", code=3)
        selected = marker.get("dependency", ())
        def identity(entry):
            return (*(entry.get(key) for key in ("role", "to", "type", "end", "link_role")),
                    entry.get("offset", 0) if entry.get("type") == "base"
                    else entry.get("offset"))

        same = [entry for entry in selected
                if identity(entry) == identity(item)]
        if same and (len(same) != 1 or same[0] != item):
            raise KbError(f"{meaning.key}: incompatible or duplicate ledger dependency", code=3)
        if not same:
            document = self._open(path)
            [held] = [entry for entry in document.get("ledger", ())
                      if entry.get("registry") == registry and entry.get("order") == order]
            held["dependency"] = [*held.get("dependency", ()), item]

        def retained(result):
            try:
                final_path, final = _selection(result, meaning.key, registry, order, item)
                same = [entry for entry in final.get("dependency", ())
                        if identity(entry) == identity(item)]
                if final_path != original_path or same != [item]:
                    return f"{meaning.key}: selected ledger dependency is not retained"
            except KbError as error:
                return str(error)
            return None

        self.expected.append(retained)
        self.lines.append(f"select {meaning.key} {registry} {order}")

    def _ends(self, op):
        """(meaning, to, type) of a link operation."""
        meaning, _ = self.resolve(op["meaning"])
        to, _ = self.resolve(op["to"])
        type_ = op["type"]
        if type_ not in vocab.LINK_TYPES:
            raise KbError(f"link type {type_!r}; the types are {', '.join(vocab.LINK_TYPES)}",
                          code=2)
        if to is meaning and type_ != "base":
            raise KbError(f"{op['meaning']} and {op['to']} name {meaning.key}; a link joins two "
                          "meanings", code=2)
        self._gate(meaning)
        self._gate(to)
        return meaning, to, type_

    def _link_keys(self, keys, allowed):
        """Checked keys of a link among `allowed`; exit code 2 for another key
        or a value against its schema or vocabulary."""
        keys = keys or {}
        if not isinstance(keys, dict):
            raise KbError("the keys of a link are a table", code=2)
        found = {}
        for name, value in keys.items():
            if name not in allowed:
                raise KbError(f"a link takes no {name} here; the keys are {', '.join(allowed)}",
                              code=2)
            value = checked(LINK_KEYS[name], name, value)
            if name in LINK_LISTS and not isinstance(value, list):
                raise KbError(f"{name} is an array", code=2)
            if name in LINK_VOCABULARY:
                # `supports` and `reverse_supports` join into arrays, and the
                # dependency of `relies` is one value.
                for item in value if isinstance(value, list) and name in LINK_JOINED else [value]:
                    if item not in LINK_VOCABULARY[name]:
                        raise KbError(f"{name} {item!r}; the values are "
                                      f"{', '.join(LINK_VOCABULARY[name])}", code=2)
            if name == "layouts":
                value = [self._layout(item) for item in value]
            found[name] = value
        return found

    def _same_link(self, link, entry, to, keys=LINK_CHOICE):
        """Whether a link of a file has the type and the keys of `entry` and
        names the meaning `to`: by its name, a generated name of one of its
        symbols, or one of its other names."""
        found = REFERENCE.fullmatch(str(link.get("to")))
        return link.get("type") == entry["type"] and found is not None \
            and found.group("kind") == to.kind and found.group("name") in self._names(to) \
            and all(link.get(name) == entry.get(name) for name in keys)

    def merge(self, op):
        meaning, named, path = self._file_of(op["meaning"])
        other, _, other_path = self._file_of(op["other"])
        if meaning.kind != other.kind:
            raise KbError(f"{op['meaning']} is a {meaning.kind} meaning and {op['other']} a "
                          f"{other.kind} one", code=2)
        self._gate(meaning)
        self._gate(other)
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
        makes equal, and drop non-base links of `own` to its own meaning;
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
                    if link.get("type") == "base" or not (
                            (found := REFERENCE.fullmatch(str(link.get("to"))))
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
        if refs.LOCATION.fullmatch(str(op["to"]).strip()):
            self._move_address(meaning, named, op)
        else:
            self._move_meaning(meaning, named, op)

    def _move_meaning(self, meaning, named, op):
        """Move a symbol into the meaning that `to` names: its entry leaves the
        file of its meaning and enters the file of the target, and the result
        must join it with the symbols of the target alone."""
        target, via = self.resolve(op["to"])
        old = self._ref(named)
        if target is meaning:
            raise KbError(f"{old} is a symbol of {meaning.key}", code=2)
        if target.kind != meaning.kind:
            raise KbError(f"{old} is a {meaning.kind} symbol and {target.key} a {target.kind} "
                          "meaning", code=2)
        self._gate(meaning)
        self._gate(target)
        layout = named.layout
        if len(meaning.symbols) == 1:
            raise KbError(f"{old} is the only symbol of {meaning.key}; `kb merge` joins the two "
                          "meanings", code=3)
        if named is meaning.home_symbol and not meaning.semantic:
            raise KbError(f"{old} is the home symbol of {meaning.key} and gives its name; `kb "
                          f"rename {meaning.key} <semantic-name>` names the meaning first", code=3)
        if meaning.props.get("home") == layout:
            raise KbError(f"the home of {meaning.key} is {layout}; `kb set {meaning.key} home=` "
                          "unsets it first", code=3)
        self._free(target, layout)
        level = op.get("level")
        if level is not None and level not in vocab.LEVELS:
            raise KbError(f"level {level!r}; the levels are {', '.join(vocab.LEVELS)}", code=2)
        if op.get("evidence"):
            evidence = [evidence_item(item) for item in op["evidence"]]
        else:
            evidence = self._found(self._source(target, via, op.get("from")), named.key)
        generated, former, keys = self._release(meaning, named)
        path, document = self.document(target)
        kind, address = named.kind, f"{named.address:08x}"
        entry = {"layout": layout, "address": address}
        if target.semantic:
            name = target.name
            if generated:
                former = [f"{generated}/{kind}/{layout}-{address}", *former]
        else:
            name = generated or self._draw(named.key)
            entry["name"] = name
            self._keep_home(target, [layout], document)
        current = f"{name}/{kind}/{layout}-{address}"
        former = [item for item in _union([old], former) if item != current]
        if former:
            entry["former"] = former
        entry.update(keys)
        entry.update({item: op[item] for item in ("level", "note") if op.get(item) is not None})
        entry["evidence"] = evidence
        document["symbol"] = [*document.get("symbol", ()), entry]
        document["status"] = [status for status in document.get("status", ())
                              if status.get("layout") != layout]
        # A reference to the symbol by a name of its former meaning on its
        # layout, or by its previous full reference, names it in the target.
        moves = {f"{item}/{kind}/{layout}": f"{name}/{kind}/{layout}"
                 for item in self._names(meaning) if item != name}
        moves[old] = current
        count = self._relocate({key: value for key, value in moves.items() if key != value})
        if generated and target.semantic:
            count += self._rename({generated}, kind, target.name, path)
        joined = {symbol.key for symbol in target.symbols.values()}
        apart = {symbol.key for symbol in meaning.symbols.values() if symbol is not named}

        def expect(result):
            found = result.meaning_of(named.key)
            if found is None or any(result.meaning_of(key) is not found for key in joined) \
                    or any(result.meaning_of(key) is found for key in apart):
                return (f"move {old} to {target.key}: the compiled model does not join the "
                        f"symbol with {target.key} alone; `kb raw {old}` shows the registry rows "
                        "that state it, and the move waits for their conversion")
            left = sorted({getattr(result.meaning_of(key), "key", "?") for key in apart})
            if found.key != target.key or left != [meaning.key]:
                return (f"move {old} to {target.key}: the compiled model names the meanings "
                        f"{found.key} and {', '.join(left)}; a registry name of the symbol moves "
                        "with it, and the move waits for the conversion of that registry")
            return None

        self.expected.append(expect)
        named_as = f" as {current}" if name != target.name and current != old else ""
        self.lines.append(f"move {old} to {target.key}{named_as}: "
                          f"{'; '.join(summary(item) for item in evidence)}"
                          f"{self._renames(count)}")

    def _release(self, meaning, symbol):
        """(generated name, former references, keys) of a symbol that leaves
        its meaning: its entry leaves the file of the meaning with its keys
        besides its place, names, evidence, level, and note, or else its row
        leaves `kb/names.csv`."""
        document = self._held(meaning)
        for entry in (document or {}).get("symbol", ()):
            if entry.get("layout") == symbol.layout:
                document["symbol"] = [item for item in document["symbol"] if item is not entry]
                keys = {key: value for key, value in entry.items()
                        if key not in (*ENTRY, "level", "note")}
                return entry.get("name"), list(entry.get("former", ())), keys
        row = self.rows.pop((symbol.layout, symbol.kind, symbol.address), None)
        if row is not None:
            self.rows_changed = True
            return row.name, [f"{name}/{symbol.kind}/{symbol.layout}-{symbol.address:08x}"
                              for name in row.former], {}
        return symbol.generated, [], {}

    def rename(self, op):
        meaning, _ = self.resolve(op["meaning"])
        name, kind = op["name"], meaning.kind
        if meaning.semantic and meaning.name == name:
            raise KbError(f"{meaning.key} has the name {name}", code=2)
        stated = [src for src in meaning.name_sources
                  if not src.startswith(f"{store.TREE.as_posix()}/")]
        if stated:
            raise KbError(f"{', '.join(stated)} names {meaning.key}; a registry owns its facts "
                          "until its conversion", code=3)
        self._semantic(name, kind, meaning)
        held = sorted(src for owner, src in self.model.files.values() if owner is meaning)
        if len(held) > 1:
            raise KbError(f"{meaning.key} has {len(held)} files, {', '.join(held)}; `kb merge` "
                          "joins them first", code=3)
        old = meaning.key
        path, document = self.document(meaning)
        target = store.path_of(kind, name)
        if target != path:
            self._fresh(target)
        others = {meaning.name, *(symbol.generated for symbol in meaning.symbols.values())}
        for entry in document.get("symbol", ()):
            generated = entry.pop("name", None)
            others.add(generated)
            previous = f"{generated or meaning.name}/{kind}/{entry.get('layout')}-" \
                       f"{entry.get('address')}"
            former = [item for item in _union([previous], entry.get("former", ()))
                      if item.partition("/")[0] != name]
            entry.pop("former", None)
            if former:
                entry["former"] = former
        former = _union(document.pop("former", []), [meaning.name] if meaning.semantic else [])
        former = [item for item in former if item != name]
        if former:
            document["former"] = former
        if target != path:
            self._remove(path)
            self.documents[target] = document
        self.renamed[old] = f"{name}/{kind}"
        count = self._rename(others - {None, name}, kind, name, target)
        self.lines.append(f"rename {old} to {name}/{kind}{self._renames(count)}")

    def _move_address(self, meaning, named, op):
        layout, address = self._location(op["to"])
        if layout != named.layout:
            raise KbError(f"{self._ref(named)} lies on {named.layout}, not on {layout}; a symbol "
                          "moves within its layout", code=2)
        if address == named.address:
            raise KbError(f"{self._ref(named)} lies at {op['to']}", code=2)
        key = SymbolKey(layout, meaning.kind, address)
        held = self._pending_symbol(key)
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
        count = self._relocate({old: new})
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

    def _relocate(self, moves):
        """Rewrite the references of the entity files to a reference of
        `moves` {old: new} as references to its new one; returns their count."""
        paths = {path for _, _, path in store.files(self.root, self.model.overlay)}
        total = 0
        for path in sorted((paths | set(self.documents)) - self.removed,
                           key=lambda item: item.as_posix()):
            document = self.documents.get(path)
            if document is None:
                document = store.load(self.root, path, self.model.overlay)
            document, count = relocated(document, moves)
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
        if self.review_text is not None and self._current(repo.OWNER_CONFIG) != self.review_text:
            found[repo.OWNER_CONFIG] = self.review_text
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
        self._gate(meaning)
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

    def _held(self, meaning):
        """The document of the file of a meaning, or None when neither the
        change nor the working tree holds one."""
        path = self._path(meaning) or store.path_of(meaning.kind, meaning.name)
        if path in self.documents or self._current(path) is not None:
            return self.document(meaning)[1]
        return None

    def _fresh(self, path):
        """Refuse the path of a new file that the store or the change holds."""
        if path in self.removed:
            raise KbError(f"{path.as_posix()} leaves the store in this change", code=3)
        if path in self.documents or self._current(path) is not None:
            raise KbError(f"{path.as_posix()} exists", code=3)

    def _gate(self, meaning):
        """Refuse a meaning that an earlier operation of the change renames."""
        new = self.renamed.get(meaning.key)
        if new is not None:
            raise KbError(f"{meaning.key} takes the name {new} earlier in this change; a batch "
                          "renames a meaning after its other operations", code=3)

    def _path(self, meaning):
        """The file of a meaning: the file of its name, or else its only file."""
        if self.new_meanings.get(meaning.key) is meaning:
            return store.path_of(meaning.kind, meaning.name)
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

    def retire(self, op):
        """Mark an unused owned entity inactive while preserving its document."""
        from kb import retirement
        text = str(op['ref']).strip()
        held = next((record for record in retirement.records(self.model)
                     if text == f'{record[1]}/{record[0]}'), None)
        if held is not None:
            self.lines.append(f'retire {text}: inactive; names remain reserved')
            return
        reference = MEANING_REF.fullmatch(text)
        entity_key = (reference['kind'], reference['name']) if reference else None
        if entity_key in self.model.entities:
            subject = self.model.entities[entity_key]
            path, document = self.designed(*entity_key)
        else:
            subject, symbol = self.resolve(text)
            if symbol is not None:
                raise KbError('retire takes a whole meaning, not one layout symbol', code=2)
            path, document = self.document(subject)
        withdrawn = (retirement.ledger_withdrawal(self.model, subject, document, op['withdraw_ledger'])
                     if op.get('withdraw_ledger') else ())
        consumers = retirement.consumers(self.model, subject)
        if withdrawn:
            consumers = [item for item in consumers if item != 'a ledger projection selects this meaning']
        if consumers:
            raise KbError(f'{subject.key}: retirement has consumers: ' + '; '.join(consumers), code=3)
        if (document.get('ledger') and not withdrawn
                or any(entry.get('curated') for entry in document.get('symbol', ()))):
            raise KbError(f'{subject.key}: generated selectors prevent retirement', code=3)
        document['retired'] = True
        key = subject.key
        def inactive(result):
            records = retirement.records(result)
            if not any(f'{name}/{kind}' == key for kind, name, _, _ in records):
                return f'{key}: retirement must retain the inactive owner'
            if any(meaning.key == key for meaning in result.meanings) or any(
                    entity.key == key for entity in result.entities.values()):
                return f'{key}: a retained source reconstructs the retired entity'
        self.expected.append(inactive)
        self.lines.append(f'retire {subject.key}: inactive; names remain reserved')
        if withdrawn:
            self.lines.append('withdraw active ledger selectors: ' + ', '.join(withdrawn)
                              + '; their records remain in the inactive owner')

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
        symbol = self._symbols(meaning).get(layout)
        if symbol is not None:
            raise KbError(f"{meaning.key} has {self._ref(symbol)} on {layout}; `kb move` "
                          "corrects a wrong symbol", code=3)

    def _source(self, meaning, named, layout):
        """The symbol that a search starts from: that of `from`, the symbol
        that the reference names, or the home symbol."""
        if layout is not None:
            symbol = self._symbols(meaning).get(self._layout(layout))
            if symbol is None:
                raise KbError(f"{meaning.key} has no symbol on {layout}", code=5)
            return symbol
        symbol = named or meaning.home_symbol
        if symbol is None:
            raise KbError(f"{meaning.key} has no symbol to search from", code=5)
        return symbol

    @staticmethod
    def _grammar(text):
        """Whether a text is a semantic name or a slug (section 5.1)."""
        return bool(vocab.SEMANTIC_NAME.fullmatch(text)) and 3 <= len(text) <= 48

    def _semantic(self, name, kind, own=None):
        """Refuse a semantic name of `kind` against its grammar, or one that
        another meaning holds: as its name, one of its other names, or the
        former name of one of its symbols (section 5.3)."""
        if not isinstance(name, str) or not self._grammar(name):
            raise KbError(f"{name!r} is no semantic name: 3 to 48 characters of "
                          "[a-z][a-z0-9]*(_[a-z0-9]+)*", code=2)
        for meaning in self.model.meanings:
            if meaning is own or meaning.kind != kind:
                continue
            if meaning.semantic and meaning.name == name:
                raise KbError(f"{name}/{kind} exists", code=3)
            for other, tier, src in meaning.other_names:
                if other == name:
                    raise KbError(f"{name} is a {tier} name of {meaning.key} in {src}", code=3)
        for key, (_, former, src) in sorted(self.model.file_names.items()):
            if key.kind == kind and name in former and self.model.meaning_of(key) is not own:
                raise KbError(f"{name} is a former name of {self._ref(self.model.symbols[key])} "
                              f"in {src}", code=3)

    @staticmethod
    def _names(meaning, symbols=None):
        """The names that references of files give a meaning: its name, the
        generated names of its symbols, and its other names."""
        symbols = meaning.symbols if symbols is None else symbols
        return {meaning.name, *(symbol.generated for symbol in symbols.values()),
                *(name for name, _, _ in meaning.other_names)} - {None}

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

    def _draw(self, key):
        if self._taken is None:
            self._taken = names.Taken(names.reserved(self.model, self.model.names))
            self._domain = names.domain_dictionary(self.model, self.root)
        attempts = self.model.config.get("names", {}).get("attempts", 1000)
        return names.draw(self._taken, self._domain, attempts, random.Random(key.key))


def _selection_row(model, key, registry, order):
    """The unique owned row of an existing compatible symbol."""
    meaning = next((entry for entry in model.meanings if entry.key == key), None)
    symbol = meaning and meaning.symbols.get("7mfk")
    if symbol is None or symbol.kind not in ledger_projection.REGISTRY_KINDS[registry]:
        raise KbError(f"{key}: ledger selection has no compatible 7mfk symbol", code=3)
    rows = []
    for kind, name, markers, src in model.stash.get("ledger_rows", ()):
        owner = model.files[kind, name][0]
        rows.extend((Path(src), marker, owner) for marker in markers
                    if marker.get("registry") == registry and marker.get("order") == order)
    if (len(rows) != 1 or rows[0][2] is not meaning
            or isinstance(rows[0][1]["order"], bool)
            or not isinstance(rows[0][1]["order"], int)):
        raise KbError(f"{key}: no unique owned ledger row {registry}/{order}", code=3)
    path, marker, _ = rows[0]
    return meaning, symbol, path, marker


def _selection(model, key, registry, order, item):
    """The unique owned row and native relation that a selector can select.

    Each candidate uses the ledger projector's direction and claim validator
    in isolation; merged registry claims cannot supply a native claim.
    """
    meaning, symbol, path, marker = _selection_row(model, key, registry, order)
    column = next((column for column, supports in tokens.SUPPORTS.items()
                   if supports == item["supports"]), None)
    if registry == "diagnostic-bindings" or column not in ledger_projection.HEADERS[registry].split(","):
        raise KbError(f"{key}: {registry} does not project a {item['supports']} dependency claim",
                      code=3)
    ledger_projection.dependency(model, symbol, item)
    target = next(entry for entry in model.meanings if entry.key == item["to"])
    owner, other = ((meaning, target) if item["end"] == "owner" else (target, meaning))
    isolated = copy.copy(model)
    isolated.self_links = []

    def matches(link):
        isolated.links = [link]
        try:
            ledger_projection.dependency(isolated, symbol, item)
            return True
        except KbError:
            return False

    candidates = [link for link in model.links
                  if link.owner is owner and link.to is other and link.type == item["type"]
                  and link.offset == (item.get("offset", 0) if item["type"] == "base"
                                      else item.get("offset"))
                  and matches(link)]
    if len(candidates) != 1:
        raise KbError(f"{key}: ledger dependency needs one relation, found {len(candidates)}",
                      code=3)
    [relation] = candidates
    native = []
    for subject, src in model.files.values():
        if subject is not owner:
            continue
        document = store.load(model.root, src, model.overlay)
        for entry in document.get("link", ()):
            found = REFERENCE.fullmatch(str(entry.get("to")))
            if (entry.get("type") == relation.type and found is not None
                    and found.group("kind") == other.kind
                    and found.group("name") in Change._names(other)
                    and entry.get("slot") == relation.slot
                    and (entry.get("offset", 0) if relation.type == "base"
                         else entry.get("offset")) == relation.offset):
                native.append(entry)
    if len(native) != 1:
        raise KbError(f"{key}: ledger dependency needs one native relation, found {len(native)}",
                      code=3)
    [entry] = native
    if "offset" in entry and (isinstance(entry["offset"], bool)
                              or not isinstance(entry["offset"], int)
                              or entry["offset"] < 0):
        raise KbError(f"{key}: native relation has an invalid offset", code=3)
    owned = copy.copy(relation)
    owned.props = {name: value for name, value in entry.items()
                   if name not in ("type", "to", "evidence", "role", "slot", "offset")}
    owned.roles = {entry["role"]} if "role" in entry else set()
    stated = {evidence["at"].split(":", 1)[0] for evidence in entry.get("evidence", ())
              if isinstance(evidence.get("at"), str) and ":" in evidence["at"]}
    owned.stated = stated or set(entry.get("layouts") or (owner.home,))
    if not matches(owned):
        raise KbError(f"{key}: native relation does not hold the selected claim", code=3)
    return path, marker


@allocation_phase
def _issues(model):
    """Current model checks and retained review issues without proof plugins."""
    found = {}
    for check in checks.CHECKS.values():
        for issue in check(model):
            found.setdefault((issue.check, issue.subject, issue.message), issue)
    for section, issues in checks.audit(model, ("disagreements", "chain-notes")).items():
        for issue in issues:
            found.setdefault((section, issue.subject, issue.message), issue)
    return found


def refusals(base, result):
    """The issues of the model checks and the registry disagreements of
    `result` that `base` lacks."""
    before, after = _issues(base), _issues(result)
    return [issue for key, issue in sorted(after.items()) if key not in before]


def plan(ops, base, resolve, root=repo.ROOT):
    """Plan supported native operations and refuse new issues before writing."""
    if (any(isinstance(op, dict) and op.get('cmd') == 'rebase-reviews' for op in ops)
            and not all(isinstance(op, dict) and op.get('cmd') == 'rebase-reviews' for op in ops)):
        raise KbError('run review rebasing separately from native fact edits', code=2)
    change = Change(base, resolve, root)
    for number, op in enumerate(ops, 1):
        change.run(op, number if len(ops) > 1 else None)
    texts = change.texts()
    result = compile.build(root, {**base.overlay, **texts})
    from kb import reconciliation
    owner_text = (reconciliation.rebase(base, result, change.renamed)
                  if change.renamed or any(op["cmd"] == "unlink" or
                     (op["cmd"] == "set-link" and "evidence" in (op.get("keys") or {}))
                     for op in ops) else None)
    if owner_text is not None:
        texts[repo.OWNER_CONFIG] = owner_text
        result = compile.build(root, {**base.overlay, **texts})
    refused = refusals(base, result)
    unmet = [message for expected in change.expected for message in [expected(result)]
             if message]
    from kb import research, retirement
    unmet += research.preservation(base, result)
    unmet += retirement.preserved(base, result)
    if refused or unmet:
        parts = [f"adds {len(refused)} issues"] if refused else []
        parts += [f"contradicts {len(unmet)} of its operations"] if unmet else []
        lines = [f"the change {' and '.join(parts)}; nothing is written"]
        lines += [f"  {issue.check}: {issue.path}: {issue.subject}: {issue.message}"
                  for issue in refused]
        lines += [f"  {message}" for message in unmet]
        raise KbError("\n".join(lines), code=3)
    return change, texts, result


def apply(ops, root=repo.ROOT, dry_run=False, log=print):
    """Validate and apply a native batch under the lock; a dry run writes nothing."""
    with lock.held(root):
        review_only = bool(ops) and all(
            isinstance(op, dict) and op.get('cmd') == 'rebase-reviews' for op in ops)
        withdrawal_only = bool(ops) and all(
            isinstance(op, dict) and op.get('cmd') == 'retire' and op.get('withdraw_ledger') for op in ops)
        source_only = review_only or withdrawal_only
        if source_only:
            from kb import fingerprint, l0

            before = fingerprint.compute(root)
            base = compile.build(root)
            change, texts, result = plan(ops, base, model_resolver(base), root)
            if review_only:
                layouts = {op['layout'] for op in ops}
            else:
                from kb import retirement

                owned = {meaning.key: set(meaning.symbols) for meaning in base.meanings}
                owned.update({f'{name}/{kind}': {item['layout'] for item in document.get('symbol', ())}
                              for kind, name, document, _ in retirement.records(base)})
                layouts = set().union(*(owned[str(op['ref']).strip()] for op in ops))
            failures = l0.check_all(root, only=sorted(layouts))
            if failures:
                raise KbError('source-only write requires valid L0:\n'
                              + '\n'.join(map(str, failures)), code=3)
            if fingerprint.compute(root) != before:
                raise KbError('the sources change during source-only planning; nothing is written', code=6)
        else:
            with graph.fresh(root, log=log, held=True) as session:
                base = compile.build(root)
                change, texts, result = plan(ops, base, graph_resolver(session, base, root, log), root)
        if not dry_run and texts:
            store.write(root, texts)
            compile.cached.cache_clear()
            graph.sync_held(root, False, log, result)
    return change, texts
