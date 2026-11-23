"""Bounded lossless transfer and refusal contracts without a compiled model."""
from copy import deepcopy
from types import SimpleNamespace

import pytest
import tomllib

from kb import research
from kb.model import Meaning, Symbol, SymbolKey

SOURCE=b'''title = "Probe"
[[step]]
from = "input/ram"
to = "output/ram"
via = ["first/fn", "second/fn", "first/fn"]
effect = "selects"
sign = "none"
note = "The alternate source is selected while bit 3 is set."
specs = ["defs/probe.md"]
'''
STEP={'from':'input/ram','to':'output/ram','via':['first/fn','second/fn','first/fn'],
      'effect':'selects','sign':'none','note':'The alternate source is selected while bit 3 is set.',
      'specs':['defs/probe.md']}
PATH='kb/chain/probe.toml'
COMMIT='a'*40
GRAMMAR=SimpleNamespace(validate=lambda text:None if text=='to = from' else 'prose')


def packet():
    record=research.archive(STEP,SOURCE,COMMIT,PATH,1)
    current={key:deepcopy(value) for key,value in STEP.items() if key!='note'}
    current['research']=deepcopy(record)
    return record,current


def alias_model():
    symbols = {}
    for kind, old, new, address in (
            ('ram', 'input', 'renamed_input', 0xffff1000),
            ('ram', 'output', 'output', 0xffff1002),
            ('fn', 'first', 'renamed_first', 0x200),
            ('fn', 'second', 'second', 0x202)):
        owner = Meaning(kind, name=new)
        symbol = Symbol(SymbolKey('7mfk', kind, address), name=new,
                        former=(old,) if old != new else (), meaning=owner)
        owner.symbols = {'7mfk': symbol}
        symbols[symbol.key] = symbol
    return SimpleNamespace(symbols=symbols)


def test_exact_retained_aliases_preserve_the_immutable_record_and_repeated_calls():
    record, current = packet()
    frozen = deepcopy(record)
    current['from'] = 'renamed_input/ram'
    current['via'] = ['renamed_first/fn', 'second/fn', 'renamed_first/fn']
    assert research.validate(record, current, SOURCE, GRAMMAR, PATH, 1,
                             model=alias_model()) is None
    assert record == frozen and current['research'] == frozen


def test_archived_spec_can_follow_its_registered_move():
    source = SOURCE.replace(b'defs/probe.md', b'defs/JK08A.cvtc.md')
    original = tomllib.loads(source.decode())['step'][0]
    record = research.archive(original, source, COMMIT, PATH, 1)
    current = {key: value for key, value in original.items() if key != 'note'}
    current['specs'] = ['defs/analysis/valve-timing/JK08A.cvtc.md']
    current['research'] = deepcopy(record)
    assert research.validate(record, current, source, GRAMMAR, PATH, 1,
                             model=alias_model()) is None
    assert record['original'] == research.exact_step(original)
    current['specs'] = ['defs/analysis/valve-timing/other.md']
    assert research.validate(record, current, source, GRAMMAR, PATH, 1,
                             model=alias_model())


@pytest.mark.parametrize('change', [
    lambda step: step.update(to='renamed_input/ram'),
    lambda step: step.update(via=['renamed_first/fn', 'renamed_first/fn', 'second/fn']),
    lambda step: step.update(via=['renamed_first/fn', 'second/fn']),
    lambda step: step.update(from_='renamed_input/ram'),
    lambda step: step.update(sign='positive'),
    lambda step: step.update(specs=['defs/other.md']),
    lambda step: step.update(to='output/ram/jk78c-ffff1002'),
    lambda step: step.update(to='output/ram/7mfk-ffff1004'),
    lambda step: step.update(to='output/reg'),
])
def test_aliases_cannot_change_bindings_order_layout_address_kind_or_metadata(change):
    record, current = packet()
    current['from'] = 'renamed_input/ram'
    change(current)
    assert research.validate(record, current, SOURCE, GRAMMAR, PATH, 1,
                             model=alias_model())


def test_an_ambiguous_former_name_cannot_rebind_an_archived_step():
    record, current = packet()
    current['from'] = 'renamed_input/ram'
    model = alias_model()
    owner = Meaning('ram', name='different_input')
    symbol = Symbol(SymbolKey('7mfk', 'ram', 0xffff1004), name=owner.name,
                    former=('input',), meaning=owner)
    model.symbols[symbol.key] = symbol
    assert research.validate(record, current, SOURCE, GRAMMAR, PATH, 1, model=model)


def test_generic_reference_rewrites_preserve_every_archival_byte():
    from kb import write
    record, current = packet()
    record['original'] += ' [[input/ram]]'
    current['research'] = record
    for transform in (
            lambda value: write.renamed(value, {'input'}, 'ram', 'renamed_input'),
            lambda value: write.relocated(value, {'input/ram': 'input/ram/7mfk-ffff1004'})):
        updated, _ = transform(current)
        assert updated['research'] == record


