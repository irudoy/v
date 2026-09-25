"""The model checks of stage 2 (tools/kb/SPEC.md, section 13).

Each check returns `Issue` records; `kb check` prints one line per issue with
the file, the subject, and the message. Adapters report the issues they find
while reading a registry under the check that owns them.
"""

from collections import Counter, defaultdict

from kb import names, vocab
from kb.model import Issue, SymbolKey

ROM = ("fn", "tbl", "axis", "const", "hook", "did", "dtc")
SPACE = {**{kind: "rom" for kind in ROM}, "ram": "ram", "reg": "io"}
LEVEL_KEYS = ("level", "contract_level", "scale_level")
VOCABULARY = {
    "access": vocab.TBL_ACCESS,
    "storage": vocab.STORAGE,
}


def _sources(meaning):
    return ";".join(sorted(meaning.sources)) or "model"


def _subject(meaning):
    if meaning.name:
        return meaning.key
    symbol = min(meaning.symbols.values(), key=lambda item: item.key, default=None)
    return symbol.key.key if symbol else f"?/{meaning.kind}"


def _evidence_issues(items, path, subject, check_required):
    for item in items:
        kind = item.get("kind")
        if kind not in vocab.EVIDENCE_KINDS:
            yield Issue("schema", path, subject, f"evidence kind {kind!r}")
            continue
        for key, value in item.items():
            if key == "legacy":
                continue
            if key not in vocab.EVIDENCE_KEYS:
                yield Issue("schema", path, subject, f"evidence key {key!r}")
        if item.get("supports") not in (None, *vocab.SUPPORTS):
            yield Issue("schema", path, subject, f"evidence supports {item['supports']!r}")
        if item.get("relies") not in (None, *vocab.RELIES):
            yield Issue("schema", path, subject, f"evidence relies {item['relies']!r}")
        if item.get("mode") not in (None, *vocab.INDIRECT_MODES):
            yield Issue("schema", path, subject, f"evidence mode {item['mode']!r}")
        if check_required and "legacy" not in item:
            required, _ = vocab.EVIDENCE_KINDS[kind]
            absent = [key for key in required if key not in item]
            if absent:
                yield Issue("schema", path, subject, f"{kind} evidence lacks {', '.join(absent)}")


def _key_issues(props, kind, path, subject, quantities):
    """Levels and vocabulary values of the keys of a meaning or of the
    overrides of a symbol."""
    for key in LEVEL_KEYS:
        if props.get(key) not in (None, *vocab.LEVELS):
            yield Issue("schema", path, subject, f"{key} {props[key]!r}")
    for key, allowed in VOCABULARY.items():
        if props.get(key) not in (None, *allowed):
            yield Issue("schema", path, subject, f"{key} {props[key]!r}")
    if kind == "axis" and props.get("quantity") not in (None, *quantities):
        yield Issue("schema", path, subject, f"quantity {props['quantity']!r} outside [vocab] "
                    "quantity of tools/kb/config.toml")


def schema(model):
    issues = [issue for issue in model.issues if issue.check == "schema"]
    quantities = tuple(model.config.get("vocab", {}).get("quantity", ()))
    for meaning in model.meanings:
        path, subject, props = _sources(meaning), _subject(meaning), meaning.props
        issues.extend(_key_issues(props, meaning.kind, path, subject, quantities))
        role = props.get("role")
        roles = {"fn": vocab.FN_ROLES, "tbl": vocab.TBL_ROLES}.get(meaning.kind)
        if role is not None and (roles is None or role not in roles):
            issues.append(Issue("schema", path, subject, f"role {role!r} of a {meaning.kind}"))
        for symbol in meaning.symbols.values():
            issues.extend(_key_issues(symbol.props, meaning.kind, path, symbol.key.key,
                                      quantities))
            issues.extend(_evidence_issues(symbol.evidence, path, symbol.key.key, True))
        for binding in meaning.tables.get("diagnostic", ()):
            if binding.get("level") not in (None, *vocab.LEVELS):
                issues.append(Issue("schema", path, subject,
                                    f"diagnostic {binding['id']} level {binding['level']!r}"))
            issues.extend(_evidence_issues(binding.get("evidence", ()), path,
                                           f"{subject} diagnostic {binding['id']}", True))
        for link in meaning.links:
            if link.type not in vocab.LINK_TYPES:
                issues.append(Issue("schema", path, subject, f"link type {link.type!r}"))
            for key in ("relies", "reverse_relies"):
                if link.props.get(key) not in (None, *vocab.RELIES):
                    issues.append(Issue("schema", path, subject, f"link {key} {link.props[key]!r}"))
            if link.type == "depends" and not link.roles:
                issues.append(Issue("schema", path, subject, "a depends link without role"))
    return issues


