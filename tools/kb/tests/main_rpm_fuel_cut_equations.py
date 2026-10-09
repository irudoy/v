"""Compare two raw RPM arithmetic views with independent exact-stock contexts."""
from datetime import datetime, timezone
from functools import cache
import re
from kb import repo
from kb.arithmetic import Grammar

from tools.kb.tests import main_rpm_fuel_cut_model as model
PREFIX = 'F = uint8(prev); A = (F>>2)&1; B = (F>>1)&1; '
SUFFIX = '; G = 1-min(1,max(0,Q-R)); Z = 1-min(1,B*RAM8[ffff24f1]+(1-B)*ROM8[00008c69]); C = G*(1-A+A*B); D = G*(A+(1-A)*Z); U = (1-A)*G*(1-B); K = (1-U)*RAM8[ffff24f1]+U*ROM8[00008c69]; to = uint8((F&249)|(2*C)|(4*D))'
FORMULAS = {
    '11': PREFIX + 'P = (RAM8[ffff2468]>>4)&1; Q = (1-A)*uint16(from[P])+A*uint16(from[2+P]); R = uint16(x)' + SUFFIX,
    '12': PREFIX + 'P = (RAM8[ffff2468]>>4)&1; Q = (1-A)*ROM16[0000934e+2*P]+A*ROM16[00009352+2*P]; R = uint16(from)' + SUFFIX,
}

@cache
def program(formula):
    assert Grammar(repo.config()).validate(formula) is None
    text = re.sub(r'\b([0-9a-f]{8})\b', r'0x\1', formula)
    text = re.sub(r'\bfrom\b', 'source', text)
    return compile(text, 'main-rpm-equation', 'exec')

def evaluate(formula, number, row):
    env = dict(min=min, max=max, uint8=lambda value:int(value)&255,
        uint16=lambda value:int(value)&65535, int16=lambda value:model.signed(int(value)&65535,16),
        source=[612,596,596,368] if number=='11' else row['speed'], x=row['speed'], prev=row['flags'],
        RAM8={0xffff24f1:row['counter'],0xffff2468:row['selector']},
        ROM8={0x8c69:model.DELAY}, ROM16={0x934e:612,0x9350:596,0x9352:596,0x9354:368})
    exec(program(formula), {'__builtins__':{}}, env)
    return env

def verify(formula, number):
    checked = 0
    for row in model.matrix():
        result = evaluate(formula, number, row)
        assert (result['to'],result['K']) == (row['expected_flags'],row['expected_counter']), (number,checked)
        checked += 1
    return checked
