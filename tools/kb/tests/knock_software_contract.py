"""Bind bounded software-knock owners and execution artifacts to tracked inputs."""
import ast
import builtins
from dataclasses import asdict
from functools import cache
import hashlib,json,re
from pathlib import Path
from kb import compile,repo
from tools.kb.tests import test_injection_start_delay_chain as publication
TOOL_DIR=repo.ROOT/'tools/sh-elf-run'
SPEC='defs/JK08A.knock-detection.md'
@cache
def contracts():
    value=json.loads((TOOL_DIR/'knock-software-contracts.json').read_text())
    assert value['hardware_ready'] is False
    assert set(value['regions'])=={'metric','normalization'}
    assert len(value['new_owners'])==15
    assert value['owner_contracts'] and value['required_owners']
    return value
def owner_contract(packet,model=None):
    model=compile.cached(repo.ROOT) if model is None else model
    wanted=contracts()['required_owners'][packet];assert wanted
    for ref in wanted:
        expected=contracts()['owner_contracts'][ref]
        owner=publication.required_owner(model,ref,int(expected['address'],16))
        symbol=owner.symbols['7mfk']
        publication.required_properties(model,owner.props,expected['props'])
        publication.required_properties(model,symbol.props,expected['symbol_props'])
        assert symbol.value('level')==expected['level']
        publication.required_evidence(model,symbol.evidence,expected['evidence'])
        for wanted_link in expected['links']:
            matches=[link for link in owner.links if
                (link.type,link.to.key,link.slot,link.offset)==
                (wanted_link['type'],wanted_link['to'],wanted_link['slot'],wanted_link['offset'])]
            assert len(matches)==1
            [link]=matches
            assert link.stated>=set(wanted_link['layouts']) and link.roles>=set(wanted_link['roles'])
            publication.required_properties(model,link.props,wanted_link['props'])
            publication.required_evidence(model,link.evidence,wanted_link['evidence'])
    if packet=='metric':
        chain=model.entities[('chain','knock_retard')];assert len(chain.steps)==16
        for index,expected in contracts()['steps'].items():
            observed=publication.normalized(model,chain.steps[int(index)-1])
            assert observed==expected
        assert contracts()['steps']['1']['from']=='knock_reference_samples/ram'
    bindings={'normal_note':'knock_normalized_cache/ram',
        'subtraction_note':'knock_metric_differences/ram','sum_note':'knock_selected_difference_sum/fn',
        'scale_note':'knock_metric_scaler/fn','composite_note':'knock_metric_base/ram'}
    def strings(value):
        if isinstance(value,str):yield value
        elif isinstance(value,dict):
            for item in value.values():yield from strings(item)
        elif isinstance(value,list):
            for item in value:yield from strings(item)
    for key,ref in bindings.items():
        [owner]=[item for item in model.meanings if item.key==ref]
        notes=list(strings(owner.props))+[note for link in owner.links for note in strings(link.props)]
        assert any(contracts()['formulas'][key] in note for note in notes),(key,ref)
def region(packet,module=None):
    module=publication.stock_module() if module is None else module
    expected=contracts()['regions'][packet]
    selected=[row for row in module.REGIONS if row.key==expected['key']]
    assert len(selected)==1
    [row]=selected;assert json.loads(json.dumps(asdict(row)))==expected
    assert module.REGION_OBSERVERS[row.key]==contracts()['observers'][packet]
    return row,module
def stock_bytes(packet,image):
    for at,raw in contracts()['slices'][packet]:
        data=bytes.fromhex(raw)
        assert image[at:at+len(data)]==data,f'{at:08x}'
