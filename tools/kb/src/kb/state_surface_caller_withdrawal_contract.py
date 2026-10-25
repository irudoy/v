"""Exact natural state surface caller withdrawal paths, literal inputs and declared pointer aliases."""

import hashlib
import json
from pathlib import Path
import tomllib
from kb import test_contract

DESCRIPTOR='defs/JK08A.state-surface-caller-withdrawal-paths.toml'
IMAGE_SHA256='ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
OBSERVER='tools/sh-elf-run/stock_ignition_consumer_invoke.s'
ENTRIES=(411624,)
UNIT={'assembly': 'tools/sh-elf-run/stock_jk08a_state_surface_caller_withdrawal.s',
 'code': [{'start': 155780, 'end': 155828},
          {'start': 156528, 'end': 156546},
          {'start': 157504, 'end': 157550},
          {'start': 157552, 'end': 157638},
          {'start': 158020, 'end': 158080},
          {'start': 158304, 'end': 158394},
          {'start': 158840, 'end': 158990},
          {'start': 411624, 'end': 411782},
          {'start': 411888, 'end': 412180}],
 'pools': [{'address': 34713, 'size': 1, 'stock_hex': '0f'},
           {'address': 35647, 'size': 1, 'stock_hex': '18'},
           {'address': 155828, 'size': 4, 'stock_hex': '00026770'},
           {'address': 155832, 'size': 4, 'stock_hex': '00026944'},
           {'address': 156546, 'size': 2, 'stock_hex': '00e0'},
           {'address': 156548, 'size': 4, 'stock_hex': '00026a80'},
           {'address': 157640, 'size': 4, 'stock_hex': '00026740'},
           {'address': 158080, 'size': 4, 'stock_hex': '00026c78'},
           {'address': 158396, 'size': 4, 'stock_hex': '00026740'},
           {'address': 411782, 'size': 2, 'stock_hex': '0a7b'},
           {'address': 411784, 'size': 2, 'stock_hex': '05e7'},
           {'address': 411786, 'size': 2, 'stock_hex': '0152'},
           {'address': 411788, 'size': 2, 'stock_hex': '05d5'},
           {'address': 411796, 'size': 4, 'stock_hex': '00008b3f'},
           {'address': 411812, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 411836, 'size': 4, 'stock_hex': 'ffff119c'},
           {'address': 411856, 'size': 4, 'stock_hex': 'ffff1082'},
           {'address': 411860, 'size': 4, 'stock_hex': 'ffff244f'},
           {'address': 411864, 'size': 4, 'stock_hex': 'ffff28f8'},
           {'address': 411868, 'size': 4, 'stock_hex': '0000b60a'},
           {'address': 411872, 'size': 4, 'stock_hex': '00026084'},
           {'address': 411876, 'size': 4, 'stock_hex': '0000b5fa'},
           {'address': 411880, 'size': 4, 'stock_hex': '00011fe2'},
           {'address': 411884, 'size': 4, 'stock_hex': '00011fde'},
           {'address': 412180, 'size': 2, 'stock_hex': '0a7b'},
           {'address': 412182, 'size': 2, 'stock_hex': '05e7'},
           {'address': 412184, 'size': 2, 'stock_hex': '0152'},
           {'address': 412186, 'size': 2, 'stock_hex': '2d0e'},
           {'address': 412484, 'size': 4, 'stock_hex': 'ffff244f'},
           {'address': 412488, 'size': 4, 'stock_hex': '00012b62'},
           {'address': 412492, 'size': 4, 'stock_hex': 'ffff28f8'},
           {'address': 412496, 'size': 4, 'stock_hex': 'ffff128c'},
           {'address': 412500, 'size': 4, 'stock_hex': '00011fe6'},
           {'address': 412504, 'size': 4, 'stock_hex': '00008799'},
           {'address': 412508, 'size': 4, 'stock_hex': 'ffff40c6'},
           {'address': 412512, 'size': 4, 'stock_hex': '00026370'}],
 'aliases': [{'address': 411812, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 411836, 'width': 4, 'original': 4294906268, 'alias': 16781724},
             {'address': 411856, 'width': 4, 'original': 4294905986, 'alias': 16781442},
             {'address': 411860, 'width': 4, 'original': 4294911055, 'alias': 16786511},
             {'address': 411864, 'width': 4, 'original': 4294912248, 'alias': 16787704},
             {'address': 412484, 'width': 4, 'original': 4294911055, 'alias': 16786511},
             {'address': 412492, 'width': 4, 'original': 4294912248, 'alias': 16787704},
             {'address': 412496, 'width': 4, 'original': 4294906508, 'alias': 16781964},
             {'address': 412508, 'width': 4, 'original': 4294918342, 'alias': 16793798}]}
