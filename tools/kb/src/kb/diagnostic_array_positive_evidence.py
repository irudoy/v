"""Positive diagnostic-array RMW evidence from the complete unchanged paired caller original."""
import hashlib
import json
from pathlib import Path
from kb import test_contract,repo
from kb import paired_inhibit_writer_withdrawal_capture_evidence as paired

RAM_BASE=0x01000000
ARRAY_BASE=RAM_BASE+0x5718
OR_OFFSETS=(0x31,0x2E,0x2B,0x28,0x25,0x22,0x1F)
AND_OFFSETS=(0x32,0x2F,0x2C,0x29,0x26,0x23,0x20)
ENTRY_SITES={0x7C8FA:(0x7C918,0x7C950),0x7C9A8:(0x7C9D4,0x7CA0E)}
ORIGINALS=('ace066de89ca0e146133354756c38ccda95830904176750f776020f78d758261',
    'e05ca8c55888e89a68795f8e3d2d7e22173743a4a5c13ad589ebab1854b4c532')


def sites(entry):
    first,second=ENTRY_SITES[entry]
    return {start+4*i:(ARRAY_BASE+offset,mode,mask) for start,offsets,mode,mask in
        ((first,OR_OFFSETS,'or',4),(second,AND_OFFSETS,'and',0xBF)) for i,offset in enumerate(offsets)}


def require_operands(entry,result,observed):
    expected=sites(entry);seen=set();publications=[]
    for site,(address,operation,mask) in expected.items():
        rows=[row for row in result['accesses'] if row['site']==site]
        if not rows:continue
        if (len(rows)!=2 or [row['mode'] for row in rows]!=['read','write']
                or any((row['address'],row['width_bytes'],row['register'],row['domain'])!=(address,1,None,'ram') for row in rows)):
            raise ValueError('the positive array writer changes an exact entry-scoped ordered byte RMW operand pair')
        incoming=bytes.fromhex(rows[0]['bytes']);published=bytes.fromhex(rows[1]['bytes'])
        if len(incoming)!=1 or len(published)!=1:
            raise ValueError('the positive array writer changes the complete physical byte width')
        computed=incoming[0]|mask if operation=='or' else incoming[0]&mask
        if published!=bytes((computed,)):
            raise ValueError('the positive array writer substitutes an input echo or another computed bit operation')
        offset=address-RAM_BASE
        if observed['memory_after'][0][offset:offset+1]!=published:
            raise ValueError('the positive array writer detaches its actual final publication from the physical write')
        seen.add(site);publications.append((site,address,incoming,published))
    return seen,publications


def require_primary(model,record):
    # The complete existing primary,including its input/state/physical/helper/
    # branch/return/causal contracts,is required without source or scope narrowing.
    original=paired.require_primary(model,record)
    packet=record['candidate']['witness'].get('paired_inhibit_writer_withdrawal_paths')
    declared=packet['declaration'];catalog=repo.images(model.root)['JK08A'];image=catalog.path.read_bytes()
    if hashlib.sha256(image).hexdigest()!=catalog.sha256:
        raise ValueError('the positive array writers change the complete owned image')
    actual=paired.observations(packet,declared)
    seen={entry:set() for entry in ENTRY_SITES};groups={};changed={}
    for case,observed in zip(declared['cases'],actual):
        entry=case['entry']
        if entry not in ENTRY_SITES:raise ValueError('the positive array writers substitute a different complete caller entry')
        result,value=paired.require_state(declared,image,case,observed,model.root)
        current,publications=require_operands(entry,result,observed);seen[entry].update(current)
        for site,address,incoming,published in publications:
            memory=bytearray(observed['memory_before'][0]);memory[address-RAM_BASE]=0
            held=dict(memory=memory.hex(),context=observed['context'],frame=observed['frame_before'].hex(),
                entry=entry,sp=observed['sp'],continuation=observed['continuation'],abi=observed['abi_before'],
                sr=observed['sr_before'],bound=observed['bound_before'].hex(),
                calibration={str(at):raw.hex() for at,raw in observed['calibration_before'].items()})
            key=hashlib.sha256(json.dumps(held,sort_keys=True,separators=(',',':')).encode()).hexdigest()
            groups.setdefault((entry,site,key),[]).append((incoming,published))
            changed[entry,site]=changed.get((entry,site),False) or incoming!=published
    for entry in ENTRY_SITES:
        if seen[entry]!=set(sites(entry)):
            raise ValueError('the positive array writer omits a real array-member RMW site')
        for site in sites(entry):
            if not changed.get((entry,site),False):
                raise ValueError('the positive array writer lacks an actual changed computed member publication')
            alternatives=[rows for (parent,at,key),rows in groups.items() if (parent,at)==(entry,site)]
            if not any(any(a[0]!=b[0] and a[1]!=b[1] for a in rows for b in rows) for rows in alternatives):
                raise ValueError('the positive array RMW lacks distinct actual computed bytes with every other complete input fixed')
    from kb import maf_access_contract as owning
    rows=[row for row in owning.descriptor(model.root)['reference']
        if row['component']=='actuator_mask_access_paths' and row['direction']=='writer']
    if tuple(row['original_claim_sha256'] for row in rows)!=ORIGINALS:
        raise ValueError('the positive array writers substitute either exact retained original')
    for row in rows:
        if (row['owner']!='hallowed-malkoha/ram' or row['address']!=0xFFFF5718
                or row['width_bytes']!=1 or row['sites']!=list(sites(row['function']))):
            raise ValueError('the positive array writer changes the existing array owner or exact site/entry scope')
    return dict(complete_paired_original_same_primary=True,positive_array_member_writes=True,
        paired_original_stdout_sha256=original['stdout_sha256'],originals=ORIGINALS,
        actual_entry_scoped_RMW_sites={f'{entry:08x}':sorted(current) for entry,current in seen.items()},
        root_byte_absence_is_array_absence=False,native_geometry_inference=False,hardware_qualification=False)
