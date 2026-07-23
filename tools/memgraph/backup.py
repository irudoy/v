#!/usr/bin/env python3
"""Ежесуточное резервное копирование Memgraph на SMB NAS.

Скрипт не использует локальный промежуточный архив:

1. проверяет 24-часовой интервал по локальному состоянию;
2. монтирует SMB share через macOS Keychain, если она не подключена;
3. создаёт native snapshot;
4. передаёт DUMP DATABASE через gzip сразу на NAS;
5. проверяет dump, считает узлы/рёбра/индексы и пишет manifest;
6. публикует комплект атомарным rename внутри SMB share.

Запуск:
  python3 tools/memgraph/backup.py --status
  python3 tools/memgraph/backup.py --if-due
"""

from __future__ import annotations

import argparse
import csv
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import fcntl
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import time
import tomllib
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[2]
MEMGRAPH_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG = MEMGRAPH_DIR / "backup.local.toml"
DEFAULT_STATE = MEMGRAPH_DIR / "backup.state.json"
DEFAULT_LOCK = MEMGRAPH_DIR / "backup.lock"
SNAPSHOT_DIR = MEMGRAPH_DIR / "data" / "lib" / "snapshots"
FORMAT_VERSION = 1
MINIMUM_ALLOWED_INTERVAL_HOURS = 24


class BackupError(RuntimeError):
    pass


@dataclass(frozen=True)
class Config:
    smb_url: str
    mount_point: Path
    backup_subdir: PurePosixPath
    minimum_interval_hours: int
    container_name: str
    mount_timeout_seconds: int
    command_timeout_seconds: int

    @property
    def destination(self) -> Path:
        return self.mount_point.joinpath(*self.backup_subdir.parts)


@dataclass(frozen=True)
class BackupState:
    created_at: datetime
    destination: str
    bundle: str


@dataclass(frozen=True)
class DumpStats:
    lines: int
    nodes: int
    relationships: int
    indexes: int
    uncompressed_bytes: int


@dataclass(frozen=True)
class Snapshot:
    host_path: Path
    container_path: str
    timestamp: int
    creation_time: str


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def iso_utc(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def parse_utc(value: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError("timestamp не является строкой")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("timestamp не содержит timezone")
    return parsed.astimezone(timezone.utc)


def require_int(data, key, default=None):
    value = data.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int):
        raise BackupError(f"{key} должен быть целым числом")
    return value


def load_config(path: Path) -> Config:
    try:
        with path.open("rb") as fh:
            data = tomllib.load(fh)
    except FileNotFoundError:
        raise BackupError(
            f"нет локального конфига {path}; скопируйте backup.example.toml"
        ) from None
    except tomllib.TOMLDecodeError as error:
        raise BackupError(f"{path}: некорректный TOML: {error}") from error

    allowed = {
        "smb_url",
        "mount_point",
        "backup_subdir",
        "minimum_interval_hours",
        "container_name",
        "mount_timeout_seconds",
        "command_timeout_seconds",
    }
    unknown = sorted(set(data) - allowed)
    if unknown:
        raise BackupError(f"{path}: неизвестные параметры: {', '.join(unknown)}")

    required = ("smb_url", "mount_point", "backup_subdir")
    missing = [key for key in required if not isinstance(data.get(key), str)]
    if missing:
        raise BackupError(f"{path}: нет строковых параметров: {', '.join(missing)}")

    smb_url = data["smb_url"]
    parsed_url = urlparse(smb_url)
    if parsed_url.scheme.lower() != "smb" or not parsed_url.hostname:
        raise BackupError(f"{path}: smb_url должен иметь вид smb://server/share")
    if not parsed_url.path.strip("/"):
        raise BackupError(f"{path}: smb_url должен называть конкретную share")
    if any(char in smb_url for char in ('"', "\n", "\r")):
        raise BackupError(f"{path}: smb_url содержит недопустимые символы")

    mount_point = Path(data["mount_point"])
    if not mount_point.is_absolute():
        raise BackupError(f"{path}: mount_point должен быть абсолютным")

    backup_subdir = PurePosixPath(data["backup_subdir"])
    if (
        backup_subdir.is_absolute()
        or not backup_subdir.parts
        or backup_subdir == PurePosixPath(".")
        or ".." in backup_subdir.parts
    ):
        raise BackupError(
            f"{path}: backup_subdir должен быть безопасным относительным путём"
        )

    minimum_interval_hours = require_int(
        data, "minimum_interval_hours", MINIMUM_ALLOWED_INTERVAL_HOURS
    )
    if minimum_interval_hours < MINIMUM_ALLOWED_INTERVAL_HOURS:
        raise BackupError(
            "minimum_interval_hours не может быть меньше "
            f"{MINIMUM_ALLOWED_INTERVAL_HOURS}"
        )

    mount_timeout_seconds = require_int(data, "mount_timeout_seconds", 30)
    command_timeout_seconds = require_int(data, "command_timeout_seconds", 900)
    if mount_timeout_seconds <= 0 or command_timeout_seconds <= 0:
        raise BackupError("timeout должен быть положительным")

    container_name = data.get("container_name", "vq-memgraph-mage")
    if not isinstance(container_name, str) or not container_name.strip():
        raise BackupError("container_name должен быть непустой строкой")

    return Config(
        smb_url=smb_url,
        mount_point=mount_point,
        backup_subdir=backup_subdir,
        minimum_interval_hours=minimum_interval_hours,
        container_name=container_name,
        mount_timeout_seconds=mount_timeout_seconds,
        command_timeout_seconds=command_timeout_seconds,
    )


def read_state(path: Path) -> BackupState | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, json.JSONDecodeError) as error:
        raise BackupError(f"{path}: не читается локальное состояние: {error}") from error
    try:
        return BackupState(
            created_at=parse_utc(data["created_at_utc"]),
            destination=str(data["destination"]),
            bundle=str(data["bundle"]),
        )
    except (KeyError, TypeError, ValueError) as error:
        raise BackupError(f"{path}: некорректное локальное состояние: {error}") from error


