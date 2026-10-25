"""Input-only legacy base-pulse fields and fixed-other physical alternatives."""

import ast
from pathlib import Path
import re

from kb import bank_pulse_contract as contract

RAM_BASE=0x01000000
RAM_SIZE=65536
INPUT_SOURCE='tools/sh-elf-run/stock-jk08a-bank-base-pulse-cases.h'
FIELDS=('raw_r4','s','l','e','precursor','additive','offset','c0','c1','f1','f2','initial_t','variant')
WORDS=(('s',0x22DC),('l',0x2302),('e',0x2A24),('precursor',0x18C0),('offset',0x2310))
READER_FIELDS=('s','l','e','precursor','offset')


def source_inputs(text):
    matches=re.findall(r'bank_base_cases\[\]\s*=\s*\{(.*?)\n\};',text,re.S)
    if len(matches)!=1:raise ValueError('the bank-pulse input source lacks its one explicit array')
    body=re.sub(r'(?<=[0-9a-fA-F])U\b','',matches[0]).replace('{','[').replace('}',']')
    rows=ast.literal_eval('['+body+']');result=[]
    for row in rows:
        if type(row) is not list or len(row)!=17 or type(row[1]) is not list or len(row[1])!=15:
            raise ValueError('the bank-pulse legacy input row changes its explicit input shape')
        values=row[2:]
        # Expected GPRs, output, final T and group are not capture inputs.
        data=dict(zip(FIELDS,(row[0],*values[:8],*values[9:13])))
        if (any(type(value) is not int for value in data.values()) or not 0<=data['raw_r4']<=0xFFFFFFFF
                or (data['raw_r4']&255) not in (0,1) or not 0<=data['variant']<=255
                or any(not 0<=data[key]<=65535 for key in ('s','l','e','precursor','additive','offset','c0','c1'))
                or any(not 0<=data[key]<=255 for key in ('f1','f2')) or data['initial_t'] not in (0,1)):
            raise ValueError('the bank-pulse legacy input leaves its bounded raw domain')
        result.append(data)
    return result


def cases(declared,image,root=None):
    if root is None:
        from kb import repo
        root=repo.ROOT
    inputs=source_inputs((Path(root)/INPUT_SOURCE).read_text())
    for bank in (0,1):
        seed=dict(raw_r4=0xA5C30000|bank,s=30000,l=30000,e=30000,precursor=32768,
                  additive=100,offset=32768,c0=16384,c1=16385,f1=2,f2=0,initial_t=bank,variant=7)
        for key in READER_FIELDS:
            for value in ((0,32768,65535) if key in ('precursor','offset') else (26000,30000,40000)):
                inputs.append(dict(seed,**{key:value}))
    return tuple(dict(row,index=index,entry=0x4EAD4) for index,row in enumerate(inputs))


def context(declared,case):
    registers=[(0x28765430+index*0x01030507+case['variant']*0x00102040)&0xFFFFFFFF for index in range(15)]
    registers[4]=case['raw_r4']
    return (*registers,0x456789AB,0x13579BDF,0x2468ACE0,case['initial_t'],0xB6C70000)


def memory(case):
    result=bytearray([0xA5])*RAM_SIZE;bank=case['raw_r4']&255
    for key,at in WORDS:
        result[at+bank*2:at+bank*2+2]=case[key].to_bytes(2,'big')
    for key,at in (('additive',0x2436),('c0',0x22E6),('c1',0x22E8)):
        result[at:at+2]=case[key].to_bytes(2,'big')
    return bytes(result)


def calibrations(declared,image,case):
    result={row['address']:image[row['address']:row['address']+row['size']] for row in contract.POOLS}
    for at,original in contract.ALIASES.items():result[at]=(RAM_BASE+(original&65535)).to_bytes(4,'big')
    result[0x893D]=bytes([case['f1']]);result[0x8940]=bytes([case['f2']])
    return result


def require_input(declared,image,case,observed):
    from kb import test_contract
    if (observed['entry']!=case['entry'] or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],calibrations(declared,image,case))
            or not test_contract.exact(observed['calibration_after'],calibrations(declared,image,case))):
        raise ValueError('the bank pulse changes its complete entry, RAM, bank or calibration inputs')
