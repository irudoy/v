"""Raw conditional division-callees observations inside the original complete primary."""

import hashlib
import json
from pathlib import Path

from kb import division_callees_contract as contract, division_callees_matrix as matrix

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parents[1]
REGION = 'jk08a-division-callees-paths'
HEADER = 'division-callees-path-cases.h'
HARNESS = 'harness-division-callees-paths.c'
OBSERVER = 'stock_ignition_consumer_invoke.s'
PREFIX = 'kb-division-callees-observation '
CAPTURE_LIMIT = 1200


def sha(value):
    return hashlib.sha256(value).hexdigest()


def declaration(target):
    if target.rom!='JK08A':
        raise ValueError('the division-callees capture requires the canonical owned JK08A image')
    source=contract.descriptor(ROOT)
    image=bytes(target.stock_image.data)
    contract.require_image(source,image)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',
        descriptor_sha256=sha((ROOT/contract.DESCRIPTOR).read_bytes()),source=source,
        cases=list(matrix.cases(source,image)),calibration_spans=[list(span) for span in matrix.calibration_spans(source)],
        semantic_admission=False,native_geometry_inference=False,caller_argument_inference=False,
        datum_identity_inference=False,automatic_resolution=False,
        natural_caller_reachability=False,hardware_qualification=False)


def header(declared,image):
    lines=['/* Exact direct-callee ABI inputs; independent consumers own outputs. */',
        '#define DIVISION_CALLEES_REGION '+json.dumps(REGION),
        'static const struct path_case division_callees_cases[] = {']
    for case in declared['cases']:
        values=(matrix.KINDS.index(case['kind']),case['entry'],case['divisor'],case['dividend'],
            case['previous_fault'],case['variant'],case['sr'])
        lines.append('    {'+','.join(f'0x{value:x}U' for value in values)+'},')
    return '\n'.join((*lines,'};','')).encode()

def region(declared,region_type):
    source=declared['source']
    spans=sorted((row['start'],row['end']) for row in source['entry'])
    return region_type(key=REGION,rom='JK08A',source=Path(source['assembly']).name,harness=HARNESS,
        start=spans[0][0],end=spans[0][1],callees=tuple(spans[1:]),
        pools=tuple((row['address'],row['width_bytes']) for row in source['pool']),
        ram_literals=tuple(row['address'] for row in source['pool'] if row['RAM_pointer_alias']),
        cases=len(declared['cases']),boundary=False)


def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('the division-callees original repeats a raw JSON key')
        result[key]=value
    return result


def observe(stdout,declared):
    actual=[json.loads(line[len(PREFIX):],object_pairs_hook=_objects)
            for line in stdout.splitlines() if line.startswith(PREFIX)]
    if len(actual)!=len(declared['cases']):
        raise ValueError('the division-callees original omits or duplicates a real invocation')
    for index,(packet,case) in enumerate(zip(actual,declared['cases'])):
        expected=dict(schema=1,index=index,kind=matrix.KINDS.index(case['kind']),entry=case['entry'])
        if any(type(packet.get(key)) is not int or packet[key]!=value for key,value in expected.items()):
            raise ValueError('the division-callees original changes its typed invocation role or order')
    marker=f'VQ_SH_ELF_DIVISION_CALLEES status=PASS region={REGION} cases={len(actual)}'
    if stdout.splitlines().count(marker)!=1:
        raise ValueError('the division-callees original lacks its unique complete marker')
    return actual,marker


def run(target,directory,captured):
    import verify_map_switching as base
    import verify_stock_code as stock
    from elf_storage_layout import require_separate_storage
    declared=declaration(target)
    image=bytes(target.stock_image.data)
    selected=region(declared,stock.Region)
    directory=Path(directory)/REGION
    directory.mkdir()
    private=directory/'consumed'
    private.mkdir()
    sources=(HARNESS,OBSERVER,selected.source)
    consumed={name:(TOOL_DIR/name).read_bytes() for name in sources}
    consumed[HEADER]=header(declared,image)
    for name,data in consumed.items():(private/name).write_bytes(data)
    reconstruction={}
    stock.require_reconstruction(selected,image,directory,source_path=private/selected.source,captured=reconstruction)
    fixture=bytearray(image)
    aliases=[]
    for row in declared['source']['pool']:
        if row['RAM_pointer_alias']:
            address,original=row['address'],row['stock_value']
            relocated=0x01000000+(original&65535)
            fixture[address:address+4]=relocated.to_bytes(4,'big')
            aliases.append(dict(address=address,original=original,alias=relocated))
    for start,end in selected.code_spans:
        if fixture[start:end]!=image[start:end]:
            raise ValueError('the division-callees fixture changes a tested stock instruction')
    observer=directory/'invoke.o'
    base.run_command([base.AS,'--big','--isa=sh2e','-o',observer,private/OBSERVER])
    fixture_path,rom_object=directory/'fixture.bin',directory/'fixture.o'
    fixture_path.write_bytes(fixture)
    base.run_command([base.OBJCOPY,'-I','binary','-O','elf32-sh','-B','sh',
        '--rename-section','.data=.rom,alloc,load,code,data,contents',fixture_path,rom_object])
    elf=directory/'harness.elf'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror',
        '-I',private,f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',elf,private/HARNESS,observer,rom_object]
    base.run_command(command,timeout=120)
    require_separate_storage(elf,((matrix.RAM_BASE,matrix.RAM_SIZE),))
    executable=elf.read_bytes()
    simulator=[base.RUN,'--memory-region=0x01000000,64k',str(elf)]
    result=base.run_command(simulator,timeout=CAPTURE_LIMIT)
    if fixture_path.read_bytes()!=fixture or elf.read_bytes()!=executable:
        raise ValueError('the division-callees actual fixture or executable changes during execution')
    for name in sources:
        if (TOOL_DIR/name).read_bytes()!=consumed[name] or (private/name).read_bytes()!=consumed[name]:
            raise ValueError('the division-callees consumed source changes during execution')
    actual,marker=observe(result.stdout,declared)
    captured.update(schema=1,declaration=declared,semantic_admission=False,
        consumed={name:data.hex() for name,data in consumed.items()},reconstruction=reconstruction,
        image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=sha(executable),
        observer_object_sha256=sha(observer.read_bytes()),aliases=aliases,boundaries=[],
        command=[str(value) for value in command],
        simulator=dict(command=simulator,returncode=result.returncode,timeout_seconds=CAPTURE_LIMIT),
        stdout=result.stdout,stderr=result.stderr,stdout_sha256=sha(result.stdout.encode()),
        stderr_sha256=sha(result.stderr.encode()),observations=actual,marker=marker,
        toolchain=stock.can_latch_copy.toolchain())
    return marker
