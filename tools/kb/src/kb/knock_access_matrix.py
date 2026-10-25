"""Explicit inputs for four separate stock knock software stages.

Legacy rows contribute input columns only. No expected value, register, frame,
instruction interpreter or arithmetic acceptance enumerator supplies an input.
"""

import ast
from pathlib import Path
import re

from kb import knock_access_unit_contract as contract, test_contract

RAM_BASE=0x01000000
RAM_SIZE=65536
KINDS=contract.KINDS
INPUT_SOURCES=tuple('tools/sh-elf-run/stock-jk08a-knock-'+kind+'-cases.h' for kind in KINDS)
PREFIX_INPUTS=16
FIELDS=('entry','scope','channel','selector','other','blocks','flag','multiplier','mask','count',
    'speed','event_count','status','bitmap','biased_input','axis_first','table_first','table_second',
    'table_override','axis_override','variant','entry_sr','sum_input')
ARRAYS=(('bins',8),('sample',8),('reference',8),('gain',3))


def source_prefix(text,array):
    start=re.search(re.escape(array)+r'\[\]\s*=\s*\{',text)
    if start is None:raise ValueError('a knock input source lacks its explicit array')
    rows=[]
    for line in text[start.end():].splitlines():
        line=line.strip()
        if not line:continue
        if line.startswith('};'):break
        raw=re.sub(r'(?<=[0-9a-fA-F])U\b','',line.rstrip(',')).replace('{','[').replace('}',']')
        rows.append(ast.literal_eval(raw))
        if len(rows)==PREFIX_INPUTS:break
    if len(rows)!=PREFIX_INPUTS:raise ValueError('a knock source changes its exact input prefix')
    return rows


def inputs(root,kind):
    path=INPUT_SOURCES[KINDS.index(kind)]
    array={'normalization':'normalization_cases','metric':'metric_cases',
        'threshold':'accessor_cases','comparison':'comparison_cases'}[kind]
    result=[]
    for row in source_prefix((Path(root)/path).read_text(),array):
        if kind=='normalization':
            if type(row) is not list or len(row)!=16:raise ValueError('a normalization literal changes shape')
            mode,channel,selector,blocks,flag,other,sr,multiplier,bins=row[:9]
            if mode!=bool(selector&8):raise ValueError('a normalization input substitutes its selected entry')
            value=dict(channel=channel,selector=selector,blocks=blocks,flag=flag,other=other,
                entry_sr=sr,multiplier=multiplier,bins=bins)
        elif kind=='metric':
            if type(row) is not list or len(row)!=15 or row[0]!=0:
                raise ValueError('a metric prefix changes its explicit composite input domain')
            scope,channel,selector,mask,count,gain,sample,reference=row[:8]
            value=dict(scope=scope,channel=channel,selector=selector,mask=mask,count=count,
                gain=gain,sample=sample,reference=reference)
        else:
            size=6 if kind=='threshold' else 14
            if type(row) is not list or len(row)!=size:raise ValueError('a lookup literal changes shape')
            speed,selector,primary,alternate=row[:4]
            value=dict(speed=speed,selector=selector,channel=alternate if selector&8 else primary,
                other=primary if selector&8 else alternate)
            if kind=='comparison':
                value.update(dict(zip(('event_count','status','bitmap','biased_input'),row[4:8])))
        result.append(value)
    return result


