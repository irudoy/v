"""Raw complete third-trim word writer under the existing complete GNU primary."""
import hashlib,json
from pathlib import Path
from kb import third_trim_word_writer_contract as contract,third_trim_word_writer_matrix as matrix

TOOL_DIR=Path(__file__).resolve().parent
ROOT=TOOL_DIR.parent.parent
REGION='jk08a-third-trim-word-writer-paths'
HEADER='third-trim-word-writer-cases.h'
HARNESS='harness-third-trim-word-writer-paths.c'
OBSERVER='stock_ignition_consumer_invoke.s'
PREFIX='kb-third-trim-word-writer-observation '
MARKER='VQ_SH_ELF_THIRD_TRIM_WORD_WRITER'
CAPTURE_LIMIT=1200

def sha(raw):return hashlib.sha256(raw).hexdigest()

def declaration(target):
    if target.rom!='JK08A':raise ValueError('the third-trim word writer capture requires the complete owned image')
    source=contract.descriptor(ROOT);image=bytes(target.stock_image.data);contract.require_image(source,image)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',source=source,
        descriptor_sha256=sha((ROOT/contract.DESCRIPTOR).read_bytes()),cases=list(matrix.cases(source,image)),
        calibration_spans=[[r['address'],r['size']] for r in contract.CONTROLLED_CALIBRATION],
        bound_spans=[[r['address'],r['size']] for r in contract.BOUND_SPANS],
        semantic_admission=False,native_geometry_inference=False,natural_caller_reachability=False,
        natural_scheduling_inference=False,hardware_qualification=False)

def header(declared,image):return matrix.header(declared,image)

def observe(stdout,declared):
    rows=[json.loads(line[len(PREFIX):]) for line in stdout.splitlines() if line.startswith(PREFIX)]
    count=len(declared['cases']);marker=f'{MARKER} status=PASS region={REGION} cases={count}'
    if len(rows)!=count or stdout.splitlines().count(marker)!=1:
        raise ValueError('the third-trim word writer capture omits its complete raw ordered natural-entry stream')
    return rows,marker

def run(target,directory,captured):
    import verify_map_switching as base
    import verify_stock_code as stock
    from elf_storage_layout import require_separate_storage
    declared=declaration(target);image=bytes(target.stock_image.data)
    directory=Path(directory)/REGION;directory.mkdir();private=directory/'consumed';private.mkdir()
    source=Path(contract.UNIT['assembly']).name;names=(HARNESS,OBSERVER,source)
    consumed={name:(TOOL_DIR/name).read_bytes() for name in names};consumed[HEADER]=header(declared,image)
    for name,raw in consumed.items():(private/name).write_bytes(raw)
    first,*rest=contract.UNIT['code']
    region=stock.Region(key=REGION,rom='JK08A',source=source,harness=HARNESS,
        start=first['start'],end=first['end'],callees=tuple((r['start'],r['end']) for r in rest),
        pools=tuple((r['address'],r['size']) for r in contract.UNIT['pools']),
        ram_literals=tuple(r['address'] for r in contract.UNIT['aliases']),cases=1,boundary=False)
    reconstruction={};stock.require_reconstruction(region,image,directory,source_path=private/source,captured=reconstruction)
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    observer=directory/'invoke.o';base.run_command([base.AS,'--big','--isa=sh2e','-o',observer,private/OBSERVER])
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
        raise ValueError('the third-trim word writer executable or prepared fixture changes during capture')
    for name in names:
        if (TOOL_DIR/name).read_bytes()!=consumed[name] or (private/name).read_bytes()!=consumed[name]:
            raise ValueError('the third-trim word writer capture changes a complete consumed executable source')
    actual,marker=observe(result.stdout,declared)
    captured.update(schema=1,declaration=declared,semantic_admission=False,
        consumed={name:raw.hex() for name,raw in consumed.items()},reconstruction=reconstruction,
        image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=sha(executable),
        observer_object_sha256=sha(observer.read_bytes()),aliases=aliases,boundaries=[],return_reconstruction=[],
        command=[str(v) for v in command],simulator=dict(command=simulator,returncode=result.returncode,timeout_seconds=CAPTURE_LIMIT),
        stdout=result.stdout,stderr=result.stderr,stdout_sha256=sha(result.stdout.encode()),
        stderr_sha256=sha(result.stderr.encode()),observations=actual,marker=marker,
        toolchain=stock.can_latch_copy.toolchain())
    return marker
