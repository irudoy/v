"""Review three fuel-cut consumer equations against accepted stock literals."""
import ast
from collections import Counter
from datetime import datetime,timezone
from fractions import Fraction
from functools import cache
import hashlib,json,math,re,sys,tomllib
from pathlib import Path
from kb import repo
from kb.arithmetic import Grammar

TOOL=repo.ROOT/'tools/sh-elf-run'
sys.path.insert(0,str(TOOL))
import stock_injection_oneshot_model as oneshot
import stock_injection_event_model as event

COUNTER_PREFIX='M = uint32(x[0]); I = uint8(x[1]); E = (RAM8[ffff4184]>>7)&1; S = (M>>I)&1; '
COUNTER_SUFFIX='; D = (1-H)*uint16(x[2])+H*RAM16[ffff23aa]; J = (RAM16[fffff666]>>I)&1; D = max(0,D-J*RAM16[ffff23aa]); C = RAM8[ffff4251]&1; A = (1-C)*min(65535,floor(800*D/256))+1000*C; to = uint16(prev+E*S*A)'
FORMULAS={
    '23':COUNTER_PREFIX+'H = min(1,M&(uint8(from)|RAM8[ffff1935]))'+COUNTER_SUFFIX,
    '24':'M = uint8(RAM8[ffff1936]); F = min(1,uint8(from))*min(1,RAM8[ffff22e0]); R = uint8(uint8(from)-F); H = (uint8(prev)&(255^M))|(F*M); E = (RAM8[ffff4184]>>7)&1; K = E*min(1,M&63)*min(1,M&(RAM8[ffff22e0]|H)); to = H|(K*M)',
    '25':COUNTER_PREFIX+'H = min(1,M&(RAM8[ffff22e0]|uint8(from)))'+COUNTER_SUFFIX,
}

@cache
def program(formula):
    assert Grammar(repo.config()).validate(formula) is None
    text=re.sub(r'\b([0-9a-f]{8})\b',r'0x\1',formula)
    text=re.sub(r'\bfrom\b','source',text)
    class ExactDivision(ast.NodeTransformer):
        def visit_BinOp(self,node):
            node=self.generic_visit(node)
            if isinstance(node.op,ast.Div):
                return ast.copy_location(ast.Call(ast.Name('Fraction',ast.Load()),[node.left,node.right],[]),node)
            return node
    return compile(ast.fix_missing_locations(ExactDivision().visit(ast.parse(text))),'fuel-cut-equation','exec')

def evaluate(formula,**values):
    env=dict(Fraction=Fraction,RAM8={},RAM16={},floor=math.floor,min=min,max=max,
        uint8=lambda n:int(n)&255,uint16=lambda n:int(n)&65535,uint32=lambda n:int(n)&0xffffffff)
    env.update(values);exec(program(formula),{'__builtins__':{}},env)
    return env

def counter_values(row,channel,number):
    return dict(x=[row['argument'],channel,row['durations'][channel]],
        source=row['inhibit'] if number=='23' else row['history'],prev=row['counters'][channel],
        RAM8={0xffff4184:row['enable'],0xffff22e0:row['inhibit'],0xffff1935:row['history'],0xffff4251:row['diagnostic']},
        RAM16={0xffff23aa:row['opening'],0xfffff666:row['started']})

def event_values(row):
    return dict(source=row['release'],prev=row['history'],
        RAM8={0xffff1936:row['selection']['pending'],0xffff22e0:row['selection']['inhibit'],0xffff4184:row['enable']})

def verify_counter(formula,number):
    checked=0
    for row in oneshot.matrix():
        for channel in range(6):
            result=evaluate(formula,**counter_values(row,channel,number))
            assert result['to']==row['output'][channel],(number,checked,row['argument'],channel,result['to'],row['output'][channel])
            checked+=1
    return checked

def verify_event(formula):
    paths=Counter()
    for row in event.matrix():
        result=evaluate(formula,**event_values(row))
        assert result['to']==row['expected_history'] and result['R']==row['expected_release']
        paths[tuple(result[key] for key in ('F','E','K'))]+=1
    return {','.join(map(str,key)):count for key,count in sorted(paths.items())}
