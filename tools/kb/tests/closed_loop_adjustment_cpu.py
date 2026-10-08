"""Independent terminal-register and frame effects of the reviewed stock blocks."""
from tools.kb.tests.closed_loop_adjustment_model import MASK_OFFSETS, signed

def expectations(context,result):
    bits = {at:[int(bool(value&(1<<bank))) for bank in range(2)]
            for at,value in zip(MASK_OFFSETS,context['masks'])}
    rising_up = [int(bool(bits[0x33][bank]) and not context['previous'][bank][2]) for bank in range(2)]
    rising_down = [int(bool(bits[0x35][bank]) and not context['previous'][bank][3]) for bank in range(2)]
    workspace = result['workspace']
    up_active = [workspace[0x68+4*bank+3] for bank in range(2)]
    down_active = [workspace[0x60+4*bank+3] for bank in range(2)]
    up_edge = [workspace[0x58+4*bank+3] for bank in range(2)]
    down_edge = [workspace[0x50+4*bank+3] for bank in range(2)]
    pulse_up = [workspace[4+bank] for bank in range(2)]
    pulse_down = [workspace[bank] for bank in range(2)]
    put_byte,put_long = [],[]
    def byte(offset,value): put_byte.append([40+offset,value&255])
    def long(offset,value): put_long.append([40+offset,value&0xffffffff])
    for bank in range(2):
        for at,value in ((bank,rising_up[bank]),(4+bank,bits[0x3b][bank]),
            (8+bank,bits[0x35][bank]),(12+bank,bits[0x37][bank]),
            (16+bank,rising_down[bank]),(20+bank,bits[0x3d][bank]),
            (24+bank,bits[0x33][bank]),(28+bank,bits[0x37][bank])):
            byte(at,value)
    for at,value in ((0x20,bits[0x33][0]),(0x24,bits[0x33][1]),(0x28,bits[0x35][1]),
        (0x2c,bits[0x37][0]),(0x30,bits[0x37][1]),(0x34,bits[0x3b][1]),(0x50,pulse_down[1])):
        byte(at,value)
    if result['up_selector'][0] <= 2:
        long(0x38,up_active[0])
    if not (up_active[0] or up_edge[0] or pulse_up[0]):
        long(0x3c,down_active[0])
        if not down_active[0]:
            long(0x40,down_edge[0])
    long(0x44,rising_down[1])
    long(0x48,rising_down[0])
    long(0x4c,int(bool(up_active[0] or up_edge[0] or pulse_up[0] or down_active[0] or down_edge[0] or pulse_down[0])))
    # R4 is either a decoded byte, a stock table offset, or a local-frame address.
    r4_literal = bits[0x33][0]
    r4_stack_offset = None
    for bank in range(2):
        if not bits[0x3b][bank]:
            r4_stack_offset = -112
            if not bits[0x35][bank]:
                r4_stack_offset = -108
    for packet in result['called']:
        if packet['direction'] == 'up':
            r4_literal,r4_stack_offset = packet['index']*2,None
    for bank in range(2):
        if not bits[0x3d][bank]:
            r4_stack_offset = -96
            if not bits[0x33][bank]:
                r4_stack_offset = -92
                if bits[0x37][bank]:
                    r4_stack_offset = -104
    down_packets = [packet for packet in result['called'] if packet['direction'] == 'down']
    if down_packets:
        r4_literal,r4_stack_offset = down_packets[-1]['index']*2,None
    r2 = context['previous'][0][6]
    if r2&128: r2 -= 256
    r6 = pulse_down[1]
    if result['down_selector'][0] == 4: r6 = 0x8fa0
    if down_packets:
        r2 = result['down_step'][down_packets[-1]['bank']]
        packet = down_packets[-1]
        table = context['down_table']
        left,right = table[packet['index']],table[packet['index']+1]
        if right >= left:
            r2 = (right-left)*packet['fraction']//65536
    if result['down_selector'][1] == 2:
        r6 = 0x26740
    elif result['down_selector'][1] == 4:
        r6 = 0x8fa0
    # A bank-one call can survive a later mode-one or mode-three selection.
    elif down_packets:
        r6 = 0x26740
    for bank in range(2):
        if result['admitted'][bank]:
            delta = signed(context['state'][bank])+result['up_step'][bank]-result['down_step'][bank]
            r2 = result['intermediate'][bank]
            if delta <= 32767:
                r6 = result['intermediate'][bank]
    nested = []
    for packet in result['called']:
        direction,bank,index,fraction = packet['direction'],packet['bank'],packet['index'],packet['fraction']
        table = context['up_table' if direction == 'up' else 'down_table']
        call_return = (0xa1414,0xa144e)[bank] if direction == 'up' else (0xa164c,0xa1686)[bank]
        nested.append([36,call_return])
        nested.append([32,0x1462a if direction == 'up' else 0x1463a])
        if fraction:
            nested.append([28,0x264da])
            nested.append([24,0x26c78])
        if table[index] > table[index+1]:
            nested.append([36,table[index]])
    # Current caller M/Q survive unless a real nonzero-fraction division executes.
    divisions = [packet['fraction'] for packet in result['called'] if packet['fraction']]
    return dict(byte_writes=put_byte,long_writes=put_long,nested_writes=nested,
        r0=(result['counters'][1]-256 if result['counters'][1]&128 else result['counters'][1])&0xffffffff,
        r2=r2&0xffffffff,r4_literal=r4_literal,r4_stack_offset=r4_stack_offset,
        r5=(down_packets[-1]['fraction'] if down_packets else 2),r6=r6&0xffffffff,
        r7_literal=0x26984 if down_packets else None,r7_stack_offset=None if down_packets else -100,
        helper_called=bool(result['called']),last_fraction=result['called'][-1]['fraction'] if result['called'] else 0,
        divided=bool(divisions),exit_q=1-(divisions[-1]&1) if divisions else 0,
        exit_t=int(context['upper'] >= max(context['lower'],result['intermediate'][1])))
