"""Names of symbols and meanings (tools/kb/SPEC.md, section 5).

`kb/names.csv` holds the generated name of every symbol of an unnamed meaning
whose knowledge lives in a legacy registry. A row is a permanent reservation:
when the meaning of its symbol takes a semantic name, the generated name stays
reserved and resolves to the symbol as a former name. A symbol that a meaning
file holds takes its generated name and its former names from the file, and
its row leaves `kb/names.csv` in the conversion of its registry.
"""

import csv
import io
from dataclasses import dataclass
from pathlib import Path
import random
import re

from kb import repo, vocab

PATH = Path("kb/names.csv")
DOMAIN = Path("tools/kb/domain-words.txt")
HEADER = ("layout", "kind", "address", "name", "former")
WORD = re.compile(r"[a-z]+")
HEX_WORD = re.compile(r"[a-f]+")


@dataclass(frozen=True, order=True)
class Row:
    layout: str
    kind: str
    address: int
    name: str
    former: tuple = ()

    @property
    def key(self):
        return (self.layout, self.kind, self.address)


def inputs():
    return [PATH.as_posix(), DOMAIN.as_posix()]


def read(root=repo.ROOT, overlay=None):
    """The rows of `kb/names.csv`, or of its text in `overlay` ({repository
    path: text}) when a change rewrites it."""
    if overlay and PATH in overlay:
        return parse(overlay[PATH])
    path = root / PATH
    if not path.exists():
        return []
    return parse(path.read_text(encoding="utf-8"))


def parse(text):
    reader = csv.DictReader(io.StringIO(text, newline=""))
    if tuple(reader.fieldnames or ()) != HEADER:
        raise repo.KbError(f"{PATH}: header must be {','.join(HEADER)}")
    return [Row(row["layout"], row["kind"], int(row["address"], 16), row["name"],
                tuple(row["former"].split()))
            for row in reader]


def render(rows):
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(HEADER)
    for row in sorted(rows):
        writer.writerow((row.layout, row.kind, f"{row.address:08x}", row.name,
                         " ".join(row.former)))
    return out.getvalue()


def owner_check(model):
    """Remaining names belong to the decoder or an exact permanent reservation."""
    from kb.adapters import dids
    from kb.model import Issue, SymbolKey
    configured = model.config.get('names', {})
    if not configured.get('owners_checked'):
        return []
    reservations, issues = {}, []
    for entry in configured.get('reserved', ()):
        if (not isinstance(entry, dict) or set(entry) != {
                'layout', 'kind', 'address', 'name', 'former', 'reason'}
                or not isinstance(entry.get('reason'), str) or not entry['reason'].strip()):
            issues.append(Issue('names', repo.OWNER_CONFIG.as_posix(), 'reserved',
                                'a permanent reservation needs its full row and a reason'))
            continue
        key = entry['layout'], entry['kind'], entry['address']
        if key in reservations:
            issues.append(Issue('names', repo.OWNER_CONFIG.as_posix(), entry['name'],
                                'duplicate permanent reservation owner'))
        reservations[key] = entry
    consumed = set()
    for row in model.names:
        symbol = model.symbols.get(SymbolKey(*row.key))
        if symbol is not None:
            if symbol.sources <= {dids.DECODER.as_posix()}:
                continue
            issues.append(Issue('names', PATH.as_posix(), row.name,
                                'the remaining name has no declared decoder owner'))
            continue
        key = row.layout, row.kind, f'{row.address:08x}'
        entry = reservations.get(key)
        expected = dict(layout=row.layout, kind=row.kind, address=f'{row.address:08x}',
                        name=row.name, former=list(row.former))
        if entry is None or {name: value for name, value in entry.items()
                             if name != 'reason'} != expected:
            issues.append(Issue('names', PATH.as_posix(), row.name,
                                'the inactive name lacks its exact permanent reservation owner'))
        consumed.add(key)
    for key in reservations.keys() - consumed:
        issues.append(Issue('names', repo.OWNER_CONFIG.as_posix(), reservations[key]['name'],
                            'the inactive reservation is absent or has an active owner'))
    return issues


def write(rows, root=repo.ROOT):
    from kb import store
    store.write(root, {PATH: render(rows)})


def words(text):
    return set(WORD.findall(text.lower()))


