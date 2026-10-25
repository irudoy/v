"""Exact originals and operands govern source reuse, with no evidence donation."""

from copy import deepcopy
import json

import pytest

from kb import cli,mcp,proof_reuse,proof_sources,repo,value_flow,derive,ordinary_access_registry
from kb import closed_loop_coordinate_access_contract as coordinate


@pytest.fixture(scope='module')
def catalog():
    return proof_reuse.index(repo.ROOT)


def _candidate(datum=0xFFFF1350):
    return dict(id='read-before-absolute-helper',component='learning_transfer_paths',
        original='a'*64,datum=datum,sites=[0x57D78],width=2,direction='reader',
        function=0x22590,entry=0x57D1E,phase='before-57d86',premises='b'*64,
        call_premises=[dict(callsite=0x57D86,target=0x22590)],image='c'*64,analysis='d'*64)


def _request(candidate):
    return {key:deepcopy(candidate[key]) for key in ('original','datum','sites','width',
        'direction','function','entry','phase','premises','call_premises','image','analysis')}


@pytest.mark.parametrize('datum',(0xFFFF134E,0xFFFF1350))
def test_shared_22590_helper_cannot_donate_evidence_to_ffff2c1c(datum):
    candidate=_candidate(datum);request=_request(candidate)
    request.update(original='e'*64,datum=0xFFFF2C1C)
    result=proof_reuse.compare(request,candidate)
    assert {row['reason'] for row in result['incompatible']}=={'incompatible-original','incompatible-datum'}
    assert result['source_compatible'] is result['accepted'] is result['semantic_admission'] is False
    assert 'function' in result['covered']


@pytest.mark.parametrize('field,wrong',(('sites',[0x57D7A]),('width',4),('width',True),
    ('direction','writer'),('entry',0x22590),('phase','after-57d86'),
    ('call_premises',[dict(callsite=0x57D86,target=0x22590,delay_slot=0x57D88)]),
    ('analysis','0'*64)))
def test_wrong_site_width_direction_entry_phase_call_premises_or_analysis_is_incompatible(field,wrong):
    candidate=_candidate();request=_request(candidate);request[field]=wrong
    result=proof_reuse.compare(request,candidate)
    assert result['incompatible'] and not result['source_compatible']
    assert result['accepted'] is result['semantic_admission'] is False


@pytest.mark.parametrize('field',('sites','width','entry','phase','premises','call_premises','analysis'))
def test_unknown_required_operand_or_premise_is_missing_coverage(field):
    candidate=_candidate();request=_request(candidate);request[field]=None
    result=proof_reuse.compare(request,candidate)
    assert result['missing'] and not result['source_compatible']
    assert result['accepted'] is False


def test_current_index_uses_exact_registry_references_and_preserves_native_types(catalog):
    rows=coordinate.descriptor(repo.ROOT)['reference']
    selected={row['original']:row for row in catalog['references']
        if row['descriptor']==coordinate.DESCRIPTOR}
    assert len(selected)==len(rows)
    for row in rows:
        actual=selected[row['original_claim_sha256']]
        assert (actual['datum'],actual['sites'],actual['width'])==(row['address'],row['sites'],row['width_bytes'])
        assert actual['native_types']==dict(width=row['declared_width'],signed=row['declared_signed'])
        assert actual['accepted'] is False and actual['accepted_status']=='not-evaluated'


def _coolant_group():
    references=[row for row in coordinate.descriptor(repo.ROOT)['reference']
        if row['component']=='closed_loop_coolant_paths']
    claims=[dict(subject=f'7mfk-{row["address"]:08x}/const',function='7mfk-0005525a/fn',
        meaning=row['owner'],original_claim_sha256=row['original_claim_sha256'],
        original_canonical_claim=json.loads(row['original_claim_json'])) for row in references]
    group=dict(function='7mfk-0005525a/fn',source_prepared_originals=[],remaining_originals=claims,
        shared_code_candidates=[dict(region='same-function-structure',semantic_admission=False)])
    return references,dict(groups=[group])


