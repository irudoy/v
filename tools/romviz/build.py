#!/usr/bin/env python3
"""Generate a self-contained interactive ROM atlas."""

from __future__ import annotations

import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys


if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.romviz import model


HERE = Path(__file__).resolve().parent
DEFAULT_OUTPUT = model.ROOT / "tmp" / "romviz" / "rom-atlas.html"


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
    javascript = (HERE / "app.js").read_text(encoding="utf-8")
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
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    atlas = model.build_atlas(manifests)
    output.write_text(render(atlas), encoding="utf-8")
    return output, atlas


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
        nargs="+",
        help="ROM label or path to a tools/romviz/roms manifest",
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
    args = parser.parse_args(argv)
    output, atlas = write_atlas(args.rom, args.output)
    summary = ", ".join(
        f"{rom['id']}={len(rom['objects'])} objects" for rom in atlas["roms"]
    )
    print(f"wrote {output} ({summary})")
    if args.serve:
        _serve(output, args.serve)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
