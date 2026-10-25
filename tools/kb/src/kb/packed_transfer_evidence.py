"""Independent bounded-state contracts for packed-field history transfers.

A wide transfer can preserve a declared byte field and its neighbors. This
module does not infer semantic storage width, publication width, natural entry
reachability or callee preservation from that fact. Complete original GNU and
TEST terminals and physical fixture admission are separate requirements.
"""

from pathlib import Path
import tomllib

from kb import test_contract
from kb.model import SymbolKey

DESCRIPTOR = 'defs/packed-field-transfers.toml'
RAM_BASE = 0x01000000
RAM_SIZE = 65536
MASK = 0xFFFFFFFF
LAYOUTS = {'1me3b': ('1ME3B', 0xFFFE0000),
           '1nd': ('1ND0A', 0xFFFE0000), 'jk78c': ('JK78C', 0xFFFF0000)}
WINDOWS = {
    '1me3b-timing-history': ('1me3b', 0x2133E, 0x21358),
    '1me3b-mask-history': ('1me3b', 0x2138E, 0x213A6),
    '1me3b-cvtc-history': ('1me3b', 0x21776, 0x21790),
    '1nd-timing-history': ('1nd', 0x21318, 0x21330),
    '1nd-mask-history': ('1nd', 0x21368, 0x21380),
    '1nd-cvtc-history': ('1nd', 0x21722, 0x21740),
    'jk78c-cvtc-history': ('jk78c', 0x21316, 0x21326),
}
COPY_BYTES = bytes.fromhex(
    '2f262f362f46880089126423340c6024210034268b0c6024801134268b08'
    '6024801234268b04602480133426710489ee64f663f6000b62f6'
)
ABI = (0x18283848, 0x19293949, 0x1A2A3A4A, 0x1B2B3B4B,
       0x1C2C3C4C, 0x1D2D3D4D, 0x1E2E3E4E, 0x12344321, 0x10203040, 0x50607080)


def descriptor(root):
    value = tomllib.loads((Path(root) / DESCRIPTOR).read_text())
    if (set(value) != {'schema', 'id', 'scope', 'semantic_width_inference',
                      'publication_width_inference', 'natural_entry_inference',
                      'hardware_qualification', 'field', 'window'}
            or type(value['schema']) is not int or value['schema'] != 1
            or value['id'] != 'packed-field-transfers'
            or any(value[key] is not False for key in ('semantic_width_inference',
                'publication_width_inference', 'natural_entry_inference', 'hardware_qualification'))):
        raise ValueError('the packed transfer descriptor changes its bounded compatibility scope')
    windows = {row['key']: row for row in value['window']}
    if len(windows) != len(value['window']) or set(windows) != set(WINDOWS):
        raise ValueError('the packed transfer descriptor omits or duplicates a declared window')
    for key, row in windows.items():
        layout, start, end = WINDOWS[key]
        if (not test_contract.exact((row['layout'], row['start'], row['end']), (layout, start, end))
                or row['rom'] != LAYOUTS[layout][0]
                or row['assembly'] != f'tools/sh-elf-run/stock_{layout}_packed_transfers.s'
                or type(row['natural_copy_callee_required']) is not bool):
            raise ValueError('the packed transfer descriptor changes its exact image or instruction boundary')
        if row['natural_copy_callee_required'] != key.endswith('-mask-history'):
            raise ValueError('the packed transfer descriptor hides a natural-callee obligation')
        if row['natural_copy_callee_required']:
            entry = row.get('copy_callee')
            callee, call, length = ((0x228EC, 0x21390, 56) if layout == '1me3b' else (0x22870, 0x2136A, 60))
            expected = dict(entry=callee, end=callee + 56, call=call, length_bytes=length,
                            source=0x01006000, destination=0x01006100)
            if (type(entry) is not dict or any(type(entry.get(name)) is not int or entry[name] != value
                                               for name, value in expected.items())):
                raise ValueError('the packed mask transfer changes its exact natural copy callee or caller inputs')
        elif 'copy_callee' in row:
            raise ValueError('the packed transfer declares an unrelated entry premise')
    identities = set()
    for field in value['field']:
        if field['symbol'] in identities or field['layout'] not in LAYOUTS:
            raise ValueError('the packed transfer descriptor repeats a field or changes its layout')
        identities.add(field['symbol'])
        if type(field['declared_bits']) is not int or field['declared_bits'] != 8:
            raise ValueError('the packed compatibility contract does not infer a wider semantic field')
        for transfer in field['transfer']:
            row = windows.get(transfer['window'])
            if row is None or row['layout'] != field['layout']:
                raise ValueError('the packed field transfer belongs to another instruction layout')
            if (type(transfer['physical_width_bytes']) is not int
                    or transfer['physical_width_bytes'] not in (2, 4)
                    or not row['start'] <= transfer['read'] < transfer['write'] < row['end']):
                raise ValueError('the packed field transfer changes its physical width or ordered instruction sites')
            address = int(field['symbol'].rsplit('-', 1)[1].split('/')[0], 16)
            if transfer['source'] != address:
                raise ValueError('the packed field transfer starts at another semantic member')
    return value


