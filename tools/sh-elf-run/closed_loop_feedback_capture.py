"""Raw whole-feedback capture through its unchanged existing observer and assembly."""

import hashlib
import json
from pathlib import Path

from kb import closed_loop_feedback_access_contract as contract,closed_loop_feedback_matrix as matrix

TOOL_DIR=Path(__file__).resolve().parent
ROOT=TOOL_DIR.parents[1]
REGION='jk08a-closed-loop-feedback-paths'
HEADER='closed-loop-feedback-path-cases.h'
HARNESS='harness-closed-loop-feedback-paths.c'
OBSERVER='invoke-closed-loop-feedback.s'
PREFIX='kb-closed-loop-feedback-observation '
CAPTURE_LIMIT=1200


def sha(data):
    return hashlib.sha256(data).hexdigest()


def declaration(target):
    if target.rom!='JK08A':raise ValueError('the feedback capture requires the owned JK08A image')
    source=contract.descriptor(ROOT);image=bytes(target.stock_image.data)
    contract.require_image(source,image)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',
        descriptor_sha256=sha((ROOT/contract.DESCRIPTOR).read_bytes()),source=source,
        cases=list(matrix.cases(source,image,root=ROOT)),
        calibration_spans=[[row['address'],row['size']] for row in contract.CONTROLLED_CALIBRATION],
        bound_spans=[[row['address'],row['size']] for row in contract.BOUND_SPANS],
        semantic_admission=False,native_geometry_inference=False,physical_callee_reader_inference=False,
        automatic_resolution=False,natural_scheduling_inference=False,hardware_qualification=False)


def header(declared,image):
    changes=[];rows=[]
    for case in declared['cases']:
        begin=len(changes);changes.extend(case['changes'])
        context=matrix.context(declared['source'],case)
        registers=','.join(f'0x{value:x}U' for value in context[:15])
        tail=','.join(f'0x{value:x}U' for value in context[15:])
        calibration=matrix.calibrations(declared['source'],image,case)
        values=b''.join(calibration[row['address']] for row in contract.CONTROLLED_CALIBRATION)
        prefix=(int(case['kind']=='controlled'),case['entry'],case['zero'],case['seed_index'],begin,len(case['changes']))
        rows.append('    {'+','.join(f'0x{value:x}U' for value in prefix)+',{{'+registers+'},'+tail+'},{'+
            ','.join(f'0x{value:02x}U' for value in values)+'}},')
    lines=['/* Complete explicit feedback inputs; no expected outputs or terminal values. */',
        '#define FEEDBACK_REGION '+json.dumps(REGION),
        f'#define FEEDBACK_BOUND_SIZE {sum(row["size"] for row in contract.BOUND_SPANS)}U',
        'static const struct span feedback_bound[] = {'+
        ','.join('{'+f'0x{row["address"]:x}U,{row["size"]}U'+'}' for row in contract.BOUND_SPANS)+'};',
        'static const struct span feedback_controlled[] = {'+
        ','.join('{'+f'0x{row["address"]:x}U,{row["size"]}U'+'}' for row in contract.CONTROLLED_CALIBRATION)+'};',
        'static const struct change feedback_changes[] = {',
        *('    {'+f'0x{at:x}U,0x{value:x}U'+'},' for at,value in changes),
        '};','static const struct path_case feedback_cases[] = {',*rows,'};','']
    return '\n'.join(lines).encode()


def region(region_type):
    first,*rest=contract.UNIT['code']
    return region_type(key=REGION,rom='JK08A',source=Path(contract.UNIT['assembly']).name,harness=HARNESS,
        start=first['start'],end=first['end'],callees=tuple((row['start'],row['end']) for row in rest),
        pools=tuple((row['address'],row['size']) for row in contract.UNIT['pools']),
        ram_literals=tuple(row['address'] for row in contract.UNIT['aliases'] if row['width']==4),
        cases=1,boundary=False)


def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('the feedback original repeats a raw JSON key')
        result[key]=value
    return result


def observe(stdout,declared):
    rows=[json.loads(line[len(PREFIX):],object_pairs_hook=_objects)
        for line in stdout.splitlines() if line.startswith(PREFIX)]
    marker=f'VQ_SH_ELF_CLOSED_LOOP_FEEDBACK status=PASS region={REGION} cases={len(declared["cases"])}'
    if len(rows)!=len(declared['cases']) or stdout.splitlines().count(marker)!=1:
        raise ValueError('the feedback capture lacks its unique complete raw invocation set')
    return rows,marker


def run(target,directory,captured):
    import verify_map_switching as base
    import verify_stock_code as stock
    from elf_storage_layout import require_separate_storage
    declared=declaration(target);image=bytes(target.stock_image.data)
    directory=Path(directory)/REGION;directory.mkdir();private=directory/'consumed';private.mkdir()
    source=Path(contract.UNIT['assembly']).name
    sources=(HARNESS,OBSERVER,source,Path(matrix.INPUT_SOURCE).name)
    consumed={name:(TOOL_DIR/name).read_bytes() for name in sources};consumed[HEADER]=header(declared,image)
    for name,data in consumed.items():(private/name).write_bytes(data)
    reconstruction={}
    stock.require_reconstruction(region(stock.Region),image,directory,source_path=private/source,captured=reconstruction)
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    observer=directory/'invoke.o'
    base.run_command([base.AS,'--big','--isa=sh2e','-o',observer,private/OBSERVER])
    fixture_path,rom_object=directory/'fixture.bin',directory/'fixture.o';fixture_path.write_bytes(fixture)
    base.run_command([base.OBJCOPY,'-I','binary','-O','elf32-sh','-B','sh',
        '--rename-section','.data=.rom,alloc,load,code,data,contents',fixture_path,rom_object])
    elf=directory/'harness.elf'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',private,
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',elf,private/HARNESS,observer,rom_object]
    base.run_command(command,timeout=120)
    # The shared low workspace is the existing writable part of the fixture image.
    require_separate_storage(elf,((matrix.RAM_BASE,matrix.RAM_SIZE),))
    executable=elf.read_bytes();simulator=[base.RUN,'--memory-region=0x01000000,64k',str(elf)]
    result=base.run_command(simulator,timeout=CAPTURE_LIMIT)
    if fixture_path.read_bytes()!=fixture or elf.read_bytes()!=executable:
        raise ValueError('the feedback fixture or executable changes during capture')
    for name in sources:
        if (TOOL_DIR/name).read_bytes()!=consumed[name] or (private/name).read_bytes()!=consumed[name]:
            raise ValueError('a feedback consumed source changes during capture')
    actual,marker=observe(result.stdout,declared)
    captured.update(schema=1,declaration=declared,semantic_admission=False,
        consumed={name:data.hex() for name,data in consumed.items()},reconstruction=reconstruction,
        image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=sha(executable),
        observer_object_sha256=sha(observer.read_bytes()),aliases=aliases,
        command=[str(value) for value in command],
        simulator=dict(command=simulator,returncode=result.returncode,timeout_seconds=CAPTURE_LIMIT),
        stdout=result.stdout,stderr=result.stderr,stdout_sha256=sha(result.stdout.encode()),
        stderr_sha256=sha(result.stderr.encode()),observations=actual,marker=marker,
        toolchain=stock.can_latch_copy.toolchain())
    return marker
