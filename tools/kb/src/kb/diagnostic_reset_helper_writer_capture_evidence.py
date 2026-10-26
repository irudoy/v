"""Actual constant-zero helper publications with every complete other input fixed."""
import hashlib,json
from kb import test_contract
TARGET=0xFFFF99C7
OFFSET=0x99C7
NATIVE_OFFSET=256+0xC7


def held_inputs(observed):
    memory=bytearray(observed['memory_before'][0]);memory[OFFSET]=0
    native=bytearray(observed['native_before']);native[NATIVE_OFFSET]=0
    held=dict(memory=memory.hex(),native=native.hex(),context=observed['context'],frame=observed['frame_before'].hex(),
        sp=observed['sp'],continuation=observed['continuation'],abi=observed['abi_before'],sr=observed['sr_before'],
        calibration={str(at):raw.hex() for at,raw in observed['calibration_before'].items()},
        bound=observed['bound_before'].hex(),entry=observed['entry'])
    return hashlib.sha256(json.dumps(held,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def require_publications(pairs):
    groups={False:{},True:{}}
    for observed,value in pairs:
        before=observed['native_before'][NATIVE_OFFSET];after=observed['native_after'][NATIVE_OFFSET]
        if (type(value['gate']) is not bool or after!=0 or observed['memory_before'][0][OFFSET]!=before
                or observed['memory_after'][0][OFFSET]!=before):
            raise ValueError('the reset helper changes its actual99C7 zero publication or copies it into the ordinary shadow')
        groups[value['gate']].setdefault(held_inputs(observed),[]).append((before,after))
    for gate,selected in groups.items():
        if not any({before for before,after in rows}==set(range(256)) and {after for before,after in rows}=={0}
                and all(before!=after for before,after in rows if before) for rows in selected.values()):
            raise ValueError('the reset helper lacks every actual raw target prior with complete other inputs fixed on both later gate paths')
    return dict(helper_constant_writer_inputs=dict(gate_0_full_priors=True,gate_1_full_priors=True,exact_actual_zero_store=True))


def require_result(result):
    if (type(result) is not dict or result.get('complete_helper_zero_PC_R7_loop') is not True
            or result.get('actual_helper_zero_priors') is not True
            or not test_contract.exact(result.get('helper_constant_writer_inputs'),
                dict(gate_0_full_priors=True,gate_1_full_priors=True,exact_actual_zero_store=True))):
        raise ValueError('the reset helper owning boundary omits full physical, R7, loop or actual-prior obligations')
    return True
