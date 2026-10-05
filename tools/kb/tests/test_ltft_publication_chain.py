"""Bind complete LTFT publication to stock bytes, literals and typed owners."""
import ast
import builtins
from collections import Counter
from dataclasses import asdict, replace
from functools import cache
import hashlib
import importlib.util
import re
import sys
from types import SimpleNamespace

import pytest
from kb import compile, derive, repo, sh2
from kb.arithmetic import Grammar
from kb.model import SymbolKey

TOOL_DIR=repo.ROOT/'tools/sh-elf-run'
KEY='jk08a-ltft-publication'


FN='liberal-dormouse/fn'


FUNCTION=SymbolKey('7mfk','fn',0x57b26)


PREDICATE='diagnostic_record_byte1_bit7_predicate/fn'


CODE_SPANS=((0x57b26,0x57b7a),(0x57bd4,0x57c34),(0x25e20,0x25e44))


POOLS=((0x8e5a,1),(0x8e5b,1),(0x25f10,4),(0x57b7a,2),(0x57b7c,2),
       (0x57bc0,4),(0x57bc4,4),(0x57bc8,4),(0x57bcc,4),(0x57bd0,4),
       (0x57d1a,2),(0x57e34,4),(0x57e38,4),(0x57e3c,4),(0x57e40,4),(0x57e44,4))


ALIASES=(0x25f10,0x57bc0,0x57bc4,0x57bc8,0x57bcc,0x57e3c,0x57e40,0x57e44)


EXISTING=(
    ('ltft_learned_b1/ram',0xffff2306),('inquisitive-dormouse/ram',0xffff2308),
    ('ltft_adjustment_b1/ram',0xffff5648),('benevolent-anteater/ram',0xffff564a),
    ('ltft_b1/ram',0xffff2302),('ltft_b2/ram',0xffff2304),
    ('logical-swan/ram',0xffff230e),('gay-bloodhound/ram',0xffff15fc),
    ('origami-iguana/ram',0xffff41fa),('onyx-jerboa/ram',0xffff248b),
    ('jovial-buzzard/ram',0xffff249c),(FN,0x57b26),(PREDICATE,0x25e20),
    ('tourmaline-jackal/ram',0xffff5a93),('hallowed-malkoha/ram',0xffff5718),
    ('hungry-sidewinder/ram',0xffff22f8),('outstanding-marmot/ram',0xffff128c))


NEW=(
    ('ltft_limit_comparison_word/ram',0xffff15fe),
    ('ltft_publication_neutral_control/ram',0xffff41b5),
    ('ltft_publication_upper_bound/tbl',0x8e5a),
    ('ltft_publication_lower_bound/tbl',0x8e5b))


FUTURE_PATH='tools/kb/tests/test_ltft_publication_chain.py'


OWNER_KEY='test_ltft_publication_chain_owner_contract'


STOCK_KEY='test_ltft_publication_registered_stock_contract'


SYMBOLS=(('SELECTED','ltft_learned_b1/ram'),('ADJUSTMENT','ltft_adjustment_b1/ram'),
    ('OUTPUT','ltft_b1/ram'),('MASK','logical-swan/ram'),('COMPARE_U','gay-bloodhound/ram'),
    ('COMPARE_V','ltft_limit_comparison_word/ram'),('DIAGNOSTIC_RECORD','tourmaline-jackal/ram'),
    ('CONTROL_F','ltft_publication_neutral_control/ram'),('CONTROL_G','origami-iguana/ram'),
    ('CONTROL_H','onyx-jerboa/ram'),('CONTROL_K','jovial-buzzard/ram'),
    ('LOWER','ltft_publication_lower_bound/tbl'),('UPPER','ltft_publication_upper_bound/tbl'))


CONSTANTS=(('DIAGNOSTIC_BYTE1_OFFSET',1),)


SPEC_PATH='defs/JK08A.fuel.md'


SPEC_SECTION='Bounded LTFT publication'


REF_SYMBOL_NOTE='''The real predicate is executed with natural returns for caller ids 012d and 013f, yielding byte1 addresses ffff5aa0 and ffff5ad6. Direct contexts separately vary all record bytes and full R4 upper words; a low-word ffff sentinel returns zero without a record read. Full R4 is preserved and nonsentinel pointer arithmetic consumes its signed low word. Other signed indices, array extent, diagnostic production and hardware identity remain outside this bounded proof. Existing generic predicate contract and other caller evidence are unchanged.'''


REF_READER_NOTE='''The real predicate uses three-byte records, loads byte1 at 00025e32 and returns bit7. Bounded direct contexts use ids 012d/013f with independent upper-word R4 patterns; the low-word ffff sentinel makes no record read. Nonsentinel R6 addresses base+3*id while full R4 is preserved. These indexed reader claims establish no complete array extent, record producer or hardware meaning. The existing diagnostic record byte unit and both ledger claiming ends remain unchanged.'''


REF_EVIDENCE=(dict(kind='l0',at='7mfk:00025e20'),
    dict(kind='test',path='tools/kb/tests/test_knock_reference_learning_chain.py',key='test_knock_reference_learning_chain_owner_contract'),
    dict(kind='test',path='tools/kb/tests/test_knock_reference_learning_chain.py',key='test_knock_reference_learning_registered_stock_contract'),
    dict(kind='spec',path='defs/JK08A.knock-detection.md',key='Bounded knock reference learning'))


REF_LEDGER=(
    ('hallowed-malkoha/ram','vars',429,dict(role='consumer',to=PREDICATE,type='reader',end='owner',relies='structure',supports='identity')),
    (PREDICATE,'funcs',522,dict(role='indexed_by',to='hallowed-malkoha/ram',type='reader',end='to',link_role='indexed_by',relies='structure',supports='identity')),
    (PREDICATE,'funcs',522,dict(role='indexed_by',to='hallowed-malkoha/ram',type='reader',end='to',link_role='indexed_by',relies='structure',supports='contract')))


FORMULA='b = uint8(x); L = uint16(RAM16[0xffff2306+2*b]); A = uint16(RAM16[0xffff5648+2*b]); R = uint32(L+A-25600); U = uint16(ffff15fc); V = int16(ffff15fe); C = (1-((uint8(ffff230e)>>b)&1))*min(1,max(0,U-V)); lo = ROM8[0x00008e5b]*256; hi = ROM8[0x00008e5a]*256; W = C*min(hi,max(lo,R))+(1-C)*R; D = (uint8(ffff5a94)>>7)&1; F = uint8(ffff41b5)&1; G = (uint8(ffff41fa)&1)*((uint8(ffff248b)>>1)&1); K = ((uint8(ffff249c)>>6)&1)*(uint8(ffff248b)&1); Z = 1-(1-D)*(1-F)*(1-G)*(1-K); to = Z*25600+(1-Z)*uint16(W)'
ROM_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
SPANS=tuple((start,end,bytes.fromhex(data)) for start,end,data in ((359206, 359290, '2fd62fe64f22644cd624d52460434000026d6d03065de0166e2dd221666d3e6ce69c46183e6c062c62437201666c26288b48d51c900e025d900d622d065d32678b40d2196620656c625342183e22892ea02e4518'), (359380, 359476, '65e3d2976620666c6263421835268b01461865636e53d2939495420b000920088b15d691846cc8018b11e051006cc8018904d68ee01b006cc8028b08d68be02c006cc8408905e01b006cc8018901ee644e18d28760d302e54f266ef6000b6df6'), (155168, 155204, 'd13b604f88ff890a661362034200320c362c8461c8800029ca01a001620ce200000b6023'), (36442, 36443, '6e'), (36443, 36444, '5a'), (155408, 155412, 'ffff5718'), (359290, 359292, '0370'), (359292, 359294, '0372'), (359360, 359364, 'ffff2306'), (359364, 359368, 'ffff5648'), (359368, 359372, 'ffff22f8'), (359372, 359376, 'ffff128c'), (359376, 359380, '00008e5b'), (359706, 359708, '0129'), (359988, 359992, '00008e5a'), (359992, 359996, '00025e20'), (359996, 360000, 'ffff41a9'), (360000, 360004, 'ffff2470'), (360004, 360008, 'ffff2302')))
SUMMARY={'cases': 12028, 'populations': {'factory-bounds-seeded-grid-adjustment': 2880, 'neutral-condition-boolean-cross': 768, 'full-mask-byte-sweep': 512, 'full-diagnostic-byte-sweep': 512, 'full-f-byte-sweep': 512, 'full-g-byte-sweep': 512, 'full-h-byte-sweep': 512, 'full-k-byte-sweep': 512, 'unsigned-u-signed-v-boundaries': 336, 'raw-underflow-word-wrap-limit-equality': 720, 'artificial-lower-byte-sweep': 1024, 'artificial-upper-byte-sweep': 1024, 'artificial-bound-equality-reversed-pairs': 924, 'full-word-input-axis': 768, 'deterministic-full-contexts': 512}, 'bank_counts': {'0': 6014, '1': 6014}, 'incoming_t_counts': {'0': 6014, '1': 6014}, 'factory_bound_contexts': 8564, 'artificial_bound_contexts': 3464, 'active_limit_contexts': 7873, 'mask_bypass_contexts': 2744, 'comparison_bypass_contexts': 1411, 'neutral_contexts': 2452, 'numerical_publication_contexts': 9576, 'raw_underflow_contexts': 5046, 'low16_wrap_contexts': 979, 'reversed_bound_contexts': 1612, 'helper_domain': 'Every natural invocation uses genuine diagnostic id0129; the low-word ffff sentinel arm is outside this fixed-caller envelope.', 'scope': 'All RAM/register/diagnostic/control inputs are explicit independent contexts. Bounds are factory or labelled artificial; no engine reachability claim.'}
STEP_FIELDS=({'from': 'ltft_learned_b1/ram', 'to': 'ltft_b1/ram', 'effect': 'adds', 'via': ['liberal-dormouse/fn']}, {'from': 'ltft_adjustment_b1/ram', 'to': 'ltft_b1/ram', 'effect': 'adds', 'via': ['liberal-dormouse/fn']})

