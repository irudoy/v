"""Declared numerical/import/include dependencies must reach real input bindings."""

from pathlib import Path

import pytest

from kb import ignition_literal_evidence, proof_adapter, proof_reuse, proof_sources, repo
from kb.test_stock_capture import tool


def _root(tmp_path):
    for name in ('pyproject.toml','uv.lock','Makefile','tools/kb/pyproject.toml'):
        path=tmp_path/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_text('')
    path=tmp_path/proof_sources.SOURCE;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes((repo.ROOT/proof_sources.SOURCE).read_bytes())
    return tmp_path


def _numerical(root):
    directory=root/'tools/sh-elf-run';directory.mkdir(parents=True,exist_ok=True)
    source=directory/'stock_coolant_conditional_model.py'
    source.write_text('from stock_injection_end_angle_model import State\n\n'
        'def case():\n    raise AssertionError("dependency discovery executes no numerical function")\n')
    dependency=directory/'stock_injection_end_angle_model.py'
    dependency.write_text('class State:\n    pass\n')
    return source.relative_to(root).as_posix(),dependency.relative_to(root).as_posix()


def test_static_import_closure_discovers_the_imported_numerical_source_without_loading_code(tmp_path):
    root=_root(tmp_path);source,dependency=_numerical(root)
    value=proof_sources.closure(root,[source])
    assert value['complete_declared_closure'] is True
    assert {source,dependency}<=set(value['files'])
    assert dependency in value['edges'][source]
    assert value['semantic_admission'] is False
    proof_sources.require_manifest(value,dict(value['files']),anchors=set(value['files']))


@pytest.mark.parametrize('fault',('missing-input','stale-input','missing-anchor'))
def test_numerical_dependency_cannot_disappear_from_execution_manifest_or_acceptance_anchors(tmp_path,fault):
    root=_root(tmp_path);source,dependency=_numerical(root)
    value=proof_sources.closure(root,[source]);inputs=dict(value['files']);anchors=set(inputs)
    if fault=='missing-input':inputs.pop(dependency)
    elif fault=='stale-input':inputs[dependency]='0'*64
    else:anchors.remove(dependency)
    with pytest.raises(ValueError,match='dependency'):
        proof_sources.require_manifest(value,inputs,anchors=anchors)


def test_missing_imported_numerical_file_is_an_unresolved_obligation(tmp_path):
    root=_root(tmp_path);source,dependency=_numerical(root);(root/dependency).unlink()
    value=proof_sources.closure(root,[source])
    assert value['complete_declared_closure'] is False
    assert any(row['reason']=='missing-local-import' for row in value['unresolved_edges'])
    with pytest.raises(ValueError,match='incomplete'):
        proof_sources.require_manifest(value,value['files'])


def test_private_generated_input_header_is_distinct_from_a_missing_persistent_include(tmp_path):
    root=_root(tmp_path);directory=root/'tools/sh-elf-run';directory.mkdir(parents=True,exist_ok=True)
    capture=directory/'sample_capture.py';capture.write_text('HEADER="sample-cases.h"\n')
    driver=directory/'harness-sample.c';driver.write_text('#include "sample-cases.h"\n')
    source=[path.relative_to(root).as_posix() for path in (capture,driver)]
    value=proof_sources.closure(root,source)
    assert value['complete_declared_closure'] is True
    assert value['generated_input_headers']==['tools/sh-elf-run/sample-cases.h']
    assert 'tools/sh-elf-run/sample-cases.h' not in value['files']
    driver.write_text('#include "missing-persistent.h"\n')
    broken=proof_sources.closure(root,source)
    assert broken['complete_declared_closure'] is False
    assert any(row.get('source')=='tools/sh-elf-run/missing-persistent.h' for row in broken['unresolved_edges'])


def test_dynamic_loader_requires_a_finite_declared_target_and_binds_every_target(tmp_path):
    root=_root(tmp_path);directory=root/'tools/sh-elf-run';directory.mkdir(parents=True,exist_ok=True)
    loader=directory/'loader.py';loader.write_text('from importlib import import_module\n'
        'def load(name):\n    return import_module(name)\n')
    target=directory/'target.py';target.write_text('raise AssertionError("source closure imports no target")\n')
    first,second=(path.relative_to(root).as_posix() for path in (loader,target))
    assert proof_sources.closure(root,[first])['complete_declared_closure'] is False
    value=proof_sources.closure(root,[first],declared_edges={first:[second]})
    assert value['complete_declared_closure'] is True and second in value['files']
    with pytest.raises(ValueError,match='nonempty finite'):
        proof_sources.closure(root,[first],declared_edges={first:[]})


@pytest.mark.parametrize('path',('kb/ram/private.toml','l0/7mfk/function_tokens.csv',
    '../other.py','/private/tmp/other.py','.git/config'))
def test_declared_closure_cannot_read_canonical_guarded_or_outside_sources(tmp_path,path):
    with pytest.raises(ValueError,match='source boundary'):
        proof_sources.closure(tmp_path,[path])


def test_complete_current_reference_closures_bind_both_numerical_sources_and_covering_anchors():
    values=proof_reuse.adapter_closures(repo.ROOT)
    assert set(values)==set(proof_adapter.DESCRIPTORS)
    inputs=ignition_literal_evidence.execution_inputs(repo.ROOT)
    acceptance=tool(repo.ROOT,'acceptance.py','_kb_proof_source_acceptance')
    document=acceptance.declared();group=next(row for row in document['group'] if row['id']=='pipeline_integration')
    anchors=acceptance.direct_sources(group,acceptance.registered(),repo.ROOT)
    for value in values.values():
        assert value['complete_declared_closure'] is True,value['unresolved_edges']
        proof_sources.require_manifest(value,inputs,anchors=set(anchors))
    coolant=values['defs/JK08A.closed-loop-coolant-accesses.toml']
    assert {'tools/sh-elf-run/stock_coolant_conditional_model.py',
        'tools/sh-elf-run/stock_injection_end_angle_model.py'}<=set(coolant['files'])
