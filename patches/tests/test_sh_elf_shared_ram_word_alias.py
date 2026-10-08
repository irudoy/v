"""Retain prior refusals and bind coherent words without changing old fixtures."""
import ast
from dataclasses import asdict,replace
import hashlib
from pathlib import Path
import pytest
from tools.kb.tests import test_injection_start_delay_chain as publication
from patches.tests import test_sh_elf_ram_word_alias as original_contract

here=Path(__file__).resolve().parent

def draft():
    stock=publication.stock_module()
    return stock,stock.__dict__

def test_coherent_shared_pointer_has_one_positive_RAM_window_and_two_pool_bindings():
    stock,api=draft()
    _,old,image=original_contract.inputs()
    row=old.ram_word_literals[0]
    changed=bytearray(image)
    changed[0x1002:0x1004]=bytes.fromhex('84ec')
    region=api['Region'](**asdict(old))
    region=replace(region,ram_word_literals=(row,(0x1002,*row[1:])))
    assert api['ram_word_aliases'](region,changed)==region.ram_word_literals
    expected=bytearray(changed)
    expected[0x1000:0x1004]=bytes.fromhex('7f007f00')
    expected[0x1004:0x1008]=bytes.fromhex('0100128c')
    expected[0x2010:0x2014]=bytes.fromhex('000b0009')
    assert api['build_fixture'](region,changed)==expected

@pytest.mark.parametrize('kind',('pool-repeat','alias-conflict','extent-conflict','wrong-second-word','different-origin'))
def test_shared_mapping_refuses_every_incoherent_or_duplicate_declaration(kind):
    stock,api=draft()
    _,old,image=original_contract.inputs()
    changed=bytearray(image)
    changed[0x1002:0x1004]=bytes.fromhex('84ec')
    row=old.ram_word_literals[0]
    second=(0x1002,*row[1:])
    if kind=='pool-repeat':second=row
    elif kind=='alias-conflict':second=(0x1002,row[1],0x7e00,1)
    elif kind=='extent-conflict':second=(0x1002,row[1],row[2],2)
    elif kind=='wrong-second-word':changed[0x1002:0x1004]=bytes.fromhex('84ed')
    elif kind=='different-origin':
        changed[0x1002:0x1004]=bytes.fromhex('84ed')
        second=(0x1002,0xffff84ed,row[2],1)
    region=replace(api['Region'](**asdict(old)),ram_word_literals=(row,second))
    with pytest.raises(stock.VerificationError):api['build_fixture'](region,changed)

@pytest.mark.parametrize('kind',('list','shape','bool','odd','pool','original','positive-original','negative-alias',
    'signed-alias','extent','origin-end','alias-end','code','boundary','data','duplicate','origin-overlap',
    'alias-overlap','pool-overlap','long-pool','long-origin','io-origin','ram-end'))
def test_every_original_RAM_refusal_remains_strict(monkeypatch,kind):
    stock,api=draft()
    for name in ('Region','ram_word_aliases','register_word_aliases','build_fixture'):
        monkeypatch.setattr(stock,name,api[name],raising=False)
    original_contract.test_word_alias_refuses_unbound_overlapping_or_malformed_intervals(kind)

