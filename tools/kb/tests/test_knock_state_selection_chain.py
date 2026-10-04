"""Bind post-lookup widened state selection to distinct entry and wrap proofs."""

import builtins
from collections import Counter
from dataclasses import replace
import hashlib
import importlib.util
import re
import sys
from types import SimpleNamespace

import pytest

from kb import compile, derive, repo, sh2
from kb.arithmetic import Grammar
from kb.model import SymbolKey


KEY = 'jk08a-knock-state-selection'
SOURCE = 'stock_jk08a_knock_state_selection.s'
HARNESS = 'harness-stock-jk08a-knock-state-selection.c'
HEADER = 'stock-jk08a-knock-state-selection-cases.h'
SPEC = 'defs/JK08A.ignition-state.md'
THIS_TEST = 'tools/kb/tests/test_knock_state_selection_chain.py'
OWNER_TEST = 'test_knock_state_selection_chain_owner_contract'
STOCK_TEST = 'test_knock_state_selection_registered_stock_contract'
FUNCTION = SymbolKey('7mfk', 'fn', 0x493e8)
BUILDER = 'knock_function/fn'
FORMULA = (
    'H = x[0]; y = x[1]; D = (1-((uint8(ffff2469)>>7)&1))*((uint8(ffff2467)>>6)&1); '
    'S = int16(ffff1258); V = int16(ffff1380); N = uint8(ffff230a); '
    'Y = min(S+ROM16[0x00009078],max(S-ROM16[0x00009078],V)); '
    'R = D*(V+256*(H-(uint32(y)&127)))+(1-D)*min(0,max(Y,-256*N)); to = uint16(R)'
)
DIRECT_FORMULA = 'H = x[0]; y = x[1]; R = int16(ffff1380)+256*(H-(uint32(y)&127)); to = uint16(R)'
ALT_FORMULA = (
    'S = int16(ffff1258); V = int16(ffff1380); N = uint8(ffff230a); '
    'Y = min(S+ROM16[0x00009078],max(S-ROM16[0x00009078],V)); '
    'R = min(0,max(Y,-256*N)); to = uint16(R)'
)
CODE_SPANS = ((0x49614, 0x4964a), (0x499b8, 0x49a0e))
POOLS = ((0x9078, 2), (0x493fc, 4), (0x495da, 2), (0x495e8, 2),
         (0x495f6, 2), (0x495fa, 10), (0x49610, 4), (0x4965c, 4),
         (0x49678, 4), (0x496ac, 4), (0x496b4, 4), (0x496c0, 4),
         (0x496c4, 4), (0x499ae, 2), (0x49b28, 4), (0x49b2c, 4),
         (0x49b38, 4), (0x49b3c, 4))
RAM_LITERALS = (0x4965c, 0x49678, 0x496ac, 0x49b28, 0x49b2c, 0x49b38)
SPANS = (
    (0x49614, 0x4964a, 'e9891f8a4be137ef5f2da5493d9a07a287ba399265310161b73f4b030d0fbc17'),
    (0x499b8, 0x49a0e, '8fd16eefec37bbd4c1b9449d58824c5aa646077195ef64b1c26920915f6b6922'),
    (0x9078, 0x907a, '2921a11f25dadaa24aa79a548e4e81508c2e5e56af2d833d65e2bcce448ce2f5'),
    (0x493fc, 0x49400, '8cc188f5947dd577b582b9a689286706bcc5c901d64e44fc0a7122f9a27e8e05'),
    (0x495da, 0x495dc, '4751ec2f62d6c6007f1741f49c1e2b073ef2ac41d2c1ff3450cecab5ff9f27c1'),
    (0x495e8, 0x495ea, '3df55977beb9f50d9744110d61794090e4e94aeb8d6873fb5079a5896419be1f'),
    (0x495f6, 0x495f8, '148062bd6b48e291459ceb915db6f6f464f7f2f611d61d65ca1d69e24ddf1d57'),
    (0x495fa, 0x49604, '0a9794a8e1eebf3086d53bb2528f687185a9e7da457d85a72b2b574c21f36a93'),
    (0x49610, 0x49614, 'f7fa9573df3c330cb852b700d46bf2162d5dba082e2bb6057cc1837daed7eb1c'),
    (0x4965c, 0x49660, 'e913e0905d7083a2ef8deb6b8e97dab601058eddb95d192dad45ac9667035dbe'),
    (0x49678, 0x4967c, '4f7e96f2f3d19407e474f2d34b2db605ff768abffb7f78d34e14dae07a06b8b1'),
    (0x496ac, 0x496b0, '1dc771c9594c55f62b87b70affffd18d809c9ef1a530c5d8dd4ae5ecb24999cd'),
    (0x496b4, 0x496b8, '7b86a9688e07744bd053da653766790cfd0ef0e7dd6158031addd25a4107941e'),
    (0x496c0, 0x496c4, 'b959fe4bad122cb9c9e6df1f9d847be77b603d2a320751efef24d7d979306a5b'),
    (0x496c4, 0x496c8, '6f6227e219294a3dbe93618aa3f1ba6d05524beaa09eec47605c2764957d6c83'),
    (0x499ae, 0x499b0, '6199087871afe79e02b3bdab658497ed97d9e1c768f966f734e3f55b32d1b9e7'),
    (0x49b28, 0x49b2c, 'cec236a342262bbc5156539981a6ecd5056a5aa425be5cb55434dcc6699e14ab'),
    (0x49b2c, 0x49b30, '4f7e96f2f3d19407e474f2d34b2db605ff768abffb7f78d34e14dae07a06b8b1'),
    (0x49b38, 0x49b3c, '1dc771c9594c55f62b87b70affffd18d809c9ef1a530c5d8dd4ae5ecb24999cd'),
    (0x49b3c, 0x49b40, 'a1b5cc7287805846826d5318b0af08319e930fdac8604a54c0dde9b67925a783'),
)
OWNER_DEFINES = {
    'SOURCE_STATE': ('thick-dalmatian/ram', 0xffff1258),
    'TARGET_STATE': ('curious-mustang/ram', 0xffff1380),
    'NEGATIVE_BOUND': ('knock_state_negative_bound/ram', 0xffff230a),
    'GATE69': ('masked-inchworm/ram', 0xffff2469),
    'GATE67': ('glorious-spider/ram', 0xffff2467),
    'WORD_OUTPUT': ('knock_timing_state/ram', 0xffff121a),
    'BYTE_OUTPUT': ('steady-lionfish/ram', 0xffff22fa),
    'SLEW_STEP': ('knock_state_slew_step/tbl', 0x9078),
}
STEP_SOURCES = (SymbolKey('7mfk', 'ram', 0xffff1380),
                SymbolKey('7mfk', 'tbl', 0x9a1a), SymbolKey('7mfk', 'tbl', 0x9b1a))
