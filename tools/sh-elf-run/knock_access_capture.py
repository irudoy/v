"""Four separate raw stock knock fixtures in the existing complete COPY primary."""

import hashlib
import json
from pathlib import Path

from kb import knock_access_unit_contract as contract,knock_access_matrix as matrix

TOOL_DIR=Path(__file__).resolve().parent
ROOT=TOOL_DIR.parent.parent
REGION='jk08a-knock-accesses'
HEADER='knock-access-cases.h'
HARNESS='harness-knock-accesses.c'
OBSERVER='stock_ignition_consumer_invoke.s'
RETURN=Path(contract.RETURN_SOURCE).name
PREFIX='kb-knock-access-observation '
CAPTURE_LIMIT=1200


def sha(data):return hashlib.sha256(data).hexdigest()


def sources(kind):
    unit=next(unit for unit in contract.UNITS if unit['id']==kind)
    return (Path(unit['assembly']).name,Path(matrix.INPUT_SOURCES[matrix.KINDS.index(kind)]).name)


def declaration(target,kind):
    if target.rom!='JK08A':raise ValueError('the knock access capture requires the owned JK08A image')
    source=contract.selection(ROOT,kind);image=bytes(target.stock_image.data)
    contract.require_image(source,image)
    return dict(schema=1,region=REGION,kind=kind,layout='7mfk',rom='JK08A',
        descriptor_sha256=sha((ROOT/contract.DESCRIPTOR).read_bytes()),source=source,
        cases=list(matrix.cases(source,image,root=ROOT)),
        calibration_spans=[list(row) for row in matrix.calibration_spans(source)],
        semantic_admission=False,native_geometry_inference=False,caller_argument_inference=False,
        datum_identity_inference=False,automatic_resolution=False,
        natural_caller_reachability=False,hardware_qualification=False)


def header(declared,image):
    spans=matrix.calibration_spans(declared['source']);size=sum(width for at,width in spans)
    lines=['/* Explicit knock stage inputs; no expected outputs, GPRs or frame state. */',
        '#define KNOCK_ACCESS_REGION '+json.dumps(REGION),
        f'#define KNOCK_ACCESS_KIND {matrix.KINDS.index(declared["kind"])}U',
        f'#define KNOCK_ACCESS_CALIBRATION_SIZE {size}U',
        'static const uint32_t knock_access_calibration_starts[] = {'+
        ','.join(f'0x{at:x}U' for at,width in spans)+'};',
        'static const uint32_t knock_access_calibration_sizes[] = {'+
        ','.join(f'{width}U' for at,width in spans)+'};',
        'struct path_case {','    uint32_t kind,'+','.join(matrix.FIELDS)+';',
        *('    uint32_t '+name+'['+str(count)+'];' for name,count in matrix.ARRAYS),
        '    struct context context;',
        '    uint8_t calibration[KNOCK_ACCESS_CALIBRATION_SIZE];','};',
        'static const struct path_case knock_access_cases[] = {']
    for case in declared['cases']:
        values=','.join(f'0x{value:x}U' for value in
            (matrix.KINDS.index(case['kind']),*(case[key] for key in matrix.FIELDS)))
        arrays=','.join('{'+','.join(f'0x{value:x}U' for value in case[name])+'}' for name,count in matrix.ARRAYS)
        context=matrix.context(declared['source'],case)
        registers=','.join(f'0x{value:x}U' for value in context[:15])
        tail=','.join(f'0x{value:x}U' for value in context[15:])
        calibration=matrix.calibrations(declared['source'],image,case)
        data=b''.join(calibration[at] for at,width in spans)
        raw=','.join(f'0x{value:02x}U' for value in data)
        lines.append('    {'+values+','+arrays+',{{'+registers+'},'+tail+'},{'+raw+'}},')
    return '\n'.join((*lines,'};','')).encode()


def observe(stdout,declared):
    rows=[json.loads(line[len(PREFIX):]) for line in stdout.splitlines() if line.startswith(PREFIX)]
    marker=(f'VQ_SH_ELF_KNOCK_ACCESSES status=PASS region={REGION} '
        f'kind={declared["kind"]} cases={len(declared["cases"])}')
    if len(rows)!=len(declared['cases']) or stdout.splitlines().count(marker)!=1:
        raise ValueError('a knock stage capture lacks its unique complete raw invocation set')
    return rows,marker


