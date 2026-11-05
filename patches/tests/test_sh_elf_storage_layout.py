"""Storage intersections fail before execution, including uninitialized sections."""
import struct
from pathlib import Path
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/sh-elf-run'))
from elf_storage_layout import ELFStorageError,require_separate_storage

RAM=0x01000000


def image(section=(0x110000,4,1,2),load=(0x110000,0x110000,4,4)):
    data=bytearray(max(512,256+section[1]))
    data[:16]=b'\x7fELF\x01\x02\x01'+bytes(9)
    struct.pack_into('>HHIIIIIHHHHHH',data,16,2,42,1,0x110000,52,84,0,52,32,1,40,2,0)
    virtual,physical,file_size,memory_size=load
    struct.pack_into('>IIIIIIII',data,52,1,256,virtual,physical,file_size,memory_size,7,4)
    address,size,kind,permissions=section
    struct.pack_into('>IIIIIIIIII',data,124,0,kind,permissions,address,256,size,0,0,4,0)
    return data


def check(tmp_path,data):
    path=tmp_path/'harness.elf';path.write_bytes(data)
    return require_separate_storage(path,((RAM,65536),))


@pytest.mark.parametrize('begin,size',[(RAM-1,2),(RAM,1),(RAM+65535,1),(RAM+65535,2),(RAM-1,65538)])
@pytest.mark.parametrize('kind',[1,8])
def test_allocated_data_and_bss_intersections(tmp_path,begin,size,kind):
    with pytest.raises(ELFStorageError,match='ALLOC.*intersects'):
        check(tmp_path,image(section=(begin,size,kind,2)))


@pytest.mark.parametrize('begin,size',[(RAM-1,2),(RAM,1),(RAM+65535,1),(RAM+65535,2),(RAM-1,65538)])
@pytest.mark.parametrize('address_kind',['virtual','physical'])
def test_load_memory_intersections(tmp_path,begin,size,address_kind):
    addresses=(begin,0x110000) if address_kind=='virtual' else (0x110000,begin)
    with pytest.raises(ELFStorageError,match='LOAD '+address_kind+'.*intersects'):
        check(tmp_path,image(load=(*addresses,0,size)))


@pytest.mark.parametrize('begin,size',[(RAM-4,4),(RAM+65536,4),(RAM,0)])
def test_exact_adjacency_and_empty_storage_pass(tmp_path,begin,size):
    assert check(tmp_path,image(section=(begin,size,8,2),load=(begin,begin,0,size)))=={'allocated_sections':1,'load_segments':1}


def test_nonallocated_debug_address_can_intersect(tmp_path):
    data=image();struct.pack_into('>H',data,48,3)
    struct.pack_into('>IIIIIIIIII',data,164,0,1,0,RAM,256,4,0,0,1,0)
    assert check(tmp_path,data)=={'allocated_sections':1,'load_segments':1}


@pytest.mark.parametrize('mutation',[
    lambda d:d.__setitem__(4,2),lambda d:d.__setitem__(5,1),
    lambda d:struct.pack_into('>H',d,18,3),lambda d:struct.pack_into('>H',d,16,1),
    lambda d:struct.pack_into('>H',d,40,0),lambda d:struct.pack_into('>H',d,42,31),
    lambda d:struct.pack_into('>H',d,44,0),lambda d:struct.pack_into('>H',d,46,39),
    lambda d:struct.pack_into('>H',d,48,0),lambda d:struct.pack_into('>I',d,28,500),
    lambda d:struct.pack_into('>I',d,32,500),lambda d:struct.pack_into('>I',d,68,5),
    lambda d:struct.pack_into('>I',d,56,510),lambda d:struct.pack_into('>I',d,140,510),
    lambda d:struct.pack_into('>I',d,136,0xffffffff),
    lambda d:struct.pack_into('>I',d,60,0xffffffff),
    lambda d:struct.pack_into('>I',d,64,0xffffffff),
    lambda d:struct.pack_into('>I',d,52,0),lambda d:struct.pack_into('>I',d,132,0),
])
def test_malformed_or_missing_storage_fails_closed(tmp_path,mutation):
    data=image();mutation(data)
    with pytest.raises(ELFStorageError):check(tmp_path,data)


