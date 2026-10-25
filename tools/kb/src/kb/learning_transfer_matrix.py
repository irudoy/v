"""Declared learned-grid inputs reuse existing literal input columns, never outputs."""

import ast
from copy import deepcopy
from pathlib import Path
import re

from kb import learning_transfer_contract as contract,repo

RAM_BASE=0x01000000
RAM_SIZE=65536
KINDS=('selection','learning','auxiliary','publication')
ENTRIES=(0x5796C,0x57D1E,0x580E8,0x57B26)
PUBLICATION_FIELDS=('ltft_l','ltft_a','ltft_u','ltft_v','ltft_mask','ltft_f','ltft_g','ltft_h','ltft_k')
FIELDS=('entry','argument','load','speed','packed','cell','flag','diagnostic','word','stft',
        'previous','cell_index','counter','permit_a','permit_b',*PUBLICATION_FIELDS)
INPUT_SOURCES=('tools/sh-elf-run/stock-jk08a-grid-selection-cases.h',
               'tools/sh-elf-run/stock-jk08a-grid-learning-cases.h',
               'tools/sh-elf-run/stock-jk08a-ltft-publication-cases.h')
PUBLICATION_PREFIX=16


def source_array(root,path,name):
    text=(Path(root)/path).read_text()
    matches=re.findall(name+r'\[\]\s*=\s*\{(.*?)\n\};',text,re.S)
    if len(matches)!=1 or re.fullmatch(r'[\s{},0-9a-fxU]+',matches[0]) is None:
        raise ValueError('the learned-grid input source changes its literal C array schema')
    body=re.sub(r'(0x[0-9a-f]+|\d+)U\b',r'\1',matches[0])
    return ast.literal_eval('['+body.replace('{','[').replace('}',']')+']')


def publication_inputs(root):
    text=(Path(root)/INPUT_SOURCES[2]).read_text()
    start=re.search(r'ltft_publication_cases\[\]\s*=\s*\{',text)
    if start is None:raise ValueError('the LTFT input source omits its explicit literal array')
    result=[]
    for line in text[start.end():].splitlines():
        line=line.strip()
        if not line:continue
        if line.startswith('};'):break
        raw=re.sub(r'(?<=[0-9a-fA-F])U\b','',line.rstrip(',')).replace('{','[').replace('}',']')
        row=ast.literal_eval(raw)
        if type(row) is not list or len(row)!=19:raise ValueError('an LTFT literal changes its explicit input shape')
        # Expected GPRs, output, terminal T and population labels supply no input.
        value=dict(argument=row[0],ltft_l=row[2],ltft_a=row[3],ltft_u=row[4],ltft_v=row[6]&65535,
            ltft_mask=row[7],diagnostic=row[8],ltft_f=row[9],ltft_g=row[10],ltft_h=row[11],ltft_k=row[12],
            ltft_lower=row[13],ltft_upper=row[14],t=row[15],variant=row[16])
        result.append(value)
        if len(result)==PUBLICATION_PREFIX:break
    if len(result)!=PUBLICATION_PREFIX:raise ValueError('the LTFT source changes its exact declared input prefix')
    return result