def cases(declared,image,root=None):
    if root is None:
        from kb import repo
        root=repo.ROOT
    if len(declared['unit'])!=1:raise ValueError('knock input matrices require separate stage fixtures')
    unit=declared['unit'][0];kind=unit['id'];rows=inputs(root,kind)
    base=dict(channel=1,other=6,selector=0x82,variant=0,entry_sr=0)
    if kind=='normalization':
        vectors=((0,0,(0,1,255,256,257,32767,32768,65535)),
            (1,32,(0,1,255,256,257,8191,8192,8193)),
            (1,64,(32767,32768,32769,0,65535,1,255,256)),
            (255,65535,(65535,32768,256,255,1,0,8192,8193)))
        for channel in range(1,7):
            for selector in (0x82,0x8A):
                for blocks,multiplier,bins in vectors:
                    for flag in (0,1):
                        for variant in (0,1):
                            rows.append(dict(base,channel=channel,selector=selector,blocks=blocks,
                                multiplier=multiplier,bins=list(bins),flag=flag,variant=variant,entry_sr=variant))
        # Fixed first slot, caller context and calibration alternatives for the cache writer.
        for value in (255,256,257):
            rows.append(dict(base,blocks=1,multiplier=32,flag=0,bins=[value]+[0]*7))
    elif kind=='metric':
        vectors=(([0]*8,[0]*8),([0,1,255,256,257,32767,32768,65535],[65535]*8),
            ([65535]*8,[0,1,255,256,257,32767,32768,65535]),
            ([40,10,80,20,70,30,60,50],[32]*8))
        for channel in range(1,7):
            for selector in (0x82,0x8A):
                for mask in (0,1,0xAA,255):
                    for count in (0,1,3,8):
                        for sample,reference in vectors:
                            rows.append(dict(base,channel=channel,selector=selector,mask=mask,count=count,
                                sample=sample,reference=reference,gain=[128]*3))
        for selector in (0x82,0x8A):
            for gain in ([0,128,128],[128]*3,[255]*3):
                for total in (0,1,0x7FFFFFFF,0x80000000,0xFFFFFFFF):
                    rows.append(dict(base,selector=selector,scope=2,gain=gain,sum_input=total))
            for value in (0,1,65535):
                rows.append(dict(base,selector=selector,mask=0,count=3,gain=[128]*3,
                    sample=[value]+[0]*7,reference=[0]*8))
    else:
        for channel in range(1,7):
            for selector in (0x82,0x8A):
                for speed in (0,31,32,33,63,64,65,480,511,512,513,65535):
                    if kind=='threshold':rows.append(dict(base,channel=channel,selector=selector,speed=speed))
                    else:
                        for metric in (0,0x80000000,0x800003E8,0x800003E9,0xFFFFFFFF):
                            for count in (0,254,255):
                                rows.append(dict(base,channel=channel,selector=selector,speed=speed,
                                    event_count=count,status=0x95,bitmap=0xA5,biased_input=metric))
        # Positive table and axis inputs hold every other datum, register and calibration fixed.
        for first in (1000,1500):
            rows.append(dict(base,speed=33,table_override=1,table_first=first,table_second=2000,
                biased_input=0x80000500,event_count=254,status=0x95,bitmap=0xA5))
        for axis in (32,34):
            rows.append(dict(base,speed=33,table_override=1,table_first=1000,table_second=2000,
                axis_override=1,axis_first=axis,biased_input=0x80000500,event_count=254,status=0x95,bitmap=0xA5))
        if kind=='comparison':
            for metric in (0x800003E7,0x800003E8,0x800003E9):
                rows.append(dict(base,speed=32,table_override=1,table_first=1000,table_second=2000,
                    biased_input=metric,event_count=254,status=0x95,bitmap=0xA5))
    result=[]
    for original in rows:
        value={key:original.get(key,base.get(key,0)) for key in FIELDS}
        value.update({name:list(original.get(name,[0]*size)) for name,size in ARRAYS})
        if any(type(value[key]) is not int or not 0<=value[key]<=0xFFFFFFFF for key in FIELDS):
            raise ValueError('a knock input leaves its explicit uint32 container')
        if value['channel'] not in range(1,7) or value['selector'] not in (0x82,0x8A):
            raise ValueError('a knock input changes the bounded selected channel or selector')
        if value['variant'] not in (0,1) or value['entry_sr'] not in (0,1):
            raise ValueError('a knock input changes its explicit prepared context premise')
        if any(value[key]>255 for key in ('other','blocks','flag','mask','event_count','status','bitmap')):
            raise ValueError('a knock input leaves its declared byte domain')
        if any(value[key]>65535 for key in ('multiplier','speed','axis_first','table_first','table_second')):
            raise ValueError('a knock input leaves its declared word domain')
        if value['count'] not in range(9) or value['scope'] not in (0,2):
            raise ValueError('a knock metric changes its bounded count or admitted entry domain')
        for name,size in ARRAYS:
            limit=255 if name=='gain' else 65535
            if len(value[name])!=size or any(type(item) is not int or not 0<=item<=limit for item in value[name]):
                raise ValueError('a knock input changes its explicit byte/word vector')
        if value['table_override'] not in (0,1) or value['axis_override'] not in (0,1):
            raise ValueError('a knock input changes its explicit artificial calibration domain')
        entry=unit['entry']
        if kind=='normalization' and value['selector']&8:entry=0x4A3B0
        if kind=='metric' and value['scope']==2:entry=0x49E96
        value.update(kind=kind,index=len(result),entry=entry)
        result.append(value)
    return tuple(result)


