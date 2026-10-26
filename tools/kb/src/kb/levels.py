"""The levels of claims (tools/kb/SPEC.md, sections 7.1 and 13).

A claim is the identity, the scale, or the contract of a meaning; the
identity or the scale of a symbol that states its own level; the identity of
a symbol that the files own on another layout than the home of its meaning;
a named bit or value; or a diagnostic binding. The effective level of a
claim is its declared level bounded by its `relies` dependencies, resolved to
the greatest fixed point, so a cycle takes the minimum of its members. Its
grounding is the highest level that its evidence grounds, and a dependency
grounds it up to `code`, resolved to the least fixed point. `check` reports
the claims above their effective level or their grounding, every `hardware`
key without a passing record, and every `arithmetic` equation that does not
hold.
"""

from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
import re
import tomllib

from kb import checks, match, sites, vocab
from kb.model import Issue, SymbolKey

HARDWARE = Path("patches/hardware-results.toml")
PATTERN, CANDIDATE, CODE, SILICON = (vocab.LEVEL_RANK[level] for level in vocab.LEVELS)
# The level key of each claim of a meaning or a symbol.
KEYS = {"identity": "level", "scale": "scale_level", "contract": "contract_level"}
# The claim of the `to` end that a `relies` value names; `structure` names
# the code object itself.
RELIED = {"level": "identity", "scale": "scale", "contract": "contract"}
NUMBER = re.compile(r"\d+(?:\.\d*)?|\.\d+")
OPERATORS = frozenset("+-*/^()")


@dataclass(eq=False)
class Claim:
    """A claim at its declared level: its evidence items, each with the
    symbol whose evidence decides its rank, its dependencies, and for the
    identity of a symbol the symbol that `match.grounded` grounds."""

    path: str
    subject: str
    name: str
    declared: str
    items: list = field(default_factory=list)
    deps: list = field(default_factory=list)
    symbol: object = None


@dataclass(eq=False)
class Dependency:
    """A `relies` dependency on the claim `claim` of the `to` end, or on the
    structure of the `to` symbol, which the program holds or not; `lacks`
    states why the `to` end has no claim to rest on."""

    relies: str
    via: str
    to: str
    claim: Claim | None = None
    held: bool = False
    lacks: str | None = None
    grounding: bool = True


@dataclass
class Levels:
    """The claims with their effective level and grounding as ranks, the
    dependency that set the effective level of each claim below its declared
    level, and the issues of `hardware` and `arithmetic` evidence items."""

    claims: list
    effective: dict
    grounded: dict
    causes: dict
    failures: list

    def level(self, claim):
        """The confidence supported by dependencies and current evidence.

        A retained assertion without grounding remains a candidate, bounded
        by any lower declared level or unresolved structural dependency.
        """
        return vocab.LEVELS[min(self.effective[id(claim)],
                                max(CANDIDATE, self.grounded[id(claim)]))]


# Arithmetic.

def evaluate(text):
    """The exact value of an expression of numbers, `+`, `-`, `*`, `/`, `^`
    with an integer exponent, and parentheses."""
    tokens, position = [], 0
    text = str(text)
    while position < len(text):
        number = NUMBER.match(text, position)
        if number:
            tokens.append(number.group())
            position = number.end()
            continue
        char = text[position]
        if not char.isspace():
            if char not in OPERATORS:
                raise ValueError(f"character {char!r}")
            tokens.append(char)
        position += 1
    tokens.append(None)
    at = 0

    def peek():
        return tokens[at]

    def take():
        nonlocal at
        at += 1
        return tokens[at - 1]

    def sum_():
        value = product()
        while peek() in ("+", "-"):
            value = value + product() if take() == "+" else value - product()
        return value

    def product():
        value = sign()
        while peek() in ("*", "/"):
            if take() == "*":
                value *= sign()
            else:
                divisor = sign()
                if divisor == 0:
                    raise ValueError("division by zero")
                value /= divisor
        return value

    def sign():
        if peek() in ("+", "-"):
            return -sign() if take() == "-" else sign()
        return power()

    def power():
        base = atom()
        if peek() != "^":
            return base
        take()
        exponent = sign()
        if exponent.denominator != 1:
            raise ValueError("an exponent that is no integer")
        return base ** int(exponent)

    def atom():
        token = take()
        if token == "(":
            value = sum_()
            if take() != ")":
                raise ValueError("an unclosed parenthesis")
            return value
        if token is not None and token not in OPERATORS:
            return Fraction(token)
        raise ValueError("a missing operand" if token is None else f"unexpected {token!r}")

    value = sum_()
    if peek() is not None:
        raise ValueError(f"unexpected {peek()!r}")
    return value