CONTROLLED_CALIBRATION=[{'address': 34713, 'size': 1},
 {'address': 35647, 'size': 1},
 {'address': 46586, 'size': 16},
 {'address': 46602, 'size': 16},
 {'address': 73694, 'size': 4},
 {'address': 73698, 'size': 4},
 {'address': 73702, 'size': 16},
 {'address': 76642, 'size': 4},
 {'address': 155828, 'size': 4},
 {'address': 155832, 'size': 4},
 {'address': 156546, 'size': 2},
 {'address': 156548, 'size': 4},
 {'address': 157640, 'size': 4},
 {'address': 158080, 'size': 4},
 {'address': 158396, 'size': 4},
 {'address': 411782, 'size': 2},
 {'address': 411784, 'size': 2},
 {'address': 411786, 'size': 2},
 {'address': 411788, 'size': 2},
 {'address': 411796, 'size': 4},
 {'address': 411812, 'size': 4},
 {'address': 411836, 'size': 4},
 {'address': 411856, 'size': 4},
 {'address': 411860, 'size': 4},
 {'address': 411864, 'size': 4},
 {'address': 411868, 'size': 4},
 {'address': 411872, 'size': 4},
 {'address': 411876, 'size': 4},
 {'address': 411880, 'size': 4},
 {'address': 411884, 'size': 4},
 {'address': 412180, 'size': 2},
 {'address': 412182, 'size': 2},
 {'address': 412184, 'size': 2},
 {'address': 412186, 'size': 2},
 {'address': 412484, 'size': 4},
 {'address': 412488, 'size': 4},
 {'address': 412492, 'size': 4},
 {'address': 412496, 'size': 4},
 {'address': 412500, 'size': 4},
 {'address': 412504, 'size': 4},
 {'address': 412508, 'size': 4},
 {'address': 412512, 'size': 4}]
BOUND_SPANS=({'address': 155780, 'size': 48},
 {'address': 156528, 'size': 18},
 {'address': 157504, 'size': 46},
 {'address': 157552, 'size': 86},
 {'address': 158020, 'size': 60},
 {'address': 158304, 'size': 90},
 {'address': 158840, 'size': 150},
 {'address': 411624, 'size': 158},
 {'address': 411888, 'size': 292},
 {'address': 34713, 'size': 1},
 {'address': 35647, 'size': 1},
 {'address': 46586, 'size': 16},
 {'address': 46602, 'size': 16},
 {'address': 73694, 'size': 4},
 {'address': 73698, 'size': 4},
 {'address': 73702, 'size': 16},
 {'address': 76642, 'size': 4},
 {'address': 155828, 'size': 4},
 {'address': 155832, 'size': 4},
 {'address': 156546, 'size': 2},
 {'address': 156548, 'size': 4},
 {'address': 157640, 'size': 4},
 {'address': 158080, 'size': 4},
 {'address': 158396, 'size': 4},
 {'address': 411782, 'size': 2},
 {'address': 411784, 'size': 2},
 {'address': 411786, 'size': 2},
 {'address': 411788, 'size': 2},
 {'address': 411796, 'size': 4},
 {'address': 411812, 'size': 4},
 {'address': 411836, 'size': 4},
 {'address': 411856, 'size': 4},
 {'address': 411860, 'size': 4},
 {'address': 411864, 'size': 4},
 {'address': 411868, 'size': 4},
 {'address': 411872, 'size': 4},
 {'address': 411876, 'size': 4},
 {'address': 411880, 'size': 4},
 {'address': 411884, 'size': 4},
 {'address': 412180, 'size': 2},
 {'address': 412182, 'size': 2},
 {'address': 412184, 'size': 2},
 {'address': 412186, 'size': 2},
 {'address': 412484, 'size': 4},
 {'address': 412488, 'size': 4},
 {'address': 412492, 'size': 4},
 {'address': 412496, 'size': 4},
 {'address': 412500, 'size': 4},
 {'address': 412504, 'size': 4},
 {'address': 412508, 'size': 4},
 {'address': 412512, 'size': 4})
