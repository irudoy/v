"""Homology matchers over L0 (tools/kb/SPEC.md, sections 7.3, 7.6, and 13).

The code of a layout is the masked instruction word at every instruction
address of its L0 bodies. Masking clears the operand bits that encode an
address that the layouts place differently: the displacements of PC-relative
loads, of `mova`, and of branches, and the displacements of GBR accesses. A
region is a maximal run of equal masked words that aligns an instruction of
one layout with an instruction of another. A region matches when it reaches
`[match] words` of `tools/kb/config.toml` and its words occur once on each
layout; a site aligns when one region matches and no other region of the site
is as long.

Aligned instructions relate the addresses they touch in the same way: the
address of a load, a store, or an update whose base register holds a pool
literal on every path (`kb.derive`), the literal of a PC-relative load, the
target of a call, and an operand of a census call in the same register.

- `verify` decides one evidence item of a symbol on L0 and the images.
- `grounded` computes the level up to which the evidence of symbols grounds
  them, on their own layout or through verified homology evidence.
- `search` lists the candidates for the counterpart of a symbol on another
  layout, with the evidence of each.
- `typed` picks the evidence item that types the homology of a symbol toward
  its counterpart, and `touching` lists the instructions that touch a symbol.
- `writers` is the writer gate.

`code` keeps the matching index of a layout in `.kb/cache/match/`, keyed by
the L0 manifest, the image digest, the census plan, and the sources of this
module and of the derivations.
"""

import bisect
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from functools import lru_cache
import gc
import hashlib
from pathlib import Path
import pickle
import weakref

from kb import derive, l0, repo, sh2, sites, vocab
from kb.model import SymbolKey

DEFAULT_WORDS = 12
GBR_DISPLACEMENT = frozenset({0xC0, 0xC1, 0xC2, 0xC4, 0xC5, 0xC6})
CONDITIONAL = frozenset({0x89, 0x8B, 0x8D, 0x8F})
MOVA = 0xC7
CALL_REFERENCES = ("unconditional_call", "computed_call")
OPERANDS = sites.CENSUS_ADDRESSES[4:]
HASHES = ("exact", "mnemonic", "shape")
STORES = frozenset({"store", "update"})
STORAGE_BYTES = {**sites.STORAGE_BYTES, "float32": 4}
HOMOLOGY_KINDS = frozenset({"masked-match", "literal-pool", "function-match", "call-ordinal",
                            "interp-contract", "did-table", "byte-identical", "l0"})
COUNTED = frozenset({"masked-match", "function-match", "call-ordinal"})
# Interpolation keys that two layouts share under one contract; `kernel` names
# a function of each layout.
CONTRACT_KEYS = ("access", "offset", "cols", "rows", "step", "storage", "x_storage", "y_storage")
CANDIDATE = vocab.LEVEL_RANK["candidate"]
CACHE = repo.STATE / "cache" / "match"
PACKAGE = Path(__file__).resolve().parent
SOURCES = ("match.py", "derive.py", "sh2.py", "sites.py", "l0.py")


def masked(word):
    """The instruction word with its address-encoding displacement cleared."""
    top, high = word >> 12, word >> 8
    if top in (0x9, 0xD) or high in CONDITIONAL or high == MOVA or high in GBR_DISPLACEMENT:
        return word & 0xFF00
    if top in (0xA, 0xB):
        return word & 0xF000
    return word


def words_setting(config):
    return int(config.get("match", {}).get("words", DEFAULT_WORDS))


@dataclass(frozen=True)
class Function:
    entry: int
    size: int
    instructions: int
    hashes: tuple


@dataclass(frozen=True)
class Region:
    """Equal masked words: `start` on the layout of the aligned site, `match`
    on the other layout, the site `offset` words from each start, and the
    occurrences of the words on the layout of the site (`count`) and on the
    other (`matches`)."""

    start: int
    match: int
    words: int
    offset: int
    count: int
    matches: int

    @property
    def unique(self):
        return self.count == 1 and self.matches == 1

    @property
    def site(self):
        return self.match + 2 * self.offset