DOC_ARITHMETIC_DECLARATIONS={'spec': {'Full incoming R4 is an independent context.': 1, 'Its low byte b=uint8(R4) is admitted only in 0..1, and its upper 24 bits vary independently.': 1, 'The bounded numerical inputs are unsigned words L at ffff2306+2*b and A at ffff5648+2*b.': 1, 'U at ffff15fc is zero-extended; V at ffff15fe is sign-extended.': 1, 'The complete byte mask M at ffff230e tests b+1, which is 1 or 2 for these legal banks.': 1, 'Bounds lo=ROM8[00008e5b]*256 and hi=ROM8[00008e5a]*256 have stock operands 90 and 110.': 1, 'Every value 0..255 and reversed bound pairs also have explicit artificial contexts.': 1, 'Each genuine short-circuit neutral condition is separate from the numerical limit gate.': 1, 'Diagnostic id 0129 addresses byte1 at ffff5718+3*0129+1=ffff5a94.': 1, 'The fixed caller cannot take the predicate sentinel branch at 25E26 to 25E3E.': 1, 'That branch and MOV #0,R2 at 25E3E are identity-only; direct sentinel, negative-id and independent helper upper-word semantics are not claimed.': 1, 'Equality U=V skips limiting.': 1, 'Negative mathematical sums wrap to uint32 before the genuine unsigned comparisons.': 1, 'Full-domain output can decrease when either input increases, so the two complete publication views use sign=none.': 1, 'Independent integer expectations cover all 12028 output/T and fifteen-GPR vectors, full R4 upper patterns, every mask/diagnostic/control/bound byte value, all neutral combinations, all three numerical gate outcomes, unsigned underflow, low-word wrap, signed comparison boundaries and bound equality.': 1, 'Every literal checks full 64 KiB RAM except the selected output word, both allowed output bytes, every bound data byte, all fifteen GPRs, MACH/MACL/GBR, natural PR/SP, immutable context and an independent C ABI.': 1, 'The actual current SR nonT bits are retained while requested T=0/1 is injected.': 1, 'STC records prepared full SR, and exit SR equals (preparedSR&~1)|expectedT.': 1, 'Arbitrary nonT variation or incoming full SR=0/1 is not claimed.': 1, 'The 80-byte observer covers SP-48..SP+31 with saved R13/R14/PR at SP-4/-8/-12.': 1, 'Snapshots are per literal.': 1}, 'readme': {'The fixed caller uses id 0129; the predicate sentinel branch/MOV at 25E3E is identity-only, with no direct sentinel or independent helper upper-word execution claim.': 1, 'Both legal banks use full incoming R4 with varied upper bits, independent uint16 selected/adjustment words, full byte controls and unsigned U versus signed V.': 1, 'The exact uint32 sum, both limit bypasses, active lower-then-upper comparisons and all four neutral causes have independent expectations.': 1, 'Each case checks output bytes, all fifteen GPRs and final T, full prepared SR nonT preservation, natural special registers/PR/SP, distinct external C ABI, all other RAM bytes and all 52 data bytes.': 1, 'The 80-byte observer uses matching SP-48..SP+31 origins, with natural R13/R14/PR saves at SP-4/-8/-12.': 1, 'RAM/data snapshots are per literal, without block aggregation; an arbitrary full incoming SR=0/1 is not claimed.': 1}}

def tool_text(name):
    path=TOOL_DIR/name
    assert path.is_file(),f'Missing required stock source: {name}'
    return path.read_text()


def harness_identity(contents):
    assert isinstance(contents,bytes)
    assert hashlib.sha256(contents).hexdigest()=='35504757402bb54ffac1bd4397063723dee6b6c73b71874d7df58ecc9f49bb37'
    return contents.decode('ascii')


def registered_region(regions=None):
    regions=stock_verifier().REGIONS if regions is None else regions
    matches=[region for region in regions if region.key==KEY]
    assert len(matches)==1,'Required LTFT Region must occur exactly once'
    exact_region(matches[0])
    return matches[0]


def section(text,title):
    matches=re.findall(rf'^## {re.escape(title)}\n(.*?)(?=^## |\Z)',text,re.S|re.M)
    assert len(matches)==1,f'Required section must occur exactly once: {title}'
    return matches[0]


def document(kind):
    assert kind in ('spec','readme')
    path,title=(SPEC_PATH,SPEC_SECTION) if kind=='spec' else ('tools/sh-elf-run/README.md','LTFT publication')
    return section((repo.ROOT/path).read_text(),title)


