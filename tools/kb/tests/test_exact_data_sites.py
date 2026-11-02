"""Exact data identities from bounded images and normalized census rows."""

import contextlib
import csv
import hashlib
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from kb import derive, l0, match, repo, sites
from kb.model import Meaning, Model, Symbol, SymbolKey


def census_row(site=0x10, **cells):
    row = dict.fromkeys((*sites.CENSUS_ADDRESSES, 'k4', 'k5', 'k6', 'k7'), '')
    row.update(callsite=f'{site:08x}', kernel='00000090', wrapper='00000080')
    row.update(cells)
    return row


def image_words(words, size=0x30):
    data = bytearray(size)
    for address, word in words.items():
        data[address:address + 2] = word.to_bytes(2, 'big')
    return bytes(data)


@pytest.mark.parametrize('kind', ['pool', 'const', 'slice', 'phi'])
def test_normalized_dataflow_includes_all_four_argument_registers(kind):
    row = census_row(**{f'df_r{r}': f'{0x100 + r:08x}' for r in range(4, 8)},
                     **{f'k{r}': kind for r in range(4, 8)})
    assert list(sites.census_operands(row, b'')) == [
        (f'df_r{r}', 0x100 + r) for r in range(4, 8)]


@pytest.mark.parametrize('kind', ['', 'unknown', 'unrecognized'])
def test_backtracking_and_unknown_dataflow_are_not_operand_proofs(kind):
    row = census_row(bt_r4='00000240', bt_r5='00000250', bt_r6='00000260',
                     df_r7='00000270', k7=kind)
    assert list(sites.census_operands(row, bytes(0x30))) == []


@pytest.mark.parametrize('kind', ['sp', 'copy'])
@pytest.mark.parametrize('transfer', [0xB036, 0xA036, 0x440B, 0x442B])
def test_fallback_holds_after_the_call_delay_slot(kind, transfer):
    row = census_row(df_r6='ffffffff', k6=kind, df_r7='00000270', k7=kind)
    # The export evaluates r6 after mov #-1,r6 in the slot.
    data = image_words({0x10: transfer, 0x12: 0xE6FF})
    assert list(sites.census_operands(row, data)) == [('df_r6', 0xFFFFFFFF), ('df_r7', 0x270)]


@pytest.mark.parametrize('kind', ['sp', 'copy'])
@pytest.mark.parametrize('words,size', [({0x10: 0xB036}, 0x12),
                                      ({0x10: 0x0009, 0x12: 0x0009}, 0x14),
                                      ({0x10: 0x8900, 0x12: 0x0009}, 0x14)])
def test_fallback_requires_a_complete_delayed_transfer(kind, words, size):
    row = census_row(df_r4='00000240', k4=kind)
    assert list(sites.census_operands(row, image_words(words, size))) == []


