"""Actual registered coherent-prefix and full comparator capture in the shared GNU primary."""
import hashlib,json
from pathlib import Path
from kb import pedal_snapshot_high_state_contract as contract,pedal_snapshot_high_state_matrix as matrix

TOOL_DIR=Path(__file__).resolve().parent
ROOT=TOOL_DIR.parent.parent
REGION='jk08a-pedal-snapshot-high-state-paths'
HEADER='pedal-snapshot-high-state-cases.h'
HARNESS='harness-pedal-snapshot-high-state-paths.c'
OBSERVER='stock_ignition_consumer_invoke.s'
SNAPSHOT_OBSERVER='stock_injection_start_delay_invoke.s'
PREFIX='kb-pedal-snapshot-high-state-observation '
MARKER='VQ_SH_ELF_PEDAL_SNAPSHOT_HIGH_STATE'
CAPTURE_LIMIT=1200


def sha(raw):return hashlib.sha256(raw).hexdigest()


def declaration(target):
    if target.rom!='JK08A':raise ValueError('the paired pedal capture requires the complete owned image')
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
        raise ValueError('the paired pedal capture omits a complete ordered raw pair or its terminal')
    return rows,marker


def run(target,directory,captured):
    import verify_map_switching as base
    import verify_stock_code as stock
    from elf_storage_layout import require_separate_storage
    declared=declaration(target);image=bytes(target.stock_image.data)
    directory=Path(directory)/REGION;directory.mkdir();private=directory/'consumed';private.mkdir()
    own_source=Path(contract.UNIT['assembly']).name;snapshot_source=Path(contract.SNAPSHOT['assembly']).name
    names=(HARNESS,OBSERVER,SNAPSHOT_OBSERVER,own_source,snapshot_source)
    consumed={name:(TOOL_DIR/name).read_bytes() for name in names};consumed[HEADER]=header(declared,image)
    for name,raw in consumed.items():(private/name).write_bytes(raw)
    first,*rest=contract.UNIT['code'];reconstruction={}
    comparator=stock.Region(key=REGION+'-comparator',rom='JK08A',source=own_source,harness=HARNESS,
        start=first['start'],end=first['end'],callees=tuple((r['start'],r['end']) for r in rest),
        pools=tuple((r['address'],r['size']) for r in contract.UNIT['pools']),
        ram_literals=tuple(r['address'] for r in contract.UNIT['aliases']),cases=1,boundary=False)
    snapshot=next(region for region in stock.REGIONS if region.key==contract.SNAPSHOT['key'])
    if (snapshot.code_spans!=tuple((r['start'],r['end']) for r in contract.SNAPSHOT['code'])
            or snapshot.source!=snapshot_source
            or snapshot.pools!=tuple((r['address'],r['size']) for r in contract.SNAPSHOT['pools'])
            or stock.return_stub(snapshot)!=bytes.fromhex(contract.SNAPSHOT['boundary']['bytes'])):
        raise ValueError('the paired pedal capture changes its exact existing registered snapshot region')
    for name,region,source in (('comparator',comparator,own_source),('snapshot',snapshot,snapshot_source)):
        value={};stock.require_reconstruction(region,image,directory,source_path=private/source,captured=value)
        reconstruction[name]=value
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    observer_objects=[]
    for source,output in ((OBSERVER,'invoke.o'),(SNAPSHOT_OBSERVER,'snapshot-invoke.o')):
        obj=directory/output;base.run_command([base.AS,'--big','--isa=sh2e','-o',obj,private/source]);observer_objects.append(obj)
    fixture_path,rom_object=directory/'fixture.bin',directory/'fixture.o';fixture_path.write_bytes(fixture)
    base.run_command([base.OBJCOPY,'-I','binary','-O','elf32-sh','-B','sh',
        '--rename-section','.data=.rom,alloc,load,code,data,contents',fixture_path,rom_object])
    elf=directory/'harness.elf'
    command=[base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror','-I',private,
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',elf,private/HARNESS,*observer_objects,rom_object]
    base.run_command(command,timeout=120);require_separate_storage(elf,((matrix.RAM_BASE,matrix.RAM_SIZE),))
    executable=elf.read_bytes();simulator=[base.RUN,'--memory-region=0x01000000,64k',str(elf)]
    result=base.run_command(simulator,timeout=CAPTURE_LIMIT)
    if fixture_path.read_bytes()!=fixture or elf.read_bytes()!=executable:
        raise ValueError('the paired pedal executable or prepared fixture changes during capture')
    for name in names:
        if (TOOL_DIR/name).read_bytes()!=consumed[name] or (private/name).read_bytes()!=consumed[name]:
            raise ValueError('the paired pedal capture changes a complete consumed executable source')
    actual,marker=observe(result.stdout,declared)
    captured.update(schema=1,declaration=declared,semantic_admission=False,
        consumed={name:raw.hex() for name,raw in consumed.items()},reconstruction=reconstruction,
        image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=sha(executable),
        observer_object_sha256={path.name:sha(path.read_bytes()) for path in observer_objects},aliases=aliases,
        boundaries=[dict(address=contract.SNAPSHOT['boundary']['address'],bytes=contract.SNAPSHOT['boundary']['bytes'])],
        return_reconstruction=[],command=[str(v) for v in command],
        simulator=dict(command=simulator,returncode=result.returncode,timeout_seconds=CAPTURE_LIMIT),
        stdout=result.stdout,stderr=result.stderr,stdout_sha256=sha(result.stdout.encode()),
        stderr_sha256=sha(result.stderr.encode()),observations=actual,marker=marker,
        toolchain=stock.can_latch_copy.toolchain())
    return marker