FLAGS=('native_identity_admission',
 'native_geometry_inference',
 'scale_admission',
 'units_admission',
 'natural_caller_reachability',
 'hardware_qualification',
 'stock_function_stubs',
 'native_publication')
CONFIGURATION=[{'address': 34713, 'field': 'config_8799', 'size': 1},
 {'address': 35647, 'field': 'config_8b3f', 'size': 1},
 {'address': 46586, 'field': 'surface_value_0', 'size': 1},
 {'address': 46587, 'field': 'surface_value_1', 'size': 1},
 {'address': 46588, 'field': 'surface_value_2', 'size': 1},
 {'address': 46589, 'field': 'surface_value_3', 'size': 1},
 {'address': 46590, 'field': 'surface_value_4', 'size': 1},
 {'address': 46591, 'field': 'surface_value_5', 'size': 1},
 {'address': 46592, 'field': 'surface_value_6', 'size': 1},
 {'address': 46593, 'field': 'surface_value_7', 'size': 1},
 {'address': 46594, 'field': 'surface_value_8', 'size': 1},
 {'address': 46595, 'field': 'surface_value_9', 'size': 1},
 {'address': 46596, 'field': 'surface_value_10', 'size': 1},
 {'address': 46597, 'field': 'surface_value_11', 'size': 1},
 {'address': 46598, 'field': 'surface_value_12', 'size': 1},
 {'address': 46599, 'field': 'surface_value_13', 'size': 1},
 {'address': 46600, 'field': 'surface_value_14', 'size': 1},
 {'address': 46601, 'field': 'surface_value_15', 'size': 1},
 {'address': 46602, 'field': 'selection_value_0', 'size': 1},
 {'address': 46603, 'field': 'selection_value_1', 'size': 1},
 {'address': 46604, 'field': 'selection_value_2', 'size': 1},
 {'address': 46605, 'field': 'selection_value_3', 'size': 1},
 {'address': 46606, 'field': 'selection_value_4', 'size': 1},
 {'address': 46607, 'field': 'selection_value_5', 'size': 1},
 {'address': 46608, 'field': 'selection_value_6', 'size': 1},
 {'address': 46609, 'field': 'selection_value_7', 'size': 1},
 {'address': 46610, 'field': 'selection_value_8', 'size': 1},
 {'address': 46611, 'field': 'selection_value_9', 'size': 1},
 {'address': 46612, 'field': 'selection_value_10', 'size': 1},
 {'address': 46613, 'field': 'selection_value_11', 'size': 1},
 {'address': 46614, 'field': 'selection_value_12', 'size': 1},
 {'address': 46615, 'field': 'selection_value_13', 'size': 1},
 {'address': 46616, 'field': 'selection_value_14', 'size': 1},
 {'address': 46617, 'field': 'selection_value_15', 'size': 1},
 {'address': 73698, 'field': 'row_axis_0', 'size': 1},
 {'address': 73699, 'field': 'row_axis_1', 'size': 1},
 {'address': 73700, 'field': 'row_axis_2', 'size': 1},
 {'address': 73701, 'field': 'row_axis_3', 'size': 1},
 {'address': 73694, 'field': 'col_axis_0', 'size': 1},
 {'address': 73695, 'field': 'col_axis_1', 'size': 1},
 {'address': 73696, 'field': 'col_axis_2', 'size': 1},
 {'address': 73697, 'field': 'col_axis_3', 'size': 1},
 {'address': 73702, 'field': 'curve_value_0', 'size': 1},
 {'address': 73703, 'field': 'curve_value_1', 'size': 1},
 {'address': 73704, 'field': 'curve_value_2', 'size': 1},
 {'address': 73705, 'field': 'curve_value_3', 'size': 1},
 {'address': 73706, 'field': 'curve_value_4', 'size': 1},
 {'address': 73707, 'field': 'curve_value_5', 'size': 1},
 {'address': 73708, 'field': 'curve_value_6', 'size': 1},
 {'address': 73709, 'field': 'curve_value_7', 'size': 1},
 {'address': 73710, 'field': 'curve_value_8', 'size': 1},
 {'address': 73711, 'field': 'curve_value_9', 'size': 1},
 {'address': 73712, 'field': 'curve_value_10', 'size': 1},
 {'address': 73713, 'field': 'curve_value_11', 'size': 1},
 {'address': 73714, 'field': 'curve_value_12', 'size': 1},
 {'address': 73715, 'field': 'curve_value_13', 'size': 1},
 {'address': 73716, 'field': 'curve_value_14', 'size': 1},
 {'address': 73717, 'field': 'curve_value_15', 'size': 1},
 {'address': 76642, 'field': 'split_value_0', 'size': 1},
 {'address': 76643, 'field': 'split_value_1', 'size': 1},
 {'address': 76644, 'field': 'split_value_2', 'size': 1},
 {'address': 76645, 'field': 'split_value_3', 'size': 1}]