def actual_counts():
    region=registered_region()
    count=len(literals())
    [macro]=re.findall(r'^#define LTFT_PUBLICATION_CASE_COUNT (\d+)U$',tool_text('stock-jk08a-ltft-publication-cases.h'),re.M)
    assert count==int(macro)==region.cases==12028
    return sum((end-start)//2 for start,end in region.code_spans),sum(end-start for start,end in region.code_spans)+sum(size for _,size in region.pools),count


BOUNDED_ARITHMETIC='''raw = uint32(L+A-25600)
active = ((M&(b+1))==0) and (U>V)
limited = min(hi,max(lo,raw)) if active else raw
neutral = diagnostic_byte1.bit7 or F.bit0
          or (G.bit0 and H.bit1) or (K.bit6 and H.bit0)
output = 25600 if neutral else uint16(limited)'''
LEGACY_RAW='raw_b = uint32(uint16[0xFFFF2306 + 2*b] + uint16[0xFFFF5648 + 2*b] - 0x6400)'
LEGACY_CLAMP='''raw_b = min(max(raw_b, ROM8[0x8E5B] << 8), ROM8[0x8E5A] << 8)
ROM8[0x8E5B] = 90, ROM8[0x8E5A] = 110'''
LEGACY_NEUTRAL='''FUN 00025E20(0x0129) != 0
uint8[0xFFFF41B5].bit0 set
uint8[0xFFFF41FA].bit0 set and uint8[0xFFFF248B].bit1 set
uint8[0xFFFF249C].bit6 set and uint8[0xFFFF248B].bit0 set'''
LEGACY_DOMAIN='The legal bank is b=uint8(full incoming R4) in 0..1; its upper 24 bits are independent of b.'
LEGACY_PUBLICATION='The final word store publishes uint16(raw_b) unless a neutral condition selects 0x6400.'
LEGACY_LIMIT='Otherwise the raw uint32 value is limited by unsigned comparisons between two adjacent ROM bytes scaled to Q8.8 percent:'


def arithmetic_declarations(text):
    prose=re.sub(r'^ {4}.*(?:\n|\Z)','',text,flags=re.M)
    prose=re.sub(r'```.*?```','',prose,flags=re.S)
    sentences=re.split(r'(?<=[.!?])\s+', ' '.join(prose.split()))
    pattern=r'\b(?:uint32|uint16|sign=none|U\s*(?:>|<=|=)\s*V|neutral|sentinel|0129|upper 24|uint8\(R4\)|bounded numerical inputs|zero-extended|sign-extended|Every value|complete byte mask|Bounds lo|Full incoming R4|nonT|STC|SR|observer|Snapshots|per literal|full 64|fifteen.GPR)\b'
    return Counter(sentence for sentence in sentences if re.search(pattern,sentence))


def document_contract(text,kind):
    publication(text,actual_counts())
    publication_details(text,kind=='spec')
    blocks=re.findall(r'(?:^ {4}[^\n]+\n?)+',text,re.M)
    blocks=[block for block in blocks if re.search(r'^ {4}raw\s*=',block,re.M)]
    assert len(blocks)==1
    assert re.sub(r'\s+','',blocks[0])==re.sub(r'\s+','',BOUNDED_ARITHMETIC)
    assert arithmetic_declarations(text)==DOC_ARITHMETIC_DECLARATIONS[kind]
    assert FUTURE_PATH in text and OWNER_KEY in text and STOCK_KEY in text
    assert not re.search(r'\b(?:ignored|prospective|pending integration|explicitly pending)\b',text,re.I)


def legacy_publication_contract(text):
    [legacy]=re.findall(r'^### Long-term trim publication and neutralization\n(.*?)(?=^### |^## |\Z)',text,re.S|re.M)
    blocks=re.findall(r'```text\n(.*?)\n```',legacy,re.S)
    assert tuple(re.sub(r'\s+','',block) for block in blocks)==tuple(
        re.sub(r'\s+','',block) for block in (LEGACY_RAW,LEGACY_CLAMP,LEGACY_NEUTRAL))
    assert legacy.count(LEGACY_DOMAIN)==1 and legacy.count(LEGACY_PUBLICATION)==1
    assert ' '.join(legacy.split()).count(LEGACY_LIMIT)==1
    raw_assignments=re.findall(r'\braw_b\s*=[^\n]+',legacy)
    assert tuple(re.sub(r'\s+','',item) for item in raw_assignments)==tuple(
        re.sub(r'\s+','',item) for item in (LEGACY_RAW,LEGACY_CLAMP.splitlines()[0]))


def named_proof(evidence):
    assert all(item in evidence for item in (
        dict(kind='test',path=FUTURE_PATH,key=OWNER_KEY),
        dict(kind='test',path=FUTURE_PATH,key=STOCK_KEY),
        dict(kind='spec',path=SPEC_PATH,key=SPEC_SECTION)))


def required_owner(model,name,address):
    assert name in {owner.key for owner in model.meanings},f'Missing required owner: {name}'
    owner=model.meaning_of(SymbolKey('7mfk',name.split('/')[1],address))
    assert owner.key==name and owner.symbols['7mfk'].key.address==address
    return owner


def ltft_step_contract(model,steps):
    assert len(steps)==19
    for index,fields in zip((13,14),STEP_FIELDS):
        step=normalized(model,steps[index])
        assert {key:value for key,value in step.items() if key not in ('note','sign')}==fields
        assert step['sign']=='none' and re.sub(r'\s+','',step['note'])==re.sub(r'\s+','',FORMULA)
        assert Grammar(repo.config()).validate(step['note']) is None


def reference_symbol_contract(symbol):
    assert any(' '.join(note.split())==REF_SYMBOL_NOTE for note in symbol.props.get('note',[]))
    assert all(item in symbol.evidence for item in REF_EVIDENCE)


def reference_reader_contract(model,link):
    assert (link.owner.key,link.type,link.to.key,link.slot,link.offset)==(
        'hallowed-malkoha/ram','reader',PREDICATE,None,None)
    assert link.stated=={'7mfk'} and 'indexed_by' in link.roles
    assert normalized(model,link.props.get('via'))==[PREDICATE]
    assert ' '.join(link.props.get('note','').split())==REF_READER_NOTE
    for key,value in dict(relies='structure',supports='identity',reverse_relies='structure',
                          reverse_supports=['contract','identity']).items():
        assert link.props.get(key)==value
    assert all(item in link.evidence for item in REF_EVIDENCE)


def ledger_claim(model,owner,registry,order,dependency):
    name,kind=owner.split('/')
    [rows]=[rows for marker_kind,owner_name,rows,_ in model.stash['ledger_rows']
            if (marker_kind,owner_name)==(kind,name)]
    [row]=[item for item in rows if (item['registry'],item['order'])==(registry,order)]
    assert dependency in row.get('dependency',[])


def reference_shared_contract(model):
    predicate=model.meaning_of(SymbolKey('7mfk','fn',0x25e20))
    records=model.meaning_of(SymbolKey('7mfk','ram',0xffff5718))
    assert predicate.key==PREDICATE and records.key=='hallowed-malkoha/ram'
    reference_symbol_contract(predicate.symbols['7mfk'])
    [reader]=[link for link in records.links if link.type=='reader' and link.to.key==PREDICATE]
    reference_reader_contract(model,reader)
    for expected in REF_LEDGER:ledger_claim(model,*expected)


def synthetic_reference_reader():
    return SimpleNamespace(owner=SimpleNamespace(key='hallowed-malkoha/ram'),type='reader',
        to=SimpleNamespace(key=PREDICATE),slot=None,offset=None,stated={'7mfk'},roles={'indexed_by'},
        props=dict(via=[PREDICATE],note=REF_READER_NOTE,relies='structure',supports='identity',
                   reverse_relies='structure',reverse_supports=['contract','identity']),
        evidence=[dict(item) for item in REF_EVIDENCE])


def expected_conditions():
    """Independent explicit software conditions for the typed links."""
    result=[]
    def add(owner,kind,target,note,slot=None,via=None,offset=None):
        item=dict(owner=owner,kind=kind,target=target,slot=slot,via=via or [FN],note=note)
        if offset is not None:item['offset']=offset
        result.append(item)
    readers=(
        ('ltft_learned_b1/ram','b=0: L=RAM16[ffff2306]. The bounded indexed MOV.W/EXTU.W supplies unsigned16 L; b=1 does not read this sibling.'),
        ('inquisitive-dormouse/ram','b=1: L=RAM16[ffff2306+2]. The bounded indexed MOV.W/EXTU.W supplies unsigned16 L; b=0 does not read this sibling.'),
        ('ltft_adjustment_b1/ram','b=0: A=RAM16[ffff5648]. The bounded indexed MOV.W/EXTU.W supplies unsigned16 A; b=1 does not read this sibling.'),
        ('benevolent-anteater/ram','b=1: A=RAM16[ffff5648+2]. The bounded indexed MOV.W/EXTU.W supplies unsigned16 A; b=0 does not read this sibling.'),
        ('logical-swan/ram','Incoming full R4 has b=uint8(x) in 0..1. The complete raw mask M=uint8(ffff230e) is tested with b+1. (M&(b+1))!=0 bypasses U/V reads and numerical limiting; clear delegates the limiting decision to unsigned U>signed V. Unrelated bits have no inferred role.'),
        ('gay-bloodhound/ram','Only when (uint8(ffff230e)&(b+1))==0, U=uint16(ffff15fc) is zero-extended unsigned16. Compare U>signed V enables numerical limiting; U<=V, including equality, bypasses it. This reader interpretation does not change a producer or another consumer.'),
        ('ltft_limit_comparison_word/ram','Only when (uint8(ffff230e)&(b+1))==0, V=int16(ffff15fe) is sign-extended signed16. Compare unsigned U>V enables numerical limiting; U<=V, including equality, bypasses it. No upstream writer or physical meaning follows from the bounded read.'),
        ('ltft_publication_lower_bound/tbl','Only under the numerical limit gate, lo=256*ROM8[00008e5b]. The raw uint32 sum is raised to lo before the upper comparison; reversed artificial bounds still evaluate min(hi,max(lo,R)). Generic shape prescribes no factory value.'),
        ('ltft_publication_upper_bound/tbl','Only under the numerical limit gate, hi=256*ROM8[00008e5a]. The lower-adjusted raw uint32 sum is capped to hi; reversed artificial bounds still evaluate min(hi,max(lo,R)). Generic shape prescribes no factory value.'),
        ('ltft_publication_neutral_control/ram','Only when the fixed-id diagnostic predicate clears, raw ffff41b5.bit0 set selects neutral 25600. Clear delegates to the G/H and K/H compound conditions; unrelated bits have no inferred role.'),
        ('origami-iguana/ram','After diagnostic and F conditions clear, neutral 25600 requires ffff41fa.bit0 set together with ffff248b.bit1 set. The conjunction is separate from the K/H condition and the numerical-limit gate.'),
        ('onyx-jerboa/ram','After diagnostic and F conditions clear, ffff248b.bit1 combines with ffff41fa.bit0, and ffff248b.bit0 combines with ffff249c.bit6, to select neutral 25600. Both conjunctions are separate; unrelated bits have no inferred role.'),
        ('jovial-buzzard/ram','Only after diagnostic, F and G/H conditions clear, neutral 25600 requires ffff249c.bit6 set together with ffff248b.bit0 set. Otherwise the numerical result publishes its low word; unrelated bits have no inferred role.'),
    )
    for owner,note in readers:add(owner,'reader',FN,note)
    for bank,output,inputs in (
        (0,'ltft_b1/ram',('ltft_learned_b1/ram','ltft_adjustment_b1/ram')),
        (1,'ltft_b2/ram',('inquisitive-dormouse/ram','benevolent-anteater/ram'))):
        for source in inputs:
            add(output,'input',source,f'b=uint8(incoming full R4)={bank}: this zero-extended unsigned16 input participates in uint32(L+A-25600) for one bounded publication. Its producer units/signedness and sibling bank are preserved. Raw underflow and bypassed low-word wrap prevent a universal positive sign.')
        add(output,'writer',FN,f'Incoming independent full R4 has uint8(x)={bank}. Publish exactly one uint16 word at ffff2302+2*b. The complete arithmetic note describes one publication shared by steps 14/15, not sequential additions. Numerical limiting uses (M&(b+1))==0 and unsigned U>signed V; equality bypasses. Any diagnostic/F/GH/KH neutral condition writes 25600; otherwise publish uint16(W). Natural return restores R13/R14/PR; terminal T=!neutral. All other RAM/data/frame and external C ABI remain preserved without a dispatcher, producer or physical bank claim.')
        add(output,'selector','logical-swan/ram',f'b={bank}: mask bit{bank} clear permits unsigned U>signed V to enable numerical limiting; set bypasses limiting and both comparison reads. The raw sum remains uint32(L+A-25600); neutral predicates remain independent.',f'bit{bank}')
        for source in ('gay-bloodhound/ram','ltft_limit_comparison_word/ram'):
            add(output,'threshold',source,'With the selected mask bit clear, unsigned U>signed V enables numerical limiting. U<=V, including equality, bypasses limiting. Both word interpretations belong to this bounded reader; no producer or physical threshold is inferred.')
        for source,name in (('ltft_publication_lower_bound/tbl','lo'),('ltft_publication_upper_bound/tbl','hi')):
            add(output,'threshold',source,f'Only under the numerical-limit gate, {name}=256*the unsigned ROM byte. W=min(hi,max(lo,uint32(L+A-25600))) applies lower then upper comparisons, including reversed artificial bounds. If the gate bypasses, W is the raw uint32 sum; a later neutral condition can still select 25600.')
        add(output,'selector','tourmaline-jackal/ram','The natural publisher calls the existing real predicate at 00025e20 with fixed id 0129. Record byte1 at ffff5a94 has bit7 set exactly when D=1, which short-circuits remaining neutral conditions and writes 25600. The sentinel helper arm is identity-only for this caller; no record producer or general-id execution is claimed.','byte1.bit7',[FN,PREDICATE])
        for source,slot,condition in (
            ('ltft_publication_neutral_control/ram','bit0','After D=0, F=ffff41b5.bit0 set'),
            ('origami-iguana/ram','bit0','After D=0 and F=0, ffff41fa.bit0 set together with ffff248b.bit1 set'),
            ('onyx-jerboa/ram','bit1','After D=0 and F=0, ffff248b.bit1 set together with ffff41fa.bit0 set'),
            ('onyx-jerboa/ram','bit0','After D=0, F=0 and the G/H conjunction clear, ffff248b.bit0 set together with ffff249c.bit6 set'),
            ('jovial-buzzard/ram','bit6','After D=0, F=0 and the G/H conjunction clear, ffff249c.bit6 set together with ffff248b.bit0 set')):
            add(output,'selector',source,condition+' selects neutral 25600. Otherwise the next short-circuit condition or the numerical result applies. No hardware mode or unrelated-bit role is inferred.',slot)
    add('ltft_limit_comparison_word/ram','base','outstanding-marmot/ram','The bounded signed16 comparison reads this word at existing raw base ffff128c+0372. The exact pool and consumer bind the offset, without an array extent or producer claim.',offset=0x372)
    add('logical-swan/ram','base','hungry-sidewinder/ram','The bounded mask-byte consumer reads this byte at existing raw base ffff22f8+0016. The exact pool and consumer bind the offset, without an array extent or producer claim.',offset=0x16)
    assert len(result)==43
    return tuple(result)


CONDITIONS=expected_conditions()

def exact_condition(model,link,expected):
    assert link.owner.key==expected['owner']
    assert (link.type,link.to.key,link.slot)==(expected['kind'],expected['target'],expected['slot'])
    assert link.offset==expected.get('offset')
    assert link.stated=={'7mfk'}
    assert link.props['relies']=='structure' and link.props['supports']=='identity'
    if expected['kind']=='writer' or (expected['kind']=='reader' and expected['owner'] in {name for name,_ in EXISTING[:4]}):
        assert link.props['reverse_relies']=='structure' and link.props['reverse_supports']=='identity'
    if expected['kind']=='reader' and expected['owner'] in {name for name,_ in EXISTING[:4]}:
        assert 'indexed_by' in link.roles
    assert normalized(model,link.props['via'])==expected['via']
    assert ' '.join(link.props['note'].split())==' '.join(expected['note'].split())
    tests={(e.get('path'),e.get('key')) for e in link.evidence if e['kind']=='test'}
    assert {(FUTURE_PATH,OWNER_KEY),(FUTURE_PATH,STOCK_KEY)}<=tests
    assert dict(kind='spec',path=SPEC_PATH,key=SPEC_SECTION) in link.evidence


def synthetic_link(expected):
    props=dict(via=list(expected['via']),note=expected['note'],relies='structure',supports='identity')
    indexed=expected['kind']=='reader' and expected['owner'] in {name for name,_ in EXISTING[:4]}
    if indexed or expected['kind']=='writer':props.update(reverse_relies='structure',reverse_supports='identity')
    return SimpleNamespace(owner=SimpleNamespace(key=expected['owner']),type=expected['kind'],
        to=SimpleNamespace(key=expected['target']),slot=expected['slot'],offset=expected.get('offset'),
        stated={'7mfk'},props=props,roles={'indexed_by'} if indexed else set(),
        evidence=[dict(kind='test',path=FUTURE_PATH,key=OWNER_KEY),
                  dict(kind='test',path=FUTURE_PATH,key=STOCK_KEY),
                  dict(kind='spec',path=SPEC_PATH,key=SPEC_SECTION)])


@cache
def stock_verifier():
    spec=importlib.util.spec_from_file_location('ltft_future_registered_verifier',
                                              repo.ROOT/'tools/sh-elf-run/verify_stock_code.py')
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    return module


def future_region():
    return stock_verifier().Region(key=KEY,rom='JK08A',
        source='stock_jk08a_ltft_publication.s',harness='harness-stock-jk08a-ltft-publication.c',
        start=CODE_SPANS[0][0],end=CODE_SPANS[0][1],pools=POOLS,ram_literals=ALIASES,
        cases=12028,boundary=False,callees=CODE_SPANS[1:],symbols=SYMBOLS,constants=CONSTANTS)


def exact_region(region):
    assert asdict(region)==asdict(future_region())
    assert region.code_spans==CODE_SPANS
    assert region.cases==len(literals())


def verify_stock(data):
    for start,end,expected in SPANS:
        assert data[start:end]==expected,f'{start:08x}'
    word=lambda at,size=2:int.from_bytes(data[at:at+size],'big')
    assert tuple((s,e) for s,e,_ in SPANS[:3])==CODE_SPANS
    assert [(word(at,4)) for at in ALIASES]==[
        0xffff5718,0xffff2306,0xffff5648,0xffff22f8,
        0xffff128c,0xffff41a9,0xffff2470,0xffff2302]
    assert [word(at,4) for at in (0x57bd0,0x57e34,0x57e38)]==[0x8e5b,0x8e5a,0x25e20]
    assert [word(at) for at in (0x57b7a,0x57b7c,0x57d1a)]==[0x370,0x372,0x129]
    assert [word(at,1) for at in (0x8e5a,0x8e5b)]==[110,90]
    assert word(0x57bc8,4)+0x16==dict(EXISTING)['logical-swan/ram']
    assert word(0x57bcc,4)+word(0x57b7a)==dict(EXISTING)['gay-bloodhound/ram']
    assert word(0x57bcc,4)+word(0x57b7c)==dict(NEW)['ltft_limit_comparison_word/ram']
    assert word(0x57e3c,4)+0xc==dict(NEW)['ltft_publication_neutral_control/ram']
    assert word(0x57e3c,4)+0x51==dict(EXISTING)['origami-iguana/ram']
    assert word(0x57e40,4)+0x1b==dict(EXISTING)['onyx-jerboa/ram']
    assert word(0x57e40,4)+0x2c==dict(EXISTING)['jovial-buzzard/ram']
    assert word(0x25f10,4)+3*word(0x57d1a)==dict(EXISTING)['tourmaline-jackal/ram']
    assert [word(at) for at in (0x57b26,0x57b28,0x57b2a,0x57b2c)]==[
        0x2fd6,0x2fe6,0x4f22,0x644c]
    assert [word(at) for at in (0x57bee,0x57bf0,0x57c2a,0x57c2c,0x57c2e,0x57c30,0x57c32)]==[
        0x420b,0x0009,0x02e5,0x4f26,0x6ef6,0x000b,0x6df6]
    assert [word(at) for at in (0x25e26,0x25e3e,0x25e40,0x25e42)]==[
        0x890a,0xe200,0x000b,0x6023]
    assert sh2.decode(word(0x25e26),0x25e26).target==0x25e3e
    assert word(0x57d1a)!=0xffff  # Sentinel arm is byte-bound, not executed by this caller.
    for start,end in CODE_SPANS:
        for at in range(start,end,2):
            insn=sh2.decode(word(at),at)
            if insn.target is not None and insn.flow in ('branch','jump'):
                assert any(s<=insn.target<e for s,e in CODE_SPANS)


@cache
def literals():
    text=tool_text('stock-jk08a-ltft-publication-cases.h')
    [body]=re.findall(r'ltft_publication_cases\[\]\s*=\s*\{(.*?)\n\};',text,re.S)
    [group_body]=re.findall(r'ltft_publication_groups\[\]\s*=\s*\{(.*?)\n\};',text,re.S)
    groups=re.findall(r'"([^"]+)"',group_body)
    rows=[]
    names=('l','a','u','output','v','mask','diagnostic','f','g','h','k',
           'lower','upper','initial_t','variant','expected_t','group')
    integer=lambda value:int(value.strip().removesuffix('U'),0)
    for line in body.splitlines():
        if not line.strip():continue
        match=re.fullmatch(r'\s*\{(0x[0-9a-f]+U),\{([^{}]+)\},([^{}]+)\},',line)
        assert match is not None
        expected=[integer(x) for x in match[2].split(',')]
        values=[integer(x) for x in match[3].split(',')]
        assert len(expected)==15 and len(values)==len(names)
        row=dict(zip(names,values),raw_r4=integer(match[1]),expected=expected)
        assert row['group']<len(groups)
        row['population']=groups[row['group']]
        rows.append(row)
    return rows


@cache
def arithmetic_program():
    assert Grammar(repo.config()).validate(FORMULA) is None
    text=re.sub(r'\bffff[0-9a-f]{4}\b',lambda m:f"memory[{int(m[0],16)}]",FORMULA)
    return builtins.compile(text,'<LTFT candidate arithmetic>','exec')


def evaluate(row):
    bank=row['raw_r4']&255
    memory={0xffff2306+2*bank:row['l'],0xffff5648+2*bank:row['a'],
        0xffff15fc:row['u'],0xffff15fe:row['v']&65535,0xffff230e:row['mask'],
        0xffff5a94:row['diagnostic'],0xffff41b5:row['f'],0xffff41fa:row['g'],
        0xffff248b:row['h'],0xffff249c:row['k'],0x8e5a:row['upper'],0x8e5b:row['lower']}
    env=dict(x=row['raw_r4'],memory=memory,RAM16=memory,ROM8=memory,min=min,max=max,
        uint8=lambda n:n&255,uint16=lambda n:n&65535,uint32=lambda n:n&0xffffffff,
        int16=lambda n:(n+32768)%65536-32768)
    exec(arithmetic_program(),{'__builtins__':{}},env)
    return env


def check_vector(row):
    env=evaluate(row)
    assert env['b'] in (0,1) and row['initial_t'] in (0,1) and row['variant'] in range(4)
    assert env['to']==row['output']
    assert row['expected_t']==1-env['Z']
    vector=[(0x28765430+r*0x01030507+row['variant']*0x00102040)&0xffffffff for r in range(15)]
    vector[0]=2*env['b'];vector[1]=0x01005718;vector[2]=0x01002302
    vector[4]=0x129;vector[7]=0x57b26
    vector[5]=(0x01005648 if row['mask']&(env['b']+1) else
               0x0100128c if row['u']<=row['v'] else env['W'])
    vector[6]=0x01005a93 if env['D'] else 0x010041a9 if env['F'] else 0x01002470
    assert row['expected']==vector


def normalized(model,value):
    if isinstance(value,SymbolKey):return model.meaning_of(value).key
    if isinstance(value,list):return [normalized(model,item) for item in value]
    if isinstance(value,dict):return {key:normalized(model,item) for key,item in value.items() if item is not None}
    return value


def publication(text,counts):
    units={'instructions':'instructions?','bytes':'bytes?','cases':'(?:cases?|times)'}
    for count,unit in zip(counts,('instructions','bytes','cases')):
        found=[]
        pattern=r'\b([0-9][0-9,]*)\s*(?:-\s*)?(?:(?:stock|bound|literal|executed|dynamic|independent)\s+)?'+units[unit]+r'\b'
        for match in re.finditer(pattern,text,re.I):
            after=text[match.end():].lstrip()
            if unit=='instructions' and re.match(r'bytes\b',after,re.I):
                continue
            if unit=='cases' and re.search(
                    r'\bEach\s+(?:legal bank|incoming T value)\s+has\s*$',
                    text[:match.start()],re.I):
                continue
            if unit=='bytes' and re.match(r'(?:(?:observed|stack|local|natural|saved|save|'
                r'R13/R14/PR|exit|capture)\s+)*(?:frame|pool|longword|word|pointer|'
                r'calibration|RAM|output|capture|observer)\b',after,re.I):
                continue
            found.append(int(match[1].replace(',','')))
        assert found and set(found)=={count},(unit,found,count)
    for phrase in ('identity-only','0129','SP-48..SP+31','nonT','physical'):
        assert phrase in text


def publication_details(text,is_spec):
    c=tool_text('harness-stock-jk08a-ltft-publication.c')
    [(frame_before,frame_after)]=re.findall(r'frame_before\[([0-9]+)\],frame_after\[([0-9]+)\]',c)
    assert frame_before==frame_after
    frames=[int(n) for n in re.findall(r'\b([0-9]+)\s*(?:-\s*)?bytes?\s+(?:observed\s+)?(?:frame|observer)\b',text)]
    assert frames and set(frames)=={int(frame_before)}
    data=[int(n) for n in re.findall(r'\b([0-9]+)\s+(?:bound\s+)?data\s+bytes\b',text)]
    assert data and set(data)=={sum(n for _,n in POOLS)}
    code_bytes=[int(n) for n in re.findall(r'\b([0-9]+)\s+instruction\s+bytes\b',text)]
    if is_spec or code_bytes:
        assert code_bytes and set(code_bytes)=={sum(e-s for s,e in CODE_SPANS)}
    rows=literals()
    populations=Counter('factory' if (r['lower'],r['upper'])==(90,110) else 'artificial' for r in rows)
    for name,count in populations.items():
        claims=[int(n) for n in re.findall(r'\b([0-9]+)\s+'+name+r'-bound\b',text)]
        if is_spec or claims:assert claims and set(claims)=={count}
    per_bank=set(Counter(r['raw_r4']&255 for r in rows).values())
    per_t=set(Counter(r['initial_t'] for r in rows).values())
    for label,actual in (('legal bank',per_bank),('incoming T value',per_t)):
        claims=[int(n.replace(',','')) for n in re.findall(
            r'\bEach\s+'+label+r'\s+has\s+([0-9][0-9,]*)\s+cases\b',text,re.I)]
        assert len(actual)==1
        if is_spec or claims:assert claims and set(claims)==actual
    other=[int(n) for n in re.findall(r'\bother\s+([0-9]+)\s+closed_loop_fuel\s+step records\b',text)]
    if is_spec or other:assert other and set(other)=={17}


def test_ltft_exact_stock_complete_natural_return_and_helper_boundary():
    data=derive.image_bytes(repo.layout('7mfk'))
    assert hashlib.sha256(data).hexdigest()==ROM_SHA256
    verify_stock(data)
    assert actual_counts()==(108,268,12028)


@pytest.mark.parametrize('address',[at for s,e,_ in SPANS for at in range(s,e)])
def test_ltft_every_bound_stock_byte_corruption_is_rejected(address):
    data=bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address]^=1
    with pytest.raises(AssertionError):verify_stock(data)