def equation(value):
    """None when the left side of `<expression>=<number>` rounds to the
    number at the decimal places that the number states, else why not."""
    left, sep, right = str(value).rpartition("=")
    right = right.strip()
    if not sep or not re.fullmatch(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)", right):
        return "is no equation <expression>=<number>"
    try:
        found = evaluate(left)
    except ValueError as error:
        return f"does not evaluate: {error}"
    places = len(right.partition(".")[2])
    if abs(found - Fraction(right)) * 2 * 10 ** places > 1:
        return f"does not hold: the left side is {float(found):.12g}"
    return None


# Hardware records.

def hardware(root):
    with (root / HARDWARE).open("rb") as source:
        return tomllib.load(source)


def record(records, key):
    """The record of `patches/hardware-results.toml` at a dotted key, or None."""
    node = records
    for part in str(key or "").split("."):
        if not isinstance(node, dict) or part not in node:
            return None
        node = node[part]
    return node if isinstance(node, dict) else None


def item_failure(item, records):
    """None when a `hardware` item names a passing record of `records` and an
    `arithmetic` item holds, else why not; other kinds hold here."""
    try:
        if match.archived(item):
            return None
    except ValueError as error:
        return str(error)
    kind = item.get("kind")
    if kind == "hardware":
        found = record(records, item.get("key"))
        if found is None:
            return f"hardware evidence names {item.get('key')}, which is no record of {HARDWARE}"
        if found.get("hardware_status") != "pass":
            return (f"hardware evidence names {item.get('key')}, whose hardware_status is "
                    f"{found.get('hardware_status')!r}, not 'pass'")
    elif kind == "arithmetic":
        failure = equation(item.get("value"))
        if failure:
            return f"arithmetic evidence {item.get('value')} {failure}"
    return None


# The program.

def entries(model):
    """The keys of the symbols that a DID table entry of the images names:
    the `source` ends of the `did` symbols whose typed `did-table` evidence
    holds their address, which the image-bytes check verifies."""
    found = set()
    for meaning in model.meanings:
        if meaning.kind != "did":
            continue
        for link in meaning.links:
            if link.owner is not meaning or link.type != "source":
                continue
            for layout in checks._claimed(link):
                symbol, to = meaning.symbols[layout], link.to.symbols[layout]
                typed = [item for item in symbol.evidence
                         if item.get("kind") == "did-table" and "legacy" not in item]
                if typed and not any(checks._did_sources("", symbol, to, link.offset)):
                    found.add(to.key)
    return found


def held(model, symbol, pointed=frozenset()):
    """Whether the program holds a symbol as a code object: a function entry
    of L0 for a `fn` symbol; for another symbol, an L0 reference to an
    address of its storage, a verified `base` reference, or a DID
    table entry of the images, which `pointed` (`entries`) names."""
    if symbol is None:
        return False
    if symbol.kind == "fn":
        return symbol.address in model.functions.get(symbol.layout, ())
    if symbol.key in pointed:
        return True
    if any(item.get("kind") == "indirect" and "legacy" not in item
           and item.get("mode") == "base" and not match.passive(item)
           and match.verify(model, symbol, item) is None
           for item in symbol.evidence):
        return True
    referenced = sites.referenced(symbol.layout, model.root)
    span = match.storage_size(symbol) or 1
    return any(address in referenced for address in range(symbol.address, symbol.address + span))


# Claims.

def _supports(value):
    if value is None:
        return ["identity"]
    return list(value) if isinstance(value, (list, tuple)) else [value]


