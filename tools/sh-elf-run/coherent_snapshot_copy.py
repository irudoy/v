"""Bounded coherent caller capture through the existing GNU stock primitives."""
import ast
import hashlib
import json
from pathlib import Path
import re
import sys

TOOL_DIR=Path(__file__).resolve().parent
ROOT=TOOL_DIR.parents[1]
sys.path.insert(0,str(ROOT/'tools/kb/src'))
from kb import coherent_copy_evidence as proof, coherent_copy_matrix as matrix

PREFIX='kb-coherent-copy-observation '
HARNESS='tools/sh-elf-run/harness-coherent-copy-capture.c'
OBSERVER='tools/sh-elf-run/stock_injection_start_delay_invoke.s'
HEADER='tools/sh-elf-run/coherent-copy-cases.h'

def _object(pairs):
    result={}
    for key,value in pairs:
        if key in result:raise ValueError('duplicate coherent observation key')
        result[key]=value
    return result

def _array(text,name):
    body,=re.findall(r'\b'+re.escape(name)+r'\[\] = (\{.*?\});',text,re.S)
    body=re.sub(r'(0x[0-9a-f]+|\d+)U\b',r'\1',body)
    return ast.literal_eval(body.replace('{','[').replace('}',']'))

def validate_header(text,descriptor):
    canonical=matrix.render_header([[p['address'] for p in row['pool']] for row in descriptor['window']])
    if text!=canonical:
        raise ValueError('the consumed coherent C header differs from its complete canonical bytes')
    expected=[];windows=[];read=[];pools=[];early=[]
    for window,row in zip(matrix.WINDOWS,descriptor['window']):
        cases=matrix.cases(window);addresses=matrix.read_addresses(window)
        selected=proof.early_indices(window);context=[0]*15
        for register,value in window.context:context[register]=value
        mask=sum(1<<register for register,_ in window.context)
        windows.append([window.entry,window.call,window.helper,window.source,window.destination,
            window.length,mask,context,len(read),len(addresses),len(pools),len(row['pool']),
            len(expected),len(cases),len(early),len(selected)])
        expected.extend([case['index'],case['seed'],case['variant'],case['t'],
                         0xffffffff if case['isolated'] is None else case['isolated'],int(case['carry'])]
                        for case in cases)
        read.extend(addresses);pools.extend(p['address'] for p in row['pool']);early.extend(selected)
    for name,value in (('coherent_cases',expected),('coherent_windows',windows),
        ('coherent_read_addresses',read),('coherent_pool_addresses',pools),('coherent_early_indices',early)):
        if _array(text,name)!=value:
            raise ValueError('the consumed coherent C inputs change: '+name)
    for name,value in (('WINDOW',len(matrix.WINDOWS)),('CASE',len(expected)),('EARLY',len(early))):
        if text.splitlines().count(f'#define COHERENT_{name}_COUNT {value}U')!=1:
            raise ValueError('the consumed coherent C count changes')

def snapshot(root,directory):
    descriptor=proof.descriptor(root)
    names=[proof.DESCRIPTOR,HARNESS,OBSERVER,HEADER]
    names.extend(row['assembly'] for row in descriptor['window'])
    consumed={name:(root/name).read_bytes() for name in names}
    validate_header(consumed[HEADER].decode('utf-8'),descriptor)
    private=directory/'coherent-copy-consumed'
    for name,data in consumed.items():
        target=private/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    return dict(descriptor=descriptor,consumed=consumed,source_dir=private/'tools/sh-elf-run')

def observe(stdout,window,row,*,early=False):
    actual=[json.loads(line[len(PREFIX):],object_pairs_hook=_object)
            for line in stdout.splitlines() if line.startswith(PREFIX)]
    cases=matrix.cases(window)
    indices=proof.early_indices(window) if early else range(len(cases))
    if len(actual)!=len(indices):raise ValueError('the original coherent execution omits or duplicates cases')
    pools=b''.join(matrix.alias(p['value']).to_bytes(4,'big') for p in row['pool'])
    memory=None
    for index,value in zip(indices,actual):
        memory=matrix.validate_observation(window,cases[index],value,pools,memory)
    marker=f'VQ_SH_ELF_COHERENT_COPY_CAPTURE call={window.call:08x} cases={len(actual)} early='+('true' if early else 'false')
    if stdout.splitlines().count(marker)!=1:
        raise ValueError('the original coherent capture lacks its unique complete marker')
    return actual

def region(window,row,*,early=False,region_type=None):
    if region_type is None:
        import verify_stock_code as stock
        region_type=stock.Region
    return region_type(key=row['key'],rom='JK08A',source=Path(row['assembly']).name,
        harness=Path(HARNESS).name,start=window.entry,end=window.call+4,
        pools=tuple((p['address'],4) for p in row['pool']),
        ram_literals=tuple(p['address'] for p in row['pool'] if p['value']>=0xffff0000),
        cases=len(proof.early_indices(window)) if early else len(matrix.cases(window)),
        boundary=True,return_address_offset=24,return_register=7,callees=proof.code_spans(window)[1:])

