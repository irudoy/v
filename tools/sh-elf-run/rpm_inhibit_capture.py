"""Raw bounded rpm-inhibit observations inside the original complete primary."""

import hashlib
import json
from pathlib import Path

from kb import rpm_inhibit_contract as contract, rpm_inhibit_matrix as matrix

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parents[1]
REGION = 'jk08a-rpm-inhibit-paths'
HEADER = 'rpm-inhibit-path-cases.h'
HARNESS = 'harness-rpm-inhibit-paths.c'
OBSERVER = 'stock_ignition_consumer_invoke.s'
PREFIX = 'kb-rpm-inhibit-observation '
CAPTURE_LIMIT = 1200
SOURCES = ('stock_jk08a_rpm_inhibit_callers.s', 'stock_jk08a_vehicle_speed_fuel_cut.s', 'stock_jk08a_main_rpm_fuel_cut.s', 'stock_jk08a_rpm_summary_leaves.s', 'stock_jk08a_composite_rpm_inhibit.s', 'stock_jk08a_diagnostic_fault_sentinel.s', 'stock_jk08a_implicit_byte_curve.s', 'publication_inhibit_snapshot_return.s')


def sha(value):
    return hashlib.sha256(value).hexdigest()


def declaration(target):
    if target.rom!='JK08A':
        raise ValueError('the rpm-inhibit capture requires the canonical owned JK08A image')
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
    lines=['/* Explicit bounded contributor path inputs; no expected outputs. */',
        '#define RPM_INHIBIT_REGION '+json.dumps(REGION),
        'static const uint8_t rpm_inhibit_stock_calibrations[] = {']
    for at,size in matrix.calibration_spans(declared['source']):
        lines.append('    '+','.join(f'0x{value:02x}U' for value in image[at:at+size])+',')
    lines.extend(('};','static const struct path_case rpm_inhibit_cases[] = {'))
    for case in declared['cases']:
        values=(matrix.KINDS.index(case['kind']),*(case[key] for key in matrix.FIELDS))
        lines.append('    {'+','.join(f'0x{value:x}U' for value in values)+'},')
    return '\n'.join((*lines,'};','')).encode()


def region(unit,region_type):
    spans=unit['code']
    return region_type(key=unit['id'],rom='JK08A',source=Path(unit['assembly']).name,harness=HARNESS,
        start=spans[0]['start'],end=spans[0]['end'],
        callees=tuple((row['start'],row['end']) for row in spans[1:]),
        pools=tuple((row['address'],row['size']) for row in unit['pools']),
        ram_literals=tuple(row['address'] for row in unit['aliases']),cases=1,boundary=False)


def _objects(pairs):
    result={}
    for key,value in pairs:
        if key in result:
            raise ValueError('the rpm-inhibit original repeats a raw JSON key')
        result[key]=value
    return result


def observe(stdout,declared):
    actual=[json.loads(line[len(PREFIX):],object_pairs_hook=_objects)
            for line in stdout.splitlines() if line.startswith(PREFIX)]
    if len(actual)!=len(declared['cases']):
        raise ValueError('the rpm-inhibit original omits or duplicates a real invocation')
    marker=f'VQ_SH_ELF_RPM_INHIBIT status=PASS region={REGION} cases={len(actual)}'
    if stdout.splitlines().count(marker)!=1:
        raise ValueError('the rpm-inhibit original lacks its unique complete marker')
    return actual,marker


def run(target,directory,captured):
    import verify_map_switching as base
    import verify_stock_code as stock
    from elf_storage_layout import require_separate_storage
    declared=declaration(target)
    image=bytes(target.stock_image.data)
    directory=Path(directory)/REGION
    directory.mkdir(); private=directory/'consumed'; private.mkdir()
    sources=(HARNESS,OBSERVER,*SOURCES)
    consumed={name:(TOOL_DIR/name).read_bytes() for name in sources}
    consumed[HEADER]=header(declared,image)
    for name,data in consumed.items():(private/name).write_bytes(data)
    reconstruction=[]
    for index,unit in enumerate(declared['source']['unit']):
        selected=region(unit,stock.Region)
        unit_directory=directory/f'unit-{index}'
        unit_directory.mkdir()
        actual={}
        stock.require_reconstruction(selected,image,unit_directory,source_path=private/selected.source,captured=actual)
        reconstruction.append(dict(unit=unit['id'],source=unit['assembly'],**actual))
    fixture=bytearray(image);aliases=[]
    for address,original in sorted(contract.ALIASES.items()):
        alias=0x01000000+(original&65535)
        fixture[address:address+4]=alias.to_bytes(4,'big')
        aliases.append(dict(address=address,original=original,alias=alias))
    stub_reconstruction=[]
    for index,row in enumerate(contract.BOUNDARIES):
        start=row['address'];source=Path(row['source']).name
        stem=directory/f'return-{index}'
        base.run_command([base.AS,'--big','--isa=sh2e','-o',stem.with_suffix('.o'),private/source])
        base.run_command([base.LD,'-EB',f'-Ttext={start:#x}','-o',stem.with_suffix('.elf'),stem.with_suffix('.o')])
        base.run_command([base.OBJCOPY,'-O','binary','--only-section=.text',stem.with_suffix('.elf'),stem.with_suffix('.bin')])
        data=stem.with_suffix('.bin').read_bytes()
        if (data!=bytes.fromhex(row['bytes'])
                or any(first<start+len(data) and start<last for first,last in contract.SPANS)):
            raise ValueError('the bounded RPM observing return changes tested instructions or declared return bytes')
        fixture[start:start+len(data)]=data
        stub_reconstruction.append(dict(address=start,bytes=data.hex(),
            object_sha256=sha(stem.with_suffix('.o').read_bytes()),
            elf_sha256=sha(stem.with_suffix('.elf').read_bytes()),source_sha256=sha(consumed[source])))
    for start,end in contract.SPANS:
        if fixture[start:end]!=image[start:end]:
            raise ValueError('the bounded RPM fixture changes tested stock instructions')
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
    executable=elf.read_bytes()
    simulator=[base.RUN,'--memory-region=0x01000000,64k',str(elf)]
    result=base.run_command(simulator,timeout=CAPTURE_LIMIT)
    if fixture_path.read_bytes()!=fixture or elf.read_bytes()!=executable:
        raise ValueError('the rpm-inhibit actual fixture or executable changes during execution')
    for name in sources:
        if (TOOL_DIR/name).read_bytes()!=consumed[name] or (private/name).read_bytes()!=consumed[name]:
            raise ValueError('the bounded RPM consumed source changes during execution')
    actual,marker=observe(result.stdout,declared)
    captured.update(schema=1,declaration=declared,semantic_admission=False,
        consumed={name:data.hex() for name,data in consumed.items()},reconstruction=reconstruction,
        image_sha256=sha(image),fixture_sha256=sha(fixture),elf_sha256=sha(executable),
        observer_object_sha256=sha(observer.read_bytes()),aliases=aliases,boundaries=list(contract.BOUNDARIES),
        stub_reconstruction=stub_reconstruction,
        command=[str(value) for value in command],
        simulator=dict(command=simulator,returncode=result.returncode,timeout_seconds=CAPTURE_LIMIT),
        stdout=result.stdout,stderr=result.stderr,stdout_sha256=sha(result.stdout.encode()),
        stderr_sha256=sha(result.stderr.encode()),observations=actual,marker=marker,
        toolchain=stock.can_latch_copy.toolchain())
    return marker
