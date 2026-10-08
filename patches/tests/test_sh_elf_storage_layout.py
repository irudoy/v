"""Storage intersections fail before execution, including uninitialized sections."""
import struct
from pathlib import Path
import subprocess
import sys
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'tools/sh-elf-run'))
from elf_storage_layout import ELFStorageError,require_separate_storage

RAM=0x01000000


def test_stock_verifier_loads_without_prior_import_path_changes(tmp_path):
    verifier=Path(__file__).resolve().parents[2]/'tools/sh-elf-run/verify_stock_code.py'
    script='''import importlib.util, sys
spec=importlib.util.spec_from_file_location("isolated_stock_verifier",sys.argv[1])
module=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=module
spec.loader.exec_module(module)
assert callable(module.require_separate_storage)
assert module.ELFStorageError.__module__=="elf_storage_layout"
'''
    result=subprocess.run([sys.executable,'-I','-c',script,str(verifier)],
        cwd=tmp_path,text=True,capture_output=True,timeout=30)
    assert result.returncode==0,result.stderr


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


@pytest.mark.parametrize('layout',["data","bss","virtual","physical","before","after"])
def test_primary_stock_runner_checks_linked_elf_before_simulator(tmp_path,monkeypatch,layout):
    from types import SimpleNamespace
    from tools.kb.tests import test_injection_start_delay_chain as publication
    stock=publication.stock_module()
    region=next(row for row in stock.REGIONS if row.key=='jk08a-fuel-compensation')
    overlap=layout not in ('before','after')
    begin=RAM if overlap else (RAM-4 if layout=='before' else RAM+65536)
    data=image(section=(begin,4,8 if layout=='bss' else 1,2))
    if layout in ('virtual','physical'):
        data=image(load=(RAM if layout=='virtual' else 0x110000,RAM if layout=='physical' else 0x110000,0,4))
    calls=[]
    marker=f'VQ_SH_ELF_STOCK_CODE status=PASS region={region.key} cases={region.cases}'
    def command(args,**kwargs):
        calls.append((args[0],kwargs))
        if args[0]==stock.base_verifier.GCC:
            Path(args[args.index('-o')+1]).write_bytes(data)
        return SimpleNamespace(stdout=marker+'\n')
    monkeypatch.setattr(stock,'stock_image',lambda rom:b'\0'*4)
    monkeypatch.setattr(stock,'require_reconstruction',lambda *args:301)
    monkeypatch.setattr(stock,'build_fixture',lambda *args:b'\0'*4)
    monkeypatch.setattr(stock,'harness_defines',lambda *args:{})
    monkeypatch.setattr(stock.base_verifier,'run_command',command)
    if overlap:
        with pytest.raises(stock.VerificationError,match='ELF storage separation.*intersects'):
            stock.run_region(region,tmp_path/'invoke.o',tmp_path)
        assert stock.base_verifier.RUN not in [cmd for cmd,_ in calls]
    else:
        assert stock.run_region(region,tmp_path/'invoke.o',tmp_path)==301
        assert calls[-1]==(stock.base_verifier.RUN,{'timeout':120})
    assert next(options for cmd,options in calls if cmd==stock.base_verifier.GCC)=={'timeout':120}
