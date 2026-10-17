"""Native scope and controlled refusals; these tests grant no execution receipt."""
import importlib
import json
import hashlib
from copy import deepcopy

import pytest

from kb import compile, copy_evidence as common, injection_copy_evidence as proof
from kb import injection_copy_matrix as matrix, repo, sid22_evidence
from kb.model import SymbolKey
from tools.kb.tests.test_copy_evidence import qualified as shared_qualified


def original_model():
    model = compile.build(repo.ROOT)
    # Test the original claim baseline both before and after native publication.
    for row in proof.MEMBERS:
        symbol = model.symbols[SymbolKey('7mfk', 'ram', row[0])]
        relation = proof.link(model, symbol, row)
        relation.evidence[:] = [entry for entry in relation.evidence if entry != proof.member_item(row)]
    return model


@pytest.fixture(scope='module')
def native():
    return original_model()


def test_twenty_original_claims_and_all_declared_widths_match(native):
    from kb import checks
    descriptor = proof.descriptor()
    assert len(descriptor['member']) == 20
    assert sum(row[3] is None for row in proof.MEMBERS) == 7
    for row in proof.MEMBERS:
        symbol = native.symbols[SymbolKey('7mfk', 'ram', row[0])]
        assert proof.member(native, symbol) == row
        relation = proof.link(native, symbol, row)
        assert not any(proof.registered(item) for item in relation.evidence)
        assert common.registered(proof.member_item(row), symbol)
        assert not list(checks._evidence_issues([proof.member_item(row)], proof.DESCRIPTOR, row[2], True))


def test_exact_publication_preserves_all_three_supported_fact_scopes(native):
    original = (common.scope_digest(native), proof.scope_digest(native), sid22_evidence.scope_digest(native))
    links = []
    try:
        for row in proof.MEMBERS:
            symbol = native.symbols[SymbolKey('7mfk', 'ram', row[0])]
            relation = proof.link(native, symbol, row)
            links.append((relation, list(relation.evidence)))
            relation.evidence.append(proof.member_item(row))
        assert (common.scope_digest(native), proof.scope_digest(native), sid22_evidence.scope_digest(native)) == original
    finally:
        for relation, evidence in links:
            relation.evidence[:] = evidence


@pytest.mark.parametrize('index', [0, 1, 4, 5, 8, 12, 19])
@pytest.mark.parametrize('fault', ['width', 'signed', 'note', 'slot', 'offset', 'source', 'duplicate', 'wrong-proof'])
def test_changed_native_claims_and_wrong_publication_metadata_fail(native, index, fault, monkeypatch):
    row = proof.MEMBERS[index]
    symbol = native.symbols[SymbolKey('7mfk', 'ram', row[0])]
    relation = proof.link(native, symbol, row)
    if fault in ('width', 'signed'):
        props = dict(symbol.props)
        props[fault] = 32 if fault == 'width' else not bool(row[4])
        monkeypatch.setattr(symbol, 'props', props)
    elif fault == 'note':
        monkeypatch.setattr(relation, 'props', {**relation.props, 'note': 'another fact'})
    elif fault in ('slot', 'offset'):
        monkeypatch.setattr(relation, fault, 3)
    elif fault == 'source':
        monkeypatch.setattr(relation, 'sources', {'kb/ram/other.toml'})
    else:
        item = proof.member_item(row)
        evidence = ([*relation.evidence, item, item] if fault == 'duplicate' else
                    [*relation.evidence, {**item, 'value': {**item['value'], 'width_bits': 32}}])
        monkeypatch.setattr(relation, 'evidence', evidence)
    with pytest.raises(ValueError):
        proof.member(native, symbol)
        proof.link(native, symbol, row)
        proof.scope_digest(native)
    assert proof.failure(proof.member_item(row), symbol, native, 'identity') is not None


@pytest.mark.parametrize('context', [None, 'scale', 'unit', 'confidence'])
def test_snapshot_proof_supports_only_identity_context(native, context, monkeypatch):
    row = proof.MEMBERS[0]
    symbol = native.symbols[SymbolKey('7mfk', 'ram', row[0])]
    relation = proof.link(native, symbol, row)
    monkeypatch.setattr(relation, 'evidence', [*relation.evidence, proof.member_item(row)])
    monkeypatch.setattr(common, 'failure', lambda *args, **kwargs: None)
    assert proof.failure(proof.member_item(row), symbol, native, 'identity') is None
    assert proof.failure(proof.member_item(row), symbol, native, context) is not None


