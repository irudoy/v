"""Patch-only orchestration, dependency boundaries and literal-consumer fixtures."""

import importlib
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import pytest


ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def driver(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'tools/sh-elf-run'))
    return importlib.import_module('verify_map_switching')


@pytest.fixture
def consumers(driver):
    return importlib.import_module('verify_ignition_consumers')


@pytest.fixture
def pipeline(driver, monkeypatch, tmp_path):
    events = []
    monkeypatch.setattr(driver, 'require_toolchain_version', lambda: ('simulator', 'gcc'))
    monkeypatch.setattr(driver.layout_model, 'load_layout', lambda: SimpleNamespace(assembly_units=()))
    monkeypatch.setattr(driver.assembly_model, 'validate_assembly_sources', lambda layout: {})
    monkeypatch.setattr(driver, 'assemble_all_units', lambda *args, **kwargs: {})
    audit = SimpleNamespace(instructions=3, delayed_transfers=5, pc_relative_references=7,
                           direct_branches=11, indirect_transfers=13)
    monkeypatch.setattr(driver.assembly_model, 'validate_instruction_semantics', lambda *args: audit)
    monkeypatch.setattr(driver, 'require_composition', lambda *args: SimpleNamespace(sha256='composition', data=b''))
    monkeypatch.setattr(driver, 'verify_fuel_cut_consumer_binding',
                        lambda *args: events.append('fuel_cut_binding'))
    monkeypatch.setattr(driver, 'verify_throttle_scalar_consumer_binding',
                        lambda *args: events.append('throttle_scalar_binding'))
    monkeypatch.setattr(driver, 'build_dynamic_fixture', lambda *args: (b'', 0, 0, ()))
    monkeypatch.setattr(driver, 'build_and_run_dynamic_harness', lambda *args, **kwargs: 'CONTROLLED_MAP_PASS')
    monkeypatch.setattr(driver, 'verify_delay_slot_incident', lambda *args: 'controlled signal')
    temporary = driver.tempfile.TemporaryDirectory
    monkeypatch.setattr(driver.tempfile, 'TemporaryDirectory',
        lambda **kwargs: temporary(dir=tmp_path, **kwargs))

    def invoke(name, **kwargs):
        events.append(name)
        if name == 'verify_runtime_targets':
            return [dict(dynamic_cases=31)]
        return dict(audit=SimpleNamespace(instructions=17), dynamic_cases=19)

    for name in ('verify_rolling_launch', 'verify_can_telemetry', 'verify_runtime_targets'):
        monkeypatch.setitem(sys.modules, name, SimpleNamespace(verify=lambda name=name, **kw: invoke(name, **kw)))
    return driver, events


def test_default_gate_runs_each_patch_stage_without_stock_or_receipt_modules(pipeline, capsys):
    driver, events = pipeline
    driver.verify()
    report = capsys.readouterr().out
    execution = importlib.import_module('execution_report')
    assert [(row['start']['kind'], row['start']['name'])
            for row in execution.read(report, require_complete=True)] == [
        ('pipeline', 'toolchain'), ('pipeline', 'reconstruction_fixture'),
        ('pipeline', 'map_switching'), ('pipeline', 'delay_slot_probe'),
        ('pipeline', 'rolling_launch'), ('pipeline', 'can_telemetry'),
        ('pipeline', 'relocated_runtime_targets'),
    ]
    assert events == ['fuel_cut_binding', 'throttle_scalar_binding', 'verify_rolling_launch', 'verify_can_telemetry', 'verify_runtime_targets']
    assert 'VQ_SH_ELF_VERIFY status=PASS' in report and 'stock_code_' not in report


def test_failed_fuel_cut_binding_prevents_execution(pipeline, monkeypatch, capsys):
    driver, events = pipeline

    def fail(*args):
        raise driver.VerificationError('controlled fuel-cut byte mismatch')

    monkeypatch.setattr(driver, 'verify_fuel_cut_consumer_binding', fail)
    assert driver.main([]) == 1
    assert events == []
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in capsys.readouterr().out


def test_failed_throttle_scalar_binding_prevents_execution(pipeline, monkeypatch, capsys):
    driver, events = pipeline

    def fail(*args):
        raise driver.VerificationError('controlled throttle scalar byte mismatch')

    monkeypatch.setattr(driver, 'verify_throttle_scalar_consumer_binding', fail)
    assert driver.main([]) == 1
    assert events == ['fuel_cut_binding']
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in capsys.readouterr().out