def write_json_atomic(path: Path, data) -> None:
    temporary = path.with_name(f".{path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def write_state(path: Path, state: BackupState) -> None:
    write_json_atomic(path, {
        "created_at_utc": iso_utc(state.created_at),
        "destination": state.destination,
        "bundle": state.bundle,
    })


def due_status(
    state: BackupState | None,
    destination: Path,
    minimum_interval_hours: int,
    now: datetime,
):
    if state is None:
        return True, "нет локального состояния", None
    if state.destination != str(destination):
        return True, "назначение backup изменилось", None
    next_due = state.created_at + timedelta(hours=minimum_interval_hours)
    if now >= next_due:
        return True, "интервал истёк", next_due
    return False, "интервал не истёк", next_due


@contextmanager
def exclusive_lock(path: Path):
    with path.open("a+", encoding="utf-8") as fh:
        try:
            fcntl.flock(fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise BackupError("другой процесс backup уже выполняется") from None
        yield


def run_capture(args, *, input_text=None, timeout=30, cwd=None):
    try:
        result = subprocess.run(
            args,
            input=input_text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            cwd=cwd,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise BackupError(f"команда не выполнена: {args[0]}: {error}") from error
    if result.returncode:
        detail = result.stderr.strip() or result.stdout.strip() or "нет диагностики"
        raise BackupError(
            f"команда завершилась с кодом {result.returncode}: "
            f"{' '.join(args)}: {detail}"
        )
    return result.stdout


def mount_record(mount_point: Path) -> str | None:
    output = run_capture(["/sbin/mount"], timeout=10)
    marker = f" on {mount_point} (smbfs,"
    for line in output.splitlines():
        if marker in line:
            return line
    return None


def mount_source(record: str):
    source = record.split(" on ", 1)[0]
    parsed = urlparse(f"smb:{source}")
    return parsed.hostname, unquote(parsed.path).strip("/")


def matching_mount_record(config: Config) -> str | None:
    record = mount_record(config.mount_point)
    if record is None:
        return None
    actual_host, actual_share = mount_source(record)
    expected = urlparse(config.smb_url)
    expected_share = unquote(expected.path).strip("/")
    if (
        actual_host is None
        or actual_host.casefold() != expected.hostname.casefold()
        or actual_share.casefold() != expected_share.casefold()
    ):
        raise BackupError(
            f"{config.mount_point} занят другой SMB share: {record}"
        )
    return record


def ensure_smb_mount(config: Config) -> bool:
    if matching_mount_record(config):
        return False

    run_capture(
        ["/usr/bin/osascript", "-e", f'mount volume "{config.smb_url}"'],
        timeout=config.mount_timeout_seconds,
    )
    deadline = time.monotonic() + config.mount_timeout_seconds
    while time.monotonic() < deadline:
        if matching_mount_record(config):
            return True
        time.sleep(0.5)
    raise BackupError(
        f"SMB share {config.smb_url} не появилась в {config.mount_point}"
    )


def require_smb_mount(config: Config) -> str:
    record = matching_mount_record(config)
    if not record:
        raise BackupError(
            f"{config.mount_point} не является SMB mount; запись остановлена"
        )
    return record


def docker_mgconsole(config: Config, query: str, output_format: str) -> str:
    return run_capture(
        [
            "docker", "exec", "-i", config.container_name,
            "mgconsole", f"--output_format={output_format}", "--no_history",
        ],
        input_text=query,
        timeout=config.command_timeout_seconds,
    )


def container_image(config: Config) -> str:
    running = run_capture(
        ["docker", "inspect", "--format={{.State.Running}}", config.container_name],
        timeout=30,
    ).strip()
    if running != "true":
        raise BackupError(f"контейнер {config.container_name} не запущен")
    return run_capture(
        ["docker", "inspect", "--format={{.Config.Image}}", config.container_name],
        timeout=30,
    ).strip()


def create_snapshot(config: Config) -> Snapshot:
    docker_mgconsole(
        config,
        "CREATE SNAPSHOT;\n",
        "csv",
    )
    output = docker_mgconsole(config, "SHOW SNAPSHOTS;\n", "csv")
    return parse_snapshot_output(output)


def parse_snapshot_output(
    output: str,
    snapshot_dir: Path | None = None,
) -> Snapshot:
    if snapshot_dir is None:
        snapshot_dir = SNAPSHOT_DIR
    try:
        reader = csv.DictReader(io.StringIO(output))
        required = {"path", "timestamp", "creation_time"}
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError(f"заголовок {reader.fieldnames}, ожидается {sorted(required)}")
        rows = list(reader)
        row = max(rows, key=lambda item: int(item["timestamp"]))
        container_path = row["path"].strip('"')
        timestamp = int(row["timestamp"])
        creation_time = row["creation_time"].strip('"')
    except (KeyError, TypeError, ValueError) as error:
        raise BackupError(f"SHOW SNAPSHOTS вернул неожиданный ответ: {error}") from error
    if not container_path:
        raise BackupError("SHOW SNAPSHOTS вернул пустой путь")
    host_path = snapshot_dir / Path(container_path).name
    if not host_path.is_file():
        raise BackupError(f"snapshot отсутствует в bind-mount: {host_path}")
    return Snapshot(host_path, container_path, timestamp, creation_time)


def stream_dump(config: Config, destination: Path) -> None:
    gzip_bin = shutil.which("gzip")
    if not gzip_bin:
        raise BackupError("gzip отсутствует в PATH")
    command = [
        "docker", "exec", "-i", config.container_name,
        "mgconsole", "--output_format=cypherl", "--no_history",
    ]
    try:
        with destination.open("wb") as output:
            database = subprocess.Popen(
                command,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            assert database.stdout is not None
            compressor = subprocess.Popen(
                [gzip_bin, "-c"],
                stdin=database.stdout,
                stdout=output,
                stderr=subprocess.PIPE,
            )
            database.stdout.close()
            try:
                _, database_error = database.communicate(
                    input=b"DUMP DATABASE;\n",
                    timeout=config.command_timeout_seconds,
                )
                _, gzip_error = compressor.communicate(
                    timeout=config.command_timeout_seconds,
                )
            except subprocess.TimeoutExpired as error:
                database.kill()
                compressor.kill()
                database.wait()
                compressor.wait()
                raise BackupError("DUMP DATABASE превысил timeout") from error
    except OSError as error:
        raise BackupError(f"не удалось записать {destination}: {error}") from error

    if database.returncode:
        detail = database_error.decode("utf-8", errors="replace").strip()
        raise BackupError(
            f"DUMP DATABASE завершился с кодом {database.returncode}: {detail}"
        )
    if compressor.returncode:
        detail = gzip_error.decode("utf-8", errors="replace").strip()
        raise BackupError(f"gzip завершился с кодом {compressor.returncode}: {detail}")


def inspect_dump(path: Path) -> DumpStats:
    lines = nodes = relationships = indexes = uncompressed_bytes = 0
    cleanup = drop_temporary_index = False
    try:
        with gzip.open(path, "rb") as fh:
            for line in fh:
                lines += 1
                uncompressed_bytes += len(line)
                if line.startswith(b"CREATE (:__mg_vertex__"):
                    nodes += 1
                elif line.startswith(
                    b"MATCH (u:__mg_vertex__), (v:__mg_vertex__)"
                ):
                    relationships += 1
                elif (
                    line.startswith(b"CREATE INDEX ON :")
                    and b":__mg_vertex__" not in line
                ):
                    indexes += 1
                elif line.startswith(b"DROP INDEX ON :__mg_vertex__"):
                    drop_temporary_index = True
                elif line.startswith(b"MATCH (u) REMOVE u:__mg_vertex__"):
                    cleanup = True
    except (OSError, EOFError, gzip.BadGzipFile) as error:
        raise BackupError(f"{path}: повреждён gzip: {error}") from error
    if nodes <= 0:
        raise BackupError(f"{path}: dump не содержит узлов")
    if relationships <= 0:
        raise BackupError(f"{path}: dump не содержит рёбер")
    if not cleanup or not drop_temporary_index:
        raise BackupError(f"{path}: dump не содержит финальную очистку служебных данных")
    return DumpStats(lines, nodes, relationships, indexes, uncompressed_bytes)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_metadata() -> dict:
    head = run_capture(["git", "rev-parse", "HEAD"], cwd=ROOT, timeout=30).strip()
    branch = run_capture(
        ["git", "branch", "--show-current"], cwd=ROOT, timeout=30
    ).strip()
    status = run_capture(
        ["git", "status", "--porcelain=v1"], cwd=ROOT, timeout=30
    )
    return {
        "head": head,
        "branch": branch or None,
        "dirty": bool(status.strip()),
        "status_sha256": hashlib.sha256(status.encode("utf-8")).hexdigest(),
    }


def latest_remote_state(destination: Path) -> BackupState | None:
    if not destination.exists():
        return None
    latest = None
    try:
        children = list(destination.iterdir())
    except OSError as error:
        raise BackupError(f"не читается {destination}: {error}") from error
    for child in children:
        if not child.is_dir() or child.name.startswith("."):
            continue
        manifest_path = child / "manifest.json"
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            if manifest["format_version"] != FORMAT_VERSION:
                continue
            files = manifest["files"]
            if not files or any(
                not (child / relative).is_file() for relative in files
            ):
                continue
            created_at = parse_utc(manifest["created_at_utc"])
        except (
            FileNotFoundError,
            OSError,
            KeyError,
            TypeError,
            ValueError,
            json.JSONDecodeError,
        ):
            continue
        state = BackupState(created_at, str(destination), child.name)
        if latest is None or state.created_at > latest.created_at:
            latest = state
    return latest


def backup_name(created_at: datetime) -> str:
    return created_at.astimezone(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")


def create_bundle(config: Config, created_at: datetime) -> BackupState:
    require_smb_mount(config)
    destination = config.destination
    destination.mkdir(parents=True, exist_ok=True)
    require_smb_mount(config)

    name = backup_name(created_at)
    final = destination / name
    partial = destination / f".{name}.partial-{os.getpid()}"
    if final.exists():
        raise BackupError(f"комплект уже существует: {final}")
    if partial.exists():
        raise BackupError(f"временный комплект уже существует: {partial}")

    partial.mkdir()
    try:
        image = container_image(config)
        snapshot = create_snapshot(config)
        require_smb_mount(config)

        dump_path = partial / "database.cypherl.gz"
        stream_dump(config, dump_path)
        dump_stats = inspect_dump(dump_path)

        require_smb_mount(config)
        snapshot_dir = partial / "snapshot"
        snapshot_dir.mkdir()
        snapshot_path = snapshot_dir / snapshot.host_path.name
        shutil.copy2(snapshot.host_path, snapshot_path)
        source_snapshot_hash = sha256(snapshot.host_path)
        copied_snapshot_hash = sha256(snapshot_path)
        if source_snapshot_hash != copied_snapshot_hash:
            raise BackupError(
                f"SHA-256 snapshot не совпал после копирования: {snapshot_path}"
            )

        files = {
            "database.cypherl.gz": {
                "sha256": sha256(dump_path),
                "size": dump_path.stat().st_size,
                "uncompressed_size": dump_stats.uncompressed_bytes,
            },
            f"snapshot/{snapshot_path.name}": {
                "sha256": copied_snapshot_hash,
                "size": snapshot_path.stat().st_size,
            },
        }
        checksums = "".join(
            f"{details['sha256']}  {relative}\n"
            for relative, details in files.items()
        )
        (partial / "SHA256SUMS").write_text(checksums, encoding="ascii")

        manifest = {
            "format_version": FORMAT_VERSION,
            "project": "vq-hr-ecu",
            "created_at_utc": iso_utc(created_at),
            "minimum_interval_hours": config.minimum_interval_hours,
            "source": {
                "container": config.container_name,
                "image": image,
                "mount": require_smb_mount(config),
            },
            "database": {
                "nodes": dump_stats.nodes,
                "relationships": dump_stats.relationships,
                "indexes": dump_stats.indexes,
                "dump_lines": dump_stats.lines,
            },
            "snapshot": {
                "container_path": snapshot.container_path,
                "timestamp": snapshot.timestamp,
                "creation_time": snapshot.creation_time,
                "filename": snapshot_path.name,
            },
            "git": git_metadata(),
            "files": files,
        }
        write_json_atomic(partial / "manifest.json", manifest)

        require_smb_mount(config)
        partial.rename(final)
    except Exception:
        try:
            if partial.exists():
                shutil.rmtree(partial)
        except OSError:
            pass
        raise
    return BackupState(created_at, str(destination), final.name)


def print_status(config: Config, state: BackupState | None, now: datetime) -> bool:
    due, reason, next_due = due_status(
        state,
        config.destination,
        config.minimum_interval_hours,
        now,
    )
    parts = [f"due={'true' if due else 'false'}", f"reason={reason}"]
    if state is not None:
        parts.append(f"last_success={iso_utc(state.created_at)}")
    if next_due is not None:
        parts.append(f"next_due={iso_utc(next_due)}")
    parts.append(f"destination={config.destination}")
    print(" ".join(parts))
    return due


def run_if_due(config: Config, state_path: Path, lock_path: Path) -> int:
    with exclusive_lock(lock_path):
        now = utc_now()
        state = read_state(state_path)
        due, _, _ = due_status(
            state,
            config.destination,
            config.minimum_interval_hours,
            now,
        )
        if not due:
            print_status(config, state, now)
            return 0

        mounted_by_script = ensure_smb_mount(config)
        remote_state = latest_remote_state(config.destination)
        if remote_state is not None:
            remote_due, _, _ = due_status(
                remote_state,
                config.destination,
                config.minimum_interval_hours,
                now,
            )
            if not remote_due:
                write_state(state_path, remote_state)
                print_status(config, remote_state, now)
                return 0

        created = create_bundle(config, now)
        write_state(state_path, created)
        print(
            f"backup_created={created.bundle} destination={created.destination} "
            f"mounted_by_script={'true' if mounted_by_script else 'false'}"
        )
        return 0


def parser():
    out = argparse.ArgumentParser(description=__doc__)
    mode = out.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--status",
        action="store_true",
        help="проверить локальный 24-часовой интервал без подключения NAS",
    )
    mode.add_argument(
        "--if-due",
        action="store_true",
        help="создать backup, только если интервал истёк",
    )
    out.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    out.add_argument("--state-file", type=Path, default=DEFAULT_STATE)
    out.add_argument("--lock-file", type=Path, default=DEFAULT_LOCK)
    return out


def main():
    args = parser().parse_args()
    try:
        config = load_config(args.config.expanduser().resolve())
        state_path = args.state_file.expanduser().resolve()
        if args.status:
            print_status(config, read_state(state_path), utc_now())
            return 0
        return run_if_due(
            config,
            state_path,
            args.lock_file.expanduser().resolve(),
        )
    except BackupError as error:
        print(f"backup error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
