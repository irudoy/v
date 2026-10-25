"""Independent bounded state equations for byte views and wider instructions.

These observations separate access width from a diagnostic byte or an indexed
base. They do not prove caller reachability, upstream value ranges, distant
GBR preservation or a semantic storage-width change. Native review retirement
requires a separately admitted exact disposition; raw capture is insufficient.
"""

from pathlib import Path
import tomllib

from kb import packed_transfer_evidence, test_contract
from kb import width_view_matrix as matrix

DESCRIPTOR = 'defs/JK08A.width-views.toml'
RAM_BASE, RAM_SIZE, MASK = matrix.RAM_BASE, matrix.RAM_SIZE, matrix.MASK
WINDOWS = {
    '118a-producer': (0x3CB9C,0x3CBB2,0xFFFF1E60,(0x3CB9C,),()),
    '118a-read-a': (0x3CC44,0x3CC4E,0xFFFF4534,(0x3CC44,),()),
    '118a-read-b': (0x3CC76,0x3CC7C,0xFFFF4534,(0x3CC76,),()),
    '118a-read-c': (0x3CE4E,0x3CE50,0xFFFF1114,(0x3CE4E,),()),
    '118a-read-d': (0x3CE8E,0x3CE90,0xFFFF1114,(0x3CE8E,),()),
    'working-terminal': (0x3CEB8,0x3CECE,0xFFFF1114,(0x3CEB8,0x3CEBE),()),
    '16d2-read-a': (0x35CE8,0x35CFC,0xFFFF4534,(0x35CE8,),()),
    '16d2-read-b': (0x7E670,0x7E680,0xFFFF4534,(0x7E670,),()),
    '16d2-read-c': (0x7E7BA,0x7E7CA,0xFFFF4534,(0x7E7BA,),()),
    '4544-write-a': (0x2C2CC,0x2C2D2,0xFFFF4534,(0x2C2CC,),()),
    '4544-read-a': (0x3CC9E,0x3CCA0,0xFFFF4534,(0x3CC9E,),()),
    '4544-write-b': (0x3CD5A,0x3CD62,0xFFFF4534,(0x3CD5A,),()),
    '4544-read-b': (0x3CDA4,0x3CDAA,0xFFFF4534,(0x3CDA4,),()),
    '4544-read-c': (0x3CDEA,0x3CDF6,0xFFFF4534,(0x3CDEA,),()),
    '4544-publication': (0xA81FA,0xA8206,0xFFFF9BB8,(0xA81FA,),()),
    '2142-indexed-store': (0x4A030,0x4A03C,0xFFFF4534,(0x4A030,),()),
    '2142-byte-counter': (0x4A35C,0x4A386,0xFFFF4534,(0x4A35C,),((0x4A3FE,0x4A402),)),
    '2142-indexed-read': (0x4A2FE,0x4A31C,0xFFFF4534,(0x4A2FE,0x4A402),((0x4A402,0x4A410),)),
}
FIELDS = {
    '7mfk-ffff118a/ram':('overjoyed-chameleon/ram',0x1116,0x22704),
    '7mfk-ffff16d2/ram':('daffodil-ape/ram',0x112A,0x22754),
    '7mfk-ffff4544/ram':('eager-boobook/ram',0x1129,0x22750),
    '7mfk-ffff2142/ram':('knock_count/ram',None,None),
}


def alias(address):
    if type(address) is not int or not 0xFFFF0000 <= address < 0x100000000:
        raise ValueError('the width-view input changes its exact physical RAM bank')
    return RAM_BASE + (address & 65535)


def spans(window):
    return ((window['start'],window['end']), *(tuple(row) for row in window['extra_spans']))


