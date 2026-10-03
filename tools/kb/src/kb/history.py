"""Recorded former references and address changes of runtime profile keys.

Entity files own former references. Git records the previous declarations of
profile keys; current feature targets associate those keys with a meaning.
History entries describe declarations and retain their source commit.
"""

from pathlib import Path
import re
import subprocess
import tomllib

from kb import repo, store
from kb.repo import KbError


def former_references(symbol, sources, root=repo.ROOT):
    """Full former references of the exact symbol entry, with graph names as
    the representation of an entry that no owned file states."""
    found = []
    owned = False
    for source in sorted(set(sources) | set(symbol.get("src") or ())):
        path = Path(source)
        if path.parts[:1] != (store.TREE.name,) or path.suffix != ".toml":
            continue
        if not (root / path).is_file():
            continue
        for entry in store.load(root, path).get("symbol", ()):
            address = entry.get("address")
            address = int(address, 16) if isinstance(address, str) else address
            if entry.get("layout") == symbol["layout"] and address == symbol["address"]:
                owned = True
                found.extend(entry.get("former", ()))
    return list(dict.fromkeys(found if owned else symbol.get("former") or ()))


def _keys(graph, meaning, layout, root):
    from kb.adapters import profiles

    layouts = repo.layouts(root)
    found = {}
    rows = graph.run(
        "MATCH (f:Kb:Entity {kind: 'feature'})-[t:TARGETS]->(l:Kb:Layout) "
        "WHERE $layout IS NULL OR l.key = $layout "
        "RETURN f.slug AS feature, l.key AS layout, properties(t) AS target", layout=layout)
    for row in rows:
        table = profiles.CANONICAL_TABLES.get(row["feature"])
        if table is None or row["layout"] not in layouts:
            continue
        target = row["target"] or {}
        tables = [table] + (["map_families"] if row["feature"] == "map_switching" else [])
        for table in tables:
            keys = dict(target.get(profiles.KEY_TABLE[table]) or {})
            if profiles.KEY_TABLE[table] == "symbols":
                keys.update((key, role.get("symbol"))
                            for key, role in (target.get("roles") or {}).items())
            for key, ref in keys.items():
                if isinstance(ref, str) and "/".join(ref.split("/")[:2]) == meaning:
                    for image in layouts[row["layout"]].images:
                        found[(image, table, key)] = row["layout"]
    return found


def _address(profiles, image, table, key, seen=()):
    if image in seen:
        raise KbError(f"historical profile inheritance cycle at {image}", code=3)
    profile = profiles.get(image, {})
    value = profile.get(table, {}).get(key)
    if value is None and profile.get("inherits"):
        return _address(profiles, profile["inherits"], table, key, (*seen, image))
    if value is None:
        return None
    value = int(value, 16) if isinstance(value, str) else value
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 0xffffffff:
        raise KbError(f"historical profile {image}.{table}.{key}: invalid address {value!r}",
                      code=3)
    return value


def _snapshots(patch, commit):
    """Both complete file versions in a diff with whole-file context."""
    before, after = [], []
    hunk = False
    for line in patch.splitlines():
        if line.startswith("@@ "):
            hunk = True
            continue
        if not hunk or not line:
            continue
        if line[0] in " -":
            before.append(line[1:])
        if line[0] in " +":
            after.append(line[1:])
    try:
        return [tomllib.loads("\n".join(lines)).get("profile", {}) for lines in (before, after)]
    except tomllib.TOMLDecodeError as error:
        raise KbError(f"profile history at {commit}: unreadable snapshot: {error}", code=3) \
            from error


def profile_changes(graph, meaning, layout=None, root=repo.ROOT):
    """Address corrections of keys that current feature targets give a meaning.
    Numeric and canonical hexadecimal representations denote one address."""
    from kb.adapters.profiles import PROFILES

    keys = _keys(graph, meaning, layout, root)
    if not keys:
        return []
    names = sorted({key for _, _, key in keys})
    pattern = "^[[:space:]]*(" + "|".join(re.escape(name) for name in names) \
              + ")[[:space:]]*="
    command = ["git", "--no-pager", "log", "--first-parent", "--reverse",
               "--diff-merges=first-parent", "--format=%x1e%H", "--no-color",
               "--no-ext-diff", "--no-textconv", "--no-renames", "-p", "--unified=100000",
               "-G", pattern, "--", PROFILES.as_posix()]
    try:
        result = subprocess.run(command, cwd=root, capture_output=True, text=True,
                                encoding="utf-8")
    except OSError as error:
        raise KbError(f"cannot read profile Git history: {error}", code=2) from error
    if result.returncode:
        raise KbError(f"cannot read profile Git history: {result.stderr.strip()}", code=2)
    found, seen = [], set()
    for chunk in result.stdout.split("\x1e")[1:]:
        commit, _, patch = chunk.partition("\n")
        commit = commit.strip()
        if not re.fullmatch(r"[0-9a-f]{40}", commit):
            raise KbError(f"profile history: invalid commit {commit!r}", code=3)
        before, after = _snapshots(patch, commit)
        for (image, table, key), on in sorted(keys.items()):
            old, new = (_address(profiles, image, table, key) for profiles in (before, after))
            identity = commit, on, table, key, old, new
            if old is not None and new is not None and old != new and identity not in seen:
                seen.add(identity)
                found.append({"commit": commit, "source": PROFILES.as_posix(), "profile": image,
                              "layout": on, "table": table, "key": key,
                              "old": f"{old:08x}", "new": f"{new:08x}"})
    return found
