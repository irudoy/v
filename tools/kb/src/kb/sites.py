"""Reproduction of the `site:` evidence of the ledgers from L0.

A `site:<a>` token of a ledger row reproduces from L0 when L0 and its image
connect the site to the row:

- `reference`: an L0 reference at the site, that is a Ghidra reference, a
  pool literal, a literal pair, or an argument of a census call, names the
  row's subject, an address within the subject's table, or an address the row
  names;
- `body`: the site is an instruction of a function whose entry is the subject
  or an address the row names;
- `pointer`: the image holds, at the site, a 32-bit address that is the
  subject or an address the row names;
- `linked`: the site is an instruction of a function that L0 links to the
  subject: its body references the subject or an address within its table,
  or a census call with such an argument runs through it as the calling
  function, the wrapper, or the kernel.

The addresses a row names are the eight-digit hexadecimal addresses of its
structured columns and evidence tokens; the prose columns do not name them.
"""

import bisect
import collections
import csv
from dataclasses import dataclass
from functools import lru_cache
import re

from kb import derive, l0, repo, sh2

# Ledger file suffix, subject column, and prose columns of each JK08A ledger.
LEDGERS = {
    "funcs": ("addr", ("semantics", "contract", "note")),
    "vars": ("addr", ("semantics", "note")),
    "findings": ("addr", ("semantics", "note")),
    "maps": ("table", ("semantics", "diagnostic_context", "note")),
    "axes": ("addr", ("note",)),
    "diagnostic-bindings": ("firmware_addr", ("note",)),
}
SITE_RE = re.compile(r"\bsite:([0-9a-f]{8})\b")
ADDRESS_RE = re.compile(r"(?<![0-9A-Za-z_])([0-9a-f]{8})(?![0-9A-Za-z_])")
STORAGE_BYTES = {"uint8": 1, "int8": 1, "uint16": 2, "int16": 2, "uint32": 4, "int32": 4,
                 "float": 4}
CENSUS_ADDRESSES = ("kernel", "wrapper", "slot", "accessor", "bt_r4", "bt_r5", "bt_r6",
                    "df_r4", "df_r5", "df_r6", "df_r7")
KINDS = ("reference", "body", "pointer", "linked")


@dataclass(frozen=True)
class Site:
    ledger: str
    subject: int
    site: int
    kind: str | None


def _rows(path):
    with path.open(newline="", encoding="utf-8") as source:
        yield from csv.DictReader(source)


@lru_cache(maxsize=None)
def references(layout_id, root=repo.ROOT):
    """{instruction or pool address: addresses L0 references there}."""
    base = root / repo.L0 / layout_id
    found = collections.defaultdict(set)
    pools = {}
    for row in _rows(base / "function_references.csv"):
        site = int(row["ins_addr"], 16)
        found[site].add(int(row["ref_addr"], 16))
        if row["value_hex"] and row["width"] in ("2", "4"):
            value = int(row["value_hex"], 16)
            if row["width"] == "2":
                value = sh2.sext(value, 16) & sh2.MASK
            found[site].add(value)
            pools[int(row["ref_addr"], 16)] = value
    for pair in derive.literal_pairs(layout_id, root):
        found[pair.ins].update((pair.address, pair.literal, pair.pool))
        pools[pair.pool] = pair.literal
    plan = l0.census(layout_id, root)
    for kernel in plan.kernels:
        for row in _rows(base / l0.Census.file(kernel)):
            found[int(row["callsite"], 16)].update(
                int(row[column], 16) for column in CENSUS_ADDRESSES if row[column]
            )
    for pool, value in pools.items():
        found[pool].add(value)
    return found


@lru_cache(maxsize=None)
def bodies(layout_id, root=repo.ROOT):
    """{function entry: sorted instruction addresses of its body}."""
    return derive.bodies(layout_id, root)


@lru_cache(maxsize=None)
def owners(layout_id, root=repo.ROOT):
    """{instruction address: entries of the functions whose body holds it}."""
    found = collections.defaultdict(set)
    for func, addresses in bodies(layout_id, root).items():
        for address in addresses:
            found[address].add(func)
    return found


@lru_cache(maxsize=None)
def linkers(layout_id, root=repo.ROOT):
    """Sorted (address, function) pairs: the functions that reach an address,
    by a reference in their body or as the path of a census call."""
    owned = owners(layout_id, root)
    found = set()
    for site, addresses in references(layout_id, root).items():
        for func in owned.get(site, ()):
            found.update((address, func) for address in addresses)
    base = root / repo.L0 / layout_id
    for kernel in l0.census(layout_id, root).kernels:
        for row in _rows(base / l0.Census.file(kernel)):
            path = {int(row["kernel"], 16), int(row["wrapper"], 16)}
            path |= owned.get(int(row["callsite"], 16), set())
            for column in CENSUS_ADDRESSES[4:]:
                if row[column]:
                    found.update((int(row[column], 16), func) for func in path)
    return sorted(found)


def linked(subject, span, links):
    """Functions that L0 links to the addresses [subject, subject + span)."""
    start = bisect.bisect_left(links, (subject, -1))
    functions = set()
    for address, func in links[start:]:
        if address >= subject + span:
            break
        functions.add(func)
    return functions


def extent(ledger, row):
    """Bytes of the subject: the table size where the row states dimensions."""
    size = STORAGE_BYTES.get(row.get("storagetype", ""), 1)
    if ledger == "maps":
        dim = row["dim"]
        if dim.startswith("1D-"):
            return int(dim[3:]) * size
        if "x" in dim:
            width, height = dim.split("x")
            return int(width) * int(height) * size
    if ledger == "findings" and row["width"]:
        return int(row["width"]) * int(row["height"] or 1) * size
    return 1


def classify(site, subject, span, named, found, owned, data, links):
    at = found.get(site, ())
    if any(subject <= address < subject + span for address in at) or named & set(at):
        return "reference"
    functions = owned.get(site, set())
    if functions & (named | {subject}):
        return "body"
    if site + 4 <= len(data):
        pointer = int.from_bytes(data[site:site + 4], "big")
        if pointer in named or subject <= pointer < subject + span:
            return "pointer"
    if functions & linked(subject, span, links):
        return "linked"
    return None


def ledger_sites(layout_id, rom, root=repo.ROOT):
    """Every site token of the ledgers of `rom`, with its reproduction kind."""
    layout = repo.layout(layout_id, root)
    data = derive.image_bytes(layout, root)
    found = references(layout_id, root)
    owned = owners(layout_id, root)
    links = linkers(layout_id, root)
    sites = []
    for ledger, (subject_column, prose) in LEDGERS.items():
        path = root / "defs" / f"{rom}.{ledger}.csv"
        if not path.exists():
            continue
        for row in _rows(path):
            subject = int(row[subject_column], 16)
            structured = ";".join(value for column, value in row.items()
                                  if value and column not in prose)
            named = {int(value, 16) for value in ADDRESS_RE.findall(structured)}
            listed = {int(value, 16) for value in SITE_RE.findall(structured)}
            named -= listed
            span = extent(ledger, row)
            for site in sorted(listed):
                sites.append(Site(ledger, subject, site,
                                  classify(site, subject, span, named, found, owned, data, links)))
    return sites


def summary(sites):
    """{ledger or "all": Counter of kinds with None for unreproduced}."""
    counts = collections.defaultdict(collections.Counter)
    for site in sites:
        counts[site.ledger][site.kind] += 1
        counts["all"][site.kind] += 1
    return counts


def share(counter):
    total = sum(counter.values())
    return (total - counter[None]) / total if total else 1.0
