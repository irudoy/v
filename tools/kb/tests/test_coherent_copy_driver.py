"""Real feedback orchestration with only the GNU execution boundary controlled."""
import importlib
from pathlib import Path

import pytest
from kb import coherent_copy_matrix as matrix, coherent_copy_evidence as proof, repo

@pytest.fixture
def driver(monkeypatch):
    monkeypatch.syspath_prepend(str(repo.ROOT/'tools/sh-elf-run'))
    main=importlib.import_module('verify_map_switching')
    capture=importlib.import_module('coherent_snapshot_copy')
    from kb import copy_witness,sid22_witness
    def forbidden(*args,**kwargs):raise AssertionError('feedback cannot execute or finalize the full pipeline')
    monkeypatch.setattr(main,'verify',forbidden)
    for module in (copy_witness,sid22_witness):
        monkeypatch.setattr(module,'begin',forbidden);monkeypatch.setattr(module,'finish',forbidden)
    return main,capture

def test_main_routes_coherent_feedback_without_full_producer(driver,monkeypatch,capsys):
    main,capture=driver;calls=[]
    monkeypatch.setattr(capture,'verify_early',lambda:calls.append('coherent'))
    assert main.main(['--coherent-copy-early'])==0
    assert calls==['coherent'] and 'kb-copy-candidate' not in capsys.readouterr().out

def test_real_feedback_loop_keeps_every_private_source_and_window(driver,monkeypatch,capsys):
    main,capture=driver;calls=[];private=[]
    def execute(index,snapshot,directory,*,early):
        assert early
        window=matrix.WINDOWS[index];row=snapshot['descriptor']['window'][index]
        assert row['call']==window.call
        for name,data in snapshot['consumed'].items():
            source=snapshot['source_dir'].parents[1]/name
            assert source.read_bytes()==data==(repo.ROOT/name).read_bytes()
        private.append(snapshot['source_dir']);calls.append((index,window.call,directory.name))
        return dict(observations=[dict(controlled_only=True)]*len(proof.early_indices(window)))
    monkeypatch.setattr(capture,'run_window',execute)
    assert main.main(['--coherent-copy-early'])==0
    assert calls==[(i,w.call,f'{w.call:08x}') for i,w in enumerate(matrix.WINDOWS)]
    assert len(set(private))==1
    output=capsys.readouterr()
    assert 'VQ_SH_ELF_COHERENT_COPY_SUBSET status=PASS cases=81 production=false' in output.out
    assert 'kb-copy-candidate' not in output.out and not output.err

def test_incomplete_feedback_has_no_success_terminal(driver,monkeypatch,capsys):
    main,capture=driver
    monkeypatch.setattr(capture,'run_window',lambda *args,**kwargs:dict(observations=[]))
    assert main.main(['--coherent-copy-early'])==1
    output=capsys.readouterr()
    assert 'omits required observations' in output.err
    assert 'VQ_SH_ELF_COHERENT_COPY_SUBSET status=PASS' not in output.out

def test_mid_loop_failure_keeps_original_error_and_refuses_completion(driver,monkeypatch,capsys):
    main,capture=driver;calls=[]
    def execute(index,*args,**kwargs):
        calls.append(index)
        if index==3:raise ValueError('controlled coherent execution failure')
        return dict(observations=[None]*len(proof.early_indices(matrix.WINDOWS[index])))
    monkeypatch.setattr(capture,'run_window',execute)
    assert main.main(['--coherent-copy-early'])==1
    assert calls==[0,1,2,3]
    output=capsys.readouterr()
    assert 'controlled coherent execution failure' in output.err
    assert 'VQ_SH_ELF_COHERENT_COPY_SUBSET status=PASS' not in output.out

@pytest.mark.parametrize('other',['--can-copy-early','--can-copy-witness','--injection-copy-early','--sid22-early','--sid22-witness'])
def test_feedback_rejects_mixed_execution_modes(driver,other):
    main,_=driver
    with pytest.raises(SystemExit) as result:main.main(['--coherent-copy-early',other])
    assert result.value.code==2

def test_readme_case_counts_are_bound_to_executable_inputs():
    text=(repo.ROOT/'tools/sh-elf-run/README.md').read_text()
    count=sum(len(matrix.cases(window)) for window in matrix.WINDOWS)
    early=sum(len(proof.early_indices(window)) for window in matrix.WINDOWS)
    assert f'The matrix declares {count} cases and the fixed feedback selects {early} cases across\n{len(matrix.WINDOWS)} callers.' in text


@pytest.fixture
def primary(driver,monkeypatch):
    main,capture=driver
    stock=importlib.import_module('verify_stock_code')
    can=importlib.import_module('can_latch_copy');calls=[]
    monkeypatch.setattr(can,'toolchain',lambda:dict(controlled_only=True))
    def execute(index,copied,directory,*,early):
        assert early is False
        calls.append(index)
        return dict(region=f'jk08a-coherent-{matrix.WINDOWS[index].call:08x}',instructions=index+1)
    monkeypatch.setattr(capture,'run_window',execute)
    selected=[region for region in stock.REGIONS if region.key.startswith('jk08a-coherent-')]
    assert len(selected)==15
    return stock,capture,selected,calls


def test_primary_stock_loop_retains_all_windows_and_private_sources(primary,tmp_path):
    stock,capture,selected,calls=primary;packet={}
    for i,region in enumerate(selected):
        assert stock.run_region(region,None,tmp_path,copy_capture=packet)==i+1
    assert calls==list(range(15))
    assert [row['region'] for row in packet['coherent']['windows']]==[region.key for region in selected]
    assert packet['coherent']['schema']==1 and packet['coherent']['key']==proof.KEY
    assert set(packet['coherent']['consumed'])==set(proof.consumed_names(proof.descriptor()))
    assert all(bytes.fromhex(value)==(repo.ROOT/name).read_bytes()
               for name,value in packet['coherent']['consumed'].items())


@pytest.mark.parametrize('order',[(0,2),(0,0),(1,)])
def test_primary_stock_loop_rejects_missing_duplicate_or_reordered_windows(primary,tmp_path,order):
    stock,capture,selected,calls=primary;packet={}
    with pytest.raises(ValueError,match='omits, duplicates, reorders or changes inputs'):
        for index in order:stock.run_region(selected[index],None,tmp_path,copy_capture=packet)
    assert calls==([0] if order[0]==0 else [])


def test_primary_stock_loop_rejects_changed_case_contract_before_execution(primary,tmp_path):
    from dataclasses import replace
    stock,capture,selected,calls=primary
    with pytest.raises(ValueError,match='complete bounded contract'):
        stock.run_region(replace(selected[0],cases=selected[0].cases-1),None,tmp_path,copy_capture={})
    assert calls==[]


def test_primary_stock_loop_rejects_changed_private_inputs_before_execution(primary,tmp_path,monkeypatch):
    stock,capture,selected,calls=primary;packet={}
    stock.run_region(selected[0],None,tmp_path,copy_capture=packet)
    original=capture.snapshot
    def changed(root,directory):
        value=original(root,directory)
        value['consumed']={**value['consumed'],capture.HARNESS:b'changed private source'}
        return value
    monkeypatch.setattr(capture,'snapshot',changed)
    with pytest.raises(ValueError,match='omits, duplicates, reorders or changes inputs'):
        stock.run_region(selected[1],None,tmp_path,copy_capture=packet)
    assert calls==[0]