INPUT_BLOBS=[{'name': 'surface_value_bytes', 'address': 46586, 'size': 16},
 {'name': 'selection_value_bytes', 'address': 46602, 'size': 16},
 {'name': 'row_axis_bytes', 'address': 73698, 'size': 4},
 {'name': 'col_axis_bytes', 'address': 73694, 'size': 4},
 {'name': 'curve_value_bytes', 'address': 73702, 'size': 16},
 {'name': 'split_value_bytes', 'address': 76642, 'size': 4}]
ADAPTER_SHA256='4d500a1a0da7fbeb7f3de6d1221e9c54536924d168ed3cb0fdf08b4cba8859c5'
HELPER_ENTRIES=(155780, 156528, 158020, 158304, 157504, 157552, 158840)
REUSED_HELPER_FILES_SHA256={'defs/JK08A.byte-surface-paths.toml': '646c7f482e579314ab663cdd58fb541b2fa56ebc47f940e7f358c2968a42f06b',
 'tools/sh-elf-run/stock_jk08a_byte_surface_paths.s': '931646a791302eda98d6239a9e2455e46574d4b4b79b715dc51975d9d9312635',
 'tools/kb/src/kb/byte_surface_contract.py': 'a70226fbee2eaf0422807ec63001aea98ad3aeabcc6f1b1316d127faa0230be6',
 'tools/kb/src/kb/byte_surface_matrix.py': '462e46a36df38131618bad602dd5c403b1b4a3463c7227a3ce4a22de7b307651',
 'tools/kb/src/kb/byte_surface_semantics.py': '8ff3d4110fb324d9a7d2daca5b6b7948a704287255c664535c36d66c0101a853',
 'tools/kb/src/kb/byte_surface_equations.py': '2c686f6ef380bf88a1635742b4cf6b25f3998b49a83e1f014baa698c3f5548cf',
 'tools/kb/src/kb/byte_surface_capture_evidence.py': '53299e49ae0d1cbedec5201f6f5a56760755d4876367a26c7b51ea0f004fbf94',
 'tools/sh-elf-run/byte_surface_capture.py': '531d5ae30752da44d6049dbbd4cc69f18794dfbc637d69a751f36dedef29e555',
 'defs/JK08A.byte-curve-caller-withdrawal-paths.toml': 'eef3bb053ec07819d675547b5667b0a188cbc0343643f318db8100ffe15e65c7',
 'tools/sh-elf-run/stock_jk08a_byte_curve_caller_withdrawal.s': '2042cd93ebd162de58c83323ba6477a37d5110a211b6d7755425dc33d6bd3c21',
 'tools/kb/src/kb/byte_curve_caller_withdrawal_contract.py': 'aaaee28de43a668abbaf7ab4d1d0288eeedfbd7c19436dc78103dbb62d52c5dc',
 'tools/kb/src/kb/byte_curve_caller_withdrawal_matrix.py': '3afd1bda60c112551d18e8fecb2197982f99550e94d97d0c63b7feec58a5e035',
 'tools/kb/src/kb/byte_curve_caller_withdrawal_semantics.py': 'c334890fab9b66321bd6643a49020116babe6911b8dbc433dde9ff63b7cea56b',
 'tools/kb/src/kb/byte_curve_caller_withdrawal_transfers.py': '45176f0d29df994a923a215650f4e5f752fee320a74dad5e38f7f3f9dae377a6',
 'tools/kb/src/kb/byte_curve_caller_withdrawal_capture_evidence.py': '56ac55bef74315fc665cc1bb1ecb9e316e1e5738f96615fc15b440f2088aa49d',
 'tools/sh-elf-run/byte_curve_caller_withdrawal_capture.py': 'c3005baae784087eb3602f4bb2264a10131b8b978ba920c742d47103bfa3d931'}
