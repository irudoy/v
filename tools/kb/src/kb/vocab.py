"""Vocabularies of the knowledge model (tools/kb/SPEC.md, sections 5 to 7)."""

import re

LEVELS = ("pattern", "candidate", "code", "silicon")
LEVEL_RANK = {level: rank for rank, level in enumerate(LEVELS)}

# Kinds of L1 meanings and of designed entities, in the order of section 6.
MEANING_KINDS = ("fn", "ram", "reg", "tbl", "axis", "const", "hook", "did", "dtc")
DESIGNED_KINDS = ("stage", "block", "endpoint", "chain", "signal", "field", "feature")
KINDS = MEANING_KINDS + DESIGNED_KINDS
DATUM = ("ram", "reg", "tbl", "axis", "const")
ROM_KINDS = ("fn", "tbl", "axis", "const", "hook", "did", "dtc")

SEMANTIC_NAME = re.compile(r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*")
GENERATED_NAME = re.compile(r"[a-z]+-[a-z]+")
LAYOUT_ID = re.compile(r"[0-9a-z]{2,8}")
ADDRESS = re.compile(r"[0-9a-f]{8}")

# Link types: kinds of the owning meaning and of the `to` end (section 7.5).
ANY = MEANING_KINDS
LINK_TYPES = {
    "writer": (("ram", "reg"), ("fn",)),
    "reader": (("ram", "reg", "tbl", "axis", "const"), ("fn",)),
    "input": (("ram", "reg"), DATUM),
    "copy": (("ram", "reg"), ("ram", "reg")),
    "index": (("tbl", "axis"), ("ram", "reg")),
    "axis": (("tbl",), ("axis",)),
    "lookup": (("ram", "reg"), ("tbl",)),
    "selector": (DATUM + ("fn",), DATUM + ("fn",)),
    "threshold": (DATUM + ("fn",), ("tbl", "ram")),
    "base": (("ram",), ("ram",)),
    "target": (("hook",), ("fn", "tbl", "const")),
    "source": (("did",), ("ram", "reg", "tbl", "const")),
    "monitor": (("dtc",), ("fn",)),
    "depends": (ANY, ANY),
}
RELIES = ("structure", "level", "contract", "scale")
SUPPORTS = ("identity", "homology", "scale", "contract", "role")

# Evidence kinds with the keys they require and the level they ground (7.6).
EVIDENCE_KINDS = {
    "l0": (("at",), "code"),
    "literal-pool": (("at", "to", "value"), "code"),
    "masked-match": (("at", "to", "count", "value"), "code"),
    "function-match": (("at", "to", "count", "value"), "code"),
    "call-ordinal": (("at", "to", "count", "value"), "code"),
    "interp-contract": (("to", "key"), "code"),
    "did-table": (("at", "value"), "code"),
    "byte-identical": (("at", "to", "sha256"), "code"),
    "rom-bytes": (("at", "value"), "code"),
    "unbound-constant": (("value",), None),
    "unverified-site": (("at",), None),
    "l0-context": (("at", "key", "value"), "code"),
    "trace": (("to", "relies"), "code"),
    "indirect": (("at", "mode"), "code"),
    "spec": ((), "code"),
    "arithmetic": (("value",), "code"),
    "test": (("path", "key"), "code"),
    "manual": (("key",), "candidate"),
    "diagnostic": (("key",), "candidate"),
    "registry": ((), "candidate"),
    "vendor": (("key",), "candidate"),
    "hardware": (("key",), "silicon"),
}
EVIDENCE_KEYS = ("kind", "supports", "at", "to", "relies", "count", "value", "sha256",
                 "mode", "path", "key", "note")
# Modes describe retained evidence data, including optional archived producers.
# A mode name does not register executable code or establish grounding.
INDIRECT_MODE = re.compile(r"[a-z][a-z0-9]*(?:[-_][a-z0-9]+)*")

FN_ROLES = ("accessor", "service", "driver", "monitor", "wrapper", "dispatch", "init",
            "handler", "selector", "consumer", "kernel", "finisher")
TBL_ROLES = ("table", "threshold", "dead")
TBL_ACCESS = ("explicit", "implicit-2d", "direct-scalar", "direct-row-major",
              "direct-indexed", "compare")
STORAGE = ("uint8", "int8", "uint16", "int16", "uint32", "int32", "float32")
STATUS_STATES = ("absent", "unresolved")
TARGET_STATUSES = ("supported", "planned", "unsupported")

# Vocabularies of the keys of designed entities (section 7.9).
ENTITY_VOCABULARY = {
    "signal": {
        "priority": ("core", "high", "medium", "research"),
        "coverage": ("fixed", "rotating", "latched", "stock-can", "external", "absent"),
        "basis": ("exact-code", "exact-code+homologous-diagnostic", "measurement-requirement",
                  "passive-can", "patch-design"),
    },
    "field": {
        "origin": ("ecu_ram", "rom_configuration", "runtime_state", "telemetry_state"),
    },
    "stage": {"lane": ("flow", "support")},
    "endpoint": {"direction": ("input", "output", "bidirectional")},
}
STEP_EFFECTS = ("scales", "looks-up", "indexes", "converts", "adds", "multiplies", "selects",
                "compares", "subtracts", "copies", "gates", "limits", "stores", "filters",
                "feeds", "integrates", "schedules", "receives", "overrides", "masks", "drives",
                "detects", "transmits", "learns")
STEP_SIGNS = ("positive", "negative", "none")

# Keys of the feature tables of meanings (section 7.8).
EDITOR_KEYS = ("name", "category", "order", "emit", "format", "fine", "coarse", "mask",
               "static_axis", "static_axis_name", "static_axis_operand", "static_axis_x",
               "static_axis_x_name", "static_axis_y", "static_axis_y_name")
VIEW_KEYS = ("name", "category", "mask", "unit", "scale", "to_raw", "format", "fine", "coarse")
LOGPARAM_KEYS = ("id", "unit", "scale", "static_axis_name")

# The editor and registry spelling of an element type and its kb storage.
STORAGE_ALIASES = {"float": "float32"}


def storage(value):
    """The kb element type of a registry storage type, or None when empty."""
    if not value:
        return None
    return STORAGE_ALIASES.get(value, value)


def level_min(*levels):
    present = [level for level in levels if level]
    return min(present, key=LEVEL_RANK.__getitem__) if present else None
