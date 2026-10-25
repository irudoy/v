"""Run the mandatory GNU gate once and qualify its exact original evidence."""

from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
from pathlib import Path
import sys
import traceback
import uuid

ROOT = Path(__file__).resolve().parents[2]
for path in (ROOT, ROOT / 'tools/kb/src'):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import acceptance
from docker_lifecycle import CID, IMAGE, TOKEN, RUNTIME_PREFIX, write_json
import process_record
from kb import (copy_evidence, copy_witness, local_paths, lock, repo, sid22_evidence,
                test_evidence)
from kb.prepare_evidence import PREFIX as PREPARED_PREFIX
from kb.test_contract import exact

PRIMARY = ['tools/sh-elf-run/run.sh', '--can-copy-witness', '--sid22-witness']
NATIVE_PRIMARY = [*PRIMARY, '--native-test-witness']
PRIMARY_LIMIT = 7200
TEST_LIMIT = 1200
VALIDATION_LIMIT = 1200
RECEIPTS = (copy_evidence.RECEIPT, sid22_evidence.RECEIPT, str(test_evidence.RECEIPT))


def utc():
    return datetime.now(timezone.utc).isoformat()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def receipt_bytes(root):
    values = {}
    for name in RECEIPTS:
        try:
            values[name] = (root / name).read_bytes()
        except FileNotFoundError:
            values[name] = None
    return values


def receipt_hashes(values):
    return {name: hashlib.sha256(data).hexdigest() if data is not None else None
            for name, data in values.items()}


def source_inputs(root):
    return {'GNU': copy_witness.provenance(root), 'TEST': test_evidence.producer_inputs(root),
            'TEST_scope_inputs': test_evidence.inputs(root)}


def metadata_source_transition(before, after, texts):
    """Require exactly the bytes written by the constrained normal writer."""
    expected = {namespace:dict(values) for namespace,values in before.items()}
    for path, text in texts.items():
        if text is None:
            raise ValueError('native proof publication removes no source input')
        name = path.as_posix()
        identity = hashlib.sha256(text.encode()).hexdigest()
        matched = False
        for values in expected.values():
            if name in values:
                values[name] = identity
                matched = True
        if not matched:
            raise ValueError('native publication writes a source outside the original input manifest')
    if after != expected:
        raise ValueError('native publication changes undeclared semantic or executable inputs')
    return expected


def publish_native_metadata(root, job, ops, before, seals):
    """Use all three prepared records with the ordinary constrained writer."""
    from kb import write
    references = {name:dict(path=local_paths.relative(output, root),
                           sha256=hashlib.sha256(data).hexdigest())
                  for name, (_, output, data) in zip(RECEIPTS, seals)}
    if len(references) != 3 or len(seals) != 3:
        raise ValueError('native metadata publication requires all three independently prepared records')
    with copy_evidence.prepared_publication(root, references):
        change, texts = write.apply(ops, root, log=lambda value:print(value, file=sys.stderr, flush=True),
                                   metadata_only=True, archive_before=job / 'native-preimages')
    after = source_inputs(root)
    expected = metadata_source_transition(before, after, texts)
    write_json(job / 'source-inputs-after-native-publication.json', after)
    write_json(job / 'native-publication.json', dict(metadata_only=True,
        prepared_records=references, operations=change.lines,
        files={path.as_posix():hashlib.sha256(text.encode()).hexdigest() for path,text in texts.items()},
        original_source_map='source-inputs.json',
        resulting_source_map='source-inputs-after-native-publication.json'))
    return expected


def test_command(candidate, *, native_profiles=False):
    command = ['uv', 'run', 'pytest', '-vv', '--tb=long', '--durations=0',
            '--junitxml=' + str(candidate.parent / 'TEST.xml'),
            '--basetemp=' + str(candidate.parent / 'TEST-work')]
    if native_profiles:
        from kb import test_cases, test_primary
        command += [case.nodeid for case in test_cases.ordered()]
        command += [test_primary.COPY_OPTION + '=' + str(candidate.parent / 'CAN-prepared.json'),
                    test_primary.SID22_OPTION + '=' + str(candidate.parent / 'SID22-prepared.json')]
    else:
        command.append(test_evidence.NODEID)
    return [*command, '--kb-test-candidate=' + str(candidate)]


def prepare_command(protocol, paths, output, candidate):
    command = ['uv', 'run', 'python', '-m', 'kb.prepare_evidence', protocol,
               '--process', str(paths[0]), '--stdout', str(paths[1]), '--stderr', str(paths[2]),
               '--output', str(output)]
    if protocol == 'TEST':
        command += ['--candidate', str(candidate)]
    return command


