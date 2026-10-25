"""Bounded width scopes preserve diagnostic bytes, state words and indexed bases."""

from copy import deepcopy

import pytest

from kb import repo, width_view_evidence as contract, width_view_matrix as matrix


@pytest.mark.parametrize('value',('','65535:00','65537:00','0:00','065536:00','32768:00,32768:00',
                                  '65536:0A','65536:0','65536:000','65536:gg','65536:00,'))
def test_lossless_ram_view_refuses_missing_noncanonical_or_excess_runs(value):
    with pytest.raises(ValueError):
        matrix.decode_rle(value)


def test_lossless_ram_view_retains_all_independent_bytes():
    value=matrix.decode_rle('1:80,1:ff,65533:00,1:7f')
    assert value==b'\x80\xff'+b'\x00'*65533+b'\x7f'


@pytest.mark.parametrize('fault',('semantic-width','selector-range','natural-entry','hardware','resolution'))
def test_descriptor_has_no_implicit_width_or_reachability_resolution(tmp_path,fault):
    source=(repo.ROOT/contract.DESCRIPTOR).read_text()
    key={'semantic-width':'semantic_width_inference','selector-range':'selector_range_inference',
         'natural-entry':'natural_entry_inference','hardware':'hardware_qualification',
         'resolution':'automatic_resolution'}[fault]
    source=source.replace(key+' = false',key+' = true',1)
    path=tmp_path/contract.DESCRIPTOR
    path.parent.mkdir(parents=True)
    path.write_text(source)
    with pytest.raises(ValueError):
        contract.descriptor(tmp_path)


@pytest.fixture(scope='module')
def sources():
    declared=contract.descriptor(repo.ROOT)
    image=repo.images()['JK08A'].path.read_bytes()
    return declared,image


def execute(sources,key,pattern,selector=1,entry=None):
    declared,image=sources
    window=next(row for row in declared['window'] if row['key']==key)
    case={**matrix.cases(window)[0],'pattern':pattern,'selector':selector}
    if entry is not None:case['entry']=entry
    context=matrix.entry(window,case)
    frame=bytearray(b''.join((0xA3B4C5D6+index*17).to_bytes(4,'big') for index in range(48)))
    frame[160:164]=context[7].to_bytes(4,'big')
    frame[168:172]=context[19].to_bytes(4,'big')
    result=contract.execute(window,image,context,matrix.memory(case),bytes(frame),0x02000000,case['entry'])
    return window,case,context,result


def test_diagnostic_high_byte_does_not_erase_distinct_word_consumer_inputs(sources):
    _,_,_,first=execute(sources,'16d2-read-a',0x1234)
    _,_,_,second=execute(sources,'16d2-read-a',0x1235)
    assert first['ram'][0x16D2]==second['ram'][0x16D2]==0x12
    assert first['registers'][4]!=second['registers'][4]
    assert first['macl']==0x1234*118 and second['macl']==0x1235*118


def test_stack_word_state_and_published_high_byte_keep_their_distinct_equations(sources):
    _,_,_,result=execute(sources,'118a-producer',5)
    assert result['ram'][0x118A:0x118C]==bytes.fromhex('0140')
    assert result['ram'][0x1FC8:0x1FCA]==bytes.fromhex('0005')


@pytest.mark.parametrize('selector',(0,1,6,255))
def test_indexed_store_retains_its_conditional_base_including_zero(sources,selector):
    _,case,context,result=execute(sources,'2142-indexed-store',0x80FF,selector)
    access=next(row for row in result['accesses'] if row['site']==0x4A03A)
    assert access['address']==contract.alias(0xFFFF2142)+2*selector
    assert access['width_bytes']==2 and access['bytes']=='80ff'
    assert result['registers'][0]==2*selector
    assert context[0]==0xB6C780FF and case['selector']==selector


def test_byte_publication_observes_the_high_lane_and_full_word_sign_extension(sources):
    _,_,context,result=execute(sources,'4544-publication',0x80FF)
    assert result['ram'][0x9BBA]==0x80
    assert result['ram'][0x9BB9]==context[0]&255
    assert result['registers'][0]==0x80


@pytest.mark.parametrize('premise',('frame','bank','entry','instruction'))
def test_bounded_oracle_refuses_an_unadmitted_execution_premise(sources,premise):
    declared,image=sources
    window=deepcopy(next(row for row in declared['window'] if row['key']=='2142-indexed-store'))
    case=matrix.cases(window)[0]
    context=list(matrix.entry(window,case))
    frame=bytes(192)
    entry=case['entry']
    if premise=='frame':frame=frame[:-1]
    elif premise=='bank':context[14]=0x00008000
    elif premise=='entry':entry+=2
    else:
        image=bytearray(image)
        image[entry:entry+2]=bytes.fromhex('000b')
    with pytest.raises(ValueError):
        contract.execute(window,bytes(image),tuple(context),matrix.memory(case),frame,0x02000000,entry)


def test_diagnostic_identity_statements_read_the_executed_descriptor():
    declared=contract.descriptor(repo.ROOT)
    text=(repo.ROOT/'defs/JK08A.width-views.md').read_text()
    for field in declared['field']:
        if field['kind']=='diagnostic-byte-view':
            assert f"`{field['diagnostic']['did']:04X}`" in text
            assert f"`{field['diagnostic']['address']:08X}`" in text
    assert '`automatic_resolution = false`' in text


@pytest.mark.parametrize('count,active',((0,False),(0,True),(254,True),(255,False),(255,True)))
def test_byte_counter_has_its_own_saturating_access_width(sources,count,active):
    declared,image=sources
    window=next(row for row in declared['window'] if row['key']=='2142-byte-counter')
    case={**matrix.cases(window)[0],'selector':count,'variant':int(active)}
    context=matrix.entry(window,case)
    before=matrix.memory(case)
    result=contract.execute(window,image,context,before,bytes(192),0x02000000,case['entry'])
    assert result['ram'][0x2142]==min(255,count+int(active))
    assert result['ram'][0x2143]==before[0x2143]
    accesses=[row for row in result['accesses'] if row['address']==contract.alias(0xFFFF2142)]
    assert [row['width_bytes'] for row in accesses]==([1,1] if active else [])
