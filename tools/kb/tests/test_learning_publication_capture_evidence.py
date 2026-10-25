"""Natural LTFT originals reject substituted state, inputs and predicate paths."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import learning_transfer_capture_evidence as proof,learning_transfer_contract as contract
from kb import learning_transfer_matrix as matrix,learning_transfer_semantics as numeric
from kb import learning_publication_transfers as physical


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['learning_transfer_paths']
        assert any(case['kind']=='publication' for case in packet['declaration']['cases'])
    except (FileNotFoundError,KeyError,AssertionError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires the complete original LTFT publication')
        pytest.skip('the complete original LTFT publication is unavailable')
    model=compile.build(repo.ROOT);proof.require_primary(model,record)
    return model,record,packet


@pytest.fixture(scope='module')
def actual(original):
    image=repo.images()['JK08A'].path.read_bytes();declared=original[2]['declaration']
    fixture,_=contract.independent_fixture(declared['source'],image)
    observations=proof.observations(original[2],declared);selected={}
    for bank in (0,1):
        case=next(case for case in declared['cases'] if case['kind']=='publication' and case['argument']==bank
            and case['ltft_l']==case['ltft_a']==25600 and case['diagnostic']==0)
        observed=observations[case['index']];result,_=proof.require_state(declared,image,fixture,case,observed)
        selected[bank]=(case,observed,result)
    return declared,image,fixture,selected


@pytest.mark.parametrize('bank',(0,1))
@pytest.mark.parametrize('fault',('left','right','output','sibling','outside','argument','sr','frame','entry-frame',
    'abi','pr','sp','continuation','calibration'))
def test_each_actual_bank_refuses_changed_datum_or_complete_state(actual,bank,fault):
    declared,image,fixture,selected=actual;case,observed,_=selected[bank];observed=deepcopy(observed)
    if fault in ('left','right','output','sibling','outside'):
        key='memory_before' if fault in ('left','right') else 'memory_after'
        at={'left':0x2306+bank*2,'right':0x5648+bank*2,'output':0x2302+bank*2,
            'sibling':0x2302+(1-bank)*2,'outside':0x1234}[fault]
        memory=bytearray(observed[key][0]);memory[at]^=1;observed[key]=(bytes(memory),)
    elif fault=='argument':
        context=list(observed['context']);context[4]^=0x100;observed['context']=tuple(context)
    elif fault=='sr':observed['sr_before']^=0x100
    elif fault in ('frame','entry-frame'):
        key='frame_before' if fault=='entry-frame' else 'frame_after';frame=bytearray(observed[key]);frame[148]^=1
        observed[key]=bytes(frame)
    elif fault in ('abi','pr'):
        key='exit' if fault=='pr' else 'abi_after';values=list(observed[key]);values[1]^=1;observed[key]=tuple(values)
    elif fault=='sp':observed['sp']+=4
    elif fault=='continuation':observed['continuation']+=2
    else:
        at=next(start for start,raw in observed['calibration_before'].items() if start<=0x8E5A<start+len(raw))
        value=bytearray(observed['calibration_before'][at]);value[0x8E5A-at]^=1;observed['calibration_before'][at]=bytes(value)
    with pytest.raises(ValueError):proof.require_state(declared,image,fixture,case,observed)


@pytest.mark.parametrize('bank',(0,1))
@pytest.mark.parametrize('fault',('site','width','direction','address','value','missing-read','extra-read',
    'missing-call','extra-call','call-target','post-delay-index'))
def test_actual_LTFT_datum_sequence_and_real_predicate_arguments_are_required(actual,bank,fault):
    _,_,_,selected=actual;case,observed,result=selected[bank];result=deepcopy(result)
    if fault=='missing-call':result['calls'].clear()
    elif fault=='extra-call':result['calls'].append(deepcopy(result['calls'][0]))
    elif fault=='call-target':result['calls'][0]['target']+=2
    elif fault=='post-delay-index':
        values=list(result['calls'][0]['entry']['registers']);values[4]=0x128;result['calls'][0]['entry']['registers']=values
    else:
        row=next(row for row in result['accesses'] if row['site']==0x57B3A)
        if fault=='missing-read':result['accesses'].remove(row)
        elif fault=='extra-read':result['accesses'].append(deepcopy(row))
        elif fault=='site':row['site']+=2
        elif fault=='width':row['width_bytes']=1
        elif fault=='direction':row['mode']='write'
        elif fault=='address':row['address']+=2
        else:row['bytes']='0000' if row['bytes']!='0000' else '0001'
    with pytest.raises(ValueError):physical.evaluate(case,observed,result)


@pytest.mark.parametrize('source',('tools/sh-elf-run/stock_jk08a_ltft_publication.s',
    'tools/sh-elf-run/stock-jk08a-ltft-publication-cases.h',physical.ARITHMETIC_SOURCE,
    'tools/kb/src/kb/learning_publication_transfers.py'))
def test_each_LTFT_executable_input_and_independent_equation_source_is_bound(original,source):
    inputs=dict(original[1]['candidate']['producer_inputs']);inputs[source]='0'*64
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.mark.parametrize('fault',('missing-unit','changed-code','changed-pool','private-assembly','private-input','omitted-publication'))
def test_the_LTFT_unit_and_actual_invocations_cannot_be_omitted_or_substituted(original,fault):
    from test_learning_transfer_capture_evidence import rewrite_observations
    packet=deepcopy(original[2]);unit=next(row for row in packet['reconstruction'] if row['unit']=='jk08a-learning-publication')
    if fault=='missing-unit':packet['reconstruction'].remove(unit)
    elif fault=='changed-code':unit['code'][0]['reconstructed']+='00'
    elif fault=='changed-pool':unit['pools'][0]['stock']='00'
    elif fault=='private-assembly':packet['consumed']['stock_jk08a_ltft_publication.s']+='00'
    elif fault=='private-input':packet['consumed']['stock-jk08a-ltft-publication-cases.h']+='00'
    else:
        packet['observations']=[row for row in packet['observations'] if row['kind']!=matrix.KINDS.index('publication')]
        rewrite_observations(packet)
    with pytest.raises(ValueError):proof.require_witness(original[0],packet,original[1]['candidate']['producer_inputs'])


def test_input_prefix_has_no_expected_output_register_or_terminal_columns(tmp_path):
    path=matrix.INPUT_SOURCES[2];text=(repo.ROOT/path).read_text();before=matrix.publication_inputs(repo.ROOT)
    start=text.index('static const struct ltft_publication_case ltft_publication_cases[] = {')
    lines=text[start:].splitlines();changed=[]
    for line in lines[1:matrix.PUBLICATION_PREFIX+1]:
        import ast,re
        raw=re.sub(r'(?<=[0-9a-fA-F])U\b','',line.strip().rstrip(',')).replace('{','[').replace('}',']')
        row=ast.literal_eval(raw);row[1]=[0]*15;row[5]=0;row[17]=0;row[18]=0
        changed.append(json.dumps(row).replace('[','{').replace(']','}')+',')
    target=tmp_path/path;target.parent.mkdir(parents=True)
    target.write_text(text[:start]+lines[0]+'\n'+'\n'.join(changed)+'\n};\n')
    assert matrix.publication_inputs(tmp_path)==before


def test_LTFT_scalar_unsigned_wrap_limit_equality_neutral_and_word_truncation_are_literal():
    memory=bytearray(65536)
    def value(left,right,u,v,mask=0,diagnostic=0):
        for at,item in ((0x2308,left),(0x564A,right),(0x15FC,u),(0x15FE,v)):
            numeric.put_word(memory,at,item)
        memory[0x230E]=mask;memory[0x5A94]=diagnostic
        return numeric.publication(bytes(memory),1,90,110)['output']
    assert value(25599,0,1,0)==28160
    assert value(25600,0,1,0)==23040
    assert value(25599,0,0,0)==65535
    assert value(65535,65535,1,0,mask=2)==39934
    assert value(0,0,1,0,diagnostic=128)==25600
