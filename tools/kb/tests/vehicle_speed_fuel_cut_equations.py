"""Compare raw vehicle-speed arithmetic with independent literal contexts."""
from functools import cache
import re
from kb import repo
from kb.arithmetic import Grammar
from tools.kb.tests import vehicle_speed_fuel_cut_model as model

FORMULA = 'F = uint8(prev); C = RAM8[ffff24a7]; A = F&1; B = (C>>7)&1; G = (C>>5)&1; S = uint8(from); L = ROM8[00008db7]; H = ROM8[00008dc3]; N = min(1,max(0,S-L+1)); V = min(1,max(0,S-H+1)); U = (1-A)*N*(1-B); K = (1-U)*RAM8[ffff24f6]+U*ROM8[00008caf]; Z = 1-min(1,K); E = A*V*B+(1-A)*N; J = uint8((C&127)|(128*E)); D = (1-G)*(A*V+(1-A)*N*Z); to = uint8((F&254)|D)'

@cache
def program(formula):
    assert Grammar(repo.config()).validate(formula) is None
    text = re.sub(r'\b([0-9a-f]{8})\b',r'0x\1',formula)
    text = re.sub(r'\bfrom\b','source',text)
    return compile(text,'vehicle-speed-fuel-cut-equation','exec')

def evaluate(formula,row):
    env = dict(min=min,max=max,uint8=lambda value:int(value)&255,
        int8=lambda value:model.signed(int(value)&255),source=row['speed'],prev=row['flags'],
        RAM8={0xffff24a7:row['control'],0xffff24f6:row['counter']},
        ROM8={0x8db7:model.ACTIVATION,0x8dc3:model.RELEASE,0x8caf:model.DELAY})
    exec(program(formula),{'__builtins__':{}},env)
    return env

def verify(formula):
    checked = 0
    for row in model.matrix():
        result = evaluate(formula,row)
        assert (result['to'],result['J'],result['K'],result['D']) == (
            row['expected_flags'],row['expected_control'],row['expected_counter'],row['result']),checked
        checked += 1
    return checked