def names_check(model):
    issues = []
    semantic = defaultdict(list)
    for meaning in model.meanings:
        if meaning.semantic:
            semantic[(meaning.kind, meaning.name)].append(meaning)
            if not vocab.SEMANTIC_NAME.fullmatch(meaning.name) or not 3 <= len(meaning.name) <= 48:
                issues.append(Issue("names", _sources(meaning), meaning.key,
                                    "a semantic name has 3 to 48 characters of "
                                    "[a-z][a-z0-9]*(_[a-z0-9]+)*"))
    for (kind, name), found in sorted(semantic.items()):
        if len(found) > 1:
            where = "; ".join(sorted(_sources(meaning) for meaning in found))
            issues.append(Issue("names", where, f"{name}/{kind}",
                                f"{len(found)} meanings of kind {kind} share the name"))
    rows = model.names
    by_name = Counter(row.name for row in rows)
    by_key = Counter(row.key for row in rows)
    semantic_names = {name for _, name in semantic}
    for row in rows:
        where = names.PATH.as_posix()
        subject = f"{row.layout}-{row.address:08x}/{row.kind}"
        if not vocab.GENERATED_NAME.fullmatch(row.name):
            issues.append(Issue("names", where, subject, f"generated name {row.name!r}"))
        if by_name[row.name] > 1:
            issues.append(Issue("names", where, subject, f"generated name {row.name} repeats"))
        if by_key[row.key] > 1:
            issues.append(Issue("names", where, subject, "two rows for one symbol"))
        if row.name in semantic_names:
            issues.append(Issue("names", where, subject, f"{row.name} is a semantic name"))
        if row.layout not in model.layouts or row.kind not in vocab.MEANING_KINDS:
            issues.append(Issue("names", where, subject, "unknown layout or kind"))
    lacking = names.missing(model, rows)
    if lacking:
        sample = ", ".join(key.key for key in lacking[:3])
        issues.append(Issue("names", names.PATH.as_posix(), f"{len(lacking)} symbols",
                            f"no generated name, among them {sample}; run `uv run kb sync`"))
    return issues


def references(model):
    issues = [issue for issue in model.issues if issue.check == "references"]
    known = set(model.symbols)
    for meaning in model.meanings:
        for symbol in meaning.symbols.values():
            for item in symbol.evidence:
                target = item.get("to")
                if isinstance(target, SymbolKey) and target not in known:
                    issues.append(Issue("references", _sources(meaning), symbol.key.key,
                                        f"evidence names {target.key}, which no registry holds"))
    return issues


def symbols(model):
    issues = [issue for issue in model.issues if issue.check == "symbols"]
    for key, symbol in sorted(model.symbols.items()):
        path = ";".join(sorted(symbol.sources))
        mcu = model.spaces[model.layouts[key.layout].mcu]
        start, end = mcu[SPACE[key.kind]]
        if not start <= key.address < end:
            issues.append(Issue("symbols", path, key.key,
                                f"the address lies outside the {SPACE[key.kind]} space of "
                                f"{model.layouts[key.layout].mcu}"))
        if key.kind == "fn" and key.address not in model.functions[key.layout]:
            issues.append(Issue("symbols", path, key.key,
                                f"no function entry of l0/{key.layout}/funcs.csv"))
    return issues


def links(model):
    issues = []
    for link in model.links:
        owners, targets = vocab.LINK_TYPES.get(link.type, ((), ()))
        if link.owner.kind not in owners or link.to.kind not in targets:
            issues.append(Issue(
                "links", ";".join(sorted(link.sources)), _subject(link.owner),
                f"{link.type} link from a {link.owner.kind} to {_subject(link.to)}; "
                f"the type joins {'/'.join(owners)} to {'/'.join(targets)}"))
    return issues


CHECKS = {
    "schema": schema,
    "names": names_check,
    "references": references,
    "symbols": symbols,
    "links": links,
}


AUDIT_SECTIONS = ("disagreements", "names", "untyped")


def audit(model):
    """{section: issues}: disagreements of one fact between registries, other
    registry names of a named meaning, and legacy evidence without the keys of
    its kind, which the conversion of its registry types."""
    found = {section: [] for section in AUDIT_SECTIONS}
    found["disagreements"] = sorted(issue for issue in model.issues if issue.check == "audit")
    for meaning in model.meanings:
        path = _sources(meaning)
        others = defaultdict(set)
        for name, tier, src in meaning.other_names:
            others[(name, tier)].add(src)
        for (name, tier), srcs in sorted(others.items()):
            found["names"].append(Issue("audit", ";".join(sorted(srcs)), meaning.key,
                                        f"the {tier} name {name} names the same meaning"))
        for symbol in meaning.symbols.values():
            for item in symbol.evidence:
                required, _ = vocab.EVIDENCE_KINDS.get(item.get("kind"), ((), None))
                absent = [key for key in required if key not in item]
                if absent and "legacy" in item:
                    found["untyped"].append(Issue(
                        "audit", path, symbol.key.key,
                        f"token {item['legacy']} gives {item['kind']} evidence without "
                        f"{', '.join(absent)}"))
    return {section: sorted(issues) for section, issues in found.items()}