def registered_stock_contract(packet,image):
    row,module=region(packet);stock_bytes(packet,image)
    for name,digest in contracts()['sources_sha256'][packet].items():
        assert hashlib.sha256((TOOL_DIR/name).read_bytes()).hexdigest()==digest,name
    assert hashlib.sha256(module.build_fixture(row,image)).hexdigest()==contracts()['fixtures'][packet]
    assert (row.return_address_offset,row.return_register,len(row.ram_literals))==(24,1,11)
    assert row.boundary and not row.ram_word_literals and not row.register_word_literals
    expected=contracts()['counts'][packet]
    assert sum((end-start)//2 for start,end in row.code_spans)==expected['instructions']
    assert sum(end-start for start,end in row.code_spans)+sum(size for _,size in row.pools)==expected['bound_bytes']
    assert len(literals(packet))==row.cases==expected['cases']
@cache
def literals(packet):
    path=TOOL_DIR/contracts()['headers'][packet]
    text=path.read_text();[body]=re.findall(packet+r'_cases\[\] = \{(.*?)\n\};',text,re.S)
    result=[]
    for line in body.splitlines():
        if line.strip():
            assert re.fullmatch(r'[\s{},0-9a-fxU]+',line)
            line=re.sub(r'(?<=[0-9a-f])U\b','',line.strip().rstrip(','))
            result.append(ast.literal_eval(line.replace('{','[').replace('}',']')))
    assert result
    return result
def publication_contract(packet):
    expected=contracts()['counts'][packet]
    row,_=region(packet)
    for path in (SPEC,'tools/sh-elf-run/README.md'):
        section=(repo.ROOT/path).read_text().split('## '+contracts()['sections'][packet],1)[1].split('\n## ',1)[0]
        published=re.findall(r'One mandatory Region binds (\d+) instructions, (\d+) bound bytes and (\d+) literal\s+cases',section)
        assert len(published)==1
        assert tuple(map(int,published[0]))==(expected['instructions'],expected['bound_bytes'],row.cases)
        for key in ('post-acquisition','physical units','cadence','Hardware readiness is NO'):
            assert key.lower() in section.lower()
        assert 'ADC/DMAC' in section
        if packet=='metric':
            facts=metric_literal_contract()
            scope=facts['scopes']
            assert f"{scope[0]} composite, {scope[1]} direct selection and {scope[2]}" in section
            assert f"{facts['stock_composite']} retain the six stock" in section
        else:
            facts=normalization_literal_contract();counts=facts['counts']
            assert f"{counts['primary']} primary and {counts['alternate']} alternate" in section
            assert f"{counts['zero_block']} zero-block, {counts['ordinary']} ordinary and {counts['weighted']} weighted" in section
            assert f"{facts['stock']} stock software" in section
def all_bound_mutations_fail(packet,image):
    for at,raw in contracts()['slices'][packet]:
        for offset in range(len(bytes.fromhex(raw))):
            changed=bytearray(image);changed[at+offset]^=1
            try:stock_bytes(packet,changed)
            except AssertionError:pass
            else:raise AssertionError(f'{packet} accepts changed byte {at+offset:08x}')
from collections import Counter
from fractions import Fraction
from math import floor
from kb.arithmetic import Grammar

def metric_literal_contract(rows=None):
    rows=literals('metric') if rows is None else rows
    assert len(rows)==9404
    MASK=0xffffffff
    signed = lambda value: value - (1 << 32) if value & (1 << 31) else value
    alias = lambda address: 0x01000000 + (address & 0xffff)
    scope_count = Counter()
    flags = Counter()
    factory = 0
    raw_gains = Counter()
    gain_scopes = set()
    saturation_neighbors = set()
    masks = set()
    counts = set()
    for row in rows:
        scope, channel, selector, mask, count, gain, sample, reference, difference, ordered, total, metric, biased, registers, t = row
        assert scope in (0, 1, 2) and channel in range(1, 7)
        assert selector in (0x82, 0x8a) and mask in range(256) and count in range(9)
        assert all(value in range(256) for value in gain)
        assert all(value in range(65536) for value in sample + reference)
        scope_count[scope] += 1
        flags[(scope, t)] += 1
        raw_gain = gain[0] * gain[1] * gain[2] >> 7
        clamped_gain = min(raw_gain, 65535)
        raw_gains[raw_gain] += 1
        gain_scopes.add((raw_gain, scope))
        differences = [signed(value) for value in difference]
        if scope == 0:
            assert differences == [a-b for a, b in zip(sample, reference)]
            if selector == 0x82 and mask == 0 and count == 3 and gain == [128, 128, 128]:
                factory += 1
        if scope != 2:
            assert all(-65535 <= value <= 65535 for value in differences)
            ranked = sorted([value if not mask & (1 << i) else -(1 << 31)
                             for i, value in enumerate(differences)], reverse=True)
            assert [signed(value) for value in ordered] == ranked
            selected_total = sum(value for value in ranked[:count] if value != -(1 << 31))
            assert total == selected_total & MASK
            masks.add(mask)
            counts.add(count)
        else:
            selected_total = signed(total)
        quotient = abs(selected_total) * clamped_gain >> 14
        limited = min(quotient, 0x7fffffff) if selected_total >= 0 else -min(quotient, 0x80000000)
        assert metric == limited & MASK
        assert biased == (limited + 0x80000000) & MASK
        expected_t = int(not selector & 8) if scope == 1 else int(scope == 2 and selected_total >= 0 and quotient >= 0x80000000)
        assert t == expected_t
        expected = [(0x28765430 + i * 0x01030507) & MASK for i in range(15)]
        expected[7] = (0x4a2b6, 0x49d88, 0x49e96)[scope]
        expected[0] = 4 * channel
        if scope == 1:
            expected[1] = 0x221e6
            expected[2] = alias(0xffff2274)-4 if selector & 8 else (ordered[count-1] if count else 0x8870)
            expected[4] = total
            expected[5] = channel if selector & 8 else count
            expected[6] = 0x8b3d if selector & 8 else alias(0xffff2274)-4
            expected[7] = count
        else:
            expected[1] = 0 if scope == 0 else 4 * channel
            expected[2] = alias(0xffff21d8)-4
            expected[4] = expected[6] = alias(0xffff21f8)-4
            expected[5] = biased
            expected[7] = abs(selected_total)
            if scope == 0:
                expected[11] = 8 if selector & 8 else 0
                expected[14] = alias(0xffff2158)+32
                if selector & 8:
                    expected[3] = alias(0xffff1ff4)
        assert registers == expected
        if scope == 2 and raw_gain in (65534, 65535, 65536):
            threshold = ((1 << 31) * 16384 + clamped_gain - 1) // clamped_gain
            distance = abs(selected_total) - threshold
            if distance in (-1, 0, 1):
                saturation_neighbors.add((raw_gain, selected_total < 0, distance, selector))
    
    assert scope_count == {0: 6488, 1: 972, 2: 1944}
    assert factory == 386 and masks == set(range(256)) and counts == set(range(9))
    assert {(gain, scope) for gain in (65534, 65535, 65536) for scope in (0, 2)} <= gain_scopes
    assert saturation_neighbors == {(gain, negative, distance, selector)
        for gain in (65534, 65535, 65536) for negative in (False, True)
        for distance in (-1, 0, 1) for selector in (0x82, 0x8a)}
    return {'scopes':dict(scope_count),'stock_composite':factory,'saturation_neighbors':len(saturation_neighbors)}

def normalization_literal_contract(rows=None):
    rows=literals('normalization') if rows is None else rows
    assert len(rows)==6563
    MASK=0xffffffff
    alias=lambda address:0x01000000+(address&0xffff)
    incoming=[(0x28765430+i*0x01030507)&MASK for i in range(15)]
    counts = Counter()
    coverage = {'selector': set(), 'blocks': set(), 'flag': set(), 'other': set(),
                'channel': set(), 'entry_t': set(), 'last_long': set(), 'quotient': set()}
    stock = 0
    word_wrap_neighbors = set()
    for row in rows:
        mode, channel, selector, blocks, flag, other, entry_t, multiplier, bins, outputs, quotients, registers, macl, saved_r3, controlled_sr, has_long = row
        assert mode == bool(selector & 8)
        assert channel in range(1, 7) and entry_t in (0, 1)
        assert all(value in range(256) for value in (selector, blocks, flag, other))
        assert multiplier in range(65536) and all(value in range(65536) for value in bins)
        for key, value in (('selector', selector), ('blocks', blocks), ('flag', flag),
                           ('other', other), ('channel', channel), ('entry_t', entry_t)):
            coverage[key].add(value)
        q = [value * multiplier // (32 * blocks) for value in bins] if blocks else [0] * 8
        assert quotients == q
        result = ([min(value * 8, 65535) for value in q] if flag else
                  [value % 65536 for value in q]) if blocks else [65535] * 8
        assert outputs == result
        assert max(q) <= 134213632 and max(q) * 8 <= 1073709056
        expected = incoming.copy()
        expected[1] = 0  # External fragment continuation; C replaces it with its address.
        expected[5] = incoming[5] if mode else channel
        expected[11] = 8 if mode else 0
        if not blocks:
            expected[0] = expected[14] = 2
            expected[2] = MASK
            expected[3] = alias(0xffff1ff4) if mode else incoming[3]
            expected[5] = alias(0xffff20d2) + 16 * channel
            expected[6] = alias(0xffff20d2)
            expected[7] = expected[9] = 0
            expected_macl = 0x2468ace0
            expected_sr = 1
        else:
            expected[0] = 16 * channel + 14
            expected[2] = result[-1] if flag else 16
            expected[3] = alias(0xffff1ff4) if mode else alias(0xffff11d4)
            expected[6] = channel if mode and flag else 0x21ce0
            expected[7] = alias(0xffff20c2)
            expected[8] = 65535 if flag else alias(0xffff1ff4)
            expected[9] = 32 * blocks
            expected[10] = multiplier if flag else channel if mode else other - (256 if other & 128 else 0)
            expected[12] = alias(0xffff20d2) if flag else multiplier
            expected[13] = 0 if flag else alias(0xffff20d2)
            expected[14] = 16
            expected_macl = bins[-1] * multiplier
            # DIV0U clears M; the final ROTCL inserts !Q as quotient bit zero.
            expected_sr = 1 | ((1 - (q[-1] & 1)) << 8)
            coverage['quotient'].update(q)
            if len(set(q)) == 1 and q[0] in (65535, 65536, 65537):
                word_wrap_neighbors.add((q[0], mode, bool(flag)))
        assert registers == [value & MASK for value in expected]
        assert macl == expected_macl and controlled_sr == expected_sr
        long_calls = [index for index, value in enumerate(q) if blocks and value >= 256]
        assert has_long == bool(long_calls)
        if not long_calls:
            expected_saved = 0
        else:
            last = long_calls[-1]
            coverage['last_long'].add(last)
            if mode:
                expected_saved = alias(0xffff1ff4)
            elif last:
                expected_saved = alias(0xffff11d4)
            elif flag:
                expected_saved = alias(0xffff1ff4)
            else:
                expected_saved = incoming[3]
        assert saved_r3 == expected_saved
        counts['alternate' if mode else 'primary'] += 1
        counts['zero_block' if not blocks else 'weighted' if flag else 'ordinary'] += 1
        counts[f'full_sr_controlled_{controlled_sr:03x}'] += 1
        counts['has_long' if long_calls else 'no_long'] += 1
        stock += selector == 0x82 and blocks <= 8 and multiplier <= 256 and flag <= 1
    
    for key in ('selector', 'blocks', 'flag', 'other'):
        assert coverage[key] == set(range(256)), key
    assert coverage['channel'] == set(range(1, 7))
    assert coverage['entry_t'] == {0, 1} and coverage['last_long'] == set(range(8))
    assert {255, 256, 257, 8191, 8192, 8193, 65535, 65536, 65537} <= coverage['quotient']
    assert word_wrap_neighbors == {(q, mode, flag) for q in (65535, 65536, 65537)
                                  for mode in (False, True) for flag in (False, True)}
    assert (counts['primary'], counts['alternate'], counts['zero_block'], counts['ordinary'], counts['weighted'], stock) == (3281, 3282, 522, 2512, 3529, 1325)
    return {'counts':dict(counts),'stock':stock,'output_words':16*len(rows)}

@cache
def statements(formula):
    assert Grammar(repo.config()).validate(formula) is None
    class ExactDivision(ast.NodeTransformer):
        def visit_BinOp(self,node):
            node=self.generic_visit(node)
            if isinstance(node.op,ast.Div):
                return ast.copy_location(ast.Call(ast.Name('Fraction',ast.Load()),[node.left,node.right],[]),node)
            return node
    result=[]
    for statement in formula.split(';'):
        target,expression=statement.split('=',1)
        expression=re.sub(r'\b(u?int(?:8|16|32))\((ffff[0-9a-f]{4})\)',
            lambda match:match[1]+'(memory[0x'+match[2]+'])',expression)
        expression=re.sub(r'\b([0-9a-f]{8})\b',r'0x\1',expression)
        expression=re.sub(r'\bfrom\b','source',expression)
        tree=ast.fix_missing_locations(ExactDivision().visit(ast.parse(expression.strip(),mode='eval')))
        result.append((target.strip(),builtins.compile(tree,'knock-arithmetic','eval')))
    return result

def evaluate(formula,**inputs):
    def signed(value):
        value=int(value)&0xffffffff
        return value-0x100000000 if value&0x80000000 else value
    env={'memory':{},'RAM16':{},'RAM32':{},'ROM8':{},'uint8':lambda value:int(value)&255,
        'uint16':lambda value:int(value)&65535,'uint32':lambda value:int(value)&0xffffffff,
        'int32':signed,'floor':floor,'min':min,'max':max,'abs':abs,'Fraction':Fraction,'source':0,'x':0}
    env.update(inputs)
    for target,program in statements(formula):env[target]=eval(program,{'__builtins__':{}},env)
    return env['to']

def formula_contract(packet,formulas=None,rows=None):
    formulas=contracts()['formulas'] if formulas is None else formulas
    rows=literals(packet) if rows is None else rows
    signed=lambda value:value-0x100000000 if value&0x80000000 else value
    if packet=='metric':
        for row in rows:
            scope,c,selector,mask,count,gain,sample,reference,difference,ordered,total,output,biased,gprs,t=row
            rom={0x8b3d:selector,0x8618:mask,0x8870:count,0x86a7:gain[0],0x8694:gain[1],0x86ac:gain[2]}
            if scope==0:
                ram={0xffff20c2+2*i:value for i,value in enumerate(sample)}
                ram.update({0xffff2178+16*(c-1)+2*i:value for i,value in enumerate(reference)})
                memory={0xffff11de:c if not selector&8 else 7-c,0xffff2143:c if selector&8 else 7-c}
                assert evaluate(formulas['composite_note'],ROM8=rom,RAM16=ram,memory=memory)==biased
                for i in range(8):
                    assert evaluate(formulas['subtraction_note'],ROM8=rom,RAM16=ram,x=i,memory=memory)==signed(difference[i])
            if scope!=2:
                assert evaluate(formulas['sum_note'],ROM8=rom,
                    RAM32={0xffff2158+4*i:value for i,value in enumerate(difference)})==signed(total)
            assert evaluate(formulas['scale_note'],ROM8=rom,source=total)==signed(output)
    else:
        assert packet=='normalization'
        for row in rows:
            mode,c,selector,b,f,other,t,p,bins,outputs,quotients,gprs,macl,saved_r3,sr,has_long=row
            ram={0xffff2132+2*i:value for i,value in enumerate(bins)}
            memory={0xffff2154:b,0xffff2152:p,0xffff87e1:f}
            for i in range(8):
                assert evaluate(formulas['normal_note'],RAM16=ram,x=i,memory=memory)==outputs[i]