def domain_dictionary(model, root=repo.ROOT):
    """Words that a generated name must not contain: the domain word list and
    the words of semantic names, entity slugs, signal titles, and editor
    table names."""
    found = set()
    for line in (root / DOMAIN).read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            found |= words(line)
    for meaning in model.meanings:
        if meaning.semantic:
            found |= words(meaning.name)
    for entity in model.entities.values():
        found |= words(entity.slug)
        if entity.kind == "signal":
            found |= words(entity.props.get("title", ""))
    for meaning in model.meanings:
        for props in (meaning.props, *(symbol.props for symbol in meaning.symbols.values())):
            editor = props.get("editor")
            if isinstance(editor, dict):
                found |= words(editor.get("name", ""))
    return found


class Taken:
    """Current and former names with a nearest-neighbour query under the
    Damerau-Levenshtein distance."""

    def __init__(self, names):
        self.names = set(names)
        self._list = sorted(self.names)

    def add(self, name):
        if name not in self.names:
            self.names.add(name)
            self._list.append(name)

    def near(self, name, distance=2):
        if name in self.names:
            return name
        from rapidfuzz import process
        from rapidfuzz.distance import DamerauLevenshtein
        found = process.extractOne(name, self._list, scorer=DamerauLevenshtein.distance,
                                   score_cutoff=distance)
        return found[0] if found else None


def rejection(candidate, taken, domain):
    """Why a candidate fails the rules of section 5.4, or None."""
    if not vocab.GENERATED_NAME.fullmatch(candidate):
        return "grammar"
    for word in candidate.split("-"):
        if HEX_WORD.fullmatch(word):
            return f"hexadecimal word {word}"
        if word in domain:
            return f"domain word {word}"
    near = taken.near(candidate)
    if near is not None:
        return f"within distance 2 of {near}"
    return None


def draw(taken, domain, attempts, rand=None):
    """A generated name that passes every rule; it joins `taken`."""
    import coolname
    rand = rand or random.SystemRandom()
    coolname.replace_random(rand)
    for _ in range(attempts):
        candidate = coolname.generate_slug(2)
        if rejection(candidate, taken, domain) is None:
            taken.add(candidate)
            return candidate
    raise repo.KbError(f"no generated name passed the rules in {attempts} attempts")


def assign(model, rows):
    """Give every symbol and meaning its name: the semantic name of the meaning,
    or the generated name of the symbol from its file or else from `rows`."""
    by_key = {row.key: row for row in rows}
    for symbol in model.symbols.values():
        named = model.file_names.get(symbol.key)
        if named is not None:
            symbol.generated, symbol.former = named[0], named[1]
            continue
        row = by_key.get((symbol.layout, symbol.kind, symbol.address))
        symbol.generated = row.name if row else None
        symbol.former = row.former if row else ()
    for meaning in model.meanings:
        if not meaning.semantic:
            home = meaning.home_symbol
            meaning.name = home.generated if home else None
        for symbol in meaning.symbols.values():
            symbol.name = meaning.name if meaning.semantic else symbol.generated


def missing(model, rows):
    """Symbols of unnamed meanings that have no generated name."""
    known = {row.key for row in rows}
    known.update((key.layout, key.kind, key.address)
                 for key, (name, _, _) in model.file_names.items() if name)
    return sorted(symbol.key for symbol in model.symbols.values()
                  if symbol.meaning is not None and not symbol.meaning.semantic
                  and (symbol.layout, symbol.kind, symbol.address) not in known)


def enroll(model, rows, root=repo.ROOT, rand=None):
    """Draw generated names for the symbols that lack one; returns the new rows."""
    needed = missing(model, rows)
    if not needed:
        return []
    attempts = repo.config(root).get("names", {}).get("attempts", 1000)
    domain = domain_dictionary(model, root)
    taken = Taken(reserved(model, rows))
    added = [Row(key.layout, key.kind, key.address, draw(taken, domain, attempts, rand))
             for key in needed]
    assign(model, rows + added)
    return added


def reserved(model, rows):
    """Every current and former name of any kind."""
    found = {row.name for row in rows}
    for row in rows:
        found.update(row.former)
    for name, former, _ in model.file_names.values():
        if name:
            found.add(name)
        found.update(former)
    for meaning in model.meanings:
        if meaning.semantic:
            found.add(meaning.name)
            found.update(name for name, _, _ in meaning.other_names)
    for entity in model.entities.values():
        found.add(entity.slug)
    from kb import retirement
    for kind, name, document, _ in retirement.records(model):
        found.update(retirement.aliases(kind, name, document))
    return found
