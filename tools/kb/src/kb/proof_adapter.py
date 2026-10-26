"""Deterministic input-only adapters for the existing ordinary observer ABI.

Generation shares typed input transport, never numerical or causal expectations.
The domain consumer independently admits the descriptor, input state and result.
"""

import hashlib
import json
from pathlib import Path
import re
import tomllib

SOURCE = 'tools/kb/src/kb/proof_adapter.py'
REFERENCE_DESCRIPTORS = ('defs/JK08A.closed-loop-coolant-accesses.toml',
    'defs/JK08A.maf-record-readers.toml')
DESCRIPTORS = (*REFERENCE_DESCRIPTORS, 'defs/JK08A.rpm-remaining-inhibit.toml',
    'defs/JK08A.exhaust-cvtc-accesses.toml','defs/JK08A.register-only-helpers.toml',
    'defs/JK08A.scalar-ram-leaves.toml','defs/JK08A.scalar-ram-products.toml','defs/JK08A.scalar-ram-gated.toml','defs/JK08A.rpm-ram-withdrawal-paths.toml','defs/JK08A.register-overflow-paths.toml','defs/JK08A.scalar-ram-word-paths.toml','defs/JK08A.rpm-state-withdrawal-paths.toml','defs/JK08A.indexed-word-update-paths.toml','defs/JK08A.division-caller-withdrawal-paths.toml','defs/JK08A.byte-curve-caller-withdrawal-paths.toml','defs/JK08A.word-interp-caller-withdrawal-paths.toml','defs/JK08A.scaled-division-caller-withdrawal-paths.toml','defs/JK08A.curve-scale-caller-withdrawal-paths.toml','defs/JK08A.derivative-scale-caller-withdrawal-paths.toml','defs/JK08A.guarded-quotient-caller-withdrawal-paths.toml','defs/JK08A.mixed-curve-caller-withdrawal-paths.toml','defs/JK08A.timing-remainder-caller-withdrawal-paths.toml','defs/JK08A.state-ratio-caller-withdrawal-paths.toml','defs/JK08A.dfco-state-caller-withdrawal-paths.toml','defs/JK08A.paired-inhibit-writer-withdrawal-paths.toml','defs/JK08A.threshold-window-reader-withdrawal-paths.toml','defs/JK08A.aux-rate-caller-withdrawal-paths.toml','defs/JK08A.paired-curve-normalization-withdrawal-paths.toml','defs/JK08A.byte-ratio-producer-withdrawal-paths.toml','defs/JK08A.state-surface-caller-withdrawal-paths.toml','defs/JK08A.byte-factor-caller-withdrawal-paths.toml','defs/JK08A.byte-sum-caller-withdrawal-paths.toml','defs/JK08A.clamp-latch-caller-withdrawal-paths.toml','defs/JK08A.paired-word-curve-sum-withdrawal-paths.toml','defs/JK08A.misfire-tail-dispatch-withdrawal-paths.toml',
    'defs/JK08A.diagnostic-record-bit4-paths.toml',
    'defs/JK08A.diagnostic-record-bits3-6-paths.toml',
    'defs/JK08A.diagnostic-record-composite-gate-paths.toml',
    'defs/JK08A.map-bias-division-caller-withdrawal-paths.toml',
    'defs/JK08A.diagnostic-record-highbit-clear-paths.toml')
PROFILE = 'ordinary-80-572'
TRANSPORT_FIELDS = frozenset(('schema', 'index', 'kind', 'entry', 'context',
    'context_after', 'observation', 'ram_before', 'ram_after',
    'calibration_before', 'calibration_after'))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def _integer(value, low, high):
    return type(value) is int and low <= value <= high


def _identifier(value):
    return type(value) is str and re.fullmatch(r'[a-z][a-z0-9_]*', value) is not None


def _spans(rows, *, empty=False):
    if type(rows) is not list or not empty and not rows:
        raise ValueError('an adapter requires explicit ordered observation spans')
    occupied = []
    for row in rows:
        if (type(row) is not dict or set(row) != {'address', 'size'}
                or not _integer(row['address'], 0, 0xFFFFFFFF)
                or not _integer(row['size'], 1, 65536)
                or row['address'] + row['size'] > 0x100000000):
            raise ValueError('an adapter changes a typed complete observation span')
        first, last = row['address'], row['address'] + row['size']
        if any(first < end and start < last for start, end in occupied):
            raise ValueError('an adapter repeats or overlaps an observation span')
        occupied.append((first, last))