def test_snapshot_receipt_depends_on_shared_CAN_original_terminal(native, monkeypatch):
    row = proof.MEMBERS[0]
    symbol = native.symbols[SymbolKey('7mfk', 'ram', row[0])]
    relation = proof.link(native, symbol, row)
    monkeypatch.setattr(relation, 'evidence', [*relation.evidence, proof.member_item(row)])
    calls = []
    def refuse(item, can_symbol, model, claim, *, record):
        calls.append((item, can_symbol.key, model, claim, record))
        return 'original terminal unavailable'
    monkeypatch.setattr(common, 'failure', refuse)
    assert proof.failure(proof.member_item(row), symbol, native, 'identity', record={'controlled': True}) == 'original terminal unavailable'
    assert len(calls) == 1 and calls[0][0] == common.item('reader')
    assert calls[0][1] == SymbolKey('7mfk', 'ram', 0xffff419b)


def observation():
    """A controlled zero-length helper call with explicit raw sentinel states."""
    index = 1304
    case = matrix.cases()[index]
    assert case[:11] == [0x22558, 0xffff4000, 0xffff5000, 0, 0, 0, 0, 0, 0, 1, 0]
    registers, context = list(case[12]), list(case[11])
    sr, continuation, sp = 0x700000f0, 0x123456, 0x02010000
    frame = bytearray(range(96))
    after = bytearray(frame)
    for offset, value in ((60, 0x01004000), (56, context[3]), (52, context[4])):
        after[offset:offset + 4] = value.to_bytes(4, 'big')
    abi = [0x18283848, 0x19293949, 0x1a2a3a4a, 0x1b2b3b4b, 0x1c2c3c4c,
           0x1d2d3d4d, 0x1e2e3e4e, 0x12344321, 0x10203040, 0x50607080, sp, 0x987654]
    return index, case, dict(index=index, entry=0x22558, source=0xffff4000, destination=0xffff5000, length=0,
        incoming=context, incoming_after=list(context), gbr=0x456789ab, mach=0x13579bdf, macl=0x2468ace0, entry_t=0,
        gbr_after=0x456789ab, mach_after=0x13579bdf, macl_after=0x2468ace0, entry_t_after=0,
        exit=[sr | 1, continuation, 0x2468ace0, 0x13579bdf, 0x456789ab, *reversed(registers)],
        sp=sp - 164, continuation=continuation, sr_before=sr, abi_before=abi, abi_after=list(abi),
        frame_before=frame.hex(), frame_after=after.hex(), source_before='', source_after='',
        destination_before='', destination_after='', pools_before='01002330010023bc',
        pools_after='01002330010023bc', outside_changes=[])


def test_controlled_zero_length_preserves_its_complete_state():
    index, case, value = observation()
    state = matrix.validate_observation(index, case, value)
    assert len(state) == 65536
    assert state[0x4000:0x4004] == bytes((0x5d + i * 19 + (i >> 8) + index) & 255 for i in range(0x4000, 0x4004))


@pytest.mark.parametrize('field', sorted(observation()[2]))
@pytest.mark.parametrize('fault', ['missing', 'changed', 'wrong-type'])
def test_raw_observation_refuses_each_missing_changed_or_wrongly_typed_field(field, fault):
    index, case, value = observation()
    if fault == 'missing':
        del value[field]
    elif fault == 'wrong-type':
        value[field] = True
    elif type(value[field]) is int:
        value[field] ^= 1
    elif type(value[field]) is str:
        value[field] = '00' + value[field]
    elif value[field]:
        value[field][0] ^= 1
    else:
        value[field] = [[1, 2, 3]]
    with pytest.raises(ValueError):
        matrix.validate_observation(index, case, value)


def test_original_header_matches_independently_generated_order(monkeypatch, tmp_path):
    monkeypatch.syspath_prepend(str(repo.ROOT / 'tools/sh-elf-run'))
    bridge = importlib.import_module('injection_snapshot_copy')
    value = bridge.snapshot(repo.ROOT, tmp_path)
    assert value['cases'] == matrix.cases() and len(value['cases']) == 1700
    for path, data in value['consumed'].items():
        assert (tmp_path / 'injection-copy-consumed' / path).read_bytes() == data


@pytest.mark.parametrize('fault', ['missing', 'duplicate', 'reordered', 'wrong-case', 'wrong-key', 'no-marker', 'duplicate-marker'])
def test_actual_output_parser_refuses_wrong_collection_and_marker(monkeypatch, fault):
    monkeypatch.syspath_prepend(str(repo.ROOT / 'tools/sh-elf-run'))
    bridge = importlib.import_module('injection_snapshot_copy')
    index, case, value = observation()
    monkeypatch.setattr(bridge, 'EARLY', (index,))
    packet = bridge.PREFIX + json.dumps(value)
    marker = 'VQ_SH_ELF_INJECTION_SNAPSHOT_CAPTURE cases=1 early=true'
    lines = [packet, marker]
    if fault == 'missing': lines = [marker]
    if fault == 'duplicate': lines.insert(0, packet)
    if fault == 'reordered': monkeypatch.setattr(bridge, 'EARLY', (index + 1,))
    if fault == 'wrong-case': lines[0] = bridge.PREFIX + json.dumps({**value, 'index': 0})
    if fault == 'wrong-key': lines[0] = lines[0].replace('"index": 1304', '"index": 1304, "index": 1304')
    if fault == 'no-marker': lines = [packet]
    if fault == 'duplicate-marker': lines.append(marker)
    with pytest.raises(ValueError):
        bridge.observe('\n'.join(lines), {'cases': matrix.cases()}, early=True)


