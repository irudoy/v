"""Migrate unresolved review bindings from manifest to exported-data identity.

Usage: uv run python -m tools.kb.migrate_l0_identity --from-ref COMMIT [--write]
The default is a dry run. Only review `l0` fields in owners.toml can change.
"""

import argparse
import hashlib
from pathlib import Path
import subprocess
import tomllib

import tomlkit

from kb import compile, l0, lock, match, reconciliation, repo, store


def bindings(layout, previous, root):
    """Refuse migration unless the historical manifest binds today's exports."""
    directory = root / repo.L0 / layout
    before = tomllib.loads(previous.decode("utf-8"))
    current = tomllib.loads((directory / l0.MANIFEST).read_text(encoding="utf-8"))
    if (before["layout"] != layout or any(before[key] != current[key]
            for key in ("layout", "image", "image_sha256"))
            or before["files"].keys() != current["files"].keys()):
        raise repo.KbError(f"L0 {layout}: the historical export identity differs")
    for name, entry in before["files"].items():
        if Path(name).name != name or name in (".", ".."):
            raise repo.KbError(f"L0 {layout}: invalid export filename {name!r}")
        actual = repo.sha256_file(directory / name)
        if actual != entry["sha256"] or actual != current["files"][name]["sha256"]:
            raise repo.KbError(f"L0 {layout}: exported data changed in {name}")
    return hashlib.sha256(previous).hexdigest()[:16], match.l0_digest(layout, root)


def plan(model, previous):
    """Keep each exact unresolved claim and reason; change only its L0 identity."""
    text = (model.root / repo.OWNER_CONFIG).read_text(encoding="utf-8")
    document = tomlkit.parse(text)
    records = document["reconciliation"]["review"]
    identities = {layout: bindings(layout, previous[layout], model.root)
                  for layout in {record["layout"] for record in records}}
    actual = {reconciliation.difference_key(item): item
              for item in reconciliation.differences(model)}
    seen, changed = set(), 0
    for record in records:
        key = reconciliation.difference_key(record)
        item = actual.get(key)
        if (key in seen or item is None or set(record) != set(item) | {"state", "reason"}
                or record.get("state") != "unresolved"
                or not isinstance(record.get("reason"), str) or not record["reason"].strip()
                or any(record.get(name) != value for name, value in item.items() if name != "l0")
                or record.get("l0") not in identities[record["layout"]]):
            raise repo.KbError(f"{record['subject']}: the exact historical review does not bind")
        seen.add(key)
        if record["l0"] != item["l0"]:
            record["l0"] = item["l0"]
            changed += 1
    if seen != actual.keys():
        raise repo.KbError("Unreviewed differences remain; no review bindings are written")
    return tomlkit.dumps(document), changed


def historical_manifests(root, reference, layouts):
    commit = subprocess.run(["git", "rev-parse", "--verify", "--end-of-options",
                             f"{reference}^{{commit}}"], cwd=root, check=True,
                            capture_output=True, text=True).stdout.strip()
    return {layout: subprocess.run(
        ["git", "show", f"{commit}:{repo.L0 / layout / l0.MANIFEST}"],
        cwd=root, check=True, capture_output=True).stdout for layout in layouts}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--from-ref", required=True, help="commit of the accepted legacy bindings")
    parser.add_argument("--write", action="store_true", help="apply the checked migration")
    args = parser.parse_args(argv)
    try:
        with lock.held():
            model = compile.build()
            layouts = {item["layout"] for item in model.config["reconciliation"]["review"]}
            previous = historical_manifests(repo.ROOT, args.from_ref, sorted(layouts))
            text, count = plan(model, previous)
            if args.write and count:
                store.write(repo.ROOT, {repo.OWNER_CONFIG: text})
                compile.cached.cache_clear()
            print(f"{'Migrated' if args.write else 'Would migrate'} {count} review bindings")
    except (repo.KbError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"{error}\n")


if __name__ == "__main__":
    main()
