"""Graph instances by working tree (tools/kb/SPEC.md, section 11).

The main working tree uses the compose service of tools/memgraph/ on its
published port. A linked working tree gets a container from the image of the
compose file, with its data under `.kb/memgraph/` and a loopback port from
the range of `[instances]` in tools/kb/config.toml; `.kb/instance.toml`
records the container, the port, the image, and the time of last use.
`KB_BOLT` overrides the connection for tests against a scratch server.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import os
from pathlib import Path
import re
import socket
import subprocess
import time
import tomllib

from kb import repo

COMPOSE = Path("tools/memgraph/docker-compose.yml")
FILE = repo.STATE / "instance.toml"
DATA = repo.STATE / "memgraph"
REPO_LABEL = "vq.kb.repo"
TREE_LABEL = "vq.kb.worktree"
PORT_LABEL = "vq.kb.port"
BOLT_PORT = 7687
READY_SECONDS = 90


@dataclass(frozen=True)
class Compose:
    image: str
    container: str
    port: int
    flags: tuple


@dataclass(frozen=True)
class Container:
    name: str
    state: str
    worktree: str
    port: int | None

    @property
    def running(self):
        return self.state == "running"


def compose(root=repo.ROOT):
    """The image, container name, published Bolt port, and server flags of the
    memgraph service of the compose file."""
    text = (root / COMPOSE).read_text(encoding="utf-8")
    block = re.search(r"^  memgraph:\n(.*?)(?=^  \S|\Z)", text, re.M | re.S)
    if block is None:
        raise repo.KbError(f"{COMPOSE}: no memgraph service")
    body = block.group(1)
    fields = {
        "image": re.search(r"^\s+image:\s*(\S+)", body, re.M),
        "container": re.search(r"^\s+container_name:\s*(\S+)", body, re.M),
        "port": re.search(rf'^\s*- "127\.0\.0\.1:(\d+):{BOLT_PORT}"', body, re.M),
        "command": re.search(r"^\s+command:\n((?:\s+- .*\n)+)", body, re.M),
    }
    absent = [name for name, match in fields.items() if match is None]
    if absent:
        raise repo.KbError(f"{COMPOSE}: the memgraph service lacks {', '.join(absent)}")
    return Compose(fields["image"].group(1), fields["container"].group(1),
                   int(fields["port"].group(1)),
                   tuple(re.findall(r'- "(--[^"]+)"', fields["command"].group(1))))


def _git_path(root, option):
    result = subprocess.run(["git", "rev-parse", "--path-format=absolute", option],
                            cwd=root, capture_output=True, text=True)
    if result.returncode != 0:
        raise repo.KbError(f"git rev-parse {option}: {result.stderr.strip()}")
    return Path(result.stdout.strip()).resolve()


def common_dir(root=repo.ROOT):
    return _git_path(root, "--git-common-dir")


def is_main(root=repo.ROOT):
    """True in the main working tree, whose git directory is the common one."""
    return _git_path(root, "--git-dir") == common_dir(root)


def worktrees(root=repo.ROOT):
    result = subprocess.run(["git", "worktree", "list", "--porcelain"], cwd=root,
                            capture_output=True, text=True, check=True)
    return {str(Path(line.removeprefix("worktree ")).resolve())
            for line in result.stdout.splitlines() if line.startswith("worktree ")}


def settings(root=repo.ROOT):
    return repo.config(root)["instances"]


def container_name(root=repo.ROOT):
    return "kb-" + hashlib.sha256(str(Path(root).resolve()).encode()).hexdigest()[:12]


def read(root=repo.ROOT):
    try:
        return tomllib.loads((root / FILE).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None


def _now():
    return datetime.now(timezone.utc).replace(microsecond=0)


def write(root, container, port, image):
    path = root / FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(
        f'container = "{container}"\nport = {port}\nimage = "{image}"\n'
        f'last_used = "{_now().isoformat().replace("+00:00", "Z")}"\n', encoding="utf-8")
    temporary.replace(path)


def touch(root, state):
    write(root, state["container"], state["port"], state["image"])


def uri(root=repo.ROOT):
    """The Bolt address of the working tree's instance."""
    override = os.environ.get("KB_BOLT")
    if override:
        return override
    if is_main(root):
        return f"bolt://localhost:{compose(root).port}"
    state = read(root)
    if state is None:
        raise repo.KbError("this linked working tree has no graph instance; "
                           "run `uv run kb instance up`", code=6)
    touch(root, state)
    return f"bolt://localhost:{state['port']}"


# Docker ----------------------------------------------------------------------

def _docker(*args, check=True):
    try:
        result = subprocess.run(["docker", *args], capture_output=True, text=True)
    except FileNotFoundError:
        raise repo.KbError("docker is not installed", code=6) from None
    if check and result.returncode != 0:
        raise repo.KbError(f"docker {' '.join(args[:2])}: {result.stderr.strip()}", code=6)
    return result