def test_ltft_all_retained_vectors_match_existing_grammar_gprs_and_terminal_t():
    for row in literals():check_vector(row)


@pytest.mark.parametrize('field',('output','expected_t','expected'))
def test_ltft_literal_contract_rejects_output_gpr_and_t_mutations(field):
    row=dict(literals()[0]);row['expected']=list(row['expected'])
    if field=='expected':row[field][6]^=1
    else:row[field]^=1
    with pytest.raises(AssertionError):check_vector(row)


def test_ltft_actual_matrix_and_all_full_byte_domains():
    rows=literals();summary=SUMMARY
    assert Counter(row['population'] for row in rows)==summary['populations']
    assert Counter(str(row['raw_r4']&255) for row in rows)==summary['bank_counts']=={'0':6014,'1':6014}
    assert Counter(str(row['initial_t']) for row in rows)==summary['incoming_t_counts']=={'0':6014,'1':6014}
    assert {r['raw_r4']&0xffffff00 for r in rows}=={0,0x80000000,0xa5c30000,0xffffff00}
    for field in ('mask','diagnostic','f','g','h','k','lower','upper'):
        population=('full-' if field not in ('lower','upper') else 'artificial-')+field+'-byte-sweep'
        for bank in (0,1):
            assert {r[field] for r in rows if r['population']==population and r['raw_r4']&255==bank}==set(range(256))
    calculated=Counter()
    for row in rows:
        env=evaluate(row)
        calculated['factory_bound_contexts']+=int((row['lower'],row['upper'])==(90,110))
        calculated['artificial_bound_contexts']+=int((row['lower'],row['upper'])!=(90,110))
        calculated['active_limit_contexts']+=env['C']
        calculated['mask_bypass_contexts']+=int(bool(row['mask']&(env['b']+1)))
        calculated['comparison_bypass_contexts']+=int(not row['mask']&(env['b']+1) and row['u']<=row['v'])
        calculated['neutral_contexts']+=env['Z']
        calculated['numerical_publication_contexts']+=1-env['Z']
        calculated['raw_underflow_contexts']+=int(row['l']+row['a']<25600)
        calculated['low16_wrap_contexts']+=int(not env['Z'] and not env['C'] and env['R']>65535)
        calculated['reversed_bound_contexts']+=int(row['lower']>row['upper'])
    assert all(summary[key]==value for key,value in calculated.items())
    boundary={r['l']+r['a']-25600 for r in rows if r['population']=='raw-underflow-word-wrap-limit-equality'}
    assert boundary=={-25600,-1,0,1,23039,23040,23041,28159,28160,28161,65535,65536,65537,105469,105470}