def test_group_subtraction_uses_current_exact_originals_and_keeps_acceptance_separate(monkeypatch,catalog):
    rows,groups=_coolant_group();row=rows[0]
    prepared=dict(source_checkpoint=1,remaining_general=1,source_preparation_is_qualification=False,
        source_prepared_originals={row['original_claim_sha256']:[dict(source=coordinate.DESCRIPTOR,
            component=row['component'],id=row['id'])]})
    monkeypatch.setattr(proof_reuse,'index',lambda root:deepcopy(catalog))
    monkeypatch.setattr(proof_sources,'closure',lambda *args,**kwargs:dict(schema=1,
        files={},edges={},generated_input_headers=[],unresolved_edges=[],complete_declared_closure=True))
    result=proof_reuse.report(repo.ROOT,groups,'7mfk-0005525a/fn',prepared)
    assert result['prepared_originals']==[row['original_claim_sha256']]
    assert len(result['remaining_originals'])==1 and result['accepted_originals']==[]
    assert result['source_preparation_is_qualification'] is result['semantic_admission'] is False
    assert all(not claim['accepted'] for claim in result['claims'])
    assert any(item['obligation']=='fixed-other-causal' for claim in result['claims']
        for candidate in claim['candidates'] for item in candidate['missing'])


def test_stale_prepared_identity_or_source_binding_is_not_subtracted(catalog):
    row=catalog['references'][0]
    prepared=dict(source_preparation_is_qualification=False,source_prepared_originals={
        row['original']:[dict(source='defs/wrong.toml',component=row['component'],id=row['id'])],
        'f'*64:[dict(source=row['descriptor'],component=row['component'],id=row['id'])]})
    accepted,unresolved=proof_reuse._prepared(prepared,catalog['references'])
    assert not accepted and len(unresolved)==2
    prepared['source_preparation_is_qualification']=True
    with pytest.raises(ValueError):proof_reuse._prepared(prepared,catalog['references'])


def test_report_refuses_conflicting_requirements_and_other_original_ids(monkeypatch,catalog):
    rows,groups=_coolant_group();prepared=dict(source_preparation_is_qualification=False,source_prepared_originals={})
    monkeypatch.setattr(proof_reuse,'index',lambda root:deepcopy(catalog))
    with pytest.raises(ValueError,match='another original'):
        proof_reuse.report(repo.ROOT,groups,'7mfk-0005525a/fn',prepared,requirements={'f'*64:{}})
    with pytest.raises(ValueError,match='datum, function or direction'):
        proof_reuse.report(repo.ROOT,groups,'7mfk-0005525a/fn',prepared,
            requirements={rows[0]['original_claim_sha256']:dict(datum=0xFFFF2C1C)})


def test_existing_accepted_component_cannot_donate_to_another_exact_original(monkeypatch,catalog):
    rows,groups=_coolant_group();claim=deepcopy(groups['groups'][0]['remaining_originals'][0])
    claim['original_canonical_claim']['props']['another_obligation']=True
    claim['original_claim_sha256']=proof_reuse.digest(claim['original_canonical_claim'])
    groups['groups'][0]['remaining_originals']=[claim]
    monkeypatch.setattr(proof_reuse,'index',lambda root:deepcopy(catalog))
    monkeypatch.setattr(proof_sources,'closure',lambda *args,**kwargs:dict(schema=1,
        files={},edges={},generated_input_headers=[],unresolved_edges=[],complete_declared_closure=True))
    calls=[]
    for family in ordinary_access_registry.families():
        monkeypatch.setattr(family.evidence,'accepted',lambda *args: calls.append(args) or True)
    prepared=dict(source_preparation_is_qualification=False,source_prepared_originals={})
    result=proof_reuse.report(repo.ROOT,groups,'7mfk-0005525a/fn',prepared,model=object())
    assert not calls and result['accepted_originals']==[]
    assert result['remaining_originals']==[claim['original_claim_sha256']]
    for key in ('semantic_admission','scale_admission','units_admission','native_geometry_inference',
            'reverse_identity_donation','hardware_qualification','canonical_publication','receipt_publication'):
        assert result[key] is False


