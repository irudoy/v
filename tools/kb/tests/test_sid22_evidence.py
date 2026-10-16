"""Descriptor and ownership refusals; these are not execution receipts."""

from copy import deepcopy
import tomllib

import pytest

from kb import compile, repo, sid22_evidence as proof
from kb import sid22_matrix as matrix
from kb.model import Builder, SymbolKey


@pytest.fixture(scope='module')
def contract():
    return proof.descriptor()


@pytest.fixture
def declaration():
    return tomllib.loads((repo.ROOT / proof.DESCRIPTOR).read_text())


def test_complete_body_and_pools_include_natural_return(contract):
    assert sum(end - start for start, end in contract.body) == 1256
    assert contract.body[-1] == (0x32864, 0x328b8)
    assert (0x328b8, 4) in contract.pools and (0x328bc, 4) in contract.pools
    assert len(contract.members) == 50 and len(contract.bindings) == 55


def test_paired_slots_are_nonadjacent_independent_sources(contract):
    rows = [row for row in contract.bindings if row.did == 0x130d]
    assert len(rows) == 2
    assert {row.source_offset for row in rows} == {0, 1}
    assert {row.read_addresses for row in rows} == {(0xffff2a83, 0xffff2a81)}
    assert {contract.member(row.member).address for row in rows} == {0xffff2a81, 0xffff2a83}


@pytest.mark.parametrize('fault', [
    'schema-bool', 'layout', 'image', 'entry', 'legacy-prefix', 'missing-return-range',
    'missing-return-pool', 'missing-pool-load', 'instruction-range', 'pool-value',
    'table-byte', 'table-stride', 'invented-family11-bound', 'family13-order',
    'member-added', 'member-width', 'claim-hash', 'binding-omitted', 'wrong-slot',
    'paired-swap', 'record-stride', 'unsupported-selector',
])
def test_descriptor_refuses_changed_boundaries_or_selectors(declaration, fault):
    value = deepcopy(declaration)
    if fault == 'schema-bool': value['schema'] = True
    elif fault == 'layout': value['layout'] = '1nd'
    elif fault == 'image': value['image_sha256'] = '0' * 64
    elif fault == 'entry': value['entry'] += 2
    elif fault == 'legacy-prefix': value['backing_end'] = value['entry'] + 1256
    elif fault == 'missing-return-range': value['code'].pop()
    elif fault == 'missing-return-pool': value['pool'].pop()
    elif fault == 'missing-pool-load': value['pool'][0]['loads'].pop()
    elif fault == 'instruction-range': value['code'][0]['end'] -= 2
    elif fault == 'pool-value': value['pool'][0]['value'] ^= 1
    elif fault == 'table-byte': value['table'][0]['sha256'] = '0' * 64
    elif fault == 'table-stride': value['table'][0]['stride'] = 8
    elif fault == 'invented-family11-bound': value['table'][0]['firmware_index_bound'] = 'before-load'
    elif fault == 'family13-order': value['table'][2]['firmware_index_bound'] = 'before-load'
    elif fault == 'member-added': value['member'].append(deepcopy(value['member'][0]))
    elif fault == 'member-width': value['member'][0]['declared_width'] = 32
    elif fault == 'claim-hash': value['member'][0]['claim_sha256'] = '0' * 64
    elif fault == 'binding-omitted': value['binding'].pop()
    elif fault == 'wrong-slot': value['binding'][0]['source_offset'] = 1
    elif fault == 'paired-swap':
        row = next(row for row in value['binding'] if row['did'] == 0x130d)
        row['source_offset'] = 1 - row['source_offset']
    elif fault == 'record-stride': value['binding'][0]['record'] += 4
    elif fault == 'unsupported-selector': value['binding'][0]['did'] = 0x120b
    with pytest.raises(ValueError):
        proof.descriptor(value=value)