LINK_CONTRACTS = (
    ('knock_timing_state/ram', 'input', 'thick-dalmatian/ram', None,
     'The alternative entry sign-extends S from ffff1258 at 000499bc through loaded base ffff124c plus 12. It forms Y=min(S+step,max(S-step,V)), then applies the N floor and zero cap. The source RAM is preserved; its preceding integration or producer is not executed by this selection envelope.'),
    ('knock_timing_state/ram', 'input', 'curious-mustang/ram', None,
     'Normal direct arithmetic reads signed V=ffff1380 at 00049644 and forms widened R2=V+256*(H-(incomingR0&127)). Alternative arithmetic reads the same signed target at 000499c4 and limits motion from S toward V. Both preserve this word; the preceding target publication is a separate entry.'),
    ('knock_timing_state/ram', 'input', 'knock_state_negative_bound/ram', None,
     'On alternative dispatch or standalone 000499b8, the unsigned byte N supplies floor -256*N. R=min(0,max(Y,-256*N)); N=128 can equal the signed lower endpoint but cannot force below it, and N>=129 cannot force within the signed input hull. Direct arithmetic does not read N.'),
    ('knock_timing_state/ram', 'input', 'knock_state_slew_step/tbl', None,
     'On alternative dispatch or standalone 000499b8, the unsigned scalar ROM16[00009078] supplies step in Y=min(S+step,max(S-step,V)). The floor and zero cap follow this limited signed target. Direct arithmetic does not read this scalar. Stock bytes and artificial contexts belong to distinct execution contracts.'),
    ('knock_timing_state/ram', 'selector', 'masked-inchworm/ram', 'bit7',
     'Normal entry 00049614 selects direct arithmetic only when this bit7 is clear and ffff2467.bit6 is set. A set bit7 dispatches to 000499b8. The byte is preserved; standalone alternative invocation does not read either gate byte.'),
    ('knock_timing_state/ram', 'selector', 'glorious-spider/ram', 'bit6',
     'Normal entry 00049614 reaches this bit6 test only with ffff2469.bit7 clear. A set bit6 selects the widened direct difference; a clear bit6 dispatches to 000499b8. Standalone alternative invocation does not read either gate byte.'),
    ('knock_timing_state/ram', 'lookup', 'high_octane_timing_state/tbl', None,
     'The bounded post-lookup entry 00049614 declares x[0]=H as the independent 0..127 byte at SP+0x0c. Static first-lookup/mask/store anchors 000495e8, 000495f6 and 000495fa are byte-bound but not executed. In normal direct arithmetic H contributes +256*H before low-word wrap. x[1]=y is the complete independent incoming R0; this link does not establish either executed lookup numeric value or their producers.'),
    ('knock_timing_state/ram', 'lookup', 'high_detonation_timing_state/tbl', None,
     'The bounded post-lookup entry 00049614 declares x[1]=y as full incoming R0 and executes AND 0x7f plus the second byte store at SP+0x10. Static table pointer, lookup JSR 00049610 and its delay slot are byte-bound but not executed. In normal direct arithmetic uint32(y)&127 contributes -256 times its value. x[0] is independently declared H; no executed lookup arithmetic or producer claim follows.'),
    ('knock_timing_state/ram', 'selector', 'knock_function/fn', None,
     'Normal post-lookup entry 00049614 receives x[0] as independent SP+0x0c byte H in 0..127 and x[1] as full incoming R0. The second AND 0x7f and store execute before reading bit7/bit6 gates. Standalone alternative entry 000499b8 uses S = int16(ffff1258); V = int16(ffff1380); N = uint8(ffff230a); Y = min(S+ROM16[0x00009078],max(S-ROM16[0x00009078],V)); R = min(0,max(Y,-256*N)); to = uint16(R); the gate bytes and x operands are not read by that invocation. These entries are alternative contexts, not sequential updates. Static lookup/first-mask/first-store anchors, natural PR from the unexecuted second lookup, full coordinator and hardware reachability remain separate facts.'),
    ('knock_timing_state/ram', 'writer', 'knock_function/fn', None,
     'At entry 0004964a, EXTS.W copies the signed low word of independent raw R2 to R12; MOV R2,R0 preserves the original low word. The BT/S delay-slot MOV.W at 00049656 stores that low word to ffff121a on both sign branches. The slice does not establish the preceding R2 calculation or a complete coordinator mode. The independent 70-instruction state-selection envelope produces widened R2 at boundary 0004964a and preserves all RAM. The separate 16-instruction conversion envelope executes EXTS.W and the raw uint16 low-word store at 00049656, followed by the byte conversion. Their evidence is not joint execution: selection supplies a mathematical R2 boundary and conversion supplies its independent low-word projection. No signed monotonicity follows across wrap, and the conversion sweep retains its per-256-case-block RAM observation limit.'),
    ('thick-dalmatian/ram', 'reader', 'knock_function/fn', None,
     'MOV.W at 00049548 and 00049906 reads sign16(ffff1258) through loaded base ffff124c plus offset 12. The bounded quiet and event entries both preserve this input word. They write ffff1380 and clear ffff2142; no ffff1258 store is executed in these spans. The separate bounded selection entry reads signed S at 000499bc, 000499d4 or 000499fe and preserves it while limiting movement toward V. Its full 64k RAM contract applies per case; no integration entry or producer is jointly executed.'),
    ('curious-mustang/ram', 'reader', 'knock_function/fn', None,
     'The bounded selection entry reads signed V at 00049644 on direct normal dispatch, or 000499c4 on alternative dispatch and standalone invocation. It preserves the word and exposes widened R2 before any low-word store. Existing integration publication evidence belongs to its separate entry.'),
    ('knock_state_negative_bound/ram', 'reader', 'knock_function/fn', None,
     'MOV.B 000499dc and EXTU.B 000499e2 read unsigned N through explicit R9=ffff22f8 plus 0x12. MUL.L establishes -256*N and the signed floor; the producing stores and R9 setup anchors are not executed by this envelope. No array size or hardware identity is inferred.'),
    ('masked-inchworm/ram', 'reader', 'knock_function/fn', None,
     'Normal entry reads this preserved byte at 0004961c and tests bit7 at 0004961e. The standalone alternative entry does not read it. The explicit GBR base is bound by unchanged 000493fc/0004965c context, without execution of that earlier setup.'),
    ('glorious-spider/ram', 'reader', 'knock_function/fn', None,
     'With bit7 clear, normal entry reads this preserved byte at 00049626 and tests bit6 at 00049628. The standalone alternative entry does not read it. Other byte bits and producer lifecycles remain outside the selection claim.'),
    ('knock_state_slew_step/tbl', 'reader', 'knock_function/fn', None,
     'Alternative arithmetic loads this unchanged ROM word at 000499cc and EXTU.W 000499ce supplies its unsigned step. Direct arithmetic does not read it. Other consumers, calibration design and engineering units are separate facts.'),
    ('knock_state_negative_bound/ram', 'base', 'hungry-sidewinder/ram', None,
     'Explicit incoming R9=ffff22f8 plus indexed 0x12 yields ffff230a at MOV.B 000499dc. Unchanged R9 anchors 000495da/000496ac and 000499ae/00049b38 bind that address but are not executed. The relation describes an address offset, not numeric input, array extent or an executed base producer.'),
)
CONVERSION_KEY = 'jk08a-knock-timing-byte'
CONVERSION_CODE = ((0x496cc, 0x496da), (0x4964a, 0x4965c))
CONVERSION_POOLS = ((0x495da, 2), (0x496ac, 4), (0x496c8, 4), (0x499ae, 2), (0x49b38, 4))
CONVERSION_SPANS = (
    (0x4964a, 0x4965c, '6c921f40efea9b8a41f21a343f443b12cbc0769b4985ce1d6451541ddc4b1b05'),
    (0x496cc, 0x496da, '77ceff8406269f87df5a9ff97c74664755ba94c857ce225eb24bb370c242f9cc'),
    (0x495da, 0x495dc, '4751ec2f62d6c6007f1741f49c1e2b073ef2ac41d2c1ff3450cecab5ff9f27c1'),
    (0x496ac, 0x496b0, '1dc771c9594c55f62b87b70affffd18d809c9ef1a530c5d8dd4ae5ecb24999cd'),
    (0x496c8, 0x496cc, 'b6ea3f1e90b525ff4bc3da46a8fb5d52ffe8605e1d80dcbc6e7976c14b81dce3'),
    (0x499ae, 0x499b0, '6199087871afe79e02b3bdab658497ed97d9e1c768f966f734e3f55b32d1b9e7'),
    (0x49b38, 0x49b3c, '1dc771c9594c55f62b87b70affffd18d809c9ef1a530c5d8dd4ae5ecb24999cd'),
)