def _flow_fixture(tmp_path):
    source=tmp_path/'tools/source.py';source.parent.mkdir(parents=True);source.write_text('VALUE=1\n')
    descriptor=tmp_path/'defs/source.toml';descriptor.parent.mkdir(parents=True);descriptor.write_text('schema=1\n')
    candidate=_candidate(0x990A);candidate.update(component='closed_loop_coolant_paths',width=1,sites=[0x553E6])
    component=dict(descriptor='defs/source.toml',entries=[0x5525A])
    case=dict(entry=0x5525A)
    binding=dict(sources={'tools/source.py':proof_reuse.sha(source.read_bytes())},
        descriptor_sha256=proof_reuse.sha(descriptor.read_bytes()),image_sha256=candidate['image'],
        input_sha256=proof_reuse.digest(case),L0_analysis_sha256='current')
    roots=dict(id=0,operation='memory-read',address=0x990A,site=0x553E6,width_bytes=1,
        data_inputs=[],address_inputs=[],control_inputs=[])
    output=dict(id=1,operation='memory-store',data_inputs=[0],address_inputs=[],control_inputs=[])
    flow=dict(schema=1,kind='bounded-concrete-value-flow',component=candidate['component'],
        source_prepared=True,status='resolved-concrete-path',unresolved_edges=[],
        request=dict(layout='7mfk',datum=0x990A,load_site=0x553E6,width_bytes=1),
        accepted=False,executable_evidence=False,causal_evidence=False,semantic_admission=False,
        binding=binding,analysis_sha256=proof_reuse.digest(binding),premises=dict(case=case),calls=[],
        path=dict(nodes=[roots,output],source_definitions=[0],outputs=[1]))
    return candidate,component,flow


@pytest.mark.parametrize('fault',('source','L0','datum-root','width-root','edge','unrelated-result','self-admission'))
def test_saved_flow_requires_current_sources_exact_root_width_edges_and_no_self_admission(tmp_path,monkeypatch,fault):
    candidate,component,flow=_flow_fixture(tmp_path)
    monkeypatch.setattr(derive,'_pair_digest',lambda *args:'current')
    if fault=='source':flow['binding']['sources']['tools/source.py']='0'*64
    elif fault=='L0':flow['binding']['L0_analysis_sha256']='stale'
    elif fault=='datum-root':flow['path']['nodes'][0]['address']=0xFFFF2C1C
    elif fault=='width-root':flow['path']['nodes'][0]['width_bytes']=2
    elif fault=='edge':flow['path']['nodes'][1]['data_inputs']=[999]
    elif fault=='unrelated-result':flow['path']['nodes'][1]['data_inputs']=[]
    else:flow['semantic_admission']=True
    flow['analysis_sha256']=proof_reuse.digest(flow['binding'])
    actual,unknown=proof_reuse.flow_binding(tmp_path,candidate,component,[flow])
    assert actual==candidate and unknown


def test_a_current_bounded_flow_adds_only_structural_bindings(tmp_path,monkeypatch):
    candidate,component,flow=_flow_fixture(tmp_path)
    candidate['call_premises']=None
    monkeypatch.setattr(derive,'_pair_digest',lambda *args:'current')
    actual,unknown=proof_reuse.flow_binding(tmp_path,candidate,component,[flow])
    assert not unknown
    assert (actual['analysis'],actual['entry'],actual['call_premises'])==(flow['analysis_sha256'],0x5525A,[])
    assert actual['original']==candidate['original']


def test_saved_group_query_is_one_read_only_cli_mcp_contract():
    parser=cli.build_parser();arguments=dict(group='tmp/groups.json',function='7mfk:0005525a',
        prepared='tmp/prepared.json',flow=['tmp/flow.json'],json=True)
    args=parser.parse_args(mcp.argv('proof-group',arguments,parser))
    assert args.handler==cli.command_proof_group and args.accepted is False
    tool=next(row for row in mcp.tools(parser) if row['name']=='kb_proof-group')
    assert set(tool['inputSchema']['required'])=={'group','function','prepared'}