def run_window(index,captured,directory,*,early=False):
    import verify_map_switching as base
    import verify_stock_code as stock
    window=matrix.WINDOWS[index];row=captured['descriptor']['window'][index]
    selected=region(window,row,early=early)
    directory.mkdir()
    source=captured['source_dir'];observer=directory/'coherent-invoke.o'
    base.run_command([base.AS,'--big','--isa=sh2e','-o',observer,source/Path(OBSERVER).name])
    image=stock.stock_image('JK08A');reconstructed={}
    instructions=stock.require_reconstruction(selected,image,directory,
        source_path=source/selected.source,captured=reconstructed)
    fixture=stock.build_fixture(selected,image)
    boundary=stock.return_stub(selected)
    if boundary!=bytes.fromhex('57f6472a000b0009'):
        raise ValueError('the coherent capture return boundary changes')
    fixture_path=directory/'coherent.sim-fixture';fixture_path.write_bytes(fixture)
    rom=directory/'coherent-rom.o'
    base.run_command([base.OBJCOPY,'-I','binary','-O','elf32-sh','-B','sh',
        '--rename-section','.data=.rom,alloc,load,code,data,contents',fixture_path,rom])
    output=directory/'coherent-harness.elf'
    base.run_command([base.GCC,'-m2e','-mb','-std=c11','-O2','-Wall','-Wextra','-Werror',
        f'-DREGION_KEY="{selected.key}"',f'-DWINDOW_INDEX={index}',f'-DEARLY_ONLY={int(early)}',
        f'-Wl,-Ttext-segment={max(base.DRIVER_TEXT_BASE,len(fixture)+0x10000):#x}',
        '-Wl,--section-start=.rom=0','-o',output,source/Path(HARNESS).name,observer,rom],timeout=120)
    stock.require_separate_storage(output,((base.TEST_RAM_BASE,65536),))
    executable=output.read_bytes()
    result=base.run_command([base.RUN,f'--memory-region={base.TEST_RAM_BASE:#x},64k',output],
        timeout=stock.stock_execution_timeout())
    if output.read_bytes()!=executable:raise ValueError('the actual coherent ELF changes during execution')
    marker=f'VQ_SH_ELF_STOCK_CODE status=PASS region={selected.key} cases={selected.cases}'
    if result.stdout.splitlines().count(marker)!=1:
        raise ValueError('the original coherent driver lacks its unique complete marker')
    actual=observe(result.stdout,window,row,early=early)
    if early:print(result.stdout,end='')
    return dict(region=selected.key,cases=matrix.cases(window),observations=actual,
        code=reconstructed['code'],pools=reconstructed['pools'],
        image_sha256=hashlib.sha256(image).hexdigest(),fixture_sha256=hashlib.sha256(fixture).hexdigest(),
        elf_sha256=hashlib.sha256(executable).hexdigest(),
        aliases=[[p['address'],p['value'],matrix.alias(p['value'])] for p in row['pool'] if p['value']>=0xffff0000],
        boundary=dict(address=selected.end,bytes=boundary.hex()),instructions=instructions)

def verify_early():
    import tempfile
    from execution_report import stage
    count=0
    with tempfile.TemporaryDirectory(prefix='vq-coherent-copy-feedback-') as temporary:
        directory=Path(temporary)
        captured=snapshot(ROOT,directory)
        for index,window in enumerate(matrix.WINDOWS):
            with stage(f'feedback:coherent:{window.call:08x}'):
                result=run_window(index,captured,directory/f'{window.call:08x}',early=True)
                count+=len(result['observations'])
    if count!=sum(len(proof.early_indices(window)) for window in matrix.WINDOWS):
        raise ValueError('the coherent feedback omits required observations')
    print(f'VQ_SH_ELF_COHERENT_COPY_SUBSET status=PASS cases={count} production=false')


def regions(region_type):
    """The primary stock registry owns each independently bounded caller."""
    value=proof.descriptor(ROOT)
    return tuple(region(window,row,region_type=region_type)
                 for window,row in zip(matrix.WINDOWS,value['window']))


def run_region(selected,directory,*,capture=None):
    """Route a full primary stock iteration into the shared COPY packet."""
    from can_latch_copy import toolchain
    index,=[i for i,w in enumerate(matrix.WINDOWS) if selected.key==f'jk08a-coherent-{w.call:08x}']
    copied=snapshot(ROOT,directory)
    expected=region(matrix.WINDOWS[index],copied['descriptor']['window'][index])
    if selected!=expected:
        raise ValueError('the coherent primary region changes its complete bounded contract')
    if capture is not None:
        if not capture:
            capture.update(schema=1,key=proof.KEY,windows=[],
                consumed={name:data.hex() for name,data in copied['consumed'].items()},toolchain=toolchain())
        if (set(capture)!={'schema','key','windows','consumed','toolchain'}
                or capture['schema']!=1 or capture['key']!=proof.KEY
                or len(capture['windows'])!=index
                or capture['consumed']!={name:data.hex() for name,data in copied['consumed'].items()}):
            raise ValueError('the coherent stock loop omits, duplicates, reorders or changes inputs')
    result=run_window(index,copied,directory/f'coherent-{selected.key}',early=False)
    if capture is not None:capture['windows'].append(result)
    return result['instructions']


def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--write',action='store_true')
    mode.add_argument('--check',action='store_true')
    args=parser.parse_args()
    catalog=proof.repo.images(ROOT)['JK08A'];image=catalog.path.read_bytes()
    if hashlib.sha256(image).hexdigest()!=catalog.sha256:
        raise ValueError('the coherent case generator requires its exact stock image')
    expected=matrix.render_header([[p['address'] for p in proof.pool_words(window,image)]
                                   for window in matrix.WINDOWS])
    descriptor=proof.expected_descriptor(image,expected.encode())
    target=ROOT/HEADER
    if args.check:
        if target.read_text()!=expected:
            raise SystemExit('the coherent case header differs from its declared matrix')
        from kb.test_contract import exact
        if not exact(proof.descriptor(ROOT),descriptor):
            raise SystemExit('the coherent descriptor differs from its declared source inputs')
    else:
        import tomlkit
        target.write_text(expected)
        (ROOT/proof.DESCRIPTOR).write_text(tomlkit.dumps(descriptor))
    print(f'{HEADER}: {sum(len(matrix.cases(window)) for window in matrix.WINDOWS)} cases')


if __name__=='__main__':
    main()