def bind_field(model, field):
    """Bind a retained width question without qualifying its disposition."""
    from kb import l0graph, match, reconciliation
    location, kind = field['symbol'].split('/')
    layout, address = location.rsplit('-', 1)
    symbol = model.symbols.get(SymbolKey(layout, kind, int(address, 16)))
    if (symbol is None or symbol.meaning is None or symbol.meaning.key != field['meaning']
            or symbol.layout != field['layout'] or type(symbol.value('width')) is not int
            or symbol.value('width') != field['declared_bits']):
        raise ValueError('the packed transfer field has another native owner, width or layout')
    l0 = match.l0_digest(layout, model.root)
    if field['original_l0'] != l0:
        raise ValueError('the packed transfer field has another normalized code source')
    spaces = tuple(sorted(model.spaces[model.layouts[layout].mcu].items()))
    locations = reconciliation.accesses(model.layouts[layout], spaces, model.root, l0)[1]
    observed = sorted({(function, site['site'], site['mode'], site['width'])
        for function, site in locations.get(symbol.key.location, ())
        if site['mode'] in l0graph.RAM_ACCESS_MODES and type(site.get('width')) is int
        and site['width'] * 8 > symbol.value('width')})
    wanted = sorted((row['function'], row['site'], row['mode'], row['width_bytes'])
                    for row in field['observed'])
    if not test_contract.exact(observed, wanted):
        raise ValueError('the packed transfer field adds, removes or changes a wider access question')
    claim = dict(symbol=symbol.key.key, width=symbol.value('width'), observed=observed)
    if reconciliation.digest(claim) != field['original_claim_sha256']:
        raise ValueError('the packed transfer width question differs from its retained exact claim')
    return symbol


def alias(layout, address):
    native = LAYOUTS[layout][1]
    if type(address) is not int or not native <= address < native + RAM_SIZE:
        raise ValueError('the packed transfer changes the physical RAM bank of its layout')
    return RAM_BASE + (address & 65535)


def signed(value, bits):
    return value - (1 << bits) if value & (1 << (bits - 1)) else value