class _Collector:
    def __init__(self, model):
        self.model = model
        self.owned = {key for key, symbol in model.symbols.items()
                      if checks._owned(model, symbol)}
        self.pointed = entries(model)
        self.claims, self.meanings, self.symbols = [], {}, {}

    def add(self, claim, index=None, key=None):
        self.claims.append(claim)
        if index is not None:
            index[key] = claim
        return claim

    def target(self, relies, meaning, symbol):
        """(claim, lacks) of the claim that a `relies` value names on a `to`
        end: its symbol's own claim, or else its meaning's."""
        if relies == "structure" or meaning is None:
            return None, None
        name = RELIED[relies]
        claim = self.symbols.get((symbol.key, name)) if symbol is not None else None
        claim = claim or self.meanings.get((id(meaning), name))
        return claim, None if claim else f"which declares no {KEYS[name]}"

    def depend(self, claim, relies, via, meaning, symbol, to, *, grounding=True):
        found, lacks = self.target(relies, meaning, symbol)
        claim.deps.append(Dependency(
            relies, via, to, found,
            relies == "structure" and held(self.model, symbol, self.pointed), lacks,
            grounding=grounding))

    def trace(self, claim, item):
        """The dependency of a `trace` item, whose `to` names a symbol."""
        to = item.get("to")
        symbol = self.model.symbols.get(to) if isinstance(to, SymbolKey) else None
        shown = to.key if isinstance(to, SymbolKey) else str(to)
        if symbol is None:
            claim.deps.append(Dependency(item.get("relies"), "trace evidence", shown,
                                         lacks="which no registry holds"))
            return
        self.depend(claim, item.get("relies"), "trace evidence", symbol.meaning, symbol, shown)

    def evidence(self, claim, symbol, items):
        for item in items or ():
            if (item.get("kind") == "trace" and item.get("relies") in vocab.RELIES
                    and not match.passive(item)):
                self.trace(claim, item)
            else:
                claim.items.append((symbol, item))

    def collect(self):
        model = self.model
        for meaning in model.meanings:
            path, subject = checks._sources(meaning), checks._subject(meaning)
            for name, key in KEYS.items():
                if meaning.props.get(key) in vocab.LEVEL_RANK:
                    self.add(Claim(path, subject, name, meaning.props[key]), self.meanings,
                             (id(meaning), name))
            for layout, symbol in sorted(meaning.symbols.items()):
                self._symbol_claims(meaning, layout, symbol)
        for meaning in model.meanings:
            self._meaning_evidence(meaning)
        for link in model.links:
            self._link(link)
        return self.claims

    def _symbol_claims(self, meaning, layout, symbol):
        path = ";".join(sorted(symbol.sources)) or "model"
        for name in ("identity", "scale"):
            level = symbol.props.get(KEYS[name])
            if level not in vocab.LEVEL_RANK:
                if (name != "identity" or symbol.key not in self.owned
                        or layout == meaning.home):
                    continue
                level = meaning.props.get("level")
                if level not in vocab.LEVEL_RANK:
                    continue
            self.add(Claim(path, symbol.key.key, name, level,
                           symbol=symbol if name == "identity" else None),
                     self.symbols, (symbol.key, name))

    def _meaning_evidence(self, meaning):
        path, subject = checks._sources(meaning), checks._subject(meaning)
        for _, symbol in sorted(meaning.symbols.items()):
            for item in symbol.evidence:
                supports = item.get("supports", "identity")
                name = "identity" if supports == "homology" else supports
                if name not in KEYS:
                    continue
                own = self.symbols.get((symbol.key, name))
                found = [own] if own else []
                if supports != "homology" and not (name == "scale" and own):
                    found.append(self.meanings.get((id(meaning), name)))
                for claim in found:
                    if claim is not None:
                        self.evidence(claim, symbol, [item])
        owners = [(subject, meaning.props, meaning.home_symbol)]
        owners += [(symbol.key.key, symbol.props, symbol)
                   for _, symbol in sorted(meaning.symbols.items())]
        for owner, props, symbol in owners:
            for table in ("bit", "value"):
                listed = props.get(table)
                for entry in listed if isinstance(listed, list) else ():
                    if not isinstance(entry, dict) or entry.get("level") not in vocab.LEVEL_RANK:
                        continue
                    claim = self.add(Claim(path, f"{owner} {table} {entry.get('name')}", table,
                                           entry["level"]))
                    self.evidence(claim, symbol, entry.get("evidence"))
        for binding in meaning.tables.get("diagnostic", ()):
            if binding.get("level") in vocab.LEVEL_RANK:
                claim = self.add(Claim(path, f"{subject} diagnostic {binding.get('id')}",
                                       "diagnostic", binding["level"]))
                self.evidence(claim, meaning.home_symbol, binding.get("evidence"))

    def _link(self, link):
        passive = any(match.passive(item) or item.get("kind") == "test" for item in link.evidence)
        ends = (("relies", "supports", link.owner, link.to, link.type),
                ("reverse_relies", "reverse_supports", link.to, link.owner,
                 f"{link.type} link of {checks._subject(link.owner)}"))
        for relies_key, supports_key, owner, to, via in ends:
            relies = link.props.get(relies_key)
            if relies not in vocab.RELIES:
                continue
            symbol = to.symbols.get(owner.home) or to.home_symbol
            shown = symbol.key.key if symbol is not None else checks._subject(to)
            for name in _supports(link.props.get(supports_key)):
                claim = self.meanings.get((id(owner), name))
                if claim is not None:
                    self.depend(claim, relies, via if relies_key == "reverse_relies"
                                else f"{via} link", to, symbol, shown, grounding=not passive)
                    if passive and relies_key == "relies":
                        # Retained optional evidence cannot borrow the function's
                        # existence as proof of an access. Independent items on
                        # the same link still support their declared claim.
                        for item in link.evidence:
                            if item.get("supports", "identity") != name:
                                continue
                            at = match.location(item.get("at"))
                            own = owner.symbols.get(at[0]) if at else owner.home_symbol
                            self.evidence(claim, own, [item])