@pytest.mark.parametrize('stage', ('verify_rolling_launch', 'verify_can_telemetry', 'verify_runtime_targets'))
def test_any_failed_patch_stage_prevents_the_gate_pass(pipeline, stage, monkeypatch, capsys):
    driver, _ = pipeline

    def fail(**kwargs):
        raise ValueError('controlled execution failure')

    monkeypatch.setattr(sys.modules[stage], 'verify', fail)
    assert driver.main([]) == 1
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in capsys.readouterr().out


@pytest.mark.parametrize('option', ('--can-copy-witness', '--sid22-witness', '--native-test-witness',
                                  '--can-copy-early', '--coherent-copy-early', '--injection-copy-early'))
def test_patch_entrypoint_rejects_stock_proof_modes(driver, monkeypatch, option):
    monkeypatch.setattr(driver, 'verify', lambda **kwargs: pytest.fail('a removed mode executes no gate'))
    with pytest.raises(SystemExit) as error:
        driver.main([option])
    assert error.value.code == 2


@pytest.mark.parametrize('load_targets', (False, True))
def test_patch_gate_import_and_profile_loading_need_no_knowledge_package(load_targets):
    script = f'''
import importlib.abc,sys
sys.path[:0]=[{str(ROOT)!r},{str(ROOT / 'tools/sh-elf-run')!r}]
class NoKnowledge(importlib.abc.MetaPathFinder):
 def find_spec(self,fullname,path=None,target=None):
  if fullname=='kb' or fullname.startswith('kb.'):
   raise AssertionError('patch gate imports '+fullname)
sys.meta_path.insert(0,NoKnowledge())
import docker_lifecycle,verify_map_switching,verify_rolling_launch,verify_can_telemetry
import verify_runtime_targets,verify_ignition_consumers
if {load_targets!r}:
 targets=verify_runtime_targets.runtime_targets
 locks=targets.load_payload_locks()
 for rom in targets.RELOCATED_ROMS:
  target=targets.load_runtime_target(rom)
  assert target.rom==rom and rom in locks
assert not any(name=='kb' or name.startswith('kb.') for name in sys.modules)
assert 'verify_stock_code' not in sys.modules
'''
    result = subprocess.run([sys.executable, '-I', '-c', script], cwd=ROOT,
                            capture_output=True, text=True, timeout=60)
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.fixture
def small_fixture():
    image = bytes(range(64))
    baseline = bytearray(image)
    baseline[24:28] = bytes.fromhex('12345678')
    declared = dict(code=((8, 12),), pools=(24,),
                    windows=[dict(end=12, literal=24, adapter=0x12345678)])
    return declared, image, bytes(baseline)


def test_consumer_fixture_retains_instructions_and_real_composed_literal(consumers, small_fixture):
    declared, image, baseline = small_fixture
    fixture = consumers.prepare_fixture(declared, image, baseline, {40: bytes.fromhex('000b0009')})
    assert fixture[8:12] == image[8:12]
    assert fixture[24:28] == baseline[24:28]
    assert fixture[12:20] == consumers.RETURN_BOUNDARY
    assert fixture[:8] == image[:8] and fixture[28:40] == image[28:40]


@pytest.mark.parametrize('fault', ('instruction', 'literal', 'short-image', 'return-overlap',
                                  'stub-code', 'stub-pool', 'stub-outside'))
def test_consumer_fixture_refuses_a_changed_operand_or_overlapping_stub(consumers, small_fixture, fault):
    declared, image, baseline = small_fixture
    baseline = bytearray(baseline)
    stubs = {40: b'\x00\x0b\x00\x09'}
    if fault == 'instruction': baseline[8] ^= 1
    elif fault == 'literal': baseline[24] ^= 1
    elif fault == 'short-image': baseline = baseline[:16]
    elif fault == 'return-overlap': declared['code'] = ((8, 12), (16, 18))
    elif fault == 'stub-code': stubs = {8: stubs[40]}
    elif fault == 'stub-pool': stubs = {24: stubs[40]}
    else: stubs = {64: stubs[40]}
    with pytest.raises(ValueError):
        consumers.prepare_fixture(declared, image, baseline, stubs)


@pytest.mark.parametrize('fault', (None, 'instruction', 'pool', 'truncated'))
def test_independent_consumer_reconstruction_checks_each_code_and_pool_span(
        consumers, small_fixture, tmp_path, monkeypatch, fault):
    declared, image, _ = small_fixture
    raw = bytearray(image[8:28])
    if fault == 'instruction': raw[0] ^= 1
    elif fault == 'pool': raw[16] ^= 1
    elif fault == 'truncated': raw = raw[:2]

    def command(args, **kwargs):
        if args[0] == consumers.base.OBJCOPY:
            Path(args[-1]).write_bytes(raw)

    monkeypatch.setattr(consumers.base, 'run_command', command)
    if fault is None:
        consumers.require_reconstruction(declared, image, tmp_path, tmp_path / 'source.s')
    else:
        with pytest.raises(ValueError, match='reconstruction differs'):
            consumers.require_reconstruction(declared, image, tmp_path, tmp_path / 'source.s')