def write_rows(path, columns, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as target:
        writer = csv.DictWriter(target, columns)
        writer.writeheader()
        writer.writerows(rows)


@pytest.fixture
def bounded_code(tmp_path, monkeypatch):
    root = tmp_path / 'repo'
    root.mkdir()
    program = {0: 0xD47F, 2: 0x8544, 4: 0x000B, 6: 0x0009,
               0x10: 0xB036, 0x12: 0x66FC, 0x14: 0x000B, 0x16: 0x0009,
               0x20: 0x9020, 0x22: 0x000B, 0x24: 0x0009,
               0x80: 0x000B, 0x82: 0x0009, 0x90: 0x000B, 0x92: 0x0009}
    bodies = {0: (0, 2, 4, 6), 0x10: (0x10, 0x12, 0x14, 0x16),
              0x20: (0x20, 0x22, 0x24), 0x80: (0x80, 0x82), 0x90: (0x90, 0x92)}
    data = bytearray(image_words(program, 0x300))
    data[0x64:0x66] = bytes.fromhex('8000')
    # An opcode-shaped word outside L0 is data, not an established load.
    data[0x40:0x42] = bytes.fromhex('d46f')
    data[0x200:0x204] = (0x240).to_bytes(4, 'big')
    data[0x220:0x224] = (0x2A0).to_bytes(4, 'big')
    # The same word at a halfword-aligned site is no pointer-table entry.
    data[0x232:0x236] = (0x2A0).to_bytes(4, 'big')
    image_path = root / 'image.bin'
    image_path.write_bytes(data)
    image = SimpleNamespace(path=image_path, sha256=hashlib.sha256(data).hexdigest())
    row = census_row(df_r4='00000280', k4='pool', df_r5='00000270', k5='unknown',
                     df_r6='00000260', k6='dyn', df_r7='00000290', k7='copy',
                     bt_r4='000002c0')
    for layout in ('t1', 't2'):
        directory = root / repo.L0 / layout
        write_rows(directory / 'function_tokens.csv',
                   ('func_addr', 'ins_addr', 'ordinal'),
                   [dict(func_addr=f'{entry:08x}', ins_addr=f'{address:08x}', ordinal=i)
                    for entry, body in bodies.items() for i, address in enumerate(body)])
        write_rows(directory / 'function_references.csv',
                   ('func_addr', 'ins_addr', 'ref_addr', 'value_hex', 'width', 'ref_type'), [])
        write_rows(directory / 'function_signatures.csv',
                   ('addr', 'size', 'instructions', 'exact_sha256', 'mnemonic_sha256',
                    'shape_sha256'),
                   [dict(addr=f'{entry:08x}', size=2 * len(body), instructions=len(body),
                         exact_sha256=str(entry), mnemonic_sha256=str(entry),
                         shape_sha256=str(entry)) for entry, body in bodies.items()])
        write_rows(directory / l0.Census.file('90'), tuple(row), [row])
        (directory / l0.MANIFEST).write_text('synthetic manifest\n')
    (root / 'interp.csv').write_text('family,kernel,wrapper\n')
    monkeypatch.setattr(repo, 'layout', lambda layout, root=root:
                        SimpleNamespace(id=layout, image='T'))
    monkeypatch.setattr(repo, 'images', lambda root=root: {'T': image})
    monkeypatch.setattr(repo, 'config', lambda root=root: {})
    monkeypatch.setattr(l0, 'census', lambda layout, root=root:
                        l0.Census('interp.csv', ('00000090',), (), ()))

    def pairs(layout, root=root):
        return [pair for entry, body in bodies.items()
                for pair in derive.function_pairs(entry, body, bytes(data))]

    monkeypatch.setattr(derive, 'literal_pairs', pairs)
    for cached in (sites.references, sites.referenced, sites.bodies, sites.owners,
                   sites.linkers, match._code, match._image):
        cached.cache_clear()
    yield SimpleNamespace(root=root, data=bytes(data), row=row)
    for cached in (sites.references, sites.referenced, sites.bodies, sites.owners,
                   sites.linkers, match._code, match._image):
        cached.cache_clear()


def symbol_model(fixture, address, kind='tbl', owned=True):
    symbol = Symbol(SymbolKey('t1', kind, address),
                    props={'cols': 16, 'rows': 1, 'storage': 'uint8', 'width': 32},
                    sources={'kb/tbl/probe.toml'} if owned else {'legacy.csv'})
    model = Model({}, {symbol.key: symbol}, {}, {}, [])
    model.root = fixture.root
    return model, symbol


def verify(model, symbol, site, kind='l0', **keys):
    return match.verify(model, symbol, dict(kind=kind, supports='identity',
                                          at=f't1:{site:08x}', **keys))


def test_filtered_arguments_are_shared_by_references_linkers_and_code(bounded_code):
    root = bounded_code.root
    found = sites.references('t1', root)
    assert {0x280, 0x290, 0x80, 0x90} <= found[0x10]
    assert not {0x260, 0x270, 0x2C0} & found[0x10]
    linked = set(sites.linkers('t1', root))
    assert {(address, owner) for address in (0x280, 0x290)
            for owner in (0x10, 0x80, 0x90)} <= linked
    assert not any(address in {0x260, 0x270, 0x2C0} for address, _ in linked)
    code = match.Code.load('t1', root)
    assert {(0x280, 'operand:df_r4'), (0x290, 'operand:df_r7')} <= code.touches(0x10)
    assert not any(address in {0x260, 0x270, 0x2C0}
                   for address, _ in code.touches(0x10))


def test_effective_access_does_not_also_prove_its_literal_base(bounded_code):
    found = sites.references('t1', bounded_code.root)
    assert 0x240 in found[0]
    # Ledger site footprints keep the literal and its pool slot at the access.
    assert found[2] == {0x248, 0x240, 0x200}
    assert sites.references('t1', bounded_code.root, effective=True)[2] == {0x248}
    assert found[0x200] == {0x240}
    assert 0xFFFF8000 in found[0x20]
    model, symbol = symbol_model(bounded_code, 0x240)
    assert verify(model, symbol, 0) is None
    assert verify(model, symbol, 2) is not None
    assert verify(model, symbol, 2, 'indirect', mode='base', value=0) is not None
    _, accessed = symbol_model(bounded_code, 0x248)
    assert verify(model, accessed, 2) is None
    assert verify(model, accessed, 0, 'indirect', mode='base', value=8) is None
    assert verify(model, accessed, 0x200, 'indirect', mode='base', value=8) is None
    assert verify(model, accessed, 0, 'indirect', mode='base', value=4) is not None
    _, signed = symbol_model(bounded_code, 0xFFFF8000, 'ram')
    assert verify(model, signed, 0x20) is None


def test_exact_data_gate_keeps_legacy_span_and_function_body_rules(bounded_code):
    for kind in ('tbl', 'axis', 'const'):
        model, symbol = symbol_model(bounded_code, 0x240, kind)
        assert verify(model, symbol, 2) is not None
    model, legacy = symbol_model(bounded_code, 0x240, owned=False)
    assert verify(model, legacy, 2) is None
    model.file_evidence.add(legacy.key)
    assert verify(model, legacy, 2) is not None
    model, function = symbol_model(bounded_code, 0, 'fn')
    assert verify(model, function, 4) is None


def test_pointer_word_and_constant_own_pool_need_complete_exact_values(bounded_code):
    model, pointer_target = symbol_model(bounded_code, 0x2A0)
    assert verify(model, pointer_target, 0x220) is None
    assert verify(model, pointer_target, 0x221) is not None
    assert verify(model, pointer_target, 0x232) is not None
    assert verify(model, pointer_target, 0x2FE) is not None
    # A truncated zero word must not qualify even an address of zero.
    _, zero = symbol_model(bounded_code, 0)
    assert verify(model, zero, 0x2FE) is not None
    model, constant = symbol_model(bounded_code, 0x200, 'const')
    assert verify(model, constant, 0) is None
    assert verify(model, constant, 0x40) is not None
    _, table = symbol_model(bounded_code, 0x200)
    assert verify(model, table, 0) is not None


@pytest.mark.parametrize('address,accepted', [(0x280, True), (0x290, True),
                                           (0x260, False), (0x270, False), (0x2C0, False)])
def test_context_and_homology_use_the_same_filtered_arguments(
        bounded_code, monkeypatch, address, accepted):
    model, symbol = symbol_model(bounded_code, address)
    other = Symbol(SymbolKey('t2', 'tbl', address))
    meaning = Meaning('tbl', symbols={'t1': symbol, 't2': other})
    symbol.meaning = other.meaning = meaning
    monkeypatch.setattr(match, 'code', lambda layout, root=bounded_code.root:
                        match.Code.load(layout, root))
    failure = verify(model, symbol, 0x10, 'l0-context', key='reference',
                     value={'span': 1, 'named': []})
    assert (failure is None) == accepted
    ctx = match.context(model, symbol, {'at': 't1:00000010', 'to': 't2:00000010'})
    assert match._relation(ctx, 0x10, 0x10) == accepted
    failure = verify(model, symbol, 0x10, 'call-ordinal', to='t2:00000010',
                     value=0, count=1)
    assert (failure is None) == accepted


def test_independent_ghidra_reference_survives_rejected_census_cell(bounded_code):
    path = bounded_code.root / repo.L0 / 't1' / 'function_references.csv'
    write_rows(path, ('func_addr', 'ins_addr', 'ref_addr', 'value_hex', 'width', 'ref_type'),
               [dict(func_addr='00000010', ins_addr='00000010', ref_addr='00000260',
                     value_hex='', width='0', ref_type='data')])
    assert 0x260 in sites.references('t1', bounded_code.root)[0x10]
    model, symbol = symbol_model(bounded_code, 0x260)
    assert verify(model, symbol, 0x10) is None


@pytest.mark.parametrize('transfer,slot,owned,forwards', [
    (0xB036, 0x66FC, True, True),    # bsr; extu.b r15,r6
    (0x000B, 0x351C, True, True),    # rts; add r1,r5
    (0x430B, 0x66E3, True, True),    # jsr @r3; mov r14,r6
    (0x8D04, 0x66E3, True, True),    # bt/s; mov r14,r6
    (0x8F04, 0x351C, True, True),    # bf/s; add r1,r5
    (0x8904, 0x66E3, True, False),   # bt has no delay slot
    (0xB036, 0x66FC, False, False),  # the transfer lies in no L0 body
    (0x430B, 0x7408, True, False),   # add #8,r4 produces a new address
    (0xB036, 0xD47F, True, False),   # mov.l @(disp,pc),r4 produces a literal
    (0xB036, 0xE47F, True, False),   # mov #imm,r4 produces a constant
    (0xB036, 0x8544, True, False),   # mov.w @(4,r4),r0 accesses memory
    (0xB036, 0x0009, True, False),   # nop writes no register
    (0x0009, 0x66FC, True, False),   # no delayed transfer
])
def test_a_delay_slot_forwards_a_register_value(transfer, slot, owned, forwards):
    data = image_words({0x10: transfer, 0x12: slot})
    assert sites.forwards_in_slot(data, 0x12, {0x10} if owned else set()) is forwards


def test_forwarding_delay_slot_leaves_an_address_of_another_site_to_that_site(bounded_code):
    path = bounded_code.root / repo.L0 / 't1' / 'function_references.csv'
    # extu.b r15,r6 at 0x12 is the delay slot of bsr at 0x10, whose census
    # operand names 0x280. No other site of the body names 0x2E0.
    write_rows(path, ('func_addr', 'ins_addr', 'ref_addr', 'value_hex', 'width', 'ref_type'),
               [dict(func_addr='00000010', ins_addr='00000012', ref_addr=f'{address:08x}',
                     value_hex='', width='0', ref_type='data') for address in (0x280, 0x2E0)])
    assert {0x280, 0x2E0} <= sites.references('t1', bounded_code.root)[0x12]
    assert sites.references('t1', bounded_code.root, effective=True)[0x12] == {0x2E0}
    model, symbol = symbol_model(bounded_code, 0x280)
    assert verify(model, symbol, 0x12) is not None
    _, produced = symbol_model(bounded_code, 0x2E0)
    assert verify(model, produced, 0x12) is None


def test_jk00d_slot_additions_leave_the_site_to_the_producing_load():
    # add r14,r5 in the slots of the calls at 00075c70 and 00075c86 consumes
    # the address that mov.l at 00075c6a loads.
    raw = sites.references('jk00d')
    found = sites.references('jk00d', effective=True)
    for slot in (0x75C72, 0x75C88):
        assert 0x104A2 in raw[slot]
        assert 0x104A2 not in found.get(slot, ())
    assert 0x104A2 in found[0x75C6A]


def test_a_slot_sum_that_names_a_new_address_is_its_site():
    # add r2,r6 in the slot of the call at 0002a8b8 computes ffff155a from
    # ffff128c and 0x2ce; no earlier site of the body names it. The same sum
    # outside a slot at 0002a8b0 names ffff1558. portable-gecko and
    # solid-jackdaw follow the same pattern.
    found = sites.references('7mfk', effective=True)
    assert 0xFFFF155A in found[0x2A8BA]
    assert 0xFFFF1558 in found[0x2A8B0]
    assert 0xFFFF224E in found[0x2BEF8]
    assert 0xFFFF301C in found[0xB2C8A]


def test_decoded_literal_survives_a_rejected_fallback_at_the_same_site(bounded_code):
    row = census_row(0, df_r4='00000240', k4='sp')
    write_rows(bounded_code.root / repo.L0 / 't1' / l0.Census.file('90'),
               tuple(row), [bounded_code.row, row])
    assert list(sites.census_operands(row, bounded_code.data)) == []
    assert 0x240 in sites.references('t1', bounded_code.root)[0]
    assert (0x240, 'literal') in match.Code.load('t1', bounded_code.root).touches(0)


def test_changing_shared_filter_source_invalidates_persisted_match_cache(
        bounded_code, monkeypatch, tmp_path):
    package = tmp_path / 'producer'
    package.mkdir()
    for name in match.SOURCES:
        (package / name).write_text(f'{name}: initial producer\n')
    monkeypatch.setattr(match, 'PACKAGE', package)
    loader = Mock(side_effect=[SimpleNamespace(revision=1), SimpleNamespace(revision=2)])
    monkeypatch.setattr(match.Code, 'load', loader)
    assert match.code('t1', bounded_code.root).revision == 1
    match._code.cache_clear()
    assert match.code('t1', bounded_code.root).revision == 1
    assert loader.call_count == 1
    (package / 'sites.py').write_text('updated shared census filter\n')
    match._code.cache_clear()
    assert match.code('t1', bounded_code.root).revision == 2
    assert loader.call_count == 2


def test_apply_refuses_an_interior_site_before_writing_sources_or_graph(tmp_path, monkeypatch):
    from kb import adapters, compile, store, write
    from kb.adapters import files
    from tools.kb.tests import writer_sources

    root = tmp_path / 'writer'
    writer_sources.write_sources(root)
    path = store.path_of('tbl', 'astute-toad')
    document = store.load(root, path)
    document['cols'] = 16
    (root / path).write_text(store.render('tbl', document))
    references = root / repo.L0 / '7mfk' / 'function_references.csv'
    with references.open('a') as target:
        target.write('00010000,00010000,0,fixture_ref,00011ff7,0,,CONTROLLED\n')
    before = (root / path).read_bytes()
    monkeypatch.setattr(adapters, 'ADAPTERS', (files,))
    base = compile.build(root)
    assert write._issues(base) == {}
    monkeypatch.setattr(write.lock, 'held', lambda root: contextlib.nullcontext())
    monkeypatch.setattr(write.graph, 'fresh',
                        lambda *args, **keys: contextlib.nullcontext('isolated'))
    monkeypatch.setattr(write, 'graph_resolver',
                        lambda session, model, *args: write.model_resolver(model))
    written, synced = Mock(), Mock()
    monkeypatch.setattr(write.store, 'write', written)
    monkeypatch.setattr(write.graph, 'sync_held', synced)
    operation = {'cmd': 'set', 'ref': 'astute-toad/tbl', 'layout': '7mfk',
                 'keys': {'evidence': [{'kind': 'l0', 'supports': 'identity',
                                        'at': '7mfk:00010000'}]}}
    with pytest.raises(repo.KbError, match='nothing is written') as failure:
        write.apply([operation], root, log=lambda message: None)
    assert 'holds no reference to 00011ff6 at 00010000' in str(failure.value)
    assert (root / path).read_bytes() == before
    written.assert_not_called()
    synced.assert_not_called()