def _verifier():
    name = 'knock_state_selection_stock_verifier'
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(
            name, repo.ROOT / 'tools/sh-elf-run/verify_stock_code.py')
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


def _region():
    [region] = [item for item in _verifier().REGIONS if item.key == KEY]
    return region


def _check_region(region):
    assert (region.key, region.rom, region.source, region.harness) == (KEY, 'JK08A', SOURCE, HARNESS)
    assert region.code_spans == CODE_SPANS and region.callees == CODE_SPANS[1:]
    assert region.pools == POOLS and region.ram_literals == RAM_LITERALS
    assert region.boundary is True and region.cases == 11615
    assert region.return_address_offset is None and region.return_register == 5
    assert region.base_load is None and region.bits == ()
    assert region.constants == (('POST_LOOKUP_ENTRY', 0x49614), ('ALTERNATIVE_ENTRY', 0x499b8))
    assert region.symbols == tuple((name, item[0]) for name, item in OWNER_DEFINES.items())


def _link(owner, kind, target, slot=None):
    [link] = [item for item in owner.links if item.type == kind
              and item.to.key == target and item.slot == slot]
    return link


def _proof(link):
    assert link.stated == {'7mfk'} and link.props['via'] == [FUNCTION]
    assert {(THIS_TEST, OWNER_TEST), (THIS_TEST, STOCK_TEST)} <= {
        (item.get('path'), item.get('key')) for item in link.evidence
        if item['kind'] == 'test'}


def _check_link_contract(link, contract):
    owner, kind, target, slot, note = contract
    assert (link.owner.key, link.type, link.to.key, link.slot) == (owner, kind, target, slot)
    _proof(link)
    assert ' '.join(link.props['note'].split()) == ' '.join(note.split())
    assert (link.props['relies'], link.props['supports']) == ('structure', 'identity')
    assert {'kind': 'spec', 'path': SPEC, 'key': 'Bounded knock state selection'} in link.evidence
    if kind == 'writer' or (kind == 'reader' and owner in (
            'curious-mustang/ram', 'masked-inchworm/ram', 'glorious-spider/ram')):
        assert (link.props['reverse_relies'], link.props['reverse_supports']) == ('structure', 'identity')
    if kind == 'reader' and owner in ('curious-mustang/ram', 'masked-inchworm/ram', 'glorious-spider/ram'):
        assert 'indexed_by' in link.roles
    assert link.offset == (0x12 if kind == 'base' else None)
    if kind == 'writer':
        assert {('tools/kb/tests/test_knock_timing_byte_chain.py', key) for key in (
            'test_knock_timing_byte_chain_owner_contract',
            'test_knock_timing_byte_registered_stock_contract')} <= {
            (item.get('path'), item.get('key')) for item in link.evidence if item['kind'] == 'test'}
        assert {'kind': 'spec', 'path': SPEC, 'key': 'Bounded timing-byte conversion'} in link.evidence