def model_of(contract):
    config = repo.config()
    functions = {'7mfk': frozenset({proof.FUNCTION.address})}
    builder = Builder(repo.layouts(), compile.spaces(config), functions, {}, config)
    fn = builder.symbol('7mfk', 'fn', proof.FUNCTION.address, 'kb/fn/married-moth.toml')
    members, dids = {}, {}
    structural = {'stft_b1/ram', 'stft_b2/ram', 'ltft_b1/ram', 'ltft_b2/ram',
                  'app1/ram', 'app2/ram'}
    for member in contract.members:
        path = f'kb/ram/{member.meaning.split("/")[0]}.toml'
        symbol = builder.symbol('7mfk', 'ram', member.address, path)
        if member.declared_width is not None:
            builder.props(symbol, {'width': member.declared_width}, path)
        builder.link(symbol, 'reader', fn, path,
                     props=dict(layouts=['7mfk'],
                                relies='structure' if member.meaning in structural else 'level',
                                supports='identity'))
        members[member.meaning] = symbol
    source = 'tools/diagnostics/sid22_inventory.py'
    for binding in contract.bindings:
        if binding.record not in dids:
            symbol = builder.symbol('7mfk', 'did', binding.record, source)
            builder.props(symbol, dict(number=binding.did, width=len(binding.read_addresses)), source)
            dids[binding.record] = symbol
        builder.link(dids[binding.record], 'source', members[binding.member], source,
                     props={} if binding.source_offset is None else {'offset': binding.source_offset})
    model = builder.finish()
    model.root, model.config, model.functions = repo.ROOT, config, functions
    model.names, model.spaces, model.overlay = [], compile.spaces(config), {}
    model.symbols[fn].meaning.name = 'married-moth'
    for meaning, key in members.items():
        model.symbols[key].meaning.name = meaning.split('/')[0]
    for address, key in dids.items():
        model.symbols[key].meaning.name = f'sid22_{address:08x}'
    for link in model.links:
        if link.type == 'reader':
            link.evidence.append(proof.item(link.owner.key))
    return model


def test_all_exact_readers_bind_their_own_source_and_width(contract):
    model = model_of(contract)
    for member in contract.members:
        symbol = model.symbols[SymbolKey('7mfk', 'ram', member.address)]
        assert proof.validate_item(proof.item(member.meaning), symbol, model, contract=contract) == member


@pytest.mark.parametrize('fault', [
    'wrong-item-member', 'callsite', 'wrong-function', 'writer', 'missing-context',
    'scale', 'wrong-layout', 'changed-width', 'missing-item', 'duplicate-item',
    'role', 'offset', 'slot', 'changed-props', 'source-slot', 'source-missing',
    'DID-number', 'DID-width', 'unowned-symbol',
])
def test_reader_scope_refuses_semantic_or_source_rebinding(contract, fault):
    model = model_of(contract)
    member = contract.members[0]
    symbol = model.symbols[SymbolKey('7mfk', 'ram', member.address)]
    link = next(row for row in model.links if row.type == 'reader' and row.owner is symbol.meaning)
    evidence = link.evidence[0]
    claim = 'identity'
    if fault == 'wrong-item-member': evidence['value']['reader'] = contract.members[1].meaning
    elif fault == 'callsite': evidence['at'] = '7mfk:0003235e'
    elif fault == 'wrong-function': evidence['to'] = SymbolKey('7mfk', 'fn', 0x3235e)
    elif fault == 'writer': link.type = 'writer'
    elif fault == 'missing-context': claim = None
    elif fault == 'scale': claim = 'scale'
    elif fault == 'wrong-layout': symbol.key = SymbolKey('1nd', 'ram', member.address)
    elif fault == 'changed-width': symbol.props['width'] = 32
    elif fault == 'missing-item': link.evidence.clear()
    elif fault == 'duplicate-item': link.evidence.append(deepcopy(evidence))
    elif fault == 'role': link.roles.add('indexed_by')
    elif fault == 'offset': link.offset = 1
    elif fault == 'slot': link.slot = 'other'
    elif fault == 'changed-props': link.props['relies'] = 'structure'
    elif fault in ('source-slot', 'source-missing', 'DID-number', 'DID-width'):
        source = next(row for row in model.links if row.type == 'source' and row.to is symbol.meaning)
        if fault == 'source-slot': source.offset = 1
        elif fault == 'source-missing': model.links.remove(source)
        elif fault == 'DID-number': source.owner.props['number'] = 0x120b
        else: source.owner.props['width'] = 1
    elif fault == 'unowned-symbol': symbol = deepcopy(symbol)
    with pytest.raises(ValueError):
        proof.validate_item(evidence, symbol, model, claim, contract=contract)