def run_unit(target,directory,kind):
    import verify_map_switching as base
    import verify_stock_code as stock
    from elf_storage_layout import require_separate_storage
    declared=declaration(target,kind);image=bytes(target.stock_image.data)
    directory=directory/kind;directory.mkdir();private=directory/'consumed';private.mkdir()
    names=(HARNESS,OBSERVER,RETURN,*sources(kind))
    consumed={name:(TOOL_DIR/name).read_bytes() for name in names}
    consumed[HEADER]=header(declared,image)
    for name,data in consumed.items():(private/name).write_bytes(data)
    unit=declared['source']['unit'][0];first,*rest=unit['code'];assembly=Path(unit['assembly']).name
    selected=stock.Region(key=kind,rom='JK08A',source=assembly,harness=HARNESS,
        start=first['start'],end=first['end'],callees=tuple((row['start'],row['end']) for row in rest),
        pools=tuple((row['address'],row['size']) for row in unit['pools']),
        ram_literals=tuple(row['address'] for row in unit['aliases']),cases=1,boundary=False)
    reconstructed={};reconstruction_directory=directory/'reconstruction';reconstruction_directory.mkdir()
    stock.require_reconstruction(selected,image,reconstruction_directory,source_path=private/assembly,captured=reconstructed)
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    returns=[]
    for index,row in enumerate(unit['boundary']):
        stem=directory/f'return-{index}'
        base.run_command([base.AS,'--big','--isa=sh2e','-o',stem.with_suffix('.o'),private/RETURN])
        base.run_command([base.LD,'-EB',f'-Ttext={row["address"]:#x}','-o',stem.with_suffix('.elf'),stem.with_suffix('.o')])
        base.run_command([base.OBJCOPY,'-O','binary','--only-section=.text',stem.with_suffix('.elf'),stem.with_suffix('.bin')])
        data=stem.with_suffix('.bin').read_bytes()
        if data!=bytes.fromhex(row['bytes']):raise ValueError('a knock observing return changes independent bytes')
        returns.append(dict(address=row['address'],bytes=data.hex(),source_sha256=sha(consumed[RETURN]),
            object_sha256=sha(stem.with_suffix('.o').read_bytes()),elf_sha256=sha(stem.with_suffix('.elf').read_bytes())))
    observer=directory/'invoke.o'
    base.run_command([base.AS,'--big','--isa=sh2e','-o',observer,private/OBSERVER])
    fixture_path,rom_object=directory/'fixture.bin',directory/'fixture.o';fixture_path.write_bytes(fixture)
    base.run_command([base.OBJCOPY,'-I','binary','-O','elf32-sh','-B','sh',
        '--rename-section','.data=.rom,alloc,load,code,data,contents',fixture_path,rom_object])
    elf=directory/'harness.elf'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',private,
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',elf,private/HARNESS,observer,rom_object]
    base.run_command(command,timeout=120);require_separate_storage(elf,((matrix.RAM_BASE,matrix.RAM_SIZE),))
    executable=elf.read_bytes();simulator=[base.RUN,'--memory-region=0x01000000,64k',str(elf)]
    result=base.run_command(simulator,timeout=CAPTURE_LIMIT)
    if fixture_path.read_bytes()!=fixture or elf.read_bytes()!=executable:
        raise ValueError('a knock fixture or executable changes during capture')
    for name in names:
        if (TOOL_DIR/name).read_bytes()!=consumed[name] or (private/name).read_bytes()!=consumed[name]:
            raise ValueError('a knock executable source changes during capture')
    actual,marker=observe(result.stdout,declared)
    packet=dict(schema=1,declaration=declared,semantic_admission=False,
        consumed={name:data.hex() for name,data in consumed.items()},reconstruction=reconstructed,
        image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=sha(executable),
        observer_object_sha256=sha(observer.read_bytes()),aliases=aliases,boundaries=returns,
        command=[str(value) for value in command],
        simulator=dict(command=simulator,returncode=result.returncode,timeout_seconds=CAPTURE_LIMIT),
        stdout=result.stdout,stderr=result.stderr,stdout_sha256=sha(result.stdout.encode()),
        stderr_sha256=sha(result.stderr.encode()),observations=actual,marker=marker,
        toolchain=stock.can_latch_copy.toolchain())
    return packet


def run(target,directory,captured):
    directory=Path(directory)/REGION;directory.mkdir()
    units={kind:run_unit(target,directory,kind) for kind in matrix.KINDS}
    captured.update(schema=1,semantic_admission=False,units=units)
    return '\n'.join(units[kind]['marker'] for kind in matrix.KINDS)
