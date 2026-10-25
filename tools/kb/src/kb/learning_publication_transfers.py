"""Exact natural LTFT datum transfers using the existing publication equations."""

from kb import learning_transfer_semantics as numeric,test_contract

BRANCHES=(0x57B56,0x57B66,0x57B74,0x57BE2,0x57BF4,0x57BFC,0x57C04,0x57C0E,0x57C18,0x57C20)
ARITHMETIC_SOURCE='tools/kb/tests/test_ltft_publication_chain.py'
WATCHED_ROM={0x57B6A,0x57BD8}


def evaluate(case,observed,result):
    before=observed['memory_before'][0];cal=observed['calibration_before'];bank=case['argument']&255
    def data(at,width):
        for first,raw in cal.items():
            if first<=at and at+width<=first+len(raw):return raw[at-first:at-first+width]
        raise ValueError('the LTFT scalar consumer lacks its exact observed calibration')
    lower,upper=data(0x8E5B,1)[0],data(0x8E5A,1)[0]
    expected=numeric.publication(before,bank,lower,upper);wanted=[]
    def read(site,at,width):wanted.append((site,'read',0xFFFF0000+at,width,before[at:at+width].hex()))
    def rom(site,at):wanted.append((site,'read',at,1,data(at,1).hex()))
    read(0x57B36,0x2306+bank*2,2);read(0x57B3A,0x5648+bank*2,2);read(0x57B4C,0x230E,1)
    if not expected['mask']&(bank+1):
        read(0x57B5C,0x15FC,2);read(0x57B62,0x15FE,2)
        if expected['active']:rom(0x57B6A,0x8E5B);rom(0x57BD8,0x8E5A)
    if (len(result['calls'])!=1 or (result['calls'][0]['site'],result['calls'][0]['target'])!=(0x57BEE,0x25E20)
            or result['calls'][0]['entry']['registers'][4]!=0x129):
        raise ValueError('the LTFT original changes its real predicate call, order or post-delay index')
    read(0x25E32,0x5A94,1)
    if not expected['diagnostic']&128:
        read(0x57BF8,0x41B5,1)
        if not expected['f']&1:
            read(0x57C00,0x41FA,1)
            if expected['g']&1:read(0x57C0A,0x248B,1)
            if not(expected['g']&1 and expected['h']&2):
                read(0x57C14,0x249C,1)
                if expected['k']&64:read(0x57C1C,0x248B,1)
    wanted.append((0x57C2A,'write',0xFFFF2302+bank*2,2,expected['output'].to_bytes(2,'big').hex()))
    if observed['memory_after']!=(expected['memory'],):
        raise ValueError('the LTFT actual RAM differs from independent wrap/limit/neutral and full-footprint equations')
    actual=[]
    for row in result['accesses']:
        if row['domain']!='ram' and row['site'] not in WATCHED_ROM:continue
        address=row['address']
        if row['domain']=='ram':address=0xFFFF0000+address-0x01000000
        elif row['domain']!='rom':raise ValueError('an LTFT datum leaves its exact RAM or ROM domain')
        actual.append((row['site'],row['mode'],address,row['width_bytes'],row['bytes']))
    if not test_contract.exact(actual,wanted):
        raise ValueError('the LTFT original changes an exact datum/site/width/direction/value or short-circuit path')
    return dict(index=case['index'],kind='publication',bank=bank,output=expected['output'],accesses=actual,
        reset=None,enabled=None,exact_learning_transfers=True,native_geometry_inference=False,
        scale_admission=False,units_admission=False,natural_caller_reachability=False,hardware_qualification=False)
