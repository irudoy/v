"""Raw stock maf-record observations inside the existing complete COPY primary."""

import hashlib
import json
from pathlib import Path

from kb import proof_adapter,proof_transport

from kb import maf_record_contract as contract,maf_record_matrix as matrix

TOOL_DIR=Path(__file__).resolve().parent
ROOT=TOOL_DIR.parent.parent
REGION='jk08a-maf-record-paths'
HEADER='maf-record-cases.h'
HARNESS='harness-maf-record.c'
OBSERVER='stock_ignition_consumer_invoke.s'
RETURN='publication_inhibit_snapshot_return.s'
PREFIX='kb-maf-record-observation '
CAPTURE_LIMIT=1200


def sha(data):
    return hashlib.sha256(data).hexdigest()


def declaration(target):
    if target.rom!='JK08A':
        raise ValueError('the maf-record capture requires the owned JK08A image')
    source=contract.descriptor(ROOT)
    proof_adapter.require_generated(ROOT,contract.DESCRIPTOR)
    image=bytes(target.stock_image.data)
    contract.require_image(source,image)
    return dict(schema=1,region=REGION,layout='7mfk',rom='JK08A',
        descriptor_sha256=sha((ROOT/contract.DESCRIPTOR).read_bytes()),source=source,
        cases=list(matrix.cases(source,image)),calibration_spans=[[row['address'],row['size']] for row in contract.POOLS],semantic_admission=False,
        native_geometry_inference=False,caller_argument_inference=False,datum_identity_inference=False,
        automatic_resolution=False,natural_caller_reachability=False,hardware_qualification=False)


def header(declared,image):
    return proof_adapter.header(declared['source']['adapter'],declared['cases'],
        lambda case: matrix.context(declared['source'],case),
        None)


def observe(stdout,declared):
    rows=[json.loads(line[len(PREFIX):]) for line in stdout.splitlines() if line.startswith(PREFIX)]
    marker=f'VQ_SH_ELF_MAF_RECORD status=PASS region={REGION} cases={len(declared["cases"])}'
    if len(rows)!=len(declared['cases']) or stdout.splitlines().count(marker)!=1:
        raise ValueError('the maf-record capture lacks its unique complete raw invocation set')
    return rows,marker


def run(target,directory,captured):
    import verify_map_switching as base
    import verify_stock_code as stock
    from elf_storage_layout import require_separate_storage
    declared=declaration(target);image=bytes(target.stock_image.data)
    directory=Path(directory)/REGION;directory.mkdir()
    private=directory/'consumed';private.mkdir()
    source=Path(contract.ASSEMBLY).name
    consumed={name:(TOOL_DIR/name).read_bytes() for name in (HARNESS,OBSERVER,source,RETURN)}
    consumed[HEADER]=header(declared,image)
    for name,data in consumed.items():(private/name).write_bytes(data)
    first,*rest=contract.WINDOWS
    selected=stock.Region(key=REGION,rom='JK08A',source=source,harness=HARNESS,
        start=first['start'],end=first['end'],callees=tuple((row['start'],row['end']) for row in rest),
        pools=tuple((row['address'],row['size']) for row in contract.POOLS),ram_literals=tuple(contract.ALIASES),cases=1,boundary=False)
    reconstruction={}
    stock.require_reconstruction(selected,image,directory,source_path=private/source,captured=reconstruction)
    fixture,aliases=contract.independent_fixture(declared['source'],image)
    boundary=contract.BOUNDARY;stem=directory/'return'
    base.run_command([base.AS,'--big','--isa=sh2e','-o',stem.with_suffix('.o'),private/RETURN])
    base.run_command([base.LD,'-EB',f'-Ttext={boundary["address"]:#x}','-o',stem.with_suffix('.elf'),stem.with_suffix('.o')])
    base.run_command([base.OBJCOPY,'-O','binary','--only-section=.text',stem.with_suffix('.elf'),stem.with_suffix('.bin')])
    data=stem.with_suffix('.bin').read_bytes()
    if data!=bytes.fromhex(boundary['bytes']):raise ValueError('the MAF record reader observing return changes independent bytes')
    returns=[dict(address=boundary['address'],bytes=data.hex(),source_sha256=sha(consumed[RETURN]),
        object_sha256=sha(stem.with_suffix('.o').read_bytes()),elf_sha256=sha(stem.with_suffix('.elf').read_bytes()))]
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
        raise ValueError('the maf-record fixture or executable changes during capture')
    for name in (HARNESS,OBSERVER,source,RETURN):
        if (TOOL_DIR/name).read_bytes()!=consumed[name] or (private/name).read_bytes()!=consumed[name]:
            raise ValueError('a maf-record executable source changes during capture')
    actual,marker=observe(result.stdout,declared)
    captured.update(schema=1,declaration=declared,semantic_admission=False,
        consumed={name:data.hex() for name,data in consumed.items()},reconstruction=reconstruction,
        image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=sha(executable),
        observer_object_sha256=sha(observer.read_bytes()),aliases=aliases,boundaries=returns,
        command=[str(value) for value in command],
        simulator=dict(command=simulator,returncode=result.returncode,timeout_seconds=CAPTURE_LIMIT),
        stdout=result.stdout,stderr=result.stderr,stdout_sha256=sha(result.stdout.encode()),
        stderr_sha256=sha(result.stderr.encode()),observations=actual,marker=marker,
        toolchain=stock.can_latch_copy.toolchain())
    return marker
