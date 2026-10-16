"""Real witness routing with controlled execution boundaries, not firmware proofs."""

import importlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[2]
CAN = 'jk08a-can-latch-copy'
SID = 'jk08a-sid22-pointer-read'


@pytest.fixture
def pipeline(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'tools/sh-elf-run'))
    driver = importlib.import_module('verify_map_switching')
    stock = importlib.import_module('verify_stock_code')
    from kb import copy_witness, sid22_witness

    assert stock.base_verifier is driver
    state = SimpleNamespace(driver=driver, stock=stock, events=[], commands=[],
        finishes={}, sid_receivers=[], fail_region=None, missing_marker=None,
        expected=[region.key for region in stock.REGIONS])
    assert state.expected.count(CAN) == state.expected.count(SID) == 1
    regions = {region.key: region for region in stock.REGIONS}

    # Keep all orchestration bodies real; unrelated executable groups and GNU
    # boundaries return distinguishable controlled outputs.
    monkeypatch.setattr(driver, 'require_toolchain_version',
        lambda: ('controlled simulator', 'controlled gcc'))
    monkeypatch.setattr(driver.layout_model, 'load_layout',
        lambda: SimpleNamespace(assembly_units=()))
    monkeypatch.setattr(driver.assembly_model, 'validate_assembly_sources', lambda layout: {})
    monkeypatch.setattr(driver, 'assemble_all_units', lambda *args, **kwargs: {})
    audit = SimpleNamespace(instructions=3, delayed_transfers=5, pc_relative_references=7,
        direct_branches=11, indirect_transfers=13)
    monkeypatch.setattr(driver.assembly_model, 'validate_instruction_semantics',
        lambda *args: audit)
    monkeypatch.setattr(driver, 'require_composition',
        lambda *args: SimpleNamespace(sha256='controlled composition'))
    monkeypatch.setattr(driver, 'build_dynamic_fixture', lambda *args: (b'', 0, 0, ()))
    monkeypatch.setattr(driver, 'build_and_run_dynamic_harness',
        lambda *args: 'CONTROLLED_DYNAMIC_BOUNDARY')
    monkeypatch.setattr(driver, 'verify_delay_slot_incident', lambda *args: 'controlled signal')
    for name, instructions, cases in (
            ('verify_rolling_launch', 17, 19), ('verify_can_telemetry', 23, 29)):
        module = importlib.import_module(name)
        result = dict(audit=SimpleNamespace(instructions=instructions), dynamic_cases=cases)
        monkeypatch.setattr(module, 'verify', lambda result=result, **kwargs: result)
    runtime = importlib.import_module('verify_runtime_targets')
    monkeypatch.setattr(runtime, 'verify', lambda **kwargs: [dict(dynamic_cases=31)])

    original_directory = driver.tempfile.TemporaryDirectory
    monkeypatch.setattr(driver.tempfile, 'TemporaryDirectory',
        lambda **kwargs: original_directory(dir=tmp_path, **kwargs))
    monkeypatch.setattr(stock, 'stock_image', lambda rom: b'controlled stock bytes')
    monkeypatch.setattr(stock, 'build_fixture',
        lambda region, image, **kwargs: ('controlled fixture ' + region.key).encode())
    monkeypatch.setattr(stock, 'harness_defines', lambda region, image: {})

    def reconstruct(region, image, directory, **kwargs):
        state.events.append(('reconstruct', region.key))
        if 'captured' in kwargs:
            kwargs['captured'].update(code=[dict(controlled_region=region.key)], pools=[])
        return sum((end - start) // 2 for start, end in region.code_spans)

    monkeypatch.setattr(stock, 'require_reconstruction', reconstruct)

    def separate(output, ranges):
        assert output.read_bytes().startswith(b'controlled ELF ')

    monkeypatch.setattr(stock, 'require_separate_storage', separate)
    can = stock.can_latch_copy
    monkeypatch.setattr(can, 'snapshot', lambda root, directory: dict(
        source_dir=tmp_path / 'controlled-can-sources',
        consumed={'controlled source': b'not stock instruction bytes'},
        cases=[dict(id='controlled CAN case')]))
    monkeypatch.setattr(can, 'boundary', lambda *args: b'controlled boundary')
    monkeypatch.setattr(can, 'toolchain', lambda: dict(controlled='not a qualified toolchain'))

    def observe(stdout, captured, *, early):
        assert not early
        state.events.append(('observe', CAN))
        return [dict(lane='CAN', observation=37)]

    monkeypatch.setattr(can, 'observe', observe)

    def command(argv, **kwargs):
        state.commands.append(argv)
        if argv[0] in (driver.AS, driver.GCC):
            output = Path(argv[argv.index('-o') + 1])
            output.write_bytes(b'controlled ELF ' + output.name.encode())
        elif argv[0] == driver.OBJCOPY:
            Path(argv[-1]).write_bytes(b'controlled object')
        elif argv[0] == driver.RUN:
            key = Path(argv[-1]).name.removesuffix('-harness.elf')
            assert key in regions and key != SID
            state.events.append(('execute', key))
            if state.fail_region == key:
                raise stock.VerificationError('controlled execution failure: ' + key)
            marker = (f'VQ_SH_ELF_STOCK_CODE status=PASS region={key} '
                      f'cases={regions[key].cases}')
            return SimpleNamespace(stdout='' if state.missing_marker == key else marker + '\n')
        else:
            raise AssertionError('unexpected external command: ' + str(argv))
        return SimpleNamespace(stdout='')

    monkeypatch.setattr(driver, 'run_command', command)

    def sid_execution(region, directory, *, capture=None):
        assert region.key == SID
        state.events.append(('execute', SID))
        state.sid_receivers.append(capture)
        if state.fail_region == SID:
            raise ValueError('controlled execution failure: ' + SID)
        if capture is not None:
            capture.update(region=SID, observations=[dict(lane='SID22', observation=41)])
        return sum((end - start) // 2 for start, end in region.code_spans)

    monkeypatch.setattr(stock.sid22_pointer_read, 'run_region', sid_execution)

    def finish(label, candidate, capture, root):
        executions = [key for event, key in state.events if event == 'execute']
        if executions != state.expected:
            raise ValueError('controlled incomplete or duplicated stock loop')
        region, observation = (CAN, 37) if label == 'CAN' else (SID, 41)
        if (candidate != dict(controlled_lane=label) or capture.get('region') != region
                or capture.get('observations') != [dict(lane=label, observation=observation)]):
            raise ValueError('controlled missing or misrouted ' + label + ' capture')
        state.finishes[label] = capture
        state.events.append(('finish', label))
        return dict(controlled_only=True, lane=label, capture=capture)

    for module, label in ((copy_witness, 'CAN'), (sid22_witness, 'SID22')):
        monkeypatch.setattr(module, 'begin',
            lambda root, label=label: dict(controlled_lane=label))
        monkeypatch.setattr(module, 'finish',
            lambda candidate, capture, root, label=label: finish(label, candidate, capture, root))
    return state


def candidates(stdout):
    from kb import copy_evidence, sid22_evidence
    prefixes = (copy_evidence.MARKER, sid22_evidence.MARKER)
    return [json.loads(line[len(prefix):]) for line in stdout.splitlines()
            for prefix in prefixes if line.startswith(prefix)]


@pytest.mark.parametrize('mode', ['ordinary', 'CAN', 'combined'])
def test_real_dispatch_and_stock_loop_preserve_witness_routing(pipeline, capsys, mode):
    args = [] if mode == 'ordinary' else ['--can-copy-witness']
    if mode == 'combined':
        args.append('--sid22-witness')
    assert pipeline.driver.main(args) == 0
    output = capsys.readouterr()
    assert not output.err
    assert [key for event, key in pipeline.events if event == 'execute'] == pipeline.expected
    packets = candidates(output.out)
    expected = [] if mode == 'ordinary' else ['CAN'] if mode == 'CAN' else ['SID22', 'CAN']
    assert [packet['lane'] for packet in packets] == expected
    assert all(packet['controlled_only'] is True for packet in packets)
    assert sum(line.startswith('VQ_SH_ELF_VERIFY status=PASS ')
               for line in output.out.splitlines()) == 1
    acceptance = importlib.import_module('acceptance')
    rows = acceptance.check_stages(output.out, pipeline.stock.REGIONS)
    assert all(row['finish']['elapsed_seconds'] >= 0 for row in rows)
    if mode == 'combined':
        assert pipeline.finishes['CAN'] is not pipeline.finishes['SID22']
        assert len(pipeline.sid_receivers) == 1
        assert pipeline.sid_receivers[0] is pipeline.finishes['SID22']
    else:
        assert pipeline.sid_receivers == [None]


@pytest.mark.parametrize('fault', ['drop-CAN', 'drop-SID22', 'swap', 'replace-CAN', 'alias'])
def test_controlled_route_mutations_cannot_publish_a_candidate(
        pipeline, monkeypatch, capsys, fault):
    original = pipeline.stock.run_region

    def changed(region, invoke, directory, *, copy_capture=None, sid22_capture=None):
        if fault == 'drop-CAN': copy_capture = None
        elif fault == 'drop-SID22': sid22_capture = None
        elif fault == 'swap': copy_capture, sid22_capture = sid22_capture, copy_capture
        elif fault == 'replace-CAN': copy_capture = {}
        elif fault == 'alias': copy_capture = sid22_capture
        return original(region, invoke, directory,
            copy_capture=copy_capture, sid22_capture=sid22_capture)

    monkeypatch.setattr(pipeline.stock, 'run_region', changed)
    assert pipeline.driver.main(['--can-copy-witness', '--sid22-witness']) == 1
    output = capsys.readouterr()
    assert 'missing or misrouted' in output.err
    assert candidates(output.out) == []


@pytest.mark.parametrize('fault', ['omitted', 'duplicated'])
def test_incomplete_or_duplicated_real_stock_loop_cannot_publish(
        pipeline, monkeypatch, capsys, fault):
    regions = pipeline.stock.REGIONS
    changed = tuple(region for region in regions if region.key != CAN)
    if fault == 'duplicated':
        changed = (*regions, next(region for region in regions if region.key == CAN))
    monkeypatch.setattr(pipeline.stock, 'REGIONS', changed)
    assert pipeline.driver.main(['--can-copy-witness', '--sid22-witness']) == 1
    output = capsys.readouterr()
    assert 'incomplete or duplicated' in output.err
    assert candidates(output.out) == []


@pytest.mark.parametrize('lane', ['ordinary', 'CAN', 'SID22'])
def test_region_failure_prevents_both_finalizers_and_candidates(pipeline, capsys, lane):
    pipeline.fail_region = (pipeline.expected[0] if lane == 'ordinary'
                            else CAN if lane == 'CAN' else SID)
    assert pipeline.driver.main(['--can-copy-witness', '--sid22-witness']) == 1
    output = capsys.readouterr()
    assert 'controlled execution failure' in output.err
    assert 'Traceback (most recent call last)' in output.err
    assert 'in run_region' in output.err
    assert pipeline.finishes == {}
    assert candidates(output.out) == []
    assert not any(line.startswith('VQ_SH_ELF_VERIFY status=PASS ')
                   for line in output.out.splitlines())
    report = importlib.import_module('execution_report')
    rows = report.read(output.out)
    assert rows[-1]['start']['name'] == pipeline.fail_region
    assert rows[-1]['finish']['status'] == 'failed'
    with pytest.raises(ValueError, match='unfinished or failed'):
        report.read(output.out, require_complete=True)


def test_zero_exit_without_region_marker_prevents_finalization(pipeline, capsys):
    pipeline.missing_marker = CAN
    assert pipeline.driver.main(['--can-copy-witness', '--sid22-witness']) == 1
    output = capsys.readouterr()
    assert 'zero exit without the exact PASS marker' in output.err
    assert pipeline.finishes == {}
    assert candidates(output.out) == []


def test_sid22_candidate_requires_the_can_primary_mode(pipeline, capsys):
    with pytest.raises(SystemExit) as error:
        pipeline.driver.main(['--sid22-witness'])
    assert error.value.code == 2
    output = capsys.readouterr()
    assert '--sid22-witness requires --can-copy-witness' in output.err
    assert pipeline.events == []
    assert pipeline.finishes == {}


@pytest.mark.parametrize('mode', ['CAN', 'SID22'])
def test_feedback_timing_cannot_satisfy_the_full_primary_stage_contract(
        pipeline, monkeypatch, capsys, mode):
    if mode == 'CAN':
        monkeypatch.setattr(pipeline.stock, 'verify_can_copy_early', lambda: None)
        args = ['--can-copy-early']
    else:
        monkeypatch.setattr(pipeline.stock.sid22_pointer_read, 'verify_early', lambda: None)
        args = ['--sid22-early']
    assert pipeline.driver.main(args) == 0
    output = capsys.readouterr()
    report = importlib.import_module('execution_report')
    rows = report.read(output.out, require_complete=True)
    assert len(rows) == 1 and rows[0]['start']['name'].startswith('feedback:')
    assert candidates(output.out) == []
    acceptance = importlib.import_module('acceptance')
    with pytest.raises(ValueError, match='complete primary registry order'):
        acceptance.check_stages(output.out, pipeline.stock.REGIONS)
    assert candidates(output.out) == []
