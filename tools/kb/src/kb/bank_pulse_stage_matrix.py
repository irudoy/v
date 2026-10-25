"""Explicit precursor/channel input prefixes and bounded physical alternatives."""

import ast
from pathlib import Path
import re

from kb import bank_pulse_stage_contract as contract

RAM_BASE=0x01000000
RAM_SIZE=65536
KINDS=('precursor','channel')
INPUT_SOURCES=('tools/sh-elf-run/pulse-precursor-cases.h','tools/sh-elf-run/channel-pulse-cases.h')
PREFIX_INPUTS=16
PRECURSOR_FIELDS=('source_flags','cap_flags','output_flags','bfs','alternate_bfs','speed','cap_floor',
    'multiplier','transient_raw','gain','bank0','bank1','cap_numerator','pulse_floor')
CHANNEL_FIELDS=('channel','argument','mask','even_base','odd_base','additive','subtractive',
    'flag','multiplier','opening','a','c','b','d','variant','entry_t')
FIELDS=('entry','raw_r4',*PRECURSOR_FIELDS,'channel','mask','even_base','odd_base','additive','subtractive',
    'flag','opening','a','c','b','d','variant','entry_sr')
BYTE_INPUTS=(('source_flags',0x245D),('cap_flags',0x24D2),('output_flags',0x24A1))
WORD_INPUTS=(('bfs',0x1024),('alternate_bfs',0x123E),('speed',0x11BC),('cap_floor',0x34F6),
    ('multiplier',0x22E6),('transient_raw',0x2300),('gain',0x165E),('bank0',0x40B6),('bank1',0x40B8))


def source_prefix(text,array):
    start=re.search(re.escape(array)+r'\[\]\s*=\s*\{',text)
    if start is None:raise ValueError('a bank-pulse stage input source lacks its explicit array')
    selected=[]
    for line in text[start.end():].splitlines():
        line=line.strip()
        if not line:continue
        if line.startswith('};'):break
        raw=re.sub(r'(?<=[0-9a-fA-F])U\b','',line.rstrip(',')).replace('{','[').replace('}',']')
        selected.append(ast.literal_eval(raw))
        if len(selected)==PREFIX_INPUTS:break
    if len(selected)!=PREFIX_INPUTS:raise ValueError('a bank-pulse stage lacks its exact declared input prefix')
    return selected


def inputs(root):
    result=[]
    for row in source_prefix((Path(root)/INPUT_SOURCES[0]).read_text(),'pulse_precursor_cases'):
        if type(row) is not list or len(row)!=25:
            raise ValueError('a precursor literal row changes its declared input shape')
        result.append(dict(zip((*PRECURSOR_FIELDS,'variant','entry_sr'),row[:16]),kind='precursor'))
    for row in source_prefix((Path(root)/INPUT_SOURCES[1]).read_text(),'channel_pulse_cases'):
        if type(row) is not list or len(row)!=26:
            raise ValueError('a channel literal row changes its declared input shape')
        value=dict(zip(CHANNEL_FIELDS,row[:16]));argument=value.pop('argument');sr=value.pop('entry_t')
        result.append(dict(value,kind='channel',raw_r4=argument,entry_sr=sr))
    return result