FUNCTIONS=(*ENTRIES,*HELPER_ENTRIES)
SPANS=tuple((row['start'],row['end']) for row in UNIT['code'])


def descriptor(root):
    value=tomllib.loads((Path(root)/DESCRIPTOR).read_text())
    if (set(value)!={'schema','id','layout','rom','image_sha256','scope','entries','observer',
            'context_bytes','frame_bytes','frame_prefix','unit','controlled_calibration','configuration','input_blobs','adapter',*FLAGS}
            or not test_contract.exact(value['schema'],1) or value['id']!='jk08a-state-surface-caller-withdrawal'
            or value['layout']!='7mfk' or value['rom']!='JK08A' or value['image_sha256']!=IMAGE_SHA256
            or not test_contract.exact((value['entries'],value['observer'],value['context_bytes'],value['frame_bytes'],
                value['frame_prefix']),(list(ENTRIES),OBSERVER,80,192,160))
            or any(value[name] is not False for name in FLAGS)
            or not test_contract.exact(value['unit'],UNIT)
            or not test_contract.exact(value['controlled_calibration'],CONTROLLED_CALIBRATION)
            or not test_contract.exact(value['configuration'],CONFIGURATION)
            or not test_contract.exact(value['input_blobs'],INPUT_BLOBS)
            or hashlib.sha256(json.dumps(value['adapter'],sort_keys=True,separators=(',',':')).encode()).hexdigest()!=ADAPTER_SHA256):
        raise ValueError('the state surface caller withdrawal paths change an exact natural entry, code/pool byte, alias or complete observer premise')
    require_reused_helper_boundary(root)
    return dict(value,entry=[dict(start=first,end=last) for first,last in SPANS])


def require_image(declared,image):
    if (type(image) is not bytes or hashlib.sha256(image).hexdigest()!=IMAGE_SHA256
            or not test_contract.exact(declared['unit'],UNIT)):
        raise ValueError('the state surface caller withdrawal paths change the complete owned stock image or exact unit')
    for row in UNIT['pools']:
        if image[row['address']:row['address']+row['size']].hex()!=row['stock_hex']:
            raise ValueError('the state surface caller withdrawal paths change a pinned exact stock pool or configuration byte')


def independent_fixture(declared,image):
    require_image(declared,image);fixture=bytearray(image);aliases=[]
    for row in UNIT['aliases']:
        at=row['address']
        if int.from_bytes(image[at:at+4],'big')!=row['original']:
            raise ValueError('the state surface caller withdrawal paths relocate a different original native pointer')
        fixture[at:at+4]=row['alias'].to_bytes(4,'big');aliases.append(dict(row))
    return bytes(fixture),aliases


def fixture_for_case(declared,image,case):
    from kb import state_surface_caller_withdrawal_matrix as matrix
    matrix.require_case(case);fixture,aliases=independent_fixture(declared,image);fixture=bytearray(fixture)
    for row in CONFIGURATION:
        at,size=row['address'],row['size'];fixture[at:at+size]=case[row['field']].to_bytes(size,'big')
    return bytes(fixture),aliases


def require_reused_helper_boundary(root):
    for name,wanted in REUSED_HELPER_FILES_SHA256.items():
        if hashlib.sha256((Path(root)/name).read_bytes()).hexdigest()!=wanted:
            raise ValueError('the state surface caller changes a complete reused signed/unsigned division,byte-curve and standard implicit-byte source boundary')