def _bound(dep, effective):
    if dep.claim is not None:
        return effective[id(dep.claim)]
    return SILICON if dep.held else PATTERN


def _claim_scope(claims, subjects):
    """Selected claims and every donor, in the collector's original order."""
    known = {id(claim) for claim in claims}
    pending = [claim for claim in claims if claim.subject in subjects]
    selected = {id(claim) for claim in pending}
    while pending:
        for dependency in pending.pop().deps:
            donor = dependency.claim
            if donor is not None and id(donor) in known and id(donor) not in selected:
                selected.add(id(donor))
                pending.append(donor)
    return [claim for claim in claims if id(claim) in selected]


def analyze(model, *, subjects=None):
    """The `Levels` of all claims, or selected subjects and their donors.

    Collection, DID structure and hardware/arithmetic failures use the full
    model. Selection limits claim evaluation, keeping original dependency
    order, causes and external homology grounding. Failures remain complete.
    """
    claims = _Collector(model).collect()
    records = hardware(model.root)
    failed, failures = set(), []
    for path, subject, item in _all_items(model):
        failure = item_failure(item, records)
        if failure:
            failed.add(id(item))
            failures.append(Issue("levels", path, subject, failure))
    if subjects is not None:
        claims = _claim_scope(claims, frozenset(subjects))
    effective = {id(claim): vocab.LEVEL_RANK[claim.declared] for claim in claims}
    # The dependency of the last decrease of each claim. A claim decreases
    # only to the level that the claim of its cause holds already, so the
    # causes lead from a claim to a dependency without a claim or to a claim
    # that keeps its declared level.
    causes = {}
    changed = True
    while changed:
        changed = False
        for claim in claims:
            for dep in claim.deps:
                value = _bound(dep, effective)
                if value < effective[id(claim)]:
                    effective[id(claim)] = value
                    causes[id(claim)] = dep
                    changed = True
    ranks = match.grounded(model, sorted({claim.symbol.key for claim in claims
                                          if claim.symbol is not None}))
    grounded = {}
    for claim in claims:
        best = ranks[claim.symbol.key][0] if claim.symbol is not None else -1
        for symbol, item in claim.items:
            if id(item) in failed or item.get("supports") == "homology":
                continue
            best = max(best, match.rank(item, symbol, model, claim))
        grounded[id(claim)] = best
    changed = True
    while changed:
        changed = False
        for claim in claims:
            for dep in claim.deps:
                if not dep.grounding:
                    continue
                if dep.claim is not None:
                    value = min(CODE, grounded[id(dep.claim)])
                else:
                    value = CODE if dep.held else -1
                if value > grounded[id(claim)]:
                    grounded[id(claim)] = value
                    changed = True
    return Levels(claims, effective, grounded, causes, failures)


