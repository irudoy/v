"""The L0 part of the graph: nodes and relationships of one layout's L0.

The rows of `l0_rows` depend only on the L0 files of the layout, its image, the
address spaces of its MCU, and the modules that build them, whose digest
decides when the loader replaces the L0 part of a layout.
"""

from collections import Counter, defaultdict
import csv
from itertools import combinations
import re

from kb import derive, repo
from kb.values import properties

CALL_REFERENCES = ("unconditional_call", "computed_call")
POINTER_REFERENCES = ("data", "param")
WIDTH = {"b": 1, "w": 2, "l": 4}
SUFFIX = re.compile(r"\.([bwl])$")
DERIVED_SRC = "literal-pairs"
RAM_ACCESS_MODES = frozenset({'read', 'write', 'read_write', 'load', 'store', 'update'})


def _read(path):
    with path.open(newline="", encoding="utf-8") as source:
        yield from csv.DictReader(source)


def space_of(spaces, address):
    for name in ("rom", "ram", "io"):
        start, end = spaces[name]
        if start <= address < end:
            return name
    return None


def width_of(mnemonic):
    match = SUFFIX.search(mnemonic)
    return WIDTH[match.group(1)] if match else None


def shared_ram(functions, locations, accesses):
    """One weighted candidate edge per pair, counting distinct RAM locations.

    Duplicate access sites and producers do not increase a pair's weight.
    ROM, peripheral registers, pointer-only literals, and functions outside
    the layout are excluded.
    These edges describe structural proximity, without a semantic claim.
    """
    entries = {row['key'] for row in functions}
    ram = {row['key'] for row in locations if row['space'] == 'ram'}
    users = defaultdict(set)
    for access in accesses:
        if (access['from'] in entries and access['to'] in ram
                and RAM_ACCESS_MODES.intersection(access['props']['modes'])):
            users[access['to']].add(access['from'])
    weights = Counter(pair for found in users.values()
                      for pair in combinations(sorted(found), 2))
    return [{'from': first, 'to': second, 'props': {
                'weight': weight, 'producer': 'derived', 'src': 'shared-ram'}}
            for (first, second), weight in sorted(weights.items())]


def l0_rows(layout, spaces, root=repo.ROOT):
    """Nodes and relationships of one layout's L0 and its literal pairs.

    - `Function` from funcs.csv with the hashes of function_signatures.csv.
    - `CALL` from calls.csv, with the call sites of function_references.csv.
    - `ACCESS` with producer `l0` from function_references.csv: every reference
      to RAM or a register with its reference type as mode, every data or
      parameter reference to ROM, and every pool literal that names RAM or a
      register, with mode `literal` and the pool address.
    - `ACCESS` with producer `derived` from the literal pairs of kb.derive.
    - `Location` at every accessed address inside the spaces of the MCU.
    """
    base = root / repo.L0 / layout.id
    src = {name: (repo.L0 / layout.id / name).as_posix()
           for name in ("funcs.csv", "calls.csv", "function_references.csv")}
    key = lambda address: f"{layout.id}:{address:08x}"
    signatures = {row["addr"]: row for row in _read(base / "function_signatures.csv")}
    functions = []
    for row in _read(base / "funcs.csv"):
        address = int(row["addr"], 16)
        signature = signatures.get(row["addr"], {})
        functions.append(properties({
            "key": key(address), "layout": layout.id, "address": address,
            "size": int(row["size"]), "thunk": row["is_thunk"] == "true",
            "external": row["is_external"] == "true",
            "instructions": int(signature["instructions"]) if signature else None,
            "exact_sha256": signature.get("exact_sha256"),
            "mnemonic_sha256": signature.get("mnemonic_sha256"),
            "shape_sha256": signature.get("shape_sha256"),
            "producer": "l0", "src": src["funcs.csv"],
        }))
    call_sites = defaultdict(set)
    direct = defaultdict(list)
    outside = Counter()
    for row in _read(base / "function_references.csv"):
        func, site = int(row["func_addr"], 16), int(row["ins_addr"], 16)
        target, kind = int(row["ref_addr"], 16), row["ref_type"]
        if kind in CALL_REFERENCES:
            call_sites[(func, target)].add(site)
            continue
        space = space_of(spaces, target)
        if space in ("ram", "io"):
            direct[(func, target)].append(
                {"site": site, "mode": kind, "width": width_of(row["mnemonic"])})
        elif space == "rom" and kind in POINTER_REFERENCES:
            direct[(func, target)].append({"site": site, "mode": kind})
        if kind == "read" and row["width"] == "4" and row["value_hex"]:
            literal = int(row["value_hex"], 16)
            if space_of(spaces, literal) in ("ram", "io"):
                direct[(func, literal)].append({"site": site, "mode": "literal",
                                                "pool": target})
    calls = []
    for row in _read(base / "calls.csv"):
        caller, callee = int(row["src"], 16), int(row["dst"], 16)
        calls.append({"from": key(caller), "to": key(callee), "props": properties({
            "sites": sorted(call_sites.get((caller, callee), ())),
            "weight": 1, "producer": "l0", "src": src["calls.csv"]})})
    derived = defaultdict(list)
    for pair in derive.literal_pairs(layout.id, root):
        if space_of(spaces, pair.address) is None:
            outside["derived"] += 1
            continue
        site = {"site": pair.ins, "mode": pair.mode, "width": pair.size,
                "literal": pair.literal, "pool": pair.pool, "base": pair.base}
        if pair.indexed:
            site["indexed"] = True
        derived[(pair.func, pair.address)].append(site)
    locations = {}
    accesses = []
    for producer, found, origin in (("l0", direct, src["function_references.csv"]),
                                    ("derived", derived, DERIVED_SRC)):
        for (func, address), sites in sorted(found.items()):
            if address not in locations or producer == "l0" and \
                    locations[address]["producer"] != "l0":
                locations[address] = {
                    "key": key(address), "layout": layout.id, "address": address,
                    "space": space_of(spaces, address), "producer": producer, "src": origin}
            sites = sorted((properties(site) for site in sites), key=lambda s: (s["site"], s["mode"]))
            accesses.append({"from": key(func), "to": key(address), "props": {
                "modes": sorted({site["mode"] for site in sites}), "sites": sites,
                "producer": producer, "src": origin}})
    location_rows = [locations[address] for address in sorted(locations)]
    return {
        "functions": functions,
        "calls": calls,
        "locations": location_rows,
        "accesses": accesses,
        "shared_ram": shared_ram(functions, location_rows, accesses),
        "outside": dict(outside),
    }