def validate(value):
    keys = {'schema', 'profile', 'symbol', 'region', 'prefix', 'marker', 'header',
        'driver', 'refusals', 'fields', 'entries', 'kind', 'memory',
        'calibration', 'calibration_input', 'bound', 'dependencies'}
    if (type(value) is not dict or set(value) != keys
            or not _integer(value['schema'], 1, 1) or value['profile'] != PROFILE
            or not _identifier(value['symbol'])
            or type(value['calibration_input']) is not bool):
        raise ValueError('an adapter changes its bounded declaration or observer profile')
    for key, pattern in (('region', r'jk08a-[a-z0-9-]+'),
            ('prefix', r'kb-[a-z0-9-]+-observation '),
            ('marker', r'VQ_SH_ELF_[A-Z0-9_]+'),
            ('header', r'[a-z0-9-]+\.h'),
            ('driver', r'tools/sh-elf-run/harness-[a-z0-9-]+\.c'),
            ('refusals', r'tools/kb/tests/test_[a-z0-9_]+_adapter_generated\.py')):
        if type(value[key]) is not str or re.fullmatch(pattern, value[key]) is None:
            raise ValueError('an adapter changes a generated name or output boundary')
    fields = value['fields']
    if type(fields) is not list or not fields:
        raise ValueError('an adapter omits its typed input fields')
    names = set()
    for row in fields:
        if (type(row) is not dict or set(row) != {'name', 'bits'}
                or not _identifier(row['name']) or row['name'] in names
                or row['name'] in {'entry', 'kind', 'context', 'calibration'}
                or any(part in row['name'] for part in ('expected', 'terminal', 'result', 'output'))
                or not _integer(row['bits'], 1, 32)):
            raise ValueError('an adapter requires unique input-only typed fields')
        names.add(row['name'])
    if (type(value['entries']) is not list or not value['entries']
            or any(not _integer(at, 0, 0xFFFFFFFE) or at & 1 for at in value['entries'])
            or len(set(value['entries'])) != len(value['entries'])):
        raise ValueError('an adapter changes its exact allowed instruction entries')
    kind = value['kind']
    if (type(kind) is not dict or set(kind) != {'field', 'values'}
            or kind['field'] not in {'entry', 'kind'} or type(kind['values']) is not list
            or not kind['values'] or len({json.dumps(item) for item in kind['values']}) != len(kind['values'])
            or any(type(item) not in (int, str) for item in kind['values'])
            or kind['field'] == 'entry' and kind['values'] != value['entries']):
        raise ValueError('an adapter changes its explicit input-kind discriminator')
    widths = {row['name']: row['bits'] for row in fields}
    occupied = set()
    if type(value['memory']) is not list or not value['memory']:
        raise ValueError('an adapter omits its complete typed RAM input mapping')
    for row in value['memory']:
        if (type(row) is not dict or set(row) not in
                ({'offset', 'width', 'field'}, {'offset', 'width', 'value'})
                or not _integer(row['width'], 1, 4) or row['width'] not in (1, 2, 4)
                or not _integer(row['offset'], 0, 65536-row['width'])
                or row['offset'] % row['width']):
            raise ValueError('an adapter changes an aligned bounded RAM operand')
        at, width = row['offset'], row['width']
        if occupied.intersection(range(at, at+width)):
            raise ValueError('an adapter assigns a RAM input byte more than once')
        occupied.update(range(at, at+width))
        if ('field' in row and (row['field'] not in widths or widths[row['field']] > 8*width)
                or 'value' in row and not _integer(row['value'], 0, (1 << (8*width))-1)):
            raise ValueError('an adapter changes an input width or constant byte value')
    _spans(value['calibration'])
    _spans(value['bound'], empty=True)
    if (type(value['dependencies']) is not list or not value['dependencies']
            or len(set(value['dependencies'])) != len(value['dependencies'])
            or any(type(path) is not str or not path.startswith(('tools/', 'defs/'))
                or '..' in Path(path).parts or Path(path).is_absolute()
                for path in value['dependencies'])):
        raise ValueError('an adapter requires exact local source-dependency declarations')
    return value


