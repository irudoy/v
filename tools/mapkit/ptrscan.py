#!/usr/bin/env python3
# Find values that may point to an address by scanning the image without Ghidra.
#
# This complements rather than replaces FindTableRefs.java. The latter lists
# analysis-resolved references and can distinguish a reference from a coincident
# value, but sees only defined code. An image scan has no semantic knowledge but
# sees everything, including pools under code not defined as functions by Ghidra
# (JK08A had 38,627 instructions across 494 regions before Stage 0). Use it for
# the first question about an unfamiliar array or a dump without a Ghidra project.
#
# Both constant forms are searched. mov.l reads a 32-bit word on a four-byte
# boundary, the usual pool pointer. mov.w reads a 16-bit word on a two-byte
# boundary and can hold calibration addresses such as 0xB33A and 0x8FDC. The
# reference backtrack treated these as 32-bit constants and failed at five sites.
#
# Context, not encoding, distinguishes a coincidence from a pointer: a one-MiB
# image contains thousands of 16-bit words in many ranges. Results are candidates;
# disassembly at each site decides (tools/ghidra/DumpListing.java).
#
# Usage: uv run python tools/mapkit/ptrscan.py [<rom>] <addr> [<addr_hi>]
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mapkit import rom as romkit          # noqa: E402 - adjacent, uninstalled package


def main():
    args = sys.argv[1:]
    try:
        known = {r["rom"] for r in romkit.registry() if r["rom"]}
    except ValueError as e:
        sys.exit(str(e))
    rom = args.pop(0) if args and args[0] in known else "JK08A"
    if not args:
        sys.exit(f"address required: ptrscan.py [<rom>] <addr> [<addr_hi>]; ROM labels: "
                 f"{', '.join(sorted(known))}")
    lo = int(args[0], 16)
    hi = int(args[1], 16) if len(args) > 1 else lo
    if hi < lo:
        sys.exit(f"empty range: {lo:#x}..{hi:#x}")
    try:
        img = romkit.load(rom)
    except ValueError as e:
        sys.exit(str(e))

    hits = img.scan(lo, hi)
    span = "" if lo == hi else f"..{hi:#07x}"
    print(f"{rom} ({os.path.basename(img.path)}): {lo:#07x}{span} - "
          f"{len(hits)} candidates")
    by_kind = {}
    for h in hits:
        by_kind[h["kind"]] = by_kind.get(h["kind"], 0) + 1
    for kind in ("mov.l", "mov.w"):
        if kind in by_kind:
            print(f"  {kind}: {by_kind[kind]}")
    for h in hits:
        print(f"  {h['at']:#08x}  {h['kind']:<5} -> {h['value']:#07x}")
    if by_kind.get("mov.w"):
        print("16-bit hits are candidates, not references: many image words share "
              "the value. Inspect each site with ghidra/DumpListing.java.")


if __name__ == "__main__":
    main()
