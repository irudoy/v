"""Compare a rendered projection with its complete on-disk file set."""

from pathlib import Path


def compare(expected, directory, patterns, *, regenerate):
    """Reject missing, extra, or changed files without changing the directory."""
    directory = Path(directory)
    found = {path.name for pattern in patterns for path in directory.glob(pattern)}
    failures = [f"{directory / name}: unexpected projection file"
                for name in sorted(found - expected.keys())]
    for name, content in sorted(expected.items()):
        path = directory / name
        if not path.is_file():
            failures.append(f"{path}: missing")
        elif path.read_bytes() != content:
            failures.append(f"{path}: differs from its rendering")
    if failures:
        raise ValueError('\n'.join(failures) + f'\nfix: {regenerate}')