def prepared(root, job, protocol, paths, candidate):
    output = job / (protocol + '-prepared.json')
    named = tuple(root / local_paths.relative(path, root) for path in paths.paths)
    validation = original(root, job, 'validate-' + protocol,
                          prepare_command(protocol, named, output, candidate), VALIDATION_LIMIT)
    lines = [line for line in validation.streams[0].decode().splitlines() if line.startswith(PREPARED_PREFIX)]
    data = output.read_bytes()
    identity = hashlib.sha256(data).hexdigest()
    expected = PREPARED_PREFIX + 'protocol=' + protocol + ' sha256=' + identity
    if lines != [expected]:
        raise ValueError('the independent preparation output is not bound to its original terminal')
    record = json.loads(data)
    expected_terminal = {**paths.record,
        'stdout': local_paths.relative(paths.paths[1], root),
        'stderr': local_paths.relative(paths.paths[2], root)}
    if (type(record) is not dict or record.get('process_path') != local_paths.relative(paths.paths[0], root)
            or record.get('process_sha256') != hashlib.sha256(paths.process_bytes).hexdigest()
            or not exact(record.get('terminal'), expected_terminal)):
        raise ValueError('the prepared record names a different original process or stream')
    native = record.get('native_model')
    if type(native) is not str or len(native) != 64 or any(char not in '0123456789abcdef' for char in native):
        raise ValueError('the prepared record lacks its independently validated native identity')
    return record, {'process': local_paths.relative(validation.paths[0], root),
                    'process_sha256': hashlib.sha256(validation.process_bytes).hexdigest(),
                    'output_sha256': identity}, (validation, output, data)


@contextmanager
def serialized(root):
    directory = local_paths.owned(root / 'tmp/local-results/sh-elf-run', root).resolve()
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / 'qualification.lock').open('a') as stream:
        try:
            fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise ValueError('another qualification owns this checkout') from error
        try:
            yield
        finally:
            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)


def original(root, job, name, command, bound):
    paths = process_record.run(root, job, name, command, bound)
    result = process_record.snapshot(paths)
    process_record.require_success(result.record)
    return result


def runtime_record(text, root, *, command=None):
    rows = [json.loads(line[len(RUNTIME_PREFIX):]) for line in text.splitlines()
            if line.startswith(RUNTIME_PREFIX)]
    if len(rows) != 1:
        raise ValueError('the original primary stream lacks its unique container terminal')
    value = rows[0]
    if (type(value['schema']) is not int or value['schema'] != 1
            or value['checkout'] != hashlib.sha256(str(root.resolve()).encode()).hexdigest()
            or value['arguments'] != (PRIMARY if command is None else command)[1:]
            or value['status'] != 'succeeded'
            or type(value['client_exit_code']) is not int or value['client_exit_code'] != 0
            or value['current_container_state'] not in ('absent', 'stopped')
            or type(value['image']) is not str or not value['image']
            or any(type(value[key]) is not str or expression.fullmatch(value[key]) is None
                   for key, expression in (('image_id', IMAGE), ('container_id', CID),
                                            ('owner', TOKEN), ('attempt', TOKEN)))):
        raise ValueError('the original primary container/runtime binding is invalid')
    return value