@pytest.mark.parametrize('value', ('', '0', '121', '-1', 'true'))
def test_consumer_execution_refuses_an_unbounded_or_unknown_timeout(consumers, monkeypatch, value):
    monkeypatch.setenv('VQ_SH_ELF_STOCK_TIMEOUT_SECONDS', value)
    with pytest.raises(ValueError): consumers.execution_timeout()


@pytest.mark.parametrize('value', ('120', '240'))
def test_consumer_execution_preserves_the_supported_timeout_contract(consumers, monkeypatch, value):
    monkeypatch.setenv('VQ_SH_ELF_STOCK_TIMEOUT_SECONDS', value)
    assert consumers.execution_timeout() == int(value)


@pytest.fixture
def consumer_process(consumers, small_fixture, monkeypatch, tmp_path):
    declared, image, baseline = small_fixture
    image_end = max(consumers.contract.LOOKUP, consumers.contract.STATE_LOOKUP) + 64
    image, baseline = image.ljust(image_end, b'\0'), baseline.ljust(image_end, b'\0')
    source_dir = tmp_path / 'sources'
    source_dir.mkdir()
    for name in consumers.SOURCES:
        (source_dir / name).write_bytes(name.encode())
    monkeypatch.setattr(consumers, 'TOOL_DIR', source_dir)
    monkeypatch.setattr(consumers, 'declaration', lambda target: declared)
    monkeypatch.setattr(consumers, 'render_header', lambda value: 'controlled input header\n')
    monkeypatch.setattr(consumers, 'require_reconstruction', lambda *args: None)
    monkeypatch.setattr(consumers, 'assemble_callee', lambda *args: bytes.fromhex('000b0009'))
    monkeypatch.setattr(consumers, 'require_separate_storage', lambda *args: None)
    state = SimpleNamespace(fault=None, commands=[])
    marker = (f"VQ_SH_ELF_IGNITION_LITERAL_CONSUMERS status=PASS "
              f"cases={len(declared['windows']) * len(consumers.SELECTORS) * len(consumers.INPUTS)} "
              f"windows={len(declared['windows'])}")

    def command(args, **kwargs):
        state.commands.append(args)
        if args[0] == consumers.base.GCC:
            assert '-DVQ_PATCH_GATE=1' in args
            Path(args[args.index('-o') + 1]).write_bytes(b'controlled executable')
        if args[0] != consumers.base.RUN:
            return SimpleNamespace(stdout='')
        if state.fault == 'gnu-failure':
            raise consumers.base.VerificationError('controlled simulator failure')
        if state.fault == 'fixture':
            (Path(args[-1]).parent / 'fixture.bin').write_bytes(b'changed fixture')
        elif state.fault == 'executable': Path(args[-1]).write_bytes(b'changed executable')
        elif state.fault == 'source': (source_dir / consumers.SOURCES[0]).write_bytes(b'changed source')
        elif state.fault == 'consumed-source':
            (Path(args[-1]).parent / 'consumed' / consumers.SOURCES[0]).write_bytes(b'changed private source')
        stdout = marker + '\n'
        if state.fault == 'missing-marker': stdout = ''
        elif state.fault == 'duplicate-marker': stdout += stdout
        elif state.fault == 'raw-evidence-stream': stdout = 'raw observation\n' + stdout
        return SimpleNamespace(stdout=stdout)

    monkeypatch.setattr(consumers.base, 'run_command', command)
    target = SimpleNamespace(stock_image=SimpleNamespace(data=image))
    return state, target, baseline, tmp_path, marker


def test_consumer_process_requires_a_complete_patch_only_terminal(consumers, consumer_process):
    state, target, baseline, directory, marker = consumer_process
    assert consumers.verify(target, baseline, directory) == marker
    assert any(args[0] == consumers.base.RUN for args in state.commands)


@pytest.mark.parametrize('fault', ('gnu-failure', 'fixture', 'executable', 'source', 'consumed-source',
                                  'missing-marker', 'duplicate-marker', 'raw-evidence-stream'))
def test_consumer_process_refuses_failed_or_changed_execution(consumers, consumer_process, fault):
    state, target, baseline, directory, _ = consumer_process
    state.fault = fault
    with pytest.raises((ValueError, consumers.base.VerificationError)):
        consumers.verify(target, baseline, directory)