def descriptor(root):
    declared = tomllib.loads((Path(root) / DESCRIPTOR).read_text())
    if (set(declared) != {'schema','id','scope','semantic_width_inference','natural_entry_inference',
            'selector_range_inference','hardware_qualification','field','window','image'}
            or type(declared['schema']) is not int or declared['schema'] != 1
            or declared['id'] != 'jk08a-width-views'
            or any(declared[key] is not False for key in ('semantic_width_inference','natural_entry_inference',
                                                         'selector_range_inference','hardware_qualification'))):
        raise ValueError('the width-view descriptor changes its exact bounded scope')
    windows = {row['key']:row for row in declared['window']}
    if len(windows) != len(declared['window']) or set(windows) != set(WINDOWS):
        raise ValueError('the width-view descriptor omits or repeats a bounded window')
    for key,row in windows.items():
        current = (row['start'],row['end'],row['gbr'],tuple(row['entries']),tuple(tuple(span) for span in row['extra_spans']))
        if not test_contract.exact(current, WINDOWS[key]):
            raise ValueError('the width-view descriptor changes its exact code, entry or GBR premise')
    fields = {row['symbol']:row for row in declared['field']}
    if len(fields) != len(declared['field']) or set(fields) != set(FIELDS):
        raise ValueError('the width-view descriptor omits or repeats a retained native question')
    for key,row in fields.items():
        owner,did,record = FIELDS[key]
        if (row['meaning'] != owner or row['layout'] != '7mfk'
                or type(row['declared_bits']) is not int or row['declared_bits'] != 8
                or row['automatic_resolution'] is not False):
            raise ValueError('the width-view descriptor infers a semantic width or automatic resolution')
        if did is None:
            if row['kind'] != 'symbolic-indexed-base' or 'diagnostic' in row:
                raise ValueError('the indexed-base question changes its semantic disposition family')
        else:
            expected = dict(did=did,record=record,address=int(key.split('-')[1].split('/')[0],16),width_bytes=1)
            if row['kind'] != 'diagnostic-byte-view' or not test_contract.exact(row['diagnostic'],expected):
                raise ValueError('the width-view descriptor changes its exact diagnostic byte')
    image = declared['image']
    if (image['layout'] != '7mfk' or image['rom'] != 'JK08A'
            or image['assembly'] != 'tools/sh-elf-run/stock_jk08a_width_views.s'
            or image['sha256'] != 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'):
        raise ValueError('the width-view descriptor changes its owned stock image or mnemonic source')
    return declared


def bind_fields(model, declared):
    return tuple(packed_transfer_evidence.bind_field(model,row) for row in declared['field'])


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits-1)) else value