def cases(declared,image,root=repo.ROOT):
    result=[]
    selection_profiles=source_array(root,INPUT_SOURCES[0],'calibrations')
    learning_profiles=source_array(root,INPUT_SOURCES[1],'calibrations')
    def add(kind,bank,t=0,**changes):
        load_axis,speed_axis,load_hysteresis,speed_hysteresis=selection_profiles[0]
        thresholds,coefficients,initial,decay,lower,upper,aux_lower,aux_upper=learning_profiles[0]
        row=dict(index=len(result),kind=kind,entry=ENTRIES[KINDS.index(kind)],argument=bank,
            load=25600,speed=100,packed=0,cell=25600,flag=0,diagnostic=0,
            word=25600,stft=25600,previous=25600,cell_index=0,counter=1,permit_a=255,permit_b=255,
            load_axis=list(load_axis),speed_axis=list(speed_axis),load_hysteresis=load_hysteresis,
            speed_hysteresis=speed_hysteresis,thresholds=list(thresholds),coefficients=list(coefficients),
            initial=initial,decay=decay,lower=lower,upper=upper,aux_lower=aux_lower,aux_upper=aux_upper,
            ltft_l=25600,ltft_a=25600,ltft_u=1,ltft_v=0,ltft_mask=0,
            ltft_f=0,ltft_g=0,ltft_h=0,ltft_k=0,ltft_lower=90,ltft_upper=110,
            variant=bank,sr=t if kind=='publication' else t|((bank&3)<<8))
        row.update(deepcopy(changes));result.append(row)
    for raw in source_array(root,INPUT_SOURCES[0],'samples'):
        argument,load,speed,packed,cell,flag,diagnostic,t,profile,lower,upper=raw[:11]
        load_axis,speed_axis,lh,sh=selection_profiles[profile]
        add('selection',argument&255,t,load=load,speed=speed,packed=packed,cell=cell,flag=flag,
            diagnostic=diagnostic,load_axis=load_axis,speed_axis=speed_axis,load_hysteresis=lh,
            speed_hysteresis=sh,lower=lower,upper=upper)
    for raw in source_array(root,INPUT_SOURCES[1],'samples'):
        argument,word,stft,previous,index,counter,permit_a,permit_b,t,profile,coefficient,decay_override=raw[:12]
        thresholds,coefficients,initial,decay,lower,upper,aux_lower,aux_upper=learning_profiles[profile]
        add('learning',argument&255,t,word=word,stft=stft,previous=previous,cell_index=index,
            counter=counter,permit_a=permit_a,permit_b=permit_b,thresholds=thresholds,
            coefficients=[coefficient]*4 if coefficient<256 else coefficients,initial=initial,
            decay=decay_override if decay_override<256 else decay,lower=lower,upper=upper,
            aux_lower=aux_lower,aux_upper=aux_upper)
    for bank in (0,1):
        for cell in (23039,23040,28160,28161):add('selection',bank,cell=cell)
        for index in (0,1,63,255):
            for counter in (0,1,0x7F,0x80,0xFE,0xFF):
                for word in (0,23039,23040,28159,28160,65535):
                    for decay in (0,1,32,127,255):
                        add('auxiliary',bank,cell_index=index,counter=counter,word=word,decay=decay)
        for field,values in (('word',(25599,25600,25601)),('stft',(1,25600)),
                             ('previous',(25600,25601))):
            for value in values:
                changes=dict(stft=1);changes[field]=value
                add('learning',bank,**changes)
        for field,values,extra in (('decay',(0,1),dict(counter=254)),
                                  ('aux_lower',(100,101),{}),('aux_upper',(100,101),{})):
            for value in values:add('learning',bank,**extra,**{field:value})
        for kind in KINDS:add(kind,bank,argument=0xF00DCA00|bank)
    for incoming in publication_inputs(root):
        value=dict(incoming);argument=value.pop('argument');t=value.pop('t')
        add('publication',argument&255,t,argument=argument,**value)
    for bank in (0,1):
        for mask in (0,1,2,255):
            for u,v in ((0,65535),(0,0),(1,0),(32767,32767),(32768,32767),(65535,32768)):
                for left,right in ((0,0),(25599,0),(25600,0),(25601,0),(65535,65535),(23040,25600),(28160,25600)):
                    add('publication',bank,ltft_l=left,ltft_a=right,ltft_u=u,ltft_v=v,ltft_mask=mask)
        for diagnostic in (0,128):
            for f in (0,1):
                for g in (0,1):
                    for h in (0,1,2,3):
                        for k in (0,64):
                            add('publication',bank,diagnostic=diagnostic,ltft_f=f,ltft_g=g,ltft_h=h,ltft_k=k)
        for lower,upper in ((0,0),(0,255),(90,110),(110,90),(255,255)):
            for left,right in ((0,0),(25600,25600),(65535,65535)):
                add('publication',bank,ltft_l=left,ltft_a=right,ltft_lower=lower,ltft_upper=upper)
        for field in ('ltft_l','ltft_a'):
            for value in (25599,25600,25601):add('publication',bank,ltft_mask=3,**{field:value})
    for case in result:
        if case['kind']!='publication':continue
        if (case['argument']&255 not in (0,1) or case['sr'] not in (0,1) or case['variant'] not in range(4)
                or any(type(case[key]) is not int or not 0<=case[key]<=65535
                       for key in ('ltft_l','ltft_a','ltft_u','ltft_v'))
                or any(type(case[key]) is not int or not 0<=case[key]<=255
                       for key in ('ltft_mask','diagnostic','ltft_f','ltft_g','ltft_h','ltft_k','ltft_lower','ltft_upper'))):
            raise ValueError('an LTFT raw input changes its exact complete bank/byte/word/context domain')
    return tuple(result)


