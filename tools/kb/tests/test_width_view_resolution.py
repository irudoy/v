"""Narrow width dispositions require complete independent original evidence."""

from copy import copy
import json
from unittest.mock import patch

import pytest

from kb import compile, copy_evidence, repo, reconciliation, sid22_evidence, test_evidence, write
from kb import width_view_resolution as proof, width_compatibility


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        record['candidate']['witness']['width_views']
        sid=json.loads(copy_evidence._read(repo.ROOT,sid22_evidence.RECEIPT))
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:
            pytest.fail('narrow width admission requires the complete original B COPY/SID22 records')
        pytest.skip('the complete original B width-view records are unavailable')
    model=compile.build(repo.ROOT)
    fields=proof.contract.descriptor(repo.ROOT)['field']
    return model,record,sid,fields


def request(source,field):
    model=source[0]
    symbol=next(row for row in model.symbols.values() if row.key.key==field['symbol'])
    claim=dict(symbol=symbol.key.key,width=field['declared_bits'],
        observed=sorted((row['function'],row['site'],row['mode'],row['width_bytes']) for row in field['observed']))
    return symbol,claim


def test_each_narrow_exception_preserves_its_semantic_byte_and_declares_every_limit(original):
    model,record,sid,fields=original
    for field in fields:
        symbol,claim=request(original,field)
        result=proof.require(model,symbol,claim,record=record,sid22_record=sid)
        assert result['original_claim_sha256']==field['original_claim_sha256']
        assert result['declared_bits']==8 and result['physical_question_bits']==16
        assert result['native_width_change'] is False and result['identity_grounding'] is False
        assert result['access_grounding'] is False and result['zero_index_disjointness'] is False
        assert result['natural_entry_inference'] is False and result['selector_range_inference'] is False
        assert symbol.value('width')==8
        if field['kind']=='diagnostic-byte-view':
            assert result['diagnostic_view']['response_bytes']==1
        else:
            assert result['diagnostic_view'] is None
            assert all(proof.contract.alias(0xFFFF2142) in row['addresses'] for row in result['working_instruction_support'])


@pytest.mark.parametrize('fault',('declared-width','site-width','site-mode','missing-site','extra-site','other-symbol'))
def test_narrow_exception_refuses_a_different_raw_question(original,fault):
    model,record,sid,fields=original
    symbol,claim=request(original,fields[0])
    claim={**claim,'observed':list(claim['observed'])}
    if fault=='declared-width':claim['width']=16
    elif fault=='other-symbol':claim['symbol']='7mfk-ffff118b/ram'
    elif fault=='missing-site':claim['observed'].pop()
    elif fault=='extra-site':claim['observed'].append(('7mfk:0003cb64',0x3CBB2,'read',2))
    else:
        function,site,mode,width=claim['observed'][0]
        claim['observed'][0]=(function,site,'read' if mode not in ('read',) else 'write',width) if fault=='site-mode' else (function,site,mode,1)
    with pytest.raises(ValueError):
        proof.require(model,symbol,claim,record=record,sid22_record=sid)


@pytest.mark.parametrize('fault',('SID22-terminal','SID22-original','SID22-native','COPY-terminal','missing-capture'))
def test_a_byte_view_cannot_use_failed_or_mixed_originals(original,fault):
    model,held,sid,fields=original
    record={**held,'candidate':dict(held['candidate']),'terminal':dict(held['terminal'])}
    sid={**sid,'terminal':dict(sid['terminal'])}
    if fault=='SID22-terminal':sid['terminal']['actual_exit_code']=1
    elif fault=='SID22-original':sid['process_sha256']='0'*64
    elif fault=='SID22-native':sid['native_model']='0'*64
    elif fault=='COPY-terminal':record['terminal']['actual_exit_code']=1
    else:record['candidate']['witness']={key:value for key,value in held['candidate']['witness'].items() if key!='width_views'}
    symbol,claim=request(original,fields[0])
    with pytest.raises(ValueError):
        proof.require(model,symbol,claim,record=record,sid22_record=sid)


@pytest.mark.parametrize('fault',('missing','failed','stale'))
def test_unqualified_width_view_leaves_the_raw_question(original,fault):
    model,_,_,fields=original
    symbol,claim=request(original,fields[0])
    with patch.object(proof,'require',side_effect=ValueError(fault+' complete original')):
        assert width_compatibility.accepted(model,symbol,claim) is None
        assert any(row['subject']==symbol.key.key for row in reconciliation.differences(model))


def test_normal_writer_does_not_remove_an_unrequested_narrow_review(original):
    model,_,_,fields=original
    raw=reconciliation.differences(model,width_proofs=False)
    pending=copy(model)
    pending.config={**model.config,'reconciliation':{
        **model.config.get('reconciliation',{}),'enabled':True,
        'review':[{**row,'state':'unresolved','reason':row['detail']} for row in raw]}}
    assert reconciliation.rebase(pending,pending,{}) is None
    field=fields[0]
    change=write.Change(pending,write.model_resolver(pending),repo.ROOT)
    change.run(dict(cmd='reconcile-width',ref=field['meaning'],layout='7mfk',claim_sha256=field['original_claim_sha256']))
    text=reconciliation.rebase(pending,pending,{},width_resolutions=change.width_resolutions)
    assert text is not None and field['original_claim_sha256'] not in text
    for row in raw:
        if row['claim_sha256']!=field['original_claim_sha256']:
            assert row['claim_sha256'] in text
    assert next(row for row in pending.symbols.values() if row.key.key==field['symbol']).value('width')==8


@pytest.mark.parametrize('flag',('native_width_change','identity_grounding','access_grounding',
    'natural_entry_inference','selector_range_inference','zero_index_disjointness','hardware_qualification'))
def test_disposition_registry_refuses_broader_claims(tmp_path,flag):
    for name in (proof.DESCRIPTOR,proof.contract.DESCRIPTOR):
        path=tmp_path/name
        path.parent.mkdir(parents=True,exist_ok=True)
        source=(repo.ROOT/name).read_text()
        if name==proof.DESCRIPTOR:
            source=source.replace(flag+' = false',flag+' = true',1)
        path.write_text(source)
    with pytest.raises(ValueError):
        proof.descriptor(tmp_path)


def test_normal_writer_preserves_the_narrow_review_when_live_proof_is_lost(original):
    model,_,_,fields=original
    raw=reconciliation.differences(model,width_proofs=False)
    pending=copy(model)
    held=[{**row,'state':'unresolved','reason':row['detail']} for row in raw]
    pending.config={**model.config,'reconciliation':{
        **model.config.get('reconciliation',{}),'enabled':True,'review':held}}
    field=fields[0]
    change=write.Change(pending,write.model_resolver(pending),repo.ROOT)
    change.run(dict(cmd='reconcile-width',ref=field['meaning'],layout='7mfk',claim_sha256=field['original_claim_sha256']))
    with patch.object(proof,'accepted',return_value=None):
        assert reconciliation.rebase(pending,pending,{},width_resolutions=change.width_resolutions) is None
    assert change.expected[0](pending)
    assert pending.config['reconciliation']['review']==held
