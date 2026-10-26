"""Keep firmware-gate artifacts inside the checkout's configured results directory."""

from pathlib import Path


RESULTS = Path('tmp/local-results')
LEGACY_RESULTS = Path('local-results')


def results_root(root):
    root = Path(root).resolve()
    alias = root / RESULTS
    try:
        physical = alias.resolve()
    except (OSError, RuntimeError) as error:
        raise ValueError('the tmp/local-results link cannot be resolved') from error
    if root.is_relative_to(physical):
        raise ValueError('tmp/local-results cannot contain the checkout or its ancestors')
    if any(path.is_symlink() for path in (alias.parent, alias)) and not physical.is_dir():
        raise ValueError('the linked tmp/local-results directory is unavailable')
    if alias.exists() and not alias.is_dir():
        raise ValueError('tmp/local-results must be a directory')
    return physical


def owned(path, root):
    """Validate local artifact paths, including a linked results directory."""
    root, path = Path(root).resolve(), Path(path)
    if '..' in path.parts:
        raise ValueError('a local artifact cannot traverse parent directories')
    if not path.is_absolute():
        path = root / path
    if path.is_relative_to(root / LEGACY_RESULTS):
        raise ValueError('new artifacts must use tmp/local-results instead of local-results')
    try:
        physical = path.resolve()
        results = results_root(root)
    except (OSError, RuntimeError) as error:
        raise ValueError('a local artifact link cannot be resolved') from error
    if physical.is_relative_to(root / LEGACY_RESULTS):
        raise ValueError('new artifacts must use tmp/local-results instead of local-results')
    if path.is_relative_to(root / RESULTS):
        if not physical.is_relative_to(results):
            raise ValueError('a local artifact link escapes tmp/local-results')
        return path
    if path.is_relative_to(results):
        if not physical.is_relative_to(results):
            raise ValueError('a local artifact link escapes tmp/local-results')
        return root / RESULTS / path.relative_to(results)
    if physical.is_relative_to(root):
        return physical
    if physical.is_relative_to(results):
        return root / RESULTS / physical.relative_to(results)
    raise ValueError('an artifact must belong to the checkout or its tmp/local-results directory')


def container_directories(root):
    """Expose a configured external results directory at its physical path."""
    root = Path(root).resolve()
    physical = results_root(root)
    return [physical] if physical != root / RESULTS else []


def relative(path, root):
    return owned(path, root).relative_to(Path(root).resolve()).as_posix()
