"""The grammar and role vocabulary of evidence tokens in legacy registries.

This module owns token parsing. `kb.adapters.ledgers.dependency` owns the
dependency-role mapping shared by legacy import and ledger projection.
Canonical links and evidence follow tools/kb/SPEC.md, sections 7.5 and 7.6.

A token is `role:value`. A dependency role names a target address with an
optional offset and the property of the target the claim rests on,
`role:<address>[+<offset>]@<property>`; a terminal role carries a value; a
process role records review history and maps to nothing.
"""

from dataclasses import dataclass
import keyword
import re

from kb import evidence_ref

DEPENDENCY = ("consumer", "writes", "indexed_by", "selector", "threshold", "from_map",
              "homolog", "trace", "base", "match")
TYPED_TERMINAL = ("indirect_base", "test")
TERMINAL = ("rom_const", "spec", "registry", "site") + TYPED_TERMINAL
PROCESS = ("wave", "arg")
ROLES = DEPENDENCY + TERMINAL + PROCESS

# The legacy target property of a dependency token and the kb `relies` value.
RELIES = {
    "structural": "structure",
    "confidence": "level",
    "contract_conf": "contract",
    "scale_conf": "scale",
}
# The evidence column of a registry row and the claim its tokens support.
SUPPORTS = {
    "evidence": "identity",
    "contract_evidence": "contract",
    "scale_evidence": "scale",
}
# Kinds a dependency target may take, in resolution order: a symbol of the
# first kind that the registries place at the address wins, and an address
# without one takes the first kind its address space admits.
TARGET_KINDS = {
    "consumer": ("fn", "ram", "reg"),
    "writes": ("ram", "reg", "fn"),
    "indexed_by": ("ram", "reg", "axis", "fn", "tbl", "const"),
    "selector": ("ram", "reg", "fn", "tbl", "const"),
    "threshold": ("ram", "reg", "tbl"),
    "from_map": ("tbl", "axis"),
    "homolog": ("fn",),
    "trace": ("fn",),
    "base": ("ram", "reg"),
    "match": ("tbl", "axis"),
}

REFERENCE = re.compile(r"([0-9a-f]{8})(?:\+(0x[0-9a-f]+|\d+))?")
ADDRESS = re.compile(r"[0-9a-f]{8}")
INDIRECT_BASE = re.compile(r"([0-9a-f]{8})\+(0x[0-9a-f]+|[0-9]+)")
TEST = re.compile(r"((?:[A-Za-z0-9_.-]+/)*[A-Za-z0-9_.-]+\.py)#([A-Za-z_][A-Za-z0-9_]*)")
SCALAR = r"(?:-?\d+|0x[0-9a-f]+|[0-9a-f]+)"
ROM_BINDING = re.compile(
    rf"([0-9a-f]{{8}})=({SCALAR}|\d+(?:\*\d+)+|\[{SCALAR}(?:,{SCALAR})*\])"
)
EQUATION = re.compile(r"[-+*/^().0-9 ]+=[-+.0-9]+")


class TokenError(ValueError):
    pass


@dataclass(frozen=True)
class Token:
    """A parsed token; `value` of a dependency is its reference without the
    target property, as the legacy parser reads it."""

    role: str
    value: str
    address: int | None = None
    offset: int | None = None
    relies: str | None = None
    text: str = ""


def _typed_value(role, value, text):
    """Validate the explicit terminal grammar without dependency addressing."""
    if role == "indirect_base":
        found = INDIRECT_BASE.fullmatch(value)
        if found is None:
            raise TokenError(f"token {text!r}: expected indirect_base:<address>+<offset>")
        return found.group(1), int(found.group(2), 16 if found.group(2).startswith("0x") else 10)
    error = f"token {text!r}: expected test:<safe-relative-python-path>#<function>"
    try:
        archive = evidence_ref.parse(value)
    except ValueError as cause:
        raise TokenError(error) from cause
    locator = f"{archive.path}#{archive.fragment or ''}" if archive is not None else value
    found = TEST.fullmatch(locator)
    if (found is None or any(part in (".", "..") for part in found.group(1).split("/"))
            or keyword.iskeyword(found.group(2))):
        raise TokenError(error)
    return value.rpartition("#")[0], found.group(2)


def parse(text):
    """The tokens of one evidence cell, in cell order."""
    tokens = []
    seen = set()
    for raw in text.split(";"):
        raw = raw.strip()
        if not raw:
            continue
        role, sep, value = raw.partition(":")
        value = value.strip()
        if not sep or role not in ROLES:
            raise TokenError(f"token {raw!r}: role outside {', '.join(ROLES)}")
        if not value:
            raise TokenError(f"token {raw!r}: empty value")
        if role in DEPENDENCY:
            reference, at, prop = value.rpartition("@")
            match = REFERENCE.fullmatch(reference) if at else None
            if match is None or prop not in RELIES:
                raise TokenError(
                    f"token {raw!r}: expected {role}:<address>[+<offset>]@<property>"
                )
            if role == "from_map" and prop != "structural":
                raise TokenError(f"token {raw!r}: from_map rests on structure")
            offset = match.group(2)
            token = Token(role, reference, int(match.group(1), 16),
                          int(offset, 0) if offset else None, RELIES[prop],
                          f"{role}:{value}")
        else:
            if "@" in value:
                raise TokenError(f"token {raw!r}: a {role} token has no target property")
            if role in TYPED_TERMINAL:
                _typed_value(role, value, raw)
            token = Token(role, value, text=f"{role}:{value}")
        if token in seen:
            raise TokenError(f"token {raw!r}: duplicate")
        seen.add(token)
        tokens.append(token)
    return tokens


def canonical(text):
    """One evidence cell, ordered lexically by complete token text.

    The order does not group or discard claims. Values, offsets, target
    properties, and process tokens remain exactly those that `parse` reads.
    """
    return "; ".join(sorted(token.text for token in parse(text)))


def evidence(token, layout, manual_prefixes):
    """The evidence item of a terminal token, or None for a process token.

    Dependency tokens become links or `trace` evidence in the adapters, which
    know the kinds of both ends.
    """
    role, value = token.role, token.value
    if role in PROCESS:
        return None
    if role == "indirect_base":
        site, offset = _typed_value(role, value, token.text)
        return {"kind": "indirect", "at": f"{layout}:{site}", "mode": "base", "value": offset}
    if role == "test":
        path, key = _typed_value(role, value, token.text)
        return {"kind": "test", "path": path, "key": key}
    if role == "site":
        if not ADDRESS.fullmatch(value):
            raise TokenError(f"token {token.text!r}: a site is an address")
        return {"kind": "l0", "at": f"{layout}:{value}"}
    if role == "rom_const":
        match = ROM_BINDING.fullmatch(value)
        if match:
            return {"kind": "rom-bytes", "at": f"{layout}:{match.group(1)}",
                    "value": match.group(2)}
        if ADDRESS.fullmatch(value):
            return {"kind": "rom-bytes", "at": f"{layout}:{value}"}
        return {"kind": "rom-bytes", "value": value}
    if role == "spec":
        if value.startswith("hardware-results:"):
            return {"kind": "hardware", "key": value.removeprefix("hardware-results:")}
        if EQUATION.fullmatch(value):
            return {"kind": "arithmetic", "value": value}
        if value.startswith(tuple(manual_prefixes)):
            return {"kind": "manual", "key": value}
        return {"kind": "spec", "key": value}
    if role == "registry":
        if "/" in value and " " not in value and "|" not in value:
            return {"kind": "registry", "path": value}
        return {"kind": "registry", "value": value}
    raise TokenError(f"token {token.text!r}: not a terminal token")
