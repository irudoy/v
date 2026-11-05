#!/usr/bin/env python3
"""Control-flow and dataflow check of the JK08A Rolling Launch units.

The check builds the control-flow graph of every function of the Rolling
Launch units: each code-region entry that is not a declared continuation,
and each internal target of a call or tail jump. A delayed transfer and its
slot form one node. A forward pass tracks the value of every register (its
entry value, a set of PC-literal constants, or a saved SR), the stack of
pushed values, and the producers of T. A backward pass computes the
registers that each node reads before it writes them.

``rolling-launch-flow.toml`` declares the convention of every function and
of every stock or Map Switching target: the registers it reads, the
registers whose exit value differs from the entry value, the outputs, and
the mnemonics whose T reaches a consumer by intent. The check requires:

- every return with an empty stack after its slot and the entry PR at the
  RTS, which takes its return address before the slot, and every tail jump
  with an empty stack and the entry PR after its slot; BSR and JSR write
  the continuation to PR before their slot, and PR still holds it after the
  slot, where the callee receives it;
- computed reads and writes equal to the declaration, outputs among the
  writes, and the T of the caller read exactly when the declaration names
  it;
- no register that a callee writes and does not output live after the call;
- every comparison or test feeding a T consumer, and every T consumer fed
  only by comparisons, tests, declared producers, callee T outputs or the
  T of the caller.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
import re
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import map_switching_assembly as common  # noqa: E402


DEFAULT_FLOW = Path(__file__).with_name("rolling-launch-flow.toml")
GENERAL = tuple(f"r{number}" for number in range(15))
SPECIAL = ("macl", "mach", "gbr", "sr")
# r15 is checked by the stack balance and PR by its value at every return.
REGISTERS = GENERAL + SPECIAL + ("t",)
DECLARABLE = frozenset(REGISTERS)
COMPARISONS = frozenset({
    "cmp/eq", "cmp/hs", "cmp/ge", "cmp/hi", "cmp/gt", "cmp/pz", "cmp/pl", "cmp/str", "tst",
})
DELAYED = frozenset({"bra", "bsr", "jsr", "jmp", "rts", "braf", "bsrf"})
MOVES = frozenset({
    "mov", "mov.b", "mov.w", "mov.l", "extu.b", "extu.w", "exts.b", "exts.w", "neg", "not",
    "swap.b", "swap.w", "mova",
})
ARITHMETIC = frozenset({"add", "sub", "and", "or", "xor"})
T_SHIFTS = frozenset({"shll", "shlr", "shal", "shar", "rotl", "rotr", "rotcl", "rotcr", "dt"})
SHIFTS = frozenset({"shll2", "shll8", "shll16", "shlr2", "shlr8", "shlr16"})
MULTIPLIES = frozenset({"mulu.w", "muls.w", "mul.l"})
REGISTER = re.compile(r"r(?:1[0-5]|[0-9])")
NUMBER = re.compile(r"#?-?(?:0x[0-9a-f]+|[0-9]+)")


class FlowError(ValueError):
    """A Rolling Launch unit breaks its control-flow or dataflow contract."""


@dataclass(frozen=True)
class Convention:
    name: str
    reads: frozenset
    writes: frozenset
    outputs: frozenset
    t_producers: frozenset = frozenset()
    external: bool = False


@dataclass(frozen=True)
class Step:
    """One instruction effect: registers read and written, and its copy form."""

    reads: frozenset
    writes: frozenset
    copy: tuple | None = None  # (source, destination), a stack slot as "push" or "pop"
    t_producer: bool = False
    mnemonic: str = ""
    literal: int | None = None  # the value of a PC-relative long load
    address: int = 0
    immediate: int | None = None  # the immediate of a logic operation on r0


@dataclass
class Node:
    address: int
    where: str
    text: str
    steps: tuple
    kind: str  # "op", "branch", "jump", "call", "tail", "exit"
    target: object = None  # label address of bt, bf, bra and bsr; register of jsr and jmp
    successors: tuple = ()
    mnemonic: str = ""
    slot: int | None = None  # index of the first delay-slot step


def _operands(text):
    head, _, rest = text.partition(" ")
    parts, depth, current = [], 0, ""
    for char in rest.replace(" ", ""):
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        if char == "," and not depth:
            parts.append(current)
            current = ""
        else:
            current += char
    if current:
        parts.append(current)
    return head, parts


def _memory_reads(operand):
    """Registers that address a memory operand, and the register it updates."""
    if operand.startswith("@(") and operand.endswith(",pc)"):
        return set(), None
    names = set(REGISTER.findall(operand))
    if "gbr" in operand:
        names.add("gbr")
    update = None
    if operand.startswith("@-") or (operand.startswith("@r") and operand.endswith("+")):
        update = REGISTER.search(operand).group(0)
    return names, update


def _source(operand):
    if NUMBER.fullmatch(operand) or not operand:
        return set(), None
    if operand.startswith("@"):
        return _memory_reads(operand)
    if operand in SPECIAL or REGISTER.fullmatch(operand) or operand == "pr":
        return {operand}, None
    return set(), None


def semantics(text):
    """The steps of one SH-2E instruction of the audited subset."""
    mnemonic, operands = _operands(text.lower())
    one = operands[0] if operands else ""
    two = operands[1] if len(operands) > 1 else ""
    if any("r15" in operand for operand in operands) and not (
            (mnemonic in ("mov.l", "sts.l") and two == "@-r15")
            or (mnemonic in ("mov.l", "lds.l") and one == "@r15+")):
        raise FlowError(f"{text}: stack access other than a long push or pop")
    if mnemonic in ("nop",):
        return mnemonic, (Step(frozenset(), frozenset()),)
    if mnemonic in ("bt", "bf"):
        return mnemonic, (Step(frozenset({"t"}), frozenset()),)
    if mnemonic in ("bra", "rts"):
        return mnemonic, (Step(frozenset({"pr"} if mnemonic == "rts" else ()), frozenset()),)
    if mnemonic in ("bsr", "jsr", "jmp"):
        reads = frozenset(REGISTER.findall(one)) if mnemonic != "bsr" else frozenset()
        return mnemonic, (Step(reads, frozenset()),)
    if mnemonic == "rte":
        raise FlowError(f"{text}: RTE is outside the Rolling Launch subset")
    if mnemonic in ("clrt", "sett"):
        return mnemonic, (Step(frozenset(), frozenset({"t"}), t_producer=True),)
    if mnemonic == "movt":
        return mnemonic, (Step(frozenset({"t"}), frozenset({one})),)
    if mnemonic in ("sts.l", "stc.l"):
        if two != "@-r15":
            raise FlowError(f"{text}: only a push of a special register is supported")
        source = one if one != "sr" else "sr"
        return mnemonic, (Step(frozenset({source}), frozenset(), copy=(source, "push")),)
    if mnemonic in ("lds.l", "ldc.l"):
        if one != "@r15+":
            raise FlowError(f"{text}: only a pop of a special register is supported")
        return mnemonic, (Step(frozenset(), frozenset({two}), copy=("pop", two)),)
    if mnemonic in ("sts", "stc"):
        reads = {one} | ({"t"} if one == "sr" else set())
        return mnemonic, (Step(frozenset(reads), frozenset({two}),
                               copy=(one, two) if one != "sr" else None),)
    if mnemonic in ("lds", "ldc"):
        writes = {two} | ({"t"} if two == "sr" else set())
        return mnemonic, (Step(frozenset({one}), frozenset(writes),
                               copy=(one, two) if two != "sr" else None,
                               t_producer=two == "sr"),)
    if mnemonic in COMPARISONS:
        reads = set()
        for operand in operands:
            reads |= _source(operand)[0]
        return mnemonic, (Step(frozenset(reads), frozenset({"t"}), t_producer=True),)
    if mnemonic in T_SHIFTS:
        reads = {one} | ({"t"} if mnemonic in ("rotcl", "rotcr") else set())
        return mnemonic, (Step(frozenset(reads), frozenset({one, "t"}), t_producer=True),)
    if mnemonic in SHIFTS:
        return mnemonic, (Step(frozenset({one}), frozenset({one})),)
    if mnemonic in MULTIPLIES:
        return mnemonic, (Step(frozenset({one, two}), frozenset({"macl"})),)
    if mnemonic in ARITHMETIC:
        reads, _update = _source(one)
        return mnemonic, (Step(frozenset(reads | {two}), frozenset({two})),)
    if mnemonic in MOVES:
        if two == "@-r15":
            if mnemonic != "mov.l":
                raise FlowError(f"{text}: only a long push is supported")
            return mnemonic, (Step(frozenset({one}), frozenset(), copy=(one, "push")),)
        if one == "@r15+":
            if mnemonic != "mov.l":
                raise FlowError(f"{text}: only a long pop is supported")
            return mnemonic, (Step(frozenset(), frozenset({two}), copy=("pop", two)),)
        if "r15" in one or "r15" in two:
            raise FlowError(f"{text}: stack access other than a push or pop")
        reads, update = _source(one)
        writes = set()
        if two.startswith("@"):
            target_reads, target_update = _memory_reads(two)
            reads |= target_reads
            update = update or target_update
        else:
            writes.add(two)
        if update:
            reads.add(update)
            writes.add(update)
        copy = (one, two) if mnemonic == "mov" and REGISTER.fullmatch(one) else None
        return mnemonic, (Step(frozenset(reads), frozenset(writes), copy=copy),)
    raise FlowError(f"{text}: {mnemonic} has no flow semantics")


# Values of the forward pass: ("entry", register), ("const", frozenset),
# ("srsave", sr value, T producers), ("continuation", call address) for the
# PR that a call writes before its slot, or None for an unknown value.
def _join_value(left, right):
    if left == right:
        return left
    if left is None or right is None:
        return None
    if left[0] == right[0] == "const":
        return ("const", left[1] | right[1])
    if left[0] == right[0] == "srsave" and left[1] == right[1]:
        return ("srsave", left[1], left[2] | right[2])
    return None


@dataclass(frozen=True)
class State:
    regs: tuple  # values in REGISTERS order with "t" replaced by T producers; then pr
    stack: tuple

    def get(self, name):
        return self.regs[_INDEX[name]]

    def put(self, **values):
        regs = list(self.regs)
        for name, value in values.items():
            regs[_INDEX[name]] = value
        return State(tuple(regs), self.stack)


_NAMES = REGISTERS + ("pr",)
_INDEX = {name: index for index, name in enumerate(_NAMES)}


def _entry_state():
    regs = [("entry", name) for name in _NAMES]
    regs[_INDEX["t"]] = frozenset({"entry"})
    return State(tuple(regs), ())


def _join(left, right, where):
    if len(left.stack) != len(right.stack):
        raise FlowError(f"{where}: paths join with different stack depths")
    regs = []
    for name, a, b in zip(_NAMES, left.regs, right.regs):
        regs.append(a | b if name == "t" else _join_value(a, b))
    return State(tuple(regs), tuple(_join_value(a, b) for a, b in zip(left.stack, right.stack)))


class Program:
    """The instructions, labels and literals of every Rolling Launch unit."""

    def __init__(self, parsed_by_unit):
        self.statements, self.labels, self.literals, self.where = {}, {}, {}, {}
        for unit, parsed in parsed_by_unit.items():
            for statement in parsed.statements:
                self.statements[statement.address] = statement
                self.where[statement.address] = f"{Path(parsed.path).name}:{statement.line_number}"
            for label, address in parsed.labels.items():
                if label in self.labels and self.labels[label] != address:
                    raise FlowError(f"label {label} names two addresses")
                self.labels[label] = address
            for label, value in common._long_literals(parsed).items():
                self.literals[parsed.labels[label]] = value
        self.label_addresses = set(self.labels.values())
        self.nodes = {}
        self.slots = set()
        for address in sorted(self.statements):
            statement = self.statements[address]
            if statement.kind != "instruction" or address in self.slots:
                continue
            self.nodes[address] = self._node(statement)

    def instruction(self, address, why):
        statement = self.statements.get(address)
        if statement is None or statement.kind != "instruction":
            raise FlowError(f"{why} reaches no instruction at {address:#010x}")
        return statement

    def _steps(self, statement):
        text = statement.text.lower()
        mnemonic, steps = semantics(text)
        _head, operands = _operands(text)
        literal = None
        if mnemonic == "mov.l" and operands[0].startswith("@(") and operands[0].endswith(",pc)"):
            literal = self.literals.get(self.labels.get(operands[0][2:-4]))
        immediate = None
        if mnemonic in ("or", "and", "xor") and operands[-1] == "r0" and NUMBER.fullmatch(operands[0]):
            immediate = int(operands[0].lstrip("#"), 0)
        return mnemonic, tuple(replace(step, mnemonic=mnemonic, literal=literal,
                                       address=statement.address, immediate=immediate)
                               for step in steps)

    def _node(self, statement):
        text = statement.text.lower()
        where = self.where[statement.address]
        mnemonic, steps = self._steps(statement)
        _head, operands = _operands(text)
        node = Node(statement.address, where, text, steps, "op", mnemonic=mnemonic)
        if mnemonic in DELAYED:
            slot = self.instruction(statement.address + 2, f"{where}: delay slot")
            if slot.address in self.label_addresses:
                raise FlowError(f"{where}: a label names the delay slot")
            slot_mnemonic, slot_steps = self._steps(slot)
            if slot_mnemonic in DELAYED or slot_mnemonic in ("bt", "bf"):
                raise FlowError(f"{where}: a transfer sits in the delay slot")
            self.slots.add(slot.address)
            node.steps = steps + slot_steps
            node.slot = len(steps)
        if mnemonic in ("bt", "bf", "bra", "bsr"):
            label = operands[0]
            if label in self.labels:
                node.target = self.labels[label]
            elif (mnemonic == "bsr" and NUMBER.fullmatch(label)
                  and int(label, 0) in self.label_addresses):
                # Each unit assembles alone, so a call into another unit
                # names the address of its entry label.
                node.target = int(label, 0)
            else:
                raise FlowError(f"{where}: {label} is no label")
        follow = statement.address + 2
        if mnemonic in ("bt", "bf"):
            node.kind, node.successors = "branch", (follow, node.target)
        elif mnemonic == "bra":
            node.kind, node.successors = "jump", (node.target,)
        elif mnemonic in ("bsr", "jsr"):
            node.kind, node.successors = "call", (follow + 2,)
            node.target = node.target if mnemonic == "bsr" else operands[0][1:]
        elif mnemonic == "jmp":
            node.kind, node.target = "tail", operands[0][1:]
        elif mnemonic == "rts":
            node.kind = "exit"
        else:
            node.successors = (follow,)
        return node


def _apply_step(step, state, node):
    regs = {}
    if step.copy is not None:
        source, destination = step.copy
        if destination == "push":
            value = state.get(source) if source != "t" else None
            return State(state.regs, state.stack + (value,))
        if source == "pop":
            if not state.stack:
                raise FlowError(f"{node.where}: pop from an empty stack")
            return State(state.regs, state.stack[:-1]).put(**{destination: state.stack[-1]})
        if destination in _INDEX and source in _INDEX:
            return state.put(**{destination: state.get(source)})
    for name in step.writes:
        if name == "t":
            continue
        regs[name] = None
    if (step.mnemonic in ("or", "and", "xor") and step.immediate is not None
            and isinstance(state.get("r0"), tuple) and state.get("r0")[0] == "srsave"):
        saved = state.get("r0")
        keeps = (step.immediate & 1) == (1 if step.mnemonic == "and" else 0)
        regs["r0"] = ("srsave", None, saved[2]) if keeps else None
    if step.mnemonic == "stc" and "sr" in step.reads:
        destination = next(iter(step.writes))
        regs[destination] = ("srsave", state.get("sr"), state.get("t"))
    if step.t_producer:
        regs["t"] = frozenset({("op", step.address, step.mnemonic)})
    if step.mnemonic == "ldc" and "sr" in step.writes:
        source = next(iter(step.reads))
        value = state.get(source)
        if value is not None and value[0] == "srsave":
            regs["sr"], regs["t"] = value[1], value[2]
        else:
            regs["sr"] = None
    if step.literal is not None:
        destination = next(iter(step.writes))
        regs[destination] = ("const", frozenset({step.literal}))
    return state.put(**regs)


class Analysis:
    def __init__(self, program, conventions, continuations):
        self.program = program
        self.conventions = conventions
        self.continuations = continuations
        self.summaries = {}
        self.functions = {}
        self.active = set()

    def targets(self, node, state):
        if isinstance(node.target, int):
            return (node.target,)
        value = state.get(node.target)
        if value is None or value[0] != "const":
            raise FlowError(f"{node.where}: {node.text} has no PC-literal target")
        return tuple(sorted(value[1]))

    def convention(self, address, where):
        """The computed convention of an internal callee, or the declared one of an external."""
        label = self.name(address)
        if address in self.continuations:
            raise FlowError(f"{where}: calls the continuation {label}")
        if address in self.program.nodes:
            return self.summary(address)
        if address not in self.conventions:
            raise FlowError(f"{where}: {label} has no declared convention")
        return self.conventions[address]

    def name(self, address):
        names = sorted(label for label, value in self.program.labels.items() if value == address)
        if address in self.conventions:
            return self.conventions[address].name
        return names[0] if names else f"{address:#010x}"

    def summary(self, entry):
        if entry in self.summaries:
            return self.summaries[entry]
        if entry in self.active:
            raise FlowError(f"{self.name(entry)} reaches itself")
        self.active.add(entry)
        function = self._forward(entry)
        self.functions[entry] = function
        self.summaries[entry] = function["computed"]
        self.active.discard(entry)
        return function["computed"]

    def _call_effect(self, node, state, targets, conventions):
        writes = frozenset().union(*(item.writes for item in conventions))
        regs = {name: None for name in writes if name != "t"}
        regs["pr"] = None
        if "t" in writes:
            regs["t"] = frozenset({("call", node.address, targets)})
        return state.put(**regs)

    def _transfer(self, node, state):
        """The states of one node, its call or tail targets, and their conventions.

        Return the state at the transfer, after the node, and after its call.
        A delayed branch performs its register transfer before its slot and
        branches after it: JSR and JMP take their target, and RTS its return
        address from PR, before the slot, and BSR and JSR write the
        continuation to PR before the slot. The callee receives PR after the
        slot and returns to it, so the slot of a call keeps the continuation.
        """
        targets = self.targets(node, state) if node.kind in ("call", "tail") else ()
        continuation = ("continuation", node.address)
        control = None
        for position, step in enumerate(node.steps):
            if position == node.slot:
                control = state
                if node.kind == "call":
                    state = state.put(pr=continuation)
            state = _apply_step(step, state, node)
        control = state if control is None else control
        if node.kind == "call" and state.get("pr") != continuation:
            raise FlowError(f"{node.where}: the slot of {node.text} replaces the "
                            "continuation in PR")
        conventions = [self.convention(target, node.where) for target in targets]
        after = (self._call_effect(node, state, targets, conventions)
                 if node.kind == "call" else state)
        return control, state, after, targets, conventions

    def _forward(self, entry):
        program = self.program
        states = {entry: _entry_state()}
        work = [entry]
        while work:
            address = work.pop()
            node = program.nodes.get(address)
            if node is None:
                raise FlowError(f"{self.name(entry)} reaches no instruction at {address:#010x}")
            *_states, state, _targets, _conventions = self._transfer(node, states[address])
            if node.kind in ("exit", "tail"):
                continue
            for successor in node.successors:
                if successor in program.slots:
                    raise FlowError(f"{node.where}: a path enters a delay slot")
                previous = states.get(successor)
                merged = state if previous is None else _join(previous, state, node.where)
                if merged != previous:
                    states[successor] = merged
                    work.append(successor)
        # The events of the function come from the fixed point.
        exits, tails, calls, consumers = [], [], [], []
        for address in sorted(states):
            node = program.nodes[address]
            control, before, _after, targets, conventions = self._transfer(node, states[address])
            if node.kind == "branch":
                consumers.append((node, states[address].get("t"), "branch"))
            if node.kind == "exit":
                exits.append((node, before, control))
            for target, convention in zip(targets, conventions):
                group = calls if node.kind == "call" else tails
                group.append((node, before, target, convention))
                if "t" in convention.reads:
                    consumers.append((node, before.get("t"),
                                      f"{node.kind} of {convention.name}"))
        computed = self._computed(entry, exits, tails)
        return dict(entry=entry, states=states, body=set(states), exits=exits, tails=tails,
                    calls=calls, consumers=consumers, computed=computed)

    def _computed(self, entry, exits, tails):
        """The convention that the forward pass computes, with declared reads and outputs."""
        name = self.name(entry)
        writes = set()
        # RTS returns to PR at the transfer; a tail callee returns to PR after
        # the slot of JMP.
        returns = [(node, state, control, frozenset()) for node, state, control in exits]
        returns += [(node, state, state, convention.writes)
                    for node, state, _target, convention in tails]
        for node, state, control, callee_writes in returns:
            if state.stack:
                raise FlowError(f"{node.where}: {name} leaves {len(state.stack)} stack words")
            if control.get("pr") != ("entry", "pr"):
                raise FlowError(f"{node.where}: {name} returns without its entry PR")
            for register in REGISTERS:
                value = state.get(register)
                if register == "t":
                    if value != frozenset({"entry"}):
                        writes.add("t")
                elif value != ("entry", register):
                    writes.add(register)
            writes |= callee_writes
        declared = self.conventions.get(entry)
        if declared is None:
            raise FlowError(f"{name} has no declared convention")
        return Convention(declared.name, declared.reads, frozenset(writes), declared.outputs,
                          declared.t_producers)

    def liveness(self, entry):
        """Registers live before every node, from the declared outputs at each exit."""
        function = self.functions[entry]
        convention = self.conventions[entry]
        states = function["states"]
        live = {address: frozenset() for address in function["body"]}
        changed = True
        while changed:
            changed = False
            for address in sorted(function["body"], reverse=True):
                node = self.program.nodes[address]
                state = states[address]
                if node.kind == "exit":
                    after = set(convention.outputs) | {"pr"}
                elif node.kind == "tail":
                    after = {"pr"}
                    for target in self.targets(node, state):
                        callee = self.conventions[target]
                        after |= callee.reads | (convention.outputs - callee.writes)
                else:
                    after = set()
                    for successor in node.successors:
                        after |= live.get(successor, frozenset())
                current = self._node_live(node, state, after)
                if current != live[address]:
                    live[address] = current
                    changed = True
        return live

    def _node_live(self, node, state, after):
        live = set(after)
        if node.kind == "call":
            targets = self.targets(node, state)
            conventions = [self.conventions[target] for target in targets]
            kill = frozenset.intersection(*(item.outputs for item in conventions)) | {"pr"}
            reads = frozenset().union(*(item.reads for item in conventions))
            live = (live - kill) | reads
        depth, slots = len(state.stack), []
        for step in node.steps:
            if step.copy and step.copy[1] == "push":
                slots.append(f"s{depth}")
                depth += 1
            elif step.copy and step.copy[0] == "pop":
                depth -= 1
                slots.append(f"s{depth}")
            else:
                slots.append(None)
        for step, slot in zip(reversed(node.steps), reversed(slots)):
            if step.copy is not None:
                source, destination = step.copy
                destination = slot if destination == "push" else destination
                source = slot if source == "pop" else source
                if destination in live:
                    live.discard(destination)
                    live.add(source)
                continue
            live = (live - step.writes) | step.reads
        return frozenset(live)


def load_declarations(path=DEFAULT_FLOW, text=None):
    raw = tomllib.loads(text) if text is not None else tomllib.loads(path.read_text(encoding="utf-8"))
    if raw.get("schema_version") != 1:
        raise FlowError("flow declarations need schema_version = 1")
    functions, externals = [], []
    for item in raw.get("function", ()):
        functions.append(_convention(item, item["label"]))
    for item in raw.get("external", ()):
        externals.append((item["address"], _convention(item, item["name"], external=True)))
    continuations = tuple(item["label"] for item in raw.get("continuation", ()))
    return functions, externals, continuations


def _convention(item, name, external=False):
    allowed = {"label", "name", "address", "reads", "writes", "outputs", "t_producers"}
    if set(item) - allowed:
        raise FlowError(f"{name}: unknown declaration keys {sorted(set(item) - allowed)}")
    fields = {}
    for key in ("reads", "writes", "outputs"):
        values = item.get(key, [])
        if len(set(values)) != len(values) or not set(values) <= DECLARABLE:
            raise FlowError(f"{name}: {key} names an unknown or repeated register")
        fields[key] = frozenset(values)
    if not fields["outputs"] <= fields["writes"]:
        raise FlowError(f"{name}: an output is not among the writes")
    producers = frozenset(item.get("t_producers", []))
    if not producers <= T_SHIFTS | {"ldc", "clrt", "sett"}:
        raise FlowError(f"{name}: t_producers names a comparison or an unknown mnemonic")
    return Convention(name, fields["reads"], fields["writes"], fields["outputs"], producers,
                      external)


def _permitted(producer, convention, conventions):
    if producer == "entry":
        return "t" in convention.reads
    kind = producer[0]
    if kind == "op":
        return producer[2] in COMPARISONS or producer[2] in convention.t_producers
    return all("t" in conventions[target].outputs for target in producer[2])


def validate_flow(parsed_by_unit, entry_labels, declarations=None):
    """Check every function of the Rolling Launch units against its convention."""
    functions, externals, continuation_labels = declarations or load_declarations()
    program = Program(parsed_by_unit)
    conventions = {}
    for convention in functions:
        if convention.name not in program.labels:
            raise FlowError(f"declared function {convention.name} is no label")
        conventions[program.labels[convention.name]] = convention
    for address, convention in externals:
        if address in program.nodes:
            raise FlowError(f"external {convention.name} lies in a Rolling Launch unit")
        conventions[address] = convention
    continuations = set()
    for label in continuation_labels:
        if label not in program.labels:
            raise FlowError(f"continuation {label} is no label")
        continuations.add(program.labels[label])
    analysis = Analysis(program, conventions, continuations)
    pending = [program.labels[label] for label in entry_labels
               if program.labels[label] not in continuations]
    seen = set()
    while pending:
        entry = pending.pop()
        if entry in seen:
            continue
        seen.add(entry)
        analysis.summary(entry)
        function = analysis.functions[entry]
        for node, _state, target, _convention in function["calls"] + function["tails"]:
            if target in program.nodes and target not in seen:
                pending.append(target)
    reached = seen | {target for entry in seen for item in
                      analysis.functions[entry]["calls"] + analysis.functions[entry]["tails"]
                      for target in [item[2]]}
    unused = sorted(conventions[address].name for address in conventions
                    if address not in reached)
    if unused:
        raise FlowError(f"declared conventions reach no call or entry: {', '.join(unused)}")
    computed = {entry: analysis.summaries[entry] for entry in seen}
    errors = []
    for entry in sorted(seen):
        errors.extend(_check_function(analysis, entry, computed))
    if errors:
        raise FlowError("\n".join(errors))
    return {analysis.name(entry): computed[entry] for entry in sorted(seen)}


def _check_function(analysis, entry, computed):
    """Every violation of one function, in source order of its checks."""
    errors = []
    program = analysis.program
    function = analysis.functions[entry]
    convention = analysis.conventions[entry]
    name = convention.name
    live = analysis.liveness(entry)
    # A callee writes no register that its caller reads afterwards.
    for node, state, target, callee in function["calls"]:
        after = set()
        for successor in node.successors:
            after |= live.get(successor, frozenset())
        actual = computed.get(target, callee)
        clobbered = sorted((after & (actual.writes - actual.outputs)) - {"t", "pr"})
        if clobbered:
            errors.append(f"{node.where}: {name} reads {', '.join(clobbered)} after "
                          f"{actual.name} writes it")
    # The T of every consumer comes from a comparison or a declared producer.
    fed = set()
    for node, producers, consumer in _t_consumers(analysis, function, convention):
        for producer in sorted(producers, key=repr):
            if not _permitted(producer, convention, analysis.conventions):
                source = ("the T of the caller" if producer == "entry" else
                          f"T of {producer[2] if producer[0] == 'op' else 'a call'} at "
                          f"{program.where[producer[1]]}")
                errors.append(f"{node.where}: {source} reaches the {consumer} of {name}")
            fed.add(producer)
    for address in sorted(function["body"]):
        node = program.nodes[address]
        for step in node.steps:
            if step.mnemonic in COMPARISONS and ("op", step.address, step.mnemonic) not in fed:
                errors.append(f"{program.where[step.address]}: the T of {step.mnemonic} "
                              f"reaches no consumer in {name}")
    for mnemonic in sorted(convention.t_producers):
        if not any(item != "entry" and item[0] == "op" and item[2] == mnemonic for item in fed):
            errors.append(f"{name}: declared T producer {mnemonic} feeds no consumer")
    if "t" in convention.reads and "entry" not in fed:
        errors.append(f"{name}: declares a T input that reaches no consumer")
    # The computed convention equals the declaration.
    reads = live[entry] & (frozenset(GENERAL) | {"macl", "mach", "gbr"})
    declared_reads = convention.reads - {"t", "sr"}
    if reads != declared_reads:
        errors.append(f"{name}: reads {_names(reads)}, declared {_names(declared_reads)}")
    actual = computed[entry].writes
    if actual != convention.writes:
        errors.append(f"{name}: writes {_names(actual)}, declared {_names(convention.writes)}")
    return errors


def _t_consumers(analysis, function, convention):
    for item in function["consumers"]:
        yield item
    for node, state, _control in function["exits"]:
        if "t" in convention.outputs:
            yield node, state.get("t"), "T output"
    for node, state, target, callee in function["tails"]:
        if "t" in convention.outputs and "t" not in callee.writes:
            yield node, state.get("t"), "T output"


def _names(registers):
    order = {name: index for index, name in enumerate(REGISTERS)}
    return "[" + ", ".join(sorted(registers, key=order.get)) + "]"