def descriptor(root, path):
    if path not in DESCRIPTORS:
        raise ValueError('the adapter descriptor is outside the registered bounded sources')
    source = tomllib.loads((Path(root)/path).read_text())
    if 'adapter' not in source:
        raise ValueError('the bounded source omits its adapter declaration')
    return validate(source['adapter'])


def source_files(root, path):
    value = descriptor(root, path)
    return tuple(dict.fromkeys((SOURCE, path, value['driver'], value['refusals'], *value['dependencies'])))


def _kind(value, case):
    item = case[value['kind']['field']]
    for index, candidate in enumerate(value['kind']['values']):
        if type(item) is type(candidate) and item == candidate:
            return index
    raise ValueError('an adapter input changes its exact kind or entry phase')


def header(value, cases, context, calibration):
    """Serialize explicit input rows using domain input callbacks, with no oracle."""
    validate(value)
    symbol = value['symbol']
    upper = symbol.upper()
    cal_size = sum(row['size'] for row in value['calibration'])
    bound_size = sum(row['size'] for row in value['bound'])
    lines = ['/* Explicit typed invocation inputs and observation spans. */',
        '#define '+upper+'_REGION '+json.dumps(value['region']),
        f'#define {upper}_CALIBRATION_SIZE {cal_size}U',
        f'#define {upper}_BOUND_SIZE {bound_size}U']
    for label, spans in (('controlled', value['calibration']), ('bound', value['bound'])):
        if spans:
            lines.append('static const struct span '+symbol+'_'+label+'[] = {'+
                ','.join('{'+f'0x{row["address"]:x}U,{row["size"]}U'+'}' for row in spans)+'};')
    lines += ['struct path_case { uint32_t entry,kind,'+
        ','.join(row['name'] for row in value['fields'])+';',
        '    struct context context;'+(f' uint8_t calibration[{upper}_CALIBRATION_SIZE];'
            if value['calibration_input'] else '')+' };',
        'static const struct path_case '+symbol+'_cases[] = {']
    if type(cases) not in (list, tuple) or not cases:
        raise ValueError('an adapter requires a complete nonempty explicit input set')
    for case in cases:
        if case['entry'] not in value['entries'] or type(case['entry']) is not int:
            raise ValueError('an adapter input changes an allowed exact instruction entry')
        scalars = [case['entry'], _kind(value, case)]
        for row in value['fields']:
            scalar = case[row['name']]
            if not _integer(scalar, 0, (1 << row['bits'])-1):
                raise ValueError('an adapter input changes a complete typed scalar')
            scalars.append(scalar)
        registers = context(case)
        if (type(registers) is not tuple or len(registers) != 20
                or any(not _integer(item, 0, 0xFFFFFFFF) for item in registers)):
            raise ValueError('an adapter input omits its complete 80-byte observer context')
        prefix = ','.join(f'0x{item:x}U' for item in scalars)
        registers_text = ','.join(f'0x{item:x}U' for item in registers[:15])
        tail = ','.join(f'0x{item:x}U' for item in registers[15:])
        extra = ''
        if value['calibration_input']:
            spans = calibration(case)
            if type(spans) is not dict or set(spans) != {row['address'] for row in value['calibration']}:
                raise ValueError('an adapter input changes its exact calibration operand set')
            parts = []
            for row in value['calibration']:
                data = spans[row['address']]
                if type(data) is not bytes or len(data) != row['size']:
                    raise ValueError('an adapter input omits a complete calibration operand')
                parts.append(data)
            extra = ',{'+','.join(f'0x{item:02x}U' for item in b''.join(parts))+'}'
        lines.append('    {'+prefix+',{{'+registers_text+'},'+tail+'}'+extra+'},')
    return '\n'.join((*lines, '};', '')).encode()