@pytest.fixture(scope='module')
def cases(contract):
    return matrix.cases(contract, repo.images()['JK08A'].path.read_bytes())


def test_fixed_early_set_and_full_member_coverage(cases, contract):
    early = [cases[index] for index in matrix.early_indices(cases)]
    assert tuple(row['id'] for row in early) == matrix.EARLY_IDS
    assert len(early) == 9
    assert {row['did'] >> 8 for row in early if row['transport']} == {0x11, 0x12, 0x13}
    dids = {row['did'] for row in cases if row['transport']}
    assert dids == {row.did for row in contract.bindings}
    assert len(dids) == 53
    assert all(any(row['did'] == binding.did and member.address in row['sources']
                   for row in cases if row['transport'])
               for member in contract.members for binding in contract.bindings
               if binding.member == member.meaning)


def test_signed_start_and_untruncated_transport_end(cases):
    case = next(row for row in cases if row['id'] == 'did-1204-l04-iFB-v80')
    writes, end = matrix.publication(case)
    assert writes[-1] == (255, 0xda) and end == 256
    pair = next(row for row in cases if row['id'] == 'did-130D-l04-iFF-v80')
    assert pair['sources'] == [0xffff2a83, 0xffff2a81]
    assert pair['values'] == [0x80, 0xda]
    assert matrix.publication(pair)[0] == [(255, 0x62), (0, 0x13), (1, 0x0d), (2, 0x80), (3, 0xda)]


def controlled_observation(case):
    initial = [0x31] * 256
    final = list(initial)
    for offset, value in matrix.publication(case)[0]:
        final[offset] = value
    frame = [0xa3b4c5d6 + 17 * index for index in range(16)]
    continuation = 0x201234
    after = [*frame[:12], continuation, matrix.ABI[6], matrix.ABI[5], matrix.ABI[4]]
    return dict(index=case['index'], id=case['id'],
        stub_args=([case['start'] if case['start'] < 128 else case['start'] | 0xffffff00,
                    matrix.publication(case)[1]] if case['transport'] else [0x22, case['error']]),
        stub_count=1, stub_kind=1 if case['transport'] else 2,
        return_value=matrix.return_value(case), sources_before=list(case['values']),
        sources_after=list(case['values']), buffer_before=bytes(initial).hex(),
        buffer_after=bytes(final).hex(), ram_checked_bytes=65536,
        outside_writes_unchanged=True, lower_guard_unchanged=True,
        sp_before=0x200000, sp_after=0x200000, pr=continuation, continuation=continuation,
        frame_before=frame, frame_after=after, caller_abi_before=list(range(12)),
        caller_abi_after=list(range(12)), gpr=[matrix.return_value(case), *range(1, 8), *matrix.ABI],
        gbr=0x12344321, mach=0x10203040, macl=0x50607080, sr_before=0, sr_after=1)


def test_controlled_oracle_accepts_complete_ordered_matrix(cases):
    for case in cases:
        matrix.validate_observation(case, controlled_observation(case))


@pytest.mark.parametrize('fault', ['id', 'signed-argument', 'truncated-end', 'helper-count',
    'return', 'pair-order', 'source-changed', 'ring-neighbor', 'missing-RAM', 'outside-write',
    'SP', 'PR', 'lower-guard', 'saved-frame', 'caller-ABI', 'callee-saved', 'special-register', 'status'])
