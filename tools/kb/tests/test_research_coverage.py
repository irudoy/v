from kb import research_coverage
from kb.model import Entity, Meaning, Model, Status, Symbol, SymbolKey
from kb.repo import Layout


def test_research_coverage_respects_image_and_layout_scope():
    layouts = {
        'shared': Layout('shared', 'family', 'exact', 'sh7059', 'ROMA', ('ROMA', 'ROMB')),
        'other': Layout('other', 'family', 'near', 'sh7059', 'ROMC', ('ROMC',)),
    }
    block = Entity('block', 'capture', {'title': 'Capture'}, {'stage': [('stage', 'acquisition')]})
    stage = Entity('stage', 'acquisition', {'title': 'Acquisition'})
    function_key = SymbolKey('shared', 'fn', 0x1000)
    signal_key = SymbolKey('shared', 'ram', 0xffff1000)
    endpoint = Entity('endpoint', 'sensor', {'direction': 'input', 'layouts': ['shared']},
                      {'functions': [function_key]})
    chain = Entity('chain', 'speed', refs={'output': [signal_key]},
                   steps=[{'from': signal_key, 'to': signal_key, 'via': [function_key]}])
    symbols = {}
    model = Model(layouts, symbols, {(entity.kind, entity.slug): entity
                                     for entity in (stage, block, endpoint, chain)}, {}, [])
    model.functions = {'shared': {0x1000, 0x1002}, 'other': {0x2000}}
    producer = Meaning('fn', 'producer', props={'block': block.key, 'level': 'code'})
    signal = Meaning('ram', 'speed', props={'block': block.key})
    absent = Meaning('ram', 'absent', props={'block': block.key},
                     statuses={'shared': Status('shared', 'absent')})
    unresolved = Meaning('ram', 'unresolved', props={'block': block.key},
                         statuses={'other': Status('other', 'unresolved')})
    for meaning, key, props in [(producer, function_key, {'images': ['ROMA']}),
                                (signal, signal_key, {'level': 'candidate'})]:
        symbol = Symbol(key, props, meaning=meaning)
        symbols[key] = symbol
        meaning.symbols[key.layout] = symbol
    model.meanings = [producer, signal, absent, unresolved]

    report = research_coverage.render(model)
    assert '| ROMA | `shared` | 1 / 2 | 1 / 0 / 0 | 1 | 1 | 1 | 1 | 1 | 0 |' in report
    assert '| ROMB | `shared` | 0 / 2 | 0 / 0 / 0 | 0 | 0 | 1 | 1 | 1 | 1 |' in report
    assert '| ROMC | `other` | 0 / 1 | 0 / 0 / 0 | 0 | 0 | 1 | 3 | 0 | 0 |' in report
    assert ('| Acquisition | Capture | 1 / 1 / 1 / 1 / 0 | 0 / 1 / 1 / 1 / 1 |'
            ' 0 / 1 / 3 / 0 / 0 |') in report
