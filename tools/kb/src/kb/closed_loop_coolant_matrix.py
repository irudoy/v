"""Input-only coolant literals and explicit constant-reader alternatives."""

from copy import deepcopy
from pathlib import Path
import re

from kb import closed_loop_coolant_access_contract as contract,test_contract

INPUT_SOURCE='tools/sh-elf-run/coolant-conditional-cases.h'
RAM_BASE=0x01000000
RAM_SIZE=65536
LEGACY_CASES=14261
FIELDS=('rpm','warm','previous_coolant','load','rpm_select','flags_a','flags_b','source_flag',
    'direction_flag','old','mixture','hysteresis','rate','cap','coolant_offset','variant','entry_sr')
ARRAYS=(('thresholds',3),('curve',8),('load_axis',4),('rpm_axis',4),('coefficients',16))
BYTE_INPUTS=(('rpm',0x11B3),('warm',0x1107),('previous_coolant',0x106F),('load',0x102C),
    ('rpm_select',0x11AE),('flags_a',0x2492),('flags_b',0x2493),('source_flag',0x2458),('direction_flag',0x2485))
WORD_INPUTS=(('old',0x15DA),('mixture',0x22E8))
DEFAULTS=dict(rpm=144,warm=150,previous_coolant=240,load=80,rpm_select=72,flags_a=0,
    flags_b=0,source_flag=0,direction_flag=0,old=0,mixture=16384,hysteresis=3,rate=5,
    cap=7799,coolant_offset=0xFF40,variant=0,entry_sr=0,
    thresholds=[144,150,150],curve=[0,0,0,4,7,10,13,16],load_axis=[64,70,82,102],
    rpm_axis=[24,72,80,104],coefficients=[0,0,0,128,0,0,0,128,0,0,128,128,0,128,128,128])


def _unsigned(text):
    if not re.fullmatch(r'(?:0x[0-9a-fA-F]+|[0-9]+)U',text.strip()):
        raise ValueError('the coolant input source changes a typed literal input')
    return int(text.strip()[:-1],0)


def legacy_inputs(root):
    text=(Path(root)/INPUT_SOURCE).read_text()
    structure=re.search(r'struct coolant_conditional_case\s*\{\s*uint32_t\s+([^;]+);(.*?)\};',text,re.S)
    if structure is None:raise ValueError('the coolant input source omits its complete literal input structure')
    names=tuple(name.strip() for name in structure[1].split(','))
    arrays=tuple((name,int(size)) for name,size in re.findall(r'uint32_t\s+(\w+)\[(\d+)\];',structure[2]))
    if names[:17]!=FIELDS or len(names)!=26 or arrays[:5]!=ARRAYS:
        raise ValueError('the coolant input source changes its exact scalar prefix or calibration array fields')
    marker='static const struct coolant_conditional_case coolant_conditional_cases[]={'
    if text.count(marker)!=1:raise ValueError('the coolant input source changes its exact literal array')
    rows=[]
    for line in text.split(marker,1)[1].splitlines():
        line=line.strip()
        if not line:continue
        if line=='};':break
        if not line.startswith('{'):raise ValueError('the coolant input source changes its literal row prefix')
        # Only the first 17 scalar inputs are parsed. The nine following scalar results are skipped.
        prefix=line[1:].split(',',len(FIELDS))[:len(FIELDS)]
        if len(prefix)!=len(FIELDS):raise ValueError('the coolant input source omits a scalar input')
        row=dict(zip(FIELDS,map(_unsigned,prefix)));row['coolant_offset']&=65535
        position=line.find('{',1)
        for name,size in ARRAYS:
            end=line.find('}',position+1)
            if position<0 or end<0:raise ValueError('the coolant input source omits a complete calibration array')
            values=[_unsigned(item) for item in line[position+1:end].split(',')]
            if len(values)!=size or any(not 0<=value<=255 for value in values):
                raise ValueError('the coolant input source changes a complete byte calibration input')
            row[name]=values;position=line.find('{',end+1)
        # Local-result, incoming-register and expected-register arrays are neither parsed nor consumed.
        rows.append(row)
    if len(rows)!=LEGACY_CASES:raise ValueError('the coolant input source changes its complete literal input count')
    return tuple(rows)


def cases(declared,image,*,root):
    result=[]
    def add(kind='controlled',source_index=None,**changes):
        row=deepcopy(DEFAULTS);row.update(deepcopy(changes))
        result.append(dict(index=len(result),kind=kind,source_index=source_index,entry=contract.ENTRY,**row))
    for index,row in enumerate(legacy_inputs(root)):add('legacy',index,**row)
    for value in range(256):
        add(load=0,rpm_select=0,curve=[255]*8,coefficients=[value,*([64]*15)],cap=65535,mixture=0)
    for load_index,load in enumerate((0,71,83,103)):
        for rpm_index,rpm in enumerate((0,73,81,105)):
            selected=4*rpm_index+load_index
            for value in (0,1,64,255):
                coefficients=[64]*16;coefficients[selected]=value
                add(load=load,rpm_select=rpm,coefficients=coefficients,curve=[255]*8,cap=65535,mixture=0)
    for previous in (0,191,192,240,255):
        for offset in (-32768,-32767,-256,-255,-241,-240,-239,-193,-192,-191,-184,-1,0,1,32767):
            add(previous_coolant=previous,coolant_offset=offset&65535,coefficients=[64]*16)
    for variant in (0,1):
        for sr in (0,1,0x301):add(variant=variant,entry_sr=sr,coefficients=[64]*16)
    return tuple(result)


def context(declared,case):
    variant=case['variant']
    if variant not in (0,1):raise ValueError('the coolant input changes its exact complete context variant')
    incoming=tuple(((0x81234567+register*0x1020305) if variant else
        (0x1728394A+register*0x110203))&0xFFFFFFFF for register in range(15))
    return (*incoming,0x01004567 if variant else 0x01003579,0x13579BDF,
        0x9274B6D8 if variant else 0x2468ACE0,case['entry_sr'],0xB6C70000)


def memory(case):
    result=bytearray([0xA5])*RAM_SIZE
    for name,at in BYTE_INPUTS:result[at]=case[name]
    for name,at in WORD_INPUTS:result[at:at+2]=case[name].to_bytes(2,'big')
    return bytes(result)


def calibrations(declared,image,case):
    return {0x87A5:bytes(case['thresholds']),0x86EB:bytes([case['hysteresis']]),
        0x12422:bytes(case['curve']),0x11B1B:bytes(case['load_axis']),0x11B17:bytes(case['rpm_axis']),
        0x990A:bytes(case['coefficients']),0x9090:case['rate'].to_bytes(2,'big'),
        0x929A:case['cap'].to_bytes(2,'big'),0x5533C:case['coolant_offset'].to_bytes(2,'big')}


def require_input(declared,image,case,observed):
    calibration=calibrations(declared,image,case)
    if (observed['entry']!=contract.ENTRY or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],calibration)
            or not test_contract.exact(observed['calibration_after'],calibration)):
        raise ValueError('the coolant original changes an exact complete input, context or controlled calibration')
