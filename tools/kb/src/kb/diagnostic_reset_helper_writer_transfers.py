"""Exact 99C7 zero-byte store inside the complete existing natural reset helper."""
from kb import test_contract
TARGET=0xFFFF99C7
SITE=0x2E77A


def require(observed,result,value):
    rows=[row for row in result['accesses'] if row['address']<=TARGET<row['address']+row['width_bytes']]
    expected=[dict(site=SITE,mode='write',address=TARGET,width_bytes=1,register=7,domain='native-io',bytes='00')]
    if not test_contract.exact(rows,expected):
        raise ValueError('the reset helper omits or substitutes its one exact actual99C7 zero-byte store')
    first=[row for row in result['trace'] if row['site']==SITE]
    if (len(first)!=4 or [row['before']['registers'][5] for row in first]!=list(range(0xFFFF99C4,0xFFFF99C8))
            or any(row['before']['registers'][7]!=0 or row['before']['registers'][6]!=index+1
                or row['before']['registers'][4]!=4 or row['before']['registers'][15]!=observed['sp']-12
                or row['word']!=0x2570 for index,row in enumerate(first))):
        raise ValueError('the reset helper changes full R7, pointer, bound, counter, instruction or real callee SP')
    selected=first[3]
    if selected['before']['registers'][5]!=TARGET or selected['before']['registers'][6]!=4:
        raise ValueError('the reset helper changes the fourth real loop store that owns99C7')
    calls=[row for row in result['calls'] if row['site']==0x2E824]
    if (len(calls)!=1 or (calls[0]['target'],calls[0]['return_address'],calls[0]['sp'])!=(0x2E76E,0x2E828,observed['sp']-12)
            or calls[0]['registers'][4]!=observed['context'][4]
            or calls[0]['entry']['registers'][4]!=observed['context'][4]
            or calls[0]['entry']['pr']!=0x2E828 or calls[0]['entry']['sp']!=observed['sp']-12):
        raise ValueError('the reset helper replaces its real complete caller entry or introduces a caller R4 premise')
    returns=[row for row in result['trace'] if row['site'] in (0x2E816,0x2E818)]
    if (len(returns)!=2 or returns[0]['branches']!=[dict(site=0x2E816,target=0x2E828,kind='return',delay=True)]
            or returns[1]['delay_slot'] is not True or returns[1]['next']!=0x2E828):
        raise ValueError('the reset helper replaces its real RTS or ordinary-byte store delay slot')
    return True
