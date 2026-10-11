#!/usr/bin/env python3
"""Validate every command projection's read-only recipe and run the full set."""

import argparse
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import tomllib

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from kb import fingerprint, project

VARIABLE = re.compile(r"\{(VQ_[A-Z0-9_]+)\}")
PLACEHOLDER = re.compile(r"<[^<>]+>")


class ContractError(ValueError):
    pass


def commands(root=ROOT, entries=None):
    """Require a checker for every registered command, using its own producer."""
    result, failures = [], []
    try:
        entries = project.load(root) if entries is None else entries
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ContractError(f'{project.PATH}: {error}') from error
    if not isinstance(entries, list):
        raise ContractError('projection registry must contain an array of tables')
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get('generator'), str):
            failures.append('projection entry must declare a generator command')
            continue
        if project.rendered(entry):
            continue
        name = entry.get('path', '<missing path>')
        argv = entry.get('check')
        if not isinstance(argv, list) or not argv or any(type(word) is not str or not word for word in argv):
            failures.append(f'{name}: check must be a nonempty argument array')
            continue
        try:
            producer = shlex.split(entry['generator'])
        except (KeyError, TypeError, ValueError):
            failures.append(f'{name}: invalid generator command')
            continue
        expected = [word for word in producer if word != '--write']
        actual = [word for word in argv if word != '--check']
        if argv.count('--check') != 1 or len(expected) != len(actual) or any(
            not (VARIABLE.fullmatch(right) if PLACEHOLDER.fullmatch(left) else left == right)
            for left, right in zip(expected, actual)
        ):
            failures.append(f'{name}: check must use the same producer and arguments with --check')
            continue
        scripts = [word for word in producer if word.endswith(('.py', '.sh'))]
        if len(scripts) != 1:
            failures.append(f'{name}: generator must name one repository script')
            continue
        script = Path(scripts[0])
        if script.is_absolute() or '..' in script.parts or not (root / script).is_file() \
                or not (root / script).resolve().is_relative_to(root.resolve()):
            failures.append(f'{name}: producer script is absent or outside the repository')
            continue
        result.append((name, argv))
    if failures:
        raise ContractError('\n'.join(failures))
    return result


def resolved(recipes, environment):
    """Resolve explicitly supplied source paths; missing inputs stop the run."""
    result = []
    for name, argv in recipes:
        values = []
        for word in argv:
            match = VARIABLE.fullmatch(word)
            if match:
                key = match[1]
                value = environment.get(key)
                if not value or value.startswith('-') or not Path(value).expanduser().is_dir():
                    raise ContractError(f'{name}: supply {key} as the exact pinned source checkout')
                word = str(Path(value).expanduser().resolve())
            values.append(word)
        result.append((name, values))
    return result


def run(root=ROOT, *, environment=None, execute=subprocess.run, compute=fingerprint.compute):
    """Run native and command checks outside their individual reader locks."""
    recipes = resolved(commands(root), os.environ if environment is None else environment)
    before = compute(root).value
    outputs, errors, failed = [], [], []
    for name, argv in [('native projections', ['uv', 'run', 'kb', 'project', '--check']), *recipes]:
        try:
            result = execute(argv, cwd=root, capture_output=True)
        except OSError as error:
            raise ContractError(f'{name}: primary checker cannot start: {error}') from error
        outputs.append(result.stdout)
        errors.append(result.stderr)
        if result.returncode:
            failed.append(f'{name}: exit {result.returncode}')
    if compute(root).value != before:
        raise ContractError('compiler inputs change during projection checks; results are withheld')
    return b''.join(outputs), b''.join(errors), failed


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true', help='execute all registered comparisons; require every source')
    args = parser.parse_args(argv)
    try:
        recipes = commands()
        if not args.run:
            print(f'status=PASS command_projection_contracts={len(recipes)}')
            return 0
        output, errors, failed = run()
        sys.stdout.buffer.write(output)
        sys.stderr.buffer.write(errors)
        if failed:
            print('\n'.join(failed), file=sys.stderr)
            return 1
        print(f'status=PASS all_projection_checks command_groups={len(recipes)}')
        return 0
    except ContractError as error:
        print(f'error: {error}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
