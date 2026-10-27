"""Run the primary container only after its checkout has no surviving gate child."""

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid


ROOT = Path(__file__).resolve().parents[2]
import gate_paths as local_paths
import image_inputs

OWNER_LABEL = 'vhrev.sh-elf-run.owner'
ROOT_LABEL = 'vhrev.sh-elf-run.checkout'
RUN_LABEL = 'vhrev.sh-elf-run.attempt'
CID = re.compile(r'[0-9a-f]{64}')
TOKEN = re.compile(r'[0-9a-f]{32}')
IMAGE = re.compile(r'sha256:[0-9a-f]{64}')
RUNTIME_PREFIX = 'VQ_SH_ELF_CONTAINER '
INSPECT = ('{"id":{{json .Id}},"labels":{{json .Config.Labels}},'
           '"mounts":{{json .Mounts}},"status":{{json .State.Status}},'
           '"running":{{json .State.Running}},'
           '"restart":{{json .HostConfig.RestartPolicy.Name}}}')
# An image without labels has no Config.Labels key, so the whole Config is read.
IMAGE_INSPECT = '{"id":{{json .Id}},"config":{{json .Config}}}'


class LifecycleError(RuntimeError):
    kind = 'invalid'


class DockerStateUnknown(LifecycleError):
    kind = 'unknown'


class SurvivingGate(LifecycleError):
    kind = 'live'


class StaleImage(LifecycleError):
    kind = 'stale'


def utc():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, value):
    temporary = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        with temporary.open('x', encoding='utf-8') as stream:
            json.dump(value, stream, indent=2)
            stream.write('\n')
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


class Docker:
    def __init__(self, root):
        self.root = root

    def capture(self, arguments):
        try:
            result = subprocess.run(['docker', '--context', 'default', *arguments],
                cwd=self.root, capture_output=True, text=True, timeout=15)
        except (OSError, subprocess.TimeoutExpired) as error:
            raise DockerStateUnknown('Docker state is unknown: ' + str(error)) from error
        if result.returncode != 0:
            raise DockerStateUnknown('Docker state is unknown: ' + result.stderr.strip())
        return result.stdout

    def inventory(self):
        ids = self.capture(['container', 'ls', '--all', '--quiet', '--no-trunc']).splitlines()
        if any(CID.fullmatch(value) is None for value in ids) or len(set(ids)) != len(ids):
            raise DockerStateUnknown('Docker returns invalid or duplicate container identities')
        if not ids:
            return []
        output = self.capture(['container', 'inspect', '--format', INSPECT, *ids])
        try:
            rows = [json.loads(line) for line in output.splitlines()]
            if ({row['id'] for row in rows} != set(ids) or len(rows) != len(ids)
                    or any(type(row['running']) is not bool
                           or not isinstance(row['mounts'], list)
                           or row['labels'] is not None and not isinstance(row['labels'], dict)
                           or type(row['status']) is not str
                           or type(row['restart']) is not str
                           or any(not isinstance(mount, dict)
                                  or type(mount.get('Source', '')) is not str
                                  or type(mount.get('Destination', '')) is not str
                                  for mount in row['mounts']) for row in rows)):
                raise ValueError('incomplete Docker inspection')
        except (ValueError, TypeError, KeyError) as error:
            raise DockerStateUnknown('Docker state is unknown: invalid inspection') from error
        return rows

    def image_identity(self, image):
        """Read the image ID and its build-input label from one inspection."""
        try:
            value = json.loads(self.capture(['image', 'inspect', '--format', IMAGE_INSPECT, image]))
            identity, labels = value['id'], value['config'].get('Labels')
            if (type(identity) is not str or IMAGE.fullmatch(identity) is None
                    or labels is not None and not isinstance(labels, dict)):
                raise ValueError('invalid image identity')
            inputs = (labels or {}).get(image_inputs.LABEL)
            if inputs is not None and type(inputs) is not str:
                raise ValueError('invalid image inputs label')
        except (ValueError, TypeError, KeyError, AttributeError) as error:
            raise DockerStateUnknown('Docker image identity is unknown') from error
        return identity, inputs

    def run(self, arguments):
        try:
            return subprocess.call(['docker', '--context', 'default', *arguments], cwd=self.root)
        except OSError as error:
            raise LifecycleError('the primary Docker client cannot start: ' + str(error)) from error


