"""Input-only legacy feedback contexts and explicit argument/store alternatives."""

import ast
from pathlib import Path
import re

from kb import closed_loop_feedback_access_contract as contract,test_contract

INPUT_SOURCE='tools/sh-elf-run/stock-jk08a-closed-loop-feedback-cases.h'
RAM_BASE=0x01000000
RAM_SIZE=65536
LEGACY_CASES=1829
PROFILES=('stock','argument-contrast','argument-reverse')


def _body(text,name):
    matches=re.findall(r'\b'+name+r'\[\]\s*=\s*\{(.*?)\};',text,re.S)
    if len(matches)!=1:raise ValueError('the feedback input source omits or repeats a literal input array')
    return matches[0]


def legacy_inputs(root):
    text=(Path(root)/INPUT_SOURCE).read_text()
    body=_body(text,'inputs')
    if not re.fullmatch(r'[\s{},0-9a-fxU]+',body):
        raise ValueError('the feedback input source contains nonliteral byte changes')
    values=ast.literal_eval('['+re.sub(r'(0x[0-9a-f]+|\d+)U\b',r'\1',body).replace('{','[').replace('}',']')+']')
    # Only the first three input columns are read; output ranges and workspace expectations are discarded.
    samples=_body(text,'memory_samples').strip().splitlines()
    rows=[]
    for line in samples:
        match=re.match(r'^\{([01])U,(\d+)U,(\d+)U,',line.strip())
        if match is None:raise ValueError('the feedback input source changes its literal input prefix')
        zero,begin,count=map(int,match.groups());changes=values[begin:begin+count]
        if (len(changes)!=count or changes!=sorted(changes) or len({row[0] for row in changes})!=count
                or any(type(row) is not list or len(row)!=2 or type(row[0]) is not int or type(row[1]) is not int
                    or not 0<=row[0]<RAM_SIZE or not 0<=row[1]<=255 for row in changes)):
            raise ValueError('the feedback input source changes complete sorted byte changes')
        rows.append(dict(zero=zero,changes=changes))
    if len(rows)!=LEGACY_CASES:raise ValueError('the feedback input source changes its complete original context count')
    return rows


def cases(declared,image,*,root):
    result=[]
    for index,row in enumerate(legacy_inputs(root)):
        result.append(dict(index=index,kind='legacy',entry=contract.ENTRY,source_index=index,
            seed_index=index,context_index=index,profile='stock',**row))
    baseline={0x88EC:0xF0,0x88D0:0,0x88D1:0,0x88D2:0,0x88D3:1,
        0x88D8:0,0x88D9:0,0x88DA:0,0x88DB:1,0x88BC:0,0x88BD:3,
        0x88C2:1,0x88CE:0,0x88F4:0x0B,0x88F5:0xB8,0x106E:40,
        0x1071:60,0x11BC:0,0x11BD:3,0x10C8:3}
    def add(profile='argument-contrast',**changes):
        inputs=dict(baseline)
        for address,value in changes.items():inputs[int(address)]=value
        result.append(dict(index=len(result),kind='controlled',entry=contract.ENTRY,source_index=None,
            seed_index=0,context_index=0,profile=profile,zero=1,
            changes=[[at,value] for at,value in sorted(inputs.items())]))
    for value in range(256):add(**{str(0x106E):value})
    for value in range(256):add(profile='argument-reverse',**{str(0x106E):value})
    for value in range(256):add(**{str(0x1071):value})
    for value in (0,1,2,3,4,255,256,32767,32768,65535):
        add(**{str(0x11BC):value>>8,str(0x11BD):value&255})
    for value in range(256):add(**{str(0x10C8):value})
    for incoming in (0,1,0x20,0x40,0x80,0xA0,0xF0,0xFF):add(**{str(0x88EC):incoming})
    for source in (0,0x40):
        for previous in (0,1,255):
            for rpm in (0,2,3):
                for previous_word in (0,3):
                    add(**{str(0x4184):source,str(0x88CE):previous,str(0x11BC):0,
                        str(0x11BD):rpm,str(0x88BC):0,str(0x88BD):previous_word})
    for flag in (0,1,127,128,255):add(**{str(0x88C2):flag})
    for count in (0,1,2551,2552,2553,65534,65535):
        add(**{str(0x88F4):count>>8,str(0x88F5):count&255})
    for offset in (0x88D3,0x88DB,0x88DF,0x88E3):
        for value in (0,1):add(**{str(offset):value})
    threshold=image[0x8822]*image[0x23752]
    lower=(5000-int.from_bytes(image[0x92EE:0x92F0],'big'))&65535
    upper=(5000+int.from_bytes(image[0x92F0:0x92F2],'big'))&65535
    for count in sorted({0,1,max(0,threshold-1),threshold,threshold+1,65534,65535}):
        for flag in (0,1):
            for observed in sorted({0,(lower-1)&65535,lower,5000,upper,(upper+1)&65535,20000,65535}):
                add(profile='stock',**{str(0x88BA):count>>8,str(0x88BB):count&255,str(0x88C1):flag,
                    str(0x11BC):0,str(0x11BD):0,str(0x28BA):0x13,str(0x28BB):0x88,
                    str(0x29E4):observed>>8,str(0x29E5):observed&255})
    for control,previous_control,current_b2,previous_b2,current_b1,previous_b1 in (
            (0,0,0,0,0,0),(1,1,0,0,0,0),(0,1,0,0,0,0),
            (0,0,0x4000,0x4001,0,0),(0,0,0x4000,0x4000,0,0),
            (0,0,0x4000,0,0,0),(0,0,0,0,1,0),(0,0,0,0,0,1)):
        add(profile='stock',**{str(0x88BA):0,str(0x88BB):0,str(0x88C1):0,
            str(0x11BC):0,str(0x11BD):0,str(0x28BA):0x13,str(0x28BB):0x88,
            str(0x29E4):0,str(0x29E5):0,str(0x14C1):control,str(0x88CD):previous_control,
            str(0x22E8):current_b2>>8,str(0x22E9):current_b2&255,
            str(0x88B4):previous_b2>>8,str(0x88B5):previous_b2&255,
            str(0x15DA):current_b1>>8,str(0x15DB):current_b1&255,
            str(0x88B6):previous_b1>>8,str(0x88B7):previous_b1&255})
    return tuple(result)