def test_execution_oracle_refuses_incomplete_or_wrong_observations(cases, fault):
    case = next(row for row in cases if row['id'] == 'did-130D-l04-iFB-v80')
    observed = controlled_observation(case)
    if fault == 'id': observed['index'] += 1
    elif fault == 'signed-argument': observed['stub_args'][0] = 251
    elif fault == 'truncated-end': observed['stub_args'][1] = 0
    elif fault == 'helper-count': observed['stub_count'] = 2
    elif fault == 'return': observed['return_value'] ^= 1
    elif fault == 'pair-order': observed['sources_before'].reverse()
    elif fault == 'source-changed': observed['sources_after'][0] ^= 1
    elif fault == 'ring-neighbor': observed['buffer_after'] = '00' + observed['buffer_after'][2:]
    elif fault == 'missing-RAM': observed['ram_checked_bytes'] -= 1
    elif fault == 'outside-write': observed['outside_writes_unchanged'] = False
    elif fault == 'SP': observed['sp_after'] += 4
    elif fault == 'PR': observed['pr'] += 2
    elif fault == 'lower-guard': observed['frame_after'][0] ^= 1
    elif fault == 'saved-frame': observed['frame_after'][12] += 2
    elif fault == 'caller-ABI': observed['caller_abi_after'][0] += 1
    elif fault == 'callee-saved': observed['gpr'][8] ^= 1
    elif fault == 'special-register': observed['mach'] ^= 1
    elif fault == 'status': observed['sr_after'] |= 0x100
    with pytest.raises(ValueError):
        matrix.validate_observation(case, observed)


def test_simulator_changes_only_explicit_pools_tables_and_external_stubs(contract, monkeypatch):
    monkeypatch.syspath_prepend(str(repo.ROOT / 'tools/sh-elf-run'))
    import sid22_pointer_read as driver
    stock = driver.image()
    changed, aliases = driver.fixture(stock, contract)
    allowed = set()
    for row in aliases:
        start = row['address']
        old, new = bytes.fromhex(row['before']), bytes.fromhex(row['after'])
        assert stock[start:start + len(old)] == old
        assert changed[start:start + len(new)] == new
        assert len(old) == len(new)
        allowed.update(range(start, start + len(new)))
    assert all(index in allowed for index, (old, new) in enumerate(zip(stock, changed)) if old != new)
    assert all(changed[start:end] == stock[start:end] for start, end in contract.body)
    word = next(row for row in aliases if row['address'] == 0x32474)
    assert word['before'] == '8005' and word['after'] == '2005'
    assert changed[0x2ec9a:0x2ec9a + 26] == matrix.stub_bytes(1, 0x2ec9a)
    assert changed[0x34114:0x34114 + 28] == matrix.stub_bytes(2, 0x34114)


def test_consumed_header_and_fixed_inputs_are_complete(contract, monkeypatch):
    monkeypatch.syspath_prepend(str(repo.ROOT / 'tools/sh-elf-run'))
    import sid22_pointer_read as driver
    assert (repo.ROOT / driver.CONSUMED[-1]).read_text() == driver.render_header(contract, driver.image())
    inputs = proof.inputs()
    assert set(driver.CONSUMED) <= inputs.keys()
    assert 'tools/kb/src/kb/sid22_matrix.py' in inputs
    assert 'tools/sh-elf-run/sid22_pointer_read.py' in inputs
    assert 'tools/kb/src/kb/sid22_witness.py' in inputs