def context(declared,case):
    variant=case['variant']
    registers=[((0x28765430+index*0x01030507) if not variant else
                (0x81234567+index*0x01020305))&0xFFFFFFFF for index in range(15)]
    registers[7]=case['entry']
    if case['kind'] in ('normalization','metric'):
        registers[11]=8 if case['selector']&8 else 0
    if case['kind']=='normalization':
        if case['selector']&8:registers[14]=case['channel']
        else:registers[5]=case['channel']
    fifth=RAM_BASE+0x20C2 if case['kind']=='metric' and case['scope']==0 else 0xB6C70000
    return (*registers,0x456789AB,0x13579BDF,0x2468ACE0,case['entry_sr'],fifth)


def memory(case):
    result=bytearray([0xA5])*RAM_SIZE
    def word(at,value):result[at:at+2]=value.to_bytes(2,'big')
    def longword(at,value):result[at:at+4]=value.to_bytes(4,'big')
    channel=case['channel'];alternate=bool(case['selector']&8)
    result[0x11DE]=case['other'] if alternate else channel
    result[0x2143]=channel if alternate else case['other']
    if case['kind']=='normalization':
        result[0x2154]=case['blocks'];result[0x87E1]=case['flag'];word(0x2152,case['multiplier'])
        for index,value in enumerate(case['bins']):word(0x2132+2*index,value)
    elif case['kind']=='metric':
        for index,value in enumerate(case['sample']):word(0x20C2+2*index,value)
        for index,value in enumerate(case['reference']):word(0x2178+16*(channel-1)+2*index,value)
        longword(0x2274+4*(channel-1),case['sum_input'])
    else:
        word(0x11F4,case['speed'])
        if case['kind']=='comparison':
            longword(0x21D8+4*(channel-1),case['biased_input'])
            result[0x2142]=case['event_count'];result[0x24C2]=case['status'];result[0x2150]=case['bitmap']
    return bytes(result)


def calibration_spans(declared):
    if len(declared['unit'])!=1:raise ValueError('knock calibrations require one exact stage')
    return tuple((row['address'],row['size']) for row in declared['unit'][0]['pools'])


def calibrations(declared,image,case):
    unit=declared['unit'][0]
    values={at:bytearray(image[at:at+size]) for at,size in calibration_spans(declared)}
    def put(at,data):
        for start,raw in values.items():
            if start<=at and at+len(data)<=start+len(raw):
                raw[at-start:at-start+len(data)]=data;return
        raise ValueError('a knock calibration input leaves its exact declared span')
    for row in unit['aliases']:
        put(row['address'],(RAM_BASE+(row['original']&65535)).to_bytes(4,'big'))
    put(0x8B3D,bytes([case['selector']]))
    if case['kind']=='metric':
        put(0x8618,bytes([case['mask']]));put(0x8870,bytes([case['count']]))
        for at,value in zip((0x86A7,0x8694,0x86AC),case['gain']):put(at,bytes([value]))
    if case['table_override']:
        put(0x1108E,case['table_first'].to_bytes(2,'big'));put(0x11090,case['table_second'].to_bytes(2,'big'))
    if case['axis_override']:put(0x15340,case['axis_first'].to_bytes(2,'big'))
    return {at:bytes(raw) for at,raw in values.items()}


def require_input(declared,image,case,observed):
    if (observed['entry']!=case['entry'] or not test_contract.exact(observed['context'],context(declared,case))
            or observed['sr_before']&0x3F1!=case['entry_sr']
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],calibrations(declared,image,case))
            or not test_contract.exact(observed['calibration_after'],calibrations(declared,image,case))):
        raise ValueError('a knock stage changes its complete RAM/context or artificial calibration inputs')