def test_ltft_none_sign_has_executed_factory_underflow_and_bypass_wrap_witnesses():
    rows=literals()
    for bank in (0,1):
        for l,out in ((25599,28160),(25600,23040)):
            assert any(r['raw_r4']&255==bank and r['l']==l and r['a']==0
                       and r['mask']==0 and r['u']==1 and r['v']==0
                       and not evaluate(r)['Z'] and r['output']==out for r in rows)
        for name in ('l','a'):
            other='a' if name=='l' else 'l'
            for value,out in ((256,40191),(32767,7166)):
                assert any(r['raw_r4']&255==bank and r[name]==value and r[other]==65535
                           and r['mask']==3 and not evaluate(r)['Z'] and r['output']==out for r in rows)


@pytest.mark.parametrize('old,new',(('108 instructions','109 instructions'),
    ('268 bound bytes','269 bound bytes'),('12028 literal cases','12029 literal cases')))
def test_ltft_draft_published_count_mutation_is_rejected(old,new):
    text=document('spec')
    assert old in text
    with pytest.raises(AssertionError):publication(text.replace(old,new),actual_counts())


@pytest.mark.parametrize('name',('spec','readme'))
@pytest.mark.parametrize('extra',('109 instructions','269 bound bytes','12029 literal cases',
    '109-instruction envelope','269-byte bound envelope','12029-case matrix','execution repeats 12029 times'))