def context(declared,case):
    index=case['context_index']
    registers=tuple((0x28765430+0x01030507*register+0x12345*index)&0xFFFFFFFF for register in range(15))
    return (*registers,0x456789AB^index,0x13579BDF^index,0x2468ACE0^index,
        ((index&3)<<8)|((index>>2)&1))


def memory(case):
    index=case['seed_index']
    data=bytearray(RAM_SIZE) if case['zero'] else bytearray((0x51+29*i+(i>>8)+index)&255 for i in range(RAM_SIZE))
    for at,value in case['changes']:data[at]=value
    return bytes(data)


def workspace(case):
    index=case['seed_index'];data=bytearray((0x91+13*i+index)&255 for i in range(366))
    before=memory(case);data[32:334]=before[0x88B0:0x89DE]
    return bytes(data)


def calibrations(declared,image,case):
    result={row['address']:image[row['address']:row['address']+row['size']] for row in contract.CONTROLLED_CALIBRATION}
    if case['profile']=='argument-contrast':
        result[0x12312]=bytes(index*16 for index in range(16))
        result[0x8392]=b'\0';result[0x8CD4]=b'\xff'
    elif case['profile']=='argument-reverse':
        result[0x12312]=bytes(240-index*16 for index in range(16))
        result[0x8392]=b'\0';result[0x8CD4]=b'\xff'
    elif case['profile']!='stock':raise ValueError('the feedback input changes its exact calibration profile')
    return result


def logical_ram(ordinary,native):
    if type(ordinary) is not bytes or len(ordinary)!=RAM_SIZE or type(native) is not bytes or len(native)!=366:
        raise ValueError('the feedback source needs complete ordinary RAM and exact native workspace/canaries')
    result=bytearray(ordinary);result[0x88B0:0x89DE]=native[32:334]
    return bytes(result)


def require_input(declared,image,case,observed):
    if (observed['entry']!=contract.ENTRY or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(memory(case),) or observed['workspace_before']!=workspace(case)
            or not test_contract.exact(observed['calibration_before'],calibrations(declared,image,case))
            or not test_contract.exact(observed['calibration_after'],calibrations(declared,image,case))):
        raise ValueError('the feedback original changes an exact input-only context, byte change, native workspace or calibration')
