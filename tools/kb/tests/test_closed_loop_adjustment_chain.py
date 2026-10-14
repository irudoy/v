"""Bind both signed adjustment views to the complete natural stock entry."""
import copy
import ast
import hashlib
import json
import re
from unittest import mock

import pytest

from tools.kb.tests import closed_loop_adjustment_contract as contract

def test_adjustment_owner_contract():
    contract.owner_contract()

def test_adjustment_preserves_every_previous_registered_region_and_fixture():
    contract.previous_regions_contract()

def test_registered_adjustment_stock_contract(jk08a_stock_bytes):
    contract.registered_stock_contract(jk08a_stock_bytes)

def test_every_bound_adjustment_byte_refuses_mutation(jk08a_stock_bytes):
    contract.all_bound_mutations_fail(jk08a_stock_bytes)

def test_adjustment_published_counts_follow_registered_region():
    contract.publication_contract()

def test_adjustment_literals_match_independent_raw_state_cpu_and_frame():
    contract.literal_contract()

def test_adjustment_two_formulas_match_both_channels_of_every_literal():
    contract.formula_contract()

@pytest.mark.parametrize('field',list(range(9,17)))
def test_adjustment_rejects_changed_independent_observations(field):
    rows = contract.literals().copy()
    rows[0] = copy.deepcopy(rows[0])
    rows[0][field][-1] ^= 1
    with pytest.raises(AssertionError):
        contract.literal_contract(rows)

def original_numeric_array(body):
    if not re.fullmatch(r'[\s{},0-9a-fxU]+',body):
        raise AssertionError
    body = re.sub(r'(0x[0-9a-f]+|\d+)U\b',r'\1',body)
    return ast.literal_eval('['+body.replace('{','[').replace('}',']')+']')

@pytest.mark.parametrize('body',(
    '0, 1, 65535, 4294967295',
    '0U, 0x00U, 0x80U, 0xffffU, 0xffffffffU,',
    '{0,1,2,},{3,{4,5,},},',
    ' \t\r\n{0x01U,0x2aU},\n{3,4},\n',
    '{{},{0},{0,1}},',
    '00, 000U, {0000,},',
    '\f{1,2},',
    '1e2, 01e2, 1e999,',
    '{'*101+'0'+'}'*101,
    '0x'+'f'*3600,
),ids=('decimal','unsigned-hex','nested-trailing','whitespace','empty-nested',
       'legacy-zero','form-feed','exponent','deep-list','unbounded-hex'))
def test_numeric_array_preserves_original_values(body):
    assert contract.numeric_array(body) == original_numeric_array(body)

def failure(reader,body):
    try:
        reader(body)
    except (AssertionError, ValueError, SyntaxError, RecursionError) as error:
        return (type(error),re.sub(r' at 0x[0-9a-f]+',' at ADDRESS',str(error)),
                getattr(error,'lineno',None),getattr(error,'offset',None),getattr(error,'text',None))
    raise AssertionError('Malformed initializer is accepted')

@pytest.mark.parametrize('body',(
    '-1', '+1', '1+2', '1<<2', '1;2',
    '1,,2', ',1', '{1,', '1}', '{1}{2}',
    '0x', '0Xff', '0x1a0x2', '10x1', '01', '1 2', 'bad',
    '\u00a01', '0x1.U', '1.0', '0x1Ue2',
    '{'*201+'0'+'}'*201,
    '9'*4500, ',', '{,}', '{1,,}', '{1,{,}}',
),ids=('negative','positive','addition','shift','statement','double-comma',
       'leading-comma','missing-close','extra-close','adjacent-lists',
       'missing-hex','upper-hex','adjacent-hex','invalid-hex-prefix','leading-zero',
       'adjacent-decimal','name','non-ascii-space','hex-dot','decimal-point',
       'suffix-adjacency','nesting-limit','decimal-digit-limit','only-comma',
       'empty-with-comma','trailing-double-comma','nested-empty-with-comma'))
def test_numeric_array_preserves_original_refusals(body):
    assert failure(contract.numeric_array,body) == failure(original_numeric_array,body)

def test_numeric_array_canonical_lists_use_no_python_ast():
    with mock.patch.object(contract.ast,'literal_eval',side_effect=AssertionError('Python AST is invoked')):
        assert contract.numeric_array('{0U,0x80U,65535U,},{1U,{2U,},},') == [[0,128,65535],[1,[2]]]

def test_numeric_array_reproduces_every_registered_stock_literal():
    rows = contract.literals()
    assert len(rows) == 10286
    assert hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest() == (
        '9ff0684e367bc388c06a2b35d481e5a276d7668eaf468e3ebf4390d4c465d4e6')