def test_ltft_extra_conflicting_main_count_claim_is_rejected(name,extra):
    text=document(name);publication(text,actual_counts())
    with pytest.raises(AssertionError):publication(text+'; '+extra,actual_counts())


@pytest.mark.parametrize('name',('spec','readme'))
@pytest.mark.parametrize('extra',('81-byte frame','53 bound data bytes',
    'Each legal bank has 6015 cases','Each incoming T value has 6015 cases',
    '8565 factory-bound','3465 artificial-bound',
    '217 instruction bytes','other 18 closed_loop_fuel step records','81 bytes observer'))
def test_ltft_extra_conflicting_scoped_count_claim_is_rejected(name,extra):
    text=document(name);publication_details(text,name=='spec')
    with pytest.raises(AssertionError):publication_details(text+'; '+extra,name=='spec')


@pytest.mark.parametrize('old,new',(
    ('Each legal bank has 6014 cases.',''),
    ('Each incoming T value has 6014 cases.',''),
    ('Each legal bank has 6014 cases.','Each legal bank has 6015 cases.'),
    ('Each incoming T value has 6014 cases.','Each incoming T value has 6015 cases.'),
))
def test_ltft_separate_marginal_count_labels_are_required(old,new):
    text=document('spec')
    assert text.count(old)==1
    with pytest.raises(AssertionError):publication_details(text.replace(old,new),True)


def test_ltft_ambiguous_joint_count_wording_is_refused():
    text=document('spec')
    old='Each legal bank has 6014 cases. Each incoming T value has 6014 cases.'
    assert old in text
    with pytest.raises(AssertionError):publication(text.replace(
        old,'There are 6014 cases for each legal bank and incoming T value.'),actual_counts())


@pytest.mark.parametrize('index',range(43))
@pytest.mark.parametrize('mutation',('note','extra_via','missing_via','wrong_layout','missing_test','missing_spec'))
def test_ltft_each_prospective_condition_rejects_wrong_path_note_and_proof(index,mutation):
    expected=CONDITIONS[index];link=synthetic_link(expected)
    if mutation=='note':link.props['note']+=' The opposite predicate also applies.'
    elif mutation=='extra_via':link.props['via'].append('bank_base/fn')
    elif mutation=='missing_via':link.props['via']=link.props['via'][1:]
    elif mutation=='wrong_layout':link.stated.add('jk00d')
    elif mutation=='missing_test':link.evidence=link.evidence[1:]
    else:link.evidence=link.evidence[:-1]
    with pytest.raises(AssertionError):exact_condition(None,link,expected)


@pytest.mark.parametrize('owner,kind,target,slot,note',(
    ('ltft_b1/ram','threshold','gay-bloodhound/ram',None,
     'When unsigned U>signed V bypass limiting; equality enables limiting.'),
    ('ltft_b2/ram','threshold','ltft_limit_comparison_word/ram',None,
     'With the selected mask bit clear, unsigned U>signed V enables limiting; equality enables limiting.'),
    ('ltft_b1/ram','selector','logical-swan/ram','bit0',
     'b=0: mask bit0 set enables limiting; clear leaves limiting disabled.'),
    ('ltft_b2/ram','selector','ltft_publication_neutral_control/ram','bit0',
     'After D=0, no neutral publication at 25600 when this bit is set.'),
    ('ltft_b1/ram','selector','origami-iguana/ram','bit0',
     'After D=0 and F=0, either ffff41fa.bit0 or ffff248b.bit1 set selects neutral 25600.'),
    ('ltft_b1/ram','selector','tourmaline-jackal/ram','byte1.bit7',
     'The predicate sentinel arm executes for the natural caller id 0129 and writes neutral 25600.'),
))
def test_ltft_inverse_and_broadened_condition_claims_are_rejected(owner,kind,target,slot,note):
    [expected]=[item for item in CONDITIONS if (item['owner'],item['kind'],item['target'],item['slot'])
                ==(owner,kind,target,slot)]
    link=synthetic_link(expected);link.props['note']=note
    with pytest.raises(AssertionError):exact_condition(None,link,expected)


@pytest.mark.parametrize('expected',[item for item in CONDITIONS if item['kind']=='base'])
def test_ltft_prospective_base_offset_mutation_is_rejected(expected):
    link=synthetic_link(expected);link.offset+=2
    with pytest.raises(AssertionError):exact_condition(None,link,expected)


@pytest.mark.parametrize('field,value',(
    ('rom','JK00D'),('key','other-ltft'),('source','other.s'),('harness','other.c'),
    ('start',0x57b28),('end',0x57b78),('callees',CODE_SPANS[1:][::-1]),
    ('pools',POOLS[:-1]),('ram_literals',ALIASES[:-1]),('cases',12029),('boundary',True),
    ('return_address_offset',4),('return_register',1),('base_load',0x57b26),
    ('symbols',SYMBOLS[::-1]),('symbols',SYMBOLS+(SYMBOLS[0],)),
    ('symbols',(('SELECTED','ltft_b2/ram'),)+SYMBOLS[1:]),
    ('bits',(('EXTRA','logical-swan/ram','bit0'),)),('constants',()),
    ('constants',(('DIAGNOSTIC_BYTE1_OFFSET',2),)),('constants',CONSTANTS+(('EXTRA',1),)),
))
def test_ltft_prospective_region_rejects_every_unreviewed_identity_and_context(field,value):
    region=future_region();exact_region(region)
    with pytest.raises(AssertionError):exact_region(replace(region,**{field:value}))


@pytest.mark.parametrize('index',range(43))
@pytest.mark.parametrize('field,value',(('relies',None),('relies','level'),('supports',None),('supports','structure')))
def test_ltft_typed_claim_levels_are_required(index,field,value):
    expected=CONDITIONS[index];link=synthetic_link(expected);link.props[field]=value
    with pytest.raises(AssertionError):exact_condition(None,link,expected)


@pytest.mark.parametrize('expected',[item for item in CONDITIONS if item['kind']=='writer' or
    (item['kind']=='reader' and item['owner'] in {name for name,_ in EXISTING[:4]})])
@pytest.mark.parametrize('field,value',(('reverse_relies',None),('reverse_relies','level'),
    ('reverse_supports',None),('reverse_supports','structure')))
