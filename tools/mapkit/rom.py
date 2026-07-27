#!/usr/bin/env python3
# ROM image support: dump registry, calibration-array reads, and measurement
# (Stage 4, section 7 of tools/map-flag-pipeline.md). This is a library rather
# than a script. load_maps.py uses it to characterize the layer in the same run
# that creates nodes, and show.py/ptrscan.py use it for inspection.
#
# Tool boundary: it MEASURES but does not INFER. Range, monotonicity, and contents
# are properties of image bytes and are read identically for maps of any
# semantics. Axis meaning, units, and map semantics are code conclusions supplied
# by traces through the handwritten layer (defs/<rom>.findings.csv and
# <rom>.axes.csv). Inferring meaning from data shape caused two earlier
# pattern-scan errors (P6) and is intentionally absent here.
#
# Monotonicity is different: an ascending array is a kernel requirement, not a
# semantic guess. The kernel scans backward from the highest point to the first
# value <= the current input. An array that violates this rule cannot act as its
# axis regardless of its assigned name.
import csv
import hashlib
import os

HERE = os.path.dirname(os.path.abspath(__file__))
IMAGES = os.path.join(HERE, "..", "..", "rom-images")
REGISTRY = os.path.join(IMAGES, "roms.csv")

# Calibration element size in bytes. Both types are unsigned: all five 2D
# finishers read EXTU.B or EXTU.W for both interpolation operands, and there is
# no EXTS instruction in 0x26740..0x26BC4 (defs/JK08A.notes.md, "2D map element
# encoding"). A signed element must be declared here together with code that
# reads it as signed.
ELEM = {"uint8": 1, "uint16": 2}

# Erased flash: an unprogrammed cell reads as all one bits.
ERASED = {"uint8": 0xFF, "uint16": 0xFFFF}


def addr_int(a):
    """Graph address as a hexadecimal string without 0x, or an integer."""
    return a if isinstance(a, int) else int(str(a), 16)


class Image:
    """Bytes of one dump. File offsets equal addresses because the base is 0x0."""

    def __init__(self, rom, path, data):
        self.rom, self.path, self.data = rom, path, data

    def __len__(self):
        return len(self.data)

    def values(self, addr, n, storagetype):
        """Read n contiguous unsigned big-endian elements."""
        if storagetype not in ELEM:
            raise ValueError(f"undeclared element {storagetype!r}; expected one of {tuple(ELEM)}")
        size, addr = ELEM[storagetype], addr_int(addr)
        end = addr + n * size
        if addr < 0 or end > len(self.data):
            raise ValueError(f"{self.rom}: {addr:#x} + {n} x {size} B exceeds image "
                             f"size {len(self.data):#x} B")
        return [int.from_bytes(self.data[i:i + size], "big")
                for i in range(addr, end, size)]

    def table(self, addr, width, height, storagetype):
        """Read a map by rows: r5 axis (:AXIS_X) rows and r6 axis columns.

        Finisher geometry is cell = table + idxY + width*idxX. idxX indexes the
        r5 axis, and the wrapper supplies the row stride: 0x10 for 16x16 uint8
        and 8 for 8x8 through 0x26040. The row stride is the row length, so the
        number of columns equals the r6-axis length. Every JK08A 2D wrapper has
        equal axis lengths (4x4, 8x8, or 16x16), where this value also equals the
        row count. A nonsquare wrapper is still read from the formula rather than
        from that coincidence.
        """
        if not height:
            return [self.values(addr, width, storagetype)]
        flat = self.values(addr, width * height, storagetype)
        return [flat[i * height:(i + 1) * height] for i in range(width)]

    def scan(self, lo, hi):
        """Find image words whose values fall in [lo, hi].

        Both constant forms are searched. mov.l reads a 32-bit word on a
        four-byte boundary, which is a pool pointer. mov.w reads a 16-bit word
        on a two-byte boundary and can hold calibration addresses such as 0xB33A
        and 0x8FDC. The reference linear backtrack read such constants as 32-bit
        and failed at five catalog sites, so this form is handled separately.

        When a matching 32-bit word also fits in 16 bits, its low half carries
        the same value and is not counted as a separate hit. It is one constant,
        not two.
        """
        out, halves = [], set()
        for off in range(0, len(self.data) - 3, 4):
            v = int.from_bytes(self.data[off:off + 4], "big")
            if lo <= v <= hi:
                out.append({"at": off, "value": v, "kind": "mov.l"})
                if v <= 0xFFFF:
                    halves.add(off + 2)
        if lo <= 0xFFFF:
            for off in range(0, len(self.data) - 1, 2):
                v = int.from_bytes(self.data[off:off + 2], "big")
                if lo <= v <= min(hi, 0xFFFF) and off not in halves:
                    out.append({"at": off, "value": v, "kind": "mov.w"})
        return sorted(out, key=lambda r: r["at"])


def measure(values):
    """Measure the range and contents directly represented by an image array.

    A hash is required where values are absent from the graph. A map can contain
    up to 256 cells; contents remain in the image and identical maps are found by
    hash. Axis values are stored in full on the node and identical axes are
    matched by list comparison, where a hash would duplicate the same fact.
    """
    return {
        "vmin": min(values),
        "vmax": max(values),
        "values_hash": hashlib.sha256(",".join(map(str, values)).encode()).hexdigest()[:16],
    }


def erased(values, storagetype):
    """Return whether every array bit is one, indicating erased flash.

    This is a storage-medium property rather than a semantic inference. NOR flash
    erases to one bits, so an all-0xFF declared array is absent.
    """
    return all(v == ERASED[storagetype] for v in values)


def monotone(values):
    """Return whether an array is non-strictly ascending.

    The kernel scans linearly from the highest point down to the first breakpoint
    <= the current value. This works only for an ascending array. An array that
    violates the rule cannot be the axis regardless of the resolver label.
    """
    return all(a <= b for a, b in zip(values, values[1:]))


def registry(path=REGISTRY):
    """Read the image registry: one dump per row and its optional graph ROM label.

    The registry is machine-readable. Human identification, provenance, part
    number, and confidence are in rom-images/README.md. SHA-256 is declared here
    because dump identification is a run precondition rather than human-only
    reference data.
    """
    if not os.path.exists(path):
        raise ValueError(f"image registry not found: {path}")
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    seen = {}
    for r in rows:
        r["path"] = os.path.join(IMAGES, r["path"])
        if not r["sha256"]:
            raise ValueError(f"{path}: {r['path']} has no sha256; dumps are identified by it")
        if r["rom"]:
            if r["rom"] in seen:
                raise ValueError(f"{path}: label {r['rom']} is assigned to two images")
            seen[r["rom"]] = r
    return rows


def load(rom, path=REGISTRY):
    """Load an image by graph label and verify it by SHA-256.

    Verification is substantive: the census comes from a Ghidra project built
    from one file, while measurement performs a separate disk read. Substitution
    would otherwise yield 227 axes of plausible numbers from the wrong dump,
    indistinguishable from facts in the graph.
    """
    row = next((r for r in registry(path) if r["rom"] == rom), None)
    if row is None:
        raise ValueError(f"{path}: no image with label {rom} in registry")
    if not os.path.exists(row["path"]):
        raise ValueError(f"{row['path']}: file not found although registry declares image {rom}")
    with open(row["path"], "rb") as f:
        data = f.read()
    got = hashlib.sha256(data).hexdigest()
    if got != row["sha256"]:
        raise ValueError(f"{row['path']}: sha256 is {got}, registry declares "
                         f"{row['sha256']}; this is a different dump")
    return Image(rom, row["path"], data)