_DRIVER = r'''/* Input driver defined by @DESCRIPTOR@. */
#include <stdint.h>
#include <stddef.h>
#include <stdio.h>
#include <string.h>
#define RAM_BASE 0x01000000U
#define RAM_SIZE 65536U
#define ARRAY_SIZE(value) (sizeof(value)/sizeof((value)[0]))
struct context { uint32_t r[15],gbr,mach,macl,entry_sr,fifth; };
struct observation {
    uint32_t exit[20],sp,continuation,abi_before[12],abi_after[12];
    uint8_t frame_before[192],frame_after[192];
    uint32_t sr_before;
};
struct span { uint32_t address,size; };
#include "@HEADER@"
_Static_assert(sizeof(void *)==4U,"SH-2E pointer ABI");
_Static_assert(sizeof(struct context)==80U,"complete incoming context");
_Static_assert(offsetof(struct context,fifth)==76U,"existing observer stack argument");
_Static_assert(sizeof(struct observation)==572U,"complete observer result");
_Static_assert(offsetof(struct observation,frame_before)==184U,"complete incoming frame");
_Static_assert(offsetof(struct observation,frame_after)==376U,"complete terminal frame");
_Static_assert(offsetof(struct observation,sr_before)==568U,"complete prepared SR");
extern void stock_invoke_ignition_consumer(uint32_t,const struct context *,struct observation *);
static uint8_t memory_before[RAM_SIZE],calibration_before[@UPPER@_CALIBRATION_SIZE];
@BOUND_STORAGE@
static void hex(const void *pointer,size_t size)
{
    const uint8_t *data=pointer;size_t index;
    for(index=0;index<size;++index)printf("%02x",(unsigned)data[index]);
}
static void rle(const uint8_t *data,size_t size)
{
    size_t first=0;
    while(first<size){
        size_t last=first+1U;
        while(last<size && data[last]==data[first])++last;
        printf("%s%lu:%02x",first ? "," : "",(unsigned long)(last-first),(unsigned)data[first]);
        first=last;
    }
}
static void snapshot(uint8_t *output,const struct span *spans,size_t count)
{
    size_t index,offset=0;
    for(index=0;index<count;++index){
        memcpy(output+offset,(const void *)(uintptr_t)spans[index].address,spans[index].size);
        offset+=spans[index].size;
    }
}
static void print_spans(const struct span *spans,size_t count)
{
    size_t index;
    for(index=0;index<count;++index)hex((const void *)(uintptr_t)spans[index].address,spans[index].size);
}
static int prepare(const struct path_case *input)
{
    @VARIABLES@
    if(@VALIDATION@)return 0;
    memset((void *)(uintptr_t)RAM_BASE,0xa5,RAM_SIZE);
@MEMORY@
@CALIBRATION@
    return 1;
}
int main(void)
{
    unsigned long index;
    for(index=0;index<ARRAY_SIZE(@SYMBOL@_cases);++index){
        const struct path_case *input=&@SYMBOL@_cases[index];
        struct context before,context=input->context;struct observation out;
        if(!prepare(input))return 1;
        memcpy(&before,&context,sizeof(before));memset(&out,0xa6,sizeof(out));
        memcpy(memory_before,(const void *)(uintptr_t)RAM_BASE,RAM_SIZE);
        snapshot(calibration_before,@SYMBOL@_controlled,ARRAY_SIZE(@SYMBOL@_controlled));
@BOUND_SNAPSHOT@
        stock_invoke_ignition_consumer(input->entry,&context,&out);
        printf("@PREFIX@{\"schema\":1,\"index\":%lu,\"kind\":%lu,\"entry\":%lu,\"context\":\"",
            index,(unsigned long)input->kind,(unsigned long)input->entry);
        hex(&before,sizeof(before));printf("\",\"context_after\":\"");hex(&context,sizeof(context));
        printf("\",\"observation\":\"");hex(&out,sizeof(out));
        printf("\",\"ram_before\":\"");rle(memory_before,RAM_SIZE);
        printf("\",\"ram_after\":\"");rle((const uint8_t *)(uintptr_t)RAM_BASE,RAM_SIZE);
        printf("\",\"calibration_before\":\"");hex(calibration_before,sizeof(calibration_before));
        printf("\",\"calibration_after\":\"");print_spans(@SYMBOL@_controlled,ARRAY_SIZE(@SYMBOL@_controlled));
@BOUND_PRINT@
        printf("\"}\n");
    }
    printf("@MARKER@ status=PASS region=%s cases=%lu\n",@UPPER@_REGION,index);
    return 0;
}
'''


