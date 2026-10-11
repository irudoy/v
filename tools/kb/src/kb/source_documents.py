"""Immutable in-memory encodings of independent source documents."""

import marshal
import pickle
import tomllib

TOML_LOADS = tomllib.loads


def freeze(document, *, native=False):
    """Encode a successful parse; native TOML dates retain pickle."""
    if native:
        try:
            return marshal.dumps(document, 4)
        except ValueError:
            pass
    return pickle.dumps(document, protocol=pickle.HIGHEST_PROTOCOL)


def thaw(packed):
    """Return separate mutable containers without copying the encoding."""
    if packed[:1] == b"\x80":
        return pickle.loads(packed)
    return marshal.loads(packed)