def _all_items(model):
    """(path, subject, item) of every evidence item of the model."""
    for meaning in model.meanings:
        path, subject = checks._sources(meaning), checks._subject(meaning)
        for _, symbol in sorted(meaning.symbols.items()):
            for item in symbol.evidence:
                yield path, symbol.key.key, item
        owners = [(subject, meaning.props)]
        owners += [(symbol.key.key, symbol.props) for _, symbol in sorted(meaning.symbols.items())]
        for owner, props in owners:
            for table in ("bit", "value"):
                listed = props.get(table)
                for entry in listed if isinstance(listed, list) else ():
                    for item in entry.get("evidence", ()) if isinstance(entry, dict) else ():
                        yield path, f"{owner} {table} {entry.get('name')}", item
        for binding in meaning.tables.get("diagnostic", ()):
            for item in binding.get("evidence", ()):
                yield path, f"{subject} diagnostic {binding.get('id')}", item
        for link in meaning.links:
            if link.owner is meaning:
                for item in link.evidence:
                    yield path, f"{subject} {link.type} link", item
        for layout, status in sorted(meaning.statuses.items()):
            for item in status.evidence:
                yield path, f"{subject} on {layout}", item


# The report.

def _end(dep):
    if dep.lacks:
        return f"the {dep.relies} of {dep.to}, {dep.lacks} ({dep.via})"
    return f"the structure of {dep.to}, which neither L0 nor a DID table references ({dep.via})"


def _explain(claim, found):
    """Why a claim stays below its declared level: the dependency that
    bounds it and the end of the chain of causes from it, a claim that keeps
    its declared level or a dependency without a claim."""
    first = dep = found.causes[id(claim)]
    head = f"it rests on the {first.relies} of {first.to} ({first.via})"
    while dep.claim is not None:
        target = dep.claim
        if id(target) not in found.causes:
            if dep is first:
                return f"{head}, declared {target.declared}"
            return f"{head}; the chain ends at {target.subject}, declared {target.declared}"
        dep = found.causes[id(target)]
    if dep is first:
        return f"it rests on {_end(dep)}"
    return f"{head}; the chain ends at {_end(dep)}"


def _grounds(rank):
    return f"grounds {vocab.LEVELS[rank]}" if rank >= 0 else "grounds no level"


def check(model, *, subjects=None):
    """The complete issues, or exactly those of selected Issue subjects.

    Every call prepares fresh claims and failures on the complete model.
    Dependencies retain all donors; no earlier check result is reused.
    """
    subjects = None if subjects is None else frozenset(subjects)
    found = analyze(model) if subjects is None else analyze(model, subjects=subjects)
    issues = list(found.failures)
    for claim in found.claims:
        declared = vocab.LEVEL_RANK[claim.declared]
        effective = found.effective[id(claim)]
        what = f"the {claim.name} level {claim.declared}"
        if effective < declared:
            issues.append(Issue("levels", claim.path, claim.subject,
                                f"{what} exceeds its effective level {vocab.LEVELS[effective]}: "
                                f"{_explain(claim, found)}"))
        if declared == CANDIDATE and not (claim.items or claim.deps):
            issues.append(Issue("levels", claim.path, claim.subject, f"{what} lacks evidence"))
        elif declared >= CODE and found.grounded[id(claim)] < declared:
            issues.append(Issue("levels", claim.path, claim.subject,
                                f"{what} lacks grounding: its evidence "
                                f"{_grounds(found.grounded[id(claim)])}"))
    return sorted(set(issues)) if subjects is None else sorted(
        {issue for issue in issues if issue.subject in subjects})