def run(root=ROOT, *, native_profiles=False, native_publication_batch=None):
    if type(native_profiles) is not bool:
        raise ValueError('qualification requires an explicit native TEST mode')
    if native_publication_batch is not None and not native_profiles:
        raise ValueError('native metadata publication requires the complete native TEST mode')
    root = Path(root).resolve()
    with serialized(root):
        job = (root / 'tmp/local-results/sh-elf-run').resolve() / ('qualification-' + uuid.uuid4().hex)
        job.mkdir()
        primary_command = NATIVE_PRIMARY if native_profiles else PRIMARY
        state = {'schema': 1, 'job': local_paths.relative(job, root),
                 'started_utc': utc(), 'status': 'prepared', 'primary_command': primary_command,
                 'native_TEST_profiles': native_profiles,
                 'primary_limit_seconds': PRIMARY_LIMIT, 'TEST_limit_seconds': TEST_LIMIT,
                 'validation_limit_seconds': VALIDATION_LIMIT}
        write_json(job / 'state.json', state)
        try:
            publication_ops = None
            if native_publication_batch is not None:
                from kb import write
                source = local_paths.owned(native_publication_batch, root)
                batch = source.read_bytes()
                batch_path = job / 'native-publication-batch.toml'
                batch_path.write_bytes(batch)
                publication_ops = write.read_batch(batch_path)
                write.require_publication_operations(publication_ops)
                state['native_publication_batch_sha256'] = hashlib.sha256(batch).hexdigest()
                write_json(job / 'state.json', state)
            before = source_inputs(root)
            write_json(job / 'source-inputs.json', before)
            saved = receipt_bytes(root)
            prior = receipt_hashes(saved)
            for name, data in saved.items():
                if data is not None:
                    destination = job / 'prior-receipts' / Path(name).relative_to('.kb')
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    destination.write_bytes(data)
            write_json(job / 'prior-receipts.json', prior)
            primary = original(root, job, 'GNU', list(primary_command), PRIMARY_LIMIT)
            primary_text = primary.streams[0].decode()
            stages = acceptance.check_stages(primary_text, acceptance.registered())
            runtime = (runtime_record(primary_text, root, command=primary_command) if native_profiles
                       else runtime_record(primary_text, root))
            write_json(job / 'runtime.json', runtime)
            state.update(status='GNU-complete', GNU_process=local_paths.relative(primary.paths[0], root),
                         GNU_process_sha256=hashlib.sha256(primary.process_bytes).hexdigest(), stage_count=len(stages),
                         runtime_sha256=sha(job / 'runtime.json'))
            write_json(job / 'state.json', state)
            candidate = job / 'TEST-candidate.json'
            records, validations, seals = [], {}, []
            if native_profiles:
                for protocol in ('CAN', 'SID22'):
                    record, terminal, seal = prepared(root, job, protocol, primary, candidate)
                    records.append(record)
                    validations[protocol] = terminal
                    seals.append(seal)
                if source_inputs(root) != before:
                    raise ValueError('qualification sources change before the common TEST cohort')
            command = (test_command(candidate, native_profiles=True) if native_profiles
                       else test_command(candidate))
            tested = original(root, job, 'TEST', command, TEST_LIMIT)
            # Execution-time source changes cannot be hidden by later fresh receipts.
            if source_inputs(root) != before:
                raise ValueError('qualification source inputs change during execution')
            # Each native validator owns a separate process, model and cache lifetime.
            protocols = ('TEST',) if native_profiles else ('CAN', 'SID22', 'TEST')
            for protocol in protocols:
                record, terminal, seal = prepared(root, job, protocol,
                                             tested if protocol == 'TEST' else primary, candidate)
                records.append(record)
                validations[protocol] = terminal
                seals.append(seal)
            if len({record['native_model'] for record in records}) != 1:
                raise ValueError('independent preparations name different native snapshots')

            def unchanged():
                for capture in (primary, tested, *(seal[0] for seal in seals)):
                    process_record.require_unchanged(capture)
                if any(output.read_bytes() != data for _, output, data in seals):
                    raise ValueError('an independently prepared output changes after validation')

            final_inputs = before
            if publication_ops is not None:
                if source_inputs(root) != before or receipt_hashes(receipt_bytes(root)) != prior:
                    raise ValueError('qualification inputs or prior receipts change before native publication')
                unchanged()
                state.update(status='publishing-native-metadata', validations=validations)
                write_json(job / 'state.json', state)
                final_inputs = publish_native_metadata(root, job, publication_ops, before, seals)
                state['native_publication'] = 'native-publication.json'
                state['native_publication_sha256'] = sha(job / 'native-publication.json')
                state['source_inputs_after_native_publication_sha256'] = sha(
                    job / 'source-inputs-after-native-publication.json')
                write_json(job / 'state.json', state)

            with lock.held(root):
                if source_inputs(root) != final_inputs:
                    raise ValueError('qualification inputs change before publication')
                if receipt_hashes(receipt_bytes(root)) != prior:
                    raise ValueError('another publication changes the prior receipts')
                unchanged()
                # All evidence is independently validated before any receipt changes.
                state.update(status='publishing', validations=validations)
                state['published_receipts'] = []
                write_json(job / 'state.json', state)
                for name, record in zip(RECEIPTS, records):
                    copy_evidence.publish(root / name, record)
                    state['published_receipts'].append(name)
                    write_json(job / 'state.json', state)
                published = {name: sha(root / name) for name in RECEIPTS}
                if any(json.loads((root / name).read_bytes()) != record
                       for name, record in zip(RECEIPTS, records)):
                    raise ValueError('qualified receipt readback disagrees')
                if source_inputs(root) != final_inputs:
                    raise ValueError('qualification inputs change during publication')
                unchanged()
            state.update(status='passed', finished_utc=utc(),
                TEST_process=local_paths.relative(tested.paths[0], root),
                TEST_process_sha256=hashlib.sha256(tested.process_bytes).hexdigest(),
                receipts=published, validations=validations,
                source_inputs_sha256=sha(job / 'source-inputs.json'))
            write_json(job / 'state.json', state)
            print('VQ_SH_ELF_QUALIFIED status=PASS job=' + state['job'], flush=True)
            return state
        except BaseException as error:
            state.update(status='failed', finished_utc=utc(),
                         error=type(error).__name__ + ': ' + str(error))
            write_json(job / 'state.json', state)
            raise


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-test-profiles', action='store_true',
                        help='qualify the complete explicit native TEST catalog in the shared gate')
    parser.add_argument('--native-publication-batch',
                        help='publish only exact registered proof/review metadata after all records validate')
    args = parser.parse_args(argv)
    try:
        if args.native_test_profiles and args.native_publication_batch is not None:
            run(native_profiles=True, native_publication_batch=args.native_publication_batch)
        elif args.native_test_profiles:
            run(native_profiles=True)
        elif args.native_publication_batch is not None:
            parser.error('--native-publication-batch requires --native-test-profiles')
        else:
            run()
    except (OSError, ValueError, RuntimeError, repo.KbError):
        traceback.print_exc()
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
