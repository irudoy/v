"""Raw width-view observations inside the existing complete runtime primary."""

import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

from kb import width_view_evidence as contract, width_view_matrix as matrix

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parents[1]
REGION = 'jk08a-width-views'
HEADER = 'width-view-cases.h'
HARNESS = 'harness-width-views.c'
OBSERVER = 'stock_width_view_invoke.s'
PREFIX = 'kb-width-view-observation '
CAPTURE_LIMIT = 1200


def sha(data):
    return hashlib.sha256(data).hexdigest()


def declaration(target):
    if target.rom != 'JK08A':
        raise ValueError('the width-view capture requires the exact canonical JK08A image')
    source = contract.descriptor(ROOT)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',
        descriptor_sha256=sha((ROOT / contract.DESCRIPTOR).read_bytes()),
        windows=source['window'],fields=source['field'],image=source['image'],
        cases=[dict(window=index,case=case) for index,window in enumerate(source['window'])
               for case in matrix.cases(window)],semantic_width_inference=False,
        natural_entry_inference=False,selector_range_inference=False,
        automatic_resolution=False,hardware_qualification=False,semantic_admission=False)


def header(declared):
    lines=['/* Exact bounded inputs; independent consumers own semantic outputs. */',
           '#define WIDTH_VIEW_REGION '+json.dumps(REGION),
           f'#define WIDTH_VIEW_WINDOWS {len(declared["windows"])}U',
           'static const struct width_case width_cases[] = {']
    for row in declared['cases']:
        case=row['case']
        window=declared['windows'][row['window']]
        values=(row['window'],case['index'],case['entry'],case['pattern'],case['selector'],
                case['variant'],case['sr'],contract.alias(window['gbr']),
                int(window['key']=='4544-write-b'),int(window['key']=='2142-indexed-store'),
                2 if window['key']=='2142-byte-counter' else int(case['entry']==0x3CEBE))
        lines.append('    {'+','.join(f'0x{value:x}U' for value in values)+'},')
    return '\n'.join((*lines,'};','')).encode()


def region(declared,image,region_type):
    spans=sorted({span for row in declared['windows'] for span in contract.spans(row)})
    pools=set()
    for start,end in spans:
        for pc in range(start,end,2):
            word=int.from_bytes(image[pc:pc+2],'big')
            if word >> 12 in (9,13):
                width=4 if word >> 12==13 else 2
                pool=((pc&~3) if width==4 else pc)+4+(word&255)*width
                pools.add((pool,width))
    return region_type(key=REGION,rom='JK08A',source=Path(declared['image']['assembly']).name,
        harness=HARNESS,start=spans[0][0],end=spans[0][1],callees=tuple(spans[1:]),
        pools=tuple(sorted(pools)),ram_literals=tuple(address for address,size in sorted(pools)
            if size==4 and int.from_bytes(image[address:address+4],'big')>=0xFFFF0000),
        cases=len(declared['cases']),boundary=True,return_address_offset=24,return_register=7)


def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('the width-view original repeats a raw JSON key')
        result[key]=value
    return result


def observe(stdout,declared):
    actual=[json.loads(line[len(PREFIX):],object_pairs_hook=_objects)
            for line in stdout.splitlines() if line.startswith(PREFIX)]
    if len(actual)!=len(declared['cases']):
        raise ValueError('the width-view original omits or duplicates a real invocation')
    for index,(packet,row) in enumerate(zip(actual,declared['cases'])):
        expected=dict(schema=1,index=index,window=row['window'],case=row['case']['index'])
        if any(type(packet.get(key)) is not int or packet[key]!=value for key,value in expected.items()):
            raise ValueError('the width-view original changes typed invocation identity or order')
    marker=(f'VQ_SH_ELF_WIDTH_VIEWS status=PASS region={REGION} cases={len(actual)} '
            f'windows={len(declared["windows"])}')
    if stdout.splitlines().count(marker)!=1:
        raise ValueError('the width-view original lacks its unique complete marker')
    return actual,marker


def run(target,directory,captured):
    import verify_map_switching as base
    import verify_stock_code as stock
    from elf_storage_layout import require_separate_storage
    declared=declaration(target)
    image=bytes(target.stock_image.data)
    selected=region(declared,image,stock.Region)
    directory=Path(directory)/REGION
    directory.mkdir()
    private=directory/'consumed'
    private.mkdir()
    sources=(HARNESS,OBSERVER,selected.source)
    consumed={name:(TOOL_DIR/name).read_bytes() for name in sources}
    consumed[HEADER]=header(declared)
    for name,data in consumed.items():
        (private/name).write_bytes(data)
    reconstruction={}
    stock.require_reconstruction(selected,image,directory,source_path=private/selected.source,captured=reconstruction)
    fixture=bytearray(image)
    aliases=[]
    for address in selected.ram_literals:
        original=int.from_bytes(image[address:address+4],'big')
        relocated=contract.alias(original)
        fixture[address:address+4]=relocated.to_bytes(4,'big')
        aliases.append(dict(address=address,original=original,alias=relocated))
    boundary=stock.return_stub(SimpleNamespace(key=REGION,return_address_offset=24,return_register=7))
    boundaries=[]
    for row in declared['windows']:
        address=row['end']
        if (any(address<end and start<address+len(boundary) for start,end in selected.code_spans)
                or any(address<pool+size and pool<address+len(boundary) for pool,size in selected.pools)):
            raise ValueError('the width-view observation boundary changes tested stock bytes')
        fixture[address:address+len(boundary)]=boundary
        boundaries.append(dict(address=address,bytes=boundary.hex()))
    for start,end in selected.code_spans:
        if fixture[start:end]!=image[start:end]:
            raise ValueError('the width-view fixture changes an instruction under test')
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
    require_separate_storage(elf,((contract.RAM_BASE,contract.RAM_SIZE),))
    executable=elf.read_bytes()
    simulator=[base.RUN,'--memory-region=0x01000000,64k',str(elf)]
    result=base.run_command(simulator,timeout=CAPTURE_LIMIT)
    if fixture_path.read_bytes()!=fixture or elf.read_bytes()!=executable:
        raise ValueError('the width-view actual fixture or ELF changes during execution')
    for name in sources:
        if (TOOL_DIR/name).read_bytes()!=consumed[name] or (private/name).read_bytes()!=consumed[name]:
            raise ValueError('the width-view consumed executable source changes during execution')
    actual,marker=observe(result.stdout,declared)
    captured.update(schema=1,declaration=declared,semantic_admission=False,
        consumed={name:data.hex() for name,data in consumed.items()},reconstruction=reconstruction,
        image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=sha(executable),
        observer_object_sha256=sha(observer.read_bytes()),aliases=aliases,boundaries=boundaries,
        command=[str(part) for part in command],
        simulator=dict(command=simulator,returncode=result.returncode,timeout_seconds=CAPTURE_LIMIT),
        stdout=result.stdout,stderr=result.stderr,stdout_sha256=sha(result.stdout.encode()),
        stderr_sha256=sha(result.stderr.encode()),observations=actual,marker=marker,
        toolchain=stock.can_latch_copy.toolchain())
    return marker
