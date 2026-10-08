"""Independent bounded raw-state equations for the whole adjustment entry."""
from fractions import Fraction

MASK_OFFSETS = (0x2c,0x2e,0x30,0x33,0x35,0x37,0x39,0x3b,0x3d,0x3f,0x41,0x43,0x45,0x47,0x49)
PREVIOUS_OFFSETS = (6,2,0x12,0x10,0xe,0xc,0xa)
signed = lambda value: value-65536 if value&32768 else value
sat = lambda value: min(32767,max(-32768,value))

def lookup(table,axis,value):
    index = max((i for i in range(8) if value >= axis[i]),default=0)
    fraction = 0 if value <= axis[0] or index == 7 or value == axis[index] else int(Fraction(65536*(value-axis[index]),axis[index+1]-axis[index]))
    change = abs(table[index+1]-table[index])*fraction//65536
    return (table[index]+change if table[index+1] >= table[index] else table[index]-change),index,fraction

def evaluate(context,index,stock_tables):
    h = bytearray((0x6d+17*i+index)&255 for i in range(122))
    for bank in range(2):
        for offset,value in zip(PREVIOUS_OFFSETS,context['previous'][bank]):
            h[offset+bank] = value
    initial = bytes(h)
    def put16(at,value):
        h[at:at+2] = (value&65535).to_bytes(2,'big')
    def put32(at,value):
        h[at:at+4] = (value&0xffffffff).to_bytes(4,'big')
    for at,value in zip(MASK_OFFSETS,context['masks']):
        for bank in range(2):
            h[at+bank] = int(bool(value&(1<<bank)))
    h[0x32] = int(bool(context['control']&4))
    for destination,source in ((0x78,0x33),(0x72,0x35),(0x74,0x37),(0x70,0x3b),(0x76,0x3d)):
        h[destination:destination+2] = h[source:source+2]
    up_active,down_active,up_edge,down_edge = [],[],[],[]
    for bank in range(2):
        up_active.append(int(bool(h[0x47+bank] or h[0x43+bank]) and bool(context['extra'][bank])))
        down_active.append(int(bool(h[0x49+bank] or h[0x45+bank]) and bool(context['extra'][bank+2])))
        up_edge.append(int(bool(h[0x3f+bank]) and not h[0xe+bank] and bool(h[0x37+bank])))
        down_edge.append(int(bool(h[0x41+bank]) and not h[0xc+bank] and bool(h[0x37+bank])))
        for at,value in ((0x68,up_active[-1]),(0x60,down_active[-1]),(0x58,up_edge[-1]),(0x50,down_edge[-1])):
            put32(at+4*bank,value)
    up_selector,down_selector,up_step,down_step,called = [],[],[],[],[]
    for bank in range(2):
        rising = bool(h[0x33+bank]) and not h[0x12+bank]
        if h[0x3b+bank] == 1 or h[0x35+bank] == 1 or h[0x37+bank] == 0:
            h[6+bank] = h[4+bank] = 0
        elif not h[6+bank]:
            if rising:
                h[6+bank] = 1
            h[4+bank] = 0
        else:
            h[4+bank] = int(rising)
        selector = 4 if h[4+bank] else 3 if up_edge[bank] else 2 if up_active[bank] else 1
        up_selector.append(selector)
        h[0x4d+bank] = selector
        packet = lookup(context['up_table'],stock_tables['00015d00'],context['coordinate'][bank]) if selector == 2 else None
        if packet:
            called.append(dict(bank=bank,direction='up',index=packet[1],fraction=packet[2]))
        step = (context['up_four'] if selector == 4 else context['up_three'] if selector == 3 else packet[0] if packet else 0)
        up_step.append(step)
        put16(0x28+2*bank,step)
    h[8] = 2
    for bank in range(2):
        rising = bool(h[0x35+bank]) and not h[0x10+bank]
        if h[0x3d+bank] == 1 or h[0x33+bank] == 1 or h[0x37+bank] == 0:
            h[2+bank] = h[bank] = 0
        elif not h[2+bank]:
            if rising:
                h[2+bank] = 1
            h[bank] = 0
        else:
            h[bank] = int(rising)
    h[9] = 2
    counters = [(h[0xa+bank]+int(bool(up_active[bank] or up_edge[bank] or h[4+bank] or down_active[bank] or down_edge[bank] or h[bank])))&255 for bank in range(2)]
    for bank in range(2):
        selector = 4 if h[bank] else 3 if down_edge[bank] else 2 if down_active[bank] else 1
        down_selector.append(selector)
        h[0x4b+bank] = selector
        packet = lookup(context['down_table'],stock_tables['00015d10'],context['coordinate'][bank]) if selector == 2 else None
        if packet:
            called.append(dict(bank=bank,direction='down',index=packet[1],fraction=packet[2]))
        step = (context['down_four'] if selector == 4 else context['down_three'] if selector == 3 else packet[0] if packet else 0)
        down_step.append(step)
        put16(0x24+2*bank,step)
    admitted,intermediate,output = [],[],[]
    for bank in range(2):
        gate = not (h[0x39+bank] or h[0x2c+bank] or h[0x2e+bank] or h[0x30+bank]) or not h[0x32]
        admitted.append(int(gate))
        first = signed(context['state'][bank])+up_step[bank]
        delta = first-down_step[bank]
        if gate:
            put32(0x14,first)
            put32(0x18,delta)
        intermediate.append(sat(delta) if gate else 0)
        put16(0x1c+2*bank,intermediate[-1])
        low = max(context['lower'],intermediate[-1])
        put16(0x20+2*bank,low)
        output.append(min(context['upper'],low)&65535)
    for destination,source in ((0x12,0x33),(0x10,0x35),(0xe,0x3f),(0xc,0x41)):
        h[destination:destination+2] = h[source:source+2]
    h[0xa:0xc] = bytes(counters)
    return dict(initial_workspace=list(initial),workspace=list(h),up_selector=up_selector,
        down_selector=down_selector,up_step=up_step,down_step=down_step,counters=counters,
        admitted=admitted,intermediate=intermediate,output=output,called=called)