def driver(value, path):
    validate(value)
    symbol, upper = value['symbol'], value['symbol'].upper()
    checks = ['('+' && '.join(f'input->entry!=0x{entry:x}U' for entry in value['entries'])+')',
        f'input->kind>={len(value["kind"]["values"])}U']
    checks.extend(f'input->{row["name"]}>0x{(1 << row["bits"])-1:x}U'
        for row in value['fields'] if row['bits'] < 32)
    memory = []
    for row in value['memory']:
        expression = 'input->'+row['field'] if 'field' in row else f'0x{row["value"]:x}U'
        bits = row['width']*8
        memory.append(f'    *(volatile uint{bits}_t *)(uintptr_t)(RAM_BASE+0x{row["offset"]:x}U)='
            f'(uint{bits}_t){expression};')
    controlled = value['calibration_input']
    substitutions = dict(DESCRIPTOR=path, HEADER=value['header'], UPPER=upper, SYMBOL=symbol,
        PREFIX=value['prefix'], MARKER=value['marker'], VALIDATION=' || '.join(checks),
        VARIABLES='size_t index,offset=0;' if controlled else '', MEMORY='\n'.join(memory),
        CALIBRATION=('    for(index=0;index<ARRAY_SIZE('+symbol+'_controlled);++index){\n'
            '        memcpy((void *)(uintptr_t)'+symbol+'_controlled[index].address,input->calibration+offset,\n'
            '            '+symbol+'_controlled[index].size);\n'
            '        offset+='+symbol+'_controlled[index].size;\n'
            '    }\n    if(offset!='+upper+'_CALIBRATION_SIZE)return 0;') if controlled else '',
        BOUND_STORAGE=('static uint8_t bound_before['+upper+'_BOUND_SIZE];') if value['bound'] else '',
        BOUND_SNAPSHOT=('        snapshot(bound_before,'+symbol+'_bound,ARRAY_SIZE('+symbol+'_bound));')
            if value['bound'] else '',
        BOUND_PRINT=('        printf("\\\",\\\"bound_before\\\":\\\"");hex(bound_before,sizeof(bound_before));\n'
            '        printf("\\\",\\\"bound_after\\\":\\\"");print_spans('+symbol+'_bound,ARRAY_SIZE('+symbol+'_bound));')
            if value['bound'] else '')
    result = _DRIVER
    for key, text in substitutions.items():
        result = result.replace('@'+key+'@', text)
    return result.encode()


def refusals(path):
    return ('"""Generated descriptor and complete raw-transport refusal sources."""\n\n'
        'from kb import proof_adapter, repo\n'
        'from tools.kb.tests.proof_adapter_cases import require_descriptor_refusals, require_transport_refusals\n\n'
        'DESCRIPTOR = '+repr(path)+'\n\n\n'
        'def test_current_generated_adapter_source_is_exact():\n'
        '    proof_adapter.require_generated(repo.ROOT, DESCRIPTOR)\n\n\n'
        'def test_adapter_rejects_inconsistent_or_result_bearing_declarations():\n'
        '    require_descriptor_refusals(proof_adapter.descriptor(repo.ROOT, DESCRIPTOR))\n\n\n'
        'def test_adapter_rejects_incomplete_or_substituted_raw_transport():\n'
        '    require_transport_refusals(proof_adapter.descriptor(repo.ROOT, DESCRIPTOR))\n').encode()


def generated(root, path):
    value = descriptor(root, path)
    return {value['driver']: driver(value, path), value['refusals']: refusals(path)}


def require_generated(root, path):
    for output, expected in generated(root, path).items():
        if (Path(root)/output).read_bytes() != expected:
            raise ValueError('a generated adapter source is stale or inconsistent: '+output)


def require_source_inputs(root, path, inputs):
    """Bind imported declared dependencies before the existing consumer admits a proof."""
    from kb import proof_reuse,proof_sources
    value=descriptor(root,path)
    closure=proof_sources.closure(root,source_files(root,path),
        declared_edges=proof_reuse.loader_declarations(root),
        generated_headers=['tools/sh-elf-run/'+value['header']])
    proof_sources.require_manifest(closure,inputs)


def write_generated(root, path):
    """Write only declared driver/refusal sources; do not construct or execute cases."""
    result = generated(root, path)
    for output, data in result.items():
        (Path(root)/output).write_bytes(data)
    return {output: digest(data) for output, data in result.items()}
