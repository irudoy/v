#!/usr/bin/env python3
"""Generate a self-contained interactive ROM atlas."""

from __future__ import annotations

import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import sys


if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.romviz import model


HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = model.ROOT / "tmp" / "romviz" / "rom-atlas.html"
SCRIPTS = ("architecture.js", "app.js")


def _safe_json(value):
    return (
        json.dumps(value, ensure_ascii=True, separators=(",", ":"))
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
    )


def render(atlas):
    template = (HERE / "app.html").read_text(encoding="utf-8")
    css = (HERE / "app.css").read_text(encoding="utf-8")
    javascript = "\n".join(
        (HERE / name).read_text(encoding="utf-8") for name in SCRIPTS
    )
    replacements = {
        "/*__ROMVIZ_CSS__*/": css,
        "/*__ROMVIZ_JS__*/": javascript,
        "__ROMVIZ_DATA__": _safe_json(atlas),
    }
    for marker, content in replacements.items():
        if template.count(marker) != 1:
            raise model.ModelError(f"template marker {marker!r} is not unique")
        template = template.replace(marker, content)
    return template


def write_atlas(manifests, output=DEFAULT_OUTPUT):
    """Render the atlas and replace the output atomically."""
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    atlas = model.build_atlas(manifests)
    document = render(atlas)
    temporary = output.with_name(f".{output.name}.{os.getpid()}.tmp")
    try:
        temporary.write_text(document, encoding="utf-8")
        os.replace(temporary, output)
    finally:
        temporary.unlink(missing_ok=True)
    return output, atlas


def summary(atlas):
    """Return the one-line inventory printed after a build or check."""
    roms = ", ".join(
        f"{rom['id']}={len(rom['objects'])} objects" for rom in atlas["roms"]
    )
    architectures = ", ".join(
        f"{key}={len(value['blocks'])} blocks, {len(value['chains'])} chains"
        for key, value in atlas["architectures"].items()
    )
    return f"{roms}; architecture {architectures or 'none'}"


def _serve(path, port):
    class AtlasHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(path.parent), **kwargs)

        def log_message(self, format, *args):
            print(format % args)

    server = ThreadingHTTPServer(("127.0.0.1", port), AtlasHandler)
    print(f"serving http://127.0.0.1:{port}/{path.name}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Generate a self-contained interactive ROM address-space atlas."
    )
    parser.add_argument(
        "rom",
        nargs="*",
        help="ROM label, manifest path, or all (default: all registered ROMs)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"output HTML path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--serve",
        type=int,
        metavar="PORT",
        help="serve the generated file on 127.0.0.1 until interrupted",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate selected inputs without writing an atlas",
    )
    args = parser.parse_args(argv)
    if args.check and args.serve:
        parser.error("--check and --serve cannot be combined")
    if args.check:
        atlas = model.build_atlas(args.rom)
        output = None
    else:
        output, atlas = write_atlas(args.rom, args.output)
    if args.check:
        print(f"validated ROM atlas inputs ({summary(atlas)})")
    else:
        print(f"wrote {output} ({summary(atlas)})")
    if args.serve:
        _serve(output, args.serve)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
