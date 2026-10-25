"""Real witness routing with controlled execution boundaries, not firmware proofs."""

import importlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from kb import ordinary_access_registry as ordinary


ROOT = Path(__file__).resolve().parents[2]
CAN = 'jk08a-can-latch-copy'
SID = 'jk08a-sid22-pointer-read'
SNAPSHOT = 'jk08a-injection-snapshot'


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
    width = importlib.import_module('width_view_capture')
    state.width_captures = []
    def width_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == width.REGION:
            raise ValueError('controlled execution failure: ' + width.REGION)
        captured.update(region=width.REGION, controlled_only=True)
        state.width_captures.append(captured)
        return 'CONTROLLED_WIDTH_VIEW_BOUNDARY'
    monkeypatch.setattr(width, 'run', width_execution)
    byte_surface = importlib.import_module('byte_surface_capture')
    state.byte_surface_captures = []
    def byte_surface_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == byte_surface.REGION:
            raise ValueError('controlled execution failure: ' + byte_surface.REGION)
        captured.update(region=byte_surface.REGION, controlled_only=True)
        state.byte_surface_captures.append(captured)
        return 'CONTROLLED_BYTE_SURFACE_BOUNDARY'
    monkeypatch.setattr(byte_surface, 'run', byte_surface_execution)
    exhaust_target = importlib.import_module('exhaust_target_capture')
    state.exhaust_target_captures = []
    def exhaust_target_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == exhaust_target.REGION:
            raise ValueError('controlled execution failure: ' + exhaust_target.REGION)
        captured.update(region=exhaust_target.REGION, controlled_only=True)
        state.exhaust_target_captures.append(captured)
        return 'CONTROLLED_EXHAUST_TARGET_BOUNDARY'
    monkeypatch.setattr(exhaust_target, 'run', exhaust_target_execution)
    bfs_path = importlib.import_module('bfs_path_capture')
    state.bfs_path_captures = []
    def bfs_path_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == bfs_path.REGION:
            raise ValueError('controlled execution failure: ' + bfs_path.REGION)
        captured.update(region=bfs_path.REGION, controlled_only=True)
        state.bfs_path_captures.append(captured)
        return 'CONTROLLED_BFS_PATH_BOUNDARY'
    monkeypatch.setattr(bfs_path, 'run', bfs_path_execution)
    ignition_diagnostic = importlib.import_module('ignition_diagnostic_capture')
    state.ignition_diagnostic_captures = []
    def ignition_diagnostic_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == ignition_diagnostic.REGION:
            raise ValueError('controlled execution failure: ' + ignition_diagnostic.REGION)
        captured.update(region=ignition_diagnostic.REGION, controlled_only=True)
        state.ignition_diagnostic_captures.append(captured)
        return 'CONTROLLED_IGNITION_DIAGNOSTIC_BOUNDARY'
    monkeypatch.setattr(ignition_diagnostic, 'run', ignition_diagnostic_execution)
    publication_inhibit = importlib.import_module('publication_inhibit_capture')
    state.publication_inhibit_captures = []
    def publication_inhibit_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == publication_inhibit.REGION:
            raise ValueError('controlled execution failure: ' + publication_inhibit.REGION)
        captured.update(region=publication_inhibit.REGION, controlled_only=True)
        state.publication_inhibit_captures.append(captured)
        return 'CONTROLLED_PUBLICATION_INHIBIT_BOUNDARY'
    monkeypatch.setattr(publication_inhibit, 'run', publication_inhibit_execution)
    division_callees = importlib.import_module('division_callees_capture')
    state.division_callees_captures = []
    def division_callees_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == division_callees.REGION:
            raise ValueError('controlled execution failure: ' + division_callees.REGION)
        captured.update(region=division_callees.REGION, controlled_only=True)
        state.division_callees_captures.append(captured)
        return 'CONTROLLED_DIVISION_CALLEES_BOUNDARY'
    monkeypatch.setattr(division_callees, 'run', division_callees_execution)
    timing_division = importlib.import_module('timing_division_capture')
    state.timing_division_captures = []
    def timing_division_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == timing_division.REGION:
            raise ValueError('controlled execution failure: ' + timing_division.REGION)
        captured.update(region=timing_division.REGION, controlled_only=True)
        state.timing_division_captures.append(captured)
        return 'CONTROLLED_TIMING_DIVISION_BOUNDARY'
    monkeypatch.setattr(timing_division, 'run', timing_division_execution)
    timing_tail = importlib.import_module('timing_tail_capture')
    state.timing_tail_captures = []
    def timing_tail_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == timing_tail.REGION:
            raise ValueError('controlled execution failure: ' + timing_tail.REGION)
        captured.update(region=timing_tail.REGION, controlled_only=True)
        state.timing_tail_captures.append(captured)
        return 'CONTROLLED_TIMING_TAIL_BOUNDARY'
    monkeypatch.setattr(timing_tail, 'run', timing_tail_execution)
    timing_denominator = importlib.import_module('timing_denominator_capture')
    state.timing_denominator_captures = []
    def timing_denominator_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == timing_denominator.REGION:
            raise ValueError('controlled execution failure: ' + timing_denominator.REGION)
        captured.update(region=timing_denominator.REGION, controlled_only=True)
        state.timing_denominator_captures.append(captured)
        return 'CONTROLLED_TIMING_DENOMINATOR_BOUNDARY'
    monkeypatch.setattr(timing_denominator, 'run', timing_denominator_execution)
    signed_curve = importlib.import_module('signed_curve_capture')
    state.signed_curve_captures = []
    def signed_curve_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == signed_curve.REGION:
            raise ValueError('controlled execution failure: ' + signed_curve.REGION)
        captured.update(region=signed_curve.REGION, controlled_only=True)
        state.signed_curve_captures.append(captured)
        return 'CONTROLLED_SIGNED_CURVE_BOUNDARY'
    monkeypatch.setattr(signed_curve, 'run', signed_curve_execution)
    fine_gopher = importlib.import_module('fine_gopher_capture')
    state.fine_gopher_captures = []
    def fine_gopher_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == fine_gopher.REGION:
            raise ValueError('controlled execution failure: ' + fine_gopher.REGION)
        captured.update(region=fine_gopher.REGION, controlled_only=True)
        state.fine_gopher_captures.append(captured)
        return 'CONTROLLED_FINE_GOPHER_BOUNDARY'
    monkeypatch.setattr(fine_gopher, 'run', fine_gopher_execution)
    independent_leopard = importlib.import_module('independent_leopard_capture')
    state.independent_leopard_captures = []
    def independent_leopard_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == independent_leopard.REGION:
            raise ValueError('controlled execution failure: ' + independent_leopard.REGION)
        captured.update(region=independent_leopard.REGION, controlled_only=True)
        state.independent_leopard_captures.append(captured)
        return 'CONTROLLED_INDEPENDENT_LEOPARD_BOUNDARY'
    monkeypatch.setattr(independent_leopard, 'run', independent_leopard_execution)
    uptight_duck = importlib.import_module('uptight_duck_capture')
    state.uptight_duck_captures = []
    def uptight_duck_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == uptight_duck.REGION:
            raise ValueError('controlled execution failure: ' + uptight_duck.REGION)
        captured.update(region=uptight_duck.REGION, controlled_only=True)
        state.uptight_duck_captures.append(captured)
        return 'CONTROLLED_UPTIGHT_DUCK_BOUNDARY'
    monkeypatch.setattr(uptight_duck, 'run', uptight_duck_execution)
    apc_reset_offset = importlib.import_module('apc_reset_offset_capture')
    state.apc_reset_offset_captures = []
    def apc_reset_offset_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == apc_reset_offset.REGION:
            raise ValueError('controlled execution failure: ' + apc_reset_offset.REGION)
        captured.update(region=apc_reset_offset.REGION, controlled_only=True)
        state.apc_reset_offset_captures.append(captured)
        return 'CONTROLLED_APC_RESET_OFFSET_BOUNDARY'
    monkeypatch.setattr(apc_reset_offset, 'run', apc_reset_offset_execution)
    quiet_cat = importlib.import_module('quiet_cat_capture')
    state.quiet_cat_captures = []
    def quiet_cat_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == quiet_cat.REGION:
            raise ValueError('controlled execution failure: ' + quiet_cat.REGION)
        captured.update(region=quiet_cat.REGION, controlled_only=True)
        state.quiet_cat_captures.append(captured)
        return 'CONTROLLED_QUIET_CAT_BOUNDARY'
    monkeypatch.setattr(quiet_cat, 'run', quiet_cat_execution)
    sexy_tamarin = importlib.import_module('sexy_tamarin_capture')
    state.sexy_tamarin_captures = []
    def sexy_tamarin_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == sexy_tamarin.REGION:
            raise ValueError('controlled execution failure: ' + sexy_tamarin.REGION)
        captured.update(region=sexy_tamarin.REGION, controlled_only=True)
        state.sexy_tamarin_captures.append(captured)
        return 'CONTROLLED_SEXY_TAMARIN_BOUNDARY'
    monkeypatch.setattr(sexy_tamarin, 'run', sexy_tamarin_execution)
    viridian_armadillo = importlib.import_module('viridian_armadillo_capture')
    state.viridian_armadillo_captures = []
    def viridian_armadillo_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == viridian_armadillo.REGION:
            raise ValueError('controlled execution failure: ' + viridian_armadillo.REGION)
        captured.update(region=viridian_armadillo.REGION, controlled_only=True)
        state.viridian_armadillo_captures.append(captured)
        return 'CONTROLLED_VIRIDIAN_ARMADILLO_BOUNDARY'
    monkeypatch.setattr(viridian_armadillo, 'run', viridian_armadillo_execution)
    rugged_gerbil = importlib.import_module('rugged_gerbil_capture')
    state.rugged_gerbil_captures = []
    def rugged_gerbil_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == rugged_gerbil.REGION:
            raise ValueError('controlled execution failure: ' + rugged_gerbil.REGION)
        captured.update(region=rugged_gerbil.REGION, controlled_only=True)
        state.rugged_gerbil_captures.append(captured)
        return 'CONTROLLED_RUGGED_GERBIL_BOUNDARY'
    monkeypatch.setattr(rugged_gerbil, 'run', rugged_gerbil_execution)
    spirited_hamster = importlib.import_module('spirited_hamster_capture')
    state.spirited_hamster_captures = []
    def spirited_hamster_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == spirited_hamster.REGION:
            raise ValueError('controlled execution failure: ' + spirited_hamster.REGION)
        captured.update(region=spirited_hamster.REGION, controlled_only=True)
        state.spirited_hamster_captures.append(captured)
        return 'CONTROLLED_SPIRITED_HAMSTER_BOUNDARY'
    monkeypatch.setattr(spirited_hamster, 'run', spirited_hamster_execution)
    arrogant_catfish = importlib.import_module('arrogant_catfish_capture')
    state.arrogant_catfish_captures = []
    def arrogant_catfish_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == arrogant_catfish.REGION:
            raise ValueError('controlled execution failure: ' + arrogant_catfish.REGION)
        captured.update(region=arrogant_catfish.REGION, controlled_only=True)
        state.arrogant_catfish_captures.append(captured)
        return 'CONTROLLED_ARROGANT_CATFISH_BOUNDARY'
    monkeypatch.setattr(arrogant_catfish, 'run', arrogant_catfish_execution)
    scaled_publication = importlib.import_module('scaled_publication_capture')
    state.scaled_publication_captures = []
    def scaled_publication_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == scaled_publication.REGION:
            raise ValueError('controlled execution failure: ' + scaled_publication.REGION)
        captured.update(region=scaled_publication.REGION, controlled_only=True)
        state.scaled_publication_captures.append(captured)
        return 'CONTROLLED_SCALED_PUBLICATION_BOUNDARY'
    monkeypatch.setattr(scaled_publication, 'run', scaled_publication_execution)
    normalization = importlib.import_module('normalization_capture')
    state.normalization_captures = []
    def normalization_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == normalization.REGION:
            raise ValueError('controlled execution failure: ' + normalization.REGION)
        captured.update(region=normalization.REGION, controlled_only=True)
        state.normalization_captures.append(captured)
        return 'CONTROLLED_NORMALIZATION_BOUNDARY'
    monkeypatch.setattr(normalization, 'run', normalization_execution)
    differential_curve = importlib.import_module('differential_curve_capture')
    state.differential_curve_captures = []
    def differential_curve_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == differential_curve.REGION:
            raise ValueError('controlled execution failure: ' + differential_curve.REGION)
        captured.update(region=differential_curve.REGION, controlled_only=True)
        state.differential_curve_captures.append(captured)
        return 'CONTROLLED_DIFFERENTIAL_CURVE_BOUNDARY'
    monkeypatch.setattr(differential_curve, 'run', differential_curve_execution)
    reciprocal_curves = importlib.import_module('reciprocal_curves_capture')
    state.reciprocal_curves_captures = []
    def reciprocal_curves_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == reciprocal_curves.REGION:
            raise ValueError('controlled execution failure: ' + reciprocal_curves.REGION)
        captured.update(region=reciprocal_curves.REGION, controlled_only=True)
        state.reciprocal_curves_captures.append(captured)
        return 'CONTROLLED_RECIPROCAL_CURVES_BOUNDARY'
    monkeypatch.setattr(reciprocal_curves, 'run', reciprocal_curves_execution)
    counter_threshold = importlib.import_module('counter_threshold_capture')
    state.counter_threshold_captures = []
    def counter_threshold_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == counter_threshold.REGION:
            raise ValueError('controlled execution failure: ' + counter_threshold.REGION)
        captured.update(region=counter_threshold.REGION, controlled_only=True)
        state.counter_threshold_captures.append(captured)
        return 'CONTROLLED_COUNTER_THRESHOLD_BOUNDARY'
    monkeypatch.setattr(counter_threshold, 'run', counter_threshold_execution)
    messy_roadrunner = importlib.import_module('messy_roadrunner_capture')
    state.messy_roadrunner_captures = []
    def messy_roadrunner_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == messy_roadrunner.REGION:
            raise ValueError('controlled execution failure: ' + messy_roadrunner.REGION)
        captured.update(region=messy_roadrunner.REGION, controlled_only=True)
        state.messy_roadrunner_captures.append(captured)
        return 'CONTROLLED_MESSY_ROADRUNNER_BOUNDARY'
    monkeypatch.setattr(messy_roadrunner, 'run', messy_roadrunner_execution)
    radical_capuchin = importlib.import_module('radical_capuchin_capture')
    state.radical_capuchin_captures = []
    def radical_capuchin_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == radical_capuchin.REGION:
            raise ValueError('controlled execution failure: ' + radical_capuchin.REGION)
        captured.update(region=radical_capuchin.REGION, controlled_only=True)
        state.radical_capuchin_captures.append(captured)
        return 'CONTROLLED_RADICAL_CAPUCHIN_BOUNDARY'
    monkeypatch.setattr(radical_capuchin, 'run', radical_capuchin_execution)
    adorable_llama = importlib.import_module('adorable_llama_capture')
    state.adorable_llama_captures = []
    def adorable_llama_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == adorable_llama.REGION:
            raise ValueError('controlled execution failure: ' + adorable_llama.REGION)
        captured.update(region=adorable_llama.REGION, controlled_only=True)
        state.adorable_llama_captures.append(captured)
        return 'CONTROLLED_ADORABLE_LLAMA_BOUNDARY'
    monkeypatch.setattr(adorable_llama, 'run', adorable_llama_execution)
    io_accesses = importlib.import_module('io_access_capture')
    state.io_access_captures = []
    def io_access_execution(target, directory, captured):
        assert target.rom == 'JK08A' and target.stock_image.data == b'controlled stock bytes'
        if state.fail_region == io_accesses.REGION:
            raise ValueError('controlled execution failure: ' + io_accesses.REGION)
        captured.update(region=io_accesses.REGION, controlled_only=True)
        state.io_access_captures.append(captured)
        return 'CONTROLLED_IO_ACCESS_BOUNDARY'
    monkeypatch.setattr(io_accesses, 'run', io_access_execution)
    state.ordinary_captures={component:[] for component,producer in ordinary.captures()}
    for component,producer_name in ordinary.captures():
        producer=importlib.import_module(producer_name)
        def ordinary_execution(target,directory,captured,component=component,producer=producer):
            assert target.rom=='JK08A' and target.stock_image.data==b'controlled stock bytes'
            if state.fail_region==producer.REGION:
                raise ValueError('controlled execution failure: '+producer.REGION)
            captured.update(region=producer.REGION,controlled_only=True)
            state.ordinary_captures[component].append(captured)
            return 'CONTROLLED_ORDINARY_ACCESS_BOUNDARY component='+component
        monkeypatch.setattr(producer,'run',ordinary_execution)
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

    snapshot = importlib.import_module('injection_snapshot_copy')
    def snapshot_execution(region, directory, *, capture=None):
        assert region.key == SNAPSHOT
        state.events.append(('execute', SNAPSHOT))
        if state.fail_region == SNAPSHOT:
            raise ValueError('controlled execution failure: ' + SNAPSHOT)
        if capture is not None:
            capture.update(region=SNAPSHOT, observations=[dict(lane='snapshot', observation=43)])
        return sum((end-start)//2 for start,end in region.code_spans)
    monkeypatch.setattr(snapshot, 'run_region', snapshot_execution)

    coherent = importlib.import_module('coherent_snapshot_copy')
    coherent_keys = [f'jk08a-coherent-{window.call:08x}' for window in coherent.matrix.WINDOWS]
    state.coherent_keys = coherent_keys
    def coherent_execution(index, captured, directory, *, early):
        assert not early
        key = coherent_keys[index]
        state.events.append(('execute', key))
        if state.fail_region == key:
            raise ValueError('controlled execution failure: ' + key)
        return dict(region=key, observations=[dict(lane='coherent', observation=47+index)],
            instructions=sum((end-start)//2 for start,end in regions[key].code_spans))
    monkeypatch.setattr(coherent, 'run_window', coherent_execution)

    def finish(label, candidate, capture, root):
        executions = [key for event, key in state.events if event == 'execute']
        if executions != state.expected:
            raise ValueError('controlled incomplete or duplicated stock loop')
        region, observation = (CAN, 37) if label == 'CAN' else (SID, 41)
        if (candidate != dict(controlled_lane=label) or capture.get('region') != region
                or capture.get('observations') != [dict(lane=label, observation=observation)]):
            raise ValueError('controlled missing or misrouted ' + label + ' capture')
        if label == 'CAN' and capture.get('snapshot') != dict(
                region=SNAPSHOT, observations=[dict(lane='snapshot', observation=43)]):
            raise ValueError('controlled missing or misrouted snapshot capture')
        if label == 'CAN' and capture.get('coherent', {}).get('windows') != [
                dict(region=key, observations=[dict(lane='coherent', observation=47+index)],
                    instructions=sum((end-start)//2 for start,end in regions[key].code_spans))
                for index,key in enumerate(coherent_keys)]:
            raise ValueError('controlled missing or misrouted coherent capture')
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
    assert len(pipeline.width_captures) == 1
    assert len(pipeline.byte_surface_captures) == 1
    assert len(pipeline.exhaust_target_captures) == 1
    assert len(pipeline.bfs_path_captures) == 1
    assert len(pipeline.ignition_diagnostic_captures) == 1
    assert len(pipeline.publication_inhibit_captures) == 1
    assert len(pipeline.division_callees_captures) == 1
    assert len(pipeline.timing_division_captures) == 1
    assert len(pipeline.timing_tail_captures) == 1
    assert len(pipeline.timing_denominator_captures) == 1
    assert len(pipeline.signed_curve_captures) == 1
    assert len(pipeline.fine_gopher_captures) == 1
    assert len(pipeline.independent_leopard_captures) == 1
    assert len(pipeline.uptight_duck_captures) == 1
    assert len(pipeline.apc_reset_offset_captures) == 1
    assert len(pipeline.quiet_cat_captures) == 1
    assert len(pipeline.sexy_tamarin_captures) == 1
    assert len(pipeline.viridian_armadillo_captures) == 1
    assert len(pipeline.rugged_gerbil_captures) == 1
    assert len(pipeline.spirited_hamster_captures) == 1
    assert len(pipeline.arrogant_catfish_captures) == 1
    assert len(pipeline.scaled_publication_captures) == 1
    assert len(pipeline.normalization_captures) == 1
    assert len(pipeline.differential_curve_captures) == 1
    assert len(pipeline.reciprocal_curves_captures) == 1
    assert len(pipeline.counter_threshold_captures) == 1
    assert len(pipeline.messy_roadrunner_captures) == 1
    assert len(pipeline.radical_capuchin_captures) == 1
    assert len(pipeline.adorable_llama_captures) == 1
    assert len(pipeline.io_access_captures) == 1
    assert set(pipeline.ordinary_captures)=={component for component,producer in ordinary.captures()}
    assert all(len(rows)==1 for rows in pipeline.ordinary_captures.values())
    if mode != 'ordinary':
        for component,rows in pipeline.ordinary_captures.items():
            assert pipeline.finishes['CAN'][component] is rows[0]
        assert pipeline.finishes['CAN']['width_views'] is pipeline.width_captures[0]
        assert pipeline.finishes['CAN']['byte_surface_paths'] is pipeline.byte_surface_captures[0]
        assert pipeline.finishes['CAN']['exhaust_target_paths'] is pipeline.exhaust_target_captures[0]
        assert pipeline.finishes['CAN']['bfs_paths'] is pipeline.bfs_path_captures[0]
        assert pipeline.finishes['CAN']['ignition_diagnostic_paths'] is pipeline.ignition_diagnostic_captures[0]
        assert pipeline.finishes['CAN']['publication_inhibit_paths'] is pipeline.publication_inhibit_captures[0]
        assert pipeline.finishes['CAN']['division_callees_paths'] is pipeline.division_callees_captures[0]
        assert pipeline.finishes['CAN']['timing_division_paths'] is pipeline.timing_division_captures[0]
        assert pipeline.finishes['CAN']['timing_tail_paths'] is pipeline.timing_tail_captures[0]
        assert pipeline.finishes['CAN']['timing_denominator_paths'] is pipeline.timing_denominator_captures[0]
        assert pipeline.finishes['CAN']['signed_curve_paths'] is pipeline.signed_curve_captures[0]
        assert pipeline.finishes['CAN']['fine_gopher_paths'] is pipeline.fine_gopher_captures[0]
        assert pipeline.finishes['CAN']['independent_leopard_paths'] is pipeline.independent_leopard_captures[0]
        assert pipeline.finishes['CAN']['uptight_duck_paths'] is pipeline.uptight_duck_captures[0]
        assert pipeline.finishes['CAN']['apc_reset_offset_paths'] is pipeline.apc_reset_offset_captures[0]
        assert pipeline.finishes['CAN']['quiet_cat_paths'] is pipeline.quiet_cat_captures[0]
        assert pipeline.finishes['CAN']['sexy_tamarin_paths'] is pipeline.sexy_tamarin_captures[0]
        assert pipeline.finishes['CAN']['viridian_armadillo_paths'] is pipeline.viridian_armadillo_captures[0]
        assert pipeline.finishes['CAN']['rugged_gerbil_paths'] is pipeline.rugged_gerbil_captures[0]
        assert pipeline.finishes['CAN']['spirited_hamster_paths'] is pipeline.spirited_hamster_captures[0]
        assert pipeline.finishes['CAN']['arrogant_catfish_paths'] is pipeline.arrogant_catfish_captures[0]
        assert pipeline.finishes['CAN']['scaled_publication_paths'] is pipeline.scaled_publication_captures[0]
        assert pipeline.finishes['CAN']['normalization_paths'] is pipeline.normalization_captures[0]
        assert pipeline.finishes['CAN']['differential_curve_paths'] is pipeline.differential_curve_captures[0]
        assert pipeline.finishes['CAN']['reciprocal_curves_paths'] is pipeline.reciprocal_curves_captures[0]
        assert pipeline.finishes['CAN']['counter_threshold_paths'] is pipeline.counter_threshold_captures[0]
        assert pipeline.finishes['CAN']['messy_roadrunner_paths'] is pipeline.messy_roadrunner_captures[0]
        assert pipeline.finishes['CAN']['radical_capuchin_paths'] is pipeline.radical_capuchin_captures[0]
        assert pipeline.finishes['CAN']['adorable_llama_paths'] is pipeline.adorable_llama_captures[0]
        assert pipeline.finishes['CAN']['io_access_paths'] is pipeline.io_access_captures[0]
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


@pytest.mark.parametrize('fault', ['drop-CAN', 'drop-SID22', 'swap', 'replace-CAN', 'alias', 'drop-coherent'])
def test_controlled_route_mutations_cannot_publish_a_candidate(
        pipeline, monkeypatch, capsys, fault):
    original = pipeline.stock.run_region

    def changed(region, invoke, directory, *, copy_capture=None, sid22_capture=None):
        if fault == 'drop-CAN': copy_capture = None
        elif fault == 'drop-SID22': sid22_capture = None
        elif fault == 'swap': copy_capture, sid22_capture = sid22_capture, copy_capture
        elif fault == 'replace-CAN': copy_capture = {}
        elif fault == 'alias': copy_capture = sid22_capture
        elif fault == 'drop-coherent' and region.key in pipeline.coherent_keys: copy_capture = None
        return original(region, invoke, directory,
            copy_capture=copy_capture, sid22_capture=sid22_capture)

    monkeypatch.setattr(pipeline.stock, 'run_region', changed)
    assert pipeline.driver.main(['--can-copy-witness', '--sid22-witness']) == 1
    output = capsys.readouterr()
    assert ('missing or misrouted' in output.err
            or 'coherent stock loop omits, duplicates, reorders or changes inputs' in output.err)
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


@pytest.mark.parametrize('lane', ['ordinary', 'CAN', 'SID22', 'snapshot'])
def test_region_failure_prevents_both_finalizers_and_candidates(pipeline, capsys, lane):
    pipeline.fail_region = (pipeline.expected[0] if lane == 'ordinary'
                            else CAN if lane == 'CAN' else SID if lane == 'SID22' else SNAPSHOT)
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


def test_width_view_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-width-views'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_byte_surface_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-byte-surface-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_exhaust_target_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-exhaust-target-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_bfs_path_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-bfs-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_ignition_diagnostic_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-ignition-diagnostic-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_publication_inhibit_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-publication-inhibit-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_division_callees_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-division-callees-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_timing_division_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-timing-division-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_sexy_tamarin_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-sexy-tamarin-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_viridian_armadillo_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-viridian-armadillo-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_rugged_gerbil_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-rugged-gerbil-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_spirited_hamster_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-spirited-hamster-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_arrogant_catfish_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-arrogant-catfish-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_scaled_publication_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-scaled-publication-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_normalization_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-normalization-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_differential_curve_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-differential-curve-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_reciprocal_curves_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-reciprocal-curves-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_counter_threshold_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-counter-threshold-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_messy_roadrunner_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-messy-roadrunner-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_radical_capuchin_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-radical-capuchin-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_adorable_llama_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-adorable-llama-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_io_access_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-io-access-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


@pytest.mark.parametrize('component,producer',ordinary.captures())
def test_each_registered_ordinary_capture_failure_prevents_the_complete_original_candidate(pipeline,capsys,component,producer):
    pipeline.fail_region=importlib.import_module(producer).REGION
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_quiet_cat_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-quiet-cat-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_apc_reset_offset_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-apc-reset-offset-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_uptight_duck_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-uptight-duck-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_independent_leopard_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-independent-leopard-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_fine_gopher_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-fine-gopher-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_signed_curve_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-signed-curve-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_timing_denominator_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-timing-denominator-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}


def test_timing_tail_failure_prevents_the_complete_original_candidate(pipeline,capsys):
    pipeline.fail_region='jk08a-timing-tail-paths'
    assert pipeline.driver.main(['--can-copy-witness','--sid22-witness'])!=0
    output=capsys.readouterr()
    assert candidates(output.out)==[]
    assert 'VQ_SH_ELF_VERIFY status=PASS' not in output.out
    assert pipeline.finishes=={}
