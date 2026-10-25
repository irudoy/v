"""Explicit K, mode, aggregate and speed inputs for the natural BFS producer."""

from kb import test_contract

RAM_BASE=0x01000000
RAM_SIZE=65536
KINDS=('bfs',)
K_VALUES=(0,1,255,256,16384,32768,65535)


def cases(declared,image):
    stock=int.from_bytes(image[0x9284:0x9286],'big')
    result=[]
    def add(k,stock_input,aggregate,rpm,mode):
        index=len(result)
        result.append(dict(index=index,kind='bfs',entry=0x3B75C,k=k,stock_input=stock_input,
            aggregate=aggregate,rpm=rpm,mode=mode,variant=index%4,
            sr=(index&1)|((index&15)<<4)|((index&3)<<8)))
    for k,stock_input in (*((value,False) for value in K_VALUES),(stock,True)):
        for aggregate in (1,64,1000,65535):
            for rpm in (64,1024,65535):
                for mode in (0,1):add(k,stock_input,aggregate,rpm,mode)
    for aggregate in (0,0x80000000,0xFFFFFFFF):
        for mode in (0,1):add(stock,True,aggregate,1024,mode)
    return tuple(result)


def calibration_spans(declared):
    return ((0x9284,2),)


def calibrations(declared,image,case):
    if type(case['k']) is not int or not 0<=case['k']<=65535:
        raise ValueError('the BFS K input changes its exact unsigned word width')
    if case['stock_input'] is True and case['k']!=int.from_bytes(image[0x9284:0x9286],'big'):
        raise ValueError('the BFS stock K role differs from the actual owned image')
    return {0x9284:case['k'].to_bytes(2,'big')}


def context(declared,case):
    values=[(0x1728394A+reg*0x110203+case['variant']*0x1000101)&0xFFFFFFFF for reg in range(15)]
    return (*values,0x12344321,0x13579BDF,0x2468ACE0,case['sr'],0xB6C70000|case['k'])


def memory(case):
    ram=bytearray(RAM_SIZE)
    ram[0x1E38:0x1E3C]=case['aggregate'].to_bytes(4,'big')
    ram[0x2804]=128
    ram[0x11E8:0x11EA]=case['rpm'].to_bytes(2,'big')
    ram[0x1160]=128
    ram[0x115C:0x115E]=(8192).to_bytes(2,'big')
    ram[0x1DEE:0x1DF0]=(65535).to_bytes(2,'big')
    ram[0x11EB]=255
    ram[0x2449]=case['mode']*128
    return bytes(ram)


def require_input(declared,image,case,observed):
    if (observed['entry']!=case['entry']
            or not test_contract.exact(observed['context'],context(declared,case))
            or observed['memory_before']!=(memory(case),)
            or observed['calibration_before']!=calibrations(declared,image,case)
            or observed['calibration_after']!=observed['calibration_before']):
        raise ValueError('the BFS original changes its declared K, mode, speed, aggregate or full entry state')