def test_ltft_held_reverse_claim_levels_are_required(expected,field,value):
    link=synthetic_link(expected);link.props[field]=value
    with pytest.raises(AssertionError):exact_condition(None,link,expected)


@pytest.mark.parametrize('expected',[item for item in CONDITIONS if item['kind']=='reader' and
    item['owner'] in {name for name,_ in EXISTING[:4]}])
def test_ltft_selected_input_indexed_role_is_required(expected):
    link=synthetic_link(expected);link.roles=set()
    with pytest.raises(AssertionError):exact_condition(None,link,expected)


@pytest.mark.parametrize('expected',[item for item in CONDITIONS if item['kind']!='base'])
@pytest.mark.parametrize('offset',(0,1))
def test_ltft_scalar_links_reject_unreviewed_offset(expected,offset):
    link=synthetic_link(expected);link.offset=offset
    with pytest.raises(AssertionError):exact_condition(None,link,expected)


@pytest.mark.parametrize('mutation',('note','via_extra','via_missing','role','offset0','offset1','layout',
    'relies','supports','reverse_relies','reverse_supports','proof0','proof1','proof2','proof3'))
def test_ltft_shared_reference_reader_required_facts_are_not_weakened(mutation):
    link=synthetic_reference_reader();reference_reader_contract(None,link)
    if mutation=='note':link.props['note']=link.props['note'].replace('no complete array extent','complete array extent')
    elif mutation=='via_extra':link.props['via'].append(FN)
    elif mutation=='via_missing':link.props['via']=[]
    elif mutation=='role':link.roles=set()
    elif mutation.startswith('offset'):link.offset=int(mutation[-1])
    elif mutation=='layout':link.stated.add('jk00d')
    elif mutation.startswith('proof'):link.evidence.pop(int(mutation[-1]))
    else:link.props[mutation]='level'
    with pytest.raises(AssertionError):reference_reader_contract(None,link)


@pytest.mark.parametrize('mutation',('note','proof0','proof1','proof2','proof3'))
def test_ltft_shared_reference_symbol_required_note_and_proofs_are_not_weakened(mutation):
    symbol=SimpleNamespace(props={'note':[REF_SYMBOL_NOTE]},evidence=[dict(item) for item in REF_EVIDENCE])
    reference_symbol_contract(symbol)
    if mutation=='note':symbol.props['note']=[]
    else:symbol.evidence.pop(int(mutation[-1]))
    with pytest.raises(AssertionError):reference_symbol_contract(symbol)


@pytest.mark.parametrize('index',range(3))
@pytest.mark.parametrize('mutation',('missing','end','relies','supports'))
def test_ltft_shared_reference_both_ledger_claiming_ends_are_required(index,mutation):
    owner,registry,order,dependency=REF_LEDGER[index]
    name,kind=owner.split('/');changed=dict(dependency)
    if mutation=='missing':dependencies=[]
    else:changed[mutation]='wrong';dependencies=[changed]
    model=SimpleNamespace(stash={'ledger_rows':[(kind,name,[dict(registry=registry,order=order,
                                                               dependency=[dict(dependency)])],None)]})
    ledger_claim(model,owner,registry,order,dependency)
    model.stash['ledger_rows'][0][2][0]['dependency']=dependencies
    with pytest.raises(AssertionError):ledger_claim(model,owner,registry,order,dependency)


def test_ltft_source_full_sr_frame_ram_and_c_abi_contract():
    for name,digest in (
        ('stock_jk08a_ltft_publication.s','4c3f0551f6b21ed42e099f0ff2ff6d169d404488a6ba0a3fece29c0018a07c82'),
        ('stock-jk08a-ltft-publication-cases.h','4cc4051e74ce41ea8bdddf450aa2035f017c2d559477768ad0c578184c53c901'),
        ('stock_ltft_publication_invoke.s','18f63b80bbafbd518e2dcbd3c595b5cb022f70c23dd590c360b1ce47ae8f998a')):
        assert hashlib.sha256((TOOL_DIR/name).read_bytes()).hexdigest()==digest
    c=harness_identity((TOOL_DIR/'harness-stock-jk08a-ltft-publication.c').read_bytes())
    asm=tool_text('stock_ltft_publication_invoke.s')
    for field,offset in (('sp',80),('continuation',84),('abi_before',88),('abi_after',136),
                         ('frame_before',184),('frame_after',264),('sr_before',344)):
        assert f'offsetof(struct observation,{field})=={offset}U' in c
    assert 'sizeof(struct observation)==348U' in c and 'offsetof(struct context,sr)==72U' in c
    for offset,expected in ((44,'context.r[13]'),(40,'context.r[14]'),(36,'out.continuation')):
        assert f'frame_word(out.frame_after,{offset})!={expected}' in c
    for check in ('out.sr_before&1U','(out.sr_before&~1U)|test->expected_t',
        'out.exit[2]!=context.macl','out.exit[3]!=context.mach','out.exit[4]!=context.gbr',
        'out.sp!=out.abi_before[10]-164U','out.exit[1]!=out.continuation',
        'memcmp(out.abi_before,out.abi_after','memcmp(&context,&before',
        'get_word(address)!=test->output','(i<36U || i>=48U)',
        'i<65536U','if(i>=first && i<first+2U)continue;','calibration_before[at]',
        'frame_word(out.frame_before,72)!=out.continuation','i<15U',
        'i<ARRAY_SIZE(ltft_publication_cases)','completed!=LTFT_PUBLICATION_CASE_COUNT','++completed;'):
        assert check in c
    assert f'VQ_SH_ELF_STOCK_CODE status=PASS region={KEY} cases=%lu' in c
    [cal]=re.findall(r'calibrations\[\]\s*=\s*\{(.*?)\n\};',c,re.S)
    assert tuple((int(at,16),int(size)) for at,size in re.findall(r'\{(0x[0-9a-f]+)U,(\d+)\}',cal))==POOLS
    assert '#define DIAGNOSTIC (DIAGNOSTIC_RECORD + DIAGNOSTIC_BYTE1_OFFSET)' in c
    assert not re.search(r'^#define\s+(?:'+'|'.join(name for name,_ in SYMBOLS)+r')\s',c,re.M)
    assert len(re.findall(r'^[ \t]*\.include[ \t]+"stock_ltft_publication_invoke.s"[ \t]*$',tool_text('stock_invoke.s'),re.M))==1
    assert 'stc sr,r0\n    mov #-2,r1\n    and r1,r0\n    or r2,r0\n    ldc r0,sr' in asm
    assert 'add #127,r1\n    add #127,r1\n    add #90,r1\n    mov.l r0,@r1' in asm
    assert 'add #-48,r1\n    mov #20,r0\nL_ltft_publication_frame_before:' in asm
    assert 'add #-80,r1\n    mov #20,r4\nL_ltft_publication_frame_after:' in asm
    assert 'add #112,r15\n    mov.l r0,@-r15' in asm


def test_ltft_publication_chain_owner_contract():
    model=compile.cached(repo.ROOT)
    reference_shared_contract(model)
    owners={name:required_owner(model,name,address) for name,address in EXISTING+NEW}
    for name,address in NEW:
        owner=owners[name];symbol=owner.symbols['7mfk']
        assert set(owner.symbols)=={'7mfk'} and normalized(model,owner.props['block'])=='fuel_closed_loop/block'
        named_proof(symbol.evidence)
        if name.endswith('/tbl'):
            assert tuple(symbol.value(key) for key in ('storage','rows','cols'))==('uint8',1,1)
        else:
            assert symbol.value('width')==(16 if address==0xffff15fe else 8)
            assert symbol.value('signed')==(address==0xffff15fe)
    for name,_ in EXISTING[:6]:
        symbol=owners[name].symbols['7mfk'];assert symbol.value('width')==16
        named_proof(symbol.evidence)
    for name in ('logical-swan/ram','origami-iguana/ram','onyx-jerboa/ram','jovial-buzzard/ram'):
        symbol=owners[name].symbols['7mfk'];assert symbol.value('width')==8
        named_proof(symbol.evidence)
    assert owners['gay-bloodhound/ram'].symbols['7mfk'].value('width')==16
    named_proof(owners['gay-bloodhound/ram'].symbols['7mfk'].evidence)
    for expected in CONDITIONS:
        [link]=[link for link in owners[expected['owner']].links if link.type==expected['kind']
                and link.to.key==expected['target'] and link.slot==expected['slot']]
        exact_condition(model,link,expected)
    ltft_step_contract(model,model.entities[('chain','closed_loop_fuel')].steps)


def test_ltft_publication_registered_stock_contract():
    region=registered_region()
    assert actual_counts()==(108,268,len(literals()))
    for kind in ('spec','readme'):document_contract(document(kind),kind)
    legacy_publication_contract((repo.ROOT/SPEC_PATH).read_text())
    model=compile.cached(repo.ROOT)
    assert tuple((name,required_owner(model,key,dict(EXISTING+NEW)[key]).symbols['7mfk'].key.address)
                 for name,key in region.symbols)==tuple((name,dict(EXISTING+NEW)[key]) for name,key in SYMBOLS)