class Code:
    """The L0 code of one layout for matching: `touch` maps an instruction to
    the (address, relation) pairs it touches, and `touched` the reverse."""

    def __init__(self, layout, data, bodies, functions, calls, pairs, operands, gram):
        self.layout = layout
        self.data = data
        self.gram = gram
        self.bodies = bodies
        self.functions = functions
        self.owner = {}
        for func, addresses in sorted(bodies.items()):
            for address in addresses:
                self.owner.setdefault(address, func)
        self.starts, self.runs = [], []
        self.literals, self.call_sites = {}, set()
        targets = defaultdict(set)
        for site, target in calls:
            targets[site].add(target)
        words, previous = [], None
        for address in sorted(self.owner):
            if previous is None or address != previous + 2:
                self._close(words)
                self.starts.append(address)
                words = []
            word = derive._word(data, address)
            words.append(masked(word))
            previous = address
            insn = sh2.decode(word, address)
            if insn.flow == "call":
                self.call_sites.add(address)
                if insn.target is not None:
                    targets[address].add(insn.target)
            if insn.value and insn.value[0] == "pool":
                literal = self._pool(insn.value[1], insn.value[2])
                if literal is not None:
                    self.literals[address] = literal
        self._close(words)
        self.index = defaultdict(list)
        for number, run in enumerate(self.runs):
            for position in range(len(run) - gram + 1):
                self.index[run[position:position + gram]].append((number, position))
        self.touch = defaultdict(set)
        for pair in pairs:
            self.touch[pair.ins].add((pair.address, pair.mode))
        for site, (_, value) in self.literals.items():
            self.touch[site].add((value, "literal"))
        for site, found in targets.items():
            self.touch[site].update((target, "call") for target in found)
        for site, column, address in operands:
            self.touch[site].add((address, f"operand:{column}"))
        self.touched = defaultdict(set)
        for site, found in self.touch.items():
            for address, relation in found:
                self.touched[address].add((site, relation))
        self.pooled = defaultdict(set)
        for site, (pool, _) in self.literals.items():
            self.pooled[pool].add(site)
        self.hashed = {name: Counter(function.hashes[index] for function in functions.values())
                       for index, name in enumerate(HASHES)}
        self._found = {}

    def __getstate__(self):
        return {**self.__dict__, "_found": {}}

    def _close(self, words):
        if words:
            self.runs.append(tuple(words))

    def _pool(self, pool, size):
        if pool + size > len(self.data):
            return None
        if size == 4:
            return pool, derive._long(self.data, pool)
        return pool, sh2.sext(derive._word(self.data, pool), 16) & sh2.MASK

    @classmethod
    def load(cls, layout_id, root=repo.ROOT, gram=DEFAULT_WORDS):
        layout = repo.layout(layout_id, root)
        base = root / repo.L0 / layout_id
        functions = {}
        for row in derive.read_rows(base / "function_signatures.csv"):
            entry = int(row["addr"], 16)
            functions[entry] = Function(entry, int(row["size"]), int(row["instructions"]),
                                        (row["exact_sha256"], row["mnemonic_sha256"],
                                         row["shape_sha256"]))
        calls = [(int(row["ins_addr"], 16), int(row["ref_addr"], 16))
                 for row in derive.read_rows(base / "function_references.csv")
                 if row["ref_type"] in CALL_REFERENCES]
        operands = []
        for kernel in l0.census(layout_id, root).kernels:
            for row in derive.read_rows(base / l0.Census.file(kernel)):
                site = int(row["callsite"], 16)
                operands.extend((site, column, int(row[column], 16))
                                for column in OPERANDS if row[column])
        return cls(layout_id, derive.image_bytes(layout, root), derive.bodies(layout_id, root),
                   functions, calls, derive.literal_pairs(layout_id, root), operands, gram)

    def raw(self, address):
        return derive._word(self.data, address)

    def place(self, address):
        """(run, position) of an instruction address, or None."""
        number = bisect.bisect_right(self.starts, address) - 1
        if number < 0:
            return None
        position, odd = divmod(address - self.starts[number], 2)
        if odd or position >= len(self.runs[number]):
            return None
        return number, position

    def pattern(self, start, words):
        """The masked words from `start`, or None past the end of its run."""
        place = self.place(start)
        if place is None:
            return None
        number, position = place
        found = self.runs[number][position:position + words]
        return found if len(found) == words else None

    def find(self, pattern):
        """Start addresses of every occurrence of a pattern of at least `gram` words."""
        found = self._found.get(pattern)
        if found is None:
            found = [self.starts[number] + 2 * position
                     for number, position in self.index.get(pattern[:self.gram], ())
                     if self.runs[number][position:position + len(pattern)] == pattern]
            self._found[pattern] = found
        return found

    def touches(self, site):
        return self.touch.get(site, set())

    def sites_of(self, address):
        """{(site, relation)} of every instruction that touches `address`."""
        return self.touched.get(address, set())

    def stores(self, address):
        return sorted(site for site, relation in self.sites_of(address) if relation in STORES)

    def ordinal(self, site):
        """(function, position) of an instruction in the body of its function."""
        func = self.owner.get(site)
        if func is None:
            return None
        body = self.bodies[func]
        return func, bisect.bisect_left(body, site)

    def call_ordinal(self, site):
        """(function, position) of a call among the calls of its function."""
        func = self.owner.get(site)
        if func is None or site not in self.call_sites:
            return None
        calls = [address for address in self.bodies[func] if address in self.call_sites]
        return func, calls.index(site)

    def align(self, site, other):
        """Regions of at least `gram` words that align `site` with an
        instruction of `other`, longest first."""
        place = self.place(site)
        if place is None:
            return []
        number, position = place
        words, gram = self.runs[number], self.gram
        aligned = set()
        for start in range(max(0, position - gram + 1), min(position, len(words) - gram) + 1):
            for other_number, other_position in other.index.get(words[start:start + gram], ()):
                aligned.add((other_number, other_position + position - start))
        regions = []
        for other_number, other_position in aligned:
            theirs = other.runs[other_number]
            left = 0
            while (position - left > 0 and other_position - left > 0
                   and words[position - left - 1] == theirs[other_position - left - 1]):
                left += 1
            right = 0
            while (position + right + 1 < len(words) and other_position + right + 1 < len(theirs)
                   and words[position + right + 1] == theirs[other_position + right + 1]):
                right += 1
            size = left + right + 1
            pattern = words[position - left:position + right + 1]
            regions.append(Region(
                self.starts[number] + 2 * (position - left),
                other.starts[other_number] + 2 * (other_position - left),
                size, left, len(self.find(pattern)), len(other.find(pattern))))
        return sorted(regions, key=lambda region: (-region.words, region.match))

    def aligned(self, site, other):
        """The region that aligns `site` with one instruction of `other`, or None
        when no region matches or another region of the site is as long."""
        regions = self.align(site, other)
        if not regions or not regions[0].unique:
            return None
        if len(regions) > 1 and regions[1].words == regions[0].words:
            return None
        return regions[0]