def execute(window, image, context, before):
    """Independent straight-line equations for the exact bounded instructions.

    This is an oracle, not a stock executor or a qualified receipt. Only the
    explicit fixed-length natural copy calls have a control-transfer equation.
    Other control transfers and unsupported opcodes refuse this bounded scope.
    Every RAM read/store is retained in instruction order with its exact width.
    """
    if (type(context) is not tuple or len(context) != 19
            or any(type(word) is not int or not 0 <= word <= MASK for word in context)
            or type(before) is not bytes or len(before) != RAM_SIZE):
        raise ValueError('the packed transfer lacks a complete raw entry context or RAM view')
    layout, start, end = WINDOWS[window['key']]
    if (window['layout'], window['start'], window['end']) != (layout, start, end):
        raise ValueError('the packed transfer oracle receives another instruction boundary')
    registers = list(context[:15])
    callee = window.get('copy_callee')
    if window['natural_copy_callee_required']:
        if callee is None or (registers[1], registers[2], registers[7]) != (
                callee['destination'], callee['source'], callee['entry']):
            raise ValueError('the packed transfer changes its bounded natural-call inputs')
        if image[callee['entry']:callee['end']] != COPY_BYTES:
            raise ValueError('the packed transfer changes a byte of its exact natural copy callee')
    memory = bytearray(before)
    trace, pools, code = [], [], {}
    saved_frame = b''
    sr_clear_t = False

    def access(site, mode, address, width, value=None, register=0):
        if type(address) is not int or not RAM_BASE <= address <= RAM_BASE + RAM_SIZE - width:
            raise ValueError('the packed transfer accesses memory outside its admitted RAM bank')
        if address % width:
            raise ValueError('the packed transfer changes a natural aligned memory access')
        offset = address - RAM_BASE
        if mode == 'read':
            raw = bytes(memory[offset:offset + width])
        else:
            raw = (value & ((1 << (8 * width)) - 1)).to_bytes(width, 'big')
            memory[offset:offset + width] = raw
        trace.append(dict(site=site, mode=mode, address=address, width_bytes=width,
                          register=register, bytes=raw.hex()))
        result = int.from_bytes(raw, 'big')
        return (signed(result, 16) & MASK) if width == 2 else result

    pc = start
    while pc < end:
        if not 0 <= pc < len(image) - 1:
            raise ValueError('the packed transfer has incomplete stock instruction bytes')
        word = int.from_bytes(image[pc:pc + 2], 'big')
        code[pc] = image[pc:pc + 2].hex()
        n, m, low = word >> 8 & 15, word >> 4 & 15, word & 15
        if word == 0x470B:
            if (callee is None or pc != callee['call'] or registers[7] != callee['entry']
                    or image[pc + 2:pc + 4] != (0xE000 | callee['length_bytes']).to_bytes(2, 'big')):
                raise ValueError('the packed transfer changes its actual indirect callee or length-setting delay slot')
            length = callee['length_bytes']
            if length not in (56, 60):
                raise ValueError('the packed transfer requests an undeclared natural copy length')
            saved_frame = b''.join(registers[index].to_bytes(4, 'big') for index in (4, 3, 2))
            code[pc + 2] = image[pc + 2:pc + 4].hex()
            for offset in range(length):
                lane = offset % 4
                value = access(callee['entry'] + 14 + lane * 8, 'read', registers[2] + offset, 1)
                access(callee['entry'] + 16 + lane * 8, 'write', registers[1] + offset, 1, value)
                registers[0] = signed(value, 8) & MASK
            registers[1] += length
            sr_clear_t = True
            pc += 4
            continue
        elif word >> 12 == 0xD:
            pool = (pc & ~3) + 4 + (word & 255) * 4
            if pool + 4 > len(image):
                raise ValueError('the packed transfer has a truncated pointer pool')
            original = int.from_bytes(image[pool:pool + 4], 'big')
            value = alias(layout, original) if original >= 0xFFFE0000 else original
            registers[n] = value
            pools.append(dict(load=pc, address=pool, original=original, alias=value))
        elif word >> 12 == 5:
            registers[n] = access(pc, 'read', registers[m] + low * 4, 4, register=n)
        elif word >> 12 == 1:
            access(pc, 'write', registers[n] + low * 4, 4, registers[m], register=m)
        elif word & 0xF00F in (0x6001, 0x6002):
            width = 2 if low == 1 else 4
            registers[n] = access(pc, 'read', registers[m], width, register=n)
        elif word & 0xF00F in (0x2001, 0x2002):
            access(pc, 'write', registers[n], 2 if low == 1 else 4, registers[m], register=m)
        elif word & 0xFF00 == 0x8500:
            registers[0] = access(pc, 'read', registers[m] + low * 2, 2)
        elif word & 0xFF00 == 0x8100:
            access(pc, 'write', registers[m] + low * 2, 2, registers[0])
        elif word & 0xF00F == 0x6003:
            registers[n] = registers[m]
        elif word & 0xF00F == 0x600C:
            registers[n] = registers[m] & 255
        elif word >> 12 == 0xE:
            registers[n] = signed(word & 255, 8) & MASK
        elif word >> 12 == 7:
            registers[n] = (registers[n] + signed(word & 255, 8)) & MASK
        elif word & 0xF0FF == 0x4018:
            registers[n] = registers[n] << 8 & MASK
        elif word & 0xF0FF == 0x0012:
            registers[n] = context[15]
        else:
            raise ValueError(f'the packed transfer oracle has no independent equation for {word:04x} at {pc:08x}')
        pc += 2
    return dict(registers=tuple(registers), gbr=context[15], mach=context[16], macl=context[17],
                ram=bytes(memory), accesses=trace, pools=pools,
                code=code,
                sr_clear_t=sr_clear_t, saved_frame=saved_frame, sp_modified=False,
                natural_callee_in_scope=bool(saved_frame), natural_entry_proven=False)


