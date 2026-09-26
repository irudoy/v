"""Write commands (tools/kb/SPEC.md, section 12.3): `bind`, `absent`,
`unresolved`, and `apply`, which applies a batch of them as one change.

A change edits entity files as documents over the working tree. An operation
reads the file of its meaning from the change or from the disk, or starts it
with the entry of the home symbol, which joins the file with the registries
that state the meaning, and the change renders every document in canonical
form. A symbol that a file takes leaves `kb/names.csv`: its generated name
becomes the `name` of its entry in an unnamed meaning, and its other names
become `former` references.

- `bind` adds the symbol of a meaning on a layout without one. Its evidence is
  stated, or it is the evidence of the candidate that `match.search` finds at
  the address from a symbol of the meaning; a `to` that names a symbol becomes
  its location. The status of the layout leaves the file, and an unnamed
  meaning draws a generated name for the symbol and keeps its home.
- `absent` states with evidence that the mechanism does not exist on a layout.
- `unresolved` records the method, the target, and the count of the search
  from a symbol of the meaning, which finds no unique candidate, or of a
  stated search, with the L0 digest of the layout.

`plan` compiles the model with the rendered files in place of those on disk
and refuses the change with exit code 3 when the result has an issue of a
model check or a registry disagreement that the working tree lacks. `apply`
takes the lock, resolves the references on a current graph, plans, writes the
files through temporary files and renames, and loads the graph.
"""

import difflib
from pathlib import Path
import tomllib
import weakref

from kb import checks, compile, graph, lock, match, names, refs, repo, store, vocab
from kb.model import SymbolKey
from kb.repo import KbError

# The keys of each operation of a batch besides `cmd`, and those it requires.
COMMANDS = {
    "bind": ("meaning", "symbol", "evidence", "from", "level", "note"),
    "absent": ("meaning", "layout", "evidence", "note"),
    "unresolved": ("meaning", "layout", "from", "method", "target", "count", "note"),
}
REQUIRED = {"bind": ("meaning", "symbol"), "absent": ("meaning", "layout", "evidence"),
            "unresolved": ("meaning", "layout")}
SEARCH = ("method", "target", "count")
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
            source = self._source(meaning, named, op.get("from"))
            found = match.search(self.model, source, layout)
            candidate = found.candidates.get(address)
            if candidate is None:
                listed = ", ".join(f"{layout}:{other:08x}" for other in sorted(found.candidates))
                raise KbError(
                    f"the {found.method} search from {source.key.location} finds "
                    f"{listed or 'no candidate'} on {layout}, not {key.location}; state the "
                    "evidence", code=3)
            evidence = [self._stored(candidate.evidence)]
        path, document = self._document(meaning)
        name = meaning.name if meaning.semantic else self._draw()
        entry = {"layout": layout, "address": f"{address:08x}"}
        if not meaning.semantic:
            entry["name"] = name
            self._keep_home(meaning, layout, document)
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
        self._status(meaning, {"layout": layout, "state": "unresolved", "method": method,
                               "target": target, "count": count,
                               "l0": match.l0_digest(layout, self.root),
                               "note": op.get("note")})
        self.lines.append(f"unresolved {meaning.key} on {layout}: {method} search of {target}, "
                          f"{count} matches")

    # Documents -------------------------------------------------------------

    def texts(self):
        """{repository path: text} of the files that the change rewrites."""
        found = {}
        for path, document in self.documents.items():
            text = store.render(path.parent.name, document)
            if self._current(path) != text:
                found[path] = text
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
                before.splitlines(keepends=True), text.splitlines(keepends=True),
                f"a/{path.as_posix()}" if before else "/dev/null", f"b/{path.as_posix()}"))
        return "".join(out)

    def _current(self, path):
        """The text of a file in the base of the change: the overlay of its
        model, or else the working tree; None for no file."""
        if path in self.model.overlay:
            return self.model.overlay[path]
        target = self.root / path
        return target.read_text(encoding="utf-8") if target.exists() else None

    def _document(self, meaning):
        """(path, document) of the file of a meaning; a meaning without one
        starts a file with the entry of its home symbol."""
        path = next((Path(src) for owner, src in self.model.files.values()
                     if owner is meaning), None)
        if path is None:
            path = store.path_of(meaning.kind, meaning.name)
            if path not in self.documents and self._current(path) is not None:
                raise KbError(f"{path.as_posix()} holds another meaning than {meaning.key}",
                              code=3)
        if path not in self.documents:
            if self._current(path) is not None:
                self.documents[path] = store.load(self.root, path, self.model.overlay)
            else:
                self.documents[path] = {"symbol": [self._adopt(meaning, meaning.home_symbol)]}
        return path, self.documents[path]

    def _adopt(self, meaning, symbol):
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
        _, document = self._document(meaning)
        kept = [entry for entry in document.get("status", ())
                if entry.get("layout") != status["layout"]]
        document["status"] = kept + [status]

    @staticmethod
    def _keep_home(meaning, layout, document):
        """Pin the home of an unnamed meaning, whose name is the generated name
        of its home symbol, when a symbol on `layout` would move it."""
        if "home" in meaning.props or "home" in document:
            return
        layouts = set(meaning.symbols) | {layout}
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
        for issue in checks.audit(model)["disagreements"]:
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