def execute(window, image, context, before, frame_before, sp, entry):
    """Execute equations only for admitted bounded instructions and memory.

    The independent oracle refuses any unsupported instruction, undeclared
    branch destination or memory domain. It retains actual-width accesses,
    both T outcomes, stack writes, register state and complete RAM bytes.
    """
    expected = WINDOWS.get(window.get('key'))
    current = (window.get('start'),window.get('end'),window.get('gbr'),
               tuple(window.get('entries',())),tuple(tuple(row) for row in window.get('extra_spans',())))
    if expected is None or not test_contract.exact(current,expected):
        raise ValueError('the width-view oracle receives another declared instruction boundary or premise')
    if (type(context) is not tuple or len(context) != 20
            or any(type(value) is not int or not 0 <= value <= MASK for value in context)
            or type(before) is not bytes or len(before) != RAM_SIZE
            or type(frame_before) is not bytes or len(frame_before) != 192
            or type(sp) is not int or sp & 3 or not 160 <= sp <= MASK-32
            or sp-160 < RAM_BASE+RAM_SIZE and RAM_BASE < sp+32
            or entry not in window['entries']):
        raise ValueError('the width-view oracle lacks its complete bounded input state')
    allowed = spans(window)
    registers = [*context[:15],sp]
    gbr,mach,macl = context[15:18]
    sr = context[18]
    memory,frame = bytearray(before),bytearray(frame_before)
    accesses,code = [],{}
    branch = None
    pc,steps = entry,0

    def access(site,mode,address,width,value=None,register=0):
        if width not in (1,2,4) or address % width:
            raise ValueError('the width-view oracle changes a natural aligned access')
        if RAM_BASE <= address <= RAM_BASE + RAM_SIZE - width:
            storage,offset = memory,address-RAM_BASE
        elif sp-160 <= address <= sp+32-width:
            storage,offset = frame,address-sp+160
        else:
            raise ValueError('the width-view oracle accesses an undeclared RAM or frame byte')
        if mode == 'write':
            storage[offset:offset+width] = (value & ((1 << (8*width))-1)).to_bytes(width,'big')
        raw = bytes(storage[offset:offset+width])
        accesses.append(dict(site=site,mode=mode,address=address,width_bytes=width,register=register,bytes=raw.hex()))
        integer = int.from_bytes(raw,'big')
        return signed(integer,width*8) & MASK if width < 4 else integer

    while pc != window['end']:
        if steps >= 256 or not any(start <= pc < end for start,end in allowed) or pc+2 > len(image):
            raise ValueError('the width-view oracle leaves its declared bounded control flow')
        steps += 1
        word = int.from_bytes(image[pc:pc+2],'big')
        code[pc] = image[pc:pc+2].hex()
        n,m,low = (word >> 8)&15,(word >> 4)&15,word&15
        previous_branch = branch
        branch = None
        next_pc = pc+2
        if word >> 12 in (9,13):
            width = 4 if word >> 12 == 13 else 2
            pool = ((pc & ~3) if width == 4 else pc) + 4 + (word & 255)*width
            if pool+width > len(image):
                raise ValueError('the width-view oracle has an incomplete PC-relative literal')
            value = int.from_bytes(image[pool:pool+width],'big')
            registers[n] = alias(value) if width == 4 and value >= 0xFFFF0000 else signed(value,width*8)&MASK
        elif word >> 12 == 14:
            registers[n] = signed(word&255,8)&MASK
        elif word >> 12 == 7:
            registers[n] = (registers[n]+signed(word&255,8))&MASK
        elif word & 0xF00F == 0x6003:
            registers[n] = registers[m]
        elif word & 0xF00F in (0x600C,0x600D):
            registers[n] = registers[m] & (255 if low == 12 else 65535)
        elif word & 0xF00F in (0x6000,0x6001,0x6002):
            registers[n] = access(pc,'read',registers[m],1 << low,register=n)
        elif word & 0xF00F in (0x000C,0x000D,0x000E):
            registers[n] = access(pc,'read',(registers[m]+registers[0])&MASK,1 << (low-12),register=n)
        elif word & 0xF00F in (0x0004,0x0005,0x0006):
            access(pc,'write',(registers[n]+registers[0])&MASK,1 << (low-4),registers[m],m)
        elif word >> 8 in (0x84,0x85):
            width = 1 << (word >> 8 & 1)
            registers[0] = access(pc,'read',(registers[m]+low*width)&MASK,width,register=0)
        elif word >> 8 in (0x80,0x81):
            width = 1 << (word >> 8 & 1)
            access(pc,'write',(registers[m]+low*width)&MASK,width,registers[0],0)
        elif word >> 12 == 5:
            registers[n] = access(pc,'read',(registers[m]+low*4)&MASK,4,register=n)
        elif word >> 12 == 1:
            access(pc,'write',(registers[n]+low*4)&MASK,4,registers[m],m)
        elif word & 0xF00F in (0x2000,0x2001,0x2002):
            access(pc,'write',registers[n],1 << low,registers[m],m)
        elif word >> 8 in (0xC0,0xC1,0xC2,0xC4,0xC5,0xC6):
            width = 1 << ((word >> 8)&3)
            address = (gbr+(word&255)*width)&MASK
            if word >> 8 & 4:
                registers[0] = access(pc,'read',address,width,register=0)
            else:
                access(pc,'write',address,width,registers[0],0)
        elif word & 0xF0FF in (0x4008,0x4018,0x4028):
            registers[n] = (registers[n] << {0x08:2,0x18:8,0x28:16}[word&255])&MASK
        elif word & 0xF0FF in (0x4009,0x4019,0x4029):
            registers[n] >>= {0x09:2,0x19:8,0x29:16}[word&255]
        elif word & 0xF0FF == 0x4000:
            sr = (sr&~1) | (registers[n] >> 31)
            registers[n] = (registers[n]<<1)&MASK
        elif word & 0xF00F == 0x300C:
            registers[n] = (registers[n]+registers[m])&MASK
        elif word & 0xF00F == 0x3008:
            registers[n] = (registers[n]-registers[m])&MASK
        elif word & 0xF00F == 0x2008:
            sr = (sr&~1) | int(registers[n]&registers[m] == 0)
        elif word & 0xF00F == 0x3007:
            sr = (sr&~1) | int(signed(registers[n],32)>signed(registers[m],32))
        elif word & 0xF00F == 0x0007:
            macl = (registers[n]*registers[m])&MASK
        elif word & 0xF0FF == 0x001A:
            registers[n] = macl
        elif word >> 8 == 0x88:
            sr = (sr&~1) | int(registers[0] == (signed(word&255,8)&MASK))
        elif word >> 8 in (0x89,0x8B):
            if previous_branch is not None:
                raise ValueError('the width-view oracle encounters a branch in a delay slot')
            take = bool(sr&1) if word >> 8 == 0x89 else not bool(sr&1)
            if take:next_pc = pc+4+signed(word&255,8)*2
        elif word >> 12 == 0xA:
            if previous_branch is not None:
                raise ValueError('the width-view oracle encounters a branch in a delay slot')
            branch = pc+4+signed(word&4095,12)*2
        elif word == 0x0009:
            pass
        else:
            raise ValueError(f'the bounded width-view oracle does not admit opcode {word:04x} at {pc:08x}')
        pc = previous_branch if previous_branch is not None else next_pc
    if branch is not None or registers[15] != sp:
        raise ValueError('the width-view oracle ends in a delay slot or changes the bounded SP')
    return dict(registers=tuple(registers[:15]),gbr=gbr,mach=mach,macl=macl,t=sr&1,
                frame=bytes(frame),ram=bytes(memory),accesses=accesses,code=code,entry=entry)