def require_lanes(field, window, result, before):
    """Require actual byte-for-byte container transfer, with no width inference."""
    conclusions = []
    for transfer in field['transfer']:
        if transfer['window'] != window['key']:
            continue
        source = alias(field['layout'], transfer['source'])
        destination = alias(field['layout'], transfer['destination'])
        width = transfer['physical_width_bytes']
        loads = [row for row in result['accesses'] if row['site'] == transfer['read']]
        stores = [row for row in result['accesses'] if row['site'] == transfer['write']]
        if (len(loads) != 1 or len(stores) != 1
                or loads[0]['mode'] != 'read' or stores[0]['mode'] != 'write'
                or loads[0]['address'] != source or stores[0]['address'] != destination
                or loads[0]['width_bytes'] != width or stores[0]['width_bytes'] != width
                or loads[0]['register'] != transfer['data_register']
                or stores[0]['register'] != transfer['data_register']
                or result['code'].get(transfer['read']) != transfer['retained_read_bytes']
                or result['code'].get(transfer['write']) != transfer['retained_write_bytes']
                or loads[0]['bytes'] != stores[0]['bytes']):
            raise ValueError('the packed transfer changes its exact access, width, byte lane or copy value')
        data = bytes.fromhex(loads[0]['bytes'])
        if data != before[source - RAM_BASE:source - RAM_BASE + width]:
            raise ValueError('the packed transfer reads a modified or different original container')
        conclusions.append(dict(symbol=field['symbol'], read=transfer['read'], write=transfer['write'],
            physical_width_bytes=width, retained_field_byte=data[0], neighboring_bytes=data[1:].hex(),
            declared_field_bits=field['declared_bits'], semantic_width_inference=False,
            publication_width_inference=False, natural_entry_proven=False))
    if not conclusions:
        raise ValueError('the packed transfer field has no exact path in the observed window')
    return conclusions


def require_observation(window, image, observed):
    """Compare complete actual state with the independent straight-line oracle.

    The physical collector separately binds this parsed observation to its real
    original bytes, complete input matrix, GNU reconstruction and fixture.
    This comparison cannot qualify a width exception on its own.
    """
    result = execute(window, image, observed['context'], observed['memory_before'][0])
    expected = list(result['registers'])
    expected[7] = observed['continuation']
    sr = observed['sr_before'] & ~1 if result['sr_clear_t'] else observed['sr_before']
    exit_state = (sr, observed['continuation'], result['macl'], result['mach'],
                  result['gbr'], *reversed(expected))
    frame = bytearray(observed['frame_before'])
    seeded = bytearray(b''.join((0xA3B4C5D6 + index * 17).to_bytes(4, 'big') for index in range(48)))
    seeded[160:164] = observed['context'][7].to_bytes(4, 'big')
    seeded[184:188] = observed['continuation'].to_bytes(4, 'big')
    if result['saved_frame']:
        frame[148:160] = result['saved_frame']
    if (observed['sr_before'] & 0x3F1 != observed['context'][18]
            or not test_contract.exact(observed['exit'], exit_state)
            or observed['sp'] != (observed['abi_before'][10] - 164) & MASK
            or observed['abi_before'][:10] != ABI
            or observed['abi_before'] != observed['abi_after']
            or observed['frame_before'] != bytes(seeded)
            or bytes(frame) != observed['frame_after']
            or observed['memory_after'] != (result['ram'],)):
        raise ValueError('the packed transfer actual full state disagrees with independent bounded equations')
    return result