def _synthetic_link(contract):
    owner, kind, target, slot, note = contract
    props = dict(via=[FUNCTION], note=note, relies='structure', supports='identity')
    reverse = kind == 'writer' or (kind == 'reader' and owner in (
        'curious-mustang/ram', 'masked-inchworm/ram', 'glorious-spider/ram'))
    if reverse:
        props.update(reverse_relies='structure', reverse_supports='identity')
    evidence = [dict(kind='test', path=THIS_TEST, key=key) for key in (OWNER_TEST, STOCK_TEST)]
    evidence.append(dict(kind='spec', path=SPEC, key='Bounded knock state selection'))
    if kind == 'writer':
        evidence += [dict(kind='test', path='tools/kb/tests/test_knock_timing_byte_chain.py', key=key)
                     for key in ('test_knock_timing_byte_chain_owner_contract',
                                 'test_knock_timing_byte_registered_stock_contract')]
        evidence.append(dict(kind='spec', path=SPEC, key='Bounded timing-byte conversion'))
    roles = {'indexed_by'} if kind == 'reader' and reverse else set()
    return SimpleNamespace(owner=SimpleNamespace(key=owner), type=kind, to=SimpleNamespace(key=target),
                           slot=slot, offset=0x12 if kind == 'base' else None,
                           stated={'7mfk'}, props=props, evidence=evidence, roles=roles)


def _check_steps(steps):
    assert len(steps) == 3
    expected = zip(STEP_SOURCES, ('adds', 'looks-up', 'looks-up'),
                   (FORMULA, DIRECT_FORMULA, DIRECT_FORMULA))
    for step, (source, effect, note) in zip(steps, expected):
        assert (step['from'], step['to'], step['effect'], step['sign'], step['via']) == (
            source, SymbolKey('7mfk', 'ram', 0xffff121a), effect, 'none', [FUNCTION])
        assert Grammar(repo.config()).validate(step['note']) is None
        assert re.sub(r'\s+', '', step['note']) == re.sub(r'\s+', '', note)


def _notes():
    steps = compile.cached(repo.ROOT).entities[('chain', 'knock_retard')].steps[10:13]
    _check_steps(steps)
    return [step['note'] for step in steps]


def _conversion_region():
    [region] = [item for item in _verifier().REGIONS if item.key == CONVERSION_KEY]
    return region


