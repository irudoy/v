"""JK08A ledger serialization (tools/kb/SPEC.md, section 20.2).

`uv run python -m kb.ledger_projection --normalize [--dry-run]` prepares the
canonical token order before conversion. It writes only after comparing all
model facts with those compiled from the prepared CSV overlay.
"""

import argparse
import csv
import io
import sys

from kb import compile, convert, lock, repo, store, tokens
from kb.adapters import ledgers
from kb.repo import KbError


def normalize(text):
    """A CSV with only evidence cells changed to canonical token order."""
    source = csv.DictReader(io.StringIO(text))
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, source.fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in source:
        for column in tokens.SUPPORTS:
            if column in row:
                row[column] = tokens.canonical(row[column])
        writer.writerow(row)
    return output.getvalue()


def normalization(root=repo.ROOT):
    """Prepared files; refuse a normalization that changes any model fact."""
    changes = {}
    for path in ledgers.PATHS.values():
        text = (root / path).read_text(encoding="utf-8")
        prepared = normalize(text)
        if prepared != text:
            changes[path] = prepared
    if changes:
        before = compile.build(root)
        after = compile.build(root, changes)
        different = convert.differences(convert.dump(before), convert.dump(after))
        if different:
            raise KbError("normalization changes model facts; nothing is written\n"
                          + "\n".join(different[:convert.SHOWN]), code=3)
    return changes


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--normalize", required=True, action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    try:
        with lock.held(repo.ROOT):
            changes = normalization()
            if not args.dry_run:
                store.write(repo.ROOT, changes)
    except (KbError, tokens.TokenError) as error:
        print(error, file=sys.stderr)
        return getattr(error, "code", 3)
    for path in changes:
        print(f"{path}: {'planned' if args.dry_run else 'written'}")
    print(f"normalize: {len(changes)} files, no model facts changed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