@pytest.fixture
def bounded_packet(monkeypatch):
    """Control only matrix size to test exact reconstruction/receipt fields."""
    monkeypatch.syspath_prepend(str(repo.ROOT / 'tools/sh-elf-run'))
    bridge = importlib.import_module('injection_snapshot_copy')
    image = repo.images()['JK08A']
    data = image.path.read_bytes()
    index, case, observed = observation()
    observed['index'] = 0
    monkeypatch.setattr(matrix, 'cases', lambda: [case])
    boundary = bytes.fromhex('57f6472a000b0009')
    fixture = bytearray(data)
    fixture[0x213a0:0x213a8] = bytes.fromhex('01002330010023bc')
    fixture[0x2131c:0x2131c + len(boundary)] = boundary
    consumed = {path: (repo.ROOT / path).read_bytes() for path in bridge.CONSUMED}
    inputs = {path: hashlib.sha256(value).hexdigest() for path, value in consumed.items()}
    packet = dict(region=proof.REGION, cases=[case], observations=[observed],
        consumed={path: value.hex() for path, value in consumed.items()}, image_sha256=image.sha256,
        code=[dict(start=start, end=end, stock=data[start:end].hex(), reconstructed=data[start:end].hex())
              for start, end in ((0x21314, 0x2131c), (0x22558, 0x22590))],
        pools=[dict(address=0x213a0, stock=data[0x213a0:0x213a8].hex(),
                    reconstructed=data[0x213a0:0x213a8].hex())],
        aliases=[[0x213a0, 0xffff2330, 0x01002330], [0x213a4, 0xffff23bc, 0x010023bc]],
        entry=dict(r11=0x22558, r12=140, caller=0x21314, callsite=0x21318,
                   delay_slot=0x2131a, source=matrix.SOURCE, destination=matrix.DESTINATION, length=140),
        boundary=dict(address=0x2131c, bytes=boundary.hex()),
        fixture_sha256=hashlib.sha256(fixture).hexdigest(), elf_sha256='c' * 64,
        toolchain=dict(simulator_version='16.3', gcc_version='13.3.0',
                       binaries={name: 'e' * 64 for name in ('as', 'ld', 'objcopy', 'gcc', 'run')}))
    return packet, inputs


@pytest.mark.parametrize('fault', ['none', 'region', 'case-count', 'case-type', 'observation-count',
    'observation', 'consumed-missing', 'consumed-bytes', 'image', 'code', 'pool', 'alias', 'entry',
    'boundary', 'fixture', 'ELF', 'simulator', 'compiler', 'binary-count', 'binary-hash'])
def test_reconstructed_packet_refuses_changed_execution_bindings(bounded_packet, fault):
    packet, inputs = bounded_packet
    if fault == 'region': packet['region'] = 'another'
    if fault == 'case-count': packet['cases'] = []
    if fault == 'case-type': packet['cases'] = deepcopy(packet['cases']); packet['cases'][0][4] = False
    if fault == 'observation-count': packet['observations'] = []
    if fault == 'observation': packet['observations'][0]['exit'][0] ^= 1
    if fault == 'consumed-missing': packet['consumed'].pop(proof.DESCRIPTOR)
    if fault == 'consumed-bytes': packet['consumed'][proof.DESCRIPTOR] = '00'
    if fault == 'image': packet['image_sha256'] = 'a' * 64
    if fault == 'code': packet['code'][0]['reconstructed'] = '0009' * 4
    if fault == 'pool': packet['pools'][0]['reconstructed'] = '00000000' * 2
    if fault == 'alias': packet['aliases'][0][2] += 4
    if fault == 'entry': packet['entry']['r12'] = 12
    if fault == 'boundary': packet['boundary']['bytes'] = '000b0009'
    if fault == 'fixture': packet['fixture_sha256'] = 'b' * 64
    if fault == 'ELF': packet['elf_sha256'] = 'not a digest'
    if fault == 'simulator': packet['toolchain']['simulator_version'] = 'other'
    if fault == 'compiler': packet['toolchain']['gcc_version'] = 'other'
    if fault == 'binary-count': packet['toolchain']['binaries'].pop('run')
    if fault == 'binary-hash': packet['toolchain']['binaries']['as'] = False
    if fault == 'none':
        proof.validate_witness(packet, inputs, repo.ROOT)
    else:
        with pytest.raises((ValueError, KeyError)):
            proof.validate_witness(packet, inputs, repo.ROOT)


