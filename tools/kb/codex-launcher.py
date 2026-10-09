#!/usr/bin/env python3
"""Pass Codex arguments through and persist explicit session KB guard modes."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile

# Resolve the installed symlink before importing the adjacent hook.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import hook


VALUES = {"-c", "--config", "--enable", "--disable", "--remote",
          "--remote-auth-token-env", "-i", "--image", "-m", "--model",
          "--local-provider", "-p", "--profile", "-s", "--sandbox", "-C", "--cd",
          "--add-dir", "-a", "--ask-for-approval"}
FLAGS = {"--strict-config", "--oss", "--approve-for-me", "--worktree", "--search",
         "--no-alt-screen", "--no-daemon", "--all", "--include-non-interactive",
         "--dangerously-bypass-approvals-and-sandbox", "--dangerously-bypass-hook-trust"}


def target(arguments):
    """Require an unambiguous resume UUID, preserving the native argument list."""
    directory = Path.cwd()
    resumed = False
    session_id = None
    positional = False
    index = 0
    while index < len(arguments):
        word = arguments[index]
        if word == "--":
            positional = True
            index += 1
            continue
        if not positional and word.startswith("-"):
            option, equals, value = word.partition("=")
            if option in VALUES:
                if not equals:
                    index += 1
                    if index == len(arguments):
                        raise ValueError(f"{option} requires a value")
                    value = arguments[index]
                if option in ("-C", "--cd"):
                    directory = Path(value).expanduser().absolute()
            elif len(word) > 2 and word[:2] in VALUES and not word.startswith("--"):
                if word[:2] == "-C":
                    directory = Path(word[2:]).expanduser().absolute()
            elif word not in FLAGS:
                raise ValueError(f"{word} cannot select an explicit session; use resume <UUID>")
        elif not resumed:
            if word != "resume":
                raise ValueError("KB_GUARD requires resume <explicit root session UUID>")
            resumed = True
        else:
            if session_id is not None:
                break  # The native CLI owns the prompt and its remaining words.
            session_id = hook.session_key(word)
            if session_id is None:
                raise ValueError("KB_GUARD requires an explicit root session UUID, not a name or picker")
        index += 1
    if session_id is not None:
        return session_id, directory
    raise ValueError("KB_GUARD requires resume <explicit root session UUID>")


def project_root(directory):
    result = subprocess.run(["git", "-C", str(directory), "rev-parse", "--show-toplevel"],
                            capture_output=True, text=True, check=True)
    root = Path(result.stdout.strip()).resolve()
    if root != hook.ROOT:
        raise ValueError(f"run the launcher in {hook.ROOT}, or select it with --cd")
    return root


def install(destination):
    """Preserve the installed native symlink and atomically place the launcher."""
    destination = Path(destination).expanduser().absolute()
    launcher = Path(__file__).resolve()
    native = destination.with_name("codex-native")
    if destination.is_symlink() and destination.resolve() == launcher:
        if not native.is_file() or not os.access(native, os.X_OK):
            raise ValueError(f"the native executable is missing: {native}")
        return
    if not destination.is_symlink() or not destination.is_file():
        raise ValueError(f"expected an existing native Codex symlink at {destination}")
    original = destination.resolve()
    if not os.access(original, os.X_OK):
        raise ValueError(f"the native executable is not executable: {original}")
    if native.exists() or native.is_symlink():
        if not native.is_symlink() or native.resolve() != original:
            raise ValueError(f"refusing to replace a different native executable: {native}")
    else:
        native.symlink_to(original)
    descriptor, name = tempfile.mkstemp(prefix=".codex-launcher-", dir=destination.parent)
    os.close(descriptor)
    os.unlink(name)
    try:
        os.symlink(launcher, name)
        os.replace(name, destination)
    finally:
        if os.path.lexists(name):
            os.unlink(name)


def main(arguments):
    if arguments[:1] == ["--install"]:
        if len(arguments) > 2:
            raise ValueError("usage: python3 tools/kb/codex-launcher.py --install [codex-symlink]")
        destination = arguments[1] if len(arguments) == 2 else Path.home() / ".local/bin/codex"
        install(destination)
        print(f"KB guard launcher installed: {destination}")
        return 0
    native = Path(sys.argv[0]).expanduser().absolute().with_name("codex-native")
    if not native.is_file() or not os.access(native, os.X_OK) or native.resolve() == Path(__file__).resolve():
        raise ValueError(f"install the launcher first; native executable missing: {native}")
    environment = dict(os.environ)
    mode = environment.get("KB_GUARD", "").lower()
    if mode:
        if mode not in ("on", "off"):
            raise ValueError("KB_GUARD must be on or off")
        session_id, directory = target(arguments)
        root = project_root(directory)
        path = hook.set_session_mode(root, session_id, mode)
        # A shared daemon must never inherit this client's maintenance switch.
        environment.pop("KB_GUARD", None)
        print(f"KB guard {mode}: session {session_id} in {root} ({path})", file=sys.stderr)
    os.execve(native, [str(native), *arguments], environment)


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"KB guard launcher: {error}", file=sys.stderr)
        sys.exit(2)