def _check_conversion_region(region):
    assert (region.key, region.rom, region.source, region.harness) == (
        CONVERSION_KEY, 'JK08A', 'stock_jk08a_knock_timing_byte.s',
        'harness-stock-jk08a-knock-timing-byte.c')
    assert region.code_spans == CONVERSION_CODE and region.callees == CONVERSION_CODE[1:]
    assert region.pools == CONVERSION_POOLS and region.ram_literals == (0x496c8,)
    assert region.cases == 65650 and region.boundary is True
    assert region.return_address_offset is None and region.return_register == 5
    assert region.base_load is None and region.bits == ()
    assert region.constants == (('CONVERSION_ENTRY', 0x4964a),)
    assert region.symbols == (('WORD_STATE', 'knock_timing_state/ram'),
                              ('BYTE_STATE', 'steady-lionfish/ram'))
    assert (sum((end-start)//2 for start, end in region.code_spans),
            sum(end-start for start, end in region.code_spans)+sum(size for _, size in region.pools)) == (16, 48)


def _check_conversion_stock(data):
    for start, end, digest in CONVERSION_SPANS:
        assert hashlib.sha256(data[start:end]).hexdigest() == digest, f'{start:08x}'
    assert data[0x4964a:0x4964c] == bytes.fromhex('6c2f')
    assert sh2.decode(int.from_bytes(data[0x49656:0x49658], 'big'), 0x49656).access == (
        sh2.Access(8, 12, 2, 'store'))


def _check_conversion_binding(module, region, data):
    _check_conversion_region(region)
    _check_conversion_stock(data)
    defines = module.harness_defines(region, data)
    assert (defines['WORD_STATE'], defines['BYTE_STATE'], defines['CONVERSION_ENTRY']) == (
        0xffff121a, 0xffff22fa, 0x4964a)
    fixture = module.build_fixture(region, data)
    for start, end in CONVERSION_CODE:
        assert fixture[start:end] == data[start:end]
    for start, size in CONVERSION_POOLS:
        expected = data[start:start+size]
        if start == 0x496c8:
            expected = module.base_verifier.alias_high_ram(int.from_bytes(expected, 'big')).to_bytes(4, 'big')
        assert fixture[start:start+size] == expected
    assert fixture[0x496da:0x496de] == bytes.fromhex('000b0009')


def _rows(header):
    [body] = re.findall(r'\bselection_cases\[\]\s*=\s*\{(.*?)\n\};', header, re.S)
    rows = []
    for line in body.splitlines():
        if not line.strip():
            continue
        match = re.fullmatch(r'\s*\{([^{}]+),\s*\{([^{}]+)\},\s*([^{}]+)\},', line)
        assert match is not None, 'Every selection exit vector is a complete literal tuple'
        pieces = [[value.strip() for value in group.split(',')] for group in match.groups()]
        assert [len(values) for values in pieces] == [9, 15, 2]
        assert all(re.fullmatch(r'-?(?:0x[0-9a-f]{8}|[0-9]+)U?', value)
                   for group in pieces for value in group)
        rows.append(tuple(int(value.rstrip('U'), 0) for group in pieces for value in group))
    return rows


def _section(path, title):
    text = (repo.ROOT / path).read_text()
    assert text.count('## '+title+'\n') == 1
    return ' '.join(text.split('## '+title+'\n', 1)[1].split('\n## ', 1)[0].split())


def _published(section, value, noun):
    labels = {'instructions': r'instructions?', 'bytes': r'bytes?',
              'cases': r'(?:cases?|times)'}
    pattern = (r'\b([0-9][0-9,]*)\s*(?:-\s*)?'
               r'(?:(?:stock|bound|literal|executed|registered)\s+)?'+labels[noun]+r'\b')
    found = []
    for match in re.finditer(pattern, section, re.I):
        if noun == 'bytes' and re.match(
                r'(?:(?:observed|stack|local|saved)\s+)*(?:frame|pool|calibration|RAM|output)\b',
                section[match.end():].lstrip(), re.I):
            continue
        found.append(int(match[1].replace(',', '')))
    assert found and set(found) == {value}, f'Only {value} {noun} belongs to this contract'


def _published_scopes(section, header, harness, require_data=False):
    entries = Counter(row[7] for row in _rows(header))
    for standalone, qualifiers in ((0, r'(?:explicit\s+)?post-lookup'),
                                   (1, r'standalone(?:\s+alternative)?')):
        counts = [int(number.replace(',', '')) for number in re.findall(
            r'\b([0-9][0-9,]*)\s+'+qualifiers+r'\s+entr(?:y|ies)\b', section, re.I)]
        assert counts and set(counts) == {entries[standalone]}
    [(frame, frame_after)] = re.findall(
        r'\buint8_t\s+frame_before\[([0-9]+)\],\s*frame_after\[([0-9]+)\];', harness)
    assert frame == frame_after
    frames = [int(number) for number in re.findall(
        r'\b([0-9]+)\s*(?:-\s*)?byte\s+(?:(?:observed|stack|local)\s+)?frame\b', section, re.I)]
    assert frames and set(frames) == {int(frame)}
    [calibration] = re.findall(
        r'\bstatic\s+uint8_t\s+ram_before\[65536\],\s*calibration_before\[([0-9]+)\];', harness)
    assert int(calibration) == sum(size for _, size in _region().pools)
    data = [int(number) for number in re.findall(
        r'\b(?:all\s+)?([0-9]+)\s+(?:bound\s+)?(?:anchor/pool/calibration|data|pool/calibration)\s+bytes\b',
        section, re.I)]
    if data or require_data:
        assert data and set(data) == {int(calibration)}


@pytest.mark.parametrize('noun,value,extra', (
    ('instructions', 70, '71 instructions'), ('instructions', 70, '71-instruction fixture'),
    ('bytes', 208, '209 bound bytes'), ('bytes', 208, '209-byte envelope'),
    ('cases', 11615, '11616 literal cases'), ('cases', 11615, '11616-case matrix'),
    ('cases', 11615, '11616 times'),
))
def test_state_selection_conflicting_publication_counts_are_refused(noun, value, extra):
    section = f'{value} {noun}.'
    _published(section, value, noun)
    with pytest.raises(AssertionError):
        _published(section+' '+extra, value, noun)


@pytest.mark.parametrize('change', (
    {'key': 'other-region'}, {'rom': 'JK00D'}, {'cases': 11616}, {'boundary': False},
    {'return_address_offset': 4}, {'return_register': 6}, {'base_load': 0x495da},
    {'bits': (('MASK', 'masked-inchworm/ram', 'bit7'),)},
    {'constants': (('POST_LOOKUP_ENTRY', 0x49614), ('ALTERNATIVE_ENTRY', 0x499b8), ('EXTRA', 0))},
    {'symbols': tuple((name, item[0]) for name, item in reversed(tuple(OWNER_DEFINES.items())))},
    {'symbols': (*tuple((name, item[0]) for name, item in OWNER_DEFINES.items()),
                 ('SOURCE_STATE', 'thick-dalmatian/ram'))},
))
def test_state_selection_registered_metadata_mutations_are_refused(change):
    region = _region()
    _check_region(region)
    with pytest.raises(AssertionError):
        _check_region(replace(region, **change))


@pytest.mark.parametrize('extra', (
    '65-byte frame', 'all 69 anchor/pool/calibration bytes', '69 bound data bytes',
    '7672 post-lookup entries', '3945 standalone alternative entries',
))
def test_state_selection_conflicting_scoped_publications_are_refused(extra):
    directory = repo.ROOT / 'tools/sh-elf-run'
    header, harness = ((directory / name).read_text() for name in (HEADER, HARNESS))
    section = _section(SPEC, 'Bounded knock state selection')
    _published_scopes(section, header, harness, require_data=True)
    with pytest.raises(AssertionError):
        _published_scopes(section+' '+extra, header, harness, require_data=True)


def test_state_selection_typed_links_match_exact_reviewed_notes_and_claim_levels():
    model = compile.cached(repo.ROOT)
    owners = {key: model.meaning_of(SymbolKey('7mfk', key.split('/')[1], address))
              for key, address in OWNER_DEFINES.values()}
    assert len(LINK_CONTRACTS) == 17
    for contract in LINK_CONTRACTS:
        owner, kind, target, slot, _ = contract
        _check_link_contract(_link(owners[owner], kind, target, slot), contract)
    _notes()


@pytest.mark.parametrize('contract', LINK_CONTRACTS)
@pytest.mark.parametrize('mutation', ('extra_via', 'changed_note', 'missing_relies',
                                     'weakened_relies', 'missing_supports', 'weakened_supports'))
def test_state_selection_link_route_note_and_claim_mutations_are_refused(contract, mutation):
    link = _synthetic_link(contract)
    _check_link_contract(link, contract)
    if mutation == 'extra_via':
        link.props['via'].append(SymbolKey('7mfk', 'fn', 0x49544))
    elif mutation == 'changed_note':
        link.props['note'] += ' The inverse predicate also applies.'
    else:
        field = mutation.split('_', 1)[1]
        if mutation.startswith('missing_'):
            del link.props[field]
        else:
            link.props[field] = 'address'
    with pytest.raises((AssertionError, KeyError)):
        _check_link_contract(link, contract)


@pytest.mark.parametrize('index,note', (
    (4, 'Normal entry 00049614 selects direct arithmetic when bit7 is set and ffff2467.bit6 is clear.'),
    (5, 'With ffff2469.bit7 clear, a clear bit6 selects direct arithmetic and a set bit6 selects 000499b8.'),
    (8, 'Standalone 000499b8 reads bit7/bit6 and x operands before selecting its alternative formula.'),
    (9, 'The state selection and timing conversion envelopes execute jointly and prove signed monotonicity across wrap.'),
))
def test_state_selection_inverse_bit_and_broadened_execution_claims_are_refused(index, note):
    contract = LINK_CONTRACTS[index]
    link = _synthetic_link(contract)
    link.props['note'] = note
    with pytest.raises(AssertionError):
        _check_link_contract(link, contract)


@pytest.mark.parametrize('index', (9, 11, 13, 14))
@pytest.mark.parametrize('field', ('reverse_relies', 'reverse_supports'))
@pytest.mark.parametrize('mutation', ('missing', 'weakened'))
def test_state_selection_held_reverse_claim_mutations_are_refused(index, field, mutation):
    contract = LINK_CONTRACTS[index]
    link = _synthetic_link(contract)
    if mutation == 'missing':
        del link.props[field]
    else:
        link.props[field] = 'address'
    with pytest.raises((AssertionError, KeyError)):
        _check_link_contract(link, contract)


@pytest.mark.parametrize('index', (11, 13, 14))
def test_state_selection_held_indexed_role_removal_is_refused(index):
    contract = LINK_CONTRACTS[index]
    link = _synthetic_link(contract)
    link.roles.clear()
    with pytest.raises(AssertionError):
        _check_link_contract(link, contract)


@pytest.mark.parametrize('missing', (
    {'kind': 'test', 'path': 'tools/kb/tests/test_knock_timing_byte_chain.py',
     'key': 'test_knock_timing_byte_chain_owner_contract'},
    {'kind': 'test', 'path': 'tools/kb/tests/test_knock_timing_byte_chain.py',
     'key': 'test_knock_timing_byte_registered_stock_contract'},
    {'kind': 'spec', 'path': SPEC, 'key': 'Bounded timing-byte conversion'},
))
def test_state_selection_word_projection_requires_separate_conversion_proof(missing):
    contract = LINK_CONTRACTS[9]
    link = _synthetic_link(contract)
    link.evidence.remove(missing)
    with pytest.raises(AssertionError):
        _check_link_contract(link, contract)


@pytest.mark.parametrize('index', range(3))
def test_state_selection_chain_source_changes_are_refused(index):
    steps = [dict(source_step) for source_step in
             compile.cached(repo.ROOT).entities[('chain', 'knock_retard')].steps[10:13]]
    _check_steps(steps)
    steps[index]['from'] = SymbolKey('7mfk', 'ram', 0xffff1258)
    with pytest.raises(AssertionError):
        _check_steps(steps)


@pytest.mark.parametrize('change', (
    {'key': 'other-conversion'}, {'rom': 'JK00D'}, {'source': 'other.s'}, {'harness': 'other.c'},
    {'start': 0x496ce}, {'end': 0x496d8}, {'callees': ()}, {'pools': CONVERSION_POOLS[:-1]},
    {'ram_literals': ()}, {'cases': 65651}, {'boundary': False}, {'return_address_offset': 4},
    {'return_register': 6}, {'base_load': 0x495da},
    {'symbols': (('WORD_STATE', 'steady-lionfish/ram'), ('BYTE_STATE', 'knock_timing_state/ram'))},
    {'symbols': (('BYTE_STATE', 'steady-lionfish/ram'), ('WORD_STATE', 'knock_timing_state/ram'))},
    {'symbols': (('WORD_STATE', 'knock_timing_state/ram'), ('BYTE_STATE', 'steady-lionfish/ram'),
                 ('WORD_STATE', 'knock_timing_state/ram'))},
    {'constants': (('CONVERSION_ENTRY', 0x4964c),)},
    {'constants': (('CONVERSION_ENTRY', 0x4964a), ('EXTRA', 0))},
    {'bits': (('EXTRA', 'knock_timing_state/ram', 'bit15'),)},
))
def test_state_selection_separate_conversion_metadata_mutations_are_refused(change):
    region = _conversion_region()
    _check_conversion_region(region)
    with pytest.raises(AssertionError):
        _check_conversion_region(replace(region, **change))


@pytest.mark.parametrize('address', [address for start, end, _ in CONVERSION_SPANS
                                   for address in range(start, end)])
def test_state_selection_separate_conversion_byte_mutations_are_refused(address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address] ^= 1
    with pytest.raises(AssertionError):
        _check_conversion_stock(data)


def test_state_selection_separate_conversion_exact_binding():
    _check_conversion_binding(_verifier(), _conversion_region(), derive.image_bytes(repo.layout('7mfk')))


def verify_state_selection_stock(data):
    for start, end, digest in SPANS:
        assert hashlib.sha256(data[start:end]).hexdigest() == digest, f'{start:08x}'
    word = lambda address, size=2: int.from_bytes(data[address:address+size], 'big')
    assert word(0x9078) == 1280
    assert [word(a) for a in (0x49614, 0x49618, 0x4961a, 0x4961e, 0x49628)] == [
        0xc97f, 0xe010, 0x0f64, 0xc880, 0xc840]
    assert [word(a) for a in (0x49634, 0x4963e, 0x49642, 0x49646, 0x49648)] == [
        0x620c, 0x666c, 0x3568, 0x4518, 0x325c]
    assert word(0x496b4, 4) == 0x9a1a and word(0x496c4, 4) == 0x9b1a
    assert word(0x496c0, 4) == 0x26230
    assert word(0x495fa) == word(0x49610) == 0x4d0b
    assert word(0x495fc) == 0x66e3 and word(0x49612) == 0x672d
    assert sh2.decode(word(0x499bc), 0x499bc).access == sh2.Access(10, 12, 2, 'load')
    assert sh2.decode(word(0x499dc), 0x499dc).access == sh2.Access(9, 0, 1, 'load', True)
    assert word(0x496ac, 4) == word(0x49b38, 4) == 0xffff22f8
    assert word(0x49b38, 4)+0x12 == OWNER_DEFINES['NEGATIVE_BOUND'][1]
    for address, pool in ((0x495da, 0x496ac), (0x499ae, 0x49b38)):
        decoded = sh2.decode(word(address), address)
        assert decoded.dest == 9 and decoded.value == ('pool', pool, 4)
    assert [word(a) for a in (0x499ce, 0x499e0, 0x499e2, 0x499e4, 0x499e8, 0x499f0)] == [
        0x666d, 0x4518, 0x666c, 0x0567, 0x3723, 0x4615]
    stores = []
    for start, end in CODE_SPANS:
        for address in range(start, end, 2):
            insn = sh2.decode(word(address), address)
            assert insn.flow != 'call'
            assert insn.dest != 15
            if insn.access is not None and insn.access.mode == 'store':
                stores.append((address, insn.access))
    assert stores == [(0x4961a, sh2.Access(15, 0, 1, 'store', True))]


def test_knock_state_selection_exact_stock_post_lookup_and_widened_boundary():
    verify_state_selection_stock(derive.image_bytes(repo.layout('7mfk')))
    assert sum((end-start)//2 for start, end in CODE_SPANS) == 70
    assert sum(end-start for start, end, _ in SPANS) == 208


@pytest.mark.parametrize('address', [a for start, end, _ in SPANS for a in range(start, end)])
def test_knock_state_selection_static_corruption_is_rejected(address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address] ^= 1
    with pytest.raises(AssertionError):
        verify_state_selection_stock(data)


def test_knock_state_selection_chain_owner_contract():
    model = compile.cached(repo.ROOT)
    chain = model.entities[('chain', 'knock_retard')]
    assert len(chain.steps) == 16
    _notes()
    assert [step['effect'] for step in chain.steps[10:13]] == ['adds', 'looks-up', 'looks-up']
    assert all(step['to'] == SymbolKey('7mfk', 'ram', 0xffff121a)
               and step['via'] == [FUNCTION] for step in chain.steps[10:13])
    owners = {name: model.meaning_of(SymbolKey('7mfk', 'tbl' if name == 'SLEW_STEP' else 'ram', at))
              for name, (_, at) in OWNER_DEFINES.items()}
    for name, (key, _) in OWNER_DEFINES.items():
        assert owners[name].key == key
    for name in ('NEGATIVE_BOUND', 'GATE69', 'GATE67'):
        symbol = owners[name].symbols['7mfk']
        assert (symbol.value('width'), symbol.value('signed'), symbol.value('level')) == (8, False, 'code')
    slew = owners['SLEW_STEP'].symbols['7mfk']
    assert (slew.value('storage'), slew.value('rows'), slew.value('cols'), slew.value('level')) == (
        'uint16', 1, 1, 'code')
    assert slew.value('block') == 'ignition_timing/block'
    assert '1280' not in owners['SLEW_STEP'].props['summary']
    state = owners['WORD_OUTPUT']
    for source in ('SOURCE_STATE', 'TARGET_STATE', 'NEGATIVE_BOUND', 'SLEW_STEP'):
        _proof(_link(state, 'input', owners[source].key))
    for source, bit in (('GATE69', 'bit7'), ('GATE67', 'bit6')):
        _proof(_link(state, 'selector', owners[source].key, bit))
    for table in ('high_octane_timing_state/tbl', 'high_detonation_timing_state/tbl'):
        context = _link(state, 'lookup', table)
        _proof(context)
        for phrase in ('post-lookup', '00049614', 'static', 'not executed', 'x', 'y'):
            assert phrase in context.props['note'].lower()
    invocation = _link(state, 'selector', BUILDER)
    _proof(invocation)
    for phrase in ('00049614', '000499b8', '0..127', 'incoming r0', 'not read'):
        assert phrase in invocation.props['note'].lower()
    writer = _link(state, 'writer', BUILDER)
    _proof(writer)
    for phrase in ('widened', '0004964a', 'separate', 'uint16', 'not joint', '00049656'):
        assert phrase in writer.props['note'].lower()
    assert ('tools/kb/tests/test_knock_timing_byte_chain.py',
            'test_knock_timing_byte_registered_stock_contract') in {
        (item.get('path'), item.get('key')) for item in writer.evidence if item['kind'] == 'test'}
    for name, registry, order, target, end in (
        ('knock_timing_state', 'vars', 584, BUILDER, 'owner'),
        ('knock_function', 'funcs', 142, 'knock_timing_state/ram', 'to'),
    ):
        [markers] = [markers for kind, owner_name, markers, _ in model.stash['ledger_rows']
                     if owner_name == name and kind == ('ram' if end == 'owner' else 'fn')]
        [marker] = [item for item in markers if item['registry'] == registry and item['order'] == order]
        assert dict(role='writes', to=target, type='writer', end=end,
                    relies='structure', supports='identity') in marker['dependency']
    for source in ('SOURCE_STATE', 'TARGET_STATE', 'NEGATIVE_BOUND', 'GATE69', 'GATE67', 'SLEW_STEP'):
        _proof(_link(owners[source], 'reader', BUILDER))
    base = _link(owners['NEGATIVE_BOUND'], 'base', 'hungry-sidewinder/ram')
    _proof(base)
    assert base.offset == 0x12
    for phrase in ('000499dc', '000495da/000496ac', '000499ae/00049b38',
                   'not executed', 'not numeric input', 'array extent'):
        assert phrase in base.props['note'].lower()


def _check_literal_arithmetic(header, note, direct_note):
    rows = _rows(header)
    [total] = re.findall(r'^#define KNOCK_STATE_SELECTION_CASE_COUNT ([0-9]+)U$', header, re.M)
    assert len(rows) == int(total) == 11615
    assert Counter(row[7] for row in rows) == {0: 7671, 1: 3944}
    assert {row[3] for row in rows} == set(range(128))
    assert all({row[index] for row in rows} == set(range(256)) for index in (4, 5, 6))
    assert {row[0] for row in rows if row[0] <= 255} == set(range(256))
    assert sum(row[0] > 255 and not row[7] for row in rows) == 120
    signed16 = lambda value: int.from_bytes((value&65535).to_bytes(2, 'big'), 'big', signed=True)
    expressions = [builtins.compile(value, '<bounded state-selection arithmetic>', 'exec')
                   for value in (note, direct_note, ALT_FORMULA)]
    counts = Counter()
    differences = set()
    for raw, s, v, first, n, gate69, gate67, standalone, stored, *exit_values in rows:
        regs, macl, t = exit_values[:15], exit_values[15], exit_values[16]
        assert all(0 <= reg <= 0xffffffff for reg in regs) and t in (0, 1)
        direct = not standalone and not(gate69&128) and bool(gate67&64)
        counts['direct' if direct else 'alternative'] += 1
        values = dict(ffff2469=gate69, ffff2467=gate67, ffff1258=s&65535,
                      ffff1380=v&65535, ffff230a=n, x=(first, raw),
                      ROM16={0x9078: 1280}, min=min, max=max,
                      int16=signed16, uint8=lambda value: value&255,
                      uint16=lambda value: value&65535, uint32=lambda value: value&0xffffffff)
        exec(expressions[2 if standalone else 0], {'__builtins__': {}}, values)
        r = values['R']
        assert regs[2] == r&0xffffffff and values['to'] == r&65535
        if direct:
            exec(expressions[1], {'__builtins__': {}}, values)
            assert values['R'] == r and values['to'] == r&65535
            assert macl == 0x2468ace0 and t == 0
            differences.add(first-(raw&127))
            counts['below16'] += r < -32768
            counts['above16'] += r > 32767
        else:
            y = min(s+1280, max(s-1280, v))
            u = max(y, -256*n)
            assert r == min(u, 0) and macl == (-256*n)&0xffffffff
            assert t == int(u > 0)
            counts['forcing'] += y < -256*n
            counts['equality'] += y == -256*n
            if n >= 128:
                assert y >= -256*n
            if n == 128:
                counts['n128equal'] += y == -256*n
        if not standalone:
            assert stored == raw&127
    assert counts['direct'] == 7361 and counts['alternative'] == 4254
    assert counts['below16'] == 1057 and counts['above16'] == 1192
    assert differences == set(range(-127, 128))
    assert counts['forcing'] == 968 and counts['equality'] == 146 and counts['n128equal'] == 8


def test_knock_state_selection_arithmetic_matches_entries_and_widened_wrap_literals():
    header = (repo.ROOT / 'tools/sh-elf-run' / HEADER).read_text()
    notes = _notes()
    _check_literal_arithmetic(header, notes[0], notes[1])


def test_knock_state_selection_registered_stock_contract():
    module, region = _verifier(), _region()
    _check_region(region)
    data = derive.image_bytes(repo.layout('7mfk'))
    verify_state_selection_stock(data)
    assert region.rom == 'JK08A' and (region.source, region.harness) == (SOURCE, HARNESS)
    assert region.code_spans == CODE_SPANS and region.pools == POOLS
    assert region.ram_literals == RAM_LITERALS and region.boundary
    assert dict(region.constants) == {'POST_LOOKUP_ENTRY': 0x49614, 'ALTERNATIVE_ENTRY': 0x499b8}
    assert dict(region.symbols) == {name: item[0] for name, item in OWNER_DEFINES.items()}
    defines = module.harness_defines(region, data)
    assert {name: defines[name] for name in OWNER_DEFINES} == {name: item[1] for name, item in OWNER_DEFINES.items()}
    fixture = module.build_fixture(region, data)
    for start, end in CODE_SPANS:
        assert fixture[start:end] == data[start:end]
    assert fixture[0x4964a:0x4964e] == bytes.fromhex('000b0009')
    for start, size in POOLS:
        expected = data[start:start+size]
        if start in RAM_LITERALS:
            expected = module.base_verifier.alias_high_ram(int.from_bytes(expected, 'big')).to_bytes(4, 'big')
        assert fixture[start:start+size] == expected
    _check_conversion_binding(module, _conversion_region(), data)
    instructions = sum((end-start)//2 for start, end in region.code_spans)
    bound = sum(end-start for start, end, _ in SPANS)
    directory = repo.ROOT / 'tools/sh-elf-run'
    header, harness = ((directory / name).read_text() for name in (HEADER, HARNESS))
    assert len(_rows(header)) == region.cases
    assert (instructions, bound, region.cases) == (70, 208, 11615)
    assert not any(re.search(r'^#define\s+'+name+r'\b', harness, re.M) for name in OWNER_DEFINES)
    assert 'ARRAY_SIZE(selection_cases)' in harness and harness.count('++completed;') == 1
    assert 'completed != KNOCK_STATE_SELECTION_CASE_COUNT' in harness
    assert 'VQ_SH_ELF_STOCK_CODE status=PASS region=%s cases=%lu\\n' in harness
    for phrase in ('test->expected[i]', 'test->expected_t', 'test->expected_macl',
                   'i<15U', 'i<65536U', 'calibration_before[68]', 'frame_before[64]',
                   'first low7 input preservation', 'natural second low7 byte store',
                   'stock SP preservation', 'driver PR preservation', 'C caller ABI restoration',
                   '(test->alternative_entry || i != 48U)', '!preserve_inputs(scope,index)'):
        assert phrase in harness
    for path, title in ((SPEC, 'Bounded knock state selection'),
                        ('tools/sh-elf-run/README.md', 'Knock timing-state selection')):
        section = _section(path, title)
        _published(section, instructions, 'instructions')
        _published(section, bound, 'bytes')
        _published(section, region.cases, 'cases')
        _published_scopes(section, header, harness, require_data=path == SPEC)
        lower = section.lower()
        for phrase in ('post-lookup', 'standalone', 'widened', 'wrap', 'separate',
                       'not executed', 'natural pr', 'hardware', 'monotonic'):
            assert phrase in lower