@pytest.mark.parametrize('ranges',[(),((RAM,0),),((RAM,-1),),((-1,1),),((0xffffffff,2),),((True,1),)])
def test_invalid_declared_ram_fails(tmp_path,ranges):
    path=tmp_path/'harness.elf';path.write_bytes(image())
    with pytest.raises(ELFStorageError):require_separate_storage(path,ranges)


@pytest.mark.parametrize('route', ['map', 'rolling', 'telemetry', 'relocated-sh7058', 'relocated-sh7059', 'relocated-jk00c', 'relocated-jk00d', 'relocated-jk78c', 'relocated-1nd0a', 'relocated-1nd3b'])
@pytest.mark.parametrize('layout', ['data', 'bss', 'virtual', 'physical', 'before', 'after', 'malformed', 'missing'])
def test_feature_runners_inspect_the_linked_elf_before_simulator(tmp_path, monkeypatch, route, layout):
    import importlib
    from types import SimpleNamespace

    modules = {
        'map': 'verify_map_switching', 'rolling': 'verify_rolling_launch',
        'telemetry': 'verify_can_telemetry',
        'relocated-sh7058': 'verify_runtime_targets',
        'relocated-sh7059': 'verify_runtime_targets',
        'relocated-jk00c': 'verify_runtime_targets',
        'relocated-jk00d': 'verify_runtime_targets',
        'relocated-jk78c': 'verify_runtime_targets',
        'relocated-1nd0a': 'verify_runtime_targets',
        'relocated-1nd3b': 'verify_runtime_targets',
    }
    module = importlib.import_module(modules[route])
    base = module if route == 'map' else module.base_verifier
    marker = {
        'map': ('VQ_SH_ELF_MAP_SWITCHING status=PASS cases=132 selector=18 '
                'adapters=91 limiter=14 feedback=9 feedback_invocations=17 entries=12'),
        'rolling': 'VQ_SH_ELF_ROLLING_LAUNCH status=PASS controlled storage-only marker',
        'telemetry': getattr(module, 'REQUIRED_DYNAMIC_MARKER', ''),
    }.get(route, 'controlled relocated feature marker')
    overlap = layout in ('data', 'bss', 'virtual', 'physical')
    begin = RAM if overlap else RAM - 4 if layout == 'before' else RAM + 65536
    data = image(section=(begin, 4, 8 if layout == 'bss' else 1, 2))
    if layout in ('virtual', 'physical'):
        data = image(load=(RAM if layout == 'virtual' else 0x110000,
                           RAM if layout == 'physical' else 0x110000, 0, 4))
    if layout == 'malformed':
        data = b'not an ELF'
    calls = []
    linked = []

    def command(args, **options):
        calls.append((args, options))
        if args[0] == base.GCC:
            output = Path(args[args.index('-o') + 1])
            linked.append(output)
            if layout != 'missing':
                output.write_bytes(data)
        return SimpleNamespace(stdout=marker + '\n')

    monkeypatch.setattr(base, 'run_command', command)

    class StorageAccepted(Exception):
        pass

    if route in ('map', 'rolling', 'telemetry', 'relocated-jk00c', 'relocated-jk00d', 'relocated-jk78c', 'relocated-1nd0a', 'relocated-1nd3b'):
        def after_storage(*args, **kwargs):
            raise StorageAccepted
        monkeypatch.setattr(base, '_invoke_trace_bindings', after_storage)

    def execute():
        if route in ('relocated-jk00c', 'relocated-jk00d', 'relocated-jk78c', 'relocated-1nd0a', 'relocated-1nd3b'):
            rom = route.rsplit('-', 1)[1].upper()
            keys = base.PC_COVERAGE_UNITS + base.ADAPTER_COVERAGE_UNITS
            if rom in ('JK00C', 'JK00D'):
                keys += ('secondary_cvtc_adapter',)
            elif rom in ('1ND0A', '1ND3B'):
                keys += ('ignition_state_adapter',)
            size = 0x180000 if rom in ('1ND0A', '1ND3B') else 0x100000
            map_layout = SimpleNamespace(assembly_unit_by_key={
                key: SimpleNamespace(code_regions=()) for key in keys}, code_region_by_key={})
            target = SimpleNamespace(rom=rom, stock_image=SimpleNamespace(data=bytes(size)),
                                     map_layout=map_layout)
            parsed = {key: SimpleNamespace(statements=()) for key in keys}
            source = tmp_path / 'harness.c'
            source.write_text('controlled storage-only fixture')
            return module._compile_and_run(target, 'map-switching', source, tmp_path / 'rom.o',
                [tmp_path / 'invoke.o'], tmp_path, marker, map_parsed=parsed,
                fixture=bytes(size), composed_image=bytes(size))
        if route.startswith('relocated-'):
            size = 0x180000 if route.endswith('sh7059') else 0x100000
            target = SimpleNamespace(rom='CONTROLLED', stock_image=SimpleNamespace(data=bytes(size)))
            return module._compile_and_run(target, 'feature', tmp_path / 'harness.c',
                tmp_path / 'rom.o', [tmp_path / 'invoke.o'], tmp_path, marker)
        if route == 'map':
            parsed = {key: SimpleNamespace(statements=())
                      for key in module.PC_COVERAGE_UNITS + module.ADAPTER_COVERAGE_UNITS}
            return module.build_and_run_dynamic_harness(
                b'controlled fixture', tmp_path, parsed_by_unit=parsed,
                composed_image=b'controlled fixture', layout=SimpleNamespace(
                    assembly_unit_by_key={key: SimpleNamespace(code_regions=()) for key in parsed},
                    code_region_by_key={}))
        if route == 'rolling':
            regions = {key: SimpleNamespace(entry=index, span=SimpleNamespace(start=index, end=index))
                       for index, key in enumerate(module.COVERAGE_REGIONS)}
            return module.build_and_run_dynamic_harness(
                b'controlled fixture', tmp_path,
                parsed_by_unit={key: SimpleNamespace(statements=(), labels={})
                                for key in module.COVERAGE_UNITS},
                composed_image=b'controlled fixture',
                rolling_layout=SimpleNamespace(code_region_by_key=regions))
        if route == 'telemetry':
            return module.build_and_run_dynamic_harness(
                b'controlled fixture', tmp_path, parsed_by_unit={key: SimpleNamespace(statements=()) for key in module.CAN_COVERAGE_UNITS},
                composed_image=b'controlled fixture', layout=SimpleNamespace())
        return module.build_and_run_dynamic_harness(b'controlled fixture', tmp_path)

    if overlap or layout in ('malformed', 'missing'):
        with pytest.raises(module.VerificationError, match='ELF storage separation'):
            execute()
        assert base.RUN not in [args[0] for args, _ in calls]
    elif route in ('map', 'rolling', 'telemetry', 'relocated-jk00c', 'relocated-jk00d', 'relocated-jk78c', 'relocated-1nd0a', 'relocated-1nd3b'):
        # Reach the next real stage after accepting ELF storage, before RUN.
        with pytest.raises(StorageAccepted):
            execute()
        assert base.RUN not in [args[0] for args, _ in calls]
    else:
        assert execute() == marker
        args, options = calls[-1]
        assert args == [base.RUN, f'--memory-region={RAM:#x},64k', linked[0]]
        assert options == {'timeout': 120 if route == 'map' else 180}
    assert len(linked) == 1
    assert next(options for args, options in calls if args[0] == base.GCC) == {'timeout': 120}