def test_registered_primary_region_and_documented_counts_follow_execution(contract, monkeypatch):
    import re
    monkeypatch.syspath_prepend(str(repo.ROOT / 'tools/sh-elf-run'))
    import verify_stock_code as stock
    selected = [row for row in stock.REGIONS if row.key == proof.REGION]
    assert len(selected) == 1
    selected = selected[0]
    cases = matrix.cases(contract, repo.images()['JK08A'].path.read_bytes())
    assert selected.cases == len(cases)
    assert (selected.start, selected.end, *selected.callees[-1]) == (0x3235c, 0x32474, 0x32864, 0x328b8)
    assert dict(selected.constants)['EARLY_ONLY'] == 0
    text = (repo.ROOT / 'tools/sh-elf-run/README.md').read_text().split('## SID22 pointer-read witness')[1].split('## Repository-contained gate')[0]
    assert int(re.search(r'instruction bytes is (\d+)', text)[1]) == sum(end - start for start, end in contract.body)
    assert int(re.search(r'pins (\d+) original RAM', text)[1]) == len(contract.members)
    assert int(re.search(r'and (\d+) SOURCE', text)[1]) == len(contract.bindings)
    assert int(re.search(r'at (\d+) selected DIDs', text)[1]) == len({row.did for row in contract.bindings})
    assert int(re.search(r'defines (\d+) ordered cases', text)[1]) == len(cases)


def test_combined_candidate_requires_full_primary_success(monkeypatch, capsys):
    monkeypatch.syspath_prepend(str(repo.ROOT / 'tools/sh-elf-run'))
    import verify_map_switching as driver
    from kb import copy_witness, sid22_witness
    calls = []
    def full(**kwargs):
        calls.append('full')
        kwargs['copy_capture']['controlled'] = 'CAN'
        kwargs['sid22_capture']['controlled'] = 'SID22'
    for module, name in ((copy_witness, 'CAN'), (sid22_witness, 'SID22')):
        monkeypatch.setattr(module, 'begin', lambda root, name=name: dict(controlled=name))
        monkeypatch.setattr(module, 'finish', lambda before, actual, root: dict(before=before, actual=actual))
    monkeypatch.setattr(driver, 'verify', full)
    assert driver.main(['--can-copy-witness', '--sid22-witness']) == 0
    assert calls == ['full']
    lines = capsys.readouterr().out.splitlines()
    assert sum(line.startswith('kb-sid22-candidate ') for line in lines) == 1
    assert sum(line.startswith('kb-copy-candidate ') for line in lines) == 1
    def failed(**kwargs):
        raise ValueError('controlled primary failure')
    monkeypatch.setattr(driver, 'verify', failed)
    assert driver.main(['--can-copy-witness', '--sid22-witness']) == 1
    assert not capsys.readouterr().out


@pytest.mark.parametrize('name', ['can_latch_copy', 'sid22_pointer_read'])
def test_registered_case_checker_is_read_only_and_refuses_stale_output(tmp_path, monkeypatch, name):
    import importlib
    import sys
    monkeypatch.syspath_prepend(str(repo.ROOT / 'tools/sh-elf-run'))
    helper = importlib.import_module(name)
    contract = helper.proof.descriptor(repo.ROOT)
    if name == 'sid22_pointer_read':
        stock = helper.image()
        expected = helper.render_header(contract, stock)
        monkeypatch.setattr(helper, 'image', lambda: stock)
        target = tmp_path / 'sid22-pointer-read-cases.h'
    else:
        expected = helper.render_header(contract)
        target = tmp_path / 'can-latch-copy-cases.h'
    monkeypatch.setattr(helper.proof, 'descriptor', lambda root: contract)
    monkeypatch.setattr(helper, 'TOOL_DIR', tmp_path)
    monkeypatch.setattr(helper, 'ROOT', tmp_path)
    monkeypatch.setattr(sys, 'argv', [name, '--check'])
    target.write_text(expected)
    original = target.read_bytes()
    helper.main()
    assert target.read_bytes() == original
    target.write_text(expected + 'controlled stale row\n')
    changed = target.read_bytes()
    with pytest.raises(SystemExit, match='differs from its declared matrix'):
        helper.main()
    assert target.read_bytes() == changed