def cases(declared,image,root=None):
    if root is None:
        from kb import repo
        root=repo.ROOT
    rows=inputs(root)
    precursor=dict(rows[0],variant=0,entry_sr=0)
    for value in (0,1,255,256,25600,65535):rows.append(dict(precursor,bank1=value))
    for source in (0,32):
        for enabled in (0,1):
            for speed in (0,1,255,256,65535):
                for floor in (0,1024,65535):
                    for numerator in (0,1,65535,0xFFFFFFFF):
                        rows.append(dict(precursor,source_flags=source,cap_flags=enabled,speed=speed,
                            cap_floor=floor,cap_numerator=numerator))
    for gain in (0,1,16383,16384,32768,65535):
        for transient in (0,32767,32768,65535):
            for floor in (0,170,65535):
                rows.append(dict(precursor,gain=gain,transient_raw=transient,pulse_floor=floor))
    channel=next(row for row in rows if row['kind']=='channel')
    vectors=((0,0,0,0,0,0),(1,65535,32767,32768,255,1),
        (65535,65535,32767,32768,255,65535),(0,1,32768,32767,128,0))
    for index in range(6):
        for inhibited in (0,1):
            for flag in (0,8):
                for a,c in ((0,0),(13528,16384),(65535,65535),(65535,0),(0,65535)):
                    for even,odd,additive,subtractive,multiplier,opening in vectors:
                        rows.append(dict(channel,channel=index,raw_r4=0xFFFFFF00|index,mask=(1<<index) if inhibited else 0,
                            flag=flag,a=a,c=c,b=65535,d=65535,even_base=even,odd_base=odd,
                            additive=additive,subtractive=subtractive,multiplier=multiplier,opening=opening,
                            variant=1,entry_sr=1))
    result=[]
    for row in rows:
        kind=row['kind'];value={key:row.get(key,0) for key in FIELDS}
        if any(type(item) is not int or not 0<=item<=0xFFFFFFFF for item in value.values()):
            raise ValueError('a stage input leaves the explicit unsigned word container')
        if value['variant'] not in (0,1) or value['entry_sr']&~0x3F1:
            raise ValueError('a stage input changes its explicit context variant or SR premise')
        if kind=='precursor' and (any(value[key]>255 for key,at in BYTE_INPUTS)
                or any(value[key]>65535 for key,at in WORD_INPUTS) or value['pulse_floor']>65535):
            raise ValueError('a precursor input leaves its declared byte or word domain')
        if kind=='channel' and (value['channel'] not in range(6) or value['raw_r4']&255!=value['channel']):
            raise ValueError('a channel input changes its bounded index and complete R4 premise')
        if kind=='channel' and (any(value[key]>255 for key in ('mask','flag','multiplier'))
                or any(value[key]>65535 for key in ('even_base','odd_base','additive','subtractive','opening','a','c','b','d'))):
            raise ValueError('a channel input leaves its declared byte or word domain')
        result.append(dict(value,kind=kind,index=len(result),entry=contract.ENTRIES[KINDS.index(kind)]))
    return tuple(result)


def context(declared,case):
    variant=case['variant']
    registers=[((0x1728394A+index*0x110203) if variant==0 else (0x81234567+index*0x1020305))&0xFFFFFFFF
               for index in range(15)]
    if case['kind']=='channel':registers[4]=case['raw_r4']
    return (*registers,0x12344321,0x13579BDF,0x2468ACE0,case['entry_sr'],0xB6C70000)


def memory(case):
    result=bytearray([0xA5])*RAM_SIZE
    def word(at,value):result[at:at+2]=(value&65535).to_bytes(2,'big')
    if case['kind']=='precursor':
        for key,at in BYTE_INPUTS:result[at]=case[key]
        for key,at in WORD_INPUTS:word(at,case[key])
    else:
        index=case['channel'];result[0x22E0]=case['mask']
        for at,key in ((0x191C,'even_base'),(0x191E,'odd_base'),(0x2436,'opening'),
            (0x1396+index*2,'additive'),(0x1466+index*2,'subtractive')):word(at,case[key])
    return bytes(result)


def calibrations(declared,image,case):
    values={row['address']:bytearray(image[row['address']:row['address']+row['size']]) for row in contract.POOLS}
    def put(at,data):
        for start,value in values.items():
            if start<=at and at+len(data)<=start+len(value):
                value[at-start:at-start+len(data)]=data;return
        raise ValueError('a bank-pulse calibration input leaves its exact declared span')
    for at,original in contract.ALIASES.items():put(at,(RAM_BASE+(original&65535)).to_bytes(4,'big'))
    if case['kind']=='precursor':
        put(0x96E0,case['cap_numerator'].to_bytes(4,'big'));put(0x94E8,case['pulse_floor'].to_bytes(2,'big'))
    else:
        put(0x8D92,bytes([case['flag']]));put(0x129C0+case['channel'],bytes([case['multiplier']]))
        for at,key in ((0x91DA,'a'),(0x91DC,'c'),(0x91DE,'b'),(0x91E0,'d')):put(at,case[key].to_bytes(2,'big'))
    return {at:bytes(value) for at,value in values.items()}


def calibration_spans(declared):
    return tuple((row['address'],row['size']) for row in contract.POOLS)


def require_input(declared,image,case,observed):
    from kb import test_contract
    if (observed['entry']!=case['entry'] or not test_contract.exact(observed['context'],context(declared,case))
            or observed['sr_before']&0x3F1!=case['entry_sr']
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],calibrations(declared,image,case))
            or not test_contract.exact(observed['calibration_after'],calibrations(declared,image,case))):
        raise ValueError('a bank-pulse stage changes its complete RAM/context or calibration inputs')