@pytest.mark.parametrize('index', range(20))
def test_only_exact_proof_append_retires_each_original_review(native, monkeypatch, index):
    row = proof.MEMBERS[index]
    before_symbol = native.symbols[SymbolKey('7mfk', 'ram', row[0])]
    old_claim = deepcopy(common.claim_fields(proof.link(native, before_symbol, row), '7mfk'))
    after = original_model()
    symbol = after.symbols[before_symbol.key]
    proof.link(after, symbol, row).evidence.append(proof.member_item(row))
    monkeypatch.setattr(common, 'failure', lambda *args, **kwargs: None)
    assert proof.retires(native, after, old_claim)
    assert common.retires(native, after, old_claim)
    assert after.config['reconciliation'] == native.config['reconciliation']


@pytest.mark.parametrize('fault', ['missing', 'duplicate', 'note', 'width', 'scope', 'other-evidence'])
def test_review_retirement_refuses_other_fact_or_evidence_changes(native, monkeypatch, fault):
    row = proof.MEMBERS[0]
    before_symbol = native.symbols[SymbolKey('7mfk', 'ram', row[0])]
    old_claim = deepcopy(common.claim_fields(proof.link(native, before_symbol, row), '7mfk'))
    after = original_model()
    symbol = after.symbols[before_symbol.key]
    relation = proof.link(after, symbol, row)
    relation.evidence.append(proof.member_item(row))
    if fault == 'missing': relation.evidence.pop()
    if fault == 'duplicate': relation.evidence.append(proof.member_item(row))
    if fault == 'note': relation.props['note'] = 'changed original fact'
    if fault == 'width': symbol.props['width'] = 32
    if fault == 'scope': relation.evidence[-1]['value']['offset_bytes'] += 1
    if fault == 'other-evidence': relation.evidence.append(dict(kind='spec', path='defs/other.md'))
    monkeypatch.setattr(common, 'failure', lambda *args, **kwargs: None)
    assert not proof.retires(native, after, old_claim)


@pytest.mark.parametrize('route', ['verify', 'rank', 'anchor', 'access'])
@pytest.mark.parametrize('fault', ['none', 'missing-receipt', 'source', 'terminal', 'stream',
    'shared-packet', 'width', 'original-note', 'proof-scope', 'old-schema'])
def test_shared_receipt_consumer_routes_refuse_each_invalid_snapshot_context(
        native, shared_qualified, monkeypatch, route, fault):
    """Use the controlled CAN terminal fixture, not a production qualification."""
    from kb import match
    state = shared_qualified
    model = original_model()
    model.root = state.root
    row = proof.MEMBERS[0]
    symbol = model.symbols[SymbolKey('7mfk', 'ram', row[0])]
    relation = proof.link(model, symbol, row)
    item = proof.member_item(row)
    relation.evidence.append(item)
    monkeypatch.setattr(common, 'scope_digest', lambda model: state.candidate['scope'])
    if route == 'anchor':
        # Other native L0/TEST anchors belong to their own contracts and require
        # the real repository. This controlled receipt root tests only this item.
        original_rank = match.rank
        monkeypatch.setattr(match, 'rank', lambda evidence, *args, **kwargs:
            original_rank(evidence, *args, **kwargs) if proof.registered(evidence) else -1)
    def award():
        if route == 'verify': return match.verify(model, symbol, item) is None
        if route == 'rank': return match.rank(item, symbol, model, 'identity') == match.vocab.LEVEL_RANK['code']
        if route == 'anchor': return match._anchor(model, symbol, []) == match.vocab.LEVEL_RANK['code']
        return common.accepted(model, symbol, model.symbols[proof.FUNCTION], common.claim_fields(relation, '7mfk')) is not None
    assert award()
    if fault == 'missing-receipt': (state.root / common.RECEIPT).unlink()
    if fault == 'source': state.source.write_bytes(b'changed')
    if fault == 'terminal': (state.root / 'process.json').write_bytes(b'{}')
    if fault == 'stream': (state.root / 'stderr.txt').write_bytes(b'changed')
    if fault == 'shared-packet':
        record = deepcopy(state.record)
        record['candidate']['witness']['snapshot'] = {}
        state.save(record)
    if fault == 'width': symbol.props['width'] = 32
    if fault == 'original-note': relation.props['note'] = 'another original fact'
    if fault == 'proof-scope': item['value']['offset_bytes'] += 1
    if fault == 'old-schema':
        record = deepcopy(state.record)
        record['candidate']['schema'] = 1
        state.save(record)
    assert award() is (fault == 'none')