def require_observation(window,image,observed):
    seeded = bytearray(b''.join((0xA3B4C5D6+index*17).to_bytes(4,'big') for index in range(48)))
    context = observed['context']
    seeded[160:164] = context[7].to_bytes(4,'big')
    seeded[168:172] = context[19].to_bytes(4,'big')
    seeded[184:188] = observed['continuation'].to_bytes(4,'big')
    if (observed['frame_before'] != bytes(seeded)
            or observed['sp'] != (observed['abi_before'][10]-164)&MASK
            or observed['abi_before'][:10] != packed_transfer_evidence.ABI
            or observed['abi_before'] != observed['abi_after']
            or observed['sr_before'] & 0x3F1 != context[18]):
        raise ValueError('the width-view observation changes its complete input frame, SP, SR or caller ABI')
    result = execute(window,image,context,observed['memory_before'][0],bytes(seeded),observed['sp'],observed['entry'])
    registers = list(result['registers'])
    registers[7] = observed['continuation']
    expected = (observed['sr_before']&~1 | result['t'],observed['continuation'],
                result['macl'],result['mach'],result['gbr'],*reversed(registers))
    if (not test_contract.exact(observed['exit'],expected)
            or observed['frame_after'] != result['frame'] or observed['memory_after'] != (result['ram'],)):
        raise ValueError('the width-view actual full state disagrees with independent bounded equations')
    return result