def containers(root=repo.ROOT):
    """The containers of the linked working trees of this repository."""
    fmt = "\t".join(("{{.Names}}", "{{.State}}", f'{{{{.Label "{TREE_LABEL}"}}}}',
                     f'{{{{.Label "{PORT_LABEL}"}}}}'))
    result = _docker("ps", "-a", "--filter", f"label={REPO_LABEL}={common_dir(root)}",
                     "--format", fmt)
    found = []
    for line in result.stdout.splitlines():
        name, state, tree, port = line.split("\t")
        found.append(Container(name, state, tree, int(port) if port else None))
    return sorted(found, key=lambda item: item.name)


def state_of(name):
    result = _docker("inspect", "--format", "{{.State.Status}}", name, check=False)
    return result.stdout.strip() if result.returncode == 0 else None


def running_count(root=repo.ROOT):
    main = state_of(compose(root).container) == "running"
    return int(main) + sum(item.running for item in containers(root))


def _free_port(root):
    start, end = settings(root)["ports"]
    taken = {item.port for item in containers(root)}
    for port in range(start, end):
        if port in taken:
            continue
        with socket.socket() as probe:
            try:
                probe.bind(("127.0.0.1", port))
            except OSError:
                continue
        return port
    raise repo.KbError(f"no free port in {start}..{end - 1} of [instances] ports", code=6)


def wait_ready(address, seconds=READY_SECONDS):
    from neo4j import GraphDatabase
    from neo4j.exceptions import ServiceUnavailable

    deadline = time.monotonic() + seconds
    while True:
        try:
            with GraphDatabase.driver(address, auth=("", "")) as driver:
                driver.verify_connectivity()
            return
        except (ServiceUnavailable, OSError):
            if time.monotonic() >= deadline:
                raise repo.KbError(f"no graph answers at {address} after {seconds} s",
                                   code=6) from None
            time.sleep(1)


def prune(root=repo.ROOT, log=print):
    """Remove the containers of working trees that no longer exist and stop
    containers idle longer than `[instances] idle_days`."""
    alive = worktrees(root)
    idle = timedelta(days=settings(root)["idle_days"])
    for item in containers(root):
        if str(Path(item.worktree).resolve()) not in alive:
            _docker("rm", "-f", item.name)
            log(f"removed {item.name}: working tree {item.worktree} no longer exists")
            continue
        if not item.running:
            continue
        state = read(Path(item.worktree))
        last = state and datetime.fromisoformat(state["last_used"].replace("Z", "+00:00"))
        if last is None or _now() - last > idle:
            _docker("stop", item.name)
            log(f"stopped {item.name}: idle since {state['last_used'] if state else 'unknown'}")


def up(root=repo.ROOT, log=print):
    service = compose(root)
    if is_main(root):
        if state_of(service.container) != "running":
            _docker("compose", "-f", str(root / COMPOSE), "up", "-d")
        address = uri(root)
        wait_ready(address)
        log(f"main instance {service.container} at {address}")
        return address
    prune(root, log)
    name = container_name(root)
    state = state_of(name)
    record = read(root)
    if state == "running" and record:
        touch(root, record)
    else:
        limit = settings(root)["max_running"]
        if running_count(root) >= limit:
            raise repo.KbError(
                f"{limit} instances run, the limit of [instances] max_running; stop one "
                f"with `uv run kb instance down` in its working tree", code=6)
        if state is not None and record:
            _docker("start", name)
            port = record["port"]
        else:
            if state is not None:
                _docker("rm", "-f", name)
            port = _free_port(root)
            data = root / DATA
            for part in ("lib", "log"):
                (data / part).mkdir(parents=True, exist_ok=True)
            _docker("run", "-d", "--name", name, "--user", "root",
                    "--label", f"{REPO_LABEL}={common_dir(root)}",
                    "--label", f"{TREE_LABEL}={Path(root).resolve()}",
                    "--label", f"{PORT_LABEL}={port}",
                    "-p", f"127.0.0.1:{port}:{BOLT_PORT}",
                    "-v", f"{data / 'lib'}:/var/lib/memgraph",
                    "-v", f"{data / 'log'}:/var/log/memgraph",
                    service.image, *service.flags)
        write(root, name, port, service.image)
    address = uri(root)
    wait_ready(address)
    log(f"instance {name} at {address}")
    return address


def down(root=repo.ROOT, log=print):
    if is_main(root):
        _docker("compose", "-f", str(root / COMPOSE), "down")
        log(f"stopped the main instance {compose(root).container}")
        return
    name = container_name(root)
    if state_of(name) is not None:
        _docker("rm", "-f", name)
        log(f"removed {name}; the graph data stays in {DATA}")
    (root / FILE).unlink(missing_ok=True)


def status(root=repo.ROOT):
    service = compose(root)
    lines = []
    if is_main(root):
        lines.append(f"working tree: main; instance {service.container} "
                     f"{state_of(service.container) or 'absent'} at {uri(root)}")
    else:
        record = read(root)
        name = container_name(root)
        where = f"port {record['port']}, last used {record['last_used']}" if record else "no record"
        lines.append(f"working tree: linked; instance {name} {state_of(name) or 'absent'}, {where}")
    lines.append(f"main instance {service.container}: {state_of(service.container) or 'absent'}")
    for item in containers(root):
        lines.append(f"{item.name}: {item.state}, port {item.port}, working tree {item.worktree}")
    lines.append(f"running: {running_count(root)} of [instances] max_running "
                 f"{settings(root)['max_running']}")
    return lines
