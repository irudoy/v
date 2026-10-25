"""Raw stock bank-pulse-stage observations inside the existing complete COPY primary."""

import hashlib
import json
from pathlib import Path

from kb import bank_pulse_stage_contract as contract,bank_pulse_stage_matrix as matrix

TOOL_DIR=Path(__file__).resolve().parent
ROOT=TOOL_DIR.parent.parent
REGION='jk08a-bank-pulse-stages'
HEADER='bank-pulse-stage-cases.h'
HARNESS='harness-bank-pulse-stages.c'
OBSERVER='stock_ignition_consumer_invoke.s'
PREFIX='kb-bank-pulse-stage-observation '
CAPTURE_LIMIT=1200
SOURCES=('stock_jk08a_pulse_precursor.s','stock_jk08a_channel_pulse.s',
         'pulse-precursor-cases.h','channel-pulse-cases.h')


def sha(data):
    return hashlib.sha256(data).hexdigest()


def declaration(target):
    if target.rom!='JK08A':
        raise ValueError('the bank-pulse-stage capture requires the owned JK08A image')
    source=contract.descriptor(ROOT)
    image=bytes(target.stock_image.data)
    contract.require_image(source,image)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',
        descriptor_sha256=sha((ROOT/contract.DESCRIPTOR).read_bytes()),source=source,
        cases=list(matrix.cases(source,image,root=ROOT)),calibration_spans=[list(row) for row in matrix.calibration_spans(source)],semantic_admission=False,
        native_geometry_inference=False,caller_argument_inference=False,datum_identity_inference=False,
        automatic_resolution=False,natural_caller_reachability=False,hardware_qualification=False)


def header(declared,image):
    spans=matrix.calibration_spans(declared['source']);size=sum(width for at,width in spans)
    lines=['/* Explicit stage inputs; no expected outputs, GPRs or frame state. */',
           '#define BANK_PULSE_STAGE_REGION '+json.dumps(REGION),
           f'#define BANK_PULSE_STAGE_CALIBRATION_SIZE {size}U',
           'static const uint32_t bank_pulse_stage_calibration_starts[] = {'+
           ','.join(f'0x{at:x}U' for at,width in spans)+'};',
           'static const uint32_t bank_pulse_stage_calibration_sizes[] = {'+
           ','.join(f'{width}U' for at,width in spans)+'};',
           'struct path_case {',
           '    uint32_t kind,'+','.join(matrix.FIELDS)+';',
           '    struct context context;',
           '    uint8_t calibration[BANK_PULSE_STAGE_CALIBRATION_SIZE];',
           '};',
           'static const struct path_case bank_pulse_stage_cases[] = {']
    for case in declared['cases']:
        values=','.join(f'0x{value:x}U' for value in (matrix.KINDS.index(case['kind']),*(case[key] for key in matrix.FIELDS)))
        context=matrix.context(declared['source'],case)
        registers=','.join(f'0x{value:x}U' for value in context[:15])
        tail=','.join(f'0x{value:x}U' for value in context[15:])
        calibration=matrix.calibrations(declared['source'],image,case)
        data=b''.join(calibration[at] for at,width in spans)
        raw=','.join(f'0x{value:02x}U' for value in data)
        lines.append('    {'+values+',{{'+registers+'},'+tail+'},{'+raw+'}},')
    return '\n'.join((*lines,'};','')).encode()


def observe(stdout,declared):
    rows=[json.loads(line[len(PREFIX):]) for line in stdout.splitlines() if line.startswith(PREFIX)]
    marker=f'VQ_SH_ELF_BANK_PULSE_STAGES status=PASS region={REGION} cases={len(declared["cases"])}'
    if len(rows)!=len(declared['cases']) or stdout.splitlines().count(marker)!=1:
        raise ValueError('the bank-pulse-stage capture lacks its unique complete raw invocation set')
    return rows,marker


def run(target,directory,captured):
    import verify_map_switching as base
    import verify_stock_code as stock
    from elf_storage_layout import require_separate_storage
    declared=declaration(target);image=bytes(target.stock_image.data)
    directory=Path(directory)/REGION;directory.mkdir()
    private=directory/'consumed';private.mkdir()
    consumed={name:(TOOL_DIR/name).read_bytes() for name in (HARNESS,OBSERVER,*SOURCES)}
    consumed[HEADER]=header(declared,image)
    for name,data in consumed.items():(private/name).write_bytes(data)
    reconstruction=[]
    for index,unit in enumerate(declared['source']['unit']):
        first,*rest=unit['code'];source=Path(unit['assembly']).name
        unit_directory=directory/f'unit-{index}';unit_directory.mkdir()
        selected=stock.Region(key=unit['id'],rom='JK08A',source=source,harness=HARNESS,
            start=first['start'],end=first['end'],callees=tuple((row['start'],row['end']) for row in rest),
            pools=tuple((row['address'],row['size']) for row in unit['pools']),
            ram_literals=tuple(row['address'] for row in unit['pools'] if row['RAM_pointer_alias']),cases=1,boundary=False)
        actual={}
        stock.require_reconstruction(selected,image,unit_directory,source_path=private/source,captured=actual)
        reconstruction.append(dict(unit=unit['id'],source=unit['assembly'],**actual))
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    observer=directory/'invoke.o'
    base.run_command([base.AS,'--big','--isa=sh2e','-o',observer,private/OBSERVER])
    fixture_path,rom_object=directory/'fixture.bin',directory/'fixture.o'
    fixture_path.write_bytes(fixture)
    base.run_command([base.OBJCOPY,'-I','binary','-O','elf32-sh','-B','sh',
        '--rename-section','.data=.rom,alloc,load,code,data,contents',fixture_path,rom_object])
    elf=directory/'harness.elf'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',private,
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',elf,private/HARNESS,observer,rom_object]
    base.run_command(command,timeout=120)
    require_separate_storage(elf,((matrix.RAM_BASE,matrix.RAM_SIZE),))
    executable=elf.read_bytes();simulator=[base.RUN,'--memory-region=0x01000000,64k',str(elf)]
    result=base.run_command(simulator,timeout=CAPTURE_LIMIT)
    if fixture_path.read_bytes()!=fixture or elf.read_bytes()!=executable:
        raise ValueError('the bank-pulse-stage fixture or executable changes during capture')
    for name in (HARNESS,OBSERVER,*SOURCES):
        if (TOOL_DIR/name).read_bytes()!=consumed[name] or (private/name).read_bytes()!=consumed[name]:
            raise ValueError('a bank-pulse-stage executable source changes during capture')
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