def _cache_key(layout, root, gram):
    digest = hashlib.sha256(f"{gram}\n".encode())
    digest.update((root / repo.L0 / layout.id / l0.MANIFEST).read_bytes())
    digest.update(repo.images(root)[layout.image].sha256.encode())
    digest.update((root / l0.census(layout.id, root).interp).read_bytes())
    for name in SOURCES:
        digest.update((PACKAGE / name).read_bytes())
    return digest.hexdigest()


def code(layout_id, root=repo.ROOT):
    """The `Code` of a layout, from the cache when its key holds."""
    return _code(layout_id, root)


@lru_cache(maxsize=None)
def _code(layout_id, root):
    layout = repo.layout(layout_id, root)
    gram = words_setting(repo.config(root))
    key = _cache_key(layout, root, gram)
    path = root / CACHE / f"{layout_id}.pickle"
    # The collector would traverse the objects of the model on every pass
    # while the index allocates, which slows a load several times. The index
    # lives as long as the process, so it is frozen afterwards: later passes of
    # the collector, such as those of a compile, skip it.
    collecting = gc.isenabled()
    gc.disable()
    try:
        try:
            with path.open("rb") as source:
                if pickle.load(source) == key:
                    return pickle.load(source)
        except (OSError, EOFError, pickle.UnpicklingError, AttributeError, ValueError):
            pass
        found = Code.load(layout_id, root, gram)
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")
        with temporary.open("wb") as target:
            pickle.dump(key, target, protocol=pickle.HIGHEST_PROTOCOL)
            pickle.dump(found, target, protocol=pickle.HIGHEST_PROTOCOL)
        temporary.replace(path)
        return found
    finally:
        gc.freeze()
        if collecting:
            gc.enable()


def l0_digest(layout_id, root=repo.ROOT):
    """The first 16 hexadecimal digits of the SHA-256 of a layout's L0 manifest."""
    return repo.sha256_file(root / repo.L0 / layout_id / l0.MANIFEST)[:16]


def location(text):
    """(layout, address) of a location `<layout>:<address>`, or None."""
    if not isinstance(text, str) or ":" not in text:
        return None
    layout, _, address = text.partition(":")
    try:
        return layout, int(address, 16)
    except ValueError:
        return None


def _int(value):
    try:
        return int(str(value), 0) if str(value).startswith("0x") else int(str(value))
    except ValueError:
        return None