class Lifecycle:
    def __init__(self, root, docker=None):
        self.root = Path(root).resolve()
        try:
            self.directory = local_paths.owned(self.root / 'tmp/local-results/sh-elf-run', self.root).resolve()
        except ValueError as error:
            raise LifecycleError(str(error)) from error
        self.docker = docker or Docker(self.root)
        self.checkout = hashlib.sha256(str(self.root).encode()).hexdigest()
        self.inputs = image_inputs.fingerprint()

    @contextmanager
    def locked(self):
        self.directory.mkdir(parents=True, exist_ok=True)
        with (self.directory / 'host.lock').open('a') as stream:
            try:
                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as error:
                raise LifecycleError('another host gate owns this checkout') from error
            try:
                yield
            finally:
                fcntl.flock(stream.fileno(), fcntl.LOCK_UN)

    def owner(self):
        path = self.directory / 'owner.json'
        if not path.exists():
            value = dict(schema=1, owner=uuid.uuid4().hex)
            write_json(path, value)
            return value['owner']
        try:
            value = json.loads(path.read_text())
            if (set(value) != {'schema', 'owner'} or type(value['schema']) is not int
                    or value['schema'] != 1 or type(value['owner']) is not str
                    or TOKEN.fullmatch(value['owner']) is None):
                raise ValueError('invalid owner')
            return value['owner']
        except (OSError, ValueError, TypeError, KeyError) as error:
            raise LifecycleError('the saved container owner is invalid') from error

    def belongs(self, row, owner):
        labels = row['labels'] or {}
        if labels.get(OWNER_LABEL) == owner or labels.get(ROOT_LABEL) == self.checkout:
            return True
        # This also detects an old unlabeled gate or an erased local record.
        sources = {str(self.root), '/host_mnt' + str(self.root)}
        return any(mount.get('Type') == 'bind' and mount.get('Destination') == '/workspace'
                   and mount.get('Source', '').rstrip('/') in sources
                   for mount in row['mounts'])

    def check(self, owner):
        rows = [row for row in self.docker.inventory() if self.belongs(row, owner)]
        survivors = [row['id'] for row in rows if row['running']]
        if survivors:
            raise SurvivingGate('surviving gate containers: ' + ', '.join(survivors))
        unknown = [row['id'] for row in rows
                   if row['status'] not in ('exited', 'dead') or row['restart'] not in ('', 'no')]
        if unknown:
            raise DockerStateUnknown('unresolved gate containers: ' + ', '.join(unknown))
        return rows

    def execute(self, image, stock_timeout, arguments, *, skip_build=False):
        if stock_timeout not in (120, 240):
            raise LifecycleError('stock timeout must be 120 or 240')
        with self.locked():
            owner = self.owner()
            self.check(owner)
            token = uuid.uuid4().hex
            path = self.directory / (token + '.json')
            cidfile = self.directory / (token + '.cid')
            record = dict(schema=1, owner=owner, checkout=self.checkout, attempt=token,
                repository=str(self.root), image=image, image_inputs=self.inputs,
                stock_timeout=stock_timeout,
                arguments=list(arguments), cidfile=str(cidfile), started_utc=utc(), status='prepared')
            write_json(path, record)

            def save(status, **fields):
                record.update(status=status, observed_utc=utc(), **fields)
                write_json(path, record)

            try:
                if not skip_build:
                    code = self.docker.run(['build', '--tag', image,
                        '--label', image_inputs.LABEL + '=' + self.inputs,
                        str(self.root / 'tools/sh-elf-run')])
                    if code:
                        save('build-failed', client_exit_code=code)
                        return code
                # Recheck after a potentially long build, before creating a child.
                self.check(owner)
                image_id, inputs = self.docker.image_identity(image)
                if inputs != self.inputs:
                    raise StaleImage(f'{image} is stale: its inputs are {inputs or "unlabeled"}, '
                                     f'the current inputs are {self.inputs}')
                command = ['run', '--rm', '--pull=never', '--cidfile', str(cidfile),
                    '--name', 'vq-sh-elf-run-' + owner,
                    '--label', OWNER_LABEL + '=' + owner,
                    '--label', ROOT_LABEL + '=' + self.checkout,
                    '--label', RUN_LABEL + '=' + token,
                    '--env', 'VQ_SH_ELF_STOCK_TIMEOUT_SECONDS=' + str(stock_timeout),
                    '--mount', f'type=bind,src={self.root},dst=/workspace,readonly']
                for directory in local_paths.container_directories(self.root):
                    command += ['--mount', f'type=bind,src={directory},dst={directory},readonly']
                command += [image_id, *arguments]
                save('container-starting', docker_arguments=command, image_id=image_id)
                code = self.docker.run(command)
                save('client-finished', client_exit_code=code)
                retained = self.check(owner)
                cid = cidfile.read_text().strip() if cidfile.exists() else None
                if cid is not None and CID.fullmatch(cid) is None:
                    raise LifecycleError('the primary container identity file is invalid')
                if code == 0 and cid is None:
                    raise LifecycleError('zero client exit lacks the primary container identity')
                for row in retained:
                    labels = row['labels'] or {}
                    if row['id'] == cid and (labels.get(OWNER_LABEL) != owner
                            or labels.get(RUN_LABEL) != token):
                        raise DockerStateUnknown('the container identity belongs to another attempt')
                    if labels.get(RUN_LABEL) == token and row['id'] != cid:
                        raise DockerStateUnknown('the attempt and container identity disagree')
                save('succeeded' if code == 0 else 'failed', container_id=cid,
                     current_container_state=('missing-identity' if cid is None else
                         'stopped' if any(row['id'] == cid for row in retained) else 'absent'),
                     retained_stopped_containers=[row['id'] for row in retained], finished_utc=utc())
                runtime = {key: record[key] for key in ('schema', 'owner', 'checkout', 'attempt',
                    'image', 'image_id', 'image_inputs', 'arguments', 'client_exit_code', 'container_id',
                    'current_container_state', 'status')}
                print(RUNTIME_PREFIX + json.dumps(runtime, sort_keys=True), flush=True)
                return code
            except BaseException as error:
                save('unresolved', refusal_kind=getattr(error, 'kind', 'unknown'),
                     error=type(error).__name__ + ': ' + str(error))
                raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', required=True)
    parser.add_argument('--stock-timeout', required=True, type=int, choices=(120, 240))
    parser.add_argument('--skip-build', action='store_true')
    parser.add_argument('arguments', nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    arguments = args.arguments[1:] if args.arguments[:1] == ['--'] else args.arguments
    try:
        code = Lifecycle(ROOT).execute(args.image, args.stock_timeout, arguments,
                                      skip_build=args.skip_build)
        return 128 - code if code < 0 else code
    except (LifecycleError, OSError) as error:
        print('VQ_SH_ELF_LIFECYCLE status=REFUSE kind='
              + getattr(error, 'kind', 'unknown') + ' error=' + str(error), file=sys.stderr)
        return 3


if __name__ == '__main__':
    raise SystemExit(main())