def context(declared,case):
    registers=[(0x1728394A+index*0x110203+case['variant']*0x1000101)&0xFFFFFFFF for index in range(15)]
    registers[4]=case['argument']
    if case['kind']=='auxiliary':
        bank=case['argument']&255
        registers[4]=RAM_BASE+(0x49B0 if bank else 0x49F0)
        registers[5]=case['cell_index'];registers[6]=case['argument']
    return (*registers,0x12344321,0x13579BDF,0x2468ACE0,case['sr'],0xB6C70000)


def memory(case):
    bank=case['argument']&255
    if bank not in (0,1):raise ValueError('the learned-grid input changes its explicit bank domain')
    result=bytearray([0xA5])*RAM_SIZE
    for base in (0x4B10,0x4B90):result[base:base+128]=bytes.fromhex('5a5a')*64
    def word(at,value):result[at:at+2]=value.to_bytes(2,'big')
    if case['kind']=='selection':
        word(0x1024,case['load']);result[0x11AE]=case['speed'];result[0x130A+bank]=case['packed']
        grid=0x4B10 if bank else 0x4B90;result[grid:grid+128]=case['cell'].to_bytes(2,'big')*64
        result[0x41B5]=case['flag'];result[0x5A94]=case['diagnostic']
    elif case['kind']=='publication':
        word(0x2306+bank*2,case['ltft_l']);word(0x5648+bank*2,case['ltft_a'])
        word(0x15FC,case['ltft_u']);word(0x15FE,case['ltft_v']);result[0x230E]=case['ltft_mask']
        for at,key in ((0x5A94,'diagnostic'),(0x41B5,'ltft_f'),(0x41FA,'ltft_g'),(0x248B,'ltft_h'),(0x249C,'ltft_k')):
            result[at]=case[key]
    else:
        word(0x134E+bank*2,case['word']);word(0x22DC+bank*2,case['stft'])
        word(0x2306+bank*2,case['previous']);result[0x130A+bank]=case['cell_index']&255
        auxiliary=0x49B0 if bank else 0x49F0
        if case['cell_index']<64:result[auxiliary+case['cell_index']]=case['counter']
        result[0x1458]=case['permit_a'];result[0x1457]=case['permit_b']
        result[0x2C21:0x2C24]=bytes(case['thresholds'])
    return bytes(result)


def calibration_spans(declared):
    intervals=sorted({(row['address'],row['address']+row['size']) for unit in contract.UNITS for row in unit['pools']})
    merged=[]
    for first,last in intervals:
        if merged and first<=merged[-1][1]:merged[-1]=(merged[-1][0],max(last,merged[-1][1]))
        else:merged.append((first,last))
    return tuple((first,last-first) for first,last in merged)


def calibrations(declared,image,case):
    result={at:bytearray(image[at:at+size]) for at,size in calibration_spans(declared)}
    def put(at,data):
        for first,value in result.items():
            if first<=at and at+len(data)<=first+len(value):
                value[at-first:at-first+len(data)]=data;return
        raise ValueError('the learned-grid input changes an undeclared calibration span')
    for at,original in contract.ALIASES.items():put(at,(RAM_BASE+(original&65535)).to_bytes(4,'big'))
    put(0x839C,bytes((case['aux_upper'],case['aux_lower'])))
    put(0x88F5,bytes([case['decay']]))
    put(0x8A9E,bytes((case['lower'],case['upper'])))
    put(0x8E5A,bytes((case['ltft_upper'],case['ltft_lower'])))
    if case['kind']=='selection':
        put(0x12592,bytes(case['load_axis']));put(0x126DC,bytes(case['speed_axis']))
        put(0x881A,bytes((case['speed_hysteresis'],case['load_hysteresis'])))
    else:
        put(0x129C6,bytes(case['coefficients']));put(0x8A9D,bytes([case['initial']]))
    return {at:bytes(data) for at,data in result.items()}


def require_input(declared,image,case,observed):
    from kb import test_contract
    if (observed['entry']!=case['entry'] or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(memory(case),)
            or not test_contract.exact(observed['calibration_before'],calibrations(declared,image,case))
            or not test_contract.exact(observed['calibration_after'],calibrations(declared,image,case))):
        raise ValueError('the learned-grid original changes a complete declared datum, argument or calibration input')
