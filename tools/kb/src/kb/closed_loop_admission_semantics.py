"""Separate bank-bit, exact byte-store and complete RAM admission equations."""

from kb import closed_loop_admission_contract as contract,closed_loop_admission_matrix as matrix
from kb import test_contract


def scalar(mask,bank):
    if type(mask) is not int or not 0<=mask<=255 or type(bank) is not int or bank not in (0,1):
        raise ValueError('the admission decoder requires a complete raw byte and exact bank')
    return (mask>>bank)&1


def evaluate(case,observed,result):
    selected=contract.selected(case);memory=bytearray(observed['memory_before'][0]);wanted=[];outputs=[]
    base_site=0xA0F04 if case['entry']==contract.ENTRIES[0] else 0xA0FFE
    wanted.append((base_site,'read',0xA114C,4,'01004558'))
    for row in selected:
        raw=case[matrix.FIELDS[contract.DECODERS.index(row)]]
        displacement=(row['input']-0xFFFF4558).to_bytes(2,'big').hex()
        wanted.extend([(row['pool_site'],'read',row['pool'],2,displacement),
                       (row['read_site'],'read',0x01000000+(row['input']&65535),1,bytes([raw]).hex())])
        for bank in (0,1):
            value=scalar(raw,bank);address=contract.INCOMING['gbr']+row['offset']+bank
            memory[address-matrix.RAM_BASE]=value;outputs.append(value)
            wanted.append((row['one_site'] if value else row['zero_site'],'write',address,1,bytes([value]).hex()))
    if (observed['memory_after']!=(bytes(memory),) or result['registers'][0]!=1
            or result['registers'][2]!=contract.INCOMING['gbr']+selected[-1]['offset']
            or result['registers'][4]!=0x01004558 or result['registers'][5]!=raw
            or result['registers'][6]!=2 or result['registers'][8:11]!=(1,0,2)
            or result['sr']&1!=1 or (result['macl'],result['mach'],result['gbr'])!=
               tuple(observed['context'][index] for index in (17,16,15))):
        raise ValueError('the admission decoder differs from separate bit, scratch, status or complete RAM equations')
    if result['calls']:raise ValueError('the admission decoder introduces a helper call')
    actual=[tuple(row[key] for key in ('site','mode','address','width_bytes','bytes'))
        for row in result['accesses'] if row['domain'] in ('ram','rom')]
    if not test_contract.exact(actual,wanted):
        raise ValueError('the admission decoder changes an exact source, bank, conditional delay-slot store, value or width')
    end=contract.BOUNDARIES[0 if case['entry']==contract.ENTRIES[0] else 1]['address']
    returns=[(row['site'],row['target']) for row in result['branches'] if row['kind']=='return']
    if returns!=[(end+4,observed['continuation'])]:
        raise ValueError('the admission decoder changes its separately assembled outside observing return')
    return dict(index=case['index'],outputs=outputs,accesses=actual,exact_admission_writes=True,
        native_geometry_inference=False,natural_caller_reachability=False,
        source_producer_admission=False,integrator_update_admission=False,
        hardware_permission_admission=False,hardware_qualification=False)