def storage_size(symbol):
    """Bytes of the storage of a data symbol from its geometry, or None."""
    meaning = symbol.meaning
    props = {**(meaning.props if meaning else {}), **symbol.props}
    width = STORAGE_BYTES.get(props.get("storage"))
    if width is None and props.get("width"):
        width = max(1, int(props["width"]) // 8)
    if width is None:
        return None
    if symbol.kind == "axis":
        return width * int(props["points"]) if props.get("points") else None
    if symbol.kind == "tbl":
        return width * int(props.get("cols") or 1) * int(props.get("rows") or 1)
    if symbol.kind == "const":
        return width * int(props.get("count") or 1)
    return width


@lru_cache(maxsize=None)
def _image(path):
    return path.read_bytes()


def images(model, layout, only=None):
    """[(ROM key, bytes)] of every image of a layout, or of those of `only`."""
    catalog = repo.images(model.root)
    return [(rom, _image(catalog[rom].path)) for rom in model.layouts[layout].images
            if not only or rom in only]


def _images_of(ctx, layout):
    """The images of a layout that the symbol applies to."""
    only = ctx.symbol.props.get("images") if layout == ctx.symbol.layout else None
    return images(ctx.model, layout, only)


# Verification of one evidence item.

@dataclass
class Context:
    """An evidence item of `symbol`: `at` and `to` as (layout, address), and
    `other`, the symbol of the same meaning that `to` names or whose layout
    `to` locates; `named` when `to` is a reference."""

    model: object
    symbol: object
    item: dict
    at: tuple | None = None
    to: tuple | None = None
    other: object = None
    named: bool = False

    @property
    def minimum(self):
        return words_setting(self.model.config)

    def code(self, which):
        return code((self.at if which == "at" else self.to)[0], self.model.root)


def context(model, symbol, item):
    found = Context(model, symbol, item, location(item.get("at")))
    target = item.get("to")
    if isinstance(target, SymbolKey):
        found.named = True
        found.to = (target.layout, target.address)
        found.other = model.symbols.get(target)
    else:
        found.to = location(target)
        if found.to is not None and symbol.meaning is not None:
            found.other = symbol.meaning.symbols.get(found.to[0])
    return found


def verify(model, symbol, item):
    """None when the evidence item holds on L0 and the images, else what
    fails. Kinds that L0 and the images do not decide hold here."""
    check = VERIFIERS.get(item.get("kind"))
    if check is None:
        return None
    found = context(model, symbol, item)
    required, _ = vocab.EVIDENCE_KINDS[item["kind"]]
    absent = [key for key in required if item.get(key) in (None, "")]
    if absent:
        return f"lacks {', '.join(absent)}"
    return check(found)


def verify_status(model, layout, item):
    """None when an evidence item of a status on `layout` holds on L0 and the
    images, else what fails: an `l0` item places an instruction of the L0 of
    the layout at `at`, and a `rom-bytes` item finds `value` at `at` in every
    image of the layout. Other kinds hold here."""
    kind = item.get("kind")
    if kind not in ("l0", "rom-bytes") or "legacy" in item:
        return None
    required, _ = vocab.EVIDENCE_KINDS[kind]
    absent = [key for key in required if item.get(key) in (None, "")]
    if absent:
        return f"lacks {', '.join(absent)}"
    at = location(item["at"])
    if at is None:
        return "`at` is no location"
    if at[0] != layout:
        return f"`at` lies on {at[0]}, not on {layout}"
    if kind == "l0":
        if at[1] in sites.owners(layout, model.root):
            return None
        return f"L0 of {layout} holds no instruction at {at[1]:08x}"
    try:
        expected = _hex_bytes(item["value"])
    except ValueError:
        return f"value {item['value']!r} is no hexadecimal byte string"
    for rom, data in images(model, layout):
        found = data[at[1]:at[1] + len(expected)]
        if found != expected:
            return f"{rom} holds {found.hex()} at {at[1]:08x}, not {expected.hex()}"
    return None


def _own(ctx):
    if ctx.at is None:
        return "`at` is no location"
    if ctx.at[0] != ctx.symbol.layout:
        return f"`at` lies on {ctx.at[0]}, not on the layout of the symbol"
    return None


def _counterpart(ctx):
    if ctx.to is None:
        return "`to` is neither a reference nor a location"
    if ctx.other is None:
        return "`to` names no symbol of the meaning"
    if ctx.other.meaning is not ctx.symbol.meaning:
        return f"`to` names {ctx.other.key.key}, a symbol of another meaning"
    if ctx.other.layout == ctx.symbol.layout:
        return "`to` names a symbol of the same layout"
    return None


def _compared(ctx):
    """Failures of an item that compares the location `at` of the symbol's
    layout with a location `to` of the counterpart's layout."""
    failure = _own(ctx) or _counterpart(ctx)
    if failure is None and ctx.named:
        failure = "`to` names a symbol; this kind compares locations"
    return failure


def _span(symbol):
    return 1 if symbol.kind == "fn" else storage_size(symbol) or 1


def _verify_l0(ctx):
    failure = _own(ctx)
    if failure:
        return failure
    layout, site = ctx.at
    symbol, root = ctx.symbol, ctx.model.root
    found = sites.references(layout, root).get(site, ())
    span = _span(symbol)
    if any(symbol.address <= address < symbol.address + span for address in found):
        return None
    if symbol.kind == "fn" and symbol.address in sites.owners(layout, root).get(site, ()):
        return None
    return f"L0 of {layout} holds no reference to {symbol.address:08x} at {site:08x}"


def _hex_bytes(value):
    text = str(value).strip().lower().removeprefix("0x")
    return bytes.fromhex(("0" if len(text) % 2 else "") + text)


def _verify_rom_bytes(ctx):
    if ctx.at is None:
        return "`at` is no location"
    layout, address = ctx.at
    if layout not in ctx.model.layouts:
        return f"`at` names the unknown layout {layout}"
    try:
        expected = _hex_bytes(ctx.item["value"])
    except ValueError:
        return f"value {ctx.item['value']!r} is no hexadecimal byte string"
    for rom, data in _images_of(ctx, layout):
        found = data[address:address + len(expected)]
        if found != expected:
            return f"{rom} holds {found.hex()} at {address:08x}, not {expected.hex()}"
    return None


def _verify_did_table(ctx):
    failure = _own(ctx)
    if failure:
        return failure
    layout, address = ctx.at
    words = str(ctx.item["value"]).split()
    for rom, data in _images_of(ctx, layout):
        found = [f"{derive._long(data, address + 4 * index):08x}" for index in range(len(words))]
        if found != words:
            return f"{rom} holds {' '.join(found)} at {address:08x}, not {' '.join(words)}"
    return None


def _relation(ctx, here, there):
    """Whether the instructions `here` of the `at` layout and `there` of the
    `to` layout relate the symbol and its counterpart in the same way."""
    at_code, to_code = ctx.code("at"), ctx.code("to")
    symbol, other = ctx.symbol, ctx.other
    if (symbol.kind == "fn" and at_code.owner.get(here) == symbol.address
            and to_code.owner.get(there) == other.address):
        return True
    relations = {relation for address, relation in to_code.touches(there)
                 if address == other.address}
    return any(address == symbol.address and relation in relations
               for address, relation in at_code.touches(here))


def _functions(ctx):
    """The L0 functions at `at` and at `to`, or a failure."""
    here = ctx.code("at").functions.get(ctx.at[1])
    there = ctx.code("to").functions.get(ctx.to[1])
    if here is None:
        return None, f"{ctx.at[0]}:{ctx.at[1]:08x} is no function of L0"
    if there is None:
        return None, f"{ctx.to[0]}:{ctx.to[1]:08x} is no function of L0"
    return (here, there), None


def _stated_count(ctx, count):
    stated = _int(ctx.item.get("count"))
    if stated != count:
        return f"count {ctx.item.get('count')}; the layouts give {count}"
    return None


def _verify_function_match(ctx):
    failure = _own(ctx) or _counterpart(ctx)
    if failure:
        return failure
    kind = ctx.item["value"]
    if kind not in HASHES:
        return f"hash class {kind!r}; the classes are {', '.join(HASHES)}"
    pair, failure = _functions(ctx)
    if failure:
        return failure
    here, there = pair
    index = HASHES.index(kind)
    if here.hashes[index] != there.hashes[index]:
        return f"the {kind} hashes of {ctx.at[1]:08x} and {ctx.to[1]:08x} differ"
    count = (ctx.code("at").hashed[kind][here.hashes[index]]
             * ctx.code("to").hashed[kind][there.hashes[index]])
    failure = _stated_count(ctx, count)
    if failure:
        return failure
    if ctx.symbol.kind == "fn":
        if (here.entry, there.entry) != (ctx.symbol.address, ctx.other.address):
            return "the functions are not the symbol and its counterpart"
        return None
    if here.instructions != there.instructions:
        return "the functions differ in length"
    first, second = ctx.code("at").bodies[here.entry], ctx.code("to").bodies[there.entry]
    if not any(_relation(ctx, a, b) for a, b in zip(first, second)):
        return "no instruction pair at one ordinal relates the symbol and its counterpart"
    return None


def _verify_byte_identical(ctx):
    failure = _own(ctx) or _counterpart(ctx)
    if failure:
        return failure
    digest = ctx.item["sha256"]
    if ctx.symbol.kind == "fn":
        pair, failure = _functions(ctx)
        if failure:
            return failure
        here, there = pair
        if (here.entry, there.entry) != (ctx.symbol.address, ctx.other.address):
            return "the functions are not the symbol and its counterpart"
        if here.hashes[0] != digest or there.hashes[0] != digest:
            return "the exact bytes of the functions differ from sha256"
        return None
    if (ctx.at[1], ctx.to[1]) != (ctx.symbol.address, ctx.other.address):
        return "the ranges do not start at the symbol and its counterpart"
    size = storage_size(ctx.symbol)
    if size is None:
        return "the symbol states no storage size"
    for layout, address in (ctx.at, ctx.to):
        for rom, data in _images_of(ctx, layout):
            if hashlib.sha256(data[address:address + size]).hexdigest() != digest:
                return f"the {size} bytes of {rom} at {address:08x} differ from sha256"
    return None


def _verify_masked_match(ctx):
    failure = _compared(ctx)
    if failure:
        return failure
    words = _int(ctx.item["value"])
    if words is None or words < ctx.minimum:
        return f"{ctx.item['value']} words; a match needs {ctx.minimum}"
    at_code, to_code = ctx.code("at"), ctx.code("to")
    pattern = at_code.pattern(ctx.at[1], words)
    if pattern is None or pattern != to_code.pattern(ctx.to[1], words):
        return f"the {words} masked words at {ctx.at[1]:08x} and {ctx.to[1]:08x} differ"
    failure = _stated_count(ctx, len(at_code.find(pattern)) * len(to_code.find(pattern)))
    if failure:
        return failure
    if not any(_relation(ctx, ctx.at[1] + 2 * offset, ctx.to[1] + 2 * offset)
               for offset in range(words)):
        return "no aligned instruction relates the symbol and its counterpart"
    return None


def homologous(model, layout, entry, other_layout, other_entry):
    """Functions of one `fn` meaning, or a pair whose hash of some class is
    unique on both layouts."""
    here = model.symbols.get(SymbolKey(layout, "fn", entry))
    there = model.symbols.get(SymbolKey(other_layout, "fn", other_entry))
    if here is not None and there is not None and here.meaning is there.meaning:
        return True
    left, right = code(layout, model.root), code(other_layout, model.root)
    first, second = left.functions.get(entry), right.functions.get(other_entry)
    if first is None or second is None:
        return False
    return any(first.hashes[index] == second.hashes[index]
               and left.hashed[name][first.hashes[index]] == 1
               and right.hashed[name][second.hashes[index]] == 1
               for index, name in enumerate(HASHES))


def _verify_literal_pool(ctx):
    failure = _compared(ctx)
    if failure:
        return failure
    at_code, to_code = ctx.code("at"), ctx.code("to")
    value = _int("0x" + str(ctx.item["value"]).lower().removeprefix("0x"))
    here = derive._long(at_code.data, ctx.at[1])
    there = derive._long(to_code.data, ctx.to[1])
    if here != value:
        return f"the literal at {ctx.at[1]:08x} is {here:08x}, not {ctx.item['value']}"
    if (here, there) != (ctx.symbol.address, ctx.other.address):
        return "the literals are not the addresses of the symbol and its counterpart"
    for site in sorted(at_code.pooled.get(ctx.at[1], ())):
        region = at_code.aligned(site, to_code)
        if region is not None and to_code.literals.get(region.site, (None,))[0] == ctx.to[1]:
            return None
        place = at_code.ordinal(site)
        for other_site in sorted(to_code.pooled.get(ctx.to[1], ())):
            other_place = to_code.ordinal(other_site)
            if (place and other_place and place[1] == other_place[1]
                    and homologous(ctx.model, ctx.at[0], place[0], ctx.to[0], other_place[0])):
                return None
    return "no load of the pool at `at` aligns with a load of the pool at `to`"


def _verify_call_ordinal(ctx):
    failure = _compared(ctx)
    if failure:
        return failure
    at_code, to_code = ctx.code("at"), ctx.code("to")
    here, there = at_code.call_ordinal(ctx.at[1]), to_code.call_ordinal(ctx.to[1])
    if here is None or there is None:
        return "`at` and `to` are not both calls of L0 functions"
    ordinal = _int(ctx.item["value"])
    if (here[1], there[1]) != (ordinal, ordinal):
        return (f"the calls are the calls {here[1]} and {there[1]} of their functions, "
                f"not {ctx.item['value']}")
    if not homologous(ctx.model, ctx.at[0], here[0], ctx.to[0], there[0]):
        return "the calling functions are neither one meaning nor a unique hash pair"
    mine = {relation for address, relation in at_code.touches(ctx.at[1])
            if address == ctx.symbol.address}
    if not mine:
        return f"the call at `at` does not relate {ctx.symbol.address:08x}"
    candidates = {address for address, relation in to_code.touches(ctx.to[1])
                  if relation in mine}
    if ctx.other.address not in candidates:
        return f"the call at `to` does not relate {ctx.other.address:08x} in the same way"
    return _stated_count(ctx, len(candidates))


def interp_entry(model, symbol):
    """(kernel, entry) of the `[interp]` of a function on its layout: the
    symbol of the kernel meaning there and the address of the kernel entry, or
    None."""
    table = symbol.value("interp")
    held = model.symbols.get(table.get("kernel")) if isinstance(table, dict) else None
    kernel = (held.meaning.symbols.get(symbol.layout)
              if held is not None and held.meaning is not None else None)
    if kernel is None:
        return None
    return kernel, kernel.address + (table.get("offset") or 0)


def kernel_calls(model, symbol, entry):
    """The instructions of the L0 body of a function that reference `entry`."""
    references = sites.references(symbol.layout, model.root)
    return [site for site in sites.bodies(symbol.layout, model.root).get(symbol.address, ())
            if entry in references.get(site, ())]


def _calls_kernel(model, symbol):
    """None when a wrapper is its own kernel or its L0 body references the
    kernel entry of its `[interp]`, else what fails."""
    found = interp_entry(model, symbol)
    if found is None:
        return f"the [interp] of {symbol.key.key} names no kernel on {symbol.layout}"
    kernel, entry = found
    if kernel is symbol or kernel_calls(model, symbol, entry):
        return None
    return f"L0 of {symbol.layout} holds no call of {entry:08x} in {symbol.address:08x}"


_WRAPPERS = weakref.WeakKeyDictionary()


def _wrappers(model):
    """{id of a kernel meaning: the meanings whose `[interp]` names it}."""
    found = _WRAPPERS.get(model)
    if found is None:
        found = defaultdict(list)
        for meaning in model.meanings:
            tables = [meaning.props.get("interp")]
            tables += [symbol.props.get("interp") for symbol in meaning.symbols.values()]
            kernels = {id(held.meaning) for held in (
                model.symbols.get(table.get("kernel")) for table in tables
                if isinstance(table, dict)) if held is not None and held.meaning is not None}
            for kernel in kernels:
                found[kernel].append(meaning)
        _WRAPPERS[model] = found
    return found


def _verify_interp_contract(ctx):
    failure = _counterpart(ctx)
    if failure:
        return failure
    if ctx.symbol.kind != "fn":
        return "interp-contract evidence relates two functions"
    model, symbol, other = ctx.model, ctx.symbol, ctx.other
    if not ctx.named and ctx.to[1] != other.address:
        return f"`to` locates {ctx.to[1]:08x}, not {other.key.key}"
    key = _int("0x" + str(ctx.item["key"]).lower().removeprefix("0x"))
    mine, theirs = symbol.value("interp") or {}, other.value("interp") or {}
    if mine or theirs:
        if key != other.address:
            return f"key {ctx.item['key']} is not the address of {other.key.key}"
        differ = [name for name in CONTRACT_KEYS if mine.get(name) != theirs.get(name)]
        if differ:
            return f"the interpolation contracts differ in {', '.join(differ)}"
        return _calls_kernel(model, symbol) or _calls_kernel(model, other)
    for wrapper in _wrappers(model).get(id(symbol.meaning), ()):
        here, there = wrapper.symbols.get(symbol.layout), wrapper.symbols.get(other.layout)
        if here is None or there is None:
            continue
        mine, theirs = interp_entry(model, here), interp_entry(model, there)
        if (mine is not None and theirs is not None and mine[0] is symbol
                and theirs[0] is other and theirs[1] == key
                and _calls_kernel(model, here) is None and _calls_kernel(model, there) is None):
            return None
    return (f"no wrapper of one meaning on {symbol.layout} and {other.layout} calls the kernel "
            f"entry {ctx.item['key']} of {other.key.key}")


VERIFIERS = {
    "l0": _verify_l0,
    "rom-bytes": _verify_rom_bytes,
    "did-table": _verify_did_table,
    "function-match": _verify_function_match,
    "byte-identical": _verify_byte_identical,
    "masked-match": _verify_masked_match,
    "literal-pool": _verify_literal_pool,
    "call-ordinal": _verify_call_ordinal,
    "interp-contract": _verify_interp_contract,
}


# Grounding.

def rank(item):
    """The level rank that an evidence item grounds: its kind's level, and at
    most `candidate` for a counted match whose count is not 1."""
    _, level = vocab.EVIDENCE_KINDS.get(item.get("kind"), ((), None))
    if level is None:
        return -1
    found = vocab.LEVEL_RANK[level]
    if item.get("kind") in COUNTED and _int(item.get("count")) != 1:
        found = min(found, CANDIDATE)
    return found


def _complete(item):
    required, _ = vocab.EVIDENCE_KINDS.get(item.get("kind"), ((), None))
    return all(item.get(key) not in (None, "") for key in required)


def _anchor(model, symbol, failures):
    """The rank that identity evidence of the symbol's own layout grounds,
    or a `relies` link of its meaning with evidence of that layout."""
    best = -1
    for item in symbol.evidence:
        if item.get("supports", "identity") != "identity" or rank(item) <= best:
            continue
        at = location(item.get("at"))
        if at is not None and at[0] != symbol.layout:
            continue
        if not _complete(item):
            continue
        failure = verify(model, symbol, item)
        if failure is not None:
            failures.append((item, failure))
            continue
        best = rank(item)
    meaning = symbol.meaning
    for link in meaning.links if meaning is not None else ():
        if (link.owner is not meaning or not link.props.get("relies")
                or link.props.get("supports", "identity") != "identity"):
            continue
        for item in link.evidence:
            at = location(item.get("at"))
            if at is not None and at[0] == symbol.layout and _complete(item):
                best = max(best, rank(item))
    return best


def grounded(model, keys):
    """{symbol key: (rank, failures)} for the symbols of `keys` and every
    symbol their homology evidence reaches: the highest level rank that
    identity evidence of the symbol's own layout grounds, or homology evidence
    toward a grounded symbol, bounded by the rank of that evidence; -1 when
    nothing grounds the symbol. `failures` pairs each evidence item that does
    not verify with the reason."""
    anchors, edges, failures = {}, defaultdict(list), defaultdict(list)
    pending, seen = list(keys), set()
    while pending:
        key = pending.pop()
        if key in seen or key not in model.symbols:
            continue
        seen.add(key)
        symbol = model.symbols[key]
        anchors[key] = _anchor(model, symbol, failures[key])
        for item in symbol.evidence:
            if item.get("supports") != "homology":
                continue
            if item.get("kind") not in HOMOLOGY_KINDS:
                failures[key].append((item, f"{item.get('kind')} evidence supports no homology"))
                continue
            failure = verify(model, symbol, item)
            if failure is not None:
                failures[key].append((item, failure))
                continue
            other = context(model, symbol, item).other
            if other is not None and other.key != key:
                edges[key].append((other.key, rank(item)))
                pending.append(other.key)
    level = dict(anchors)
    changed = True
    while changed:
        changed = False
        for key, targets in edges.items():
            for target, bound in targets:
                value = min(bound, level.get(target, -1))
                if value > level[key]:
                    level[key] = value
                    changed = True
    return {key: (level[key], failures[key]) for key in seen}


# Search.

@dataclass
class Candidate:
    """A candidate address with its strongest evidence item, the number of
    items that voted for it, and those items."""

    address: int
    evidence: dict
    votes: int = 0
    items: list = field(default_factory=list)


@dataclass
class Search:
    """The candidates for the counterpart of `symbol` on `layout`, by the
    evidence kind of `method`."""

    symbol: object
    layout: str
    method: str
    candidates: dict = field(default_factory=dict)

    @property
    def target(self):
        return self.symbol.key.location

    @property
    def count(self):
        return len(self.candidates)


def _function_pairs(home, other, entry):
    """{entry on `other`: hash class} of the functions whose hash equals that
    of `entry` on `home` and is unique on both layouts."""
    function = home.functions.get(entry)
    found = {}
    for index, name in enumerate(HASHES):
        if function is None or home.hashed[name][function.hashes[index]] != 1:
            continue
        for candidate, item in other.functions.items():
            if item.hashes[index] == function.hashes[index] and \
                    other.hashed[name][item.hashes[index]] == 1:
                found.setdefault(candidate, name)
    return found


def search(model, symbol, layout):
    """The counterparts of `symbol` on `layout`: for a function, the unique
    hash pairs and the functions that its aligned calls and body reach; for a
    datum, the addresses that aligned sites touch in the same way, and those
    at the same ordinal of a function whose hash pairs uniquely with one that
    touches the symbol."""
    home, other = code(symbol.layout, model.root), code(layout, model.root)
    result = Search(symbol, layout, "masked-match")
    votes, best, every = defaultdict(int), {}, defaultdict(list)

    def vote(address, item, strength):
        votes[address] += 1
        every[address].append(item)
        if address not in best or strength > best[address][0]:
            best[address] = (strength, item)

    if symbol.kind == "fn":
        for address, name in _function_pairs(home, other, symbol.address).items():
            vote(address, {"kind": "function-match", "supports": "homology",
                           "at": f"{layout}:{address:08x}", "to": symbol.key,
                           "count": 1, "value": name}, 1 << 20)
        seeds = [(site, "call") for site, relation in home.sites_of(symbol.address)
                 if relation == "call"]
        seeds += [(site, "body") for site in home.bodies.get(symbol.address, ())[::home.gram]]
    else:
        seeds = sorted(home.sites_of(symbol.address))
    for site, relation in sorted(seeds):
        region = home.aligned(site, other)
        if region is None:
            continue
        if relation == "body":
            found = {other.owner.get(region.site)} - {None}
        else:
            found = {address for address, kind in other.touches(region.site) if kind == relation}
        if symbol.kind == "fn":
            found &= set(other.functions)
        for address in found:
            vote(address, {"kind": "masked-match", "supports": "homology",
                           "at": f"{layout}:{region.match:08x}",
                           "to": f"{symbol.layout}:{region.start:08x}",
                           "count": region.count * region.matches, "value": region.words},
                 region.words)
    if symbol.kind != "fn":
        for site, relation in sorted(seeds):
            place = home.ordinal(site)
            if place is None:
                continue
            pairs = _function_pairs(home, other, place[0])
            for entry, name in pairs.items():
                if home.functions[place[0]].instructions != other.functions[entry].instructions:
                    continue
                mapped = other.bodies[entry][place[1]]
                for address, kind in other.touches(mapped):
                    if kind == relation:
                        vote(address, {"kind": "function-match", "supports": "homology",
                                       "at": f"{layout}:{entry:08x}",
                                       "to": f"{symbol.layout}:{place[0]:08x}",
                                       "count": 1, "value": name}, 0)
    if best and all(item["kind"] == "function-match" for _, item in best.values()):
        result.method = "function-match"
    for address, (_, item) in best.items():
        result.candidates[address] = Candidate(address, item, votes[address], every[address])
    return result


# Typing.

# The kinds that type the homology of a symbol toward its counterpart, in the
# order in which `typed` picks the item.
TYPED = ("call-ordinal", "literal-pool", "masked-match", "function-match", "byte-identical")


def touching(model, symbol):
    """Sorted instructions of the symbol's layout that touch an address of its
    storage, or its entry for a function, in a relation of the matchers."""
    here = code(symbol.layout, model.root)
    return sorted({site for address in range(symbol.address, symbol.address + _span(symbol))
                   for site, _ in here.sites_of(address)})


def _call_ordinals(model, symbol, other):
    here, there = code(symbol.layout, model.root), code(other.layout, model.root)
    for site in sorted({site for site, _ in here.sites_of(symbol.address)}):
        place = here.call_ordinal(site)
        if place is None:
            continue
        mine = {relation for address, relation in here.touches(site)
                if address == symbol.address}
        for other_site in sorted({site for site, relation in there.sites_of(other.address)
                                  if relation in mine}):
            other_place = there.call_ordinal(other_site)
            if other_place is None or other_place[1] != place[1]:
                continue
            count = len({address for address, relation in there.touches(other_site)
                         if relation in mine})
            yield {"kind": "call-ordinal", "supports": "homology",
                   "at": f"{symbol.layout}:{site:08x}", "to": f"{other.layout}:{other_site:08x}",
                   "count": count, "value": place[1]}


def _literal_pools(model, symbol, other):
    here, there = code(symbol.layout, model.root), code(other.layout, model.root)
    mine = sorted({pool for pool, value in here.literals.values() if value == symbol.address})
    theirs = sorted({pool for pool, value in there.literals.values() if value == other.address})
    for pool in mine:
        for other_pool in theirs:
            yield {"kind": "literal-pool", "supports": "homology",
                   "at": f"{symbol.layout}:{pool:08x}", "to": f"{other.layout}:{other_pool:08x}",
                   "value": f"{symbol.address:08x}"}


def _byte_identical(model, symbol, other):
    if symbol.kind == "fn":
        here = code(symbol.layout, model.root).functions.get(symbol.address)
        there = code(other.layout, model.root).functions.get(other.address)
        if here is None or there is None or here.hashes[0] != there.hashes[0]:
            return
        yield {"kind": "byte-identical", "supports": "homology",
               "at": f"{symbol.layout}:{symbol.address:08x}",
               "to": f"{other.layout}:{other.address:08x}", "sha256": here.hashes[0]}
        return
    size = storage_size(symbol)
    if size is None or storage_size(other) != size:
        return
    digests = {hashlib.sha256(data[address:address + size]).hexdigest()
               for layout, address, only in (
                   (symbol.layout, symbol.address, symbol.props.get("images")),
                   (other.layout, other.address, None))
               for _, data in images(model, layout, only)}
    if len(digests) == 1:
        yield {"kind": "byte-identical", "supports": "homology",
               "at": f"{symbol.layout}:{symbol.address:08x}",
               "to": f"{other.layout}:{other.address:08x}", "sha256": digests.pop()}


def homology_items(model, symbol, other):
    """The evidence items of the kinds of `TYPED` that the matchers find for
    `symbol` toward `other`, a symbol of its meaning on another layout; they
    still need `verify`."""
    yield from _call_ordinals(model, symbol, other)
    yield from _literal_pools(model, symbol, other)
    hit = search(model, other, symbol.layout).candidates.get(symbol.address)
    if hit is not None:
        yield from hit.items
    yield from _byte_identical(model, symbol, other)


def _typed_order(item):
    return TYPED.index(item["kind"]), str(item.get("at")), str(item.get("to"))


def typed(model, symbol, other):
    """The evidence item that types the homology of `symbol` toward `other`:
    the first item of `homology_items`, by the order of `TYPED` and then by
    `at` and `to`, that verifies and grounds `code`; None when none does."""
    for item in sorted(homology_items(model, symbol, other), key=_typed_order):
        if rank(item) >= vocab.LEVEL_RANK["code"] and verify(model, symbol, item) is None:
            return item
    return None


# The writer gate.

@dataclass(frozen=True)
class Contradiction:
    """A store at `site` of one symbol of a meaning that aligns with a store
    of another address on the layout of the other symbol; `symbol` is the
    symbol other than the home symbol."""

    meaning: object
    symbol: object
    site: str
    message: str


def writers(model):
    """[Contradiction] of the `ram` and `reg` meanings, in both directions
    between the home symbol and each other symbol."""
    found = []
    for meaning in model.meanings:
        home = meaning.home_symbol
        if meaning.kind not in ("ram", "reg") or home is None:
            continue
        for layout, symbol in sorted(meaning.symbols.items()):
            if layout == home.layout:
                continue
            for source, target in ((home, symbol), (symbol, home)):
                left = code(source.layout, model.root)
                right = code(target.layout, model.root)
                for site in left.stores(source.address):
                    region = left.aligned(site, right)
                    if region is None:
                        continue
                    stored = {address for address, relation in right.touches(region.site)
                              if relation in STORES}
                    if stored and target.address not in stored:
                        found.append(Contradiction(meaning, symbol, f"{source.layout}:{site:08x}", (
                            f"the store at {source.layout}:{site:08x} of {source.address:08x} "
                            f"aligns over {region.words} words with {target.layout}:"
                            f"{region.site:08x}, which stores "
                            f"{', '.join(f'{address:08x}' for address in sorted(stored))}, "
                            f"not {target.address:08x}")))
    return found
