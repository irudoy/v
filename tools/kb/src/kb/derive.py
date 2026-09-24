"""Relations the compiler derives from L0 (tools/kb/SPEC.md, section 8.5).

Literal pairing propagates register values through the control flow of each
function body: a register holds a pool literal at an instruction when every
path from the function entry reaches it with that literal, copied or offset by
immediates. An access through such a register yields the accessed address,
the literal, its pool address, and the base register.
"""

import csv
from dataclasses import dataclass
from functools import lru_cache

from kb import repo, sh2

UNKNOWN = None


@dataclass(frozen=True, order=True)
class Pair:
    """An access whose base register holds a pool literal on every path."""

    func: int
    ins: int
    address: int
    literal: int
    pool: int
    base: str
    mode: str
    size: int
    indexed: bool


def read_rows(path):
    with path.open(newline="", encoding="utf-8") as source:
        yield from csv.DictReader(source)


def bodies(layout_id, root=repo.ROOT):
    """{function entry: sorted instruction addresses} from function_tokens.csv."""
    found = {}
    for row in read_rows(root / repo.L0 / layout_id / "function_tokens.csv"):
        found.setdefault(int(row["func_addr"], 16), []).append(int(row["ins_addr"], 16))
    return {func: sorted(addresses) for func, addresses in found.items()}


def image_bytes(layout, root=repo.ROOT):
    image = repo.images(root)[layout.image]
    data = image.path.read_bytes()
    if repo.sha256_file(image.path) != image.sha256:
        raise repo.KbError(f"{image.path}: digest differs from the image catalog")
    return data


def _word(data, address):
    return (data[address] << 8) | data[address + 1]


def _long(data, address):
    return int.from_bytes(data[address:address + 4], "big")


def _successors(address, insns, body):
    """Successors in the flow graph; a delayed transfer leaves from its slot."""
    insn = insns[address]
    if insn.delayed:
        return [address + 2] if address + 2 in body else []
    return _after(address, insn, body)


def _after(address, insn, body, slot=None):
    fall = (slot if slot is not None else address) + 2
    targets = []
    if insn.flow in (None, "call", "cbranch"):
        targets.append(fall)
    if insn.flow in ("branch", "cbranch") and insn.target is not None:
        targets.append(insn.target)
    return [target for target in targets if target in body]


def _transfer(state, insn, data):
    """The register state after one instruction.

    A known register holds (value, pool address, pool literal); a value that
    no pool literal feeds carries None for both."""
    out = dict(state)
    if insn.gbr is not None:
        value = state.get(insn.gbr[1]) if insn.gbr[0] == "copy" else UNKNOWN
        if value is UNKNOWN:
            out.pop("gbr", None)
        else:
            out["gbr"] = value
    for register in insn.writes:
        out.pop(register, None)
    if insn.dest is None or insn.value is None:
        return out
    kind = insn.value[0]
    value = UNKNOWN
    if kind == "const":
        value = (insn.value[1], None, None)
    elif kind == "pool":
        pool, size = insn.value[1], insn.value[2]
        if pool + size <= len(data):
            literal = _long(data, pool) if size == 4 else sh2.sext(_word(data, pool), 16) & sh2.MASK
            value = (literal, pool, literal)
    elif kind == "mova":
        value = (insn.value[1], None, None)
    elif kind == "copy":
        value = state.get(insn.value[1])
    elif kind == "addi":
        current = state.get(insn.dest)
        if current is not None:
            value = ((current[0] + insn.value[1]) & sh2.MASK, *current[1:])
    elif kind in ("add", "sub"):
        left, right = state.get(insn.dest), state.get(insn.value[1])
        if left is not None and right is not None:
            total = left[0] + right[0] if kind == "add" else left[0] - right[0]
            source = left if left[1] is not None else right
            value = (total & sh2.MASK, *source[1:])
    elif kind == "gbr":
        value = state.get("gbr")
    elif kind in ("extu", "exts"):
        source = state.get(insn.value[2])
        if source is not None:
            bits = insn.value[1]
            number = source[0] & ((1 << bits) - 1)
            if kind == "exts":
                number = sh2.sext(number, bits) & sh2.MASK
            value = (number, *source[1:])
    if value is not None:
        out[insn.dest] = value
    return out


def _meet(left, right):
    return {key: value for key, value in left.items() if right.get(key) == value}


def _clobber(state):
    return {key: value for key, value in state.items() if key not in sh2.CALLER_SAVED}


def function_pairs(func, addresses, data):
    """Literal pairs of one function body."""
    body = set(addresses)
    insns = {address: sh2.decode(_word(data, address), address) for address in addresses}
    # A delay slot inherits the transfer of the instruction before it.
    owner = {address + 2: address for address, insn in insns.items()
             if insn.delayed and address + 2 in body}
    edges = {}
    for address in addresses:
        if address in owner:
            branch = insns[owner[address]]
            edges[address] = [(target, branch.flow == "call")
                              for target in _after(owner[address], branch, body, address)]
        else:
            edges[address] = [(target, False) for target in _successors(address, insns, body)]
    # The entry, and code that no edge reaches (a jump-table case, a body
    # fragment), start with every register unknown.
    reached = {target for targets in edges.values() for target, _ in targets}
    entering = {address: {} for address in addresses
                if address == func or address not in reached}
    work = list(entering)
    while work:
        address = work.pop()
        out = _transfer(entering[address], insns[address], data)
        for target, call in edges[address]:
            state = _clobber(out) if call else out
            if target not in entering:
                entering[target] = state
            else:
                merged = _meet(entering[target], state)
                if merged == entering[target]:
                    continue
                entering[target] = merged
            work.append(target)
    pairs = []
    for address in addresses:
        insn = insns[address]
        access = insn.access
        if access is None or address not in entering:
            continue
        state = entering[address]
        base = state.get(access.base)
        if base is None or base[1] is None:
            continue
        accessed = (base[0] + access.disp) & sh2.MASK
        if access.indexed:
            index = state.get(0)
            if index is not None:
                accessed = (accessed + index[0]) & sh2.MASK
        name = "gbr" if access.base == "gbr" else f"r{access.base}"
        pairs.append(Pair(func, address, accessed, base[2], base[1], name,
                          access.mode, access.size,
                          access.indexed and state.get(0) is None))
    return pairs


@lru_cache(maxsize=None)
def literal_pairs(layout_id, root=repo.ROOT):
    """Every literal pair of a layout, sorted."""
    layout = repo.layout(layout_id, root)
    data = image_bytes(layout, root)
    pairs = []
    for func, addresses in bodies(layout_id, root).items():
        pairs.extend(function_pairs(func, addresses, data))
    return tuple(sorted(pairs))