def test_complete_original_text_binding_repeated_calls_and_specs_are_preserved():
    record,current=packet()
    assert research.validate(record,current,SOURCE,GRAMMAR,PATH,1) is None
    assert record['original']==research.exact_step(STEP)
    assert record['state']=='unresolved'
    assert set(current)==set(STEP)-{'note'}|{'research'}


def test_source_record_round_trips_through_native_schema_and_architecture_view():
    from kb import architecture_projection,store,write
    record,current=packet()
    document={'title':'Probe','summary':'Declared transfer.','quantity':'raw',
              'output':'output/ram','home':'7mfk','order':1,'step':[current]}
    assert tomllib.loads(store.render('chain',document))==document
    assert write.checked(store.STEP,'step',current)==current
    view={'schema_version':1,'rom':'JK08A','summary':'Probe',
          'sources':architecture_projection.SOURCES,'stage':[],'block':[],
          'endpoint':[],'chain':[{'id':'probe','name':'Probe','step':[current]}]}
    assert tomllib.loads(architecture_projection.render(view))['chain'][0]['step'][0]==current
    assert record['original']==current['research']['original']


@pytest.mark.parametrize('change',[
    lambda record,current:record.update(state='verified'),
    lambda record,current:record.update(source_commit='a'*7),
    lambda record,current:record.update(source_path='kb/chain/other.toml'),
    lambda record,current:record.update(order=2),
    lambda record,current:record.update(order=True),
    lambda record,current:record.update(source_sha256='0'*64),
    lambda record,current:record.update(step_sha256='0'*64),
    lambda record,current:record.update(original=record['original']+' '),
    lambda record,current:record.update(level='code'),
    lambda record,current:current.update(via=['first/fn','second/fn']),
    lambda record,current:current.update(sign='positive'),
    lambda record,current:current.update(note='to = from'),
    lambda record,current:current.pop('specs'),
])
def test_source_field_loss_and_unsupported_semantic_promotions_are_refused(change):
    record,current=packet();change(record,current)
    assert research.validate(record,current,SOURCE,GRAMMAR,PATH,1)


def test_changed_original_with_a_recomputed_digest_is_still_refused_by_the_source():
    record,current=packet()
    altered=deepcopy(STEP);altered['note']='A different unsupported condition.'
    record['original']=research.exact_step(altered)
    record['step_sha256']=research.sha256(record['original'].encode())
    assert 'historical source step' in research.validate(record,current,SOURCE,GRAMMAR,PATH,1)


def test_existing_arithmetic_cannot_be_relabelled_as_unresolved_prose():
    step={**STEP,'note':'to = from'}
    source=SOURCE.replace(STEP['note'].encode(),b'to = from')
    record=research.archive(step,source,COMMIT,PATH,1)
    current={key:value for key,value in step.items() if key!='note'}
    current['research']=record
    assert 'unresolved original prose' in research.validate(record,current,source,GRAMMAR,PATH,1)


@pytest.mark.parametrize('replacement',[None,[],[{}]])
def test_an_existing_record_cannot_be_removed_by_generic_batch_replacement(replacement):
    record,current=packet()
    entity=SimpleNamespace(kind='chain',key='probe/chain',steps=[current])
    before=alias_model()
    before.entities={('chain','probe'):entity}
    entities={} if replacement is None else {('chain','probe'):SimpleNamespace(steps=replacement)}
    after=alias_model()
    after.entities=entities
    assert research.preservation(before,after)
    assert research.preservation(before,before)==[]


def test_name_only_rename_preserves_exact_before_after_bindings_and_archive():
    _, current = packet()
    before = alias_model()
    before.entities = {('chain', 'probe'): SimpleNamespace(
        kind='chain', key='probe/chain', props={'home': '7mfk'}, steps=[current])}
    after = deepcopy(before)
    changed = after.entities[('chain', 'probe')].steps[0]
    changed['from'] = 'renamed_input/ram'
    changed['via'] = ['renamed_first/fn', 'second/fn', 'renamed_first/fn']
    assert research.preservation(before, after) == []
    assert changed['research'] == current['research']


@pytest.mark.parametrize('field,index', [('from', None), ('to', None), ('via', 0), ('via', 1), ('via', 2)])
def test_unchanged_names_cannot_hide_moved_owned_symbols(field, index):
    record, current = packet()
    before = alias_model()
    before.entities = {('chain', 'probe'): SimpleNamespace(
        kind='chain', key='probe/chain', props={'home': '7mfk'}, steps=[current])}
    after = deepcopy(before)
    reference = current[field][index] if index is not None else current[field]
    key = research.reference_binding(reference, after, '7mfk')
    symbol = after.symbols.pop(key)
    symbol.key = SymbolKey(key.layout, key.kind, key.address + 4)
    after.symbols[symbol.key] = symbol
    assert after.entities[('chain', 'probe')].steps[0] == current
    assert research.validate(record, current, SOURCE, GRAMMAR, PATH, 1, model=after) is None
    assert 'owned SymbolKey bindings' in '\n'.join(research.preservation(before, after))