@pytest.mark.parametrize('regions',((),(future_region(),future_region())))
def test_ltft_missing_or_duplicate_registration_is_a_failure(regions):
    with pytest.raises(AssertionError):registered_region(regions)


@pytest.mark.parametrize('name,address',EXISTING+NEW)
def test_ltft_missing_required_owner_is_a_failure(name,address):
    model=SimpleNamespace(meanings=[SimpleNamespace(key=key) for key,_ in EXISTING+NEW if key!=name])
    with pytest.raises(AssertionError):required_owner(model,name,address)


def test_ltft_missing_required_header_is_a_failure(monkeypatch):
    path=TOOL_DIR/'stock-jk08a-ltft-publication-cases.h'
    monkeypatch.setattr(type(path),'is_file',lambda current:False if current==path else True)
    with pytest.raises(AssertionError):tool_text(path.name)


@pytest.mark.parametrize('kind',('spec','readme'))
@pytest.mark.parametrize('old,new',(
    ('uint32(L+A-25600)','uint16(L+A-25600)'),
    ('uint32(L+A-25600)','uint32(L+A-25601)'),
    ('(U>V)','(U>=V)'),
    ('((M&(b+1))==0)','((M&(b+1))!=0)'),
    ('min(hi,max(lo,raw))','max(hi,min(lo,raw))'),
    ('uint16(limited)','limited'),
    ('diagnostic_byte1.bit7 or F.bit0','diagnostic_byte1.bit7 and F.bit0'),
    ('(G.bit0 and H.bit1)','(G.bit0 or H.bit1)'),
    ('25600 if neutral','25601 if neutral'),
))
def test_ltft_published_arithmetic_rejects_typed_wrap_gate_neutral_and_clamp_changes(kind,old,new):
    text=document(kind);document_contract(text,kind);assert old in text
    with pytest.raises(AssertionError):document_contract(text.replace(old,new),kind)


@pytest.mark.parametrize('kind',('spec','readme'))
@pytest.mark.parametrize('extra',(
    'Unsigned U>V bypasses numerical limiting.',
    'Equality U=V enables numerical limiting.',
    'The uint32 sum is saturated before addition.',
    'Any neutral condition publishes 25601.',
    'The low word is uint16(limited+1).',
    'The caller uses 0129 and executes the sentinel branch.',
))
def test_ltft_published_arithmetic_rejects_added_contradictory_declarations(kind,extra):
    text=document(kind);document_contract(text,kind)
    with pytest.raises(AssertionError):document_contract(text+'\n\n'+extra,kind)


@pytest.mark.parametrize('old,new',((LEGACY_RAW,LEGACY_RAW.replace('uint32(','(')),
    (LEGACY_RAW,LEGACY_RAW.replace('0x6400','0x6401')),
    (LEGACY_DOMAIN,LEGACY_DOMAIN.replace('0..1','0..2')),
    (LEGACY_PUBLICATION,LEGACY_PUBLICATION.replace('uint16(raw_b)','raw_b'))))
def test_ltft_existing_spec_machine_formula_and_low_word_domain_are_required(old,new):
    text=(repo.ROOT/SPEC_PATH).read_text();legacy_publication_contract(text);assert old in text
    with pytest.raises(AssertionError):legacy_publication_contract(text.replace(old,new))


@pytest.mark.parametrize('old,new',((LEGACY_CLAMP,LEGACY_CLAMP.replace('min(max','max(min')),
    (LEGACY_CLAMP,LEGACY_CLAMP.replace('= 90','= 91')),
    (LEGACY_CLAMP,LEGACY_CLAMP.replace('= 110','= 111')),
    (LEGACY_CLAMP,''),(LEGACY_RAW,''),(LEGACY_NEUTRAL,''),
    (LEGACY_NEUTRAL,LEGACY_NEUTRAL.replace('0x0129','0x012d')),
    (LEGACY_NEUTRAL,LEGACY_NEUTRAL.replace('.bit0 set and','.bit0 set or')),
    (LEGACY_NEUTRAL,LEGACY_NEUTRAL.replace('.bit6','.bit5'))))
def test_ltft_existing_spec_clamp_and_all_neutral_declarations_are_required(old,new):
    text=(repo.ROOT/SPEC_PATH).read_text();legacy_publication_contract(text);assert old in text
    with pytest.raises(AssertionError):legacy_publication_contract(text.replace(old,new))


@pytest.mark.parametrize('extra',(LEGACY_RAW,'raw_b = uint16(L+A-25600)',
    'raw_b = max(lo,min(hi,raw_b))','raw_b = uint32(L+A-25601)'))
def test_ltft_existing_spec_rejects_added_raw_assignments(extra):
    text=(repo.ROOT/SPEC_PATH).read_text();legacy_publication_contract(text)
    at=text.index('### Long-term trim publication and neutralization')
    text=text[:at]+text[at:].replace('\n\n','\n\n'+extra+'\n\n',1)
    with pytest.raises(AssertionError):legacy_publication_contract(text)


@pytest.mark.parametrize('index',(0,1))
@pytest.mark.parametrize('mutation',('from','extra_via','to','effect','sign','note'))
def test_ltft_two_publication_views_require_exact_source_route_and_arithmetic(index,mutation):
    steps=[{} for _ in range(19)]
    for at,fields in zip((13,14),STEP_FIELDS):steps[at]=dict(fields,note=FORMULA,sign='none')
    ltft_step_contract(None,steps)
    step=steps[13+index]
    if mutation=='extra_via':step['via']=step['via']+['bank_base/fn']
    elif mutation=='note':step['note']=FORMULA.replace('uint32(L+A-25600)','uint16(L+A-25600)')
    elif mutation=='sign':step['sign']='positive'
    else:step[mutation]='wrong'
    with pytest.raises(AssertionError):ltft_step_contract(None,steps)


def test_ltft_existing_shared_reference_facts_remain_required():
    reference_shared_contract(compile.cached(repo.ROOT))


@pytest.mark.parametrize('kind',('spec','readme'))
@pytest.mark.parametrize('mutation',('remove_arithmetic','duplicate_arithmetic','duplicate_neutral_sentence'))
def test_ltft_published_math_declarations_have_exact_cardinality(kind,mutation):
    text=document(kind);document_contract(text,kind)
    if mutation=='remove_arithmetic':text=text.replace('    raw = uint32(L+A-25600)\n','')
    elif mutation=='duplicate_arithmetic':text+='\n    raw = uint32(L+A-25600)\n'
    else:
        [sentence]=[item for item in DOC_ARITHMETIC_DECLARATIONS[kind] if 'neutral' in item][:1]
        text+='\n\n'+sentence
    with pytest.raises(AssertionError):document_contract(text,kind)


@pytest.mark.parametrize('old,new',(('Every value 0..255','Every value 0..256'),
    ('b=uint8(R4) is\nadmitted only in 0..1','b=uint8(R4) is\nadmitted only in 0..2'),
    ('U at ffff15fc is zero-extended','U at ffff15fc is sign-extended'),
    ('V at ffff15fe is sign-extended','V at ffff15fe is zero-extended'),
    ('requested T=0/1','requested T=0/2'),
    ('(preparedSR&~1)|expectedT','expectedT')))
def test_ltft_published_domain_extensions_and_sr_weakenings_are_refused(old,new):
    text=document('spec');document_contract(text,'spec');assert old in text
    with pytest.raises(AssertionError):document_contract(text.replace(old,new),'spec')


@pytest.mark.parametrize('size',(18,20))
def test_ltft_publication_chain_length_must_match_the19_step_contract(size):
    steps=[{} for _ in range(19)]
    for at,fields in zip((13,14),STEP_FIELDS):steps[at]=dict(fields,note=FORMULA,sign='none')
    ltft_step_contract(None,steps)
    steps=steps[:size] if size<19 else steps+[{}]
    with pytest.raises(AssertionError):ltft_step_contract(None,steps)


@pytest.mark.parametrize('kind',('spec','readme'))
@pytest.mark.parametrize('extra',('12029 dynamic cases','12029 independent cases'))
def test_ltft_qualified_conflicting_case_publications_are_refused(kind,extra):
    text=document(kind);document_contract(text,kind)
    with pytest.raises(AssertionError):document_contract(text+'\n\n'+extra,kind)


def test_ltft_disabled_gpr_comparison_cannot_pass_source_identity():
    contents=(TOOL_DIR/'harness-stock-jk08a-ltft-publication.c').read_bytes()
    harness_identity(contents)
    old=b'reg(&out,i)!=test->expected[i]'
    assert contents.count(old)==1
    changed=contents.replace(old,b'0U && reg(&out,i)!=test->expected[i]')
    assert changed!=contents
    with pytest.raises(AssertionError):harness_identity(changed)
